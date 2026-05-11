---
title: "Serial Protocols: Talking to Hardware from Go — How We Do It"
aliases:
  - serial go
  - go serial
  - uart go
  - go hardware serial
tags: [knowledge-base, tribal, serial, uart, go, hardware, embedded]
status: active
type: knowledge-base
created: 2026-05-11
---

# Serial Protocols: Talking to Hardware from Go — How We Do It

> [!summary]
> How we communicate with hardware devices over USB serial from Go: the `go.bug.st/serial` package, CTS flow control, the full-body buffer pattern for continuous streaming, and the protocol-specific framing that each device demands. The key insight: serial is not a pipe — it is a timing-sensitive channel where pauses between bytes carry meaning.

## The pattern

Serial communication is the most direct way to talk to hardware. A USB-serial adapter creates a `/dev/ttyACM0` (Linux) or `/dev/cu.usbmodem*` (macOS) device that behaves like a file — you open it, configure baud rate and flow control, then read and write bytes. But the resemblance to a file is superficial. On a file, pauses between reads are invisible. On a serial port, pauses between bytes are protocol-significant: the device's state machine may interpret a gap as a message boundary.

Our standard approach:

```go
// Open the serial port with hardware flow control
mode := &serial.Mode{
    BaudRate: 115200,
    Parity:   serial.NoParity,
    DataBits: 8,
    StopBits: serial.OneStopBit,
}
port, err := serial.Open("/dev/ttyACM0", mode)

// Enable CTS flow control — the device will pause us when its buffer is full
port.SetMode(&serial.Mode{
    BaudRate: 115200,
})

// Write a command as one continuous stream — no pauses between bytes
port.Write(append(commandHeader, pixelData...))
```

The critical constraint: **a serial command that spans multiple `Write()` calls may be interpreted differently than the same bytes sent in a single call.** The device's firmware processes bytes as they arrive, and if there's a gap (even a few milliseconds), it may decide the current message is complete and start processing it. This is the root cause of the stripe artifacts in thermal printing, the corrupted frames on the Loupedeck, and the silent failures on other serial devices.

## Why we do it this way

**CTS flow control over manual delays.** Before we discovered CTS flow control, we used `time.Sleep()` between commands to give the device time to process. This is fragile — the right delay depends on the device's buffer size, the command complexity, and the baud rate. CTS hardware flow control lets the device signal "my buffer is full, stop sending" and "I have space, resume sending." No guessing required.

**Full-body buffering before writing.** For raster commands (ESC/POS `GS v 0`, Loupedeck bitmap draws), we read the entire image into a Go byte slice before writing it to the serial port. This guarantees one continuous write with no TCP reassembly gaps, no GC pauses between chunks, and no OS scheduling delays. The alternative — reading and writing in chunks — is where the artifacts come from.

**`go.bug.st/serial` over `go.bug.st/serial.v1`.** The newer API supports `SetMode` for runtime reconfiguration (changing baud rate, enabling/disabling flow control) without closing and reopening the port. We need this for devices that change baud rate during operation.

## Where it lives

| Repo | Path | Device |
|------|------|--------|
| `corporate-headquarters/loupedeck` | `internal/serial/` | Loupedeck Live (USB serial, mutant WebSocket) |
| `2026-05-08/extract-almanach/almanach` | `internal/printer/` | K118 thermal printer (USB serial, ESC/POS) |
| `2026-04-11--loupedeck-test` | `driver/` | Loupedeck Live initial driver |

### Related PARC project reports

- [[PROJ - Loupedeck Live Hello World - Serial Go Driver]] — initial driver, mutant WebSocket discovery, rate-limiting
- [[PROJ - SToMS3R - AtomS3R Lite Thermal Printer Firmware]] — ESC/POS serial printing, full-body buffer pattern

## Common mistakes

1. **Writing multi-part commands without buffering.** If you write the `GS v 0` header, then the pixel data in a separate `Write()` call, a GC pause or OS scheduling gap between the two writes produces a visible stripe in the printed output. The printer's firmware has received the header, started reading pixel data, and then the stream stops — it interprets this as a short (corrupted) bitmap. Always buffer the full command and write it as one `Write()`.

2. **Ignoring CTS and using fixed delays instead.** `time.Sleep(100 * time.Millisecond)` between commands "works" until the device is busy and needs more time, or until you upgrade to a faster baud rate and the delay is now 10× too long. CTS flow control is hardware-mediated and adapts automatically.

3. **Not draining the read buffer.** Many devices send responses (ACK, status, sensor data) that accumulate in the OS read buffer. If you only write and never read, the buffer fills up and the device may stop sending. Start a goroutine that continuously reads from the port and dispatches responses.

4. **Cross-platform device path differences.** Linux uses `/dev/ttyACM0` or `/dev/ttyUSB0`. macOS uses `/dev/cu.usbmodemXXXX`. Windows uses `COM3`. Use `serial.GetPortsList()` to enumerate available ports, or accept a port path from the user/config.

5. **Assuming the device is ready immediately after port open.** Many USB-serial devices reset when the port is opened (the DTR signal triggers a microcontroller reset). Wait for the device to boot (typically 500ms–2s for ESP32) before sending commands. Some devices send a "ready" message; others require a specific initialization sequence.

## Variations

- **WebSocket-over-serial (Loupedeck)**: The Loupedeck's firmware 2.x wraps WebSocket framing over USB serial. The Go driver opens a serial port, performs a WebSocket handshake (HTTP upgrade request → 101 response), and then sends/receives WebSocket binary frames. Standard WebSocket libraries don't work because the device sends non-standard control frames and has rate-limiting quirks. The driver implements a custom framer.

- **ESC/POS binary commands (K118 printer)**: The K118 uses Epson's ESC/POS protocol — a sequence of binary commands with specific byte sequences. No handshake, no framing beyond the command structure. Each command starts with `ESC` (`0x1B`) or `GS` (`0x1D`), followed by command-specific bytes. The driver builds command byte slices and writes them to the serial port.
