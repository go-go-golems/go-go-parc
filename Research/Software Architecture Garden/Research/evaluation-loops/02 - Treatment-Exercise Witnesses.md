---
title: Treatment-Exercise Witnesses — Proving a Mutation Was Causally Live
aliases:
  - Treatment exercise formalization
  - Configuration is not behavior
  - Exercise witnesses for paired experiments
status: proposed
type: architecture-garden-research
created: 2026-08-14
analyzed: 2026-08-14
repository: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault
repository_commit: 10d1a8d8c5b281f78b4e73d3956be573dcc8fad1
comparison_repositories:
  - /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/rag-ttc (0b0e420925ec9919f2e89838b23df722cb5e3b3d)
  - ~/go/pkg/mod/github.com/go-go-golems/ragopt@v0.0.1
tags:
  - architecture-garden
  - research
  - evaluation
  - causal-experiments
  - treatment-exercise
  - trace-predicates
  - go
  - tla-plus
  - ragopt
  - coinvault
related_files:
  - cmd/coinvault/cmds/knowledge_ragopt_treatment.go
  - cmd/coinvault/cmds/knowledge_ragopt.go
  - cmd/coinvault/cmds/knowledge_ragopt_trace.go
related_notes:
  - "[[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]]"
  - "[[Research/Software Architecture Garden/coinvault/README|Architecture Garden — CoinVault]]"
  - "[[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]]"
  - "[[Research/Software Architecture Garden/ragopt/README|Architecture Garden — Ragopt]]"
---

# Treatment-Exercise Witnesses — Proving a Mutation Was Causally Live

A paired incumbent/challenger experiment can be flawless in every custody dimension — frozen inputs, digest-verified snapshots, hash-chained cells, exact resume — and still measure nothing. That is not a hypothetical: CoinVault's first six `default_results 5→8` candidates were structurally perfect experiments in which both arms behaved identically, because the answering model supplied an explicit `limit: 5` on every `knowledge_search` call and the mutated fallback default never determined behavior. The mutation was installed; it was never *live*. The program's own textbook names the lesson: configuration is not behavior (GEC-RAG-OPT-002, `design-doc/05-evaluation-judging-and-optimization-textbook.md:321-334`).

CoinVault's answer is the treatment-exercise report: a per-cell, per-arm proof, computed from the observed event trace, that the declared mechanism actually determined runtime behavior — and a typed failure class, `treatment_not_exercised`, that pre-empts judging when the proof fails (`cmd/coinvault/cmds/knowledge_ragopt.go:625-643,691-692`). This research project asks whether that product-specific mechanism generalizes: can "the mutation was causally live" be stated as a decidable predicate over observed traces, packaged as a reusable kernel with the same purity discipline as Ragopt's gate, and inserted into Ragopt's cell contract without importing any product vocabulary?

> [!summary]
> - Exercise is decidable and generic: a mechanism is a canonical ordered set of named pure checks over (declared arm parameters, contract invariants, observed trace); `Exercised` is exactly the conjunction, applicability is a separate predicate, and the contract must list the mechanism's check set exactly — a dropped or smuggled check is an admission error, not a silent weakening.
> - Exercise witnesses come in strength classes. Budget-style mechanisms yield **determination witnesses** (the observed value provably came from the mutated source); identity-style mechanisms yield **consultation witnesses**; digest-style prompt mechanisms yield only **installation witnesses**. A contract should say which class it delivers; the classes must not be conflated.
> - Exercise is symmetric across arms: the incumbent must prove the declared *absence* of the treatment as actively as the challenger proves its presence, or a leaked treatment silently contaminates the baseline.
> - A checked Go prototype (`specs/treatment/`, 12 tests, `go vet` clean) implements admission, evaluation, and report re-validation, and rejects the historical neutralized-treatment shape, forged `Exercised` flags, dropped checks, and equal-armed contracts.
> - A TLC-checked TLA+ model (`specs/treatment/tla/`) proves, over all interleavings of the abstract cell pipeline, that a judge score exists only for attributable cells; weakening the guard to ignore exercise produces the exact counterexample TLC reports (`JudgeAttribution` violated at a judged, applicable, unexercised cell).
> - The proposed Ragopt insertion is minimal: an optional typed `Treatment` report on `eval.Outcome`, a reserved `treatment_not_exercised` failure class validated against it, and a separate `pkg/treatment` kernel. Products keep the trace vocabulary and mechanism definitions; the kernel owns admission, conjunction, and re-validation.

