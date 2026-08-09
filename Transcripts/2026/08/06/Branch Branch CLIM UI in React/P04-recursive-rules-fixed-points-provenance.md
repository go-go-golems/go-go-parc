---
title: "P04: Recursive Rules, Fixed Points, and Provenance"
subtitle: "Study semantic closure, stratified negation, convergence, and proof-relevant recursive results"
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
| Project | **P04: Recursive Rules, Fixed Points, and Provenance** |
| Track | Query semantics / formal foundations |
| Suggested team | 1-2 students with logic, databases, order theory, or semantics experience |
| Nominal duration | 9-11 weeks |
| Primary result | A finite relational rule engine with explicit least-fixed-point semantics, provenance, and an optimized evaluator checked against the reference closure. |

## Executive framing

Several PBUI properties are recursive: permission inheritance, linked-view reachability, pipeline ancestry, component containment, and action-table inheritance. Ad hoc graph walks scatter recursion policy through code and make cycles, negation, and explanations difficult to reason about.

This project builds the recursive layer independently of selector syntax. It must clarify when finite iteration is enough, when monotonicity is required, where stratified negation is safe, and what transfinite iteration contributes to metatheory without pretending a finite browser should execute through large ordinals.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- Which PBUI relations genuinely require recursion?
- What positivity or stratification restrictions give predictable least-fixed-point semantics?
- How should deletion and changing facts be represented without hiding nonmonotonicity?
- Can recursive provenance remain finite, useful, and cycle-aware?
- What is the smallest convergence class the API should admit?
- How can semi-naive or differential evaluation be checked against reference closure?

## Falsifiable hypotheses

- Positive finite Datalog-style rules cover most recursive PBUI relations.
- Stratified negation is sufficient for practical exclusions but belongs outside the monotone core.
- Transfinite induction is mainly metatheoretic; executable fixtures should converge in finitely many stages.
- Provenance DAGs with cycle summaries are more useful than expanded proof trees.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- A general theorem prover.
- Unrestricted higher-order recursion.
- Assuming every recursive program terminates.
- Production incremental maintenance.
- Using transfinite language without identifying a lattice and operator.

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

Let $F$ be finite possible ground facts and $L=\mathcal P(F)$ ordered by inclusion. A positive rule set $R$ induces an immediate-consequence operator $T_R:L\to L$. Positivity gives

$$X\subseteq Y\implies T_R(X)\subseteq T_R(Y).$$

The intended closure is the least fixed point

$$\mu T_R=\bigcap\{X\mid T_R(X)\subseteq X\}.$$

For finite $F$, iteration from $\varnothing$ stabilizes finitely. The report should still explain the ordinal construction

$$X_0=\bot,\quad X_{\alpha+1}=T_R(X_\alpha),\quad X_\lambda=\bigvee_{\beta<\lambda}X_\beta.$$

Provenance may use a semiring or proof algebra, but must state whether it represents all, one, minimal, or cyclicly summarized derivations.

## Minimum API and executable artifact

```ts
const Connected = derivedRelation("Connected", [View, View]);
rules([
  rule(Connected(x,y)).when(Link(x,y)),
  rule(Connected(x,z)).when(Connected(x,y), Link(y,z)),
]);
const result = engine.close(baseFacts,{provenance:"dag",maxStages:10_000});
```

Expose `rules.check`, `rules.close`, `rules.derive`, `rules.explain`, `rules.stages`, and `rules.compare-evaluators`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Rule kernel

Define typed relation symbols, variables, positive rule bodies, and a direct stage evaluator.

### Convergence analysis

Implement finite-domain bounds, cycle diagnostics, and explicit budget/nonconvergence outcomes.

### Stratified layer

Add stratified negation with a dependency checker and compare it with explicit positive revoked/hidden relations.

### Provenance

Implement at least two representations and explanations for connectivity or inherited authority.

### Optimized evaluator

Implement semi-naive evaluation and differential-test it against stage semantics.

## Required experiments

### Recursive corpus

Model connectivity, permission inheritance, component ancestry, and pipeline reachability.

### Stage-growth study

Generate chains, diamonds, dense components, and cycles; record stages, facts, and provenance growth.

### Negation failures

Construct unstratified examples and demonstrate ambiguity or nonmonotonicity.

### Provenance usability

Compare proof trees, DAGs, and path summaries for developer diagnosis.

## Proof and validation obligations

- The positive consequence operator is monotone.
- Reference closure is a fixed point containing base facts.
- Finite stages either add a fact or terminate.
- Semi-naive and reference closures are extensionally equal.
- Every derived fact has valid provenance.
- Negative dependency cycles are rejected.
- Rule insertion order does not change extensional results.
- Budget exhaustion is not logical falsehood.

## Measurements to report

- Stages and facts by graph family.
- Reference versus semi-naive time and allocation.
- Provenance size and explanation latency.
- Positive/stratified corpus coverage.
- Diagnosis accuracy by provenance format.

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

Export typed relation declarations, checked rule modules, closure snapshots, stage traces, and provenance DAGs. P03 consumes closure as extensional facts; P11 compares incremental results; P14 receives a golden finite rule corpus. Consumers may not depend on worklist order or internal fact IDs.

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

- Worklist algorithm without denotation.
- Treating budget exhaustion as empty result.
- Negation through foreign callbacks while claiming monotonicity.
- Infinite/exponential proof-tree expansion.
- Invoking ordinals without a concrete closure operator.

## Stretch directions

- Provenance semirings for derivation costs.
- Formalize positive fixed-point soundness.
- Well-founded semantics as a separate extension.
- Infer finite-domain convergence bounds.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Relation corpus and semantics. |
| Weeks 2-3 | Reference fixed point. |
| Week 4 | Stratification and failures. |
| Weeks 5-6 | Provenance study. |
| Weeks 7-8 | Semi-naive evaluator. |
| Weeks 9-11 | Formalization and report. |

## Selected readings

1. Alfred Tarski. "A Lattice-Theoretical Fixpoint Theorem and Its Applications." Pacific Journal of Mathematics 5(2), 1955. https://msp.org/pjm/1955/5-2/pjm-v5-n2-p11-s.pdf
2. Michael Arntzenius and Neelakantan R. Krishnaswami. "Datafun: A Functional Datalog." ICFP 2016. https://www.rntz.net/files/datafun.pdf
3. Todd J. Green, Grigoris Karvounarakis, and Val Tannen. "Provenance Semirings." PODS 2007. https://web.cs.ucdavis.edu/~green/papers/pods07.pdf

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
