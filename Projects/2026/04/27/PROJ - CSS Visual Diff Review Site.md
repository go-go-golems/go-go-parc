---
title: "CSS Visual Diff Review Site"
aliases:
  - CSS Visual Diff Review Site
  - Visual Review Site
  - css-visual-diff review
tags:
  - project
  - css-visual-diff
  - react
  - go
  - visual-regression
  - glazed
  - embed
  - dagger
status: active
type: project
created: 2026-04-27
repo: /home/manuel/code/wesen/corporate-headquarters/css-visual-diff
---
[]()
# CSS Visual Diff Review Site

This project adds an interactive visual review site to `css-visual-diff`, a Go command-line tool that compares rendered HTML and CSS across browser targets. The review site is a React single-page application, embedded into the Go binary at compile time, and served through a new `css-visual-diff serve` command. A reviewer opens a single URL, sees every comparison as an interactive card with screenshots and metadata, annotates what they see, and exports their feedback as a structured markdown document ready for an issue, a pull request, or an LLM prompt.

> [!summary]
> The project has three important identities:
> 1. **A replacement for a Python-generated static HTML page** that previously showed comparison results as a flat grid of images and textareas — notes disappeared on reload, there was no zoom, no annotation, and no export.
> 2. **A template for embedding React SPAs into Go CLIs**, demonstrating the Dagger build pipeline, `go:embed` integration, and the `net/http.ServeMux` serving pattern.
> 3. **A bridge between automated measurement and human judgment**, keeping pixel percentages, CSS diffs, and selector metadata close to the reviewer's own status decisions and notes.

## Why this project exists

Visual regression tools are good at measurement. They take screenshots, compute pixel differences, extract CSS property deltas, and classify sections by severity. But measurement is only half the job. The other half is judgment — someone has to look at the screenshots, decide whether each difference is acceptable, write notes about what to fix or accept, and pass those notes to a developer or a coding agent.

The previous workflow produced a folder of PNGs and JSON files, then ran a Python script that generated a single `index.html` with basic image grids and textareas. It worked, but it had critical limitations. Notes disappeared on reload because the textareas had no persistence. There were no interactive comparison modes — no overlay, no slider, no synchronized pan. There was no way to annotate a specific location on a screenshot. And there was no structured export beyond manual copy-paste from a textarea.

The review site solves all of these problems while embedding the entire experience into the `css-visual-diff` binary. No Node.js runtime is needed at serve time. No separate Python step is required. The reviewer runs one command, opens one URL, and gets a fully interactive review environment.

## Current project status

The project is complete and functional. It has been tested end-to-end with real Pyxis public-page comparison data (13 cards, real screenshots, real compare.json metadata).

What exists:

- A React SPA with 14 components, Redux Toolkit state management, and Tailwind CSS
- Four interactive view modes: side-by-side, overlay, slider, and diff-only
- Zoom and pan for pixel-level inspection
- Comment pins with four types (issue, note, question, praise)
- Review status tracking with localStorage persistence
- A markdown + YAML export modal for LLM handoff
- Keyboard shortcuts for fast review
- A Go `serve` subcommand with three API endpoints
- A Dagger-based build pipeline with local pnpm fallback
- A Glazed help entry accessible via `css-visual-diff help review-site`
- Complete docmgr ticket (CSSVD-REVIEW-SITE) with design doc and diary

What is not yet built:

- Synchronized pan between prototype and React images
- Touch gesture support for tablets
- Pixel color under cursor
- Run comparison feature (start new visual-diff runs from the browser)
- Server-side persistence (SQLite or otherwise)

## Project shape

The project spans three layers that work together: a React frontend, a Go HTTP server, and a build pipeline that connects them.

