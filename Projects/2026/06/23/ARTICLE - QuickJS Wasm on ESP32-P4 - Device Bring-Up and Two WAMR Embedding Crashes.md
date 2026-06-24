---
title: "QuickJS-WASM on the ESP32-P4: Device Bring-Up and Two WAMR Embedding Crashes"
aliases:
  - QuickJS Wasm ESP32-P4 Device Bring-Up
  - WAMR ESP-IDF Embedding Crashes
  - EMBED_FILES WAMR Flash Buffer
tags:
  - article
  - wasm
  - wamr
  - embedded
  - esp32
  - esp32p4
  - quickjs
  - debugging
status: resolved
type: article
created: 2026-06-23
updated: 2026-06-23
repo: /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/0100-esp32-p4-quickjs-wasm
---

# QuickJS-WASM on the ESP32-P4: Device Bring-Up and Two WAMR Embedding Crashes

This note records what happened when a QuickJS engine compiled to WebAssembly was first run on an ESP32-P4 after it had already passed on a host PC. The host result was correct, so the device session became a study of the assumptions a host environment hides. Two failures appeared, both in the WebAssembly Micro Runtime (WAMR) embedding layer rather than in QuickJS, and both are general to any WAMR-on-ESP-IDF embedding. Both failures are now fixed and verified on hardware: the firmware completes `qjs_init` and evaluates JavaScript from the ESP console on the ESP32-P4.

> [!summary]
> - On the host, the wasm module buffer was `malloc`'d and the calling thread was a pthread. On the device, `EMBED_FILES` puts the module in read-only flash and `app_main` runs on a FreeRTOS task that is not a pthread. Both differences caused a crash that the host could not expose.
> - **Crash 1 (fixed):** WAMR's loader writes into the module buffer it is given. A flash-mapped buffer is read-only, so `wasm_runtime_load` faulted with a store-access exception. Copy the module to writable PSRAM before loading.
> - **Crash 2 (fixed):** `wasm_runtime_call_wasm` records the calling thread via `pthread_self`. `app_main`'s task is not a pthread, so the call asserted. The fix is a long-lived owner pthread: it initializes WAMR's thread environment, owns the QuickJS/WAMR session, and services console eval requests through a queue.
> - **Verified result:** on the ESP32-P4, `qjs_init` completes in roughly 2.7 seconds and `js eval "print(1+2)"` prints `3`.

## Why this note exists

Embedding a Wasm runtime in ESP-IDF firmware is a recurring pattern: compile an engine to Wasm, embed the runtime, call an exported function. The outline is simple, and on a host PC it usually works on the first try. The device is where the embedding assumptions break, because the host provides a writable heap and pthread semantics that ESP-IDF does not hand to every task for free. These two failures are worth writing down once because they will recur in any WAMR embedding that uses `EMBED_FILES` and calls exports from `app_main`.

The concrete vehicle is firmware `0100-esp32-p4-quickjs-wasm`, which runs QuickJS-as-Wasm under WAMR on a PicoCalc ESP32-P4 board. The Phase 0 host implementation and its own failure modes are recorded separately in [[ARTICLE - QuickJS Wasm on WAMR - Running a JS Engine Inside a Wasm Sandbox]]. This note covers only the device port.

## What was already proven on the host

Before any device work, the stack ran end to end on a PC. A small host program embedded WAMR (built from the vendored `bytecodealliance/wasm-micro-runtime`), registered three native symbols under the import module `"env"` (`host_print`, `host_millis`, `host_gpio_write`), loaded `quickjs.wasm`, instantiated it, called `qjs_init`, and evaluated JavaScript through `qjs_eval`. The smoke test passed: `print(1+2)` returned `3`, loops and string concatenation worked, and `throw new Error('boom')` surfaced as `Error: boom`. The host result is the reference for correctness. Nothing in this note revisits the engine itself.

The host program did two things that turned out to matter on the device and not on the host: it read the wasm from disk into a `malloc`'d buffer, and it ran the WAMR calls on a normal Linux thread. Both are incidental on a host and load-bearing on a microcontroller.

## The device baseline that worked

The firmware flashes and boots, and the parts that do not touch the two failures work. From the monitor:

```
I (600) esp_psram: Found 32MB PSRAM device
I (601) esp_psram: Speed: 200MHz
I (1566) cpu_start: cpu freq: 360000000 Hz
I (1880) 0100_qjs: WAMR ready: pool=16777216 bytes, pool_external=yes
I (1880) 0100_host: registered 3 env native symbols
```

