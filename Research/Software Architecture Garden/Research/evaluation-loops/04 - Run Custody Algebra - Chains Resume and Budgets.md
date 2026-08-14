---
title: Run Custody Algebra — Chains, Resume, and Budgets
aliases:
  - Run custody formalization
  - Hash-chained journal resume proofs
  - Budget accountant verification
status: proposed
type: architecture-garden-research
created: 2026-08-14
analyzed: 2026-08-14
repositories:
  - /home/manuel/go/pkg/mod/github.com/go-go-golems/ragopt@v0.0.1
  - /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault
tags:
  - architecture-garden
  - research
  - evaluation-loops
  - experiment-custody
  - hash-chain
  - resume
  - budgets
  - tla-plus
  - tlc
  - go
  - crash-safety
related_files:
  - Research/Software Architecture Garden/Research/evaluation-loops/specs/runcustody/tla/RunCustody.tla
  - Research/Software Architecture Garden/Research/evaluation-loops/specs/runcustody/tla/Budget.tla
  - Research/Software Architecture Garden/Research/evaluation-loops/specs/runcustody/go/journal.go
  - Research/Software Architecture Garden/Research/evaluation-loops/specs/runcustody/go/budget.go
related_notes:
  - "[[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]]"
  - "[[Research/Software Architecture Garden/ragopt/README|Ragopt]]"
  - "[[Research/Software Architecture Garden/coinvault/README|CoinVault]]"
  - "[[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]]"
  - "[[Research/Software Architecture Garden/sessionstream/designs/research/02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables|Sessionstream — Constraining the Go Binary]]"
---

# Run Custody Algebra — Chains, Resume, and Budgets

An evaluation campaign spends real money on provider calls and produces evidence that later gates a promotion decision. Two failure families threaten it: losing or corrupting committed evidence when the process dies mid-campaign, and spending past a hard ceiling when accounting and admission drift apart. Ragopt and CoinVault each built defenses — a hash-chained append-only cell journal with exact-coordinate resume in Ragopt, a pre-reserving budget accountant with a sticky conservative close in CoinVault — and each defense carries an implicit correctness argument that has so far lived only in code review and one interruption test.

This research project makes those arguments explicit and checks them. The custody mechanisms are stated as a small algebra — journals as hash-linked words, resume as an ordered set difference over exact coordinates, budgets as a reserved-plus-spent counter under a ceiling — and the resulting claims are checked twice: as bounded TLA+ models run through TLC, and as a dependency-free Go prototype (`specs/runcustody/`) whose tests include crash simulation at every interruption point and a race-detected concurrency suite. The project also does something the source repositories cannot do in their own test suites: it uses TLC to *exhibit* the honest non-claim — external effects are at-least-once, never exactly-once — as a concrete counterexample trace rather than a sentence in a README.

