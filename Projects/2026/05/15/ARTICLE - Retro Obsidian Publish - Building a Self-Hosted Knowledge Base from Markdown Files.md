---
title: "Retro Obsidian Publish — Building a Self-Hosted Knowledge Base from Markdown Files"
aliases:
  - Retro Obsidian Publish Technical Deep Dive
  - Building a Markdown Publishing Engine in Go and React
tags:
  - article
  - go
  - react
  - obsidian
  - publishing
  - fullstack
  - goldmark
  - bleve
status: active
type: article
created: 2026-05-15
repo: /home/manuel/code/wesen/2026-05-13--retro-obsidian-publish
---

# Retro Obsidian Publish — Building a Self-Hosted Knowledge Base from Markdown Files

This article is a technical deep dive into Retro Obsidian Publish, a single-binary web application that turns a folder of Obsidian Markdown files into a searchable, linkable, self-hosted website. It covers the architecture end to end: how the Go backend parses Markdown and resolves wiki links, how the search index works, how the React frontend renders notes with live navigation, and how the whole system fits into a deployment pipeline.

The target audience is someone building a publishing engine for structured text who wants to understand the design decisions, not just the API surface. Each section explains why a choice was made before showing what it produces.

> [!summary]
> - The vault is a read-only data source. The server builds an in-memory index at load time and serves it through a JSON API. There is no database.
> - Wiki-link resolution uses a suffix-based index so that `[[App-Auth]]` can resolve to `Research/KB/Tribal/App-Auth.md` without the author writing the full path.
> - The frontend is a React SPA that fetches all data from the API. It has no build-time knowledge of the vault contents.
> - The production artifact is one Go binary with the React app embedded via `go:embed`.

## When this architecture is the right choice

Use a single-binary publishing engine when:

- your content lives as Markdown files in a directory and you want a website without a static-site generator's build step
- you need full-text search, backlink computation, and wiki-link resolution at request time, not as a pre-computed artifact
- you want to update content by changing files on disk (or pulling a Git repository) and have the site reflect changes immediately
- you want one deployment artifact: a binary that serves both the API and the frontend

Do not use this architecture when:

- you need multi-user writes or collaboration — the server treats the vault as read-only
- you need a database for structured queries beyond text search
- your content is not Markdown (the parser is purpose-built for Obsidian-flavored Markdown)

## Repository layout

The project has two major directories with clear ownership boundaries.

```text
retro-obsidian-publish/
├── backend/                         # Go module: API server + CLI
│   ├── cmd/retro-obsidian-publish/  # Cobra CLI entry point
│   ├── internal/
│   │   ├── parser/                  # goldmark pipeline, wiki-link extraction
│   │   ├── vault/                   # vault loader, slugs, backlinks, tree
│   │   ├── search/                  # Bleve full-text search index
│   │   ├── api/                     # HTTP handlers for /api/*
│   │   ├── server/                  # HTTP server, runtime state, reload
│   │   ├── watcher/                 # fsnotify file watcher
│   │   └── web/                     # SPA static file handler + go:embed
│   └── vault-example/               # Small demo vault
├── web/                             # React/Vite SPA
│   ├── src/components/              # UI components (atoms, molecules, organisms, pages)
│   ├── src/store/                   # RTK Query API layer, Redux UI state
│   ├── src/vault/                   # Static demo vault for standalone builds
│   └── src/index.css                # Design system tokens and component styles
└── ttmp/                            # Ticket documentation (docmgr)
```

The boundary is strict: the backend owns all data processing and serves JSON. The frontend owns all rendering and makes zero assumptions about the vault contents. They communicate exclusively through the `/api/*` endpoints.

## The publishing pipeline

The system has two phases: load time and request time.

### Load time: building the in-memory vault

When the server starts, it walks the vault directory, parses every `.md` file, and builds four data structures in memory.

