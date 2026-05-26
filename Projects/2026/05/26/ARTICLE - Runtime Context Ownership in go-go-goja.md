---
title: "Runtime Context Ownership in go-go-goja"
aliases:
  - "go-go-goja runtime context ownership"
  - "RuntimeServices refactor"
  - "RuntimeOwner refactor"
tags:
  - article
  - goja
  - xgoja
  - runtime
  - context
  - go
status: active
type: article
created: 2026-05-26
repo: /home/manuel/workspaces/2026-05-24/add-js-providers/go-go-goja
source_ticket: XGOJA-014
---

# Runtime context ownership in go-go-goja: a deep dive into the refactor

## 1. The problem that made the refactor necessary

`go-go-goja` began as a small framework for composing Go-backed JavaScript modules on top of `goja`. The early design was sufficient for simple runtimes: create a `goja.Runtime`, attach a Node-style `require`, register modules, run code, and close the runtime when the command finishes. That model becomes more difficult when xgoja enters the picture. A generated xgoja binary can now combine providers that open HTTP servers, receive Discord events, listen to hardware, run timers, perform file-system work, and expose package-owned Glazed commands. A single runtime may be entered by a command invocation, an HTTP request, a hardware event, a background goroutine, or a cleanup hook.

The core technical constraint never changed: a `*goja.Runtime` must be accessed in a serialized way. JavaScript values, callback invocation, Promise resolution, and VM state all belong to the runtime owner. The change was in the number of entry sources and cancellation domains around that owner. A CLI command has one cancellation scope. An HTTP request has another. A hardware listener belongs to the runtime lifetime. A Promise created during an HTTP request should stop if the request is canceled, but it must also stop if the runtime closes. Cleanup receives a separate close context that answers how long shutdown may take.

The old API names did not express these distinctions. `runtimebridge.Bindings` exposed a generic `Context` field. `runtimebridge.CurrentContext(vm)` sounded like a universal answer. `runtimeowner.Runner` did not say what was being run or owned. `Factory.NewRuntime(ctx)` accepted one context without making clear whether it controlled startup, lifetime, or both. The code could compile while carrying the wrong context across a boundary. The result was not only confusing documentation; it produced real runtime behavior problems.

The Loupedeck web/hardware UI work exposed the issue clearly. A generated xgoja command created a retained hardware UI page from JavaScript. The script reached the first tile binding and hung. The log stopped after `configuring tile 0,0`, and the command eventually failed with:

```text
Error: runtimeowner jsverbs.invoke: runtime call canceled: context canceled
```

The deck was not the cause. The hang reproduced with hardware disabled. The failure came from a nested runtime-owner call: a JS-facing native function configured a retained UI callback, that callback evaluated JavaScript while already inside an owner call, and the module used the wrong context. The owner could not recognize the call as reentrant, so it scheduled work behind itself and waited. This was the concrete failure that forced the API cleanup.

## 2. The design principle: name each context by what it controls

The refactor is built around one principle: context names must describe the lifetime they control. A single generic `Context` field is not enough because runtime construction, runtime lifetime, current owner entry, external requests, subscriptions, and cleanup have different cancellation semantics.

The refactor gives those concepts explicit API positions:

| Concept | Meaning | API after the refactor |
| --- | --- | --- |
| Startup context | Controls runtime construction, module registration, and runtime initializers. | `engine.WithStartupContext(ctx)` |
| Runtime lifetime context | Controls runtime-owned resources after construction. | `engine.WithLifetimeContext(ctx)`, `Runtime.Context()`, `RuntimeServices.Lifetime()` |
| Current owner-entry context | The context active for the JavaScript/native callback currently running on the runtime owner. | `runtimebridge.CurrentOwnerContext(vm)` |
| Custom operation context | A caller-provided request, event, command, or subscription context. | `CallWithCustomContext`, `PostWithCustomContext` |
| Cleanup context | The context passed to `Runtime.Close(ctx)` and runtime closers. | `Runtime.Close(ctx)`, registered closers |

