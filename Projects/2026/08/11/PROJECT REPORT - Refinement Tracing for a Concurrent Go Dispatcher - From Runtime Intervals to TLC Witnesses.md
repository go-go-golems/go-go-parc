---
title: "PROJECT REPORT - Refinement Tracing for a Concurrent Go Dispatcher - From Runtime Intervals to TLC Witnesses"
aliases:
  - Sessionstream Observer Refinement Tracing Deep Dive
  - Go Runtime Traces to TLA+ Refinement Witnesses
  - Operation-Interval Verification for Concurrent Go
  - TraceLink-Style Verification in Sessionstream
tags:
  - project
  - article
  - go
  - concurrency
  - formal-methods
  - tla-plus
  - runtime-trace
  - trace-refinement
  - linearizability
  - sessionstream
status: complete
type: project
created: 2026-08-11
repo: /home/manuel/code/wesen/go-go-golems/sessionstream
research_repo: /home/manuel/code/wesen/go-go-golems/go-go-parc
source_commits:
  - ed506015ff4b167dd076cfc4bf0c48d457891705
  - 957c906a2558091270ba684bc81961eb69975f6a
  - 229a47ebf1b2403c10075105e9504558fb675495
research_commits:
  - 7d10e1cd974a6371f750507bc371f7567a669137
  - e35a458852c127f2aac749ba6d5a22c0cf4965a5
  - e1af65f
---

# Refinement Tracing for a Concurrent Go Dispatcher: From Runtime Intervals to TLC Witnesses

A proof of a transition system establishes facts about that transition system. It does not establish that a concurrent Go program implements it. The missing argument is a refinement relation: every relevant execution of the program must correspond to a behavior admitted by the model. This report explains how that relation was made executable for Sessionstream's bounded asynchronous WebSocket observer dispatcher.

The completed system instruments the actual `ws.Server`, records operation intervals and sparse abstract updates, correlates them with Go runtime traces, converts the observations into a constrained TLA+ model, and asks TLC to find a legal abstract linearization. The verification harness runs the production dispatcher under multiple `GOMAXPROCS` values and rejects traces with corrupted operation identity, contradictory state updates, invalid lifecycle order, or impossible real-time boundaries.

This is not a universal proof of the Go binary. It is finite-execution refinement evidence with explicit semantics, mutation sensitivity, runtime correlation, and preserved failure artifacts. Its value comes from knowing precisely what each layer establishes and where each trusted boundary remains.

> [!summary]
> - The central verification problem was the correspondence between the concurrent Go execution and the proved dispatcher kernel, not the kernel invariant proof by itself.
> - Invocation, linearization, and return events preserve the partial order of overlapping Go operations. TLC searches the linearizations permitted by those intervals instead of trusting one instrumentation timestamp order.
> - Model events contain sparse abstract updates. State such as queue contents may be reconstructed by TLC when the Go program cannot observe it atomically at the claimed linearization point.
> - `runtime/trace` records the scheduler-level execution that produced the model evidence. Shared operation IDs connect runtime tasks and regions to abstract transitions without treating scheduler behavior as language semantics.
> - Production harvests at `GOMAXPROCS=1,2,4` all produced complete TLC refinement witnesses. Mutations to identity, lifecycle boundaries, and state updates were rejected.

## 1. The system under verification

Sessionstream's WebSocket transport exposes a typed diagnostic observer:

```go
type TransportObserver interface {
    OnTransport(ctx context.Context, rec TransportRecord)
}
```

The observer records connection, subscription, snapshot, heartbeat, frame, and fanout stages. Its callback is extension code. It must not determine socket-read latency, heartbeat progress, request execution, or connection shutdown.

The server therefore delivers observer records through a bounded asynchronous dispatcher. Producers call `observe`. A single worker invokes callbacks. The queue has fixed capacity. A full queue drops the new diagnostic record and increments a counter. Shutdown closes admission, drains accepted records, and waits for the worker. Callback panic is recovered per invocation.

The lifecycle can be summarized by five categories of operation:

```text
submit      admit, drop, or reject one record
close       make admission permanently closed
callback    receive and offer one accepted record
drain       establish worker exit after close and empty queue
wait        return after worker completion
```

The abstract safety contract includes:

