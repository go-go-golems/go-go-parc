---
title: "P13: Explanation, Accessibility, and Proof-Relevant Interaction"
subtitle: "Project one semantic interaction state into pointer, keyboard, screen-reader, textual, and diagnostic experiences"
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
| Project | **P13: Explanation, Accessibility, and Proof-Relevant Interaction** |
| Track | Human factors / semantics |
| Suggested team | 1-2 students with HCI, accessibility, information visualization, or explainable-systems experience |
| Nominal duration | 8-10 weeks |
| Primary result | A renderer-neutral explanation model and accessible interaction laboratory for selection, authority, staleness, linking, conflicts, and machine phase. |

## Executive framing

A proof-relevant semantic kernel is useful only when users and developers can understand enough of its results to act. Color highlights alone cannot explain why a candidate is selectable, why an operation disappeared, which views will change after a link, or whether an unavailable result is false, unknown, pending, stale, unauthorized, ambiguous, or unsupported.

This project treats explanation and accessibility as semantic projections rather than decorations added after implementation. One normalized interaction state should support pointer, keyboard, screen reader, command palette, developer inspector, and trace report without giving each modality a different truth. The work must also identify where complete explanations are impossible or harmful and how to communicate bounded, partial, ranked, or foreign evidence honestly.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- What is the smallest renderer-neutral model of candidate, rejection, authority, staleness, binding, lens conflict, machine phase, and provenance?
- How should positive evidence and negative explanations differ?
- Can pointer, keyboard, screen-reader, and textual projections preserve the same semantic availability and commit validation?
- How should the UI distinguish false, unknown, pending, stale, unauthorized, ambiguous, and unsupported?
- What level of provenance is useful to end users versus developers?
- How can linked-view impact and conflict repair be previewed without overwhelming users?
- How should candidate ranking be explained without presenting rank as truth or certainty?

## Falsifiable hypotheses

- A normalized explanation tree with stable evidence IDs can support several modalities while preserving semantic consistency.
- Users recover from stale and ambiguous interactions more reliably when the system states the failed obligation and next action.
- Linked-state changes need an explicit affected-view preview; iconography alone is insufficient.
- Complete provenance is usually too detailed; layered summaries with drill-down are more effective.
- Accessibility testing will expose semantic inconsistencies that pointer-only testing misses.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- Automatically generating perfect natural-language explanations.
- Treating ARIA attributes as the entire accessibility problem.
- Claiming rejection explanations are complete when only one failing branch is known.
- A broad demographic study.
- Changing semantic truth in the renderer.

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

Let an evaluator or machine produce an outcome $o$ together with evidence, missing obligations, or conflict information. Define a total projection

$$\operatorname{explain}:\operatorname{Outcome}\to\operatorname{ExplanationModel}.$$

The model should distinguish status from presentation and include stable references to semantic evidence. Each modality $m$ is an interpretation

$$\rho_m:\operatorname{ExplanationModel}\to\operatorname{RenderedExperience}_m.$$

State a cross-modality consistency relation: modalities may omit detail appropriate to their channel, but they must not disagree on candidate membership, enabled operation, authority requirement, current phase, or commit result. Where a negative explanation is incomplete, the model carries completeness metadata rather than implying a proof of nonexistence.

## Minimum API and executable artifact

```ts
interface ExplanationModel {
  id: string;
  status: "available" | "unavailable" | "unknown" | "pending" |
          "stale" | "unauthorized" | "ambiguous" | "unsupported";
  summary: MessageToken;
  obligations: readonly ExplanationNode[];
  evidence: readonly EvidenceRef[];
  affectedSubjects: readonly SubjectRef[];
  affectedViews: readonly ComponentRef[];
  remedies: readonly Remedy[];
  completeness: "complete" | "partial" | "foreign";
}
interface SemanticInteractionState {
  request?: SelectionRequest;
  candidates: readonly CandidateState[];
  phase: MachinePhase;
  focusedOccurrence?: OccurrenceRef;
  explanationFor(id: string): ExplanationModel;
}
```

