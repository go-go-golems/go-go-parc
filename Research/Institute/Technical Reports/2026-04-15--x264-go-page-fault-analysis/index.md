---
Title: x264/Go CGO Page Fault Root Cause Analysis
Topics:
    - x264
    - go
    - cgo
    - page-faults
    - memory-management
    - gstreamer
    - performance
    - buffer-pool
Date: 2026-04-15
Status: complete
---

# x264/Go CGO Page Fault Root Cause Analysis

## Status: Complete — Root Cause Corrected After Validation

**SCS-0017** identified the 10x page fault ratio and collected all raw evidence. **SCS-0018** critically validated the findings and corrected three false claims in the original report.

## Key Finding

GStreamer allocates 56 × 12 MB = 672 MB of video frame buffers at 1080p when running inside a Go process, but 0–1 buffers in gst-launch. This is the sole cause of the 10x RSS and page fault difference.

## Documents

- **[01-REPORT-x264-Go-CGO-Page-Fault-Root-Cause-Analysis.md](01-REPORT-x264-Go-CGO-Page-Fault-Root-Cause-Analysis.md)** — Full technical report with corrected root cause, demand paging explanation, and validation evidence

## Source Tickets

- **SCS-0017** — Original 8-step investigation (ttmp/2026/04/15/SCS-0017--x264-page-fault-deep-analysis/)
- **SCS-0018** — Critical validation that corrected the root cause (ttmp/2026/04/15/SCS-0018--critical-validation-of-x264-go-cgo-page-fault-root-cause/)

## Errata

Three foundational claims from SCS-0017 were disproven:
1. ~~CGO intercepts C malloc~~ → FALSE (libc malloc confirmed)
2. ~~Go heap pre-allocation causes RSS~~ → FALSE (heap is 0 MB)
3. ~~Pipeline backpressure inflates heap~~ → FALSE (GC never runs)
