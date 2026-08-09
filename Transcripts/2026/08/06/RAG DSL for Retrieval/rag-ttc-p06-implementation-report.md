---
title: "P06: Flow Executor Semantics and Captured Effects"
subtitle: "Implementation and conformance report for rag-ttc"
author: "OpenAI - implementation study"
date: "August 5, 2026"
lang: en-US
toc: true
toc-depth: 3
numbersections: false
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

# Abstract

P06 implements a rigorous operational contract for `rag-ttc/pkg/flow` without replacing its typed Go composition model. The implementation separates semantic output from execution history, introduces explicit effect and locality declarations, distinguishes step definition, stage placement, logical operation, retry attempt, and physical batch identity, adds attempt-level external-effect capture and offline replay, revises reports so repeated display names no longer conflate executions, and supplies a reusable metamorphic conformance harness.

The central result is conditional rather than absolute: caching, retry, batching, concurrency, and barriers preserve semantic output only when their documented preconditions hold. The implementation rejects retries for declared non-idempotent operations, even when capture is configured, because recording an ambiguous mutation is not an exactly-once protocol. It adds `Snapshot` for operations that truly require the complete input collection and demonstrates that the existing temporal `Barrier` cannot implement global top-k by itself.

The standalone model exhaustively tested all 720 completion schedules for six inputs and all 128 contiguous partitions for eight inputs. The actual adapter tested eight `flow.Bulk` sizes, report non-conflation, cache and retry faults, partial batches, budget boundaries, snapshot-global behavior, and offline replay. The selected P06 and pre-existing `flow` packages passed 102 race-enabled test functions and `go vet` under an offline Go 1.23.2 compatibility harness. The repository declares Go 1.26.5; the complete module suite could not be executed without the declared toolchain and dependency downloads. Claims are therefore labeled by evidence level throughout.

# Executive summary

## What changed

P06 adds four small semantic boundaries:

1. **Contract:** each step declares whether it is pure, read-only, idempotent, captured, non-idempotent, or not yet classified, and whether it is item-local or snapshot-global.
2. **Identity:** display names are separated from stable definition IDs, run-specific stage IDs, logical operation IDs, attempt IDs, and physical batch IDs.
3. **Captured effects:** external attempt outcomes can be captured once and replayed offline by semantic request and attempt number.
4. **Semantic comparison:** executor variants are compared after projecting away trace-only differences such as timestamps, retries, cache outcomes, and trace IDs.

The architecture remains:

```text
ordinary Go program -> typed flow Steps/Pipes -> executor mechanics
```

It does not become:

```text
workflow DSL -> central scheduler -> persisted control graph
```

## Main findings

- **Confirmed source defect:** the supplied `flow.Report` stored one record per display name, so two distinct stages called `transform` were merged. The v2 report preserves two stage identities while retaining the old aggregate as a compatibility view.
- **Confirmed undocumented precondition:** `Bulk` can detect the wrong number of outputs but cannot detect a same-length permutation. A reversed result batch passes cardinality checks and produces wrong aligned semantics.
- **Confirmed barrier mismatch:** `Barrier=true` waits for upstream completion but still invokes `Do` item by item. Global top-k requires explicit complete-collection access.
- **Confirmed retry limit:** capture can reproduce an attempt sequence, including transient failure followed by success, but cannot prevent a committed non-idempotent mutation from being repeated after an ambiguous timeout.
- **Positive result:** for compliant item-local operations, the tested sequential, parallel, batched, cached, retried, and replayed paths agree under the semantic projection while their operational traces differ as expected.
- **Positive result:** generation and embedding adapters can declare read-only effects and reuse existing cache identity as a capture key without changing their public orchestration shape.

## Recommended disposition

Adopt the P06 identity hierarchy, report v2, `effectlog`, locality boundary, and conformance harness, with three merge conditions:

1. run the complete suite under Go 1.26.5 and real dependencies;
2. audit every production step before changing `EffectUnknown` to a stronger declaration;
3. require provider adapters to document or validate batch response mapping rather than relying on cardinality alone.

# Evidence labels

Every substantive claim uses one of these labels:

| Label | Meaning in this report |
| --- | --- |
| **Proved from the model** | Follows from the executable reference model or ID construction under stated assumptions. It is not a proof about arbitrary external providers. |
| **Verified by exhaustive finite testing** | Every member of a stated finite space was executed, such as all 720 permutations. |
| **Property-tested** | Deterministic, adversarial, race-enabled, or metamorphic tests support the claim, but the input space is not exhaustive. |
| **Supported empirically** | Measured on one environment; useful for engineering comparison, not a semantic guarantee. |
| **Still conjectural** | Requires the declared toolchain, real provider behavior, production load, or a broader proof. |

# 1. Scope and questions

P06 studies the operational layer only. It does not define canonical RAG facts, ranking quality, closure rules, or agent policy. It asks when execution mechanics preserve the result promised by a typed operation.

The implementation answers the project questions as follows:

1. A `flow.Step` is a typed operation interpreted under an explicit effect/locality contract. It may be pure, effectful, or a deterministic function over captured observations.
2. Workers, cache, retry, and batching are transparent only under local preconditions stated in `contract-catalog.md`.
3. `StepID`, `StageID`, `OperationID`, `AttemptID`, `BatchID`, and `Name` have separate roles.
4. Non-monotone cross-item operations require `Snapshot`; temporal barriers alone are insufficient.
5. `effectlog` records each attempt outcome and replays it by semantic request identity and attempt number.
6. The existing Go APIs can be instrumented without a workflow scheduler; `Step`, `Pipe`, `Bulk`, and `Batched` remain the programming model.

