---
title: Playbook - Building E-Ink Drawing Apps for the ReMarkable Paper Pro
aliases:
  - Paper Pro E-Ink Playbook
  - E-Ink Drawing Playbook
tags:
  - article
  - playbook
  - remarkable
  - eink
  - qt6
  - cmake
  - cross-compilation
  - evdev
status: active
type: article
created: 2026-04-07
repo: /home/manuel/code/wesen/2026-04-06--paper-pro-pen-prob
---

# Playbook — Building E-Ink Drawing Apps for the ReMarkable Paper Pro

This playbook captures the engineering knowledge needed to build a working drawing application for the reMarkable Paper Pro from scratch. It is based on a 14-hour session that fixed a broken build, diagnosed missing pen input, and reverse-engineered the display stack.

> [!summary]
> The four things that will bite you first:
> 1. Qt 6.8.2 changed `QQuickPaintedItem::update()` — no zero-arg overload, use a lambda
> 2. The Paper Pro has **no `/dev/fb0`** — old reMarkable framebuffer approaches don't apply
> 3. The Qt epaper plugin does **not dispatch `QTabletEvent`** — read `/dev/input/event2` directly
> 4. Xochitl owns the display backend via `/tmp/epframebuffer.lock` — only one process can be the EPFramebuffer owner

## When to use this playbook

Use this playbook when you are starting a new Qt6/QML drawing application for the Paper Pro, or when you are debugging why your existing Qt drawing app doesn't receive stylus events.

## Core mental model

The Paper Pro display pipeline has three layers:

1. **Rendering layer** — Qt Quick/QML scenegraph produces frames
2. **E-ink policy layer** — `EPFramebuffer` decides which regions to update with which waveforms
3. **DRM/KMS layer** — atomic commits push buffer changes to the hardware

A third-party app currently sits at layer 1. Layers 2 and 3 are owned by `xochitl` unless you replace them.

## Recommended implementation sequence

### 1. Set up cross-compilation

The Ferrari SDK is at `/opt/codex/ferrari/5.6.75`. Use it for cross-compilation.

```bash
# Source the SDK environment
source /opt/codex/ferrari/5.6.75/environment-setup

# Build
eval "$CC -o app ..."  # Note: CC is a command string, not a bare executable

# Deploy
scp build/my_app root@10.11.99.1:/home/root/my_app/
ssh root@10.11.99.1 "systemctl stop xochitl; ./my_app; systemctl start xochitl"
```

### 2. Fix Qt 6.8.2 API issues

In Qt 6.8.2, `QQuickPaintedItem::update()` has only one signature:
```cpp
void update(const QRect &rect = QRect());  // NOT void update()
```

If your code uses `QOverload<>::of(&MyItem::update)` targeting a zero-arg overload, it will fail to compile. Use a lambda instead:
```cpp
connect(engine, &StrokeEngine::sceneChanged,
        this, [this]() { update(); });
```

Also ensure your header includes both:
```cpp
#include <QQuickItem>   // for generated QML type registration
#include <QQuickPaintedItem>
```

And add the source directory to your CMake include path:
```cmake
target_include_directories(my_app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
```

This is required because Qt's `qt_add_qml_module()` generates `#include <HeaderName.h>` with angle brackets — if your headers are in a subdirectory, that subdirectory must be explicitly added.

### 3. Implement direct pen input

The Paper Pro pen device is `/dev/input/event2` with:
- Protocol: single-touch evdev (ABS_X/Y + BTN_TOOL_PEN + BTN_TOUCH + ABS_PRESSURE)
- Raw ranges: X [0, 11180], Y [0, 15340], Pressure [0, 4096]
- Screen: 1620×2160 pixels

Use `QSocketNotifier` for async I/O, not threads:
```cpp
// Open with exclusive access
m_fd = open("/dev/input/event2", O_RDONLY | O_NONBLOCK);
ioctl(m_fd, EVIOCGRAB, 1);  // exclusive access

// Async notification via Qt event loop
m_notifier = new QSocketNotifier(m_fd, QSocketNotifier::Read, this);
connect(m_notifier, &QSocketNotifier::activated,
        this, &EvdevPenReader::onSocketActivated);
```

Process evdev events with a state machine that only emits on `SYN_REPORT`:
```cpp
void EvdevPenReader::processEvent(const input_event &ev) {
    if (ev.type == EV_ABS) {
        switch (ev.code) {
        case ABS_X: m_x = ev.value; m_dirtyX = true; break;
        case ABS_Y: m_y = ev.value; m_dirtyY = true; break;
        case ABS_PRESSURE: m_pressure = ev.value; m_dirtyP = true; break;
        }
    } else if (ev.type == EV_KEY) {
        if (ev.code == BTN_TOOL_PEN) m_inProximity = ev.value;
        if (ev.code == BTN_TOOL_RUBBER) m_inProximity = false;
        if (ev.code == BTN_TOUCH) m_inContact = ev.value;
    } else if (ev.type == EV_SYN && ev.code == SYN_REPORT) {
        flushSample();  // only emit here, not on every event
    }
}
```