```text
queue length never exceeds capacity
accepted values preserve FIFO order
capacity drops increment a monotone counter
post-close submissions are rejected
Close takes effect at most once
worker exit implies closed and drained
Wait return implies worker exit
callback panic still counts as an offered invocation
```

The earlier report, [[PROJECT REPORT - Bounded Asynchronous Observer Dispatch - Contracts Lifecycle and Generic Go Design|Bounded Asynchronous Observer Dispatch]], develops this contract and the dispatcher design. The present report begins where that design leaves off: how to attach the abstract contract to the actual concurrent program.

## 2. Three claims that must remain separate

Verification work becomes misleading when different evidence forms are collapsed into one word such as “verified.” This project maintains three distinct claims.

### 2.1 Abstract semantic correctness

The deterministic dispatcher kernel has state:

$$
S = (Q, A, O, C, d, closing, exited, waited)
$$

where:

- $Q$ is the bounded FIFO queue;
- $A$ is the admitted history;
- $O$ is the offered history;
- $C$ is either empty or the item currently being offered;
- $d$ is the capacity-drop count;
- `closing`, `exited`, and `waited` are lifecycle flags.

The central shape invariant is:

$$
A = O \mathbin{\raisebox{0.2ex}{$\smallfrown$}} C \mathbin{\raisebox{0.2ex}{$\smallfrown$}} Q.
$$

It says that every admitted item is in exactly one abstract location: already offered, currently in flight, or still queued. Coq and Lean prove this and related invariants for arbitrary capacities and transition sequences. TLA+ and Alloy explore the concurrent protocol and produce bounded counterexamples for deliberately unguarded variants.

These results establish correctness of the stated formal systems.

### 2.2 Source/runtime synchronization correctness

The Go shell owns mutexes, channels, goroutines, panic recovery, context handling, and worker completion. Its correctness depends on the Go memory model:

- mutex unlock synchronizes before a subsequent lock;
- channel send and receive establish defined synchronization edges;
- channel close synchronizes with receives that observe closure;
- goroutine exit creates no implicit join edge;
- data-race freedom permits sequentially consistent interleaving reasoning through DRF-SC.

`go test -race`, deterministic `testing/synctest` tests, stress runs, and mutation tests address this layer. Gobra proves selected deterministic and permission-transfer fragments, but its current frontend cannot desugar `select/default` and does not recognize `recover`. Those limitations are retained as executable probes rather than hidden behind trusted helper contracts.

### 2.3 Concrete trace refinement

For a concrete program execution $\tau_G$, the project checks whether there exists an abstract execution $\tau_A$ such that:

$$
\tau_G \preceq \tau_A.
$$

The relation $\preceq$ requires:

1. abstract actions agree with observed operation outcomes;
2. observed partial updates agree with the next abstract state;
3. per-operation abstract steps occur between invocation and return;
4. real-time precedence between non-overlapping operations is preserved;
5. every model event belongs to one run and dispatcher partition;
6. operation identities link model events and interval events consistently.

TLC checks this relation for each harvested finite execution. A successful witness does not quantify over executions that were not harvested.

## 3. Why a strict event log was insufficient

The first executable oracle used one total sequence of linearization-point events. That approach is effective when every event can be emitted at the exact synchronization point under a common ordering mechanism. It fails when the implementation's synchronization does not produce one directly observable total order.

Consider a capacity-one channel:

```text
producer sends item 10
worker receives item 10, freeing the slot
producer sends item 20
worker logs the receive of item 10
```

If the event log records:

```text
submit_accepted(10)
submit_accepted(20)
receive(10)
```

then the abstract queue appears full when item 20 is accepted. Strict replay rejects the trace, even though the underlying channel execution is legal. The instrumentation timestamp was not the receive's linearization point.

This is not a cosmetic logging problem. The event stream claims a temporal order that the program did not establish. Any verifier consuming that stream should reject it.

One response is to redesign the worker so channel receive and event emission occur under the same mutex as submission. The research scaffold tested that design. It is not desirable to impose that synchronization change on the production dispatcher only to simplify verification instrumentation.

The production solution records operation intervals.

## 4. Operation intervals

Every traced operation receives a stable operation ID and emits an interval stream:

```json
{"operation_id":"op-12","operation":"callback","phase":"invoke"}
{"operation_id":"op-12","operation":"callback","phase":"linearize","action":"receive"}
{"operation_id":"op-12","operation":"callback","phase":"linearize","action":"offered"}
{"operation_id":"op-12","operation":"callback","phase":"return"}
```