## 1. Research question

The current CoinVault implementation answers, per cell:

```text
Did the single declared mutation determine observable runtime behavior
in this arm of this cell, according to this mechanism's checks?
```

This project asks three sharper questions:

1. **Formalizability.** Is there a precise, product-neutral definition of *applicability* and *exercise* as predicates over observed traces, with stated soundness and completeness boundaries — what a passing conjunction does and does not establish about the two arms' behavioral difference?
2. **Generality.** Can CoinVault's nine mechanism families (`knowledge_ragopt_treatment.go:79`) be expressed as instances of one declarative shape — canonical check set, applicability predicate, arms-must-differ rule — so that a new product registers mechanisms instead of forking harness code?
3. **Adoptability.** What is the minimal change to Ragopt's cell contract (`eval.Outcome`, `eval.Cell` at `ragopt@v0.0.1/pkg/eval/types.go:55-87`) that makes treatment exercise a first-class, validated concept rather than a product convention, while preserving Ragopt's rule that case inputs and native evidence remain opaque?

## 2. The evidence base

### 2.1 CoinVault: the full mechanism

The treatment contract is a locked candidate asset (`gec-ragopt-treatment-contract/v1`) declaring mechanism, mutation asset, eligibility, exactly two arms with mechanism-specific parameters, semantic invariants, and a check list (`knowledge_ragopt_treatment.go:19-49`). Admission is strict and mechanism-aware: arms must differ in the mechanism's parameter (equal defaults rejected at `:177-179`, equal prompt digests at `:153-155`, equal tool-description identities at `:170-176`); enablement must agree with digest presence (`:148-152`); and the check list must equal a per-mechanism *exact sorted set* — the comparison at `:205-209` joins sorted names with `\x00` and rejects any deviation. A check cannot be silently dropped.

Evaluation (`evaluateGECRagoptDefaultResultsTreatment`, `knowledge_ragopt.go:845-990`) is a pure function over the collected trace. For the fallback-default mechanism it counts, per knowledge call, whether the configured default matched the arm, whether at least one call resolved its effective limit from the fallback source at the arm's value (`call.EffectiveLimitSource == "default" && call.EffectiveLimit == expectedDefault`, `:877-879`), whether every call produced an observed result, and whether every call carried the contract's invariant identities. `Exercised` is set to the conjunction of all checks and nothing else (`:982-988`). Non-applicable cases return an empty report; a non-applicable report claiming evidence is rejected by the validator (`:1009-1014`), as is an `Exercised` flag disagreeing with its own conjunction (`:1031-1033`) and a check set differing from the contract (`:1072-1081`).

The consequence sits in the cell executor: `treatment.Applicable && !treatment.Exercised` adds an issue (`:626-628`), the judge runs only when `len(issues) == 0` (`:635`), and the failure class is `treatment_not_exercised` with the message "configured knowledge treatment did not determine an effective knowledge_search behavior" (`:691-692`). Treatment reports are also computed on failure paths (`buildGECRagoptFailureOutcome`, `:793`), so every native artifact carries one regardless of how the cell ended.

The observations this depends on are supplied by a trace collector that is itself a validator: each knowledge call records the full limit-resolution story — requested, configured default, maximum, forced, effective, and provenance `EffectiveLimitSource ∈ {server_forced, explicit, default, explicit_clamped}` — plus the three semantic identities and the reranker/tool-description runtime identities (`knowledge_ragopt_trace.go:14-41`).

### 2.2 rag-ttc: the ancestor without the proof

The rag-ttc `optimize` command carries arm difference the same way — the mutable assets arrive through the Ragopt candidate view and are materialized into the arm's working directory (`cmd/rag-ttc/cmds/tooleval/ragopt.go:311-317`: five required assets checked for *presence*, then `materializeToolConfig`) — but there is no exercise check: materialization is trusted. Both generations share one executor for both arms (`:128-133`), which is the right architecture for treatment isolation, but rag-ttc proves only that the assets were installed, not that they determined behavior. The [[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc optimization study]] records this as the generational delta: CoinVault added the exercise proof after paying for its absence six times.

### 2.3 Ragopt: the static counterpart