Map coordinates with linear interpolation:
```cpp
float EvdevPenReader::mapX(int raw) const {
    return (float)(raw - m_minX) / (m_maxX - m_minX) * SCREEN_WIDTH;
}
```

### 4. Render efficiently for e-ink

E-ink displays are slow to update but retain their state. The key optimization is **not redrawing everything on every stroke**. Use a two-layer model:

```
LiveInkSurface  — last N strokes with current stroke
CommittedInkSurface — confirmed committed strokes
```

On pen-down: add to LiveInkSurface only.
On pen-up: move from Live to Committed.
On repaint: only repaint what changed (LiveInkSurface).

For damage-region updates, track the bounding box of the current stroke and only call `update(boundingRect)` on that region.

### 5. Display updates

For now, rely on Qt's scenegraph to push frames to `libqsgepaper.so`. The `EPFramebuffer` layer will handle e-ink policy automatically. The tradeoff is that Qt's update rate may feel laggy compared to xochitl's direct DRM control.

If you need faster updates: the long-term path is to understand the DRM atomic property protocol and potentially call DRM directly, but that requires decoding the property IDs used by xochitl.

## Common failure modes

### Failure: "QOverload not found"
**Cause**: Qt 6.8.2 has no zero-arg `update()` overload.
**Fix**: Use a lambda `[this]() { update(); }` instead.

### Failure: "InkSurface not declared" in generated QML code
**Cause**: Generated QML type registration uses `#include <Header.h>` with angle brackets, but `src/` is not in include path.
**Fix**: `target_include_directories(my_app PRIVATE ${CMAKE_SOURCE_DIR}/src)`

### Failure: Pen doesn't work, no tablet events received
**Cause**: `libepaper.so` never discovers the pen device — it only looks for touch udev tags.
**Fix**: Read `/dev/input/event2` directly with EvdevPenReader.

### Failure: "Fast preview unavailable"
**Cause**: `FastEinkController` targets `/dev/fb0`, which doesn't exist on Paper Pro.
**Fix**: Remove fbdev-based fast preview. The Paper Pro uses DRM/KMS, not framebuffer.

### Failure: App runs but xochitl reports "display locked"
**Cause**: Another process (possibly a previous app run) still holds `/tmp/epframebuffer.lock`.
**Fix**: `ssh root@10.11.99.1 "rm -f /tmp/epframebuffer.lock; systemctl restart xochitl"`

### Failure: DRM atomic commits don't produce visible updates
**Cause**: Missing e-ink-specific DRM properties, or buffer resolution mismatch (405×1084 vs 1620×2160).
**Fix**: Use the buffer geometry xochitl uses, and ensure the EPFramebuffer layer is in charge.

## Anti-patterns to avoid

- **Don't try to build for `/dev/fb0`** — it doesn't exist on Paper Pro
- **Don't rely on `QTabletEvent`** — the epaper plugin doesn't dispatch them
- **Don't hard-code axis ranges** — query them at runtime with `EVIOCGABS`
- **Don't forget `EVIOCGRAB`** if you need exclusive device access
- **Don't use `QOverload<>::of` for Qt 6.8.2 `update()`** — use lambdas

## Cross-compilation reference

```
SDK path:       /opt/codex/ferrari/5.6.75
Qt version:     6.8.2 (not 6.5)
Architecture:   AArch64 (ARM Cortex-A53 + crypto)
Compiler:       aarch64-remarkable-linux-gcc
Build tool:     CMake with qt_add_qml_module()
```

Build script pattern:
```bash
eval "$(/opt/codex/ferrari/5.6.75/environment-setup)"
rm -rf build && mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

Deploy:
```bash
scp my_app root@10.11.99.1:/home/root/my_app/
ssh root@10.11.99.1 "systemctl stop xochitl; ./my_app; systemctl start xochitl"
```

## Related notes

- [[PROJ - Paper Pro E-Ink - Pen Input and SDK Build Fix]] — detailed build fix and EvdevPenReader implementation
- [[PROJ - Paper Pro E-Ink - DRM KMS Fast Mode Investigation]] — the DRM/KMS architecture and why fbdev is wrong
- [[PROJ - Paper Pro E-Ink - Ghidra Reverse Engineering]] — the EPFramebuffer class hierarchy and update policy
- [[ARTICLE - Key Findings - ReMarkable Paper Pro Platform Architecture]] — the top-level platform overview
