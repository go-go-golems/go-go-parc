# A Pragmatic Workflow Builder and Execution Framework for Go and Goja

## Fresh architecture, API specification, and implementation manual

**Project context:** `go-go-golems/scraper`  
**Design date:** 2026-07-28  
**Audience:** a developer joining the project to implement a replacement framework from first principles  
**Status:** proposed clean-slate design; not a compatibility specification for the existing engine

---

## Preface

This document has two purposes.

First, it explains the current scraper workflow architecture well enough to make an informed judgment about its complexity. The current code is not dismissed as “bad” or “unnecessary.” Much of it encodes hard-won correctness properties: durable state, retries, lease ownership, stale-worker fencing, dependency recovery, artifact custody, and observable run history. The problem is that several different products and operational levels have accumulated behind one conceptual front door. A developer who merely wants to compose three tasks now encounters abstractions designed for distributed workers, hot implementation rollout, resource accounting, sandboxing, and research evidence systems.

Second, this document specifies a new framework that starts from the smallest useful contract and grows by adapters. The same canonical workflow plan is authored from Go or JavaScript. The same task registry and executor run it. In-memory execution is the default. SQLite durability is optional. Multi-process leasing, isolation, and durable rate accounting are later extensions rather than prerequisites.

The intended outcome is not a thinner facade over the existing engine. It is a new package with a smaller semantic center.

### Review scope

The source-level review covered:

- `go-go-golems/scraper` at main commit `803a28ef4e85eb2c12eea4b2ccc8ff3dd4c2dc27`;
- the public `pkg/workflow` facade, lower-level engine model, scheduler, SQLite store, runners, JavaScript APIs, site manifests, and representative Hacker News workflow;
- the project map and linked reports in `go-go-golems/go-go-parc`, especially the workflow API, resumability hardening, Workflow V3, Book OCR, and later RAG simplification reports;
- the Workflow V3 research branch in `wesen/scraper`, reviewed in the linked project material at head `202229464629e2b6d0e193ff7798b16770b3a270`;
- the current Goja module and runtime-factory patterns in `go-go-golems/go-go-goja` around commit `c265ae037c319aa90fd9c6c4e3818a2f6c9bd15e`.

This was a static source and design review. The test suite was not independently executed in the review environment because the repository could not be cloned there. Existing test code and project reports were inspected, but claims about runtime behavior should still be revalidated during implementation.

---

# Part I — Diagnosis

## 1. Executive conclusion

The codebase is overengineered **as the minimum reusable workflow API**, but not necessarily overengineered **for every operational problem it has attempted to solve**.

That distinction matters.

The existing system has accumulated at least five concerns:

1. a workflow authoring model;
2. a local task executor;
3. a durable and potentially multi-worker scheduler;
4. scraper-specific site, HTTP, database, CLI, and projection behavior;
5. a research-oriented execution platform with exact implementation identities, budgets, gates, isolation, artifacts, and evidence projections.

Each concern can be valid. The overengineering appears when all five are presented as one inseparable model. The current public `pkg/workflow` package reduces some syntax, but it still translates directly into lower-level engine operations and exposes many engine-era concepts. Workflow V3 improves important boundaries, especially compact artifacts and exact task identities, but moves still more advanced mechanisms into the base vocabulary.

The clean replacement should therefore follow this rule:

> A workflow framework should make a local three-step DAG trivial, a restartable SQLite-backed DAG straightforward, and a distributed fenced executor possible without forcing all three users to learn the same operational machinery.

The proposed design has one canonical `Plan`, one task `Handler` contract, one execution state machine, and one JavaScript-to-plan boundary. Durability and hosting are adapters around that core.

### The main recommendation

Create a new standalone module, provisionally:

```text
github.com/go-go-golems/workflow
```

The scraper application imports this module. The workflow module must not import scraper packages, site concepts, Glazed/Cobra, database modules, browser code, provider code, or the scraper engine.

The new module should initially support four progressively optional levels:

| Level | Capability | Required concepts |
|---|---|---|
| 0 | Build, validate, serialize, and digest plans | plan, step, task, reference |
| 1 | Execute in memory in one process | registry, handler, run, attempt |
| 2 | Resume locally with SQLite | repository, recovery, events |
| 3 | Coordinate multiple processes | lease, heartbeat, fencing |
| 4 | Execute untrusted or remote work | process/container/remote adapter |

A user should learn only the level being used.

---

## 2. What the current codebase actually is

At first glance scraper appears to be a web-scraping application. Internally it is a durable workflow system whose original domain still shapes its abstractions.

The core path is approximately:

```text
site manifest or Go package
        |
        v
submission-time Go or JavaScript
        |
        v
workflow + operation rows in SQLite
        |
        v
scheduler refreshes dependency state
        |
        v
queue candidate selection and transactional lease
        |
        v
runner registry chooses js or http/fetch or public executor adapter
        |
        v
runner reads dependencies, site database, scraper database, artifacts
        |
        v
atomic completion/failure plus emitted child operations
        |
        v
workflow status refresh, events, snapshots, projections
```

### 2.1 Lower-level engine

The lower engine owns:

- workflows and operations;
- required and optional dependencies;
- operation statuses, retry state, and next-attempt deadlines;
- site and queue identity;
- queue concurrency and durable token-bucket rate limits;
- leases, heartbeats, and stale-completion protection;
- results, records, inline artifacts, and dynamically emitted operations;
- workflow-level status derivation;
- observers and durable snapshots.

This is a meaningful operational subsystem, not a simple function runner.

### 2.2 Public workflow facade

`pkg/workflow` exposes friendlier names such as `Runtime`, `Package`, `Entrypoint`, `RunBuilder`, `Executor`, and `StepContext`. It is explicitly a facade over the engine rather than an independent model.

That choice kept implementation effort low and preserved engine correctness. It also means the public package inherits the engine’s shape:

- a runtime requires a store configuration;
- the built-in path is SQLite-first;
- a package entrypoint creates lower-level operation specifications;
- a step has a queue, site, deduplication key, retry model, parent, and dependency objects;
- a step context exposes workflow, operation, lease, scheduler time, dependency results, records, artifacts, projections, and child operation emission;
- executors are adapted back into the runner registry;
- projections and scraper/site databases remain nearby.

The facade is easier than direct scheduler use, but it does not establish a small domain-neutral workflow kernel.

### 2.3 JavaScript site layer

The JavaScript API has two phases:

- submission scripts create the first durable operations;
- worker scripts execute operations and may emit more operations.

Scripts author raw scheduler-shaped objects. A typical `ctx.emit()` call names:

- operation ID;
- runner kind, such as `js` or `http/fetch`;
- queue;
- deduplication key;
- dependencies;
- retry configuration;
- metadata containing the execution script;
- parent, site, and workflow overrides.

Execution scripts can also read dependency result envelopes, including artifact bodies, and access generic site and scraper databases. This is powerful, but it makes JavaScript authors responsible for infrastructure details that a workflow builder should normally hide.

### 2.4 Workflow V3 research path

Workflow V3 reacts to genuine failures in the earlier system:

- source-bearing JSON was copied into operation rows, producing extreme SQLite and WAL growth;
- fixed-cycle scheduling left independent resources idle while slow tasks held a batch open;
- symbolic task names did not pin exact JavaScript implementation bytes;
- artifacts and credentials needed a stricter control-plane boundary.

Its response introduces:

- mutable JavaScript builder state;
- normalized workflow IR;
- a task catalog;
- compiled plans;
- task bundles and bundle digests;
- implementation ABI identity;
- module aliases;
- sealed registry generations;
- resource classes;
- retries and append-only attempts;
- leases and cancellation epochs;
- content-addressed artifact references;
- maps, reductions, gates, budgets, and isolation policies;
- external-operation evidence;
- deterministic observation projections;
- restricted subprocess execution.

These mechanisms are individually defensible under the right forces. Together they are too large a minimum model for an embeddable workflow package.

---

## 3. Where the overengineering comes from

Overengineering is not measured by file count alone. It occurs when the conceptual and operational cost paid by ordinary users exceeds the risks their workload actually has.

### 3.1 Product layers do not vary independently

The current runtime constructor and task context combine concerns that should be independently selectable:

- persistence backend;
- scheduler configuration;
- worker identity;
- queue policy;
- artifact storage;
- projection storage;
- operator services;
- site database access;
- JavaScript runner hosting.

A local command that wants to run two Go functions should not need to understand the same constructor as a multi-process scraper worker.

### 3.2 Scraper vocabulary leaks into the reusable model

`SiteName`, site databases, scraper databases, queue keys, records, and per-site projections are valid scraper concepts. They are not universal workflow concepts.

A reusable task should receive its input and explicit dependencies. A Hacker News parser that needs a repository should capture a `StoryRepository` in its handler constructor. The workflow engine should not provide a generic “site DB” service locator to every task.

### 3.3 The builder emits persistence objects too early

The current Go `RunBuilder.Step` and JavaScript `ctx.emit()` effectively construct persisted operation rows. This collapses three different stages:

1. author intent;
2. validated workflow structure;
3. mutable run state.

The result is that authoring must know queue fields, parent IDs, retry row shapes, and runner kinds. It also makes validation fragmented: many errors appear only after submission or lease time.

### 3.4 The simplest execution mode is not the default

The current public runtime begins with a durable store. That is appropriate for production scraping but not for a general package.

A new user should be able to write:

```go
result, err := workflow.Run(ctx, plan, input,
    workflow.Tasks(registry),
)
```

without creating a database, worker identity, poll interval, queue configuration, artifact root, or command host.

### 3.5 Control plane and data plane remain mixed

The older schema can store artifact bodies in the engine database. Dependency envelopes can expose artifact body text directly to JavaScript. Step outputs and emitted operation inputs are arbitrary JSON.

This makes it easy to move source documents, HTML, prompts, or model payloads through scheduler rows. Workflow V3 correctly identifies this as both a size and privacy problem, but its complete solution introduces a large platform model. A smaller framework can retain the essential rule—large bytes live in an artifact store—without adopting every V3 mechanism.

### 3.6 Persisted derived state increases transition complexity

`ready` and `blocked` are useful operator views, but they can be derived from:

- the step’s terminal or pending state;
- dependency states;
- retry deadline;
- run cancellation.

Persisting every derived state requires refresh loops and repair transitions. The proposed v1 stores only fundamental state and derives readiness and blockedness in queries and snapshots.

### 3.7 JavaScript object identity is used as compiler state

The V3 authoring implementation maintains maps keyed by `*goja.Object` for references, sets, tasks, jobs, workflows, and plans, plus an active build pointer. That design can enforce handle provenance, but it tightly couples the workflow compiler to one Goja runtime and substantially expands the binding code.

A data-only authoring DSL does not need this. JavaScript can construct a plain JSON plan, then submit that JSON to one strict native normalization function. The compiler validates semantics; JavaScript object identity carries no authority.

### 3.8 Advanced reliability mechanisms are exposed before basic portability

Workflow V3 offers bundle generations, budgets, gates, isolation ceilings, and external-operation accounting before an ordinary user can point a step at a pinned command, Python script, or container image through a simple standard adapter.

This is a product-ordering problem. The hardest internals were developed before the most ordinary front door.

---

## 4. What should be preserved

A clean-slate design should not erase the correctness lessons already learned.

### 4.1 Numeric database time

Every time used for ordering or comparison in SQLite should be stored as an integer, preferably UTC epoch microseconds. RFC3339 strings remain useful for logs and external JSON, but variable-width timestamp text is not a safe database ordering representation.

### 4.2 Atomic state transitions

Starting an attempt, completing an attempt, publishing compact output references, adding dynamic steps, and updating terminal run state require explicit transaction boundaries.

### 4.3 Append-only attempts

A retry must not overwrite its predecessor. Operators need to see that attempts 1 and 2 failed and attempt 3 succeeded.

### 4.4 Structured failure classification

Failures need stable codes and a retryability decision. Free-form error strings are diagnostic detail, not control flow.

### 4.5 Durable ownership when multiple workers exist

When more than one process may execute a step, a lease token is an ownership proof. Completion and failure must be fenced by the current, unexpired token. The handler itself should not see the token.

### 4.6 External effects remain at-least-once

A workflow engine can prevent a stale worker from committing authoritative state. It cannot retroactively cancel an HTTP request, provider call, database transaction, or email already sent.

Every side-effecting task therefore needs a stable operation key and a domain idempotency strategy. The engine should provide the key; the handler must use it where the external system permits.

### 4.7 Store state is authoritative; notifications are projections

An observer is informed after commit. Observer failure must not roll back or corrupt the run. A dashboard reconstructs current truth from a snapshot, not from an assumption that it received every in-process event.

### 4.8 Completion-driven scheduling

The scheduler should refill capacity when any task finishes. It should not lease a batch and wait for the slowest member before admitting unrelated ready work.

### 4.9 Bounded dynamic expansion

Data-dependent fan-out is useful for pagination, discovered document pages, and extraction subwork. It must be bounded and committed atomically with the parent result.

### 4.10 Artifact references, not artifact bodies

Large and sensitive bytes belong in an external, streaming artifact store. Workflow state contains compact references with digest, media type, and size.

### 4.11 Goja runtime ownership

A Goja runtime is single-owner state. Work may happen in Go goroutines, but resolution back into JavaScript must be posted through the runtime owner/event loop. No Goja value should survive plan compilation.

---

## 5. Mechanisms to defer

The following features should not be in the initial core. They may be added later behind explicit adapters or profiles.

| Mechanism | Add it only when |
|---|---|
| Registry generations | live workers must hot-switch implementations while old attempts drain |
| Exact source bundle digests | historical byte-for-byte task reconstruction is a product requirement |
| Durable token buckets | multiple processes must share provider admission state |
| Budget ledgers | paid or scarce effects need transactional reservation and settlement |
| Approval gates | a run must durably pause for human authorization |
| Map materializers | fan-out is too large to return as one bounded fragment |
| Reduction trees | aggregate input cannot be processed by one bounded task |
| Bubblewrap/cgroups | semi-trusted code must run locally with OS isolation |
| Remote/distributed executors | one SQLite host and one worker process are insufficient |
| Canonical evidence projection | a downstream research system requires a stable redacted evidence schema |
| Hot plugin quarantine | candidate implementations can be activated without process restart |

The first release should leave extension points for these forces without pretending to solve them.

---

# Part II — Design principles

## 6. Architectural laws

The implementation should treat the following as enforceable laws, not aspirational style advice.

### Law 1 — One canonical plan

Go, JSON, YAML tooling, and JavaScript all produce the same `Plan` schema. There is no mandatory sequence of builder state, IR, catalog, compiled plan, and run plan.

A builder is temporary syntax. `Plan` is the durable definition.

### Law 2 — Plans contain data, never authority

A plan may contain task references, values, references, retry policy, timeouts, lanes, and metadata. It may not contain:

- Go functions;
- Goja values or callbacks;
- database handles;
- credentials;
- HTTP clients;
- filesystem handles;
- worker identities;
- lease tokens;
- open readers;
- process-global registry pointers.

### Law 3 — The core depends only on the Go standard library

The root module’s core package should use standard-library packages. SQLite, Goja, OpenTelemetry, Prometheus, Redis, Glazed, and scraper integrations live in subpackages or downstream applications.

### Law 4 — Local execution is the reference semantics

The in-memory executor is not a toy. It defines the state-machine behavior used by durable adapters. SQLite changes persistence, not workflow meaning.

### Law 5 — Readiness is derived

A pending step is runnable when:

- its retry deadline is due;
- the run is not canceled;
- all dependencies have succeeded;
- the selected executor has capacity;
- its task implementation exists.

`ready` and `blocked` are snapshot views, not essential stored states.

### Law 6 — Handlers receive domain input, not engine internals

A task handler receives resolved JSON input, stable run and step identity, attempt number, a logger, artifact access, and a stable idempotency key. It does not receive the repository, lease token, scheduler, site DB, scraper DB, or operator service.

### Law 7 — Dependencies are inferred from data references

When step B reads step A’s output, B depends on A. Authors should not have to repeat the same edge manually.

An explicit `After` edge exists only for ordering without data flow.

### Law 8 — Completion is atomic

The following durable facts are committed together:

- attempt success;
- compact task output;
- dynamic fragment, if any;
- step success;
- resulting run transition;
- associated durable events.

### Law 9 — Artifacts stream outside the repository

The repository never accepts a large `[]byte` artifact body. The artifact interface uses `io.Reader` and `io.ReadCloser`.

### Law 10 — Optional operational levels do not pollute authoring

A plan does not change because it runs in memory, in local SQLite, or through a leased multi-process adapter. Operational deployment policy belongs to engine configuration and task adapters.

### Law 11 — No ambient JavaScript authority

The authoring module is data-only. Task runtimes receive only explicitly registered modules. `process.env`, generic filesystem, generic database, network, and command execution are opt-in capabilities.

### Law 12 — Process restart is the default deployment update

The initial registry is immutable for the life of an engine. Updating task implementations means constructing a new engine or restarting the process. Hot generations are not part of v1.

---

## 7. Goals and non-goals

### 7.1 Goals

The v1 framework must:

- make a linear Go workflow fit comfortably on one screen;
- represent static DAGs with data references and ordering edges;
- execute tasks concurrently with global and per-lane bounds;
- refill capacity immediately after each completion;
- support retries, deadlines, cancellation, structured errors, and append-only attempts;
- support bounded dynamic expansion;
- expose deterministic in-memory stepping for tests;
- offer a SQLite repository that survives process restart;
- keep large bytes in a streaming artifact store;
- let Go and Goja author identical canonical plans;
- expose execution to Goja without duplicating the engine;
- support JavaScript task handlers through a separate adapter;
- produce useful snapshots and post-commit events;
- remain understandable to a new developer without prior scraper knowledge.

### 7.2 Non-goals for v1

The first release does not promise:

- exactly-once external effects;
- hostile-code sandboxing;
- automatic Kubernetes, cloud, or HPC dispatch;
- hot task implementation rollout;
- a distributed consensus scheduler;
- durable cross-process rate accounting;
- transactional money budgets;
- human approval gates;
- a generic map/reduce language;
- a schema registry;
- automatic cache/materialization reuse;
- a universal secrets system;
- compatibility with old scraper database rows;
- automatic translation of Workflow V3 plans;
- a graphical workflow editor.

These omissions are deliberate scope control.

---

## 8. Proposed package layout

The initial repository should be organized around one root package and a small number of adapters.

```text
workflow/
├── plan.go                 # Plan, StepSpec, TaskRef, Ref, Value
├── builder.go              # Go builder and handles
├── normalize.go            # strict validation and normalization
├── digest.go               # canonical plan digest
├── registry.go             # task registry copied into Engine
├── handler.go              # Handler, typed adapters, TaskContext, Result
├── errors.go               # TaskError and classification
├── expansion.go            # bounded Fragment builder and validation
├── state.go                # run, step, attempt states and snapshots
├── repository.go           # high-level persistence contract
├── memory_repository.go    # reference implementation
├── engine.go               # Submit, Run, Resume, Serve, Tick
├── scheduler.go            # completion-driven dispatch loop
├── retry.go                # deterministic backoff
├── event.go                # durable event shape and observer boundary
├── artifact.go             # ArtifactRef and ArtifactStore interfaces
├── file_artifacts.go       # optional stdlib file CAS implementation
├── clock.go                # real and fake clock contracts
├── limits.go               # global/lane/expansion bounds
└── internal/
    ├── strictjson/
    └── jsonpointer/

workflow/sqlite/
├── store.go
├── claim.go
├── completion.go
├── snapshot.go
├── migrations.go
├── schema.sql
└── sqlite_test.go

workflow/goja/
├── authoring.go            # require("workflow")
├── authoring.js            # data-only JS builder implementation
├── runtime_module.go       # require("workflow/runtime")
├── js_handler.go           # JS module as a task Handler
├── conversion.go
├── workflow.d.ts
└── goja_test.go

workflow/distributed/       # explicitly later
├── repository.go
├── lease_supervisor.go
└── fencing_test.go

integrations/scraper/       # preferably in scraper repository, not core
├── http_task.go
├── js_site_task.go
├── cli.go
└── legacy_inspection.go
```

The root package is intentionally usable by itself. A user who does not need SQLite or Goja should not download or initialize them.

---
# Part III — The canonical workflow model

## 9. Core vocabulary

A small vocabulary reduces accidental complexity. Use these terms consistently in code, documentation, logs, and APIs.

### Plan

An immutable, data-only workflow definition. It names tasks, input expressions, dependencies, retry policy, and published outputs. A plan is reusable across runs.

### Run

One execution of a plan with one concrete input document. A run has mutable state.

### Step

One node in the plan. A step references one task implementation by stable logical name and version.

### Task

A reusable operation kind, such as `http.fetch@1`, `html.parse-hackernews@1`, or `book.ocr-page@2`.

