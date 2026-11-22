---
title: "When faster code broke the boot: measuring and restoring on-device compile budgets"
aliases:
  - PicoCalc compile budget
  - COMPILE-BUDGET report
tags: [project, compiler, picocalc, quickjs, performance]
type: project
status: active
created: 2026-11-21
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
ticket: PICOCALC-COMPILE-BUDGET
source_revision: cf177af
---

# When faster code broke the boot

The PicoCalc compiles its own applications. At every boot, the ESP32-P4 runs the Typed compiler, written in JavaScript, inside QuickJS, and turns the source of Files, Agenda, Editor and Chess into RISC-V code. Each of these compiles has a wall-clock deadline. During one evening, a series of compiler optimizations made the ray tracer 2.8× faster, and they also made two of these boot compiles miss their deadlines. The handheld then booted without its applications.

This report follows the PICOCALC-COMPILE-BUDGET ticket, in order:

- how the regression got past every gate
- the firmware that measured each application under every optimization level on the device
- the per-application policies chosen from that table
- the bytecode cache that removed a fixed cost of 0.4–0.5 s from every compile
- the reinstallation that nearly lost the 3D Chess board

It continues [[PROJECT REPORT - PicoCalc Compiler - Closing the Typed Ray Tracer's Gap to C - From 5.8x to 2.1x in Measured Steps - A Technical Deep Dive]].

> [!summary]
> - Every optimization step added compile time. Measured from no optimizations to the full default on the P4, Agenda went from 0.86 s to 2.75 s against a 1.7 s deadline, and Editor from 2.82 s to 7.89 s against 6 s.
> - Each application now names a compile policy. Agenda and Editor use `interactive`, which omits inlining and loop transforms. Files and Chess use `default`. The ray tracer uses `kernel`, which adds division facts, at 15.27 ms per frame (1.97× the C version).
> - Before seeing the application, each compile spent 0.41–0.53 s evaluating the compiler's own JavaScript. Caching it as QuickJS bytecode cut that to 0.05 s, with byte-identical output.
> - A host interpreter (goja) understated the growth for large applications by half, because on the device part of the frontend is native code. Only measuring on the device gave the right numbers.

## How the regression got through

PICOCALC-RAY-PARITY qualified each optimization with four gates:

- the host frame, measured in executed instructions
- differential tests against unoptimized code
- 24 host replays of the four applications
- a paired benchmark run on the P4

The board benchmark compiles on the device, but only the ray tracer and a small Chess kernel. The replays compile the applications, but on the host. No gate compiled the boot applications on the device. The host proxy for compile time was goja, the Go JavaScript interpreter behind the project's trace REPL. In goja, Editor's compile grew only 1.6× over the ticket's steps.

The installation of the first firmware with the new default made the problem visible. Its boot log:

```text
agenda compile rejected: InternalError: interrupted
    at inlineCalls (typed/rv32.js:946:29)
agenda compile source=bundle status=failed us=1746878 ...
editor compile rejected: InternalError: interrupted
editor compile source=bundle status=failed us=6101996 ...
E (11206) picocalc-os: the manifest did not load
```

`typed_p4.c` installs a QuickJS interrupt handler that returns true once the deadline passes. The deadline is 1.7 s by default, and 6 s for Editor and Chess. The previous firmware was restored the same evening.

## Why goja misled

Jitless Node, which is also an interpreter, measured Editor at 3.1× and Agenda at 4.6×, close to the device's ratios. The difference is the frontend. On the device, the Typed lexer's index is a native C function (`typed_lex_index_install`). In goja, it is interpreted JavaScript and dominates the large applications' compile time, which dilutes the backend's growth. A proxy that runs a different share of the work natively measures a different program. The workbench therefore gained a proposal for per-phase compile timers, so that a proxy can leave out the phases the device runs natively.

## The measurement firmware

`scripts/01-stage-arms-firmware.py` builds a measurement copy of the everyday firmware. It copies the tracked tree and turns the device's compile entry into a wrapper. For each boot application, the wrapper first compiles the real source once under each "arm": a complete options object, passed as the compile entry's third argument. For each compile it prints:

```text
CCARM {"app":"agenda","round":0,"arm":"step7","status":"ok","us":1690042,"evalUs":410731,"peak":1330436,"bytes":66364,"fnv":"d9cea55b"}
```

The deadlines are lifted to 60 s, so slow arms finish. The heap limits are unchanged, so an arm that runs out of heap fails visibly. The arms are RAY-PARITY's cumulative steps, from `stock` (no optimizations) to `step13` (the full default), each spelled out field by field.

The device measurements were deterministic. Four compiles of the same arm agreed to within 10 ms, and every arm's module digest was identical across rounds and boots. The full table (run 2):

| Application | stock | step6 | step7 | step8 | step11 | step13 | 75% of deadline |
|---|---:|---:|---:|---:|---:|---:|---:|
| Files | 0.52 s | 0.55 | 0.62 | 0.66 | 0.69 | 0.77 | 1.28 |
| Agenda | 0.86 | 1.01 | 1.69 | 1.97 | 2.33 | 2.75 | 1.28 |
| Editor | 2.82 | 3.40 | 5.10 | 5.83 | 6.53 | 7.89 | 4.50 |
| Chess (2D) | 1.64 | 1.98 | 2.93 | 3.14 | 3.49 | 4.34 | 4.50 |

The first run lost Chess to a bug in the wrapper. The application's own compile kept the caller's start time, which already included the arm compiles. Editor's arms took 63 s, so its real compile met the 60 s deadline at once, the manifest failed, and Chess was never reached. Each real compile now starts its own clock.

## Policies per application

The decision rule: an application compiles with the most optimizing policy whose slowest compile fits within 75% of its deadline. By that rule, the table gives step6 for Agenda and Editor and the full default for Files and Chess. The step that breaks the budget is inlining (step7), which roughly doubles the code every later phase processes.

The compiler already had named policies. Three are used:

```js
const POLICIES = Object.freeze({
    interactive: {...},      // Step 6: operand locations and instruction selection, no inlining or loop transforms
    default: DEFAULT_POLICY, // everything through Step 13
    kernel: {...DEFAULT_POLICY, select: {...DEFAULT_POLICY.select, facts: true}},
    stock: {},
});
```

- **Pins.** A test pins `interactive` to Step 6's ray image, which was timed on the P4 earlier, and `kernel` to the image that board run 10 timed.
- **Firmware.** The firmware names a policy per application through `p4_compile_limits.policy`, which `typed_p4.c` passes as `{policy}`. A misspelled name throws inside the compiler and fails the compile loudly.
- **Replays.** All 24 replays were run with `interactive` as the default. The reported module sizes changed to the Step 6 sizes, which proves the variant was used.

`kernel` exists because of division facts, the last optimization of the evening. Facts take a division or remainder by a constant whose dividend is provably non-negative and drop its rounding bias and sign correction. They took the ray frame from 16.25 to 15.27 ms on the P4, and the Chess evaluation kernel 17.9% faster. They also cost about a quarter more compile time for Chess, which would push its boot compile past its target. So facts stay out of `default`, and compute kernels select them.

## The fixed cost: evaluating the compiler

Even the `stock` arm compiled more slowly than the previous firmware had: Agenda 0.86 s against 0.61 s. The code generation was the same, so the extra time had to be in work every compile repeats. A second measurement image timed evaluation separately (`evalUs`), from creating the runtime to the end of evaluating the compiler sources. Evaluation took 0.41 s for Files and Agenda and 0.53 s for Editor and Chess. That is 80% of a Files compile. During RAY-PARITY, `typed-rv32.js` had grown from 19 KB to 98 KB, and each compile parses it again in a fresh runtime.

QuickJS can serialize compiled functions. The cache in `eval_file` works like this:

```c
compiled_source *cached = compiled_find(path, false);
if (cached && cached->bytes) {
    JSValue function = JS_ReadObject(ctx, cached->bytes, cached->length, JS_READ_OBJ_BYTECODE);
    return evaluate(JS_EvalFunction(ctx, function));
}
JSValue function = JS_Eval(ctx, text, length, path, JS_EVAL_TYPE_GLOBAL | JS_EVAL_FLAG_COMPILE_ONLY);
uint8_t *written = JS_WriteObject(ctx, &size, function, JS_WRITE_OBJ_BYTECODE);
/* copy to PSRAM outside every compiler heap, store under a mutex, never free */
return evaluate(JS_EvalFunction(ctx, function));
```

Bytecode does not depend on the runtime that wrote it, so later runtimes get the same functions. The measurement firmware confirmed it: every module digest equalled the run without the cache. Evaluation fell to 0.05–0.06 s for every compile after the first. Editor under `interactive` went from 3.40 to 2.92 s, and Chess under `default` from 4.34 to 3.86 s. The first compile of a boot still parses. A cache kept in flash, keyed by the source digest, would remove that too.

## Reinstalling without losing a feature

The handheld's everyday firmware has to stay installed, so the new compiler had to reach it. The first build followed the recipe that `AGENTS.md` cites. All boot compiles fit, but Chess appeared as a flat 2D board. The user asked where the 3D Chess had gone.

The recipe predated the 3D painter. The firmware being replaced had been built with `port/esp32p4/build-smooth-chess.sh`. That script turns on `PICOCALC_CHESS_3D` and `PICOCALC_MOBILE_PAINTER`, and `PICOCALC_CHESS_3D` also enables the Candela world. Rebuilt with that script, the firmware boots every world on the new compiler:

| World | Policy | Boot compile | Deadline |
|---|---|---:|---:|
| Candela | default | 2.00 s (first compile of the boot, pays the parse) | 8 s |
| Agenda | interactive | 0.65 s | 1.7 s |
| Files | default | 0.41 s | 1.7 s |
| Editor | interactive | 3.06 s | 6 s |
| Chess, 3D | default | 4.69 s | 6 s |

The recipe now carries a dated note pointing to `build-smooth-chess.sh`. The measurement stager builds the same configuration. Chess with the 3D painter compiles at 78% of its deadline, slightly outside the margin, and the next measurement run covers that configuration.

The device also showed a hardware failure that no flash can fix. After many resets, every I2C transfer to the keyboard's microcontroller failed. The probe kept failing across ESP32 resets until the board was power-cycled by hand.

## What the evening changed in the method

Two gates now come before a compiler default changes or a firmware is installed:

- **The measurement firmware on the device.** Every boot application must stay inside 75% of its deadline under the candidate default.
- **A feature comparison with the firmware being replaced.** Compare the build flags and the world list, not just whether the worlds boot.

## Important project docs

- Ticket: `ttmp/2026/11/21/PICOCALC-COMPILE-BUDGET--fit-the-optimizing-typed-compiler-into-the-picocalc-s-on-device-compile-budgets/`
  - `design-doc/01-measuring-and-restoring-the-on-device-compile-budget-of-the-four-boot-compiled-worlds.md`
  - `reference/01-investigation-diary.md`: Steps 1–5
  - `scripts/01-stage-arms-firmware.py`, `02-run-arms-firmware.py`, `03-summarize-arms.py`, `05-replays-policy.sh`
  - `various/04-arms-run-2/`, `various/06-arms-run-3/`, `various/08-install-smooth-chess/`
- Firmware: `picocalc-os/port/esp32p4/main/typed_p4.c` (`eval_file`, `p4_compile_limits.policy`), `agenda_p4.c`, `editor_p4.c`
- Compiler: `picocalc-os/compiler/typed-rv32.js` (`POLICIES`)

## Open questions

- Does Chess with the 3D painter deserve `default` at 78% of its deadline? Or should it use a policy between `interactive` and `default` that no name covers yet?
- Is tiered compilation worth its kernel support? That means compiling at boot with `interactive` and recompiling with `default` while the device is idle.

## Near-term next steps

- The measurement run on the 3D-Chess configuration, including a `kernel` arm.
- A bytecode cache kept in flash.
- Per-phase compile timers in the compiler, so the host proxies can drop the natively run phases.

## Project working rule

A compiler optimization is not done when the benchmark gets faster. It is done when every application the device compiles at boot still meets its deadline, measured on the device.
