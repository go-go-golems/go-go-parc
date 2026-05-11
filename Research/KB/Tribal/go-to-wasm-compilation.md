---
title: "Go → WASM: Compiling Go to WebAssembly — How We Do It"
aliases:
  - go wasm
  - tinygo wasm
  - go to wasm
  - wasm from go
tags: [knowledge-base, tribal, go, wasm, webassembly, tinygo, browser]
status: active
type: knowledge-base
created: 2026-05-11
---

# Go → WASM: Compiling Go to WebAssembly — How We Do It

> [!summary]
> How we compile Go programs to WebAssembly, bridge Go and JavaScript through `syscall/js`, handle the CGo limitation (TinyGo for CGo-free builds, standard Go for everything else), and structure the host/kernel boundary so the WASM module is testable from Go without a browser.

## The pattern

We compile Go code to WASM using `GOOS=js GOARCH=wasm`. The output is a `.wasm` binary that runs inside a browser's WebAssembly runtime, mediated by a JavaScript "glue" layer that `wasm_exec.js` provides. The Go code cannot access the DOM, network, or filesystem directly — it communicates with the browser through `syscall/js` function calls.

The host/kernel split is deliberate. The WASM binary is the *kernel*: it owns the computation, maintains internal state, and produces results. The browser is the *host*: it owns the display, handles user input, and mediates side effects. The boundary between them is a thin API layer that both sides agree on.

```go
// Kernel exposes a dispatch function that the host calls
js.Global().Set("dispatch", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
    // Parse the incoming command
    cmd := args[0].String()

    // Execute the kernel logic
    result := kernel.Dispatch(cmd)

    // Return the result as a JSON string (or js.Value)
    return js.ValueOf(result.JSON())
}))
```

The host calls `dispatch()` and receives structured results. Every side effect the kernel wants to perform (drawing a rectangle, making a network request, logging a message) is returned as an *op* in the result, and the host decides whether to execute it. This is the op-stream pattern from our goja embedding work, applied at the WASM boundary.

## Why we do it this way

**Go compiles to WASM without CGo.** This is the key property. Our Go codebase is pure Go — no C bindings, no CGo, no platform-specific build tags. This means `GOOS=js GOARCH=wasm go build` works out of the box. The moment you add CGo (SQLite, image processing libraries, anything using `cgo`), you need TinyGo, and TinyGo has a smaller standard library and different runtime behavior.

**`syscall/js` is the bridge, not a crutch.** The `syscall/js` package lets Go code call JavaScript functions and receive JavaScript values. It's the only way to interact with the browser from WASM Go. We use it for: registering callable functions (`js.Global().Set`), reading browser state (`js.Global().Get("document")`), and receiving callbacks from JavaScript events.

**The op-stream pattern makes the kernel testable.** If the kernel directly called `document.getElementById()`, you couldn't test it without a browser. By returning ops instead of executing them, the kernel is a pure function: input command → output ops. This can be tested from Go with `go test`.

## Where it lives

| Repo | Use | Compiler |
|------|-----|----------|
| `2026-04-02--capsule-lab` | goja sandbox in WASM | Go (standard) |
| `corporate-headquarters/sqlide` | SQL IDE in browser | Go (standard) |
| `corporate-headquarters/json-flattener` | JSON tool in browser | Go (standard) |
| `corporate-headquarters/vt100` | Terminal emulator | Go (standard) |
| `corporate-headquarters/codebase-browser` | Code navigator | Go (standard) |

### Related PARC project reports

- [[PROJ - Capsule Lab - A Sandboxed JS Capsule Runtime in the Browser]] — goja-in-WASM with op-stream host/kernel boundary
- [[ARTICLE - Playbook - Self-Contained Go Wasm and JavaScript Browser Applications]] — our general WASM-from-Go playbook

## Common mistakes

1. **Using TinyGo when you don't need CGo.** TinyGo has a smaller runtime, no garbage collector (it uses a simple allocator), and missing standard library packages (`encoding/json`, `database/sql`, parts of `net`). If your code is pure Go, use the standard compiler. TinyGo is for when you need CGo (SQLite, image processing via C libraries) and can accept the reduced runtime.

2. **Direct DOM access from Go.** Code like `js.Global().Get("document").Call("getElementById", "canvas")` ties the kernel to the browser. If you need to test it, you need a headless browser. Instead, have the host pass the canvas context as a parameter: the host calls `kernel.init(canvas)`, passing the canvas JS value. The kernel stores it but never accesses the DOM directly.

3. **Blocking in a callback.** The Go WASM runtime runs on a single thread. If a `js.FuncOf` callback blocks (e.g., waiting on a channel), the entire WASM module freezes. Use `go func()` to spawn a goroutine, do the work, and call back when done.

4. **Forgetting `wasm_exec.js` version matching.** The `wasm_exec.js` glue file is version-locked to the Go version that compiled the WASM binary. A mismatch between `wasm_exec.js` version and the compiled binary causes cryptic runtime errors ("Go program has already exited"). Always copy `wasm_exec.js` from the same Go installation used to build.

5. **Large WASM binaries from heavy dependencies.** A Go WASM binary that imports `encoding/json`, `html/template`, and `net/http` can be 10–20 MB. For browser delivery, this is painful. Consider: can the kernel be a small computation unit that receives pre-parsed JSON from the host? Can image processing happen in the browser? Strip dependencies ruthlessly.

## Variations

- **TinyGo with CGo for SQLite in the browser**: The SQLide project compiles SQLite (a C library) via TinyGo's CGo support. The WASM binary runs SQLite queries in the browser with zero network calls. The tradeoff: TinyGo's runtime limitations (no `encoding/json` with struct tags, reduced `reflect` support) require workarounds.

- **Go+goja in WASM for JavaScript sandboxing**: The Capsule Lab pattern — compile the goja interpreter to WASM, then run user-provided JavaScript inside goja inside WASM. Three layers of sandboxing: the browser sandbox, the WASM sandbox, and the goja sandbox. No other system gives you this depth of isolation for running untrusted JavaScript.