These names are longer than the old names. That is deliberate. A native module call site should reveal intent during code review. `services.PostWithLifetimeContext("device.button", fn)` communicates a different ownership decision from `services.PostWithCustomContext(req.Context(), "http.route", fn)`. The reviewer can ask whether the event truly belongs to the runtime lifetime or to a request/event context.

## 3. Runtime creation before and after

Before the refactor, embedders called:

```go
rt, err := factory.NewRuntime(ctx)
```

That single context was overloaded. It was easy to assume that it meant “the runtime lifetime,” but code also used it during construction and initialization. The refactor changes the lower-level engine API to accept explicit runtime options:

```go
rt, err := factory.NewRuntime(
    engine.WithStartupContext(ctx),
    engine.WithLifetimeContext(ctx),
)
```

When startup and lifetime differ, the call site can say so:

```go
rt, err := factory.NewRuntime(
    engine.WithStartupContext(startupCtx),
    engine.WithLifetimeContext(lifetimeCtx),
)
```

The implementation lives in `engine/factory.go`. `Factory.NewRuntime` now collects `RuntimeOption` values, defaults missing contexts to `context.Background`, checks whether the startup context is already canceled, creates the VM and event loop, creates a `RuntimeOwner`, derives the runtime context from the lifetime context, and stores runtime services for the VM (`engine/factory.go:181-232`). Module registration receives the startup context through `RuntimeModuleContext.Context` (`engine/factory.go:234-242`), and runtime initializers receive the startup context through `RuntimeContext.Context` (`engine/factory.go:270-283`). Runtime-owned goroutines and resources get the derived lifetime context through `Runtime.Context()` and `runtimebridge.RuntimeServices`.

The xgoja-level runtime factory did not get the same signature. That is important. `providerapi.RuntimeFactory.NewRuntime(ctx, profile, ...)` still takes a command/request context and a named xgoja runtime profile. It is responsible for translating the xgoja-level request into a lower-level engine runtime with startup and lifetime options. This keeps provider authors focused on runtime profiles while keeping engine embedders explicit about construction and lifetime.

## 4. RuntimeOwner: the serialized VM boundary

The old public name `runtimeowner.Runner` was too generic. The interface does not run arbitrary work. It owns serialized access to a `goja.Runtime`. The refactor renames the public type to `runtimeowner.RuntimeOwner` and the constructor to `runtimeowner.NewRuntimeOwner`.

The current interface is:

```go
type RuntimeOwner interface {
    Call(ctx context.Context, op string, fn CallFunc) (any, error)
    Post(ctx context.Context, op string, fn PostFunc) error
    WaitIdle(ctx context.Context) error
    Shutdown(ctx context.Context) error
    IsClosed() bool
}
```

`Call` is the request/response form. It schedules a function onto the owner, waits for the result, and returns the result or error. `Post` is the fire-and-forget form. It schedules a function onto the owner but does not return a value from that function. Both methods preserve operation names so errors can say which owner operation failed.

The implementation in `pkg/runtimeowner/runner.go` still uses a file name that predates the rename, but the internal type is now `runtimeOwner`. The implementation tracks whether the runtime is closed, accepts a scheduler, detects reentrant owner calls, pushes the active call context into `runtimebridge`, recovers panics when configured, and tracks active calls for shutdown. Active-call tracking happens in `beginActive` and `endActive`; both `invoke` and `invokePost` wrap owner callbacks with that accounting (`runtimeowner/runner.go:222-258`).

The `WaitIdle` addition is part of the shutdown story. `RuntimeOwner.WaitIdle(ctx)` waits until the active owner-call count drops to zero (`runtimeowner/runner.go:93-113`). This gives `Runtime.Close` a bounded way to let in-flight owner work finish before resorting to interruption.

## 5. RuntimeServices: the module-facing bridge

Native modules should not import the full runtime owner implementation details. They need a small set of runtime services: the owner scheduling subset, the event loop when necessary, and the runtime lifetime context. That is the role of `runtimebridge.RuntimeServices`.

The new type is defined in `pkg/runtimebridge/runtimebridge.go`:

