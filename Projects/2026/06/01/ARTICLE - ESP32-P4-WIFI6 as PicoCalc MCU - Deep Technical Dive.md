---
title: "ESP32-P4-WIFI6 as PicoCalc MCU — Deep Technical Dive"
aliases:
  - ESP32-P4 PicoCalc
  - Waveshare ESP32-P4-WIFI6 PicoCalc
  - PicoCalc ESP32-P4 replacement
tags:
  - article
  - esp32-p4
  - picocalc
  - hardware
  - firmware-port
  - waveshare
  - rp2350
status: active
type: article
created: 2026-06-01
repo: /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5
updated: 2026-06-01
---

# ESP32-P4-WIFI6 as PicoCalc MCU — Deep Technical Dive

This article documents a feasibility investigation and initial firmware bring-up for replacing the Raspberry Pi Pico (RP2040/RP2350) inside a ClockworkPi PicoCalc with a Waveshare ESP32-P4-WIFI6 development board. The investigation covers hardware compatibility, pin mapping, power analysis, firmware migration strategy, and the practical results of flashing and booting the first ESP-IDF firmware on the actual board.

> [!summary]
> 1. The Waveshare ESP32-P4-WIFI6 can replace the Pico in the PicoCalc, but not as a drop-in — an adapter PCB is required to remap peripheral connections.
> 2. The board exposes 25 GPIOs on two 2×20 headers, all available for the PicoCalc project; on-board peripherals (C6 SDIO, I²S codec, SDMMC, UART) consume only internal-trace GPIOs that never reach the headers.
> 3. The specific board received carries ESP32-P4 revision v1.3 silicon, which is supported by ESP-IDF 5.3+. Phase 1 is validated: the board boots ESP-IDF v5.4.2, detects 32 MB PSRAM at 200 MHz, reaches `app_main()`, and prints logs through the on-board CH343 USB-UART bridge on `/dev/ttyACM1`.
> 4. The first networking experiment is also validated: `0098-esp32-p4-wifi6-webserver` brings up the onboard ESP32-C6 over ESP-Hosted SDIO, joins `yolobolo`, starts an `esp_console` REPL, and serves HTTP on the LAN at `http://192.168.0.88/` during the captured run.

## Why this note exists

The PicoCalc ships with a Raspberry Pi Pico as its main MCU. That MCU works, but it has constraints: no built-in Wi-Fi on the base model, limited RAM (264–520 KB SRAM plus an 8 MB PSRAM driven by PIO bit-bang), no hardware display acceleration, and a single SPI bus shared between the LCD and SD card. The ESP32-P4 offers a 360 MHz dual-core RISC-V processor, 32 MB stacked PSRAM on a hardware bus, 32 MB NOR flash, Wi-Fi 6 via an integrated ESP32-C6 co-processor, MIPI-DSI/CSI interfaces, multiple hardware SPI buses, and SDIO 3.0 for the SD card. The question is whether those capabilities can be brought to bear inside the PicoCalc's physical and electrical constraints.

This note records the complete investigation — the pin mapping, the GPIO budget, the power analysis, the firmware porting strategy, and the concrete results of attempting to boot ESP-IDF on the actual hardware. It is written to be useful to anyone evaluating the same board for a similar peripheral-replacement project, not only for the PicoCalc.

## The PicoCalc's current hardware

The ClockworkPi PicoCalc is a handheld device built around a Raspberry Pi Pico. It provides a 4-inch 320×320 IPS LCD, a full QWERTY keyboard driven by an STM32 southbridge over I²C, a full-size SD card slot, dual PWM speakers, and 8 MB of PSRAM accessible through the Pico's PIO peripheral. Power comes from USB-C or an internal 18650 Li-ion cell, managed by an AXP2101 power management IC.

The PicoCalc hardwires specific Pico GPIOs to each peripheral. The following table is the ground truth for any replacement effort, verified from the PiPAPo project's hardware specification and the official ClockworkPi firmware sources.

### PicoCalc pin map

| Interface | Signal | Pico Pin | Notes |
|-----------|--------|----------|-------|
| SPI1 | SCK | GP10 | LCD clock |
| SPI1 | MOSI | GP11 | LCD data (no MISO needed — write-only display) |
| GPIO | LCD CS | GP13 | LCD chip select |
| GPIO | LCD DC | GP14 | LCD data/command |
| GPIO | LCD RST | GP15 | LCD reset |
| I2C1 | SDA | GP6 | Keyboard southbridge SDA |
| I2C1 | SCL | GP7 | Keyboard southbridge SCL |
| SPI0 | MISO | GP16 | SD card data out |
| GPIO | SD CS | GP17 | SD card chip select |
| SPI0 | SCK | GP18 | SD card clock |
| SPI0 | MOSI | GP19 | SD card data in |
| GPIO | SD CD | GP22 | SD card detect (active low) |
| PIO | PSRAM SIO0 | GP2 | PSRAM quad data 0 |
| PIO | PSRAM SIO1 | GP3 | PSRAM quad data 1 |
| PIO | PSRAM SIO2 | GP4 | PSRAM quad data 2 |
| PIO | PSRAM SIO3 | GP5 | PSRAM quad data 3 |
| PIO | PSRAM CS | GP20 | PSRAM chip select |
| PIO | PSRAM SCK | GP21 | PSRAM clock |
| PWM | Audio L | GP26 | Left speaker |
| PWM | Audio R | GP27 | Right speaker |
| UART0 | TX | GP0 | Serial TX to USB-C bridge |
| UART0 | RX | GP1 | Serial RX from USB-C bridge |
| GPIO | LED | GP25 | On-board LED |

