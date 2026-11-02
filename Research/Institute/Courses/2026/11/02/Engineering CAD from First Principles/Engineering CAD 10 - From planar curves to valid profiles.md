---
title: "Engineering CAD from First Principles — Chapter 10. From planar curves to valid profiles"
aliases:
  - "Chapter 10. From planar curves to valid profiles"
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

# Chapter 10. From planar curves to valid profiles

[[Engineering CAD 09 - Reliable decisions in planar geometry|← Chapter 9. Reliable decisions in planar geometry]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 11 - Boolean solids, blending and healing|Chapter 11. Boolean solids, blending and healing →]]

Mathematics in this chapter: [[Mathematics - Point-Set Topology|Point-Set Topology]], [[Mathematics - Computational Geometry|Computational Geometry]] (see [[Mathematics]]).

A profile is the filled planar region that a modeling operation will extrude, revolve or sweep. The profile builder must decide which closed loops are outer boundaries, which are holes, and what touching or self-intersecting curves mean. Small mistakes here can yield a topologically valid but completely wrong solid.

## 10.1 Define the filled set before implementing it

A sketch is a set of geometric entities; a *profile* represents a subset of the plane. A typical profile has one outer Jordan curve and zero or more inner boundary curves. A simple material region is

$$
R=\operatorname{inside}(C_{out})\setminus\bigcup_i\operatorname{inside}(C_i).
$$

This formula assumes well-defined, noncrossing boundary curves with a clear notion of inside. It does not define the intended result when a hole touches the outer boundary or two loops share an arc. Those cases require additional semantics, rejection, or a general planar arrangement with a selected filling rule.

A correct implementation must decide whether boundary points themselves are material, how tangencies are represented, and whether zero-width necks are supported. This is not a floating-point detail; it is part of the modeling-language specification.

## 10.2 Lines and circles: simple exact calculations

For a polygon with vertices $P_i=(x_i,y_i)$ in cyclic order, the shoelace formula gives signed area

$$
A=\frac12\sum_i(x_i y_{i+1}-x_{i+1}y_i).
$$

The sign reflects orientation. An exact full circle has area $\pi r^2$. For mixed line-and-arc loops, Green's theorem can integrate each segment analytically:

$$
A=\frac12\oint_{\partial R}(x\,dy-y\,dx).
$$

This is preferable to approximating a large circle with a coarse polygon merely to compute its area. Jig's shape constructors implement exact contributions for lines and circular arcs, while more general splines are approximated.

A hole of radius $4$ mm inside a $20\times20$ mm square gives area $400-16\pi\approx349.7345\;\mathrm{mm}^2$, and a 10 mm extrusion gives $3497.3452\;\mathrm{mm}^3$. That calculation becomes an oracle for the profile and solid stages.

## 10.3 Constructing regions from arbitrary curves

A robust profile pipeline follows these steps:

```text
1. Normalize source curves into canonical representations.
2. Detect all pairwise crossings, tangencies and overlaps.
3. Split curves into directed monotone or intersection-free pieces.
4. Merge truly identical vertices under an explicit policy.
5. Construct a half-edge graph with reliable cyclic orders.
6. Walk all bounded face cycles and determine containment.
7. Apply a documented filling rule and assign holes.
8. Reject nonmanifold or unsupported zero-width configurations.
9. Check area, boundary orientation and downstream B-rep consistency.
```

The main trap is step 4. Snapping vertices together because they are “close enough” can change the topology. Conversely, failing to merge mathematically identical endpoints can leave wires open. A correct implementation uses stable geometric classification plus a controlled tolerance model.

## 10.4 Tangency is a topological event

Consider a $20\times20$ square centered at the origin and a circular hole of radius $4$ centered at $(c,0)$. The square's right edge is $x=10$. The circle is strictly inside when $c+4<10$, tangent when $c+4=10$, and protrudes through the boundary when $c+4>10$.

When $c=6$, the circle touches the perimeter at one point. A simple “outer loop contains circle” test may now disagree with a polygonized point-in-region test. Neither answer should silently define an extra filled disk. The user's intent—drill a hole that reaches the edge—may require a slot-like open notch, or the construction should be rejected as ambiguous at exact tangency.


%%FIG:10%%

**Try it.** [The profile-tangency bench](lab:sketch?id=tangency) moves the circle through the square boundary. It labels the strict-inside, tangent and crossing regimes. The diagram depicts the intended geometric classification; it is not a direct JigCAD compile.

