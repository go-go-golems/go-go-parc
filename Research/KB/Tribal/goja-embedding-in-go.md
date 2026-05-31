---
title: "goja: Embedding a JavaScript Interpreter in Go — How We Do It"
aliases:
  - goja embedding
  - goja in Go
  - Go JavaScript interpreter
tags: [knowledge-base, tribal, goja, javascript, go, interpreter, wasm]
status: active
type: knowledge-base
created: 2026-05-11
---

# goja: Embedding a JavaScript Interpreter in Go — How We Do It

> [!summary]
> How we embed the goja ECMAScript interpreter in Go applications, expose Go functions as JavaScript APIs, wire the `require()` module system, use `RuntimeHook` for tracing and debugging, and handle the gotchas that come up every time.

## The pattern

We embed goja as a scripting/runtime layer inside Go applications. The host Go code owns the sandbox boundary: it creates the `goja.Runtime`, installs API objects, evaluates JS source, and mediates all side effects. The JS code running inside goja has no access to the filesystem, network, or DOM unless the host explicitly provides it.

```go
vm := goja.New()

// Expose a Go function as a JS API
vm.Set("drawRect", func(call goja.FunctionCall) goja.Value {
    x := call.Argument(0).ToInteger()
    y := call.Argument(1).ToInteger()
    w := call.Argument(2).ToInteger()
    h := call.Argument(3).ToInteger()
    hostDrawRect(int(x), int(y), int(w), int(h))
    return goja.Undefined()
})

// Evaluate JS that calls back into Go
_, err := vm.RunString(`
    drawRect(10, 10, 100, 50);
`)
```

Key elements of our standard approach:

1. **Fresh Runtime per sandbox** — Each isolated JS context gets its own `goja.Runtime`. No sharing of state between sandboxes. This is the isolation boundary.
2. **Host-mediated side effects** — The JS code calls API functions (like `drawRect`, `setInterval`, `log`) that the Go host installs via `vm.Set()`. The host decides whether to allow each operation.
3. **Permission-locked API surface** — Before evaluating JS source, the host installs only the API functions the sandbox has declared permissions for. A sandbox without `clock` permission doesn't get `setInterval`.
4. **Op-stream response pattern** — For WASM kernels, the host calls `dispatch()` and receives a JSON array of `ops` (operations the JS wants the host to perform). The host processes each op and then calls `dispatch()` again.

## Why we do it this way

- **goja is pure Go** — no CGO, no external V8 binary, compiles to WASM. This means our JS runtime cross-compiles everywhere Go does.
- **goja is embeddable** — The `goja.Runtime` is a single Go struct. Create it, configure it, run code. No process spawning, no IPC, no FFI.
- **goja has no JIT** — Slower than V8, but deterministic. Same input always produces same output. This matters for testing and reproducibility.
- **ES5.1+ is enough for our APIs** — We're not running arbitrary web apps. We're running controlled domain scripts. ES5.1 with some ES6 additions (arrow functions, let/const, template literals via goja's extensions) covers our needs.

Alternatives we considered and rejected:
- **V8/QuickJS via CGO** — Faster, but CGO breaks cross-compilation and WASM builds. QuickJS has memory safety concerns.
- **Browser-native JS** — No sandboxing control. The JS code can access the DOM, network, and localStorage unless we add complex proxy layers.
- **ShadowRealm** — Not widely supported yet. Doesn't give us Go-side control of the API surface.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `go-go-golems/go-go-goja` | `modules/`, `pkg/` | Module system, `require()` wiring, IIFE rewriting, native module adapters |
| `corporate-headquarters/loupedeck` | `internal/js/` | Loupedeck JS API layer (SVG, animation, scheduling) |
| `2026-04-02--capsule-lab` | `kernel/` | WASM sandbox, op-stream bridge, permission enforcement |
| `corporate-headquarters/pinocchio` | `internal/jsrepl/` | REPL and tool-call dispatch |

### Related PARC project reports

- [[PROJ - Capsule Lab - A Sandboxed JS Capsule Runtime in the Browser]] — goja-in-WASM sandbox with op-stream API
- [[PROJ - Loupedeck Live Hello World - Serial Go Driver]] — goja embedded in Go process for SVG/animation
- [[PROJ - go-go-goja Plugins - Since origin main]] — module system and require() wiring
- [[PROJ - go-go-goja REPL API - Profiles, IIFE Rewriting, and AST-Driven Session Semantics]] — profile-based execution, IIFE rewrite, session semantics
- [[PROJ - go-go-goja Node-like Primitives - Technical Deep Dive]] — runtime factory composition, data-only vs host-access module split
- [[PROJ - JS Discord Bot Framework]] — goja-based bot host with defineBot DSL
- [[PROJ - go-go-goja jsverbs - JavaScript to Glazed Commands]] — JS-defined Glazed commands

**Variations** (projects that extend this pattern):
- **Profile-based execution** (REPL API) — raw/interactive/persistent profiles configure session behavior on top of the base embedding
- **Runtime factory composition** (Node-like Primitives) — engine.NewBuilder() with module specs and runtime initializers for explicit capability selection
- **JS-defined Glazed commands** (jsverbs) — .js files scanned as command definitions, exposed as Glazed verbs

## Common mistakes

1. **goja exports JS `NaN` as Go `math.NaN()`, which `json.Marshal` rejects** — The fix is recursive NaN sanitization before any JSON serialization of goja-exported values. Every pipeline that exports goja values to JSON needs this guard.

2. **`goja.FunctionCall` arguments are `goja.Value`, not Go types** — You must call `.ToInteger()`, `.ToString()`, `.ToFloat()` etc. Calling `call.Argument(0).Export()` and type-asserting works but is slower and loses type safety.

3. **ES5.1 means no Promises, no `async/await`** — If your JS code uses `fetch()` or any async pattern, you need to provide a callback-based API from Go and bridge it manually. There is no `Promise` in goja by default.

4. **Runtime is not goroutine-safe** — A single `goja.Runtime` must not be used from multiple goroutines concurrently. If you need concurrent execution, create separate Runtimes (one per goroutine) or add a mutex.

5. **Circular references in JS objects leak memory** — goja's GC can't collect JS objects that reference each other in a cycle if Go also holds a reference. Break cycles explicitly or let Go references go out of scope.

## Variations

> [!note]
> For session semantics, thread discipline, and async patterns, see the companion entry: [[Tribal/goja-execution-model]].

- **goja-in-WASM** (Capsule Lab pattern): The goja Runtime runs inside a WASM kernel. The browser host calls `dispatch()` and receives an op stream. This adds a serialization boundary but gives complete control over the sandbox.

- **goja as embedded scripting** (Loupedeck pattern): The goja Runtime runs directly in the Go process. JS code calls Go functions synchronously. No serialization — Go and JS share memory within the same process.

- **goja REPL with tool-call dispatch** (Pinocchio pattern): The goja Runtime exposes a REPL where JS code can call Go "tools" that perform side effects. Each tool call is logged and can be replayed.

For the runtime ownership and context propagation model (RuntimeOwner, RuntimeServices, named contexts, async Promise settlement), see [[Tribal/goja-runtime-ownership-and-context-propagation]].