An operation may have multiple abstract transitions. A callback operation first receives an item and later records either `offered` or `panic_recovered`. Their order is fixed within the operation.

A receive candidate may lose the worker's `select` to the stop signal or to the default drain branch. It records:

```json
{"operation_id":"op-21","operation":"callback","phase":"invoke"}
{"operation_id":"op-21","operation":"callback","phase":"cancel"}
```

Cancelled operations contain no abstract transition and do not participate in linearization search.

### 4.1 Real-time precedence

For operation $a$, let $inv(a)$ be its invocation sequence and $ret(a)$ its return sequence. If:

$$
ret(a) < inv(b),
$$

then every abstract transition of $a$ must precede every abstract transition of $b$.

Overlapping operations have no such forced order. TLC may choose any order that satisfies the abstract transition relation and all observed updates.

The generated predecessor relation is:

```python
for before, (_, return_sequence) in bounds.items():
    for after, (invoke_sequence, _) in bounds.items():
        if before != after and return_sequence < invoke_sequence:
            for after_step in step_by_operation[after]:
                predecessors[after_step - 1].update(
                    step_by_operation[before]
                )
```

This is the operational content of interval-based linearizability checking. The verifier does not sort events by timestamps and declare that order authoritative. It constructs the partial order that the observed invocation and return boundaries justify.

### 4.2 Stable partition identity

Every event includes:

```go
RunID        string
DispatcherID string
OperationID  string
```

`RunID` identifies one harvested process/test execution. `DispatcherID` identifies one observer dispatcher within that run. `OperationID` joins the model and interval streams.

The generator refuses mixed input unless the caller selects exactly one run/dispatcher pair. It also rejects empty keys, non-contiguous sequences, missing operation intervals, operation metadata changes, and disagreement between model and interval action lists.

This validation matters because sequence number 17 has no global meaning. It is meaningful only within a specified event stream partition.

## 5. The production tracing API

The implementation is in:

```text
/home/manuel/code/wesen/go-go-golems/sessionstream/
  pkg/sessionstream/transport/ws/observer_trace.go
  pkg/sessionstream/transport/ws/observer_trace_jsonl.go
  pkg/sessionstream/transport/ws/observer.go
```

Tracing is enabled with an option:

```go
WithObserverTrace(ObserverTraceConfig{
    RunID:        "gomaxprocs-4",
    DispatcherID: "ws-observer-1",
    Sink:         sink,
})
```

Both IDs are required when a sink is configured. A nil sink sets the internal trace state to nil and disables instrumentation.

The sink receives two typed streams:

```go
type ObserverTraceSink interface {
    OnObserverModelEvent(ObserverModelEvent)
    OnObserverIntervalEvent(ObserverIntervalEvent)
}
```

The JSONL implementation serializes concurrent callbacks through a mutex and writes model and interval streams independently.

### 5.1 Nil-gated instrumentation

The main path starts with:

```go
operation := s.observerTrace.begin("submit")
defer operation.end()
```

Calling a method on a nil `*observerTraceState` is intentional. `begin` returns an empty operation without allocating an operation ID, starting a runtime region, or invoking a sink.

Sparse update maps are constructed only when tracing is active:

```go
if operation.state != nil {
    operation.linearize(
        "submit_rejected",
        item.itemID,
        nil,
        map[string]any{"closing": true},
    )
}
```

The benchmark comparison recorded during the completion audit was:

```text
Tracing disabled: 320.3 ns/op, 16 B/op, 1 alloc/op
Tracing enabled:  1820 ns/op, 149 B/op, 10 allocs/op
```

The disabled allocation is part of the existing observer-record/context path. Tracing adds no map allocation while disabled. Enabled tracing is an explicit verification/diagnostic mode rather than the default server behavior.

### 5.2 Sequencing concurrent sink callbacks

An early implementation used an atomic increment to allocate event sequence numbers before passing the event to a separately locked JSONL sink. Under concurrency, one goroutine could allocate sequence 7, pause, and write after the goroutine holding sequence 8. JSONL line order then disagreed with sequence order.

The correction assigns the sequence and calls the sink under one trace-state mutex:

```go
op.state.emitMu.Lock()
op.state.modelSeq++
op.state.config.Sink.OnObserverModelEvent(
    ObserverModelEvent{
        Sequence: op.state.modelSeq,
        // ...
    },
)
op.state.emitMu.Unlock()
```

