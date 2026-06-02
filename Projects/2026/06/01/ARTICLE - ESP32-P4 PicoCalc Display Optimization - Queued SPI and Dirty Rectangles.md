---
title: "ESP32-P4 PicoCalc Display Optimization — Queued SPI and Dirty Rectangles"
aliases:
  - ESP32-P4 PicoCalc display optimization
  - PicoCalc LCD queued SPI
  - ESP32-P4 LCD dirty rectangles
  - PicoCalc display performance deep dive
tags:
  - article
  - esp32-p4
  - picocalc
  - display
  - spi
  - embedded
  - performance
  - dirty-rectangles
status: active
type: article
created: 2026-06-01
repo: /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5
source_ticket: ESP32-P4-PICOCALC
---

# ESP32-P4 PicoCalc Display Optimization — Queued SPI and Dirty Rectangles

This article explains the display optimization work for replacing the PicoCalc's RP2350/Pico MCU with a Waveshare ESP32-P4-WIFI6 board. It focuses entirely on the LCD path: SPI clock selection, DMA chunk size, terminal-shaped workloads, queued SPI transfer, double-buffered RGB565 generation, moving rectangles, background restore, mixed dirty regions, and the display-task API that should follow.

> [!summary]
> 1. The initial 20 MHz ceiling was not a panel limit. ESP-IDF was using the 40 MHz XTAL SPI clock source, so the driver correctly rejected SCLK above 20 MHz. Selecting `SPI_CLK_SRC_SPLL` made actual 80 MHz LCD SPI work.
> 2. A 32 KiB internal DMA buffer reduced full-screen fills to about 21 ms, close to the theoretical 80 MHz RGB565 payload floor for a 320×320 display.
> 3. Terminal-like workloads are not full-frame workloads. Small cells are command-overhead dominated; full-width rows and coalesced dirty regions are much more efficient.
> 4. Queued SPI payload transfer with double-buffered rendering improved pseudo-text redraws from 950 ms to 568 ms per 20 screens, and improved moving/restore/mixed dirty-region workloads as well.
> 5. The safe queued-transfer invariant is precise: do not change the LCD window or the DC GPIO while a queued pixel payload that depends on the current window/DC state is still in flight.
> 6. The next production step is a single display task that owns LCD commands, DC transitions, queued transaction lifetime, DMA buffers, and dirty-region batching.

## Why this note exists

The PicoCalc display path reached a point where simple bring-up notes are no longer enough. The LCD now runs at actual 80 MHz on the same-position adapter wiring, but that fact alone does not describe the performance shape of a usable handheld UI. A terminal, editor, menu system, or widget UI does not repeatedly fill the whole screen with one color. It draws rows, cells, cursors, small moving regions, restored backgrounds, and batches of dirty rectangles.

The optimization work therefore shifted from “can the panel receive bytes?” to “which update shapes make good use of the SPI bus and the ESP32-P4 CPU?” The answer is not a single number. It is a set of constraints and design rules that should guide the next display architecture.

The central lesson is that the LCD driver owns protocol state, not only byte transmission. The SPI master can queue transactions, but the LCD also depends on command ordering, address-window state, chip select, and a GPIO-controlled DC line. Optimizing the display path means improving throughput without losing those ordering guarantees.

## Hardware and firmware baseline

The test firmware is:

```text
0099-esp32-p4-picocalc-display-keyboard/
```

It is intentionally lean: no Wi-Fi, no ESP-Hosted, no HTTP server. That matters because display and keyboard bring-up need a quiet firmware environment. The console runs on the Waveshare board's CH343 USB-UART bridge, and the PicoCalc keyboard uses the same-position adapter mapping:

```c
#define PICOCALC_KBD_I2C_SDA_GPIO 50
#define PICOCALC_KBD_I2C_SCL_GPIO 49
#define PICOCALC_KBD_I2C_SPEED_HZ 10000
#define PICOCALC_KBD_I2C_ADDR     0x1F
```

The current LCD mapping is also the same-position physical adapter mapping:

```c
#define LCD_PIN_SCK   3
#define LCD_PIN_MOSI  2
#define LCD_PIN_CS    7
#define LCD_PIN_DC    24
#define LCD_PIN_RST   25
```