A task is not a workflow node. Ten plan steps may invoke the same task with different inputs.

### Handler

The Go implementation registered for a task reference in the current engine process.

### Attempt

One invocation of a step handler. Retries create additional attempts rather than replacing history.

### Reference

A pointer to a value in the run input or in a previous step output.

### Lane

An optional local concurrency class such as `network`, `cpu`, or `provider.openai`. A lane limits concurrent tasks. It is deliberately simpler than a durable queue and token-bucket model.

### Fragment

A bounded set of steps returned by a successful task for dynamic graph expansion. Fragment step IDs are relative to their parent and are namespaced by the engine.

### Artifact

An immutable external object referenced by digest, size, media type, and locator. Artifact bytes are not workflow control state.

### Repository

The high-level persistence boundary for runs, steps, attempts, claims, outputs, and events.

### Engine

The composition root that owns a frozen task registry, repository, artifact store, scheduler limits, clock, and observers.

---

## 10. Plan schema

The canonical plan should remain compact. The following is the recommended public shape. Exact naming may change during implementation, but every additional field requires a concrete use case.

```go
package workflow

type Plan struct {
    Schema   string            `json:"schema"`
    Name     string            `json:"name"`
    Version  string            `json:"version"`
    Steps    []StepSpec        `json:"steps"`
    Outputs  map[string]Ref    `json:"outputs,omitempty"`
    Metadata map[string]string `json:"metadata,omitempty"`
}

type StepID string

type TaskRef struct {
    Name    string `json:"name"`
    Version string `json:"version"`
}

type StepSpec struct {
    ID             StepID            `json:"id"`
    Task           TaskRef           `json:"task"`
    Input          Value             `json:"input"`
    After          []StepID          `json:"after,omitempty"`
    Retry          RetryPolicy       `json:"retry"`
    TimeoutMillis  int64             `json:"timeoutMillis,omitempty"`
    Lane           string            `json:"lane,omitempty"`
    Metadata       map[string]string `json:"metadata,omitempty"`
}
```

The serialized format uses integer milliseconds for durations. Go builder options accept `time.Duration`, but canonical JSON should avoid implementation-specific duration strings.

### 10.1 Schema and version

`Schema` identifies the document grammar, for example:

```text
golems-workflow-plan/v1
```

`Version` is the application-level version of this workflow definition. It is not the schema version and not a task version.

The plan digest is computed from normalized content and does not need to be stored inside the plan itself. Storing a digest inside the value it digests creates awkward self-reference and duplicate validation rules.

### 10.2 Task references

A task reference consists of a name and version:

```go
TaskRef{Name: "http.fetch", Version: "1"}
```

The convenient text form is:

```text
http.fetch@1
```

Both fields are required in a normalized plan. The builder may default a missing version to `1`, but the normalized result is always explicit.

A task reference is a logical compatibility contract. The registry may record an optional implementation identity such as a Git commit, binary build ID, or script digest on each attempt. Exact bundle identity is not mandatory plan syntax in v1.

### 10.3 Step input as an expression tree

A step input is a recursively structured JSON value containing literals and references.

```go
type ValueKind string

const (
    ValueLiteral ValueKind = "literal"
    ValueRef     ValueKind = "ref"
    ValueObject  ValueKind = "object"
    ValueArray   ValueKind = "array"
)

type Value struct {
    Kind    ValueKind        `json:"kind"`
    Literal json.RawMessage  `json:"literal,omitempty"`
    Ref     *Ref             `json:"ref,omitempty"`
    Object  map[string]Value `json:"object,omitempty"`
    Array   []Value          `json:"array,omitempty"`
}
```

This explicit tagged form is preferable internally because it distinguishes a workflow reference from a literal object that merely resembles one. The JavaScript and JSON authoring surfaces may use a concise sentinel representation, but strict parsing must convert it into this type before validation.

### 10.4 References

A reference names a source document and an RFC 6901 JSON Pointer.

```go
type RefSource string

const (
    RefRunInput  RefSource = "input"
    RefStepOutput RefSource = "step"
)

type Ref struct {
    Source  RefSource `json:"source"`
    StepID  StepID    `json:"stepId,omitempty"`
    Pointer string    `json:"pointer,omitempty"`
}
```

Examples:

```json
{"source":"input","pointer":"/baseURL"}
{"source":"step","stepId":"fetch","pointer":"/body"}
{"source":"step","stepId":"parse","pointer":""}
```

The empty pointer selects the complete document.

A reference to a step output implies a required dependency. This is one of the design’s most important simplifications.

### 10.5 Explicit ordering edges

`After` is used only when ordering is required without reading data.

For example, a publication step might need to run after an audit step even though it does not consume the audit output. The author writes:

```go
workflow.After(audit)
```

The normalizer combines inferred data dependencies and explicit ordering dependencies into one internal edge set. Duplicate edges are removed.

### 10.6 Retry policy

The canonical v1 retry policy should be small:

```go
type RetryPolicy struct {
    MaxAttempts         int     `json:"maxAttempts"`
    InitialDelayMillis  int64   `json:"initialDelayMillis,omitempty"`
    MaxDelayMillis      int64   `json:"maxDelayMillis,omitempty"`
    Multiplier          float64 `json:"multiplier,omitempty"`
    JitterFraction      float64 `json:"jitterFraction,omitempty"`
}
```

Normalized defaults:

```text
maxAttempts         = 1
initialDelayMillis  = 1000
maxDelayMillis      = 60000
multiplier          = 2.0
jitterFraction      = 0.0
```

Jitter is disabled by default to maximize deterministic behavior. Production applications may enable it explicitly.

Do not put retryable error codes into the plan. Retryability is a property of the task failure plus the step’s attempt allowance.

### 10.7 Timeout

`TimeoutMillis` limits one handler attempt. Zero means no additional step-specific timeout beyond the parent context.

A timeout does not guarantee that an external effect stops. It cancels the handler context and prevents authoritative completion from an expired or canceled attempt.

### 10.8 Lane

`Lane` is a scheduling hint interpreted by engine configuration. It is not a globally durable queue identity.

Examples:

```text
network
cpu
provider.openai
browser
```

An unknown lane uses the global capacity unless engine configuration rejects unknown lanes. The recommended default is permissive for local execution and strict in production configuration.

### 10.9 Metadata

Metadata is a string map intended for labels, display, and diagnostics. It must not carry task input, credentials, source text, or implementation code.

The normalizer should enforce a configurable total metadata size, with a conservative default such as 16 KiB per plan and 4 KiB per step.

---

## 11. Normalization and validation

The builder is not the trust boundary. Every entry path—Go builder, JSON file, YAML conversion, JavaScript module, HTTP submission—must call the same strict normalization function.

Recommended API:

```go
func NormalizePlan(input Plan) (Plan, Diagnostics)
func ParsePlanJSON(data []byte) (Plan, Diagnostics)
func ValidatePlan(input Plan) Diagnostics
```

`NormalizePlan` returns a deep copy. The engine submits only the normalized copy.

### 11.1 Diagnostic model

Return all independent authoring errors in one pass where practical.

```go
type Severity string

const (
    SeverityError   Severity = "error"
    SeverityWarning Severity = "warning"
)

type Diagnostic struct {
    Severity Severity `json:"severity"`
    Code     string   `json:"code"`
    Path     string   `json:"path,omitempty"`
    Message  string   `json:"message"`
}

type Diagnostics []Diagnostic

func (d Diagnostics) Err() error
func (d Diagnostics) HasErrors() bool
```

Stable codes allow Goja, CLI, and editor integrations to present errors without parsing text.

### 11.2 Required validation

Normalization must verify:

1. known plan schema;
2. non-empty plan name and version;
3. non-empty, unique step IDs;
4. valid task names and explicit versions;
5. exactly one valid value variant at every input node;
6. valid JSON literal bytes;
7. valid RFC 6901 pointers;
8. every step reference names an existing step;
9. no self-reference;
10. all `After` targets exist and are not self-edges;
11. inferred and explicit dependency graph is acyclic;
12. output names are non-empty and unique;
13. published output references are valid;
14. retry fields are within safe bounds;
15. timeout and metadata sizes are within configured limits;
16. plan and step counts are within configured limits.

Task implementation availability is checked by `Engine.Submit` against its registry. Structural plan validation should remain usable without a registry.

### 11.3 Strict JSON decoding

`ParsePlanJSON` should:

- accept exactly one JSON document;
- reject trailing non-whitespace content;
- reject unknown fields;
- reject duplicate object keys if the decoder implementation can detect them;
- impose a maximum document size;
- avoid generic `map[string]any` as the durable representation.

Unknown fields should fail rather than disappear. Silent field loss is dangerous for execution policy.

### 11.4 Cycle detection

Use a standard Kahn topological sort or depth-first color traversal over the normalized edge set.

Kahn’s algorithm has a useful side effect: it can produce a stable topological order for diagnostics and snapshots. For deterministic output, select the next zero-indegree step in lexical ID order.

### 11.5 Deep-copy rule

After `Build` or `NormalizePlan`, caller mutation must not alter the submitted plan.

The simplest enforceable approach is:

1. deep-copy during normalization;
2. deep-copy or canonical-marshal during `Engine.Submit`;
3. expose snapshots and plans as copies;
4. never retain maps or slices owned by a caller.

Go cannot make exported structs physically immutable, but the engine can make its own state independent.

---

## 12. Canonical plan digest

A digest is useful for run identity, audit, cache keys, and regression tests. It should remain one utility rather than a family of mandatory identity layers.

Recommended API:

```go
func PlanDigest(plan Plan) (string, error)
```

Algorithm:

1. normalize the plan;
2. remove non-semantic display-only fields only if the contract explicitly declares them non-semantic;
3. sort steps by ID for digesting;
4. sort each step’s normalized dependency list;
5. normalize empty maps and slices consistently;
6. serialize with canonical JSON rules;
7. compute SHA-256;
8. return `sha256:<lowercase hex>`.

The first implementation may use `encoding/json` over a canonical DTO whose slices have already been sorted. Add golden fixtures. Do not invent a custom binary codec before a demonstrated interoperability need.

Whether metadata contributes to the digest must be explicit. The recommended v1 rule is that all persisted plan fields, including metadata, contribute. A future separate `DisplayMetadata` field could be excluded if necessary.

---

## 13. Go builder API

The Go builder should be ergonomic but thin. It collects author intent and delegates semantics to `NormalizePlan`.

### 13.1 Construction

```go
b := workflow.NewPlan("hackernews",
    workflow.Version("1"),
    workflow.Metadata(map[string]string{
        "owner": "scraper",
    }),
)
```

The builder records diagnostics rather than panicking for ordinary author errors.

### 13.2 Inputs

```go
baseURL := b.Input("/baseURL")
maxPages := b.Input("/maxPages")
wholeInput := b.Input("")
```

`Input` returns a `Ref`.

### 13.3 Steps

Recommended signature:

```go
func (b *Builder) Step(
    id string,
    task TaskRef,
    input any,
    options ...StepOption,
) StepHandle
```

`input` is converted recursively by `ValueOf`:

- ordinary JSON-compatible Go values become literals;
- `Ref` becomes a reference;
- `StepHandle` is rejected unless converted through `Output`;
- maps must have string keys;
- unsupported values create diagnostics;
- `json.RawMessage` is validated and retained as a literal.

Example:

```go
fetch := b.Step(
    "fetch-frontpage",
    workflow.Task("http.fetch", "1"),
    map[string]any{
        "method": "GET",
        "url":    baseURL,
    },
    workflow.Lane("network"),
    workflow.Retry(workflow.RetryPolicy{
        MaxAttempts: 3,
    }),
)

parse := b.Step(
    "parse-frontpage",
    workflow.Task("hackernews.parse", "1"),
    map[string]any{
        "html":     fetch.Output("/body"),
        "baseURL":  baseURL,
        "maxPages": maxPages,
    },
)
```

The parse step automatically depends on `fetch-frontpage` because its input contains a reference to that output.

### 13.4 Step handle

```go
type StepHandle struct {
    builder *Builder
    id      StepID
}

func (h StepHandle) ID() StepID
func (h StepHandle) Output(pointer string) Ref
```

A handle is valid only for the builder that created it. Cross-builder use records a diagnostic.

### 13.5 Explicit ordering

```go
audit := b.Step("audit", workflow.Task("audit.check", "1"), input)

publish := b.Step(
    "publish",
    workflow.Task("publish.site", "1"),
    publishInput,
    workflow.After(audit),
)
```

`After` accepts handles or step IDs but validates builder ownership.

### 13.6 Outputs

```go
b.Output("stories", parse.Output("/stories"))
b.Output("pageCount", parse.Output("/pageCount"))
```

A plan may have no published outputs when it exists entirely for side effects, though applications should generally publish a compact receipt.

### 13.7 Build

```go
plan, err := b.Build()
if err != nil {
    return err
}
```

`Build` may be called more than once and returns independent normalized copies. Building does not permanently freeze or mutate the builder unless the implementation deliberately chooses one-shot behavior. Repeatable builds are convenient for tests and diagnostics.

### 13.8 Complete Go authoring example

```go
func HackerNewsPlan() (workflow.Plan, error) {
    b := workflow.NewPlan("hackernews-frontpage", workflow.Version("1"))

    baseURL := b.Input("/baseURL")

    fetch := b.Step(
        "fetch",
        workflow.Task("http.fetch", "1"),
        map[string]any{
            "method": "GET",
            "url":    baseURL,
        },
        workflow.Lane("network"),
        workflow.Retry(workflow.RetryPolicy{MaxAttempts: 3}),
    )

    parse := b.Step(
        "parse",
        workflow.Task("hackernews.parse", "1"),
        map[string]any{
            "html":    fetch.Output("/body"),
            "baseURL": baseURL,
        },
    )

    store := b.Step(
        "store",
        workflow.Task("hackernews.store", "1"),
        map[string]any{
            "stories": parse.Output("/stories"),
        },
    )

    b.Output("summary", store.Output(""))
    return b.Build()
}
```

Notice what is absent:

- no workflow ID;
- no worker ID;
- no site field;
- no queue key;
- no lease;
- no runner kind separate from task;
- no script path hidden in metadata;
- no manual dependency duplicated beside data references;
- no store or scheduler object.

---

## 14. Plan JSON example

The normalized representation of a small plan may look like this:

```json
{
  "schema": "golems-workflow-plan/v1",
  "name": "hackernews-frontpage",
  "version": "1",
  "steps": [
    {
      "id": "fetch",
      "task": {"name": "http.fetch", "version": "1"},
      "input": {
        "kind": "object",
        "object": {
          "method": {
            "kind": "literal",
            "literal": "GET"
          },
          "url": {
            "kind": "ref",
            "ref": {
              "source": "input",
              "pointer": "/baseURL"
            }
          }
        }
      },
      "retry": {
        "maxAttempts": 3,
        "initialDelayMillis": 1000,
        "maxDelayMillis": 60000,
        "multiplier": 2,
        "jitterFraction": 0
      },
      "lane": "network"
    },
    {
      "id": "parse",
      "task": {"name": "hackernews.parse", "version": "1"},
      "input": {
        "kind": "object",
        "object": {
          "html": {
            "kind": "ref",
            "ref": {
              "source": "step",
              "stepId": "fetch",
              "pointer": "/body"
            }
          }
        }
      },
      "retry": {
        "maxAttempts": 1,
        "initialDelayMillis": 1000,
        "maxDelayMillis": 60000,
        "multiplier": 2,
        "jitterFraction": 0
      }
    }
  ],
  "outputs": {
    "stories": {
      "source": "step",
      "stepId": "parse",
      "pointer": "/stories"
    }
  }
}
```

The explicit internal `Value` encoding is verbose but stable. Human-authored JSON or YAML may use a concise surface syntax if a converter produces this canonical form.

---
# Part IV — Tasks and handlers

## 15. Task registry

The registry maps a logical `TaskRef` to one process-local handler.

```go
type Registry struct {
    // unexported; safe for concurrent reads after Engine construction
}

type Registration struct {
    Task                   TaskRef
    Handler                Handler
    ImplementationIdentity string
}

func NewRegistry() *Registry
func (r *Registry) Register(reg Registration) error
func (r *Registry) MustRegister(reg Registration)
func (r *Registry) Lookup(task TaskRef) (Registration, bool)
func (r *Registry) Tasks() []TaskRef
```

`ImplementationIdentity` is optional but recommended for durable production runs. Examples:

```text
git:4f2c9be
binary:sha256:...
script:sha256:...
container:sha256:...
```

The identity is recorded in the attempt row and event. It is not used as a mandatory compile-time catalog dimension in v1.

### 15.1 Registry lifecycle

The registry is mutable while being assembled. `NewEngine` takes and validates a snapshot. Later registration changes do not affect an existing engine.

```go
registry := workflow.NewRegistry()
registry.MustRegister(...)

engine, err := workflow.NewEngine(workflow.EngineConfig{
    Registry: registry,
})
```

Updating handlers means constructing a new engine. This avoids hot-generation management until it is actually needed.

### 15.2 Registration validation

Reject:

- empty task names or versions;
- nil handlers;
- duplicate task references;
- empty or oversized implementation identities;
- reserved task namespaces if the host defines them.

Task names should use lowercase dotted identifiers:

```text
http.fetch
hackernews.parse
book.ocr-page
artifact.unpack
```

The framework should validate syntax but not own organization-wide naming policy.

---

## 16. Handler contract

A handler executes one resolved step input.

```go
type Handler interface {
    Run(ctx context.Context, task TaskContext) (Result, error)
}

type HandlerFunc func(context.Context, TaskContext) (Result, error)

func (f HandlerFunc) Run(ctx context.Context, task TaskContext) (Result, error) {
    return f(ctx, task)
}
```

### 16.1 Task context

```go
type TaskContext struct {
    RunID          RunID
    StepID         StepID
    Attempt        int
    Input          json.RawMessage
    IdempotencyKey string
    Logger         *slog.Logger
    Artifacts      ArtifactStore
}
```

This is intentionally small.

`RunID`, `StepID`, and `Attempt` support diagnostics. `IdempotencyKey` supports safe external effects. `Input` is the fully resolved JSON document. `Logger` is already annotated with run, step, task, and attempt fields. `Artifacts` stores and opens large objects.

The following do not belong in `TaskContext`:

- repository;
- transaction;
- lease token;
- worker identity;
- scheduler clock;
- queue policy;
- operator API;
- site database;
- scraper database;
- generic SQL connection;
- Goja runtime pointer.

Domain services are constructor dependencies of the handler.

### 16.2 Result

```go
type Result struct {
    Output   json.RawMessage  `json:"output"`
    Fragment *Fragment        `json:"fragment,omitempty"`
    Metadata map[string]string `json:"metadata,omitempty"`
}
```

`Output` is one compact JSON document. An absent output is normalized to JSON `null`.

`Fragment` is optional bounded dynamic work, explained later.

`Metadata` is bounded diagnostic metadata. It is not a second output channel.

### 16.3 Output size limit

The engine should enforce `MaxInlineOutputBytes`, with a default such as 1 MiB. Larger data must be placed in the artifact store, and the output should contain an `ArtifactRef`.

This catches accidental control-plane amplification early.

### 16.4 Convenience constructors

```go
func JSONResult(value any) (Result, error)
func RawResult(value json.RawMessage) (Result, error)
func ResultWithFragment(value any, fragment Fragment) (Result, error)
```

These helpers perform strict JSON serialization and return errors rather than panicking.

---

## 17. Typed Go handlers

Most Go users should not manually decode `json.RawMessage`.

```go
func Typed[I, O any](
    fn func(context.Context, TaskContext, I) (O, error),
) Handler
```

Implementation sketch:

```go
func Typed[I, O any](
    fn func(context.Context, TaskContext, I) (O, error),
) Handler {
    return HandlerFunc(func(ctx context.Context, tc TaskContext) (Result, error) {
        var input I
        if err := strictjson.Unmarshal(tc.Input, &input); err != nil {
            return Result{}, Permanent(
                "INVALID_TASK_INPUT",
                fmt.Errorf("decode input: %w", err),
            )
        }

        output, err := fn(ctx, tc, input)
        if err != nil {
            return Result{}, err
        }
        return JSONResult(output)
    })
}
```

For dynamic expansion:

```go
type TypedOutcome[O any] struct {
    Output   O
    Fragment *Fragment
    Metadata map[string]string
}

func TypedWithOutcome[I, O any](
    fn func(context.Context, TaskContext, I) (TypedOutcome[O], error),
) Handler
```

### 17.1 Example pure handler

