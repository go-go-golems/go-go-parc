---
title: "Semantic Foundations for Composable Retrieval-Augmented Generation"
subtitle: "Semantic Identity, Canonical Provenance, and Lawful Merge in rag-ttc - Implementation and Evaluation of Projects P01-P03"
date: "August 2026"
author: "Research artifact prepared for the rag-ttc program"
documentclass: report
classoption:
  - oneside
papersize: a4
fontsize: 10pt
geometry:
  - top=24mm
  - bottom=25mm
  - left=25mm
  - right=25mm
mainfont: "DejaVu Serif"
sansfont: "Inter"
monofont: "DejaVu Sans Mono"
colorlinks: true
linkcolor: "blue"
urlcolor: "blue"
toc: true
toc-depth: 3
lof: true
lot: true
numbersections: true
header-includes:
  - |
    \usepackage{microtype}
    \usepackage{booktabs}
    \usepackage{longtable}
    \usepackage{array}
    \usepackage{float}
    \usepackage{fvextra}
    \usepackage{enumitem}
    \usepackage{xcolor}
    \usepackage{fancyhdr}
    \floatplacement{figure}{H}
    \fvset{breaklines=true,breakanywhere=true,fontsize=\small}
    \setlength{\parindent}{0pt}
    \setlength{\parskip}{0.55em}
    \setlist{nosep,leftmargin=*}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[L]{rag-ttc semantic foundations}
    \fancyhead[R]{P01-P03}
    \fancyfoot[C]{\thepage}
---

# Abstract {-}

Retrieval-augmented generation systems are commonly assembled from components whose local APIs appear straightforward but whose composition has weak or implicit semantics. A chunk may be identified by content in one package and by serialized structure in another. A cache may omit a configuration field that changes model behavior. A concurrent evidence collector may impose a limit before all candidates have arrived, allowing completion order to alter citations. A record may combine source content, retrieval rank, score, and presentation labels in one value, even though those fields have different lifetimes and different equality rules. These defects are not primarily failures of model quality. They are failures to define what the system means by "the same request", "the same fact", "another proof of the same fact", and "the same result under a different execution schedule".

This thesis develops and implements a semantic foundation for three research projects in the `rag-ttc` codebase: P01, Semantic Identity and Cache Fingerprints; P02, Canonical Facts and Provenance; and P03, Lawful Merge and a Deterministic Evidence Ledger. The work treats the three projects as a single dependency chain. Identity determines when two records may be considered interchangeable. Provenance distinguishes stable fact content from the potentially many derivations and query-local observations associated with it. Lawful merge combines independently produced records by set union over canonical variants, yielding associative, commutative, and idempotent behavior. Deterministic selection is then performed only after global merge, under a total ordering and an explicit budget policy.

The implementation adds two standalone Go packages. `pkg/semanticid` provides a typed canonical value language, domain- and version-separated SHA-256 fingerprints, portable path handling, explicit field-role catalogs, and generic mutation-contract tests. `pkg/rag/derive` provides canonical facts, derivations, observations, a provenance-aware state, conflict-preserving join, deterministic snapshots, validation, finite proof ranks, proof bundles, a concurrent ledger facade, and deterministic post-merge selection. Adapters map existing `rag.Chunk`, `rag.Evidence`, `rag.Representation`, and `knowledge.Fact` values into the new kernel. A deterministic tool-evidence ledger demonstrates how to remove arrival-order dependence from limits and citation labels. Production identity paths were also patched to use the canonical text digest, include the connected-retrieval reciprocal-rank-fusion constant, and incorporate a fingerprint of resolved provider configuration into generation and reranking cache keys.

The algebraic laws are proved over a finite state model and tested as executable API contracts. The reference state join is proved associative, commutative, and idempotent because it is componentwise set union over complete record variants. Consequently, any fold over a fixed multiset of worker deltas has one canonical result, independent of batching, ordering, duplicate delivery, or retry. The verifier detects identity conflicts, altered record content, missing dependencies, invalid observations, and facts without a finite well-founded proof. The selection barrier is proved permutation-invariant because it validates against the merged state, removes exact duplicate candidates, applies a total deterministic ordering, chooses at most one candidate per fact, and only then assigns budgets and citation labels.

Executable evidence supports the design. The P01 mutation matrix passed for semantic, operational, presentation, and secret fields. Object field order and set delivery order were invariant; list order, semantic content, domain, and version remained distinguishing. The P02 diamond fixture produced three facts, four derivations, two observations, two independent proofs of one claim, a least proof rank of one for that claim, a verifiable proof bundle, and successful tamper detection. Across all 720 permutations of six merge deltas, the lawful state produced one output. Across all six candidate completion orders, deterministic selection produced one view, while a legacy first-arrival budget produced six views. One hundred race-enabled concurrent retry runs produced zero divergences. A scaling experiment also showed that the simple persistent `Join` reference is unsuitable for one-record-at-a-time ingestion, while a mutable ledger preserving the same semantics reduced the median cost by two to three orders of magnitude over the tested range.

The principal limitation is integration validation. The supplied repository declares Go 1.26.5 and uses a `tool` block not understood by the available Go 1.23.2 toolchain. Network access was unavailable for toolchain acquisition. The standalone semantic packages were compiled, race-tested, vetted, and exercised; every repository Go file was parsed after the patches; production call arities were statically audited. The complete repository test suite was not executed. Accordingly, this thesis distinguishes proved model properties, executed package properties, empirical measurements, static source findings, and unverified integration claims.

# Executive summary {-}

The work can be summarized as six engineering rules:

1. **Name behavior, not structs.** A semantic fingerprint is built from an explicit projection of behavior-affecting fields, encoded by declared collection and scalar semantics, and separated by domain and version.
2. **Separate facts from evidence about facts.** Stable content belongs in `Fact`; support belongs in `Derivation`; scores, ranks, retrieval methods, and request-local annotations belong in `Observation`.
3. **Merge complete variants by union.** Do not use first-writer or last-writer conflict resolution for immutable semantic records. Preserve every conflicting variant and report the conflict.
4. **Delay non-monotone decisions.** Merge candidates before applying top-k, token budgets, one-per-fact selection, or citation numbering.
5. **Prove API laws and execute them.** Identity mutation matrices, join laws, proof verification, permutation tests, retry tests, and deterministic serialization are part of the public contract.
6. **Keep operational and information semantics separate.** `flow` should continue to own caching, retries, batching, budgets, tracing, and execution. The semantic kernel defines what records mean and how their information combines.

The proposed architecture is:

![Semantic kernel embedded in the existing operational architecture.](rag-ttc-p01-p03-thesis-assets/architecture.png){width=78%}

The resulting composition boundary is:

```text
Plan -> Execute -> Admit -> Merge -> Verify -> View -> Generate
```

`Plan` and `Execute` may be effectful. `Admit` converts raw results to canonical records. `Merge` is add-only and lawful. `Verify` checks integrity and provenance closure. `View` may rank, limit, pack, and label without mutating the canonical state. `Generate` consumes that selected view.

# Status, claim types, and reproducibility {-}

This document is a doctoral-style implementation thesis and reproducibility report. It is not represented as a university-awarded degree, a peer-reviewed publication, or a proof of factual correctness for language-model output.

To prevent category errors, claims use the following evidence classes:

| Marker | Meaning |
|---|---|
| **THEOREM** | A mathematical statement proved from definitions in this document. |
| **EXECUTED** | A property exercised by compiled code in the available environment. |
| **EMPIRICAL** | A measured result from a specific experiment; not a universal performance claim. |
| **STATIC** | A conclusion from source inspection, parsing, or call-site analysis without full integration execution. |
| **CONDITIONAL** | A result that depends on assumptions stated with the claim. |

The primary reproduction command is:

```bash
cd research/p01-p03-foundations
./demo.sh
```

The standalone package validation command used for the final artifact was:

```bash
GO111MODULE=off GOPATH=/mnt/data/gopath \
  go test -race -v ./pkg/semanticid ./pkg/rag/derive
```

The final executed environment was Linux on `amd64`, with Go 1.23.2 used in GOPATH mode for the standalone packages. The full module declared Go 1.26.5. The integration-test limitation is discussed in Chapters 2, 9, and 12.

\newpage

# Introduction

## Retrieval systems need semantic contracts

A RAG system is often described as a sequence: retrieve documents, rank them, build a prompt, generate an answer. That description is operational. It says what calls are made, but it does not fully specify the meaning of their inputs and outputs. The missing semantics become visible under ordinary engineering changes:

- A worker is retried after a timeout.
- Dense and sparse retrievers return the same chunk.
- A result arrives one millisecond later under a different scheduler.
- A model setting changes while a cache entry remains addressable by the old key.
- A chunk schema gains a presentation field.
- A citation is discovered through two independent paths.
- A source document is imported from a path spelled with different separators.
- Two workers emit the same identifier with different immutable content.

If these changes alter the canonical evidence state without an explicit policy, the system does not have stable semantics. It has accidental semantics inherited from map insertion order, serializer behavior, call timing, or incomplete cache keys.

The `rag-ttc` codebase already contains several strong design decisions: narrow component interfaces, deterministic ordering in many retrieval paths, content-derived chunk lineage, explicit experiment artifacts, and a `flow` layer that centralizes operational concerns. Those strengths make the remaining gap more precise. The repository needs a small kernel for information semantics rather than a general workflow language.

## Problem statement

The thesis addresses three coupled problems.

**P01: semantic identity.** For an operation, record, or configuration, which fields determine behavioral identity? How are values encoded so that irrelevant representation choices do not change identity and relevant changes do? How are caches versioned and reviewed?

**P02: canonical facts and provenance.** How can stable information be separated from the reasons it is believed and from query-specific observations? How can one fact retain multiple proofs? How can an independent verifier detect altered content, missing dependencies, cycles without a finite proof, and malformed evidence packages?

**P03: lawful merge.** How can independently produced evidence be combined so that worker ordering, batching, retries, duplicate messages, and concurrency do not alter the canonical result? How should identity conflicts be handled without hiding them? Where should ranking, limits, and citation labels occur?

The central proposition is:

> A composable RAG evidence layer can be obtained by combining explicit semantic fingerprints, a fact/derivation/observation model, conflict-preserving set-union merge, and deterministic post-merge views. Under these contracts, execution scheduling becomes an operational choice rather than part of result meaning.

## Research questions

The implementation and evaluation answer the following questions.

**RQ1.** Can semantic cache identity be expressed as a small typed value language whose canonical encoding is deterministic and reviewable?

**RQ2.** Can mutation contracts distinguish semantic and lineage fields from operational, presentation, observation, and secret fields in an executable form?

**RQ3.** Can existing `rag-ttc` facts, chunks, representations, evidence values, and knowledge facts map into one canonical interchange model without placing ranks and scores in stable fact identity?

**RQ4.** Can one canonical fact preserve several independent derivations without duplicating the fact or discarding support?

**RQ5.** Can a verifier compute the least finite proof depth and reject malformed, conflicted, altered, missing, or circular proof structures?

**RQ6.** Can merge be made associative, commutative, and idempotent while retaining identity conflicts instead of choosing a winner?

**RQ7.** Does lawful merge eliminate output differences caused by delivery order, batching, duplicate messages, and retries?

**RQ8.** Can top-k limits and citation labels be made deterministic by moving them behind a global merge and total sort?

**RQ9.** Can these semantics be inserted into `rag-ttc` as adapters and cache-key corrections without replacing its operational `flow` abstractions?

## Contributions

The thesis contributes the following concrete artifacts.

1. A standalone `semanticid` package with a typed canonical value language, binary encoding, domain/version separation, field-role catalogs, portable paths, and mutation-contract testing.
2. A standalone `derive` package with canonical JSON, facts, derivations, observations, conflict-preserving state, lawful join, deterministic snapshots, verification, proof ranks, proof bundles, a concurrent ledger, and deterministic selection.
3. Go adapters from current `rag-ttc` domain values to the semantic kernel.
4. A deterministic tool-evidence ledger that demonstrates the merge-before-limit boundary.
5. Corrections to production identity paths for chunk fallback identity, connected retrieval, generation caching, reranking caching, and provider configuration.
6. A conformance command producing machine-readable fixtures and results.
7. Formal proofs of the core identity, merge, retry, conflict-retention, proof-rank, and deterministic-selection properties.
8. Executed law tests, adversarial fixtures, exhaustive permutation experiments, race-enabled concurrency tests, and a reference performance comparison.
9. A migration and governance model for adopting the kernel incrementally.

## Scope and non-goals

The scope is deliberately narrower than a full RAG architecture rewrite. The work does not introduce a general workflow DSL, replace `flow`, prescribe one database, define one ranking algorithm, or claim that a valid proof bundle makes a natural-language claim true. The verifier establishes structural integrity relative to declared rules and seed imports; it does not validate the external truth of a source document or the soundness of an arbitrary learned extraction rule.

The work also does not solve document deletion and retraction, authorization propagation, distributed replication across mutually distrustful nodes, cryptographic signing, model nondeterminism, or recursive closure over arbitrary rules. The design prepares for those projects by making identity, dependencies, and merge explicit.

## Thesis organization

Chapter 2 describes the repository context and research method. Chapter 3 introduces the minimal mathematics. Chapter 4 derives requirements from concrete `rag-ttc` structures. Chapters 5, 6, and 7 present P01, P02, and P03. Chapter 8 explains composition with `flow` and the broader architecture. Chapter 9 reports the experiments. Chapter 10 gives consolidated formal results. Chapter 11 provides an engineering and migration handbook. Chapter 12 discusses limitations and threats to validity. Chapter 13 concludes and defines the next research pass. Appendices document APIs, encoding, tests, changes, and reproduction steps.

# Repository context and research method

## Existing architecture

The supplied repository is a Go codebase organized around reusable RAG components and application commands. Its design includes domain packages for chunks, representations, retrieval, reranking, generation, knowledge extraction, connected retrieval, tool-assisted answering, providers, caching, and experimental evaluation. A `flow` abstraction wraps components with execution concerns such as retries, caching, budgets, batching, concurrency, tracing, and order restoration.

This separation is useful. It means the new kernel does not need to become an orchestrator. It can instead define the semantic content that operational execution transports.

The review identified a recurring shape in the current system:

```text
request/configuration -> component call -> result values -> ranking/limits -> answer
```

The proposed semantic shape inserts explicit boundaries:

```text
request/configuration
    -> semantic request identity
    -> component call
    -> admitted Fact / Derivation / Observation records
    -> lawful merge
    -> verification
    -> deterministic selected view
    -> answer
```

## Why P01-P03 form one thesis

P01 can be implemented as a hashing library, P02 as a provenance graph, and P03 as a merge helper. Doing so independently would miss their dependency structure.

A merge operation requires equality. If two workers emit records with the same semantic meaning but different serialization order, a merge based on raw bytes duplicates them. If two records share an identifier but differ in immutable content, a map assignment hides the conflict. P03 therefore depends on P01.

Provenance requires stable identities for facts, derivations, requests, rule versions, and configuration. It also requires merge to preserve alternate proofs rather than overwrite them. P02 therefore depends on both P01 and P03.

Cache correctness connects all three. A cache key is a semantic identity for an operation. A cached retrieval result may contain facts, derivations, and observations. A cache hit must be observationally equivalent to executing the operation and lawfully merging its result. Incomplete identity invalidates that equivalence.

The implementation therefore uses one shared kernel with three layers rather than three isolated prototypes.

## Research method

The work followed an artifact-centered method.

### Static source analysis

Relevant packages and call sites were inventoried. Identity and cache constructors were traced to their production callers. Domain types were inspected to classify fields by semantic lifetime. Concurrency and admission paths were inspected for order-sensitive limits and labels.

### Reference implementation

The new packages were written to depend only on the Go standard library and each other. This isolates semantic validation from external providers, databases, model SDKs, and network services.

### Adapters and production patches

Adapters map existing values into canonical records without forcing immediate repository-wide type replacement. Confirmed identity omissions were patched in their current packages. The production patches are intentionally small and versioned.

### Formalization

The state and merge model was defined mathematically as finite maps from semantic identifiers to finite sets of complete record variants. This model is simple enough to prove directly and close enough to the implementation that the proof obligations become unit and property tests.

### Executable law testing

The test suite includes:

- golden fingerprint vectors;
- object and set permutation invariance;
- list-order sensitivity;
- domain and version separation;
- field mutation matrices;
- canonical JSON equivalence and malformed-input rejection;
- fact/observation separation;
- alternate derivations;
- proof bundle verification;
- content tampering and missing dependency rejection;
- all permutations of a fixed merge workload;
- generated join-law trials;
- conflict preservation;
- concurrent duplicate delivery under the race detector;
- deterministic serialization round trips;
- all candidate completion permutations;
- total tie-breaking and one-per-fact selection.

### Adversarial experiments

The conformance command creates a diamond-shaped provenance fixture, an explicit identity conflict, a concurrent retry workload, and an arrival-order-sensitive legacy baseline. Results are written as JSON so that later projects can consume the same evidence.

### Performance experiment

Two semantically equivalent merge implementations were compared: repeated immutable `State.Join`, which clones the accumulated state for each insertion, and a mutable mutex-protected `Ledger`, which performs in-place union and returns immutable snapshots. The experiment tests implementation shape, not the algebraic model.

## Evidence hierarchy

A passing test does not prove all inputs. A proof does not establish that code matches the model. A benchmark does not establish correctness. The thesis therefore maintains separate evidence layers:

1. definitions and theorems for the abstract model;
2. constructor-level correspondence arguments between model and code;
3. generated and exhaustive tests for implementation laws;
4. empirical experiments for observed behavior and cost;
5. static integration checks for code that could not be built in the available toolchain.

## Execution environment and integration limitation

The repository declares Go 1.26.5 and contains a `tool` block in `go.mod`. The available toolchain was Go 1.23.2. Running the full module with `GOTOOLCHAIN=local` failed during module parsing:

```text
go: errors parsing go.mod:
go.mod:187: unknown block type: tool
```

Automatic toolchain download was unavailable because outbound network access failed. The standalone packages were therefore validated in GOPATH mode, where they compiled and passed race-enabled tests. The research handoff package also compiled. All Go source files in the patched repository were parsed, and changed generation/reranking call sites were checked for updated arity. Production integration remains a required validation step in an environment with the declared toolchain and dependencies.

This constraint affects confidence in adapter and cache-patch integration, not the executed status of the standalone semantic kernel.

# Minimal mathematical background for programmers

## Identity is an API decision

Programs routinely use several notions of equality:

- two pointers are the same allocation;
- two structs have equal fields;
- two JSON values differ in whitespace but represent the same object;
- two retrieval records refer to the same chunk but carry different scores;
- two derivations support the same claim through different sources;
- two requests use different worker counts but have the same intended result.

No hash function decides which notion is correct. The API must first define a projection from the full runtime value to the fields that determine behavior. Canonicalization then removes representation choices that are declared irrelevant. Hashing produces a compact name for the canonical bytes.

Write this as:

$$
\operatorname{ID}(x) = H(D, V, C(P(x)))
$$

where:

- $P$ selects identity-relevant fields;
- $C$ produces canonical bytes;
- $D$ is a domain label;
- $V$ is a schema or behavior version;
- $H$ is SHA-256 in this implementation.

A cache key error normally occurs in $P$ or $V$, not in $H$.

