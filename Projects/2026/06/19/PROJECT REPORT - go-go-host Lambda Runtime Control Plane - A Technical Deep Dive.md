---
title: "go-go-host Lambda Runtime Control Plane — A Technical Deep Dive"
aliases:
  - go-go-host lambda control plane
  - HOST-013-LAMBDA-RT-CTRL
  - go-go-host warm pool runtime
  - go-go-host function invocation
  - go-go-host on-demand functions
tags: [project-report, go-go-host, lambda, runtime, control-plane, warm-pool, goja, goja-vm, javascript-runtime, event-sources, invocation, functions, go]
status: active
type: project-report
created: 2026-06-19
repo: /home/manuel/code/wesen/go-go-golems/go-go-host
source_ticket: HOST-013-LAMBDA-RT-CTRL
ticket_path: /home/manuel/code/wesen/go-go-golems/go-go-host/ttmp/2026/06/18/HOST-013-LAMBDA-RT-CTRL--lambda-runtime-control-plane-turning-hosting-platform-into-on-demand-function-runtime
implementation_commits:
  - 1b093e0 Phase L1: lambda runtime control plane schema + store wrappers
  - 2650d2a Phase L1: lambda control plane control stubs + Core wire-up
  - 582124f Phase L2 prep: move shared DTO types + wire interfaces to runtime package
  - b677414 Phase L2 part 1: runtime layer (lambda runtime + warm pool + supervisor + recorder) + config
  - de9501e Phase L2 part 2: wire-up (deploy manifest + control routing + main startup)
  - 9fcd9eb Phase L2 part 3: integration test + async-handler fix + lambda table reset
  - 4fa1bf0 Phase L3 part 1: host→site resolver for the EventDispatcher
baseline_commit: f6c9cce Merge pull request #4 from go-go-golems/task/bump-goja
design_doc: ttmp/2026/06/18/HOST-013-LAMBDA-RT-CTRL--.../design-doc/01-lambda-runtime-control-plane-design-and-implementation-guide-for-interns.md
related_vault_notes:
  - "[[PROJECT REPORT - go-go-host Beta Bringup - From Local MVP to Public Hosted Runtime]]"
  - "[[PROJECT REPORT - go-go-host OAuth Device Flow CLI - A Technical Deep Dive]]"
---

# go-go-host Lambda Runtime Control Plane — A Technical Deep Dive

This report explains how `go-go-host` gained a lambda runtime control plane: on-demand function invocations, warm pools of pre-initialized JavaScript runtimes, event source bindings, and per-call invocation records. The work adds a second execution model alongside the existing always-on express site model without modifying the working v1 code paths. The two models share the same Postgres control-plane store, the same deployment bundle pipeline, and the same Goja runtime factory, but they are served by distinct supervisors with distinct lifecycles.

The main result is that a site can now host an AWS-Lambda-style handler that accepts `(event, context)` and returns a value, invoked on demand from the API or from a public event source route, with the first invocation paying a cold-start cost and subsequent invocations reusing a warmed runtime within a configurable idle window. The existing express sites continue to serve HTTP traffic exactly as before.

> [!summary]
> HOST-013 adds a lambda execution model to `go-go-host` as an additive layer.
> 1. A separate `WarmPoolSupervisor` and `LambdaRuntime` serve function invocations; the existing `Supervisor` and `SiteRuntime` serve always-on express sites unchanged.
> 2. The deployment `Manifest` gains optional `handlers` and `eventSources` fields, so a function bundle reuses the entire validation, capability, and quota pipeline instead of defining a new archive type.
> 3. Invocation lifecycle is recorded in a new `invocation_records` table with typed columns, while a slim `runtime_events` row keeps the existing dashboard event stream working.
> 4. The public event source route is mounted before the host-router fallback so that `POST /hooks/{site_slug}/{function_name}` is not shadowed by the always-on site router.

## The problem this work solved

`go-go-host` before HOST-013 served one execution model. A site deployed a bundle containing JavaScript that called an express-style API to register HTTP routes. The daemon's `Supervisor` built one `SiteRuntime` per site, kept it resident for the life of the deployment, and routed public traffic to it by `Host` header. This model is well suited to sites that answer requests continuously: a storefront, a documentation site, a dashboard backend.

