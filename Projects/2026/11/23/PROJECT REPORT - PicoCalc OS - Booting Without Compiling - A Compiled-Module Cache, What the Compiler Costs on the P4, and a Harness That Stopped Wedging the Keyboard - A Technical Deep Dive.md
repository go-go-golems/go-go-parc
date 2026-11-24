---
title: "Booting without compiling: a compiled-module cache, what the compiler costs on the P4, and a harness that stopped wedging the keyboard"
aliases:
  - PicoCalc Typed-next, report 1
  - PicoCalc compile cache
tags: [project, picocalc, operating-system, esp32-p4, compiler, measurement]
type: project
status: active
created: 2026-11-23
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
ticket: PICOCALC-TYPED-NEXT
source_revision: 80b8bb0
---

# Booting without compiling

The PicoCalc's operating system compiles its own applications. Every boot app (Chess, Editor, Agenda, Files, Chess's 3D painter and the Candela scene) is Typed source that the handheld's ESP32-P4 compiles to RV32 machine code before the app's first frame. The day before this work, moving Agenda and Files into Typed had made the boot about 2.8 s slower, and the most demanding Typed program, Candela's path-tracing kernel, took 85 s to compile on the device.

This report describes three tickets of the PICOCALC-TYPED-NEXT program that dealt with what compiling at boot costs:
- **PICOCALC-COMPILE-CACHE** stores each compiled module in flash and reuses it.
- **PICOCALC-COMPILER-DEVICE-COST** measured and reduced the compiler's own memory and time on the P4.
- **PICOCALC-BOARD-HARNESS** fixed the tools that install and check firmware, and found the probable cause of a recurring hardware wedge.

> [!summary]
> - **A warm boot no longer compiles.** Modules are cached on the FAT partition under a SHA-256 of every compile input. A warm boot's first frames arrive 3.6–6.4 s after reset instead of 18.4–21.2 s, and each boot app loads in 28–89 ms instead of 1.5–5.7 s.
> - **The Typed Candela kernel became the gallery's default.** It compiles once in the background (about 2–3 minutes) while the C++ kernel draws, then loads from the cache in 0.3 s.
> - **The compiler costs less memory.** Stripping debug information from its QuickJS bytecode (1,065 → 191 KB) saves 337–590 KB of peak heap and 40–216 ms per boot compile.
> - **Compiles now collect garbage.** The compile allocator had never reported its size to QuickJS, so no compile on the device ever ran the cycle collector.
> - **Writing to flash interferes with the scheduler,** and the writer had to be paced into the kernel's idle gaps.
> - **The keyboard wedges were probably self-inflicted.** Every install reset the chip without first quiescing the keyboard's I2C bus.

## 1. Why every boot compiled

The kernel boots worlds from a manifest. For each Typed app the manifest names a file such as `chess/compiled.bin`, and the port intercepts the read:

```
kernel_boot
  └─ add_world("chess")
       └─ port_read_file("chess/compiled.bin")
            └─ p4_typed_world_read → p4_typed_app_compile → p4_typed_compile   (QuickJS runs the compiler)
```

This chain is synchronous. No world runs until the kernel has added every world, so every app's first frame waits for every compile. The compiles themselves were close to their deadlines:

| App | Cold compile | Deadline | Share |
|---|---:|---:|---:|
| Chess | 4.34 s | 6 s | 72 % |
| Chess painter | 5.65 s | 8 s | 71 % |
| Agenda | 2.79 s | 4 s | 70 % |
| Editor | 3.48 s | 6 s | 58 % |
| Files | 1.52 s | 3 s | 51 % |

Most of these compiles produce the same bytes every boot. The firmware is reproducible: the same source, reactor, compiler and policy always produce the same module. Only an edited source, or a firmware that changes the compiler, changes the output. That is the condition under which a cache is both safe and simple.

## 2. The cache

**Key.** A SHA-256 over every input that can change the module:
- the app's assembled source, including an edited source when the user rebuilt from the store;
- the reactor ELF;
- the bytes of every compiler bundle the compile may evaluate, including the pass groups the backend loads lazily;
- the linker and entry names, the policy, and a format version.

A firmware update that changes any compiler file changes every key, so nothing has to be invalidated by hand. The key is computed at boot, which takes 21–40 ms per app. The design warned that missing one lazily loaded bundle from the key would serve stale modules after an update that changed only that bundle. The key therefore covers every bundle a compile can load, whether or not this compile loads it.

**Storage.** Entries live in a hidden directory on the `files` FAT partition. Each is written as a `.tmp` file and renamed, and carries the full key, the length and a checksum. A read that fails any check is a miss, and the entry is deleted. Eviction keeps two entries per app and source (the current and the previous firmware) within a 4 MB budget, and leaves 1 MB of the partition free.

**Checks on the device:**
- `typed cache verify` recompiled every cached module and compared bytes. It found 6 of 6 identical in three sessions.
- A cache entry with a flipped byte and one truncated were each detected, deleted, recompiled and stored again, and the boot passed health.

