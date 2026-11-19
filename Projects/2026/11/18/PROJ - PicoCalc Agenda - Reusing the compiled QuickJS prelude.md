---
title: "PicoCalc Agenda — Reusing the compiled QuickJS prelude"
tags: [project, picocalc, quickjs, compilers, performance]
status: active
type: project
created: 2026-11-18
---

# PicoCalc Agenda — Reusing the compiled QuickJS prelude

A native RV32 Agenda build compiles the reminder parser, starts the application, reads the task file, and publishes its view. During a full-system boot the kernel also initializes the other registered worlds. That made QuickJS startup a major part of the native application's measured response time. Sharing the compiled representation of one firmware script reduced the median cold response from 2.733 s to 2.162 s on the ESP32-P4.

## Measuring the boot lane

The kernel runs world initialization and application turns on one dispatch lane. A newly registered world receives an initialization segment before ordinary messages run. The Agenda experiment records the first segment start and cumulative initialization time for each world until it publishes its first frame. For QuickJS each sample also records runtime setup, prelude evaluation, app source evaluation, and initialization jobs. The firmware stores these timestamps in memory and prints them after the first frame to keep UART wait out of the measured dispatch path.

Across three headless RV32 boots, the eleven QuickJS worlds spent a median of 627 ms in prelude evaluation and about 411 ms evaluating their application sources. Native Agenda itself took about 6 ms to initialize. Agent took about 50 ms. The Calc app alone took about 297 ms to initialize, with about 225 ms in its own source evaluation. These figures explain how a native app can wait for a significant amount of JavaScript work before it sends its first filesystem request.

## Compilation output and runtime ownership

Every QuickJS world has its own runtime, context, globals, memory limit, and interrupt handler. Each also needs the same firmware `js/prelude.js`. The prelude defines the JavaScript side of the system calls and event API. It must run with the world's own `__k` and `__ka` host functions, even though the source text is identical.

QuickJS separates compiling global script text from evaluating its compiled representation. In the typed Agenda firmware, `build_prelude_cache` uses the compile-only evaluation flag in a temporary trusted context and serializes the resulting function with `JS_WriteObject`. The firmware copies those bytes out before destroying the temporary runtime. Every subsequent world uses `JS_ReadObject` to decode a new function and constants into its own runtime, then `JS_EvalFunction` executes them. The serialized bytes contain no live objects from another world. The firmware generates them at boot with the same QuickJS build that reads them.

```text
first QuickJS world:
    compile fixed prelude without executing it
    serialize the result and copy the bytes to the shared heap

each QuickJS world, including a restarted world:
    create its own context and install host functions
    decode the serialized prelude into that context
    execute the decoded function
    evaluate this world's application source and initialize its state
```

If the firmware cannot create the shared bytes, it uses its existing source evaluation path. Editable application source and native Agenda generation use their normal compiler paths. The optimization is contained to the typed Agenda profiles while it is being qualified.

## Results and interpretation

![[picocalc-agenda-quickjs-prelude-cache.png]]

Each condition used three headless ESP32-P4 resets with the same RV32 source, notes file, and installed CJI slot. The endpoint was the first kernel frame publication. Building the cache cost about 95 ms, included in the timing. The shared cache occupied 44,544 bytes. Total prelude work fell to a median of 198 ms. Application worlds still allocate the decoded code and constants under their individual caps. A live Calc restart returned to idle with the restart count incremented, while Chat, Launcher, and native Agenda remained idle.

The three optimized response times were 1.995 s, 2.162 s and 2.163 s. The notes result reached the kernel around 1.919 s on all three boots. Two runs then spent about 240 ms waiting before the result's settlement. To explain the remaining variability, the next trace needs to account for ready work and kernel-side relocation between file return and settlement. The three measurements identify a candidate interval and leave tail latency uncertain. Physical input-to-visible-frame timing remains a separate assembled-device test.

## Reproduction

Firmware commit `d66a65e` adds the per-world trace and its baseline. Commit `464d1ba` adds the cache, matched receipt, Calc restart evidence, and the chart. The implementation is in `picocalc-os/nucleus/vm.c`. Use `scripts/10-measure-agenda-boot.py --world-profile` in the Agenda compiler ticket with a typed RV32 firmware and the board UART. The plotting script in the same ticket generates the figure from the JSON receipts.