This mapping is important because it is not the function-optimized SPI2 IO-MUX mapping. A cross-routed adapter would put the LCD on GPIO28–GPIO31. The current board instead proves that the simpler same-position adapter can drive the PicoCalc display at actual 80 MHz through GPIO-matrix routing.

## The first false ceiling: why 20 MHz appeared to be the limit

The first LCD tests showed that 20 MHz worked and higher speeds failed. The visible symptom was an ESP-IDF error before pixel transfer:

```text
spi_master: spi_bus_add_device(432): invalid sclk speed
```

The relevant ESP-IDF v5.4.2 rule in `spi_master.c` is:

```c
clock_speed_hz <= MIN(clock_source_hz / 2, 80 MHz)
```

On ESP32-P4, `SPI_CLK_SRC_DEFAULT` resolved to XTAL, and the XTAL source is 40 MHz. Half of 40 MHz is 20 MHz. The driver was behaving correctly: a request above 20 MHz was invalid for the selected source clock.

The fix was to select the SPLL source explicitly:

```c
#define LCD_DEFAULT_SPI_HZ        (80 * 1000 * 1000)
#define LCD_SPI_CLK_SRC           SPI_CLK_SRC_SPLL
```

After that change, the firmware reported:

```text
lcd speed requested=80000000 actual_khz=80000
```

The user visually confirmed 80 MHz color bars. This distinction is essential. `ESP_OK` tells us the driver accepted and completed a transaction. Human-visible output tells us the panel, wiring, timing, color order, and initialization sequence produced correct pixels.

## The wire-rate reference point

A 320×320 RGB565 frame contains:

```text
320 * 320 * 2 = 204,800 bytes
```

An 80 MHz SPI clock transfers 80,000,000 bits per second, or 10,000,000 bytes per second before protocol overhead. The raw payload floor for a full frame is therefore:

```text
204,800 / 10,000,000 = 0.02048 seconds = 20.48 ms
```

This number is useful because it separates two classes of performance problem. A 90 ms full-screen fill is not near the bus limit. It is dominated by transaction overhead, small chunks, software work, or command setup. A 21 ms full-screen fill is near the payload floor, so the next gains must come from sending fewer pixels or overlapping CPU work with transfer.

## The 32 KiB DMA chunk optimization

The first optimized 80 MHz path still used a small pixel buffer. A full-screen fill needed hundreds of SPI transactions. That made the result much slower than the wire-rate reference.

The improved path uses a reusable internal DMA-capable buffer:

```c
#define LCD_SPI_MAX_TRANSFER_SZ   (32 * 1024)
#define LCD_FILL_DMA_CHUNK_BYTES  LCD_SPI_MAX_TRANSFER_SZ
```

The 32 KiB value matches the ESP32-P4 SPI DMA transaction ceiling:

```c
#define SPI_LL_DMA_MAX_BIT_LEN (1 << 18)
```

`1 << 18` bits is 262,144 bits, or 32,768 bytes. A 204,800-byte full-frame fill now needs about seven pixel transactions instead of about 400.

Measured result:

```text
Before 32 KiB DMA chunks: ~32 ms/fill at 80 MHz
After  32 KiB DMA chunks:  21 ms/fill at 80 MHz
```

The optimized fill is close enough to the 20.48 ms payload floor that it is no longer the interesting performance problem. It proves the transport can be efficient when the workload is large, contiguous, and simple.

## Pattern tests: visual and signal stress

Solid fills are weak tests. They can pass even when high-frequency pixel transitions are marginal. The firmware therefore added generated patterns:

```text
lcd pattern checker
lcd pattern stripes
lcd pattern diagonal
lcd pattern all
```

Observed timings:

```text
checker  -> 34 ms
stripes  -> 32 ms
diagonal -> 33 ms
```

These are slower than solid fills because the CPU generates each pixel before transfer. The important result is that the user confirmed these patterns visually. That gives stronger evidence that the same-position GPIO-matrix path is stable at actual 80 MHz.

## Terminal-shaped workloads

A PicoCalc UI will often behave like a terminal: character cells, rows, scroll regions, prompts, status lines, and cursor changes. The firmware added commands for those shapes:

```text
lcd rectbench [w h loops]
lcd cellbench [w h loops]
lcd rowbench [h loops]
lcd scrollbench [row_h loops]
```

Measured results:

```text
lcd rectbench 16 16 500 -> 1170 rects/s
lcd rectbench 80 24 200 -> 843 rects/s

lcd cellbench 8 16 1000 -> 1206 updates/s
lcd rowbench 16 200     -> 546 row updates/s

lcd scrollbench 16 20 -> 27 scroll-style redraws/s, 546 row updates/s
lcd scrollbench 8 20  -> 18 scroll-style redraws/s, 759 row updates/s
```

These measurements explain why a display driver should avoid per-cell updates for bulk redraw. A single 8×16 cell is only 256 bytes of RGB565 payload, but it still requires address-window setup and command/data transitions. A 320×16 row is 10,240 bytes, so the same kind of setup buys much more payload.

The rule is direct: redraw dirty rows when possible, redraw cells only for isolated changes, and coalesce adjacent dirty regions before programming the panel window.

## Pseudo-text: measuring CPU rendering plus SPI transfer

The next benchmark added pseudo-text rendering:

```text
lcd textbench [cell_w cell_h loops]
lcd text [cell_w cell_h]
```

The pseudo-text renderer is not a production font renderer. It generates glyph-like black/white RGB565 pixels into row buffers. That is still valuable because it has the right performance structure: CPU work expands symbolic text into pixels, and then the SPI path transfers those pixels to the panel.

Baseline measurements:

```text
lcd textbench 8 16 20 -> 21 screens/s, 17112 cells/s
lcd textbench 8 8 20  -> 20 screens/s, 32653 cells/s
lcd text 8 16          -> 46 ms/screen
```

The repeatable full performance suite produced the key split:

```text
lcd perf case=text8x16 loops=20 elapsed_ms=955 render_ms=477 transfer_ms=476 screens_s=20 cells_s=16744 payload_kib_s=4186
```

Render time and transfer time were almost equal. That measurement set up the queued-transfer experiment.

## Queued SPI for text rows

The firmware then added:

```text
lcd textqueued [cell_w cell_h loops]
lcd perf queued
```

The queued path uses two internal DMA-capable row buffers. It queues one row's pixel payload, renders the next row while that payload transfers, and waits before changing the LCD window for the next row.

The benchmark result:

```text
lcd perf case=text8x16-poll loops=20 elapsed_ms=950 render_ms=461 transfer_ms=476 screens_s=21 cells_s=16841 payload_kib_s=4210
lcd perf case=text8x16-queued loops=20 elapsed_ms=568 render_ms=463 window_ms=59 wait_ms=21 screens_s=35 cells_s=28152 payload_kib_s=7038
```

This is the clearest demonstration of overlap in the current firmware. Rendering still costs about 463 ms. The queued path improves elapsed time because transfer happens concurrently with the next row's render work.

The implementation intentionally allows only one queued payload in flight. That is conservative, but correct for the manual DC GPIO design. Deeper queueing would require a different command/data abstraction, such as transaction-level DC callbacks or a panel IO layer that owns DC transitions per transaction.

## Moving rectangles: arbitrary dirty payloads

The next question was whether this only helped pseudo-text. `lcd movebench` answers that by generating patterned RGB565 rectangles:

```text
lcd movebench [poll|queued|both] [w h frames]
```

Results:

| Workload | Polling | Queued / double-buffered |
|---|---:|---:|
| `lcd movebench both 64 64 500` | 754 ms, 662 frames/s | 503 ms, 992 frames/s |
| `lcd movebench both 80 40 500` | 607 ms, 823 frames/s | 413 ms, 1208 frames/s |
| `lcd movebench both 128 64 300` | 854 ms, 351 frames/s | 550 ms, 545 frames/s |
| `lcd movebench both 128 128 200` | 1106 ms, 180 frames/s | 697 ms, 286 frames/s |

The queued path helps arbitrary generated rectangles. The gain is not specific to text. It applies when the next payload can be rendered while the current payload is in flight.

## Background restore: a more realistic animation step

