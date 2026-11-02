---
title: "Engineering CAD from First Principles — Chapter 6. Newton, Gauss–Newton, DogLeg and LM"
aliases:
  - "Chapter 6. Newton, Gauss–Newton, DogLeg and LM"
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

# Chapter 6. Newton, Gauss–Newton, DogLeg and LM

[[Engineering CAD 05 - Jacobians and automatic differentiation|← Chapter 5. Jacobians and automatic differentiation]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 07 - Redundancy, conflict and singularity|Chapter 7. Redundancy, conflict and singularity →]]

The nonlinear equations of a sketch cannot usually be solved by one matrix multiplication. The solver constructs a local approximation, chooses a step, and checks whether the step actually improved the original constraints. This chapter derives Jig's three principal numerical methods and traces a concrete problem to a solution.

## 6.1 From root finding to least squares

For $m=n$ and invertible $J$, Newton's method solves the linearized equation

$$
J(x_k)p_k=-F(x_k),\qquad x_{k+1}=x_k+p_k.
$$

When $m\neq n$ or constraints are inconsistent, the natural objective is $\phi(x)=\frac12\|F(x)\|_2^2$. Its gradient is $\nabla\phi=J^\top F$, and its exact Hessian is

$$
\nabla^2\phi=J^\top J+\sum_i F_i\nabla^2F_i.
$$

**Gauss–Newton** drops the second term, leading to a linear least-squares step that minimizes $\|F+Jp\|^2$. Near an exact solution, the discarded term is small because $F$ is small. Far from a solution or in poorly conditioned geometry, an unrestricted Gauss–Newton step can increase the true residual dramatically.

## 6.2 A fully worked Newton trace

Use the circle and line from Chapter 5:

$$
F(x,y)=(x^2+y^2-25,\;x+y-3).
$$

At $x_0=(4,-1)$, $F=(-8,0)$ and $J=\bigl[\begin{smallmatrix}8&-2\\1&1\end{smallmatrix}\bigr]$. Solve $Jp=(8,0)^\top$. The second row gives $p_y=-p_x$; the first then gives $10p_x=8$, so $p=(0.8,-0.8)$. The new point is $(4.8,-1.8)$, whose first residual is $1.28$ and second residual is exactly zero.

A second Newton step respects $p_x+p_y=0$ and solves $2(x-y)p_x=-1.28$. At $(4.8,-1.8)$, $2(x-y)=13.2$, so $p_x=-1.28/13.2\approx-0.096969697$, giving $(4.703030303,-1.703030303)$. The remaining first residual is about $0.0188062$. A further step reaches the positive-$x$ solution

$$
x^*=\frac{3+\sqrt{41}}2\approx4.701562119,\quad y^*=\frac{3-\sqrt{41}}2\approx-1.701562119.
$$

This is a locally well-behaved example. If the initial guess lies on a singular or almost-singular configuration, the same method can fail. If the user starts near the other circle-line intersection, it will normally converge to that *different* valid branch.


%%FIG:6%%

## 6.3 Why a trust region helps

A **trust-region method** minimizes a model $m_k(p)$ subject to $\|p\|\le\Delta_k$. The radius $\Delta_k$ defines how far we trust the local linearization. The important ratio is

$$
\rho_k=\frac{\phi(x_k)-\phi(x_k+p_k)}{m_k(0)-m_k(p_k)}.
$$

If $\rho$ is near one, actual improvement matches predicted improvement. If it is negative, the step made the objective worse; shrink the radius and try again. If it is large and the step reaches the boundary, the model is reliable enough to enlarge the region.

The **DogLeg** approximation joins a steepest-descent step to a Gauss–Newton step. Let $g=J^\top F$ and $B\approx J^\top J$. The Cauchy step along $-g$ is

$$
p_U=-\frac{g^\top g}{g^\top B g}g.
$$

The DogLeg path runs from the origin to $p_U$, then to the Gauss–Newton step $p_{GN}$. Choose the point on that piecewise-linear path satisfying the trust-radius constraint. This approximates the trust-region solution without a complete constrained quadratic optimization each iteration.

**Try it.** In [the nonlinear solver bench](lab:sketch?id=newton), change the starting point and compare Newton and damped steps. The bench uses a simplified two-residual model to show iteration paths; it is a teaching implementation, not Jig's full solver.

