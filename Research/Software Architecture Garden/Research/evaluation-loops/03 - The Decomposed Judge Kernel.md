---
title: The Decomposed Judge Kernel — Structural Admission of Model Verdicts
aliases:
  - Judge kernel research project
  - Structural vs empirical judge invariants
  - judgekernel package design
status: proposed
type: architecture-garden-research
created: 2026-08-14
analyzed: 2026-08-14
repositories:
  - /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault
  - /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/rag-ttc
applies_to:
  - "[[Research/Software Architecture Garden/coinvault/README|CoinVault]]"
  - "[[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc optimization loops]]"
  - "[[Research/Software Architecture Garden/ragopt/README|Ragopt]]"
tags:
  - architecture-garden
  - research
  - llm-as-judge
  - evaluation
  - go
  - lean4
  - fuzzing
  - mutation-testing
  - structural-validation
related_files:
  - Research/Software Architecture Garden/Research/evaluation-loops/specs/judgekernel/admit.go
  - Research/Software Architecture Garden/Research/evaluation-loops/specs/judgekernel/estimate.go
  - Research/Software Architecture Garden/Research/evaluation-loops/specs/judgekernel/repair.go
  - Research/Software Architecture Garden/Research/evaluation-loops/specs/judgekernel/lean/JudgeKernel.lean
  - Research/Software Architecture Garden/Research/evaluation-loops/specs/judgekernel/results/build.txt
related_notes:
  - "[[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]]"
  - "[[Research/Software Architecture Garden/coinvault/README|CoinVault]]"
  - "[[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]]"
  - "[[Research/Software Architecture Garden/ragopt/README|Ragopt]]"
---

# The Decomposed Judge Kernel — Structural Admission of Model Verdicts

Two repositories in this ecosystem judge LLM answers with the same two-step protocol: a statements step that extracts factual claims without seeing the evidence, and a verdicts step that judges the extracted claims against labeled evidence without re-reading the answer, with faithfulness computed in Go as supported-over-total rather than asked of any model. The ancestor lives in rag-ttc (`cmd/rag-ttc/cmds/experiments/answerquality/judge.go`); the port lives in CoinVault (`internal/knowledge/judge.go`). Both carry the same one-line law in a source comment: *the judge is a witness, not a gate*.

This research project asks the question that separates a bespoke pipeline from a reusable library: **which of the judge's invariants are structural — provable about the validator and the estimators, independent of any model — and which are empirical properties of models that no library can promise?** The structural half is then designed as a kernel package, `judgekernel`, and its invariants are checked three ways: property and fuzz tests in Go, a six-mutation kill test over the admission rules, and kernel-checked Lean 4 theorems over a faithful miniature of the checker. All artifacts were executed; results are recorded in [[Research/Software Architecture Garden/Research/evaluation-loops/specs/judgekernel/results/build.txt|specs/judgekernel/results/build.txt]].

> [!summary]
> - The judge decomposes into a large untrusted producer (the judge model) and a small trusted admission boundary; everything the admission boundary decides is structural and provable, and everything the model asserts is empirical and must stay labeled as such.
> - Eleven admission rules define the relation between a raw verdict payload, a statement list, and an evidence-label universe. The `judgekernel` Go package implements them as a pure `Admit` function whose result type, `Admitted`, can be constructed no other way — possession of the value is proof of validation.
> - Faithfulness is an explicit `Fraction` with numerator and denominator; the 0/0 vacuous-abstention case has no float value by construction, so the "vacuously 1.0" convention both source implementations use becomes an aggregation-time policy instead of a stored measurement.
> - The kernel exports no accept/reject decision about the judged answer. Witness-not-gate is an API property: there is nothing in the package for a gate to call.
> - Comparing the two source implementations yields real findings: rag-ttc never validates evidence citations at all (`verdict.Evidence []int` is accepted unchecked, including supported-with-no-evidence); CoinVault's per-step cache constants are dead code; the two repositories resolve malformed payloads with opposite disciplines (salvage-and-label versus reject-and-repair); and both converged independently on excluding abstention from faithfulness means.
> - Checked evidence: `go vet` + full test suite pass; 1,033,072 + 784,831 fuzz executions with zero counterexamples against an independent rule re-implementation; six seeded rule deletions all caught; six Lean theorems (count soundness, ordered numbering, citation membership, supported-requires-evidence, faithfulness bound, vacuity) check under core Lean 4.33.0 with no `sorry`, and a seeded weakening of the Lean checker breaks the proofs.

