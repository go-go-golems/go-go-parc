---
title: "Mathematics - Tolerancing, Uncertainty and Statistics"
aliases:
  - "Tolerancing"
  - "Uncertainty"
  - "Statistics"
  - "Probability"
tags:
  - knowledge-base
  - mathematics
  - statistics
  - manufacturing
status: active
type: knowledge-base
created: "2026-11-02"
---

# Tolerancing, Uncertainty and Statistics

This topic covers how to reason about values that are not exact: worst-case intervals, statistical tolerance stacks, measurement uncertainty, and the probability and statistics behind them. In CAD and manufacturing it decides whether parts fit; elsewhere in the vault it is Bayesian modeling and evaluation.

Part of [[Mathematics]].

> [!summary]
> - A worst-case interval guarantee and a probabilistic tolerance stack answer different questions and must not be mixed.
> - A tolerance in a model is a policy with topological effects, not an equality test.
> - Measurement uncertainty is a property of the measurement process, not of the drawing.

## Concepts

- Interval arithmetic for fits (shaft–hole clearance).
- Kinds of error: modeling tolerance, manufacturing variation, measurement uncertainty, numerical error.
- Tolerance budgets across a pipeline; GD&T and metrology.
- Layered-manufacturing anisotropy; sheet-metal bend allowance and K-factor.
- Robust design under uncertainty.
- Probability models, Bayesian inference, hierarchical models, posterior decisions.

## In the CAD textbook

[[Course - Engineering CAD from First Principles]] treats this topic in:

- [[Engineering CAD 19 - Tolerance, healing and metrology|Chapter 19. Tolerance, healing and metrology]]: four meanings of error, a shaft–hole fit from intervals, tolerance budgets, healing, metrology.
- [[Engineering CAD 20 - Manufacturing, drawings and sheet metal|Chapter 20. Manufacturing, drawings and sheet metal]]: fit-aware printed holes, flat patterns and bend allowance, drawings and GD&T.
- [[Engineering CAD 21 - Design-space search and robust optimization|Chapter 21. Design-space search and robust optimization]]: robust design under uncertainty.

## Elsewhere in the vault

### Manufacturing and CNC

- [[PROJ - Makera Z1 Control - Typed Interfaces and Explicit Uncertainty]]: a controller that represents what it does not know about the machine.
- [[Transcripts/2026/08/16/Branch Z1 Controller Review/Compiling_Metal|Compiling Metal]]: tolerances and error budgets in a CAM compiler.
- [[Transcripts/2026/08/08/CHATGPT TRANSCRIPT - CNC CAM API Design|CNC CAM API Design (transcript)]]: tolerances as first-class values in a CAM API.
- [[ARTICLE - PaperS3 E-Paper Qualification - Physics, Waveforms, and Physical Drive]]: measurement and worst-case reasoning in hardware qualification.

### Probability and statistics

- [[PROJECT REPORT - Bayesian Marketing Day 1 - Generative Models, Conjugate Validation, and the Poisson Failure Pattern]]: generative models, conjugate checks, posterior predictive checks.
- [[PROJECT REPORT - Bayesian Marketing Day 2 - Hierarchical Recovery of Customer Heterogeneity]]: hierarchical models and partial pooling.
- [[PROJECT REPORT - Bayesian Marketing Day 3 - Product Choice, Willingness to Pay, and the Posterior Price Decision]]: choice models and decisions under the posterior.
- [[PROJECT REPORT - Bayesian Marketing Day 4 - Causal Identification, Membership Economics, and the Targeting Decision]]: causal identification.
- [[PROJ - TTC Customer Clustering - Tier B Customer Segmentation]]: clustering and segmentation statistics.
- [[PROJECT REPORT - Factory Multi-Camera Person Tracking - Research Program, Literature System, and the Twin-Lab Series]]: joint estimation and tracking under uncertainty (Kalman-style filtering).
- [[Transcripts/2026/08/17/LLM Judges for Self-Optimization/llms_as_judges_textbook|LLMs as judges textbook]]: measurement error and agreement statistics for model-based evaluation.

## Gaps

Statistics in the vault is mostly Bayesian modeling and evaluation. Mechanical tolerancing (fits, GD&T, stacks) appears only in the CAD textbook and the CNC notes.

## Related topics

- [[Mathematics - Floating-Point and Exact Arithmetic]]
- [[Mathematics - Point-Set Topology]]
- [[Mathematics - Nonlinear Solving and Optimization]]
