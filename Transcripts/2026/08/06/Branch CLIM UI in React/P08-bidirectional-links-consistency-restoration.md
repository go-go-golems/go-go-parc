---
title: "P08: Bidirectional Links and Consistency Restoration"
subtitle: "Distinguish identity links, directed transformations, lenses, and peer synchronization"
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
| Project | **P08: Bidirectional Links and Consistency Restoration** |
| Track | Synchronization semantics |
| Suggested team | 1-2 students with bidirectional programming, synchronization, or HCI experience |
| Nominal duration | 9-11 weeks |
| Primary result | A link-policy laboratory making consistency relations, repair direction, partiality, ambiguity, and lens laws explicit. |

## Executive framing

Many UI links are not identity. A table selection may induce a pipeline filter; a chart domain may summarize a richer query; a textual editor and structured form may encode the same concept differently. Equating these ports loses information or creates loops. A better model is a consistency relation with explicit restoration procedures.

This project builds a laboratory for identity sharing, directed derivation, and peer synchronization. Success means ambiguity, partiality, information loss, and conflict are explicit, not that every pair of models can be synchronized automatically.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- Which workbench links are identity, directed, asymmetric lenses, symmetric lenses, or replicated merge?
- Which round-trip laws fit each link?
- How should partial and ambiguous repairs appear to users?
- Can delta updates preserve intent better than replacement?
- How are feedback loops scheduled and stabilized?
- When should the system refuse a link?

## Falsifiable hypotheses

- A first-class link-mode distinction prevents equality mistakes and feedback bugs.
- Partial lenses with typed conflicts are more honest than total functions that guess.
- Delta-aware synchronization preserves selection/filter intent.
- Lens laws are necessary but do not replace conflict and provenance UX.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- Treating all links as lenses.
- Automatic arbitrary reconciliation.
- Using identity quotienting for unequal representations.
- Network replication.
- Assuming classical laws fit lossy domains unchanged.

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

An asymmetric lens has $\operatorname{get}:S\to V$ and $\operatorname{put}:S\times V\to S$, with possible laws

$$\operatorname{get}(\operatorname{put}(s,v))=v\quad\text{and}\quad\operatorname{put}(s,\operatorname{get}(s))=s.$$

Peer synchronization begins with a consistency relation $R\subseteq A\times B$ and restoration functions that establish $R$ or return explicit conflict. The project must define distinct semantics for identity links, directed links, bidirectional laws, and replicated merge structures.

## Minimum API and executable artifact

```ts
type Repair<T> =
  | {kind:"updated";value:T;evidence:RepairEvidence}
  | {kind:"unchanged";value:T}
  | {kind:"conflict";choices:readonly RepairChoice[]}
  | {kind:"invalid";reason:string};
const rowSelectionFilter = symmetricLink({consistent,repairRight,repairLeft,laws:[stability,consistencyRestoration]});
```

Expose `links.check-policy`, `links.propagate`, `links.explain-repair`, `links.simulate-feedback`, and `links.run-laws`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Link taxonomy

Classify at least 20 plausible PBUI links and preserve disputed cases.

### Policy kernel

Implement identity reference, directed, asymmetric-lens, and symmetric-consistency policies with partial outcomes.

### Law harness

Generate law tests with shrinkers and known counterexamples; separate domain equivalence from structural equality.

### Scheduler

Implement deterministic propagation, transactions, loop detection, and stable-state reporting.

### Conflict UI

Prototype automatic choice, ranked choices, explicit resolution, and refusal.

## Required experiments

### Selection-to-filter study

Compare replacement, asymmetric lens, symmetric repair, and delta repair for add/remove/reorder.

### Law versus usability

Create a lawful surprising lens and intuitive law-breaking link; evaluate failures.

### Feedback cycle test

Compose links in cycles and measure convergence, oscillation, and diagnostics.

### Ambiguity policy

Test automatic, ranked, dialog, and refuse policies for many-to-one inverse mappings.

## Proof and validation obligations

- Successful repair establishes consistency.
- Stable consistent states remain unchanged.
- Selected round-trip laws are stated and checked.
- Identity is not two recursive setters.
- Ambiguity and partiality are typed.
- Propagation terminates, stabilizes, or reports bounded failure.
- Information loss appears in evidence.
- Composition does not silently alter scheduling.

## Measurements to report

- Law violations and minimized examples.
- Propagation steps/convergence rate.
- Intent preservation under deltas.
- Conflict resolution success/time/reversal.
- Policy authoring and explanation complexity.

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

Export policy metadata/IDs, inspectable consistency terms where possible, repair schemas, evidence, and law fixtures. Host callbacks are foreign assumptions. P06 owns identity classes; P07 declares compatible ports; P09 schedules link creation; P12 handles replicated state. Consumers rely on typed repair outcomes and declared laws, not hidden propagation order.

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

- Choosing laws after tests.
- Structural equality for semantic equivalence.
- Arbitrary total repair.
- Feedback suppression via mutable flags.
- Calling replicated merge a lens.

## Stretch directions

- Delta/edit lenses.
- Inspectable profunctor optics.
- Mechanize one finite lens.
- Provenance through composed links.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Taxonomy/laws. |
| Weeks 2-3 | Policy kernel/law harness. |
| Week 4 | Scheduler. |
| Weeks 5-6 | Selection/filter experiments. |
| Weeks 7-8 | Conflict UI. |
| Weeks 9-11 | Composition and proof stretch. |

## Selected readings

1. J. Nathan Foster et al. "Combinators for Bidirectional Tree Transformations." TOPLAS 29(3), 2007. https://inria.hal.science/inria-00484971v1/document
2. Martin Hofmann, Benjamin C. Pierce, and Daniel Wagner. "Symmetric Lenses." POPL 2011. https://www.cis.upenn.edu/~bcpierce/papers/symmetric.pdf
3. Michael Johnson and Robert Rosebrugh. "Symmetric Delta Lenses and Spans of Asymmetric Delta Lenses." Journal of Object Technology 16(1), 2017. https://www.jot.fm/issues/issue_2017_01/article2.pdf
4. Matthew Pickering, Jeremy Gibbons, and Nicolas Wu. "Profunctor Optics." 2017. https://arxiv.org/abs/1703.10857

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
