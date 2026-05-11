---
title: "PARC Project Index: Repos, Concepts, and Knowledge Base Gaps"
doc-type: reference
topics: parc, projects, knowledge-base, repos, concepts
owners: manuel
created: "2026-05-11"
updated: "2026-05-11"
---

# PARC Project Index: Repos, Concepts, and Knowledge Base Gaps

> [!note]
> This is the canonical location for the project index. When analyzing new projects, update this file. The copy in `ttmp/.../PARC-001/reference/` is the original from the initial batch analysis and should not be edited directly.

This document maps project reports in the go-go-parc library to their source repositories, identifies fundamental technology concepts that warrant dedicated knowledge base entries, and explicitly lists **tribal candidates** (our-specific patterns) per project so future analysts can count and cross-reference them.

See [[building-knowledge-base]] for the KB authoring playbook, decision rules, and entry templates.

---

## Batch 1: Representative Initial Sample (8 projects)

---

### 1. Smalltalk-80 VM — Blue Book Interpreter in Go

**Date**: 2026-03-18

**Summary**: A Go implementation of the Smalltalk-80 virtual machine reconstructed from the Blue Book specification. Not a "Smalltalk-like" runtime — a faithful Blue Book VM that boots real Smalltalk images, runs the scheduler, and exercises the full object-memory model. The project's discipline is strict: the Blue Book is the primary specification, and other implementations are not used as hidden oracles. The hardest bugs were specification-interpretation bugs (bit numbering, header decoding, selector cache hashing), not missing features.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-17--smalltalk` | Main VM implementation, boot traces, OCR Blue Book extracts |

**Tribal candidates** (our-specific patterns — even if only this project uses them):
- **Spec-first implementation discipline**: Building from a formal specification instead of referencing another implementation as an oracle. The Blue Book is the authority; other VMs are not consulted for design decisions. This pattern avoids "cargo-cult" bugs where you copy behavior you don't understand.
- **Regression-trace-driven debugging**: Running known-good image traces against the VM and comparing step-by-step to find divergence. The project uses `data/trace2`, `data/trace3` as regression baselines.
- **Go struct packing for VM word formats**: How we map Smalltalk's object-pointer encoding (object table entries, header fields, odd-word base pointers) onto Go structs without resorting to raw byte manipulation everywhere.

**On-Ramp concepts this project depends on**:
- Stack-based virtual machine architecture
- Object memory models (object table vs direct pointer)
- Image-based persistence (snapshot/restore)
- Bytecode instruction set design
- Garbage collection (mark/sweep)

**Fundamental concepts this project rests on**:
- Von Neumann vs Harvard execution models
- Process scheduling and semaphores
- Tagged pointer representations

---

### 2. Gnosis Layout Engine — PaperS3 E-Ink UI Operating System

**Date**: 2026-03-22

**Summary**: A tree-based UI layout engine running on the M5Paper S3 (ESP32-S3, 960×540 e-ink). Takes a declarative screen description and automatically computes positions, renders widgets, tracks changes, and issues the minimum possible set of e-ink partial refreshes. The four-stage pipeline (Layout → Update → Collect+Merge → Render+Refresh) solves both the layout composition problem and the e-ink partial-refresh optimization problem.

**Repos**:
| Path | GitHub | Notes |
|------|--------|-------|
| `/home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5` | `go-go-golems/esp32-s3-m5` | Firmware `0078-papers3-gnosis-layout` |

