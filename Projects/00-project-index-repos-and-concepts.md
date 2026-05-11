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

## Batch 3: goja/JS Runtime Ecosystem (6 projects)

These 6 projects were analyzed as part of the goja ecosystem batch. See [[KB-BATCH3-goja-ecosystem]] for the full analysis.

### 15. go-go-goja REPL API — Profiles, IIFE Rewriting, and Session Semantics

**Date**: 2026-04-03

**Summary**: The REPL subsystem of go-go-goja, implementing profile-based execution (raw/interactive/persistent), IIFE cell rewrites for lexical capture, replay-based session restore, and SQLite-backed persistence. The key insight: a JavaScript REPL session is not just a live VM — it's a product concept with explicit binding capture, execution policy, and optional durable history.

**Repos**:
| Path | Notes |
|------|-------|
| `go-go-goja` (workspace) | pkg/replapi, pkg/replsession, pkg/repldb |

**Tribal entries**: [[Tribal/goja-embedding-in-go]] (variation: profile-based execution), [[Tribal/goja-execution-model]] (sessions + thread discipline)

**Tribal candidates**:
- IIFE cell rewrite (2/3) — async IIFE wrapping for lexical capture + last-expression semantics
- Promise handling in evaluation (2/3) — detect promise-like results and await before building cell response
- Replay-based restore (1/3) — re-execute persisted source into a fresh runtime
- Static analysis for cell planning (1/3) — jsparse + Tree-sitter for declarations, unresolved refs, final expression
- Console capture / JSDoc sentinels (1/3) — structured console events and no-op doc helpers

**On-Ramp candidates**: None new

### 16. go-go-goja Node-like Primitives — Technical Deep Dive

**Date**: 2026-04-25

**Summary**: Node.js-like primitive modules in go-go-goja: Buffer, URL, fs, path, os, crypto, time, timer. The key design: data-only primitives are default-enabled; host-access modules (fs, os, exec, database) require explicit opt-in. Async native modules follow the goroutine → Promise pattern.

**Repos**:
| Path | Notes |
|------|-------|
| `go-go-goja` (workspace) | engine/factory.go, modules/fs/, modules/path/, modules/os/, modules/crypto/ |

**Tribal entries**: [[Tribal/goja-embedding-in-go]] (variation: runtime factory composition with engine.NewBuilder())

**Tribal candidates**:
- Data-only vs host-access module split (2/3) — safe defaults vs opt-in host modules; seen in Node-like Primitives, Capsule Lab
- Runtime-scoped module registrars (2/3) — per-runtime module registration and cleanup; seen in Plugins, Node-like Primitives
- Granular module selection (1/3) — DefaultRegistryModule("fs") vs DefaultRegistryModules()
- process global opt-in (1/3) — require-able but not installed globally
- Module specs vs runtime initializers (1/3) — two composition APIs: require registry vs live VM mutation

**On-Ramp candidates**: None new

### 17. go-go-goja Plugins — Since origin main

**Date**: 2026-03-18

**Summary**: Full external plugin stack for go-go-goja using HashiCorp go-plugin: plugin discovery, manifest validation, subprocess lifecycle, authoring SDK, docs hub, and REPL integration. The key rule: the host runtime is the center of truth; plugins extend it through controlled RPC bridges, never by owning the VM.

**Repos**:
| Path | Notes |
|------|-------|
| `go-go-goja` (workspace) | pkg/hashiplugin/, pkg/docaccess/, plugins/examples/ |

**Tribal candidates**:
- HashiCorp go-plugin for JS modules (1/3) — external subprocess providing JS modules via RPC
- Plugin authoring SDK (1/3) — MustModule/Function/Object/Method/Call/Serve DSL
- Plugin discovery + manifest validation (1/3)
- Runtime-scoped docs hub (1/3) — docaccess.Hub with providers (Glazed, jsdoc, plugin manifest)
- Docs-aware REPL autocomplete (1/3) — plugin docs feeding completion candidates
- Result normalization before structpb encoding (1/3) — rewriting Go values into structpb-friendly shapes

**On-Ramp candidates**: None new

### 18. Goja vs Sobek Deep Analysis

**Date**: 2026-04-12

**Summary**: Comprehensive comparison of goja and its Grafana-maintained fork Sobek. Three findings: (1) Sobek tracks Goja with near-zero lag, (2) ESM is the only major difference (+4.6% code size, +5 files), (3) Sobek exists to power k6 with modern JS module capabilities.

**Repos**:
| Path | Notes |
|------|-------|
| `2026-04-12--goja-vs-sobek` | Clones of both repos, analysis scripts |

**Tribal candidates**:
- Goja vs Sobek decision framework (1/3) — when to choose Sobek (ESM, k6, Renovate)

**On-Ramp candidates**: ESM support in Go JS engines (1/5) 🌐 Domain seed

### 19. JS Discord Bot Framework

**Date**: 2026-04-20

**Summary**: Go Discord bot host running JavaScript bot scripts via goja with a clean defineBot DSL. Commands, components, modals, events, and runtime config. Key decision: single-bot per process (not multi-bot composition).

**Repos**:
| Path | Notes |
|------|-------|
| `2026-04-20--js-discord-bot` | internal/jsdiscord/, internal/bot/, internal/botcli/ |

**Tribal entries**: Contributes to [[Tribal/goja-execution-model]] (owner thread discipline variation)

**Tribal candidates**:
- goja-based Discord bot host (1/3)
- defineBot DSL (1/3) — command/component/modal/event registration
- Single-bot per process (1/3) — architectural decision against multi-bot composition
- Two-stage Glazed parsing for runtime config (2/3) — pre-parse static flags, then dynamically build schema
- UI DSL for Discord (1/3) — message/embed/button/select/form/card/confirm builders

**On-Ramp candidates**: None new

### 20. go-go-goja jsverbs — JavaScript to Glazed Commands

**Date**: 2026-03-16

**Summary**: JavaScript-defined Glazed commands — .js files scanned as command definitions, exposed as Glazed verbs. Static metadata extraction via AST, source overlay runtime preserving relative require(), shared binding plan between schema and execution.

**Repos**:
| Path | Notes |
|------|-------|
| `go-go-goja` (workspace) | pkg/jsverbs/ |

**Tribal candidates**:
- JS-defined Glazed commands (2/3) — JS files as first-class Glazed verb definitions; seen in jsverbs, (Glazed help?)
- Static metadata extraction via AST (1/3)
- Source overlay runtime (1/3) — in-memory loader preserving relative require()
- Shared binding plan (1/3) — one contract between schema generation and runtime invocation
- Multi-source scanning (1/3) — ScanDir/ScanFS/ScanSource/ScanSources

**On-Ramp candidates**: None new

---

## Batch 4: Embedded/Hardware Ecosystem (6 projects)

These 6 projects were analyzed as part of the embedded/hardware batch. See [[KB-BATCH4-embedded-hardware]] for the full analysis.

### 21. Smalltalk-80 VM — Blue Book Interpreter in Go

**Date**: 2026-03-18

**Summary**: A Blue-Book-first Smalltalk-80 interpreter in Go. The VM matches the execution model from the canonical specification closely enough to boot the real image, run the scheduler, and execute real image methods. Key insight: when behavior diverges, assume specification mismatch before assuming the image is strange.

**Repos**:
| Path | Notes |
|------|-------|
| `2026-03-17--smalltalk` | pkg/interpreter/, pkg/objectmemory/, pkg/image/ |

**Tribal entries**: [[Tribal/goja-embedding-in-go]] (contrast: spec-first discipline vs pragmatic embedding)

**Tribal candidates**:
- Spec-first VM implementation (2/3) — building from formal spec, not referencing another implementation as oracle
- Regression-trace-driven debugging (1/3) — comparing VM execution against known-good image traces
- SmallInteger boundary bugs (1/3) — positive integers exceeding SmallInteger range cause silent corruption
- Method cache hash translation (1/3) — wrong hash causes semantic corruption, not just performance loss
- Context lifetime bugs as disguised send failures (1/3) — bugs in context creation appear later as unrelated crashes
- Primitive argument widening (1/3) — primitives should accept non-negative integers, not just SmallIntegers

**On-Ramp candidates**: None new

### 22. PaperS3 WAMR Debugging — Embedded Wasm Root Cause

**Date**: 2026-03-23

**Summary**: A long debugging campaign proving that WAMR's interpreter loader mutates flash-mapped embedded Wasm buffers in place, causing later PSRAM crashes. Key insight: the crash site is not the cause site. Shrink the problem until the smallest toxic step is obvious.

**Repos**:
| Path | Notes |
|------|-------|
| `esp32-s3-m5` (workspace) | 0079-.../0082-... firmware dirs, ESP-39..46 tickets |

**Tribal entries**: Contributes to **microVM as execution boundary** (3/3 → READY)

**Tribal candidates**:
- Reduction-ladder debugging (2/3) — shrink until smallest toxic step is obvious
- Flash-mapped buffer mutability bug (1/3) — WAMR rewrites const strings on read-only flash
- Cross-board A/B debugging (1/3) — using AtomS3R as control to separate board vs runtime bugs

**On-Ramp candidates**: None new

### 23. Cardputer Web Serial Demo — Browser-to-Device over Web Serial

**Date**: 2026-04-02

**Summary**: M5Stack Cardputer ADV firmware speaks NDJSON over USB Serial/JTAG, browser connects via Web Serial with either Raw JS or Go→WASM protocol engine. Key insight: when the full browser app behaves strangely, prove the transport with the smallest possible page first.

**Repos**:
| Path | Notes |
|------|-------|
| `2026-04-02--cardputer-web-demo` | firmware/, wasm/, web/ |

**Tribal entries**: Contributes to **reduction-ladder debugging** (2/3 — smoke.html pattern)

**Tribal candidates**:
- NDJSON as wire protocol for embedded (2/3) — simple, observable, debuggable
- Web Serial for browser-to-embedded (1/3)
- Go→WASM protocol engine A/B with Raw JS (1/3)
- ESP-IDF driver_ng conflict with legacy I2C driver (1/3)
- Board-specific GPIO pin remapping (1/3)

**On-Ramp candidates**:
- Web Serial from the browser (1/5) — MDN has the API spec; the working pattern for browser-to-embedded communication is missing

### 24. SToMS3R — AtomS3R Lite Thermal Printer Firmware

**Date**: 2026-04-28

