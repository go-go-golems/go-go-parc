---
title: "WebAssembly from Go"
aliases:
  - wasm go
  - go wasm
  - goos=js goarch=wasm
  - syscall/js
  - wasm_exec.js
tags: [knowledge-base, on-ramp, wasm, go, webassembly, browser, syscall-js]
status: active
type: knowledge-base
created: 2026-05-11
---

# WebAssembly from Go

> [!summary]
> Go compiles to WebAssembly with `GOOS=js GOARCH=wasm`. The output runs in the browser with a JavaScript glue layer (`wasm_exec.js`). Go code communicates with the browser through `syscall/js`; it cannot access the DOM, network, or filesystem directly. This entry covers the compilation pipeline, the Go↔JS bridge, the difference between standard Go and TinyGo for WASM, and the structural pattern that keeps your WASM kernel testable from Go without a browser.

## The idea in one paragraph

Go's WASM target compiles your Go program into a `.wasm` binary that runs inside the browser's WebAssembly runtime. The binary is not standalone — it requires `wasm_exec.js`, a JavaScript glue file that bridges between the browser's WebAssembly API and Go's runtime expectations (goroutine scheduler, garbage collector, `syscall/js` calls). Your Go code runs in a sandbox: it can compute, allocate memory, and call functions registered through `syscall/js`, but it cannot touch the browser's DOM, network, or filesystem unless the JavaScript host explicitly passes those capabilities in.

## The compilation pipeline

```bash
# Compile Go to WASM
GOOS=js GOARCH=wasm go build -o kernel.wasm ./cmd/kernel

# Copy the matching glue file (version must match Go version!)
cp "$(go env GOROOT)/misc/wasm/wasm_exec.js" ./web/

# In the browser, load both:
# <script src="wasm_exec.js"></script>
# <script>
#   const go = new Go();
#   WebAssembly.instantiateStreaming(fetch("kernel.wasm"), go.importObject)
#     .then(({ instance }) => go.run(instance));
# </script>
```

Three things can go wrong here:

1. **Version mismatch between `wasm_exec.js` and the compiled binary.** The glue file is version-locked to the Go release. A binary compiled with Go 1.22 won't work with `wasm_exec.js` from Go 1.21. Always copy from the same Go installation used to compile.

2. **MIME type not set.** The web server must serve `.wasm` files as `application/wasm`. Many static file servers default to `application/octet-stream`, which causes `WebAssembly.instantiateStreaming` to fail. Either configure the server or use `WebAssembly.instantiate` (slower, but works with any MIME type).

3. **Large binary size.** A Go WASM binary that imports `encoding/json`, `net/http`, or `html/template` is 10–20 MB. For browser delivery, this means a long initial load. Strip dependencies ruthlessly: can the host pre-process data and pass it in? Can image rendering happen in Canvas API instead of Go?

## The Go↔JS bridge

`syscall/js` is the only way for Go WASM code to interact with the browser. It provides:

```go
// Register a Go function as a JavaScript global
js.Global().Set("dispatch", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
    result := processCommand(args[0].String())
    return js.ValueOf(result)
}))

// Call a JavaScript function from Go
canvas := js.Global().Get("document").Call("getElementById", "canvas")
ctx := canvas.Call("getContext", "2d")
ctx.Call("fillRect", 10, 10, 100, 50)

// Receive a callback from JavaScript
button := js.Global().Get("document").Call("getElementById", "submit")
button.Call("addEventListener", "click", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
    handleSubmit()
    return nil
}))
```

The bridge is synchronous: when Go calls `ctx.Call("fillRect", ...)`, it blocks until JavaScript executes the call. When JavaScript calls `dispatch()`, it blocks until Go returns. This means:

- **Blocking in Go blocks the browser tab.** If a `js.FuncOf` callback does heavy computation, the UI freezes. Spawn a goroutine: `go processAsync()` and return immediately.
- **JavaScript values are garbage-collected differently.** `js.Value` objects hold a reference to a JavaScript value. Go's GC doesn't know about JavaScript's GC. Call `value.Release()` when you're done with a `js.FuncOf` to prevent leaks on both sides.

## Standard Go vs TinyGo for WASM

| Property | Standard Go | TinyGo |
|----------|-------------|--------|
| CGo support | No (in WASM) | Yes (SQLite, C image libs) |
| Binary size | 10–20 MB | 1–5 MB |
| Standard library | Full | Partial (no `encoding/json` struct tags, limited `reflect`) |
| Garbage collection | Full concurrent GC | Simple mark-sweep |
| Goroutines | Full support | Limited (no preemption in some cases) |
| `syscall/js` | Full support | Full support |

Use **standard Go** unless you need CGo. TinyGo's reduced runtime means you'll spend time working around missing standard library features. The binary size difference (10 MB vs 2 MB) matters less with gzip compression (both compress to ~2–3 MB).

## The testable kernel pattern

Direct `syscall/js` calls tie your code to the browser. Instead, structure the WASM binary as a kernel that receives commands and returns results:

```go
// kernel.go — pure Go, testable with `go test`
func Dispatch(cmd string) Result {
    // All logic here — no syscall/js calls
    return processCommand(cmd)
}

// main.go — WASM entry point, thin bridge
func main() {
    js.Global().Set("dispatch", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
        result := Dispatch(args[0].String())
        json, _ := json.Marshal(result)
        return string(json)
    }))
    <-make(chan struct{}) // Block forever
}
```

The `Dispatch` function is pure Go. It can be tested from Go without a browser. The `main` function is a thin adapter that registers the bridge and blocks. This separation means your WASM code is testable with `go test` and debuggable from Go, not only from browser DevTools.

## Where to go deeper

- **Go Wiki: WebAssembly** — <https://github.com/golang/go/wiki/WebAssembly> — Official compilation instructions and known issues.
- [[Tribal/go-to-wasm-compilation]] — Our specific patterns for compiling Go to WASM.
- [[Tribal/goja-embedding-in-go]] — The three-layer sandbox pattern (browser → WASM → goja) for running untrusted JavaScript.
- [[PROJ - Capsule Lab - A Sandboxed JS Capsule Runtime in the Browser]] — testable kernel pattern, op-stream API, permission enforcement