```text
Markdown files on disk
  → parser.Parse (goldmark + custom transformers)
  → Note objects (slug, title, frontmatter, HTML, wiki links)
  → wiki-link suffix index (short paths → full slugs)
  → backlink computation (reverse link graph)
  → HTML re-render with resolved link targets
  → Bleve search index
```

Each step depends on the previous one, and the order matters. Wiki links cannot be resolved until every note has been parsed and indexed, because the target of `[[Some Note]]` might be defined later in the walk. Backlinks cannot be computed until wiki links are resolved, because the reverse graph needs the final targets. HTML cannot be re-rendered with correct link URLs until resolution is complete.

This is why the pipeline runs in sequence, not in parallel. The total load time for a vault of 500 notes is under a second on modern hardware. For the typical personal knowledge base (50–200 notes), the load is imperceptible.

### Request time: serving from the snapshot

Once the vault is loaded, API handlers read from the prepared state. A `GET /api/notes/epistemology` request does not parse Markdown. It looks up the slug in a `map[string]*Note`, serializes the pre-rendered HTML, and returns JSON. This keeps page loads fast — the expensive work happened once at startup.

The server holds a single `Vault` object and a single `search.Index` object in memory. Both are protected by a `sync.RWMutex`, so concurrent reads (normal page loads) proceed without contention. Writes happen only during initial load or an administrative reload.

## Parsing: goldmark with custom extensions

The parser (`backend/internal/parser/parser.go`) converts raw Markdown bytes into a `ParsedNote` containing frontmatter, HTML, extracted wiki links, tags, title, and excerpt.

### The goldmark pipeline

The Markdown rendering uses goldmark, a CommonMark-compatible Markdown parser for Go, with several extensions:

| Extension | Purpose |
|---|---|
| `goldmark-meta` | YAML frontmatter extraction |
| `extension.GFM` | GitHub-Flavored Markdown (tables, task lists, strikethrough) |
| `extension.Table` | Pipe-delimited tables |
| `extension.TaskList` | `- [ ]` and `- [x]` checkboxes |
| `extension.Footnote` | `[^1]` footnote syntax |

The pipeline configures goldmark with `html.WithUnsafe()` to allow raw HTML pass-through — this is necessary because wiki links are replaced with HTML anchor tags before goldmark sees the content.

### Wiki-link extraction

Obsidian wiki links follow several patterns that the parser must handle:

```markdown
[[Note]]             → link to "Note"
[[Folder/Note]]      → link with path
[[Note|Display]]     → link with alias
[[Note#Heading]]     → link with heading anchor
![[Note]]            → embed (transclusion)
```

The parser extracts wiki links using a regex before goldmark processes the Markdown. This two-pass approach exists because goldmark's AST does not understand `[[brackets]]` as link syntax. The regex finds all `[[...]]` and `![[...]]` patterns, records them as `WikiLink` structs (target, alias, embed flag, heading), and replaces them with HTML anchor placeholders that goldmark will pass through unchanged.

```
Input:  "See [[Tribal/App-Auth]] for details."
Output: 'See <a href="/note/tribal/app-auth" class="wiki-link" 
              data-target="tribal/app-auth">Tribal/App-Auth</a> for details.'
```

The `data-target` attribute preserves the original slugified target. The `data-raw` attribute preserves the original text the author wrote. Both are used during the link resolution phase.

### Callout rendering

Obsidian callouts (`> [!type] Title`) are rendered by a post-processing step that finds goldmark's `<blockquote>` output and detects the `[!type]` prefix pattern. The transformer converts blockquotes into styled `<div class="callout">` elements with type-specific icons and optional collapsibility:

```go
var calloutRe = regexp.MustCompile(
    `<blockquote>\s*<p>\[!(\w+)\]([+-])?([\s\S]*?)</blockquote>`)
```

The `([+-])?` group captures the fold character: `-` means collapsed by default, `+` means expanded. The frontend adds a toggle button for collapsible callouts.

### Why two passes for wiki links

