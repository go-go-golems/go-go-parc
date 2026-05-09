---
title: "Playbook: Building E-Ink Drawing Apps for the reMarkable Paper Pro"
aliases:
  - reMarkable Paper Pro drawing playbook
  - eink drawing playbook
  - Paper Pro pen app guide
tags:
  - article
  - playbook
  - remarkable
  - eink
  - qt
  - evdev
  - cross-compilation
  - stylus
status: active
type: article
created: 2026-04-06
repo: /home/manuel/code/wesen/2026-04-06--paper-pro-pen-prob
---

# Playbook: Building E-Ink Drawing Apps for the reMarkable Paper Pro

This article is a reusable playbook for anyone who wants to build a pen-aware drawing or note-taking application for the reMarkable Paper Pro (model rm510, codenamed "ferrari"). It captures everything we learned building [[PROJ - Paper Pro Pen Probe - reMarkable E-Ink Drawing and Pen Input]] — the hard-won knowledge about the epaper plugin, pen input, cross-compilation, deployment, and rendering that is not documented anywhere else.

> [!summary]
> The four most important things to know:
> 1. **The Paper Pro's epaper Qt plugin does not dispatch `QTabletEvent`.** You must read the marker device directly via evdev. There is no workaround.
> 2. **Cross-compilation uses the Ferrari SDK** — an OpenEmbedded/Yocto toolchain that sources an `environment-setup-*` script to set the cross-compiler and sysroot.
> 3. **Touch works out of the box** via the epaper plugin. Only pen/marker input requires special handling.
> 4. **E-ink rendering needs damage-region optimization** — full repaints on every pen sample are too slow for responsive drawing.

## Why this note exists

The reMarkable developer portal provides a "Hello reMarkable" example that demonstrates touch input. The portal explicitly states: "Touch event handling works out of the box, while handling the marker is more involved and not shown here." There are essentially no public examples of QML-based pen/drawing apps for the Paper Pro because the proprietary xochitl app reads the pen device directly and doesn't share its approach.

This playbook exists to fill that gap with concrete, tested knowledge.

## When to use this pattern

Use this playbook when:

- You are building a Qt Quick / QML application for the reMarkable Paper Pro (rm510)
- Your app needs to receive marker/pen/stylus input
- You need to render ink strokes on the e-ink display with acceptable latency
- You are cross-compiling from an x86_64 Linux host to ARM aarch64

## Core mental model

The Paper Pro runs a custom Linux distribution called "codex" with a custom Qt platform plugin called `epaper`. The hardware has two separate input devices on the same Elan SPI digitizer chip:

```text
┌─────────────────────────────────────────────┐
│              reMarkable Paper Pro             │
│                                               │
│  Elan SPI Digitizer                           │
│    ├── event2: "Elan marker input"            │
│    │     protocol: single-touch (ABS_X/Y)     │
│    │     udev: ID_INPUT_TABLET=1              │
│    │     axes: X, Y, Pressure, TiltX, TiltY   │
│    │     buttons: BTN_TOOL_PEN, BTN_TOOL_RUBBER│
│    │                                          │
│    └── event3: "Elan touch input"             │
│          protocol: multi-touch (ABS_MT_*)     │
│          udev: ID_INPUT_TOUCHSCREEN=1         │
│                                               │
│  epaper plugin (Qt platform)                   │
│    ├── discovers event3 ✓ (touchscreen)        │
│    ├── discovers event2 ✗ (not touchscreen)    │
│    ├── dispatches QTouchEvent ✓                │
│    └── dispatches QTabletEvent ✗ (missing)     │
│                                               │
│  Your app                                     │
│    ├── Touch → handled by epaper plugin        │
│    └── Pen → YOU must read event2 yourself     │
└─────────────────────────────────────────────┘
```

The epaper plugin's touch handler scans for `Device_Touchpad|Device_Touchscreen`. The marker device is tagged `Device_Tablet`, so it is invisible to the plugin. Even if the plugin detects pen events internally, it logs `"unable to dispatch pen event"` because the `handleTabletEvent` function does not exist in the binary.

## Architecture

### Recommended component layout