```go
type RuntimeServices struct {
    LifetimeContext context.Context
    Loop            *eventloop.EventLoop
    Owner           RuntimeOwner
}
```

The old type was `runtimebridge.Bindings`. It had a `Context` field. That field was the core ambiguity. Some code treated it as the runtime lifetime context. Some code treated it as the right context for callbacks into JavaScript. Some code captured it at module load time and reused it later. The refactor removes the compatibility field instead of aliasing it. The missing field produces compile errors in downstream packages, which is the desired behavior for a breaking API cleanup.

`RuntimeServices` provides intent-specific helpers:

```go
services.CallWithCurrentContext(vm, op, fn)
services.PostWithCurrentContext(vm, op, fn)
services.CallWithLifetimeContext(op, fn)
services.PostWithLifetimeContext(op, fn)
services.CallWithCustomContext(ctx, op, fn)
services.PostWithCustomContext(ctx, op, fn)
```

These helpers are not just convenience wrappers. They encode policy. `CallWithCurrentContext` uses `runtimebridge.CurrentOwnerContext(vm)`, which reads the context stack for the currently executing owner call. `CallWithLifetimeContext` uses `services.Lifetime()`. `CallWithCustomContext` uses an explicit caller context and links it to runtime lifetime cancellation.

The linking behavior was refined after code review. The first implementation spawned a goroutine for each linked context and did not explicitly cancel linked contexts after the operation finished. Codex review on PR 41 flagged that as a potential goroutine/memory leak for high-frequency async paths. The fix replaced per-call goroutines with `context.AfterFunc(lifetime, cancel)`, cancels linked call contexts after `CallWithCustomContext` returns, and unregisters the lifetime callback after a posted callback runs (`runtimebridge/runtimebridge.go:70-135`). This preserves async Promise behavior: `PostWithCustomContext` must not cancel the linked context immediately after enqueueing, because cancellation before the posted callback runs would cause the owner to skip the callback.

The final behavior is:

```text
CallWithCustomContext(ctx)
  ├─ link ctx to runtime lifetime
  ├─ call owner
  └─ cancel linked context when owner call returns

PostWithCustomContext(ctx)
  ├─ link ctx to runtime lifetime
  ├─ enqueue callback on owner
  ├─ if enqueue fails: cancel linked context immediately
  └─ when callback runs: unregister lifetime hook after callback returns
```

This design avoids per-operation goroutines, prevents premature cancellation of Promise settlement callbacks, and still lets runtime shutdown cancel pending operations.

## 6. CurrentOwnerContext: why the current owner entry matters

`runtimebridge.CurrentOwnerContext(vm)` is the replacement for `runtimebridge.CurrentContext(vm)`. The new name is intentionally specific. It returns the context active for the current owner call on that VM. If no owner call context is active, it falls back to the runtime lifetime context (`runtimebridge/runtimebridge.go:187-200`).

The owner pushes and pops contexts with `runtimebridge.WithCallContext` (`runtimebridge/runtimebridge.go:203-219`). The stack matters because owner calls can be nested. A nested call should see its own context while it runs, and the outer context should be restored afterward. The tests verify this behavior, including restoration after panic.

This context is the correct default inside JavaScript-facing native functions. If JavaScript calls a Go function and that Go function needs to evaluate a JS callback synchronously, it should use `CallWithCurrentContext`. The Loupedeck UI issue was precisely this case. Retained tile/display bindings were created inside JavaScript execution. The binding functions evaluated JS callbacks while the owner was already active. Using `CallWithCurrentContext` let the owner detect the reentrant call and execute directly instead of queueing behind itself.

## 7. Async Promise settlement: timer and fs as reference implementations

The `timer` module shows the canonical Promise-settlement pattern after the refactor. The module creates a Promise on the owner, captures the current owner-entry context, captures the runtime lifetime context, starts a goroutine, and later settles the Promise through `RuntimeServices.PostWithCustomContext` (`modules/timer/timer.go:162-195`).

The key lines are:

```go
callCtx := runtimebridge.CurrentOwnerContext(vm)
runtimeCtx := runtimeServices.Lifetime()
```