## Canonical representation

A canonical representation gives one byte string to every value under the chosen equality relation. For an object whose field order is irrelevant, fields are sorted. For a set, elements are encoded, sorted, and deduplicated. For a list, order remains. Type tags distinguish a string from a byte array and an integer from its textual spelling.

Canonicalization needs a version because equality policies evolve. Changing number normalization, Unicode policy, optional-field treatment, or set semantics must not silently reuse old identifiers.

## Hashes are compact names, not mathematical equality

The implementation uses SHA-256. The proofs establish that distinct valid typed values produce distinct pre-hash byte encodings. After hashing, equality is conditional on the usual collision-resistance assumption. The code does not claim that SHA-256 is injective; no fixed-size hash can be injective over an unbounded input domain.

This distinction matters for conflict handling. A state retains the full record variant under an identifier and recomputes identifiers during verification. It does not treat an identifier string as sufficient evidence that record content is correct.

## Three merge laws

A merge operation $\sqcup$ is suitable for add-only distributed evidence when it obeys:

$$
a \sqcup b = b \sqcup a
$$

**Commutativity:** delivery order does not matter.

$$
(a \sqcup b) \sqcup c = a \sqcup (b \sqcup c)
$$

**Associativity:** batching and grouping do not matter.

$$
a \sqcup a = a
$$

**Idempotence:** duplicate delivery and retry do not matter.

A type with such a merge is commonly called a join-semilattice when an induced information order is also considered. The name is less important than the API laws.

The induced order is:

$$
a \preceq b \quad\text{when}\quad a \sqcup b = b.
$$

Read this as "all information in `a` is already contained in `b`." Merge is then the least state containing both inputs.

## Provenance as a directed hypergraph

A normal graph edge connects one node to another. A derivation may require several input facts to produce one output fact, so it is better modeled as a directed hyperedge:

```text
{input fact 1, input fact 2, ...} --rule/version--> output fact
```

A fact may have several incoming derivation hyperedges. Those are alternate proofs, not duplicate facts.

An observation is a separate node attached to a fact. It records something such as "dense retriever scored this fact 0.91 for request q". Changing or adding an observation does not change the fact.

## Least finite proof rank

A seed derivation with no inputs gives its output fact rank zero. A derivation whose input facts have ranks gives its output candidate rank:

$$
1 + \max(\text{input ranks}).
$$

When several derivations support a fact, the fact receives the smallest available candidate rank:

$$
\operatorname{rank}(f)
= \min_{d:\operatorname{out}(d)=f}
\begin{cases}
0, & d\text{ has no inputs},\\
1 + \max_{i\in\operatorname{inputs}(d)}\operatorname{rank}(i), & \text{all inputs ranked}.
\end{cases}
$$

The verifier computes this by repeated relaxation until no rank improves. A cycle with no seed or other finite proof never receives a rank. A cycle with an alternate finite proof is acceptable because the least finite proof exists.

## Total ordering and deterministic views

Ranking is not add-only. Adding a high-score candidate can displace an earlier top result. The design therefore applies ranking only to a completed candidate state or an explicit snapshot.

To make a view deterministic, the comparator must be total: for any two distinct candidates, one must sort before the other. The implementation compares:

1. utility descending;
2. stable key ascending;
3. fact ID ascending;
4. observation ID ascending;
5. units ascending.

Exact duplicate candidates are removed first. A total order converts an unordered candidate set into one sequence independent of arrival order.

## Induction and correspondence

The proofs use ordinary induction rather than heavy notation.

- To prove canonical encoding, show that each scalar constructor has an unambiguous encoding and that child encodings remain unambiguous inside collection length boundaries.
- To prove proof ranks, show seed facts are ranked correctly, then show a fact with a proof of height $n+1$ becomes ranked after its inputs of height at most $n$.
- To prove schedule independence, use associativity and commutativity to reorder and regroup merges, then use idempotence to remove duplicates.

The implementation tests mirror these proof steps. This is intentional: the mathematical definitions are valuable only when they generate reviewable API contracts.

# Requirements derived from rag-ttc

## A semantic inventory of current values

The first design task was to classify existing fields by lifetime and meaning. A useful classification is:

- **semantic content:** changes what the operation computes or what the fact states;
- **lineage:** identifies the source snapshot, model, rule, or configuration under which content was obtained;
- **observation:** records request-specific measurements such as score or rank;
- **presentation:** controls labels, titles, formatting, or display order;
- **operational:** controls how work runs without changing intended results, such as worker count;
- **secret:** permits access but must not normally participate as raw cache-key material.

The same Go struct can contain several classes. That is not automatically wrong, but using the struct as a direct hash input usually is.

For example, an evidence item may contain source text, retrieval score, rank, and a citation label. Source text belongs to fact identity. Score and rank belong to a request observation. Citation label belongs to a selected view. A single struct-level digest cannot express these different semantics cleanly.

## Confirmed identity defect: fallback chunk digest

The repository's canonical chunk identity uses the text digest function. A fallback evidence identity path used JSON hashing over the text string. Even when both use SHA-256 internally, the pre-hash bytes differ because JSON includes quoting and escaping.

The consequence is practical: the same text can receive a different identity depending on which code path admitted it. Dense retrieval, knowledge retrieval, tool evidence, and cached artifacts can then fail to deduplicate.

The patch changes the fallback to the canonical text digest. The corresponding test asserts exact compatibility with `digest.Text`, not merely determinism within the fallback implementation.

This defect illustrates a general rule:

> A digest function name is not a semantic contract. All producers of the same entity must share the same pre-hash canonicalization and version.

## Confirmed identity defect: omitted RRF constant

Connected retrieval fuses branches using reciprocal-rank fusion. The fusion constant changes the weight assigned to each rank and can therefore change final ordering. The connected runtime digest included configuration and database identity but omitted the RRF constant.

Two runtimes with different behavior could consequently share one semantic digest. Any downstream cache, experiment artifact, or comparison keyed by that digest could conflate them.

The patch introduces a versioned fingerprint containing:

- connected configuration digest;
- database digest;
- the fusion algorithm identifier `weighted-rrf-v1`;
- the finite positive RRF constant.

The runtime now rejects non-finite and non-positive constants. Domain and version are `rag.connected.runtime` and `v2`.

This is a direct P01 application: algorithm parameters are semantic fields, while worker scheduling parameters would remain operational fields.

## Confirmed cache gap: resolved provider configuration

Generation and reranking cache keys identified provider and model but did not fully identify resolved inference configuration. Settings such as temperature, reasoning mode, endpoint behavior, or provider-specific options may change outputs while leaving the previous key unchanged.

The patch computes a provider-configuration fingerprint from a conservative JSON projection of resolved settings. Credential-like keys are replaced with a presence marker. The cache-key versions are advanced from `v1` to `v2`, and the provider fingerprint becomes required input.

This policy favors false cache misses over false hits. Including an operational setting may invalidate extra entries; omitting a semantic setting can return an invalid result. The projection therefore includes every serializable non-secret field unless explicitly redacted.

The policy has limitations:

- field-name heuristics cannot prove that every secret is identified;
- settings that cannot be represented as JSON cause fingerprint construction to fail;
- semantically irrelevant fields may over-invalidate;
- a presence marker intentionally makes secret rotation cache-stable, which is correct only if credentials affect authorization rather than model behavior or tenancy.

A future provider-specific catalog should replace the conservative projection once the complete settings types are stable.

## Architectural risk: evidence mixes stable and request-local data

Current `rag.Evidence` values combine source material with scores, ranks, and related metadata. This is convenient for a single retrieval pass, but it creates several semantic ambiguities:

- Does a changed rank create a new evidence identity?
- Can dense and sparse retrieval observations coexist for one chunk?
- Does an answer citation refer to the source fact or to one scored observation?
- Can a stored evidence graph be reused for a different query?
- Does reranking mutate the canonical source record?

The adapter resolves these questions by producing separate records:

```text
Fact         stable source content
Derivation   source/import or transformation lineage
Observation  request-local retrieval score, rank, and method
```

The existing type can remain as a transport value while the canonical state preserves the separation.

## Architectural risk: admission-time limits

A concurrent tool-answer path can receive evidence in arbitrary completion order. If it assigns citation labels or rejects results after reaching a limit during admission, scheduling becomes semantic:

```text
worker completion order -> admitted subset -> citation numbers -> prompt -> answer
```

This is undesirable when the intended policy is "choose the globally best evidence under a budget." A mutex prevents data races but does not prevent order dependence.

The deterministic ledger changes the sequence:

```text
admit every valid candidate
-> merge candidates
-> deterministic total sort
-> choose one per fact
-> apply budgets
-> assign labels
```

The original operational trace remains available for diagnostics, but it no longer defines the selected view.

## Constraint: preserve the role of flow

The repository intentionally avoids a general workflow DSL. P01-P03 should not reintroduce one under a different name. The semantic kernel therefore does not define retries, timeouts, queues, provider clients, or execution graphs. It exposes immutable records, pure constructors, validation, union-like merge, and deterministic view functions.

`flow` remains free to execute components sequentially or concurrently. Its wrappers are semantically transparent only under explicit conditions:

- a cache key names all behavior-affecting inputs;
- a retry does not change admitted identity or duplicate meaning;
- a batcher restores request/result association;
- budgets used during execution are declared semantic if they alter which raw results can ever be observed;
- merge occurs before query-level truncation when schedule independence is required.

## Design requirements

The source review produced the following requirements.

### Identity requirements

1. Identity projections must be explicit and versioned.
2. Collection order must be declared: list, set, or object.
3. Scalar encodings must include types and boundaries.
4. Non-finite floats must be rejected.
5. Equivalent relative path spellings must normalize independently of host OS.
6. Secrets must not be serialized as raw fingerprint inputs by default.
7. Cache constructors must require semantic provider configuration rather than infer it from partial labels.
8. Golden vectors must detect accidental encoding changes.

### Provenance requirements

1. Stable fact content must not contain query-local scores, ranks, or labels.
2. A fact must support zero or more observations and one or more derivations.
3. Every admitted fact must have at least one derivation before a state is considered valid.
4. Derivations must identify rule and rule version, output, canonical premises, request, configuration, and attributes.
5. A verifier must recompute every record ID.
6. Missing premises and subjects must be errors.
7. A selected proof package must contain transitive support.
8. Cycles without a finite proof must be rejected.

### Merge requirements

1. Merge must be associative, commutative, and idempotent.
2. Same ID plus identical full record is a retry, not a conflict.
3. Same ID plus different full record is an explicit conflict, not overwrite.
4. Snapshots and diagnostics must be deterministically ordered.
5. Concurrent admission may use mutation internally but must implement the same union semantics.
6. Selection and citation assignment must operate on a merged snapshot.
7. Selection must use a total deterministic comparator.
8. Canonical state must not be mutated by ranking or view construction.

## Proposed composition contract

The kernel offers a small contract to every retrieval subsystem:

```go
type Admission struct {
    Facts        []derive.Fact
    Derivations  []derive.Derivation
    Observations []derive.Observation
}

type Admit[Raw any] func(raw Raw, context AdmitContext) (Admission, error)
```

A component may return raw provider-specific data. Its adapter is responsible for validating and admitting canonical records. Those records enter a ledger by lawful merge. Consumers receive either a verified state or a deterministic view derived from it.

The contract is intentionally not an execution graph. It is a semantic boundary around component outputs.

# P01 - Semantic identity and cache fingerprints

## Design objective

P01 makes identity a first-class API. The objective is not merely to produce hashes. It is to make every hash reviewable through four questions:

1. What behavior or entity is being named?
2. Which fields participate?
3. How is each field interpreted and encoded?
4. Which domain and version define the contract?

The implementation is in `pkg/semanticid`.

## The typed value language

The `Value` type supports ten constructors:

```go
type Kind byte

const (
    KindNull Kind = iota
    KindBool
    KindString
    KindBytes
    KindInt
    KindUint
    KindFloat64
    KindList
    KindSet
    KindObject
)
```

The constructors are deliberately fewer than Go's type system. Semantic identity should use an explicit portable vocabulary rather than reflect over arbitrary structs.

### Scalar policies

`String` accepts valid UTF-8 and preserves code points exactly. It does not apply Unicode normalization. This means canonically equivalent Unicode sequences remain distinct unless a caller normalizes them before construction. That policy avoids silent text rewriting but must be recorded in the identity version if changed.

`Bytes` copies its input. `Int` and `Uint` retain signedness. `Float64` rejects NaN and positive or negative infinity. Negative zero is normalized to positive zero. Finite floats are encoded by their IEEE-754 bits after zero normalization.

These choices prevent several common ambiguities:

```text
string "1"        != integer 1
integer 1          != unsigned integer 1
integer 1          != float 1.0
negative zero      == positive zero
NaN                rejected
```

Whether integer 1 and float 1.0 should be semantically equal is domain-specific. The typed identity language does not assume that they are.

### Collection policies

`List` preserves order and multiplicity.

`Set` canonicalizes every child, sorts child bytes lexicographically, and removes byte-identical duplicates. Set order and duplicate delivery therefore do not affect identity.

`Object` sorts fields by name and rejects duplicate names. Field order does not affect identity. Empty and invalid UTF-8 field names are rejected.

An optional value is encoded explicitly as an object containing a name, a presence Boolean, and, when present, the value. This distinguishes absence from the zero value of a field.

### Portable path policy

`PortablePath` defines slash semantics independently of the host OS:

1. outer whitespace is trimmed;
2. backslashes are converted to slashes;
3. Unix absolute, UNC, and drive-qualified paths are rejected;
4. path cleaning removes `.` and internal `..` segments;
5. root escape through `..` is rejected.

Thus `folder/sub/../item.json` and `folder\sub\..\item.json` receive the same canonical value on Unix and Windows.

The constructor intentionally accepts only relative paths. Repository roots, corpus snapshots, and tenant scopes must be represented separately rather than hidden in machine-specific absolute paths.

## Canonical binary encoding

Each value begins with a one-byte kind tag. Variable-width payloads are length-prefixed with unsigned varints. Lists and sets encode an element count followed by individually length-prefixed child encodings. Objects encode a field count followed by length-prefixed field names and child encodings.

The grammar is:

```text
value       = kind-tag payload
null        = 0x00
bool        = 0x01 (0x00 | 0x01)
string      = 0x02 length utf8-bytes
bytes       = 0x03 length raw-bytes
int         = 0x04 canonical-varint
uint        = 0x05 canonical-uvarint
float64     = 0x06 eight-big-endian-IEEE754-bytes
list        = 0x07 count { length value }*
set         = 0x08 count { length value }*   // sorted, deduplicated
object      = 0x09 count { name-length name value-length value }* // sorted
```

Length prefixes prevent concatenation ambiguity. For example, without lengths, `["ab", "c"]` and `["a", "bc"]` could share the same concatenated bytes. Type tags prevent cross-type ambiguity.

![P01 identity pipeline.](rag-ttc-p01-p03-thesis-assets/identity.png){width=65%}

## Fingerprint envelope

A fingerprint hashes this preimage:

```text
"rag-ttc-semantic-id\x00"
+ length(domain) + domain
+ length(version) + version
+ length(canonical-value) + canonical-value
```

The textual form is:

```text
sid1:<domain>:<version>:sha256:<hex>
```

The domain grammar permits lowercase names with digits and `._/-` after the first character. Versions use alphanumeric names with `._-`. Both reject colons so the textual format remains unambiguous.

Domain and version are inside the hash preimage, not merely attached to the output string. The same canonical value in two domains or versions therefore receives a different digest under the collision-resistance assumption.

Examples include:

```text
rag.generation.request / v2
rag.provider.configuration / v1
rag.connected.runtime / v2
rag.fact / v1
rag.derivation / v1
rag.observation / v1
rag.derive.state / v1
rag.selection.candidate / v1
```

## Field-role catalogs

The package defines six field roles:

```go
const (
    RoleSemantic     FieldRole = "semantic"
    RoleLineage      FieldRole = "lineage"
    RoleObservation  FieldRole = "observation"
    RolePresentation FieldRole = "presentation"
    RoleOperational  FieldRole = "operational"
    RoleSecret       FieldRole = "secret"
)
```

A `Catalog` documents every relevant field path, its role, whether it participates in identity, and a rationale. Validation enforces default policy:

- semantic and lineage fields must participate;
- operational, presentation, and secret fields must not participate;
- observation fields are context-dependent and require an explicit choice.

The observation exception is necessary. A retrieval score should not identify a fact, but it should identify a score observation. The role describes lifetime; the catalog describes identity for a particular entity.

A sample generation request catalog is conceptually:

| Field | Role | In request identity | Reason |
|---|---|---:|---|
| normalized query | semantic | yes | changes requested computation |
| corpus snapshot | lineage | yes | changes searchable facts |
| model/profile fingerprint | semantic/lineage | yes | changes generation behavior |
| top-k used inside retrieval | semantic | yes | changes candidate set |
| worker count | operational | no | scheduling only |
| display title | presentation | no | output decoration only |
| API key | secret | no | raw credential excluded |

Catalogs are stored in the handoff package as JSON so that code review and automated checks can share one source.

## Mutation contracts

A mutation contract begins with a baseline value and a fingerprint function. Each mutation declares whether identity must change.

```go
type Mutation[T any] struct {
    Name       string
    Role       FieldRole
    MustChange bool
    Apply      func(T) T
}
```

The harness computes the before and after fingerprint and reports whether the observed behavior matches the contract. This turns identity review into a test matrix rather than an informal assertion.

The conformance experiment used six mutations:

- query change: must change;
- top-k change: must change;
- collection-set change: must change;
- worker-count change: must not change;
- API-key rotation: must not change;
- display-title change: must not change.

All six passed in the final execution.

Mutation testing does not prove that the catalog is complete. It provides a reviewable checklist and catches regressions when known fields change. The catalog must still be compared against constructors and provider configuration types.

## Formal properties of the encoding

### Theorem 5.1 - deterministic construction

**THEOREM.** For every valid `semanticid.Value`, repeated calls to `CanonicalBytes` produce the same byte sequence.

**Proof.** Scalar encodings depend only on stored scalar values. Object fields are sorted at construction. Set elements are encoded, sorted, and deduplicated at construction. Lists preserve stored order. Every writer operation is deterministic. The method copies the result before returning, so caller mutation cannot alter the stored value. Therefore repeated calls produce equal bytes. QED.

### Theorem 5.2 - injective pre-hash encoding over valid values

**THEOREM.** If two valid values have equal canonical bytes, they have the same kind and recursively equal constructor content under the language's declared semantics.

**Proof sketch.** The first byte uniquely determines the kind. For fixed-width scalar kinds, the remaining bytes uniquely determine the stored value under the constructor policy. For strings and byte arrays, the canonical unsigned length determines the payload boundary. For lists and sets, the element count and each child length determine a unique sequence of child byte strings; apply the induction hypothesis to each child. Set construction has already sorted and removed duplicate child encodings, so equal sequences represent the same set. For objects, the field count, field-name lengths, names, and child lengths determine a unique sorted field sequence; duplicate names are invalid; apply the induction hypothesis to child values. No constructor's encoding can be confused with another because kind tags differ. QED.

The theorem is about the bytes before SHA-256. Fingerprint equality additionally depends on collision resistance.

