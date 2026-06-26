---
title: "PicoCalc Keyboard Reset and I2C Recovery: ESP32-P4 Host Investigation"
aliases:
  - PicoCalc Keyboard Reset Investigation
  - PicoCalc Keyboard I2C Recovery
  - ESP32-P4 Keyboard Bus Clear
  - PicoCalc BIOS 1.4 Keyboard Firmware
tags:
  - article
  - firmware
  - esp32-p4
  - picocalc
  - i2c
  - keyboard
  - recovery
  - investigation
status: active
type: article
created: 2026-06-25
repo: /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5
---

# PicoCalc Keyboard Reset and I2C Recovery: ESP32-P4 Host Investigation

This article documents an investigation into resetting and recovering the PicoCalc keyboard from an ESP32-P4 host. The keyboard is not a passive peripheral. It is a separate microcontroller that scans a key matrix and exposes its state over an I2C register interface. When the host's view of that interface diverges from the keyboard's state, the host loses input. The investigation tried to recover the bus without a power cycle, measured which approaches were safe, and produced a conservative committed recovery path. The article records the hardware contract, the failure modes observed, the approaches considered, and the working rules that follow from them.

The work took place on the `0102-esp32-p4-visual-quickjs-repl` firmware, which runs a visual QuickJS REPL and a small operating environment called PicoOS on the PicoCalc. The keyboard is central to that environment: every interactive surface, from the REPL editor to the launcher, depends on receiving key events. A wedged keyboard makes the whole device unusable even though the display and CPU keep running.

> [!summary]
> - The PicoCalc keyboard is an STM32F103 microcontroller accessed by the host over I2C at address `0x1F`. The host only reads and writes registers; it cannot directly reset the STM32.
> - Register `0x08` (`REG_ID_RST`) resets the keyboard MCU. Reading or writing it can hang the I2C bus and force a power cycle, especially on older keyboard firmware. Host code must not touch it during normal operation.
> - The keyboard firmware on this device reports `reg0e=[0x0e 0x01]`, which matches BIOS 1.4-compatible behavior, even though the version register `reg01` returns `0x00`.
> - An ESP-side GPIO I2C bus-clear was attempted and rejected. It wedged a previously responsive keyboard path with `ESP_ERR_INVALID_STATE`. The committed recovery tears down the ESP-IDF I2C master, holds host I2C quiet for 3.1 seconds so the STM32's own idle watchdog can reset its I2C slave, then recreates the master.
> - Hard keyboard wedges still require a physical PicoCalc power cycle. Future work should add single-flight recovery, diagnostic counter reset, and an explicitly guarded dangerous reset command.

## Why this note exists

The PicoCalc presents itself to a firmware developer as a single integrated device: a display, a keyboard, and a battery. That framing hides an important architectural fact. The keyboard is a separate computer with its own firmware, its own register map, and its own failure modes. Code that treats the keyboard as a simple I2C peripheral will eventually hit a state where the peripheral stops responding and the host cannot explain why.

This note exists because the investigation produced three pieces of knowledge that are not obvious from reading the host driver:

1. The register interface has a dangerous member (`0x08`) whose semantics changed across keyboard firmware versions. Treating it as a safe diagnostic register is wrong.
2. Host-side I2C recovery that works on generic buses can damage a healthy PicoCalc keyboard path on this specific ESP32-P4 adapter. The naive recovery is not free.
3. The keyboard firmware contains its own recovery logic that the host can trigger by staying quiet. This is the safe first recovery step, and it is the one the host should use by default.

The note is written for a reader who will maintain or extend the keyboard driver. It assumes familiarity with I2C, FreeRTOS tasks, and ESP-IDF, but it does not assume prior knowledge of the PicoCalc hardware.

## The hardware contract

### Three processors, one bus

The PicoCalc contains three processors that matter to a firmware developer:

| Processor | Role | Interface to host |
|-----------|------|-------------------|
| ESP32-P4 (host) | Runs user firmware, display, QuickJS, PicoOS | — |
| STM32F103 (keyboard MCU) | Scans key matrix, manages power, exposes key FIFO | I2C slave at `0x1F` |
| ILI9488 (display) | Drives the LCD panel | SPI |

