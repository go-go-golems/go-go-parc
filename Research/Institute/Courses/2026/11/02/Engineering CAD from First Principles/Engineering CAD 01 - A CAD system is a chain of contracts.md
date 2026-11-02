---
title: "Engineering CAD from First Principles — Chapter 1. A CAD system is a chain of contracts"
aliases:
  - "Chapter 1. A CAD system is a chain of contracts"
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

# Chapter 1. A CAD system is a chain of contracts

[[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 02 - Curves, surfaces and rational geometry|Chapter 2. Curves, surfaces and rational geometry →]]

A parametric CAD model is not a picture and not a mesh. It is an executable construction whose numerical parameters, geometric curves, topological structure, manufacturing export and user-visible interpretation must agree. We will follow a single part through JigCAD and identify the invariants that make that agreement testable.

## 1.1 What a CAD kernel actually computes

A **geometric model** assigns mathematical meaning to points, curves and surfaces. A circle is a center and a radius; a cylindrical surface is a map from two parameters to three-dimensional space. A **topological model** states which pieces are incident, which loops bound a face, and which oriented faces enclose material. A **feature model** records the operations that construct and edit the object. These are different kinds of data. The triangle mesh used by the viewer is a fourth representation.

Suppose the intended object is a rectangular block of dimensions $60\times40\times30$ mm, hollowed from the top with $2$ mm walls and bottom. The outer volume is $V_o=60\cdot40\cdot30=72{,}000\;\mathrm{mm}^3$. If the hollow is a simple rectangular pocket, its inside dimensions are $56\times36\times28$ mm, and its volume is $56\cdot36\cdot28=56{,}448\;\mathrm{mm}^3$. The material volume is therefore $15{,}552\;\mathrm{mm}^3$. This is a **reference calculation**, not a claim that Jig's rounded-box shell has exactly this volume; rounded corners and the actual offset shape change it.

A good design system must not confuse a formula for a sharp-edged box with a measurement of a rounded shell. The worked calculation is useful precisely because it names its assumptions.

## 1.2 The construction pipeline

For a sketch-based solid, a useful mental model is

$$
\text{script}\longrightarrow\text{parameters}\longrightarrow\text{solved sketch}\longrightarrow\text{profile}\longrightarrow\text{B-rep}\longrightarrow\text{mesh/export}.
$$

The first transition resolves unit-bearing expressions, configurations and overrides. The next solves constraints and identifies free parameters. The third extracts *regions*: a set of closed boundary loops with nesting. The fourth builds topological wires and faces and then performs B-rep operations. The final stages compute a display triangulation or a file such as STEP or 3MF.

Each arrow has a contract. A solved sketch must satisfy every active driving constraint. A profile must represent exactly the region shown in the sketch. A B-rep must represent the intended volume and have appropriate orientation and manifold properties. A triangulation must approximate that B-rep within a stated tolerance. An exporter must preserve the properties promised by its format.

The critical observation is that **valid at one level does not imply correct at the next**. A B-rep can pass an internal validity check while representing a physically different region from the source sketch. A mesh can be watertight but approximate the wrong shape. A regenerated face can be geometrically correct but carry the wrong parametric name.

%%FIG:1%%

## 1.3 How JigCAD divides the work

JigCAD uses JavaScript to express features, parameters, selectors, compilation and most application orchestration. OpenCascade compiled to WebAssembly constructs and modifies analytic B-rep solids. A separate Rust WebAssembly module, `jig-compute`, evaluates expression tapes, computes derivatives, solves numerical sketch constraints and accelerates mesh analyses. The browser rendering code works on derived geometry; a Go server can provide the workbench and agent backend.

This division is intentional. A geometric kernel needs mathematical curves, intersection algorithms and topology. A *parametric compiler* additionally needs a dependency graph, a cache, stable references, diagnostics and a durable document model. Those latter pieces are Jig's distinctive work, not features that OpenCascade supplies automatically.

An excerpt from Jig's real example shows the relationship between the feature model and geometry:

```javascript
return j.part('box')
  .params({ w: mm(60), d: mm(40), h: mm(30), wall: mm(2) })
  .extrude(
    j.sketch('base', { on: j.plane.XY })
      .rect('outline', 'w', 'd', { center: true }).profiles(),
    'h', { id: 'body' })
  .shell(j.feat('body').endFace(), 'wall',
    { direction: 'in', id: 'shell' });
```

The `body` feature denotes an extrusion, while `j.feat('body').endFace()` refers to the top cap *by its provenance*, not by its current array index. Changing `w` should recompute affected downstream geometry without changing the meaning of that reference.

## 1.4 Invariants: the core idea of quality

