---
title: "PBUI Subsystem Research Projects"
subtitle: "Program handbook, fifteen standalone briefs, and composition appendices"
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

# Part I - Program handbook

## Purpose

This package defines a first research pass for a presentation-based user-interface architecture. It is intentionally organized as **small, independently executable projects** rather than as a single platform implementation. Each team receives a bounded semantic problem, a shared miniature workbench, a black-box handoff protocol, and an obligation to report negative results.

The program has two passes:

1. **Subsystem pass.** Each team builds and evaluates one subsystem without importing another team's code. The goal is to discover semantic boundaries, false assumptions, laws, counterexamples, implementation costs, and user-facing consequences.
2. **Composition pass.** Only after individual capsules have stabilized are selected subsystems substituted and composed in controlled constellations. The goal is not to merge everything. It is to identify which interfaces compose, which guarantees survive, which assumptions conflict, and where a simpler architecture is preferable.

The package is suitable for graduate seminars, doctoral rotations, research engineers, or parallel exploratory teams. Projects differ in mathematical and empirical emphasis, but every project must ship executable evidence.

## Program principles

### Semantic claims before framework choices

A project begins by stating its objects, operations, observations, and laws. React, TypeScript, Lean, Datalog, CRDT libraries, statechart tools, and database engines are candidate implementations. None is the definition of the subsystem.

### Reference semantics before optimization

Every optimized, incremental, distributed, or ergonomic implementation needs a smaller, transparent reference model whenever feasible. The reference may be slow. Its job is to make disagreement observable.

### Proof scope is explicit

Reports label each claim as one of:

- **proved** in a named formal development under stated assumptions;
- **model-checked** over a stated finite abstraction;
- **property-tested** over generated cases and recorded seeds;
- **example-tested** over a fixed suite;
- **empirical** from measurement or user study;
- **assumed** at a foreign boundary;
- **conjectured** and unresolved.

No project may use the phrase "verified" without naming the artifact and scope.

### Counterexamples are first-class results

A minimized counterexample that invalidates an appealing law or API is a successful outcome. Every team maintains a counterexample corpus and explains how the design changed in response.

### User experience is part of the semantics

Selection, rejection, authority, staleness, conflicts, phase, and affected views must be visible through at least one user-facing prototype. A subsystem that cannot explain its result may be semantically incomplete even when its internal algorithm is correct.

### Composition is by declared artifacts

Teams compose through versioned syntax, extensional data, evidence, events, resources, or process protocols. They do not import undocumented classes or rely on accidental in-memory object identity.

## Portfolio

| Code | Project | Primary track | Nominal duration |
|---|---|---|---|
| P01 | Semantic Identity and the Subject Registry | Semantic foundations | 7-9 weeks |
| P02 | Occurrence Semantics and the Concurrent React Adapter | Semantic foundations / runtime boundary | 8-10 weeks |
| P03 | Inspectable Typed Selectors and Selection Evidence | Query semantics | 8-10 weeks |
| P04 | Recursive Rules, Fixed Points, and Provenance | Query semantics / formal foundations | 9-11 weeks |
| P05 | Operations, Capabilities, and Invariant-Preserving Affordances | Operations and authority | 8-10 weeks |
| P06 | Typed Ports and the Binding Quotient Compiler | Open systems / wiring | 9-11 weeks |
| P07 | Open Components, Plugin Signatures, and Composition | Open systems / modularity | 9-11 weeks |
| P08 | Bidirectional Links and Consistency Restoration | Synchronization semantics | 9-11 weeks |
| P09 | Coalgebraic Interaction Machines | Interaction semantics | 8-10 weeks |
| P10 | Algebraic Interaction Programs and Effect Handlers | Interaction programming | 8-10 weeks |
| P11 | Incremental and Differential Evaluation | Runtime / optimization | 10-12 weeks |
| P12 | Local-First Replicated Bindings and Topology | Replication / coordination | 10-12 weeks |
| P13 | Explanation, Accessibility, and Proof-Relevant Interaction | Human factors / semantics | 8-10 weeks |
| P14 | Mechanized Semantic Kernel and Proof-Carrying Compilation | Formal verification | 11-13 weeks |
| P15 | Conformance, Model-Based Testing, and Comparative Benchmarking | Validation / integration science | 9-11 weeks |

The portfolio is intentionally redundant at boundaries. For example, P06 studies port quotienting while P12 studies replicated link declarations, and P03 studies query evidence while P13 studies human explanations. This overlap is diagnostic: two teams should sometimes discover that a boundary was drawn incorrectly.

## Shared analytical workbench

### Shared laboratory setting

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

### Common artifact boundary

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

The fixture is deliberately small enough to model exhaustively in several projects. Teams may add scale fixtures for performance studies, but all published results must include the common traces so readers can compare interpretations.

## Independence rules for the first pass

1. A team may read another project brief, but it must not import another team's implementation during the subsystem pass.
2. Shared fixtures and protocol schemas are permitted.
3. If a project needs a neighboring subsystem, it builds the smallest local stub or reference model and labels it as such.
4. Teams may exchange counterexamples through the program repository.
5. Cross-reviewers inspect semantic assumptions and capsule boundaries; they do not rewrite the implementation.
6. A project can narrow its supported fragment, but the narrowing must be machine-readable in its capability manifest.

## Repository and artifact structure

Each team should use the following shape:

```text
project/
  README.md
  report/
  src/
  reference/
  demo/
  tests/
  counterexamples/
  fixtures/
  capsule/
    manifest.json
    schemas/
    adapter
  scripts/
    reproduce
```

The `scripts/reproduce` entry point installs or checks the pinned toolchain, runs tests, builds the capsule, executes common traces, and generates the principal report tables. When installation must use a network, document an offline cache or container alternative.

## Program milestones

### Milestone 0 - preregistration and threat model

Before implementation, each team submits:

- a one-page semantic model;
- three falsifiable hypotheses;
- the proposed trusted boundary;
- a list of likely false laws;
- an experimental plan and stopping condition;
- the initial capability manifest.

### Milestone 1 - reference artifact

The reference semantics runs at least three shared traces and has generated tests for its basic laws. No optimization claim is accepted before this milestone.

### Milestone 2 - experimental prototype

The main implementation or proof development exists, common traces run, and at least one early design has produced a counterexample.

### Milestone 3 - external replication

A paired reviewer checks out the artifact, runs the entry point, writes one new trace, and attempts to falsify one claim.

### Milestone 4 - capsule freeze

Schemas, capability claims, normalization, and assumptions are versioned. The artifact is ready for the second-pass composition lab.

## Evaluation rubric

Each project is assessed on a 100-point rubric:

| Dimension | Weight | Core question |
|---|---:|---|
| Semantic clarity | 20 | Are the objects, observations, laws, and non-goals precise? |
| Correctness evidence | 20 | Do proofs, models, generated tests, and examples match the claims? |
| Experimental quality | 15 | Can the hypotheses actually be falsified, and are negative results reported? |
| User-facing evidence | 10 | Can a user or reviewer observe the relevant state and failures? |
| Composition readiness | 15 | Is the capsule stable, versioned, typed, and explicit about reliance? |
| Reproducibility | 10 | Can a second team reproduce results from a clean checkout? |
| Critical judgment | 10 | Does the report identify limitations, alternatives, and overclaims? |

The detailed rubric is in `shared/EVALUATION-RUBRIC.md`.

## Cross-review assignments

| Primary pair | Review focus |
|---|---|
| P01 and P02 | Domain identity versus occurrence identity and lifecycle |
| P03 and P04 | Nonrecursive query meaning versus recursive closure |
| P05 and P12 | Authority and invariant preservation under concurrency |
| P06 and P08 | Identity links versus transformed consistency links |
| P07 and P15 | Open component contracts versus black-box substitutability |
| P09 and P10 | Explicit machines versus effectful program notation |
| P11 and P14 | Optimized maintenance versus checked semantic kernels |
| P13 and all teams | User-visible semantic status and explanation quality |
| P15 and all teams | Reproducibility, negative controls, and comparison boundaries |

A cross-review must produce at least one new test, counterexample, or clarified assumption.

## Decision records

Every project maintains short decision records with:

```text
Context
Candidate designs
Chosen design
Laws or evidence supporting it
Counterexamples rejected or accepted
Consequences for composition
Revisit trigger
```

Decisions are not permanent. A revisit trigger is mandatory because later composition may invalidate a locally reasonable choice.

## Second-pass composition constellations

The program does not begin with a single grand integration. It uses five controlled constellations.

### Constellation A - deterministic local workbench

P01 + P02 + P03 + P05 + P06 + P09 + P11 + P13

Question: can identity, mounted occurrences, inspectable selection, authorized operations, shared bindings, explicit workflows, incremental maintenance, and accessible explanation form one deterministic local system?

### Constellation B - open analytical components

P06 + P07 + P08 + P09 + P13

Question: can independently developed chart, pipeline, and table components be wired through typed identity and transformed links without private-store coupling?

### Constellation C - proof-carrying semantic runtime

P03 + P04 + P06 + P11 + P14 + P15

Question: can query, closure, binding, and incremental artifacts carry enough evidence or certificates for an independent checker and differential harness?

### Constellation D - local-first linked workbench

P01 + P05 + P06 + P08 + P12 + P13 + P15

Question: which identity, authority, link, and explanation invariants survive partitions, concurrent edits, and replica merge?

### Constellation E - effectful interaction architecture

P03 + P05 + P09 + P10 + P13

Question: does a structured interaction program improve authoring while lowering to an explicit machine whose semantic phases and effects remain inspectable?

Detailed entry criteria and experiment sequences are in `shared/PHASE-2-COMPOSITION-MAP.md`.

## Program-wide stop conditions

A subsystem should stop expanding and ship a bounded result when any of the following holds:

- the proposed law is false and a useful counterexample plus replacement contract has been established;
- the supported fragment is sufficient for all common traces and expansion would add only host-language features;
- performance is already dominated by an adjacent subsystem outside the project's scope;
- the proof burden exposes an unstated assumption that must be resolved in another project;
- user testing shows the semantic distinction is not actionable in the current form;
- composition requires an interface change that should be evaluated in the second pass rather than hidden locally.

## Program-wide failure modes

The research program should actively watch for:

- category-theoretic terminology used without naming objects, morphisms, and the claimed universal property;
- formal proofs detached from the executable artifact;
- TypeScript types presented as proof of runtime properties;
- opaque callbacks inheriting guarantees from a structured core;
- eventual convergence presented as invariant preservation;
- union-find representatives persisted as semantic identities;
- user interfaces that collapse unknown, stale, unauthorized, and false into disabled;
- benchmarks without a correctness gate;
- project scopes that silently grow into complete platforms;
- composition through undocumented implementation classes.

## Handoff to the composition pass

A project is eligible for composition only when:

1. its capability manifest validates;
2. its common traces and declared law suite pass;
3. its assumptions and guarantee labels are current;
4. an external reviewer reproduced the artifact;
5. at least one negative control demonstrates that the tests can fail;
6. its composition capsule states what may be relied upon and what may not;
7. user-facing semantic statuses are inspectable, directly or through P13's model;
8. no unresolved critical safety issue is being hidden as a performance or UX detail.

The composition pass should preserve all original traces and counterexamples. Integration success is not merely that the demo runs; it is that local guarantees are either preserved, weakened explicitly, or refuted with a reproducible example.

\clearpage

# Part II - Individual subsystem projects

\clearpage

## P01: Semantic Identity and the Subject Registry

*Separate domain identity, value equality, aliases, revisions, and occurrence identity*

| Field | Assignment |
|---|---|
| Project | **P01: Semantic Identity and the Subject Registry** |
| Track | Semantic foundations |
| Suggested team | 1-2 students with type-system or data-modeling experience |
| Nominal duration | 7-9 weeks |
| Primary result | A reference model and API for stable semantic subjects that does not confuse JavaScript references, values, aliases, or rendered occurrences. |

### Executive framing

Every other subsystem depends on an answer to "what object is this?" A React key, JavaScript pointer, database key, structural hash, and user-visible name answer different questions. This project studies a typed subject model that remains coherent under immutable updates, decoding, aliases, deletion, merging, and multiple visual forms.

The central tension is between nominal identity, which is stable but requires key authority, and extensional value equality, which is useful for pure values but unsafe for entities. The prototype must support both without accidental cross-sort equality and must expose evidence for equality and distinction.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- Which semantic sorts denote entities, which denote values, and which permit both interpretations?
- Should canonicalization be total, partial, revision-sensitive, or context-sensitive?
- How should aliases, tombstones, entity merges, and entity splits be represented without erasing provenance?
- Can cross-sort identity such as `project` and `projectId` be expressed safely without making all strings interchangeable?
- What must be persisted so identity is stable across reloads and replicas?
- How should identity evidence be exposed to selection, caching, explanations, and users?

### Falsifiable hypotheses

- A dependent pair of semantic sort and sort-local key is sufficient for most application entities when aliases are represented separately.
- Canonicalization can be idempotent and deterministic without structural equality of arbitrary host objects.
- Revision should not normally participate in entity identity, but must participate in staleness validation.
- A small explicit identity-evidence type prevents more integration bugs than implicit coercions.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- A universal database key system.
- Distributed consensus for key allocation.
- Structural deep equality as the default entity semantics.
- Rendered occurrence lifecycle.
- Generic query evaluation.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

Let $S$ be semantic sorts. Each sort $s$ has carrier $V_s$ and key space $K_s$. A subject reference is

$$\operatorname{SubjectRef}=\sum_{s:S}K_s.$$

Application values may have a partial key function $\operatorname{key}_s:V_s\rightharpoonup K_s$. Aliases form a typed relation $A_s\subseteq K_s\times K_s$; only a policy-approved equivalence closure $\sim_s$ supports canonicalization

$$c_s:K_s\to K_s/{\sim_s}.$$

Revisions are separate observations used for freshness, not normally identity. The project must distinguish `sameEntity`, `sameValue`, `aliases`, and `freshEnough`. A single undifferentiated `equals` method is an anti-design to test.

### Minimum API and executable artifact

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

### Work packages

#### Identity taxonomy

Classify fixture sorts as entity, value, occurrence, capability, or compound reference. Write cases where each equality policy succeeds and fails.

#### Reference registry

Implement namespaces, aliases, revisions, tombstones, and deterministic canonical representatives. Start with a transparent graph model.

#### Evidence and diagnostics

Return structured evidence for equality and inequality. Build an inspector for canonical key, alias path, revision, and retirement.

#### Host-object adapters

Adapt immutable records and primitive IDs. Demonstrate that reconstruction does not change entity identity and duplicate rows need explicit keys.

#### Generated tests

Generate aliases, merges, retirements, and reloads; preserve minimized namespace, idempotence, and revision counterexamples.

### Required experiments

#### Equality-policy comparison

Compare pointer identity, structural equality, bare strings, and typed semantic keys on shared traces; classify false merges and splits.

#### Alias stress test

Generate adversarial alias graphs from 10 to 100,000 keys; compare stability, latency, and explanation quality.

#### Persistence round trip

Serialize and reload in randomized order; verify observable comparisons remain stable.

#### Explanation probe

Ask developers to diagnose identity failures with and without evidence; record time and requested information.

### Proof and validation obligations

- Canonicalization is idempotent: $c(c(x))=c(x)$.
- Alias-equivalent keys have equal canonical representatives.
- Incompatible identity domains never compare as the same entity.
- Revision changes do not silently change entity identity.
- Retired subjects cannot commit without an explicit resurrection policy.
- Serialization preserves observable comparisons.
- Duplicate alias insertion is idempotent.
- Every alias-path explanation is valid.

### Measurements to report

- False identity merges and splits.
- Comparison latency by alias-graph size.
- Serialized size and reload time.
- Explanation path length.
- Developer diagnosis time.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export immutable `SubjectRef`, `IdentityEvidence`, identity policy metadata, alias events, and canonicalization. Later teams may rely on idempotence and sort separation, not on key string format, internal graph structure, or JavaScript pointer equality. Include golden object-to-subject fixtures.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Insertion-order-dependent representatives presented as deterministic.
- Aliases bridging incompatible sorts.
- Treating merge as reversible after information loss.
- Using revision as identity.
- Hidden process-global key allocation.

### Stretch directions