### The southbridge I²C protocol

The keyboard southbridge is an STM32 co-processor at I²C address `0x1F`. The bus speed is 10 kHz — not a typo. The PicoCalc's firmware polls this device for key events. The protocol works as follows: read register `0x04` (key FIFO status), check the FIFO count in bits 0–4, then read 2 bytes from register `0x09` (FIFO data) for each event. Byte 0 is the key state (1 = pressed, 2 = hold/repeat, 3 = released); byte 1 is the key code (ASCII for printable keys, special codes for function keys, arrows, and modifiers).

The 10 kHz bus speed is a hard constraint. Any replacement MCU must be able to operate the I²C bus at this speed reliably. No hardware reset pin exists for the STM32; the firmware should allow approximately 100 ms after I²C initialization before polling.

### The LCD controller

The PicoCalc's LCD uses an ST7365P controller (marketed as ILI9488-compatible). It connects via SPI at approximately 33 MHz. The display is 320×320 pixels in RGB565 format. The initialization sequence requires a vendor unlock command: `0xF0` with data bytes `0xC3` and `0x96` to enable RGB565 over 4-wire SPI. Without this unlock, the `COLMOD` command (setting pixel format to `0x55`) is silently ignored. Display inversion must be enabled (command `0x21`) for correct colour polarity. The MADCTL register should be set to `0x48` (MX | BGR).

## The Waveshare ESP32-P4-WIFI6 board

The Waveshare ESP32-P4-WIFI6 is a development board built around the ESP32-P4NRW32 chip — a dual-core 360 MHz RISC-V processor with 32 MB of stacked PSRAM and 32 MB of external NOR flash. An ESP32-C6 co-processor on the same board provides Wi-Fi 6 and BLE 5 connectivity over an SDIO interface. The board also includes an ES8311 audio codec with I²S interface, a speaker amplifier, a MicroSD card slot on SDMMC 4-bit, a MIPI-DSI display connector, a MIPI-CSI camera connector, and a CH343P USB-to-UART bridge for the console.

### GPIO availability on the headers

The ESP32-P4 chip has 55 GPIOs total. Many are consumed by on-board peripherals, but all of those run on internal traces — they do not reach the user headers. The board exposes 25 GPIOs across two 2×20 pin headers, and every one of them is available for the PicoCalc project.

The following two tables list every pin on both headers, from the USB-C/SD-card edge (top) toward the ESP32-C6 module (bottom).

#### Left header

| Pin | GPIO | Notes |
|-----|------|-------|
| 1 | GPIO52 | |
| 2 | GPIO51 | |
| 3 | GND | |
| 4 | GPIO31 | SPI2 IO-MUX direct (Q_PAD) |
| 5 | GPIO30 | SPI2 IO-MUX direct (CK_PAD) |
| 6 | GPIO29 | SPI2 IO-MUX direct (D_PAD) |
| 7 | GPIO28 | SPI2 IO-MUX direct (CS_PAD) |
| 8 | GND | |
| 9 | GPIO50 | |
| 10 | GPIO49 | |
| 11 | GPIO5 | LP_IO — deep-sleep wake capable |
| 12 | GPIO4 | JTAG MTMS default (using disables JTAG) |
| 13 | GND | |
| 14 | GPIO3 | JTAG MTDI default |
| 15 | GPIO2 | JTAG MTCK default |
| 16 | GPIO8 | I²C0 SCL — shares bus with on-board ES8311 codec at 0x18 |
| 17 | GPIO7 | I²C0 SDA — shares bus with on-board ES8311 codec at 0x18 |
| 18 | GND | |
| 19 | GPIO24 | USB Serial/JTAG D− default |
| 20 | GPIO25 | USB Serial/JTAG D+ default |

#### Right header

| Pin | GPIO/Signal | Notes |
|-----|------------|-------|
| 1 | VBUS | +5 V input |
| 2 | VSYS | +5 V battery/external |
| 3 | GND | |
| 4 | EN | CHIP_PU — hold low for reset |
| 5 | 3V3 | 3.3 V output from on-board LDO (≤500 mA) |
| 6 | GPIO20 | |
| 7 | GPIO21 | |
| 8 | GND | |
| 9 | GPIO22 | |
| 10 | GPIO23 | |
| 11 | RUN | System reset button net |
| 12 | GPIO26 | |
| 13 | GND | |
| 14 | GPIO27 | |
| 15 | GPIO32 | |
| 16 | GPIO33 | |
| 17 | GPIO46 | GND pad between GPIO46 and GPIO47 — multi-pin housings short |
| 18 | GND | Between GPIO46/GPIO47 |
| 19 | GPIO47 | Same GND warning as GPIO46 |
| 20 | GPIO48 | |

### On-board peripheral GPIO commitments (internal traces only)

These GPIOs are committed by the Waveshare board design and cannot be reassigned. None of them appear on the user headers.

| Peripheral | GPIOs |
|-----------|-------|
| ESP32-C6 SDIO (Wi-Fi 6) | GPIO6, GPIO14–GPIO19, GPIO54 |
| I²S0 codec (ES8311) | GPIO9–GPIO13 |
| SDMMC (TF card, 4-bit) | GPIO39–GPIO44 |
| CH343P UART console | GPIO35, GPIO37, GPIO38 |
| USB 2.0 HS PHY | chip pins 49/50 (dedicated) |
| Speaker amp (NS4150B) | GPIO53 |
| BOOT strapping | GPIO0 (not on header) |

