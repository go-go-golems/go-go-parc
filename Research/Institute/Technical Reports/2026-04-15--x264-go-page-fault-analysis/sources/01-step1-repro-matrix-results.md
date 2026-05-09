---
Title: Step 1 Results - 4-Cell Repro Matrix
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
Summary: Results from 4-cell repro matrix comparing Go+x264, Go+openh264, gst-launch+x264, gst-launch+openh264.
LastUpdated: 2026-04-15T04:15:00-04:00
WhatFor: Document Step 1 findings and interpret the repro matrix results.
WhenToUse: Reference for confirming the isolated interaction hypothesis.
---

# Step 1 Results: 4-Cell Repro Matrix

## Test Parameters

- Duration: 5 seconds
- Resolution: 640x480 @ 30fps (150 frames)
- Bitrate: 2500 kbps
- Encoder settings: tune=zerolatency, speed-preset=veryfast, bframes=0

## Raw Results

| Cell | Configuration | Task-Clock | Cycles | Instructions | Page Faults | Major Faults |
|------|--------------|------------|--------|--------------|-------------|--------------|
| 1 | Go + x264enc | 1,817.50 ms | 4.83B | 7.34B | **28,276** | 0 |
| 2 | Go + openh264enc | 217.84 ms | 0.71B | 1.86B | 4,322 | 0 |
| 3 | gst-launch + x264enc | 734.15 ms | 1.88B | 3.19B | 2,800 | 0 |
| 4 | gst-launch + openh264enc | 222.48 ms | 0.73B | 1.83B | 4,050 | 0 |

## Key Ratios

| Comparison | Page Fault Ratio | Interpretation |
|------------|-----------------|----------------|
| Go+x264 vs gst-launch+x264 | **10.1:1** | **Go+x264 is the outlier** |
| Go+openh264 vs gst-launch+openh264 | 1.1:1 | Normal variance |
| gst-launch+x264 vs gst-launch+openh264 | 0.7:1 | Similar range |

## Interpretation

**Hypothesis confirmed: Isolated Interaction Problem**

The page-fault explosion is specific to the **Go + x264enc** combination:

- ❌ **NOT** x264 alone → gst-launch+x264 has normal fault counts (2,800)
- ❌ **NOT** Go alone → Go+openh264 has normal fault counts (4,322)
- ✅ **IS** Go+x264 interaction → 10x higher than baseline

This validates the working hypothesis:
> Go host process + libx264 allocation/access pattern + Linux VM policy = fault-heavy path

## Checkpoint Decision

Proceed to **Step 2** (allocation tracing with heaptrack) and **Step 3** (uprobes on x264_malloc/x264_free) to determine:
1. Does Go+x264 allocate more frequently?
2. Are allocation sizes different?
3. Which specific x264 paths are hot?

## Artifacts

- Full results: `scripts/results/02-repro-matrix/20260415-041235/`
- Raw logs: `/tmp/repro-matrix.log`
