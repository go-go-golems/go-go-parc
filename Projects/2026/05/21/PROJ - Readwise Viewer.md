---
title: Readwise Viewer
aliases:
  - Readwise Viewer
  - readwise-viewer
tags:
  - project
  - readwise
  - sqlite
  - go
  - typescript
  - clim
  - redux
status: active
type: project
created: 2026-05-21
repo: /home/manuel/code/wesen/2026-05-21--readwise-viewer
---

# Readwise Viewer

Readwise Viewer is a local workbench for navigating, inspecting, and classifying a personal Readwise Reader library of 13,848 documents. It combines a Go backend built on the Glazed command framework with a monochrome CLIM-style web UI built on Redux and Immer. The system reads from a local SQLite database populated by a Python sync script, and it serves both a terminal CLI and a browser-based presentation interface from a single binary.

> [!summary]
> The project currently has three important identities:
> 1. a SQLite-backed Go API server that wraps every data row in a typed `PresentationRef` with semantic capabilities
> 2. a Glazed CLI for terminal-based document browsing, searching, and inspection
> 3. a CLIM-style web UI that treats every on-screen object as a typed, selectable, actionable presentation — with Redux state management, Immer immutable updates, and a centralized action registry

## Why this project exists

Readwise Reader accumulates documents faster than any individual can triage them. The current library has 13,848 documents, of which 13,770 are untagged. The Readwise web interface is designed for reading, not for bulk classification or systematic review. The Viewer exists to fill that gap: it provides dense, fast, command-first interaction with a large document corpus, without relying on the Readwise cloud for every operation.

The project also exists to explore the CLIM presentation pattern in a real working tool. The Street Deli prototype proved that typed presentations, an action registry, and a two-mode interaction model (normal and select) work well for a small domain. Readwise Viewer applies the same pattern to a domain where the objects are documents, sources, tags, clusters, and curation proposals — where the scale (13K+ items) and the stakes (mutations affect a real personal library) make the interaction discipline more important, not less.

## Current project status

The repository is in an active development phase. The Go backend and CLIM UI are both functional and connected.

What already exists:

- a Go binary `readwise-viewer` with 8 Glazed CLI subcommands: `documents`, `sources`, `tags`, `runs`, `stats`, `search`, `clusters`, `get`
- a `serve` command that starts an HTTP server on port 8771, serving the CLIM UI and a REST API from a single binary (using `go:embed`)
- a Python sync script that populates the local SQLite database from the Readwise CLI with full pagination and retry
- a CLIM web UI with 8 views: documents, detail, sources, tags, runs, clusters, help, and search
- a Redux + Immer store managing the CLIM state machine (normal/select/confirm modes)
- a centralized action registry mapping 16 CLIM commands to Redux dispatch calls
- a right-click context menu showing actions compatible with the clicked presentation type
- a YES/NO confirm modal for dangerous actions
- pagination controls for the document list
- clickable action suggestions in the hint bar after selecting a presentation

What is still incomplete:

- the Python categorization pipeline (`02-categorize.py`, `03-apply-tags.py`, `04-triage-inbox.py`)
- proposal views and proposal mutation actions in the CLIM UI
- the `rules.yaml` and `tag-vocabulary.yaml` configuration files for the rule engine
- any remote mutation — all write operations are stubbed

## Project shape

At a high level, the project has four layers:

1. **Local data pipeline** — Python scripts that sync Readwise data into SQLite
2. **Go backend** — Glazed CLI commands + HTTP API over the SQLite database
3. **CLIM web UI** — TypeScript/Redux/Immer frontend with typed presentations and an action registry
4. **DMETA model** — YAML-defined semantic vocabulary (archetypes, capabilities, presentations)

```text
Readwise Cloud
  │
  │ readwise CLI + scripts/01-sync-to-sqlite.py
  ▼
data/readwise.db (SQLite, 13,848 docs)
  │
  │ Go: pkg/readwiseviewer/db.go → api.go
  ▼
HTTP API (GET /api/documents, /api/sources, /api/tags, ...)
  │
  │ JSON with PresentationRef wrappers
  ▼
CLIM UI (Redux store → render → DOM)
```

## Architecture

The architecture separates three concerns: data access, API presentation, and UI interaction. Each layer has a single responsibility and a clean boundary.

### Go backend: data and API layer

The Go backend is organized into two packages:

- `pkg/readwiseviewer/db.go` — domain types and SQL query functions
- `pkg/readwiseviewer/api.go` — HTTP handlers and PresentationRef builders
- `pkg/web/serve.go` — embedded static file server

