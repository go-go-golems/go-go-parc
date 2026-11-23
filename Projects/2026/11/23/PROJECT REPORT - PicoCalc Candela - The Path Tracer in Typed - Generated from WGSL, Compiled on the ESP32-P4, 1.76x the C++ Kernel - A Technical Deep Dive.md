---
title: "Candela in Typed: the path tracer generated from WGSL, compiled on the ESP32-P4, at 1.76× the C++ kernel's cycles"
aliases:
  - PicoCalc Typed-first, milestone 3
  - PICOCALC-CANDELA-TYPED
tags: [project, compiler, picocalc, path-tracing, riscv, measurement]
type: project
status: active
created: 2026-11-23
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
ticket: PICOCALC-CANDELA-TYPED
source_revision: 46f57c0
---

# Candela in Typed

Candela is a physically based path tracer. On the PicoCalc's ESP32-P4 it renders an 18-scene gallery. Until this ticket, every pixel came from C++. A generator translated Candela's WGSL kernel into `cdl_kernel.cpp`, which GCC compiled into the firmware, and each scene's own code ran as bytecode in a small section interpreter. The project's stated goal is the opposite arrangement: application and compute code written in Typed and compiled to RV32 on the handheld, with C kept only where it cannot be avoided or as a benchmark.

PICOCALC-CANDELA-TYPED applied the goal to the largest workload in the repository. A new generator turns the same WGSL into Typed. The handheld compiles that Typed program, about 10,000 lines, into a 788 KB native module and draws all 18 scenes with it. The C++ kernel stays in the firmware as the yardstick. This report describes how the generator maps WGSL onto a language without vectors, local structs or `continue`, how the result was checked at three levels, and what the device measured. Typed needs 1.76 times the C++ kernel's cycles per sample, and it is faster than C++ on the three scenes whose time the C++ arm spends in its interpreter.

> [!summary]
> - **One generated program for the whole gallery.** The kernel and all 18 scenes' code become one Typed program of 372 KB. It is committed, regenerated and checked by `make test`, and compiled once to serve every scene and both colour modes.
> - **Correct at three levels.**
>   - All 18 scenes are within an image-error bound fixed before measuring (worst: 4.3 × 10⁻⁴ relative), and 7 are bit-identical to the C++ kernel.
>   - The WebAssembly and RV32 builds agree on every float of every pixel over 4 passes.
>   - On the device, all 18 scenes reproduce the workstation's digests.
> - **Speed on the P4.** Typed takes 0.81–2.79 times the C++ kernel's cycles per sample (geometric mean 1.76). It wins where C++ interprets scene code and loses about 2.5× where the time is in the fixed kernel.
> - **Not yet a boot app.** Compiling the program on the handheld takes 85 s and 16.3 MB of QuickJS heap. The Typed arm is a separate firmware profile until compiled images can be cached.

## 1. Where Candela's code ran before

Candela's kernel is written in WGSL, the WebGPU shading language. On the P4 it ran as two pieces:

| Part | What it does | Implementation before |
|---|---|---|
| Fixed kernel | camera rays, sphere tracing of signed distance fields, BSDF sampling (GGX microfacets), sky, spectral sampling, path loop | `cdl_kernel.cpp`, generated from the WGSL by regular expressions that rely on C++ operator overloading; compiled by GCC -O2 |
| Scene sections | each scene's distance field, materials and lights | WGSL translated to a compact bytecode, run by `cdl_vm` |
| Renderer core | passes over the image, accumulation, the display pass (tone mapping), digests | C, `nucleus/candela_gallery.c` |

The gallery app draws a scene and records three digests per scene: the first frame, the accumulation buffer after 4 passes, and the displayed image. `bench/board/gallery.py` compares them with a reference file, and that comparison has been the gallery's regression check since it was built.

The work became possible on 22 November, when Typed gained `f32`, bitwise operators and a math library (PICOCALC-TYPED-F32 and PICOCALC-TYPED-BITWISE, described in the previous report).

## 2. The generator

The generator, `tools/gen/candela/kernel-typed.mjs` and its modules under `tools/gen/candela/typed/`, reads the WGSL rather than the generated C++, whose meaning depends on operator overloads. Candela's existing section translator could not be reused either: it rejects loops, arrays and module-level state, all of which the kernel uses. So the generator has its own parser for the kernel's subset of WGSL. Lowering is typed: every expression has a WGSL type, and the generator stops on anything it does not lower. Examples are unsigned comparison or division, and converting a `u32` that may exceed 2³¹.