**Tribal candidates**:
- **Four-stage e-ink render pipeline**: Layout → Update → Collect+Merge → Render+Refresh. The split between "collect dirty rects" and "merge them into larger regions" is the key insight that makes e-ink partial refresh composable. We've used it in Gnosis and Loupedeck; it should apply to reMarkable too.
- **Compile-time DSL → struct initializer lists**: The Gnosis DSL is a JSON-based screen description, but the C++ port compiles DSL trees directly into struct initializer lists, skipping JSON parsing entirely. Zero runtime cost for layout description.
- **Custom 5×7 bitmap font at 4× scale**: Each character stored as seven bytes, each byte encoding a 5-bit row, rendered as `fillRect(gx + col*4, y + row*4, 4, 4, color)`. Not the fastest approach (scanline buffer would be faster) but the bottleneck is always e-ink refresh, not CPU rendering. The tradeoff is documented.
- **Waveform mode selection strategy**: Use `epd_text` for partial dirty-rect refreshes during normal operation; `epd_quality` for periodic full-screen refreshes that clean up accumulated ghosting. This "cheap partial + periodic full clean" pattern is our standard approach for e-ink.

**On-Ramp concepts this project depends on**:
- Retained-mode vs immediate-mode rendering
- E-ink display waveforms and ghosting
- Dirty-rectangle partial refresh
- Declarative layout trees (CSS box model analogs)

**Fundamental concepts this project rests on**:
- Computational geometry (rectangle merging)
- Rendering pipeline fundamentals
- Display physics (electrophoresis, bistable media)

---

### 3. Capsule Lab — Sandboxed JS Capsule Runtime in the Browser

**Date**: 2026-04-02

**Summary**: A browser-based playground for running small JavaScript programs inside a sandboxed goja runtime compiled to WebAssembly. The capsule has no direct access to DOM, network, or filesystem — every side effect goes through a host-mediated API. The three-panel IDE (editor, canvas, bridge log) makes the sandbox boundary visible and debuggable.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-02--capsule-lab` | Go/WASM kernel, browser host shell, CodeMirror editor |

**Tribal candidates**:
- **goja-in-WASM as sandbox boundary**: The pattern of compiling a Go JS interpreter to WASM and using it as the sandbox instead of browser-native approaches (iframes, Web Workers, ShadowRealm). The capsule's JS code runs inside goja, which has no DOM/network/filesystem access. This is our approach to JS sandboxing; nobody else documents it this way.
- **Host-mediated op-stream API**: Every interaction between host and kernel follows a request-response pattern. The host calls `createSandbox`, `loadSource`, `dispatch` and receives JSON with `ok: boolean` and an array of `ops` — operations the capsule wants the host to perform. This op-stream pattern is the bridge between WASM kernel and browser host.
- **goja NaN sanitization in JSON export**: goja faithfully exports JS `NaN` as Go `math.NaN()`, and Go's `json.Marshal` rejects NaN per the JSON spec. The kernel had to add recursive NaN sanitization in `flushOps()`. This is a recurring gotcha in any goja-to-JSON pipeline.
- **Permission-locked API surface**: The sandbox installs a controlled API object before evaluating capsule source. Permission set is declared in manifest and locked at define-time. `requirePermission()` checks before every side-effecting call.

**On-Ramp concepts this project depends on**:
- WebAssembly from Go
- goja ECMAScript interpreter
- Capability-based security
- JavaScript sandboxing models

**Fundamental concepts this project rests on**:
- Process isolation and capability security
- Interpreter design (AST walk vs bytecode)

---

### 4. Loupedeck Live — Serial Go Driver and Hardware Integration

**Date**: 2026-04-11

**Summary**: A Go driver for the Loupedeck Live control surface communicating over USB serial via firmware 2.x's "mutant WebSocket" protocol. The project moved from a minimal Hello World through a feature tester that discovered protocol rate-limiting issues, to an advanced architecture with SVG rendering, animation pipelines, render scheduling, and region coalescing.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-11--loupedeck-test` | Initial driver and hello world |
| `/home/manuel/code/wesen/corporate-headquarters/loupedeck` | Advanced driver with Goja runtime, SVG, scheduler |