Explicit non-goals were honored. No distributed scheduler, persisted workflow state, provider throughput redesign, or exactly-once side-effect mechanism was introduced.

# 2. Supplied architecture and source verification

## 2.1 `flow` was already the correct architectural boundary

The supplied package documentation explicitly says `flow` owns mechanics and that workflow belongs to the calling program, with no DAG scheduler or persisted control state (`pkg/flow/doc.go:1-17` in the supplied snapshot). That boundary is retained. P06 extends local contracts and observability rather than introducing another orchestration layer.

The supplied `Step` combined identity, policy, one-item work, meters, result observation, barrier behavior, and internal composition hooks (`pkg/flow/step.go:27-64` in the supplied snapshot). This was a strong base: typed composition already existed, and the implementation did not need to invent a generic node graph.

## 2.2 Ordered parallelism was already deliberate

`pkg/execution.Map` allocated a result slice with input cardinality and wrote each result to `results[current.index]`, while worker completion could occur out of order (`pkg/execution/map.go:32-105` in the supplied snapshot). The supplied `flow.Result` documentation also promised `Results[i]` corresponds to `items[i]` (`pkg/flow/report.go:89-101`).

This gives the executor an important invariant: completion order need not be semantic output order. P06 makes the corresponding preconditions explicit and records operation identity independently of completion timing.

## 2.3 Report-name conflation was real

The original report was exactly:

```go
type Report struct {
    Steps map[string]StepReport `json:"steps"`
}
```

and merge aggregated by the string key (`pkg/flow/report.go:67-80` in the supplied snapshot). The original `Step.Name` comment called it the report and log name (`pkg/flow/step.go:30-34`). Therefore two distinct step definitions or placements with the same display name were indistinguishable in the report.

This is not merely a naming preference. It prevents precise attribution of retries, errors, meters, and cache behavior and makes a repeated stage impossible to reconstruct from the report.

## 2.4 Batch order was a real semantic precondition

The supplied cached-batch implementation documented that results preserve input order and checked only that the number of outputs matched the number of unique miss groups (`pkg/execution/cached_batch_map.go:21-25` and `141-147`). The supplied `flow.Bulk` comment likewise required one result per input in order.

That is a valid contract, but it is not enforceable from generic same-typed values. The reversed-batch fixture confirms that a provider can return the right number of values in the wrong order and silently change semantics.

## 2.5 Barrier wording exceeded its API power

The supplied `Step.Barrier` comment said it was needed when a stage consumes cross-item state (`pkg/flow/step.go:37-40`). The implementation waited before running the stage, but `Do` still received one item. A caller could use hidden shared state, but `flow` could not guarantee the complete snapshot, immutable membership, or deterministic access pattern.

P06 narrows the old flag to its actual temporal meaning and adds a typed collection operation for the stronger use case.

# 3. Semantic model

## 3.1 Two outputs from one execution

P06 treats execution as producing two related but different artifacts:

```text
semantic outcome + operational trace
```

For each input position, the semantic outcome is success, quarantine, skip, or a stopped run. The operational trace records how that outcome was obtained: cache traffic, worker completion, physical batches, retries, capture/replay, meters, and timing.

This is necessary because transparent executor variants are expected to have different traces. A cache hit and a provider call should yield the same semantic value under a correct cache contract, but they must not yield the same cost trace. A two-attempt live call and its offline replay should yield the same final value and retry control flow, but only the replay should mark attempts as replayed and avoid fresh provider metering.

## 3.2 Semantic projection

Let `R` be the full result and report. P06 compares a projection `P(R)` that retains:

- aligned successful values;
- quarantine error class/message;
- skip markers;
- terminal run error/stop contract.

It removes:

- run, stage, operation, attempt, and batch IDs;
- timestamps and event sequence;
- cache hit/miss/store state;
- retry count and attempt timing;
- provider meters that describe execution cost;
- completion order.

A policy variant is transparent for a test case when:

```text
P(run_baseline(inputs)) == P(run_variant(inputs))
```

This equation is meaningful only after stating the operation's effect, locality, key, mapping, and failure preconditions.

## 3.3 Effect declarations

The implemented effect taxonomy is small enough to audit:

```text
unknown, pure, read-only, idempotent, captured, non-idempotent
```

`unknown` preserves source compatibility but carries no strong guarantee. `pure`, `read-only`, and `idempotent` permit retry under their usual preconditions. `captured` requires a capture codec and recorder. `non-idempotent` rejects multiple attempts.

The taxonomy is a contract, not a compiler proof. A developer can lie. Its value is that safety assumptions are visible in code, rejected when obviously inconsistent, and reusable by tests and report tooling.

## 3.4 Locality declarations

Two localities are implemented:

- `item-local`: one logical operation can be interpreted without another item's partial state;
- `snapshot-global`: one operation receives the complete declared collection.

A plain step is item-local by construction. A plain step cannot claim snapshot-global locality. The `Snapshot` constructor sets and validates the global contract.

## 3.5 Identity hierarchy

![Trace identity hierarchy](assets/identity-hierarchy.png)

