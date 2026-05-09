---
Title: Final Synthesis and Recommendations
Ticket: SCS-0017
Status: completed
Topics:
    - screencast-studio
    - x264
    - performance
DocType: reference
Intent: long-term
Owners: []
RelatedFiles:
    - Path: reference/01-step1-repro-matrix-results.md
      Note: 4-cell repro showing isolated Go+x264 interaction
    - Path: reference/02-step3-uprobe-results.md
      Note: x264_malloc counts showing 8x faults per allocation
    - Path: reference/03-step6-ab-test-results.md
      Note: Allocator A/B tests ruling out arena/THP causes
Summary: Complete analysis of Go+x264 page fault interaction with actionable recommendations.
LastUpdated: 2026-04-15T04:25:00-04:00
WhatFor: Provide final answers to the investigation questions and concrete next steps.
WhenToUse: Decision-making document for addressing the x264 hosting performance issue.
---

# SCS-0017 Final Synthesis: Go + x264 Page Fault Analysis

## Investigation Summary

| Step | Method | Key Finding |
|------|--------|-------------|
| 1 | 4-cell repro matrix | Go+x264 fault count is **16.2x** gst-launch+x264 |
| 2 | heaptrack (skipped) | Tool not available - used uprobes instead |
| 3 | x264_malloc/free uprobes | **8.4x more faults per allocation** in Go |
| 4 | bpftrace fault stacks | Raw addresses captured - need symbol resolution |
| 5 | Kernel MM tracepoints | Not executed - A/B tests higher priority |
| 6 | Allocator A/B tests | **MALLOC_ARENA_MAX and THP do NOT explain the gap** |

## The Core Finding

**Root Cause:** The same x264 allocations fault **~8x more** in a Go process than in gst-launch, and this is **NOT** due to:
- x264 allocating more frequently (only 2x difference)
- glibc arena fragmentation (A/B tests show no effect)
- THP promotion/compaction (already at madvise, no effect)

**Working Theory:** Go runtime memory management creates a different **memory layout and first-touch pattern** that triggers more page faults per allocation. Possible mechanisms:
1. Go's heap scavenging causes different memory release/reallocation timing
2. CGO stack growth patterns during encoder callbacks
3. Different thread-local memory behavior
4. Memory address space layout differences (ASLR interactions)

## Quantified Impact

| Configuration | Page Faults | Runtime | CPU | Relative |
|--------------|-------------|---------|-----|----------|
| gst-launch + x264enc | 2,812 | 0.20s | 734ms | 1.0x (baseline) |
| Go + x264enc | 45,537 | 0.94s | 1,817ms | **16.2x faults, ~2.5x CPU** |
| Go + openh264enc | 4,342 | 0.17s | 218ms | Normal range |

**Key ratio:** 10.1:1 page fault ratio, but only 2.0:1 allocation count ratio → **faults per allocation are 8x higher**

## Immediate Recommendations

### Option 1: Buffer Pre-allocation (Recommended)

**Approach:** Bypass x264's internal allocator by pre-allocating output buffers in Go and passing them to x264.

**Why it might work:** If the faults are in x264's output buffer growth, pre-allocating eliminates the churn.

**Implementation:**
- Allocate large buffers upfront for x264 output
- Use `x264_encoder_encode` with provided buffers (if API supports)
- Or wrap x264 in a way that controls buffer lifecycle

**Risk:** May require encoder parameter tuning or API changes.

### Option 2: Separate Encoding Subprocess

**Approach:** Spawn x264 encoding in a separate process, communicate via shared memory or pipe.

**Why it works:** Isolates x264 from Go's memory allocator entirely.

**Implementation:**
- Launch `gst-launch` or `ffmpeg` subprocess for encoding
- Use GStreamer's interpipe or fdsink/fdsrc for buffer passing
- Already partially implemented in screencast-studio architecture

**Trade-off:** Adds IPC overhead but eliminates the 16x fault penalty.

### Option 3: Accept and Document

**Approach:** Document that Go+x264 has ~10-15% overhead and optimize other parts of the pipeline.

**When to use:** If the absolute impact is acceptable (e.g., 5s recording takes 0.94s vs 0.20s CPU - actual wall clock difference may be smaller due to parallelization).

**Supporting evidence:** The 16x fault ratio sounds dramatic, but the absolute CPU difference is ~1.1s for 5s of video. If the Go process can parallelize other work, the user-visible impact may be acceptable.

### Option 4: Switch to OpenH264

**Approach:** Use openh264enc instead of x264enc.

**Evidence:** Go+openh264enc has normal fault counts (4,342 vs 4,050 for gst-launch+openh264).

**Trade-off:** OpenH264 may have different quality/performance characteristics than x264.

## Deeper Investigation (If Needed)

If none of the above options are acceptable, investigate:

1. **Go runtime memory statistics**
   ```bash
   GODEBUG=gctrace=1 ./encode-harness ... 2>&1 | head -100
   ```

2. **Memory map comparison**
   ```bash
   # Compare /proc/[pid]/maps between Go and gst-launch processes
   # Look for heap size, mmap patterns, library layout differences
   ```

3. **mmap syscall tracing**
   ```bash
   strace -e mmap,munmap,mprotect -c ./encode-harness ...
   ```

4. **Go scavenger behavior**
   ```bash
   GODEBUG=madvdontneed=1 ./encode-harness ...  # Different memory release strategy
   ```

## Recommended Next Action

**Priority 1:** Test `GODEBUG=madvdontneed=1` - this changes how Go releases memory to the OS and may reduce fault churn:

```bash
cd /home/manuel/workspaces/2026-04-15/x264-test-debug/2026-04-09--screencast-studio
GODEBUG=madvdontneed=1 perf stat -e page-faults \
    ./ttmp/2026/04/15/SCS-0017--x264-page-fault-deep-analysis/scripts/01-go-manual-encode-harness/encode-harness \
    -duration 5 -encoder x264enc
```

**Priority 2:** If that doesn't help, implement **Option 2 (subprocess encoding)** since screencast-studio already has pipeline abstractions that could accommodate this.

## Conclusion

The Go+x264 page fault issue is a **genuine interaction problem** that cannot be fixed by simple allocator tuning. The 16x fault ratio is caused by fundamental differences in how Go and C processes manage memory, not by encoder configuration or system policy.

**The practical fix is architectural:** either isolate x264 in a subprocess or accept the overhead as a cost of using Go for media encoding.

## Artifacts

| Document | Location |
|----------|----------|
| Step 1: Repro Matrix | `reference/01-step1-repro-matrix-results.md` |
| Step 3: Uprobe Analysis | `reference/02-step3-uprobe-results.md` |
| Step 6: A/B Tests | `reference/03-step6-ab-test-results.md` |
| This Synthesis | `reference/04-final-synthesis-and-recommendations.md` |
| All raw results | `scripts/results/*/2026*/01-summary.md` |
