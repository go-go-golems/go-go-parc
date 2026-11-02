---
title: "Engineering CAD from First Principles — Chapter 8. Continuation, sparse structure and performance"
aliases:
  - "Chapter 8. Continuation, sparse structure and performance"
tags:
  - course
  - cad
  - textbook
  - jigcad
status: active
type: course
created: 2026-11-02
course: "[[Course - Engineering CAD from First Principles]]"
---

# Chapter 8. Continuation, sparse structure and performance

[[Engineering CAD 07 - Redundancy, conflict and singularity|← Chapter 7. Redundancy, conflict and singularity]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 09 - Reliable decisions in planar geometry|Chapter 9. Reliable decisions in planar geometry →]]

A solver that works for a small sketch near the origin may fail when the same sketch is moved, resized or embedded in a larger model. Reliable CAD requires both numerical invariance and interactive performance. This chapter separates those problems and develops a benchmark that makes them measurable.

## 8.1 Units and conditioning

Let $J$ be the Jacobian of a residual system. If $J$ has singular values $\sigma_1\ge\dots\ge\sigma_n>0$, its two-norm condition number is $\kappa_2(J)=\sigma_1/\sigma_n$. Large $\kappa$ means small residual perturbations may produce large parameter changes.

Suppose one parameter is expressed in millimeters and another in radians, while residuals combine a positional error and an angular error. Changing the unit of length to meters multiplies some coordinates or derivatives by $10^{-3}$. Exact solutions do not change, but floating-point stopping conditions and estimated ranks can change if the solver ignores dimensions.

A scaling policy should specify a characteristic variable scale $d_j$ and constraint tolerance $\tau_i$, then solve for dimensionless coordinates $z_j=(x_j-x_{0,j})/d_j$ with dimensionless residuals $\widetilde F_i=F_i/\tau_i$. Crucially, the engineering meaning of $\tau_i$ is not always the same as a preconditioning weight for least squares. When constraints must all be satisfied, the final status should check **every original constraint** against its own tolerance.

## 8.2 Why local edits should use continuation

Imagine a sketch solution $x^*(p)$ that depends on a design parameter $p$, such as a length. At a regular solution, the implicit-function theorem gives

$$
J_x\frac{dx^*}{dp}+\frac{\partial F}{\partial p}=0.
$$

When $J_x$ is invertible, the local derivative is $dx^*/dp=-J_x^{-1}F_p$. This provides a predictor for the next configuration after a small parameter change. A corrector (Newton or DogLeg) then solves the modified constraints. This predictor–corrector idea is a **continuation method**.

Warm starts are the simplest continuation strategy: start from the previous solution. Jig already does that for unchanged sketch definitions. A stronger implementation can take smaller substeps when a large parameter edit threatens to cross a singularity or branch boundary.

%%FIG:8%%

## 8.3 A simple branch-tracking example

Consider $x^2=p$ with $p>0$. There are two branches $x_\pm(p)=\pm\sqrt p$. Starting at $p=4$ with $x=+2$, reducing $p$ to $1$ should normally yield $x=+1$, not $x=-1$. Warm starting makes the correct behavior likely for a local method. But as $p\to0$, the derivative $dx/dp=1/(2x)$ diverges. At the branch point the implicit-function theorem fails: the Jacobian $2x$ loses rank.

The solver should report that event rather than silently declaring the model inconsistent. The same phenomenon appears when circles become tangent or a mechanism reaches a toggle configuration.

**Try it.** [The conditioning bench](lab:sketch?id=conditioning) shows a deliberately small geometric feature moved far from the origin. Compare the exact derivative of a local quadratic with finite-difference estimates under different offsets and step rules. This is a model of the numerical issue, not a direct run of JigCAD.

## 8.4 Dense versus sparse Jacobians

A full sketch with $n$ parameters and $m$ residuals has an $m\times n$ Jacobian. Most geometric constraints touch only a few entities, so the Jacobian is structurally sparse. A distance between two points affects at most four position coordinates; its other partial derivatives are zero.