## 1. Research question

A judge pipeline makes two different kinds of promise. "Every admitted verdict cites only evidence labels that exist" is a promise about code: it can be enforced by a validator and proved about that validator. "A supported verdict means the evidence actually entails the statement" is a promise about a model: no validator can enforce it, and any API that implies it is lying. The two source implementations mix both kinds in single files, which makes it hard to see what a reusable library could truthfully export.

The project's objective is the separation itself:

```text
structural half  →  a kernel library with proved/tested invariants
empirical half   →  named, labeled residue that stays a model property
```

with the acceptance bar of the [[Research/Software Architecture Garden/Research/evaluation-loops/README|evaluation-loops research family]]: run what you build, state guarantee taxonomies, and demonstrate mutation sensitivity.

## 2. Baseline evidence

Both implementations were read in full at the pinned workspace checkouts (CoinVault commit `10d1a8d8`, rag-ttc commit `0b0e420`), and every symbol cited below was verified in source.

### 2.1 CoinVault: reject-and-repair

`internal/knowledge/judge.go` runs both steps through one `Generator func(ctx, prompt) (string, error)`. Step 1, `ExtractStatements` (`judge.go:402-421`), formats the question and answer into `judgeStatementsPrompt` (`judge.go:37-50`) — the prompt has no evidence slot. Step 2, `JudgeVerdicts` (`judge.go:425-498`), numbers the statements, sorts the knowledge labels, appends `SQL1..SQLn` labels for tool results, and validates the parsed payload against nine rules (`judge.go:453-496`): verdict count equals statement count; `addresses_question` present, finite, in [0,1]; `abstained` present; verdict *i* references statement *i+1*; `supported` present; `reason` non-blank; every cited label in the admitted set; no duplicate citations per verdict; supported verdicts cite at least one label. Every optional wire field is a pointer so absent and zero stay distinct (`judge.go:349-362`).

A violation produces `invalidJudgeResponseError` (`judge.go:364-382`), and exactly one repair is shared across both steps: `extractStatementsWithRetry` and `judgeVerdictsWithRetry` thread one `retryUsed *bool` (`judge.go:500-516`), and the repair generator re-issues the prompt with the validation error appended (`judge.go:384-388`). `JudgeAnswer` (`judge.go:519-565`) computes faithfulness as `supported/statements` (`judge.go:561`); zero extracted statements set `Abstained` and `Faithfulness = 1.0` "vacuously" but still run the verdict step for relevance and the judge's own abstention flag (`judge.go:533-544`).

The runtime layer adds denominator discipline — `emitJudgeSummaries` reports `metric_denominator`, `faithfulness_denominator`, `relevance_denominator` separately and excludes abstained scores from the faithfulness mean (`cmd/coinvault/cmds/knowledge.go:2027-2071`) — plus call ceilings with pre-reservation and rollback (`knowledge.go:2163-2170`), resume seeding (`:2150-2161`), and a three-attempt transport retry recorded as the response to a real killed baseline run (`:2219-2236`).

### 2.2 rag-ttc: salvage-and-label

The ancestor (`cmd/rag-ttc/cmds/experiments/answerquality/judge.go`) makes different choices at almost every boundary. Its two steps run on **separately configurable profiles** (`tooleval/judge.go:33-34,65-66`), through a cached-generation flow with a worker pool and a fail-closed budget precomputed as two calls per judgeable cell (`judge.go:425-431`). Its prompts are exported constants declared to be experiment identity — "a changed prompt is a new judge arm, never an update" (`judge.go:39-44`) — and its relevance scale is anchored to {0, 0.5, 1} (`judge.go:49-58`).