- Mechanize the equivalence core in Lean.
- Support explicit key migration.
- Explore privacy-preserving opaque keys.
- Model entity split with provenance-preserving branching.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Taxonomy and law draft. |
| Weeks 2-3 | Registry and persistence. |
| Week 4 | Evidence inspector. |
| Weeks 5-6 | Generated tests and policy comparison. |
| Week 7 | Explanation probe and report. |
| Weeks 8-9 | Optional formalization. |

### Selected readings

1. Joseph A. Goguen and Rod M. Burstall. "Institutions: Abstract Model Theory for Specification and Programming." JACM 39(1), 1992. https://cseweb.ucsd.edu/~goguen/pps/ins.pdf
2. Matthew A. Hammer et al. "Incremental Computation with Names." OOPSLA 2015. https://arxiv.org/abs/1503.07792
3. Todd J. Green, Grigoris Karvounarakis, and Val Tannen. "Provenance Semirings." PODS 2007. https://web.cs.ucdavis.edu/~green/papers/pods07.pdf

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P02: Occurrence Semantics and the Concurrent React Adapter

*Make mounted denotations explicit under speculation, hydration, virtualization, and stale events*

| Field | Assignment |
|---|---|
| Project | **P02: Occurrence Semantics and the Concurrent React Adapter** |
| Track | Semantic foundations / runtime boundary |
| Suggested team | 1-2 students comfortable with React internals and operational semantics |
| Nominal duration | 8-10 weeks |
| Primary result | A renderer-independent occurrence model plus a React adapter whose committed registrations refine that model. |

### Executive framing

A semantic subject may have many visual occurrences, and a React render may construct trees that never commit. A PBUI fails if it registers semantics during speculative render, keeps retired nodes selectable, or treats virtualized absence as proof that a subject does not exist.

This project defines occurrence identity, denotation, visibility, addressability, and lifecycle independently of React, then treats React as an implementation that must refine the abstract lifecycle. The core result is a precise rule for when an occurrence can witness selection and when an event must be revalidated.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- What is the difference among rendered, committed, visible, addressable, and selectable?
- How should occurrence identity behave across remounting, reordering, hydration, and hidden trees?
- Can registration be commit-causal without undocumented React timing?
- How should stale pointer and keyboard events be rejected and explained?
- What does virtualization mean for occurrence-required selectors?
- Can the adapter be tested against an abstract scheduler?

### Falsifiable hypotheses

- A lifecycle of absent, speculative, committed, and retired is sufficient for core safety, with visibility separate.
- Occurrence IDs must differ from React keys and include a generation or lease.
- Activation-time revalidation is required even if sensitivity was previously correct.
- A small renderer contract can support React, server rendering, and non-DOM renderers.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- Reimplementing React reconciliation.
- Defining subject identity.
- Designing the selector language.
- Making unmounted virtualized subjects occurrence-selectable.
- Premature registry optimization.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

Let $O$ be occurrence identities and $S$ subjects. A denotation relation $\operatorname{denotes}\subseteq O\times S$ associates an occurrence with a subject. Lifecycle is a labeled transition system

$$\textsf{Absent}\to\textsf{Speculative}\to\textsf{Committed}(e)\to\textsf{Retired}.$$

Visibility, focusability, and hit-testability are observations, not lifecycle states. An activation carrying occurrence $o$ and generation $e$ is valid only when

$$\operatorname{currentEpoch}(o)=e\land\operatorname{committed}(o)\land\operatorname{denotes}(o,s).$$

The React adapter is evaluated as a refinement mapping from renderer traces to this abstract machine. Abandoned renders must map to no committed semantic resource.

### Minimum API and executable artifact

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

### Work packages

#### Abstract lifecycle

Define states, epochs, leases, denotation, visibility, and revalidation without React.

#### React adapter

Implement commit-time registration and cleanup; test Strict Mode, remounts, transitions, Suspense-like delay, and hydration.

#### Adversarial scheduler

Interleave render proposals, commits, retirements, and events to generate counterexamples.

#### Virtualization semantics

Demonstrate subject existence, registered occurrence, visible occurrence, and mounted-required selection as separate facts.

#### Accessible activation

Produce one semantic activation path for keyboard and pointer and test ARIA/focus consistency.

### Required experiments

#### Render-time versus commit-time registration

Force abandoned renders and compare ghost occurrences and stale selections.

#### Generation strategy

Compare stable IDs, React keys, monotone generations, and lease tokens under rapid remount.

#### Virtualized selection

Evaluate mounted, scrolled-out, remounted, and filtered-away candidates.

#### Stale event race

Queue activation, retire or retarget, then deliver; require typed rejection and evidence.

### Proof and validation obligations

- Speculative render creates no committed occurrence.
- Lease retirement is idempotent.
- Stale generation cannot activate.
- One subject may have many occurrences.
- React key reuse cannot inherit old denotation.
- Keyboard and pointer share revalidation.
- Snapshots are transactionally coherent.
- Unmounting one occurrence does not retire siblings.

### Measurements to report

- Ghost/stale count under generated traces.
- Registration churn per commit.
- Selection latency at 10, 1,000, and 100,000 occurrences.
- Retained memory after mount cycles.
- Keyboard completion and focus defects.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export immutable occurrence snapshots, deltas, leases, and activation revalidation. Selectors may consume snapshots as facts but may not inspect React hooks or DOM nodes. State whether visibility and geometry are authoritative, advisory, or unavailable in non-browser interpreters.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Registering in render because simple tests pass.
- Equating visibility with existence.
- Assuming undocumented cleanup timing.
- Using React key as global occurrence identity.
- Testing only final DOM snapshots.

### Stretch directions

- Composite occurrences with semantic subregions.
- A second non-React renderer.
- TLA+ or Lean lifecycle refinement.
- Safe semantic annotations for SSR/hydration.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Lifecycle and adversarial examples. |
| Weeks 2-3 | Registry and React adapter. |
| Week 4 | Adversarial scheduler. |
| Weeks 5-6 | Virtualization, stale events, accessibility. |
| Weeks 7-8 | Measurement and report. |
| Weeks 9-10 | Optional refinement proof. |

### Selected readings

1. Neelakantan R. Krishnaswami and Nick Benton. "A Semantic Model for Graphical User Interfaces." ICFP 2011. https://www.cl.cam.ac.uk/~nk480/
2. Patrick Bahr, Christian Graulund, and Rasmus Ejlers Møgelberg. "Simply RaTT." 2019. https://arxiv.org/abs/1903.05879
3. J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." Theoretical Computer Science 249, 2000. https://ir.cwi.nl/pub/48/0048D.pdf

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P03: Inspectable Typed Selectors and Selection Evidence

*Replace opaque acceptance lambdas with a small query language whose results explain themselves*

| Field | Assignment |
|---|---|
| Project | **P03: Inspectable Typed Selectors and Selection Evidence** |
| Track | Query semantics |
| Suggested team | 1-2 students with programming-languages, database, or type-system experience |
| Nominal duration | 8-10 weeks |
| Primary result | A typed selector AST, reference evaluator, and proof-relevant candidate format with a controlled foreign-predicate boundary. |

### Executive framing

Arbitrary JavaScript predicates are convenient but opaque: dependencies, serialization, optimization, replay, and explanation are unavailable. This project finds the smallest inspectable language that can express practical requests such as "choose an active numeric field from the current document, witnessed by a mounted occurrence."

The aim is not SQL in TypeScript. It is a typed semantic request with a denotation, evidence, a separate ranking policy, and an explicit escape hatch for foreign predicates.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- What core syntax captures practical selection while remaining small enough for structural induction?
- Should occurrence constraints be relations, modal operators, or a separate phase?
- How do parameters, context, and authority facts enter the query?
- What evidence explains acceptance and rejection?
- How should unknown or pending differ from false?
- Which optimizations preserve evidence and deterministic ranking?

### Falsifiable hypotheses

- Conjunction, disjunction, typed atoms, equality, bounded negation, existential variables, and occurrence predicates cover most selectors.
- Truth and ranking should be separate.
- Three-valued results are more robust for remote or leased facts.
- Foreign predicates remain usable when dependency, purity, timeout, and explanation assumptions are explicit.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- Recursive rules.
- A full cost-based optimizer.
- Proving arbitrary JavaScript.
- The full operation/capability system.
- Serializing foreign closures.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

A typing judgment $\Gamma\vdash q:\operatorname{Query}(s)$ states that $q$ returns subjects of sort $s$. Its proof-relevant denotation is

$$\llbracket q\rrbracket_{D,\rho}\subseteq\operatorname{SubjectRef}(s)\times\operatorname{Evidence}.$$

Evidence records successful facts, equalities, occurrence witnesses, and foreign assumptions. Negative explanations may be partial and must be labeled as such. If three-valued semantics is used, define an information order such as $\textsf{unknown}\sqsubseteq\textsf{true}$ and $\textsf{unknown}\sqsubseteq\textsf{false}$ while keeping truth order separate. Negation must not silently treat unknown as false.

### Minimum API and executable artifact

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

### Work packages

#### Core language

Define a typed AST and builder; encode convenience forms as derived syntax.

#### Reference semantics

Evaluate finite facts and occurrence snapshots while preserving derivations.

#### Foreign boundary

Represent dependency, purity, timeout, cache, and explanation claims as assumptions.

#### Ranking layer

Order candidates by a separate stable policy; test locality, proof cost, and authority strength.

#### Explanation UI

Show why one occurrence is selectable, why another is not, and where evidence is foreign.

### Required experiments

#### Coverage study

Encode at least 25 realistic selectors and classify foreign or recursive needs.

#### Lambda comparison

Compare opaque callbacks for dependency extraction, replay, explanation, and optimization.

#### Evidence cost

Measure no evidence, minimal evidence, and complete derivations.

#### Three-valued interaction

Compare disabled, optimistic, and explicit pending behavior for remote facts.

### Proof and validation obligations

- Well-typed selectors return only their declared sort.
- Every accepted candidate has a valid derivation or labeled foreign assumption.
- Core evaluation is deterministic for fixed inputs and ranking.
- Dependency extraction is sound.
- Normalization preserves denotation.
- Ranking does not alter truth.
- Foreign timeout/exception is typed.
- Commit revalidation detects revision change.

### Measurements to report

- Core-language coverage.
- Evaluation latency by fact/occurrence count.
- Evidence size and rendering time.
- Dependency precision and false invalidation.
- User comprehension of false/unknown/pending.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export the versioned AST, type environment, dependency set, candidate/evidence schema, pure evaluator, selector corpus, and golden derivations. Foreign nodes serialize as stable IDs plus assumption metadata, never source strings. P04, P11, P14, and P15 should be able to implement independent evaluators.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Unprincipled AST growth.
- Claiming complete rejection explanations from one failed branch.
- Mixing ranking into truth.
- Treating foreign exceptions as false.
- Executing host control flow in a builder that should construct syntax.

### Stretch directions

- Certified normalization.
- Modal operators for mounted/visible/local/authoritative facts.
- Interactive query holes.
- Compile a subset to SQL or Datalog.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Selector corpus and syntax. |
| Weeks 2-3 | Typed AST and evaluator. |
| Week 4 | Evidence and foreign boundary. |
| Weeks 5-6 | Ranking, explanations, generated tests. |
| Weeks 7-8 | Coverage and three-valued study. |
| Weeks 9-10 | Optional certification. |

### Selected readings

1. Michael Arntzenius and Neelakantan R. Krishnaswami. "Datafun: A Functional Datalog." ICFP 2016. https://www.rntz.net/files/datafun.pdf
2. Todd J. Green, Grigoris Karvounarakis, and Val Tannen. "Provenance Semirings." PODS 2007. https://web.cs.ucdavis.edu/~green/papers/pods07.pdf
3. Patrick Cousot and Radhia Cousot. "Abstract Interpretation Frameworks." Journal of Logic and Computation 2(4), 1992. https://www.di.ens.fr/~cousot/publications.www/CousotCousot-JLC-n2--3-p103--179-1992.pdf

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P04: Recursive Rules, Fixed Points, and Provenance

*Study semantic closure, stratified negation, convergence, and proof-relevant recursive results*

| Field | Assignment |
|---|---|
| Project | **P04: Recursive Rules, Fixed Points, and Provenance** |
| Track | Query semantics / formal foundations |
| Suggested team | 1-2 students with logic, databases, order theory, or semantics experience |
| Nominal duration | 9-11 weeks |
| Primary result | A finite relational rule engine with explicit least-fixed-point semantics, provenance, and an optimized evaluator checked against the reference closure. |

### Executive framing

Several PBUI properties are recursive: permission inheritance, linked-view reachability, pipeline ancestry, component containment, and action-table inheritance. Ad hoc graph walks scatter recursion policy through code and make cycles, negation, and explanations difficult to reason about.

This project builds the recursive layer independently of selector syntax. It must clarify when finite iteration is enough, when monotonicity is required, where stratified negation is safe, and what transfinite iteration contributes to metatheory without pretending a finite browser should execute through large ordinals.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- Which PBUI relations genuinely require recursion?
- What positivity or stratification restrictions give predictable least-fixed-point semantics?
- How should deletion and changing facts be represented without hiding nonmonotonicity?
- Can recursive provenance remain finite, useful, and cycle-aware?
- What is the smallest convergence class the API should admit?
- How can semi-naive or differential evaluation be checked against reference closure?

### Falsifiable hypotheses

- Positive finite Datalog-style rules cover most recursive PBUI relations.
- Stratified negation is sufficient for practical exclusions but belongs outside the monotone core.
- Transfinite induction is mainly metatheoretic; executable fixtures should converge in finitely many stages.
- Provenance DAGs with cycle summaries are more useful than expanded proof trees.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- A general theorem prover.
- Unrestricted higher-order recursion.
- Assuming every recursive program terminates.
- Production incremental maintenance.
- Using transfinite language without identifying a lattice and operator.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

Let $F$ be finite possible ground facts and $L=\mathcal P(F)$ ordered by inclusion. A positive rule set $R$ induces an immediate-consequence operator $T_R:L\to L$. Positivity gives

$$X\subseteq Y\implies T_R(X)\subseteq T_R(Y).$$

The intended closure is the least fixed point

$$\mu T_R=\bigcap\{X\mid T_R(X)\subseteq X\}.$$

For finite $F$, iteration from $\varnothing$ stabilizes finitely. The report should still explain the ordinal construction

$$X_0=\bot,\quad X_{\alpha+1}=T_R(X_\alpha),\quad X_\lambda=\bigvee_{\beta<\lambda}X_\beta.$$

Provenance may use a semiring or proof algebra, but must state whether it represents all, one, minimal, or cyclicly summarized derivations.

### Minimum API and executable artifact

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

### Work packages

#### Rule kernel

Define typed relation symbols, variables, positive rule bodies, and a direct stage evaluator.

#### Convergence analysis

Implement finite-domain bounds, cycle diagnostics, and explicit budget/nonconvergence outcomes.

#### Stratified layer

Add stratified negation with a dependency checker and compare it with explicit positive revoked/hidden relations.

#### Provenance

Implement at least two representations and explanations for connectivity or inherited authority.

#### Optimized evaluator

Implement semi-naive evaluation and differential-test it against stage semantics.

### Required experiments

#### Recursive corpus

Model connectivity, permission inheritance, component ancestry, and pipeline reachability.

#### Stage-growth study

Generate chains, diamonds, dense components, and cycles; record stages, facts, and provenance growth.

#### Negation failures

Construct unstratified examples and demonstrate ambiguity or nonmonotonicity.

#### Provenance usability

Compare proof trees, DAGs, and path summaries for developer diagnosis.

### Proof and validation obligations

- The positive consequence operator is monotone.
- Reference closure is a fixed point containing base facts.
- Finite stages either add a fact or terminate.
- Semi-naive and reference closures are extensionally equal.
- Every derived fact has valid provenance.
- Negative dependency cycles are rejected.
- Rule insertion order does not change extensional results.
- Budget exhaustion is not logical falsehood.

### Measurements to report

- Stages and facts by graph family.
- Reference versus semi-naive time and allocation.
- Provenance size and explanation latency.
- Positive/stratified corpus coverage.
- Diagnosis accuracy by provenance format.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export typed relation declarations, checked rule modules, closure snapshots, stage traces, and provenance DAGs. P03 consumes closure as extensional facts; P11 compares incremental results; P14 receives a golden finite rule corpus. Consumers may not depend on worklist order or internal fact IDs.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Worklist algorithm without denotation.
- Treating budget exhaustion as empty result.
- Negation through foreign callbacks while claiming monotonicity.
- Infinite/exponential proof-tree expansion.
- Invoking ordinals without a concrete closure operator.

