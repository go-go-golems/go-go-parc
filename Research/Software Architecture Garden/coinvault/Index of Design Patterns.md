---
title: CoinVault — Index of Design Patterns
aliases:
  - CoinVault design pattern index
  - CoinVault pattern index
  - CoinVault glossary
status: active
type: architecture-garden-index
created: 2026-08-14
analyzed: 2026-08-14
analysis_schema: architecture-garden-v1
repository: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault
repository_commit: 10d1a8d8c5b281f78b4e73d3956be573dcc8fad1
derived_from: Research/Software Architecture Garden/coinvault/README.md
tags:
  - architecture-garden
  - coinvault
  - design-pattern-index
  - rag
  - llm-as-judge
  - evaluation-loops
related_notes:
  - "[[Research/Software Architecture Garden/coinvault/README]]"
  - "[[Research/Software Architecture Garden/coinvault/Index of Design Patterns - Rationale]]"
  - "[[Research/Software Architecture Garden/README]]"
---

# CoinVault — Index of Design Patterns

This is the back-of-the-book index for the [[Research/Software Architecture Garden/coinvault/README|CoinVault architecture study]]. It catalogues the design patterns and vocabulary of the Gold Eagle Coin admin-chat evaluation, judging, and causal-optimization apparatus so a reader can find a concept by name, recall it in one sentence, and jump to the exact place it is established, applied, compared, or owed.

This is a **hybrid index-plus-glossary**: each entry carries a one-sentence definition (the glossary job — *what does this mean?*) and a set of locators (the index job — *where can I read about this?*). It is filed by how a reader is likely to remember a concept, not by how the study happened to phrase it, so it carries many `See` redirects from alternate phrasings to the canonical entry.

## How to read this index

