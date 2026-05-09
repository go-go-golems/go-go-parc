---
title: Paper Pro E-Ink - Pen Input and SDK Build Fix
aliases:
  - Paper Pro Pen Probe
  - PPPP-001
  - EvdevPenReader
tags:
  - project
  - remarkable
  - eink
  - qt6
  - cmake
  - cross-compilation
  - evdev
  - stylus
  - pen-input
status: active
type: project
created: 2026-04-06
repo: /home/manuel/code/wesen/2026-04-06--paper-pro-pen-prob
---

# Paper Pro E-Ink — Pen Input and SDK Build Fix

This project is a Qt6/QML drawing application for the reMarkable Paper Pro that reads the stylus directly from the Linux evdev layer rather than relying on Qt's tablet event pipeline. The work was triggered by a build failure against the reMarkable Ferrari SDK (Qt 6.8.2 / codex 5.6.75), and resolved into a working direct-pen-input architecture.

> [!summary]
> Three things matter most from this work:
> 1. Qt 6.8.2 changed `QQuickPaintedItem::update()` — it has only one overload (`update(const QRect&)`), not a zero-arg `update()`. `QOverload<>::of(...)` targeting `void()` fails at compile time.
> 2. The reMarkable Paper Pro's `libepaper.so` Qt platform plugin discovers touch devices via udev tags (`Device_Touchscreen`) but **never discovers the pen** (`ID_INPUT_TABLET`) because the plugin only looks for touch tags, not tablet tags.
> 3. The fix is a `QSocketNotifier`-based evdev reader that opens `/dev/input/event2` directly with `EVIOCGRAB` exclusive access and emits Qt signals for pen proximity, contact, motion, and pressure.

## Why this project exists

The goal is a low-latency drawing application on the reMarkable Paper Pro. The core drawing stack (`StrokeEngine`, `CommittedInkSurface`, `LiveInkSurface`) was already present, but two things prevented it from working:

1. The app failed to build against the Ferrari SDK.
2. The app's `TabletProbe` listened for Qt `QTabletEvent`, but the Paper Pro's Qt platform plugin never dispatched tablet events — only touch events.

## Build failures against Ferrari SDK

### Error 1: `QOverload<>::of(&InkSurface::update)` fails

The codebase used a pattern like:
```cpp
connect(m_engine, &StrokeEngine::sceneChanged, 
        this, QOverload<>::of(&InkSurface::update));
```

This assumes `QQuickPaintedItem::update()` has a zero-argument overload. In Qt 6.8.2 (the Ferrari SDK version), there is only:
```cpp
void update(const QRect &rect = QRect());
```

`QOverload<>::of(...)` selects by signature, not by callability. A default argument doesn't create a separate overload. The fix is a lambda:
```cpp
connect(m_engine, &StrokeEngine::sceneChanged,
        this, [this]() { update(); });
```

### Error 2: `InkSurface` not declared in generated QML type registration

The `qt_add_qml_module()` CMake integration generates a `paper_pro_pen_probe_qmltyperegistrations.cpp` that does:
```cpp
#if __has_include(<InkSurface.h>)
#  include <InkSurface.h>
#endif
```

The generated code uses **angle brackets** (`<InkSurface.h>`), which searches only system include paths. The file lives at `src/InkSurface.h`, but `src/` was not in the project's include directories.

The fix: add to `CMakeLists.txt`:
```cmake
target_include_directories(paper_pro_pen_probe PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
```

This makes `#include <InkSurface.h>` resolvable by the generated registration code.

## The pen discovery problem

Once the app built and deployed, the stylus didn't work. Investigation showed:

The Paper Pro has two Elan input devices on the same SPI bus:

| Device | Event node | udev tag | Protocol |
|--------|-----------|----------|----------|
| Elan marker | `/dev/input/event2` | `ID_INPUT_TABLET=1` | ABS_X/Y + BTN_TOOL_PEN |
| Elan touch | `/dev/input/event3` | `ID_INPUT_TOUCHSCREEN=1` | ABS_MT_POSITION_X/Y (multi-touch) |

The epaper Qt platform plugin (`libepaper.so`) discovers input devices via udev:
- Touch handler scans for `Device_Touchpad|Device_Touchscreen` → finds event3 ✓
- **No tablet handler exists.** The plugin looks for touch tags only.

The pen device (event2 with `ID_INPUT_TABLET=1`) is never discovered.

