---
title: "PicoCalc Agenda — Compiling a native RV32 world on the handheld"
aliases: [Agenda P4 RV32 measurements]
tags: [project, picocalc, compilers, riscv, performance]
status: active
type: project
created: 2026-11-18
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
---

# PicoCalc Agenda — Compiling a native RV32 world on the handheld

Agenda reads a notes file, parses reminders against the device clock, and renders the tasks in a view. The ESP32-P4 can compile the parser from editable source into instructions that execute directly on its RISC-V CPU. In this experiment the native frame-producing turn took about a quarter of the time of the Wasm turn. Compiling native code took longer, so the elapsed time from source to the first frame stayed close to half a second for both targets.

## From typed source to machine instructions

The input program in `picocalc-os/worlds/agenda/reminder.typed` declares the record layout for a task and defines the parser. Its inputs are a UTF-16 string buffer, a title buffer, and a record buffer. The return value indicates whether the line matched. On success, the parser fills the record with task fields and writes the cooked title to the supplied title buffer. A shared validator in `worlds/agenda/compile.js` checks the fields and parser signature before producing either artifact. For example, a boolean field and an integer field both occupy 32 bits in the target interface, but the source contract can distinguish them.

The frontend produces structured integer instructions and function metadata. For RV32, `compiler/typed-rv32.js` assigns stack slots to locals and intermediate operands. For a binary operation it loads the operands into registers, executes the instruction, and saves the result to its operand slot. Each function preserves the ABI's stack alignment and saves its return address across calls. Once instruction locations are known, the emitter resolves branches and writes each instruction word in little-endian order. This direct emitter is small enough to run in the QuickJS realm on the PicoCalc. The stack traffic remains a possible runtime optimization.

```mermaid
flowchart LR
  Source["Typed reminder parser"] --> Ops["Checked functions and integer operations"]
  Ops --> Wasm["Wasm module with linked reactor"]
  Ops --> Words["RV32IM instructions"]
  Words --> ELF["Executable slot in prebuilt ELF"]
  Wasm --> SDK["Agenda world lifecycle and SDK"]
  ELF --> SDK
  SDK --> Frame["File read, reminder and published view"]
```

## How the kernel starts the native world

The compiler patches code generated on the device into a reserved section of an existing shared ELF. The SDK reactor is built ahead of time from `worlds/agenda/wasm-world.c` and the native SDK, with `worlds/agenda/rv32-slot.S` defining the fixed parser slot. The linker locates the unique marker in a file-backed executable segment, copies the new instructions into its reserved area, and replaces the slot entry with a relative jump. Existing reactor addresses and relocations stay valid. The normal native loader resolves the SDK reactor's imported libc symbols and starts the world under the Agenda manifest, which grants access to its notes directory.

The editable parser takes real pointers on the native target. The Wasm version uses offsets in separately managed linear memory. With the current firmware loader, native code runs with firmware privileges and an instruction trap may fault the device. This experimental profile is for the trusted built-in template and trusted source edits. The portable Wasm build remains independently usable.

## Behavioral validation

The native parser ran under the project's RV32 emulator and agreed with Wasm on 6,411 task lines, including all returned record fields and title code units. It also passed 405 calendar cases and 10,000 lead-time inputs. A separate emulator driver loaded the complete native ELF twice at distinct addresses. The driver presented the same simulated notes file to both instances. It advanced the clock through a reminder threshold on the first instance, retained the saved identity, and asserted that the second instance published the view without replaying the reminder. The emulator test used deterministic clock, filesystem and storage stubs at the SDK boundary. The P4 test used the firmware's filesystem and frame publication path with the existing 43-byte task file.

## What the handheld timings establish

The serial benchmark starts before reading the source, creates a fresh compiler realm, loads a fresh world, and ends when the first file-backed frame is published. Each column below summarizes twenty bundled-source trials on a settled system. The RV32 trial used a headless build. The earlier Wasm trial included the peripheral drivers, with an unresponsive keyboard bus. The comparison records what each firmware did. Attribution to the backend alone requires a matched repeat.

| Measurement | Optimized Wasm | RV32 |
| --- | ---: | ---: |
| Compiler median | 258.7 ms | 443.5 ms |
| Source to frame publication median | 538.4 ms | 573.3 ms |
| Source to frame publication p95 | 606 ms | 829 ms |
| Frame-producing turn median | 2.45 ms | 0.66 ms |
| Module size | 42,201 B | 24,304 B |
| Compiler heap peak median | 407,436 B | approximately 586 KB |

Five editable-source RV32 builds reached the frame in a median of 573 ms and a maximum of 586 ms. The full-system RV32 boot took 3.046 seconds from compile start to first publication. The compiler used about 446 ms of that interval. Startup scheduling and the time to obtain the first filesystem settlement deserve their own measurements before further emitter work. The 124,588-byte native world counter includes mapped code and live world heap. The 147,456-byte Wasm figure covers linear memory and interpreter stack.

The stopwatch ends at kernel publication. Finishing the hardware qualification also requires the time from a physical keypress to a visibly changed panel. The native timing run had both keyboard and panel drivers disabled. After the session I restored the previous app image, verified the flash hash and confirmed firmware startup over serial.

## Reproducing the milestone

Firmware commit `e03e3ab` includes the source, the per-trial `various/p4-rv32-bench.json` receipt, and both emulator test drivers in the `PICOCALC-AGENDA-COMPILER` ticket. Build the ESP-IDF project with `PICOCALC_RV32_AGENDA=ON` to generate the native template. Run the parser and world harnesses from the repository root with the cross-compiler and CJI emulator. The ticket diary records the firmware, measurement boundaries, ABI decisions, and diagnostic failures encountered during the tests.
