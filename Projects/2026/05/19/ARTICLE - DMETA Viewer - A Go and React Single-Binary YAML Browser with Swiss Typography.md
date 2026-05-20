---
title: "DMETA Viewer: A Go + React Single-Binary YAML Browser with Swiss Typography"
aliases:
  - DMETA Viewer
  - DMETA YAML Viewer
tags:
  - article
  - go
  - react
  - rtk-query
  - tailwind
  - swiss-typography
  - yaml
  - dmeta
  - single-binary
status: active
type: article
created: 2026-05-19
repo: /home/manuel/workspaces/2026-05-19/dmeta-dsl/2026-05-19--dmeta-viewer
---

# DMETA Viewer: A Go + React Single-Binary YAML Browser with Swiss Typography

This article is a technical deep dive into building a self-contained Go + React application that renders structured YAML files as purpose-built information displays rather than raw text dumps. It covers the full stack: the Go backend that scans and serves YAML directories, the React frontend with custom artifact-type widgets, and the Swiss typography system that creates visual hierarchy through font weight and color instead of font size. The reference implementation is the DMETA Viewer, built to browse the DMETA Intermediate Representation YAML files, but the architecture applies to any directory of structured YAML documents.

> [!summary]
> 1. A Go binary embeds a pre-built React SPA via `go:embed`, scans a YAML directory at startup, and serves both the API and the SPA on a single port.
> 2. The frontend routes to custom widgets based on `artifact_type` — a `CapabilityCard` renders projections with middle-dot separators, a `PresentationCard` shows layer/role/density summary rows, and an `ArchetypeCard` presents capabilities and presentations as cross-reference token rows.
> 3. The typography system (Programme № 2) uses a single font at a single size (13px) and creates all hierarchy through weight (400 vs 700) and color (ink vs muted). There are no borders. Spacing, weight, and color do all the structural work.

## When to use this pattern

Use this Go + React single-binary approach when:

- you have a directory of structured YAML files that people need to browse, search, and cross-reference interactively
- you want the distribution to be a single executable with no external dependencies — the user points it at a directory and opens a browser
- the YAML files have internal cross-references (names that appear in one file referring to entities defined in another) that should be navigable
- the data has enough structure that a raw key-value dump wastes the reader's time — capabilities have projections, archetypes have capabilities, presentations have interaction affordances

Do not use this pattern when:

- you only need a static site generator — there are simpler tools for that
- the YAML files are flat key-value stores with no internal relationships
- you need write/edit operations on the YAML — this viewer is read-only
- the dataset is so large that scanning at startup is impractical (the scanner reads every file once at launch)

## Architecture

The system has three layers: a Go backend that provides the API, a React SPA that provides the UI, and an embedding layer that packages them into a single binary.

```mermaid
graph TD
    subgraph Go Binary
        A[main.go<br/>CLI: --dir --port] --> B[scanner.Scan<br/>Walk + index YAML]
        B --> C[api.Handler<br/>GET /api/index<br/>GET /api/files/:id<br/>GET /api/search]
        C --> D[yamlutil.ParseToJSON<br/>YAML → interface{}]
    end

    subgraph React SPA
        E[apiSlice<br/>RTK Query] --> F[YamlViewer<br/>artifact_type router]
        F --> G[CapabilityCard]
        F --> H[PresentationCard]
        F --> I[ArchetypeCard]
        F --> J[SectionView<br/>generic fallback]
    end

    subgraph Embedding
        K["//go:embed frontend/dist"] --> L[http.FileServer<br/>serves SPA on /]
    end

    C -->|JSON| E
    L -->|HTML/JS/CSS| Browser
```

During development, Vite runs on port 5173 with hot module replacement and proxies `/api` requests to the Go server on port 8080. For production, `npm run build` compiles the SPA into `frontend/dist/`, and `go build` embeds that directory into the binary. The result is one executable that serves everything.

## The Go backend

### Scanner: building the file index

The scanner walks the configured directory at startup, reads every `.yaml` and `.yml` file, and builds an in-memory index. It does not parse the full YAML structure at scan time — it only reads enough to extract the `artifact_type` and `summary` fields, which appear near the top of every DMETA IR file.

This partial-parse approach is deliberate. Full YAML parsing is expensive when the directory contains large files with deeply nested structures. The scanner only needs enough metadata to build the sidebar tree and route to the correct widget. The full parse happens on demand when a user requests a specific file.

```go
type FileEntry struct {
    ID           string      // URL-safe slug from relative path
    Name         string      // filename without extension
    Path         string      // relative path from --dir root
    ArtifactType string      // value of "artifact_type" field
    Summary      string      // value of "summary" field
    Children     []FileEntry // sub-files for directory groupings
    IsDir        bool        // true for directory group entries
}
```

