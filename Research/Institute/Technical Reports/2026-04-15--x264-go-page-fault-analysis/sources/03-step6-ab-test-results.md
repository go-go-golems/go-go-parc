---
Title: Step 6 Results - Allocator A/B Tests
Ticket: SCS-0017
Status: completed
Topics:
    - screencast-studio
    - x264
    - performance
DocType: reference
Intent: long-term
Owners: []
RelatedFiles: []
Summary: A/B tests show allocator policy is NOT the root cause of the 16x fault gap.
LastUpdated: 2026-04-15T04:22:00-04:00
WhatFor: Rule out allocator/THP as primary causes and redirect investigation.
WhenToUse: Evidence that deeper analysis is needed.
---

# Step 6 Results: Allocator A/B Tests

## Test Summary

| Test | Configuration | Page Faults | vs Baseline |
|------|--------------|-------------|-------------|
| Baseline | Default (no changes) | 28,261 | 1.0x |
| A | MALLOC_ARENA_MAX=1 | 27,263 | 0.96x (-3.5%) |
| B | MALLOC_ARENA_MAX=4 | 27,236 | 0.96x (-3.6%) |
| C | THP=madvise (already set) | 27,346 | 0.97x (-3.2%) |

## Critical Finding: Allocator Policy is NOT the Root Cause

The **3-4% differences are within normal variance** and do not explain the 16x fault gap observed between Go+x264 and gst-launch+x264.

**Ruled out:**
- ❌ glibc arena fragmentation
- ❌ THP promotion/compaction behavior
- ❌ Simple allocator tuning fixes

## Remaining Hypotheses

Since the fault gap persists despite similar:
- x264_malloc call counts (~2x, not 16x)
- Allocator arena policies (no effect)
- THP settings (already at madvise)

The remaining explanations must be:

### 1. Go Runtime Memory Allocator Interaction
- Go's garbage collector and memory allocator may interact poorly with x264's allocation patterns
- Go's scavenging behavior may cause different first-touch patterns
- Different heap growth strategies between Go and C host

### 2. Stack Growth Patterns
- Go's segmented stacks vs C's contiguous stacks
- Stack growth faults during CGO callbacks

### 3. Memory Layout / Address Space Differences
- Go's heap placement vs standard C process layout
- ASLR interactions
- Different mmap patterns for large allocations

### 4. First-Touch Patterns
- Different threads touching allocated memory first
- NUMA effects (if applicable)
- Memory initialization patterns

## Next Investigation Steps

1. **Compare memory maps** (`/proc/[pid]/maps`) between Go and gst-launch processes
2. **Trace mmap/munmap calls** using strace or bpftrace
3. **Analyze Go runtime memory statistics** during encoding
4. **Test with Go's `GODEBUG=madvdontneed=1`** to change memory release behavior
5. **Pre-allocate encoder buffers** in Go and pass to x264 to bypass its allocator

## Immediate Mitigation Options

Since the root cause is complex, consider:

1. **Buffer pooling**: Pre-allocate and reuse buffers to reduce allocation churn
2. **Separate encoding process**: Spawn x264 in a subprocess (like ffmpeg wrapper)
3. **Accept the overhead**: Document that Go+x264 has ~10-15% overhead vs native gst-launch

## Artifacts

- Full results: `scripts/results/06-allocator-ab/20260415-042109/`
- Baseline: `baseline-default.log`
- ARENA_MAX=1: `test-a-arena1.log`
- ARENA_MAX=4: `test-b-arena4.log`
- THP test: `test-c-thp-current.log`
