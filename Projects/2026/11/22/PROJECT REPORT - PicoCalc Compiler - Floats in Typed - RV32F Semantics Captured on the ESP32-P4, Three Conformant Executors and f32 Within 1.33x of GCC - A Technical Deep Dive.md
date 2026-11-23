---
title: "Floats in Typed: RV32F semantics captured on the ESP32-P4, three conformant executors, and f32 within 1.33× of GCC"
aliases:
  - PicoCalc Typed-first, milestone 2
  - PICOCALC-TYPED-F32 and PICOCALC-RV32-CONFORMANCE
tags: [project, compiler, picocalc, riscv, floating-point, measurement]
type: project
status: active
created: 2026-11-22
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
ticket: PICOCALC-TYPED-FIRST
source_revision: 0a227fc
---

# Floats in Typed

Typed is the typed subset of JavaScript that the PicoCalc's operating system compiles to RV32 machine code on the handheld itself. Until 22 November its only numeric type was the 32-bit integer. The project's goal is an operating system written in Typed, and its next large workload is Candela, a path tracer whose kernel is single-precision floating point throughout, so Typed needed floats.

Adding a floating-point type to a compiler raises two questions. The first is semantic: what exactly is `min(NaN, 1)`, or the integer value of `3e9`? Typed has two targets, WebAssembly and RISC-V, and they answer some of these questions differently. The second is about evidence: before generated float code can be trusted, the tools that run it on the workstation have to agree with the real chip, bit for bit, including the flag bits.

This report describes two tickets of the PICOCALC-TYPED-FIRST program that answered them. PICOCALC-RV32-CONFORMANCE captured the ESP32-P4's floating-point behaviour on 15,454 single-instruction vectors and made the project's three RV32 executors agree with it. PICOCALC-TYPED-F32 then added `f32` to Typed end to end. That covers the language, the intermediate representation, the WebAssembly and RV32F backends and a math library written in Typed. On three fragments of Candela's kernel the result runs within 1.17–1.33× of GCC's cycles on the device.

> [!summary]
> - **The board defines the semantics.** An ESP-IDF app executed each of 264 instruction forms on generated inputs on the P4, and the captured results became the reference. The P4's FPU followed the RISC-V F specification in every captured case: canonical NaN `0x7fc00000`, subnormals kept, tininess detected after rounding, saturating conversions.
> - **Three executors, one suite.** The JavaScript reference interpreter, the Go machine of the trace REPL and the C emulator rv32emu now run all of RV32IMF and pass the same 15,664 vectors in `make test`.
> - **Typed follows RV32F where the targets differ.** Float-to-integer conversion saturates, `min`/`max` return the non-NaN operand, and nothing is fused into a multiply-add. Each rule costs at most one instruction on the device, and the WebAssembly backend expands to match.
> - **Floats compete with GCC.** On the P4, Typed's code for three Candela fragments takes 1.33×, 1.26× and 1.17× GCC -O2's cycles, and 1.27×, 1.19× and 1.17× once GCC is also denied fused multiply-add. Integer programs compile 3.4–3.9 % slower on the workstation as a side effect.

## 1. Why the executors came first

The project checks generated code on the workstation before it reaches the device. Three programs execute RV32 there, each for its own reason:

| Executor | Language | Used for |
|---|---|---|
| `bench/emu` (rv32emu) | C | whole-program runs: it loads the firmware ELF and modules as the device's loader does; the 25 historical replays and the Chess oracle |
| `bench/host/rv32-interp.js` | JavaScript | the reference: it runs inside any JavaScript VM next to the compiler and checks the calling convention at every call |
| `pkg/tracerv32` (now `tools/trace-repl/pkg/tracerv32`) | Go | a predecoded twin of the reference, about 1,200 times faster, for instruction counts and profiles |

Before this work none of them decoded floating-point instructions. Each implemented its own subset of the integer ISA. The Go machine was tested against the JavaScript one, and rv32emu against neither. Adding floats to three independent implementations without a shared reference would have produced three slightly different float semantics.

## 2. Capturing the P4's floating-point behaviour

The conformance suite is a file of *vectors*. Each vector holds one instruction word, the input registers (integer and float), memory where relevant, the floating-point control register `fcsr`, and the expected outputs or fault:

```json
{"word": "...", "x": {...}, "f": {...}, "fcsr": 0, "expect": {"x": {...}, "f": {...}, "fcsr": 1}}
```

A generator (`bench/rv32/generate.mjs`) produces inputs per instruction class. The integer cases cover overflow, division by zero and `INT_MIN / -1`, shifts, sign extension and alignment. The float cases cover the five rounding modes, quiet and signaling NaNs, signed zeros, subnormals, values near the conversion limits, `fsqrt.s`, `fdiv.s`, `fclass.s` and the comparison flags.

The expected values for floats come from the chip. `bench/board/rv32-vectors` is an ESP-IDF application with one generated assembly stub per instruction form, 264 in all. Each stub loads the inputs, executes the instruction, and stores the results and `fcsr`. The capture script runs it on the P4 through the project's board library, which checks the installed firmware first and restores and health-checks it afterwards. 15,454 vectors were captured. For integer vectors, the build additionally requires a small model and the board to agree; they agreed on all of them.

The captured behaviour, in the cases most likely to differ between implementations:

- **NaNs.** Every NaN produced by arithmetic is the canonical `0x7fc00000`. Sign injection, moves, `flw` and `fsw` preserve NaN payloads.
- **Subnormals** are kept, not flushed to zero.
- **Tininess** is detected after rounding. A result that rounds up to 2⁻¹²⁶ raises the inexact flag without underflow. Only two vectors sit on this boundary.
- **`fmin`/`fmax`** return the non-NaN operand and raise "invalid" only for a signaling NaN. −0 orders below +0.
- **`fcvt.w.s`** saturates and raises "invalid" alone. A negative value that rounds to 0 gives 0 with "inexact" only.
- **`fmadd.s`** with ∞ × 0 and a quiet-NaN addend raises "invalid".
- **Comparisons:** `feq` raises "invalid" only for signaling NaNs; `flt` and `fle` raise it for any NaN.

The P4 followed the RISC-V F specification in every captured case. That result is useful in itself: the reference semantics for Typed's floats are the specification's, and the device does not need special cases.

All three executors gained RV32F, including every rounding mode and the `fcsr` flags, and pass every vector. `make test` runs the JavaScript reference and rv32emu against the vectors, and the Go machine runs them in `go test`. A mutation check confirms that the suite detects errors: changing one rounding rule fails 33 vectors in the JavaScript implementation and 52 in rv32emu.

Two discoveries along the way. rv32emu had been RV32IMC, not the RV32IMF its Makefile claimed. The reference interpreter and the Go machine had covered only the integer instructions the Typed compiler emitted, so they were extended to all of RV32IM before the integer vectors could pass on all three.

## 3. The language

`f32` is a type and a reserved word. The rules are strict on purpose, matching how Typed treats integers:

```js
function norm3(x: f32, y: f32, z: f32): f32 {
    const len = Math.sqrt(x * x + y * y + z * z);
    if (len > 0.0) { return 1.0 / len; }
    return 0.0;
}
```

- **Literals.** A float literal needs a fraction or an exponent (`1.0`, `2e-3`); `1` stays an `i32`.
- **No implicit mixing.** `f32(i)` converts an integer and `i32(x)` converts a float; adding an `i32` to an `f32` is a type error.
- **Operators:** `+ - * /`, unary minus and the comparisons.
- **`Math` functions:** `sqrt`, `abs`, `floor`, `ceil`, `trunc`, `copysign`, `min`, `max`, plus `bitsOf`/`fromBits` to read and build bit patterns. `Math.round` is not included yet.
- **Storage.** Records can have `f32` fields; each is still one 32-bit word. Buffers, which hold 16-bit cells, gain `getF32(i)` and `setF32(i, x)`: element `i` occupies cells `2i` and `2i + 1`, and the access is bounds-checked like every other buffer access.

The handheld's lexical index, the C code that tokenizes Typed source on the device instead of the JavaScript regular expression, gained a float-literal token. A check on a host QuickJS compares it with the JavaScript lexer and agrees on all seven test sources.

## 4. Where WebAssembly and RISC-V disagree

The WebAssembly build of every program is the oracle for its RV32 build, so every semantic difference must be decided once and implemented on both targets. Typed follows RV32F in every case:

