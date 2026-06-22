---
Title: Single-Binary Go + SPA Pattern
Ticket: PROJECT-MAPS-001
Status: active
Topics:
  - research
  - projects
  - concept-maps
  - web-ui
  - local-first
  - go
  - react
DocType: bridge-report
Intent: long-term
Owners: []
RelatedFiles:
  - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/05-bridge-topic-reports-plan.md
    Note: Bridge 7 assignment
  - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/04-refined-topic-concept-maps-v2.md
    Note: Refined concept maps that identified this bridge topic
  - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/sources/07a-webui-localshells-backendui.md
    Note: Topic 7 partition A evidence
  - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/sources/06b-data-browsers-readwise-knowledge.md
    Note: Topic 6 partition B evidence
  - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/sources/05b-agents-pi-providers-dashboards.md
    Note: Topic 5 partition B evidence
  - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/sources/04a-infra-hosting-secrets-deployment.md
    Note: Topic 4 partition A evidence
ExternalSources: []
Summary: Textbook-style bridge report on the single-binary Go + SPA pattern, spanning T4, T5, T6, T7.
LastUpdated: 2026-06-22T23:59:00-04:00
WhatFor: Use this to understand the single-binary Go + SPA pattern, its concrete instances, enhancements, failure modes, and learning path.
WhenToUse: Before designing, reviewing, or extending a local-first Go-hosted web application.
---

# Single-Binary Go + SPA Pattern

A single Go binary that serves an HTTP API and an embedded single-page application from one process is the dominant local-first application shell across this body of work. The same Go renderer core that drives the CLI is reused by the HTTP server, and in some projects it is reused again by a desktop shell built on Wails. This report explains why the pattern exists, what its invariants are, how it appears in concrete instances, which enhancements make it production-grade, where it breaks, and how to build one.

The pattern spans four topics: static-site deployment (T4), agent dashboards and minitrace UIs (T5), local corpus browsers (T6), and local-first app shells (T7). It is the same architecture in each place because it solves the same problem: a Go program already owns the data model and the parsing logic, and the browser is a presentation surface that should not require a separate deployment artifact.

## Why the pattern exists

The alternative to a single binary is the standard split: a backend service that speaks HTTP, a separate frontend build process that emits static assets, and an operator who must keep both in sync. That split is acceptable for a public web service with a large team. It is wrong for a local-first tool.

A local-first tool has three properties that the split deployment violates. First, the data is already in memory inside the Go process; shipping it out to a separate frontend over HTTP just to render it is an unnecessary hop. Second, the user expects the tool to start with one command and stop with one command; running two processes changes the lifecycle contract. Third, the tool should be portable: a single binary can be copied to a new machine, dropped into a container, or opened from `file://` without a runtime dependency graph.

The `go:embed` directive, stabilized in Go 1.16, is what makes the pattern cheap. A frontend built with Vite or esbuild produces a `dist/` directory. A Go file with `//go:embed` compiles that directory into the binary. The HTTP server serves the embedded files with one handler. There is no asset pipeline at runtime, no CDN dependency, no path resolution against the working directory. The Go binary is the application and the artifact.

```go
//go:embed all:public
var embeddedAssets embed.FS

func spaHandler() http.Handler {
    sub, _ := fs.Sub(embeddedAssets, "public")
    return http.FileServer(http.FS(sub))
}
```

The pattern is not the only way to deliver a Go-hosted UI. The `docsctl` SSR sidecar (`Projects/2026/05/25/ARTICLE - SSR Sidecar for Go-Hosted React SPAs - A Deep Dive into docsctl Server-Side Rendering.md`) keeps the Go binary and the React SPA as the primary shell, but adds a Node.js Express sidecar for server-side rendering. The sidecar exists because a React component tree that uses hooks, context, and browser APIs cannot be rendered by embedding V8 or goja in the Go process. The single-binary shape still owns routing and asset serving; the sidecar enriches specific page requests and falls back to the SPA shell on failure. The pattern is therefore the foundation, not the ceiling.

## The core invariants

The pattern is not just "compile a frontend into a Go binary." Four invariants distinguish it from a naive bundle.

