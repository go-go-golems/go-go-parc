---
title: CNC and CAM Research Cluster
tags:
  - research
  - cnc
  - cam
  - manufacturing
  - transcripts
---

# CNC and CAM Research Cluster

## Research arc

The CNC material progresses from learning the Makera Z1 ecosystem and CAM algorithms to a typed, semantic JavaScript IR and a repaired Drop-Cutter reference implementation. The central design move is to stop treating G-code text as the primary program representation. Geometry, toolpath planning, canonical machine actions, analysis, simulation, and controller-specific emission are separate layers.

## Material synthesis

The **Dropcut** textbook and audit provide the strongest algorithmic core. They describe an upper-envelope/drop-cutter model over triangle meshes, tool-contact evaluation, roughing, raster/hybrid/waterline finishing, marching squares, fast sweeping, arc fitting, G-code export, and dexel verification. The audit focuses on the kinds of defects that make geometry code look correct while failing at boundaries: finite triangle validation, degenerate projections, grid consistency, asymptotic deciders, closed-loop seams, anisotropic fast sweeping, entry validation, adaptive midpoint checks, coverage guarantees, and exact cutter-location re-evaluation.

The **CNC IR report** then lifts the problem into a typed program architecture:

- immutable frame-aware geometry and branded units;
- a phase-indexed `Plan<A,B>` with lawful composition;
- a fluent `Job` API for machine actions;
- a serializable canonical IR and JSON Schema;
- static analysis for clearance, sequencing, limits, arcs, probing, and safe termination;
- an operational interpreter producing motion traces, observations, distances, and time estimates;
- capability-checked G-code profiles and a prototype adapter.

The strongest safety insight is structural: rapid-Z and rapid-XY are different constructors, so an unsafe mixed-axis rapid move is not representable in the conforming IR. This is a design guarantee, not physical collision certification.

The **Z1 protocol** material is deliberately more modest: a byte-transparent TCP/UDP recording proxy, controller/API archaeology, and an incremental learning path. It is an observation tool, not a controller replacement or safety layer.

## Major deliverables

- [[Transcripts/2026/08/08/Algorithm Textbook Creation/dropcut_cam_textbook|Drop-Cutter CAM textbook]] and PDF.
- [[Transcripts/2026/08/08/Algorithm Textbook Creation/dropcut_cam_algorithm_audit|Drop-Cutter algorithm audit]].
- [[Transcripts/2026/08/08/JS API for CNC CAM/CNC_CAM_IR_Design_Report|A Compositional JavaScript IR for CNC CAM]] and PDF.
- [[Transcripts/2026/08/02/Z1 Controller Development Guide/README|Z1 controller development guide]] and `z1-recording-proxy.zip`.
- Source conversations: [[Transcripts/2026/08/08/CHATGPT TRANSCRIPT - CNC API Design|CNC API Design]], [[Transcripts/2026/08/08/CHATGPT TRANSCRIPT - CNC CAM API Design|CNC CAM API Design]], [[Transcripts/2026/08/08/CHATGPT TRANSCRIPT - JS API for CNC CAM|JS API for CNC CAM]], [[Transcripts/2026/08/08/CHATGPT TRANSCRIPT - CNC GCODE Previewer Features|CNC GCODE Previewer Features]], [[Transcripts/2026/08/02/CHATGPT TRANSCRIPT - CAM algorithms resources|CAM algorithms resources]], and [[Transcripts/2026/08/01/CHATGPT TRANSCRIPT - Makera Z1 Overview|Makera Z1 Overview]].

## Evidence and limits

The archived Drop-Cutter test report states 14/14 executable tests and run-specific benchmarks. Those are useful evidence, not universal guarantees. The IR document explicitly says it is not a production-certified postprocessor. Physical validation still requires a machine-specific profile, controller simulation, fixture/stock verification, dry runs, and supervised proof-out.