| Case | WebAssembly | RV32F | Typed |
|---|---|---|---|
| `i32(x)` out of range or NaN | `i32.trunc_f32_s` traps | `fcvt.w.s` saturates | saturates; NaN gives 2³¹−1 |
| `min`/`max` with one NaN | NaN | the other operand | the other operand; −0 below +0 |
| Fused multiply-add | none | `fmadd.s` exists | never fused |
| Rounding | round to nearest even | dynamic or static per instruction | nearest even, set statically in each instruction |
| NaN payload and sign | nondeterministic | canonical NaN | unspecified; the tests treat all NaNs as equal |

Three new tape pseudo-operations carry these rules: `0xf4 f32.to_i32`, `0xf5 f32.min_num` and `0xf6 f32.max_num`. On RV32 each is one instruction. On WebAssembly the conversion becomes `i32.trunc_sat_f32_s` plus a select for NaN, and min/max become two NaN selects.

Saturation was chosen over trapping for two reasons. A trapping conversion costs 5–7 extra instructions per site on RV32, and Candela's kernel has 63 conversion sites. And a trap would stop a whole render because of one stray NaN, where saturation degrades a single pixel. The cost comparison was static, counting instructions, not a timed run.

## 5. The RV32F backend

The register work done just before this ticket (PICOCALC-RV32-REGISTERS) gave the backend two register classes: integer `x0`–`x31` and float `f0`–`f31`, encoded as one number with a class bit. On top of that:

- **Operand stacks per class.** The backend keeps the top of the operand stack in registers: `t0`–`t4` for integers, and now `ft0`–`ft7` for floats. At each depth the two classes share one spill slot.
- **Arithmetic, comparisons, sign injection and conversions** use static rounding. `floor`, `ceil` and `trunc` have no RV32F instruction, so each is an 8-word sequence: convert with the right rounding mode, convert back, and keep the original value when |x| ≥ 2²³, where it is already integral.
- **Calls follow `ilp32f`:** float arguments in `fa0`–`fa7`, results in `fa0`, `fs0`–`fs11` saved by the callee. Frameless leaf functions accept float parameters.

Several optimizations apply only to functions that contain a float value. This keeps every integer program's compiled image byte-identical, which was this program's gate for each change:
- such functions are inlined anywhere, not only inside loops;
- a new `fields` pass loads each float field of an unmodified record parameter once;
- float constants get registers;
- leaves may keep values in argument and unused stack registers;
- a returned value is computed directly in `fa0`;
- functions that need no stack frame get none.

## 6. A math library in Typed

Under the project's goal, Typed code does not call C's `libm`. `compiler/typed/lib/math.typed` implements the functions Candela's kernel uses with range reduction and polynomial approximations. Accuracy, in units in the last place (ulp) against a double-precision reference rounded to f32:

| Function | Max error |
|---|---|
| `sinf`, `cosf` on [−π, π] and [−100, 100] | 1 ulp |
| `sinf`, `cosf` on [−8192, 8192] | 33 and 232 ulp near the zeros (absolute error < 7.6e−8) |
| `tanf` | 3 ulp |
| `expf`, `exp2f`, `logf`, `log2f` | 1 ulp |
| `atanf`, `atan2f` | 3 ulp |
| `asinf`, `acosf` | 2 ulp |
| `powf` | 21–48 ulp |

Edge cases (zeros, infinities, NaN, the ends of each range) are within 0–1 ulp. `powf` is the weak entry; a two-part `log2` would fix it. The library also provides `fract`, `mix`, `clamp`, `saturate`, `step`, `sign`, `smoothstep` and `ldexpf`. It declares no records, so a program can prepend it to its own source.

Bit-exactness with C's `libm` is deliberately not a goal. What is required is that the WebAssembly and RV32 builds of the library agree bit for bit, and they do.

## 7. Results

**Correctness.** Differential tests cover generated float expressions, hand-written programs under five policies, and the whole math library. Each runs through WebAssembly in Node, RV32 on the reference interpreter and a JavaScript model. The Go machine runs a fixture of 6,360 further cases. All agree. Every integer program's image is byte-identical to before (84 of 84 digests). `make test` and the host gates pass.