**The Go renderer core is reusable across shells.** The renderer that parses Markdown, computes backlinks, and produces HTML fragments is the same code in the CLI, the HTTP server, and the Wails desktop shell. The shell changes; the renderer does not. The `md-view` rewrite (`Projects/2026/06/13/ARTICLE - Replacing md-view with a Wails v2 Desktop Application - Technical Deep Dive.md`) is the clearest instance: `Render(filePath, opts) -> full HTML page` was refactored into `RenderBody(filePath, opts) -> { Frontmatter, Body, Title }`, and the same `RenderBody` then powered the daemon, the Wails app, and any future shell.

**The API and the frontend share one origin.** The browser receives the SPA shell from `/`, then calls `/api/*` on the same origin. There is no CORS configuration, no separate frontend host, no cross-origin cookie story. This is visible in the `go-minitrace` web UI (`Projects/2026/04/01/PROJ - go-minitrace - Web UI and Transcript Explorer.md`), where the React SPA and the DuckDB-backed REST API live behind the same `http://127.0.0.1:8080`.

**The vault, source directory, or database is read-only at runtime.** The application treats its data source as ground truth and derives everything from it. Retro Obsidian Publish (`Projects/2026/06/06/PROJ - Retro Obsidian Publish - A Retro Monochrome Vault Browser.md`) states this as a working rule: "The vault directory is the single source of truth. The application reads it, never writes to it. All data — HTML, search index, backlinks, file tree — is derived from the Markdown files." The same rule holds for the Codebase Browser static export (`Projects/2026/05/01/ARTICLE - Static SQL.js Codebase Browser - SQLite as the Browser Runtime.md`): Go indexes the repository offline and the browser reads the resulting SQLite database.

**The static assets and the Go code ship as one artifact.** The Dockerfile for Go-Go Parc (`Projects/2026/05/14/PROJECT REPORT - Go-Go Parc Website - Implementation Deployment and Git-Sync Runtime.md`) shows the canonical three-stage build: Node builds the React app, Go builds the binary with `-tags embed` after copying `web/dist` into `backend/internal/web/embed/public`, and the final Alpine image contains only the binary and CA certificates. The deployed image is `ghcr.io/go-go-golems/retro-obsidian-publish:sha-6c22a66`. There is no second container for the frontend.

## Concrete instances

The pattern appears in at least seven projects across the corpus. Each instance solves a different content problem but shares the same shell.

| Project | Data source | Frontend | Shell | Evidence |
|---|---|---|---|---|
| Go-Go Parc Website | Obsidian vault (git-sync) | React + RTK Query | Go HTTP server + git-sync sidecar | `Projects/2026/05/14/PROJECT REPORT - Go-Go Parc Website - Implementation Deployment and Git-Sync Runtime.md` |
| Retro Obsidian Publish | Obsidian vault | React + Vite + Wouter | Go HTTP server + SSR sidecar + git-sync | `Projects/2026/06/06/PROJ - Retro Obsidian Publish - A Retro Monochrome Vault Browser.md` |
| go-minitrace web UI | `.minitrace.json` archives | React + MUI + RTK Query | Go HTTP server, in-process DuckDB | `Projects/2026/04/01/PROJ - go-minitrace - Web UI and Transcript Explorer.md` |
| Codebase Browser (static) | Git repository | React + RTK Query + HashRouter | Static `file://` artifact with `sql.js` | `Projects/2026/05/01/ARTICLE - Static SQL.js Codebase Browser - SQLite as the Browser Runtime.md` |
| Readwise Viewer | Readwise API (synced to SQLite) | TypeScript + Redux + Immer | Go HTTP server, embedded CLIM UI | `Projects/2026/05/21/PROJ - Readwise Viewer.md` |
| Streaming Agent Dashboard | pi RPC subprocess | React + RTK Query + Storybook | Go HTTP server, sessionstream WebSocket | `Projects/2026/05/12/ARTICLE - Streaming Agent Dashboard - Server Side Implementation Deep Dive.md` |
| docsctl docs browser | SQLite help databases | React + Vite + RTK Query | Go HTTP server + SSR sidecar | `Projects/2026/05/24/ARTICLE - Docsctl and Docs-Yolo Documentation Deployment.md`, `Projects/2026/05/25/ARTICLE - SSR Sidecar for Go-Hosted React SPAs - A Deep Dive into docsctl Server-Side Rendering.md` |
| md-view (Wails) | Markdown file | Static HTML/CSS/JS | Wails desktop binary | `Projects/2026/06/13/ARTICLE - Replacing md-view with a Wails v2 Desktop Application - Technical Deep Dive.md` |

