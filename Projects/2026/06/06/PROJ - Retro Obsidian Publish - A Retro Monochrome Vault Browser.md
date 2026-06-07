---
title: "Retro Obsidian Publish"
aliases:
  - Retro Obsidian Publish
  - Retro Obsidian
  - Retro Vault
  - Retro Publish
  - Retro Publish Vault
tags:
  - project
  - obsidian
  - go
  - react
  - frontend
  - retro
  - static-site
  - single-binary
status: active
type: project
created: 2026-06-04
repo: /home/manuel/workspaces/2026-06-04/publish-vault-ssr/publish-vault
---

# Retro Obsidian Publish

Retro Obsidian Publish is a small self-hosted web application that turns an Obsidian vault directory into a publishable website. It reads Markdown files from a vault, builds an in-memory note index with wiki-link resolution and backlinks, and serves both a JSON REST API and a monochrome retro-styled React frontend from a single Go process.

> [!summary]
> Retro Obsidian Publish has three core identities:
> 1. a single-binary vault publisher with Obsidian wiki-link support and backlinks
> 2. a retro macOS System 1 visual design system for Obsidian content
> 3. a full SSR sidecar system with Node.js Express, RTK Query cache preloading, and React hydration

The project is a Go application with a React/Vite frontend, targeting people who want to publish a personal knowledge base without changing how they write notes. The vault directory remains the source of truth — the application treats it as read-only content and derives everything from it.

## Why this project exists

Obsidian is an excellent tool for writing and linking notes, but its built-in publish features are either too minimal (Obsidian Publish, $8/mo) or too heavy (self-hosting a full wiki engine). People who already maintain a rich Obsidian vault with thousands of linked notes and want to share a read-only mirror do not want to migrate away from Markdown + YAML frontmatter.

Retro Obsidian Publish fills that gap by treating the vault directory as a read-only data source and deriving a complete website from it: parsed HTML, wiki-link resolution, backlinks, search, and a file tree — all from one binary.

The retro monochrome aesthetic was chosen deliberately: it avoids the distraction of modern flat design and gives vault content a timeless, print-on-paper feel that matches how most people think about their personal knowledge base.

## Current project status

The project is in an active development phase. All core features are implemented and production-ready.

What is implemented:

### Backend (Go)
- A single Go binary built from `cmd/retro-obsidian-publish/` that serves both the API and the web frontend
- Vault loader: recursive `.md` file discovery, Goldmark parsing, frontmatter extraction, wiki-link resolution, backlink computation, and full-text search via Bleve
- JSON REST API: `/api/notes`, `/api/notes/{slug}`, `/api/tree`, `/api/search`, `/api/tags`, `/api/config`
- SPA static-file handler with server-side routing fallback
- Live filesystem watching with fsnotify (optional; disabled in git-sync deployments)
- Content reload endpoint (`POST /api/admin/reload`) for GitOps workflows
- Asset handling: vault images served via `/vault-assets/` with path resolution and URL escaping
- Docker build: multi-stage build with Go + Node.js + Alpine
- Kubernetes deployment manifests with ArgoCD and git-sync

### Frontend (React + Vite)
- A retro System 1 (1984 Macintosh) visual design system with monochrome ink-on-paper aesthetic
- File tree sidebar with hierarchical vault navigation
- Note rendering with syntax highlighting, Mermaid diagrams, collapsible callouts, and backlink panels
- Full-text search via RTK Query with debounced input
- Responsive layout: sidebar as off-canvas drawer on mobile, resizable panels on desktop
- Storybook with stories for all components
- Build pipeline: Vite build + SSR build producing client bundle and SSR bundle

### SSR (Server-Side Rendering) — added 2026-06-06
A complete SSR system for SEO and agent-readability:
- Node.js Express sidecar (`server.mjs`) that pre-fetches data from the Go API and renders React via `renderToString()`
- SSR entry point (`entry-server.tsx`) with RTK Query cache preloading using `upsertQueryData`
- Client entry (`entry-client.tsx`) with `createRoot()` for client-side takeover
- Go server reverse proxy with `--ssr-url` flag and SPA fallback on sidecar failure
- Dockerfile and docker-compose integration
- SEO: JSON-LD structured data, Open Graph tags, `<noscript>` fallback, `<title>` and meta descriptions

