---
title: "Value types in a streaming compiler: scalar replacement without a syntax tree, and Candela's kernel from 1.76× to 1.46× C++"
aliases:
  - PicoCalc Typed-next, report 2
  - PICOCALC-TYPED-VALUES and PICOCALC-CANDELA-KERNEL-CODEGEN
tags: [project, compiler, picocalc, riscv, floating-point, measurement]
type: project
status: active
created: 2026-11-23
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
ticket: PICOCALC-TYPED-NEXT
source_revision: 80b8bb0
---

# Value types in a streaming compiler

Typed is the typed subset of JavaScript that the PicoCalc compiles to RV32 on the handheld. A day before this work, a generator had translated Candela's path-tracing kernel from WGSL into Typed. The result ran on the ESP32-P4 at 1.76 times the C++ kernel's cycles per sample, and at 2.5–2.8 times on scenes where the time goes to the fixed kernel rather than to scene code.

The generator's own notes said where much of that came from. Typed had no way to hold a vector or a struct as a value. Every `vec3` result came back as one float plus two fields stored in memory, and every struct lived in a static record reached through two pointers.

This report covers two tickets.
- **PICOCALC-TYPED-VALUES** added value records, record results, local arrays, `continue`, the conditional expression, `u32` and stack parameters to Typed, on both of its targets. The constraint was a compiler that streams one function at a time and builds no syntax tree.
- **PICOCALC-CANDELA-KERNEL-CODEGEN** regenerated Candela with them, profiled the result, changed the compiler where the profile pointed, and measured on the device.

> [!summary]
> - **Value records are scalar-replaced by the front end as it parses.** A `Vec3` becomes three locals, a `Vec3` parameter three parameters, and a `Vec3` result three results. No pass and no backend ever sees a record value.
> - **The language change alone made the kernel slower** (B-01: 10,279 → 11,464 instructions per sample). The values had moved from the heap into the stack frame. A profile showed that float arithmetic was under 7 % of the instructions; the rest was frame traffic, register moves and the address arithmetic of row reads.
> - **Compiler work aimed at that profile** brought the kernel-bound scenes from 1.89× to 1.41× C++ in host instructions. On the P4 they went from 2.59× to 2.03× in cycles, and all 18 scenes from 1.76× to 1.46×.
> - **The host overstates the gain.** Instruction counts on the workstation do not predict P4 cycles for this code. The hypothesis is that the remaining stack traffic and code fetches go to PSRAM; it has not been tested yet.

## 1. The constraint: no syntax tree

The Typed compiler runs at boot inside QuickJS on a 360 MHz core, under a few megabytes of heap. It is built around two properties that the earlier reports explain:

- **It streams.** Each function is parsed, lowered to RV32 and freed before the next one is read, so memory is bounded by the largest function, not the program.
- **It has no syntax tree.** The parser checks types while it parses and writes operations directly into the *tape*, the compiler's intermediate representation: a flat array of WebAssembly opcodes with operand cells.

Any new language feature has to fit these. In particular, a feature cannot be implemented by building a tree and rewriting it later.

## 2. Value records as scalar replacement

Typed already had `record`, but a record there means a reference to memory that the host lays out: the world's state, or a structure in a shared buffer. A value needs different semantics. It is copied on assignment, has no address and never aliases. The ticket therefore added a distinct declaration:

```js
value record Vec3 { x: f32; y: f32; z: f32; }
function add(a: Vec3, b: Vec3): Vec3 { return Vec3(a.x + b.x, a.y + b.y, a.z + b.z); }
function dot(a: Vec3, b: Vec3): f32 { return a.x * b.x + a.y * b.y + a.z * b.z; }
function normalize(a: Vec3): Vec3 {
    const l = Math.sqrt(dot(a, a));
    return l > 0.0 ? scale(a, 1.0 / l) : a;
}
```

The front end lowers every value record into its *leaves*, the scalar fields at the bottom of any nesting, at the moment it parses them:

| Source | Becomes |
|---|---|
| `const v = Vec3(1.0, 2.0, 3.0)` | three locals `v.x`, `v.y`, `v.z`, set from three operand-stack values |
| `v.y` | a read of the local `v.y` |
| `w = v` | three local-to-local copies |
| a `Vec3` parameter | three consecutive parameters |
| a `Vec3` result | three results |

Records nest. A `Hit` holding three `Vec3`s, a `Vec2`, integers and booleans has 21 leaves, and a function returning a `Hit` returns 21 values.

Because the replacement happens during parsing, none of the backend changes. The tape after the front end contains only scalar locals, scalar parameters and multiple results. Every existing pass, from inlining to range analysis, works on value records without knowing they exist. The cost moves to calling conventions, which must carry many values.

**Positional construction.** The constructor `Vec3(a, b, c)` is positional, as in WGSL. An object-literal form would need the expected type to be known while the literal is parsed, which a parser that does not look ahead cannot always provide.