**Tribal candidates**:
- **"Mutant WebSocket over serial" protocol handling**: The Loupedeck's firmware 2.x sends WebSocket frames over USB serial. Standard WebSocket libraries (gorilla/websocket) panic on the device's malformed control frames. We handle this with rate-limiting, draw batching, and graceful error recovery. This is a specific pattern for talking to this device; no public docs cover it.
- **Draw batching at 30fps**: The device's WebSocket state machine gets confused under load. We queue draws and send them at 30fps instead of immediately. 100ms delays between button updates; 500ms after setup. These numbers were discovered empirically.
- **Render scheduler with region coalescing**: Multiple dirty rectangles are merged into fewer, larger regions to minimize serial transfer bandwidth. This is the same dirty-rect pattern from Gnosis, but applied to a 60×360 LCD over serial instead of a 960×540 e-ink display.
- **SVG→bitmap→serial pipeline**: Parse SVG, rasterize paths, cache bitmaps, tile large images. The rendering approach for a 60×360 LCD with 16-bit color at serial-line speeds.

**On-Ramp concepts this project depends on**:
- USB serial protocols
- Rendering pipelines
- Backpressure and flow control

**Fundamental concepts this project rests on**:
- Encoding and framing (WebSocket-like framing over serial)
- Rendering pipeline fundamentals (dirty-rect, compositing)
- Flow control theory (backpressure, rate limiting)

---

### 5. BYOK Host — Keycloak + SQLite Broker for Browser-Facing Inference

**Date**: 2026-04-17

**Summary**: A local broker application for "Bring Your Own Key" inference. Keycloak authenticates the user; the broker decides what the user's stored provider connection may be used for. The broker issues short-lived OAuth tokens, manages consent and grants, stores everything in SQLite, and enforces the separation between authentication (Keycloak) and authorization (broker).

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-17--byok-host` | Main broker implementation |

**Tribal candidates**:
- **Broker-not-proxy architecture**: The broker is not a transparent proxy — it makes authorization decisions, stores grants, and issues its own tokens. This distinction is the core design decision. "Keycloak authenticates the user; the broker decides what the user's stored provider connection may be used for." We had to learn this separation the hard way in earlier projects that mixed auth and authz.
- **Signed broker session cookies**: Using HMAC-signed cookies to avoid server-side session state. The broker issues a signed cookie after Keycloak login; subsequent requests validate the cookie without hitting Keycloak again. The tradeoff: statelessness vs revocation difficulty.
- **SQLite persistence surviving broker restart**: WAL mode, schema migrations in Go, connection pooling. The broker stores users, connections, grants, auth codes, access tokens, and audit events in SQLite, and all state survives a process restart.
- **Authorization Code + PKCE from a Go CLI**: The pattern for doing the full OAuth browser-redirect flow from a command-line tool. Open browser → user logs in at Keycloak → redirect to localhost callback → CLI exchanges code for tokens. This is a non-obvious wiring that we've implemented repeatedly.

**On-Ramp concepts this project depends on**:
- OAuth 2.0 and OIDC flows
- Keycloak as identity provider
- SQLite as application database

**Fundamental concepts this project rests on**:
- Access control models (authentication vs authorization vs delegation)
- Database transaction isolation

---

### 6. SToMS3R — AtomS3R Lite Thermal Printer Firmware

**Date**: 2026-04-28

**Summary**: ESP-IDF firmware for the M5Stack AtomS3R Lite driving a K118 58mm thermal printer. Three identities: (1) console-driven printer controller with 16 `esp_console` commands, (2) web UI with browser-side Floyd-Steinberg dithering, (3) diagnostic toolkit. Key design decision: image processing happens in the browser, not on the ESP32.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/stoms3r` | Firmware source |
| `/home/manuel/workspaces/2026-05-08/extract-almanach/almanach` | Almanach render service (Go server) |