Where CoinVault rejects, rag-ttc salvages and labels. `scoreJudgedCell` (`judge.go:315-370`) drops out-of-range statement numbers, keeps the first of duplicate verdicts, computes faithfulness over the judged subset when coverage is partial, and records the cell as `partial`; an unparseable response becomes status `unjudged`, "recorded, never guessed, never retried" beyond transport retries (`judge.go:69-71`). Out-of-range relevance is discarded with a note while the cell stays judged (`judge.go:359-363`). Abstention is decided upstream by the deterministic answer contract — abstained cells never reach the judge and relevance is not judged for them (`judge.go:406-412`) — and contract-invalid answers are never judged at all (`judge.go:400-405`). Statement parsing deduplicates order-preserving (`judge.go:276-287`). The same-family hazard is a **persisted structural label**: `JudgeRunConfig.SameFamilyVerdicts` is computed by `sameModelFamily` and recorded in the run config (`judge.go:119-127,186-207`). Aggregation excludes abstained faithfulness with the recorded reason that "arms cannot buy faithfulness by abstaining" (`judge.go:627-630`) and never imputes missing metrics (`judge.go:105-117`).

### 2.3 Divergence findings

| Boundary | rag-ttc (ancestor) | CoinVault (port) | Assessment |
|---|---|---|---|
| Malformed payload | Salvage and label: drop out-of-range, keep-first duplicates, `partial`/`unjudged` statuses, faithfulness over judged subset | Reject whole payload, one repair round-trip with the error appended, then fail the cell | Opposite disciplines protecting different things: rag-ttc protects the campaign denominator record, CoinVault protects per-cell score integrity. Neither documents the trade against the other. |
| Evidence citations | **Not validated at all**: `verdict.Evidence []int` is unmarshaled and stored unchecked (`judge.go:289-309`); supported verdicts with zero citations are accepted; indices beyond the evidence count are accepted | Membership, per-verdict duplicates, and supported-requires-evidence all enforced (`judge.go:466-495`) | Real gap in the ancestor. A rag-ttc audit that "grades the judge" from `JudgeVerdictRecord.Evidence` can be reading citations that point at nothing. |
| Relevance out of range | Discarded with note, cell stays judged | Whole payload rejected → repair | CoinVault's choice couples an unrelated field's failure to the verdicts; rag-ttc's silently narrows the relevance denominator. Both are defensible; neither is stated as a decision. |
| Abstention | Upstream deterministic contract decides; judge never sees abstained cells; relevance not judged | Zero extracted statements infer abstention; verdict step still runs for relevance and the judge's abstained flag | CoinVault measures abstention quality (relevance of a refusal); rag-ttc keeps the judge population smaller and cleaner. Different estimands, same word. |
| Statement dedup | Order-preserving dedup at parse | Trim and drop empties only | A duplicated statement in CoinVault double-counts in the faithfulness denominator. |
| Same-family judging | Persisted `SameFamilyVerdicts` flag computed from model names | Source comment on the builder (`knowledge.go:2085-2088`) | The structural label is strictly better: it travels with every judged number. |
| Cache identity | Versioned kinds `ttc-judge-statements-v1`/`ttc-judge-verdicts-v1` plus adapter version and context policy; byte-deterministic requests with all content in `Text` | One step string `"gec-judge"` + `judgePromptVersion` + model + full prompt; the declared per-step constants `judgeStatementsStep`/`judgeVerdictsStep` (`judge.go:29-30`) are **dead code** | Both are safe against stale replay because the full prompt is in the key; CoinVault's collapse loses per-step cache accounting and left dead constants recording the abandoned design. |
| Concurrency and budget | Worker pool, fail-closed up-front budget (≥ 2× judgeable), 6-attempt transport retry | Sequential, per-call pre-reservation with rollback, 3-attempt transport retry + 1 semantic repair | Convergent goal (bounded spend), divergent mechanism; the kernel takes neither and leaves budgeting to project 04's vocabulary. |
| Faithfulness-mean exclusion of abstention | Yes (`judge.go:627-633`) | Yes (`knowledge.go:2032-2037`) | The strongest convergent invariant. Extraction lineage, not independent confirmation — but the *reason* is independently articulated in both. |

## 3. Formal definitions

