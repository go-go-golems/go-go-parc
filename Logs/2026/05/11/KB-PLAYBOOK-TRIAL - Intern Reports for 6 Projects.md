---
Title: ""
Ticket: ""
Status: ""
Topics: []
DocType: ""
Intent: ""
Owners: []
RelatedFiles:
    - Path: ../../../../../../../go-go-golems/go-go-parc/Projects/2026/03/15/PROJ - ZK Tool.md
      Note: Project 1 analyzed
    - Path: ../../../../../../../go-go-golems/go-go-parc/Projects/2026/04/02/PROJ - Sqleton SQL Command Cleanup - Technical Project Report.md
      Note: Project 2 analyzed
    - Path: ../../../../../../../go-go-golems/go-go-parc/Projects/2026/04/13/PROJ - Screencast Studio - GStreamer Migration and Media Runtime Intern Guide.md
      Note: Project 5 analyzed
    - Path: ../../../../../../../go-go-golems/go-go-parc/Projects/2026/05/03/PROJ - Agent Enroll - Kanban Agent Credential MVP Deep Dive.md
      Note: Project 6 analyzed
    - Path: ../../../../../../../go-go-golems/go-go-parc/Projects/2026/05/05/PROJ - uLisp PicoCalc - From Cross-Compilation to a Lisp Machine in Your Hand.md
      Note: Project 4 analyzed
    - Path: ../../../../../../../go-go-golems/go-go-parc/Research/playbooks/building-knowledge-base.md
      Note: The playbook being tested
    - Path: and Isolation Design.md
      Note: Project 3 analyzed
ExternalSources: []
Summary: ""
LastUpdated: 0001-01-01T00:00:00Z
WhatFor: ""
WhenToUse: ""
---


# KB Playbook Trial: Intern Reports for 6 Projects

This document follows the playbook Steps 1–5 for each of the six assigned projects: ZK Tool, Sqleton SQL Command Cleanup, Firecracker VM, uLisp PicoCalc, Screencast Studio, and Agent Enroll.

After the per-project sections, there is a combined candidate tracking list update (Step 5) and a playbook feedback section.

---

# Project 1: ZK Tool (Easy)

## Step 1: Concept Extraction

| Concept | Category | Role in the project | Tribal? |
|---------|----------|---------------------|---------|
| Goja JS runtime embedding | Technology | Running JavaScript locally inside a Go CLI | Yes — our specific goja embedding pattern |
| `require("obsidian")` native module | Pattern | Go-to-JS bridge for Obsidian CLI access | Yes — our native module pattern |
| Obsidian CLI (`obsidian` binary) | Technology | Local Obsidian app interaction | No — Obsidian publishes a CLI API |
| Zettelkasten filing workflow | Pattern | Classify and route notes into a vault structure | Partially — Luhmann codes are public knowledge, but our routing logic is ours |
| Luhmann-style branching codes | Technology | The coding system for ZK claims (2a0a1...) | No — public knowledge from Niklas Luhmann's system |
| Glazed command framework | Technology | CLI structure, help pages, command registration | Partially — Glazed is our framework, but documented internally |
| ZK note routing / branch suggestion | Pattern | Determining where a new note should go | Yes — our specific routing logic (not yet implemented) |
| Vault structure conventions | Pattern | Parallel knowledge areas (ZK/, Wiki/, Notes/, Inbox/) | Partially — our specific vault layout, but the concept of parallel areas is universal |

## Step 2: Classification

| Concept | Decision | Reason |
|---------|----------|--------|
| Goja JS runtime embedding | Tribal entry **EXISTS** | Already documented as `[[Tribal/goja-embedding-in-go]]`. This project uses the same pattern. |
| `require("obsidian")` native module | Tribal candidate (2/3) | Our pattern for exposing Go APIs as JS modules. Seen in goja-embedding (generic), ZK Tool (Obsidian-specific). The existing goja tribal covers the generic embedding; this is about a specific native module pattern. Consider whether this is a variation of goja-embedding or its own pattern. |
| Obsidian CLI | On-Ramp candidate (1/5) | Lookupable (Obsidian publishes docs), but our angle (calling it from Go via JS) is unique. Too few projects depend on it yet. |
| Zettelkasten filing workflow | Tribal candidate (1/3) | Our routing logic (not just generic ZK). Only ZK Tool uses it so far. |
| Luhmann-style branching codes | On-Ramp candidate (1/5) | Public knowledge, but the specific format rules and our conventions could use a short orientation. Only ZK Tool depends on it. |
| Glazed command framework | Tribal candidate — **ALREADY COUNTED** | Glazed is used in 50+ projects. The goja tribal entry references it. Not a new candidate. |
| ZK note routing / branch suggestion | Tribal candidate (1/3) | Our specific pattern, not yet implemented. |
| Vault structure conventions | Tribal candidate (1/3) | Our vault's layout is our convention. |

### Key question answer: Does the Go+JS pattern overlap with our goja tribal entry?

**It overlaps but extends.** The goja-embedding-in-go tribal entry documents the generic pattern: embed goja, create a runtime, expose Go functions as JS. ZK Tool follows that exact pattern. However, ZK Tool adds two things that go beyond the generic entry:

1. **Native `require("obsidian")` module**: A domain-specific Go→JS bridge that wraps the Obsidian CLI. This is the "native module" pattern mentioned briefly in the goja entry but not documented as its own pattern. It's similar to how `require("fs")` or `require("http")` works in Node — the Go side registers a module factory, the JS side imports it.

2. **Read-first workflow discipline**: The project enforces a working rule of "prefer proving behavior with read-only scripts first." This is a pattern for safe development against live systems, not specific to goja.

My conclusion: the Go+JS runtime part is covered by the existing goja tribal entry. The native module registration pattern could become a variation or a separate tribal candidate once more projects use it. Right now it's at 2/3 (goja-embedding uses generic module registration; ZK Tool uses Obsidian-specific; Loupedeck uses hardware-specific modules).

## Step 3: KB Entries Ready to Create

**None.** All tribal candidates are below the 3-project threshold. All on-ramp candidates are below the 5-project threshold. The existing goja-embedding tribal entry already covers the core pattern.

## Step 4: Cross-References

The ZK Tool project report should add:

```markdown
## Related KB entries

- [[Tribal/goja-embedding-in-go]] — the Go+JS runtime pattern used here
- Candidate: [[Tribal/goja-native-module-registration]] (2/3) — the `require("obsidian")` pattern
- Candidate: [[Tribal/zk-note-routing-logic]] (1/3) — our specific vault filing workflow
```

