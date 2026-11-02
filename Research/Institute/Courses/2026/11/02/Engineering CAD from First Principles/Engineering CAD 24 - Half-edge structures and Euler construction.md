---
title: "Engineering CAD from First Principles — Chapter 24. Half-edge structures and Euler construction"
aliases:
  - "Chapter 24. Half-edge structures and Euler construction"
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

# Chapter 24. Half-edge structures and Euler construction

[[Engineering CAD 23 - Solids as regular sets and representation contracts|← Chapter 23. Solids as regular sets and representation contracts]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 25 - Simplicial complexes, links and homology|Chapter 25. Simplicial complexes, links and homology →]]

A list of segments can describe the visible edges of a square, but it does not directly answer which face lies on either side or which edge comes next around a hole. A half-edge structure stores those answers. This chapter derives its invariants, traces a face split, and explains why Euler operations preserve a chosen topological structure without certifying its geometric realization.

**Source basis.** The planar DCEL convention comes from de Berg et al., §2.2, printed pp. 29–33. The solid-modeling operations and their implementation layers come from Mäntylä, chapters 9–11. The Rust-oriented storage and transaction recommendations are this guide's implementation design, not code reproduced from either book. [[Engineering CAD B - Source Library#^ref-deberg-upload|de Berg]] · [[Engineering CAD B - Source Library#^ref-mantyla-upload|Mäntylä]].

## 24.1 One edge, two directed uses

Let a square have vertices $A=(0,0)$, $B=(4,0)$, $C=(4,3)$, $D=(0,3)$. Its bounded face is traversed $A\to B\to C\to D\to A$. Every directed edge has that face on its left. The opposite traversal bounds the unbounded exterior face, which also lies to the left of its own directed uses.

For each geometric edge create two **half-edges**. A half-edge $h$ stores an origin vertex, an incident face, and three connectivity references: `twin(h)`, `next(h)`, and `prev(h)`. Its destination is `origin(twin(h))`. The twin has the opposite direction along the same undirected edge.

A face stores a representative half-edge of its outer boundary, plus representatives of its inner boundary components. With the face-left convention, outer cycles are counterclockwise and holes are clockwise. The unbounded face has no outer component in de Berg's convention. These are orientation conventions, not conclusions inferred repeatedly from approximate coordinates.

This is a **doubly-connected edge list**, or DCEL. A solid boundary uses closely related directed edge uses, but a planar DCEL and a curved B-rep are not the same representation. Curved edges need geometric support, parameter intervals, and often face-specific pcurves. Nonmanifold edges may require more than a single twin pair.

## 24.2 Make invariants explicit

For every ordinary half-edge in this restricted structure require

$$
\operatorname{twin}(\operatorname{twin}(h))=h,
\qquad \operatorname{twin}(h)\ne h,
$$

$$
\operatorname{prev}(\operatorname{next}(h))=h,
\qquad \operatorname{next}(\operatorname{prev}(h))=h.
$$

Also require that the destination of $h$ equals the origin of `next(h)` and that `next(h)` belongs to the same face cycle. Every stored cycle must terminate by returning to its starting half-edge, not by entering a different cycle. Each live reference must identify an existing record of the correct type.

These assertions are cheap enough to run after every edit in a small educational modeler. Global audits can additionally check that every half-edge appears in exactly one boundary cycle and every cycle is assigned to the intended face. Geometric tests are separate: a closed cycle can still cross itself.

```rust
struct VertexId { slot: u32, generation: u32 }
struct HalfEdgeId { slot: u32, generation: u32 }
struct FaceId { slot: u32, generation: u32 }

struct HalfEdge {
    origin: VertexId,
    twin: HalfEdgeId,
    next: HalfEdgeId,
    prev: HalfEdgeId,
    face: FaceId,
}
```

This is a type sketch, not a complete compiled library. Generation tags prevent a stale reference to a deleted slot from silently naming a later record that reuses that slot. They do not prevent logical mistakes among live records; invariant checks remain necessary.

