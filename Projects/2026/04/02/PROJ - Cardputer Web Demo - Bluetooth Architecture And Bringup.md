---
title: Cardputer Web Demo Bluetooth Architecture And Bringup
aliases:
  - Cardputer Web Demo Bluetooth
  - Cardputer BLE Architecture
  - Cardputer Web Bluetooth Bringup
tags:
  - project
  - bluetooth
  - ble
  - webbluetooth
  - esp32s3
  - nimble
  - wasm
  - m5stack
status: active
type: project
created: 2026-04-02
repo: /home/manuel/code/wesen/2026-04-02--cardputer-web-demo
---

# Cardputer Web Demo: Adding Bluetooth Without Rewriting the Project

This is the Bluetooth/browser transport branch of the [[esp32]] project map.

One of the most satisfying moments in a systems project is when a new transport drops into place and the rest of the architecture barely flinches. That is what happened here.

This project began as a Web Serial demo for the **M5Stack Cardputer ADV**: firmware on an ESP32-S3 exported a tiny newline-delimited JSON protocol, the browser connected over Web Serial, and the Cardputer became a small physical frontend for a browser-native UI. The project was already interesting because it split responsibilities cleanly across embedded firmware, browser transport, UI state, and a swappable protocol engine that could run either as plain JavaScript or as Go compiled to WebAssembly.

Adding Bluetooth made the project significantly more ambitious, but also more honest. Once the architecture already says "transport is separate from protocol," the obvious next question is whether that is really true. Can the browser talk to the same device over **Web Bluetooth** instead of **Web Serial**? Can the firmware expose a BLE service without inventing a second protocol? Can the same UI and the same protocol engines continue to work without being rewritten around GATT?

The answer is yes, and the details are what make the addition interesting.

> [!summary]
> The Bluetooth work turns the project from a serial-only browser hardware demo into a dual-transport architecture:
> 1. the firmware now speaks the same NDJSON protocol over both USB Serial/JTAG and BLE
> 2. the browser now has interchangeable transport implementations for Web Serial and Web Bluetooth
> 3. the protocol engine layer remains unchanged in spirit, which proves that the original layering was real rather than accidental

## Why Bluetooth mattered here

Serial was already a good fit for bring-up because it is simple, inspectable, and easy to probe from Python. But it also anchors the project to a cable and to the ESP32-S3 USB Serial/JTAG interface. Bluetooth changes the feel of the system.

With BLE, the Cardputer is no longer just "a USB-connected embedded board with a browser page on the other end." It starts to feel like an actual browser-native peripheral. The transport becomes discoverable, wireless, and chooser-driven. The browser is still in charge, but the device is no longer tied to a debugging cable as its only host interface.

That is an architectural upgrade, not just a convenience feature.

Bluetooth also stress-tests the original design in exactly the right place. If the protocol was too entangled with Web Serial, BLE would expose that quickly. If the UI assumed serial semantics too deeply, the main page would start to collect transport-specific hacks. If the firmware had taken shortcuts that only worked because serial is a byte stream, GATT characteristics and notifications would force a rethink.

The reason the BLE addition is satisfying is that none of those worst-case outcomes happened. The project needed real implementation work, but not a conceptual rewrite.

## The core design decision: keep the protocol, change the transport

The most important decision in the Bluetooth extension was not to invent a new BLE-native message format. The firmware already had a line-oriented NDJSON protocol that worked well:

- browser-to-device commands such as:
  - `get_info`
  - `ping`
  - `set_ui_state`
  - `set_screen_text`
  - `clear_screen`
  - `beep`
- device-to-browser events such as:
  - `hello`
  - `status`
  - `key`
  - `ack`
  - `pong`
  - `error`

Those messages were already:

- small
- textual
- human-readable
- stream-friendly
- easy to log and replay

So the Bluetooth work deliberately treated BLE as a transport replacement, not as a protocol redesign.

That is a subtle but high-leverage decision. It means the new transport carries exactly the same kind of application-level message the old one carried:

```json
{"type":"cmd","name":"get_info"}
{"type":"cmd","name":"ping","nonce":"example-123"}
{"type":"cmd","name":"set_ui_state","connection":"connected","engine":"go-wasm"}
```

And the device still responds with the same kind of events:

```json
{"type":"hello","device":"m5stack-cardputer-adv","fw":"0.2.0","transport":"ble","protocol":"ndjson"}
{"type":"status","uptime_ms":159031,"connection":"disconnected","engine":"raw-js","ui_transport":"serial"}
{"type":"pong","nonce":"example-123"}
```

What changes is only how those lines move.

## How the browser architecture had to evolve

Before Bluetooth, the browser app could be mentally modeled as:

1. one UI
2. one transport
3. two protocol engines

Bluetooth forced that to become:

1. one UI
2. two transports
3. two protocol engines

That sounds like a small refactor, but it is exactly the kind of change that reveals whether the layering in a frontend is real. The browser now distinguishes two independent axes:

- **transport mode**
  - `serial`
  - `ble`
- **protocol engine mode**
  - `raw-js`
  - `go-wasm`

This is the right abstraction boundary.

The transport only owns:

- opening the session
- receiving text
- writing text
- reporting connection status

The protocol engine only owns:

- turning lines into events
- building outbound commands
- tracking parse state

The UI only owns:

- presenting the session
- routing user actions into the engine
- rendering device state and logs

That separation became concrete in the web layer with the introduction of a dedicated `BleTransport` alongside the existing serial transport. The main app can now instantiate the appropriate transport based on the selected browser mode, but the higher-level flow is unchanged:

```mermaid
flowchart LR
  UI[Main UI]
  Transport[Selected transport]
  Engine[Selected protocol engine]
  Device[Cardputer firmware]

  UI --> Engine
  Engine --> Transport
  Transport --> Engine
  Transport <-->|NDJSON text| Device
```

The value of this is not only code cleanliness. It also means the project can make interesting combinations explicit:

- Web Serial + Raw JS
- Web Serial + Go/WASM
- Web Bluetooth + Raw JS
- Web Bluetooth + Go/WASM

That is a much richer matrix than the original demo, and it comes from a relatively small architectural generalization.

## Web Bluetooth in practice

Web Bluetooth is not just Web Serial with a different constructor. The browser does not open a byte stream to a serial port; it discovers a BLE peripheral, connects to a GATT server, and interacts with named characteristics.

That changes the transport implementation in very specific ways.

### The peripheral identity

The device now advertises under the name:

- `CardBLE`

And exposes a custom GATT service:

- service UUID: `19b10000-e8f2-537e-4f6c-d104768a1214`

with two characteristics:

- RX characteristic:
  - `19b10001-e8f2-537e-4f6c-d104768a1214`
  - browser writes commands here
- TX characteristic:
  - `19b10002-e8f2-537e-4f6c-d104768a1214`
  - firmware notifies events here

This is intentionally minimal. There is one write path and one notify path. That is enough to emulate the original serial contract while staying very readable at the GATT level.

### What the browser transport actually does

The BLE transport has to:

1. call the browser chooser
2. filter or recognize the target peripheral
3. connect to the GATT server
4. resolve the custom service
5. resolve RX and TX characteristics
6. subscribe to notifications on TX
7. write NDJSON command lines to RX

At that point the rest of the app can keep thinking in text lines. That is the real win. BLE is encapsulated where it belongs: in the transport implementation, not in the UI or engine.

### Why the BLE smoke page matters

The project already benefited from having a very small `smoke.html` page for Web Serial. Bluetooth needed the same treatment.

The dedicated `ble-smoke.html` page is important because it reduces the problem size dramatically. Instead of debugging BLE through the entire main app, the smoke page can answer the first-order questions directly:

- does the browser see the device?
- can it connect?
- can it subscribe to notifications?
- can it send `get_info`?
- does it receive `hello` and `status`?

That is not just convenient. It is good engineering practice for transport bring-up. A smaller surface gives a clearer answer.

## How the firmware had to change