The goja-embedding tribal entry should add ZK Tool to its Related PARC project reports:
```markdown
- [[PROJ - ZK Tool]] — goja + Obsidian CLI native module pattern
```

---

# Project 2: Sqleton SQL Command Cleanup (Easy)

## Step 1: Concept Extraction

| Concept | Category | Role in the project | Tribal? |
|---------|----------|---------------------|---------|
| SQL as first-class command source | Pattern | `.sql` files define commands, not YAML wrappers | Yes — our specific design in the Glazed ecosystem |
| SqlCommandSpec as compilation seam | Pattern | Neutral intermediate representation between parsing and execution | Yes — our design pattern |
| App config vs command config separation | Pattern | `repositories:` is app-level; `sql-connection:` is command-level | Yes — our specific pain point and solution |
| SQL command preamble format | Pattern | YAML metadata block inside `.sql` files | Yes — our format convention |
| Glazed CLI framework | Technology | Command parsing, Cobra integration, config middleware | Partially — our framework |
| SQLite as application database | Technology | Runtime testing against real SQLite DBs | Covered by existing tribal entry |
| Viper removal / explicit config loading | Pattern | Replacing implicit config magic with explicit ownership | Yes — our pattern, though this is more of a lesson than a reusable pattern |
| Repository-based command discovery | Pattern | Finding commands in directories/repositories | Partially — shared with Glazed ecosystem |

## Step 2: Classification

| Concept | Decision | Reason |
|---------|----------|--------|
| SQL as first-class command source | Tribal candidate (2/3) | Our pattern for the Glazed ecosystem. Seen in Sqleton, Minitrace Query Commands. One more SQL-backed tool triggers it. |
| SqlCommandSpec compilation seam | Tribal candidate (1/3) | Our specific design in sqleton. The idea of a neutral spec stage is generic, but our specific implementation is ours. |
| App config vs command config separation | Tribal candidate (2/3) | Our specific pain point and resolution. Sqleton and (potentially) other Glazed apps have hit this. The BYOK Host also separates app vs command config. |
| SQL command preamble format | Tribal candidate (1/3) | Our specific format. Only Sqleton uses it currently. |
| Viper removal / explicit config loading | Tribal candidate (2/3) | The pattern of removing implicit Viper usage. Sqleton did it; other Glazed apps likely need it. |

### Key question answer: Is "SQL commands via Glazed CLI" a new tribal pattern, or just combining two existing ones?

**It is a new tribal pattern.** The combination of SQL + Glazed CLI is more than the sum of its parts. The key insight is that SQL files become *command definitions* with metadata preambles, not just queries that happen to be invoked from a CLI. The `SqlCommandSpec` compilation seam — parsing SQL + metadata into a neutral spec, then compiling that spec into a Cobra command — is a genuine design pattern that doesn't exist in either SQL or Glazed independently.

However, it doesn't hit the 3-project threshold yet. Sqleton and Minitrace Query Commands are the only two instances I can find. This is a "2/3 tribal candidate" — it needs one more SQL-backed Glazed command system to trigger.

## Step 3: KB Entries Ready to Create

**None.** All tribal candidates are below threshold. The existing `[[Tribal/sqlite-as-application-database]]` entry covers SQLite usage but not the SQL-as-command-definition pattern.

## Step 4: Cross-References

The Sqleton project report should add:

```markdown
## Related KB entries

- [[Tribal/sqlite-as-application-database]] — SQLite as the runtime database for SQL commands
- Candidate: [[Tribal/sql-as-first-class-command-source]] (2/3) — SQL files define Glazed commands
- Candidate: [[Tribal/app-config-vs-command-config-separation]] (2/3) — explicit config ownership in Glazed apps
```

The SQLite tribal entry should add Sqleton to its Related PARC project reports:
```markdown
- [[PROJ - Sqleton SQL Command Cleanup - Technical Project Report]] — SQL command loader with SQLite smoke tests
```

---

# Project 3: Firecracker VM (Medium)

## Step 1: Concept Extraction

| Concept | Category | Role in the project | Tribal? |
|---------|----------|---------------------|---------|
| MicroVM as execution boundary | Pattern | One Firecracker VM per job, not shared process state | Partially — Firecracker is public, but our "one VM per agent run" pattern is ours |
| Host-mediated secret delivery | Pattern | Vault on host, secrets materialized in guest via vsock | Yes — our specific design, not documented anywhere |
| Ext4 workspace as boundary artifact | Pattern | Host files → staged tree → ext4 image → guest mount → retained output | Yes — our deliberate choice over bind mounts |
| Guest bootstrap daemon (bootstrapd) | Pattern | Minimal guest-side coordinator: vsock listener, mount, secrets, exec | Yes — our design |
| Rootfs + tooling disk model | Pattern | Immutable rootfs, read-only tooling, mutable workspace | Yes — our filesystem contract |
| Firecracker API / configuration | Technology | Launching and configuring microVMs | No — AWS documents the Firecracker API |
| vsock communication | Technology | Host↔guest channel for bootstrap request and streaming logs | No — public Linux feature |
| Vault secret injection | Technology | Reading secrets from Vault and materializing them as files | Partially — Vault is public, but host-mediated injection is ours |
| SELinux for guest confinement | Technology | Mandatory access control inside the guest | No — public Linux security feature |
| Explicit resource model | Pattern | Explicit kernel, rootfs, drives, vsock — no implicit sharing | Yes — our design principle |

## Step 2: Classification

| Concept | Decision | Reason |
|---------|----------|--------|
| MicroVM as execution boundary | Tribal candidate (2/3) | Our pattern. Seen in Firecracker VM and pi-sandbox. Capsule Lab uses WASM instead, which is a different approach (see key question). |
| Host-mediated secret delivery | Tribal candidate (2/3) | Our specific design. Firecracker VM uses it; BYOK Host uses a related pattern (host holds credentials, guest never sees them). One more project and it triggers. |
| Ext4 workspace as boundary artifact | Tribal candidate (1/3) | Only Firecracker VM uses this. Containers typically use bind mounts. |
| Guest bootstrap daemon pattern | Tribal candidate (1/3) | Only Firecracker VM currently. The idea of a minimal init-time coordinator is generic, but our specific design is ours. |
| Rootfs + tooling disk + workspace model | Tribal candidate (1/3) | Only Firecracker VM. The multi-disk contract hasn't been implemented yet. |
| Vault secret injection (host-mediated) | Tribal candidate — **DUPLICATE** with "host-mediated secret delivery" above. Same concept. |
| Explicit resource model | Tribal candidate (1/3) | A design principle, not a code pattern. Worth noting but may not make a good tribal entry on its own. |