The harvest harness requires:

```python
[e["sequence"] for e in events] == list(range(1, len(events) + 1))
```

This check would have detected the original ordering defect on every affected trace before TLC generation.

## 6. Sparse abstract updates

A model event names an action and may constrain selected next-state variables:

```go
type ObserverModelEvent struct {
    OperationID string
    Action      string
    ItemID      uint64
    Updates     map[string]any
    Evidence    map[string]any
}
```

Examples:

```json
{"action":"close_effective","updates":{"closing":true}}
{"action":"panic_recovered","item_id":17,
 "updates":{"offered_item":17}}
{"action":"wait_returned","updates":{"waited":true},
 "evidence":{"worker_done":true}}
```

An omitted variable is not assumed to be zero or false. TLC reconstructs it from the selected abstract transition.

The validator supports constraints on:

```text
queue_len
 dropped
closing
worker_done
waited
offered_item
```

The TLA+ predicate checks each constraint against the next state:

```tla
EvidenceMatches(e) ==
    /\ (~e.has_queue_len \/ e.queue_len = Len(queue'))
    /\ (~e.has_dropped \/ e.dropped = dropped')
    /\ (~e.has_closing \/ e.closing = closing')
    /\ (~e.has_worker_done \/ e.worker_done = exited')
    /\ (~e.has_waited \/ e.waited = waited')
    /\ (~e.has_offered_item \/
         (Len(offered') > 0 /\
          e.offered_item = offered'[Len(offered')]))
```

### 6.1 The queue-length correction

The first production instrumentation recorded `len(observerQueue)` immediately after native channel send and receive. The value was protected against data races by the channel implementation, but it was not an atomic observation of the abstract transition.

Under `GOMAXPROCS=2`, this sequence occurred:

```text
send item 2
worker receives item 2
submitter records queue_len = 2
```

The callback's receive could be observed before the submit's model event, and the sampled length could already include unrelated operations. TLC correctly reported that no abstract execution satisfied all claimed queue lengths.

Commit `229a47e` removed `queue_len` from accepted-submit and receive updates:

```go
operation.linearize("submit_accepted", item.itemID, nil, nil)
operation.linearize("receive", item.itemID, nil, nil)
```

The abstract actions determine their queue effects. TLC reconstructs queue contents and length. Queue length remains valid evidence where the synchronization makes the claim sound, such as the full-queue default branch under `observerMu` and the final closed-and-drained worker exit.

This correction establishes an important rule:

> [!important]
> Data-race-free observation is weaker than linearization-point observation. A value may be safe to read and still be invalid as an abstract next-state constraint.

## 7. Reusing one transition semantics

The interval validator does not reimplement dispatcher actions. It instantiates the strict `DispatcherTraceValidator` and calls its `Apply` predicate:

```tla
Kernel == INSTANCE DispatcherTraceValidator
    WITH Capacity <- Capacity,
         Items <- Items,
         Trace <- <<>>,
         queue <- queue,
         admitted <- admitted,
         offered <- offered,
         current <- current,
         closing <- closing,
         dropped <- dropped,
         closeCount <- closeCount,
         exited <- exited,
         waited <- waited,
         pos <- kernelPos
```

A candidate step is enabled when it has not been consumed and all predecessors have been consumed:

```tla
Enabled(i) ==
    /\ i \in StepSet \ consumed
    /\ Predecessors[i] \subseteq consumed

Consume(i) ==
    /\ Enabled(i)
    /\ Kernel!Apply(Steps[i])
    /\ kernelPos' = kernelPos
    /\ consumed' = consumed \cup {i}
```

This reuse is essential. If strict replay and interval checking had separate transition implementations, disagreements between them would become another verification problem.

### 7.1 Reachability as an expected invariant counterexample

The search asks whether all steps can be consumed:

```tla
NoCompleteLinearization == consumed # StepSet
```

For a valid trace, TLC violates this invariant. The counterexample is the desired witness: a sequence of abstract transitions that consumes every observed step while respecting interval precedence.

For an invalid trace, model checking completes without violating the invariant. No complete legal linearization is reachable within the finite generated system.

This use of an expected invariant counterexample is explicit in the harness. Exit status alone is not interpreted as success or failure; the script searches for the exact TLC verdict.