**Summary**: ESP-IDF firmware for AtomS3R Lite driving K118 58mm thermal printer. 16 esp_console commands + web UI with browser-side Floyd-Steinberg dithering. Key insight: ESP32 does zero image processing — browser does dithering, bit-packing, and POSTs raw 1-bit bitmap.

**Repos**:
| Path | Notes |
|------|-------|
| `esp32-s3-m5/stoms3r` (workspace) | 2,291 lines of C and HTML across 14 source files |

**Tribal entries**: [[Tribal/esp-idf-firmware-patterns]] (textbook instance: esp_console + web UI + UART + NVS)

**Tribal candidates**:
- Buffer-full-body-before-UART (2/3) — read entire HTTP body before single uart_write_bytes()
- Browser-side image processing for embedded (2/3) — heavy computation in browser, only final bitmap to ESP32
- GPIO pin swap at runtime (1/3) — uart_set_pin() for straight-through K118 cable
- ESP-IDF console REPL bring-up (2/5) — ESP-IDF docs describe esp_console API but not USB Serial/JTAG bring-up for ESP32-S3

**On-Ramp candidates**: Directly exercises [[On-Ramp/esc-pos-thermal-printer]], [[On-Ramp/dithering-and-rasterization]], [[Fundamentals/encoding-and-framing]]

### 25. Wi-Fi Audio Cues Lab — ESP32-S3 Audio Feedback for Wi-Fi Events

**Date**: 2026-04-05

**Summary**: ESP-IDF firmware for AtomS3R-CAM + Atomic Echo Base: USB Serial/JTAG REPL for Wi-Fi station management, data-driven audio cues through ES8311 codec. Key insight: bring-up must follow strict sequence — console → codec → tone → cues → events. Never debug multiple layers simultaneously.

**Repos**:
| Path | Notes |
|------|-------|
| `kball/esp-projects/wifi_audio_cues_lab` | main/ with wifi_manager, audio_cue_player, audio_backend_es8311 |

**Tribal entries**: [[Tribal/esp-idf-firmware-patterns]] (textbook instance: esp_console + NVS + WiFi STA)

**Tribal candidates**:
- Bring-up sequence discipline (2/3) — bring up one layer at a time, never debug multiple layers simultaneously
- Data-driven audio cue system (1/3) — static note-step tables, queue, event-driven playback
- ES8311 codec bring-up (1/3) — I2C, I/O expander unmute, I2S TX, clock tree
- Phase accumulator tone generation (1/3)
- Pending-only queue deduplication (1/3)

**On-Ramp candidates**:
- ESP-IDF console REPL bring-up (2/5) — ESP-IDF docs describe esp_console API but not USB Serial/JTAG bring-up for ESP32-S3
- ES8311 codec bring-up on AtomS3R (1/5) — no public doc for this board+codec combination

### 26. uLisp PicoCalc Firmware Split — CMake Modularization Report

**Date**: 2026-05-06

**Summary**: Monolithic Arduino .ino sketch → flat side-by-side .h/.cpp modules with CMake-orchestrated Arduino-Pico bridge. Generated forward-declarations deleted, replaced by focused subsystem headers. Key insight: keep the project flat until the seams stop moving.

**Repos**:
| Path | Notes |
|------|-------|
| `2026-05-05--ulisp-picocalc` | ulisp-picocalc/ with 20+ extracted modules |

**Tribal entries**: [[Tribal/goja-embedding-in-go]] (contrast: Arduino sketch preprocessing vs explicit C++ modules)

**Tribal candidates**:
- Monolithic sketch → flat C++ module split (1/3) — process knowledge, not architecture
- Arduino sketch preprocessing as migration hazard (1/3) — hidden prototypes, implicit Arduino.h
- Translation-unit-local macros are behavior (1/3) — #define Serial Serial1 lost across .cpp boundaries
- CMake bridge for Arduino-Pico builds (1/3)
- UF2 Loader deployment workflow (1/3)
- Shared error messages / C++ internal linkage (1/3)

**On-Ramp candidates**: None new

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

## Batch 5: Infrastructure/Secrets/Glazed (6 projects)

Strategic batch targeting 2/3 candidates near threshold. See [[KB-BATCH5-infra-secrets-glazed]] for the full analysis.

### 27. Vault on K3s — Auth and Secret Delivery Platform

**Date**: 2026-03-27

**Summary**: Vault on K3s with Raft + AWS KMS auto-unseal, Keycloak OIDC for humans, Kubernetes auth for machines, VSO for GitOps-friendly secret delivery. Key insight: secret intent in Git, secret values in Vault.

**Repos**:
| Path | Notes |
|------|-------|
| `2026-03-27--hetzner-k3s` | gitops/applications/vault.yaml, vault/policies/, vault/roles/ |

**Tribal entries**: Contributes to **host-mediated secret delivery** (3/3 → READY)

**Tribal candidates**:
- Separate human auth (OIDC) from machine auth (AppRole/K8s) (2/3)
- Keycloak group-gated Vault access (2/3)

**On-Ramp candidates**:
- Vault on K3s with VSO (2/5) — HashiCorp docs are cloud-centric; our single-node GitOps pattern is missing

### 28. Glazed Secret Redaction and Vault Bootstrap

**Date**: 2026-04-02

**Summary**: Two-phase Glazed framework work: central secret redaction, then Vault source middleware with bootstrap parsing. Key insight: only `TypeSecret` fields are eligible for Vault hydration.

**Repos**:
| Path | Notes |
|------|-------|
| `add-vault-middleware-to-glazed/glazed` | `pkg/cmds/fields/sensitive.go`, `pkg/cmds/sources/vault.go` |

**Tribal entries**: Contributes to [[Tribal/host-mediated-secret-delivery]] and [[Tribal/app-config-vs-command-config-separation]]

### 29. Minitrace Query Commands — Sqleton-Inspired SQL Verb System

**Date**: 2026-04-10

**Summary**: .sql files with YAML preambles → catalog → CLI + API + UI forms. Key insight: SQL is a command definition format.

**Repos**:
| Path | Notes |
|------|-------|
| `corporate-headquarters/go-minitrace` | pkg/minitracecmd/ |

**Tribal entries**: Contributes to **SQL as first-class command source** (3/3 → READY)

### 30. Hetzner K3s Platform — Single-Node GitOps Bring-Up

**Date**: 2026-03-27

**Summary**: Terraform creates, cloud-init bootstraps, Argo CD reconciles. Key insight: the platform is the product, not Kubernetes.

**Repos**:
| Path | Notes |
|------|-------|
| `2026-03-27--hetzner-k3s` | gitops/, terraform/ |

**Tribal candidates**: Terraform/cloud-init/Argo three-phase bring-up (1/3)

### 31. CoinVault on K3s — First Real GitOps App

**Date**: 2026-03-27

**Summary**: First real app migration onto K3s platform: Keycloak auth, VSO secrets, MySQL, PVC, HTTPS. Key insight: a platform is only real once a real workload lands on it.

**Repos**:
| Path | Notes |
|------|-------|
| `2026-03-27--hetzner-k3s` | gitops/applications/coinvault.yaml |

**Tribal entries**: [[Tribal/keycloak-oauth-in-go-services]] (Keycloak redirect for K3s hostname)

### 32. Terraform Infra — Vault Platform Bring-Up

**Date**: 2026-03-25

**Summary**: Coolify-hosted Vault, Keycloak OIDC for humans, AppRole for machines, KV layout, first app handoff. Four control planes in one session.

**Repos**:
| Path | Notes |
|------|-------|
| `terraform` (wesen) | vault/ module, keycloak/ module |

**Tribal entries**: Contributes to **host-mediated secret delivery** (3/3 → READY)

---

## Batch 6: Mixed Domain (6 projects)

Strategic batch targeting remaining 2/3 candidates. See [[KB-BATCH6-mixed-domain]] for the full analysis.

### 33. Capsule Lab — A Sandboxed JS Capsule Runtime in the Browser

**Date**: 2026-04-02

**Summary**: Browser-based JS playground running goja in WASM with host-mediated API. Capsules declare permissions; kernel enforces; host mediates all side effects. Key insight: compile a Go JS interpreter to WASM and use it as the sandbox boundary.

**Repos**:
| Path | Notes |
|------|-------|
| `2026-04-02--capsule-lab` | kernel/, host.js, inspector |

**Tribal entries**: [[Tribal/goja-embedding-in-go]] (textbook instance: op-stream, permission-locked API), [[Tribal/goja-execution-model]] (op-stream variation), [[Tribal/microvm-as-execution-boundary]] (WASM sandbox variation)

**Tribal candidates**: Contributes to **data-only vs host-access module split** (3/3 → READY)

### 34. Geppetto — Open Responses and Chat Boundary Cutover

**Date**: 2026-03-28

**Summary**: Open Responses support + Together/Qwen thinking-stream fix + chat boundary cutover from go-openai to Geppetto-owned structs. Key insight: own the normalization boundary for provider-specific deltas.

**Repos**:
| Path | Notes |
|------|-------|
| `use-open-responses/geppetto` | pkg/steps/ai/openai/ |

**Tribal candidates**: Contributes to **reduction-ladder debugging** (3/3 → READY)

### 35. Goja REPL Hardening

**Date**: 2026-04-08

**Summary**: Persistence correctness (soft-delete, UUID IDs, SQLite integrity), evaluation timeouts (deadline-based for async+sync), and structural cleanup of replsession package. Key insight: infrastructure code needs invariants that are simple enough to explain and strong enough to test.

**Repos**:
| Path | Notes |
|------|-------|
| `go-go-goja` (workspace) | pkg/replsession/ |

**Tribal entries**: Contributes to [[Tribal/goja-execution-model]] (IIFE rewrite hardening, timeout recovery)

**Tribal candidates**: Contributes to **IIFE cell rewrite** (now 3/3 → READY)

### 36. Remarquee — reMarkable Toolkit

**Date**: 2026-03-19

**Summary**: Unified Go CLI for reMarkable workflows: cloud auth with OAuth refresh, markdown-to-PDF upload, rmdoc rendering (V6 scene tree parser), OCR, and document DSL. Key insight: bounded retry on transient failures prevents auth escalation.

**Repos**:
| Path | Notes |
|------|-------|
| `remarquee` | pkg/rmcloud/, pkg/rmdoc/, pkg/mdpdf/ |

**Tribal candidates**: OAuth refresh with bounded retry (2/3)