A second class of workload does not fit that model. An event handler that runs once per webhook delivery, once per queue message, or once per scheduled tick should not occupy a resident runtime between calls. It should start when the event arrives, run to completion, and release its resources. Charging for, and accounting for, that handler on the same per-request counters as an always-on site conflates two different runtime shapes. The platform also had no record of individual function calls: `runtime_events` logged site lifecycle, and `runtime_status` stored per-site counters, but neither captured the event payload, the result, the duration, or the cold-start attribution of a single invocation.

HOST-013 closes that gap. It introduces function definitions linked to deployments, warm pools of reusable JavaScript runtimes keyed by `(site, function, qualifier, deployment)`, event source bindings that map a public path to a function, and typed invocation records that make per-call data queryable. The design constraint throughout is that the v1 express path must not regress. A site that deploys an express bundle today must deploy and serve identically after HOST-013 lands.

## What shipped

At the time of this report, the lambda control plane is implemented through Phase L3 part 1. The persistence layer, the runtime layer, the warm pool, the invocation recorder, the deployment routing, the daemon startup wiring, and the host-resolution foundation for the public event route are all in place and tested against a live Postgres. The HTTP API surface for functions, invocations, warm pools, and event sources, plus the Glazed CLI verbs and the public `/hooks` route, remain open in Phase L3 part 2.

The shipped surface is:

- Five new tables in migration `009_lambda_runtime_control_plane.sql`: `functions`, `event_source_bindings`, `invocation_records`, `warm_pool_status`, `warm_pool_events`.
- Five sqlc query files and five store wrappers mirroring the existing `runtime_status` and `runtime_events` patterns.
- A runtime layer in `internal/runtime`: `LambdaRuntime`, `WarmPool`, `WarmPoolSupervisor`, `InvocationRecorder`, and the shared DTO and interface types in `warm_pool_wire.go`.
- Control-layer services in `internal/control`: `FunctionService`, `InvocationService`, `WarmPoolService`, `EventSourceService`, wired into `Core`.
- An extended deployment pipeline: the `Manifest` gains `handlers` and `eventSources`, the dry-run branches on function bundles, and `DeploymentService.activate` routes function manifests to the warm pool supervisor.
- A `WarmPoolDefaults` configuration block with pool size, idle TTL, thaw timeout, and pool key format.
- A host-to-site resolver in the store, the foundation for the public event dispatcher.

## Architecture at completion

The finished control plane adds a second supervisor alongside the existing one. The two supervisors share the store and the deployment pipeline but own disjoint runtimes.

```mermaid
flowchart TD
    subgraph Control["control.Core"]
        Sup["Supervisor (v1, unchanged)"]
        WPS["WarmPoolSupervisor (HOST-013)"]
        Deploy["DeploymentService"]
        Inv["InvocationService"]
        Events["EventSourceService"]
    end

    Store[("Postgres store")]
    Bundle["bundle pipeline"]
    Engine["engine.RuntimeFactory"]

    Deploy -->|express manifest| Sup
    Deploy -->|function manifest| WPS
    Sup --> Store
    WPS --> Store
    Inv --> WPS
    Events --> Store

    Sup -.builds.-> SiteRT["SiteRuntime (resident)"]
    WPS -.builds.-> WarmPool["WarmPool (slots)"]
    SiteRT --> Engine
    WarmPool --> Engine
```

The `Supervisor` path is unchanged. The `WarmPoolSupervisor` path is new. A single deployment can activate either path, and a site can hold both an express deployment and a function deployment simultaneously. That coexistence is intentional, and the implementation preserves it by keeping the two supervisors as separate objects rather than adding a mode flag to one.

## Why a separate warm pool supervisor

The first design decision was whether to extend the existing `Supervisor` with a mode field or to build a separate `WarmPoolSupervisor`. The existing supervisor is built around two assumptions that do not hold for functions. It keys runtimes by site, on the grounds that one site has one resident runtime. And its lifecycle verbs—activate, stop, restart, swap—are shaped by swapping one resident runtime for another.

