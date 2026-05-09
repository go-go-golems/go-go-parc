---
title: M5 Tab5 - Getting Acquainted
aliases:
  - M5 Tab5
  - Tab5 Getting Acquainted
  - Tab5 Web Text Echo
  - M5Stack Tab5 Web Echo
tags:
  - project
  - m5stack
  - tab5
  - esp32-p4
  - esp-idf
  - wifi
  - webserver
  - firmware
  - reference
  - documentation
status: active
type: project
created: 2026-04-21
repo: /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/0050-tab5-web-text-echo
---

# M5 Tab5 - Getting Acquainted

The M5Stack Tab5 is a touchscreen IoT terminal built around two Espressif chips: a host application processor and a separate wireless co-processor. That dual-chip design is the first thing to understand, because it makes the board fundamentally different from every ESP32 tutorial board that puts Wi-Fi on the same silicon as the application CPU. This project is the first hands-on investigation of that architecture, starting from the official factory firmware and ending with a working browser-based text echo demo that can be reached from a phone or laptop on the same network.

> [!summary]
> - The Tab5 runs **ESP32-P4** as its application host — a RISC-V dual-core chip with no built-in radio.
> - Wireless connectivity comes from a **separate ESP32-C6 module** connected over SDIO, managed through Espressif's **ESP-Hosted** transport layer and the **esp_wifi_remote** component.
> - The working demo in `0050-tab5-web-text-echo` combines a small HTTP server, a mutex-protected text buffer, NVS-backed Wi-Fi credential storage, and an `esp_console` command-line interface.
> - The project confirmed that the Tab5 Wi-Fi stack cannot be treated as a drop-in replacement for plain `esp_wifi`; the host/remote split has to be explicit from the start.

## Why this project exists

The practical goal was to understand the Tab5 well enough to write firmware for it. A text echo web server is a good vehicle for this because it touches every layer of the system — boot, NVS, Wi-Fi, network stack, HTTP routing, shared state, and a browser frontend — without pulling in LVGL, audio, camera, or RS485 complexity. The board could have been treated as a black box, but the Tab5's two-chip architecture meant that the board's own reference materials had to be studied carefully before the tutorial demo could even compile.

The secondary goal was to produce documentation that a future engineer could use without already knowing the board. That meant keeping the diary, the design guide, and the working firmware in sync, and making sure the design decisions were explained rather than just listed.

## Hardware architecture

The Tab5 is built around two Espressif chips connected by a high-speed SDIO bus. Understanding this relationship is the prerequisite for everything else.

**ESP32-P4 (U1) — the application host.** This is a high-performance RISC-V dual-core SoC running at up to 360 MHz. It has no built-in Wi-Fi or Bluetooth. Its job is to run the application: the display, camera, audio, storage, USB, RS485, and any network services. The P4 is what you program when you write firmware.

**ESP32-C6-MINI-1U (U2) — the wireless module.** This is a complete Wi-Fi 6, Bluetooth 5, and 802.15.4 (Zigbee/Thread) module mounted on the board as a separate package. It is not a general-purpose application processor. Its firmware is pre-loaded at the factory and handles only the radio. It talks to the P4 exclusively over SDIO.

The two chips are physically on the same board and share a 4-bit SDIO bus. The C6 runs its firmware as a slave; the P4 sends it Wi-Fi configuration commands and receives scan results and connection events through a structured RPC protocol. This is the **ESP-Hosted** transport layer.