> [!summary]
> - The custody story decomposes into three independently checkable claims: chain integrity (tampering with a committed prefix is detected on reload), resume equivalence (a resumed run commits exactly the uninterrupted run's coordinate sequence), and budget safety (completed spend never exceeds the ceiling, and unprovable spend closes admission stickily).
> - All three hold in bounded TLC checks and in the Go prototype, including under `-race`; four seeded mutations (skip the completed-coordinate check, skip torn-tail recovery, drop the reservation, ignore the close latch) each produce the predicted counterexample or test failure.
> - The at-least-once boundary is demonstrated, not assumed: TLC refutes `AtMostOnceEffects` with a five-state trace — effect, crash, recover, re-execute — and the Go resume-equivalence test asserts the doubled effect count at every interruption point.
> - The decisive design insight from the budget model: ceiling safety under concurrency requires the guard and the admission to be one atomic step (a reservation). CoinVault's sequential answer budget is safe without one only because arms are sequential; its judge runtime pre-reserves precisely because it is not.
> - A reusable `runcustody` package API falls out of the algebra: `Coord`/`Record`/`Journal` for chained custody, `Plan` for resume, and an `Accountant` whose `Reserve() → Reservation{Commit,Rollback}` shape makes the atomic-guard requirement unrepresentable to get wrong.
> - Everything here is finite evidence: TLC checks small bounds, tests check chosen fixtures, and filesystem durability (fsync, O_APPEND, truncate) is an assumed platform contract, not a proved one.

## 1. Research question

The pinned implementations answer operational questions with mechanism. This project asks whether the mechanisms compose into provable claims:

```text
(a) Resume equivalence   For every interruption point, does resume execute
                         exactly the absent coordinates, and does the final
                         committed journal equal the uninterrupted run's?

(b) Chain integrity      Are deletion, reordering, and in-place edits of a
                         committed prefix always detected on reload?

(c) Budget safety        Can completed spend ever exceed the ceiling, and
                         can work start after spend became unprovable?

(d) Honest non-claims    What exactly is NOT guaranteed — and can the gap
                         be exhibited rather than merely asserted?
```

## 2. Baseline evidence

All claims below were verified by reading the pinned sources; nothing is cited from memory.

### 2.1 Ragopt: the journal and resume protocol

The journal commit boundary is `runstore.AppendJSONL`: marshal one record, append under the run mutex, `fsync` the file, and sync the directory entry on first creation; the doc comment declares each successful return "a durability boundary suitable for interruption and later resume" (`pkg/runstore/run.go:256-307`). Chain sealing and validation live in `pkg/eval/cell_chain.go:10-42`: `sealCell` blanks the digest field, marshals, and stores `sha256(record-with-blank-digest)`; `validateCellChain` checks the stored `PreviousDigest` against the running head and recomputes the digest.

Resume is three cooperating pieces:

1. `runstore.Resume` reopens only an *active* run and only under the exact canonical config digest, and states its single-writer boundary in its doc comment: no inter-process lock; the operator guarantees one writer (`pkg/runstore/run.go:32-59`).
2. `loadCompletedCells` truncates-and-syncs a torn final line, then strict-decodes every retained line, validates the hash chain, requires each cell's key to be in the expected schedule, rejects duplicates, and re-verifies each cell's native artifact (`pkg/eval/resume.go:13-78`, truncation at `:30-40`, `truncateAndSync` at `:105-130`).
3. `execute` iterates the deterministic schedule (case-major, incumbent/challenger adjacent, `buildSchedule` at `pkg/eval/runner.go:301-312`) and skips any coordinate present in the completed map, keyed by `expectedCellKey` = suite digest ∥ policy digest ∥ candidate ID ∥ snapshot digest ∥ case ∥ repeat ∥ arm (`runner.go:735-745`); each executed cell is sealed against the running head and appended (`runner.go:239-260`).

The interruption test `TestInterruptedRunResumesToUninterruptedCanonicalResult` (`pkg/eval/runner_test.go:26-99`) cancels at the fourth arm call, observes three durable cells of sixteen, appends a deliberately torn tail fragment, resumes, asserts the resumed writer performs exactly the thirteen missing calls starting at the correct cell, and requires the canonicalized resumed cell set to `DeepEqual` an uninterrupted run's.

Within one cell, `executeCell` shows the effect/commit window this project models: the arm runs (external effects happen), the outcome is validated, the native artifact is copied to a run-owned synced inode — and only then does the cell append commit (`runner.go:314-386` then `:250`). A crash anywhere in that window loses the commit but not the effects.

### 2.2 CoinVault: the budget accountant

`gecRagoptExecutionBudget` (`cmd/coinvault/cmds/knowledge_ragopt.go:1115-1122`) is a mutex-guarded accountant with three ceilings and a sticky close:

- `AllowAnswerRun` refuses to start another arm when closed or when calls/tokens have reached their ceilings (`:1128-1141`);
- `Observe` accounts each finished provider call and additionally errors when the budget is exactly exhausted by a call that `HasToolCalls` — stopping the tool loop before its next iteration rather than after (`:1157-1172`);
- `CloseForUncertainProviderSpend` latches the first reason for the remainder of the run (`:1146-1155`);
- `Seed` installs prior durable spend exactly once, rejecting seeds above a ceiling (`:1194-1208`), fed by `loadGECRagoptResumeUsage`, which strict-decodes every prior native artifact, cross-checks its identity against its cell, and re-validates its treatment and contract reports before trusting its usage numbers (`:1210-1251`).

The judge runtime uses a different, fused mechanism: `reserveProviderCall` atomically increments the call counter and rolls back on ceiling breach (`cmd/coinvault/cmds/knowledge.go:2163-2170`), with `SeedProviderCalls` CAS-guarded to run once (`:2150-2161`). The failure-custody note (`ttmp/2026/08/07/GEC-RAG-OPT-002/reference/41-failed-cell-provider-usage-custody.md`) records the design position this project formalizes: when a provider-started event has no matching finished event, the adapter "cannot prove the final cost… and closes admission for later provider-backed cells. This is intentionally conservative."

Note the asymmetry the models must capture: the *answer* budget's guard (`AllowAnswerRun`) and its spend (`Observe`, later) are separate atomic steps with no reservation between them. That is safe in CoinVault only because arms execute sequentially. The *judge* path, which may be driven from concurrent contexts, pre-reserves. Whether the unreserved design is a latent hazard is exactly question (c).

## 3. The algebra

### 3.1 Journals are hash-linked words

Let $C$ be the set of exact coordinates and $R$ the set of records. A journal is a word $r_1 \cdots r_n \in R^*$ where each $r_j$ stores $prev_j = digest(r_{j-1})$ (empty for $j{=}1$) and $digest(r_j)$ computed over $r_j$ with its digest field blank. Validation of a claimed word succeeds iff every link recomputes, which gives:

**Claim (chain integrity).** For a validated load, the accepted word is the unique untampered append history: deleting $r_i$ breaks $prev_{i+1}$; reordering breaks the first displaced link; editing $r_i$ in place breaks $digest(r_i)$. (Assuming SHA-256 collision resistance; and detecting nothing about truncation of a *suffix* — see §7.)

### 3.2 Resume is an ordered set difference

Let $S = \langle c_1, \ldots, c_m \rangle$ be the deterministic schedule over exact coordinates, and $D \subseteq C$ the coordinates of the validated committed word. The resume plan is

$$
Plan(S, D) = \langle c_i \in S \mid c_i \notin D \rangle
$$

in schedule order, with the side condition $D \subseteq range(S)$ (a foreign committed coordinate aborts).

**Claim (resume equivalence).** For a sequential writer, $D$ is always a prefix of $S$; executing $Plan(S,D)$ to completion yields a committed word equal to $S$ itself — the uninterrupted result — for every interruption point.

### 3.3 Budgets are reservation counters

A budget state is $(spent, reserved, closed)$ with ceiling $M$. Admission requires $\lnot closed \wedge spent + reserved < M$ and increments $reserved$; completion moves one unit from $reserved$ to $spent$; rollback releases one unit; close latches $closed$ forever.

**Claim (budget safety).** $spent + reserved \le M$ is inductive, hence $spent \le M$ always; and no admission occurs after $closed$. The load-bearing property is that the guard and the increment of $reserved$ are one atomic step. Splitting them — check the ceiling now, spend later, reserve nothing — breaks the invariant with as few as two concurrent callers.

## 4. Guarantee taxonomy

| Evidence | Establishes | Does not establish |
|---|---|---|
| TLC on `RunCustody.tla` (base) | Within the modeled bounds (4 coordinates, 1 crash), every behavior keeps the journal a distinct schedule prefix, recovery precedes trusted appends, and terminal runs committed the whole schedule exactly once. | Unbounded schedules; real filesystem semantics; multi-writer behavior. |
| TLC refutation of `AtMostOnceEffects` | A concrete legal trace where one coordinate's external effect runs twice. This is the at-least-once boundary made exhibit. | That re-execution is *frequent* or *harmful* — that depends on product effect idempotency. |
| TLC on `Budget.tla` (base) | With 2 workers × 2 attempts and ceiling 2, spend never exceeds the ceiling, reservations account soundly, and nothing starts after close. | Real token costs (post-hoc by nature); fairness or liveness; cross-process budgets. |
| TLC on the four mutation configs | The invariants are load-bearing: each seeded protocol deletion produces the predicted counterexample. | Completeness of the mutation set. |
| Go prototype tests | The concrete mechanisms (fsync-append journal, truncate recovery, strict reload, plan, accountant) implement the algebra on a real filesystem, at every interruption point of the fixture schedule, with `-race` clean concurrency for the accountant. | That ragopt/CoinVault's production code equals the prototype; that fsync semantics hold on every platform/filesystem. |
| Reading of pinned sources (§2) | The modeled protocol is the production protocol's shape. | A mechanical refinement relation between model and production code. |

## 5. TLA+ models and results

### 5.1 `RunCustody.tla`

The model keeps ragopt's essentials and abstracts the rest. The schedule is the four-coordinate word `⟨c1/inc, c1/chal, c2/inc, c2/chal⟩`. The writer's cycle is two steps — `ExecEffect` (the arm runs; the external effect counter increments; the record is pending) then `CommitCell` (the atomic append) — because that two-step window is where the at-least-once truth lives. `Crash` (bounded to one) drops the pending record, optionally leaves a torn tail, and `Recover` truncates it before the schedule resumes against the durable prefix. The hash chain is represented by construction (`durable` is a sequence); chain *checking* is deliberately left to the Go prototype, because in an abstract model where digests are perfect the check is vacuous — the model checks the protocol above the chain, the prototype checks the chain itself.

Two mutation constants delete one protocol obligation each: `SkipCompletedCheck` makes the resumed writer restart the schedule from the top (deleting `execute`'s completed-map skip), and `SkipTailRecovery` lets the next append land on a torn tail (deleting `truncateAndSync`).

> [!success] TLC results — base protocol (TLC2 2.19, 2026-08-14)
> `RunCustody.cfg` checks `DurableDistinct`, `DurableIsSchedulePrefix`, `JournalWellFormed`, and `CompletionExact`: **no error**, 85 states generated, 66 distinct, depth 13. The state count is small because the sequential writer admits little nondeterminism beyond the crash point and the torn flag — which is itself a faithful property of the design.

> [!success] TLC exhibits the at-least-once boundary
> `RunCustodyAtMostOnce.cfg` adds `AtMostOnceEffects` (every coordinate's effect runs at most once). TLC **violates it at depth 5** (21 generated / 18 distinct): `ExecEffect(c1/inc)` → `Crash` (pending lost, journal empty) → `Recover` → `ExecEffect(c1/inc)` again, `effects[c1/inc] = 2`. This is precisely the crash-between-effect-and-commit window in `executeCell` (`runner.go:314-386`) before the `AppendJSONL` at `:250`, and it is why ragopt's own docs refuse the words "exactly-once": resume re-executes the coordinate, so any external effect must be idempotent at the *product* layer or accepted as repeatable.

> [!success] Mutation sensitivity
> `RunCustodyMutSkipCheck.cfg` (resume without the completed check): **`DurableDistinct` violated**, depth 7, 36/30 states — the resumed writer re-commits an already-committed coordinate. `RunCustodyMutSkipRecovery.cfg` (no torn-tail truncation): **`JournalWellFormed` violated**, depth 5, 25/24 states — the first post-crash append lands on the partial line. Both counterexample traces are archived under `specs/runcustody/tla/results/`.

### 5.2 `Budget.tla`

The budget model has two workers, each admitted (`Admit` = atomic guard-plus-reserve), completing (`Complete` = spend lands), or abandoning (`Rollback`), with an environment `Close` that can latch at any time. Attempts are bounded at two per worker; the ceiling is two calls. Its mutations: `NoReservation` (the guard checks `spent < M` but reserves nothing — the check-then-spend-later shape of `AllowAnswerRun` + `Observe` if arms were concurrent) and `IgnoreClose`.

> [!success] TLC results — accountant (TLC2 2.19, 2026-08-14)
> Base `Budget.cfg`: `SpentWithinCeiling`, `ReservationSound`, `NoStartAfterClose` — **no error**, 200 states generated, 98 distinct, depth 10.
>
> `BudgetMutNoReserve.cfg`: **`SpentWithinCeiling` violated**, depth 7 (126/74 states): both workers pass the guard at `spent = 1`, ceiling 2, then both complete → `spent = 3`. `BudgetMutIgnoreClose.cfg`: **`NoStartAfterClose` violated** at depth 3 (17/12): `Close` then an admission.

The `NoReservation` counterexample is the model's most useful output, because it classifies the two production mechanisms: CoinVault's judge runtime (`reserveProviderCall`, an atomic add-then-check-with-rollback — reservation and spend fused into one atomic step) is in the safe class; CoinVault's answer budget (`AllowAnswerRun` guard now, `Observe` spend later, nothing reserved between) is in the unsafe class *if arms ever run concurrently*, and is safe today only by the sequential-arms convention. That convention is currently enforced by nothing but the shape of `execute`'s loop.

## 6. Go prototype and results

`specs/runcustody/go/` is a dependency-free module (`evaluationloops.research/runcustody`, Go 1.26) with three files mirroring the algebra:

- `journal.go` — `Coord` (exact identity with a NUL-joined `Key()`), `Record`, `seal`/`validateChain` (byte-compatible in shape with ragopt's `sealCell`/`validateCellChain`), and `Journal` with `Open` (torn-tail truncate-and-sync, strict decode, chain validation, schedule membership, duplicate rejection) and `Append` (O_APPEND write + fsync + directory sync on creation; the head advances only after fsync).
- `resume.go` — `Plan(schedule, completed)`: ordered set difference with foreign-key rejection.
- `budget.go` — `Accountant` with one-shot `Seed`, atomic `Reserve() (*Reservation, error)`, `Reservation.Commit(tokens)` / `Rollback()` (idempotent settle), sticky `CloseForUncertainSpend`, and `Snapshot`.

The test suite checks each claim where the abstraction cannot:

| Test | Claim exercised |
|---|---|
| `TestJournalRoundTrip` | Append/reload identity over the full schedule. |
| `TestTornTailTruncatedAndJournalContinues` | Crash mid-append: recovery truncates, syncs, and the journal keeps accepting appends on the surviving head. |
| `TestInPlaceEditDetected` / `TestReorderDetected` / `TestDeletionDetected` | Chain integrity: the three tamper families each fail reload with the predicted error (`digest mismatch`, `previous digest mismatch` ×2). |
| `TestDuplicateCoordinateDetected` / `TestUnexpectedIdentityDetected` | Reload-side protocol checks beyond the chain: a correctly sealed duplicate and a foreign coordinate are both rejected. |
| `TestResumeEquivalenceAtEveryInterruptionPoint` | For every interruption point k ∈ 1..4: interrupt between effect and commit (leaving a torn tail), resume, and require the committed sequence to `DeepEqual` the uninterrupted baseline — while asserting `effects[interrupted] == 2` and all others `== 1`. The at-least-once refutation and the equivalence theorem in one loop. |
| `TestAccountantCeilingUnderConcurrency` (`-race`) | Eight goroutines racing `Reserve`/`Commit` land on exactly the ceiling with zero leaked reservations. |
| `TestRollbackReleasesReservation` / `TestStickyCloseRefusesNewWorkAndKeepsFirstReason` / `TestTokenCeilingIsPostHoc` / `TestSeedOnceBeforeSpendAndWithinCeilings` | The accountant's edges: idempotent settle, first-reason latch, honest post-hoc token accounting (the overshooting commit is recorded *and* reported), seed-once-before-spend. |
| `TestNaiveCheckThenSpendOvershoots` | The executable twin of `BudgetMutNoReserve`: two goroutines, a barrier between guard and spend, and an assertion that the naive design **does** overshoot. The test passes by demonstrating the failure. |

> [!success] Go results (go1.26.5, 2026-08-14)
> `GOWORK=off go vet ./...` clean; `GOWORK=off go test ./... -count=1` — **ok** (0.025s); `GOWORK=off go test ./... -race -count=1` — **ok** (1.085s). All 13 tests pass, including the deliberate-overshoot demonstration.

## 7. Model/implementation correspondence and assumed platform contracts

The models and prototype are honest only together with their assumptions:

1. **fsync establishes durability.** `AppendJSONL`'s comment and the prototype both treat write+fsync as the commit boundary. On a filesystem or device that lies about flush, the "durable prefix" is weaker than modeled. This is a trusted platform contract, exactly as the Go compiler and memory model are trusted in [[Research/Software Architecture Garden/sessionstream/designs/research/02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables|the sessionstream refinement study]].
2. **Torn tails are suffixes.** Recovery truncates a final partial *line*. A corruption that manifests mid-file (bit rot, concurrent writer) is detected by the chain, not repaired; the run is then unreadable by design. The chain also cannot detect *suffix truncation along the chain boundary*: a journal cut back to a shorter valid prefix validates cleanly. Ragopt compensates at a higher layer — `execute` requires completed = expected before finalization (`runner.go:266-268`) and `finalizeRun` re-audits the whole run (`:272-281`) — so a truncated journal yields missing coordinates, not silent acceptance. The model's `CompletionExact` captures that obligation; a library adopting the journal without a completion check would lose it.
3. **Single writer is a precondition, not a theorem.** `runstore.Resume` documents that no inter-process lock exists (`run.go:32-34`). Both the model (one writer) and the prototype assume it. The Ragopt Garden entry already records the missing writer fence as an open obligation; this project inherits, and does not discharge, it.
4. **Effect idempotency is product-owned.** The at-least-once trace is a fact of the two-step effect/commit window. The only honest mitigations are product-side idempotency keys or acceptance of repeatable effects — never a claim of exactly-once resume. CoinVault's response is different and complementary: when even the *accounting* of the effect is unprovable, close the budget (`CloseForUncertainProviderSpend`), trading campaign length for spend certainty.
5. **The abstract digest is perfect; the real one is SHA-256.** Chain claims inherit collision-resistance assumptions, as the Ragopt study already notes; the chain is integrity, not signed authenticity.

## 8. Proposed reusable API

The prototype doubles as the API proposal. Three shapes earned their place:

1. **`Coord` as a first-class exact identity with an explicit `Key()`.** Ragopt builds keys inline in two places (`expectedCellKey`, `cellKey`) that must agree by review; a nominal type with one join function removes the duplication. In a real extraction the key must also bind the frozen run identity (suite/policy/candidate/snapshot digests) — the prototype documents this narrowing.
2. **`Journal.Open` returning `(journal, completed)` in one call.** Recovery, validation, and the resume input are one operation; there is no API state in which a caller holds a journal whose torn tail has not been truncated or whose records were not validated. Ragopt's `loadCompletedCells` already has this shape internally; the proposal is to make it the *only* door.
3. **`Reserve() → Reservation{Commit, Rollback}`.** The TLC counterexample shows the unsafe design is a *natural* one — guard here, spend there. Returning a reservation object makes the atomic-guard requirement structural: there is no way to spend without having reserved, mismatched bookkeeping becomes a type error rather than a review finding, and the idempotent settle prevents double-release. Token ceilings stay honestly post-hoc: `Commit(tokens)` records the overshoot and reports it, mirroring `Observe`'s exceed-then-error and the exhausted-before-next-iteration rule.

Adoption targets, in order of value: Ragopt could adopt the `Reservation` accountant directly if it ever grows concurrent arms or in-kernel budget enforcement (today budgets are product-adapter code in CoinVault); CoinVault's answer budget could migrate to the reservation shape, converting the sequential-arms convention from an implicit safety argument into an enforced one; and any future evaluation harness in the family gets journal/resume custody without re-deriving the seven validation rules `loadCompletedCells` accumulated.

The extraction cost is honest: Ragopt's journal validation is entangled with cell semantics (native-artifact re-verification inside `validateStoredCell`), so a generic journal needs a validation hook per record — a small interface, but a real API commitment.

## 9. Decision records

### DR-1: Model the effect/commit window as two steps

- **Context:** Whether to model a cell as one atomic action or as effect-then-commit.
- **Decision:** Two steps, with crash allowed between them.
- **Rationale:** The single most important honest claim (at-least-once) lives in that window; an atomic-cell model would prove a pleasant falsehood.
- **Status:** accepted; validated by the `AtMostOnceEffects` refutation and the doubled effect count in the Go test.

### DR-2: Represent the chain by construction in TLA+, check it in Go

- **Context:** Modeling SHA-256 in TLC is possible (digest = prefix) but makes tamper detection tautological.
- **Decision:** TLC checks the protocol above the chain (distinctness, prefix, recovery, completion); the Go prototype checks the chain itself against real byte-level tampering.
- **Consequence:** Neither artifact alone covers both layers; the document must always present them together.
- **Status:** accepted.

### DR-3: The reservation is the API, not a guideline

- **Context:** The unsafe check-then-spend shape is idiomatic and passed review in CoinVault (safe there only by sequential arms).
- **Decision:** The proposed accountant exposes no unreserved spend path at all.
- **Rationale:** TLC shows two callers suffice to overshoot; a convention held by loop shape is one refactor away from a violation.
- **Status:** proposed.

### DR-4: Keep the sticky close latch mono-directional

- **Context:** A closed budget could plausibly reopen once accounting is reconciled later.
- **Decision:** No reopen operation exists; the first reason latches (as in `CloseForUncertainProviderSpend`).
- **Rationale:** Reopening converts a proof obligation ("spend is now proven") into a runtime judgment call inside the cheapest-to-get-wrong component. The failure-custody note's position — conservative, run-scoped — is preserved as algebra.
- **Status:** proposed.

## 10. Risks

- **Bounded checks breed overconfidence.** 4 coordinates and 1 crash cover the protocol's combinatorics but not, for example, repeated crash/resume cycles; a follow-up config with `crashes ≤ 2` and a longer schedule is cheap insurance.
- **The prototype could drift from production.** The value of §6 depends on the prototype staying a faithful miniature of `cell_chain.go`/`resume.go`/`run.go`. If Ragopt's validation rules change, the prototype and this document age silently. A correspondence manifest ([[Research/Software Architecture Garden/Research/01 - Theory-to-Code Correspondence Manifests|Theory-to-Code Correspondence Manifests]]) is the designed remedy.
- **Filesystem contracts vary.** fsync-on-directory behavior differs across platforms; the prototype's tests pass on Linux/ext4-like semantics and prove nothing elsewhere.
- **The missing writer fence remains missing.** Nothing here adds inter-process exclusion; two resumed writers can still interleave appends into a chain that validates per-writer but not globally. This is the highest-value follow-up (Ragopt study, "Single-writer resume and external effects").

## 11. Open questions

1. Should the exact-coordinate key be widened in the generic package to carry the frozen-identity digests (as `expectedCellKey` does), or should identity binding remain a wrapper concern with the journal generic over an opaque key?
2. Can the completion obligation (`CompletionExact`) move into `Journal` itself — a `Finalize(schedule)` that refuses while coordinates are missing — without stealing the runner's failure-classification role?
3. Is a two-crash TLC campaign worth running to check crash-during-recovery (torn tail created, recovery itself interrupted)?
4. Should the accountant's post-hoc token overshoot close the budget automatically (today: error returned, caller decides), aligning it with the sticky-close philosophy?
5. What is the minimal writer fence compatible with Ragopt's no-daemon design — an O_EXCL lease file with a staleness protocol, or flock on the journal itself — and can its safety be added to `Budget.tla`/`RunCustody.tla` as a third model?

## 12. Working rules

- Model the window where the honest limitation lives; never atomize it away.
- Every invariant ships with at least one mutation that TLC or a test must reject.
- Exhibit non-claims as counterexample traces, not prose.
- Keep chain checking and protocol checking in the layer that can actually falsify each.
- Treat fsync, rename, and single-writer as named platform/operator contracts, listed with the results that depend on them.
- A convention that a model proves load-bearing (sequential arms) should be promoted into a type or a fence, not documented harder.

## Related notes

- [[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]] — the research family index and overlap analysis
- [[Research/Software Architecture Garden/ragopt/README|Ragopt]] — the journal/resume implementation and its recorded open obligations
- [[Research/Software Architecture Garden/coinvault/README|CoinVault]] — the budget accountant, resume seeding, and failure custody
- [[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]] — the ancestor loop discipline
- [[Research/Software Architecture Garden/sessionstream/designs/research/02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables|Sessionstream — Constraining the Go Binary]] — the guarantee-taxonomy and mutation-sensitivity conventions this project follows
