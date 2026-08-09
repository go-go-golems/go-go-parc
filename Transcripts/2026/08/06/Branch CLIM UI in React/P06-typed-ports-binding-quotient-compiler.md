---
title: "P06: Typed Ports and the Binding Quotient Compiler"
subtitle: "Give the PortBindingResolverRegistry a precise quotient, coequalizer, and runtime projection semantics"
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
| Project | **P06: Typed Ports and the Binding Quotient Compiler** |
| Track | Open systems / wiring |
| Suggested team | 1-2 students with category theory, type systems, graph algorithms, or formal methods experience |
| Nominal duration | 9-11 weeks |
| Primary result | A typed wiring compiler that turns identity-link equations into canonical binding classes and proves linked ports observe one runtime resource. |

## Executive framing

"Link these views" is underspecified. For an identity link, distinct local port occurrences are declared to denote one global binding. In finite sets this is a quotient; more generally it is the coequalizer of endpoint maps. The runtime then interprets each quotient class as a shared cell or resource.

This project gives that statement executable content in a small `PortBindingResolverRegistry` independent of union-find, persistent IDs, React, and Redux. It must confront dynamic unlinking, type compatibility, provenance, topology edits, and the fact that a quotient has no canonical inverse.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- What precisely are port occurrence, contract, identity link, binding class, and projection?
- Which contract fields must match definitionally for identity linking?
- How can persistence be stable while insertion order is irrelevant?
- What universal property is useful to downstream interpreters?
- How should unlink allocate and initialize new bindings?
- Can dynamic recompilation preserve unaffected resources?
- Where does coequalizer semantics stop and synchronization policy begin?

## Falsifiable hypotheses

- Identity links should compile to a typed equivalence relation rather than pairwise callbacks.
- Union-find can refine quotient semantics while external binding IDs are assigned separately.
- Universal factorization gives a useful plugin/runtime boundary.
- Unlinking needs provenance and explicit initialization because quotienting is not reversible.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- Transformed or bidirectional mappings as identity.
- Whole component composition.
- Claiming quotienting defines scheduling, ownership, or concurrency.
- Raw TypeScript payload equality as semantic compatibility.
- A production distributed topology service.

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

For contract $\tau$, let $P_\tau$ be local port occurrences and $R_\tau$ link declarations with endpoint maps

$$s_\tau,t_\tau:R_\tau\rightrightarrows P_\tau.$$

The compiler forms a coequalizer $q_\tau:P_\tau\to Q_\tau$ satisfying $q_\tau\circ s_\tau=q_\tau\circ t_\tau$. In finite sets, $Q_\tau$ is the quotient by the generated equivalence relation. A runtime interpretation

$$v_\tau:Q_\tau\to\operatorname{Resource}(\tau)$$

gives each local port observation $v_\tau\circ q_\tau$. Equal projections therefore observe the same generated resource. The report must state the chosen category or typed fiber and keep authority, temporal mode, and multiplicity in compatibility checks.

## Minimum API and executable artifact

```ts
const doc = portContract<DocumentId>({semantic:"primary-document",mode:"read-write-cell",authority:"workspace",multiplicity:"one"});
const plan = bindings()
  .declare(chart.port("document",doc))
  .declare(pipeline.port("document",doc))
  .identify(chart.port("document"),pipeline.port("document"))
  .compile();
plan.bindingOf(chart.port("document"));
plan.allocate(interpreter);
```

Expose `bindings.check-link`, `bindings.compile`, `bindings.explain`, `bindings.edit`, and `bindings.allocate`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Typed contracts

Define semantic tag, payload sort, mode, authority, multiplicity, update algebra, and lifetime; identify identity-compatible fields.

### Reference quotient

Implement transparent equivalence closure with classes, projections, and link provenance.

### Optimized compiler

Implement union-find or another structure and differential-test it against the reference partition.

### Runtime projection

Allocate one shared cell per class and typed projections to widgets.

### Dynamic topology

Specify link, merge, unlink, component removal, reload, and value initialization.

### Mechanized core

Formalize relation-to-quotient and linked-observation theorems in Lean/Agda/Coq/Isabelle or equivalent checked model.

## Required experiments

### Algorithm equivalence

Generate typed graphs with duplicates, cycles, disconnected parts, and random insertion order.

### Compatibility matrix

Use same payload types with different semantics, authority, and temporal modes; assess diagnostics.

### Unlink policies

Compare copy-current, reset, history restore, and user choice; show none follows from quotient alone.

### Binding stability

Edit unrelated topology and measure resource/subscription churn under external-ID strategies.

### Widget projection demo

Render chart, pipeline, and table from projected bindings while displaying classes and values.

## Proof and validation obligations

- Every declared port belongs to one class.
- Every accepted identity link has compatible contracts.
- Linked endpoints project equally.
- Partition is independent of link order and duplicates.
- Every link-respecting interpretation factors through the quotient in the chosen category.
- All projections of a class observe one allocated resource.
- Unlinking has explicit initialization and does not claim inversion.
- Persistence preserves the relation up to ID renaming.
- Removing one port preserves a nonempty class.
- Type erasure cannot merge incompatible contracts.

## Measurements to report

- Compile/edit latency by graph size.
- Resource/subscription churn.
- Serialized topology size/stability.
- Compatibility diagnosis time.
- Formal proof coverage and assumptions.

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

Export serializable contracts, port graph, link declarations, classes, projection map, provenance, and allocation interface. P07 can use this as identity-wiring backend; P08 must keep lenses separate; P12 replicates declarations and recompiles; P14 receives the formal kernel. Consumers may not depend on a union-find representative as persistent ID.

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

- Calling union-find the semantics.
- Payload equality as full compatibility.
- Claiming atomic writes from shared classes alone.
- Deleting equivalence edges without preserving declarations.
- External IDs from unstable representatives.
- Unsynchronized component shadow values.

## Stretch directions

- Prove incremental recompilation.
- Generalize to typed graphs/categories.
- Generate checkable binding-plan certificates.
- Explore linearity/ownership for write ports.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Contract taxonomy and categorical statement. |
| Weeks 2-3 | Reference quotient. |
| Week 4 | Optimized compiler. |
| Weeks 5-6 | Projection and widget demo. |
| Week 7 | Dynamic topology. |
| Weeks 8-9 | Mechanized theorem. |
| Weeks 10-11 | Experiments and report. |

## Selected readings

1. John C. Baez and Kenny Courser. "Structured Cospans." Theory and Applications of Categories 35, 2020. https://math.ucr.edu/home/baez/structured.pdf
2. Joseph A. Goguen and Rod M. Burstall. "Institutions: Abstract Model Theory for Specification and Programming." JACM 39(1), 1992. https://cseweb.ucsd.edu/~goguen/pps/ins.pdf
3. J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." Theoretical Computer Science 249, 2000. https://ir.cwi.nl/pub/48/0048D.pdf

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
