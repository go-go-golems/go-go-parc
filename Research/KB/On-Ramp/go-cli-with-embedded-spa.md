---
title: "Go CLI with Embedded SPA"
aliases:
  - Go embedded SPA
  - single-binary Go web app
  - Go CLI serving React
  - embedded Vite app in Go
tags: [knowledge-base, on-ramp, go, spa, react, vite, embed, cli, documentation]
status: active
type: knowledge-base
created: 2026-05-11
---

# Go CLI with Embedded SPA

> [!summary]
> A Go CLI with an embedded SPA is a single binary that serves both backend API routes and a built frontend bundle, usually from `embed.FS`. We use this shape for documentation/help browsers and code browsers where distribution should be as simple as copying one executable.

Related tribal pattern: [[Tribal/canonical-doc-model-across-delivery-modes]]

## The idea in one paragraph

A Go CLI with an embedded SPA is a command-line program that also acts as a small web server. At build time, a frontend tool such as Vite produces static assets. Go embeds those assets with `//go:embed`, registers API routes with `net/http`, and serves the SPA from the same process. The result feels like a local web application but ships like a CLI: one binary, no Node runtime, no separate web server, and no manual asset directory to keep next to the executable.

## Why we care

This pattern appears in the Glazed help browser, Glazed static help export, Codebase Browser, and related docs-as-product work. These projects are not general SaaS apps. They are local documentation or inspection tools. The user should not have to run Postgres, Node, nginx, and a backend just to browse help pages or inspect a source index.

The embedded-SPA shape gives us a useful compromise:

- Go owns the CLI, API, index loading, filesystem access, and release artifact.
- React/Vite owns the interactive browser UI.
- `go build` produces the thing users run.
- static export can reuse the same frontend model when a live server is unnecessary.

The important design lesson is that the SPA is a delivery surface over a backend model. It should not become the authoritative documentation or index model. That is why this On-Ramp pairs with [[Tribal/canonical-doc-model-across-delivery-modes]].

## The 5 things to understand

### 1. `embed.FS` turns build artifacts into Go data

Go's `embed` package lets files become part of the compiled binary:

```go
//go:embed dist/*
var assets embed.FS
```

A typical production build runs Vite first, then Go embeds the resulting `dist/` directory. At runtime, the binary serves those files through `http.FileServer` or a custom handler. The user does not need the original `ui/` directory or `node_modules`; those were build-time inputs.

The same mechanism can embed more than the SPA bundle. Codebase Browser embeds the UI, index JSON, source snapshots, and markdown documentation pages. Glazed embeds help pages and serves them through a browser UI. The exact files differ, but the packaging model is the same.

### 2. API routes and SPA routes must not fight

A Go server that hosts an SPA usually has two kinds of routes:

```text
/api/...       backend JSON endpoints
/assets/...    built JS/CSS/image files
/              SPA entrypoint
/symbol/foo    SPA route that should still return index.html
```

The tricky bit is the SPA fallback. Browser-side routers often own paths like `/packages/foo` or `/symbols/bar`. If a user refreshes that page, the Go server sees a request for `/symbols/bar`. It should usually return `index.html`, not `404`, so the frontend router can take over.

The working rule is: reserve a clear API prefix such as `/api/`, serve known static assets directly, and route unknown non-API paths to the SPA entrypoint. If you also support `file://` static artifacts, consider `HashRouter` because normal history routes do not work reliably from local files.

### 3. Development and production are usually different modes

During development, Vite's dev server is better than rebuilding embedded assets after every UI change. Production should not depend on Vite.

A common split is:

| Mode | Frontend source | Backend source |
|---|---|---|
| Dev | Vite dev server on `:3000` | Go API on `:3001`, proxied from Vite |
| Production | embedded `dist/` files | same Go binary serves API and SPA |
| Static export | built files on disk | no live Go server, data precomputed |

Codebase Browser uses this split directly: `make dev-frontend` runs Vite, `make dev-backend` runs Go, and production build embeds the final bundle. Glazed's help browser similarly treats the web UI as a view over structured help data, not as a separate app server.

