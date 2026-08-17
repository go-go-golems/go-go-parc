---
title: "rag-ttc Composition Pass Playbook"
subtitle: "Second-pass integration and evaluation protocol"
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

The first-pass projects intentionally avoid shared implementation dependencies. The second pass asks a different question: do the independently refined contracts compose into a coherent RAG system, and where do local guarantees fail at subsystem boundaries?

Composition is not a mass merge of all student branches. It is a sequence of controlled replacement experiments. At each step, one local fake is replaced by another team’s implementation while the same neutral fixtures, conformance laws, and sealed artifacts are rerun.

# Entry criteria

A project is eligible for composition when it provides:

- a versioned public contract and neutral schemas;
- a standalone implementation with deterministic test mode;
- a rag-ttc adapter or compatibility fixture;
- `results.json` and a sealed artifact bundle;
- at least one counterexample and one intentionally bad implementation/test double;
- a clear equality/comparison function for its semantic output;
- no hidden dependency on another student branch.

Projects that do not meet the criteria can still participate through their fixture contracts, but their code is not placed on the critical integration path.

# Integration principles

1. **Replace one boundary at a time.** Preserve a known-good oracle or fixture at every step.
2. **Compare semantics and traces separately.** A faster or differently scheduled run may be semantically equal.
3. **Keep candidates and views separate.** Do not use top-k equality as evidence that candidate states agree.
4. **Preserve alternative derivations.** Do not collapse provenance merely to make two implementations look equal.
5. **Make partial failure explicit.** Empty, unavailable, failed, skipped, and cancelled are distinct.
6. **Version all contracts.** A migration is an experiment, not a silent compatibility assumption.
7. **Use recorded effects first.** Only after deterministic composition passes should live providers be introduced.
8. **Treat security projection as a boundary, not a final filter.** Run both secure and intentionally insecure orderings.

# Core composition ports

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

# Recommended integration order

## Stage A - identity and artifact custody

Integrate P01 with P10 first.

- Replace P10 local fingerprint fake with P01.
- Seal one result from each project.
- Verify that identity versions, source snapshot hashes, and no-secret rules are consistently represented.
- Introduce one deliberate identity version change and test rejection/migration.

**Gate A:** Every project output can be sealed and verified; semantic IDs are unambiguous and versioned.

## Stage B - facts, merge, and storage

Integrate P02, P03, and P12.

- Store the P02 diamond provenance state in all P12 exact backends.
- Join independently produced states through P03 before and after persistence.
- Verify facts, alternative derivations, conflicts, and canonical serialization.
- Migrate v1 to v2 and run the P02 verifier on both paths.

**Gate B:** Exact backends preserve one fact/provenance semantics; merge and migration laws pass.

## Stage C - candidates, views, and execution

Integrate P03, P04, and P06.

- Produce candidate deltas through P06 sequential, cached, retried, batched, and parallel execution.
- Join them through P03.
- Apply P04 ranking/packing after an explicit barrier.
- Compare semantic candidates, selected views, and traces separately.

**Gate C:** Operational policy changes do not alter candidate state or fixed-policy views under declared preconditions.

## Stage D - recursive knowledge and connected retrieval

Integrate P05, P07, and P08, using P03/P04/P06 underneath.

- Expose P07 discovery operations as P05 rules.
- Evaluate fixed depth and saturation over the multi-hop fixture.
- Combine baseline and knowledge channel candidates in P08.
- Apply P04 views and retain knowledge paths/provenance.
- Compare current-compatible and lossless diagnostic policies.

**Gate D:** Multi-hop candidate closure, connected composition, and final views have distinct, reproducible contracts.

## Stage E - tool controller and citations

Integrate P09 with P06 and P08.

- Make connected retrieval one recorded tool.
- Run completion permutations and retry/failure scenarios.
- Select and label through the shared view layer.
- Verify citation levels against the integrated fact/provenance bundle.

**Gate E:** Tool scheduling changes only trace; selected evidence and citation resolution are deterministic under fixed policy.

## Stage F - updates and security

Integrate P11 and P13 across the assembled stack.

- Apply source additions and retractions to recursive knowledge/connected candidates.
- Compare incremental and full rebuild.
- Project authorized state before views and generation.
- Test cross-user cache, tool, trace, and artifact boundaries.
- Seal every snapshot and security report through P10.

**Gate F:** Updates preserve semantic laws, and restricted input changes do not alter declared low-authority observations.

# Integrated scenarios

## S1 - Deterministic one-shot hybrid RAG

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

## S2 - Recursive knowledge RAG

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

## S3 - Tool-using answer

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

## S4 - Live corpus update

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

## S5 - Multi-tenant secure RAG

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

## S6 - Backend and schema migration

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

# Pairwise compatibility test matrix

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

# Integrated law suite

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

# Conflict resolution protocol

Independent projects will make incompatible choices. Resolve them through experiments, not committee intuition.

1. State both contracts in neutral terms.
2. Identify the observable behavior on which they disagree.
3. Construct the smallest fixture that distinguishes them.
4. Run each implementation and a simple oracle if possible.
5. Assess correctness, compatibility, ergonomics, performance, and composition impact separately.
6. Select one, version both as alternatives, or define a narrower common contract.
7. Preserve the counterexample and decision record in the compendium.

Never erase a meaningful conflict by weakening equality to compare only final answer strings.

# Ablation plan

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

# User-study and exploratory evaluation

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

# Composition artifacts

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

# Stop conditions

Stop the composition pass when:

- all six scenarios have a reproducible baseline;
- every core port has at least one successful replacement test;
- every failed law has a minimal fixture and classified cause;
- no unresolved conflict is hidden by final-output-only comparison;
- security and artifact verification gates pass for the recommended stack;
- remaining work is optimization, broader dataset validation, or optional feature expansion rather than unclear semantics.

# Final synthesis report structure

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