The hierarchy is designed to avoid two opposite errors:

- using one display string for unrelated executions;
- using run-local trace identity as portable semantic request identity.

`StepID` is stable across runs. `StageID`, `OperationID`, `AttemptID`, and `BatchID` are trace identities derived within a run. The effect capture key uses stable step and semantic request identity, not run-local IDs.

## 3.6 Cache and capture

![Result cache and attempt capture boundaries](assets/execution-boundaries.png)

The result cache and effect capture are orthogonal:

- a cache stores the final successful admitted value;
- capture stores each attempted external observation, including errors.

This separation is important in RAG experiments. A result cache is efficient but erases whether an answer required a retry. A captured-effect snapshot can reproduce the retry path and failure classification offline. Conversely, replaying each attempt can be more expensive than a result cache and should not be mistaken for the preferred production cache path.

# 4. Implementation

## 4.1 `pkg/effectlog`

The new package provides typed IDs, deterministic derivation functions, a `Recorder` interface, and a concurrency-safe in-memory implementation.

The portable request carries:

```go
type Request struct {
    Run, Step, Stage, Operation, Attempt, Batch ...
    AttemptNumber int
    SemanticKey   string
    Payload       json.RawMessage
}
```

Only `Step`, `SemanticKey`, and `AttemptNumber` determine replay lookup. The other IDs preserve live-run causality. A payload mismatch under the same lookup key fails closed. Captures include an integrity digest, recording time, duration, and either a JSON response or classified error.

Concurrent capture misses for one key are single-flighted. Waiting callers receive the same recorded result rather than repeating live work. Replay mode refuses a miss. Snapshot loading validates schema, keys, outcomes, content digests, conflicting duplicate captures, unknown fields, and trailing JSON.

## 4.2 Flow contracts and capture codecs

`pkg/flow/semantics.go` adds ID aliases, `TraceOptions`, effect/locality enums, `Contract`, generic `CaptureSpec`, `JSONCapture`, and an invocation context accessor. The invocation context allows adapters to access operation and attempt identity without changing the typed `Do` signature.

Contract validation runs before item one. It enforces:

- valid enum values;
- snapshot-global only through the snapshot constructor;
- capture availability for `EffectCaptured`;
- no automatic retry for `EffectNonIdempotent`.

## 4.3 Report v2 and operation traces

`pkg/flow/report.go` now defines explicit run status, stop reason, stage, operation, and attempt records. The old `Steps` map remains but is documented as lossy. `Report.Validate` verifies the identity hierarchy and cross-links.

`pkg/flow/trace.go` contains a concurrency-safe operation tracker. It groups duplicate positions under one logical operation where cache or capture identity identifies the request, records attempt start/finish and replay state, and constructs deterministic report slices. Event stamping is run-scoped and synchronized.

Flow executor events use `operation-trace/v1`; capture-recorder lifecycle events use `captured-effect-event/v1`; the report schema is `flow-report/v2`. Keeping these schemas distinct prevents capture events from being misrepresented as executor-operation events. Sample artifacts are bundled and schema-validated.

## 4.4 `Run`, `Bulk`, and `Batched`

`Run` allocates a stage placement independently of display name, validates the contract, tracks logical operations and attempts, mediates capture/replay, and finalizes explicit completion or stop status.

`Bulk` now records both logical operations and physical batches. It applies capture/replay around the physical grouped call while retaining one logical operation for each unique request. A replayed batch does not count as a fresh provider work call or fresh meter usage. Response length mismatch marks affected operations failed and returns an error. Same-length permutation remains an explicit adapter precondition.

`Batched` exposes stable group-call identity, effect contract, and capture configuration. Repair remains a typed nested step and continues to share declared budgets when configured.

## 4.5 `Snapshot`

`Snapshot` is a new aligned collection-level constructor. It receives all input values in one call, returns exactly one output per input, and participates in retry, capture, cache, budget, failure policy, report, and trace infrastructure. It is deliberately not a generic reduce or cardinality-changing operator.

![Item-local barrier versus snapshot-global access](assets/locality-boundary.png)

## 4.6 `pkg/flowtest`

The new package provides reusable cases, variants, projections, assessments, and mismatch descriptions. The default projection ignores expected operational variance but includes semantic values and declared failure outcomes. Callers can supply domain-specific equality.

The harness is used as a positive conformance test and a negative-control detector. A test suite that cannot detect the reversed-batch fixture is not accepted.

## 4.7 RAG-shaped adapters

The generation and embedding flow adapters now declare read-only item-local effects and attach JSON capture codecs. The embedding path retains the explicit positional bulk precondition. Existing semantic cache identities are reused rather than inventing a second request identity.

The production adapters compile in the offline harness. Their test files require the declared newer Go toolchain and were not executed here.

# 5. Experimental method

## 5.1 Two implementations

The assignment required an executable specification independent of the production executor and a narrow adapter to the actual codebase.

### Standalone model

`standalone/` uses only the Go standard library. It models:

- semantic requests and outcomes;
- effect kinds and retry validation;
- result cache and attempt capture state;
- run, stage, operation, and attempt identity;
- worker completion schedules;
- contiguous batch partitions;
- explicit budget stops;
- aligned global snapshot operations.

The model is intentionally smaller than `pkg/flow`; it serves as an oracle for the laws rather than a second production executor.

