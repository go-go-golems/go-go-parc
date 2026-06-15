---
title: "Go Go Objects: Async Durable Objects Dispatch and xgoja v2 Integration"
aliases:
  - Go Go Objects Async Dispatch
  - Async Durable Objects on Goja
  - GOJA-DO-002 Report
  - Go Go Objects xgoja v2 Follow-up
tags:
  - article
  - go
  - goja
  - xgoja
  - durable-objects
  - promises
  - actor-runtime
  - sqlite
  - glazed
  - release-engineering
status: active
type: article
created: 2026-06-14
repo: /home/manuel/workspaces/2026-06-12/goja-durable-objects/go-go-objects
related:
  - "[[ARTICLE - Go Go Objects - Durable Objects Runtime on Goja]]"
---

# Go Go Objects: Async Durable Objects Dispatch and xgoja v2 Integration

This report documents the work completed after [[ARTICLE - Go Go Objects - Durable Objects Runtime on Goja]]. The earlier article described the first complete Durable Objects runtime: object identity, actor startup, SQLite storage, alarms, HTTP routing, and xgoja/v2 generated-binary integration. Today's work moved the runtime from a synchronous actor kernel to a Promise-aware actor system with a documented JavaScript API, a released xgoja dependency, proper Glazed help, validated release packaging, and review-driven concurrency fixes.

The central technical change is that a Durable Object handler may now be `async`. RPC methods, `fetch(req)`, and `alarm()` may return a `goja.Promise`; the runtime waits for that Promise to settle before converting the result. This is not a cosmetic API change. It changes the actor event lifecycle. A dispatch no longer ends when the JavaScript method returns a value from the first owner-thread callback. It ends when the returned value has been classified, awaited if necessary, converted, and reported back to the caller.

> [!summary]
> - GOJA-DO-002 added Promise-aware dispatch for RPC, fetch, and alarm handlers while keeping same-object dispatches serialized until Promise settlement.
> - The implementation had to distinguish goja runtime ownership from Durable Object actor serialization. `RuntimeOwner.Call()` serializes VM callbacks; the actor still needs its own dispatch gate for async event lifecycles.
> - The xgoja integration was updated to the finalized v2 `RuntimePlan` API and pinned to released `go-go-goja v0.9.5`.
> - The standalone CLI now uses Glazed/Cobra, embedded help pages, `help export`, and a working GoReleaser snapshot configuration.

## Why this follow-up was necessary

The first runtime could run object methods, persist state, wake alarms, and serve HTTP. That was enough to prove the Durable Objects model on top of goja. It was not enough to support normal Durable Objects programming style. JavaScript Durable Object handlers are often written as `async` functions even when the storage layer is simple. The method body may wait on timers, host APIs, network calls, or other Promise-returning code before producing its result.

Before this work, a handler that returned a Promise was treated as if the Promise object itself were the final result. That produced incorrect RPC responses, incorrect fetch responses, and alarm handlers that could return before their effect had happened. It also hid rejected Promises from the Go caller. A rejected async handler should be an error in the dispatch result, not a successful response containing an unresolved JavaScript object.

The new work therefore had two responsibilities:

1. **Implement Promise-aware completion.** The actor must detect returned Promises, wait for fulfillment or rejection on the runtime owner, and only then convert the result.
2. **Preserve actor semantics while waiting.** The actor must not allow a second request to mutate the same JavaScript instance while the first dispatch is suspended on a Promise.

These requirements are related but not identical. Promise awaiting answers when one dispatch is complete. Actor serialization answers whether another dispatch may start before that completion point.

## The dispatch lifecycle before and after

The original actor dispatch path had one owner-thread call. It invoked the JavaScript method and immediately converted the returned value. That worked for synchronous methods because the returned value was the final value.

```text
Dispatch
  -> RuntimeOwner.Call(invoke method)
  -> convert returned goja.Value
  -> return Result
```

The new dispatch path separates invocation, awaiting, and conversion. This makes the event lifecycle explicit.