The firmware work is where the Bluetooth addition becomes mechanically real. The serial-only version already had:

- a device state model
- a render loop
- keyboard input handling
- command parsing
- periodic `status` emission

To add BLE properly, the firmware needed to become a dual-transport endpoint.

### NimBLE as the BLE host stack

On ESP-IDF 5.4, the implementation uses **NimBLE**, not Bluedroid. That is the right fit here because the project needs a lean BLE peripheral with custom GATT service definitions rather than a large classic-Bluetooth stack.

The firmware now initializes:

- NVS for BLE state storage requirements
- NimBLE host via `nimble_port_init()`
- GAP and GATT helper services
- the custom GATT service table
- the host sync callback that sets the device address and starts advertising

The custom service is defined in the firmware using:

- one RX characteristic for command writes
- one TX characteristic for notifications

This is exactly the minimal GATT shape the project needs.

### BLE link state becomes part of the runtime

The firmware now maintains BLE-specific link state alongside the serial-oriented device state. That includes:

- whether a BLE central is connected
- whether notifications are enabled
- the connection handle
- the negotiated MTU
- the maximum payload size for notifications
- an RX buffer for assembling incoming command text

That is an important step because BLE is not just another output channel. It has real session state that must be tracked independently of the browser-facing UI labels.

### Notifications instead of raw stream writes

On the serial side, emitting a line is conceptually easy: write bytes to `usb_serial_jtag_write_bytes(...)` and you are done.

On the BLE side, the same event has to be delivered through characteristic notifications. That creates two practical concerns:

1. notifications are only meaningful after the client subscribes
2. payload size is constrained by the negotiated MTU

This is why the firmware tracks whether notifications are enabled and what the effective payload ceiling is. The BLE path is still NDJSON, but it cannot pretend that the transport beneath it is an unbounded text stream.

The implementation therefore has to be aware of chunking and notification readiness while still presenting a simple line-oriented interface to the rest of the firmware.

That is exactly the right shape: BLE-specific complexity is localized in the transport handling, not smeared across the command and event model.

## What changed in the protocol surface

Interestingly, the Bluetooth addition did not require much protocol expansion. The important additions are more about self-description than about new command categories.

The firmware now reports transport-related metadata such as:

- `transport: "ble"` in the BLE `hello` response
- BLE service and characteristic UUIDs in the `hello` message
- BLE link status in `status`
- UI transport awareness via `ui_transport`

This is valuable because it lets the device explain its current understanding of the session instead of forcing the browser to infer everything from context.

A BLE-side `hello` frame now looks like this in spirit:

```json
{
  "type": "hello",
  "device": "m5stack-cardputer-adv",
  "fw": "0.2.0",
  "transport": "ble",
  "protocol": "ndjson",
  "ble_service": "19b10000-e8f2-537e-4f6c-d104768a1214",
  "ble_rx": "19b10001-e8f2-537e-4f6c-d104768a1214",
  "ble_tx": "19b10002-e8f2-537e-4f6c-d104768a1214"
}
```

That kind of explicitness is useful far beyond debugging. It makes the device self-describing, which is exactly what you want in a transport-flexible architecture.

## The actual bring-up story

The Bluetooth work was not just a matter of adding code and trusting it. The imported branch arrived with the right overall shape, but the firmware side still had compile blockers. That is an important detail because it says something about the nature of the work: the feature idea was already correct, but the implementation had not fully crossed the line into reality.

The main blockers were all concentrated in the NimBLE/C++ integration:

- designated initializer ordering in the GATT definitions
- a bad advertisement-name initialization pattern
- a missing include for `ble_hs_util_ensure_addr(...)`

Those are the kinds of issues that often appear when C-oriented embedded examples are ported into a C++ firmware codebase. They are not architectural problems. They are integration problems.

Once those were fixed, the new Bluetooth path moved quickly from "plausible" to "real":

1. the firmware built successfully under ESP-IDF 5.4
2. the firmware flashed successfully to the connected Cardputer ADV
3. the Linux host discovered the peripheral as `CardBLE`
4. a standalone GATT probe connected and subscribed successfully
5. the probe received initial `hello` and `status` events
6. the probe sent real NDJSON commands and got correct responses

