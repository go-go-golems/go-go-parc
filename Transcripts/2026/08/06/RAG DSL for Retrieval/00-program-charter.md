---
title: "rag-ttc Semantic Research Program Charter"
subtitle: "First-pass research program charter"
author: "Research assignment brief"
date: "August 4, 2026"
lang: en-US
toc: true
toc-depth: 3
numbersections: true
geometry: margin=0.78in
fontsize: 10pt
mainfont: "DejaVu Serif"
sansfont: "DejaVu Sans"
monofont: "DejaVu Sans Mono"
colorlinks: true
linkcolor: blue
urlcolor: blue
header-includes:
  - \usepackage{microtype}
  - \usepackage{booktabs}
  - \usepackage{longtable}
  - \usepackage{array}
  - \usepackage{enumitem}
  - \usepackage{xcolor}
  - \usepackage{listings}
  - \usepackage{tocloft}
  - \setlength{\cftsecnumwidth}{3.2em}
  - \setlength{\cftsubsecnumwidth}{4.2em}
  - \setlength{\cftsubsubsecnumwidth}{5.2em}
  - \lstset{breaklines=true,basicstyle=\ttfamily\small,columns=fullflexible,keepspaces=true,showstringspaces=false}
---

# Purpose

This package defines a first-pass research program for understanding and refining the semantics of `rag-ttc`. The program does not ask one team to redesign the whole repository. It decomposes the system into small, independently executable projects, each centered on one falsifiable semantic boundary.

The first pass answers questions such as:

- What counts as the same source, request, fact, derivation, view, or operation?
- Which states can be merged without order dependence?
- Which operations only add candidates and which deliberately select or remove them?
- When do retries, caching, batching, concurrency, and backend replacement preserve meaning?
- What can be replayed, incrementally updated, migrated, cited, or safely disclosed?

The second pass, described in `90-composition-pass-playbook.md`, replaces local fakes with neighboring project implementations and tests whether the contracts compose.

# Architectural starting point

The source snapshot already has strong local mechanisms: immutable source revisions, content-addressed chunks and representations, deterministic ordering, narrow typed interfaces, cache/retry/batch/budget utilities, explicit experiment artifacts, answering phases, and an enforced boundary between reusable packages and application code.


ewpage

![Current rag-ttc architecture](assets/current-architecture.png){width=96%}


ewpage

The proposed research architecture adds a semantic spine without turning the repository into a workflow language:

![Proposed semantic architecture - portrait rendering](assets/proposed-architecture-portrait.png){width=78%}

The shared conceptual boundary is:

```text
Plan -> Execute -> Admit -> Merge -> View -> Generate
```

- **Plan** creates a typed request or operation.
- **Execute** performs an external or expensive effect.
- **Admit** validates the observation and converts it into canonical facts and derivations.
- **Merge** combines add-only state without depending on order or duplication.
- **View** ranks, resolves ambiguity, truncates, packs, or labels a fixed snapshot.
- **Generate** produces an answer observation from a selected view.

This boundary is a hypothesis to test. Individual projects may refine or reject parts of it by providing counterexamples.

# Project catalog

| Code | Project | Track | Duration | Team | Priority |
| --- | --- | --- | --- | --- | --- |
| P01 | Semantic Identity and Cache Fingerprints | Foundations: identity and reproducibility | 4-6 weeks | 1-2 students | Critical path |
| P02 | Canonical Facts and Provenance Kernel | Foundations: semantic data model | 5-7 weeks | 1-2 students | Critical path |
| P03 | Lawful Merge and Deterministic Evidence Ledger | Foundations: composition and concurrency | 5-7 weeks | 1-2 students | Critical path |
| P04 | Candidate State and Ranked View Separation | Policy semantics: ranking and selection | 4-6 weeks | 1-2 students | High |
| P05 | Closure and Frontier Evaluation Engine | Recursive semantics: rules and fixed points | 6-8 weeks | 2 students | High |
| P06 | Flow Executor Semantics and Captured Effects | Operational semantics: execution | 5-7 weeks | 1-2 students | High |
| P07 | Knowledge Retrieval: Discovery versus Selection | Subsystem semantics: knowledge retrieval | 6-8 weeks | 2 students | High |
| P08 | Connected Retrieval Composition | Subsystem semantics: retrieval composition | 6-8 weeks | 2 students | High |
| P09 | Tool-Agent Evidence and Citation Contracts | Subsystem semantics: agentic/tool RAG | 6-8 weeks | 2 students | High |
| P10 | Proof-Carrying Experiments and Replay | Reproducibility: artifacts and audit | 5-7 weeks | 1-2 students | High |
| P11 | Incremental Maintenance, Updates, and Retractions | State evolution: incremental computation | 6-8 weeks | 2 students | Medium-high |
| P12 | Backend Conformance and Schema Migration | Representation semantics: backends and evolution | 6-8 weeks | 2 students | Medium-high |
| P13 | Security Labels, Authorization, and Noninterference | Cross-cutting semantics: security | 6-8 weeks | 2 students | Medium-high |

