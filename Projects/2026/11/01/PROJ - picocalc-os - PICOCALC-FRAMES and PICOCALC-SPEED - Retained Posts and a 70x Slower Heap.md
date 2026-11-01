---
title: "picocalc-os, PICOCALC-FRAMES and PICOCALC-SPEED: retained posts and a 70x slower heap"
aliases:
  - PICOCALC-FRAMES
  - PICOCALC-SPEED
  - picocalc-os retained channel posts
  - ESP32-P4 LP SRAM heap slowdown
tags:
  - project
  - picocalc
  - esp32-p4
  - performance
  - quickjs
status: active
type: project
created: 2026-11-01
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
---

# picocalc-os, PICOCALC-FRAMES and PICOCALC-SPEED: retained posts and a 70x slower heap

Two tickets came out of one bug report on the device, after the native-worlds work of
[[PROJ - picocalc-os - PICOCALC-NATIVE - WebAssembly and Machine Code on the P4]]: opening Logs restarted the
compositor, and afterwards Calc and Files showed "starting calc…" forever without ever crashing or timing out. The
report had two independent causes. One was a design gap in how worlds share state: a world that restarts never sees
the state other worlds posted before (PICOCALC-FRAMES). The other was a performance mystery left open in
PICOCALC-NATIVE: JavaScript on the ESP32-P4 sometimes ran 2.8 to 14 times slower, depending on things that should
not matter (PICOCALC-SPEED). Its cause turned out to be one line of ESP-IDF configuration. The project overview is
[[PROJ - picocalc-os - Project Overview - A JavaScript OS on Two Devices, With an Agent]].

> [!summary]
> - **Retained posts.** A channel post can now be marked as state (`publish(ch, v, { retain: true })`); the kernel
>   keeps the latest per publisher and channel and replays it to a world that starts later. A world's frame is its
>   retained post on `frames`, so a restarted compositor gets every app's screen back at once.
> - **LP SRAM in the heap was the slowdown.** ESP-IDF adds 32 KB of LP SRAM ("RTC fast memory") to the heap as
>   internal memory. On the P4 an access there costs 994 ns against 14 ns elsewhere, and the caches never see it.
>   QuickJS blocks that landed there made a runtime 2.8–14× slower. One line in `sdkconfig.defaults` removes it.
> - **Two collateral fixes.** The Logs app sent every log line in every frame, and the SPI driver copied unaligned
>   transfers into blocks of up to 32 KB, which failed when memory was tight. Both are fixed.

## Why these tickets exist

