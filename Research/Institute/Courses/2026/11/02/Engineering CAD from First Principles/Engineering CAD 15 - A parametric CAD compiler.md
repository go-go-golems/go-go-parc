---
title: "Engineering CAD from First Principles — Chapter 15. A parametric CAD compiler"
aliases:
  - "Chapter 15. A parametric CAD compiler"
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

# Chapter 15. A parametric CAD compiler

[[Engineering CAD 14 - B-rep, STEP, meshes and manufacturing|← Chapter 14. B-rep, STEP, meshes and manufacturing]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 16 - Rust, WebAssembly and resource ownership|Chapter 16. Rust, WebAssembly and resource ownership →]]

Mathematics in this chapter: [[Mathematics - Graphs and Discrete Structures|Graphs and Discrete Structures]] (see [[Mathematics]]).

A parametric CAD program describes a dependency graph, not just a sequence of commands. When a user changes one dimension, the system should recompute exactly the affected parts of the graph while keeping independent results, references and diagnostics consistent. This is the problem of incremental computation and cache correctness.

## 15.1 A feature tree is a directed acyclic graph

Consider the following simplified model:

```text
width ─┬─> rectangle sketch ─> extrusion ─> fillet ─> export
       │
       └─> hole positions ─────────────────> hole cut ─────┘
height ──────────────────────> extrusion
radius ───────────────────────────────> fillet
```

Each node is a pure computation only if all relevant inputs are explicitly represented. In that ideal case, a node output is a function of its declared predecessors. If `radius` changes, the fillet and its descendants must recompute, but the independent rectangular sketch need not.

A *feature timeline* can be represented as a DAG because each operation consumes earlier geometry. A presentation may show a sequence, but dependency semantics are richer: multiple branches can share sketches, parameter expressions and reference geometry.


%%FIG:15%%

## 15.2 The cache correctness condition

For a deterministic function $f$, a cache entry keyed by $k(x)$ is safe only if

$$
k(x_1)=k(x_2)\implies f(x_1)=f(x_2).
$$

A key that forgets a parameter, tolerance, printer configuration, selected face or external environment can falsely reuse an old result. Such a cache bug is particularly dangerous in CAD: it can return a plausible older solid with no visible error.

The easiest sound key is a content fingerprint of every semantically relevant input, including the fingerprints of upstream nodes. This may be conservatively large; correctness comes first, and performance optimization can refine dependencies afterward.

## 15.3 Jig's per-feature cache

Jig's [compile.js](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/compile.js) constructs feature cache keys from the feature type, canonicalized arguments and options, previous-feature key, relevant parameter values, and some fit/build context. It keeps a bounded worker-lifetime cache and reuses existing B-rep results when keys agree.

The architecture is promising. The risk lies in *dependency discovery*. If a JavaScript callback closes over an undeclared variable or a selector depends on a context not included in the key, the content hash can miss an input. It is hard to infer complete dependencies from arbitrary JavaScript functions by textual analysis.

A more reliable language design distinguishes declarative expressions from opaque callbacks. Declarative expressions carry explicit dependencies in an AST. Opaque functions can be marked noncacheable or required to declare and validate their dependencies.

**Try it.** [The cache bench](lab:sketch?id=cache) changes `width`, `height` and `filletRadius` on a small feature graph. It highlights which nodes a sound incremental scheduler should recompute.

## 15.4 Persistent identity and cache identity are different

A feature identity answers “which conceptual operation is this?” A content hash answers “are its current inputs equivalent to a previous execution?” A changed radius should not change the conceptual identity of `fillet1`, but it must change its result hash. Conversely, two distinct features with identical arguments might share geometry computation while retaining different provenance IDs.

Separating these concepts allows common-subexpression sharing without accidentally merging user-visible feature identities.

## 15.5 Intermediate representations and explainability

Jig returns multiple IR levels, a feature graph, resolved parameters, decisions, timing traces and geometric metrics. That is a valuable compiler design. In a reliable system each representation should have a precise meaning and a checkable invariant: an IR node must name its dependencies, a cached pass must record the key and version under which it was reused, and a metric must identify whether it came from exact B-rep integration or mesh approximation.

The `why` query is more powerful when it can produce a causal chain: “this face exists because extrusion `body` swept sketch entity `outline.left`; its placement depends on width; it was split by `hole2`; this compile reused the extrusion and recomputed the hole.”

Such an explanation can be mechanically verified against the actual graph. It should not be generated as free-form text without structured backing evidence.

## 15.6 Transactions and last-known-good states

Interactive CAD frequently has invalid intermediate states. A parameter edit may make a fillet impossible or a sketch inconsistent. A good workbench can preserve the last valid visual result while displaying a failure for the current requested model. But the state must be unambiguous: the viewer may show an older solid, while the current compilation is failed.

Model changes are best treated as transactions: evaluate candidate inputs, collect diagnostics, commit a valid new state or retain the previous one with a visible stale marker. When an AI agent edits code, the same transactional model permits checking proposals without replacing the current working model.

> **Exercise.** Find a case where a cache key including only `(featureId, explicitParameters)` is unsound. Construct two different geometric inputs that would collide. Propose the smallest additional key data that fixes the example.

> **Careful.** Hash stability is not semantic stability. A deterministic hash of an incomplete dependency list is still an incorrect cache key.

## Toward a reusable API

```text
NodeId          conceptual feature identity
InputFingerprint  canonical hash of every semantic dependency
FeatureValue    geometry + provenance + validity report
CompileTrace    evaluation/cached state and causal inputs
Transaction     candidate changes, diagnostics, commit/revert
```

## Key points

A parametric model is an incremental computation graph. Safe caching requires complete semantic dependencies. Feature identities are distinct from content hashes. Arbitrary callbacks complicate dependency analysis. Structured IR and diagnostics can make a compiler inspectable and allow transactional edits without losing the last good model.

## Further reading

- [JigCAD compilation and cache implementation](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/compile.js) shows the actual key construction.
- [JigCAD build contract](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BUILD.md) documents ProgramData and execution traces.
- [JigCAD naming implementation](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/body.js) links feature provenance with result topology.

---

[[Engineering CAD 14 - B-rep, STEP, meshes and manufacturing|← Chapter 14. B-rep, STEP, meshes and manufacturing]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 16 - Rust, WebAssembly and resource ownership|Chapter 16. Rust, WebAssembly and resource ownership →]]
