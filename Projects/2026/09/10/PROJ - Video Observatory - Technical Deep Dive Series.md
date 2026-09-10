---
title: Video Observatory — Technical Deep Dive Series
aliases: [Video Observatory Engineering Articles]
tags: [project, article, video, architecture]
status: active
type: project
created: 2026-09-07
written: 2026-09-10
repo: /home/manuel/code/wesen/2026-09-07--streaming-system
source_commit: ee51ca7b3091d96f9428199412038c1285099085
---

# Video Observatory — Technical Deep Dive Series

These four articles explain the difficult parts of the browser implementation and synthetic load laboratory at the September 10 checkpoint. They are technical project reports written as standalone engineering chapters: definitions precede algorithms, worked examples explain invariants, and source references distinguish implementation from experimental evidence.

> [!summary]
> The series covers viewport/resource coordination, historical-media synchronization, semantic aggregation and realistic load experiments. The synthetic lab is complete; that does not establish production-backend integration or hardware qualification.

## Read the articles

1. [[ARTICLE - Video Observatory - Scrolling Through a Day of Video Without Loading a Day of Video]] derives viewport transformations and canonical resource resolution, then explains virtualization, worker rendering, budgets and stale-result admission. It distinguishes the LOD helper's optional hysteresis from the lab server's actual calls without previous-level state.
2. [[ARTICLE - Video Observatory - Synchronizing Four Video Players Against One UTC Clock]] develops fragment-local time mappings, session grants, monotonic coordination, readiness and drift correction. It analyzes the actual moving-master recovery defect and distinguishes frame-callback evidence from weaker media-time fallback.
3. [[ARTICLE - Video Observatory - Preserving Meaning While Aggregating Millions of Observations]] derives weighted summaries and aligned pyramids, follows validity through protobuf admission and inspection, and separates point observations, bucket extents and recording coverage.
4. [[ARTICLE - Video Observatory - Building a Synthetic Lab That Exercises the Real Product]] explains deterministic content, real encoded resources, bounded generators, shared transport impairment and cache-reset semantics. It analyzes cold/warm, error and media-coexistence observations without converting them into universal benchmark claims.

Each article defines its own terms and can be read independently. The cross-links identify related mechanisms rather than requiring the reader to reconstruct the implementation from several notes.

## Project and evidence provenance

The source repository is `/home/manuel/code/wesen/2026-09-07--streaming-system`, pinned here to `ee51ca7b3091d96f9428199412038c1285099085`. Its `web-ui/` directory contains the implementation; the WEBUI-LAB-001 ticket under `ttmp/2026/09/09/` contains the guide, diary, exact failures and final findings. No application code was changed to write these articles.

Earlier context remains in [[PROJ - Video Observatory - Evidence Correctness in a Browser Video Timeline]] and [[PROJ - Video Observatory Backend - Verified Recording and Authenticated Playback]]. These historical notes describe their own checkpoints and are not overwritten by this series.

Figures and primary experiment evidence are copied into the colocated `_assets/` directory so the vault does not depend on cross-repository image links. [The original sixty-export campaign](_assets/vo-deep-dive-campaign.json) records a 907,110-ms headed Chromium/Xvfb investigation. [The retained validation log](_assets/vo-deep-dive-validation.log) records 25 production-build browser cases, eight lab-browser cases and 92 unit/property tests at the source checkpoint. These are retained executed results, not test runs performed for documentation publication.

## Reading the limits correctly

The examples distinguish generated numeric/image patterns from generated video; the lab does not claim that its thumbnails were extracted from its HLS clips. Its noon recording window is only 24 seconds. Unknown clock uncertainty, null GPU elapsed time, sampled ownership maxima and bounded recent percentiles remain explicitly qualified.

The four-player campaign's scheduling slowdown is an observation, not an isolated causal diagnosis. Opening diagnostics also changed video visibility and affected a screenshot; the caption preserves that fact. These limitations are part of the technical account, not omitted conditions behind a performance claim.

A separate discussion proposed a future, project-independent textbook series on visualization, temporal coordination, mergeable summaries and bounded asynchronous systems. The four published chapters here remain the requested project-grounded reports.