### 37. E2E Encrypted Storage Prototype

**Date**: 2026-04-14

**Summary**: Browser-based E2E encryption with envelope pattern: per-document AES-GCM keys wrapped per-user with RSA-OAEP. Server stores only ciphertext. Key insight: Web Crypto API handles real encryption without external libraries.

**Repos**:
| Path | Notes |
|------|-------|
| `2026-04-14--browser-e2e-encryption` | main.go (550 lines), static/index.html (800+ lines) |

**Tribal candidates**: Envelope encryption for selective sharing (2/3)

**On-Ramp candidates**:
- Browser E2E encryption with Web Crypto (1/5) — Web Crypto API docs exist; envelope-encryption-for-sharing pattern is missing

### 38. AUTODISCO — Keyhive Access Control Architecture

**Date**: 2026-05-09

**Summary**: Access-control layer for Automerge CRDT chat using Keyhive WASM. Mock ACL for product flow, real Keyhive for experiments. Durable snapshots, invitation as membership events, and a `tryEncrypt` WASM binding fix. Key insight: CRDTs solve collaboration; they don't solve authorization.

**Repos**:
| Path | Notes |
|------|-------|
| `2026-05-09--automerge-discord` | `packages/chat-acl/`, `packages/chat-server/` |

**Tribal candidates**: CRDT-local authorization layer (2/3), Envelope encryption for selective sharing (2/3)

**On-Ramp candidates**:
- Automerge + Keyhive for local-first auth (1/5) 🌐 — cutting-edge; almost no public docs for CRDT access control
- Browser E2E encryption with Web Crypto (1/5) — envelope-encryption-for-sharing pattern is missing

## Batch 7: Glazed/JS Command Surfaces (6 projects)

Strategic batch targeting Glazed/JS command-definition and help-surface patterns. See [[KB-BATCH7-glazed-js]] for the full analysis.

### 39. JS Discord Bot — Building a Discord Bot with a JavaScript API

**Date**: 2026-04-20

**Summary**: Go Discord bot with a planned Goja behavior layer. Key insight: Go should keep Discord session lifecycle and secrets; JS should own behavior only after the host contract is stable.

### 40. JS Discord Bot — Adding jsverbs Support

**Date**: 2026-04-20

**Summary**: Planned jsverbs integration for operational CLI verbs. Key insight: runtime bot behavior and CLI jsverbs are separate JavaScript surfaces.

**Tribal entries**: Contributes to [[Tribal/js-defined-glazed-commands]]

### 41. go-minitrace PR #6 — JS Commands and Structured Query Catalog

**Date**: 2026-04-21

**Summary**: JS-backed analysis commands added alongside SQL commands in one catalog. Key insight: two command-definition languages can coexist when both compile into the same command model.

**Tribal entries**: Contributes to [[Tribal/js-defined-glazed-commands]] and reinforces [[Tribal/sql-as-first-class-command-source]]

### 42. go-minitrace Local Query Repository Config

**Date**: 2026-04-27

**Summary**: Project-local query repository discovery via `.go-minitrace.yml`. Key insight: command catalogs are part of project context, not just global tooling.

**Tribal entries**: Reinforces [[Tribal/app-config-vs-command-config-separation]]

### 43. Glazed Serve — Help Browser, Embedded Docs, and SPA

**Date**: 2026-04-08

**Summary**: Embedded React SPA and API inside the `glaze` binary. Key insight: one canonical section model, parser, and query system.

**On-Ramp candidates**:
- Go CLI with embedded SPA (2/5) — single-binary Go+web pattern needs orientation

### 44. Glazed Static Help Export — render-site and Static Snapshot Publishing

**Date**: 2026-04-09

**Summary**: Static-site export as a second delivery mode for the same help system. Key insight: static export is not a second help stack.

**On-Ramp candidates**:
- Go CLI with embedded SPA (2/5) — same domain as Glazed Serve

## Batch 8: Hosted Auth / Keycloak Identity (5 projects)

Focused batch on hosted identity, Keycloak, browser-vs-machine auth, and local identity normalization. See [[KB-BATCH8-hosted-auth]] for the full analysis.

### 45. Smailnail OIDC Identity and Hosted Auth

**Date**: 2026-03-16

**Summary**: One hosted server now serves SPA, browser login/logout, session-backed API auth, MCP at `/mcp`, and protected-resource metadata. Key insight: local app identity is keyed by `(issuer, subject)` across both browser and bearer-token surfaces.

### 46. go-go-mcp Hosted OIDC and Smailnail Delivery

**Date**: 2026-03-18

**Summary**: `go-go-mcp` became the hosted-auth substrate for Smailnail. Key insight: an embeddable MCP server must carry verified identity through request context into tool execution.

### 47. Hair Booking — MVP Buildout, Hosted Auth, Vault, and Production Fixes

**Date**: 2026-03-25

**Summary**: Hosted product with dedicated Keycloak realm, SES, Vault-backed SMTP sync, and embedded React frontend. Key insight: hosted auth is part of the product runtime, not an afterthought.

### 48. Smailnail Hosted Identity, Terraform, and Claude Fix

**Date**: 2026-03-18

**Summary**: Branch-level report for hosted Smailnail identity, Terraform migration, and Claude DCR fix. Key insight: production auth blockers can live in Keycloak registration policy, not the app server.

### 49. Keycloak Identity Platform on Coolify

**Date**: 2026-03-16

**Summary**: Central identity provider on `auth.scapegoat.dev` for multiple hosted services. Key insight: Keycloak is the issuer; consuming apps should still normalize local identity in app-owned terms.

---

## Batch 9: Tree-sitter and Structured Text Systems (6 projects)

Focused batch from the campaign handoff's Batch C. See [[KB-BATCH9-tree-sitter-structured-text]] for the full analysis.

### 50. Query Treesitter — Tree-sitter Query Language Prototypes and Design

**Date**: 2026-03-15

**Summary**: Research repo exploring a better query language for Tree-sitter-style syntax trees. It compares Norvig-style unification, TUQL relational syntax, and Hybrid TUQL with lightweight semantic relations. Key insight: Tree-sitter is the structural substrate; richer AST tooling needs a semantic/query layer above it.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-14--query-treesitter` | `norvig/`, `tuql/`, `hybrid-tuql/` prototypes |

**On-Ramp entries**: [[On-Ramp/tree-sitter-for-go-tools]]

**Tribal candidates**:
- Tree-sitter as structural prefilter plus semantic layer (1/3 here; 3/3 across batch, review needed)
- Repeated-variable subtree equality (1/3)
- User-defined named AST queries (1/3)
- Host-language custom predicates and binders (1/3)

**On-Ramp candidates**: Tree-sitter query language (covered by [[On-Ramp/tree-sitter-for-go-tools]]), first-order unification for AST matching (1/5), lexical scope / declaration-use resolution (1/5)

### 51. Sanitize — Tree-sitter Structured Text Sanitizer

**Date**: 2026-03-15

**Summary**: Go CLI/library/server for structured-text sanitizing across YAML and JSON. Tree-sitter provides parse evidence, the packages add linting and conservative fix rules, and the browser UI acts as a recovery lab. Key insight: almost-valid text should be repaired only when the fix is explainable.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-05--yaml-sanitizing` | `pkg/yaml`, `pkg/json`, CLI, server, browser playground |

**On-Ramp entries**: [[On-Ramp/tree-sitter-for-go-tools]]

**Tribal candidates**:
- Conservative repair boundary (1/3 here; 3/3 across Sanitize reports, review needed)
- Format-specific engines under one CLI/server surface (1/3)
- Example corpus as repair evidence loop (1/3)
- Parse/lint/fix as inspectable local workflow (1/3)

**On-Ramp candidates**: Structured text recovery for LLM outputs (1/5 🌐 domain seed)

### 52. Tree-sitter Templating — Syntax-Aware Code Expansion System

**Date**: 2026-03-15

**Summary**: Go backend + React/Monaco prototype for deterministic syntax-aware code expansion. The backend parses incrementally with Tree-sitter, evaluates data-driven rules, and sends proposals or patches over WebSocket. Key insight: syntax-aware behavior should come from backend parse state and rules, not frontend heuristics.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-14--treesitter-templating` | `pkg/parser`, `pkg/rules`, `pkg/session`, `pkg/protocol`, React frontend |

**On-Ramp entries**: [[On-Ramp/tree-sitter-for-go-tools]]

**Tribal candidates**:
- Backend-authoritative syntax tooling (1/3; related to backend snapshot patterns)
- Rule = query + trigger + guard + expansion (1/3)
- Fired-key idempotence for editor proposals (1/3)
- Changed-range filtered rule evaluation (1/3)

**On-Ramp candidates**: Monaco editor integration with Go backend (1/5), WebSocket editor protocol (1/5)

### 53. Sanitize — JSON Recovery Experiments and Limits

**Date**: 2026-03-27

**Summary**: Focused report on the JSON side of `sanitize`, especially malformed LLM JSON recovery. The work shipped narrow fixes for wrappers, comments, Python literals, duplicate commas, and trailing commas, while proving broad structural JSON repair is unsafe. Key insight: detection and repair are different products.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-05--yaml-sanitizing` | `pkg/json`, JSON corpus, parse matrices, repair matrix |

**On-Ramp entries**: [[On-Ramp/tree-sitter-for-go-tools]]

**Tribal candidates**:
- Conservative repair boundary (2/3 here, 3/3 across Sanitize reports, review needed)
- Strict-parser plus Tree-sitter dual validation (1/3)
- Detection vs repair separation (1/3)
- Repair matrix as engineering artifact (1/3)

**On-Ramp candidates**: Malformed LLM JSON recovery (1/5 🌐 domain seed)

### 54. Sanitize — YAML Sanitizing Deep Dive

**Date**: 2026-03-27

