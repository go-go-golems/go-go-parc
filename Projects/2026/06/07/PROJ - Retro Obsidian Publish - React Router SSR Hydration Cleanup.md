---
title: "Retro Obsidian Publish — React Router SSR Hydration Cleanup"
aliases:
  - Publish Vault SSR Hydration Cleanup
  - Retro Obsidian Publish SSR Report
description: A complete case study of replacing a divergent SSR/SPA architecture with a single hydratable React tree using React Router, including live debugging of duplicate React instances and real hydration failures.
status: published
type: project
created: 2026-06-07
repo: /home/manuel/workspaces/2026-06-04/publish-vault-ssr/publish-vault
topics: [retro-obsidian-publish, ssr, hydration, react-router, web-architecture]
tags: [project, retro-obsidian-publish, ssr, hydration, react-router, web-architecture, case-study]
---

# Retro Obsidian Publish — React Router SSR Hydration Cleanup

## Introduction

Retro Obsidian Publish is a self-hosted, read-only Obsidian vault viewer. It consists of three main layers:

1. A Go backend that loads vault Markdown files, builds a full-text search index, exposes a REST API (`/api/notes`, `/api/tree`, `/api/config`, etc.), and serves the React SPA's static assets.
2. A Node.js SSR sidecar (Express server) that receives page requests from the Go server's reverse proxy, pre-fetches data from the Go API, renders a React tree to an HTML string via `react-dom/server`, injects SEO meta tags, and returns the complete HTML page.
3. The browser, which downloads the HTML page, executes JavaScript, and mounts the full interactive React SPA.

The SSR sidecar was designed as a "server-rendered preview" — a simplified HTML page that crawlers and agents can read without executing JavaScript. The browser was designed to completely replace that preview with the full interactive app. That made the first release easy, but it created a long-term maintenance burden: **the server and client have two different component trees, two different route definitions, two different title systems, and two different layout behaviors.**

This report documents the migration from that divergent architecture to a **single hydratable React tree** using React Router. It covers the analysis, the implementation plan, the actual code changes, and the live debugging of real production-class failures that only appeared during live testing.

## The Problem: Two Trees, One Site

### The divergent architecture

The original architecture can be visualized as two parallel rendering paths that share data but never share code:

```
                         ┌─────────────────────────────────────────────┐
                         │           SSR SIDE (Node.js Express)         │
                         │                                              │
                         │  1. Fetch /api/config, /api/notes, etc.     │
                         │  2. Build simplified "SSRNotePage"          │
                         │     - Just <h1> + note HTML + backlinks     │
                         │  3. renderToString() → HTML string          │
                         │  4. Inject meta tags, title, noscript       │
                         │  5. Return HTML                             │
                         │                                              │
                         │  SSR components:                            │
                         │    SSRNotePage, SSRHomePage, SSRSearchPage    │
                         │    (hand-built React.createElement calls)    │
                         └───────────────┬─────────────────────────────┘
                                         │ HTML response
                                         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                              BROWSER                                     │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │ 1. Browser receives HTML with SSR content in <div id="root">    │     │
│  │ 2. entry-client.tsx: root.textContent = ""                     │     │
│  │    (completely clears SSR content)                              │     │
│  │ 3. createRoot(root).render(<App />)                            │     │
│  │    (mounts entirely new tree)                                   │     │
│  │ 4. App → VaultLayout → Router (Wouter) → NotePage              │     │
│  │                                                                  │     │
│  │ Client components:                                              │     │
│  │   App, VaultLayout, NotePage, SearchPage, NotFoundPage          │     │
│  │   (full interactive app with sidebar, backlinks panel, etc.)    │     │
│  └─────────────────────────────────────────────────────────────────┘     │
│                                                                          │
│  Result: Two component trees that do the same job with different code.   │
└──────────────────────────────────────────────────────────────────────────┘
```

This divergence manifests in several concrete ways:

**1. Duplicate route logic.** Route declarations live in `App.tsx` using Wouter:

```tsx
// App.tsx — client routes
<Switch>
  <Route path="/" component={HomeRedirect} />
  <Route path="/note/*" component={NoteRoute} />
  <Route path="/search" component={SearchRoute} />
  <Route component={NotFoundPage} />
</Switch>
```