A warm pool keys runtimes by a four-part tuple: site, function, qualifier, and deployment. A single site can hold several functions, each with its own pool, and a single function can hold several slots within one pool. The lifecycle is not swap; it is thaw, freeze, and evict, where a slot is borrowed for one invocation and returned to an idle pool or closed. Adding a mode flag to the existing supervisor would force every existing HTTP code path to learn about pools, slots, and function identifiers, and it would make the meaning of `Stop` ambiguous: does stopping a site also stop its pools?

A separate supervisor avoids that coupling. The HTTP path remains untouched. The lambda path evolves its own pool policy without changing the express swap semantics. Operators who want to stop a site explicitly stop both the resident runtime and the site's pools, or a future `SiteService.StopAll` does both. The cost is one additional field on `Core` and one branch in `DeploymentService.activate`. That cost is smaller than the cost of a god object that serves two runtime shapes.

## Why the bundle manifest extends rather than forks

The second design decision was whether to introduce a new archive type for function bundles or to extend the existing `Manifest`. A function bundle needs the same path policy enforcement, the same byte and file quotas, and the same capability intersection as an express bundle. A separate archive type would duplicate that logic and force the agent to produce two bundle formats.

The implementation extends `Manifest` with two optional fields:

```go
Handlers     map[string]string        `json:"handlers,omitempty"`
EventSources []EventSourceBindingSpec `json:"eventSources,omitempty"`
```

The validation rule is symmetric. A manifest with a non-empty `handlers` map and an empty `entrypoint` is a function bundle. A manifest with a non-empty `entrypoint` and an empty `handlers` map is a v1 express bundle. A manifest with both empty is rejected. This rule lets the existing `ValidateAndStore` pipeline run unchanged for express bundles and branch only where the function contract differs: the dry-run step and the activation step.

```mermaid
flowchart TD
    Upload["DeploymentService.Upload"] --> Validate["deploy.ValidateAndStore (unchanged)"]
    Validate --> Manifest{"manifest.Handlers non-empty?"}
    Manifest -->|yes| FnDryRun["function dry-run: build LambdaRuntime, load handlers, invoke sample event"]
    Manifest -->|no| ExDryRun["express dry-run: build SiteRuntime, health check"]
    FnDryRun --> Activate
    ExDryRun --> Activate
    Activate["DeploymentService.activate"] --> Route{"manifest.Handlers non-empty?"}
    Route -->|yes| PoolActivate["WarmPoolSupervisor.Activate (build pool)"]
    Route -->|no| SupActivate["Supervisor.Activate (resident runtime)"]
```

The function dry-run is the most important reuse of this design. Before a function bundle is accepted, the pipeline builds a real `LambdaRuntime`, loads the named handlers from the script, and invokes the first handler with a synthetic event. If the handler throws, or if the named export is not a function, the bundle is rejected before it is stored. An express bundle that passes today passes unchanged.

## The warm pool and the slot lifecycle

A warm pool is a bounded set of pre-initialized runtimes for one `(site, function, qualifier, deployment)` tuple. Each slot in the pool holds a `LambdaRuntime`, its cached handler callables, a last-used timestamp, and a busy flag. The pool exposes four operations that an invocation moves through.

```mermaid
flowchart LR
    Idle["idle (busy=false)"] -->|Thaw| Busy["busy (invoking)"]
    Busy -->|Freeze| Idle
    Idle -.expired.-> Evict["evict (close + drop)"]
    Busy -.error.-> Evict
    Cold["cold start"] --> Busy
```

`Thaw` is the core scheduling decision. It is called at the start of every invocation, and it must be fast in the common case. The implementation tries three strategies in order. First, it looks for an idle, non-expired slot—a warm reuse that returns immediately. Second, if no idle slot is within the idle TTL, it evicts one expired idle slot to make room, provided the pool is at capacity and `PoolEvictOnColdStart` is set. Third, it cold-starts a new slot by building a fresh `LambdaRuntime` and loading the handlers.

