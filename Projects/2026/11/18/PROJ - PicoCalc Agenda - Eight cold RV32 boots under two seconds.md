---
title: "PicoCalc Agenda — Eight cold RV32 boots under two seconds"
tags: [project, picocalc, riscv, compilers, performance]
status: active
type: project
created: 2026-11-18
---

# PicoCalc Agenda — Eight cold RV32 boots under two seconds

On the headless ESP32-P4, Agenda compiled its parser to RISC-V, read the real task file, and published the file-backed view in a median of 1.897 seconds on eight fresh firmware boots. The slowest boot took 1.910 seconds. The measurement starts before source capture and ends when the kernel publishes the frame. It includes an initialized Agenda world and a real filesystem settlement.

## The remaining startup race

Previous profiling removed repeated QuickJS prelude compilation, putting the first file reply at about 1.92 seconds. Agenda still could not render until its settlement segment ran on the kernel lane. The installed CJI development compiler restores on that same task when it needs to relocate its tool ELF. Relocation stops other dispatch work while the loader resolves the executable and coordinates instruction-cache maintenance.

Two new timestamps mark the entry and exit of the actual loader call. In a baseline reboot, the notes reply reached the kernel at 1.917 s. CJI relocation started at 2.001 s, with the reply already queued. It ended at 2.147 s, and Agenda started handling the result at 2.149 s. On the other two baseline boots Agenda began the settlement before the deadline, and relocation ran after the frame. The same filesystem result could therefore take two different paths to publication.

```text
slow baseline    file arrives  ->  CJI relocation  ->  Agenda settles  ->  frame
post-change      file arrives  ->  Agenda settles  ->  frame           ->  CJI relocation
```

The firmware now allows up to 50 ms of extra deferral if a successful Agenda read returns before the original boot deadline. The filesystem callback checks the current world epoch. Publication releases the deferral immediately, and the extended cutoff remains finite if the world fails to publish. None of the eight optimized boots reached the original deadline. This verifies the improved fast path and CJI resumption. A controlled near-deadline experiment would be needed to measure the extension itself.

## Why the native linker was consuming time

The editable program provides the parser, and a prelinked native reactor provides the world lifecycle and SDK. The linker in `picocalc-os/compiler/typed-rv32.js` scans executable ELF segments for a four-word marker. Most positions fail on the first word. The original JS loop created an array callback and invoked it at each candidate. Direct little-endian comparisons retain the same search and uniqueness requirements while removing the per-candidate callback. The linker also constructs the output directly from the existing typed byte array, which lets QuickJS use its typed-array copy path.

Median cold compilation fell from 449.2 ms to 360.7 ms. The output file remained exactly 24,304 bytes and matched the previously validated ELF hash. The emulator revalidated the parser on 6,411 task lines and confirmed that a persisted reminder did not replay after restarting the native world.

| Post-change headless trial | Runs | Median first response | Maximum |
| --- | ---: | ---: | ---: |
| Fresh firmware boot | 8 | 1.897 s | 1.910 s |
| Editable source while CJI was active | 5 | 0.749 s | 1.320 s |

The compiler allocator peaked at a median of 433,504 B on the editable runs. The native module and world counters measure other parts of the process. The two rows use different background conditions. The editable results confirm that the normal source file still builds and publishes a view under concurrent compiler activity.

## Reproducing the hardware boundary

The baseline trace is in `92f2a2f` and the changed headless measurements are in `19a73d6`. The Agenda compiler ticket contains the serial sampler, emitted-artifact tests, full receipts, and restore evidence. A clean build after `8d537a0` also produced the peripheral-enabled RV32 image with the keyboard, compositor and display worlds in its manifest. This prepares the separate physical measurement. It requires the assembled handheld, a real launcher keypress, and observation of the first changed LCD pixels.
