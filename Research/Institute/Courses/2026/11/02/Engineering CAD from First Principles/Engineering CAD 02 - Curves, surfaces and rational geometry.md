---
title: "Engineering CAD from First Principles — Chapter 2. Curves, surfaces and rational geometry"
aliases:
  - "Chapter 2. Curves, surfaces and rational geometry"
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

# Chapter 2. Curves, surfaces and rational geometry

[[Engineering CAD 01 - A CAD system is a chain of contracts|← Chapter 1. A CAD system is a chain of contracts]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 03 - Topology and boundary representation|Chapter 3. Topology and boundary representation →]]

When a sketch displays one curve but the extrusion uses another, a valid solid can be geometrically wrong. This chapter derives the representations behind analytic geometry and NURBS, then identifies the exact point where interpolation, approximation and parameterization must be kept separate.

## 2.1 Geometry as a parameterized map

A **parametric curve** is a map $C:I\to\mathbb R^d$, often for $I=[0,1]$. A circle of radius $r$ centered at $(c_x,c_y)$ is

$$
C(t)=(c_x+r\cos 2\pi t,\;c_y+r\sin 2\pi t).
$$

A **surface** maps a two-dimensional parameter domain into $\mathbb R^3$. A cylinder is

$$
S(u,v)=(r\cos u,\;r\sin u,\;v).
$$

The geometry is continuous even though a display mesh samples it. A circle rendered with $n$ straight chords is a polygonal approximation; it is not the same mathematical object as the circle.

A parameterization also matters. Two formulas may trace exactly the same point set with different speeds and derivatives. Geometry comparisons should therefore distinguish equality of the *image* from equality of the parameterized map.

## 2.2 Bézier curves from Bernstein polynomials

A degree-$n$ Bézier curve uses control points $P_0,\ldots,P_n$ and the Bernstein basis:

$$
B(t)=\sum_{i=0}^{n}\binom ni(1-t)^{n-i}t^iP_i.
$$

For a quadratic, $B(t)=(1-t)^2P_0+2t(1-t)P_1+t^2P_2$. The coefficients are nonnegative on $[0,1]$ and sum to one, so the curve lies in the convex hull of the control points. It interpolates its *endpoints*, not generally the middle control point.

The endpoint derivatives are $B'(0)=n(P_1-P_0)$ and $B'(1)=n(P_n-P_{n-1})$. Thus two joined Bézier pieces are $C^0$ if their endpoints meet; they are $C^1$ if their endpoint derivatives match as vectors. Geometric continuity $G^1$ is weaker: tangent directions agree, even if speeds do not.

These distinctions matter for lofts and fillets. A visible kink at a curve junction can become an actual crease in a surface; a seam with only $G^1$ continuity may look smooth but carry a derivative discontinuity in its parameterization.

## 2.3 Why rational curves are necessary

A polynomial quadratic Bézier generally does not trace an exact circular arc. A **rational Bézier curve** adds positive weights $w_i$:

$$
R(t)=\frac{\sum_i w_i B_i^n(t)P_i}{\sum_i w_iB_i^n(t)}.
$$

Choose the control points $P_0=(1,0)$, $P_1=(1,1)$ and $P_2=(0,1)$ with weights $(1,1/\sqrt2,1)$. Then the rational quadratic traces an exact quarter-circle. At $t=1/2$, its coordinates are $(1/\sqrt2,1/\sqrt2)$; substituting gives $x^2+y^2=1$. Changing the middle weight while keeping the points fixed produces a different conic arc.

This is the essential idea behind **NURBS** (non-uniform rational B-splines): local polynomial basis functions, a knot sequence that determines their support, and rational weights that allow exact conics. B-spline curves offer local control because modifying a control point affects only knot spans on which its basis function is nonzero.


%%FIG:2%%

**Try it.** In [the rational Bézier bench](lab:sketch?id=bezier), change the middle weight from $1/\sqrt2$ to $1$. The reference quarter-circle remains fixed while the represented curve moves. Inspect the measured radial error.

## 2.4 Interpolation, approximation and control points are different

Suppose a sketch has four points $Q_0,\ldots,Q_3$. An **interpolating spline** solves for a curve satisfying $C(t_i)=Q_i$. A **control-point B-spline** uses the same coordinates as poles, but its curve usually does not pass through the interior poles. A **polyline approximation** samples either continuous curve at finitely many points and joins the samples with lines.

These constructions must not share an ambiguous input such as `points` without an explicit `meaning: control | interpolate | sampled` field.