The display is driven over SPI and is not part of this investigation. The keyboard MCU is the focus. The host talks to it exclusively over I2C. There is no dedicated reset GPIO from the host to the STM32. The host's only control channels are I2C register reads and writes.

The original PicoCalc design routed the keyboard to a Raspberry Pi Pico (RP2040) on `Wire1` (I2C1), using SDA on GP6 and SCL on GP7. The ESP32-P4 adapter used in this project maps those same PicoCalc southbridge positions to ESP32-P4 GPIOs:

```text
Pico physical pin  9 / GP6 / SDA1 -> ESP32-P4 GPIO50
Pico physical pin 10 / GP7 / SCL1 -> ESP32-P4 GPIO49
```

The host driver encodes this mapping directly:

```c
#define PICOCALC_KBD_I2C_SDA_GPIO      50
#define PICOCALC_KBD_I2C_SCL_GPIO      49
#define PICOCALC_KBD_I2C_SPEED_HZ      10000
#define PICOCALC_KBD_I2C_ADDR          0x1F
```

The bus speed of 10 kHz is deliberately slow. The original Pico firmware and the Arduino `arduino_picocalc_kbd` library both initialize `Wire` at this rate or leave it at the default. The host driver preserves the conservative speed.

### The register interface

The keyboard MCU exposes a small register file over I2C. The host selects a register by writing its address, then reads or writes data. A write bit (`0x80`) is OR'd into the register address byte to distinguish writes from reads. The register map, taken from the keyboard firmware source `reg.h`, is:

| Register | Name | Purpose | Safety |
|----------|------|---------|--------|
| `0x01` | `REG_ID_VER` | Firmware version | safe to read |
| `0x02` | `REG_ID_CFG` | Configuration flags | safe |
| `0x03` | `REG_ID_INT` | Interrupt status | safe |
| `0x04` | `REG_ID_KEY` | Key count + lock states | safe |
| `0x05` | `REG_ID_BKL` | Display backlight | safe |
| `0x06` | `REG_ID_DEB` | Debounce config | safe |
| `0x07` | `REG_ID_FRQ` | Poll frequency config | safe |
| `0x08` | `REG_ID_RST` | Reset | **dangerous** |
| `0x09` | `REG_ID_FIF` | Key FIFO | safe |
| `0x0A` | `REG_ID_BK2` | Keyboard backlight | safe |
| `0x0B` | `REG_ID_BAT` | Battery status | safe |
| `0x0C` | `REG_ID_C64_MTX` | C64 matrix read | safe |
| `0x0D` | `REG_ID_C64_JS` | Joystick bits | safe |
| `0x0E` | `REG_ID_OFF` | Power off (BIOS 1.4+) | safe to read |

The host driver only needs two registers for normal operation: `0x04` (`REG_ID_KEY`) to check whether any key events are queued, and `0x09` (`REG_ID_FIF`) to dequeue a key event. The status register's low five bits hold the FIFO count; bits 5 and 6 hold Caps Lock and Num Lock state:

```c
uint8_t picocalc_keyboard_fifo_count(uint8_t status)
{
    return status & PICOCALC_KBD_COUNT_MASK;  // 0x1F
}
```

Everything else is diagnostic or configuration. The host driver reads `0x04` first; if the count is zero it returns `ESP_ERR_NOT_FOUND` without touching the FIFO. If the count is nonzero it reads two bytes from `0x09`: the first byte is the key state, the second is the key code.

### The dangerous register

Register `0x08` is the keyboard MCU reset. The keyboard firmware handles it as follows:

```c
case REG_ID_RST: {
    if (is_write) {
        delay(rcv_data[1] * 1000);   // delay value seconds
    } else {
        delay(1000);                 // a read still delays 1s
    }
    NVIC_SystemReset();              // reset the STM32
} break;
```

Any access to `0x08` — read or write — ends in an `NVIC_SystemReset()`. A read delays one second first; a write delays the supplied number of seconds first. On older keyboard firmware (BIOS 1.2), this behavior was unreliable enough that reading `0x08` during a diagnostic register dump crashed the keyboard MCU, hung the I2C bus, and required a full power cycle. The uLisp PicoCalc investigation recorded this explicitly:

> Reading I2C register 0x08 (RST) crashed the keyboard MCU and hung the system. There is no protection in the uLisp I2C interface against reading dangerous registers. The fix is purely procedural: document which registers are safe and never probe 0x08.