```mermaid
flowchart TD
    P4["ESP32-P4\nApplication Host\n(RISC-V dual-core 360 MHz)"]
    C6["ESP32-C6\nWireless Module\n(Wi-Fi 6 / BT5 / 802.15.4)"]
    P4-->|SDIO|H["ESP-Hosted\nTransport"]
    H-->|HCI commands|C6
    C6-->|events / data|H
    P4-->|MIPI DSI|LCD["5" IPS TFT\n1280×720\nST7123 driver"]
    P4-->|MIPI CSI|CAM["2 MP Camera\nSC2356"]
    P4-->|I2S|AU["ES8388 Codec\nES7210 ADC\nNS4150 Amp"]
    P4-->|I2C|IO["BMI270 IMU\nRX8130 RTC\nINA226 Power\nIP2326 Charger"]
    P4-->|USB|PC["USB-C\nProgramming"]
    P4-->|SDIO|SD["MicroSD\nSlot"]
    P4-.->|EXT / RS485|IOT["EXT ports\nRS485\nM5-Bus"]
```

This matters for firmware development because **the Wi-Fi driver on the P4 is not `esp_wifi` in the usual sense.** The P4-side code calls the standard `esp_wifi` API, but the calls are transparently forwarded over SDIO to the C6, which actually drives the radio. This is what `esp_wifi_remote` provides — a shim that makes the remote radio look like a local Wi-Fi interface to the application.

## Onboard subsystems

The block diagram and schematics reveal a well-structured board with clearly separated functional blocks.

### Display and touch

The 5-inch IPS TFT display runs at 1280 × 720 (720P) and connects to the P4 over a 2-lane MIPI DSI interface. The display has an integrated ST7123 display driver IC, controlled by the P4 over the shared I2C bus (GPIO 31 / GPIO 32). The backlight is driven by a dedicated ME2212 boost converter, enabled by a GPIO signal from the P4.

The capacitive touch panel uses a GT911 touch controller, also on the shared I2C bus, with its own reset and interrupt lines. The touch panel FPC connector sits on the same physical connector as the display.

### Audio

The audio path is split between a playback chain and a recording chain.

For playback, the P4 sends I2S digital audio to the ES8388 stereo codec (U14), which converts it to analog and drives either the 3.5mm headphone jack or the NS4150B mono Class-D speaker amplifier (U15). The NS4150 is powered from the 5 V rail and driven from the headphone left channel. Speaker enable is controlled by an I/O expander bit.

For recording, two MSM381A MEMS microphones (U16, U17) feed a dedicated ES7210 4-channel ADC (U13), which sends digital I2S audio back to the P4. Both audio chips share the same I2C bus for control, and both get their power from a dedicated `AUDIO_VDD` LDO that keeps digital switching noise off the analog supply. A zero-ohm resistor at the analog ground node is the single point where digital and analog grounds meet — a classic high-performance audio grounding strategy.

### Motion and timing

A Bosch BMI270 6-axis IMU (accelerometer + gyroscope) and a RX8130CE real-time clock are both on the shared I2C bus. The RTC has an interrupt line to the C6 for wake-from-sleep scheduling. The IMU connects through a bidirectional level-shifter because the sensor may operate at 1.8 V while the P4 bus is at 3.3 V.

### Power management

The power architecture handles three input scenarios:

- **USB-C input** through the primary USB-C connector
- **Wide-voltage input** (6–24 V) through the HVIN pin on the M5-Bus header
- **2S lithium battery** (7.4 V nominal) through the dedicated battery connector

A IP2326 2S battery charger IC manages the battery path. The INA226 on the I2C bus provides voltage and current telemetry for monitoring. A CN809R reset controller supervises the standby rail and can trigger a system reset on power dropout. The board uses separate LDO regulators for the camera (1.8 V and 2.8 V rails), the audio chain (clean analog 3.3 V), and the main 3.3 V logic rail.

### Expansion

Two GPIO expander chips (PI4IOE5V6408 at addresses 0x43 and 0x44) provide additional control lines beyond what the P4's native GPIOs can cover. These expanders handle display reset, touch reset, camera reset, speaker enable, external 5 V enable, USB power enable, and headphone detection. Everything on the expansion headers — RS485, Grove, M5-Bus — goes through the shared I2C bus on GPIO 31/32.

## Current project status