### Key question answer: Do the sandboxing patterns overlap with Capsule Lab?

**No — they are fundamentally different approaches to the same problem.** Both projects create isolated execution environments, but the mechanisms are entirely different:

| Aspect | Capsule Lab | Firecracker VM |
|--------|-------------|-----------------|
| Boundary | goja interpreter in WASM | Linux microVM (hardware virtualization) |
| Attack surface | JS interpreter API surface | Full Linux kernel syscall surface |
| Resource model | Browser memory + CPU | Dedicated kernel, rootfs, drives |
| Secret handling | Host-mediated op-stream | Host-mediated vsock + `/run/secrets` |
| Output | Ops array back to host | Retained ext4 workspace image |
| Network | None (browser sandbox) | Optional, configurable |
| Tooling | What goja supports | Full Linux toolchain on tooling disk |

The common thread is the *principle* of host-mediated, explicit-boundary sandboxing. But the implementations share no code and no architecture. If a "host-mediated sandbox patterns" fundamental entry existed, both could link to it. Right now, that fundamental candidate would need to support 2+ KB entries — and both the WASM tribal and the Firecracker tribal would qualify if they existed. So this is a **fundamental candidate** at 1/2.

**What overlaps:** The design *principle* of "host prepares sealed inputs, guest consumes them, output comes back as artifact." Both projects follow this. The *mechanism* is different.

## Step 3: KB Entries Ready to Create

**None.** All tribal candidates are below the 3-project threshold. The Firecracker-specific concepts (host-mediated secrets, ext4 workspace, bootstrapd) are each at 1–2 projects.

The existing `[[Fundamentals/access-control-models]]` entry is relevant — the "host mediates what the guest sees" pattern is a delegation model. Firecracker VM's host-mediated secret delivery is a concrete instance of controlled delegation. The existing entry should be cross-referenced.

## Step 4: Cross-References

The Firecracker VM project report should add:

```markdown
## Related KB entries

- [[Fundamentals/access-control-models]] — the delegation model behind host-mediated secret delivery
- Candidate: [[Tribal/microvm-as-execution-boundary]] (2/3) — one VM per agent run
- Candidate: [[Tribal/host-mediated-secret-delivery]] (2/3) — secrets materialized from host, not guest-side Vault
- Candidate: [[Tribal/explicit-resource-model-for-sandboxed-runtimes]] (1/3) — no implicit sharing, everything is an explicit image/drive/channel
- Candidate: [[Fundamentals/host-mediated-sandbox-principles]] (1/2) — the design principle shared with Capsule Lab's WASM sandbox
```

The access-control-models fundamental entry should add:
```markdown
- [[PROJ - Firecracker VM - Guest Bring-Up, Host-Mediated Secrets, and Isolation Design]] — host-mediated delegation of secrets to a sandboxed guest
```

---

# Project 4: uLisp PicoCalc (Medium)

## Step 1: Concept Extraction

| Concept | Category | Role in the project | Tribal? |
|---------|----------|---------------------|---------|
| Arduino-cli cross-compilation | Technology | Building RP2040 firmware from the command line | No — Arduino publishes the toolchain, but our specific workflow (CLI-only, no IDE) is ours |
| RP2040 / Pico SDK | Technology | The target platform (dual-core ARM M0+) | No — Raspberry Pi documents it |
| ILI9488 display driver | Technology | SPI-driven 320×320 color display | No — display controller is documented |
| I2C keyboard scanner (STM32) | Technology | External MCU scanning keys, exposed over I2C | No — hardware design is in the PicoCalc repo |
| C99 native port for host testing | Pattern | Cross-compile a native REPL for fast host-side iteration | Yes — our specific workflow of "test on host, deploy to target" |
| CLion configuration for Arduino | Pattern | Generate c_cpp_properties.json from compile_commands.json + @file expansion | Yes — our tooling workaround, nobody else documents this |
| Forward-declaration extraction | Pattern | Reducing Arduino's 462 injected prototypes to 36 actually-needed ones | Yes — our specific optimization |
| Source index for monolith navigation | Pattern | Annotating a 7,793-line .ino into a 1,000-line indexed reference | Yes — our documentation pattern |
| TFT_eSPI library patching | Pattern | Two-file configuration for specific hardware (User_Setups + Setup_Select) | Partially — TFT_eSPI is public, but the "blank screen with no error" gotcha is ours |
| I2C address routing quirk | Pattern | Addresses ≥ 128 route to Wire1; keyboard must use `#x9F` not `#x1F` | Yes — discovered by reading source, not documented anywhere |
| Dangerous register (0x08 RST) | Pattern | Reading keyboard reset register crashes the I2C bus | Yes — our hard-won knowledge |
| ESP-IDF firmware patterns | Technology | Console, web UI, OTA | Covered by existing tribal entry? **No** — this project uses Arduino, not ESP-IDF |

## Step 2: Classification

| Concept | Decision | Reason |
|---------|----------|--------|
| C99 native port for host testing | Tribal candidate (2/3) | Our pattern. uLisp PicoCalc uses it; Smalltalk-80 VM has a similar "test on host" workflow. One more project with cross-compile + native REPL triggers it. |
| CLion configuration for Arduino | Tribal candidate (1/3) | Only uLisp PicoCalc uses this workaround. The script is generic enough to help other Arduino projects, but there's only one instance. |
| Forward-declaration extraction | Tribal candidate (1/3) | Only uLisp PicoCalc. Generic idea but specific implementation. |
| Source index for monolith navigation | Tribal candidate (1/3) | Only uLisp PicoCalc. A documentation pattern, not a code pattern. |
| TFT_eSPI library patching | Tribal candidate (2/3) | Any RP2040 + TFT_eSPI project hits this. Seen in uLisp PicoCalc and potentially in other display projects. The "blank screen with no error" gotcha is the key scar tissue. |
| I2C address routing quirk (≥128 → Wire1) | Tribal candidate (1/3) | uLisp-specific quirk. Not even other PicoCalc firmware might hit it. |
| Dangerous register gotcha | Tribal candidate (1/3) | uLisp PicoCalc-specific. Hardware-specific scar tissue. |
| Arduino-cli cross-compilation workflow | On-Ramp candidate (2/5) | Lookupable (Arduino docs exist), but our angle (CLI-only, no IDE, headless build scripts) is underserved. Too few projects. |

