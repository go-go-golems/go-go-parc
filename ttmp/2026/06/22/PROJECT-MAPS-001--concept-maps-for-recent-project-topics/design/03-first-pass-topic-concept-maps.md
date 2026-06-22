---
Title: First Pass Topic Concept Maps
Ticket: PROJECT-MAPS-001
Status: active
Topics:
    - research
    - projects
    - concept-maps
DocType: design
Intent: long-term
Owners: []
RelatedFiles:
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/01-initial-scan-and-subagent-fanout-plan.md
      Note: Original topic slices and fanout plan
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/02-first-batch-source-report-guidelines.md
      Note: Reporting contract that shaped the map synthesis
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/sources
      Note: Seven first-batch source reports used as concept-map inputs
ExternalSources: []
Summary: First-pass Mermaid concept maps synthesized from the seven source reports.
LastUpdated: 2026-06-22T21:45:00-04:00
WhatFor: Use this as the first visual synthesis of recent project-topic constellations.
WhenToUse: After reading the first-batch source reports and before deeper map refinement.
---


# First Pass Topic Concept Maps

## Scope

These are first-pass Mermaid maps synthesized from the seven source reports in `sources/`. They are intentionally conceptual rather than exhaustive. The goal is to expose recurring topic spines, not to list every project file.

Source reports:

- `sources/01-hardware-embedded-esp32.md`
- `sources/02-javascript-goja-xgoja-dsls.md`
- `sources/03-typography-layout-design-systems.md`
- `sources/04-infra-auth-deployment-gitops.md`
- `sources/05-ai-agents-transcripts-observability.md`
- `sources/06-data-rag-ocr-search.md`
- `sources/07-web-ui-apps-media-productivity.md`

## Cross-topic integration map

```mermaid
flowchart TD
    Corpus[Recent Projects Corpus\nProjects/2026 Mar-Jun] --> Runtime[Go-backed JavaScript runtimes\ngo-go-goja / xgoja / jsverbs]
    Corpus --> Data[Local data and search systems\nSQLite / RAG / OCR / Bleve]
    Corpus --> Devices[Physical devices and firmware\nESP32 / e-ink / printers / Loupedeck]
    Corpus --> Design[Typography and design systems\nPretext / DMETA / CSS visual diff]
    Corpus --> Infra[Hosted substrate\nK3s / Vault / Keycloak / GitOps]
    Corpus --> Agents[Agent observability\nPi / go-minitrace / Sessionstream]
    Corpus --> Apps[User-facing app shells\nReact / Wails / chat overlays / media]

    Runtime --> Apps
    Runtime --> Agents
    Runtime --> Data
    Runtime --> Infra
    Data --> Apps
    Data --> Agents
    Design --> Apps
    Design --> Data
    Devices --> Apps
    Devices --> Design
    Infra --> Apps
    Infra --> Agents

    FM[Failure-mode-driven design] --> Runtime
    FM --> Data
    FM --> Devices
    FM --> Infra
    FM --> Agents
    FM --> Design

    Artifact[Agent-readable / portable artifacts] --> Agents
    Artifact --> Data
    Artifact --> Design
    Artifact --> Apps
```

## Hardware / embedded / ESP32 map

```mermaid
flowchart TD
    HW[Physical-device projects] --> ESP[ESP-IDF / M5Stack firmware]
    HW --> Ink[E-ink and slow-display systems]
    HW --> Print[Thermal printing]
    HW --> Deck[Loupedeck physical UI]
    HW --> Pico[PicoCalc / RP2040-RP2350]

    ESP --> PaperS3[PaperS3]
    ESP --> Atom[AtomS3R / ATOM Lite]
    ESP --> Tab5[M5Stack Tab5 / ESP32-P4]
    ESP --> Chan[M5StackChan / CoreS3]
    ESP --> Dial[M5Dial]

    Host[Browser / CLI / designer] --> Raster[Canvas resize / dithering / RGB565 / command encoding]
    Raster --> Transport[BLE / HTTP / USB serial / UART / SD]
    Transport --> FW[Firmware or driver]
    FW --> HAL[ESP-IDF / Pico SDK / DRM-KMS / Go serial]
    HAL --> Device[Display / e-ink panel / thermal head / LEDs / pen sensor]
    Device --> Obs[Serial logs / visual output / printed output / benchmarks]
    Obs --> Host

    Atom --> Provision[BLE WiFi provisioning]
    Provision --> NVS[NVS credentials]
    Atom --> Print
    Print --> ESC[ESC/POS / UART pacing]
    Print --> Banding[Failure: banding / underfeed / power limits]

    Tab5 --> MIPI[MIPI DSI / LVGL 9]
    Chan --> Dirty[Dirty rectangles / SPI chunking]
    Deck --> Coalesce[Region coalescing / backpressure-safe writer]
    Ink --> DRM[Paper Pro DRM/KMS / evdev pen]
    Pico --> UF2[UF2 loader / fixed-offset bootloader split]

    Dirty --> FM1[Failure: tearing / slow full redraw]
    Coalesce --> FM2[Failure: transport storms]
    DRM --> FM3[Failure: no framebuffer / hidden Qt path]
    UF2 --> FM4[Failure: boot format mismatch]
```