```go
type ParseInput struct {
    HTML    string `json:"html"`
    BaseURL string `json:"baseURL"`
}

type ParseOutput struct {
    Stories []Story `json:"stories"`
    NextURL string  `json:"nextURL,omitempty"`
}

parseHandler := workflow.Typed(
    func(ctx context.Context, tc workflow.TaskContext, in ParseInput) (ParseOutput, error) {
        stories, nextURL, err := parseFrontpage(in.HTML, in.BaseURL)
        if err != nil {
            return ParseOutput{}, workflow.Permanent("PARSE_FAILED", err)
        }
        return ParseOutput{Stories: stories, NextURL: nextURL}, nil
    },
)
```

### 17.2 Example handler with explicit domain dependency

```go
type StoreStoriesHandler struct {
    Stories StoryRepository
}

func (h StoreStoriesHandler) Run(
    ctx context.Context,
    tc workflow.TaskContext,
) (workflow.Result, error) {
    var input struct {
        Stories []Story `json:"stories"`
    }
    if err := json.Unmarshal(tc.Input, &input); err != nil {
        return workflow.Result{}, workflow.Permanent("INVALID_INPUT", err)
    }

    if err := h.Stories.UpsertBatch(ctx, tc.IdempotencyKey, input.Stories); err != nil {
        if isTemporaryDatabaseError(err) {
            return workflow.Result{}, workflow.Retryable("STORE_TEMPORARY", err)
        }
        return workflow.Result{}, workflow.Permanent("STORE_FAILED", err)
    }

    return workflow.JSONResult(map[string]any{
        "stored": len(input.Stories),
    })
}
```

The repository is visible in application composition, not discovered through the workflow context.

---

## 18. Structured errors

The handler error model should distinguish stable control facts from diagnostic causes.

```go
type TaskError struct {
    Code       string            `json:"code"`
    Retryable  bool              `json:"retryable"`
    Message    string            `json:"message"`
    Details    map[string]string `json:"details,omitempty"`
    Cause      error             `json:"-"`
}

func (e *TaskError) Error() string
func (e *TaskError) Unwrap() error

func Retryable(code string, cause error, opts ...ErrorOption) error
func Permanent(code string, cause error, opts ...ErrorOption) error
```

### 18.1 Error rules

- `Code` is a stable uppercase identifier.
- `Message` is safe, bounded, and operator-facing.
- `Cause` may contain sensitive detail and belongs in process logs, not automatically in durable state.
- `Details` is a bounded string map and must not contain secrets or large payloads.
- An ordinary error that is not a `TaskError` is permanent by default. Silent automatic retry of unknown failures can repeat unsafe side effects.
- `context.Canceled` maps to cancellation, not task failure.
- `context.DeadlineExceeded` maps to `ATTEMPT_TIMEOUT`; retryability is configurable and defaults to true only when attempts remain.
- Panics are recovered at the handler boundary and recorded as `TASK_PANIC`, permanent by default. The stack is logged, not placed in the database.

### 18.2 Why permanent is the default

Retrying unknown errors sounds resilient but is hazardous for side-effecting tasks. Task authors should explicitly mark temporary failures. HTTP and provider adapters can centralize their own classification.

### 18.3 Failure persistence

A durable failure record should contain:

```go
type Failure struct {
    Code      string            `json:"code"`
    Retryable bool              `json:"retryable"`
    Message   string            `json:"message"`
    Details   map[string]string `json:"details,omitempty"`
}
```

It should not contain arbitrary nested errors, full response bodies, stack traces, credentials, or source documents.

---

## 19. Idempotency contract

The engine provides two stable keys:

```text
operation key = <run-id>/<step-id>
attempt key   = <run-id>/<step-id>/<attempt-number>
```

`TaskContext.IdempotencyKey` is the stable operation key, not the attempt key. Retries of the same logical step receive the same idempotency key.

### 19.1 Side-effect guidance

A handler should use the stable key when it:

- inserts into a database table with an idempotency column;
- sends an API request supporting an idempotency header;
- publishes an immutable object under a deterministic key;
- records a provider operation in a domain ledger;
- creates a message whose consumer deduplicates by key.

### 19.2 Limits of the contract

The engine cannot guarantee exactly-once behavior when the external system has no idempotency mechanism. The safe guarantee is:

> The engine records at-least-once attempts and never accepts a stale authoritative completion in a leasing configuration. Domain effects may still occur more than once.

This sentence should appear prominently in package documentation.

---

## 20. Task adapters

The framework should provide ordinary adapters before inventing task-package systems.

### 20.1 Function adapter

The typed Go handler is the primary adapter.

### 20.2 HTTP adapter

A reusable `http.fetch@1` handler belongs in an optional integration package. It receives a configured `http.Client`, request policy, allowed hosts, response-size limit, and artifact store.

Its output should be compact:

```json
{
  "status": 200,
  "finalURL": "https://example.test/",
  "headers": {"content-type": ["text/html"]},
  "body": {
    "digest": "sha256:...",
    "size": 42317,
    "mediaType": "text/html",
    "locator": "filecas:sha256/..."
  }
}
```

It should not copy the response body into step JSON.

### 20.3 Command adapter

A later but high-value adapter should execute a pinned command specification:

```go
type CommandInput struct {
    Executable string            `json:"executable"`
    Args       []string          `json:"args"`
    Env        map[string]string `json:"env,omitempty"`
    Inputs     map[string]ArtifactRef `json:"inputs,omitempty"`
}
```

The host—not the plan—defines allowed executables, workspaces, and environment policy. This provides a practical bridge to Python, R, shell, and compiled tools.

### 20.4 Container or remote adapter

OCI/container, Kubernetes, or remote-agent execution should implement the same `Handler` contract from the engine’s perspective. They are operational adapters, not new plan grammars.

---

# Part V — Execution state and scheduling

## 21. State model

The state machine should be smaller than the current engine while preserving attempt history.

### 21.1 Run status

```go
type RunStatus string

const (
    RunPending   RunStatus = "pending"
    RunRunning   RunStatus = "running"
    RunSucceeded RunStatus = "succeeded"
    RunFailed    RunStatus = "failed"
    RunCanceled  RunStatus = "canceled"
)
```

### 21.2 Stored step status

```go
type StepStatus string

const (
    StepPending   StepStatus = "pending"
    StepRunning   StepStatus = "running"
    StepSucceeded StepStatus = "succeeded"
    StepFailed    StepStatus = "failed"
    StepCanceled  StepStatus = "canceled"
)
```

There is no stored `ready`, `retrying`, or `blocked` state.

### 21.3 Derived step view

Snapshots derive a view:

```go
type StepView string

const (
    ViewWaiting    StepView = "waiting"     // dependencies still active
    ViewReady      StepView = "ready"       // runnable now
    ViewRetryWait  StepView = "retry_wait"  // deadline in future
    ViewRunning    StepView = "running"
    ViewSucceeded  StepView = "succeeded"
    ViewFailed     StepView = "failed"
    ViewBlocked    StepView = "blocked"     // terminal dependency failed/canceled
    ViewCanceled   StepView = "canceled"
)
```

A failed dependency makes a pending descendant appear blocked. Repairing or administratively retrying the dependency automatically changes the derived view; no descendant row transition is required.

### 21.4 Attempt status

```go
type AttemptStatus string

const (
    AttemptRunning     AttemptStatus = "running"
    AttemptSucceeded   AttemptStatus = "succeeded"
    AttemptFailed      AttemptStatus = "failed"
    AttemptInterrupted AttemptStatus = "interrupted"
    AttemptCanceled    AttemptStatus = "canceled"
    AttemptLeaseLost   AttemptStatus = "lease_lost" // distributed extension
)
```

Attempts are append-only.

---

## 22. State transitions

### 22.1 Submission

A successful submission transaction:

1. validates and normalizes the plan;
2. verifies every task exists in the engine registry;
3. validates concrete run input JSON;
4. assigns or accepts a run ID;
5. inserts the run with plan and input stored once;
6. materializes static step rows;
7. materializes normalized dependency edges;
8. appends `run.created`;
9. commits.

The run starts `pending`. It becomes `running` when the first attempt begins.

### 22.2 Claiming a ready step

A claim transaction:

1. selects a pending step whose `ready_at` is due;
2. confirms all dependencies succeeded;
3. confirms the run is not terminal or canceled;
4. resolves the next attempt number;
5. generates an opaque claim token;
6. marks the step running;
7. inserts a running attempt;
8. updates the run to running if necessary;
9. appends `step.started`;
10. commits.

The task handler never receives the claim token.

### 22.3 Success

A success transaction:

1. verifies the opaque claim is current;
2. validates output JSON and size;
3. validates and namespaces a returned fragment;
4. inserts any new step rows and edges;
5. stores compact output JSON;
6. marks the attempt succeeded;
7. marks the step succeeded;
8. clears the claim;
9. derives whether the run is complete;
10. appends `step.succeeded`, optional `steps.expanded`, and possible `run.succeeded`;
11. commits.

### 22.4 Retryable failure

A retryable failure transaction:

1. verifies the claim;
2. marks the attempt failed with structured failure;
3. increments the step’s completed attempt count;
4. computes a deterministic next deadline;
5. returns the step to pending with `ready_at`;
6. clears the claim;
7. appends `step.failed` and `step.retry_scheduled`;
8. commits.

### 22.5 Terminal failure

When no retry remains:

1. the attempt becomes failed;
2. the step becomes failed;
3. the run becomes failed;
4. descendants remain pending but appear blocked;
5. events are appended;
6. the claim is cleared;
7. the transaction commits.

The default v1 policy is fail-fast at the run level: no new unrelated steps are claimed after a terminal step failure. Already running steps are canceled cooperatively. This policy is simple and predictable.

A future `ContinueOnFailure` plan feature should not be added until a concrete workflow requires it and its output semantics are designed.

### 22.6 Cancellation

Cancellation:

- marks the run canceled;
- marks pending steps canceled;
- requests cancellation of active local handler contexts;
- marks active attempts canceled when they return or when recovery detects them;
- rejects later completion for obsolete claims;
- appends `run.canceled`.

In a leasing repository, cancellation also changes an epoch or invalidates leases so stale workers cannot commit.

### 22.7 Recovery after local process crash

On opening a local durable repository:

1. find attempts left running by the prior process instance;
2. mark them interrupted;
3. clear their claims;
4. return their steps to pending when policy permits another attempt;
5. otherwise mark them failed with `PROCESS_INTERRUPTED`;
6. append recovery events;
7. resume ordinary scheduling.

The local repository assumes one active engine process. Multiple concurrent processes require the distributed extension.

---

## 23. Repository contract

The repository interface should express state-machine operations, not expose tables or generic transactions.

```go
type Repository interface {
    CreateRun(ctx context.Context, command CreateRun) error

    ClaimReady(ctx context.Context, request ClaimRequest) (*Claim, error)
    Complete(ctx context.Context, command CompleteAttempt) error
    Fail(ctx context.Context, command FailAttempt) error

    CancelRun(ctx context.Context, runID RunID, at time.Time) error
    RetryStep(ctx context.Context, runID RunID, stepID StepID, at time.Time) error
    RecoverInterrupted(ctx context.Context, at time.Time) (int, error)

    Snapshot(ctx context.Context, runID RunID) (RunSnapshot, error)
    ListRuns(ctx context.Context, query RunQuery) ([]RunSummary, error)
    NextWake(ctx context.Context, scope ClaimScope, now time.Time) (*time.Time, error)

    Close() error
}
```

This is deliberately higher-level than the current broad store interface.

### 23.1 Commands

```go
type CreateRun struct {
    RunID      RunID
    Plan       Plan
    PlanDigest string
    Input      json.RawMessage
    CreatedAt  time.Time
    Metadata   map[string]string
}

type ClaimRequest struct {
    Scope      ClaimScope
    Now        time.Time
    TaskFilter func(TaskRef) bool // optional in memory; durable adapters use a task list
}

type Claim struct {
    Token                  string
    RunID                  RunID
    StepID                 StepID
    Task                   TaskRef
    Attempt                int
    Input                  json.RawMessage
    Retry                  RetryPolicy
    Timeout                time.Duration
    Lane                   string
    ImplementationIdentity string
}

type CompleteAttempt struct {
    Claim      Claim
    Output     json.RawMessage
    Fragment   *NormalizedFragment
    Metadata   map[string]string
    FinishedAt time.Time
}

type FailAttempt struct {
    Claim      Claim
    Failure    Failure
    RetryAt    *time.Time
    FinishedAt time.Time
}
```

The engine resolves step input before invoking the handler. Input resolution may happen inside `ClaimReady` or immediately after claim through a repository read method. The recommended approach is for the repository to return the step expression and dependency outputs, while the engine’s shared resolver computes input. To keep adapters consistent, expose a compact internal method rather than duplicating JSON Pointer behavior in SQL.

A practical internal split is:

```go
type ClaimedStep struct {
    Claim Claim
    Spec  StepSpec
    RunInput json.RawMessage
    DependencyOutputs map[StepID]json.RawMessage
}
```

The public `Claim` passed through completion remains opaque; the scheduler uses the larger internal value.

### 23.2 Claim tokens in local mode

Even the in-memory and local SQLite repositories should use opaque claim tokens internally. This prevents duplicate local completions and makes the state transition contract compatible with the later leasing adapter. It does not mean every user is forced to configure leases.

### 23.3 Repository invariants

Every implementation must guarantee:

- one current claim per running step;
- monotonically increasing attempt numbers;
- completion or failure accepts only the current claim;
- attempts are never overwritten;
- dynamic fragment insertion and parent completion are atomic;
- run terminal state is updated in the same transaction as the triggering step transition;
- event sequence numbers are monotonic within the repository;
- snapshots do not observe half-committed transitions.

---

## 24. Engine API

The engine provides a small synchronous Go surface. It may run tasks concurrently internally.

```go
type Engine struct {
    // unexported
}

type EngineConfig struct {
    Registry      *Registry
    Repository    Repository
    Artifacts     ArtifactStore
    Observer      Observer
    Clock         Clock
    Limits        Limits
    Logger        *slog.Logger
}

func NewEngine(config EngineConfig) (*Engine, error)
```

Defaults:

- memory repository;
- no-op artifact store that returns a clear configuration error on use, or a temporary file store when explicitly requested;
- real UTC clock;
- no-op observer;
- global concurrency equal to `max(1, runtime.GOMAXPROCS(0))` with a conservative cap;
- no lane-specific limits;
- safe plan, output, metadata, and expansion size bounds.

### 24.1 Constructor naming

Use unambiguous constructors throughout the public API:

```go
builder := workflow.NewPlan("name", ...)
engine, err := workflow.NewEngine(config)
```

Do not add a generic `workflow.New` alias. The small amount of extra typing prevents confusion in documentation, autocomplete, and mixed plan/engine composition code.

### 24.2 Submission

```go
func (e *Engine) Submit(
    ctx context.Context,
    plan Plan,
    input any,
    options ...SubmitOption,
) (RunID, error)
```

Options include:

- explicit run ID;
- run metadata;
- idempotent create-or-attach identity;
- start time for deterministic tests.

Create-or-attach should be a small optional feature:

```go
workflow.WithRunKey("source-snapshot:2026-07-28")
```

The repository stores a unique run key and requires plan digest plus input digest to match on attachment. Do not accept a caller-provided key that silently attaches to different work.

### 24.3 Run to completion

```go
func (e *Engine) Run(
    ctx context.Context,
    plan Plan,
    input any,
    options ...RunOption,
) (RunResult, error)
```

`Run` is `Submit` plus `Resume`.

### 24.4 Resume

```go
func (e *Engine) Resume(
    ctx context.Context,
    runID RunID,
) (RunResult, error)
```

`Resume` schedules only the selected run until terminal or context cancellation.

### 24.5 Serve

```go
func (e *Engine) Serve(ctx context.Context) error
```

`Serve` processes all runnable runs visible to the repository. It is the worker mode used by a service or CLI.

### 24.6 Deterministic tick

```go
func (e *Engine) Tick(
    ctx context.Context,
    options ...TickOption,
) (TickResult, error)
```

`Tick` performs a bounded amount of work and is intended for tests and maintenance. Its semantics should be explicit:

- claim at most N steps;
- execute them;
- process each completion;
- return after the selected claims finish.

Production `Serve` must not be implemented as a loop that waits for every fixed tick batch before refilling capacity.

### 24.7 Inspection and control

```go
func (e *Engine) Snapshot(ctx context.Context, runID RunID) (RunSnapshot, error)
func (e *Engine) Cancel(ctx context.Context, runID RunID) error
func (e *Engine) Retry(ctx context.Context, runID RunID, stepID StepID) error
func (e *Engine) Close() error
```

Administrative retry is allowed only for terminal failed steps. It creates a new pending opportunity without deleting old attempts.

---

## 25. Completion-driven scheduler

The production scheduler should be work-conserving.

### 25.1 Core loop

Conceptual algorithm:

```go
for {
    // Fill every currently available local slot.
    for capacity.Available() {
        claimed, err := repository.ClaimReady(ctx, request)
        if err != nil {
            return err
        }
        if claimed == nil {
            break
        }

        capacity.Acquire(claimed.Claim.Lane)
        startAttempt(claimed)
    }

    if selectedRunIsTerminal() {
        return result
    }

    nextWake, err := repository.NextWake(ctx, scope, clock.Now())
    if err != nil {
        return err
    }

    select {
    case completion := <-completions:
        capacity.Release(completion.Lane)
        persistCompletion(completion)
        // Immediately return to the fill loop.

    case <-wakeSignal:
        // Submission, retry, cancellation, or another local transition.

    case <-clock.After(until(nextWake)):
        // A retry deadline became due.

    case <-maintenanceTicker.C:
        // Detect cross-process changes in adapters that require polling.

    case <-ctx.Done():
        cancelActiveAttempts()
        return ctx.Err()
    }
}
```

A completed network task can free the network lane and admit the next network task even while an unrelated CPU task continues.

### 25.2 Capacity model

```go
type Limits struct {
    MaxParallel       int
    LaneParallel      map[string]int
    MaxInlineOutput   int64
    MaxPlanBytes      int64
    MaxPlanSteps      int
    MaxStepsPerRun    int
    MaxSpawnPerStep   int
    MaxExpansionDepth int
    MaxMetadataBytes  int
}
```

The local scheduler enforces `MaxParallel` and lane limits with semaphores owned by the engine.

A multi-process repository must add durable admission if capacity is meant to be global across processes. Local semaphores are not misrepresented as cluster limits.

### 25.3 Missing task implementation

Submission should normally reject a plan whose task is absent from the registry. This moves failure left.

A durable repository may contain an older run whose task is unavailable after restart. `Serve` should not mark it failed immediately. Snapshot should report `implementation_unavailable`, and the worker should leave it pending until the correct implementation is restored or an operator cancels it.

This is enough for v1. Exact generation coexistence can be added later.

### 25.4 Scheduler errors versus task errors

Repository failures, malformed persisted state, and internal invariant violations are engine errors. They stop the affected scheduler loop and are not automatically converted into task failures.

A handler return is a task outcome. Keep these categories separate.

---

## 26. Input resolution

Before a handler runs, the engine evaluates the step’s `Value` expression against:

- the immutable run input;
- successful dependency outputs.

### 26.1 JSON Pointer behavior

Use RFC 6901 exactly.

- `""` selects the whole document;
- `/a/b` selects nested object fields;
- `/0` indexes arrays;
- `~0` decodes to `~`;
- `~1` decodes to `/`.

A missing path is a permanent configuration/input failure:

```text
REFERENCE_NOT_FOUND
```

Do not silently substitute `null`.

### 26.2 Resolution copies values

Resolved JSON is copied into a new compact input document. The handler cannot mutate stored dependency output.

### 26.3 Size bounds

Resolution must enforce a maximum resolved input size. A plan that combines many large inline outputs should fail and direct the author toward artifacts.

### 26.4 Artifact references remain references

The resolver does not automatically open artifact bodies. A handler receives `ArtifactRef` JSON and explicitly calls the artifact store. This preserves the data-plane boundary and supports streaming.

---

## 27. Retry timing

Retry timing should be deterministic under an injected clock and random source.

```go
type Clock interface {
    Now() time.Time
    After(time.Duration) <-chan time.Time
}

type Random interface {
    Float64() float64
}
```

Backoff:

```text
delay = initial * multiplier^(failedAttempts-1)
delay = min(delay, maxDelay)
if jitter > 0:
    delay = delay * uniform(1-jitter, 1+jitter)
```

Clamp overflow and reject invalid multipliers or jitter fractions during normalization.

The deadline is persisted as integer epoch microseconds. Restart does not reset the delay.

---

## 28. Fail-fast run policy

The recommended v1 run policy is:

- every step is required;
- the first terminal step failure fails the run;
- no new steps are claimed after run failure;
- active handlers receive cancellation;
- successful prior steps remain recorded;
- an operator may retry the failed step, which reopens the run and naturally unblocks descendants.

