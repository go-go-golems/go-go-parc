---
title: Engineering Temporal Systems — Textbook Series
created: 2026-09-07
written: 2026-09-10
type: project
status: in-progress
tags: [engineering-temporal-systems, textbook, video-observatory]
repo: /home/manuel/code/wesen/2026-09-07--streaming-system
source_commit: ee51ca7b3091d96f9428199412038c1285099085
---

# Engineering Temporal Systems — Textbook Series

This special feature develops reusable mathematical and engineering techniques from the Video Observatory investigation. It is separate from the four implementation reports in [[PROJ - Video Observatory - Technical Deep Dive Series]]. The implementation pin identifies inspected product behavior; new examples are explicitly educational rather than retrospectively attributed to the product.

## Reading order and current publication

1. [[ARTICLE - Engineering Temporal Systems - 01 - Multiresolution Visualization]] — display resolution, integer coordinates, canonical grids, bounded geometry and asynchronous replacement.
2. [[ARTICLE - Engineering Temporal Systems - 02 - Temporal Coordination]] — general clock mathematics, bounded feedback and an executed four-processor simulation.
3. [[ARTICLE - Engineering Temporal Systems - 03 - Mergeable Summaries]] — aggregation algebra, missing data, stable variance and tested partition invariants.
4. [[ARTICLE - Engineering Temporal Systems - 04 - Bounded Asynchronous Systems]] — publication eligibility, ownership, bounded scheduling and a useful-versus-blocked experiment.
5. [[ARTICLE - Engineering Temporal Systems - 05 - Indexing Historical Video]] — sample-aware plans, real PTS/DTS evidence and verified non-keyframe decoding.
6. [[ARTICLE - Engineering Temporal Systems - 06 - HLS fMP4 and MSE]] — actual fragment delivery, explicit timestamp mapping, observed browser frames and cleanup.
7. [[ARTICLE - Engineering Temporal Systems - 07 - Coordinating Historical Playback]] — session-window reuse/reopening, delayed reports, camera-specific gaps and tested archive coordination.
8. [[ARTICLE - Engineering Temporal Systems - 08 - Safe Frame Presentation]] — frame evidence, authority and visibility lifetimes, deterministic closure/revocation races.

The historical-media sequence answers four distinct questions: which recording contains the target, how its bytes reach the decoder, which time playback should follow, and when a frame is eligible to appear.

## Reproducible examples and evidence

The [example README](_assets/temporal-systems/README.md) documents executable modules, commands and limits. All eight chapters and their examples are written. The shared suite has 30 tests, including 120 bounded presentation-event permutations. Final contract-wide publication and cross-chapter review remain in progress; chapter existence alone is not the completion criterion.

UTC values use integer microseconds; local media time uses seconds; encoded timestamps use an explicit timescale. Intervals are half-open. Simulation outputs, retained browser observations, allocation estimates and physical capture synchronization are different evidence categories throughout the series.