## 6.4 Levenberg–Marquardt and damping

LM stabilizes Gauss–Newton by solving a damped system, commonly

$$
(J^\top J+\mu I)p=-J^\top F.
$$

For small $\mu$, the step approaches Gauss–Newton if the system is well conditioned. For large $\mu$, the step approximates a small gradient-descent step. The damping parameter is updated according to agreement between predicted and actual improvement.

Jig's Rust solver uses Cholesky on a damped normal matrix. This is practical for modest dense sketches, but forming $J^\top J$ can square the condition number in the undamped idealization. A QR- or SVD-based least-squares formulation is preferable when near-singular systems dominate.

## 6.5 What the Rust implementation does

The source [solve.rs](https://github.com/go-go-golems/jig/blob/main/import/jigcad/rust/jig-compute/src/solve.rs) implements DogLeg, LM and Newton. It computes residual/Jacobian values from a tape, tries a requested strategy, and may fall back to LM after DogLeg fails. Its Newton method uses a bounded line search. The high-level JavaScript solver partitions clusters and orchestrates conflict diagnosis.

There are practical heuristics: stopping thresholds, maximum iterations, trust-radius updates, early-stall detection and a retry after perturbing a singular starting drawing. Such heuristics are necessary engineering choices, but they need tests across scales and problem families.

One mathematical limitation is fundamental: local descent cannot prove a system is globally infeasible. Finding a nonzero local minimum or exhausting an iteration budget is evidence of nonconvergence, not a proof of contradiction.

## 6.6 How to compare solver algorithms fairly

A useful benchmark reports success **and** correctness. Record the norm of the original (unscaled) geometric residual, the scaled residual, wall-clock time, number of residual/Jacobian evaluations, number of fallbacks, chosen branch, and whether a ground-truth solution exists. For a constrained design, also test small parameter changes around a solved configuration.

An algorithm that rapidly returns a plausible-looking but incorrect configuration should not score as success. Neither should an algorithm that reports “overconstrained” after hitting a small iteration cap.

> **Exercise.** Starting from $(4,-1)$, reproduce the two Newton steps above. Then compute the same first step with a Levenberg–Marquardt damping $\mu=1$. Compare the step norms and the residual decrease.

> **Careful.** The expression $J^\top J+\mu I$ has no automatic physical meaning when columns have different units. Use variable scaling if the sketch combines lengths and angles.

### Deeper study: inspect the step before selecting a nonlinear strategy

The Gauss–Newton or Newton step relies on a linear solve whose rank, scaling and solution convention must be known. [[Engineering CAD 31 - The linear algebra underneath a geometric solver|Chapter 31]] supplies worked QR and SVD examples and derives an augmented least-squares formulation for damping. It distinguishes a basic solution from a minimum-norm solution; merely saying “QR is used” does not establish the latter for every rank-deficient problem. Use the singular-value lab to compare residual improvement against step magnitude.

## Toward a reusable API

```text
Problem.residual(x) -> F(x)
Problem.jacobian(x) -> J(x)
Solver.solve(problem, initial, strategy) -> SolveReport
SolveReport { status, x, residual, scaledResidual, iterations,
              rank, fallback, trustTrace, branch, explanation }
```

## Key points

Newton solves a local linearization; Gauss–Newton minimizes a linearized residual. A trust region checks how much the local model can be believed. DogLeg approximates the trust-region step along two directions. LM adds damping to stabilize the least-squares solve. None of these local methods can, alone, certify global infeasibility or branch identity.

## Further reading

- [Nocedal and Wright, *Numerical Optimization*](https://link.springer.com/book/10.1007/978-0-387-40065-5) treats trust regions and nonlinear least squares in detail.
- [JigCAD Rust solver](https://github.com/go-go-golems/jig/blob/main/import/jigcad/rust/jig-compute/src/solve.rs) contains the exact algorithm choices, limits and fallback logic.
- [JigCAD Rust QR/Cholesky implementation](https://github.com/go-go-golems/jig/blob/main/import/jigcad/rust/jig-compute/src/linalg.rs) reveals the linear subproblems solved at each step.

---

[[Engineering CAD 05 - Jacobians and automatic differentiation|← Chapter 5. Jacobians and automatic differentiation]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 07 - Redundancy, conflict and singularity|Chapter 7. Redundancy, conflict and singularity →]]
