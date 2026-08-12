# Verification artifacts for the Bounded Asynchronous Observer Dispatcher

Companion to
[[Research/Software Architecture Garden/sessionstream/designs/research/01 - Proving the Bounded Asynchronous Observer Dispatcher|01 - Proving the Bounded Asynchronous Observer Dispatcher]].

All artifacts are self-contained and reproducible with the commands below
(expected tool versions in parentheses).

## tla/ — TLA+ concurrent model (TLC 2.19)

```
cd tla
java -jar ~/Downloads/tla2tools.jar -config DispatcherGuarded.cfg   -workers 4 -cleanup Dispatcher.tla
java -jar ~/Downloads/tla2tools.jar -config DispatcherUnguarded.cfg -workers 4 -cleanup Dispatcher.tla
```

- Guarded: all 12 invariants + `Termination` + `ClosingSticky` hold
  (118,771 distinct states, depth 39, ~25 s).
- Unguarded (`Guarded = FALSE`): TLC reports a `NoSendAfterClose`
  counterexample at depth 7 (close, then submit sends on the closed queue).
- Captured output: `results/guarded.txt`, `results/unguarded.txt`.

## alloy/ — Alloy 6 temporal model (org.alloytools dist, SAT4J)

```
cd alloy
javac -cp ~/Downloads/org.alloytools.alloy.dist.jar RunAlloy.java
./run_all.sh        # parallel per-command runs, writes results/
```

- Guarded: 8 assertions hold within scope (4 Item, 1 Flag, 6 seq, 10 steps);
  `ExampleLifecycle` produces a witness at 14 steps.
- Unguarded (no closing guard): `NoEnqueueAfterClose` AND `DrainComplete`
  counterexamples — post-exit submissions land in a queue nobody drains.
- `RunAlloy.java` is a minimal headless command runner
  (`java -cp .:alloy.jar RunAlloy <file.als> [labelPrefix]`).

## coq/ — Coq 8.20 mechanized proofs (Coq Platform CP.2025.08.0~8.20)

```
cd coq
eval $(opam env --switch CP.2025.08.0~8.20~2025.01)
coqc Dispatcher.v
```

All seven exported theorems print `Closed under the global context`
(axiom-free). Log: `results/build.txt`.

## lean/ — Lean 4 (4.33.0) mechanized proofs

```
cd lean
~/.elan/bin/lean Dispatcher.lean
```

All seven theorems report axioms `[propext, Quot.sound]` only (no
`Classical.choice`, no `sorryAx`). Log: `results/build.txt`.

## go/ — executable scaffold: dispatcher, oracle, tests, fuzzer, mutations

```
cd go
go vet ./...
go test ./... -count=1                              # deterministic + stress + turnstile
go test -race -count=20 -timeout 300s ./...         # race repetitions
go test -race -run FuzzDispatcherOps -count=1 .     # fuzz seeds under -race
go test -fuzz=FuzzDispatcherOps -fuzztime=45s .     # campaign (3.3M execs PASS)
./mutate.sh                                         # 5 mutations, all caught
```

Results: `results/fuzz_campaign.txt`, `results/mutations.txt`.

## gobra/ — deterministic dispatcher-kernel verification (Gobra v26.02)

```bash
cd gobra
PATH="$HOME/.local/bin:$PATH" gobra -i DispatcherKernel.gobra
```

`DispatcherKernel.gobra` proves queue boundedness, capacity stability,
monotone drop accounting, sticky close, exact accept/drop/reject state changes,
and abstract idempotence of Close. Gobra reports zero errors. A sensitivity
mutation changing accepted admission from `queueLen + 1` to `queueLen + 2` is
rejected with `Postcondition might not hold`.

`DispatcherShellPrimitives.gobra` then verifies two production-relevant
permission mechanisms independently: `sync.Mutex` invariant ownership of
lifecycle state, and exclusive item ownership transfer through a buffered
channel. Removing the lock before invariant unfolding is rejected (`Unfold
might fail`); accessing an item after sending away its permission is rejected
(`Assignment might fail`). The remaining step is to combine these mechanisms
with nonblocking `select/default`, closure debt, goroutine termination, panic
recovery, and Wait. Toolchain, claims, mutations, and scope are recorded in
`gobra/results/build.txt`.

A production-shaped combined proof is currently blocked by Gobra v26.02
frontend limitations, captured reproducibly by `gobra/probe_unsupported.sh`:

- `probes/SelectDefault.gobra` reaches Gobra desugaring and crashes with
  `scala.NotImplementedError`; the source contains an explicit select-support
  TODO.
- `probes/Recover.gobra` is rejected with `unknown identifier recover`.

These are hard blockers for proving the actual guarded `select/default`
admission and panic-isolated callback shell. The probe runner is expected to
pass only while both limitations remain; a future tool upgrade that supports
either construct makes the runner fail so this decision is revisited.

## spin/ — Promela channel/lifecycle protocol model (SPIN 6.5.2)

```bash
cd spin
./run_all.sh
```

The guarded model serializes Submit and Close with a mutex token, bounds the
queue, rejects post-close submissions, drains admitted items, and requires
worker exit only after close + empty queue. Exhaustive verification stores
16,865 states, explores 40,687 transitions to depth 73, and reports zero
errors.