### GPIO category summary

**18 GPIOs with no caveats:** GPIO2–5, GPIO20–23, GPIO26–27, GPIO32–33, GPIO46–49, GPIO51–52

**2 GPIOs sharing I²C0 with the on-board codec:** GPIO7 (SDA), GPIO8 (SCL). The ES8311 codec at address 0x18 is always present on this bus. PicoCalc's keyboard southbridge at address 0x1F can share the bus without address collision, but the keyboard's 10 kHz speed must coexist with the codec's expected clock rate.

**5 GPIOs with JTAG/USB defaults:** GPIO2–4 default to JTAG signals; GPIO24–25 default to USB Serial/JTAG. Using any of these as general-purpose IO disables JTAG-via-USB-Serial. Since the board has a CH343P UART console and the C6 debug header for flashing, losing USB JTAG is acceptable for most development.

## Proposed pin mapping

The mapping below assigns PicoCalc peripheral signals to ESP32-P4 header GPIOs. It prioritizes the LCD on SPI2's IO-MUX direct pins for maximum SPI throughput, and routes the keyboard to the shared I²C0 bus.

### Primary peripherals

| PicoCalc Net | Pico Pin | ESP32-P4 Pin | Header | Rationale |
|-------------|----------|-------------|--------|-----------|
| LCD SCK | GP10 | GPIO30 | left | SPI2_CK_PAD — IO-MUX direct, up to 80 MHz |
| LCD MOSI | GP11 | GPIO29 | left | SPI2_D_PAD — IO-MUX direct |
| LCD CS | GP13 | GPIO28 | left | SPI2_CS_PAD — IO-MUX direct |
| LCD DC | GP14 | GPIO31 | left | SPI2_Q_PAD — IO-MUX direct, used as GPIO |
| LCD RST | GP15 | GPIO49 | left | Plain GPIO output |
| LCD BL | — | GPIO50 | left | LEDC PWM for backlight control |
| I²C SDA | GP6 | GPIO7 | left | I²C0 SDA, shared with ES8311 codec |
| I²C SCL | GP7 | GPIO8 | left | I²C0 SCL, shared with ES8311 codec |
| Audio L | GP26 | GPIO27 | right | LEDC PWM output |
| Audio R | GP27 | GPIO32 | right | LEDC PWM output |
| UART TX | GP0 | GPIO37 | internal | CH343P console TX (P4 → PC) |
| UART RX | GP1 | GPIO38 | internal | CH343P console RX (PC → P4) |

### SD card decision

The Waveshare board has its own MicroSD slot on SDMMC 4-bit (GPIO39–GPIO44), which runs at SDIO 3.0 speeds — far faster than the PicoCalc's SPI-mode SD. Two options exist:

1. **Use the Waveshare onboard SD only.** No additional GPIOs consumed. Much faster I/O. The PicoCalc's external SD slot becomes unusable. This is the recommended path for first bring-up.

2. **Wire the PicoCalc SD slot via SPI3.** Consumes 5 header GPIOs (for example: GPIO46 MISO, GPIO47 CS, GPIO48 SCK, GPIO33 MOSI, GPIO52 card detect). SPI3 through the GPIO matrix works at approximately 40 MHz, which is slower than the onboard SDMMC but retains the user-accessible SD slot. The right-header GND between GPIO46 and GPIO47 makes multi-pin Dupont housings dangerous — use individual jumpers.

### PSRAM — skip for all revisions

The PicoCalc's 8 MB PSRAM (GP2–GP5, GP20–GP21 via PIO) should be left unconnected. The ESP32-P4-WIFI6 already provides 32 MB PSRAM on a hardware HEX-SPI bus inside the chip package. There is no need for external PSRAM, and the RP2040 PIO bit-bang driver is not portable to ESP32-P4.

## Power considerations

Power is the single highest-risk area of this project. The PicoCalc was designed for the RP2040/RP2350 power envelope (approximately 50–100 mA typical, 150 mA peak). The ESP32-P4-WIFI6 can draw 200–350 mA with the HP dual-core active and PSRAM in use, and the ESP32-C6 adds 70–100 mA during Wi-Fi transmit bursts. Peak total current could reach 400–500 mA.

### PicoCalc power architecture

USB-C VBUS feeds an AXP2101 power management IC. An 18650 Li-ion battery feeds AXP2101 VBAT. The AXP2101 regulates to VSYS (approximately 5 V) for the Pico and peripherals. The Pico's on-board LDO or SMPS generates 3.3 V. All peripherals operate at 3.3 V I/O levels.

### Recommended power approach

- Feed the ESP32-P4-WIFI6's VIN from PicoCalc VSYS (the 5 V rail).
- Maintain a common ground between PicoCalc and ESP32-P4.
- Do not tie PicoCalc 3V3 and ESP32-P4 SOC_3V3 together — verify regulator topology and backfeed behaviour first.
- Both sides use 3.3 V I/O levels; ESP32-P4 VDD I/O recommended range is up to 3.6 V, matching PicoCalc peripherals.
- Bring out CHIP_EN and BOOT button access on the adapter board for reset and download mode entry.