**Tribal candidates**:
- **Buffer-full-body-before-UART pattern**: The firmware reads the entire HTTP POST body into memory before sending the `GS v 0` raster command to the printer. This prevents TCP read gaps from creating visible stripe artifacts in the printed output. If the UART stream is interrupted mid-raster, the printer interprets the gap as a command boundary, corrupting the bitmap. Buffering the full body first eliminates this.
- **MSB-first bit packing for ESC/POS**: `data[y*bytesPerRow+x/8] |= byte(0x80) >> (x % 8)`. The K118 expects MSB-first packing (leftmost pixel = bit 7 of the first byte). This convention is easy to get wrong — LSB-first would produce a mirror image.
- **Browser-side image processing for embedded devices**: The pattern of doing heavy computation (decoding, resizing, dithering) in the browser and sending only the final 1-bit bitmap to the microcontroller. The ESP32 does zero image processing. This is a deliberate architectural decision, not an accident.
- **AtomS3R Lite over ATOM Lite for printer projects**: The ESP32-S3's built-in USB Serial/JTAG peripheral frees every GPIO pin; 8 MB PSRAM handles full-page bitmaps; ESP-IDF gives `esp_console` as a first-class component. The ATOM Lite has pin conflicts, no PSRAM, and Arduino hides the UART.
- **Pin-swapping for K118 cable**: The K118 cable is straight-through (pin-for-pin), but the ESP32 needs TX→RX crossover. We swap at runtime with `printer_drv_swap_pins(true)` instead of making a custom crossover cable.

**On-Ramp concepts this project depends on**:
- ESC/POS thermal printer commands
- 1-bit image dithering and rasterization
- E-ink/thermal display waveforms (if generalizing beyond thermal)

**Fundamental concepts this project rests on**:
- Signal quantization and sampling theory
- Encoding and framing (bit packing, raster command structure)
- Human visual perception (contrast sensitivity, dot gain)

---

### 7. Wish Git — OAuth-Scoped Git over SSH for Coding Agents

**Date**: 2026-05-02

