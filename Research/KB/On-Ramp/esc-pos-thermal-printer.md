---
title: "ESC/POS Thermal Printer Commands"
aliases:
  - esc pos
  - esc/pos
  - thermal printer commands
  - k118 printer
  - gs v 0
tags: [knowledge-base, on-ramp, esc-pos, thermal-printer, printer, embedded]
status: active
type: knowledge-base
created: 2026-05-11
---

# ESC/POS Thermal Printer Commands

> [!summary]
> ESC/POS is the command language that Epson thermal printers speak. It's a binary protocol where you send byte sequences to control printing, paper feeding, barcodes, and bitmaps. This entry covers the commands we actually use (about 12 out of the 200+ in the spec), the bitmap raster command that prints images, and the timing constraint that causes most printing failures.

## The idea in one paragraph

A thermal printer is a stateful device connected over serial. You send it commands — byte sequences starting with `ESC` (0x1B) or `GS` (0x1D) — and it executes them in order. There is no response for most commands. The printer doesn't confirm success; it either prints or silently fails. Debugging is visual: you print a test pattern and look at the paper.

## The commands we use

| Command | Bytes | What it does |
|---------|-------|-------------|
| Initialize | `1B 40` | Reset to power-on defaults. Send this first. |
| Print + feed | `1B 64 n` | Print buffer + feed n lines. |
| Line feed | `0A` | Feed one line. |
| Set justification | `1B 61 n` | 0=left, 1=center, 2=right |
| Bold on/off | `1B 45 n` | 0=off, 1=on |
| Underline on/off | `1B 2D n` | 0=off, 1=1px, 2=2px |
| Cut paper | `1D 56 n` | 0=full cut, 1=partial cut, 66=feed+full |
| Print barcode | `1D 6B m d1..dk 00` | Print barcode type m with data d |
| **Print raster bitmap** | `1D 76 30 m xL xH yL yH d1..dk` | The image printing command |
| Status request | `1D 48 n` | Return printer status byte |

Everything else in the 200-page Epson specification is noise for our use cases. The bitmap command is the one that matters.

## The raster bitmap command in detail

`GS v 0` (`1D 76 30`) prints a bitmap image. The command structure:

```
1D 76 30  m   xL  xH  yL  yH  d1 d2 d3 ... dk
|        |   |   |   |   |   |   |              |
cmd      mode  width    height   pixel data
               (bytes)  (dots)
```

- **m**: Mode. `00` = normal, `01` = double width, `02` = double height, `03` = double both.
- **xL, xH**: Width in bytes (8 pixels per byte). Width = xL + xH × 256. The K118's print area is 384 dots wide = 48 bytes.
- **yL, yH**: Height in dots. Height = yL + yH × 256. Maximum height depends on printer memory; the K118 can handle up to ~1666 dots at 384 width.
- **d1..dk**: Pixel data. `k = width × height` bytes. MSB-first: bit 7 of byte 0 is the leftmost pixel of the first row.

The pixel data must be packed as described in [[dithering-and-rasterization]]. The entire command — header + pixel data — must be sent as one continuous stream. This is the timing constraint that causes most failures.

## The timing constraint

The `GS v 0` command has no flow control at the application level. The printer receives bytes at the serial baud rate and processes them as they arrive. If there is a gap in the byte stream — even a few milliseconds — the printer may interpret it as the end of the command and start printing with whatever data it has so far.

This produces **stripe artifacts**: a partially printed bitmap where some rows are correct and others are missing or shifted. The artifact is always a horizontal stripe — the printer prints what it has, then feeds paper, then the next command's bytes arrive and get interpreted as a new (corrupted) command.

The fix is the full-body buffer pattern described in [[serial-protocols-from-go]] and [[encoding-and-framing]]: read the entire HTTP POST body into memory, pack the complete `GS v 0` command, and write it to the serial port in one `Write()` call. No chunked writes, no streaming, no read-write interleaving.

## The gotchas we've hit

**Width must be a multiple of 8.** The printer prints 8 pixels per byte. If your image is 380 pixels wide, pad it to 384 (48 bytes per row). The extra 4 pixels print as white.

**Byte order is little-endian for multi-byte fields.** xL/xH and yL/yH are little-endian: the low byte comes first. For a 48-byte-wide, 1200-dot-tall image: `xL=48, xH=0, yL=176, yH=4` (because 1200 = 176 + 4×256).

**9600 baud is slow for bitmaps.** A 384×1200 bitmap (57,600 bytes) takes ~60 seconds at 9600 baud. At 115200 baud, it takes ~5 seconds. But some K118 units are unreliable above 115200 — test your specific hardware.

**The K118 ignores some commands.** Barcode printing, status requests, and some paper-cut modes are not supported on all K118 firmware versions. Test each command; don't assume the spec applies.

## Where to go deeper

- **Epson ESC/POS Application Programming Guide** — The authoritative reference. Search for "ESC/POS" on Epson's developer portal.
- [[On-Ramp/dithering-and-rasterization]] — How to prepare the image data that goes into `GS v 0`.
- [[Fundamentals/encoding-and-framing]] — Why the command structure is a length-prefixed binary frame and what happens when framing breaks.
- [[PROJ - SToMS3R - AtomS3R Lite Thermal Printer Firmware]] — full implementation: GS v 0 command, MSB-first packing, stripe-artifact debugging