The goroutine waits for one of three outcomes:

```go
select {
case <-callCtx.Done():
    return
case <-runtimeCtx.Done():
    return
case <-timer.C:
    _ = runtimeServices.PostWithCustomContext(callCtx, "timer.sleep.resolve", func(context.Context, *goja.Runtime) {
        _ = resolve(goja.Undefined())
    })
}
```

The file-system async helpers use the same pattern. `asyncValue` and `asyncReadFile` create Promises, capture `callCtx` and `runtimeCtx`, do Go file work in a goroutine, and settle the Promise through `PostWithCustomContext` (`modules/fs/fs_async.go:11-66`). This pattern answers two cancellation questions:

1. Did the operation that created the Promise get canceled?
2. Did the runtime itself close?

Both conditions stop the goroutine from touching JavaScript. Successful completion schedules settlement back on the runtime owner.

## 8. Shutdown: cancel lifetime, wait, interrupt, close resources

The refactor changed runtime shutdown from a simple cleanup sequence into an explicit bounded shutdown path. The current `Runtime.Close(ctx)` does the following (`engine/runtime.go:86-127`):

```text
Runtime.Close(ctx)
  ├─ mark runtime as closing
  ├─ copy and clear registered closers
  ├─ cancel runtime lifetime context
  ├─ wait for runtime owner to become idle
  ├─ if still active, interrupt JavaScript and wait again
  ├─ run closers while runtimebridge services still exist
  ├─ delete runtimebridge services for the VM
  ├─ shutdown owner
  └─ stop event loop
```

Two decisions are worth calling out.

First, lifetime cancellation happens before closers. Runtime-owned goroutines should observe cancellation and begin stopping before cleanup code runs. This prevents new work from continuing while shutdown is in progress.

Second, runtimebridge services are deleted after closers, not before. Some closers need final owner-thread cleanup or access to runtime-scoped values. Deleting services before closers would make those cleanup paths fail at the moment they need the runtime most. The runtime services remain available during cleanup, then `runtimebridge.Delete` removes them before the owner and event loop are stopped (`engine/runtime.go:109-123`).

`waitOwnerIdleOrInterrupt` implements bounded waiting (`engine/runtime.go:130-152`). It waits for owner idleness with a close wait context. If active JavaScript does not finish, it calls `goja.Runtime.Interrupt`, clears the interrupt afterward, and waits again. The default close wait context is currently 250 milliseconds when no deadline is provided (`engine/runtime.go:154-162`). That timeout may become configurable later, but the current behavior is explicit and testable.

## 9. Downstream migration: breaking compile errors were useful

The refactor intentionally avoided backwards-compatible aliases for the ambiguous APIs. That choice created compile errors in downstream packages. Those compile errors were useful because they pointed to code that had to choose a context deliberately.

The downstream sweep found and fixed references in Geppetto, Discord Bot, go-minitrace, css-visual-diff, and Loupedeck. The old-API search looked for:

```bash
runtimebridge\.(Bindings|CurrentContext|OwnerRunner)
runtimeowner\.Runner
\bNewRunner\(
\.NewRuntime\((ctx|context\.Background\(\)|context\.TODO\(\))\)
```

Examples of downstream changes:

- Geppetto moved Go runtime options to `runtimeowner.RuntimeOwner` and explicit engine runtime contexts while keeping its JavaScript `gp.runner` API stable. That distinction matters: not every package-level “runner” term is the go-go-goja owner abstraction.
- Discord Bot replaced `runtimebridge.CurrentContext(vm)` in outbound channel helpers with `runtimebridge.CurrentOwnerContext(vm)` and updated runtime construction.
- go-minitrace updated query runtime construction to pass startup and lifetime options.
- css-visual-diff updated VM-derived runtime module context helpers to use `RuntimeServices.Lifetime()` and `runtimebridge.RuntimeOwner` adapters.
- Loupedeck migrated `loupedeck/state`, `loupedeck/ui`, `loupedeck/anim`, and `loupedeck/present` from old bindings to RuntimeServices helpers.

