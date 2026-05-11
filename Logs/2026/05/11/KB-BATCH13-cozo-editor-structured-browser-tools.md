# KB Batch 13: Cozo / Editor / Structured Browser Tools

## Batch scope

This batch processes the handoff document's **Batch D — Cozo / editor / structured browser tools**.

Analyzed project reports:

1. [[PROJ - CozoDB Editor - SEM Streaming, Widgetization, and Hydration Refactor]]
2. [[PROJ - CozoScript Web UI - CodeMirror Language Package and Browser Editor]]
3. [[PROJ - CozoDB Editor - Notebook Packaging and JavaScript Preset]]
4. [[PROJ - CozoDB Editor - Merge Resolution, SQLite Preset, and Editor Highlighting]]
5. [[PROJ - SQLide Browser - Go Wasm SQL IDE]]
6. [[PROJ - Hover Component Inspector - Building a Browser Overlay Lens]]

## Executive summary

Batch D is really two adjacent clusters rather than one perfectly unified theme.

The first cluster is the **Cozo / notebook / editor product line**. Those reports repeatedly show that language- or runtime-specific behavior should sit behind preset adapters or editor adapters, while the shared notebook/editor shell stays honest about what it owns. The second cluster is **structured browser tooling**: SQLide Browser and Hover Component Inspector both show browser-side tools becoming much more usable once the runtime boundary is explicit and the UI is a thin explanation layer over a smaller, well-defined core.

This batch did not produce a new standalone KB entry. The strongest outputs were:

- a new 3/3 Tribal candidate: **preset adapter over notebook core behavior**
- a reinforced 2/3 Tribal candidate: **language package as product, browser shell as consumer**
- an update to [[On-Ramp/wasm-from-go]] using SQLide Browser as a new split-architecture example

## What was written

### KB updates

- [[On-Ramp/wasm-from-go]] — updated with SQLide Browser as a variation where Go/Wasm handles editor intelligence while SQLite's own Wasm build runs in a worker.

### No new standalone KB entries

The batch generated strong candidates, but none that clearly outranked the existing KB surface enough to justify a new entry immediately.

## What could / should be written later

### Tribal candidates promoted or reinforced

| Concept | Seen in | Status | Notes |
|---------|---------|--------|-------|
| **Preset adapter over notebook core behavior** | Cozo Notebook Packaging, Cozo Merge/SQLite follow-up, Cozo SEM refactor | 3/3 — candidate | Repeated rule: language/runtime-specific behavior belongs in preset adapters, not in shared notebook core. |
| **Language package as product, browser shell as consumer** | CozoScript Web UI, Cozo Merge/editor modularization | 2/3 | Strong editor-architecture pattern: grammar/language package first, shell second. |
| **Backend-authoritative semantic event stream projected into stable UI threads** | Cozo SEM refactor, Cozo notebook packaging line | 2/3 | Strong local architecture pattern, but still concentrated in one product family. |
| **Go/Wasm editor intelligence over worker-owned SQLite engine** | SQLide Browser, broader Wasm/browser work | 2/3 — covered partly by [[On-Ramp/wasm-from-go]] | Better as a variation of the existing Wasm entry than a separate doc right now. |
| **Page-level overlay as guest, not page owner** | Hover Component Inspector | 1/3 | Good browser-tooling principle, but currently isolated. |

### On-Ramp candidates

| Concept | Seen in | Status | What's missing from public docs |
|---------|---------|--------|--------------------------------|
| **CodeMirror 6 language package mental model** | CozoScript Web UI, Cozo editor modularization | 2/5 🌐 | Docs exist, but not the “grammar first, highlighting second, shell third” orientation from a real language workbench port. |
| **Notebook preset architecture** | Cozo notebook packaging line | 2/5 | Existing notebook docs are often framework-specific and do not explain the preset/runtime split crisply. |
| **Browser overlay inspection architecture** | Hover Component Inspector | 1/5 🌐 | Browser extension docs exist, but not a newcomer-focused mental model for overlay-as-guest inspection. |
| **SQLite worker + OPFS mental model** | SQLide Browser | 1/5 🌐 | SQLite Wasm and OPFS docs exist, but not the precise boundary between Go/Wasm text logic, worker RPC, and DB ownership. |

## What was updated / reinforced

- [[On-Ramp/wasm-from-go]] — reinforced by SQLide Browser's split architecture.
- [[On-Ramp/tree-sitter-for-go-tools]] — lightly adjacent via CozoScript Web UI's grammar-first editor architecture, though not directly updated.
- [[Tribal/go-to-wasm-compilation]] — adjacent via SQLide Browser, but not directly updated this batch.

