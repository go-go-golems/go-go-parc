# Code Context

## Files Retrieved

Scope: recent project Markdown corpus under `Projects/2026/{03,04,05,06}/`, with emphasis on end-user web/app/media/productivity surfaces not primarily owned by hardware, infra, data/RAG, typography, or JS-runtime slices.

Search method:
- Counted Markdown corpus with `find Projects/2026/{03,04,05,06} -type f -name '*.md'`.
- Title/path filtered with web/app keywords: `react|browser|chat|wails|md-view|screencast|audio|video|podcast|extension|web|static|spa|ui|admin|dashboard|overlay|productivity|app|frontend|site|voice|media|chrome|firefox|automation`.
- Read or heading-scanned high-signal files and retained line references for claims below.

Retrieved / inspected evidence:
1. `Projects/2026/04/10/PROJ - Screencast Studio - Architecture and Runtime Deep Dive.md` (lines 22-78, 95-142) - local screencast app: DSL, web control server, ffmpeg preview/recording, telemetry, subprocess lifecycle.
2. `Projects/2026/04/02/PROJ - SQLide Browser - Go Wasm SQL IDE.md` (lines 20-66, 76-117) - browser SQL IDE using Go/Wasm, sqlite-wasm, OPFS, Vite, dark IDE shell.
3. `Projects/2026/04/30/PROJ - Browser-Side React Widget Runtime - In-Browser TSX Compilation and Reload.md` (lines 25-75, 99-153, 177) - browser-side TSX/React live widget runtime, CodeMirror editor, Go harness, import/security policy.
4. `Projects/2026/05/16/PROJECT REPORT - Fringe Admin DSL Backend Driven Admin Interfaces Deep Dive.md` (lines 37-86, 163-217, 285-365, 486-620, 665-674) - backend-driven admin DSL, renderer-as-interpreter, Goja execution, Storybook contracts, protobuf transport.
5. `Projects/2026/05/29/ARTICLE - Chatbot Overlay Framework - TypeScript and Frontend Tool Calling Deep Dive.md` (lines 26-101, 145-190, 279-333, 375-482, 682-756) - reusable chat overlay, WebSocket hydration, typed frontend tools, human approval cards.
6. `Projects/2026/06/13/ARTICLE - Replacing md-view with a Wails v2 Desktop Application - Technical Deep Dive.md` (lines 25-51, 77-97, 122-140, 184-212) - replacement of browser/daemon markdown viewer with Wails desktop app and reusable fragment renderer.
7. `Projects/2026/06/18/PROJECT REPORT - Fake CMS 11ty Frontend - GraphQL to Static Site Deep Dive.md` (lines 41-54, 111-127, 218-248, 377-432, 482-499) - GraphQL-to-Eleventy static site frontend with typed block rendering and executable schema constraints.
8. `Projects/2026/05/07/ARTICLE - md-view - Building a Daemon-Based Markdown Viewer in Go.md` (lines 24-53, 72-132, 151-201, 248) - daemon/browser productivity tool pattern: CLI starts server, browser receives rendered Markdown and SSE reloads.
9. `Projects/2026/05/28/PROJ - md-view - Markdown Viewer Daemon.md` (lines 20-53, 71-142) - productized md-view status: daemon, Chroma, Mermaid, themes, localStorage, copy buttons, i3/Sway titles.
10. `Projects/2026/06/01/ARTICLE - Generic ChatProvider - From Overlay Runtime to Provider Backed Web Chat.md` (lines 27-60, 109-133, 166-257) - headless React ChatProvider separating chat mechanics from product rendering.
11. `Projects/2026/06/02/ARTICLE - CoinVault Web Chat - Event Projection Debug Exports and Thinking Persistence.md` (lines 22-40, 69-128, 245-315, 437-466) - application web chat event projection, debug SQLite exports, timeline merge/failure rules.
12. `Projects/2026/04/25/Building Chrome Extensions for DOM Overlay Selection and Component Extraction.md` (lines 1-38, 73-156, 177-303) - browser extension overlay selection, DOM geometry, computed CSS capture, html2canvas, extension popup messaging.
13. `Projects/2026/04/13/PROJ - Jingle Extractor - AI Audio Pipeline with MiniMax Demucs WhisperX.md` (lines 21-85) - audio generation/extraction pipeline with MiniMax, Demucs, WhisperX, librosa, pydub.
14. `Projects/2026/04/11/PROJ - Rabbit Hole Podcast Intros - Remotion Video Generation.md` (lines 20-117) - podcast/video intro generation via Remotion compositions and audio processing.
15. `Projects/2026/05/14/PROJECT REPORT - Go-Go Parc Website - Implementation Deployment and Git-Sync Runtime.md` (lines 42-108, 181-231, 256-309, 379-445) - Go-hosted SPA/static knowledge site with vault loading, search, Mermaid, copy buttons, Git sync.
16. `Projects/2026/06/06/PROJ - Retro Obsidian Publish - A Retro Monochrome Vault Browser.md` (lines 24-74) - single-binary Go+SPA vault browser with REST API, Bleve, SSR sidecar, agent-readable Markdown mirrors.

