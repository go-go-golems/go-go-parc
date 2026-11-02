---
title: "Mathematics - Curves and Surfaces"
aliases:
  - "Curves and surfaces"
  - "Bézier and NURBS"
  - "Differential geometry of curves"
tags:
  - knowledge-base
  - mathematics
  - geometry
  - cad
status: active
type: knowledge-base
created: "2026-11-02"
---

# Curves and Surfaces

This branch studies curves and surfaces as parameterized maps from a parameter domain into space, and the derivative quantities (tangents, normals, curvature) that describe how they bend. In CAD it is the mathematics of the *geometry* layer: every edge carries a curve and every face carries a surface.

Part of [[Mathematics]].

> [!summary]
> - A curve is a map t ↦ C(t); a surface is a map (u, v) ↦ S(u, v). Evaluation is not topology: one point can have several parameters.
> - Bézier, B-spline and NURBS curves are built from polynomial and rational basis functions; rational weights are what make an exact circle possible.
> - Continuity has two vocabularies: parametric (C1, C2: matching derivatives) and geometric (G1, G2: matching tangent direction and curvature).

## Concepts

- Parameterized maps; control points; interpolation versus approximation.
- Bernstein polynomials, de Casteljau evaluation, Bézier, B-splines and knots, NURBS and rational weights.
- Tangents, normals, curvature, Frenet and rotation-minimizing frames for sweeps.
- C1/C2 versus G1/G2 continuity at a junction of two pieces.
- Chord error: how far a polygon misses an arc, which decides tessellation density.
- Offsets and their singularities; implicit versus parametric surfaces; tracing the intersection curve of two surfaces.

## In the CAD textbook

[[Course - Engineering CAD from First Principles]] treats this topic in:

- [[Engineering CAD 02 - Curves, surfaces and rational geometry|Chapter 2. Curves, surfaces and rational geometry]]: Bézier curves from Bernstein polynomials, why rational curves are necessary, and chord error.
- [[Engineering CAD 11 - Boolean solids, blending and healing|Chapter 11. Boolean solids, blending and healing]]: fillets as a surface-construction problem, shelling and offsets.
- [[Engineering CAD 14 - B-rep, STEP, meshes and manufacturing|Chapter 14. B-rep, STEP, meshes and manufacturing]]: exact boundary descriptions versus sampled meshes.
- [[Engineering CAD 18 - Surface continuity and advanced modeling|Chapter 18. Surface continuity and advanced modeling]]: continuity at a Bézier junction, lofts, sweeps and offset singularities.
- [[Engineering CAD 20 - Manufacturing, drawings and sheet metal|Chapter 20. Manufacturing, drawings and sheet metal]]: chord error decides how many segments a printed round hole needs.
- [[Engineering CAD 29 - Tracing intersections of curved surfaces|Chapter 29. Tracing intersections of curved surfaces]]: tracing intersections of curved surfaces with a predictor–corrector method.

## Elsewhere in the vault

### Projects and articles

- [[ARTICLE - TTF Glyph-Outline VM Renderer - Architecture and Implementation]]: glyph outlines are quadratic Bézier curves; the VM flattens them into edges before rasterizing.
- [[ARTICLE - TTF Rasterizer Bug Hunting - Scale, Windings, and Coverage]]: what goes wrong between a curve outline and pixel coverage.
- [[Research/Institute/Magazine/Issues/002/03 - From Outline to Pixel|From Outline to Pixel (magazine)]]: the same rasterizer told as a magazine piece: outlines, fill rules, coverage.
- [[PROJECT REPORT - jigcad - Architecture of a Browser CAD Workbench, from Script to Agent]]: where B-spline sketch geometry enters jigcad.

### CAM research and textbooks (transcript artifacts)

- [[dropcut_cam_textbook]]: the drop-cutter CAM textbook: tool contact with parametric surfaces, arc length, curvature limits on feed.
- [[Transcripts/2026/08/08/CHATGPT TRANSCRIPT - CNC Precision Re-mounting Techniques|CNC Precision Re-mounting Techniques]]: Bézier, B-spline and NURBS vocabulary while planning a two-sided milling job.
- [[Transcripts/2026/08/16/CHATGPT TRANSCRIPT - Branch Z1 Controller Review|Branch Z1 Controller Review]]: spline and NURBS motion in a CNC controller and CAM compiler review; de Casteljau.
- [[Transcripts/2026/08/01/CHATGPT TRANSCRIPT - CFS Geometry and CNC|CFS Geometry and CNC]]: Connected Fermat Spirals: space-filling toolpath curves and their curvature.

## Gaps

The vault has no note that develops NURBS or surface differential geometry on its own; the CAD textbook chapters are the reference. Font outlines (quadratic Bézier) are the only curve family that has a full implementation note.

## Related topics

- [[Mathematics - Computational Geometry]]
- [[Mathematics - Floating-Point and Exact Arithmetic]]
- [[Mathematics - Nonlinear Solving and Optimization]]