### rag-ttc adapter

`adapter/` constructs real `flow.Step` values, invokes actual `flow.Run`, `flow.Bulk`, and `flow.Snapshot`, injects faults, validates reports, and compares semantic projections through `pkg/flowtest`.

This two-level method reduces circularity. Passing tests in the production implementation alone would not show that the intended law was specified independently. Passing the standalone model alone would not show that rag-ttc implements it.

## 5.2 Test environment

The supplied repository declares Go 1.26.5 and includes a `tool` block. The available environment provided Go 1.23.2 and had no network access for downloading the declared toolchain or modules. P06 therefore created a narrowly scoped GOPATH validation harness with small source-compatible stubs for the dependencies required by the target packages.

The stubs are bundled under `compat/` and are explicitly not production replacements. They allowed execution of:

- `pkg/effectlog`;
- `pkg/flow`, including all pre-existing tests;
- `pkg/flowtest`;
- the standalone model;
- the P06 rag-ttc adapter.

The generation and embedding production packages were built in the same harness. Their tests use APIs unavailable in Go 1.23.2, so those tests await the declared toolchain.

## 5.3 Test inventory

The selected packages expose 102 test functions:

| Package | Test functions | Role |
| --- | ---: | --- |
| `pkg/effectlog` | 9 | capture, replay, integrity, concurrency, payload collision, IDs |
| `pkg/flow` | 73 | 62 supplied executor tests plus 11 P06 semantic tests |
| `pkg/flowtest` | 2 | positive and negative metamorphic controls |
| standalone model | 8 | finite schedules, partitions, retry, budget, capture, globality |
| rag-ttc adapter | 10 | real executor schedules, faults, batches, cache, budget, snapshot |
| **Total** | **102** | race-enabled target suite |

All selected tests were run with `-race` and `-count=1`. The raw command output is in `results/raw/test-output.txt`; vet output is in `results/raw/vet-output.txt`.

## 5.4 Primary finite experiments

### Completion schedule independence

Six distinct logical inputs were evaluated under every permutation of completion order. There are:

```text
6! = 720
```

schedules. Each schedule was applied to the standalone executor and compared to the input-order baseline.

### Batch partition independence

Eight inputs were partitioned into every non-empty contiguous partitioning. The seven gaps between eight elements can each be cut or not cut:

```text
2^7 = 128
```

partitions. Every aligned batch implementation was compared to the per-item reference.

### Actual `flow.Bulk` batch sizes

The actual executor ran the same eight-item operation with batch sizes 1 through 8. Each output was compared to per-item execution.

### Report name collision

Two different definitions with the display name `transform` were composed. The v2 report was required to contain two distinct stages and the compatibility view was expected to aggregate four item-stage executions.

### Captured retry and replay

A generation-shaped call returned a classified transient error on attempt one and success on attempt two. Both attempts were captured. A new run with a replay-only recorder and a live function that always fails if called was required to reproduce the same result and retry sequence with zero live calls.

### Global barrier

Scores `[3, 10, 7]` were evaluated by an item-local pseudo-top-one function and by a snapshot-global top-one function. Only the snapshot version was expected to return membership `[false, true, false]`.

### Unsafe retry refusal

A declared non-idempotent mutation with two attempts and capture configured was required to fail contract validation before executing the mutation.

## 5.5 Fault injection

The adapter tests cover:

- transient failure followed by success;
- corrupt cache decode;
- cache hit and miss paths;
- incomplete batch response;
- same-length reversed batch response;
- duplicate logical keys;
- completion-order permutations;
- budget boundaries from zero through five units;
- unknown legacy mutation behavior;
- declared non-idempotent mutation;
- capture replay miss and payload mismatch;
- capture snapshot tampering;
- repeated display names;
- invalid report links and attempt IDs.

Each stable counterexample is represented in `fixtures/` using `p06-fixture/v1`.

## 5.6 Schema validation

The hand-off includes schemas for:

- `captured-effect/v1`;
- `captured-effect-event/v1`;
- `captured-effect-snapshot/v1`;
- `operation-trace/v1`;
- `flow-report/v2`;
- `p06-fixture/v1`;
- the shared project result schema.

The validation run checked nine fixtures, one report, eighteen operation-trace events, one capture snapshot, and two captures. The validation result is recorded in `results/raw/schema-validation.json`.

## 5.7 Benchmark method

Five microbenchmarks executed 100 logical inputs for 50 benchmark iterations:

- pure sequential;
- pure with eight workers;
- aligned bulk size 20;
- in-memory cache hits;
- captured generation replay.

They report wall-clock nanoseconds, bytes allocated, and allocations on one Linux/amd64 environment. They are diagnostic only. The benchmark is not statistically sufficient for production capacity planning and does not use live network providers.

# 6. Results

## 6.1 Primary conformance results

| Scenario | Cases | Result | Evidence level |
| --- | ---: | --- | --- |
| All six-input completion schedules | 720 | One aligned semantic output | **Verified by exhaustive finite testing** |
| All contiguous eight-input partitions | 128 | One aligned semantic output | **Verified by exhaustive finite testing** |
| Actual `flow.Bulk` sizes 1..8 | 8 | Equal to per-item baseline | **Property-tested** |
| Repeated display name | 2 stages | Distinct v2 stages; one expected lossy legacy aggregate | **Property-tested** and **proved from ID construction** |
| Two-attempt capture/replay | 2 captured attempts | Same output; replay made zero live calls | **Property-tested** |
| Snapshot global top-one | 3 items | `[false, true, false]` | **Property-tested** |
| Non-idempotent retry | 1 contract | Rejected before work | **Proved from validation rule** and **property-tested** |

