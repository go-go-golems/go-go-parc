---
title: "Agent-Readable Web Architecture — How We Do It"
aliases:
  - agent-readable web
  - a14y
  - SSR sidecar
  - docsctl SSR
  - agent readability
  - llms.txt
  - defuddle
  - devctl sidecar
tags: [knowledge-base, tribal, web, ssr, react, go, agent, a14y, node, devctl]
status: active
type: knowledge-base
created: 2026-05-31
repos:
  - /home/manuel/code/wesen/go-go-golems/glazed
---

# Agent-Readable Web Architecture — How We Do It

> [!summary]
> Agent readability is a server contract, not a frontend enhancement. A React SPA can remain the interactive UI, but agents need stable HTTP responses: text files must be text, sitemaps must be XML or Markdown, HTML pages must contain metadata and structure, and Markdown mirrors must be reachable without JavaScript. The docsctl docs browser went from 42/100 to 97/100 on the a14y audit by placing the right responsibilities at the right layer: the Go server handles agent-facing files and Markdown mirrors, a Node SSR sidecar provides server-rendered HTML with metadata, and the SPA shell serves as the fallback when the sidecar is unavailable.

## The pattern

Agent readability means the server provides meaningful responses at fetch time, before client-side JavaScript runs. A browser turns an SPA shell into a page. An agent evaluates the HTTP response directly. The server must serve agent-facing content at the correct URLs with the correct content types.

### The routing contract

The Go server routes requests in this order, and the order matters — if `/llms.txt` reaches the SPA fallback, the site fails a14y even if the React app works perfectly:

```
Incoming request
  ├─ /api/*                         → API handler (JSON)
  ├─ well-known agent file          → WellKnownHandler (text/plain, text/markdown, application/xml)
  ├─ .md section URL                → Markdown mirror handler
  ├─ Accept: text/markdown          → Markdown mirror handler (content negotiation)
  ├─ static asset                   → embedded static file handler
  ├─ page request with SSR enabled  → SSR sidecar proxy
  └─ fallback                       → SPA shell (index.html)
```

### The well-known agent files

| URL | Content type | Purpose |
|---|---|---|
| `/llms.txt` | `text/plain` | LLM discovery: site description, package list, top-level section links |
| `/robots.txt` | `text/plain` | Crawler policy and sitemap pointer |
| `/AGENTS.md` | `text/markdown` | Agent operating guide: installation, usage, API, URL scheme |
| `/sitemap.xml` | `application/xml` | Standard XML sitemap with lastmod |
| `/sitemap.md` | `text/markdown` | Human- and agent-readable Markdown sitemap |
| `/index.md` | `text/markdown` | Markdown mirror of the root page with frontmatter |

### Markdown mirrors and content negotiation

Every page URL has a Markdown equivalent:

```
/glazed/_/sections/jq-filter          → HTML page
/glazed/_/sections/jq-filter.md       → Markdown mirror
```

The server also supports content negotiation:

```bash
curl -H 'Accept: text/markdown' http://localhost:8088/glazed/_/sections/jq-filter
```

This makes the site self-describing for coding agents. A future agent fetches `/AGENTS.md`, understands the URL scheme, discovers the API, and knows that `.md` suffix URLs are the preferred plain-text representation.

### The SSR sidecar pattern

The Go server cannot render React itself — the React component tree uses hooks, context, and browser APIs (`window`, `document`, `location`) that require a full Node.js environment. The alternatives were rejected:

| Alternative | Why rejected |
|---|---|
| Embedded V8 (v8go) | No DOM polyfills; impractical browser API surface |
| Embedded goja | No ES modules, no import resolution for Vite-built React |
| WASM (QuickJS) | Same DOM problem; cold-start latency makes per-request rendering expensive |
| Build-time pre-rendering | docsctl supports `--reload-interval` for live-reloading; pre-rendered pages go stale |

The SSR sidecar is a separate Node process that renders React to HTML:

```
Browser/Agent → Go Server (:8088)
                 ├─ /api/* → REST API
                 └─ page request → SSR Proxy → Node Sidecar (:8089)
                                                ├─ fetch API data
                                                ├─ renderToString
                                                └─ return HTML
                                           ↓ on failure
                                           SPA Fallback (index.html)
```

The fallback is deliberate: when the sidecar is down, the browser still loads the React app and fetches data client-side. The user experience degrades gracefully.

### The devctl plugin

The `devctl` plugin orchestrates the two-process development environment:

1. Starts the Go server on port 8088
2. Starts the Node SSR sidecar on port 8089
3. Health-checks both processes
4. Provides process supervision (restart on crash)
5. Wires the Go server's `--ssr-url` flag automatically

### The docsctl deployment pipeline

Documentation publishing goes through a three-part system:

1. **`docsctl publish`** validates a local help SQLite database and uploads it to `docs-registry` with a package-scoped bearer token
2. **`docs-registry`** stores each uploaded database under `/var/lib/glazed-docs/packages/<package>/<version>/<package>.db` and updates `catalog.json`
3. **`docs-browser`** serves the public documentation UI from the same package directory

Publisher authorization is controlled by a Vault-backed `publishers.json` catalog. The registry write API is internal-only (reached through `kubectl port-forward`); the public host (`docs.yolo.scapegoat.dev`) routes only to the browser service.

## Why we do it this way

**Agent readability is a server contract.** The React app does not need to change. The server adds routing for well-known agent files, Markdown mirrors, and content negotiation. The frontend continues to work exactly as before for browsers.

**The SSR sidecar is simpler than embedding a runtime.** A separate Node process provides the full browser API surface that React expects. It can crash independently without taking down the Go server. In Kubernetes, the sidecar runs in the same pod — the network hop is localhost.

**Always have a fallback.** If the sidecar fails, the Go server falls back to the SPA shell. The user gets a degraded experience (no server-rendered metadata) but not a broken page.

**`defuddle` for static content, Playwright for JS-rendered content.** This is the consistent scraper pattern across the project. `defuddle` extracts clean Markdown from web pages by removing clutter. Playwright renders JavaScript and returns the full DOM. Use `defuddle` when the server provides meaningful HTML; use Playwright when only the client-rendered DOM has content.

**The a14y audit drives the work.** Instead of guessing which files agents might want, the audit reports concrete checks with names, expected behavior, and observed behavior. The score went from 42/100 to 97/100 by fixing the specific checks the audit identified.

## Evidence

| Report | Date | Contribution |
|---|---|---|
| [[ARTICLE - Docsctl and Docs-Yolo Documentation Deployment]] | 2026-05-24 | Three-part deployment pipeline: docsctl publish → docs-registry → docs-browser; Vault-backed publisher auth; Kubernetes sidecar deployment |
| [[ARTICLE - Agent a14y for Go-Hosted React Docs - Converting docsctl from SPA Shell to Agent-Readable Site]] | 2026-05-25 | Canonical a14y conversion: 42→97 score, well-known handler, Markdown mirrors, content negotiation, routing order, `.md` suffix convention |
| [[ARTICLE - SSR Sidecar for Go-Hosted React SPAs - A Deep Dive into docsctl Server-Side Rendering]] | 2026-05-25 | SSR sidecar architecture: four components, three runtime bugs (ESM hoisting, Express 5, dual React), Go reverse proxy, devctl plugin |

## Working rules

1. **Agent readability requirements are server-side.** Text files must be text (not JS-rendered), sitemaps must be XML or Markdown, HTML pages must contain metadata and structure, Markdown mirrors must be reachable without JavaScript. The React app does not need to change.

2. **SSR sidecar over embedded rendering.** A separate Node process is simpler than embedding V8 or compiling React to WASM. The sidecar can crash independently without taking down the Go server.

3. **Always have a fallback.** If the sidecar fails, serve the SPA shell. The user gets a degraded experience but not a broken page.

4. **Use `devctl` for development orchestration.** The devctl plugin manages both processes with health checks and process supervision. Don't start the Go server and the Node sidecar manually.