The Loupedeck migration validated the core design. After migrating retained UI callbacks to `CallWithCurrentContext` and hardware events to `PostWithLifetimeContext`, the generated web/hardware example stopped hanging. The non-hardware smoke passed, and the hardware path ran against a real Loupedeck Live on `/dev/ttyACM0`.

## 10. Documentation and migration surface

The code change was not complete until the docs changed. The repository now has a user-facing xgoja migration help page at `cmd/xgoja/doc/07-migrating-runtime-context-api.md`, an updated async patterns guide at `pkg/doc/03-async-patterns.md`, updated README examples, and a playbook for adding xgoja support at `cmd/xgoja/doc/08-playbook-adding-xgoja-support.md`.

The migration page explains the mechanical replacements:

```text
runtimeowner.Runner              -> runtimeowner.RuntimeOwner
runtimeowner.NewRunner           -> runtimeowner.NewRuntimeOwner
runtimebridge.Bindings           -> runtimebridge.RuntimeServices
runtimebridge.CurrentContext(vm) -> runtimebridge.CurrentOwnerContext(vm)
factory.NewRuntime(ctx)          -> factory.NewRuntime(engine.WithStartupContext(ctx), engine.WithLifetimeContext(ctx))
```

The async patterns guide explains the operational model: choose current owner-entry context for JS-facing callbacks, lifetime context for runtime-owned background work, custom context for request/event operations, and cleanup context for shutdown.

The xgoja provider playbook applies the same rules to new provider packages. It tells provider authors to expose loader-friendly modules, register config sections with `DecodeSectionInto`, register closers for owned resources, return Glazed commands from command providers, and add generated binary smoke tests that prove the provider path.

## 11. What failed along the way

The refactor had several useful failures.

The first broad validation failure was a simple alias issue. An automated replacement inserted `engine.WithStartupContext` into a file that imported the engine package as `ggjengine`. The compiler caught it. This was not a design failure, but it showed why mechanical migration of API names needs focused compile passes.

The second failure came from historical `ttmp` scripts. Pre-commit lint compiled old script packages that still called `factory.NewRuntime(context.Background())`. Those scripts had to be migrated too. That revealed an operational fact about the repository: examples and investigation scripts can be part of lint/test surfaces, so API refactors must either update them or explicitly exclude them.

The third failure was more important. The first implementation of linked custom contexts used a goroutine per call/post and did not cancel linked contexts after completion. PR 41 review correctly flagged that high-frequency async paths could accumulate blocked goroutines until runtime shutdown. The fix moved to `context.AfterFunc`, canceled linked contexts after synchronous calls, and stopped lifetime hooks after posted callbacks. This was the kind of issue that arises only when the API is used in hot paths such as `fs` and `timer` Promise settlement.

The fourth failure was semantic over-renaming. Geppetto has a JavaScript API named `runner`. The Go runtime owner is not the same concept as that package-level JS API. An initial automated replacement renamed too much and broke DTS export parity. The fix kept the JS API stable while migrating the Go owner type.

## 12. Review-critical details

Several parts of this refactor deserve careful review.

### 12.1 RuntimeModuleContext.Context remains startup context

`RuntimeModuleContext.Context` and `RuntimeContext.Context` receive startup context in `engine/factory.go`. That means module registration and runtime initializers should treat `ctx.Context` as construction context, not runtime lifetime. Runtime lifetime is available through `RuntimeServices.Lifetime()` after services are stored. This separation is the central design decision. Reviewers should check module specs that start long-lived goroutines during registration and ensure they use runtime lifetime where appropriate.

### 12.2 PostWithCustomContext must not cancel before callback execution

`PostWithCustomContext` links a custom context to runtime lifetime. If it canceled the linked context immediately after scheduling, the owner would observe a canceled context before the posted callback ran. That would break Promise settlement from goroutines. The final implementation cancels only when enqueue fails, and otherwise unregisters the lifetime hook after the callback executes. This is the most subtle part of the helper implementation.

### 12.3 Runtime.Close keeps services available during closers