The consequence is a hard rule: host code must not read or write `0x08` during normal operation. If a reset is ever needed, it must be an explicit operator action, not an automatic recovery step.

### Keyboard firmware versions

The keyboard firmware is what the PicoCalc community calls the "BIOS." There have been at least three released versions:

| Version | Register `0x01` value | Register `0x0E` value | Notes |
|---------|------------------------|------------------------|-------|
| BIOS 1.2 | `0x00` (unimplemented) | `0x00` | Original; uLisp-compatible |
| BIOS 1.4 | `0x14` | `0x01` | Adds power-off register; power button as keypress |
| BIOS 1.6 | `0x16` | `0x01` | Source defines `BIOSVERSION 0x16` |

BIOS 1.4 added the `0x0E` power-off register. A host writes a delay value (minimum 6 seconds) and the keyboard controller cuts power after that delay. This was added to support graceful Linux shutdown on PicoCalc units that use a Linux SBC instead of a Pico. BIOS 1.4 also changed the power button to emit a key event (`0x91`) instead of acting only as a hardware toggle.

The device under test reports:

```text
kbd version: ver_err=ESP_OK reg01=[0x00 0x00] off_err=ESP_OK reg0e=[0x0e 0x01] detected=0x00 BIOS 1.4-compatible
```

The version register `0x01` returns `0x00`, which is ambiguous (it could mean BIOS 1.2 or an unimplemented version field). The power-off register `0x0E` returns `0x01`, which is the BIOS 1.4 indicator. The combined probe classifies the keyboard as BIOS 1.4-compatible. This matters because the reset register's behavior is more reliable on 1.4+, but the historical crash evidence means the host still treats `0x08` as dangerous regardless of version.

## The host driver

### Structure

The host driver lives in `components/picocalc_keyboard/`. It is a C component with a thin C++ wrapper at the call sites. The state is held in file-scope statics protected by a FreeRTOS mutex:

```c
static i2c_master_bus_handle_t s_bus = NULL;
static i2c_master_dev_handle_t s_dev = NULL;
static SemaphoreHandle_t s_lock = NULL;
static bool s_initialized = false;
static volatile bool s_recovering = false;
static uint8_t s_last_status = 0;
static uint32_t s_error_count = 0;
static uint32_t s_recover_count = 0;
static esp_err_t s_last_error = ESP_OK;
```

The mutex serializes register access. The `s_recovering` flag prevents reinitialization during a recovery window. The counters feed a diagnostics struct that the console and visual REPL can display.

A register read is a two-phase I2C transaction: transmit the register address, wait, then receive the data:

```c
err = i2c_master_transmit(s_dev, &reg, 1, 50);
if (err != ESP_OK) { note_error(err); give_lock(); return err; }
vTaskDelay(pdMS_TO_TICKS(2));   // settle delay, matching Pico firmware
err = i2c_master_receive(s_dev, dst, len, 50);
```

The 2 ms settle delay is applied to all register reads, not just FIFO reads. It is harmless at diagnostic polling rates and avoids one special timing path during bring-up.

### The polling task

The firmware runs a dedicated keyboard task at priority 5 with a 12288-word stack:

```c
xTaskCreate(keyboard_task, "kbd0102", 12288, nullptr, 5, &g_keyboard_task);
```

The task polls the keyboard in a loop. When a poll returns `ESP_ERR_NOT_FOUND` (no event queued), it sleeps for a short delay and retries. When a poll returns a hard error, it counts consecutive errors and triggers recovery after a threshold:

```c
if (err != ESP_OK) {
    ++consecutive_errors;
    if (consecutive_errors == 5 || consecutive_errors % 30 == 0) {
        esp_err_t rec = picocalc_keyboard_recover();
        ESP_LOGW(kTag, "keyboard recovery after poll errors: %s", esp_err_to_name(rec));
    }
    const TickType_t delay = consecutive_errors < 5 ? pdMS_TO_TICKS(250) : pdMS_TO_TICKS(1000);
    vTaskDelay(delay);
    continue;
}
```