An alternative approach would register a goldmark AST transformer that walks the document tree and replaces text nodes containing `[[...]]` with link nodes. This is more architecturally correct — it keeps all transformation inside goldmark's pipeline.

The regex approach was chosen for three reasons:

1. **Simplicity.** The regex handles all five wiki-link forms in one pattern. An AST transformer would need to handle text node splitting, merge adjacent text nodes, and deal with inline context that goldmark's AST does not naturally expose for bracket syntax.

2. **Correctness with frontmatter.** Wiki links can appear inside YAML frontmatter (for example, `Related: "[[Some Note]]"`). Replacing them inside frontmatter would corrupt the YAML. The parser explicitly splits frontmatter from the body before doing regex replacement, which is simpler than teaching an AST transformer to ignore the metadata block.

3. **Provenance.** The regex approach preserves the original raw target in a `data-raw` attribute, which the vault loader uses during the resolution phase. An AST transformer would lose this information unless explicitly wired to retain it.

## The vault loader and wiki-link resolution

The vault loader (`backend/internal/vault/vault.go`) is the core data structure. It owns the note map, the wiki-link resolution index, and the backlink graph.

### Slug generation

Every note gets a slug derived from its file path relative to the vault root:

```text
Research/KB/Tribal/App-Auth.md → "research/kb/tribal/app-auth"
Philosophy/Stoicism.md         → "philosophy/stoicism"
Index.md                       → "index"
```

Slugs are lowercase, use hyphens for spaces and special characters, and strip the `.md` extension. They serve as the URL path component and the primary key in the note map.

### Suffix-based wiki-link resolution

Obsidian users write links using short paths. A note might contain `[[App-Auth]]` when the actual file lives at `Research/KB/Tribal/App-Auth.md`. The vault loader builds a suffix index that maps every possible suffix of each note's path to the full slug:

```text
File: Research/KB/Tribal/App-Auth.md

Registered suffixes:
  "research/kb/tribal/app-auth"  (full path)
  "kb/tribal/app-auth"
  "tribal/app-auth"
  "app-auth"                      (filename only)
  "app-auth"                      (title slug, if different)
```

When two notes share the same short suffix (for example, `Index.md` exists in multiple folders), the first note registered wins. The suffix index is a `map[string]string`, so lookup is O(1). The trade-off is that ambiguous short names resolve to whichever note the filesystem walker encountered first. The resolution is deterministic for a given vault state, but authors should use more specific paths when their vault has name collisions.

The `buildWikiLinkIndex` method iterates over all notes, computes every suffix of each note's path, and registers them. The implementation splits the path into segments and progressively shortens from the front:

```go
parts := strings.Split(filepath.ToSlash(note.Path), "/")
for i := len(parts) - 2; i >= 0; i-- {
    shortPath := strings.Join(parts[i:], "/")
    shortPath = strings.TrimSuffix(shortPath, ".md")
    suffixes = append(suffixes, parser.Slugify(shortPath))
}
```

### Backlink computation

Backlinks are the reverse of the wiki-link graph. If note A contains `[[B]]`, then B's backlinks include A. The computation happens after wiki-link resolution because it needs the final resolved targets.

```go
func (v *Vault) buildBacklinks() {
    for _, n := range v.notes {
        n.Backlinks = []string{}  // Reset to empty slice, not nil
    }
    for slug, note := range v.notes {
        for _, wl := range note.WikiLinks {
            resolved, ok := v.ResolveWikiLink(wl.Target)
            if !ok { continue }
            if target, ok := v.notes[resolved]; ok {
                target.Backlinks = appendUnique(target.Backlinks, slug)
            }
        }
    }
}
```

The `appendUnique` guard prevents duplicates when a note links to the same target multiple times. The initialization to `[]string{}` rather than `nil` ensures that JSON serialization produces `[]` instead of `null` for notes with no backlinks — a small detail that prevents null-checking on the frontend.

### HTML re-rendering

