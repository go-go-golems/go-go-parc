---
title: "Engineering CAD from First Principles — Chapter 29. Tracing intersections of curved surfaces"
aliases:
  - "Chapter 29. Tracing intersections of curved surfaces"
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

# Chapter 29. Tracing intersections of curved surfaces

[[Engineering CAD 28 - Delaunay triangulation and quality refinement|← Chapter 28. Delaunay triangulation and quality refinement]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification|Chapter 30. Tetrahedral quality and topology-safe simplification →]]

Mathematics in this chapter: [[Mathematics - Curves and Surfaces|Curves and Surfaces]], [[Mathematics - Nonlinear Solving and Optimization|Nonlinear Solving and Optimization]] (see [[Mathematics]]).

A Boolean operation on curved solids needs curves where their supporting surfaces intersect. Finding a few plausible points is not enough: the algorithm must follow branches, respect trim domains, and avoid losing small or disconnected components. This chapter derives a predictor–corrector tracer from a sphere and a plane, then explains how the same linear algebra appears in general parametric surface intersection.

**Source basis.** Hoffmann chapter 5 distinguishes implicit and parametric representations and their edge-identification problems. Chapter 6 develops numerical tracing, Newton correction, SVD, and higher-dimensional formulations. Its main numerical development assumes a starting point and a regular intersection; it explicitly does not solve the general initial-point problem. Our sphere–plane tracer is a smaller original implementation of those ideas. [[Engineering CAD B - Source Library#^ref-hoffmann-upload|Hoffmann]].

## 29.1 Implicit and parametric descriptions answer different questions

An implicit surface is a zero set $f(x,y,z)=0$. A sphere of radius five is $f=x^2+y^2+z^2-25=0$. Substituting a point into $f$ is easy, although converting a residual into a geometric distance still requires care.

A parametric surface is a map $S(u,v)\in\mathbb R^3$. A cylindrical patch, for example, is $S(u,v)=(r\cos u,r\sin u,v)$. Generating a surface point is easy. Determining whether a given point lies on the surface requires solving for parameters and handling nonunique values such as $u$ and $u+2\pi$.

Neither representation is uniformly superior. Intersecting an implicit and a parametric surface gives the equation $f(S(u,v))=0$ in the parameter plane. Intersecting two parametric surfaces naturally produces three equations in four variables. Implicitizing a surface first may eliminate variables but increase algebraic complexity. Hoffmann treats these tradeoffs explicitly rather than assuming every surface should use one canonical algebraic form.

A CAD face is a trimmed part of its supporting surface. Even a correct intersection of the infinite supporting surfaces may contain long portions outside one or both faces. Support intersection and trim classification are separate stages.

## 29.2 Derive a tangent from two equations

Suppose an intersection curve is $r(s)$ and satisfies $f(r(s))=g(r(s))=0$. Differentiate with respect to $s$:

$$
\nabla f(r(s))\cdot r'(s)=0,\qquad
\nabla g(r(s))\cdot r'(s)=0.
$$

The tangent is orthogonal to both surface normals. When the gradients are linearly independent, one unit tangent is

$$
t=\frac{\nabla f\times\nabla g}{\|\nabla f\times\nabla g\|}.
$$

Its negative follows the same curve in the opposite direction. Choose the sign consistently, for example by maintaining positive dot product with the previous tangent. A sudden sign reversal otherwise makes the tracer walk backward.

The independence condition is **transversality**. It makes the local intersection a regular curve. If the gradients become dependent, the intersection might be a tangency, a singular curve, an isolated point, or overlapping surfaces. The formula's denominator is a diagnostic of the parameterization and equations, not a reason to divide by a tiny arbitrary replacement value and continue blindly.

## 29.3 A sphere cut by a plane

Intersect $f=x^2+y^2+z^2-25=0$ with $g=z-h=0$. Substitution gives

$$
x^2+y^2=25-h^2,\qquad \rho=\sqrt{25-h^2}.
$$

For $|h|<5$, the intersection is a circle of radius $\rho$. For $|h|=5$, it is one point. For $|h|>5$, there is no real intersection. At $h=3$, $\rho=4$ and $p=(4,0,3)$ lies on the curve.

The sphere gradient is $(8,0,6)$ and the plane gradient is $(0,0,1)$. Their cross product points toward negative $y$; its negative points toward positive $y$. The lab chooses the positive-$y$ direction. With step length one, the tangent predictor is $q_0=(4,1,3)$.

This predicted point is on the plane but outside the sphere:

$$
f(q_0)=16+1+9-25=1.
$$

That residual has squared-length units. It is not a one-millimeter position error. The radial distance error in the plane is $\sqrt{17}-4\approx0.123106$.

## 29.4 Correct the prediction without unnecessary tangent motion

Linearizing the two equations at $q$ gives

$$
J(q)\,\delta=-F(q),\qquad
J=\begin{bmatrix}\nabla f^T\\\nabla g^T\end{bmatrix},\quad
F=\begin{bmatrix}f\\g\end{bmatrix}.
$$

There are two equations and three unknown corrections. Among compatible corrections, choose the minimum-norm one, which avoids arbitrary tangent displacement. An SVD or suitable rank-aware factorization provides this solution. Do not obtain it by inverting a nonexistent square $2\times3$ matrix.

For the sphere–plane family, the point already has $z=h$. Let $u=(x,y)$ and $r=\|u\|$. The minimum-norm linearized correction is radial:

$$
u_{k+1}=u_k-\frac{\|u_k\|^2-\rho^2}{2\|u_k\|^2}u_k.
$$

Beginning at $(4,1)$ with $\rho=4$, the first multiplier is $1-1/34=33/34$. Thus

$$
u_1=(3.88235294,\;0.97058824).
$$

After a second correction,

$$
u_2\approx(3.88057041,\;0.97014260),
$$

with squared-radius residual approximately $3.3760\times10^{-6}$ and radial position error approximately $4.2200\times10^{-7}$. The two quantities differ by roughly the factor $2\rho$, as the first-order residual–distance relationship predicts.

> **Try it.** Open [the surface-intersection tracing lab](lab:sketch?id=tracing). At plane height 3 and step 1, set zero, one, then two correction iterations. Compare the predicted point, corrected point, equation residual, and radial distance error. Increase the step and observe the extra correction work.

%%FIG:29%%

The analytic seed and radial correction make this example unusually simple. The lab does not search for all intersection components, classify trims, or implement a general surface tracer.

## 29.5 A small residual is not a complete tracing guarantee

A correction can land on the wrong branch, return to an already visited region, or converge to an isolated point. A sequence of well-corrected points can also skip a small loop elsewhere. Local accuracy and global completeness are different requirements.

Track step acceptance using several criteria: normalized residuals, correction size relative to the predictor step, tangent change, and progress along the selected branch. If the correction is large, reduce the step and retry. Curvature can guide an initial step estimate, but it does not replace an error check. A maximum number of retries should produce an explicit incomplete-trace result rather than a closed curve invented from the last few points.

At $h\to5$, the sphere–plane circle shrinks and the two normals become nearly parallel. Their cross-product magnitude on the circle is $2\rho$, tending to zero. The existence of an exact analytic answer in this example does not mean the generic numerical formulation remains well-conditioned at the endpoint. At $h=5$ the regular-curve assumption has failed.

## 29.6 Two parametric surfaces give a curve in four dimensions

Let the surfaces be $S(u,v)$ and $T(s,t)$. Define

$$
F(u,v,s,t)=S(u,v)-T(s,t)=0.
$$

Its Jacobian has three rows and four columns:

$$
J=\begin{bmatrix}S_u&S_v&-T_s&-T_t\end{bmatrix}.
$$

At rank three, the null space is one-dimensional and supplies a tangent direction in parameter space. Mapping it through either surface gives the corresponding spatial tangent. The parameter-space tangent has mixed scaling if the two surfaces use very different parameter ranges; scale variables before interpreting a step norm.

One predictor–corrector formulation adds a fourth equation fixing the corrector to a hyperplane normal to the predicted parameter-space tangent:

$$
\tau_k^T(q-q_{\mathrm{pred}})=0.
$$

The resulting four-equation Newton system removes the free tangential direction. Another formulation uses minimum-norm corrections directly. These choices have different continuation behavior and conditioning; both require a regularity check and a consistent parameter metric.

The output must retain a spatial curve and corresponding parameter curves on both surfaces. If $C(w)$ is the spatial curve and $c_S(w)=(u(w),v(w))$, check that $S(c_S(w))$ agrees with $C(w)$ within the intended tolerance. A curve that looks correct in 3D can still have a bad pcurve that breaks trim classification.

## 29.7 Find seeds, respect trims, and identify branches

A full intersection algorithm needs initial points for every relevant component. Bounding boxes, subdivision, interval exclusion, boundary intersections, and specialized analytic cases can help find seeds. A closed intersection loop wholly inside two parameter patches need not touch either patch boundary, so “start only from boundary crossings” can miss it.

Once a branch is traced, classify it against each face's trim domain. Split at trim intersections and at parameter seams. Preserve the identity of endpoints and the agreement between 2D and 3D representations. At singularities, report unresolved branching unless a dedicated classification method establishes the local structure.

Hoffmann's numerical development explicitly starts from a supplied regular point. Its later discussion includes algebraic and projection approaches and explains their tradeoffs. Read those as the book's historical treatment, not as a current claim that no later methods exist.

A useful contrast is the rational parameterization of the unit circle:

$$
x=\frac{1-t^2}{1+t^2},\qquad y=\frac{2t}{1+t^2}.
$$

Substitution proves $x^2+y^2=1$, but finite real $t$ omits $(-1,0)$. A globally complete representation needs another chart or a treatment of the point at infinity in the parameter. Algebraic equivalence on a chart does not imply globally complete parameter coverage.

## 29.8 Exercises and checkpoint

> **Exercise 29.A.** Derive the radial correction formula as a minimum-norm solution of one linearized circle equation. Verify the two numerical iterates above independently.

> **Exercise 29.B.** For the sphere–plane family, classify the intersections at $h=0,3,5,6$. Identify which cases admit a regular one-dimensional trace.

> **Exercise 29.C.** Design a trace record containing both surface parameter pairs, the spatial point, tangent, residual, accepted step length, and termination reason. Explain which fields detect a bad pcurve and which could help detect an unintended branch jump.

The checkpoint is a tracer for one analytically checkable family, with explicit singular and incomplete statuses. A general seeding algorithm is a separate project, not an implicit feature of the Newton loop.

> **Careful.** This trace starts from an analytic seed. It does not establish that all components of a general surface intersection have been found.

## Toward a reusable API

```text
intersection_seeds(face_a, face_b) -> Seeds + coverage_report
intersection_tangent(q) -> RegularTangent | RankDeficient
predict_correct(q, tangent, step, scales) -> Accepted | Retry | Singular
trace(seed, policy) -> Branch + termination_reason
trim_branch(branch, faces) -> OrientedSegments
validate_pcurves(branch) -> consistency_report
```

## Key points

Implicit and parametric representations make different operations easy. Independent surface gradients define a local intersection tangent. A predictor needs a corrector because tangent motion leaves the curved surfaces. Minimum-norm corrections avoid arbitrary tangent motion but do not guarantee branch identity. Parameter-space tracing must control scaling and retain pcurve correspondence. Accurate samples on one branch do not prove that every intersection component was found.

## Further reading

[[Engineering CAD B - Source Library#^ref-hoffmann-upload|Hoffmann, chapter 5, printed pp. 155–204]], treats representations, conversions, and edge identification. Chapter 6, printed pp. 205–255, develops tracing; the scope restriction on initial points is on printed p. 206, PDF p. 226. Read §§6.2.3–6.2.4 for Newton correction and SVD, and §6.3.2 for the three-equation/four-variable parametric formulation. [[Engineering CAD 31 - The linear algebra underneath a geometric solver|Chapter 31]] supplies a smaller linear-algebra derivation before returning to the book's systems.

---

[[Engineering CAD 28 - Delaunay triangulation and quality refinement|← Chapter 28. Delaunay triangulation and quality refinement]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification|Chapter 30. Tetrahedral quality and topology-safe simplification →]]