```text
┌─────────────────────────────────────────────────────────────┐
│ Go Binary (css-visual-diff)                                  │
│                                                              │
│  ┌──────────────────┐    ┌────────────────────────────┐     │
│  │ css-visual-diff   │    │ css-visual-diff serve        │     │
│  │ run / compare     │    │                              │     │
│  │ (existing cmds)   │    │ 1. Serves embedded SPA        │     │
│  │                    │    │    from go:embed FS            │     │
│  │ Produces:         │    │                              │     │
│  │ - summary.json    │    │ 2. Serves artifact files       │     │
│  │ - compare.json    │    │    from --data-dir              │     │
│  │ - *.png files     │    │                              │     │
│  └──────┬───────────┘    │ 3. Provides API endpoints      │     │
│         │                 │    /api/manifest                │     │
│         ▼                 │    /api/compare                 │     │
│  ┌──────────────────┐    │    /artifacts/{path}             │     │
│  │ /tmp/run-dir/     │    └──────────────┬─────────────────┘     │
│  │  summary.json     │◄───────────────────┘                      │
│  │  page/artifacts/  │   --data-dir points here                  │
│  │    section/       │                                          │
│  │      compare.json │                                          │
│  │      diff_only.png│                                          │
│  │      left_region  │                                          │
│  │      right_region │                                          │
│  └──────────────────┘                                          │
└─────────────────────────────────────────────────────────────┘

         Network boundary (localhost)

┌─────────────────────────────────────────────────────────────┐
│ Browser (React SPA)                                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Vite-built React app                                  │   │
│  │                                                        │   │
│  │ ┌─────────┐  ┌─────────┐  ┌───────────────────────┐ │   │
│  │ │ RTK      │  │ React   │  │ localStorage           │ │   │
│  │ │ Store    │  │ Views   │  │ sync middleware        │ │   │
│  │ │          │  │         │  │                        │ │   │
│  │ │ - cards  │  │ - header│  │ On status/note change: │ │   │
│  │ │ - filter │  │ - canvas│  │ write to localStorage  │ │   │
│  │ │ - view   │  │ - side  │  │ keyed by run+page+sect │ │   │
│  │ │ - comment│  │ - export│  │                        │ │   │
│  │ └─────────┘  └─────────┘  └───────────────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

The key design decision is that the review site does not replace `css-visual-diff`'s measurement capabilities. It consumes the artifacts that measurement produces — screenshots, metadata, and summary manifests — and presents them for human judgment. This separation is deliberate. The review site is a viewer, not a runner.

## Architecture

### File layout

The project's code is organized into three main areas within the `css-visual-diff` repository:

```text
css-visual-diff/
├── cmd/
│   ├── build-web/main.go          ← Dagger build pipeline
│   └── css-visual-diff/
│       ├── main.go                ← CLI entry point (serve registered here)
│       └── serve.go               ← serve subcommand + HTTP routing
├── internal/cssvisualdiff/
│   ├── review/
│   │   ├── embed.go               ← //go:embed embed/public (build tag: embed)
│   │   ├── embed_none.go          ← disk fallback (no embed tag)
│   │   ├── static.go              ← SPA handler with fallback to index.html
│   │   ├── generate.go            ← //go:generate go run ../../../cmd/build-web
│   │   └── embed/public/          ← built SPA assets land here
│   │       └── .keep
│   └── ...
├── web/review-site/               ← React SPA source
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.tsx               ← React entry point
│   │   ├── App.tsx                ← Root layout + keyboard shortcuts
│   │   ├── types/                 ← TypeScript types
│   │   ├── store/                 ← RTK slices + middleware
│   │   ├── components/            ← 14 React components
│   │   └── utils/                 ← path rewriting, export, storage
│   └── index.html
├── Makefile                       ← build-web, build-embed, dev-web targets
└── internal/cssvisualdiff/doc/
    └── tutorials/review-site.md   ← Glazed help entry