And route parsing lives in two places:
- `entry-server.tsx` has a custom `parseRoute()` function
- `server.mjs` has another custom `parseRoute()` function

If the route URLs ever need to change, both must be updated independently.

**2. Duplicate page components.** The SSR side uses simplified components:

```tsx
// entry-server.tsx — SSR-only note page
function SSRNotePage({ note }) {
  return <div className="ssr-note">
    <h1>{note.title}</h1>
    <div dangerouslySetInnerHTML={{__html: note.html}} />
    {/* backlinks */}
  </div>;
}
```

While the client uses the full `NotePage` component with sidebar, backlinks panel, breadcrumb navigation, and responsive layout. These two components share no code.

**3. Divergent title behavior.** The SSR correctly includes note-specific titles:

```html
<!-- SSR HTML -->
<title>Research Institute Guidelines — current</title>
<meta property="og:title" content="Research Institute Guidelines — current" />
```

But the client React app's `useEffect` in `App.tsx` overwrites this with only the site-level config:

```tsx
// App.tsx — client title effect
useEffect(() => {
  document.title = config?.pageTitle || config?.vaultName || "Retro Obsidian Publish";
}, [config?.pageTitle, config?.vaultName]);
```

Since `config.pageTitle` defaults to the vault directory name ("current"), every page shows "current" in the browser tab, regardless of which note is displayed. The SSR title is correct; the client title is wrong.

**4. The sidebar omission.** The SSR only renders note content (title, tags, HTML body, backlinks). It does not render the sidebar with file tree navigation. That is intentional — the sidebar is an interactive element that doesn't make sense before JavaScript loads. But it means crawlers that don't execute JavaScript see only note content without navigation context.

### The goal

The goal of the migration was to:

1. Use **one route table** (React Router) shared by server and client.
2. Render the **real `AppRoutes` component tree** during SSR (instead of simplified SSR-only pages).
3. Hydrate that same tree in the browser with `hydrateRoot()` (instead of clearing the DOM and remounting).
4. Eliminate Wouter entirely.
5. Align title behavior between SSR and client.

### Why this matters

A divergent SSR/client architecture creates these long-term problems:

- **Maintenance burden**: Every route change, component update, or layout fix must be implemented in two places.
- **Title bugs**: The client title system cannot easily include per-note information because it only reads from site-level config.
- **SEO inconsistency**: The SSR renders content the client component tree never sees, and vice versa.
- **Hydration impossibility**: Without a shared tree, the browser must clear SSR content and remount, which means the SSR output is only useful as a "preview" rather than as hydration seed.

## The Solution Architecture

### High-level diagram

The target architecture after migration:

```
                         ┌─────────────────────────────────────────────┐
                         │         SSR SIDE (Node.js Express)           │
                         │                                              │
                         │  1. Fetch /api/config, /api/notes, etc.     │
                         │  2. Preload RTK Query cache                 │
                         │  3. renderToString(                         │
                         │  4.   <Provider store={store}>              │
                         │  5.     <StaticRouter location={url}>       │
                         │  6.       <AppRoutes />   ← SAME tree       │
                         │  7.     </StaticRouter>                     │
                         │  8.   </Provider>                           │
                         │  9.     )                                   │
                         │ 10. Inject meta tags, title                 │
                         │ 11. Return HTML                             │
                         └───────────────┬─────────────────────────────┘
                                         │ HTML with hydrated markup
                                         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                              BROWSER                                     │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │ 1. Browser receives HTML with SSR content in <div id="root">    │     │
│  │ 2. entry-client.tsx: hydrateRoot(root, ...)                    │     │
│  │    (attaches event handlers to EXISTING DOM)                    │     │
│  │ 3. hydrateRoot(                                                 │     │
│  │ 4.   <Provider store={store}>                                   │     │
│  │ 5.     <BrowserRouter>                                          │     │
│  │ 6.       <AppRoutes />   ← SAME tree                           │     │
│  │ 7.     </BrowserRouter>                                         │     │
│  │ 8.   </Provider>                                                │     │
│  │ 9. )                                                           │     │
│  │                                                                  │     │
│  │ Result: ONE component tree, two rendering modes.                │     │
│  │         No DOM clearing. No remounting.                         │     │
│  └─────────────────────────────────────────────────────────────────┘     │
│                                                                          │
│  Key difference: StaticRouter on server → BrowserRouter on client.       │
│  Everything between them (AppRoutes, VaultLayout, NotePage) is shared.   │
└──────────────────────────────────────────────────────────────────────────┘
```