### Theorem 5.3 - object and set permutation invariance

**THEOREM.** Reordering object fields or set inputs does not change canonical bytes. Reordering list elements generally can.

**Proof.** Object construction sorts by field name. Set construction sorts by child encoding and deduplicates. List construction performs neither transformation. QED.

### Theorem 5.4 - domain and version separation

**CONDITIONAL THEOREM.** For a fixed canonical value, changing domain or version changes the pre-hash byte sequence. Assuming no SHA-256 collision on the compared inputs, it changes the fingerprint.

**Proof.** Domain and version occur as separate length-prefixed fields inside the preimage. Changing either changes at least one field's bytes or length. The conditional hash statement follows from collision resistance for those inputs. QED.

## Golden vectors and compatibility

The package includes a golden fingerprint test. Golden vectors serve a different purpose from law tests. A law can continue passing after an incompatible global change; a golden vector fails when the exact byte contract changes.

Any intentional encoding change requires:

1. a new identity version;
2. new golden vectors;
3. a migration policy for stored fingerprints and cache namespaces;
4. dual-read or explicit invalidation if old artifacts remain in use.

Changing implementation while leaving the version constant is a compatibility defect even when the new encoding appears more elegant.

## Production applications

### Evidence fallback identity

The fallback path now uses the same text digest as canonical chunks. This restores one identity function for the same source text.

### Connected runtime identity

The connected runtime now uses `rag.connected.runtime/v2` and includes the RRF algorithm identifier and constant. Tests assert sensitivity to connected configuration, database identity, and RRF constant, and reject invalid constants.

### Provider configuration

Provider bundles now carry `ConfigurationFingerprint` for embedding, generation, and reranking roles. The fingerprint contains role, provider, model, and a redacted projection of resolved settings.

### Generation and reranking caches

Generation cache keys and flow adapters now require the provider configuration fingerprint. The key version is `v2`. Reranking cache keys likewise require a provider fingerprint and use `v2`. All located production call sites were updated to pass the role-specific bundle metadata.

These migrations deliberately invalidate old cache namespaces. Reusing `v1` would imply compatibility that is not present.

## Executed P01 evidence

The final package test suite passed under the race detector. It included:

- object-order invariance;
- set-order and duplicate invariance;
- list-order sensitivity;
- 500 generated object/set permutation trials;
- domain and version separation;
- text and JSON fingerprint round trips;
- finite-float and zero policy;
- path normalization and root-escape rejection;
- host-independent slash normalization;
- duplicate object-field rejection;
- golden fingerprint stability;
- catalog validation;
- mutation-contract evaluation.

The conformance artifact records:

```text
contract passed:             true
set permutation invariant:   true
object order invariant:      true
domain separated:            true
version separated:           true
```

## P01 limitations

The identity layer has explicit boundaries.

- SHA-256 collisions are not structurally impossible.
- Unicode normalization is caller policy.
- The current portable-path grammar trims outer whitespace and does not attempt to model every filesystem restriction.
- `Float64` preserves binary floating-point identity, not mathematical decimal equivalence.
- Field catalogs can be incomplete if not maintained with type changes.
- The conservative provider projection can over-invalidate and relies on field-name heuristics for redaction.
- A fingerprint names declared semantics; it does not prove that the underlying operation is pure or deterministic.

These are acceptable when versioned and documented. The dangerous case is an implicit or unreviewed policy.

# P02 - Canonical facts and provenance

## Design objective

P02 introduces a small semantic interchange model for evidence. The objective is to answer three distinct questions with three distinct record types:

- **What is asserted or retrieved?** A `Fact`.
- **Why is it in the state?** One or more `Derivation` records.
- **What was measured about it for a request?** Zero or more `Observation` records.

This separation prevents a retrieval score, a query rank, a citation label, or a worker completion time from changing the identity of source content. It also prevents deduplication from erasing independent support.

The implementation is in `pkg/rag/derive`.

## Canonical fact model

A fact contains only a semantic identity, a kind, a schema, and canonical JSON payload:

```go
type Fact struct {
    ID      FactID          `json:"id"`
    Kind    string          `json:"kind"`
    Schema  string          `json:"schema"`
    Payload json.RawMessage `json:"payload"`
}
```

`Kind` identifies a broad semantic class such as `source-chunk`, `claim`, or `representation`. `Schema` identifies the payload contract. Both are part of identity. A change from `rag.claim/v1` to `rag.claim/v2` is therefore explicit even if one payload happens to serialize the same way.

The fact ID is a P01 fingerprint over:

```text
canonical-json-policy = derive-json-v1
kind
schema
canonical payload bytes
```

Its domain and version are `rag.fact/v1`.

The request that discovered the fact is not part of fact identity. The corpus or source path may be in payload if it changes what entity the fact denotes, or in a seed derivation if it is lineage rather than content. Adapters choose that boundary per source schema.

## Canonical JSON policy

Fact payloads, derivation attributes, observation payloads, snapshots, and proof bundles use a local deterministic JSON policy named `derive-json-v1`.

The normalizer:

- parses with `json.Number` rather than binary float conversion;
- sorts object member names;
- rejects duplicate object member names;
- removes insignificant whitespace;
- rejects trailing JSON values;
- normalizes decimal and exponent spellings to one plain decimal form;
- maps negative zero to zero;
- preserves array order;
- preserves strings exactly under Go's JSON escaping rules.

For example, these inputs normalize to the same bytes:

```json
{"b":1.0,"a":[1e0,{"z":-0,"y":2.5000}]}
```

```json
{"a":[1,{"y":2.5,"z":0}],"b":1}
```

The result is:

```json
{"a":[1,{"y":2.5,"z":0}],"b":1}
```

This format is intentionally versioned separately from the P01 binary value language. It is not claimed to be RFC 8785. In particular, its number formatting favors exact finite decimal normalization and can expand exponents to plain decimal form. Its use is internal to the `derive` schema and should not be silently substituted for another canonical JSON standard.

Duplicate-name rejection is important. Standard JSON decoders often retain only one of repeated names, which can make signatures and fingerprints parser-dependent. The normalizer rejects ambiguity instead.

## Derivation model

A derivation records one support edge from zero or more input facts to one output fact:

```go
type Derivation struct {
    ID          DerivationID    `json:"id"`
    Output      FactID          `json:"output"`
    Rule        string          `json:"rule"`
    RuleVersion string          `json:"rule_version"`
    Inputs      []Input         `json:"inputs,omitempty"`
    RequestID   string          `json:"request_id,omitempty"`
    ConfigID    string          `json:"config_id,omitempty"`
    Attributes  json.RawMessage `json:"attributes,omitempty"`
}

type Input struct {
    Role string `json:"role"`
    Fact FactID `json:"fact"`
}
```

The rule and version identify the transformation semantics. Input roles carry positional meaning, so the stored input sequence is canonicalized by sorting `(role, fact ID)`. Delivery order therefore does not alter derivation identity. A rule requiring ordered inputs should express order in role names such as `left`, `right`, or `position-0003`, rather than rely on arrival order.

`RequestID` and `ConfigID` are included because two invocations can produce the same output through materially different lineage. A future deployment may choose a second derivation identity profile that omits request IDs to deduplicate repeated execution traces while retaining execution events separately. The current profile favors audit specificity.

Seed imports are represented as derivations with no input facts and a rule name prefixed by `seed/`. This avoids a special provenance bypass. Every valid fact, including source facts, is supported by at least one derivation record.

The derivation ID uses domain `rag.derivation/v1` and contains output, rule, rule version, canonical input list, request ID, configuration ID, and canonical attributes.

## Observation model

An observation attaches request-specific information to one fact:

```go
type Observation struct {
    ID        ObservationID   `json:"id"`
    Kind      string          `json:"kind"`
    Schema    string          `json:"schema"`
    Subject   FactID          `json:"subject"`
    RequestID string          `json:"request_id,omitempty"`
    Payload   json.RawMessage `json:"payload"`
}
```

Examples include:

- dense retrieval score and rank;
- BM25 score and rank;
- reranker score;
- ambiguity status;
- query-specific relevance judgment;
- model confidence estimate;
- extraction span quality;
- latency or cost measurement, when that measurement belongs in the semantic record rather than an operational trace.

Observation identity uses domain `rag.observation/v1`. Its subject fact ID is required. An observation may change freely without changing the fact.

This relationship is shown in the provenance fixture:

![One canonical claim has two derivations; query-local observations remain separate.](rag-ttc-p01-p03-thesis-assets/provenance.png){width=72%}

## State model

A state contains three maps:

```go
type State struct {
    facts        map[FactID]map[string]Fact
    derivations  map[DerivationID]map[string]Derivation
    observations map[ObservationID]map[string]Observation
}
```

The outer key is semantic identity. The inner key is a fingerprint of the complete record. The inner map is therefore a set of full variants sharing one claimed semantic ID.

Why not use `map[FactID]Fact`? Because a single-value map forces a conflict policy at insertion time. First-writer-wins, last-writer-wins, or panic all make worker timing or local control flow part of meaning. The variant set preserves evidence needed for diagnosis and independent verification.

An unconflicted fact ID has exactly one full variant. A conflicted fact ID has two or more. `State.Fact(id)` returns a value only when the ID is unconflicted. `State.FactVariants(id)` returns all variants. Equivalent methods exist for derivations and observations.

The complete state snapshot sorts IDs and record-variant keys. Canonical JSON and a state fingerprint can therefore be compared across runs, backends, and merge schedules.

## Provenance as a finite hypergraph

Let:

- $F$ be the set of unconflicted fact records;
- $D$ be the set of unconflicted derivations;
- $O$ be the set of unconflicted observations.

Each derivation $d \in D$ has one output $\operatorname{out}(d) \in F$ and a finite list of role-labeled inputs $\operatorname{in}(d) \subseteq F$. It is a directed hyperedge from its premise set to its output.

Each observation $o \in O$ has one subject $\operatorname{subj}(o) \in F$.

The verifier requires referential closure:

$$
\forall d\in D:\operatorname{out}(d)\in F
$$

$$
\forall d\in D, f\in\operatorname{in}(d):f\in F
$$

$$
\forall o\in O:\operatorname{subj}(o)\in F.
$$

It also requires at least one finite well-founded proof for every fact.

## Verification algorithm

`Verify` returns a deterministically ordered `VerificationReport` containing validity, issues, ranks, and counts.

Verification has five passes.

### Conflict detection

Every outer ID with more than one complete record variant produces an `identity-conflict` issue. Conflicted records are excluded from the unambiguous fact, derivation, or observation maps used by later checks.

### Identifier recomputation

Every record ID is recomputed from canonical content. Mismatches yield:

- `fact-id-mismatch`;
- `derivation-id-mismatch`;
- `observation-id-mismatch`.

This detects altered payloads, attributes, rules, request IDs, and configuration IDs, assuming no relevant hash collision.

### Dependency closure

A derivation whose output is absent or conflicted yields `derivation-output-missing`. Each absent or conflicted premise yields `derivation-input-missing`. An observation whose subject is absent or conflicted yields `observation-subject-missing`.

### Least proof-rank computation

The verifier begins with no ranks and repeatedly examines derivations. A zero-input derivation can assign rank zero. A derivation whose inputs are all ranked can assign one plus the maximum input rank. If this candidate improves the current rank, the map changes and another pass occurs.

The algorithm stops because the state is finite and ranks only move from absent to finite or decrease to a smaller nonnegative integer. In practice, the first discovered rank can be non-minimal depending on iteration order, so relaxation continues until no improvement remains.

### Completeness and well-foundedness

A fact with no derivation yields `fact-unproved`. A fact with derivations but no finite rank yields `fact-not-well-founded`. The latter detects a cycle without a seed or alternate finite proof.

Issues are sorted by code, namespace, ID, and message. Diagnostic order is therefore deterministic.

## The least-rank theorem

Define the height of a finite derivation tree:

- a zero-input derivation has height zero;
- a derivation with child proof trees has height one plus their maximum height.

A fact's least proof height is the minimum height among its finite proof trees.

### Theorem 6.1 - rank soundness

**THEOREM.** If the verifier assigns rank $n$ to a fact, that fact has a finite derivation tree of height $n$.

**Proof.** A rank is assigned only by a derivation whose inputs already have ranks. For a zero-input derivation, the constructed tree has height zero. For a nonzero derivation, apply induction to each ranked input to obtain finite trees. Attach them under the derivation node. The resulting height is one plus the maximum input rank, equal to the candidate rank. If a later relaxation lowers the rank, it does so through another derivation with a correspondingly lower finite tree. QED.

### Theorem 6.2 - rank completeness and minimality

**THEOREM.** If a fact has a finite derivation tree of least height $n$, the verifier eventually assigns it rank $n$, and no smaller rank is possible.

**Proof.** By induction on $n$. For $n=0$, a zero-input derivation is immediately eligible and assigns zero. Assume every fact with a proof of height at most $n$ eventually receives its least rank. Consider a least-height $n+1$ proof of fact $f$. Every premise has a proof of height at most $n$, so by induction all receive their least ranks. The derivation then becomes eligible and proposes exactly the height of this proof, at most $n+1$. Since the selected proof was least, no derivation can propose a smaller valid rank. Repeated relaxation therefore assigns $n+1$. QED.

### Corollary 6.3 - cycle handling

A pure cycle without a zero-input or otherwise finite incoming proof receives no rank and is rejected. A cycle with an alternate finite proof receives the least finite rank through that alternate proof.

This policy rejects circular justification while permitting redundant cyclic dependencies that do not constitute the chosen proof.

## Proof bundles

A `ProofBundle` packages selected fact IDs and their transitive support:

```go
type ProofBundle struct {
    Schema          string   `json:"schema"`
    CorpusID        string   `json:"corpus_id,omitempty"`
    ConfigurationID string   `json:"configuration_id,omitempty"`
    Selected        []FactID `json:"selected"`
    State           Snapshot `json:"state"`
}
```

`BuildProofBundle` first requires a valid source state. It performs a backward traversal from selected facts, including:

- each selected fact;
- every derivation whose output is included;
- every premise of those derivations, recursively;
- observations attached to included facts.

All alternate derivations are retained. This choice can produce a larger bundle than selecting one minimal proof, but it preserves independent support and permits later proof-policy choices.

`VerifyProofBundle` checks the schema, reconstructs the state, runs the full verifier, and confirms that every selected fact is present and unconflicted.

The bundle is proof-carrying in the structural sense: an independent consumer can recompute IDs and validate declared dependencies without trusting the producer's in-memory state. It is not a cryptographic signature and does not certify source truth.

## Fact identity is independent of observations

### Theorem 6.4 - observation separation

**THEOREM.** Adding, changing, or removing observations cannot change a fact ID.

**Proof.** The fact-ID preimage contains only the canonical JSON policy label, kind, schema, and payload. Observation records are stored and fingerprinted in a separate namespace. No observation field is read by `factID`. QED.

This theorem is simple but operationally important. It permits reranking, multiple retrievers, A/B experiments, and query replay over one canonical fact store.

## Alternate derivations are first-class

Suppose dense retrieval and knowledge-graph expansion both lead to one canonical source fact. Or suppose two source chunks independently support one claim. The state records one fact and two derivations.

This avoids two bad extremes:

- duplicating the fact for every discovery path, which complicates selection and citation;
- retaining only one proof, which loses corroboration and deletion resilience.

A fact remains available after deleting one source only if another valid derivation remains. P11 can later use this structure for dependency-aware retraction.

## Adapters to rag-ttc

### `rag.Chunk`

`ragcodec.Chunk` maps canonical chunk content and source location into a `source-chunk` fact. A seed derivation records corpus and request lineage. The legacy chunk ID is preserved as lineage metadata rather than blindly reused as the new semantic ID.

This allows comparison between old and new identity during migration.

### `rag.Representation`

`ragcodec.Representation` creates a representation fact supported by a derivation whose input is the source chunk fact. The derivation records the representation-building rule, request, and configuration.

This distinguishes source identity from transformed representation identity.

### `rag.Evidence`

`ragcodec.Evidence` creates or identifies the source fact, admits a seed/retrieval derivation, and creates a retrieval observation containing score, rank, and method. Two `rag.Evidence` values with identical source content but different scores map to one fact and two observations.

### `knowledge.Fact`

`knowledgecodec.Fact` maps claim content into a canonical fact. Source spans, methods, status, legacy identifiers, request, and configuration become derivation attributes. Confidence becomes an observation. Input chunk fact IDs form the proof premises.

The adapter makes the current knowledge type usable without declaring every field part of stable claim identity.

## P02 conformance fixture

The executed diamond fixture contains:

- source fact A: a chunk explicitly naming the oak-wilt pathogen;
- source fact B: a chunk describing a vascular fungus;
- claim fact C: oak wilt is caused by *Bretziella fagacearum*;
- seed derivations for A and B;
- extraction derivation from A to C;
- entity-resolution derivation from B to C;
- dense and BM25 observations attached to A and B.

The final executed report contained:

```text
fact IDs:                 3
fact variants:            3
derivation IDs:           4
derivation variants:      4
observation IDs:          2
observation variants:     2
claim least rank:         1
independent claim proofs: 2
bundle verified:          true
tamper detected:          true
```

The claim has rank one because either source fact has rank zero and either one-step derivation supports the claim. The bundle retains both proofs.

## Tamper and omission behavior

The test suite altered a fact payload without changing its ID. Verification rejected the state with an ID mismatch. It then removed a source fact while retaining a derivation that referenced it. Verification rejected the state with a missing-input issue.

These tests demonstrate two distinct checks:

- content integrity: does the ID match the record?
- dependency integrity: does every declared edge refer to a usable record?

A provenance system that checks only one of these remains vulnerable to malformed artifacts.

## P02 limitations

The provenance kernel does not solve all trust questions.

- A valid seed derivation means "declared as imported from this source", not "source is truthful".
- Rule names and versions are identifiers; the verifier does not execute or prove the rule implementation.
- Request and configuration IDs are trusted strings unless themselves semantic fingerprints.
- Proof bundles are not signed and provide no origin authentication.
- The bundle currently includes all alternate derivations, which can grow substantially.
- The verifier is in-memory and optimized for clarity, not billion-edge graphs.
- Facts are JSON payloads rather than a strongly typed schema registry.
- Unicode normalization remains schema policy.
- Retraction, temporal validity, authorization, and negative evidence are future layers.

The important gain is that these concerns now have explicit attachment points rather than being mixed into evidence structs.

# P03 - Lawful merge and deterministic evidence ledger

## Design objective

P03 defines what it means to combine evidence from independent workers. The essential requirement is:

> A fixed set of admitted records must produce one canonical state regardless of delivery order, batching, concurrency, duplicate messages, or retry.

A mutex alone cannot provide this property. A mutex serializes writes, but the serialized order may still change first-writer selection, budget consumption, citation labels, or map replacement. The property must come from the merge operation itself.

The implementation uses componentwise set union over complete record variants.

## Formal state definition

Let:

- $I_F$, $I_D$, and $I_O$ be the identifier spaces for facts, derivations, and observations;
- $R_F$, $R_D$, and $R_O$ be the corresponding complete record spaces.

A finite evidence state is a triple:

$$
S = (S_F, S_D, S_O)
$$

where:

$$
S_F : I_F \rightharpoonup \mathcal{P}_{fin}(R_F)
$$