```

### The data that feeds the review site

Understanding the data flow is essential. Everything the React app displays comes from files that `css-visual-diff` writes to disk during a comparison run.

- [x] A comparison run produces a nested artifact directory. Each section contains four PNG files and one JSON file. The names follow a convention that the review site relies on:

- `diff_only.png` — only the pixels that differ, highlighted in red or magenta. This is the first image a reviewer should inspect because it answers the question "where are the differences?" without the distraction of the full screenshots.
- `left_region.png` — the cropped screenshot of the prototype element. It answers "what did the reference look like?"
- `right_region.png` — the cropped screenshot of the React element. It answers "what did our implementation render?"
- `diff_comparison.png` — a side-by-side triptych (left, diff, right). Useful for broad context but too wide for first-pass review.
- `compare.json` — the structured evidence: selectors, bounds, pixel counts, computed CSS differences, changed attributes, and source URLs.

The summary JSON is the entry point. It lives at the root of the data directory (or at an explicit path specified by `--summary`) and contains one row per page/section combination. Each row includes the page name, section name, computed classification, changed percentage, and absolute paths to every artifact file.

### How the Go server maps URLs to files

The serve command's artifact handler performs a simple but important transformation. The React app requests files using relative URLs like `/artifacts/shows/content/diff_only.png`. On disk, the actual file lives at `<data-dir>/shows/artifacts/content/diff_only.png`. The Go handler splits the three-part URL path and inserts the `artifacts/` subdirectory between the page name and the section name:

```text
URL:    /artifacts/shows/content/diff_only.png
                 ─────  ───────  ─────────────
                 page   section  file

Disk:   <data-dir>/shows/artifacts/content/diff_only.png
                      ─────  ─────────  ───────  ─────────────
                      page   artifacts   section  file
```

This mapping is a convention established by `css-visual-diff`'s run output. The review site relies on it. If a future version of `css-visual-diff` changes the directory structure, the serve handler would need to be updated to match.

## Implementation details

### The React SPA

The React app is organized around four Redux Toolkit slices that manage distinct aspects of the review state.

**The cards slice** owns the loaded comparison data. When the app mounts, it dispatches `fetchManifest`, an async thunk that fetches `/api/manifest` and normalizes the summary JSON into an array of `SummaryRow` objects. Each row's absolute artifact paths are rewritten into relative `/artifacts/` URLs by the `toArtifactUrl` utility function. The slice also manages filter state (classification, status, search text) and the selected card index.

**The view slice** tracks the current view mode, sidebar tab, comment mode, and overlay parameters (opacity, blend mode, slider position). These are pure UI state that does not need persistence.

**The review slice** manages the human reviewer's decisions: status (unreviewed, accepted, needs-work, fixed, wont-fix) and free-form notes. Each card's review state is keyed by `page/section`.

**The comments slice** manages annotation pins. Each pin records its position as percentage coordinates (x% and y% of the image area), its side (left, right, or merged), its type (issue, note, question, praise), and its text content.

The localStorage sync middleware intercepts every action that modifies the review or comments slices and writes the combined state to `localStorage` under a key like `cssvd-review-run-<hash>`. This ensures feedback survives page reloads without any server-side storage.

### Component hierarchy

The component tree reflects the user's mental model: a header with controls, a list of expandable cards, a sidebar for metadata, and a modal for export.

```text
<Provider store={store}>
  <App>                           ← global keyboard shortcuts, manifest loading
    <Header>                      ← view mode buttons, comment toggle, export button
    <main>
      <CardList>                  ← renders filtered cards
        <ReviewCard> × N          ← expand/collapse, status dropdown, notes
          <ZoomPan>               ← scroll zoom, shift+drag pan
            <ViewModeSideBySide>  ← or Overlay / Slider / Diff
          <CommentPin> × M        ← annotation markers on images
      <Sidebar>                   ← sticky right panel
        <CommentsTab>             ← pin list with inline editing
        <StylesTab>               ← CSS property diff table
        <MetaTab>                 ← bounds, pixels, selectors, URLs
    </main>
    <ExportModal>                 ← markdown + YAML preview and copy
  </App>
