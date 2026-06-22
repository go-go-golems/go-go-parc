---
Title: Bridge Topic Reports Plan
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
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/bridges
      Note: 8 bridge topic reports being written by parallel subagents
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/bridges/01-sqlite-canonical-store.md
      Note: Bridge report 01
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/bridges/02-go-backed-js-dsls.md
      Note: Bridge report 02
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/bridges/03-browser-as-coprocessor.md
      Note: Bridge report 03
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/bridges/04-provider-profile-boundary.md
      Note: Bridge report 04
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/bridges/05-agent-readable-artifacts.md
      Note: Bridge report 05
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/bridges/06-evidence-workflows-repair.md
      Note: Bridge report 06
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/bridges/07-single-binary-go-spa.md
      Note: Bridge report 07
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/bridges/08-derived-rebuildable-artifacts.md
      Note: Bridge report 08
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/04-refined-topic-concept-maps-v2.md
      Note: Refined maps that revealed the 8 bridge topics
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/sources
      Note: 14 partition summaries providing evidence for bridge reports
ExternalSources: []
Summary: Plan for 8 bridge-topic reports spanning multiple topic slices, with mermaid graphs and per-agent instructions.
LastUpdated: 2026-06-22T23:30:00-04:00
WhatFor: Use this to understand which bridge topics were assigned and how each agent was briefed.
WhenToUse: Before reviewing bridge reports or launching additional bridge agents.
---










# Bridge Topic Reports Plan

## Goal

The 7 topic maps (design/04) revealed 8 recurring cross-cutting concepts that span multiple topics. Each bridge topic deserves its own textbook-style report because it is a first-class architectural pattern, not just a footnote in a single topic. This document assigns one subagent per bridge topic.

## Bridge topic overview

```mermaid
flowchart TD
    B1[Bridge 1: SQLite as Canonical Store\nT2 T5 T6 T7]
    B2[Bridge 2: Go-Backed JavaScript DSLs\nT1 T2 T5 T6 T7]
    B3[Bridge 3: Browser as Coprocessor\nT1 T3 T7]
    B4[Bridge 4: Provider/Profile Boundary\nT2 T4 T5 T6]
    B5[Bridge 5: Agent-Readable Artifacts and a14y\nT3 T5 T6 T7]
    B6[Bridge 6: Evidence-Preserving Workflows\nwith Human-in-the-Loop Repair\nT1 T3 T4 T6]
    B7[Bridge 7: Single-Binary Go + SPA\nT4 T5 T6 T7]
    B8[Bridge 8: Derived Rebuildable Artifacts\nT2 T3 T6 T7]

    B1 --> Output[bridges/ directory\n8 textbook-style reports]
    B2 --> Output
    B3 --> Output
    B4 --> Output
    B5 --> Output
    B6 --> Output
    B7 --> Output
    B8 --> Output
```

## Bridge topics and mermaid graphs

### Bridge 1: SQLite as Canonical Store and Product Boundary

**Spans**: T2 (Durable Objects), T5 (go-minitrace), T6 (RAG/OCR/Readwise/codebase browser), T7 (app shells)

**Output**: `bridges/01-sqlite-canonical-store.md`

```mermaid
flowchart TD
    SQLite[SQLite canonical store] --> Durable[Durable Objects\nper-actor SQLite storage]
    SQLite --> Minitrace[go-minitrace\nnormalized transcript DB\nmt.db 9-10 tables]
    SQLite --> RAG[RAG Evaluation\ncorpus DB + engine DB split]
    SQLite --> OCR[Book OCR\nwork queue + provenance]
    SQLite --> Codebase[Codebase Browser\nstatic SQLite + FTS5 + sql.js]
    SQLite --> Readwise[Readwise Viewer\ndocuments + tags + FTS5]
    SQLite --> CoRead[Document Co-Read\nDuckDB graph from transcripts]
    SQLite --> AppShells[App Shells\nGo-Go Parc / Retro Obsidian]

    Boundary[SQLite as product boundary] --> BrowserRuntime[sql.js in browser\nstatic artifact runtime]
    Boundary --> ScriptArtifact[SQLite as script/LLM artifact\nquery plans as frontend architecture]
    Boundary --> OperatorSurface[Glazed CLI over SQLite\nshared service layers]

    FM1[Chunking termination bug\noverlap loop unbounded]
    FM2[SQLite concurrency hazard\nparallel OCR workers need BEGIN IMMEDIATE]
    FM3[snapshot_refs view freeze\n60s browser freeze from broad view expansion]
    FM4[GOWORK=off in worktrees\nsilent empty DBs]
    FM5[Regex table extraction fragility\nfails on quoted identifiers]
```