Ragopt already proves the *static* half of the causal story: `Mutation` is computed independently from parent/child snapshot bytes, and the author's declaration must equal the computed single difference (`ragopt@v0.0.1/pkg/candidate/types.go:78-86` and the loader's validation). What Ragopt cannot see is the *dynamic* half — whether that byte difference was consulted at runtime. The cell contract has a `Failure{Class, Message}` (`pkg/eval/types.go:49-52`) that products may populate with any class, which is exactly where `treatment_not_exercised` currently travels, as an unvalidated string convention.

The division of labor is therefore already clean and already incomplete:

```text
Ragopt proves:      parent and child differ in exactly one declared asset   (static)
Product must prove: that asset determined behavior in its arm               (dynamic)
Nothing validates:  that the product actually proved it                     (the gap)
```

## 3. Formal statement

### 3.1 Traces, contracts, mechanisms

Let $V$ be a set of opaque fact values (strings in the prototype). A **cell trace** for one arm execution is a pair

$$
\tau = (\gamma, w), \qquad \gamma : K_{cell} \rightharpoonup V, \qquad w = o_1 o_2 \cdots o_n \in O^*,
$$

where $\gamma$ maps cell-scoped fact keys to observed values (for example, the digest of the actually-installed prompt suffix), and each observation $o_i = (\mathit{point}_i, \nu_i)$ carries a point name and a fact map $\nu_i : K_{obs} \rightharpoonup V$ (one `knowledge_search` call with its limit provenance and identities). The word structure matters only insofar as checks may quantify over it; no check in the current families depends on observation *order*, a deliberate simplification recorded as an open question in §9.

An **arm declaration** is $\alpha : P \rightharpoonup V$ over mechanism parameter keys. A **contract** is

$$
\kappa = (m,\ \{\alpha_{inc}, \alpha_{cha}\},\ \iota,\ N),
$$

naming a mechanism $m$, two arm declarations, invariant facts $\iota : K_{inv} \rightharpoonup V$, and a declared check-name set $N$.

A **mechanism** is a triple

$$
m = (C_m,\ \mathit{app}_m,\ \mathit{diff}_m),
$$

where $C_m = \langle c_1, \ldots, c_k \rangle$ is the canonical ordered list of named checks, each a *pure total* function

$$
c_j : (\alpha, \iota, \tau) \to \mathit{Evidence} = (\mathit{expected}, \mathit{observed}, \mathit{passed} \in \mathbb{B}),
$$

$\mathit{app}_m : \mathit{Case} \to \mathbb{B}$ is the applicability predicate, and $\mathit{diff}_m$ is the arms-must-differ admission rule.

### 3.2 The three obligations

**Admission.** $\kappa$ is admitted iff $m$ is registered, both arms are present, $\mathit{diff}_m(\alpha_{inc}, \alpha_{cha})$ holds, and $N = \{\mathrm{name}(c_1), \ldots, \mathrm{name}(c_k)\}$ *exactly* (set equality, duplicates rejected). The exact-set rule is what makes the check list reviewable governance rather than advisory documentation: weakening the proof obligation requires editing the mechanism definition, which in CoinVault sits behind the source lock studied in research project 01.

**Exercise.** For an admitted contract, arm $a$, applicable case, and trace $\tau$:

$$
\mathit{Exercised}_m(\alpha_a, \iota, \tau) \;=\; \bigwedge_{j=1}^{k} \mathit{passed}\big(c_j(\alpha_a, \iota, \tau)\big).
$$

There is no partial credit, no privileged check, and no path by which a report can claim exercise other than every check passing. Non-applicable cases are $\mathit{Exercised} = \bot$ with an empty evidence list — absence of obligation, not vacuous success.

**Attribution (the judge guard).** A cell's quality delta is admissible for judgment only if

$$
\mathit{outcome} = \mathit{ok} \;\land\; \mathit{contract} \;\land\; \big(\mathit{app}_m(\mathit{case}) \Rightarrow \mathit{Exercised}\big).
$$

This is the treatment-exercise law in its operational form: judging spend and judged scores exist only for attributable cells.

### 3.3 Symmetry: the incumbent proves absence