The table does work that prose cannot. Read it row by row and notice what changes and what does not. The data source changes. The frontend library changes (React, plain TypeScript, static HTML). The shell changes (HTTP server, static artifact, desktop binary). What does not change is the invariant: a Go core owns the data model, the frontend is embedded or served from the same process, and the binary is the deployment artifact.

### Go-Go Parc Website

Go-Go Parc publishes this Obsidian vault as `https://parc.yolo.scapegoat.dev`. The Go binary serves a JSON REST API (`/api/notes`, `/api/notes/{slug}`, `/api/search`, `/api/tree`, `/api/tags`) and the embedded React SPA from one process. The `SnapshotProvider` interface is the structural center:

```go
type SnapshotProvider interface {
    Snapshot() (*vault.Vault, *search.Index)
}
```

Handlers do not own the vault directly. They ask the provider for the current pair. This indirection is what allows the reload endpoint to build a replacement vault and search index, then swap both into service without changing the request handlers. The content is updated by a `git-sync` sidecar, not by rebuilding the container image.

### Retro Obsidian Publish

Retro Obsidian Publish is the same pattern with an SSR sidecar layered on top. The Go binary still serves the API and the embedded SPA. A Node.js Express sidecar renders React via `renderToString()` for crawler and agent requests, and the Go server reverse-proxies to it with SPA fallback on failure. The a14y score went from 62 to 99 after adding markdown mirrors (`/index.md`, `/note/{slug}.md`), discovery endpoints (`/AGENTS.md`, `/llms.txt`, `/sitemap.md`), and `Accept: text/markdown` content negotiation. The vault directory remains read-only; all derived data (HTML, Bleve search index, backlinks, file tree) is rebuilt from Markdown on reload.

### go-minitrace web UI

`go-minitrace serve` is a Glazed command that opens an in-process DuckDB connection, loads `.minitrace.json` archives, and serves a React SPA with three screens: session browser, transcript viewer, and SQL workbench. The Go backend computes block decomposition and artifact badges; the frontend renders. The dev mode splits the transport: Go serves only `/api`, Vite serves the frontend with HMR, and Vite proxies `/api` to `http://localhost:8080`. Production compiles the frontend into the binary. This is the cleanest instance of the "thin frontend, backend owns semantics" rule.

### Codebase Browser (static SQL.js)

The Codebase Browser is the pattern pushed to its logical endpoint: there is no Go server at runtime. Go indexes the repository offline and produces a SQLite database. The browser loads `db/codebase.db` with `sql.js`, queries it locally, and renders pages. The artifact runs from `file://` with no server process. The manifest declares `hasGoRuntimeServer: false`. This is the single-binary pattern with the binary removed from the runtime — Go is a build tool, the database is the runtime, and the browser is the shell.

### Readwise Viewer

Readwise Viewer wraps a SQLite database populated by a Python sync script. The Go binary serves `/api/*` and an embedded CLIM-style web UI built from TypeScript, Redux, and Immer. The backend wraps every API result in a typed `PresentationRef` envelope with semantic capabilities. The frontend does not guess what a row means from its fields; it receives a presentation object. The same Go binary also provides Glazed CLI commands for terminal-based browsing, so the renderer core is shared across the CLI and HTTP shells.

### Streaming Agent Dashboard

The Streaming Agent Dashboard is the pattern applied to live data. The Go binary starts a pi coding agent subprocess, observes its RPC frames through runtime observer hooks, and projects them into sessionstream timeline entities. The React SPA subscribes over WebSocket and upserts entities. The key design choice is that the backend owns accumulation and the frontend owns rendering: the WebSocket sends complete `ClawMessageEntity` values, not text deltas, so snapshots and live updates reduce through the same frontend path. This is the single-binary pattern extended to streaming.

### docsctl

docsctl is the documentation deployment system. The `docs-browser` container runs `glaze serve --from-sqlite-dir` and serves the embedded React SPA from the Go binary. The `docs-registry` container accepts uploads of SQLite help databases. Both share a persistent volume. The SSR sidecar was added later to improve SEO and agent readability, with the Go server falling back to the SPA shell when the sidecar is unavailable. The a14y score went from 42 to 97.

## Enhancements that make the pattern production-grade

