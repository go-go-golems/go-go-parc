---
title: "PBUI Subsystem Research Program Handbook"
subtitle: "Fifteen independent projects for semantic validation, empirical assessment, and later composition"
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

# Purpose

This package defines a first research pass for a presentation-based user-interface architecture. It is intentionally organized as **small, independently executable projects** rather than as a single platform implementation. Each team receives a bounded semantic problem, a shared miniature workbench, a black-box handoff protocol, and an obligation to report negative results.

The program has two passes:

1. **Subsystem pass.** Each team builds and evaluates one subsystem without importing another team's code. The goal is to discover semantic boundaries, false assumptions, laws, counterexamples, implementation costs, and user-facing consequences.
2. **Composition pass.** Only after individual capsules have stabilized are selected subsystems substituted and composed in controlled constellations. The goal is not to merge everything. It is to identify which interfaces compose, which guarantees survive, which assumptions conflict, and where a simpler architecture is preferable.

The package is suitable for graduate seminars, doctoral rotations, research engineers, or parallel exploratory teams. Projects differ in mathematical and empirical emphasis, but every project must ship executable evidence.

# Program principles

## Semantic claims before framework choices

A project begins by stating its objects, operations, observations, and laws. React, TypeScript, Lean, Datalog, CRDT libraries, statechart tools, and database engines are candidate implementations. None is the definition of the subsystem.

## Reference semantics before optimization

Every optimized, incremental, distributed, or ergonomic implementation needs a smaller, transparent reference model whenever feasible. The reference may be slow. Its job is to make disagreement observable.

## Proof scope is explicit

Reports label each claim as one of:

- **proved** in a named formal development under stated assumptions;
- **model-checked** over a stated finite abstraction;
- **property-tested** over generated cases and recorded seeds;
- **example-tested** over a fixed suite;
- **empirical** from measurement or user study;
- **assumed** at a foreign boundary;
- **conjectured** and unresolved.

No project may use the phrase "verified" without naming the artifact and scope.

## Counterexamples are first-class results

A minimized counterexample that invalidates an appealing law or API is a successful outcome. Every team maintains a counterexample corpus and explains how the design changed in response.

## User experience is part of the semantics

Selection, rejection, authority, staleness, conflicts, phase, and affected views must be visible through at least one user-facing prototype. A subsystem that cannot explain its result may be semantically incomplete even when its internal algorithm is correct.

## Composition is by declared artifacts

Teams compose through versioned syntax, extensional data, evidence, events, resources, or process protocols. They do not import undocumented classes or rely on accidental in-memory object identity.

# Portfolio

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

# Shared analytical workbench

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

The fixture is deliberately small enough to model exhaustively in several projects. Teams may add scale fixtures for performance studies, but all published results must include the common traces so readers can compare interpretations.

# Independence rules for the first pass

1. A team may read another project brief, but it must not import another team's implementation during the subsystem pass.
2. Shared fixtures and protocol schemas are permitted.
3. If a project needs a neighboring subsystem, it builds the smallest local stub or reference model and labels it as such.
4. Teams may exchange counterexamples through the program repository.
5. Cross-reviewers inspect semantic assumptions and capsule boundaries; they do not rewrite the implementation.
6. A project can narrow its supported fragment, but the narrowing must be machine-readable in its capability manifest.

# Repository and artifact structure

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

# Program milestones

## Milestone 0 - preregistration and threat model

Before implementation, each team submits:

- a one-page semantic model;
- three falsifiable hypotheses;
- the proposed trusted boundary;
- a list of likely false laws;
- an experimental plan and stopping condition;
- the initial capability manifest.

## Milestone 1 - reference artifact

The reference semantics runs at least three shared traces and has generated tests for its basic laws. No optimization claim is accepted before this milestone.

## Milestone 2 - experimental prototype

The main implementation or proof development exists, common traces run, and at least one early design has produced a counterexample.

## Milestone 3 - external replication

A paired reviewer checks out the artifact, runs the entry point, writes one new trace, and attempts to falsify one claim.

## Milestone 4 - capsule freeze

Schemas, capability claims, normalization, and assumptions are versioned. The artifact is ready for the second-pass composition lab.

# Evaluation rubric

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

# Cross-review assignments

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

# Decision records

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

# Second-pass composition constellations

The program does not begin with a single grand integration. It uses five controlled constellations.

## Constellation A - deterministic local workbench

P01 + P02 + P03 + P05 + P06 + P09 + P11 + P13

Question: can identity, mounted occurrences, inspectable selection, authorized operations, shared bindings, explicit workflows, incremental maintenance, and accessible explanation form one deterministic local system?

## Constellation B - open analytical components

P06 + P07 + P08 + P09 + P13

Question: can independently developed chart, pipeline, and table components be wired through typed identity and transformed links without private-store coupling?

## Constellation C - proof-carrying semantic runtime

P03 + P04 + P06 + P11 + P14 + P15

Question: can query, closure, binding, and incremental artifacts carry enough evidence or certificates for an independent checker and differential harness?

## Constellation D - local-first linked workbench

P01 + P05 + P06 + P08 + P12 + P13 + P15

Question: which identity, authority, link, and explanation invariants survive partitions, concurrent edits, and replica merge?

## Constellation E - effectful interaction architecture

P03 + P05 + P09 + P10 + P13

Question: does a structured interaction program improve authoring while lowering to an explicit machine whose semantic phases and effects remain inspectable?

Detailed entry criteria and experiment sequences are in `shared/PHASE-2-COMPOSITION-MAP.md`.

# Program-wide stop conditions

A subsystem should stop expanding and ship a bounded result when any of the following holds:

- the proposed law is false and a useful counterexample plus replacement contract has been established;
- the supported fragment is sufficient for all common traces and expansion would add only host-language features;
- performance is already dominated by an adjacent subsystem outside the project's scope;
- the proof burden exposes an unstated assumption that must be resolved in another project;
- user testing shows the semantic distinction is not actionable in the current form;
- composition requires an interface change that should be evaluated in the second pass rather than hidden locally.

# Program-wide failure modes

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

# Handoff to the composition pass

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
