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

**On-Ramp candidates**: None new

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

**On-Ramp candidates**: None new

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

### 28. Glazed Secret Redaction and Vault Bootstrap

**Date**: 2026-04-02

**Summary**: Two-phase Glazed framework work: central secret redaction, then Vault source middleware with bootstrap parsing. Key insight: only TypeSecret fields eligible for Vault hydration.

**Repos**:
| Path | Notes |
|------|-------|
| `add-vault-middleware-to-glazed/glazed` | pkg/cmds/fields/sensitive.go, pkg/cmds/sources/vault.go |

**Tribal entries**: Contributes to **host-mediated secret delivery** (3/3 → READY), **app config vs command config** (3/3 → READY)

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
| **SQL as first-class command source** | Sqleton, Minitrace Query Commands | 3/3 → **READY** |
| **App config vs command config separation** | Sqleton, BYOK Host, Glazed Vault (bootstrap parsing) | 3/3 → **READY** |
| **MicroVM as execution boundary** | Firecracker VM, pi-sandbox, PaperS3 WAMR | 3/3 → CREATED |
| **Host-mediated secret delivery** | Firecracker VM, BYOK Host, Vault/Glazed/Terraform Vault | 3/3 → **READY** |
| **Three-layer credential separation** | Wish Git, Agent Enroll | 2/3 |
| **C99 native port for host testing** | uLisp PicoCalc | 1/3 |
| **TFT_eSPI patching for RP2040** | uLisp PicoCalc, (other display projects) | 2/3 |
| **Bring-up sequence discipline** | Wi-Fi Audio Cues Lab, SToMS3R | 2/3 |
| **Reduction-ladder debugging** | PaperS3 WAMR, Cardputer Web Serial (smoke.html) | 2/3 |
| **Bring-up sequence discipline** | Wi-Fi Audio Cues Lab, SToMS3R | 2/3 |
| **Spec-first VM implementation** | Smalltalk-80 VM (Blue Book), uLisp PicoCalc (from spec) | 2/3 |
| **Reduction-ladder debugging** | PaperS3 WAMR, Cardputer Web Serial (smoke.html) | 2/3 |
| **Buffer-full-body-before-UART** | SToMS3R, PaperS3 WAMR (buffer before load) | 2/3 |
| **NDJSON as wire protocol for embedded** | Cardputer Web Serial, SToMS3R | 2/3 |
| **Separate human auth (OIDC) from machine auth** | Vault on K3s, Terraform Vault | 2/3 |
| **Keycloak group-gated Vault access** | Vault on K3s, Terraform Vault | 2/3 |
| **Data-only vs host-access module split** | Node-like Primitives, Capsule Lab | 2/3 |
| **Runtime-scoped module registrars** | Plugins, Node-like Primitives | 2/3 |
| **Two-stage Glazed parsing for runtime config** | JS Discord Bot, (other Glazed apps?) | 2/3 |
| **JS-defined Glazed commands** | jsverbs, (Glazed help?) | 2/3 |
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
| **HashiCorp go-plugin for JS modules** | Plugins | 1/3 |
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
| **GStreamer for Go programmers** | Screencast Studio, (future media projects) | 2/5 🌐 Domain seed |
| **Arduino-cli cross-compilation** | uLisp PicoCalc, (other Arduino projects) | 2/5 🌐 Domain seed |
| **Obsidian CLI from Go** | ZK Tool | 1/5 |
| **ESM support in Go JS engines** | Goja vs Sobek | 1/5 🌐 Domain seed |

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
8. **goja Execution Model** — 5 projects (REPL API, Geppetto/Pinocchio, Loupedeck, Node-like Primitives, JS Discord Bot) ← **NEW**
9. **MicroVM as Execution Boundary** — 3 projects (Firecracker VM, pi-sandbox, PaperS3 WAMR) ← **NEW**
10. **DSL → Normalized Config → Compiled Plan** — 2 projects + implementer confirmation (Screencast Studio, Almanach Studio) ← **NEW**
11. **Browser-Side Processing for Embedded Devices** — 2 projects + implementer confirmation (SToMS3R, Cardputer Web Serial) ← **NEW**
12. **SQL as First-Class Command Source** — 2 projects + implementer confirmation (Sqleton, Minitrace Query Commands) ← **NEW**
13. **Host-Mediated Secret Delivery** — 3+ projects (Firecracker VM, BYOK Host, Vault K3s, Glazed Vault, Terraform Vault) ← **NEW**
14. **App Config vs Command Config Separation** — 3 projects (Sqleton, BYOK Host, Glazed Vault) ← **NEW**

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
| Tribal/goja-execution-model | REPL API, Node-like Primitives, JS Discord Bot, Geppetto/Pinocchio, Loupedeck |
| Tribal/microvm-as-execution-boundary | Firecracker VM, pi-sandbox, PaperS3 WAMR |
| Tribal/dsl-normalized-config-compiled-plan | Screencast Studio, Almanach Studio |
| Tribal/browser-side-processing-for-embedded | SToMS3R, Cardputer Web Serial |
| Tribal/sql-as-first-class-command-source | Sqleton, Minitrace Query Commands |
| Tribal/host-mediated-secret-delivery | Firecracker VM, BYOK Host, Vault K3s, Glazed Vault, Terraform Vault |
| Tribal/app-config-vs-command-config-separation | Sqleton, BYOK Host, Glazed Vault |