### Key question answer: Does uLisp follow the same architecture as ESP-IDF patterns?

**No — it deviates significantly.** The existing `[[Tribal/esp-idf-firmware-patterns]]` entry documents the `esp_console` + web UI + IDF component architecture. uLisp PicoCalc uses a completely different stack:

| Aspect | ESP-IDF tribal pattern | uLisp PicoCalc |
|--------|----------------------|----------------|
| Build system | CMake + ESP-IDF `idf.py` | `arduino-cli compile` (Arduino builder) |
| Console | `esp_console` component | uLisp REPL over USB serial |
| Display | LVGL or custom | TFT_eSPI + uLisp graphics primitives |
| Language | C/C++ | uLisp (Lisp interpreter in C++) |
| OTA | IDF OTA partition scheme | UF2 bootloader drag-and-drop |
| Framework | ESP-IDF (full RTOS) | Arduino-Pico core (FreeRTOS underneath, but Arduino API surface) |

The only overlap is the hardware: RP2040 is ARM Cortex-M0+ like some ESP32 variants. But the entire software stack is different. uLisp PicoCalc is *not* an instance of the ESP-IDF firmware pattern. It's a different approach to embedded firmware.

However, some tribal *candidates* overlap:
- The "test on host, deploy to target" workflow exists in both (ESP-IDF has `idf.py monitor`; uLisp has native C99 REPL)
- The "dangerous register gotcha" pattern exists in both ecosystems (ESP-IDF has peripheral-specific crash modes; uLisp has I2C register 0x08)
- The "library patching" pattern exists in both (ESP-IDF has Kconfig; Arduino has User_Setups)

These are at the level of *principles*, not code patterns. They don't warrant a shared tribal entry yet.

## Step 3: KB Entries Ready to Create

**None.** All tribal candidates are below threshold.

However, this project surfaces something the existing KB doesn't cover: **Arduino-cli as an alternative firmware build path**. The ESP-IDF tribal entry covers our CMake/IDF approach. When more projects use Arduino-cli (or PlatformIO, or Pico SDK directly), an "embedded firmware build workflows" tribal entry or on-ramp entry may be warranted. Right now it's premature.

## Step 4: Cross-References

The uLisp PicoCalc project report should add:

```markdown
## Related KB entries

- [[Tribal/esp-idf-firmware-patterns]] — the *other* firmware architecture we use (not this one; this project uses Arduino-cli)
- Candidate: [[Tribal/c99-native-port-for-host-testing]] (2/3) — compile a host-side REPL for fast iteration
- Candidate: [[Tribal/tft-espi-patching-for-rp2040]] (2/3) — the two-file configuration dance with blank-screen gotcha
- Candidate: [[On-Ramp/arduino-cli-cross-compilation]] (2/5) — headless Arduino builds from the command line
```

The ESP-IDF tribal entry should add a note that uLisp PicoCalc deliberately uses a different approach:
```markdown
- [[PROJ - uLisp PicoCalc - From Cross-Compilation to a Lisp Machine in Your Hand]] — uses Arduino-cli, not ESP-IDF; a contrasting firmware build path
```

---

# Project 5: Screencast Studio (Hard)

## Step 1: Concept Extraction

| Concept | Category | Role in the project | Tribal? |
|---------|----------|---------------------|---------|
| GStreamer pipeline construction from Go | Pattern | Building native media pipelines using go-gst bindings | Yes — our specific Go+GStreamer integration |
| GStreamer pipeline lifecycle (state transitions, EOS, bus) | Technology | How GStreamer pipelines start, run, and stop | No — GStreamer documentation exists, but our specific shutdown/EOS patterns are ours |
| FFmpeg subprocess management | Technology | Launching and supervising FFmpeg processes | No — FFmpeg docs exist, but our state machine for signal escalation is ours |
| DSL → normalized config → compiled plan | Pattern | User description → runtime plan, media-engine-independent | Yes — our architecture pattern |
| Preview vs recording lifecycle | Pattern | Live pipeline (low latency) vs file pipeline (correct finalization) | Partially — public concept, but our specific separation is ours |
| Runtime seam (interface-based engine swap) | Pattern | PreviewRuntime/RecordingRuntime interfaces behind which FFmpeg and GStreamer coexist | Yes — our migration pattern |
| appsink delivery into Go | Pattern | Getting pixel/audio data from GStreamer into Go callbacks | Yes — our specific bridge |
| EOS-driven file finalization | Pattern | Send EOS, wait for bus EOS, then NULL — not just kill | Partially — public GStreamer knowledge, but the "don't skip this" gotcha is ours |
| Container vs codec distinction | Technology | H.264 vs MP4, Opus vs Ogg | No — public media knowledge |
| GLib main loop coexistence with Go | Pattern | Running enough GLib for GStreamer bus handling inside a Go server | Yes — our specific threading/event-loop challenge |
| audiomixer request-pad API | Technology | Dynamic input pad creation for audio mixing | No — GStreamer docs |
| Media DSL / domain model | Pattern | Describing recording setups declaratively | Yes — our domain-specific language |

## Step 2: Classification

| Concept | Decision | Reason |
|---------|----------|--------|
| GStreamer pipeline construction from Go | Tribal candidate (1/3) | Only Screencast Studio uses Go+GStreamer. This opens a completely new KB domain. |
| DSL → normalized config → compiled plan | Tribal candidate (2/3) | Screencast Studio and (potentially) Almanach Studio follow this pattern. One more declarative-pipeline project triggers it. |
| Runtime seam for engine migration | Tribal candidate (1/3) | Only Screencast Studio has this explicit interface-based swap pattern. The idea is generic, but our implementation is ours. |
| appsink delivery into Go | Tribal candidate (1/3) | Only Screencast Studio. The go-gst bridge pattern. |
| GLib main loop coexistence with Go | Tribal candidate (1/3) | Only Screencast Studio. A nasty gotcha when mixing GLib and Go runtimes. |
| Preview vs recording lifecycle | On-Ramp candidate (1/5) | Public knowledge (live vs file pipelines), but our angle (the specific gotchas of EOS, muxer drain, stop semantics) is valuable. Too few projects. |
| EOS-driven file finalization | On-Ramp candidate (1/5) | Public GStreamer knowledge, but the "killing instead of finalizing" gotcha is common enough that it could become an on-ramp entry if we had more media projects. |
| Container vs codec distinction | On-Ramp candidate (1/5) | Public knowledge, well-documented. Our angle is minimal. Probably not worth an entry. |
| GStreamer concepts (elements, pads, caps, bus) | On-Ramp candidate (2/5) | GStreamer docs exist but are scattered and overwhelming for newcomers. Our angle (the 10-minute orientation for someone who needs to read our media code) could be valuable. Screencast Studio and any future GStreamer project would depend on it. |