This captures the useful `blocked` versus `canceled` lesson without persisting a blocked status.

Do not add optional dependencies, soft failures, compensation, or saga semantics to v1. They require explicit output and terminal-state rules.

---
# Part VI — Dynamic workflows

## 29. Why dynamic expansion belongs in the core

Scraping and OCR often discover work only after a task runs:

- a listing page reveals a next-page URL;
- a book manifest reveals page images;
- an archive reveals member files;
- an API response reveals object IDs;
- a discovery task determines a bounded set of detail pages.

Requiring authors to predeclare all such steps is impractical. On the other hand, making arbitrary task code directly mutate the repository is unsafe and impossible to validate.

The compromise is a bounded data-only `Fragment` returned as part of successful task output.

---

## 30. Fragment model

A fragment is a miniature plan whose IDs are relative to its parent step.

```go
type Fragment struct {
    Steps    []FragmentStep      `json:"steps"`
    Metadata map[string]string   `json:"metadata,omitempty"`
}

type FragmentStep struct {
    Key            string            `json:"key"`
    Task           TaskRef           `json:"task"`
    Input          FragmentValue     `json:"input"`
    After          []FragmentTarget  `json:"after,omitempty"`
    Retry          RetryPolicy       `json:"retry"`
    TimeoutMillis  int64             `json:"timeoutMillis,omitempty"`
    Lane           string            `json:"lane,omitempty"`
    Metadata       map[string]string `json:"metadata,omitempty"`
}
```

A fragment input may reference:

- the parent step’s output;
- another step in the same fragment;
- the original run input;
- an existing absolute step, when explicitly allowed.

Recommended reference shape:

```go
type FragmentRefSource string

const (
    FragmentRunInput FragmentRefSource = "input"
    FragmentParent   FragmentRefSource = "parent"
    FragmentSibling  FragmentRefSource = "sibling"
    FragmentAbsolute FragmentRefSource = "step"
)
```

The initial implementation should support run input, parent, and sibling references. Absolute references can be deferred unless a real workflow needs them.

---

## 31. Fragment builder

Use a builder parallel to the plan builder:

```go
fragment := workflow.NewFragment()

fetch := fragment.Step(
    "fetch-next",
    workflow.Task("http.fetch", "1"),
    map[string]any{
        "method": "GET",
        "url":    nextURL,
    },
    workflow.Lane("network"),
)

parse := fragment.Step(
    "parse-next",
    workflow.Task("hackernews.parse-page", "1"),
    map[string]any{
        "body": fetch.Output("/body"),
    },
)

normalized, err := fragment.Build()
```

For a broad fan-out plus finalizer:

```go
fragment := workflow.NewFragment()
workers := make([]workflow.FragmentHandle, 0, len(pages))

for i, page := range pages {
    worker := fragment.Step(
        fmt.Sprintf("page-%04d", i+1),
        workflow.Task("book.ocr-page", "2"),
        map[string]any{"page": page},
        workflow.Lane("provider.ocr"),
    )
    workers = append(workers, worker)
}

finalize := fragment.Step(
    "assemble",
    workflow.Task("book.assemble", "1"),
    map[string]any{
        "pages": workflow.OutputList(workers, ""),
    },
)
```

`OutputList` expands into an array of sibling references. This is acceptable only within configured fragment size limits.

---

## 32. Namespacing

The engine converts a relative fragment key into an absolute step ID:

```text
<parent-step-id>/<escaped-relative-key>
```

Examples:

```text
discover/page-0001
discover/page-0002
discover/assemble
parse-page-1/fetch-next
parse-page-1/parse-next
```

Use one documented escaping scheme. Do not concatenate raw user strings without validation.

Every fragment root step implicitly depends on the parent’s success. Sibling references infer additional edges.

### 32.1 Stable keys

Fragment keys are part of durable identity. Task code should derive them from stable domain identity, not completion order or random values.

Good:

```text
page-000123
story-39881234
sha256-abcd...
```

Poor:

```text
child-1 based on goroutine completion
random UUID generated on every retry
current Unix nanoseconds
```

---

## 33. Atomic expansion

Fragment insertion is part of parent completion. The repository transaction must either:

- commit parent output, all fragment steps, all edges, and parent success; or
- commit none of them.

This prevents a crash from producing a successful discovery step with only part of its discovered work persisted.

---

## 34. Expansion bounds

The engine enforces:

- maximum fragment bytes;
- maximum steps returned by one task;
- maximum total steps in one run;
- maximum dynamic depth;
- maximum fan-in for one step;
- maximum metadata and inline literal bytes;
- maximum total reference count.

Suggested conservative defaults:

```text
max fragment steps       1,000
max total run steps      100,000
max dynamic depth        64
max fragment JSON        4 MiB
max direct dependencies  10,000
```

These are defaults, not claims that every environment can safely support the maximum.

### 34.1 When fragments are insufficient

If a discovery result contains millions of items, returning one fragment is wrong. That workload justifies a later paged materializer or domain-owned cursor task.

A simple v1 pattern is recursive bounded discovery:

```text
read one manifest page
  -> spawn up to N item tasks
  -> spawn next manifest-page task if a cursor exists
```

This keeps every completion bounded without a first-class map subsystem.

---

## 35. Expansion idempotency

A current claim should complete only once. Nevertheless, repositories should defend against duplicate fragment insertion.

For every dynamic step, store a normalized spec digest. When `(run_id, absolute_step_id)` already exists:

- identical digest: treat as an idempotent duplicate;
- different digest: fail the parent completion with `DYNAMIC_STEP_CONFLICT`.

Never silently replace a previously persisted dynamic step.

---

## 36. Why not expose repository mutation to tasks

Direct mutation would let task code:

- insert unvalidated cycles;
- bypass size and count limits;
- create steps outside parent completion;
- observe partial graphs;
- depend on a specific database schema;
- forge run or lease state;
- produce behavior that cannot be reproduced by JavaScript and Go equally.

A returned fragment preserves dynamic power without granting control-plane authority.

---

# Part VII — Artifacts and the data plane

## 37. Artifact reference

The canonical artifact reference should remain compact and implementation-neutral.

```go
type ArtifactRef struct {
    Digest    string            `json:"digest"`
    Size      int64             `json:"size"`
    MediaType string            `json:"mediaType"`
    Name      string            `json:"name,omitempty"`
    Locator   string            `json:"locator"`
    Metadata  map[string]string `json:"metadata,omitempty"`
}
```

`Digest` should normally be `sha256:<hex>`. `Locator` is opaque to tasks except when passed back to the same artifact store.

The workflow repository stores this JSON reference as part of task output. It does not store artifact bytes.

---

## 38. Streaming artifact interface

```go
type ArtifactDescriptor struct {
    Name      string
    MediaType string
    Metadata  map[string]string
}

type ArtifactStore interface {
    Put(
        ctx context.Context,
        descriptor ArtifactDescriptor,
        body io.Reader,
    ) (ArtifactRef, error)

    Open(
        ctx context.Context,
        ref ArtifactRef,
    ) (io.ReadCloser, error)

    Stat(
        ctx context.Context,
        ref ArtifactRef,
    ) (ArtifactRef, error)
}
```

Optional extension interfaces:

```go
type ArtifactRemover interface {
    Remove(ctx context.Context, ref ArtifactRef) error
}

type ArtifactLister interface {
    List(ctx context.Context, query ArtifactQuery) ([]ArtifactRef, error)
}
```

The core engine requires only `Put`, `Open`, and `Stat`.

### 38.1 No primary `[]byte` API

Convenience helpers may accept small byte slices, but the fundamental interface streams. This avoids making whole-file memory loading the default architecture.

### 38.2 Verification

`Open` should verify that the requested digest and locator agree. A file store may verify the content digest on every read, on first read, or according to configuration. `Stat` must not silently change the reference identity.

---

## 39. File content-addressed store

A standard-library file store is valuable because it keeps the first durable deployment simple.

Recommended layout:

```text
<root>/
  objects/
    sha256/
      ab/
        cd...full-digest
  metadata/
    sha256/
      ab/
        cd...full-digest.json
  tmp/
```

Publication algorithm:

1. create a temporary file under the same filesystem;
2. stream input while computing SHA-256 and size;
3. enforce an optional maximum size;
4. flush and `fsync` the temporary file;
5. derive the final digest path;
6. create parent directories;
7. rename atomically if the object does not already exist;
8. sync the parent directory;
9. write bounded metadata atomically;
10. return the reference.

Concurrent publication of identical content should converge on one object.

### 39.1 Orphan behavior

A task may publish an immutable artifact and crash before its workflow completion commits. That leaves an unreferenced object. This is acceptable.

Artifact garbage collection is a separate maintenance process that compares object inventory with retained references. Do not try to make external byte publication and SQLite completion one distributed transaction.

---

## 40. Artifact use in handlers

Example:

```go
func renderReport(
    ctx context.Context,
    tc workflow.TaskContext,
    input ReportInput,
) (ReportOutput, error) {
    reader, writer := io.Pipe()

    renderErr := make(chan error, 1)
    go func() {
        defer writer.Close()
        renderErr <- writeLargeReport(writer, input)
    }()

    ref, err := tc.Artifacts.Put(ctx, workflow.ArtifactDescriptor{
        Name:      "report.jsonl",
        MediaType: "application/x-ndjson",
    }, reader)
    if err != nil {
        _ = reader.CloseWithError(err)
        return ReportOutput{}, workflow.Retryable("ARTIFACT_WRITE_FAILED", err)
    }
    if err := <-renderErr; err != nil {
        return ReportOutput{}, workflow.Permanent("REPORT_RENDER_FAILED", err)
    }

    return ReportOutput{Report: ref}, nil
}
```

In real code, avoid a goroutine if the producer can write directly into a temporary file or exposes a reader. The example illustrates that the API does not require buffering the entire report.

---

## 41. Directories and trees

Directory artifacts are useful but should not be improvised as arbitrary host paths.

A later extension can define a deterministic tree manifest:

```json
{
  "schema": "golems-artifact-tree/v1",
  "entries": [
    {"path":"index.json","artifact":{...}},
    {"path":"vectors/0001.bin","artifact":{...}}
  ]
}
```

The tree manifest itself is an artifact. Paths are normalized, relative, and traversal-safe. This can be implemented without changing workflow control state.

---

## 42. Secrets and sensitive data

Plans, run input, step output, events, metadata, and errors should be assumed inspectable by operators.

Therefore:

- credentials are injected into handlers or capability modules by the host;
- plans refer to secret names only when needed;
- durable errors never copy request headers or provider bodies by default;
- artifact metadata remains bounded and reviewed;
- locators should avoid embedding credentials;
- observer payloads should contain IDs and counts, not source documents.

The workflow engine is not a secrets manager.

---

# Part VIII — SQLite durability

## 43. Why SQLite remains a good adapter

SQLite is appropriate for a local restartable executor because it provides:

- transactional state transitions;
- simple deployment;
- inspectable state;
- good testability;
- WAL-based concurrent readers;
- enough throughput for a local scheduler whose task durations dominate transaction time.

SQLite should be an adapter, not the root package’s identity.

---

## 44. Recommended schema

The exact DDL will evolve, but the initial schema should remain close to the state model.

### 44.1 Runs

```sql
CREATE TABLE workflow_runs (
    id                 TEXT PRIMARY KEY,
    run_key            TEXT UNIQUE,
    plan_schema        TEXT NOT NULL,
    plan_name          TEXT NOT NULL,
    plan_version       TEXT NOT NULL,
    plan_digest        TEXT NOT NULL,
    plan_json          TEXT NOT NULL,
    input_json         TEXT NOT NULL,
    input_digest       TEXT NOT NULL,
    metadata_json      TEXT NOT NULL,
    status             TEXT NOT NULL,
    failure_json       TEXT,
    created_at_us      INTEGER NOT NULL,
    updated_at_us      INTEGER NOT NULL,
    canceled_at_us     INTEGER
);

CREATE INDEX workflow_runs_status_created
    ON workflow_runs(status, created_at_us);
```

The plan and run input are stored once per run.

### 44.2 Steps

```sql
CREATE TABLE workflow_steps (
    run_id                 TEXT NOT NULL
        REFERENCES workflow_runs(id) ON DELETE CASCADE,
    step_id                TEXT NOT NULL,
    parent_step_id         TEXT,
    expansion_depth        INTEGER NOT NULL DEFAULT 0,
    task_name              TEXT NOT NULL,
    task_version           TEXT NOT NULL,
    spec_json              TEXT NOT NULL,
    spec_digest            TEXT NOT NULL,
    status                 TEXT NOT NULL,
    attempt_count          INTEGER NOT NULL DEFAULT 0,
    ready_at_us            INTEGER,
    current_claim_token    TEXT,
    output_json            TEXT,
    output_digest          TEXT,
    failure_json           TEXT,
    created_at_us          INTEGER NOT NULL,
    updated_at_us          INTEGER NOT NULL,
    PRIMARY KEY (run_id, step_id)
);

CREATE INDEX workflow_steps_runnable
    ON workflow_steps(status, ready_at_us, created_at_us);
```

The token is an opaque local claim in v1. The distributed extension adds worker and expiry semantics.

### 44.3 Dependencies

```sql
CREATE TABLE workflow_edges (
    run_id          TEXT NOT NULL,
    step_id         TEXT NOT NULL,
    depends_on_id   TEXT NOT NULL,
    PRIMARY KEY (run_id, step_id, depends_on_id),
    FOREIGN KEY (run_id, step_id)
        REFERENCES workflow_steps(run_id, step_id)
        ON DELETE CASCADE,
    FOREIGN KEY (run_id, depends_on_id)
        REFERENCES workflow_steps(run_id, step_id)
        ON DELETE CASCADE
);

CREATE INDEX workflow_edges_dependency
    ON workflow_edges(run_id, depends_on_id);
```

### 44.4 Attempts

```sql
CREATE TABLE workflow_attempts (
    run_id                   TEXT NOT NULL,
    step_id                  TEXT NOT NULL,
    attempt                  INTEGER NOT NULL,
    claim_token              TEXT NOT NULL,
    status                   TEXT NOT NULL,
    implementation_identity  TEXT NOT NULL,
    failure_json             TEXT,
    started_at_us            INTEGER NOT NULL,
    finished_at_us           INTEGER,
    PRIMARY KEY (run_id, step_id, attempt),
    FOREIGN KEY (run_id, step_id)
        REFERENCES workflow_steps(run_id, step_id)
        ON DELETE CASCADE
);
```

### 44.5 Events

```sql
CREATE TABLE workflow_events (
    sequence       INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id         TEXT NOT NULL,
    step_id        TEXT,
    attempt        INTEGER,
    type           TEXT NOT NULL,
    occurred_at_us INTEGER NOT NULL,
    data_json      TEXT NOT NULL,
    FOREIGN KEY (run_id)
        REFERENCES workflow_runs(id) ON DELETE CASCADE
);

CREATE INDEX workflow_events_run_sequence
    ON workflow_events(run_id, sequence);
```

### 44.6 Migrations

```sql
CREATE TABLE workflow_schema_migrations (
    version       INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    applied_at_us INTEGER NOT NULL
);
```

Use additive migrations where practical. Fail fast when a database schema is newer than the binary understands.

---

## 45. Runnable query

A pending step is runnable when all dependencies succeeded.

Conceptual SQL:

```sql
SELECT s.run_id, s.step_id
FROM workflow_steps s
JOIN workflow_runs r ON r.id = s.run_id
WHERE s.status = 'pending'
  AND r.status IN ('pending', 'running')
  AND (s.ready_at_us IS NULL OR s.ready_at_us <= ?)
  AND NOT EXISTS (
      SELECT 1
      FROM workflow_edges e
      JOIN workflow_steps d
        ON d.run_id = e.run_id
       AND d.step_id = e.depends_on_id
      WHERE e.run_id = s.run_id
        AND e.step_id = s.step_id
        AND d.status <> 'succeeded'
  )
ORDER BY r.created_at_us, s.created_at_us, s.step_id
LIMIT 1;
```

Selection and transition to running must occur in one write transaction.

For SQLite, use `BEGIN IMMEDIATE` or a driver-supported transaction mode that prevents two local claimers from selecting the same row. The local adapter officially supports one engine process; tests should still prove claim atomicity across concurrent goroutines and connections.

---

## 46. Transaction boundaries

### 46.1 Create run

One transaction inserts:

- run;
- static steps;
- edges;
- creation event.

### 46.2 Claim

One transaction:

- selects one ready step;
- checks registry-supported task filter;
- increments attempt count;
- writes claim token;
- marks running;
- inserts attempt;
- marks run running;
- appends event.

### 46.3 Complete

One transaction:

- verifies current claim token and running state;
- validates no duplicate terminal transition;
- writes output;
- inserts normalized dynamic steps and edges;
- marks attempt and step succeeded;
- clears claim;
- derives run terminal state;
- appends events.

### 46.4 Fail

One transaction:

- verifies claim;
- writes attempt failure;
- either schedules retry or marks step failed;
- clears claim;
- derives run state;
- appends events.

### 46.5 Cancellation

One transaction:

- marks run canceled;
- marks pending steps canceled;
- invalidates current local claims;
- appends event.

Active handler contexts are canceled in memory after the transaction. A later completion fails claim verification.

---

## 47. SQLite operational settings

At open time:

```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL; -- or FULL for stricter durability profile
PRAGMA busy_timeout = 5000;
```

Make the durability profile explicit. Tests for crash-sensitive publication should run under the stricter setting.

Keep write transactions short. Task execution, artifact streaming, network calls, JSON rendering, and observer delivery occur outside transactions.

---

## 48. Numeric time rule

Every column compared or ordered as time uses integer UTC epoch microseconds.

Text timestamps may be included in external snapshots for readability, generated from integer values. Do not use variable-width RFC3339 strings in SQLite predicates.

Provide helpers in one package:

```go
func toMicros(t time.Time) int64
func fromMicros(value int64) time.Time
```

Normalize all input times to UTC.

---

## 49. Snapshots

A snapshot is a read model produced from authoritative state in one read transaction.

```go
type RunSnapshot struct {
    RunID       RunID                    `json:"runId"`
    Status      RunStatus                `json:"status"`
    Plan        Plan                     `json:"plan"`
    PlanDigest  string                   `json:"planDigest"`
    InputDigest string                   `json:"inputDigest"`
    Steps       []StepSnapshot           `json:"steps"`
    Outputs     map[string]json.RawMessage `json:"outputs,omitempty"`
    Failure     *Failure                 `json:"failure,omitempty"`
    CreatedAt   time.Time                `json:"createdAt"`
    UpdatedAt   time.Time                `json:"updatedAt"`
}

type StepSnapshot struct {
    StepID       StepID          `json:"stepId"`
    Task         TaskRef         `json:"task"`
    StoredStatus StepStatus      `json:"storedStatus"`
    View         StepView        `json:"view"`
    BlockedBy    []StepID        `json:"blockedBy,omitempty"`
    AttemptCount int             `json:"attemptCount"`
    ReadyAt      *time.Time      `json:"readyAt,omitempty"`
    Output       json.RawMessage `json:"output,omitempty"`
    Failure      *Failure        `json:"failure,omitempty"`
    Attempts     []AttemptSnapshot `json:"attempts"`
}
```

For large runs, provide paged step and attempt queries rather than always embedding all history. The simple `Snapshot` may impose a configured maximum and return summary counts plus cursors.

---

## 50. Store input and output bounds

The repository should enforce limits even if the engine already validated them.

Recommended checks:

- plan JSON maximum;
- run input maximum;
- inline step output maximum;
- failure JSON maximum;
- event data maximum;
- metadata maximum;
- dynamic spec maximum;
- maximum run steps.

Defense in depth prevents another caller from bypassing the engine and inserting pathological rows.

---
# Part IX — Events, logs, and observability

## 51. Event model

Events describe committed state transitions. They are not commands and not the sole source of truth.

```go
type EventType string

const (
    EventRunCreated       EventType = "run.created"
    EventRunStarted       EventType = "run.started"
    EventRunSucceeded     EventType = "run.succeeded"
    EventRunFailed        EventType = "run.failed"
    EventRunCanceled      EventType = "run.canceled"
    EventRunReopened      EventType = "run.reopened"

    EventStepStarted      EventType = "step.started"
    EventStepSucceeded    EventType = "step.succeeded"
    EventStepFailed       EventType = "step.failed"
    EventRetryScheduled   EventType = "step.retry_scheduled"
    EventStepInterrupted  EventType = "step.interrupted"
    EventStepsExpanded    EventType = "steps.expanded"
)

type Event struct {
    Sequence   int64           `json:"sequence"`
    Type       EventType       `json:"type"`
    OccurredAt time.Time       `json:"occurredAt"`
    RunID      RunID           `json:"runId"`
    StepID     StepID          `json:"stepId,omitempty"`
    Attempt    int             `json:"attempt,omitempty"`
    Data       json.RawMessage `json:"data,omitempty"`
}
```

