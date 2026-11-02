---
title: "Mathematics - Numerical Linear Algebra"
aliases:
  - "Numerical linear algebra"
  - "Least squares"
  - "SVD"
  - "Jacobian rank"
tags:
  - knowledge-base
  - mathematics
  - linear-algebra
  - numerics
status: active
type: knowledge-base
created: "2026-11-02"
---

# Numerical Linear Algebra

Numerical linear algebra solves linear systems, least-squares problems and eigen/singular-value problems in floating-point arithmetic, with attention to stability and conditioning. In a CAD constraint solver every nonlinear step reduces to one of these linear problems.

Part of [[Mathematics]].

> [!summary]
> - A sketch's constraints form a residual vector; its Jacobian's rank counts the remaining degrees of freedom.
> - Least squares is an orthogonal projection; QR and the SVD solve it stably because orthogonal transformations preserve length.
> - Small singular values mark weakly determined directions; numerical rank is a diagnosis that depends on scaling and a threshold.

## Concepts

- Residual vectors and Jacobians; rank and nullity; under-, over- and redundantly constrained systems.
- Minimal inconsistent subsets of constraints.
- Least squares as orthogonal projection; normal equations versus QR; Cholesky.
- Singular value decomposition, pseudoinverse, minimum-norm steps.
- Condition numbers, column scaling, truncation and Tikhonov damping.
- Dense versus sparse Jacobians; reusing factorizations.

## In the CAD textbook

[[Course - Engineering CAD from First Principles]] treats this topic in:

- [[Engineering CAD 04 - Constraints become equations|Chapter 4. Constraints become equations]]: the residual vector, the Jacobian and local freedom, building a minimal solver.
- [[Engineering CAD 05 - Jacobians and automatic differentiation|Chapter 5. Jacobians and automatic differentiation]]: scaling the Jacobian before interpreting rank.
- [[Engineering CAD 07 - Redundancy, conflict and singularity|Chapter 7. Redundancy, conflict and singularity]]: redundant rows and rank, minimal inconsistent subsets, singular derivatives.
- [[Engineering CAD 08 - Continuation, sparse structure and performance|Chapter 8. Continuation, sparse structure and performance]]: units and conditioning, sparse Jacobians, factorization reuse.
- [[Engineering CAD 31 - The linear algebra underneath a geometric solver|Chapter 31. The linear algebra underneath a geometric solver]]: least squares as projection, orthogonal transforms, SVD, truncation and damping, numerical rank.

## Elsewhere in the vault

### Projects and articles

- [[PROJECT REPORT - jigcad - Constraint Equations as Data and a Rust Renderer]]: jigcad's constraint equations as a table the Rust solver linearizes.
- [[PROJECT REPORT - jigcad - Moving the Numeric Core of a Browser CAD Engine into Rust and WebAssembly]]: the Rust solver: Jacobians, least squares, the wasm boundary.
- [[ARTICLE - Kiln - Matrix Semantics Canonical Bindings and Numerical Acceptance]]: matrix products in a compiler, and numerical acceptance tolerances.
- [[ARTICLE - Kiln - Tensor-Core Matrix Products Built and Checked Without a GPU]]: blocked matrix products on tensor cores, checked against a reference.
- [[ARTICLE - Constraint-Based Layout on Canvas - Cassowary + Pretext + React]]: Cassowary solves linear equality and inequality constraints with a simplex method; text height enters by iteration.
- [[PROJ - Cassowary Constraint Layout Demo]]: the demo behind the Cassowary article.

## Gaps

Matrix work in the vault is either the jigcad solver or GPU matrix products (Kiln). There is no note on SVD-based diagnosis outside the CAD textbook.

## Related topics

- [[Mathematics - Nonlinear Solving and Optimization]]
- [[Mathematics - Floating-Point and Exact Arithmetic]]
- [[Mathematics - Rigid Motions and Kinematics]]
