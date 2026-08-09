---
title: "P12: Local-First Replicated Bindings and Topology"
subtitle: "Separate convergence of replicated declarations from derived port equivalence and application invariants"
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
| Project | **P12: Local-First Replicated Bindings and Topology** |
| Track | Replication / coordination |
| Suggested team | 1-2 students with distributed systems, CRDTs, local-first software, or concurrency experience |
| Nominal duration | 10-12 weeks |
| Primary result | A replicated workspace model for link declarations, unlinking, values, deletion, and conflicts, with explicit convergence and coordination claims. |

## Executive framing

A local presentation-based workbench may be edited on several devices or by several collaborators. While disconnected, users can change selected documents, link or unlink ports, delete components, and revoke authority. Eventual delivery can make replicas converge, but convergence alone does not preserve typing, uniqueness, authorization, or user intent.

This project separates replicated **source declarations** from deterministic **derived structures**. In particular, replicas should exchange link and unlink facts or commands, not unstable union-find representatives. Each replica derives its port quotient from the same surviving declarations. The study must classify which invariants are coordination-free, which need conflict objects, and which require coordination or a redesign into monotone state.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- Which workspace facts are grow-only, retractable, ordered, or authority-sensitive?
- Should identity links be represented by edge sets, observed-remove sets, operation logs, epochs, or another structure?
- How should unlinking interact with concurrent linking and transitive groups?
- What policy should reconcile concurrent writes to a shared binding value?
- How do component deletion, tombstones, permission revocation, and schema migration affect derived bindings?
- Which invariants are invariant-confluent and which require coordination?
- How can the UI explain causal histories and unresolved intent rather than merely displaying a winning value?

## Falsifiable hypotheses

- Replicating link declarations and deriving equivalence classes is more stable than replicating quotient representatives.
- No single register policy is appropriate for all binding values; the port contract must choose LWW, multi-value, join, intent log, or coordinated update.
- Convergence and invariant preservation must be reported separately.
- A compact causal explanation substantially improves recovery from concurrent link/unlink and deletion conflicts.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- A production collaboration service.
- Assuming clocks are perfectly synchronized.
- Calling any merge function a CRDT without laws.
- Silent last-writer-wins for every semantic conflict.
- Replicating React component state.

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

For state-based replication, use a join-semilattice $(L,\sqsubseteq,\sqcup)$ and inflationary local updates. Replica merge is $x\sqcup y$ and must be associative, commutative, and idempotent. Operation-based designs must state causal delivery and exactly-once or idempotence assumptions.

Let $E_r$ be the surviving typed link declarations at replica $r$. The derived binding partition is

$$Q_r = P/{\sim_{E_r}},$$

where $\sim_{E_r}$ is the least equivalence relation generated by valid declarations. The quotient is derived, not directly merged. For each safety invariant $I$, investigate invariant confluence: can all independently valid states merge to another state satisfying $I$ without coordination? A negative result should identify the minimal conflicting operations.

## Minimum API and executable artifact

```ts
interface Replica {
  applyLocal(command: WorkspaceCommand): LocalResult;
  merge(remote: ReplicaState): MergeResult;
  derivedBindings(): BindingPlan;
  conflicts(): readonly SemanticConflict[];
  causalTrace(target: SubjectRef | PortRef | BindingRef): CausalExplanation;
}
type WorkspaceCommand =
  | { kind: "link"; left: PortRef; right: PortRef }
  | { kind: "unlink"; linkId: string }
  | { kind: "setBinding"; port: PortRef; value: SubjectRef }
  | { kind: "removeComponent"; component: ComponentRef };
```

Expose `replica.apply`, `replica.merge`, `replica.bindings`, `replica.conflicts`, and `replica.explain`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### State classification

Catalog topology, value, identity, authority, occurrence, and UI-only state; decide what is replicated and why.

### Replicated topology

Implement at least two candidate designs for link/unlink declarations, derive typed partitions, and preserve causal provenance.

### Value policies

Implement LWW, multi-value, join-semilattice, and intent-log policies behind explicit port contracts.

### Invariant analysis

