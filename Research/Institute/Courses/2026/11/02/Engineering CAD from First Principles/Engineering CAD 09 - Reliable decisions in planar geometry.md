---
title: "Engineering CAD from First Principles — Chapter 9. Reliable decisions in planar geometry"
aliases:
  - "Chapter 9. Reliable decisions in planar geometry"
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

# Chapter 9. Reliable decisions in planar geometry

[[Engineering CAD 08 - Continuation, sparse structure and performance|← Chapter 8. Continuation, sparse structure and performance]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 10 - From planar curves to valid profiles|Chapter 10. From planar curves to valid profiles →]]

Geometry algorithms repeatedly ask yes-or-no questions: is a point to the left of a line, do two segments cross, is a curve inside another, or is a circle tangent? If those decisions disagree because of floating-point rounding, a profile builder can construct the wrong topology even when every formula is locally reasonable. We derive the robust-predicate approach used by reliable computational-geometry systems.

## 9.1 Predicates versus constructions

A **predicate** returns a discrete classification based on continuous input. The orientation of three planar points $A,B,C$ is the sign of

$$
\operatorname{orient}(A,B,C)=(B_x-A_x)(C_y-A_y)-(B_y-A_y)(C_x-A_x).
$$

Positive means $C$ lies to the left of the oriented line $A\to B$; negative means right; zero means collinear. This is a determinant. A *construction*, by contrast, returns a point or curve such as the intersection of two lines.

The difference is crucial: a construction may tolerate a small coordinate error, but a wrong sign can change the combinatorial structure of an arrangement. A line intersection placed a few nanometers away usually looks the same. Classifying the two edges as non-intersecting instead of intersecting can destroy an entire face.


%%FIG:9%%

## 9.2 Floating-point arithmetic near zero

IEEE binary floating point stores a finite number of significant bits. The determinant involves subtraction of products, so almost-collinear configurations can exhibit catastrophic cancellation. When two large products nearly agree, their difference may contain far fewer reliable bits.

A naive rule such as `abs(det) < 1e-7` declaring collinearity is not scale invariant. The determinant has units of length squared; scaling the geometry by $1000$ multiplies it by $10^6$. A fixed absolute threshold may classify identical shapes differently after a unit conversion.

A tolerance policy for *measurement* is distinct from a method for *correctly evaluating a predicate*. The first expresses intentional design uncertainty; the second addresses numerical implementation error.

## 9.3 Adaptive exact predicates

Shewchuk's classical robust-predicates work uses a fast approximate determinant and an error bound. If the approximate value is safely separated from zero, return its sign. Otherwise evaluate with expansions or higher precision until the sign is reliable.

The broad pattern is

```text
approx = determinant_in_double(inputs)
err = proven_roundoff_bound(inputs)
if abs(approx) > err: return sign(approx)
return exact_or_adaptive_sign(inputs)
```

This does **not** imply that every geometric coordinate must be stored as an arbitrary-precision rational. It means the *combinatorial decisions* that control topology should be correct for the represented input numbers whenever practical.

**Try it.** The [orientation bench](lab:sketch?id=orientation) compares a floating-point orientation test with an integer-arithmetic oracle on an intentionally nearly collinear configuration. Change the perturbation and coordinate magnitude to see when classifications become delicate.

## 9.4 Segment intersections and degeneracy

For two nonparallel line segments $AB$ and $CD$, a common test examines orientation signs on each pair. In the generic crossing case, $A$ and $B$ lie on opposite sides of line $CD$, and $C,D$ lie on opposite sides of line $AB$.

But CAD profiles routinely include nongeneric cases: shared endpoints, collinear overlaps, tangent circles and arcs touching exactly at one point. Correct handling requires an explicit **intersection classification**:

```text
Disjoint
ProperCross(point, multiplicity)
TouchEndpoint(point)
Tangent(point, multiplicity)
Overlap(interval/curve)
Coincident
DegenerateInput
```

If the API returns only a list of points, it can discard crucial information. Two coincident segments have infinitely many intersection points; representing them as no points is dangerously ambiguous. A tangent has intersection multiplicity two, so the local ordering of branches differs from a transverse crossing.

## 9.5 Arrangements, DCELs and faces

An **arrangement** is the subdivision of the plane induced by a collection of curves. Its construction conceptually has three phases: find all intersections and split curves at them, assemble a directed incidence graph, then traverse directed cycles to identify faces.