The machine-readable summary is `results/raw/experiment-summary.json`.

## 6.2 Race and vet results

All selected packages passed the race-enabled test run. `go vet` produced no findings for the target packages. This supports memory safety and conformance under the tested executions, but it is not a proof that all possible user-provided callbacks are race-free.

The most relevant positive checks were:

- simultaneous capture calls for one semantic attempt execute live work once;
- operation and attempt report mutation is protected under concurrent workers;
- deterministic result alignment survives delayed and gated completions;
- repeated names do not overwrite stage records;
- replayed physical bulk calls do not increment fresh-work meters;
- report validation detects broken stage references and tampered attempt IDs.

## 6.3 Capture and replay

The primary captured retry produced two capture records:

1. attempt one with a transient error;
2. attempt two with a successful response.

A replay run used a different `RunID`, `StageID`, `OperationID`, and `AttemptID` hierarchy but found the same records because those trace-local IDs are excluded from replay lookup. The live provider function was replaced with a function that would fail the test if invoked. It was not invoked.

This supports the claim that run-local trace identity is separated from semantic attempt replay identity. It does not claim that the captured external response remains factually current.

## 6.4 Report non-conflation

The sample report has:

```text
name aggregate: transform -> 6 item-stage executions
stage 1: increment definition -> 3 items
stage 2: double definition    -> 3 items
logical operations: 6
attempts: 6
```

Both stages retain the same display name. Their `StepID` and `StageID` values differ. This is the intended coexistence of human-readable grouping and exact execution identity.

The compatibility map is preserved so existing dashboards do not fail immediately. It should not be used for causality, error attribution, or exact replay.

## 6.5 Barrier result

The item-local operation saw each value alone and marked every one as its own local maximum. Setting `Barrier=true` did not change that because the function signature remained `Do(ctx, item)`.

The snapshot operation received all three values and selected exactly one global maximum. This is a direct counterexample to treating temporal waiting as complete-collection semantics.

## 6.6 Batch result

Compliant positional batching matched per-item output across every finite partition and every actual batch size in the primary study. The reversed batch returned the correct number and type of values but attached them to wrong input positions. It was detected only by semantic comparison, not by the generic cardinality guard.

This falsifies any stronger claim that `Bulk` can guarantee mapping correctness for arbitrary provider functions. Its correct contract is conditional and must remain documented at the adapter boundary.

## 6.7 Retry result

Pure, read-only/captured, and test-idempotent operations produced the same admitted result under injected transient retry as under a single successful attempt. The traces correctly differed in work calls, retries, and attempts.

The deliberately non-idempotent legacy operation demonstrated the opposite: if an external increment occurs before a transient error is observed, a retry increments twice. Declaring the effect as non-idempotent causes the P06 runtime to refuse the policy before any mutation.

Capture does not alter this conclusion. It can record the ambiguous first attempt and later replay it, but it cannot retroactively provide an external idempotency key or transaction.

## 6.8 Cache result

Correct cache hits and misses agree under semantic projection. Cache hits avoid fresh admission and fresh meters. Corrupt cache content produces a visible error rather than a zero value or silent live fallback.

The result is conditional on P01-style complete semantic identity. P06 does not prove that every production cache key is complete; it provides the operational test surface and reuses the earlier semantic identity work.

## 6.9 Budget result

Budget exhaustion returns a stopped report with `stop_reason=budget-exhausted`. It does not report a successful empty result. The trace may show operations attempted before the refusal, but P06 does not promote those partial attempts to a complete semantic result.

This distinction matters for later closure and retrieval projects. A caller may decide that a partial state is sound and useful, but that is a domain decision and must be labeled as partial completeness rather than inferred from executor success.

## 6.10 Benchmark results

| Benchmark, 100 inputs | ns/op | B/op | allocs/op |
| --- | ---: | ---: | ---: |
| Pure sequential | 537,109 | 311,209 | 4,603 |
| Pure parallel, 8 workers | 421,766 | 312,442 | 4,619 |
| Aligned bulk, size 20 | 352,545 | 311,002 | 4,646 |
| In-memory cache hits | 451,867 | 329,241 | 3,919 |
| Captured generation replay | 1,327,649 | 897,374 | 8,949 |

**Supported empirically:** in this small local benchmark, bulk and cache-hit execution were faster than sequential pure execution, while exact attempt replay had substantially higher allocation and time overhead. These numbers include report/identity construction and use an in-memory reference recorder. They do not predict network-bound provider throughput.

The allocation profile indicates that the semantic trace layer is not free. A production deployment may choose sampling, compressed traces, or a more efficient recorder after preserving the identity and schema contracts.

# 7. Counterexamples and falsified stronger claims

## 7.1 Display name is not identity

**Stronger claim:** one report record per step name is sufficient.

**Counterexample:** two distinct functions named `transform` appear in one pipeline. The supplied report aggregates them and cannot say which stage retried or failed.

**Result:** falsified. Name remains presentation only.

## 7.2 Response length does not prove batch alignment

