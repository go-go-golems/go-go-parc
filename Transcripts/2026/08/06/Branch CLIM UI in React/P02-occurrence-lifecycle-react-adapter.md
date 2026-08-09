---
title: "P02: Occurrence Semantics and the Concurrent React Adapter"
subtitle: "Make mounted denotations explicit under speculation, hydration, virtualization, and stale events"
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
| Project | **P02: Occurrence Semantics and the Concurrent React Adapter** |
| Track | Semantic foundations / runtime boundary |
| Suggested team | 1-2 students comfortable with React internals and operational semantics |
| Nominal duration | 8-10 weeks |
| Primary result | A renderer-independent occurrence model plus a React adapter whose committed registrations refine that model. |

## Executive framing

A semantic subject may have many visual occurrences, and a React render may construct trees that never commit. A PBUI fails if it registers semantics during speculative render, keeps retired nodes selectable, or treats virtualized absence as proof that a subject does not exist.

This project defines occurrence identity, denotation, visibility, addressability, and lifecycle independently of React, then treats React as an implementation that must refine the abstract lifecycle. The core result is a precise rule for when an occurrence can witness selection and when an event must be revalidated.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- What is the difference among rendered, committed, visible, addressable, and selectable?
- How should occurrence identity behave across remounting, reordering, hydration, and hidden trees?
- Can registration be commit-causal without undocumented React timing?
- How should stale pointer and keyboard events be rejected and explained?
- What does virtualization mean for occurrence-required selectors?
- Can the adapter be tested against an abstract scheduler?

## Falsifiable hypotheses

- A lifecycle of absent, speculative, committed, and retired is sufficient for core safety, with visibility separate.
- Occurrence IDs must differ from React keys and include a generation or lease.
- Activation-time revalidation is required even if sensitivity was previously correct.
- A small renderer contract can support React, server rendering, and non-DOM renderers.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- Reimplementing React reconciliation.
- Defining subject identity.
- Designing the selector language.
- Making unmounted virtualized subjects occurrence-selectable.
- Premature registry optimization.

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

Let $O$ be occurrence identities and $S$ subjects. A denotation relation $\operatorname{denotes}\subseteq O\times S$ associates an occurrence with a subject. Lifecycle is a labeled transition system

$$\textsf{Absent}\to\textsf{Speculative}\to\textsf{Committed}(e)\to\textsf{Retired}.$$

Visibility, focusability, and hit-testability are observations, not lifecycle states. An activation carrying occurrence $o$ and generation $e$ is valid only when

$$\operatorname{currentEpoch}(o)=e\land\operatorname{committed}(o)\land\operatorname{denotes}(o,s).$$

The React adapter is evaluated as a refinement mapping from renderer traces to this abstract machine. Abandoned renders must map to no committed semantic resource.

## Minimum API and executable artifact

```ts
interface OccurrenceRef { occurrenceId: string; generation: number }
interface OccurrenceRecord {
  ref: OccurrenceRef; subject: SubjectRef; form: string; viewId: string;
  committed: boolean; visible: boolean; focusable: boolean;
}
interface OccurrenceRegistry {
  commit(record: Omit<OccurrenceRecord,"committed">): Lease;
  retire(ref: OccurrenceRef): void;
  snapshot(): readonly OccurrenceRecord[];
  revalidate(ref: OccurrenceRef, expected: SubjectRef): Validation;
}
function useSemanticOccurrence(spec: OccurrenceSpec): DomBinding;
```

The demo includes Strict Mode, virtualization, delayed state, hydration where feasible, and stale-click replay.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Abstract lifecycle

Define states, epochs, leases, denotation, visibility, and revalidation without React.

### React adapter

Implement commit-time registration and cleanup; test Strict Mode, remounts, transitions, Suspense-like delay, and hydration.

### Adversarial scheduler

Interleave render proposals, commits, retirements, and events to generate counterexamples.

### Virtualization semantics

Demonstrate subject existence, registered occurrence, visible occurrence, and mounted-required selection as separate facts.

### Accessible activation

Produce one semantic activation path for keyboard and pointer and test ARIA/focus consistency.

## Required experiments

### Render-time versus commit-time registration

Force abandoned renders and compare ghost occurrences and stale selections.

### Generation strategy

Compare stable IDs, React keys, monotone generations, and lease tokens under rapid remount.

### Virtualized selection

Evaluate mounted, scrolled-out, remounted, and filtered-away candidates.

### Stale event race

Queue activation, retire or retarget, then deliver; require typed rejection and evidence.

## Proof and validation obligations

- Speculative render creates no committed occurrence.
- Lease retirement is idempotent.
- Stale generation cannot activate.
- One subject may have many occurrences.
- React key reuse cannot inherit old denotation.
- Keyboard and pointer share revalidation.
- Snapshots are transactionally coherent.
- Unmounting one occurrence does not retire siblings.

## Measurements to report

- Ghost/stale count under generated traces.
- Registration churn per commit.
- Selection latency at 10, 1,000, and 100,000 occurrences.
- Retained memory after mount cycles.
- Keyboard completion and focus defects.

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

Export immutable occurrence snapshots, deltas, leases, and activation revalidation. Selectors may consume snapshots as facts but may not inspect React hooks or DOM nodes. State whether visibility and geometry are authoritative, advisory, or unavailable in non-browser interpreters.

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

- Registering in render because simple tests pass.
- Equating visibility with existence.
- Assuming undocumented cleanup timing.
- Using React key as global occurrence identity.
- Testing only final DOM snapshots.

## Stretch directions

- Composite occurrences with semantic subregions.
- A second non-React renderer.
- TLA+ or Lean lifecycle refinement.
- Safe semantic annotations for SSR/hydration.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Lifecycle and adversarial examples. |
| Weeks 2-3 | Registry and React adapter. |
| Week 4 | Adversarial scheduler. |
| Weeks 5-6 | Virtualization, stale events, accessibility. |
| Weeks 7-8 | Measurement and report. |
| Weeks 9-10 | Optional refinement proof. |

## Selected readings

1. Neelakantan R. Krishnaswami and Nick Benton. "A Semantic Model for Graphical User Interfaces." ICFP 2011. https://www.cl.cam.ac.uk/~nk480/
2. Patrick Bahr, Christian Graulund, and Rasmus Ejlers Møgelberg. "Simply RaTT." 2019. https://arxiv.org/abs/1903.05879
3. J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." Theoretical Computer Science 249, 2000. https://ir.cwi.nl/pub/48/0048D.pdf

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