## Key Code

This is a report over project reports, not source code. Critical implementation concepts repeatedly appearing across the corpus:

### Browser app shells and local-first product surfaces

- `SQLide Browser` is a self-contained browser IDE: Vite shell, Go/Wasm bridge, sqlite-wasm worker, OPFS persistence, editor/schema/results/log panels (`Projects/2026/04/02/...SQLide...md`, lines 49-56, 108-115).
- `md-view` starts as a CLI-managed daemon serving rendered Markdown over HTTP/SSE, then evolves toward Wails desktop shells. The durable core is Markdown rendering (`RenderBody`) plus re-runnable frontend augmentation for Mermaid/copy buttons (`Projects/2026/06/13/...Replacing md-view...md`, lines 122-140, 184-212).
- Go-Go Parc and Retro Obsidian Publish are Go-hosted knowledge-site shells: Markdown vault loading, wiki links/backlinks, search, client enhancements, SPA fallback, GitOps reload, SSR/a11y/a14y endpoints (`Projects/2026/05/14/...Go-Go Parc Website...md`, lines 256-277; `Projects/2026/06/06/...Retro Obsidian Publish...md`, lines 49-68).

### Backend-driven UI / widget IR / admin DSL

- Fringe Admin DSL centers on `pages, nodes, surfaces, and actions`; browser receives page data, renderer interprets explicit node kinds, action ids are opaque, and page versions scope actions (`Projects/2026/05/16/...Fringe Admin DSL...md`, lines 86-217, 605-616).
- Browser-side React Widget Runtime treats source as data until browser import/compilation; combines TSX, CodeMirror, esbuild-wasm, import allowlists, strict host APIs, and planned iframe isolation (`Projects/2026/04/30/...Browser-Side React Widget Runtime...md`, lines 59-73, 153-177).
- WidgetRenderer standalone / Goja-authored React-rendered UI and June Widget IR/RAG DSL reports likely form the same subcluster, but were only title-scanned in this pass.

### Chat overlays and web chat runtimes

- Chatbot Overlay Framework provides typed widget streaming and frontend tool calls: backend asks for `cart.add` or `checkout.confirm`, frontend executes automatic tools or renders human approval cards, then resumes backend runs (`Projects/2026/05/29/...Chatbot Overlay Framework...md`, lines 36-51, 190-279, 482-559).
- Generic ChatProvider factors out headless React runtime concerns: Redux store, WebSocket subscription, session persistence, tool/widget/timeline registries, frontend tool manifests/results, while apps keep product rendering and CSS (`Projects/2026/06/01/...Generic ChatProvider...md`, lines 109-133).
- CoinVault Web Chat documents event projection and failure modes: absent vs empty content, stable entity ids, created vs updated ordinals, debug exports kept app-owned (`Projects/2026/06/02/...CoinVault Web Chat...md`, lines 437-446).

### Media pipelines

- Screencast Studio: DSL -> normalized config -> compiled plan -> managed ffmpeg/preview/telemetry processes, exposed by CLI plus `serve` frontend/API (`Projects/2026/04/10/...Screencast Studio...md`, lines 26-69, 95-142).
- Jingle Extractor: MiniMax generation, Demucs separation, WhisperX alignment, librosa beat scoring, pydub clips; limitations include CPU slowness and no batch mode (`Projects/2026/04/13/...Jingle Extractor...md`, lines 49-85).
- Rabbit Hole Podcast Intros: Remotion compositions, generated audio, visual effects and timing around podcast/social-video intro assets (`Projects/2026/04/11/...Rabbit Hole Podcast Intros...md`, lines 60-117).

### Browser automation/extensions

- Chrome Extension overlay/component extraction work focuses on Manifest V3, content script lifecycle, fixed-position overlays, `getBoundingClientRect()` traps, computed CSS filtering, `chrome.storage.local`, html2canvas, and popup/content-script messaging (`Projects/2026/04/25/Building Chrome Extensions...md`, lines 24-38, 73-156, 232-303).
- Related title-scanned surfaces: `Hover Component Inspector`, `TypoScope Firefox Typography Measurement Extension`, `Firefox Tab Tracker`, `surf-go Browser Verbs`, `surf-cli`, `DOM Scraping Experiment`, `Claude Agent SDK - Teaching an AI to Write Web Scrapers`.

## Architecture

### Cluster 1: Local-first Go-hosted browser/desktop apps