The firmware scaffold in `esp32-s3-m5/0050-tab5-web-text-echo` is the primary working artifact of this project.

What is in place:

- a working Tab5 firmware scaffold that boots on the actual hardware
- a minimal HTTP server that serves an embedded browser page
- a mutex-protected shared text buffer with a monotonically increasing version counter
- `esp_console` Wi-Fi commands over USB Serial/JTAG for credential entry and status inspection
- NVS-backed Wi-Fi credential storage so the board remembers the last network on reboot
- AP+STA boot behaviour: the board keeps a recovery SoftAP running while it tries to join the saved STA network
- the official `M5Tab5-UserDemo` firmware tree studied as the factory reference
- the full downloaded Tab5 hardware documentation pack available locally in `M5Tab5-UserDemo/datasheets/`
- a `docmgr` ticket (`ESP-48-TAB5-WEBSERVER-ECHO`) containing the design guide, diary, changelog, and tasks

What remains intentionally simple:

- the echoed text is RAM-only; a board reboot clears it
- the web UI is a single static page with no framework dependencies
- there is no WebSocket push; the browser polls state on load and after each submission
- audio, camera, display, and sensors are not wired into the demo

## Project shape

The firmware is split into five small source files, each with a single clear responsibility.

### `main/app_main.c` — boot orchestration

The entire application entry point is under 40 lines. It calls each subsystem's init function in the right order, then idles.

```c
void app_main(void) {
    ESP_LOGI(TAG, "boot");
    ESP_ERROR_CHECK(echo_state_init());
    ESP_ERROR_CHECK(wifi_app_start());
    wifi_console_start();
    ESP_ERROR_CHECK(http_server_start());
    ESP_LOGI(TAG, "ready");
    while (true) { vTaskDelay(pdMS_TO_TICKS(1000)); }
}
```

The sequence matters. `echo_state_init()` must run first so the mutex exists before the HTTP handlers try to use it. `wifi_app_start()` brings up the network and registers the event handlers. `wifi_console_start()` runs last because it blocks in the REPL loop.

### `main/wifi_app.c` — network bring-up and credential management

This is the most complex file in the project. It handles three distinct concerns:

**NVS persistence.** Credentials are stored as two strings (`ssid` and `pass`) in a dedicated NVS namespace called `wifi`. The module reads them on boot, writes them on user command, and erases them on `wifi clear`.

**ESP-Hosted transport.** The `esp_wifi_init()` call on the P4 creates the transport session with the C6 over SDIO, resets the C6 through GPIO 15, and waits for the HCI handshake to complete. The event handler logs the host IP address once the AP comes up and logs the STA IP once a DHCP lease is acquired.

**AP+STA mode.** The board runs in `WIFI_MODE_APSTA`. The SoftAP (`Tab5-Text-Echo` / `tab5echo`) is always present as a recovery path. The STA interface attempts to connect only when credentials exist in NVS. If the STA connects, the event handler logs the LAN IP so the user knows where to reach the web server normally.

```c
static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_CONNECTED) {
        // transition to CONNECTING
    }
    if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        // log the DHCP lease address
    }
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        // retry up to TAB5_WIFI_MAX_RETRY times, then give up
    }
}
```

The public API surface of `wifi_app.c` is intentionally small: `wifi_app_start`, `wifi_app_get_status`, `wifi_app_set_credentials`, `wifi_app_save_credentials`, `wifi_app_clear_credentials`, `wifi_app_connect`, `wifi_app_disconnect`, and `wifi_app_scan`.

### `main/http_server.c` — HTTP routes and response encoding

The server registers five URI handlers. `GET /` and `GET /app.js` serve the embedded static assets. `GET /api/health` is a smoke test. `GET /api/state` returns the current text as JSON. `POST /api/text` accepts a plain text body, updates the shared buffer, and returns the new state.