## 24.3 Trace a face split, pointer by pointer

Name the bounded square's half-edges $h_0=A\to B$, $h_1=B\to C$, $h_2=C\to D$, $h_3=D\to A$. Initially their `next` cycle is $(h_0,h_1,h_2,h_3)$. Add diagonal $A\to C$ as a pair $d=A\to C$ and $\bar d=C\to A$.

The two resulting bounded cycles are

$$
(A\to B,\;B\to C,\;C\to A),\qquad
(A\to C,\;C\to D,\;D\to A).
$$

Their actual `next` cycles are $(h_0,h_1,\bar d)$ and $(d,h_2,h_3)$. Set `twin(d)=dbar` and its inverse. Replace four successor relations:

```text
next(h1) = dbar       next(dbar) = h0
next(h3) = d          next(d) = h2
```

Set the corresponding `prev` relations, then assign a face identifier to every half-edge in each new cycle. The exterior square cycle does not change. We started with $V=4,E=4,F=2$, counting the exterior. We finish with $V=4,E=5,F=3$. The planar Euler total remains $V-E+F=2$.

> **Try it.** Open [the half-edge traversal lab](lab:sketch?id=halfedge). Toggle the diagonal and select a half-edge. Read its origin, destination, twin, predecessor, successor, and incident face. Follow `next` until the cycle closes, then cross `twin` to inspect the neighboring face.

The lab reconstructs the small example from its face cycles; it is not executing the in-place splice above. This separation is useful: the reconstruction provides an independent expected result against which an in-place implementation can be tested.

%%FIG:24%%

## 24.4 Euler operations are local transformations with preconditions

Mäntylä uses mnemonic names such as **MEV**, “make edge and vertex,” and **MEF**, “make edge and face.” Their general meanings matter. MEV splits a vertex's incident-edge cycle into two vertices connected by a new edge. Adding a dangling edge and a fresh vertex inside a face is a special case. It is not correct to define every MEV as “subdivide an existing edge.”

MEF connects two uses of vertices belonging to the same loop and splits that face. Its inverse KEF removes an edge separating two distinct faces and joins their boundaries. A low-level MEF requires the correct half-edge positions, not merely two coordinate triples. Different occurrences of a vertex in a loop may define different edits.

Mäntylä also separates **low-level** operators, which receive direct references and perform no geometric search, from **high-level** operators, which accept identifiers and locate the relevant entities. This is an important library boundary. Picking a face from a screen, resolving a persistent name, and mutating a face loop should not be one inseparable procedure.

The implementation of `lmef` in §11.5 does not automatically redistribute all other loops of the old face. That requires an additional classification step. A face split through a region containing holes therefore needs both a topological splice and a geometric decision about which new face contains each hole.

## 24.5 Construct a cube and account for every entity

A skeletal initialization MVFS creates one vertex, one face, and a shell-like construction state. Three special-case MEV operations add three vertices and three edges. One MEF closes the quadrilateral into a two-sided lamina. Four more MEV operations create the four vertical edges and their upper vertices. Four MEF operations connect the upper vertices and complete the side faces and top.

The count is

$$
V=1+7=8,\qquad E=7+5=12,\qquad F=1+5=6.
$$

Thus $8-12+6=2$. The construction is described in Mäntylä §9.3, before the additional steps that make a through-hole. Notice that the intermediate skeleton and lamina are useful states in the construction language, not positive-volume solids. A transaction can permit these internal states while exposing only fully validated results to ordinary modeling operations.

Choosing cube coordinates produces a cube. Choosing bad coordinates can produce intersecting faces while leaving the same counts and connectivity. Euler operations preserve their topological invariants under their preconditions; they do not make arbitrary coordinates geometrically valid.

## 24.6 Faces with holes change the counting formula

A face with an inner loop is not a disk-like 2-cell. Under Mäntylä's convention, let $R$ be the total number of inner face loops, $S$ the number of connected shells, and $G$ the sum of their genera. Then the necessary count is

