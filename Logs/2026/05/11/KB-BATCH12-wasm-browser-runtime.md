# KB Batch 12: WASM / Browser Runtime Cluster

## Batch scope

This batch processes the handoff document's **Batch J — WASM/browser runtime cluster**.

Analyzed project reports:

1. [[PROJ - WASM JSON Flattener - Go CLI and WebAssembly Tool]]
2. [[PROJ - JSON Flattener - Go WASM JSON Conversion Tool]]
3. [[PROJ - VT100 WASM Emulator]]
4. [[PROJ - Goja WASM Web REPL - A JavaScript Sandbox in the Browser]]
5. [[PROJ - WASM Plugin REPL - Goja wazero Deep Dive]]
6. [[PROJ - Federated Modules - Single-Origin Runtime Demo]]
7. [[PROJ - Browser-Side React Widget Runtime - In-Browser TSX Compilation and Reload]]

## Executive summary

Batch J did not create a new standalone KB entry, but it clearly deepened the library's browser-runtime and Wasm surface. The strongest repeated theme is not simply “Wasm in the browser.” It is **runtime boundary design**: who owns compilation, who owns capabilities, how data crosses the host/guest edge, and how much runtime machinery should be visible to the person debugging the system.

The batch most strongly reinforced two existing KB entries:

- [[On-Ramp/wasm-from-go]]
- [[Tribal/go-to-wasm-compilation]]

The JSON Flattener pair, Goja WASM Web REPL, and WASM Plugin REPL all add concrete evidence for standard Go vs TinyGo tradeoffs, browser interop shape, and host/kernel boundary choices. Federated Modules and Browser-Side React Widget Runtime broaden the cluster from “compile Go to Wasm” into “load code at runtime in the browser without pretending the boundary is simple.”

## What was written

### KB updates

- [[On-Ramp/wasm-from-go]] — updated with stronger standard-Go vs TinyGo guidance and deeper project references.
- [[Tribal/go-to-wasm-compilation]] — updated with JSON Flattener and Goja WASM Web REPL as concrete variations and with a more accurate TinyGo tradeoff warning.

### No new standalone KB entries

No single new concept crossed threshold cleanly enough to justify a separate On-Ramp or Tribal entry this batch.

## What could / should be written later

### Tribal candidates promoted or reinforced

| Concept | Seen in | Status | Notes |
|---------|---------|--------|-------|
| **goja-in-WASM as sandbox boundary** | Capsule Lab, Goja WASM Web REPL | 2/3 | Now clearly a repeated pattern, but still one project short of a dedicated Tribal entry if kept separate from broader goja/WASM docs. |
| **Host-mediated guest capability boundary** | Capsule Lab, WASM Plugin REPL | 2/3 | Browser host and wazero host differ, but both mediate what the guest may ask for instead of giving direct access. |
| **Standard Go vs TinyGo comparison harness** | JSON Flattener, Goja WASM Web REPL, WASM Plugin REPL | 3/3 — covered by existing [[On-Ramp/wasm-from-go]] and [[Tribal/go-to-wasm-compilation]] | Good example of a threshold-looking concept that should stay folded into stronger existing entries. |
| **Source string → browser transform → blob import runtime** | Browser-Side React Widget Runtime | 1/3 | Important, but currently isolated. |
| **Same-origin runtime federation teaching surface** | Federated Modules | 1/3 | Valuable teaching pattern, but still a one-off. |
| **JSON-through-memory Wasm ABI** | WASM Plugin REPL | 1/3 | Strong host/guest technique; needs another plugin/runtime project. |

### On-Ramp candidates

| Concept | Seen in | Status | What's missing from public docs |
|---------|---------|--------|--------------------------------|
| **Module Federation mental model** | Federated Modules | 1/5 🌐 | Many examples jump straight to micro-frontend scale and skip the basic host/remote/runtime questions. |
| **Browser-side TSX compilation and blob-module import** | Browser-Side React Widget Runtime | 1/5 🌐 | Existing docs cover esbuild or blob URLs separately, not the full runtime contract for user-provided widgets. |
| **WASI / Wasm guest ABI for plugin calls** | WASM Plugin REPL | 1/5 🌐 | Public docs describe Wasm and WASI, but not the concrete JSON-through-memory ABI and host-mediated call flow we used. |
| **VT100 hardware emulation mental model** | VT100 WASM Emulator | 1/5 🌐 | There is retrocomputing material, but a newcomer-oriented explanation of linked-line display memory and VT100-specific hardware simulation would help. |

## What was updated / reinforced

- [[On-Ramp/wasm-from-go]] — reinforced by JSON Flattener's dual-target comparison and Goja WASM REPL's larger-runtime lessons.
- [[Tribal/go-to-wasm-compilation]] — reinforced by JSON Flattener, Goja WASM Web REPL, and TinyGo timeout/interop tradeoffs.
- [[Tribal/goja-embedding-in-go]] — adjacent via Goja WASM Web REPL and WASM Plugin REPL, but not directly updated.
- [[Tribal/data-only-vs-host-access-module-split]] — lightly adjacent via host-mediated capability design in WASM Plugin REPL and Capsule-like sandboxing.