The scanner produces two data structures from this walk: a tree (for the sidebar, grouped by directory) and a flat map from ID to absolute path (for O(1) file lookups when the API receives a request). The slugify function converts relative paths into URL-safe IDs: `core-model/archetypes.yaml` becomes `core_model_archetypes`.

### API: three endpoints

The API uses Go 1.22's new `ServeMux` route patterns with `r.PathValue("id")`, which is cleaner than manual string trimming:

| Method | Pattern | Response |
|--------|---------|----------|
| `GET` | `/api/index` | Full file tree with metadata |
| `GET` | `/api/files/{id}` | Parsed YAML content as JSON |
| `GET` | `/api/search?q=...` | Search across file names and summaries |

The file endpoint returns two things: the file metadata (name, artifact type, summary) and the full parsed YAML data as a generic `interface{}`. The `gopkg.in/yaml.v3` library produces `map[string]any` for YAML mappings, which serializes directly to JSON. This means the Go backend never needs to know the schema of any YAML file — it is a transparent YAML-to-JSON converter.

### Embedding the SPA

The `main.go` file declares an embed directive:

```go
//go:embed frontend/dist
var frontendFS embed.FS
```

At runtime, `fs.Sub(frontendFS, "frontend/dist")` creates a subtree that `http.FileServer` serves on `/`. This is the standard Go pattern for single-binary web applications. The SPA's `index.html` is served for all unmatched routes (client-side routing), and the API routes take precedence because they are registered first.

## The React frontend

### RTK Query for server state

The API slice defines three endpoints that map directly to the Go handlers:

```javascript
export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  endpoints: (builder) => ({
    getIndex: builder.query({ query: () => '/index' }),
    getFile: builder.query({ query: (id) => `/files/${id}` }),
    searchFiles: builder.query({ query: (q) => ({ url: '/search', params: { q } }) }),
  }),
});
```

RTK Query handles caching, loading states, and refetching automatically. The `getFile` hook caches by file ID, so navigating back to a previously visited file is instant. The `useGetIndexQuery` hook runs once at app load and provides the data for the sidebar tree.

### Artifact-type routing: the key design decision

The most important architectural choice in the frontend is the `YamlViewer` component's routing logic. When the API returns file data, it includes the `artifact_type` field. The viewer checks this field and routes to the appropriate custom widget:

- `dmeta_archetypes` → `ArchetypeCard` per archetype
- `dmeta_capabilities` → `CapabilityCard` per capability
- `dmeta_presentations` → `PresentationCard` per presentation, grouped by layer
- everything else → generic `SectionView` (recursive key-value rendering)

This routing is what separates an information-design tool from a generic YAML viewer. A capability is not a flat map — it has projections (typed fields with required/optional semantics), presentations (named display contracts), actions (operations), and filters (query predicates). Rendering these as a key-value grid loses the structural relationships. The custom widget preserves them.

## Custom widgets

### CapabilityCard: projections with middle-dot separators

A capability's projections are its most structured content. Each projection has a name, a type, a required flag, and a description. The `CapabilityCard` renders these as inline rows with middle-dot (`·`) separators:

```
id · string · req · Canonical stable id.
label · string · req · Primary display label.
subtitle · string · opt · Optional secondary label.
```

The separator is styled with `color: var(--faint)` so it stays visually quiet against the bold projection name and the muted description. The `req`/`opt` indicator uses bold weight for required and muted label style for optional, creating a clear distinction without adding borders, badges, or background colors.

Below the projections, cross-reference rows present the capability's presentations, actions, and filters as inline token lists. Presentations and actions use bold weight (they are navigable — clicking them jumps to the presentations file). Filters use muted weight (they are secondary information).

### PresentationCard: the summary row

A presentation has a layer (capability or archetype), a role (inline_code, badge, metric_cell, etc.), and a density (compact, any, spacious). These three properties form the "summary row" — a compact inline display that tells you what kind of presentation this is without reading the full description:

```
compact_id · capability · inline_code · compact
```

The summary row uses the `.label` role (muted, uppercase, tracked) for all three parts, separated by middle-dots. This is intentionally less prominent than the projection rows in the CapabilityCard — presentations are leaf nodes in the cross-reference graph, and their most important information is the name and the summary, not the detailed field list.

The `applies_to` section shows which archetypes or capabilities a presentation serves, rendered as cross-reference tokens. The `requires` and `optional` sections list the projection names that the presentation needs. The `interaction` section shows affordance flags (select, copy, menu) as compact label tokens.