### Stretch directions

- Provenance semirings for derivation costs.
- Formalize positive fixed-point soundness.
- Well-founded semantics as a separate extension.
- Infer finite-domain convergence bounds.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Relation corpus and semantics. |
| Weeks 2-3 | Reference fixed point. |
| Week 4 | Stratification and failures. |
| Weeks 5-6 | Provenance study. |
| Weeks 7-8 | Semi-naive evaluator. |
| Weeks 9-11 | Formalization and report. |

### Selected readings

1. Alfred Tarski. "A Lattice-Theoretical Fixpoint Theorem and Its Applications." Pacific Journal of Mathematics 5(2), 1955. https://msp.org/pjm/1955/5-2/pjm-v5-n2-p11-s.pdf
2. Michael Arntzenius and Neelakantan R. Krishnaswami. "Datafun: A Functional Datalog." ICFP 2016. https://www.rntz.net/files/datafun.pdf
3. Todd J. Green, Grigoris Karvounarakis, and Val Tannen. "Provenance Semirings." PODS 2007. https://web.cs.ucdavis.edu/~green/papers/pods07.pdf

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P05: Operations, Capabilities, and Invariant-Preserving Affordances

*Derive visible actions from explicit transition specifications and authority evidence*

| Field | Assignment |
|---|---|
| Project | **P05: Operations, Capabilities, and Invariant-Preserving Affordances** |
| Track | Operations and authority |
| Suggested team | 1-2 students with security, PL, or transactional-systems experience |
| Nominal duration | 8-10 weeks |
| Primary result | An operation model separating menu affordances from authoritative transitions and making preconditions, effects, and invariants explicit. |

### Executive framing

A menu item is not an operation. It is a visual affordance suggesting an operation may be attempted. Between rendering and activation, state, authority, and revision can change. A robust PBUI therefore needs authoritative operation specifications and commit-time checks, not callbacks captured when a menu opens.

This project studies operation schemas, capability evidence, effect footprints, transactions, typed failures, and invariant preservation. It should expose why an action is offered and why a later commit can still be rejected.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- What belongs in an operation specification versus an affordance?
- How should capability evidence be scoped, leased, and rechecked?
- Can effect footprints support invariant modularity and incremental invalidation?
- How should optimistic UI represent later rejection?
- Which invariants require coordination or authority?
- Can operation composition preserve useful contracts?

### Falsifiable hypotheses

- Affordances should be pure derived data over operation specs, subjects, context, and capability evidence.
- Authoritative handlers must recheck preconditions at commit revision.
- Declared footprints materially improve testing and incremental recomputation.
- Typed rejection outcomes improve recovery compared with exceptions.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- A complete authorization infrastructure.
- Encoding all business logic in a theorem prover.
- UI visibility as authority.
- Cross-replica invariant preservation.
- Coupling operations to React or menus.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

Model operation $O$ with input $I_O$, precondition $P_O$, transition relation $\tau_O$, postcondition $Q_O$, and effect footprint $E_O$:

$$P_O\subseteq\Sigma\times I_O,\qquad \tau_O\subseteq\Sigma\times I_O\times\Sigma.$$

Capability evidence has the form $e:\operatorname{Can}(p,O,i,\sigma,r)$ for principal, input, state, and revision/lease. It supports offering an affordance but does not guarantee future success. For invariant $Inv$:

$$Inv(\sigma)\land P_O(\sigma,i)\land\tau_O(\sigma,i,\sigma')\implies Inv(\sigma').$$

Label whether this is proved, model-checked, property-tested, or merely checked at runtime.

### Minimum API and executable artifact

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

### Work packages

#### Operation schema

Define inputs, preconditions, outcomes, effects, footprints, revisions, and idempotency independently of UI.

#### Capability evidence

Implement issuance and explanation with principal, scope, expiry/revision, and provenance.

#### Transactional executor

Recheck preconditions, apply effects atomically, and record replayable traces.

#### Affordance derivation

Derive labels, enabled/pending state, and reasons without capturing mutation callbacks.

#### Invariant laboratory

Implement document, port compatibility, audit, and role invariants; generate races and stale intents.

### Required experiments

#### TOCTOU comparison

Compare callback capture, capability-only commit, and full revalidation under randomized changes.

#### Failure UX

Compare disabled, pending, optimistic, and reject-after-click presentations.

#### Footprint precision

Measure invalidation and invariant cost with absent, broad, and precise footprints.

#### Operation composition

Compose two operations transactionally and test contract/explanation clarity.

### Proof and validation obligations

- No affordance without displayed-snapshot evidence.
- Commit rechecks authoritative preconditions.
- Failed operations expose no partial effects.
- Fixture invariants hold after success.
- Effect traces cover the declared footprint.
- Expiry/revocation is a typed rejection.
- Duplicate non-idempotent commit is detected or governed.
- Labels do not determine authority.

### Measurements to report

- Stale-intent and false-authorization rates.
- Invariant cost by footprint precision.
- Affordance derivation latency.
- Recovery success after rejection.
- Trace size and replay determinism.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export immutable operation specs, affordances, capability evidence, intents, typed results, footprints, and transaction traces. P09/P10 may request operations but receive no mutable store. P11 may use footprints. P12 may classify coordination requirements. Stable IDs and schemas, not labels, form the boundary.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Embedding callbacks in menu records.
- Treating old capabilities as irrevocable.
- Incomplete footprints.
- Disabled UI as security boundary.
- Checking invariants after partial mutation.

### Stretch directions

- Refinement proof for one operation.
- Capability delegation/attenuation.
- Compensating operations without claiming inverses.
- Generate audit policy and docs from specs.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Operation and invariant corpus. |
| Weeks 2-3 | Schema, capabilities, executor. |
| Week 4 | Affordance derivation. |
| Weeks 5-6 | Race and invariant lab. |
| Weeks 7-8 | UX and footprint experiments. |
| Weeks 9-10 | Report and proof stretch. |

### Selected readings

1. Jonathan Haas et al. "LoRe: A Programming Model for Verifiably Safe Local-First Software." ECOOP 2023. https://drops.dagstuhl.de/opus/volltexte/2023/18205/pdf/LIPIcs-ECOOP-2023-12.pdf
2. Patrick Cousot and Radhia Cousot. "Abstract Interpretation Frameworks." Journal of Logic and Computation 2(4), 1992. https://www.di.ens.fr/~cousot/publications.www/CousotCousot-JLC-n2--3-p103--179-1992.pdf
3. Gordon Plotkin and Matija Pretnar. "Handlers of Algebraic Effects." ESOP 2009. https://homepages.inf.ed.ac.uk/gdp/publications/Effect_Handlers.pdf

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P06: Typed Ports and the Binding Quotient Compiler

*Give the PortBindingResolverRegistry a precise quotient, coequalizer, and runtime projection semantics*

| Field | Assignment |
|---|---|
| Project | **P06: Typed Ports and the Binding Quotient Compiler** |
| Track | Open systems / wiring |
| Suggested team | 1-2 students with category theory, type systems, graph algorithms, or formal methods experience |
| Nominal duration | 9-11 weeks |
| Primary result | A typed wiring compiler that turns identity-link equations into canonical binding classes and proves linked ports observe one runtime resource. |

### Executive framing

"Link these views" is underspecified. For an identity link, distinct local port occurrences are declared to denote one global binding. In finite sets this is a quotient; more generally it is the coequalizer of endpoint maps. The runtime then interprets each quotient class as a shared cell or resource.

This project gives that statement executable content in a small `PortBindingResolverRegistry` independent of union-find, persistent IDs, React, and Redux. It must confront dynamic unlinking, type compatibility, provenance, topology edits, and the fact that a quotient has no canonical inverse.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- What precisely are port occurrence, contract, identity link, binding class, and projection?
- Which contract fields must match definitionally for identity linking?
- How can persistence be stable while insertion order is irrelevant?
- What universal property is useful to downstream interpreters?
- How should unlink allocate and initialize new bindings?
- Can dynamic recompilation preserve unaffected resources?
- Where does coequalizer semantics stop and synchronization policy begin?

### Falsifiable hypotheses

- Identity links should compile to a typed equivalence relation rather than pairwise callbacks.
- Union-find can refine quotient semantics while external binding IDs are assigned separately.
- Universal factorization gives a useful plugin/runtime boundary.
- Unlinking needs provenance and explicit initialization because quotienting is not reversible.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- Transformed or bidirectional mappings as identity.
- Whole component composition.
- Claiming quotienting defines scheduling, ownership, or concurrency.
- Raw TypeScript payload equality as semantic compatibility.
- A production distributed topology service.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

For contract $\tau$, let $P_\tau$ be local port occurrences and $R_\tau$ link declarations with endpoint maps

$$s_\tau,t_\tau:R_\tau\rightrightarrows P_\tau.$$

The compiler forms a coequalizer $q_\tau:P_\tau\to Q_\tau$ satisfying $q_\tau\circ s_\tau=q_\tau\circ t_\tau$. In finite sets, $Q_\tau$ is the quotient by the generated equivalence relation. A runtime interpretation

$$v_\tau:Q_\tau\to\operatorname{Resource}(\tau)$$

gives each local port observation $v_\tau\circ q_\tau$. Equal projections therefore observe the same generated resource. The report must state the chosen category or typed fiber and keep authority, temporal mode, and multiplicity in compatibility checks.

### Minimum API and executable artifact

```ts
const doc = portContract<DocumentId>({semantic:"primary-document",mode:"read-write-cell",authority:"workspace",multiplicity:"one"});
const plan = bindings()
  .declare(chart.port("document",doc))
  .declare(pipeline.port("document",doc))
  .identify(chart.port("document"),pipeline.port("document"))
  .compile();
plan.bindingOf(chart.port("document"));
plan.allocate(interpreter);
```

Expose `bindings.check-link`, `bindings.compile`, `bindings.explain`, `bindings.edit`, and `bindings.allocate`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

### Work packages

#### Typed contracts

Define semantic tag, payload sort, mode, authority, multiplicity, update algebra, and lifetime; identify identity-compatible fields.

#### Reference quotient

Implement transparent equivalence closure with classes, projections, and link provenance.

#### Optimized compiler

Implement union-find or another structure and differential-test it against the reference partition.

#### Runtime projection

Allocate one shared cell per class and typed projections to widgets.

#### Dynamic topology

Specify link, merge, unlink, component removal, reload, and value initialization.

#### Mechanized core

Formalize relation-to-quotient and linked-observation theorems in Lean/Agda/Coq/Isabelle or equivalent checked model.

### Required experiments

#### Algorithm equivalence

Generate typed graphs with duplicates, cycles, disconnected parts, and random insertion order.

#### Compatibility matrix

Use same payload types with different semantics, authority, and temporal modes; assess diagnostics.

#### Unlink policies

Compare copy-current, reset, history restore, and user choice; show none follows from quotient alone.

#### Binding stability

Edit unrelated topology and measure resource/subscription churn under external-ID strategies.

#### Widget projection demo

Render chart, pipeline, and table from projected bindings while displaying classes and values.

### Proof and validation obligations

- Every declared port belongs to one class.
- Every accepted identity link has compatible contracts.
- Linked endpoints project equally.
- Partition is independent of link order and duplicates.
- Every link-respecting interpretation factors through the quotient in the chosen category.
- All projections of a class observe one allocated resource.
- Unlinking has explicit initialization and does not claim inversion.
- Persistence preserves the relation up to ID renaming.
- Removing one port preserves a nonempty class.
- Type erasure cannot merge incompatible contracts.

### Measurements to report

- Compile/edit latency by graph size.
- Resource/subscription churn.
- Serialized topology size/stability.
- Compatibility diagnosis time.
- Formal proof coverage and assumptions.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export serializable contracts, port graph, link declarations, classes, projection map, provenance, and allocation interface. P07 can use this as identity-wiring backend; P08 must keep lenses separate; P12 replicates declarations and recompiles; P14 receives the formal kernel. Consumers may not depend on a union-find representative as persistent ID.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Calling union-find the semantics.
- Payload equality as full compatibility.
- Claiming atomic writes from shared classes alone.
- Deleting equivalence edges without preserving declarations.
- External IDs from unstable representatives.
- Unsynchronized component shadow values.

### Stretch directions

- Prove incremental recompilation.
- Generalize to typed graphs/categories.
- Generate checkable binding-plan certificates.
- Explore linearity/ownership for write ports.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Contract taxonomy and categorical statement. |
| Weeks 2-3 | Reference quotient. |
| Week 4 | Optimized compiler. |
| Weeks 5-6 | Projection and widget demo. |
| Week 7 | Dynamic topology. |
| Weeks 8-9 | Mechanized theorem. |
| Weeks 10-11 | Experiments and report. |

### Selected readings

1. John C. Baez and Kenny Courser. "Structured Cospans." Theory and Applications of Categories 35, 2020. https://math.ucr.edu/home/baez/structured.pdf
2. Joseph A. Goguen and Rod M. Burstall. "Institutions: Abstract Model Theory for Specification and Programming." JACM 39(1), 1992. https://cseweb.ucsd.edu/~goguen/pps/ins.pdf
3. J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." Theoretical Computer Science 249, 2000. https://ir.cwi.nl/pub/48/0048D.pdf

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P07: Open Components, Plugin Signatures, and Composition

*Specify independently developed UI components by typed boundaries and compose them through explicit wiring*

| Field | Assignment |
|---|---|
| Project | **P07: Open Components, Plugin Signatures, and Composition** |
| Track | Open systems / modularity |
| Suggested team | 1-2 students with module systems, category theory, architecture, or plugin-platform experience |
| Nominal duration | 9-11 weeks |
| Primary result | A component signature and plugin compiler separating interface gluing from behavior and testing associativity, compatibility, and schema evolution. |

### Executive framing

A component should not import another component's store, actions, or React context to participate in a workbench. It should expose a typed boundary and compose through explicit wiring. Structured cospans and pushouts offer one account of gluing open systems; algebraic specifications and institutions clarify independently named schemas and theories.

This project tests how much of that structure produces practical value in a TypeScript plugin platform. It must distinguish signature composition from runtime behavior and reject the mistake that a pushout automatically solves synchronization.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- What belongs in a component signature: subjects, facts, ports, operations, forms, effects, or all?
- Can composition be associative up to stable isomorphism in a serialized representation?
- How should name collisions and schema versions be diagnosed?
- When is pushout-like gluing appropriate, and when is an adapter required?
- How should a plugin declare authority, time, and update-algebra assumptions?
- Can harnesses be generated from signatures alone?

### Falsifiable hypotheses

- A compact declarative signature supports independent testing and composition better than framework-specific interfaces.
- Pushout-like gluing helps shared boundaries, while schema differences require explicit adapters.
- Composition should be associative up to canonical renaming, not byte-identical output.
- A signature checker reveals hidden architectural coupling before runtime.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- Defining all internal behavior.
- Category terminology without executable mapping.
- Same-named ports as automatically compatible.
- A package manager.
- Replacing binding compilation or link policies.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

Model a component with input boundary $I$, internal structure $G$, and output boundary $O$ as a cospan

$$I\longrightarrow G\longleftarrow O.$$

Compatible components glue along shared boundary $B$ using a pushout $G+_B H$. In finite sets or graphs this often means coproduct followed by quotienting the two images of $B$. This is structural composition, not a behavioral synchronization theorem.

A component signature may also be viewed as a theory with schema maps changing notation and models moving contravariantly by reduct. Use this only where it improves versioning or plugin compatibility.

### Minimum API and executable artifact

```ts
const Chart = componentSignature({
  name:"chart", version:"1.0.0",
  imports:[Document,RowSelection], exports:[ChartView,HighlightOperation],
  ports:{document:ioPort(PrimaryDocument),selection:outputPort(RowSelection)},
  assumptions:["workspace-authority","transactional-bindings"]
});
const workspace = composeComponents([instantiate(Chart,"chart-1"),instantiate(Pipeline,"pipeline-1")],wiring);
```

Expose `components.check`, `components.compose`, `components.explain-conflict`, `components.generate-harness`, and `components.serialize`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

### Work packages

#### Signature language

Define imported/exported sorts, relations, ports, operations, forms, effects, assumptions, and versions.

#### Structural composition

Implement reference composition with namespaces, canonical renaming, and explicit boundary identifications.

#### Compatibility and adapters

Diagnose sort, semantic tag, authority, and version mismatches; require explicit adapters.

#### Generated harnesses

Generate mock environments and contract tests from signatures.

#### Plugin laboratory

