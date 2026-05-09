---
title: Glazed Static Help Export
aliases:
  - Glaze render-site
  - Glazed Static Help Site
  - GL-012 Static Render
tags:
  - project
  - glazed
  - go
  - react
  - vite
  - help
  - static-site
  - documentation
status: active
type: project
created: 2026-04-09
repo: /home/manuel/workspaces/2026-04-09/glaze-render-static/glazed
---

# Glazed Static Help Export

This project extends the new Glazed help browser work into a second delivery mode: instead of only serving documentation over HTTP with `glaze serve`, the `glaze` binary can now export the same help corpus as a static website with `glaze render-site`. The exported output is a self-contained directory tree with the embedded SPA, a runtime config file, and a static JSON snapshot of all help sections.

The important idea is that this is not a second documentation system. It is a new delivery adapter for the same underlying help model, store, and frontend that power the live browser.

> [!summary]
> The current system has four important identities:
> 1. a **new CLI export command**: `glaze render-site`
> 2. a **static snapshot pipeline** that serializes the canonical help store into JSON files
> 3. a **dual-mode frontend** that can browse either live `/api/...` endpoints or pre-rendered `site-data/*.json`
> 4. a **publishing workflow** that now includes tests, built-in help docs, ticket research, diary tracking, and reMarkable delivery

## Why this project exists

The earlier `glaze serve` work solved browser-based help browsing, but it still assumed that a Go server process would be running. That is convenient for local exploration and embedding into another HTTP service, but it is the wrong shape for several other use cases:

- publishing Glazed documentation to a static host
- attaching browsable help docs to build artifacts or release bundles
- reviewing a frozen documentation snapshot without a live backend
- reusing the browser UI in environments where only static files can be deployed

The static export work exists to close that gap while preserving the strongest part of the serving architecture: one canonical help model, one parser, one store, and one SPA.

This project also matters architecturally because it validates the design decision made during the `serve` cleanup: once the data model and frontend are clean, a second delivery mode should look like an output transform, not like a parallel stack.

## Current project status

The core feature is now implemented and documented.

### What exists today

- `glaze render-site` is wired into the root CLI in `cmd/glaze/main.go`
- explicit path-loading semantics match `glaze serve`
- a shared loader package now owns local markdown file and directory loading
- the exporter emits:
  - frontend assets
  - `site-config.js`
  - `site-data/health.json`
  - `site-data/sections.json`
  - `site-data/sections/<slug>.json`
  - topic/command/flag/top-level/default indexes
  - `site-data/manifest.json`
- the frontend can run in either:
  - live server mode
  - static JSON mode
- section selection is now route-backed through hash URLs
- frontend coverage exists for:
  - static/server runtime path selection
  - route-driven section selection
- a user-facing built-in help page now explains static export and hosting
- ticket `GL-012-STATIC-RENDER` contains:
  - design doc
  - phased task list
  - diary
  - changelog
- the ticket bundle has been uploaded to reMarkable

### What is still incomplete

- the remaining planned task is a developer validation playbook for exported sites
- the `--base-path` story is implemented, but it still deserves more real-world hosting validation
- there is not yet any SEO-oriented prerendered HTML beyond the SPA shell
- the static snapshot package is still internal to this feature rather than framed as a reusable library boundary

## Relationship to the earlier Glazed Serve work

This note is best understood as a direct continuation of [[PROJ - Glazed Serve - Help Browser, Embedded Docs, and SPA]].

That earlier work established:

- a canonical `model.Section`
- a canonical help store
- a server API over `/api/*`
- an embedded React SPA under `pkg/web`

This project adds a second delivery path:

- `serve` starts a live HTTP process
- `render-site` writes a frozen browser artifact to disk

The most important success criterion was that both modes should browse the same content through the same frontend, not drift into separate implementations.

## Project shape

There are five layers in the current static export implementation:

1. **Documentation source layer**
   - built-in docs loaded by `pkg/doc`
   - optional user-supplied markdown files or directories

2. **Help model and storage layer**
   - `pkg/help/model`
   - `pkg/help/store`
   - `pkg/help/help.go`