**Results:**

| App | Cold compile | Warm hit (key + read) |
|---|---:|---:|
| Chess | 4.34–4.40 s | 89 ms |
| Editor | 3.50 s | 79–80 ms |
| Agenda | 2.75 s | 79–81 ms |
| Files | 1.50 s | 76–78 ms |
| Chess painter | 5.3–5.5 s | 28–33 ms |
| Candela scene | 2.44 s | 59 ms |

A warm boot finishes its boot work 3.4 s after reset instead of about 18 s. The first frames arrive 3.6–6.4 s after reset instead of 18.4–21.2 s.

## 3. Writing to flash without breaking the kernel

The cache's hardest problem was not the cache. It was writing to flash on a device whose kernel promises each world a turn budget.

The first version wrote each entry in one go after the compile. On the device this made Agent, Files and the compositor overrun their turn budgets. A NOR flash erase suspends cache access to flash, so code and data mapped from flash stall until the erase finishes. The kernel's turns stalled with them.

The second version ran the writer at a priority above the kernel, writing small pieces. Turns still broke, for a less obvious reason. A flash erase in ESP-IDF pauses every 20 ms to let other work run, and the kernel used exactly that pause to start a turn. The turn then stalled when the erase resumed.

The final writer runs **below** the kernel on its core:
1. It writes one 4 KB piece only when the kernel is waiting in an idle gap of at least 10 ms and no compile has run on that core for 2 s.
2. It rests between pieces.

Writes take longer, 9–12 s per boot app module and 19–27 s for the 788 KB Candela module, but no world misses a turn. This cost is paid once per firmware.

## 4. The Typed Candela kernel as the default

The previous program left the Typed Candela kernel in a separate firmware profile, because compiling it on the device took 85 s with a 16.3 MB QuickJS peak. With the cache:
- **First use after a firmware update:** the gallery draws with the C++ kernel while the Typed program compiles in the background. That takes 113.5 s alone, or 177–182 s while the writer is storing the boot apps.
- **Every later use:** the module loads from the cache in 0.30–0.35 s (read 0.26–0.32 s, relocate 37–69 ms).

Both arms draw all 18 scenes with digests equal to their references. The `candela-typed` profile was removed, and the playable gallery now defaults to the Typed arm; C++ stays selectable as the benchmark.

Getting the compile to fit took three memory fixes, found by two tickets independently:

| State | Peak QuickJS heap, Typed Candela compile |
|---|---:|
| Before any fix | > 17.8 MB (PSRAM ran out; keyboard, compositor, Snake and Settings worlds failed) |
| Cycle collection during compiles (COMPILE-CACHE) | 13.0–13.4 MB |
| plus each function's emitter released after lowering (CANDELA-KERNEL-CODEGEN) | 9.87 MB |

**Garbage collection.** QuickJS decides when to run its cycle collector from the size the allocator reports in `malloc_size`. Its built-in allocator maintains that count; a custom allocator must do it itself. The firmware's compile allocator never did, so on the device no compile had ever collected a cycle. COMPILE-CACHE and COMPILER-DEVICE-COST both found this in the same afternoon.

**A PSRAM reserve.** Past 8 MB of live compile heap, an allocation that would leave less than 3 MB of PSRAM free is refused, and the compile fails instead of starving the running worlds.

## 5. What the compiler itself costs on the P4

PICOCALC-COMPILER-DEVICE-COST first instrumented every compile. A `TYPEDCOMPILE` record gives, per compile:
- each compiler source evaluated, whether from cached bytecode or parsed, with its load and run time;
- the heap after each evaluation;
- the linker call;
- the teardown;
- the number and duration of calls into the PSRAM heap.

Then it changed three things and measured each in a paired boot study: 4 arms in rotating order, 3 blocks, the module cache emptied before every boot. Each arm repeated itself within 3 ms across blocks.

| App | Control | Kernel pass group | + `JS_STRIP_DEBUG` |
|---|---|---|---|
| Candela scene | 2.818 s, 1,880 KB | −133 ms, −136 KB | −216 ms, −462 KB |
| Editor | 3.558 s | −8 ms | −66 ms, −590 KB |
| Agenda | 2.797 s | −19 ms | −50 ms, −337 KB |
| Files | 1.522 s | +11 ms | −40 ms, −346 KB |
| Chess | 4.391 s | +13 ms | −40 ms, −438 KB |

**Stripping.** QuickJS keeps each function's source text and debug information in its bytecode unless told otherwise. The compiler's seven sources produce 1,065 KB of bytecode unstripped, 263 KB with `JS_STRIP_SOURCE` and 191 KB with `JS_STRIP_DEBUG`. The firmware now strips debug information in every compile runtime, the only producer of the cached compiler bytecode. Compile-error messages are unchanged in all 33 tested cases, because they come from the compiler's own diagnostics. Stack traces through the compiler keep function names and lose file and line.