Inside `libepaper.so`, there IS pen-handling code — `EpaperEvdevTouchScreenData::processInputEvent()` recognizes `BTN_TOOL_PEN`, `BTN_TOUCH`, and pressure values — but it cannot dispatch them as `QTabletEvent`. The only Qt event dispatch in the plugin is `QWindowSystemInterface::handleTouchEvent`.

Xochitl (reMarkable's own app) handles this by not using Qt tablet events at all. It reads `/dev/input/event2` directly via raw evdev in its own `PenInputHandler` class.

## EvdevPenReader implementation

The fix is a new class that reads the pen device directly and emits Qt signals:

```cpp
class EvdevPenReader : public QObject {
    Q_OBJECT
public:
    EvdevPenReader(const QString &devicePath, QObject *parent = nullptr);
    ~EvdevPenReader();

signals:
    void penSample(const PenSample &sample);

private:
    void openDevice();
    void onSocketActivated();
    void processEvent(const input_event &ev);
    void flushSample();
    float mapX(int rawX) const;
    float mapY(int rawY) const;
    float mapPressure(int rawPressure) const;

    // Evdev state
    int m_fd = -1;
    QSocketNotifier *m_notifier = nullptr;
    bool m_inProximity = false;
    bool m_inContact = false;
    bool m_dirtyX = false, m_dirtyY = false, m_dirtyPressure = false;
    int m_rawX = 0, m_rawY = 0, m_rawPressure = 0;
    int m_minX = 0, m_maxX = 11180;
    int m_minY = 0, m_maxY = 15340;
};
```

### Key design decisions

**Async via QSocketNotifier (no threads):**
The class opens the evdev fd with `O_NONBLOCK` and uses Qt's main event loop for I/O. `QSocketNotifier` fires `activated()` when data is available, and `onSocketActivated()` reads and processes events on the Qt thread.

**Exclusive access via EVIOCGRAB:**
```cpp
ioctl(m_fd, EVIOCGRAB, 1);
```
This prevents the epaper plugin from receiving duplicate events if it somehow opens the device. On Paper Pro this is safe because the plugin never opens event2 anyway.

**State machine on SYN_REPORT:**
Evdev events arrive one at a time. `processEvent()` updates dirty flags for each axis/key. The actual `penSample` signal only emits on `SYN_REPORT` via `flushSample()`:

```cpp
void EvdevPenReader::processEvent(const input_event &ev) {
    if (ev.type == EV_ABS) {
        switch (ev.code) {
        case ABS_X:      m_rawX = ev.value; m_dirtyX = true; break;
        case ABS_Y:      m_rawY = ev.value; m_dirtyY = true; break;
        case ABS_PRESSURE: m_rawPressure = ev.value; m_dirtyPressure = true; break;
        }
    } else if (ev.type == EV_KEY) {
        if (ev.code == BTN_TOOL_PEN) m_inProximity = ev.value;
        if (ev.code == BTN_TOOL_RUBBER) m_inProximity = false;
        if (ev.code == BTN_TOUCH) m_inContact = ev.value;
    } else if (ev.type == EV_SYN && ev.code == SYN_REPORT) {
        flushSample();
    }
}
```

**Coordinate mapping:**
The Paper Pro marker reports raw ABS ranges much larger than screen resolution:
- X: 0–11180 → screen: 0–1620 (scale ~6.9x)
- Y: 0–15340 → screen: 0–2160 (scale ~7.1x)
- Pressure: 0–4096 → normalized: 0.0–1.0
- Tilt: ±9000 (0.01-degree units) → ±90 degrees

## Current status

The app builds, deploys, and receives pen events. The marker draws on the e-ink display and touch buttons still work.

Remaining open questions:
- E-ink rendering optimization: currently every pen sample triggers a full repaint. Need damage-region updates and incremental painting.
- Eraser detection: `BTN_TOOL_RUBBER` is tracked but not yet wired to eraser behavior.
- Export: session/stroke export with evdev-originated data not yet tested.

## Open questions

- Does `FastEinkController` have a viable path forward on DRM/KMS Paper Pro hardware?
- Can third-party apps use DRM atomic commits directly, or must they go through a Qt-compatible layer?
- What is the minimum viable latency for e-ink stroke rendering without flickering?

## Related notes

- [[PROJ - Paper Pro E-Ink - DRM/KMS Fast Mode Investigation]] — why the existing fast-preview code was wrong
- [[PROJ - Paper Pro E-Ink - Ghidra Reverse Engineering]] — the libqsgepaper.so class hierarchy
- [[ARTICLE - Playbook - Building E-Ink Drawing Apps for the reMarkable Paper Pro]] — the playbook written from this session
