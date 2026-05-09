---
title: go-minitrace HTML Transcript Export
aliases:
  - go-minitrace HTML Export
  - Transcript Export Reader
  - Self-Contained Transcript Reader
  - go-minitrace Reader Export
tags:
  - project
  - go-minitrace
  - html-export
  - transcript-analysis
  - react
  - go
  - vite
status: active
type: project
created: 2026-04-14
repo: /home/manuel/code/wesen/corporate-headquarters/go-minitrace
---

# go-minitrace HTML Transcript Export

This project adds a read-only, self-contained HTML export path to `go-minitrace`. The goal is simple to state but surprisingly subtle to implement: given a `.minitrace.json` session archive, generate a single HTML file that can be handed to another person and opened locally as a rich transcript reader without depending on a running server, a database, or external static assets.

The current implementation is centered around a simplified “Proposal 2” chronological reader. Instead of inventing extra narrative layers, it stays close to the source material: raw session data, deterministic display reshaping, and original annotations. The result is a reader that is easier to trust, easier to validate, and easier to ship as a durable artifact.

> [!summary]
> This work currently has three important identities:
> 1. a new `go-minitrace export html` CLI workflow for exporting one session to one HTML file
> 2. a backend payload-shaping and HTML-inlining pipeline in Go under `pkg/exporthtml`
> 3. a dedicated read-only React export entrypoint that reuses the existing transcript viewer components without live API plumbing

## Why this project exists

`go-minitrace` already has strong raw-analysis capabilities: conversion, querying, annotation, and an interactive `serve` mode. What it did not have was a portable, durable, review-friendly artifact for a *single session*. In practice, that gap matters a lot.

A large analysis session often needs to be:

- shared with someone who does not have the archive locally,
- reviewed offline,
- attached to a ticket or handoff,
- preserved as a historical snapshot,
- opened later without remembering how to re-run the server.

A self-contained export solves that by collapsing the runtime stack into a document. The exported file becomes both a presentation layer and an archival object.

## Current project status

The project is in an active implementation phase and already has a working end-to-end path.

What exists now:

- a new CLI command:
  - `go-minitrace export html`
- session archive indexing and session lookup helpers
- a deterministic export payload builder for:
  - session metadata
  - blocks
  - turns
  - tool calls
  - original annotations
  - deterministic indices
- two rendering paths:
  - a minimal built-in template renderer
  - an inlined built-bundle renderer for the dedicated React export UI
- a dedicated frontend export entrypoint in `web/src/export`
- reader features including:
  - search
  - block expansion
  - turn anchors
  - tool-call anchors
  - read-only annotation display
- browser validation against a real large session export

What is still incomplete or still worth tightening:

- a true out-of-harness `file://` validation pass
- a more explicit startup error surface if the payload is malformed
- optional extra UX such as visible permalinks, a table of contents, or boot-time payload diagnostics

## Project shape

At a high level, the export feature has five layers:

1. **archive discovery**
   - find matching `.minitrace.json` files
   - map session IDs to archive paths
2. **payload shaping**
   - load one session
   - normalize it into a reader-oriented JSON payload
3. **HTML assembly**
   - create a single HTML document with embedded payload + JS + CSS
4. **browser boot**
   - parse the embedded payload
   - mount the React reader
5. **read-only interaction**
   - search, expand, scroll, highlight, and inspect without mutation

## Architecture

```mermaid
flowchart TD
    A[go-minitrace export html] --> B[Expand archive globs]
    B --> C[Build session index]
    C --> D[Load target session]
    D --> E[Build ReaderExport payload]
    E --> F{Renderer mode}
    F -->|template| G[RenderHTML]
    F -->|built bundle| H[RenderHTMLFromBuiltBundle]
    H --> I[Inline JS bundle]
    H --> J[Embed payload JSON]
    G --> K[Write single HTML file]
    I --> K
    J --> K
    K --> L[Browser opens HTML]
    L --> M[loadEmbeddedExport()]
    M --> N[TranscriptExportViewer]
    N --> O[Read-only transcript navigation]
```

Key code locations:

- CLI entrypoint:
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/cmd/go-minitrace/cmds/export/html.go`
- backend payload/rendering:
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/pkg/exporthtml/archive.go`
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/pkg/exporthtml/builder.go`
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/pkg/exporthtml/types.go`
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/pkg/exporthtml/render.go`
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/pkg/exporthtml/render_built.go`
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/pkg/exporthtml/render_payload.go`
- export-reader frontend:
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/web/export-reader.html`
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/web/src/export/loadEmbeddedExport.ts`
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/web/src/export/TranscriptExportViewer.tsx`
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/web/src/export/readerExportMain.tsx`
- reused viewer components:
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/web/src/components/TranscriptViewer/BlockCard.tsx`
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/web/src/components/TranscriptViewer/BlockBody.tsx`
  - `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/web/src/components/TranscriptViewer/ToolCallRow.tsx`

## Implementation details

The most important design choice is that the export is **JSON-driven**. The browser is not scraping HTML to reconstruct meaning. Instead, Go computes a stable `ReaderExport` payload, embeds it into the page, and the frontend renders that payload directly.

### The export payload

The payload contains four main regions:

- `version`
- `session`
- `annotations`
- `indices`

The `session` field is not just the raw session copied verbatim. It is normalized into a shape that better matches the reader UI:

- top-level metadata
- an array of chronological `blocks`
- each block containing `turns`
- each turn containing `tool_calls_in_turn`

The `indices` field stores precomputed lookup material such as:

- session annotation ids
- turn-to-annotation ids
- tool-call-to-annotation ids
- a simple search term index

This keeps the browser runtime comparatively dumb. The export file is more useful because the expensive “reader shape” decisions are made once, at export time, rather than repeatedly in the browser.

### Block formation

The block model is deliberately simple: a new block begins when a user turn appears. Assistant turns and the tool calls associated with them are grouped under that user prompt until the next user turn starts a new block.

That is a good compromise between fidelity and readability:

- it preserves chronology,
- it gives readers a prompt-centered structure,
- and it does not require heuristic thread detection.

Pseudocode:

```text
currentBlock = nil
for turn in session.turns:
  if turn.role == "user":
    flush currentBlock if present
    currentBlock = new block anchored at this user turn

  if currentBlock == nil:
    currentBlock = synthetic first block

  normalizedTurn = normalizeTurn(turn)
  currentBlock.turns.append(normalizedTurn)
  currentBlock.tool_calls += len(turn.tool_calls_in_turn)
  if turn.role != "user":
    currentBlock.agent_turns += 1