## JavaScript / Goja / xgoja / DSL map

```mermaid
flowchart TD
    GoHost[Go host owns resources\ninvariants lifecycle credentials] --> Kernel[go-go-goja runtime kernel]
    Kernel --> Modules[CommonJS module registry\nGo-backed providers]
    Modules --> RuntimeProfile[xgoja runtime profiles]
    RuntimeProfile --> RuntimePlan[RuntimePlan v2\nSourceRegistry / source graph]
    RuntimePlan --> JS[JS/TS authored composition]
    JS --> Surfaces[Glazed commands / HTTP routes / agents / UI DSLs]

    JSVerbs[jsverbs scanner] --> Binding[Shared binding plan]
    Binding --> Glazed[Glazed/Cobra command surface]
    Binding --> Exec[Goja execution]

    Xgoja[xgoja buildspec] --> Providers[Compile-time provider packages]
    Providers --> Binary[Generated Go binary]
    Binary --> Profiles[Per-command capability boundary]
    Profiles --> Modules

    TS[TypeScript support] --> DTS[Generated .d.ts descriptors]
    TS --> Esbuild[esbuild compile layer]
    Esbuild --> JSVerbs
    Esbuild --> Exec

    DSL[Go-backed fluent DSLs] --> Builders[Go-owned builders / wrappers]
    Builders --> Invariants[Validation and typed final values]
    Invariants --> Surfaces

    Durable[Go Go Objects] --> Actor[Identity-bound actor runtime]
    Actor --> Storage[SQLite object storage]
    Actor --> HTTP[HTTP RPC/fetch gateway]

    Geppetto[Geppetto wrapper-first bindings] --> Profiles2[Profile-backed inference settings]
    Profiles2 --> AgentAPI[Agent / turn / tool wrappers]

    FM[Failure modes] --> Drift[Schema/buildspec/runtime drift]
    FM --> Sharing[Unsafe runtime sharing]
    FM --> PlainObj[Plain-object domain state drift]
    FM --> ScopeBug[Source scoping bugs]
```

## Typography / layout / design systems map

```mermaid
flowchart TD
    Type[Typography and design-system projects] --> Pretext[Pretext text measurement]
    Type --> DMETA[DMETA semantic design-system compiler]
    Type --> Visual[Visual parity and CSS diff]
    Type --> Fonts[Font tooling and typography debugging]

    Pretext --> Prepare[prepare: segment and measure]
    Prepare --> Layout[layout: fast arithmetic reflow]
    Layout --> Pagination[Swiss print pagination]
    Layout --> Canvas[Canvas constraint layout]
    Layout --> Reflow[Interactive text reflow]
    Layout --> Posters[Orthogonal poster fitting]

    Canvas --> Cassowary[Cassowary solve-measure loop]
    Cassowary --> FM1[Failure: nonlinear text height vs linear constraints]
    Pagination --> FM2[Failure: Pretext heights diverge from CSS absolute layout]

    DMETA --> Semantic[Semantic archetypes / capabilities / actions]
    Semantic --> IR[Widget / presentation IR]
    IR --> Generated[Generated React scaffold]
    Generated --> Promoted[Promoted hand-owned React components]
    Promoted --> Storybook[Storybook contracts]
    Promoted --> Governance[CSS governance\nnarrowest durable owner]

    Visual --> Baseline[Prototype / imported original baseline]
    Baseline --> Diff[css-visual-diff]
    Diff --> Pixel[Pixel diff]
    Diff --> CSS[Computed CSS and cascade winner diff]
    Diff --> Repair[Visual parity repair loop]
    Repair --> Promoted

    Fonts --> Debug[Computed-style sampling / CSS variables]
    Fonts --> Raster[TTF / glyph outline / rasterizer investigations]
```

## Infra / auth / deployment / GitOps map