</Provider>
```

Each component has a single responsibility. `ReviewCard` owns the per-card layout and review controls. `ZoomPan` handles scroll-to-zoom and drag-to-pan for any view mode content. `ExportModal` generates the full markdown document and copies it to the clipboard. The component boundaries are chosen so that each one could be tested independently with mock data.

### View modes in depth

The four view modes are the main interactive feature of the review site. Each provides a different way to compare the prototype and React screenshots, optimized for a different stage of the review process.

**Side-by-side** shows both images next to each other in a flex row. Each image has a label strip identifying it as "prototype" or "react" with the source selector. This is the default mode and the best starting point for understanding what changed at a glance.

**Overlay** stacks both images. The reviewer drags an opacity slider between A (prototype only) and B (React only). A "diff blend" toggle switches to CSS difference blend mode, which makes even subtle color shifts visible as bright spots. The reviewer holds the F key to flash between the two images instantly — this is the fastest way to spot subtle alignment or color differences. The original implementation used the spacebar for flashing, but that conflicted with page scrolling, so it was changed to F.

**Slider** uses CSS `clip-path` to show the prototype on the left of a draggable divider and React on the right. The reviewer drags the circular handle to sweep across the image. The implementation tracks mouse position during drag and updates the clip-path percentage.

**Diff-only** shows only `diff_only.png`, which highlights the changed pixels without the distraction of the full screenshots. This is the recommended first inspection target — look at where the differences are, then switch to side-by-side or overlay to understand them.

### Zoom and pan

The `ZoomPan` component wraps all view mode content and provides three interactions.

Scroll the mouse wheel to zoom in and out, from 0.25x to 8x. The zoom tracks toward the cursor position using the formula `newOffset = mouse - scale × (mouse - oldOffset)`, where `scale = newZoom / oldZoom`. This means the point under the cursor stays fixed as you zoom in, which feels natural.

Hold Shift and drag with the left mouse button (or drag with the middle button) to pan. Double-click to reset zoom and pan to the defaults. A small indicator in the bottom-left corner shows the current zoom percentage and pixel offset (`Δx, Δy`), which is useful for measuring distances between features in the screenshots.

The component uses CSS `transform: translate(...) scale(...)` for smooth rendering and disables the CSS transition during active drag to avoid lag.

### Keyboard shortcuts

The review site supports keyboard shortcuts for fast navigation without touching the mouse. They are disabled when the cursor is inside a textarea, input field, or dropdown.

| Key | Action |
| --- | --- |
| `j` | Move to the next card |
| `k` | Move to the previous card |
| `a` | Mark current card as accepted |
| `n` | Mark current card as needs work |
| `w` | Mark current card as won't fix |
| `x` | Mark current card as fixed |
| `1` | Switch to side-by-side view |
| `2` | Switch to overlay view |
| `3` | Switch to slider view |
| `4` | Switch to diff-only view |
| `e` | Open the export modal |
| `p` | Enter comment pin mode |
| `F` (hold) | Flash between prototype and React in overlay mode |

The shortcuts are registered in a global `keydown` listener in `App.tsx`. The handler checks the event target's tag name and skips processing for text inputs.

### The export modal

The export modal is the bridge between the review site and the developer or coding agent who will act on the feedback. It generates a markdown document with YAML metadata for each card, combining the computed evidence (classification, changed percentage, CSS diffs) with the human feedback (status, notes, pin comments).

The reviewer can choose to export all cards or only reviewed ones (those with a non-default status or a note). The "Copy markdown" button writes the full text to the clipboard. The generated output includes enough context for an LLM to understand what changed and what the reviewer wants done.

### Classification versus status

One of the most important design decisions in the review site is the separation of classification and status.

Classification is computed by `css-visual-diff` from the pixel-change percentage using policy bands defined in the visual spec YAML. If a section shows 7% changed pixels, it falls into the "review" band (between 0.5% and 10%). If it shows 12%, it falls into "tune-required" (between 10% and 30%). Classification answers: "how different is this section, mechanically?"

Status is decided by the human reviewer. A section classified as "tune-required" might still be accepted by the reviewer if the visual difference is intentional or acceptable. This happened in the real Pyxis project — the Shows page was numerically above 10% but visually acceptable. The review site records both values independently. The number starts the conversation; it does not end it.

## The build pipeline

The build pipeline transforms the React source code into static files that are embedded into the Go binary at compile time. It has two modes: Dagger (recommended for CI) and local pnpm (recommended for development).

### Dagger build

The `cmd/build-web` tool uses Dagger to build the frontend inside a `node:22` container. It creates a pnpm CacheVolume so that repeated builds reuse downloaded packages. After the first build, subsequent builds are fast because the package store is persisted.

```text
┌─────────────────────────────────┐
│ 1. Dagger connects to engine     │
│    spins up node:22 container    │
│    mounts web/review-site/       │
│    as /src                        │
├─────────────────────────────────┤
│ 2. Container runs:               │
│    corepack enable                │
│    corepack prepare pnpm@10.15.0  │
│    pnpm install --prefer-offline  │
│    pnpm run build                 │
├─────────────────────────────────┤
│ 3. Export /src/dist/ to temp dir  │
│    copy to internal/.../embed/    │
│    /public/                       │
└─────────────────────────────────┘
```

### Local fallback

If Docker is unavailable or `BUILD_WEB_LOCAL=1` is set, the build tool falls back to running `pnpm run build` on the local machine. This is useful for development or environments without Docker.

### The embed layer

The Go embed layer uses build tags to switch between embedded and on-disk assets:

- `embed.go` (build tag `embed`) uses `//go:embed embed/public` to embed the built SPA into the binary.
- `embed_none.go` (build tag `!embed`) walks up from the working directory to find the repo root and serves assets from disk.