The cold-start path releases the pool mutex during the build. Building a `LambdaRuntime` and loading handlers is expensive—it constructs a Goja runtime, registers modules, and evaluates the script—and holding the pool lock across that work would serialize every cold start behind every other invocation. Releasing the lock, building outside the critical section, and re-acquiring the lock to append the new slot lets concurrent invocations thaw in parallel. The pseudocode for the released-lock section is the sharpest edge in the pool, and it is the first thing a reviewer should check under the race detector.

```go
// Release the lock for the expensive build, re-acquire to append the slot.
p.mu.Unlock()
lambdaRT, err := NewLambdaRuntime(ctx, spec)
if err != nil { /* mark pool failed, persist status */ return nil, err }
if err := lambdaRT.LoadFunctionHandlers(ctx, manifest.Handlers); err != nil { /* ... */ }
p.mu.Lock()
slot := &poolSlot{runtime: lambdaRT, handlers: lambdaRT.handlers,
    lastUsed: time.Now().UTC(), busy: true, coldStart: true}
p.slots = append(p.slots, slot)
```

`Freeze` returns a slot to the idle pool without closing it. `Evict` closes the runtime and drops the slot. `Invoke` is the composition: thaw a slot, run the handler, freeze on success, evict on error so a slot that produced an error is not handed to the next caller. The current implementation evicts on a returned error but does not yet defer the freeze on a panic; that gap is the top Phase L5 hardening item.

## How a function invocation runs

An invocation moves through three layers, each with a distinct responsibility.

```mermaid
sequenceDiagram
    participant Caller
    participant IS as control.InvocationService
    participant WPS as runtime.WarmPoolSupervisor
    participant Pool as runtime.WarmPool
    participant LR as runtime.LambdaRuntime
    participant Store as store

    Caller->>IS: Invoke(ctx, actor, site, fn, event, qualifier)
    IS->>Store: GetFunction(fn) -> handlers + active deployment
    IS->>WPS: PoolKeyFor(site, fn, qualifier)
    IS->>WPS: Invoke(ctx, poolKey, fn, handlerName, event, timeoutMS)
    WPS->>Pool: Thaw (warm reuse or cold start)
    Pool->>LR: Invoke(ctx, handlerName, event, contextMap)
    LR-->>Pool: result json.RawMessage
    Pool->>Pool: Freeze (success) or Evict (error)
    Pool->>Store: record invocation + slim runtime_event
    Pool-->>WPS: WarmPoolInvokeResult
    WPS-->>IS: result
    IS-->>Caller: InvocationResult
```

The control layer resolves authorization, looks up the function definition, picks the first handler name from the stored handlers slice, and computes the pool key. The supervisor thaws a slot and delegates to the pool. The pool runs the handler on the `LambdaRuntime` and records the outcome.

The pool key includes the deployment identifier. This is deliberate. When a function is re-deployed, the new deployment has a new identifier, and therefore a new pool key. The new pool is built without first draining the old pool's slots, so in-flight invocations on the old deployment complete against the old runtimes while new invocations go to the new pool. Versioning at the pool-key level means old and new deployments coexist cleanly during a rollout.

## Awaiting an async handler

The handler contract is `async (event, context) => result`, matching the AWS Lambda calling convention. In Goja, an async function returns a `Promise`, not the resolved value. A naive invocation that calls the handler and exports its return value receives the `Promise` object, not the result the handler computed. The integration test caught exactly this: the first implementation returned an empty map because `Value.Export()` on a `Promise` does not yield the resolved value.

The correct sequence relies on two properties of the runtime owner. First, `RuntimeOwner.Call` runs its callback on the event-loop goroutine and drains the event loop before returning, so a `Promise` returned from the callback is resolved by the time the call completes. Second, a Goja `Promise` exposes its `State` and its resolved `Result` as Go methods, and `Value.Export()` on a `Promise` returns the underlying `*goja.Promise` struct.

