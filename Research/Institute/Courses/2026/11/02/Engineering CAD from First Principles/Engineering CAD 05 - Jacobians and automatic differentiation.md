---
title: "Engineering CAD from First Principles — Chapter 5. Jacobians and automatic differentiation"
aliases:
  - "Chapter 5. Jacobians and automatic differentiation"
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

# Chapter 5. Jacobians and automatic differentiation

[[Engineering CAD 04 - Constraints become equations|← Chapter 4. Constraints become equations]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 06 - Newton, Gauss–Newton, DogLeg and LM|Chapter 6. Newton, Gauss–Newton, DogLeg and LM →]]

Mathematics in this chapter: [[Mathematics - Numerical Linear Algebra|Numerical Linear Algebra]], [[Mathematics - Nonlinear Solving and Optimization|Nonlinear Solving and Optimization]] (see [[Mathematics]]).

Nonlinear solvers repeatedly need derivatives. Derivative accuracy affects convergence, numerical rank, conflict diagnosis and dragging. This chapter derives the Jacobian calculation used by Jig's Rust/WASM solver, compares it with finite differences, and explains the limits that remain even with exact program derivatives.

## 5.1 Linearization is the central computation

For a differentiable function $F:\mathbb R^n\to\mathbb R^m$, the Jacobian is the $m\times n$ matrix of partial derivatives. Its columns describe how the residual vector responds to each variable. The linearization

$$
F(x+\Delta x)\approx F(x)+J(x)\Delta x
$$

lets the solver choose a small displacement by solving a linear least-squares problem. A wrong Jacobian can send Newton's method toward a wrong step or make independent constraints appear dependent.

Take two residuals for a point constrained to a circle and a line:

$$F(x,y)=\begin{bmatrix}x^2+y^2-25\\x+y-3\end{bmatrix},\qquad
J(x,y)=\begin{bmatrix}2x&2y\\1&1\end{bmatrix}.$$

At $(x,y)=(4,-1)$, $F=(-8,0)^\top$ and $J=\bigl[\begin{smallmatrix}8&-2\\1&1\end{smallmatrix}\bigr]$. The Jacobian predicts that moving $x$ right while moving $y$ left increases squared radius while preserving the line equation. Chapter 6 traces the resulting Newton steps.

## 5.2 Finite differences and cancellation

A central finite difference approximates $\partial f/\partial x$ by

$$
\frac{f(x+h)-f(x-h)}{2h}.
$$

For smooth $f$, the truncation error is generally $O(h^2)$, but rounding error grows as $h$ becomes tiny because it subtracts nearly equal floating-point values. A rough total-error model is $O(h^2)+O(\epsilon/h)$, where $\epsilon$ is machine precision multiplied by a problem-dependent scale. There is no universally correct fixed $h$.

Jig's JavaScript fallback estimates derivatives numerically, with a step proportional to the magnitude of a coordinate. The project's own issue report shows that tiny sketch features positioned far from the origin can receive an excessively large finite-difference step, producing an incorrect rank or conflict diagnosis. This is one specific problem that the Rust automatic-differentiation path avoids.

%%FIG:5%%

## 5.3 Automatic differentiation is not symbolic simplification

**Automatic differentiation (AD)** applies the chain rule to elementary operations performed by a program. It computes derivatives of the function represented by an operation graph. It is different from replacing a formula with a symbolic closed form, and different from perturbing inputs numerically.

Suppose $z=x^2+y^2$. A computational graph may contain

$$
u=x\cdot x,\qquad v=y\cdot y,\qquad z=u+v.
$$

In reverse mode, begin with adjoint $\bar z=\partial z/\partial z=1$. The addition sends $\bar u=1$ and $\bar v=1$; each multiplication contributes $\bar x=2x$ and $\bar y=2y$. At $(3,4)$, the computed gradient is $(6,8)$ and $z=25$.

For a large number of inputs feeding one scalar residual, reverse mode can be efficient. To build a full $m\times n$ Jacobian, however, reverse-mode AD may require one reverse sweep per independent residual. Sparsity and reusing expression graphs become important.

**Try it.** [The derivatives bench](lab:sketch?id=derivatives) plots a scalar function and compares the analytic derivative with finite differences for adjustable step size. Increase the coordinate offset while keeping a very small local feature to observe cancellation and scaling effects.

## 5.4 What Jig's Rust tape implements