**Summary**: Deep dive on the mature YAML side of `sanitize`. The central architecture is a shared parse-aware analysis pass that feeds parse, lint, duplicate-key traversal, and fix orchestration. Key insight: successful sanitizing is iterative and conservative, not one heroic parser trick.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-05--yaml-sanitizing` | `pkg/yaml/analysis.go`, `lint.go`, `fix.go`, `sanitize.go` |

**On-Ramp entries**: [[On-Ramp/tree-sitter-for-go-tools]]

**Tribal candidates**:
- Shared parse-aware analysis object (1/3 here; 3/3 across Sanitize reports, review needed)
- Conservative iterative repair loop (1/3)
- Parser plus heuristic classification (1/3)
- Span-rich diagnostics as UI/API contract (1/3)

**On-Ramp candidates**: YAML parser recovery and duplicate-key behavior (1/5)

### 55. Scenario Runtime Workbench — Scenario-Driven Reconciliation Demo

**Date**: 2026-03-15

**Summary**: Interactive workbench for inspectable controller-style loops. Go owns lifecycle, sessions, transport, snapshots, and WebSocket events; JavaScript owns scenario semantics; React renders backend-authored snapshots. Key insight: reconciliation becomes teachable when observe, compare, plan, and execute are visible stages.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-13--pod-deployment-demo` | Go runtime, Goja scenario scripts, React workbench, embedded docs |

**Tribal entries**: Reinforces [[Tribal/goja-execution-model]] as a runtime variation, but not a direct REPL/session instance.

**Tribal candidates**:
- Scenario package contract (1/3)
- Observe/compare/plan/execute visible reconciliation loop (1/3)
- Backend snapshot as source of truth (1/3)
- Go-owned lifecycle with JS-owned scenario semantics (1/3)

**On-Ramp candidates**: Reconciliation loops / controller pattern (1/5), Goja sandbox for scenario scripts (covered partly by goja KB entries)

## Batch 12: WASM / Browser Runtime Cluster (7 projects)

Focused batch from the campaign handoff's Batch J. See [[KB-BATCH12-wasm-browser-runtime]] for the full analysis.

### 56. WASM JSON Flattener — Go CLI and WebAssembly Tool

**Date**: 2026-04-14

**Summary**: Practical Go JSON flattener that runs both as a native CLI and as a browser WASM module. The same pure-Go flattening core powers standard Go and TinyGo browser targets, making the size/interoperability trade visible instead of theoretical.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-14--wasm-transcript-conversation/jsonflatten` | `pkg/flatten`, CLI wrapper, standard Go WASM, TinyGo WASM, web demos |

**Tribal entries**: Reinforces [[Tribal/go-to-wasm-compilation]]

**Tribal candidates**:
- Standard Go vs TinyGo comparison harness (3/3, covered by existing WASM KB entries)
- Dual-target utility with shared pure-Go kernel (2/3)
- Minimal WASI polyfill for TinyGo browser target (1/3)

**On-Ramp candidates**: Reinforces [[On-Ramp/wasm-from-go]]

### 57. JSON Flattener — Go WASM JSON Conversion Tool

**Date**: 2026-04-15

**Summary**: Second report variant for the JSON Flattener project, emphasizing the single-codebase dual-target story and the 95% TinyGo size reduction. Useful mainly as additional support for the same Go→WASM pattern rather than as a separate architecture cluster.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-14--wasm-transcript-conversation/jsonflatten` | same canonical JSON Flattener repo; alternate report framing |

**Tribal entries**: Reinforces [[Tribal/go-to-wasm-compilation]]

**Tribal candidates**:
- Reinforces standard Go vs TinyGo comparison harness
- Reinforces dual-target utility with shared pure-Go kernel

**On-Ramp candidates**: No separate count beyond the canonical JSON Flattener cluster

### 58. VT100 WASM Emulator

**Date**: 2026-04-15

**Summary**: Browser-based Rust/WASM emulator for the DEC VT100 that models the actual 8080 firmware and hardware rather than only escape-sequence behavior. It broadens the batch from Go-specific browser WASM into hardware-faithful browser emulation.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-15--8080-rom/vt100-wasm-emulator` | Rust 8080 CPU, VT100 system integration, planned browser UI |

**Tribal entries**: None new

**On-Ramp candidates**: VT100 hardware emulation mental model (1/5 🌐), Rust/WASM browser emulator architecture (1/5 🌐)

### 59. Goja WASM Web REPL — A JavaScript Sandbox in the Browser

**Date**: 2026-04-25

**Summary**: Browser REPL that runs Goja compiled to WASM, exposing a tiny `gojaEval` bridge through `syscall/js`. The project demonstrates both the usefulness of nested runtimes for sandboxing and the practical TinyGo timeout constraint on larger initialization-heavy programs.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-25--goja-wasm-web-repl` | Goja REPL WASM module, browser test page, TinyGo experiments, ticket docs |

**Tribal entries**: Reinforces [[Tribal/go-to-wasm-compilation]]

**Tribal candidates**:
- goja-in-WASM as sandbox boundary (2/3 with Capsule Lab)
- Standard Go vs TinyGo comparison harness (covered by existing WASM KB entries)
- TinyGo interpreter-timeout as compile-system constraint (1/3)

**On-Ramp candidates**: Reinforces [[On-Ramp/wasm-from-go]]

### 60. WASM Plugin REPL — Goja wazero Deep Dive

**Date**: 2026-04-25

**Summary**: Pure-Go host/guest plugin architecture where Wasm guests request capabilities through imports and exchange data through a JSON-through-memory ABI. The key lesson is that a plugin system stays understandable only if the host mediates capabilities instead of letting guests tunnel through the boundary.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-25--goja-wazero` | wazero plugin manager, host module, primitive registry, Goja bridge, example plugins |

**Tribal entries**: Adjacent to [[Tribal/data-only-vs-host-access-module-split]]

**Tribal candidates**:
- Host-mediated guest capability boundary (2/3 with Capsule Lab)
- JSON-through-memory Wasm ABI (1/3)
- One primitive registry shared by JS callers and Wasm guests (1/3)

**On-Ramp candidates**: WASI / Wasm guest ABI for plugin calls (1/5 🌐)

### 61. Federated Modules — Single-Origin Runtime Demo

**Date**: 2026-03-22

**Summary**: Teaching-oriented Module Federation demo where host, remote, and registry are all served from one origin so the runtime-loading boundary stays visible. The important lesson is not scale; it is the difference between build-configured and runtime-discovered remote modules.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-22--federated-modules` | host app, remote app, registry, same-origin Express server, smoke script |

**Tribal entries**: None new

**Tribal candidates**:
- Same-origin runtime federation teaching surface (1/3)
- Runtime module shape discipline (1/3)

**On-Ramp candidates**: Module Federation mental model (1/5 🌐)

### 62. Browser-Side React Widget Runtime — In-Browser TSX Compilation and Reload

**Date**: 2026-04-30

**Summary**: Browser runtime that treats TSX source as data until the browser compiles it with `esbuild-wasm`, wraps it with host bindings, imports it as a blob module, and renders it as a React component. The project makes runtime code loading explicit instead of hiding it behind Vite HMR assumptions.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-30--react-browser-reload` | live-widget runtime, demo app, Go harness server, ticket docs |

**Tribal entries**: None new

**Tribal candidates**:
- Source string → browser transform → blob import runtime (1/3)
- Shared React instance injected into dynamic modules (1/3)
- Strict import allowlist before compilation/import (1/3)

**On-Ramp candidates**: Browser-side TSX compilation and blob-module import (1/5 🌐)

## Batch 13: Cozo / Editor / Structured Browser Tools (6 projects)

Focused batch from the campaign handoff's Batch D. See [[KB-BATCH13-cozo-editor-structured-browser-tools]] for the full analysis.

### 63. CozoDB Editor — SEM Streaming, Widgetization, and Hydration Refactor

**Date**: 2026-03-15

**Summary**: Browser-based CozoScript workbench where AI output becomes a semantic event stream rather than plain prose. The backend extracts structured payloads, the frontend projector turns them into stable bundle-backed UI threads, and widgets render under editor context. Key insight: semantic assistance needs a stable local event contract, not just streamed text.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-14--cozodb-editor` | Cozo editor backend/frontend, semantic extraction pipeline, projector, widget renderer |

**Tribal entries**: None new

**Tribal candidates**:
- Backend-authoritative semantic event stream projected into stable UI threads (2/3 across the Cozo editor line)
- Request-scoped projection defaults (1/3)
- Canonical preview/final identity (1/3)
- Preset adapter over notebook core behavior (supports later Cozo packaging line; 3/3 across the broader family)

**On-Ramp candidates**: Semantic event projection in notebook/editor UIs (1/5 internal-domain seed)

### 64. CozoScript Web UI — CodeMirror Language Package and Browser Editor

**Date**: 2026-03-19

**Summary**: Browser-native CozoScript editor built around a Lezer grammar, CodeMirror 6 language package, and CozoDB WASM-backed web shell. The project treats the grammar and language package as the main product, with the browser UI as a thin consumer. Key insight: grammar first, editor second, shell third.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-02-24--cozoscript-treesitter-autocomplete` | `lang-cozoscript`, `cozo-webui`, examples, Lezer grammar, tests |

**Tribal entries**: None new

**Tribal candidates**:
- Language package as product, browser shell as consumer (2/3 with later Cozo editor modularization)
- Parse-context-driven autocomplete rather than regex-driven autocomplete (1/3)
- Browser shell intentionally thin over language package (1/3)

**On-Ramp candidates**: CodeMirror 6 language package mental model (2/5 🌐)

### 65. CozoDB Editor — Notebook Packaging and JavaScript Preset

**Date**: 2026-03-22

**Summary**: Cozo-focused notebook environment refactored into shared notebook infrastructure plus current preset families, including a JavaScript preset powered by go-go-goja. Key insight: keep shared notebook seams honest, and keep runtime-specific behavior behind preset wrappers.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-14--cozodb-editor` | shared backend/frontend notebook modules, current Cozo and JS presets, Storybook/MSW validation |

**Tribal entries**: None new

**Tribal candidates**:
- Preset adapter over notebook core behavior (2/3 here; 3/3 across the Cozo line)
- Shared notebook seams own runtime result vocabulary (1/3)
- Storybook/MSW as architecture test for preset surfaces (1/3)

**On-Ramp candidates**: Notebook preset architecture (2/5)

### 66. CozoDB Editor — Merge Resolution, SQLite Preset, and Editor Highlighting

**Date**: 2026-03-23