The user's words: "the compositor restarts if i open logs, calc takes a shit ton of time to start (right now) /
seems to hang (but also doesn't exit if taking too long). same with files". A traced capture on the device showed
the chain: the compositor overran its 80 ms budget drawing Logs and was restarted; the Logs app then overran its own
tick; and after the restart, opening Calc produced a `focus` message to Calc and no frame back. The benchmark on the
console said JavaScript was running at 316 ms for a loop that normally takes 113.

## Current project status

Both tickets are closed. Commits in `/home/manuel/code/wesen/2026-10-20--ds-js-os`:

| Commit | Change |
|---|---|
| `0da00ca` | retained channel posts in the kernel, the JavaScript and native APIs, tests |
| `6631809` | `cachestat`, a console command that reads the P4's cache counters around a benchmark |
| `4168b95` | `CONFIG_ESP_SYSTEM_ALLOW_RTC_FAST_MEM_AS_HEAP=n` |
| `26c5eb6` | the Logs app sends only the lines that can be on screen |
| `8ab3b51` | SPI transfers that never need ESP-IDF's copy |
| `3edc6b4` | README |

The device runs the normal (agent) firmware with all of these: the benchmark is 113 ms and 30.5 ms at boot and with
every world running, and two stress runs (a full log ring, nine app switches) had no overrun and no crash.

## Implementation details

### Why apps went blank

Apps never draw in picocalc-os. After a world's turn the kernel renders its screen to a tree of ui nodes, and if
the tree changed since the last one it posts it on the `frames` channel, stamped with the world's name; the
compositor keeps the last tree of each app (`s.apps`) and draws the focused one. Three reasonable decisions combine
into the bug:

- the kernel deduplicates frames (`strcmp(f, W->frame)` in `run_segment()`), so an idle app posts nothing;
- a crash wipes a world's state on purpose, so a restarted compositor has an empty `s.apps`;
- a channel post goes to the worlds listening at that moment and is then gone.

The power driver has the same shape: it posts the battery level only when it changes, so the restarted compositor
drew an empty battery glyph.

```mermaid
sequenceDiagram
  participant Calc as calc
  participant K as kernel
  participant C as compositor
  Note over Calc,C: calc's frame F was posted once; K keeps it as W->frame
  K->>C: crash and restart: s.apps = {}
  C->>Calc: focus
  K->>Calc: render -> F again, equal to W->frame: nothing posted
  C->>C: paint: no frame for calc -> "starting calc..."
```

### Retained posts

The channels carry two kinds of message. Some are state (a frame, a battery level, the PaperS3's time) where only
the latest matters and a new listener needs exactly that one. Others are events (a key press, a crash report) that
must never be delivered twice. Only the publisher knows which, so retaining is the publisher's choice:

```js
publish("power", { pct, charging, backlight, screen }, { retain: true });   // js/drivers/power.js
```

```c
// nucleus/kernel.c, simplified
int kernel_retain(world_t *W, const char *ch, const char *json, char *why, size_t n);   // keep W's latest on ch
static void replay_retained(world_t *T) {          // called in T's start segment, after a successful boot
  for each channel ch T needs (and may use, as for a live post):
    for each other running world P:
      json = ch == "frames" ? frame_message(P) : P->retained[index of ch in P->provides];
      if (json) defer_deliver(T, new_msg(M_ON, ch, json, P->id));
}
// teardown(W): drop_retained(W) next to free(W->frame): retained posts go with their publisher
```

Because the replay is queued inside the booting world's segment, it is part of that segment's deferred effects: it
arrives after the `start` message, before anything posted later, and not at all if the start fails. A retained post
carries no handles (they would be granted long after they were sent) and a world may retain at most 4 KB. Native
worlds get the same through bit 0 of the existing publish call (`nw_publish_retained`), so old modules keep working.

The host reproduces the bug deterministically with a script (`key x`, `crash compositor`, `key x`, `capture`); after
the change, the captures before and after the restart are byte-identical, and on the device a compositor killed from
the console comes back with Calc, its title and the battery level.

### The slowdown: the counters said "not the caches"

The PICOCALC-NATIVE diary had a table of benchmark times that defied explanation: 113 ms normally, 316 ms after any
native module load, 1604 ms for the loop alone in one image, 277 ms for fib alone in another. The working hypothesis
was L2 cache conflicts between interpreter code (executed from flash) and heap data (in PSRAM), since both share a
128 KB L2. The P4 has per-bus hit, miss and refill counters for both cache levels; `cachestat` runs one benchmark
program in a fresh QuickJS runtime on a chosen heap and prints them. On the slow firmware, in the same minute:

| Program and heap | Time | L1 code refills | L2 external reads |
|---|---|---|---|
| loop, C library heap | 319.9 ms | 2878 | 1041 |
| loop, PSRAM only | 116.4 ms | 2732 | 1043 |

Same cache traffic, 2.8× the time. The time was going to memory the caches do not handle. Counting where the slow
runtime's allocations landed and timing each kind of memory gave the answer:

```
L2MEM (internal SRAM)       14.0 ns per read and write
PSRAM (through the caches)  14.0 ns
LP SRAM (RTC fast memory)  993.7 ns
allocations: L2MEM 13 (13600 bytes); LP SRAM 8 (29360 bytes); TCM 2; PSRAM 28
```

ESP-IDF's default `CONFIG_ESP_SYSTEM_ALLOW_RTC_FAST_MEM_AS_HEAP=y` adds LP SRAM to the heap with the capabilities of
internal memory, and its help text says the speed has "not much performance impact". With
`CONFIG_SPIRAM_MALLOC_ALWAYSINTERNAL=4096`, blocks of 4 KB or less (QuickJS's atom and shape tables, a context's
arrays) go to internal memory first and land in LP SRAM once the main SRAM is short or fragmented. That explains
every row of the old table: a module load takes internal SRAM, a 16 KB `.bss` change shrinks it, the heap's region
order decides at boot, and which blocks land in LP SRAM decides which program slows down.

World heaps were never affected (they come from PSRAM explicitly), so worlds paid little: their per-turn costs were
within 5 % between the fast and slow firmware. The compositor's original restart was mostly load: the Logs app put
up to 400 lines into every frame, which the compositor parsed and word-wrapped on every draw.

### The flush that ran out of memory

The acceptance run (a full log ring, then app switching) crashed the display driver once with
`spi2: ESP_ERR_NO_MEM`. ESP-IDF's spi_master sends a DMA transaction from the caller's buffer only if its address
and length are multiples of the cache line (`spi_master.c:1156`); otherwise it allocates a copy as large as the
transaction. That was every command byte and the last chunk of almost every rectangle, up to 32 KB, from internal
SRAM whose largest free block was 31 KB. Commands of up to 4 bytes now go inline (`SPI_TRANS_USE_TXDATA`), the bounce
buffers are aligned, and a last chunk goes as its aligned part plus a tail shorter than one line.

## Important project docs

- `ttmp/2026/11/01/PICOCALC-FRAMES--…/design-doc/01-retained-channel-messages-analysis-design-and-implementation-guide.md`
  (intern guide: worlds, the lane, channels, supervision, the screen pipeline, the design)
- `ttmp/2026/11/01/PICOCALC-SPEED--…/design-doc/01-javascript-speed-after-a-native-module-loads-analysis-and-investigation-design.md`
  (the P4's memory system, hypotheses, instruments; an outcome section at the top)
- both tickets' `log/01-diary.md` and `various/` (every device capture quoted)
- `picocalc-os/port/esp32p4/main/perf_p4.c` (`cachestat`)

## Open questions

- The counters' "miss" field behaves like stall cycles (about 465 per L1 refill), not like a count of misses;
  Espressif's register descriptions do not say.
- The panel itself was not inspected after the SPI change: `shot` reads the framebuffer, not the glass.
- Other ESP-IDF defaults may cost the same way on the P4; LP SRAM was found only because the cache counters stayed
  flat while the time tripled.

## Near-term next steps

- Native screens (`nw_frame`) can now store into `W->frame` and get retention for free.
- `drawLines()` in the compositor could wrap only the items it shows.

## Project working rule

When a benchmark disagrees with itself, measure inside the machine before believing a story about it: the cache
hypothesis was plausible, documented, and wrong, and the counters refuted it in one run.