This means `go run ./cmd/css-visual-diff serve ...` works without the embed tag during development, while `go build -tags embed` produces a self-contained binary for distribution.

### Development workflow

During frontend development, run the Vite dev server and the Go server separately. Vite runs on port 5173 with hot module replacement, and proxies `/api` and `/artifacts` requests to the Go server on port 8097. Edit React components and see changes instantly without recompiling Go.

```bash
# Terminal 1: Go server
go run ./cmd/css-visual-diff serve --data-dir /tmp/my-run --port 8097

# Terminal 2: Vite dev server
cd web/review-site && pnpm dev
```

## Important project docs

| Document | Location | Purpose |
| --- | --- | --- |
| Design guide | `ttmp/.../design/01-design-...md` | 22-section implementation guide (2404 lines) |
| Diary | `ttmp/.../reference/01-diary.md` | 4 steps of implementation narrative |
| Glazed help | `internal/.../doc/tutorials/review-site.md` | User-facing help entry |
| Pyxis reference | `ttmp/.../sources/local/05-public-pages-...md` | Original static HTML analysis |
| Mock JSX | `ttmp/.../sources/local/diff-review.jsx` | Original React mock UI |

## Open questions

- Should the review site support comparing two runs side by side (showing whether a section improved or regressed between commits)?
- Should localStorage be replaced or supplemented with server-side persistence (SQLite)?
- Should the serve command auto-detect summary JSON in common locations rather than requiring `--data-dir`?
- Could the review site start comparison runs by calling `css-visual-diff` as a child process?

## Near-term next steps

- Add synchronized pan between prototype and React images in side-by-side mode
- Add touch gesture support for zoom/pan on tablets
- Show pixel color under cursor
- Add a ruler or measurement tool for measuring distances in pixels
- Test the Dagger pipeline on CI (currently only tested locally)

## Project working rule

The review site is a viewer, not a runner. It consumes artifacts that `css-visual-diff` produces. It does not capture screenshots, run browser automation, or compute diffs. Every feature added to the review site should make human judgment faster or more durable — not replicate measurement capabilities that already exist in the CLI.
