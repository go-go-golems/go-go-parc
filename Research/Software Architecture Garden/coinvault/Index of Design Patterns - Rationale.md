---
title: CoinVault — Index of Design Patterns (Rationale)
aliases:
  - CoinVault index rationale
  - why each CoinVault index term belongs
status: active
type: architecture-garden-index-rationale
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
  - rationale
related_notes:
  - "[[Research/Software Architecture Garden/coinvault/README]]"
  - "[[Research/Software Architecture Garden/coinvault/Index of Design Patterns]]"
  - "[[Research/Software Architecture Garden/README]]"
---

# CoinVault — Index of Design Patterns (Rationale)

This document is the companion to the [[Research/Software Architecture Garden/coinvault/Index of Design Patterns|CoinVault index]]. An index is only as good as its omissions: a back-of-the-book index that lists every noun is useless. So this document states the principles that earned a term an entry, then justifies each entry in the index — what kind of evidence grounds it, and what a reader loses if it is dropped. Read it as the editor's marginalia on the index, not as a second pass through the study.

The index is a deliberate **hybrid**: a glossary (one-sentence *what does this mean?*) folded into an index (locators — *where can I read about this?*), because the task asked for both a short description and links. It follows two disciplines that sharpened the revision. First, the index/glossary/notation separation: the notation table ([[Index of Design Patterns#Identity strings, schemas, and budgets]]) carries the versioned handles and closed vocabularies a reader will look up as "what did `gec-ragopt-native/v5` mean again?", rather than burying them in the alphabetic list. Second, the reader-memory rule — *index according to how readers might remember the knowledge, not how the author happened to phrase it* — which is why the index carries many `See` redirects from alternate phrasings ("configuration is not behavior" → Treatment-exercise proof) and why every entry is a heading so every `See` and `see also` is a proper clickable anchor.

The evidence and provenance are inherited from the [[Research/Software Architecture Garden/coinvault/README|CoinVault study]] (commit `10d1a8d8`, branch `task/deploy-dev-indexer`, analysis date 2026-08-14). Where the study cites a file and line, the index links to the study section that does the citing; this rationale never claims evidence the study did not first pin.

## The five principles of selection

A term earned an index entry only if it satisfied one or more of these. The principles are ordered by how much value an entry adds when a reader meets the concept cold.

1. **It distinguishes two things that are easy to conflate.** The Garden's central discipline is anti-flattening: a registry is not authority, a snapshot is not always an immutable release, configuration is not behavior, a judge is not a gate, a gate pass is not promotion. The CoinVault study is unusually rich in these distinctions because it was built by being burned by them — the treatment-exercise proof exists because six experiments conflated configuration with behavior. An entry that prevents a conflation is the most valuable kind, because the conflation is the failure mode the system was designed to make impossible.

2. **It is evidence-backed, not prose-backed.** A term names something with concrete code, tests, a recorded failure, or a deployment artifact in the pinned snapshot, ranked by the Garden's [[Research/Software Architecture Garden/README#Evidence hierarchy|evidence hierarchy]] (runtime code and public interfaces above tests above consumers above build above design docs above git history above comments). Pure intent recorded only in a comment did not earn an entry unless it named a Garden-defined term.

3. **It is transferable or it must travel intact.** A term belongs if it names a *candidate ecosystem pattern* — a structure stable enough to compare across repositories — or if it is a vocabulary term that must be carried unchanged for cross-project comparison to be honest. The semantic identity strings and the attribution law are the clearest case: they are local names for a relation the wider Garden and the [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo|RAG Pattern Zoo]] already recognize, so the index gives them their canonical name and a `↳` link rather than inventing a new one.

4. **It carries an operational consequence.** A term belongs if naming it tells an operator something about cost, budget, failure, or limit — the instrument ladder (cost ordering), hard budgets (ceilings), sticky close on unprovable spend (the conservative move), failure-as-miss (don't abort the baseline), the same-family judge caveat (label, don't hide). These entries make the index useful to someone running the system, not only to a taxonomist.

5. **It is Garden-defined vocabulary.** The maturity labels and the authority/identity map categories are the Garden's own language. They belong so the index speaks the same dialect as every other entry in the Garden and can be read alongside them.

## What was deliberately excluded

A good index is defined by what it leaves out. Three classes of thing appear in the study but were not given entries, and the reason matters:

- **The chatbot's own retrieval machinery** — BM25 lexical scoring, vector kNN, chunk sizes (1600/200/120 runes), cross-encoder reranking, shingle-frequency boilerplate stripping. The study treats these as *the system under evaluation*, not the measuring apparatus, and they are the subject of the [[Research/Software Architecture Garden/ragkit/README|Ragkit]] entry. Indexing them here would duplicate Ragkit's own index once it exists; the CoinVault index points to Ragkit instead.
- **Routine composition over upstream Garden projects** — the Geppetto tool loop, Pinocchio chat composition, Sessionstream event/timeline streaming. These are documented in their own entries; CoinVault's contribution is the apparatus *around* the chatbot, and the index reflects that scope.
- **One-off identifiers with no conceptual weight** — Go field names, config filenames, and CLI flag names, except where the name *is* the concept (`EvidenceLedger`, `EvalSet`, `source-lock.yaml`, the `gec-ragopt-native/v5` artifact schema, the `gec-evidence-ledger/v1` policy string). These last are included because they are the durable handles a reader will meet in the code and the receipts, and because they are identity coordinates, not implementation detail.

The exclusion principle is the Garden's own: one repository establishes local evidence; ecosystem guidance requires comparison. The index indexes what CoinVault *contributes or hardens*, and points outward for what it merely consumes.

## Per-term rationale

Entries are alphabetical to match the index, so a reader can move between the two documents in parallel. Each gives a category, the reason it was chosen, and the reason it belongs — what is lost if it is omitted. Categories: **Pattern** (a design pattern with a maturity label), **Law** (a stated invariant), **Vocabulary** (a named object, identity string, or artifact schema), **Failure mode** (a named class of failure), **Debt/Open** (architecture debt or open obligation), **Garden term** (Garden-defined vocabulary).

### Attribution law — Law
> Index entry: [[Index of Design Patterns#Attribution law]].

**Chosen because** it is stated as the repository's governing idea *before any loop is described* ([[Research/Software Architecture Garden/coinvault/README#1. The system under evaluation|§1]]): a measurement is attributable only when every cause is frozen-and-digest-identified or observed-and-recorded. It is the axiom from which the semantic identity strings, the preflight, the source lock, and the version-keyed cache all derive.

**Belongs because** without it the rest of the index reads as a bag of mechanisms. It is the one entry that lets a reader see *why* the system is so elaborate about identity: the elaboration is the cost of making the attribution law hold. Drop it and the treatment-exercise proof, the preflight, and the version-keyed cache become unexplained ceremony.

### Answer contract, deterministic — Pattern (candidate)
> Index entry: [[Index of Design Patterns#Answer contract, deterministic]].

**Chosen because** it is a staged, self-validating report (`FirstFailure` names the first responsible stage; the report's `Valid` flag must agree with the conjunction of its own checks) that runs *before* any model judges anything ([[Research/Software Architecture Garden/coinvault/README#7.3 The deterministic answer contract|§7.3]]).

**Belongs because** it instantiates a transferable shape — deterministic contracts as a cheaper, faster gate than a judge — and because its self-validation is a small but sharp law (a report that disagrees with its own checks is a hard error). Omitting it would let a reader assume the judge is the only quality check, which is exactly the witness/gate confusion the system refuses.

### Authority and identity map — Vocabulary
> Index entry: [[Index of Design Patterns#Authority and identity map]].

**Chosen because** §11 is a single table that pins every object family to its owner, its identity coordinate, and the thing it must not be confused with — the densest expression of the attribution law in the study.

**Belongs because** it is the index's spine. Most other entries are rows of this table elaborated into prose. A reader who holds this map can place any pattern in the index ("is this a candidate, a cell, a native artifact, a gate decision?") without re-reading the loops. It is also the local instance of a Garden-wide correspondence ([[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 1 — Semantic Identity as Explicit Projection|RAG Pattern 1]]), so it travels.

### Blame-assigning diagnostics as citable artifacts — Pattern (candidate ecosystem)
> Index entry: [[Index of Design Patterns#Blame-assigning diagnostics as citable artifacts]].

**Chosen because** it is one of the five named [[Research/Software Architecture Garden/coinvault/README#14. Candidate ecosystem patterns|candidate ecosystem patterns]] and it generalizes a relation: a cheap instrument that reports *where* a failure happened, digest-addressed, and cited by the hypothesis of every expensive experiment ([[Research/Software Architecture Garden/coinvault/README#4. The candidate-pool diagnostic: blame assignment as a first-class instrument|§4]], §14.5).

**Belongs because** it is the bridge between the cheap and expensive rungs of the instrument ladder — the mechanism by which "nothing enters the expensive loop on intuition alone" is actually enforced. Drop it and the ladder reads as six independent loops rather than a discipline where the cheap rung justifies the expensive one.

### Budget accounting, hard — Pattern (established)
> Index entry: [[Index of Design Patterns#Budget accounting, hard]].

**Chosen because** provider spend is fenced with pre-reservation, seeded on resume, and stickily closed when it cannot be proven accounted for, with a recorded operational incident driving the retry wrapper ([[Research/Software Architecture Garden/coinvault/README#7.2 The trace collector as validator|§7.2]], §12). It satisfies principle 4 (operational consequence) directly.

**Belongs because** "under-counted spend is treated as worse than a shortened campaign" is a real governance position, not an implementation detail. A reader who skips this entry will not understand why a timed-out cell closes the budget for the *whole remainder* of the run — the conservative move that distinguishes this harness from an optimistic one.

### Cached-channel hyper-parameter sweep under the one-change rule — Pattern (established)
> Index entry: [[Index of Design Patterns#Cached-channel hyper-parameter sweep under the one-change rule]].

**Chosen because** it is an established pattern with a clever cost trick (retrieve both channels once, re-fuse in memory for all 30 cells) and a discipline (force-include the serving-default cell; exclude the reranker so the winner is attributable) ([[Research/Software Architecture Garden/coinvault/README#5. Hyper-parameter search under the one-change rule|§5]], §12).

**Belongs because** it is the cheapest rung that already applies the one-change rule — the same rule the expensive RAGOPT loop depends on. It shows the attribution discipline operating where no judge and no causal proof is involved, which is what makes the discipline a *habit* of the codebase rather than a feature of one loop.

### Candidate bundle — Vocabulary
> Index entry: [[Index of Design Patterns#Candidate bundle]].

**Chosen because** it is the unit the expensive loop freezes: a parent/challenger pair differing in exactly one asset, independently verified by Ragopt's `Mutation` ([[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], §11).

**Belongs because** "exactly one mutable asset, independently verified" is the boundary that makes a candidate a valid experiment rather than a confounded change. A reader who does not hold this term will confuse a candidate with an applied change or with the run that measures it — the exact conflation §11 warns against.

### Candidate-pool diagnostic — Pattern (candidate ecosystem)
> Index entry: [[Index of Design Patterns#Candidate-pool diagnostic]].

**Chosen because** it is the 950-line instrument that reports *where* retrieval failed across nine stages and six diagnosis classes, and it is cited by candidate hypotheses via `diagnostic_manifest_digest` ([[Research/Software Architecture Garden/coinvault/README#4. The candidate-pool diagnostic: blame assignment as a first-class instrument|§4]], §12).

**Belongs because** it is the concrete realization of "blame-assigning diagnostics as citable artifacts." It is also the study's candidate for generalization with the strongest single implementation, so it earns a separate entry from the abstract pattern: the pattern is the *relation*, the diagnostic is the *instance*, and both are load-bearing.

### Cell — Vocabulary
> Index entry: [[Index of Design Patterns#Cell]].

**Chosen because** it is the exact evaluation coordinate — run config + (suite, policy, candidate, snapshot, case, repeat, arm) + hash chain — and the study is emphatic that a cell is not a retry attempt and not a production session ([[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], §11).

**Belongs because** "repeat is not retry" is the kind of distinction (principle 1) that, if lost, makes an experiment corpus unreadable. It is the local name for [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 8: Exact Experimental Coordinates and Explicit Coupling|RAG Pattern 8]], so it travels, and the index gives it the canonical coordinate language.

### Component evidence ledger — Vocabulary
> Index entry: [[Index of Design Patterns#Component evidence ledger]].

**Chosen because** it accumulates cross-candidate statuses (`structurally_invalid` … `release_promoted`) and is the place where the study records that no entry has ever reached `release_promoted` — "treated as information, not embarrassment" ([[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]]).

**Belongs because** it is the mechanism that holds the double verdict apart: a component can be `historically_supported` (causal learning) while the release gate says `release_rejected` (gate outcome). Without this entry the double verdict has no home, and a reader cannot see *where* the two results are kept separate.

### Computed faithfulness — Vocabulary
> Index entry: [[Index of Design Patterns#Computed faithfulness]].

**Chosen because** faithfulness is computed as supported-over-total from structurally validated verdicts; the model is "never asked for a score it could flatter" ([[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]]).

**Belongs because** it is the sharpest instance of witness/gate separation: the judge's headline metric is *not* the judge's opinion but a deterministic function of the judge's structured output. Drop it and "the judge is a witness, not a gate" is a slogan; with it, the slogan has a mechanism.

### Concentration crowd-out — Failure mode
> Index entry: [[Index of Design Patterns#Concentration crowd-out]].

**Chosen because** it is one of the six diagnosis classes — the duplicate-chunk failure fired when the surviving top slice is dominated by more than two chunks of a single document ([[Research/Software Architecture Garden/coinvault/README#4. The candidate-pool diagnostic: blame assignment as a first-class instrument|§4]]).

**Belongs because** it is a real, named retrieval failure that a flat relevance metric hides. It earns an entry on principle 4 (operational consequence): a reader diagnosing "the right document was retrieved but the answer was wrong" needs this name.

### Constraint-before-preference gate — Pattern
> Index entry: [[Index of Design Patterns#Constraint-before-preference gate]].

**Chosen because** the lexicographic policy (hard constraints → target → regressions → cost tie-breakers) appears in three places — the sweep's `BestCell`, the in-process A/B verdict `retrievalSummaryWins`, and the RAGOPT gate — so it is a recurring shape, not a one-off ([[Research/Software Architecture Garden/coinvault/README#5. Hyper-parameter search under the one-change rule|§5]], §3, §8).

**Belongs because** it is the local name for [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 9: Constraint-First Decisions and Partial Preference|RAG Pattern 9]] and the inherited shape from [[Research/Software Architecture Garden/ragopt/README#6. Feasibility precedes preference|Ragopt]]. Its recurrence across three cost points is what makes it a habit of the codebase, so it belongs even though it is inherited rather than novel.

### Determinism by prefix derivation — Pattern
> Index entry: [[Index of Design Patterns#Determinism by prefix derivation]].

**Chosen because** it is a non-obvious cost trick: retrieve once at maximum depth and derive shallower depths as a stable prefix, eliminating depth-dependent nondeterminism at one embedding call per question ([[Research/Software Architecture Garden/coinvault/README#4. The candidate-pool diagnostic: blame assignment as a first-class instrument|§4]]).

**Belongs because** it is the reason the candidate-pool diagnostic is *cheap enough to run broadly* — principle 4 again. It is local to the diagnostic, but it is the kind of determinism-preserving trick that transfers to any multi-depth evaluation, so it earns an entry rather than a sentence.

### Deterministic retrieval eval — Pattern (established)
> Index entry: [[Index of Design Patterns#Deterministic retrieval eval]].

**Chosen because** it is the bottom rung of the ladder and an established pattern with visible operational hardening: failure-as-miss, unknown-ID warnings, mode-per-question enforcement, grouped any-of expectations ([[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]], §12).

**Belongs because** it is the foundation every other loop's attribution rests on — "instruments are frozen before they measure" starts here, with the digest-locked 80-question set. A reader who skips it cannot tell what the sweep sweeps over or what the diagnostic diagnoses.

### Diagnosis classes — Vocabulary
> Index entry: [[Index of Design Patterns#Diagnosis classes]].

**Chosen because** the six classes (absent, below fused cutoff, removed by scope, below budget, below budget with concentration, admitted at final depth) are a typed failure-mode taxonomy, not free-form labels ([[Research/Software Architecture Garden/coinvault/README#4. The candidate-pool diagnostic: blame assignment as a first-class instrument|§4]]).

**Belongs because** a typed taxonomy is what makes the diagnostic *machine-readable* and therefore *citable* by candidate hypotheses. Drop it and the candidate-pool diagnostic reads as a report a human reads, not a coordinate a candidate binds to.

### Double verdict — Law
> Index entry: [[Index of Design Patterns#Double verdict]].

**Chosen because** the study states that *gate outcome* and *causal learning* are different results, and that conflating them is "the category error the program's own evidence ledger later diagnosed in itself" ([[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]]).

**Belongs because** it is the highest-level distinction in the study (principle 1) and it is *self-correcting*: the system made the error, then built the component evidence ledger to keep the two verdicts apart. An index for a discipline built from failure must include the failure it most explicitly learned from.

### Epistemic grade — Vocabulary
> Index entry: [[Index of Design Patterns#Epistemic grade]].

**Chosen because** every projection block's epistemic claim must come from the closed set `measured | estimate | association | hypothesis` ([[Research/Software Architecture Garden/coinvault/README#9. Runtime grounding: the always-on loop|§9]]).

**Belongs because** it is a small, closed-set discipline that prevents the model from inventing a confidence vocabulary. It is the kind of vocabulary boundary (principle 1) that transfers to any grounded-answer UI, and it is paired with the strict evidence-ID pattern in projection blocks.

### EvalSet — Vocabulary
> Index entry: [[Index of Design Patterns#EvalSet]].

**Chosen because** it is the durable handle (version 3, digest-locked) for the golden set, and `validateEvalQuestion` rejects zero-or-two-mode questions — a contract, not a file ([[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]]).

**Belongs because** it participates in instrument freezing: the eval set's digest is one of the seventeen source-locked files and one of the preflight dimensions. A reader will meet `EvalSet` in the code and the receipts, so the index gives the canonical name and the version that the cache key depends on.

### EvidenceLedger — Vocabulary
> Index entry: [[Index of Design Patterns#EvidenceLedger]].

**Chosen because** it is the run-scoped admission structure (`gec-evidence-ledger/v1`, max 12 items / 18 000 runes) that assigns the stable `E1..En` labels the answer and the judge both cite, and its `PolicyID` is one of the three semantic identity strings ([[Research/Software Architecture Garden/coinvault/README#1. The system under evaluation|§1]]).

**Belongs because** it is the shared contract between production grounding and evaluation — "production and evaluation enforce the same law at the same boundary." That shared contract is what makes eval results transferable to production behavior at all, which is the study's reason for being. Omitting it would leave the most important boundary unnamed.

### Failure-as-miss — Failure mode
> Index entry: [[Index of Design Patterns#Failure-as-miss]].

**Chosen because** a per-question search failure is scored as a miss rather than aborting the run, "so one transport error cannot erase a baseline" ([[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]]).

**Belongs because** it is a recorded operational lesson (principle 4) and a governance choice: the eval is biased toward *not* producing a false-clean baseline. It pairs with unknown-ID warnings to show a harness built by people who were burned by silent rot.

### Four-way triage table — Vocabulary
> Index entry: [[Index of Design Patterns#Four-way triage table]].

**Chosen because** it is the designed classification that would turn a production complaint into either a candidate or a corpus fix, and it exists *before* the pipe that would use it ([[Research/Software Architecture Garden/coinvault/README#10. Human feedback: collected, not yet closed-loop|§10]]).

**Belongs because** it embodies the study's ordering principle — "the triage vocabulary exists before the pipe" — which is itself a candidate ecosystem lesson. It earns an entry even though the pipe is unbuilt, because the vocabulary is the part that is done.

### Gate decision — Vocabulary
> Index entry: [[Index of Design Patterns#Gate decision]].

**Chosen because** the gate decision is the output of a *pure policy evaluator* over the comparison (policy byte + semantic digests), and §11 insists it is "not promotion, not scientific proof" ([[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], §11).

**Belongs because** it is one term in a chain of four that must stay distinct — gate decision, gate pass, promotion plan, application — and each of the four is a different authority. The index lists them separately so a reader cannot collapse "the gate passed" into "we shipped it."

### GEPA correspondence — Law
> Index entry: [[Index of Design Patterns#GEPA correspondence]].

**Chosen because** §8 is an explicit table of what CoinVault adopts from GEPA-style reflective optimization (bounded mutations, rich trajectories, frozen metrics, iterative candidates) and what it rejects (automated reflection, population search, self-applied winners) ([[Research/Software Architecture Garden/coinvault/README#8. The GEPA correspondence, stated precisely|§8]]).

**Belongs because** the rejection half is a governance position, not missing infrastructure, and it is recorded in three standing rules. An index entry for it lets a reader see the whole apparatus as a *stance* about autonomy, which is the study's intellectual contribution, not merely its engineering.

### Grouped any-of expectations — Vocabulary
> Index entry: [[Index of Design Patterns#Grouped any-of expectations]].

**Chosen because** the two-level structure (any-of within a group, complementary groups) encodes a real property of retrieval ground truth that flat relevance lists cannot ([[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]]).

**Belongs because** it is a small, precise answer to "why not just a relevance list?" — the kind of design rationale (principle 1) that, if omitted, makes the eval's coverage metric look arbitrary. Documents within a group are interchangeable evidence for one facet; the groups are jointly necessary. That is a semantic claim worth indexing.

### Hard budget accounting — see Budget accounting, hard
> Index entry: [[Index of Design Patterns#Budget accounting, hard]].

A redirect, not a duplicate entry. It belongs because "hard" is the natural search term a reader will reach for, and a back-of-the-book index that makes the reader hunt for the canonical spelling has failed.

### Held-out split, structurally closed — Pattern (candidate ecosystem)
> Index entry: [[Index of Design Patterns#Held-out split, structurally closed]].

**Chosen because** leakage is prevented by mechanism (a sentinel file plus a hard CLI error), not by convention, and the rule "if feedback fails, do not use validation as another source of tuning data" is enforced, not advised ([[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]], §14.4).

**Belongs because** "prevented by mechanism, not convention" is the strongest form of a discipline and the rarest in ML practice. It is one of the five named candidate ecosystem patterns, and it transfers to any system with a held-out set.

### Human feedback store — Vocabulary
> Index entry: [[Index of Design Patterns#Human feedback store]].

**Chosen because** it is the production-side evidence loop (votes, bounded tags, append-only comments) that is collected but not yet closed-loop ([[Research/Software Architecture Garden/coinvault/README#10. Human feedback: collected, not yet closed-loop|§10]]).

**Belongs because** it is the open edge the study names as "the largest open edge of the system," and an index that omits the biggest gap is dishonest. It pairs with the four-way triage table to show the loop that is *designed and unbuilt*.

### Human promotion authority outside the binary — Pattern (established, inherited)
> Index entry: [[Index of Design Patterns#Human promotion authority outside the binary]].

**Chosen because** the promotion plan is fixed at `review_required` with `human_apply_required: true` and no apply command exists in either module ([[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], §12).

**Belongs because** "autonomy ends at evidence; application authority is entirely human" is the third of the three governance rules and the one that most sharply distinguishes CoinVault from autonomous GEPA. It is inherited from Ragopt, which is why the entry says so — the index must not claim CoinVault originated it.

### Information boundary — Pattern
> Index entry: [[Index of Design Patterns#Information boundary]].

**Chosen because** Ragopt sees only scalars and an artifact digest while the full trace stays in the private native artifact, so the generic kernel is reusable across products without leaking product data ([[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]]).

**Belongs because** it is a clean separation-of-authorities (principle 1) and the contractual surface that lets CoinVault consume Ragopt as a pinned library. It is the reason a reusable experiment kernel can exist at all in a product-specific codebase.

### Instrument freezing by version key and source lock — Pattern (candidate ecosystem)
> Index entry: [[Index of Design Patterns#Instrument freezing by version key and source lock]].

**Chosen because** every score-producing component (judge prompts, judge implementation, eval set, harness source, dependency revision) participates in a frozen, digest-verified identity checked before spend; changing the instrument invalidates the population by construction ([[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]], §7.4, §14.2).

**Belongs because** it is the operational form of the attribution law (principles 2 and 3) and the second of the three governance rules — "instruments are frozen before they measure." It is also one of the five candidate ecosystem patterns, so it is meant to travel.

### Instrument ladder — Vocabulary
> Index entry: [[Index of Design Patterns#Instrument ladder]].

**Chosen because** the six loops are ordered by cost and epistemic strength, and the ordering is the discipline: cheap deterministic instruments justify the expensive causal loop ([[Research/Software Architecture Garden/coinvault/README#2. The instrument ladder|§2]]).

**Belongs because** it is the single image that organizes the whole apparatus. A reader who holds the ladder can place any other entry on its rung; without it, the six loops look redundant. It earns its place as the index's conceptual map even though it names no single mechanism.

### Judge, two-step decomposed — Pattern (candidate ecosystem)
> Index entry: [[Index of Design Patterns#Judge, two-step decomposed]].

**Chosen because** the two-step separation (extraction sees Q+A never evidence; verdicts see statements+evidence never the freedom to restate) is "the point," and the judge is ported from rag-ttc with documented lineage ([[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]], §12).

**Belongs because** the separation is what makes faithfulness computable and what makes the judge a witness rather than a gate. It is also the entry where the same-family caveat and the version-keyed cache attach, so it is a hub for three related terms.

### Judge spend, call-bounded not token-bounded — Debt/Open
> Index entry: [[Index of Design Patterns#Judge spend, call-bounded not token-bounded]].

**Chosen because** it is one of the three named open laws and the study records it in "the program's own textbook" — the budget counts tokens for the answer path but not for the judge ([[Research/Software Architecture Garden/coinvault/README#13. Architecture debt and open laws|§13]]).

**Belongs because** an index that lists only the established patterns and hides the open obligation would flatter the system. This entry is the honest counterweight to "hard budget accounting": the budget is hard where it is enforced and admitted-bounded where it is not.

### Maturity labels — Garden term
> Index entry: [[Index of Design Patterns#Maturity labels]].

**Chosen because** the six labels (Established, Emergent, Candidate ecosystem pattern, Architecture debt, Retired, Open correctness obligation) are the Garden's own vocabulary, applied at [[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]] and defined at the [[Research/Software Architecture Garden/README#Pattern maturity vocabulary|Garden root]].

**Belongs because** the index uses these labels as trailing brackets on every pattern entry, so a reader needs the key in the same document. It also satisfies the user's explicit ask to include the project's vocabulary, and the maturity vocabulary is the one piece that is shared across every future Garden index.

### Mutation — Vocabulary
> Index entry: [[Index of Design Patterns#Mutation]].

**Chosen because** Ragopt's `Mutation` is the *independent* computation of the single differing asset — the candidate cannot self-certify its own one-change claim ([[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], §11).

**Belongs because** "independently verified" is the load-bearing word: it is what makes the one-change rule a *proof* rather than a *promise*. Drop it and a reader might think the candidate declares its own mutation, which would undo the attribution discipline at its root.

### Mutation surface — Vocabulary
> Index entry: [[Index of Design Patterns#Mutation surface]].

**Chosen because** the mutation surface is deliberately narrow — one bounded text/config asset per candidate — and the `grounded-answer-v2` decision mutated a single paragraph replacing an empty file ([[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], §8).

**Belongs because** narrowness is the discipline (principle 1 against confounded changes) and the GEPA correspondence row where CoinVault is "identical in kind; narrower per step." Indexing it lets a reader see *how* the one-change rule is bounded in practice.

### Native artifact — Vocabulary
> Index entry: [[Index of Design Patterns#Native artifact]].

**Chosen because** `gec-ragopt-native/v5` is the private, product-side artifact that retains the full trace, judge score, treatment and contract reports, budgets, and termination accounting ([[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]], §11).

**Belongs because** it is the other half of the information boundary — what the product keeps when the kernel sees only scalars. It is also run custody in the rag-ttc sense (configuration, inputs, observations, status, results under one coordinate), so it travels to [[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 8: Exact Experimental Coordinates and Explicit Coupling|RAG Pattern 8]].

### One-change-per-candidate rule — Law
> Index entry: [[Index of Design Patterns#One-change-per-candidate rule]].

**Chosen because** it is the stated reason the reranker is excluded from sweeps and the reason each candidate mutates exactly one asset — "a sweep that varied fusion and reranking together could not attribute its winner" ([[Research/Software Architecture Garden/coinvault/README#5. Hyper-parameter search under the one-change rule|§5]], §7).

**Belongs because** it is the attribution law applied to the *mutation*, and it is the precondition that makes the treatment-exercise proof meaningful. Without it, "did the mutation cause the delta?" is not even a well-posed question.

### Pattern maturity assessment — Vocabulary
> Index entry: [[Index of Design Patterns#Pattern maturity assessment]].

**Chosen because** §12 is the table that assigns each pattern its label with evidence or limitation, and it is the section the index's maturity brackets quote ([[Research/Software Architecture Garden/coinvault/README#12. Pattern maturity assessment|§12]]).

**Belongs because** it is the bridge between the prose study and the index's bracketed labels. A reader who wants to know *why* a pattern is marked *Candidate ecosystem pattern* rather than *Established* is sent here.

### Preflight environment-identity validation — Pattern (candidate ecosystem)
> Index entry: [[Index of Design Patterns#Preflight environment-identity validation]].

**Chosen because** it runs before any provider call and asserts resolved runtime identity, eight dimension cross-checks, byte digests, the dependency revision, and a seventeen-file source lock, with `--preflight-only` giving a zero-spend dry run ([[Research/Software Architecture Garden/coinvault/README#7.4 The preflight: environment identity before spend|§7.4]], §12).

**Belongs because** it is the most complete realization of instrument freezing and the place where the attribution law becomes a *gate* on spend. The zero-spend dry run is an operational consequence (principle 4) that transfers to any expensive experiment harness.

### Promotion plan — Vocabulary
> Index entry: [[Index of Design Patterns#Promotion plan]].

**Chosen because** the reporter emits a run/candidate/decision binding with state fixed at `review_required` and `human_apply_required: true` ([[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], §11).

**Belongs because** it is the third term in the gate-decision → promotion-plan → application chain and the one that is *deliberately inert* — the plan cannot apply itself. Indexing it separately from the gate decision keeps "the gate passed" and "we have a promotion plan" from collapsing into "we shipped."

### Projection blocks — Vocabulary
> Index entry: [[Index of Design Patterns#Projection blocks]].

**Chosen because** `<gec:sources:v1>` blocks carry evidence IDs matching a strict pattern and an epistemic grade from a closed set, and a cited ID matching nothing the server returned fails the widget build ([[Research/Software Architecture Garden/coinvault/README#9. Runtime grounding: the always-on loop|§9]]).

**Belongs because** they are the runtime surface where the model's claim meets the server's record — the place a grounding failure becomes a visible projection-error event. It is the production-side counterpart of the eval-side answer contract.

### Proposer — Vocabulary
> Index entry: [[Index of Design Patterns#Proposer]].

**Chosen because** `candidate.Proposer.Kind` records who proposed a candidate but changes no behavior — the proposer is recorded-but-inert ([[Research/Software Architecture Garden/coinvault/README#8. The GEPA correspondence, stated precisely|§8]]).

**Belongs because** "recorded but inert" is a precise governance position (principle 1): provenance is captured without granting authority. It is the term that lets the system later add an automated reflection step without silently granting it authorship rights — the open question §15.5 asks.

### Reconciliation instruments — Vocabulary
> Index entry: [[Index of Design Patterns#Reconciliation instruments]].

**Chosen because** the debug recorder (set-difference views across backend/transport/provider/frontend) and the provider-accounting reconciliation turn "we cannot prove spend" into "a closed budget" ([[Research/Software Architecture Garden/coinvault/README#9. Runtime grounding: the always-on loop|§9]]).

**Belongs because** they are the always-on analogues of the trace collector — observability that *validates* rather than merely records. They earn an entry on principle 4: a reader debugging a production mismatch needs the `missing_transport_fanout` view by name.

### Reflection held outside the binary — Law
> Index entry: [[Index of Design Patterns#Reflection held outside the binary]].

**Chosen because** no code feeds failing traces to an LLM to author the next mutation; reflection is a human or assistant working outside the binary, and the candidate-pool diagnostic serves as the structured reflection input ([[Research/Software Architecture Garden/coinvault/README#7. The RAGOPT loop: a GEPA-shaped program with the reflection step held outside|§7]], §8).

**Belongs because** it is the rejected half of GEPA, stated as a deliberate choice ("governed, reviewable, and slow by choice"). It is the entry that most clearly expresses the study's *governance* rather than its *engineering*, and it is the one a future automated-reflection proposal would have to reckon with.

### Reviewed suite lock (open) — Debt/Open
> Index entry: [[Index of Design Patterns#Reviewed suite lock (open)]].

**Chosen because** the reviewed-suite lock validator exists but is called only from tests; nothing on the command path proves the bundle's locked suite equals the *reviewed* suite, so a bundle could lock an unreviewed suite and pass every check ([[Research/Software Architecture Garden/coinvault/README#13. Architecture debt and open laws|§13]]).

**Belongs because** it is the most consequential open law: it is a gap *in the attribution discipline itself* — two overlapping mechanisms, one unwired. An index that lists instrument freezing as a candidate ecosystem pattern but omits the place it is not enforced would be misleading. The debt entry is the honest pair to the pattern entry.

### RRF — Vocabulary
> Index entry: [[Index of Design Patterns#RRF]].

**Chosen because** weighted reciprocal-rank fusion (k = 60, vector weight 1.0, over-fetch = limit × 8) is the fusion step and the knob surface of the sweep, applied after per-channel authorization ([[Research/Software Architecture Garden/coinvault/README#1. The system under evaluation|§1]], §5).

**Belongs because** it is the one piece of the *measured system* (not the measuring apparatus) that earns an entry, and only because it is the mutation surface of the cheapest optimization rung. The index keeps the scope tight: RRF is here as a knob, not as a retrieval algorithm (which is Ragkit's index).

### Runtime citation grounding with server-owned provenance — Pattern (established)
> Index entry: [[Index of Design Patterns#Runtime citation grounding with server-owned provenance]].

**Chosen because** `runEvidenceCache` resolves the model's cited IDs against server-retrieved items — "source cards can only contain server-retrieved documents, never model-authored provenance" — and it shares its evidence contract with the eval stack ([[Research/Software Architecture Garden/coinvault/README#9. Runtime grounding: the always-on loop|§9]], §12).

**Belongs because** it is the always-on loop that closes the circle: the same law enforced in production and in evaluation is "what makes eval results transferable to production behavior at all." That is the study's reason for being, so its index entry is non-negotiable.

### Same-family judge caveat — Vocabulary
> Index entry: [[Index of Design Patterns#Same-family judge caveat]].

**Chosen because** `gpt-5.6-luna` judging `gpt-5.6-luna-low` is a labeled configuration, not a claim of judge independence, and it is "documented rather than hidden" ([[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]]).

**Belongs because** it is the honest disclosure (principle 4) that keeps the judge's numbers from overclaiming. An index that lists computed faithfulness without listing the caveat under which those numbers were produced would let a reader mistake a label for a guarantee.

### Scalar Outcome — Vocabulary
> Index entry: [[Index of Design Patterns#Scalar Outcome]].

**Chosen because** it is what Ragopt sees — metrics plus an artifact digest only — and listing the exact fields (faithfulness, relevance, unsupported-claim rate, citation rates, contract/route booleans, abstention correctness, call counts) makes the information boundary concrete ([[Research/Software Architecture Garden/coinvault/README#7.5 The information boundary and the double verdict|§7.5]]).

**Belongs because** it is the public contract of the kernel and the *projection* of the native artifact. Naming both halves (native artifact = what is kept; scalar outcome = what is shared) is what makes the information boundary readable.

### Semantic identity strings — Vocabulary
> Index entry: [[Index of Design Patterns#Semantic identity strings]].

**Chosen because** `QueryTransformID`, `RetrievalPolicyID`, and `EvidenceLedgerID` travel with every search result and evaluation trace so a quality delta can never silently mix two retrieval configurations, and the `EvidenceLedgerID` is literally `gec-evidence-ledger/v1;scope=run;dedupe=chunk;max_items=12;max_runes=18000` ([[Research/Software Architecture Garden/coinvault/README#1. The system under evaluation|§1]], §11).

**Belongs because** they are the operational form of the attribution law and the local name for a Garden-wide relation ([[Transcripts/Research/09 - RAG-MATHS Pattern Zoo#Pattern 1 — Semantic Identity as Explicit Projection|RAG Pattern 1]]). They are the terms a reader will see in every trace and every receipt, so the index must give them their canonical name and the exact policy string.

### Sentinel file — Vocabulary
> Index entry: [[Index of Design Patterns#Sentinel file]].

**Chosen because** it is the mechanism that closes the held-out split: candidate bundles ship a sentinel in place of the validation data ([[Research/Software Architecture Garden/coinvault/README#14. Candidate ecosystem patterns|§14.4]]).

**Belongs because** it is the *mechanism* half of "prevented by mechanism, not convention." Separating the principle (held-out split, structurally closed) from the mechanism (sentinel file) lets a reader see that the principle is enforced by a concrete artifact, which is the transferable part.

### Source lock — Vocabulary
> Index entry: [[Index of Design Patterns#Source lock]].

**Chosen because** `source-lock.yaml` pins seventeen files — including the judge implementation itself, the service, the tool, the eval set, `go.mod`/`go.sum`, and the prompt-pack templates — every one re-hashed at preflight ([[Research/Software Architecture Garden/coinvault/README#7.4 The preflight: environment identity before spend|§7.4]]).

**Belongs because** it is the most striking instance of instrument freezing: the *harness source* is part of the frozen identity, not just the data and the prompts. A reader who skips it will not believe that `internal/knowledge/judge.go` changing aborts a run at preflight — which it does.

### Sticky close on unprovable spend — Failure mode
> Index entry: [[Index of Design Patterns#Sticky close on unprovable spend]].

**Chosen because** `CloseForUncertainProviderSpend` closes the budget for the remainder of the run when a timed-out cell cannot prove all spend was accounted for ([[Research/Software Architecture Garden/coinvault/README#7.2 The trace collector as validator|§7.2]]).

**Belongs because** it is the conservative move that defines the harness's character (principle 4): under-counted spend is worse than a shortened campaign. It is the operational consequence of treating spend as accounting, not estimation.

### Strata as failure-mode taxonomy — Vocabulary
> Index entry: [[Index of Design Patterns#Strata as failure-mode taxonomy]].

**Chosen because** the eval strata (guide-keyword, facet-product, multi-doc, paraphrase, schema-keyword, scope-negative, unanswerable, jargon-paraphrase, document-concentration, schema-paraphrase) are "a deliberate failure-mode taxonomy, not a topic taxonomy" ([[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]]).

**Belongs because** the failure-mode-vs-topic distinction (principle 1) is what makes the golden set a *measurement instrument* rather than a coverage sample. Indexing it tells a reader *how* to author a new stratum: name a failure mode, not a topic.

### Structural validation of judge output — Pattern
> Index entry: [[Index of Design Patterns#Structural validation of judge output]].

**Chosen because** `JudgeVerdicts` rejects a long, specific list of malformations (count mismatch, relevance out of range, missing abstention flag, out-of-order refs, `supported: true` with no cited evidence, …) and allows exactly one repair round-trip shared across both steps ([[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]]).

**Belongs because** it is the mechanism that makes the judge an *untrusted structured producer* rather than an oracle — the structural side of witness/gate separation. The sharpest clause (`supported: true` with no cited evidence) is worth indexing because it is the exact shape of a faith-flattering judge the system refuses to trust.

### Trace collector as validator — Pattern
> Index entry: [[Index of Design Patterns#Trace collector as validator]].

**Chosen because** `gecRagoptTraceCollector.Observe` is "not a passive recorder" — it errors on duplicate provider-call IDs, unmatched tool results, missing semantic identities, and invalid limit provenance, and it records the full limit-resolution story per knowledge call ([[Research/Software Architecture Garden/coinvault/README#7.2 The trace collector as validator|§7.2]]).

**Belongs because** it is the observational engine of the treatment-exercise proof: the proof needs the limit-resolution story, and the collector is what makes that story *trusted*. It earns an entry separate from the treatment proof because it is a transferable pattern — observability that validates rather than records.

### Train/validation hygiene — Law
> Index entry: [[Index of Design Patterns#Train/validation hygiene]].

**Chosen because** the feedback split is for iteration and the validation split is structurally closed until feedback passes and reproduces, with the rule enforced rather than advised ([[Research/Software Architecture Garden/coinvault/README#8. The GEPA correspondence, stated precisely|§8]]).

**Belongs because** "if feedback fails, do not use validation as another source of tuning data" is the ML-hygiene rule most often violated in practice and the one CoinVault makes a *mechanism*. It is the GEPA-correspondence row where CoinVault claims to be "stronger than typical practice."

### Treatment contract — Vocabulary
> Index entry: [[Index of Design Patterns#Treatment contract]].

**Chosen because** it is a locked asset declaring the mechanism, per-arm expected knob values, the identity strings, per-case applicability, and an *exact sorted set* of required checks — "a check cannot be silently dropped" ([[Research/Software Architecture Garden/coinvault/README#7.1 The treatment-exercise proof|§7.1]], §11).

**Belongs because** it is the declarative half of the treatment-exercise proof: the contract says what *should* happen, the proof checks what *did* happen. Indexing it separately keeps the declaration and the verification distinct, which is the same anti-conflation discipline as candidate-bundle-vs-run.

### Treatment mechanisms — Vocabulary
> Index entry: [[Index of Design Patterns#Treatment mechanisms]].

**Chosen because** the nine mechanisms (default/forced result budgets, comparison decomposition/intent, grounding/routing/policy prompts, reranker, tool description) are the closed set of mutation surfaces the proof knows how to verify ([[Research/Software Architecture Garden/coinvault/README#7.1 The treatment-exercise proof|§7.1]]).

**Belongs because** a closed, enumerated set is what makes the proof *mechanical* rather than ad hoc. A reader proposing a new mutation must add a mechanism and its exact check set, and this entry is where they learn the contract.

### Treatment-exercise proof — Pattern (candidate ecosystem)
> Index entry: [[Index of Design Patterns#Treatment-exercise proof]].

**Chosen because** it is the study's "strongest original contribution": a measured delta counts only when the harness proves from the observed event stream that the mutation was causally live in the challenger and absent in the incumbent, otherwise the cell fails as `treatment_not_exercised` and the judge is never invoked ([[Research/Software Architecture Garden/coinvault/README#7.1 The treatment-exercise proof|§7.1]], §12, §14.1).

**Belongs because** it is born from a concrete, recorded failure (six `default_results 5→8` experiments that measured nothing because "configuration is not behavior") and it is the general law the study states for any optimization loop. It is the single entry a reader should take away if they take away only one. It is marked *candidate* because no second implementation exists yet — the index refuses to promote it to *established* without independent confirmation, exactly as the Garden requires.

### Two-step decomposed judge — see Judge, two-step decomposed
> Index entry: [[Index of Design Patterns#Judge, two-step decomposed]].

A redirect to the canonical entry. It belongs because "two-step decomposed judge" is the descriptive phrase a reader will search for, while the index files it under *Judge* with the other judge-adjacent terms.

### Unknown-ID warnings — Failure mode
> Index entry: [[Index of Design Patterns#Unknown-ID warnings]].

**Chosen because** expected document IDs that do not exist in the corpus surface as warnings, never silent misses, "so golden-set rot is visible rather than absorbed into the metrics" ([[Research/Software Architecture Garden/coinvault/README#3. Deterministic retrieval evaluation|§3]]).

**Belongs because** it pairs with failure-as-miss to show a harness biased against silent rot (principle 4). It is the small, transferable discipline any golden-set maintainer should adopt, so it earns an entry rather than a clause.

### Version-keyed durable cache — Pattern
> Index entry: [[Index of Design Patterns#Version-keyed durable cache]].

**Chosen because** `CachedGeneratorWithObserver` keys the content-addressed cache on `(step, judgePromptVersion, model, prompt)`, so bumping `judgePromptVersion` invalidates the entire judged population at once — "an instrument change and a data change cannot be confused" ([[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]]).

**Belongs because** it is the cache-side realization of instrument freezing: invalidation by construction rather than by memo. It is the mechanism that lets the judge be cached durably without the cache lying about what was measured.

### Witness/gate separation — Pattern (candidate ecosystem)
> Index entry: [[Index of Design Patterns#Witness/gate separation]].

**Chosen because** it is the third of the three governance rules and one of the five candidate ecosystem patterns: judges produce metrics under structural validation; admission is a deterministic constraint-first policy; application is human. Three authorities, never merged ([[Research/Software Architecture Garden/coinvault/README#6. The LLM judge: a witness under discipline|§6]], §14.3).

**Belongs because** it is the discipline that keeps the LLM judge from becoming an automated decision-maker, and it is the abstract law under which computed faithfulness, the gate decision, and human promotion authority all sit. It is the entry that names the *stance* the whole judging apparatus takes.

## Reader-situation test

A back-of-book index is only as good as the retrieval paths it offers a reader with imperfect memory. The test below invents realistic reader situations and traces each to the index entry that serves it. Every arrow is an actual anchor in the index; this is the index's usability test, and it doubles as a map of the access paths the `See` redirects exist to provide.

1. *"There was a mechanism that proves the A/B mutation actually did something, not just that the config changed."* → [[Index of Design Patterns#A/B experiment, proving the mutation fired]] → [[Index of Design Patterns#Treatment-exercise proof]] → §7.1.
2. *"What was the phrase they coined when the default-results experiments measured nothing?"* → [[Index of Design Patterns#Configuration is not behavior]] → [[Index of Design Patterns#Treatment-exercise proof]] → §7.1.
3. *"Where did a judge that couldn't see SQL evidence give wrong faithfulness, and how was it fixed?"* → [[Index of Design Patterns#Judge, two-step decomposed]] → its subentry [[Index of Design Patterns#Evidence admitted includes non-knowledge tool results]] → §6.
4. *"What was the rule about not using the validation split as another source of tuning data?"* → [[Index of Design Patterns#Train/validation hygiene]] → §8.
5. *"How is the held-out set kept from leaking — convention or mechanism?"* → [[Index of Design Patterns#Held-out leakage (prevented)]] → [[Index of Design Patterns#Held-out split, structurally closed]] / [[Index of Design Patterns#Sentinel file]] → §12, §14.4.
6. *"What does the EvidenceLedger identity string actually look like?"* → [[Index of Design Patterns#Identity strings, schemas, and budgets]] (notation table) → §1.
7. *"What's the difference between a gate decision, a promotion plan, and shipping?"* → [[Index of Design Patterns#Gate decision]] → [[Index of Design Patterns#Promotion plan]] → [[Index of Design Patterns#No apply command exists]] → §7, §11.
8. *"Where do they record that no candidate ever got promoted, and treat it as information not embarrassment?"* → [[Index of Design Patterns#Component evidence ledger]] → §7.5.
9. *"What are the nine mutation mechanisms?"* → [[Index of Design Patterns#Treatment mechanisms]] (and the notation table) → §7.1.
10. *"How do they keep the judge from being asked to score itself flatteringly?"* → [[Index of Design Patterns#Computed faithfulness]] → §6.
11. *"What's the cheapest eval and what does it measure?"* → [[Index of Design Patterns#Deterministic retrieval eval]] / [[Index of Design Patterns#Instrument ladder]] → §3, §2.
12. *"Which diagnostic tells me WHICH stage lost the evidence?"* → [[Index of Design Patterns#Diagnosing a retrieval failure]] → [[Index of Design Patterns#Candidate-pool diagnostic]] → §4.
13. *"What does `gec-ragopt-native/v5` contain?"* → [[Index of Design Patterns#Identity strings, schemas, and budgets]] → [[Index of Design Patterns#Native artifact]] → §7.5.
14. *"How is the judge cached so a prompt change invalidates everything?"* → [[Index of Design Patterns#Version-keyed durable cache]] → §6.
15. *"What's the epistemic-grade vocabulary a source card must choose from?"* → [[Index of Design Patterns#Epistemic grade]] (and the notation table) → §9.
16. *"Where did they say the judge is a witness, not a gate?"* → [[Index of Design Patterns#Judge as witness, not a gate]] → [[Index of Design Patterns#Witness/gate separation]] → §6, §14.3.
17. *"What's the rule that each candidate changes only one thing, and why?"* → [[Index of Design Patterns#One-change-per-candidate rule]] → §5, §7.
18. *"What happens to a cell that can't prove its treatment fired?"* → [[Index of Design Patterns#Treatment-exercise proof]] → its subentry [[Index of Design Patterns#Cell failure class]] → §7.1.
19. *"What's the open bug where the reviewed-suite lock isn't enforced on the command path?"* → [[Index of Design Patterns#Reviewed suite lock (open)]] → §13.
20. *"Where's the rule that under-counted spend is worse than a shortened campaign?"* → [[Index of Design Patterns#Under-counted spend]] → [[Index of Design Patterns#Sticky close on unprovable spend]] / [[Index of Design Patterns#Budget accounting, hard]] → §7.2.

All twenty land on a section that substantively treats the concept (the disappointed-reader test passes). The situations that needed a `See` redirect — 1, 2, 5, 12, 16, 20 — are exactly the ones where a reader remembers the *idea* but not the study's own spelling, which is the case the redirects were added to serve.

## How the index and this rationale should grow

When the planned deep-dives for this folder are written (the judge protocol, the treatment/trace/contract triad, budget and termination custody, and the runtime grounding boundary, as listed at [[Research/Software Architecture Garden/coinvault/README#15. Open questions and next investigations|§15]]), each will introduce refinements of the terms above. The index should add new entries only when a deep dive names a *new* distinction, law, or candidate pattern — not when it re-elaborates an existing one, in which case the existing entry gains a new §-link. This keeps the index a true back-of-the-book reference rather than a growing table of contents.

Two maintenance rules follow from the index's structure. First, because every entry is a heading, a new entry is automatically an anchorable target — add the term, then link to it from any `see also` that the new distinction relates to, and add a `See` redirect for any alternate phrasing a reader might plausibly use. Second, new versioned handles, schemas, budgets, and closed vocabularies go in the [[Index of Design Patterns#Identity strings, schemas, and budgets|notation table]], not the alphabetic list, so the "what did X mean again?" lookup stays in one place. The same rule applies when the other Garden projects receive their own indexes: shared terms (semantic identity, exact coordinates, constraint-before-preference, run custody) should be filed under the *same canonical name* in each project's index, with cross-links, so that the set of indexes becomes a cross-referenceable Garden-wide glossary rather than seventeen independent alphabets.

## Related documents

- [[Research/Software Architecture Garden/coinvault/Index of Design Patterns|Index of Design Patterns]] — the index this rationale justifies.
- [[Research/Software Architecture Garden/coinvault/README|CoinVault study]] — the evidence-pinned source.
- [[Research/Software Architecture Garden/README|Software Architecture Garden]] — maturity vocabulary and evidence hierarchy.