- Each entry is a **heading**, so every `See` and `see also` is a clickable link that lands on that entry.
- A trailing **§n** (or **§n.m**) links into the CoinVault study, e.g. [[Research/Software Architecture Garden/coinvault/README#7.1 The treatment-exercise proof|§7.1]]. § is the primary appearance; later §-links are further occurrences. The locator points at the section that *substantively* treats the concept — a passing mention is not indexed (the disappointed-reader test).
- A leading **↳** marks a cross-reference into the wider Garden or a Pattern Zoo, so the reader can tell at a glance whether a pattern is local or travels.
- A trailing bracket, e.g. `[Established]`, is the Garden's [[Research/Software Architecture Garden/README#Pattern maturity vocabulary|maturity label]] for that pattern, taken from [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]].
- **`See`** redirects to the canonical entry when the entry itself has no locators (alternate phrasing, synonym, reader-memory handle). **`see also`** links to a *related but distinct* concept the reader should not collapse into one.
- For identity strings, schema versions, budgets, and closed vocabularies, see the [[#Identity strings, schemas, and budgets|notation table]] near the end — the analogue of a symbol table for a codebase that speaks in versioned handles.

The reasoning behind every entry — what kind of evidence grounds it, and what a reader loses if it is omitted — is in [[Research/Software Architecture Garden/coinvault/Index of Design Patterns - Rationale|the companion rationale]].

---

## A

### Attribution law

The repository's governing idea, stated before any loop is described: *a measurement is attributable only when everything that could have caused it is either frozen and digest-identified, or observed and recorded.* [[Research/Software Architecture Garden/coinvault/README#1. The system under evaluation|§1]], [[Research/Software Architecture Garden/coinvault/README#11. Authority and identity map|§11]]. ↳ [[Research/Software Architecture Garden/ragopt/README|Ragopt]] identity discipline; [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo|RAG Pattern 1]]. *see also* [[#Semantic identity strings]], [[#Instrument freezing by version key and source lock]], [[#Treatment-exercise proof]].

### A/B experiment, proving the mutation fired

*See* [[#Treatment-exercise proof]].

### Answer contract, deterministic

Staged deterministic checks (generation → route → retrieval → contract) that name the first responsible stage via `FirstFailure`, with a report whose own `Valid` flag must agree with the conjunction of its checks. [[Research/Software Architecture Garden/coinvault/README#7.3 The deterministic answer contract|§7.3]]. *see also* [[#Trace collector as validator]], [[#Treatment-exercise proof]], [[#Projection blocks]].

### Authority and identity map

The §11 table that pins every object family — knowledge bundle, retrieval configuration, eval set, chat suite case, candidate, treatment contract, cell, native artifact, judge score, gate decision, promotion plan, human feedback — to its owner, its identity coordinate, and the thing it must not be confused with. [[Research/Software Architecture Garden/coinvault/README#11. Authority and identity map|§11]]. ↳ [[Research/Software Architecture Garden/rag-ttc/03 - Reproducible Experiment Custody and Semantic Identity|rag-ttc identity]]; [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo|RAG Pattern 1]]. *see also* [[#Attribution law]], [[#Semantic identity strings]].

## B

### Blame-assigning diagnostics as citable artifacts

A cheap diagnostic that reports *where* retrieval failed, digest-addressed, and cited by the hypothesis of every expensive experiment via `diagnostic_manifest_digest`. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/coinvault/README#4. The candidate-pool diagnostic: blame assignment as a first-class instrument|§4]], [[Research/Software Architecture Garden/coinvault/README#14. Candidate ecosystem patterns|§14.5]]. ↳ [[Research/Software Architecture Garden/rag-ttc/README|rag-ttc]] diagnostic lineage (extraction, not independent confirmation). *see also* [[#Candidate-pool diagnostic]], [[#Instrument ladder]], [[#Determinism by prefix derivation]].

### Budget accounting, hard

Provider ceilings enforced with pre-reservation, spend seeded on resume, and a sticky close when spend cannot be proven accounted for; under-counted spend is treated as worse than a shortened campaign. [Established] [[Research/Software Architecture Garden/coinvault/README#7.2 The trace collector as validator|§7.2]], [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]]. ↳ [[Research/Software Architecture Garden/ragopt/README|Ragopt]] budgets. *see also* [[#Sticky close on unprovable spend]], [[#Trace collector as validator]], [[#Judge spend, call-bounded not token-bounded]]. For the exact ceilings, see [[#Identity strings, schemas, and budgets]].

## C

### Cached-channel hyper-parameter sweep under the one-change rule

Grid-search RRF constants × vector weights by retrieving both channels once at over-fetch depth and re-fusing *in memory* per cell, forcing the serving-default cell into the grid, and picking `BestCell` lexicographically. [Established] [[Research/Software Architecture Garden/coinvault/README#5. Hyper-parameter search under the one-change rule|§5]], [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]]. *see also* [[#One-change-per-candidate rule]], [[#Determinism by prefix derivation]], [[#RRF]], [[#Constraint-before-preference gate]].

### Candidate bundle

A frozen parent/challenger pair of snapshots differing in exactly one mutable asset, independently verified by Ragopt's `Mutation` computation. [[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], [[Research/Software Architecture Garden/coinvault/README#11. Authority and identity map|§11]]. ↳ [[Research/Software Architecture Garden/ragopt/README|Ragopt]] candidate/snapshot identity. *see also* [[#Mutation]], [[#Treatment contract]], [[#One-change-per-candidate rule]], [[#Mutation surface]]. *Must not be confused with* the applied change or the run that measures it.

### Candidate-pool diagnostic

A 950-line instrument that scores every retrieval stage (raw/authorized lexical and vector, fused, authorized-fused, reranked, returned, admitted) at multiple depths and classifies each miss into one of six diagnosis classes. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/coinvault/README#4. The candidate-pool diagnostic: blame assignment as a first-class instrument|§4]], [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]]. *see also* [[#Blame-assigning diagnostics as citable artifacts]], [[#Diagnosis classes]], [[#Determinism by prefix derivation]], [[#Concentration crowd-out]].

### Cell

One evaluation unit: run config + (suite, policy, candidate, snapshot, case, repeat, arm) + hash chain. *Not* a retry attempt, *not* a production session. [[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], [[Research/Software Architecture Garden/coinvault/README#11. Authority and identity map|§11]]. ↳ [[Research/Software Architecture Garden/ragopt/README|Ragopt]] coordinates; [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo|RAG Pattern 8]]. *see also* [[#Native artifact]], [[#Scalar Outcome]]. *Repeat is not retry.*

### Component evidence ledger

The cross-candidate status ledger that accumulates verdicts across one-mechanism experiments, with statuses `structurally_invalid`, `component_rejected`, `historically_supported`, `conditional_evidence`, `release_rejected`, `release_promoted`. No entry has ever reached `release_promoted`, which the record treats as information, not embarrassment. [[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]]. *see also* [[#Double verdict]], [[#Gate decision]], [[#Witness/gate separation]].

### Computed faithfulness

Faithfulness is computed as supported-over-total from structurally validated verdicts; the model is never asked for a score it could flatter. [[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]]. *see also* [[#Judge, two-step decomposed]], [[#Witness/gate separation]], [[#Structural validation of judge output]].

### Concentration crowd-out

The duplicate-chunk failure mode fired when the surviving top slice is dominated by more than two chunks of a single document; one of the six diagnosis classes. [[Research/Software Architecture Garden/coinvault/README#4. The candidate-pool diagnostic: blame assignment as a first-class instrument|§4]]. *see also* [[#Diagnosis classes]], [[#Candidate-pool diagnostic]].

### Configuration is not behavior

*See* [[#Treatment-exercise proof]]. (The recorded conclusion from six failed `default_results 5→8` experiments that measured nothing.)

### Constraint-before-preference gate

A lexicographic policy: hard constraints before target before regressions before cost tie-breakers; preference is total, deterministic, and reproducible from the artifact. Appears in the sweep (`BestCell`), in the in-process A/B verdict (`retrievalSummaryWins`), and in the RAGOPT gate. [[Research/Software Architecture Garden/coinvault/README#5. Hyper-parameter search under the one-change rule|§5]], [[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]], [[Research/Software Architecture Garden/coinvault/README#8. The GEPA correspondence, stated precisely|§8]]. ↳ [[Research/Software Architecture Garden/ragopt/README|Ragopt gates]]; [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo|RAG Pattern 9]]. *see also* [[#Witness/gate separation]], [[#Gate decision]].

## D

### Default-results failure, the six experiments

*See* [[#Treatment-exercise proof]]. (Six successive `default_results 5→8` runs measured nothing because the model supplied an explicit `limit: 5`, so the mutated fallback never determined behavior.)

### Determinism by prefix derivation

Retrieve once at maximum depth and derive every shallower depth as a stable prefix of the same ordered list: one embedding call per question, no depth-dependent nondeterminism. [[Research/Software Architecture Garden/coinvault/README#4. The candidate-pool diagnostic: blame assignment as a first-class instrument|§4]]. *see also* [[#Candidate-pool diagnostic]], [[#Cached-channel hyper-parameter sweep under the one-change rule]].

### Deterministic answer contract

*See* [[#Answer contract, deterministic]].

### Deterministic retrieval eval

`EvalSet` v3, a digest-locked 80-question golden set, one of three modes per question (`positive`/`authorization-negative`/`judge-only`), grouped any-of expectations, failure-as-miss scoring, and unknown-ID warnings so golden-set rot is visible. [Established] [[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]], [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]]. *see also* [[#Strata as failure-mode taxonomy]], [[#Grouped any-of expectations]], [[#Failure-as-miss]], [[#Unknown-ID warnings]].

### Diagnosing a retrieval failure

*See* [[#Candidate-pool diagnostic]] and [[#Diagnosis classes]]. (The diagnostic reports *where* evidence was lost, not just *that* retrieval failed.)

### Diagnosis classes

The six miss classifications of the candidate-pool diagnostic: absent from both channels; below the fused measurement cutoff; removed by scope authorization; below the result budget; below the budget with concentration; admitted at final depth. [[Research/Software Architecture Garden/coinvault/README#4. The candidate-pool diagnostic: blame assignment as a first-class instrument|§4]]. *see also* [[#Candidate-pool diagnostic]], [[#Concentration crowd-out]].

### Double verdict

The apparatus is built to produce two separable results: the *gate outcome* (did this candidate pass the frozen release gate?) and the *causal learning* (did the mutation causally improve a measured cell?). Conflating them is the category error the program's own evidence ledger later diagnosed in itself. [[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]]. *see also* [[#Component evidence ledger]], [[#Witness/gate separation]], [[#Treatment-exercise proof]], [[#Gate outcome vs causal learning]].

## E

### Epistemic grade

The closed set `measured | estimate | association | hypothesis` from which every projection block's epistemic claim must be drawn. [[Research/Software Architecture Garden/coinvault/README#9. Runtime grounding: the always-on loop|§9]]. *see also* [[#Projection blocks]], [[#Runtime citation grounding with server-owned provenance]].

### EvalSet

Version 3 of the strict-YAML, digest-locked golden set; `validateEvalQuestion` rejects any question declaring zero or two modes. [[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]]. *see also* [[#Deterministic retrieval eval]], [[#Instrument freezing by version key and source lock]].

### EvidenceLedger

`gec-evidence-ledger/v1`, run-scoped, dedupe=chunk, hard budget of 12 items / 18 000 runes, assigning stable `E1..En` labels under which admitted evidence is cited; its `PolicyID` is one of the three semantic identity strings. [[Research/Software Architecture Garden/coinvault/README#1. The system under evaluation|§1]]. *see also* [[#Semantic identity strings]], [[#Runtime citation grounding with server-owned provenance]].

## F

### Failure-as-miss

A per-question search failure is recorded in `EvalResult.Failure` and scored as a miss rather than aborting the run, so one transport error cannot erase a baseline. [[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]]. *see also* [[#Deterministic retrieval eval]], [[#Unknown-ID warnings]].

### Feedback-to-corpus (designed, not built)

The designed-but-unbuilt pipe from production dissatisfaction to governed experiment: sanitization, classification, and review before a complaint becomes a candidate or a corpus case. The store, the UI, and the triage vocabulary exist; no reader, no backlog integration. The study names this the largest open edge of the system. [Emergent / Architecture debt] [[Research/Software Architecture Garden/coinvault/README#10. Human feedback: collected, not yet closed-loop|§10]], [[Research/Software Architecture Garden/coinvault/README#13. Architecture debt and open laws|§13]]. *see also* [[#Human feedback store]], [[#Four-way triage table]]. *The triage vocabulary exists before the pipe — the correct order.*

### Four-way triage table

The designed classification for turning a production complaint into either a candidate or a corpus fix: product defect → one isolated candidate; case defect → fix the corpus, don't tune the product; known limit → tracked, non-gating; investigate → gather evidence first. [[Research/Software Architecture Garden/coinvault/README#10. Human feedback: collected, not yet closed-loop|§10]]. *see also* [[#Human feedback store]], [[#Feedback-to-corpus (designed, not built)]].

### Freezing instruments before a run

*See* [[#Instrument freezing by version key and source lock]] and [[#Preflight environment-identity validation]]. (`--preflight-only` exercises the freeze with zero spend.)

## G

### Gate decision

The output of a pure policy evaluator over the comparison (policy byte + semantic digests); *not* promotion, *not* scientific proof. [[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], [[Research/Software Architecture Garden/coinvault/README#11. Authority and identity map|§11]]. *see also* [[#Constraint-before-preference gate]], [[#Witness/gate separation]], [[#Double verdict]], [[#Promotion plan]], [[#Gate outcome vs causal learning]].

### Gate outcome vs causal learning

The distinction the apparatus exists to hold apart: a candidate can be `historically_supported` (causal learning) while the release gate says `release_rejected` (gate outcome). [[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]]. *see also* [[#Double verdict]], [[#Component evidence ledger]], [[#Gate decision]].

### GEPA correspondence

CoinVault implements GEPA's *evaluation discipline* (bounded mutations, rich trajectories, frozen metrics, iterative candidates) while explicitly rejecting its *autonomy* (automated reflection, population search, self-applied winners). [[Research/Software Architecture Garden/coinvault/README#8. The GEPA correspondence, stated precisely|§8]]. *see also* [[#Reflection held outside the binary]], [[#Proposer]], [[#Mutation surface]], [[#Witness/gate separation]].

### Golden-set rot

*See* [[#Unknown-ID warnings]] and [[#Failure-as-miss]]. (The harness is built to make corpus/expectation drift visible rather than absorbed into the metrics.)

### Grouped any-of expectations

Each group is satisfied by *any* of its `AnyOf` document IDs and groups are complementary; coverage is satisfied-groups over required-groups, encoding that documents within a group are interchangeable evidence for one facet while groups are jointly necessary. [[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]]. *see also* [[#Deterministic retrieval eval]].

## H

### Held-out split, structurally closed

Candidate bundles ship a sentinel file in place of the validation split and the CLI hard-errors on `--split validation`, so held-out leakage is prevented by mechanism, not convention. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]], [[Research/Software Architecture Garden/coinvault/README#14. Candidate ecosystem patterns|§14.4]]. *see also* [[#Sentinel file]], [[#Train/validation hygiene]], [[#Held-out leakage (prevented)]].

### Held-out leakage (prevented)

*See* [[#Held-out split, structurally closed]] and [[#Sentinel file]]. (Prevented by mechanism, not convention.)

### Human feedback store

Per-message and per-conversation votes (−1/0/1), bounded tags, and append-only comments in SQLite behind authorized HTTP routes, surfaced with preset tags (`helpful`, `incorrect`, `incomplete`, `needs sql`, `pricing`). [[Research/Software Architecture Garden/coinvault/README#10. Human feedback: collected, not yet closed-loop|§10]]. *see also* [[#Feedback-to-corpus (designed, not built)]], [[#Four-way triage table]].

### Human promotion authority outside the binary

The promotion plan is fixed at `review_required` with `human_apply_required: true` and no apply command exists in either module; autonomy ends at evidence. [Established, inherited] [[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]]. ↳ [[Research/Software Architecture Garden/ragopt/README|Ragopt]] promotion authority. *see also* [[#Promotion plan]], [[#Witness/gate separation]], [[#Reflection held outside the binary]].

## I

### Information boundary

Ragopt sees only scalars and an artifact digest; answer text, SQL rows, and evidence bodies stay in the private native artifact, so the generic kernel is reusable across products without leaking product data. [[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]]. ↳ [[Research/Software Architecture Garden/ragopt/README|Ragopt]] scalar-outcome contract. *see also* [[#Native artifact]], [[#Scalar Outcome]].

### Instrument freezing by version key and source lock

Every component that produces a score (judge prompts, judge implementation, eval set, harness source, dependency revision) participates in a frozen, digest-verified identity checked before spend; changing the instrument invalidates the population by construction. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]], [[Research/Software Architecture Garden/coinvault/README#7.4 The preflight: environment identity before spend|§7.4]], [[Research/Software Architecture Garden/coinvault/README#14. Candidate ecosystem patterns|§14.2]]. *see also* [[#Attribution law]], [[#Preflight environment-identity validation]], [[#Source lock]], [[#Version-keyed durable cache]].

### Instrument ladder

The six loops ordered by cost and epistemic strength (retrieval eval → candidate-pool diagnostic → RRF sweep → LLM judge → RAGOPT paired loop → human promotion), with runtime grounding always-on alongside; cheap deterministic instruments justify the expensive causal loop. [[Research/Software Architecture Garden/coinvault/README#2. The instrument ladder|§2]]. *see also* each loop ([[#Deterministic retrieval eval]], [[#Candidate-pool diagnostic]], [[#Cached-channel hyper-parameter sweep under the one-change rule]], [[#Judge, two-step decomposed]], [[#Treatment-exercise proof]], [[#Human promotion authority outside the binary]]), [[#Blame-assigning diagnostics as citable artifacts]], [[#Runtime citation grounding with server-owned provenance]].

## J

### Judge, two-step decomposed

Statement extraction sees the question and answer but never the evidence; verdicts see the statements and evidence but never the freedom to restate the claims; the separation is the point. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]], [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]]. ↳ [[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc judge pipeline]] (port lineage). *see also* [[#Computed faithfulness]], [[#Structural validation of judge output]], [[#Version-keyed durable cache]], [[#Same-family judge caveat]], [[#Witness/gate separation]].

#### Evidence admitted includes non-knowledge tool results

The first baseline run scored every SQL-grounded claim as unsupported because the judge saw only knowledge-ledger evidence; a judge that cannot see the evidence the production answer actually used produces confidently wrong faithfulness. [[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]]. *see also* [[#Computed faithfulness]].

### Judge as witness, not a gate

*See* [[#Witness/gate separation]]. (The judge produces metrics; admission is a deterministic policy; application is human.)

### Judge outage masquerading as a quality change

*See* [[#Structural validation of judge output]]. (The reporting layer keeps explicit separate denominators — faithfulness, relevance, completion rate, judge success rate — so a judge outage cannot masquerade as a quality change.)

### Judge spend, call-bounded not token-bounded

The judge runtime ceilings calls (72) but a pathological answer could inflate per-call tokens without limit; the program's own documentation records this. [Open correctness obligation] [[Research/Software Architecture Garden/coinvault/README#13. Architecture debt and open laws|§13]]. *see also* [[#Budget accounting, hard]].

### Judging an answer

*See* [[#Judge, two-step decomposed]] and [[#Computed faithfulness]].

## M

### Maturity labels

The Garden's six-valued vocabulary applied at [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]]: **Established**, **Emergent**, **Candidate ecosystem pattern**, **Architecture debt**, **Retired**, **Open correctness obligation**. Defined at the [[Research/Software Architecture Garden/README#Pattern maturity vocabulary|Garden maturity vocabulary]]. *see also* [[#Pattern maturity assessment]].

### Mutation

Ragopt's independent computation of the single bounded asset that differs between parent and challenger; the candidate cannot self-certify its own one-change claim. [[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], [[Research/Software Architecture Garden/coinvault/README#11. Authority and identity map|§11]]. ↳ [[Research/Software Architecture Garden/ragopt/README|Ragopt]] `Mutation`. *see also* [[#Candidate bundle]], [[#One-change-per-candidate rule]], [[#Mutation surface]].

### Mutation surface

One bounded text/config asset per candidate: prompt suffixes, tool descriptions, result budgets, comparison plans, reranker config. The `grounded-answer-v2` decision mutated a single paragraph replacing an empty file. [[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], [[Research/Software Architecture Garden/coinvault/README#8. The GEPA correspondence, stated precisely|§8]]. *see also* [[#GEPA correspondence]], [[#Treatment contract]], [[#Treatment mechanisms]].

## N

### Native artifact

`gec-ragopt-native/v5`, private to the product adapter, retaining the full trace, judge score with per-statement verdicts, treatment report, contract report, budgets, and termination accounting. [[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]], [[Research/Software Architecture Garden/coinvault/README#11. Authority and identity map|§11]]. *see also* [[#Information boundary]], [[#Scalar Outcome]]. Run custody in the rag-ttc sense.

### No apply command exists

*See* [[#Human promotion authority outside the binary]]. (The promotion plan's state is fixed at `review_required` with `human_apply_required: true`; nothing in either module can mutate production.)

## O

### One-change-per-candidate rule

A sweep that varied fusion and reranking together could not attribute its winner, so the reranker is excluded from sweeps and each candidate mutates exactly one asset. [[Research/Software Architecture Garden/coinvault/README#5. Hyper-parameter search under the one-change rule|§5]], [[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]]. *see also* [[#Cached-channel hyper-parameter sweep under the one-change rule]], [[#Treatment-exercise proof]], [[#Mutation]], [[#Attribution law]].

### Open correctness obligation

*See* [[#Maturity labels]]. Concrete instance: [[#Judge spend, call-bounded not token-bounded]].

## P

### Pattern maturity assessment

The §12 table that assigns each pattern or law one maturity label with its evidence or limitation. [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]]. *see also* [[#Maturity labels]].

### Preflight environment-identity validation

Before any provider call: exact application/model profiles, *resolved* runtime identity, eight snapshot dimensions cross-checked, corpus digest, byte digests of the lexical manifest and vectors SQLite, mechanism-specific asset digests, the `ragopt_revision` against the parsed pseudo-version, and a seventeen-file source lock; `--preflight-only` exercises all of it with zero spend. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/coinvault/README#7.4 The preflight: environment identity before spend|§7.4]], [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]]. *see also* [[#Instrument freezing by version key and source lock]], [[#Source lock]], [[#Attribution law]].

### Promoting a candidate

*See* [[#Human promotion authority outside the binary]] and [[#Promotion plan]]. (Application authority is entirely human; the binary can only propose.)

### Promotion plan

The reporter's run/candidate/decision binding with state fixed at `review_required` and `human_apply_required: true`. [[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], [[Research/Software Architecture Garden/coinvault/README#11. Authority and identity map|§11]]. *see also* [[#Human promotion authority outside the binary]], [[#Gate decision]]. *Must not be confused with* application — no apply command exists.

### Projection blocks

`<gec:sources:v1>` blocks whose evidence IDs match a strict pattern and whose epistemic grade comes from a closed set; if a cited ID matches nothing the server returned, the widget build fails and surfaces as a projection-error event. [[Research/Software Architecture Garden/coinvault/README#9. Runtime grounding: the always-on loop|§9]]. *see also* [[#Runtime citation grounding with server-owned provenance]], [[#Epistemic grade]], [[#Answer contract, deterministic]].

### Proposer

`candidate.Proposer.Kind` records who proposed a candidate but changes no behavior: the proposer is recorded-but-inert, and the reflection step is a human or assistant working outside the binary. [[Research/Software Architecture Garden/coinvault/README#8. The GEPA correspondence, stated precisely|§8]]. *see also* [[#GEPA correspondence]], [[#Reflection held outside the binary]].

## R

### Reconciliation instruments

The debug recorder (on-demand SQLite with set-difference views like `missing_transport_fanout` across backend/transport/provider/frontend) and the provider-accounting reconciliation that turns unprovable spend into a closed budget. [[Research/Software Architecture Garden/coinvault/README#9. Runtime grounding: the always-on loop|§9]]. *see also* [[#Trace collector as validator]], [[#Budget accounting, hard]].

### Reflection held outside the binary

No code feeds failing traces to an LLM to author the next mutation; reflection is governed, reviewable, and slow by choice, with the candidate-pool diagnostic serving as a structured reflection input. [[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], [[Research/Software Architecture Garden/coinvault/README#8. The GEPA correspondence, stated precisely|§8]]. *see also* [[#GEPA correspondence]], [[#Proposer]], [[#Blame-assigning diagnostics as citable artifacts]].

### Reviewed suite lock (open)

`gec-chat-suite-lock/v1` with review status and reviewer date exists, but its validator is called only from tests; nothing on the `ragopt` command path proves the bundle's locked suite equals the *reviewed* suite. [Architecture debt] [[Research/Software Architecture Garden/coinvault/README#13. Architecture debt and open laws|§13]]. *see also* [[#Preflight environment-identity validation]], [[#Instrument freezing by version key and source lock]]. *Two overlapping mechanisms, one unwired.*

### RRF

Weighted reciprocal-rank fusion (k = 60, vector weight 1.0, over-fetch depth = limit × 8), applied after per-channel authorization; the knob surface of the sweep. [[Research/Software Architecture Garden/coinvault/README#1. The system under evaluation|§1]], [[Research/Software Architecture Garden/coinvault/README#5. Hyper-parameter search under the one-change rule|§5]]. *see also* [[#Cached-channel hyper-parameter sweep under the one-change rule]], [[#One-change-per-candidate rule]].

### Runtime citation grounding with server-owned provenance

`runEvidenceCache` observes every `knowledge_search` result per run and resolves the model's cited IDs against server-retrieved items; source cards can only contain server-retrieved documents, never model-authored provenance. Production and evaluation enforce the same law at the same boundary. [Established] [[Research/Software Architecture Garden/coinvault/README#9. Runtime grounding: the always-on loop|§9]], [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]]. *see also* [[#Projection blocks]], [[#EvidenceLedger]], [[#Answer contract, deterministic]].

## S

### Same-family judge caveat

`gpt-5.6-luna` judging `gpt-5.6-luna-low` answers is a labeled configuration, not a claim of judge independence; documented rather than hidden. [[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]]. *see also* [[#Judge, two-step decomposed]].

### Scalar Outcome

What Ragopt sees: faithfulness, relevance, unsupported-claim rate, citation-resolution and evidence-citation rates, contract/route booleans, abstention correctness, call counts — metrics plus an artifact digest only. [[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]]. *see also* [[#Information boundary]], [[#Native artifact]].

### Semantic identity strings

`QueryTransformID`, `RetrievalPolicyID`, and `EvidenceLedgerID` (e.g. `gec-evidence-ledger/v1;scope=run;dedupe=chunk;max_items=12;max_runes=18000`), traveling with every search result and evaluation trace so a quality delta can never silently mix two retrieval configurations. [[Research/Software Architecture Garden/coinvault/README#1. The system under evaluation|§1]], [[Research/Software Architecture Garden/coinvault/README#11. Authority and identity map|§11]]. ↳ [[Research/Software Architecture Garden/rag-ttc/03 - Reproducible Experiment Custody and Semantic Identity|rag-ttc identity]]; [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo|RAG Pattern 1]]. *see also* [[#Attribution law]], [[#EvidenceLedger]].

### Sentinel file

The mechanism that closes the held-out split: candidate bundles ship a sentinel in place of the validation data. [[Research/Software Architecture Garden/coinvault/README#14. Candidate ecosystem patterns|§14.4]]. *see also* [[#Held-out split, structurally closed]].

### Source lock

`source-lock.yaml` pinning seventeen files — including `internal/knowledge/judge.go`, the service, the tool, the eval set, `go.mod`/`go.sum`, and the prompt-pack templates — every one re-hashed at preflight. [[Research/Software Architecture Garden/coinvault/README#7.4 The preflight: environment identity before spend|§7.4]]. *see also* [[#Preflight environment-identity validation]], [[#Instrument freezing by version key and source lock]], [[#Attribution law]].

### Sticky close on unprovable spend

`CloseForUncertainProviderSpend` closes the budget for the remainder of the run when a timed-out cell cannot prove all provider spend was accounted for. [[Research/Software Architecture Garden/coinvault/README#7.2 The trace collector as validator|§7.2]]. *see also* [[#Budget accounting, hard]], [[#Trace collector as validator]].

### Strata as failure-mode taxonomy

The eval strata (guide-keyword, facet-product, multi-doc, paraphrase, schema-keyword, scope-negative, unanswerable, jargon-paraphrase, document-concentration, schema-paraphrase) are a deliberate failure-mode taxonomy, not a topic taxonomy. [[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]]. *see also* [[#Deterministic retrieval eval]].

### Structural validation of judge output

`JudgeVerdicts` rejects count mismatch, relevance outside [0,1] or non-finite, missing abstention flag, out-of-order statement refs, missing support flags, empty reasons, evidence labels outside the admitted `E1..En` ∪ `SQL1..SQLn` set, duplicate labels, and `supported: true` with no cited evidence; one repair round-trip is shared across both steps. [[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]]. *see also* [[#Judge, two-step decomposed]], [[#Computed faithfulness]]. The reporting layer keeps separate denominators so a judge outage cannot masquerade as a quality change.

## T

### Trace collector as validator

`gecRagoptTraceCollector.Observe` is not a passive recorder: it errors on duplicate provider-call IDs, tool results without matching requests, missing semantic identities, invalid effective-limit provenance, and comparison-intent disagreement; it records the full limit-resolution story per knowledge call. [[Research/Software Architecture Garden/coinvault/README#7.2 The trace collector as validator|§7.2]]. *see also* [[#Treatment-exercise proof]], [[#Budget accounting, hard]], [[#Reconciliation instruments]].

### Train/validation hygiene

The feedback split (12 cases) is for iteration; the validation split (24 held-out cases) is structurally closed until feedback passes and reproduces, and "if feedback fails, do not use validation as another source of tuning data" is enforced, not advised. [[Research/Software Architecture Garden/coinvault/README#8. The GEPA correspondence, stated precisely|§8]]. *see also* [[#Held-out split, structurally closed]].

### Triaging user feedback

*See* [[#Four-way triage table]]. (The vocabulary exists before the pipe that would use it.)

### Treatment contract

A locked asset declaring the mechanism, per-arm expected knob values, the invariant identity strings, per-case applicability, and an *exact sorted set* of required checks per mechanism; a check cannot be silently dropped. [[Research/Software Architecture Garden/coinvault/README#7.1 The treatment-exercise proof|§7.1]], [[Research/Software Architecture Garden/coinvault/README#11. Authority and identity map|§11]]. *see also* [[#Treatment-exercise proof]], [[#Treatment mechanisms]], [[#Mutation surface]]. *The declaration; the proof checks what actually happened.*

### Treatment mechanisms

The nine mechanisms: `knowledge_tool_default_results`, `knowledge_tool_forced_results`, `knowledge_comparison_decomposition`, `knowledge_comparison_intent`, `answer_grounding_prompt`, `answer_routing_prompt`, `answer_policy_prompt`, `knowledge_reranker`, `knowledge_tool_description`. [[Research/Software Architecture Garden/coinvault/README#7.1 The treatment-exercise proof|§7.1]]. *see also* [[#Treatment contract]], [[#Mutation surface]].

### Treatment-exercise proof

A measured delta counts only when the harness proves from the observed event stream that the mutation was causally live in the challenger arm and absent in the incumbent; otherwise the cell fails as `treatment_not_exercised` and the judge is never invoked. Born from six failed `default_results 5→8` experiments where "configuration is not behavior." [Candidate ecosystem pattern] [[Research/Software Architecture Garden/coinvault/README#7.1 The treatment-exercise proof|§7.1]], [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]], [[Research/Software Architecture Garden/coinvault/README#14. Candidate ecosystem patterns|§14.1]]. *The strongest original contribution; no second implementation yet.* *see also* [[#Attribution law]], [[#Treatment contract]], [[#One-change-per-candidate rule]], [[#Trace collector as validator]], [[#Configuration is not behavior]].

#### The law, in general form

A delta between arms is evidence about a mutation only if the run proves the mutation was causally live in the challenger and absent in the incumbent. Equal configuration is not equal treatment; observed behavior decides. [[Research/Software Architecture Garden/coinvault/README#7.1 The treatment-exercise proof|§7.1]].

#### The failure it was born from

Six successive `default_results 5→8` experiments measured nothing: the model supplied an explicit `limit: 5` on every knowledge call, so the mutated fallback default never determined behavior, and both arms ran identically while appearing to be an A/B experiment. [[Research/Software Architecture Garden/coinvault/README#7.1 The treatment-exercise proof|§7.1]].

#### Cell failure class

`treatment_not_exercised` — the cell fails before judging when the treatment was applicable but not exercised; the system refuses to spend judgment on a cell that cannot attribute. [[Research/Software Architecture Garden/coinvault/README#7.1 The treatment-exercise proof|§7.1]], [[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]].

### Two-step decomposed judge

*See* [[#Judge, two-step decomposed]].

## U

### Unknown-ID warnings

Expected document IDs that do not exist in the corpus surface as warnings, never silent misses, so golden-set rot is visible rather than absorbed into the metrics. [[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]]. *see also* [[#Deterministic retrieval eval]], [[#Failure-as-miss]].

### Under-counted spend

*See* [[#Sticky close on unprovable spend]] and [[#Budget accounting, hard]]. (Under-counted spend is treated as worse than a shortened campaign — the conservative move.)

## V

### Version-keyed durable cache

`CachedGeneratorWithObserver` keys flowkit's content-addressed file cache on `(step, judgePromptVersion, model, prompt)`, so bumping `judgePromptVersion` (currently `v2`) invalidates the entire judged population at once; an instrument change and a data change cannot be confused. [[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]]. *see also* [[#Instrument freezing by version key and source lock]], [[#Attribution law]].

## W

### Witness/gate separation

LLM judges produce metrics under structural validation; admission decisions are made by deterministic, product-authored constraint-first policies over those metrics; application decisions are made by humans. Three authorities, never merged. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]], [[Research/Software Architecture Garden/coinvault/README#14. Candidate ecosystem patterns|§14.3]]. *see also* [[#Computed faithfulness]], [[#Constraint-before-preference gate]], [[#Human promotion authority outside the binary]], [[#Double verdict]], [[#Gate decision]].

---

## Identity strings, schemas, and budgets

This is the index's notation table. CoinVault speaks in versioned handles and closed vocabularies; a reader will frequently think "what did `gec-ragopt-native/v5` mean again?" Look it up here, then follow the §-link.

| Handle / schema | Kind | Meaning | Where |
|---|---|---|---|
| `gec-evidence-ledger/v1` | identity string | EvidenceLedger policy: run-scoped, dedupe=chunk, budgets below. Full form `gec-evidence-ledger/v1;scope=run;dedupe=chunk;max_items=12;max_runes=18000`. | [[Research/Software Architecture Garden/coinvault/README#1. The system under evaluation|§1]], [[#EvidenceLedger]] |
| `gec-ragopt-native/v5` | artifact schema | Private native artifact: full trace, per-statement verdicts, treatment & contract reports, budgets, termination accounting. | [[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]], [[#Native artifact]] |
| `gec-chat-eval-case/v2` | case schema | Chat suite case input; cross-validated at suite level (schema cases must require both SQL tools and forbid knowledge search; authorization cases must forbid all tools). | [[Research/Software Architecture Garden/coinvault/README#7.3 The deterministic answer contract|§7.3]], [[#Answer contract, deterministic]] |
| `gec-candidate-pool-eval/v2` | artifact schema | Candidate-pool run record: bundle ID, corpus digest, suite digest, the three semantic identity strings; CLI emits its SHA. | [[Research/Software Architecture Garden/coinvault/README#4. The candidate-pool diagnostic: blame assignment as a first-class instrument|§4]], [[#Candidate-pool diagnostic]] |
| `gec-chat-suite-lock/v1` | lock schema | Reviewed-suite lock with review status and reviewer date. Validator is called only from tests — open. | [[Research/Software Architecture Garden/coinvault/README#13. Architecture debt and open laws|§13]], [[#Reviewed suite lock (open)]] |
| `EvalSet` v3 | eval schema | Strict-YAML, digest-locked 80-question golden set; one of three modes per question. | [[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]], [[#EvalSet]] |
| `judgePromptVersion` v2 | cache key component | Bumping it invalidates the entire judged population at once. | [[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]], [[#Version-keyed durable cache]] |
| `<gec:sources:v1>` | projection block | The model's source-card block; IDs must resolve against server-retrieved items. | [[Research/Software Architecture Garden/coinvault/README#9. Runtime grounding: the always-on loop|§9]], [[#Projection blocks]] |
| `QueryTransformID`, `RetrievalPolicyID`, `EvidenceLedgerID` | semantic identity strings | Travel with every search result and trace; prevent silent configuration mixing. | [[Research/Software Architecture Garden/coinvault/README#1. The system under evaluation|§1]], [[#Semantic identity strings]] |
| `source-lock.yaml` | source lock | Seventeen re-hashed files including `internal/knowledge/judge.go`, the service, tool, eval set, `go.mod`/`go.sum`, prompt-pack templates. | [[Research/Software Architecture Garden/coinvault/README#7.4 The preflight: environment identity before spend|§7.4]], [[#Source lock]] |
| Evidence budget | budgets | 12 items / 18 000 runes per EvidenceLedger. | [[Research/Software Architecture Garden/coinvault/README#1. The system under evaluation|§1]], [[#EvidenceLedger]] |
| RAGOPT hard budgets | budgets | 216 answer calls / 192 embeddings / 72 judge calls / 1 000 000 answer tokens; any deviation is an error. | [[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], [[#Budget accounting, hard]] |
| Limit-resolution sources | closed vocabulary | `server_forced | explicit | default | explicit_clamped` — the provenance the treatment proof needs. | [[Research/Software Architecture Garden/coinvault/README#7.2 The trace collector as validator|§7.2]], [[#Trace collector as validator]] |
| Epistemic grades | closed vocabulary | `measured | estimate | association | hypothesis`. | [[Research/Software Architecture Garden/coinvault/README#9. Runtime grounding: the always-on loop|§9]], [[#Epistemic grade]] |
| Diagnosis classes (6) | closed vocabulary | Absent; below fused cutoff; removed by scope; below budget; below budget with concentration; admitted at final depth. | [[Research/Software Architecture Garden/coinvault/README#4. The candidate-pool diagnostic: blame assignment as a first-class instrument|§4]], [[#Diagnosis classes]] |
| Treatment mechanisms (9) | closed vocabulary | default/forced result budgets; comparison decomposition/intent; grounding/routing/policy prompts; reranker; tool description. | [[Research/Software Architecture Garden/coinvault/README#7.1 The treatment-exercise proof|§7.1]], [[#Treatment mechanisms]] |
| Component evidence ledger statuses (6) | closed vocabulary | `structurally_invalid`, `component_rejected`, `historically_supported`, `conditional_evidence`, `release_rejected`, `release_promoted`. | [[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]], [[#Component evidence ledger]] |
| Eval strata (10) | failure-mode taxonomy | guide-keyword, facet-product, multi-doc, paraphrase, schema-keyword, scope-negative, unanswerable, jargon-paraphrase, document-concentration, schema-paraphrase. | [[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]], [[#Strata as failure-mode taxonomy]] |

---

## Cross-reference summary

The concepts above connect to the wider Garden through a small number of load-bearing correspondences. Each is a *correspondence*, not an equivalence: the Garden's discipline is that a registry is not authority, a snapshot is not always an immutable release, and a UI event is not a mounted occurrence.

- **Identity is a deliberate scoped projection, not incidental serialization** — [[#Attribution law]], [[#Semantic identity strings]], [[#Authority and identity map]]. ↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo|RAG Pattern 1]].
- **Exact experimental coordinates form a finite product** — [[#Cell]], [[#Candidate bundle]], [[#Mutation]]. ↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo|RAG Pattern 8]].
- **Constraint-first decisions and partial preference** — [[#Constraint-before-preference gate]], [[#Witness/gate separation]]. ↳ [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo|RAG Pattern 9]].
- **Run custody retains configuration, inputs, observations, status, and results under one coordinate** — [[#Cell]], [[#Native artifact]]. ↳ [[Research/Software Architecture Garden/rag-ttc/03 - Reproducible Experiment Custody and Semantic Identity|rag-ttc run custody]].

Patterns marked *Candidate ecosystem pattern* ([[#Treatment-exercise proof]], [[#Instrument freezing by version key and source lock]], [[#Witness/gate separation]], [[#Blame-assigning diagnostics as citable artifacts]], [[#Held-out split, structurally closed]], [[#Candidate-pool diagnostic]], [[#Judge, two-step decomposed]], [[#Preflight environment-identity validation]]) have at most Ragopt/rag-ttc extraction lineage as a second occurrence — the same caveat the [[Research/Software Architecture Garden/ragopt/README|Ragopt study]] records for its own consumer evidence — and so remain candidates until an independent implementation confirms them.

## Related documents

- [[Research/Software Architecture Garden/coinvault/README|CoinVault study]] — the evidence-pinned source this index catalogues.
- [[Research/Software Architecture Garden/coinvault/Index of Design Patterns - Rationale|Rationale]] — why each term was chosen and why it belongs.
- [[Research/Software Architecture Garden/README|Software Architecture Garden]] — the Garden root and its maturity vocabulary.
