---
title: Paper Pro E-Ink - Ghidra Reverse Engineering of libqsgepaper.so
aliases:
  - PPPP-004
  - EPFramebuffer
  - EPFramebufferAcep2
  - EPFramebufferSwtcon
  - Ghidra Paper Pro
tags:
  - project
  - remarkable
  - eink
  - ghidra
  - reverse-engineering
  - aarch64
  - elf
  - qt6
  - drm
  - kms
status: active
type: project
created: 2026-04-07
repo: /home/manuel/code/wesen/2026-04-06--paper-pro-pen-prob
---

# Paper Pro E-Ink — Ghidra Reverse Engineering of libqsgepaper.so

This project recovered the architecture of the reMarkable Paper Pro's proprietary e-ink display layer by reverse-engineering `libqsgepaper.so` (the Qt scenegraph plugin that implements the EPFramebuffer classes) and `xochitl` (the main reMarkable daemon). The work was done with Ghidra headless on AArch64 ELF binaries extracted from the Ferrari SDK sysroot and the live device.

> [!summary]
> The three most important findings:
> 1. **Class hierarchy**: `EPFramebuffer ← EPFramebufferSwtcon ← EPFramebufferAcep2` — a three-level inheritance chain where Acep2 is the concrete Paper Pro implementation constructed by the singleton.
> 2. **Content classification**: `EPContentMap` has 4 slots and classifies rendered content into mono/grayscale/color buckets. `EPScreenModeMap` has 6 modes (Pen, Mono, Animation, UI, Content, Sleep).
> 3. **Update policy**: `EPFramebufferAcep2::swapBuffers_impl()` is not a simple buffer flip — it partitions the dirty region, checks content type and temperature, and issues multiple `Swtcon::update()` calls with different mode/flag tuples.

## Why this project exists

PPPP-003 established that the Paper Pro uses DRM/KMS with heavy atomic commit traffic and a proprietary display stack. The remaining question was: what do the `EPFramebuffer`, `SWTCON`, and `Acep2` classes actually do, and can a third-party app call into or replicate their behavior?

The binaries under study:

| Binary | Source | Purpose |
|--------|--------|---------|
| `libqsgepaper.so` | Ferrari SDK sysroot | Qt scenegraph plugin with EPFramebuffer classes |
| `xochitl` | Live device | Main reMarkable daemon, owns the display backend |
| `libepaper.so` | Live device | Qt platform plugin (touch/evdev handling) |

## Tooling setup

The host lacked `analyzeHeadless` initially. Static analysis proceeded with `readelf`, `aarch64-linux-gnu-objdump`, `strings`, and `nm -C`. Ghidra headless was later confirmed at `/opt/ghidra/support/analyzeHeadless`.

**AArch64 objdump is required** — host `objdump` cannot disassemble AArch64:
```bash
/usr/bin/aarch64-linux-gnu-objdump -d -C --start-address=0x0035600 libqsgepaper.so
```

Headless Ghidra import:
```bash
/opt/ghidra/support/analyzeHeadless /home/manuel/ghidra-projects paper_pro_display_stack \
  -import libqsgepaper.so \
  -analysisTimeoutPerFile 3600 \
  -scriptPath scripts/ \
  -postScript FindPaperProDisplaySymbols.java
```

## Class hierarchy

From RTTI/vtable relocations and constructor disassembly:

```
EPFramebuffer (base)
  ├── QObject
  ├── EPContentMap (4-slot content classifier)
  ├── EPScreenModeMap (6-mode screen mode map)
  └── two QImage buffers

EPFramebufferSwtcon (intermediate)
  └── internal thread, initialize(), sync(), temperature()

EPFramebufferAcep2 (Paper Pro concrete)
  └── QTimer, scheduleTModeUpdate(), delayTModeUpdate(), swapBuffers_impl()
```

Singleton construction (from disassembly):
```asm
EPFramebuffer::instance():
  ; takes mutex, uses once-guard
  sub  sp, sp, #0x110          ; allocates 0x110 bytes
  bl   EPFramebufferAcep2::EPFramebufferAcep2()
  ; stores result in g_EPFramebuffer_singleton_slot

EPFramebufferAcep2::EPFramebufferAcep2():
  bl   EPFramebufferSwtcon::EPFramebufferSwtcon()  ; calls base first
  ; then: constructs QTimer, rebuilds maps, sets interval=1500ms

EPFramebufferSwtcon::EPFramebufferSwtcon():
  bl   EPFramebuffer::EPFramebuffer()  ; base constructor first
  ; then: starts internal thread, checks /tmp/epframebuffer.lock
  ; calls initialize(), setBuffers()
```