```text
Dispatch
  -> acquire actor dispatch gate
  -> start dispatch timeout / VM interrupt timer
  -> RuntimeOwner.Call(invoke method)
  -> RuntimeOwner.Call(detect whether returned value is Promise)
  -> if Promise:
       loop:
         RuntimeOwner.Call(read Promise state and result)
         wait briefly outside owner if pending
  -> RuntimeOwner.Call(convert fulfilled value or rejection)
  -> release actor dispatch gate
```

The important property is not the polling loop by itself. The important property is that every operation that touches `goja.Value` or `goja.Promise` happens on the runtime owner. The dispatch goroutine may hold opaque references to goja values, but it must not inspect or export them directly.

The current implementation lives in `pkg/durableobjects/actor.go`. The high-level flow is visible in `Actor.Dispatch`:

```go
func (a *Actor) Dispatch(ctx context.Context, env Envelope) (Result, error) {
    a.active.Add(1)
    a.touch()
    defer func() {
        a.touch()
        a.active.Add(-1)
    }()

    release, err := a.acquireDispatch(ctx)
    if err != nil {
        return Result{}, err
    }
    defer release()

    return a.withInterrupt(ctx, func(ctx context.Context) (Result, error) {
        raw, err := a.invokeDispatch(ctx, env)
        if err != nil {
            return Result{}, err
        }
        settled, err := a.awaitDispatchValue(ctx, raw)
        if err != nil {
            return Result{}, err
        }
        return a.convertDispatchValue(ctx, settled)
    })
}
```

This code is compact, but it encodes three design decisions.

First, `active` still tracks running work for idle eviction. An actor awaiting a Promise remains active; it must not be closed while its event is incomplete.

Second, `acquireDispatch` happens before `withInterrupt`. A request waiting behind an already-active dispatch does not consume its JavaScript CPU/Promise settlement budget while it is queued. The timeout applies to the event after the actor accepts it.

Third, conversion happens after awaiting. RPC, fetch, and alarm dispatch all share the same Promise settlement behavior, but they keep their own result conversion rules.

## Runtime ownership is not actor serialization

The most important review finding exposed a boundary that is easy to miss. `go-go-goja` already provides `RuntimeOwner.Call()`. It schedules callbacks onto the runtime owner loop and makes goja VM access single-threaded. That does not automatically serialize a whole Durable Object dispatch when the dispatch spans multiple owner calls.

A pending Promise creates exactly that situation. The first owner callback invokes the JavaScript method and returns a `goja.Promise`. At that point `RuntimeOwner.Call()` has completed. If the Durable Objects layer does nothing else, another HTTP request can enter another `RuntimeOwner.Call()` and invoke another method on the same object while the first Promise remains pending.

That would break the current Durable Objects semantics in two ways.

- A second dispatch could observe or mutate object state before the first async dispatch has finished.
- The first dispatch's timeout interrupt could fire while the second dispatch is executing on the same VM.

The fix is an actor-level dispatch gate:

```go
type Actor struct {
    // ...
    dispatchGate chan struct{}
}

func (a *Actor) acquireDispatch(ctx context.Context) (func(), error) {
    if ctx == nil {
        ctx = context.Background()
    }
    select {
    case a.dispatchGate <- struct{}{}:
        return func() { <-a.dispatchGate }, nil
    case <-ctx.Done():
        return nil, timeoutOrContextError(ctx)
    }
}
```

A channel is used instead of a plain mutex because waiting for a busy actor should be cancellable. If the caller's context expires while another dispatch is running, the caller should return rather than block indefinitely. The gate is initialized when the manager starts an actor.

This design keeps the first async milestone conservative. It does not attempt Cloudflare-style input gates or event interleaving. It makes a narrower guarantee: for one object identity, the runtime processes one dispatch lifecycle at a time.

## Promise detection and owner-thread safety

The first async implementation detected Promises with:

```go
promise, ok := value.Export().(*goja.Promise)
```

That line was wrong when run outside the runtime owner. `goja.Value.Export()` may inspect VM-managed state. Even if the returned Go object is only used as a pointer later, the detection itself touches the runtime. The corrected implementation moves detection into an owner callback:

```go
ret, err := a.runtime.Owner.Call(ctx, "durable-object.promise-detect",
    func(_ context.Context, vm *goja.Runtime) (any, error) {
        promise, ok := value.Export().(*goja.Promise)
        if !ok {
            return awaitValueState{value: value}, nil
        }
        return awaitValueState{promise: promise}, nil
    })
```

After detection, the dispatch goroutine may keep the `*goja.Promise` reference, but it only reads `State()` and `Result()` through later owner callbacks:

```go
ret, err := a.runtime.Owner.Call(ctx, "durable-object.promise-state",
    func(_ context.Context, vm *goja.Runtime) (any, error) {
        return promiseSnapshot{
            state:  promise.State(),
            result: promise.Result(),
        }, nil
    })
```

This is the pattern to remember. Non-owner code may coordinate the wait loop, contexts, and timers. Owner callbacks do the VM work.

## Rejection handling and durable error codes

A synchronous storage error already preserves its durable error code. For example, `state.storage.put("", 1)` produces `CodeBadRequest` because an empty storage key is invalid. The first async implementation lost that precision when the same error happened after an `await`.

The reason is that a Go-backed error crossing into JavaScript becomes a goja `GoError` object. When an async function rejects with that object, the Promise rejection value is not the Go error itself. It is a JavaScript object with a `message` and an internal `value` property containing the original Go `error`.

The final implementation extracts this value on the owner thread:

```go
func durableErrorFromValue(vm *goja.Runtime, value goja.Value) *Error {
    if value == nil || goja.IsUndefined(value) || goja.IsNull(value) {
        return nil
    }
    if durableErr := durableErrorFromExport(value.Export()); durableErr != nil {
        return durableErr
    }
    obj := value.ToObject(vm)
    if obj == nil {
        return nil
    }
    for _, key := range []string{"value", "cause", "error"} {
        child := obj.Get(key)
        if child == nil || goja.IsUndefined(child) || goja.IsNull(child) {
            continue
        }
        if durableErr := durableErrorFromExport(child.Export()); durableErr != nil {
            return durableErr
        }
    }
    return nil
}
```

This gives async and sync handlers the same API-level error behavior. A JavaScript author can move a failing storage operation after an `await` without accidentally changing a bad request into a generic execution error.

The regression test is direct:

```javascript
async badStorageAfterAwait() {
  await Promise.resolve();
  this.state.storage.put("", 1);
}
```

The expected result is `CodeBadRequest`, not `CodeExecutionError`.

## The JavaScript API after this work

The supported JavaScript surface is now clear enough to document as a local API. A bundle is still a CommonJS file that exports classes through `exports.objects`:

```javascript
class Counter {
  constructor(state, env) {
    this.state = state;
    this.env = env;
  }

  async increment(by = 1) {
    const current = this.state.storage.get("count") || 0;
    const next = current + by;
    this.state.storage.put("count", next);
    return next;
  }
}

exports.objects = { Counter };
```

The namespace derives from the export name unless a manifest overrides it. `Counter` becomes `COUNTER`; `ChatRoom` becomes `CHAT_ROOM`.

RPC dispatch calls object methods through:

```text
/rpc/:namespace/:objectName/:method
```

Fetch dispatch calls `fetch(req)` through:

```text
/fetch/:namespace/:objectName/*path
```

Alarm dispatch calls `alarm()` when the scheduler finds a due alarm. All three dispatch kinds now share Promise settlement semantics.

The storage API remains synchronous:

| Method | Behavior |
| --- | --- |
| `get(key)` | Return the stored value or `undefined`. |
| `put(key, value)` | Store a JSON-serializable value. |
| `delete(key)` | Delete one key. |
| `list({ prefix })` | Return keys and values, optionally filtered by literal prefix. |
| `transaction(fn)` | Run a synchronous callback in a SQLite transaction. |
| `setAlarm(timestampMs)` | Schedule this object's alarm. |
| `getAlarm()` | Return the scheduled alarm timestamp or `undefined`. |
| `deleteAlarm()` | Clear the scheduled alarm. |