$\mathit{Exercised}$ is evaluated per arm against that arm's *own* declaration. For the challenger this proves presence-and-effect; for the incumbent it proves declared absence — the reranker incumbent must show `enabled=false, applied 0/N`, the prompt incumbent must show an empty installed digest. A treatment that leaks into the incumbent (a suffix installed in both arms, a reranker left on) fails the *incumbent's* exercise check, which is exactly right: a contaminated baseline is as unattributable as a neutralized challenger. The prototype's `TestCellDigestMechanism` demonstrates the leak case explicitly.

### 3.4 Witness strength: what a passing conjunction proves

Not all check sets prove the same thing, and the honest formalization must grade them rather than flatten them:

| Class | Definition | Example | What it establishes | What it does not |
|---|---|---|---|---|
| **Installation witness** | The mutated artifact was present in the runtime at its declared identity. | `prompt_suffix_matches_arm` + `prompt_suffix_applied` (digest of the actually-installed suffix) | The bytes reached the runtime; enablement agrees with declaration. | That the model's behavior depended on those bytes. A suffix can be installed, attended to, and ignored. |
| **Consultation witness** | The mutated component was invoked on the observed path. | `reranker_application_matches_arm` (applied on every call), `comparison_plan_applied` | The component executed with the declared configuration on real calls. | That its output changed anything downstream (a reranker can return the input order). |
| **Determination witness** | An observed value provably *came from* the mutated source. | `fallback_default_applied`: at least one call whose `EffectiveLimitSource = default` and effective value equals the arm's declared default | The mutation determined a concrete observed behavior at at least one point. | That the determined behavior mattered to the outcome metric; and nothing about calls where an explicit limit won. |

The v1–v6 failure was precisely a determination gap dressed as an installation success. A contract should therefore *declare* its witness class; a promotion review reading "exercised" must know whether it is reading "installed" or "determined." This grading is the project's main conceptual addition over the source implementation, which treats all check sets uniformly.

### 3.5 Soundness and completeness boundaries

**What passing establishes (soundness of the witness).** Each check is a necessary condition for causal liveness under its class; the conjunction is evidence that the declared mechanism was live *at the witnessed strength* in that arm, at those observation points, with the declared invariant identities held fixed.

**What passing does not establish.**

- It is not a counterfactual proof. $\mathit{Exercised}$ in both arms does not prove the arms' *outcomes* would have differed had the assets been swapped; it proves each arm ran under its declared configuration with the mechanism live. The outcome delta remains the experiment's measurement, not the witness's.
- It does not bound behavior outside the declared mechanism. The invariant-identity checks ($\iota$) pin the *named* confounders — query transform, retrieval policy, evidence ledger — but undeclared environment (provider state, sampling, cache temperature) stays outside, exactly as Ragopt's snapshot dimensions stay outside behavior-completeness. Same constraint, same honesty obligation.
- Failing is not proof of no effect (incompleteness). A prompt suffix that subtly changes tokenization of the system prompt could influence behavior while a *stricter* mechanism's checks fail for unrelated reasons; conversely `treatment_not_exercised` on a budget mechanism means only that the fallback never decided a limit — the installed configuration might still have influenced logging or timing. Not-exercised means *unattributable*, and the correct response is to fix the mechanism or the case, never to interpret the delta anyway.
- The trace is trusted. Checks are only as sound as the collector, which runs in-process with the arm. CoinVault partially mitigates this by making the collector a strict validator (duplicate provider calls, unmatched results, missing identities are hard errors) and by source-locking the collector itself; a fully adversarial arm is out of scope here as it is throughout Ragopt's trust model.

### 3.6 Guarantee taxonomy

| Evidence | Establishes | Does not establish |
|---|---|---|
| Ragopt `Mutation` computation | Parent/child snapshots differ in exactly one declared asset's bytes. | The asset was loaded, consulted, or determined behavior. |
| Contract admission (exact check set, arms differ) | The proof obligation is complete per the mechanism definition and the arms are distinguishable in the declared parameter. | The mechanism definition itself is strong enough (witness class is a separate declaration). |
| Passing exercise conjunction, per arm | Mechanism live at the declared witness strength; invariant identities held on every observation; incumbent absence proven. | Counterfactual outcome difference; behavior outside declared mechanism; influence for installation-class witnesses. |
| `treatment_not_exercised` failure | The cell is unattributable and was excluded from judging and from `Completed`. | That the mutation "does not work" — the mechanism, the case, or the model's call pattern may each be responsible. |
| Report re-validation | A serialized report is internally coherent and matches its contract; forged flags and dropped checks are rejected at read time. | That the producing process observed honestly (trust boundary above). |
| TLC check of the cell model (§5.2) | Over all modeled interleavings, judged ⇒ attributable; artifacts always persist; failures never claim completion. | Anything about the real Go code's conformance to the model (that is the refinement gap studied in the sessionstream program). |

