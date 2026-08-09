---
title: "rag-ttc Semantic Research Projects Compendium"
subtitle: "Charter, 13 project briefs, and composition playbook"
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

# How to use this compendium

This volume contains the program charter, 13 independent project briefs, and the second-pass composition playbook. Each project may be distributed separately from `projects/`. The charter defines common fixtures, evidence levels, deliverables, and review rubric.

\newpage

# Part I - Program charter

## Purpose

This package defines a first-pass research program for understanding and refining the semantics of `rag-ttc`. The program does not ask one team to redesign the whole repository. It decomposes the system into small, independently executable projects, each centered on one falsifiable semantic boundary.

The first pass answers questions such as:

- What counts as the same source, request, fact, derivation, view, or operation?
- Which states can be merged without order dependence?
- Which operations only add candidates and which deliberately select or remove them?
- When do retries, caching, batching, concurrency, and backend replacement preserve meaning?
- What can be replayed, incrementally updated, migrated, cited, or safely disclosed?

The second pass, described in `90-composition-pass-playbook.md`, replaces local fakes with neighboring project implementations and tests whether the contracts compose.

## Architectural starting point

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

## Project catalog

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

### Suggested cohorts

A practical assignment plan is:

- **Cohort A - foundations:** P01, P02, P03, and P04. These projects define identity, canonical state, lawful merge, and views.
- **Cohort B - execution and recursion:** P05 and P06. These projects test fixed-point evaluation and operational transparency.
- **Cohort C - RAG subsystems:** P07, P08, and P09. These projects study knowledge, connected retrieval, and tool-agent turns.
- **Cohort D - lifecycle and assurance:** P10, P11, P12, and P13. These projects study replay, updates, backends/migration, and security.

Projects may start concurrently. Cohort labels are for review meetings and eventual composition, not implementation dependencies.

## Shared research method

### Two implementations per project

Every team builds:

1. A **standalone executable semantic model**. It should be small enough to understand completely and should use deterministic fakes or recorded effects.
2. A **rag-ttc adapter** against the supplied source snapshot. The adapter tests whether the proposed model captures real structures and where compatibility fails.

The standalone model prevents repository complexity from hiding a semantic mistake. The adapter prevents a beautiful toy model from remaining irrelevant.

### Falsification first

For each proposed law, build at least one intentionally bad implementation or adversarial fixture that should fail. A test suite that only passes the preferred implementation is not sufficient evidence that the law was stated or tested correctly.

Every hypothesis receives one of these outcomes:

- **Supported:** the stated tests and experiments did not find a counterexample.
- **Falsified:** a minimal reproducible counterexample exists.
- **Mixed:** the result depends on a clarified precondition or contract variant.
- **Not tested:** required evidence was unavailable.

### Evidence levels

Use these labels in reports and `results.json`:

| Evidence label | Meaning |
|---|---|
| `proved_model` | A direct argument from the executable model or constructors, with assumptions stated |
| `exhaustive_finite` | Every state or schedule in a finite bounded universe was checked |
| `property_tested` | Random/generated testing with saved seeds and shrinking |
| `empirical` | Measurements on selected workloads; no universal claim |
| `conjectural` | Plausible design hypothesis not yet validated |

Do not label an empirical result as a proof. Do not dismiss a finite counterexample because a broader empirical average looks good.

## Shared vocabulary

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

## Repository and baseline protocol

### Supplied snapshot

- Source archive: `rag-ttc.zip`
- Module: `github.com/the-tree-center/rag-ttc`
- Declared Go version: `1.26.5`
- Static inventory: 449 Go files and 151 Go test files in the reviewed snapshot
- Source checksum: see `reference/SHA256SUMS.txt`

The prior handbook review was static because the analysis environment could not use the declared toolchain and dependencies. Each team must establish an executable baseline in its own approved environment.

### Baseline gate

Before semantic changes:

1. Record Go/toolchain, OS/architecture, module cache state, and source commit/archive digest.
2. Run `go test ./...` and preserve full output.
3. Run the package-specific tests relevant to the assignment at least three times where scheduling may matter.
4. Freeze representative current outputs as compatibility fixtures.
5. Record any pre-existing failures; do not silently fix unrelated tests in the research branch.
6. Build a no-network test mode using fakes or captured effects.

A project may proceed with a partially failing baseline, but must isolate those failures from its own claims.

## Shared fixture pack

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

## Shared interchange contracts

The program intentionally does not require a shared Go implementation in pass one. It requires neutral versioned files:

- `schemas/project-result.schema.json` - common assessment output;
- `schemas/semantic-interchange.schema.json` - minimal fact/derivation envelope;
- `schemas/operation-trace.schema.json` - stable operational trace event;
- project-specific schemas named in each brief.

Every project must emit `results.json`. This allows program-level comparison without requiring one monorepo branch.

## Common test design

### Unit tests

Use examples for exact edge behavior: missing IDs, invalid spans, conflicts, tie breaks, budget boundaries, cache corruption, unknown schema versions, and explicit error categories.

### Law tests

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

### Model-based tests

Where stateful behavior matters, implement a simple reference model and compare arbitrary operation sequences against the real implementation. P03, P06, P11, and P12 are expected to use this method.

### Schedule tests

Do not rely only on the Go race detector. It detects data races, not semantic order dependence. Enumerate all completion orders for small fixtures and use a deterministic randomized scheduler for larger tests.

### Fault tests

Inject failure at semantically meaningful boundaries: before an external effect, after the effect but before response delivery, after admission but before persistence, during batch write, and during manifest sealing.

## Common evaluation dimensions

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

## Review rubric

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

## Program-wide non-goals

- Do not build a new workflow language or central scheduler.
- Do not replace typed domain APIs with one generic `any`-based framework.
- Do not claim model factuality, entailment, or exact reproducibility beyond tested guarantees.
- Do not optimize away provenance before the reference semantics are stable.
- Do not require live paid providers for correctness tests.
- Do not merge all student branches during pass one.
- Do not treat deterministic ordering alone as proof of lawful merge or retry safety.
- Do not force approximate retrieval backends into an exact-equivalence claim.

## Team hand-off checklist

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

## Governance and coordination

### Weekly project review

Each team reports only four items:

1. Strongest new invariant or contract statement.
2. Strongest counterexample or uncertainty.
3. Current executable artifact.
4. One interface decision that may affect another project.

This keeps cross-project coordination semantic rather than branch-level.

### Contract changes

A team may revise a shared contract by publishing:

- the old and new schema versions;
- a migration or explicit incompatibility statement;
- the counterexample motivating the change;
- affected project codes;
- updated conformance fixture.

No in-place contract mutation is allowed after another team has consumed it.

### Stop conditions

A project should stop expanding scope when it can:

- state the boundary precisely;
- demonstrate the main positive law;
- demonstrate at least one negative boundary/counterexample;
- adapt one real rag-ttc path;
- publish a composition-ready contract.

Open questions belong in stretch work or the second pass.

## Primary theory references

These readings motivate the laws but do not prescribe implementation architecture:

- [Keeping CALM: When Distributed Consistency is Easy](https://arxiv.org/abs/1901.01930)
- [A comprehensive study of Convergent and Commutative Replicated Data Types](https://inria.hal.science/inria-00609399v2/document)
- [W3C PROV-DM: The PROV Data Model](https://www.w3.org/TR/prov-dm/)
- [Provenance Semirings](https://web.cs.ucdavis.edu/~green/papers/pods07.pdf)
- [QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs](https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf)
- [Differential Dataflow](http://cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf)
- [DBSP: Automatic Incremental View Maintenance for Rich Query Languages](https://www.vldb.org/pvldb/vol16/p1601-budiu.pdf)
- [Security Policies and Security Models](https://www.cs.purdue.edu/homes/ninghui/readings/AccessControl/goguen_meseguer_82.pdf)

## Deliverable map

- `projects/` contains 13 independently assignable briefs in Markdown and PDF.
- `fixtures/` contains neutral shared test data.
- `schemas/` contains the common result and interchange schemas.
- `90-composition-pass-playbook.md` defines the later integration experiments.
- `reference/` contains the prior semantic handbook and repository inventory.
- `rag-ttc-research-projects-compendium.*` combines the charter, all briefs, and composition playbook.

\newpage

# Part II - Independent project briefs


\newpage

# P01 - Semantic Identity and Cache Fingerprints

## Assignment summary

**Project code:** P01  
**Track:** Foundations: identity and reproducibility  
**Suggested duration:** 4-6 weeks  
**Suggested team:** 1-2 students  
**Program priority:** Critical path

Define when two rag-ttc values represent the same semantic input or output, then turn that definition into canonical encoders, versioned fingerprints, cache-key contracts, and regression tests. This project establishes the identity boundary on which every later reproducibility claim depends.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/digest`
- `pkg/rag/types.go`
- `pkg/rag/evidence_identity.go`
- `pkg/rag/chunking`
- `pkg/rag/representations`
- `pkg/rag/embedding`
- `pkg/rag/generation`
- `pkg/rag/reranking`
- `pkg/rag/connected/runtime.go`
- `pkg/rag/connectedconfig`
- `pkg/flow/store.go`
- `pkg/execution/cache.go`
- `pkg/rag/providers/geppetto/profile`

### Why this project exists

- A cache key is a claim that all omitted differences are semantically irrelevant. The repository has several local identity schemes, but no single explicit rule for deciding which configuration fields affect meaning.
- Canonical chunks use content digests, representations bind model and prompt data, and execution caches use separate key builders. These are strong ingredients, but they can drift unless tested against a shared identity contract.
- The handbook identified concrete candidates for drift: the fallback evidence digest uses a different encoding path, the connected runtime semantic digest appears not to include every fusion parameter, and generation identity may omit inference settings that can alter text.
- Later projects need stable fact IDs, derivation IDs, request IDs, and artifact fingerprints. An error here invalidates merge, provenance, replay, and backend-conformance results.

### Source-level observations to verify

- `pkg/rag/evidence_identity.go` derives a missing content digest through `digest.JSON(item.Chunk.Text)`; compare this with canonical chunk construction.
- `pkg/rag/connected/runtime.go` stores `RRFConstant` in runtime options and behavior; inspect the exact `SemanticDigest` construction for sensitivity.
- Generation and reranking caches have separate wrappers and key builders; identify whether their configuration snapshots include all output-affecting settings.
- `Representation` already separates source evidence from generated retrieval material and records model and prompt digest, providing a useful identity precedent.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. Which fields in each core type are semantic identity, source lineage, observation metadata, presentation metadata, or operational trace?
2. Can rag-ttc define a small family of canonical, versioned encoders instead of ad hoc JSON hashing at call sites?
3. For each cache family, what is the minimal sufficient key: the smallest key that never aliases two behaviorally different invocations under the declared contract?
4. How should model/provider settings be divided between secret credentials, execution-only policy, and non-secret semantic inference fingerprint?
5. How should identity versions evolve without silently reusing artifacts created under older semantics?
6. Can semantic equality be checked independently of Go map iteration order, JSON field order, path spelling, timestamps, and non-semantic scores?

### Falsifiable hypotheses

1. A versioned canonical encoder plus field-classification table can make every cache family pass sensitivity and irrelevance tests generated from its public configuration.
2. Replacing the evidence fallback with the canonical text digest will make legacy and fully populated evidence records produce the same identity.
3. Adding the RRF constant and fusion algorithm version to connected-runtime identity will distinguish configurations that can reorder fused results.
4. A non-secret inference fingerprint derived from all output-affecting model settings can make generation cache hits observationally transparent for deterministic or recorded provider responses.
5. The repository contains at least one additional identity field omission or accidental inclusion beyond the three candidates already identified.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Inventory all digest and cache-key constructors in the repository and classify their fields.
- Specify canonical byte encodings for text, structured values, ordered lists, unordered sets/maps, optional values, floats, paths, and version tags.
- Implement a small `semanticid` reference package with explicit domain separators and algorithm versions.
- Build sensitivity tests that mutate one field at a time and irrelevance tests that mutate operational-only fields.
- Patch or adapt at least three current identity paths: evidence identity, connected-runtime identity, and one generation or reranking cache identity.
- Measure artifact invalidation caused by corrected keys on representative fixtures.

### Explicit non-goals

- Designing a globally unique identity service or distributed naming authority.
- Hiding all configuration behind reflection-based generic hashing.
- Claiming that equal prompts imply equal stochastic model outputs without a recorded response or deterministic provider contract.
- Changing user-visible IDs merely for aesthetic uniformity.
- Encrypting secrets or implementing credential management.

## System to build

1. A field-classification catalog for core structs and cache inputs. Each field must be labeled semantic, lineage, observation, presentation, operational, or secret.
2. A canonical encoding library with domain-separated functions such as `Text`, `Ordered`, `Set`, `Struct`, and `Fingerprint`.
3. A declarative cache-family specification that states key inputs, ignored inputs, schema version, and expected sensitivity.
4. A mutation-based conformance harness that produces one-field perturbations and verifies key changes or stability according to the specification.
5. A compatibility report and minimal patches for the identified rag-ttc paths.
6. A migration note describing cache invalidation and artifact-version handling when identity rules change.

### Proposed API sketch

```go
package semanticid

type Digest string
type Domain string
type Version string

type Fingerprinter interface {
    SemanticFingerprint() (Digest, error)
}

type FieldRole string
const (
    Semantic    FieldRole = "semantic"
    Lineage     FieldRole = "lineage"
    Observation FieldRole = "observation"
    Presentation FieldRole = "presentation"
    Operational FieldRole = "operational"
    Secret      FieldRole = "secret"
)

type CacheContract[I any] struct {
    Family  string
    Version Version
    Key     func(I) (Digest, error)
    Mutations []Mutation[I]
}

type Mutation[I any] struct {
    Name       string
    Role       FieldRole
    Apply      func(I) I
    MustChange bool
}

func Text(domain Domain, version Version, value string) Digest
func Canonical(domain Domain, version Version, value any) (Digest, error)
func Ordered(domain Domain, version Version, parts ...Digest) Digest
func Unordered(domain Domain, version Version, parts ...Digest) Digest
func CheckCacheContract[I any](c CacheContract[I], seeds []I) Report
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Determinism | The same semantic input always produces the same digest. | Run across process restarts, map insertion orders, and repeated encodes. |
| Semantic sensitivity | Changing any declared meaning-affecting field changes the key. | One-field mutation suite for every cache family. |
| Operational irrelevance | Changing retry count, timing, logging, or display metadata does not change semantic identity unless explicitly declared. | Negative mutation suite with documented exceptions. |
| Representation independence | Equivalent canonical values hash equally even if Go allocation, map order, or source formatting differs. | Permutation and normalization fixtures. |
| Domain separation | The same bytes used as a chunk, prompt, and request do not collide by construction. | Cross-domain test vectors. |
| Version separation | Changing the identity algorithm version changes the namespace. | Golden vectors for at least two versions. |
| Cache transparency | A cache hit is observationally equivalent to recomputation under the cache contract. | Compare outputs and semantic traces using a recorded provider. |
| No secret leakage | Fingerprints do not serialize raw credentials. | Static scan and adversarial credential fixtures. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: Legacy evidence digest compatibility

**Setup.** Create two equal chunks, one with a populated `ContentDigest` and one using the fallback path.

**Procedure.** Compute identities under the current code, the proposed canonical code, and a direct `digest.Text` oracle. Repeat with quotes, Unicode, newlines, and empty strings.

**Expected observations.** The corrected identity matches canonical chunk identity for every byte string. The current mismatch, if reproduced, is reduced to a minimal fixture.

**Failure interpretation.** A remaining mismatch means canonical text identity is not uniformly defined or a chunk field other than text is implicitly part of the intended identity.
### Scenario 2: Connected fusion sensitivity

**Setup.** Use fixed baseline and knowledge hit lists for which changing the RRF constant changes at least one fused score or ordering.

**Procedure.** Vary `RRFConstant`, channel weights, limits, gate policy, database digest, and execution-only options. Compare runtime semantic digests and final views.

**Expected observations.** Every behavior-affecting variation changes the semantic digest; operational-only variations do not.

**Failure interpretation.** A key collision with a changed final view is a correctness defect. A key change with no possible semantic effect is an over-keying candidate.
### Scenario 3: Generation profile matrix

**Setup.** Construct a recorded generator whose output deterministically reflects temperature, seed, reasoning effort, response format, stop sequences, and model identity.

**Procedure.** Enumerate profile mutations and compare generation keys, provider requests, and outputs.

**Expected observations.** The cache key changes exactly for settings that the declared generator contract allows to affect output.

**Failure interpretation.** Aliasing indicates stale response reuse; excessive variation reduces cache utility and exposes an unclear contract.
### Scenario 4: Cross-version artifact audit

**Setup.** Build a small index, generation cache, and experiment artifact under identity version v1.

**Procedure.** Switch to v2 and attempt reads with explicit migration, no migration, and mixed-version manifests.

**Expected observations.** The system rejects or namespaced-separates incompatible artifacts and reports actionable provenance.

**Failure interpretation.** Silent reuse across versions invalidates reproducibility.


### Metrics

- Number of identity/cache families inventoried and covered by an explicit contract.
- Mutation coverage: semantic fields detected, operational fields ignored, and unclassified fields remaining.
- False-alias count: key equality where the declared output can differ.
- False-split count: key inequality for inputs declared semantically equivalent.
- Cache hit-rate change and invalidated artifact volume after corrected keys.
- Encoding throughput and allocation cost for representative values.
- Number and severity of previously unknown identity defects found.

### Fault injection

- Randomized Go map insertion order and JSON field order.
- Path aliases, relative versus absolute paths, and equivalent cleaned paths.
- Missing legacy digests and partially populated records.
- NaN, infinities, negative zero, and float formatting edge cases where relevant.
- Provider profiles that differ only in one nested inference setting.
- Identity-version skew between writer and reader.
- Credentials and tokens embedded in configuration objects.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - inventory and taxonomy | All digest/key call sites cataloged with field roles and current tests. |
| M2 - canonical model | Standalone encoder, golden vectors, and mutation harness complete. |
| M3 - defect reproduction | At least the named candidate defects confirmed or refuted with minimal fixtures. |
| M4 - adapters and patches | Three or more rag-ttc identity paths pass the new conformance suite. |
| M5 - evaluation | Cache/artifact impact measured and migration recommendation written. |
| M6 - hand-off | Versioned contract, fixtures, report, and demo reviewed independently. |

## Acceptance gates

- Every public fingerprint has a domain name and algorithm/schema version.
- The field taxonomy has no unclassified field for the studied cache families.
- Generated mutation tests fail against at least one intentionally broken key function.
- Legacy evidence with and without a stored digest has one canonical identity.
- Connected fusion identity responds to all demonstrated behavior-changing parameters.
- Generation identity includes a documented non-secret inference fingerprint or a justified alternative.
- No raw credential appears in test fingerprints, logs, or fixtures.
- The report quantifies both correctness improvement and cache-cost impact.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- Plain JSON values and configuration snapshots.
- Recorded provider request/response fixtures.
- Core rag-ttc values such as `Chunk`, `Evidence`, connected options, and model profiles.

### Outputs offered to later projects

- `semantic-fingerprint/v1` strings with domain and version metadata.
- Field-role catalog in machine-readable JSON.
- Golden digest vectors for use by P02, P03, P06, P10, and P12.
- Cache contract reports containing mutation outcomes.

### Expected composition experiments

- Replace locally defined fact and derivation IDs in P02 with P01 fingerprints and rerun provenance tests.
- Use P01 request fingerprints as operation IDs in P06 and verify trace correlation without affecting semantic outputs.
- Use versioned fingerprints in P10 replay manifests and test mixed-version rejection.
- Use P01 schema/version tags in P12 migration experiments.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| Over-general canonicalizer | Prefer domain-specific typed encoders. Generic reflection may erase intentional ordering or option semantics. |
| Equating deterministic key with deterministic model | State cache transparency only for a recorded response or explicit deterministic-provider contract. |
| Hash algorithm distraction | Focus on canonical input bytes and versioning; cryptographic primitive choice is secondary for this project. |
| Unstable external profiles | Snapshot and normalize the non-secret semantic subset before hashing. |
| Over-keying all configuration | Use irrelevance tests and report cache utility costs. |

## Questions the final report must answer

1. What exact equivalence relation does each studied identity implement?
2. Which current keys are under-specified, over-specified, or correct?
3. Which defect candidates were confirmed, refuted, or refined?
4. What is the minimum sufficient generation inference fingerprint?
5. How should identity versions be recorded in indexes, caches, traces, and experiments?
6. What compatibility break would the recommended changes cause?
7. What new counterexample most changed the team’s initial design?

## Stretch investigations

- Cross-language golden vectors implemented in a second language.
- A static analyzer that flags digest construction from structs containing unclassified fields.
- Minimal-key inference using differential mutation over recorded calls.
- An artifact migration tool that explains which fingerprint component changed.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/semantic-identity-cache-fingerprints` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, sections 4.1-4.4, 6.1, 7.3, 8.1, 10.4, and 11 Phase 0.
- Go specification sections on comparison, maps, and numeric values.
- RFC 8785, JSON Canonicalization Scheme, as a comparison point rather than a mandatory implementation.
- NIST FIPS 180-4 for SHA-2 terminology and domain-separation considerations.
- QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs, for generated law testing methodology.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# P02 - Canonical Facts and Provenance Kernel

## Assignment summary

**Project code:** P02  
**Track:** Foundations: semantic data model  
**Suggested duration:** 5-7 weeks  
**Suggested team:** 1-2 students  
**Program priority:** Critical path

Build the smallest useful semantic state for rag-ttc: immutable canonical facts plus one or more derivations explaining how each fact entered the state. Validate whether this model can cover source chunks, retrieval observations, knowledge facts, and tool evidence without collapsing their important differences.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/rag/types.go`
- `pkg/rag/components.go`
- `pkg/rag/chunking`
- `pkg/rag/representations`
- `pkg/rag/knowledge/types.go`
- `pkg/rag/knowledge/deterministic.go`
- `pkg/rag/toolanswer/evidence.go`
- `pkg/ttcrag/types.go`
- `pkg/rag/answering/types.go`
- `pkg/rag/agenttrace`
- `pkg/app/session`
- `pkg/digest`

### Why this project exists

- The repository has several evidence-like structures: immutable chunks, ranked `Evidence`, knowledge `Fact` with supporting spans, tool evidence ledgers, and answer traces. They share provenance needs but currently encode identity and derivation differently.
- `rag.Evidence` combines a stable source chunk with query-specific rank and scores. This makes it difficult to state whether two evidence values are the same fact, two observations of one fact, or different selected views.
- A canonical fact/provenance kernel can preserve source truth, multiple discovery paths, and auditability while allowing ranking and execution metadata to vary independently.
- This project tests whether a heterogeneous fact store can remain typed and explicit rather than becoming a generic `map[string]any` framework.

### Source-level observations to verify

- `pkg/rag/types.go` defines immutable `Document`, `Chunk`, and `Representation`, but `Evidence` adds rank and scores to the hydrated chunk.
- `pkg/rag/knowledge/types.go` already models facts with source evidence spans, but confidence/method/evidence are combined in one domain object.
- `pkg/rag/toolanswer` and `pkg/ttcrag` maintain turn-scoped evidence and citation labels; inspect whether those labels are semantic identity or presentation state.
- `pkg/rag/answering` exposes staged observations that should remain operational trace rather than canonical evidence.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. What is the minimum common structure shared by source chunks, representations, knowledge concepts/facts, retrieval observations, and tool-produced evidence?
2. Should retrieval hits themselves be facts, derivations, observations, or view annotations?
3. How are alternative derivations represented without duplicating the canonical fact payload?
4. What must be included in a derivation to support replay, audit, security propagation, and deletion impact analysis?
5. Can fact codecs preserve strong Go types while supporting one heterogeneous state and neutral JSON interchange?
6. How should rejected admissions and invalid derivations be represented: absent, negative facts, or a separate diagnostic stream?

### Falsifiable hypotheses

1. A fact envelope containing `(kind, schema, canonical payload, fact ID)` plus a derivation set can represent the relevant rag-ttc semantic objects without moving rank or score into fact identity.
2. Retrieval scores and ranks are best represented as observation records or view entries, not canonical facts.
3. Every admitted non-seed fact can be required to have at least one derivation whose dependencies exist and whose rule/configuration identity is explicit.
4. Typed codecs at package boundaries provide enough safety to avoid a generic untyped fact API in application code.
5. Knowledge `Fact.Evidence` and tool citation records can be mapped into the same provenance graph while preserving their domain-specific validation rules.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Define versioned `Fact`, `FactID`, `FactKind`, `Derivation`, `DerivationID`, and `State` interchange forms.
- Implement typed codecs for at least chunks, representations, knowledge facts, retrieval observations, and tool evidence.
- Implement provenance validation: dependency existence, acyclicity or well-founded rank where required, rule identity, and source-span checks.
- Represent multiple derivations for the same fact and retain them through serialization and merge.
- Build an independent verifier that can validate a result bundle without running retrieval or generation.
- Adapt one answering path to emit canonical facts plus a selected evidence view.

### Explicit non-goals

- Creating a universal ontology for all claims or solving entity resolution.
- Proving factual truth or textual entailment of arbitrary generated claims.
- Replacing domain types in `pkg/rag` or `pkg/rag/knowledge` with one untyped struct.
- Specifying execution retries, cache behavior, or scheduling; those belong to P06.
- Implementing recursive closure; P05 consumes this kernel.

## System to build

1. A standalone fact/provenance package with immutable values, canonical encoding, typed codec registration, and deterministic serialization.
2. A provenance graph validator with clear error categories and a small trusted core.
3. Adapters from current `rag.Chunk`, `rag.Representation`, `rag.Evidence`, `knowledge.Fact`, and tool evidence records.
4. A proof-carrying answer bundle that contains selected fact IDs, all required canonical payloads, derivations, corpus/config fingerprints, and an answer observation.
5. A provenance inspection CLI that renders dependency trees/DAGs and explains alternative derivations.
6. A corpus of valid and deliberately malformed provenance fixtures.

### Proposed API sketch

```go
package derive

type FactID string
type DerivationID string
type FactKind string

type Fact struct {
    ID      FactID          `json:"id"`
    Kind    FactKind        `json:"kind"`
    Schema  string          `json:"schema"`
    Payload json.RawMessage `json:"payload"`
}

type Derivation struct {
    ID          DerivationID      `json:"id"`
    Output      FactID            `json:"output"`
    Rule        string            `json:"rule"`
    RuleVersion string            `json:"rule_version"`
    Inputs      []FactID          `json:"inputs"`
    RequestID   string            `json:"request_id,omitempty"`
    ConfigID    string            `json:"config_id,omitempty"`
    Observation json.RawMessage   `json:"observation,omitempty"`
}

type State struct {
    Facts       map[FactID]Fact
    Derivations map[DerivationID]Derivation
    ByOutput    map[FactID][]DerivationID
}

type Codec[T any] interface {
    Encode(T) (Fact, error)
    Decode(Fact) (T, error)
}

type ValidationReport struct {
    Valid bool
    Errors []ValidationError
}

func AddSeed(s State, f Fact, sourceRef string) (State, error)
func AddDerived(s State, f Fact, d Derivation) (State, error)
func Verify(s State) ValidationReport
func Explain(s State, id FactID) Explanation
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Fact immutability | One fact ID always names one canonical payload and schema. | Reject conflicting payloads for an existing ID. |
| Identity consistency | Encoding, decoding, and re-encoding a typed value preserves its fact ID. | Round-trip tests for every codec. |
| Provenance completeness | Every non-seed admitted fact has at least one valid derivation. | Verifier and malformed-fixture suite. |
| Dependency closure | Every derivation input is present or explicitly externalized. | Dangling-input rejection tests. |
| Alternative preservation | Adding a second valid derivation does not replace the first. | Diamond-provenance fixture. |
| Observation separation | Changing rank, score, or completion time does not change source fact identity. | Mutation tests over adapted `rag.Evidence`. |
| Deterministic serialization | Equivalent states serialize identically after canonical ordering. | Permutation and round-trip golden files. |
| Verifier independence | A bundle can be validated without invoking the original retriever or model. | Offline verifier demonstration. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: One chunk, multiple discovery paths

**Setup.** The same canonical chunk is returned by BM25, vector search, and a knowledge lookup with different scores and ranks.

**Procedure.** Adapt all three outputs into the fact state, serialize, deserialize, and inspect the explanation.

**Expected observations.** There is one chunk fact, three distinct observations or derivations, and no score in the fact ID.

**Failure interpretation.** Duplicated facts or overwritten derivations indicate an unclear identity/provenance boundary.
### Scenario 2: Diamond provenance

**Setup.** Two independent rules derive the same normalized claim from different source chunks, and a downstream fact depends on that claim.

**Procedure.** Add derivations in all permutations, validate, and render the explanation DAG.

**Expected observations.** The downstream fact remains one fact with a dependency on the canonical claim; both alternative supports survive.

**Failure interpretation.** Order-dependent loss or duplicate downstream identity means derivation identity or merge policy is wrong.
### Scenario 3: Malformed proof bundle

**Setup.** Create bundles with a missing dependency, conflicting payload under one ID, cyclic dependencies, invalid source span, and unknown schema.

**Procedure.** Run the independent verifier and compare error categorization against expected diagnostics.

**Expected observations.** Every malformed bundle is rejected deterministically with a useful local explanation.

**Failure interpretation.** Acceptance is unsound; nondeterministic or vague errors make the verifier unsuitable as a trusted boundary.
### Scenario 4: Answer package inspection

**Setup.** Run a small recorded answering fixture through the adapter.

**Procedure.** Create an answer bundle, remove the original indexes and caches, and verify/explain the selected evidence offline.

**Expected observations.** Source identity, all selected facts, and their derivations remain inspectable without the runtime.

**Failure interpretation.** A hidden runtime dependency or missing semantic input prevents durable audit.


### Metrics

- Coverage of existing evidence-like types by typed codecs.
- Verifier trusted-code size and cyclomatic complexity.
- Bytes per fact and derivation; duplication relative to current artifacts.
- Number of alternative derivations retained in adversarial fixtures.
- Percentage of malformed fixtures rejected with the expected category.
- Time to encode, merge, serialize, and verify states of increasing size.
- Number of downstream fields removed from canonical identity because they are observations or views.

### Fault injection

- Conflicting payloads under the same fact ID.
- Dangling and cyclic derivation dependencies.
- Duplicate derivation IDs with different contents.
- Unknown fact schema versions and malformed payloads.
- Incorrect byte/character source spans and quote mismatches.
- Alternative derivations arriving in different orders.
- Scores and ranks changed while source payload stays fixed.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - semantic inventory | Evidence-like values classified as fact, derivation, observation, view, or trace. |
| M2 - standalone kernel | Fact, derivation, codec, state, and verifier pass core unit tests. |
| M3 - adapters | At least five current rag-ttc types mapped with round-trip tests. |
| M4 - proof bundle | Offline answer package verifies and explains selected evidence. |
| M5 - adversarial evaluation | Malformed and alternative-provenance fixtures evaluated at scale. |
| M6 - hand-off | Versioned schemas, neutral fixtures, API rationale, and composition ports complete. |

## Acceptance gates

- The project states exactly what a fact is and what it is not.
- A fact ID cannot silently refer to two payloads.
- Every non-seed fact in the accepted state has a verifier-accepted derivation.
- Alternative derivations survive insertion order changes and serialization.
- Rank, retrieval score, reranker score, and citation display label are excluded from canonical source-fact identity.
- At least five typed codecs round-trip without exposing `any` to normal callers.
- The offline verifier rejects all required malformed fixtures.
- The final report identifies at least one rag-ttc type that should not be mapped into the canonical fact state and explains why.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- Versioned fingerprints from P01, or the local `semantic-fingerprint/v1` fixture contract.
- Current rag-ttc source, retrieval, knowledge, and tool evidence records.
- Neutral fixture schemas for source spans and provider observations.

### Outputs offered to later projects

- `fact-state/v1`, `fact/v1`, and `derivation/v1` JSON schemas.
- Typed codec examples and a verifier API.
- Proof-carrying answer bundle fixture for P03, P05, P09, P10, P11, P12, and P13.
- Explanation DAG export in deterministic JSON and Graphviz DOT.

### Expected composition experiments

- Use P03 merge to combine two P02 states and verify that every derivation remains valid.
- Use P04 views to rank fact IDs without changing P02 canonical payloads.
- Use P05 rules to emit P02 facts and derivations, then verify closure provenance.
- Use P13 labels as an optional fact/derivation annotation and test inherited restrictions.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| Universal-object trap | Keep domain payloads typed and versioned; the envelope is common, not the ontology. |
| Provenance bloat | Measure structural sharing, compact IDs, and selective bundle export rather than deleting alternative proofs. |
| Confusing observation with derivation | Document whether a record asserts a new fact or merely reports how an existing fact was found. |
| Cycles from normalization | Define whether derivations must be acyclic, rank-bounded, or support explicit equivalence components. |
| False proof language | Call the object a derivation or evidence certificate unless the rule is actually logically sound. |

## Questions the final report must answer

1. Which current values became facts, derivations, observations, views, traces, or diagnostics?
2. What is the exact trusted core of the verifier?
3. How are seed facts distinguished from derived facts?
4. How are alternative derivations identified and ordered?
5. Which provenance fields are required for audit, replay, deletion, and security, and which are optional?
6. What storage overhead is introduced, and what compaction preserves semantics?
7. Where did the common envelope fail to capture an important domain distinction?

## Stretch investigations

- Compact provenance using hash-consed DAG nodes or semiring annotations.
- A proof explanation UI integrated with the existing chat UI.
- Typed generic codecs generated from Go declarations.
- Selective disclosure bundles that reveal only the derivation slice needed for one answer.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/canonical-facts-provenance-kernel` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, sections 3, 5, 6.1-6.5, 8.2, 8.7, 8.9, 9.14, and 10.6.
- W3C PROV-DM: The PROV Data Model, for entity/activity/agent distinctions and provenance relations.
- Provenance Semirings, Green, Karvounarakis, and Tannen, PODS 2007, for the idea that one result can retain multiple derivations.
- Content-addressable storage designs such as Git objects, as an engineering comparison for immutable payload identity.
- QuickCheck for generated constructor and round-trip laws.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# P03 - Lawful Merge and Deterministic Evidence Ledger

## Assignment summary

**Project code:** P03  
**Track:** Foundations: composition and concurrency  
**Suggested duration:** 5-7 weeks  
**Suggested team:** 1-2 students  
**Program priority:** Critical path

Design and validate the add-only state merge used when retrieval channels, workers, retries, or tool calls produce overlapping facts. The project must determine exactly when merge can be associative, commutative, and idempotent, and isolate all policy choices that make admission order-sensitive.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/rag/ordering.go`
- `pkg/rag/retrieval/retrieval.go`
- `pkg/rag/toolanswer/evidence.go`
- `pkg/rag/toolanswer/search.go`
- `pkg/ttcrag/search.go`
- `pkg/ttcrag/types.go`
- `pkg/execution/map.go`
- `pkg/execution/cached_map.go`
- `pkg/flow/batch.go`
- `pkg/flow/bulk.go`
- `pkg/rag/answering/context.go`

### Why this project exists

- rag-ttc already uses deterministic ordering in many places, but concurrent tool evidence admission can still couple semantic output to completion order when count or rune budgets are consumed as results arrive.
- Retries, duplicate queue delivery, channel overlap, and parallel execution should not change the canonical evidence state. That property requires a lawful merge, not merely a mutex.
- Top-k, first-N, token budgets, citation numbering, and conflict resolution are policy decisions. Placing them inside add-only merge destroys permutation invariance and makes distributed execution harder to reason about.
- This project supplies the concrete algebra and test harness needed before recursive closure, incremental updates, or distributed composition can be trusted.

### Source-level observations to verify

- `pkg/ttcrag/search.go` uses a mutex around a turn ledger; inspect how evidence labels and count/rune budgets are assigned relative to concurrent completion.
- `pkg/rag/ordering.go` and retrieval code already contain stable ordering helpers that can inform view policy.
- `pkg/execution` and `pkg/flow` restore order in some batch operations; distinguish restored input order from semantic merge invariance.
- `pkg/rag/toolanswer/evidence.go` provides another evidence ledger implementation to compare against `pkg/ttcrag`.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. What is the canonical merge behavior for equal fact IDs, equal derivation IDs, conflicting payloads, duplicate observations, and alternative derivations?
2. Which current ledgers are true add-only states and which are ordered views disguised as state?
3. Can evidence budgets be expressed as a deterministic view over an unbounded candidate ledger rather than as arrival-time admission?
4. What fairness and delivery assumptions are necessary for sequential and parallel executions to converge to the same semantic state?
5. How should conflicts be reported without introducing last-write-wins semantics?
6. Can a compact merge certificate explain why two independently built states are compatible or incompatible?

### Falsifiable hypotheses

1. A state represented as maps from canonical IDs to immutable payloads and sets of derivations admits an associative, commutative, idempotent merge when conflicts are surfaced rather than overwritten.
2. Citation labels and bounded evidence selection can be moved to a deterministic post-merge view without changing source facts or tool observations.
3. All completion-order permutations of a fixed multiset of successful operations produce the same canonical state under the proposed ledger.
4. Current order-sensitive tool evidence behavior can be reproduced with a small fixture and eliminated by separating candidate collection from budgeted selection.
5. A merge law suite will find at least one hidden order dependence outside the named tool ledger path.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Specify merge for facts, derivations, observations, diagnostics, and conflicts.
- Implement a standalone immutable or copy-on-write `State.Join` plus a mutable concurrency-safe facade.
- Build exhaustive permutation tests for small operation sets and randomized schedule tests for larger sets.
- Refactor or adapt one tool evidence path into collect candidates, join candidates, then deterministically label/select.
- Define deterministic tie-break rules and prove that they are view policy rather than canonical merge semantics.
- Produce a conflict format that preserves both incompatible values and prevents silent success.

### Explicit non-goals

- Implementing a general distributed database or network consensus protocol.
- Making non-monotone top-k selection coordination-free.
- Solving semantic equivalence of natural-language claims.
- Benchmarking every Go concurrent map implementation.
- Replacing `flow` scheduling mechanics.

## System to build

1. A reference join-semilattice-like state over facts and derivations with deterministic conflict reporting.
2. A linearizable mutable ledger facade whose snapshot is defined by the reference join, not by insertion order.
3. A deterministic candidate-to-view function for citation labels, item limits, rune/token budgets, and stable ordering.
4. A schedule explorer that enumerates or randomizes operation completion orders, retries, and duplicate delivery.
5. An adapter for `pkg/ttcrag` or `pkg/rag/toolanswer` demonstrating the before/after behavior.
6. A law/conformance package reusable by P05, P06, P08, P09, and P11.

### Proposed API sketch

```go
package ledger

type Conflict struct {
    Namespace string
    ID        string
    Left      []byte
    Right     []byte
    Reason    string
}

type State struct {
    Facts       map[FactID]Fact
    Derivations map[DerivationID]Derivation
    Observations map[ObservationID]Observation
    Conflicts   map[string]Conflict
}

func Join(a, b State) State
func Equal(a, b State) bool
func Validate(s State) error

type Candidate struct {
    FactID      FactID
    Observation ObservationID
    StableKey   string
    Utility     float64
    Size        int
}

type SelectionPolicy struct {
    MaxItems int
    MaxSize  int
    OrderVersion string
}

type Selected struct {
    Label string
    FactID FactID
    Observation ObservationID
}

func Select(s State, candidates []Candidate, p SelectionPolicy) []Selected
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Associativity | `Join(Join(a,b),c)` equals `Join(a,Join(b,c))`. | Generated triples including conflicts and alternative derivations. |
| Commutativity | `Join(a,b)` equals `Join(b,a)`. | Permutation tests and canonical serialization. |
| Idempotence | `Join(a,a)` equals `a`. | Duplicate delivery and retry tests. |
| Identity element | Joining the empty state changes nothing. | Empty-left and empty-right tests. |
| No silent overwrite | Conflicting immutable payloads are retained as explicit conflicts or rejected. | Collision fixtures. |
| Schedule independence | Any completion order of the same successful operation multiset has the same state. | Exhaustive permutations for small cases; randomized scheduler for larger cases. |
| View determinism | For one candidate snapshot and policy, labels and limits are stable. | Tie, size-boundary, and input-permutation tests. |
| Candidate monotonicity | Adding a candidate never deletes an already admitted canonical fact. | Budget tests distinguish state from selected view. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: Concurrent tool completions under a budget

**Setup.** Create five tool search results with distinct stable IDs and sizes; configure a three-item and fixed-rune budget.

**Procedure.** Complete operations in every permutation, with duplicate delivery and selected failures. Compare current ledger output, proposed candidate state, and deterministic selected view.

**Expected observations.** The canonical state is permutation-invariant. The selected view is also invariant for a fixed deterministic policy, even though operational traces differ.

**Failure interpretation.** Any semantic difference identifies arrival-order admission or unstable tie-breaking.
### Scenario 2: Channel overlap and alternative derivations

**Setup.** BM25, vector, and knowledge channels return overlapping chunks and one exact duplicate observation.

**Procedure.** Join channel-local states in all binary tree shapes and orders.

**Expected observations.** One fact per chunk, all distinct derivations/observations retained, and one canonical final state.

**Failure interpretation.** Loss, double counting, or order-dependent conflict indicates a bad merge identity.
### Scenario 3: Conflicting immutable payload

**Setup.** Two workers emit the same fact ID with different text or source range.

**Procedure.** Join in both directions and through an intermediate state; serialize and inspect diagnostics.

**Expected observations.** The result deterministically exposes a conflict and never selects one payload based on arrival order.

**Failure interpretation.** Last-write-wins or first-write-wins silently corrupts semantic identity.
### Scenario 4: Crash, retry, and replay

**Setup.** A worker emits half a batch, crashes, and is retried from the beginning; another worker delivers the same messages twice.

**Procedure.** Compare the final state with an exactly-once baseline.

**Expected observations.** States match exactly; only operational traces contain extra attempts.

**Failure interpretation.** Semantic output contains duplicates, shifted labels, or missing derivations.


### Metrics

- Number of schedule permutations explored and unique semantic outputs observed.
- Conflict detection precision and diagnostic completeness.
- Memory and CPU overhead of retaining derivation/observation sets.
- Contention and throughput of the mutable facade under concurrent writers.
- Difference between candidate count and selected-view count under budgets.
- Number of current code paths whose output changes under permutation testing.
- Minimal counterexample size for each order-dependence defect.

### Fault injection

- Duplicate queue delivery and repeated retries.
- Random worker delays and forced completion permutations.
- Partial batch commit followed by crash.
- Same ID with conflicting payload or schema version.
- Equal scores and sizes at exact item/rune budget boundaries.
- Nondeterministic Go map iteration in selection input.
- Cancellation after candidate production but before labeling.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - merge specification | All namespaces and conflict cases have explicit join behavior. |
| M2 - law harness | Standalone state passes ACI, identity, and serialization tests. |
| M3 - schedule explorer | Permutation/retry/failure generator produces reproducible traces and shrunk counterexamples. |
| M4 - ledger adapter | One current tool ledger path is represented as candidate state plus deterministic view. |
| M5 - stress evaluation | Concurrency, performance, and fault-injection results complete. |
| M6 - hand-off | Conformance package and composition fixtures published. |

## Acceptance gates

- Join passes associative, commutative, idempotent, and identity laws over generated states.
- Conflicting immutable values are never silently overwritten.
- Every permutation of the shared completion fixture yields one canonical state.
- The selected citation view is deterministic for a fixed snapshot and policy.
- Retries and duplicate deliveries change only the operational trace.
- At least one current order-sensitive behavior is confirmed or convincingly refuted.
- The API makes it impossible or visibly exceptional to consume a budget while mutating canonical candidate state.
- Performance results identify the practical state-size limit of the reference implementation.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- `fact-state/v1` and derivation fixtures from P02, or local compatible fakes.
- Operation completion records containing stable request and observation IDs.
- Selection policy with versioned stable tie-break definition.

### Outputs offered to later projects

- `joined-state/v1`, `merge-conflict/v1`, and `selected-evidence-view/v1` schemas.
- Reusable ACI and schedule-independence test harness.
- Completion-permutation fixtures for P06 and P09.
- Deterministic labeling/selection adapter.

### Expected composition experiments

- Combine P02 provenance states produced by independent channels and rerun its verifier.
- Feed the joined candidates into P04 ranking and budget policies.
- Use P06 to execute candidate-producing operations under retries and random schedules, then compare states.
- Use P11 deltas as small joinable states for incremental additions.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| Treating a mutex as a semantic proof | Always compare snapshots across schedules; mutual exclusion only prevents data races. |
| Smuggling policy into join | Move score aggregation, first-N, and budget selection into an explicit view. |
| Unbounded provenance growth | Measure and experiment with compact representations while keeping law-preserving reference behavior. |
| Conflict equals error ambiguity | Specify whether a conflict state is inspectable, terminal, or excluded from normal consumers. |
| Weak scheduler tests | Use exhaustive permutations for small cases and deterministic randomized seeds for larger ones. |

## Questions the final report must answer

1. Which current structures are lawful add-only states, and which are selected views?
2. What exact conflict policy makes join total or partial?
3. What assumptions are needed for schedule independence?
4. Which budgets can be moved after merge, and what behavior changes?
5. How much provenance/observation data can be retained before compaction is necessary?
6. What current order dependence was found, and what was its smallest counterexample?
7. Which law was hardest to preserve in the rag-ttc adapter?

## Stretch investigations

- A delta-state merge format for network-efficient synchronization.
- Merkle summaries for comparing large ledgers.
- A deterministic streaming top-k view with an explicit finalization barrier.
- Formal finite-state model checking of the mutable facade.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/lawful-merge-deterministic-ledger` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, sections 4.6, 6.4, 8.9, 9.2, 9.8-9.10, and 10.2.
- A comprehensive study of Convergent and Commutative Replicated Data Types, Shapiro et al., for join-based replicated state.
- Keeping CALM: When Distributed Consistency is Easy, for the relationship between monotonicity and coordination.
- QuickCheck for algebraic law testing and counterexample shrinking.
- Go memory model and sync package documentation for the operational facade.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# P04 - Candidate State and Ranked View Separation

## Assignment summary

**Project code:** P04  
**Track:** Policy semantics: ranking and selection  
**Suggested duration:** 4-6 weeks  
**Suggested team:** 1-2 students  
**Program priority:** High

Refactor the conceptual boundary between all admitted candidates and the ordered, scored, bounded context shown to a generator or user. The project should make selection policy explicit, deterministic, inspectable, and replaceable without changing canonical evidence identity.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/rag/types.go`
- `pkg/rag/retrieval/retrieval.go`
- `pkg/rag/reranking`
- `pkg/rag/answering/context.go`
- `pkg/rag/answering/service.go`
- `pkg/rag/evaluation`
- `pkg/rag/review`
- `pkg/app/chatui/hits.go`
- `pkg/app/chatui/evidence.go`

### Why this project exists

- The current `rag.Evidence` structure mixes source material with rank and retrieval/reranker scores. These fields change across queries and policies even when the source chunk is identical.
- Ranking, RRF fusion, collapse, top-k, token packing, diversity, and citation labels are non-monotone policies. They are useful, but they should be views over a stable candidate snapshot rather than mutations of evidence identity.
- A clean view boundary makes retrieval recall, ranking quality, context packing, and generation use separately measurable and cacheable.
- The repository already has deterministic retrieval and answering preparation stages. This project makes their contracts explicit and tests policy substitutability.

### Source-level observations to verify

- `rag.Evidence` contains `Chunk`, `Rank`, `RetrievalScore`, and optional `RerankerScore`; assess which fields belong to source, observation, and view.
- `pkg/rag/retrieval` performs collapse, weighted RRF, and hydration with deterministic ordering tests.
- `pkg/rag/answering/context.go` prepares context and enforces output constraints; inspect whether packing identity includes all relevant policy.
- `pkg/rag/evaluation` provides existing metric conventions that should be retained but assigned to explicit pipeline stages.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. What is the smallest candidate record needed to support current lexical, vector, fused, knowledge, and tool ranking policies?
2. Which scores are channel observations, normalized utilities, or policy-specific derived values?
3. How should stable tie-breaking work across equal scores, missing scores, multiple representations of one chunk, and document collapse?
4. Can context packing be modeled as a pure deterministic function of candidate snapshot, query, policy, and tokenizer/version?
5. Which evaluation metrics belong to candidate recall versus ranking/view quality versus generation use?
6. What view metadata is necessary to explain why an item was selected or excluded?

### Falsifiable hypotheses

1. Separating canonical facts from `CandidateObservation` and `SelectedViewEntry` removes score/rank from evidence identity without losing current functionality.
2. For a fixed snapshot and versioned policy, ranking and packing can be deterministic even when the candidate state was built concurrently.
3. Retrieval and ranking regressions become easier to localize when evaluation reports candidate recall, view recall, and context inclusion separately.
4. At least two current APIs can be simplified by accepting stable fact IDs plus observations instead of hydrated `rag.Evidence` with mutable ranks.
5. Selection explanations can be produced from pure policy traces without promoting those traces to canonical provenance.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Define candidate observation, channel contribution, ranked entry, selected context item, exclusion reason, and view identity.
- Implement pure deterministic policies for collapse, weighted RRF, reranking, top-k, and one token/rune packing strategy.
- Build an explanation trace for score transformations, tie breaks, exclusions, and budget decisions.
- Adapt one current answering path while preserving externally visible answer context.
- Create evaluation reports that separate candidate-set, ranked-view, packed-context, and answer stages.
- Test view cache identity and sensitivity to policy versions.

### Explicit non-goals

- Inventing a new learned reranker model.
- Declaring one ranking policy scientifically best.
- Making top-k monotone or placing selection inside canonical merge.
- Changing corpus chunking or source identity.
- Solving semantic entailment of answers.

## System to build

1. A standalone view package over neutral fact IDs and observations.
2. Versioned pure functions for collapse, fusion, reranking adaptation, deterministic tie-breaking, and context packing.
3. A `ViewTrace` that explains each transformation without changing canonical state.
4. An adapter from current `Hit`, `FusedHit`, and `Evidence` sequences into the new view model and back for compatibility.
5. A stage-aware evaluator and visualization showing candidate, ranked, selected, and used evidence funnels.
6. A policy matrix experiment across tie cases, budgets, channel weights, and alternative rerankers.

### Proposed API sketch

```go
package view

type Observation struct {
    ID       string
    FactID   FactID
    Channel  string
    Rank     int
    Score    *float64
    Metadata map[string]string
}

type CandidateSet struct {
    SnapshotID string
    Facts      []FactID
    Observations []Observation
}

type Entry struct {
    FactID       FactID
    Rank         int
    Utility      float64
    Contributions []Contribution
    Selected     bool
    Exclusion    string
}

type Policy interface {
    ID() string
    Apply(query QueryRef, candidates CandidateSet) (View, Trace, error)
}

type View struct {
    ID       string
    PolicyID string
    Entries  []Entry
}

type PackPolicy struct {
    MaxItems  int
    MaxTokens int
    TokenizerID string
}

func Pack(v View, facts FactReader, p PackPolicy) (Context, PackTrace, error)
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Fact independence | Changing scores or ranks does not change canonical fact IDs. | Adapted evidence mutation tests. |
| Determinism | A fixed candidate snapshot and policy produce one ordered view. | Input permutation, map-order, and restart tests. |
| Stable tie-break | Equal utility is resolved by a documented total order. | Tie fixtures with all input permutations. |
| Policy version sensitivity | Behavior-changing policy changes alter view identity. | Mutation tests over weights, constants, limits, and algorithm version. |
| Trace fidelity | Every selected or excluded entry has a reproducible reason. | Recompute trace and compare against result. |
| Budget validity | Packed context never exceeds declared limits under the specified tokenizer/size function. | Boundary and Unicode fixtures. |
| Candidate preservation | Applying a view does not mutate or delete candidate facts. | Snapshot hash before/after. |
| Stage metric separation | Candidate recall cannot be worsened by reranking; selected recall can. | Synthetic evaluation fixtures. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: Ranking tie matrix

**Setup.** Create candidates with equal fused/reranker scores, duplicate document membership, and different stable IDs.

**Procedure.** Permute input order, map order, and channel contribution order across all policies.

**Expected observations.** The view order and trace are identical under the documented tie-break.

**Failure interpretation.** Order drift exposes reliance on incidental input or map iteration order.
### Scenario 2: Candidate versus selected recall

**Setup.** Use a query with relevant facts present in the candidate set but vulnerable to top-k or token packing exclusion.

**Procedure.** Vary reranker, k, tokenizer, and packing policy while holding candidates fixed.

**Expected observations.** Reports attribute the loss to ranking or packing rather than retrieval.

**Failure interpretation.** A combined metric cannot identify the responsible subsystem.
### Scenario 3: Same facts, different policies

**Setup.** Freeze one candidate snapshot and apply baseline RRF, connected fusion, diversity-aware selection, and a simple oracle policy.

**Procedure.** Compare view identities, traces, selected contexts, and downstream recorded answers.

**Expected observations.** Canonical state stays unchanged; each view is separately named and reproducible.

**Failure interpretation.** Policy application mutates shared evidence or produces an unversioned view.
### Scenario 4: Context budget boundaries

**Setup.** Use ASCII, multibyte Unicode, long chunks, empty chunks, and exact-boundary token/rune sizes.

**Procedure.** Pack under several item and size budgets, then rerun with permuted candidates.

**Expected observations.** Limits are never exceeded and exclusions are deterministic and explained.

**Failure interpretation.** Different selection under permutation or inaccurate size accounting indicates an underspecified packer.


### Metrics

- Candidate recall, ranked recall at k, packed-context recall, and answer citation use.
- NDCG/MRR or existing retrieval metrics at the appropriate stage.
- View determinism failures over permutations and restarts.
- Percentage of exclusions with a machine-readable reason.
- Policy trace size and computation overhead.
- Cache reuse across policies and invalidation when policy identity changes.
- Number of current APIs that can drop rank/score from canonical evidence payloads.

### Fault injection

- Equal scores, missing scores, NaN handling, and negative scores.
- Random candidate and contribution order.
- Duplicate observations for one fact and multiple representations per chunk.
- Tokenizer/version mismatch and exact budget edges.
- Reranker returning partial, duplicate, or unknown IDs.
- Policy ID accidentally unchanged after behavior modification.
- Hydration failure for a selected fact.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - stage model | Candidate, observation, view, context, and trace types defined with identity rules. |
| M2 - pure policies | Collapse, fusion, tie-breaking, top-k, and packing pass deterministic tests. |
| M3 - adapter | One answering path produces equivalent context through the new boundary. |
| M4 - evaluator | Stage-separated metrics and funnel visualization implemented. |
| M5 - policy experiments | Tie, budget, and policy matrix results complete. |
| M6 - hand-off | View schemas, traces, fixtures, and recommendations published. |

## Acceptance gates

- Canonical fact identity is unaffected by rank, score, selection, or citation label.
- Every policy is pure for a fixed snapshot and has a versioned identity.
- All tie fixtures yield stable order across input permutations.
- Packing respects declared item and size limits at exact boundaries.
- The evaluator reports at least four distinct stages: candidate, ranked, packed, and answer-used.
- The adapted answering path matches a frozen baseline context for the compatibility policy.
- Every excluded candidate has an explanation or an explicit unsupported-reason marker.
- The report identifies where non-determinism is scientifically desired and how it should be represented.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- Canonical fact IDs and payload reader from P02 or neutral fixtures.
- Joined candidate observations from P03.
- Query and policy configuration fingerprints.

### Outputs offered to later projects

- `candidate-set/v1`, `ranked-view/v1`, `view-trace/v1`, and `packed-context/v1` schemas.
- Pure policy interface and compatibility adapters.
- Stage-separated evaluation result for P08, P09, and composition studies.
- Ranking-tie and context-budget fixtures.

### Expected composition experiments

- Consume a P03 joined state and prove selection does not mutate it.
- Compare P07 knowledge candidate discovery with multiple P04 selection policies.
- Use P08 connected composition to generate channel observations, then apply one shared view layer.
- Feed packed context into P09 tool/answer generation and distinguish selected from cited evidence.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| View object becomes a new evidence monolith | Keep source payloads referenced by ID; view entries contain policy metadata only. |
| Hidden tokenizer semantics | Version the size function/tokenizer and store exact measured sizes in the trace. |
| Compatibility masks design flaws | Provide a compatibility policy, but evaluate cleaner alternatives separately. |
| Learned reranker nondeterminism | Treat model response as an observation; purity begins after the recorded response is admitted. |
| Metric confusion | Name the input set for every metric and never call selected-view recall retrieval recall. |

## Questions the final report must answer

1. Which current fields moved from evidence identity to observation or view?
2. What total order resolves every tie case?
3. Which policies are pure after recording external model output, and which remain stochastic?
4. How often does relevant evidence exist in candidates but disappear during ranking or packing?
5. What is the right cache boundary for candidate sets, ranked views, and packed contexts?
6. Which compatibility behavior should be retained, and which should be intentionally changed?
7. How useful are selection explanations to developers and human evaluators?

## Stretch investigations

- Pareto-front or diversity-aware views with explicit trade-off traces.
- Counterfactual explanation: the smallest policy change that would select an excluded fact.
- A UI comparing two views over the same candidate snapshot.
- Formal optimization model for context packing with deterministic approximation guarantees.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/candidate-state-ranked-views` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, sections 3, 4.5, 6.9, 8.5-8.6, 9.9, 10.5, and 11 Phase 2.
- Original Reciprocal Rank Fusion paper or a primary description of RRF for score semantics.
- Information retrieval evaluation references for recall, MRR, NDCG, and stage-aware error analysis.
- QuickCheck for deterministic permutation and boundary testing.
- rag-ttc existing retrieval and evaluation tests as executable specification candidates.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# P05 - Closure and Frontier Evaluation Engine

## Assignment summary

**Project code:** P05  
**Track:** Recursive semantics: rules and fixed points  
**Suggested duration:** 6-8 weeks  
**Suggested team:** 2 students  
**Program priority:** High

Build a small recursive retrieval engine whose meaning is the least state closed under a set of add-only rules. Compare breadth-first, worklist, batched, and parallel evaluators; prove or experimentally validate when they return the same result; and map the model onto multi-hop retrieval in rag-ttc.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/rag/components.go`
- `pkg/rag/knowledge`
- `pkg/rag/knowledge/retrieve`
- `pkg/rag/connected`
- `pkg/rag/answering`
- `pkg/rag/toolanswer`
- `pkg/execution/map.go`
- `pkg/flow`
- `pkg/rag/ordering.go`

### Why this project exists

- The proposed semantic model becomes materially useful when retrieval is recursive: direct hits enable graph expansion, extracted claims enable new queries, or tool observations enable additional searches.
- A fixed-depth loop and a true saturation process are different contracts. The codebase needs a precise way to say what is complete after N rounds and what is complete at termination.
- Worklist and frontier algorithms can avoid repeatedly evaluating rules against the entire state, but optimization is valid only if the rule and merge laws are explicit.
- This project provides the strongest demonstration of the theory: partial results are sound, fair schedules agree, provenance records derivation depth, and finite universes terminate.

### Source-level observations to verify

- `pkg/rag/knowledge/retrieve` contains planner logic that can be decomposed into candidate discovery and selection.
- `pkg/rag/connected` composes baseline and knowledge retrieval but currently operates as a completed augmentation path rather than a generic closure rule.
- `pkg/rag/toolanswer` and agent-oriented search naturally provide follow-up operations but also contain turn limits and presentation concerns.
- `pkg/flow` supplies operational mechanisms; the proposed closure engine should not duplicate cache/retry/budget implementations.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. What rule interface cleanly separates planning, external execution, admission, and joining while remaining easy to implement in Go?
2. Which practical rag-ttc retrieval operations are monotone candidate producers, and which are non-monotone views that must stay outside closure?
3. Under what assumptions do naive repeated evaluation, semi-naive frontier evaluation, asynchronous workers, and batched evaluation compute the same state?
4. How should derivation rank, round number, operation budget, and wall-clock deadline be represented without conflating soundness and completeness?
5. Can the engine give useful completeness certificates such as saturated, complete through rank N, or stopped with a pending frontier?
6. How are external failures represented so that retry policy does not change the semantic result contract?

### Falsifiable hypotheses

1. For finite facts, stable identities, add-only admission, and fair evaluation, all tested schedules converge to the same least closed state.
2. A frontier evaluator produces the same state as naive iteration while invoking substantially fewer rule matches on sparse multi-hop fixtures.
3. Derivation rank stored in provenance corresponds to the earliest round in which a fact can appear under synchronous breadth-first evaluation.
4. Ranking, top-k, and token budgets inside a rule can produce schedule-dependent or incomplete closure; moving them to views restores the law.
5. A stopped evaluator can provide a sound partial state and a precise pending-work certificate without claiming saturation.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Define add-only rules with explicit input patterns, planned operations, admitted outputs, and derivations.
- Implement naive round-based, worklist/frontier, batched, and parallel fair evaluators.
- Track new facts, pending operations, completed operations, derivation rank, stop reason, and saturation status.
- Build finite synthetic fixtures with known closure and selected rag-ttc adapters for knowledge/connected retrieval.
- Test monotonicity of rules and detect or reject rule implementations that delete, replace, or inspect unstable selected views.
- Compare fixed-depth, goal-based, resource-bounded, and full-saturation semantics.

### Explicit non-goals

- Supporting arbitrary user code with an undecidable static monotonicity checker.
- Executing an actual infinite ordinal computation.
- Embedding ranking or generation inside the canonical closure state.
- Solving distributed consensus or exactly-once networking.
- Replacing ordinary Go control flow with a general workflow DSL.

## System to build

1. A standalone rule and closure package over a finite fact universe and an effect interface that can be faked or recorded.
2. Four evaluators: synchronous rounds, semi-naive frontier, deterministic worklist, and randomized/parallel fair schedule.
3. A rule conformance harness checking add-only admission, monotone input behavior on finite samples, stable IDs, and derivation completeness.
4. A completeness certificate containing stop reason, completed rank, pending frontier, failed/retryable operations, and resource use.
5. Adapters implementing at least two realistic multi-hop patterns from rag-ttc: knowledge neighbor expansion and query/tool follow-up.
6. A visualization of stages/frontiers and an experiment comparing correctness and cost across evaluators.

### Proposed API sketch

```go
package closure

type RuleID string
type OperationID string

type Rule interface {
    ID() RuleID
    Plan(ctx context.Context, snapshot State, frontier Frontier) ([]Operation, error)
    Admit(snapshot State, op Operation, result Result) (Delta, error)
}

type Operation struct {
    ID      OperationID
    Rule    RuleID
    Inputs  []FactID
    Request json.RawMessage
}

type Delta struct {
    Facts       []Fact
    Derivations []Derivation
    Diagnostics []Diagnostic
}

type Limits struct {
    MaxRounds     int
    MaxFacts      int
    MaxOperations int
}

type Certificate struct {
    Saturated       bool
    StopReason      string
    CompleteThrough int
    Pending         []OperationID
    Failed          []OperationID
}

type Evaluator interface {
    Close(ctx context.Context, seed State, rules []Rule, limits Limits) (State, Certificate, Trace, error)
}
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Inflationary state | Each admitted delta joins with the old state; no fact or derivation is removed. | Snapshot subset checks at every transition. |
| Rule monotonicity | Giving a rule more facts cannot invalidate outputs already admissible from fewer facts. | Generated nested-state checks for finite rules. |
| Closure stability | When saturated, running closure again adds nothing. | Idempotence test over saturated fixtures. |
| Least-result behavior | The engine does not invent unrelated facts merely because they form a closed state. | Compare against exhaustive finite reference closure. |
| Schedule independence | Fair evaluators produce the same semantic state. | Round/worklist/parallel comparison across schedule seeds. |
| Rank correspondence | A fact first appearing in round N has a derivation of depth N and none shallower. | Exhaustive small graph oracle. |
| Sound partial result | Every returned fact has a valid derivation even when stopped early. | Verifier over all budget/deadline stop cases. |
| Certificate honesty | `Saturated=true` only when no enabled work remains. | Attempt one more reference step and inspect pending frontier. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: Finite multi-hop graph with known closure

**Setup.** Use a directed graph with cycles, diamonds, unreachable components, and typed edge-follow rules. Seed one query node.

**Procedure.** Run all evaluators across depths, random schedules, duplicate operations, and full saturation.

**Expected observations.** All fair full runs return exactly the reachable closure; depth-limited runs match the known distance/rank boundary.

**Failure interpretation.** Missing, extra, or schedule-dependent facts expose rule or evaluator defects.
### Scenario 2: Knowledge expansion adapter

**Setup.** Build a small rag-ttc knowledge repository containing ambiguous concepts, facts, mentions, and source chunks.

**Procedure.** Express concept discovery, fact-neighbor expansion, and source hydration as separate rules. Compare with the current planner output.

**Expected observations.** Candidate closure is reproducible and retains all supports; current selection limits are represented only in a downstream view.

**Failure interpretation.** If current behavior cannot be mapped without non-monotone admission, document the exact semantic mismatch.
### Scenario 3: Non-monotone rule counterexample

**Setup.** Implement an intentionally invalid rule that keeps only the current top result or suppresses an earlier fact after seeing a better score.

**Procedure.** Run it under different schedules and input growth paths.

**Expected observations.** The conformance harness detects monotonicity failure or the evaluators diverge, producing a minimal teaching counterexample.

**Failure interpretation.** If the harness passes the bad rule, the contract is too weak.
### Scenario 4: Resource-bounded continuation

**Setup.** Use a fixture larger than the operation budget and stop after several frontier items.

**Procedure.** Serialize state and certificate, resume with a fresh process, and compare with uninterrupted closure.

**Expected observations.** Resumed and uninterrupted semantic states match; the partial result remains verifier-sound.

**Failure interpretation.** Lost or duplicated pending work changes the result or makes the certificate misleading.


### Metrics

- Semantic equality across evaluator and schedule variants.
- Rule planning calls, operation executions, duplicate suppressions, and admitted facts.
- Frontier size and rounds to saturation.
- Derivation rank accuracy against graph distance oracle.
- Time and memory for naive versus frontier evaluation.
- Completeness/stop-certificate accuracy under budgets and failures.
- Number of current operations classified monotone candidate producer versus non-monotone view.

### Fault injection

- Duplicate operation scheduling and duplicate results.
- Random worker delay, failure, retry, and cancellation.
- Cycles and self-loops in the derivation graph.
- Rules returning conflicting IDs or dangling dependencies.
- Budget exhaustion between execution and admission.
- Resume from partially persisted frontier.
- An intentionally non-monotone top-k rule.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - formal executable model | Finite reference closure and rule laws complete. |
| M2 - evaluator family | Round, frontier, worklist, and parallel evaluators agree on synthetic fixtures. |
| M3 - certificates | Depth, saturation, pending frontier, and resume semantics tested. |
| M4 - rag-ttc adapters | Two realistic retrieval expansions implemented without changing core packages. |
| M5 - comparative study | Correctness, cost, and counterexample experiments complete. |
| M6 - hand-off | Rule contract, evaluator interface, fixtures, and report published. |

## Acceptance gates

- All fair evaluators agree with the exhaustive reference closure on finite fixtures.
- The engine rejects or exposes the intentionally non-monotone rule.
- Every partial and complete output passes provenance verification.
- A saturated certificate is validated by one additional reference step with no new work.
- Depth-limited outputs match derivation-rank expectations.
- Resume after budget stop matches uninterrupted execution.
- At least two rag-ttc multi-hop patterns are expressed through the rule boundary.
- The report states the assumptions under which schedule independence is claimed.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- P02-compatible facts and derivations or neutral local equivalents.
- P03-compatible join/delta behavior.
- Recorded external operation effects or deterministic fakes.

### Outputs offered to later projects

- `rule/v1`, `operation/v1`, `closure-certificate/v1`, and `frontier-checkpoint/v1` schemas.
- Rule conformance harness and evaluator comparison suite.
- Multihop graph and knowledge-expansion fixtures.
- Saturated and partial proof-carrying states for P10 and P11.

### Expected composition experiments

- Execute P05 operations through P06 and verify retries/schedules do not change the closure state.
- Apply P04 views only after candidate closure and measure loss by selection.
- Use P07 candidate discovery rules inside P05 and compare fixed-depth versus saturation behavior.
- Use P11 delta maintenance to update an already saturated closure.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| Rule API too effectful | Keep planning and admission pure around an explicit operation/result boundary. |
| Claiming monotonicity by convention | Provide finite generated checks and counterexample fixtures; document unproved external assumptions. |
| Infinite or explosive closure | Require limits, expose pending work, and analyze finite-universe conditions. |
| Mixing failure with absence | Represent failed operations separately from successful empty results. |
| General workflow-engine drift | Limit the engine to add-only derivation closure and normal Go composition. |

## Questions the final report must answer

1. Which rule contract was easiest to implement and verify?
2. Under exactly which assumptions did evaluator outputs agree?
3. What did derivation rank mean for each real adapter?
4. Where did current retrieval policy prevent a monotone mapping?
5. How accurate and useful were partial completeness certificates?
6. What cost reduction did frontier evaluation achieve?
7. What is the smallest counterexample showing why top-k does not belong inside closure?

## Stretch investigations

- Prioritized but semantically transparent worklists whose priority changes only trace/cost.
- A small model checker for finite rule systems.
- Stratified negative rules in a separate finalized layer.
- A distributed delta exchange experiment across two evaluator processes.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/closure-frontier-evaluation-engine` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, sections 6.6-6.8, 9.3-9.8, 9.17, and 11 Phase 6.
- Datalog and Recursive Query Processing survey material for bottom-up and semi-naive evaluation.
- Keeping CALM for monotone computation and schedule/coordination intuition.
- Differential Dataflow for iterative and incremental dataflow concepts.
- Database fixed-point semantics and worklist algorithm references.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# P06 - Flow Executor Semantics and Captured Effects

## Assignment summary

**Project code:** P06  
**Track:** Operational semantics: execution  
**Suggested duration:** 5-7 weeks  
**Suggested team:** 1-2 students  
**Program priority:** High

Characterize `pkg/flow` and `pkg/execution` as an operational layer: what a step means, which policy changes only execution history, which changes semantic output, and when caching, retry, batching, concurrency, or barriers are transparent. Build a reference effect-capture harness and fix identity/trace ambiguities.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/flow/step.go`
- `pkg/flow/run.go`
- `pkg/flow/pipe.go`
- `pkg/flow/policy.go`
- `pkg/flow/report.go`
- `pkg/flow/store.go`
- `pkg/flow/batch.go`
- `pkg/flow/bulk.go`
- `pkg/execution/cache.go`
- `pkg/execution/map.go`
- `pkg/execution/cached_map.go`
- `pkg/execution/cached_batch_map.go`
- `pkg/execution/budget.go`
- `pkg/execution/rate.go`

### Why this project exists

- The repository already has a substantial, typed operational toolkit for caching, retrying, batching, limiting, budgeting, and restoring result order. It should be preserved rather than replaced by a workflow engine.
- Operational transparency is conditional. Retry is transparent only for idempotent or captured effects; batching is transparent only if the batch implementation preserves per-item meaning; cache is transparent only with a correct semantic key.
- `flow.Report` appears to use a display step name as a map key, which can conflate repeated logical executions. Stable operation identity should be separate from human-readable names.
- Later composition needs a way to prove that different traces correspond to one semantic result, while still retaining trace differences for cost and reliability analysis.

### Source-level observations to verify

- `pkg/flow` deliberately describes execution mechanics rather than a scheduler; retain this architectural intent.
- `pkg/flow/report.go` should be tested with repeated step names and repeated invocations to determine whether entries are conflated.
- `pkg/execution` includes ordered parallel map, cache, batch, limiter, and budget primitives that can be tested through policy metamorphisms.
- Generation and embedding flow adapters provide realistic effect-shaped operations without requiring live providers when responses are recorded.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. What is the denotational contract of a `flow.Step`: a pure function, an effectful operation, or a function over captured observations?
2. Which policies are semantics-preserving under which preconditions?
3. How should stage definition identity, operation invocation identity, attempt identity, and display name be represented?
4. What barriers are required before non-monotone operations such as top-k or global reranking?
5. How can external effects be recorded and replayed so that semantic equivalence can be tested offline?
6. Can the existing APIs be instrumented without introducing a central scheduler or generic graph DSL?

### Falsifiable hypotheses

1. Most `flow` combinators can be given local transparency contracts that are testable against a recorded-effect oracle.
2. Separating `StepID`, `OperationID`, `AttemptID`, and display `Name` removes report collisions without changing pipeline composition APIs.
3. Sequential, batched, cached, and parallel execution yield the same semantic outputs for compliant steps, with differences confined to operational traces.
4. At least one existing combinator has an undocumented precondition or edge case where semantic transparency fails.
5. A lightweight captured-effect adapter is sufficient for replay and does not require a general workflow runtime.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Inventory `flow` and `execution` combinators and write a semantic precondition/effect table.
- Define identities for step definition, operation invocation, attempt, batch, and trace event.
- Build a recorded-effect interface and deterministic fake operations for cache/retry/batch/rate/budget experiments.
- Create conformance tests for sequential versus parallel, item versus batch, cached versus uncached, and retry versus single-attempt execution.
- Reproduce or refute report-name conflation and propose a compatible report schema.
- Document barrier semantics and test a global operation that is invalid under item-local execution.

### Explicit non-goals

- Creating a workflow DAG language, scheduler service, or visual orchestration product.
- Making arbitrary external side effects retry-safe.
- Defining canonical RAG facts or ranking semantics; use fakes or published contracts from other projects.
- Optimizing provider throughput beyond what is needed to evaluate semantics.
- Guaranteeing deterministic wall-clock timing or goroutine interleavings.

## System to build

1. A semantic contract catalog for every major combinator and policy.
2. A standalone `effectlog` package that records request identity, response, error class, attempt, and timing, and can replay responses by semantic request ID.
3. A reference suite of compliant and intentionally non-compliant steps: pure, idempotent effect, non-idempotent effect, order-sensitive batch, partial batch, and global barrier step.
4. A trace/report identity revision with migration adapter for current `flow.Report` consumers.
5. A metamorphic test runner comparing semantic outputs under operational policy transformations.
6. A benchmark and failure-injection study using representative rag-ttc embedding/generation-shaped calls without live providers.

### Proposed API sketch

```go
package effectlog

type StepID string
type OperationID string
type AttemptID string

type Request struct {
    Step      StepID
    Operation OperationID
    SemanticKey string
    Payload   json.RawMessage
}

type RecordedResult struct {
    RequestKey string
    Response   json.RawMessage
    ErrorClass string
}

type Event struct {
    Step       StepID
    Operation  OperationID
    Attempt    AttemptID
    Kind       string
    At         time.Time
    Detail     json.RawMessage
}

type Recorder interface {
    Execute(ctx context.Context, req Request, fn func(context.Context) (json.RawMessage, error)) (RecordedResult, error)
    Replay(req Request) (RecordedResult, bool)
    Events() []Event
}

type TransparencyCase[I, O any] struct {
    Name string
    Baseline func(context.Context, []I) ([]O, error)
    Variant  func(context.Context, []I) ([]O, error)
    Equal    func([]O, []O) bool
}
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Output transparency | Changing an allowed operational policy does not change semantic output. | Metamorphic comparisons against a baseline executor. |
| Retry transparency | Retrying a compliant operation yields the same admitted result as one successful attempt. | Injected transient failures and duplicate completions. |
| Cache transparency | Cache hit and miss paths return the same semantic value and error contract. | Recorded-effect and corrupted-cache tests. |
| Batch equivalence | Batch execution is equivalent to per-item execution with declared order mapping. | Random batch boundaries, partial failures, duplicates. |
| Order restoration | Item outputs correspond to their input identities even when workers complete out of order. | Delayed-operation permutation tests. |
| Stable trace identity | Repeated display names do not conflate distinct operations or attempts. | Nested/repeated-step report fixture. |
| Budget honesty | Budget stop is explicit and does not masquerade as a successful empty semantic result. | Boundary and cancellation tests. |
| Barrier correctness | A global step observes the complete declared input snapshot, not an accidental partial batch. | Top-k/global-normalization counterexample. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: Policy metamorphism matrix

**Setup.** Use a deterministic recorded operation over 100 typed inputs with stable semantic keys.

**Procedure.** Run direct, cached, retried, parallel, batched, cached-batched, rate-limited, and budgeted variants under compatible limits.

**Expected observations.** All complete variants have equal semantic outputs; traces differ in expected attempts, cache outcomes, and timing.

**Failure interpretation.** A difference isolates a missing precondition or combinator defect.
### Scenario 2: Repeated step names

**Setup.** Compose two distinct steps with the same display name and invoke one step multiple times.

**Procedure.** Inspect current and proposed reports, including failures and retries.

**Expected observations.** Proposed reports retain distinct step definitions, operations, and attempts while preserving display names.

**Failure interpretation.** Metrics or errors are overwritten/conflated.
### Scenario 3: Non-idempotent retry counterexample

**Setup.** Use an operation that increments an external counter before returning a transient error.

**Procedure.** Run with retry, captured-effect deduplication, and a pure recorded replay.

**Expected observations.** The raw operation demonstrates non-transparency; the contract rejects it or requires an idempotency key/effect capture.

**Failure interpretation.** The framework claims retry safety without observing duplicate side effects.
### Scenario 4: Global barrier violation

**Setup.** Implement a step that selects global top-k or normalizes scores over all items.

**Procedure.** Run it item-wise, in arbitrary batches, and behind an explicit collection barrier.

**Expected observations.** Only the barrier version matches the reference global result; documentation identifies why.

**Failure interpretation.** An item/batch adapter silently changes global semantics.


### Metrics

- Semantic mismatch count across operational policy variants.
- Trace completeness: steps, operations, attempts, cache outcomes, and stop reasons represented.
- Report collision count under repeated names and nested composition.
- Extra external effects caused by retry for compliant and non-compliant operations.
- Throughput, latency, allocation, and cache-hit differences across variants.
- Number of combinators with explicit preconditions and counterexamples.
- Replay coverage: percentage of calls reproducible without live effects.

### Fault injection

- Transient, permanent, and ambiguous timeout errors.
- Failure before effect, after effect, and after response receipt.
- Corrupt, stale, and version-skewed cache entries.
- Out-of-order worker completion and duplicate result delivery.
- Partial batch success and response length mismatch.
- Budget expiration at every operation boundary.
- Repeated display names and nested pipelines.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - contract inventory | Every major combinator has semantic meaning, preconditions, and expected trace effects. |
| M2 - captured effects | Recorder/replayer and compliant/non-compliant fake steps complete. |
| M3 - metamorphic suite | Policy matrix produces stable, shrinkable mismatch reports. |
| M4 - identity/report adapter | Step/operation/attempt distinction implemented and compatibility assessed. |
| M5 - rag-shaped evaluation | Embedding/generation-shaped benchmark and fault study complete. |
| M6 - hand-off | Conformance APIs, fixtures, and operational contract report published. |

## Acceptance gates

- Every studied combinator has a written semantic precondition and a test that would fail if it were violated.
- Complete policy variants return one semantic output for compliant operations.
- The non-idempotent retry fixture demonstrates why retry safety is conditional.
- Repeated display names no longer conflate report entries in the proposed model.
- Cache hit/miss equivalence is tested with correct, missing, stale, and corrupt entries.
- Global barrier counterexample is included and explained.
- Recorded replay can reproduce the main experiment without provider/network access.
- The design preserves rag-ttc’s explicit Go composition and does not introduce a workflow DSL.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- Semantic request fingerprints from P01 or compatible fixture keys.
- Pure or recorded operation functions from any later project.
- Optional P03 state comparison for semantic equality.

### Outputs offered to later projects

- `operation-trace/v1`, `captured-effect/v1`, and revised `flow-report/v2` schemas.
- Metamorphic operational-transparency harness.
- Failure/retry/batch fixtures for P05, P08, P09, and P10.
- A documented barrier contract for non-local operations.

### Expected composition experiments

- Execute P05 rule operations under all P06 policies and compare closure state/certificates.
- Run P08 baseline and knowledge channels concurrently and verify output equality with sequential execution.
- Capture P09 tool calls for deterministic replay and duplicate-effect testing.
- Store P06 traces in P10 experiment bundles while keeping semantic state separately comparable.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| Defining all steps as pure | Model effects explicitly and make transparency conditional rather than fictional. |
| Trace identity contaminates semantics | Operation/attempt IDs belong to trace unless they identify a recorded external observation required by derivation. |
| Benchmark-driven scope creep | Measure enough to expose trade-offs; do not redesign the entire execution package for speed. |
| Hidden provider behavior | Use captured deterministic fakes and separately document live-provider observations. |
| Workflow DSL drift | Keep existing typed function composition and add contracts/instrumentation only. |

## Questions the final report must answer

1. What does a `flow.Step` mean under the proposed model?
2. Which policies were transparent, and under what preconditions?
3. Which current combinator or adapter violated the expected contract?
4. How should step definition, operation, attempt, and display identity be represented?
5. Where are explicit barriers necessary?
6. How much of a run can be replayed from captured effects?
7. What changes should be made to `flow.Report`, if any?

## Stretch investigations

- A lightweight effect type taxonomy generated in Go documentation.
- Deterministic simulated scheduler for model checking small concurrent executions.
- Trace compression and causal linking across nested operations.
- An OpenTelemetry adapter that preserves semantic/operational identity distinctions.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/flow-executor-semantics-effects` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, sections 4.4, 7, 8.10, 9.8-9.11, and 10.4.
- Go memory model and context cancellation documentation.
- Retry and idempotency guidance from distributed systems literature, using primary technical sources.
- QuickCheck for metamorphic and algebraic testing.
- CALM as background for why add-only semantic results tolerate more operational reordering than non-monotone selection.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# P07 - Knowledge Retrieval: Discovery versus Selection

## Assignment summary

**Project code:** P07  
**Track:** Subsystem semantics: knowledge retrieval  
**Suggested duration:** 6-8 weeks  
**Suggested team:** 2 students  
**Program priority:** High

Decompose the knowledge subsystem into lossless candidate discovery, explicit ambiguity and support records, and replaceable selection policies. The project should determine what the knowledge graph can guarantee independently of ranking and how its facts map into the common evidence semantics.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/rag/knowledge/types.go`
- `pkg/rag/knowledge/contract.go`
- `pkg/rag/knowledge/validate.go`
- `pkg/rag/knowledge/deterministic.go`
- `pkg/rag/knowledge/repository.go`
- `pkg/rag/knowledge/sqlite.go`
- `pkg/rag/knowledge/retrieve`
- `pkg/rag/knowledgetools`
- `cmd/rag-ttc/cmds/knowledge`

### Why this project exists

- The knowledge package has rich source-grounded structures: concepts, aliases, mentions, facts, evidence spans, and validation. This is an ideal proving ground for typed facts and provenance.
- The retrieval planner combines candidate discovery, ambiguity handling, ranking, and result limits. That makes it hard to state whether a missed fact was undiscoverable or merely excluded by policy.
- Knowledge facts can support multi-hop retrieval, but confidence thresholds and limits can make recursive behavior non-monotone if they are treated as canonical admission.
- A disciplined separation can make the knowledge repository usable by several policies and evaluators without losing its domain-specific constraints.

### Source-level observations to verify

- `pkg/rag/knowledge/types.go` distinguishes candidates, validated extractions, stored concepts/facts, and supporting spans; retain these domain stages.
- `pkg/rag/knowledge/retrieve` should be inspected for where lookup, ambiguity handling, ranking, and limits occur in one planner call.
- `pkg/rag/knowledge/deterministic.go` and tests provide existing stable-ID/order behavior to preserve.
- `pkg/rag/knowledgetools` demonstrates scoped access patterns that may be useful as explicit discovery operations.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. What is the complete candidate relation for a query surface: exact canonical names, aliases, mentions, topics, facts, neighboring concepts, and supporting chunks?
2. How should ambiguity be represented when one surface maps to several concepts, rather than resolved prematurely?
3. Which confidence values are extraction observations and which are stable attributes of the stored model?
4. How should source evidence spans and normalization decisions map into canonical facts and derivations?
5. Can candidate discovery be monotone with respect to repository additions while selection remains an explicit view?
6. Which graph expansion operations are suitable as closure rules, and what bounds are policy rather than semantics?

### Falsifiable hypotheses

1. The planner can be factored into `Discover -> ExplainAmbiguity -> Expand -> Rank/Limit` without reducing current compatibility behavior.
2. A lossless candidate graph will reveal cases where current limits or early ambiguity resolution discard useful evidence.
3. Repository additions are monotone for candidate discovery when identifiers and normalization versions are stable.
4. Knowledge facts and supporting spans can be mapped into the P02 fact/provenance contract without treating model confidence as fact identity.
5. A simple deterministic selection policy over the lossless candidate graph can reproduce current planner outputs on frozen fixtures.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Inventory current concept/fact extraction, validation, normalization, storage, and retrieval contracts.
- Define lossless candidate records for surface matches, concept matches, fact edges, topic associations, mentions, and source supports.
- Represent ambiguity explicitly, including competing concepts and the evidence for each mapping.
- Implement pure selection policies that can reproduce current behavior and alternative policies for comparison.
- Map knowledge objects to canonical facts/derivations and selected chunks to ranked views.
- Evaluate discovery completeness and selection loss on synthetic and repository-derived queries.

### Explicit non-goals

- Building a general-purpose knowledge graph platform.
- Solving open-domain entity linking or ontology alignment.
- Assuming model-generated extraction candidates are factually correct without validation.
- Replacing SQLite for performance reasons alone.
- Integrating baseline lexical/vector retrieval; P08 covers composition.

## System to build

1. A standalone in-memory knowledge fixture and candidate-discovery API with deterministic JSON output.
2. An adapter over `knowledge.Repository`/SQLite returning the same neutral candidate graph.
3. Explicit ambiguity, match-reason, path, confidence observation, and source-support records.
4. At least three pure selection policies: current-compatible, lossless/high-recall diagnostic, and a deliberately conservative policy.
5. A stage-aware evaluator distinguishing surface lookup, concept discovery, fact expansion, chunk support, and final selection.
6. A set of ambiguous, multi-hop, conflicting, and normalization-version fixtures.

### Proposed API sketch

```go
package knowledgediscovery

type SurfaceMatch struct {
    Surface      string
    ConceptID    string
    MatchKind    string
    MatchValue   string
    Confidence   *float64
    SupportFacts []FactID
}

type FactEdge struct {
    FactID     FactID
    SubjectID  string
    Predicate  string
    ObjectID   string
    Support    []FactID
}

type CandidateGraph struct {
    QueryID    string
    Surfaces   []SurfaceMatch
    Concepts   []ConceptRef
    Facts      []FactEdge
    Chunks     []FactID
    Paths      []Path
    Diagnostics []Diagnostic
}

type Discoverer interface {
    Discover(context.Context, Query) (CandidateGraph, error)
}

type Selector interface {
    ID() string
    Select(Query, CandidateGraph) (KnowledgeView, SelectionTrace, error)
}
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Discovery determinism | A fixed repository snapshot and query produce one canonical candidate graph. | Permutation/restart tests with stable serialization. |
| Discovery monotonicity | Adding repository facts cannot remove previously discoverable candidates. | Nested repository fixtures and delta tests. |
| Ambiguity preservation | All valid concept matches survive discovery; resolution occurs only in a view. | Ambiguous-surface fixtures. |
| Support completeness | Every candidate fact/chunk records a path to its source support. | Graph verifier and missing-support mutations. |
| Policy separation | Changing ranking/limits changes only the view, not the candidate graph. | Snapshot hash and policy matrix. |
| Compatibility | A versioned compatibility policy reproduces frozen current planner output. | Golden query fixtures. |
| Normalization sensitivity | Changing normalization schema/version changes affected candidate identity or snapshot identity. | Version-skew tests. |
| Repository equivalence | In-memory and SQLite adapters return equal graphs for equal logical contents. | Backend conformance fixtures. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: Ambiguous alias

**Setup.** One surface form is an alias for two concepts with different supporting mentions and facts.

**Procedure.** Run discovery, current-compatible selection, conservative selection, and a policy using query context.

**Expected observations.** Discovery retains both concepts and all supports; each policy gives a reproducible, explained view.

**Failure interpretation.** A concept disappears before policy or the ambiguity cannot be reconstructed from the trace.
### Scenario 2: Two-hop fact bridge

**Setup.** The answer-supporting chunk is reachable only through concept A -> fact -> concept B -> mention/chunk.

**Procedure.** Vary expansion depth and selection limits while comparing candidate graph and selected evidence.

**Expected observations.** Discovery exposes the full path at sufficient depth; selection loss is attributed separately.

**Failure interpretation.** The system cannot identify whether the path was undiscovered or excluded.
### Scenario 3: Repository addition

**Setup.** Start with a snapshot lacking one alias/support edge, then add it without modifying existing rows.

**Procedure.** Compare candidate graphs and views before/after under stable IDs.

**Expected observations.** Old candidates remain and new ones are added; a view may reorder but the candidate relation is monotone.

**Failure interpretation.** Existing candidates vanish or change identity due solely to append-only data.
### Scenario 4: Invalid extraction and source span

**Setup.** Inject knowledge candidates with missing concepts, mismatched quotes, invalid spans, or unsupported fact objects.

**Procedure.** Run validation/admission and then discovery.

**Expected observations.** Invalid items remain diagnostics/rejections and never appear as admitted candidate facts.

**Failure interpretation.** Discovery leaks rejected or unverifiable items.


### Metrics

- Surface-match, concept, fact-edge, and supporting-chunk recall on labeled fixtures.
- Ambiguity set size and rate of premature resolution.
- Path recall by hop depth.
- Candidate-to-selected loss by policy and limit.
- Compatibility agreement with current planner outputs.
- SQLite versus in-memory graph equality and performance.
- Unsupported or rejected candidate rate with diagnostic categories.

### Fault injection

- Duplicate aliases and normalization collisions.
- Dangling concept/fact references.
- Conflicting facts with distinct support spans.
- Invalid or shifted character spans.
- Repository row insertion order changes.
- Normalization and schema version skew.
- Depth and candidate limits placed at discovery versus view stages.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - planner decomposition | Current phases and hidden selection points mapped with frozen outputs. |
| M2 - candidate graph | Standalone and repository adapters produce deterministic lossless graphs. |
| M3 - provenance mapping | Knowledge objects map to facts/derivations with source-support validation. |
| M4 - policy suite | Compatibility and alternative selectors implemented with traces. |
| M5 - evaluation | Ambiguity, multi-hop, additions, and invalid-data studies complete. |
| M6 - hand-off | Candidate graph schema, fixtures, adapters, and recommendations published. |

## Acceptance gates

- Candidate discovery retains all valid ambiguous matches in the shared fixture.
- Every candidate fact and chunk has a source-support path or explicit diagnostic.
- Adding repository records does not remove old candidates in tested append-only cases.
- Selection policies do not mutate the candidate graph.
- The compatibility selector reproduces frozen planner outputs or documents intentional deltas.
- SQLite and in-memory adapters agree on neutral fixtures.
- Invalid extraction fixtures are rejected before discovery.
- The report identifies which current limits belong to discovery safety versus selection policy.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- Query records and immutable knowledge repository snapshots.
- P02-compatible fact/provenance IDs or local equivalents.
- P04-compatible view contracts for optional policy evaluation.

### Outputs offered to later projects

- `knowledge-candidate-graph/v1`, `knowledge-path/v1`, and `knowledge-view/v1` schemas.
- Discovery and selector interfaces.
- Ambiguous-knowledge and multi-hop fixtures for P05 and P08.
- Stage-aware knowledge retrieval metrics.

### Expected composition experiments

- Expose discovery operations as P05 rules and compare depth-limited versus saturated candidate graphs.
- Feed candidate chunk observations into P04 ranking without losing knowledge paths.
- Combine knowledge candidates with baseline channels in P08.
- Apply P11 repository deltas and verify discovery monotonicity/incremental maintenance.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| Candidate explosion | Measure graph size and keep safety caps explicit; do not confuse an operational cap with semantic completeness. |
| Confidence semantics unclear | Record whether confidence belongs to extraction observation, stored assertion, or selection policy. |
| Compatibility overfitting | Preserve a compatibility selector but allow the candidate graph to expose better alternatives. |
| Entity-linking scope growth | Use controlled fixtures and current normalization; document unresolved open-world issues. |
| Source span inconsistency | Reuse or strengthen existing validation and include byte/character conventions in schemas. |

## Questions the final report must answer

1. Where exactly did current discovery end and selection begin?
2. What information was lost by early ambiguity resolution or limiting?
3. Which knowledge records are canonical facts versus observations or views?
4. Does append-only repository growth produce monotone discovery in practice?
5. How does policy choice affect useful multi-hop evidence?
6. What is the smallest candidate graph contract that supports connected RAG?
7. Which current planner behavior should be retained, revised, or removed?

## Stretch investigations

- Calibrated ambiguity views using query context without changing the lossless candidate graph.
- Counterfactual path explanations for why a fact was not selected.
- Incremental candidate graph maintenance over repository change logs.
- A small browser for inspecting concepts, facts, paths, and source spans.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/knowledge-discovery-selection` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, sections 4.7, 8.7, 9.4, 9.7, and 11 Phase 3.
- Datalog and recursive query processing references for relation discovery and graph expansion.
- W3C PROV-DM for representing source support paths.
- Entity linking literature focused on candidate generation versus disambiguation as separate stages.
- rag-ttc knowledge validation and repository tests as current executable contracts.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# P08 - Connected Retrieval Composition

## Assignment summary

**Project code:** P08  
**Track:** Subsystem semantics: retrieval composition  
**Suggested duration:** 6-8 weeks  
**Suggested team:** 2 students  
**Program priority:** High

Treat baseline lexical/vector retrieval and knowledge retrieval as independently testable candidate producers, then study principled ways to combine them. Separate gating, channel fusion, source admission, and final selection so that each composition law and failure mode can be evaluated directly.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/rag/connected/runtime.go`
- `pkg/rag/connected/runtime_test.go`
- `pkg/rag/connectedconfig`
- `pkg/rag/retrieval`
- `pkg/rag/knowledge/retrieve`
- `pkg/rag/answering`
- `pkg/rag/evaluation`
- `cmd/rag-ttc/cmds/experiments/answerquality`

### Why this project exists

- The connected runtime already composes baseline and knowledge retrieval with a deterministic gate and weighted fusion. It is a concrete subsystem in which semantic identity, candidate merge, policy views, and execution traces meet.
- The current runtime trace includes baseline channels, fused lists, knowledge outputs, gate decisions, selected evidence, labels, and timing. This makes it possible to decompose and assess each stage instead of treating connected RAG as one opaque retriever.
- A connected result can change because of candidate discovery, gate policy, fusion parameters, source hydration, limits, or ordering. These causes should have separate identities and tests.
- This project is the principal first-pass composition study while still remaining self-contained through recorded channel fixtures.

### Source-level observations to verify

- `pkg/rag/connected/runtime.go` already emits a rich trace with baseline channels, fused results, gate, selected evidence, and labels; use it to locate stage boundaries.
- `Options.RRFConstant` influences fusion; inspect whether it is included in `SemanticDigest` and all artifact identities.
- The runtime performs baseline and knowledge augmentation with current deterministic policies; freeze this before refactoring.
- `cmd/rag-ttc/cmds/experiments/answerquality` provides realistic experiment integration and artifact patterns.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. What is the correct semantic contract for a gate: a policy view, a planning decision, or a rule that changes the candidate universe?
2. Should baseline and knowledge channels be unioned before selection, fused as observations of canonical facts, or treated as separate ranked views?
3. Which configuration fields define candidate production, gate behavior, fusion behavior, and final context selection?
4. Does channel execution order or failure change the semantic candidate state, selected view, or only trace/status?
5. How should partial channel failure be represented without confusing unavailable evidence with empty evidence?
6. Which composition policies improve retrieval and answer quality, and at what cost or provenance complexity?

### Falsifiable hypotheses

1. The runtime can be factored into `ProduceBaseline`, `ProduceKnowledge`, `Gate`, `JoinCandidates`, `FuseView`, and `SelectContext` with separately testable identities.
2. Concurrent and sequential execution of independent channels produce the same candidate state and selected view when both succeed.
3. The RRF constant, channel weights, gate configuration, and algorithm versions all belong to explicit policy identity.
4. Representing channel failure separately from an empty result improves reproducibility and prevents misleading gate/fusion behavior.
5. A union-first candidate model with multi-channel observations provides better provenance and policy reuse than mutating a completed baseline answer result.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Freeze current connected-runtime behavior on controlled recorded fixtures.
- Decompose baseline production, knowledge production, gate, candidate merge, fusion, hydration, and selection into explicit functions or adapters.
- Define channel result states: success with candidates, success empty, unavailable/retryable, failed permanent, and skipped by policy.
- Implement and compare at least three composition policies: current-compatible gated fusion, unconditional union/fusion, and diagnostic side-by-side views.
- Audit and test semantic digests for all behavior-affecting configuration.
- Evaluate retrieval, context, provenance, latency, and failure behavior.

### Explicit non-goals

- Training a new retriever or reranker.
- Redesigning the knowledge extraction pipeline.
- Claiming one composition policy is universally optimal from a small evaluation set.
- Hiding channel failures by silently falling back without trace.
- Building a generic plugin framework for arbitrary retrievers.

## System to build

1. A standalone connected-composition model using recorded baseline and knowledge channel outputs.
2. A stage graph and typed intermediate records for channel results, gate decisions, joined candidates, fused views, and selected context.
3. A compatibility adapter around the current `connected.Runtime` and trace.
4. A configuration identity audit and sensitivity suite including RRF constant and algorithm version.
5. A failure-policy matrix covering channel timeout, empty result, corrupt candidate, hydration failure, and gate uncertainty.
6. An evaluation runner producing stage-separated quality, cost, latency, and provenance metrics.

### Proposed API sketch

```go
package connectedmodel

type ChannelStatus string
const (
    ChannelSuccess ChannelStatus = "success"
    ChannelEmpty ChannelStatus = "empty"
    ChannelUnavailable ChannelStatus = "unavailable"
    ChannelFailed ChannelStatus = "failed"
    ChannelSkipped ChannelStatus = "skipped"
)

type ChannelResult struct {
    Channel    string
    Status     ChannelStatus
    Candidates CandidateSet
    Trace      json.RawMessage
    ErrorClass string
}

type Gate interface {
    ID() string
    Decide(Query, map[string]ChannelResult) GateDecision
}

type Composer interface {
    ID() string
    Compose(Query, map[string]ChannelResult, GateDecision) (CandidateSet, CompositionTrace, error)
}

type Pipeline struct {
    Baseline Producer
    Knowledge Producer
    Gate Gate
    Composer Composer
    View view.Policy
}
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Channel independence | Reordering independent channel execution does not change successful channel outputs. | Sequential/parallel and completion-permutation tests. |
| Candidate merge ACI | Combining channel candidate states is associative, commutative, and idempotent. | P03-style law suite over recorded outputs. |
| Status distinction | Empty, unavailable, failed, and skipped channels remain distinguishable. | Failure-policy fixtures and serialized traces. |
| Policy determinism | Gate, fusion, and selection are deterministic for a fixed input snapshot and versioned configuration. | Permutation and restart tests. |
| Identity sensitivity | Every demonstrated behavior-changing parameter changes the relevant stage identity. | Configuration mutation matrix. |
| Provenance preservation | Every final selected item retains all contributing channels and source derivations. | Trace-to-view consistency checks. |
| Fallback honesty | Fallback results explicitly record the unavailable/failed channel and policy used. | Timeout and permanent-failure tests. |
| Compatibility | The current-compatible composition reproduces frozen runtime outputs. | Golden connected fixtures. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: Baseline and knowledge overlap

**Setup.** Both channels return the same chunk plus distinct chunks, with ranks designed to make RRF parameter changes visible.

**Procedure.** Run compatibility, union, and diagnostic policies under sequential and parallel channel execution.

**Expected observations.** One canonical chunk fact retains both channel observations; policy views are deterministic and separately identified.

**Failure interpretation.** Duplicate source facts, lost contributions, or execution-order changes expose a composition flaw.
### Scenario 2: Gate boundary cases

**Setup.** Construct knowledge outputs just below, at, and above the current minimum fact-subject threshold, including ambiguous subjects.

**Procedure.** Evaluate gate decisions, candidate production cost, and selected context across configurations.

**Expected observations.** Gate identity and trace explain the boundary exactly; changing the threshold changes policy identity.

**Failure interpretation.** Unexplained gate behavior or identity collision invalidates reproducibility.
### Scenario 3: Channel failure matrix

**Setup.** Inject timeout, transient error, permanent error, corrupt payload, empty success, and hydration failure independently into each channel.

**Procedure.** Apply fail-closed, explicit fallback, and partial-result policies.

**Expected observations.** Statuses remain distinct and every final result says which policy handled the failure.

**Failure interpretation.** Failure is indistinguishable from no evidence or silently changes semantic identity.
### Scenario 4: Quality-cost frontier

**Setup.** Use a small labeled query set with recorded baseline and knowledge outputs and answer-generation recordings.

**Procedure.** Sweep gate thresholds, RRF constants, weights, k, and composition policies.

**Expected observations.** Reports show candidate recall, selected recall, answer support, added operations, latency, and provenance complexity as separate dimensions.

**Failure interpretation.** A single aggregate score obscures which stage or cost produced the difference.


### Metrics

- Baseline-only, knowledge-only, union candidate recall, and final selected recall.
- Overlap rate and number of alternative channel observations per fact.
- Gate open rate, false-negative gate cases, and avoided knowledge calls.
- NDCG/MRR or existing retrieval metrics for each view policy.
- Answer support/citation use on recorded generation runs.
- Channel latency, total latency, operations, tokens, and failures.
- Configuration sensitivity coverage and compatibility agreement.

### Fault injection

- Channel completion order permutations.
- Timeout, cancellation, transient, and permanent channel errors.
- Success-empty versus unavailable response.
- Duplicate and conflicting candidate IDs across channels.
- RRF constants and weights at numerical boundary cases.
- Hydration failure after fusion.
- Stale knowledge database or configuration digest.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - frozen baseline | Current connected behavior captured in deterministic fixtures and stage diagram. |
| M2 - decomposition | Typed channel, gate, merge, fusion, and selection interfaces implemented. |
| M3 - identity and law suite | Composition laws and configuration sensitivity tests pass. |
| M4 - failure policies | Channel-status matrix and explicit fallback behavior complete. |
| M5 - evaluation | Quality-cost-provenance study across policies complete. |
| M6 - hand-off | Adapters, schemas, fixtures, and recommended composition contract published. |

## Acceptance gates

- Current-compatible mode reproduces frozen connected outputs or documents intentional corrections.
- RRF constant and all behavior-affecting stage parameters participate in versioned identity.
- Sequential and parallel successful channel runs have equal candidate states and views.
- Empty, unavailable, failed, and skipped channels remain distinguishable through the final trace.
- Overlapping channel results retain all contributions without duplicating canonical facts.
- Every selected item can be traced to channel observations and source facts.
- The evaluation reports quality, cost, latency, and provenance separately.
- At least one composition policy is rejected or constrained by a demonstrated counterexample.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- Recorded baseline and knowledge channel outputs.
- P03-compatible candidate merge and P04-compatible view contracts, or local fakes.
- P07 knowledge candidate graph fixtures.

### Outputs offered to later projects

- `channel-result/v1`, `gate-decision/v1`, and `composition-trace/v1` schemas.
- Connected composition policies and compatibility adapter.
- Failure matrix and overlap fixtures for P06, P09, and program composition.
- Stage-separated quality/cost result format.

### Expected composition experiments

- Run channel producers through P06 execution policies and compare semantic results.
- Replace local merge/view fakes with P03/P04 implementations and rerun conformance.
- Use P05 to allow knowledge expansion before connected selection.
- Store all channel states, policy identities, and traces in P10 replay bundles.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| Current trace treated as perfect semantics | Use it to freeze compatibility, then explicitly distinguish facts, observations, views, and operational fields. |
| Gate changes candidate availability | Record whether the gate prevents execution or merely selects a view; these have different semantics/costs. |
| Evaluation dataset too small | Use results for subsystem diagnosis and hypothesis refinement, not universal claims. |
| Silent fallback | Require explicit channel status and fallback policy in final artifacts. |
| Configuration sprawl | Assign identity at each stage rather than one opaque mega-digest. |

## Questions the final report must answer

1. What is the semantic role of the gate?
2. Which stage owns each connected configuration field?
3. How should overlapping channel evidence be represented?
4. Which channel failure policies are sound and transparent to users?
5. Does current-compatible fusion preserve all candidate/provenance information needed by later policies?
6. What quality-cost frontier was observed?
7. What changes are recommended for `connected.Runtime` and its trace?

## Stretch investigations

- Adaptive gate policy evaluated without changing candidate semantics.
- More than two channels with algebraic composition plans.
- Per-query counterfactual: what knowledge candidate would have changed selection?
- An interactive stage explorer over the existing chat UI.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/connected-retrieval-composition` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, sections 4.2, 4.8, 8.8, 9.9, and 11 Phase 4.
- Primary RRF references for fusion behavior and parameter semantics.
- CALM for separating monotone candidate union from non-monotone gating/selection.
- Information retrieval fusion and failure-aware ensemble references.
- rag-ttc connected runtime and tests as the compatibility baseline.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# P09 - Tool-Agent Evidence and Citation Contracts

## Assignment summary

**Project code:** P09  
**Track:** Subsystem semantics: agentic/tool RAG  
**Suggested duration:** 6-8 weeks  
**Suggested team:** 2 students  
**Program priority:** High

Specify the semantics of tool-using RAG turns: tool requests, external observations, candidate evidence, citation labels, answer claims, and turn limits. Build a deterministic controller around recorded tool effects and assess whether every cited answer can be verified against the admitted evidence bundle.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/rag/toolanswer`
- `pkg/ttcrag`
- `pkg/rag/tooleval`
- `pkg/rag/toolconfig`
- `pkg/rag/agenttrace`
- `pkg/app/chat/agent_controller.go`
- `pkg/app/chat/tool_runtime.go`
- `pkg/app/session`
- `cmd/rag-ttc/cmds/chat/tooleval`

### Why this project exists

- Tool-oriented retrieval introduces an external interaction loop: the model chooses searches, results arrive asynchronously, evidence is labeled, and a final answer cites labels. This is where operational ordering, semantic evidence, and presentation identity are most easily confused.
- Current turn ledgers enforce evidence count/rune limits and assign labels while handling concurrent searches. The semantics must state whether labels depend on request order, completion order, result ranking, or a final deterministic view.
- Citation validation currently demonstrates reference to an admitted label, not necessarily textual entailment or factual correctness. The system should make this guarantee precise rather than overclaiming.
- A proof-carrying turn bundle can support offline replay, user inspection, agent comparison, and security checks.

### Source-level observations to verify

- `pkg/ttcrag/search.go` should be examined for mutex-protected label/budget assignment and arrival-order effects.
- `pkg/rag/toolanswer` contains a parallel evidence/session design; compare semantics rather than choosing one by package age.
- `pkg/rag/tooleval` and chat command paths already provide evaluation/artifact integration.
- `pkg/app/session` and `pkg/rag/agenttrace` offer durable turn/agent trace structures that should remain distinct from canonical evidence.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. What are the identities of a tool definition, tool request, tool execution, external observation, admitted fact, citation label, and answer claim?
2. When several searches complete concurrently, which aspects of the final turn must be permutation-invariant?
3. Should evidence limits constrain execution, candidate admission, selected context, or only presentation?
4. What exactly does a valid citation prove: label existence, source inclusion, quote support, claim entailment, or something else?
5. How should failed, cancelled, duplicated, or replayed tool calls affect the turn state and agent budget?
6. Can controller policy be separated from model decisions sufficiently to compare agents over one recorded observation universe?

### Falsifiable hypotheses

1. A turn can be modeled as an append-only set of requests, observations, facts, and derivations plus a deterministic selected/citation view and final answer observation.
2. Moving citation label assignment after candidate collection eliminates completion-order dependence without reducing auditability.
3. Tool-call retries and duplicate results are semantically transparent when request/observation IDs and evidence merge are idempotent.
4. Citation validity can be split into increasingly strong checks: referenced label, selected fact, source-span integrity, quote support, and optional entailment assessment.
5. Recorded tool effects allow deterministic controller/agent comparisons even when live generation remains stochastic.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Model a turn state with tool requests, attempts, observations, admitted facts, selected evidence, citation labels, answer text, and claims.
- Separate candidate evidence collection from deterministic budgeted selection and labeling.
- Implement recorded tool search effects and replay across controller variants.
- Define and implement a citation validation ladder with explicit guarantee levels.
- Adapt either `pkg/ttcrag` or `pkg/rag/toolanswer`, then compare the other implementation against the contract.
- Evaluate concurrency, retry, budgeting, malformed citations, and multi-turn behavior.

### Explicit non-goals

- Proving arbitrary natural-language entailment with mathematical certainty.
- Designing a generally intelligent autonomous agent.
- Allowing arbitrary side-effecting tools; focus on retrieval/read-only tools or captured effects.
- Replacing the existing chat UI.
- Treating model-generated chain-of-thought as required provenance.

## System to build

1. A standalone turn-state model and controller over deterministic scripted agents and recorded retrieval tools.
2. Versioned identities and schemas for tool requests, observations, evidence candidates, selected citation view, claims, and answer.
3. A deterministic selection/labeling policy with item and size budgets applied after candidate merge.
4. A citation validator supporting at least four levels: syntax/label, selected-fact, source integrity, and quote/span support.
5. Adapters and behavior comparison for current `ttcrag` and `toolanswer` paths.
6. An offline turn explorer showing timeline, semantic state, selected evidence, labels, answer claims, and validation results.

### Proposed API sketch

```go
package toolturn

type ToolRequest struct {
    ID         string
    ToolID     string
    Arguments  json.RawMessage
    SemanticKey string
}

type ToolObservation struct {
    ID        string
    RequestID string
    Status    string
    Payload   json.RawMessage
    ErrorClass string
}

type TurnState struct {
    Requests     map[string]ToolRequest
    Observations map[string]ToolObservation
    Evidence     FactState
    Answers      map[string]AnswerObservation
}

type CitationLevel string
const (
    CitationLabel CitationLevel = "label"
    CitationSelectedFact CitationLevel = "selected_fact"
    CitationSourceIntegrity CitationLevel = "source_integrity"
    CitationQuoteSupport CitationLevel = "quote_support"
)

type Controller interface {
    Run(context.Context, TurnInput, Agent, ToolRegistry, Policy) (TurnBundle, error)
}

func ValidateCitations(bundle TurnBundle, level CitationLevel) CitationReport
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Request identity | Equivalent tool calls have one semantic request identity independent of attempt. | Canonical argument and retry tests. |
| Observation immutability | One observation ID never names two external responses. | Conflict and replay tests. |
| Duplicate transparency | Repeated delivery of one observation/fact does not change the semantic turn. | Retry and duplicate-result fixtures. |
| Completion-order independence | A fixed set of successful observations produces one candidate state and selected citation view. | Exhaustive completion permutations. |
| Budget validity | Selected evidence respects the declared item/size budget; candidate state remains intact. | Boundary and oversized-result tests. |
| Citation referential integrity | Every cited label resolves to exactly one selected fact. | Malformed, missing, duplicate-label tests. |
| Guarantee honesty | The validator reports only the level actually checked. | Claims with valid labels but unsupported quotes. |
| Replay equivalence | Replaying recorded observations under the same controller policy reproduces semantic turn output before stochastic generation. | Live-recorded versus replay comparison. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: Concurrent multi-search turn

**Setup.** A scripted agent issues three searches whose results overlap and finish in every possible order under a tight evidence budget.

**Procedure.** Compare current ledgers, proposed candidate state, selected labels, and final recorded answer.

**Expected observations.** Candidate state and labels are permutation-invariant under the proposed policy; only timeline/attempt trace differs.

**Failure interpretation.** Label shifts or evidence loss reveal completion-order admission.
### Scenario 2: Citation guarantee ladder

**Setup.** Create answers containing a valid label with unsupported claim, wrong quote, missing label, duplicate label, and correct source-supported claim.

**Procedure.** Run each validation level and inspect pass/fail reasons.

**Expected observations.** Each level catches exactly the errors in its stated scope and does not claim entailment when only reference integrity was checked.

**Failure interpretation.** A weak check is reported as stronger or diagnostics cannot localize the defect.
### Scenario 3: Retry after ambiguous timeout

**Setup.** A search produces a response but the controller sees a timeout and retries, receiving the same or a different observation ID.

**Procedure.** Test idempotency-key, duplicate-response, and conflicting-response policies.

**Expected observations.** Duplicate observations merge; conflicting observations remain explicit; attempts do not become separate facts by default.

**Failure interpretation.** The turn double-counts evidence or silently overwrites conflicting effects.
### Scenario 4: Recorded-agent comparison

**Setup.** Record a finite universe of tool observations for a query and use two scripted/model-controller policies over the same universe.

**Procedure.** Compare requests, selected evidence, citation validity, answer support, cost, and stop reasons.

**Expected observations.** Differences are attributable to controller/agent policy rather than external search variance.

**Failure interpretation.** Hidden live effects or unstable evidence identity prevent controlled comparison.


### Metrics

- Completion-permutation unique candidate/view output count.
- Duplicate and conflicting observation handling accuracy.
- Citation precision by validation level.
- Selected evidence coverage and unused cited/selected evidence rates.
- Tool requests, attempts, unique observations, tokens, latency, and stop reasons.
- Replay agreement before and after generation.
- Behavioral differences between `ttcrag` and `toolanswer` adapters.

### Fault injection

- Random completion order and duplicate delivery.
- Timeout after effect, cancellation, and retry.
- Malformed tool arguments and unknown tools.
- Oversized, empty, corrupt, or partially hydrated results.
- Missing, duplicate, invented, and out-of-range citation labels.
- Source text changed after observation.
- Agent exceeds turn/tool/evidence budgets.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - turn ontology | Requests, attempts, observations, evidence, views, labels, claims, and traces classified. |
| M2 - standalone controller | Scripted agent and recorded tools produce deterministic proof-carrying turns. |
| M3 - ledger/label policy | Completion permutation and budget law suite passes. |
| M4 - citation validator | Guarantee ladder and adversarial claim fixtures complete. |
| M5 - rag-ttc adapters | Both current tool paths compared against the contract. |
| M6 - evaluation and hand-off | Replay study, explorer, schemas, and recommendations published. |

## Acceptance gates

- Candidate evidence is separate from selected/labeled evidence.
- All completion permutations of the shared tool fixture yield one proposed candidate state and citation view.
- Duplicate observations are idempotent and conflicts are explicit.
- The citation validator states and tests at least four guarantee levels.
- A valid-label but unsupported-quote fixture fails the appropriate stronger level.
- Recorded replay reproduces the controller state without live tools.
- Current `ttcrag` and `toolanswer` behavior is compared with concrete deltas.
- The final report avoids claiming factual truth from citation-reference checks alone.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- P02/P03-compatible facts and deterministic merge, or local contract-compatible fakes.
- P06 captured tool effects.
- P04 selected evidence view or a local deterministic selection policy.

### Outputs offered to later projects

- `tool-request/v1`, `tool-observation/v1`, `turn-bundle/v1`, and `citation-report/v1` schemas.
- Recorded tool-effect corpus and completion-permutation fixtures.
- Citation guarantee ladder and validator.
- Turn explorer artifacts for P10 and composition studies.

### Expected composition experiments

- Execute tool requests through P06 retry/cache policies and verify turn semantic equivalence.
- Use P08 connected retrieval as one tool and preserve its channel provenance in citations.
- Store proof-carrying turns in P10 experiment/session artifacts.
- Apply P13 access projection before selected citation views and answer generation.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| Citation equals truth | Use explicit validation levels and reserve entailment/factuality for separate assessed checks. |
| Agent nondeterminism hides controller defects | Use scripted agents and recorded model outputs for law tests. |
| Budget semantics remain order-dependent | Apply limits to a deterministic snapshot or explicitly version an order-sensitive policy. |
| Tool side effects | Restrict the reference study to read-only/captured effects and state stronger preconditions for others. |
| Trace as chain-of-thought | Record public decisions, requests, observations, and reasons; do not require hidden model reasoning. |

## Questions the final report must answer

1. What exactly does the turn state contain, and which parts are semantic versus operational?
2. When are evidence labels assigned and what identifies them?
3. Which citation guarantee levels are practical and reliable?
4. How do current tool implementations differ under completion-order and budget tests?
5. What does replay reproduce, and where does stochastic generation remain?
6. Which agent/controller comparisons became possible after effect capture?
7. What user-facing explanation should accompany a citation validation result?

## Stretch investigations

- Claim segmentation and quote-level support mapping.
- Selective replay where only missing observations are executed live.
- Multi-agent comparison over one recorded tool universe.
- A user study of citation explanation levels and trust calibration.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/tool-agent-evidence-citations` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, sections 4.6, 4.9, 8.9, 9.10, and 11 Phase 5.
- W3C PROV-DM for relating requests/activities, observations/entities, and agents.
- Primary literature on tool-use evaluation and citation-grounded generation, with guarantee scope stated carefully.
- CRDT/CALM references for add-only turn state and completion-order independence.
- rag-ttc toolanswer, ttcrag, tooleval, and session tests as compatibility material.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# P10 - Proof-Carrying Experiments and Replay

## Assignment summary

**Project code:** P10  
**Track:** Reproducibility: artifacts and audit  
**Suggested duration:** 5-7 weeks  
**Suggested team:** 1-2 students  
**Program priority:** High

Extend rag-ttc’s strong experiment custody into a semantic replay bundle: immutable inputs, versioned identities, captured external observations, canonical outputs, operational traces, and verification results. Determine what can be reproduced exactly, replayed approximately, or only compared statistically.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/experiment`
- `pkg/flow/report.go`
- `pkg/rag/generation/observed.go`
- `pkg/rag/answering`
- `pkg/rag/agenttrace`
- `pkg/app/session`
- `pkg/rag/tooleval`
- `pkg/rag/diagnostic`
- `cmd/rag-ttc/cmds/experiments/answerquality`
- `cmd/rag-ttc/cmds/experiments/chunkcompare`

### Why this project exists

- The experiment package already copies immutable inputs, stores config digests, appends observations, and records terminal status. This is an excellent base for reproducible research.
- Exact replay requires more than a manifest: external model/tool observations, semantic identities, policy versions, source snapshots, and verifier results must be available or explicitly marked unavailable.
- A run may have equal semantic outputs but different operational traces, or equal configuration but different stochastic model output. The artifact format should represent these distinctions directly.
- The student project portfolio needs a shared evidence standard for comparing implementations and preserving counterexamples across teams.

### Source-level observations to verify

- `pkg/experiment` copies immutable inputs, records a config digest and host/module context, appends observations, and writes terminal status; preserve these strengths.
- `pkg/rag/generation/observed.go` and answering observations can supply captured effect/trace data but must be classified carefully.
- `pkg/app/session` is append-oriented and can serve as a second artifact family for turn replay.
- Current experiment commands write domain-specific results; the bundle should index them rather than flatten them.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. What minimum artifact set is required to verify a semantic result offline?
2. Which run components are inputs, captured effects, semantic outputs, views, traces, metrics, diagnostics, and terminal status?
3. What levels of reproducibility should be claimed: bitwise artifact, semantic replay, provider-request replay, statistical replication, or provenance verification?
4. How should partial/failed/cancelled runs be sealed so they remain inspectable and cannot be mistaken for complete results?
5. How can artifacts remain append-safe while final manifests and indexes are canonical and verifiable?
6. Can a replay tool detect semantic drift caused by code, identity version, configuration, corpus, or provider response changes?

### Falsifiable hypotheses

1. A versioned run bundle with immutable input copies, semantic fingerprints, captured effects, output states/views, and checksums can support deterministic offline replay for recorded fixtures.
2. Separating semantic comparison from trace comparison allows cached/retried/parallel runs to be recognized as equivalent while preserving cost differences.
3. A run-sealing manifest can detect missing, modified, extra, or version-incompatible artifacts.
4. Current experiment artifacts can be adapted incrementally without replacing `pkg/experiment` or changing ordinary Go experiment programs.
5. At least one current artifact family lacks enough identity or effect data to support the desired replay level.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Define a run-bundle schema and reproducibility-level taxonomy.
- Build a sealer/verifier that hashes artifacts, records schema/identity versions, and checks terminal completeness.
- Capture or import recorded provider/tool effects for one answer-quality and one tool-turn fixture.
- Implement replay that can skip external effects, recompute pure stages, and compare semantic outputs and traces separately.
- Implement a semantic diff explaining changed facts, derivations, views, answers, configuration fields, and trace events.
- Integrate the portfolio-wide `results.json` schema and neutral fixture custody.

### Explicit non-goals

- Guaranteeing that a live third-party model returns the same output in the future.
- Building a centralized experiment tracking service or web platform.
- Storing secrets or raw credentials in bundles.
- Replacing existing domain-specific result files with one generic blob.
- Treating successful process exit as proof of semantic validity.

## System to build

1. A versioned bundle layout with manifest, immutable inputs, captured effects, semantic outputs, views, traces, metrics, verifier reports, and terminal status.
2. A `seal` command that writes canonical artifact inventory and digests only after validating required files and statuses.
3. A `verify` command that detects mutation, omission, unknown schema, identity-version skew, and incomplete terminal state.
4. A `replay` command with modes such as pure, recorded-effects, live-missing, and compare-only.
5. A semantic diff command that compares two runs by stage and identifies the earliest divergent artifact.
6. Adapters for at least one existing experiment command and one interactive/tool session artifact.

### Proposed API sketch

```go
package replay

type ReproLevel string
const (
    BitwiseArtifacts ReproLevel = "bitwise_artifacts"
    SemanticReplay   ReproLevel = "semantic_replay"
    RequestReplay    ReproLevel = "request_replay"
    StatisticalReplication ReproLevel = "statistical_replication"
    ProvenanceOnly   ReproLevel = "provenance_only"
)

type Artifact struct {
    Path       string
    Role       string
    Schema     string
    Digest     string
    SemanticID string
    Required   bool
}

type BundleManifest struct {
    SchemaVersion string
    RunID         string
    Reproducibility []ReproLevel
    Inputs        []Artifact
    Effects       []Artifact
    Outputs       []Artifact
    Traces        []Artifact
    Reports       []Artifact
    Terminal      string
}

type ReplayMode string
func Seal(dir string) (BundleManifest, error)
func Verify(dir string) VerificationReport
func Replay(ctx context.Context, dir string, mode ReplayMode) (ReplayReport, error)
func Diff(left, right string) (SemanticDiff, error)
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Artifact integrity | Any byte change in a sealed required artifact is detected. | Mutation tests over every artifact class. |
| Manifest completeness | A sealed successful run contains all declared required roles. | Omission and extra-file tests. |
| Append-safe observations | Adding a valid later observation does not rewrite earlier observation bytes. | Prefix-digest and sequence tests. |
| Terminal honesty | Success, failure, cancellation, and partial status cannot be confused. | Interrupted-run sealing tests. |
| Replay determinism | Pure and recorded-effect stages reproduce semantic outputs under matching versions. | Offline replay golden fixtures. |
| Trace separation | Different attempts/timing may coexist with equal semantic output. | Cached/retried/parallel run comparison. |
| Version safety | Unknown or incompatible semantic/schema versions prevent silent replay. | Version-skew fixtures. |
| No secret custody | Bundles contain no raw configured credentials. | Static scan and injected-secret tests. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: Offline answer replay

**Setup.** Create a small answer-quality run with copied corpus/query/config, recorded retrieval/model effects, canonical evidence, selected view, answer, and metrics.

**Procedure.** Remove network access and caches, replay pure stages, and compare semantic outputs.

**Expected observations.** The run verifies and replays to the same semantic result under the declared identity versions.

**Failure interpretation.** A missing external observation or hidden configuration dependency blocks exact semantic replay.
### Scenario 2: Equivalent output, different trace

**Setup.** Run the same recorded workload sequentially, in parallel, with cache misses, with cache hits, and with injected retry.

**Procedure.** Seal and diff all bundles.

**Expected observations.** Semantic state/view equality is reported separately from timing/attempt/cache trace differences.

**Failure interpretation.** The diff either calls equivalent results different or erases important operational differences.
### Scenario 3: Corrupt and incomplete artifacts

**Setup.** Mutate a source file, remove one captured effect, append junk, alter terminal status, and mix identity versions.

**Procedure.** Run verifier and replay.

**Expected observations.** Every corruption is localized; replay is blocked or downgraded to an honest reproducibility level.

**Failure interpretation.** The tool silently trusts invalid custody or reports exact replay when prerequisites are missing.
### Scenario 4: Earliest semantic drift

**Setup.** Create paired runs differing one at a time in corpus, chunker, embedding model, fusion constant, ranking policy, generator profile, and code version.

**Procedure.** Run semantic diff and inspect divergence explanation.

**Expected observations.** The earliest affected stage and identity component are identified for each pair.

**Failure interpretation.** The diff reports only final output differences with no causal localization.


### Metrics

- Percentage of studied runs supporting each reproducibility level.
- Replay success and semantic agreement rate.
- Corruption/omission/version-skew detection rate.
- Bundle size by artifact class and captured-effect overhead.
- Time to seal, verify, replay, and diff.
- Earliest-divergence localization accuracy.
- Number of hidden dependencies uncovered during replay.

### Fault injection

- Byte mutation, truncation, deletion, renaming, and extra artifacts.
- Interrupted writes and missing terminal marker.
- Schema and identity version skew.
- Cache entry available during original run but absent during replay.
- Provider response missing or associated with wrong request key.
- Clock/timing differences and reordered trace events.
- Injected secrets in config and trace payloads.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - artifact taxonomy | Current experiment/session files mapped to bundle roles and reproducibility levels. |
| M2 - seal/verify | Canonical manifest and corruption/version tests complete. |
| M3 - captured replay | One answer run replays offline from recorded effects. |
| M4 - semantic diff | Stage-aware comparison localizes controlled changes. |
| M5 - second adapter | Tool/session bundle and interrupted-run handling complete. |
| M6 - hand-off | Bundle schema, commands, fixtures, and custody recommendations published. |

## Acceptance gates

- A sealed bundle detects every required corruption fixture.
- At least one answer-quality run replays without network access.
- Equivalent semantic outputs with different traces are reported correctly.
- Incomplete and failed runs remain inspectable but cannot be mislabeled successful/complete.
- Unknown identity/schema versions block or explicitly downgrade replay.
- Semantic diff localizes controlled changes to the expected earliest stage.
- No raw credential appears in produced bundles.
- The adapter preserves normal Go experiment programs and existing artifact strengths.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- P01 semantic fingerprints and version tags or compatible local values.
- P02/P03 semantic state and P04 views where available.
- P06 captured effects and operational traces.
- Any project `results.json` conforming to the common schema.

### Outputs offered to later projects

- `run-bundle/v1`, `artifact-entry/v1`, `verification-report/v1`, and `semantic-diff/v1` schemas.
- Seal, verify, replay, and diff commands.
- Canonical bundles for the second-pass composition scenarios.
- Reproducibility-level assessment rubric.

### Expected composition experiments

- Seal one result from every project and verify common custody requirements.
- Replay P05 closure and P09 tool-turn scenarios from captured effects.
- Use P12 migration to transform an old bundle and verify semantic equivalence.
- Use P13 redaction/selective-disclosure policy and ensure the remaining bundle is honestly labeled.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| Reproducible means live deterministic | Use explicit reproducibility levels and captured observations. |
| Artifact mega-schema | Keep domain files typed; manifest indexes roles and versions rather than replacing them. |
| Append-only versus canonical manifest tension | Append observations during the run, then seal with a final immutable inventory. |
| Sensitive data leakage | Define redaction scans and never persist credentials. |
| Replay tool becomes a runner framework | Replay existing explicit commands/stages through adapters, not a new workflow language. |

## Questions the final report must answer

1. What reproducibility levels can current artifacts honestly support?
2. Which hidden dependencies prevented replay?
3. What belongs in the immutable manifest versus append-only observation log?
4. How should failed and partial runs be sealed?
5. What semantic/trace differences were most useful in debugging?
6. What bundle size and capture overhead are acceptable?
7. Which changes to `pkg/experiment` are minimal and justified?

## Stretch investigations

- Content-addressed bundle storage with deduplicated captured effects.
- A provenance query CLI across multiple runs.
- Reproduction capsules suitable for container execution.
- Automated minimization of a divergent run to the smallest counterexample bundle.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/proof-carrying-experiments-replay` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, sections 2.3, 3, 8.11-8.12, 9.11, 10.8, and 11 Phase 7.
- W3C PROV-DM for artifact and activity relationships.
- FAIR and reproducible computational research guidance from primary standards or institutional sources.
- Software supply-chain manifest concepts such as checksummed artifact inventories, used as comparison points.
- rag-ttc experiment package tests as the current custody contract.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# P11 - Incremental Maintenance, Updates, and Retractions

## Assignment summary

**Project code:** P11  
**Track:** State evolution: incremental computation  
**Suggested duration:** 6-8 weeks  
**Suggested team:** 2 students  
**Program priority:** Medium-high

Study how a previously computed RAG semantic state changes when documents, representations, indexes, knowledge records, or policies are updated. Implement correct append-only delta maintenance first, then compare explicit deletion/retraction strategies that preserve alternative derivations.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/rag/indexbundle`
- `pkg/rag/dataset`
- `pkg/rag/chunking`
- `pkg/rag/representations`
- `pkg/rag/embedding`
- `pkg/rag/knowledge/repository.go`
- `pkg/rag/knowledge/sqlite.go`
- `pkg/experiment`
- `pkg/app/session`

### Why this project exists

- The add-only closure laws imply a useful incremental result: after adding new seed facts, starting from the old closed state should agree with recomputing closure from the expanded seed. This can reduce indexing and multi-hop recomputation cost.
- Real corpora also change by deletion, correction, replacement, model-version migration, and policy change. These operations are not add-only and require dependency tracking, versioned snapshots, or a different algebra.
- Alternative derivations matter during retraction: a fact should disappear only when no valid derivation remains in the active snapshot.
- rag-ttc already treats documents and index bundles as immutable snapshots in many places. This project can build on that discipline rather than introducing in-place mutation as the default.

### Source-level observations to verify

- `pkg/rag/indexbundle` records bundle identity and verified documents; inspect current rebuild/reuse boundaries.
- Chunk and representation IDs already bind important source/model inputs, providing a natural invalidation graph.
- `pkg/rag/knowledge/sqlite.go` offers a persistent fact repository but not necessarily an explicit semantic change log.
- `pkg/experiment` can seal immutable update experiments and full-rebuild comparisons.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. What is the correct delta unit for documents, chunks, representations, vectors, knowledge facts, derivations, and selected views?
2. When does `Close(Close(old) join delta) = Close(old join delta)` hold for the studied rules?
3. How should replacements be represented: deletion plus addition, new immutable revision, or supersession relation?
4. What dependency index is sufficient to retract only facts whose last valid derivation is removed?
5. Which derived artifacts can be reused after source, algorithm, model, or policy changes, and how is this decided from identity?
6. How should incremental results be validated against full rebuilds and sealed into reproducible snapshots?

### Falsifiable hypotheses

1. For append-only corpus/knowledge deltas and monotone rules, incremental closure from the old saturated state is semantically equal to full recomputation.
2. Immutable source revisions plus snapshot manifests are simpler and safer than in-place mutation for most rag-ttc workflows.
3. Support-count or derivation-set tracking can implement exact retraction on finite provenance DAGs while preserving facts with alternative support.
4. View-only policy changes require no candidate-state recomputation when view identity is separated correctly.
5. Identity dependency analysis can substantially reduce recomputation after localized source additions but will intentionally invalidate broad model/schema changes.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Define source snapshots, append deltas, tombstones/supersession, active derivations, and derived-state checkpoints.
- Implement append-only incremental closure and compare it with full rebuild across generated update sequences.
- Implement at least two retraction strategies: full rebuild oracle and provenance-based incremental truth maintenance.
- Build dependency indexes from source facts to derivations and downstream facts.
- Classify updates by identity impact: source content, chunker, representation prompt/model, embedding model, index algorithm, knowledge normalization, ranking policy, generator profile.
- Evaluate correctness, work saved, storage overhead, and failure recovery.

### Explicit non-goals

- Building a continuously distributed database or production change-data-capture platform.
- Supporting arbitrary non-monotone rules without full recomputation.
- Mutating immutable source revisions in place.
- Optimizing a specific index backend beyond what is needed for experiments.
- Resolving conflicting concurrent edits to document text.

## System to build

1. A standalone finite derivation-state model with source snapshots, additions, tombstones, alternative supports, and full-rebuild oracle.
2. An incremental add evaluator using old closure plus deltas and a provenance-indexed retraction evaluator.
3. A dependency/impact analyzer that predicts which artifacts and stages must be recomputed for a typed change.
4. Adapters for a small rag-ttc corpus/index/knowledge fixture with immutable document revisions.
5. A checkpoint/resume format and consistency verifier.
6. A generated update-sequence benchmark containing additions, replacements, deletions, policy changes, crashes, and replays.

### Proposed API sketch

```go
package incremental

type SnapshotID string

type Snapshot struct {
    ID       SnapshotID
    Parents  []SnapshotID
    Sources  map[FactID]SourceStatus
    State    FactState
    Manifest Manifest
}

type ChangeKind string
const (
    Add       ChangeKind = "add"
    Retract   ChangeKind = "retract"
    Supersede ChangeKind = "supersede"
    PolicyOnly ChangeKind = "policy_only"
)

type Change struct {
    ID       string
    Kind     ChangeKind
    Fact     *Fact
    Target   FactID
    Metadata map[string]string
}

type Impact struct {
    Reusable     []ArtifactID
    Invalidated  []ArtifactID
    RecomputeRules []RuleID
    Reasons      []Reason
}

func ApplyAdditions(old Snapshot, changes []Change, rules []Rule) (Snapshot, UpdateReport, error)
func ApplyRetractions(old Snapshot, changes []Change, rules []Rule) (Snapshot, UpdateReport, error)
func FullRebuild(seed State, rules []Rule) Snapshot
func AnalyzeImpact(old Manifest, changes []Change) Impact
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Append equivalence | Incremental additions equal full recomputation from the expanded seed. | Generated finite update sequences and oracle comparison. |
| Old-fact preservation | Append-only changes do not remove prior active facts. | Subset tests after every addition. |
| Alternative-support retention | Retracting one derivation does not retract a fact with another active derivation. | Diamond-support fixtures. |
| Exact retraction | A fact is inactive exactly when no active seed/derivation supports it in the chosen semantics. | Truth-maintenance versus full-rebuild oracle. |
| Snapshot immutability | Earlier snapshots remain byte-verifiable after later changes. | Digest and mutation tests. |
| Idempotent change replay | Reapplying the same change ID has no extra semantic effect. | Duplicate event tests. |
| Policy isolation | Changing only a view policy leaves canonical candidate state reusable. | Impact-analysis and state-hash tests. |
| Checkpoint equivalence | Resume from checkpoint equals uninterrupted update processing. | Crash-at-boundary tests. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: Append-only corpus growth

**Setup.** Start with a closed two-hop fixture and add documents/chunks that create new paths and alternative supports.

**Procedure.** Apply changes incrementally and by full rebuild after each event.

**Expected observations.** States are equal; old facts remain; work metrics show reused closure and localized new derivations.

**Failure interpretation.** A mismatch identifies an invalid incremental rule or missing dependency.
### Scenario 2: Retraction with alternative support

**Setup.** A claim has two independent source derivations and one downstream fact depends on it.

**Procedure.** Retract each source separately and then both, comparing truth maintenance with full rebuild.

**Expected observations.** The claim/downstream fact remain after one retraction and disappear only after all valid supports are gone.

**Failure interpretation.** Premature or missing retraction indicates support accounting error.
### Scenario 3: Configuration impact matrix

**Setup.** Freeze artifacts for source, chunks, representations, vectors, indexes, knowledge, candidates, views, and answers.

**Procedure.** Change one field at a time: metadata, text, chunker, prompt, model, normalization, RRF, top-k, generator temperature.

**Expected observations.** Impact analysis invalidates exactly the semantically dependent stages under the published contracts.

**Failure interpretation.** Reusing an affected artifact is unsound; invalidating unrelated artifacts is inefficient and signals an unclear dependency model.
### Scenario 4: Crash and resume during update

**Setup.** Apply a multi-event delta and crash after source admission, derivation update, or checkpoint write.

**Procedure.** Resume with duplicate event delivery and compare against uninterrupted processing.

**Expected observations.** The final snapshot is equal and earlier snapshots remain intact.

**Failure interpretation.** Partial mutation, duplicate effects, or lost frontier breaks durability semantics.


### Metrics

- Semantic agreement with full rebuild after every update prefix.
- Rules/operations/facts recomputed versus reused.
- Wall time, CPU, memory, and checkpoint size.
- Dependency index storage overhead.
- Retraction cascade size and correctness.
- Impact-analysis precision and recall relative to actual changed outputs.
- Recovery success across injected crash points.

### Fault injection

- Duplicate, out-of-order, and missing change events.
- Retraction of unknown or already inactive sources.
- Replacement with identical content but different metadata and vice versa.
- Checkpoint truncation and version skew.
- Crash between state and manifest persistence.
- Alternative derivations with shared downstream dependencies.
- Policy-only change incorrectly treated as source change.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - update semantics | Snapshot, addition, supersession, retraction, and active-support rules specified. |
| M2 - add-only engine | Incremental additions equal full rebuild on generated sequences. |
| M3 - truth maintenance | Alternative-support retraction passes oracle comparison. |
| M4 - impact analyzer | Configuration change matrix classified and tested. |
| M5 - rag-ttc adapter | Corpus/index/knowledge fixture updates and checkpoint recovery complete. |
| M6 - hand-off | Update schemas, benchmark, counterexamples, and adoption guidance published. |

## Acceptance gates

- Every append-only update prefix matches full recomputation.
- Alternative-support fixtures retract exactly when the last support is removed.
- Earlier immutable snapshots verify after later updates.
- Duplicate change replay is idempotent.
- Checkpoint resume matches uninterrupted updates across all injected crash boundaries.
- Policy-only changes reuse canonical state in the impact model.
- The report states which update classes require full rebuild and why.
- Performance results quantify when incremental maintenance is worthwhile.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- P01 versioned identity/dependency information or compatible local manifest.
- P02 facts/derivations and P05 rule closure, or finite local equivalents.
- Immutable source/index/knowledge snapshots from rag-ttc fixtures.

### Outputs offered to later projects

- `snapshot/v1`, `change-event/v1`, `impact-report/v1`, and `update-report/v1` schemas.
- Generated update sequence and alternative-support fixtures.
- Incremental/full-rebuild oracle comparison harness.
- Checkpoint bundle for P10 and composition scenarios.

### Expected composition experiments

- Use P05 closure for additions and compare P11 delta execution with its full saturation.
- Apply updates to P07 candidate discovery and P08 connected composition.
- Seal each snapshot/update report using P10 and test replay.
- Combine with P13 authorization changes, distinguishing policy projection from source retraction.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| Deletion semantics underspecified | Define active snapshot and support semantics before optimizing. |
| Truth-maintenance complexity | Use finite DAG fixtures and full rebuild as the oracle; treat cycles explicitly. |
| Identity changes masquerade as updates | Version source and derived artifact identities; classify change types. |
| Incremental slower than rebuild | Measure crossover points and recommend selective adoption. |
| Mutable snapshot corruption | Prefer immutable revisions and atomic sealed checkpoints. |

## Questions the final report must answer

1. For which rules did append equivalence hold?
2. What is the exact semantics of retraction and supersession?
3. How were alternative derivations maintained?
4. Which configuration changes invalidate which stages?
5. When did incremental execution save enough work to justify complexity?
6. What crash/replay failure exposed the weakest persistence boundary?
7. Which changes should rag-ttc represent as new snapshots rather than in-place updates?

## Stretch investigations

- Delta rules derived automatically for a restricted rule language.
- Cycles and strongly connected provenance components under retraction.
- Cross-snapshot semantic diff and query impact explanation.
- Streaming ingestion benchmark with periodic closure checkpoints.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/incremental-updates-retractions` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, sections 9.12-9.13 and package adaptation sections for indexes, knowledge, experiments, and sessions.
- Differential Dataflow, McSherry, Murray, Isaacs, and Isard, for incremental iterative computation.
- DBSP: Automatic Incremental View Maintenance for Rich Query Languages, for algebraic incremental maintenance.
- Truth maintenance systems and database view maintenance references.
- Content-addressed immutable snapshot designs as engineering comparisons.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# P12 - Backend Conformance and Schema Migration

## Assignment summary

**Project code:** P12  
**Track:** Representation semantics: backends and evolution  
**Suggested duration:** 6-8 weeks  
**Suggested team:** 2 students  
**Program priority:** Medium-high

Demonstrate that semantic behavior can be independent of storage and representation. Implement multiple small backends for the same constructors and merge laws, then design a versioned schema migration whose two paths - migrate then compute, or compute then migrate - can be compared precisely.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/rag/vector/exact.go`
- `pkg/rag/vector/sqliteexact`
- `pkg/rag/lexical`
- `pkg/rag/lexical/bleve`
- `pkg/rag/knowledge/repository.go`
- `pkg/rag/knowledge/sqlite.go`
- `pkg/rag/indexbundle`
- `pkg/flow/store.go`
- `pkg/experiment`
- `pkg/rag/representations`

### Why this project exists

- rag-ttc uses in-memory and persistent implementations across vector search, lexical search, knowledge storage, caches, and artifacts. Replacing a backend should not silently change semantic results beyond an explicitly documented approximation contract.
- Initial-algebra/fold language from the handbook has a practical interpretation: if every backend preserves the primitive constructors and observations, whole programs composed from them should agree.
- Schema migration is a second composition test. Migrating source data before computation should agree with migrating computed semantic state when the migration preserves every rule-relevant field.
- This project turns those ideas into a reusable conformance kit and reveals where current interfaces conflate semantics with backend-specific details.

### Source-level observations to verify

- Inspect exact vector and SQLite exact vector packages for shared score/order contracts and backend-specific behavior.
- Compare lexical interfaces with Bleve implementation, especially score interpretation and deterministic ties.
- `knowledge.Repository` plus SQLite implementation is a typed domain backend suitable for round-trip and migration study.
- `indexbundle` identities/manifests provide an artifact-level schema/version precedent.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. What is the minimal backend interface for facts/derivations, vector/lexical observations, or knowledge records that admits meaningful conformance tests?
2. Which aspects of retrieval are exact semantics and which are backend-specific approximation, scoring, or ordering contracts?
3. Can conformance be reduced to constructor/local-operation tests plus a small set of end-to-end generated programs?
4. What migration metadata and versioning are required to avoid silent interpretation of old payloads under new rules?
5. Under what conditions does `Migrate(Close_old(x)) = Close_new(Migrate(x))` hold?
6. How should lossy migrations be represented and evaluated when exact commutation is impossible?

### Falsifiable hypotheses

1. A neutral typed conformance suite can test in-memory, JSON/file, and SQLite backends against one semantic reference model.
2. Exact backends will agree on canonical facts and deterministic views; approximate retrieval backends require a weaker declared contract focused on admissible observations and stable tie behavior.
3. Constructor-level preservation plus merge/round-trip laws catches most backend drift before end-to-end testing.
4. A migration that drops a rule-relevant field will fail the commutation test on a generated counterexample.
5. Versioned envelopes and explicit lossy-migration reports are sufficient to evolve fact/provenance schemas without global rewrites.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Define backend capability and conformance levels: exact state, ordered exact query, approximate candidate, and artifact store.
- Implement three small semantic-state backends: in-memory, canonical JSON/files, and SQLite.
- Adapt at least one existing rag-ttc backend pair, such as exact vector implementations or knowledge repository forms.
- Build constructor, merge, query, round-trip, crash, and migration conformance tests.
- Define v1 and v2 schemas with one semantics-preserving migration and one intentionally lossy migration.
- Run migrate-before/after-computation experiments on finite rule fixtures.

### Explicit non-goals

- Benchmarking or choosing a production database vendor.
- Pretending approximate ANN retrieval is extensionally equal to exact search.
- Automatic arbitrary schema evolution.
- A generic object-relational mapper.
- Changing all existing backend interfaces in the first pass.

## System to build

1. A neutral backend interface and capability declaration with exact semantic expectations.
2. In-memory, file/JSON, and SQLite reference implementations for facts and derivations.
3. A conformance harness that runs constructor, merge, serialization, query, transaction/crash, and ordering tests.
4. Adapters for one current rag-ttc backend family and a report of semantic versus implementation-specific fields.
5. A schema migration framework with versioned readers/writers, preservation reports, and commutation tests.
6. A corpus of backend and migration counterexamples including ordering, float, null, unknown-field, and crash cases.

### Proposed API sketch

```go
package backend

type Capability string
const (
    ExactState Capability = "exact_state"
    ExactOrderedQuery Capability = "exact_ordered_query"
    ApproximateCandidates Capability = "approximate_candidates"
    AtomicSnapshot Capability = "atomic_snapshot"
)

type Store interface {
    Capabilities() []Capability
    PutFact(context.Context, Fact) error
    PutDerivation(context.Context, Derivation) error
    GetFact(context.Context, FactID) (Fact, bool, error)
    Snapshot(context.Context) (State, error)
    Close() error
}

type Migration interface {
    ID() string
    FromSchema() string
    ToSchema() string
    MigrateFact(Fact) (Fact, PreservationReport, error)
    MigrateDerivation(Derivation) (Derivation, PreservationReport, error)
}

func CheckStore(factory func() Store, suite Suite) ConformanceReport
func CheckCommutation(seed State, oldRules, newRules []Rule, m Migration) CommutationReport
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Round-trip | Writing then reading preserves canonical values. | All fact/derivation schemas and edge values. |
| Backend state equivalence | Equal operation sequences produce equal snapshots on exact backends. | Generated operation programs. |
| Merge preservation | Persisting joined states equals joining persisted snapshots. | Binary/ternary state fixtures. |
| Ordering contract | Exact ordered queries use the declared total tie-break. | Tie and insertion-order tests. |
| Crash atomicity | Capabilities accurately state whether partial writes can be observed. | Injected crash/transaction boundary tests. |
| Version safety | Readers do not silently interpret unknown schemas as current. | Unknown/newer schema fixtures. |
| Migration commutation | Semantics-preserving migration agrees before and after rule computation. | Finite closure comparison. |
| Loss honesty | Lossy migration identifies every dropped/approximated field and affected rule. | Intentionally lossy migration fixtures. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: Three-backend operation program

**Setup.** Generate facts, alternative derivations, duplicates, conflicts, deletes/tombstones if supported, and snapshots.

**Procedure.** Run identical operation sequences against memory, files, and SQLite with varied insertion order and restarts.

**Expected observations.** Exact snapshots and diagnostics agree under declared capabilities.

**Failure interpretation.** A backend leaks storage order, overwrites alternatives, or mishandles canonical values.
### Scenario 2: Existing retrieval backend pair

**Setup.** Use a tiny corpus and deterministic embeddings or lexical tokens across an in-memory/reference and current persistent backend.

**Procedure.** Compare candidate membership, exact scores where promised, ordering, tie breaks, and error behavior.

**Expected observations.** Agreement matches the capability contract; any approximation is explicit and measured.

**Failure interpretation.** Backend-specific behavior is presented as common semantics.
### Scenario 3: Semantics-preserving migration

**Setup.** Migrate a v1 fact schema into v2 by splitting a field or adding normalized metadata while retaining all rule inputs.

**Procedure.** Compute old closure then migrate, and migrate seed/rules then compute new closure.

**Expected observations.** Canonical migrated states agree after normalization.

**Failure interpretation.** The migration or new rule interpretation fails to preserve a constructor.
### Scenario 4: Lossy migration counterexample

**Setup.** Drop timestamps, qualifiers, source spans, or another field used by a guard/rule.

**Procedure.** Generate a seed where that field changes derivability and run commutation.

**Expected observations.** The test fails with a preservation report naming the field and affected rule.

**Failure interpretation.** The framework labels the migration preserving despite divergent semantics.


### Metrics

- Conformance cases passed by capability and backend.
- Semantic snapshot/query disagreements and minimal counterexamples.
- Round-trip and migration data-loss counts.
- Crash recovery and atomicity outcomes.
- Storage size, throughput, and latency as secondary trade-offs.
- Commutation agreement across generated finite rule programs.
- Number of backend-specific fields removed from common interfaces.

### Fault injection

- Random insertion and iteration order.
- Process restart, partial file write, and transaction rollback.
- Unknown schema, missing field, extra field, null, and numeric edge values.
- Duplicate IDs with equal and conflicting payloads.
- Equal retrieval scores and approximation misses.
- Migration interrupted midway.
- Rule-relevant field intentionally dropped.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - capability model | Backend semantics and exact/approximate conformance levels specified. |
| M2 - reference stores | Memory, file, and SQLite implementations pass core laws. |
| M3 - current adapter | One rag-ttc backend family assessed against the suite. |
| M4 - migration framework | Versioned preserving/lossy migrations and reports implemented. |
| M5 - commutation study | Generated before/after computation tests and counterexamples complete. |
| M6 - hand-off | Conformance kit, schemas, fixtures, and backend guidance published. |

## Acceptance gates

- All exact reference backends produce equal canonical snapshots over generated programs.
- Capabilities accurately predict the tested query and crash behavior.
- Unknown schema versions are rejected or explicitly migrated.
- The preserving migration commutes on all finite fixtures.
- The intentionally lossy migration is detected by a minimal counterexample.
- One existing rag-ttc backend family is classified with concrete conformance results.
- Approximate retrieval differences are documented rather than hidden under equality.
- The report states which local constructor checks are sufficient and where end-to-end tests remain necessary.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- P01/P02 canonical IDs, facts, and derivations or neutral compatible schemas.
- P03 merge laws and P05 finite closure programs, or local reference versions.
- Existing rag-ttc backend fixtures and index/knowledge snapshots.

### Outputs offered to later projects

- `backend-capabilities/v1`, `conformance-report/v1`, `migration/v1`, and `preservation-report/v1` schemas.
- Reusable backend law suite and generated operation programs.
- v1/v2 migration fixtures for P10 replay and the composition pass.
- Backend equivalence and approximation guidance.

### Expected composition experiments

- Persist P02/P03 states in each backend and verify provenance after round-trip.
- Run P05 closure using different state stores and compare semantic outputs.
- Migrate P10 sealed bundles and verify old/new replay semantics.
- Use P11 snapshots as backend migration sources and targets.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| One interface hides important capability differences | Declare capabilities and separate exact from approximate contracts. |
| SQL/file implementation dominates project | Keep reference schemas small and prioritize semantic tests over tuning. |
| Commutation claim too broad | State the finite rule/migration assumptions and provide counterexamples outside them. |
| Float/order portability | Canonicalize comparison and specify tie/precision behavior explicitly. |
| Migration framework scope creep | Implement two concrete versions and a preservation report, not a universal language. |

## Questions the final report must answer

1. What semantic capabilities can backends honestly claim?
2. Which local operations were sufficient to predict whole-program agreement?
3. Where did storage order or transaction behavior leak into results?
4. What made the preserving migration commute?
5. What was the smallest lossy-migration counterexample?
6. How should approximate retrieval backends be compared?
7. Which rag-ttc interfaces should expose capabilities or versioning more explicitly?

## Stretch investigations

- A remote service backend with network fault injection.
- Cross-language backend implementation against the same neutral conformance suite.
- Automatic migration dependency report from rule field access.
- Query-plan equivalence for recursive closure over SQL versus in-memory evaluation.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/backend-conformance-schema-migration` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, sections 8.4, 8.7, 9.14-9.16, and migration guidance.
- Database conformance and transaction semantics references relevant to SQLite/file stores.
- Category-theoretic initial algebra/fold and Kan extension intuition from the handbook, translated into constructor preservation and migration commutation.
- QuickCheck for generated operation programs and model-based state-machine testing.
- Exact versus approximate nearest-neighbor evaluation literature for capability distinctions.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# P13 - Security Labels, Authorization, and Noninterference

## Assignment summary

**Project code:** P13  
**Track:** Cross-cutting semantics: security  
**Suggested duration:** 6-8 weeks  
**Suggested team:** 2 students  
**Program priority:** Medium-high

Attach explicit access requirements to source and derived evidence, propagate them through derivations, and test whether an unauthorized user can learn from restricted data through retrieval, ranking, generation, caches, traces, or error behavior. Produce a small, auditable security contract rather than a generic policy framework.

The assignment is intentionally bounded. The goal is not to redesign all of rag-ttc. The goal is to isolate one semantic question, build a clear reference model, attack it with counterexamples, and publish a contract that can later be composed with the other projects.

## Repository context

### Relevant code paths

- `pkg/rag/types.go`
- `pkg/rag/answering`
- `pkg/rag/knowledge`
- `pkg/rag/connected`
- `pkg/rag/toolanswer`
- `pkg/ttcrag`
- `pkg/flow/store.go`
- `pkg/execution/cache.go`
- `pkg/experiment`
- `pkg/app/session`
- `pkg/app/chat`

### Why this project exists

- RAG can leak restricted information through derived summaries or answers even when the original chunk is not shown. Access control must propagate through derivations, not only be checked at final source hydration.
- Caching, shared indexes, tool observations, traces, and error messages can cross authorization scopes unless scope is part of identity and every projection is filtered consistently.
- The fact/provenance model gives a direct security rule: a derived item must require at least the access level of every source dependency used by its derivation.
- A finite noninterference test can compare two worlds differing only in restricted facts and verify that a low-authority observer sees equal allowed outputs and traces under a stated policy.

### Source-level observations to verify

- Core `Document`/`Chunk` metadata can carry source access context, but derived facts and observations need explicit propagated requirements.
- Cache wrappers and generation/retrieval identity should be audited for authorization-scope inclusion or namespace partitioning.
- `pkg/rag/connected` and tool paths combine multiple sources and are high-value mixed-scope test targets.
- `pkg/experiment` and `pkg/app/session` can leak restricted content through durable traces even when final answer display is filtered.

The supplied handbook is a starting hypothesis, not an oracle. Confirm each relevant claim against the repository snapshot and record exact file and line references in the final report.

## Research framing

### Research questions

1. What label lattice or access predicate is sufficient for rag-ttc’s likely public/internal/confidential/tenant use cases?
2. Should labels attach to facts, derivations, observations, views, requests, or all of these?
3. How are output requirements computed when a fact has multiple derivations with different access labels?
4. Where must authorization be enforced: index construction, candidate retrieval, admission, merge, view, generation, cache read/write, trace, and artifact export?
5. What noninterference property is realistic for deterministic recorded fixtures, and what side channels are explicitly out of scope?
6. Can selective disclosure preserve enough provenance to verify an answer without revealing restricted source content?

### Falsifiable hypotheses

1. A small finite label lattice plus derivation-aware propagation can prevent direct and derived evidence disclosure in the studied pipelines.
2. For facts with alternative derivations, the minimum required authority can be the least restrictive valid derivation available to the user, provided the chosen derivation is recorded.
3. Authorization scope must participate in cache identity or cache partitioning for retrieval, views, and generated answers.
4. A low-view projection applied before ranking/generation yields stronger and easier-to-test noninterference than filtering citations only at the end.
5. At least one current trace, cache, or error path will require additional filtering or scope identity even if source hydration is access-controlled.

A hypothesis counts as falsified when the team supplies a minimal reproducible counterexample. Counterexamples are first-class results and must be added to the neutral fixture pack.

## Scope

### In scope

- Define a small access-label model, principal capabilities, tenant/domain context, and label join/order.
- Attach labels to source facts and compute derivation requirements, including alternative derivations.
- Implement authorized projection of fact states, candidate observations, selected views, traces, and proof bundles.
- Create scope-aware cache-key/partition tests and cross-user replay attacks.
- Adapt one baseline answering path and one tool/connected path using synthetic public/confidential fixtures.
- Implement finite two-world noninterference tests and document timing/provider side-channel limits.

### Explicit non-goals

- Designing an enterprise-wide identity provider or policy administration system.
- Eliminating all timing, model-memorization, or traffic-analysis side channels.
- Using cryptography to hide data from the executing process.
- Treating model instructions as an access-control boundary.
- Retrofitting every UI and command in the first pass.

## System to build

1. A standalone label lattice/predicate model with principal contexts and deterministic authorization checks.
2. Derivation-aware label calculation and an explanation of which source/derivation requires the effective label.
3. Projection functions for state, selected view, trace, citation bundle, and cache namespace.
4. A two-world test harness comparing low-observable outputs when high-only facts vary.
5. Adapters for one answer pipeline and one tool or connected pipeline.
6. An attack corpus covering shared cache, restricted inference, count/score leakage, error leakage, and provenance disclosure.

### Proposed API sketch

```go
package secureevidence

type Label string
type Principal struct {
    ID       string
    Tenant   string
    Grants   []Label
}

type Policy interface {
    ID() string
    Dominates(principal Principal, label Label) bool
    Join(labels ...Label) Label
}

type LabeledFact struct {
    Fact  Fact
    Label Label
}

type LabeledDerivation struct {
    Derivation Derivation
    Required   Label
}

type ProjectionReport struct {
    IncludedFacts  []FactID
    ExcludedFacts  []FactID
    RedactedTraces []string
    Reasons        []Reason
}

func DerivationRequirement(d Derivation, inputs map[FactID]Label, p Policy) Label
func EffectiveFactAccess(id FactID, state State, p Policy) AccessExplanation
func Project(principal Principal, state State, p Policy) (State, ProjectionReport)
func CheckNoninterference(low Principal, publicWorld, secretWorld Scenario, observe Observer) Report
```

The API sketch is intentionally small. The team may change names and representation choices, but must retain a comparable boundary and explain all semantic differences.

## Required laws and tests

| Law or invariant | Programmer reading | Required evidence |
| --- | --- | --- |
| Source authorization | A projected state contains only facts accessible through an allowed source/derivation. | Public/confidential fixture and verifier. |
| Derivation propagation | A derivation requirement is at least as restrictive as every dependency it uses. | Generated dependency DAG tests. |
| Alternative derivation minimum | A fact may be exposed through an allowed derivation without revealing a restricted alternative. | Dual-support fixture and explanation check. |
| Projection idempotence | Projecting an already projected state for the same principal changes nothing. | Repeated projection tests. |
| Projection monotonicity in authority | A more authorized principal sees a superset of semantic facts. | Principal-order generated tests. |
| Cache isolation | Users with different effective scopes cannot receive each other’s restricted cached output. | Cross-principal cache attack fixtures. |
| Low noninterference | Changing high-only inputs does not change declared low-observable semantic outputs. | Two-world finite scenario comparisons. |
| Trace/artifact hygiene | Restricted payloads and identifiers do not appear in low traces or bundles unless allowed. | Recursive content scan and structured projection tests. |

The law suite must test both the standalone model and the rag-ttc adapter. For randomized tests, persist the seed and shrink any failure to a stable JSON fixture.

## Experimental plan

### Scenario 1: Derived confidential summary

**Setup.** A public fact and confidential fact are combined into a derived summary; another public-only derivation may or may not exist.

**Procedure.** Project for public and confidential principals and inspect effective access explanations.

**Expected observations.** The mixed derivation is confidential. The fact is public only if an independent valid public derivation supports the exact canonical fact.

**Failure interpretation.** A public user sees content supported only by confidential input or the system over-restricts a public alternative without explanation.
### Scenario 2: Cross-user cache attack

**Setup.** A privileged user populates retrieval/view/generation caches; an unprivileged user submits the same text query.

**Procedure.** Test keys with omitted scope, tenant-only scope, full effective scope, and separate cache namespaces.

**Expected observations.** No restricted candidate, context, answer, or trace is returned to the low user; the correct design has explicit scope identity.

**Failure interpretation.** Any cross-scope hit leaks semantic output or restricted metadata.
### Scenario 3: Two-world noninterference

**Setup.** Construct two repository worlds identical in public facts but different in confidential facts, scores, and graph edges.

**Procedure.** Run authorized candidate production, ranking, answer generation from recorded outputs, errors, and trace projection for a public principal.

**Expected observations.** Declared low-observable outputs are equal; privileged outputs may differ.

**Failure interpretation.** Candidate counts, ranks, labels, answer text, errors, or traces reveal high-only changes.
### Scenario 4: Tool and provenance disclosure

**Setup.** A tool returns mixed-tenant results and a proof bundle includes dependencies/IDs from both tenants.

**Procedure.** Apply admission checks, selected view projection, citation validation, and bundle export.

**Expected observations.** Only authorized facts/derivations and sanitized trace fields remain, with honest redaction markers.

**Failure interpretation.** Restricted source IDs, snippets, request parameters, or existence signals survive export.


### Metrics

- Unauthorized fact/view/answer disclosure count over attack corpus.
- False denial count where an allowed alternative derivation exists.
- Two-world low-output disagreement count by stage.
- Cache cross-scope hit attempts and prevented leaks.
- Trace/artifact restricted-token scan results.
- Projection and label-propagation overhead.
- Percentage of outputs with human-readable access explanation.

### Fault injection

- Missing, malformed, and unknown labels.
- Mixed-tenant derivations and alternative supports.
- Cache key with omitted or stale scope.
- Restricted facts affecting scores/counts but filtered before output.
- Error messages containing source IDs or query fragments.
- Tool result mislabeled by provider or adapter.
- Redacted proof bundle with dangling dependencies.

Experiments should separate semantic disagreement from operational variance. Timing and allocation data are useful, but they do not substitute for checking output equivalence and invariant preservation.

## Work plan

| Milestone | Exit condition |
| --- | --- |
| M1 - threat and label model | Principals, labels, observables, trusted boundaries, and out-of-scope channels defined. |
| M2 - propagation/projection | Standalone state and derivation security laws pass. |
| M3 - cache/trace tests | Cross-scope cache and artifact leakage suite complete. |
| M4 - pipeline adapters | One answer and one tool/connected path enforce projection at declared boundaries. |
| M5 - noninterference study | Two-world scenarios and false-denial analysis complete. |
| M6 - hand-off | Security schemas, attack corpus, verifier, and adoption recommendations published. |

## Acceptance gates

- Every exposed derived fact has an allowed supporting derivation for the principal.
- Alternative public support is preserved without revealing restricted alternatives.
- Projection is idempotent and monotone with increasing authority on generated fixtures.
- No cross-scope cache attack in the shared corpus leaks restricted semantic output.
- The declared low-observable outputs are equal in all required two-world fixtures.
- Low traces and bundles contain no restricted fixture tokens or IDs.
- Adapters enforce authorization before ranking/generation, not only at citation display.
- The report states residual timing/model/provider side channels without overclaiming full security.

A project is not accepted solely because the code compiles. It must include at least one adversarial scenario, one generated-law test, and one result that could have falsified the preferred design.

## Composition contract

### Inputs accepted from later projects

- P02 fact/derivation state and P03 merge, or compatible neutral fixtures.
- P04 views and P09 turn bundles for projection experiments.
- P01 scope-aware identity/cache contracts.

### Outputs offered to later projects

- `security-label/v1`, `principal/v1`, `projection-report/v1`, and `noninterference-report/v1` schemas.
- Public/confidential and multi-tenant attack fixtures.
- Label propagation and projection library.
- Security checklist for composition and experiment bundles.

### Expected composition experiments

- Project P08 connected candidates before P04 ranking and compare with post-ranking filtering counterexamples.
- Run P09 tool turns with mixed-scope observations and validate selected citations.
- Use P10 selective bundle export and verify provenance remains honest after redaction.
- Apply P11 source/authorization changes and distinguish data retraction from policy projection.

No implementation dependency is required in the first pass. The contract is the hand-off. In the second pass, adapters may be replaced by another team's implementation and the same conformance suite rerun.

## Risks and likely traps

| Risk | Mitigation or diagnostic |
| --- | --- |
| Overclaiming noninterference | Define exact observables, finite fixtures, deterministic recorded effects, and residual channels. |
| Label granularity explosion | Start with a small lattice/predicate and explicit tenant context. |
| Alternative derivation ambiguity | Expose which derivation justifies access and avoid merging payloads that are only approximately equivalent. |
| Filtering too late | Test pre-ranking/pre-generation projection against post-hoc citation filtering. |
| Security metadata leaks | Project traces, counts, errors, IDs, and manifests, not only text payloads. |

## Questions the final report must answer

1. What threat model and low-observable boundary were tested?
2. Where are labels attached and how are derivation requirements calculated?
3. How are alternative derivations handled?
4. Which cache/trace/artifact paths were vulnerable or safe?
5. What is the earliest reliable authorization boundary in each pipeline?
6. Which two-world differences remained observable and why?
7. What minimal changes should rag-ttc adopt before multi-tenant use?

## Stretch investigations

- Selective-disclosure cryptographic commitments for proof bundles.
- Declassification rules with explicit authority and audit records.
- Quantitative side-channel tests for candidate counts and timing.
- Policy-as-data adapters for an external authorization engine while retaining the semantic contract.


## Common research protocol

This project is one independent unit in the rag-ttc semantic research program. It must be executable and assessable without importing another student's branch.

The team must produce two implementations:

1. **Standalone semantic model.** A deliberately small Go package, command, or test harness that demonstrates the proposed semantics without depending on the rest of rag-ttc. This implementation is the executable specification.
2. **rag-ttc adapter.** A narrow adapter against the supplied repository snapshot. It may live under `research/security-labels-noninterference` or in a separate module using `replace` to point at the snapshot. It must minimize changes to production packages during the first pass.

Use the shared fixture IDs and interchange formats in `../fixtures/` and `../schemas/`. Do not depend on another project team's implementation. Where a neighboring concept is needed, implement the smallest local fake that satisfies the published JSON contract.

Every result must distinguish:

- **semantic output:** facts, derivations, selected view, or other domain result;
- **operational trace:** retries, cache hits, worker order, timing, and failures;
- **experimental assessment:** metrics, counterexamples, and interpretation.

The team may revise the proposed API. Any revision must preserve the stated laws or document a counterexample showing why a law is inappropriate.



## Required hand-off package

Submit a single directory containing:

- `README.md` with build and experiment commands;
- `design.md` with the final semantics and rejected alternatives;
- `api.go` or equivalent public interface;
- standalone implementation and rag-ttc adapter;
- deterministic unit tests and property-based or generated tests;
- `fixtures/` containing every new counterexample in neutral JSON form;
- `results.json` conforming to `../schemas/project-result.schema.json`;
- `report.md` with methods, results, limitations, and recommendations;
- `demo.sh` that runs the primary scenarios without network access where possible;
- a commit or patch that can be inspected independently.

The final report must clearly label statements as one of: **proved from the model**, **verified by exhaustive finite testing**, **supported empirically**, or **still conjectural**.



## Tiny mathematical background

The project uses laws in the same way an API uses invariants:

- A **semantic identity** says when two values must be interchangeable to all relevant consumers.
- A **monotone** operation can add information but cannot make previously admitted information disappear.
- An **idempotent** operation has no additional effect when repeated.
- A **join** is a deterministic merge of compatible states. For the intended add-only states, merge should be associative, commutative, and idempotent.
- A **fixed point** is a state for which one more application of the rules adds nothing.
- An **induction proof** checks a base state and then checks that every allowed transition preserves the invariant. For an implementation, this normally becomes a constructor-level proof plus generated tests.

No advanced mathematical notation is required in the implementation. Use equations only where they make an API law more precise.


## Selected readings

- rag-ttc Semantic Architecture Handbook, section 9.16 and cache/provenance/package adaptation guidance.
- Security Policies and Security Models, Goguen and Meseguer, for noninterference foundations.
- Information-flow control references on security lattices and label propagation.
- W3C PROV-DM for dependency-aware access explanations.
- OWASP guidance on authorization, cache isolation, and sensitive logging as implementation checklists.

## Definition of done

The project is done when an independent reviewer can run the demonstration, inspect a compact set of laws, reproduce the main counterexample and positive cases, and decide whether the proposed semantic contract should be adopted by rag-ttc. The reviewer must not need to infer the meaning of the API from implementation details.


\newpage

# Part III - Composition pass playbook

## Purpose

The first-pass projects intentionally avoid shared implementation dependencies. The second pass asks a different question: do the independently refined contracts compose into a coherent RAG system, and where do local guarantees fail at subsystem boundaries?

Composition is not a mass merge of all student branches. It is a sequence of controlled replacement experiments. At each step, one local fake is replaced by another team’s implementation while the same neutral fixtures, conformance laws, and sealed artifacts are rerun.

## Entry criteria

A project is eligible for composition when it provides:

- a versioned public contract and neutral schemas;
- a standalone implementation with deterministic test mode;
- a rag-ttc adapter or compatibility fixture;
- `results.json` and a sealed artifact bundle;
- at least one counterexample and one intentionally bad implementation/test double;
- a clear equality/comparison function for its semantic output;
- no hidden dependency on another student branch.

Projects that do not meet the criteria can still participate through their fixture contracts, but their code is not placed on the critical integration path.

## Integration principles

1. **Replace one boundary at a time.** Preserve a known-good oracle or fixture at every step.
2. **Compare semantics and traces separately.** A faster or differently scheduled run may be semantically equal.
3. **Keep candidates and views separate.** Do not use top-k equality as evidence that candidate states agree.
4. **Preserve alternative derivations.** Do not collapse provenance merely to make two implementations look equal.
5. **Make partial failure explicit.** Empty, unavailable, failed, skipped, and cancelled are distinct.
6. **Version all contracts.** A migration is an experiment, not a silent compatibility assumption.
7. **Use recorded effects first.** Only after deterministic composition passes should live providers be introduced.
8. **Treat security projection as a boundary, not a final filter.** Run both secure and intentionally insecure orderings.

## Core composition ports

| Port | Producer | Consumer | Comparison |
|---|---|---|---|
| Semantic fingerprint | P01 | all projects | exact string/version equality and sensitivity report |
| Fact/provenance state | P02 | P03, P05, P09, P10, P11, P12, P13 | canonical state equality plus verifier |
| Join/delta state | P03 | P05, P08, P09, P11 | ACI laws and canonical serialization |
| Candidate/view boundary | P04 | P07, P08, P09, P13 | candidate hash unchanged; deterministic view equality |
| Rule/closure operations | P05 | P06, P07, P11 | closure state and certificate equality |
| Captured effect/trace | P06 | P05, P08, P09, P10 | semantic request ID and replay outcome |
| Knowledge candidate graph | P07 | P05, P08 | graph equality and support-path verification |
| Connected channel result | P08 | P09, P10, P13 | channel status/candidate/view/provenance comparison |
| Turn bundle/citation report | P09 | P10, P13 | verifier and citation-level outcomes |
| Run bundle | P10 | all integrated scenarios | seal/verify/replay/diff |
| Change/snapshot | P11 | P05, P07, P08, P10, P13 | incremental versus rebuild equality |
| Backend/migration | P12 | P02, P05, P10, P11 | conformance and commutation reports |
| Authorized projection | P13 | P04, P08, P09, P10 | noninterference and no-leak checks |

## Recommended integration order

### Stage A - identity and artifact custody

Integrate P01 with P10 first.

- Replace P10 local fingerprint fake with P01.
- Seal one result from each project.
- Verify that identity versions, source snapshot hashes, and no-secret rules are consistently represented.
- Introduce one deliberate identity version change and test rejection/migration.

**Gate A:** Every project output can be sealed and verified; semantic IDs are unambiguous and versioned.

### Stage B - facts, merge, and storage

Integrate P02, P03, and P12.

- Store the P02 diamond provenance state in all P12 exact backends.
- Join independently produced states through P03 before and after persistence.
- Verify facts, alternative derivations, conflicts, and canonical serialization.
- Migrate v1 to v2 and run the P02 verifier on both paths.

**Gate B:** Exact backends preserve one fact/provenance semantics; merge and migration laws pass.

### Stage C - candidates, views, and execution

Integrate P03, P04, and P06.

- Produce candidate deltas through P06 sequential, cached, retried, batched, and parallel execution.
- Join them through P03.
- Apply P04 ranking/packing after an explicit barrier.
- Compare semantic candidates, selected views, and traces separately.

**Gate C:** Operational policy changes do not alter candidate state or fixed-policy views under declared preconditions.

### Stage D - recursive knowledge and connected retrieval

Integrate P05, P07, and P08, using P03/P04/P06 underneath.

- Expose P07 discovery operations as P05 rules.
- Evaluate fixed depth and saturation over the multi-hop fixture.
- Combine baseline and knowledge channel candidates in P08.
- Apply P04 views and retain knowledge paths/provenance.
- Compare current-compatible and lossless diagnostic policies.

**Gate D:** Multi-hop candidate closure, connected composition, and final views have distinct, reproducible contracts.

### Stage E - tool controller and citations

Integrate P09 with P06 and P08.

- Make connected retrieval one recorded tool.
- Run completion permutations and retry/failure scenarios.
- Select and label through the shared view layer.
- Verify citation levels against the integrated fact/provenance bundle.

**Gate E:** Tool scheduling changes only trace; selected evidence and citation resolution are deterministic under fixed policy.

### Stage F - updates and security

Integrate P11 and P13 across the assembled stack.

- Apply source additions and retractions to recursive knowledge/connected candidates.
- Compare incremental and full rebuild.
- Project authorized state before views and generation.
- Test cross-user cache, tool, trace, and artifact boundaries.
- Seal every snapshot and security report through P10.

**Gate F:** Updates preserve semantic laws, and restricted input changes do not alter declared low-authority observations.

## Integrated scenarios

### S1 - Deterministic one-shot hybrid RAG

**Goal:** Validate the simplest full path before recursion or tools.

**Components:** P01 -> P06 -> baseline lexical/vector producers -> P03 -> P04 -> recorded generator -> P10.

**Fixture:** A small corpus with overlapping lexical/vector hits and ranking ties.

**Experiments:**

- sequential versus parallel channels;
- cache miss versus hit;
- transient retry;
- input and completion permutations;
- two ranking policies over one candidate snapshot;
- backend swap for an exact vector fixture.

**Required invariants:**

- one candidate fact state across operational variants;
- one selected view per policy;
- alternative channel observations retained;
- sealed replay produces the same semantic result;
- no step display-name collision in traces.

**User exploration:** Show the candidate set, fused view, packed context, and final citations separately. Ask users to identify whether an intentionally removed relevant item was lost in retrieval, ranking, or packing.

### S2 - Recursive knowledge RAG

**Goal:** Test multi-hop completeness and the separation of discovery from selection.

**Components:** P02/P03 -> P05 -> P07 -> P08 -> P04 -> P10.

**Fixture:** `multihop-graph-v1` plus an ambiguous alias and a cycle.

**Experiments:**

- depth 1, 2, 3, and saturation;
- round versus frontier versus parallel schedule;
- compatibility versus lossless knowledge selection;
- gate open/closed boundary;
- addition of one new alias/fact path.

**Required invariants:**

- closure state agrees across fair evaluators;
- partial certificate accurately states complete rank;
- candidate discovery retains ambiguity;
- selection changes do not alter closure;
- incremental addition agrees with full rebuild.

**User exploration:** Present path/provenance explanations and let users compare a concise selected view with the full candidate graph. Record whether explanations help locate missing evidence.

### S3 - Tool-using answer

**Goal:** Validate turn semantics, deterministic citation labels, and explicit citation guarantees.

**Components:** P06 -> P09 with P08 as one tool -> P03/P04 -> recorded generator -> P10.

**Fixture:** `completion-permutations-v1` plus malformed citation claims.

**Experiments:**

- every tool completion order;
- timeout after effect and retry;
- duplicate observation;
- conflicting observation;
- evidence budget at exact boundary;
- citation validation ladder.

**Required invariants:**

- one candidate state and selected label map;
- duplicate transparency;
- explicit conflicts and channel failures;
- valid labels resolve uniquely;
- quote-support checks do not overclaim entailment.

**User exploration:** Ask users to distinguish “citation exists,” “source text matches,” and “claim is supported.” Measure whether the layered report calibrates trust better than a binary citation-valid flag.

### S4 - Live corpus update

**Goal:** Validate append-only incremental closure and exact retraction semantics.

**Components:** P11 -> P05/P07/P08 -> P04 -> P10/P12.

**Fixture:** `update-sequences-v1` and `diamond-provenance-v1`.

**Experiments:**

- add new source and alternative support;
- duplicate update delivery;
- retract one support, then all supports;
- supersede a document revision;
- change only top-k policy;
- crash/resume during update;
- migrate snapshot schema.

**Required invariants:**

- additions equal full rebuild;
- alternative support prevents premature retraction;
- policy-only change reuses canonical state;
- resume equals uninterrupted processing;
- every snapshot seals and verifies.

**User exploration:** Provide a timeline showing why a fact appeared or disappeared. Ask users whether the explanation supports debugging and audit decisions.

### S5 - Multi-tenant secure RAG

**Goal:** Test authorization propagation and low-observable noninterference across the full stack.

**Components:** P13 around P08/P09/P04/P10, with scope-aware P01/P06 caches.

**Fixture:** `public-confidential-v1` plus mixed-tenant tool results.

**Experiments:**

- privileged cache warm-up followed by public query;
- public and confidential derivations of the same fact;
- filtering before versus after ranking;
- secret-world A versus secret-world B;
- trace and sealed-bundle export;
- authorization policy change without source deletion.

**Required invariants:**

- public user receives only facts with an allowed derivation;
- no cross-scope cache leakage;
- low-observable outputs agree across secret worlds;
- restricted IDs/text do not appear in traces or bundles;
- policy projection is distinct from source retraction.

**User exploration:** Test whether access explanations are understandable and whether redacted proof bundles remain useful without leaking existence or identifiers.

### S6 - Backend and schema migration

**Goal:** Validate that the assembled semantics survives representation changes.

**Components:** P12 over P02/P03/P05/P10/P11.

**Fixture:** A sealed recursive retrieval snapshot with alternative derivations and selected views.

**Experiments:**

- memory -> JSON -> SQLite round trips;
- old schema closure then migrate versus migrate then new closure;
- unknown schema version;
- intentionally lossy migration;
- crash during migration;
- approximate retrieval backend under a weaker capability contract.

**Required invariants:**

- exact backends preserve canonical state and verifier success;
- preserving migration commutes;
- lossy migration is detected and explained;
- approximate backend differences are not mislabeled exact;
- replay artifacts record migration identity and preservation report.

**User exploration:** Ask maintainers to inspect a semantic diff and decide whether a migration is acceptable. Measure whether the preservation report makes the decision tractable.

## Pairwise compatibility test matrix

| Pair | Mandatory test |
|---|---|
| P01 + P02 | Codec round-trip preserves fact IDs; observation mutations do not |
| P01 + P06 | Operation identity separates semantic request from attempts |
| P01 + P10 | Mixed identity versions are rejected or migrated |
| P02 + P03 | Join preserves all valid alternative derivations |
| P02 + P12 | Every exact backend round-trip passes the verifier |
| P03 + P04 | View application leaves joined state unchanged |
| P03 + P06 | retries/duplicates yield one joined semantic state |
| P04 + P07 | ambiguity retained in candidates, resolved only by policy |
| P04 + P08 | channel fusion produces view metadata, not new source identity |
| P05 + P06 | fair operational variants reach equal closure |
| P05 + P07 | knowledge expansion rank/path matches closure certificate |
| P05 + P11 | incremental additions equal resaturation from expanded seed |
| P06 + P09 | tool retries do not duplicate evidence or shift labels |
| P06 + P10 | recorded replay preserves semantic output and trace distinctions |
| P07 + P08 | knowledge support paths survive connected fusion |
| P08 + P09 | connected tool evidence preserves channel/source provenance |
| P09 + P13 | unauthorized observations cannot enter selected citation view |
| P10 + P12 | migrated bundle verifies and replay result is compared honestly |
| P10 + P13 | selective export removes restricted data and marks redaction |
| P11 + P13 | authorization-policy changes are not confused with data deletion |

## Integrated law suite

The assembled system should attempt these properties under explicit assumptions:

```text
IdentityStable:
    Encode(Decode(fact)) has the same FactID

MergeACI:
    Join is associative, commutative, and idempotent

ClosureStable:
    Close(Close(seed)) == Close(seed)

FairSchedule:
    CloseSequential(seed) == CloseParallel(seed)

OperationalTransparency:
    Semantic(Run(policyA)) == Semantic(Run(policyB))
    // only for declared transparent policies and compliant operations

ViewPurity:
    StateHash(ApplyView(state, policy)) == StateHash(state)

Replay:
    Semantic(Replay(bundle)) == Semantic(original)

AppendIncremental:
    Close(Join(Close(seed), delta)) == Close(Join(seed, delta))

Migration:
    Migrate(CloseOld(seed)) == CloseNew(Migrate(seed))

Authorization:
    Every exposed fact has an allowed derivation

LowNoninterference:
    ObserveLow(worldA) == ObserveLow(worldB)
    // worlds differ only in high-restricted inputs
```

A failure does not automatically reject a subsystem. It may identify a missing precondition, a non-monotone policy boundary, or an approximation contract. The composition report must classify the cause.

## Conflict resolution protocol

Independent projects will make incompatible choices. Resolve them through experiments, not committee intuition.

1. State both contracts in neutral terms.
2. Identify the observable behavior on which they disagree.
3. Construct the smallest fixture that distinguishes them.
4. Run each implementation and a simple oracle if possible.
5. Assess correctness, compatibility, ergonomics, performance, and composition impact separately.
6. Select one, version both as alternatives, or define a narrower common contract.
7. Preserve the counterexample and decision record in the compendium.

Never erase a meaningful conflict by weakening equality to compare only final answer strings.

## Ablation plan

For each integrated scenario, remove or alter one semantic mechanism:

- remove identity versioning;
- merge by arrival order;
- discard alternative derivations;
- perform top-k before merge;
- omit a barrier before global ranking;
- treat failure as empty result;
- omit captured effects;
- update without dependency tracking;
- filter authorization only after generation.

The ablation must produce a measurable failure or show that the mechanism is unnecessary under narrower assumptions. Both outcomes refine the architecture.

## User-study and exploratory evaluation

The composition pass should include users because semantic elegance must support diagnosis and trust.

Suggested tasks:

- Locate whether a missing citation was lost in discovery, merge, ranking, packing, or generation.
- Explain why two runs with different traces are semantically equal.
- Decide whether a partial closure result is sufficient for a stated question.
- Compare two derivation explanations for the same fact.
- Identify why a cached answer was invalidated.
- Decide whether a schema migration is preserving or lossy.
- Interpret citation validation levels without assuming entailment.
- Understand why an item is inaccessible and which allowed derivation could expose it.

Collect completion time, correctness, confidence calibration, and qualitative confusion points. Do not use the study as a substitute for law tests.

## Composition artifacts

Each integrated scenario must produce:

- sealed run bundle;
- exact component/contract versions;
- semantic state, selected view, and operational trace as separate artifacts;
- conformance-law report;
- scenario metrics and resource report;
- minimal counterexamples for every failed law;
- semantic diff against the closest baseline;
- user-exploration notes where applicable;
- final decision record.

## Stop conditions

Stop the composition pass when:

- all six scenarios have a reproducible baseline;
- every core port has at least one successful replacement test;
- every failed law has a minimal fixture and classified cause;
- no unresolved conflict is hidden by final-output-only comparison;
- security and artifact verification gates pass for the recommended stack;
- remaining work is optimization, broader dataset validation, or optional feature expansion rather than unclear semantics.

## Final synthesis report structure

1. Adopted contracts and versions.
2. Rejected or narrowed contracts with counterexamples.
3. End-to-end semantic model.
4. Operational preconditions and failure semantics.
5. Quality/cost/reproducibility/security results.
6. Compatibility impact on current rag-ttc APIs and artifacts.
7. Minimal migration sequence for production packages.
8. Remaining scientific questions and recommended experiments.
9. User-study findings and developer ergonomics.
10. Complete conformance matrix and sealed artifact index.