The bare pattern — embed the SPA, serve the API, ship the binary — is enough for a local tool. Production adds three enhancements that are worth understanding as distinct decisions.

### Re-runnable DOM augmentation

The `md-view` Wails rewrite surfaced a structural requirement that is easy to miss. In a traditional browser app, the renderer produces a full HTML page, so inline scripts run once per page load and are done. In a stable-shell WebView (Wails) or a SPA with fragment swaps, only `#content` is replaced. Any DOM augmentation — copy buttons, Mermaid rendering, syntax highlighting — must be **re-runnable** after each fragment swap.

The fix in `md-view` was architectural. `augment.js` exposes `window.MDSAugmentPage()`, and `showContent(html)` calls `MDSAugmentPage()` after `content.innerHTML = html`. The same path is reused after live reloads. The augmentation is split into two idempotent passes: copy-button injection (skipping Mermaid blocks) and Mermaid conversion. The order is observable: an early version ran copy-button injection before Mermaid conversion without skipping `language-mermaid`, which left a stray copy button beside each diagram.

This requirement generalizes. Any single-binary Go + SPA that uses a stable shell — whether Wails, an iframe-based preview, or an SPA with client-side routing — must treat DOM augmentation as a re-runnable function, not a one-shot script.

### Atomic reload

When the vault or data source updates, the application must rebuild derived state (parsed notes, search index, backlinks) and swap it into service without serving a half-built snapshot. Go-Go Parc implements this with a mutex-protected `RuntimeState`:

```go
func (s *RuntimeState) Reload() error {
    configured := s.ConfiguredRoot()
    v, si, resolved, err := loadVaultAndSearch(configured)
    if err != nil {
        return err
    }

    s.mu.Lock()
    s.vault = v
    s.search = si
    s.resolvedRoot = resolved
    s.mu.Unlock()
    return nil
}
```

A failed reload leaves the old state active. This is the correct behavior for a public website: serving slightly older content is better than replacing a working snapshot with a broken one. The search index is part of the same snapshot as the vault, because a search result must refer to notes that exist in the active vault. If they were swapped independently, there would be a window where search returns stale slugs.

### git-sync sidecar

The content/application separation is the operational invariant of Go-Go Parc. Application code changes produce a new container image and a new Kubernetes rollout. Content changes produce a new Git commit in the vault repository. The `git-sync` sidecar tracks the vault repo, publishes a new checkout through a symlink, and calls `POST /api/admin/reload` on the Go server. The server resolves the symlink, rebuilds the vault and search index, and atomically swaps.

This separation prevents the common deployment problem of rebuilding the whole application for every content change. A vault commit is not an application release. The `git-sync` plus reload design implements that distinction directly. The reload endpoint has two authorization modes: a bearer token through `RETRO_RELOAD_TOKEN`, and loopback requests allowed with `--reload-allow-loopback` for the in-pod sidecar.

## Evolution: Wails desktop shell and Go/Wasm browser tools

The pattern has two natural extensions that appear in the corpus.

### Wails desktop shell

The `md-view` rewrite is the canonical example. The daemon model used three processes (CLI, daemon, browser) and three protocols (Unix socket, HTTP, SSE). The Wails model collapses them into one process: the WebView is inside the application, and the Go runtime owns the full lifecycle. Bound methods replace HTTP request/response; Wails events replace SSE.

The renderer survived the rewrite because it was already pure. The crucial refactor was extracting `RenderBody`, which returns a chrome-free HTML fragment consumed by a stable frontend shell. The shell — toolbar, dropzone, content area — lives in `frontend/dist/index.html` and persists across file opens. The same `RenderBody` function could power a CLI, an HTTP server, or a desktop app without modification.

The working rules distilled from the rewrite are general:

- If the browser moves inside the process, remove the network transport unless it still solves a real problem.
- Preserve the renderer as a pure component. Change the output contract only as much as the embedding model requires.
- In a stable-shell WebView frontend, all DOM augmentation must be re-runnable after fragment swaps.
- Menu callbacks and other Go-originated UI actions must emit events. They cannot update the DOM directly.
- A Wails production build must be built through `wails build`, not plain `go build`.

### Go/Wasm browser tools

The SQLide Browser (`Projects/2026/04/02/PROJ - SQLide Browser - Go Wasm SQL IDE.md`) and the Codebase Browser static WASM build show the pattern extended into the browser itself. Go compiles to Wasm with `GOOS=js GOARCH=wasm`, and the resulting module runs in the browser alongside the SPA. The invariant is a split: Go owns text processing and state; a worker (sqlite-wasm, sql.js) owns the database engine. Go never talks to SQLite directly.

