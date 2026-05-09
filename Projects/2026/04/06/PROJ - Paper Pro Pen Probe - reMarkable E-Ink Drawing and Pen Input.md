---
title: Paper Pro Pen Probe
aliases:
  - Paper Pro Pen Probe
  - PPPP
  - reMarkable Paper Pro pen probe
tags:
  - project
  - remarkable
  - eink
  - qt
  - cross-compilation
  - stylus
  - evdev
status: active
type: project
created: 2026-04-06
repo: /home/manuel/code/wesen/2026-04-06--paper-pro-pen-prob
---

# Paper Pro Pen Probe

A Qt Quick / QML application for the reMarkable Paper Pro that captures stylus input, renders pressure-sensitive ink strokes on the e-ink display, shows live pen telemetry (position, pressure, tilt, rotation, event rate), enumerates Qt-visible input devices, and exports captured sessions as JSON + PNG. Built to validate the pen input pipeline before building more complex features like OCR on top.

> [!summary]
> The project's main identities:
> 1. A working e-ink drawing app that runs on the reMarkable Paper Pro hardware — the marker draws ink on the display, touch controls the side panel, and all data exports correctly.
> 2. A deep investigation into how the Paper Pro's custom Qt platform plugin handles (or rather, *doesn't* handle) pen events, and the direct-evdev workaround required to make stylus input work in third-party apps.
> 3. A reusable playbook for building any e-ink drawing app on the Paper Pro — the architecture, the SDK cross-compilation, the deployment workflow, and the hard-won knowledge about the epaper plugin's limitations.

## Why this project exists

The reMarkable Paper Pro uses a custom Qt platform plugin (`epaper`) that is poorly documented for third-party developers. The official developer portal example shows a "Hello reMarkable" app with touch events only, noting that "handling the marker is more involved and not shown here." This project exists to fill that gap — to understand exactly how pen input works on the device, build a working pen-aware application, and document the full path so others can reproduce it.

## Current project status

The project is **functional on hardware**:

- Touch input works (buttons, toggles, steppers in the side panel)
- **Pen/marker input works** — draws strokes on the e-ink canvas via direct evdev reading of `/dev/input/event2`
- Live telemetry updates (position, pressure, tilt, phase, event rate)
- Device inventory shows all Qt-visible input devices
- Export produces `session.json`, `events.jsonl`, `strokes.json`, and `snapshot.png`
- Cross-compilation from x86_64 Linux to ARM aarch64 works cleanly

What is still rough:

- Every pen sample triggers a full canvas repaint (all strokes redrawn from scratch) — needs damage-region optimization for better e-ink latency
- No eraser detection from `BTN_TOOL_RUBBER` yet
- No OCR, networking, or cloud integration

## Project shape

The project has three layers:

1. **Build and deployment pipeline** — CMake-based cross-compilation against the reMarkable Ferrari SDK, deployment over USB SSH
2. **Input handling** — `TabletProbe` (Qt tablet events, for desktop fallback) + `EvdevPenReader` (direct evdev reading, for Paper Pro hardware)
3. **Rendering and data export** — `StrokeEngine` (ink model with smoothing and pressure-to-width), `InkSurface` (QQuickPaintedItem renderer), `SessionRecorder` (JSON/PNG export)

## Architecture

```text
  Marker Hardware (Elan SPI digitizer)
      │
      ▼
  /dev/input/event2 (Linux evdev)
      │
      ▼
  EvdevPenReader (QSocketNotifier, async on main loop)
      │
      ├─→ penSample(PenSample) ─→ StrokeEngine::handleInkSample()
      │                                  │
      │                                  ▼
      │                             InkSurface::paint() → e-ink display
      │
      └─→ penSample(PenSample) ─→ TabletProbe::handleEvdevPenSample()
                                       │
                                       ▼
                                  telemetryChanged() → QML UI
                                  sampleRecorded()  → SessionRecorder → JSON/PNG

  Touch Hardware (Elan capacitive)
      │
      ▼
  /dev/input/event3
      │
      ▼
  epaper plugin touch handler → QTouchEvent → QML MouseArea → buttons/toggles
```

### Source file map

| File | Role |
|------|------|
| `src/EvdevPenReader.h/.cpp` | Direct evdev reader for Paper Pro marker device — `QSocketNotifier`-based, state machine for pen phases, coordinate mapping |
| `src/TabletProbe.h/.cpp` | Qt `QTabletEvent` bridge — event filter on window, telemetry QML properties, session recording |
| `src/StrokeEngine.h/.cpp` | Ink model — stroke accumulation, exponential smoothing, pressure-to-width mapping, `QImage` rendering |
| `src/InkSurface.h/.cpp` | `QQuickPaintedItem` canvas — connects to `StrokeEngine`, paints all strokes |
| `src/SessionRecorder.h/.cpp` | Data export — captures all `PenSample`s, writes `session.json`, `events.jsonl`, `strokes.json`, `snapshot.png` |
| `src/DeviceInventoryModel.h/.cpp` | `QAbstractListModel` listing all Qt-visible input devices |
| `src/PenTypes.h` | Shared data types — `PenSample`, `Stroke`, `StrokePoint`, `PenPhase` enum, JSON conversion helpers |
| `src/main.cpp` | Application entry — instantiates all C++ objects, wires signal-slot connections |
| `qml/Main.qml` | Full-screen QML UI — canvas + side panel with buttons, toggles, steppers, telemetry, device inventory |
| `scripts/build_ferrari.sh` | Sources the SDK environment and runs cmake + make |
| `scripts/deploy_usb.sh` | Copies the binary to the device via scp |
| `scripts/run_usb.sh` | Stops xochitl, runs app with epaper backend, restores xochitl on exit |

