---
title: Paper Pro E-Ink - DRM/KMS Fast Mode Investigation
aliases:
  - PPPP-003
  - Paper Pro DRM
  - Paper Pro fast mode
  - drm_spy
  - epfb_spy
tags:
  - project
  - remarkable
  - eink
  - drm
  - kms
  - linux
  - framebuffer
  - reverse-engineering
status: active
type: project
created: 2026-04-06
repo: /home/manuel/code/wesen/2026-04-06--paper-pro-pen-prob
---

# Paper Pro E-Ink — DRM/KMS Fast Mode Investigation

This project investigated why the Paper Pro's experimental `FastEinkController` reported "fast preview unavailable" and traced the actual display path used by reMarkable's own `xochitl` daemon. The investigation confirmed that the Paper Pro uses **DRM/KMS on `/dev/dri/card0`** rather than the old framebuffer device (`/dev/fb0`) that older reMarkable reverse-engineering targeted.

> [!summary]
> Three findings that matter most:
> 1. The Paper Pro has **no `/dev/fb0`** and no MXCFB/EPDC framebuffer ioctls. The old rm1/rm2 e-ink approach is inapplicable.
> 2. `xochitl` uses `/dev/dri/card0` with **dumb buffers**, **DRM framebuffer objects**, and heavy **`DRM_IOCTL_MODE_ATOMIC`** traffic during drawing.
> 3. The Paper Pro display stack includes proprietary userspace components (`EPFramebuffer`, `SWTCON`, `Acep2`) that sit above DRM and implement the actual e-ink policy — waveform selection, temperature thresholds, region partitioning.

## Why this project exists

The `FastEinkController` in the parent project attempted to write directly to `/dev/fb0` and issue framebuffer refresh ioctls modeled after `libremarkable`. On the Paper Pro, `/dev/fb0` does not exist, so the fast preview path failed immediately.

The question became: what does the Paper Pro actually use for fast drawing, and can a third-party app use the same or a similar path?

## The answer: no `/dev/fb0`

Device inspection on the Paper Pro:

```bash
ssh root@10.11.99.1 "ls -la /dev/fb* 2>&1"
# ls: /dev/fb*: No such file or directory

ssh root@10.11.99.1 "ls -la /dev/dri/"
# card0  by-path/
```

The Paper Pro exposes only the DRM device. This rules out all fbdev-based approaches.

## The DRM/KMS startup sequence

When `xochitl` starts, it goes through a well-defined KMS initialization:

```c
open("/dev/dri/card0", O_RDWR)           // → fd=17
drmSetClientCap(fd, DRM_CLIENT_CAP_UNIVERSAL_PLANES, 1)
drmSetClientCap(fd, DRM_CLIENT_CAP_ATOMIC, 1)
drmGetCap(fd, DRM_CAP_DUMB_BUFFER)       // → 1 (supports dumb buffers)
drmGetCap(fd, DRM_CAP_CRTC_IN_VBLANK_EVENT) // → 1
drmModeGetResources(fd)                  // enumerate connectors, encoders, CRTCs
drmModeGetConnector(fd, connector_id)     // get display properties
drmModeGetEncoder(fd, encoder_id)         // get encoder
drmModeGetPlaneResources(fd)             // enumerate planes
drmModeGetPlane(fd, plane_id)            // get plane properties
```

This is textbook modern KMS setup. The key enabling caps are `UNIVERSAL_PLANES` (access to all planes, not just the primary) and `ATOMIC` (for atomic commits).

## Buffer allocation: dumb buffers, not GBM

Xochitl allocates display buffers using the DRM dumb buffer API:

```c
struct drm_mode_create_dumb create = {
    .width = 405,      // note: small width — likely downscaled
    .height = 1084,
    .bpp = 32,
};
drmIoctl(fd, DRM_IOCTL_MODE_CREATE_DUMB, &create);
// → returns handle, pitch=1620, size

drmModeAddFB(fd, width=405, height=1084, depth=24, bpp=32, pitch=1620, handle=N, ...)
```

The width of 405 is notable. The Paper Pro screen is 1620×2160 (RGBA). A buffer width of 405 suggests **quarter-resolution buffers** — xochitl renders at 1/4 horizontal resolution and the hardware upscales. This is a common e-ink optimization: lower resolution means faster buffer swaps and less data to transfer.

## The dominant drawing ioctl: DRM_IOCTL_MODE_ATOMIC

During active drawing (pen down, moving), the dominant ioctl by far is:

```
DRM_IOCTL_MODE_ATOMIC  (0xBC = DRM_IOCTL_BASE + 0x3C)
```

A live trace while the user drew and switched colors showed:
- ~4090 atomic commits during the session
- ~32 other ioctls (mostly `drmModeSetCrtc` for blank/unblank transitions)

The atomic commits are the hot path. They carry the update data in a payload that includes:
- which framebuffer to display (plane `FB_ID`)
- which CRTC to use
- which connectors to activate
- any vendor-specific property values