This is not the same as the single-binary pattern, but it is a sibling. The single-binary pattern puts Go on the server and the SPA in the browser. The Go/Wasm pattern puts Go in the browser alongside the SPA. Both share the invariant that the Go core is reusable: the same `pkg/flatten` core that powers the WASM JSON Flattener CLI also powers the browser Wasm module (`Projects/2026/04/14/PROJ - WASM JSON Flattener - Go CLI and WebAssembly Tool.md`).

## Failure modes

The pattern has four failure modes that recur across instances. Each is a design lesson, not a bug.

### SPA-only shells are weak for agents and search

A pure SPA shell returns an empty `<div id="root"></div>` to any client that does not execute JavaScript. This includes search engine crawlers, social preview fetchers, and coding agents. The docsctl docs browser scored 42/100 on the a14y audit for this reason. The fix is the SSR sidecar or markdown mirrors, but the lesson is structural: agent readability is an HTTP routing commitment served **before** the SPA fallback, not a frontend enhancement. Retro Obsidian Publish reached 99/100 by serving `/index.md`, `/note/{slug}.md`, `/AGENTS.md`, `/llms.txt`, and `/sitemap.md` before the SPA shell, plus `Accept: text/markdown` content negotiation.

### One-shot DOM augmentation breaks on reload

Scripts that run once per page load break when only `#content` is replaced. This is the failure mode that produced the re-runnable augmentation invariant in `md-view`. The fix is not cosmetic: `augment.js` exposes `window.MDSAugmentPage()` and the shell calls it after every fragment swap. Any single-binary Go + SPA that uses a stable shell must treat augmentation as a re-runnable function.

### fsnotify inode loss

`fsnotify` watches inodes, not paths. When `git checkout` or an editor recreates a file, the watch is lost. The SSE stream stays open but no events arrive. The `md-view` daemon article (`Projects/2026/05/07/ARTICLE - md-view - Building a Daemon-Based Markdown Viewer in Go.md`) documents this explicitly. Go-Go Parc works around it by disabling `fsnotify` in production (`--watch=false`) and using the `git-sync` webhook to trigger reloads instead. The lesson: for production content updates, prefer an explicit reload endpoint over filesystem watching.

### Wails build tag failure

A Wails production binary is not produced by plain `go build` with only `-tags webkit2_41`. A direct `go build` produces a binary that launches with the runtime error: `Wails applications will not build without the correct build tags.` This matters because it changes every build path: local `make build`, CI compile checks, GoReleaser, and documentation. The fix is to repoint the project to `wails build`, and to give GoReleaser the equivalent tag set explicitly. This is the kind of detail that is easy to miss if you only test through `wails dev`, which injects the necessary flow automatically.

## A learning path

The following path builds a single-binary Go + SPA application from scratch, using the invariants and enhancements documented above as milestones.

**1. Start with the Go core and a CLI.** Build the renderer and data model as a pure Go package with no HTTP dependency. The `md-view` `RenderBody` function is the target shape: it takes a file path and options, returns a structured result, and does not know how it will be consumed. Write a Glazed CLI command that uses this core. This step proves the renderer is reusable before any shell is added.

**2. Add an HTTP server that serves the API.** Mount a `net/http` or `gorilla/mux` router with `/api/*` endpoints. Return explicit DTOs, not raw internal structs — the `go-minitrace` web UI does this to avoid pushing pointer-heavy Go schemas into TypeScript. Add a `SnapshotProvider` interface so handlers ask for the current state rather than owning it directly. This indirection is what enables atomic reload later.

**3. Build the frontend and embed it.** Use Vite or esbuild to produce a `dist/` directory. Add a `//go:embed all:public` directive and an SPA handler that serves `index.html` for any non-asset path. Use a build tag (`-tags embed`) so development can serve from disk while production serves from the embedded filesystem. The Go-Go Parc Dockerfile is the reference: Node stage builds the frontend, Go stage copies `web/dist` and builds with the embed tag, Alpine stage ships only the binary.

