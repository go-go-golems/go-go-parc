---
title: "P09: Coalgebraic Interaction Machines"
subtitle: "Represent long-running interaction by explicit observations, transitions, effects, and behavioral equivalence"
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
| Project | **P09: Coalgebraic Interaction Machines** |
| Track | Interaction semantics |
| Suggested team | 1-2 students with semantics, state machines, model checking, or UI architecture experience |
| Nominal duration | 8-10 weeks |
| Primary result | A small machine IR and runtime for PBUI workflows, with checks for safety, cancellation, resolution, and behavioral equivalence. |

## Executive framing

Workflows such as "choose source, choose target, validate, confirm, commit, or cancel" are ongoing processes. Nested callbacks and promises hide intermediate states, cancellation paths, stale resources, and liveness assumptions.

A coalgebraic view describes current observations and future transitions. Statecharts offer authoring syntax; labeled transition systems, bisimulation, and temporal properties support analysis. This project seeks the smallest useful machine model without becoming a general workflow engine.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- Which observations belong to the semantic machine versus rendering?
- Are effects transition outputs, handler commands, or state?
- How are cancellation, disposal, timeout, and nesting scoped?
- What fairness assumptions underlie liveness?
- Can callback and machine implementations be observationally compared?
- How do changing occurrence, authority, and binding snapshots enter the model?

## Falsifiable hypotheses

- A deterministic Mealy-style core with typed effects covers most local workflows.
- Hierarchical statecharts aid authoring; a flat normalized LTS aids checking.
- Bisimulation or trace equivalence can validate refactoring.
- Cancellation and stale rejection become easier to test as ordinary transitions.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- A business-process engine.
- All application state inside the machine.
- Liveness without fairness assumptions.
- Hidden side effects in transitions.
- Replacing effect handlers.

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

A deterministic Moore machine is a coalgebra $\gamma:X\to O\times X^I$. An effectful Mealy form is

$$\delta:X\times I\to X\times E^*.$$

Define a labeled transition system. A relation $R\subseteq X\times Y$ is a bisimulation when related states have equivalent observations and transition to related states for corresponding events. Safety can be proved over reachable transitions; liveness requires explicit delivery, completion, and fairness assumptions.

## Minimum API and executable artifact

```ts
const LinkMachine = machine({
  initial:{state:"idle"},
  states:{
    idle:on("start","choosingSource"),
    choosingSource:{output:{request:SourcePortSelector},on:{selected:"choosingTarget",cancel:"cancelled"}},
    choosingTarget:{}, committing:{}, done:{terminal:true}, cancelled:{terminal:true}, failed:{terminal:true}
  }
});
```

Expose `machine.check`, `machine.initial`, `machine.observe`, `machine.step`, `machine.explore`, `machine.replay`, and `machine.compare`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Machine kernel

Define state, event, observation, typed effects, terminality, and model snapshots with pure transitions.

### Authoring syntax

Compile a statechart-like syntax to a normalized table with explicit priority.

### Explorer/checker

Find dead states, double resolution, unhandled events, and selected temporal violations.

### Runtime/inspector

Run with handlers and display state, enabled events, effects, and trace.

### Callback comparison

Implement one workflow as callbacks and machine; compare failure injection and refactoring.

## Required experiments

### Workflow corpus

Encode selection, port linking, validated drag/drop, command arguments, and confirmable operation.

### Cancellation matrix

Inject cancel, disposal, timeout, and staleness at every state.

### Model exploration

Generate finite environments and search for deadlock, double resolution, and unreachable states.

### Behavioral comparison

Refactor state representation and test an explicit trace/bisimulation relation.

### Phase visibility

Compare explicit phase, spinner, and no phase in user tasks.

## Proof and validation obligations

- Every state/event has transition, explicit ignore, or typed rejection.
- Terminal sessions resolve at most once.
- Cancellation is idempotent and releases resources.
- Disposed state emits no new user-visible effects.
- Stale resources are revalidated before commit.
- Replay is deterministic for fixed event/model traces.
- Liveness claims list fairness assumptions.
- Normalization preserves authoring semantics.

## Measurements to report

- State/transition count.
- Counterexamples found by exploration.
- Replay/comparison cost.
- Complexity versus callbacks.
- User understanding of phase/cancellation.

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

Export normalized machine IR, event/observation/effect schemas, traces, model abstractions, and checker results. P10 supplies handlers; P02 activations; P03 selection requests; P05 operation intents; P06/P08 link effects. Guarantees such as determinism and terminality are relied upon only when declared and checked.

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

- Async effects in transition functions.
- Coinductive claims from finite samples.
- Hidden environment globals.
- Ambiguous statechart priority.
- Undocumented ignored events.

## Stretch directions

- Finite bisimulation proof.
- SCXML compilation.
- Hierarchical/parallel states with precise priority.
- Abstract interpretation of possible effects and requested sorts.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Workflow corpus/semantics. |
| Weeks 2-3 | Kernel/syntax. |
| Week 4 | Explorer. |
| Weeks 5-6 | Runtime/cancellation. |
| Weeks 7-8 | Callback/user comparison. |
| Weeks 9-10 | Equivalence stretch. |

## Selected readings

1. J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." Theoretical Computer Science 249, 2000. https://ir.cwi.nl/pub/48/0048D.pdf
2. David Harel. "Statecharts: A Visual Formalism for Complex Systems." Science of Computer Programming 8, 1987. https://www.state-machine.com/doc/Harel87.pdf
3. W3C. "State Chart XML (SCXML): State Machine Notation for Control Abstraction." https://www.w3.org/TR/scxml/

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