## 8. Correlation with `runtime/trace`

Model traces intentionally omit scheduler implementation details. They describe abstract actions and constraints. Debugging a failed refinement still requires knowing which goroutine ran, blocked, or resumed around a disputed operation.

The production tracer creates one runtime task:

```go
t.runtimeCtx, t.runtimeTask = trace.NewTask(
    ctx,
    "ws.observer_dispatcher",
)
```

Each operation creates a region:

```go
region := trace.StartRegion(
    ctx,
    "observer."+operation,
)
```

Invocation, linearization, cancellation, and return are logged with the same operation ID used by JSONL:

```go
trace.Logf(
    op.ctx,
    "observer.linearize",
    "id=%s action=%s item=%d",
    op.id,
    action,
    itemID,
)
```

A parsed runtime trace contains records such as:

```text
TaskBegin Type="ws.observer_dispatcher"
Category="observer.operation"
Message="id=op-3 phase=invoke operation=wait"
Category="observer.linearize"
Message="id=op-18 action=close_effective item=0"
```

The runtime trace answers diagnostic questions:

```text
Which goroutine emitted the disputed transition?
Which operations overlapped?
Where was a waiter blocked?
Was a callback running when Close returned?
Did a receive candidate lose the select and cancel?
```

It does not decide abstract legality. The TLC validator performs that check. Runtime tracing and model tracing are correlated evidence streams with different semantics.

## 9. The production harvest campaign

The environment-gated test `TestObserverTraceHarvestConcurrent` runs the actual `ws.Server` observer dispatcher. It writes JSONL only when `SESSIONSTREAM_OBSERVER_TRACE_DIR` is set.

The test begins with an accepted prefix so every schedule covers admission, receive, callback, close, drain, and wait. It then races:

```text
four submitter goroutines
one closer
three waiters
one observer worker
```

Each submitter attempts 40 records. Every seventeenth callback intentionally panics, exercising panic isolation when that item is accepted.

The external harness runs:

```bash
SESSIONSTREAM_OBSERVER_TRACE_DIR="$run_dir" \
GOMAXPROCS="$procs" \
go test ./pkg/sessionstream/transport/ws \
    -run '^TestObserverTraceHarvestConcurrent$' \
    -count=1 \
    -trace="$run_dir/runtime.trace"
```

for:

```text
GOMAXPROCS=1
GOMAXPROCS=2
GOMAXPROCS=4
```

### 9.1 Harness checks before TLC

Before generating TLA+, the script requires:

- nonempty model and interval streams;
- contiguous sequence numbers in line order;
- exactly one run/dispatcher partition;
- required actions: accepted submit, receive, effective close, worker exit, wait return;
- a runtime trace that parses successfully;
- a `ws.observer_dispatcher` runtime task;
- correlated `observer.linearize` runtime log records.

The parser is retried once because one campaign encountered a transient Go toolchain diagnostic:

```text
unknown or unsupported trace version go 1.26
```

The same file parsed successfully immediately afterward. The retry preserves the first diagnostic rather than deleting it.

### 9.2 TLC evidence

Every completed campaign found a complete interval-refinement witness.

| `GOMAXPROCS` | Observed model / interval events | Observed generated states | Distinct states | Depth |
|---:|---:|---:|---:|---:|
| 1 | 189 / 555 | 938 | 190 | 190 |
| 2 | 189 / 555 | 9,362–12,966 | 800–1,001 | 190 |
| 4 | 189–237 / 555–651 | 17,778–99,138 | 1,215–6,246 | 190–238 |

The counts vary because the test deliberately harvests concurrent schedules. Exact state counts are not acceptance criteria. The stable acceptance conditions are:

```text
event streams are structurally valid
runtime correlation is present
TLC reaches consumed = StepSet
abstract invariants hold along the witness
```

The larger P4 campaign generated 99,138 states and found 6,246 distinct states before reaching a complete depth-238 witness. The increase reflects more overlapping intervals and therefore more permitted candidate orders.

## 10. Failure preservation

A verification harness loses much of its value if it reports only “failed.” The production runner preserves a bundle whenever harvesting, runtime parsing, TLA+ generation, or TLC validation fails.

The bundle contains available copies of:

```text
model.jsonl
intervals.jsonl
runtime.trace
runtime parser output
generated TLA+ modules
TLC output
Go test output
REASON.txt
```

The implementation is direct:

```bash
fail_bundle() {
    local run_dir=$1 reason=$2
    local bundle="$FAILURES/$(basename "$run_dir")-$(date +%Y%m%dT%H%M%S)"
    mkdir -p "$bundle"
    cp -a "$run_dir"/. "$bundle"/ 2>/dev/null || true
    printf '%s\n' "$reason" > "$bundle/REASON.txt"
    exit 1
}
```

This mechanism was exercised during development. It preserved the P1 item-domain generator defect, the P2 non-atomic queue-length claim, and the transient runtime parser failure. Those failures were diagnosed from complete evidence rather than rerun speculation.

Raw production bundles are large and schedule-specific, so they are not committed to the vault. The scripts reproduce them, and the compact result summary records stable findings.

## 11. Mutation sensitivity

A refinement harness should reject known violations in the instrumentation and implementation boundary. The project uses several mutation classes.

### 11.1 Source-level dispatcher mutations

The research scaffold applies five source mutations:

| Mutation | Broken property | Observed detector |
|---|---|---|
| Remove closing guard | No send after close | Runtime panic or trace rejection |
| Bypass panic recovery | Worker survives callback panic | Process/test failure |
| Disable drop accounting | Accurate drop state | Runtime/oracle mismatch |
| Skip callback invocation | Accepted work is offered | Delivery history mismatch |
| Remove Close idempotence | Close at most once | Double-close panic |

All five fail the test harness and the comprehensive trace-generation boundary.

### 11.2 Production trace mutations

The production campaign derives three corruptions from an actual harvest.

#### Missing operation identity

One model event is changed to reference `missing-operation`. The interval generator rejects the trace before TLC:

```text
model event references missing operation interval: missing-operation
```

This tests structural integrity of the two-stream join.

#### Contradictory partial update

The `close_effective` action is changed to claim:

```json
{"updates":{"closing":false}}
```

The abstract transition requires `closing' = TRUE`. TLC explores the constrained system but finds no complete linearization.

#### Invalid real-time boundary

An accepted submit's complete interval is moved after Close has returned. The action remains `submit_accepted`; only invocation/return placement changes. Real-time precedence now forces:

```text
close_effective < submit_accepted
```

The sticky-close model makes that order impossible. TLC finds no complete witness.

These mutations demonstrate sensitivity to three different defects:

```text
stream identity corruption
state-constraint contradiction
real-time linearization impossibility
```

## 12. What each tool contributed

The project used multiple verification tools because no single tool covered the whole claim.

| Tool | Contribution | Explicit boundary |
|---|---|---|
| TLA+ / TLC | Concurrent protocol exploration and finite trace-refinement search | Model and generated constraints are trusted inputs |
| Alloy | Independent bounded temporal counterexamples and lifecycle witnesses | Finite configured scope |
| Coq | Axiom-audited invariant theorems for the transition kernel | Does not prove the Go shell |
| Lean 4 | Independent mechanized kernel theorems and axiom audit | Does not prove the Go shell |
| Gobra | Deterministic contracts, mutex invariant ownership, buffered-channel permission transfer | Current frontend lacks `select/default` and `recover` |
| SPIN / Promela | Independent channel/lifecycle protocol exploration | Abstracted item values and bounded topology |
| Go race detector | Dynamic race detection on exercised executions | Does not cover unexecuted schedules |
| `testing/synctest` | Durable-blocking and fake-time synchronization in deterministic tests | Bubble-local concurrency only |
| Go fuzzing | Millions of state-aware operation sequences | Finite generated inputs and schedules |
| `runtime/trace` | Goroutine/runtime diagnostics correlated by operation ID | Not an abstract legality checker |
| TLC interval validator | Finite executable-to-model refinement witnesses | Not a universal source proof |

The independent tools also test one another. TLC rejected an instrumentation order that the Go behavior itself allowed. The production harvest found an unsound queue-length claim. Mutations demonstrated that positive results were not caused by a verifier that accepted every input.

## 13. Trusted computing base

A rigorous report must identify what remains trusted.

The current chain includes:

```text
Go source instrumentation
ObserverTraceSink implementation
JSON encoder and files
Python generators
TLA+ transition semantics
TLC implementation
Go compiler and runtime
runtime/trace implementation and parser
```

The theorem-prover work has its own proof-kernel assumptions. Gobra adds its frontend, Viper translation, Silicon backend, and Z3. SPIN adds its Promela semantics and generated verifier.