The singleton pattern directly constructs `EPFramebufferAcep2` — no factory or chooser. This is the Paper Pro build, so the ACEP2 backend is hardcoded.

## EPContentMap: content classification

The content map classifies rendered content into 4 buckets. From `EPContentMap::setTypeForRect()` disassembly and `dump()` strings:

```cpp
// 4 slots: slot 0 is hidden default, slots 1-3 are named
// - mono
// - grayscale
// - color

// Loop in setTypeForRect:
for (slot = 0; slot < 4; slot++) {
    // classify rect content into appropriate slot
}

// dump() prints only 3 named buckets (slot 0 is background/default)
```

The content classification is done per-rectangle before calling `swapBuffers_impl`. The classifier likely examines pixel values in the rendered QImage to determine whether a region contains mono (black/white), grayscale, or color content.

## EPScreenModeMap: display modes

From `EPScreenModeMap::region()` and string evidence:

```
Values 0..5 are valid:
  0 = Pen
  1 = Mono
  2 = Animation
  3 = UI
  4 = Content
  5 = Sleep
  6 = LastScreenMode (sentinel/warning value)
```

The `dump()` function warns if an invalid mode > 5 is passed. This is the semantic layer: different e-ink waveform/lut selections for different content types. "Pen" mode is optimized for low-latency stylus tracking (fewer waveform phases). "UI" mode is for interface elements. "Content" mode is for full-resolution document rendering.

## swapBuffers_impl: the core update policy

From disassembly of `EPFramebufferAcep2::swapBuffers_impl()`:

```cpp
void EPFramebufferAcep2::swapBuffers_impl(...) {
    // 1. Inspect screen-mode buckets (from EPScreenModeMap)
    //    Which modes are active in the current update region?

    // 2. Inspect content/coverage buckets (from EPContentMap)
    //    What type of content is in the dirty region?
    //    Is coverage above threshold?

    // 3. Check temperature via Swtcon::temperature()
    //    Read EPFB_HIGHTEMP_TMODE_THRESHOLD env var
    //    If temp > threshold: use slower waveform (quality mode)
    //    If temp < threshold: use faster waveform (performance mode)

    // 4. Compute region: potentially split into sub-regions
    //    If content changes across region: partition by content type
    //    "merged UI/Content" string suggests bucket collapsing

    // 5. For each sub-region, call:
    Swtcon::update(rect, mode, pixelMode, flags);

    // 6. Schedule or delay T-mode (temperature-compensated waveform):
    //    scheduleTModeUpdate() — QTimer-based deferred update
    //    delayTModeUpdate() — explicit wait
    //    sendTModeUpdate() — immediate mutex-protected send
}
```

The `update()` calls use `(mode, pixelMode, flags)` tuples. From disassembly, the observed tuples include:

```
(update rect w3, w4, w5) where:
  w3 = update mode (1=normal, 2=fast, 5=quality, 6=ultra-quality)
  w4 = pixel mode (7=normal, 15=duochrome, 17=partial)
  w5 = flags (0=no-verify, 1=verify, 8=skip-buffer-check)
```

Multiple calls per `swapBuffers_impl` invocation — not a single buffer flip, but a sequence of targeted region+mode updates.

## Ghost control

`EPFramebuffer::ghostControl()` handles display-wide sp'ecial modes:

```cpp
void EPFramebuffer::ghostControl(int mode) {
    if (mode == 1) {
        // Set internal byte flag, return immediately
        // → Screen goes "ghost" (last frame held, no updates processed)
    } else {
        // Lock, build full-screen region from image rect,
        // call swapBuffers() with special flags,
        // invoke virtual callback,
        // clear flag
        // → Known modes: BlinkNow, BlinkLater, BleachNow, FactoryReset
    }
}
```

The "ghost" mode is likely used during sleep/idle or when the app is backgrounded.

## Temperature compensation

`EPFramebufferAcep2::scheduleTModeUpdate()`:

```cpp
void EPFramebufferAcep2::scheduleTModeUpdate() {
    // Must be called on the EPFramebuffer thread
    // Reads: EPFB_HIGHTEMP_TMODE_THRESHOLD from environment
    // Compares: against Swtcon::temperature()
    // If conditions met: starts QTimer(1500ms, single-shot)
}
```

