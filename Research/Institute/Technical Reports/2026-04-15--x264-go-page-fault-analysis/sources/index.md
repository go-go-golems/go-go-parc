---
Title: x264 Page Fault Deep Analysis
Ticket: SCS-0017
Status: completed
Topics:
    - screencast-studio
    - gstreamer
    - x264
    - performance
    - memory
    - profiling
DocType: index
Intent: long-term
Owners: []
RelatedFiles:
    - Path: pkg/media/gst/recording.go
      Note: Direct recording builder with x264enc
    - Path: ttmp/2026/04/14/SCS-0016--investigate-low-level-performance-hot-path-with-pprof-perf-and-ebpf/reference/01-investigation-diary.md
      Note: Parent evidence showing 134832 vs 232 page-fault delta
    - Path: ttmp/2026/04/14/SCS-0016--investigate-low-level-performance-hot-path-with-pprof-perf-and-ebpf/scripts/results/32-small-graph-hosting-ladder-matrix/20260415-033745/01-manifest.tsv
      Note: Small-graph ladder showing x264enc as first divergence boundary
ExternalSources: []
Summary: Completed investigation showing Go+x264 fault issue is NOT allocator/THP fixable - requires architectural solution (subprocess isolation or buffer pre-allocation).
LastUpdated: 2026-04-15T04:25:00-04:00
WhatFor: Document the root cause finding and recommended fixes for the x264enc hosting interaction problem.
WhenToUse: Decision-making for addressing Go+x264 performance overhead.
---

# SCS-0017: x264 Page Fault Deep Analysis

## Executive Summary

**Investigation completed.** The Go+x264 page fault issue is a **genuine interaction problem** that cannot be fixed by simple allocator tuning.

### Key Findings

| Metric | Go + x264enc | gst-launch + x264enc | Ratio |
|--------|-------------|---------------------|-------|
| Page Faults | **28,261** | **2,812** | **10.1x** |
| x264_malloc calls | 419 | 211 | 2.0x |
| **Faults per malloc** | **~67** | **~13** | **~5x** |

### Root Cause

The same x264 allocations fault **~5x more** in a Go process due to Go runtime memory management creating different memory layout and first-touch patterns.

**NOT due to:**
- ❌ x264 allocating more frequently (only 2x, not 10x)
- ❌ glibc arena fragmentation (MALLOC_ARENA_MAX tests: no effect)
- ❌ THP policy (already at madvise, no effect)
- ❌ Go scavenger behavior (GODEBUG=madvdontneed=1: no effect)

**Likely due to:**
- Go heap address space layout differences
- CGO callback stack growth patterns
- Different first-touch thread behavior

### Recommended Fixes (in priority order)

1. **Buffer Pre-allocation** - Bypass x264 allocator with pre-allocated buffers
2. **Subprocess Isolation** - Spawn x264 in separate process (like ffmpeg wrapper)
3. **Switch to OpenH264** - No fault anomaly with openh264enc
4. **Accept Overhead** - Document ~10-15% overhead as Go encoding cost

## Deep Diagnostics for Root Cause (New)

To find the **exact mechanism**, run these diagnostics:

| Script | Tests | Hypothesis | Quick Command |
|--------|-------|------------|---------------|
| `scripts/07-memory-map-comparison.sh` | H1: Memory Layout | Virtual address space differences | `bash scripts/07-memory-map-comparison.sh` |
| `scripts/08-mmap-syscall-tracer.sh` | H2: Allocation Timing | Different mmap/mprotect patterns | `bash scripts/08-mmap-syscall-tracer.sh` |
| `scripts/09-thread-fault-analysis.sh` | H3: Thread-Local Touch | Thread migration effects | Manual (requires sudo) |

### Hypotheses Being Tested

**H1: Memory Map Layout** - Are heaps at different virtual addresses?
- Check: `/proc/[pid]/maps` comparison
- If true: Virtual address placement affects kernel behavior