$$
V-E+F-R=2(S-G).
$$

The reason for the correction is concrete. Connect each inner loop to its outer loop with a bridge. Each bridge adds an edge without adding a vertex or a face, converting the face boundary into a disk-like decomposition. After $R$ bridges, the ordinary Euler expression uses $E+R$, giving the displayed equation.

For a rectangular tube with a rectangular through-hole, one representation has $V=16,E=24,F=10,R=2,S=1,G=1$. The two annular end faces account for the two rings. Then $16-24+10-2=0=2(1-1)$. Forgetting the rings gives two and falsely suggests genus zero.

This formula has assumptions: oriented manifold shells and the specified face-loop conventions. Do not apply it blindly to arbitrary degenerate periodic B-reps or nonmanifold complexes. [[Engineering CAD 25 - Simplicial complexes, links and homology|Chapter 25]] gives stronger local checks.

## 24.7 Transactions, undo, and safe mutation

An edit may need several pointer changes before any invariant is restored. Publishing after the first assignment exposes an invalid intermediate structure. Use a transaction: validate preconditions, allocate new records, prepare all changes, apply them, audit the affected neighborhood, and commit. On failure restore the previous state.

For a small modeler, copying an affected subgraph can be simpler than logging every mutation. For large models, an inverse-operation log or persistent storage may be preferable. A topology edit's inverse must restore record identity and attributes, not only produce an isomorphic graph. This is why “undo” and “run a mathematically inverse operation” are not always equivalent at the document level.

In Rust, use arena identifiers to avoid a web of mutable references with interdependent lifetimes. Read the relevant IDs first, validate them, then perform writes through the owning arena. Make the transaction the exclusive mutation interface. Serialize stable identifiers and geometric attributes rather than raw addresses.

## 24.8 Exercises and checkpoint

> **Exercise 24.A.** Write the complete half-edge table for the square split by $AC$. Include the unbounded face. Verify every invariant in §24.2 and check the Euler total.

> **Exercise 24.B.** Subdivide an ordinary edge by inserting one vertex. Derive the changes in $V,E,F$ and explain why this is a different description from the general vertex-splitting MEV operation.

> **Exercise 24.C.** Split a face containing two inner loops. Construct a placement where one loop belongs to each resulting face. Identify which decisions are combinatorial and which require geometric classification.

The checkpoint is a square-face splitter with an audit function and reversible transactions. Test both the expected result and the expected failure when the selected half-edges belong to different loops.

> **Careful.** A successful topological edit does not establish that its coordinates form a valid embedded solid.

## Toward a reusable API

```text
face_cycle(start) -> bounded iterator of HalfEdgeId
split_face(h_a, h_b) -> new edge, new face, undo record
split_edge(edge, point) -> new vertex, edge pair, undo record
audit_local(changed_ids) -> Findings
commit(edit) -> Snapshot | FailureWithRollback
```

## Key points

Directed edge uses turn adjacency into explicit data. Face-left orientation gives different traversal directions for outer and inner boundaries. Euler operators have precise preconditions and do not certify coordinates. A face split must redistribute holes as well as splice pointers. Euler counts require ring corrections when faces are not disks. Transaction boundaries prevent partially updated topology from escaping into the model.

## Further reading

[[Engineering CAD B - Source Library#^ref-deberg-upload|de Berg et al., §2.2, printed pp. 29–33]], gives the DCEL records and traversal conventions; the record example is printed p. 32, PDF p. 42. [[Engineering CAD B - Source Library#^ref-mantyla-upload|Mäntylä, chapter 9, printed pp. 139–160]], develops Euler operators and the cube example. Continue through chapter 10, printed pp. 161–174, for the data structure and chapter 11, printed pp. 175–198, for implementation. Chapter 16 develops undo and transaction management.

---

[[Engineering CAD 23 - Solids as regular sets and representation contracts|← Chapter 23. Solids as regular sets and representation contracts]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 25 - Simplicial complexes, links and homology|Chapter 25. Simplicial complexes, links and homology →]]
