---
title: "Browser-Side Processing for Embedded Devices — How We Do It"
aliases:
  - browser-side processing
  - browser offload
  - heavy computation in browser
  - embedded browser offload
tags: [knowledge-base, tribal, embedded, browser, esp32, web-serial, image-processing, offload]
status: active
type: knowledge-base
created: "2026-05-11"
---

# Browser-Side Processing for Embedded Devices — How We Do It

> [!summary]
> When the compute device is a microcontroller, the browser does the heavy lifting. We offload image processing, protocol handling, and data transformation to JavaScript running in the browser, then send only the final artifact to the embedded device. The microcontroller receives a ready-to-use payload and streams it to hardware with zero processing. Two projects converged on this: SToMS3R (dithering + bit-packing in browser, raw 1-bit bitmap to ESP32) and Cardputer Web Serial (protocol engine in browser, NDJSON to firmware).

## The pattern

Our browser-to-embedded systems follow a clear division of labor:

```
Browser (heavy compute)           Embedded device (thin relay)
─────────────────────           ──────────────────────────────
Decode image/parse input         Receive final payload
Resize to device constraints     Stream to hardware peripheral
Transform to device format       No processing, no re-encoding
Pack into wire format            UART / I2S / SPI write

Only final artifact crosses the wire
```

The key invariant: **the embedded device does zero transformation on the payload it receives.** It receives a ready-to-stream artifact and writes it directly to a hardware peripheral. This means the firmware stays simple, the memory footprint stays small, and the device doesn't need a JPEG decoder, a resizer, or a protocol parser.

### The three offload categories we've used

1. **Image processing** (SToMS3R). The browser decodes a JPEG, resizes to 384px, converts to grayscale, runs Floyd-Steinberg dithering, packs 1-bit pixels into bytes (MSB first), and POSTs the raw bitmap. The ESP32 sends an 8-byte GS v 0 header and streams the bitmap to UART. Zero image processing on the microcontroller.

2. **Protocol handling** (Cardputer Web Serial). The browser parses NDJSON from the serial stream, builds command objects, manages UI state, and serializes outgoing commands. The firmware speaks newline-delimited JSON over USB Serial/JTAG. The browser is the protocol engine; the firmware is the serial endpoint.

3. **Image processing in Go/WASM** (Cardputer Web Serial, alternate mode). Same protocol handling, but compiled from Go to WebAssembly instead of written in raw JavaScript. The Go/WASM engine receives raw text from Web Serial, buffers it, splits into lines, parses events, and builds outgoing commands. Same offload principle, different implementation language.

## Why we do it this way

**Microcontrollers have severe memory constraints.** The AtomS3R Lite has 512 KB SRAM + 8 MB PSRAM. A full-page bitmap at 384 pixels wide × 200 lines is only 9.6 KB, but the intermediate processing state (decoded JPEG, resized canvas, grayscale buffer, dithered bitmap) could easily exceed available heap. By doing all intermediate steps in the browser, we only need to buffer the final 9.6 KB on the ESP32.

**Browser APIs are powerful and free.** The Canvas API gives us image decoding, resizing, and pixel access in milliseconds. `FileReader` gives us drag-and-drop file loading. `TextDecoder` gives us UTF-8 handling. All of these would require significant C/C++ libraries on the ESP32. Using them in the browser means the firmware stays small (SToMS3R is 2,291 lines total) and builds quickly.

**The wire format can be device-native.** By processing in the browser, we send data in the exact format the hardware peripheral expects: 1-bit packed pixels for the thermal printer, NDJSON for the serial console, raw PCM for the I2S DAC. The firmware doesn't need to convert between formats — it just writes bytes to a peripheral.

**The browser is the natural UI anyway.** If you're building a web interface for an embedded device, the processing is already happening in the browser. You might as well do the data transformation there too, rather than splitting it between browser and firmware.

