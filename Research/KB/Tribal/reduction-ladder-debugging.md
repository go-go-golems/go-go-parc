---
title: "Reduction-Ladder Debugging — How We Do It"
aliases:
  - minimal toxic step debugging
  - debug by reduction
  - smallest toxic step
  - smoke page debugging
tags: [knowledge-base, tribal, debugging, investigation, systems]
status: active
type: knowledge-base
created: 2026-05-11
---

# Reduction-Ladder Debugging — How We Do It

> [!summary]
> When a complex system fails, we do not keep debugging at the level of the full system. We shrink the problem until the smallest toxic step is obvious. The output is a reduction ladder: full workflow → smaller subsystem → smaller input → alternate mode → minimal reproducer. This pattern showed up independently in PaperS3 WAMR, Cardputer Web Serial, and Geppetto's thinking-stream bug.

## The pattern

A reduction ladder is a deliberate sequence of smaller experiments that remove variables one by one.

The generic shape is:

```text
full system fails
  -> smaller subsystem still fails
  -> smaller input still fails
  -> swap one mode / one flag / one boundary
  -> identify the first tiny step after which failure becomes inevitable
```

The goal is not just to create a minimal repro. The goal is to find the **first poisonous transition**.

## Why we do it this way

**Most failures are diagnosed at the wrong level.** If the whole product is broken, the failure might still come from one tiny operation deep inside a loader, transport loop, or normalization layer.

**Complex systems hide causality.** Display code, network code, parsers, runtimes, and persistence layers can all make the same failure look plausible. Reduction removes explanation space.

**A good reduction ladder changes one variable at a time.** That makes the final explanation defensible instead of speculative.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `esp32-s3-m5` | PaperS3 WAMR tickets | full run → load-only → empty-module → ownership flags |
| `2026-04-02--cardputer-web-demo` | `web/smoke.html`, serial transport debugging | full app → smoke page |
| `use-open-responses/geppetto` | Together/Qwen stream normalization tickets | full stack → raw provider stream → field-level delta analysis |

### Related PARC project reports

- [[PROJ - PaperS3 WAMR Debugging - Embedded Wasm Root Cause]] — canonical reduction ladder: full runtime → load-only → embedded buffer vs RAM copy → empty-module → ownership flag
- [[PROJ - Cardputer Web Serial Demo - Technical Project Report]] — smoke page proves transport while main app still looks broken
- [[PROJ - Geppetto - Open Responses and Chat Boundary Cutover]] — isolate provider-specific reasoning delta loss from full application stack

## The three canonical examples

### 1. PaperS3 WAMR

The visible crash looked like a PSRAM/display/runtime mystery. The ladder reduced it to:
- full Wasm run + display
- instantiate-only
- load-only
- embedded direct buffer vs RAM copy
- `return-42.wasm` vs `empty-module.wasm`
- `binary_freeable=true`
- `reuse_const_strings=false`

That isolated the toxic step:
**WAMR mutating flash-mapped read-only bytes in place**.

### 2. Cardputer Web Serial

The visible failure looked like “browser app is broken, maybe device or transport is flaky.”
The ladder reduced it to:
- full main UI
- minimal `smoke.html`
- open port
- dump lines
- send one manual frame

That proved the transport layer was healthy. The bug had to be above it.

### 3. Geppetto thinking-stream bug

The visible failure looked like “Together/Qwen thinking is missing somewhere in the stack.”
The ladder reduced it to:
- full Geppetto/Pinocchio stack
- raw provider stream inspection
- field-level delta comparison
- `delta.reasoning` vs `delta.reasoning_content`

That isolated the toxic step:
**the abstraction layer was dropping the provider-specific field**.

## Common mistakes

1. **Changing multiple variables per step.** If you switch input, runtime mode, transport, and logging all at once, you do not know what fixed or broke the system.

2. **Stopping at the first workaround.** A workaround that makes the failure disappear is useful, but the ladder should keep going until you know which precise step was toxic.

3. **Debugging only at the top of the stack.** Logs from the full app are often too noisy. Reduction means moving downward until the boundary of failure is narrow.

4. **Assuming the crash site is the cause site.** In PaperS3 WAMR the visible crash happened later in PSRAM touch, not where the loader did the bad mutation.

5. **Not preserving the ladder.** The order of experiments matters. If you only record the final answer and not the sequence, future debugging starts from scratch.

6. **Skipping the "boring" smoke test.** The smallest transport-only or parser-only test is often the fastest way to recover trust in a lower layer.

## Variations

- **Mode reduction** — full app vs smoke page vs direct API call.
- **Input reduction** — real payload vs tiny payload vs empty payload.
- **Boundary reduction** — full stack vs one layer lower (provider stream, loader, transport loop).
- **Ownership/flag reduction** — same input, one ownership flag or runtime switch changed.