A moving rectangle that never erases the old rectangle is not a full animation workload. `lcd restorebench` adds a previous-region restore before drawing the next rectangle:

```text
lcd restorebench [poll|queued|both] [w h frames]
```

Results:

| Workload | Polling | Queued / double-buffered |
|---|---:|---:|
| `lcd restorebench both 64 64 300` | 922 ms, 325 frames/s, 649 ops/s | 604 ms, 496 frames/s, 991 ops/s |
| `lcd restorebench both 80 40 300` | 742 ms, 404 frames/s, 806 ops/s | 496 ms, 604 frames/s, 1206 ops/s |

`restorebench` is closer to real UI motion because it includes background repair. Queued transfer still helps because each operation has enough payload to overlap with background or rectangle rendering.

## Mixed dirty regions: where command overhead becomes dominant

The final benchmark in this phase is `lcd mixedbench`:

```text
lcd mixedbench [poll|queued|both] [w h frames rects_per_frame]
```

It draws several independent dirty rectangles per frame. This models small widgets, cursor fragments, short text changes, and independent UI regions.

Results:

| Workload | Polling | Queued / double-buffered |
|---|---:|---:|
| `lcd mixedbench both 24 16 200 6` | 353 ms, 566 frames/s, 3396 ops/s | 315 ms, 633 frames/s, 3802 ops/s |
| `lcd mixedbench both 40 24 200 4` | 386 ms, 517 frames/s, 2071 ops/s | 303 ms, 659 frames/s, 2638 ops/s |

The queued path still improves performance, but the gain is smaller for tiny rectangles. The reason is visible in the accounting: small rectangles have little payload, so LCD window setup consumes a larger share of the elapsed time. This is where dirty-region coalescing matters.

## The safe queued-transfer invariant

The current driver controls DC manually with `gpio_set_level(LCD_PIN_DC, ...)`. That means the SPI transaction does not carry its own command/data phase. The queued-transfer invariant is therefore:

> A queued pixel payload must complete before firmware changes the LCD address window or changes DC for another command.

The practical sequence is:

```text
render payload into inactive DMA buffer
program LCD address window with polling commands
set DC high
queue pixel payload
render next payload into the other DMA buffer
wait for queued payload completion
program next LCD address window
```

The invariant also defines what not to do:

```text
queue pixel payload for window A
immediately set DC low
send CASET/RASET for window B
```

That sequence can corrupt the in-flight payload because the panel may observe DC or window state changes before all bytes belonging to the old payload have arrived.

## Why one in-flight payload is enough for now

The current queued implementation does not maximize the SPI queue depth. It overlaps one render operation with one transfer operation. That is enough to answer the first performance question: does overlap help? The answer is yes.

Maximizing queue depth would require solving a different problem: each queued transaction would need stable command/data phase semantics and stable address-window semantics. With manual GPIO DC and explicit window commands, deeper queueing would either be unsafe or would still require waiting before every next window change. A future `esp_lcd_panel_io_spi` comparison may be worthwhile because that layer can encode DC handling more directly in the panel IO abstraction.

## Display task API: the architectural next step

The benchmark code now contains enough low-level knowledge to justify a display task. The display task should be the only owner of the LCD device handle, DC GPIO, address-window commands, DMA buffers, queued transactions, and dirty-region coalescing.

A minimal API could be:

```c
typedef enum {
    DISPLAY_CMD_FILL_RECT,
    DISPLAY_CMD_BLIT_RGB565,
    DISPLAY_CMD_TEXT_ROW,
    DISPLAY_CMD_SCROLL,
    DISPLAY_CMD_CLEAR,
    DISPLAY_CMD_PRESENT,
} display_cmd_type_t;

typedef struct {
    display_cmd_type_t type;
    uint16_t x, y, w, h;
    union {
        struct { uint16_t color; } fill;
        struct { const uint16_t *pixels; size_t stride_pixels; } blit;
        struct { const char *text; uint16_t fg, bg; uint8_t font_id; } text_row;
        struct { int16_t dy; uint16_t fill_color; } scroll;
    } u;
} display_cmd_t;

esp_err_t display_start(void);
esp_err_t display_submit(const display_cmd_t *cmd, TickType_t timeout);
esp_err_t display_submit_batch(const display_cmd_t *cmds, size_t count, TickType_t timeout);
esp_err_t display_flush(TickType_t timeout);
```

