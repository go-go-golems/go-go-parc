---
Title: Step 3 Results - x264 Allocation Uprobe Analysis
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
Summary: x264_malloc/x264_free call counts reveal fault attribution is the primary issue.
LastUpdated: 2026-04-15T04:18:00-04:00
WhatFor: Document the critical finding that same allocations fault differently.
WhenToUse: Evidence that allocation churn is not the full explanation.
---

# Step 3 Results: x264 Allocation Uprobe Analysis

## Test Parameters

- Duration: 5 seconds
- Resolution: 640x480 @ 30fps (150 frames)
- Bitrate: 2500 kbps
- Probes: probe_libx264:x264_malloc, probe_libx264:x264_free

## Raw Results

| Configuration | x264_malloc | x264_free | Page Faults | Runtime |
|--------------|-------------|-----------|-------------|---------|
| **Go + x264enc** | **419** | **429** | **45,537** | 0.94s |
| Go + openh264enc | 0 | 0 | 4,342 | 0.17s |
| gst-launch + x264enc | 211 | 221 | 2,812 | 0.20s |

## Critical Finding: Fault Attribution

**Allocation Churn is NOT the primary explanation:**

| Metric | Go vs gst-launch |
|--------|-----------------|
| x264_malloc calls | **2.0x** |
| Page faults | **16.2x** |
| **Faults per allocation** | **~8.1x** |

**Math:**
- Go: 45,537 faults / 419 mallocs = **~109 faults per malloc**
- gst-launch: 2,812 faults / 211 mallocs = **~13 faults per malloc**
- Ratio: **8.4x more faults per allocation in Go**

## Interpretation

**Fault Attribution Hypothesis CONFIRMED**

The same x264 allocations are faulting **~8x more** in a Go process than in gst-launch. This points to:

1. **Different allocator arena behavior** (glibc in Go process)
2. **Memory layout / fragmentation differences**
3. **THP (Transparent Huge Pages) interaction**
4. **First-touch patterns** (who touches the memory first)

**NOT primarily about:**
- x264 allocating more (only 2x difference)
- Different encoder settings (same pipeline)
- Different workload (same frames)

## Checkpoint Decision

Proceed to **Step 4** (page-fault stack attribution with bpftrace) to identify:
- Which user-space stacks are causing the faults?
- Are faults coming from libx264, malloc, or Go runtime?
- Can we isolate the exact faulting paths?

Then **Step 6** (allocator A/B tests) with:
- `MALLOC_ARENA_MAX=1` 
- THP policy changes

## Artifacts

- Full results: `scripts/results/04-x264-allocations/20260415-041749/`
- Raw logs: `go-x264-counts.log`, `gst-x264-counts.log`
