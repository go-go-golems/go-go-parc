---
title: CozoDB Editor
aliases:
  - CozoDB Editor
  - Project CozoDB Editor
  - CozoDB Editor SEM Refactor
tags:
  - project
  - cozodb
  - go
  - react
  - ai
status: active
type: project
created: 2026-03-14
repo: /home/manuel/code/wesen/2026-03-14--cozodb-editor
---

# CozoDB Editor

This note is about the **CozoDB editor project as a whole**, not just the ticket trail.

The project is a browser-based CozoScript workbench: part editor, part query runner, part AI-assisted semantic notebook. The user writes CozoScript in a lightweight line-oriented pad, executes queries against an embedded CozoDB backend, and can ask for help inline. The AI side does not just stream plain text anymore. It can emit structured semantic items that the UI renders as rich widgets such as hints, query suggestions, and documentation references.

The simplest mental model is:

- a local CozoDB-backed query IDE,
- with a React frontend and a Go backend,
- where AI output is treated as a semantic event stream rather than as a blob of markdown.

That last point is the real differentiator of the project.

## What the project is for

The editor exists to make working with CozoScript easier and more interactive. It is trying to solve several problems at once:

- writing and iterating on CozoScript queries quickly,
- inspecting query results without leaving the editor,
- understanding the current database schema,
- getting context-sensitive help while writing,
- and turning AI output into something more structured and actionable than a wall of text.

So this is not just “ChatGPT next to a query editor”. The intent is closer to a semantic programming surface where assistance can attach to specific editor lines, suggest concrete next queries, explain concepts, and help diagnose errors.

## What the user experiences

From the user’s point of view, the app has a few core flows.

### 1. Write CozoScript and run it

The user edits lines in a pad-like editor and hits run. The backend executes the script against CozoDB and the frontend renders results in a table.

Relevant files:

- backend entrypoint:
  - [backend/main.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/main.go)
- HTTP query handlers:
  - [backend/pkg/api/handlers.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/api/handlers.go)
- CozoDB wrapper:
  - [backend/pkg/cozo/db.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/cozo/db.go)
- main screen:
  - [frontend/src/DatalogPad.jsx](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/DatalogPad.jsx)
- editor shell:
  - [frontend/src/editor/PadEditor.jsx](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/editor/PadEditor.jsx)

### 2. Ask for help inline

The editor supports AI questions tied to a line context. The user can ask a question, and the UI requests a streamed hint from the backend over websockets.

Relevant files:

- websocket API:
  - [backend/pkg/api/websocket.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/api/websocket.go)
- frontend websocket transport:
  - [frontend/src/transport/hintsSocket.js](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/transport/hintsSocket.js)
- socket handler registration:
  - [frontend/src/sem/registerDefaultSemHandlers.js](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/sem/registerDefaultSemHandlers.js)
  - [frontend/src/sem/registerCozoSemHandlers.js](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/sem/registerCozoSemHandlers.js)

### 3. Receive semantic widgets rather than only prose

The backend can stream and then authoritatively extract structured YAML payloads from the model output. These are turned into semantic widgets:

- primary hints,
- query suggestions,
- doc references.

The frontend then projects those events into bundle-backed threads and renders them under the right editor line or as global trailing items.

Relevant files:

- extraction configuration:
  - [backend/pkg/hints/extraction_config.yaml](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/hints/extraction_config.yaml)
- extraction parser and extractors:
  - [backend/pkg/hints/structured_extractors.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/hints/structured_extractors.go)
  - [backend/pkg/hints/structured_parser.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/hints/structured_parser.go)
  - [backend/pkg/hints/structured_events.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/hints/structured_events.go)
- frontend projector:
  - [frontend/src/sem/semProjection.js](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/sem/semProjection.js)
- widget renderer:
  - [frontend/src/features/cozo-sem/CozoSemRenderer.jsx](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/features/cozo-sem/CozoSemRenderer.jsx)

### 4. Diagnose errors

When a query fails, the app can send the error and script back through the hint engine and produce a diagnosis/fix suggestion flow. This currently stays slightly separate from the richer Cozo SEM widget thread path.

Relevant files:

- diagnosis request path:
  - [backend/pkg/api/websocket.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/api/websocket.go)
- diagnosis UI:
  - [frontend/src/features/diagnosis/DiagnosisCard.jsx](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/features/diagnosis/DiagnosisCard.jsx)

## The architecture

The app now has a cleaner shape than when this work started.

### Backend

The backend is a Go server that does three jobs:

1. open and query CozoDB,
2. expose HTTP and websocket APIs,
3. optionally run AI hint/diagnosis inference.

The main backend layers are:

- `backend/pkg/cozo`
  - local database wrapper over the CozoDB C interface
- `backend/pkg/api`
  - HTTP query endpoints
  - schema endpoints
  - websocket event transport
- `backend/pkg/hints`
  - prompt building
  - structured extraction config
  - preview and final parsing
  - event translation into frontend-facing SEM envelopes

There is a nice separation now between:

- raw model streaming,
- extraction of typed semantic payloads,
- and translation into UI-consumable websocket events.

### Frontend

The frontend is a React/Vite app. It is no longer one giant screen component. The important split is:

- `transport`
  - websocket and HTTP clients
- `editor`
  - line-oriented document model and rendering shell
- `sem`
  - event projector and selector layer
- `features`
  - actual UI cards and widgets
- `theme`
  - shared styling and tokens

This matters because the semantic thread projector is its own architectural layer. The frontend is no longer pretending that streaming UI state is the same thing as editor state.

## The semantic event model

This is the part of the project that is easiest to lose if I only think in terms of UI cards.

The system now effectively has three semantic levels:

### 1. Request/stream level

One hint or diagnosis request becomes one response stream. The backend assigns a bundle identity for that stream.

### 2. Structured item level

Inside that response, the model can emit multiple structured items:

- hint
- query suggestion
- doc ref

Each item is canonicalized using bundle identity plus family plus ordinal.

### 3. UI thread level

The frontend groups those items into one visible thread by explicit parent-child relationships, not by arrival order.

This is the key reason the current system is much more robust than the earlier version.

## Why the current architecture is better

The project started closer to “editor plus AI responses”. It now looks more like “editor plus event-sourced semantic assistance”.

The practical improvements are:

- previews and final extracted entities now line up,
- structured items can be anchored to the correct line,
- multiple semantic items from the same response are grouped deterministically,
- collapse and dismiss state can key off stable thread IDs,
- and the system is in a much better place to support future hydration or replay.

Another important improvement is that the temporary compatibility fallback was eventually removed. The frontend no longer synthesizes visible SEM threads from bundleless adjacency. That is a good thing. It means there is now one semantic model instead of two competing ones.

## What was built during the project, in product terms

If I ignore ticket names and just describe the application improvements, the project delivered roughly this:

- a modularized frontend editor architecture,
- optional AI streaming via the backend hint engine,
- structured YAML extraction for semantic widgets,
- inline and global rich widget rendering,
- foldable and dismissible semantic threads,
- deterministic bundle-backed identity for extracted items,
- backend-authoritative anchor propagation,
- and cleanup of the legacy fallback path.

That is the real shape of the project.

## Relationship to geppetto and pinocchio

This project is adjacent to [[PROJ - GO GO GOLEMS - GEPPETTO]] and to the broader pinocchio ecosystem, but the most useful way to think about it is:

- the CozoDB editor uses ideas and infrastructure from that world,
- but it also has its own local event contract and UI projector logic,
- and those local seams turned out to matter more than broad “framework integration” language.

In other words, geppetto and pinocchio are relevant context, but the important work here was making the **local application contract** coherent:

- request in,
- stream out,
- extract semantic payloads,
- project them into stable UI entities,
- render them under editor context.

## What can be reused elsewhere

This project contains several reusable patterns.

### Request-scoped projection defaults

The backend `ProjectionDefaults` model is a good pattern whenever a streaming inference session should carry request-owned metadata into extraction.

Main source:

- [backend/pkg/hints/projection_defaults.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/hints/projection_defaults.go)

### Canonical preview/final identity

If previews and finals can both refer to the same extracted semantic object, they must share the same canonical ID. This is a reusable lesson for any streamed extraction UI.

Main sources:

- [backend/pkg/hints/structured_extractors.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/hints/structured_extractors.go)
- [backend/pkg/hints/structured_parser.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/hints/structured_parser.go)

### Relation-based projector

The frontend SEM projector is a general pattern for notebook or chat/editor hybrid systems:

- normalize events into entities,
- keep transport thin,
- expose selectors,
- key UI state off stable IDs,
- never make rendering depend on arrival adjacency if explicit relations are available.

Main source:

- [frontend/src/sem/semProjection.js](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/sem/semProjection.js)

### Render-after-line editor seam

The editor’s `renderAfterLine(...)` seam is a good compromise between plain text editing and notebook composition. It lets semantic widgets attach to lines without forcing the core document into a full cell-based notebook model.

Main sources:

- [frontend/src/editor/PadEditor.jsx](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/editor/PadEditor.jsx)
- [frontend/src/editor/usePadDocument.js](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/editor/usePadDocument.js)

## What I would tell future me first

If I come back to this project later, the most important facts are:

- this is a **CozoScript editor with semantic AI assistance**, not just a frontend refactor exercise,
- the backend now owns semantic identity and anchor defaults,
- the frontend projector is the semantic heart of the UI,
- bundle metadata is mandatory for visible Cozo SEM threads,
- and the ticket docs are useful as implementation history, but they are not the project itself.

## Important source files

If I need to re-understand the project quickly, these are the first files I should open.

### Server and API

- [backend/main.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/main.go)
- [backend/pkg/api/handlers.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/api/handlers.go)
- [backend/pkg/api/websocket.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/api/websocket.go)

### Cozo and hints

- [backend/pkg/cozo/db.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/cozo/db.go)
- [backend/pkg/hints/engine.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/hints/engine.go)
- [backend/pkg/hints/prompt.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/hints/prompt.go)
- [backend/pkg/hints/extraction_config.yaml](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/hints/extraction_config.yaml)
- [backend/pkg/hints/projection_defaults.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/hints/projection_defaults.go)
- [backend/pkg/hints/sem_registry.go](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/backend/pkg/hints/sem_registry.go)

### Frontend

- [frontend/src/DatalogPad.jsx](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/DatalogPad.jsx)
- [frontend/src/editor/usePadDocument.js](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/editor/usePadDocument.js)
- [frontend/src/transport/hintsSocket.js](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/transport/hintsSocket.js)
- [frontend/src/sem/semProjection.js](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/sem/semProjection.js)
- [frontend/src/features/cozo-sem/CozoSemRenderer.jsx](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/frontend/src/features/cozo-sem/CozoSemRenderer.jsx)

## Important implementation history

These are worth keeping around because they explain how the architecture got to its current shape.

### COZODB-002

- [COZODB-002 design doc](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/ttmp/2026/03/14/COZODB-002--geppetto-pinocchio-streaming-structured-extraction-for-sem-frame-rich-widgets/design-doc/01-independent-review-and-implementation-guide-for-geppetto-pinocchio-and-sem-extraction-widgets.md)
- [COZODB-002 tasks](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/ttmp/2026/03/14/COZODB-002--geppetto-pinocchio-streaming-structured-extraction-for-sem-frame-rich-widgets/tasks.md)
- [COZODB-002 diary](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/ttmp/2026/03/14/COZODB-002--geppetto-pinocchio-streaming-structured-extraction-for-sem-frame-rich-widgets/reference/01-investigation-diary.md)

### COZODB-003

- [COZODB-003 design doc](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/ttmp/2026/03/15/COZODB-003--frontend-decomposition-plan-for-sem-migration-and-widget-modularization/design-doc/01-frontend-decomposition-architecture-review-and-intern-implementation-guide.md)
- [COZODB-003 tasks](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/ttmp/2026/03/15/COZODB-003--frontend-decomposition-plan-for-sem-migration-and-widget-modularization/tasks.md)
- [COZODB-003 diary](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/ttmp/2026/03/15/COZODB-003--frontend-decomposition-plan-for-sem-migration-and-widget-modularization/reference/01-investigation-diary.md)

### COZODB-004

- [COZODB-004 design doc](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/ttmp/2026/03/15/COZODB-004--sem-projection-and-timeline-hydration-tightening/design-doc/01-sem-projection-and-timeline-hydration-refactor-guide.md)
- [COZODB-004 tasks](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/ttmp/2026/03/15/COZODB-004--sem-projection-and-timeline-hydration-tightening/tasks.md)
- [COZODB-004 diary](file:///home/manuel/code/wesen/2026-03-14--cozodb-editor/ttmp/2026/03/15/COZODB-004--sem-projection-and-timeline-hydration-tightening/reference/01-investigation-diary.md)

## Bottom line

The CozoDB editor is now a much more coherent system than the original prototype. It has:

- a real frontend architecture,
- a real semantic extraction pipeline,
- a real projector model,
- and a cleaner separation between raw model output and rendered UI meaning.

That is the actual project.

## KB reviews

- [[KB-BATCH13-cozo-editor-structured-browser-tools]] (2026-05-11) — Batch D analysis; highlighted the semantic-event projector architecture and its relation to later notebook packaging work.

## Related KB entries

**Tribal candidates** (not yet written / needs review):
- Backend-authoritative semantic event stream projected into stable UI threads (2/3 across the Cozo editor line).
- Request-scoped projection defaults (1/3).
- Canonical preview/final identity (1/3).
- Preset adapter over notebook core behavior (supports the later packaging line; 3/3 across the broader Cozo family).

**On-Ramp candidates** (not yet written):
- Semantic event projection in notebook/editor UIs (1/5 internal-domain seed).

