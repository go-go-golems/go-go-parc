---
title: "Engineering CAD from First Principles — Chapter 18. Surface continuity and advanced modeling"
aliases:
  - "Chapter 18. Surface continuity and advanced modeling"
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

# Chapter 18. Surface continuity and advanced modeling

[[Engineering CAD 17 - Verification, differential tests and fuzzing|← Chapter 17. Verification, differential tests and fuzzing]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 19 - Tolerance, healing and metrology|Chapter 19. Tolerance, healing and metrology →]]

Mathematics in this chapter: [[Mathematics - Curves and Surfaces|Curves and Surfaces]] (see [[Mathematics]]).

A CAD part may be a valid closed solid yet have an unacceptable seam between two surfaces. This occurs in product housings, aerodynamic shells, complex lofts and variable-radius fillets: meeting at the same curve is not the same as meeting with the same tangent or curvature. This chapter derives continuity from derivatives and relates it to NURBS surfaces, trimmed patches, fillets and offsets.

## 18.1 A curve has both position and derivatives

Let $C:[0,1]\to\mathbb R^3$ be a regular parametric curve with $C'(t)\ne0$. Its **unit tangent** is $T(t)=C'(t)/\|C'(t)\|$. For a planar curve $C(t)=(x(t),y(t))$, the signed curvature is

$$
\kappa(t)=\frac{x'(t)y''(t)-y'(t)x''(t)}{(x'(t)^2+y'(t)^2)^{3/2}}.
$$

The numerator measures how rapidly the tangent turns; the denominator compensates for parameter speed. A circle of radius $R$ has $|\kappa|=1/R$ at every regular point. A straight line has curvature zero. These are measurable geometric claims, not merely statements about how a curve looks on screen.

Two curve segments $C$ and $D$ meet **position-continuously** ($C^0$) when $C(1)=D(0)$. They meet **tangent-continuously** ($G^1$) when their unit tangents agree, even if one segment is traversed faster. **Parametric first-derivative continuity** ($C^1$) requires $C'(1)=D'(0)$, which is stronger. Curvature continuity ($G^2$) additionally requires matching curvature vectors with compatible tangent directions. $C^2$ requires the second derivatives to agree in the chosen parameterization. Be careful with signed versus unsigned curvature: a reversed traversal changes the sign convention.

## 18.2 Work an explicit Bézier junction

A cubic Bézier curve with control points $P_0,P_1,P_2,P_3$ has endpoint derivatives

$$
C'(1)=3(P_3-P_2),\qquad C''(1)=6(P_3-2P_2+P_1).
$$

Suppose the first piece ends at $P_3=(1,0)$ and has $P_2=(0.7,0)$. Its endpoint derivative is $(0.9,0)$. A second cubic begins at $Q_0=(1,0)$ with $Q_1=(1.6,0)$ and derivative $D'(0)=(1.8,0)$. The pieces meet at the same point with the same tangent direction: $G^1$ holds. Yet $C'(1)\ne D'(0)$, so $C^1$ fails. Setting $Q_1=(1.3,0)$ would enforce $C^1$ without changing the common point.

Curvature needs second derivatives, so matching tangent alone says nothing about how abruptly the curve begins to bend. The useful design exercise is to prescribe the tangent and curvature at the join, then solve for the neighboring control points. A spline editor should expose whether its continuity setting means geometric or parametric continuity.

**Try it.** Use [the curve-junction bench](lab:sketch?id=curvature). Change the downstream handle length. The two pieces retain a horizontal common tangent while the derivative magnitudes differ; then choose a matched handle and observe the numerical derivative check.

%%FIG:18%%

## 18.3 From curves to parametric surfaces

A regular surface is a map $S:U\subset\mathbb R^2\to\mathbb R^3$. Its partial derivatives $S_u,S_v$ span a tangent plane when $S_u\times S_v\ne0$. The oriented normal is

$$
N(u,v)=\frac{S_u\times S_v}{\|S_u\times S_v\|}.
$$

Two surfaces meeting along a shared boundary curve can be position-continuous but have different tangent planes. Tangent-plane continuity requires compatible normals along the seam. Curvature continuity requires additional agreement of how these normals vary with position, and depends on the surface direction considered.

For a tensor-product B-spline surface,

$$
S(u,v)=\sum_{i,j}N_{i,p}(u)M_{j,q}(v)P_{ij},
$$

or its rational version with weights $w_{ij}$, the control net influences local shape through the basis functions. Knots, multiplicities and degree determine the available smoothness at internal parameter lines. Rational surface patches can represent many quadrics exactly. Complex industrial surfaces frequently consist of several patches with explicitly managed boundary continuity.

A **trimmed surface** is not a smaller parametric domain automatically understood by the underlying surface formula. A B-rep face stores a supporting surface and boundary curves defining the retained region; the same edge must agree with the face's parameter-space representation (a *pcurve*). This is a major source of tolerance and topology work in CAD kernels.

## 18.4 Why lofts and sweeps are delicate

A loft constructs surfaces through a family of section curves. The sections may have different parameterizations, different seam locations or different numbers of meaningful features. Even when every cross-section is individually valid, an inconsistent correspondence can twist the surface. Closed sections have a seam choice; moving that seam changes which points are paired across profiles.

A sweep carries a section along a space curve. One must choose a moving frame: a Frenet frame derived from curvature can become undefined where curvature is zero, while parallel-transport or rotation-minimizing frames avoid unnecessary twist. Neither frame choice changes the intrinsic shape of the path, but it changes the orientation of noncircular cross-sections and hence the resulting surface.

