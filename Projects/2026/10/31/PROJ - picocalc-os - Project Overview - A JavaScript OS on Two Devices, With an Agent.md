---
title: "picocalc-os: project overview — a JavaScript OS on two devices, with an agent"
aliases:
  - picocalc-os overview
  - picocalc-os project report
  - ds-js-os
tags:
  - project
  - picocalc
  - papers3
  - quickjs
  - embedded
  - operating-systems
status: active
type: project
created: 2026-10-31
updated: 2026-10-31
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
---

# picocalc-os: project overview — a JavaScript OS on two devices, with an agent

picocalc-os is a small operating system in which almost everything is JavaScript. A C core, the
*nucleus*, runs many isolated JavaScript programs, one at a time, and those programs are the drivers,
the window system and the applications. It started on 2026-10-20 as a simulator on Linux. In eleven days
it ran on two very different devices: a PicoCalc handheld with an ESP32-P4 and a colour LCD, and an
M5Stack PaperS3 e-paper tablet on an ESP32-S3. It now runs a language-model agent on the PicoCalc that
uses local tools and asks before it writes anything. This note is the whole-project view: what was
built, in what order, what each step found, where it stands, and what comes next. The per-phase reports
it links go deeper.

> [!summary]
> - **Isolation by worlds, safety by deferred effects.** Every driver and app is a separate JavaScript VM
>   with its own heap and time budget, talking only by messages. Effects are applied only when a run
>   segment ends cleanly, so a crash discards its half-done work and the supervisor can restart the world.
> - **Seams, not forks.** One nucleus serves two engines (QuickJS, MicroQuickJS), two pixel formats (RGB565,
>   8-bit gray) and three targets (Linux simulator, ESP32-P4, ESP32-S3). Each port was an exercise in finding
>   the one place the core depended on something specific and moving it behind a small API.
> - **The simulator is a measuring instrument.** Virtual time makes runs repeatable and screenshots
>   byte-identical, which turned every refactor into a diff of pictures. The hardware then showed what the
>   simulator could not model: compiler behaviour, heap alignment, caches, radios, power circuits.
> - **The newest layer is an agent.** A chat app and an agent world drive a remote model over a narrow
>   native HTTPS transport. Credentials stay in C, model output is data, and writes need a physical key.

## Why this project exists

The question behind the project is whether a small device can be programmed the way a desktop is: in a
high-level language, with programs that cannot corrupt each other, and with a crash being an ordinary,
recoverable event. A microcontroller usually runs one firmware image in which any bug can bring down
everything. picocalc-os instead gives each driver and each application its own JavaScript virtual machine
and treats failure as data: a world that throws, overruns its time or exhausts its heap is stopped,
reported and restarted, and the rest of the system keeps running.

The PicoCalc is the natural first target. It is a handheld with a full keyboard and a 320×320 screen, a
format for which writing small tools is the whole point. The PaperS3 was chosen as the second target
because it is unlike the first in every way that matters to an OS: touch instead of keys, e-paper instead
of an LCD, gray instead of colour, a different CPU family, and much less RAM per world.

## The system in brief

The concepts are described in full in [[PROJ - picocalc-os on the ESP32-P4 - From Simulator to Hardware - Technical Project Report]];
the short version:

- A **world** is one VM created from one JavaScript file listed in a manifest (`js/system.json`), with a heap
  limit, a time budget and **claims** (the hardware or privileges it may use).
- Worlds share nothing. They `send`, `ask` and `publish` JSON messages; every message carries its sender.
- One **lane** runs one world at a time. A **turn** is one message handled to completion, cut into
  **segments** at each `await`.
- Every effect of a segment (messages, bus transfers, store writes, network requests) is **deferred** and
  applied when the segment ends; a segment that throws is discarded with its effects.
- A **handle** is an integer standing for hardware (an I2C device, a bus, a framebuffer); the kernel checks
  it on every use, and a handle can be narrowed for another world.
- Apps never draw. They return a tree of plain objects; the **compositor** world lays it out, paints a
  framebuffer and asks the **display** world to send the changed rectangles.