`Runtime.Close` deletes runtimebridge services only after closers finish. This ordering is intentional. Moving `runtimebridge.Delete` earlier can break cleanup hooks that need to post final work or inspect runtime-scoped services. Moving owner shutdown earlier can also break cleanup. The current order should be preserved unless tests are added for any proposed alternative.

### 12.4 CurrentOwnerContext fallback is lifetime context

`CurrentOwnerContext(vm)` falls back to runtime lifetime context when no owner-entry context is active. This keeps modules functional in unusual entry paths, but it also means a missing current context may not fail loudly. New code should prefer helper methods whose names document the intended context. Tests should cover current-context propagation where request cancellation matters.

### 12.5 Active-call accounting must remain balanced

`WaitIdle` depends on `beginActive` and `endActive`. Those methods must stay wrapped around both returning owner calls and posted owner callbacks. Panic recovery must not bypass `endActive`. The current implementation uses `defer` in both `invoke` and `invokePost`, which is the right shape.

## 13. How to add a native async module after the refactor

A module that creates asynchronous JavaScript results should use this pattern:

```go
func install(vm *goja.Runtime, services runtimebridge.RuntimeServices) {
    vm.Set("doAsync", func() goja.Value {
        promise, resolve, reject := vm.NewPromise()

        callCtx := runtimebridge.CurrentOwnerContext(vm)
        lifetimeCtx := services.Lifetime()

        go func() {
            result, err := doGoWork(callCtx, lifetimeCtx)
            if err != nil {
                _ = services.PostWithCustomContext(callCtx, "doAsync.reject", func(context.Context, *goja.Runtime) {
                    _ = reject(vm.NewGoError(err))
                })
                return
            }
            _ = services.PostWithCustomContext(callCtx, "doAsync.resolve", func(context.Context, *goja.Runtime) {
                _ = resolve(vm.ToValue(result))
            })
        }()

        return vm.ToValue(promise)
    })
}
```

Use this checklist:

1. Create the Promise on the owner thread.
2. Capture `runtimebridge.CurrentOwnerContext(vm)` before starting the goroutine.
3. Capture `services.Lifetime()` before starting the goroutine.
4. Make Go work observe both contexts when possible.
5. Settle Promise values only through `services.PostWithCustomContext(callCtx, ...)`.
6. Treat errors from `PostWithCustomContext` as cancellation/shutdown outcomes unless the module has a stronger recovery path.

Do not capture `RuntimeModuleContext.Context` and reuse it for later Promise settlement. That is startup context. Do not call `resolve` or `reject` directly from a goroutine. Do not use `context.Background()` as a shortcut for retained callbacks; it opt-outs of request cancellation and shutdown coordination.

## 14. How to choose among the helper methods

The helper names are the public review tool. This is the decision table for new code:

| Situation | Preferred helper | Reason |
| --- | --- | --- |
| JS-facing native function calls/evaluates JS while already in owner execution | `CallWithCurrentContext(vm, ...)` | Preserves request/event context and allows reentrant owner execution. |
| JS-facing native function schedules JS work while already in owner execution | `PostWithCurrentContext(vm, ...)` | Preserves the current owner-entry context for queued work. |
| Runtime-owned background listener posts a hardware/event update not tied to a request | `PostWithLifetimeContext(...)` | Work should stop when runtime closes. |
| Request/HTTP/command operation posts a JS callback | `PostWithCustomContext(req.Context(), ...)` | Work should stop when the request or runtime closes. |
| Synchronous external operation needs a result from JS | `CallWithCustomContext(ctx, ...)` | Caller controls deadline/cancellation and runtime lifetime still cancels it. |
| Cleanup hook needs owner-thread work | Usually `CallWithCustomContext(closeCtx, ...)` | Cleanup should obey close deadline. |

If a call site needs `context.Background()`, it should be treated as a design decision. Sometimes it is correct for tests or top-level CLI processes. In runtime modules, it is usually a bug.

## 15. Validation that mattered

The refactor was validated at several levels.

Focused runtime tests covered the core packages:

```bash
go test ./pkg/runtimebridge ./pkg/runtimeowner ./engine ./modules/timer ./modules/fs -count=1
```

