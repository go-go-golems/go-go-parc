---
title: "P10: Algebraic Interaction Programs and Effect Handlers"
subtitle: "Describe choosing, linking, performing, waiting, and cancellation independently of React and concrete stores"
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
| Project | **P10: Algebraic Interaction Programs and Effect Handlers** |
| Track | Interaction programming |
| Suggested team | 1-2 students with functional programming, effects, interpreters, or language tooling experience |
| Nominal duration | 8-10 weeks |
| Primary result | A typed interaction-program language with handlers for browser execution, deterministic simulation, tracing, and static effect analysis. |

## Executive framing

Promises sequence asynchronous work but do not expose which effects may occur, how cancellation scopes resources, how traces replay, or how one program can run in a browser and simulator. Algebraic effects separate requests from handlers that assign operational meaning.

This project tests whether a practical TypeScript authoring style can remain understandable while yielding inspectable effect signatures, deterministic interpreters, and explicit resource scopes.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- What are primitive PBUI effects?
- Should programs use ASTs, free monads, generators, async iterators, or final encodings?
- How are cancellation and cleanup scoped?
- Which equations should handlers preserve?
- Can effect summaries be inferred before execution?
- How do handler failure and resumption interact with P09-like machines?

## Falsifiable hypotheses

- A generator surface can compile to an inspectable program or resumable machine.
- Multiple handlers reveal assumptions hidden by direct Promise calls.
- Scoped resources/cancellation should be primitive constructs.
- A small signature supports useful static analysis despite foreign payloads.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- Unrestricted continuations.
- A general-purpose language.
- Replacing operation authority checks.
- Hiding all machine structure behind monadic notation.
- Unqualified commutativity laws for order-sensitive handlers.

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

Let $\Sigma$ be an effect signature. A program may be represented by the free monad $F_\Sigma A$ generated by returns and effect requests with continuations. A handler interprets it into computation algebra $M$ while preserving return and substitution structure.

A generator surface may hide this construction, but the runtime must retain inspectable requests and resumptions. Define equations for return, sequencing, handler composition, cancellation, and scoped cleanup. Static analysis is another interpreter into an abstract domain of possible sorts, operations, ports, and effects.

## Minimum API and executable artifact

```ts
const linkViews = program(function* ($) {
  const source = yield* $.choose(SourcePortSelector);
  const target = yield* $.choose(TargetPortSelector);
  const authority = yield* $.requireCapability(LinkPorts,{source,target});
  yield* $.scope(function* ($) {
    const preview = yield* $.previewLink({source,target});
    yield* $.confirm(preview.explanation);
    yield* $.connect({source,target,mode:"identity",authority});
  });
});
```

Expose `program.analyze`, `program.run`, `program.simulate`, `program.replay`, and `program.pretty`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Effect signature

Define typed PBUI effects and result/error/cancellation semantics.

### Authoring representation

Compare AST, generators, and final encoding; select an ergonomic surface with inspectable core.

### Handlers

Implement deterministic, browser/mock, denial, trace, and static-summary handlers.

### Resource scopes

Make leases, subscriptions, overlays, and cleanup explicit; inject failures at every suspension.

### Machine lowering

Show how programs become resumable machines and where continuation state lives.

## Required experiments

### Encoding comparison

Implement three workflows in Promise, AST, and generator styles.

### Handler substitution

Run unchanged program against deterministic, browser, denial, timeout, and trace-only handlers.

### Static summary accuracy

Compare predicted effects with executed traces on generated inputs.

### Cancellation fault injection

Cancel/fail at each effect boundary and verify cleanup/terminal outcomes.

## Proof and validation obligations

- Deterministic handler yields deterministic interpretation.
- Every scoped resource releases on success, failure, and cancellation.
- Handler substitution cannot bypass mandatory authority effects.
- Replay reproduces request/response sequence for fixed answers.
- Static summaries overapproximate core effects.
- Foreign continuations are labeled.
- Nested cancellation policy is documented.
- Lowered machine resolves exactly once.

## Measurements to report

- Authoring size/failure-path count.
- Static-summary precision.
- Runtime suspension overhead.
- Cleanup failures under injection.
- Developer comprehension in code review.

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

Export effect signature, program IR or normalized trace, effect summaries, handler contracts, and deterministic fixtures. P09 hosts resumable execution; P03/P05/P06/P08 provide semantic requests; P15 replays with deterministic handlers. Stable composition uses effect IDs and payload schemas, not generator internals.

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

- Generators used as opaque coroutines.
- Handlers swallow denials.
- Assuming effects commute.
- Hidden acquisition in helpers.
- API too advanced for routine workflows.

## Stretch directions

- Proof-relevant handlers.
- Abstract interpretation of cancellation/liveness.
- Resumable server execution.
- Mechanize a tiny signature/handler theorem.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Effect corpus/encoding spike. |
| Weeks 2-3 | Core program/deterministic handler. |
| Week 4 | Browser/mock handlers. |
| Weeks 5-6 | Scopes/cancellation/lowering. |
| Weeks 7-8 | Static analysis/comparison. |
| Weeks 9-10 | Report/formal stretch. |

## Selected readings

1. Gordon Plotkin and Matija Pretnar. "Handlers of Algebraic Effects." ESOP 2009. https://homepages.inf.ed.ac.uk/gdp/publications/Effect_Handlers.pdf
2. Patrick Cousot and Radhia Cousot. "Abstract Interpretation Frameworks." Journal of Logic and Computation 2(4), 1992. https://www.di.ens.fr/~cousot/publications.www/CousotCousot-JLC-n2--3-p103--179-1992.pdf
3. J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." Theoretical Computer Science 249, 2000. https://ir.cwi.nl/pub/48/0048D.pdf

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