```text
┌──────────────────────────────────────────────────────┐
│                    Your QML App                       │
│                                                       │
│  ┌─────────────┐    ┌─────────────┐                  │
│  │ EvdevPen     │    │ InkSurface  │ ← QQuickPaintedItem│
│  │ Reader       │───→│ (renderer)  │                   │
│  │ reads event2 │    │             │                   │
│  └──────┬───────┘    └──────┬──────┘                   │
│         │                   │                          │
│         ▼                   ▼                          │
│  ┌─────────────┐    ┌─────────────┐                  │
│  │ Stroke      │    │ Session     │                  │
│  │ Engine      │    │ Recorder    │                  │
│  │ (ink model) │    │ (JSON/PNG)  │                  │
│  └─────────────┘    └─────────────┘                  │
│                                                       │
│  ┌─────────────┐                                     │
│  │ QML UI      │ ← MouseArea/TouchArea for buttons   │
│  │ (side panel)│ ← InkSurface for the canvas         │
│  └─────────────┘                                     │
└──────────────────────────────────────────────────────┘
```

### Signal flow for pen input

```text
/dev/input/event2
    │ (kernel evdev)
    ▼
EvdevPenReader (QSocketNotifier on main loop)
    │
    ├─→ penSample(PenSample) ─→ StrokeEngine::handleInkSample()
    │                                │
    │                                ▼
    │                           InkSurface::update() → paint()
    │
    └─→ penSample(PenSample) ─→ TabletProbe (telemetry for QML)
```

### Signal flow for touch input

```text
/dev/input/event3
    │ (kernel evdev)
    ▼
epaper plugin (EpaperEvdevTouchScreenHandler)
    │
    ▼
QTouchEvent → QML MouseArea → buttons, toggles, steppers
```

The two paths coexist without conflict.

## Common failure modes

### Failure 1: "My app runs but the pen doesn't do anything"

**Symptom:** Touch works, buttons work, but drawing with the Marker produces no ink.

**Cause:** You are listening for `QTabletEvent` via an event filter. The epaper plugin does not dispatch these events. Your event filter never fires.