Broader repository validation covered xgoja, jsverbs, HTTP, REPL, and documentation packages. `make lint` caught the staticcheck nil-context warning in `runtimebridge_test.go`, which was fixed by replacing the nil context in the test with an explicit context value.

Downstream validation mattered because the API change crossed repository boundaries. Focused test suites passed in Geppetto, Discord Bot, go-minitrace, css-visual-diff, workspace-manager, goja-git, and Loupedeck. Loupedeck received additional generated xgoja command-provider smoke validation and a hardware validation path using a real device.

The most important behavioral validation was not only that tests passed. It was that the Loupedeck retained UI path, which had previously deadlocked/canceled, ran after the migration. That proved the current-owner-context and reentrant-owner-call fixes in a realistic retained-callback environment.

## 16. Release implications

This is a breaking API cleanup. It removes ambiguous compatibility fields and renames public types. The repository is still pre-1.0, but downstream packages already use it. The next release should be treated as a breaking pre-1.0 release, likely `v0.6.0`.

Before tagging, the release checklist should include:

1. Run `go test ./... -count=1` in `go-go-goja`, or record exact unrelated failures and run the focused stable suite.
2. Run `make lint`.
3. Confirm `xgoja help migrating-runtime-context-api` works.
4. Confirm `xgoja help playbook-adding-xgoja-support` works.
5. Check for stale old API references with:

```bash
rg -n "runtimebridge\.(Bindings|CurrentContext|OwnerRunner)|runtimeowner\.Runner|NewRunner\(|\.NewRuntime\((ctx|context\.Background\(\)|context\.TODO\(\))\)" . -S
```

6. Tag/publish the new version.
7. Update downstream `go.mod` files to the new version.
8. Rerun downstream hooks with `GOWORK=off` after the new version is visible.

The `GOWORK=off` step is important. Several downstream repositories currently compile through the workspace because the workspace contains the refactored `go-go-goja`. Once the new version is tagged, `GOWORK=off` validates that normal module resolution sees the new APIs.

## 17. Final architecture summary

The final architecture is small enough to describe precisely:

```text
engine.Factory
  └─ NewRuntime(WithStartupContext, WithLifetimeContext)
       ├─ creates goja.Runtime
       ├─ starts event loop
       ├─ creates runtimeowner.RuntimeOwner
       ├─ derives runtime lifetime context
       ├─ stores runtimebridge.RuntimeServices for VM
       ├─ registers modules with startup context
       └─ runs initializers with startup context

runtimeowner.RuntimeOwner
  ├─ serializes VM access
  ├─ detects reentrant owner calls
  ├─ installs current owner-entry context stack
  ├─ tracks active owner callbacks
  └─ exposes WaitIdle for shutdown

runtimebridge.RuntimeServices
  ├─ exposes lifetime context
  ├─ exposes owner scheduling subset
  ├─ provides context-specific Call/Post helpers
  └─ links custom contexts to runtime lifetime

engine.Runtime.Close
  ├─ cancels runtime lifetime
  ├─ waits for owner idle
  ├─ interrupts active JS if necessary
  ├─ runs closers while services exist
  ├─ deletes runtimebridge services
  ├─ shuts down owner
  └─ stops event loop
```

The key invariant is that JavaScript execution and Promise settlement cross the owner boundary with an explicit context. The key API design choice is that the context names state the ownership domain. The key implementation detail is that runtime lifetime cancellation is applied consistently without erasing request/event cancellation.

## 18. What should happen next

The next work is release and downstream stabilization, not another API rename. The public model is now clear enough to publish: startup context constructs the runtime, lifetime context owns runtime resources, current owner context follows the active JS/native entry, custom context represents external operations, and close context bounds cleanup.

Future changes should be additive and driven by real call sites. A possible `EventSourceContext` struct can wait until several modules need a richer retained-event API. The current helper set is explicit enough for timer, fs, HTTP, Discord, Loupedeck, jsverbs, and xgoja providers. The most valuable next step is to tag the breaking release, update downstream modules, and make the new context model the documented baseline for every new provider.