### Key question answer: Are GStreamer pipeline patterns tribal or on-ramp?

**Mostly on-ramp, with one tribal candidate.** Here's the split:

- **On-ramp**: The GStreamer concepts themselves (elements, pads, caps, bus, state transitions, EOS, pipeline construction). These are lookupable — GStreamer documentation exists. But our angle (the specific 10-minute orientation for someone reading our Go media code, with our specific pipeline shapes and our specific gotchas) is missing from public docs. An on-ramp entry like "GStreamer for Go Programmers" would serve future projects that need media capabilities.

- **Tribal candidate**: Our Go+GStreamer integration pattern (go-gst bindings, appsink delivery, GLib main loop coexistence, bus watch handling). This is our-specific knowledge. Nobody else documents how to embed GStreamer in a Go server with a GLib main loop coexistence story. But it's at 1/3 — only Screencast Studio uses it.

The pipeline shapes themselves (ximagesrc → videoconvert → videoscale → jpegenc → appsink for preview; ximagesrc → videoconvert → x264enc → mp4mux → filesink for recording) are *our specific pipeline designs*. They're closer to tribal knowledge than on-ramp — you won't find our exact pipeline topologies in GStreamer tutorials. But they're probably too specific to be a standalone entry; they'd be part of a "GStreamer in Go" tribal or on-ramp entry.

**This project opens a new KB domain (media).** The question isn't whether GStreamer patterns are tribal or on-ramp — it's whether we'll have enough media projects to justify any entry at all. Right now, with only Screencast Studio, we don't hit any threshold. But if we add transcription, audio processing, or video editing projects, the GStreamer on-ramp entry becomes valuable.

## Step 3: KB Entries Ready to Create

**None.** All candidates are below threshold. The media domain is too new to our library.

However, I want to flag something: the **GStreamer concepts** on-ramp candidate at 2/5 is close to being worth writing even below threshold, because it opens a new domain. The playbook says "let project reports drive the KB" and "don't create entries preemptively." But this domain has zero coverage, and an intern reading the Screencast Studio report will get stuck on GStreamer fundamentals. I'd argue this is exactly the scenario where an on-ramp entry is most valuable — it's the kind of entry that makes a project report readable. I'll note this in the playbook feedback.

## Step 4: Cross-References

The Screencast Studio project report should add:

```markdown
## Related KB entries

- [[Tribal/goja-embedding-in-go]] — the JS runtime pattern (not directly used here, but the runtime seam pattern is analogous)
- Candidate: [[Tribal/gstreamer-pipeline-construction-from-go]] (1/3) — Go+GStreamer integration pattern
- Candidate: [[Tribal/runtime-seam-for-engine-migration]] (1/3) — interface-based engine swap
- Candidate: [[On-Ramp/gstreamer-for-go-programmers]] (2/5) — GStreamer elements, pads, caps, bus, lifecycle
```

---

# Project 6: Agent Enroll (Hard)

## Step 1: Concept Extraction

| Concept | Category | Role in the project | Tribal? |
|---------|----------|---------------------|---------|
| Three-layer credential separation | Pattern | Human token → agent key → run token, each narrower than the last | Yes — our specific security architecture |
| Agent enrollment with Ed25519 keypair | Pattern | Agent generates key locally, sends only public key | Yes — our specific enrollment flow |
| Canonical request signing | Pattern | METHOD + PATH + SHA256(body) + TIMESTAMP + NONCE | Yes — our specific signing format |
| Run token as scoped, short-lived bearer token | Pattern | Opaque token, hash-only storage, task/run binding | Yes — our specific authorization mechanism |
| Guarded task update (race-safe claim) | Pattern | SQL UPDATE with WHERE conditions, check row count | Partially — standard SQL technique, but our specific application is ours |
| Keycloak JWT/JWKS validation (local) | Technology | Validate tokens without calling Keycloak per request | Covered by existing tribal entry |
| SQLite as security-relevant storage | Pattern | WAL mode, hash-only token storage, transactional claims | Partially — SQLite tribal covers app usage; this is security-specific |
| Enrollment token (one-time, hash-only) | Pattern | Short-lived, hash-stored, single-use enrollment secret | Yes — our specific design |
| Rate limiting by identity plane | Pattern | IP for anonymous, user for human, agent for signed, run for scoped | Yes — our specific rate-limiting strategy |
| Audit logging as evidence | Pattern | Append-only event log for security-relevant operations | Partially — standard practice, but our specific events are ours |
| Application-native authorization (not Keycloak) | Pattern | Keycloak authenticates humans; Go API owns agent/run/task authorization | Yes — our specific separation decision |

## Step 2: Classification

| Concept | Decision | Reason |
|---------|----------|--------|
| Three-layer credential separation | Tribal candidate (2/3) | Agent Enroll and Wish Git both use a multi-credential architecture. Wish Git has 3 credentials (Keycloak → OAuth → SSH cert); Agent Enroll has 3 (Keycloak → agent key → run token). The pattern is the same: authority narrows from human to agent to run. One more project triggers it. |
| Agent enrollment with Ed25519 keypair | Tribal candidate (1/3) | Only Agent Enroll. Wish Git uses SSH keypairs instead. |
| Canonical request signing | Tribal candidate (1/3) | Only Agent Enroll. Our specific canonical format. |
| Run token as scoped bearer token | Tribal candidate (1/3) | Only Agent Enroll. Wish Git uses SSH certificates for scope. |
| Enrollment token (one-time, hash-only) | Tribal candidate (1/3) | Only Agent Enroll. |
| Guarded task update (race-safe claim) | Tribal candidate (2/3) | Agent Enroll uses it; Wish Git uses guarded git operations. The pattern of "optimistic lock with row count check" is standard SQL, but our application of it to agent task claiming is ours. |
| Rate limiting by identity plane | Tribal candidate (1/3) | Only Agent Enroll. |
| Application-native authorization | Tribal candidate (3/3) → **READY** | Three projects: BYOK Host (broker-not-proxy), Wish Git (SSH cert + pre-receive), Agent Enroll (agent key + run token). All three separate Keycloak authn from application authz. This is a pattern. |
| SQLite as security-relevant storage | Tribal candidate (2/3) — overlaps with existing [[Tribal/sqlite-as-application-database]] | The existing entry covers general SQLite usage. Agent Enroll uses SQLite for security-specific patterns (hash-only storage, transactional claims, WAL + backup). This could be a variation in the existing entry rather than a new one. |