Do not emit a durable `step.ready` event in v1 because readiness is derived and may change with time or administrative repair. A live UI may calculate it from snapshots.

---

## 52. Durable and live events

The SQLite repository appends durable events in the same transaction as state changes. After commit, the engine delivers the event to an optional observer.

```go
type Observer interface {
    Observe(ctx context.Context, event Event)
}

type ObserverFunc func(context.Context, Event)
```

### 52.1 Observer safety

The engine must:

- invoke observers only after commit;
- recover observer panics;
- log observer failures;
- never convert observer failure into workflow failure;
- define whether delivery is serialized;
- avoid holding repository or scheduler locks during delivery.

The simplest v1 behavior is serialized, synchronous post-commit delivery with panic recovery. A buffered asynchronous adapter can be provided for slow consumers.

### 52.2 Restart behavior

A live observer may miss events while the process is down. Consumers that require recovery read events by sequence from the repository and then subscribe to new delivery.

The source of current truth is still `Snapshot`.

---

## 53. Event payload discipline

Event payloads should be compact and stable.

Good event data:

```json
{
  "task": "http.fetch@1",
  "lane": "network",
  "implementation": "git:4f2c9be"
}
```

```json
{
  "failureCode": "HTTP_503",
  "retryable": true,
  "retryAt": "2026-07-28T18:20:00Z"
}
```

```json
{
  "count": 37,
  "parent": "discover"
}
```

Bad event data:

- entire task input;
- entire task output;
- artifact bytes;
- HTTP response bodies;
- SQL rows;
- prompts or model completions;
- credentials;
- stack traces.

---

## 54. Logging

Use `log/slog` in the core to avoid a logging dependency.

Each task logger should be pre-annotated:

```text
run_id
step_id
task
attempt
lane
```

The engine logs:

- submission rejection;
- claim and completion invariant failures;
- handler panic stacks;
- repository failures;
- observer failures;
- recovery actions;
- cancellation and shutdown.

Task logs are not automatically durable. A later log sink may capture them by run and attempt. Do not force arbitrary log text into workflow state rows.

---

## 55. Metrics

Metrics should be an optional observer or scheduler hook. Useful measurements include:

- active tasks globally and by lane;
- claim latency;
- step execution duration;
- retry count by task and code;
- run terminal count;
- runnable backlog;
- artifact bytes written;
- repository transaction duration;
- observer lag.

Labels must be bounded. Do not label metrics by run ID, step ID, URL, or arbitrary failure message.

---

# Part X — Goja authoring library

## 56. Boundary principle

JavaScript is an authoring language for the canonical plan, not a second workflow engine.

The complete path is:

```text
JavaScript builder calls
        |
        v
plain data-only plan object
        |
        v
JSON.stringify
        |
        v
one native strict parse/normalize function
        |
        v
canonical plan JSON
        |
        v
plain frozen JavaScript object
```

No JavaScript callback, object identity, Promise, runtime pointer, or closure survives compilation.

---

## 57. Module shape

Expose an instance-bound module:

```javascript
const workflow = require("workflow");
```

Recommended exports:

```typescript
export function define(
  name: string,
  options: DefineOptions,
  build: (builder: Builder) => void,
): Plan;

export function parse(json: string): Plan;
export function validate(value: unknown): ValidationResult;
export function digest(plan: Plan): string;
export function toJSON(plan: Plan, pretty?: boolean): string;
```

`define` executes the callback immediately and returns a normalized plain plan.

---

## 58. JavaScript builder API

```typescript
interface Builder {
  input(pointer?: string): Ref;

  step(
    id: string,
    task: string | TaskRef,
    input: unknown,
    options?: StepOptions,
  ): StepHandle;

  output(name: string, ref: Ref): void;
}

interface StepHandle {
  readonly id: string;
  output(pointer?: string): Ref;
}

interface StepOptions {
  after?: Array<StepHandle | string>;
  retry?: Partial<RetryPolicy>;
  timeoutMs?: number;
  lane?: string;
  metadata?: Record<string, string>;
}
```

Example:

```javascript
const wf = require("workflow");

module.exports = wf.define(
  "hackernews-frontpage",
  { version: "1" },
  (b) => {
    const baseURL = b.input("/baseURL");

    const fetch = b.step(
      "fetch",
      "http.fetch@1",
      {
        method: "GET",
        url: baseURL,
      },
      {
        lane: "network",
        retry: { maxAttempts: 3 },
      },
    );

    const parse = b.step(
      "parse",
      "hackernews.parse@1",
      {
        body: fetch.output("/body"),
        baseURL,
      },
    );

    b.output("stories", parse.output("/stories"));
  },
);
```

This mirrors the Go authoring model. JavaScript does not specify worker queues, lease policy, site identity, script metadata, runner kind, or persistence details.

---

## 59. Plain reference encoding

Inside the JavaScript builder, a reference may be a frozen plain object:

```javascript
Object.freeze({
  $workflow: "ref/v1",
  source: "step",
  stepId: "fetch",
  pointer: "/body",
});
```

The sentinel has no authority. A user can forge it, and the native normalizer will validate it. Security does not depend on hidden symbols or Goja object identity.

The builder should recursively transform sentinel references into the canonical tagged `Value` form before normalization.

---

## 60. Native compiler hook

The JavaScript implementation can be mostly embedded JavaScript plus a very small native export:

```typescript
interface NativeCompiler {
  normalize(json: string): string;
  digest(json: string): string;
}
```

Conceptual Go loader:

```go
type AuthoringModule struct {
    Limits workflow.Limits
}

func (m *AuthoringModule) Name() string { return "workflow" }

func (m *AuthoringModule) Loader(
    vm *goja.Runtime,
    module *goja.Object,
) {
    native := vm.NewObject()

    _ = native.Set("normalize", func(source string) (string, error) {
        plan, diagnostics := workflow.ParsePlanJSON([]byte(source))
        if diagnostics.HasErrors() {
            return "", &ValidationError{Diagnostics: diagnostics}
        }
        data, err := json.Marshal(plan)
        return string(data), err
    })

    exports, err := instantiateEmbeddedAuthoringJS(vm, native)
    if err != nil {
        panic(vm.NewGoError(err))
    }
    _ = module.Set("exports", exports)
}
```

The actual implementation should return JavaScript `TypeError` or a structured validation exception with diagnostics.

### 60.1 Why stringify at the boundary

Passing a JSON string through the native hook has useful properties:

- functions and exotic prototypes cannot cross accidentally;
- Go receives one bounded byte sequence;
- strict JSON decoding is shared with file and HTTP plan loading;
- no `map[*goja.Object]...` state is required;
- canonical output can be returned as JSON;
- no Goja object survives the call.

If a function or `undefined` value disappears during `JSON.stringify`, required-field validation detects the resulting malformed plan.

---

## 61. No global mutable module registry

The workflow authoring module should be registered per runtime factory or per require registry.

Avoid a package-level global engine pointer or mutable catalog. Multiple hosts may run different registries, repositories, and security profiles in the same process.

The current Goja infrastructure supports runtime-aware module registration and an owned runtime/event loop. Use those composition mechanisms rather than `init()` registration for host-specific workflow instances.

---

## 62. TypeScript declarations

Ship generated or hand-reviewed declarations:

```text
workflow/goja/workflow.d.ts
```

Declarations should include:

- plan schema;
- builder API;
- references and handles;
- retry and step options;
- diagnostics;
- execution module APIs described below.

Declaration generation must be tested against the Go/JavaScript exports. A CI test can load the module, enumerate expected exports, and compare them with a generated manifest.

---

## 63. JavaScript validation errors

Example:

```javascript
try {
  const plan = wf.define("bad", { version: "1" }, (b) => {
    b.step("a", "missing-version", {});
  });
} catch (error) {
  console.error(error.name);        // WorkflowValidationError
  console.error(error.diagnostics); // stable code/path/message objects
}
```

Do not collapse all compiler failures into one Go error string. Preserve structured diagnostics.

---

## 64. Canonical equivalence test

The same logical plan authored in Go and JavaScript must normalize to byte-equivalent canonical JSON and the same digest.

This is a central acceptance test, not a documentation example.

Test fixture:

```text
testdata/equivalence/hackernews.go.json
testdata/equivalence/hackernews.js
testdata/equivalence/hackernews.canonical.json
```

The Go builder, JS builder, and JSON parser must all produce the canonical fixture.

---

# Part XI — Exposing execution to Goja

## 65. Runtime module

Expose the existing Go engine through a second host-injected module:

```javascript
const runtime = require("workflow/runtime");
```

Recommended API:

```typescript
export function run(
  plan: Plan,
  input: unknown,
  options?: RunOptions,
): Promise<RunResult>;

export function submit(
  plan: Plan,
  input: unknown,
  options?: SubmitOptions,
): Promise<string>;

export function resume(runId: string): Promise<RunResult>;
export function inspect(runId: string): Promise<RunSnapshot>;
export function cancel(runId: string): Promise<void>;
export function retry(runId: string, stepId: string): Promise<void>;
```

The module does not implement scheduling. It calls the same `Engine` methods used by Go.

---

## 66. Promise and runtime ownership

Engine work can block or use goroutines. Goja values may only be created or resolved on the runtime owner.

Conceptual implementation:

```go
func makeRunFunction(
    runtimeCtx *engine.RuntimeModuleRegistrationContext,
    wfEngine *workflow.Engine,
) func(goja.FunctionCall) goja.Value {
    return func(call goja.FunctionCall) goja.Value {
        vm := runtimeCtx.VM
        promise, resolve, reject := vm.NewPromise()

        planJSON, inputJSON, options, err := decodeRunCall(vm, call)
        if err != nil {
            reject(vm.ToValue(err.Error()))
            return vm.ToValue(promise)
        }

        lifetime := runtimeCtx.Context
        go func() {
            result, runErr := runFromJSON(
                lifetime,
                wfEngine,
                planJSON,
                inputJSON,
                options,
            )

            _ = runtimeCtx.Owner.Post(
                lifetime,
                "workflow.run.resolve",
                func(_ context.Context, vm *goja.Runtime) {
                    if runErr != nil {
                        reject(errorValue(vm, runErr))
                        return
                    }
                    resolve(vm.ToValue(result))
                },
            )
        }()

        return vm.ToValue(promise)
    }
}
```

Exact APIs depend on the Goja host library, but the ownership rule is invariant:

> A worker goroutine performs Go work; it never touches `*goja.Runtime`, `goja.Value`, resolver functions, or JavaScript objects directly.

### 66.1 Runtime shutdown

The module’s operations inherit the Goja runtime lifetime context. Closing the runtime cancels pending workflow API calls from that JavaScript host. Canceling the host call does not necessarily cancel a submitted durable run unless the API explicitly requests that behavior.

`run()` owns and cancels its submitted run on caller cancellation only if documented. `submit()` returns after durable creation and leaves the run independent.

---

## 67. Data conversion

At the runtime boundary:

1. serialize the JavaScript plan through `JSON.stringify`;
2. parse and normalize using the shared Go compiler;
3. serialize the input to bounded JSON;
4. return snapshots/results as JSON-compatible plain objects;
5. never export Go repository objects, handlers, readers, or contexts into JavaScript.

Large artifact bodies are read through explicit artifact APIs, not included in `inspect()`.

---

## 68. Runtime module injection

The `workflow/runtime` module must be bound to one concrete engine instance:

```go
module := gojaworkflow.RuntimeModule(engine)

factory, err := gojaengine.NewRuntimeFactoryBuilder(
    gojaengine.WithoutImplicitDefaultModules(),
).
    WithModules(
        gojaworkflow.AuthoringModule(),
        module,
    ).
    Build()
```

The exact builder options may differ, but the host should explicitly select modules. A process-global default engine is prohibited.

---

## 69. JavaScript execution example

```javascript
const wf = require("workflow");
const runtime = require("workflow/runtime");

const plan = wf.define("thumbnail", { version: "1" }, (b) => {
  const source = b.input("/source");

  const render = b.step(
    "render",
    "image.thumbnail@1",
    { source, width: 320 },
    { lane: "cpu" },
  );

  b.output("thumbnail", render.output("/artifact"));
});

async function main() {
  const result = await runtime.run(plan, {
    source: {
      digest: "sha256:...",
      size: 123456,
      mediaType: "image/jpeg",
      locator: "filecas:sha256/...",
    },
  });

  console.log(result.outputs.thumbnail);
}

module.exports = main();
```

This is an execution client. The task itself may be implemented in Go, JavaScript, a command adapter, or a future remote adapter.

---

# Part XII — JavaScript task handlers

## 70. Separate authoring from task execution

A JavaScript workflow definition and a JavaScript task handler are different products:

- the authoring module constructs a plan and needs no dangerous capability;
- a task handler executes later, may perform I/O through capabilities, and must obey runtime ownership and cancellation rules.

Do not combine them into one ambient `ctx` API.

---

## 71. JavaScript module handler

A production adapter can turn a named JavaScript module export into a Go `Handler`.

```go
type JSModuleHandlerConfig struct {
    Factory       *gojaengine.RuntimeFactory
    Module        string
    Export        string
    SourceIdentity string
    MaxResultBytes int64
}

func NewJSModuleHandler(config JSModuleHandlerConfig) (workflow.Handler, error)
```

The handler should create a fresh owned runtime for each attempt by default.

Benefits:

- no state leakage across attempts;
- cancellation is scoped;
- module cache is scoped;
- capability set is explicit;
- a failed script cannot poison a shared long-lived VM;
- concurrency uses independent runtimes.

A carefully implemented runtime pool can be added later after measurement. The fresh-runtime path defines correctness.

---

## 72. JavaScript task API

A task module exports a function:

```javascript
module.exports = async function task(ctx) {
  return {
    output: { ... },
    fragment: { ... } // optional
  };
};
```

Recommended context:

```typescript
interface TaskContext {
  readonly runId: string;
  readonly stepId: string;
  readonly attempt: number;
  readonly input: unknown;
  readonly idempotencyKey: string;

  log: {
    debug(message: string, fields?: Record<string, unknown>): void;
    info(message: string, fields?: Record<string, unknown>): void;
    warn(message: string, fields?: Record<string, unknown>): void;
    error(message: string, fields?: Record<string, unknown>): void;
  };

  artifacts: {
    putText(name: string, mediaType: string, text: string): Promise<ArtifactRef>;
    putBytes(name: string, mediaType: string, bytes: Uint8Array): Promise<ArtifactRef>;
    readText(ref: ArtifactRef, limit?: number): Promise<string>;
  };

  fragment(): FragmentBuilder;
  retryable(code: string, message: string, details?: Record<string, string>): never;
  permanent(code: string, message: string, details?: Record<string, string>): never;
}
```

`putBytes` and `readText` are bounded convenience methods. A future stream API can be added when the Goja host has a robust stream bridge. Large-data production tasks should generally use Go, command, or remote adapters rather than copying huge data through JavaScript strings.

### 72.1 No lease or repository

The JS task API does not expose:

- lease token;
- current expiry;
- SQL database;
- workflow repository;
- raw dependency rows;
- arbitrary child insertion;
- worker identity.

Its input already contains resolved dependency values.

---

## 73. Task result decoding

Accepted returns:

```javascript
return { output: value };
```

```javascript
return { output: value, fragment };
```

For convenience, a non-envelope value may be interpreted as `output`, but a single explicit envelope is easier to evolve. The recommended production API requires the envelope and makes the convenience behavior development-only or opt-in.

Validation checks:

- result is JSON-serializable;
- output size is bounded;
- fragment is data-only and bounded;
- no function, Promise, symbol, or host object survives serialization;
- metadata is bounded;
- returned artifact references have valid shape.

---

## 74. Promise handling

The handler invokes the module function on the owned runtime and awaits a returned Promise using the host event loop.

Cancellation must interrupt or close the runtime according to the Goja host’s supported mechanism. The adapter must not busy-wait on promise state.

Tests need to cover:

- immediate return;
- resolved Promise;
- rejected Promise;
- never-resolving Promise canceled by context;
- panic or JavaScript exception;
- runtime close during operation;
- oversized output;
- malformed fragment.

---

## 75. Capability profiles

Provide explicit host profiles rather than claiming Goja is a sandbox.

### Data-only profile

For plan authoring:

- workflow authoring module;
- deterministic utility modules such as path manipulation if required;
- no network;
- no filesystem;
- no database;
- no process environment;
- no command execution.

### Trusted task profile

For application-owned JavaScript:

- logging;
- artifact API;
- selected domain modules;
- optionally HTTP through a policy-bound module;
- optionally a narrow repository module.

### Untrusted task profile

Do not execute untrusted code in-process. Use a subprocess/container adapter with OS-level restrictions and a bounded protocol.

Goja is a language runtime, not a security boundary.

---

## 76. Narrow domain modules

Prefer:

```javascript
const stories = require("hackernews/stories");
await stories.upsert(ctx.input.stories, ctx.idempotencyKey);
```

Over:

```javascript
const db = require("site-db");
db.exec("arbitrary SQL ...");
```

A narrow module:

- validates domain records;
- centralizes idempotency;
- hides schema migrations;
- limits authority;
- is easier to test and version;
- produces clearer task dependencies.

Generic SQL can remain available in explicitly trusted application profiles, but it should not define the workflow framework.

---

## 77. Development-only inline JS tasks

A REPL or notebook may want:

```javascript
runtime.registerTask("demo.double@1", async (ctx) => ({
  output: { value: ctx.input.value * 2 },
}));
```

This can be offered as a development feature with clear restrictions:

- registration lasts only for that runtime/engine instance;
- functions are not serializable;
- durable restart requires host re-registration;
- execution is tied to the owning runtime;
- concurrency may be serialized;
- it is not suitable for production multi-process workers.

Do not let this convenience distort the production handler contract.

---
# Part XIII — Optional multi-process execution

## 78. Why this is a separate level

A single local engine can recover after crashes without leases. It owns all active handler goroutines, and startup can mark abandoned attempts interrupted.

Multiple processes create a different correctness problem:

- two workers may race to claim the same step;
- a worker may pause beyond a timeout;
- another worker may recover the step;
- the stale worker may later attempt to commit;
- capacity and rate limits may need cluster-wide coordination.

Those forces justify leases and fencing. They do not justify exposing leases in every plan or task context.

---

## 79. Leasing repository extension

```go
type LeasingRepository interface {
    Repository

    RenewClaim(
        ctx context.Context,
        claim Claim,
        now time.Time,
        duration time.Duration,
    ) (Claim, error)
}
```

The distributed `Claim` includes executor-only fields:

```go
type Claim struct {
    Token     string
    WorkerID  string
    ExpiresAt time.Time
    // ordinary run/step/attempt fields
}
```

Handlers still receive only `TaskContext`.

### 79.1 Claim invariant

A completion or failure may mutate durable state only when:

- the token matches the current claim;
- the step is running;
- the claim has not expired at commit time;
- the run has not invalidated the claim through cancellation or epoch change.

This proof occurs inside the same transaction as the transition.

### 79.2 Heartbeat supervisor

The engine detects `LeasingRepository` and starts a supervisor per active claim.

Recommended behavior:

- renew at one third of lease duration;
- compute new expiry from current time, not a stale copied expiry;
- cancel the handler context immediately on lost claim;
- do not attempt completion after lease loss;
- record `lease_lost` in attempt history when the repository permits;
- keep heartbeat errors separate from task errors.

### 79.3 Cancellation epoch

A run-level cancellation epoch is useful when claims can outlive an administrative action. The claim captures the epoch; completion verifies it has not changed.

This field belongs in the distributed repository implementation and attempt record, not the plan.

---

## 80. Durable capacity

Per-process semaphores do not enforce global capacity. A distributed deployment has three choices:

1. accept capacity per worker process;
2. partition lanes so only one worker group serves a lane;
3. add durable reservations to the leasing transaction.

The initial distributed extension should document option 1 or 2. Durable global capacity is another feature with transaction and failure semantics; it should not appear accidentally.

---

## 81. Durable rate limiting and budgets

Rate limits and monetary budgets are best modeled as an independent `Admission` service used by side-effecting handlers or a future repository extension.

```go
type Admission interface {
    Acquire(
        ctx context.Context,
        request AdmissionRequest,
    ) (AdmissionGrant, error)

    Settle(
        ctx context.Context,
        grant AdmissionGrant,
        outcome AdmissionOutcome,
    ) error
}
```

The framework should not include this in v1. When added, it must define:

- reservation identity;
- retry interaction;
- cache-hit ordering;
- crash recovery;
- conservative versus actual settlement;
- approval behavior on exhaustion;
- privacy of provider payloads.