After wiki-link resolution, every note's HTML is re-rendered to replace placeholder slug targets with the resolved full slugs. This is a string replacement pass over the pre-rendered HTML, not a re-parse of the Markdown. The `ReplaceWikiLinksString` function uses regex to swap `data-target` and `href` attributes:

```go
note.HTML = parser.ReplaceWikiLinksString(note.HTML, func(target string) string {
    if resolved, ok := v.wikiLinkIndex[target]; ok {
        return resolved
    }
    return target
})
```

A second pass replaces display text. When a wiki link has no alias, the display text is replaced with the target note's title:

```go
note.HTML = parser.ReplaceWikiLinkDisplay(note.HTML, func(slug string) string {
    if n, ok := v.notes[slug]; ok { return n.Title }
    return ""
})
```

This means `[[tribal/app-auth]]` renders as `<a href="/note/research/kb/tribal/app-auth">App Auth</a>` — the user sees the note's actual title, not the path they typed.

## Full-text search with Bleve

The search index (`backend/internal/search/search.go`) wraps Bleve, a full-text search library for Go. It creates an in-memory index and loads every note as a document with four fields:

| Field | Stored | Analyzed | Purpose |
|---|---|---|---|
| `title` | Yes | Yes (standard analyzer) | Matches on note titles |
| `body` | No | Yes (standard analyzer) | Matches in full content |
| `tags` | Yes | Yes (standard analyzer) | Matches on tag names |
| `excerpt` | Yes | No | Returned in search results |

The body field is analyzed but not stored. This means Bleve builds a term index for the content but does not keep the original text in the index. When a search hit is returned, the excerpt comes from the stored `excerpt` field, not from re-reading the body.

### Query strategy

The search function adapts its strategy based on query length:

- **Short single words (≤3 characters)**: prefix query. Searching for `"goj"` becomes `goj*`, matching `goja`, `gojobs`, etc.
- **Longer or multi-word queries**: fuzzy match queries with fuzziness 1. This handles typos (`"obsidan"` matches `"obsidian"`) and partial matches. Multiple words are combined with a conjunction (AND) query.

The fuzzy approach trades precision for recall. In a personal knowledge base, the user often remembers part of a term but not the exact spelling. A fuzzy match with distance 1 covers the most common typo patterns without producing excessive false positives on a small corpus.

### Why not a database

The vault typically contains tens to hundreds of notes, not millions. An in-memory Bleve index handles this scale with sub-millisecond query times. Adding a database (SQLite, PostgreSQL) would introduce operational complexity (file permissions, schema migrations, backup) without meaningful performance benefit. The index is rebuilt from scratch on every vault reload, which takes under a second for typical vaults. If the vault grows to tens of thousands of notes, the rebuild time would need optimization, but the current architecture handles the common case well.

## The API layer

The API (`backend/internal/api/api.go`) is a set of HTTP handlers that read from the vault snapshot. The design is intentionally thin — each handler does one thing:

| Endpoint | What it returns |
|---|---|
| `GET /api/config` | Site configuration (vault name, note count) |
| `GET /api/notes` | Lightweight list of all notes (slug, title, tags, excerpt) |
| `GET /api/notes/{slug}` | Full note with HTML, frontmatter, wiki links, backlinks |
| `GET /api/tree` | Hierarchical folder tree for sidebar navigation |
| `GET /api/search?q=...` | Full-text search results with scores |
| `GET /api/tags` | All tags with counts |
| `GET /api/healthz` | Server health, note count, vault paths |
| `POST /api/admin/reload` | Administrative vault reload (auth-gated) |

The handlers access the vault through a `SnapshotProvider` interface:

```go
type SnapshotProvider interface {
    Snapshot() (*vault.Vault, *search.Index)
}
```

This interface enables atomic vault swaps during reloads. The server creates a new `Vault` and `Index`, and the `RuntimeState` swaps both pointers under a write lock. Ongoing requests continue reading from the old snapshot until they call `Snapshot()` again, at which point they get the new state. There is no point where a request sees a partially-loaded vault.