`transaction(fn)` is intentionally synchronous-only. Holding a SQLite transaction open across an `await` would make ordering, cancellation, and lock ownership difficult to reason about. The runtime rejects async transaction callbacks rather than trying to approximate Cloudflare's async storage behavior.

## xgoja v2 cutover and provider compatibility

The earlier xgoja integration used the v2 buildspec shape, but the surrounding xgoja code was still changing. Today's work aligned `go-go-objects` with the finalized `app.RuntimePlan` API and then pinned the dependency to the released `github.com/go-go-golems/go-go-goja v0.9.5`.

The important migration was replacing removed runtime-spec types:

| Removed shape | Current shape |
| --- | --- |
| `app.RuntimeSpec` | `app.RuntimePlan` |
| `app.ModuleInstanceSpec` | `app.RuntimeModulePlan` inside `RuntimeSection` |
| `app.AssetSourceSpec` | `app.SourcePlan{Kind: app.SourceKindAssets}` |

The Durable Objects provider tests now construct runtime plans that match generated xgoja/v2 metadata. The custom template in `examples/templates/durableobjects_http_runtime.go.tmpl` also decodes `*app.RuntimePlan`.

The released dependency matters. The project no longer relies on a local checkout or an unreleased commit hash. `GOWORK=off go test ./...` passes with `go-go-goja v0.9.5`, which means CI and downstream users can reproduce the build without a workspace-specific `replace`.

## Host services and template-generated hosts

The xgoja provider work also clarified why provider command sets need access to host services. A provider-owned command such as `durableobjects serve` is not a runtime module, but it still needs generated-host resources. It may need embedded assets, a manifest asset, a shared HTTP host, or an application-provided service.

The xgoja side now documents `CommandSetContext.Host`, and `go-go-objects` uses the pattern for Durable Objects command provider setup. This is especially relevant for template-generated hosts. A custom template may emit Go code that owns the outer `http.Server`, registers providers, decodes `app.RuntimePlan`, and attaches provider commands. Those commands should see the same host service bag as modules.

The rule is simple: template code should construct the host through `app.NewHost` or `app.NewHostWithOptions`, not bypass xgoja command-set attachment and reimplement asset/service plumbing.

## Release configuration and Glazed help

The runtime is now closer to a normal Go Go Golems CLI package. Two infrastructure pieces were finished today.

First, the GoReleaser configuration was still using generated scaffold names. It tried to build `./cmd/XXX` into a binary named `XXX`. The active release configuration now uses:

```yaml
project_name: go-go-objects

builds:
  - id: go-go-objects-linux
    main: ./cmd/go-go-objects
    binary: go-go-objects
```

The snapshot release command now succeeds:

```bash
GORELEASER_TARGET=--single-target make goreleaser
```

It produces the Linux binary, archive, deb, and rpm artifacts under `dist/linux_amd64`.

Second, the standalone CLI moved from plain `flag` parsing to a Glazed/Cobra root command. The default invocation shape remains the same:

```bash
go-go-objects --addr 127.0.0.1:8787 --storage ./var/durable-objects
```

The difference is that the binary now has standard Glazed help, logging flags, and help export:

```bash
go-go-objects help
go-go-objects help go-go-objects-js-api
go-go-objects help export --format sqlite --output-path help.sqlite
```

The embedded help pages are now part of the repository:

| Help slug | Purpose |
| --- | --- |
| `go-go-objects-overview` | Application-level overview and local server usage. |
| `go-go-objects-js-api` | JavaScript object API, storage, alarms, and async semantics. |
| `go-go-objects-xgoja-provider` | xgoja/v2 provider configuration, embedded assets, HTTP composition, and direct serve command. |

This matters because the project now exposes multiple surfaces. A README is useful, but it is not enough for a CLI that has a standalone server, JavaScript API, xgoja provider, embedded assets, direct command provider, template integration, and release packaging.

## Validation performed

The final local validation covered unit tests, linting, security scanning, vulnerability scanning, help export, and snapshot release packaging.