**4. Make DOM augmentation re-runnable.** If the SPA uses client-side routing or fragment swaps, expose augmentation as a function (`window.MDSAugmentPage()`) and call it after every content change. Split augmentation into idempotent passes with a defined order. Skip Mermaid blocks during copy-button injection. This is the lesson that is hardest to recover from if missed.

**5. Add atomic reload.** Wrap the vault and search index in a `RuntimeState` with a `sync.RWMutex`. Build the replacement state fully before swapping. A failed reload leaves the old state active. Treat the search index as part of the same snapshot as the vault to avoid stale slugs.

**6. Add a reload endpoint and disable filesystem watching in production.** Expose `POST /api/admin/reload` with bearer token or loopback authorization. Disable `fsnotify` in production (`--watch=false`). For Kubernetes deployments, add a `git-sync` sidecar that polls the content repository, publishes a symlink, and calls the reload endpoint. The content/application separation is the operational payoff: a vault commit is not an application release.

**7. Add agent-readable mirrors before the SPA fallback.** Serve `/index.md` and `/note/{slug}.md` with frontmatter and canonical `Link` headers. Add `Accept: text/markdown` content negotiation. Add discovery endpoints: `/AGENTS.md`, `/llms.txt`, `/sitemap.md`, `/sitemap.xml`. Verify with an a14y audit. The target is 97+.

**8. Consider an SSR sidecar if the React tree needs server rendering.** Add a Node.js Express sidecar that calls `renderToString()` with a fresh Redux store per request. Reverse-proxy page requests from Go to the sidecar with SPA fallback on failure. Use `createRoot()` with `root.textContent = ""` on the client to avoid hydration mismatch. Do not embed V8 or goja for this — the React component tree uses hooks, context, and browser APIs that require a real Node.js environment.

**9. Consider Wails for a desktop shell.** If the tool should be a native application, wrap the same Go core in a Wails v2 binary. Replace HTTP with bound methods and SSE with Wails events. Preserve the renderer as a fragment producer (`RenderBody`). Build with `wails build`, not plain `go build`. Treat platform-specific single-instance behavior as an integration point that must be verified on the target platform.

**10. Consider Go/Wasm for browser-side logic.** If the browser needs Go logic (AST parsing, text processing, query helpers), compile a Go module to Wasm with `GOOS=js GOARCH=wasm`. Keep a split architecture: Go owns logic, a worker (sqlite-wasm, sql.js) owns the engine. Use `syscall/js` for the bridge and poll for the Go module to register itself. This is the sibling pattern, not a replacement for the single-binary shell.

## Key points

- The single-binary Go + SPA pattern exists because local-first tools have three properties that split deployments violate: the data is already in the Go process, the lifecycle is one command, and the artifact is portable.
- `go:embed` is what makes the pattern cheap: a Vite build produces `dist/`, a Go file embeds it, and the HTTP server serves it with one handler.
- Four invariants distinguish the pattern from a naive bundle: reusable Go renderer core, shared origin for API and frontend, read-only data source at runtime, and a single deployment artifact.
- The pattern appears in at least seven projects: Go-Go Parc, Retro Obsidian Publish, go-minitrace web UI, Codebase Browser, Readwise Viewer, Streaming Agent Dashboard, and docsctl.
- Production enhancements are re-runnable DOM augmentation, atomic reload, and the git-sync sidecar. Each solves a specific failure mode that the bare pattern does not.
- The pattern extends to Wails desktop shells (the renderer survives, the transport changes) and to Go/Wasm browser tools (Go owns logic, a worker owns the engine).
- The four recurring failure modes are: SPA-only shells weak for agents/search, one-shot DOM augmentation breaks on reload, fsnotify inode loss, and Wails build tag failure.
- Agent readability is an HTTP routing commitment served before the SPA fallback, not a frontend enhancement. The a14y scores (42 → 97 for docsctl, 62 → 99 for Retro Obsidian Publish) measure this directly.

## Closing

The single-binary Go + SPA pattern is the default local-first application shell across this body of work. It is not the only shell — the SSR sidecar, the Wails desktop binary, and the Go/Wasm browser tool are all siblings — but it is the foundation they extend. Understanding why the pattern exists, what its invariants are, and where it breaks is the prerequisite for building any local-first Go-hosted application. The next bridge report, on derived rebuildable artifacts, covers what happens when the data source itself becomes a derived artifact: SQLite as the canonical store, Bleve as the disposable index, and the rebuild rule that keeps them in sync.
