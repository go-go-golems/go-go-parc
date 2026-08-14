---
title: Constraint-First Gates and the Authority Ladder
aliases:
  - Gate algebra research project
  - Lexicographic constraint domination formalization
  - Witness gate human authority ladder
status: proposed
type: architecture-garden-research
created: 2026-08-14
analyzed: 2026-08-14
repository: /home/manuel/go/pkg/mod/github.com/go-go-golems/ragopt@v0.0.1
comparison_repositories:
  - /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault
  - /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/rag-ttc
tags:
  - architecture-garden
  - research
  - evaluation
  - gate
  - lexicographic
  - constraint-domination
  - lean4
  - go
  - ragopt
  - coinvault
  - rag-ttc
related_files:
  - "specs/gatealgebra/lean/GateAlgebra.lean"
  - "specs/gatealgebra/go/gatealgebra.go"
  - "specs/gatealgebra/go/authority.go"
related_notes:
  - "[[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]]"
  - "[[Research/Software Architecture Garden/ragopt/README|Ragopt]]"
  - "[[Research/Software Architecture Garden/coinvault/README|CoinVault]]"
  - "[[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]]"
  - "[[Research/Software Architecture Garden/sessionstream/designs/research/02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables|Sessionstream — Constraining the Go Binary]]"
---

# Constraint-First Gates and the Authority Ladder

Three repositories in the evaluation-loop family decide whether a challenger beats an incumbent, and all three refuse to let preference touch that decision until every constraint has passed. Ragopt's `gate.Evaluate` runs identity, hard, target, and regression phases in fixed order and appends cost observations that cannot change the verdict (`pkg/gate/evaluate.go:45-121`). CoinVault's retrieval mini-gate `retrievalSummaryWins` demands no regression on five metrics plus at least one improvement (`cmd/coinvault/cmds/knowledge.go:1656-1668`). rag-ttc delegates its gate entirely to Ragopt, passing only a policy path (`cmd/rag-ttc/cmds/tooleval/ragopt.go:132`). The pattern was named in the Garden studies — constraint-first decisions, the judge as witness, human-only application — but the *algebra* behind it was never stated, and the claims that justify the implementation shortcuts (that `stopAfter` is only an optimization, that missing data can never rescue a candidate, that tie-breakers are inert) were never proved.

This project states the algebra, proves its load-bearing theorems in Lean 4, rebuilds the gate as a small pure Go package whose property tests re-check the theorems on the implementation, and encodes the witness → gate → human authority ladder in the type system with a verified compile-error witness. The most useful result is negative: two of the gate's own statistics — the failure rate and the presence-guarded mean delta — are **not** monotone under missing data in isolation. Dropping a failing pair makes both look better. The unconditional complete-pairing identity check is the single mechanism that restores monotonicity for the whole gate, which means it is load-bearing infrastructure, not bookkeeping, and no future refactor may make it policy-optional.

> [!summary]
> - The gate algebra is: phases are lists of boolean checks; a phase passes iff all its checks pass (intra-phase totality); a failed phase ends evaluation (inter-phase short-circuit); tie-break checks are constant-true observations.
> - Five theorem families are proved in core Lean 4 (no mathlib) and re-checked as Go property tests: short-circuit soundness, failed-phase inertness, verdict order-invariance, tie-break inertness, and gate-level missing-data monotonicity — plus two decidable counterexamples showing the failure-rate and mean-delta checks are non-monotone alone.
> - The verdict is order-free; the transcript is not. Phase order is therefore a blame-assignment choice, not a decision choice — the same distinction CoinVault's `FirstFailure` makes for answer contracts.
> - Preference is reported, never decided: ragopt constructs every tie-break check with `Passed: true` (`pkg/gate/evaluate.go:274`), and the Lean rescue-mutant example plus a seeded Go mutant show what deleting that property looks like and that the golden suite catches it.
> - The authority ladder is enforced by a package boundary: the prototype exports no path to an authorized `Application`, external forging is a verified compile error, and a reflection-based structural guard fails the moment anyone adds an apply path to the library.
> - Everything checked is finite or model-level evidence: the Lean model corresponds to the Go code by construction and property tests, not by verified translation, and ragopt itself was read, not modified.