```bash
GOWORK=off go test ./... -count=1
GOWORK=off golangci-lint run --timeout=5m
GOWORK=off gosec -exclude=G101,G304,G301,G306,G204 -exclude-dir=.history ./...
GOWORK=off govulncheck ./...
go-go-objects help export --format sqlite --output-path /tmp/go-go-objects-help/help.sqlite
GORELEASER_TARGET=--single-target make goreleaser
```

Generated xgoja binary smoke tests were also run during the work. Both the composed HTTP serve path and the direct Durable Objects serve path succeeded. The composed path mounts the Durable Objects gateway through xgoja HTTP/Express. The direct path uses the provider-owned `durableobjects serve` command.

## Current implementation state

The current branch includes the following important commits after the original project article:

| Commit | Purpose |
| --- | --- |
| `d8dd209` | Implement Promise-aware Durable Objects dispatch. |
| `fa8d13f` | Document async dispatch behavior and update examples. |
| `d48274d` | Validate async behavior and normalize timeout handling. |
| `3b8dafa` | Finalize GOJA-DO-002 documentation. |
| `01da119` | Adapt Durable Objects integration to xgoja `RuntimePlan`. |
| `a1bec39` | Bump `go-go-goja` dependency to `v0.9.5`. |
| `43df9d8` | Serialize async dispatches per actor. |
| `3260b58` | Fix GoReleaser configuration. |
| `32df7ee` | Add Glazed help for the Durable Objects API. |
| `b765c4c` | Address PR review feedback for owner-safe Promise detection and coded async errors. |

The repository state is now substantially different from the first article. The original system proved that a Durable Objects runtime could be built on goja and xgoja. The current system defines the first useful async contract for JavaScript authors and tightens the project into a documented, releaseable CLI/provider package.

## Open technical questions

The next questions are no longer about whether async handlers can work. They are about how far the runtime should move toward Cloudflare compatibility.

### Should the timeout option be renamed?

`CPUTimeout` now covers more than synchronous JavaScript CPU time. It also bounds Promise settlement. The current flag remains `--cpu-timeout` for compatibility, but the conceptual name is closer to `dispatch-timeout`.

### Should Promise waiting move into go-go-goja?

`go-go-goja` already has Promise waiting logic in REPL/session code. `go-go-objects` now has a carefully reviewed owner-safe version. If another package needs this behavior, a public helper could reduce duplicated promise polling logic.

### Should input gates and output gates be implemented?

The current runtime deliberately does not interleave same-object events during awaits. Cloudflare Durable Objects have a more elaborate concurrency model with input gates and output gates. Implementing that would require a new design phase. It cannot be added by simply releasing the dispatch gate during every await.

### Should storage become async?

The current storage API is synchronous and SQLite-backed. That choice keeps transactions simple and actor behavior predictable. An async storage API would need explicit rules for transaction lifetime, cancellation, and output gating.

## Working rules after today

The work produced several rules that should guide future changes.

- Every operation that inspects or exports a `goja.Value` must run on the runtime owner.
- `RuntimeOwner.Call()` serializes VM access callbacks, not whole Durable Object events.
- A Promise-returning handler keeps the object dispatch active until the Promise settles or times out.
- Same-object dispatch interleaving is a future feature, not an accidental side effect of async support.
- Go-backed durable errors must preserve their `ErrorCode` across synchronous throws and asynchronous Promise rejections.
- Template-generated xgoja hosts should use host services rather than duplicating embedded asset resolution.
- CLI features should be discoverable through Glazed help pages, not only through README text.

## Near-term next steps

The immediate next step is to push the branch and let PR #2 run CI and review again. The local validation is clean, but the PR should confirm the same result in GitHub Actions.

After that, the next technical milestone should be chosen deliberately. The strongest candidates are:

1. Rename or alias the timeout option to reflect full dispatch settlement semantics.
2. Factor an owner-safe Promise-await helper into go-go-goja if another package needs it.
3. Add more end-to-end examples that show async RPC, fetch, alarms, and xgoja HTTP composition together.
4. Write a separate design ticket for Cloudflare-style input/output gates if compatibility requires interleaving during awaits.

The project is now in a good state for review because the implementation, tests, local help, release configuration, and design diary all describe the same runtime contract.
