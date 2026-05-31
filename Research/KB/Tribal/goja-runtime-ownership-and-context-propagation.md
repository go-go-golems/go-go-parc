---
title: "Goja Runtime Ownership and Context Propagation — How We Do It"
aliases:
  - goja runtime ownership
  - goja context propagation
  - go-go-goja runtime owner
  - RuntimeOwner pattern
  - goja single-writer VM
  - goja owner thread
  - goja context bridge
tags: [knowledge-base, tribal, goja, go, javascript, concurrency, context, runtime]
status: active
type: knowledge-base
created: 2026-05-31
repos:
  - /home/manuel/code/wesen/go-go-golems/go-go-goja
---

# Goja Runtime Ownership and Context Propagation — How We Do It

> [!summary]
> Every `goja.Runtime` is owned by exactly one `RuntimeOwner`, which serializes all VM access through `Call` (returns a value) and `Post` (fire-and-forget). Per-call Go `context.Context` propagates through `runtimebridge.CurrentOwnerContext(vm)` so that HTTP cancellation, DB timeouts, and tracing reach native module code without being exposed to JavaScript. Async modules do blocking work in goroutines but settle promises only by posting back through the owner — never directly. The `engine.Factory` freezes module policy at build time; each `NewRuntime` call creates a fresh owned VM with its own lifecycle, closers, and runtime services.

## The pattern

The go-go-goja runtime system is built around one invariant: **a single goroutine owns all access to a `goja.Runtime`**. Every other goroutine posts work to that owner. The owner executes closures on the VM's event loop, one at a time. This is not a suggestion; it is the correctness boundary. Two goroutines touching the same `goja.Runtime` concurrently is a data race.

```
engine.Factory (frozen module policy)
  └─ NewRuntime(WithStartupContext, WithLifetimeContext)
       ├─ creates goja.Runtime
       ├─ starts event loop
       ├─ creates RuntimeOwner
       ├─ derives runtime lifetime context
       ├─ stores RuntimeServices for VM in runtimebridge
       ├─ registers modules with startup context
       └─ runs initializers with startup context

RuntimeOwner
  ├─ Call(ctx, op, fn) → (any, error)    // request/response
  ├─ Post(ctx, op, fn) → error            // fire-and-forget
  ├─ detects reentrant owner calls
  ├─ installs current owner-entry context stack
  └─ WaitIdle + Shutdown for clean shutdown

RuntimeServices (module-facing bridge)
  ├─ Lifetime() → context.Context
  ├─ CallWithCurrentContext / PostWithCurrentContext
  ├─ CallWithLifetimeContext / PostWithLifetimeContext
  ├─ CallWithCustomContext / PostWithCustomContext
  └─ links custom contexts to runtime lifetime
```

### The three contexts that matter

The system distinguishes three context scopes that a native module must understand:

| Context | What it controls | When to use |
|---|---|---|
| **Startup context** | Runtime construction, module registration, runtime initializers. | `RuntimeModuleContext.Context` and `RuntimeContext.Context` during `NewRuntime`. |
| **Runtime lifetime context** | Runtime-owned resources after construction. Canceled on `Runtime.Close`. | Background goroutines, hardware listeners, retained callbacks. Access via `RuntimeServices.Lifetime()`. |
| **Current owner-entry context** | The Go `context.Context` active for the currently executing owner call. Falls back to lifetime context when no owner call is active. | Synchronous JS-facing callbacks, database queries, HTTP handler work. Access via `runtimebridge.CurrentOwnerContext(vm)`. |

A fourth context — **custom operation context** — represents external operations like HTTP requests or hardware events. It is linked to runtime lifetime: if the runtime closes, the custom context is also canceled.

### Module registration is runtime-aware

All module registration goes through one interface:

```go
type RuntimeModuleSpec interface {
    ID() string
    RegisterRuntimeModule(ctx *RuntimeModuleContext, reg *require.Registry) error
}
```