**H2: Allocation Timing** - Different syscall patterns?
- Check: `strace -e mmap,mprotect` comparison  
- If true: Different allocation strategies cause different kernel paths

**H3: Thread-Local Touch** - Cross-thread memory access?
- Check: bpftrace correlating alloc_thread vs fault_thread
- If true: Thread migration or NUMA effects

**H4: Stack Growth** - CGO stack faults vs heap?
- Check: Fault address ranges in stack vs heap
- If true: Problem is CGO overhead, not x264

**H5: Initialization Pattern** - Zeroing behavior differences?
- Check: memset calls following allocations
- If true: Memory initialization is the trigger

---

## Investigation Timeline

1. **Repro Matrix**: 4-cell comparison (Go+x264, Go+openh264, gst-launch+x264, gst-launch+openh264) with `perf stat`
2. **Allocation Tracing**: heaptrack/Massif on Go+x264 vs gst-launch+x264
3. **Uprobe Instrumentation**: `perf probe` on `x264_malloc`/`x264_free`
4. **Page-Fault Attribution**: bpftrace on `exceptions:page_fault_user` with `ustack()` aggregation
5. **Kernel MM Events**: tracepoints for compaction, reclaim, huge-page allocation
6. **Allocator A/B**: `MALLOC_ARENA_MAX=1` and THP policy change
7. **Code Review**: x264 buffer-growth patterns, per-thread allocations
8. **Synthesis**: Determine which hypothesis is supported

## Documents

- [design-doc/01-analysis-plan.md](design-doc/01-analysis-plan.md) - Detailed 8-step plan with exact commands
- [design-doc/03-root-cause-deep-dive.md](design-doc/03-root-cause-deep-dive.md) - Extended diagnostics for finding exact mechanism
- [reference/01-step1-repro-matrix-results.md](reference/01-step1-repro-matrix-results.md) - 4-cell repro matrix confirming isolated interaction
- [reference/02-step3-uprobe-results.md](reference/02-step3-uprobe-results.md) - x264_malloc/free counts showing 8x faults per allocation
- [reference/03-step6-ab-test-results.md](reference/03-step6-ab-test-results.md) - Allocator A/B tests ruling out arena/THP causes
- [reference/04-final-synthesis-and-recommendations.md](reference/04-final-synthesis-and-recommendations.md) - Complete findings and recommended actions
- [reference/05-root-cause-identified.md](reference/05-root-cause-identified.md) - **ROOT CAUSE: Go heap pre-allocation mechanism**
- [reference/06-web-research-sources.md](reference/06-web-research-sources.md) - **Authoritative web sources backing up findings**
- [reference/07-surf-cli-research-guide.md](reference/07-surf-cli-research-guide.md) - Guide for deeper surf-go/ChatGPT/Kagi research
- [reference/08-cgo-malloc-interception.md](reference/08-cgo-malloc-interception.md) - **Why x264_malloc uses Go's heap (CGO malloc interception)**
- [reference/09-x264-vs-openh264-analysis.md](reference/09-x264-vs-openh264-analysis.md) - **Why x264 has 10x faults but openh264 doesn't**

## Scripts (All Executed)

| Script | Purpose | Status |
|--------|---------|--------|
| `scripts/01-go-manual-encode-harness/` | Go test harness for x264/openh264 | ✅ Built & working |
| `scripts/02-repro-matrix-perf-stat.sh` | 4-cell repro matrix with perf stat | ✅ Completed |
| `scripts/04-count-x264-allocations.sh` | uprobe counting on x264_malloc/free | ✅ Completed |
| `scripts/05-page-fault-bpftrace.sh` | Page-fault stack attribution | ✅ Completed (raw stacks) |
| `scripts/06-allocator-ab-test.sh` | MALLOC_ARENA_MAX and THP A/B test | ✅ Completed |

## Detailed Investigation Plan (Completed)