The implementation uses two `owner.Call` round trips. The first runs the handler and returns the `Promise` as a `goja.Value`. The event loop drains, and the `Promise` resolves. The second round trip, still on the same VM goroutine, detects the `Promise` via the type assertion `res.Export().(*goja.Promise)`, reads its state, and returns the resolved value's export.

```go
// First round trip: call the handler, return the Promise (or plain value).
handlerResult, err := l.runtime.Owner.Call(invokeCtx, "function-handler",
    func(callCtx context.Context, vm *goja.Runtime) (any, error) {
        res, callErr := handler(goja.Undefined(), vm.ToValue(event), vm.ToValue(contextMap))
        if callErr != nil { return nil, callErr }
        return res, nil // goja.Value (Promise or plain)
    })

// Second round trip: if it was a Promise, read the resolved value after the loop drained.
finalResult, err := l.runtime.Owner.Call(invokeCtx, "read-handler-result",
    func(callCtx context.Context, vm *goja.Runtime) (any, error) {
        res := handlerResult.(goja.Value)
        if promise, ok := res.Export().(*goja.Promise); ok {
            switch promise.State() {
            case goja.PromiseStateFulfilled:
                return promise.Result().Export(), nil
            case goja.PromiseStateRejected:
                return nil, fmt.Errorf("async handler rejected: %s", promise.Result())
            }
            return nil, fmt.Errorf("async handler promise not fulfilled (state %d)", promise.State())
        }
        return res.Export(), nil // sync handler: export the plain value
    })
```

This sequence is what makes the warm pool a viable lambda runtime rather than a synchronous script runner. A handler that awaits a database query or a timer resolves correctly, and the result that reaches the caller is the value the handler returned, not the `Promise` that wraps it.

## Loading CommonJS handlers

The handler script uses CommonJS-style exports: `exports.handler = async (event, context) => { ... }`. Loading that script is not a call to `vm.RunScript` on the raw text. The Goja require module provides `module`, `exports`, and `require` as locals inside a `require()` closure, not as VM globals, so a script that assigns to `exports` as a free variable fails with `ReferenceError: exports is not defined` if it is run raw.

The express bundles in the existing codebase do not hit this because their scripts call `require("express")` and register routes on the returned app object; they never assign to `exports` at the top level. Function bundles do assign to `exports`, so they need a CommonJS closure.

The implementation provides that closure directly. Before running the handler script, it creates a fresh `module` object and a fresh `exports` object on the VM globals, runs the script raw, then reads the named export path off the resulting `module.exports`. The dotted path `exports.handler` is walked as a field traversal, and the final value is asserted to a `goja.Callable` and cached on the slot for the life of the runtime.

```go
moduleObj := vm.NewObject()
exportsObj := vm.NewObject()
_ = moduleObj.Set("exports", exportsObj)
_ = vm.Set("module", moduleObj)
_ = vm.Set("exports", exportsObj)
if _, runErr := vm.RunScript(scriptPath, source); runErr != nil { return nil, runErr }
// walk the dotted path on module.exports; assert goja.AssertFunction; cache.
```

This avoids depending on the require module's module-root resolution, which would need the bundle's scripts directory registered as a module path. The manual closure is sufficient because function handlers use `exports` and nothing else from the CommonJS surface.

## Why invocation records are a separate table

The third design decision was whether to store invocation data in the existing `runtime_events` table or in a new `invocation_records` table. `runtime_events` is a free-form event log keyed by site and deployment, with a `metadata_json` blob. Reusing it for invocations would mean putting the event digest, the result, the duration, and the cold-start flag into JSON, and querying invocations would require filtering on an `event_type` prefix and parsing JSON for every row.

A separate table with typed columns makes the per-call data queryable directly. The `invocation_records` table has dedicated columns for `event_digest`, `duration_ms`, `cold_start`, and `status`, with composite indexes on `(function_id, started_at)` and `(site_id, started_at)`. A dashboard that lists recent invocations for a function, or that replays a specific call, reads an indexed, typed row instead of parsing a JSON blob.