and similarly for derivations and observations. Each record in a bucket claims the bucket's semantic ID. A bucket can contain one variant, no variant, or several conflicting variants.

The join of states is pointwise union:

$$
(S \sqcup T)_F(i) = S_F(i) \cup T_F(i)
$$

and likewise for $D$ and $O$.

The empty state maps every identifier to the empty set.

The Go implementation represents finite sets as inner maps keyed by a fingerprint of the complete canonical record. The record key is not used as semantic identity; it is used to deduplicate byte-equivalent variants inside an identity bucket.

## Why conflicts are retained

Consider two workers:

```text
worker A: fact ID x, payload A
worker B: fact ID x, payload B
```

If `x` is supposed to be a content-derived identifier, both records cannot be valid unless a hash collision or implementation defect occurred. Yet choosing one record at merge time destroys evidence about the defect.

The state therefore becomes:

```text
State[x] = {record A, record B}
```

and verification reports an identity conflict. This result is the same under every delivery order.

![Conflicting immutable variants are retained and reported.](rag-ttc-p01-p03-thesis-assets/conflict.png){width=68%}

Conflict retention has several benefits:

- diagnostics retain both producers' outputs;
- replay can reproduce the conflict;
- a backend can quarantine the identity;
- dependent derivations are rejected because the fact is ambiguous;
- schedule cannot decide the winner;
- future repair tools can compare variants and lineage.

This policy is appropriate for immutable semantic records. Mutable application entities may require domain-specific conflict resolution, but that policy should be a separate explicit view or state transition.

## The join laws

### Theorem 7.1 - commutativity

**THEOREM.** For all states $A$ and $B$,

$$
A \sqcup B = B \sqcup A.
$$

**Proof.** Each component and each identifier bucket is merged by set union. Set union is commutative. Equality holds pointwise for facts, derivations, and observations. QED.

### Theorem 7.2 - associativity

**THEOREM.** For all states $A$, $B$, and $C$,

$$
(A \sqcup B) \sqcup C = A \sqcup (B \sqcup C).
$$

**Proof.** Each bucket is a set. Set union is associative. Componentwise application preserves the equality. QED.

### Theorem 7.3 - idempotence

**THEOREM.** For every state $A$,

$$
A \sqcup A = A.
$$

**Proof.** Unioning a set with itself adds no element. The result holds for every bucket and component. QED.

### Theorem 7.4 - identity

**THEOREM.** Let $\bot$ be the empty state. Then:

$$
A \sqcup \bot = \bot \sqcup A = A.
$$

**Proof.** Union with the empty set is the identity operation in every bucket. QED.

Together, the finite states form a commutative idempotent monoid under join, and a finite join-semilattice under the induced information order.

## Schedule independence

A worker execution produces a finite sequence of deltas:

$$
\Delta_1, \Delta_2, \ldots, \Delta_n.
$$

The accumulated state is:

$$
S_0 \sqcup \Delta_1 \sqcup \cdots \sqcup \Delta_n.
$$

### Theorem 7.5 - permutation invariance

**THEOREM.** For any permutation $\pi$ of $1,\ldots,n$,

$$
S_0 \sqcup \Delta_1 \sqcup \cdots \sqcup \Delta_n
=
S_0 \sqcup \Delta_{\pi(1)} \sqcup \cdots \sqcup \Delta_{\pi(n)}.
$$

**Proof.** Associativity permits regrouping; commutativity permits swapping adjacent deltas. Every permutation is a sequence of adjacent swaps. QED.

### Corollary 7.6 - batching independence

Combining deltas into arbitrary batches before merging does not change the result.

### Corollary 7.7 - retry and duplicate-message safety

Adding any delta one or more additional times does not change the result.

**Proof.** Use idempotence to remove repeated terms. QED.

### Conditional theorem 7.8 - concurrent convergence

**CONDITIONAL THEOREM.** If every admitted delta is eventually merged, no delta is destructively removed, and the concurrent ledger implements the same join, then all executions over the same set of deltas converge to the same canonical state.

This does not claim that effectful workers always produce the same deltas. Provider nondeterminism, time-dependent data, authorization changes, or incomplete cache identity can change the delta set. The theorem isolates scheduling from those other sources of variation.

## Persistent state and mutable ledger

`State.Join` is a simple persistent reference operation:

```go
func Join(a, b State) State {
    r := a.Clone()
    r.mergeMutable(b)
    return r
}
```

It is easy to reason about and safe for functional use, but repeated single-record insertion clones the entire accumulated state each time.

`Ledger` is a mutable facade:

```go
type Ledger struct {
    mu    sync.RWMutex
    state State
}
```

`Merge` acquires a write lock and mutates inner maps by union. `Snapshot` acquires a read lock and returns a clone. The lock provides race freedom; the union provides semantic schedule independence.

This distinction is central:

```text
mutex                 -> operations do not race in memory
associative/commutative/idempotent join
                      -> operation order and retry do not change meaning
```

A system can have either property without the other. P03 requires both.

## Deterministic snapshots

Go map iteration order is not a serialization contract. `State.Snapshot` sorts:

1. fact IDs and each fact variant key;
2. derivation IDs and each derivation variant key;
3. observation IDs and each observation variant key.

`CanonicalJSON` then normalizes the snapshot. State equality compares canonical bytes. The state fingerprint uses `rag.derive.state/v1` over those bytes.

Deterministic snapshots are useful for:

- result comparisons;
- golden fixtures;
- experiment artifacts;
- backend conformance;
- cache values;
- reproducible bug reports;
- checksums and signatures in later work.

They are not required for the mathematical join laws, but they make those laws observable in tests.

## The selection barrier

The canonical state is add-only. Selection is not. A top-k operation can remove a previously selected candidate when a stronger candidate appears. P03 therefore places a barrier between accumulation and view construction.

A candidate contains:

```go
type Candidate struct {
    Fact        FactID
    Observation ObservationID
    StableKey   string
    Utility     float64
    Units       int
}
```

A policy contains a version, item limit, optional unit limit, and label prefix.

Selection performs this sequence:

1. validate the policy;
2. validate every candidate's fact and optional observation against an unconflicted state;
3. reject non-finite utilities and invalid unit counts;
4. deduplicate exact candidate records by a P01 fingerprint;
5. sort by a total comparator;
6. skip subsequent candidates for a fact already selected;
7. apply item and unit budgets;
8. assign ranks and labels in final order.

![Non-monotone ranking and budgets occur only after candidate merge.](rag-ttc-p01-p03-thesis-assets/selection.png){width=64%}

The state is not modified. Multiple policies can produce multiple views over one canonical evidence set.

## Deterministic selection theorem

Let $C$ be a finite multiset of candidates. Let $U(C)$ remove exact duplicate candidate records. Let $<$ be the total comparator defined by utility, stable key, fact ID, observation ID, and units. Let $P$ be a fixed selection policy.

### Theorem 7.9 - candidate permutation invariance

**THEOREM.** `Select(S, C, P)` is unchanged by any permutation of `C`, provided all candidates are valid against the same state `S`.

**Proof.** Exact deduplication produces the same set $U(C)$ for every permutation. Sorting a finite set by a total comparator produces one sequence. The subsequent scan is a deterministic function of that sequence and fixed policy. Therefore the final selected view, ranks, and labels are equal. QED.

### Corollary 7.10 - duplicate candidate safety

Repeating an exact candidate does not change the selected view.

### Theorem 7.11 - one selected record per fact

For every output of `Select`, no two selected entries have the same fact ID.

**Proof.** The scan maintains a `seen` set and skips any candidate whose fact has already been selected. QED.

The one-per-fact rule is a policy choice suitable for citation evidence. It is not a universal property of ranking. A future policy can permit several observations per fact while retaining total ordering and post-merge application.

## Legacy arrival-order counterexample

Consider three candidates and an item budget of two. A legacy collector accepts the first two completions and rejects the third. Every completion permutation can produce a different ordered pair. The conformance experiment observed six distinct views across the six permutations.

The lawful implementation merged all candidates, then selected. It produced one view across all six permutations.

This is a falsifying counterexample, not just a positive test. It demonstrates that concurrency safety plus a fixed numeric limit is insufficient. The placement of the limit determines semantics.

## Deterministic tool-answer ledger

`pkg/rag/toolanswer/deterministic_ledger.go` adapts the P03 pattern to the existing tool-answer subsystem.

During admission it:

- converts evidence to canonical fact, derivation, and observation records;
- merges them into the ledger;
- records candidates without assigning citation labels;
- retains all valid candidates regardless of completion order.

During finalization it:

- snapshots the merged state;
- verifies or validates candidate references;
- applies the deterministic selection policy;
- assigns labels only in final selected order;
- returns a view suitable for prompt construction.

A warning comment remains on the legacy admission-time path to identify the semantic risk during migration.

## Conflict semantics

Same ID and same complete record is an idempotent retry. Same ID and different complete record is a conflict. The state never attempts to infer which producer is correct.

A verifier treats conflicted records as unavailable for proof closure. This is conservative. It prevents downstream facts from being validated through ambiguous premises. A remediation tool can later:

- recompute the identifier and identify the malformed variant;
- quarantine a producer version;
- migrate an old schema;
- split a mistakenly conflated identity domain;
- record a human adjudication as a new explicit derivation or view.

Conflict resolution should not be smuggled into merge.

## Executed P03 evidence

The final conformance experiment used six deltas from the diamond fixture. It computed all $6! = 720$ delivery permutations. Every permutation produced the same canonical state fingerprint.

It then used three candidates and all six completion permutations:

```text
lawful selected views:      1
legacy arrival-time views:  6
```

An explicit same-ID/different-payload fixture produced two retained variants under both delivery orders.

The concurrent test launched duplicate merges from goroutines and ran under the Go race detector. Across 100 conformance runs:

```text
concurrent divergences: 0
```

The package tests also ran 500 generated law trials for identity, associativity, commutativity, and idempotence, plus deterministic snapshot round trips and selection tie-breaking.

These results do not prove the implementation for every input. They are targeted evidence that the code corresponds to the union model and that named adversarial cases are handled.

## Performance experiment

The persistent reference implementation clones accumulated state for every `Join`. The mutable ledger updates inner maps in place under a lock. Both produce equal final states.

Median timings from the scaling artifact were:

| Facts inserted | Persistent repeated join (ms) | Mutable ledger (ms) | Ratio |
|---:|---:|---:|---:|
| 250 | 13.22 | 0.60 | 21.9x |
| 500 | 68.82 | 0.69 | 103.6x |
| 1,000 | 344.35 | 1.68 | 199.7x |
| 2,000 | 1,513.77 | 3.09 | 426.1x |
| 4,000 | 5,237.40 | 6.94 | 760.8x |

![Scaling of the reference persistent join and mutable ledger.](rag-ttc-p01-p03-thesis-assets/scaling.png){width=88%}

The delivered evaluation artifact records one 2,000-fact conformance run at approximately 1,839.2 ms for repeated persistent joins and 5.29 ms for the mutable ledger. Timing varied across runs, but output equality held.

**EMPIRICAL interpretation.** The algebra does not require persistent cloning. A mutable builder or database upsert layer can preserve identical set-union semantics at far lower ingestion cost. The persistent implementation should remain a clarity reference and small-state utility, not the primary streaming ingestion path.

The experiment is not a production benchmark. It uses in-memory synthetic facts, no database, no provider calls, one process, and a workload designed to expose cloning cost. Ratios must not be generalized to end-to-end RAG latency.

## P03 limitations

- The ledger is process-local and does not implement replicated-state transport.
- The mutex can become a contention point; sharding by namespace or identifier is future work.
- Variant retention can increase storage when a producer is faulty.
- Selection assumes a deterministic finite utility value supplied by the caller.
- A deterministic tie-break does not make a ranking policy substantively good.
- `MaxUnits` uses caller-supplied units; tokenizer identity belongs in the policy configuration if units represent tokens.
- The fixed selected view requires a snapshot boundary. Streaming "best so far" views are partial and may change.
- Deletion is not a join operation and requires dependency-aware retraction.
- Cross-process convergence additionally requires reliable eventual delta delivery or anti-entropy.

The kernel is nonetheless sufficient to remove accidental ordering from the core evidence state and selected citation view.

# Composition with rag-ttc

## Two semantic layers

The cleanest integration keeps two layers separate.

| Layer | Responsibility | Existing/new owner |
|---|---|---|
| Operational semantics | retries, cache lookup, batching, concurrency, timeout, budgets, tracing, order restoration | existing `flow` and component packages |
| Information semantics | identity, canonical records, provenance, union merge, conflict detection, verification, deterministic views | `semanticid` and `derive` |

The distinction prevents the semantic kernel from becoming a second execution framework. It also makes operational wrappers auditable: a wrapper is correct when it preserves the information semantics of the wrapped component under its declared policy.

## Plan, Execute, Admit, Merge, View, Generate

The proposed end-to-end shape is:

```text
Plan -> Execute -> Admit -> Merge -> Verify -> View -> Generate
```

### Plan

A planner creates typed requests from the query, corpus snapshot, authorization context, and strategy configuration. Planning should return a semantic request fingerprint alongside the operational request.

```go
type Planned[Request any] struct {
    Request       Request
    SemanticID   semanticid.Fingerprint
    ConfigurationID string
}
```

The plan identifies what is intended, not which worker will run it.

### Execute

Execution performs effects: database queries, provider calls, model inference, filesystem reads, or tool invocation. `flow` owns retries, batching, budgets, and observability.

Raw results need not use the canonical interchange schema. They remain provider-specific until admission.

### Admit

Admission is the trusted conversion boundary. It validates raw results, applies canonical schemas, constructs facts, derivations, and observations, and returns a delta state.

```go
type AdmitContext struct {
    RequestID     string
    ConfigurationID string
    CorpusID      string
}

type Admit[Raw any] func(Raw, AdmitContext) (derive.State, error)
```

An admission error rejects the malformed record rather than inventing a partial identity.

### Merge

Every accepted delta enters a `derive.Ledger`. Merge may occur after each result, per batch, per worker, or through a database adapter. The only semantic requirement is implementation of the same set-union join.

### Verify

A verification boundary can be placed:

- after every admission in high-assurance systems;
- after a worker batch;
- before selected-view construction;
- before artifact export;
- at an independent consumer.

Incremental verification can later avoid a full scan.

### View

A view interprets the canonical state for a query. It may rank, filter, resolve ambiguity, pack tokens, choose proof policies, label citations, or redact by authorization. Its policy fingerprint should identify all behavior-affecting choices.

Views are replaceable because they do not mutate facts.

### Generate

Generation consumes a selected view and a generation profile. The generation cache key includes the prompt/input view identity and the provider-configuration fingerprint. Generated output can itself be admitted as a fact with a derivation from the selected evidence and generation configuration.

## A minimal composable API

The following API sketch is sufficient for most integrations:

```go
type Component[Request, Raw any] interface {
    Run(context.Context, Request) (Raw, error)
}

type Adapter[Raw any] interface {
    Admit(Raw, AdmitContext) (derive.State, []derive.Candidate, error)
}

type SemanticComponent[Request, Raw any] struct {
    Execute Component[Request, Raw]
    Adapter Adapter[Raw]
}

func RunAndAdmit[Request, Raw any](
    ctx context.Context,
    c SemanticComponent[Request, Raw],
    request Request,
    admitCtx AdmitContext,
) (derive.State, []derive.Candidate, error)
```

`flow` can wrap `Execute` without changing `Adapter`. A backend can replace the in-memory ledger without changing facts. A ranking policy can replace `Select` without changing retrieval. This is composability by small semantic interfaces rather than a workflow syntax.

## Cache transparency

A cache wrapper is semantically transparent when:

```text
cacheMiss(request) -> execute -> admit -> delta
cacheHit(request)  -> decode cached raw or admitted delta -> same delta
```

The key must identify every input that can change the admitted delta, including:

- normalized request content;
- corpus or database snapshot;
- model/provider configuration;
- retrieval algorithm and semantic parameters;
- authorization scope when it changes visible data;
- adapter/rule/schema versions;
- tokenizer version if a budget affects reachable raw results.

It normally excludes:

- worker count;
- retry count;
- trace ID;
- logging configuration;
- presentation title;
- raw API secret, when credential rotation does not change tenancy or accessible data.

### Conditional cache theorem

Let `Exec(k)` be the admitted delta produced by executing semantic input `k`. Let a cache return a previously stored delta for the same fingerprint.

**CONDITIONAL THEOREM.** A cache hit is information-semantically equivalent to execution if:

1. the fingerprint projection is complete for `Exec`;
2. canonicalization is stable within the key version;
3. cached bytes decode to the same admitted delta;
4. external state named by the key, such as corpus snapshot, is immutable;
5. authorization and tenancy are included when relevant.

Then merging the cache hit yields the same canonical state as merging a fresh execution result.

The theorem exposes why P01 is part of execution correctness. A cache is not merely a performance feature; it is an alternative implementation of a semantic operation.

## Retry transparency

A retry wrapper may execute a component more than once. There are two cases.

1. **Same admitted delta.** P03 idempotence removes duplicates.
2. **Different admitted delta.** Both deltas are preserved. They may be alternate observations/derivations, or they may expose nondeterminism and conflict.

Retries are therefore safe in the sense that repeated identical information does not change state. They are not guaranteed to hide provider nondeterminism. The record model makes that nondeterminism observable rather than allowing last-writer replacement.

A policy can later choose whether repeated stochastic generations are separate facts, observations, or derivations. That choice belongs in the relevant identity catalog.

## Batch transparency

A batcher changes how several requests are transported. To preserve semantics it must retain a stable association between every result and its request identity. The admitted union of a batch must equal the union of individually admitted results:

$$
\operatorname{AdmitBatch}(r_1,\ldots,r_n)
=
\bigsqcup_{i=1}^{n}\operatorname{Admit}(r_i).
$$

This equation is an adapter conformance test. It also exposes accidental batch-global fields, such as one rank sequence shared across requests.

## Budget semantics

Not all budgets are operational.

A deadline that merely cancels outstanding work is operational in configuration but changes completeness of the returned partial state. The result must therefore carry status such as:

```go
type Completion struct {
    Saturated       bool
    CompletedPlans  []semanticid.Fingerprint
    PendingPlans    []semanticid.Fingerprint
    DeadlineReached bool
}
```

A top-k parameter passed to a vector database can be semantic because candidates beyond `k` are never observed. It belongs in request identity. A token budget applied only to a post-merge prompt view belongs in view-policy identity, not fact identity.

The semantic location of a budget is more important than the word "budget".

## Mapping current subsystems

### Chunking and representations

Chunking produces source facts and seed derivations from document snapshots. Representation builders produce representation facts derived from chunk facts. Chunker configuration and representation model fingerprints belong in derivation configuration.

A changed overlap or tokenizer may change chunk boundaries and therefore facts. A changed worker count should not.

### Dense and sparse retrieval

Retrieval returns observations about canonical source facts. Dense and BM25 branches can attach different observations to one fact. Fusion can create a fused observation whose derivation-like inputs are the branch observations; the current kernel models observations without observation inputs, so the initial adapter may place branch references in payload. A future observation-provenance extension can make this relation typed.

### Connected retrieval

