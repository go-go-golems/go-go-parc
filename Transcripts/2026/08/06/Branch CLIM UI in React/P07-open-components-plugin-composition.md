---
title: "P07: Open Components, Plugin Signatures, and Composition"
subtitle: "Specify independently developed UI components by typed boundaries and compose them through explicit wiring"
author: "PBUI Research Program"
date: "2026-08-04"
lang: en-US
documentclass: article
geometry: margin=0.8in
fontsize: 10pt
toc: true
toc-depth: 3
numbersections: true
colorlinks: true
linkcolor: blue
urlcolor: blue
---

# Project brief

| Field | Assignment |
|---|---|
| Project | **P07: Open Components, Plugin Signatures, and Composition** |
| Track | Open systems / modularity |
| Suggested team | 1-2 students with module systems, category theory, architecture, or plugin-platform experience |
| Nominal duration | 9-11 weeks |
| Primary result | A component signature and plugin compiler separating interface gluing from behavior and testing associativity, compatibility, and schema evolution. |

## Executive framing

A component should not import another component's store, actions, or React context to participate in a workbench. It should expose a typed boundary and compose through explicit wiring. Structured cospans and pushouts offer one account of gluing open systems; algebraic specifications and institutions clarify independently named schemas and theories.

This project tests how much of that structure produces practical value in a TypeScript plugin platform. It must distinguish signature composition from runtime behavior and reject the mistake that a pushout automatically solves synchronization.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- What belongs in a component signature: subjects, facts, ports, operations, forms, effects, or all?
- Can composition be associative up to stable isomorphism in a serialized representation?
- How should name collisions and schema versions be diagnosed?
- When is pushout-like gluing appropriate, and when is an adapter required?
- How should a plugin declare authority, time, and update-algebra assumptions?
- Can harnesses be generated from signatures alone?

## Falsifiable hypotheses

- A compact declarative signature supports independent testing and composition better than framework-specific interfaces.
- Pushout-like gluing helps shared boundaries, while schema differences require explicit adapters.
- Composition should be associative up to canonical renaming, not byte-identical output.
- A signature checker reveals hidden architectural coupling before runtime.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- Defining all internal behavior.
- Category terminology without executable mapping.
- Same-named ports as automatically compatible.
- A package manager.
- Replacing binding compilation or link policies.

## Shared laboratory setting

Every project is self-contained, but all teams use the same deliberately small domain so that results can be compared without importing another team's implementation.

The domain is an analytical workbench containing four independently developed components:

- a **source browser** that presents documents and fields;
- a **chart** with a primary-document port and a row-selection port;
- a **pipeline editor** with a primary-document port, a filter port, and an output-document port;
- a **table** with a primary-document port and a row-selection port.

The fixed fixture contains documents `doc-a`, `doc-b`, and deleted tombstone `doc-z`; fields `station`, `temperature`, `pressure`, and `internal_id`; users `analyst`, `admin`, and `viewer`; views `chart-1`, `pipeline-1`, `table-1`, and `browser-1`; multiple occurrences of the same semantic field; immutable copies with different JavaScript references; one stale occurrence; one unauthorized operation; and one deliberately ambiguous bidirectional update.

The mandatory user-visible traces are:

1. **Same subject, different occurrence.** Select `temperature` from either a field chip or a table header and obtain the same semantic subject.
2. **Refined selection.** Ask for a non-internal numeric field owned by the currently selected document.
3. **Identity linking.** Link the chart and pipeline primary-document ports, then switch the document from either component.
4. **Transformed linking.** Translate a table row selection into a pipeline filter and expose ambiguity rather than silently guessing.
5. **Staleness and authority.** Render an action, revoke its authority or retire its occurrence, then attempt to commit it.
6. **Concurrent topology.** On two replicas, link and unlink overlapping groups while offline, then merge.

A team may add fixtures, but it may not remove or weaken these six traces.

## Common artifact boundary

Each submission exposes a deterministic command-line adapter over JSON Lines. It may implement only relevant messages, but unsupported messages return a typed `unsupported` result.

```ts
interface LabEnvelope<T = unknown> {
  protocol: "pbui-research/0.1";
  requestId: string;
  kind: string;
  payload: T;
}

interface LabResult<T = unknown> {
  protocol: "pbui-research/0.1";
  requestId: string;
  status: "ok" | "rejected" | "unsupported" | "error";
  payload?: T;
  explanation?: Explanation;
}
```

This adapter is an experimental seam for replay, comparison, and later substitution. It is not the proposed production API.

## Formal object of study

Model a component with input boundary $I$, internal structure $G$, and output boundary $O$ as a cospan