**Fix:** Implement direct evdev reading of `/dev/input/event2`. See the [[#Core mental model]] section.

### Failure 2: "I opened /dev/input/event2 but get no events"

**Symptom:** `open()` succeeds but `read()` returns `EAGAIN` forever.

**Cause:** xochitl (or another process) already has the device open and is consuming events. Or you opened with `O_NONBLOCK` before the pen is in proximity.

**Fix:** Stop xochitl first (`systemctl stop xochitl`). Use `EVIOCGRAB` to get exclusive access. Use `QSocketNotifier` for async reads.

### Failure 3: "The pen draws but coordinates are wrong"

**Symptom:** Strokes appear offset, mirrored, or scaled incorrectly.

**Cause:** Raw evdev ABS values are in the digitizer's native resolution (typically 0–11180 for X, 0–15340 for Y) and must be mapped to screen pixels (1620×2160).

**Fix:** Query actual axis ranges with `EVIOCGABS` ioctl. Map with linear interpolation:
```
screenX = (rawX - absXMin) * SCREEN_WIDTH / (absXMax - absXMin)
screenY = (rawY - absYMin) * SCREEN_HEIGHT / (absYMax - absYMin)
```

### Failure 4: "Drawing is laggy / the display flickers"

**Symptom:** Each pen stroke causes a visible full-screen refresh with a flash.

**Cause:** You are calling `update()` (no rect) on every pen sample, which triggers a full canvas repaint. The epaper display controller must refresh the entire screen.

**Fix:** Use `update(const QRect&)` with only the bounding box of the new ink segment. See [[#E-ink rendering optimization]].

### Failure 5: "CMake can't find my headers in the generated QML registration code"

**Symptom:** `'MyType' was not declared in this scope` in `qmltyperegistrations.cpp`.

**Cause:** Qt's CMake integration generates code that uses `#include <MyType.h>` with angle brackets. If your headers are in a `src/` subdirectory, the compiler can't find them.

**Fix:** Add `target_include_directories(your_target PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)` to `CMakeLists.txt`.

### Failure 6: "QOverload<>::of(&MyItem::update) fails to compile"

**Symptom:** `no matching function for call to 'QOverload<>::of(...)'`.

**Cause:** In Qt 6.8.x, `QQuickPaintedItem::update()` has only one signature: `void update(const QRect &rect = QRect())`. A default argument does not create a separate overload in C++. `QOverload<>::of(...)` tries to match `void()` and fails.

**Fix:** Use a lambda: `[this]() { update(); }`.

## Anti-patterns

- **Don't use `QTabletEvent` on Paper Pro.** It will never fire. Use evdev directly.
- **Don't use `QThread` for reading evdev.** Use `QSocketNotifier` on the main loop — it's simpler and avoids thread-safety issues in the signal-slot chain.
- **Don't hard-code axis ranges.** Query them with `EVIOCGABS` at device open time. Different firmware versions may use different ranges.
- **Don't call `update()` without a rect on every pen sample.** Full repaints are extremely expensive on e-ink.
- **Don't forget to stop xochitl before running your app.** It occupies the display and may grab input devices.

## Recommended implementation sequence

### Phase 1: Get a basic app running

1. Install the Ferrari SDK for your tablet's firmware version
2. Create a minimal `CMakeLists.txt` with `qt_add_executable` + `qt_add_qml_module`
3. Write a simple `main.cpp` + `Main.qml` with a full-screen window
4. Cross-compile, deploy, and verify it launches with `QT_QUICK_BACKEND=epaper ./app -platform epaper`
5. Verify touch events work (add a `MouseArea` with a counter)

### Phase 2: Add evdev pen reading

1. Write `EvdevPenReader` class (see [[#EvdevPenReader implementation checklist]])
2. Wire it to a `StrokeEngine` that accumulates `StrokePoint`s
3. Render strokes in a `QQuickPaintedItem` subclass
4. Test: does the marker produce strokes on screen?

### Phase 3: Polish for e-ink

1. Implement damage-region updates (`update(const QRect&)`)
2. Turn off antialiasing (wasted on e-ink)
3. Add eraser support from `BTN_TOOL_RUBBER`
4. Add data export (JSON + PNG)

### Phase 4: Production readiness

1. Add graceful fallback when `/dev/input/event2` is unavailable
2. Handle device hotplug (pen charge/dock events)
3. Add session management (save/resume)
4. Test with different marker tips and pressure ranges

## EvdevPenReader implementation checklist

This is the core class you need. It should:

- [ ] Open the device with `O_RDONLY | O_NONBLOCK`
- [ ] Query ABS ranges via `EVIOCGABS(ABS_X)`, `EVIOCGABS(ABS_Y)`, `EVIOCGABS(ABS_PRESSURE)`
- [ ] Optionally grab exclusively with `EVIOCGRAB`
- [ ] Create a `QSocketNotifier` on the fd for `QSocketNotifier::Read`
- [ ] In the slot: read `struct input_event` in a loop until `read()` returns `EAGAIN`
- [ ] Accumulate `EV_ABS` values (X, Y, Pressure, TiltX, TiltY) between `SYN_REPORT`s
- [ ] Track `EV_KEY` buttons: `BTN_TOOL_PEN`, `BTN_TOOL_RUBBER`, `BTN_TOUCH`
- [ ] On `SYN_REPORT`: determine phase from button state (proximity + touch → Down/Move/Up/Hover)
- [ ] Map raw coordinates to screen pixels via linear interpolation
- [ ] Normalize pressure to [0.0, 1.0]
- [ ] Emit `penSample(const PenSample&)` with all data

### Phase state machine

```text
                    BTN_TOOL_PEN=1
    ┌──────────┐ ──────────────────→ ┌──────────────┐
    │ Not in   │                     │ In proximity │
    │ proximity│ ←────────────────── │ (hovering)   │
    └──────────┘   BTN_TOOL_PEN=0    └──────┬───────┘
                                         │  ▲  │  ▲
                                BTN_TOUCH=1  │  BTN_TOUCH=1
                                         │  │  │
                                         ▼  │  ▼
                                    ┌──────────────┐
                                    │ Pen down     │
                                    │ (drawing)    │
                                    └──────────────┘
```

### Coordinate mapping

The Paper Pro's Elan digitizer reports:

- **ABS_X**: range `[0, 11180]`, resolution 2832 units/mm
- **ABS_Y**: range `[0, 15340]`, resolution 2064 units/mm
- **ABS_PRESSURE**: range `[0, 4096]`
- **ABS_TILT_X**: range `[-9000, 9000]` (0.01-degree units)
- **ABS_TILT_Y**: range `[-9000, 9000]` (0.01-degree units)

Screen resolution: **1620 × 2160** pixels.

Mapping formulas (always query actual ranges at runtime, don't hard-code):

```cpp
qreal screenX = (rawX - xMin) * 1620.0 / (xMax - xMin);
qreal screenY = (rawY - yMin) * 2160.0 / (yMax - yMin);
qreal pressure = (rawPressure - pMin) / (pMax - pMin);  // [0.0, 1.0]
qreal tiltDegrees = rawTilt / 100.0;                    // 0.01° units → degrees
```

## E-ink rendering optimization

### The problem

Every pen sample triggers a repaint. A naive implementation fills the entire canvas white and redraws every stroke from scratch. On a 1620×2160 display (3.5M pixels), even at 30 Hz that's 100M pixel writes per second. The epaper display controller can do maybe 30–60 full refreshes per second, and each full refresh causes a visible flash.

### The solution: three layers of optimization

**Layer 1: Damage-region updates**

Instead of `update()` (full repaint), use `update(QRect)` with only the bounding box of the new ink segment:

```cpp
// On new stroke segment from (x1,y1) to (x2,y2) with width w:
int pad = qCeil(w / 2.0) + 2;
QRect dirty = QRect(QPointF(x1, y1), QPointF(x2, y2)).toRect().adjusted(-pad, -pad, pad, pad);
inkSurface->update(dirty);
```

This tells the epaper backend to only refresh the changed rectangle.

**Layer 2: Incremental painting on a persistent QImage**

Maintain a `QImage` as the canvas state. On each new stroke segment, only draw the new line segment onto the existing image. In `paint()`, just blit the relevant region of the image instead of redrawing all strokes:

```cpp
void InkSurface::paint(QPainter *painter) {
    if (m_needsFullRedraw) {
        painter->drawImage(0, 0, m_canvasImage);
        m_needsFullRedraw = false;
    }
    // Otherwise, the base class only calls paint() for the dirty rect,
    // and we just blit that region from m_canvasImage
}
```

**Layer 3: Antialiasing off**

Antialiased rendering is wasted on e-ink (which is 1-bit or 4-bit grayscale with hardware dithering). Turning it off halves the paint cost:

```cpp
painter->setRenderHint(QPainter::Antialiasing, false);
```

## Cross-compilation reference

### SDK structure

```
/opt/codex/ferrari/5.6.75/
├── environment-setup-cortexa53-crypto-remarkable-linux   # ← source this
├── site-config-cortexa53-crypto-remarkable-linux
├── version-cortexa53-crypto-remarkable-linux
├── buildinfo
└── sysroots/
    ├── cortexa53-crypto-remarkable-linux/   # TARGET (ARM) sysroot
    │   └── usr/
    │       ├── include/                     # Qt 6.8.2 headers
    │       └── lib/                         # Qt 6.8.2 libraries
    └── x86_64-codexsdk-linux/               # HOST (x86_64) tools
        └── usr/bin/
            └── aarch64-remarkable-linux-g++ # Cross-compiler
```

### Build commands

```bash
source /opt/codex/ferrari/5.6.75/environment-setup-cortexa53-crypto-remarkable-linux
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)
```

### CMakeLists.txt template

```cmake
cmake_minimum_required(VERSION 3.16)
project(your_app VERSION 0.1 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Qt6 6.5 REQUIRED COMPONENTS Quick Gui Qml)
qt_standard_project_setup(REQUIRES 6.5)
qt_policy(SET QTP0004 NEW)

qt_add_executable(your_app)

qt_add_qml_module(your_app
    URI YourApp
    VERSION 1.0
    QML_FILES qml/Main.qml
    SOURCES
        src/main.cpp
        src/EvdevPenReader.h
        src/EvdevPenReader.cpp
        # ... your other sources
)

target_include_directories(your_app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_definitions(your_app PRIVATE APP_VERSION="${PROJECT_VERSION}")
target_link_libraries(your_app PRIVATE Qt6::Quick Qt6::Gui Qt6::Qml)
```

Key points:
- `qt_policy(SET QTP0004 NEW)` suppresses the QML directory policy warning
- `target_include_directories(... src)` is essential — without it, generated QML registration code can't find your headers
- No extra libraries needed for evdev — it's kernel headers only

## Deployment and runtime reference

### Deploy

```bash
scp build/your_app root@10.11.99.1:/home/root/your_app/
ssh root@10.11.99.1 "chmod +x /home/root/your_app/your_app"
```

### Run

```bash
ssh root@10.11.99.1 "systemctl stop xochitl"
ssh -t root@10.11.99.1 "trap 'systemctl start xochitl' EXIT; \
  cd /home/root/your_app && \
  QT_QUICK_BACKEND=epaper ./your_app -platform epaper"
```

**Why stop xochitl?** It occupies the display and may hold input devices. Your app needs exclusive access.

**Why the trap?** Restores xochitl when your app exits (Ctrl+C or crash).

### USB SSH defaults

- Host: `root@10.11.99.1` (over USB-C)
- No password (root access by default)
- Target architecture: `aarch64` (ARM Cortex-A53)

## API references

### Linux evdev ioctls

| IOCTL | Purpose |
|-------|---------|
| `EVIOCGABS(axis)` | Query axis range: returns `input_absinfo` with `.minimum`, `.maximum`, `.resolution` |
| `EVIOCGRAB` | Exclusive grab: `int grab = 1; ioctl(fd, EVIOCGRAB, &grab)` |
| `EVIOCGNAME(len)` | Get device name string |

### Linux input event types

| Type | Code | Meaning |
|------|------|---------|
| `EV_ABS` | `ABS_X`, `ABS_Y` | Absolute position |
| `EV_ABS` | `ABS_PRESSURE` | Pen pressure |
| `EV_ABS` | `ABS_TILT_X`, `ABS_TILT_Y` | Pen tilt |
| `EV_KEY` | `BTN_TOOL_PEN` | Pen is in proximity |
| `EV_KEY` | `BTN_TOOL_RUBBER` | Eraser is in proximity |
| `EV_KEY` | `BTN_TOUCH` | Pen is touching the screen |
| `EV_SYN` | `SYN_REPORT` | End of event frame |

### Qt classes used

| Class | Purpose |
|-------|---------|
| `QSocketNotifier` | Async I/O on evdev fd (read events without threads) |
| `QQuickPaintedItem` | Custom-painted QML item for the ink canvas |
| `QQuickWindow` | Main window (attach event filters here) |
| `QAbstractListModel` | Device inventory list for QML ListView |

## File references

All file paths are relative to the project root at `/home/manuel/code/wesen/2026-04-06--paper-pro-pen-prob`:

- `src/EvdevPenReader.h/.cpp` — Direct evdev pen reader (the key new class)
- `src/TabletProbe.h/.cpp` — Qt QTabletEvent bridge (works on desktop, not on Paper Pro)
- `src/StrokeEngine.h/.cpp` — Ink model with smoothing and pressure-to-width
- `src/InkSurface.h/.cpp` — QQuickPaintedItem canvas renderer
- `src/SessionRecorder.h/.cpp` — JSON/PNG data export
- `src/DeviceInventoryModel.h/.cpp` — Input device list for QML
- `src/PenTypes.h` — Shared data types (PenSample, Stroke, PenPhase)
- `qml/Main.qml` — Full-screen UI with canvas + side panel
- `CMakeLists.txt` — Build configuration
- `scripts/build_ferrari.sh` — One-command cross-compilation
- `scripts/deploy_usb.sh` — Deploy binary to device
- `scripts/run_usb.sh` — Stop xochitl, run app, restore xochitl

## Working rules

1. **Never assume `QTabletEvent` works.** Test on Paper Pro hardware. The epaper plugin's limitations cannot be simulated on desktop.
2. **Always query axis ranges at runtime.** Don't hard-code `[0,11180]` — firmware updates may change them.
3. **Use `QSocketNotifier`, not threads.** The evdev fd is non-blocking. Async I/O on the main loop is simpler and safer.
4. **Call `update(QRect)`, not `update()`.** Full repaints are the enemy of e-ink responsiveness.
5. **Always stop xochitl before running your app.** And always restore it on exit.
6. **Keep the `TabletProbe` path alive.** It enables desktop testing. Don't remove it just because Paper Pro uses evdev.

## Related notes

- [[PROJ - Paper Pro Pen Probe - reMarkable E-Ink Drawing and Pen Input]] — the project that produced this playbook
- [[PROJ - EInk Typewriter]] — earlier reMarkable e-ink project