## 1. Research question

```text
What are the algebraic properties of lexicographic constraint-domination
gates — short-circuit soundness, missing-data monotonicity, phase-order
sensitivity — and how can a type system enforce that witness, gate, and
human hold three different kinds of authority?
```

The question matters because all three repositories treat these properties as true without stating them. Ragopt's `stopAfter` (`pkg/gate/evaluate.go:280-293`) is written as if stopping early cannot change the verdict. The Ragopt Garden study's law "missing is explicit, never zero" is about comparison construction (`pkg/compare/build.go:95-100`), but nothing establishes that the *gate* inherits safety from it. And the human-application boundary — `review_required` with `human_apply_required: true` fixed in `pkg/report/types.go:14-31` — is enforced today by the absence of an apply command, which is a convention a future contributor can break in one commit.

## 2. The three implementations are three different decision structures

Reading the code side by side yields the first finding: the family does not share one gate. It shares one *law* (constraints dominate preference) realized in three algebraically distinct structures.

| Implementation | Structure | Feasibility | Preference | Missing-data stance |
|---|---|---|---|---|
| Ragopt `gate.Evaluate` (`pkg/gate/evaluate.go:45-121`) | Lexicographic constraint domination: identity → hard → target → regression phases, then informational tie-breaks | Conjunction of all phase checks; short-circuit between phases | **Reported, never decided**: tie-break checks are constructed `Passed: true` (`:274`); external readers compare costs across candidates | Unconditional `complete_pairing` identity check (`:68-69`); target and regression checks fail closed on absent metrics (`:155-158`, `:198-210`) |
| CoinVault `retrievalSummaryWins` (`cmd/coinvault/cmds/knowledge.go:1656-1668`) | Weak Pareto dominance: challenger wins iff no metric regresses and at least one improves | All five metrics are constraints simultaneously; no phases, no order | Improvement on *any* metric suffices; no ranking among metrics | Not applicable — both summaries come from the same completed eval run; a query failure is scored as a miss upstream (`internal/knowledge/eval.go:280-284`) |
| CoinVault `BestCell` (`internal/knowledge/sweep.go:182`) | Lexicographic total preference: complete-hit rate, then coverage, then MRR, then lower rank constant, then grid order | None — every cell is feasible by construction (same eval set, same run) | Total, deterministic order; always selects a winner | Not applicable for the same reason |
| rag-ttc (`cmd/rag-ttc/cmds/tooleval/ragopt.go:132`) | Delegation: passes `shared/gate-policy.yaml` to Ragopt; no in-repo gate exists | Ragopt's | Ragopt's | Ragopt's |

The differences are principled, not accidental. `retrievalSummaryWins` compares two *routes* under one instrument where every metric is safety-relevant and none is designated the target, so Pareto dominance — which can refuse to pick a winner — is the right structure. `BestCell` ranks thirty *fusion configurations* where a winner must always exist for the sweep to be useful, so a total lexicographic preference is right. `gate.Evaluate` decides *promotion evidence*, where a wrong pass is expensive and a refusal is cheap, so constraint domination with fail-closed missing-data handling is right. The adoption plan below deliberately does **not** unify them; it names them so future code reviews can ask "which of the three structures is this, and is it the right one for the stakes?"

One more implementation detail deserves promotion to a finding: `gate.Evaluate` begins by recomputing the policy's semantic digest and rejecting the document if it drifted (`pkg/gate/evaluate.go:52-58`, tested by `TestEvaluateRejectsMutatedPolicyDocument`, `pkg/gate/evaluate_test.go:71-80`). The gate checks its own instrument identity before evaluating anything — research project 01's frozen-instrument law appearing *inside* the decision function.