## Per-project extraction

### 1. WASM JSON Flattener

**Role in batch**: the clearest compact example of one pure-Go core serving both CLI and browser WASM targets.

**Tribal candidates**:
- Standard Go vs TinyGo comparison harness — same core, two build targets, explicit size/interoperability tradeoff.
- Dual-target utility with shared pure-Go kernel.
- Minimal WASI polyfill for TinyGo browser target.

**On-Ramp candidates**:
- Reinforces [[On-Ramp/wasm-from-go]].

### 2. JSON Flattener — Go WASM JSON Conversion Tool

**Role in batch**: second narrative/report variant for the same JSON Flattener work, useful as stronger support for the same Go→WASM pattern.

**Tribal candidates**:
- Reinforces standard Go vs TinyGo comparison harness.
- Reinforces shared pure-Go core across CLI and browser targets.

**On-Ramp candidates**:
- No separate concept count beyond the canonical JSON Flattener project cluster.

### 3. VT100 WASM Emulator

**Role in batch**: non-Go contrast case showing browser Wasm as a delivery surface for hardware-faithful emulation rather than a utility kernel.

**Tribal candidates**:
- None strong yet.

**On-Ramp candidates**:
- VT100 hardware emulation mental model (1/5 🌐).
- Rust/WASM browser emulator architecture (1/5 🌐).

### 4. Goja WASM Web REPL

**Role in batch**: proof that a non-trivial Go JavaScript engine can run in browser Wasm and still expose a simple `syscall/js` bridge.

**Tribal candidates**:
- goja-in-WASM as sandbox boundary (2/3 with Capsule Lab).
- Standard Go vs TinyGo comparison harness (covered by existing Wasm entries).
- TinyGo interpreter-timeout as compile-system constraint (1/3).

**On-Ramp candidates**:
- Reinforces [[On-Ramp/wasm-from-go]].
- Could contribute later to a goja orientation entry.

### 5. WASM Plugin REPL

**Role in batch**: pure-Go host/guest architecture where Wasm plugins ask for capabilities through imports rather than escaping the sandbox.

**Tribal candidates**:
- Host-mediated guest capability boundary (2/3 with Capsule Lab).
- JSON-through-memory Wasm ABI (1/3).
- One primitive registry shared by JS callers and Wasm guests (1/3).

**On-Ramp candidates**:
- WASI / Wasm guest ABI for plugin calls (1/5 🌐).

### 6. Federated Modules — Single-Origin Runtime Demo

**Role in batch**: teaching-oriented runtime module loading demo that strips away CORS/process sprawl so the federation boundary stays visible.

**Tribal candidates**:
- Same-origin runtime federation teaching surface (1/3).
- Runtime module shape discipline (`default` export expectations, manifest/remoteEntry split) (1/3).

**On-Ramp candidates**:
- Module Federation mental model (1/5 🌐).

### 7. Browser-Side React Widget Runtime

**Role in batch**: runtime compiler/loader for TSX source strings that become ESM modules and React components inside the browser.

**Tribal candidates**:
- Source string → browser transform → blob import runtime (1/3).
- Shared React instance injected into dynamic modules (1/3).
- Strict import allowlist before compilation/import (1/3).

**On-Ramp candidates**:
- Browser-side TSX compilation and blob-module import (1/5 🌐).

## Candidate decisions

### Created now

- None.

### Do not create yet

- **goja-in-WASM as sandbox boundary** — now 2/3, but not yet a separate entry.
- **Host-mediated guest capability boundary** — 2/3, promising but still broad.
- **Standard Go vs TinyGo comparison harness** — effectively 3/3, but already better represented by existing Wasm KB entries.
- **Module Federation mental model** — 1/5.
- **Browser-side TSX compilation and blob-module import** — 1/5.

## Suggested index changes

If folded into the canonical campaign index, add this as Batch 12 and update tracking so that:

- `goja-in-WASM as sandbox boundary` moves to 2/3
- `Host-mediated guest capability boundary` is tracked as a new 2/3 Tribal candidate
- `Standard Go vs TinyGo comparison harness` is noted as covered by existing Wasm KB entries
- `Module Federation mental model` and `Browser-side TSX compilation and blob-module import` are added as new On-Ramp seeds

## Follow-up review questions

1. Does another future Wasm/browser project lift **goja-in-WASM as sandbox boundary** to 3/3?
2. Should **host-mediated guest capability boundary** live as its own Tribal entry, or remain folded into broader sandbox/embedding entries?
3. When we eventually do the Codebase Browser / docs-as-product batch, does that combine with Browser-Side React Widget Runtime to form a larger browser-runtime entry?