```text
           apps (launcher, repl, sysmon, chat, ...)      services (compositor, agent, standby, ...)
                 |  screen() trees, messages                    |  messages, claims
   ==============v==============================================v===================
   nucleus:  kernel.c (lane, mailboxes, deferred effects, supervision)
             vm.c / vm_mqjs.c (engine binding)   hw.c (handles, buffers)   gfx.c (pixels)
   ==============+====================+===================+=========================
       port seam |  board seam        |   engine seam     |  pixel seam
   +-------------v--+  +--------------v---+  +------------v---------+
   | host simulator |  | ESP32-P4 port    |  | ESP32-S3 port        |
   | (Linux, virtual|  | PicoCalc: keys,  |  | PaperS3: touch,      |
   |  time, sim     |  | LCD, Wi-Fi via   |  | e-paper, RTC, power  |
   |  chips)        |  | C6, NVS          |  | latch, NVS           |
   +----------------+  +------------------+  +----------------------+
```

## Timeline

| Date | Ticket / phase | What happened | Report |
|---|---|---|---|
| 10-20 – 10-24 | simulator | The nucleus, the worlds and the host simulator with simulated chips (ST7365P panel, STM32 keyboard) | in the P4 report |
| 10-24 | PICOCALC-P4-PORT | Port seam; the ESP32-P4 port runs on the PicoCalc | [[PROJ - picocalc-os on the ESP32-P4 - From Simulator to Hardware - Technical Project Report]] |
| 10-26 | PAPERS3-PORT | Engine, board and pixel seams; MicroQuickJS binding; PaperS3 simulator, QEMU, first device run | [[PROJ - picocalc-os on the M5Stack PaperS3 - E-Paper, MicroQuickJS and an Idle Tablet - Technical Project Report]] |
| 10-27 – 10-28 | PAPERS3-IDLE | Profiler, stoppable timers, interrupts as messages, light sleep, retained painting, bytecode prelude | same report and [[PROJ - picocalc-os on the M5Stack PaperS3 - Follow-up - Faster Turns on a PSRAM-Bound Tablet]] |
| 10-28 | PAPERS3-OFF | Per-world persistent store, power-off, RTC wake, standby service, resume without a flash | this note |
| 10-31 | PICOCALC-AGENT | Imported agent, adapted to Chat Completions, run on the PicoCalc against a real model | this note |

62 commits on `main`. Every ticket has an intern guide and a diary under `ttmp/`, each uploaded to the
reMarkable.

## Phase by phase

### The simulator (10-20 to 10-24)

The OS was written against a Linux host that models the PicoCalc's chips at the register level and the
passage of time as a cost model: each interpreter step, each bus byte and each pixel has a price in virtual
microseconds. That made every run deterministic. A script of key presses produces the same screenshots,
byte for byte, every time, so the screenshots became the test suite. Thirteen worlds ran: three drivers,
three services and seven apps (launcher, system monitor, REPL, snake, faults, keys, about).

### The ESP32-P4 port (10-24)

The port introduced a **port seam**: the nucleus's few dependencies on the simulator (clock, bus back ends,
heap, file loading) became a small API that the host and the device implement separately. On the device the
kernel runs on the real clock, and each bus has a FreeRTOS worker task that hands results back through one
queue, so the nucleus stays single-threaded. The hardware found three faults the simulator could not:
QuickJS miscompiled at `-O2` without `-fno-strict-aliasing` on 32-bit RISC-V, ESP-IDF's heap returned
4-aligned blocks where QuickJS assumes 8, and `int32_t` is `long` on RISC-V newlib. The simulator's cost
model held where it modelled physics (bus wire time) and drifted where it modelled the compiler.

### The PaperS3 port (10-26)

The second device forced three more seams. An **engine seam** let the same kernel run MicroQuickJS, a much
smaller ES5 engine, behind its own binding (`vm_mqjs.c`) and prelude. A **board seam** let a port name its
own buses and handle types. A **pixel seam** made the graphics code compile for RGB565 or 8-bit gray. The
PicoCalc build kept producing byte-identical screenshots through all of it. E-paper inverted a basic rule:
a waveform pass costs about the same whatever its size, so the display driver sends one update over the
union of the damage and decides between clean and partial refreshes by counting ghosting.

### Idle and speed on the PaperS3 (10-27, 10-28)

PAPERS3-IDLE measured before changing anything. A per-world profiler showed that a 20 ms touch poll and
off-screen apps' timers used seven eighths of the idle lane. Stoppable timers, rendering only the visible
world, and pin interrupts delivered as messages took the idle lane from 23.2% to 0.4%; light sleep then
needed three board-specific fixes (the USB console, re-enumeration, a floating power-latch pin). The speed
phase timed host calls separately from the interpreter, tuned the S3's caches (repaint 94 → 58 ms), added
retained painting with an oracle that compares every partial paint with a full one (31 ms per repaint), and
compiled the prelude to bytecode once (world restart 10–25 ms), which also exposed and fixed an mquickjs
garbage-collector bug.