### The config endpoint

The `/api/config` endpoint returns the vault display name and the current note count:

```json
{
  "vaultName": "My Research Institute",
  "notes": 142
}
```

The vault name is configurable via the `--vault-name` CLI flag. When omitted, it defaults to the basename of the vault directory. This endpoint exists so the frontend can display the correct name without hardcoding it at build time. The same binary can serve different vaults with different names, which matters for multi-vault deployments.

## The frontend architecture

The frontend is a React application built with Vite. It uses RTK Query for data fetching and Redux for UI state (sidebar open/closed, active note, search query).

### Component hierarchy

```text
App
 └── Router (wouter)
      └── VaultLayout (page)
           ├── Header/Menubar (responsive)
           ├── Sidebar (organism)
           │    ├── SearchBar (molecule)
           │    └── FileTreeItem (molecule, recursive)
           └── children (route content)
                ├── NotePage (page)
                │    ├── NoteRenderer (organism)
                │    │    ├── Prose HTML rendering
                │    │    ├── Syntax highlighting (highlight.js)
                │    │    ├── Mermaid diagrams
                │    │    └── Wiki embeds
                │    └── BacklinksPanel (organism, desktop) or inline section (mobile)
                ├── SearchPage (page)
                └── HomeRedirect (auto-selects home note)
```

The component tree follows an atomic design pattern: atoms (Icon, ScrollArea), molecules (SearchBar, FileTreeItem), organisms (Sidebar, NoteRenderer), and pages (VaultLayout, NotePage). Each layer composes the layer below it.

### RTK Query and the API slice

All API communication goes through a single RTK Query API slice (`web/src/store/vaultApi.ts`). The slice defines endpoints for each API route and auto-generates React hooks:

```typescript
export const { useGetConfigQuery, useGetNoteQuery, useListNotesQuery,
               useGetTreeQuery, useSearchQuery, useListTagsQuery } = vaultApi;
```

RTK Query handles caching, deduplication, and loading states. When `useGetNoteQuery("epistemology")` is called, RTK Query checks if the data is already in the cache. If it is, the hook returns immediately with the cached data. If not, it fires the API request and tracks `isLoading` and `isError` states.

### Static demo mode

The frontend can operate without a backend. When `VITE_STATIC_VAULT=true` is set at build time, the RTK Query endpoints use `queryFn` instead of `query`:

```typescript
getConfig: builder.query<SiteConfig, void>(
  IS_STATIC
    ? { queryFn: async () => ok(staticGetConfig()) }
    : { query: () => "/api/config" }
),
```

The static vault module (`web/src/vault/staticVault.ts`) imports all Markdown files via Vite's `import.meta.glob` with the `?raw` query, parses them in the browser with `js-yaml` and `marked`, and builds the same data structures the backend would produce. This mode enables standalone demos and static deployments where no Go server is available.

### The NoteRenderer

The `NoteRenderer` component receives pre-rendered HTML from the API and enhances it on the client side:

- **Syntax highlighting**: highlight.js scans `<pre><code>` blocks and adds language-specific token classes.
- **Mermaid diagrams**: the Mermaid library replaces `<code class="language-mermaid">` blocks with rendered SVG diagrams.
- **Wiki embeds**: `<div class="wiki-embed" data-target="slug">` elements are replaced with the content of the referenced note, fetched via `useGetNoteQuery`.
- **Copy buttons**: each `<pre>` block gets an absolutely-positioned copy button that appears on hover.
- **Heading anchors**: each heading gets a `#` permalink that copies the direct link URL.

Client-side enhancement was chosen over server-side rendering for these features because they require browser APIs (clipboard, DOM measurement for Mermaid sizing) or benefit from progressive enhancement (highlighting loads after the text is visible).

## The retro design system

The visual language is based on Macintosh System 1 (1984): monochrome ink on aged paper, hard 1px borders, zero border-radius, and system-ui typography.