**Summary**: A Git forge where local coding agents receive short-lived, narrowly scoped SSH certificates instead of long-lived human credentials. The human authenticates through Keycloak, the server creates an `agent_run` row in Postgres, the CLI generates a fresh SSH keypair, the server signs it as an OpenSSH user certificate, and the agent uses ordinary Git-over-SSH. Enforcement at SSH command execution and Git `pre-receive` hook time.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-05-01--wish-git` | Forge server, CLI, SSH server, certificate CA |

**Tribal candidates**:
- **Three-credential separation**: User credential (Keycloak session) → broker credential (OAuth token) → agent credential (SSH certificate). Each has different scope, lifetime, and storage. The agent never sees the user's OAuth token; the SSH server never sees the Keycloak session. This separation is the core security model.
- **SSH certificate as scoped delegation**: Using OpenSSH user certificates (not `authorized_keys`) to represent a scoped, short-lived agent run. The `principals` field carries the run ID; `force-command` restricts what the SSH session can execute; certificate expiry limits the damage window. This is a non-obvious use of SSH certificates that most tutorials don't cover.
- **`pre-receive` hook as policy enforcement layer**: The `forge-hook` binary is installed into bare repositories as the `pre-receive` hook. It reads the agent run's allowed refs and paths from the database and rejects any push that violates them. The hook is the final enforcement point — even if the SSH server somehow allows an unauthorized operation, the hook catches it.
- **`git-upload-pack`/`git-receive-pack` interception at SSH layer**: The SSH server's `exec` callback inspects the requested command and repository, checks it against the agent run's scope, and either allows or denies it. This is where the SSH certificate's `force-command` and `principals` are resolved into a real policy decision.

**On-Ramp concepts this project depends on**:
- OpenSSH user certificates
- OAuth 2.0 and OIDC flows
- Git hooks for policy enforcement

**Fundamental concepts this project rests on**:
- Access control models (delegation, scoped credentials, audit)
- Public key infrastructure (CA signing, certificate chains)

---

## Batch 2: KB Playbook Trial (6 projects)

These 6 projects were analyzed as part of the KB-PLAYBOOK-TRIAL intern assignment. See [[KB-PLAYBOOK-TRIAL - Intern Reports for 6 Projects]] for the full analysis.

### 9. ZK Tool — Obsidian Vault Automation + Go JS Runner

**Date**: 2026-03-15

**Summary**: A local toolchain for working with an Obsidian-based Zettelkasten vault. Combines a Go CLI with a goja JavaScript runtime that can talk to the local Obsidian CLI through a native `require("obsidian")` API. Two identities: ZK filing/routing tool and Obsidian automation platform.

**Tribal candidates**:
- goja native module registration (2/3) — the `require("obsidian")` pattern; seen in goja-embedding, ZK Tool, Loupedeck
- ZK note routing logic (1/3) — our specific vault filing workflow

**On-Ramp candidates**: Obsidian CLI from Go (1/5), Luhmann-style branching codes (1/5)

### 10. Sqleton SQL Command Cleanup — Glazed CLI Ecosystem

**Date**: 2026-04-02

**Summary**: Full cleanup of how sqleton defines, discovers, parses, and executes SQL-backed commands. SQL files become first-class command definitions with metadata preambles. App config and command config are separated after removing Viper from the startup path.

**Tribal candidates**:
- SQL as first-class command source (2/3) — `.sql` files define Glazed commands; seen in Sqleton, Minitrace
- App config vs command config separation (2/3) — keeping them out of the same parser; seen in Sqleton, BYOK Host

### 11. Firecracker VM — Host-Mediated Secrets and Isolation Design

**Date**: 2026-03-31

**Summary**: Local reference runtime for "one microVM per job" coding-agent execution. Host prepares sealed inputs (kernel, rootfs, workspace ext4 image, vsock), guest consumes them, output comes back as a retained filesystem artifact. Key design: host-mediated Vault secret delivery instead of guest-side Vault.

**Tribal candidates**:
- MicroVM as execution boundary (2/3) — seen in Firecracker VM, pi-sandbox
- Host-mediated secret delivery (2/3) — seen in Firecracker VM, BYOK Host
- Ext4 workspace as boundary artifact (1/3)

**Fundamental candidates**: Host-mediated sandbox principles (1/2)

### 12. uLisp PicoCalc — Lisp Interpreter on RP2040

**Date**: 2026-05-05

**Summary**: A kit-built handheld running uLisp 4.8f on a PicoCalc (RP2040 + 320×320 display + keyboard). Cross-compilation via arduino-cli, native C99 REPL for host-side testing, CLion configuration generator, annotated source index.

**Tribal candidates**:
- C99 native port for host testing (2/3) — seen in uLisp PicoCalc, Smalltalk-80 VM
- TFT_eSPI patching for RP2040 (2/3) — the "blank screen with no error" gotcha
- I2C address routing quirk (1/3) — addresses ≥ 128 → Wire1
- Dangerous register gotcha (1/3) — reading I2C register 0x08 crashes MCU

**On-Ramp candidates**: Arduino-cli cross-compilation (2/5)

### 13. Screencast Studio — GStreamer Migration and Media Runtime

**Date**: 2026-04-13

**Summary**: Local recording system migrating from FFmpeg subprocesses to native GStreamer pipelines managed from Go. Opens a new KB domain (media) with zero existing coverage. Key architecture: DSL → normalized config → compiled plan → runtime seam → concrete engine.

**Tribal candidates**:
- GStreamer pipeline construction from Go (1/3)
- Runtime seam for engine migration (1/3)
- GLib main loop coexistence with Go (1/3)
- DSL → normalized config → compiled plan (2/3)

**On-Ramp candidates**: GStreamer for Go programmers (2/5), Preview vs recording lifecycle (1/5)

### 14. Agent Enroll — Kanban Agent Credential MVP

**Date**: 2026-05-03

**Summary**: Security-sensitive Kanban agent credential system. Humans log in through Keycloak; the Go application owns agent enrollment (Ed25519 keys), canonical request signing, one-time enrollment tokens, scoped opaque run tokens, and task-scoped authorization.

**Tribal entries**: [[Tribal/application-native-authorization]] (3/3 → CREATED)

**Tribal candidates**:
- Three-layer credential separation (2/3) — seen in Wish Git, Agent Enroll
- Canonical request signing (1/3)
- Opaque scoped bearer tokens (1/3)
- Enrollment tokens (one-time, hash-only) (1/3)

---

### 8. AUTODISCO — Automerge Discord App Architecture

**Date**: 2026-05-09

**Summary**: A local-first Discord-style chat prototype built around Automerge CRDT documents. The browser opens an Automerge document, applies changes locally, persists in IndexedDB, and syncs through an Automerge Repo WebSocket relay. The server bootstraps documents and relays sync messages but is not the exclusive writer of chat state.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-05-09--automerge-discord` | Monorepo: chat-core, chat-server, chat-web |

