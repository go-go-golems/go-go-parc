---
title: "Engineering CAD from First Principles — Chapter 3. Topology and boundary representation"
aliases:
  - "Chapter 3. Topology and boundary representation"
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

# Chapter 3. Topology and boundary representation

[[Engineering CAD 02 - Curves, surfaces and rational geometry|← Chapter 2. Curves, surfaces and rational geometry]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 04 - Constraints become equations|Chapter 4. Constraints become equations →]]

Mathematics in this chapter: [[Mathematics - Combinatorial and Algebraic Topology|Combinatorial and Algebraic Topology]] (see [[Mathematics]]).

A solid is not determined by its visible faces alone. It must also specify how those faces meet, which side is inside, and whether the boundary actually encloses a valid volume. This chapter derives the combinatorial structure used by a B-rep kernel and distinguishes topological checks from numerical geometric checks.

## 3.1 Geometry versus topology

A plane is an infinite geometric surface. A **face** is a bounded, oriented subset of that plane. A line or circle is an infinite or periodic geometric curve; an **edge** uses a bounded portion of a curve. A **vertex** identifies an endpoint and may carry a tolerance. The topology describes incidence: which oriented edges form loops, which loops bound faces, and which faces bound shells and solids.

A useful hierarchy is

$$
\text{vertex}\subset\text{edge}\subset\text{wire}\subset\text{face}\subset\text{shell}\subset\text{solid}.
$$

The inclusion symbol here denotes a containment hierarchy of topological entities, not literal subset inclusion of their storage objects. OpenCascade also supports compounds and compsolids.

A face may have one *outer* wire and several *inner* wires. For a plate with four circular holes, the top planar face has five boundary wires. Its underlying geometric plane is still a single plane.

## 3.2 Directed uses and the half-edge idea

An undirected geometric edge may be used by two adjacent faces with opposite orientations. A **coedge** or directed edge use records which way the edge is traversed as part of a particular face loop. A canonical half-edge structure stores a twin, a next pointer and a face. OpenCascade uses its own topology representation but the half-edge abstraction is invaluable for reasoning about algorithms.

A **closed orientable manifold** neighborhood of each ordinary boundary edge should have two compatible face uses. A boundary edge used once indicates an open shell; an edge used by three incident surface sheets indicates a nonmanifold junction. Seams of periodic faces and degenerate edges require special treatment, so raw counts of distinct edge objects can be misleading.

For an oriented face with outward normal $n$, reversing its orientation changes which side of the surface is material. This is why computing a positive-looking triangulation and checking only the bounding box does not establish solid validity.

%%FIG:3%%

## 3.3 Parametric curves on surfaces: pcurves

On a face supported by $S(u,v)$, a boundary edge can be stored by a 2D curve $(u(t),v(t))$ in the surface domain. This is its **pcurve**. The corresponding 3D boundary is $C(t)=S(u(t),v(t))$.

A correct face must keep the 3D curve, its pcurve, and the surface consistent within tolerances. Periodic surfaces make this subtle: a cylindrical face can have a seam that is closed in 3D but appears at opposite sides of its unwrapped $(u,v)$ domain. Missing or reversed seam edges are classic shape-healing cases.