### Key question answer: Does the existing Wish Git KB help you read this, or is something missing?

**The existing KB almost covers it, but there's a gap.** Here's what the KB already provides:

- `[[Tribal/keycloak-oauth-in-go-services]]` — ✅ Covers the Keycloak JWT/JWKS validation that both projects use.
- `[[On-Ramp/oauth-2-oidc-flows]]` — ✅ Covers the OAuth browser flow that humans use to authenticate.
- `[[On-Ramp/openssh-certificates]]` — ✅ Covers Wish Git's SSH certificate approach. Agent Enroll *doesn't* use SSH certificates, so this isn't directly relevant, but the delegation model is the same.
- `[[Fundamentals/access-control-models]]` — ✅ Covers authn/authz/delegation, which is the core model.
- `[[On-Ramp/git-hooks-for-policy-enforcement]]` — ⚠️ Wish Git-specific, not relevant to Agent Enroll.

**What's missing:**

1. **Application-native authorization for agents** — Neither the Keycloak tribal nor the OAuth on-ramp covers the pattern of "Keycloak authenticates humans, but the Go application owns agent and run authorization." The existing entries assume the credential chain ends at the service. In Agent Enroll, it continues: human → agent → run. This is the "application-native authorization" tribal candidate at 3/3.

2. **Ed25519 request signing for agent authentication** — The SSH certificates on-ramp covers one way to do agent authentication (SSH cert with scope). Agent Enroll uses a different method (Ed25519 signatures on canonical requests). There's no KB entry that explains this alternative. It's at 1/3, so it's not ready, but it's a gap.

3. **Opaque bearer tokens vs signed certificates** — The conceptual tradeoff between opaque tokens (Agent Enroll) and cryptographic certificates (Wish Git) is not documented. An intern reading Agent Enroll after Wish Git might ask "why not use SSH certificates here too?" The answer is that Agent Enroll's operations are HTTP API calls, not SSH sessions — SSH certificates don't map well to HTTP bearer tokens. This is the kind of on-ramp orientation that would help.

**Bottom line:** The existing KB covers the *human authentication* layer well. It does not cover the *agent and run authorization* layer that sits below it. The "application-native authorization" tribal entry would fill this gap.

## Step 3: KB Entries Ready to Create

**One entry is ready:** Application-native authorization (3/3 tribal).

| Concept | Section | Reason |
|---------|---------|--------|
| Application-native authorization: Keycloak authenticates humans, the Go app owns agent/run/task authz | Tribal | 3 projects: BYOK Host, Wish Git, Agent Enroll |

However, I need to be honest: this is the *first time* I'm analyzing these projects for KB extraction. The existing project index (Batch 1) didn't include Agent Enroll. The count of 3/3 includes projects from both Batch 1 and this trial. Let me verify:

- BYOK Host: "Keycloak authenticates the user; the broker decides what the user's stored provider connection may be used for." ✅
- Wish Git: "Three-credential separation — user credential → broker credential → agent credential. Keycloak does authentication; the forge makes authorization decisions." ✅
- Agent Enroll: "Keycloak is already good at human identity, but the agent workflow needs application-native authority." ✅

Yes, three projects. This tribal entry is ready.

I am **not going to write the full entry** in this report because the playbook warns: "If you're writing an entry about something you learned while reading the project report, you're probably the wrong person to write it. The scar-tissue sections require real scars." I don't have implementation experience with these projects. I'll note it as ready-to-create and provide a draft skeleton, but it needs review by someone who has built this pattern in at least two projects.

### Draft skeleton for Application-Native Authorization tribal entry

```markdown
---
title: "Application-Native Authorization — How We Do It"
aliases: [app-native authz, keycloak plus local auth, agent authorization]
tags: [knowledge-base, tribal, authorization, agents, keycloak]
status: draft
type: knowledge-base
created: 2026-05-11
---

# Application-Native Authorization — How We Do It

> [!summary]
> Keycloak authenticates humans; the Go application owns agent, run, and task authorization. This separation is the core pattern for any system where autonomous agents operate under delegated human authority.

## The pattern

[To be written by someone with implementation experience]

## Why we do it this way

Keycloak is excellent at human identity: browser redirect, PKCE, token validation, realm management. But Keycloak does not know about agents, runs, tasks, boards, or scoped delegations. Modeling these in Keycloak roles creates coupling that makes permissions hard to audit and impossible to test locally.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `byok-host` | `internal/auth/` | Broker authorization after Keycloak authn |
| `wish-git` | `internal/forge/` | SSH cert issuance + pre-receive enforcement |
| `agent-enroll` | `internal/agent/`, `internal/runs/` | Agent enrollment + run-token authz |

### Related PARC project reports

- [[PROJ - BYOK Host - Project Report]] — broker-not-proxy architecture
- [[PROJ - Wish Git - OAuth Scoped Git over SSH for Coding Agents]] — three-credential separation
- [[PROJ - Agent Enroll - Kanban Agent Credential MVP Deep Dive]] — agent key + run token authorization

## Common mistakes

[Needs real scar tissue from implementers]

## Variations

- BYOK Host: OAuth token as broker credential
- Wish Git: SSH certificate as agent credential
- Agent Enroll: Ed25519 signature + opaque run token
```

## Step 4: Cross-References

The Agent Enroll project report should add:

```markdown
## Related KB entries

- [[Tribal/keycloak-oauth-in-go-services]] — Keycloak JWT/JWKS validation pattern
- [[On-Ramp/oauth-2-oidc-flows]] — the browser OAuth flow for human login
- [[Fundamentals/access-control-models]] — authn/authz/delegation separation
- [[Tribal/sqlite-as-application-database]] — SQLite as security-relevant storage
- Candidate: [[Tribal/application-native-authorization]] (3/3) — **READY**: Keycloak for humans, Go app for agents
- Candidate: [[Tribal/three-layer-credential-separation]] (2/3) — human → agent → run
- Candidate: [[Tribal/canonical-request-signing]] (1/3) — Ed25519 signed requests
- Candidate: [[Tribal/opaque-scoped-bearer-tokens]] (1/3) — hash-only, task-bound, short-lived
```