A *test oracle* tells us what must remain true. Some oracles come from exact mathematics: the volume of a sharp rectangular prism, the area of a disk, the invariance of volume under rigid motion. Others are structural: a closed orientable solid has appropriately paired boundary uses, and a serialized model should retain units and placement. Others concern continuity: a small dimensional edit should normally preserve intended topology and solver branch until a genuine geometric event occurs.

For sets $A,B$ with finite volume, the inclusion–exclusion identity is

$$
V(A\cup B)+V(A\cap B)=V(A)+V(B).
$$

This gives a **metamorphic test** of a Boolean implementation even when the resulting surface is complicated. Run both `union` and `intersection`, check that each output is valid, then compare the volumes with a tolerance that accounts for the kernel's precision. The identity alone does not prove correctness—a pair of correlated errors could cancel—but it detects many regressions.

A second invariant is translation invariance. For a rigid translation $T$, $V(TA)=V(A)$. If moving a part one kilometer from the origin changes its topology or sketch degrees of freedom, the implementation has a scale or cancellation problem, not a new physical design.

## 1.5 Contracts should be explicit in types and diagnostics

A robust CAD API should distinguish a successful *exact* B-rep operation, a successful *approximate* mesh operation, a recovered operation with altered tolerances, and an unsupported operation. These outcomes should not all be represented by an unqualified `ok: true`.

For example, a result might conceptually carry `value`, `representation`, `tolerance`, `validity`, `warnings` and `provenance`. In Rust, this can become an enum distinguishing `ExactBrep`, `ApproximateMesh`, and structured failure. This is a proposed interface design, not Jig's current API.

The same discipline applies to feature cache entries. A cache hit is correct only when all observable dependencies are unchanged, including geometry, tolerances, build orientation, configuration, material-dependent choices, and any environment that influences generated features.

## 1.6 A worked failure: tangent holes

Jig's project issue notes record a rectangle with a circular hole tangent to its boundary that could build an incorrect solid with more volume than the uncut block. Later changes added a warning, but the underlying construction is still listed as unresolved in the inspected repository state. This is a failure across the **sketch-to-profile-to-B-rep boundary**, not evidence that the elementary formula for the cylinder is inaccurate.

The correct response is to locate the earliest representation where the intended region diverges. If the profile extractor emits separate filled regions when the circle touches the perimeter, fix the planar decomposition or reject the ambiguous profile *before* calling an extrusion routine. Adding more checks to the STEP exporter cannot repair the wrong input semantics.

**Try it.** Open [the pipeline bench](lab:sketch?id=pipeline). Change a parameter and inspect which stages change. The dependency arrows are part of the computational model.

> **Exercise.** Define three independently checkable oracles for a plate with four through holes. Explain which oracle detects a missing hole, which detects a wrong face name, and which detects incorrect export units.

> **Careful.** “OpenCascade succeeded” means an OCCT routine returned a result. It does not by itself prove that the result matches the user's construction intent.

### Deeper study: three independent meanings of correctness

The source-guided extension begins in [[Engineering CAD 23 - Solids as regular sets and representation contracts|chapter 23]]. It separates the mathematical point set, its finite representation, and the implementation that evaluates operations on it. A model can pass a connectivity check yet have self-intersecting coordinates; it can also be geometrically valid while representing the wrong design. Use these distinctions when deciding what a diagnostic or a test actually establishes. [[Engineering CAD 32 - A source-guided implementation course|Chapter 32]] turns the whole subject into four restricted implementation projects with independent acceptance tests.

## Toward a reusable API

```text
Quantity<T>         a value with physical dimensions and a canonical unit
Sketch              geometric entities plus driving constraints
Profile             validated oriented loops with exact curve semantics
Brep                topology and analytic geometry with validity metadata
Feature             typed operation with explicit inputs and provenance
CompileReport       results, diagnostics, graph, decisions and trace
ExportReport        preserved, approximated and discarded properties
```

## Key points

A CAD system contains mathematical and topological representations that must remain consistent. Parametric correctness means preserving design intent under edits, not only producing a closed solid. Unit and volume invariants provide inexpensive independent checks. JigCAD's Rust module handles numerical tasks, while OpenCascade handles most underlying geometric construction. The most important bugs can occur between correct-looking subsystems.

## Further reading

- [OpenCascade technical overview](https://www.occt3d.com/dev/doc/overview/html/index.html) distinguishes modeling data, algorithms and exchange.
- [JigCAD build contract](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BUILD.md) maps the actual worker architecture and result structure.
- [JigCAD issue register](https://github.com/go-go-golems/jig/blob/main/import/jigcad/BOOK-ISSUES.md) documents the motivating geometry defects and which remain open.
- [JigCAD API status](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/KERNEL-API.md) separates working, partial and unsupported features.

---

[[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 02 - Curves, surfaces and rational geometry|Chapter 2. Curves, surfaces and rational geometry →]]