Alternatives we considered:
- **Processing on the ESP32.** Requires porting libjpeg/turbojpeg, a resizer, and a ditherer to ESP-IDF. Significant memory pressure. Adds build complexity and firmware size. Only worth it if the device must work without a browser (standalone mode).
- **Processing on a server.** Requires network connectivity. Adds latency. Requires hosting infrastructure. Defeats the "local device" use case.
- **Raw pixel streaming.** Sending uncompressed pixel data from the browser to the ESP32 for dithering. Possible but slow (9600 baud UART) and would require the ESP32 to do dithering + bit-packing, which is exactly the work we want to avoid.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `esp32-s3-m5/stoms3r` | `main/index.html` (embedded) | Browser-side: Canvas, Floyd-Steinberg, bit-packing, POST |
| `esp32-s3-m5/stoms3r` | `main/printer_drv.c` | Firmware: GS v 0 header + `uart_write_bytes()` |
| `esp32-s3-m5/stoms3r` | `main/web_server.c` | Firmware: HTTP server, bitmap streaming endpoint |
| `2026-04-02--cardputer-web-demo` | `web/app.js` | Browser-side: protocol parsing, UI state |
| `2026-04-02--cardputer-web-demo` | `wasm/main.go` | Browser-side: Go/WASM protocol engine |
| `2026-04-02--cardputer-web-demo` | `firmware/main/main.cpp` | Firmware: NDJSON serial loop, device state |

### Related PARC project reports

- [[PROJ - SToMS3R - AtomS3R Lite Thermal Printer Firmware]] — canonical instance: browser dithering + bit-packing → ESP32 UART streaming
- [[PROJ - Cardputer Web Serial Demo - Technical Project Report]] — protocol offload: browser parses NDJSON, firmware echoes to hardware

## Common mistakes

1. **Sending device-native format without verifying it in the browser.** If the browser sends a malformed bitmap (wrong width, wrong byte order, missing padding), the ESP32 will happily stream garbage to the printer, which prints garbage. There's no validation layer on the firmware side because the firmware doesn't understand the payload — it just writes bytes. The fix: validate the payload in the browser before sending. Check width, height, byte count, and bit order against the hardware specification before POSTing.

2. **Not accounting for UART streaming gaps.** The SToMS3R firmware buffers the entire HTTP body before writing to UART because interleaving TCP reads with UART writes creates gaps. At 9600 baud, a 50ms gap in the UART stream makes the thermal printer advance the paper partially, producing horizontal stripes. The fix: read the full body into heap memory, then make a single `uart_write_bytes()` call. The UART driver's ring buffer handles the flow.

3. **Forgetting that the browser may lose the device connection.** The browser connects via Web Serial or WiFi HTTP. Both can drop. If the browser sends a partial payload and the connection breaks, the firmware may be in a half-written state (e.g., a bitmap header sent but pixel data truncated). The fix: either make the payload idempotent (safe to retry) or add a transaction mechanism (start marker → payload → end marker) so the firmware can detect and discard incomplete payloads.

4. **Doing too much processing in the browser and too little on the device.** The offload pattern is a tradeoff, not an absolute. Some transformations are better done on the device: real-time sensor reading, time-critical motor control, interrupt-driven input handling. If you offload a time-critical task to the browser, you add network latency and risk missed deadlines. The rule: offload *computation*, not *timing*.

5. **Not providing a firmware-only fallback path.** The browser-offload pattern requires a browser. If the device must also work standalone (e.g., SToMS3R printing from esp_console without WiFi), the firmware needs its own minimal path for the same operation. The SToMS3R console has `printer_bitmap_test` for this reason — it prints a test pattern without needing the browser.

6. **Assuming the browser and firmware agree on byte order.** The ESC/POS raster bitmap format is MSB-first: pixel 0 is bit 7 (0x80), pixel 7 is bit 0 (0x01). If the browser packs pixels LSB-first, the printed image is horizontally mirrored. The fix: explicitly document and test the byte order convention. The SToMS3R web UI uses `0x80 >> (x % 8)` for MSB-first packing.

## Variations

- **Image processing offload** (SToMS3R). The heaviest variation: JPEG decode → resize → grayscale → Floyd-Steinberg dithering → bit-packing → POST. The browser does ~500ms of JavaScript processing; the ESP32 does a single UART write.

- **Protocol offload** (Cardputer Web Serial, Raw JS mode). The browser parses NDJSON, manages UI state, and builds command objects. The firmware speaks simple JSON over serial. The browser is the protocol engine; the firmware is a thin device controller.

- **Protocol offload in Go/WASM** (Cardputer Web Serial, Go mode). Same as Raw JS, but the protocol engine is Go compiled to WebAssembly. The Go code receives raw text from the serial transport, buffers it, splits into lines, and builds outgoing commands. This proves the offload pattern works across implementation languages.

- **Pure firmware** (SToMS3R console, Wi-Fi Audio Cues Lab). When no browser is connected, the firmware falls back to its own minimal path: esp_console commands for direct hardware control. This is the degenerate case of the pattern — all processing on the device, no browser involved.