**Key source reports to read**: `02b`, `05a`, `05b`, `06a`, `06b`, `07a`
**Key project articles**: RAG Evaluation System, Codebase Browser, Readwise Viewer, go-minitrace API Redesign, Durable Objects, SQLite Authorizer and Query Safety, SQLite Introspection

---

### Bridge 2: Go-Backed JavaScript DSLs

**Spans**: T1 (Loupedeck), T2 (go-go-goja/xgoja), T5 (Geppetto), T6 (goja-bleve), T7 (Widget IR/Fringe)

**Output**: `bridges/02-go-backed-js-dsls.md`

```mermaid
flowchart TD
    Rule[JavaScript owns composition\nGo owns invariants/state/lifecycle/typed values] --> Builders[Go-backed fluent builders\nhidden Go refs on JS wrappers]
    Builders --> Domains

    subgraph Domains["DSL Application Domains"]
        GojaBleve[goja-bleve\nrequire bleve for JS RAG]
        GeppettoWrap[Geppetto wrapper-first\nhidden-ref __geppetto_ref]
        WidgetIR[Widget IR DSL\nGoja authors data, React renders]
        LoupedeckJS[Loupedeck JS API\nGo serial driver + Goja runtime]
        CSSDiff[CSS Visual Diff JS API\nGo-backed workflow engine]
        GojaText[goja-text\nMarkdown AST bindings + template builders]
        ProtoBuilder[Protobuf fluent builders\nGoja native proto construction]
        AuthRoutes[Express auth route planner\nGo-backed fluent route plans]
    end

    Fluent[Fluent builder pattern] --> Validate[Go validates transitions\nrejects illegal combinations]
    WrapperFirst[Wrapper-first when\ncredentials/sessions/typed state matter] --> GeppettoWrap
    WrapperFirst --> AuthRoutes

    FM1[Plain-object domain state drift\nJS owns too much state]
    FM2[Hidden-ref lifecycle bugs\nreopened index, batch execution timing]
    FM3[Schema/buildspec/runtime drift\nlegacy v2-to-legacy metadata loss]
```

**Key source reports to read**: `01b`, `02a`, `02b`, `05a`, `06a`, `07a`
**Key project articles**: Designing DSLs with go-go-goja, Fluent Builders with Go-Backed Objects, goja-bleve, Geppetto JS Bindings, Building a Goja UI DSL, Loupedeck Goja API, CSS Visual Diff JS API, goja-text

---

### Bridge 3: Browser as Coprocessor for Constrained Runtimes

**Spans**: T1 (SToMS3R/Tab5/Almanach/Face Animation), T3 (Almanach raster), T7 (browser widget runtime)

**Output**: `bridges/03-browser-as-coprocessor.md`

```mermaid
flowchart LR
    Browser[Browser / host app] --> Encode[Encode pixels/commands\nCanvas resize, dithering,\nRGB565, ESC-POS, UF2]
    Encode --> Transport[Transport\nBLE / HTTP / USB serial / UART / SD]
    Transport --> Firmware[Thin firmware bridge]
    Firmware --> HAL[ESP-IDF / Pico SDK / DRM-KMS]
    HAL --> Device[Physical device\nDisplay, thermal head, e-ink, LEDs]
    Device --> Feedback[Observable feedback\nserial logs, visual output, benchmarks]
    Feedback --> Browser

    subgraph Examples["Concrete Instances"]
        SToMS3R[SToMS3R\nbrowser dithering → UART → K118]
        Tab5[Tab5\nbrowser Canvas → HTTP → MIPI DSI]
        Almanach[Almanach\nReact SPA in firmware + CLI render service]
        FaceAnim[Face Animation Studio\nbrowser sprite tool → ESP32 robot]
        WidgetRT[Browser-Side React Widget Runtime\nTSX compilation + import policy]
    end

    Invariant[Invariant: browser does compute-heavy work\nfirmware streams raw bytes/pixels] --> SToMS3R
    Invariant --> Tab5
    Invariant --> Almanach

    FM1[TCP read gaps cause horizontal stripes\nbetween UART writes]
    FM2[Partial frame writes expose half-updated display]
    FM3[LVGL 9 vs LVGL 8 image descriptor API mismatch]
    FM4[EMBED_TXTFILES corrupts multi-byte UTF-8]
```