### Development tooling
- devctl plugin (`plugins/retro-obsidian-publish.py`) for local three-service orchestration (backend, web, SSR)
- docmgr ticket system for project tracking with design docs, implementation diaries, and reMarkable upload
- Dagger for containerized web builds (optional)
- GitOps with GitHub App credentials for PR automation and ArgoCD deployment

### Project documentation
- Comprehensive docmgr ticket (RETRO-SSR-009) with design documents, implementation diary, and phase-by-phase task tracking
- Detailed design doc covering architecture, decision records, pseudocode, and phased implementation plan
- Uploads to reMarkable for portable reference

## Project shape

The repository has a clean two-layer structure: a Go backend and a Vite-based React frontend.

```text
retro-obsidian-publish/
├── backend/                         # Go module (single binary)
│   ├── cmd/retro-obsidian-publish/   # CLI entrypoint
│   │   ├── main.go
│   │   └── commands/
│   │       ├── root.go
│   │       ├── build/
│   │       │   ├── root.go
│   │       │   └── web.go           # "build web" — Vite build + copy
│   │       ├── serve/
│   │       │   └── serve.go         # "serve" — Glazed-backed CLI
│   └── internal/
│       ├── api/                     # JSON REST API handlers
│       │   ├── api.go               # Handler, Register, endpoint types
│       │   └── api_test.go
│       ├── parser/                  # Markdown parsing with wiki-link support
│       │   ├── parser.go            # Goldmark pipeline + wiki-link extraction
│       │   └── parser_test.go       # Comprehensive parsing tests
│       ├── server/                  # HTTP server
│       │   ├── server.go            # Router, handlers, proxy, asset serving
│       │   ├── server_test.go
│       │   └── runtime.go           # RuntimeState: mutex-protected Vault + search index
│       ├── vault/                   # Vault loader and data models
│       │   ├── vault.go             # Note struct, file tree, backlinks, slug generation
│       │   └── vault_test.go
│       ├── search/                  # Bleve full-text search index
│       │   ├── search.go            # Index, persistent index, search with fuzzy matching
│       │   └── search_test.go
│       ├── watcher/                 # fsnotify-based file watching
│       │   ├── watcher.go
│       │   └── watcher_test.go
│       └── web/                     # SPA handler and embed support
│           ├── embed.go             # //go:build embed — embedded filesystem
│           ├── embed_none.go        # //go:build !embed — disk serving (dev)
│           ├── static.go            # SPAHandler: static files + index.html fallback
│           ├── generate.go          # go:generate runs "build web"
│           └── static_test.go
├── web/                              # React/Vite frontend
│   ├── public/
│   │   └── __manus__/               # Manus debug collector
│   ├── src/
│   │   ├── components/
│   │   │   ├── pages/
│   │   │   │   ├── VaultLayout/     # Main layout: menubar, sidebar, content pane
│   │   │   │   ├── NotePage/        # Note view with right-side backlinks panel
│   │   │   │   └── SearchPage/      # Search UI with debounced input
│   │   │   ├── organisms/
│   │   │   │   ├── Sidebar/         # File tree navigation
│   │   │   │   ├── NoteRenderer/    # Markdown rendering, Mermaid, syntax highlight
│   │   │   │   └── BacklinksPanel/  # Linked mentions sidebar
│   │   │   ├── molecules/           # BreadcrumbBar, SearchBar, NoteCard, etc.
│   │   │   ├── atoms/               # Badge, Checkbox, Divider, Tag, Icon, etc.
│   │   │   └── ui/                  # Radix UI primitives (shadcn-style)
│   │   ├── store/
│   │   │   ├── store.ts             # makeStore() factory + singleton
│   │   │   ├── vaultApi.ts          # RTK Query API slice (listNotes, getNote, etc.)
│   │   │   └── uiSlice.ts           # UI state: sidebar, right panel, search query
│   │   ├── hooks/
│   │   │   └── redux.ts             # Typed useAppDispatch/useAppSelector
│   │   ├── vault/
│   │   │   └── staticVault.ts       # In-browser static vault (demo mode)
│   │   ├── App.tsx                  # Root component: Router + VaultLayout
│   │   ├── entry-client.tsx         # Client entry: createRoot + preloaded state
│   │   ├── entry-server.tsx         # SSR entry: renderApp + cache preloading
│   │   ├── entry-server.test.tsx    # 11 unit tests for SSR
│   │   └── main.tsx                 # Dev entry: createRoot (no SSR)
│   ├── server.mjs                   # Node.js Express SSR sidecar
│   ├── ssr.Dockerfile               # Docker image for SSR sidecar
│   ├── vite.config.ts               # Vite config with SSR noExternal
│   ├── vitest.config.ts             # Vitest config for frontend tests
│   └── package.json                 # Dependencies and scripts
├── plugins/
│   └── retro-obsidian-publish.py    # devctl plugin (3-service orchestration)
├── .devctl.yaml                     # devctl profiles and plugin config
├── ideas.md                         # Design philosophy (System 1 aesthetic)
├── docker-compose.yml               # Multi-service deployment
├── backend/Dockerfile               # Multi-stage build (Go + Node + Alpine)
├── deploy/
│   └── gitops-targets.json          # ArgoCD/gitops deployment targets
├── ttmp/                            # docmgr ticket workspace
│   └── 2026/06/06/RETRO-SSR-009/    # SSR sidecar design docs, diary, tasks
└── README.md
```