### 4. The frontend should talk to a stable model, not to implementation details

The frontend should ask for product concepts:

```text
GET /api/sections
GET /api/symbols/:id
GET /api/xref/:id
GET /api/doc/:slug
```

It should not care whether the answer came from an embedded JSON file, a SQLite database, a markdown directory, another binary's export, or a live in-memory store. That is how Codebase Browser can move from live HTTP to static WASM to SQLite without rewriting every component, and how Glazed Help can serve embedded pages or external exported help through one browser.

This separation is the difference between an embedded SPA and an accidental second backend in TypeScript.

### 5. The build pipeline is part of the product

An embedded SPA is only pleasant if the build is boring. The usual production sequence is:

```text
pnpm install/build frontend
copy or emit dist/ into Go embed directory
go generate ./...
go build -tags embed ./cmd/tool
```

Some projects use Dagger to make the Node/Vite/pnpm part hermetic and cacheable. Codebase Browser uses a Dagger-orchestrated Node path for TypeScript tooling, with a local fallback for machines without Docker. The important invariant is not "always use Dagger"; it is "the final Go binary should be reproducible and should not accidentally depend on local `node_modules`."

## The gotchas we've hit

### SPA refreshes returning 404

If the Go server treats every unknown path as a missing file, browser refresh breaks on frontend routes. The fix is to make the server distinguish API/static paths from SPA routes and return `index.html` for the latter. Static `file://` delivery may need `HashRouter` instead of normal history routing.

### Static export becoming a second help system

Glazed Static Help Export would have been fragile if it built a separate static-only help representation. The correct approach was to project the same help model into another delivery mode. The browser should render the same section data whether it came from live serve, static export, JSON, SQLite, or another Glazed binary.

### Build-time Node leaking into runtime assumptions

Codebase Browser needs Node/TypeScript tooling at build time. The final browser should not require Node at runtime. Dagger and local fallback are both acceptable as build mechanisms, but the release artifact should be a Go binary or a static directory that has already absorbed the frontend build.

### Nil slices and JSON shape drift

Go's nil slices marshal as `null`, not `[]`. Codebase Browser hit a frontend failure when xref response fields like `usedBy` were `null` and the React code expected arrays. API response shapes are contracts; initialize empty slices when the frontend expects arrays.

### Letting the SPA define the canonical model

The frontend is tempting because it is where the product is visible. But if React components invent the canonical model, CLI export, static export, server APIs, and SQLite snapshots will drift. Keep the model in Go/shared schema/database, and make the SPA a renderer over that model.

## Where to go deeper

1. Go `embed` package documentation — the core mechanism for putting built assets inside a binary.
2. Vite production build documentation — how `dist/` assets are generated and how base paths affect deployment.
3. [[Tribal/canonical-doc-model-across-delivery-modes]] — our pattern for keeping live/static/export/browser modes on one documentation model.
4. [[PROJ - Codebase Browser - Embedded Go+TS Doc Server with Live Source Snippets]] — full example of an embedded code/documentation browser.
5. [[PROJ - Glazed Help Export and External Serve Sources - Technical Project Report]] — structured help as portable data served through a browser.

### Related PARC project reports

- [[PROJ - Glazed Serve - Help Browser, Embedded Docs, and SPA]] — embedded help browser inside a Go CLI.
- [[PROJ - Glazed Static Help Export - render-site and Static Snapshot Publishing]] — static delivery as a second projection of the same help system.
- [[PROJ - Codebase Browser - Embedded Go+TS Doc Server with Live Source Snippets]] — one binary serving API, docs, source snippets, and React SPA.
- [[PROJ - Codebase Browser - Static WASM Build and SQLite Prototype]] — static artifact and browser-side query evolution.
- [[PROJ - Glazed Help Export and External Serve Sources - Technical Project Report]] — help export/import and serve modes over one structured help store.

For making this Go+SPA pattern agent-readable (SSR sidecar, well-known agent files, Markdown mirrors, a14y audit), see [[Tribal/agent-readable-web-architecture]].