The ESP32-P4 detects its 32 MB hex PSRAM at 200 MHz, runs its HP core at 360 MHz, allocates a 16 MB WAMR pool in PSRAM, and registers the three `env` native symbols. The setup is not the problem. The problems begin at the next two calls.

## Failure mode 1 — WAMR writes to the module buffer

The firmware embeds `quickjs.wasm` with `EMBED_FILES`, which turns the blob into `_binary_quickjs_wasm_start` / `_binary_quickjs_wasm_end` symbols. Those symbols point into flash-mapped `.rodata`. The bootloader reports the segment as `vaddr=40070020 size=14064ch`, so the wasm occupies `0x40070020` through `0x401b066c`. Flash is read-only at runtime.

The firmware passed that pointer straight to `wasm_runtime_load`. WAMR's loader does not treat its input as read-only. It writes into the buffer — for example, to rewrite bytecode for the fast interpreter and to handle the reference-types sections that Clang 22 emits. The first write faulted:

```
Guru Meditation Error: Core 0 panic'ed (Store access fault). Exception was unhandled.
MCAUSE : 0x00000007   MTVAL : 0x400809b9
--- b_memmove_s at .../core/shared/utils/bh_common.c:116
A0 : 0x400809b9   A1 : 0x400809ba   A2 : 0x00000003
```

`MCAUSE 0x7` is a store access fault. `MTVAL 0x400809b9` is the address of the store, and it lies inside the wasm segment (`0x40070020`–`0x401b066c`). The register dump shows `b_memmove_s` shifting three bytes within the buffer at `0x400809b9`. WAMR was rewriting the module in place; the module was in read-only flash.

The host did not fault because the host read the wasm from disk with `malloc`, which returns writable memory. The same library call, `wasm_runtime_load`, behaved differently only because the buffer it received had different permissions.

The fix is to give WAMR a writable copy. Allocate the copy in PSRAM (the blob is 1.2 MB; internal SRAM is too small and too precious) and pass that to `wasm_runtime_load`:

```c
size_t sz = quickjs_wasm_size();
g_wasm_copy = heap_caps_malloc(sz, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
memcpy(g_wasm_copy, quickjs_wasm_data(), sz);
g_mod = wasm_runtime_load(g_wasm_copy, sz, err, sizeof(err));
```

After this change the device log reads `copied quickjs.wasm (1231348 bytes) to writable buffer 0x49000aa8` and the load completes. This crash is closed. The general rule: the buffer handed to `wasm_runtime_load` must be writable. `EMBED_FILES` does not produce a writable buffer, so an embedded Wasm module must be copied to RAM or PSRAM before loading.

## Failure mode 2 — `wasm_runtime_call_wasm` needs a valid thread identity

With the load fixed, the firmware originally called `qjs_init` (a `wasm_runtime_call_wasm` with zero arguments) directly from `app_main` and asserted immediately:

```
assert failed: pthread_self pthread...
#0  panic_abort (details="assert failed: pthread_self pthre...")
#3  pthread_self ()
#4  os_self_thread ()                       (WAMR)
#5  wasm_exec_env_set_thread_info ()
#6  wasm_call_function (argc=0, argv=0x0)
#7  wasm_runtime_call_wasm ()
#8  wasm_runner_init ()                    ← the qjs_init call
#9  app_main ()
```

`wasm_runtime_call_wasm` calls `wasm_exec_env_set_thread_info`, which records the thread that owns the execution environment. In the registry `espressif/wasm-micro-runtime` component used by 0100, the ESP-IDF platform implementation reaches `pthread_self`. `pthread_self` is only valid on a task created through ESP-IDF's pthread layer. The `main_task` that runs `app_main` is a plain FreeRTOS task, not a pthread, so the call asserted before QuickJS executed.

The comparison project `0079-papers3-wamr-assemblyscript-console` provided the key clue. It has a pthread-worker execution path (`RunEmbeddedWasmModuleOnWorkerThread`) and a local WAMR ESP-IDF shim where `os_self_thread()` returns `xTaskGetCurrentTaskHandle()` instead of calling `pthread_self`. For 0100, the durable fix was to avoid editing generated `managed_components` and instead make the application own the thread context explicitly.

The fixed 0100 runner now has one long-lived owner pthread:

1. `wasm_runner_init()` creates a pthread and waits for it to finish initialization.
2. The worker calls `wasm_runtime_init_thread_env()`.
3. The worker copies `quickjs.wasm` to PSRAM, loads it, instantiates it, creates the WAMR exec environment, and calls `qjs_init`.
4. The worker then waits on a FreeRTOS queue for eval requests.
5. `js eval` commands call `wasm_runner_eval()`, which queues an `EvalRequest`, blocks on a completion semaphore, and returns the worker's result.
6. All `wasm_runtime_call_wasm()` calls now happen on the owner pthread, not on `app_main` or the console task.

The design fixes the assertion and also serializes access to the QuickJS context. That is important because QuickJS contexts should be treated as single-owner state unless deliberately protected by a stronger concurrency design.

Verified hardware output after this fix:

```text
I (2001) 0100_run: copied quickjs.wasm (1231348 bytes) to writable buffer 0x49000aa8
I (4681) 0100_run: QuickJS ready (qjs_init ok on worker pthread)
I (4681) 0100: QuickJS ready. Try: js eval "print(1+2)"

0100>  js eval "print(1+2)"
3
0100>  js status
runtime=ready
pool=0x48000aa4 external=yes size=16777216
wamr.heap_total=16777024 heap_free=14547872 highmark=2229152
0100>  js eval "let s=0; for (let i=0;i<5;i++) s+=i; print(s)"
10
0100>  js eval "throw new Error(\"boom\")"
Error: boom
Command returned non-zero error code: 0x1 (ERROR)
```

The observed `qjs_init` latency was roughly 2.7 seconds, measured from `I (2001)` (`quickjs.wasm` copied) to `I (4681)` (`QuickJS ready`).

## Working rules

- The buffer passed to `wasm_runtime_load` must be writable. An `EMBED_FILES` blob lives in read-only flash; copy it to PSRAM before loading. This applies to every WAMR embedding that embeds its module, not only QuickJS.
- `wasm_runtime_call_wasm` must run from a context that gives WAMR a valid thread identity. In 0100, the safe application-level pattern is a long-lived owner pthread, not ad hoc calls from `app_main` or the console task.
- A host smoke test does not substitute for a device test. The host provides writable memory and pthreads by default; the device does not. Treat a passing host test as evidence that the embedding logic is correct, not that the device will run.
- When a crash dumps `MCAUSE` and `MTVAL`, read them: `MCAUSE 0x7` is a store fault, and `MTVAL` is the faulting address. Compare `MTVAL` to the linker segment ranges in the bootloader log to tell flash from SRAM from PSRAM.
- Keep one monitor per serial port. Drive the ESP-IDF console through `idf.py monitor` in a tmux session so commands can be sent with `tmux send-keys` and output captured with `tmux capture-pane`, and kill the session before flashing so the flash and monitor never contend for the port.

## Reproducing

```bash
cd /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/0100-esp32-p4-quickjs-wasm
source /home/manuel/esp/esp-idf-5.4.2/export.sh
# device: /dev/serial/by-id/usb-1a86_USB_Single_Serial_5B61091051-if00 (-> /dev/ttyACM0)
idf.py build && idf.py -p /dev/ttyACM0 flash
tmux new-session -d -s qjs0100 -c "$PWD" \
  "bash -lc 'source /home/manuel/esp/esp-idf-5.4.2/export.sh >/dev/null 2>&1; idf.py -p /dev/ttyACM0 monitor'"
sleep 6; tmux capture-pane -t qjs0100 -p | tail -40
tmux send-keys -t qjs0100 'js eval "print(1+2)"' Enter
tmux kill-session -t qjs0100
```

The fixed firmware now reaches the prompt and returns the expected result:

```text
0100> js eval "print(1+2)"
3
```

Keep the monitor single-owner and kill `qjs0100` before reflashing.

## Related notes

- Host implementation and its own failure modes: [[ARTICLE - QuickJS Wasm on WAMR - Running a JS Engine Inside a Wasm Sandbox]].
- Full device post-mortem with addresses, backtraces, and the resolved hardware smoke result: `0100-esp32-p4-quickjs-wasm` ticket `design/02-phase1-device-bringup-post-mortem.md`.
- Working WAMR-on-ESP32-S3 reference to compare against: `0079-papers3-wamr-assemblyscript-console` (its `wasm_module_runner.cpp`, `wasm_command.cpp`, and `sdkconfig`).
- ESP-IDF build/dev-environment rules: `AGENTS.md` and `docs/01-playbook-esp-idf-build-and-dev-environment.md` in the `esp32-s3-m5` workspace.
