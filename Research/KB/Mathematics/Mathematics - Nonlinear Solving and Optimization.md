---
title: "Mathematics - Nonlinear Solving and Optimization"
aliases:
  - "Nonlinear solving"
  - "Newton methods"
  - "Optimization"
  - "Automatic differentiation"
tags:
  - knowledge-base
  - mathematics
  - optimization
  - numerics
status: active
type: knowledge-base
created: "2026-11-02"
---

# Nonlinear Solving and Optimization

This branch covers solving systems of nonlinear equations and minimizing objective functions: Newton-type iterations, globalization by trust regions and line search, derivatives by automatic differentiation, path following, and multi-objective design search.

Part of [[Mathematics]].

> [!summary]
> - Linearization is the central computation: every Newton-type step solves a linear model of the residual.
> - Trust regions, DogLeg and Levenberg–Marquardt make Newton's method robust far from a solution; continuation keeps a solution on the intended branch during edits.
> - A parametric design defines a feasible set; Pareto fronts, sampling and sensitivity analysis explore it.

## Concepts

- Finite differences versus forward- and reverse-mode automatic differentiation; AD tapes.
- Newton, Gauss–Newton, trust regions, DogLeg, Levenberg–Marquardt, line search.
- Continuation and branch tracking near tangency.
- Predictor–corrector tracing of solution curves.
- Feasible sets, Pareto dominance, Latin hypercube sampling, sensitivity, robust design, surrogate models.

## In the CAD textbook

[[Course - Engineering CAD from First Principles]] treats this topic in:

- [[Engineering CAD 05 - Jacobians and automatic differentiation|Chapter 5. Jacobians and automatic differentiation]]: linearization, finite differences and cancellation, automatic differentiation, the Rust tape.
- [[Engineering CAD 06 - Newton, Gauss–Newton, DogLeg and LM|Chapter 6. Newton, Gauss–Newton, DogLeg and LM]]: a worked Newton trace, trust regions, Levenberg–Marquardt, comparing solvers fairly.
- [[Engineering CAD 08 - Continuation, sparse structure and performance|Chapter 8. Continuation, sparse structure and performance]]: continuation and branch tracking.
- [[Engineering CAD 21 - Design-space search and robust optimization|Chapter 21. Design-space search and robust optimization]]: feasible sets, Pareto fronts, sampling, sensitivity and robust design.
- [[Engineering CAD 29 - Tracing intersections of curved surfaces|Chapter 29. Tracing intersections of curved surfaces]]: predictor–corrector tracing of an intersection curve.

## Elsewhere in the vault

### Projects and articles

- [[PROJECT REPORT - jigcad - Constraint Equations as Data and a Rust Renderer]]: the solver that runs Newton-type steps on sketch constraints.
- [[PROJECT REPORT - jigcad - Moving the Numeric Core of a Browser CAD Engine into Rust and WebAssembly]]: automatic differentiation and the solver in Rust.
- [[ARTICLE - Responsive Orthogonal Typography Solver - Pretext Poster Fitting Deep Dive]]: fitting a typographic poster as a search over layout parameters.
- [[ARTICLE - GateMate Symbolic - Inside an FPGA Rollback Solver]]: constraint propagation and backtracking search in hardware (discrete, not numerical).

### Optimization research (transcript artifacts)

- [[Transcripts/2026/08/20/CHATGPT TRANSCRIPT - Design Optimization Framework|Design Optimization Framework (transcript)]]: a framework for self-optimizing systems: search spaces, objectives, Pareto tradeoffs.
- [[Transcripts/2026/08/09/Branch Designing RAG Abstractions/A_Categorical_Backbone_for_Composable_Optimization|A categorical backbone for composable optimization]]: optimization problems composed categorically.
- [[Transcripts/2026/08/17/LLM Judges for Self-Optimization/llms_as_judges_textbook|LLMs as judges textbook]]: optimization with noisy model-based objectives.

## Gaps

Most optimization material in the vault concerns LLM systems and discrete search. Continuous Newton-type solving appears only in jigcad and the CAD textbook.

## Related topics

- [[Mathematics - Numerical Linear Algebra]]
- [[Mathematics - Curves and Surfaces]]
- [[Mathematics - Tolerancing, Uncertainty and Statistics]]
