---
title: "Engineering CAD from First Principles — Chapter 31. The linear algebra underneath a geometric solver"
aliases:
  - "Chapter 31. The linear algebra underneath a geometric solver"
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

# Chapter 31. The linear algebra underneath a geometric solver

[[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification|← Chapter 30. Tetrahedral quality and topology-safe simplification]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 32 - A source-guided implementation course|Chapter 32. A source-guided implementation course →]]

A nonlinear sketch solver repeatedly solves a linear approximation. If that approximation is rank-deficient, badly scaled, or nearly singular, the choice of factorization determines both the step and the diagnosis. This chapter derives least squares, orthogonal factorization, minimum-norm solutions, and singular-value filtering before connecting them back to JigCAD's solver architecture.

**Source basis.** Hoffmann §6.2.4 introduces SVD for possibly singular geometric systems. The LAPACK Users' Guide distinguishes full-rank QR/LQ solvers, complete orthogonal factorization, and SVD-based minimum-norm solvers. This chapter's small systems and derivations are original teaching material. The user research note recommends Trefethen–Bau and Nocedal–Wright for further study; the full texts of those books were not supplied for this expansion. [[Engineering CAD B - Source Library#^ref-hoffmann-upload|Hoffmann]] · [[Engineering CAD B - Source Library#^ref-lapack-lls|LAPACK least squares]] · [[Engineering CAD B - Source Library#^ref-lapack-orthogonal|LAPACK orthogonal factorizations]].

## 31.1 Linearize one step, not the whole geometry

A sketch defines a residual vector $F(x)\in\mathbb R^m$ from parameters $x\in\mathbb R^n$. Near the current iterate,

$$
F(x+\delta)\approx F(x)+J\delta,
$$

where $J$ is the Jacobian. The Gauss–Newton step solves

$$
\min_\delta\|J\delta+F(x)\|_2.
$$

This is a linear least-squares problem, even though the original constraints are nonlinear. Its solution is only locally predictive. A perfect linear solve cannot make a poor linearization valid far from the current point; trust regions and line searches control that separate issue.

If the columns of $J$ are independent and $m\ge n$, the least-squares minimizer is unique. If they are dependent, there may be many minimizers. A minimum-norm rule chooses one, but the norm itself encodes a metric on the parameters. Mixing millimeters and radians without scaling makes that choice arbitrary.

## 31.2 Least squares as orthogonal projection

For $A\in\mathbb R^{m\times n}$ and $b\in\mathbb R^m$, least squares chooses $x$ so that $Ax$ is the closest point to $b$ in the column space of $A$. At a minimizer, the residual $r=Ax-b$ is orthogonal to every column:

$$
A^T(Ax-b)=0.
$$

These are the normal equations. They characterize the solution, but forming and solving $A^TA$ is not always the best algorithm. For full column rank in the 2-norm, $\kappa_2(A^TA)=\kappa_2(A)^2$, so the conditioning can become much worse.

Use a concrete system:

$$
A=\begin{bmatrix}1&1\\1&-1\\0&1\end{bmatrix},\qquad
b=\begin{bmatrix}3\\1\\2\end{bmatrix}.
$$

The columns are orthogonal, with squared norms $2$ and $3$. Their dot products with $b$ are $4$ and $4$. Thus $x=(2,4/3)^T$. The residual is $(1/3,-1/3,-2/3)^T$, with norm $\sqrt{2/3}$. Multiplying by $A^T$ gives zero, which is an independent check of optimality.

This example does not establish that the original geometric constraints are feasible. A nonzero residual may reflect genuine inconsistency, a poor linearization, or an incorrect model. Linear optimality is narrower than nonlinear feasibility.

## 31.3 Orthogonal transformations preserve the norm

An orthogonal matrix satisfies $Q^TQ=I$. Therefore $\|Qx\|_2=\|x\|_2$. A QR factorization writes $A=QR$ with $R$ upper triangular or upper trapezoidal. The least-squares problem becomes

$$
\min_x\|Rx-Q^Tb\|_2,
$$

so triangular substitution solves the full-rank part without explicitly squaring the matrix's conditioning.

A **Householder reflector** has the form

$$
H=I-2\frac{vv^T}{v^Tv}.
$$

For $a=(3,4)^T$, choose $v=a+5e_1=(8,4)^T$. Then

$$
H=\begin{bmatrix}-0.6&-0.8\\-0.8&0.6\end{bmatrix},
\qquad Ha=(-5,0)^T.
$$

A sequence of such reflections eliminates subdiagonal entries. In an implementation, store the reflector vectors and apply them; do not allocate a full dense $H$ for every column. The sign choice in constructing $v$ avoids subtracting nearly equal quantities.

Column pivoting can help reveal numerical rank, but a rank-revealing QR decomposition alone does not automatically provide the minimum-norm solution of every rank-deficient problem. Additional complete orthogonal factorization, a suitable underdetermined formulation, or SVD is needed for that guarantee. LAPACK distinguishes these cases explicitly.

## 31.4 Underdetermined does not mean unsolvable

Consider the single equation $x+y=2$. There are infinitely many solutions. The minimum-Euclidean-norm solution is $(1,1)$, because

$$
x^2+(2-x)^2=2(x-1)^2+2.
$$

A basic solution such as $(2,0)$ satisfies the equation but moves farther in that norm. In a sketch, this difference affects dragging: which free coordinates move and by how much?

The null space is the span of $(1,-1)$. Adding a null-space vector changes the parameters without changing the linearized residual. A solver can use this freedom to favor proximity to a previous configuration, a drag target, or a preferred gauge. These are additional objectives, not hidden consequences of the constraints.

If $x$ and $y$ have different units or characteristic scales, use a diagonal scaling matrix $D$ and measure $\|D\delta\|$. The selected minimum-norm step changes accordingly. A documented metric is part of predictable CAD behavior.

## 31.5 Singular values expose weakly determined directions

The singular value decomposition is

$$
A=U\Sigma V^T.
$$

The columns of $V$ define orthogonal input directions; $A$ maps the $i$th direction to the corresponding column of $U$, scaled by $\sigma_i$. A small singular value means a large parameter change produces only a small residual change. Such a direction is weakly constrained and highly sensitive to error.

For a full-rank matrix, the 2-norm condition number is $\sigma_{\max}/\sigma_{\min}$. For a rank-deficient matrix, an exact inverse does not exist. The pseudoinverse replaces each nonzero singular value by its reciprocal and leaves zero directions at zero, producing a minimum-norm least-squares solution.

Now examine

$$
J_\varepsilon=\begin{bmatrix}1&0\\1&\varepsilon\end{bmatrix},\qquad
b=\begin{bmatrix}0\\d\end{bmatrix}.
$$

For nonzero $\varepsilon$, the exact solution is $x=0,y=d/\varepsilon$. With $d=10^{-6}$ and $\varepsilon=10^{-4}$, $y=0.01$. With $\varepsilon=10^{-8}$, $y=100$. The small perturbation in the second equation has become a large motion along a weak direction.

The squared singular values are

$$
\lambda_\pm=\frac{2+\varepsilon^2\pm\sqrt{4+\varepsilon^4}}2.
$$

Computing $\lambda_-$ by subtracting nearly equal numbers is numerically poor for small $\varepsilon$. Since $\sigma_{\max}\sigma_{\min}=|\det J|=|\varepsilon|$, compute the smaller singular value as $|\varepsilon|/\sigma_{\max}$. This is a small example of changing a formula without changing the mathematics.

> **Try it.** Open [the singular-value lab](lab:sketch?id=svd). Decrease epsilon and compare the full, truncated, and damped solutions. Watch both residual and step norm. Set exact rank deficiency to distinguish a truly zero singular value from a small nonzero one.

%%FIG:31%%

## 31.6 Truncation and damping solve modified problems

A truncated pseudoinverse ignores singular directions below a threshold $\tau$. Its filter is $1/\sigma$ for retained values and zero for discarded values. The result may have a larger residual but a much smaller parameter step. This is a deliberate regularization, not the exact solution of the original full-rank system.

Tikhonov damping solves

$$
\min_x\|Ax-b\|_2^2+\lambda\|x\|_2^2.
$$

Its singular-direction filter is $\sigma/(\sigma^2+\lambda)$. In the lab, the damping parameter is $\lambda=\tau^2$. Very weak directions are suppressed continuously instead of being cut off abruptly.

For a scaled Levenberg–Marquardt step, solve the augmented least-squares system

$$
\min_\delta
\left\|
\begin{bmatrix}J\\\sqrt\lambda D\end{bmatrix}\delta-
\begin{bmatrix}-F\\0\end{bmatrix}
\right\|_2.
$$

This formulation allows QR or other least-squares methods without explicitly forming $J^TJ+\lambda D^TD$. It does not remove the need to choose damping and scaling, and it does not make a nonlinear inconsistent system feasible.

## 31.7 Numerical rank is a diagnosis with assumptions

Exact rank is a mathematical property of the represented matrix. Numerical rank is a decision about which singular values are significant relative to uncertainty and scale. A criterion such as $\sigma_i>\tau_{\mathrm{abs}}+\tau_{\mathrm{rel}}\sigma_{\max}$ makes the policy explicit, but the constants must be justified by the application and arithmetic.

In geometric constraints, $n-\operatorname{rank}J$ is the dimension of the linearized null space. At a regular solution, suitable hypotheses let this describe local degrees of freedom. At a singular point it can overestimate the dimension of actual finite motion. For example, $F(x)=x^2$ has Jacobian zero at $x=0$, yet its real zero set near zero contains only that point.

Likewise, dependent Jacobian rows do not necessarily identify a globally redundant nonlinear constraint. They identify local first-order dependence. Conflict extraction must distinguish numerical nonconvergence, local singularity, and a proven contradiction. This sharpens the diagnostic discussion in [[Engineering CAD 07 - Redundancy, conflict and singularity|chapter 7]].

For JigCAD, the source-inspection snapshot showed dense linear algebra and rank-aware analysis. The correct development question is not merely which named method is present. It is which factorization, scaling, stopping rules, and test corpus establish the behavior claimed by the user-facing status.

## 31.8 Exercises and checkpoint

> **Exercise 31.A.** Verify the least-squares solution and residual in §31.2. Compute $A^Tr$ explicitly. Then change the last entry of $b$ from two to one and find the now exactly consistent solution.

> **Exercise 31.B.** Derive the two singular values of $J_\varepsilon$ from $J_\varepsilon^TJ_\varepsilon$. Explain why the determinant relation is the more stable way to compute the smaller one.

> **Exercise 31.C.** For $\varepsilon=0$, solve the minimum-norm least-squares problem with $b=(0,d)$. Compare its residual with the limit of the full-rank solutions as $\varepsilon\to0$.

The checkpoint is a least-squares test harness with full-rank, rank-deficient, and nearly rank-deficient cases, verified against analytic answers and an independent trusted implementation. Report residuals and solution norms, not only a success boolean.

> **Careful.** A small singular value is not by itself proof that a nonlinear constraint system is inconsistent.

## Toward a reusable API

```text
factor(A, policy) -> QR | CompleteOrthogonal | SVD
least_squares(A, b, metric) -> solution + residual + rank_evidence
null_space(A, threshold_policy) -> basis + singular_values
regularized_step(J, residual, scaling, damping) -> step + diagnostics
classify_linearization(result) -> regular | weak | rank_deficient
```

## Key points

A nonlinear solver depends on the quality of its linear subproblems. Orthogonal transformations preserve Euclidean norms and avoid explicitly forming normal equations. Minimum-norm solutions require the appropriate factorization and metric. Small singular values expose sensitive directions rather than automatically proving infeasibility. Truncation and damping deliberately modify the problem. Jacobian nullity describes actual local freedom only under the necessary regularity assumptions.

## Further reading

[[Engineering CAD B - Source Library#^ref-hoffmann-upload|Hoffmann, §6.2.4, printed pp. 216–220]], introduces SVD in its geometric setting. The [[Engineering CAD B - Source Library#^ref-lapack-lls|LAPACK least-squares overview]] distinguishes full-rank, complete-orthogonal, and SVD-based solvers; the [[Engineering CAD B - Source Library#^ref-lapack-orthogonal|orthogonal-factorization overview]] explains norm preservation. Trefethen and Bau's *Numerical Linear Algebra* is recommended in the supplied research note for a sustained treatment; Nocedal and Wright's [[Engineering CAD B - Source Library#^ref-Nocedal|*Numerical Optimization*]] develops the outer nonlinear methods. These are further-study references, not claims that their full texts were supplied here.

---

[[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification|← Chapter 30. Tetrahedral quality and topology-safe simplification]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 32 - A source-guided implementation course|Chapter 32. A source-guided implementation course →]]