The state response requires careful JSON escaping. The handler walks the text byte-by-byte, replacing control characters, backslashes, and quotes with their escaped equivalents. This is a good example of a case where a simple algorithm is clearer than a library call for the typical payload size.

```c
static esp_err_t send_state_json(httpd_req_t *req) {
    echo_state_snapshot_t st = {0};
    esp_err_t err = echo_state_snapshot(&st);
    // ... escape text to JSON-safe form ...
    // ... write chunked response: {"ok":true,"version":N,"text":"..."}
}
```

### `main/echo_state.c` — shared in-memory text buffer

A single mutex-protected struct holds the text, its length, and a version counter. The version counter increments on every write, which lets the browser detect whether its local view is stale without needing timestamps or complex invalidation logic.

```c
static struct {
    SemaphoreHandle_t mutex;
    uint32_t version;
    size_t len;
    char text[ECHO_STATE_MAX_TEXT_BYTES + 1];
} s_state;
```

`ECHO_STATE_MAX_TEXT_BYTES` is set to 1024, which is generous for a text field and small enough to keep on the stack during a snapshot.

### `main/wifi_console.c` — command-line Wi-Fi interface

The console is the only way to configure STA credentials without rebuilding the firmware. It registers a single `wifi` command with subcommands: `status`, `scan`, `set`, `save`, `connect`, `disconnect`, and `clear`.

The `wifi set <ssid> <password> save` flow is the most important UX path:

```bash
tab5> wifi set "YourNetwork" "YourPassword" save
credentials set (ssid=YourNetwork, saved)
connect requested
tab5> wifi status
state=CONNECTED ssid=YourNetwork saved=yes runtime=yes reason=-1
sta_ip=192.168.1.42
ap_ip=192.168.4.1
```

The board will run this connect sequence automatically on every subsequent boot because the credentials persist in NVS.

## Implementation notes

### Why ESP-Hosted is not optional

The Tab5 ships with the C6 pre-flashed to run as the wireless slave. You cannot replace its firmware with application code, and you cannot run Wi-Fi without it. When `esp_wifi_init()` succeeds on the P4, it means the SDIO handshake with the C6 completed. If that handshake fails, the board logs `sdmmc_card_init failed` or `Identified slave [esp32c6] != Expected [esp32]`. The fix is always in the `sdkconfig.defaults` — the slave target must be declared as `esp32c6`, not `esp32`.

### The AP+STA recovery pattern

Running both interfaces simultaneously means the board is always reachable. If the saved STA password is wrong, the STA will retry, exhaust its budget, and fall back to reporting no STA IP — but the SoftAP stays up at `192.168.4.1`. The user can always connect to the SoftAP, open the console, run `wifi clear`, and reconfigure from scratch.

### Why the console uses USB Serial/JTAG

The Tab5's P4 has a dedicated USB Serial/JTAG peripheral. This means the console appears as a CDC device on the host computer without requiring an external USB-UART bridge. The `sdkconfig.defaults` enables `CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y`, which is why the REPL is available on the first USB-C cable that connects the board to the computer.

## User-facing commands

### Build and flash

```bash
# in esp32-s3-m5/0050-tab5-web-text-echo/
./build.sh                    # configure + build
./build.sh flash monitor      # flash + open serial monitor
```

### Console Wi-Fi setup

```bash
wifi status                   # show current AP IP, STA IP, credential state
wifi scan [max]              # scan for nearby networks
wifi set "SSID" "PASS" save  # set + persist credentials
wifi save                    # persist runtime credentials only
wifi connect                 # attempt STA connection now
wifi disconnect              # drop STA
wifi clear                   # erase credentials and disconnect
```

### Browser usage

1. Connect to the SoftAP `Tab5-Text-Echo` with password `tab5echo` (no saved credentials yet).
2. Browse to `http://192.168.4.1/` — the echo page appears.
3. Once the board joins a saved STA network, browse to the STA IP reported by `wifi status`.

## Important project docs