**Tribal candidates**:
- **Server as relay, not authority**: The Express server bootstraps documents and hosts a WebSocket sync endpoint, but it does not own the canonical state. The server is an Automerge Repo peer with filesystem persistence, not a database-backed API. This is a deliberate architectural choice — the server could go down and browsers would continue working offline.
- **Domain mutation helpers inside CRDT changes**: `sendMessage` in `chat-core/src/mutations.ts` checks that the channel exists, refuses archived channels, initializes the message array, and writes the record with a stable shape. Automerge provides merge semantics; the domain package provides application semantics. This separation prevents raw CRDT operations from violating business rules.
- **IndexedDB-backed Repo storage in the browser**: The browser Automerge Repo uses IndexedDB for persistence, so the app survives tab reloads and browser restarts. The `chat-web/src/features/automerge/repo.ts` sets up the Repo with `IndexedDBStorageAdapter`, `WebSocketClientAdapter`, and a random peer ID.
- **Monorepo package decomposition for local-first apps**: `@autodisco/chat-core` (shared document schema and mutations), `@autodisco/chat-server` (Node relay), `@autodisco/chat-web` (React client). The core package is shared between server and browser — this is a pattern we'll reuse for any local-first app.

**On-Ramp concepts this project depends on**:
- CRDTs and local-first architecture
- IndexedDB for browser persistence
- WebSocket sync protocols

**Fundamental concepts this project rests on**:
- Distributed consistency (CAP, eventual consistency, commutative operations)
- Encoding and framing (WebSocket sync message format)

---

## KB Candidate Tracking

### Tribal candidates (trigger at 3 projects)