Connected retrieval may produce new facts or new derivations depending on whether graph traversal discovers source content or infers relationships. The RRF configuration fingerprint names the fusion view. Recursive traversal belongs in a future closure engine, but every frontier addition can already be admitted and merged lawfully.

### Knowledge extraction

Extracted claims are facts. Source chunks are premises. Extraction method, model, prompt, schema, and spans are derivation lineage. Confidence and ambiguity are observations. A claim supported by several chunks retains several derivations.

### Reranking

Reranking produces observations or a selected view, not new source facts. The reranker cache key includes input candidate identities and provider configuration. A reranked order should not overwrite retrieval observations.

### Tool-assisted answering

Tool outputs may become source facts, transformed facts, or observations depending on the tool contract. The deterministic ledger proves the candidate merge/selection pattern. Tool call arguments and tool version belong in derivation identity; network retry count does not.

### Generation

A generated answer can be represented as:

- an ephemeral presentation value only; or
- a generated-answer fact with a derivation from selected evidence, prompt template, and model configuration.

The second option supports proof-carrying experiment artifacts. It should not imply that the generated content is logically entailed unless the declared generation rule has that meaning.

### Experiments

Experiment artifacts should record:

- semantic request fingerprints;
- configuration fingerprints;
- canonical state fingerprint;
- selected-view policy and output;
- proof bundle for cited facts;
- operational trace separately;
- generated output and evaluator judgments;
- schema versions and code revision.

This permits replay to separate semantic differences from scheduler, latency, and trace differences.

## Backend independence

The in-memory state is one implementation. A relational backend might use:

```text
facts(id, variant_digest, kind, schema, payload)
derivations(id, variant_digest, output, rule, rule_version, ...)
derivation_inputs(derivation_id, variant_digest, role, fact_id)
observations(id, variant_digest, subject, kind, schema, payload)
```

with primary keys over `(id, variant_digest)`. Merge is `INSERT ... ON CONFLICT DO NOTHING` for exact variants. A query identifies conflicts by grouping on semantic ID with more than one variant digest.

A graph backend can store fact nodes and derivation hyperedge nodes. A content-addressed object store can store canonical records by variant digest and maintain ID-to-variant indexes.

Backend conformance requires:

$$
\operatorname{decode}(\operatorname{backendJoin}(A,B))
=
\operatorname{Join}(\operatorname{decode}(A),\operatorname{decode}(B)).
$$

P12 can implement this law across stores.

## Error semantics

Errors should be classified by boundary.

- **Plan error:** request cannot be assigned valid semantic identity.
- **Execute error:** effect failed; retry policy may apply.
- **Admission error:** raw result cannot be represented under the declared schema.
- **Merge conflict:** records claim one ID with different immutable content; retain and report.
- **Verification error:** state violates integrity or proof closure.
- **View error:** candidate or policy invalid against a verified state.
- **Generation error:** model invocation or output validation failed.

This classification avoids collapsing a semantic conflict into a transient execution error or treating malformed provider output as a valid empty result.

## Version registry

The growing set of domain/version pairs should be governed centrally. At minimum, each entry should record:

- owner package;
- preimage schema;
- field catalog;
- canonicalization policy;
- golden vectors;
- migration from previous version;
- cache/artifact retention period;
- privacy review;
- compatibility status.

A machine-readable registry can drive CI checks that reject unregistered fingerprint domains or version reuse after constructor changes.

## An elegant end-state

The proposed end-state is not a large abstraction tower. It consists of:

```text
semanticid.Value + Fingerprint
Fact + Derivation + Observation
State.Join + Ledger
Verify + ProofBundle
Candidate + SelectionPolicy + Select
small adapters at component boundaries
```

Everything else remains domain code. The elegance comes from making a few high-leverage laws universal across components.

# Evaluation

## Evaluation questions

The evaluation was designed to answer five different questions rather than collapse them into one "tests pass" result.

1. **Identity correctness:** do declared semantic mutations alter fingerprints while operational, presentation, and secret mutations do not?
2. **Provenance integrity:** can the implementation preserve alternate proofs and detect malformed or altered records?
3. **Merge lawfulness:** do all orderings, groupings, retries, and concurrent deliveries converge to one state?
4. **View determinism:** does merge-before-selection remove arrival-order dependence from budgets and citation labels?
5. **Implementation viability:** can the semantics be implemented without the repeated-clone cost of the reference persistent join?

## Artifact layout

The implementation produces:

```text
pkg/semanticid/
pkg/rag/derive/
cmd/semantic-foundations/
pkg/rag/derive/ragcodec/
pkg/rag/derive/knowledgecodec/
pkg/rag/toolanswer/deterministic_ledger.go
research/p01-p03-foundations/
```

The research handoff includes:

- design and report documents;
- public type aliases for the semantic kernel;
- a runnable demonstration script;
- identity catalogs;
- a machine-readable manifest;
- checksums;
- diamond, conflict, proof-bundle, selection, and evaluation fixtures;
- core test output;
- scaling results;
- static integration evidence.

## Standalone test execution

The final command was:

```bash
GO111MODULE=off GOPATH=/mnt/data/gopath \
  go test -race -v ./pkg/semanticid ./pkg/rag/derive
```

**EXECUTED.** The command passed. The package inventory contained 12 P01 tests and 17 P02/P03 core tests. `go vet` also completed without diagnostics for these packages.

The race-enabled run is relevant to P03 because it exercises the concurrent ledger test while Go's race detector instruments memory access. A race-free result does not prove the merge laws; the law tests and model address that separate property.

## P01 mutation matrix

The conformance request contained query, top-k, worker count, API key, display title, and an unordered collection set. The identity projection included query, top-k, and the collection set.

| Mutation | Role | Expected fingerprint change | Observed | Result |
|---|---|---:|---:|---|
| append text to query | semantic | yes | yes | pass |
| increment top-k | semantic | yes | yes | pass |
| add collection to set | semantic | yes | yes | pass |
| increment worker count | operational | no | no | pass |
| rotate API key | secret | no | no | pass |
| change display title | presentation | no | no | pass |

**EXECUTED.** The contract report passed.

Additional generated tests shuffled object fields and set inputs over 500 deterministic random trials. Every object and set permutation retained one fingerprint. List order remained distinguishing. Domain and version changes produced distinct fingerprints. Text and JSON representations of fingerprints round-tripped. Invalid floats, duplicate object fields, absolute/escaping paths, drive-qualified paths, and UNC paths were rejected.

## P02 diamond experiment

The diamond fixture was selected because it tests more than a linear provenance chain. One claim has two independent support paths, and two source facts carry independent retrieval observations.

The executed state fingerprint was recorded in the evaluation JSON. Counts were:

| Record class | Semantic IDs | Full variants |
|---|---:|---:|
| Facts | 3 | 3 |
| Derivations | 4 | 4 |
| Observations | 2 | 2 |

The verifier assigned both source facts rank zero and the claim rank one. The claim had two derivations. The proof bundle included all four derivations and verified independently.

The experiment then modified a source payload while retaining its original fact ID. Verification rejected the state. A second fault removed one source fact while retaining a derivation that referenced it. Verification reported a missing input.

**Interpretation.** The implementation distinguishes duplicate support from duplicate content and distinguishes content integrity from dependency integrity.

## P03 exhaustive merge experiment

The fixture was split into six deltas. The command enumerated all 720 permutations and folded each from the empty state.

| Measure | Result |
|---|---:|
| Merge deltas | 6 |
| Delivery permutations | 720 |
| Distinct canonical outputs | 1 |

**EXECUTED.** All permutations produced one canonical state.

The core test suite separately generated 500 triples of synthetic states and checked:

```text
Join(a, empty) == a
Join(empty, a) == a
Join(a, a) == a
Join(a, b) == Join(b, a)
Join(Join(a, b), c) == Join(a, Join(b, c))
```

Generated tests are not exhaustive over all states, but they test the implementation against the algebra rather than only one fixture.

## Conflict experiment

Two records were constructed with one semantic ID and different immutable payloads. The experiment merged them in both orders.

| Measure | Result |
|---|---:|
| Variants retained under the ID | 2 |
| Order-independent state | true |
| Verification conflict | true |

This case could have falsified the design if the state silently chose one variant or if variant order changed serialization.

## Concurrent retry experiment

The ledger received duplicate deltas from goroutines under the race detector. The conformance command repeated the scenario 100 times.

| Measure | Result |
|---|---:|
| Concurrent runs | 100 |
| Divergent final states | 0 |

This experiment tests the combination of synchronization and idempotent merge. It does not simulate process failure, distributed partitions, or nondeterministic worker outputs.

## Selection experiment

Three candidates were delivered in every possible order. The deterministic policy selected from the merged state. A legacy baseline accepted the first two arrivals.

| Policy | Completion permutations | Distinct views |
|---|---:|---:|
| Merge, total sort, then budget | 6 | 1 |
| First two arrivals | 6 | 6 |

**EXECUTED.** The selection barrier removed the scheduling dependency in this fixture.

Core tests also established:

- exact retry candidates are ignored;
- state bytes are unchanged by selection;
- at most one candidate is emitted per fact;
- ties are resolved by a total stable comparator;
- candidate observations must exist and refer to the candidate fact.

## Performance scaling

The scaling experiment inserted synthetic facts one at a time. The persistent implementation cloned accumulated state at every insertion. The mutable ledger performed in-place union and returned a snapshot only at the end.

Every measured pair produced equal canonical output. The median values are reported in Chapter 7 and the machine-readable scaling artifact.

The observed shape is expected from implementation structure:

- repeated cloning copies a growing number of map entries, producing approximately quadratic total work for this workload;
- in-place insertion performs approximately constant expected map work per new variant, excluding resizing and final snapshot cost.

This is an implementation result, not a new algebraic property. It supports the decision to provide both a persistent reference and mutable builder.

## Static production validation

The changed repository was parsed after formatting. Generation and reranking call sites were enumerated and checked for updated constructor arities after provider fingerprint parameters were added. Source-level tests were added for the modified cache and runtime paths.

**STATIC.** Confirmed code changes include:

1. fallback evidence text identity now uses the canonical text digest;
2. connected runtime fingerprint includes RRF algorithm and constant and uses version `v2`;
3. resolved provider configuration receives a redacted fingerprint;
4. generation cache keys require provider fingerprint and use `v2`;
5. reranking cache keys require provider fingerprint and use `v2`;
6. current production callers pass role-specific configuration fingerprints;
7. current chunks, representations, evidence, and knowledge facts have semantic adapters;
8. tool evidence has a deterministic ledger alternative.

The standalone tests for `ragcodec`, provider bundles, connected runtime, cache packages, and toolanswer could not be executed as part of the full module under the available Go version. They are source-level implementation claims pending integration validation.

## Full repository test attempt

The final full test attempt was:

```bash
GOTOOLCHAIN=local go test ./...
```

It failed before compilation because Go 1.23.2 did not understand the repository's module `tool` block:

```text
go: errors parsing go.mod:
go.mod:187: unknown block type: tool
```

This failure is not evidence of a code defect in the patches. It is also not evidence that the patches integrate successfully. The correct conclusion is narrower: the complete integration claim remains unverified in the available environment.

## Hypothesis outcomes

The P01-P03 briefs were framed with falsifiable hypotheses. The implemented outcomes are summarized below.

| Hypothesis | Outcome | Evidence class |
|---|---|---|
| Explicit semantic projection can distinguish behavior from operations | supported in tested catalog | executed |
| Current code contains at least one behavior-affecting identity omission | supported: RRF and provider configuration | static |
| Facts can remain stable across changed scores/ranks | supported | theorem + executed |
| One fact can retain multiple independent derivations | supported | executed fixture |
| Verifier can detect altered and incomplete proof artifacts | supported for tested faults | executed |
| Set-union state satisfies ACI merge laws | proved for model; supported in code | theorem + executed |
| Delivery order and retry can be removed from canonical-state meaning | supported under fixed deltas | theorem + executed |
| Admission-time limits cause observable order dependence | supported by six-view counterexample | executed |
| Mutable ingestion can preserve semantics at lower cost than repeated cloning | supported in tested workload | empirical |

No hypothesis establishes answer quality. The thesis concerns semantic stability and auditability.

## Acceptance against project briefs

### P01 acceptance

- standalone identity model: complete;
- explicit field catalog: complete;
- mutation matrix: complete;
- adversarial canonicalization cases: complete;
- generated law tests: complete;
- repository identity patches: implemented, statically validated;
- full adapter integration: pending declared-toolchain execution.

### P02 acceptance

- fact/derivation/observation kernel: complete;
- one fact with several derivations: complete;
- diamond fixture: complete;
- malformed bundle/tamper checks: complete;
- proof bundle: complete;
- `rag` and knowledge adapters: implemented, static integration pending;
- independent schema package and fixtures: complete.

### P03 acceptance

- ACI join: complete;
- exhaustive order experiment: complete;
- generated laws: complete;
- conflict retention: complete;
- concurrent retry test: complete;
- deterministic selection: complete;
- legacy counterexample: complete;
- toolanswer adapter: implemented, static integration pending;
- mutable ledger performance experiment: complete.

## Interpretation

The strongest result is not any individual test count. It is the elimination of three hidden variables from canonical evidence meaning:

```text
map/serialization order
worker delivery order
query-local observation fields
```

The remaining variability becomes explicit:

```text
semantic request/configuration changes
external data changes
provider nondeterminism
conflicting producer output
selection-policy changes
partial execution/completeness
```

That boundary is the basis for later composition experiments.

# Consolidated formal semantics

## Purpose of the model

This chapter collects the formal results in one place. The goal is not abstraction for its own sake. The definitions are chosen so that each theorem corresponds to an API invariant or test.

The model has three layers:

1. semantic naming;
2. provenance records and state;
3. deterministic interpretation of a state as a selected view.

## Semantic naming

Let $\mathcal{V}$ be the set of valid typed semantic values generated by:

$$
v ::= \text{null} \mid \text{bool}(b) \mid \text{string}(s)
\mid \text{bytes}(x) \mid \text{int}(n) \mid \text{uint}(n)
\mid \text{float}(q) \mid \text{list}(v_1,\ldots,v_n)
\mid \text{set}\{v_1,\ldots,v_n\}
\mid \text{object}\{k_1:v_1,\ldots,k_n:v_n\}.
$$

Validity imposes finite floats, unique object keys, valid UTF-8 strings and keys, and constructor-specific normalization.

Let $C:\mathcal{V}\to\{0,1\}^{*}$ be the canonical byte encoder. Let $E(D,V,v)$ be the domain envelope containing a fixed prefix and length-separated domain, version, and $C(v)$.

Let:

$$
\operatorname{fp}(D,V,v)=\operatorname{SHA256}(E(D,V,v)).
$$

The implementation's textual identifier includes $D$, $V$, algorithm name, and digest.

### Lemma 10.1 - prefix decodability

**THEOREM.** Every canonical value encoding has one valid parse into its constructor and children.

This is the decoding form of Theorem 5.2. It follows from kind tags, canonical varints, collection counts, and explicit child lengths.

### Lemma 10.2 - canonical set quotient

Define $L$ as a finite list of values and $[L]_{set}$ as the equivalence class under permutation and duplicate insertion. The `Set` constructor maps every member of $[L]_{set}$ to the same canonical value.

**Proof.** Each element maps to its canonical bytes. Sorting removes permutation, and adjacent duplicate removal removes multiplicity. QED.

### Lemma 10.3 - canonical object quotient

Define objects as finite unique-key maps. Any two enumerations of the same key/value map produce the same canonical value because construction sorts by key. QED.

## Identity projections

A runtime structure $X$ generally has more fields than its semantic identity. An identity contract is a function:

$$
P:X\to\mathcal{V}.
$$

A field mutation $m:X\to X$ is:

- identity-preserving when $P(m(x))=P(x)$;
- identity-changing when $P(m(x))\neq P(x)$.

The mutation harness compares fingerprints, so its result is conditional on hash collision resistance. At the contract level, the intended law is about $P$.

### Proposition 10.4 - catalog consistency

The implemented catalog validator enforces:

- every declared semantic or lineage field is included;
- no declared operational, presentation, or secret field is included;
- every field path is unique;
- observation participation is explicit.

This does not prove that every runtime field appears in the catalog. A reflection- or code-generation-based completeness check is future work.

## Record spaces

Let $F$, $D$, and $O$ be the sets of all valid complete fact, derivation, and observation records. Let:

$$
id_F:F\to I_F,
\quad id_D:D\to I_D,
\quad id_O:O\to I_O
$$

be their fingerprint functions.

A fact is a tuple:

$$
f=(kind,schema,payload).
$$

A derivation is:

$$
d=(output,rule,ruleVersion,inputs,request,config,attributes).
$$

An observation is:

$$
o=(kind,schema,subject,request,payload).
$$

IDs are stored in records for transport, but validity requires equality with recomputation.

## Variant-aware state

For a record $r$, define its full record digest $vr(r)$ over canonical serialization including its claimed semantic ID. This digest distinguishes complete transport variants.

A state is:

$$
S=(S_F,S_D,S_O)
$$

where, for example:

$$
S_F:I_F\to\mathcal{P}_{fin}(F)
$$

with every $f\in S_F(i)$ claiming `f.ID = i`. Empty buckets are omitted in implementation.

A bucket is:

- absent if cardinality zero;
- unconflicted if cardinality one;
- conflicted if cardinality greater than one.

The unambiguous projection $U_F(S)$ contains only the unique record in each unconflicted fact bucket. Similar projections exist for derivations and observations.

## Join and order

Define join pointwise by union. Define information order:

$$
S\preceq T \iff S\sqcup T=T.
$$

Equivalently, every variant in every bucket of $S$ also occurs in $T$.

### Theorem 10.5 - partial order

**THEOREM.** $\preceq$ is reflexive, antisymmetric, and transitive.

**Proof.** Reflexivity follows from idempotence. If $S\sqcup T=T$ and $T\sqcup S=S$, commutativity gives $S=T$, establishing antisymmetry. If $S\sqcup T=T$ and $T\sqcup U=U$, then by associativity $S\sqcup U=S\sqcup(T\sqcup U)=(S\sqcup T)\sqcup U=T\sqcup U=U$, establishing transitivity. QED.

### Theorem 10.6 - least upper bound

**THEOREM.** $S\sqcup T$ is the least state containing both $S$ and $T$ under $\preceq$.

**Proof.** Union contains both operands. Any upper bound containing every variant of both operands also contains their union. QED.

This theorem gives the term "join" its precise meaning.

## Deterministic fold over deltas

Let $M=[\Delta_1,\ldots,\Delta_n]$ be a finite multiset of deltas. Define:

$$
\operatorname{fold}(M)=\bigsqcup_{i=1}^{n}\Delta_i.
$$

Because the operation is commutative and associative, this is well-defined independently of list order and parenthesization. Because it is idempotent, multiplicity is irrelevant. The result depends only on the set of distinct complete record variants delivered.

### Theorem 10.7 - operational quotient

Consider execution traces equivalent when they differ only by:

- permutation of delta deliveries;
- batch regrouping;
- insertion or removal of duplicate deltas;
- insertion or removal of duplicate records within a delta.

**THEOREM.** `fold` is constant on every such equivalence class.

This is the formal expression of schedule, batching, and retry independence.

## Conflict preservation

Let $r_1\neq r_2$ be two complete records with the same claimed semantic ID $i$. Let $S_1$ contain $r_1$ and $S_2$ contain $r_2$.