The linked Workflow V3 work contains useful patterns for this later phase, but those patterns should remain outside the initial authoring vocabulary.

---

## 82. Remote executor

A remote executor may implement a handler that:

1. packages resolved input and artifact references;
2. submits a remote job with the stable idempotency key;
3. polls or waits for completion;
4. validates returned compact output and artifacts;
5. maps remote errors into `TaskError`;
6. respects context cancellation;
7. returns the same `Result` contract.

The plan remains unchanged. Deployment decides that `image.thumbnail@1` is local Go in one host and remote container execution in another, provided the logical contract is compatible.

---

# Part XIV — Applying the design to scraper

## 83. Correct ownership boundary

The new workflow module owns:

- plan structure;
- task references;
- input resolution;
- run/step/attempt state;
- retries and cancellation;
- bounded dynamic expansion;
- local scheduling;
- persistence contract;
- compact events and snapshots;
- artifact references and streaming store interface.

The scraper application owns:

- site manifests;
- site-specific task composition;
- HTTP policy;
- HTML parsing;
- site repositories and migrations;
- browser automation;
- site CLI commands;
- scraper API routes;
- domain records and projections;
- site-specific rate and provider policy.

The Goja host owns:

- runtime construction;
- module selection;
- event-loop ownership;
- script source resolution;
- capability injection;
- shutdown.

This separation should be reflected in imports and enforced by tests.

---

## 84. Built-in scraper tasks

The scraper integration can register a small task set.

### 84.1 HTTP fetch

```text
scraper.http.fetch@1
```

Host dependencies:

- configured `http.Client`;
- allowed methods and host policy;
- user-agent policy;
- response-size limit;
- artifact store;
- optional domain rate admission.

Input:

```json
{
  "method": "GET",
  "url": "https://news.ycombinator.com/",
  "headers": {}
}
```

Output:

```json
{
  "status": 200,
  "finalURL": "https://news.ycombinator.com/",
  "headers": {"content-type": ["text/html; charset=utf-8"]},
  "body": {
    "digest": "sha256:...",
    "size": 34891,
    "mediaType": "text/html",
    "name": "frontpage.html",
    "locator": "filecas:sha256/..."
  }
}
```

### 84.2 JavaScript site task

```text
scraper.js.module@1
```

Input:

```json
{
  "module": "hackernews/extract-frontpage.js",
  "export": "default",
  "args": {
    "body": {"artifact-ref": "..."},
    "baseURL": "..."
  }
}
```

A stricter design registers each script as its own logical task:

```text
hackernews.extract-frontpage@1
```

That is preferable for production because it gives a stable contract and implementation identity. A generic module task is useful during migration.

### 84.3 Store stories

```text
hackernews.store-stories@1
```

Implemented in Go or a narrow JavaScript module. It captures the Hacker News repository and uses the workflow idempotency key.

---

## 85. Hacker News workflow in the new model

A clean static seed plan:

```go
func HackerNewsSeedPlan() (workflow.Plan, error) {
    b := workflow.NewPlan(
        "hackernews-seed",
        workflow.Version("1"),
    )

    baseURL := b.Input("/baseURL")
    maxPages := b.Input("/maxPages")

    fetch := b.Step(
        "fetch-page-1",
        workflow.Task("scraper.http.fetch", "1"),
        map[string]any{
            "method": "GET",
            "url":    baseURL,
        },
        workflow.Lane("hackernews.http"),
        workflow.Retry(workflow.RetryPolicy{MaxAttempts: 3}),
    )

    parse := b.Step(
        "parse-page-1",
        workflow.Task("hackernews.parse-page", "1"),
        map[string]any{
            "body":       fetch.Output("/body"),
            "pageNumber": 1,
            "maxPages":   maxPages,
            "baseURL":    baseURL,
        },
    )

    b.Output("lastPage", parse.Output("/pageNumber"))
    b.Output("storyCount", parse.Output("/totalStored"))
    return b.Build()
}
```

The parse handler stores current-page stories and, when another page is allowed, returns a two-step fragment:

```go
func (h ParsePageHandler) Run(
    ctx context.Context,
    tc workflow.TaskContext,
) (workflow.Result, error) {
    input, err := decodeParseInput(tc.Input)
    if err != nil {
        return workflow.Result{}, workflow.Permanent("INVALID_INPUT", err)
    }

    reader, err := tc.Artifacts.Open(ctx, input.Body)
    if err != nil {
        return workflow.Result{}, workflow.Retryable("BODY_OPEN_FAILED", err)
    }
    defer reader.Close()

    stories, nextURL, err := h.Parser.Parse(reader, input.BaseURL)
    if err != nil {
        return workflow.Result{}, workflow.Permanent("HTML_PARSE_FAILED", err)
    }

    if err := h.Stories.UpsertBatch(ctx, tc.IdempotencyKey, stories); err != nil {
        return workflow.Result{}, classifyStoreError(err)
    }

    output := map[string]any{
        "pageNumber": input.PageNumber,
        "stored":     len(stories),
        "nextURL":    nextURL,
    }

    if nextURL == "" || input.PageNumber >= input.MaxPages {
        return workflow.JSONResult(output)
    }

    fragment := workflow.NewFragment()

    fetch := fragment.Step(
        fmt.Sprintf("fetch-page-%d", input.PageNumber+1),
        workflow.Task("scraper.http.fetch", "1"),
        map[string]any{
            "method": "GET",
            "url":    nextURL,
        },
        workflow.Lane("hackernews.http"),
    )

    fragment.Step(
        fmt.Sprintf("parse-page-%d", input.PageNumber+1),
        workflow.Task("hackernews.parse-page", "1"),
        map[string]any{
            "body":       fetch.Output("/body"),
            "baseURL":    nextURL,
            "pageNumber": input.PageNumber + 1,
            "maxPages":   input.MaxPages,
        },
    )

    built, err := fragment.Build()
    if err != nil {
        return workflow.Result{}, workflow.Permanent("FRAGMENT_BUILD_FAILED", err)
    }

    result, err := workflow.JSONResult(output)
    if err != nil {
        return workflow.Result{}, err
    }
    result.Fragment = &built
    return result, nil
}
```

This preserves durable pagination without teaching site authors about leases, raw operation rows, parent IDs, or database mutation.

---

## 86. Site manifests after the refactor

A site manifest should describe application composition rather than engine row fields.

Possible shape:

```yaml
name: hackernews
workflow:
  module: workflows/seed.js
  export: default
lanes:
  hackernews.http:
    maxParallel: 1
capabilities:
  - hackernews/stories
  - scraper/http
migrations: migrations
```

Rate policy may remain a scraper host concern:

```yaml
admission:
  hackernews.http:
    requestsPerSecond: 1
    burst: 1
```

The workflow plan can name the lane but does not encode the token-bucket algorithm.

### 86.1 CLI generation

Glazed/Cobra command generation remains in scraper. A command loads or constructs a plan, validates command input, and calls `Engine.Submit`.

The workflow library should not import command frameworks or generate site commands.

---

## 87. Database projections

Remove projection storage from `TaskContext`.

Three replacement patterns are clearer:

1. a Go handler captures a typed domain repository;
2. a JS task receives a narrow domain module;
3. a workflow publishes an artifact and a downstream projector consumes it.

This makes schema ownership explicit and prevents the generic engine from becoming an application database service locator.

---

## 88. Book OCR fit

The Book OCR use case maps naturally:

```text
inspect book input
  -> dynamic page tasks
  -> final assembly task after all pages
```

Each page task can be retried independently. Completed pages remain successful. A failed page leaves the assembly step derived as blocked. Administrative retry reopens the path without recreating successful pages.

Artifacts:

- raw page image or source PDF;
- provider response, when retention policy permits;
- normalized page text;
- page diagnostics;
- final Markdown or JSONL assembly.

Provider identity and request policy belong in the OCR handler implementation identity and domain records. A full transactional provider budget ledger is optional, not required to represent the workflow.

---

## 89. RAG and research workloads

The new engine can execute research graphs, but it should not own hypotheses, experiment matrices, evidence interpretation, or cache semantics.

A research application should decide:

- which scientific occurrence is required;
- which graph realizes it;
- which outputs are canonical evidence;
- which materializations may be reused;
- which providers and budgets are allowed.

The workflow engine executes or resumes the graph and records what happened.

### 89.1 Materialization cache

Cross-run cache reuse is valuable but should be an explicit layer:

```go
type MaterializationCache interface {
    Lookup(ctx context.Context, key MaterializationKey) (Result, bool, error)
    Store(ctx context.Context, key MaterializationKey, result Result) error
}
```

Cache keys require semantic task input, task implementation identity, environment identity, and artifact identity. This is not safe to infer from plan syntax alone.

A future cache decorator can wrap handlers or integrate into the engine. The v1 design must not claim that content-addressed artifacts alone provide computation reuse.

---

## 90. Scraper API and operator views

The scraper HTTP API should translate workflow snapshots into scraper-facing views. The workflow module offers no Gin routes.

Recommended application endpoints:

```text
POST /scraper/runs
GET  /scraper/runs/:id
GET  /scraper/runs/:id/events
POST /scraper/runs/:id/cancel
POST /scraper/runs/:id/steps/:step/retry
```

The application may add site names, target step IDs, command information, or domain projection links in its own metadata and response types.

---
# Part XV — Implementation guide

## 91. Implementation strategy

Do not begin by copying the existing engine and deleting fields. That preserves accidental boundaries and makes every simplification a compatibility debate.

Implement the new module in vertical slices. Each phase should leave a coherent, tested system. The old scraper engine remains operational until representative workflows run on the new module.

The recommended sequence is:

1. semantic core;
2. in-memory execution;
3. retries, cancellation, and dynamic fragments;
4. artifacts and events;
5. Goja plan authoring;
6. SQLite durability;
7. Goja runtime and JS tasks;
8. scraper adapters and migration;
9. optional distributed claims.

---

## 92. Phase 0 — Architecture decisions and fixtures

Before implementation, write short ADRs for decisions that are costly to reverse.

### ADR-001: One canonical plan

Decision: builder and JavaScript output normalize directly into `Plan`; no mandatory IR/catalog/compiled-plan layers.

### ADR-002: Dependency inference

Decision: step output references imply required dependencies; `After` is ordering-only.

### ADR-003: Stored versus derived state

Decision: persist pending/running/succeeded/failed/canceled; derive ready/retry-wait/blocked.

### ADR-004: Artifact boundary

Decision: repository stores references only; artifact API is streaming.

### ADR-005: JavaScript boundary

Decision: authoring crosses through bounded JSON; no Goja value survives compilation.

### ADR-006: Deployment levels

Decision: local in-memory and local SQLite are v1; leases are a later repository extension.

### ADR-007: External effects

Decision: engine is at-least-once and provides stable idempotency keys.

### ADR-008: Registry update

Decision: engine snapshots registry; implementation update requires a new engine/restart.

### 92.1 Representative fixtures

Create three end-to-end fixtures before writing the scheduler:

1. **linear:** `A -> B -> C`, pure Go tasks;
2. **diamond:** `A -> B`, `A -> C`, then `B+C -> D`, proving parallelism and data resolution;
3. **dynamic:** discovery returns N children plus finalizer, proving atomic expansion and restart behavior.

Add a scraper-specific fourth fixture:

4. **pagination:** fetch/parse recursively discovers the next page.

The same fixtures should later run through memory, SQLite, Go authoring, and JavaScript authoring.

### Exit criteria

- ADRs reviewed;
- fixture plans and expected outputs checked in;
- package import policy documented;
- no production code yet depends on scraper.

---

## 93. Phase 1 — Plan, values, builder, and validation

### 93.1 Files

```text
plan.go
value.go
builder.go
normalize.go
digest.go
diagnostics.go
internal/strictjson/
internal/jsonpointer/
```

### 93.2 Implement `TaskRef`

Functions:

```go
func Task(name, version string) TaskRef
func ParseTask(text string) (TaskRef, error)
func (t TaskRef) String() string
func (t TaskRef) Validate() error
```

Test malformed forms:

```text
""
"fetch"
"@1"
"fetch@"
"Fetch Space@1"
"fetch@1@2"
```

### 93.3 Implement references and JSON Pointer

Do not rely on an unreviewed generic pointer library for core semantics. A small RFC 6901 implementation is manageable.

Functions:

```go
func ValidatePointer(pointer string) error
func ResolvePointer(document json.RawMessage, pointer string) (json.RawMessage, error)
```

Test escaping, arrays, root pointer, missing fields, malformed escapes, and scalar traversal.

### 93.4 Implement `ValueOf`

`ValueOf(any)` recursively converts supported Go values.

Carefully handle:

- `nil`;
- `Ref` and `*Ref`;
- `json.RawMessage`;
- structs through JSON serialization;
- maps with string keys;
- slices and arrays;
- integer width and floating-point non-finite values;
- unsupported channels, functions, complex numbers, and cyclic Go structures.

A safe implementation may marshal ordinary values to JSON and parse into an internal literal, while separately walking maps/slices to preserve nested `Ref` values. Add cycle detection for pointer containers used during recursive conversion.

### 93.5 Implement builder diagnostics

Builder methods should not panic for duplicate IDs or invalid handles. Record diagnostics with paths such as:

```text
/steps/parse/input/html
/steps/fetch/task/version
/outputs/stories
```

`Build()` merges builder diagnostics with normalization diagnostics.

### 93.6 Implement graph validation

Generate inferred edges by walking each step input for refs. Add explicit `After` edges. Deduplicate and cycle-check.

Provide an internal normalized plan representation with cached edge lists if useful, but do not serialize a second public plan type.

### 93.7 Implement canonical digest

Add golden tests. Verify authoring order differences do not change digest when semantics are equal.

### Exit criteria

- plans round-trip through strict JSON;
- invalid plans return stable diagnostics;
- Go builder produces canonical fixtures;
- cycle and reference fuzz tests pass;
- `go test -race ./...` passes for implemented packages;
- root package uses standard library only.

---

## 94. Phase 2 — Registry, handlers, and memory execution

### 94.1 Files

```text
registry.go
handler.go
errors.go
state.go
repository.go
memory_repository.go
engine.go
scheduler.go
clock.go
limits.go
```

### 94.2 Implement registry snapshot

`NewEngine` copies registrations into a private map and sorted list. It rejects duplicates and nil handlers.

### 94.3 Implement handler boundary

The scheduler wrapper should:

1. derive a child context with timeout;
2. create an annotated logger;
3. recover panic;
4. invoke handler;
5. classify context error and task error;
6. validate output JSON and size;
7. return an internal completion message.

It must not write repository state from the handler goroutine except through the scheduler completion path.

### 94.4 Implement memory repository first

The memory repository should be a real state-machine implementation under a mutex, not a special shortcut that bypasses repository commands.

Internals:

```go
type memoryRepository struct {
    mu      sync.Mutex
    runs    map[RunID]*memoryRun
    events  []Event
    nextSeq int64
    closed  bool
}
```

Every method:

- locks;
- checks invariants;
- mutates state;
- constructs post-commit event copies;
- unlocks;
- returns.

This repository becomes the executable specification for SQLite behavior.

### 94.5 Implement synchronous `Run`

Start with one worker, no retries, no dynamic fragments. Get linear and diamond fixtures passing, then add bounded concurrency.

### 94.6 Implement completion-driven concurrency

Use an internal completion channel. Do not use `errgroup.Wait()` over a fixed leased batch in the production loop.

Test with controlled handlers:

```text
lane A: slow 200 ms, fast 10 ms, fast 10 ms
lane B: medium 50 ms
```

Verify the second lane-A task starts immediately after the first fast lane-A slot frees, not after the slow task or a batch boundary.

### Exit criteria

- linear and diamond fixtures run in memory;
- outputs resolve correctly;
- exact concurrency limits are observed;
- missing task is rejected before run creation;
- handler panic is contained;
- snapshots are coherent under `-race`;
- no goroutine leaks under cancellation tests.

---

## 95. Phase 3 — Retries, cancellation, and fragments

### 95.1 Retry implementation

Use a fake clock in tests. Avoid `time.Sleep` in unit tests.

Scenarios:

- retryable failure then success;
- permanent failure;
- retryable failure with attempts exhausted;
- timeout then retry;
- context cancellation without retry;
- deadline persists across engine pause;
- jitter deterministic under fake random source.

### 95.2 Cancellation registry

The engine tracks active attempt cancel functions by claim token:

```go
type activeAttempts struct {
    mu      sync.Mutex
    cancel  map[string]context.CancelFunc
}
```

After durable cancellation commits, cancel matching active handlers. A handler that ignores context may continue running, but its completion is rejected because its claim was invalidated.

### 95.3 Administrative retry

`RetryStep`:

- requires terminal failed step;
- does not delete failure or attempts;
- returns step to pending;
- clears current failure view or archives it in attempt history;
- reopens run from failed to running/pending;
- descendants automatically stop appearing blocked.

### 95.4 Fragment implementation

Implement:

- fragment builder;
- parent/sibling refs;
- namespacing;
- depth and count checks;
- digest conflict checks;
- atomic insertion in memory repository;
- finalizer dependencies.

### 95.5 Atomicity fault injection

Memory repository can expose test-only fault injection points:

```text
before parent output
mid child insertion
before event append
before commit publication
```

Because memory mutations can be staged on a cloned run and swapped at commit, tests can prove no partial fragment is visible.

SQLite will later use real transactions.

### Exit criteria

- dynamic fixture succeeds;
- duplicate identical fragment is idempotent;
- conflicting fragment fails safely;
- expansion bounds are enforced;
- failed dependency yields derived blocked descendants;
- retry reopens descendants;
- cancellation rejects late completion.

---

## 96. Phase 4 — Artifacts and events

### 96.1 File artifact store

Implement and test:

- streaming digest;
- atomic publication;
- duplicate concurrent puts;
- failed reader mid-stream;
- maximum size;
- metadata limits;
- read and digest verification;
- traversal-safe paths;
- orphan tolerance.

### 96.2 Output artifact convention

Add helper types and JSON examples, but do not force a special output schema. An `ArtifactRef` is ordinary JSON embedded in typed output.

### 96.3 Events

Memory repository appends durable in-memory events. The engine delivers post-commit observer events.

Tests:

- observer sees state after snapshot reflects transition;
- observer panic does not fail run;
- observer receives serialized calls if documented;
- event payload size bound;
- sequence monotonicity;
- no input/output bodies leak into default events.

### Exit criteria

- artifact fixture processes a file larger than inline output limit without full repository buffering;
- event recovery by sequence works in memory;
- observer adversarial tests pass.

---

## 97. Phase 5 — Goja authoring

### 97.1 Files

```text
workflow/goja/authoring.go
workflow/goja/authoring.js
workflow/goja/conversion.go
workflow/goja/workflow.d.ts
```

### 97.2 Embedded JavaScript builder

Implement the fluent objects in JavaScript. Keep native calls to normalization and digest.

Use `Object.freeze` for returned refs, handles, and plan objects to catch accidental mutation. Freeze is an ergonomics feature, not a security boundary.

### 97.3 Strict boundary

Before native normalization:

- build a plain serializable spec;
- call `JSON.stringify` once;
- enforce a source byte limit in Go;
- parse through shared `ParsePlanJSON`;
- return canonical JSON;
- parse and deeply freeze the canonical value in JS.

### 97.4 Module registration

Support both:

- a plain `NativeModule` for simple Goja hosts;
- a runtime-aware registrar for the `go-go-goja` factory.

Do not register an engine globally through `init()`.

### 97.5 Tests

- Go/JS equivalence golden;
- duplicate step diagnostics;
- cycle diagnostics;
- forged ref validation;
- functions and undefined values rejected through resulting missing/invalid fields;
- plan object mutation fails or has no effect;
- two runtimes compile independently;
- concurrent separate runtimes do not share builder state;
- no Go pointer to a Goja object retained after compile.

A test can compile a plan, release the runtime, force GC, and prove the Go plan remains usable.

### Exit criteria

- representative fixture authored in JS produces exact canonical digest;
- TypeScript declarations compile in a small fixture project;
- authoring module requires no filesystem, network, DB, or process module.

---

## 98. Phase 6 — SQLite repository

### 98.1 Implement migrations first

Create versioned migration application and schema-open tests before repository methods.

Cases:

- new empty database;
- current database reopen;
- old supported version upgrade;
- newer unknown version rejection;
- interrupted migration transaction;
- foreign keys enabled.

### 98.2 Port command by command

Implement in this order:

1. `CreateRun`;
2. `Snapshot`;
3. `ClaimReady`;
4. `Complete` without fragments;
5. `Fail` and retry deadlines;
6. fragments;
7. cancellation;
8. administrative retry;
9. interrupted recovery;
10. event pagination;
11. run listing and `NextWake`.

For each operation, run the same repository contract tests against memory and SQLite.

### 98.3 Repository conformance suite