## Implementation details

### The build failure and its three fixes

The project initially failed to build against the Ferrari SDK (codex 5.6.75, Qt 6.8.2) with three distinct errors:

**Error 1: `QOverload<>::of(&InkSurface::update)` in InkSurface.cpp**

The code assumed `QQuickPaintedItem::update()` had a zero-argument overload. In Qt 6.8.2, the only signature is `void update(const QRect &rect = QRect())` — a single overload with a default argument. `QOverload<>::of(...)` tries to match `void()` and fails. A default argument does not create a separate overload in C++.

Fix: replaced with lambdas `[this]() { update(); }`.

**Error 2: `InkSurface` undeclared in generated `qmltyperegistrations.cpp`**

The auto-generated QML type registration code uses `#include <InkSurface.h>` with angle brackets. The `src/` directory was not in the include path, so `__has_include` returned false and the header was never included.

Fix: added `target_include_directories(paper_pro_pen_probe PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)` to `CMakeLists.txt`.

**Error 3: `QQuickItem` undeclared in generated `qmltyperegistrations.cpp`**

Even after the include path fix, the generated code couldn't resolve `QQuickItem` (base class of `InkSurface`). The header `<QQuickPaintedItem>` includes it transitively in some Qt versions but not all.

Fix: added `#include <QQuickItem>` to `InkSurface.h`.

### The pen input investigation

After the build succeeded and the app launched on the device, touch worked but the marker pen produced no events. The investigation went through these stages:

1. **Kernel device discovery**: The Paper Pro has two Elan input devices — `/dev/input/event2` (marker, `ID_INPUT_TABLET=1`) and `/dev/input/event3` (touch, `ID_INPUT_TOUCHSCREEN=1`).

2. **epaper plugin analysis**: `strings` on `/usr/lib/plugins/platforms/libepaper.so` revealed that the touch handler only scans for `Device_Touchpad|Device_Touchscreen` devices. It never discovers the marker device (`ID_INPUT_TABLET`). The plugin has pen event code (`Got pen event: %3d`) but no `QWindowSystemInterface::handleTabletEvent` symbol — it literally cannot dispatch `QTabletEvent`.

3. **Official documentation**: The reMarkable developer portal confirms: "Touch event handling works out of the box, while handling the marker is more involved and not shown here."

4. **How xochitl does it**: Xochitl (the proprietary reMarkable note-taking app) reads `/dev/input/event2` directly via its own `PenInputHandler` class, completely bypassing Qt's input system.

### The EvdevPenReader solution

The fix was a new class `EvdevPenReader` that:

- Opens `/dev/input/event2` with `O_RDONLY | O_NONBLOCK`
- Queries axis ranges via `EVIOCGABS` ioctl (X=[0,11180], Y=[0,15340], Pressure=[0,4096])
- Grabs the device exclusively with `EVIOCGRAB` to prevent conflicts
- Uses `QSocketNotifier` for async reads on the main event loop (no threads)
- Maintains a state machine tracking `BTN_TOOL_PEN`, `BTN_TOOL_RUBBER`, `BTN_TOUCH` and all `EV_ABS` axes
- Emits `penSample(const PenSample&)` on every `SYN_REPORT`, using the same `PenSample` struct as `TabletProbe`
- Maps raw coordinates to screen pixels: `screenX = rawX * 1620 / 11180`, `screenY = rawY * 2160 / 15340`

This coexists with the existing `TabletProbe` (which handles Qt `QTabletEvent` on desktop) — on Paper Pro, only `EvdevPenReader` produces events.

## Important project docs

- **Design doc**: `ttmp/.../design-doc/02-evdevpenreader-direct-pen-input-for-paper-pro.md` — full architecture, state machine, coordinate mapping formulas, alternatives considered
- **Analysis guide**: `ttmp/.../design-doc/01-analysis-design-implementation-guide.md` — ~8000-word intern-facing guide covering the entire system
- **Diary**: `ttmp/.../reference/01-diary.md` — detailed step-by-step diary of the full investigation
- **Investigation scripts**: `scripts/XX-01-input-device-info.sh`, `XX-02-xochitl-env.sh`, `XX-03-debug-run.sh` — saved ephemeral scripts used during debugging

## Open questions

- How to optimize e-ink rendering for low latency? Currently every pen sample triggers a full repaint of all strokes. Need damage-region `update(const QRect&)`, incremental painting on a persistent `QImage`, and possibly turning off antialiasing on the 1-bit/4-bit e-ink display.
- Should `BTN_TOOL_RUBBER` be wired to eraser mode in `StrokeEngine`?
- The `EVIOCGRAB` (exclusive grab) prevents other processes from reading the marker device. Is this safe if future code needs shared access?

## Near-term next steps

- Implement damage-region updates and incremental painting for better e-ink latency
- Wire eraser detection from `BTN_TOOL_RUBBER`
- Test export flow with evdev-originated data
- Upload updated guide to reMarkable

## Project working rule

When working on Paper Pro pen input, assume `QTabletEvent` will never fire. Always test on hardware — the epaper plugin's behavior cannot be simulated on desktop. Keep the `EvdevPenReader` and `TabletProbe` paths separate so desktop testing still works.

## Related notes

- [[ARTICLE - Playbook - Building E-Ink Drawing Apps for the reMarkable Paper Pro]]
