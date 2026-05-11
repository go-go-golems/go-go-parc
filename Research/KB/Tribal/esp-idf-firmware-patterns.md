---
title: "ESP-IDF Firmware Patterns — How We Do It"
aliases:
  - ESP-IDF patterns
  - ESP32 firmware patterns
  - go-go-golems firmware
tags: [knowledge-base, tribal, esp-idf, esp32, firmware, embedded, esp_console]
status: active
type: knowledge-base
created: 2026-05-11
---

# ESP-IDF Firmware Patterns — How We Do It

> [!summary]
> How we structure ESP-IDF firmware projects for M5Stack devices (AtomS3R Lite, M5Paper S3, Cardputer): console commands, web servers, UART drivers, NVS persistence, and WiFi provisioning.

## The pattern

Our firmware projects follow a consistent architecture:

```
main/
  app_main.c          — Entry point: init NVS, netif, WiFi, UART, start console + web server
  web_server.c/.h      — HTTP server with endpoint handlers
  printer_drv.c/.h     — Hardware driver (UART, GPIO)
  printer_cmd.c/.h     — Console commands (esp_console + argtable3)
  nvs_store.c/.h       — Thin NVS wrapper for persistent config
  wifi_cmd.c/.h        — WiFi console commands
  index.html           — Embedded web UI (preprocessed to C array)
```

Key conventions:

1. **`esp_console` REPL as the primary debug interface** — Every firmware gets 10+ console commands accessible over USB serial. Line editing, history, tab completion, and argument parsing come free. A new diagnostic command takes ~20 lines of boilerplate.

2. **Embedded web UI with browser-side processing** — The HTML/JS is embedded as a C byte array (`EMBED_TXTFILES`). The ESP32 serves it on port 80. Heavy computation (image processing, dithering) happens in the browser; the ESP32 only receives the final bitmap.

3. **UART with CTS flow control** — For printer and serial devices, we enable `UART_HW_FLOWCTRL_CTS`. The CTS line pauses TX when the device buffer is full, preventing data loss without manual delays.

4. **Full-body buffering before UART transmit** — For bitmap printing, the firmware reads the entire HTTP POST body into memory before sending the raster command. TCP read gaps inside a raster command produce visible stripe artifacts; buffering eliminates them.

5. **NVS for persistent config** — WiFi credentials, printer settings, and calibration values are stored in NVS key-value pairs. Boot loads them; console commands update them.

## Why we do it this way

- **ESP-IDF over Arduino** — Arduino hides the UART driver behind `HardwareSerial`, which doesn't support CTS flow control or multiple UARTs properly. ESP-IDF gives us `esp_console`, direct UART driver access, and proper NVS.
- **AtomS3R Lite over ATOM Lite** — The ESP32-S3's built-in USB Serial/JTAG frees all GPIO pins (no USB-UART bridge consuming printer pins). 8 MB PSRAM handles full-page bitmaps. The ATOM Lite has pin conflicts and only 520 KB SRAM.
- **Console + Web dual interface** — USB serial for development/debugging; WiFi web UI for end-user operation. Both paths produce the same results.

## Where it lives

| Project | Path | Device |
|---------|------|--------|
| SToMS3R | `esp32-s3-m5/stoms3r/` | AtomS3R Lite + K118 printer |
| Gnosis | `esp32-s3-m5/0078-papers3-gnosis-layout/` | M5Paper S3 |
| BLE Provision | `esp32-s3-m5/0092-m5-printer-esp-idf-provision/` | AtomS3R Lite |
| Cardputer | `esp32-s3-m5/0083-cardputer-adv-animation-ui/` | Cardputer |

### Related PARC project reports

- [[PROJ - SToMS3R - AtomS3R Lite Thermal Printer Firmware]] — console-driven printer controller with 16 esp_console commands
- [[PROJ - Gnosis Layout Engine - PaperS3 UI Operating System]] — tree-based UI with four-stage render pipeline on e-ink

## Common mistakes

1. **Straight-through cable needs pin swap** — The K118's HY2.0-4P cable is straight-through (pin-for-pin), but the ESP32 needs TX→RX crossover. Call `printer_drv_swap_pins(true)` at init. If you forget, `printer_probe` gets no response.

2. **WiFi provisioning loses NVS data** — `esp_wifi_set_config()` overwrites the NVS station block. If you store custom NVS keys in the same namespace, they survive; if you store them in the WiFi namespace, they don't.

3. **Embedded HTML needs NUL stripping** — `EMBED_TXTFILES` appends a NUL byte. Strip it when serving: `if (len > 0 && start[len-1] == '\0') len--;`

4. **9600 baud is slow for bitmaps** — A 384×1200 bitmap (57,600 bytes) takes ~60 seconds at 9600 baud. Don't increase baud without testing — some K118 units are unreliable above 115200.

5. **Missing `esp_console` task yield** — Long-running console commands block the FreeRTOS task. Add `vTaskDelay(pdMS_TO_TICKS(10))` in loops to keep the watchdog happy.

## Variations

- **Banded printing** (SToMS3R fallback): Split large bitmaps into multiple `GS v 0` commands with delays between bands. Creates visible seams at band boundaries. Only use when CTS is unavailable.
- **BLE provisioning instead of WiFi** (ATOM-PRINTER): Use NimBLE GATT server for WiFi credential delivery instead of SmartConfig or WPS.
