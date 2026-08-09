---
title: "P11: Incremental and Differential Evaluation"
subtitle: "Maintain semantic query results under change while retaining a transparent from-scratch meaning"
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
| Project | **P11: Incremental and Differential Evaluation** |
| Track | Runtime / optimization |
| Suggested team | 1-2 students with databases, incremental computation, compilers, or performance engineering experience |
| Nominal duration | 10-12 weeks |
| Primary result | A reference evaluator and an incremental runtime whose updates, deletions, evidence, and recursive results are continuously checked for from-scratch consistency. |

## Executive framing

A presentation-based system continuously changes. Occurrences mount and unmount, facts arrive from stores or servers, revisions advance, authorities are revoked, component topology changes, and recursive relations gain or lose support. Recomputing every selector and affordance from scratch is simple but may be too expensive. Ad hoc memoization is fast until a dependency, deletion, alias, or proof object is missed.

This project studies incremental evaluation as a semantic refinement rather than as a bag of caches. The reference meaning remains ordinary evaluation over a complete snapshot. The optimized engine consumes transactions of changes and must produce exactly the result that a fresh reference evaluation would produce, including retractions and explanation evidence. The study should determine which fragments are straightforward, which require stable names or logical time, and when a hybrid planner should abandon maintenance and recompute.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

## Research questions

- What change algebra is suitable for facts, occurrences, aliases, authorities, binding topology, and revisions?
- How should deletions and negative information be represented so stale candidates and evidence are retracted correctly?
- Which selector and rule operators admit simple derivatives, and which require indexes, arrangements, or recomputation?
- How should stable semantic names interact with incremental caches without merging distinct subjects?
- Can provenance and explanations be maintained incrementally without unbounded retention?
- How are transactions, logical time, and recursive fixed points exposed without leaking runtime machinery into the semantic API?
- When should the planner choose from-scratch, incremental, or partially materialized execution?

## Falsifiable hypotheses

- A snapshot reference semantics plus transaction boundaries is sufficient to state a strong from-scratch-consistency property.
- Most practical PBUI selectors can be maintained using indexed relational changes; opaque predicates require declared dependencies or conservative invalidation.
- Stable names improve reuse but must be typed and revision-aware.
- Evidence can be maintained as reference-counted support DAGs more reliably than by caching rendered explanations.
- For small relations or high-churn updates, recomputation will outperform differential maintenance; a hybrid planner is necessary.

A negative result is acceptable when demonstrated rather than asserted.

## Explicit non-goals

- Inventing a new general-purpose streaming database.
- Claiming incremental support for arbitrary JavaScript closures.
- Treating a cache hit as a semantic proof.
- Hiding transaction or disposal boundaries.
- Optimizing before a reference evaluator exists.

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

Let $D$ be a semantic database and let $Q$ be a query or derived relation. A change $\Delta D$ is interpreted by a composition operation $D\oplus\Delta D$. An incremental evaluator computes a result change $\delta Q(D,\Delta D)$ satisfying

$$Q(D\oplus\Delta D)=Q(D)\oplus\delta Q(D,\Delta D).$$

This is **from-scratch consistency**. State the result carrier and update algebra explicitly: sets may use insertions and deletions, multisets may use integer weights, and proof-relevant results may use support counts or provenance expressions. For recursive rules, define logical timestamps or stage coordinates and state when the maintained fixed point agrees with the least fixed point of the updated database.

If a change action is used for higher-order or structured values, specify its laws rather than assuming subtraction exists. Stable names are observations used to align computations; prove or test that equal names imply the intended semantic reuse relation, not merely syntactic coincidence.

## Minimum API and executable artifact

```ts
interface IncrementalEngine {
  load(snapshot: SemanticSnapshot): Promise<Revision>;
  subscribe(query: QueryIR, sink: (change: ResultChange) => void): Subscription;
  transact(changes: readonly SemanticChange[]): Promise<Revision>;
  materialize(query: QueryIR): Promise<ResultSnapshot>;
  verifyFromScratch(query?: QueryIR): Promise<ConsistencyReport>;
  explainPlan(query: QueryIR): IncrementalPlan;
}
```

Expose `incremental.load`, `incremental.subscribe`, `incremental.transact`, `incremental.materialize`, `incremental.verify`, and `incremental.plan` through the lab adapter. The same query IR must run in a slow reference evaluator.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

## Work packages