**Summary**: Follow-up proving that the packaged notebook/editor architecture survives a real upstream merge and absorbs a third preset family through SQLite. The key lesson is architectural: when a feature differs by runtime or language, add or refine an adapter instead of mutating the notebook core.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-14--cozodb-editor` | notebook package, preset registry, reusable CodeMirror shell, SQLite preset, merge-resolved frontend |

**Tribal entries**: None new

**Tribal candidates**:
- Preset adapter over notebook core behavior (3/3 across the Cozo line)
- Language package as product, browser shell as consumer (2/3 with CozoScript Web UI)
- Keep modular architecture during merge; port behavior into new seams instead of regressing structure (1/3)

**On-Ramp candidates**: CodeMirror 6 language package mental model (2/5 🌐), Notebook preset architecture (2/5)

### 67. SQLide Browser — Go Wasm SQL IDE

**Date**: 2026-04-02

**Summary**: Browser-only SQL IDE where Go/Wasm handles SQL splitting and editor intelligence while SQLite's own Wasm build runs in a worker and owns OPFS persistence. Key insight: keep the split architecture until an all-Go persistence story is actually proven.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-02--sqlide-browser` | Go/Wasm module, bridge loader, SQLite worker, OPFS persistence, browser UI |

**Tribal entries**: Reinforces [[On-Ramp/wasm-from-go]]

**Tribal candidates**:
- Go/Wasm editor intelligence over worker-owned SQLite engine (2/3 when considered with broader Wasm/browser evidence)
- Keep split architecture: text/state in Go, DB engine in worker (1/3)

**On-Ramp candidates**: SQLite worker + OPFS mental model (1/5 🌐)

### 68. Hover Component Inspector — Building a Browser Overlay Lens

**Date**: 2026-04-28

**Summary**: Chrome MV3 extension that inspects hovered page elements through a content-script overlay rendered in Shadow DOM. The important insight is boundary discipline: the overlay must see the page without becoming the page, and component identity must be treated as evidence rather than certainty.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-28--overlay-extenseion` | MV3 extension, content script, overlay, inspector helpers, popup/options, tests |

**Tribal entries**: None new

**Tribal candidates**:
- Page-level overlay as guest, not page owner (1/3)
- Inspection result as central curated data structure (1/3)
- Component identity as evidence, not certainty (1/3)

**On-Ramp candidates**: Browser overlay inspection architecture (1/5 🌐)

### 69. Pi Extension — Hello World Before Thinking Blocks

**Date**: 2026-04-21

**Summary**: Minimal Pi extension that watches `message_update` for thinking-block events and displays a widget while the model is thinking. Key insight: streaming assistant events are an observation seam; UI should be added through documented widget APIs rather than mutating messages.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-21--pi-extensions` | hello-world-thinking extension, docmgr analysis, API cheat sheet, setup/test playbook |

**Tribal entries**: Created [[Tribal/pi-extension-event-seams]]

**Tribal candidates**:
- Thinking-block UI as stream observer, not message mutation (covered by [[Tribal/pi-extension-event-seams]])
- Widget cleanup on lifecycle edges (covered by [[Tribal/pi-extension-event-seams]])

**On-Ramp candidates**: Pi extension authoring mental model (1/5), Pi TUI widget/status surfaces (1/5)

### 70. Pi Extension — A Textbook on Writing and Testing Pi Extensions

**Date**: 2026-04-23

**Summary**: Textbook-style report that generalizes the first two Pi extensions into the observation/injection/display model. Key insight: most events are read-only observations; the few mutable seams must be used deliberately.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-21--pi-extensions` | hello-world and session-summary extensions, textbook docs, go-minitrace analysis examples |

**Tribal entries**: Reinforces [[Tribal/pi-extension-event-seams]] and [[Tribal/transcript-analysis-with-go-minitrace]]

**Tribal candidates**:
- Observation / injection / display as extension architecture (covered by [[Tribal/pi-extension-event-seams]])
- File logging plus go-minitrace as extension debugging workflow (1/3; related to [[Tribal/transcript-analysis-with-go-minitrace]])

**On-Ramp candidates**: Pi extension authoring mental model (2/5), Pi TUI widget/status surfaces (2/5)

### 71. Pi Session Summary Extension — Textbook Report

**Date**: 2026-04-25

**Summary**: Extension that enforces a `<summary>` contract, parses the final assistant response, and renders a full-width-aware summary widget. Key insight: use a contract + parser + widget architecture, and keep the raw assistant text as the durable record.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/session-summary` | prompt contract, turn_end parser, widget renderer, commands, directory symlink install |

**Tribal entries**: Reinforces [[Tribal/pi-extension-event-seams]]

**Tribal candidates**:
- Contract + parser + widget extension architecture (1/3)
- Multi-file Pi extension installed as directory symlink (1/3)
- Widget should preserve meaning and only adapt wrapping (1/3)

**On-Ramp candidates**: Pi extension authoring mental model (3/5), Pi TUI widget/status surfaces (3/5)

### 72. Pi Extensions — Agent Env, Response Capture, and Compaction Meter

**Date**: 2026-04-26

**Summary**: Three operational extensions: `agent-env` exports session/tool metadata into shell commands, `response-capture` saves assistant output into docmgr, and `compaction-meter` shows distance to compaction. Key insight: each extension should touch one boundary and preserve Pi's built-in behavior around it.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/agent-env` | PI_AGENT_* command preamble and self-tests |
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/response-capture` | turn_end response capture, markdown save, docmgr import |
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/compaction-meter` | context-usage arithmetic and footer status |

**Tribal entries**: Reinforces [[Tribal/pi-extension-event-seams]]

**Tribal candidates**:
- Safe bash command preamble injection with idempotence markers (1/3)
- Extension-to-docmgr artifact handoff via saved markdown and `docmgr import file` (1/3)
- Status item as lightweight agent instrument (1/3)

**On-Ramp candidates**: Pi extension authoring mental model (4/5), Pi TUI widget/status surfaces (4/5), Pi context compaction model (1/5)

### 73. Pi Extensions — Compaction Title Extension

**Date**: 2026-04-27

**Summary**: Extension that reuses Pi's built-in `compact()` helper, appends title instructions, parses `## Session Title`, and stores the title as session metadata. Key insight: compaction is memory preservation first; title generation is a narrow appendix.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/compaction-title` | session_before_compact hook, title parser, session name storage, self-tests |

**Tribal entries**: Reinforces [[Tribal/pi-extension-event-seams]]

**Tribal candidates**:
- Built-in behavior plus one appendix for high-risk hooks (1/3)
- Compaction as session metadata checkpoint (1/3)
- Multi-file Pi extension installed as directory symlink (2/3)

**On-Ramp candidates**: Pi extension authoring mental model (5/5 — ready/covered by article; consider On-Ramp only if KB form is desired), Pi context compaction model (2/5)

### 74. Pi Extensions — Direnv Bash Extension

**Date**: 2026-04-27

**Summary**: Extension that loads the current directory's allowed direnv environment before Pi bash and user_bash commands. Key insight: preserve Pi's built-in bash runner and direnv's trust model by injecting `direnv export bash`, not by sourcing `.envrc` directly.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-21--pi-extensions/extensions/direnv-bash` | direnv shell preamble, tool_call/user_bash hooks, tmux tests, README |

**Tribal entries**: Reinforces [[Tribal/pi-extension-event-seams]]

**Tribal candidates**:
- Safe bash command preamble injection with idempotence markers (2/3 with agent-env)
- Preserve external tool trust model instead of bypassing it (1/3)
- Extension load + standalone + tmux validation ladder (1/3)

**On-Ramp candidates**: Pi extension authoring mental model (5/5), Pi TUI widget/status surfaces (4/5), direnv for agent-launched shells (1/5)

### 75. Configuring Wafer Models in Pi

**Date**: 2026-05-05

**Summary**: Configuration report adding Wafer Pass as a custom OpenAI-compatible provider in Pi's `models.json`. Key insight: model-provider integration is a schema/configuration seam; use provider docs for hard limits, validate JSON, and treat `pi --list-models` as the local registry ground truth.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/gec/2026-03-16--gec-rag` | work context for Wafer/Pi configuration |
| `~/.pi/agent/models.json` | Pi custom provider registry edited by the project |

**Tribal entries**: Reinforces [[Tribal/pi-extension-event-seams]] at the configuration/provider boundary

**Tribal candidates**:
- Documentation-first model-provider registration (1/3)
- `pi --list-models` as registry validation ground truth (1/3)

**On-Ramp candidates**: Pi custom model/provider configuration (1/5 🌐), OpenAI-compatible model endpoint registration (1/5)

### 76. Codebase Browser — Embedded Go+TS Doc Server with Live Source Snippets

**Date**: 2026-04-19

**Summary**: Single-binary documentation browser for Go and TypeScript codebases. A build-time indexer emits one schema-shared index, a Go binary embeds index/source/docs/SPA assets, and markdown pages resolve live source snippets by symbol ID.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-19--go-codebase-browser` | Go+TS indexer, embedded source/index/doc FS, Go server, React SPA, Dagger TS build |

**Tribal entries**: Created [[Tribal/canonical-doc-model-across-delivery-modes]]

**Tribal candidates**:
- Stable symbol IDs as documentation contract (1/3)
- Schema-first multi-language code index (1/3; reinforced by drill-down)
- Live source snippets by symbol identity, not copy-paste (1/3)

**On-Ramp candidates**: Go CLI with embedded SPA (3/5), TypeScript Compiler API for code intelligence (1/5), Dagger-orchestrated Node tooling from Go (1/5)

### 77. Codebase Browser — Static Analysis and Dagger Pipeline

**Date**: 2026-04-20

**Summary**: Drill-down on the Codebase Browser's Go+TypeScript static analysis pipeline and Dagger-orchestrated Node build. Key insight: one shared schema plus deterministic Dagger/local outputs makes the Node toolchain a build-time implementation detail, not a runtime dependency.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-19--go-codebase-browser` | `internal/indexer`, `tools/ts-indexer`, `cmd/build-ts-index`, `internal/indexfs` |

**Tribal entries**: Reinforces [[Tribal/canonical-doc-model-across-delivery-modes]]

**Tribal candidates**:
- Schema-first multi-language code index (2/3 with embedded server report)
- Dagger/local build paths must produce byte-identical artifacts (1/3)
- Build-time foreign toolchain behind Go orchestrator (1/3)

**On-Ramp candidates**: Dagger-orchestrated Node tooling from Go (2/5), TypeScript Compiler API for code intelligence (2/5)

### 78. Codebase Browser — Static WASM Build and SQLite Prototype

**Date**: 2026-04-23