`RuntimeModuleContext` gives modules the VM, event loop, owner, lifecycle context, closer registry, and runtime values before `require` is enabled. This is the key architectural shift: static modules and runtime-scoped modules are not separate categories. A default module, an HTTP module, a plugin module, a generated xgoja provider module, and a documentation access module all register through the same interface.

### The async Promise settlement pattern

When a native module needs to do blocking work and return a JavaScript Promise:

1. Create the Promise on the owner thread.
2. Capture `runtimebridge.CurrentOwnerContext(vm)` before starting the goroutine.
3. Capture `RuntimeServices.Lifetime()` before starting the goroutine.
4. Do Go work in a goroutine, observing both contexts.
5. Settle the Promise **only** through `services.PostWithCustomContext(callCtx, op, fn)`.
6. Never call `resolve` or `reject` directly from the goroutine.

The `timer` module is the reference implementation:

```go
callCtx := runtimebridge.CurrentOwnerContext(vm)
lifetimeCtx := services.Lifetime()

go func() {
    select {
    case <-callCtx.Done():
        return
    case <-lifetimeCtx.Done():
        return
    case <-timer.C:
        _ = services.PostWithCustomContext(callCtx, "timer.sleep.resolve",
            func(context.Context, *goja.Runtime) {
                _ = resolve(goja.Undefined())
            })
    }
}()
```

### xgoja generated binaries disable implicit defaults

Generated xgoja binaries must expose only modules selected by their build spec:

```go
builder := engine.NewBuilder(
    engine.WithImplicitDefaultRegistryModules(false),
    engine.WithDataOnlyDefaultRegistryModules(false),
).WithModules(modules...)
```

The buildspec separates **compile-time package selection** (what Go code is in the binary) from **runtime profile selection** (what `require()` names are available). A module can be compiled into the binary without being visible to every command.

## Why we do it this way

**The owner thread prevents data races.** goja's `Runtime` has no internal synchronization. Two goroutines calling `vm.RunString()` concurrently produces undefined behavior. The owner serializes all VM access. Alternatives we considered and rejected:

- **Mutex around every VM call** — Correct but serializes all work including CPU-bound JS. No way to overlap I/O with computation.
- **Separate runtime per goroutine** — Correct for isolation but loses shared state. Doesn't work for REPL sessions where cells build on each other.

**Named contexts prevent the wrong cancellation domain from being used.** The pre-refactor API had a single `runtimebridge.Bindings.Context` that was used for both runtime lifetime and request scope. The Loupedeck UI hang (see [[ARTICLE - Runtime Context Ownership in go-go-goja]]) demonstrated the consequence: a retained hardware callback was created during an HTTP request, used the request context for its posted callbacks, and the request context was canceled when the HTTP handler returned. The callback never fired. The fix was to name contexts by what they control and provide intent-specific helpers whose names document the decision.

**Runtime-aware module registration makes all extension seams converge.** Before the unified `RuntimeModuleSpec`, the codebase had static module specs, runtime registrars, and xgoja provider adapters as separate concepts. Each invented its own lifecycle. The unified interface means plugin modules, HTTP modules, generated xgoja providers, and default modules all attach at the same point.

**Explicit module exposure prevents accidental capability leakage.** A plain `engine.NewBuilder().Build()` exposes the default registry, which includes `fs`, `os`, `exec`, and `database`. That is convenient for developer REPLs but wrong for sandboxed systems. The builder options `WithImplicitDefaultRegistryModules(false)` and `WithDataOnlyDefaultRegistryModules(false)` make the decision visible at the call site.

## Evidence