Before designing an adapter PCB, measure PicoCalc VSYS voltage and current capacity under all power states: USB-C powered with battery full, battery only, battery low, and each power-switch position. If VSYS is not a clean 5 V under all conditions, add a buck-boost regulator on the adapter.

## Firmware migration

### Current firmware stack (Pico SDK)

The existing PicoCalc firmware (`pico-sdk-picocalc-wm`) uses Pico SDK C/C++ with the following hardware abstractions:

- `hardware_spi` for SPI1 (LCD) and SPI0 (SD card)
- `hardware_i2c` for I2C1 (keyboard southbridge)
- `hardware_gpio` for LCD control signals and SD card detect
- `hardware_pwm` for dual-channel audio
- UART0 for serial console
- PIO for PSRAM access (not needed on ESP32-P4)

### Target firmware stack (ESP-IDF)

ESP32-P4 Arduino support is still preliminary (arduino-esp32 issue #10278, merged in release/v3.1.x with basic functions only). Waveshare explicitly recommends ESP-IDF for ESP32-P4 development. The firmware must be built with ESP-IDF.

| Pico SDK API | ESP-IDF equivalent |
|-------------|-------------------|
| `hardware_spi` | `esp_lcd_panel_io_spi_config_t` or `spi_device_interface_config_t` |
| `hardware_i2c` | `i2c_master_driver` (ESP-IDF v6.x) or legacy `i2c_driver` |
| `hardware_gpio` | `gpio_config()` / `gpio_set_level()` |
| `hardware_pwm` | `ledc_channel_config()` (LEDC PWM controller) |
| `pico_stdlib` UART | ESP-IDF UART0 console via CH343 bridge on GPIO37/GPIO38 |
| `hardware_flash` | `esp_partition` / `nvs_flash` |
| FatFS (SPI SD) | `esp_vfs_fat_sdmmc_format` or `esp_vfs_fat_sdspi_format` |
| PIO PSRAM | Not needed — ESP32-P4 PSRAM managed by MMU/heap |

### Firmware port phases

**Phase 1 — Blink and console (bring-up).** Create an ESP-IDF project skeleton, configure the target as `esp32p4`, enable PSRAM in HEX mode at 200 MHz, and flash a minimal firmware that prints boot information and blinks a GPIO. This phase confirms that the toolchain, flash, PSRAM, and console all function on the actual hardware.

**Phase 2 — LCD driver.** Implement SPI2 LCD output using `esp_lcd_panel_io_spi` with the ST7365P/ILI9488 initialization sequence (including the vendor unlock at command `0xF0`). Allocate the framebuffer in PSRAM and flush via DMA. Test by filling the screen with colour bars.

**Phase 3 — Keyboard southbridge.** Implement I²C0 master driver at 10 kHz. Poll register `0x04` for FIFO status and register `0x09` for key events. Map key codes to the existing key code table. This phase must handle the shared I²C bus with the ES8311 codec — verify that the 10 kHz speed does not disrupt codec operation.

**Phase 4 — SD card.** Mount the onboard SDMMC slot (SDIO 4-bit, fastest path) or optionally wire the PicoCalc SPI SD slot. Verify FatFS read/write.

**Phase 5 — Audio.** Configure two LEDC PWM channels for the PicoCalc speaker path. Test with tone generation.

**Phase 6 — Window manager port.** Port the `pico-sdk-picocalc-wm` UI framework (text grid, line editor, terminal pane, app registry) from Pico SDK to ESP-IDF. Leverage PSRAM for large framebuffers and display lists.

**Phase 7 — New capabilities.** Enable Wi-Fi 6 via ESP-Hosted (ESP32-C6 SDIO slave), MIPI-DSI display, camera input via MIPI-CSI, and BLE peripherals.

## Phase 1 results — actual hardware bring-up

The firmware was created as `0097-esp32-p4-picocalc-bringup` under the existing ESP32-S3/M5 workspace, targeting ESP-IDF v5.4.2 with the following `sdkconfig.defaults`:

```
CONFIG_IDF_TARGET="esp32p4"
CONFIG_ESP_CONSOLE_UART_DEFAULT=y
CONFIG_IDF_EXPERIMENTAL_FEATURES=y
CONFIG_SPIRAM=y
CONFIG_SPIRAM_MODE_HEX=y
CONFIG_SPIRAM_SPEED_200M=y
CONFIG_ESPTOOLPY_FLASHSIZE_32MB=y
```

The firmware prints chip revision, flash size, PSRAM size, internal RAM, and performs a 1 MB PSRAM write/read integrity test. It blinks GPIO49 on the left header at 1 Hz.

### Build and flash

```bash
source ~/esp/esp-idf-5.4.2/export.sh
idf.py set-target esp32p4
idf.py build
idf.py -p /dev/ttyACM1 flash
```

The build succeeded without errors. The flash command reported:

```
Chip is ESP32-P4 (revision v1.3)
Features: High-Performance MCU
Crystal is 40MHz
MAC: e8:f6:0a:e0:ec:9f
```

### Chip revision

The board carries **ESP32-P4 revision v1.3** (eco2 ROM, July 2024). According to the ESP-IDF COMPATIBILITY.md, revisions v1.0 and v1.3 are supported since ESP-IDF v5.3. ESP-IDF v5.4.2 includes this support. The Kconfig setting `CONFIG_ESP32P4_REV_MIN_FULL=1` (minimum revision v1.0) and `CONFIG_ESP32P4_REV_MAX_FULL=199` (maximum revision v1.99) are compatible with v1.3 silicon.

### Serial console model

The first serial interpretation was wrong. The Linux device visible during the bring-up was not the ESP32-P4 native USB Serial/JTAG device. It was the board's external WCH/QinHeng USB serial bridge:

```text
Bus 003 Device 034: ID 1a86:55d3 QinHeng Electronics USB Single Serial
/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B61091051-if00 -> ../../ttyACM1
```

That distinction matters because ESP-IDF has multiple console backends. Selecting the wrong backend can produce a confusing split: ROM output appears, then application output disappears. The ROM prints through UART0. If ESP-IDF is configured for native USB Serial/JTAG, the application logs move away from the CH343 bridge. The serial capture then shows only the early ROM/loader lines, even though the application may be running correctly.

For this Waveshare board, the correct development console is the CH343 bridge wired to ESP32-P4 UART0:

| Board path | ESP32-P4 function | GPIO |
|-----------|-------------------|------|
| CH343 RX input | UART0 TX from ESP32-P4 | GPIO37 |
| CH343 TX output | UART0 RX into ESP32-P4 | GPIO38 |

ESP-IDF v5.4.2's ESP32-P4 SoC definitions confirm the same mapping:

```text
UART_NUM_0_TXD_DIRECT_GPIO_NUM = 37
UART_NUM_0_RXD_DIRECT_GPIO_NUM = 38
```

Therefore the correct `sdkconfig.defaults` console block is:

```text
# Console: UART via CH343 bridge on ESP32-P4 UART0
# CH343 USB CDC device appears as /dev/ttyACM* on Linux.
# CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG is not set
CONFIG_ESP_CONSOLE_UART_DEFAULT=y
```

This is not a workaround for a broken chip. It is the board's normal USB serial path. GPIO24/GPIO25 may still expose ESP32-P4 USB Serial/JTAG functions on the headers, but the USB cable used during this bring-up enumerated the CH343 bridge, not a native Espressif USB console.

### Why the earlier monitor attempts failed

Three independent issues were mixed together.

First, `CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y` routed application logs to a console backend that was not the connected `/dev/ttyACM1` device. The ROM boot lines still appeared because they come from UART0 before ESP-IDF takes over.

Second, `idf.py monitor` was started from a non-TTY shell. ESP-IDF's monitor needs standard input attached to a real terminal because it handles key sequences, reset shortcuts, and serial input. From the non-interactive shell it failed with:

```text
Monitor requires standard input to be attached to TTY
```

Third, a raw `cat /dev/ttyACM1` process was left running in the background. That process held the port and caused later flash attempts to fail with a port-busy error. On ESP32-S3/ESP32-P4 USB serial paths this kind of stale owner creates misleading symptoms: write timeouts, missing logs, failed prompt detection, and false suspicions of crashes.

The correct operating rule is simple: one process owns `/dev/ttyACM1` at a time. Before flashing or probing, check:

```bash
lsof /dev/ttyACM1 || true
```

### Controlled reset-and-capture

The reliable capture procedure was to avoid `idf.py monitor` entirely for one test and use `pyserial` directly. The script opened the CH343 CDC device, configured 115200 baud, deasserted BOOT/IO0 through DTR, pulsed EN through RTS, then captured all output for eight seconds.

```python
import serial, time, sys

ser = serial.Serial('/dev/ttyACM1', 115200, timeout=0.05)
ser.reset_input_buffer()

ser.dtr = False  # IO0 high: normal boot, not download mode
ser.rts = True   # EN low: hold chip in reset
time.sleep(0.12)
ser.rts = False  # EN high: release reset and boot app

start = time.time()
while time.time() - start < 8:
    data = ser.read(4096)
    if data:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()

ser.close()
```

This capture proved that the app was not crashing. The output contained the ROM log, second-stage bootloader, PSRAM setup, CPU start, `app_main()`, the bring-up banner, the PSRAM write/read test, and the GPIO blink task startup.

Important excerpts:

```text
ESP-ROM:esp32p4-eco2-20240710
Build:Jul 10 2024
rst:0x1 (POWERON),boot:0x30f (SPI_FAST_FLASH_BOOT)
SPI mode:DIO, clock div:1
load:0x4ff33ce0,len:0x15f0
load:0x4ff2abd0,len:0xd88
load:0x4ff2cbd0,len:0x3310
entry 0x4ff2abda
I (25) boot: ESP-IDF v5.4.2 2nd stage bootloader
I (27) boot: chip revision: v1.3
I (40) boot.esp32p4: SPI Flash Size : 32MB
```

The PSRAM initialization was also clean:

```text
I (376) esp_psram: Found 32MB PSRAM device
I (377) esp_psram: Speed: 200MHz
I (1333) esp_psram: SPI SRAM memory test OK
I (1412) esp_psram: Adding pool of 32768K of PSRAM memory to heap allocator
```

The application then reached `app_main()` and printed the bring-up diagnostics:

```text
I (1466) main_task: Calling app_main()
I (1466) bringup: Booting...
I (1476) bringup: ESP32-P4-WIFI6 PicoCalc Bring-Up
I (1486) bringup: Chip: esp32p4 rev 1.3
I (1486) bringup: Cores: 2 (HP dual-core RISC-V)
I (1486) bringup: CPU freq: 360 MHz
I (1496) bringup: Flash: 32 MB (OK — 32MB)
I (1496) bringup: PSRAM: 32768 KB total, 32765 KB free
I (1506) bringup: PSRAM: OK — 32MB stacked
I (1506) bringup: Internal RAM: 630 KB total, 580 KB free
I (1576) bringup: PSRAM: 1MB write/read test PASSED
I (1576) bringup: blink: starting on GPIO49
I (1586) bringup: Phase 1 bring-up complete. LED blinking on GPIO49.
```

The phase result is therefore stronger than "flash succeeded". The chip boots the app image, initializes external PSRAM at the intended speed, allocates the PSRAM heap, passes an application-level memory test, and enters the GPIO blink loop.

### Remaining Phase 1 warning

One warning remains in the log:

```text
W (1422) spi_flash: Detected flash size > 16 MB, but access beyond 16 MB is not supported for this flash model yet.
```

The bootloader and application both report a 32 MB flash configuration, and the current application is far below 16 MB, so this warning does not block Phase 1. It does matter for future partition layouts. If a later firmware stores filesystem data, assets, or OTA slots above the 16 MB boundary, the flash model support must be verified before relying on that address range.

For the next phases, keep the partition table below 16 MB until this warning is resolved. That still leaves enough room for LCD, keyboard, SD, and audio bring-up.

## Networking experiment — ESP-Hosted webserver on the standalone board

The next useful test did not require the PicoCalc to be connected. The Waveshare board already contains the part of the system that is hardest to emulate in software: an ESP32-C6 radio connected to the ESP32-P4 host over SDIO. Validating that path early answers a different question from the LCD or keyboard work. It asks whether the P4 can initialize the C6, run the ESP-Hosted transport, expose the usual `esp_wifi_*` APIs through `esp_wifi_remote`, join a real Wi-Fi network, and serve TCP traffic through lwIP.

The result was a new firmware project:

```text
/home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/0098-esp32-p4-wifi6-webserver
```

This project is deliberately separate from `0097-esp32-p4-picocalc-bringup`. The `0097` firmware remains the minimal hardware sanity check. The `0098` firmware is the first networking application. It connects as a station using the default credentials requested during the session, starts an interactive UART console, and serves a small HTTP diagnostic site.

### Why ESP-Hosted is required

ESP32-P4 is a high-performance MCU, but it does not contain a native Wi-Fi radio. On the Waveshare ESP32-P4-WIFI6 board, Wi-Fi and BLE are provided by an onboard ESP32-C6 module. The P4 is the application host; the C6 is the radio/transport slave. The firmware therefore uses two managed Espressif components:

```yaml
dependencies:
  idf: '>=5.4'
  espressif/esp_hosted: 1.4.0
  espressif/esp_wifi_remote: 0.8.5
```

`esp_hosted` handles the host/slave transport. `esp_wifi_remote` presents the familiar `esp_wifi_*` API to the application. That distinction is important: the source code looks like ordinary ESP-IDF Wi-Fi code, but the radio operations are being forwarded to the C6 across SDIO.

### Waveshare-specific SDIO wiring

The Tab5 examples in the workspace already use ESP-Hosted, but their transport configuration cannot be copied directly. The Waveshare board uses a different SDIO pinout and a different reset polarity. The runtime log confirmed the final configuration:

```text
I (2814) sdio_wrapper: SDIO master: Data-Lines: 4-bit Freq(KHz)[40000 KHz]
I (2814) sdio_wrapper: GPIOs: CLK[18] CMD[19] D0[14] D1[15] D2[16] D3[17] Slave_Reset[54]
```

The corresponding board mapping is:

| ESP32-P4 GPIO | ESP32-C6 / SDIO signal |
|---|---|
| GPIO18 | SDIO CLK |
| GPIO19 | SDIO CMD |
| GPIO14 | SDIO D0 |
| GPIO15 | SDIO D1 |
| GPIO16 | SDIO D2 |
| GPIO17 | SDIO D3 |
| GPIO54 | C6 reset / EN, active-high from P4 firmware view |

The reset polarity is the non-obvious field. The Waveshare pinout source notes that P4 GPIO54 reaches the C6 EN path through board-level logic and must be treated as active-high from the P4 firmware point of view. Using the Tab5 active-low reset default is the kind of mistake that leads to SDIO command failures before application code has any useful network state.

The project records that wiring in `sdkconfig.defaults`:

```text
CONFIG_ESP_HOSTED_SDIO_RESET_ACTIVE_HIGH=y
# CONFIG_ESP_HOSTED_SDIO_RESET_ACTIVE_LOW is not set
CONFIG_ESP_HOSTED_SDIO_GPIO_RESET_SLAVE=54
CONFIG_ESP_HOSTED_SDIO_4_BIT_BUS=y
CONFIG_ESP_HOSTED_SDIO_BUS_WIDTH=4
CONFIG_ESP_HOSTED_SDIO_CLOCK_FREQ_KHZ=40000
CONFIG_ESP_HOSTED_SDIO_PIN_CLK=18
CONFIG_ESP_HOSTED_SDIO_PIN_CMD=19
CONFIG_ESP_HOSTED_SDIO_PIN_D0=14
CONFIG_ESP_HOSTED_SDIO_PIN_D1=15
CONFIG_ESP_HOSTED_SDIO_PIN_D2=16
CONFIG_ESP_HOSTED_SDIO_PIN_D3=17
```

### Application structure

The webserver app has four responsibilities.

First, it initializes NVS, `esp_netif`, the default event loop, and the `esp_wifi_remote` stack. The application calls `esp_wifi_init()`, `esp_wifi_set_mode(WIFI_MODE_STA)`, `esp_wifi_set_config()`, and `esp_wifi_start()` just as it would on a native Wi-Fi ESP32. The difference is in the linked components and Kconfig: those calls target the C6 radio through the remote Wi-Fi implementation.

Second, it connects to the default network:

```c
#define DEFAULT_WIFI_SSID      "yolobolo"
#define DEFAULT_WIFI_PASSWORD  "bring3248camera"
```

Third, it starts `esp_http_server` with three routes:

| Route | Purpose |
|---|---|
| `GET /` | Small HTML status page with JavaScript that fetches `/status`. |
| `GET /status` | JSON state: uptime, chip info, flash size, heap/PSRAM, Wi-Fi state, IP address. |
| `GET /api/ping` | Minimal machine-readable liveness endpoint returning `{"ok":true,"message":"pong"}`. |

Fourth, it starts an `esp_console` REPL over the CH343 UART backend. This gives the board an operator interface without adding a screen or keyboard yet. The implemented commands are intentionally small:

```text
help
wifi status
wifi scan
wifi reconnect
wifi set <ssid> [password]
wifi reconnect
```

The console is a useful midpoint between hard-coded credentials and a full provisioning UI. It lets the operator inspect Wi-Fi state and change runtime credentials while keeping the firmware simple.

### Build and flash result

The firmware built successfully under ESP-IDF v5.4.2. The final binary size was far below the 3 MB app partition:

```text
0098-esp32-p4-wifi6-webserver.bin binary size 0xaced0 bytes.
Smallest app partition is 0x300000 bytes. 0x253130 bytes (77%) free.
```

Flashing succeeded through the same CH343 UART bridge used for Phase 1:

```text
Chip is ESP32-P4 (revision v1.3)
MAC: e8:f6:0a:e0:ec:9f
Writing at 0x000ba6ad... (100 %)
Hash of data verified.
Leaving...
Hard resetting via RTS pin...
Done
```

### Runtime evidence

The boot log shows the same validated P4 fundamentals as Phase 1: v1.3 silicon, ESP-IDF v5.4.2, 32 MB flash configuration, and 32 MB PSRAM at 200 MHz. It then shows ESP-Hosted starting and the C6 transport coming up:

```text
I (1512) host_init: ESP Hosted : Host chip_ip[18]
I (1538) H_API: ESP-Hosted starting. Hosted_Tasks: prio:23, stack: 5120 RPC_task_stack: 5120
I (1654) transport: Attempt connection with slave: retry[0]
I (1654) transport: Reset slave using GPIO[54]
I (2814) sdio_wrapper: SDIO master: Data-Lines: 4-bit Freq(KHz)[40000 KHz]
I (2814) sdio_wrapper: GPIOs: CLK[18] CMD[19] D0[14] D1[15] D2[16] D3[17] Slave_Reset[54]
I (2924) transport: Received INIT event from ESP32 peripheral
I (2944) transport:     * WLAN
I (2964) transport: Slave chip Id[12]
```

The application then starts the HTTP server and console:

```text
I (4004) p4_web: starting HTTP server on port 80
Type 'help' to get the list of commands.
p4web>
I (5014) p4_web: console ready: try 'help' or 'wifi status'
```

Association took several attempts. The logs showed transient disconnect reasons `2` and `205` before the final successful association. This is not yet diagnosed, but the final result was good: the board connected to `yolobolo`, obtained a DHCP address, and printed the URLs.

```text
W (7764) p4_web: STA disconnected reason=2; retrying
W (10184) p4_web: STA disconnected reason=205; retrying
W (13614) p4_web: STA disconnected reason=2; retrying
W (16034) p4_web: STA disconnected reason=205; retrying
I (24674) p4_web: STA connected: ssid=yolobolo channel=1 authmode=3
I (25694) esp_netif_handlers: sta ip: 192.168.0.88, mask: 255.255.255.0, gw: 192.168.0.1
I (25694) p4_web: Browse:  http://192.168.0.88/
I (25704) p4_web: Status:  http://192.168.0.88/status
```

HTTP validation from the host succeeded:

```bash
curl -sS --max-time 5 http://192.168.0.88/api/ping
```

```json
{"ok":true,"message":"pong"}
```

The status endpoint returned full diagnostic state:

```json
{
  "ok": true,
  "project": "0098-esp32-p4-wifi6-webserver",
  "uptime_ms": 40280,
  "chip": {
    "target": "esp32p4",
    "revision": 103,
    "cores": 2
  },
  "flash": {
    "bytes": 33554432
  },
  "heap": {
    "internal_free": 494799,
    "psram_total": 33554432,
    "psram_free": 33549744
  },
  "wifi": {
    "mode": "sta",
    "state": "got_ip",
    "ssid": "yolobolo",
    "ip": "192.168.0.88",
    "retries": 0,
    "last_disconnect_reason": -1
  }
}
```

This proves the full network path: P4 application code, ESP-Hosted SDIO transport, C6 radio, DHCP on the LAN, HTTP serving, and host-side reachability.

### Build failures that shaped the implementation

Two failures are worth preserving because they clarify ESP-IDF mechanics.

The first CMake run failed because the project listed `esp_flash` as a component requirement. The source includes `esp_flash.h`, but the build-system component name is `spi_flash`:

```text
Failed to resolve component 'esp_flash' required by component 'main': unknown name.
```

The fix was to use `spi_flash` in `PRIV_REQUIRES`.

The second compile attempt failed around `MACSTR`/`MAC2STR` while the app was still SoftAP-first. The final implementation moved to STA-first per the corrected requirement and uses the Wi-Fi event logs that matter for this phase: STA connect/disconnect, DHCP IP, and retry state. The lesson is not that AP mode is wrong, but that the first networking app should match the intended operator workflow: serial console plus STA on the normal LAN.

### What this changes for the project

Networking is now no longer an unknown. The ESP32-P4-WIFI6 board can use its onboard C6 through ESP-Hosted on the documented Waveshare pins, and a P4 application can serve HTTP on the LAN. This gives future PicoCalc firmware a viable control-plane path even before the PicoCalc screen and keyboard are ported.

The next networking improvements are incremental rather than foundational:

- Persist console-provided Wi-Fi credentials in NVS.
- Add an endpoint for ESP-Hosted transport counters or C6 firmware identification if the API exposes it.
- Run a longer HTTP stability test and record whether reasons `2` and `205` recur.
- Add a simple benchmark endpoint or reuse the `0094` HTTP benchmark patterns.

## Open questions

1. **Physical fit.** The Waveshare ESP32-P4-WIFI6 board is larger than a Pico. It may not fit inside the PicoCalc case. Measurement or a test fit is needed before the adapter PCB becomes meaningful.

2. **Power budget.** Can the PicoCalc VSYS rail supply an additional 400–500 mA? Real measurements under USB power, battery power, low-battery state, and power-switch transitions are required before PCB design.

3. **I²C bus sharing.** The 10 kHz keyboard polling speed must coexist with the ES8311 codec on the shared I²C0 bus. The codec's minimum I²C clock rate is not documented in the sources examined; testing is required.

4. **PicoCalc SD slot.** Is the user-accessible SD card slot important enough to consume 5 header GPIOs, or is the Waveshare's onboard MicroSD slot sufficient? The onboard SDMMC path is faster and easier; the PicoCalc slot preserves the original physical user experience.

5. **ESP-Hosted Wi-Fi retry behavior.** The webserver firmware eventually connected successfully, but the first run showed transient disconnect reasons `2` and `205` before association completed. A longer stability test should determine whether this is normal startup behavior or a configuration/timing issue.

6. **Flash addressing above 16 MB.** ESP-IDF detected a 32 MB flash configuration but warned that access beyond 16 MB is not supported for the detected flash model yet. Future partition tables should stay below 16 MB until this is resolved or verified.

7. **Adapter board design.** A PCB that presents a Pico-compatible 2×20 header footprint while wiring signals to the Waveshare board's headers is needed. The design depends on the physical-fit, power, I²C, and SD-slot decisions above.

## Near-term next steps

1. Extend `0098-esp32-p4-wifi6-webserver` with NVS-backed credential storage so `wifi set ...` can persist across reboots.
2. Run a 10–30 minute HTTP stability test against `0098`, recording disconnect/reconnect behavior and whether reasons `2` or `205` recur.
3. Keep using `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B61091051-if00` or `/dev/ttyACM1` as the console path, with `lsof` checks before every flash/probe session.
4. Begin the display-facing hardware phase when ready: implement the SPI2 LCD driver on GPIO28–31 and verify the ST7365P/ILI9488 initialization sequence with colour-bar output.
5. Measure PicoCalc VSYS voltage and current capacity.
6. Check physical dimensions of the Waveshare board against the PicoCalc case interior.

## Working rules

- Always use ESP-IDF (not Arduino) for ESP32-P4 firmware development at this stage.
- Use the CH343 USB-UART bridge as the default console. On Linux it appears as `1a86:55d3 QinHeng Electronics USB Single Serial`, currently `/dev/ttyACM1`, and maps to ESP32-P4 UART0 on GPIO37/GPIO38.
- Do not assume that a `/dev/ttyACM*` device is native ESP32 USB Serial/JTAG. Check the USB vendor/product ID and `/dev/serial/by-id` symlink before choosing the ESP-IDF console backend.
- Treat `/dev/ttyACM1` as single-owner. Before flashing, monitoring, or scripted probing, run `lsof /dev/ttyACM1 || true` and kill stale readers such as `cat`, `idf.py monitor`, or previous pyserial probes.
- Use `idf.py monitor` only in a real terminal or tmux pane. For non-interactive automation, use a pyserial reset-and-capture script rather than `idf.py monitor`.
- When assigning GPIOs, check the adsb-p4 project's `board_pinout.md` for the authoritative board-level wiring data — but remember that its "current allocation" column is project-specific, not board-inherent.
- The right-header GND between GPIO46 and GPIO47 is a real physical trap. Never use a multi-pin Dupont housing across that region.
- Record the chip revision (v1.3) in all design decisions. Any ESP-IDF version or library that requires revision ≥ v3.0 will not work on this board without the "ignore maximum revision" eFuse burned.
- Keep early partition layouts below 16 MB until the ESP-IDF flash warning about >16 MB access is resolved.
- For ESP-Hosted networking on this Waveshare board, use SDIO CLK/CMD/D0-D3 GPIO18/19/14/15/16/17 and active-high C6 reset on GPIO54; do not copy Tab5 SDIO defaults.
- Treat `esp_wifi_*` calls on ESP32-P4 as remote-radio calls when `esp_wifi_remote` is enabled: the application code looks native, but the radio work runs on the C6 over ESP-Hosted.