The most important manually reviewed boundaries are:

1. **Action mapping.** `submit_accepted`, `receive`, `offered`, `close_effective`, `worker_exit`, and `wait_returned` must denote the intended abstract transitions.
2. **Interval placement.** Invocation and return must surround the real operation, and linearization records must belong to the correct operation.
3. **Partial update soundness.** Every emitted update must be atomic at or implied by the claimed transition.
4. **Generator correctness.** Operation IDs, action lists, predecessor sets, item domains, and partitions must be translated without alteration.

Mutation tests reduce risk at these boundaries. They do not eliminate the trust assumptions.

## 14. Reproduction

### 14.1 Tool installation

The verified local setup used:

```text
Go 1.26.5
TLC 2.19
Gobra v26.02
Z3 4.8.7
SPIN 6.5.2
Java 21
```

Local launchers:

```text
~/.local/bin/tlc
~/.local/bin/gobra
~/.local/bin/z3
```

### 14.2 Sessionstream validation

```bash
cd /home/manuel/code/wesen/go-go-golems/sessionstream

go test ./... -count=1
go test -race ./pkg/sessionstream/transport/ws -count=1
go vet ./...
GOWORK=off ./.bin/golangci-lint run
```

Focused deterministic checks:

```bash
go test ./pkg/sessionstream/transport/ws \
  -run 'TestObserverTrace|TestObserverDispatcherSynctest' \
  -count=20

go test -race ./pkg/sessionstream/transport/ws \
  -run 'TestObserverTrace|TestObserverDispatcherSynctest' \
  -count=10
```

### 14.3 Research and production refinement

```bash
cd "/home/manuel/code/wesen/go-go-golems/go-go-parc/Research/Software Architecture Garden/sessionstream/designs/research/specs/tracelink"

./run_all.sh
./mutate_tracegen.sh
./run_production.sh
./run_production_mutations.sh
```

The production runner creates schedule-specific outputs under:

```text
results/production/gomaxprocs-1/
results/production/gomaxprocs-2/
results/production/gomaxprocs-4/
```

Failure bundles are written under:

```text
results/failures/
```

### 14.4 Source archive verification

The research archive contains 15 Defuddle Markdown snapshots and 12 primary papers/theses, including Goose, Perennial, Waddle, PGo, TraceLink, Gomela, GoJournal, Grove, and CertiCoq material.

```bash
cd "/home/manuel/code/wesen/go-go-golems/go-go-parc/Research/Software Architecture Garden/sessionstream/designs/research/sources"
sha256sum --check SHA256SUMS
```

All 28 checksummed entries passed during the completion audit.

## 15. Commits and artifact map

### Sessionstream implementation

```text
ed506015ff4b167dd076cfc4bf0c48d457891705
    Add observer dispatcher refinement tracing

957c906a2558091270ba684bc81961eb69975f6a
    Stabilize observer trace harvest coverage

229a47ebf1b2403c10075105e9504558fb675495
    Avoid non-atomic observer queue trace claims
```

### Vault and research package

```text
7d10e1cd974a6371f750507bc371f7567a669137
    Archive Go verification research sources

e35a458852c127f2aac749ba6d5a22c0cf4965a5
    Add executable Go refinement verification study

e1af65f
    Record concurrent refinement evidence ranges
```

### Core files

```text
Sessionstream:
  pkg/sessionstream/transport/ws/observer.go
  pkg/sessionstream/transport/ws/observer_trace.go
  pkg/sessionstream/transport/ws/observer_trace_jsonl.go
  pkg/sessionstream/transport/ws/observer_trace_harvest_test.go

Vault research:
  Research/Software Architecture Garden/sessionstream/designs/research/
    01 - Proving the Bounded Asynchronous Observer Dispatcher.md
    02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables.md
    specs/tracelink/DispatcherTraceValidator.tla
    specs/tracelink/DispatcherIntervalValidator.tla
    specs/tracelink/generate_trace.py
    specs/tracelink/generate_interval_trace.py
    specs/tracelink/run_production.sh
    specs/tracelink/run_production_mutations.sh
    specs/tracelink/results/production-summary.txt
```

## 16. Technical lessons

The strongest lessons from the implementation are specific.

### 16.1 Prove only claims emitted at real synchronization points

