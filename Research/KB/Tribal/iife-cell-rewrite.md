---
title: "IIFE Cell Rewrite — How We Do It"
aliases:
  - repl iife rewrite
  - async iife cells
  - cell wrapping
  - repl lexical capture
tags: [knowledge-base, tribal, goja, repl, javascript]
status: active
type: knowledge-base
created: 2026-05-11
---

# IIFE Cell Rewrite — How We Do It

> [!summary]
> For a JavaScript REPL to feel interactive, each submitted cell must behave like a small lexical program while still sharing state with later cells. We achieve that by rewriting cells into async IIFEs, capturing declared bindings, and reinstalling them before the next evaluation. This pattern appears in the REPL API, Goja REPL Hardening, and the broader goja execution model.

## The pattern

A raw `vm.RunString(cell)` loop does not give a good JS notebook/REPL experience. `let` and `const` are block-scoped, so declarations in one evaluation do not naturally become visible in the next.

We fix that by rewriting each cell into an async immediately-invoked function expression:

```javascript
(async () => {
  let x = 10;
  __capture("x", x);
  return x;
})()
```

The evaluation pipeline becomes:

1. analyze the cell,
2. wrap it in an async IIFE,
3. detect/capture declared bindings,
4. await the result if needed,
5. reinstall captured bindings into the next runtime state.

## Why we do it this way

**Lexical semantics stay intact inside a cell.** The cell still behaves like real JS code.

**The REPL still feels stateful across cells.** Captured bindings are made available to later evaluations.

**Async results fit naturally.** Using an async IIFE means `await`-style flows and promise handling fit the same envelope.

This is the compromise between “real JavaScript semantics” and “interactive notebook semantics.”

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `go-go-goja` | `pkg/replapi/`, `pkg/replsession/` | core REPL/session implementation |
| `go-go-goja` | REPL hardening work | timeout recovery, persistence, refactor around the same rewrite model |
| `goja-execution-model` | KB companion | explains how rewriting fits sessions + owner-thread discipline |

### Related PARC project reports

- [[PROJ - go-go-goja REPL API - Profiles, IIFE Rewriting, and AST-Driven Session Semantics]] — canonical implementation
- [[PROJ - Goja REPL Hardening]] — correctness and recovery work around the same rewrite model
- [[Tribal/goja-execution-model]] — broader runtime/session context

## Common mistakes

1. **Using plain `RunString` per cell.** That breaks cross-cell visibility for lexical declarations.

2. **Capturing but not reinstalling.** Capturing `x` at the end of one cell is useless if the next evaluation does not see `x` before execution starts.

3. **Returning the Promise object instead of its resolved value.** If the IIFE is async, the host must await settlement before producing the REPL result.

4. **Forgetting that side effects replay on restore.** If restoration replays prior cells, side-effecting cells can run again.

5. **Mixing rewrite policy and runtime policy.** The rewrite solves lexical/state behavior. Timeout, persistence, and session ownership are separate concerns.

6. **Treating the rewrite as parser-free magic.** Real implementations still need analysis to know what to capture and how to preserve last-expression semantics.

## Variations

- **Interactive profile** — rewrite for last-expression return and cross-cell convenience.
- **Persistent profile** — rewrite plus durable history and replay.
- **Hardening pass** — same rewrite model, stronger timeout and persistence invariants.