The task loop should not immediately execute every submitted command. It should drain the queue briefly, merge compatible dirty regions, prefer row batching for text, and then run the safe queued-transfer sequence.

```text
receive one display command
drain more commands for a short bounded interval
normalize commands into dirty operations
coalesce adjacent compatible rectangles
render first operation into buffer A
for each operation:
    set LCD window
    queue current buffer
    render next operation into inactive buffer
    wait for current buffer completion
```

This API separates callers from LCD protocol details. Keyboard code, terminal code, status bars, and future widgets can submit display work without knowing about SPI queue lifetime or DC ordering.

## What should not be optimized next

The next optimization should not be an unsupported attempt to exceed 80 MHz. ESP-IDF's normal GPSPI path enforces 80 MHz, and the full-screen fill is already near the 80 MHz payload floor.

The next optimization should also not be a complicated multi-transaction queue that ignores DC/window ownership. That would make benchmark numbers harder to trust because the failure mode is visual corruption, not necessarily an API error.

The next valuable improvements are:

1. Add operator visual confirmation for queued text, moving, restore, and mixed workloads.
2. Add a real bitmap font renderer so pseudo-text measurements can be replaced by production glyph expansion.
3. Add dirty row and dirty cell tracking for terminal updates.
4. Add dirty-rectangle coalescing benchmarks.
5. Move benchmark loops into a display task or display-owner abstraction.
6. Investigate ST7365P/ILI9488 vertical scroll commands for terminal scroll.
7. Compare manual `spi_master` control against `esp_lcd_panel_io_spi` for DC handling and queue semantics.

## Command reference for the current benchmark harness

The current `0099` display commands include:

```text
lcd init
lcd speed
lcd speed 80M
lcd fill red|green|blue|white|black
lcd bars

lcd bench 10
lcd pattern checker
lcd pattern stripes
lcd pattern diagonal
lcd pattern all

lcd rectbench 16 16 500
lcd cellbench 8 16 1000
lcd rowbench 16 200
lcd scrollbench 16 20

lcd textbench 8 16 20
lcd textqueued 8 16 20
lcd text 8 16

lcd perf
lcd perf full
lcd perf queued

lcd movebench both 64 64 500
lcd restorebench both 64 64 300
lcd mixedbench both 40 24 200 4
```

These commands are now a regression harness. After a display driver change, the useful sequence is to run a transport baseline, a text baseline, a dirty-region baseline, and then leave a visible output on the panel for human confirmation.

## Key points

- The ESP32-P4 can drive the PicoCalc LCD at actual 80 MHz on the current same-position mapping when `SPI_CLK_SRC_SPLL` is selected.
- The full-frame fill path is already near the payload floor; future gains come from batching, dirty tracking, and overlap.
- Queued transfer is useful when CPU rendering and SPI transfer are both significant.
- Tiny dirty rectangles are limited by command/window overhead, so coalescing and row batching matter.
- Manual DC GPIO control requires strict sequencing around queued transactions.
- A display task is the right production owner for LCD protocol state, queued transfer, DMA buffers, and dirty-region normalization.

## Source artifacts

The main source files and docs for this phase are:

```text
/home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/0099-esp32-p4-picocalc-display-keyboard/main/app_main.c
/home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/0099-esp32-p4-picocalc-display-keyboard/README.md
/home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/ttmp/2026/06/01/ESP32-P4-PICOCALC--esp32-p4-wifi6-as-picocalc-mcu-replacement-rp2350-swap/design-doc/04-picocalc-lcd-spi-throughput-optimization-guide.md
/home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/ttmp/2026/06/01/ESP32-P4-PICOCALC--esp32-p4-wifi6-as-picocalc-mcu-replacement-rp2350-swap/reference/01-investigation-diary.md
```

Relevant commits:

```text
7bb4d1a 0099: optimize LCD fill throughput
e91b3e5 0099: add queued LCD text benchmark
43c06dc 0099: add moving rectangle LCD benchmark
665a3fe 0099: add dirty region LCD benchmarks
```