## 4. API design

The prototype (`specs/treatment/`) is a dependency-free pure kernel of roughly 300 lines plus exemplar mechanisms. Its shape is the proposal.

```go
type Case struct { ID string; Labels map[string][]string }
type Observation struct { Point string; Values map[string]string }
type Trace struct { Cell map[string]string; Observations []Observation }

type ArmDeclaration struct { Name string; Parameters map[string]string }
type Contract struct {
    Mechanism  string
    Arms       map[string]ArmDeclaration   // exactly incumbent + challenger
    Invariants map[string]string
    Checks     []string                    // must equal the mechanism's canonical set
}

type Evidence struct { Name, Expected, Observed string; Passed bool }
type Report struct {
    APIVersion string
    Mechanism, Arm string
    Applicable, Exercised bool
    Checks []Evidence
}

type CheckSpec struct {
    Name string
    Eval func(arm ArmDeclaration, invariants map[string]string, trace Trace) Evidence
}
type MechanismSpec struct {
    Name         string
    Checks       []CheckSpec
    Applicable   func(Case) bool
    ValidateArms func(incumbent, challenger ArmDeclaration) error
}
type Registry map[string]MechanismSpec

func AdmitContract(Contract, Registry) (MechanismSpec, error)
func Evaluate(Contract, Registry, armName string, Case, Trace) (Report, error)
func ValidateReport(Report, Contract, Registry) error
```

Design decisions, with rationale:

1. **Mechanisms are registered data plus pure predicates, not harness branches.** CoinVault's nine mechanisms live in one 145-line `if/else` chain inside the evaluator (`knowledge_ragopt.go:884-981`); adding a mechanism means editing source-locked harness code. In the kernel, a mechanism is a `MechanismSpec` value; products register their own, and the kernel's admission/conjunction/validation logic never changes. The exact-check-set rule moves from a hand-maintained `wanted` list per mechanism (`knowledge_ragopt_treatment.go:186-204`) to a derivation from the registered spec, so the contract's set and the evaluator's set cannot drift — in CoinVault they are two lists that must be kept synchronized by review.
2. **Evidence is expected/observed prose, never a bare boolean.** Every failed check explains itself in the artifact, following the CoinVault convention that made the v7 receipts auditable. The validator enforces non-empty expected/observed strings.
3. **`Exercised` is derived, then re-derived.** `Evaluate` computes the conjunction; `ValidateReport` recomputes it from the serialized evidence and rejects disagreement. A report crossing a storage or process boundary is re-admitted, not trusted — the same discipline Ragopt applies to cells and runs on reload.
4. **Applicability is a first-class predicate with library combinators** (`ApplicableAlways`, `ApplicableWhenLabelContains`, `ApplicableToCaseIDs`), generalizing CoinVault's three eligibility shapes (prompt treatments always apply; comparison treatments apply to an eligible-ID list; tool treatments apply when the case requires the tool, `knowledge_ragopt_treatment.go:227-253`). Case metadata is an opaque label map, keeping the kernel product-neutral.
5. **The trace vocabulary is stringly and product-owned — deliberately.** The kernel does not know what `effective_limit` means; the mechanism's checks do. Typing the fact keys would force a shared product vocabulary, which is exactly what Ragopt's opaque-`Case.Input` philosophy exists to avoid. The cost — typos in fact keys fail checks rather than compilation — is accepted and mitigated by mechanism-local key constants.

What the kernel deliberately does not do: it does not observe (collectors are product-owned and trust-bearing), does not decide judging (that guard belongs to the harness, modeled in §5.2), does not compare arms to each other (each report is per-arm; cross-arm reasoning stays in compare/gate), and does not grade witness strength automatically (the class is a declaration, §3.4).

## 5. Checked artifacts

### 5.1 Go prototype