| Concept | Seen in | Count |
|---------|---------|-------|
| **Application-native authorization** | BYOK Host, Wish Git, Agent Enroll | 3/3 → **CREATED** as [[Tribal/application-native-authorization]] |
| **goja-in-WASM as sandbox boundary** | Capsule Lab, (go-go-goja ecosystem) | 1/3 — need 2 more goja+WASM projects |
| **Host-mediated op-stream API** | Capsule Lab, (future sandboxed runtimes) | 1/3 |
| **goja NaN sanitization in JSON export** | Capsule Lab, (any goja-to-JSON pipeline) | 1/3 |
| **Buffer-full-body-before-UART** | SToMS3R, Almanach | 2/3 — needs 1 more UART streaming project |
| **MSB-first bit packing for ESC/POS** | SToMS3R, Almanach | 2/3 |
| **Browser-side image processing for embedded** | SToMS3R, Capsule Lab (partial) | 2/3 |
| **Four-stage e-ink render pipeline** | Gnosis, (reMarkable projects) | 1/3 |
| **Draw batching at hardware-limited fps** | Loupedeck, (Gnosis uses different approach) | 1/3 |
| **"Mutant WebSocket over serial" handling** | Loupedeck | 1/3 |
| **Broker-not-proxy architecture** | BYOK Host, (future auth projects) | 1/3 |
| **Authorization Code + PKCE from Go CLI** | BYOK Host, Wish Git | 2/3 — needs 1 more |
| **SSH certificate as scoped delegation** | Wish Git | 1/3 |
| **pre-receive hook as policy enforcement** | Wish Git | 1/3 |
| **Server-as-relay-not-authority** | AUTODISCO | 1/3 |
| **Domain mutation helpers inside CRDT changes** | AUTODISCO | 1/3 |
| **Spec-first implementation discipline** | Smalltalk-80 VM | 1/3 |
| **Pin-swapping for K118 cable at runtime** | SToMS3R | 1/3 |
| **AtomS3R Lite over ATOM Lite for printer** | SToMS3R | 1/3 |
| **goja native module registration** | goja-embedding (generic), ZK Tool (Obsidian), Loupedeck (hardware) | 2/3 |
| **SQL as first-class command source** | Sqleton, Minitrace Query Commands | 2/3 |
| **App config vs command config separation** | Sqleton, BYOK Host | 2/3 |
| **MicroVM as execution boundary** | Firecracker VM, pi-sandbox | 2/3 |
| **Host-mediated secret delivery** | Firecracker VM, BYOK Host (credential mediation) | 2/3 |
| **Three-layer credential separation** | Wish Git, Agent Enroll | 2/3 |
| **C99 native port for host testing** | uLisp PicoCalc, Smalltalk-80 VM (partial) | 2/3 |
| **TFT_eSPI patching for RP2040** | uLisp PicoCalc, (other display projects) | 2/3 |
| **DSL → normalized config → compiled plan** | Screencast Studio, Almanach Studio | 2/3 |
| **GStreamer pipeline construction from Go** | Screencast Studio | 1/3 |
| **Runtime seam for engine migration** | Screencast Studio | 1/3 |
| **GLib main loop coexistence with Go** | Screencast Studio | 1/3 |
| **Canonical request signing** | Agent Enroll | 1/3 |
| **Opaque scoped bearer tokens** | Agent Enroll | 1/3 |
| **Enrollment tokens (one-time, hash-only)** | Agent Enroll | 1/3 |
| **ZK note routing logic** | ZK Tool | 1/3 |
| **Ext4 workspace as boundary artifact** | Firecracker VM | 1/3 |

### On-Ramp candidates (trigger at 5 projects)

| Concept | Seen in | Count |
|---------|---------|-------|
| **ESC/POS thermal printer commands** | SToMS3R, Almanach, ATOM-PRINTER | 3/5 |
| **E-ink display driving** | Gnosis, Paper Pro, reMarkable projects | 3/5 |
| **Git hooks for policy enforcement** | Wish Git, (future forge projects) | 2/5 |
| **Retained-mode rendering / dirty rects** | Gnosis, Loupedeck | 2/5 |
| **Go→WASM compilation** | Capsule Lab, SQLide, JSON Flattener, VT100, Codebase Browser | 5/5 → **READY** |
| **goja ECMAScript interpreter** | Capsule Lab, Loupedeck, go-go-goja ecosystem | 2/5 (from 8-project sample; 52/5 in full library) |
| **CRDTs and local-first architecture** | AUTODISCO | 1/5 (from 8-project sample) |
| **GStreamer for Go programmers** | Screencast Studio, (future media projects) | 2/5 |
| **Arduino-cli cross-compilation** | uLisp PicoCalc, (other Arduino projects) | 2/5 |
| **Obsidian CLI from Go** | ZK Tool | 1/5 |

### Fundamental candidates (trigger when supporting 2+ KB entries)