Projects:
- SQLide Browser (`04/02`) - browser IDE shell, Go/Wasm + sqlite-wasm.
- md-view daemon (`05/07`, `05/28`) - CLI/server/browser Markdown viewer.
- Wails replacement (`06/13`) - desktop shell retaining renderer core.
- Go-Go Parc Website (`05/14`) and Retro Obsidian Publish (`06/06`, `06/07`) - static/SPA vault browsers.
- DMETA Viewer (`05/19`) and RAG dashboards (`05/28`, `06/02`, `06/07`) likely adjacent.

Recurring concepts:
- Single binary serving API + static frontend.
- Go renderer/core reused across CLI, HTTP, and desktop shells.
- Browser enhancements must be re-runnable after fragment swaps/live reloads.
- SQLite/Bleve/OPFS as local browser/store/search substrate.

Failure modes:
- SPA-only shells are weak for agents/search until SSR or Markdown mirrors are added.
- Live reload and fragment replacement break one-shot DOM enhancement scripts.
- Browser persistence and worker headers (COOP/COEP, OPFS fallbacks) create deployment friction.

### Cluster 2: Backend-driven / generated UI systems

Projects:
- Fringe Admin DSL (`05/13`, `05/15`, `05/16`, `05/18`).
- Browser-side React Widget Runtime (`04/30`).
- Widget IR / WidgetRenderer standalone (`06/04`, `06/05`, `06/06`, `06/07`).
- DMETA React/design-system/CLIM work (`05/20`, `05/23`, `05/24`, `05/25`, `05/26`, `05/27`, `06/01`).

Recurring concepts:
- UI as data: page/node/action/widget IR transported from backend or Goja scripts.
- Renderer as interpreter, not arbitrary executable code.
- Narrow host modules and opaque action IDs.
- Storybook/test fixtures as contract surfaces for every node/widget kind.

Failure modes:
- Security boundary unfinished for untrusted widgets.
- Auth/role guards often explicitly postponed for admin surfaces.
- Widget/schema growth must not outrun renderer coverage and visual fixtures.

### Cluster 3: Chat overlay, web chat, and frontend tool execution

Projects:
- Chat Overlay API proposals (`05/29`).
- Chatbot Overlay Framework (`05/29`).
- Generic ChatProvider / Pinocchio web chat cleanup (`06/01`).
- CoinVault Web Chat (`06/02`) and earlier CoinVault RAG chat (`03/17`, `05/04`, `05/13`).
- Canonical Chat Event Protocol (`05/08`, `05/09`).

Recurring concepts:
- Protocol-first WebSocket event stream + HTTP commands.
- Frontend tool registry/manifest/result flow.
- Timeline entities, stream patches, reducers, stable ordinals.
- Headless provider package separated from product UI.

Failure modes:
- Empty string vs absent field bugs in protobuf/JSON projection.
- Entity ID instability between patch and terminal events.
- Debug export ownership boundaries between generic provider and application.

### Cluster 4: Media creation, capture, and review workflows

Projects:
- Screencast Studio (`04/10`, `04/13`, `04/15`).
- Jingle Extractor (`04/13`).
- Rabbit Hole Podcast Intros (`04/11`).
- Latent Space Podcast Downloader (`05/02`) and video lecture/Jellyfin workflow (`05/07`) likely adjacent.

Recurring concepts:
- Declarative plan/config over raw ffmpeg/audio commands.
- Local CLI-first orchestration with optional web control/review surface.
- Generated artifacts need preview, trimming, telemetry, and export policies.

Failure modes:
- Subprocess cancellation/shutdown and output overwrite semantics.
- CPU/GPU performance variance in AI audio/video tooling.
- Batch/retry/resume behavior underdeveloped.

### Cluster 5: Browser automation, overlays, and measurement extensions

Projects:
- Chrome DOM overlay/component extraction (`04/25`, `04/26`).
- Hover Component Inspector (`04/28`).
- TypoScope Firefox extension (`05/18`).
- Firefox Tab Tracker (`04/11`).
- surf-go/surf-cli/browser verbs/transcript extraction (`04/10`, `04/11`, `04/17`).

Recurring concepts:
- Content scripts and overlays as inspection/selection lenses.
- DOM geometry and computed style capture.
- Native messaging / external CLI integration for browser state.
- Browser automation as a reliability layer around JS probes, not blind scraping.

Failure modes:
- Coordinate-system traps (`getBoundingClientRect`, scrolling, fixed positioning).
- Extension bundling/module constraints and cross-context messaging complexity.
- Browser auth/login false positives and fragile selector assumptions.

## Candidate concept-map nodes and edges