**Summary**: Codebase Browser can now ship as a static artifact and has a working SQLite/browser prototype. Key insight: the browser UI should keep asking for index/package/symbol/xref/doc data while the transport changes from live HTTP to static/Wasm/SQLite.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-19--go-codebase-browser` | static build, TinyGo/Wasm lookup path, SQLite design/prototype scripts |

**Tribal entries**: Reinforces [[Tribal/canonical-doc-model-across-delivery-modes]] and [[On-Ramp/wasm-from-go]]

**Tribal candidates**:
- Dual-mode frontend over live API or static snapshot (3/3 — covered by [[Tribal/canonical-doc-model-across-delivery-modes]])
- Shared canonical model across delivery modes (3/3 — covered by [[Tribal/canonical-doc-model-across-delivery-modes]])
- SQLite as browser-queryable documentation/index runtime (1/3)

**On-Ramp candidates**: Go CLI with embedded SPA (4/5), SQLite worker/browser database mental model (2/5), static browser artifact with HashRouter/file delivery (1/5)

### 79. Glazed Help Export and External Serve Sources

**Date**: 2026-04-28

**Summary**: Glazed help became a portable documentation interface: `help export` emits JSON/files/SQLite, and `glaze serve --from-*` loads markdown, JSON, SQLite, or another Glazed binary's export. Key insight: structured help is a database/product surface, not just terminal text.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/corporate-headquarters/glazed` | `pkg/help/cmd/export.go`, `pkg/help/loader/sources.go`, `pkg/help/server/serve.go`, help docs |

**Tribal entries**: Reinforces [[Tribal/canonical-doc-model-across-delivery-modes]]

**Tribal candidates**:
- Documentation export as subsystem contract (1/3)
- External documentation sources as loaders into canonical store (1/3)
- Unsafe slugs become security-sensitive when exported as files (1/3)

**On-Ramp entries**: [[On-Ramp/go-cli-with-embedded-spa]]

**On-Ramp candidates**: SQLite as documentation snapshot format (1/5), Glazed help entries as structured docs (1/5)

### 80. Rabbit Hole Podcast Intros — Remotion Video Generation

**Date**: 2026-04-11

**Summary**: Remotion/React project generating podcast video intros with programmatic animation, deep-fried visual effects, and synthesized audio. Key insight: short-form video can be generated as code when timing, audio, and visual effects are frame-addressable.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/patreon/videos/003-rabbit-hole` | Remotion compositions, generated audio assets, Python audio synthesis |

**Tribal entries**: None new

**Tribal candidates**:
- Programmatic media composition as code (1/3)
- Generated audio SFX as timeline assets (1/3)

**On-Ramp candidates**: Remotion for code-generated video (1/5 🌐), browser/React video rendering mental model (1/5)

### 81. Jingle Extractor — AI Audio Pipeline with MiniMax Demucs WhisperX

**Date**: 2026-04-13

**Summary**: Python audio pipeline that generates music, separates stems with Demucs, transcribes vocals with WhisperX, mines beat-aligned clips with librosa, and exports vocal/instrumental/mixed jingles. Key insight: useful media tools are staged pipelines with explicit intermediate artifacts.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-13--jingle-extraction` | MiniMax integration, Demucs, WhisperX, librosa scoring, pydub export |

**Tribal entries**: None new

**Tribal candidates**:
- Staged ML media pipeline with durable intermediates (1/3)
- Beat/transient-scored clip mining (1/3)

**On-Ramp candidates**: ASR/stem-separation audio pipeline (1/5 🌐), Demucs stem separation (1/5), WhisperX word-level alignment (1/5)

### 82. Transcription Go — Dagger Nemotron ASR Pipeline

**Date**: 2026-04-13

**Summary**: Go transcription CLI with pure-Go WAV conversion, Dagger-managed Python/Nemotron ASR service, and Go-owned SRT/VTT/TXT/SQLite output. Key insight: keep the ML runtime behind a narrow inference service and let Go own the product artifact boundary.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-13--transcription-go` | Go CLI, Dagger service/tunnel lifecycle, FastAPI ASR, output writers |

**Tribal entries**: None new

**Tribal candidates**:
- ML service as narrow inference engine, Go owns artifacts (1/3)
- Dagger host-tunnel lifecycle discipline (1/3)
- Pure-Go media conversion to reduce host dependencies (1/3)

**On-Ramp candidates**: ASR pipeline architecture (2/5), Dagger service + host tunnel lifecycle (1/5)

### 83. Transcription Go — Streaming Transcription Architecture

**Date**: 2026-04-13

**Summary**: Streaming transcription subsystem with replay-driven validation, WebSocket sessions, explicit partial/final transcript state, SQLite outputs, and timing fixes around incoming `pts`. Key insight: streaming transcription is a state/timing problem, not merely a transport problem.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-04-13--transcription-go` | live command, WebSocket transport, transcript state, replay metrics, SQLite comparison tools |

**Tribal entries**: None new

**Tribal candidates**:
- Pending vs committed transcript state (1/3)
- Replay-driven validation for live media systems (1/3)
- Incoming PTS as authority for streaming timestamps (1/3)

**On-Ramp candidates**: ASR pipeline architecture (3/5), WebSocket streaming media/session model (1/5), transcript timing semantics (1/5)

### 84. MiroTalk SFU on K3s — Video Realm and WebRTC Deployment

**Date**: 2026-04-28

**Summary**: GitOps/K3s deployment of MiroTalk SFU with Keycloak OIDC, Vault-synced secrets, TLS ingress, and direct TCP/UDP media ports. Key insight: the web page and WebRTC media packets are different network paths.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-27--hetzner-k3s` | Kustomize app, Argo CD application, hostNetwork deployment, firewall/media config |
| `/home/manuel/code/wesen/terraform/keycloak/apps/mirotalk-sfu/envs/k3s-parallel` | dedicated Keycloak video realm and OIDC client |

**Tribal entries**: Reinforces [[On-Ramp/oauth-2-oidc-flows]] and [[On-Ramp/vault-on-k3s-with-vso]]

**Tribal candidates**:
- WebRTC media plane is not HTTPS ingress (1/3)
- Dedicated identity realm for media app (1/3)

**On-Ramp candidates**: WebRTC/SFU deployment mental model (1/5 🌐), mediasoup/MiroTalk SFU orientation (1/5)

### 85. Static Apple Music Player — Deep Dive

**Date**: 2026-05-01

**Summary**: Static MusicKit JS frontend backed by a narrow Go token server that signs short-lived Apple Music developer tokens while keeping the `.p8` private key out of the browser. Key insight: static frontend does not mean secret-free; the backend should own exactly the secret-bearing operation.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-05-01--static-music-player` | Go/Glazed server, Apple token signer, static MusicKit frontend |

**Tribal entries**: Reinforces [[Tribal/host-mediated-secret-delivery]] and [[On-Ramp/go-cli-with-embedded-spa]]

**Tribal candidates**:
- Static frontend plus token-vending backend (1/3)
- Browser owns playback, backend owns developer identity (1/3)

**On-Ramp candidates**: MusicKit JS / Apple Music developer token model (1/5 🌐), browser media API playback model (1/5)

### 86. Latent Space Podcast Downloader

**Date**: 2026-05-02

**Summary**: Python script that downloads latent.space podcast episodes from RSS when available and falls back to YouTube/yt-dlp when Substack's 20-item feed window drops older episodes. Key insight: media downloaders often need discovery fallbacks and MIME-aware enclosure handling, not just URL fetching.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/claw-stuff/scripts/01-download-latent-space.py` | RSS parsing, MIME filtering, YouTube search fallback, yt-dlp extraction |

**Tribal entries**: None new

**Tribal candidates**:
- Discovery ladder for podcast/audio downloads (1/3)
- MIME type over file extension for RSS enclosure classification (1/3)

**On-Ramp candidates**: Podcast RSS enclosure model (1/5), yt-dlp as fallback extractor (1/5)

### 87. LibriVox Player — Retro Macintosh Browser Audio Prototype

**Date**: 2026-03-22

**Summary**: Single-file browser audiobook player with retro Macintosh UI, curated LibriVox/Archive.org audio URLs, and direct `Audio.src` playback. Key insight: for a small static media prototype, verified source URLs and simple browser audio semantics matter more than clever fetch wrappers.

**Repos**:
| Path | Notes |
|------|-------|
| `/home/manuel/code/wesen/2026-03-22--librivox-player` | single-file HTML/CSS/JS player, static catalog, browser Audio controller |

**Tribal entries**: None new

**Tribal candidates**:
- Curated external media catalog as product data (1/3)
- Direct browser `Audio.src` over custom fetch wrappers (1/3)

**On-Ramp candidates**: Browser audio playback model (2/5), LibriVox/Archive.org audio sourcing (1/5)

---

## Campaign Status

- **Total project reports**: 167
- **Analyzed so far**: 87
- **Remaining**: 80
- **Current KB totals**:
  - Tribal: 22 entries
  - On-Ramp: 19 entries
  - Fundamentals: 5 entries

### Unwritten entries that are actually READY

There are a few threshold or near-threshold candidates that need editorial judgment before writing:

- **Pi extension authoring mental model** — 5/5, but much of the material already exists as a PARC article/playbook; decide whether to canonicalize it into an On-Ramp entry.
- **Tree-sitter as structural prefilter plus semantic layer**, **Conservative repair boundary**, **Shared parse-aware analysis object**, and **Preset adapter over notebook core behavior** — 3/3 Tribal candidates, but each may overlap with existing entries or be too product-family-specific.

What remains is mostly:
- sub-threshold candidates (1/3, 2/3, 1/5, 2/5, etc.)
- concepts intentionally folded into existing entries instead of split into new ones
- user-requested entries written below normal thresholds

---

## KB Candidate Tracking

### Tribal candidates (unwritten)