### ArchetypeCard: capabilities and presentations as token rows

An archetype is simpler than a capability or presentation. It has a name, a description, a list of default capabilities, a list of recommended presentations, and a list of domain examples. The `ArchetypeCard` renders the capabilities and presentations as bold cross-reference tokens (clicking navigates to the corresponding file) and the examples as muted tokens (they are concrete domain types, not cross-references within the IR).

The long description is rendered as muted prose below the token rows, capped at `max-width: 72ch` for comfortable reading.

### CrossRef: the shared navigation component

All three widgets use the `CrossRef` component for rendering values that might correspond to files in the index. `CrossRef` accepts a `tone` prop (`bold` or `muted`) and checks the index data to see if the value matches a known file name. If it does, the token is rendered as a clickable link with a dotted underline. If not, it renders as plain text with the specified tone.

The matching heuristic normalizes both the token value and the file names by lowercasing and stripping underscores, spaces, and hyphens. This handles the common case where a YAML key says `identifiable` and the corresponding file is named `capabilities.yaml` — the cross-reference is file-level, not section-level, so navigating to the capabilities file is the right behavior.

## Programme № 2: the typography system

### Why not use font size for hierarchy?

The DMETA Viewer initially used Programme № 1, which had two sizes: 13px for body text and 28px for display headers. This is the standard web approach — make important things bigger. But the DMETA data is dense and deeply nested. When every section header is 28px, the page becomes a sequence of visual cliffs. The reader's eye jumps between large headers and small body text, and the intermediate structure (archetype names, capability names, projection names) has no natural place in the size hierarchy.

The alternative, drawn from the `log-presentation-based-ui` project, is to keep everything at 13px and create hierarchy through two other channels: font weight and color.

### The five roles

Programme № 2 defines five CSS classes, all at 13px:

| Role | Weight | Color | Transform | Tracking | Used for |
|------|--------|-------|------------|----------|----------|
| `.body` | 400 | ink | none | 0 | Default reading text, descriptions, values |
| `.label` | 400 | muted | uppercase | 0.06em | Structural chrome: field names, column headers, section labels |
| `.bold` | 700 | ink | none | 0 | Primary data: archetype names, projection names, status tokens |
| `.boldcap` | 700 | ink | uppercase | 0.08em | Section headers: file names, archetype section names, layer group headers |
| `.caption` | 400 | ink | uppercase | 0.06em | Emphasized inline labels |

The scan path this creates is: bold/boldcap first (weight 700 draws the eye), then body text (ink color is high contrast), then labels (muted color recedes). The reader scans a capability card by seeing `IDENTIFIABLE` (boldcap), then `id · string · req` (bold + label), then the description (body, muted), then the cross-reference tokens (bold or muted depending on importance).

### Why this works for structured data

Structured YAML has a characteristic that plain prose does not: the same hierarchical level appears many times on a page. A capabilities file contains fifteen capabilities, each with three to six projections. If each capability name were 28px, the page would be mostly header. At 13px with bold weight, fifteen capability names stack compactly while remaining scannable. The weight difference (400 vs 700) is enough to distinguish names from descriptions, and the color difference (ink vs muted) is enough to distinguish data from structure.

### No borders

The viewer uses no borders on any content element. This is a direct consequence of the weight+color hierarchy. Borders exist to create visual grouping when typography cannot do it alone. When bold names, muted labels, and consistent spacing already define the card boundaries, borders become redundant visual noise. The space between cards (32px margin-bottom), the consistent internal spacing (8-10px between sections), and the weight transitions (boldcap → body → label → bold) create enough structure that borders would add nothing.

The one exception is the `yaml-nested` class used in the generic `SectionView`, which has a 2px left border in `var(--faint)` to indicate nesting depth. This is a structural cue for deeply nested fallback rendering, not a decorative border.

## The build and run workflow

### Development mode

Two servers run simultaneously. Vite serves the React SPA on port 5173 with hot module replacement, and the Go server provides the API on port 8080. Vite's proxy configuration forwards `/api` requests:

```javascript
// vite.config.js
export default defineConfig({
  server: {
    proxy: { '/api': 'http://localhost:8080' },
  },
});
```

Run them in separate terminals:

```bash
# Terminal 1
cd 2026-05-19--dmeta-viewer && GOWORK=off go run . --dir ../dmeta/sources/dmeta-ir --port 8080

# Terminal 2
cd 2026-05-19--dmeta-viewer/frontend && npm run dev
```

The `GOWORK=off` flag is necessary because this repository lives inside the dmeta-dsl workspace, which has a `go.work` file. Without the flag, Go tries to resolve the module through the workspace and fails.

### Production mode