### Power off and resume on the PaperS3 (10-28)

PAPERS3-OFF made the tablet switch itself off when idle on battery and come back to the same screen. It
was built in five phases, each tested in the simulator, which gained a simulated power cycle (the board
halts, the kernel is reset, time passes, the power button or the RTC starts it again):

- **P1, a persistent store.** Each world gets one JSON record (`store.get/set/remove/all`), quota from the
  manifest (`store_kb`, 16 KB by default), kept in NVS on the device. A write is a deferred effect: a
  segment that faults saves nothing.
- **P2, power-off.** `sys.powerOff()` (claim `sys.power`) pulses the PaperS3's power-latch pin. It refuses
  while external power is present, because USB bypasses the latch.
- **P3, RTC wake.** The clock driver arms the BM8563's timer. Measured: its interrupt power-cycles the board
  even on USB (a real power-on reset), and the first tick of a minute timer comes at the chip's next minute
  boundary, so it can be up to 60 s early; the driver gained second-resolution alarms.
- **P4, standby.** A service waits, without polling, until the board has been idle for ten minutes on
  battery, asks every world to save its state, has the compositor draw an "asleep" screen, arms the RTC if
  configured, and switches off. A board the RTC woke goes back off after 20 s unless touched.
- **P5, resume without a flash.** The last frame is saved run-length encoded (96,023 bytes in 373 ms) and
  adopted at the next boot, so only changed areas refresh. The display library's own initial clear had to be
  disabled first.

What remains is P6, validation on battery with the device unplugged, which needs a person at the device.

### The agent on the PicoCalc (10-31)

An external implementation of an on-device LLM agent arrived as a zip built on the exact current commit. It
was imported unchanged and then made to run on the hardware (ticket PICOCALC-AGENT). Two worlds were added:
`chat`, the screen you type into, and `agent`, which owns the conversation, the request bodies, five local
tools (calculator, device status, list, read and save notes) and the approval of writes. A native transport
posts one bounded JSON body to one configured HTTPS endpoint and adds the bearer token itself, so
JavaScript never sees a URL or a key. On the P4 the radio is the board's ESP32-C6, reached over SDIO through
Espressif's ESP-Hosted.

The first hardware run found three problems: a second `net connect` crashed the P4 inside lwIP (restarting
a running radio over ESP-Hosted adds the network interface twice), TLS stalled because the C6's firmware
streams SDIO packets while the import had chosen packet mode, and the import's (correct) rule that only the
keyboard world may send keys had silently disabled the serial console's key injection. That last one was
fixed by injecting console keys at the keyboard controller's register interface, so they arrive through the
same path as typed keys.

The provider, lunaroute's `deepseek-4.1-flash`, speaks the Chat Completions dialect; the import spoke only
Responses. The agent now keeps its run as Responses items and translates at the edge, so every validation
rule applies to both dialects. Device runs then found two more issues. The model apologised for saves it
had made, because history keeps text only and the instructions forbid claiming unconfirmed tool success;
the device now states which tools ran in the next user message. And the display driver died once for lack
of internal RAM after TLS sessions fragmented it; mbedTLS and network buffers moved to PSRAM.

On the device: a calculation through the local tool, a note saved after an F4 approval, a cold reboot that
restored conversation and note, and the model reading the note back. Credentials are provisioned over the
serial console from local sources (NetworkManager, the pi agent's provider file) and never committed.

## The code today

| Part | Lines | Contents |
|---|---|---|
| `nucleus/` | 3,790 | kernel 730, QuickJS binding 1,020, MicroQuickJS binding 1,032, handles 250, graphics 307 |
| `js/` (PicoCalc) | 1,980 | prelude, 3 drivers, compositor, agent, sandbox, 8 apps |
| `js-papers3/` | 1,826 | ES5 prelude, 4 drivers, paper compositor, standby, 6 apps |
| `port/` | 1,865 | ESP32-P4 and ESP32-S3 ports |
| `host/`, `sim/` | 1,348 | the simulator and its chip models |
| `tests/` | 1,046 | agent unit, native and integration tests |

Two manifests run: 15 worlds on the PicoCalc, and the PaperS3's own set (touch, clock, power, display,
compositor, standby, apps).