### 3.1 The admission relation

Let $S$ be a finite statement list of length $n$, and $U$ a finite set of evidence labels (the *universe*). Let $P$ be the set of raw text payloads. Define the partial parse $\pi : P \rightharpoonup V^* \times \mathbb{R} \times \mathbb{B}$ extracting a verdict sequence, a relevance value, and an abstention flag from the first-to-last-brace JSON slice. The admission relation is

$$
\mathrm{Admit}(S, U, p) \downarrow \iff \pi(p)\ \text{is defined} \wedge |V| = n \wedge \mathrm{rel} \in [0,1] \wedge \bigwedge_{i=1}^{n} \mathrm{ok}(v_i, i)
$$

where $\mathrm{ok}(v, i)$ requires: $v$ references statement $i$; its supported flag and reason are present and non-blank; its citation multiset is a *set* (no duplicates) contained in $U$; and $\mathrm{supported}(v) \Rightarrow \mathrm{cites}(v) \neq \emptyset$. Admission is a pure function of $(S, U, p)$ — determinism is not an implementation nicety but part of the definition, because the durable cache replays raw payloads and a nondeterministic validator would make cached populations unstable.

### 3.2 Estimators with explicit denominators

For an admitted verdict sequence $V$, faithfulness is the fraction

$$
F(V) = \frac{|\{v \in V : \mathrm{supported}(v)\}|}{|V|}, \qquad 0 \le F(V) \le 1 \text{ when } |V| > 0.
$$

$|V| = 0$ is the vacuous case: $F$ is *undefined*, not 1. Both source implementations store 1.0 by convention and then exclude it from means; the kernel refuses the laundering step — a `Fraction{0,0}` has no float value, and the convention becomes visible aggregation policy. Aggregate means carry their denominators:

$$
\bar{F} = \frac{\sum_{c \in C'} F(c)}{|C'|}, \qquad C' = \{c \in C : \neg\mathrm{abstained}(c) \wedge |V_c| > 0\},
$$

and an empty $C'$ yields "undefined with denominator zero", never zero. This is the shared law both repositories converged on: an arm cannot buy faithfulness by abstaining, and a missing population cannot look like a zero-scoring one.

### 3.3 Information hiding as a signature property

The decomposition's bias argument is an information-flow claim: extraction unbiased by supportability requires that the extraction input contain no evidence; verdicts unable to judge unextracted claims requires that the verdict input contain no answer. In both source implementations this is enforced by prompt-construction care. The kernel lifts it to types: `StatementsRequest{Question, Answer}` has no evidence field and `VerdictsRequest{Question, Statements, Evidence}` has no answer field, so the discipline holds for every caller that builds prompts through the kernel. A caller can still leak by hand-building prompts — the guarantee is "the kernel provides no leaking path", not "leaking is impossible".

### 3.4 Bounded repair

Repair is a function on generators: $\mathrm{repair}(g, e)$ is $g$ with the validation error $e$ appended to the prompt. The combinator law: for one cell, across both steps, repair fires at most once, and only when the failure is an admission failure. Provider errors and admitted-but-unwelcome results (low scores, all-unsupported verdicts) never trigger it — retrying a *valid* verdict because it scored poorly would be the witness quietly becoming an advocate. Because the repaired prompt differs from the original, its cache key differs, so a cached invalid response can never be replayed as its own repair (this is tested against a real file cache in CoinVault's `TestJudgeAnswerRepairRetryBypassesIdenticalPromptCacheKey`).

### 3.5 Population identity

A judged population is $(step, promptVersion, model)$; the cache key of one generation is the hash of that triple plus the full prompt. Two consequences, one per component: bumping `promptVersion` orphans every cached judgment at once (the frozen-instrument discipline), and including the full prompt makes silent prompt drift *safe* (old entries can never be replayed for the new prompt) while leaving it *mislabeled* (the population label no longer identifies one instrument). The label lies only if the version is not bumped; the replay never lies. Both source implementations share exactly this property; the kernel makes it a named type so the distinction is documentable.

## 4. The structural/empirical guarantee taxonomy

This table is the heart of the project. Each row is one invariant of the judge protocol; the columns separate what a library can promise from what only a model evaluation can show.

| Invariant | Provable about the validator/estimator | Empirical about models | Evidence at this snapshot |
|---|---|---|---|
| One verdict per statement, in order, no gaps or duplicates | Yes — admission rule; Lean `check_length` + `checkFrom_numbering`; Go rule 3/6 + fuzz | — | Lean checked; mutation M3 caught; 1.03M fuzz execs |
| Citations name only admitted evidence | Yes — universe membership; Lean `checkFrom_sound`; Go rule 9 | — | Lean checked; mutation M2 caught; rag-ttc lacks this rule entirely (finding) |
| No duplicate citations per verdict | Yes — Go rule 10 | — | Go test + fuzz; deliberately absent from the Lean miniature (see §7 limits) |
| Supported requires cited evidence | Yes — Lean `checkFrom_sound`; Go rule 11 | — | Lean checked; mutation M1 caught; Lean weakening probe breaks `check_sound` |
| Reasons present, relevance finite in [0,1], abstained present | Yes — Go rules 4/5/7/8 | — | Go table test covers every reason code |
| Faithfulness = supported/total, bounded [0,1] | Yes — computed, never asked; Lean `supportedCount_le_length`; `Fraction` type | — | Lean checked; mutation M6 (faithfulness-as-constant) caught |
| Vacuous abstention is 0/0, not 1.0 | Yes — `Fraction{0,0}.Value()` undefined | — | Go test; laundering becomes impossible rather than discouraged |
| Abstained cells excluded from faithfulness means; denominators explicit; empty populations undefined | Yes — `Summarize` | — | Go test; mutation M4 caught; convergent with both source implementations |
| At most one repair, only on structural invalidity, shared across steps | Yes — `RepairBudget` + `RunWithRepair` | Repair *convergence* (does the second attempt actually fix it) is empirical | Go tests; mutation M5 caught |
| Cache determinism and population separation | Yes up to hash collision — canonical key encoding | — | Go collision/determinism test |
| Extraction never sees evidence; verdicts never see the answer | Yes as an API property of the request types | Leak-freedom of callers who bypass the kernel is not covered | Go test asserts the rendered bodies |
| Statements are atomic, complete, non-hallucinated restatements of the answer | — | Entirely a property of the extraction model and prompt | rag-ttc's human calibration workbook design; no automated check exists in either repo |
| A supported verdict tracks true entailment | — | Entirely a judge-model property; the rubric line ("plausibility is not support") is prompt text, not enforcement | Recorded caveat in both repos; no human-agreement computation exists (rag-ttc gap) |
| Relevance is calibrated | — | Judge-model property; rag-ttc anchors the scale, CoinVault leaves it continuous | Divergence recorded in §2.3 |
| Same-family self-preference | — | Structural *labeling* is possible (rag-ttc persists the flag); the bias itself is empirical | `SameFamilyVerdicts` is the better practice; kernel adoption plan carries it |

The empirical rows are the honest residue: a library can *carry* them as labels and caveats, but any API that turns them into return values is overclaiming. This is why `judgekernel` has no `Entailed(statement, evidence) bool` and never will.

## 5. The kernel API

The package (≈480 lines of implementation, ≈520 of tests) lives at [[Research/Software Architecture Garden/Research/evaluation-loops/specs/judgekernel/admit.go|specs/judgekernel/]]:

```go
// labels
type EvidenceLabel string
func NewLabelUniverse(labels ...EvidenceLabel) (LabelUniverse, error)
func KnowledgeLabels(n int) []EvidenceLabel      // E1..En
func SQLLabels(n int) []EvidenceLabel            // SQL1..SQLn

// admission — the only constructor of Admitted
func AdmitStatements(raw string) ([]string, error)                    // trim, drop empty, dedup
func Admit(statements []string, universe LabelUniverse, raw string) (Admitted, error)
type AdmissionError struct{ Reason AdmissionReason; Detail string }   // 13-reason closed taxonomy

// estimators — arithmetic over admitted values only
func ScoreCell(admitted Admitted) Score          // Fraction faithfulness; vacuous status
func Summarize(scores []Score) Summary           // MeanReport with denominators; abstention excluded

// bounded repair
type RepairBudget struct{ ... }                  // one per cell, shared across steps
func RunWithRepair[T any](ctx, *RepairBudget, Generator,
    func(ctx, Generator) (T, error)) (T, error)

// population identity
type PopulationKey struct{ Step, PromptVersion, Model string }
func (k PopulationKey) CacheKey(prompt string) string

// information hiding as types
type StatementsRequest struct{ Question, Answer string }              // no evidence field
type VerdictsRequest struct{ Question string; Statements []string;
    Evidence []LabeledEvidence }                                      // no answer field
```

Three design points carry the argument:

**Possession is proof.** `Admitted` has only unexported fields and only `Admit` constructs it, so every downstream consumer — estimator, journal writer, report renderer — takes validation as a type-level precondition instead of re-checking or trusting. This is the RAG-10 "large producer, small trusted validator" shape reduced to a Go visibility rule. The verdicts also bind their statement *text* at admission, eliminating the parallel-slice indexing both source implementations do at scoring time.

**The witness cannot gate.** The package exports fractions, means, statuses, and denominators. It exports no threshold, no pass/fail, no comparison of arms. A gate (project [[Research/Software Architecture Garden/Research/evaluation-loops/README|05]]) consumes `Summary` values under a product-authored policy; the kernel cannot express the question "is this good enough", which is exactly the separation both source comments assert and neither source API enforces.

**Vacuity is unrepresentable, not discouraged.** Both repositories store faithfulness 1.0 for abstentions and then remember to exclude it from means — two mechanisms where one law suffices, and a trap for any new consumer that averages scores without reading the exclusion comment. `Fraction{0,0}` has no value; the trap is gone. This is the one place the kernel deliberately diverges from both sources, and it is recorded as DR-2 below.

## 6. Checked artifacts and their guarantee taxonomy

Everything below was executed on 2026-08-14; the full transcript is in `results/build.txt`.

| Artifact | Command | Result | Establishes | Does not establish |
|---|---|---|---|---|
| Go module (8 files) | `GOWORK=off go vet ./... && go test ./... -count=1` | pass | Every admission rule has an accepting and a rejecting fixture; estimator and repair laws hold on the tested inputs | Behavior on inputs outside the suite |
| Fuzz: `FuzzAdmit` | `-fuzztime 15s` | 1,033,072 execs, 0 counterexamples | Determinism and rule-satisfaction of admitted values, checked against an independent re-implementation (`revalidate`) sharing no code with `Admit` | Absence of violations on unexplored inputs; the fuzzer's 15s corpus is finite |
| Fuzz: `FuzzAdmitStatements` | `-fuzztime 10s` | 784,831 execs, 0 counterexamples | Trim/nonempty/dedup invariants of statement admission | Same finite-corpus limit |
| Mutation script `mutate.sh` | 6 seeded rule deletions | 6/6 caught | The test suite actually protects: supported-without-evidence, unknown-evidence, count-match, abstention-mean-exclusion, repair bound, computed faithfulness | Sensitivity to mutations not in the set |
| Lean `JudgeKernel.lean` | `lean JudgeKernel.lean` | compiles, no `sorry` | Six theorems about the miniature checker: count soundness, ordered 1..n numbering, citation membership, supported-requires-evidence, `supportedCount ≤ length`, vacuity | Anything about the Go code (see limits below) |
| Lean weakening probe | sed the supported-evidence conjunct to `true` | proofs fail to compile | The theorems track the checker; they are not vacuously true | — |

**Limits of the Lean miniature, stated precisely.** The miniature abstracts labels to `Nat` indices below a bound, reasons to a nonemptiness flag, and omits two rules: per-verdict duplicate citations (a `List Nat` models a citation list but the dedup proof was not attempted) and the float-valued relevance range (core Lean has no float order theory worth the modeling cost). The Lean theorems are therefore statements about a *model* of the admission walk, connected to the Go implementation by structural correspondence a reviewer can check function-by-function (`verdictOK` ↔ the per-verdict body of `Admit`, `checkFrom` ↔ the indexed loop, `check` ↔ count guard plus loop) — not by extraction or refinement proof. Closing that gap mechanically is an open question below.

## 7. Adoption plan

**Target.** A shared module — the natural home is alongside [[Research/Software Architecture Garden/ragopt/README|Ragopt]] (which already owns the generic experiment side and whose `Outcome` metrics these scores feed), either as `ragopt/pkg/judgekernel` or a sibling module. Ragopt itself is judge-agnostic today and should stay so; the kernel is a library its product adapters use, not a new Ragopt phase.

**CoinVault adapter.** `JudgeVerdicts`'s validation body is replaced by `Admit` against a universe built from the ledger and SQL labels; `JudgeAnswer`'s scoring becomes `ScoreCell`; `emitJudgeSummaries` consumes `Summarize`. Behavior differences to decide deliberately, each requiring a `judgePromptVersion` bump if adopted: statement dedup (new), vacuous faithfulness no longer stored as 1.0 (schema change in native artifacts), and the dead per-step constants either deleted or revived as real per-step `PopulationKey.Step` values.

**rag-ttc adapter.** Adoption is a *behavior change*, not a refactor: the ancestor currently admits citation-free supported verdicts and unvalidated evidence indices. Under its own rule — "a changed prompt is a new judge arm" — a changed validator is a new judge arm too, so adoption means new kind versions and an explicit note that historical `partial`-salvage populations and strict-admission populations are not comparable. The salvage discipline itself can be preserved as a layer above the kernel: run `Admit`; on rejection, record status `unjudged` with the typed `AdmissionReason` instead of repairing. The kernel does not force the CoinVault discipline; it forces that whatever is *scored* was admitted.

**What is deliberately left out.** Budgets and spend accounting (project 04's vocabulary), caching infrastructure (both repos have one; the kernel only defines the key), prompt text (product-owned experiment identity), and the answer-acquisition client (product transport).

## 8. Decision records

### DR-1: strict admission with bounded repair, salvage as an optional layer above

- **Context:** rag-ttc salvages malformed payloads with a status vocabulary; CoinVault rejects and repairs once.
- **Decision:** the kernel admits all-or-nothing; `RunWithRepair` bounds semantic retries to one; salvage policies live above the kernel and may not feed unadmitted verdicts to estimators.
- **Rationale:** partial salvage inside the validator makes "admitted" a matter of degree, and every downstream proof would weaken to match. Keeping admission binary keeps `Admitted` a proof token; keeping the status vocabulary above preserves rag-ttc's denominator record.
- **Consequence:** a rag-ttc-style consumer records more `unjudged` cells than its current salvage produces `partial` cells. That is a measurement-policy change and must be versioned.
- **Status:** proposed.

### DR-2: vacuous faithfulness is unrepresentable

- **Context:** both sources store 1.0 for zero-statement cells and separately exclude it from means.
- **Decision:** `Fraction{0,0}` has no float value; exclusion is structural.
- **Consequence:** native-artifact schemas that persist the 1.0 convention need a version bump on adoption; in exchange, no future consumer can average the convention into a population.
- **Status:** proposed.

### DR-3: information hiding as request types

- **Decision:** the kernel's request builders are the only prompt-body constructors it offers, and their fields encode the hiding discipline.
- **Consequence:** the guarantee is "no leaking path through the kernel"; callers who format prompts by hand are outside it, and the document says so rather than implying more.
- **Status:** proposed.

### DR-4: one repair budget per cell, shared across steps

- **Context:** CoinVault threads a single `retryUsed` across extraction and verdicts; rag-ttc has no semantic retry at all.
- **Decision:** adopt the shared single budget as the kernel default; zero-repair (rag-ttc style) is expressible by passing an exhausted budget.
- **Rationale:** the bound is a spend guarantee (a cell costs at most one extra call) and a bias bound (at most one response per cell was produced under a feedback-modified prompt).
- **Status:** proposed.

### DR-5: per-step population keys

- **Context:** CoinVault collapsed both steps into one cache step string, leaving its per-step constants dead; rag-ttc keeps per-step versioned kinds.
- **Decision:** `PopulationKey.Step` is per-step; the full prompt stays in the key.
- **Rationale:** replay safety comes from the prompt; per-step labels restore per-step cache accounting and let one step's prompt be revised (with its own version bump) without relabeling the other.
- **Status:** proposed.

## 9. Risks

- **Same-family judging.** `gpt-5.6-luna` judging `gpt-5.6-luna-low` answers is structurally suspect of self-preference. The kernel cannot detect this; it can only carry rag-ttc's persisted-flag practice into the adoption plan. Any faithfulness comparison across answer models with a shared judge family should treat the flag as a confounder.
- **Repair-population bias.** Repaired responses were generated under a different prompt. One bounded repair keeps the bias small and the budget's `Used()` flag makes it measurable, but a population with many repairs is measuring a slightly different instrument; repair rates belong in run summaries.
- **First-to-last-brace JSON extraction.** Both sources and the kernel slice from the first `{` to the last `}`. A payload containing two JSON objects, or prose with braces after the object, parses the wrong span and fails admission (safe) or, in contrived cases, parses an unintended object that happens to validate (unsafe). The fuzz campaign found no such admitted-but-wrong case, which is finite evidence only; a stricter incremental decoder is a candidate hardening.
- **Prompt-version labeling drift.** Nothing forces a version bump when a caller edits prompt text; the replay is safe regardless, but population labels can silently span two instruments. Project 01 (frozen instruments) owns the general mechanism — source locks over prompt constants — that closes this.
- **The Lean/Go gap.** The theorems are about a miniature. The correspondence is reviewable but informal; treating the Lean results as statements about the Go binary would repeat exactly the refinement-gap mistake the [[Research/Software Architecture Garden/sessionstream/designs/research/02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables|sessionstream research]] warns against.

## 10. Open questions

1. Should the salvage layer (rag-ttc statuses over strict admission) be part of the kernel as a second package, so its denominator vocabulary is standardized too — or does that pull campaign policy into the kernel?
2. Human-agreement calibration is designed in rag-ttc (shared-rubric workbook) and computed nowhere. What is the minimal agreement artifact — per-statement human labels on a fixed sample, kappa against judge verdicts — and where does it live so the empirical rows of §4 stop being unmeasured?
3. Can the Lean miniature be tied to the Go implementation mechanically — e.g., a shared JSON test-vector corpus that both the Lean checker (via `#eval`) and the Go `Admit` must classify identically — turning the informal correspondence into executable evidence?
4. Should duplicate-citation and relevance-range rules enter the Lean model, or is the marginal assurance below the modeling cost?
5. Is statement deduplication extraction policy (as here and in rag-ttc) or admission policy? A duplicated statement is arguably a judge-input defect the extractor caused; the current placement hides it from the rejection taxonomy.
6. When a repaired response is admitted, should the score carry a `repaired: true` mark down to the cell record, making repair-population bias visible per cell rather than per run?

## 11. Working rules

- Score only what was admitted; possession of `Admitted` is the only proof of admission.
- Compute estimators; never ask a model for a score a validator can derive.
- Keep the vacuous case unrepresentable rather than conventionally represented and separately excluded.
- Repair at most once per cell, only on structural invalidity, never on valid-but-unwelcome results.
- Label empirical residue (entailment fidelity, calibration, self-preference) as model properties; export no API that implies otherwise.
- Bump the population version for any instrument change — prompt, validator, or scoring policy alike.
- Report means only with their denominators; an empty population is undefined, not zero.
- State what each proof, fuzz campaign, and mutation run establishes, and what it does not.

## Related notes

- [[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]] — the research-family index and overlap analysis
- [[Research/Software Architecture Garden/coinvault/README|CoinVault]] — the port under study
- [[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]] — the ancestor under study
- [[Research/Software Architecture Garden/ragopt/README|Ragopt]] — the experiment kernel whose adapters would consume this package
- [[Research/Software Architecture Garden/sessionstream/designs/research/02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables|Sessionstream — Constraining the Go Binary]] — the guarantee-taxonomy and refinement-gap discipline this project follows