**Stronger claim:** if a batch returns `len(outputs) == len(inputs)`, it preserves per-item semantics.

**Counterexample:** reverse the output slice while keeping type and length correct.

**Result:** falsified. The runtime can enforce cardinality but mapping remains an adapter contract unless explicit IDs are returned.

## 7.3 Waiting is not snapshot access

**Stronger claim:** a barrier makes an item function suitable for global top-k.

**Counterexample:** each item independently appears locally maximal after the barrier.

**Result:** falsified. `Snapshot` is required.

## 7.4 Capturing an effect is not exactly-once execution

**Stronger claim:** recording attempts makes any retry safe.

**Counterexample:** external mutation commits, response is lost, recorder observes an error, retry repeats mutation.

**Result:** falsified. The contract rejects automatic retry; external idempotency or transaction semantics are required.

## 7.5 Equal full reports are not the right transparency criterion

**Stronger claim:** transparent policy variants should have byte-identical reports.

**Counterexample:** a cache hit and a live call return the same value but correctly differ in work calls and cache state.

**Result:** falsified. Compare semantic projection and separately inspect expected operational differences.

## 7.6 Completion order must not assign semantic labels

**Stronger claim:** a mutex is sufficient to make concurrent admission deterministic.

**Counterexample pattern:** assign citation labels or limited slots as workers finish. The lock prevents races but lets scheduling choose winners.

**Result:** not reintroduced in P06. The report and result APIs preserve input/logical identity; completion-order observers remain explicitly operational. Later evidence selection should merge candidates first and assign labels afterward, consistent with P03.

# 8. Contract-by-contract assessment

The full catalog is in `contract-catalog.md`. The implementation-level disposition is summarized here.

| Feature | Disposition | Required precondition |
| --- | --- | --- |
| Worker count | Transparent | Item-local, schedule-independent callback; aligned result slots |
| Retry | Transparent conditionally | Pure/read-only/idempotent stable request; classifier and failure policy fixed |
| Non-idempotent retry | Rejected | Use one attempt or external idempotency/transaction protocol |
| Result cache | Transparent conditionally | Complete semantic key; valid schema/value; declared corruption behavior |
| Effect capture/replay | Reproduces attempts | Canonical semantic key/payload; observation freshness not claimed |
| `Bulk` | Transparent conditionally | Correct one-to-one mapping and equivalent per-item meaning |
| `Batched` repair | Transparent conditionally | Correct grouping/split/repair equivalence and shared budget semantics |
| Rate limiting | Usually operational | No deadline/cancel/freshness change caused by delay |
| Budget | Intentionally non-transparent | Stop reason must be explicit; partiality is domain-labeled |
| Fail-fast | Intentionally changes completion | Part of public failure contract |
| Quarantine | Transparent only to enriched outcome | Quarantine is retained as semantic data |
| Skip | Intentionally loses an item | Caller explicitly accepts skip semantics |
| Temporal `Barrier` | Execution-order only | No assumption of collection access |
| `Snapshot` | Global aligned operation | Complete immutable declared input; one output per input |
| Ledger | Operational observer | Reliable append; failure intentionally stops run |
| `OnResult` | Operational callback | Idempotent/order-independent if it performs durable effects |
| Report v1 projection | Compatible but lossy | Not used for exact stage/operation attribution |

# 9. Compatibility and migration

## 9.1 Source compatibility

Existing steps compile with zero-value contracts. Defaults are:

```text
effect = unknown
locality = item-local
```

Existing names remain visible. Existing `Report.Step(name)` consumers continue to receive aggregated counts. Existing `Pipe`, `Bulk`, and `Batched` call shapes remain available.

## 9.2 Behavioral changes

The following are intentional behavioral changes:

- explicit non-idempotent steps with multiple attempts are rejected;
- `EffectCaptured` steps require a recorder and capture codec;
- stopped runs carry explicit status and stop reason;
- new report consumers can distinguish repeated stages and attempts;
- bulk replay no longer counts fresh provider meters;
- snapshot-global claims cannot be made by an item-local step.

Legacy steps classified `unknown` retain old permissiveness. This is a migration compromise, not a recommendation to leave them unaudited.

## 9.3 Report migration

The recommended transition is:

1. serialize `flow-report/v2` for new runs;
2. keep `steps` while dashboards migrate;
3. use `stages` for stage metrics and `operations/attempts` for causality;
4. project v2 through `Legacy()` only at old API boundaries;
5. when importing a v1 report, use `UpgradeLegacyReport()` and preserve `migration_losses`.

A v1 report cannot recover operation or attempt identity. Any migration tool claiming otherwise would fabricate causality.

## 9.4 Step migration

For each production step:

1. assign an explicit `StepID` from stable domain and version;
2. audit whether it is pure, read-only, idempotent, or non-idempotent;
3. state item-local versus snapshot-global locality;
4. identify the complete semantic request key;
5. add a capture codec for external observations;
6. run baseline, worker, cache, retry, and batch variants through `flowtest`;
7. retain at least one negative-control fixture.

## 9.5 Recommended initial production targets

The generation and embedding adapters are suitable first targets because they are read-only effect-shaped calls with existing semantic cache keys. Tool calls that mutate external systems should not be migrated to automatic retry until each tool has an idempotency contract.

# 10. Composition with the broader RAG semantics program

P06 is designed to compose with other projects through artifacts, not branch dependencies.

