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
3. Mergeable Summaries — aggregation algebra, missing data and stable variance. Writing remains in progress.
4. Bounded Asynchronous Systems — publication eligibility, ownership and measurement. Writing remains in progress.
5. From UTC to a Decodable Frame — indexing and decode dependencies. Writing remains in progress.
6. Streaming an Archive Through the Browser — HLS, fragmented MP4 and MSE. Writing remains in progress.
7. Coordinating Historical Playback — apply the clock foundation to archive sessions. Writing remains in progress.
8. When Is a Frame Safe to Show? — state machines, authorization and resource lifetimes. Writing remains in progress.

The historical-media sequence answers four distinct questions: which recording contains the target, how its bytes reach the decoder, which time playback should follow, and when a frame is eligible to appear.

## Reproducible examples and evidence

The [example README](_assets/temporal-systems/README.md) documents executable modules, commands and limits. The timeline model and its tests are available now. This series is not yet complete; missing chapters are listed as writing work rather than linked to nonexistent notes.

UTC values use integer microseconds; local media time uses seconds; encoded timestamps use an explicit timescale. Intervals are half-open. Simulation outputs, retained browser observations, allocation estimates and physical capture synchronization are different evidence categories throughout the series.
