---
title: "Encoding and Framing: Turning Bytes into Messages"
aliases:
  - protocol framing
  - message encoding
  - wire format
  - serialization
tags: [knowledge-base, fundamental, encoding, framing, protocol, serialization]
status: active
type: knowledge-base
created: 2026-05-11
---

# Encoding and Framing: Turning Bytes into Messages

> [!summary]
How we turn raw byte streams into structured messages — the layer between "bytes on a wire" and "meaningful protocol." This is the hidden problem behind every serial device, every printer command, and every network protocol we implement. Getting framing wrong is the number one cause of data corruption in our hardware projects.

## The core idea

A **byte stream** (UART, TCP, USB serial) delivers an undifferentiated sequence of bytes. There are no boundaries between "messages." If you send "HELLO" and then "WORLD", the receiver might read "HELL" and then "OWORLD" — the stream doesn't know where one message ends and the next begins.

**Framing** is the act of adding structure to a byte stream so the receiver can separate individual messages. Every protocol does this differently, and the choice of framing determines what can go wrong.

**Encoding** is the act of mapping structured data (integers, strings, bitmaps) into the bytes that make up a framed message. This includes byte order (endianness), bit packing, length prefixes, and checksums.

## Why it matters to our work

Three of our KB entries depend on this:

- **On-Ramp: ESC/POS Thermal Printer Commands** — The `GS v 0` command is a length-prefixed binary frame: command bytes + width/height fields + pixel data. If framing is wrong (e.g., missing bytes, wrong byte order), the printer produces garbage or nothing.
- **Tribal: Serial Protocols from Go** — The Loupedeck uses "mutant WebSocket over serial" framing. Standard WebSocket libraries can't parse it. We had to learn its specific framing to talk to it.
- **Tribal: ESP-IDF Firmware Patterns** — Our `POST /api/print/bitmap` endpoint must read the entire body before sending to UART, because gaps in the UART stream inside a raster command corrupt the print.

Every hardware integration project we've done has hit a framing problem. The symptoms are always the same: garbage output, silent failures, or protocol desynchronization. The root cause is always the same: the receiver assumed a different framing than the sender.

## The key result

**Any byte stream protocol needs an unambiguous way to delimit messages.** There are three fundamental approaches:

1. **Length-prefixed framing**: Each message starts with a fixed-length header that encodes the message length. The receiver reads the header, then reads exactly that many bytes. ESC/POS `GS v 0` uses this: `1D 76 30 00 xL xH yL yH [data]`.

2. **Delimiter-based framing**: Messages are separated by a special byte sequence (like `\n` for line-based protocols, or `0x7E` for HDLC). The delimiter must be escaped if it appears in the data. HTTP uses `\r\n\r\n` as a header delimiter.

3. **State-machine framing**: The protocol has distinct states (handshake, header, payload, checksum) and the receiver transitions between them based on byte values. WebSocket framing is state-machine-based: opcode, mask bit, length, payload.

The critical property is **resynchronization**: if the receiver gets out of sync (dropped byte, noise), can it find the start of the next message? Length-prefixed framing resyncs after the next length field. Delimiter-based framing resyncs at the next delimiter. State-machine framing may never resync without an explicit reset.

## The intuition behind the key result

Think of framing like reading a book where someone removed all the spaces and punctuation. "HELLOWORLDISTHISONEWORDORTWO" is ambiguous. Add spaces and it's clear: "HELLO WORLD IS THIS ONE WORD OR TWO."

Length-prefix framing is like numbered paragraphs: "5:HELLO 5:WORLD" — each starts with its length. Delimiter framing is like periods: "HELLO. WORLD." State-machine framing is like a table of contents that tells you the structure before you read.

Our serial devices use all three approaches:
- **K118 thermal printer**: Length-prefixed (GS v 0 header with width/height, then exact-length payload)
- **Loupedeck**: State-machine (WebSocket handshake, then binary/text frames with opcode+length headers)
- **Simple text protocols**: Delimiter (newline-separated commands)

## What goes wrong when you don't know this

1. **SToMS3R: stripe artifacts from TCP gaps** — If the ESP32 reads the HTTP body in chunks and writes each chunk to UART immediately, gaps between chunks (TCP reassembly delays, Wi-Fi jitter) appear as pauses in the UART stream. The printer interprets these as message boundaries, corrupting the bitmap. Fix: read the entire body into memory first, then send as one continuous stream.

2. **Loupedeck: WebSocket parser panic** — The device sends malformed WebSocket control frames (FIN bit not set). Standard gorilla/websocket parser panics. Fix: rate-limit draws and handle non-standard frames gracefully.

3. **Bit packing off by one** — The K118 expects MSB-first packing: leftmost pixel = bit 7 of byte 0. If you pack LSB-first (common in some graphics libraries), the image prints mirrored. This is an encoding error, not a framing error, but it's in the same layer.

## Where we use it

- [[On-Ramp/esc-pos-thermal-printer]]
- [[Tribal/serial-protocols-from-go]]
- [[Tribal/esp-idf-firmware-patterns]]

### Related PARC project reports

- [[PROJ - SToMS3R - AtomS3R Lite Thermal Printer Firmware]] — stripe artifacts from TCP gaps inside raster commands
- [[PROJ - Loupedeck Live Hello World - Serial Go Driver]] — WebSocket parser panic from non-standard framing

## Where to go deeper

1. **Tanenbaum, A. S. & Wetherall, D. J. (2011)**. *Computer Networks*, 5th ed. Pearson. Chapter 3 covers framing, byte stuffing, and bit stuffing — the fundamental techniques.
2. **Epson ESC/POS Application Programming Guide** — The specific framing used by thermal printers. Available from Epson's developer portal.
3. **RFC 6455 (WebSocket Protocol)** — The framing format that the Loupedeck adapts (with device-specific quirks).