Typed is smaller than WGSL in several ways, and each one became a rule in the generator:

| WGSL has | Typed lacks it, so the generator |
|---|---|
| `vec3<f32>` values | uses scalar components everywhere: locals `p__x, p__y, p__z`, three parameters, record fields `P__x`. A vector *result* returns its first component and leaves the others in fields `r1..r3` of the kernel record, which the caller reads in the next statements. |
| local structs | gives each function one static *frame record* holding a reference to one record per struct local or temporary. WGSL has no recursion, so one frame per function is enough. |
| `continue` | folds it into the following statements, or uses a one-shot inner loop with a break flag |
| `a ? b : c`, `select` | uses if/else into temporaries; a lazy `select` puts each argument's statements in its own branch |
| `u32` | uses `i32` with `>>>`; unsigned comparison and division are refused |
| local arrays | uses buffers, with `Math.bitsOf`/`fromBits` for integer elements |
| more than 8 float parameters | passes the extra parameters through the callee's frame record |

The math follows the C++ arm operation for operation, because the C++ arm is the comparison. Its CPU substitutions are transcribed into Typed:
- `floor` and `fract` through integer conversion;
- a degree-9 sine and a degree-6 exponential;
- the pcg3d hashes;
- a 64 × 64 sky table.

Where the C++ calls newlib (`acos`, `atan2`, `log`, `pow`, `tan`, `asin`, `exp2`, `log2`), the Typed program calls the Typed math library instead. The generated sine, as it appears in `kernel.typed`:

```js
function q_sin(a: f32): f32 {
    const k: f32 = q_floor(a * 0.15915494 + 0.5);
    let x: f32 = a - k * 6.2831855;
    if (x > 1.5707963) { x = 3.1415927 - x; } else { if (x < (-1.5707963)) { x = (-3.1415927) - x; } }
    const x2: f32 = x * x;
    return x * (1.0 + x2 * ((-0.16666667) + x2 * (0.008333331 + x2 * ((-0.00019840874) + x2 * 0.0000027525562))));
}
```

Neither side fuses multiply-adds: Typed never does, and the C++ arm is built with `-ffp-contract=off`. A scene that calls none of the newlib functions therefore renders bit for bit as the C++ arm does. Seven of the 18 scenes are like that.

**One program for the gallery.** The kernel and the code of all 18 scenes form a single Typed program: about 10,000 lines in `types.typed`, `kernel.typed`, `scenes.typed` and `glue.typed`, 372 KB of source and 403 KB of RV32 under the `kernel` policy. The five functions the kernel calls in scene code dispatch on a scene index through a binary tree, and the spectral mode is a field rather than a per-scene constant. So one compile serves every scene. Per-scene programs would avoid the dispatch, but would need a compile on every scene change.

The program talks to the C renderer core through four entry points:
- `cdlLayout` describes the memory arena the C side must provide;
- `cdlInit` fills the GGX table;
- `cdlSky` builds the sky table;
- `cdlRenderSpan` writes 12 floats per pixel for a span of a row.

The generated files are committed. `regenerate.mjs --check` in `make test` fails if they differ from what the generator writes.

**Two compiler changes were needed.** After inlining, two kernel functions (`tracePath` and `sampleLobe`) have about 600 locals. Their stack frames exceed the 12-bit offsets RV32 load and store instructions can reach from `sp`, so the backend now uses `s0` as a second frame base for large frames. The WebAssembly backend's source-length limit and memory size became options. Both changes left every pinned image digest unchanged.

## 3. Checking it

The check ran at three levels, each stronger than the last.

**Against the C++ kernel (image error).** The bound was fixed before any measurement: E_rel ≤ 0.02 per scene, where E_rel is the summed per-pixel absolute error of the 4-pass mean colour divided by the summed C++ colour. All 18 scenes are within it. The largest errors are:

| Scene | E_rel |
|---|---:|
| R-04 | 4.3 × 10⁻⁴ |
| G-03 | 2.0 × 10⁻⁴ |
| V-03 | 3.4 × 10⁻⁵ |
| the other 15 | ≤ 10⁻⁷ (7 bit-identical) |

The differences come from the Typed math library standing in for newlib in scenes that use `pow`, `atan2` and the like.