## P01 semantic identity

P01 request fingerprints are the preferred `SemanticKey` values for capture. P06 detects byte mismatch but does not define which request fields are semantically relevant.

## P02 provenance

A derivation can refer to P06 operation/attempt trace records when external observations must be audited. Trace IDs should not be embedded in canonical fact identity unless the observation itself is part of the fact's derivation contract.

## P03 lawful merge

P03 candidate/fact merge should occur independently of worker completion. P06 guarantees aligned outputs and trace identity, while P03 supplies schedule-independent state merge. Completion-order labels should remain outside both cores.

## P05 closure

Each rule invocation can run as a P06 logical operation. Schedule-independent closure requires both P05 monotone rule semantics and P06 transparent execution. A stopped budget report should map to a partial closure certificate, not a false fixed point.

## P08 connected retrieval

Baseline and knowledge retrieval branches can execute concurrently. `flowtest` can compare concurrent and sequential plans after P03 merge. Fusion/top-k should occur after an explicit snapshot boundary.

## P09 tools

Read-only tools can use captured attempts for deterministic replay. Mutating tools require declared idempotency keys or transaction protocols before retry. P06 operation traces can support citation and action audits.

## P10 experiments

P10 bundles can store `flow-report/v2`, `operation-trace/v1`, and captured-effect snapshots next to semantic outputs. Replay should verify capture digests and report structural identity before comparison.

# 11. Security and integrity considerations

The reference recorder may contain prompts, query payloads, provider responses, error text, and model output. A production implementation must address:

- secret and personal-data redaction before persistence;
- encryption at rest and access control;
- tenant separation in semantic keys and storage paths;
- retention and deletion policy;
- content-digest verification;
- atomic publication and crash consistency;
- schema/version migration;
- replay authorization;
- malicious or oversized JSON payloads;
- error messages that accidentally contain credentials.

The current `Memory` recorder and file snapshot are research artifacts. They use a restrictive file mode and atomic rename but do not fsync the file or parent directory, encrypt content, or enforce multi-tenant policy.

Stable IDs are hashes, not authorization tokens. A caller who knows an ID must not automatically gain access to the corresponding capture or report.

# 12. Limitations

1. The complete declared-toolchain module suite was not run.
2. Production provider tests were not executed; adapters compile only in the compatibility harness.
3. Effect declarations are auditable claims, not compiler-verified properties.
4. The finite schedule and partition checks are exhaustive only for their stated sizes.
5. The conformance harness cannot prove semantic equality for arbitrary domain values without a correct equality/projection function.
6. Exact capture replay reproduces old observations; it does not assert they remain current or factually correct.
7. The in-memory recorder is not a production distributed log.
8. Report validation cannot prove that every semantic key is complete.
9. Generic bulk execution cannot detect same-length response permutation without explicit IDs.
10. Timing, scheduler interleavings, and live-provider nondeterminism remain intentionally outside deterministic semantics.
11. A global `Snapshot` materializes the complete collection and may be unsuitable for very large streams; a future windowed or external-sort contract would need separate semantics.
12. Benchmarks are local microbenchmarks without network latency or provider quotas.

# 13. Answers to the assignment questions

## What does a `flow.Step` mean?

A typed logical operation interpreted by the executor under an explicit effect and locality contract. It yields aligned semantic outcomes and a separate operational trace. For captured effects, the exact offline meaning is a deterministic function over recorded attempt observations.

## Which policies were transparent, and under what preconditions?

Workers, cache, retry, and batching were transparent for compliant item-local operations with complete identity, correct batch mapping, lawful effect repetition, stable classification, and no intentional stop. Rate limiting was operational only when delay did not trigger cancellation or change freshness. Budget exhaustion, skip, and fail-fast intentionally changed completion and were made explicit.

## Which current combinator violated or hid an expected contract?

The original report conflated repeated display names. `Bulk` had a necessary but unenforceable positional-order precondition; same-length permutation is a concrete counterexample. `Barrier` was sometimes described as supporting cross-item state although its API did not provide the complete collection.

## How should identities be represented?

`StepID` for stable definition, `StageID` for placement, `OperationID` for logical request, `AttemptID` for retry attempt, `BatchID` for physical group call, and `Name` for display only.

## Where are explicit barriers necessary?

Before any operation whose result depends on the full candidate set: global top-k, normalization, diversification, cross-item deduplication, and similar selection. In P06 this is represented by `Snapshot`, not merely `Barrier=true`.

## How much can be replayed?

Every attempted external call that passes through a capture codec and recorder can be replayed by semantic request key and attempt number, including classified errors. Cache hits, uncaptured callbacks, hidden side effects, and external mutations outside the adapter cannot be reconstructed.

## What should change in `flow.Report`?

Adopt v2 with run status, stop reason, stages, operations, attempts, cache/replay/batch linkage, and structural validation. Retain the old name map only as a marked lossy compatibility view.

# 14. Recommendations

## Immediate

- Merge `effectlog`, ID types, `Contract`, report v2, trace schema, `flowtest`, and `Snapshot` after declared-toolchain validation.
- Keep all legacy steps at `EffectUnknown` until individually audited.
- Require explicit `StepID` for new production steps.
- Store v2 reports and operation traces in experiment artifacts.
- Add semantic baseline comparisons to every provider bulk adapter.

## Near term