Build independently designed chart, pipeline, and table components and compose in several orders.

### Required experiments

#### Associativity study

Compose three components in different parenthesizations and compare canonicalized signatures and plans.

#### Name-collision corpus

Compare global names, namespaces, and explicit schema maps for overlapping independent schemas.

#### Adapter pressure test

Version document and selection contracts; classify mechanical versus semantic adaptation.

#### Independent implementation trial

Give only the signature to another developer and measure successful compatible implementation.

### Proof and validation obligations

- Composition preserves typed boundaries or returns typed conflict.
- Identity composition is neutral up to canonical renaming.
- Supported composition is associative up to explicit isomorphism.
- No name collision resolves silently.
- Adapters declare direction, information loss, and failure.
- Generated harnesses exercise all required imports/ports.
- Serialized workspaces retain provenance.
- Structural composition makes no behavioral guarantee by itself.

### Measurements to report

- Signature size/authoring overhead.
- Checker latency and diagnostic precision.
- Hidden dependencies found.
- Adapter count and human-decision fraction.
- Independent implementation success.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export signatures, schema maps, adapter declarations, canonical composition results, and generated contract tests. P06 supplies identity bindings; P08 supplies nonidentity link policies; P09 attaches behavior; P15 composes mocks from capsules. Mark definitional equalities, adapter-mediated relations, and unresolved obligations separately.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Manifest merely mirrors TypeScript.
- Pushout metaphor with object merge implementation.
- Strict associativity claimed despite unstable names.
- Hidden adapters.
- Plugins reaching around ports into shared stores.

### Stretch directions

- Formalize the fragment as structured cospans.
- Schema migration via Kan-extension-inspired adapters.
- Capability-aware boundaries.
- Generate integration documentation.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Component inventory and signature. |
| Weeks 2-3 | Reference composition. |
| Week 4 | Diagnostics/adapters. |
| Weeks 5-6 | Harnesses and independent plugins. |
| Weeks 7-8 | Associativity/versioning experiments. |
| Weeks 9-11 | Formal account and report. |

### Selected readings

1. John C. Baez and Kenny Courser. "Structured Cospans." Theory and Applications of Categories 35, 2020. https://math.ucr.edu/home/baez/structured.pdf
2. Joseph A. Goguen and Rod M. Burstall. "Institutions: Abstract Model Theory for Specification and Programming." JACM 39(1), 1992. https://cseweb.ucsd.edu/~goguen/pps/ins.pdf
3. Matthew Pickering, Jeremy Gibbons, and Nicolas Wu. "Profunctor Optics." 2017. https://arxiv.org/abs/1703.10857

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P08: Bidirectional Links and Consistency Restoration

*Distinguish identity links, directed transformations, lenses, and peer synchronization*

| Field | Assignment |
|---|---|
| Project | **P08: Bidirectional Links and Consistency Restoration** |
| Track | Synchronization semantics |
| Suggested team | 1-2 students with bidirectional programming, synchronization, or HCI experience |
| Nominal duration | 9-11 weeks |
| Primary result | A link-policy laboratory making consistency relations, repair direction, partiality, ambiguity, and lens laws explicit. |

### Executive framing

Many UI links are not identity. A table selection may induce a pipeline filter; a chart domain may summarize a richer query; a textual editor and structured form may encode the same concept differently. Equating these ports loses information or creates loops. A better model is a consistency relation with explicit restoration procedures.

This project builds a laboratory for identity sharing, directed derivation, and peer synchronization. Success means ambiguity, partiality, information loss, and conflict are explicit, not that every pair of models can be synchronized automatically.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- Which workbench links are identity, directed, asymmetric lenses, symmetric lenses, or replicated merge?
- Which round-trip laws fit each link?
- How should partial and ambiguous repairs appear to users?
- Can delta updates preserve intent better than replacement?
- How are feedback loops scheduled and stabilized?
- When should the system refuse a link?

### Falsifiable hypotheses

- A first-class link-mode distinction prevents equality mistakes and feedback bugs.
- Partial lenses with typed conflicts are more honest than total functions that guess.
- Delta-aware synchronization preserves selection/filter intent.
- Lens laws are necessary but do not replace conflict and provenance UX.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- Treating all links as lenses.
- Automatic arbitrary reconciliation.
- Using identity quotienting for unequal representations.
- Network replication.
- Assuming classical laws fit lossy domains unchanged.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

An asymmetric lens has $\operatorname{get}:S\to V$ and $\operatorname{put}:S\times V\to S$, with possible laws

$$\operatorname{get}(\operatorname{put}(s,v))=v\quad\text{and}\quad\operatorname{put}(s,\operatorname{get}(s))=s.$$

Peer synchronization begins with a consistency relation $R\subseteq A\times B$ and restoration functions that establish $R$ or return explicit conflict. The project must define distinct semantics for identity links, directed links, bidirectional laws, and replicated merge structures.

### Minimum API and executable artifact

```ts
type Repair<T> =
  | {kind:"updated";value:T;evidence:RepairEvidence}
  | {kind:"unchanged";value:T}
  | {kind:"conflict";choices:readonly RepairChoice[]}
  | {kind:"invalid";reason:string};
const rowSelectionFilter = symmetricLink({consistent,repairRight,repairLeft,laws:[stability,consistencyRestoration]});
```

Expose `links.check-policy`, `links.propagate`, `links.explain-repair`, `links.simulate-feedback`, and `links.run-laws`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

### Work packages

#### Link taxonomy

Classify at least 20 plausible PBUI links and preserve disputed cases.

#### Policy kernel

Implement identity reference, directed, asymmetric-lens, and symmetric-consistency policies with partial outcomes.

#### Law harness

Generate law tests with shrinkers and known counterexamples; separate domain equivalence from structural equality.

#### Scheduler

Implement deterministic propagation, transactions, loop detection, and stable-state reporting.

#### Conflict UI

Prototype automatic choice, ranked choices, explicit resolution, and refusal.

### Required experiments

#### Selection-to-filter study

Compare replacement, asymmetric lens, symmetric repair, and delta repair for add/remove/reorder.

#### Law versus usability

Create a lawful surprising lens and intuitive law-breaking link; evaluate failures.

#### Feedback cycle test

Compose links in cycles and measure convergence, oscillation, and diagnostics.

#### Ambiguity policy

Test automatic, ranked, dialog, and refuse policies for many-to-one inverse mappings.

### Proof and validation obligations

- Successful repair establishes consistency.
- Stable consistent states remain unchanged.
- Selected round-trip laws are stated and checked.
- Identity is not two recursive setters.
- Ambiguity and partiality are typed.
- Propagation terminates, stabilizes, or reports bounded failure.
- Information loss appears in evidence.
- Composition does not silently alter scheduling.

### Measurements to report

- Law violations and minimized examples.
- Propagation steps/convergence rate.
- Intent preservation under deltas.
- Conflict resolution success/time/reversal.
- Policy authoring and explanation complexity.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export policy metadata/IDs, inspectable consistency terms where possible, repair schemas, evidence, and law fixtures. Host callbacks are foreign assumptions. P06 owns identity classes; P07 declares compatible ports; P09 schedules link creation; P12 handles replicated state. Consumers rely on typed repair outcomes and declared laws, not hidden propagation order.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Choosing laws after tests.
- Structural equality for semantic equivalence.
- Arbitrary total repair.
- Feedback suppression via mutable flags.
- Calling replicated merge a lens.

### Stretch directions

- Delta/edit lenses.
- Inspectable profunctor optics.
- Mechanize one finite lens.
- Provenance through composed links.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Taxonomy/laws. |
| Weeks 2-3 | Policy kernel/law harness. |
| Week 4 | Scheduler. |
| Weeks 5-6 | Selection/filter experiments. |
| Weeks 7-8 | Conflict UI. |
| Weeks 9-11 | Composition and proof stretch. |

### Selected readings

1. J. Nathan Foster et al. "Combinators for Bidirectional Tree Transformations." TOPLAS 29(3), 2007. https://inria.hal.science/inria-00484971v1/document
2. Martin Hofmann, Benjamin C. Pierce, and Daniel Wagner. "Symmetric Lenses." POPL 2011. https://www.cis.upenn.edu/~bcpierce/papers/symmetric.pdf
3. Michael Johnson and Robert Rosebrugh. "Symmetric Delta Lenses and Spans of Asymmetric Delta Lenses." Journal of Object Technology 16(1), 2017. https://www.jot.fm/issues/issue_2017_01/article2.pdf
4. Matthew Pickering, Jeremy Gibbons, and Nicolas Wu. "Profunctor Optics." 2017. https://arxiv.org/abs/1703.10857

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P09: Coalgebraic Interaction Machines

*Represent long-running interaction by explicit observations, transitions, effects, and behavioral equivalence*

| Field | Assignment |
|---|---|
| Project | **P09: Coalgebraic Interaction Machines** |
| Track | Interaction semantics |
| Suggested team | 1-2 students with semantics, state machines, model checking, or UI architecture experience |
| Nominal duration | 8-10 weeks |
| Primary result | A small machine IR and runtime for PBUI workflows, with checks for safety, cancellation, resolution, and behavioral equivalence. |

### Executive framing

Workflows such as "choose source, choose target, validate, confirm, commit, or cancel" are ongoing processes. Nested callbacks and promises hide intermediate states, cancellation paths, stale resources, and liveness assumptions.

A coalgebraic view describes current observations and future transitions. Statecharts offer authoring syntax; labeled transition systems, bisimulation, and temporal properties support analysis. This project seeks the smallest useful machine model without becoming a general workflow engine.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- Which observations belong to the semantic machine versus rendering?
- Are effects transition outputs, handler commands, or state?
- How are cancellation, disposal, timeout, and nesting scoped?
- What fairness assumptions underlie liveness?
- Can callback and machine implementations be observationally compared?
- How do changing occurrence, authority, and binding snapshots enter the model?

### Falsifiable hypotheses

- A deterministic Mealy-style core with typed effects covers most local workflows.
- Hierarchical statecharts aid authoring; a flat normalized LTS aids checking.
- Bisimulation or trace equivalence can validate refactoring.
- Cancellation and stale rejection become easier to test as ordinary transitions.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- A business-process engine.
- All application state inside the machine.
- Liveness without fairness assumptions.
- Hidden side effects in transitions.
- Replacing effect handlers.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

A deterministic Moore machine is a coalgebra $\gamma:X\to O\times X^I$. An effectful Mealy form is

$$\delta:X\times I\to X\times E^*.$$

Define a labeled transition system. A relation $R\subseteq X\times Y$ is a bisimulation when related states have equivalent observations and transition to related states for corresponding events. Safety can be proved over reachable transitions; liveness requires explicit delivery, completion, and fairness assumptions.

### Minimum API and executable artifact

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

### Work packages

#### Machine kernel

Define state, event, observation, typed effects, terminality, and model snapshots with pure transitions.

#### Authoring syntax

Compile a statechart-like syntax to a normalized table with explicit priority.

#### Explorer/checker

Find dead states, double resolution, unhandled events, and selected temporal violations.

#### Runtime/inspector

Run with handlers and display state, enabled events, effects, and trace.

#### Callback comparison

Implement one workflow as callbacks and machine; compare failure injection and refactoring.

### Required experiments

#### Workflow corpus

Encode selection, port linking, validated drag/drop, command arguments, and confirmable operation.

#### Cancellation matrix

Inject cancel, disposal, timeout, and staleness at every state.

#### Model exploration

Generate finite environments and search for deadlock, double resolution, and unreachable states.

#### Behavioral comparison

Refactor state representation and test an explicit trace/bisimulation relation.

#### Phase visibility

Compare explicit phase, spinner, and no phase in user tasks.

### Proof and validation obligations

- Every state/event has transition, explicit ignore, or typed rejection.
- Terminal sessions resolve at most once.
- Cancellation is idempotent and releases resources.
- Disposed state emits no new user-visible effects.
- Stale resources are revalidated before commit.
- Replay is deterministic for fixed event/model traces.
- Liveness claims list fairness assumptions.
- Normalization preserves authoring semantics.

### Measurements to report

- State/transition count.
- Counterexamples found by exploration.
- Replay/comparison cost.
- Complexity versus callbacks.
- User understanding of phase/cancellation.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export normalized machine IR, event/observation/effect schemas, traces, model abstractions, and checker results. P10 supplies handlers; P02 activations; P03 selection requests; P05 operation intents; P06/P08 link effects. Guarantees such as determinism and terminality are relied upon only when declared and checked.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Async effects in transition functions.
- Coinductive claims from finite samples.
- Hidden environment globals.
- Ambiguous statechart priority.
- Undocumented ignored events.

### Stretch directions

- Finite bisimulation proof.
- SCXML compilation.
- Hierarchical/parallel states with precise priority.
- Abstract interpretation of possible effects and requested sorts.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Workflow corpus/semantics. |
| Weeks 2-3 | Kernel/syntax. |
| Week 4 | Explorer. |
| Weeks 5-6 | Runtime/cancellation. |
| Weeks 7-8 | Callback/user comparison. |
| Weeks 9-10 | Equivalence stretch. |

### Selected readings

1. J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." Theoretical Computer Science 249, 2000. https://ir.cwi.nl/pub/48/0048D.pdf
2. David Harel. "Statecharts: A Visual Formalism for Complex Systems." Science of Computer Programming 8, 1987. https://www.state-machine.com/doc/Harel87.pdf
3. W3C. "State Chart XML (SCXML): State Machine Notation for Control Abstraction." https://www.w3.org/TR/scxml/

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P10: Algebraic Interaction Programs and Effect Handlers

*Describe choosing, linking, performing, waiting, and cancellation independently of React and concrete stores*

| Field | Assignment |
|---|---|
| Project | **P10: Algebraic Interaction Programs and Effect Handlers** |
| Track | Interaction programming |
| Suggested team | 1-2 students with functional programming, effects, interpreters, or language tooling experience |
| Nominal duration | 8-10 weeks |
| Primary result | A typed interaction-program language with handlers for browser execution, deterministic simulation, tracing, and static effect analysis. |

### Executive framing

Promises sequence asynchronous work but do not expose which effects may occur, how cancellation scopes resources, how traces replay, or how one program can run in a browser and simulator. Algebraic effects separate requests from handlers that assign operational meaning.

This project tests whether a practical TypeScript authoring style can remain understandable while yielding inspectable effect signatures, deterministic interpreters, and explicit resource scopes.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- What are primitive PBUI effects?
- Should programs use ASTs, free monads, generators, async iterators, or final encodings?
- How are cancellation and cleanup scoped?
- Which equations should handlers preserve?
- Can effect summaries be inferred before execution?
- How do handler failure and resumption interact with P09-like machines?

### Falsifiable hypotheses

- A generator surface can compile to an inspectable program or resumable machine.
- Multiple handlers reveal assumptions hidden by direct Promise calls.
- Scoped resources/cancellation should be primitive constructs.
- A small signature supports useful static analysis despite foreign payloads.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- Unrestricted continuations.
- A general-purpose language.
- Replacing operation authority checks.
- Hiding all machine structure behind monadic notation.
- Unqualified commutativity laws for order-sensitive handlers.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

Let $\Sigma$ be an effect signature. A program may be represented by the free monad $F_\Sigma A$ generated by returns and effect requests with continuations. A handler interprets it into computation algebra $M$ while preserving return and substitution structure.

A generator surface may hide this construction, but the runtime must retain inspectable requests and resumptions. Define equations for return, sequencing, handler composition, cancellation, and scoped cleanup. Static analysis is another interpreter into an abstract domain of possible sorts, operations, ports, and effects.

### Minimum API and executable artifact

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

### Work packages

#### Effect signature

Define typed PBUI effects and result/error/cancellation semantics.

#### Authoring representation

Compare AST, generators, and final encoding; select an ergonomic surface with inspectable core.

#### Handlers

Implement deterministic, browser/mock, denial, trace, and static-summary handlers.

#### Resource scopes

Make leases, subscriptions, overlays, and cleanup explicit; inject failures at every suspension.

#### Machine lowering

Show how programs become resumable machines and where continuation state lives.

### Required experiments

#### Encoding comparison

Implement three workflows in Promise, AST, and generator styles.

#### Handler substitution

Run unchanged program against deterministic, browser, denial, timeout, and trace-only handlers.

#### Static summary accuracy

Compare predicted effects with executed traces on generated inputs.

#### Cancellation fault injection

Cancel/fail at each effect boundary and verify cleanup/terminal outcomes.

