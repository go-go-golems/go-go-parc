---
title: Key Findings - ReMarkable Paper Pro Platform Architecture
aliases:
  - Paper Pro Platform Architecture
  - Paper Pro Reverse Engineering Findings
tags:
  - article
  - remarkable
  - eink
  - platform
  - architecture
  - reverse-engineering
  - qt6
  - drm
  - kms
status: active
type: article
created: 2026-04-07
repo: /home/manuel/code/wesen/2026-04-06--paper-pro-pen-prob
---

# Key Findings — ReMarkable Paper Pro Platform Architecture

This article distills the most important engineering facts learned from 14 hours of reverse engineering and development on the reMarkable Paper Pro. It is written for engineers who want to build third-party apps for the Paper Pro without repeating our dead ends.

> [!summary]
> Four things that would have saved us days:
> 1. The Paper Pro has no `/dev/fb0` — the old rm1/rm2 framebuffer approach is completely wrong.
> 2. The Qt epaper platform plugin (`libepaper.so`) does not dispatch `QTabletEvent` — the stylus must be read from `/dev/input/event2` directly.
> 3. The display fast path is driven by `DRM_IOCTL_MODE_ATOMIC` with proprietary e-ink policy in `EPFramebuffer` userspace code above DRM.
> 4. Xochitl renders at quarter resolution (405×1084) into dumb buffers, not full resolution.

## The Paper Pro is NOT the old reMarkable

The existing open-source ecosystem for reMarkable (rmkit, libremarkable, remarkable2-framebuffer) is almost entirely based on `/dev/fb0` and MXCFB/EPDC ioctls. These are the framebuffer interface used by the original reMarkable and reMarkable 2.

**The Paper Pro has no framebuffer device.** There is only `/dev/dri/card0`.

This means:
- `libremarkable` approaches will not work on Paper Pro
- MXCFB refresh ioctls (`MXCFB_SEND_UPDATE`, etc.) do not exist on Paper Pro
- Any app that targets `/dev/fb0` will silently fail or report "unavailable"

The Paper Pro uses a completely different architecture.

## The platform stack

```
Application (Qt Quick / QML)
       ↓
libepaper.so (Qt platform plugin) — handles touch via evdev
       ↓
libqsgepaper.so (Qt scenegraph plugin) — EPFramebuffer classes
       ↓
xochitl daemon — owns the display backend
       ↓
DRM/KMS on /dev/dri/card0
       ↓
imx-drm / imx8mm_lcdif_crtc / remarkable-cumulus-panel (kernel)
       ↓
e-ink panel hardware (ACEP2 controller)
```

The `EPFramebuffer` layer sits between the Qt scenegraph and DRM. It is the policy engine for e-ink updates.

## Pen input is broken in the public SDK

The epaper Qt platform plugin discovers input devices via udev:
- Looks for `Device_Touchpad` or `Device_Touchscreen` → finds the touchscreen
- Does **not** look for `Device_Tablet` → never sees the pen

The pen device on Paper Pro:
- `/dev/input/event2` — "Elan marker input"
- udev tag: `ID_INPUT_TABLET=1`
- Protocol: single-touch evdev (ABS_X/Y + BTN_TOOL_PEN + ABS_PRESSURE)

Xochitl reads the pen via its own internal `PenInputHandler` that bypasses Qt's input system entirely.

**Solution**: Open `/dev/input/event2` with `EVIOCGRAB` exclusive access and parse evdev events directly. The `BTN_TOOL_PEN` proximity signal and `BTN_TOUCH` contact signal are independent booleans — hover and draw are distinct states.

## Display resolution: quarter buffers

Xochitl allocates buffers at 405×1084 pixels, not 1620×2160. The hardware upscales. This is a fundamental e-ink optimization: lower resolution means:
- faster buffer copies
- smaller DMA transfers
- less waveform data per update

Any third-party app targeting the same e-ink pipeline should consider rendering at quarter resolution and letting the hardware upscale, rather than fighting for full-resolution buffer access.

## The e-ink update model

E-ink displays cannot update individual pixels — they update in waves. A full refresh requires:
1. Applying voltage to pixels (waveform lookup table)
2. Waiting for physical settling
3. Holding the voltage