- Add P01 fingerprints as standard capture semantic keys.
- Add an OpenTelemetry adapter that maps the identity hierarchy without replacing it.
- Define secret-redaction hooks for captured payloads and outcomes.
- Introduce a durable recorder with transactional publication and tenant-aware access control.
- Add provider response IDs to embedding/tool batch adapters where APIs support them.
- Add CI under Go 1.26.5 for the full module.

## Not recommended

- Do not infer retry safety from capture alone.
- Do not use display names as map keys for exact metrics.
- Do not assign semantic labels or budgets by completion order.
- Do not treat a temporal barrier as a collection API.
- Do not introduce a general workflow DSL to solve these local contracts.

# 15. Conclusion

P06 turns `flow` from an executor with several implicit assumptions into an executor with inspectable, testable contracts. The implementation does not attempt to eliminate effects or operational variance. It makes them explicit, records them, and states when they may be changed without changing the result.

The most useful outcome is not one new abstraction. It is the separation of concerns:

```text
semantic request identity
semantic aligned outcome
operational policy
external attempt observation
trace identity
collection locality
```

With those boundaries, retry, caching, batching, parallelism, and replay can be tested independently and then composed with the canonical fact, merge, closure, retrieval, tool, and experiment projects. The result remains ordinary Go, but with contracts strong enough to support adversarial tests and later formal composition.

# Appendix A. Artifact index

| Artifact | Purpose |
| --- | --- |
| `README.md` | Build and hand-off overview |
| `design.md` | Semantic design and rejected alternatives |
| `api.md` | Public API examples |
| `contract-catalog.md` | Combinator and policy preconditions |
| `standalone/` | Executable reference model |
| `adapter/` | Actual rag-ttc conformance and fault tests |
| `fixtures/` | Nine neutral counterexamples/scenarios |
| `schemas/` | Capture, trace, report, fixture, and result schemas |
| `results/raw/test-output.txt` | Race-enabled test output |
| `results/raw/vet-output.txt` | Vet output |
| `results/raw/experiment-summary.json` | Primary finite experiment summary |
| `results/raw/benchmarks.txt` | Local benchmark output |
| `results/raw/captured-effects.json` | Two-attempt offline replay snapshot |
| `results/raw/sample-flow-report.json` | Non-conflating report sample |
| `results/raw/sample-operation-trace.jsonl` | Eighteen trace events |
| `results/raw/schema-validation.json` | Artifact validation summary |
| `results.json` | Shared machine-readable project result |
| `demo.sh` | Offline reproduction entry point |

# Appendix B. Neutral fixtures

| Fixture | Property or failure |
| --- | --- |
| `repeated-display-name.json` | Display-name report collision |
| `reversed-bulk-order.json` | Same-length batch permutation |
| `partial-batch-response.json` | Positional cardinality failure |
| `ambiguous-non-idempotent-retry.json` | Duplicate external mutation risk |
| `captured-retry-sequence.json` | Attempt-preserving offline replay |
| `snapshot-global-barrier.json` | Temporal barrier versus complete snapshot |
| `semantic-key-payload-collision.json` | Incomplete capture key detection |
| `corrupt-cache.json` | Visible cache decode failure |
| `budget-stop.json` | Explicit incomplete execution status |

# Appendix C. Selected source references

The following references are to the implemented snapshot:

- `pkg/effectlog/id.go:32-53` - definition, stage, operation, attempt, and batch ID derivation.
- `pkg/effectlog/log.go:46-126` - requests, outcomes, events, captures, and snapshots.
- `pkg/effectlog/log.go:220-344` - live/capture/replay execution and single-flight behavior.
- `pkg/effectlog/log.go:345-408` - portable snapshots, strict I/O, and replay loading.
- `pkg/flow/semantics.go:44-121` - effect/locality contracts and validation.
- `pkg/flow/semantics.go:129-209` - capture codecs and invocation context.
- `pkg/flow/run.go:314-354` - top-level typed run and result alignment.
- `pkg/flow/report.go:80-166` - run, stage, operation, and attempt report types.
- `pkg/flow/report.go:338-407` - structural validation.
- `pkg/flow/bulk.go:25-35` - explicit bulk ordering precondition.
- `pkg/flow/snapshot.go:18-52` - collection-level constructor.
- `pkg/flowtest/compare.go:92-151` - metamorphic comparison engine.
- `pkg/rag/generation/flow_step.go:49-68` - generation read-only/capture declaration.
- `pkg/rag/embedding/cached.go:102-126` - embedding read-only/capture declaration.

# Appendix D. Background references

- Claessen, K. and Hughes, J. "QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs." ICFP, 2000.
- Herlihy, M. and Wing, J. "Linearizability: A Correctness Condition for Concurrent Objects." ACM TOPLAS, 1990.
- Lamport, L. "Time, Clocks, and the Ordering of Events in a Distributed System." Communications of the ACM, 1978.
- Ajmani, S. "Go Concurrency Patterns: Pipelines and Cancellation." The Go Blog, 2014.
- The Go Authors. "The Go Memory Model."
- Hellerstein, J. and Alvaro, P. "Keeping CALM: When Distributed Consistency is Easy." Communications of the ACM, 2020.

These works motivate testing laws, identity and ordering, cancellation, and the distinction between monotone data semantics and operational scheduling. P06 does not claim to re-prove their general results.