## 3. The formal algebra

The model lives in [[Research/Software Architecture Garden/Research/evaluation-loops/specs/gatealgebra/lean/GateAlgebra.lean|specs/gatealgebra/lean/GateAlgebra.lean]] and checks with `lean GateAlgebra.lean` under Lean 4.33.0, core library only. Definitions first.

A report type $R$ is abstract. A **check** is a named predicate $c : R \to \mathbb{B}$. A **phase** is a named list of checks, and intra-phase totality is:

$$
\mathrm{phasePasses}(r, P) \;=\; \bigwedge_{c \in P} c(r).
$$

Two evaluators are defined over a list of phases. The **strict** evaluator runs everything:

$$
\mathrm{evalStrict}(\vec{P}, r) = \mathrm{pass} \iff \bigwedge_{P \in \vec{P}} \mathrm{phasePasses}(r, P),
$$

and the **short-circuit** evaluator mirrors ragopt's `stopAfter`: it evaluates phases in order, records the transcript, and stops at the first failing phase. The intra-phase totality is not an invention of the model — ragopt's `hard-fail` golden records both `require_completed=fail` and `max_failure_rate=fail` in one phase (`pkg/gate/testdata/hard-fail.golden`), so failures within a phase accumulate and only the *next* phase is cut off.

### T1 — short-circuit soundness (`sc_status_eq_strict`)

$$
\mathrm{evalSC}(\vec{P}, r).\mathrm{status} \;=\; \mathrm{evalStrict}(\vec{P}, r)
\quad\text{for all } \vec{P}, r.
$$

Proved by induction on the phase list. `stopAfter` is a transcript and cost policy; the verdict it produces is exactly the conjunction over every phase, evaluated or not. This licenses the implementation shortcut and also licenses tooling: a strict re-evaluation of a stored decision (as `report.Build` effectively performs when it recomputes the decision, `pkg/report/render.go:18-79`) can never disagree with the short-circuited original on status.

### T2 — a failed phase makes later phases irrelevant (`failed_phase_inert`)

If $\mathrm{phasePasses}(r, P) = \mathrm{false}$, then for all continuations $\vec{Q}, \vec{Q}'$:

$$
\mathrm{evalSC}(P \mathbin{::} \vec{Q}, r) = \mathrm{evalSC}(P \mathbin{::} \vec{Q}', r)
\quad\text{and the status is } \mathrm{fail}.
$$

This is the formal content of *constraint domination*: not merely that preference is evaluated last, but that once a constraint phase fails, the decision — status and transcript both — is invariant under arbitrary replacement of everything after it. No content of the target, regression, or tie-break phases can rescue a hard failure, because the decision no longer depends on them at all.

### T3 — the verdict is order-free; the transcript is not

$$
\mathrm{evalStrict}(\vec{A} \mathbin{+\!\!+} \vec{B}, r) = \mathrm{evalStrict}(\vec{B} \mathbin{+\!\!+} \vec{A}, r),
$$

and the same commutation holds for check order inside one phase (`strict_phase_order_irrelevant`, `phase_check_order_irrelevant`). A decidable example then shows the short-circuit *transcript* does depend on order: with a failing phase F and passing phase P, `[F, P]` evaluates one phase and `[P, F]` evaluates two, with equal status.

This answers the phase-order-sensitivity question precisely. Two policies with permuted checks are always **verdict-equivalent** (given T4's inert tie-breaks) and generally **transcript-inequivalent**. Phase order is therefore a *blame-assignment* choice: it decides which failure is named first, exactly as CoinVault's `FirstFailure` walks contract stages in fixed order so "the first responsible stage names the failure class" (`cmd/coinvault/cmds/knowledge_ragopt_contract.go:244`). Ragopt's identity → hard → target → regression order encodes a diagnostic philosophy — identity drift is a worse explanation than a hard failure, which is worse than a missed target — and changing it would change what operators read, not what passes.

One honest boundary: T3 holds for total, pure checks. Ragopt's target evaluation can return an *error* on non-finite accumulation (`checkedMean`, `pkg/gate/evaluate.go:357-373`), and error paths need not commute. In practice `compare.Build` already rejects non-finite metrics at admission (`pkg/compare/build.go:63-67`), so on admitted reports the checks are total and the theorem applies; but a reordering refactor in code that *can* error should re-verify this assumption.

### T4 — tie-break inertness (`tiebreak_inert`)

Appending a phase that passes on the report never changes the status. Ragopt's tie-break phase passes on *every* report by construction, since each check is created with `Passed: true` (`pkg/gate/evaluate.go:274`) — preference is a row of observations ("candidate minus incumbent mean provider_calls delta"), not a vote. The Lean file also defines `evalRescueMutant`, the evaluator that lets the last phase overwrite the verdict, and exhibits a two-phase witness where strict fails and the mutant passes. That mutant is re-seeded in Go and caught by the golden suite (section 6).

The policy layer completes the picture: tie-breakers come from a closed allowlist of four cost names with duplicates rejected (`pkg/policy/policy.go:167-179`). A product cannot smuggle a quality metric into the preference tier, because the preference tier only speaks cost.

### T5 — gate-level missing-data monotonicity, and why it is conditional

Model the denominator-relevant slice of a report as `(expected, complete, failures)` and the two checks

$$
\mathrm{pairing}(r) \equiv (\mathrm{complete} = \mathrm{expected}),
\qquad
\mathrm{failRate}_{p/q}(r) \equiv (\mathrm{failures} \cdot q \le p \cdot \mathrm{expected}).
$$

**Counterexample C1** (decidable, checked): with a zero failure budget, $(\mathrm{expected}, \mathrm{complete}, \mathrm{failures}) = (2,2,1)$ fails $\mathrm{failRate}_{0/1}$, and dropping the failing pair — $(2,1,0)$ — passes it. The failure rate's denominator is the schedule (`ExpectedPairs`, `pkg/compare/build.go:275`), but its numerator counts only *observed* failures, so deleting the observation deletes the failure. **Counterexample C2** shows the same shape for the presence-guarded target mean: deltas $\{+2, -3\}$ fail mean $\ge 0$; dropping the $-3$ pair passes it.

**Theorem** (`dropped_report_fails`, `dropped_target_fails`): in a gate whose phase list contains the unconditional pairing check, every report obtained by dropping a pair from a fully paired schedule fails, for every failure budget and every threshold. So data loss can flip pass → fail (the safe direction) but never fail → pass. The gate's pass-set is contained in the fully-paired reports, and monotonicity of the whole follows even though two of its parts are non-monotone.

The design rule this extracts, stated for reuse:

```text
Every aggregate must either carry the schedule denominator for the same
event space as its numerator, or sit behind an unconditional completeness
check earlier in the phase order. A statistic whose denominator shrinks
with the data (means over present pairs) and a statistic whose numerator
counts only observed events over a fixed denominator (failure rates) are
both improvable by deletion.
```

A corollary about ragopt's own policy surface: the optional hard-phase `require_all_cells` check (`pkg/gate/evaluate.go:77-80`) is *redundant* with the unconditional identity `complete_pairing` check under `compare.Build`'s invariant that pairs plus missing pairs account for the schedule. Its value is that policy authors see completeness stated in their own policy file. The redundancy is harmless today, but the load-bearing copy is the unconditional one, and any refactor that makes completeness purely policy-optional deletes theorem T5. This should be recorded in ragopt's package documentation.

## 4. The Go prototype: `gatealgebra`

The package in [[Research/Software Architecture Garden/Research/evaluation-loops/specs/gatealgebra/go/gatealgebra.go|specs/gatealgebra/go]] is a standalone module (`GOWORK=off go test ./...` passes, 13 tests) implementing the proven algebra with ragopt-faithful phase content. Its API decisions, each with its reason:

**Nominal digests.** `PolicyDigest` is a defined type with a validating constructor. Ragopt's own Garden study records "historical schemas overload `policy_digest`" — the byte digest that binds execution and the semantic digest that identifies parsed meaning share a field name — and its first API implication is nominal types for exactly these identities. A defined type makes the confusion a compile error instead of a review comment.

**Purity is load-bearing, not stylistic.** `Evaluate(Policy, Report) Decision` performs no I/O, reads no clock, and consults no globals. This is what makes three other things possible: `report.Build`-style recomputation (a stored decision can be re-derived from durable evidence and rejected on mismatch), golden testing (the transcript is a deterministic function of the inputs), and T1's strict/short-circuit equivalence check as a property test. A gate that reads anything outside its arguments silently gives up all three.

**Phase-tagged checks and the transcript as evidence.** Every `Check` carries its `Phase`, and the transcript preserves evaluation order. Because the verdict is order-free (T3) but the transcript is the blame assignment, the transcript — not the status — is what goldens must pin. The mutation results below demonstrate this concretely.

**The authority ladder is three types, not three comments.** The witness produces a `Report` (numbers, no authority). The gate produces a `Decision` (verdict plus transcript, no ability to act). Application authority is represented by `Application`, whose authorization evidence is the unexported `approvedBy` field, and the package exports *no* constructor, factory, or method returning an `Application`. Outside the package the only constructible value is the zero value, and it answers `Authorized() == false`. The forging attempt is preserved as a build-tagged witness (`forge_attempt.go`) and was verified externally against go1.26.5:

```text
cannot refer to unexported field approvedBy in struct literal of type
gatealgebra.Application
```

Two guards keep the property true over time. A black-box test (`authority_test.go`, package `gatealgebra_test`) asserts the zero value is unauthorized. A reflection-based structural guard in the go-go-datadrop genre walks the exported types' method sets and fails if any method ever returns `Application` — the test that fails the moment someone adds an apply path to the library. This is deliberately stronger than ragopt's current enforcement, which is the *absence* of an apply command; absence is a fact about today's code, while the guard is a fact about every future commit that keeps the tests green.

What the type system cannot do is also worth stating: it cannot force the human to deliberate. `Application` being unforgeable in-library means application authority must come from *somewhere else* — a product's own deployment workflow, as in ragopt's `review_required` plan — and that somewhere else can still be careless. The ladder's top rung is organizational, and the types only guarantee the library never impersonates it.

## 5. Correspondence between the Lean model and the Go implementation

The model and the implementation are kept honest with each other by construction and by re-checking, not by verified translation. The Go package's property tests re-run the theorems on the real implementation over a deterministic enumeration (17 reports × the policy, and every single-pair drop of each):

- `TestShortCircuitStatusEqualsStrict` re-checks T1: `Evaluate` and `evaluateStrict` agree on status everywhere in the enumeration, and the short-circuit transcript is never longer.
- `TestDroppingPairsNeverFlipsToPass` re-checks T5 at gate level: every drop from every enumerated fully-paired report fails.
- `TestFailureRateAloneIsNotMissingMonotone` re-checks C1 against the implementation: the `max_failure_rate` check flips to pass after the drop while `complete_pairing` catches it and the gate still fails.

This is the light-weight end of the [[Research/Software Architecture Garden/Research/01 - Theory-to-Code Correspondence Manifests|theory-to-code correspondence]] spectrum: the correspondence is maintained by hand and re-checked by finite tests, and that limitation is recorded in the guarantee taxonomy below rather than papered over.

## 6. Mutation sensitivity

Two mutants are seeded in `mutants_test.go`, chosen to attack the two properties a gate exists to protect:

**The rescue mutant** (`evaluateRescueMutant`) lets a passing tie-break phase reset a failed verdict to pass — the deletion of constraint domination. On the hard-fail fixture the correct gate fails, the mutant passes, and the pinned `hard-fail.golden` rejects the mutant's output. Caught by status and by transcript.

**The reorder mutant** (`evaluateReorderedMutant`) swaps the hard and target phases. As T3 predicts, its *status* is identical to the correct gate's on the hard-fail fixture — a status-only assertion cannot catch it. Its *transcript* differs (target checks appear before the hard failure), and the transcript golden rejects it. This is the concrete demonstration that golden tests for gates must pin transcripts: a suite asserting only pass/fail would silently admit phase-reordering refactors that change every operator-facing failure explanation.

The golden corpus itself replicates ragopt's scenario shapes (pass, hard-fail with two failures recorded in one phase, target-fail, regression-fail, tie-break, incomplete-pairing) plus one scenario ragopt's goldens do not have: `hard-floor-fail` versus `regression-fail` for the *same* safety drop, showing that the hard metric floor shadows the case-delta regression check unless the floor is loosened. Phase coverage overlaps, and which phase names a failure depends on thresholds — one more reason the transcript is the artifact of record.

## 7. The algebra applied: reading a production policy

The theorems become concrete against a real policy. CoinVault's `default-results-8-v7` candidate ships this gate policy (`configs/ragopt/default-results-8-v7/shared/gate-policy.yaml`):

```yaml
hard_gates: {require_all_cells: true, require_completed: true, require_contract_valid: true,
             max_failure_rate: 0, metric_floors: {faithfulness: 0.80}}
target:     {metric: answer_relevance, groups: [feedback], minimum_mean_delta: 0}
regressions:
  maximum_case_delta: {faithfulness: -0.20, answer_relevance: -0.30}
  maximum_mean_delta: {all: {faithfulness: -0.05, answer_relevance: -0.05}}
tie_breakers: [provider_calls, tool_calls, total_tokens, duration]
```

Compiled into the algebra, this is four constraint phases over a 12-case × 1-repeat × 2-arm report, then four inert observations. What the theorems then guarantee for this specific document:

- **T5 with `max_failure_rate: 0`:** the failure-rate check alone would pass a run in which every failing cell simply went missing (C1 is exactly the zero-budget case). The policy author gets monotonicity not from their `require_all_cells: true` — which is optional — but from the unconditional `complete_pairing` identity check. If a future ragopt version made completeness fully policy-controlled, this policy would *look* maximally strict while becoming deletion-gameable.
- **T2 for the recorded rejections:** the `grounded-answer-v2` terminal decision rejected promotion because five of twenty-four cells failed hard gates, while the *causal* comparison-case evidence was dramatic (faithfulness 0.46 → 1.00). T2 is why no strength of that target-phase evidence could rescue the run: after the hard phase failed, the decision was invariant under everything downstream. The CoinVault study's "double verdict" — gate outcome versus causal learning — is the operational face of failed-phase inertness.
- **T3 for review:** swapping `maximum_case_delta` and `maximum_mean_delta` evaluation order, or reordering the two metric floors, could never change which candidates pass — only which reason string an operator reads first. Reviewers of policy changes can therefore ignore pure reorderings and concentrate on threshold changes.
- **T4 for the cost row:** all four tie-breakers are listed, and none can veto. A candidate that doubles provider calls while passing every constraint passes; the cost delta is evidence for the *human* on the ladder's top rung, which is where ragopt's `review_required` plan sends it.

The floor/regression shadowing from section 6 also appears here: a faithfulness collapse to 0.65 would be named `metric_floor:faithfulness` (hard phase), not `maximum_case_delta:faithfulness` (regression phase), because 0.65 < 0.80 trips the floor first. Operators reading rejection reasons should know that the earliest phase wins the naming rights even when several phases would object.

## 8. Guarantee taxonomy

| Evidence | Establishes | Does not establish |
|---|---|---|
| Lean theorems T1–T5 (`lean GateAlgebra.lean`, exit 0, Lean 4.33.0 core) | The stated properties for **all** phase lists, reports, and thresholds *of the model* | That the Go or ragopt implementations are instances of the model |
| Lean decidable examples C1, C2, rescue-mutant witness | Existence of the specific counterexamples | Anything universal |
| Go property tests over deterministic enumeration | T1, T5, C1 hold on the **implementation** for the enumerated space (17 reports, all single drops) | Behavior outside the enumeration; universal quantification |
| Golden transcript tests (7 scenarios) | Pinned end-to-end behavior including phase order and intra-phase totality | Correctness of the pinned behavior beyond review |
| Seeded mutants (rescue, reorder) | The suite detects deletion of constraint domination and of transcript order | Detection of unenumerated defect classes |
| Compile-error witness + structural guard | No authorized `Application` is constructible outside the package, now or while tests stay green | That the human on the top rung deliberates; organizational authority |
| Read-only source analysis of ragopt/CoinVault/rag-ttc at their pinned snapshots | The comparative findings of section 2 | Any change to those repositories; their behavior at other commits |

Nothing here is a universal proof about ragopt's binary. The theorems are about the algebra; the algebra was extracted from ragopt's code and goldens by reading; the prototype re-checks the theorems on itself.

## 9. Adoption plan

1. **Ragopt (smallest step, highest value):** adopt nominal digest types for the byte/semantic policy digests — its own study already lists this as implication #1 — and add one sentence to `pkg/gate` documentation recording that the unconditional `complete_pairing` identity check is what makes the gate missing-data monotone (theorem T5), so it must never become policy-optional. Optionally port the reorder-mutant test; its goldens already pin transcripts, so the suite is one seeded mutant away from proving it.
2. **Ragopt (medium):** consider whether `require_all_cells` should be documented as policy-visible restatement of an unconditional invariant rather than an independent control, so policy authors do not conclude that omitting it permits partial runs.
3. **CoinVault:** no migration. `retrievalSummaryWins` and `BestCell` are different decision structures serving different stakes (section 2); the adoption is vocabulary — name them "weak-Pareto improvement gate" and "lexicographic preference" in code comments so reviewers ask the right question.
4. **The family:** if the evaluation-loop projects converge on a shared module, `gatealgebra`'s shape — pure `Evaluate`, phase-tagged transcript, nominal digests, no apply path — is the candidate API, with the Lean file and property tests carried alongside as the package's correspondence evidence. Adoption cost is honest: ragopt's gate works and is tested; the prototype's value is the proofs and guards, which can be adopted without adopting the code.

## 10. Decision records

### DR-1: The verdict is an order-free conjunction; the transcript is the ordered diagnosis

- **Decision:** specify gate semantics as T1/T3: status equals the conjunction over all constraint phases; phase order affects only the transcript.
- **Rationale:** proved; licenses short-circuiting and strict recomputation; makes phase order reviewable as a blame-assignment choice.
- **Consequence:** golden tests must pin transcripts, not statuses; status-only assertions cannot catch reordering.
- **Status:** accepted (proved in Lean, re-checked in Go).

### DR-2: Preference is reported, never decided

- **Decision:** tie-break checks are constant-true observations, as in ragopt; any selection among gated survivors happens outside the gate.
- **Rationale:** T4 makes the phase provably inert; the policy allowlist keeps quality metrics out of the preference tier.
- **Consequence:** multi-candidate selection needs a separate, explicitly-named preference structure (BestCell-style) applied only to passes.
- **Status:** accepted.

### DR-3: Application authority is a package boundary, not a runtime check

- **Decision:** represent application authority as a type constructible only inside the library, with no exported path to an authorized value; guard with a compile witness and a reflection walk.
- **Rationale:** ragopt's "no apply command" is a fact about today; the guard converts it into a property of every future green build.
- **Consequence:** the library can never grow a convenience apply path without failing its own tests; human authority remains organizational and is documented as such.
- **Status:** accepted for the prototype; proposed for ragopt.

### DR-4: Core Lean 4 without mathlib

- **Decision:** model in core Lean with `omega` for arithmetic and `decide` for witnesses; cross-multiplied rational comparisons instead of real-valued means.
- **Rationale:** zero dependency setup on this machine; every proof obligation here is finite-structure or linear-arithmetic; Float reasoning would buy nothing but cost.
- **Consequence:** the model's numbers are exact rationals; float-specific hazards (NaN ordering in `BestCell`'s `!=` switch, non-finite accumulation) live outside the model and are noted as open question 3.
- **Status:** accepted.

## 11. Open questions

1. Should the Lean model and Go implementation share a serialized fixture corpus (Lean `#eval` exporting decisions, Go replaying them) to upgrade the hand-maintained correspondence into a mechanical one, in the spirit of the [[Research/Software Architecture Garden/sessionstream/designs/research/02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables|sessionstream trace-refinement bridge]]?
2. Ragopt's group-scoped targets fail closed when a group selects zero pairs (`selectedPairs > 0` required, `pkg/gate/evaluate.go:155-158`). The model covers dropped pairs but not dropped *groups*; extending T5 to group-scoped selection would close that gap.
3. Float hazards: `BestCell`'s comparison switch treats NaN asymmetrically, and `checkedMean` can error mid-phase. Both live outside the exact-arithmetic model. Is admission-time finiteness validation (compare.Build's) a sufficient shield everywhere a gate-family check runs, including CoinVault's mini-gates over `EvalSummary` floats?
4. Should preference over gated survivors (a cross-candidate `BestCell`) ever enter the shared gate API, or does codifying it invite exactly the preference-creep the constant-true tie-break design exists to prevent?
5. When the judge kernel (project 03) and run custody (project 04) land, the ladder spans packages: witness metrics flow from judged cells into `Report`. What is the minimal shared vocabulary (nominal metric names? denominators as types?) that keeps the witness/gate boundary typed across module seams?