The key insight: **the only difference between server and client is the router wrapper.** Everything else — `VaultLayout`, `NotePage`, `Sidebar`, `BacklinksPanel` — is shared code rendered in both directions.

### Route architecture

React Router provides two router components for the two environments:

- **`StaticRouter`** (server): A router that does not manage history or perform navigation. It simply provides routing context for `useNavigate`, `useLocation`, `useParams`, etc. It accepts a `location` prop indicating the current URL.

- **`BrowserRouter`** (client): A standard router that uses the HTML5 History API (`pushState`, `popState`) to manage URL changes and trigger navigation between pages.

```tsx
// Server: wraps AppRoutes in StaticRouter with the request URL
<StaticRouter location="/note/philosophy/epistemology">
  <AppRoutes />
</StaticRouter>

// Client: wraps AppRoutes in BrowserRouter for live navigation
<BrowserRouter>
  <AppRoutes />
</BrowserRouter>
```

`AppRoutes` exports a router-agnostic route table:

```tsx
export function AppRoutes() {
  const { data: config } = useGetConfigQuery();

  useEffect(() => {
    // Title is owned by each page component, not here
  }, [config?.pageTitle, config?.vaultName]);

  return (
    <VaultLayout vaultName={config?.vaultName}>
      <Routes>
        <Route path="/" element={<HomeRedirect />} />
        <Route path="/note/*" element={<NoteRoute />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </VaultLayout>
  );
}
```

### Data loading and hydration

The existing RTK Query architecture was already compatible with SSR hydration:

```tsx
// 1. Server pre-fetches data from Go API
const [config, notes, tree] = await Promise.all([
  fetchAPI("/api/config"),
  fetchAPI("/api/notes"),
  fetchAPI("/api/tree"),
]);
const note = fetchAPI(`/api/notes/${slug}`);

// 2. Server seeds RTK Query cache
store.dispatch(vaultApi.util.upsertQueryData("getConfig", undefined, config));
store.dispatch(vaultApi.util.upsertQueryData("listNotes", undefined, notes));
store.dispatch(vaultApi.util.upsertQueryData("getTree", undefined, tree));
store.dispatch(vaultApi.util.upsertQueryData("getNote", slug, note));

// 3. Server serializes store state
const serialized = JSON.stringify(store.getState());

// 4. Server injects into HTML
htmlPage = htmlPage.replace(
  "</head>",
  `<script>window.__PRELOADED_STATE__=${serialized}</script></head>`
);

// 5. Browser restores state before hydrateRoot
const preloadedState = window.__PRELOADED_STATE__;
const store = makeStore(preloadedState);

// 6. Browser hydrates with same cache
hydrateRoot(root, <Provider store={store}><AppRoutes /></Provider>);
```

This pattern means the React components see the same data on server and client during the first render. No double-fetching. No loading flicker.

### Title architecture

The title is now owned by each page component rather than by a global `useEffect` in the router shell:

```tsx
// NotePage.tsx — note page owns its title
const { data: note } = useGetNoteQuery(slug);
const { data: config } = useGetConfigQuery();

useEffect(() => {
  if (!note) return;
  const siteTitle = config?.pageTitle || config?.vaultName || "Retro Obsidian Publish";
  document.title = `${note.title} — ${siteTitle}`;
}, [config?.pageTitle, config?.vaultName, note]);
```

```tsx
// SearchPage.tsx — search page owns its title
useEffect(() => {
  const siteTitle = config?.pageTitle || config?.vaultName || "Retro Obsidian Publish";
  document.title = `Search — ${siteTitle}`;
}, [config?.pageTitle, config?.vaultName]);
```