> [!success] `specs/treatment` — 12 tests passing, vet clean — 2026-08-14
> `GOWORK=off go vet ./...` and `GOWORK=off go test ./... -count=1` → `ok github.com/go-go-golems/evaluation-loops-research/treatment 0.003s`.
>
> Mutation sensitivity, all rejected as required:
> - **Neutralized treatment** (`TestNeutralizedTreatmentIsNotExercised`): challenger declares default 8; every observation carries `limit_source=explicit, effective_limit=5` — the exact v1–v6 shape. Result: applicable, not exercised, with `fallback_applied` the *only* failed check, and the truthful not-exercised report passes re-validation.
> - **Forged `Exercised` flag** on that same report → `ValidateReport` rejects (`exercised=true disagrees with check conjunction=false`).
> - **Dropped check** (`fallback_applied` removed from the contract) → admission error `checks must be exactly [...]`; **smuggled check** (`vanity_check` added) → same rejection.
> - **Equal arms** (both defaults 5) → admission error from the mechanism's `ValidateArms`.
> - **Identity drift** (`retrieval_policy_id` differing from the invariant on one observation) → `identities_match` fails, not exercised.
> - **Leaked treatment** (`TestCellDigestMechanism`): the challenger's suffix digest observed in the *incumbent* cell → incumbent not exercised, demonstrating arm symmetry.
> - **Non-applicable report claiming evidence** and **unknown mechanism** → rejected.

### 5.2 TLA+ model of the attribution guard

The model (`specs/treatment/tla/TreatmentCell.tla`) abstracts one cell of the CoinVault adapter into five phases — execute (nondeterministic outcome ok/deadline/infra), assess (contract and exercise valued on every path, mirroring the fact that failure outcomes also carry treatment reports), judge, persist, done — with a constant `Guarded` selecting the production judge guard (`JudgeEligible == outcome = "ok" /\ contractOK /\ (applicable => exercised)`) or a mutated guard that ignores exercise. Four invariants: `JudgeAttribution` (judged ⇒ attributable), `ArtifactTotal` (done ⇒ artifact persisted), `FailureNotCompleted` (typed failure excludes completion, mirroring `finalizeGECRagoptOutcomeState`), and `NotExercisedNamed` (a clean-but-unexercised cell is classified exactly `treatment_not_exercised`, never absorbed into another class).

> [!success] TLC results — 2026-08-14
> **Guarded:** exhaustive, no error — 86 states generated, 66 distinct, depth 5 (`tla/results-guarded.txt`).
> **Mutated:** `Error: Invariant JudgeAttribution is violated` with the four-state counterexample ending in `judged = TRUE /\ applicable = TRUE /\ exercised = FALSE /\ contractOK = TRUE /\ outcome = "ok"` — a judged, neutralized cell, the precise defect class the guard exists to prevent (`tla/results-mutated.txt`).
>
> This is a bounded check of the abstract protocol, not of the Go code; the model-to-implementation link would need the trace-refinement machinery of the sessionstream program if it were ever to be claimed.

## 6. Generalizing into Ragopt

### 6.1 Insertion point

The minimal adoption is three additions to `ragopt`, none of which touches product opacity:

1. **`pkg/treatment`** — the kernel of §4, dependency-free, alongside `pkg/gate` as a second pure evaluator.
2. **One optional field on `eval.Outcome`** (`pkg/eval/types.go:55-67`):

   ```go
   type Outcome struct {
       // ...existing fields...
       Treatment *treatment.Report `json:"treatment,omitempty"`
   }
   ```

   carried into the sealed `Cell` like every other outcome field, and therefore into the hash chain.
3. **A reserved failure class.** `validateOutcome` (in `pkg/eval/runner.go`) gains: if `Failure.Class == "treatment_not_exercised"`, the outcome must carry a `Treatment` report with `Applicable && !Exercised` that passes `treatment.ValidateReport` against the run's admitted contract; conversely a report with `Applicable && !Exercised` on an otherwise successful outcome forces that failure class. This turns today's string convention into a validated invariant, symmetric with the existing rules (failure ⇒ not completed, abstained ⇒ completed).

The treatment *contract* travels where CoinVault already puts it: a locked shared asset in the candidate bundle, loaded by the product arm. Ragopt could optionally learn to admit it (`AdmitContract` at run preparation, so a malformed contract fails before any spend, matching the preflight philosophy), with the mechanism registry supplied by the product through `RunRequest` — registry values are code, so this stays an in-process capability exactly like `Arm` itself.