Nodes:
- `Local-first web app shell`
- `Single-binary Go + SPA`
- `Go/Wasm browser tool`
- `Wails desktop shell`
- `Markdown rendering core`
- `Re-runnable DOM augmentation`
- `Static/vault browser`
- `Agent-readable web mirror`
- `Backend-driven UI DSL`
- `Widget IR`
- `Renderer-as-interpreter`
- `Opaque action id`
- `Storybook contract surface`
- `Frontend tool registry`
- `Headless ChatProvider`
- `Sessionstream/WebSocket timeline`
- `Stable event/entity ordinals`
- `Media plan compiler`
- `ffmpeg subprocess supervisor`
- `AI audio pipeline`
- `Browser overlay lens`
- `DOM geometry capture`

Edges:
- `Single-binary Go + SPA` -> serves -> `Local-first web app shell`
- `Markdown rendering core` -> reused by -> `md-view daemon` and `Wails desktop shell`
- `Static/vault browser` -> needs -> `Agent-readable web mirror`
- `Backend-driven UI DSL` -> compiles/transports -> `Widget IR`
- `Widget IR` -> interpreted by -> `Renderer-as-interpreter`
- `Renderer-as-interpreter` -> validated by -> `Storybook contract surface`
- `Chat overlay` -> factors into -> `Headless ChatProvider`
- `Headless ChatProvider` -> owns -> `Sessionstream/WebSocket timeline`
- `Frontend tool registry` -> publishes -> `tool manifest` -> consumed by -> `backend run loop`
- `Sessionstream timeline` -> vulnerable to -> `stable id / absent-vs-empty failure modes`
- `Media plan compiler` -> supervises -> `ffmpeg subprocess supervisor`
- `Browser overlay lens` -> measures -> `DOM geometry capture` -> feeds -> `component extraction / visual diff / typography measurement`

## Overlaps with other topic slices

- Agent 2 JS runtimes/xgoja: Goja-authored UI DSLs, WidgetRenderer, xgoja TypeScript/hot reload, Goja site rendering.
- Agent 3 typography/layout/design systems: DMETA React, CLIM, constraint/canvas layout, visual diff sites, TypoScope, hover inspector.
- Agent 4 infra/auth/deployment: Go-Go Parc/Retro Obsidian static deployment, GitOps reload, Argo CD, Vault/OIDC, Wails packaging maybe release tooling.
- Agent 5 AI agents/transcripts/observability: ChatProvider, sessionstream, Pi dashboard/extensions, chat overlays, transcript extraction.
- Agent 6 data/RAG/search: Codebase Browser, RAG evaluation UI, Retro Obsidian search, SQLide/db-browser, CoinVault RAG web chat.
- Agent 1 hardware: Cardputer web serial/Bluetooth demos, ESP32 browser-to-display pipeline, Loupedeck HTTP/API/frontend and face animation studio.

## Open questions

1. Should concept maps treat `DMETA / Widget IR / Admin DSL` as one umbrella node or separate parallel UI-IR traditions?
2. Should `ChatProvider` and `Sessionstream` live under AI-agent infrastructure, web app surfaces, or both with explicit cross-links?
3. Which browser automation reports are product surfaces vs research tooling? The boundary between extension, scraper, and design-system measurement is blurry.
4. Does `Wails/md-view` deserve its own app-shell lifecycle map: daemon browser -> Wails v2 -> Wails v3 bridge?
5. For media workflows, should the map emphasize user-facing review/control surfaces or the pipeline engines (ffmpeg/Demucs/Remotion/WhisperX)?
6. Several title-scanned candidates need deeper second pass: `Face Animation Studio`, `Collage Editor`, `PDF Page Reordering`, `Providence Therapist Search`, `ATProto Client`, `Racket Web Editor`, `Codebase Browser`, `RAG Evaluation frontend`.

## Recommended report-format lessons

- A cluster-first report works better than a flat list; this slice spans many small end-user surfaces that share architecture patterns more than repository names.
- Include a compact `retrieved evidence` section with exact line ranges first, then use cluster summaries for synthesis.
- Mark title-scanned but not deeply read files separately in future reports; otherwise reviewers may assume equal evidentiary confidence.
- Concept-map nodes/edges are most useful when phrased as reusable architectural concepts (`renderer-as-interpreter`, `headless provider`, `re-runnable augmentation`) rather than project names only.
- For future batches, add confidence labels: `read`, `heading-scanned`, `title-only`.

## Start Here

Start with `Projects/2026/05/29/ARTICLE - Chatbot Overlay Framework - TypeScript and Frontend Tool Calling Deep Dive.md` for the web-chat/app-shell part of this slice, and `Projects/2026/05/16/PROJECT REPORT - Fringe Admin DSL Backend Driven Admin Interfaces Deep Dive.md` for the backend-driven UI/Widget IR axis. Together they expose the core recurring pattern: protocol/data-driven UI plus narrow frontend/backend execution boundaries.