Expose `explanation.project`, `explanation.render-text`, `explanation.render-a11y`, `explanation.inspect`, and `explanation.compare-modalities`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Explanation schema

Define statuses, obligations, evidence references, affected resources, remedies, completeness, severity, and localization tokens.

### Semantic projections

Build pointer, keyboard/listbox, screen-reader/live-region, command-palette, plain-text, and developer-inspector projections.

### Accessible interaction lab

Implement all six shared traces with focus management, reading order, reduced motion, non-color cues, and commit-time revalidation.

### Explanation variants

Compare terse, layered, provenance-first, remedy-first, and causal-timeline forms without changing underlying semantics.

### User evaluation

Conduct a small preregistered formative study or structured expert review; report limitations and qualitative counterexamples.

## Required experiments

### Selectable-state comprehension

Ask users to identify selectable and rejected occurrences and explain the decisive obligation.

### Link visibility

Compare chain icon only, shared-label indicator, affected-view preview, and persistent topology inspector.

### Commit rejection recovery

Revoke authority or stale an occurrence after rendering and measure recovery under generic versus proof-relevant messages.

### Modality parity

Replay identical traces by pointer, keyboard, screen reader, and command palette; compare semantic event logs.

### Ranking transparency

Show equal-truth candidates with different ranking reasons; test whether users mistake ordering for eligibility or confidence.

## Proof and validation obligations

- No semantically relevant state is conveyed by color alone.
- Pointer and keyboard activation pass through the same semantic commit validation.
- A screen reader can discover the active request, candidate count, candidate state, phase, and final result.
- False, unknown, pending, stale, unauthorized, ambiguous, and unsupported are distinct machine-readable states.
- A linked change can enumerate affected views before or immediately after commit.
- Evidence references are stable enough to correlate UI, logs, and replay.
- Ranking metadata is separate from truth and authority.
- Incomplete and foreign explanations are labeled.
- Focus is restored or moved according to a documented transition policy.
- Study claims are bounded by participant/sample/method limitations.

## Measurements to report

- Task completion and error rate.
- Time to identify cause and remedy.
- Semantic-event parity across modalities.
- Accessibility audit findings.
- Explanation depth and interaction count.
- User confidence versus actual correctness.

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

Export a versioned explanation schema, message-token catalog, modality-neutral interaction snapshot, rendered textual fixtures, semantic event traces, and study instruments. P03/P04 supply selection evidence; P05 authority; P06/P08 topology and conflicts; P09 machine phase; P12 causal history. P15 compares event logs. This project must not reach into subsystem internals when stable evidence references suffice.

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

- Inventing friendly prose unsupported by evidence.
- Making disabled controls undiscoverable.
- Separate pointer and keyboard code paths.
- Overwhelming users with proof trees.
- Using ranking as a confidence score.
- Overclaiming from a small convenience sample.

## Stretch directions

- Verified cross-modality state projection for a finite core.
- Localization stress test including bidirectional text.
- Sonification or haptic projection.
- Adaptive explanation depth without changing semantic status.
- Screen-reader-accessible topology graph.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Status/explanation inventory. |
| Weeks 2-3 | Schema and text/inspector projections. |
| Weeks 4-5 | Accessible interaction lab. |
| Week 6 | Modality parity and audits. |
| Weeks 7-8 | User study. |
| Weeks 9-10 | Refinement and report. |

## Selected readings

1. Todd J. Green, Grigoris Karvounarakis, and Val Tannen. "Provenance Semirings." PODS 2007. https://web.cs.ucdavis.edu/~green/papers/pods07.pdf
2. Neelakantan R. Krishnaswami and Nick Benton. "A Semantic Model for Graphical User Interfaces." ICFP 2011. https://www.cl.cam.ac.uk/~nk480/
3. David Harel. "Statecharts: A Visual Formalism for Complex Systems." Science of Computer Programming 8, 1987. https://www.state-machine.com/doc/Harel87.pdf

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