### Proof and validation obligations

- Deterministic handler yields deterministic interpretation.
- Every scoped resource releases on success, failure, and cancellation.
- Handler substitution cannot bypass mandatory authority effects.
- Replay reproduces request/response sequence for fixed answers.
- Static summaries overapproximate core effects.
- Foreign continuations are labeled.
- Nested cancellation policy is documented.
- Lowered machine resolves exactly once.

### Measurements to report

- Authoring size/failure-path count.
- Static-summary precision.
- Runtime suspension overhead.
- Cleanup failures under injection.
- Developer comprehension in code review.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export effect signature, program IR or normalized trace, effect summaries, handler contracts, and deterministic fixtures. P09 hosts resumable execution; P03/P05/P06/P08 provide semantic requests; P15 replays with deterministic handlers. Stable composition uses effect IDs and payload schemas, not generator internals.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Generators used as opaque coroutines.
- Handlers swallow denials.
- Assuming effects commute.
- Hidden acquisition in helpers.
- API too advanced for routine workflows.

### Stretch directions

- Proof-relevant handlers.
- Abstract interpretation of cancellation/liveness.
- Resumable server execution.
- Mechanize a tiny signature/handler theorem.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Effect corpus/encoding spike. |
| Weeks 2-3 | Core program/deterministic handler. |
| Week 4 | Browser/mock handlers. |
| Weeks 5-6 | Scopes/cancellation/lowering. |
| Weeks 7-8 | Static analysis/comparison. |
| Weeks 9-10 | Report/formal stretch. |

### Selected readings

1. Gordon Plotkin and Matija Pretnar. "Handlers of Algebraic Effects." ESOP 2009. https://homepages.inf.ed.ac.uk/gdp/publications/Effect_Handlers.pdf
2. Patrick Cousot and Radhia Cousot. "Abstract Interpretation Frameworks." Journal of Logic and Computation 2(4), 1992. https://www.di.ens.fr/~cousot/publications.www/CousotCousot-JLC-n2--3-p103--179-1992.pdf
3. J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." Theoretical Computer Science 249, 2000. https://ir.cwi.nl/pub/48/0048D.pdf

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P11: Incremental and Differential Evaluation

*Maintain semantic query results under change while retaining a transparent from-scratch meaning*

| Field | Assignment |
|---|---|
| Project | **P11: Incremental and Differential Evaluation** |
| Track | Runtime / optimization |
| Suggested team | 1-2 students with databases, incremental computation, compilers, or performance engineering experience |
| Nominal duration | 10-12 weeks |
| Primary result | A reference evaluator and an incremental runtime whose updates, deletions, evidence, and recursive results are continuously checked for from-scratch consistency. |

### Executive framing

A presentation-based system continuously changes. Occurrences mount and unmount, facts arrive from stores or servers, revisions advance, authorities are revoked, component topology changes, and recursive relations gain or lose support. Recomputing every selector and affordance from scratch is simple but may be too expensive. Ad hoc memoization is fast until a dependency, deletion, alias, or proof object is missed.

This project studies incremental evaluation as a semantic refinement rather than as a bag of caches. The reference meaning remains ordinary evaluation over a complete snapshot. The optimized engine consumes transactions of changes and must produce exactly the result that a fresh reference evaluation would produce, including retractions and explanation evidence. The study should determine which fragments are straightforward, which require stable names or logical time, and when a hybrid planner should abandon maintenance and recompute.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- What change algebra is suitable for facts, occurrences, aliases, authorities, binding topology, and revisions?
- How should deletions and negative information be represented so stale candidates and evidence are retracted correctly?
- Which selector and rule operators admit simple derivatives, and which require indexes, arrangements, or recomputation?
- How should stable semantic names interact with incremental caches without merging distinct subjects?
- Can provenance and explanations be maintained incrementally without unbounded retention?
- How are transactions, logical time, and recursive fixed points exposed without leaking runtime machinery into the semantic API?
- When should the planner choose from-scratch, incremental, or partially materialized execution?

### Falsifiable hypotheses

- A snapshot reference semantics plus transaction boundaries is sufficient to state a strong from-scratch-consistency property.
- Most practical PBUI selectors can be maintained using indexed relational changes; opaque predicates require declared dependencies or conservative invalidation.
- Stable names improve reuse but must be typed and revision-aware.
- Evidence can be maintained as reference-counted support DAGs more reliably than by caching rendered explanations.
- For small relations or high-churn updates, recomputation will outperform differential maintenance; a hybrid planner is necessary.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- Inventing a new general-purpose streaming database.
- Claiming incremental support for arbitrary JavaScript closures.
- Treating a cache hit as a semantic proof.
- Hiding transaction or disposal boundaries.
- Optimizing before a reference evaluator exists.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

Let $D$ be a semantic database and let $Q$ be a query or derived relation. A change $\Delta D$ is interpreted by a composition operation $D\oplus\Delta D$. An incremental evaluator computes a result change $\delta Q(D,\Delta D)$ satisfying

$$Q(D\oplus\Delta D)=Q(D)\oplus\delta Q(D,\Delta D).$$

This is **from-scratch consistency**. State the result carrier and update algebra explicitly: sets may use insertions and deletions, multisets may use integer weights, and proof-relevant results may use support counts or provenance expressions. For recursive rules, define logical timestamps or stage coordinates and state when the maintained fixed point agrees with the least fixed point of the updated database.

If a change action is used for higher-order or structured values, specify its laws rather than assuming subtraction exists. Stable names are observations used to align computations; prove or test that equal names imply the intended semantic reuse relation, not merely syntactic coincidence.

### Minimum API and executable artifact

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

### Work packages

#### Snapshot semantics

Implement a deliberately slow evaluator for the relevant P03/P04-style query and rule fragment; canonicalize outputs and evidence.

#### Change algebra

Define typed inserts, deletes, replacements, revisions, topology changes, transaction commits, and disposal; reject malformed retractions.

#### Incremental operators

Maintain selection, projection, union, join, antijoin or bounded negation, ranking, and proof support with explicit indexes.

#### Recursive maintenance

Implement a bounded positive recursive fragment using semi-naive or differential techniques and compare it with fresh closure.

#### Planner and diagnostics

Explain materialization, dependencies, indexes, estimated costs, invalidation, foreign fallbacks, and memory retention.

#### Benchmark and differential oracle

Generate workloads, replay traces, compare every committed state to the reference result, and minimize divergences.

### Required experiments

#### Scale and churn

Run 1k, 10k, and 100k fact/occurrence workloads under read-heavy, write-heavy, burst, and delete-heavy traces.

#### Naming ablation

Compare no stable names, semantic names, occurrence names, and deliberately colliding names; measure reuse and correctness.

#### Evidence strategies

Compare recomputed explanations, support counts, minimal-support DAGs, and complete provenance for update cost and memory.

#### Hybrid planning

Find crossover points between full recomputation, local invalidation, and differential maintenance; test plan stability.

#### Fault injection

Drop, duplicate, reorder, or partially apply internal changes and verify that transactions detect or expose divergence rather than silently committing it.

### Proof and validation obligations

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

### Measurements to report

- Commit and propagation latency distributions.
- Peak memory and retained support size.
- Number of touched facts/operators per change.
- From-scratch verification cost and divergence rate.
- Planner crossover accuracy.
- Subscription/resource leak count.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export the supported query/rule fragment, snapshot and change schemas, canonical result format, transaction semantics, plan explanation, subscriptions, and consistency reports. P03/P04 provide syntax and reference corpora; P06 contributes topology changes; P12 may feed replicated deltas; P14 may certify a small derivative fragment; P15 acts as independent oracle. Consumers must not depend on internal timestamp or arrangement representations.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Benchmarking only insertions.
- Using object identity as a stable name.
- Keeping obsolete provenance forever.
- Assuming deletions are inverse insertions in every carrier.
- Observing intermediate states.
- Optimized and reference evaluators sharing enough code to share the same bug.

### Stretch directions

- Proof-producing incremental plans.
- Adaptive materialization under workload change.
- Incremental three-valued remote facts.
- Worker or WASM execution with deterministic traces.
- A mechanized derivative theorem for one relational fragment.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Snapshot semantics and workload corpus. |
| Weeks 2-3 | Change algebra and basic operators. |
| Weeks 4-5 | Joins, negation, ranking, evidence. |
| Weeks 6-7 | Recursive maintenance. |
| Week 8 | Planner and diagnostics. |
| Weeks 9-10 | Benchmark and fault injection. |
| Weeks 11-12 | Report and proof stretch. |

### Selected readings

1. Frank McSherry et al. "Differential Dataflow." CIDR 2013. https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf
2. Mihai Budiu et al. "DBSP: Automatic Incremental View Maintenance for Rich Query Languages." PVLDB 16(7), 2023. https://www.vldb.org/pvldb/vol16/p1601-budiu.pdf
3. Yufei Cai et al. "A Theory of Changes for Higher-Order Languages." PLDI 2014. https://arxiv.org/abs/1312.0658
4. Matthew A. Hammer et al. "Adapton: Composable, Demand-Driven Incremental Computation." PLDI 2014. https://matthewhammer.org/adapton/adapton-pldi2014.pdf
5. Matthew A. Hammer et al. "Incremental Computation with Names." OOPSLA 2015. https://arxiv.org/abs/1503.07792

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P12: Local-First Replicated Bindings and Topology

*Separate convergence of replicated declarations from derived port equivalence and application invariants*

| Field | Assignment |
|---|---|
| Project | **P12: Local-First Replicated Bindings and Topology** |
| Track | Replication / coordination |
| Suggested team | 1-2 students with distributed systems, CRDTs, local-first software, or concurrency experience |
| Nominal duration | 10-12 weeks |
| Primary result | A replicated workspace model for link declarations, unlinking, values, deletion, and conflicts, with explicit convergence and coordination claims. |

### Executive framing

A local presentation-based workbench may be edited on several devices or by several collaborators. While disconnected, users can change selected documents, link or unlink ports, delete components, and revoke authority. Eventual delivery can make replicas converge, but convergence alone does not preserve typing, uniqueness, authorization, or user intent.

This project separates replicated **source declarations** from deterministic **derived structures**. In particular, replicas should exchange link and unlink facts or commands, not unstable union-find representatives. Each replica derives its port quotient from the same surviving declarations. The study must classify which invariants are coordination-free, which need conflict objects, and which require coordination or a redesign into monotone state.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- Which workspace facts are grow-only, retractable, ordered, or authority-sensitive?
- Should identity links be represented by edge sets, observed-remove sets, operation logs, epochs, or another structure?
- How should unlinking interact with concurrent linking and transitive groups?
- What policy should reconcile concurrent writes to a shared binding value?
- How do component deletion, tombstones, permission revocation, and schema migration affect derived bindings?
- Which invariants are invariant-confluent and which require coordination?
- How can the UI explain causal histories and unresolved intent rather than merely displaying a winning value?

### Falsifiable hypotheses

- Replicating link declarations and deriving equivalence classes is more stable than replicating quotient representatives.
- No single register policy is appropriate for all binding values; the port contract must choose LWW, multi-value, join, intent log, or coordinated update.
- Convergence and invariant preservation must be reported separately.
- A compact causal explanation substantially improves recovery from concurrent link/unlink and deletion conflicts.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- A production collaboration service.
- Assuming clocks are perfectly synchronized.
- Calling any merge function a CRDT without laws.
- Silent last-writer-wins for every semantic conflict.
- Replicating React component state.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

For state-based replication, use a join-semilattice $(L,\sqsubseteq,\sqcup)$ and inflationary local updates. Replica merge is $x\sqcup y$ and must be associative, commutative, and idempotent. Operation-based designs must state causal delivery and exactly-once or idempotence assumptions.

Let $E_r$ be the surviving typed link declarations at replica $r$. The derived binding partition is

$$Q_r = P/{\sim_{E_r}},$$

where $\sim_{E_r}$ is the least equivalence relation generated by valid declarations. The quotient is derived, not directly merged. For each safety invariant $I$, investigate invariant confluence: can all independently valid states merge to another state satisfying $I$ without coordination? A negative result should identify the minimal conflicting operations.

### Minimum API and executable artifact

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

### Work packages

#### State classification

Catalog topology, value, identity, authority, occurrence, and UI-only state; decide what is replicated and why.

#### Replicated topology

Implement at least two candidate designs for link/unlink declarations, derive typed partitions, and preserve causal provenance.

#### Value policies

Implement LWW, multi-value, join-semilattice, and intent-log policies behind explicit port contracts.

#### Invariant analysis

State typing, uniqueness, authority, deletion, and referential invariants; test or prove coordination requirements on bounded domains.

#### Conflict explanations

Expose concurrent operations, causal order, derived effect, policy, and available repairs in machine- and human-readable forms.

#### Partition simulator

Run deterministic and randomized network schedules with partitions, duplication, reordering, and delayed revocation.

### Required experiments

#### Concurrent topology matrix

Link A-B versus unlink B-C, overlapping links, repeated unlink, delete versus link, and component recreation with a new identity.

#### Concurrent value switch

Compare LWW, multi-value, join, and intent log when chart and pipeline select different documents offline.

#### Delete versus edit

Delete a document or component concurrently with selection, linking, operation commit, and alias creation.

#### Bounded invariant confluence

Enumerate small states and pairs of valid operations; find minimal merges violating each invariant.

#### Explanation study

Ask users to predict and repair outcomes from final value alone versus causal explanation.

### Proof and validation obligations

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

### Measurements to report

- Replica-state and operation-log growth.
- Merge/derived-partition latency.
- Conflict frequency by workload.
- Metadata overhead by policy.
- Convergence schedules explored.
- User repair time and correctness.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export the replica state schema, command/event schema, merge contract, derived link declarations, value-policy descriptors, conflicts, and causal explanations. P01 supplies subject identity; P05 authority and operation safety; P06 recompiles declarations into bindings; P08 handles unequal-view repair; P13 renders conflict explanations; P15 controls schedules. No consumer may infer semantic order from transport arrival order.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Equating eventual convergence with correct intent.
- Replicating implementation-generated class IDs.
- Using wall-clock LWW without acknowledging loss.
- Garbage collecting tombstones without a causal-stability argument.
- Authority checks made only when an affordance was rendered.
- Calling bounded enumeration a general proof.

### Stretch directions

- Delta-state CRDTs and compact causal contexts.
- Mechanized convergence for the topology carrier.
- Verified invariant-confluence checker on a bounded DSL.
- Local-first undo as compensating intent.
- Encrypted or partially replicated workspaces.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | State/invariant classification. |
| Weeks 2-3 | Replicated topology candidates. |
| Weeks 4-5 | Value policies and simulator. |
| Weeks 6-7 | Invariant-confluence study. |
| Weeks 8-9 | Conflict explanation and user study. |
| Weeks 10-12 | Optimization, report, formal stretch. |

### Selected readings

1. Marc Shapiro et al. "A Comprehensive Study of Convergent and Commutative Replicated Data Types." INRIA Research Report 7506, 2011. https://inria.hal.science/inria-00555588v1/document
2. Joseph M. Hellerstein and Peter Alvaro. "Keeping CALM: When Distributed Consistency Is Easy." CACM 63(9), 2020. https://arxiv.org/abs/1901.01930
3. Lindsey Kuper and Ryan R. Newton. "LVars: Lattice-Based Data Structures for Deterministic Parallelism." FHPC 2013. https://users.soe.ucsc.edu/~lkuper/papers/lvars-fhpc13.pdf
4. Jonathan Haas et al. "LoRe: A Programming Model for Verifiably Safe Local-First Software." ECOOP 2023. https://drops.dagstuhl.de/opus/volltexte/2023/18205/pdf/LIPIcs-ECOOP-2023-12.pdf

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P13: Explanation, Accessibility, and Proof-Relevant Interaction

*Project one semantic interaction state into pointer, keyboard, screen-reader, textual, and diagnostic experiences*

| Field | Assignment |
|---|---|
| Project | **P13: Explanation, Accessibility, and Proof-Relevant Interaction** |
| Track | Human factors / semantics |
| Suggested team | 1-2 students with HCI, accessibility, information visualization, or explainable-systems experience |
| Nominal duration | 8-10 weeks |
| Primary result | A renderer-neutral explanation model and accessible interaction laboratory for selection, authority, staleness, linking, conflicts, and machine phase. |

### Executive framing