```bash
make build
./bin/dmeta-viewer --dir /path/to/yaml/dir --port 8080
```

The Makefile runs `npm install && npm run build` in the frontend directory, then `go build` with the `frontend/dist` directory embedded. The resulting binary is self-contained — no Node.js runtime, no external web server, no configuration files. Point it at any directory of YAML files and open the listed URL.

### Pointing at a different directory

The viewer is not DMETA-specific. Any directory of YAML files will work. The custom widgets only activate for known `artifact_type` values; unknown types fall back to the generic `SectionView`. This means you can use the viewer as a general-purpose YAML browser for any project:

```bash
./bin/dmeta-viewer --dir ./my-kubernetes-manifests --port 3000
```

## Failure modes and design traps

### The go.work conflict

The most likely failure when building is a `go.work` conflict. If the viewer repository is inside a Go workspace (as it is in the dmeta-dsl monorepo), `go build` will fail with "current directory is contained in a module that is not one of the workspace modules." The fix is `GOWORK=off`, which tells Go to ignore the workspace file and treat the module as standalone.

### Cross-reference false positives

The `CrossRef` matching heuristic normalizes names by lowercasing and stripping separators. This can produce false positives for short names. For example, a YAML value of `in` (a filter operator) could match a file named `in.yaml` if one existed. The current implementation accepts this trade-off because false positives are rare in the DMETA IR (file names are descriptive), but a production system would need a more precise matcher — perhaps a two-pass approach that first collects all known entity names from within files, then matches against that expanded index.

### Deeply nested fallback rendering

The generic `SectionView` handles arbitrary YAML nesting, but its readability degrades past three levels of indentation. The DMETA capabilities file has projections that contain objects (type, required, description), which is three levels deep. Files with five or more levels would benefit from a collapsible tree view rather than the current flat recursion.

## Implementation details

### File inventory

The project has five commits and approximately 1,500 lines of source code (not counting the auto-generated `package-lock.json` and `go.sum`):

| File | Lines | Purpose |
|------|-------|---------|
| `main.go` | 49 | CLI entry point, embed directive, HTTP server |
| `internal/scanner/scanner.go` | 191 | Directory walker, metadata extractor, index builder |
| `internal/api/handler.go` | 71 | Three API endpoints with Go 1.22 route patterns |
| `internal/yamlutil/yamlutil.go` | 30 | YAML-to-JSON transparent converter |
| `frontend/src/features/viewer/YamlViewer.jsx` | 254 | Artifact-type router, file header, view components |
| `frontend/src/features/viewer/CapabilityCard.jsx` | 126 | Projection rows, cross-reference rows |
| `frontend/src/features/viewer/PresentationCard.jsx` | 136 | Summary row, applies_to, interaction |
| `frontend/src/features/viewer/ArchetypeCard.jsx` | 69 | Token rows for capabilities/presentations/examples |
| `frontend/src/features/viewer/CrossRef.jsx` | 51 | Shared cross-reference navigation token |
| `frontend/src/styles/programme.css` | 114 | Programme № 2: tokens, roles, base styles |
| `frontend/src/styles/components.css` | 265 | Borderless layout, card classes, sidebar, search |

### Git history

```
58455eb feat: Programme № 2 typography + custom widgets
7fdfc0c fix: Go 1.22 PathValue routing, suppress duplicate headers
a79b648 feat: Storybook stories
34d0408 feat: React SPA with Swiss typography, RTK Query, YamlViewer
060c358 feat: scaffold Go project with scanner, api, yamlutil
```

### Key commands

```bash
# Build and run
GOWORK=off go run . --dir ../dmeta/sources/dmeta-ir --port 8080

# Verify API
curl localhost:8080/api/index | jq '.files | length'
curl localhost:8080/api/files/core_model_archetypes | jq '.file.artifact_type'

# Frontend only (dev)
cd frontend && npm run dev

# Build production binary
make build && ./bin/dmeta-viewer --dir ../dmeta/sources/dmeta-ir
```

## Working rules

- Everything is 13px. Do not introduce a new font size. If something needs emphasis, use weight or color.
- No borders on content elements. If you feel the need for a border, add spacing instead.
- Custom widgets for known artifact types. Do not add special cases to the generic `SectionView` — add a new card component and register it in `YamlViewer`.
- Cross-references are file-level, not section-level. Clicking `identifiable` navigates to the capabilities file, not to the `identifiable` section within it. Section-level anchoring is a future improvement.
- The Go backend is a transparent YAML-to-JSON pipe. Do not add schema knowledge to the backend — that belongs in the frontend widgets.
- Use `GOWORK=off` when building inside the dmeta-dsl workspace.