A mutex-protected field update can usually be observed atomically within the mutex critical section. A native channel send followed by `len(ch)` is not one atomic abstract step. The latter value must be omitted unless the implementation supplies stronger synchronization.

### 16.2 Omitted state is better than false precision

A partial trace can be more trustworthy than a complete-looking trace. TLC can reconstruct queue contents from admitted and received actions. It cannot correct an incorrect queue-length claim without rejecting the trace.

### 16.3 Operation intervals preserve concurrency semantics

One event sequence is appropriate for already-linearized transitions. It is not sufficient for overlapping operations whose exact order is unobserved. Invocation and return boundaries encode the order the program actually establishes; search resolves the rest.

### 16.4 Runtime traces and model traces should share identity, not semantics

Runtime traces contain goroutine scheduling and blocking events. Model traces contain abstract state transitions. Operation IDs make the two streams jointly useful without incorporating scheduler implementation details into the formal model.

### 16.5 Failure bundles are part of the verification design

The first production campaigns failed for different reasons: an incomplete item domain, an unsound abstract update, and a transient runtime parser diagnostic. Automatic artifact preservation made each failure reproducible and distinguishable.

### 16.6 Mutation sensitivity is required evidence

A passing positive trace does not show that the checker rejects bad traces. Identity, lifecycle, update, instrumentation-order, panic, delivery, accounting, and idempotence mutations establish that the harness responds to the contract violations it claims to detect.

## 17. Current boundary and next work

The system now provides production-grade finite trace-refinement evidence for the actual Sessionstream observer dispatcher. It does not prove every possible Go execution. A universal source proof still requires a verifier with semantics for the production constructs or a verified compilation/refinement chain.

Current Gobra cannot cover the complete shell because:

```text
select/default -> scala.NotImplementedError during desugaring
recover         -> unknown identifier
```

The retained proofs still establish useful fragments: deterministic kernel contracts, mutex invariant ownership, and buffered-channel permission transfer. A future Gobra release should be retested through the pinned probes.

The strongest next extensions are:

1. Add a rolling `runtime/trace` flight recorder for long-running soak tests and dump it on refinement rejection or shutdown watchdog failure.
2. Harvest more than one dispatcher instance in one process and validate explicit partition selection at production scale.
3. Add randomized but reproducible operation schedules with seed metadata while retaining the deterministic accepted prefix.
4. Explore Goose translation on a reduced production shell, explicitly inventorying unsupported Go constructs and trusted external specifications.
5. Move stable trace-schema definitions into a package reusable by other bounded concurrent components only after another retained consumer demonstrates the same contract.

## 18. Working rules

- Separate abstract proof, source synchronization evidence, and finite trace refinement.
- Attach every model event to a stable run, dispatcher, and operation identity.
- Record invocation and return when overlapping operations make one timestamp order unjustified.
- Emit only abstract updates that are atomic at or implied by the claimed transition.
- Omit state that TLC can reconstruct rather than recording a racy or temporally displaced value.
- Correlate runtime and model traces through operation IDs; do not model scheduler internals as correctness assumptions.
- Require positive witnesses and contract-targeted negative traces.
- Preserve all artifacts when verification fails.
- Treat state counts as schedule-dependent evidence, not golden constants.
- State the trusted computing base and the finite-run boundary in every verification report.

## Related notes

- [[PROJECT REPORT - Bounded Asynchronous Observer Dispatch - Contracts Lifecycle and Generic Go Design|Bounded Asynchronous Observer Dispatch: Contracts, Lifecycle, and Generic Go Design]]
- [[Research/Software Architecture Garden/sessionstream/designs/research/01 - Proving the Bounded Asynchronous Observer Dispatcher|Proving the Bounded Asynchronous Observer Dispatcher]]
- [[Research/Software Architecture Garden/sessionstream/designs/research/02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables|Constraining the Go Binary: Layered Refinement from Proved Kernels to Executables]]
- [[Research/Software Architecture Garden/sessionstream/designs/02 - Typed Transition Systems and Trace Algebra|Typed Transition Systems and Trace Algebra]]
- [[Research/Software Architecture Garden/sessionstream/designs/03 - Effect-Acknowledged State Machines and Runtime Refinement|Effect-Acknowledged State Machines and Runtime Refinement]]
- [[Research/Software Architecture Garden/sessionstream/README|Architecture Garden — sessionstream]]