| Report | Date | Contribution |
|---|---|---|
| [[ARTICLE - go-go-goja Runtime System - Creation Context Scheduling and Modules]] | 2026-05-23 | Canonical description: factory, RuntimeModuleSpec, runtimebridge, owner scheduling, async Promise pattern, close sequence |
| [[ARTICLE - Goja Sandbox Architecture - Lessons from go-go-goja and vm-system]] | 2026-05-23 | Three-system comparison; identifies engine.Runtime as the strongest substrate; proposes sandbox manager on top |
| [[REVIEW - go-go-goja PR 38 - UIDSL attrs and per-call context propagation]] | 2026-05-23 | First implementation of per-call context bridge; `rows.Err()` review point; `uidsl.Attrs` compile-time normalization |
| [[ARTICLE - xgoja - Generated Goja Applications Provider Architecture and Runtime Profiles]] | 2026-05-24 | xgoja buildspec, provider API, runtime profiles, generated command surface, core/host providers |
| [[ARTICLE - xgoja Modules in Existing Runners - Discord Bot Case Study]] | 2026-05-25 | Inserting xgoja modules into existing runners without rewriting them; domain runtime ownership vs. module composition boundary |
| [[ARTICLE - Runtime Context Ownership in go-go-goja]] | 2026-05-26 | The context refactor: named contexts (startup, lifetime, current-owner, custom, cleanup), RuntimeServices helpers, Loupedeck hang fix, breaking API cleanup, downstream migration |
| [[ARTICLE - Go AST Analysis - From JavaScript Bindings to Web Source Browser]] | 2026-05-27 | Demonstrates composable modules: `ast + db + fs + express` in one generated binary |
| [[ARTICLE - Playbook - Building go-go-goja xgoja Provider Packages]] | 2026-05-27 | Provider authoring workflow: domain logic first, narrow JS API, explicit wrapper objects |
| [[ARTICLE - Go AST Analysis - xgoja Bindings and Codebase Navigation]] | 2026-05-27 | Reinforces explicit wrapper object rule for fluent APIs; goja interop should not rely on Go struct reflection |

## Working rules

1. **Never settle a JavaScript Promise from a goroutine directly.** Always post back through the RuntimeOwner using `services.PostWithCustomContext(callCtx, op, fn)`. Calling `resolve` or `reject` from a goroutine is a data race.

2. **Only the RuntimeOwner touches the VM.** Any goroutine that calls `vm.RunString`, `vm.Set`, `vm.ToValue`, `resolve`, `reject`, or any other VM method without going through the owner is a data race.

3. **Always propagate context through `runtimebridge`.** Use `runtimebridge.CurrentOwnerContext(vm)` for request-scoped work inside native functions. Use `RuntimeServices.Lifetime()` for runtime-owned background work. Use `services.PostWithCustomContext(ctx, ...)` for request/event operations. Never use `context.Background()` as a shortcut for retained callbacks.

4. **Name each context by what it controls.** Startup context constructs the runtime. Lifetime context owns runtime resources. Current-owner context follows the active JS/native entry. Custom context represents external operations. The helper name at the call site should document which domain you chose.

5. **Expose explicit JavaScript wrapper objects, not raw Go struct reflection.** Go struct reflection produces awkward JavaScript APIs with wrong property names, missing methods, and confusing prototype chains. Build JavaScript-facing objects explicitly with `exports.Set("methodName", func(...))` and return handles (opaque objects with known methods) when the Go type is complex.

6. **Register modules through `RuntimeModuleSpec` only.** Do not introduce a second registrar abstraction. If code needs `ctx.Require`, it belongs in a `RuntimeInitializer`, not in module registration.

7. **Generated binaries must disable implicit defaults.** xgoja binaries set `WithImplicitDefaultRegistryModules(false)` and `WithDataOnlyDefaultRegistryModules(false)`. The `require()` surface comes only from the buildspec's runtime profiles. If a generated binary doesn't list a module, `require()` must fail.

8. **Three provider patterns exist: simple loader, guarded host-capability, host-services.** Simple loaders just register a `require.ModuleLoader`. Guarded host-capabilities (like `fs`, `exec`) require explicit `config.allow: true`. Host-services (like `express`, `discord`) need live runtime state and lifecycle hooks.