```mermaid
flowchart TD
    Infra[Hosted platform evolution] --> Coolify[Coolify on Hetzner\nhistorical fast hosting]
    Infra --> K3s[Hetzner K3s GitOps platform\ncurrent substrate]
    Infra --> Vault[Vault secret plane]
    Infra --> Keycloak[Keycloak identity plane]
    Infra --> CI[CI/CD and publishing]
    Infra --> Ops[Operations / backup / outages]

    Coolify --> K3s
    Terraform[Terraform] --> VM[Hetzner VM / DNS / firewall]
    VM --> CloudInit[cloud-init bootstrap]
    CloudInit --> K3s
    K3s --> Argo[Argo CD desired state]
    Argo --> Apps[Hosted apps / static sites / protocol services]

    Keycloak --> HumanOIDC[Human OIDC]
    HumanOIDC --> Vault
    Keycloak --> Apps
    Vault --> K8sAuth[Kubernetes auth / VSO]
    K8sAuth --> Secrets[Kubernetes workload secrets]
    Vault --> GHA[GitHub Actions OIDC]
    GHA --> GitOpsPR[Short-lived GitOps PR credentials]
    GitOpsPR --> Argo

    DNS[DigitalOcean DNS / delegation] --> Cert[cert-manager ACME DNS-01]
    Cert --> TLS[TLS secrets]
    TLS --> Traefik[Traefik ingress]
    Traefik --> Apps

    CI --> GHCR[Images / packages / schemas]
    CI --> Trusted[Trusted npm publishing]
    CI --> Release[Release trains / ggg]

    Ops --> Restic[Restic / TrueNAS backup]
    Ops --> Postmortems[Outage postmortems]
    Postmortems --> FM[Failure modes: state drift / reboot outage / token scope / flat Argo taxonomy]
```

## AI agents / transcripts / observability map

```mermaid
flowchart TD
    Agents[Agent systems and observability] --> Retrospective[Retrospective transcript analysis]
    Agents --> Live[Live streaming observability]
    Agents --> Pi[Pi core and extensions]
    Agents --> Providers[Provider/tool-calling behavior]
    Agents --> Readability[Agent-readable artifacts]

    Retrospective --> Native[Native agent session JSONL]
    Native --> Convert[go-minitrace convert]
    Convert --> Archive[Canonical minitrace archive]
    Archive --> DB[Normalized SQLite / DuckDB]
    DB --> Query[JS query repository]
    Query --> HTML[Self-contained HTML reports]
    Query --> Metrics[Tool-call frequency / transitions / retries / churn]

    Live --> Provider[Geppetto provider engine]
    Provider --> ProviderObs[Provider observability records]
    ProviderObs --> Sessionstream[Sessionstream hub]
    Sessionstream --> Transport[WebSocket transport records]
    Transport --> Browser[Browser parser / Redux timeline]
    Browser --> Pinocchio[Pinocchio recorder / debug API / SQLite export]

    Pi --> Registry[Pi shared extension registry]
    Registry --> Tools[LLM-callable tools]
    Registry --> Widgets[Dashboards / TUI widgets / command palette]
    Registry --> Docs[Docs / settings / actions]
    Tools --> External[External CLIs: surf / md-view / pinocchio]

    Providers --> LLMProxy[LLM proxy / ChatProvider adapters]
    Providers --> Failures[Provider replay / thinking truncation / missing stream IDs]
    Failures --> Retrospective
    Failures --> Live

    Readability --> Static[Static HTML / Markdown mirrors / a14y]
    Static --> Agents
```

## Data / RAG / OCR / search map

```mermaid
flowchart TD
    Data[Data, RAG, OCR, search systems] --> Canon[SQLite canonical store]
    Data --> RAG[RAG Evaluation System]
    Data --> OCR[Book OCR workflow]
    Data --> Search[Search indexes]
    Data --> Browsers[Local corpus browsers]
    Data --> Graph[Document co-read graph]

    RAG --> Source[Source]
    Source --> Document[Document]
    Document --> Chunk[Chunk]
    Chunk --> Embedding[Embedding]
    Embedding --> Retrieval[Search / retrieval]
    Retrieval --> Eval[Evaluation]

    Canon --> Chunk
    Canon --> Embedding
    Canon --> WorkflowDB[Workflow engine DB\nseparate orchestration state]
    WorkflowDB --> RAG

    Search --> BM25[Bleve BM25]
    Search --> Vector[Vector retrieval]
    Vector --> FAISS[FAISS / CGO vector build]
    BM25 --> Hybrid[Hybrid RRF]
    Vector --> Hybrid
    Canon --> Derived[Derived disposable indexes]
    Derived --> BM25
    Derived --> FAISS

    OCR --> PageImages[Page images]
    PageImages --> VLM[VLM OCR model calls]
    VLM --> RawTurn[Persisted raw turns]
    RawTurn --> JSON[Structured target-page JSON]
    JSON --> Render[Deterministic Markdown/PDF]
    Render --> Review[Manual review / targeted repair]

    Browsers --> Codebase[Codebase Browser]
    Browsers --> Readwise[Readwise Viewer]
    Browsers --> Obsidian[Retro Obsidian Publish]
    Browsers --> Corpus[Corpus Explorer]

    Graph --> Transcripts[Transcript read events]
    Transcripts --> CoRead[Co-read weighted edges]
    CoRead --> Recommend[Recommendation dashboard]

    FM[Failure modes] --> ChunkBug[Chunk loop / idempotency bugs]
    FM --> Sparse[Sparse embedding coverage]
    FM --> Concurrent[SQLite concurrency hazards]
    FM --> Native[FAISS native build fragility]
    FM --> OCRDrift[OCR hallucination / style drift]
```