### Snapshot semantics

Implement a deliberately slow evaluator for the relevant P03/P04-style query and rule fragment; canonicalize outputs and evidence.

### Change algebra

Define typed inserts, deletes, replacements, revisions, topology changes, transaction commits, and disposal; reject malformed retractions.

### Incremental operators

Maintain selection, projection, union, join, antijoin or bounded negation, ranking, and proof support with explicit indexes.

### Recursive maintenance

Implement a bounded positive recursive fragment using semi-naive or differential techniques and compare it with fresh closure.

### Planner and diagnostics

Explain materialization, dependencies, indexes, estimated costs, invalidation, foreign fallbacks, and memory retention.

### Benchmark and differential oracle

Generate workloads, replay traces, compare every committed state to the reference result, and minimize divergences.

## Required experiments

### Scale and churn

Run 1k, 10k, and 100k fact/occurrence workloads under read-heavy, write-heavy, burst, and delete-heavy traces.

### Naming ablation

Compare no stable names, semantic names, occurrence names, and deliberately colliding names; measure reuse and correctness.

### Evidence strategies

Compare recomputed explanations, support counts, minimal-support DAGs, and complete provenance for update cost and memory.

### Hybrid planning

Find crossover points between full recomputation, local invalidation, and differential maintenance; test plan stability.

### Fault injection

Drop, duplicate, reorder, or partially apply internal changes and verify that transactions detect or expose divergence rather than silently committing it.

## Proof and validation obligations

- For every committed transaction in the supported fragment, maintained results equal canonical from-scratch results.
- No subscriber observes a partially applied transaction.
- Deleting the last support retracts the candidate and its evidence.
- Recursive maintained results equal fresh least-fixed-point closure.
- Stable names do not merge semantically distinct subjects or occurrences.
- Disposal releases subscriptions, indexes, and retained evidence.
- A divergence report contains a minimized trace, seed, query, and differing result.
- Foreign predicates state dependency and invalidation policy and cannot inherit core guarantees silently.
- Ranking updates cannot alter membership truth.
- Plan changes do not alter denotation.

## Measurements to report

- Commit and propagation latency distributions.
- Peak memory and retained support size.
- Number of touched facts/operators per change.
- From-scratch verification cost and divergence rate.
- Planner crossover accuracy.
- Subscription/resource leak count.

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

Export the supported query/rule fragment, snapshot and change schemas, canonical result format, transaction semantics, plan explanation, subscriptions, and consistency reports. P03/P04 provide syntax and reference corpora; P06 contributes topology changes; P12 may feed replicated deltas; P14 may certify a small derivative fragment; P15 acts as independent oracle. Consumers must not depend on internal timestamp or arrangement representations.

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

- Benchmarking only insertions.
- Using object identity as a stable name.
- Keeping obsolete provenance forever.
- Assuming deletions are inverse insertions in every carrier.
- Observing intermediate states.
- Optimized and reference evaluators sharing enough code to share the same bug.

## Stretch directions

- Proof-producing incremental plans.
- Adaptive materialization under workload change.
- Incremental three-valued remote facts.
- Worker or WASM execution with deterministic traces.
- A mechanized derivative theorem for one relational fragment.

## Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Snapshot semantics and workload corpus. |
| Weeks 2-3 | Change algebra and basic operators. |
| Weeks 4-5 | Joins, negation, ranking, evidence. |
| Weeks 6-7 | Recursive maintenance. |
| Week 8 | Planner and diagnostics. |
| Weeks 9-10 | Benchmark and fault injection. |
| Weeks 11-12 | Report and proof stretch. |

## Selected readings

1. Frank McSherry et al. "Differential Dataflow." CIDR 2013. https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf
2. Mihai Budiu et al. "DBSP: Automatic Incremental View Maintenance for Rich Query Languages." PVLDB 16(7), 2023. https://www.vldb.org/pvldb/vol16/p1601-budiu.pdf
3. Yufei Cai et al. "A Theory of Changes for Higher-Order Languages." PLDI 2014. https://arxiv.org/abs/1312.0658
4. Matthew A. Hammer et al. "Adapton: Composable, Demand-Driven Incremental Computation." PLDI 2014. https://matthewhammer.org/adapton/adapton-pldi2014.pdf
5. Matthew A. Hammer et al. "Incremental Computation with Names." OOPSLA 2015. https://arxiv.org/abs/1503.07792

## Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?