- Local tutorial firmware: `esp32-s3-m5/0050-tab5-web-text-echo/`
  - `main/app_main.c` — boot entrypoint
  - `main/wifi_app.c` — Wi-Fi bring-up and credential management
  - `main/wifi_console.c` — console command implementations
  - `main/http_server.c` — HTTP routes and state response encoding
  - `main/echo_state.c` — mutex-protected text buffer
  - `sdkconfig.defaults` — Tab5/P4 target defaults, ESP-Hosted, and console config
  - `main/idf_component.yml` — `esp_hosted` and `esp_wifi_remote` dependency declarations
  - `README.md` — user-facing quick start
- Official reference firmware: `/home/manuel/workspaces/2025-12-21/echo-base-documentation/M5Tab5-UserDemo/`
  - `platforms/tab5/main/app_main.cpp` — factory app entrypoint and HAL injection pattern
  - `platforms/tab5/main/hal/components/hal_wifi.cpp` — factory Wi-Fi bring-up with embedded HTTP page
  - `platforms/tab5/sdkconfig.defaults` — P4 target defaults and PSRAM/LVGL settings
  - `repos.json` / `fetch_repos.py` — factory dependency fetch model
- Downloaded hardware docs: `M5Tab5-UserDemo/datasheets/`
  - `Tab5_Overall_Design_Block_Diagram.pdf` / `.webp` — authoritative subsystem map
  - `Tab5_Schematics_PDF.pdf` — complete board schematics
  - `sch_tab5_b08_page_01.webp` through `sch_tab5_b08_page_05.webp` — browsable schematic slices
  - `C145_Pinmap_Overview.png` — pin assignments and connector locations
  - `esp32-p4_datasheet_en.pdf` — P4 SoC reference
  - peripheral datasheets: ES8388, ES7210, ST7123, BMI270, NS4150, INA226, IP2326, RX8130
  - `download-manifest.json` — upstream URLs for reproducibility
- Ticket documentation: `esp32-s3-m5/ttmp/2026/04/21/ESP-48-TAB5-WEBSERVER-ECHO--tab5-simple-web-server-text-echo-firmware-guide/`
  - `design-doc/01-tab5-simple-web-server-text-echo-firmware-design-and-implementation-guide.md` — intern-facing architecture and implementation guide
  - `reference/01-diary.md` — chronological investigation record with commands, failure modes, and design decisions
  - `changelog.md` — version history
  - `tasks.md` — completion checklist

## Open questions

- Should the echoed text be persisted to NVS or SD card in a later iteration?
- Should the browser UI eventually display Wi-Fi status and signal strength?
- Is the SoftAP password (`tab5echo`) secure enough for a recovery interface, or should it be randomized or omitted in production?
- Should the console be extended with commands for reading sensor data or displaying text on the screen?
- Does this scaffold have the right shape to serve as a Tab5 starter template for future tutorials?

## Near-term next steps

- Test the saved-credential reconnect path with a real network SSID and password
- Add a browser-side Wi-Fi status panel if the console provisioning UX feels too hidden for everyday use
- Consider whether the NVS partition needs to be enlarged if persistent storage is added later
- Build a small LVGL screen layer that mirrors the current text echo state to the onboard display

## Project working rule

> [!important]
> Treat the Tab5 as a remote-radio board first and a web demo second.
>
> The application CPU (P4) talks to the wireless module (C6) over SDIO through ESP-Hosted. Every Wi-Fi call on the P4 is an RPC to the C6. If you forget this and write code as if `esp_wifi` is local, the board will compile but fail at runtime with SDIO handshake or slave-identification errors. Keep the `sdkconfig.defaults` aligned with the P4+C6 two-chip reality, and keep the SoftAP available as a recovery path.

The overall lesson from getting acquainted with the M5 Tab5 is that the board's architecture is well-thought-out and well-documented — but only if you read both the schematics and the code. Skipping either one produces a false mental model.
