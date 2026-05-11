---
title: "goja Execution Model — Sessions, Thread Safety, and Async — How We Do It"
aliases:
  - goja execution model
  - goja session semantics
  - goja thread discipline
  - goja owner thread
  - goja REPL session
tags: [knowledge-base, tribal, goja, javascript, go, concurrency, repl]
status: active
type: knowledge-base
created: 2026-05-11
---

# goja Execution Model — Sessions, Thread Safety, and Async — How We Do It

> [!summary]
> How we structure goja execution at the application level: session semantics (what a session is, how it persists, how it restores) and thread discipline (goroutines do blocking work, post closures back to the VM-owning thread). These two concerns are tightly coupled — session semantics depend on the thread model for correctness. Three projects independently converged on this architecture: the go-go-goja REPL API, Node-like Primitives, and the JS Discord Bot Framework.

## The pattern

Our goja applications treat execution as a product concept, not just a runtime call. A session is a live VM plus an execution policy plus durable history. The VM-owning goroutine is the single arbiter of all mutations. Blocking OS work happens in worker goroutines that post closures back to the owner.

### Session semantics

A goja session is not just a `goja.Runtime`. It is three things:

1. **Live runtime** — The `goja.Runtime` with its current global scope, bindings, and module state.
2. **Execution policy** — Rules for how cells/expressions are evaluated: raw (no rewrite), interactive (IIFE wrap, last-expression return), or persistent (IIFE wrap + binding capture + durable history).
3. **Durable history** — The persisted sequence of evaluations, their captured bindings, console events, and metadata. Stored in SQLite.

```
Session = Live Runtime + Execution Policy + Durable History
```

When a session restores, we replay the persisted source into a fresh runtime. We do not serialize/deserialize the VM state — replay is simpler, more debuggable, and doesn't couple us to goja internals.

### Thread discipline

The goja VM is single-threaded. All VM mutations — `vm.Set()`, `vm.RunString()`, `vm.RunProgram()` — must happen on the same goroutine that created the runtime. We enforce this with the **owner thread** pattern:

```go
type Owner struct {
    runtime *goja.Runtime
    ops     chan func()  // closures posted by worker goroutines
}

// Owner loop — the only goroutine that touches the VM
func (o *Owner) Run(ctx context.Context) {
    for {
        select {
        case fn := <-o.ops:
            fn()  // execute closure on the owner goroutine
        case <-ctx.Done():
            return
        }
    }
}

// Worker goroutine — does blocking OS work, posts result back
func asyncReadFile(owner *Owner, path string, resolve func(goja.Value)) {
    go func() {
        data, err := os.ReadFile(path)
        owner.ops <- func() {
            if err != nil {
                resolve(owner.runtime.NewGoError(err))
            } else {
                resolve(owner.runtime.NewValue(string(data)))
            }
        }
    }()
}
```

The owner loop is the concurrency boundary. Workers never touch the VM directly. The owner never blocks on I/O.

### How they fit together

Session semantics and thread discipline are inseparable in practice. A REPL session that evaluates async code (file reads, HTTP requests, Discord API calls) must route all results back through the owner thread to update the VM state. The session's binding capture depends on the owner being the sole mutator. The owner's closure queue is what makes async results flow back into the session's live runtime.

## Why we do it this way

**Sessions make REPL behavior a product decision, not an accident of implementation.** Without explicit session semantics, a REPL is just a loop that calls `vm.RunString()`. Binding leaks between cells, no way to replay, no way to persist. With sessions, the REPL can offer different execution profiles (raw for debugging, interactive for exploration, persistent for notebooks) and survive process restarts.

**Owner thread prevents data races.** goja's `Runtime` has no internal synchronization. If two goroutines call `vm.RunString()` concurrently, the result is undefined behavior — panics, corrupted state, or silent data loss. The owner thread pattern is the correct way to use goja from a concurrent Go program. Alternatives we considered:

- **Mutex around every VM call** — Correct but serializes all work, including CPU-bound JS computation. No way to overlap I/O with computation.
- **Separate runtime per goroutine** — Correct for isolation, but loses shared state. Doesn't work for REPL sessions where cells build on each other.
- **goja.Runtime from sync.Pool** — Nonsensical; each runtime has independent state.

**Replay-based restore avoids VM serialization coupling.** We could serialize the VM's internal state (global scope, closures, prototypes) and deserialize on restore. But goja's internals are not a stable API — they change between versions. Replay re-executes source into a fresh runtime, which is slower but decoupled from goja internals. If goja's representation changes, replay still works because it operates at the JavaScript source level.

**IIFE cell rewriting gives lexical scope without leaking.** In an interactive REPL, users expect:

```javascript
let x = 10;        // cell 1
let y = x + 1;    // cell 2 — sees x from cell 1
x                   // cell 3 — returns 10
```

But `let` and `const` are block-scoped. If each cell is `vm.RunString(source)`, cell 2 can't see `x` because it's in a different evaluation scope. The fix: wrap each cell in an async IIFE, capture declared bindings, and re-install them as globals before the next cell:

```javascript
// Cell 1 rewritten:
(async () => {
    let x = 10;
    __capture("x", x);  // sentinel to record binding
    return x;
})()

// Before cell 2:
vm.Set("x", 10)  // re-install captured binding

// Cell 2 rewritten:
(async () => {
    let y = x + 1;
    __capture("y", y);
    return y;
})()
```

This gives JavaScript-native scoping semantics (block scope per cell, but accumulated bindings across cells) without a custom parser for `var` hoisting.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `go-go-golems/go-go-goja` | `pkg/replapi/`, `pkg/replsession/`, `pkg/repldb/` | REPL session management, IIFE rewrite, SQLite persistence |
| `go-go-golems/go-go-goja` | `engine/factory.go`, `modules/fs/async*.go` | Runtime factory, async fs module (goroutine → Promise) |
| `2026-04-20--js-discord-bot` | `internal/jsdiscord/`, `internal/bot/` | Discord dispatch: goroutines post interaction results back to owner |

### Related PARC project reports

- [[PROJ - go-go-goja REPL API - Profiles, IIFE Rewriting, and AST-Driven Session Semantics]] — canonical instance: profiles, IIFE rewrite, replay-based restore, SQLite persistence, owner thread, console capture
- [[PROJ - go-go-goja Node-like Primitives - Technical Deep Dive]] — async native module pattern: goroutine does blocking fs I/O, Promise settlement on owner thread
- [[PROJ - JS Discord Bot Framework]] — Discord interaction dispatch: goroutines handle HTTP, post closures back to VM owner

**Also related** (session-like patterns without the full session model):
- [[PROJ - Capsule Lab - A Sandboxed JS Capsule Runtime in the Browser]] — goja-in-WASM; no session persistence, no async (synchronous op-stream)
- [[PROJ - Loupedeck Live Hello World - Serial Go Driver]] — goja for SVG rendering; no session, no async

## Common mistakes

1. **Calling `vm.RunString()` from a non-owner goroutine.** This is the most common and most dangerous mistake. The program appears to work under light load, then crashes or corrupts state under concurrency. The fix is always the owner thread pattern: one goroutine owns the VM, all others post closures.

2. **Evaluating REPL cells without IIFE rewriting.** If you call `vm.RunString("let x = 10")` followed by `vm.RunString("let y = x + 1")`, the second cell throws `ReferenceError: x is not defined`. JavaScript `let`/`const` are block-scoped — each `RunString` creates a new scope. The IIFE rewrite is not optional for interactive REPLs; it's how you make block-scoped declarations visible across cells.

3. **Capturing bindings without re-installing them before the next cell.** The IIFE rewrite captures bindings at the *end* of cell execution. But the next cell needs those bindings available *before* it starts. If you capture `x = 10` from cell 1 but forget to `vm.Set("x", 10)` before evaluating cell 2, the next cell can't see `x`. The capture-and-reinstall cycle must be atomic: capture at end → reinstall before next → evaluate next.

4. **Blocking the owner thread on I/O.** The owner loop must never block. If the owner calls `os.ReadFile()` directly, all other pending closures are stuck waiting. This defeats the entire point of the owner thread pattern. The fix: always do I/O in a worker goroutine, post the result back.

5. **Forgetting to await Promise results before building the cell response.** When a cell returns a Promise (e.g., from an async fs call), the evaluation function must detect the Promise and await it before returning the cell result. If you return the Promise object directly, the caller gets a goja Promise value instead of the resolved result. The REPL API handles this by checking `IsPromise()` on the result value and polling for settlement.

6. **Storing VM object references across sessions.** A `goja.Value` from session 1 is invalid in session 2's runtime. If you cache `goja.Value` instances and try to use them after a session restore (which creates a fresh runtime), you get panics or garbage data. Store serialized values (strings, numbers, JSON) in your persistence layer, not `goja.Value` references.

7. **Replay-based restore that doesn't handle side effects.** Replaying a cell that calls `fs.writeFileSync()` will write the file again. Replaying a cell that sends a Discord message will send it again. If your cells have side effects, replay-based restore is not transparent — you need idempotency guards or a way to mark cells as "replay-skip" during restore.

## Variations

- **Profile-based execution** (REPL API). The same session mechanism supports three profiles: *raw* (no rewrite, for debugging goja internals), *interactive* (IIFE wrap + last-expression return, for exploration), and *persistent* (IIFE wrap + binding capture + durable history, for notebooks). The execution policy is a configuration layer on top of the session model.

- **Async native modules** (Node-like Primitives). The `fs` module does blocking filesystem I/O in a goroutine and returns a Promise. The goroutine posts the result back to the owner thread for Promise settlement. This is the owner thread pattern applied at the module level: the JS code `await fs.readFile("/tmp/data")` triggers a goroutine, the goroutine reads the file, the owner thread settles the Promise.

- **Discord interaction dispatch** (JS Discord Bot). Discord's HTTP callback arrives on any goroutine. The handler posts a closure to the owner thread, which evaluates the JS handler function. The owner thread sends the Discord response back. This is the owner thread pattern applied at the application dispatch level.

- **Op-stream** (Capsule Lab). No owner thread needed — the host calls `dispatch()` synchronously and processes the op stream. No async, no goroutines. The simplest variation because it runs in a WASM sandbox with no I/O access.