The router shell's `useEffect` only handles non-note, non-search pages (like `/` when it shows a static home):

```tsx
// App.tsx — only handles pages that don't have their own title
useEffect(() => {
  // /, /note/*, /search → title owned by page component
  if (location.pathname === "/" || location.pathname.startsWith("/note/") || location.pathname === "/search") return;
  document.title = config?.pageTitle || config?.vaultName || "Retro Obsidian Publish";
}, [config?.pageTitle, config?.vaultName, location.pathname]);
```

## Implementation Phases

The migration was executed in six focused phases, each committed separately:

### Phase 0: Documentation and safety commit

Before touching code, all existing ticket documents were committed to establish a known baseline:

```bash
git add ttmp/vocabulary.yaml ttmp/2026/06/07/RETRO-SEO-009--...
git commit -m "Docs: plan SEO SSR hydration cleanup"
```

This ensures that if anything goes wrong during implementation, the documentation of the plan is preserved.

### Phase 1: Add React Router dependency

```bash
cd web && pnpm add react-router-dom react-router
```

`react-router-dom` provides `BrowserRouter`, `Routes`, `Route`, `useNavigate`, `useParams`, `useLocation` for the client.
`react-router` (direct dependency) provides `StaticRouter` for the server — note that in React Router v7, `StaticRouter` is exported from `react-router` itself, not from `react-router-dom/server` (an older API that no longer exists).

Validation:

```bash
pnpm --dir web check          # TypeScript type checking passes
```

Commit: `web: add React Router dependency`

### Phase 2: Migrate client routing from Wouter to React Router

Five files were changed to replace Wouter imports and APIs with React Router equivalents:

| File | Wouter API | React Router API |
|------|-----------|------------------|
| `App.tsx` | `Route`, `Switch`, `useLocation` from `"wouter"` | `Routes`, `Route`, `useLocation`, `useParams` from `"react-router-dom"` |
| `App.tsx` | `props.params["*"]` for wildcard | `useParams()["*"]` for wildcard |
| `VaultLayout.tsx` | `useLocation` → `[, navigate]` destructuring | `useNavigate` → `const navigate = useNavigate()` |
| `NotePage.tsx` | `useLocation` → `[, navigate]` destructuring | `useNavigate` → `const navigate = useNavigate()` |
| `SearchPage.tsx` | `useLocation` → `[, navigate]` destructuring | `useNavigate` → `const navigate = useNavigate()` |
| `NotFound.tsx` | `useLocation` → `[, setLocation]` destructuring | `useNavigate` → `const navigate = useNavigate()` |

The `Switch` component from Wouter was replaced by `Routes` from React Router. Note the API difference:

- Wouter: `<Route path="/" component={HomeRedirect} />`
- React Router: `<Route path="/" element={<HomeRedirect />} />`

React Router uses the `element` prop (render prop pattern) instead of `component`. This is a required API change.

The wildcard parameter extraction also changed:

- Wouter: `props.params["*"]` (from `useLocation` params object)
- React Router: `useParams()["*"]` (from the `useParams` hook)

The `App.tsx` was also restructured to export `AppRoutes` as a router-agnostic component:

```tsx
// Before: Router was the top-level component
function Router() {
  return (
    <VaultLayout>
      <Switch>...</Switch>
    </VaultLayout>
  );
}
export default function App() {
  return <Provider store={store}><Router /></Provider>;
}

// After: AppRoutes is router-agnostic; entry points choose the router
export function AppRoutes() {
  return (
    <VaultLayout>
      <Routes>...</Routes>
    </VaultLayout>
  );
}
export default function App() {
  return <Provider store={store}><BrowserRouter><AppRoutes /></BrowserRouter></Provider>;
}
```

Commit: `web: migrate client routing to React Router`

### Phase 3: Consolidate SSR onto the real app tree

This was the core architectural change. The entry point file `entry-server.tsx` was completely rewritten:

```tsx
// Before: hand-built SSR components
function SSRNotePage({ note }) {
  return React.createElement("div", { className: "ssr-note" }, [
    React.createElement("h1", null, note.title),
    // ... tags, body, backlinks
  ]);
}

export async function renderApp(url, data) {
  const store = makeStore();
  await preloadCache(store, data, slug);

  // Route parsing and component selection — duplicated from client
  const route = parseRoute(url);
  let content;
  if (route.type === "note" && data.note) {
    content = React.createElement(SSRNotePage, { note: data.note });
  } else if (route.type === "home") {
    content = React.createElement(SSRHomePage, { notes: data.notes, config: data.config });
  }

  const html = renderToString(<Provider store={store}>{content}</Provider>);
  return { html, preloadedState: store.getState() };
}
```

```tsx
// After: real AppRoutes under StaticRouter
import { StaticRouter } from "react-router";
import { AppRoutes } from "./App";

export async function renderApp(url, data) {
  const store = makeStore();
  await preloadCache(store, data, slug);

  const html = renderToString(
    <Provider store={store}>
      <StaticRouter location={url}>
        <AppRoutes />
      </StaticRouter>
    </Provider>
  );

  return { html, preloadedState: store.getState() };
}
```

The `extractNoteSlug()` helper replaced the old `parseRoute()` function — it simply extracts the note slug from a URL for cache key preloading. The full routing logic lives in `AppRoutes`.

The server.mjs was also updated to preload the home note for the `/` route, since `/` now renders `HomeRedirect` → `NotePage(index-slug)` instead of a dedicated SSR home page.

Commit: `web: render real app tree during SSR hydration`

### Phase 4: Replace remount with hydrateRoot

The client entry point was changed from a "clear and remount" pattern to a hydrate pattern:

```tsx
// Before: clear + remount
root.textContent = "";
createRoot(root).render(<App />);
```

```tsx
// After: hydrate
hydrateRoot(
  root,
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </Provider>
  </React.StrictMode>
);
```

The `window.__PRELOADED_STATE__` is still read before hydration. No DOM clearing.

Commit: (merged into Phase 3)

### Phase 5: Make render output deterministic

Two sources of non-deterministic first-render output were identified and fixed:

**1. UI state based on viewport size.** The `uiSlice` initial state used `window.innerWidth` to decide if the sidebar should be open:

```tsx
// Before: reads window at module load time — server sees "undefined" → true, client sees actual viewport
sidebarOpen: typeof window !== "undefined" ? window.innerWidth >= 768 : true,
```

If the server renders `sidebarOpen = true` but the client renders `sidebarOpen = false` (because the viewport is different), React reports a hydration mismatch. Fix: always start with `sidebarOpen: true`:

```tsx
// After: deterministic for all environments
sidebarOpen: true,
```

**2. Date formatting uses local timezone.** The `FrontmatterPanel` component formatted modTime using the browser's locale:

```tsx
// Before: server and client may show different dates
v.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
```

If the server is in UTC and the client is in EST, a date like "2026-06-07" could render as "Jun 7" on one and "Jun 6" on the other. Fix: use UTC consistently:

```tsx
// After: deterministic across environments
v.toLocaleDateString("en-US", {
  year: "numeric", month: "short", day: "numeric",
  timeZone: "UTC",
});
```

The clock in `VaultLayout` was already fixed in a previous step with a `HydrationSafeClock` component.

Commit: `web: make layout clock hydration safe`

### Phase 6: Align SSR and client page titles

The client's `useEffect` in `App.tsx` was updated to skip pages that have their own title ownership, and each page component was given its own `useEffect`:

- `NotePage`: `document.title = note.title — siteTitle`
- `SearchPage`: `document.title = Search — siteTitle`
- `App.tsx` (router shell): only sets title for non-note, non-search pages

The SSR sidecar `server.mjs` was also updated to use the same title format.

Commit: `web: align SSR and client page titles`

## Live Testing: Bugs Found in Production

The build and test suite (`pnpm --dir web check`, `pnpm --dir web exec vitest run src/entry-server.test.tsx`, `pnpm --dir web build:all`, `GOWORK=off go test ./...`) all passed. But a live local test revealed two production-class failures that were invisible to the build:

### Bug 1: SSR sidecar returning 500