## Architecture

### High-level data flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Vault Directory (read-only .md files, images, assets)           │
└──────────────────┬──────────────────────────────────────────────┘
                   │ filepath.Walk + goldmark parsing
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│ Backend (Go single binary)                                      │
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Vault      │  │  Search      │  │  API Handlers          │ │
│  │  (mutex-    │  │  (Bleve      │  │  /api/notes,           │ │
│  │   protected)│  │   in-memory) │  │  /api/tree,            │ │
│  │             │  │              │  │  /api/search,          │ │
│  │  Notes:     │  │  NoteDoc:    │  │  /api/tags             │ │
│  │  ┌────────┐ │  │  {          │ │  │                        │ │
│  │  │ Slug   │ │  │   title,    │ │  │  SPA Handler:        │ │
│  │  │ Title  │ │  │   body,     │ │  │  /assets/* →         │ │
│  │  │ HTML   │ │  │   tags,     │ │  │  embedded FS         │ │
│  │  │ Tags   │ │  │   excerpt   │ │  │  / → index.html      │ │
│  │  │ Back-  │ │  │ }           │ │  │                        │ │
│  │  │ links  │ │  │             │ │  │  SSR Proxy:          │ │
│  │  │ Wiki   │ │  │  Search:    │ │  │  / → sidecar :8089   │ │
│  │  │ links  │ │  │  fuzzy +   │ │  │  fallback → SPA      │ │
│  │  │ Assets │ │  │  prefix    │ │  │                        │ │
│  │  │ URL    │ │  │  matching  │ │  │  File Watcher:       │ │
│  │  │ resolu-│ │  │  + AND/    │ │  │  fsnotify → reload   │ │
│  │  │ tion   │ │  │  OR logic  │ │  │  endpoint            │ │
│  │  └────────┘ │  │             │ │  └────────────────────────┘ │
│  └─────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
                   │ HTTP responses
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│ Frontend (React + Vite)                                          │
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Vault      │  │  Note        │  │  Search                │ │
│  │  Layout     │  │  Page        │  │  Page                  │ │
│  │  (menubar,  │  │  (renderer,  │  │  (search bar,          │ │
│  │   sidebar,  │  │   backlinks, │  │   results list)         │ │
│  │   panels)   │  │   tags)      │  │                        │ │
│  └─────────────┘  └──────────────┘  └────────────────────────┘ │
│                                                                 │
│  Store: RTK Query (vaultApi) + uiSlice                         │
│  Router: Wouter (client-side routing)                          │
└─────────────────────────────────────────────────────────────────┘
```

### The parser pipeline

The Markdown parser is the heart of the backend. It uses Goldmark with a custom preprocessing pipeline for wiki-link handling:

```go
func Parse(src []byte) (*ParsedNote, error) {
    // Step 1: Extract all [[wiki links]] and ![[embeds]] before goldmark
    // sees them. These become structured data for later resolution.
    wikiLinks := extractWikiLinks(src)

    // Step 2: Replace [[wiki links]] with placeholder HTML so goldmark
    // doesn't mangle the brackets. Placeholders survive the Goldmark
    // pipeline and get replaced back with proper <a> tags later.
    processed := replaceWikiLinks(src)

    // Step 3: Parse with Goldmark extensions for GFM, tables,
    // strikethrough, task lists, footnotes, and YAML frontmatter.
    md := goldmark.New(
        goldmark.WithExtensions(
            meta.Meta,           // YAML frontmatter
            extension.GFM,       // GitHub Flavored Markdown
            extension.Table,
            extension.Strikethrough,
            extension.TaskList,
            extension.Footnote,
        ),
        goldmark.WithParserOptions(
            parser.WithAutoHeadingID(), // auto-generate heading IDs
        ),
        goldmark.WithRendererOptions(
            html.WithHardWraps(),
            html.WithXHTML(),
            html.WithUnsafe(),         // allow raw HTML (for our placeholders)
        ),
    )

    // Step 4: Render HTML + extract frontmatter
    ctx := parser.NewContext()
    var buf bytes.Buffer
    if err := md.Convert(processed, &buf, parser.WithContext(ctx)); err != nil {
        return nil, err
    }

    htmlOut := buf.String()
    frontmatter := normalizeFrontmatter(meta.Get(ctx))

    // Step 5: Post-process: render callouts (admonitions), extract title,
    // tags, and excerpt (first paragraph as plain text).
    htmlOut = renderCallouts(htmlOut)
    title := extractTitle(frontmatter, src)
    tags := extractTags(frontmatter)
    excerpt := extractExcerpt(src)

    return &ParsedNote{
        Frontmatter: frontmatter,
        HTML:        htmlOut,
        WikiLinks:   wikiLinks,
        Tags:        tags,
        Title:       title,
        Excerpt:     excerpt,
    }, nil
}
```

The wiki-link regex matches all Obsidian wiki-link forms:

```
[[Target]]                → target only
[[Target|Alias]]          → target + display alias
[[Target#Heading]]        → target + heading anchor
![[Embed]]                → embed (IsEmbed = true)
[[Target#Heading|Alias]]  → all three components
```

After Goldmark parsing, the HTML output is post-processed for callout rendering (Obsidian admonition blocks like `> [!note]` become styled `<div>` elements), and then wiki-link placeholders are replaced with resolved `<a>` tags.

### The vault model

Each `.md` file becomes a `vault.Note`:

```go
type Note struct {
    Slug        string                 // URL slug: "research/kb/tribal/foo"
    Title       string                 // From frontmatter or first H1
    Path        string                 // Relative path inside vault
    Frontmatter map[string]interface{} // YAML frontmatter
    Tags        []string               // Extracted tags
    Excerpt     string                 // First paragraph, plain text
    HTML        string                 // Parsed HTML output
    WikiLinks   []WikiLinkRef          // Outgoing wiki links
    Backlinks   []string               // Inbound wiki links (computed)
    ModTime     time.Time              // File modification time
}
```

The slug is generated by converting the vault-relative path to a URL-friendly form. For example, `Research/KB/Tribal/App.md` becomes slug `research/kb/tribal/app`.

Wiki link resolution is the trickiest part of the vault. Obsidian wiki links can reference notes by:
1. Full path: `[[Research/KB/Tribal/App]]`
2. Short path suffix: `[[tribal/app]]` (suffix of the full path)
3. Title: `[[App]]` (if the note title matches)
4. Folder: `[[Tribal]]` (resolves to index.md if it exists)

The vault builds an index mapping every suffix of every note's path to the note's full slug. A wiki link like `[[tribal/app]]` is resolved by looking it up in this index.

Backlinks are computed after all notes are loaded: for every wiki link in every note, the target note's `Backlinks` slice is appended with the source note's slug.

### Search index

The search index uses Bleve, an in-memory full-text search engine. Each note is indexed as a `noteDoc`:

```go
type noteDoc struct {
    Title   string `json:"title"`
    Body    string `json:"body"`       // Stripped HTML from note body
    Tags    string `json:"tags"`        // Space-separated
    Excerpt string `json:"excerpt"`
}
```

The search implementation supports fuzzy matching for partial words and prefix matching for short queries:

```go
func (si *Index) Search(query string, limit int) ([]SearchResult, error) {
    words := tokenizeQuery(query)
    if len(words) == 0 {
        return []SearchResult{}, nil
    }

    var bleveQuery bq.Query

    if len(words) == 1 && len(words[0]) <= 3 {
        // Short single word: use prefix wildcard ("goj" → "goj*")
        bleveQuery = bleve.NewPrefixQuery(words[0])
    } else {
        // Multi-word or longer single word: fuzzy match with AND logic
        var disjuncts []bq.Query
        for _, w := range words {
            mq := bleve.NewMatchQuery(w)
            mq.SetFuzziness(1)
            disjuncts = append(disjuncts, mq)
        }
        bleveQuery = bleve.NewConjunctionQuery(disjuncts...)
    }

    req := bleve.NewSearchRequestOptions(bleveQuery, limit, 0, false)
    result, err := si.idx.Search(req)
    // ... map hits to SearchResult
}
```

### The HTTP server

The Go server uses `gorilla/mux` for routing with three categories of handlers:

```go
r := mux.NewRouter()

// API routes — JSON data
h.Register(r)  // mounts: GET /api/config, /api/notes, /api/notes/{slug},
               //        /api/tree, /api/search, /api/tags

// Vault assets — serve images and other files from the vault
r.PathPrefix("/vault-assets/").Handler(assetHandler(state))

// Admin reload — optional POST endpoint for GitOps workflows
r.HandleFunc("/api/admin/reload", reloadHandler(...))

// SPA fallback — serve static assets + index.html for client-side routing
r.PathPrefix("/").Handler(spaHandler)
```

The SPA handler serves static assets from an embedded filesystem (production) or from disk (development). For any non-asset path, it returns `index.html`, enabling client-side routing.

### Runtime state and reload

The server holds a `RuntimeState` that wraps the `*vault.Vault` and `*search.Index` with a `sync.RWMutex`. This supports atomic reloads:

```go
func (s *RuntimeState) Reload() error {
    // Load a new vault and index independently
    v, si, resolved, err := loadVaultAndSearch(configured)
    if err != nil {
        return err
    }

    // Atomically swap into service
    s.mu.Lock()
    s.vault = v
    s.search = si
    s.resolvedRoot = resolved
    s.mu.Unlock()
    return nil
}
```

This pattern is essential for GitOps deployments where a sidecar process atomically flips a symlink to a new vault checkout and then calls the reload endpoint.

### Frontend architecture

The frontend uses RTK Query for API data fetching and Wouter for routing. The store is split into two parts:

```typescript
// RTK Query slice — all API data
export const vaultApi = createApi({
  reducerPath: "vaultApi",
  endpoints: (builder) => ({
    getConfig:  builder.query<SiteConfig, void>(...),
    listNotes:  builder.query<NoteListItem[], void>(...),
    getNote:    builder.query<Note, string>(...),
    getTree:    builder.query<FileNode, void>(...),
    search:     builder.query<SearchResult[], string>(...),
    listTags:   builder.query<TagCount[], void>(...),
  }),
});

// UI state slice — local component state
const uiSlice = createSlice({
  reducers: {
    toggleSidebar(state),
    toggleRightPanel(state),
    setSearchQuery(state, action),
    setActiveNote(state, action),
  },
});
```

The three page components form the core of the UI:

- **VaultLayout**: The chrome — menubar with toggle buttons, resizable sidebar (file tree), and the main content pane. On mobile (<768px), the sidebar becomes an off-canvas drawer.
- **NotePage**: Fetches a note by slug via `useGetNoteQuery()`, renders it with `NoteRenderer`, and optionally shows a right panel with backlinks.
- **SearchPage**: Debounced search input that triggers `useSearchQuery()` and renders results in `NoteCard` components.

### The SSR system (added 2026-06-06)

The SSR sidecar was added to improve SEO and agent-readability. The previous SPA returns an empty `<div id="root"></div>` to crawlers and agents that don't execute JavaScript.

The SSR system consists of four components:

**1. Server entry (`entry-server.tsx`)** — Parses the URL, creates a fresh Redux store, preloads RTK Query cache with server-fetched data, and renders React to an HTML string using `renderToString()`:

```typescript
export async function renderApp(url: string, data: SSRData): Promise<SSRResult> {
  const store = makeStore();

  // Preload RTK Query cache
  await preloadCache(store, data, slug);

  // Parse URL and render the matching page
  const pathname = url.split('#')[0] || '/';
  let html: string;

  if (pathname.startsWith('/note/')) {
    html = renderToString(<SSRNotePage note={data.note} />);
  } else if (pathname === '/search') {
    html = renderToString(<SSRSearchPage />);
  } else {
    html = renderToString(<SSRHomePage />);
  }

  return { html, preloadedState: store.getState() };
}
```

**2. Client entry (`entry-client.tsx`)** — Uses `createRoot()` to render the full interactive app, reading `window.__PRELOADED_STATE__` for preloaded data:

```typescript
const preloadedState = window.__PRELOADED_STATE__;
delete window.__PRELOADED_STATE__;
const store = makeStore(preloadedState);

const root = document.getElementById("root")!;
root.textContent = "";  // Clear SSR content before mounting client app
createRoot(root).render(<App />);
```

**3. Express sidecar (`server.mjs`)** — An Express server that:
- Receives page requests from the Go server's reverse proxy
- Pre-fetches data from the Go API
- Calls `renderApp()` to render React to HTML
- Assembles complete HTML with meta tags, JSON-LD, and `<noscript>` fallback

**4. Go server proxy (`server.go`)** — The Go server gains an `--ssr-url` flag. When set, page requests are reverse-proxied to the Node.js sidecar. If the sidecar is unavailable, the server falls back to the SPA handler.

```go
func newSSRProxy(ssrURL string, spaHandler http.Handler) http.Handler {
    proxy := &http.Client{Timeout: 10 * time.Second}
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        proxyReq, _ := http.NewRequestWithContext(r.Context(), r.Method, proxyURL.String(), nil)
        resp, err := proxy.Do(proxyReq)
        if err != nil || resp.StatusCode >= 500 {
            spaHandler.ServeHTTP(w, r)  // fallback to SPA
            return
        }
        // Copy response headers and body
        io.Copy(w, resp.Body)
    })
}
```

Key design decisions in the SSR implementation:

- **No hydration mismatch**: The SSR renders simplified components (just note title, HTML body, tags, backlinks) while the client renders the full app (sidebar, panels, etc.). Using `hydrateRoot` would require identical DOM trees. Instead, `createRoot()` with `root.textContent = ""` clears the SSR content and mounts the full app fresh. The SSR HTML is still visible to crawlers/agents.
- **Store factory**: The store is a factory (`makeStore(preloadedState?)`) so each SSR request gets its own store, preventing data leaking between concurrent renders.
- **URL parsing without Wouter**: Wouter doesn't support server-side rendering (no `StaticRouter`). The SSR entry parses URLs manually and renders matching components directly.
- **Static assets through Go**: `/assets/` and `/fonts/` routes are served directly by the Go server, not through the SSR proxy. The SSR sidecar only renders page HTML.

### Deployment

The project uses a multi-stage Docker build:

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Node 22 Alpine  │    │  Go 1.25 Alpine  │    │  Alpine 3.20     │
│  (web-builder)   │───▶│  (go-builder)    │───▶│  (final image)   │
│                  │    │                  │    │                  │
│  pnpm install    │    │  CGO_ENABLED=1   │    │  ./retro-publish │
│  pnpm build:all  │    │  go build        │    │  serve --port 8080│
│  → dist/         │    │  → binary        │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

In production, the Go binary is the only container. The web assets are embedded at build time via `//go:embed`. The build command is `retro-obsidian-publish build web` which runs `vite build`.

For local development, three services run via devctl:
- **Backend**: Go server with `go run ./cmd/... serve --vault ... --serve-web=false`
- **Web**: Vite dev server with `pnpm dev` (hot-reload for frontend changes)
- **SSR**: Node.js sidecar with `node server.mjs` (for SSR pages)

## Implementation details

### Wiki-link resolution algorithm

The wiki-link resolution is the most complex non-trivial algorithm in the codebase. It must handle all Obsidian wiki-link reference patterns:

```
[[Note]]                  → simple reference
[[Folder/Note]]           → nested path
[[Note|Display Text]]     → with alias
[[Note#Heading]]          → with heading anchor
[[Note#Heading|Alias]]    → alias + heading
![[Embed]]                → embed
![[Embed#Heading]]        → embed with heading
```

The resolution works in two phases:

1. **Pre-processing** (during parsing): The wiki-link regex extracts all wiki links from the source text, creating a list of `WikiLink` structs. The raw markdown is then modified to replace wiki-link syntax with placeholder HTML tags so Goldmark doesn't mangle them.

2. **Post-processing** (after vault loading): Once all notes are loaded and the wiki-link index is built, the HTML of every note is re-processed:
   - `ReplaceWikiLinksString()` walks the HTML and replaces placeholder tags with proper `<a>` tags with resolved slugs
   - `ReplaceWikiLinkDisplay()` replaces the display text with the target note's title
   - `RewriteImageSources()` rewrites image `src` attributes to use `/vault-assets/` URLs

The wiki-link index maps from any possible short-form reference to the full vault slug:

```go
func (v *Vault) buildWikiLinkIndex() {
    for _, note := range v.notes {
        // Register full slug
        v.wikiLinkIndex[note.Slug] = note.Slug

        // Register suffix-based short paths
        // e.g., "Research/KB/Tribal/App" → register:
        //   "tribal/app", "kb/tribal/app"
        parts := strings.Split(filepath.ToSlash(note.Path), "/")
        for i := len(parts) - 2; i >= 0; i-- {
            shortPath := strings.Join(parts[i:], "/")
            shortPath = strings.TrimSuffix(shortPath, ".md")
            suffix := Slugify(shortPath)
            if _, exists := v.wikiLinkIndex[suffix]; !exists {
                v.wikiLinkIndex[suffix] = note.Slug
            }
        }

        // Also register by title slug
        titleSlug := Slugify(note.Title)
        if titleSlug != "" {
            v.wikiLinkIndex[titleSlug] = note.Slug
        }
    }
}
```

### Asset URL resolution

Vault images need special URL handling. A note at `Research/Notes/foo.md` might reference an image as `![screenshot](images/diagram.png)`. The image resolution must:
1. Resolve relative paths against the note's directory
2. Convert to `/vault-assets/` URLs for the static file handler
3. Handle root-relative paths (`/images/diagram.png`) as vault-root-relative

```go
func (v *Vault) ResolveAssetURL(notePath, src string) string {
    // Skip external URLs, data: URIs, and already-resolved paths
    if shouldLeaveAssetURL(src) {
        return src
    }

    // Resolve relative paths against note's directory
    assetPath := parsed.Path
    if !strings.HasPrefix(assetPath, "/") {
        base := path.Dir(filepath.ToSlash(notePath))
        assetPath = path.Join(base, assetPath)
    }

    // Convert to /vault-assets/ URL
    return "/vault-assets/" + url.PathEscape(cleanVaultRelativePath(assetPath))
}
```

The asset handler (`assetHandler`) validates paths to prevent directory traversal and rejects `.md` files and symlinks.

### The design system

The visual design follows the Retro System 1 aesthetic (early Macintosh, 1984). Key design principles:

- **Monochrome foundation**: Near-black ink (`#1a1a1a`) on warm aged paper (`#f0ede8`). No gradients, no shadows except hard 1px offsets.
- **Color accents reserved exclusively for functional elements**: links = deep blue (`#0000cc`), tags = forest green (`#005500`), destructive = deep red (`#cc0000`).
- **Square corners everywhere**: zero border-radius, hard 1px borders, inset box-shadows for sunken panels.
- **Bitmap-inspired typography**: system-ui/Chicago fallback stack, no web fonts, `-webkit-font-smoothing: none`.
- **Asymmetric fixed chrome**: top menubar (28px), left sidebar (224px), right content pane (flex-1).

The CSS uses CSS custom properties for the color system:

```css
:root {
    --background: #f0ede8;  /* aged paper */
    --foreground: #1a1a1a;  /* ink */
    --accent: #0000cc;      /* link blue */
    --border: #1a1a1a;      /* hard borders */
}
```

State changes are instant (no smooth color transitions), mimicking physical buttons:

```css
a:hover { background-color: var(--accent); }  /* instant hover */
button:active { transform: translateY(1px); }  /* 1px press-down */
```

### RTK Query with multiple modes

The `vaultApi` supports two modes of operation:

1. **Backend mode** (default): Fetches data from the Go API at `/api/*` on the same origin. This is the standard deployment.
2. **Static demo mode** (`VITE_STATIC_VAULT=true`): Serves data from an in-browser static vault module. This is useful for demos and testing without a running backend.

The mode detection is done at module load time:

```typescript
const API_BASE = import.meta.env.VITE_API_URL || "";
const IS_STATIC = import.meta.env.VITE_STATIC_VAULT === "true";

export const vaultApi = createApi({
  endpoints: (builder) => ({
    listNotes: builder.query<NoteListItem[], void>(
      IS_STATIC
        ? {
            queryFn: async () => ok(staticListNotes()),
          }
        : {
            query: () => "/api/notes",
          }
    ),
    // ... other endpoints follow the same pattern
  }),
});
```

## Current user-facing commands

### CLI (Go binary)

```bash
# Serve the vault with the web app
retro-obsidian-publish serve \
  --vault /path/to/vault \
  --port 8080

# Serve with a custom vault name
retro-obsidian-publish serve \
  --vault /path/to/vault \
  --vault-name "My Notes" \
  --port 8080

# Build the web frontend (copies to embed directory)
retro-obsidian-publish build web

# Build with SSR enabled (requires --ssr-url)
retro-obsidian-publish serve \
  --vault /path/to/vault \
  --ssr-url http://localhost:8089
```

### Development

```bash
# Install frontend dependencies
pnpm --dir web install --frozen-lockfile

# Start dev environment (3 services: backend, web, SSR)
devctl up --profile example

# Or manually:
cd backend && go run ./cmd/retro-obsidian-publish serve \
  --vault ./vault-example \
  --port 8080 &

cd web && pnpm dev

cd web && node server.mjs  # SSR sidecar
```

### Deployment

```bash
# Docker build
docker build -t retro-obsidian-publish -f backend/Dockerfile .

# Docker Compose (includes SSR sidecar)
docker compose up --build

# Production: single Go binary with embedded assets
go build -tags embed -o retro-obsidian-publish ./cmd/retro-obsidian-publish
./retro-obsidian-publish serve --vault /vault --port 8080
```

## Important project docs

- **DESIGN DOC**: `ttmp/2026/06/06/RETRO-SSR-009/design-doc/01-ssr-sidecar-analysis-and-implementation-guide.md` — Comprehensive SSR sidecar design with architecture diagrams, decision records, pseudocode, and phased implementation plan
- **DIARY**: `ttmp/2026/06/06/RETRO-SSR-009/reference/01-implementation-diary.md` — Chronological investigation diary capturing all decisions, failures, and lessons
- **DESIGN IDEAS**: `ideas.md` — Design philosophy, the System 1 aesthetic rationale, color system
- **README**: `README.md` — Project overview and quick start
- **DEVCTL PLUGIN**: `plugins/retro-obsidian-publish.py` — Local development orchestration for 3 services
- **SSR DESIGN DOC** (reference implementation): `glazed/ttmp/2026/05/25/DOCSCTL-SSR/design-doc/01-ssr-sidecar-analysis-and-implementation-guide.md` — The Glazed docs browser SSR implementation that served as the reference for this project's SSR system

## Open questions

1. **Writing direction**: Should the project support a reverse direction — importing rendered HTML back into Obsidian? This would be useful for collaborative workflows.

2. **Editor integration**: Could the project expose an Obsidian plugin that uses the local API for live preview? The current setup is read-only (vault directory is treated as read-only).

3. **Streaming SSR**: The current SSR renders the entire page synchronously. For large vaults with many notes, streaming SSR with React 19's `renderToReadableStream` could improve perceived load time.

4. **Static generation**: Could the project support pre-rendering at build time? This would eliminate the need for the SSR sidecar in production, but would require a rebuild whenever the vault changes.

5. **Plugin system**: The project is currently self-contained. A plugin system (similar to Obsidian's) could allow community extensions for custom rendering, additional data sources, etc.

## Near-term next steps

- [ ] Add `retro-obsidian-publish serve --ssr-url http://localhost:8089` flag to the help output
- [ ] Add integration tests that verify the full SSR pipeline (Go → SSR → client)
- [ ] Add a `docs/` directory with developer setup instructions
- [ ] Consider adding a GraphQL API alongside the REST API for more flexible querying
- [ ] Evaluate streaming SSR for large vaults (1000+ notes)

## Project working rule

> The vault directory is the single source of truth. The application reads it, never writes to it. All data — HTML, search index, backlinks, file tree — is derived from the Markdown files. If the vault is the ground truth, then the website is just a view.