$$I\longrightarrow G\longleftarrow O.$$

Compatible components glue along shared boundary $B$ using a pushout $G+_B H$. In finite sets or graphs this often means coproduct followed by quotienting the two images of $B$. This is structural composition, not a behavioral synchronization theorem.

A component signature may also be viewed as a theory with schema maps changing notation and models moving contravariantly by reduct. Use this only where it improves versioning or plugin compatibility.

## Minimum API and executable artifact

```ts
const Chart = componentSignature({
  name:"chart", version:"1.0.0",
  imports:[Document,RowSelection], exports:[ChartView,HighlightOperation],
  ports:{document:ioPort(PrimaryDocument),selection:outputPort(RowSelection)},
  assumptions:["workspace-authority","transactional-bindings"]
});
const workspace = composeComponents([instantiate(Chart,"chart-1"),instantiate(Pipeline,"pipeline-1")],wiring);
```

Expose `components.check`, `components.compose`, `components.explain-conflict`, `components.generate-harness`, and `components.serialize`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Signature language

Define imported/exported sorts, relations, ports, operations, forms, effects, assumptions, and versions.

### Structural composition

Implement reference composition with namespaces, canonical renaming, and explicit boundary identifications.

### Compatibility and adapters

Diagnose sort, semantic tag, authority, and version mismatches; require explicit adapters.

### Generated harnesses

Generate mock environments and contract tests from signatures.

### Plugin laboratory

Build independently designed chart, pipeline, and table components and compose in several orders.

## Required experiments

### Associativity study

Compose three components in different parenthesizations and compare canonicalized signatures and plans.

### Name-collision corpus

Compare global names, namespaces, and explicit schema maps for overlapping independent schemas.

### Adapter pressure test

Version document and selection contracts; classify mechanical versus semantic adaptation.

### Independent implementation trial

Give only the signature to another developer and measure successful compatible implementation.

## Proof and validation obligations

- Composition preserves typed boundaries or returns typed conflict.
- Identity composition is neutral up to canonical renaming.
- Supported composition is associative up to explicit isomorphism.
- No name collision resolves silently.
- Adapters declare direction, information loss, and failure.
- Generated harnesses exercise all required imports/ports.
- Serialized workspaces retain provenance.
- Structural composition makes no behavioral guarantee by itself.

## Measurements to report

- Signature size/authoring overhead.
- Checker latency and diagnostic precision.
- Hidden dependencies found.
- Adapter count and human-decision fraction.
- Independent implementation success.

## Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

## Composition capsule

Export signatures, schema maps, adapter declarations, canonical composition results, and generated contract tests. P06 supplies identity bindings; P08 supplies nonidentity link policies; P09 attaches behavior; P15 composes mocks from capsules. Mark definitional equalities, adapter-mediated relations, and unresolved obligations separately.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

## Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

## Baseline acceptance criteria

- The core distinction is explicit in code or proof terms.
- The reference semantics executes at least three shared traces.
- At least five nontrivial laws are tests or formal theorems.
- At least one plausible but incorrect design is shown to fail.
- Errors and conflicts are typed and observable.
- There is no hidden process-global mutable singleton.
- A second team can invoke the artifact through the common adapter.
- Claims over opaque callbacks are explicitly bounded.
- Performance reports include data size, hardware, warm-up, and uncertainty.
- Visual demonstrations are keyboard-operable.

## Risks and failure modes to seek deliberately

- Manifest merely mirrors TypeScript.
- Pushout metaphor with object merge implementation.
- Strict associativity claimed despite unstable names.
- Hidden adapters.
- Plugins reaching around ports into shared stores.

## Stretch directions

- Formalize the fragment as structured cospans.
- Schema migration via Kan-extension-inspired adapters.
- Capability-aware boundaries.
- Generate integration documentation.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Component inventory and signature. |
| Weeks 2-3 | Reference composition. |
| Week 4 | Diagnostics/adapters. |
| Weeks 5-6 | Harnesses and independent plugins. |
| Weeks 7-8 | Associativity/versioning experiments. |
| Weeks 9-11 | Formal account and report. |

## Selected readings

1. John C. Baez and Kenny Courser. "Structured Cospans." Theory and Applications of Categories 35, 2020. https://math.ucr.edu/home/baez/structured.pdf
2. Joseph A. Goguen and Rod M. Burstall. "Institutions: Abstract Model Theory for Specification and Programming." JACM 39(1), 1992. https://cseweb.ucsd.edu/~goguen/pps/ins.pdf
3. Matthew Pickering, Jeremy Gibbons, and Nicolas Wu. "Profunctor Optics." 2017. https://arxiv.org/abs/1703.10857

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