The Keycloak tribal entry should add Agent Enroll:
```markdown
- [[PROJ - Agent Enroll - Kanban Agent Credential MVP Deep Dive]] — Keycloak for human authn, app-native agent/run authz
```

The access-control-models fundamental should add Agent Enroll:
```markdown
- [[PROJ - Agent Enroll - Kanban Agent Credential MVP Deep Dive]] — three-layer credential narrowing (human → agent → run)
```

---

# Step 5: Updated Candidate Tracking List

This section merges the new candidates from all six projects with the existing candidate tracking list from the project index.

## Tribal candidates (trigger at 3 projects)

| Concept | Seen in | Status |
|---------|---------|--------|
| **Application-native authorization** | BYOK Host, Wish Git, Agent Enroll | **3/3 — READY** |
| goja-in-WASM as sandbox boundary | Capsule Lab, (ecosystem) | 1/3 |
| Host-mediated op-stream API | Capsule Lab | 1/3 |
| goja NaN sanitization in JSON export | Capsule Lab | 1/3 |
| Buffer-full-body-before-UART | SToMS3R, Almanach | 2/3 |
| MSB-first bit packing for ESC/POS | SToMS3R, Almanach | 2/3 |
| Browser-side image processing for embedded | SToMS3R, Capsule Lab | 2/3 |
| Four-stage e-ink render pipeline | Gnosis | 1/3 |
| Draw batching at hardware-limited fps | Loupedeck | 1/3 |
| "Mutant WebSocket over serial" handling | Loupedeck | 1/3 |
| Broker-not-proxy architecture | BYOK Host | 1/3 |
| Authorization Code + PKCE from Go CLI | BYOK Host, Wish Git | 2/3 |
| SSH certificate as scoped delegation | Wish Git | 1/3 |
| pre-receive hook as policy enforcement | Wish Git | 1/3 |
| Server-as-relay-not-authority | AUTODISCO | 1/3 |
| Domain mutation helpers inside CRDT changes | AUTODISCO | 1/3 |
| Spec-first implementation discipline | Smalltalk-80 VM | 1/3 |
| **goja native module registration** | goja-embedding (generic), ZK Tool (Obsidian), Loupedeck (hardware) | 2/3 |
| **SQL as first-class command source** | Sqleton, Minitrace Query Commands | 2/3 |
| **App config vs command config separation** | Sqleton, BYOK Host (implicit) | 2/3 |
| **MicroVM as execution boundary** | Firecracker VM, pi-sandbox | 2/3 |
| **Host-mediated secret delivery** | Firecracker VM, BYOK Host (credential mediation) | 2/3 |
| **Three-layer credential separation** | Wish Git, Agent Enroll | 2/3 |
| C99 native port for host testing | uLisp PicoCalc, Smalltalk-80 VM (partial) | 2/3 |
| TFT_eSPI patching for RP2040 | uLisp PicoCalc, (other display projects?) | 2/3 |
| GStreamer pipeline construction from Go | Screencast Studio | 1/3 |
| Runtime seam for engine migration | Screencast Studio | 1/3 |
| GLib main loop coexistence with Go | Screencast Studio | 1/3 |
| Canonical request signing | Agent Enroll | 1/3 |
| Opaque scoped bearer tokens | Agent Enroll | 1/3 |
| Enrollment tokens (one-time, hash-only) | Agent Enroll | 1/3 |
| ZK note routing logic | ZK Tool | 1/3 |
| CLion configuration for Arduino | uLisp PicoCalc | 1/3 |
| Ext4 workspace as boundary artifact | Firecracker VM | 1/3 |

## On-Ramp candidates (trigger at 5 projects)

| Concept | Seen in | Status |
|---------|---------|--------|
| ESC/POS thermal printer commands | SToMS3R, Almanach, ATOM-PRINTER | 3/5 |
| E-ink display driving | Gnosis, Paper Pro, reMarkable | 3/5 |
| Git hooks for policy enforcement | Wish Git | 2/5 |
| Retained-mode rendering / dirty rects | Gnosis, Loupedeck | 2/5 |
| goja ECMAScript interpreter | Capsule Lab, Loupedeck, ecosystem | 2/5 (from sample; 52/5 in full library → already an entry) |
| CRDTs and local-first architecture | AUTODISCO | 1/5 |
| **GStreamer for Go programmers** | Screencast Studio, (future media projects) | 2/5 |
| **Arduino-cli cross-compilation** | uLisp PicoCalc, (other Arduino projects?) | 2/5 |
| Obsidian CLI from Go | ZK Tool | 1/5 |

## Fundamental candidates (trigger when supporting 2+ KB entries)

| Concept | Supports | Status |
|---------|----------|--------|
| Signal quantization and sampling | Dithering, ESC/POS, E-ink | **READY** (already exists) |
| Access control models | OAuth, SSH Certs, Keycloak Tribal | **READY** (already exists) |
| Encoding and framing | ESC/POS, Serial Protocols | **READY** (already exists) |
| Rendering pipeline fundamentals | E-ink, Dirty-rect | **READY** (already exists) |
| Distributed consistency | CRDT On-Ramp | 1/2 |
| **Host-mediated sandbox principles** | goja-embedding Tribal, Firecracker microVM Tribal (candidate) | 1/2 — needs either goja-embedding or microVM tribal to exist |

---

# Playbook Feedback

After applying the playbook to six projects, here is my assessment of playbook clarity, completeness, and usability.

## What was clear and worked well

1. **The decision flowchart is excellent.** The "Is it tribal? → 3 projects? / Is it lookupable? → 5 projects? / Does it underlie 2+ entries?" flowchart is unambiguous and fast to apply. I never had to guess which section a concept belonged in.

2. **The three-section model (Tribal/On-Ramp/Fundamental) is the right granularity.** The distinction between "how we do it," "what it is, why we care," and "the theory you actually need" maps cleanly onto the kinds of concepts I found in project reports.

3. **The templates are detailed enough to follow.** Each section tells you what to write and where. The worked example (SToMS3R → KB entries) is particularly valuable — it showed me exactly what the output should look like.

4. **The anti-patterns section saved me from mistakes.** I was initially going to write a "GStreamer for Go Programmers" on-ramp entry even though it's at 2/5, because the Screencast Studio report is hard to read without one. The anti-pattern "Creating entries preemptively" stopped me, correctly: we don't have enough media projects yet to justify a standalone entry. The right approach is to leave it as a candidate and let future projects drive it.