**Key source reports to read**: `01a`, `03b`, `07a`, `07b`
**Key project articles**: SToMS3R, ESP32-P4 MIPI DSI Image Blitter, Almanach Studio, Almanach Render Service, Face Animation Studio, Browser-Side React Widget Runtime, Optimizing WiFi Image Upload on ESP32-P4

---

### Bridge 4: Provider/Profile Boundary

**Spans**: T2 (Geppetto), T4 (xgoja auth host), T5 (Pi providers/LLM proxy), T6 (embedding providers)

**Output**: `bridges/04-provider-profile-boundary.md`

```mermaid
flowchart TD
    Profile[Profile YAML\nprovider setup, credentials, sampling defaults] --> Resolution[Profile resolution\nmodel field resolves to profile, not provider model]
    Resolution --> Boundary[Provider/profile boundary\nJS cannot build provider/model settings directly]

    subgraph Instances["Concrete Instances"]
        Geppetto[Geppetto wrapper-first\nprofile-backed inference settings\nhidden-ref __geppetto_ref]
        LLMProxy[LLM proxy\nOpenAI-compatible surface\nresolves model as Geppetto profile slug]
        PiScoped[Pi scoped models\nenabledModels cycle\nprovider-qualified IDs]
        EmbedProfile[Embedding provider profile\nGeppetto/Pinocchio resolves\nprovider + model + dimensions]
        AuthHost[xgoja Keycloak auth host\nplanned routes → generated host auth]
        TokenFam[Token families + device auth flow\nOAuth/OIDC provider boundaries]
    end

    Compat[Provider compatibility contract\ncompat object consumed at request builder] --> LLMProxy
    Compat --> Geppetto

    ShortLived[Short-lived credentials\nOIDC tokens, Vault tokens, GitHub App tokens] --> AuthHost
    ShortLived --> TokenFam

    FM1[Provider replay bug\nduplicate Responses item IDs]
    FM2[Thinking-content dampening\nsystem prompt + tools reduce reasoning]
    FM3[Keycloak DCR scope mismatch\nfor Claude]
    FM3b[Provider replay bugs\ntimeline/adapters cannot replay states]
```

**Key source reports to read**: `02b`, `04a`, `05a`, `05b`, `06a`
**Key project articles**: Geppetto JS Bindings, Geppetto JS Overhaul, LLM Proxy, Pi Scoped Models, xgoja Keycloak Auth Host, go-go-goja Express Auth, go-go-goja Token Families, RAG Evaluation embedding profiles, Geppetto Gemini SDK Modernization

---

### Bridge 5: Agent-Readable Artifacts and a14y

**Spans**: T3 (Storybook), T5 (self-contained reports), T6 (Retro Obsidian), T7 (docsctl/SSR)

**Output**: `bridges/05-agent-readable-artifacts.md`

```mermaid
flowchart TD
    A14y[Agent readability =\nHTTP routing commitment\nbefore SPA fallback] --> ServerContract[Server routing contract\nMarkdown mirror before SPA shell]
    A14y --> StaticDiscovery[Structured discovery endpoints\nAGENTS.md, llms.txt, sitemap]

    subgraph Artifacts["Concrete Artifact Types"]
        HTMLReport[Self-contained HTML transcript report\ninlined JSON + CDN libs]
        MarkdownMirror[Markdown mirror\n.md suffix + Accept: text/markdown]
        SSRSidecar[SSR sidecar\nNode Express renderToString\n+ RTK Query preload]
        StorybookFix[Storybook contract surface\nfixtures for every node/widget kind]
        StaticSite[Static browser artifact\nruns from file://, no server]
    end

    subgraph Systems["Systems Producing Agent-Readable Output"]
        Minitrace[go-minitrace\nself-contained HTML reports]
        RetroObsidian[Retro Obsidian Publish\nMarkdown mirrors + Bleve + SSR]
        Docsctl[docsctl\nSSR sidecar for Go-hosted React]
        GoGoParc[Go-Go Parc Website\nvault → static + agent-readable]
        Storybook[Storybook\nvisual contract + fixture discovery]
        TranscriptReports[Transcript-driven design recovery\nagent-readable output from minitrace]
    end

    A14y --> Artifacts
    Artifacts --> Systems

    FM1[SPA-only shells weak for agents/search\nuntil SSR or Markdown mirrors added]
    FM2[Divergent SSR/SPA trees\nduplicate route/title/layout maintenance]
    FM2b[Protobuf unknown fields silently dropped\n.proto is the real API]
```