### 6.2 Adoption cost and what stays product-owned

Costs: one cell API version bump (`ragopt-cell/v1` → `v2` or a tolerant optional-field reading), the validator extension, and CoinVault migrating its bespoke types to the kernel — mechanical, since the kernel's shapes were reverse-engineered from CoinVault's. rag-ttc's harness gains exercise proof for free once its arms populate observations, which its session artifacts already nearly contain.

Product-owned forever: the trace collector and its trust story, the fact vocabulary, the mechanism definitions and their witness-class declarations, and applicability semantics. Ragopt-owned: admission, conjunction, re-validation, the failure-class law, and chain custody of the report. The boundary is the same one Ragopt already draws for `Outcome` versus native artifacts, which is the strongest argument that it is the right one.

### 6.3 Comparison with the alternative: schema-level treatment fields

The rejected alternative is adding mechanism-specific fields to the generic cell (CoinVault's `ConfiguredDefault`, `FallbackCalls`, `RerankerApplied`, ... on `gecRagoptTreatmentReport`, `knowledge_ragopt.go:420-438`). That shape is visible in the source: every new mechanism grew the one struct, and the validator accumulated cross-field rules like "non-budget treatment must not declare result-depth settings" (`:1066-1068`). The generic kernel replaces field accretion with the evidence list; the per-mechanism structure lives in check names and expected/observed strings, which is what the receipts actually consume.

## 7. Decision records

### DR-1: Mechanisms are registered specifications, not harness code paths

- **Context:** CoinVault hard-codes nine mechanisms in evaluator branches behind a source lock; extending requires editing locked harness source.
- **Decision:** a mechanism is a `MechanismSpec` value (canonical checks, applicability, arms-must-differ) in a product-supplied registry; the kernel derives the exact check set from it.
- **Consequence:** contract and evaluator cannot drift; new mechanisms do not touch the kernel; the source-lock obligation narrows to the kernel plus the product's registry file.
- **Status:** proposed, prototype-validated.

### DR-2: `Exercised` is exactly the conjunction, re-derived at every trust boundary

- **Context:** a forged or drifted flag would silently re-admit unattributable cells to judging.
- **Decision:** `Evaluate` derives it; `ValidateReport` re-derives it from serialized evidence and rejects disagreement, dropped checks, duplicates, and non-applicable claims.
- **Consequence:** reports are re-admitted like cells, not trusted; the flag carries no independent authority.
- **Status:** proposed, prototype-validated (forgery test).

### DR-3: Witness strength is a declared class, not an implication of "exercised"

- **Context:** installation, consultation, and determination witnesses prove different things (§3.4); the source implementation labels all of them "exercised".
- **Decision:** contracts declare their witness class; promotion reviews and receipts must surface it next to the exercised flag.
- **Consequence:** a passing prompt candidate reads "installed", not "determined", preventing the next-generation version of the v1–v6 illusion one level up.
- **Status:** proposed; not yet in the prototype's `Contract` type (open question 3).

### DR-4: Exercise is symmetric; the incumbent proves absence

- **Context:** a leaked treatment contaminates the baseline invisibly if only the challenger is checked.
- **Decision:** per-arm evaluation against each arm's own declaration, with absence checks (digest empty, applied 0/N) first-class.
- **Consequence:** contamination fails the incumbent cell with the same typed class; paired comparison never sees a poisoned pair.
- **Status:** matches CoinVault behavior; prototype-validated (leak test).

### DR-5: Unattributable cells are judged never, persisted always

- **Context:** judge spend on a neutralized cell buys a misleading score; dropping the cell would hide the neutralization.
- **Decision:** the guard `outcome=ok ∧ contract ∧ (applicable ⇒ exercised)` gates judging; the artifact with the failed report persists on every path.
- **Consequence:** `treatment_not_exercised` is visible in denominators and receipts; TLC-checked in the abstract model.
- **Status:** matches CoinVault behavior; model-checked here.

## 8. Risks

- **Check-set over-fitting.** A team whose candidate keeps failing `fallback_applied` may be tempted to weaken the mechanism definition rather than the candidate. The exact-set rule moves that edit into the registered spec, and research project 01's source-lock discipline makes it visible, but no mechanism prevents a *reviewed* weakening. Mitigation is procedural: witness-class declarations make the weakening legible ("this now proves installation only").
- **Goodhart pressure on exercise.** A prompt change that instructs the model to omit explicit limits would flip `fallback_applied` from failing to passing — by genuinely changing behavior, which is legitimate, but it converts a budget experiment into a compound prompt-plus-budget experiment. The one-mutation rule guards the asset surface; nothing guards against a single asset whose content is chosen to satisfy the witness. Contracts for budget mechanisms should record the expectation that call patterns are comparable across arms (an aggregate check candidate: explicit-limit rates within a declared tolerance).
- **Probe effect.** The collector observes in-process; its strict validation can turn benign event anomalies into cell failures. CoinVault accepts this (a trace the collector cannot vouch for is a cell that cannot be attributed), and the kernel inherits the stance; the cost is availability, not soundness.
- **False generality.** Nine mechanisms from one product plus one ancestor is thin evidence for the `MechanismSpec` shape. The honest maturity claim is candidate: the shape must survive a mechanism it was not reverse-engineered from (a cache-policy or embedding-model mutation would be a good stress).

## 9. Open questions

1. Should check predicates be able to quantify over observation *order* (for example, "the reranker ran after fusion on every call")? The current families are order-free; admitting order would pull the trace toward the sessionstream interval formalism and should wait for a real mechanism that needs it.
2. How do check sets compose for stacked candidates (CoinVault's `canonical-seed-stack-v1` composes three primitives in one asset)? The natural proposal — conjunction of the component mechanisms' sets over disjoint parameter spaces — needs a real stacked contract to test against, and a decision about whether one failed component fails the stack cell or classifies it per component.
3. Where does the witness class live — a field on `MechanismSpec`, on the contract, or both with agreement validation? (DR-3 requires it somewhere before adoption.)
4. Should Ragopt admit the treatment contract at run preparation (fail before spend) or leave admission entirely to arms? Preflight admission matches the freeze philosophy but requires the registry at prepare time, which slightly widens `RunRequest`.
5. Can an aggregate call-pattern check (explicit-limit rate comparability across arms, §8) be made mechanism-generic without importing product semantics?
6. Is there value in a *quantified* exercise signal (fraction of observation points where the mechanism determined behavior) for gate policies, or does any number beyond the boolean invite exactly the partial-credit reasoning DR-2 forbids?

## 10. Working rules

- State the witness class before celebrating an exercised flag; installation is not determination.
- Evaluate exercise per arm against that arm's own declaration; the incumbent's absence proof is not optional.
- Never judge an unattributable cell; always persist its report and typed failure class.
- Derive `Exercised` from evidence at every boundary; a flag is never authority.
- Keep the exact-check-set rule: weakening a proof obligation must be a reviewed edit to a registered mechanism, never an omission in one contract.
- Keep trace vocabulary and mechanism semantics product-owned; keep admission, conjunction, and re-validation kernel-owned.
- Treat `treatment_not_exercised` as "fix the mechanism or the case", never as a quality verdict on the mutation.
- Report the model check as a check of the abstract protocol; the Go-code-to-model link is unproven and must be labeled so.

## Artifacts

```text
specs/treatment/
├── go.mod
├── treatment.go            kernel: types, admission, evaluation, report re-validation
├── mechanisms.go           exemplars: fallback_default (determination), cell_digest (installation)
├── treatment_test.go       12 tests incl. neutralization replay, forgery, drop/smuggle, leak
└── tla/
    ├── TreatmentCell.tla   abstract cell pipeline with Guarded constant
    ├── TreatmentCell.cfg   guarded: exhaustive pass (86 gen / 66 distinct / depth 5)
    ├── TreatmentCellMutated.cfg  guard ignoring exercise
    ├── results-guarded.txt
    └── results-mutated.txt JudgeAttribution counterexample
```

## Related notes

- [[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]] — the research family index and overlap analysis
- [[Research/Software Architecture Garden/coinvault/README|Architecture Garden — CoinVault]] — the source implementation and its history
- [[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]] — the ancestor harness without the exercise proof
- [[Research/Software Architecture Garden/ragopt/README|Architecture Garden — Ragopt]] — the static mutation proof and the cell contract this project extends
