---
title: Proving the Bounded Asynchronous Observer Dispatcher
aliases:
  - Dispatcher formal verification study
  - TLA+ Alloy Coq Lean proofs for the observer dispatcher
  - Dispatcher correctness transposition study
status: complete
type: architecture-garden-research
created: 2026-08-11
repository: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/sessionstream-p111
verifies_design: "[[Research/Software Architecture Garden/sessionstream/designs/01 - Bounded Asynchronous Observer Dispatcher]]"
tags:
  - architecture-garden
  - sessionstream
  - formal-methods
  - tla+
  - alloy
  - coq
  - lean4
  - go
  - fuzzing
  - concurrency
  - model-checking
related_notes:
  - "[[Research/Software Architecture Garden/sessionstream/README|Architecture Garden — sessionstream]]"
  - "[[Research/Software Architecture Garden/sessionstream/designs/01 - Bounded Asynchronous Observer Dispatcher]]"
  - "[[PROJECT REPORT - Bounded Asynchronous Observer Dispatch - Contracts Lifecycle and Generic Go Design]]"
  - "[[PROJECT REPORT - Sessionstream Heartbeats - From Ping Pong Loops to a Timed Failure Detector]]"
  - "[[PROJECT REPORT - Proving WebSocket Heartbeat Arbitration - From Review Counterexample to Seeded Runtime Fuzzing]]"
  - "[[Research/Software Architecture Garden/sessionstream/designs/02 - Typed Transition Systems and Trace Algebra]]"
  - "[[Research/Software Architecture Garden/sessionstream/designs/03 - Effect-Acknowledged State Machines and Runtime Refinement]]"
  - "[[Research/Software Architecture Garden/sessionstream/designs/research/02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables]]"
---

# Proving the Bounded Asynchronous Observer Dispatcher

This study asks how much confidence formal methods and pragmatic runtime verification can buy for the [[Research/Software Architecture Garden/sessionstream/designs/01 - Bounded Asynchronous Observer Dispatcher|Bounded Asynchronous Observer Dispatcher]] design, and how that confidence can be attached to a real Go implementation. It builds and executes four formal artifacts and one executable verification scaffold:

1. a **TLA+** concurrent model checked with TLC, including a deliberately racy variant that must fail;
2. an **Alloy 6** temporal model checked headlessly with SAT4J, same contract, same racy variant;
3. a **Coq 8.20** mechanized proof of the invariant bundle over the abstract transition kernel;
4. a **Lean 4** mechanized proof of the same kernel, for proof-engineering comparison;
5. a **Go scaffold** (`specs/go/`) containing the reference dispatcher with linearization-point instrumentation, an executable oracle transliterated from the proved kernel, deterministic and turnstile tests, a state-aware native fuzzer, and mutation experiments.

> [!summary]
> - The dispatcher's contract (D1–D10) decomposes cleanly into a **sequential transition kernel**, a **concurrency protocol** (mutex + channel + WaitGroup), and a **runtime adapter** (the actual Go code). Each layer takes a different proof tool.
> - **Coq and Lean 4 prove the kernel invariants for arbitrary capacity, item type, and run length**: queue bound, `admitted = offered ++ queue`, close-once, no queue growth after close, drain completeness, wait-after-exit, dropped monotonicity. Both developments compile and are axiom-audited (Coq: closed under global context; Lean: `propext, Quot.sound` only).
> - **TLA+ checks the concurrency protocol exhaustively** over a bounded model: 118,771 distinct states, all invariants plus termination and close-stickiness hold. Removing the closing guard produces a depth-7 send-after-close counterexample — the exact race the mutex protocol exists to prevent.
> - **Alloy independently reproduces the race and surfaces a second violation TLC's first-error stop did not show**: without the closing guard, `DrainComplete` also breaks, because a submission can be accepted into a queue whose worker has already exited. Go's "send on closed channel" panic is, in effect, the runtime defending D8.
> - The **transposition to Go works**: 9 deterministic tests + a turnstile linearization test + 20 race repetitions + a 3.3M-execution fuzz campaign all replay execution traces through an oracle transliterated from the proved kernel, and all five targeted mutations are caught by named detectors.
> - What remains unproven is named explicitly: callback blocking (bounded queue ≠ bounded close), real-scheduler interference, item memory bounds, and adapter policies (cloning, context detachment).

## 1. The verification question

### 1.1 What is being proved

The design's behavioral contract:

```text
D1. Queue length never exceeds Capacity.
D2. Submit never waits for queue space or callback completion.
D3. Accepted values are delivered in admission order.
D4. Capacity rejection increments a monotone drop counter.
D5. One callback panic does not terminate later delivery.
D6. Close is idempotent and serializes against Submit.
D7. Submit after Close returns false without panic.
D8. Every accepted value is offered to the callback before worker exit.
D9. Wait returns only after the worker exits.
D10. One dispatcher has exactly one callback worker.
```

These clauses do not have equal epistemic status, and a verification plan that ignores the differences wastes effort:

| Clause | Kind | Where it can be proved |
|---|---|---|
| D1, D3, D4, D6, D7, D8, D9 | Safety invariants / transition guards | kernel (Coq/Lean) + protocol (TLA+/Alloy) + runtime replay |
| D2 | Structural nonblocking + deadlock freedom | code shape (select/default) + TLC deadlock check + tests |
| D5 | Safety (worker continuity) + liveness under fairness | kernel modeling + TLC liveness + fuzzer with panics |
| D10 | Structural | code review (one worker goroutine) + kernel assumption |

### 1.2 The three-layer decomposition

The heartbeat project reports ([[PROJECT REPORT - Sessionstream Heartbeats - From Ping Pong Loops to a Timed Failure Detector|heartbeats]], [[PROJECT REPORT - Proving WebSocket Heartbeat Arbitration - From Review Counterexample to Seeded Runtime Fuzzing|arbitration]]) established the pattern this study reuses:

```text
Layer 1: pure transition kernel    Step : State × Event -> State
         (no goroutines, channels, locks, or time)
Layer 2: concurrency protocol      mutex + channel + WaitGroup
         (why real executions are serializable into kernel steps)
Layer 3: runtime adapter           the actual Go code
         (why the binary's behavior refines the protocol)
```

The dispatcher is small enough that all three layers can be attacked directly. The kernel is a single inductive relation with eight constructors — small enough for fully mechanized proofs in two proof assistants. The protocol has four process roles (producers, closer, worker, waiter) — small enough for exhaustive model checking. The adapter is ~120 lines of Go — small enough for instrumentation, fuzzing, and mutation experiments.

The decomposition also tells you what each formalism is *for*:

- **Proof assistants (Coq, Lean)** answer: is the contract internally consistent and invariant under the kernel's own steps, for *arbitrary* parameters? This is where "proof" in the strong sense lives.
- **Model checkers (TLA+, Alloy)** answer: does the *concurrent* protocol — with real interleavings between producers, closer, and worker — preserve the invariants, and where exactly does it break when you remove a piece? This is where counterexamples live.
- **Runtime verification (oracle replay, fuzzing, mutation)** answers: does the Go binary produce executions the proved kernel allows? This is where the formal work becomes *engineering confidence*.

### 1.3 The kernel, stated once

All four formal artifacts and the Go oracle share one transition relation. A state is:

```text
queue       bounded FIFO of admitted items
admitted    history: accepted items in admission order
offered     history: items whose callback was invoked, in order
current     0-or-1 in-flight item being offered      (TLA+/oracle only)
dropped     overflow drop counter
closing     admission-closed flag (sticky)
closeCount  effective closes so far
workerDone  worker exited
waited      Wait returned
```

Steps (guards in brackets):

```text
submitAccepted(x)  [¬closing ∧ |queue| < cap]  queue += x; admitted += x
submitDropped(x)   [¬closing ∧ |queue| = cap]  dropped += 1
submitRejected(x)  [closing]                   no state change
closeFirst         [¬closing]                  closing := true; closeCount += 1
closeAgain         [closing]                   no state change
deliver            [queue = x ∷ rest]          queue := rest; offered += x
workerExit         [closing ∧ queue = []]      workerDone := true
waitReturn         [workerDone]                waited := true
```

The Alloy model fuses receive-and-offer into one atomic `deliver` step, so it has no `current`; the TLA+ model and the Go oracle split them, so the shape invariant reads `admitted = offered ++ current ++ queue`.

## 2. TLA+: the concurrency protocol, exhaustively

Artifact: `specs/tla/Dispatcher.tla`, configs `DispatcherGuarded.cfg` / `DispatcherUnguarded.cfg`, results in `specs/tla/results/`.

### 2.1 Modeling decisions

The model makes the protocol's mechanisms explicit rather than assuming them:

- **The mutex is a variable** (`lockOwner`), not an assumption. Submit acquire → body → release and close acquire → body → release are separate actions, so the submit/close race is *checked*, not stipulated away. The critical-section decision itself (closing check + nonblocking send) is one atomic action, because the Go mutex makes it atomic with respect to `Close` — and Section 7 shows that atomicity claim being tested in Go.
- **Panic is nondeterministic per offer** (`WorkerDeliverOK` / `WorkerDeliverPanic`). Both append to `offered` (D8's "offered" means *invoked*); only one increments `panics`. D5 becomes: the worker always returns to receive.
- **Blocked callback = unfair worker**. The `Termination` property holds only under weak fairness of the worker. This is the honest formalization of "bounded queue does not imply bounded close latency": TLC proves termination *given that callbacks return*, and the spec comments say so.
- **Bounded behaviors**: 2 producers × 3 submits, capacity 2, closer calls Close twice (exercising idempotence). The model is finite, so TLC is exhaustive — not sampling.
- **Error counters instead of wishful invariants**: `sendsAfterClose` and `closeCount` are history variables; the invariants `NoSendAfterClose` (D7) and `CloseOnce` (D6) assert they stay at 0 / ≤ 1.
- The strengthening invariant `QueueMatches` — `admitted = offered ++ current ++ queue` — does the heavy lifting for D3 and D8, and is the same shape clause proved in Coq/Lean.

### 2.2 Results, guarded model

```text
256,959 states generated, 118,771 distinct states, depth 39, ~25 s
Invariants: TypeOK, QueueBound, Accounting, NoSendAfterClose, CloseOnce,
            OrderOK, QueueMatches, DrainOK, WaitOK, PanicsBounded,
            WorkerHasItem — all hold
Properties: Termination (<>AllDone) and ClosingSticky ([](closing => []closing))
            — both hold under WF(Next)
```

`Accounting` deserves a note: `Len(admitted) + dropped + rejected = attempts` — every submit attempt is partitioned into exactly one outcome. It is the kind of invariant that catches misplaced counter increments, and its Go counterpart (M3 in the mutation matrix) is indeed caught.

### 2.3 Results, unguarded model (the sensitivity experiment)

`Guarded = FALSE` removes the closing check before the send — the mutation whose Go twin is M1. TLC reports at depth 7:

```text
State 2: CloseAcquire          lockOwner = "closer"
State 3: CloseBody             closing = TRUE, closeCount = 1
State 4: CloseRelease          lockOwner = "none"
State 5: SubmitAcquire(p2)     lockOwner = p2
State 6: SubmitBody(p2)        queue = <<<p2,1>>>, sendsAfterClose = 1   ← D7 broken
```

In Go this execution is `close(d.queue)` followed by `d.queue <- item` — `panic: send on closed channel`. The counterexample is the point of the experiment: a model that cannot exhibit the defect it guards against proves nothing. Compare the heartbeat report's pre-fix fuzz-seed sensitivity run; here the sensitivity run is built into the spec as a config flag.

### 2.4 What TLC did not check

- Capacities, producer counts, and submit counts beyond the small constants. (Kernel properties that must hold for *all* capacities are the Coq/Lean job.)
- Real Go scheduling, GC pauses, or channel internals. (Runtime replay's job.)
- Whether the model matches the code. (Section 7's bridge + Section 8's replay.)

### 2.5 Two modeling lessons recorded for reuse

1. **The in-flight item is easy to forget.** The first transcription of `QueueMatches` omitted `current` (`admitted = offered ++ queue`) and TLC immediately produced a counterexample — the worker had dequeued an item and not yet offered it. The design doc's "retained work ≤ N queued + 1 active" remark exists precisely because this off-by-one-in-time is the natural mistake. The same shape clause, with `current`, then checked clean and was reused in the Coq/Lean/Go-oracle models.
2. **TLC equality is not a total function.** Comparing the sentinel string `"none"` with an item tuple is a TLC *runtime error*, not `FALSE`. The fix is a type-compatible sentinel (`current = <<>>`). Any reusable TLA+ style guide for this codebase should say: pick sentinels in the same value domain as the variable's real contents.

## 3. Alloy: the relational view, and a second violation

Artifact: `specs/alloy/dispatcher_guarded.als` / `dispatcher_unguarded.als`, runner `RunAlloy.java` + `run_all.sh`, results in `specs/alloy/results/`.

### 3.1 Why a second model checker

Alloy's value here is different from TLC's. The model is declarative — sequences and temporal logic over mutable relations, no explicit process control — so it serves as an *independent transcription* of the same contract. A specification bug shared by both transcriptions is much less likely than one in a single transcription. Alloy also produces free visualizable traces and makes "find me a full lifecycle" a one-line `run` command.

Delivery is atomic in this model (`deliverOk`/`deliverPanic` move the head of `queue` to `offered` in one step), so the shape assertion is `admitted = append[offered, queue]` with no in-flight item.

### 3.2 Results

Scope: 4 `Item`, 6-length sequences, 10 steps, SAT4J (parallel per-command runs; timings recorded in `results/`).

Guarded model — all eight assertions hold within scope:

```text
QueueBound, NoEnqueueAfterClose, OfferedIsPrefix, QueueIsSuffix,
DrainComplete, WaitAfterExit, ClosedSticky, DropsMonotone
run ExampleLifecycle: SAT (full lifecycle witness with drops, panics,
post-close rejections, close, drain, exit, wait — needs 14 steps)
```

Unguarded model:

```text
check NoEnqueueAfterClose   COUNTEREXAMPLE   (the race, as with TLC)
check DrainComplete         COUNTEREXAMPLE   ← the interesting one
check QueueBound, OfferedIsPrefix, QueueIsSuffix, WaitAfterExit,
  ClosedSticky, DropsMonotone: no counterexample within scope
```

### 3.3 The DrainComplete insight

The unguarded `DrainComplete` counterexample is a genuinely useful find, and TLC did not show it (TLC stops at the first violated invariant, `NoSendAfterClose`). The trace:

```text
close → (queue drains) → workerExit → submitAccepted
```

Without the closing guard, a submission can be accepted *after the worker has exited*: the queue is momentarily empty and below capacity, the send succeeds, and the item now sits in a queue no worker will ever drain. `offered ≠ admitted` at exit — **D8 breaks, not just D7**. The closing check is therefore not only protecting the channel from a panicking send; it is protecting the *drain guarantee* from late admissions. In Go, the "send on closed channel" panic is effectively the runtime defending D8 on behalf of the missing guard.

This is a general lesson for the design doc's contract table: D7 and D8 are not independent. Any weakened variant of the design that relaxes admission closure must re-examine drain completeness, not just send safety.

### 3.4 Alloy's limits observed

- Temporal checks over history sequences are expensive: `QueueIsSuffix` took ~440 s at scope 6-seq/10-steps while `ClosedSticky` took ~8 s. Nested temporal operators (`always (… implies always …)`) had to be rewritten as one-step stickiness to stay tractable. Alloy here is a counterexample hunter and spec debugger, not a high-throughput prover.
- Bounded steps mean liveness properties are only checked within trace length — fine for this contract, whose liveness content is small (Section 2.2 covers it in TLA+).

## 4. Coq: the kernel, proved for all parameters

Artifact: `specs/coq/Dispatcher.v` (compiles with Coq 8.20.1, zero warnings), build log `specs/coq/results/build.txt`.

### 4.1 What mechanized proof buys over model checking

TLC verified the protocol for capacity 2, 2 producers, 3 submits each. The Coq development proves the kernel invariants for **arbitrary capacity, arbitrary item type, and runs of unbounded length** — there is no state-space bound anywhere in the file. This is the difference between "checked exhaustively at small scale" and "proved".

The proof is a single induction over reachability against a six-clause invariant bundle:

```coq
Record inv (s : state) : Prop := {
  inv_bound      : length (queue s) <= cap;                       (* D1 *)
  inv_shape      : offered s ++ queue s = admitted s;             (* D3/D8 *)
  inv_close_once : close_count s <= 1;                            (* D6 *)
  inv_closed_iff : closing s = true <-> close_count s = 1;
  inv_exit       : worker_done s = true -> closing s = true /\ queue s = [];
  inv_wait       : waited s = true -> worker_done s = true        (* D9 *)
}.
```

The load-bearing clause is `inv_shape`. It is stronger than any single contract clause — and that strength is exactly what makes the induction go through: `submitAccepted` appends to both sides, `deliver` moves the head of `queue` to the tail of `offered`, and every other step leaves the factorization untouched. D3 (`offered` is a prefix of `admitted`) and D8 (at exit, `queue = []`, so `offered = admitted`) are one-line corollaries.

Transition-level lemmas then cover the properties that are about *pairs* of states rather than single states:

```coq
step_dropped_mono      : step s t -> dropped s <= dropped t          (* I8 *)
step_closing_sticky    : step s t -> closing s = true -> closing t = true
step_closed_shrinks    : step s t -> closing s = true ->             (* D7/I5 *)
                         length (queue t) <= length (queue s)
```

lifted to `steps` (reflexive-transitive closure) and exported as `no_send_after_close` and `dropped_monotone_reachable`.

### 4.2 Exported theorems and audit

```text
queue_bound                  admitted_factors / offered_prefix
close_once                   no_send_after_close
drain_complete               wait_after_exit
dropped_monotone_reachable
```

Every theorem closes with `Print Assumptions` reporting **"Closed under the global context"** — no axioms, no admits, no classical assumptions. The proof is fully constructive; it lives in the Coq kernel's computational fragment.

### 4.3 What the Coq proof does *not* cover

The `Step` relation is sequential by construction. Nothing in the Coq file knows about goroutines, mutexes, or channels. The claim that real executions refine this kernel is a *separate* argument — the TLA+ protocol model (mutex-serialized decisions) plus the Section 7 bridge. This separation is deliberate and matches the heartbeat reports: pure semantics in the proof assistant, concurrency in the model checker, binary behavior in runtime verification.

## 5. Lean 4: the same kernel, second proof engine

Artifact: `specs/lean/Dispatcher.lean` (compiles with Lean 4.33.0, zero errors/warnings), build log `specs/lean/results/build.txt`.

The development is deliberately parallel to the Coq one — same `State`, same eight-step `Step`, same `Inv` bundle, same final theorems — so that the two serve as mutual transcription checks and as a honest comparison of proof engineering cost:

| Aspect | Coq 8.20 | Lean 4.33 |
|---|---|---|
| Step relation | `Inductive step : state -> state -> Prop` | `inductive Step (cap : Nat) : State Item → State Item → Prop` |
| Invariant bundle | `Record inv : Prop` | `structure Inv : Prop` |
| Main induction | `induction reachable` over 8 cases | `induction Reachable`, `step_preserves` lemma over 8 cases |
| List lemmas | `app_length`/`length_app`, `app_assoc`, `app_nil_r` | `List.length_append`, `List.append_assoc` |
| Axiom audit | `Print Assumptions` → closed under global context | `#print axioms` → `[propext, Quot.sound]` for every theorem |
| Lines (approx.) | 310 | 300 |

Lean's `[propext, Quot.sound]` are the two standard definitional axioms pulled in by `simp` on propositions and quotients; notably absent are `Classical.choice` and `sorryAx`. Both developments are axiom-clean by their own ecosystem's standards.

Proof-engineering differences that actually bit, recorded for future Lean/Coq work in this codebase:

1. **Induction-hypothesis placement in intro patterns.** Coq inserts the IH immediately after the recursive constructor argument (`[| s t Hr IH Hst]`), Lean appends IHs at the end of the named hypotheses. Getting this wrong binds the IH to the step proof and produces "expects a disjunctive pattern with 8 branches" (Coq) or silently wrong names.
2. **`cases` on indexed families in Lean unifies indices with existing context variables.** Constructor arguments that coincide with an index are *not* re-introduced — the alternative expects 3 names, not 4 (`submitAccepted x hclosing hcap`, not `submitAccepted s x hclosing hcap`). The state remains the outer variable, and goals mention the outer `s` directly.
3. **Structure-update projections reduce definitionally but not syntactically.** Goals like `{ s with queue := … }.queue.length ≤ cap` need `show (s.queue ++ [x]).length ≤ cap` (defeq restatement) before rewriting; `simp` reduces such projections automatically, `rw` does not.
4. **Tactic fragility of `destruct` on `<=`.** Destructing a `le` hypothesis in Coq does not produce usable equalities for non-variable indices; asserting `close_count ≠ 1` and letting `lia` finish is both shorter and more robust.

## 6. What each lens saw — and could not see

| | TLA+ / TLC | Alloy / SAT4J | Coq 8.20 | Lean 4.33 |
|---|---|---|---|---|
| Abstraction | concurrent protocol (processes, mutex, channel) | relational temporal spec | sequential kernel | sequential kernel |
| Parameter bounds | cap 2, 2 producers, 3 submits | 4 items, 6-seq, 10 steps | arbitrary | arbitrary |
| Verdict form | exhaustive check + counterexample traces | counterexample/witness traces | machine-checked proof, axiom audit | machine-checked proof, axiom audit |
| Send-after-close race | depth-7 counterexample | counterexample | excluded by step guards (lemma) | excluded by step guards (lemma) |
| Post-exit drain break (D8) | not shown (first-error stop) | **counterexample** | excluded (`no_send_after_close` corollary) | excluded (same) |
| Liveness (termination under fairness) | **proved** (`WF`, `<>AllDone`) | bounded traces only | not modeled | not modeled |
| Blocked callback | modeled as unfair worker | not modeled | not modeled | not modeled |
| Nonblocking submit (D2) | structural + deadlock-free check | structural | N/A (kernel has no waiting) | N/A |
| Concurrency fidelity | mutex explicit | decision-level | none (assumes serializability) | none |
| Effort (this study) | ~250 lines spec, 2 debug iterations | ~260 lines, 3 iterations | ~310 lines, 4 iterations | ~300 lines, 4 iterations |

The four lenses overlap enough to catch each other's transcription bugs (my initial `QueueMatches` omission was caught by TLC before it reached the proof assistants), and each has one question it answers best. Nobody but TLC answered "does the protocol terminate"; nobody but Alloy volunteered the post-exit drain counterexample; nobody but Coq/Lean says "for every capacity and every run"; nobody but the Go scaffold (next sections) says anything about the binary.

## 7. The correspondence argument: why Go executions refine the kernel

This is the bridge that makes Sections 4–5 mean something about the Go binary. It is stated once here and then *executed* in Section 8.

**Claim.** Every execution of the instrumented dispatcher produces, at its linearization points, a sequence of events that is a legal path of the abstract kernel (Section 1.3).

This bridge is the dispatcher instance of the runtime-refinement pattern generalized in [[Research/Software Architecture Garden/sessionstream/designs/03 - Effect-Acknowledged State Machines and Runtime Refinement|design 03]]: identify concrete linearization points, define the abstraction map from Go runtime state to abstract state, and require trace inclusion — every concrete execution's event trace must be permitted by the specification. The queue-transducer view of the dispatcher in [[Research/Software Architecture Garden/sessionstream/designs/02 - Typed Transition Systems and Trace Algebra|design 02]] supplies the matching algebraic reading: the kernel relation is the transducer's transition function, and `admitted`/`offered` are its input and output words.

**Linearization-point table.** The mapping is by construction, one Go statement to one kernel step:

| Go statement (holding `d.mu`) | Kernel step | Event emitted |
|---|---|---|
| `if d.closing { return false }` (taken) | `submitRejected` | `submit_rejected` |
| `case d.queue <- item:` succeeds | `submitAccepted` | `submit_accepted` |
| `default:` taken, `d.dropped++` | `submitDropped` | `submit_dropped` |
| `d.closing = true; close(d.queue)` | `closeFirst` | `close_effective` |
| repeated `Close` (flag already set) | `closeAgain` | `close_noop` |
| worker pop (two-phase loop, under `d.mu`) | `deliver` (part 1: dequeue) | `receive` |
| callback returns | `deliver` (part 2: offer) | `offered` |
| callback panics, recovered | `deliver` + panic count | `panic_recovered` |
| closed-and-drained observed in worker | `workerExit` | `worker_exit` |
| `wg.Wait()` returns | `waitReturn` | `wait_returned` |

**Why the serialization is sound.**

1. Every event is emitted **under `d.mu` at the statement that linearizes the step**. Submit and close decisions happen inside the critical section; the worker pops and emits under the same mutex; `Wait` emits after `wg.Wait()`.
2. Because all emissions hold `d.mu`, mutex-acquisition order = log order. And because each emit happens at (not after) its step's linearization point, no event can be logged before the step it records actually linearized. The log is therefore a true serialization of the execution's linearization points.
3. The worker's callback itself runs **outside** `d.mu` (only its receive/offer emissions take the mutex), preserving D2: producers never wait for callback completion.
4. The channel never needs a separate close-abort protocol: `close(d.queue)` inside the critical section both stops future sends (via the `closing` check — D6/D7, proved) and tells the worker to drain (D8, proved).

**The one place this argument broke during the study** is recorded in Section 8.2: the naive instrumented worker (`for item := range d.queue` + emit after pop) violates premise 1 — a pop can interpose between a producer's send and its emit, and the log then orders events in a way the kernel cannot replay. The fix (two-phase pop under `d.mu`) restores the premise. Instrumentation that claims to record a linearization must itself respect the linearization it records.

## 8. Pragmatic transposition: turning the formal work into Go confidence

Artifact: `specs/go/` — a self-contained module (`module dispatchlab`, stdlib only) containing the reference dispatcher with the instrumentation seam, the executable oracle, all tests, the fuzzer, and the mutation harness.

### 8.1 The scaffold

The dispatcher in `specs/go/dispatcher.go` is the design doc's reference implementation with two clearly marked test-only seams (`log`, `preDecision`). Everything else — the API, the mutex protocol, the select/default admission, the per-callback recover, the WaitGroup — is verbatim the design. This is deliberate: the formal models specify the *reference implementation*, and the scaffold keeps the correspondence auditable line by line.

### 8.2 Instrumentation: the receive-lag race

The first instrumented worker was:

```go
for item := range d.queue {
    d.emitMu(evReceive, item, true)   // emit AFTER the pop, under d.mu
    d.deliverSafe(item)
}
```

The concurrent stress test immediately failed trace replay with:

```text
trace event 19 (submit_accepted value=7019): D1: submit accepted while queue full (8 >= 8)
```

Root cause: `for item := range` pops **without** `d.mu`. A worker pop can therefore interpose between a producer's channel send and its (mutex-held) `submit_accepted` emission. In the real execution the send succeeded *because* the pop freed a slot; in the log, the `receive` event appears only after the producer's event, and the model — which must apply steps in log order — sees an accept into a full queue. The log was not a linearization of anything.

Fix (documented in the code): a two-phase worker loop that pops **under** `d.mu`:

```go
for {
    d.mu.Lock()
    select {
    case item, ok := <-d.queue:
        if !ok { d.emitLocked(evWorkerExit, …); d.mu.Unlock(); return }
        d.emitLocked(evReceive, item, true); d.mu.Unlock(); d.deliverSafe(item)
    default:
        d.mu.Unlock()
        <-d.nonempty        // sleep WITHOUT the mutex; woken by sends and Close
    }
}
```

`d.nonempty` is a buffered size-1 signal posted by every accepted send and by `Close`. The loop is behaviorally equivalent to the range loop (greedy pop, drain-on-close, exit on closed-empty), but every pop linearizes atomically with its `receive` event. This is the instrumentation tax, and it is worth being explicit about it in the production playbook: *the elegant range loop does not expose its pop linearization point to an external observer; a trace-validated variant needs the two-phase form.*

### 8.3 The executable oracle

`specs/go/model.go` is a transliteration of the Coq/Lean kernel (and the TLA+ model's `current` item): `apply(event)` rejects any event that is not a legal step, then **cross-checks the event's recorded state evidence** — every event carries the queue length and drop counter read under `d.mu` — and re-validates the invariant bundle after every step. The oracle is therefore checking two things at once: that the *sequence of steps* is kernel-legal, and that the *implementation's own state* at each linearization point agrees with the kernel's.

Two disciplines make the oracle trustworthy:

1. **It is smaller than the implementation and structurally independent** — a switch over event kinds plus sequence equality, no channels, no locks (the arbitration report's oracle rule).
2. **It is self-checked**: `TestModelRejectsFabricatedTraces` feeds eight fabricated violations (accept-while-closing, accept-over-capacity, offer-without-receive, exit-with-undrained-items, wait-before-exit, drop-while-not-full, double-effective-close, queue-length-evidence-mismatch) and requires each to be rejected. An oracle that accepts everything is worse than no oracle.

### 8.4 Deterministic tests

The nine obligations from the design doc are implemented, each *additionally* replaying its trace through the oracle — every test validates the same execution twice, semantically and against the proved kernel:

| Test | Clause |
|---|---|
| `TestDeliveredInAdmissionOrder` | D3 |
| `TestFullQueueDropsAndCounts` (blocked callback; wait for `receive`; fill to cap; next submit drops) | D1, D4, "N+1 active" |
| `TestCloseDrainsAccepted` | D8 |
| `TestSubmitAfterCloseReturnsFalse` (and not counted as a drop) | D7 |
| `TestRepeatedCloseHarmless` | D6 |
| `TestPanicDoesNotStopDelivery` | D5 |
| `TestWaitBlocksWhileCallbackBlocked` (100 ms probe, then release) | D9 + unbounded-close caveat |
| `TestWaitReturnsAfterReleaseAndDrain` | D9, D8 |
| `TestFinalQueueSlotDelivered` | D1/D8 boundary |
| `TestConcurrentProducersAndClose` (8 producers × 400 submits, panics, double close, `-race`) | D3/D4/D6/D7/D8 under concurrency |
| `TestModelRejectsFabricatedTraces` | oracle sensitivity |

### 8.5 The turnstile linearization test

`TestSubmitCloseSerializeThroughMutex` forces one exact schedule deterministically, using the `preDecision` hook as a turnstile:

```text
P1 enters TrySubmit and blocks inside the critical section (hook)
C  calls Close()                          → must block on d.mu
assert Close has not proceeded (100 ms probe)
release P1 → its admission linearizes BEFORE the close
Close completes → next TrySubmit returns false
```

This converts the TLA+ atomicity *assumption* (Section 2.1: "the mutex makes the critical-section decision atomic") into a tested Go fact, and it is the direct Go-side counterpart of the TLC counterexample in Section 2.3 — same schedule, opposite outcome, because the guard exists. The technique is the heartbeat report's "scheduler as data": never assert a race outcome that the scheduler chose probabilistically when a turnstile can make the schedule deterministic (the only timing element is a generous 100 ms negative probe).

### 8.6 State-aware fuzzing

`FuzzDispatcherOps` follows the SESSIONSTREAM-005 fuzzer pattern: bytes encode operations, the kernel transliteration is the oracle.

```text
input: pairs of bytes (op, arg); op = b % 6
  0 TrySubmit(arg)      1 Close()        2 Wait checkpoint (kicks a Wait goroutine)
  3 arm/disarm panic-on-odd  4 block callbacks (gate)  5 release callbacks
final phase (always): release gate → Close → Wait with 10 s watchdog
oracles: (1) whole trace replays through the kernel
         (2) invoked == admitted  (D3 order + D8 drain + D5 panic continuity)
         (3) Dropped() == kernel dropped (D4)
         (4) kicked Wait returns after worker exit (D9)
```

Seven readable seeds anchor the corpus as regression tests (fill-then-close, blocked-callback overfill, panic stream, close-then-submit, double close, mixed lifecycle). Campaign result:

```text
seeds 7 → corpus 81 interesting inputs
3,307,183 executions in 45 s, PASS, no failure corpus
20× -race repetitions of the full suite: PASS
-race seed runs: PASS
```

One fuzz-authoring lesson is worth recording: seeds #3 and #6 initially "failed" because the harness asserted that the kicked Wait *goroutine* had already run at assertion time — an oracle bug asserting a scheduling fact, not an implementation bug. The corrected oracle waits for the kicked Wait with a timeout *after* the worker has provably exited. Oracle discipline: assert contract outcomes, not scheduler behavior.

### 8.7 Mutation experiments: does the harness have teeth?

`mutate.sh` applies five contract-breaking mutations to a scratch copy and requires the suite to fail. All five are caught, each by a named detector:

| Mutation | Broken clause | Formal counterpart | Detector that fired |
|---|---|---|---|
| M1 remove closing guard | D7 (and D8, §3.3) | TLA+ `NoSendAfterClose` cx; Alloy `NoEnqueueAfterClose`/`DrainComplete` cx; Coq/Lean `no_send_after_close` | `panic: send on closed channel` in `TestSubmitAfterCloseReturnsFalse` |
| M2 bypass `deliverSafe` | D5 | TLA+ `WorkerDeliverPanic` / `Termination` | `panic: boom` — worker death crashes the suite |
| M3 `dropped += 0` | D4 | TLA+ `Accounting`; Coq/Lean `dropped_monotone` | oracle evidence mismatch + fuzz oracle + `Dropped()` assertions |
| M4 skip `d.deliver` | D8 | Coq/Lean `drain_complete`; TLA+ `DrainOK`; Alloy `DrainComplete` | `invoked == admitted` fails across tests and fuzz seeds |
| M5 remove close idempotence | D6 | TLA+ `CloseOnce`; Coq/Lean `close_once` | `panic: close of closed channel` in `TestRepeatedCloseHarmless` |

Note the division of labor in the table: M1/M2/M5 are caught by Go's own runtime panics (the contract clauses exist to *avoid* panics); M3 is caught only by the oracle's state-evidence cross-check; M4 is caught only by the semantic `invoked == admitted` assertion, *not* by the mechanical trace replay (the fabricated `offered` events are kernel-legal — the kernel cannot know the callback never ran). No single detector covers all five; that is the argument for layering.

### 8.8 Post-trace inspection as a production pattern

The scaffold's trace-replay pattern lifts directly to production hardening:

1. **Debug-build event log.** Gate the event log behind a build tag (`//go:build dispatcher_debug`) or an env-var-checked nil field; nil log = zero overhead (one branch per emit site).
2. **Emit at linearization points only**, under the admission mutex, exactly as in Section 7. Keep the two-phase worker loop in the debug build (it is also correct in release; the range loop is simply cheaper to read).
3. **Offline replay.** Dump events as JSONL from soak tests, integration runs, or chaos runs; replay with a standalone checker binary sharing `model.go`'s logic. Any replay error is a contract violation with a precise event index — a much better bug report than "sometimes records go missing".
4. **Optional: TLC trace validation.** The same JSONL can be translated into TLC's trace format and checked against `Dispatcher.tla` itself (TLC's trace-checking mode: spec-generated state space + externally supplied behavior). That closes the loop "binary trace ∈ behaviors of the formal spec" rather than "∈ behaviors of a hand-ported Go oracle". Section 10 lists it as future work; the Go oracle is the pragmatic 90% because it ships in `go test`.

### 8.9 What remains unproven

Honest residuals, each with its owning test technique:

- **A callback can block forever.** Proved: nothing. Modeled: TLC liveness assumes a fair worker. The contract's own caveat ("bounded queue ≠ bounded close latency") stands; the owner-level answer remains context-bounded waiting at the `Server.Close` level, exactly as the design says.
- **The kernel says nothing about real memory.** D1 bounds *item count*, not bytes; deep item size (cloned protobufs, slices) is an adapter-level capacity-planning concern, per the design doc.
- **Real-scheduler interference** (GC pauses, `GOMAXPROCS` collapse, channel implementation details) is outside every model here. The mitigation is empirical: `-race` repetitions, stress, and post-trace inspection of long runs.
- **Adapter policies are separate contracts.** `context.WithoutCancel` detachment, deep cloning, and record mapping for the Sessionstream `TransportObserver` adapter need their own tests (and already have them in `server_test.go`); they are not part of the generic kernel.
- **One-worker structural claim (D10)** is code-shape, verified by review and by the model's single worker; it is not something any of these tools enforce on the binary.
- **The instrumentation seam itself** (Section 8.2) shows a trace-validated binary differs slightly from the prettiest production loop. If the production package adopts trace validation, adopt the two-phase loop in the debug build and keep a comment tying it to this study.

## 9. Recommended verification ladder for sessionstream

Status note (post-SESSIONSTREAM-006): Systemlab and the Bus/Pipeline/Error observers have been removed; `TransportObserver` remains because rag-ttc consumes subscribed-stage observations for reconnect metrics, and the generic dispatcher mechanism remains *unextracted* because there is still only one retained delivery use. The ladder below therefore applies in two stages: stage A today, against the embedded observer machinery in `ws.Server`; stage B if and when a second retained consumer justifies the generic `internal/asyncdispatch` package the design doc defers.

If and when that extraction happens, the ladder that falls out of this study is:

1. **Package layout.** `dispatcher.go` (reference implementation as in the design), `events.go` + `model.go` copied from the scaffold (they are transport-agnostic), tests as in Section 8.4–8.6, `mutate.sh` adapted to package paths. Do not export the event log in the public API; keep `NewChecked`/trace replay test-only or behind `dispatcher_debug`.
2. **CI wiring.** `go test -race -count=10 ./internal/asyncdispatch/...` per push; a fuzz campaign job (`-fuzztime=60s`) on merge to main; `mutate.sh` as a nightly or pre-release job, not a blocker (it is slow by design).
3. **Apply the same replay to the *current embedded* observer** (`ws.Server` observer path): the adapter can emit the same event kinds (it already has `observerMu` serializing decisions), and `server_test.go` can replay after observer-heavy tests. This buys contract confidence for the code that exists *today*, before any extraction decision.
4. **Keep the specs next to the code they verify.** The TLA+/Alloy/Coq/Lean files in `specs/` are written to be re-runnable; if the dispatcher contract ever changes (e.g., an abort-without-drain mode), the change must show up as a diff in *both* the kernel relation and the Go code, with the invariant bundle re-proved. The four files share one `Step` relation by design — a contract change that touches only one of them is a red flag.
5. **Do not weaken the oracle when extending.** Richer metrics (accepted/delivered/panic counters, high-water mark) should extend the event record and the model together, with new fabricated-violation cases in the oracle self-test.

## 10. Decision records

### DR-1: Prove the kernel twice (Coq + Lean), model the protocol once (TLA+), hunt with Alloy

- **Context:** Four candidate tools, limited study budget.
- **Options:** TLA+ only; proof assistant only; all four; any two.
- **Decision:** TLA+ for the concurrent protocol (exhaustive at small scope, best counterexample traces, liveness under fairness); Coq as the primary mechanized proof (theorems for arbitrary parameters, axiom-free audit); Lean 4 as the parallel proof (transcription check + ecosystem comparison); Alloy as the independent relational spec (found the post-exit drain violation TLC's first-error stop hid).
- **Consequences:** Four artifacts share one `Step` relation by construction; each caught at least one issue the others missed or would have shown later. Cost: four transcriptions to maintain — mitigated by keeping them small and adjacent (`specs/`).
- **Status:** accepted.

### DR-2: Instrumentation at linearization points under the admission mutex; two-phase worker loop in checked builds

- **Context:** Trace replay requires the log to be a true serialization of linearization points; the naive range-loop worker broke that (Section 8.2).
- **Decision:** Emit every event under `d.mu` at its step's linearization point; in checked builds, use the two-phase pop-under-mutex worker loop with a coalesced `nonempty` signal.
- **Consequences:** Traces replay strictly against the kernel; the production range loop and the checked loop differ by a documented, semantics-preserving transformation; debug-build instrumentation is nil-gated for zero release overhead.
- **Status:** accepted (scaffold); proposed for the production package.

### DR-3: Oracle = transliterated kernel + state-evidence cross-check + oracle self-test

- **Context:** A fuzzer/trace-checker is only as good as its oracle; a hand-rolled second implementation risks correlated bugs (arbitration report's oracle rule).
- **Decision:** The oracle is a minimal switch transliterating the proved `Step` relation; it additionally cross-checks per-event queue-length and drop-counter evidence recorded under `d.mu`; `TestModelRejectsFabricatedTraces` must reject eight fabricated violations.
- **Consequences:** M3 (drop accounting) is caught *only* by the evidence cross-check — kept deliberately; the self-test makes oracle vacuity a test failure.
- **Status:** accepted.

### DR-4: Mutation testing as the sensitivity gate

- **Context:** Green tests do not prove the harness detects violations (cf. the arbitration report's pre-fix sensitivity run).
- **Decision:** Five contract-targeted mutations (M1–M5) must each fail the suite, each mapped to a formal counterpart; `mutate.sh` restores the tree and records results.
- **Consequences:** The sensitivity matrix (Section 8.7) is reproducible; new contract clauses require new mutations.
- **Status:** accepted.

### DR-5: TLC trace validation of Go logs — future work

- **Context:** The Go oracle hand-ports the kernel; validating JSONL traces directly against `Dispatcher.tla` (TLC trace checking) removes the port.
- **Decision:** Document the recipe, do not build it yet — the Go oracle plus self-test covers the pragmatic need inside `go test`.
- **Status:** proposed.

## 11. Lessons from the exercise

1. **The in-flight item is the natural off-by-one-in-time.** My first `QueueMatches` (`admitted = offered ++ queue`) was wrong the moment the worker held an item; TLC's counterexample taught the correct shape in seconds. The design's "N queued + 1 active" phrasing now has a formal counterpart.
2. **Model-checker equality is typed by usage.** TLC errors on `"none" = <<p,1>>` instead of returning false; sentinels must live in the same value domain as real contents.
3. **First-error stop hides second violations.** TLC reported the send-after-close race and stopped; Alloy's per-assertion checks additionally surfaced the post-exit drain break. Run independent assertions independently.
4. **D7 and D8 are not independent.** Losing the admission guard does not just allow a panicking send; it allows admission into a queue whose worker is gone — the drain guarantee dies with it. Contract tables should record this coupling.
5. **Instrumentation must respect the linearization it records.** The receive-lag race (Section 8.2) was an instrumentation bug with the same shape as the production bugs being hunted: an event logged *after* the step it names. Emit at the step, under the lock, or do not replay.
6. **Oracle bugs masquerade as implementation bugs.** The fuzz "D9 violation" was the harness asserting goroutine scheduling. Assert contract outcomes; give scheduler-dependent observations timeouts and provable preconditions.
7. **Proof-assistant friction is real but bounded.** Coq's IH placement in intro patterns, Lean's index unification in `cases`, and structure-update `show`-restatements each cost an iteration; the resulting files are short, stable, and axiom-audited. For transition kernels of this size, mechanized proof is cheap *after* the model checkers have debugged the spec.
8. **Model check first, prove second.** Every bug found in this study was found by TLC or Alloy or `go test` before a proof assistant saw it. The proof assistants' role was to make the *final* spec parameter-free — they are the wrong tool for spec debugging and the right tool for spec sealing.

## 12. Artifacts and reproduction

All under `Research/Software Architecture Garden/sessionstream/designs/research/specs/` (commands in `specs/README.md`):

| Path | Content | Headline result |
|---|---|---|
| `tla/Dispatcher.tla`, `*.cfg`, `results/` | concurrent model, guarded + racy variants | 118,771 states, all invariants + termination; depth-7 race cx |
| `alloy/*.als`, `RunAlloy.java`, `run_all.sh`, `results/` | temporal relational model | guarded: 8/8 hold + lifecycle witness; unguarded: 2 counterexamples |
| `coq/Dispatcher.v`, `results/build.txt` | mechanized kernel proof | 7 theorems, closed under global context |
| `lean/Dispatcher.lean`, `results/build.txt` | same, Lean 4 | 7 theorems, `[propext, Quot.sound]` only |
| `go/` (`dispatcher.go`, `events.go`, `model.go`, tests, `mutate.sh`), `results/` | executable scaffold | suite + 20× race + 3.3M-exec fuzz PASS; M1–M5 all caught |

Environment used: TLC 2.19 (`tla2tools.jar`), Alloy 6 dist (`org.alloytools.alloy.dist.jar`, SAT4J), Coq Platform 8.20.1 (`CP.2025.08.0~8.20~2025.01`), Lean 4.33.0 (elan), Go 1.26.5, OpenJDK 21.

## Related notes

- [[Research/Software Architecture Garden/sessionstream/designs/01 - Bounded Asynchronous Observer Dispatcher|The design this study verifies]]
- [[PROJECT REPORT - Bounded Asynchronous Observer Dispatch - Contracts Lifecycle and Generic Go Design|The contract report]]
- [[PROJECT REPORT - Sessionstream Heartbeats - From Ping Pong Loops to a Timed Failure Detector|The three-layer verification pattern this reuses]]
- [[PROJECT REPORT - Proving WebSocket Heartbeat Arbitration - From Review Counterexample to Seeded Runtime Fuzzing|Oracle discipline, sensitivity runs, and seeded runtime fuzzing]]
- [[Research/Software Architecture Garden/sessionstream/designs/02 - Typed Transition Systems and Trace Algebra|Dispatchers as queue transducers — the algebraic framing]]
- [[Research/Software Architecture Garden/sessionstream/designs/03 - Effect-Acknowledged State Machines and Runtime Refinement|The general runtime-refinement pattern this study instantiates]]
- [[Research/Software Architecture Garden/sessionstream/README|Architecture Garden — sessionstream]]
