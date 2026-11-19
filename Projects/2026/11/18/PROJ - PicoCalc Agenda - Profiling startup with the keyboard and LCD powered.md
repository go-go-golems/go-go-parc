---
title: "PicoCalc Agenda — Profiling startup with the keyboard and LCD powered"
tags: [project, picocalc, riscv, performance]
status: active
type: project
created: 2026-11-18
---

# PicoCalc Agenda — Profiling startup with the keyboard and LCD powered

With power connected, the peripheral-enabled PicoCalc completed 540 I²C transfers and 82 SPI transfers with zero errors during the serial qualification. The same firmware had previously logged repeated NACKs from the STM32 keyboard and power controller at address 0x1f. The new counters establish that the board's driver transactions complete. The physical keypress-to-visible-frame interval still requires a recording of the keyboard and glass.

## Edit and boot have different costs

A fresh editable RV32 build reached the first file-backed Agenda frame in 667 ms on the powered device. Compilation used 369 ms and peaked at 433,732 bytes under the compiler allocator. The frame-producing turn took 1.022 ms and the native module measured 24,304 bytes. The stopwatch starts before reading the editable source and ends at kernel publication.

The three powered full boots measured about 2.79, 2.86 and 2.91 seconds through the same publication endpoint. The matched headless RV32 median was 1.90 seconds. The powered firmware includes keyboard, power, compositor and display worlds. These worlds initialize, handle messages and service devices while Agenda starts. That changes the amount and priority of work even when Agenda's compiled parser performs the same operations.

## What runs while a notes reply waits

The profiler records the first successful Agenda file reply as it reaches the kernel. It accumulates elapsed segment time and segment count for each world until Agenda publishes. The data stays in a fixed array during boot and is printed after the frame, which avoids serial output for each segment.

In the profiled boot, the reply arrived at 2.296 seconds after source capture and Agenda's settlement began at 2.855 seconds. Measured world segments explain 529 ms of this 559 ms interval.

| World | Segments while Agenda waited | Total segment time |
| --- | ---: | ---: |
| Compositor | 30 | 293 ms |
| Keyboard | 44 | 81 ms |
| Display | 46 | 32 ms |
| Other worlds combined | 19 | 123 ms |

The kernel gives drivers and services higher dispatch priority than applications. This keeps device activity moving and can delay an application whose reply is ready. Segment totals establish which worlds occupied the lane. They do not identify the precise compositor message or rendering operation responsible for its time. The remaining 29.6 ms is outside the measured world segments. In the earlier powered captures CJI relocation finished before the notes reply arrived, so it cannot explain that later waiting interval.

## Reproduction

Commits `db92c07` and `d6de4f8` contain the two bus probes, the powered dispatch profile, and the capture scripts in the Agenda compiler ticket. The instrumentation is in `picocalc-os/nucleus/kernel.c` and `picocalc-os/port/esp32p4/main/agenda_p4.c`. The ticket records the scope of the bus evidence and the separate physical capture protocol. The original app was restored and its boot verified after the experiments.
