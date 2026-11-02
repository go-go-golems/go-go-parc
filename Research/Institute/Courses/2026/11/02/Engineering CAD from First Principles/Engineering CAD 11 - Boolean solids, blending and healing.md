---
title: "Engineering CAD from First Principles — Chapter 11. Boolean solids, blending and healing"
aliases:
  - "Chapter 11. Boolean solids, blending and healing"
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

# Chapter 11. Boolean solids, blending and healing

[[Engineering CAD 10 - From planar curves to valid profiles|← Chapter 10. From planar curves to valid profiles]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 12 - Identity through parametric edits|Chapter 12. Identity through parametric edits →]]

Mathematics in this chapter: [[Mathematics - Curves and Surfaces|Curves and Surfaces]], [[Mathematics - Point-Set Topology|Point-Set Topology]] (see [[Mathematics]]).

Boolean operations and fillets are central to mechanical CAD because they alter both geometry and topology. They are also among the hardest features to make reliable: intersection curves, coincident faces, tangencies, tolerance propagation and new face identities must all agree. This chapter develops the underlying decomposition and explains what OpenCascade provides and what JigCAD still must verify.

## 11.1 Sets first, representations second

For solid point sets $A,B\subset\mathbb R^3$, the basic Boolean operations are union $A\cup B$, intersection $A\cap B$, and difference $A\setminus B$. Their meaning is set-theoretic. A B-rep algorithm must construct boundary faces whose inside/outside classification agrees with those sets.

A Boolean between two spheres is not just “delete overlapping triangles.” In analytic B-rep modeling, it requires finding intersection curves of the underlying surfaces, trimming faces at those curves, classifying candidate pieces, then assembling oriented shells and solids.

OpenCascade's Boolean algorithms use an intersection-processing phase and a rebuilding phase. They also report shape modification history, which Jig uses to maintain topology names.

## 11.2 A two-circle calculation before three dimensions

For two equal disks of radius $r$ whose centers are distance $d$ apart, with $0<d<2r$, the overlap area is

$$
A_\cap=2r^2\cos^{-1}\left(\frac d{2r}\right)-\frac d2\sqrt{4r^2-d^2}.
$$

Let $r=10$ mm and $d=10$ mm. Then $A_\cap=200\pi/3-50\sqrt3\approx122.83697$ mm². Each disk has area $100\pi\approx314.15927$ mm², and their union has area $200\pi-A_\cap\approx505.48156$ mm². The inclusion–exclusion identity holds exactly.

At $d=20$ mm, the disks touch at one point and overlap area tends to zero; for $d>20$ mm, they are disjoint. The boundary topology changes at $d=20$. The same three regimes—crossing, tangency, separation—drive difficult Boolean edge cases in 3D.


%%FIG:11%%

**Try it.** [The Boolean lens bench](lab:sketch?id=booleans) computes the overlapping area as $d$ changes, and checks inclusion–exclusion. Look near tangency and observe how quickly the intersection becomes small.

## 11.3 The Boolean pipeline in more detail

A general B-rep Boolean may involve broad-phase bounding boxes, edge/edge and edge/face intersections, face/face intersection curves, splitting of edges and faces, classification of split pieces, selection based on the requested set operation, shell construction and shape validation.

The hard cases involve coincident surfaces, nearly tangent intersections, tiny sliver faces, periodic seams, and tolerance mismatches. Exact analytic surface equations do not eliminate numeric difficulty: intersections of general spline surfaces usually require iterative numerical algorithms and tolerance decisions.

The *general fuse* approach constructs common subdivision information once, then uses a different selection rule for union, difference or intersection. This explains why modification history and correct classification are both natural outputs of the Boolean engine.

## 11.4 Fillets are a surface-construction problem

A constant-radius fillet of a sharp edge replaces the neighborhood of the edge with a smooth blending surface. For two perpendicular planes, the elementary cross-section is a circular arc. On complex surfaces, the blend requires offset surfaces, intersection loci, trimming and corner patches. The radius may be feasible for some edges and impossible for others.

A non-monotonic failure is possible: a fillet can fail at one radius because of a tangency or a topological event while succeeding at both smaller and larger radii. Therefore, searching for “the maximum allowed fillet” by binary search assumes a monotonic property that may not hold. Jig's issue register documents a case that prompted a more accurate tangent-failure diagnostic.