3. **Delivery adapter layer**
   - `pkg/help/server` for live HTTP
   - `pkg/help/site` for static export
   - `pkg/help/loader` for shared explicit-path loading

4. **Frontend runtime layer**
   - `web/src/services/api.ts`
   - `web/src/App.tsx`
   - `HashRouter`-based navigation

5. **Distribution/build layer**
   - `cmd/build-web/main.go`
   - `pkg/web/dist`
   - `pkg/web/static.go`
   - exported static site directories such as `/tmp/glaze-static-site`

## Architecture

```mermaid
flowchart TD
    A[Markdown docs\npkg/doc or explicit paths] --> B[model.ParseSectionFromMarkdown]
    B --> C[help.Store / canonical section store]

    C --> D[server.NewServeHandler]
    C --> E[site.RenderSite]

    D --> F[/api/health]
    D --> G[/api/sections]
    D --> H[/api/sections/{slug}]

    E --> I[site-data/sections.json]
    E --> J[site-data/sections/{slug}.json]
    E --> K[site-data/indexes/*.json]
    E --> L[site-config.js]
    E --> M[index.html + assets]

    N[React SPA] --> O[services/api.ts runtime mode]
    O --> D
    O --> I
    O --> J

    style C fill:#e8f5e9,stroke:#2e7d32
    style E fill:#fff3e0,stroke:#ef6c00
    style N fill:#e3f2fd,stroke:#1565c0
```

The key architectural decision is that static export happens *after* the help store is already populated. The exporter does not own alternate parsing rules or alternate content transforms. It serializes the same store-backed state that the live server would expose.

## Important code locations

The main files for the current implementation are:

- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/cmd/glaze/main.go`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/pkg/help/site/render.go`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/pkg/help/site/render_test.go`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/pkg/help/loader/paths.go`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/pkg/help/server/serve.go`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/web/src/services/api.ts`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/web/src/App.tsx`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/web/src/services/api.test.ts`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/web/src/App.test.tsx`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/pkg/doc/topics/26-export-help-as-static-website.md`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/ttmp/2026/04/09/GL-012-STATIC-RENDER--add-static-website-rendering-to-cmd-glaze/`

## Implementation details

The core implementation story is that static export was added by reusing the existing help stack as deeply as possible.

### 1. Command wiring and settings

The new command is registered in `cmd/glaze/main.go` alongside `serve`. The exporter is configured through a deterministic settings struct in `pkg/help/site/render.go`:

- `OutputDir`
- `SiteTitle`
- `BasePath`
- `DataDir`
- `Overwrite`
- `Paths`

That shape is important because it keeps all file-system and runtime-path decisions explicit and serializable.

### 2. Shared path loading

One of the first refactors in this work was extracting explicit path loading out of `pkg/help/server/serve.go` into `pkg/help/loader/paths.go`.

That gives both `serve` and `render-site` the same semantics:

- no explicit paths means "use the docs already loaded into the help system"
- explicit paths mean "clear the preloaded docs and replace them with only the sections discovered from these paths"

That behavior matters because `cmd/glaze/main.go` preloads built-in docs before command execution starts.

### 3. Static snapshot generation

The exporter walks the existing help store and serializes a stable, sorted snapshot. The high-level logic is:

```text
decode render-site settings
if explicit paths were provided:
    replace the store contents using the shared loader

query store in canonical order
sort by Order, then Slug

prepare output directory
copy embedded frontend assets
write site-config.js

for each section:
    write section detail JSON
    collect summary
    collect topic / command / flag indexes
    collect top-level and default slugs