The [OpenCascade shape-healing guide](https://www.occt3d.com/dev/doc/overview/html/occt_user_guides__shape_healing.html) describes repairs for edge connectivity, seam edges and 2D/3D curve consistency.

## 3.4 Euler characteristic and genus

For a connected closed orientable surface, choose a genuine cell decomposition and count vertices $V$, edges $E$ and faces $F$. Its Euler characteristic is

$$
\chi=V-E+F=2-2g,
$$

where $g$ is the genus (number of handles). The boundary of a box has $(V,E,F)=(8,12,6)$, giving $\chi=8-12+6=2$ and $g=0$. A torus has $g=1$ and $\chi=0$ in any valid cell decomposition.

If a face contains holes or if edges are degenerate, a simplistic “number of OCCT faces minus number of OCCT edges” computation need not be a valid cell decomposition. One must account for the face's boundary structure and identify periodic or degenerate representations consistently. For instance, a sphere can be represented by a single periodic surface face with seam and pole degeneracies; that representation is not a one-face simplicial decomposition.

Jig's issue log documents an earlier genus calculation that counted degenerate edges incorrectly. Its later repair excludes those edges and warns if a resulting genus is not a nonnegative integer. That is a useful *sanity check*, not a proof of manifoldness.

**Try it.** Open [the Euler characteristic bench](lab:sketch?id=euler) to inspect the count for a cube surface and a torus. The diagram uses mathematical cell decompositions, not OpenCascade's exact internal face enumeration.

## 3.5 Why validity has layers

There are at least four distinct questions:

**Combinatorial consistency:** are all incidence pointers and orientations legal? **Geometric consistency:** do vertices lie on their incident curves and do boundary curves lie on their supporting surfaces within tolerance? **Topological manifoldness:** does every point have an appropriate disk-like or half-disk-like neighborhood? **Physical validity:** does the oriented boundary enclose the intended positive-volume region without self-intersections or extraneous components?

`BRepCheck_Analyzer::IsValid` addresses a collection of OCCT-specific criteria, but it is not a complete independent proof. The OpenCascade Boolean documentation explicitly warns that validity checks themselves can be imperfect. A practical validation system therefore combines several independent measurements and checks.

One particularly useful independent check is the **signed-volume integral**. For an oriented closed triangular mesh with triangles $(a,b,c)$ consistently directed outwards,

$$
V=\frac16\sum_{(a,b,c)}\det[a\ b\ c].
$$

This formula sums signed tetrahedral volumes relative to the origin. It can detect reversed orientation or gross inconsistencies when compared with exact B-rep volume properties. For better conditioning, translate the mesh near the origin before computing the sum and use stable summation.

## 3.6 A concrete example: plate with one through-hole

Consider a rectangular prism $20\times20\times10$ mm with a through-hole of radius $4$ mm. When the hole lies strictly inside, the exact material volume is

$$
V=(400-16\pi)\cdot10\approx3497.3452\;\mathrm{mm}^3.
$$

The object has one handle through the material, so its closed boundary has genus one. If the hole moves until it touches the side boundary, the topological type changes at contact. That is not merely a small numeric adjustment: the identity of boundary loops changes, and a modeler must decide whether to reject the tangent construction or represent the resulting touching boundary in a supported way.

JigCAD's documented tangent-hole failure arose in this exact family of cases: the profile and resulting solid no longer represented the intended set. The correct implementation must reason about topology at the contact event, not only compare the output volume against an error threshold.

> **Exercise.** A cube has one face removed. Does $V-E+F=2$ still hold for the remaining open shell? Explain what topological object you are counting and why the boundary changes the result.

> **Careful.** Do not equate an OCCT `TopoDS_Face` count with the number of 2-cells in an arbitrarily chosen regular cell decomposition without checking seams, degeneracies and inner wires.

### Deeper study: build the topology before trusting its counts

[[Engineering CAD 24 - Half-edge structures and Euler construction|Chapter 24]] traces the actual half-edge changes in a square-face split and derives the ring correction to Euler counting. [[Engineering CAD 25 - Simplicial complexes, links and homology|Chapter 25]] then constructs a counterexample: two tetrahedron shells sharing a vertex have two incident faces at every edge, but a disconnected vertex link. This is why an edge-count audit is not a complete manifold test. The mathematical definition of a regular solid, developed in [[Engineering CAD 23 - Solids as regular sets and representation contracts|chapter 23]], is also distinct from a manifold-boundary representation policy.

## Toward a reusable API

```text
Topology.explore(shape) -> vertices, oriented edge uses, wires, faces, shells
Topology.incidence(edge) -> adjacent oriented face uses
Topology.audit(shape) -> manifold status, boundary loops, degeneracies
Geometry.audit(shape) -> pcurve agreement, tolerance budgets, self-intersections
Brep.validate(shape) -> structured findings, not only a boolean
```

## Key points

An analytic surface is not a face, and a curve is not an edge. Oriented incidence determines the solid boundary. Pcurves link 2D surface coordinates with 3D edges. Euler characteristic checks topology only when counts are taken from a valid cell decomposition. A valid-looking B-rep may still represent the wrong intended region.

## Further reading

- [OpenCascade BREP format](https://occt3d.com/dev/doc/overview/html/specification__brep_format.html) is the primary reference for OCCT topology storage.
- [OpenCascade shape healing](https://www.occt3d.com/dev/doc/overview/html/occt_user_guides__shape_healing.html) explains pcurve and seam consistency.
- [ShapeAnalysis_Wire reference](https://dev.opencascade.org/doc/occt-7.6.0/refman/html/class_shape_analysis___wire.html) enumerates wire-level checks.
- [JigCAD B-rep issue reproductions](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BOOK-ISSUES.md) show how topological checks found real regressions.

---

[[Engineering CAD 02 - Curves, surfaces and rational geometry|← Chapter 2. Curves, surfaces and rational geometry]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 04 - Constraints become equations|Chapter 4. Constraints become equations →]]