The existing dashboard event stream is not abandoned. The invocation recorder writes two rows per call: the typed `invocation_records` row for query and replay, and a slim `runtime_events` row with `event_type = invocation.ok` or `invocation.error` so that any consumer of the existing event stream continues to see invocations. One table holds the canonical per-call data; the other keeps the existing consumers working without a schema fork.

## The public event source route

An event source binding maps a public path to a function. The intended contract is `POST /hooks/{site_slug}/{function_name}`, where the path is stable, owned by the site, and does not require the caller to know a binding identifier. The binding itself may optionally require a header secret, but the route shape is public.

The fourth design decision was where to mount that route. Mounting it under `/api` would put it behind the API auth middleware and would couple the public contract to the control API path structure. Mounting it inside the host-router fallback would let the always-on site router shadow it, because the fallback already claims every path that is not under `/api`, `/app`, `/admin`, or the health endpoints.

The correct placement is before the fallback. The lambda routes and the `/hooks` route are registered on the top-level mux before `withFallback(api, core.Supervisor)` is installed. The fallback still handles `GET /products` on a mixed-mode site whose express deployment answers that path, and a function-only site returns a 404 from the host router because no express runtime is registered for the host. The control CRUD for event source bindings stays under `/api/v1/sites/.../event-sources` for the dashboard.

Resolving a public request to an invocation requires turning the `Host` header into a site identifier. Phase L3 part 1 adds `Store.GetSiteByHost`, which checks `sites.primary_host` first and falls back to a verified `site_domains` row. That resolver is the foundation the dispatcher needs before it can call `FindEventSourceBindingByHostPath` and `WarmPoolSupervisor.Invoke`.

## The phased implementation

The work is structured as five phases, each with an explicit exit criterion and a commit boundary. The phases are ordered so that each one is independently testable and so that the riskiest integration points land where they can be isolated.

| Phase | Scope | Exit criterion | Status |
|---|---|---|---|
| L1 | Schema, store wrappers, control stubs | `go test ./internal/store ./internal/control` | Done |
| L2 | Runtime, warm pool, invocation, wire-up | function fixture deploys, activates, invokes, warm reuse | Done |
| L3 | HTTP API, event sources, CLI verbs | end-to-end deploy + invoke + public hook + fallback compat | In progress (part 1 done) |
| L4 | Dashboard, docs, example function | dashboard lists and invokes functions | Open |
| L5 | Hardening, quotas, observability parity | `go test ./... -race` | Open |

The phase boundaries are real test boundaries, not accounting devices. Phase L1 ships store round-trip tests and control stubs that return `ErrNotImplemented`. Phase L2 replaces those stubs with a working runtime and ships an integration test that deploys a real function fixture and observes warm reuse. Phase L3 mounts the HTTP surface and verifies backwards compatibility with the express fallback. Each phase can be reviewed and validated on its own evidence.

## What was tricky to build

The implementation has four sharp edges that a reviewer should examine closely.

The pool mutex release during cold start is the first. The lock is held for slot selection and released for the runtime build, then re-acquired to append the new slot. This pattern is necessary to avoid serializing cold starts, but it introduces a window in which the pool can be closed while a build is in flight. The implementation checks `p.closed` after re-acquiring the lock and cleans up the freshly built runtime if the pool was stopped during the build. The Phase L5 race test is the real validation of this invariant.

The async-Promise two-step is the second. The correctness of the second `owner.Call` depends on the first having drained the event loop. If a future change to `RuntimeOwner.Call` stops draining before returning, async handlers would silently return unfulfilled Promises. The integration test covers this by asserting that the echo handler's `{ echoed, ctx }` result arrives complete, but a regression in the owner's drain behavior would need a focused test to catch.

The import cycle break is the third. The concrete `*WarmPoolSupervisor` must satisfy the `WarmPoolSupervisorWire` interface that `control.Core` holds, but `control` imports `runtime` for the existing `*Supervisor` field. The resolution was to define the shared DTO types and the wire interfaces in the `runtime` package, not the `control` package, so the concrete type implements them in its own package. Phase L1 had defined those types in `control`; a dedicated Phase L2 prep commit moved them to `runtime` before the concrete supervisor landed. The lesson is general: when a concrete type in package A must satisfy an interface held in package B that imports A, the interface belongs in A.