Expose a test helper in an internal or testing package:

```go
func RunRepositoryContract(
    t *testing.T,
    factory func(t *testing.T) workflow.Repository,
)
```

Contract scenarios include:

- duplicate run ID;
- create-or-attach identity match and conflict;
- concurrent claims;
- stale claim completion;
- attempt monotonicity;
- retry deadline;
- snapshot atomicity;
- fragment atomicity;
- cancellation fencing;
- recovery;
- event ordering;
- integer time ordering around mixed subsecond values.

### 98.4 Restart tests

Use actual close/reopen boundaries:

1. submit dynamic workflow;
2. complete some children;
3. leave one attempt running;
4. close repository without graceful attempt completion;
5. reopen;
6. recover interrupted attempt;
7. resume;
8. verify completed children were not rerun;
9. verify attempts show interruption and retry.

### Exit criteria

- memory and SQLite pass one conformance suite;
- process-restart fixtures pass;
- no artifact body appears in SQLite;
- database size remains proportional to compact control state in a large fixture;
- timestamps are integer and ordering tests pass.

---

## 99. Phase 7 — Goja runtime and JavaScript handlers

### 99.1 Runtime module

Bind one concrete `Engine` to `workflow/runtime`. Implement Promise APIs using the Goja runtime owner/event loop.

Tests:

- run and await;
- submit then inspect;
- cancel;
- runtime closes while Promise pending;
- Go error becomes structured JS error;
- no VM access from worker goroutine, checked with race tests and owner instrumentation.

### 99.2 JS module handler

Start with fresh runtime per attempt.

Implement:

- module loading;
- named/default export selection;
- task context conversion;
- Promise awaiting;
- structured error helpers;
- output JSON boundary;
- fragment conversion;
- artifact convenience API;
- cancellation and close.

### 99.3 Capability fixtures

Create tests proving:

- authoring profile cannot access process environment;
- task profile sees only selected modules;
- one runtime’s modules do not leak to another;
- domain module captures the correct host repository;
- unregistered generic DB/fs/network modules are unavailable.

### Exit criteria

- Go-authored plan can invoke JS task;
- JS-authored plan can invoke Go task;
- JS runtime client can run both;
- mixed Go/JS dynamic workflow survives SQLite restart;
- no Goja runtime or value is stored in plan or repository.

---

## 100. Phase 8 — Scraper migration

### 100.1 Freeze old engine scope

During migration, new features should target the new module unless needed for production fixes. Avoid continuing to expand both architectures.

### 100.2 Build adapters

Implement in scraper:

- HTTP fetch handler;
- generic legacy JS script handler for transition;
- file artifact store wiring;
- site repository capability modules;
- CLI submit/resume/inspect commands;
- snapshot-to-API translation.

### 100.3 Migrate representative sites

Order:

1. `js-demo` — proves JS task and domain storage;
2. Hacker News — proves HTTP artifact plus parsing plus pagination;
3. Slashdot — proves a second site shape and fan-out;
4. Nereval — proves complex forms and normalized projections;
5. Book OCR — proves large artifacts, dynamic fan-out, retries, and finalization.

### 100.4 Dual-run comparison

For each migrated workflow:

- run existing engine against fixed fixtures;
- run new engine against the same fixtures;
- compare domain database rows;
- compare retained raw and intermediate artifacts;
- compare retry and recovery behavior;
- compare operator-visible status;
- measure database size and execution timing.

Do not compare internal operation IDs when models differ. Compare semantic outputs and observable guarantees.

### 100.5 CLI cutover

Move command generation and default worker path only after fixtures and at least one live bounded run pass.

Keep legacy inspection commands for old databases until the agreed retention period ends. Do not make the new repository silently open or rewrite old engine databases.

### Exit criteria

- default sites run on new engine;
- old and new results match on fixtures;
- restart test passes for a live-site bounded scrape;
- documentation teaches only new API for new sites;
- old engine is read-only or isolated behind a legacy command.

---

## 101. Phase 9 — Distributed extension, only if required

Implement only when two or more worker processes are an actual deployment requirement.

Tasks:

- add worker ID, lease expiry, and cancellation epoch;
- implement transactional lease claim;
- implement heartbeat from current time;
- fence completion and failure;
- add lease-loss attempt state;
- test stale worker adversarially;
- define capacity semantics across workers;
- document at-least-once external effects again.

Do not add registry generations, quarantine, or global budget accounting automatically with leases. They solve separate forces.

---

# Part XVI — Detailed code skeletons

## 102. Minimal user-facing Go program

```go
package main

import (
    "context"
    "fmt"
    "log/slog"
    "os"

    "github.com/go-go-golems/workflow"
)

type DoubleInput struct {
    Value int `json:"value"`
}

type DoubleOutput struct {
    Value int `json:"value"`
}

func main() {
    ctx := context.Background()

    registry := workflow.NewRegistry()
    registry.MustRegister(workflow.Registration{
        Task: workflow.Task("math.double", "1"),
        Handler: workflow.Typed(
            func(
                ctx context.Context,
                tc workflow.TaskContext,
                input DoubleInput,
            ) (DoubleOutput, error) {
                return DoubleOutput{Value: input.Value * 2}, nil
            },
        ),
        ImplementationIdentity: "example:v1",
    })

    builder := workflow.NewPlan("double-twice", workflow.Version("1"))
    initial := builder.Input("/value")

    first := builder.Step(
        "first",
        workflow.Task("math.double", "1"),
        map[string]any{"value": initial},
    )

    second := builder.Step(
        "second",
        workflow.Task("math.double", "1"),
        map[string]any{"value": first.Output("/value")},
    )

    builder.Output("value", second.Output("/value"))

    plan, err := builder.Build()
    if err != nil {
        panic(err)
    }

    engine, err := workflow.NewEngine(workflow.EngineConfig{
        Registry: registry,
        Logger:   slog.New(slog.NewTextHandler(os.Stderr, nil)),
    })
    if err != nil {
        panic(err)
    }
    defer engine.Close()

    result, err := engine.Run(ctx, plan, map[string]any{"value": 21})
    if err != nil {
        panic(err)
    }

    fmt.Println(string(result.Outputs["value"])) // 84
}
```

This is the complexity target for ordinary Go use.

---

## 103. Durable Go program

```go
repo, err := sqlite.Open(sqlite.Config{
    Path: "runs.db",
})
if err != nil {
    return err
}

defer repo.Close()

artifacts, err := workflow.NewFileArtifactStore("artifacts")
if err != nil {
    return err
}

engine, err := workflow.NewEngine(workflow.EngineConfig{
    Registry:   registry,
    Repository: repo,
    Artifacts:  artifacts,
    Limits: workflow.Limits{
        MaxParallel: 8,
        LaneParallel: map[string]int{
            "network": 2,
            "cpu":     6,
        },
    },
})
if err != nil {
    return err
}

runID, err := engine.Submit(
    ctx,
    plan,
    input,
    workflow.WithRunKey("hackernews:2026-07-28T18:00Z"),
)
if err != nil {
    return err
}

result, err := engine.Resume(ctx, runID)
```

The authored plan did not change when durability was added.

---

## 104. Handler execution wrapper

Conceptual internal code:

```go
func (e *Engine) executeClaim(
    parent context.Context,
    claimed ClaimedStep,
) completionMessage {
    registration, ok := e.registry.Lookup(claimed.Claim.Task)
    if !ok {
        return completionMessage{
            Claim: claimed.Claim,
            EngineError: fmt.Errorf(
                "task implementation unavailable: %s",
                claimed.Claim.Task,
            ),
        }
    }

    input, err := ResolveValue(
        claimed.Spec.Input,
        claimed.RunInput,
        claimed.DependencyOutputs,
    )
    if err != nil {
        return taskFailureMessage(
            claimed.Claim,
            Permanent("INPUT_RESOLUTION_FAILED", err),
        )
    }

    ctx := parent
    cancel := func() {}
    if claimed.Spec.TimeoutMillis > 0 {
        ctx, cancel = context.WithTimeout(
            parent,
            time.Duration(claimed.Spec.TimeoutMillis)*time.Millisecond,
        )
    }
    defer cancel()

    logger := e.logger.With(
        "run_id", claimed.Claim.RunID,
        "step_id", claimed.Claim.StepID,
        "task", claimed.Claim.Task.String(),
        "attempt", claimed.Claim.Attempt,
    )

    taskContext := TaskContext{
        RunID:          claimed.Claim.RunID,
        StepID:         claimed.Claim.StepID,
        Attempt:        claimed.Claim.Attempt,
        Input:          input,
        IdempotencyKey: operationKey(
            claimed.Claim.RunID,
            claimed.Claim.StepID,
        ),
        Logger:    logger,
        Artifacts: e.artifacts,
    }

    result, runErr := safeRunHandler(
        ctx,
        registration.Handler,
        taskContext,
    )
    return classifyCompletion(claimed.Claim, result, runErr)
}
```

The code that persists the returned completion runs in the scheduler owner, not inside `safeRunHandler`.

---

## 105. Memory repository completion sketch

```go
func (r *memoryRepository) Complete(
    ctx context.Context,
    cmd CompleteAttempt,
) error {
    r.mu.Lock()
    defer r.mu.Unlock()

    run := r.runs[cmd.Claim.RunID]
    if run == nil {
        return ErrRunNotFound
    }

    step := run.steps[cmd.Claim.StepID]
    if step == nil {
        return ErrStepNotFound
    }

    if step.status != StepRunning ||
        step.claimToken != cmd.Claim.Token {
        return ErrClaimLost
    }

    staged := run.clone()
    stagedStep := staged.steps[cmd.Claim.StepID]

    if err := staged.applyOutputAndFragment(cmd); err != nil {
        return err
    }

    stagedStep.status = StepSucceeded
    stagedStep.claimToken = ""
    stagedStep.output = cloneRaw(cmd.Output)
    stagedStep.updatedAt = cmd.FinishedAt

    staged.finishAttempt(cmd.Claim, AttemptSucceeded, cmd.FinishedAt, nil)
    staged.recomputeRunStatus(cmd.FinishedAt)
    staged.appendSuccessEvents(cmd)

    r.runs[cmd.Claim.RunID] = staged
    r.publishWake()
    return nil
}
```

Staging on a clone is not required for every implementation, but it makes atomic fragment tests straightforward in memory.

---

## 106. SQLite claim sketch

Pseudocode, not driver-specific production code:

```go
func (s *Store) ClaimReady(
    ctx context.Context,
    req workflow.ClaimRequest,
) (*workflow.ClaimedStep, error) {
    tx, err := s.beginImmediate(ctx)
    if err != nil {
        return nil, err
    }
    defer tx.Rollback()

    candidate, err := selectReadyCandidate(ctx, tx, req)
    if errors.Is(err, sql.ErrNoRows) {
        return nil, tx.Commit()
    }
    if err != nil {
        return nil, err
    }

    token, err := randomToken()
    if err != nil {
        return nil, err
    }

    attempt := candidate.AttemptCount + 1
    nowUS := toMicros(req.Now)

    changed, err := guardedMarkRunning(
        ctx, tx, candidate, token, attempt, nowUS,
    )
    if err != nil {
        return nil, err
    }
    if changed != 1 {
        return nil, workflow.ErrClaimRace
    }

    if err := insertAttempt(ctx, tx, ...); err != nil {
        return nil, err
    }
    if err := appendEvent(ctx, tx, ...); err != nil {
        return nil, err
    }

    claimed, err := loadClaimedStep(ctx, tx, candidate, token, attempt)
    if err != nil {
        return nil, err
    }

    if err := tx.Commit(); err != nil {
        return nil, err
    }
    return &claimed, nil
}
```

Use guarded updates even inside a serialized transaction. They make assumptions explicit and improve diagnostics.

---
# Part XVII — Testing strategy

## 107. Test pyramid

The framework’s correctness depends more on state transitions and boundaries than on individual algorithms. Tests should therefore be organized around contracts and adversarial sequences.

### Unit tests

Cover:

- task reference parsing;
- pointer parsing and resolution;
- value conversion;
- normalization;
- graph cycles;
- digest stability;
- backoff calculation;
- error classification;
- fragment namespacing;
- artifact path validation.

### Repository contract tests

Run exactly the same transition scenarios against memory and SQLite.

### Engine integration tests

Use deterministic handlers, fake clocks, and controlled channels to prove scheduling, retries, cancellation, and dynamic behavior.

### Goja boundary tests

Use real runtimes and event loops. Test lifecycle, concurrency, Promise settlement, module isolation, and serialization.

### Application migration tests

Use fixed HTML/PDF fixtures and compare domain outputs between old and new scraper paths.

### Adversarial tests

Inject failures at transaction boundaries, artifact publication, observer delivery, runtime shutdown, and lease expiry.

---

## 108. Builder and compiler tests

### 108.1 Table tests

Create one test case per diagnostic code. Verify code and path, not only message text.

### 108.2 Fuzz plan parsing

Fuzz `ParsePlanJSON` with arbitrary bytes. Required property:

- no panic;
- bounded memory according to input limit;
- either valid normalized plan or diagnostics;
- re-marshaling a valid plan parses identically.

### 108.3 Fuzz JSON Pointer

Generate JSON documents and pointers. Compare behavior with a small independent reference implementation or property checks.

### 108.4 Graph property tests

Generate acyclic graphs, normalize, and verify topological order. Add one back-edge and verify cycle detection.

### 108.5 Digest properties

Verify:

- map insertion order does not change digest;
- normalized empty values do not produce multiple digests;
- changing task version changes digest;
- changing literal input changes digest;
- changing metadata changes digest under v1 policy;
- authoring order changes only display order, not semantic digest, when graph and fields are equal.

---

## 109. Scheduler tests

### 109.1 Controlled handler

Build a reusable test handler:

```go
type ControlledHandler struct {
    Started chan AttemptKey
    Release map[AttemptKey]chan Outcome
}
```

The handler announces start and waits for the test to release a result. This lets tests assert exact scheduling order without sleeps.

### 109.2 Work conservation

Scenario:

- global capacity 3;
- lane `network` capacity 2;
- lane `cpu` capacity 1;
- three network tasks and two CPU tasks ready;
- one network task completes early.

Assert the third network task starts immediately while the first CPU and second network task remain running.

### 109.3 Dependency barrier

In a diamond graph, final step must not start until both branches succeed.

### 109.4 Failure cancellation

One branch fails terminally while another handler is running. Assert:

- run becomes failed;
- running handler context is canceled;
- late success cannot commit;
- final step appears blocked;
- successful completed branch remains recorded.

### 109.5 Retry timing

With fake clock:

- fail at T0;
- next ready time T0+1s;
- advancing 999ms does not claim;
- advancing 1ms allows claim;
- attempt number increments.

### 109.6 Engine shutdown

Close engine with active handlers. Define and test graceful behavior:

- stop claiming new work;
- cancel active local handlers;
- wait up to configured grace period;
- repository claims left running are recovered on next open if handlers do not stop.

---

## 110. State-machine model tests

For high confidence, implement a small pure reference model in tests.

Generate random command sequences:

```text
create
claim
complete
fail retryable
fail permanent
cancel
retry step
recover
snapshot
```

Apply each sequence to:

- pure model;
- memory repository;
- SQLite repository.

Compare normalized snapshots and events after every command.

This catches transition divergence that example tests miss.

---

## 111. Fragment tests

Required cases:

- zero-child fragment;
- one child;
- sibling dependency;
- finalizer after N children;
- nested fragments;
- max-depth rejection;
- max-count rejection;
- duplicate key in one fragment;
- absolute ID collision;
- identical retry insertion;
- conflicting retry insertion;
- cycle within fragment;
- sibling reference to unknown key;
- parent reference resolution;
- crash/fault before commit leaves no child visible.

Use stable expected absolute IDs as golden fixtures.

---

## 112. Artifact tests

### 112.1 Large stream

Generate a deterministic stream larger than memory thresholds without allocating it all at once. Put, reopen, and verify digest and byte count.

### 112.2 Interrupted source

A reader returns an error midway. Assert no final object or metadata is published.

### 112.3 Concurrent duplicate

Multiple goroutines put identical content. Assert all receive the same digest and one final object exists.

### 112.4 Corruption

Modify object bytes after publication. Assert verification fails closed rather than treating it as a cache miss or returning silent corruption.

### 112.5 Path safety

Malicious names and locators must not escape the root. The digest determines storage path; display name never does.

---

## 113. SQLite tests

### 113.1 Time ordering regression

Use times with and without fractional seconds whose RFC3339 lexical order differs from chronological order. Assert integer predicates recover the correct step or lease.

### 113.2 Concurrent claim

Open multiple connections and race `ClaimReady`. Exactly one receives a step.

### 113.3 Stale claim

Claim, invalidate through cancellation or recovery, then attempt completion. Expect `ErrClaimLost` and no output mutation.

### 113.4 Read snapshot during writes

Continuously read snapshots while steps complete and expand. Every snapshot must satisfy invariants; no partial fragment or mismatched attempt/step status.

### 113.5 WAL growth

Run a fixture with thousands of compact steps and external artifacts. Measure database and WAL growth. Set a regression threshold so artifact or source bodies do not accidentally return to control rows.

### 113.6 Migration fixtures

Keep one database file per schema version in `testdata/migrations`. Upgrade and verify state.

---

## 114. Goja tests

### 114.1 Authoring equivalence

Go and JS definitions produce the same canonical plan.

### 114.2 Runtime ownership

Instrument runtime owner calls. Assert all Promise resolution and JS object conversion occurs through the owner.

### 114.3 Multiple runtimes

Create two runtimes with different engine instances and task sets. Assert no cross-talk.

### 114.4 Cancellation

Start a Promise-returning JS task that waits. Cancel context and assert runtime closes or interrupt is delivered, attempt records cancellation, and no Promise is resolved from a foreign goroutine.

### 114.5 Capability absence

In data-only profile, attempts to require filesystem, process, generic DB, and network modules fail.

### 114.6 Resource retention

Run many short JS tasks, close runtimes, and use leak-sensitive tests or profiling to detect retained event loops, timers, or source modules.

---

## 115. Failure-injection matrix

A durable system should enumerate crash points.

| Point | Expected recovery |
|---|---|
| after run inserted, before static steps | transaction rollback; no run |
| after claim commit, before handler starts | running attempt recovered as interrupted |
| after external effect, before artifact put | task/domain idempotency handles retry |
| after artifact put, before completion | orphan artifact; task may retry safely |
| during fragment validation | no parent completion or children |
| after fragment rows staged, before commit | transaction rollback |
| after completion commit, before observer | state correct; observer may miss live event |
| observer panic | state remains committed |
| process exits during retry wait | persisted deadline remains |
| cancellation commits while handler returns | claim rejected; canceled state wins |
| distributed lease expires before completion | fenced completion rejected |

Turn every row into an automated test where feasible.

---

## 116. Benchmarks

Benchmark only after correctness tests exist.

Useful benchmarks:

- plan normalization for 10, 1,000, and 100,000 steps;
- JSON Pointer resolution;
- memory repository claim/complete throughput;
- SQLite claim/complete throughput under WAL;
- snapshot generation for large runs;
- artifact streaming throughput;
- Goja runtime creation and module loading;
- JS handler execution with fresh runtime versus pool;
- scheduler overhead for no-op tasks.

Performance targets should be based on actual scraper workloads. Avoid adding pooling, custom codecs, or denormalized state solely from microbenchmarks.

---

# Part XVIII — Migration from the current codebase

## 117. Migration principle

Migrate semantics, not storage rows or type names.

The old engine and Workflow V3 have different assumptions. An automatic translator risks preserving precisely the complexity the new design is intended to remove.

The migration should allow:

- old runs to finish or remain inspectable in the old engine;
- new runs to use the new engine;
- application commands to select the correct backend during transition;
- domain artifacts and projections to be compared;
- old code to be deleted after a defined retention period.

---

## 118. Concept mapping

| Existing concept | New concept | Action |
|---|---|---|
| `model.WorkflowRun` | `RunSnapshot` / stored run | replace |
| `model.OpSpec` | `StepSpec` plus mutable step row | split definition from state |
| `runner.Runner` | `Handler` | replace with smaller context |
| `runner.RunContext` | `TaskContext` | remove lease and DB services |
| `workflow.Package` | ordinary plan factory | remove package registry from core |
| `workflow.Entrypoint` | Go or JS function returning `Plan` | replace |
| `RunBuilder.Step` | canonical plan builder | rewrite |
| `StepContext.Emit` | returned bounded `Fragment` | replace |
| `StepContext.Record` | domain repository or output artifact | move out of core |
| `StepContext.Projection` | injected typed repository | move out of core |
| inline `ArtifactWrite.Body` | external `ArtifactRef` | migrate data plane |
| `SiteName` | scraper metadata/composition | remove from core |
| queue key/token bucket | engine lane plus scraper admission | split |
| stored `blocked` | derived view | stop persisting |
| observer | post-commit observer | retain simplified |
| snapshots | `RunSnapshot` | retain, redesign |
| V3 WorkflowIR/Plan | one normalized `Plan` | collapse |
| V3 catalog/registry generation | engine registry snapshot | defer hot reload |
| V3 task bundle | handler registration identity | optional record |
| V3 maps/reductions/gates/budgets | fragments or later extensions | defer |