5. **`defuddle` for static content, Playwright for JS-rendered content.** This is the consistent scraper pattern. `defuddle` extracts Markdown; Playwright renders JavaScript.

6. **Routing order must be explicit.** Agent-facing handlers must sit before the SPA fallback. If `/llms.txt` reaches the fallback, the site fails a14y even if the React app works.

7. **`.md` suffix convention for Markdown mirrors.** Every page URL gains a `.md` equivalent. Links in `llms.txt` and `sitemap.md` should point to `.md` URLs so agents get plain text.

8. **`AGENTS.md` is an operating guide, not a marketing page.** Include installation, usage, API, and URL scheme. A future agent should be able to fetch `/AGENTS.md` and understand how to use the site.

9. **The `noExternal` list in Vite SSR config must include `react` and every package that depends on React internals.** The dual-React-instance problem is caused by bundling some React-dependent packages while externalizing `react`. Always bundle `react`, `react-dom`, `react-router-dom`, `@reduxjs/toolkit`, `react-redux`, and `use-sync-external-store`.

10. **The a14y audit must target the Go server (port 8088), not the sidecar (port 8089).** The public contract is the Go server's routing behavior, not the sidecar's rendering in isolation.

## Gotchas

1. **ESM import hoisting breaks the sidecar.** A static `import { renderApp } from './dist/ssr/entry-server.js'` runs before any runtime code — including the `window` mock that the SSR bundle needs. Use a dynamic `await import()` after setting up the mock. This is not a goja bug; it's JavaScript module semantics.

2. **Express 5 breaking changes.** Express 5 requires named wildcards: `app.get('{*path}', handler)` instead of `app.get('*', handler)`. The old syntax throws `PathError: Missing parameter name at index 1: *`.

3. **The dual-React-instance problem.** If `react` is not in Vite's `noExternal` list, Node resolves it from `node_modules/react/` while bundled packages use their own copy. Two React instances cause "Invalid hook call" errors. The fix: add `react` and `use-sync-external-store` to `noExternal`.

4. **Fresh Redux store per SSR request.** The store must be created fresh for each request, not shared. Sharing the store causes data leaks between concurrent requests — one user's data could appear in another user's rendered page.

5. **`docs-registry` is not publicly reachable.** The public host (`docs.yolo.scapegoat.dev`) routes to the browser service only. Publishing requires `kubectl port-forward` to reach the internal registry service. An operator who tries to `docsctl publish` against the public URL will get a connection refused error.

6. **`llms.txt` links must use `.md` extensions.** The a14y `llms-txt.md-extensions` check expects Markdown links to point to Markdown resources. Linking to `/sections/foo` sends the agent to HTML. Linking to `/sections/foo.md` sends the agent to raw Markdown.

7. **The SSR sidecar renders the loading skeleton, not the full content.** `renderToString` renders the component tree in its "loading" state because the RTK Query cache is not pre-populated. The HTML shell has meaningful metadata and structure, but the actual documentation content loads client-side via hydration. This is acceptable for a14y but insufficient for full SSR SEO.

8. **`--reload-interval` invalidates build-time pre-rendering.** docsctl supports live-reloading documentation from a directory. Pre-rendered pages would go stale between reloads. The SSR sidecar renders on each request, so it always reflects current data.

## Related KB entries

- [[On-Ramp/go-cli-with-embedded-spa]] — The Go CLI with embedded SPA pattern that the SSR sidecar extends. The base pattern serves `index.html` from `embed.FS`; the sidecar adds server-rendered HTML.
- [[Tribal/browser-side-processing-for-embedded]] — Browser-side processing for embedded devices. The `defuddle` + Playwright scraper pattern is the server-side counterpart: `defuddle` for static content, Playwright for JS-rendered content.
- [[Tribal/goja-runtime-ownership-and-context-propagation]] — The goja runtime substrate was considered for SSR but rejected because goja lacks ES modules and the DOM polyfills that React requires.