### Theorem 10.8 - conflict invariance

**THEOREM.** Both $S_1\sqcup S_2$ and $S_2\sqcup S_1$ contain exactly the variant set $\{r_1,r_2\}$ at $i$.

**Proof.** Directly from set union and commutativity. QED.

### Corollary 10.9 - no timing-based conflict resolution

No delivery schedule can make a well-formed join choose only one of the conflicting variants.

This property is stronger than deterministic first-writer-wins. First-writer-wins can be deterministic only after imposing an external total order on writers; it still discards information and changes the state algebra.

## Verification relation

Define `Valid(S)` when all of the following hold:

1. every bucket is unconflicted;
2. every record ID equals its recomputed ID;
3. every derivation output and input names an unconflicted fact;
4. every observation subject names an unconflicted fact;
5. every fact has at least one derivation;
6. every fact has at least one finite well-founded derivation tree.

The implementation reports all discoverable violations rather than returning only a Boolean.

### Proposition 10.10 - validity is not monotone under raw join

Even though state information is add-only, `Valid` is not monotone. A valid state can become invalid when a conflicting variant is added.

This is intentional. Monotone accumulation preserves evidence, including evidence of inconsistency. Validation is an observation over the accumulated state, not the merge operation itself.

The distinction prevents a common misconception: add-only does not mean every derived predicate remains true. It means records are not silently removed.

## Proof-rank operator

For a fixed unconflicted provenance graph, define an operator $T$ on partial rank maps $R:F\rightharpoonup\mathbb{N}$. `T(R)` contains every rank already in $R$ and every derivation candidate whose inputs are ranked, retaining the least candidate per output.

Starting from the empty map:

$$
R_0=\varnothing,
\quad R_{n+1}=T(R_n).
$$

For a finite state, repeated relaxation reaches a fixed point. The result is the least finite proof-rank map, as established in Theorems 6.1 and 6.2.

This is the first point where P01-P03 connect to the broader fixed-point RAG model. The current kernel computes closure over proof ranks for an already admitted finite state. P05 can generalize the same pattern to recursive rule execution and frontier expansion.

## Proof bundles as substate closure

For selected fact set $Q$, define backward support closure $B_S(Q)$ as the least substate containing:

- every fact in $Q$;
- every derivation in $S$ whose output is included;
- every input fact of included derivations;
- observations whose subjects are included.

`BuildProofBundle` computes this closure by a queue over facts.

### Theorem 10.11 - support closure

**THEOREM.** If `S` is valid and every selected fact is in `S`, then every derivation in `B_S(Q)` has its output and all inputs in `B_S(Q)`.

**Proof.** A derivation is included only when its output fact is included. When included, every input is enqueued and eventually included. Because the state is finite, the queue terminates after each fact is processed once. QED.

### Corollary 10.12 - independently verifiable bundle

If the serialized bundle is unaltered and uses the declared schema, reconstructing its state and running `Verify` establishes the same structural integrity properties as for an ordinary state.

The statement remains conditional on the identity hash and on trust in the verifier implementation.

## Observation projection

Let $forget_O(S)$ remove all observation buckets. Fact and derivation IDs and records remain unchanged.

### Theorem 10.13 - fact/proof stability under observations

For any states $S$ and observation-only delta $O$:

$$
forget_O(S\sqcup O)=forget_O(S).
$$

**Proof.** Observation-only deltas have empty fact and derivation components. Componentwise union changes only the observation component. QED.

This theorem justifies reusing canonical facts and proofs across rerankers and requests.

## Deterministic view function

Let a candidate be a tuple:

$$
c=(fact,observation,key,utility,units).
$$

The candidate key function is a P01 fingerprint of the complete tuple. Let `dedup(C)` be the set of candidates by this key. Let `sort(C)` use the total comparator. Let `scan_P` enforce one-per-fact and policy budgets, then assign deterministic ranks and labels.

Define:

$$
View_P(S,C)=scan_P(sort(dedup(C))).
$$

when all candidates validate against $S$.

### Theorem 10.14 - view permutation invariance

For every candidate-list permutation $\pi$:

$$
View_P(S,C)=View_P(S,\pi(C)).
$$

The proof is Theorem 7.9.

### Proposition 10.15 - view is intentionally non-monotone

There exist $C\subset C'$ such that the selected facts in `View(S,C)` are not a subset of those in `View(S,C')` under a finite budget.

Example: a new higher-utility candidate displaces a previous selection. Therefore the view must not be confused with canonical state growth.

## Composable interpreters

A consumer can be viewed as a function from verified state to another representation:

$$
h:S\to A.
$$

Examples include a relational snapshot, provenance graph, prompt context, audit report, or citation package.

A consumer preserves merge when:

$$
h(S\sqcup T)=h(S)\oplus h(T)
$$

for a suitable target merge $\oplus$. Such a function is a join homomorphism. Backend and serialization adapters should satisfy this law when they claim to preserve canonical state.

Ranking and bounded prompt selection are not join homomorphisms because they are non-monotone. They belong after merge.

## Cache composition theorem

Let $K:X\to I$ be a semantic fingerprint projection for requests, $E:X\to S$ be execution plus admission, and `Cache` return a previously stored state by $K(x)$.

### Conditional theorem 10.16 - cache replacement

If:

$$
K(x)=K(y) \implies E(x)=E(y)
$$

and cached serialization round-trips exactly, then replacing `E(x)` with a cache lookup by `K(x)` preserves every later computation that is a function of the admitted state.

**Proof.** The premise gives equal admitted states for equal keys. Substitution into any deterministic downstream function preserves equality. QED.

This theorem makes key completeness the core cache proof obligation.

## Composition of P01-P03

The three projects form a proof chain:

1. P01 defines the identifiers and complete-record canonicalization assumptions.
2. P02 constructs provenance records using those identifiers.
3. P03 merges sets of those complete records.
4. P02 verification recomputes P01 identities after P03 merge.
5. P03 selection references unconflicted P02 facts and observations.

A defect in an earlier layer weakens later theorems. For example:

- incomplete fact identity can merge semantically different facts;
- unstable derivation identity can duplicate one proof;
- overwrite merge can erase P02 alternate derivations;
- admission-time ranking can make P03 output schedule-dependent;
- incomplete cache identity can change the set of deltas before lawful merge.

The system is rigorous because these dependencies are explicit, not because any one package is complicated.

## Relationship to established constructions

The state join is the standard finite powerset union construction used in grow-only replicated data types. Associative, commutative, and idempotent merge is the algebraic foundation of state-based convergence when all replicas eventually receive all updates.

The add-only boundary also aligns with the CALM principle: monotone information accumulation is the part of a distributed computation that can be coordinated without retracting earlier conclusions. The selected top-k view is non-monotone and is therefore placed behind an explicit snapshot/coordination boundary.

The fact/derivation/observation model is compatible in spirit with provenance standards that distinguish entities, activities, and agents, although the kernel deliberately uses a smaller domain-specific schema. A derivation is analogous to an activity relation that generated an entity from used entities. The thesis does not claim complete W3C PROV conformance.

The least proof-rank computation is a finite fixed-point construction. Later recursive retrieval can extend it to ordinal-indexed closure, but no genuinely transfinite execution is needed for P01-P03.

# Engineering handbook and adoption plan

## Package map

The implementation separates general semantics from repository-specific adapters.

### `pkg/semanticid`

| File | Responsibility |
|---|---|
| `value.go` | typed semantic values, canonical binary encoding, set/object normalization, portable paths |
| `fingerprint.go` | domain/version validation, SHA-256 fingerprinting, text and JSON round trips |
| `contract.go` | field roles, catalogs, mutation-contract reports |
| `value_test.go` | encoding laws, generated permutations, paths, float policy, golden vector |
| `contract_test.go` | catalog and mutation tests |
| `doc.go` | package contract and usage guidance |

### `pkg/rag/derive`

| File | Responsibility |
|---|---|
| `canonical_json.go` | `derive-json-v1` normalization |
| `types.go` | facts, derivations, observations, constructors and IDs |
| `state.go` | variant-aware state, join, snapshots, conflicts, mutable ledger |
| `verify.go` | integrity, closure, finite proof ranks |
| `proof.go` | proof-bundle extraction and verification |
| `select.go` | deterministic post-merge selection |
| tests | canonicalization, facts, proof, merge laws, concurrency, selection |

### Adapters

| Path | Responsibility |
|---|---|
| `pkg/rag/derive/ragcodec` | current chunks, representations, and evidence to kernel records |
| `pkg/rag/derive/knowledgecodec` | current knowledge facts to claims, derivations, and observations |
| `pkg/rag/toolanswer/deterministic_ledger.go` | tool-evidence admission followed by deterministic finalization |

### Conformance and handoff

| Path | Responsibility |
|---|---|
| `cmd/semantic-foundations` | executable P01-P03 experiments and fixture generation |
| `research/p01-p03-foundations` | design, report, API aliases, demo, schemas, fixtures, results, checksums |

## Public identity API

A typical identity constructor should look like:

```go
func requestFingerprint(req Request) (semanticid.Fingerprint, error) {
    collections := make([]semanticid.Value, len(req.Collections))
    for i, c := range req.Collections {
        collections[i] = semanticid.MustString(c)
    }

    value := semanticid.MustObject(
        semanticid.Field{
            Name:  "query",
            Value: semanticid.MustString(normalizeQuery(req.Query)),
        },
        semanticid.Field{
            Name:  "collections",
            Value: semanticid.Set(collections...),
        },
        semanticid.Field{
            Name:  "provider_configuration",
            Value: semanticid.MustString(req.ProviderFingerprint),
        },
    )
    return semanticid.FingerprintValue(
        "rag.example.request",
        "v1",
        value,
    )
}
```

Reviewers should be able to compare this constructor directly with a field catalog.

Avoid these patterns:

```go
// Ambiguous: struct changes silently alter or fail to alter identity.
digest.JSON(req)

// Ambiguous: delimiter collisions and type loss are possible.
sha256(query + ":" + model + ":" + strconv.Itoa(k))

// Incomplete: model label does not identify resolved behavior.
cacheKey(query, providerName, modelName)
```

## Public provenance API

The basic usage is:

```go
source, err := derive.NewFact(
    "source-chunk",
    "rag.chunk/v1",
    map[string]any{
        "document": "doc-17",
        "span":     "120:260",
        "text":     "...",
    },
)
if err != nil { return err }

seed, err := derive.NewSeedDerivation(
    source.ID,
    "corpus",
    "v1",
    requestID,
    corpusFingerprint,
    map[string]any{"locator": "doc-17#120:260"},
)
if err != nil { return err }

score, err := derive.NewObservation(
    "retrieval-score",
    "rag.score/v1",
    source.ID,
    requestID,
    map[string]any{
        "method": "dense",
        "rank":   3,
        "score":  0.82,
    },
)
```

The records can be inserted in any order into a delta state, but the state is not valid until all dependencies and proofs are present.

## Public merge API

For immutable composition:

```go
combined := derive.Join(left, right)
```

For concurrent ingestion:

```go
ledger := derive.NewLedger(initial)

// Safe to call from several goroutines.
conflicts := ledger.Merge(delta)

snapshot := ledger.Snapshot()
report := derive.Verify(snapshot)
```

Callers must not interpret an empty `conflicts` slice as proof that the entire state is valid. It reports conflicts affected by the merged delta; full validation is a separate operation.

## Public selected-view API

```go
selected, err := derive.Select(
    verifiedState,
    candidates,
    derive.SelectionPolicy{
        Version:     "citation-selection-v1",
        MaxItems:    12,
        MaxUnits:    6000,
        LabelPrefix: "E",
    },
)
```

The policy version should change when comparator, deduplication, budget, or label semantics change. A complete view fingerprint can include:

- state fingerprint;
- candidate-set fingerprint;
- selection-policy fingerprint;
- tokenizer/configuration fingerprint if units are tokens.

## Constructor discipline

Canonical records should normally be created through constructors, not struct literals. Constructors perform:

- whitespace and required-field checks;
- JSON normalization;
- input sorting;
- finite-number checks;
- ID calculation.

Struct literals remain possible for decoding and adversarial tests. `Verify` exists because transport values cannot be assumed to have come through trusted constructors.

A future version can make fields private and expose custom JSON decoding, but that would increase adapter complexity. The current balance favors transparent interchange plus explicit verification.

## Schema discipline

Every fact and observation payload has a schema string. Schemas should be small and domain-owned. A schema definition should include:

- required fields and types;
- semantic equality policy;
- Unicode and whitespace policy;
- units and numeric policy;
- whether order matters in arrays;
- migration rules;
- examples and counterexamples.

JSON Schema can validate shape, but it does not fully specify semantic identity. The identity catalog and constructor remain necessary.

## Semantic ID governance checklist

Before adding or changing a fingerprint:

1. Name the entity or operation being identified.
2. List every input field and classify its role.
3. Decide list/set/object behavior for every collection.
4. Decide absent versus zero/empty behavior.
5. Decide path, case, whitespace, Unicode, number, and time normalization.
6. Include source/configuration snapshots that change behavior.
7. exclude raw secrets unless there is a documented requirement;
8. choose a domain and new version;
9. add at least one golden vector;
10. add positive and negative mutation cases;
11. define old-version migration or invalidation;
12. document privacy and dictionary-attack implications.

## Cache-key governance checklist

A cache review should ask:

- Can two executions share the key but legally admit different records?
- Is every external mutable resource represented by an immutable snapshot ID?
- Is authorization scope represented?
- Does the key identify the adapter and schema version, not only the provider call?
- Are stochastic controls included?
- Are prompt templates and tool definitions included where relevant?
- Does a secret rotation preserve behavior and tenancy?
- Is the cache value raw provider output or admitted semantic state?
- Can old values be decoded after a schema change?

The safest cache value for composition is often an admitted delta with its own state fingerprint and verification report. Raw output caches remain useful when admission logic evolves, but then adapter version must be part of the semantic operation identity.

## Provenance design checklist

For every new fact kind:

1. Define canonical content.
2. Identify source/import derivations.
3. Identify transformation rules and versions.
4. Define input roles.
5. Separate confidence, rank, score, and selection status into observations.
6. Decide whether request ID belongs in derivation identity or an execution event.
7. Define proof-bundle expectations.
8. Define deletion dependencies.
9. Define authorization inheritance.
10. Define temporal validity if facts can expire.

## Merge design checklist

For any new state component:

- What is the semantic ID?
- What is the complete record variant key?
- Is addition set-like, multiset-like, or replacement-like?
- Does exact retry change state?
- What happens under same ID/different content?
- Is serialization deterministic?
- Can a backend implement union without hidden overwrite?
- Is any top-k, first-N, or quota being applied before global merge?
- Does conflict handling preserve evidence?

Only add-only set-like components should enter the canonical join directly. Counters, last-seen timestamps, or mutable statuses need separate algebra or observation/event records.

## CI test matrix

A production CI pipeline should separate fast semantic tests from full integration tests.

### Fast, dependency-light stage

```bash
GO111MODULE=off GOPATH="$GOPATH" \
  go test -race ./pkg/semanticid ./pkg/rag/derive
```

Required checks:

- golden vectors;
- generated canonicalization laws;
- mutation matrices;
- join ACI laws;
- proof verification;
- selection permutation tests;
- race detector.

### Module integration stage

Run with the repository-declared Go toolchain:

```bash
go test ./pkg/rag/connected/...
go test ./pkg/rag/generation/...
go test ./pkg/rag/reranking/...
go test ./pkg/rag/providers/geppetto/...
go test ./pkg/rag/toolanswer/...
go test ./pkg/rag/derive/ragcodec/...
go test ./pkg/rag/derive/knowledgecodec/...
```

### Full repository stage

```bash
go test ./...
go vet ./...
```

### Artifact stage

```bash
go run ./cmd/semantic-foundations \
  --output results/evaluation.json \
  --artifact-dir results/artifacts
sha256sum -c research/p01-p03-foundations/CHECKSUMS.sha256
```

### Compatibility stage

- compare golden vectors against released versions;
- reject changed bytes under an unchanged version;
- test dual-read migrations;
- validate that old caches are invalidated or decoded intentionally;
- run backend conformance over common fixtures.

## Observability

Operational traces should refer to semantic IDs without being included in those IDs.

Useful trace fields include:

```text
request_semantic_id
configuration_fingerprint
admitted_state_fingerprint
fact_id
derivation_id
observation_id
worker_id
attempt_number
cache_hit
batch_id
admission_error
conflict_count
verification_issue_codes
selected_view_fingerprint
```

This structure permits queries such as:

- Did two different schedules admit the same state?
- Did a cache hit return the same state as a later fresh execution?
- Which producer first introduced a conflicting variant?
- Which selection policy changed citation labels?
- Did answer quality change while canonical evidence stayed constant?

Do not use human-readable display names as unique execution identity. Names can remain labels attached to stable IDs.

## Migration plan

A safe migration avoids replacing all current types at once.

### Phase 0 - reproduce and baseline

- obtain the declared Go toolchain;
- run the full unmodified test suite;
- run existing experiment baselines;
- archive current cache-key golden vectors and representative artifacts;
- add integration CI for the new standalone packages.

### Phase 1 - identity fixes and cache namespace change

- deploy the canonical text-digest correction;
- deploy connected runtime `v2` fingerprints;
- deploy provider configuration fingerprints;
- use generation and reranking cache `v2` namespaces;
- do not read `v1` values unless an explicit migration proves compatibility;
- monitor cache hit rate and output divergence.

A temporary dual-key logger can compute old and new keys without serving old values. It should report cases where one old key maps to several new keys; those are evidence of prior under-identification.

### Phase 2 - dual admission

At selected boundaries, keep producing existing `rag.Evidence` while also admitting canonical records:

```text
current result -> existing consumers
              -> ragcodec -> semantic ledger -> audit artifact