The unguarded mutation omits the closing check. SPIN finds a depth-27
`sendsAfterClose == 0` assertion violation in which the worker has already
exited and a producer then enqueues an item. `results/unguarded-trail.txt`
contains the replayed trail.

Sharp edge: generated `pan` returned process status 0 even after reporting an
assertion violation. `run_all.sh` therefore parses the authoritative
`errors:` count and fails if it differs from the expected verdict.

## tracelink/ — actual Go JSONL trace constrained through TLC

```bash
cd tracelink
./run_all.sh
```

The Go scaffold's `cmd/tracegen` runs a deterministic comprehensive lifecycle
and emits both a versioned 15-event model JSONL trace and an
invocation/linearization/return interval stream. Every event carries a stable
run ID and dispatcher ID; model and interval events are joined by operation ID.
The lifecycle covers accept, receive, full-queue
drop, effective/no-op close, post-close rejection, callback return/panic,
worker exit, and Wait return. `generate_trace.py` validates schema/sequence
metadata and generates a root TLA+ module that instantiates
`DispatcherTraceValidator.tla` with the observations, item domain, and
capacity.

The strict trace produces 16 distinct states to depth 16 with no error.
`project_partial.py` then removes every queue/drop observation and replaces
exact worker actions with the `worker` abstraction class. TLC reconstructs
receive-versus-offer choices, explores 31 generated transitions, and still
finds the 16-state legal behavior. A post-close `submit_accepted` mutation is
rejected at event two with a deadlock because no abstract transition admits
it. A second negative fixture models delayed receive instrumentation at
capacity one: the worker frees a slot but does not log `receive` before a
second accepted submit. TLC rejects the claimed order because the abstract
queue is still full. `run_all.sh` requires both positive and both negative
verdicts.

`mutate_tracegen.sh` applies source mutations M1–M5 and requires each mutated
executable to fail before producing a valid trace artifact. All five are
caught: send-after-close and double-close panic; unhandled callback panic or
missing delivery breaks the expected offered history; disabled drop accounting
breaks the runtime evidence check.

Mixed trace files are rejected unless `generate_trace.py` receives an exact
`--run-id` + `--dispatcher-id` pair; selecting either partition produces a
valid TLC instance. Empty keys and one-sided selectors are rejected.

`generate_interval_trace.py` converts operation intervals into a real-time
precedence relation, preserves intra-operation abstract-step order, and asks
`DispatcherIntervalValidator.tla` to search possible linearizations while
reusing `DispatcherTraceValidator!Apply` rather than duplicating transition
semantics. A completed linearization is an expected `NoCompleteLinearization`
invariant counterexample: the valid intervals yield a depth-16 witness after
48 generated/23 distinct states. Mutating the post-close rejection to
acceptance yields no completion witness (36 generated/15 distinct states,
depth 9).

This remains finite-run evidence. It supports omitted evidence, reviewed action
classes, operation-interval ordering, and partial abstract-variable updates;
it does not establish universal implementation correctness.

### Actual Sessionstream production harvest

The tracing design is implemented in the real repository at
`pkg/sessionstream/transport/ws/observer_trace*.go` (Sessionstream commits
`ed50601`, `957c906`, and `229a47e`). `WithObserverTrace` is nil-gated and
requires stable run/dispatcher IDs. `ObserverModelEvent` uses sparse `updates`
and `evidence` maps; `ObserverIntervalEvent` records invoke/linearize/return or
invoke/cancel. Operation IDs also appear in `runtime/trace` tasks, regions, and
logs for submit, close, callback, drain, and wait.

```bash
cd tracelink
./run_production.sh
./run_production_mutations.sh
```

`run_production.sh` runs the actual Go harvest test under `GOMAXPROCS=1,2,4`,
checks contiguous single-partition JSONL, parses each `runtime.trace`, verifies
runtime task/operation correlation, generates interval TLA+, and requires TLC
to find a complete legal linearization. Results:

| GOMAXPROCS | Observed model / interval events | Observed TLC generated | Distinct | Depth |
|---:|---:|---:|---:|---:|
| 1 | 189 / 555 | 938 | 190 | 190 |
| 2 | 189 / 555 | 9,362–12,966 | 800–1,001 | 190 |
| 4 | 189–237 / 555–651 | 17,778–99,138 | 1,215–6,246 | 190–238 |

Counts vary with the harvested concurrent schedule; the acceptance criterion is
a complete legal linearization witness plus contiguous partitioned streams and
runtime correlation, not an exact state count.

The campaign found and corrected an instrumentation claim: native channel
`queue_len` sampled after send/receive is not atomic because another goroutine
may change it before logging. Production therefore emits only sound sparse
updates and lets TLC reconstruct queue state.

On any harvest, runtime parsing, generation, or TLC failure,
`run_production.sh` automatically preserves JSONL, runtime trace, generated
TLA+, TLC output, and a reason under `results/failures/`. Generated harvests are
large and reproducible, so they are not committed; compact evidence is in
`tracelink/results/production-summary.txt`.

Production mutations prove bridge sensitivity:

- missing operation identity is rejected structurally;
- `close_effective` with `updates.closing=false` has no complete refinement;
- moving an accepted-submit interval after Close return has no complete
  refinement.