As an implementation rule, distinguish section geometry, feature correspondence, frame construction and topology stitching. Report each separately when a loft or sweep fails. A single “operation failed” message does not tell the designer which contract was violated.

## 18.5 Offsets, shells and singularities

An offset surface is constructed formally as $S_d=S+dN$. Let $\kappa_i$ be a principal curvature under a chosen normal/sign convention. The corresponding offset principal curvature has the form

$$
\kappa_i(d)=\frac{\kappa_i}{1-d\kappa_i},
$$

with the sign of $d$ adjusted for the offset-normal convention. When $1-d\kappa_i=0$, the local offset becomes singular: normals from nearby source points meet and the offset can develop a fold or cusp. This is a geometric limitation, not a bad choice of iteration count.

For a circle of radius $10\,\mathrm{mm}$, an inward offset by $9.9\,\mathrm{mm}$ leaves a circle of radius $0.1\,\mathrm{mm}$; an inward offset by $10\,\mathrm{mm}$ collapses it to a point. This is why shell thickness can be constrained by the smallest local radius of curvature, not merely by whether the input solid is closed.

A fillet can be understood as introducing a new surface tangent to two neighboring surfaces. In general, the rolling-ball construction must find compatible contact loci and handle corner transitions where three or more blends meet. Variable-radius fillets make this more difficult because the contact condition changes along the edge.

## 18.6 JigCAD and OpenCascade boundaries

JigCAD delegates much of its loft, sweep, shell and fillet geometry to OpenCascade, including `BRepOffsetAPI_ThruSections`, `BRepOffsetAPI_MakePipeShell`, `BRepOffsetAPI_MakeThickSolid` and `BRepFilletAPI_MakeFillet`. Those algorithms are substantial, but the wrapper still chooses input profiles, frames, tolerances, reference faces and failure explanations. The repository also documents that a tapered polygon extrusion can yield mathematically planar faces represented as degree-one spline surfaces, affecting simplistic surface-type selectors.

An advanced modeling API needs orientation and knot information, section correspondence, surface continuity queries, reliable detection of self-intersection, and clear error reporting when an offset or blend is geometrically impossible. It should not silently refit a sketch curve to a visibly different curve before extrusion.

## 18.7 Validation experiments

Construct two connected bicubic patches with a known common boundary. First make their boundary positions equal but their tangent planes different; verify a $G^0$ seam. Then align the tangents while changing derivative magnitudes; verify $G^1$ but not necessarily $C^1$. Finally adjust the second-derivative data and measure curvature mismatch along the seam at many sample points.

For offsets, evaluate radii approaching the critical offset distance from below and above. The test should classify singularity, self-intersection and topology change explicitly. Volume or display appearance alone is insufficient: a near-singular shell may triangulate convincingly but remain unsuitable for manufacturing.

> **Exercise.** Derive $C'(0)$, $C'(1)$, $C''(0)$ and $C''(1)$ for a cubic Bézier curve. Construct two cubic pieces meeting at $(1,0)$ that are $G^1$ but not $C^1$. What additional equations enforce $C^2$ at their junction?

> **Careful.** “Smooth” is not a single mathematical property. State $G^1$, $C^1$, $G^2$ or $C^2$, and state the parameter direction and tolerances used for the test.

### Deeper study: continue from surface derivatives to intersections

[[Engineering CAD 29 - Tracing intersections of curved surfaces|Chapter 29]] differentiates the intersection equations to derive a tangent, then applies minimum-norm Newton corrections to a sphere–plane example. It also explains why parameter-space tracing must retain pcurves on both surfaces. Smooth support surfaces do not guarantee a regular intersection, and locally accurate trace points do not prove that all branches or trim components were found.

## Toward a reusable API

```text
Curve { evaluate(t), derivative(t,k), bounds(), knots(), degree() }
Surface { evaluate(u,v), partials(u,v), normal(u,v), curvature(u,v) }
ContinuityReport { location, G0, G1, G2, C1, C2, tolerances }
SurfaceBlend { sides, radiusLaw, continuity, cornerPolicy }
OffsetResult { patches, singularities, selfIntersections, diagnostics }
```

## Key points

A shared boundary does not imply shared tangents or curvature. Geometric and parametric continuity are different promises. NURBS patches can represent smooth shapes but require careful seam and trim construction. Lofting needs meaningful section correspondence. Offsets have genuine geometric singularities governed by curvature. OpenCascade supplies sophisticated building blocks, while JigCAD must preserve their input meaning and expose their limitations.

## Further reading

- [Piegl and Tiller, *The NURBS Book*](https://link.springer.com/book/10.1007/978-3-642-59223-2) derives B-spline basis functions, continuity and rational surface patches.
- [OpenCascade modeling data guide](https://documentation.help/Open-Cascade/occt_user_guides__modeling_data.html) documents geometric versus parametric continuity.
- [OpenCascade shape construction in JigCAD](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/shapes.js) shows the actual loft and sweep calls.
- [JigCAD blend/shell wrappers](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/ops.js) show which operation options reach OpenCascade.

---

[[Engineering CAD 17 - Verification, differential tests and fuzzing|← Chapter 17. Verification, differential tests and fuzzing]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 19 - Tolerance, healing and metrology|Chapter 19. Tolerance, healing and metrology →]]