A proof-relevant semantic kernel is useful only when users and developers can understand enough of its results to act. Color highlights alone cannot explain why a candidate is selectable, why an operation disappeared, which views will change after a link, or whether an unavailable result is false, unknown, pending, stale, unauthorized, ambiguous, or unsupported.

This project treats explanation and accessibility as semantic projections rather than decorations added after implementation. One normalized interaction state should support pointer, keyboard, screen reader, command palette, developer inspector, and trace report without giving each modality a different truth. The work must also identify where complete explanations are impossible or harmful and how to communicate bounded, partial, ranked, or foreign evidence honestly.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- What is the smallest renderer-neutral model of candidate, rejection, authority, staleness, binding, lens conflict, machine phase, and provenance?
- How should positive evidence and negative explanations differ?
- Can pointer, keyboard, screen-reader, and textual projections preserve the same semantic availability and commit validation?
- How should the UI distinguish false, unknown, pending, stale, unauthorized, ambiguous, and unsupported?
- What level of provenance is useful to end users versus developers?
- How can linked-view impact and conflict repair be previewed without overwhelming users?
- How should candidate ranking be explained without presenting rank as truth or certainty?

### Falsifiable hypotheses

- A normalized explanation tree with stable evidence IDs can support several modalities while preserving semantic consistency.
- Users recover from stale and ambiguous interactions more reliably when the system states the failed obligation and next action.
- Linked-state changes need an explicit affected-view preview; iconography alone is insufficient.
- Complete provenance is usually too detailed; layered summaries with drill-down are more effective.
- Accessibility testing will expose semantic inconsistencies that pointer-only testing misses.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- Automatically generating perfect natural-language explanations.
- Treating ARIA attributes as the entire accessibility problem.
- Claiming rejection explanations are complete when only one failing branch is known.
- A broad demographic study.
- Changing semantic truth in the renderer.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

Let an evaluator or machine produce an outcome $o$ together with evidence, missing obligations, or conflict information. Define a total projection

$$\operatorname{explain}:\operatorname{Outcome}\to\operatorname{ExplanationModel}.$$

The model should distinguish status from presentation and include stable references to semantic evidence. Each modality $m$ is an interpretation

$$\rho_m:\operatorname{ExplanationModel}\to\operatorname{RenderedExperience}_m.$$

State a cross-modality consistency relation: modalities may omit detail appropriate to their channel, but they must not disagree on candidate membership, enabled operation, authority requirement, current phase, or commit result. Where a negative explanation is incomplete, the model carries completeness metadata rather than implying a proof of nonexistence.

### Minimum API and executable artifact

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

### Work packages

#### Explanation schema

Define statuses, obligations, evidence references, affected resources, remedies, completeness, severity, and localization tokens.

#### Semantic projections

Build pointer, keyboard/listbox, screen-reader/live-region, command-palette, plain-text, and developer-inspector projections.

#### Accessible interaction lab

Implement all six shared traces with focus management, reading order, reduced motion, non-color cues, and commit-time revalidation.

#### Explanation variants

Compare terse, layered, provenance-first, remedy-first, and causal-timeline forms without changing underlying semantics.

#### User evaluation

Conduct a small preregistered formative study or structured expert review; report limitations and qualitative counterexamples.

### Required experiments

#### Selectable-state comprehension

Ask users to identify selectable and rejected occurrences and explain the decisive obligation.

#### Link visibility

Compare chain icon only, shared-label indicator, affected-view preview, and persistent topology inspector.

#### Commit rejection recovery

Revoke authority or stale an occurrence after rendering and measure recovery under generic versus proof-relevant messages.

#### Modality parity

Replay identical traces by pointer, keyboard, screen reader, and command palette; compare semantic event logs.

#### Ranking transparency

Show equal-truth candidates with different ranking reasons; test whether users mistake ordering for eligibility or confidence.

### Proof and validation obligations

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

### Measurements to report

- Task completion and error rate.
- Time to identify cause and remedy.
- Semantic-event parity across modalities.
- Accessibility audit findings.
- Explanation depth and interaction count.
- User confidence versus actual correctness.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export a versioned explanation schema, message-token catalog, modality-neutral interaction snapshot, rendered textual fixtures, semantic event traces, and study instruments. P03/P04 supply selection evidence; P05 authority; P06/P08 topology and conflicts; P09 machine phase; P12 causal history. P15 compares event logs. This project must not reach into subsystem internals when stable evidence references suffice.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Inventing friendly prose unsupported by evidence.
- Making disabled controls undiscoverable.
- Separate pointer and keyboard code paths.
- Overwhelming users with proof trees.
- Using ranking as a confidence score.
- Overclaiming from a small convenience sample.

### Stretch directions

- Verified cross-modality state projection for a finite core.
- Localization stress test including bidirectional text.
- Sonification or haptic projection.
- Adaptive explanation depth without changing semantic status.
- Screen-reader-accessible topology graph.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Status/explanation inventory. |
| Weeks 2-3 | Schema and text/inspector projections. |
| Weeks 4-5 | Accessible interaction lab. |
| Week 6 | Modality parity and audits. |
| Weeks 7-8 | User study. |
| Weeks 9-10 | Refinement and report. |

### Selected readings

1. Todd J. Green, Grigoris Karvounarakis, and Val Tannen. "Provenance Semirings." PODS 2007. https://web.cs.ucdavis.edu/~green/papers/pods07.pdf
2. Neelakantan R. Krishnaswami and Nick Benton. "A Semantic Model for Graphical User Interfaces." ICFP 2011. https://www.cl.cam.ac.uk/~nk480/
3. David Harel. "Statecharts: A Visual Formalism for Complex Systems." Science of Computer Programming 8, 1987. https://www.state-machine.com/doc/Harel87.pdf

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P14: Mechanized Semantic Kernel and Proof-Carrying Compilation

*Formalize a deliberately small PBUI core and connect checked theorems to executable binding and selection artifacts*

| Field | Assignment |
|---|---|
| Project | **P14: Mechanized Semantic Kernel and Proof-Carrying Compilation** |
| Track | Formal verification |
| Suggested team | 1-2 students with Lean, Coq, Agda, Isabelle, proof assistants, or mechanized semantics experience |
| Nominal duration | 11-13 weeks |
| Primary result | A proof-assistant development of typed subjects, positive selection, typed port equations, quotient bindings, and certificates checked by an executable bridge. |

### Executive framing

The broader PBUI architecture contains too many host-language, browser, network, and human factors to verify monolithically. A more credible strategy is to identify a small semantic kernel, mechanize its definitions and central theorems, and make optimized or foreign implementations produce artifacts checked against that kernel.

This project should resist two opposite failures: formalizing an elegant toy with no connection to the experimental API, and encoding the implementation so literally that the proof merely restates code. The target is a small model that makes sort safety, candidate soundness, generated link equivalence, and equal binding observations precise, then connects those results to a JSON or certificate format usable by P03, P06, and P15.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- What is the smallest kernel that captures typed subjects, facts, positive selectors, evidence, ports, link declarations, equivalence closure, and interpretation?
- Should bindings use quotients, canonical finite partitions, or both with an equivalence theorem?
- Which theorems express selector soundness without formalizing all JavaScript?
- How can an optimized compiler emit a certificate checked by the kernel rather than being trusted?
- What assumptions are needed to connect extracted or mirrored definitions to a TypeScript runtime?
- Which host features must remain foreign, and how are those assumptions represented?
- How should engineering claims map to theorem statements so proof scope is not overstated?

### Falsifiable hypotheses

- A sort-indexed finite kernel can prove the most important selection and identity-link properties with modest proof-assistant effort.
- Canonical partitions are executable and quotient types are conceptually clean; proving their correspondence yields a useful bridge.
- A binding compiler can emit a compact certificate consisting of a projection map plus edge checks.
- Selector soundness can be proved for a positive typed fragment while opaque predicates remain explicit assumptions.
- Mutation testing of certificates will expose whether the checker validates meaningful structure.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- Verifying React, browsers, Redux, network stacks, or arbitrary TypeScript.
- Formalizing all fifteen projects.
- Using `admit`, `sorry`, or unreported axioms in claimed theorems.
- Treating finite testing as a substitute for proof.
- Generating production code before the model stabilizes.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

Choose a proof assistant and define:

- semantic sorts $S$ and sort-indexed references $\operatorname{Ref}:S\to\mathsf{Type}$;
- finite typed facts and a positive query judgment;
- proof-relevant candidate derivations;
- port types and sort-indexed ports $\operatorname{Port}:S\to\mathsf{Type}$;
- typed link declarations and the generated equivalence relation $\sim$;
- either the quotient $Q_s=\operatorname{Port}(s)/{\sim}$ or a canonical finite partition;
- a binding interpretation $v_s:Q_s\to V_s$ and port observation $v_s\circ q_s$.

Representative target theorems are:

$$\operatorname{derive}(q,D,r,e)\Longrightarrow r\in\llbracket q\rrbracket_D,$$

$$p\sim q\Longrightarrow \operatorname{project}(p)=\operatorname{project}(q),$$

and therefore

$$p\sim q\Longrightarrow f(\operatorname{project}(p))=f(\operatorname{project}(q))$$

for any interpretation $f$. State theorem assumptions and computational relevance explicitly.

### Minimum API and executable artifact

```lean
inductive Sort | document | field | selection
inductive Port : Sort -> Type
inductive Linked : {s : Sort} -> Port s -> Port s -> Prop

abbrev Binding (s : Sort) := Quotient (portSetoid s)
def project {s} (p : Port s) : Binding s := Quotient.mk _ p

theorem linked_same_binding {s} {p q : Port s}
  (h : Linked p q) : project p = project q := Quotient.sound h

theorem linked_same_widget {p q : Port .document}
  (h : Linked p q) (f : Binding .document -> Widget) :
  f (project p) = f (project q) := congrArg f (linked_same_binding h)
```

Expose a checker command such as `pbui-kernel check binding-certificate.json` plus machine-readable theorem/build metadata.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

### Work packages

#### Kernel freeze

Write a one-page trusted-base and theorem inventory; choose finite representations, decidable equality, and foreign assumptions.

#### Mechanized definitions

Formalize sorts, references, facts, selectors, evidence, ports, links, equivalence closure, partitions/quotients, and interpretations.

#### Core theorems

Prove selector type/soundness, equivalence laws, linked-equal-projection, linked-equal-observation, and certificate soundness for the chosen fragment.

#### Executable certificate bridge

Define a language-neutral certificate; implement encoder from a small TypeScript or reference compiler and checker invocation.

#### Countermodel collaboration

Use failed proof attempts and finite counterexamples to refine P03/P06 contracts rather than weakening theorem statements silently.

#### Proof audit

Document trusted axioms, extraction/FFI boundary, theorem-to-claim map, proof statistics, and reproducible toolchain.

### Required experiments

#### Representation comparison

Compare quotient-based, representative-map, and canonical-partition encodings for proof effort, execution, and API clarity.

#### Certificate size/cost

Generate random typed port graphs and measure compiler certificate size and checker time.

#### Mutation test

Corrupt projection maps, edge justifications, sorts, class membership, and evidence; verify rejection and minimize accepted bad mutations if any.

#### API drift test

Change the external schema in controlled ways and record whether the bridge fails loudly or silently misinterprets it.

#### Selector corpus

Encode a small positive subset of shared selectors and compare checked derivations with an independent evaluator.

### Proof and validation obligations

- Claimed theorem files contain no unreported axioms, `sorry`, `admit`, or equivalent escape hatches.
- Ill-sorted identity links are unrepresentable or rejected before certificate acceptance.
- Every checked candidate derivation denotes a subject of the declared sort and satisfies the reference semantics.
- Generated linking is reflexive, symmetric, and transitive.
- Linked ports project to equal bindings and therefore have equal observations under any common interpretation.
- Every accepted binding plan satisfies every source identity equation.
- The certificate checker rejects incompatible sorts and malformed projections.
- The TypeScript/JSON bridge performs a clean, tested encoding rather than relying on unchecked object casts.
- Every theorem is mapped to an exact engineering claim and does not imply browser/runtime properties outside the model.
- All finiteness, decidability, and foreign-function assumptions are explicit.

### Measurements to report

- Definitions/theorems and proof lines by concept.
- Trusted axioms and executable bridge size.
- Certificate bytes and check time by graph size.
- Mutation rejection score.
- External scenarios represented without new axioms.
- Proof-maintenance cost under schema changes.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export proof source, pinned toolchain, theorem inventory, trusted-base report, executable checker, certificate schema, positive-selector subset, binding-plan subset, and golden accepted/rejected certificates. P03 and P06 produce artifacts; P11 may add a derivative certificate; P15 mutates and replays them. Downstream claims cite theorem names and assumptions, not the generic phrase "formally verified."

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- Proving a theorem about a model disconnected from artifacts.
- Encoding union-find internals as the mathematical definition.
- Hiding axioms in convenience libraries or extraction.
- Making evidence proof-irrelevant when downstream explanations need it.
- Overstating equal observations as synchronization or liveness.
- Letting proof scope expand until no executable result ships.

### Stretch directions

- Prove quotient/canonical-partition equivalence.
- Mechanize finite least-fixed-point closure for positive rules.
- Proof-producing selector normalization.
- Verified code extraction for the checker.
- A logical-relations bridge between an executable evaluator and denotation.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Kernel/theorem inventory. |
| Weeks 2-4 | Definitions and basic lemmas. |
| Weeks 5-7 | Selection and binding theorems. |
| Weeks 8-9 | Certificate bridge and mutation tests. |
| Weeks 10-11 | External corpus and proof audit. |
| Weeks 12-13 | Stretch theorem and report. |

### Selected readings

1. Alfred Tarski. "A Lattice-Theoretical Fixpoint Theorem and Its Applications." Pacific Journal of Mathematics 5(2), 1955. https://msp.org/pjm/1955/5-2/pjm-v5-n2-p11-s.pdf
2. Michael Arntzenius and Neelakantan R. Krishnaswami. "Datafun: A Functional Datalog." ICFP 2016. https://www.rntz.net/files/datafun.pdf
3. John C. Baez and Kenny Courser. "Structured Cospans." Theory and Applications of Categories 35, 2020. https://math.ucr.edu/home/baez/structured.pdf
4. J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." Theoretical Computer Science 249, 2000. https://ir.cwi.nl/pub/48/0048D.pdf

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

## P15: Conformance, Model-Based Testing, and Comparative Benchmarking

*Build the neutral harness that lets independently developed PBUI subsystems be substituted, stressed, and compared*

| Field | Assignment |
|---|---|
| Project | **P15: Conformance, Model-Based Testing, and Comparative Benchmarking** |
| Track | Validation / integration science |
| Suggested team | 1-2 students with testing research, property-based testing, benchmarking, or experimental-methods experience |
| Nominal duration | 9-11 weeks |
| Primary result | A black-box conformance laboratory with reference micro-models, generated traces, shrinking, metamorphic laws, reproducible benchmarks, and capability-aware reports. |

### Executive framing

Independent student teams will choose different languages, data structures, proof techniques, and UI frameworks. Direct source-level integration would reward accidental similarity and hide semantic disagreement. The research program therefore needs a neutral laboratory that compares observable claims through versioned traces and deliberately simpler reference models.

This project designs that laboratory. It must distinguish unsupported capability from rejection, crash, timeout, nondeterminism, and semantic disagreement. It should generate well-typed histories across subsystem boundaries, shrink failures while preserving prerequisites, and report what each artifact actually guarantees. The harness is also a check on the program design: if no stable observation boundary can be stated, the subsystem may not yet be sufficiently understood.

This is a bounded project. It should make one subsystem precise enough that later composition reveals real interface boundaries rather than accidental coupling.

### Research questions

- What is the smallest common protocol that permits meaningful comparison without becoming a lowest-common-denominator production API?
- Which observations are semantically relevant and which can be normalized away?
- What independent micro-models can serve as trustworthy oracles for identity, selection, closure, bindings, machines, and replication?
- How should generators maintain typing, revisions, authority, causal context, and reachability preconditions?
- Can shrinkers preserve the reason a cross-subsystem trace fails?
- Which metamorphic laws expose bugs without requiring one privileged implementation?
- How can performance be compared fairly across languages and architectures?

### Falsifiable hypotheses

- A JSONL protocol plus capability manifest is sufficient for first-pass black-box substitution.
- Small executable models catch more semantic mismatches than broad snapshots of production-like code.
- Metamorphic and differential testing complement formal proof by testing bridges and unsupported regions.
- Dependency-aware shrinking can turn long concurrent traces into comprehensible counterexamples.
- Benchmark reports should stratify guarantees before ranking throughput.