## Per-project extraction

### 1. CozoDB Editor — SEM Streaming, Widgetization, and Hydration Refactor

**Role in batch**: canonical semantic-event/UI-projection report.

**Tribal candidates**:
- Backend-authoritative semantic event stream projected into stable UI threads (2/3 across Cozo editor reports).
- Request-scoped projection defaults (1/3).
- Canonical preview/final identity (1/3).
- Preset adapter over notebook core behavior (supports later packaging line by showing why local app contracts must stay coherent).

**On-Ramp candidates**:
- Semantic event projection in notebook/editor UIs (1/5 internal-domain seed).

### 2. CozoScript Web UI — CodeMirror Language Package and Browser Editor

**Role in batch**: grammar-first browser workbench.

**Tribal candidates**:
- Language package as product, browser shell as consumer (2/3 with later editor modularization work).
- Parse-context-driven autocomplete rather than regex-driven autocomplete (1/3).
- Browser shell intentionally thin over language package (1/3).

**On-Ramp candidates**:
- CodeMirror 6 language package mental model (2/5 🌐).

### 3. CozoDB Editor — Notebook Packaging and JavaScript Preset

**Role in batch**: first explicit preset architecture report.

**Tribal candidates**:
- Preset adapter over notebook core behavior (2/3 here; 3/3 across Cozo line).
- Shared notebook seams own runtime result vocabulary (1/3).
- Storybook/MSW as architecture test for preset surfaces (1/3).

**On-Ramp candidates**:
- Notebook preset architecture (2/5).

### 4. CozoDB Editor — Merge Resolution, SQLite Preset, and Editor Highlighting

**Role in batch**: proof that the packaged architecture survives upstream merge pressure and a third preset family.

**Tribal candidates**:
- Preset adapter over notebook core behavior (3/3).
- Language package as product, browser shell as consumer (2/3).
- Keep modular architecture during merge; port behavior into new seams instead of regressing structure (1/3).

**On-Ramp candidates**:
- CodeMirror 6 language package mental model (2/5 🌐).
- Notebook preset architecture (2/5).

### 5. SQLide Browser — Go Wasm SQL IDE

**Role in batch**: browser SQL IDE with explicit split between Go/Wasm editor intelligence and worker-owned SQLite engine.

**Tribal candidates**:
- Go/Wasm editor intelligence over worker-owned SQLite engine (2/3 when considered with broader Wasm/browser evidence; covered partly by existing Wasm KB entries).
- Keep split architecture: text/state in Go, DB engine in worker (1/3 local expression of the same principle).

**On-Ramp candidates**:
- SQLite worker + OPFS mental model (1/5 🌐).

### 6. Hover Component Inspector — Building a Browser Overlay Lens

**Role in batch**: browser extension overlay tool with clear content-script/page boundary rules.

**Tribal candidates**:
- Page-level overlay as guest, not page owner (1/3).
- Inspection result as central curated data structure (1/3).
- Component identity as evidence, not certainty (1/3).

**On-Ramp candidates**:
- Browser overlay inspection architecture (1/5 🌐).

## Candidate decisions

### Created now

- None.

### Do not create yet

- **Preset adapter over notebook core behavior** — 3/3, but very concentrated inside one Cozo product line; worth waiting for another notebook/editor family before promoting.
- **Language package as product, browser shell as consumer** — 2/3.
- **CodeMirror 6 language package mental model** — 2/5.
- **Notebook preset architecture** — 2/5.

## Suggested index changes

Add Batch 13 entries for all six projects and update campaign counts:

- Analyzed so far: 68
- Remaining: 99
- On-Ramp entries: 18

Update candidate tracking:

- Add **preset adapter over notebook core behavior** as a 3/3 Tribal candidate.
- Add **language package as product, browser shell as consumer** as a 2/3 Tribal candidate.
- Add **CodeMirror 6 language package mental model** as a 2/5 On-Ramp candidate.
- Add **Notebook preset architecture** as a 2/5 On-Ramp candidate.

## Follow-up review questions

1. Should **preset adapter over notebook core behavior** stay a Cozo-local lesson, or become a general Tribal entry after one more notebook/editor family appears?
2. Does a future docs/product or browser-runtime batch provide the third project needed for **language package as product, browser shell as consumer**?
3. Should SQLide Browser stay folded into `wasm-from-go`, or does a future browser-database project justify a standalone On-Ramp around worker-owned engines and OPFS?