## Web UI / apps / media / productivity map

```mermaid
flowchart TD
    Apps[Web UI, apps, media, productivity] --> Local[Local-first app shells]
    Apps --> UIIR[Backend-driven UI / Widget IR]
    Apps --> Chat[Chat overlays and web chat]
    Apps --> Media[Media creation pipelines]
    Apps --> Browser[Browser automation and overlays]

    Local --> Single[Single-binary Go + SPA]
    Local --> Wasm[Go/Wasm browser tools]
    Local --> Daemon[CLI daemon + browser UI]
    Local --> Wails[Wails desktop shell]
    Local --> Knowledge[Static/vault browser]
    Knowledge --> AgentMirror[Agent-readable mirrors]

    UIIR --> Page[Page/node/action DSL]
    Page --> Renderer[Renderer as interpreter]
    Renderer --> Storybook[Storybook contract surface]
    UIIR --> Widget[Widget IR]
    Widget --> HostAPI[Narrow host APIs / opaque action IDs]

    Chat --> ChatProvider[Headless ChatProvider]
    ChatProvider --> Timeline[Sessionstream/WebSocket timeline]
    Timeline --> Stable[Stable entity IDs / ordinals]
    ChatProvider --> Tools[Frontend tool registry]
    Tools --> Approval[Human approval cards]

    Media --> Plan[Declarative media plan]
    Plan --> FFmpeg[ffmpeg subprocess supervisor]
    Media --> Audio[AI audio pipeline\nMiniMax / Demucs / WhisperX]
    Media --> Remotion[Remotion video compositions]

    Browser --> Lens[DOM overlay lens]
    Lens --> Geometry[getBoundingClientRect / computed styles]
    Geometry --> Extraction[Component extraction / visual diff / typography measurement]

    FM[Failure modes] --> SPA[SPA shell poor for agents/search]
    FM --> Reload[One-shot DOM augmentation breaks on live reload]
    FM --> Schema[Widget/schema growth outruns renderer fixtures]
    FM --> Event[Absent-vs-empty and entity-id projection bugs]
    FM --> Extension[Extension cross-context messaging complexity]
```

## Reusable bridge concepts

These nodes should probably appear in the final cross-topic map because they recur in multiple slices:

- **SQLite canonical store**: data/RAG/OCR, go-minitrace, durable objects, Readwise, codebase browser.
- **Go-backed JavaScript DSL**: goja/xgoja, CSS visual diff, UI DSLs, RAG scripting, Loupedeck/device APIs.
- **Single-binary Go + SPA**: data browsers, documentation sites, app shells, dashboards.
- **Derived artifact / rebuildable index**: search indexes, generated UI scaffolds, static sites, firmware assets, printed layouts.
- **Provider/profile boundary**: Geppetto, xgoja, Pi providers, embedding providers, hosted auth.
- **Failure mode as design driver**: every slice uses concrete failures to discover architecture boundaries.
- **Agent-readable artifact**: self-contained transcript reports, SSR/Markdown mirrors, project reports, source maps, Storybook/visual diffs.
- **Human-in-the-loop repair loop**: OCR review, visual parity repair, hardware visual debugging, deployment postmortems, provider replay debugging.

## Refinement notes

- These maps should be treated as draft topology. Node names and edge labels should be normalized once the evidence ledgers are formalized.
- Several high-overlap topics need bridge maps of their own: `go-go-goja + agents`, `RAG + UI`, `design systems + web apps`, `hardware + browser coprocessor`, and `infra + hosted runtime auth`.
- Later maps should mark current/historical status more clearly, especially for Coolify vs K3s and early xgoja RuntimePlan formats.