A negative result is acceptable when demonstrated rather than asserted.

### Explicit non-goals

- Declaring one architecture the winner from a single composite score.
- Using wall-clock microbenchmarks without warm-up, workload, or uncertainty.
- Depending on undocumented internal APIs.
- Normalizing away meaningful evidence, conflict, or status differences.
- Replacing project-specific proof and user studies.

### Shared laboratory setting

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

### Common artifact boundary

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

### Formal object of study

Model each artifact as a labeled transition system with requests $I$, internal state $X$, and observable responses $O$:

$$\delta:X\times I\to X\times O.$$

The harness compares observations under a declared equivalence or refinement relation rather than raw JSON equality. A canonicalization function may erase only fields proven or declared observationally irrelevant, such as generated request IDs.

Metamorphic relations include: duplicate and reordered identity links yield the same partition; permutation of positive base facts yields the same closure; deterministic machine replay yields the same normalized trace; and CRDT delivery orders respecting the declared assumptions converge to equivalent states. For nondeterministic artifacts, comparison is relational: an observation must belong to the specified allowed set or simulation relation.

### Minimum API and executable artifact

```ts
interface ResearchArtifactManifest {
  protocol: "pbui-research/0.1";
  artifact: string;
  version: string;
  capabilities: readonly string[];
  guarantees: readonly GuaranteeClaim[];
  command: readonly string[];
  normalization: readonly string[];
}
interface Harness {
  replay(artifact: Artifact, trace: Trace): RunReport;
  generate(model: ScenarioModel, seed: number): Trace;
  shrink(failure: Failure): Trace;
  compare(a: Artifact, b: Artifact, trace: Trace): ComparisonReport;
  benchmark(suite: BenchmarkSuite): BenchmarkReport;
}
```

Expose `harness.validate-manifest`, `harness.replay`, `harness.generate`, `harness.shrink`, `harness.compare`, and `harness.benchmark`.

The names are provisional. The final report must map the implemented API mechanically back to the semantic objects above.

### Work packages

#### Protocol and manifests

Finalize envelopes, statuses, evidence references, capabilities, version negotiation, deterministic modes, and guarantee labels.

#### Reference micro-models

Implement independent finite models for subject identity, positive selection, recursive closure, port partitions, small machines, and a simple replicated topology.

#### Generators and shrinkers

Generate typed fixtures and histories while tracking prerequisites; shrink graph, facts, components, events, causal schedules, and evidence.

#### Metamorphic/differential engine

Run laws, cross-implementation comparisons, mutation tests, and bridge checks with explicit observation relations.

#### Benchmark laboratory

Define cold/warm runs, workload scaling, resource measurement, correctness gates, uncertainty, and guarantee-stratified comparison.

#### Reports and replay viewer

Produce a portable failure bundle with seed, trace, manifests, normalized observations, divergence, and one-command reproduction.

### Required experiments

#### Mutation score

Seed realistic faults in micro-models and student adapters; measure which generators and laws detect each fault family.

#### Black-box substitution

Swap two implementations behind one capability and replay the same composition trace without source-level changes.

#### Nondeterminism study

Compare exact equality, trace inclusion, bounded simulation, and invariant-only relations for concurrent or ranked results.

#### Benchmark fairness

Demonstrate how warm-up, batching, validation, evidence level, and workload shape alter apparent rankings.

#### Failure comprehension

Give minimized and unminimized reports to developers; measure reproduction success and diagnosis time.

### Proof and validation obligations

- The harness invokes only documented protocol and process boundaries.
- Canonicalization removes only declared observationally irrelevant differences.
- Generators emit well-typed traces satisfying stated prerequisites or intentionally labeled negative cases.
- Shrinkers preserve failure and required dependency/causal structure.
- Every failure bundle includes command, versions, seed, trace, timeout, and normalized outputs.
- Reports distinguish proved, model-checked, property-tested, example-tested, empirical, assumed, and unsupported guarantees.
- Reference models are simpler and independently implemented rather than wrappers around submissions.
- Negative controls and seeded faults demonstrate test sensitivity.
- Nondeterministic comparisons use an explicit relation rather than flaky exact matching.
- Timeout, crash, malformed output, rejection, and unsupported capability are distinct outcomes.

### Measurements to report

- Seeded-fault detection by category.
- Median and tail shrink time and resulting trace size.
- Adapter/protocol implementation effort.
- Cross-implementation disagreement count and cause.
- Benchmark variance and correctness-gate failures.
- Developer reproduction and diagnosis success.

### Research method

The project is an investigation, not only a library implementation. It must make at least one claim that could be false and design an experiment capable of falsifying it.

Use this order:

1. State semantic objects and laws before selecting data structures.
2. Build the smallest executable reference semantics.
3. Add optimized or ergonomic implementations only after reference behavior is testable.
4. Generate counterexamples with property-based or model-based testing.
5. Record assumptions, especially opaque callbacks, clocks, fairness, and trusted host functions.
6. Run at least one user-facing scenario.

The report must distinguish proved properties, finite model checks, generated tests, empirical performance observations, user-study judgments, and unresolved conjectures.

### Composition capsule

Export the protocol schema, manifest schema, capability vocabulary, reference micro-models, generators, shrinkers, metamorphic laws, benchmark suites, report schema, and replay viewer. Every other project supplies a capsule that P15 can invoke. P15 does not dictate internal APIs; it controls only the experimental seam. Composition experiments are accepted only after individual artifacts pass their declared capability suite.

The capsule must classify each export as extensional data, intensional syntax, proof evidence, opaque callback, mutable resource, or event stream.

### Required deliverables

1. **Framing report:** 15-30 pages stating the model, alternatives, laws, assumptions, implementation, results, and negative findings.
2. **Reference implementation:** compact and optimized for clarity.
3. **Experimental prototype:** optimized runtime, React demo, proof development, or simulator as appropriate.
4. **Executable test suite:** unit, generated, and shared traces where applicable.
5. **Counterexample corpus:** minimized examples that broke an early law, API, optimization, or user assumption.
6. **Composition capsule:** manifest, JSONL adapter, exported schema, semantic version, and reliance statement.
7. **Demonstration script:** reproducible 10-15 minute walkthrough.
8. **Handoff note:** no more than two pages describing solid, provisional, and non-composable results.

All commands must run from a clean checkout using one documented entry point. Pin toolchains and record seeds.

### Baseline acceptance criteria

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

### Risks and failure modes to seek deliberately

- The harness becoming the de facto architecture.
- Shared bugs from copied reference code.
- Overcanonicalizing evidence or order.
- Flaky wall-clock assertions.
- Generating impossible histories.
- One aggregate score hiding guarantee differences.
- Treating unsupported as failure or vice versa.

### Stretch directions

- Coverage-guided semantic trace generation.
- Proof-certificate mutation integration with P14.
- Statistical model checking for selected machine/replica properties.
- Cross-language resource accounting in containers.
- A public corpus of minimized PBUI counterexamples.

### Suggested schedule

| Period | Milestone |
|---|---|
| Week 1 | Protocol and threat model. |
| Weeks 2-3 | Micro-models and adapters. |
| Weeks 4-5 | Generators/shrinkers. |
| Week 6 | Metamorphic engine and mutations. |
| Weeks 7-8 | Benchmark/reporting. |
| Weeks 9-10 | Cross-team pilot. |
| Week 11 | Refinement and final corpus. |

### Selected readings

1. Patrick Cousot and Radhia Cousot. "Abstract Interpretation Frameworks." Journal of Logic and Computation 2(4), 1992. https://www.di.ens.fr/~cousot/publications.www/CousotCousot-JLC-n2--3-p103--179-1992.pdf
2. J. J. M. M. Rutten. "Universal Coalgebra: A Theory of Systems." Theoretical Computer Science 249, 2000. https://ir.cwi.nl/pub/48/0048D.pdf
3. Marc Shapiro et al. "A Comprehensive Study of Convergent and Commutative Replicated Data Types." INRIA Research Report 7506, 2011. https://inria.hal.science/inria-00555588v1/document
4. Frank McSherry et al. "Differential Dataflow." CIDR 2013. https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf

### Final handoff questions

1. What is the smallest semantic kernel another team should trust?
2. Which laws are essential and which are merely convenient?
3. What counterexample most changed the design?
4. What is the worst composition mistake a future integrator could make?
5. Which result should be reimplemented independently before adoption?

\clearpage

# Part III - Shared interoperability contract

## Status and purpose

This contract defines the **research adapter**, not the eventual production PBUI API. It exists so that independently developed projects can be replayed, compared, substituted, and composed without sharing source code or framework internals.

The protocol is intentionally narrow:

- transport is newline-delimited JSON over standard input and output;
- every request has one response unless the manifest declares streaming support;
- messages are versioned and typed by `kind`;
- unsupported capabilities are first-class outcomes;
- semantic evidence, explanations, revisions, and assumptions are references rather than embedded host objects;
- deterministic mode is mandatory for reproducible traces where the subsystem permits it.

## Process contract

An artifact manifest provides an executable command. The harness starts one process, sends one JSON object per line on standard input, and reads one JSON object per line from standard output. Diagnostics go to standard error. The process must flush each response.

The process begins with `control.hello`. It may reject an incompatible protocol version. It ends with `control.shutdown` or end-of-input.

```json
{"protocol":"pbui-research/0.1","requestId":"r1","kind":"control.hello","payload":{"deterministic":true,"seed":17}}
```

```json
{"protocol":"pbui-research/0.1","requestId":"r1","status":"ok","payload":{"artifact":"example","capabilities":["selector.evaluate"]}}
```

## Envelope

```ts
interface LabEnvelope<T = unknown> {
  protocol: "pbui-research/0.1";
  requestId: string;
  kind: string;
  payload: T;
  context?: RequestContext;
}

interface RequestContext {
  revision?: string;
  transaction?: string;
  replica?: string;
  logicalTime?: string;
  deterministic?: boolean;
  seed?: number;
  deadlineMs?: number;
}

interface LabResult<T = unknown> {
  protocol: "pbui-research/0.1";
  requestId: string;
  status: "ok" | "rejected" | "unsupported" | "error";
  payload?: T;
  explanation?: Explanation;
  assumptions?: readonly AssumptionRef[];
  diagnostics?: readonly Diagnostic[];
}
```

A malformed request produces `error`. A well-formed request that violates a semantic precondition produces `rejected`. A valid request for an unimplemented capability produces `unsupported`. These outcomes may not be collapsed.

## Manifest

```ts
interface ResearchArtifactManifest {
  protocol: "pbui-research/0.1";
  artifact: string;
  version: string;
  project: string;
  command: readonly string[];
  capabilities: readonly CapabilityId[];
  deterministicMode: boolean;
  stateModel: "stateless" | "session" | "replica";
  schemas: Record<string, string>;
  guarantees: readonly GuaranteeClaim[];
  assumptions: readonly AssumptionDeclaration[];
  normalization: readonly NormalizationRule[];
  limits?: Record<string, number | string | boolean>;
}

type GuaranteeLevel =
  | "proved"
  | "model-checked"
  | "property-tested"
  | "example-tested"
  | "empirical"
  | "assumed"
  | "conjectured";
```

Every guarantee names the exact property, supported fragment, evidence artifact, and assumptions. A capability does not imply a guarantee.

## Common references

### Semantic subjects

```ts
interface SubjectRef {
  sort: string;
  key: string;
  revision?: string;
  authorityDomain?: string;
}
```

`sort` is part of identity. The protocol does not assume that identical strings in different sorts identify the same object. Aliases and cross-form identity are explicit relations or evidence.

### Occurrences

```ts
interface OccurrenceRef {
  occurrenceId: string;
  subject: SubjectRef;
  form: string;
  owner: string;
  lifecycleRevision: string;
}
```

An occurrence is a mounted or recorded presentation opportunity, not the subject itself. Two occurrences may denote one subject. A retired occurrence may remain in a trace but cannot be committed without revalidation.

### Ports

```ts
interface PortRef {
  component: string;
  name: string;
  contract: PortContractRef;
}

interface PortContractRef {
  contractId: string;
  semanticTag: string;
  payloadSort: string;
  mode: "read" | "write" | "read-write" | "event-source" | "event-sink";
  multiplicity: "one" | "optional" | "many";
  updateAlgebra: string;
  lifetime: "component" | "workspace" | "persistent" | "replicated";
}
```

Matching payload sorts are necessary but not sufficient for identity linking. The artifact must perform its declared compatibility judgment.

### Evidence and explanations

```ts
interface EvidenceRef {
  evidenceId: string;
  kind: string;
  producer: string;
  revision?: string;
}

interface Explanation {
  explanationId?: string;
  status: "available" | "unavailable" | "unknown" | "pending" |
          "stale" | "unauthorized" | "ambiguous" | "unsupported" | "error";
  summary: string;
  evidence?: readonly EvidenceRef[];
  obligations?: readonly Explanation[];
  remedies?: readonly Remedy[];
  completeness?: "complete" | "partial" | "foreign";
}
```

Evidence IDs must be stable within a trace and resolvable through a project-specific inspect capability when detailed evidence is claimed.

## Capability vocabulary

Projects may extend this vocabulary with namespaced IDs. The shared capabilities are:

| Capability | Meaning |
|---|---|
| `identity.compare` | Compare two subjects and return typed evidence |
| `identity.canonicalize` | Return a canonical or explicitly noncanonical subject |
| `occurrence.snapshot` | Return committed occurrence snapshot |
| `occurrence.revalidate` | Revalidate lifecycle and semantic revision before commit |
| `selector.typecheck` | Check selector IR and parameters |
| `selector.evaluate` | Produce candidates and evidence |
| `selector.explain` | Resolve evidence or rejection explanation |
| `rules.close` | Compute recursive closure for declared fragment |
| `rules.explain` | Return derivation/provenance for a fact |
| `operation.affordances` | Return currently offered operations |
| `operation.commit` | Revalidate and attempt an operation |
| `bindings.check-link` | Validate identity-link compatibility |
| `bindings.compile` | Compile declarations into a binding plan |
| `bindings.edit` | Apply dynamic link/unlink topology edit |
| `bindings.explain` | Return class and link provenance |
| `components.compose` | Compose component signatures and wiring |
| `links.propagate` | Apply an identity or transformed link update |
| `machine.step` | Advance an explicit interaction machine |
| `machine.replay` | Replay and normalize a machine trace |
| `program.run` | Interpret an interaction program |
| `program.analyze` | Return static effect/requirement summary |
| `incremental.transact` | Apply an atomic semantic change transaction |
| `incremental.verify` | Compare maintained and from-scratch result |
| `replica.apply` | Apply a local replicated command |
| `replica.merge` | Merge replica state or operations |
| `replica.explain` | Return causal/conflict explanation |
| `explanation.project` | Produce modality-neutral explanation model |
| `explanation.render-text` | Produce deterministic textual projection |
| `certificate.check` | Check a proof or compilation certificate |

## Control messages

### `control.hello`

Negotiates protocol, deterministic mode, seed, limits, and capabilities.

### `control.reset`

Resets session state to the common fixture or a provided snapshot. A stateful artifact must implement reset or declare a one-request process model.

### `control.snapshot`

Returns a normalized semantic snapshot sufficient for trace debugging. Private caches and data structures need not be exposed.

### `control.shutdown`

Requests graceful termination and cleanup.

## Revisions and transactions

- A semantic snapshot has a revision.
- A request may require an exact revision or freshness predicate.
- A transaction groups changes that must not be externally observed partially.
- A response identifies the revision it observed or produced where relevant.
- Occurrence lifecycle revision and subject semantic revision are separate.
- Replica logical time is not assumed to be globally total.

A stale revision is `rejected` with status `stale`; it is not a transport error.

## Determinism and normalization

Deterministic mode fixes random seeds, synthetic clocks, tie-breaking, generated IDs, and scheduling where the artifact supports such control. An artifact declares any irreducible nondeterminism.

Normalization may remove:

- request IDs;
- temporary process-local handles after they are mapped to stable trace symbols;
- timestamps generated solely for diagnostics;
- map/object field ordering;
- presentation-only prose when a stable message token is also returned.

Normalization may not remove:

- candidate or operation membership;
- semantic ordering when the contract makes it observable;
- evidence kind or completeness;
- authority, stale, unknown, ambiguous, or conflict status;
- affected subjects or views;
- causal relationships;
- failed obligations.

## Failure taxonomy