## 12. Working rules

- State the gate's semantics as an order-free conjunction plus an ordered transcript; never let a refactor claim they are the same thing.
- Every aggregate a gate consumes either carries the schedule denominator for its numerator's event space or sits behind an unconditional completeness check.
- Tie-breakers are observations; if a check can change the status, it is a constraint and belongs in a constraint phase.
- Pin transcripts in goldens; statuses alone cannot catch reordering.
- Keep the gate pure; recomputation and audit depend on it.
- Application authority is never minted by the library; guard the absence structurally, not by convention.
- Report model-level proofs as model-level proofs; finite enumerations as finite enumerations.

## Artifacts and verification evidence

```text
specs/gatealgebra/lean/GateAlgebra.lean   lean GateAlgebra.lean → exit 0 (Lean 4.33.0)
specs/gatealgebra/go/                     GOWORK=off go vet ./...   → clean
                                          GOWORK=off go test ./... -count=1 → ok, 13 tests
specs/gatealgebra/go/testdata/*.golden    generated with -update, hand-reviewed
specs/gatealgebra/go/forge_attempt.go     compile-error witness, verified externally
                                          against go1.26.5 on 2026-08-14
```

## Related notes

- [[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]] — the overlap analysis this project executes
- [[Research/Software Architecture Garden/ragopt/README|Ragopt]] — the primary gate implementation and its recorded debt
- [[Research/Software Architecture Garden/coinvault/README|CoinVault]] — the mini-gate and sweep preference structures
- [[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]] — the delegating consumer and the authority-ladder thesis
- [[Research/Software Architecture Garden/Research/01 - Theory-to-Code Correspondence Manifests|Theory-to-Code Correspondence Manifests]] — where the model↔code correspondence discipline comes from
