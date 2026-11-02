---
title: "Engineering CAD from First Principles — Chapter 23. Solids as regular sets and representation contracts"
aliases:
  - "Chapter 23. Solids as regular sets and representation contracts"
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

# Chapter 23. Solids as regular sets and representation contracts

[[Engineering CAD 22 - Engineering a trustworthy next version|← Chapter 22. Engineering a trustworthy next version]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 24 - Half-edge structures and Euler construction|Chapter 24. Half-edge structures and Euler construction →]]

Two blocks can touch along a face without sharing any material volume. A polygon can look closed while its data structure contains a gap. A completely valid model can describe the wrong part. These are three different failures, and they require three different definitions of correctness. This chapter starts with point sets, derives regularized solid operations, and then connects the mathematical object to its representation and implementation.

**Source basis.** Mäntylä develops point-set regularity in §3.4 and representation schemes in §3.6; Hoffmann develops regularized Boolean operations in §2.2.2 and separates user interface, algorithmic infrastructure, and arithmetic in §1.2. The examples and contract design below are original teaching constructions based on those distinctions. Neither historical book is evidence about the current state of JigCAD. [[Engineering CAD B - Source Library#^ref-mantyla-upload|Mäntylä]] · [[Engineering CAD B - Source Library#^ref-hoffmann-upload|Hoffmann]].

## 23.1 Start with membership, not a picture

A subset $A\subseteq\mathbb R^3$ answers a precise question: does a point $p$ belong to $A$? A closed box of side lengths $4,3,2$ at the origin is

$$
A=\{(x,y,z):0\le x\le4,\;0\le y\le3,\;0\le z\le2\}.
$$

Its membership condition is finite even though it contains infinitely many points. A representation does not enumerate the points; it provides finite data from which suitable questions can be answered. For this box, six inequalities suffice. A boundary representation instead records six bounded faces, their incidence, and their orientation.

The **interior** $\operatorname{int}A$ consists of points with a sufficiently small open ball wholly inside $A$. The box interior uses strict inequalities. The **closure** $\overline A$ adds all limit points. The **boundary** is $\partial A=\overline A\setminus\operatorname{int}A$. A point on $x=0$ belongs to the closed box but not its interior.

These operations refer to an ambient space. A filled square has a nonempty interior in $\mathbb R^2$ but an empty interior when regarded as a zero-thickness subset of $\mathbb R^3$. Every regularization discussion must name that space. A CAD face is a useful two-dimensional object; it is not by itself a three-dimensional solid.

For algorithms it is often useful to expose three answers, `Inside`, `Outside`, and `OnBoundary`, rather than a boolean. This is a classification of a point relative to a represented region. An additional `Indeterminate` status may be needed when the numerical computation cannot certify a classification within its permitted budget. That status concerns knowledge, not a fourth geometric region.

## 23.2 Regularization removes unsupported lower-dimensional pieces

Mäntylä calls a set regular when it equals the closure of its interior. Define

$$
\operatorname{reg}(A)=\overline{\operatorname{int}A},\qquad
A\text{ regular closed}\iff A=\operatorname{reg}(A).
$$

The adjective “closed” makes the convention explicit; some mathematical literature uses other regular-set terminology. A closed ball is regular closed. A ball with an isolated point outside it is not: the isolated point has no three-dimensional interior around it, so regularization deletes it. A ball with an interior point removed has the same regularization as the original ball: the missing point is restored by closure.

Consider two closed cubes:

$$
A=[0,1]^3,\qquad B=[1,2]\times[0,1]^2.
$$

Their ordinary intersection is the square $\{1\}\times[0,1]^2$. In three-dimensional space that square has empty interior. Therefore

$$
\operatorname{reg}(A\cap B)=\varnothing.
$$

This is not an approximation or an epsilon rule. It is the exact consequence of choosing a solid-only result domain. A collision or contact query might still need the shared square. Such a query should return a contact entity rather than asking a regularized solid intersection to preserve it.

Regularization is idempotent: regularizing an already regularized set changes nothing. To see the main inclusion, write $U=\operatorname{int}A$. Because $U$ is open, $U\subseteq\operatorname{int}\overline U$. Taking closures gives $\overline U\subseteq\overline{\operatorname{int}\overline U}$. The reverse inclusion follows because $\overline U$ is closed and contains its interior. Thus $\operatorname{reg}(\operatorname{reg}(A))=\operatorname{reg}(A)$.

## 23.3 Derive the solid Boolean operations

For regular closed operands, define

$$
A\cup^*B=\operatorname{reg}(A\cup B),\qquad
A\cap^*B=\operatorname{reg}(A\cap B),\qquad
A\setminus^*B=\operatorname{reg}(A\setminus B).
$$

For the difference, closure restores the exposed cut boundary. For the intersection, interior removes contacts that have no material around them. The formulas specify the answer; they are not an instruction to construct an arbitrary point set and then literally enumerate its interior. Hoffmann emphasizes that actual Boolean algorithms classify boundary elements and reconstruct the appropriate result (§2.2.2, printed p. 22).

A two-dimensional example makes the contact transitions measurable. Let

$$
A=[0,4]\times[0,3],\qquad
B=[x,x+4]\times[y,y+3].
$$

For $x,y\ge0$, the overlap area is

$$
I(x,y)=\max(0,4-x)\max(0,3-y).
$$

At $(x,y)=(2,1)$, $I=2\cdot2=4$, the union area is $12+12-4=20$, and the difference area is $12-4=8$. At $(4,0)$, the ordinary intersection is an edge of length $3$, but the regularized intersection in $\mathbb R^2$ is empty. At $(4,3)$, the ordinary intersection is a single point. At $(4.1,0)$ it is already empty before regularization.

> **Try it.** Use [the regularized-set lab](lab:sketch?id=regularized). Set `x=4`, `y=0`, and switch regularization off and on. Then set `y=3`. Watch the intersection dimension, not just its area: an edge and a point both have zero area, but they are different contact sets.

%%FIG:23%%

The lab evaluates axis-aligned rectangles by elementary interval arithmetic. It does not implement arbitrary polygon or B-rep Boolean operations. Its purpose is to make the result contract observable before introducing the harder algorithms of [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction|chapter 27]].

## 23.4 Regularity does not imply manifoldness

A **two-manifold boundary** has a neighborhood around each point that is topologically a disk. Two solid cubes that touch at exactly one vertex form a regular closed union, yet the boundary near the shared vertex consists of two surface neighborhoods meeting only at that point. That boundary is not a two-manifold.

This distinction is central to kernel design. “All regular closed sets representable by these primitives” and “only solids with manifold boundaries” are different supported domains. A regularized union need not stay inside the second domain. An implementation must either support the resulting nonmanifold structure, split it into a documented collection of components, or reject it with an explicit explanation.

Mäntylä's workbench develops a manifold-oriented construction discipline. Hoffmann explicitly distinguishes manifold and nonmanifold B-reps in §2.3 and develops topological validity in §2.4. Treat these as alternative modeling commitments, not as interchangeable definitions. [[Engineering CAD 25 - Simplicial complexes, links and homology|Chapter 25]] gives executable local tests for the difference.

A further issue is geometric embedding. An abstract sphere-like connectivity graph can be embedded with triangles crossing through one another. Its Euler characteristic still equals two. Topological consistency of the abstract complex has not proved that the coordinates realize the intended embedded surface.

## 23.5 Four contracts for one operation

Suppose an operation receives two model records and promises their difference. Its obligations can be separated as follows.

| Contract | Question | Example failure |
|---|---|---|
| Representation | Are the records internally coherent? | A half-edge's twin does not point back. |
| Geometric realization | Do coordinates and supporting curves agree with the records? | An edge endpoint is not on its curve. |
| Set semantics | Does the result equal the requested regularized operation? | A cut adds material or leaves an unwanted component. |
| Design intent | Does that operation express the intended design? | The tool was positioned on the wrong face. |

A shape validator can establish some representation properties without establishing set equivalence. Volume comparison can refute a wrong result but cannot prove equality: different shapes can have equal volume. A correct difference operation cannot infer whether the user intended that particular tool placement.

A useful output is therefore a result accompanied by evidence: generated and modified entity mappings, validation findings, tolerance changes, and the policy used for contacts. “Success” must not mean merely that a C++ call returned a non-null shape.

For the $4\times3$ rectangle with a fully internal circular hole of radius $0.5$, a correct area is $12-\pi/4$. Three independent observations are possible: analytic area, sampled point membership away from boundaries, and loop nesting. Agreement increases confidence; none should be mislabeled as a universal proof.

## 23.6 Tolerance is a policy, not equality

Hoffmann's §4.2 discusses a basic difficulty with approximate coincidence. With tolerance $\varepsilon$, choose points on a line at $0$, $0.8\varepsilon$, and $1.6\varepsilon$. Consecutive pairs are within tolerance, but the first and last are not. Thus “distance less than epsilon” is not a transitive equality relation.

This matters when sewing vertices. Pairwise welding performed in different orders can create different identifications. A union-find computes a transitive closure of the selected pair relations, but that closure may merge endpoints farther apart than the original tolerance. It solves a combinatorial grouping problem, not the question of whether the resulting geometry is acceptable.

Specify a policy: representative selection, maximum cluster diameter, geometric displacement budget, and rules for protected features. Preserve the original coordinates and report what changed. Exact predicates, discussed in [[Engineering CAD 26 - Predicates, constructions and symbolic perturbation|chapter 26]], solve a different problem: deciding facts about the represented input without rounding-induced inconsistency.

## 23.7 Exercises and implementation checkpoint

> **Exercise 23.A.** In $\mathbb R^2$, let $A=[0,2]^2$ and $B=[2,4]\times[1,3]$. Compute the ordinary intersection, regularized intersection, union area, and regularized difference area. Explain why an area-only assertion cannot distinguish an empty intersection from a contact edge.

> **Exercise 23.B.** Give a regular closed set whose boundary is not a manifold. State a local test that rejects the boundary without using its Euler characteristic.

> **Exercise 23.C.** Design a test suite for rectangle difference that includes disjoint, overlapping, contained, coincident, edge-touching, and point-touching cases. Test membership at points whose distance from every boundary exceeds a chosen margin. Keep exact set semantics separate from the numerical margin used by the test.

The implementation checkpoint is an interval-based rectangle algebra with explicit result dimension and a documented regularization option. Do not begin arbitrary curved Booleans until its contact cases are unambiguous.

> **Careful.** Regularized set semantics, manifold-boundary restrictions and tolerance-based simplification are three separate policies. Do not use one as an unstated substitute for another.

## Toward a reusable API

```text
classify(point, region) -> Inside | Outside | Boundary | Indeterminate
boolean(op, a, b, contact_policy) -> RegionResult
RegionResult = geometry + provenance + diagnostics + tolerance_changes
validate_representation(region) -> Findings
validate_embedding(region) -> Findings
```

## Key points

A solid representation encodes a point set without enumerating its points. Interior and regularization depend on the ambient dimension. Regularized intersection removes lower-dimensional contacts, but contact queries may still preserve them separately. Regular closed sets need not have manifold boundaries. Representation validity, geometric realization, operation semantics, and design intent require different evidence. Approximate coincidence is not mathematical equality.

## Further reading

[[Engineering CAD B - Source Library#^ref-mantyla-upload|Mäntylä, §§3.3–3.6, printed pp. 32–51]], develops mathematical solids and representation schemes; §3.4.2 is printed p. 33, PDF p. 51. [[Engineering CAD B - Source Library#^ref-hoffmann-upload|Hoffmann, §2.2.2, printed p. 22]], defines regularized Booleans; §§2.3–2.4 distinguish boundary domains and validity. Read Hoffmann §4.2, printed pp. 113–123, for the arithmetic and coincidence problems rather than treating a tolerance as a universal repair.

---

[[Engineering CAD 22 - Engineering a trustworthy next version|← Chapter 22. Engineering a trustworthy next version]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 24 - Half-edge structures and Euler construction|Chapter 24. Half-edge structures and Euler construction →]]