**Key source reports to read**: `03b`, `05a`, `05b`, `06b`, `07a`
**Key project articles**: Agent a14y for Go-Hosted React Docs, Retro Obsidian Publish, Self-Contained HTML Transcript Exports, Streaming Agent Dashboard, Storybook contracts, Building a Knowledge Base Playbook, docsctl and SSR Sidecar

---

### Bridge 6: Evidence-Preserving Workflows with Human-in-the-Loop Repair

**Spans**: T1 (hardware debugging), T3 (visual parity), T4 (postmortems), T6 (OCR repair)

**Output**: `bridges/06-evidence-workflows-repair.md`

```mermaid
flowchart TD
    Model[Model/expensive call] --> RawEvidence[Persisted raw evidence\nturns, screenshots, serial logs, metrics]
    RawEvidence --> Structured[Structured/typed representation\nJSON, CompareResult, page OCR JSON]
    Structured --> Rendered[Deterministic rendered artifact\nMarkdown, PDF, visual diff, print output]
    Rendered --> Review[Human review\nvisual inspection, manual PDF repair, postmortem]
    Review --> Repair[Targeted repair loop\nrerun selected pages, fix specific CSS, re-provision]
    Repair --> Structured

    subgraph Instances["Concrete Instances"]
        OCRRepair[Book OCR\ntarget-page-only structured JSON\n→ deterministic MD/PDF → manual repair]
        VisualParity[CSS Visual Diff\npixel + cascade diff\n→ parity repair loop]
        HWDebug[Hardware debugging\nserial probes + visual benchmarks\n→ transcript-mined root cause]
        Postmortem[Deployment postmortems\noutage evidence → root cause → fix]
        ThermalBanding[Thermal printer banding\nserial logs → root cause → firmware fix]
    end

    Invariant1[Evidence-preserving: never discard raw model/hardware output] --> RawEvidence
    Invariant2[Targeted repair: rerun only what failed, preserve dependencies] --> Repair
    Invariant3[Deterministic rendering: Go owns rendering from structured data] --> Rendered

    FM1[OCR hallucination / style drift\nduplicated paragraphs, list-page drift, caption bleed]
    FM2[Visual parity drift\nIR vs promoted vs Storybook vs original]
    FM3[Workflow dependency race\ntargeted rerun set downstream ops ready not pending]
```

**Key source reports to read**: `01a`, `03b`, `04a`, `04b`, `06a`
**Key project articles**: Book OCR Project Report, CSS Visual Diff, k3s Post-Reboot Outage, Thermal Receipt Printer Banding, Deep Research Thermal Printer, Transcript-Driven Design System Recovery, Structured Book OCR

---

### Bridge 7: Single-Binary Go + SPA Pattern

**Spans**: T4 (static sites), T5 (minitrace UI/dashboards), T6 (codebase browser/Readwise), T7 (Go-Go Parc/Retro Obsidian)

**Output**: `bridges/07-single-binary-go-spa.md`

```mermaid
flowchart TD
    Pattern[Single-binary Go + SPA\ngo:embed frontend] --> API[Go HTTP API + static frontend]
    Pattern --> ReuseCore[Go renderer/core reused\nacross CLI, HTTP, desktop shells]
    Pattern --> LocalFirst[Local-first: no external dependencies]

    subgraph Instances["Concrete Instances"]
        GoGoParc[Go-Go Parc Website\nvault loading + search + Mermaid + git-sync]
        RetroObsidian[Retro Obsidian Publish\nvault browser + Bleve + SSR + a14y]
        MinitraceUI[go-minitrace web UI\nsession browser + transcript reader + SQL workbench]
        CodebaseBrowser[Codebase Browser\nGo/AST → SQLite → static SPA]
        Readwise[Readwise Viewer\nSQLite + FTS5 + CLIM UI]
        StreamingDash[Streaming Agent Dashboard\nobserver → projector → WebSocket → React reducer]
        Docsctl[docsctl\nSSR sidecar + SPA fallback]
    end

    Enhancements[Re-runnable DOM augmentation\nsurvives fragment swaps] --> Pattern
    AtomicReload[Atomic reload\nvault + search swap under mutex] --> Pattern
    GitSync[git-sync sidecar\ncontent updates ≠ app deployments] --> Pattern

    Wails[Wails desktop shell\nbound methods + events + AssetServer] --> Pattern
    GoWasm[Go/Wasm browser tool\nGOOS=js GOARCH=wasm] --> Pattern

    FM1[SPA-only shells weak for agents/search]
    FM2[One-shot DOM augmentation breaks on live reload]
    FM3[fsnotify inode loss\nwatch lost on file recreation]
    FM4[Wails build tag failure\nplain go build fails without tags]
```

