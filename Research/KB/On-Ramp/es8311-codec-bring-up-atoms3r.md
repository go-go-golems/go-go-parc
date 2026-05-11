---
title: "ES8311 Codec Bring-Up on AtomS3R + Atomic Echo Base"
aliases:
  - es8311 atoms3r
  - atoms3r audio bring-up
  - es8311 bring-up
  - atomic echo base audio
tags: [knowledge-base, on-ramp, esp32, esp-idf, audio, es8311, atoms3r]
status: active
type: knowledge-base
created: 2026-05-11
---

# ES8311 Codec Bring-Up on AtomS3R + Atomic Echo Base

> [!summary]
> The ES8311 is the audio codec used in the AtomS3R-CAM + Atomic Echo Base combination. The hard part is not “how I2S works” in the abstract. The hard part is the exact board wiring: I2C pins, I/O expander unmute, I2S routing, and clock assumptions. This entry is the practical orientation we wished existed before doing the bring-up.

## The idea in one paragraph

The audio path has three pieces:
1. an ESP32-S3 host,
2. an ES8311 codec reachable over I2C and fed by I2S,
3. an output path gated by an I/O expander that must be unmuted before you hear anything.

If any one of those pieces is wrong, the system “builds fine” and produces silence.

## Why we care

[[PROJ - Wi-Fi Audio Cues Lab - ESP32-S3 Audio Feedback for Wi-Fi Events]] depends on this exact stack. The project proved that short audio cues on this board are practical, but only after finding the real pin map and the mute-gating sequence.

## The board-specific facts that matter

For the AtomS3R-CAM + Atomic Echo Base assembly used in our project, the important pin map is:

| Function | GPIO |
|----------|------|
| I2C SDA | 38 |
| I2C SCL | 39 |
| I2S DOUT | 5 |
| I2S WS | 6 |
| I2S BCLK | 8 |
| I2S DIN | 7 |

The codec is not the only thing on the path. The speaker path is gated by a PI4IOE5V6408 I/O expander. If that expander is not configured correctly, the codec can be fully initialized and the speaker still stays silent.

## The practical bring-up order

Do not debug everything at once. The working order is:

1. prove the console works,
2. prove the codec and expander are reachable over I2C,
3. play one direct tone,
4. only then test queued cues and event-driven playback.

This is the same layered bring-up discipline we use elsewhere, but here it matters especially because silence does not tell you *which* layer is broken.

## The gotchas we've hit

**Wrong board assumptions.** The standalone Atom EchoS3R board uses different assumptions than the AtomS3R-CAM + Atomic Echo Base kit. Borrowing the wrong pin map makes the codec look dead.

**Mute gating is separate from codec init.** The codec can be alive while the output path is still muted. This is why “I can read codec registers” is not the same as “audio output works.”

**Clock assumptions matter.** Our path is hardcoded for a specific playback setup, not a generic audio engine. If you change sample-rate assumptions casually, the codec may initialize but not render useful sound.

**Silence is ambiguous.** Silence can mean: wrong I2C pins, wrong I2S pins, muted output path, wrong sample format, or gain too low.

## The minimum useful test

A direct tone command is more valuable than a fancy cue system during bring-up. A 440 Hz tone for a fixed duration proves:
- the REPL works,
- the control path works,
- the codec path works,
- the speaker path is unmuted,
- and the board is physically capable of audible output.

Only after that should you test multi-step cues.

## Where to go deeper

- [[PROJ - Wi-Fi Audio Cues Lab - ESP32-S3 Audio Feedback for Wi-Fi Events]] — the full implementation and runbook
- ES8311 datasheet — codec register-level reference
- ESP-IDF I2S docs — transport layer details