## Suggested cohorts

A practical assignment plan is:

- **Cohort A - foundations:** P01, P02, P03, and P04. These projects define identity, canonical state, lawful merge, and views.
- **Cohort B - execution and recursion:** P05 and P06. These projects test fixed-point evaluation and operational transparency.
- **Cohort C - RAG subsystems:** P07, P08, and P09. These projects study knowledge, connected retrieval, and tool-agent turns.
- **Cohort D - lifecycle and assurance:** P10, P11, P12, and P13. These projects study replay, updates, backends/migration, and security.

Projects may start concurrently. Cohort labels are for review meetings and eventual composition, not implementation dependencies.

# Shared research method

## Two implementations per project

Every team builds:

1. A **standalone executable semantic model**. It should be small enough to understand completely and should use deterministic fakes or recorded effects.
2. A **rag-ttc adapter** against the supplied source snapshot. The adapter tests whether the proposed model captures real structures and where compatibility fails.

The standalone model prevents repository complexity from hiding a semantic mistake. The adapter prevents a beautiful toy model from remaining irrelevant.

## Falsification first

For each proposed law, build at least one intentionally bad implementation or adversarial fixture that should fail. A test suite that only passes the preferred implementation is not sufficient evidence that the law was stated or tested correctly.

Every hypothesis receives one of these outcomes:

- **Supported:** the stated tests and experiments did not find a counterexample.
- **Falsified:** a minimal reproducible counterexample exists.
- **Mixed:** the result depends on a clarified precondition or contract variant.
- **Not tested:** required evidence was unavailable.

## Evidence levels

Use these labels in reports and `results.json`:

| Evidence label | Meaning |
|---|---|
| `proved_model` | A direct argument from the executable model or constructors, with assumptions stated |
| `exhaustive_finite` | Every state or schedule in a finite bounded universe was checked |
| `property_tested` | Random/generated testing with saved seeds and shrinking |
| `empirical` | Measurements on selected workloads; no universal claim |
| `conjectural` | Plausible design hypothesis not yet validated |

Do not label an empirical result as a proof. Do not dismiss a finite counterexample because a broader empirical average looks good.

# Shared vocabulary

| Term | Programmer meaning |
|---|---|
| Semantic identity | The fields all relevant consumers must treat as meaningfully the same |
| Fact | Immutable canonical information, named by semantic identity |
| Derivation | Why a fact exists: rule, inputs, configuration, and admitted observation |
| Observation | A recorded external or algorithm result such as score, response, or match |
| Candidate state | All admitted facts/observations before selection |
| View | Ordered, scored, bounded, or projected result over a fixed candidate snapshot |
| Trace | What happened operationally: attempts, cache, worker order, timing, errors |
| Merge/join | Deterministic combination of compatible add-only states |
| Closure | Repeated rule application until no new facts or operations remain |
| Saturated | One more complete rule step adds nothing |
| Sound partial result | Every returned fact is valid even though deeper facts may be missing |
| Semantic transparency | An operational change alters trace/cost but not declared semantic output |
| Noninterference | Restricted input changes do not alter declared low-authority observations |

# Repository and baseline protocol

## Supplied snapshot

- Source archive: `rag-ttc.zip`
- Module: `github.com/the-tree-center/rag-ttc`
- Declared Go version: `1.26.5`
- Static inventory: 449 Go files and 151 Go test files in the reviewed snapshot
- Source checksum: see `reference/SHA256SUMS.txt`