**Key source reports to read**: `04a`, `05a`, `05b`, `06b`, `07a`
**Key project articles**: Go-Go Parc Website, Retro Obsidian Publish, go-minitrace Web UI, Codebase Browser Static WASM, Readwise Viewer, Streaming Agent Dashboard, Wails v2 Desktop Applications, docsctl SSR Sidecar

---

### Bridge 8: Derived Rebuildable Artifacts

**Spans**: T2 (generated React), T3 (print layouts), T6 (search indexes), T7 (static sites/firmware assets)

**Output**: `bridges/08-derived-rebuildable-artifacts.md`

```mermaid
flowchart TD
    Canonical[Canonical source\nSQLite, YAML IR, Markdown, Go source] --> Generator[Generator/extractor\nAST, dithering, embedding, codegen]
    Generator --> Derived[Derived artifact\nrebuildable from canonical source]

    subgraph ArtifactTypes["Derived Artifact Types"]
        SearchIdx[Search indexes\nBleve BM25, FAISS vector, FTS5\nrebuildable from SQLite]
        GenReact[Generated React scaffolds\nDMETA IR → React components\npromoted to hand-owned]
        PrintLayout[Print layouts\nPretext measurement → pagination\n→ PDF typography]
        StaticSite[Static browser artifacts\nGo/AST → SQLite → static SPA\nruns from file://]
        FirmwareAssets[Firmware assets\nbrowser dithering → 1-bit bitmap\n→ ESC-POS bytes]
        HelpDocs[Generated help docs\nxgoja provider-shipped Glazed help]
        TSDecls[TypeScript declarations\n.d.ts from generated binaries]
    end

    Canonical --> SearchIdx
    Canonical --> GenReact
    Canonical --> PrintLayout
    Canonical --> StaticSite
    Canonical --> FirmwareAssets
    Canonical --> HelpDocs
    Canonical --> TSDecls

    RebuildRule[Rebuild rule: derived artifact is disposable\ncanonical source is the source of truth] --> Derived
    Promote[Promotion: generated scaffold → hand-owned\nwith provenance and manifest] --> GenReact

    FM1[FAISS build fragility\nmissing headers, incomplete CGO_LDFLAGS]
    FM2[Visual parity drift\nIR vs promoted vs Storybook vs original]
    FM3[Pretext heights diverge from CSS\nwhen used for absolute positioning]
    FM4[Generated artifact stale\nsource changed but artifact not rebuilt]
    FM5[TypeScript declarations not matching\nselected runtime profile]
```

**Key source reports to read**: `02a`, `02b`, `03a`, `03b`, `06a`, `06b`, `07a`
**Key project articles**: DMETA Design System Factory, Pretext Print Layout, Goja Bleve, Building FAISS for Bleve, Codebase Browser Static WASM, xgoja Provider-Shipped Help, TypeScript Declarations, SQLite Introspection (32MB→1.4MB), DMETA Visual Parity

---

## Agent instructions template

Each bridge agent receives:

1. **Skill**: Read `/home/manuel/.pi/agent/skills/textbook-authoring/SKILL.md` and follow its tone, structure, and patterns.
2. **Context**: Read the relevant source reports from `sources/` (listed per bridge) and the refined maps in `design/04`.
3. **Primary sources**: Read the assigned project articles from `Projects/2026/...` directly (not just the source report summaries).
4. **Output**: Write a textbook-style report to the assigned `bridges/NN-*.md` file.
5. **Constraint**: Only write within the ticket workspace (`ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/`). Do not modify `Projects/2026/` or any other source files. Do not launch subagents.
6. **Style**: Peter Norvig style — foundational prose, concrete examples, pseudocode, diagrams, structured learning materials. Define the concept, explain why it exists, show concrete instances across multiple topics, extract invariants, document failure modes, and provide a learning path.