5. **The calibration examples set the right tone.** Reading keycloak-oauth-in-go-services.md and openssh-certificates.md before starting gave me a clear picture of the expected depth and style. The "Common mistakes" / "gotchas" sections are what make our KB different, and the examples showed exactly how to write them.

## What was confusing or took longer than expected

1. **The boundary between "variation of existing entry" and "new tribal candidate" is unclear.** ZK Tool's `require("obsidian")` module is a variation of the goja-embedding tribal entry (it follows the same pattern, just with a different native module). Is it a 2/3 tribal candidate for "goja native module registration," or is it just an example to add to the existing goja-embedding entry? The playbook doesn't address this case. I ended up calling it a 2/3 candidate, but I'm not sure that's right.

   **Suggestion:** Add a subsection to the decision flowchart: "Does this concept extend an existing tribal entry with a new variation?" If yes, add the variation to the existing entry rather than creating a new candidate. Only create a new candidate if the variation is structurally different (different code, different gotchas, different tradeoffs).

2. **Cross-referencing project reports is described but not exemplified for the "add KB links to project report" step.** The playbook says "add a `## Related KB entries` section at the bottom of the project report." But the project reports I analyzed don't have this section yet. Should I add it? The playbook implies yes, but it's a separate action from writing the intern report. I wasn't sure whether modifying the actual project report files was part of my assignment or whether I should just document what *should* be added.

   **Suggestion:** Clarify in the playbook whether Step 4 (cross-reference) means "actually modify the project reports and KB entries" or "document the cross-references that should be added." For an intern who doesn't have implementation experience, the latter is safer.

3. **Counting projects for tribal candidates is ambiguous when projects share a pattern but implement it differently.** Agent Enroll uses Ed25519 request signing + opaque run tokens. Wish Git uses SSH certificates. BYOK Host uses broker OAuth tokens. All three separate Keycloak authn from application authz. But the specific mechanisms are different. Is this one tribal pattern at 3/3, or three separate patterns at 1/3 each?

   I decided it's one pattern ("application-native authorization") at 3/3, because the core insight is the same: Keycloak authenticates humans, the Go application decides what agents and runs can do. The specific credential format is a variation. But the playbook doesn't give explicit guidance on this.

   **Suggestion:** Add a rule: "Count projects that share the core insight, even if the specific mechanism differs. Document the mechanism differences as variations in the tribal entry."

4. **The "size" of project reports doesn't correlate with analysis difficulty.** ZK Tool is 6 KB and was straightforward. But Agent Enroll is 26 KB and the hardest part wasn't the length — it was the conceptual density. The playbook's "Easy/Medium/Hard" classification in the assignment doc uses project report size as a proxy, but what actually determines difficulty is the number of concept domains and the density of cross-references. The Screencast Studio report (23 KB) was hard not because of length but because it opens an entirely new KB domain (media) with no existing entries to anchor to.

   **Suggestion:** Don't use project report size as the difficulty proxy. Use "number of concept domains with zero existing KB coverage" as the proxy.

## What I wished the playbook had explained better

1. **How to handle concepts that span the Tribal/On-Ramp boundary.** Some concepts have both a tribal aspect ("how we build GStreamer pipelines") and an on-ramp aspect ("what GStreamer is and why we care"). The playbook says "don't mix them in one entry" and gives the OAuth/Keycloak example. But for GStreamer, the tribal and on-ramp aspects are tightly coupled — you can't understand our pipeline construction without understanding elements, pads, and caps. The playbook should address this more: when both aspects are needed to read a project report, should you create both entries at once, or only the on-ramp?

2. **How to handle "domain opening" projects.** Screencast Studio opens the media domain. The current candidate tracking list doesn't have a way to mark "this project introduces a new technology domain that currently has zero KB coverage." The closest thing is the on-ramp candidate count, but the real issue is different: it's not that the concept is at 2/5, it's that *the entire domain* is at 0/N. The playbook assumes incremental growth from existing coverage. It doesn't address the "cold start" problem where a project report is unreadable without a cluster of new entries.

   **Suggestion:** Add a concept of "domain seed": when a project opens a new technology domain with zero KB coverage, flag it so that a human reviewer can decide whether to create an initial set of entries or let the domain grow organically.

3. **The "you're probably the wrong person to write it" rule is important but could use more nuance.** The playbook says if you learned it from the project report, you shouldn't write the entry. But for on-ramp entries, the playbook also says "You CAN write the first draft of an On-Ramp entry from fresh knowledge, as long as someone with experience reviews the Common mistakes and Why we care sections." This tension is real: on-ramp entries are precisely the ones that make project reports readable, and they're the ones a new person is most likely to encounter first. The playbook should make the exception more prominent and provide a clearer review workflow.

## What took longer than expected

1. **Reading all six project reports took ~30 minutes.** This is unavoidable but worth noting for planning. The playbook should set expectations: "reading a project report takes 5–10 minutes for a 6 KB report, 15–20 minutes for a 25 KB report."

2. **Deciding whether concepts are tribal or lookupable took judgment, not just rule-following.** For example: "Arduino-cli cross-compilation" — is the CLI itself lookupable? Yes, Arduino documents it. Is our angle (headless, no-IDE, reproducible build scripts) lookupable? No. But the playbook's decision tree asks "Is it our-specific knowledge?" and the answer is nuanced. I ended up calling it an on-ramp candidate at 2/5, but I could see arguing for tribal at 1/3. The playbook should acknowledge this ambiguity and recommend a default: "When in doubt, classify as on-ramp candidate (higher threshold = less premature creation)."

3. **Cross-referencing is labor-intensive.** Each project report needs links to existing KB entries, links to candidates with counts, and the KB entries need links back. For six projects, that's 12+ cross-references to add. The playbook should mention that cross-referencing is the most time-consuming step and may be worth batching.

## Summary assessment

The playbook is well-structured and produces consistent output. The decision rules are clear. The templates work. The anti-patterns section prevents the most common mistakes. My main feedback is:

1. **Add guidance for "variation of existing entry" vs "new candidate."**
2. **Add guidance for counting projects when mechanisms differ but the core insight is the same.**
3. **Clarify whether Step 4 means "actually modify files" or "document what should be modified."**
4. **Add a "domain seed" concept for projects that open new technology domains.**
5. **Don't use project report size as the difficulty proxy; use concept-domain novelty instead.**
6. **Make the on-ramp "fresh knowledge" exception more prominent.**
7. **Recommend defaulting to on-ramp when tribal/lookupable classification is ambiguous.**
