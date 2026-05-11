---
title: "Web Serial from the Browser to Embedded Devices"
aliases:
  - web serial
  - browser serial
  - navigator.serial
  - browser to esp32 serial
tags: [knowledge-base, on-ramp, web-serial, browser, serial, embedded, esp32]
status: active
type: knowledge-base
created: 2026-05-11
---

# Web Serial from the Browser to Embedded Devices

> [!summary]
> The Web Serial API lets a browser talk directly to a USB-attached device without a native desktop app. MDN documents the API, but not the working end-to-end pattern for embedded devices: open the port, read bytes continuously, decode text, split frames, and keep a tiny smoke page for transport isolation.

## The idea in one paragraph

Web Serial exposes a serial port to JavaScript through `navigator.serial`. The browser becomes the host app: it opens the port, reads and writes raw bytes, and translates those bytes into a line protocol, JSON messages, or whatever framing your device uses.

## Why we care

Our [[PROJ - Cardputer Web Serial Demo - Technical Project Report]] uses Web Serial as the main browser-to-device transport. The important discovery was not just that the API works — it was that the **minimal page** is the debugging tool. A tiny page that only opens the port and prints lines can prove the transport even when the full app feels haunted.

## The working pattern

The practical browser loop is:

1. ask the user for a port,
2. open it at the correct baud rate,
3. keep a reader loop alive,
4. decode bytes into text,
5. split into frames (usually newline-delimited),
6. hand complete frames to the protocol layer.

Sketch:

```js
const port = await navigator.serial.requestPort();
await port.open({ baudRate: 115200 });

const reader = port.readable.getReader();
const decoder = new TextDecoder();
let buffer = "";

while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });

  let idx;
  while ((idx = buffer.indexOf("\n")) !== -1) {
    const line = buffer.slice(0, idx);
    buffer = buffer.slice(idx + 1);
    handleLine(line);
  }
}
```

This is the real pattern. The API itself is the easy part; framing and continuous reading are the parts that make the system usable.

## Why line-oriented framing wins

For prototypes and device tools, newline-delimited frames are often ideal because they are:
- easy to log,
- easy to debug manually,
- easy to replay from Python or a shell,
- easy to inspect in both browser and firmware.

In Cardputer, NDJSON over USB Serial/JTAG is deliberately boring for exactly this reason.

## The gotchas we've hit

**The API can work while your app is broken.** This is why `smoke.html` matters. If the smoke page works and the main app doesn't, your bug is above the transport layer.

**Framing is your responsibility.** Web Serial gives you bytes, not messages. If your protocol is line-based, you must buffer partial reads and split only on complete delimiters.

**Port permissions are browser state.** The browser may remember a granted port or force you to reselect it depending on context. Treat port selection and reuse as UX state, not protocol state.

**The device can disappear mid-session.** Your read loop and write path need to handle disconnects cleanly.

## The minimal smoke page rule

When the full app behaves strangely, build a page that does only this:
- connect,
- dump incoming lines,
- send one manual test frame.

If that page works, the device, cable, USB stack, and browser transport are probably fine. Now debug the app.

## Where to go deeper

- MDN Web Serial docs: <https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API>
- [[PROJ - Cardputer Web Serial Demo - Technical Project Report]] — the full browser + firmware pattern
- [[Fundamentals/encoding-and-framing]] — why framing matters more than transport