## 3. Many parameters and many results

Scalar replacement multiplies parameters and results, so the calling convention had to grow.

**More than eight parameters per register class.** RISC-V's `ilp32f` convention passes up to eight integer arguments in `a0–a7` and eight floats in `fa0–fa7`, and the rest on the stack. Typed now implements the stack part exactly:
- The caller reserves a stack-argument area at the bottom of its frame.
- The callee copies its stack words in its prologue, addressed from the caller's stack pointer through one patched `addi`.

**Record results.** WebAssembly 2.0 allows a function to return several values, so the WebAssembly target uses multi-value results directly. On RV32 there is no standard convention for 21 results. Typed returns integer leaves in `a0–a7` and float leaves in `fa0–fa7`, and anything beyond eight per class in the caller's stack-argument area. A single result still uses `a0` or `fa0`, so every existing world's interface is unchanged.

Every pass that models the abstract operand stack had to learn that a call can push more than one value, through a new `arity.results`. The inliner handles callees with record results by writing their leaves into result locals.

## 4. The smaller features

- **`continue`.** A body that contains `continue` gets a block around it, and `continue` branches to that block's end, so the loop's update and condition still run. This also holds after the `rotate` pass moves a loop's condition to the bottom. The front end finds the word by scanning the body's text before parsing it, a consequence of having no tree to inspect afterwards.
- **`c ? a : b`.** Lowered to `if (result T) … else … end` on the tape. Both arms must have one type, and a literal takes the other arm's integer type.
- **`u32`.**
  - An i32 on the tape whose comparisons, division and remainder are unsigned (`sltu`, `bltu`/`bgeu`, `divu`/`remu`, or a shift or mask for a power of two).
  - `>>` on a `u32` is an error that points to `>>>`. Conversions are explicit.
  - `u32(x)` of a float saturates, and NaN gives 2³² − 1.
  - A decimal literal from 2³¹ to 2³² − 1 is a `u32`.
- **Local arrays.** `new Float32Array(16)`, `Int32Array` or `Uint32Array`, with a literal length from 1 to 1024, zeroed at the declaration.
  - Indexing is bounds-checked with one unsigned comparison.
  - The check is dropped for a literal index (checked at compile time), and for the counter of a counted loop whose body never writes it. The front end proves the latter, so no policy needs range analysis for it.
  - On RV32 arrays live in the stack frame. On WebAssembly each function gets a static area at the top of memory, which is exact because Typed's call graph is acyclic.

**Checks.**
- Every feature has differential tests: WebAssembly, RV32 under all five policies, and a JavaScript model. 87 compiler tests pass.
- The 84 pinned images of programs that use none of the features are byte-identical.
- The handheld's C tokenizer, which the device uses instead of the JavaScript lexer, agrees with the lexer on all 10 test sources.
- On the device, every boot app still compiled within 75 % of its deadline. Chess went from 69.8 % to 72.6 %, because the front end does a little more work per token.

A small example of what value records buy: a 100-iteration loop of `Vec3` additions and cross products takes 3,020 instructions under the `default` policy, against 5,124 with the memory-record workaround, and `add(Vec3, Vec3)` compiles to a frameless leaf of three `fadd.s`, three moves and `ret`.

## 5. Regenerating Candela, and why it got slower first

The generator was rewritten to use the new features:
- value records `V2f`, `V3f`, `V4f`, `V2i` plus one per WGSL struct;
- record results in place of the result fields;
- native `continue`, `?:` and `u32`;
- local arrays.

A new step passes each callee only the leaves of an aggregate it actually reads. The generated program shrank from 372 KB to 302 KB, and its images were bit-identical to the old generator's.

It also ran **slower**: B-01 went from 10,279 to 11,464 instructions per sample. Scalar replacement had moved the values from records in the heap to locals, and locals that do not fit in registers live in the stack frame. Without the right optimizations, the same traffic simply moved from one kind of memory to another.

## 6. What the profile showed

Before changing the compiler, the ticket profiled B-01 on the step-1 build, per function and per instruction class.

| Instruction class (B-01, per sample) | Count |
|---|---:|
| frame loads | ~1,500 |
| frame stores | ~1,500 |
| `fmv.s` (float register copies) | 1,045 |
| `fmv.x` (float ↔ integer moves) | 522 |
| float arithmetic | < 7 % of all instructions |

Three patterns produced most of it:
1. **Row reads.** Each `getF32` on one of the kernel's row buffers cost about 8 extra instructions for its address and range check, and the output routine read four in a row.
2. **Copies of record leaves** went through frame slots.
3. **Unused float registers.** Calling functions left `fa1–fa7`, `ft8` and `ft9` unused, so values that could have stayed in registers went to frame slots. The change that followed gives float values those registers in functions that make no calls.

The design had guessed the remaining cost was "memory". The profile made that precise: it was the frame, not the heap arena.

## 7. Compiler changes aimed at the profile