In a large *connected* sketch, dense QR costs roughly cubic work in the smaller matrix dimension, while sparse methods can exploit the incidence graph and avoid work on zeros. However, sparse QR introduces fill-in depending on ordering, and using a generic sparse package can increase overhead for small sketches. Profiling must establish the crossover.

Jig's current Rust `linalg.rs` implements dense Householder QR and Cholesky, with graph decomposition at a higher layer. That is sensible for modest sketch clusters. A high-value optimization path is to retain dense methods for small clusters while introducing sparse Jacobian assembly and sparse factorization only for large coupled clusters.

## 8.5 Factorization reuse and incremental constraint solving

A local edit often affects only one parameter and a small neighborhood of the constraint graph. At the graph level, solve unaffected connected components only when their dependencies actually changed. At the numeric level, reuse the sparsity pattern, permutation and possibly a factorization update if the Jacobian changes slightly.

Be careful: reusing an old factorization without checking the new Jacobian can break convergence. A safe cache entry includes the structure it assumes, a generation identifier, and explicit invalidation when equations are inserted, deleted or change branch.

## 8.6 A useful benchmark matrix

Benchmark *dimensions* of difficulty, not just popular models. Use small/medium/large systems; well-conditioned and near-singular conditions; cold and warm starts; consistent and inconsistent constraints; many disconnected clusters and one highly connected cluster; coordinate offsets from zero to very large values; and shapes scaled across several orders of magnitude.

Record solve time, memory, Jacobian evaluations, residual at termination, rank, branch identity and failure classification. Use mathematical oracles wherever possible. Example: construct $n$ independent copies of a two-variable analytic system and assert that solving $n$ copies does not change any individual answer. Then tie them with a few constraints to measure sparse coupling.

> **Exercise.** Derive the implicit derivative for a circle intersecting the line $y=c$ as $c$ approaches the radius. Identify the singular parameter value and explain why a predictor becomes unstable there.

> **Careful.** “Use sparse matrices” is not a complete performance proposal. The sparsity pattern, numerical rank, ordering, refactorization policy and WASM allocation costs all matter.

### Deeper study: conditioning is not the same problem as predicate robustness

A nearly parallel line intersection is sensitive to small input changes even when computed by a stable algorithm. A rounded orientation sign can instead cause an inconsistent discrete decision about the represented input. [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation|Chapter 26]] separates these problems using an integer determinant with exact value −1, while [[Engineering CAD 31 - The linear algebra underneath a geometric solver|chapter 31]] analyzes a nearly rank-deficient linear system. Both need scaling awareness, but exact predicates and numerical regularization solve different contracts.

## Toward a reusable API

```text
ScalePolicy.variable(entity, coordinate) -> characteristic scale
ScalePolicy.residual(constraint) -> feasibility scale
Continuation.advance(solution, parameterDelta) -> predictor/corrector trace
SparseJacobian.pattern() -> row/column incidence
BenchmarkCase { geometry, parameters, expectedStatus, oracle, seed }
```

## Key points

Numerical scaling affects conditioning, rank and stopping decisions. Continuation helps preserve branches across parameter edits. Graph decomposition is distinct from sparse linear algebra. Large coupled sketches may need sparse factorizations, but small sketches benefit from simple dense algorithms. Performance claims need controlled benchmark families and correctness oracles.

## Further reading

- [Nocedal and Wright](https://link.springer.com/book/10.1007/978-0-387-40065-5) covers scaling, conditioning and trust-region numerical methods.
- [JigCAD Rust linear algebra](https://github.com/go-go-golems/jig/blob/main/import/jigcad/rust/jig-compute/src/linalg.rs) defines the present dense baseline.
- [JigCAD solver orchestration](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/sketch/solver.js) shows cluster decomposition and warm-start behavior.

---

[[Engineering CAD 07 - Redundancy, conflict and singularity|← Chapter 7. Redundancy, conflict and singularity]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 09 - Reliable decisions in planar geometry|Chapter 9. Reliable decisions in planar geometry →]]
