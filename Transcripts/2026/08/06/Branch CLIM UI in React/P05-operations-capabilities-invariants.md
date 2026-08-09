---
title: "P05: Operations, Capabilities, and Invariant-Preserving Affordances"
subtitle: "Derive visible actions from explicit transition specifications and authority evidence"
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
| Project | **P05: Operations, Capabilities, and Invariant-Preserving Affordances** |
| Track | Operations and authority |
| Suggested team | 1-2 students with security, PL, or transactional-systems experience |
| Nominal duration | 8-10 weeks |
| Primary result | An operation model separating menu affordances from authoritative transitions and making preconditions, effects, and invariants explicit. |

## Executive framing

A menu item is not an operation. It is a visual affordance suggesting an operation may be attempted. Between rendering and activation, state, authority, and revision can change. A robust PBUI therefore needs authoritative operation specifications and commit-time checks, not callbacks captured when a menu opens.

This project studies operation schemas, capability evidence, effect footprints, transactions, typed failures, and invariant preservation. It should expose why an action is offered and why a later commit can still be rejected.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- What belongs in an operation specification versus an affordance?
- How should capability evidence be scoped, leased, and rechecked?
- Can effect footprints support invariant modularity and incremental invalidation?
- How should optimistic UI represent later rejection?
- Which invariants require coordination or authority?
- Can operation composition preserve useful contracts?

## Falsifiable hypotheses

- Affordances should be pure derived data over operation specs, subjects, context, and capability evidence.
- Authoritative handlers must recheck preconditions at commit revision.
- Declared footprints materially improve testing and incremental recomputation.
- Typed rejection outcomes improve recovery compared with exceptions.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- A complete authorization infrastructure.
- Encoding all business logic in a theorem prover.
- UI visibility as authority.
- Cross-replica invariant preservation.
- Coupling operations to React or menus.

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

Model operation $O$ with input $I_O$, precondition $P_O$, transition relation $\tau_O$, postcondition $Q_O$, and effect footprint $E_O$:

$$P_O\subseteq\Sigma\times I_O,\qquad \tau_O\subseteq\Sigma\times I_O\times\Sigma.$$

Capability evidence has the form $e:\operatorname{Can}(p,O,i,\sigma,r)$ for principal, input, state, and revision/lease. It supports offering an affordance but does not guarantee future success. For invariant $Inv$:

$$Inv(\sigma)\land P_O(\sigma,i)\land\tau_O(\sigma,i,\sigma')\implies Inv(\sigma').$$

Label whether this is proved, model-checked, property-tested, or merely checked at runtime.

## Minimum API and executable artifact

```ts
const ArchiveProject = operation({
  input:{project:Project},
  precondition:q=>q.and(q.capability("archive",q.input.project),q.not(q.fact(Archived,q.input.project))),
  footprint:[Archived,AuditLog],
  apply:({project},tx)=>{tx.assert(Archived(project));tx.append(AuditLog,{action:"archive",project});}
});
const offered = deriveAffordance(ArchiveProject,context);
const result = executor.commit(offered.intent,currentRevision);
```

Expose `operation.affordances`, `operation.explain`, `operation.prepare`, `operation.commit`, and `operation.check-invariants`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Operation schema

Define inputs, preconditions, outcomes, effects, footprints, revisions, and idempotency independently of UI.

### Capability evidence

Implement issuance and explanation with principal, scope, expiry/revision, and provenance.

### Transactional executor

Recheck preconditions, apply effects atomically, and record replayable traces.

### Affordance derivation

Derive labels, enabled/pending state, and reasons without capturing mutation callbacks.

### Invariant laboratory

Implement document, port compatibility, audit, and role invariants; generate races and stale intents.

## Required experiments

### TOCTOU comparison

Compare callback capture, capability-only commit, and full revalidation under randomized changes.

### Failure UX

Compare disabled, pending, optimistic, and reject-after-click presentations.

### Footprint precision

Measure invalidation and invariant cost with absent, broad, and precise footprints.

### Operation composition

Compose two operations transactionally and test contract/explanation clarity.

## Proof and validation obligations

- No affordance without displayed-snapshot evidence.
- Commit rechecks authoritative preconditions.
- Failed operations expose no partial effects.
- Fixture invariants hold after success.
- Effect traces cover the declared footprint.
- Expiry/revocation is a typed rejection.
- Duplicate non-idempotent commit is detected or governed.
- Labels do not determine authority.

## Measurements to report

- Stale-intent and false-authorization rates.
- Invariant cost by footprint precision.
- Affordance derivation latency.
- Recovery success after rejection.
- Trace size and replay determinism.

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

Export immutable operation specs, affordances, capability evidence, intents, typed results, footprints, and transaction traces. P09/P10 may request operations but receive no mutable store. P11 may use footprints. P12 may classify coordination requirements. Stable IDs and schemas, not labels, form the boundary.

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

- Embedding callbacks in menu records.
- Treating old capabilities as irrevocable.
- Incomplete footprints.
- Disabled UI as security boundary.
- Checking invariants after partial mutation.

## Stretch directions

- Refinement proof for one operation.
- Capability delegation/attenuation.
- Compensating operations without claiming inverses.
- Generate audit policy and docs from specs.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Operation and invariant corpus. |
| Weeks 2-3 | Schema, capabilities, executor. |
| Week 4 | Affordance derivation. |
| Weeks 5-6 | Race and invariant lab. |
| Weeks 7-8 | UX and footprint experiments. |
| Weeks 9-10 | Report and proof stretch. |

## Selected readings

1. Jonathan Haas et al. "LoRe: A Programming Model for Verifiably Safe Local-First Software." ECOOP 2023. https://drops.dagstuhl.de/opus/volltexte/2023/18205/pdf/LIPIcs-ECOOP-2023-12.pdf
2. Patrick Cousot and Radhia Cousot. "Abstract Interpretation Frameworks." Journal of Logic and Computation 2(4), 1992. https://www.di.ens.fr/~cousot/publications.www/CousotCousot-JLC-n2--3-p103--179-1992.pdf
3. Gordon Plotkin and Matija Pretnar. "Handlers of Algebraic Effects." ESOP 2009. https://homepages.inf.ed.ac.uk/gdp/publications/Effect_Handlers.pdf

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
