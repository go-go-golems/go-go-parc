---
title: "P01: Semantic Identity and the Subject Registry"
subtitle: "Separate domain identity, value equality, aliases, revisions, and occurrence identity"
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
| Project | **P01: Semantic Identity and the Subject Registry** |
| Track | Semantic foundations |
| Suggested team | 1-2 students with type-system or data-modeling experience |
| Nominal duration | 7-9 weeks |
| Primary result | A reference model and API for stable semantic subjects that does not confuse JavaScript references, values, aliases, or rendered occurrences. |

## Executive framing

Every other subsystem depends on an answer to "what object is this?" A React key, JavaScript pointer, database key, structural hash, and user-visible name answer different questions. This project studies a typed subject model that remains coherent under immutable updates, decoding, aliases, deletion, merging, and multiple visual forms.

The central tension is between nominal identity, which is stable but requires key authority, and extensional value equality, which is useful for pure values but unsafe for entities. The prototype must support both without accidental cross-sort equality and must expose evidence for equality and distinction.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- Which semantic sorts denote entities, which denote values, and which permit both interpretations?
- Should canonicalization be total, partial, revision-sensitive, or context-sensitive?
- How should aliases, tombstones, entity merges, and entity splits be represented without erasing provenance?
- Can cross-sort identity such as `project` and `projectId` be expressed safely without making all strings interchangeable?
- What must be persisted so identity is stable across reloads and replicas?
- How should identity evidence be exposed to selection, caching, explanations, and users?

## Falsifiable hypotheses

- A dependent pair of semantic sort and sort-local key is sufficient for most application entities when aliases are represented separately.
- Canonicalization can be idempotent and deterministic without structural equality of arbitrary host objects.
- Revision should not normally participate in entity identity, but must participate in staleness validation.
- A small explicit identity-evidence type prevents more integration bugs than implicit coercions.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- A universal database key system.
- Distributed consensus for key allocation.
- Structural deep equality as the default entity semantics.
- Rendered occurrence lifecycle.
- Generic query evaluation.

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

Let $S$ be semantic sorts. Each sort $s$ has carrier $V_s$ and key space $K_s$. A subject reference is

$$\operatorname{SubjectRef}=\sum_{s:S}K_s.$$

Application values may have a partial key function $\operatorname{key}_s:V_s\rightharpoonup K_s$. Aliases form a typed relation $A_s\subseteq K_s\times K_s$; only a policy-approved equivalence closure $\sim_s$ supports canonicalization

$$c_s:K_s\to K_s/{\sim_s}.$$

Revisions are separate observations used for freshness, not normally identity. The project must distinguish `sameEntity`, `sameValue`, `aliases`, and `freshEnough`. A single undifferentiated `equals` method is an anti-design to test.

## Minimum API and executable artifact

```ts
interface SubjectRef<S extends string = string> { sort: S; key: string }
type IdentityEvidence =
  | { kind: "same-key"; subject: SubjectRef }
  | { kind: "alias-path"; path: readonly SubjectRef[] }
  | { kind: "value-proof"; comparatorId: string }
  | { kind: "distinct"; reason: string };
interface SubjectRegistry {
  canonical(ref: SubjectRef): SubjectRef;
  compare(a: SubjectRef, b: SubjectRef): IdentityEvidence;
  revision(ref: SubjectRef): string | undefined;
  addAlias(a: SubjectRef, b: SubjectRef, reason: string): Result<void>;
  retire(ref: SubjectRef, tombstone: Tombstone): Result<void>;
}
```

The adapter supports `identity.canonicalize`, `identity.compare`, `identity.alias`, `identity.retire`, and `identity.snapshot`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Identity taxonomy

Classify fixture sorts as entity, value, occurrence, capability, or compound reference. Write cases where each equality policy succeeds and fails.

### Reference registry

Implement namespaces, aliases, revisions, tombstones, and deterministic canonical representatives. Start with a transparent graph model.

### Evidence and diagnostics

Return structured evidence for equality and inequality. Build an inspector for canonical key, alias path, revision, and retirement.

### Host-object adapters

Adapt immutable records and primitive IDs. Demonstrate that reconstruction does not change entity identity and duplicate rows need explicit keys.

### Generated tests

Generate aliases, merges, retirements, and reloads; preserve minimized namespace, idempotence, and revision counterexamples.

## Required experiments

### Equality-policy comparison

Compare pointer identity, structural equality, bare strings, and typed semantic keys on shared traces; classify false merges and splits.

### Alias stress test

Generate adversarial alias graphs from 10 to 100,000 keys; compare stability, latency, and explanation quality.

### Persistence round trip

Serialize and reload in randomized order; verify observable comparisons remain stable.

### Explanation probe

Ask developers to diagnose identity failures with and without evidence; record time and requested information.

## Proof and validation obligations

- Canonicalization is idempotent: $c(c(x))=c(x)$.
- Alias-equivalent keys have equal canonical representatives.
- Incompatible identity domains never compare as the same entity.
- Revision changes do not silently change entity identity.
- Retired subjects cannot commit without an explicit resurrection policy.
- Serialization preserves observable comparisons.
- Duplicate alias insertion is idempotent.
- Every alias-path explanation is valid.

## Measurements to report

- False identity merges and splits.
- Comparison latency by alias-graph size.
- Serialized size and reload time.
- Explanation path length.
- Developer diagnosis time.

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

Export immutable `SubjectRef`, `IdentityEvidence`, identity policy metadata, alias events, and canonicalization. Later teams may rely on idempotence and sort separation, not on key string format, internal graph structure, or JavaScript pointer equality. Include golden object-to-subject fixtures.

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

- Insertion-order-dependent representatives presented as deterministic.
- Aliases bridging incompatible sorts.
- Treating merge as reversible after information loss.
- Using revision as identity.
- Hidden process-global key allocation.

## Stretch directions

- Mechanize the equivalence core in Lean.
- Support explicit key migration.
- Explore privacy-preserving opaque keys.
- Model entity split with provenance-preserving branching.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Taxonomy and law draft. |
| Weeks 2-3 | Registry and persistence. |
| Week 4 | Evidence inspector. |
| Weeks 5-6 | Generated tests and policy comparison. |
| Week 7 | Explanation probe and report. |
| Weeks 8-9 | Optional formalization. |

## Selected readings

1. Joseph A. Goguen and Rod M. Burstall. "Institutions: Abstract Model Theory for Specification and Programming." JACM 39(1), 1992. https://cseweb.ucsd.edu/~goguen/pps/ins.pdf
2. Matthew A. Hammer et al. "Incremental Computation with Names." OOPSLA 2015. https://arxiv.org/abs/1503.07792
3. Todd J. Green, Grigoris Karvounarakis, and Val Tannen. "Provenance Semirings." PODS 2007. https://web.cs.ucdavis.edu/~green/papers/pods07.pdf

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