State typing, uniqueness, authority, deletion, and referential invariants; test or prove coordination requirements on bounded domains.

### Conflict explanations

Expose concurrent operations, causal order, derived effect, policy, and available repairs in machine- and human-readable forms.

### Partition simulator

Run deterministic and randomized network schedules with partitions, duplication, reordering, and delayed revocation.

## Required experiments

### Concurrent topology matrix

Link A-B versus unlink B-C, overlapping links, repeated unlink, delete versus link, and component recreation with a new identity.

### Concurrent value switch

Compare LWW, multi-value, join, and intent log when chart and pipeline select different documents offline.

### Delete versus edit

Delete a document or component concurrently with selection, linking, operation commit, and alias creation.

### Bounded invariant confluence

Enumerate small states and pairs of valid operations; find minimal merges violating each invariant.

### Explanation study

Ask users to predict and repair outcomes from final value alone versus causal explanation.

## Proof and validation obligations

- Merge is associative, commutative, and idempotent for the stated state-based carrier, or equivalent delivery assumptions are explicit.
- All replicas with the same delivered operations derive extensionally equal bindings.
- Derived identity links preserve typed compatibility or surface a conflict rather than generating an invalid class.
- No chosen value policy silently discards a concurrent semantic conflict unless that loss is its declared contract.
- Tombstones or epochs prevent unintended resurrection under the chosen model.
- Every coordination claim is classified as proved, bounded-model-checked, tested, or conjectured.
- Causal explanations identify contributing operations and policy.
- Stable external binding IDs do not depend on local union-find representatives.
- Authority revocation is not treated as an ordinary eventually consistent preference when safety requires coordination.
- Garbage collection assumptions are explicit.

## Measurements to report

- Replica-state and operation-log growth.
- Merge/derived-partition latency.
- Conflict frequency by workload.
- Metadata overhead by policy.
- Convergence schedules explored.
- User repair time and correctness.

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

Export the replica state schema, command/event schema, merge contract, derived link declarations, value-policy descriptors, conflicts, and causal explanations. P01 supplies subject identity; P05 authority and operation safety; P06 recompiles declarations into bindings; P08 handles unequal-view repair; P13 renders conflict explanations; P15 controls schedules. No consumer may infer semantic order from transport arrival order.

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

- Equating eventual convergence with correct intent.
- Replicating implementation-generated class IDs.
- Using wall-clock LWW without acknowledging loss.
- Garbage collecting tombstones without a causal-stability argument.
- Authority checks made only when an affordance was rendered.
- Calling bounded enumeration a general proof.

## Stretch directions

- Delta-state CRDTs and compact causal contexts.
- Mechanized convergence for the topology carrier.
- Verified invariant-confluence checker on a bounded DSL.
- Local-first undo as compensating intent.
- Encrypted or partially replicated workspaces.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | State/invariant classification. |
| Weeks 2-3 | Replicated topology candidates. |
| Weeks 4-5 | Value policies and simulator. |
| Weeks 6-7 | Invariant-confluence study. |
| Weeks 8-9 | Conflict explanation and user study. |
| Weeks 10-12 | Optimization, report, formal stretch. |

## Selected readings

1. Marc Shapiro et al. "A Comprehensive Study of Convergent and Commutative Replicated Data Types." INRIA Research Report 7506, 2011. https://inria.hal.science/inria-00555588v1/document
2. Joseph M. Hellerstein and Peter Alvaro. "Keeping CALM: When Distributed Consistency Is Easy." CACM 63(9), 2020. https://arxiv.org/abs/1901.01930
3. Lindsey Kuper and Ryan R. Newton. "LVars: Lattice-Based Data Structures for Deterministic Parallelism." FHPC 2013. https://users.soe.ucsc.edu/~lkuper/papers/lvars-fhpc13.pdf
4. Jonathan Haas et al. "LoRe: A Programming Model for Verifiably Safe Local-First Software." ECOOP 2023. https://drops.dagstuhl.de/opus/volltexte/2023/18205/pdf/LIPIcs-ECOOP-2023-12.pdf

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
