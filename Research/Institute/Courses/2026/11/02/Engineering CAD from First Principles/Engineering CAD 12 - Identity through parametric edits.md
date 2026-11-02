---
title: "Engineering CAD from First Principles — Chapter 12. Identity through parametric edits"
aliases:
  - "Chapter 12. Identity through parametric edits"
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

# Chapter 12. Identity through parametric edits

[[Engineering CAD 11 - Boolean solids, blending and healing|← Chapter 11. Boolean solids, blending and healing]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 13 - Assembly constraints on rigid motions|Chapter 13. Assembly constraints on rigid motions →]]

A face's array index is not its identity. Adding a hole can split a face, deleting a fillet can merge surfaces, and the Boolean engine can reorder its internal topology. A parametric model must distinguish *what a user referred to* from whichever face happens to occupy index seven after regeneration.

## 12.1 Identity is not geometric equality

Consider a rectangular plate with a boss. Its topmost face before the boss is added is the plate top. After adding the boss, the topmost face is the boss cap. The selector “highest face” remains a valid geometric query but changes its referent. The selector “the cap created by extrusion `plate`” should preserve its source feature identity.

These are different concepts: **extensional selection** describes current geometry, while **intentional or provenance-based selection** describes the construction history. Neither is always preferable. A design that truly wants the highest surface should use a geometric query; a fillet attached specifically to the original plate face should use a stable feature reference.

## 12.2 Provenance through modeling operations

OpenCascade exposes methods conceptually called `Generated`, `Modified`, and `IsDeleted` for many modeling algorithms. They answer how source subshapes contributed to the result. Jig's [body.js](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/body.js) propagates names through those histories.

An extrusion side face can be named `body/side[base.outline.bottom]`; a shell's inner face becomes `shell/inner[body/side[base.outline.bottom]]`. Such names provide a readable derivation chain from the script entity to the final face.

A face split into multiple pieces creates a one-to-many mapping. Jig adds suffixes like `#a` and `#b` to distinguish pieces, currently relying partly on their geometric positions. This gives deterministic names under many small edits but cannot guarantee semantic identity when pieces move past one another or a topology change reorders them.

%%FIG:12%%

## 12.3 What a naming system must promise

A useful persistent-reference contract specifies:

**Existence.** Does the referenced conceptual entity still exist after regeneration? **Uniqueness.** Does it denote exactly one current entity? **Stability.** Does it continue to denote the intended entity under benign dimension edits? **Failure visibility.** If the answer becomes ambiguous, does the compiler report it rather than choose arbitrarily?

The last condition is essential. It is preferable to stop a feature with a clear “reference ambiguous” diagnostic than to fillet the wrong edge silently. FreeCAD's documentation emphasizes detection and recovery precisely because general topological naming cannot be solved by a single heuristic.

## 12.4 Split and merge as correspondence relations

Instead of assuming a function from old face to new face, model correspondence as a relation

$$
H\subseteq F_{old}\times F_{new}.
$$

A preserved face may map to one result. A split maps to several. A merge can map several sources to one result. Deletion maps a source to none. A generated face may have provenance in an edge or vertex rather than an earlier face.

Each correspondence can carry a *role* (side, cap, bore, blend), feature ID, geometric support (plane/cylinder etc.), adjacency signatures, and a confidence/ambiguity status. Importantly, geometric proximity can help rank candidates, but should not silently override a contradictory provenance record.

**Try it.** [The topology naming bench](lab:sketch?id=naming) changes a notch that splits the top region into pieces. Observe how array indices, provenance labels and geometric selectors answer different questions. This is a schematic illustration of the naming problem.

## 12.5 Stable identifiers and graph semantics

There are two relevant levels of identity. A *feature* should have an explicit stable ID, ideally independent of execution order. An *output face* should refer to a feature role and the source entity or subshape. Anonymous auto-generated IDs are convenient in scripts but fragile as dependencies in long models.

An operation that changes a face's topology may invalidate downstream selections. A compiler should propagate a typed reference error, preferably with the original source location, the candidate result faces, and suggestions. Tests must verify the *intended geometry* rather than just that a name string remains present.

## 12.6 A regression test for reference stability

Construct a plate, add a boss, and fillet the plate's external top perimeter. Then vary plate width from $40$ to $80$ mm, move the boss, suppress the boss, insert another hole, and restore it. After each change, verify that the selected perimeter belongs to the plate, is convex where expected, and has the intended edge lengths. Also compare exported volume and validate the new solid.

A string comparison alone can miss a wrong reference. A selector that returns an edge with the same name but different geometric role can produce a successful yet incorrect downstream feature.

> **Exercise.** Define a correspondence relation for a face that splits into three pieces, two of which later merge. State which semantic questions an algorithm must ask before it can assign a unique stable name to the merged face.

> **Careful.** Topology naming is not equivalent to hashing geometric coordinates. Under a dimension edit, the same conceptual face can move and change area; different faces can also become geometrically congruent.

### Deeper study: preserve event provenance through topology edits

A stable geometric reference needs more than an array index. [[Engineering CAD 24 - Half-edge structures and Euler construction|Chapter 24]] shows how an edit changes directed uses and face cycles, and [[Engineering CAD 27 - Plane sweep, DCEL overlays and profile extraction|chapter 27]] recommends retaining input-curve intervals and event identity in every atomic edge. Those records provide evidence for naming decisions. They cannot remove genuine ambiguity when a design edit changes topology; an explicit ambiguous-reference result is preferable to silently selecting a different face.

## Toward a reusable API

```text
FeatureId, SketchEntityId, TopologyRef, ProvenanceRecord
Resolve(ref, model) -> Unique(shape) | Missing | Ambiguous(candidates)
History { generated, modified, deleted, split, merged }
Selector { provenanceQuery, geometricPredicate, expectCardinality }
```

## Key points

Array indices are ephemeral. Geometric selection and provenance selection express different intentions. Construction histories enable useful stable names but do not resolve every split or merge. The correct reference type should permit missing and ambiguous results. Regression tests must validate semantic identity across model edits.

## Further reading

- [FreeCAD's topological naming discussion](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Topological_naming_problem.md) explains why perfect automatic reference tracking is unrealistic.
- [JigCAD naming guide](https://github.com/go-go-golems/jig/blob/main/import/jigcad/content/docs/naming.md) documents its roles and warnings.
- [JigCAD `body.js`](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/body.js) implements history propagation.
- [OpenCascade Boolean guide](https://www.occt3d.com/dev/doc/overview/html/specification__boolean_operations.html) discusses generated and modified output geometry.

---

[[Engineering CAD 11 - Boolean solids, blending and healing|← Chapter 11. Boolean solids, blending and healing]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 13 - Assembly constraints on rigid motions|Chapter 13. Assembly constraints on rigid motions →]]