The prior handbook review was static because the analysis environment could not use the declared toolchain and dependencies. Each team must establish an executable baseline in its own approved environment.

## Baseline gate

Before semantic changes:

1. Record Go/toolchain, OS/architecture, module cache state, and source commit/archive digest.
2. Run `go test ./...` and preserve full output.
3. Run the package-specific tests relevant to the assignment at least three times where scheduling may matter.
4. Freeze representative current outputs as compatibility fixtures.
5. Record any pre-existing failures; do not silently fix unrelated tests in the research branch.
6. Build a no-network test mode using fakes or captured effects.

A project may proceed with a partially failing baseline, but must isolate those failures from its own claims.

# Shared fixture pack

The fixture pack in `fixtures/` defines common adversarial cases. Each project brief names the fixtures it must use. Teams may extend but not mutate a published version.

- `trees-v1`: cycles, diamonds, unreachable nodes, and known derivation ranks.
- `identity-edgecases-v1`: encoding, Unicode, order, map, and numeric edge cases.
- `diamond-provenance-v1`: one fact with two independent derivations.
- `multihop-graph-v1`: concept/fact/mention path requiring multiple hops.
- `ranking-ties-v1`: equal scores, channel overlap, and exact budget boundaries.
- `completion-permutations-v1`: overlapping concurrent operations and deterministic selection.
- `ambiguous-knowledge-v1`: one surface with multiple valid concept candidates.
- `update-sequences-v1`: additions, duplicate events, retraction, supersession, and policy-only change.
- `public-confidential-v1`: principals and two secret worlds for security tests.
- `corrupt-artifacts-v1`: mutation classes for experiment custody and replay.

# Shared interchange contracts

The program intentionally does not require a shared Go implementation in pass one. It requires neutral versioned files:

- `schemas/project-result.schema.json` - common assessment output;
- `schemas/semantic-interchange.schema.json` - minimal fact/derivation envelope;
- `schemas/operation-trace.schema.json` - stable operational trace event;
- project-specific schemas named in each brief.

Every project must emit `results.json`. This allows program-level comparison without requiring one monorepo branch.

# Common test design

## Unit tests

Use examples for exact edge behavior: missing IDs, invalid spans, conflicts, tie breaks, budget boundaries, cache corruption, unknown schema versions, and explicit error categories.

## Law tests

Use generated values for equations such as:

```text
Join(a, b) == Join(b, a)
Join(Join(a, b), c) == Join(a, Join(b, c))
Join(a, a) == a
Close(Close(seed)) == Close(seed)
seed subset-of Close(seed)
a subset-of b  =>  Close(a) subset-of Close(b)
Sequential(x) == Parallel(x)
Once(x) == Retry(x)          // only under the declared retry preconditions
Migrate(CloseOld(x)) == CloseNew(Migrate(x))
```

Persist random seeds. Shrink failures. Convert important failures into neutral fixtures.

## Model-based tests

Where stateful behavior matters, implement a simple reference model and compare arbitrary operation sequences against the real implementation. P03, P06, P11, and P12 are expected to use this method.

## Schedule tests

Do not rely only on the Go race detector. It detects data races, not semantic order dependence. Enumerate all completion orders for small fixtures and use a deterministic randomized scheduler for larger tests.

## Fault tests

Inject failure at semantically meaningful boundaries: before an external effect, after the effect but before response delivery, after admission but before persistence, during batch write, and during manifest sealing.

# Common evaluation dimensions

Every project reports the dimensions that apply:

| Dimension | Core question |
|---|---|
| Correctness | Does the implementation satisfy its laws and reject adversarial fixtures? |
| Compatibility | Does the adapter reproduce frozen current behavior where intended? |
| Determinism | Do permutation, restart, and schedule changes preserve declared output? |
| Completeness | What result is complete, through which stage/depth, under which assumptions? |
| Provenance | Can each output be traced to validated inputs and operations? |
| Reproducibility | Can the result be verified or replayed without live effects? |
| Performance | What CPU, memory, storage, latency, and external-call costs are introduced? |
| Ergonomics | Can a normal Go programmer use the API without understanding the implementation theory? |
| Security | Can restricted data cross source, cache, trace, view, or artifact boundaries? |
| Composability | Can a neighboring implementation replace the local fake while laws still pass? |