**Instruction counts.** Typed's output for three fragments of Candela's kernel, against GCC 14 for the same functions, counted on the reference interpreter. The fragments are the sphere test from `hitObj`, the GGX microfacet term from `evalLobe`, and a vector normalization.

| Fragment | Typed | GCC -O2 | Ratio | GCC -O2 without fused multiply-add |
|---|---:|---:|---:|---:|
| sphere | 37.97 | 25.45 | 1.49 | 33.45 |
| GGX | 76 | 58 | 1.31 | 66 |
| norm3 | 30 | 23 | 1.30 | 26 |

Before the float-only optimizations of Section 5, the ratios were 2.19, 2.64 and 1.83. Typed's results are bit-identical to GCC's when GCC is built with `-ffp-contract=off`.

**Cycles on the P4.** Medians of 6 blocks with rotated arm order, 2,000 inputs each. Before timing, the board checked every result against the workstation's Typed results; all were bit-exact.

| Fragment | GCC -O2 | GCC without FMA | Typed | Typed / GCC | Typed / GCC without FMA |
|---|---:|---:|---:|---:|---:|
| sphere | 75.1 | 78.9 | 100.0 | 1.33 | 1.27 |
| GGX | 290.0 | 306.0 | 364.0 | 1.26 | 1.19 |
| norm3 | 104.0 | 104.0 | 122.0 | 1.17 | 1.17 |

The gap on the device is smaller than the instruction counts suggest. Floating-point latencies dominate, and most of what remains is GCC's fused multiply-add, which Typed refuses by rule.

**The cost to integer programs.** The compiler grew, and integer programs pay for parsing a larger compiler. One boot compile measured with callgrind in QuickJS on the workstation: Editor +3.4 %, Chess +3.9 %. About 15 million of the extra instructions are QuickJS parsing the bigger bundle; the compile itself costs +1.6–2.1 %. On the device the lexer's regular expression does not run (the C lexical index replaces it), so the device cost should be lower. Chess's boot compile had 0.48 s of margin before its deadline, so the first firmware with floats has to confirm it on the board.

## 8. What this taught

- **Let the hardware define the semantics, then test every tool against it.** Capturing 15,454 vectors on the P4 settled questions that reading specifications leaves open, such as tininess after rounding and NaN payloads through moves, and it found that one emulator implemented a different ISA from the one its build claimed.
- **Choose the target's semantics when one target is the device.** Following RV32F costs nothing on the handheld and a select or two in WebAssembly, which runs only on the workstation.
- **Keep integer output fixed while adding a type.** Gating float-only optimizations on the presence of a float value let the 84-digest gate stay meaningful for this ticket too. The open task is to widen those optimizations to integer code with its own board study.
- **Measure on the device.** Instruction ratios of 1.30–1.49 became cycle ratios of 1.17–1.33.

## 9. What comes next

- **PICOCALC-CANDELA-TYPED** (running) generates Candela's kernel and scene code in Typed from its WGSL, uses this math library, and compares speed and image error with the C++ kernel on the device.
- **F32 follow-ups:**
  - range facts and value sets for functions with float operations;
  - `Math.round`;
  - `f32` in the world interface and in async functions;
  - a better `powf`;
  - argument reduction for `sin`/`cos` beyond about 51,000;
  - a board study of cold compile time.
- **Conformance follow-ups:** misaligned accesses and illegal encodings were not captured; instruction profiles do not yet classify float instructions.

## Related notes

- [[PROJECT REPORT - PicoCalc Compiler - One Tape, a Target-Neutral Front End, Declared Passes and Register Classes - Refactoring the Typed Compiler for Floats - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc OS - App Manifests, One Typed-World Path and No App-Specific C - Restructuring the Operating System Around Typed Applications - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc Candela - The Fixed Path-Tracing Kernel as Firmware C++, Measured on the ESP32-P4 - A Technical Deep Dive]]
- Tickets: `ttmp/2026/11/22/PICOCALC-RV32-CONFORMANCE--*`, `ttmp/2026/11/21/PICOCALC-TYPED-F32--*` (design-doc 02, diary, board capture in `sources/board-2026-11-22/`); guides `docs/rv32-executors.md`, `docs/typed-compiler.md`, `compiler/typed/lib/README.md`.