That host-side probe validated the most important round-trips:

- `set_ui_state` -> `ack`
- `get_info` -> `hello`
- `ping` -> `pong`

At that point the BLE extension stopped being speculative. The device was really advertising, really accepting commands, and really sending NDJSON notifications back.

## Why this extension is architecturally satisfying

Many transport additions make a codebase worse before they make it better. They expose hidden coupling, trigger awkward branching, and leave behind a trail of "if transport == X" conditionals in places that should never have learned about transports in the first place.

This Bluetooth addition is satisfying because it mostly did the opposite.

It clarified the system:

- transport is now explicit
- protocol is now more clearly transport-independent
- the firmware is more honestly multi-channel
- the smoke-test philosophy became more central, not less

It also makes the project more legible as a design artifact. The system now says something concrete:

> a browser can talk to a small embedded device over multiple host-native transports if the wire protocol is simple, the transport layer is isolated, and the device remains self-describing

That is a surprisingly strong statement for such a compact repo.

## The role of Go/WASM after Bluetooth

One of the nicest aspects of the BLE work is that it did not invalidate the earlier experiment with dual protocol engines. The Raw JS engine and the Go/WASM engine still sit above transport.

That means the browser can, in principle, use the same WASM-based protocol logic over either:

- Web Serial
- Web Bluetooth

This matters because it proves the original protocol-engine abstraction is not merely a serial-specific convenience. It survives a transport expansion.

That makes the WASM part of the project more compelling, not less. It is no longer just "Go running in the browser for fun." It is now part of a layered architecture where transport and protocol are clearly distinct concerns.

## What is still worth validating

The device-side BLE path now has solid proof behind it:

- build
- flash
- advertising
- GATT connection
- notify
- command writes
- response round-trips

The remaining work is mostly browser-level proof in Chromium:

- `ble-smoke.html`
- main app with BLE + Raw JS
- main app with BLE + Go/WASM

That is no longer foundational risk. It is the last user-facing validation pass.

And that difference matters. The project is no longer asking, "can BLE be made to work at all?" It is asking, "does the browser-facing experience now match the underlying device capability?"

That is a much healthier place to be.

## Why this makes the whole project cooler

Before Bluetooth, the project was already a neat demonstration of:

- embedded firmware talking directly to the browser
- a physical device UI cooperating with a web UI
- protocol logic that could run in either JavaScript or Go/WASM

After Bluetooth, the project becomes more ambitious in a very grounded way. It is no longer just a cable demo. It is a general browser-connected peripheral architecture for a Cardputer ADV with interchangeable transports and interchangeable protocol engines.

That makes it feel less like a one-off experiment and more like a reusable pattern:

- choose a physical device with a compact local UI
- expose a tiny explicit protocol
- keep transport separate from protocol
- keep protocol separate from the page
- add small transport-specific smoke pages

If you do that, you get a system that can grow without collapsing into complexity.

That is what makes this Bluetooth addition interesting. It is not impressive because Bluetooth exists. It is impressive because the project was structured well enough that Bluetooth could be added without changing what the project fundamentally is.

## Final assessment

The Bluetooth addition upgrades the Cardputer Web Demo from a Web Serial experiment into a genuinely multi-transport browser-device system.

Technically, the important achievements are:

- a custom BLE GATT service on the ESP32-S3 using NimBLE
- a browser-side `BleTransport` alongside Web Serial
- preservation of the existing NDJSON application protocol
- preservation of the Raw JS and Go/WASM engine split
- transport-first validation through a dedicated BLE smoke path and a standalone GATT probe

Architecturally, the more important achievement is that the project stayed honest. The protocol really was separate from the transport. The browser really could be transport-agnostic. The firmware really could become dual-transport without abandoning the simple state-and-events model that made the original demo understandable.

That is the best outcome a feature like this can have. The system becomes more capable, but also more clearly designed.