Started the local backend and SSR sidecar:

```bash
GOWORK=off go run ./cmd/retro-obsidian-publish serve \
  --vault ./vault-example \
  --vault-name TestVault \
  --page-title "Test Vault" \
  --port 18080 \
  --ssr-url http://127.0.0.1:18089 \
  --watch=false &

SSR_PORT=18089 API_BASE=http://127.0.0.1:18080 \
  BASE_URL=http://127.0.0.1:18080 \
  node web/server.mjs &
```

`curl -sI http://127.0.0.1:18080/` showed a 200 response, but the raw HTML contained `<div id="root"></div>` — an empty root, not SSR content. The Go server was silently falling back to the SPA.

Backend logs confirmed:

```
2026/06/07 08:46:07 SSR proxy unavailable, falling back to SPA
```

SSR sidecar logs revealed the actual error:

```
Invalid hook call. Hooks can only be called inside of the body of a function component.
TypeError: Cannot read properties of null (reading 'useContext')
    at useInRouterContext (...)
    at Router (...)
    at StaticRouter (...)
```

**Root cause**: Vite's SSR build had `noExternal` for `react`, `react-dom`, and a few libraries, but not for all React-using libraries. `react-router` and `react-resizable-panels` were left external. This meant:

- The SSR bundle contained a bundled copy of React
- The externalized packages used a separate React instance loaded from `node_modules`
- `StaticRouter` (from the externalized `react-router`) tried to call `useContext()` on React's internal context, but the React instance it saw was different from the one the app's components used
- React detected the mismatch and threw the "invalid hook call" error

**Fix**: Changed Vite config to `ssr.noExternal: true`, bundling all frontend dependencies:

```typescript
// vite.config.ts
ssr: {
  noExternal: true, // Bundle ALL deps for SSR sidecar
},
```

This ensures every React component library uses the same React singleton as the SSR renderer.

### Bug 2: Module script MIME type error

After fixing the SSR rendering, the browser loaded the page but showed:

```
Failed to load module script: Expected a JavaScript-or-Wasm module script but the server responded with a MIME type of "text/html"
@ http://127.0.0.1:18080/assets/index.js:0
```

The browser was trying to load `/assets/index.js` instead of the hashed Vite asset. The SSR sidecar's `server.mjs` had read `./dist/index.html` as a CWD-relative path, which resolved to the repo root's `dist/index.html` instead of the `web/dist/index.html`. When that file didn't exist, it used a fallback shell that referenced `/assets/index.js` instead of the correct hashed asset.

**Fix**: Resolve `dist/index.html` relative to `server.mjs` using `import.meta.url`:

```javascript
import { dirname, join } from "path";
import { fileURLToPath } from "url";
const WEB_DIR = dirname(fileURLToPath(import.meta.url));

function getIndexHtml() {
  return readFileSync(join(WEB_DIR, "dist", "index.html"), "utf-8");
}
```

This works both locally (started from repo root) and in Docker (started from `/app/web`).

### Live test results

After both fixes:

```
Page URL: http://127.0.0.1:18080/
Page Title: Test Vault
Console: 0 errors, 0 warnings
```

Direct navigation to `/note/philosophy/epistemology`:
```
Page URL: http://127.0.0.1:18080/note/philosophy/epistemology
Page Title: Epistemology — Test Vault
Console: 0 errors, 0 warnings
```

Sidebar navigation (client SPA): works correctly.

## Files Changed