| Concept | Seen in | Status |
|---------|---------|--------|
| **Tree-sitter as structural prefilter plus semantic layer** | Query Treesitter, Tree-sitter Templating, Sanitize YAML/JSON | 3/3 — review before creating; partly covered by [[On-Ramp/tree-sitter-for-go-tools]] |
| **Conservative repair boundary** | Sanitize overview, Sanitize YAML, Sanitize JSON | 3/3 — review before creating |
| **Shared parse-aware analysis object** | Sanitize overview, Sanitize YAML, Sanitize JSON | 3/3 — review before creating; may be Sanitize-specific |
| **Three-layer credential separation** | Wish Git, Agent Enroll | 2/3 |
| **TFT_eSPI patching for RP2040** | uLisp PicoCalc, related display projects | 2/3 |
| **Bring-up sequence discipline** | Wi-Fi Audio Cues Lab, SToMS3R | 2/3 |
| **Spec-first VM implementation** | Smalltalk-80 VM, uLisp PicoCalc | 2/3 |
| **Buffer-full-body-before-UART** | SToMS3R, PaperS3 WAMR | 2/3 |
| **NDJSON as wire protocol for embedded** | Cardputer Web Serial, SToMS3R | 2/3 |
| **Keycloak group-gated Vault access** | Vault on K3s, Terraform Vault | 2/3 |
| **OIDC logout must clear provider session** | Smailnail OIDC, Hair Booking | 2/3 |
| **Runtime-scoped module registrars** | Plugins, Node-like Primitives | 2/3 |
| **Two-stage Glazed parsing for runtime config** | JS Discord Bot, related Glazed apps | 2/3 |
| **Envelope encryption for selective sharing** | E2E Storage, AUTODISCO Keyhive | 2/3 |
| **CRDT-local authorization layer** | AUTODISCO Keyhive, future CRDT projects | 2/3 |
| **OAuth refresh with bounded retry** | Remarquee, Smailnail OIDC | 2/3 |
| **goja-in-WASM as sandbox boundary** | Capsule Lab, Goja WASM Web REPL | 2/3 |
| **Host-mediated guest capability boundary** | Capsule Lab, WASM Plugin REPL | 2/3 |
| **Preset adapter over notebook core behavior** | Cozo Notebook Packaging, Cozo Merge/SQLite follow-up, Cozo SEM refactor | 3/3 — candidate |
| **Language package as product, browser shell as consumer** | CozoScript Web UI, Cozo editor modularization | 2/3 |
| **Host-mediated op-stream API** | Capsule Lab | 1/3 |
| **goja NaN sanitization in JSON export** | Capsule Lab | 1/3 |
| **Four-stage e-ink render pipeline** | Gnosis | 1/3 |
| **Draw batching at hardware-limited fps** | Loupedeck | 1/3 |
| **Mutant WebSocket over serial handling** | Loupedeck | 1/3 |
| **Broker-not-proxy architecture** | BYOK Host | 1/3 |
| **Authorization Code + PKCE from Go CLI** | BYOK Host, Wish Git | 2/3 |
| **SSH certificate as scoped delegation** | Wish Git | 1/3 |
| **pre-receive hook as policy enforcement** | Wish Git | 1/3 |
| **Server-as-relay-not-authority** | AUTODISCO | 1/3 |
| **Domain mutation helpers inside CRDT changes** | AUTODISCO | 1/3 |
| **Pin-swapping for K118 cable at runtime** | SToMS3R | 1/3 |
| **AtomS3R Lite over ATOM Lite for printer** | SToMS3R | 1/3 |
| **GStreamer pipeline construction from Go** | Screencast Studio | 1/3 |
| **Runtime seam for engine migration** | Screencast Studio | 1/3 |
| **GLib main loop coexistence with Go** | Screencast Studio | 1/3 |
| **Regression-trace-driven debugging** | Smalltalk-80 VM | 1/3 |
| **SmallInteger boundary bugs** | Smalltalk-80 VM | 1/3 |
| **Method cache hash translation** | Smalltalk-80 VM | 1/3 |
| **Context lifetime bugs as disguised send failures** | Smalltalk-80 VM | 1/3 |
| **Primitive argument widening** | Smalltalk-80 VM | 1/3 |
| **Flash-mapped buffer mutability bug** | PaperS3 WAMR | 1/3 |
| **Cross-board A/B debugging** | PaperS3 WAMR | 1/3 |
| **Web Serial for browser-to-embedded** | Cardputer Web Serial | 1/3 |
| **Go→WASM protocol engine A/B** | Cardputer Web Serial | 1/3 |
| **ESP-IDF driver_ng conflict** | Cardputer Web Serial | 1/3 |
| **GPIO pin swap at runtime** | SToMS3R | 1/3 |
| **Data-driven audio cue system** | Wi-Fi Audio Cues Lab | 1/3 |
| **ES8311 codec bring-up** | Wi-Fi Audio Cues Lab | 1/3 |
| **Phase accumulator tone generation** | Wi-Fi Audio Cues Lab | 1/3 |
| **Pending-only queue deduplication** | Wi-Fi Audio Cues Lab | 1/3 |
| **Monolithic sketch → flat C++ module split** | uLisp PicoCalc Firmware Split | 1/3 |
| **Arduino sketch preprocessing hazard** | uLisp PicoCalc Firmware Split | 1/3 |
| **Translation-unit-local macros are behavior** | uLisp PicoCalc Firmware Split | 1/3 |
| **CMake bridge for Arduino-Pico** | uLisp PicoCalc Firmware Split | 1/3 |
| **UF2 Loader deployment** | uLisp PicoCalc Firmware Split | 1/3 |
| **Shared error messages / internal linkage** | uLisp PicoCalc Firmware Split | 1/3 |
| **Canonical request signing** | Agent Enroll | 1/3 |
| **Opaque scoped bearer tokens** | Agent Enroll | 1/3 |
| **Enrollment tokens (one-time, hash-only)** | Agent Enroll | 1/3 |
| **ZK note routing logic** | ZK Tool | 1/3 |
| **Ext4 workspace as boundary artifact** | Firecracker VM | 1/3 |
| **HashiCorp go-plugin for JS modules** | Plugins | 1/3 |
| **process global opt-in** | Node-like Primitives | 1/3 |
| **Plugin authoring SDK** | Plugins | 1/3 |
| **Plugin discovery + manifest validation** | Plugins | 1/3 |
| **Runtime-scoped docs hub** | Plugins | 1/3 |
| **Docs-aware REPL autocomplete** | Plugins | 1/3 |
| **Result normalization before structpb** | Plugins | 1/3 |
| **Goja vs Sobek decision framework** | Goja vs Sobek | 1/3 |
| **goja-based Discord bot host** | JS Discord Bot | 1/3 |
| **defineBot DSL** | JS Discord Bot | 1/3 |
| **Single-bot per process** | JS Discord Bot | 1/3 |
| **UI DSL for Discord** | JS Discord Bot | 1/3 |
| **Static metadata extraction via AST** | jsverbs | 1/3 |
| **Source overlay runtime** | jsverbs | 1/3 |
| **Shared binding plan** | jsverbs | 1/3 |
| **Multi-source scanning** | jsverbs | 1/3 |
| **Stable symbol IDs as documentation contract** | Codebase Browser embedded server | 1/3 |
| **Schema-first multi-language code index** | Codebase Browser embedded server, Codebase Browser static analysis drill-down | 2/3 |
| **Dagger/local build paths must produce byte-identical artifacts** | Codebase Browser static analysis drill-down | 1/3 |
| **Documentation export as subsystem contract** | Glazed Help Export | 1/3 |
| **External documentation sources as loaders into canonical store** | Glazed Help Export | 1/3 |
| **Scanner-first JS command extraction** | jsverbs, go-minitrace PR #6 | 2/3 |
| **Repository-local command catalogs** | go-minitrace local config, related local overlays | 2/3 |
| **Safe bash command preamble injection with idempotence markers** | Pi agent-env, Pi direnv-bash | 2/3 |
| **Multi-file Pi extension installed as directory symlink** | Pi session-summary, Pi compaction-title | 2/3 |
| **Contract + parser + widget extension architecture** | Pi session-summary | 1/3 |
| **Extension-to-docmgr artifact handoff via saved markdown** | Pi response-capture | 1/3 |
| **Status item as lightweight agent instrument** | Pi compaction-meter | 1/3 |
| **Compaction as session metadata checkpoint** | Pi compaction-title | 1/3 |
| **Extension load + standalone + tmux validation ladder** | Pi direnv-bash | 1/3 |
| **Documentation-first model-provider registration** | Configuring Wafer Models in Pi | 1/3 |
| **Staged ML media pipeline with durable intermediates** | Jingle Extractor | 1/3 |
| **ML service as narrow inference engine, Go owns artifacts** | Transcription Go batch | 1/3 |
| **Dagger host-tunnel lifecycle discipline** | Transcription Go batch | 1/3 |
| **Pending vs committed transcript state** | Transcription Go streaming | 1/3 |
| **WebRTC media plane is not HTTPS ingress** | MiroTalk SFU | 1/3 |
| **Static frontend plus token-vending backend** | Static Apple Music Player | 1/3 |
| **Discovery ladder for podcast/audio downloads** | Latent Space Podcast Downloader | 1/3 |
| **Direct browser Audio.src over custom fetch wrappers** | LibriVox Player | 1/3 |

### Tribal concepts intentionally covered by existing entries

| Concept | Covered by |
|---------|------------|
| **Separate human auth from machine auth** | [[On-Ramp/oauth-2-oidc-flows]] + [[Tribal/keycloak-oauth-in-go-services]] |
| **(issuer, subject) as stable local user key** | [[Tribal/keycloak-oauth-in-go-services]] |
| **Dynamic client registration policy as auth boundary** | [[Tribal/keycloak-oauth-in-go-services]] + [[On-Ramp/oauth-2-oidc-flows]] |
| **Dedicated Keycloak realm per app** | [[Tribal/keycloak-oauth-in-go-services]] |

### On-Ramp candidates (unwritten)