The Paper Pro manages this through `EPFramebuffer`:
- **Content classification**: per-region pixel analysis → mono / grayscale / color buckets
- **Mode selection**: per-region purpose → Pen (fast), UI (medium), Content (quality), Sleep (off)
- **Temperature compensation**: high temperature increases e-ink latency, triggering slower waveforms
- **Region partitioning**: a single `swapBuffers_impl` call may issue multiple `Swtcon::update()` calls with different mode/flag tuples

The waveform file (`.eink` format) encodes the lookup tables. It is loaded at startup from `/usr/share/remarkable/`.

## DRM atomic commits

During active drawing, the dominant kernel traffic is `DRM_IOCTL_MODE_ATOMIC`. The atomic commit carries:
- which framebuffer to display (FB_ID)
- which CRTC to use
- connector/plane state
- e-ink-specific properties (vendor-private)

The key open question is whether those e-ink properties are standard KMS properties or require the proprietary `EPFramebuffer` layer. If they are public, a third-party app could use DRM atomic commits directly. If they are private, the app must either integrate with `EPFramebuffer` or accept that only xochitl can produce fast e-ink updates.

## What xochitl owns that third-party apps can't

- `/tmp/epframebuffer.lock` — only one process can own the display backend
- The waveform file loaded into the hardware
- The EPFramebuffer singleton (hardcoded to ACEP2)
- Any private DRM atomic properties

This means third-party apps are constrained to:
1. Qt's scenegraph rendering path (through `libqsgepaper.so`)
2. DRM atomic commits using only public properties
3. Direct framebuffer access (if the kernel exposes any alternative)

## Cross-compilation environment

The Ferrari SDK at `/opt/codex/ferrari/5.6.75` provides:
- Qt 6.8.2 (not 6.5 as older docs suggest)
- AArch64 cross-compiler: `aarch64-remarkable-linux-gcc`
- ARM Cortex-A53 + crypto extensions
- Build with: `eval "$CC ..."` — the `CC` variable is a command string, not a bare executable

## The single most useful diagnostic commands

```bash
# What's on the DRM device?
ssh root@10.11.99.1 "ls -la /dev/dri/"
ssh root@10.11.99.1 "cat /proc/dri/0/state" 2>/dev/null

# What's in /dev/fb*?
ssh root@10.11.99.1 "ls -la /dev/fb*"

# Input devices
ssh root@10.11.99.1 "cat /proc/bus/input/devices"

# DRM connector properties
ssh root@10.11.99.1 "cat /sys/class/drm/card0-LVDS-1/status"
ssh root@10.11.99.1 "ls /sys/class/drm/card0-*/"

# Panel sysfs
ssh root@10.11.99.1 "ls /sys/devices/platform/cumulus-panel/"

# DRM properties (on a machine with libdrm tools)
drmModeGetProperty(fd, prop_id) for each prop in the atomic payload

# Which binaries does xochitl link?
nm -D /tmp/rm-analysis/xochitl | grep -i epfb
strings /tmp/rm-analysis/xochitl | grep -i 'swapBuffers\|EPFB\|SWTCON'

# What does the panel plugin import?
nm -D /tmp/rm-analysis/libepaper.so | grep -i 'QTablet\|QTouch\|evdev'
```

## Summary for future explorers

If you want to build a drawing app for Paper Pro:
1. Use Qt6/QML — it works on the platform
2. Read the pen from `/dev/input/event2` directly, not from Qt events
3. Don't try `/dev/fb0` — it doesn't exist
4. Don't expect Qt's `QTabletEvent` — the plugin doesn't dispatch them
5. If you want fast e-ink: either integrate with the EPFramebuffer layer, or use Qt's scenegraph and accept that only xochitl can currently do full-speed partial refreshes
6. If you want to experiment with DRM directly: use atomic commits with dumb buffers at 405×1084, and decode the property IDs to understand what xochitl actually sets

The architecture is sound for third-party apps. The constraint is the display fast path — and that constraint is primarily a reverse-engineering problem, not an SDK limitation.