In [tape.rs](https://github.com/go-go-golems/jig/blob/main/import/jigcad/rust/jig-compute/src/tape.rs), Jig stores a sequence of operations per residual expression. Forward evaluation computes intermediate numerical values. Reverse evaluation traverses instructions backward, adding adjoint contributions for arithmetic, square root, trigonometric functions, `atan2`, and geometric operations.

An expression tape is a natural boundary between JavaScript and Rust: JavaScript constructs the geometric constraint semantics, while the compact tape and parameter arrays cross the WebAssembly ABI. Rust evaluates residuals and Jacobians without requiring arbitrary JavaScript callbacks inside a numerical iteration.

The tape also defines behavior at exceptional points. For example, the derivative of $\sqrt{x}$ is $1/(2\sqrt{x})$ when $x>0$ and becomes singular at zero. The derivative of $\mathrm{atan2}(y,x)$ depends on $x^2+y^2$ and is undefined at the origin. Jig's implementation guards some cases by returning finite or zero-like derivatives, but such choices are conventions, not mathematical regularity theorems.

## 5.5 Scaling the Jacobian before interpreting rank

The numerical rank of $J$ depends on the units and scaling of rows and columns. If a distance is measured in millimeters instead of meters, its derivative can change by a factor of $1000$. A rank tolerance applied to the raw matrix can classify the same geometry differently under a unit change.

Introduce row scaling $W=\operatorname{diag}(w_1,\ldots,w_m)$ and variable scaling $D=\operatorname{diag}(d_1,\ldots,d_n)$. Work with $z=D^{-1}(x-x_0)$ and normalized residuals $\widetilde F=WF$. The corresponding scaled Jacobian is

$$
\widetilde J=WJD.
$$

For nonzero diagonal scales, exact algebraic rank is unchanged, but numerical conditioning and the magnitude of singular values can improve dramatically. A distance row might be divided by a specified geometric tolerance, an angle row by an angular tolerance, and position variables by typical feature dimensions. The design must say whether scales represent numerical preconditioning or physical importance in a least-squares compromise.

## 5.6 Rank analysis and false certainty

For a regular solution, the singular values of $J$ measure sensitivity to motion. If $\sigma_{\min}$ is close to zero, a perturbation in residuals can require a large change in parameters. This is a conditioning problem even when AD computes each derivative accurately.

Householder QR with column pivoting is a reasonable way to estimate rank. Singular-value decomposition (SVD) is more diagnostic when a sketch is nearly singular, because it displays the singular values directly. A practical system may use QR ordinarily and fall back to SVD for disputed rank classifications.

> **Exercise.** Derive the Jacobian of $F(x,y)=(x^2+y^2-r^2,\;x-y)$. At $(0,0)$, what is its rank? Does this imply that the original system has infinitely many feasible solutions for $r>0$?

> **Careful.** AD is exact with respect to the implemented program's operations up to floating-point rounding. If the residual formula encodes the wrong geometry or has a nondifferentiable branch, AD faithfully differentiates the wrong or nonsmooth expression.

### Deeper study: derivatives do not cure an ill-conditioned solve

Automatic differentiation can evaluate the derivative of a smooth expression accurately while the resulting Jacobian remains nearly singular. [[Engineering CAD 31 - The linear algebra underneath a geometric solver|Chapter 31]] isolates that distinction with a two-equation system whose weak singular value tends to zero. Exact derivative formulas do not prevent a large step along a weakly constrained direction. [[Engineering CAD 29 - Tracing intersections of curved surfaces|Chapter 29]] gives a geometric example: surface normals become dependent as a sphere and plane approach tangency.

## Toward a reusable API

```text
ResidualTape.eval(x) -> residual vector
ResidualTape.jacobian(x) -> Jacobian with sparsity metadata
ResidualTape.jvp(x,v) -> Jv
ResidualTape.vjp(x,w) -> Jᵀw
ScaledSystem.residual(x) -> dimensionless residuals with tolerances
RankReport -> rank estimate, threshold, singularity evidence
```

## Key points

A nonlinear solver is only as reliable as its residuals and their derivatives. Finite differences balance truncation against cancellation and depend on scale. Reverse-mode AD computes Jacobians from expression graphs and is a genuine strength of Jig's Rust backend. Accurate derivatives do not eliminate singular configurations or poor scaling. Numerical rank should be reported with a tolerance and conditioning evidence.

## Further reading

- [Baydin et al., *Automatic Differentiation in Machine Learning: A Survey*](https://www.jmlr.org/papers/v18/17-468.html) explains forward and reverse modes.
- [Nocedal and Wright, *Numerical Optimization*](https://link.springer.com/book/10.1007/978-0-387-40065-5) discusses derivative quality and nonlinear optimization.
- [JigCAD Rust expression tape](https://github.com/go-go-golems/jig/blob/main/import/jigcad/rust/jig-compute/src/tape.rs) is the implementation studied here.
- [JigCAD numerical issue log](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BOOK-ISSUES.md) contains the far-from-origin finite-difference reproduction.

---

[[Engineering CAD 04 - Constraints become equations|← Chapter 4. Constraints become equations]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 06 - Newton, Gauss–Newton, DogLeg and LM|Chapter 6. Newton, Gauss–Newton, DogLeg and LM →]]