This loop is the source of a subtle concurrency problem that surfaced later. The task calls recovery automatically. A human operator can also call recovery through the `kbd recover` console command or the `/kbd recover` visual REPL command. Both paths call the same `picocalc_keyboard_recover()` function. When both run at once, they interleave their teardown and reinitialization steps, which produces misleading log output and can extend the recovery window.

## The failure mode

### Symptoms

The keyboard enters a wedged state in two observable ways:

1. **Soft wedge.** Polling returns `ESP_ERR_INVALID_STATE` repeatedly. The ESP-IDF I2C master driver believes the bus or device is not in a usable state, but the keyboard MCU is still alive. A recovery that reinitializes the master often fixes this.
2. **Hard wedge.** Polling returns `ESP_ERR_INVALID_STATE` and recovery does not restore communication. `kbd version` fails with `ESP_ERR_INVALID_STATE`. The keyboard MCU's I2C slave has stopped responding. This requires a physical PicoCalc power cycle.

The two are not always distinguishable from the host's perspective. Both report the same error code. The difference is whether a recovery succeeds.

### Causes observed during this investigation

Three causes were identified:

- **Touching register `0x08`.** A diagnostic register dump that includes `0x08` resets the STM32. On older firmware this hangs the bus. The historical uLisp crash and the firmware source both confirm this.
- **ESP-side GPIO bus clear.** Configuring the I2C pins as open-drain GPIOs and clocking SCL to release a stuck SDA line wedged a previously responsive keyboard path on this adapter. The details are in the next section. This was the cause of the hard wedge during this investigation.
- **Host driver state divergence.** The ESP-IDF I2C master's internal state can diverge from the hardware state if a transaction is interrupted or if the bus is accessed from two tasks without coordination. This produces `ESP_ERR_INVALID_STATE` without any hardware fault.

## The investigation

### Step 1: Identify the firmware version

Before changing recovery behavior, the investigation needed to know which keyboard firmware was running, because the reset register's reliability differs across versions. A `kbd version` console command was added to `cmd_kbd` in `app_main.cpp`:

```c
if (argc >= 2 && std::strcmp(argv[1], "version") == 0) {
    uint8_t ver[2] = {};
    uint8_t off[2] = {};
    esp_err_t ver_err = picocalc_keyboard_read_register(0x01, ver, sizeof(ver));
    esp_err_t off_err = picocalc_keyboard_read_register(0x0e, off, sizeof(off));
    const uint8_t bios = ver_err == ESP_OK ? ver[1] : 0;
    const char *label = "unknown";
    if (bios == 0x12 || (bios == 0 && off_err == ESP_OK && off[1] == 0)) label = "BIOS 1.2 or earlier";
    else if (bios == 0x14 || (bios == 0 && off_err == ESP_OK && off[1] == 1)) label = "BIOS 1.4-compatible";
    else if (bios == 0x16) label = "BIOS 1.6";
    // ...print...
}
```

The classification reads two bytes from each register because the keyboard firmware returns the register address in the first byte and the value in the second byte. The `0x01` value disambiguates 1.4 from 1.6 when populated; the `0x0E` value disambiguates 1.2 from 1.4 when `0x01` is unimplemented.

The probe confirmed the device is BIOS 1.4-compatible. This means the power-off register is present, but it does not mean the reset register is safe to use automatically. The historical crash evidence still applies.

### Step 2: Attempt GPIO I2C bus clear

The standard I2C bus recovery procedure is to configure SCL and SDA as open-drain GPIOs, clock SCL up to nine times to let a stuck slave finish the byte it thinks it is sending, then issue a STOP condition. This recovers a bus where a slave is holding SDA low mid-transaction.

An implementation was added to the driver:

```c
static esp_err_t bus_clear_locked(void)
{
    gpio_config_t cfg = {
        .pin_bit_mask = (1ULL << SDA) | (1ULL << SCL),
        .mode = GPIO_MODE_INPUT_OUTPUT_OD,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&cfg);

    gpio_set_level(SDA, 1);
    gpio_set_level(SCL, 1);
    esp_rom_delay_us(10);

    for (int i = 0; i < 16 && gpio_get_level(SDA) == 0; ++i) {
        gpio_set_level(SCL, 0);
        esp_rom_delay_us(10);
        gpio_set_level(SCL, 1);
        esp_rom_delay_us(10);
    }

    // STOP: SDA low while SCL high, then release SDA high
    gpio_set_level(SDA, 0);
    esp_rom_delay_us(10);
    gpio_set_level(SCL, 1);
    esp_rom_delay_us(10);
    gpio_set_level(SDA, 1);
    esp_rom_delay_us(10);

    gpio_reset_pin(SDA);
    gpio_reset_pin(SCL);
    return ESP_OK;
}
```

