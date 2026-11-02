---
title: "Engineering CAD from First Principles — Chapter 16. Rust, WebAssembly and resource ownership"
aliases:
  - "Chapter 16. Rust, WebAssembly and resource ownership"
tags:
  - course
  - cad
  - textbook
  - jigcad
status: active
type: course
created: 2026-11-02
course: "[[Course - Engineering CAD from First Principles]]"
---

# Chapter 16. Rust, WebAssembly and resource ownership

[[Engineering CAD 15 - A parametric CAD compiler|← Chapter 15. A parametric CAD compiler]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 17 - Verification, differential tests and fuzzing|Chapter 17. Verification, differential tests and fuzzing →]]

JigCAD already executes its numerical solver in WebAssembly, while OpenCascade's C++ geometry kernel runs as a separate WASM module. This chapter explains what that architecture guarantees, where its performance costs arise, and how to design a reusable Rust API without confusing FFI memory safety with geometric correctness.

## 16.1 Two different WebAssembly responsibilities

The browser's JavaScript layer constructs sketches, feature graphs, selectors and UI state. The Rust module `jig-compute` performs numerical algorithms: tape evaluation, reverse-mode Jacobians, matrix calculations, constrained solving, mesh gap checks, orientation metrics, sections and portions of rendering. A separate WebAssembly instance contains the OpenCascade geometry algorithms.

This is not “one Rust CAD kernel compiled to WASM.” The geometric B-rep functionality is still C++ OpenCascade; Rust provides numeric acceleration and an increasingly independent mathematical subsystem.

## 16.2 The linear-memory model

A WebAssembly module can export a **linear memory**, conceptually a mutable byte array indexed by addresses. Passing a JavaScript `Float64Array` to a Rust function generally involves arranging the values in the module's memory, passing a pointer and length, invoking a function, then reading results back.

Jig uses a plain C ABI with functions such as `jc_alloc`, `jc_free`, `jc_result_ptr` and numerical operation functions. JavaScript serializes arrays into WASM memory and decodes results. This avoids higher-level bindings but makes the memory contract explicit: element type, alignment, ownership, lifetime and error semantics must be correct.

WebAssembly memory can grow. After growth, a JavaScript typed-array view backed by a previous memory buffer may become invalid or detached depending on the memory and embedding behavior. A safe bridge recreates views after calls that may allocate or grow memory. Jig's loader documents and follows this practice.

%%FIG:16%%

## 16.3 Handles and generation counters

Large mesh or tape objects should not cross the ABI as copied arrays on every operation. Instead, create an object inside Rust, return an opaque handle, and perform several operations using the handle.

A naive integer handle can create a **use-after-free by identity reuse**: handle `7` is freed, a new object occupies slot 7, and stale JavaScript code accidentally uses it. Generation-tagged handles avoid this by combining the slot index with a generation counter. A stale handle then fails validation rather than referring to a different object.

Jig's mesh and tape registries use generation-tagged handles. The surrounding JavaScript still has to release them. A leak in either WASM instance accumulates memory across repeated compiles, and a finalizer is not a substitute for explicit lifecycle tests.

## 16.4 Error boundaries and fallbacks

Jig's Rust module is loaded with an ABI version check. If the Rust module is not available, the engine can fall back to its JavaScript numeric implementation. A WebAssembly trap disables the Rust path rather than trusting potentially corrupted module state.

This is good engineering, but a fallback must not silently change numerical semantics. The Rust path uses analytic program derivatives; the JavaScript fallback uses finite differences. They may disagree near degeneracies. The application should report which backend ran and include it in diagnostics and regression tests.

**Try it.** [The WASM memory bench](lab:sketch?id=wasm) models allocation, handle reuse and generation checking. It illustrates the ownership invariant; it is not a live inspection of Jig's runtime memory.

## 16.5 Performance is an end-to-end question

For a computation with JavaScript-to-WASM transfers, a simple timing model is

$$
T_{total}=T_{marshal}+T_{compute}+T_{copy\_back}+T_{schedule}.
$$

Moving a tiny dot product into Rust may be slower than executing JavaScript because the call and copying overhead dominate. Performing a dense factorization or many triangle operations per call may be faster because most work stays within WASM.

Benchmark cold loading separately from warm steady-state computation. Also measure 50–100 repeated recompiles, peak and retained WASM memory, typed-array allocations, and time spent serializing large meshes between worker and UI threads.

## 16.6 Packaging a native Rust solver

Jig's current `jig-compute` is a Rust crate that exports a WASM-oriented C ABI. A reusable numerical package would separate three layers:

```text
jig-math       pure Rust residuals, AD, QR, nonlinear solving, tests
jig-ffi        C ABI and handle registry
jig-web        JavaScript loading, typed-array marshalling, worker RPC
```

The pure Rust layer can expose idiomatic functions with borrowed slices, explicit error types, and testable deterministic behavior. The WASM layer manages pointers and resource lifetimes. This separation makes native testing and benchmarking easier and prevents browser-specific policies from leaking into core numerical algorithms.

A later design could also expose more OpenCascade operations through a uniform typed interface. But wrapping C++ classes as if they were ordinary Rust values without a careful ownership model would create more problems than it solves.

> **Exercise.** Design an opaque handle containing a 16-bit slot and a 16-bit generation number. What happens on generation overflow? State the invariant you need to prevent stale references from becoming valid again.

> **Careful.** Memory safety and WASM sandboxing do not imply correct geometry or correct constraint solving. A memory-safe program can reliably compute the wrong result.

## Toward a reusable API

```text
JigMath.solve(problem, initial, options) -> Result<SolveReport, Error>
AbiVersion { major, minor }
Handle { slot, generation }
WasmBuffer { pointer, byteLength, ownership }
BackendStatus { rustWasm | jsFallback, version, reason }
```

## Key points

JigCAD uses two WASM modules for different tasks. Its Rust module is a real numerical backend, not simply a browser wrapper. ABI correctness requires explicit ownership, alignment, memory growth handling and stale-handle checks. Numerical parity must be tested because the Rust and JavaScript derivative paths differ. Packaging pure Rust core functionality separately would strengthen reuse and native validation.

## Further reading

- [WebAssembly Core Specification](https://www.w3.org/TR/wasm-core/) defines linear memory, modules and execution.
- [JigCAD Rust/WASM bridge](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/rs/wasm.js) shows the actual ABI handling.
- [JigCAD Rust numerical crate](https://github.com/go-go-golems/jig/blob/main/import/jigcad/rust/jig-compute/src/lib.rs) contains the exported entrypoints.
- [JigCAD parity tests](https://github.com/go-go-golems/jig/blob/main/import/jigcad/test/rs/parity.mjs) compare the two backends.

---

[[Engineering CAD 15 - A parametric CAD compiler|← Chapter 15. A parametric CAD compiler]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 17 - Verification, differential tests and fuzzing|Chapter 17. Verification, differential tests and fuzzing →]]