| Outcome | Use |
|---|---|
| `ok` | The capability completed according to its contract |
| `rejected` | Input was understood but a semantic precondition failed |
| `unsupported` | The artifact does not implement the requested capability or fragment |
| `error` | Malformed input, invariant breach, internal failure, or protocol failure |
| timeout | Harness-level outcome when no response arrives before the deadline |
| crash | Process exits or loses protocol framing |

A result may be `ok` with an empty candidate set. Empty is not equivalent to unsupported, error, or unknown.

## Trace discipline

A trace is a sequence of envelopes plus expected relations over responses. Expected results may be:

- exact normalized output;
- set or multiset equality;
- trace inclusion;
- invariant satisfaction;
- evidence validity;
- convergence after delivery;
- observational equivalence under a named relation.

Each trace records its fixture version, seed, capabilities, assumptions, and timeout.

## Versioning

Protocol changes follow semantic versioning at the schema level:

- additive optional fields and new capability IDs are compatible within `0.1` only when old readers may ignore them safely;
- changed meaning requires a new protocol version;
- project-specific payloads carry their own schema IDs and versions;
- capsules must preserve decoders for published fixture traces or provide a migration command.

## Security and trust boundary

The harness treats artifacts as untrusted processes. It should execute them with resource limits and a disposable working directory. Proof certificates and guarantee claims are inputs to a checker; they are not trusted merely because the manifest lists them.

## What this contract intentionally does not settle

This contract does not choose:

- the production store or transport;
- TypeScript versus another implementation language;
- a universal query or component syntax;
- UI rendering technology;
- one evidence representation;
- a distributed consistency policy;
- whether an artifact is embedded or process-isolated in production.

Its purpose is experimental substitutability. A successful composition study may justify a narrower and more ergonomic production API later.

\clearpage

# Part IV - Evaluation rubric

## Evidence labels

Every nontrivial claim in a report or manifest uses one of these labels.

| Label | Minimum evidence |
|---|---|
| Proved | Named theorem in a reproducible proof development, with assumptions and trusted base |
| Model-checked | Explicit finite abstraction, bounds, checker, and counterexample output |
| Property-tested | Generator, oracle or metamorphic law, shrinker, seeds, and run counts |
| Example-tested | Fixed named examples and expected results |
| Empirical | Measurement protocol, environment, uncertainty, and raw data |
| Assumed | Foreign boundary or environmental premise stated explicitly |
| Conjectured | Plausible claim without sufficient evidence |
| Unsupported | Deliberately outside the implemented fragment |

A stronger-sounding label may not be inferred from a weaker one. For example, exhaustive testing of a bounded model is not a proof for unbounded inputs.

## Scoring

### 1. Semantic clarity - 20 points

Full credit requires:

- named semantic objects and distinctions;
- a formal or executable denotation where appropriate;
- laws and non-laws separated;
- explicit supported fragment and non-goals;
- alternative designs considered fairly;
- terms such as quotient, fixed point, bisimulation, lens, CRDT, or capability used with concrete definitions.

Diagnostic questions:

1. Can a reviewer state what two implementations must agree on?
2. Are subject identity, occurrence identity, binding identity, and host-object identity separated where relevant?
3. Does the project define observations before implementation internals?
4. Are undefined or partial cases represented rather than silently guessed?

### 2. Correctness evidence - 20 points

Full credit requires:

- a transparent reference semantics or proof kernel where feasible;
- at least five nontrivial laws as theorems or executable checks;
- negative controls or seeded faults;
- minimized counterexamples;
- typed failures rather than swallowed exceptions;
- claim-to-artifact traceability.

Deduct heavily when optimized and reference implementations share the same critical logic, or when tests merely snapshot one implementation.

### 3. Experimental quality - 15 points

Full credit requires:

- falsifiable hypotheses stated before the main experiment;
- workloads varying structure, not only size;
- ablations or competing designs;
- recorded seeds and raw observations;
- an explanation of threats to validity;
- negative findings and crossover points.

A benchmark with no correctness gate receives at most half credit in this dimension.

### 4. User-facing evidence - 10 points

Full credit requires:

- at least one scenario where a user can observe the subsystem's semantic state;
- keyboard operation;
- explicit stale, unauthorized, unknown, ambiguous, or conflict status where applicable;
- a reproducible demonstration script;
- user study or structured expert review for projects making usability claims.

A developer console alone is acceptable only when the project has no direct user-facing claim and the reason is argued.

### 5. Composition readiness - 15 points

Full credit requires:

- a valid capability manifest;
- a versioned schema or syntax;
- a deterministic JSONL adapter where possible;
- a reliance statement distinguishing stable contract from implementation detail;
- resource ownership and lifecycle described;
- unsupported fragments reported explicitly;
- at least one substitution test by another team.

No credit is awarded for "composition" achieved by importing private classes from another project.

### 6. Reproducibility - 10 points

Full credit requires:

- one clean-checkout entry point;
- pinned toolchains and dependencies;
- fixtures, seeds, and commands;
- generated output separated from source;
- documented hardware and runtime for performance results;
- successful external reproduction.

### 7. Critical judgment - 10 points

Full credit requires:

- strongest counterexample highlighted;
- remaining assumptions and conjectures ranked by risk;
- places where a simpler mechanism is preferable;
- language proportional to evidence;
- a clear recommendation to adopt, revise, restrict, or reject the investigated design.

## Mandatory review checklist

A reviewer records yes/no/not-applicable for each item:

- [ ] The semantic kernel is stated independently of framework code.
- [ ] At least one attractive wrong design is implemented or modeled and fails visibly.
- [ ] Opaque callbacks or external services are marked as foreign assumptions.
- [ ] Revision, cancellation, disposal, and error behavior are tested.
- [ ] Generated tests have shrinking or equivalent counterexample reduction.
- [ ] Every benchmark run validates output correctness.
- [ ] User-visible availability and commit-time validity are not conflated.
- [ ] Evidence and explanations identify their completeness.
- [ ] Persistent IDs do not depend on unstable implementation representatives.
- [ ] Concurrency claims state delivery and coordination assumptions.
- [ ] Formal claims name theorem files and assumptions.
- [ ] The capsule can be invoked without importing source-level internals.
- [ ] A second team reproduced the artifact.
- [ ] The handoff note distinguishes solid, provisional, and non-composable results.

## Review report format

```text
Summary judgment
Most credible result
Most important counterexample
Unsupported or overstated claim
Composition risk
Reproduction status
Required revision before phase 2
Score by dimension
```

## Phase-2 gate

A project enters a composition constellation only if it scores at least:

- 14/20 semantic clarity;
- 14/20 correctness evidence;
- 10/15 composition readiness;
- 7/10 reproducibility;

and has no unresolved critical issue involving type safety, authority bypass, silent conflict loss, or unreproducible proof claims.

\clearpage

# Part V - Phase-2 composition map

## Why composition is a second pass

Subsystem composition should begin only after each artifact has a stable observation boundary. Integrating earlier encourages teams to encode neighboring assumptions directly into their implementations, after which apparent success says little about modularity.

The second pass asks four separate questions:

1. **Syntactic compatibility:** can artifacts exchange well-typed messages and schemas?
2. **Semantic compatibility:** do their interpretations agree on shared objects and laws?
3. **Operational compatibility:** do lifecycle, scheduling, transaction, and failure assumptions coexist?
4. **Human compatibility:** can a user understand the composed state, phase, authority, and conflicts?

Passing one layer does not imply the next.

## Universal entry criteria

Every participating project must provide:

- a validated `pbui-research/0.1` manifest;
- a one-command adapter and reset operation;
- exact supported capabilities and limits;
- normalized common-trace outputs;
- guarantee labels and assumptions;
- at least one negative control;
- a reliance statement;
- a versioned schema migration story;
- a named contact or owner for interpreting failures;
- successful external reproduction.

The integration coordinator freezes artifact versions before each experiment. A later fix creates a new run; it does not rewrite the original result.

## Composition protocol

For each constellation:

1. Draw the semantic dependency graph.
2. Mark each edge as extensional data, intensional syntax, evidence, event, mutable resource, effect request, or foreign callback.
3. Identify laws relied upon at each edge.
4. Run artifacts independently on their local traces.
5. Run an adapter-only dry connection with no user interface.
6. Run deterministic shared traces through the composition.
7. Inject stale state, cancellation, denial, malformed evidence, and process failure.
8. Run the user-facing scenario.
9. Compare composed behavior with each subsystem's reliance statement.
10. Record preserved, weakened, contradicted, and newly required guarantees.

## Constellation A - deterministic local workbench

### Participants

P01, P02, P03, P05, P06, P09, P11, P13

### Architectural question

Can a deterministic local application connect stable subjects, mounted occurrences, inspectable selection, authorized operations, quotient bindings, explicit workflows, incremental maintenance, and accessible explanations without collapsing them into one store or callback registry?

### Required interfaces

```text
P01 SubjectRef + comparison evidence
        ↓
P02 occurrence snapshot/lifecycle
        ↓
P03 candidate + evidence
        ↓
P09 selection/linking machine
        ↓
P05 operation intent + commit result

P06 binding declarations/plan ──→ P11 change transactions
                                  ↓
                             P13 explanation model
```

### Experiment sequence

1. Mount two occurrences of `temperature` with different host objects; P03 must return one subject through either occurrence.
2. Start a refined selection request; unmount the focused occurrence before commit; P02/P09/P13 must expose the stale transition.
3. Link chart and pipeline document ports through P06; project one binding into two widgets.
4. Change the shared value; P11 incrementally updates candidates and actions, then verifies from scratch.
5. Revoke an operation capability between offer and commit; P05 rejects, P13 explains the failed obligation, and P09 reaches one terminal outcome.
6. Repeat by keyboard and pointer and compare semantic event traces.

### Primary failure hypotheses

- P01 revisions and P02 lifecycle revisions are conflated.
- P03 evidence cannot survive P11 incremental retraction.
- P06 topology edits leak implementation IDs into P13.
- P05 affordances are cached beyond authority validity.
- P09 machine state and React state disagree after cancellation.

### Success criterion

All six shared traces complete with one canonical semantic event log per modality, and P11 reports from-scratch consistency after every committed change.

## Constellation B - open analytical components

### Participants

P06, P07, P08, P09, P13

### Architectural question

Can separately implemented chart, pipeline, and table components compose through typed boundaries, using identity links where semantics are equal and lens/repair policies where representations differ?

### Experiment sequence

1. Load component manifests without application-specific imports.
2. Compose chart and pipeline primary-document ports with an identity link.
3. Attempt to identify semantically different ports carrying the same payload type; P06/P07 must reject with a contract explanation.
4. Connect table row selection to pipeline filter through P08; exercise an ambiguous inverse update.
5. Create the links through a P09 machine and inspect phase/cancellation.
6. Add a third component in two association orders; compare normalized composed signatures and behavior.
7. Remove and reload one component; preserve or explicitly migrate link declarations.
8. Present topology, affected views, ambiguity, and remedies through P13.

### Primary failure hypotheses

- Component manifests omit temporal or authority semantics required to judge compatibility.
- Identity and transformed links share one API and silently choose conversions.
- Associativity holds only for wiring syntax, not for scheduling or naming.
- Unlinking claims to invert quotienting without an initialization policy.

### Success criterion

A component from a separate repository can replace one fixture component using only the published signature and adapter, while all incompatibilities and repair choices remain typed and user-visible.

## Constellation C - proof-carrying semantic runtime

### Participants

P03, P04, P06, P11, P14, P15

### Architectural question

Can query, recursion, binding, and incremental compilers emit artifacts whose core correctness is checked independently, while unsupported foreign regions remain clearly outside the proof boundary?

### Experiment sequence

1. P03 emits typed selector IR and candidate evidence for the common fixture.
2. P04 computes recursive link/authority closure and provenance.
3. P06 emits a binding plan plus certificate for a typed port graph.
4. P14 checks selector derivations and binding certificates.
5. P11 maintains the same results over transactions and runs its from-scratch oracle.
6. P15 mutates syntax, evidence, projection maps, sorts, change traces, and certificates.
7. Introduce a foreign predicate and verify that guarantees are weakened only at the marked node.
8. Compare independently implemented reference evaluators.

### Primary failure hypotheses

- The proof kernel and JSON bridge disagree on sort encodings.
- Certificates prove local edges but not global class coverage.
- Incremental evidence retains support removed from recursive closure.
- Normalization hides a meaningful provenance difference.
- "Verified" claims extend beyond the positive finite fragment.

### Success criterion

Seeded mutations are rejected by either typechecking, certificate checking, from-scratch comparison, or explicit unsupported status; every surviving guarantee maps to a named artifact and assumption set.

## Constellation D - local-first linked workbench

### Participants

P01, P05, P06, P08, P12, P13, P15

### Architectural question

Which identity, authority, topology, transformed-link, and explanation properties remain valid when replicas edit offline and merge under different causal schedules?

### Experiment sequence

1. Create identical workspaces on two replicas from one P01 identity snapshot.
2. Concurrently link A-B and B-C; merge and derive the quotient through P06.
3. Concurrently unlink one declaration and link an overlapping pair; display causal explanation.
4. Select different documents on the shared binding under LWW and multi-value policies.
5. Delete a document while another replica uses it in a transformed P08 link.
6. Revoke link authority concurrently with an offline operation.
7. Deliver all operations in several permitted orders; P15 checks convergence and invariant relations.
8. Ask users to predict and repair conflicts using P13 projections.

### Primary failure hypotheses

- Replicas exchange quotient representatives instead of source declarations.
- Converged topology violates typed compatibility after schema change.
- LWW hides meaningful concurrent intent.
- Authority safety is treated as eventual preference.
- Causal explanation cannot connect a conflict to the rendered views.

### Success criterion

For each declared policy, all replicas converge under its delivery assumptions; invariant violations are either prevented, coordinated, or surfaced as explicit conflicts with repair actions. No report equates convergence with safety.

## Constellation E - effectful interaction architecture

### Participants

P03, P05, P09, P10, P13

### Architectural question

Can ergonomic interaction programs be interpreted into explicit machines while preserving selection requirements, authority effects, cancellation, trace replay, and user-visible phase?

### Experiment sequence

1. Author choose-field, perform-operation, and link-two-ports workflows in P10.
2. Run a static effect analysis and compare it with actual deterministic traces.
3. Lower or interpret each program into a P09 machine.
4. Substitute normal, denial, timeout, stale, and cancellation handlers.
5. Verify P05 authority cannot be bypassed by handler substitution.
6. Replay the same answers and compare normalized machine traces.
7. Render phase, requested object, denial, and cleanup through P13.
8. Compare with a direct Promise/callback implementation under fault injection.

### Primary failure hypotheses

- Generator syntax hides opaque host control flow.
- Effect summaries are unsound when helper functions acquire resources.
- Cancellation releases machine state but not handler resources.
- Handler substitution changes mandatory authority semantics.
- Lowering duplicates or loses terminal resolution.

### Success criterion

The same structured program runs under at least three handlers, lowers to a machine with one terminal outcome, and exposes every mandatory effect and phase in a deterministic trace.

## Cross-constellation tests

After individual constellations succeed, run these limited crossovers:

- Feed P12 replica changes into P11 incremental maintenance, but keep correctness checked against a merged snapshot.
- Let P10 invoke P06/P08 link effects through P09 while P13 renders state.
- Use P14 certificates inside P07 plugin loading only for the verified binding subset.
- Use P15 to replace one implementation at a time in Constellation A.

Do not attempt an all-project integration until at least two constellations have produced stable reliance records.

## Composition result record

Each run produces:

```text
Constellation and artifact versions
Dependency graph
Trace and seed
Preserved guarantees
Weakened guarantees
Contradicted guarantees
New assumptions
Observed emergent behavior
User-facing failures
Performance/resource observations
Minimized counterexamples
Adopt/revise/reject recommendation
```

## Stop rules

Pause or split a composition experiment when:

- two artifacts assign different meanings to the same schema field;
- an adapter must inspect a private internal data structure;
- a safety claim depends on scheduling that neither artifact owns;
- normalization is proposed to hide a semantic disagreement;
- the user interface cannot distinguish conflict from ordinary unavailability;
- a proof or test guarantee is being applied outside its manifest fragment;
- performance debugging begins before correctness disagreement is resolved;
- one subsystem is being expanded into another solely to make the integration pass.

The appropriate result may be a revised boundary, a new explicit adapter, or rejection of the composition. A working demo is not the only successful outcome.