```

Compare:

- current evidence count versus canonical fact count;
- legacy IDs versus new fact IDs;
- duplicate paths merged;
- scores/ranks retained as observations;
- conflicts and malformed records;
- proof closure.

No production behavior changes in this phase.

### Phase 3 - canonical experiment artifacts

Add state fingerprints, proof bundles, and selected-view records to experiments. Use them to classify differences:

```text
same state, different view       -> ranking/policy difference
same view, different answer      -> generation difference
new state                        -> retrieval/admission/configuration difference
invalid state                    -> identity/provenance defect
```

This phase provides high diagnostic value with low serving risk.

### Phase 4 - deterministic tool evidence

Switch tool-answer candidate accumulation to the deterministic ledger behind a feature flag. Run completion-order permutation tests and shadow comparisons. Expect citation labels and selected subsets to change in scenarios where the previous behavior depended on arrival.

Record both views during evaluation; do not assume legacy output is the ground truth.

### Phase 5 - canonical retrieval views

Move dense, sparse, knowledge, and connected results toward facts plus observations. Merge branch outputs before fusion/selection where policy permits. Keep branch-specific observations for explainability.

### Phase 6 - backend storage

Introduce a durable variant-aware backend with conformance tests. In-memory state remains the reference oracle for small fixtures.

### Phase 7 - recursive closure and updates

Build P05 and P11 on the same fact IDs, derivations, and join. Add frontier state, completion contracts, delta maintenance, and dependency-aware retraction.

## Cache migration details

Changing a cache-key version creates three options.

1. **Cold namespace.** Safest; old entries are ignored.
2. **Verified promotion.** Decode an old entry, reconstruct all missing semantic inputs, compute the new key, and promote only if equivalence is established.
3. **Dual execution audit.** Serve new execution while comparing old cached output offline.

Blindly copying `v1` values into `v2` defeats the purpose of the correction.

Provider configuration fingerprinting should be logged only as the fingerprint, never with the raw projected settings. The redacted projection may still reveal structure if persisted.

## Conflict operations

A production system needs explicit conflict workflows.

### Detection

- verifier issue `identity-conflict`;
- metrics by namespace and producer configuration;
- alert on first occurrence for content-derived IDs.

### Quarantine

- exclude conflicted facts from selected views;
- preserve all variants and derivations in an audit store;
- prevent proof bundles from claiming validity.

### Diagnosis

- recompute semantic IDs from every variant;
- identify whether one record has a stale or malformed ID;
- compare schema and canonicalization versions;
- inspect producer request/configuration fingerprints;
- detect hash-domain reuse.

### Resolution

Resolution should produce new explicit records rather than mutate history invisibly. Examples:

- migrate malformed records to corrected IDs;
- issue a new schema version;
- add an adjudication fact and derivation;
- revoke a producer configuration;
- retain a tombstone/retraction event in P11.

## Performance engineering

The reference data structures favor semantic transparency. Production scaling should preserve the same contracts while changing representation.

Potential optimizations include:

- mutable builders with immutable snapshots;
- sharded ledgers by record namespace and ID prefix;
- copy-on-write maps;
- persistent hash-array mapped tries;
- batched sorting at snapshot time;
- database uniqueness constraints over `(semantic_id, variant_digest)`;
- incremental conflict counters;
- incremental verification of newly affected proof regions;
- compact binary snapshots;
- proof-bundle policies selecting minimal or diverse proofs;
- observation retention policies by request or experiment.

Each optimization must be tested against the reference join and canonical fixtures.

## Security and privacy

Content-addressed IDs can leak information through dictionary attacks. Hashing a secret or sensitive short string does not make it safe. The system should:

- avoid raw secret fields in fingerprints;
- avoid exposing content fingerprints across unauthorized boundaries when an attacker can guess content;
- include tenant/authorization scope when cross-tenant cache reuse is forbidden;
- encrypt sensitive payloads at rest independently of identity;
- sign artifacts if origin authenticity is required;
- propagate authorization labels through derivations in P13;
- treat proof bundles as potentially sensitive because they reveal source relationships.

A globally stable source fact ID can be valuable for deduplication but unsafe for privacy if it permits cross-tenant correlation. A deployment may use tenant-scoped identity domains or keyed hashes while preserving the same canonical value model.

## Governance and review roles

Semantic versions should have explicit owners.

- Component owners define behavioral fields.
- Security reviewers approve secret and tenancy handling.
- Data/schema owners define canonical payloads.
- Infrastructure owners implement merge backends.
- Experiment owners preserve artifact compatibility.
- CI enforces golden vectors and law suites.

A version change should be reviewed like an API change, not a hash implementation detail.

## Definition of adoption success

The kernel is successfully adopted when maintainers can answer these questions from artifacts rather than intuition:

- Which semantic input changed?
- Did retrieval admit a different fact set?
- Did only scores or ranks change?
- Were two independent proofs merged?
- Did retry duplicate information?
- Did worker completion order affect the selected view?
- Is a cache hit valid under the resolved provider configuration?
- Is every cited fact present in a verifiable proof bundle?
- Did a backend migration preserve canonical state?

The objective is not to maximize formal vocabulary. It is to make these operational questions decidable.

# Limitations and threats to validity

## Integration validity

The largest practical limitation is the unavailable repository toolchain. The semantic packages were intentionally isolated and executed, but production adapters and cache changes depend on packages that were not compiled in the full module.

Static parsing and call-arity checks reduce syntax and obvious migration risk, but they do not detect:

- imported API changes in dependencies;
- type mismatches hidden by unavailable packages;
- runtime initialization behavior;
- provider settings that fail JSON projection;
- database/cache integration errors;
- command-specific build tags;
- tests relying on Go 1.26 behavior;
- semantic regressions in existing end-to-end experiments.

The first follow-up action is therefore full CI under Go 1.26.5 or the repository's actual supported toolchain. No production deployment should rely solely on the standalone evidence.

## Model-to-code correspondence

The join theorems apply to mathematical set union. The Go implementation corresponds closely: inner maps are sets keyed by full record digest and merge assigns each variant into those maps. The tests exercise this correspondence.

Still, formal verification of the Go implementation was not performed. Possible defects outside tested paths include:

- a clone method omitting a future field;
- a serializer changing behavior under a new Go release;
- a constructor not applying a canonicalization helper;
- integer overflow in a future budget calculation;
- resource exhaustion under adversarial inputs;
- accidental mutation through a newly exposed slice or map.

The code copies JSON bytes and input slices at important boundaries, but Go does not provide deep immutability by default.

## Hash assumptions

The system uses SHA-256 as a compact identity. The formal properties are conditional on collision resistance. The verifier's conflict model can expose same-ID/different-record variants if both are delivered, but a malicious collision could cause semantically different records to share an ID intentionally.

Applications requiring adversarial cryptographic assurance should consider:

- signed records;
- a stronger or configurable hash suite;
- algorithm agility in textual IDs;
- keyed hashes for tenant isolation;
- collision-response procedures;
- full canonical bytes retained alongside fingerprints.

The `sid1` textual format includes the algorithm name, but the current parser supports only SHA-256.

## Canonical JSON policy

`derive-json-v1` is deliberately local and deterministic, but it has limits.

### Not RFC 8785

It does not claim compatibility with the JSON Canonicalization Scheme. Its number representation expands exponents into plain decimals and uses Go's string escaping behavior. Interoperating implementations must implement this exact version or exchange already canonical bytes.

### Resource expansion

The parser permits exponents within a bounded range, but canonicalization can still expand a compact exponent into a large decimal string. A hostile input can consume memory. Production admission should impose input-size and normalized-output-size limits.

### Unicode policy

Object names are sorted by Go string order and strings are not Unicode-normalized. Two visually equivalent sequences can receive different fact IDs. This may be correct for source fidelity but should be explicit in schemas that handle user text.

### JSON type limitations

JSON cannot natively distinguish integers from arbitrary-precision decimals after schema interpretation, byte arrays from base64 strings, timestamps from strings, or sets from lists. Fact schemas must define those meanings. The P01 typed value language is richer for identity constructors, but fact payloads remain JSON for interoperability.

## Semantic projection completeness

A field catalog is only as complete as its maintenance. The generic contract harness cannot mutate a field that the author forgot to list. Provider settings are particularly dynamic and vendor-specific.

Mitigations include:

- code generation from configuration structs;
- reflection-based field inventory tests;
- compile-time builders rather than arbitrary maps;
- snapshot tests over resolved settings;
- dual-execution audits after provider upgrades;
- default cache invalidation on unknown fields;
- ownership and review of identity catalogs.

The conservative provider projection is an interim strategy. It reduces under-identification but can over-invalidate and cannot establish that field-name redaction finds every credential.

## Secret handling

Raw credentials are removed from the provider projection by key-name heuristics. This is not a general secret-taint system. A secret in a field with an unexpected name can enter the hash preimage. Although the raw value is not emitted, a fingerprint of a low-entropy secret can be attacked by enumeration.

Conversely, replacing a credential with a presence marker assumes credential rotation does not change semantic access. If two keys grant different tenants, datasets, regions, or model features, an authorization or account identity must participate explicitly.

The correct long-term design is provider-specific semantic configuration separated from credential material, not ever-expanding redaction heuristics.

## Meaning of facts

A `Fact` is a canonical assertion record. The type name does not guarantee truth. A source chunk can be inaccurate. An extraction rule can hallucinate. Two sources can contradict one another while producing distinct fact IDs.

The kernel proves or checks:

- stable identity under declared canonicalization;
- declared derivation structure;
- finite proof support;
- preservation under merge;
- artifact integrity.

It does not prove:

- logical entailment;
- empirical truth;
- source authority;
- model calibration;
- citation sufficiency;
- absence of omitted counterevidence.

Future schemas may use terms such as `assertion`, `claim`, or `source-record` more carefully in user-facing APIs.

## Derivation identity granularity

The current derivation ID includes request and configuration IDs. This preserves detailed lineage but can create many derivation records for repeated execution of the same logical rule over the same inputs.

Alternative models include:

1. **Logical derivation ID:** output, rule/version, inputs, semantic attributes.
2. **Execution event ID:** logical derivation ID plus request, attempt, timing, provider response.

The current implementation combines parts of both. This is acceptable for P02's audit goal but may inflate states in production. A future version should separate logical proof edges from operational execution events while preserving migration.

## Input multiplicity and role semantics

Derivation inputs are sorted by role and fact ID, making delivery order irrelevant. Duplicate identical role/fact pairs are currently retained rather than deduplicated. Most proof rules should treat such duplicates as redundant; some weighted or multiplicity-sensitive rule might not.

The schema must decide whether inputs are:

- a set of role/fact edges;
- a multiset;
- an ordered vector whose position is encoded in role.

The current constructor implements a canonical ordered list after sorting, preserving duplicates. This should be documented per rule and may be refined in `v2`.

## Validation and inconsistent states

Raw state join is monotone, but validity is not. Adding a conflicting variant makes a previously valid state invalid. This is desirable for evidence preservation but affects service behavior.

A production system needs explicit policies for:

- whether to serve the last verified snapshot while a new conflict is quarantined;
- whether any conflict fails the whole request or only affected facts;
- how dependent selected views are invalidated;
- how conflict metrics and artifacts are retained;
- how repairs become auditable state transitions.

The reference verifier is whole-state and conservative.

## Performance validity

The scaling experiment isolates repeated cloning. It does not include:

- database indexes;
- JSON encoding or network transfer;
- proof verification at each step;
- realistic payload size distribution;
- garbage-collector tuning;
- lock contention under high parallelism;
- cross-process replication;
- persistence or fsync;
- compression;
- deletion or compaction.

The large ratios should be read as evidence against a specific ingestion pattern, not as expected end-to-end speedups.

The mutable ledger still clones the full state for each snapshot. Frequent snapshots can dominate cost. Production designs may use immutable snapshot handles, MVCC, persistent data structures, or database transactions.

## Determinism boundaries

The kernel makes merge and selection deterministic given fixed admitted records and policy. It does not make providers deterministic.

A language model may produce different outputs under nominally identical settings. A remote index may change without a snapshot ID. Floating-point scoring can differ across hardware. A timeout can produce a partial candidate set. An external tool can read changing data.

The semantic model responds by naming these variables where possible and preserving divergent records where they occur. It cannot eliminate unmodeled external change.

## Selection quality

A total comparator ensures reproducibility, not relevance. Stable keys can break ties arbitrarily. Utility values can be poorly calibrated across retrieval methods. One-per-fact can suppress useful alternate passages if a fact is too coarsely defined. A fixed unit budget can favor short evidence.

P04, P07, and P08 should evaluate ranking and view policy separately. P03 only establishes that the same policy over the same state yields the same view.

## Incomplete recursive semantics

P01-P03 provide the records and merge needed for recursive retrieval but do not implement a general closure engine. The verifier computes finite proof ranks after records are present. It does not schedule rules, track frontiers, prove fairness, or emit partial-completeness certificates.

P05 should build recursive closure over this kernel. Its rules should admit deltas, and its frontier state should merge lawfully. Limit and ranking operations should remain view-level unless explicitly modeled as semantic search bounds.

## Deletion and retraction

Set union cannot remove a fact. Corpus deletion, correction, expiration, and authorization revocation require more structure.

Possible approaches include:

- immutable retraction events interpreted by a temporal view;
- reference-counted valid derivations;
- differential dataflow-style positive and negative weights;
- truth-maintenance systems;
- epoch/snapshot replacement;
- explicit tombstones with causal ordering.

P11 should select one model and define laws. Applying ordinary map deletion to a shared ledger would invalidate P03's convergence properties.

## Authorization

The kernel has request and configuration IDs but no access-control labels. A proof bundle can reveal restricted sources. A public fact may be derived from confidential evidence and require confidential treatment.

P13 should add labels with conservative propagation through derivations and prove noninterference properties. Until then, state and proof bundles must remain within the authorization boundary of all included sources.

## External validity

The evaluation fixtures are synthetic and small. They are designed to expose semantic edge cases, not represent every real workload. The oak-wilt diamond demonstrates alternate proofs but not complex document schemas, multilingual normalization, or large knowledge graphs.

Adoption should include shadow evaluation on representative `rag-ttc` corpora, providers, tool traces, and experiments. Important measures include conflict rate, deduplication rate, state size, proof-bundle size, cache invalidation, citation stability, and answer-quality decomposition.

# Conclusion and next research pass

## Thesis conclusion

P01-P03 can be implemented as a compact semantic kernel that fits the existing `rag-ttc` architecture.

P01 replaces ad hoc structural hashing with explicit, typed, domain- and version-separated semantic identity. It provides a vocabulary for ordered and unordered collections, scalar policies, path portability, field roles, mutation contracts, and golden compatibility vectors. The production review found and patched concrete identity omissions.

P02 replaces the overloaded notion of evidence with three records: facts, derivations, and observations. This separation permits stable source and claim identity, multiple independent proofs, request-specific scores without fact mutation, finite proof ranks, proof bundles, tamper detection, and adapters from existing domain types.

P03 replaces arrival-sensitive accumulation with componentwise set union over complete variants. The resulting join is associative, commutative, and idempotent. It retains conflicts instead of hiding them. A deterministic selection barrier moves ranking, budgets, and citation labels after global merge. Exhaustive and generated tests support the implementation, and a mutable ledger shows that lawful semantics need not imply persistent-clone overhead.

The key architectural result is a boundary, not a framework:

```text
operational execution may vary
canonical admitted information must obey explicit identity and merge laws
non-monotone selection must occur as a versioned view
```

Under this boundary, retries, duplicate queue delivery, batching, and worker order can be changed without changing the canonical state, provided they deliver the same admitted variants. Differences that remain become attributable to semantic configuration, source snapshots, provider nondeterminism, partial completion, conflicts, or view policy.

## Answers to the research questions

**RQ1.** Yes. A small typed value language with tags, lengths, canonical sets/objects, and domain/version separation provides deterministic reviewable identity construction.

**RQ2.** Yes, for declared fields. Catalog validation and mutation matrices make field-role policy executable. Completeness of the catalog still requires governance and future structural checks.

**RQ3.** Yes. Existing chunks, representations, evidence, and knowledge facts can map into facts, derivations, and observations. Full module compilation of these adapters remains pending.

**RQ4.** Yes. One fact bucket can have one canonical fact variant and several derivations. The diamond fixture retains two proofs without duplicating the claim.

**RQ5.** Yes for finite states under the implemented structural rules. The verifier recomputes IDs, checks closure, detects conflicts, and computes the least finite proof rank.

**RQ6.** Yes. Variant-set union is associative, commutative, and idempotent and retains same-ID/different-record conflicts.

**RQ7.** Yes, conditional on a fixed set of admitted deltas and eventual delivery. Exhaustive and concurrent tests support the implementation.

**RQ8.** Yes. Exact deduplication, a total comparator, and post-merge budgets produce a permutation-invariant view. The legacy counterexample demonstrated the defect removed.

**RQ9.** Yes architecturally. The kernel is adapter-based and leaves `flow` responsible for execution. Production integration tests require the declared Go toolchain.

## Immediate next actions

The next engineering pass should:

1. run the full repository suite under Go 1.26.5;
2. resolve any adapter or cache API integration errors;
3. add identity catalogs for every production cache;
4. shadow-admit canonical records in representative experiments;
5. measure duplicate facts, alternate derivations, conflicts, and bundle sizes;
6. enable deterministic tool selection behind a feature flag;
7. add a durable backend conformance prototype;
8. separate logical derivations from execution events if state growth warrants it.

## Research projects enabled by this work

### P04 - candidate state and ranked views

P04 can now assume a stable canonical fact store and focus on view semantics: ranking fusion, ambiguity, token packing, diversity, and citation policies. It should define policy fingerprints and test that ranking changes do not mutate facts.

### P05 - closure and frontier evaluation

P05 can use facts and derivations as rule products and the ledger as accumulated state. It should prove sound partial results, frontier fairness, fixed-point completion, and schedule independence for recursive retrieval.

### P06 - flow executor semantics

P06 can formalize wrappers as semantics-preserving transformations. Cache transparency, retry transparency, batch homomorphism, budget placement, and trace identity now have concrete record-level oracles.

### P07/P08 - knowledge and connected retrieval

These projects can compare discovery algorithms by admitted fact and observation sets rather than conflated ranked evidence lists. Fusion parameters already have explicit runtime identity.

### P09 - tool evidence and citations

P09 can extend the deterministic ledger, define typed tool-result schemas, and verify citations against proof bundles. The arrival-order counterexample becomes a regression fixture.

### P10 - proof-carrying experiments

Experiment outputs can package canonical state, selected view, proof bundle, configuration fingerprints, and operational trace. Replay can identify where runs diverge.

### P11 - incremental updates and retractions

P11 can track which derivations remain after corpus changes. Alternate derivations already provide the dependency structure needed to avoid retracting a fact while another proof survives.

### P12 - backend and migration conformance

The in-memory state and canonical fixtures provide an oracle for SQL, graph, event-log, and object-store implementations.

### P13 - authorization and noninterference

Fact and derivation boundaries provide the places where labels can be attached and conservatively propagated. Proof bundles reveal exactly which sources a selected claim depends on.

## Final perspective

The thesis does not argue that every RAG system should expose category theory or a custom DSL. It argues that a small number of semantic laws should be as ordinary as interface conformance and unit tests.

A programmer should be able to read the kernel and say:

```text
this fingerprint changes exactly when these semantic inputs change
this fact is stable across scores and ranks
this claim has these two proofs
this merge cannot depend on worker order
this retry cannot duplicate state
this conflict cannot be hidden by timing
this citation list is selected only after all candidates are merged
this artifact can be verified independently
```

That is the practical meaning of rigorous semantics in `rag-ttc`.

\appendix

# Public API reference

## `semanticid`

The core exported surface is:

```go
type Domain string
type Version string

type Fingerprint struct {
    Domain  Domain
    Version Version
    Sum     [32]byte
}

func FingerprintValue(
    domain Domain,
    version Version,
    value Value,
) (Fingerprint, error)

func MustFingerprint(
    domain Domain,
    version Version,
    value Value,
) Fingerprint

func Parse(text string) (Fingerprint, error)
```

`Fingerprint` implements text and JSON marshaling. The text form is intended for logs, schemas, and database fields. Callers should compare complete parsed fingerprints, not only hex payloads, because domain and version are part of identity.

The value constructors are:

```go
func Null() Value
func Bool(bool) Value
func String(string) (Value, error)
func MustString(string) Value
func Bytes([]byte) Value
func Int(int64) Value
func Uint(uint64) Value
func Float64(float64) (Value, error)
func MustFloat64(float64) Value
func List(...Value) Value
func Set(...Value) Value
func Object(...Field) (Value, error)
func MustObject(...Field) Value
func Optional(name string, value *Value) Value
func PortablePath(string) (Value, error)
```

Fields are explicit:

```go
type Field struct {
    Name  string
    Value Value
}
```

The catalog API is:

```go
type FieldSpec struct {
    Path        string
    Role        FieldRole
    InIdentity  bool
    Explanation string
}