The raw bytes of each atomic commit's property list are the remaining unknown.

## DRM property decoding is the next step

The atomic commit properties are identified by numeric IDs. Without decoding those IDs to names, we can't know what values xochitl is setting. The standard approach:

```bash
# Get all property IDs and names for the plane
drmModeObjectGetProperties(fd, plane_id, DRM_MODE_OBJECT_PLANE)
# → returns array of {prop_id, value}

# For each prop_id, get the property definition
drmModeGetProperty(fd, prop_id)
# → returns {name, type, enum_values, range, ...}
```

Xochitl's atomic commits likely include both standard KMS properties (`FB_ID`, `CRTC_ID`, `ACTIVE`, `alpha`, `zpos`) and **vendor-private properties** ( waveform mode, update region, temperature compensation flags). The private properties are where the e-ink intelligence lives.

## The proprietary display stack above DRM

Static analysis of `xochitl` strings revealed a proprietary layer:

```
EPFramebuffer
EPFramebufferAcep2
EPFramebufferSwtcon
Acep2_PModeInvoker
SWTCON initialized \o/
Failed to initialize SWTCON.
/tmp/epframebuffer.lock
EPFB_HIGHTEMP_TMODE_THRESHOLD
EPFB_HIGHTEMP_STD_FAST_THRESHOLD
Loading waveforms from: /usr/share/remarkable/GAL3_AAB0AC_ID0F11_AC118TC1F2_AD1004-LHA_TC.eink
pmic: setting rails to 6.0, 12.0, 24.0, -6.0, -12.0, -24.0
```

And from `libqsgepaper.so` (the Qt scenegraph plugin for the Paper Pro display):

```
vtable for EPFramebuffer
vtable for EPFramebufferAcep2
vtable for EPFramebufferSwtcon
EPFramebuffer::instance()
EPFramebuffer::swapBuffers(QRect, ...)
EPFramebuffer::swapBuffers(QRegion const&, ...)
EPFramebuffer::ghostControl(...)
EPFramebufferAcep2::swapBuffers_impl(...)
EPFramebufferAcep2::scheduleTModeUpdate(...)
EPFramebufferSwtcon::update(QRect, int, PixelMode, int)
EPFramebufferSwtcon::initialize()
EPFramebufferSwtcon::temperature()
```

This is a three-level inheritance chain that manages the e-ink update policy above DRM.

## Panel hardware and waveform

The kernel driver is `remarkable-cumulus-panel` (device tree: `remarkable,cumulus-panel`), built on top of `imx-drm`. The panel exposes voltage rail controls via sysfs:

```
/sys/devices/platform/cumulus-panel/vneg1    6000000
/sys/devices/platform/cumulus-panel/vneg2   12005000
/sys/devices/platform/cumulus-panel/vneg3   24015000
/sys/devices/platform/cumulus-panel/vcom       507600
```

Xochitl loads a proprietary waveform file (`.eink` format) from `/usr/share/remarkable/` and configures the panel rails at startup. The waveform file encodes the precise pixel-transition lookup tables for each display mode (fast grayscale, full grayscale, color, etc.).

## DRM spy: `drm_spy.so`

A reusable preload library was built to intercept xochitl's DRM calls:

```c
// Intercepted symbols
drmOpen
drmIoctl              // raw ioctl tracing
drmGetCap
drmSetClientCap
drmModeGetResources
drmModeGetConnector
drmModeGetEncoder
drmModeGetPlaneResources
drmModeGetPlane
drmModeObjectGetProperties
drmModeGetProperty
drmModeAddFB
drmModeRmFB
drmModeSetCrtc
```

Usage:
```bash
LD_PRELOAD=/home/root/drm_spy.so xochitl 2>&1 | tee /tmp/drm-trace.txt
```

Build note: The Ferrari SDK's `CC` variable is a full command string, not a bare executable. Build with `eval "$CC ..."` not `"$CC" ...`.

## Current status

The DRM/KMS path is confirmed. The remaining question is whether a third-party app can reproduce the fast e-ink behavior using public DRM/KMS APIs, or whether the critical logic lives entirely in the proprietary `EPFramebuffer` userspace layer.

The next step is decoding the atomic commit payloads: resolve property IDs to names and capture the property-value pairs during a drawing session.

## Open questions

- Can we set e-ink-specific DRM properties from a third-party app, or are they restricted to the EPFramebuffer process?
- Does the Paper Pro kernel driver (`remarkable-cumulus-panel`) expose any e-ink control interfaces other than sysfs voltage rails?
- Is there a waveform file format spec, or is it fully proprietary?
- Can Qt's scenegraph be wired to DRM atomic commits without going through xochitl's EPFramebuffer layer?

## Related notes

- [[PROJ - Paper Pro E-Ink - Pen Input and SDK Build Fix]] — the pen input architecture that made drawing possible
- [[PROJ - Paper Pro E-Ink - Ghidra Reverse Engineering]] — the EPFramebuffer class hierarchy recovered from libqsgepaper.so