A DCEL (doubly connected edge list) stores for each directed half-edge a twin, a next edge and the incident face. At a vertex, sort outgoing edge directions cyclically; following appropriate “next” links traces the boundary of each face. Interior holes arise from nested boundary components, which require separate containment or face-incidence logic.

The complexity of these algorithms depends on the number and type of curve intersections. Efficient algorithms such as sweep lines are important for large inputs, but an initially correct small arrangement implementation can use pairwise intersections and later optimize.

CGAL's arrangement library separates topology from **geometry traits** that implement precise curve comparisons and intersections. That separation is a good design model for a CAD profile builder supporting lines, arcs, ellipses and eventually general splines.

## 9.6 Tolerance-induced topology change

Suppose two circles are separated by a gap $\delta$. A CAD tolerance $\tau$ may intentionally treat $|\delta|\le\tau$ as coincident for a downstream manufacturing operation. This is a *policy* that changes the intended equivalence relation on geometry. Such snapping should be explicit, deterministic, and reported.

By contrast, the orientation predicate for the unsnapped input should not produce random positive and negative answers near zero because of cancellation. A robust pipeline keeps these concepts separate:

$$
\text{exact/filtered classification}\;\longrightarrow\;\text{declared snapping policy}\;\longrightarrow\;\text{topology construction}.
$$

A tolerance cannot be chosen correctly without considering smallest supported features, model scale and downstream kernel precision. If two geometric entities are closer than the modeler's resolution, reporting ambiguity may be safer than silently merging them.

## 9.7 Design consequence for JigCAD

Jig's `profiles.js` implements intersections, splitting, a directed-edge walk and loop nesting. This is more sophisticated than merely concatenating polygons. However, its reliance on floating-point comparison and sampling at some stages exposes boundary cases. Its documented tangent-hole and sliver problems are precisely the cases where a robust arrangement and clear contact semantics would help.

The best next step is not necessarily replacing all code with a large dependency. First specify the predicate contract, analytic cases, and topology representation, then test cases against a known reference such as CGAL. If adopting CGAL itself is incompatible with the target browser/runtime or licensing constraints, its algorithmic decomposition remains instructive.

> **Exercise.** Show that $\operatorname{orient}(A,B,C)$ changes sign if $B$ and $C$ are exchanged. Show that translating all three points by the same vector leaves its exact value unchanged. Which of those claims might fail in naive finite-precision evaluation for very large coordinates?

> **Careful.** Robust predicates do not automatically provide robust *constructed intersection coordinates*. The complete algorithm must control the accuracy and identity of vertices created from those predicates.

### Deeper study: a concrete exact oracle and the limits of perturbation

[[Engineering CAD 26 - Predicates, constructions and symbolic perturbation|Chapter 26]] gives a family of exactly representable integer coordinates for which separate floating-point products lose a one-unit determinant difference. It then separates exact predicates from exact constructions: a correct predicate cannot restore an intersection point already rounded by an earlier construction. Symbolic perturbation is a third mechanism, appropriate only when its tie-breaking semantics match the application. Intended CAD contact should not silently become a gap or overlap.

## Toward a reusable API

```text
Predicate.orientation(A,B,C) -> Negative | Zero | Positive
Intersection.segmentSegment(A,B,C,D) -> structured contact
Intersection.curveCurve(curveA,curveB) -> points/overlaps/multiplicities
Arrangement.fromCurves(curves, policy) -> validated DCEL
TolerancePolicy { absolute, relative, angular, snapMode }
```

## Key points

Discrete geometric decisions are more sensitive than continuous coordinate estimates. The orientation predicate is a determinant whose sign can be lost to cancellation. Filtered exact predicates compute reliable signs without making every calculation arbitrary precision. A planar arrangement separates curve intersections, combinatorial adjacency and face extraction. Numerical predicates and intentional snapping tolerances solve different problems.

## Further reading

- [Shewchuk, *Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates*](https://people.eecs.berkeley.edu/~jrs/papers/robustr.pdf) derives efficient reliable determinant tests.
- [CGAL 2D Arrangements manual](https://doc.cgal.org/latest/Arrangement_on_surface_2/index.html) explains traits, DCELs and curve arrangements.
- [JigCAD profile implementation](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/sketch/profiles.js) is the code to evaluate against these requirements.

---

[[Engineering CAD 08 - Continuation, sparse structure and performance|← Chapter 8. Continuation, sparse structure and performance]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 10 - From planar curves to valid profiles|Chapter 10. From planar curves to valid profiles →]]
