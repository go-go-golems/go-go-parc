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
---

# ESP32-P4-WIFI6 as PicoCalc MCU — Deep Technical Dive

This article documents a feasibility investigation and initial firmware bring-up for replacing the Raspberry Pi Pico (RP2040/RP2350) inside a ClockworkPi PicoCalc with a Waveshare ESP32-P4-WIFI6 development board. The investigation covers hardware compatibility, pin mapping, power analysis, firmware migration strategy, and the practical results of flashing and booting the first ESP-IDF firmware on the actual board.

> [!summary]
> 1. The Waveshare ESP32-P4-WIFI6 can replace the Pico in the PicoCalc, but not as a drop-in — an adapter PCB is required to remap peripheral connections.
> 2. The board exposes 25 GPIOs on two 2×20 headers, all available for the PicoCalc project; on-board peripherals (C6 SDIO, I²S codec, SDMMC, UART) consume only internal-trace GPIOs that never reach the headers.
> 3. The specific board received carries ESP32-P4 revision v1.3 silicon, which is supported by ESP-IDF 5.3+ but requires care with console selection — the USB Serial/JTAG console may not produce output on v1.x chips; UART via the on-board CH343P bridge is the safer default.

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
| `pico_stdlib` UART | `uart_driver_config` or USB Serial/JTAG console |
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

### Console output problem

The first attempt used USB Serial/JTAG as the console (`CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y`). The bootloader loaded and the ROM output appeared on `/dev/ttyACM1`, but the ESP-IDF application produced no console output after the bootloader entry point. The ROM boot log was:

```
ESP-ROM:esp32p4-eco2-20240710
Build:Jul 10 2024
rst:0x1 (POWERON),boot:0x30f (SPI_FAST_FLASH_BOOT)
SPI mode:DIO, clock div:1
load:0x4ff33ce0,len:0x15f4
load:0x4ff2abd0,len:0xcf4
load:0x4ff2cbd0,len:0x3324
entry 0x4ff2abda
```

After the `entry` line, nothing. The second stage bootloader and application did not produce any output on USB Serial/JTAG.

The `sdkconfig.defaults` was then switched to UART console via the CH343P bridge (`CONFIG_ESP_CONSOLE_UART_DEFAULT=y`). The firmware rebuilt and reflashed successfully. The serial console output is pending verification — the CH343P bridge appears on a different serial device than the USB Serial/JTAG CDC, and identifying the correct port requires checking `ls /dev/ttyUSB*` or `dmesg` after the board enumerates.

### Possible causes for the USB Serial/JTAG silence

1. **v1.3 silicon may have USB Serial/JTAG errata.** Early ESP32-P4 revisions are known to have USB-related issues. The CH343P UART path bypasses the chip's USB PHY entirely, making it the more reliable console path.

2. **GPIO24/GPIO25 strapping conflict.** These pins default to USB Serial/JTAG functions. If the board's strapping resistors or external signals interfere during boot, the USB Serial/JTAG interface may not initialize correctly.

3. **Application image revision check.** If the second stage bootloader detects a revision mismatch, it aborts silently — no output reaches any console. The Kconfig settings should allow v1.3, but a mismatch between the bootloader's maximum revision check and the actual chip revision would produce exactly this symptom.

## Open questions

1. **UART console verification.** The CH343P-based UART console has not been confirmed to produce output yet. The next step is to identify the correct `/dev/ttyUSB*` device and monitor it.

2. **Physical fit.** The Waveshare ESP32-P4-WIFI6 board is larger than a Pico. It may not fit inside the PicoCalc case. Measurement or a test fit is needed.

3. **Power budget.** Can the PicoCalc VSYS rail supply an additional 400–500 mA? Real measurements under all power states are required before PCB design.

4. **I²C bus sharing.** The 10 kHz keyboard polling speed must coexist with the ES8311 codec on the shared I²C0 bus. The codec's minimum I²C clock rate is not documented in the sources examined; testing is required.

5. **PicoCalc SD slot.** Is the user-accessible SD card slot important enough to consume 5 header GPIOs, or is the Waveshare's onboard MicroSD slot sufficient?

6. **Adapter board design.** A PCB that presents a Pico-compatible 2×20 header footprint while wiring signals to the Waveshare board's headers is needed. The design depends on the answers to the questions above.

## Near-term next steps

1. Verify UART console output on the CH343P serial device.
2. If UART works, confirm PSRAM detection, flash size, and GPIO blink in the serial log.
3. Measure PicoCalc VSYS voltage and current capacity.
4. Check physical dimensions of the Waveshare board against the PicoCalc case interior.
5. Begin Phase 2: implement the SPI2 LCD driver once the console is confirmed working.

## Working rules

- Always use ESP-IDF (not Arduino) for ESP32-P4 firmware development at this stage.
- Prefer the CH343P UART console over USB Serial/JTAG until the USB console is confirmed working on v1.3 silicon.
- When assigning GPIOs, check the adsb-p4 project's `board_pinout.md` for the authoritative board-level wiring data — but remember that its "current allocation" column is project-specific, not board-inherent.
- The right-header GND between GPIO46 and GPIO47 is a real physical trap. Never use a multi-pin Dupont housing across that region.
- Record the chip revision (v1.3) in all design decisions. Any ESP-IDF version or library that requires revision ≥ v3.0 will not work on this board without the "ignore maximum revision" eFuse burned.