---

## 119. Legacy JS migration

Current scripts expect a broad `ctx` with dependency lookups, emit, databases, artifacts, workflow, operation, and lease fields.

A direct compatibility context would perpetuate the old model. Use a temporary adapter with a deletion plan.

### 119.1 Temporary legacy task

Register:

```text
scraper.legacy-js@1
```

It:

- loads one old script;
- constructs a restricted compatibility context;
- maps resolved input into `ctx.input`;
- maps artifact references to bounded compatibility views;
- captures `ctx.emit` calls into a `Fragment` rather than repository mutation;
- routes database access through existing trusted modules;
- ignores or rejects lease-specific behavior;
- converts the old return envelope into `Result`.

### 119.2 Constraints

- no new scripts should target the compatibility API;
- each use is tracked in a migration inventory;
- artifact body text has a strict limit;
- raw scraper DB access is disabled unless required;
- generated fragments are validated by the new engine;
- compatibility code lives in scraper, not the workflow module.

### 119.3 Rewrite endpoint

Each migrated script becomes either:

- a plan definition using `require("workflow")`;
- a JavaScript task module using the new task context;
- a Go handler with a narrow domain repository.

Delete compatibility support when the inventory reaches zero.

---

## 120. Database migration policy

Do not migrate live old engine rows into the new schema automatically.

Reasons:

- old operation input may contain runner-specific metadata;
- parent and dynamic emission semantics differ;
- stored blocked/canceled meanings differ;
- artifacts may be inline BLOBs;
- result records and projections have no direct core equivalent;
- operation IDs may not satisfy new namespacing rules;
- run status may be derived differently.

Preferred policy:

```text
old DB: read-only legacy inspection and completion with old binary
new DB: all new submissions
```

If business requirements demand conversion of a specific unfinished run, write a one-off semantic exporter/importer for that workflow type with a signed conversion report. Do not call it a general migration.

---

## 121. Artifact migration

Existing inline artifacts can be exported to the file artifact store:

1. read old artifact row;
2. stream body to new artifact store;
3. verify digest and size;
4. write a migration manifest mapping old artifact ID to new `ArtifactRef`;
5. leave old database unchanged;
6. use the manifest only for newly imported semantic runs or domain records.

This can be a maintenance command in scraper.

---

## 122. Operational rollout

Recommended rollout:

### Stage A — library only

New module and tests exist, no production commands.

### Stage B — shadow fixture runs

CI runs old and new implementations against site fixtures.

### Stage C — opt-in command

Add:

```text
scraper workflow2 run ...
```

or a backend flag restricted to developers.

### Stage D — bounded live sites

Run low-volume Hacker News and Slashdot workflows with separate databases and artifact roots.

### Stage E — default for new submissions

Old engine remains available for old runs.

### Stage F — remove old authoring path

No new old-style site scripts or packages.

### Stage G — retire old worker

After old runs are terminal or archived, remove scheduler/bootstrap code and legacy dependencies.

---

## 123. Metrics for migration success

Measure:

- lines and concepts required for a new site workflow;
- number of packages imported by the core;
- time from process restart to resumed execution;
- database bytes per completed step;
- artifact bytes mistakenly stored inline;
- task throughput and lane utilization;
- number of configuration fields required for in-memory and durable modes;
- number of legacy JS scripts remaining;
- operator ability to explain a failed run from one snapshot;
- equivalence of domain outputs on fixtures.

A successful simplification is observable in both developer experience and system behavior.

---

# Part XIX — Alternatives considered

## 124. Keep the current engine and add a thinner facade

### Advantages

- least code movement;
- preserves tested durability;
- immediate compatibility;
- no migration of operators or scripts.

### Rejection reason

The current public facade already demonstrates the limit of this approach. A thinner layer can rename methods but cannot remove scraper concepts, SQLite-first construction, raw operation emission, broad task context, inline artifact assumptions, or derived state transitions without changing the lower model.

Use the old engine for old runs, not as the semantic core of the new API.

---

## 125. Adopt Workflow V3 as-is

### Advantages

- strong compiled identity;
- compact artifacts;
- careful leases and attempts;
- bounded maps and reductions;
- budgets, gates, isolation, and observations;
- defensive engineering.

### Rejection reason

Its minimum concept set is too large for the requested reusable Go/Goja library. It also centers static task packages and a substantial JavaScript compiler/runtime product before offering the most ordinary task adapters.

Retain its lessons and selectively port mechanisms when their forces appear.

---

## 126. Use plain Go orchestration only

### Advantages

- maximum readability;
- typed control flow;
- no workflow schema;
- simple debugging;
- excellent fit for one application.

### Rejection reason

The project explicitly needs reusable plan authoring from both Go and Goja, durable inspection, dynamic graphs, and restartable execution. Plain Go commands remain a good application pattern, but they do not satisfy the shared plan requirement.

The proposed framework stays small enough that applications can still use plain Go around it.

---

## 127. Store Go callbacks in the plan

### Advantages

- very ergonomic local API;
- strong static types;
- no task registry.

### Rejection reason

Callbacks cannot be serialized, authored from JavaScript, resumed in another process, inspected, or compared by digest. Register handlers separately from data-only plans.

---

## 128. Make JavaScript the canonical plan representation

### Advantages

- expressive authoring;
- easy dynamic generation;
- fewer JSON types.

### Rejection reason

JavaScript source is not a stable cross-language execution contract. It introduces runtime ownership, source loading, and capability questions into every host. JavaScript should generate the canonical plan, not replace it.

---

## 129. Persist `ready` and `blocked`

### Advantages

- simple status queries;
- explicit operator state;
- can reduce dependency joins.

### Rejection reason

These are derived facts. Persisting them creates refresh loops, repair transitions, and more opportunities for divergence. Start with derivation; denormalize later only after measurement, with invariant-repair tests.

---

## 130. Put rate limits in every plan step

### Advantages

- self-contained operational policy;
- scheduler can enforce centrally.

### Rejection reason

Rate policy is deployment- and provider-specific. A plan that says “one request per second” may be wrong when several plans share one provider account. Lanes and an optional admission service separate computation intent from shared authority.

---

## 131. First-class map, reduce, and gates in v1

### Advantages

- concise large workflows;
- clear specialized semantics;
- direct parity with sophisticated systems.

### Rejection reason

Bounded fragments cover current scraping and OCR needs with fewer concepts. Large lazy maps, reduction trees, and approval gates should be added only with real workloads and precise persistence semantics.

---

## 132. Event sourcing as the sole state model

### Advantages

- complete history;
- replay and audit;
- append-only writes.

### Rejection reason

It adds projection consistency, schema evolution, replay, snapshotting, and debugging complexity. The project needs append-only attempts and durable events, not a fully event-sourced database. Current state tables plus transition events are simpler.

---

## 133. Generic service locator in task context

### Advantages

- easy extension;
- fewer handler constructors;
- dynamic capability lookup.

### Rejection reason

It hides dependencies, complicates testing, weakens capability boundaries, and recreates `site-db`/`scraper-db` coupling. Use constructor injection and explicit narrow modules.

---

# Part XX — Review checklist and definition of done

## 134. API simplicity checklist

A v1 release is not ready unless:

- a two-step in-memory Go workflow requires no database or worker configuration;
- the same plan can be expressed in JavaScript without queue, lease, or script metadata;
- adding SQLite changes engine construction, not the plan;
- a handler does not receive repository or lease access;
- a large artifact never passes through a repository `[]byte` field;
- data references infer dependencies;
- a new developer can explain all stored statuses in one paragraph;
- the core root package has no third-party dependencies;
- task implementation update is documented as engine restart;
- optional distributed code is absent from the default execution path.

---

## 135. Correctness checklist

- plan normalization is strict and deterministic;
- cycles and missing refs are rejected before submission;
- attempt numbers are append-only and monotonic;
- current claim is verified on every terminal transition;
- cancellation wins over late completion;
- retry deadlines survive restart;
- dynamic insertion is atomic with parent success;
- identical dynamic IDs cannot change specification;
- snapshots never expose partial transitions;
- observer failure cannot alter state;
- artifact publication is atomic and digest-checked;
- integer database time is used for comparisons;
- external side effects are documented as at-least-once;
- Goja values never enter durable state;
- Goja runtime access is owner-mediated.

---

## 136. Documentation checklist

The release should include:

- a ten-minute Go tutorial;
- a ten-minute JavaScript authoring tutorial;
- a durable SQLite tutorial;
- task handler guide;
- artifact guide;
- retries and idempotency guide;
- dynamic fragment guide;
- Goja capability guide;
- state-machine reference;
- repository adapter contract;
- migration guide for scraper sites;
- operational troubleshooting guide;
- explicit non-goals and deployment-level table.

Documentation examples must be executable tests where practical.

---

## 137. Security checklist

- plan and input size limits enforced at every boundary;
- strict unknown-field rejection;
- artifact locators traversal-safe;
- artifact digests verified;
- failure and event payloads bounded;
- credentials absent from plan and snapshot fixtures;
- process environment unavailable in authoring profile;
- generic DB/fs/network unavailable unless selected;
- untrusted JS rejected from in-process profile;
- command adapter uses allowlists and clean environment;
- no user-provided string becomes SQL identifier;
- observer cannot block state transaction;
- panic stacks logged but not durably exposed by default.

---

## 138. Performance checklist

- scheduler refills on individual completion;
- no fixed-batch barrier in `Serve`;
- repository transactions exclude task work;
- plan/input stored once per run;
- artifact bytes excluded from SQLite;
- large snapshots paginated;
- Goja runtime pooling introduced only after profiling;
- dependency queries indexed;
- WAL checkpoint policy documented;
- limits prevent unbounded fragment materialization.

---

## 139. Definition of done for the fresh framework

The first stable release is complete when all of the following are true:

1. Go and JavaScript author the same canonical plan fixtures.
2. Memory and SQLite pass the same repository contract suite.
3. Linear, diamond, dynamic fan-out, and pagination fixtures run on both repositories.
4. A process-restart test resumes without rerunning completed independent work.
5. A failed prerequisite produces derived blocked descendants; retry reopens them.
6. A canceled or stale claim cannot commit output.
7. Artifacts larger than inline limits stream through the file store.
8. A Go plan can invoke a JS task, and a JS plan can invoke a Go task.
9. Goja Promise resolution obeys runtime ownership under the race detector.
10. Hacker News fixture output matches the old implementation semantically.
11. One bounded live scrape completes, is interrupted, and resumes.
12. New-site documentation contains no old `OpSpec`, lease, site DB service locator, or raw queue API.
13. The old engine is not imported by the new workflow module.
14. The root package has a small dependency and concept surface suitable for third-party reuse.

---
# Part XXI — Final architectural decision

## 140. Current versus proposed architecture

| Concern | Current main direction | Workflow V3 direction | Proposed fresh framework |
|---|---|---|---|
| Authoring unit | package entrypoint or JS emit script | Goja builder handles and typed IR | one data-only `Plan` from Go or JS |
| Execution unit | operation with runner kind | compiled node with implementation identity | step with logical `TaskRef` |
| Basic runtime | durable SQLite scheduler | durable product application | in-memory by default; SQLite adapter |
| Dependencies | explicit operation dependency objects | typed value/set references plus explicit dependencies | refs infer edges; `After` for ordering |
| Dynamic work | task directly emits operations | first-class maps/reductions and runtime expansion | bounded returned `Fragment` |
| Task context | workflow, op, lease, DBs, dependencies, sinks | runtime/task modules and artifact bindings | resolved input, IDs, logger, artifact store |
| Scraper domain | site and queue in core model | more domain-neutral, but platform-heavy | entirely downstream integration |
| Artifacts | inline BLOBs and external-ref facade | content-addressed refs | streaming refs from first release |
| Scheduling | durable queues, token buckets, batched cycles | resource-class dispatcher | completion-driven local lanes |
| Durability | mandatory public-runtime assumption | mandatory product center | optional repository |
| Multi-process | leases in base engine | leases/cancel epochs in base runtime | optional leasing repository |
| Implementation identity | runner kind and process registration | bundle, entrypoint, ABI, generation | optional identity recorded per attempt |
| Goja | broad submit/execute contexts | compiler frontend and task runtime | plan adapter plus task adapter |
| Database access | generic scraper/site DB services | trusted modules | constructor injection or narrow modules |
| Advanced policy | queue rates in runtime | budgets, gates, isolation, ledger | deferred adapters |

The proposed design does not attempt to be less capable forever. It sequences capability according to demonstrated forces.

---

## 141. Non-negotiable invariants

A future implementation review should reject changes that violate these invariants without an explicit ADR:

1. A plan is data-only and language-neutral.
2. A task handler never sees an engine lease token.
3. Large bytes do not enter workflow control rows.
4. Completion and dynamic insertion are one atomic transition.
5. Attempts are append-only.
6. Data references imply dependencies.
7. Ready and blocked are derived in v1.
8. The default engine runs without SQLite or Goja.
9. Go and JavaScript use the same normalizer.
10. No Goja value survives compilation or crosses worker goroutines.
11. Observer failure cannot change workflow truth.
12. External effects are explicitly at-least-once.
13. Multi-process safety is not claimed unless fencing is enabled.
14. Scraper concepts remain in scraper integrations.
15. Every new mechanism names the concrete risk that pays for it.

---

## 142. Questions intentionally left open

Some details should be settled during implementation with prototypes and tests rather than fixed prematurely.

### 142.1 Exact JSON `Value` wire syntax

The tagged representation is robust but verbose. A concise human syntax may be desirable. Any alternate syntax must normalize into the same canonical type and must not make literal objects ambiguous.

### 142.2 Run failure policy extensions

V1 is fail-fast and all steps are required. Optional branches or “always-run” finalizers may be useful later, but they need explicit result and cancellation semantics.

### 142.3 Artifact stream support in JavaScript

Goja byte/string helpers are enough for small artifacts. True streaming needs careful event-loop and backpressure design. Do not simulate streaming while buffering whole content internally.

### 142.4 Snapshot pagination API

Small runs can use one snapshot. Very large runs need paging, filtering, and summary counts. Implement the simple API first, then measure real run sizes.

### 142.5 Handler environment identity

Recording a Git or script digest is useful. Exact reconstruction may later require Go toolchain, OS, container, module lock, or hardware identities. Keep an extensible attempt identity record, but do not require every dimension in v1.

### 142.6 Cache integration point

A cache can wrap handlers or be integrated before admission in the engine. The right choice depends on cross-run research requirements and whether cache hits should appear as attempts. Treat caching as a separate design project.

---

## 143. First implementation tasks for a new developer

A new developer should begin in this order:

1. Read Parts II through V to understand the vocabulary, plan, handler, and state model.
2. Implement `TaskRef`, `Ref`, `Value`, strict parsing, and JSON Pointer resolution.
3. Implement the Go builder and diagnostic suite.
4. Build linear and diamond canonical fixtures.
5. Implement the memory repository and one-worker engine.
6. Add controlled-handler tests before adding concurrency.
7. Add completion-driven concurrency and fake-clock retries.
8. Add fragments and atomic memory staging.
9. Add artifact streaming.
10. Only then begin SQLite or Goja.

The first pull request should not include a database, JavaScript, HTTP, CLI, or scraper adapter. It should establish the semantic core and golden fixtures.

---

## 144. Suggested pull request sequence

Keep review units small enough that invariants can be checked.

```text
PR 01  plan types, strict JSON, refs, JSON Pointer
PR 02  builder, diagnostics, cycle detection, canonical digest
PR 03  registry, handler contract, typed adapter
PR 04  memory repository and sequential engine
PR 05  completion-driven concurrency and cancellation
PR 06  retry timing and administrative retry
PR 07  fragment builder and atomic expansion
PR 08  artifact interface and file CAS
PR 09  events, observer, snapshots
PR 10  Goja authoring module and TypeScript declarations
PR 11  SQLite schema and repository conformance
PR 12  SQLite restart and failure-injection tests
PR 13  Goja runtime module
PR 14  JavaScript module handler and capability profiles
PR 15  scraper HTTP and legacy-JS adapters
PR 16  Hacker News fixture and live bounded migration
PR 17  remaining sites and old-engine retirement plan
```

Each PR should update executable examples and the definition-of-done matrix.

---

## 145. Evidence map from the reviewed project

The following source areas motivated this design.

### Current scraper main

- `README.md` and `pkg/doc/topics/scraper-architecture-overview.md` describe the split between durable Go engine, JavaScript site behavior, manifests, CLI, and site databases.
- `pkg/engine/model/types.go` shows scraper/site, queue, retry, lease, result, record, artifact, and emitted-operation concepts in one model.
- `pkg/engine/scheduler/scheduler.go` contains durable queue selection, concurrent leased batches, heartbeat supervision, runner invocation, retry classification, status refresh, and observer delivery.
- `pkg/engine/store/sqlite/*` demonstrates the valuable transaction and lease hardening work, as well as the cost of persisted dependency-derived state.
- `pkg/workflow/*` demonstrates a friendlier public facade that still maps directly onto engine operations.
- `pkg/workflow/context.go` illustrates the broad task context that this proposal narrows.
- `pkg/doc/topics/scraper-js-api-reference.md` and `sites/hackernews/*` show JavaScript authors specifying raw runner kinds, queues, deduplication, dependencies, script metadata, database writes, artifact body access, and dynamic operation emission.

### Linked project notes

- `Research/KB/Projects/scraper.md` frames the durable runtime as a reusable project and emphasizes restartability, auditability, explicit stages, raw/intermediate artifact retention, validation, provider identity, and manual repair.
- `ARTICLE - Scraper Workflow API - Building a Public Reusable Durable Workflow Runtime.md` documents the facade strategy and its broad `StepContext`.
- `ARTICLE - Hardening Scraper for Long-Running Resumable Workflows.md` records the essential lessons around numeric time, lease ownership, heartbeats, stale completion, blocked versus canceled, concurrency, observers, and snapshots.
- `ARTICLE - Scraper Workflow V3 - Compact Durable Dataflow and Typed JavaScript.md` documents the compact-control-plane and work-conserving motivations, along with the expanded compiler/runtime architecture.
- `PROJECT REPORT - rag-ttc - Simplifying a Recoverable and Measurable RAG Experiment System.md` provides a useful counterexample: stable generic mechanisms can be extracted without converting every application sequence into a workflow platform.

### Workflow V3 branch

- `pkg/workflowv3/types.go` shows the large base vocabulary: task and bundle identity, isolation, budgets, value and set refs, maps, reductions, gates, compiled plan nodes, attempts, and leases.
- `pkg/workflowv3/compiler.go` centralizes extensive policy and graph validation.
- `pkg/gojamodules/workflow/authoring.go` demonstrates the cost of Goja object-identity maps and active compiler state.
- `pkg/workflowv3runtime/engine.go` demonstrates the number of runtime subsystems required once all advanced features are mandatory.

### Goja host

- `go-go-goja/modules/common.go` defines native module registration.
- `go-go-goja/pkg/engine/factory.go` provides runtime factories, event loops, runtime ownership, lifetime contexts, and per-runtime module composition.
- `go-go-goja/pkg/engine/module_specs.go` shows runtime-aware registrars and that environment/process authority can remain opt-in.
- `go-go-goja/pkg/doc/02-creating-modules.md` documents native modules and TypeScript declarations.

This proposal deliberately preserves the strongest invariants from those sources while reducing the minimum authoring and hosting surface.

---

## 146. Final recommendation

Do not continue evolving `pkg/workflow` as a facade over the scraper engine, and do not make Workflow V3 the default reusable package.

Build a new standalone module with this center:

```text
Go or JavaScript builder
        -> normalized data-only Plan
        -> Engine with frozen task registry
        -> memory or SQLite Repository
        -> Go, JS, command, or remote Handler
        -> compact JSON output plus ArtifactRef values
```

The core should make the common case obvious:

```text
define steps
register handlers
run
```

Durability should add:

```text
provide SQLite repository
resume after restart
```

Distributed execution should add:

```text
provide leasing repository
supervise heartbeats
fence stale completion
```

No lower level should require vocabulary from a higher one.

The decisive design sentence is:

> The plan describes computation, the registry supplies capabilities, the repository records execution, and adapters decide where and how tasks run.

That boundary is small enough for a Go package, stable enough for durable state, and clean enough to expose through Goja without maintaining a second workflow system.