The temperature check gates whether a slower/high-quality waveform is used. High temperature increases e-ink refresh latency, so the controller switches to a different waveform family above the threshold.

## Singleton slot and vtable addresses (confirmed)

From Ghidra and relocation analysis:

```
g_EPFramebuffer_singleton_slot:  address 0x1a2c0a8
EPFramebuffer::instance():       address 0x97a6e0
EPFramebuffer::ctor():            address 0x98ed40
EPFramebufferAcep2::ctor():      address 0x98f2c0
EPFramebufferSwtcon::ctor():     address 0x99b240
EPFramebufferAcep2::swapBuffers_impl: address 0x98aaa0  (STRONG candidate)

Base vtable:  0x1528af8
Acep2 vtable: 0x1528948
```

## Annotation notation used

For Ghidra comment annotations:

```
[PPA:<class>:<confidence>:<evidence>]
class:  FUNC, DATA, VTBL, SLOT, FLOW
confidence: CONF, STRONG, HYP, OPEN
evidence:   STR, CFG, VFT, CMP, RT, OPS, RTTI

Examples:
[PPA:FUNC:STRONG:CFG,VFT]  — strongly confirmed function, based on CFG and vtable
[PPA:DATA:HYP:STR]          — hypothesized data, based on string evidence
[PPA:VTBL:STRONG:RTTI,VFT]  — strongly confirmed vtable, RTTI + vtable relocation
```

## Runtime preload strategy: from DRM to EPFramebuffer

The initial runtime strategy was a libdrm-level `LD_PRELOAD` spy (`drm_spy.so`). That revealed the atomic commit pattern but not the property semantics.

The refined strategy is EPFramebuffer-level interposition:

```bash
# Hook the singleton to intercept initialization
# Hook swapBuffers_impl to capture update tuples
# Hook Swtcon::update to log (rect, mode, pixelMode, flags) for each call
```

The singleton is at `0x97a6e0`. The `swapBuffers_impl` slot in the Acep2 vtable (offset from `0x1528948`) is the most promising hook point.

## Current status

- Class hierarchy fully recovered
- Singleton construction path confirmed
- Content and screen mode maps understood (4 slots, 6 modes)
- `swapBuffers_impl` policy partially recovered (partitioning, temperature, tuple sequences)
- Ghidra project exists at `/home/manuel/ghidra-projects/paper_pro_display_stack`
- Annotation batch applied and exported

Remaining work:
- Decode exact DRM atomic property IDs and values during drawing
- Determine whether EPFramebuffer policy is reproducible via DRM alone or requires the proprietary layer
- Investigate whether third-party apps can create `EPFramebuffer`-compatible buffers

## Ghidra workflow reference

```bash
# Headless import
/opt/ghidra/support/analyzeHeadless $PROJDIR $PROJNAME \
  -import $BINARY -analysisTimeoutPerFile 3600

# Headless annotation
/opt/ghidra/support/analyzeHeadless $PROJDIR $PROJNAME \
  -postScript AnnotateXochitlEpframebufferCandidates.java \
  -scriptPath scripts/ -analysisTimeoutPerFile 60

# Headless annotation dump
/opt/ghidra/support/analyzeHeadless $PROJDIR $PROJNAME \
  -postScript DumpXochitlEpframebufferAnnotations.java \
  -scriptPath scripts/ -analysisTimeoutPerFile 60
```

## Key binaries and paths

```
Primary target:     /opt/codex/ferrari/5.6.75/sysroots/.../libqsgepaper.so
xochitl (device):   /usr/bin/xochitl
libepaper (device): /usr/lib/plugins/platforms/libepaper.so
Waveform files:     /usr/share/remarkable/*.eink
Lock file:          /tmp/epframebuffer.lock
Ghidra project:     /home/manuel/ghidra-projects/paper_pro_display_stack.gpr
```

## Open questions

- Are the DRM atomic properties used by EPFramebuffer public KMS properties or vendor-private ones?
- Can a third-party app register as the EPFramebuffer owner (via the lock file), or is that restricted to xochitl?
- What is the minimum DRM atomic property set needed to produce an e-ink update on Paper Pro?
- Is the waveform file format documented anywhere, or fully proprietary?

## Related notes

- [[PROJ - Paper Pro E-Ink - DRM/KMS Fast Mode Investigation]] — the runtime trace and DRM/KMS evidence
- [[PROJ - Paper Pro E-Ink - Pen Input and SDK Build Fix]] — the evdev pen input architecture