9. **Always call `Runtime.Close(ctx)` when done.** A runtime owns an event loop, bridge services, context, module resources, and possibly plugin subprocesses. `defer rt.Close(context.Background())` is the minimum.

10. **Test runtime isolation by creating two runtimes from the same factory.** A factory is a frozen plan; a runtime is a live instance. Bugs often appear when state accidentally belongs to the factory but should belong to each runtime.

## Gotchas

1. **`PostWithCustomContext` must not cancel before the callback executes.** If the linked context is canceled immediately after scheduling, the owner observes a canceled context before the posted callback runs, breaking Promise settlement from goroutines. The implementation cancels only when enqueue fails and unregisters the lifetime hook after the callback returns.

2. **`CurrentOwnerContext(vm)` falls back to lifetime context.** When no owner call is active, the function returns the runtime lifetime context, not `context.Background()`. This keeps modules functional in unusual entry paths, but it also means a missing current context may not fail loudly. New code should prefer helper methods whose names document the intended context.

3. **`RuntimeModuleContext.Context` is startup context, not lifetime context.** Module registration and runtime initializers receive startup context. If a module starts long-lived goroutines during registration, it must use `RuntimeServices.Lifetime()` for those goroutines, not the context from `RuntimeModuleContext.Context`.

4. **`Runtime.Close` keeps runtimebridge services available during closers.** Services are deleted after closers finish, not before. Some closers need final owner-thread cleanup. Moving `runtimebridge.Delete` earlier breaks cleanup hooks that need to post final work.

5. **Reentrant owner calls are detected and executed directly.** If code is already on the owner path and calls `Call` again, the owner invokes the function directly instead of scheduling it. This prevents deadlocks. The Loupedeck hang was caused by a module that used the wrong context for a reentrant callback, causing the owner to schedule behind itself.

6. **The `context.AfterFunc` pattern prevents goroutine leaks.** The first implementation of linked custom contexts used a goroutine per call, which leaked under high-frequency async paths. The fix uses `context.AfterFunc(lifetime, cancel)` and cleans up after callback execution.

7. **Duplicate module IDs cause build-time validation failure.** The builder validates unique IDs. xgoja includes package, module name, and alias in its generated module spec ID so the same provider module can be mounted under distinct aliases.

8. **ESM import hoisting breaks the SSR sidecar.** The sidecar entry point must use `require()` or explicit `.mjs` extensions — ESM auto-hoisting changes execution order. This is not a goja bug but affects the hosting model for server-side rendered Go+React applications.

9. **Provider package ID must match the buildspec `packages[].id`.** If a provider calls `registry.Package("my-provider", ...)`, the spec must use `id: my-provider`. A mismatch produces confusing runtime creation errors like "runtime main references unknown provider module."

10. **Goja has no JIT; CPU-intensive loops cannot be interrupted cooperatively.** The `Runtime.Close` path uses `goja.Runtime.Interrupt` to break long-running scripts, but this is a best-effort mechanism. For hard CPU limits, a process boundary is required.

## Related KB entries

- [[Tribal/goja-embedding-in-go]] — How we embed goja, expose Go functions as JS APIs, wire `require()`, and handle per-sandbox isolation. This entry covers the embedding layer; the present entry covers the ownership and context layer above it.
- [[Tribal/goja-execution-model]] — Session semantics, IIFE cell rewriting, replay-based restore, and owner-thread discipline for REPL applications. This entry covers REPL-specific execution; the present entry covers the generic runtime substrate.
- [[Tribal/dsl-normalized-config-compiled-plan]] — The engine Factory is a compiled plan (frozen module policy) and each `NewRuntime` is a live instance. This is the DSL→Config→Plan pattern applied to JavaScript runtimes.
- [[On-Ramp/go-cli-with-embedded-spa]] — The SSR sidecar pattern for Go-hosted React SPAs, where the goja runtime serves as the server-side rendering engine.