The cross-test database leak is the fourth. The warm pool recorder writes pool rows to `warm_pool_status`, and the development Postgres volume persists across `go test` invocations. Phase 1 tests that asserted an empty pool summary found Phase 2's pool rows. The fix is a `ResetLambdaTables` helper that truncates the lambda tables at the start of each lambda test without touching the core v1 tables that the express tests rely on. Any future test that writes to the lambda tables must call it.

## Open questions and near-term next steps

Several decisions are deliberately deferred and recorded as open questions in the design doc.

Pool warmup at startup is currently disabled. Pools are marked ready on activation, but their slots are built on the first invocation, so the first call after a daemon restart is a cold start. A configuration flag and a background warmup goroutine would remove that cold start, at the cost of cold-start thundering when many functions restart together. The tradeoff is unresolved.

Replay idempotency is pinned to the current active deployment, not to the deployment that produced the original invocation. A replay after a re-deployment runs against the new code, not the code that ran originally. Pinning replay to the original deployment would give exact reproducibility but would require keeping old runtimes resident for replay, which is expensive. The current behavior is documented; the stricter behavior is a Phase L5 decision.

Event source authentication is optional in development and intended to be required in production. The binding schema carries a `secretHeader` field, but the dispatcher does not yet verify it. Phase L3 part 2 will wire the verification, and Phase L5 will enforce it.

The immediate next steps are Phase L3 part 2 through Phase L5. Phase L3 part 2 implements the `EventDispatcher`, the lambda HTTP handlers, the route registration before the fallback, and the Glazed CLI verbs. Phase L4 adds the dashboard pages, the RTK Query endpoints, the Storybook stories, and an example function bundle. Phase L5 closes the panic-defer gap in `WarmPool.Invoke`, reuses the `dbguard` for concurrent pool slots, adds invocation-level timeout and metrics parity, and runs the full suite under the race detector.

## Key file locations

- Migration and queries: `internal/store/migrations/009_lambda_runtime_control_plane.sql`, `internal/store/queries/{functions,invocation_records,warm_pool_status,warm_pool_events,event_source_bindings}.sql`.
- Store wrappers: `internal/store/{functions,invocation_records,warm_pool_status,warm_pool_events,event_source_bindings,sites,lambda_reset}.go`.
- Runtime layer: `internal/runtime/{warm_pool_wire,invocation_recorder,lambda_runtime,warm_pool,warm_pool_supervisor}.go`.
- Control services: `internal/control/{functions,invocations,warm_pools,event_sources,core,deployments}.go`.
- Deployment pipeline: `internal/deploy/bundle.go`.
- Configuration: `internal/config/config.go`.
- Daemon startup: `cmd/go-go-hostd/main.go`.
- Design doc and diary: `ttmp/2026/06/18/HOST-013-LAMBDA-RT-CTRL--.../design-doc/01-...md` and `reference/01-...diary.md`.

## How to validate

With the development Postgres running, the lambda control plane is exercised by:

```bash
docker compose -f deployments/dev/docker-compose.yaml up -d postgres
export GO_GO_HOST_TEST_DATABASE_URL='postgres://go_go_host:go_go_host_dev@127.0.0.1:55432/go_go_host?sslmode=disable'
psql "$GO_GO_HOST_TEST_DATABASE_URL" -c "Drop SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"
go test ./internal/store ./internal/runtime ./internal/control ./internal/deploy -count=1
```

The Phase L2 integration test `TestPhase2FunctionDeployActivateInvoke` deploys a function fixture that exports an async echo handler, activates it, invokes it twice, and asserts that the first call is a cold start and the second reuses the warmed slot. The full module should build and vet clean:

```bash
go build ./...
go vet ./...
```

## Working rule

The lambda control plane is an additive layer over a working hosting platform. Every change is judged by whether the v1 express path still behaves identically. When two design options conflict, the one that keeps the express path untouched wins, even when the alternative is more uniform. A god object that serves two runtime shapes is a larger liability than two supervisors that share a store.