### Design tokens

The design system is expressed as CSS custom properties in `web/src/index.css`:

```css
:root {
  --background: #f0ede8;         /* aged paper */
  --foreground: #1a1a1a;         /* near-black ink */
  --color-link: #0000cc;         /* Mac link blue */
  --color-tag: #005500;          /* forest green */
  --color-destructive: #cc0000;  /* deep red */
  --radius: 0px;                 /* no rounded corners */
}
```

The color palette has three functional accents: blue for links and active states, green for tags, red for destructive actions. These are the only non-monochrome colors. Everything else is black, white, or gray.

### Component classes

The CSS uses a layered approach with Tailwind CSS v4's `@layer` directive:

- **`@layer base`**: resets, typography, scrollbar styling, link behavior, heading styles.
- **`@layer components`**: retro window chrome (`.retro-window`), menubar (`.retro-menubar`), tree items (`.retro-tree-item`), search input (`.retro-search`), note prose (`.note-prose`), callouts, badges, code blocks.

The component layer provides the retro aesthetic. The base layer provides readable typography. Tailwind utilities handle layout (flex, grid, spacing, responsive breakpoints).

### Why not a component library

The retro aesthetic requires precise control over borders, shadows, and typography that would require extensive overrides on a component library like shadcn/ui or Radix. Instead, the project uses a small set of hand-written CSS component classes combined with Tailwind utilities. The component classes define the look; Tailwind handles layout and spacing. This separation keeps the design tokens in one place and makes the retro aesthetic easy to adjust (change `--radius: 0px` to `--radius: 4px` and the entire app softens).

## Mobile responsive layout

The desktop layout uses three resizable columns: sidebar (20%), content (55%), and backlinks panel (25%). On viewports narrower than 768px, this three-column layout collapses.

### Design decisions

The mobile layout follows three principles:

1. **One thing at a time.** The user sees the note content. Everything else is one tap away.
2. **No resize handles.** Touch targets for drag handles are too small on mobile.
3. **Single scroll.** One scrollable region — the note body. Secondary content (backlinks) renders inline below the note.

### Implementation

The mobile layout uses viewport-aware state initialization and separate rendering trees:

```typescript
// uiSlice.ts — sidebar closed by default on mobile
const initialState = {
  sidebarOpen: window.innerWidth >= 768,
  rightPanelOpen: window.innerWidth >= 768,
};
```

The `VaultLayout` component renders the sidebar as a fixed-position drawer on mobile:

```tsx
{sidebarOpen && (
  <div className="fixed inset-y-0 left-0 z-40 w-[80vw] max-w-[320px] md:hidden">
    <Sidebar ... />
  </div>
)}
```

The `NotePage` component renders two completely separate trees. On desktop, the right panel shows backlinks in a resizable column. On mobile, backlinks render as an inline section below the note body:

```tsx
return (
  <>
    <div className="hidden md:block h-full">{desktopLayout}</div>
    <div className="md:hidden h-full">{mobileLayout}</div>
  </>
);
```

This dual-tree approach avoids the complexity of conditionally composing a single tree. The `NoteRenderer` is stateless, so rendering it twice (once in each tree) has no side effects.

## CLI flags and configuration with Glazed

The server CLI uses Glazed, a command framework from the go-go-golems ecosystem, for schema-backed flag definitions. Each flag is declared as a `fields.Field` with a name, type, default, and help text:

```go
fields.New("vault-name", fields.TypeString,
    fields.WithDefault(""),
    fields.WithHelp("Display name for the vault in the web UI."),
),
```

Glazed generates Cobra flags from these field definitions. The `--config-file` flag comes built-in through `NewCommandSettingsSection()`, which allows users to write a YAML configuration file:

```yaml
command-settings:
  vault-name: "My Research Institute"
  vault: "/data/vaults/research"
  port: "8080"
```