| File | Change |
|------|--------|
| `web/package.json` | Added `react-router-dom`, `react-router`; removed `wouter` |
| `web/pnpm-lock.yaml` | Updated lockfile |
| `web/vite.config.ts` | `ssr.noExternal: true` (bundle all SSR deps) |
| `web/server.mjs` | CWD-relative `dist/index.html` fix; home-note prefetching |
| `web/src/App.tsx` | Wouter → React Router; exported `AppRoutes`; title ownership |
| `web/src/entry-client.tsx` | `createRoot` + clear → `hydrateRoot` (no clearing) |
| `web/src/entry-server.tsx` | Simplified `SSRNotePage` etc. → real `AppRoutes` under `StaticRouter` |
| `web/src/entry-server.test.tsx` | Updated tests for real-app SSR rendering |
| `web/src/components/pages/VaultLayout/VaultLayout.tsx` | Wouter → React Router navigation; `HydrationSafeClock` component |
| `web/src/components/pages/NotePage/NotePage.tsx` | Wouter → React Router navigation; note-title `useEffect` |
| `web/src/components/pages/SearchPage/SearchPage.tsx` | Wouter → React Router navigation; search-title `useEffect` |
| `web/src/pages/NotFound.tsx` | Wouter → React Router navigation |
| `web/src/store/uiSlice.ts` | Deterministic initial `sidebarOpen`/`rightPanelOpen` state |
| `web/src/components/molecules/FrontmatterPanel/FrontmatterPanel.tsx` | UTC date formatting for SSR/client determinism |
| `web/src/main.tsx` | Removed (stale entry point no longer referenced) |
| `web/patches/wouter@3.7.1.patch` | Removed (Wouter no longer used) |
| `web/patches/wouter@3.7.1.patch` | Removed (Wouter no longer used) |
| `web/patches/wouter@3.7.1.patch` | Removed (Wouter no longer used) |

## Key Learnings

### 1. Build success does not guarantee SSR correctness

The typecheck, unit tests, and build all passed. The SSR sidecar still returned 500s because duplicate React instances are a runtime issue, not a build issue. **Always test live** — start the backend and sidecar, load a page in a browser, check console for errors.

### 2. SSR fallback masks errors

The Go server's SSR proxy silently falls back to the SPA handler on any SSR 500. This means the page still loads (with SPA content) and the user might not notice a problem. But crawlers and agents see SPA HTML, not SSR HTML. The fallback behavior is convenient but hides bugs.

### 3. Vite SSR bundling requires discipline

When `ssr.noExternal` is not set for all React-dependent packages, Vite creates a fragment: some React code is in the bundle, some is loaded at runtime from `node_modules`. React hooks work fine when both caller and callee use the same instance, but break when they don't. The fix (`noExternal: true`) is safe but increases bundle size.

### 4. First-render determinism is non-negotiable

Any value that differs between server and client during the initial render — viewport size, `new Date()`, `Math.random()`, locale formatting — causes a hydration mismatch. These are often subtle because they only manifest in the first render; subsequent client-side updates are fine.

### 5. The "clear and remount" pattern is a deferred cost

Clearing `root.textContent` and calling `createRoot` instead of `hydrateRoot` avoids immediate hydration warnings, but it means:
- The SSR output is only a temporary preview
- The server-rendered title is lost
- The first render is always a flash (SSR HTML → blank → React renders)
- There is no semantic connection between server and client

Eventually the two trees need to converge, and the cost of doing so grows with the complexity of the app.

## Future Work

- **Extract shared home-route selection**: `server.mjs` duplicates `chooseHomeSlug()` from `App.tsx`. Extract this into a pure module used by both the SSR sidecar and the React app.
- **Add automated smoke test**: A script that starts the backend and SSR sidecar, loads pages, checks raw SSR root is populated, and asserts zero browser console errors.
- **Consider scoped `noExternal`**: Replace `noExternal: true` with a curated list of known React-dependent packages once bundle size becomes a concern.
- **Consider React Helmet or similar**: Currently `server.mjs` owns `<head>` injection. A React-side head manager could centralize this, though it adds complexity.

## Summary

The migration from divergent SSR/client rendering to a single hydratable React tree was completed in six focused phases. The key technical insight was that the SSR and client share the same component tree (`AppRoutes`); they only differ in their router wrapper (`StaticRouter` vs `BrowserRouter`). The migration was complicated by three real-world issues that only appeared during live testing: duplicate React instances due to Vite's SSR bundling, CWD-relative path resolution in the Express sidecar, and non-deterministic first-render values (viewport-dependent UI state, timezone-sensitive date formatting). All three were resolved, and the live test passes with zero console warnings or errors.

The result is a simpler architecture with less duplication, correct page titles on both server and client, and a foundation for future improvements (shared utilities, React-side head management, automated smoke tests).
