---
title: "P03: Inspectable Typed Selectors and Selection Evidence"
subtitle: "Replace opaque acceptance lambdas with a small query language whose results explain themselves"
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
| Project | **P03: Inspectable Typed Selectors and Selection Evidence** |
| Track | Query semantics |
| Suggested team | 1-2 students with programming-languages, database, or type-system experience |
| Nominal duration | 8-10 weeks |
| Primary result | A typed selector AST, reference evaluator, and proof-relevant candidate format with a controlled foreign-predicate boundary. |

## Executive framing

Arbitrary JavaScript predicates are convenient but opaque: dependencies, serialization, optimization, replay, and explanation are unavailable. This project finds the smallest inspectable language that can express practical requests such as "choose an active numeric field from the current document, witnessed by a mounted occurrence."

The aim is not SQL in TypeScript. It is a typed semantic request with a denotation, evidence, a separate ranking policy, and an explicit escape hatch for foreign predicates.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- What core syntax captures practical selection while remaining small enough for structural induction?
- Should occurrence constraints be relations, modal operators, or a separate phase?
- How do parameters, context, and authority facts enter the query?
- What evidence explains acceptance and rejection?
- How should unknown or pending differ from false?
- Which optimizations preserve evidence and deterministic ranking?

## Falsifiable hypotheses

- Conjunction, disjunction, typed atoms, equality, bounded negation, existential variables, and occurrence predicates cover most selectors.
- Truth and ranking should be separate.
- Three-valued results are more robust for remote or leased facts.
- Foreign predicates remain usable when dependency, purity, timeout, and explanation assumptions are explicit.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- Recursive rules.
- A full cost-based optimizer.
- Proving arbitrary JavaScript.
- The full operation/capability system.
- Serializing foreign closures.

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

A typing judgment $\Gamma\vdash q:\operatorname{Query}(s)$ states that $q$ returns subjects of sort $s$. Its proof-relevant denotation is

$$\llbracket q\rrbracket_{D,\rho}\subseteq\operatorname{SubjectRef}(s)\times\operatorname{Evidence}.$$

Evidence records successful facts, equalities, occurrence witnesses, and foreign assumptions. Negative explanations may be partial and must be labeled as such. If three-valued semantics is used, define an information order such as $\textsf{unknown}\sqsubseteq\textsf{true}$ and $\textsf{unknown}\sqsubseteq\textsf{false}$ while keeping truth order separate. Negation must not silently treat unknown as false.

## Minimum API and executable artifact

```ts
const selectableField = selector(Field, q => q.and(
  q.rel(BelongsTo, q.result, q.param("document")),
  q.rel(Numeric, q.result),
  q.not(q.rel(Internal, q.result)),
  q.exists(Occurrence, o => q.and(q.rel(Denotes,o,q.result), q.rel(Committed,o)))
));
const candidates = evaluator.evaluate(selectableField,{document:docA});
```

Expose `selector.typecheck`, `selector.evaluate`, `selector.explain`, `selector.explain-rejection`, and `selector.dependencies`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Core language

Define a typed AST and builder; encode convenience forms as derived syntax.

### Reference semantics

Evaluate finite facts and occurrence snapshots while preserving derivations.

### Foreign boundary

Represent dependency, purity, timeout, cache, and explanation claims as assumptions.

### Ranking layer

Order candidates by a separate stable policy; test locality, proof cost, and authority strength.

### Explanation UI

Show why one occurrence is selectable, why another is not, and where evidence is foreign.

## Required experiments

### Coverage study

Encode at least 25 realistic selectors and classify foreign or recursive needs.

### Lambda comparison

Compare opaque callbacks for dependency extraction, replay, explanation, and optimization.

### Evidence cost

Measure no evidence, minimal evidence, and complete derivations.

### Three-valued interaction

Compare disabled, optimistic, and explicit pending behavior for remote facts.

## Proof and validation obligations

- Well-typed selectors return only their declared sort.
- Every accepted candidate has a valid derivation or labeled foreign assumption.
- Core evaluation is deterministic for fixed inputs and ranking.
- Dependency extraction is sound.
- Normalization preserves denotation.
- Ranking does not alter truth.
- Foreign timeout/exception is typed.
- Commit revalidation detects revision change.

## Measurements to report

- Core-language coverage.
- Evaluation latency by fact/occurrence count.
- Evidence size and rendering time.
- Dependency precision and false invalidation.
- User comprehension of false/unknown/pending.

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

Export the versioned AST, type environment, dependency set, candidate/evidence schema, pure evaluator, selector corpus, and golden derivations. Foreign nodes serialize as stable IDs plus assumption metadata, never source strings. P04, P11, P14, and P15 should be able to implement independent evaluators.

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

- Unprincipled AST growth.
- Claiming complete rejection explanations from one failed branch.
- Mixing ranking into truth.
- Treating foreign exceptions as false.
- Executing host control flow in a builder that should construct syntax.

## Stretch directions

- Certified normalization.
- Modal operators for mounted/visible/local/authoritative facts.
- Interactive query holes.
- Compile a subset to SQL or Datalog.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Selector corpus and syntax. |
| Weeks 2-3 | Typed AST and evaluator. |
| Week 4 | Evidence and foreign boundary. |
| Weeks 5-6 | Ranking, explanations, generated tests. |
| Weeks 7-8 | Coverage and three-valued study. |
| Weeks 9-10 | Optional certification. |

## Selected readings

1. Michael Arntzenius and Neelakantan R. Krishnaswami. "Datafun: A Functional Datalog." ICFP 2016. https://www.rntz.net/files/datafun.pdf
2. Todd J. Green, Grigoris Karvounarakis, and Val Tannen. "Provenance Semirings." PODS 2007. https://web.cs.ucdavis.edu/~green/papers/pods07.pdf
3. Patrick Cousot and Radhia Cousot. "Abstract Interpretation Frameworks." Journal of Logic and Computation 2(4), 1992. https://www.di.ens.fr/~cousot/publications.www/CousotCousot-JLC-n2--3-p103--179-1992.pdf

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