A practical fillet API should return a structured failure: source edge, selected radius, local geometric cause, and possibly nearby radii that succeed. It should also validate that faces outside the intended local blend were not silently deleted.

## 11.5 Shelling and offsets

A shell operation offsets selected faces by thickness $t$ and connects boundaries with rim faces. Mathematically, a surface offset is $S_t(u,v)=S(u,v)+t n(u,v)$ for unit normal $n$. This can develop singularities where the offset distance reaches the reciprocal of principal curvature, or self-intersections when offset regions collide.

Even a shell that appears valid at a small thickness may fail when $t$ approaches a narrow wall or concave corner. A good system can classify “too thick,” “self-intersection,” “unclosed rim” and “unsupported geometry” separately. Merely catching an exception from `BRepOffsetAPI_MakeThickSolid` does not give the user enough information.

## 11.6 Shape analysis before shape healing

OpenCascade provides shape analysis and repair tools for disconnected wires, missing curves, seam errors, tolerances, and inconsistent orientation. Healing can make a shape usable for downstream operations, but it is not free: it may move vertices, merge edges or otherwise change geometry.

Therefore, a healing report should include original defects, repair actions, geometric deviation and changed topology. Treat a healed shape as a modified artifact with provenance, not as an identical substitute.

For a parametric CAD compiler, automatic repair is especially sensitive: moving geometry in one feature may invalidate stable references or make a dimensioned relationship inaccurate. Recovery should be explicit, bounded and reproducible.

## 11.7 What JigCAD actually uses

Jig's [ops.js](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/ops.js) calls `BRepAlgoAPI_Fuse`, `BRepAlgoAPI_Cut`, `BRepAlgoAPI_Common`, `BRepFilletAPI_MakeFillet`, `BRepFilletAPI_MakeChamfer` and offset-related APIs. That provides a mature core implementation for elementary solid operations.

The missing work is surrounding validation and integration: richer kernel diagnostics, greater shape-healing coverage, tolerance policy, systematic degeneracy testing and careful feature naming after operations. These are important even if no new Boolean algorithm is implemented in Rust.

> **Exercise.** Prove $V(A\cup B)+V(A\cap B)=V(A)+V(B)$ by partitioning the two sets into disjoint regions. Then propose a test that would detect a Boolean implementation that returns the correct volume but incorrect face orientations.

> **Careful.** Healing can repair topology while changing the intended geometry. Record how much and where it changed before accepting an automatic fix.

### Deeper study: specify the result before implementing the boolean

[[Engineering CAD 23 - Solids as regular sets and representation contracts|Chapter 23]] derives regularized intersection and explains why a shared contact face can disappear from a solid-only result while remaining relevant to a contact query. [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction|Chapter 27]] shows Boolean selection on an overlay of planar regions. [[Engineering CAD 29 - Tracing intersections of curved surfaces|Chapter 29]] develops the curved-support intersection that a general B-rep Boolean must combine with trimming, classification and reconstruction. Each is a separate contract, not a single tolerance adjustment.

## Toward a reusable API

```text
BooleanResult { brep, sourceToOutputHistory, contacts, validations }
BlendResult { brep, createdFaces, preservedFaces, failureCause }
HealPolicy { maxGap, maxDeviation, allowedTopologyChanges }
HealReport { originalFindings, repairs, postValidation }
```

## Key points

Boolean semantics come from set theory; B-rep algorithms implement the boundary reconstruction. The difficult work lies in intersections, classifications and tangencies. Fillet feasibility is not necessarily monotonic in radius. Offsets can self-intersect and create singularities. Shape healing is useful only when its geometric changes are bounded and reported.

## Further reading

- [OpenCascade Boolean operations guide](https://www.occt3d.com/dev/doc/overview/html/specification__boolean_operations.html) explains its intersection and building phases.
- [OpenCascade shape healing](https://www.occt3d.com/dev/doc/overview/html/occt_user_guides__shape_healing.html) covers analysis and repair.
- [JigCAD feature operations](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/ops.js) shows the actual OCCT calls.
- [JigCAD issue register](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BOOK-ISSUES.md) contains concrete tangent-fillet and invalid-solid cases.

---

[[Engineering CAD 10 - From planar curves to valid profiles|← Chapter 10. From planar curves to valid profiles]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 12 - Identity through parametric edits|Chapter 12. Identity through parametric edits →]]