A `kbd bus-clear` command exposed it. The result was negative. On a healthy keyboard path, running `kbd bus-clear` caused all subsequent register reads to fail with `ESP_ERR_INVALID_STATE`:

```text
--- kbd version
kbd version: ver_err=ESP_OK reg01=[0x00 0x00] off_err=ESP_OK reg0e=[0x0e 0x01] detected=0x00 BIOS 1.4-compatible
--- kbd bus-clear
W: clearing PicoCalc keyboard I2C bus with GPIO pulses (attempt=1)
I: initialized PicoCalc keyboard I2C: sda=50 scl=49 speed=10000 addr=0x1f recoveries=0
kbd bus-clear: ESP_OK initialized=1 errors=1 bus_clears=1 last_error=ESP_ERR_INVALID_STATE
--- kbd version
kbd version: ver_err=ESP_ERR_INVALID_STATE reg01=[0x00 0x00] ... detected=0x00 unknown
```

The bus-clear reported `ESP_OK` because reinitializing the ESP-IDF master succeeded. But the keyboard MCU stopped responding. The master was alive; the slave was not.

The `gpio_reset_pin` calls were added to return the pads to reset state before the I2C driver reclaimed them. Leaving them as open-drain GPIOs made the I2C master appear initialized while transfers failed. The reset calls did not fix the underlying problem: the keyboard MCU itself had stopped responding to its I2C address.

This approach was removed from the committed code. The lesson is specific to this adapter: the ESP32-P4's GPIO matrix and the PicoCalc southbridge's I2C pull-up and protection circuitry do not tolerate the host bit-banging the I2C lines the way a generic I2C bus would. A safe GPIO bus clear on this hardware would require a lower-level pinmux and electrical review that was not available during this investigation.

### Step 3: Use the keyboard's own idle watchdog

The keyboard firmware source contains its own I2C slave recovery logic. In its main loop, it tracks the time of the last `receiveEvent` and `requestEvent` callbacks. If more than 2.5 seconds pass with no host I2C activity, it resets its own I2C slave:

```c
void loop() {
    check_pmu_int();
    keyboard_process();
    if (millis() > 10000) {
        if (((millis() - receiveEventTick) > 2500) || ((millis() - requestEventTick) > 2500)) {
            ResetI2CBus();
        }
    }
    check_hp_det();
    nbDelay_ms(10);
}
```

`ResetI2CBus()` ends the `Wire` slave, detaches the callbacks, waits, and reinitializes the slave on the same pins. This is the keyboard MCU resetting its own side of the bus without touching the host.

The host can trigger this path by staying quiet. The committed recovery does exactly that:

```c
esp_err_t picocalc_keyboard_recover(void)
{
    esp_err_t err = take_lock();
    if (err != ESP_OK) { note_error(err); return err; }

    ++s_recover_count;
    ESP_LOGW(TAG, "recovering ... (attempt=%u)", (unsigned)s_recover_count);
    s_recovering = true;
    teardown_locked();   // remove the ESP-IDF I2C master
    give_lock();

    // Let the keyboard STM32 firmware's internal idle watchdog reset its I2C
    // slave. The STM32 source resets Wire after ~2.5s without host I2C traffic.
    vTaskDelay(pdMS_TO_TICKS(3100));
    s_recovering = false;
    return picocalc_keyboard_init();
}
```

The 3.1-second delay exceeds the STM32's 2.5-second threshold with margin. The `s_recovering` flag blocks `picocalc_keyboard_init()` during the quiet window, so the polling task cannot accidentally re-create the master and start traffic before the watchdog has fired.

### Result of the quiet recovery

After a physical PicoCalc power cycle restored the keyboard, the quiet recovery was validated. The keyboard responded to version probes:

```text
--- kbd version
kbd version: ver_err=ESP_OK reg01=[0x00 0x00] off_err=ESP_OK reg0e=[0x0e 0x01] detected=0x00 BIOS 1.4-compatible
--- kbd 1
kbd: no event
```