# Review rubric

Score each category from 0 to 4:

| Score | Interpretation |
|---:|---|
| 0 | Missing or cannot be evaluated |
| 1 | Prototype only; contract implicit; weak tests |
| 2 | Clear API and examples; incomplete adversarial evidence |
| 3 | Laws, counterexamples, adapter, and repeatable evaluation are complete |
| 4 | Independent reproduction, strong negative results, and composition-ready contract |

Recommended weighting:

| Category | Weight |
|---|---:|
| Semantic clarity and contract precision | 20% |
| Law/adversarial test quality | 20% |
| Correctness of standalone model | 15% |
| Fidelity and insight of rag-ttc adapter | 15% |
| Experimental design and evidence | 10% |
| Reproducibility and artifact quality | 10% |
| API ergonomics and documentation | 5% |
| Composition readiness | 5% |

A high score does not require the original hypothesis to survive. A well-demonstrated rejection may be more valuable than a weak positive result.

# Program-wide non-goals

- Do not build a new workflow language or central scheduler.
- Do not replace typed domain APIs with one generic `any`-based framework.
- Do not claim model factuality, entailment, or exact reproducibility beyond tested guarantees.
- Do not optimize away provenance before the reference semantics are stable.
- Do not require live paid providers for correctness tests.
- Do not merge all student branches during pass one.
- Do not treat deterministic ordering alone as proof of lawful merge or retry safety.
- Do not force approximate retrieval backends into an exact-equivalence claim.

# Team hand-off checklist

Before review, each team must provide:

- standalone model and rag-ttc adapter;
- exact build/test commands;
- frozen source/toolchain identifiers;
- law table with pass/fail evidence;
- at least one intentionally bad implementation or adversarial test;
- minimized counterexamples as neutral fixtures;
- machine-readable `results.json`;
- performance/resource results where relevant;
- limitations and untested assumptions;
- versioned schemas and composition ports;
- five-minute and thirty-minute demos;
- final recommendation: adopt, adopt with changes, continue research, or reject.

# Governance and coordination

## Weekly project review

Each team reports only four items:

1. Strongest new invariant or contract statement.
2. Strongest counterexample or uncertainty.
3. Current executable artifact.
4. One interface decision that may affect another project.

This keeps cross-project coordination semantic rather than branch-level.

## Contract changes

A team may revise a shared contract by publishing:

- the old and new schema versions;
- a migration or explicit incompatibility statement;
- the counterexample motivating the change;
- affected project codes;
- updated conformance fixture.

No in-place contract mutation is allowed after another team has consumed it.

## Stop conditions

A project should stop expanding scope when it can:

- state the boundary precisely;
- demonstrate the main positive law;
- demonstrate at least one negative boundary/counterexample;
- adapt one real rag-ttc path;
- publish a composition-ready contract.

Open questions belong in stretch work or the second pass.

# Primary theory references

These readings motivate the laws but do not prescribe implementation architecture:

- [Keeping CALM: When Distributed Consistency is Easy](https://arxiv.org/abs/1901.01930)
- [A comprehensive study of Convergent and Commutative Replicated Data Types](https://inria.hal.science/inria-00609399v2/document)
- [W3C PROV-DM: The PROV Data Model](https://www.w3.org/TR/prov-dm/)
- [Provenance Semirings](https://web.cs.ucdavis.edu/~green/papers/pods07.pdf)
- [QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs](https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf)
- [Differential Dataflow](http://cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf)
- [DBSP: Automatic Incremental View Maintenance for Rich Query Languages](https://www.vldb.org/pvldb/vol16/p1601-budiu.pdf)
- [Security Policies and Security Models](https://www.cs.purdue.edu/homes/ninghui/readings/AccessControl/goguen_meseguer_82.pdf)

# Deliverable map

- `projects/` contains 13 independently assignable briefs in Markdown and PDF.
- `fixtures/` contains neutral shared test data.
- `schemas/` contains the common result and interchange schemas.
- `90-composition-pass-playbook.md` defines the later integration experiments.
- `reference/` contains the prior semantic handbook and repository inventory.
- `rag-ttc-research-projects-compendium.*` combines the charter, all briefs, and composition playbook.