In the inspected project issue log, this family of inputs once yielded a body whose volume exceeded the original uncut square prism. A later update added a warning, but the incorrect solid itself remained documented as open. That is a strong regression test: subtracting material must not increase total volume, subject to the operation's agreed interpretation.

## 10.5 Closed splines and the single-source-of-geometry rule

Jig's source-reported closed-spline mismatch illustrates a second class of bug. The sketch renderer can evaluate an interpolating or control-point spline according to one convention while solid construction uses an OpenCascade interpolator with another. The resulting filled profile may be entirely different, even without tangency.

The correct architecture converts the user's authoring representation to a canonical curve once, preserving whether control points or interpolation samples were specified. Both display and B-rep construction then evaluate that curve. Where a kernel translation is approximate, record an error bound or reject operations whose tolerance cannot be met.

A test should sample points on the sketch curve and evaluate distance to the final B-rep boundary. Compare oriented area independently too: a curve-to-solid area discrepancy is easier to diagnose before extrusion.

## 10.6 Slivers and topology under perturbation

A circle whose radius exceeds a tangency threshold by $10^{-5}$ mm can create a microscopic sliver region. Whether that sliver is real material depends on the declared modeling precision. A production profile builder should have a clear *minimum feature policy* and must not silently discard valid thin geometry based only on a hard-coded area threshold.

An area threshold $A<\tau^2$ cannot by itself decide whether a feature is important: a long narrow slot may have tiny area but be intentional. Better diagnostics consider minimum separation, local feature size, curve identity, and the operation's requested tolerance.

## 10.7 Validation before B-rep creation

Before calling `BRepBuilderAPI_MakeFace`, verify closure, non-self-intersection under the chosen policy, consistent oriented loops, hole containment, and absence of unsupported contact cases. After conversion to an OCCT face, compare area and boundaries. Then extrude and compare the resulting solid volume with an analytically derived or independently computed expectation.

At the user-facing level, the best failure is a meaningful one: `profile.tangentHole: circle h touches outer boundary at (10,0); choose open-notch semantics, offset the hole, or reject this contour.` A failed downstream Boolean with no geometric context is much less useful.

> **Exercise.** Derive the exact area for the square-minus-circle profile while the hole lies strictly inside. Explain why this formula stops describing the desired *hole* when the circle crosses the square boundary, even though the numerical expression $400-16\pi$ remains well-defined.

> **Careful.** A display polygon is useful for rendering and hit testing but is not a reliable substitute for exact containment in a profile extractor near a curved boundary.

### Deeper study: work through the complete planar pipeline

[[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction|Chapter 27]] expands profile construction into event detection, edge splitting, directed incidence, boundary cycles, face grouping and membership labels. It includes two inline labs: a sweep-event inspector and a labeled rectangle overlay. These expose the intermediate combinatorial decisions rather than showing only the final polygon. [[Engineering CAD 28 - Delaunay triangulation and quality refinement|Chapter 28]] follows with triangulation and constrained refinement once a valid region has been identified.

## Toward a reusable API

```text
ProfileInput { canonicalCurves, fillRule, tolerancePolicy }
ArrangementResult { vertices, halfEdges, faces, contacts }
Profile { outerLoop, innerLoops, signedArea, provenance }
ProfileValidator.validate() -> structural and geometric diagnostics
```

## Key points

Profiles are filled sets, not just lists of curves. Hole containment has a precise meaning only under explicit boundary assumptions. Tangencies and contacts change topology and require policy decisions. Closed spline semantics must be identical between display and B-rep construction. Validate profiles before invoking a solid-making operation.

## Further reading

- [CGAL 2D Arrangements](https://doc.cgal.org/latest/Arrangement_on_surface_2/index.html) provides a mature architecture for curves-to-faces conversion.
- [JigCAD profile builder](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/sketch/profiles.js) contains the present arrangement and containment logic.
- [JigCAD shape constructors](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/shapes.js) translate profiles into OCCT geometry.
- [JigCAD issue log](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BOOK-ISSUES.md) provides numerical reproductions of tangent holes, slivers and spline mismatches.

---

[[Engineering CAD 09 - Reliable decisions in planar geometry|← Chapter 9. Reliable decisions in planar geometry]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 11 - Boolean solids, blending and healing|Chapter 11. Boolean solids, blending and healing →]]