`kbd 1` polls for one event and reports none, which confirms the poll path is functioning rather than hard-failing. The recovery does not fix every wedge — a hard keyboard MCU hang still needs a power cycle — but it is safe to run automatically and does not make a healthy path worse.

## Current state

The committed code is in two parts:

- `components/picocalc_keyboard/picocalc_keyboard.c` holds the quiet recovery and the `s_recovering` guard.
- `0102-esp32-p4-visual-quickjs-repl/main/app_main.cpp` holds the `kbd version`, `kbd status`, and `kbd recover` console commands, plus the `/kbd recover` visual REPL command.

The firmware builds and flashes. The binary is approximately 0x950 KB with 77% of the 4 MB app partition free. The keyboard task runs with a 12288-word stack.

The investigation left one unresolved problem. After the failed GPIO bus-clear experiment, the keyboard was hard-wedged. A physical PicoCalc power cycle (resetting the keyboard MCU, not the ESP32-P4) restored communication. The ESP-side error and recovery counters persisted across that reset because the ESP32-P4 itself did not reset:

```text
kbd status: initialized=1 last_status=0x00 errors=2634 recoveries=91 last_error=ESP_ERR_INVALID_STATE
```

These counters are stale relative to the current healthy state. They make diagnostics noisy because a reader cannot tell which errors are current and which are historical.

## Open questions

- **Does the quiet recovery fix soft wedges in practice?** It is safe and committed, but the investigation ended before a soft wedge could be reproduced and recovered in isolation. The validation so far is that it does not break a healthy path.
- **Is there a safe ESP-IDF native I2C recovery API for ESP32-P4?** ESP-IDF's I2C master driver may expose bus recovery primitives that do not require manual GPIO bit-banging. That path was not evaluated.
- **Should the host use register `0x08` for an explicit reset?** On BIOS 1.4+ the reset register is more reliable than on 1.2, but the historical crash evidence means it should remain an explicit operator action, never automatic.
- **How should the host detect a hard wedge?** The current code cannot distinguish "soft wedge that recovery will fix" from "hard wedge that needs a power cycle." Both report `ESP_ERR_INVALID_STATE`. A heuristic based on failed recovery count could surface a "power cycle required" diagnostic.

## Near-term next steps

1. **Add single-flight recovery.** A flag or mutex should prevent the polling task and a console `kbd recover` from running recovery at the same time. The logs from this investigation showed overlapping attempts (manual recover attempt 90, background task recover attempt 91).
2. **Add a diagnostic counter reset.** A `kbd diag-reset` command should clear `errors`, `recoveries`, and `last_error` so a fresh session can be observed without stale counts.
3. **Add an explicitly guarded dangerous reset command.** A command such as `kbd reset-mcu --i-understand` would write register `0x08` only when the operator confirms. It must never be called automatically.
4. **Re-evaluate GPIO bus clear with a pinmux review.** If host-side bus clear is still desired, it needs a lower-level pin and electrical review specific to the ESP32-P4 adapter, not the generic implementation that was rejected here.

## Working rules

- The keyboard is a separate microcontroller, not a passive peripheral. Treat it as one.
- Never read or write register `0x08` during normal operation. If a reset is needed, make it an explicit operator action with a confirmation flag.
- Do not bit-bang the I2C lines as GPIOs on this ESP32-P4 adapter. The generic I2C bus-clear procedure wedged a healthy keyboard path here.
- The first recovery step is to stop talking to the keyboard for longer than 2.5 seconds. Its firmware will reset its own I2C slave.
- A physical PicoCalc power cycle is the last resort for a hard wedge. Resetting the ESP32-P4 is not equivalent; the keyboard MCU has its own state.
- Recovery that reinitializes the host's I2C master can return `ESP_OK` while the keyboard MCU remains unresponsive. Always validate recovery with a register read, not just with the master's init status.

## Related notes

- [[ARTICLE - PicoCalc QuickJS DSL - Native and Portable Runtime Deep Dive]]
- [[ARTICLE - ESP32-S3 QuickJS HTTP and Fetch - From Firmware Static Serving to Host-Testable APIs]]
- [[ARTICLE - QuickJS Native Modules on ESP32-S3 - Implementing Firmware JavaScript Namespaces]]