type Catalog struct {
    Name    string
    Domain  Domain
    Version Version
    Fields  []FieldSpec
}

func (c Catalog) Validate() error
func (c Catalog) SortedFields() []FieldSpec
```

The mutation harness is generic:

```go
type Mutation[T any] struct {
    Name       string
    Role       FieldRole
    MustChange bool
    Apply      func(T) T
}

func VerifyContract[T any](
    name string,
    baseline T,
    fingerprint func(T) (Fingerprint, error),
    mutations []Mutation[T],
) (ContractReport, error)
```

## `derive` record constructors

```go
type FactID string
type DerivationID string
type ObservationID string

func NewFact(
    kind string,
    schema string,
    payload any,
) (Fact, error)

func NewFactFromJSON(
    kind string,
    schema string,
    payload []byte,
) (Fact, error)

func NewDerivation(
    output FactID,
    rule string,
    version string,
    inputs []Input,
    requestID string,
    configID string,
    attributes any,
) (Derivation, error)

func NewSeedDerivation(
    output FactID,
    sourceKind string,
    sourceVersion string,
    requestID string,
    configID string,
    attributes any,
) (Derivation, error)

func NewObservation(
    kind string,
    schema string,
    subject FactID,
    requestID string,
    payload any,
) (Observation, error)
```

## State operations

```go
func NewState() State
func FromSnapshot(Snapshot) (State, error)
func Join(State, State) State

func (s State) WithFact(Fact) (State, error)
func (s State) WithDerivation(Derivation) (State, error)
func (s State) WithObservation(Observation) (State, error)
func (s State) WithProof(Fact, Derivation) (State, error)
func (s State) Clone() State
func (s State) Equal(State) bool
func (s State) Snapshot() Snapshot
func (s State) CanonicalJSON() ([]byte, error)
func (s State) Fingerprint() (semanticid.Fingerprint, error)
func (s State) Conflicts() []Conflict
func (s State) Counts() Counts
```

Single-record accessors return `ok=false` when a bucket is absent or conflicted. Variant accessors remain available for diagnostics.

The concurrent facade is:

```go
func NewLedger(initial State) *Ledger
func (l *Ledger) Merge(delta State) []Conflict
func (l *Ledger) Snapshot() State
func (l *Ledger) Conflicts() []Conflict
```

## Verification and proofs

```go
func Verify(State) VerificationReport

func BuildProofBundle(
    state State,
    selected []FactID,
    corpusID string,
    configID string,
) (ProofBundle, error)

func VerifyProofBundle(ProofBundle) VerificationReport
```

The verifier returns issue codes intended for stable machine use. New issue codes can be added without changing existing meanings; changing an existing meaning requires a report schema version.

## Selection

```go
type Candidate struct {
    Fact        FactID
    Observation ObservationID
    StableKey   string
    Utility     float64
    Units       int
}

type SelectionPolicy struct {
    Version     string
    MaxItems    int
    MaxUnits    int
    LabelPrefix string
}

type Selected struct {
    Candidate Candidate
    Rank      int
    Label     string
}

func Select(
    state State,
    candidates []Candidate,
    policy SelectionPolicy,
) ([]Selected, error)
```

Selection currently returns an ordered slice but not a view fingerprint. A production wrapper should fingerprint state, candidate set, and policy if the selected view is cached or stored as an experiment identity.

# Encoding and schema contracts

## P01 kind tags

| Hex tag | Kind | Payload |
|---:|---|---|
| `00` | null | none |
| `01` | bool | one byte, `00` or `01` |
| `02` | string | uvarint byte length + UTF-8 bytes |
| `03` | bytes | uvarint length + raw bytes |
| `04` | signed integer | Go canonical varint |
| `05` | unsigned integer | Go canonical uvarint |
| `06` | float64 | 8-byte big-endian IEEE-754 bits |
| `07` | list | count + length-delimited child encodings |
| `08` | set | sorted/deduplicated child encodings |
| `09` | object | sorted unique names and child encodings |

The exact Go varint format is part of the versioned contract. Implementations in other languages must reproduce it or consume the provided canonical bytes.

## Fingerprint text grammar

A simplified grammar is:

```text
fingerprint = "sid1:" domain ":" version ":sha256:" 64HEXDIG

domain      = lowercase-letter
              { lowercase-letter | digit | "." | "_" | "/" | "-" }

version     = alphanumeric
              { alphanumeric | "." | "_" | "-" }
```

Text parsing validates the domain and version and requires exactly 32 digest bytes.

## P02 snapshot schema

The canonical snapshot has this logical shape:

```json
{
  "schema": "rag-derive-state/v1",
  "facts": [
    {
      "id": "sid1:rag.fact:v1:sha256:...",
      "kind": "source-chunk",
      "schema": "rag.chunk/v1",
      "payload": {}
    }
  ],
  "derivations": [
    {
      "id": "sid1:rag.derivation:v1:sha256:...",
      "output": "sid1:rag.fact:v1:sha256:...",
      "rule": "seed/corpus",
      "rule_version": "v1",
      "inputs": [],
      "request_id": "...",
      "config_id": "...",
      "attributes": {}
    }
  ],
  "observations": [
    {
      "id": "sid1:rag.observation:v1:sha256:...",
      "kind": "retrieval-score",
      "schema": "rag.score/v1",
      "subject": "sid1:rag.fact:v1:sha256:...",
      "request_id": "...",
      "payload": {}
    }
  ]
}
```

Snapshots list every variant. They do not collapse conflicts.

## Proof-bundle schema

```json
{
  "schema": "rag-proof-bundle/v1",
  "corpus_id": "...",
  "configuration_id": "...",
  "selected": ["sid1:rag.fact:v1:sha256:..."],
  "state": {
    "schema": "rag-derive-state/v1",
    "facts": [],
    "derivations": [],
    "observations": []
  }
}
```

`selected` is sorted during construction. The state is the backward support closure. A consumer must verify the bundle before using it.

## Evaluation schema

The conformance command emits:

```text
rag-ttc-p01-p03-evaluation/v1
```

with environment, P01 contract, P02 provenance metrics, and P03 merge/selection/concurrency/performance results. This is an experiment-result schema, not a stable runtime API.

# Test specification

## P01 tests

### `TestObjectOrderDoesNotAffectFingerprint`

Constructs equivalent objects with different field enumeration order and requires equal fingerprints.

### `TestListOrderChangesAndSetOrderDoesNot`

Requires list reversal to change identity and set reversal to preserve it.

### `TestGeneratedObjectAndSetPermutationInvariance`

Runs 500 generated trials with shuffled object and set construction order.

### `TestDomainAndVersionSeparation`

Uses one value under changed domain and version and requires distinct fingerprints.

### `TestFingerprintTextAndJSONRoundTrip`

Checks parse, text marshal, and JSON marshal round trips.

### `TestFloatPolicy`

Checks rejection of NaN/infinity and normalization of negative zero.

### `TestPortablePath`

Checks path cleaning, relative-path policy, and root escape.

### `TestPortablePathIsHostIndependent`

Checks slash/backslash equivalence and rejects Unix absolute, drive-qualified, UNC, and escaping paths.

### `TestObjectRejectsDuplicateFields`

Checks ambiguous object rejection.

### `TestGoldenFingerprint`

Pins the exact encoding contract.

### `TestCatalogValidation`

Checks mandatory and forbidden role participation.

### `TestMutationContract`

Checks identity-changing and identity-preserving field mutations.

## P02 tests

### `TestNormalizeJSONCanonicalizesObjectOrderAndNumberSpelling`

Checks equivalent object order and decimal/exponent spellings.

### `TestNormalizeJSONRejectsDuplicateNamesAndTrailingValues`

Checks ambiguous and multi-value inputs.

### `TestFactIdentityUsesCanonicalContent`

Checks equivalent payloads share identity and semantic mutations do not.

### `TestObservationsDoNotAlterFactIdentity`

Checks distinct request scores remain attached to one fact.

### `TestDerivationInputOrderIsCanonical`

Checks premise delivery order does not alter derivation identity and stored order is canonical.

### `TestDiamondProvenanceAndProofBundle`

Checks alternate proofs, ranks, support closure, and independent bundle verification.

### `TestVerificationRejectsTamperingAndMissingDependencies`

Checks ID mismatch and missing-premise errors.

## P03 tests

### `TestJoinLawsAndAllDeliveryOrders`

Checks empty identity, idempotence, ACI laws, and all fixture delta permutations.

### `TestJoinGeneratedLaws`

Checks 500 generated state triples.

### `TestIdentityConflictRetainsAllVariantsAndIsRetrySafe`

Checks same-ID/different-record preservation and exact retry behavior.

### `TestConcurrentRetriesConverge`

Checks goroutine delivery under race detection.

### `TestDeterministicSnapshotRoundTrip`

Checks stable canonical serialization and state reconstruction.

### `TestSelectIsPermutationAndRetryInvariant`

Checks candidate order and duplicate delivery.

### `TestSelectionBarrierRemovesArrivalOrderNondeterminism`

Compares deterministic selection with a first-arrival baseline.

### `TestSelectDoesNotMutateKnowledgeState`

Checks canonical state bytes before and after view construction.

### `TestSelectEmitsAtMostOneCandidatePerFact`

Checks per-fact deduplication policy.

### `TestSelectTieBreakIsTotalAndStable`

Checks stable ordering for utility ties.

## Adapter tests

`ragcodec` checks that equal source content with different query observations maps to one fact. The tool-answer deterministic-ledger test checks completion-order invariant finalization. These tests were added but remain pending full-module execution under the declared toolchain.

# Source changes

## New general packages

```text
pkg/semanticid/
pkg/rag/derive/
```

## New conformance command and handoff

```text
cmd/semantic-foundations/
research/p01-p03-foundations/
```

## New adapters

```text
pkg/rag/derive/ragcodec/
pkg/rag/derive/knowledgecodec/
pkg/rag/toolanswer/deterministic_ledger.go
pkg/rag/toolanswer/deterministic_ledger_test.go
```

## Modified production identity paths

```text
pkg/rag/evidence_identity.go
pkg/rag/evidence_identity_test.go
pkg/rag/connected/runtime.go
pkg/rag/connected/runtime_test.go
pkg/rag/providers/geppetto/bundle.go
pkg/rag/providers/geppetto/fingerprint.go
pkg/rag/providers/geppetto/fingerprint_test.go
pkg/rag/generation/cached.go
pkg/rag/generation/flow_adapters.go
pkg/rag/generation/flow_step.go
pkg/rag/generation/*_test.go
pkg/rag/reranking/cached.go
pkg/rag/reranking/cached_test.go
pkg/rag/toolanswer/evidence.go
```

## Updated application call sites

Generation and reranking callers under application commands, chat runtime, experiments, index building, and knowledge building were updated to pass role-specific provider configuration fingerprints. The exact list is included in the implementation patch and changed-file artifact.

# Reproduction guide

## Prerequisites

For the standalone core:

- Go 1.23.2 or a compatible newer toolchain;
- no network services;
- no database;
- no provider credentials.

For full repository integration:

- the Go version declared by the repository, currently 1.26.5 in the supplied snapshot;
- module dependencies;
- any test-specific services or build tools documented by the repository.

## Standalone validation

From a GOPATH placement of the repository:

```bash
export GO111MODULE=off
export GOPATH=/path/to/gopath
cd "$GOPATH/src/github.com/the-tree-center/rag-ttc"

go test -race -v ./pkg/semanticid ./pkg/rag/derive
go vet ./pkg/semanticid ./pkg/rag/derive
```

## Conformance command

```bash
go run ./cmd/semantic-foundations \
  --output /tmp/evaluation.json \
  --artifact-dir /tmp/p01-p03-artifacts \
  --stress-facts 2000
```

Expected qualitative results:

```text
P01 contract_passed = true
P02 verification.valid = true
P02 bundle_verified = true
P02 tamper_detected = true
P03 unique_merge_outputs = 1
P03 unique_selection_views = 1
P03 legacy_arrival_views > 1
P03 conflict_variants = 2
P03 concurrent_divergences = 0
P03 stress_outputs_equal = true
```

Timing fields are environment-dependent and should not be used as golden values.

## Handoff demonstration

```bash
cd research/p01-p03-foundations
./demo.sh
```

The script creates a temporary GOPATH placement, runs race-enabled core tests, executes the conformance command, and prints the generated evaluation artifact location.

## Checksum validation

```bash
cd research/p01-p03-foundations
sha256sum -c CHECKSUMS.sha256
```

If any source, fixture, result, or report is intentionally updated, regenerate the checksum manifest and review the schema/version implications.

## Full integration validation

With the declared toolchain available:

```bash
go test ./...
go vet ./...
```

Then run targeted tests with uncached execution:

```bash
go test -count=1 ./pkg/rag/connected/...
go test -count=1 ./pkg/rag/generation/...
go test -count=1 ./pkg/rag/reranking/...
go test -count=1 ./pkg/rag/providers/geppetto/...
go test -count=1 ./pkg/rag/toolanswer/...
go test -count=1 ./pkg/rag/derive/ragcodec/...
go test -count=1 ./pkg/rag/derive/knowledgecodec/...
```

A production acceptance run should also execute representative current experiments with old and new cache namespaces and compare semantic state/view/answer layers separately.

# Machine-readable result summary

The final 2,000-fact conformance execution reported:

```text
P01
  mutation contract passed:       true
  set order invariant:            true
  object order invariant:         true
  domain separated:               true
  version separated:              true

P02
  fact IDs / variants:            3 / 3
  derivation IDs / variants:      4 / 4
  observation IDs / variants:     2 / 2
  verifier valid:                 true
  claim rank:                     1
  claim proofs:                   2
  proof bundle valid:             true
  tamper detected:                true
  observations separate:          true

P03
  merge deltas:                   6
  merge permutations:             720
  distinct merge outputs:         1
  selection permutations:         6
  distinct deterministic views:   1
  legacy arrival views:           6
  conflict variants retained:     2
  conflict order independent:     true
  concurrent runs:                100
  concurrent divergences:         0
  stress facts:                   2000
  stress outputs equal:           true
```

The exact fingerprints and timing measurements are in `evaluation-final.json` in the results package. Exact digest values are deterministic for the fixture; elapsed times are not.

# Selected design alternatives

## Reflection-based hashing

**Rejected as the primary API.** Reflection reduces boilerplate but makes field inclusion depend on struct evolution and tags. It also obscures list/set policy and can include operational or secret fields accidentally. Reflection may assist catalog-completeness checks, not replace semantic constructors.

## Direct RFC 8785 identity for all records

**Not adopted in P02.** RFC 8785 is an established interoperable JSON canonicalization scheme, but the prototype required exact decimal equivalence across inputs such as `1`, `1.0`, and `1e0` without binary float conversion. A local versioned normalizer was simpler for the experiment. Interoperability may justify migration to a standard in a later version.

## One evidence struct

**Rejected for canonical storage.** It conflates stable facts, support, query observations, and presentation. It remains useful as an adapter/transport type.

## Map ID to one record

**Rejected.** It forces overwrite or immediate failure and cannot retain diagnostic variants independently of delivery order.

## First-writer-wins

**Rejected.** It is idempotent but not commutative without an external writer order, and it discards conflicting evidence.

## Last-writer-wins

**Rejected.** It requires a trusted total timestamp/order, changes under retry timing, and discards evidence. It is unsuitable for immutable content-derived records.

## Multiset merge

**Rejected for canonical records.** Retry count would change state. Operational attempt counts belong in traces or events.

## Ranking during admission

**Rejected.** It makes budgets and labels depend on completion order. Ranking remains a view.

## Persistent-only state

**Rejected for high-volume ingestion.** It is retained as a simple oracle, while the mutable ledger preserves the same laws at lower cost.

## Minimal proof only

**Deferred.** Keeping only one proof reduces bundle size but loses independent support and makes the chosen proof policy semantic. P02 retains all proofs; a view can later choose minimal, diverse, authoritative, or cheapest proof subsets.

# Bibliography

The references below informed the design context. The implementation and theorem statements in this thesis are specific to the supplied `rag-ttc` artifact.

1. S. Gilbert and N. Lynch. "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services." *SIGACT News*, 2002.
2. M. Shapiro, N. Preguica, C. Baquero, and M. Zawirski. "Conflict-Free Replicated Data Types." *Stabilization, Safety, and Security of Distributed Systems*, 2011. Available from INRIA/HAL and Springer.
3. P. Alvaro, N. Conway, J. Hellerstein, and W. Marczak. "Consistency Analysis in Bloom: a CALM and Collected Approach." *CIDR*, 2011.
4. J. M. Hellerstein and P. Alvaro. "Keeping CALM: When Distributed Consistency is Easy." *Communications of the ACM*, 2020. Preprint: https://arxiv.org/abs/1901.01930
5. Y. Gil, S. Miles, K. Belhajjame, H. Deus, D. Garijo, G. Klyne, P. Missier, S. Soiland-Reyes, and S. Zednik. "PROV Model Primer." W3C Working Group Note, 2013. https://www.w3.org/TR/prov-primer/
6. L. Moreau and P. Missier, editors. "PROV-DM: The PROV Data Model." W3C Recommendation, 2013. https://www.w3.org/TR/prov-dm/
7. T. J. Green, G. Karvounarakis, and V. Tannen. "Provenance Semirings." *PODS*, 2007.
8. K. Claessen and J. Hughes. "QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs." *ICFP*, 2000.
9. A. Rundgren, B. Jordan, and S. Erdtman. "JSON Canonicalization Scheme (JCS)." RFC 8785, 2020. https://www.rfc-editor.org/rfc/rfc8785
10. National Institute of Standards and Technology. "Secure Hash Standard (SHS)." FIPS PUB 180-4, 2015. https://csrc.nist.gov/pubs/fips/180-4/upd1/final
11. The Go Authors. "The Go Memory Model." https://go.dev/ref/mem
12. The Go Authors. `encoding/binary`, `encoding/json`, `crypto/sha256`, and `sync` package documentation. https://pkg.go.dev/
13. M. Zaharia, M. Chowdhury, T. Das, A. Dave, J. Ma, M. McCauley, M. Franklin, S. Shenker, and I. Stoica. "Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing." *NSDI*, 2012.
14. F. McSherry, D. G. Murray, R. Isaacs, and M. Isard. "Differential Dataflow." *CIDR*, 2013.
15. P. Wadler. "Theorems for Free!" *Functional Programming Languages and Computer Architecture*, 1989. Included as general background on deriving program laws from interfaces.

# Artifact declaration

The delivered artifact set contains:

- the patched `rag-ttc` repository snapshot;
- a unified source patch against the supplied snapshot;
- the standalone research handoff package;
- machine-readable evaluation and scaling results;
- Markdown thesis source;
- rendered PDF thesis;
- diagrams and chart sources;
- checksums for distributable archives.

The artifact should be treated as a research branch until the complete repository passes under its declared toolchain. The standalone P01-P03 kernel is executable and independently reviewable.
