---
title: "JS-to-Wasm Compiler Architecture"
aliases:
  - javascript to wasm compiler
  - js to webassembly compiler
  - acorn to wasm
  - direct wasm emitter
tags: [knowledge-base, on-ramp, compiler, wasm, javascript, webassembly]
status: active
type: knowledge-base
created: 2026-05-11
---

# JS-to-Wasm Compiler Architecture

> [!summary]
> A JS-to-Wasm compiler takes a restricted JavaScript-like language, parses it into an AST, lowers that AST into a simpler internal model, and emits WebAssembly that preserves a small, explicit runtime contract. The hard part is not parsing JavaScript. The hard part is choosing a subset, representing closures and mutable state, and keeping the generated Wasm valid as the language grows.

## The idea in one paragraph

A practical JS-to-Wasm compiler is usually not “JavaScript, but in Wasm.” It is a compiler for a deliberately smaller language that borrows JavaScript syntax and some JavaScript semantics. The compiler parses source code, analyzes functions and variables, decides how values live in Wasm locals or linear memory, and emits a `.wasm` module. As features grow, the architecture succeeds or fails based on whether the internal runtime model stays simple enough to extend.

## Why we care

Two of our reports study this pattern directly:

- [[PROJ - Generic Agent - Principled Compiler Experiment]]
- [[PROJ - GPT Base Principles Compiler Experiment - Principles-Guided JS to Wasm Compiler]]

Both are useful because they are not just toy parsers. They hit real compiler problems: closures, lambda lifting, boxed mutation, simple type propagation, direct Wasm binary emission, and the need for disassemblers, fixtures, and playgrounds to debug the result.

## The minimum architecture

A small JS-to-Wasm compiler usually has five layers:

1. **Parser** — turns source into an AST, often with Acorn.
2. **Front-end analysis** — collects function names, variables, and basic semantic facts.
3. **Lowering / compilation model** — turns JS constructs into a smaller machine-oriented representation.
4. **Runtime layout decisions** — decides what stays in Wasm locals and what must move into linear memory.
5. **Wasm emission** — writes module sections, function bodies, tables, exports, and code bytes.

Very roughly:

```text
JavaScript source
  -> Acorn AST
  -> compiler/lowering passes
  -> internal module model
  -> Wasm encoder
  -> .wasm binary
```

That picture is deceptively simple. The real work is hidden in the middle: what exactly counts as a local, a closure environment, a boxed mutable cell, a string, an object, or a callable function pointer?

## The key design decision: choose a language you can actually compile

The first real architectural move is to stop pretending you are compiling all of JavaScript. A manageable compiler picks a subset and makes the runtime rules explicit.

Typical supported features in our reports include:
- function declarations,
- `let` / `const` / limited `var`,
- arithmetic and comparisons,
- control flow,
- closures,
- arrays or fixed-shape objects,
- simple printing or host intrinsics.

Typical things deliberately *not* implemented include:
- full prototype semantics,
- `this` in all forms,
- reflection-heavy dynamic behavior,
- arbitrary coercion rules,
- the browser or Node runtime.

This is not cheating. It is the only way to build a compiler whose semantics you can still reason about.

## How control flow usually maps

Wasm is structured. JavaScript ASTs are not quite the same thing. So the compiler needs an explicit lowering strategy.

For example:
- `if` becomes conditional blocks,
- loops become labeled Wasm block/loop structures,
- `break` and `continue` require branch target bookkeeping,
- expression statements often need explicit `drop` instructions.

A useful invariant from the paired compiler experiments is: **every compiled expression should leave a predictable value effect on the Wasm stack**. Once that invariant is blurry, everything downstream becomes harder to debug.

## Closures are the first big architectural cliff

A closure is where most “small compiler” projects stop being small. Wasm does not natively give you JavaScript closures with captured lexical variables. You have to represent them yourself.

The common move is **lambda lifting**:

1. Turn nested functions into top-level functions.
2. Add an explicit hidden environment parameter.
3. Build a closure object in linear memory.
4. Store captured values, or pointers to captured cells, in that object.
5. Use a function table plus `call_indirect` for dynamic dispatch.

Conceptually:

```text
function outer(x) {
  return function inner(y) { return x + y }
}
```

becomes something more like:

```text
inner_lifted(env, y) = load(env.x) + y
closure = { table_index: inner_lifted, captured_x: x }
```

This is where runtime layout becomes architecture, not implementation detail.

## Mutable captured variables usually require boxing

If a variable is both:
- captured by a closure, and
- mutated,

then storing its value directly in a closure snapshot is wrong. The closure and outer scope need shared storage.

The standard fix is **boxing**:
- allocate a heap cell,
- store the current value in that cell,
- let both the outer scope and closures load/store through the pointer.

Without boxing, you get the classic bug where closures see stale values or updates do not propagate.

## Types matter even in “dynamic” experiments

Even a tiny JS-like compiler needs some value discipline. The paired reports use a restricted numeric model and limited inference/propagation to decide when code should be treated as integer-like or float-like.

The lesson is not “build a big type system.” The lesson is: **Wasm is typed, so your compiler must make type decisions somewhere.** If you avoid the question, the encoder or validator will answer it for you with errors.

## Direct Wasm emission means you own the binary format

Once you emit `.wasm` directly, you are responsible for:
- section ordering,
- function/type/table indices,
- LEB128 integer encoding,
- locals declarations,
- block signatures,
- `call_indirect` type indices,
- default returns on all control paths,
- valid stack discipline.

This is why small compilers often grow support tools early:
- a disassembler,
- fixtures,
- golden outputs,
- a web playground,
- benchmark scripts.

The tooling is not side work. It is how you stay sane while debugging binary output.

## What goes wrong

### Pretending the subset is larger than it is

Many compiler bugs are really specification bugs. The source language “looks like JavaScript,” so it is easy to accidentally promise semantics you do not implement.

### Adding features before stabilizing the runtime model

Closures, arrays, objects, and strings all want memory layout decisions. If every new feature invents a special case, the compiler becomes unreviewable.

### Treating captured mutation like ordinary locals

This is the boxing problem. A closure that should share state instead gets a copy.

### Losing control of Wasm validity

A compiler can produce bytes that look plausible but fail validation because a branch target is wrong, a return path is missing, or stack effects do not line up.

### Debugging only at the source level

When the real bug is in emitted Wasm, AST-level debugging is not enough. You need to inspect the binary or a readable disassembly.

## How to read projects like this

When you open a JS-to-Wasm compiler report, read in this order:

1. **What subset is supported?**
2. **How are functions and control flow represented?**
3. **How are closures represented?**
4. **What lives in locals vs linear memory?**
5. **How is Wasm emitted and validated?**
6. **What tools exist to inspect the output?**

If the report is fuzzy on those six questions, the architecture is probably fuzzy too.

## Where to go deeper

- [[PROJ - Generic Agent - Principled Compiler Experiment]] — direct emitter, closures, boxing, type propagation, tool-building loop
- [[PROJ - GPT Base Principles Compiler Experiment - Principles-Guided JS to Wasm Compiler]] — same domain with stronger emphasis on iterative architecture growth and fixtures
- [[On-Ramp/what-is-a-stack-based-vm]] — useful contrast: some compiler targets are stack machines, but Wasm emission also forces you to think about structured control and typed stacks
- [[On-Ramp/wasm-from-go]] — useful if you want to contrast “compile a language to Wasm” with “compile Go itself to Wasm” as two very different workflows