| Concept | Seen in | Status | What's missing from public docs |
|---------|---------|--------|-------------------------------|
| **goja ECMAScript interpreter** | Capsule Lab, Loupedeck, go-go-goja ecosystem | 2/5 | README-level docs are too sparse; embedding/module/session patterns are missing |
| **GStreamer for Go programmers** | Screencast Studio, future media projects | 2/5 🌐 | GStreamer docs are C-centric; Go bindings and CGo/coexistence patterns are underexplained |
| **Arduino-cli cross-compilation** | uLisp PicoCalc, future Arduino projects | 2/5 🌐 | Arduino docs assume IDE-first workflows |
| **Obsidian CLI from Go** | ZK Tool | 1/5 | Obsidian docs exist, but not the Go-centric integration patterns |
| **ESM support in Go JS engines** | Goja vs Sobek | 1/5 🌐 | Spec exists; engine migration/orientation material does not |
| **Dagger-orchestrated Node tooling from Go** | Codebase Browser embedded server, Codebase Browser static analysis drill-down | 2/5 | Dagger docs exist, but not the Go-orchestrated pnpm/Node build-time toolchain pattern. |
| **TypeScript Compiler API for code intelligence** | Codebase Browser embedded server, Codebase Browser static analysis drill-down | 2/5 | TS Compiler API docs exist, but alias-following/xref extraction needs a newcomer orientation. |
| **SQLite as documentation snapshot format** | Glazed Help Export | 1/5 | SQLite docs exist, but not docs/help export as portable queryable artifact. |
| **ASR pipeline architecture** | Jingle Extractor, Transcription Go batch, Transcription Go streaming | 3/5 🌐 | Public ASR docs are model-specific; our projects need the pipeline view: conversion, chunking, alignment, transcript state, and durable outputs. |
| **Browser audio playback model** | Static Apple Music Player, LibriVox Player | 2/5 | Browser media docs exist, but our reports need orientation around Audio/MusicKit, autoplay, source URLs, and token boundaries. |
| **WebRTC/SFU deployment mental model** | MiroTalk SFU | 1/5 🌐 | WebRTC docs exist, but not the K3s/ingress/firewall/media-plane deployment view. |
| **Podcast RSS enclosure model** | Latent Space Podcast Downloader | 1/5 | RSS docs exist, but feed windowing, enclosure MIME types, and fallback discovery need a practical orientation. |
| **Remotion for code-generated video** | Rabbit Hole Podcast Intros | 1/5 🌐 | Remotion docs exist, but not the frame-addressed media-as-code mental model. |
| **CodeMirror 6 language package mental model** | CozoScript Web UI, Cozo editor modularization | 2/5 🌐 | Docs exist, but not the “grammar first, highlighting second, shell third” orientation from a real language workbench port. |
| **Notebook preset architecture** | Cozo notebook packaging line | 2/5 | Notebook docs are often framework-specific and do not explain the preset/runtime split crisply. |
| **SQLite worker + OPFS mental model** | SQLide Browser | 1/5 🌐 | SQLite Wasm and OPFS docs exist, but not the precise boundary between Go/Wasm text logic, worker RPC, and DB ownership. |
| **Browser overlay inspection architecture** | Hover Component Inspector | 1/5 🌐 | Browser extension docs exist, but not a newcomer-focused mental model for overlay-as-guest inspection. |
| **Pi extension authoring mental model** | Pi Hello World, Pi Extension Textbook, Session Summary, Agent Env/Response Capture/Compaction Meter, Compaction Title, Direnv Bash | 5/5 — ready/covered by article; consider KB On-Ramp if the article should be canonicalized into KB form. |
| **Pi TUI widget/status surfaces** | Pi Hello World, Pi Extension Textbook, Session Summary, Agent Env/Response Capture/Compaction Meter | 4/5 🌐 | Pi docs list APIs, but a newcomer needs the surface-selection mental model: status vs widget vs overlay vs renderer. |
| **Pi context compaction model** | Compaction Meter, Compaction Title | 2/5 | Pi docs describe compaction, but extension authors need the operational model for thresholds, hooks, and continuation summaries. |
| **Pi custom model/provider configuration** | Configuring Wafer Models in Pi | 1/5 🌐 | Pi docs describe models.json, but provider registration needs a documentation-first, validation-oriented workflow. |

### On-Ramp entries created during the campaign

These are in the library already and should not be treated as unwritten candidates:
- [[On-Ramp/tree-sitter-for-go-tools]] — threshold-triggered by Batch 9 / handoff Batch C

### On-Ramp entries created below threshold by request

These are in the library already and should not be treated as unwritten candidates:
- [[On-Ramp/esp-idf-console-repl-bring-up]]
- [[On-Ramp/web-serial-browser-to-embedded]]
- [[On-Ramp/es8311-codec-bring-up-atoms3r]]
- [[On-Ramp/v6-rmdoc-scene-tree-rendering]]
- [[On-Ramp/vault-on-k3s-with-vso]]
- [[On-Ramp/browser-e2e-encryption-with-web-crypto]]
- [[On-Ramp/automerge-keyhive-local-first-auth]]
- [[On-Ramp/what-is-a-stack-based-vm]]

### Fundamental candidates (unwritten)

| Concept | Supports | Status |
|---------|----------|--------|
| **Distributed consistency** | [[On-Ramp/crdts-and-local-first]] | 1 supporting KB entry — needs 1 more |

---

## KB Entries in the Library

### Tribal

The current tribal library contains the 22 entries in `Research/KB/Tribal/`, including the campaign-created entries:
- [[Tribal/application-native-authorization]]
- [[Tribal/goja-execution-model]]
- [[Tribal/microvm-as-execution-boundary]]
- [[Tribal/dsl-normalized-config-compiled-plan]]
- [[Tribal/browser-side-processing-for-embedded]]
- [[Tribal/sql-as-first-class-command-source]]
- [[Tribal/host-mediated-secret-delivery]]
- [[Tribal/reduction-ladder-debugging]]
- [[Tribal/app-config-vs-command-config-separation]]
- [[Tribal/data-only-vs-host-access-module-split]]
- [[Tribal/iife-cell-rewrite]]
- [[Tribal/js-defined-glazed-commands]]
- [[Tribal/transcript-analysis-with-go-minitrace]]
- [[Tribal/geppetto-engine-config-vs-runtime-behavior]]
- [[Tribal/pi-extension-event-seams]]
- [[Tribal/canonical-doc-model-across-delivery-modes]]

### On-Ramp

The current on-ramp library contains the 19 entries in `Research/KB/On-Ramp/`, including the 8 user-requested below-threshold entries written during this campaign, [[On-Ramp/tree-sitter-for-go-tools]] from Batch 9, [[On-Ramp/js-to-wasm-compiler-architecture]], and [[On-Ramp/go-cli-with-embedded-spa]].

### Fundamentals

The current fundamentals library contains:
- [[Fundamentals/signal-quantization-and-sampling]]
- [[Fundamentals/access-control-models]]
- [[Fundamentals/encoding-and-framing]]
- [[Fundamentals/rendering-pipeline-fundamentals]]
- [[Fundamentals/host-mediated-sandbox-principles]]

---

## Cross-Reference: Which Projects Feed Which KB Entries

| KB Entry | Projects that feed it |
|----------|------------------------|
| Tribal/application-native-authorization | BYOK Host, Wish Git, Agent Enroll |
| Tribal/goja-execution-model | REPL API, Node-like Primitives, JS Discord Bot, Geppetto/Pinocchio, Loupedeck |
| Tribal/microvm-as-execution-boundary | Firecracker VM, pi-sandbox, PaperS3 WAMR |
| Tribal/dsl-normalized-config-compiled-plan | Screencast Studio, Almanach Studio |
| Tribal/browser-side-processing-for-embedded | SToMS3R, Cardputer Web Serial |
| Tribal/sql-as-first-class-command-source | Sqleton, Minitrace Query Commands |
| Tribal/host-mediated-secret-delivery | Firecracker VM, BYOK Host, Vault K3s, Glazed Vault, Terraform Vault |
| Tribal/reduction-ladder-debugging | PaperS3 WAMR, Cardputer smoke.html, Geppetto thinking bug |
| Tribal/app-config-vs-command-config-separation | Sqleton, BYOK Host, Glazed Vault |
| Tribal/data-only-vs-host-access-module-split | Node-like Primitives, Capsule Lab, goja-embedding |
| Tribal/iife-cell-rewrite | REPL API, Goja REPL Hardening, goja-execution-model |
| Tribal/js-defined-glazed-commands | jsverbs, JS Discord Bot jsverbs, go-minitrace PR #6 |
| Tribal/pi-extension-event-seams | Pi Hello World, Pi Extension Textbook, Session Summary, Agent Env, Response Capture, Compaction Meter, Compaction Title, Direnv Bash, Wafer model config |
| Tribal/canonical-doc-model-across-delivery-modes | Glazed Serve, Glazed Static Help Export, Codebase Browser embedded/static/SQLite line, Glazed Help Export |
| On-Ramp/crdts-and-local-first | AUTODISCO |
| On-Ramp/oauth-2-oidc-flows | BYOK Host, Wish Git, hosted Keycloak apps |
| On-Ramp/openssh-certificates | Wish Git |
| On-Ramp/dithering-and-rasterization | SToMS3R |
| On-Ramp/esc-pos-thermal-printer | SToMS3R |
| On-Ramp/e-ink-display-driving | Gnosis, Paper Pro, reMarkable cluster |
| On-Ramp/git-hooks-for-policy-enforcement | Wish Git |
| On-Ramp/wasm-from-go | Capsule Lab, JSON Flattener, Goja WASM Web REPL, VT100, Codebase Browser, SQLide Browser |
| On-Ramp/js-to-wasm-compiler-architecture | Generic Agent compiler experiment, GPT Base Principles compiler experiment |
| On-Ramp/esp-idf-console-repl-bring-up | SToMS3R, Wi-Fi Audio Cues Lab |
| On-Ramp/web-serial-browser-to-embedded | Cardputer Web Serial |
| On-Ramp/es8311-codec-bring-up-atoms3r | Wi-Fi Audio Cues Lab |
| On-Ramp/v6-rmdoc-scene-tree-rendering | Remarquee |
| On-Ramp/vault-on-k3s-with-vso | Vault on K3s, CoinVault |
| On-Ramp/browser-e2e-encryption-with-web-crypto | E2E Encrypted Storage |
| On-Ramp/automerge-keyhive-local-first-auth | AUTODISCO Keyhive |
| On-Ramp/what-is-a-stack-based-vm | Smalltalk-80 VM, uLisp PicoCalc, Gnosis VM |
| On-Ramp/tree-sitter-for-go-tools | Query Treesitter, Tree-sitter Templating, Sanitize structured text/YAML/JSON |
| On-Ramp/go-cli-with-embedded-spa | Glazed Serve, Glazed Static Help Export, Codebase Browser embedded/static line, Glazed Help Export |
| Fundamentals/signal-quantization-and-sampling | Dithering / ESC-POS / E-ink clusters |
| Fundamentals/access-control-models | OAuth / OpenSSH / application authorization cluster |
| Fundamentals/encoding-and-framing | ESC-POS / serial / line-protocol clusters |
| Fundamentals/rendering-pipeline-fundamentals | E-ink / retained-mode rendering clusters |
| Fundamentals/host-mediated-sandbox-principles | MicroVM boundary, data-only vs host-access module split, Wasm host/guest boundary, goja embedding |
