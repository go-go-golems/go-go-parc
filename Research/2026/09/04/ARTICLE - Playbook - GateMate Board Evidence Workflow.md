---
title: "Playbook - GateMate Board Evidence Workflow"
aliases:
  - GateMate Board Workflow Playbook
  - Olimex GateMateA1-EVB Bring-Up
tags:
  - article
  - playbook
  - fpga
  - gatemate
  - olivex-evb
  - oss-cad-suite
  - hardware-verification
status: active
type: article
created: 2026-09-04
repo: /home/manuel/code/wesen/2026-09-04--gatemate-symbolic
---

# Playbook - GateMate Board Evidence Workflow

This playbook records the operational workflow for producing *evidence* — not just "it seems to work" — from a design on the Olimex GateMateA1-EVB (Cologne Chip CCGM1A1) using the OSS CAD Suite. The facts below were each learned from a concrete failure or a silent gap in the recorded output; together they are the difference between a demo and a measurement.

## The flow

```bash
source ~/fpga/oss-cad-suite/environment
make versions     # record tool versions -> build/tool-versions.txt
make bit PROG=x   # yosys synth_gatemate -> nextpnr-himbaechel -> gmpack
make load         # openFPGALoader -b olimex_gatemateevb build/top.bit
```

Two ports appear on the host: `/dev/ttyACM0` is the RP2040's CDC UART (the FPGA's `uart_tx_pin` arrives here), `/dev/ttyACM1` is the JTAG control channel used by DirtyJTAG.

## Programs run at configuration time

The bitstream configures the FPGA, `CC_USR_RSTN` releases, and the program starts immediately — its output is on the wire within milliseconds, long before a terminal is attached. Capturing the evidence therefore means **reading the serial port concurrently with loading**:

```bash
stty -F /dev/ttyACM0 115200 raw -echo
rm -f /tmp/uart.log
(timeout 6 cat /dev/ttyACM0 > /tmp/uart.log &)
sleep 0.3
openFPGALoader -b olimex_gatemateevb build/top.bit
sleep 3.5
od -c /tmp/uart.log
```

A reader attached after the load captures nothing, and an empty capture is indistinguishable from a broken design. The concurrent-capture pattern (or a logic analyzer on the pin) is the only way to make "no output" mean something.

## Restart without reloading

Wire the FPGA button as a global experiment abort: pressing it async-asserts the design reset; releasing it synchronously restarts the program from the initial ROM image. This turns "run it again while I watch the terminal" into a button press instead of a bitstream reload. It also makes reset semantics explicit: restart-from-initial-image, never resume.

## Pin and LED conventions

- The user LED is **active-low** (the LiteX platform names the pin `user_led_n`): driving the pin low lights it. A "solid ON" state implemented as `pin <= 1` is invisible. Encode states so that *lit* is the success condition and write the polarity down in the README — "LED dark" and "machine dead" are otherwise indistinguishable, and the serial output is the ground truth that separates them.
- A useful state encoding: running = slow blink (~0.6 Hz), halted/success = solid lit, faulted = fast blink (~2.4 Hz). Short programs spend microseconds running, so the blink phase is decorative; the steady state is the signal.

## Reading the budget numbers correctly

- Yosys `stat` reports **cells** (after `synth_gatemate -luttree -nomx8`); nextpnr's "Created N CPEs" reports **packed configurable processing elements**. In the source project, 1,894 cells packed into 392 CPEs — compare budgets against CPEs, and record both.
- Block RAM appears as `CC_BRAM_20K` (20-Kbit halves; two halves per physical block). A 1K×20 ROM and a 512×40 stack each fit one half.
- The routed `Max frequency` line is the number that matters; the pre-route estimate is optimistic.
- Budgets are stop-build triggers, not forecasts. When a design exceeds one, look for register arrays left enabled, wide resets, duplicated decoders, and unexpectedly general multipliers before accepting the number. Debug instrumentation (trace RAM, ILA) is *excluded* from the stop-build budget by convention — the budget guards the architecture, not the observability.

## Working rules

- Record tool versions, synthesis commands, PnR seeds, and the capture method with every hardware result. Without that record, a smaller or faster result may be tool drift rather than a design change.
- Every board claim should be reproducible from one shell command plus one button press; if it needs luck or timing, fix the workflow first.
- Treat absence of output as a claim requiring the concurrent-capture pattern to verify, not as a negative result by default.