The `db.go` package defines domain types that map directly to the SQLite schema: `ReaderDocument`, `Source`, `Tag`, `SyncRun`, `UntaggedCluster`, `DBStats`. Every nullable column uses `sql.NullString` or `sql.NullInt64` — a detail that matters because 3,023 of the 13,848 documents have NULL titles, and 3,154 have NULL summaries.

The query functions accept filter structs and return paginated results:

```go
type DocumentFilters struct {
    Location *string
    Category *string
    Source   *string
    Tag      *string
    Untagged bool
    Query    *string
    Limit    int
    Offset   int
}

func ListDocuments(db *sql.DB, filters DocumentFilters) ([]ReaderDocument, int, error)
```

The `api.go` package wraps every domain object in a `PresentationRef` before returning it as JSON. This is the key design decision: the API does not return raw SQL rows. It returns semantic objects that carry their own type, capabilities, and identity.

```go
type PresentationRef struct {
    SemanticID       string   `json:"semanticId"`
    DomainType       string   `json:"domainType"`
    PresentationType string   `json:"presentationType"`
    Label            string   `json:"label"`
    Capabilities     []string `json:"capabilities"`
    CopyValue        string   `json:"copyValue,omitempty"`
}
```

Every API response follows this envelope:

```json
{
  "items": [{ "presentation": {...}, "data": {...} }],
  "page": { "limit": 50, "offset": 0, "total": 13848 }
}
```

The CLI commands are built using the Glazed command framework. Each command follows the same pattern: define a `CommandDescription` with flags, implement `RunIntoGlazeProcessor` that decodes settings into a struct, query the database, and emit rows through the processor. The Glazed framework handles output formatting (table, JSON, YAML) automatically.

### CLIM UI: Redux + Immer state machine

The CLIM UI is a single-page application built with TypeScript, Redux, and Immer. Its architecture follows one unidirectional data flow:

```text
User input (click, keyboard)
  → dispatch(Redux action)
  → reducer (Immer produce)
  → new immutable state
  → render(state → DOM)
```

The source is organized into six TypeScript modules:

| Module | Responsibility | Lines |
|--------|---------------|-------|
| `types.ts` | Type definitions for PresentationRef, ClimState, ActionTypes | 247 |
| `api.ts` | Typed fetch wrappers for /api/* endpoints | 67 |
| `store.ts` | Redux store, Immer reducer, action creators | 433 |
| `actions.ts` | CLIM action registry → Redux dispatch bridge | 324 |
| `render.ts` | Pure functions: ClimState → DOM | 465 |
| `app.ts` | Entry point, event wiring, store subscription | 276 |

The store shape:

```typescript
interface ClimState {
  ui: {
    view: string
    mode: 'normal' | 'select' | 'confirm'
    selected: PresentationRef | null
    pendingAction: ClimAction | null
    pendingRef: PresentationRef | null
    commandBuffer: string
    actionResult: string
    commandHint: string
    contextMenu: ContextMenuState
  }
  documents: ViewState<ReaderDocumentData> & { filters: DocumentFilters }
  detail: { item: ItemWrapper | null, loading: boolean, error: string | null }
  sources: ViewState<SourceData>
  tags: ViewState<TagData>
  runs: ViewState<SyncRunData>
  clusters: ViewState<ClusterData>
  stats: DBStats | null
}
```

The Immer reducer uses `produce()` to make updates read like mutations while producing immutable state. This matters for nested updates like setting document filters:

```typescript
case ActionTypes.SET_DOCUMENT_FILTERS: {
  draft.documents.filters = action.payload as DocumentFilters
  draft.documents.page.offset = 0
  break
}
```

Without Immer, this would require spreading the entire state tree. With Immer, it reads like direct mutation, but the draft is a proxy that records changes and produces a new immutable object.

### The CLIM action registry: bridging commands and Redux

The action registry is the bridge between the CLIM interaction pattern and the Redux dispatch pattern. It defines 16 CLIM actions, each with an ID, argument types, and a danger flag:

```typescript
const CLIM_ACTIONS: ClimAction[] = [
  { id: 'DOCUMENTS', argTypes: [], noArg: true },
  { id: 'INBOX', argTypes: [], noArg: true },
  { id: 'INSPECT', argTypes: ['ReaderDocument'] },
  { id: 'ARCHIVE-DOCUMENT', argTypes: ['ReaderDocument'], dangerous: true },
  { id: 'FILTER-BY-TAG', argTypes: ['Tag'] },
  // ...
]
```

The `executeCommand` function parses typed input and dispatches:

```text
User types "INSPECT" + Enter
  → findAction("INSPECT") → action has argTypes
  → dispatch(enterSelectMode(action))
  → compatible presentations turn red
  → user clicks red <ReaderDocument>
  → executeArgAction(action, ref)
  → dispatch(loadDocumentDetail(ref.semanticId))
  → render(detail view)
```

The compatibility check is a pure function of the action's `argTypes` and the presentation's `presentationType` and `capabilities`:

```typescript
function actionAcceptsRef(action: ClimAction, ref: PresentationRef): boolean {
  return action.argTypes.includes(ref.presentationType) ||
    action.argTypes.some(t => ref.capabilities.includes(t.toLowerCase()))
}
```

This same function drives three UI surfaces: the hint bar (clickable action suggestions after selecting a presentation), the right-click context menu (shows all compatible actions), and select-mode highlighting (compatible presentations turn red).

### Interaction modes

The CLIM UI has three interaction modes, each represented as a distinct value in `state.ui.mode`:

**Normal mode.** Click a presentation to select it. The hint bar shows compatible actions as white clickable labels. Right-click a presentation to see a context menu with all compatible actions.

**Select mode.** Type a command that requires an argument (like `INSPECT`). All compatible presentations turn red. Clicking a red presentation supplies it as the argument and dispatches the action. Pressing Escape exits select mode.

**Confirm mode.** Triggered by dangerous actions (like `ARCHIVE-DOCUMENT`). A modal overlay appears with YES (red) and NO (white) buttons. Clicking YES or typing YES executes the action. Clicking NO or pressing Escape cancels it. This replaces the previous keyboard-only confirmation flow.

### Visual design

The UI follows strict monochrome rules inherited from the Street Deli CLIM prototype:

- Background: `#000000`
- Base text: `#FFFFFF` (white)
- Dim text: `#CCCCCC` for secondary labels, `#666666` for metadata
- Select-mode red: `#ff4444`
- Font: Berkeley Mono, 13px, line-height 1.5
- No shadows, no rounded corners, no gradients, no card chrome

Every meaningful object on screen is a typed presentation rendered with `data-type`, `data-id`, `data-label`, `data-capabilities`, and `data-copy-value` attributes. Event delegation handles all clicks — no inline event handlers.

## Implementation details

### SQLite schema and NULL handling

The SQLite database was created by a Python sync script (`scripts/01-sync-to-sqlite.py`) that paginates the Readwise CLI and upserts documents. The schema has a critical detail: many columns are nullable. The current data shows:

| Column | NULL count | Notes |
|--------|-----------|-------|
| `title` | 3,023 | Highlights and notes often have no title |
| `author` | 3,023 | |
| `source` | 2,698 | |
| `site_name` | 3,203 | |
| `summary` | 3,154 | |
| `location` | 3,023 | Highlights have NULL location |
| `source_url` | 3,023 | |

The Go `ReaderDocument` struct uses `sql.NullString` for all nullable text columns. The `nullString` helper converts these to empty strings for JSON serialization. This was discovered the hard way: filtering by tag returned 500 errors because `Scan` could not convert NULL to a plain `string`.

The FTS5 virtual table (`documents_fts`) supports full-text search over title, author, site_name, summary, source_url, and notes. It requires the `fts5` build tag when compiling with `mattn/go-sqlite3`:

```bash
go build -tags fts5 ./...
go run -tags fts5 ./cmd/readwise-viewer serve
```

Without the tag, search queries return "no such module: fts5".

### PresentationRef as the API contract

The `PresentationRef` type is the central design contract of the system. It ensures that the frontend never has to infer semantics from raw SQL column names. Instead, every item arrives with its own type, capabilities, and identity:

```json
{
  "semanticId": "01ks6213c9j2fdbavb623stsht",
  "domainType": "ReaderDocument",
  "presentationType": "ReaderDocument",
  "label": "Datasette Agent",
  "capabilities": ["contentful", "sourceable", "readable", "taggable", "classifiable", "triageable", "syncable"],
  "copyValue": "https://read.readwise.io/read/01ks6213c9j2fdbavb623stsht"
}
```

The capabilities list comes from the DMETA model defined in `sources/dmeta-ir/core-model/capabilities.yaml`. The UI uses capabilities for action compatibility checks: a `<ReaderDocument>` with `taggable` capability is compatible with `CLASSIFY`, while a `<Source>` with `sourceable` capability is compatible with `FILTER-BY-SOURCE`.

### The render function is a pure subscriber

The `render()` function subscribes to the Redux store and updates the DOM on every state change. It is a pure function of state: given the same `ClimState`, it produces the same DOM. This has several consequences:

- The render function has no side effects. It does not call `window.open()` or make API calls.
- Select-mode highlighting is computed inline during rendering: `getSelectModeClasses(ref, state)` returns `selectable` or `select-disabled` CSS classes based on the current mode and pending action.
- Context menu and confirm modal are rendered as positioned DOM elements created on demand and removed when dismissed.
- The render function uses `requestAnimationFrame` batching, not time-based throttling. Multiple dispatches within the same frame are coalesced into a single render call. This fixed a bug where `HELP + Enter` required an extra keypress to take effect.

### Single-binary distribution with go:embed

The `serve` command embeds the entire CLIM UI (HTML, CSS, compiled JavaScript) into the Go binary using `//go:embed clim/*` in `pkg/web/serve.go`. The build pipeline is:

```bash
cd pkg/web && bun build clim/app.ts --outdir clim --target browser
go build -tags fts5 ./...
```

The first step bundles all TypeScript modules and their dependencies (Redux, Immer) into a single `app.js`. The second step compiles the Go binary with the JavaScript embedded. The result is a single `readwise-viewer` binary that serves both the API and the UI on port 8771.

### Action dispatch from multiple surfaces

The same CLIM action can be dispatched from three UI surfaces:

1. **Keyboard command line** — type `INSPECT` + Enter
2. **Hint bar** — click a white action label after selecting a presentation
3. **Context menu** — right-click a presentation and choose from compatible actions

All three surfaces converge on the same `executeArgAction()` function in `actions.ts`. This ensures consistent behavior regardless of how the user triggers an action. Dangerous actions always enter confirm mode, whether triggered by keyboard, hint bar, or context menu.

## Current user-facing commands

### CLI (terminal)

```text
readwise-viewer documents [--location new] [--untagged] [--limit 50]
readwise-viewer sources [--limit 100]
readwise-viewer tags
readwise-viewer runs [--limit 50]
readwise-viewer stats
readwise-viewer search --q "sqlite datasette" [--limit 50]
readwise-viewer clusters
readwise-viewer get <document-id>
readwise-viewer serve [--port 8771] [--db data/readwise.db]
```

All list commands support Glazed output formatting: `--output json`, `--output yaml`, `--fields id,title,category`.

### Browser (CLIM UI)

| Command | Effect |
|---------|--------|
| `DOCUMENTS` | Show document list (paginated) |
| `INBOX` | Show documents in inbox (location=new) |
| `FEED` | Show documents in feed |
| `UNTAGGED` | Show untagged documents |
| `SOURCES` | Show source aggregation |
| `TAGS` | Show tag list |
| `RUNS` | Show sync run history |
| `CLUSTERS` | Show untagged document clusters |
| `SEARCH <query>` | FTS5 full-text search |
| `INSPECT` | Enter select mode, then click a document |
| `HELP` | Show command reference |

Right-click any presentation for a context menu. Click a presentation for action suggestions in the hint bar.

## Important project docs

- Architecture and pipeline guide: `ttmp/.../design-doc/01-readwise-reader-categorization-system-architecture-and-implementation-guide.md`
- CLIM UI design and implementation guide: `ttmp/.../design-doc/02-readwise-clim-presentation-ui-design-and-implementation-guide.md`
- API quick reference: `ttmp/.../reference/02-readwise-cli-and-reader-api-quick-reference.md`
- Implementation diary: `ttmp/.../reference/01-diary.md`
- DMETA semantic model: `sources/dmeta-ir/core-model/`

## Open questions

1. Should the CLIM UI switch to React as the view layer for complex views (detail, proposals) while keeping the presentation/action model?
2. Should proposal tables be created by the Go backend or by the Python categorization scripts?
3. Should any high-confidence proposals auto-apply, or should the CLIM UI always require explicit acceptance?
4. Should the API support GraphQL-style field selection to reduce payload size for 13K+ document lists?

## Near-term next steps

- Implement `02-categorize.py` with rules engine, site clustering, and LLM classification
- Create `rules.yaml` and `tag-vocabulary.yaml` with seed rules
- Add proposal read model and accept/reject actions to the CLIM UI
- Add a `--output yaml` default for the `get` command (table output is too wide)
- Test query performance with the full 13,848-document dataset
- Consider adding a Makefile target for the FTS5 build tag

## Project working rule

Every rendered semantic object must carry its type, identity, and capabilities. The UI must never guess what a row of data means — the API must tell it. Mutations must be visible, reviewable, and reversible. The action registry is the single source of truth for what can be done to what.