write list payloads
write index payloads
write manifest
```

The important design point is that the static payloads are derived from `server.SummaryFromModel(...)` and `server.DetailFromModel(...)`. That means the live server and static export share the same API-facing section shapes.

### 4. Frontend dual-mode runtime

The frontend did not become a second app. Instead, `web/src/services/api.ts` now resolves a runtime mode from `window.__GLAZE_SITE_CONFIG__`.

In server mode it uses:

- `/api/health`
- `/api/sections`
- `/api/sections/{slug}`

In static mode it uses:

- `site-data/health.json`
- `site-data/sections.json`
- `site-data/sections/{slug}.json`

The frontend therefore stays conceptually the same. Only its transport changes.

### 5. Route-backed section selection

Before static export, section selection in the SPA was still local-state driven. That was acceptable for a live browser session but wrong for exported documentation because readers need bookmarkable URLs.

The current implementation now drives selection from hash routes such as:

```text
#/sections/documentation-guidelines
```

That change is important for both:

- static hosting compatibility
- shareable deep links

### 6. Generated output shape

The exported site now looks like this at a stable conceptual level:

```text
output-dir/
  index.html
  site-config.js
  assets/
  site-data/
    health.json
    sections.json
    sections/<slug>.json
    indexes/
      topics.json
      commands.json
      flags.json
      top-level.json
      defaults.json
    manifest.json
```

That directory structure is simple enough to host on a plain file server while still preserving enough metadata for the SPA to behave like the live browser.

## Current user-facing commands

The main new command is:

```bash
go run ./cmd/glaze render-site
```

The most useful current invocations are:

```bash
go run ./cmd/glaze render-site ./pkg/doc --output-dir /tmp/glaze-static-site --overwrite
```

```bash
go run ./cmd/glaze help render-site
```

```bash
go run ./cmd/glaze help export-help-static-website
```

To preview an exported site locally:

```bash
python3 -m http.server 8123 --directory /tmp/glaze-static-site
```

## Validation and review status

This project is in a good state for a feature branch:

- backend export code exists
- backend tests exist
- frontend static-mode tests exist
- user-facing help docs exist
- ticket research and diary exist
- reMarkable bundles exist

The key commits in the implementation sequence are:

- `8181daa` — `feat(help): add static render-site export`
- `1828776` — `test(web): cover static help routing`
- `bb73490` — `docs(help): add static export guide`

Validation already performed includes:

- `go test ./pkg/help/server ./pkg/help/site ./cmd/glaze`
- `go test ./pkg/web ./pkg/help/server ./pkg/help/site`
- `cd web && pnpm test`
- `cd web && pnpm build`
- `go run ./cmd/build-web`
- `go run ./cmd/glaze render-site ./pkg/doc --output-dir /tmp/glaze-static-site --overwrite`
- browser-level smoke validation through a local static file server
- `docmgr doctor --ticket GL-012-STATIC-RENDER --stale-after 30`

## Important project docs

The main current documentation lives in the repo ticket workspace:

- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/ttmp/2026/04/09/GL-012-STATIC-RENDER--add-static-website-rendering-to-cmd-glaze/index.md`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/ttmp/2026/04/09/GL-012-STATIC-RENDER--add-static-website-rendering-to-cmd-glaze/design-doc/01-static-help-website-rendering-architecture-and-implementation-guide.md`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/ttmp/2026/04/09/GL-012-STATIC-RENDER--add-static-website-rendering-to-cmd-glaze/reference/01-diary.md`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/ttmp/2026/04/09/GL-012-STATIC-RENDER--add-static-website-rendering-to-cmd-glaze/tasks.md`
- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/ttmp/2026/04/09/GL-012-STATIC-RENDER--add-static-website-rendering-to-cmd-glaze/changelog.md`

There is also a built-in end-user help page in the main documentation corpus:

- `/home/manuel/workspaces/2026-04-09/glaze-render-static/glazed/pkg/doc/topics/26-export-help-as-static-website.md`

## Open questions

- Should `glaze serve` later gain an `--export` shortcut that delegates to `render-site`?
- Should the static export eventually emit per-section prerendered HTML for better indexing and previews?
- Should the static snapshot builder become a reusable package boundary for other Go CLIs using the Glazed help stack?
- How much real-world hosting validation is needed before `--base-path` can be considered fully hardened?

## Near-term next steps

- add the remaining developer validation playbook
- exercise `--base-path` on one or two non-root hosting layouts
- decide whether the static snapshot layer should remain feature-local or become reusable
- consider whether more frontend filtering should move into precomputed indexes or remain client-side

## Project working rule

> [!important]
> Treat static export as a second delivery mode for the *same* help system.
> If a future change starts introducing a second parser, a second section shape, or a second browser implementation, that is probably architectural drift and should be resisted.
