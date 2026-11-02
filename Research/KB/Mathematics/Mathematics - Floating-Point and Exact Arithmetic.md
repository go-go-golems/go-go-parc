---
title: "Mathematics - Floating-Point and Exact Arithmetic"
aliases:
  - "Floating-point arithmetic"
  - "Exact arithmetic"
  - "Robust predicates"
  - "Numerical precision"
tags:
  - knowledge-base
  - mathematics
  - numerics
  - arithmetic
status: active
type: knowledge-base
created: "2026-11-02"
---

# Floating-Point and Exact Arithmetic

This topic covers how computers represent numbers (IEEE 754 floating point, fixed point, integers, rationals) and how rounding affects programs. In geometry the decisive issue is the sign of a computed value near zero: a wrong sign changes topology, not just a coordinate.

Part of [[Mathematics]].

> [!summary]
> - A fixed epsilon cannot repair a predicate; adaptive exact predicates compute the sign exactly when an error bound says the float result is uncertain.
> - Exact predicates do not make constructed coordinates exact; each construction needs its own policy.
> - Symbolic perturbation answers a deliberately changed question so degenerate input never needs a special case.

## Concepts

- IEEE 754 rounding, cancellation, error bounds near zero.
- Adaptive exact predicates (Shewchuk), filters, integer determinant oracles.
- Symbolic perturbation (Simulation of Simplicity).
- Interval enclosures for certified signs.
- Fixed-point arithmetic in rasterizers and firmware; GPU precision qualifiers.
- Quantization: mapping many values to few, and dithering as error shaping.

## In the CAD textbook

[[Course - Engineering CAD from First Principles]] treats this topic in:

- [[Engineering CAD 01 - A CAD system is a chain of contracts|Chapter 1. A CAD system is a chain of contracts]]: a worked failure: tangent holes.
- [[Engineering CAD 09 - Reliable decisions in planar geometry|Chapter 9. Reliable decisions in planar geometry]]: floating-point arithmetic near zero, adaptive exact predicates, tolerance-induced topology change.
- [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation|Chapter 26. Predicates, constructions and symbolic perturbation]]: a lost sign worked through, filters, exact predicates versus constructions, symbolic perturbation.

## Elsewhere in the vault

### Projects and articles

- [[ARTICLE - Kiln - Numerical Contracts Correctness Gates and Eleven Complete Tasks]]: an explicit contract for FP32 rounding preserved through compiler passes and CUDA.
- [[ARTICLE - TTF Glyph-Outline VM Renderer - Architecture and Implementation]]: fixed-point arithmetic in a font rasterizer.
- [[ARTICLE - TTF Rasterizer Bug Hunting - Scale, Windings, and Coverage]]: fixed-point scale errors and corrupted winding values.
- [[PROJECT REPORT - Falllinie Native GLES Spike - Deterministic Terrain, Print Shaders and Mali Depth Precision]]: a depth sampler that needed `highp` on a Mali GPU.
- [[signal-quantization-and-sampling]]: quantization error and why dithering converts it into high-frequency noise.
- [[ARTICLE - Thermal Dithering Algorithms - Almanach Rasterization Deep Dive]]: dithering algorithms for 1-bit thermal output.
- [[ARTICLE - Engineering Temporal Systems - 01 - Multiresolution Visualization]]: integer coordinates and canonical grids for a timeline.

### CAM research (transcript artifacts)

- [[Transcripts/2026/08/16/Z1 Controller Review/Certificate_Carrying_CAM_Compilers|Certificate-Carrying CAM Compilers]]: approximation, tolerances and certified bounds in toolpath generation.
- [[Transcripts/2026/08/16/Branch Z1 Controller Review/Compiling_Metal|Compiling Metal]]: numerical trust in a CAM compiler: invariants, certificates, runtime assurance.

## Gaps

The vault has many practical precision notes (fixed point, GPU precision, FP32 contracts) but no note on exact geometric predicates outside the CAD textbook.

## Related topics

- [[Mathematics - Computational Geometry]]
- [[Mathematics - Numerical Linear Algebra]]
- [[Mathematics - Tolerancing, Uncertainty and Statistics]]