**WebAssembly against RV32 (bit identity).** The Typed program was compiled to WebAssembly and run in Node, and compiled to RV32 under the `kernel` policy and run on the project's reference RV32 interpreter. For every scene, every float of every pixel over 4 passes was compared. All 18 scenes are identical. The interpreter is slow: the heaviest scene, G-03, took about two hours.

**The device against the workstation (digests).** On the P4, the gallery drew all 18 scenes with the Typed arm. Their first-frame, accumulation and display digests equal the workstation's. The C++ arm, still in the same firmware, also matched its own reference on all 18.

Two scenes, F-01 and G-02, first appeared to differ, in the display digest only. The cause was the reference, not the device. The display pass's tone mapping calls the C library's math functions, and the workstation reference had run that pass on x86-64 with glibc. The device uses newlib, and the two libraries round some results differently. One fact pointed at the reference: G-02's accumulation buffers are bit-identical between the arms, so their displayed images must be too, and on the device they were. The reference is now built the same way as the C++ arm's. The display pass is compiled for RV32 with ESP-IDF's toolchain and newlib, then run in an RV32 interpreter, and it reproduces the device's digests exactly.

## 4. Speed on the P4

A paired board study ran 18 scenes × 2 arms × 4 blocks, alternating which arm goes first in each block, at 4 passes of 160 × 160 pixels. The table shows medians, sorted by ratio; per-block ranges were tight (B-01: 2.49–2.51).

| Scene | Typed cycles/sample | C++ cycles/sample | Typed / C++ | Typed s/pass | C++ s/pass |
|---|---:|---:|---:|---:|---:|
| V-02 | 76,564 | 27,480 | 2.79 | 5.45 | 1.95 |
| R-01 | 54,131 | 20,089 | 2.70 | 3.85 | 1.43 |
| L-03 | 26,240 | 10,455 | 2.51 | 1.87 | 0.74 |
| B-01 | 32,434 | 13,022 | 2.49 | 2.31 | 0.93 |
| W-02 | 75,778 | 30,458 | 2.49 | 5.39 | 2.17 |
| F-01 | 37,382 | 15,178 | 2.46 | 2.66 | 1.08 |
| G-01 | 50,466 | 20,709 | 2.44 | 3.59 | 1.47 |
| R-05 | 80,239 | 35,664 | 2.24 | 1.43 | 0.63 |
| E-02 | 19,711 | 10,207 | 1.93 | 1.40 | 0.73 |
| S-02 | 90,837 | 50,122 | 1.81 | 1.62 | 0.89 |
| G-02 | 61,534 | 37,042 | 1.66 | 4.38 | 2.63 |
| V-03 | 145,830 | 92,807 | 1.57 | 2.59 | 1.65 |
| V-04 | 267,695 | 177,161 | 1.51 | 4.76 | 3.15 |
| G-03 | 1,866,066 | 1,329,444 | 1.40 | 33.18 | 23.64 |
| R-04 | 1,472,683 | 1,127,424 | 1.30 | 26.18 | 20.04 |
| X-03 | 744,668 | 750,979 | 0.99 | 13.24 | 13.35 |
| X-04 | 62,459 | 73,300 | 0.85 | 1.11 | 1.30 |
| R-08 | 180,198 | 221,465 | 0.81 | 3.20 | 3.94 |

Geometric mean of the ratios: **1.76**.

The ratios split cleanly by where a scene spends its time.

- **Typed wins where C++ interprets.** X-03, X-04 and R-08 spend most of their samples in scene code: distance fields and materials. The C++ arm runs that code in the section bytecode interpreter, and the Typed arm runs it as native RV32. Native Typed beats interpreted bytecode even though the C++ kernel around it is better compiled.
- **Typed loses about 2.5× where the fixed kernel dominates.** B-01, R-01, L-03 and V-02 have simple scene code, so the time is in the kernel's path loop and BSDF sampling, where GCC's code is much better than Typed's.

The likely causes are visible in the generated code. Struct values live in static frame records in memory instead of registers. Every vector result goes through the kernel record's `r1..r3` fields. Inlining inflates frames to hundreds of locals. These causes are not yet proven by a profile. The earlier fragment measurements, where Typed was within 1.17–1.33× of GCC on single functions, show that the code generator is close on small, register-resident code. The gap is in how the generated program uses memory.

## 5. The cost of compiling on the device

Compiling the program on the handheld:

| Measure | Value |
|---|---|
| Compile time | 84.8 s (at priority 1; 172 s at idle priority) |
| QuickJS heap peak | 16.3 MB |
| Native module | 788 KB |
| Relocation | 59 ms |

The first device run did not get this far. The compile finished, but relocating the module panicked:

```
assert failed: ... cache_utils.c:152 (esp_task_stack_is_sane_cache_disabled())
```

The relocation writes flash-cache-sensitive memory and briefly disables the cache. The task doing it ran on a stack in PSRAM, which cannot be accessed while the cache is off. The fix runs the relocation on a small task with an internal-RAM stack.

A second problem was the watchdog. An 85 s compile on core 0 starves that core's idle task, and the task watchdog fired. Running the compile at idle priority avoided the watchdog but doubled the time, because the compile then shared core 0 round-robin with the idle task. The final arrangement compiles at priority 1 and takes core 0's idle task off the watchdog for the duration of the compile, restoring the configured settings afterwards.

The panic also had a side effect. The keyboard controller, an STM32 on I2C, stopped answering after the panic (every transfer NACKed) until a person power-cycled the handheld; the same hang had followed earlier resets of the ESP32 alone. Board work stopped until then. It is now an explicit rule for the project's agents: after a panic that leaves the bus NACKing, stop and ask.

Every boot app still compiled within 75 % of its deadline on the experimental image. Chess took 4.19 s of 6 s and its painter 5.75 s of 8 s. An 85-second compile, though, cannot happen at every boot. Until compiled images can be cached in flash, keyed by the source digest, the compiler digest and the policy, the Typed arm stays in a separate `candela-typed` firmware profile. The playable firmware's gallery draws with the C++ kernel.

## 6. What this taught

- **Generate from the source language, not from another generator's output.** The WGSL has the types the lowering needs, and the C++ had operator overloads that hid them.
- **Fix the comparison bound before measuring.** E_rel ≤ 0.02 was written down first. Without it, a 4 × 10⁻⁴ error could have been argued either way.
- **A reference must use the device's libraries.** The two false mismatches came from running the display pass with glibc instead of newlib. One fact identified the culprit: two arms with bit-identical accumulation buffers must display identically.
- **The split in the speed table is a map for compiler work.** Native Typed already beats interpreted scene code. The fixed kernel shows what the compiler must learn next: keep struct and vector values in registers instead of static frames, return several results, and stop inlining from multiplying locals.
- **Language gaps cost speed as well as convenience.** Each workaround in Section 2 adds memory traffic: static frames for local structs, the `r1..r3` fields for vector results, buffers for arrays.

## 7. What comes next

- **A compiled-image cache in flash.** This is the prerequisite for making the Typed arm the gallery's default (milestone 5), and it would also shorten every boot (see the OS report).
- **Compiler work aimed at the fixed kernel:**
  - local records and arrays;
  - multiple results;
  - more than 8 parameters per register class;
  - `continue`;
  - a conditional expression;
  - `u32`;
  - range analyses for f32 functions;
  - controlling local growth under inlining.

  This study's table is the baseline each change is measured against.
- **The renderer core in Typed:** passes, accumulation, display and digests are still C.
- **The device compile itself:** 85 s and 16 MB for 372 KB of source. The program's size makes it a useful benchmark for the compiler's own speed.

## Related notes

- [[PROJECT REPORT - PicoCalc Compiler - Floats in Typed - RV32F Semantics Captured on the ESP32-P4, Three Conformant Executors and f32 Within 1.33x of GCC - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc Compiler - One Tape, a Target-Neutral Front End, Declared Passes and Register Classes - Refactoring the Typed Compiler for Floats - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc OS - App Manifests, One Typed-World Path and No App-Specific C - Restructuring the Operating System Around Typed Applications - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc Candela - The Fixed Path-Tracing Kernel as Firmware C++, Measured on the ESP32-P4 - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc Candela - Scene Code as Verified Bytecode in the Fixed Kernel - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc Candela - Eighteen Path-Traced Scenes on the Handheld's Own Screen - A Technical Deep Dive]]
- Ticket: `ttmp/2026/11/22/PICOCALC-CANDELA-TYPED--*` (design doc with Refinements, diary steps 1–4, raw board data in `various/device-6c7e2ca0/`); generator `tools/gen/candela/kernel-typed.mjs`; generated program `apps/typed/candela-gallery/`.