The JigCAD issue report provides a concrete failure: a closed sketch spline is rendered according to one semantic convention, then passed into `GeomAPI_Interpolate` during solid construction. The reported sketch and solid areas can differ by tens of percent. The proposed fix is not “sample more densely”; it is to use the **same canonical curve object** in every stage.

A suggested interface separates authoring and representation:

```text
Curve::Line(p0, p1)
Curve::Arc(center, radius, start, sweep)
Curve::Nurbs { degree, knots, poles, weights, periodic }
Curve::Interpolant { samples, parameterization, tolerance }
```

An interpolant should be converted *once* to an explicit curve representation, after which the viewer, profile builder and B-rep operator all read that same representation. If conversion incurs error, record the error bound.

## 2.5 Curve evaluation is not curve topology

Even an exact curve representation does not say which part of it is a boundary. An edge of a face contains a trimmed interval and an orientation. A full circle can become a hole boundary; the same circle can become a separate filled disk depending on its placement and nesting. A periodic spline has a parameter seam, but the underlying geometric curve may be smooth across it.

A self-intersecting curve is especially dangerous. Its geometric image need not bound a unique region under a simple inside/outside rule. The arrangement of its branches must be constructed and a filling rule chosen. We develop this in Chapters 9 and 10.

## 2.6 Worked example: chord error

For a circle of radius $r$, an inscribed regular $n$-gon has maximum radial deviation at the midpoint of a chord:

$$
\varepsilon=r\left(1-\cos\frac\pi n\right).
$$

With $r=10$ mm and $n=32$, $\varepsilon\approx0.04815$ mm. Doubling to $n=64$ reduces the error to about $0.01205$ mm. For large $n$, $1-\cos(\pi/n)\sim\pi^2/(2n^2)$, so doubling the number of segments improves chordal accuracy by approximately a factor of four.

A display tessellation may use this approximation while the STEP exporter still writes an exact circular surface. An STL exporter instead serializes the approximating triangles. Those are intentionally different representations; their error report must say which one is being exported.

> **Exercise.** Derive the derivative of a cubic Bézier curve and show the conditions under which two pieces meet with equal first derivatives. Then prove the chord-error formula from a right triangle.

> **Careful.** An analytic curve can be exactly planar even if a particular modeling operation stores it as a degree-one B-spline. Geometric classification should not rely exclusively on runtime type names.

### Deeper study: connect curve evaluation to solid operations

A curve evaluator is not yet a trimmed-face representation. The same spatial point can have several parameter values, and a valid support surface can contain parts outside the intended face. [[Engineering CAD 29 - Tracing intersections of curved surfaces|Chapter 29]] derives intersection tracing from a sphere and plane before developing the three-equation, four-variable problem for two parametric surfaces. Project C in [[Engineering CAD 32 - A source-guided implementation course|chapter 32]] provides a restricted evaluator roadmap with endpoint, derivative, knot-insertion and rational-circle tests.

## Toward a reusable API

```text
Curve2.eval(t) -> Point2              curve in canonical parameterization
Curve2.derivative(t) -> Vec2         geometric tangent, not normalized
Curve2.bounds() -> IntervalBox       conservative support
Curve2.intersections(other) -> ...   points/overlaps with multiplicity
Curve2.approx(tolerance) -> Polyline with error certificate
Curve2.toBrepCurve() -> OCCT handle   no silent refitting
```

## Key points

Bézier and B-spline control points do not generally lie on the curve. Rational weights allow exact circles and other conics. Interpolation, fitting and sampling are distinct operations. Geometry, parameterization and topology must not be conflated. A common canonical curve representation is a prerequisite for trustworthy sketch-to-solid compilation.

## Further reading

- [Piegl and Tiller, *The NURBS Book*](https://link.springer.com/book/10.1007/978-3-642-59223-2) provides the full basis-function and rational-spline theory.
- [OpenCascade modeling data overview](https://www.occt3d.com/dev/doc/overview/html/index.html) describes analytic and spline geometry in the kernel.
- [JigCAD `shapes.js`](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/shapes.js) shows profile segments translated into OpenCascade curves.
- [JigCAD's documented spline inconsistency](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BOOK-ISSUES.md) motivates the canonical-representation contract.

---

[[Engineering CAD 01 - A CAD system is a chain of contracts|← Chapter 1. A CAD system is a chain of contracts]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 03 - Topology and boundary representation|Chapter 3. Topology and boundary representation →]]