CLI flags override the config file, which overrides defaults. This three-tier precedence (default → config file → CLI flag) is a standard pattern that Glazed provides without custom code.

## Deployment models

### Single binary (embedded frontend)

The production build compiles the React app into static assets and embeds them in the Go binary via `go:embed`:

```bash
go build -tags embed -o retro-obsidian-publish ./cmd/retro-obsidian-publish
```

The resulting binary serves the API and the frontend from the same process. No reverse proxy is required, though one can be added for TLS termination.

### Docker container

The Dockerfile builds the frontend in a Node.js stage and the Go binary in a Go stage, producing a minimal runtime image. The vault is mounted read-only:

```bash
docker run -p 8080:8080 -v /path/to/vault:/vault:ro \
  retro-obsidian-publish serve --vault /vault
```

### Kubernetes with Git-sync

For server deployments, the vault can be kept in a Git repository and synced to the container via `git-sync`. The server runs with `--watch=false` and exposes a reload endpoint:

```bash
RETRO_RELOAD_TOKEN=secret \
  retro-obsidian-publish serve \
  --vault /git/root/current \
  --watch=false \
  --reload-allow-loopback
```

A sidecar container pulls Git updates and calls `POST /api/admin/reload`. The reload endpoint builds a new vault and search index, validates them, and atomically swaps the active snapshot. If the reload fails, the old snapshot remains in service.

## Key design trade-offs

| Decision | Benefit | Cost |
|---|---|---|
| In-memory vault (no database) | Fast reads, simple deployment | Memory proportional to vault size; full rebuild on reload |
| Suffix-based link resolution | Short wiki links work without full paths | Ambiguous short names resolve to first match |
| Pre-rendered HTML at load time | API requests return immediately | HTML is not re-rendered on single-file update (full rebuild instead) |
| Static vault demo mode | Standalone frontend without backend | Demo data is baked into the frontend bundle |
| `go:embed` for frontend assets | Single binary deployment | Frontend changes require binary rebuild |
| Retro CSS design system | Consistent aesthetic, no component library overhead | Not a standard UI framework; custom classes need maintenance |

## What this project does not do

The system has intentional boundaries:

- **No write path.** The server never modifies vault files. It reads Markdown and produces JSON and HTML. Writing is done in Obsidian or any text editor.
- **No user authentication for reading.** The API is public. The only authenticated endpoint is the admin reload.
- **No real-time collaboration.** There is no WebSocket layer for multi-user editing. Content updates happen through file changes and reloads.
- **No plugin system.** The parser supports a fixed set of Markdown extensions. Adding new syntax requires changing the parser code.
- **No multi-vault serving.** One server process serves one vault. Multi-vault deployments run multiple processes behind a reverse proxy.

These boundaries keep the architecture simple. Each of them could be relaxed, but doing so would add complexity that the typical personal-knowledge-base use case does not require.

## File index

The most important source files, organized by subsystem:

| File | Role |
|---|---|
| `backend/internal/parser/parser.go` | Markdown parsing, wiki-link extraction, callout rendering |
| `backend/internal/vault/vault.go` | Note loading, slug generation, suffix index, backlinks, file tree |
| `backend/internal/search/search.go` | Bleve index, fuzzy search, result formatting |
| `backend/internal/api/api.go` | HTTP handlers, JSON serialization |
| `backend/internal/server/server.go` | HTTP server setup, CORS, health/reload endpoints |
| `backend/internal/server/runtime.go` | Atomic snapshot swap, reload logic |
| `web/src/store/vaultApi.ts` | RTK Query API slice, endpoint definitions |
| `web/src/App.tsx` | Router, config fetching, home note selection |
| `web/src/components/pages/NotePage/NotePage.tsx` | Note rendering, desktop/mobile layout split |
| `web/src/components/pages/VaultLayout/VaultLayout.tsx` | App shell, sidebar drawer, responsive menubar |
| `web/src/index.css` | Design system tokens, retro component styles, mobile overrides |