**A third pass group.** The RV32 backend's optimization passes load lazily in groups. The kernel-only passes moved out of the loop group into their own bundle, so a `default` compile reads 114 KB of group bytecode instead of 256 KB. Only the Candela scene compiles under `default` at boot, so only it gains (−133 ms). The ±10–20 ms on the other apps is noise from heap placement, explained next.

**Arena reuse, built and removed.** QuickJS returns a 4 KB arena to the allocator the moment it empties, and a boot compile takes and returns 2,100–5,100 of them. Keeping up to 64 freed arenas cut heap calls by 33–38 %, but produced no boot gain (+2 to +21 ms). It was removed.

**The P4-only slowdown.** An earlier ticket had measured boot compiles 15–96 ms slower after the backend's passes were split into lazily loaded groups, with no change in host instruction counts. The study found that the same compile repeats within a few milliseconds on one image, but moves by up to about 2 % with where its allocations land:
- Holding a block of 1 KB to 1 MB in front of the heap moved Agenda from 2,719 to 2,766 ms with identical work.
- The difference between lazy and eager loading changed sign for Chess, from +34 ms to −48 ms, between two heap layouts.
- Core 1's L1 instruction-cache misses moved with the time in every case.

The project's compiler guide now says that a compiler-speed claim below about 2 % needs several heap placements, not one pair of images.

## 6. The harness, and the keyboard wedges

The keyboard and battery controller is an STM32 on the P4's I2C bus. Three times in two days the bus stopped answering. Every transfer was NACKed until a person power-cycled the handheld, and board work stopped each time.

PICOCALC-BOARD-HARNESS rewrote parts of the board library (`bench/board/device.py`) with a test suite of 18 cases against a fake console on a virtual clock. It also found an omission. The firmware has a `hold` command that quiesces i2c0 before a reset. The console's own `reboot` uses it, but the install path did not: every install and every restore reset the chip through esptool, at whatever moment a keyboard transfer happened to be in flight. An STM32 left mid-transfer can keep holding the bus. Installs now `hold` first. Since then, one restore and two installs have left the keyboard healthy, though three clean operations prove little against a rare wedge.

Other changes:
- **A fresh boot before judging health.** A board up longer than 120 s is rebooted before health is judged. World errors carry no timestamps, and a USB-powered ESP32 is not reset by switching the handheld off and on, so old errors had failed a healthy board.
- **The keyboard judged on a 5 s window.** It qualifies when transfers rise and errors stay at zero over the window. Cumulative counters had shown 437,641 errors that were hours old.
- **One painter wait** for both peripheral modes, and absolute console deadlines.

A 30-minute soak with key injection (the gallery and Chess in turn, 71 samples) showed 0 I2C errors and no world restarts. The compositor overrun seen after the second wedge did not recur. The evidence points to that overrun following the I2C error storm, not occurring on its own.

## 7. What coordinating this taught

These tickets ran in parallel on one handheld, and that shaped the results as much as the code did.

- **One board is a scheduling problem.** Four agents shared the board through a serial lock, held per measurement block. Each block was sound, but other agents reflashed the board between blocks. One paired study reinstalled its image before every one of its four blocks, and a restore waited 40 minutes for the lock. Board steps took two to four times their planned length.
- **Optimistic merges help, with one rule.** To stop waiting for board studies, two branches were merged into main on their host evidence alone, and their agents kept measuring. One problem slipped through: the merged firmware printed the `TYPEDCOMPILE` record in pieces, another task's console reply landed inside it, and the harness's health check failed on 9 of 12 boots. The agent's own study caught it. The rule that made the merge safe was to install nothing from main until the board numbers were in.
- **Two tickets found the same bug from different sides.** The cache needed the collector to keep the Candela compile in PSRAM, and the cost study needed it to explain heap churn. Their merge conflicted in eight places inside one allocator, and both fixes were kept.

## 8. Open problems

- **The cold boot.** The first boot after every firmware update still compiles everything, and Chess's cold compile is at 72–73 % of its deadline. Each front-end feature adds a little. Cold compile speed (front end, location planner, emitter) is the next research problem.
- **Health checks run too early to catch the writer.** Health is judged at about 10 s of uptime, before the cache writer starts.
- **`typed cache clear` does not cancel a write already queued.**

## Related notes

- [[PROJECT REPORT - PicoCalc OS - App Manifests, One Typed-World Path and No App-Specific C - Restructuring the Operating System Around Typed Applications - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc Candela - The Path Tracer in Typed - Generated from WGSL, Compiled on the ESP32-P4, 1.76x the C++ Kernel - A Technical Deep Dive]]
- [[PROJECT REPORT - PicoCalc Compiler - One Tape, a Target-Neutral Front End, Declared Passes and Register Classes - Refactoring the Typed Compiler for Floats - A Technical Deep Dive]]
- Tickets: `ttmp/2026/11/23/PICOCALC-COMPILE-CACHE--*`, `PICOCALC-COMPILER-DEVICE-COST--*`, `PICOCALC-BOARD-HARNESS--*`, and the program diary in `PICOCALC-TYPED-NEXT--*`.