All of these apply only to functions with float values under the `kernel` policy, so every integer program stayed byte-identical (84 of 84) after every commit.

| Change | B-01 / R-01 / V-02 instructions per sample |
|---|---|
| step-1 build | 11,247 / 21,294 / 33,017 |
| `rows`: one range check and one base address per row, and `coalesce`: copies between float locals removed | 9,248 / 16,664 / 26,333 |
| float registers in call-free functions, open inlining of record results, set–get forwarding | 8,641 / 15,369 / 24,560 |
| result leaves written straight into the locals that store them | 8,451 / 15,073 / 24,011 |
| `rows` grouping reads by affine index and by record-field buffer | 8,041 / 13,705 / 22,183 |

An inlining budget of 400 locals per caller keeps scalar replacement from multiplying locals without bound. Before it, two kernel functions reached about 600 locals. The deepest stack fell from 9,120 to 6,288 bytes.

The ticket also found a memory bug on the device. The RV32 backend kept every function's *emitter*, its location plan, intervals and tables, until final assembly, which needs only the instruction words, calls and descriptor. For the 302 KB Candela program, the device compile peaked at 17.8 MB and failed, and running worlds crashed for want of PSRAM. Releasing each emitter after lowering brought the host peak from 27.4 to 20.9 MB and the device compile to 13.6 MB, with identical output.

## 8. The device

The paired board study used the baseline's configuration: 18 scenes, 4 blocks with alternating arm order, 4 passes at 160 × 160. All 144 digests matched the references, and block-to-block spread was about ±1 %.

| Scene | Before (Typed / C++) | After |
|---|---:|---:|
| B-01 | 2.49 | 2.06 |
| R-01 | 2.70 | 1.97 |
| L-03 | 2.51 | 2.10 |
| V-02 | 2.79 | 2.10 |
| W-02 | 2.49 | 1.95 |
| Kernel-bound geometric mean | 2.593 | 2.034 |
| All 18 scenes, geometric mean | 1.764 | 1.463 |

The Typed kernel's own cycles per sample fell 13–27 % on every scene except X-04 (−1 %), whose time goes to scene code. The targets of ≤ 1.3× overall and ≤ 1.5× on kernel-bound scenes were not reached.

**The host and the device disagree.** On the workstation, the kernel-bound scenes measure 1.41× C++ in instructions. On the P4 they measure 2.03× in cycles. The gap existed before this work too (1.89× on the host against 2.59× on the device). The ticket's hypothesis is that the remaining frame loads and stores hit a stack in PSRAM, because the gallery's worker task stack is allocated there, and that the module's code is fetched from PSRAM as well. C++ pays less for this because GCC keeps more in registers. The hypothesis is cheap to test: run the same module with the worker's stack in internal RAM, or with the code copied to internal RAM, and compare cycles per sample.

## 9. What this taught

- **Scalar replacement belongs in the front end when there is no tree.** Doing it while parsing kept every pass and both backends unchanged. Its cost is confined to the calling convention and the parser.
- **A language feature can make code slower until the compiler uses it.** Value records removed heap traffic and created frame traffic. Only the passes written afterwards turned the change into speed.
- **Profile before optimizing.** The profile showed float arithmetic under 7 % of the instructions. The work that paid was about row addressing, copies and register reservation, none of which the design had named.
- **Host instruction counts are not P4 cycles.** For integer code the two agreed well enough; for this float kernel with a PSRAM stack they do not. Every speed claim for the kernel has to be a board study.

## 10. Open problems

- **The host–device gap.** Test the PSRAM hypothesis: the worker stack and the module in internal RAM.
- **The next profile items:** f32 constants (about 560 instructions per sample on B-01) and callee-saved register saves and restores (about 510).
- **The Wasm inspector** crashes on `0xfc`-prefixed operations (an older bug the ticket found).
- **Language follow-ups:** array accesses still compute their offset separately from the load, and value records cannot yet be used in async functions.
- **Compile time.** The device compile of the Typed Candela program takes about 115 s. The compile cache (the companion report) makes that a one-time cost per firmware, but the front end's speed is the next research problem.

## Related notes

- [[PROJECT REPORT - PicoCalc OS - Booting Without Compiling - A Compiled-Module Cache, What the Compiler Costs on the P4, and a Harness That Stopped Wedging the Keyboard - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc Candela - The Path Tracer in Typed - Generated from WGSL, Compiled on the ESP32-P4, 1.76x the C++ Kernel - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc Compiler - Floats in Typed - RV32F Semantics Captured on the ESP32-P4, Three Conformant Executors and f32 Within 1.33x of GCC - A Technical Deep Dive]]
- Tickets: `ttmp/2026/11/23/PICOCALC-TYPED-VALUES--*`, `PICOCALC-CANDELA-KERNEL-CODEGEN--*` (design Refinements, diary steps 1–8, `various/device-22abf5aa/`); `docs/typed-compiler.md`.