| Concept | Supports | Status |
|---------|----------|--------|
| **Signal quantization and sampling** | Dithering On-Ramp, ESC/POS On-Ramp, E-ink On-Ramp | 3 → **READY** |
| **Access control models** | OAuth On-Ramp, SSH Certs On-Ramp, Keycloak Tribal | 3 → **READY** |
| **Encoding and framing** | ESC/POS On-Ramp, Serial Protocols Tribal, UART Tribal | 3 → **READY** |
| **Rendering pipeline fundamentals** | E-ink On-Ramp, Dirty-rect Tribal | 2 → **READY** |
| **Distributed consistency** | CRDT On-Ramp | 1 — needs 1 more KB entry |
| **Host-mediated sandbox principles** | goja-embedding Tribal, Firecracker microVM Tribal (candidate) | 1/2 — needs either goja-embedding or microVM tribal to exist |

---

## KB Entries Ready to Create

Based on the candidate counts across the full 304-project library (not just the 8-project sample), these entries have passed their threshold:

### Tribal (3+ projects, our pattern)

1. **goja: Embedding a JavaScript Interpreter in Go** — 52 projects
2. **ESP-IDF Firmware Patterns** — 28 projects
3. **Keycloak OAuth in Go Services** — 29 projects
4. **Go → WASM Compilation** — 33 projects
5. **Serial Protocols: Talking to Hardware from Go** — 17 projects
6. **SQLite as Application Database in Go** — 84 projects
7. **Application-Native Authorization** — 3 projects (BYOK Host, Wish Git, Agent Enroll) ← **NEW**

### On-Ramp (5+ projects, lookupable but our angle missing)

1. **CRDTs and Local-First Architecture** — justified by concept density even if project count is low
2. **OAuth 2.0 and OIDC — The Flows That Matter** — 29 projects
3. **OpenSSH Certificates** — 11+ projects
4. **1-Bit Image Dithering and Rasterization** — 9 projects
5. **ESC/POS Thermal Printer Commands** — 13 projects
6. **E-Ink Display Driving** — 14 projects
7. **Git Hooks for Policy Enforcement** — 41 projects
8. **WebAssembly from Go** — 33 projects

### Fundamentals (underpins 2+ KB entries)

1. **Signal Quantization and Sampling Theory** — underlies 3 On-Ramp entries
2. **Access Control Models: Authentication, Authorization, Delegation** — underlies 3 entries
3. **Encoding and Framing: Turning Bytes into Messages** — underlies 3 entries
4. **Rendering Pipeline Fundamentals: Retained Mode, Dirty Rects, Compositing** — underlies 2 entries

---

## Cross-Reference: Which Projects Feed Which KB Entries

| KB Entry | Projects that feed it (from Batch 1) |
|----------|--------------------------------------|
| Tribal/goja-embedding | Capsule Lab, Loupedeck |
| Tribal/ESP-IDF-firmware | Gnosis, SToMS3R |
| Tribal/Keycloak-OAuth | BYOK Host, Wish Git |
| Tribal/Go-to-WASM | Capsule Lab |
| Tribal/serial-protocols | Loupedeck, SToMS3R |
| Tribal/SQLite-as-app-DB | BYOK Host |
| On-Ramp/CRDT-and-local-first | AUTODISCO |
| On-Ramp/OAuth-2-OIDC | BYOK Host, Wish Git |
| On-Ramp/OpenSSH-certificates | Wish Git |
| On-Ramp/dithering-and-rasterization | SToMS3R |
| On-Ramp/ESC-POS-thermal-printer | SToMS3R |
| On-Ramp/e-ink-display-driving | Gnosis |
| On-Ramp/git-hooks-for-policy | Wish Git |
| On-Ramp/WASM-from-Go | Capsule Lab |
| Fundamentals/signal-quantization | SToMS3R |
| Fundamentals/access-control-models | BYOK Host, Wish Git |
| Fundamentals/encoding-and-framing | Loupedeck, SToMS3R |
| Fundamentals/rendering-pipeline-fundamentals | Gnosis, Loupedeck |
| Tribal/application-native-authorization | BYOK Host, Wish Git, Agent Enroll |