## How it is tested

- **Screenshot scripts.** `make shots` runs every script in `scripts/` (and `scripts-papers3/`) and writes
  PNGs; with virtual time they are byte-identical between runs, so `git status` on `out/` is a regression
  check.
- **Ticket scripts.** Each PAPERS3-OFF phase has a script and an expected log, compared after removing
  timestamps.
- **Sanitizer builds** (`build-san`) for the C code.
- **The agent suite** (`make test-agent`): Node unit tests of the agent and chat code against a fake
  runtime, native tests through the host binary with response fixtures, and an integration tour through
  both API dialects.
- **On hardware:** `tools/p4cap.py` and `tools/s3cap.py` reset or attach to a board, send console commands at
  set times and decode screenshots streamed over the UART.

## Measurements across the devices

| Quantity | Simulator model | PicoCalc ESP32-P4 | PaperS3 ESP32-S3 |
|---|---|---|---|
| 100k-iteration loop | 133 ms | 115 ms (offline build) | interpreter-bound; see the follow-up report |
| fib(20) | 29.1 ms | 29.0 ms | — |
| world restart | — | about 55 ms | 10–25 ms (bytecode prelude) |
| idle lane | — | about 8% on the home screen | 0.4% |
| internal RAM free | — | 193 KB (offline build), about 150 KB (Wi-Fi build) | — |
| model round trip | — | 1–3 s per request (lunaroute) | — |

## Working rules the project settled on

- Measure before changing anything; every phase that skipped this paid for it.
- Keep the core single-threaded and hand results to it through one queue.
- Put a policy where its information is: the endpoint's dialect is decided in C because only C knows the
  endpoint; the approval check stays in the compositor because only it knows which world is focused.
- Do not loosen a safety check to make testing easier; find the path real input takes and inject there.
- Import external work unchanged first, so every later change is a reviewable diff.

## Current project status

- PicoCalc (ESP32-P4): running, with Wi-Fi and the agent, on firmware `4a9657b`.
- PaperS3: running with standby and resume; P6 battery validation is pending.
- Open questions: JavaScript runs markedly slower on the P4 while Wi-Fi is up (a runtime benchmark took
  1,601 ms for the loop that takes 114 ms at boot); the agent sometimes still doubts its own earlier tool use
  (one follow-up in three); a one-off loss of the keyboard controller after a flash.

## Near-term next steps

The next round adds the applications a keyboard device is for, in five tickets:

1. **PICOCALC-FS** — a filesystem: the SD card on the device, a directory on the host, a file service world,
   and file handles that can be narrowed to one file or one directory.
2. **PICOCALC-EDIT** — a text editor and a file browser that opens a file in another app by handing it a
   handle to that one file.
3. **PICOCALC-CALC** — a calculator with history and graphing.
4. **PICOCALC-AGENDA** — a todo list and agenda with reminders, using the network clock.
5. **PICOCALC-SYS** — settings (Wi-Fi and provider on the device), Wi-Fi status, a log viewer and an app
   loader for worlds stored on the SD card.

## Important project files and docs

- Repository: `/home/manuel/code/wesen/2026-10-20--ds-js-os/picocalc-os`
- Nucleus: `nucleus/kernel.c`, `nucleus/vm.c`, `nucleus/vm_mqjs.c`, `nucleus/hw.c`, `nucleus/gfx.c`, `nucleus/nucleus.h`
- PicoCalc worlds: `js/system.json`, `js/system/compositor.js`, `js/system/agent.js`, `js/apps/*.js`
- PaperS3 worlds: `js-papers3/system.json`, `js-papers3/system/standby.js`, `js-papers3/system/compositor.js`
- Ports: `port/esp32p4/main/`, `port/esp32s3-papers3/main/`
- Tickets and guides: `ttmp/2026/10/24/PICOCALC-P4-PORT--…`, `ttmp/2026/10/26/PAPERS3-PORT--…`,
  `ttmp/2026/10/26/PAPERS3-IDLE--…`, `ttmp/2026/10/28/PAPERS3-OFF--…`, `ttmp/2026/10/31/PICOCALC-AGENT--…`

## Project working rule

Every phase gets a ticket with an intern guide written before the code, a diary written while working,
commits at each validated step, and a report after.