flush final block
```

### Renderer split: template mode vs built-bundle mode

There are two render paths because the project evolved in stages.

#### Template mode

The built-in renderer uses embedded template assets from `pkg/exporthtml/templates/*` and emits a fully self-contained HTML document directly from Go.

This mode is useful as:

- a fallback,
- a debugging baseline,
- a lower-complexity option if the React path regresses.

#### Built-bundle mode

The more feature-rich path uses a dedicated frontend build:

```bash
cd web
pnpm build:export-reader
```

That build emits a special `export-reader.html` and a single JS bundle. Go then reads the built shell, inlines the JS, replaces the payload placeholder, strips leftover external asset tags, and writes the final export.

That path gets the best of both worlds:

- reuse of the real transcript components,
- but still a single exported HTML file.

### Script-tag-safe payload embedding

One of the most important under-the-hood details is that the payload is **not** inserted into the HTML as a raw string.

The export now uses a dedicated helper to marshal and escape the JSON for safe inclusion inside:

```html
<script id="minitrace-export-data" type="application/json">...</script>
```

The helper escapes characters that can break script-tag embedding or create parsing ambiguity:

- `<`
- `>`
- `&`
- U+2028
- U+2029

This matters because transcript content and tool-call content can easily contain shell scripts, HTML-looking text, Markdown code fences, or other strings that would otherwise be dangerous to embed verbatim.

### Frontend boot model

The browser boot path is intentionally tiny:

1. locate `#minitrace-export-data`
2. parse JSON
3. mount the read-only React app into `#root`

Pseudocode:

```text
el = document.getElementById("minitrace-export-data")
if no element or no textContent:
  throw error
payload = JSON.parse(el.textContent)
createRoot(document.getElementById("root")).render(<TranscriptExportViewer data={payload} />)
```

This is a good model because it keeps the export-page contract explicit. The browser is never asked to fetch data from a server.

## Validation strategy

The export needs validation at three different levels.

### 1. Backend correctness

Validate:

- session archive selection
- payload structure
- HTML generation
- literal-safe inlining
- script-tag-safe payload embedding

Key tests live in:

- `pkg/exporthtml/builder_test.go`
- `pkg/exporthtml/render_test.go`
- `pkg/exporthtml/render_built_test.go`

### 2. End-to-end export generation

Validate with a real session:

```bash
cd /home/manuel/code/wesen/corporate-headquarters/go-minitrace
go run ./cmd/go-minitrace export html \
  --archive-glob '/home/manuel/code/wesen/corporate-headquarters/go-minitrace/ttmp/2026/04/14/GST-2026-04-13--gstreamer-pi-sessions-analysis-with-go-minitrace/output/active/*/*.minitrace.json' \
  --session-id bbf1bdf1-364a-44cb-8cd0-ebcba86dd1ad \
  --web-dist-dir ./web/dist-export-reader \
  --output /tmp/gstreamer-reader-react.html
```

### 3. Browser behavior

Validate:

- page renders
- no console errors
- no external JS/CSS/data requests
- search works
- hash navigation works
- large payloads do not corrupt the HTML document

## Important project docs

The main working ticket is:

- `/home/manuel/code/wesen/corporate-headquarters/go-minitrace/ttmp/2026/04/14/GST-2026-04-13--gstreamer-pi-sessions-analysis-with-go-minitrace`

The most important docs in that ticket are:

- `design-doc/04-proposal-2-chronological-reader-annotation-export-and-visualization-guide.md`
- `reference/01-investigation-diary.md`
- `reference/02-export-reader-dev-workflow.md`

Related durable note:

- [[ARTICLE - Self-Contained HTML Transcript Exports - Under the Hood in go-minitrace]]

## Open questions

The implementation already works, but there are still useful design questions:

- Should the export boot path show a friendlier error panel if payload parsing fails?
- Should the reader expose visible permalink affordances for turns and tool calls?
- Should a future version add optional lightweight filters by role or tool name?
- Should the minimal template renderer remain a permanent supported fallback?

## Near-term next steps

The next sensible steps are:

1. perform one manual `file://` validation outside the Playwright harness
2. keep the ticket diary and validation notes current as the export hardens
3. consider a small boot-time payload validator or React error boundary
4. decide whether to keep expanding the reader or to begin a separate timeline-style export

## Project working rule

The most important working rule for this project is:

> Keep the export literal, deterministic, and portable. If a feature requires server state, mutation APIs, or heuristic interpretation that cannot be explained clearly, it probably does not belong in the first-generation self-contained reader.
