---
Title: Refined Topic Concept Maps v2
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
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/02-first-batch-source-report-guidelines.md
      Note: Reporting contract followed by all partition scouts
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/03-first-pass-topic-concept-maps.md
      Note: v1 first-pass maps superseded by v2
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/sources
      Note: 14 second-batch partition summaries that feed these refined maps
ExternalSources: []
Summary: Refined concept maps merged from 14 second-batch partition summaries with cross-topic bridges.
LastUpdated: 2026-06-22T23:00:00-04:00
WhatFor: Use this as the primary concept-map deliverable, replacing the first-pass maps in design/03.
WhenToUse: After the second batch of 14 partition scouts; before any third-pass refinement.
---


# Refined Topic Concept Maps v2

## Sources

These maps merge 14 second-batch partition summaries (2 per topic × 7 topics) with evidence-backed typed nodes, labeled edges, and explicit cross-topic bridges. Each partition is in `sources/NNx-*.md`.

| Topic | Partition A | Partition B |
|---|---|---|
| 1 Hardware/embedded/ESP32 | `01a-hardware-esp32-firmware-devices.md` | `01b-hardware-remarkable-loupedeck-pico.md` |
| 2 JavaScript/Goja/xgoja/DSLs | `02a-js-runtime-xgoja-typescript.md` | `02b-js-dsls-geppetto-durable-auth.md` |
| 3 Typography/layout/design | `03a-typography-pretext-canvas.md` | `03b-typography-dmeta-visualdiff-fonts.md` |
| 4 Infra/auth/GitOps | `04a-infra-hosting-secrets-deployment.md` | `04b-infra-dns-tls-backup-publishing.md` |
| 5 AI agents/observability | `05a-agents-transcripts-sessionstream.md` | `05b-agents-pi-providers-dashboards.md` |
| 6 Data/RAG/OCR/search | `06a-data-rag-vectors-ocr.md` | `06b-data-browsers-readwise-knowledge.md` |
| 7 Web UI/apps/media | `07a-webui-localshells-backendui.md` | `07b-webui-chat-media-browserext.md` |

---

## Cross-Topic Integration Map

```mermaid
flowchart TD
    subgraph Runtimes["Topic 2: JS Runtimes"]
        GoHost[Go host owns invariants\nresources lifecycle credentials]
        Kernel[go-go-goja runtime kernel]
        XgojaPlan[xgoja RuntimePlan v2\nSourceRegistry]
        GojaDSL[Go-backed fluent DSL]
        Durable[Durable Objects actor runtime]
    end

    subgraph Data["Topic 6: Data/RAG/Search"]
        SQLite[SQLite canonical store]
        RAG[RAG Evaluation System]
        OCR[Book OCR workflow]
        Bleve[Derived search index\nBleve/FAISS]
        Browser[Local corpus browsers]
    end

    subgraph Devices["Topic 1: Hardware/Embedded"]
        ESPIDF[ESP-IDF firmware]
        BrowserCoproc[Browser as coprocessor]
        Display[Display pipeline\ndirty rects / region coalescing]
        Thermal[Thermal printing\nESC/POS dithering]
        Ink[E-ink / DRM/KMS / pen]
    end

    subgraph Design["Topic 3: Typography/Design"]
        Pretext[Pretext measurement\nprepare/layout split]
        DMETA[DMETA design-system compiler]
        VisualDiff[CSS visual diff\nvisual parity loop]
        Storybook[Storybook contract surface]
    end

    subgraph Infra["Topic 4: Infra/GitOps"]
        K3s[Hetzner K3s GitOps platform]
        Vault[Vault secret plane]
        Keycloak[Keycloak identity plane]
        GitOps[Argo CD desired state]
        ReleaseTrains[Release trains / ggg]
    end

    subgraph Agents["Topic 5: Agents/Observability"]
        Minitrace[go-minitrace\ntranscript analysis]
        Sessionstream[Sessionstream hub\nlive observability]
        PiExt[Pi extensions registry]
        LLMProxy[LLM proxy / ChatProvider]
        A14y[Agent-readable artifacts]
    end

    subgraph WebUI["Topic 7: Web UI/Apps"]
        AppShell[Single-binary Go+SPA\napp shell]
        BackendUI[Backend-driven UI\nrenderer-as-interpreter]
        ChatOverlay[Chat overlay\nheadless ChatProvider]
        MediaPlan[Media plan compiler\nffmpeg/GStreamer]
        BrowserLens[Browser overlay lens\nDOM geometry capture]
    end

    %% Cross-topic bridges
    GoHost --> Kernel --> XgojaPlan --> GojaDSL
    GojaDSL --> BackendUI
    GojaDSL --> RAG
    GojaDSL --> ChatOverlay
    Durable --> SQLite
    XgojaPlan --> Minitrace

    SQLite --> RAG
    SQLite --> OCR
    SQLite --> Browser
    SQLite --> Durable
    RAG --> Bleve
    OCR --> AppShell

    BrowserCoproc --> Thermal
    BrowserCoproc --> Display
    BrowserCoproc --> AppShell
    Display --> Design
    Thermal --> MediaPlan

    Pretext --> Design
    DMETA --> BackendUI
    DMETA --> Storybook
    VisualDiff --> BrowserLens
    VisualDiff --> Storybook

    K3s --> GitOps
    Vault --> Keycloak
    Keycloak --> ChatOverlay
    Vault --> ReleaseTrains
    GitOps --> AppShell
    GitOps --> Browser

    Minitrace --> A14y
    Sessionstream --> ChatOverlay
    Sessionstream --> LLMProxy
    PiExt --> A14y
    LLMProxy --> ChatOverlay
    A14y --> AppShell

    ChatOverlay --> Sessionstream
    BackendUI --> AppShell
    BrowserLens --> VisualDiff
    MediaPlan --> AppShell

    %% Failure-mode hub
    FM[Failure-mode-driven design] -.-> Runtimes
    FM -.-> Data
    FM -.-> Devices
    FM -.-> Design
    FM -.-> Infra
    FM -.-> Agents
    FM -.-> WebUI
```

### Reusable bridge concepts (appear in 3+ topics)

| Bridge concept | Topics | Evidence |
|---|---|---|
| **SQLite canonical store** | 2, 5, 6, 7 | Durable object storage, minitrace normalized DB, RAG corpus, codebase browser, Readwise |
| **Go-backed JavaScript DSL** | 2, 5, 6, 7 | goja-bleve, Geppetto wrappers, Widget IR, Loupedeck, CSS visual diff |
| **Single-binary Go + SPA** | 5, 6, 7, 4 | Go-Go Parc, Retro Obsidian, minitrace UI, docsctl, dashboard |
| **Derived rebuildable artifact** | 2, 3, 6, 7 | Search indexes, generated React scaffolds, static sites, firmware assets, print layouts |
| **Provider/profile boundary** | 2, 4, 5, 6 | Geppetto profiles, xgoja auth host, Pi providers, embedding providers |
| **Failure mode as design driver** | all | Every topic uses concrete failures to discover architecture boundaries |
| **Agent-readable artifact** | 5, 6, 7, 3 | Self-contained transcript reports, SSR/Markdown mirrors, Storybook, a14y |
| **Human-in-the-loop repair loop** | 1, 3, 4, 6 | OCR review, visual parity repair, hardware visual debugging, deployment postmortems |
| **Browser as coprocessor** | 1, 7, 3 | SToMS3R, Tab5, Almanach, Face Animation Studio, browser-side widget runtime |

---

## Topic 1: Hardware / Embedded / ESP32

**Merged from**: `01a` (ESP32 firmware: PaperS3, AtomS3R, Tab5, M5StackChan) + `01b` (PicoCalc, reMarkable, Loupedeck, other devices)

```mermaid
flowchart TD
    subgraph ESP32Firmware["ESP-IDF Firmware"]
        PaperS3[PaperS3\ne-paper + touch + WAMR]
        AtomS3R[AtomS3R / ATOM Lite\nBLE provisioning + thermal printer]
        Tab5[Tab5 / ESP32-P4\nESP-Hosted WiFi + MIPI DSI]
        M5StackChan[M5StackChan / M5Dial\nSPI LCD + dirty rects]
    end

    subgraph NonESP["Non-ESP Physical Devices"]
        PicoCalc[PicoCalc / RP2040-RP2350\nUF2 bootloader + Pico SDK]
        Remarkable[reMarkable Paper Pro\nDRM/KMS e-ink + evdev pen]
        Loupedeck[Loupedeck Live\nserial display + Go driver]
        Cardputer[Cardputer / Zebra / Framework\nadjacent physical devices]
    end

    subgraph CrossCutting["Cross-cutting Patterns"]
        BrowserCoproc[Browser as coprocessor\nCanvas dither / RGB565 / ESC-POS encode]
        Transport[Transport\nBLE / HTTP / USB serial / UART / SD]
        DirtyRects[Dirty rectangles\nregion coalescing + backpressure]
        Provisioning[Provisioning\nBLE GATT + Curve25519 + NVS]
        FlashLoad[Firmware loading\nESP-IDF flash / UF2 / BOOTSEL]
        RevEng[Reverse engineering\nGhidra / DRM ioctls / evdev / transcript mining]
    end

    subgraph FailureModes["Failure Modes"]
        Banding[Thermal banding\nserial underfeed / power]
        Tearing[Display tearing\nSPI clock too high]
        InitOrder[ESP-Hosted init order crash]
        NoFramebuffer[No /dev/fb0 on Paper Pro]
        BootMismatch[UF2 vs stock bootloader mismatch]
        WAMRBug[WAMR flash-mapped buffer writability]
        TransportStorm[Transport storms\nqueue flooding]
    end

    BrowserCoproc --> Transport
    Transport --> ESP32Firmware
    Transport --> NonESP
    AtomS3R --> Provisioning
    AtomS3R --> BrowserCoproc
    Tab5 --> BrowserCoproc
    M5StackChan --> DirtyRects
    Loupedeck --> DirtyRects
    PaperS3 --> DirtyRects
    Remarkable --> RevEng
    PicoCalc --> FlashLoad
    PaperS3 --> WAMRBug

    BrowserCoproc -.cross-link.-> Topic7[Topic 7: browser-side widget runtime]
    BrowserCoproc -.cross-link.-> Topic3[Topic 3: Almanach layout / rasterization]
    Loupedeck -.cross-link.-> Topic2[Topic 2: Goja JS runtime API]
    Provisioning -.cross-link.-> Topic4[Topic 4: Almanach render service hosted]
    RevEng -.cross-link.-> Topic5[Topic 5: transcript-mined serial bug]
    Remarkable -.cross-link.-> Topic6[Topic 6: book indexing / Obsidian sync]
```

**Key architectural invariants**:
- Move expensive/iteration-heavy work out of firmware into browser/host; keep firmware as thin measurable bridge to physical I/O.
- Measurement-drawing parity (same font/shaping/coordinate system) applies to both Canvas typography (T3) and e-ink/thermal output (T1).
- Dirty rectangles + region coalescing + backpressure-safe writer is the universal display-pipeline pattern across ESP32, Loupedeck, and Paper Pro.
- BLE provisioning uses Security 1 / Curve25519 / 6-digit PoP; SoftAP as fallback for non-BLE devices.

---

## Topic 2: JavaScript / Goja / xgoja / DSLs

**Merged from**: `02a` (runtime kernel, jsverbs, xgoja, TypeScript) + `02b` (DSLs, Geppetto, Durable Objects, auth hosts)

```mermaid
flowchart TD
    subgraph Core["Runtime Kernel"]
        GoHost[Go host owns\ninvariants/resources/lifecycle]
        Engine[engine.Runtime\nVM + owner + event loop]
        Owner[RuntimeOwner.Call\nserialized VM access]
        Context[Request/async context\nstartup vs lifetime vs call]
        Modules[CommonJS module registry\nGo-backed providers]
    end

    subgraph GenLayer["Generation Layer"]
        Jsverbs[jsverbs scanner\nstatic sentinel metadata]
        Binding[Shared binding plan\navoids parse/invoke drift]
        Glazed[Glazed/Cobra command surface]
        XgojaBuild[xgoja buildspec\ncompile-time provider packages]
        RuntimeProfile[Runtime profile\nper-command capability boundary]
        RuntimePlan[RuntimePlan v2\nSourceRegistry / source graph]
        Assets[Embedded assets/help]
    end

    subgraph TSLayer["TypeScript Layer"]
        DTS[Generated .d.ts descriptors]
        Esbuild[esbuild compile layer\npkg/tsscript]
        HotReload[HTTP hot reload\nblue/green manager]
    end

    subgraph AppLayer["DSLs and Applications"]
        GojaDSL[Go-backed fluent DSL\nGo owns state + validates]
        GeppettoWrap[Geppetto wrapper-first\nhidden-ref __geppetto_ref]
        DurableObj[Durable Objects\nidentity-bound actor + SQLite]
        HTTPComp[HTTP composition\nmountable handlers + WebSocket]
        AuthRoutes[Express auth route planner\nplanned routes to generated host auth]
        KeycloakAuth[xgoja Keycloak auth host]
        RateLimit[Planned route rate limiting]
        TokenFam[Token families + device auth flow]
    end

    subgraph FailureModes["Failure Modes"]
        SchemaDrift[Schema/buildspec/runtime drift]
        UnsafeSharing[Unsafe runtime sharing]
        PlainObjDrift[Plain-object domain state drift]
        ScopeBug[Source scoping bugs]
        PromisePoll[Promise polling v1 tradeoff]
        LegacyConversion[v2-to-legacy metadata loss]
    end

    GoHost --> Engine --> Owner --> Context --> Modules
    Modules --> Jsverbs --> Binding --> Glazed
    Modules --> XgojaBuild --> RuntimeProfile --> RuntimePlan
    RuntimePlan --> Assets
    Esbuild --> Jsverbs
    Esbuild --> Engine
    DTS --> RuntimeProfile

    Modules --> GojaDSL
    Modules --> GeppettoWrap
    GeppettoWrap --> DurableObj
    DurableObj --> HTTPComp
    HTTPComp --> AuthRoutes --> KeycloakAuth
    AuthRoutes --> RateLimit --> TokenFam

    RuntimePlan -.cross-link.-> Topic5[Topic 5: Geppetto provider integration]
    GojaDSL -.cross-link.-> Topic6[Topic 6: goja-bleve, RAG scripting]
    GojaDSL -.cross-link.-> Topic7[Topic 7: Widget IR, Fringe DSL, CSS visual diff]
    GojaDSL -.cross-link.-> Topic1[Topic 1: Loupedeck JS API, browser-side firmware UI]
    KeycloakAuth -.cross-link.-> Topic4[Topic 4: K3s/Vault/Keycloak deployment]
    DurableObj -.cross-link.-> Topic6[Topic 6: SQLite object storage]
```

**Key architectural invariants**:
- JavaScript owns composition; Go owns domain state, validation, resources, lifecycle, and final typed values.
- Compile-time Go module composition (xgoja) is safer than dynamic Go plugins.
- Runtime profile selection is a capability boundary, not just convenience.
- Wrapper-first APIs are mandatory when credentials, provider config, sessions, or typed domain state matter.
- Hard-cutover discipline: delete legacy paths once typed substrate exists; do not wrap.

---

## Topic 3: Typography / Layout / Design Systems

**Merged from**: `03a` (Pretext, print layout, canvas measurement) + `03b` (DMETA, CSS visual diff, font tooling)

```mermaid
flowchart TD
    subgraph Measurement["Measurement-Driven Typography"]
        Pretext[Pretext two-stage\nprepare segments/measures\nlayout computes line count/height]
        CanvasMeasure[Canvas measureText\nmeasurement-drawing parity]
        PrepareLayout[prepare/layout split\n500-600x faster than DOM]
        Cassowary[Cassowary solve-measure loop\nnonlinear text height feedback]
        Reflow[Region-based text reflow\nfree rect + line-band obstruction]
        OrthoFrame[Orthogonal frame/run engine\nstructural invariants]
        PosterFit[Responsive poster solver\nmeasure + fit + score]
    end

    subgraph DesignSystems["Semantic Design Systems"]
        DMETA[DMETA design-system factory\nsemantic archetypes + capabilities + actions]
        WidgetIR[Widget / presentation IR]
        Generated[Generated React scaffold]
        Promoted[Promoted hand-owned React]
        Governance[CSS governance\nnarrowest durable owner]
        TTC[TTC layered React design system\ntokens/foundation/layout/atoms/molecules/organisms]
    end

    subgraph VisualParity["Evidence-Based Visual Parity"]
        Baseline[Prototype / imported original baseline]
        CSSDiff[css-visual-diff\npixel + computed CSS + cascade winner]
        Storybook[Storybook contract surface]
        ParityLoop[Visual parity repair loop]
        EmbedWidget[Embeddable semantic diff widgets]
    end

    subgraph FontTools["Font and Typography Tooling"]
        TypoScope[TypoScope Firefox extension]
        TypoDebug[Typography debug palette\ncomputed-style sampling / CSS vars]
        TTCFont[TTC extraction / font-util]
        TTFRender[TTF glyph-outline VM renderer]
        RasterBug[TTF rasterizer bug hunting]
        Sphinx[Sphinx LaTeX PDF typography]
    end

    subgraph FailureModes["Failure Modes"]
        HeightDiv[Pretext heights diverge from CSS\nabsolute positioning]
        FontCache[Pretext font-cache poisoning\nnarrow widths]
        FontString[Canvas font string must match CSS]
        NonlinearText[Constraint solver cannot express\nnonlinear text height directly]
        ParityDrift[Visual parity drift\nIR vs promoted vs Storybook vs original]
        DuplicateCSS[CSS decisions duplicated locally\nbecome unreviewable]
    end

    Pretext --> PrepareLayout
    CanvasMeasure --> Pretext
    PrepareLayout --> Cassowary
    PrepareLayout --> Reflow
    PrepareLayout --> OrthoFrame --> PosterFit

    DMETA --> WidgetIR --> Generated --> Promoted
    Promoted --> Storybook
    Promoted --> Governance
    TTC --> Governance

    Baseline --> CSSDiff --> ParityLoop
    ParityLoop --> Promoted
    CSSDiff --> EmbedWidget

    DMETA -.cross-link.-> Topic2[Topic 2: Goja DSL for CSS visual diff]
    DMETA -.cross-link.-> Topic7[Topic 7: generated UI / Widget IR / admin DSL]
    CSSDiff -.cross-link.-> Topic7[Topic 7: browser overlay lens / component extraction]
    CSSDiff -.cross-link.-> Topic5[Topic 5: transcript-driven design-system recovery]
    Pretext -.cross-link.-> Topic1[Topic 1: Almanach print layout / thermal rasterization]
    FontTools -.cross-link.-> Topic7[Topic 7: browser-based font/typography tools]
```

**Key architectural invariants**:
- Measurement-drawing parity is the only foundation: `ctx.measureText` and `ctx.fillText` must use the same font/shaping/coordinate system.
- Two-stage layout: slow `prepare()` once, fast `layout()` many times. Pretext is for page-break decisions, not absolute CSS positioning.
- Structural invariants over computed targets: orthogonality by derived axes, not recalculated angles.
- Generated scaffolds become promoted hand-owned React with provenance; CSS governance assigns each decision to its narrowest durable owner.
- Visual parity requires explicit roles: imported original, DMETA IR, generated artifacts, promoted React, Storybook fixtures.

---

## Topic 4: Infra / Auth / Deployment / GitOps

**Merged from**: `04a` (hosting evolution, secret/identity, app deployment) + `04b` (DNS/TLS, backup, release trains)

```mermaid
flowchart TD
    subgraph Platform["Platform Evolution"]
        Coolify[Coolify on Hetzner\nstatus: historical]
        K3s[Hetzner K3s GitOps platform\nstatus: current]
        Terraform[Terraform\nprovisions VM/DNS/firewall]
        CloudInit[cloud-init\nbootstraps K3s + Argo CD]
        ArgoCD[Argo CD\nreconciles desired state]
    end

    subgraph Secrets["Secret and Identity Plane"]
        Vault[Vault secret plane\nKMS auto-unseal + Raft]
        Keycloak[Keycloak identity plane\nOIDC realms + clients]
        K8sAuth[Kubernetes auth / VSO\ndelivers secrets to workloads]
        GHAOIDC[GitHub Actions OIDC\nshort-lived Vault tokens]
        GitHubApp[GitHub App tokens\nGitOps PR automation]
        KeycloakAdmin[Terraform-managed\nKeycloak admin OIDC]
    end

    subgraph Deploy["Application Deployment"]
        Apps[Hosted apps / static sites\n/ protocol services]
        StaticContract[Static-sites 3-contract model\nsource artifact / GitOps handoff / cluster serving]
        AppPatterns[App patterns: VSO secrets\nsync waves / migration Jobs]
    end

    subgraph Network["DNS / TLS / Networking"]
        DigitalOceanDNS[DigitalOcean DNS zone]
        CertManager[cert-manager ACME DNS-01]
        Traefik[Traefik ingress\nTLS termination + routing]
        Tailscale[Tailscale overlay\nWireGuard mesh]
        XMPPProto[XMPP non-HTTP protocol\nhostPort + firewall + SRV DNS]
    end

    subgraph Ops["Backup / Resilience / Publishing"]
        Restic[Restic SFTP backup baseline\nlaptop to TrueNAS]
        TrueNASBackup[TrueNAS + Vault credentials\nSFTP fail-closed]
        ReleaseTrain[Release train invariant\nGOWORK=off validation]
        GggCLI[ggg CLI\nPR readiness + Codex gates]
        TrustedPub[npm Trusted Publishing\ntokenless OIDC]
        BufPub[Buf schema publishing\nprotobuf distribution]
        DaggerSplit[Dagger/GoReleaser split-build]
    end

    subgraph FailureModes["Failure Modes (all resolved)"]
        StateDrift[Terraform state drift\nuncommitted DNS apply]
        RebootOutage[k3s post-reboot outage\nTraefik disabled + CCM RBAC race]
        DNATHealth[DNAT proxy false health]
        SchedSat[Scheduler request saturation\n96% CPU / 95% memory]
        DCRFail[Keycloak DCR scope mismatch\nfor Claude]
        NFSSilent[NFS silent mount failure\nempty local dir masquerade]
        VSOShape[VSO secret shape mismatch\nTraefik basicAuth _raw]
        SyncDeadlock[PVC sync-wave deadlock]
        FlatArgo[Flat Argo CD taxonomy\nunreviewable at scale]
    end

    Coolify ==> K3s
    Terraform --> K3s
    CloudInit --> K3s
    K3s --> ArgoCD --> Apps
    K3s --> Vault
    Keycloak --> Vault
    Vault --> K8sAuth --> Apps
    GHAOIDC --> Vault
    GitHubApp --> ArgoCD
    KeycloakAdmin --> Keycloak

    DigitalOceanDNS --> CertManager --> Traefik
    Tailscale --> Traefik
    Traefik --> Apps
    XMPPProto --> Traefik

    Restic --> TrueNASBackup
    ReleaseTrain --> GggCLI
    GggCLI --> TrustedPub
    GggCLI --> BufPub
    DaggerSplit --> ReleaseTrain

    K3s -.cross-link.-> Topic2[Topic 2: xgoja Keycloak auth host deployment]
    Vault -.cross-link.-> Topic2[Topic 2: token families + device auth]
    ArgoCD -.cross-link.-> Topic7[Topic 7: static sites / vault publishers]
    ArgoCD -.cross-link.-> Topic5[Topic 5: go-minitrace transcript-driven ops]
    ReleaseTrain -.cross-link.-> Topic2[Topic 2: go-go-goja ecosystem releases]
    GggCLI -.cross-link.-> Topic5[Topic 5: Codex review signal model]
    TrueNASBackup -.cross-link.-> Topic1[Topic 1: Jellyfin/NFS power outage]
```

**Key architectural invariants**:
- Explicit ownership boundaries: each system owns one layer and does not perform the next layer's job.
- Contracts over scripts: source artifact contract, GitOps handoff contract, cluster serving contract.
- Short-lived credentials everywhere: OIDC tokens, Vault-issued tokens, GitHub App installation tokens, npm Trusted Publishing.
- Day-two operations matter: documentation, taxonomy, app cleanup, backups, monitoring, validation.
- Terraform owns durable infrastructure/DNS; cert-manager owns ephemeral ACME challenge DNS; Argo CD owns Kubernetes desired state.

---

## Topic 5: AI Agents / Transcripts / Observability

**Merged from**: `05a` (go-minitrace, sessionstream, Geppetto) + `05b` (Pi extensions, LLM proxy, dashboards, a14y)

```mermaid
flowchart TD
    subgraph Retrospective["Retrospective Transcript Analysis"]
        NativeJSONL[Native agent session JSONL]
        Convert[go-minitrace convert]
        Archive[Canonical minitrace archive\n.minitrace.json v0.2.0]
        NormDB[Normalized transcript SQLite\nmt.db() 9-10 tables]
        QueryRepo[JS query repository\nscanner-first __verb__ commands]
        HTMLReport[Self-contained HTML report\ninlined JSON + CDN libs]
        ChurnAnalysis[Tool-call churn analysis\nfrequency / transitions / retry loops]
        Authorizer[SQLite authorizer\ncompile-time table allowlist]
    end

    subgraph Live["Live Streaming Observability"]
        ProviderStream[LLM provider stream]
        GeppettoEngine[Geppetto provider engine\nnormalizes provider events]
        ChatPlugin[Chat plugin\npublishes typed events]
        Hub[Sessionstream hub\nprojections + fanout]
        WSTransport[WebSocket transport\nprotobuf frames]
        BrowserReducer[Browser parser\nRedux timeline]
        PinocchioRec[Pinocchio recorder\ndebug API + SQLite reconcile export]
        Correlation[Provider-to-browser traceability\nevents.Correlation identity]
    end

    subgraph PiSurface["Pi Core and Extensions"]
        PiExt[Pi extension\n.ts + jiti + ExtensionAPI]
        Registry[Pi shared registry\nregisterPiExtension + Symbol.for]
        ToolDeleg[Thin-boundary tool delegation\npi.exec to external CLIs]
        PiLauncher[pi-launcher\nYAML profile compiler]
        ScopedModels[Pi scoped models\nenabledModels cycle]
        Compaction[Compaction extension\nrewriting middle session context]
        SessionSearch[Session search extension\ntool call history + fork points]
        ResponseViewer[Response viewer extension]
    end

    subgraph Providers["Provider / Tool-Calling"]
        LLMProxy[LLM proxy\nOpenAI-compatible over Geppetto profiles]
        ChatProvider[ChatProvider headless runtime\ninstance-scoped registries]
        ProviderCompat[Provider compatibility contract\ncompat object consumed at request builder]
        ProviderReplay[Provider replay bug\nduplicate Responses item IDs]
        ThinkingContent[Thinking-content dampening\nsystem prompt + tools reduce reasoning]
        FrontendTool[Frontend tool round trip\nChatFrontendToolCallRequested → browser → result → resume]
    end

    subgraph Dashboards["Dashboards / Readability"]
        StreamingDash[Streaming agent dashboard\nobserver → mapper → projector → entity-wrapper UI event]
        SharedProjector[Shared projector\none event → timeline entity + UI event parity]
        MinitraceUI[go-minitrace web UI\nsession browser / transcript reader / SQL workbench]
        A14y[Agent-readable site\nserver routing contract before SPA fallback]
        MarkdownMirror[Markdown mirror\n.md suffix + Accept: text/markdown]
        SSRSidecar[SSR sidecar\nNode Express renderToString + RTK Query preload]
    end

    NativeJSONL --> Convert --> Archive --> NormDB --> QueryRepo --> HTMLReport
    QueryRepo --> ChurnAnalysis
    NormDB --> Authorizer

    ProviderStream --> GeppettoEngine --> ChatPlugin --> Hub --> WSTransport --> BrowserReducer
    GeppettoEngine --> PinocchioRec
    Hub --> PinocchioRec
    BrowserReducer --> PinocchioRec
    Correlation -.connects.-> GeppettoEngine
    Correlation -.connects.-> BrowserReducer

    PiExt --> Registry --> ToolDeleg
    Registry --> PiLauncher
    Registry --> StreamingDash
    Registry --> Compaction
    Registry --> SessionSearch
    Registry --> ResponseViewer

    LLMProxy --> ChatProvider
    ChatProvider --> Hub
    ProviderCompat --> LLMProxy

    StreamingDash --> SharedProjector
    A14y --> MarkdownMirror
    A14y --> SSRSidecar

    NormDB -.cross-link.-> Topic6[Topic 6: document co-read graph / DuckDB]
    Hub -.cross-link.-> Topic7[Topic 7: ChatProvider / chat overlay / web chat]
    Hub -.cross-link.-> Topic2[Topic 2: goja-sessionstream xgoja binding]
    LLMProxy -.cross-link.-> Topic2[Topic 2: Geppetto wrapper-first JS API]
    A14y -.cross-link.-> Topic7[Topic 7: single-binary Go+SPA / docsctl]
    A14y -.cross-link.-> Topic6[Topic 6: Retro Obsidian Publish / knowledge base]
    ChurnAnalysis -.cross-link.-> Topic1[Topic 1: transcript-mined Loupedeck serial bug]
    Registry -.cross-link.-> Topic2[Topic 2: Pi extensions TypeScript surfaces]
```

**Key architectural invariants**:
- Reusable packages emit neutral records; the application owns storage, debug APIs, and exports.
- Provider-to-browser traceability is the core invariant: provider delta → Geppetto record → UI event → frontend frame → timeline entity.
- Retrospective analysis has converged on normalized SQLite (not DuckDB UNNEST) as the canonical substrate.
- Pi extensions delegate to external CLIs rather than reimplementing capabilities; the boundary is thin by design.
- Agent readability is an HTTP routing commitment before the SPA fallback, not a frontend enhancement.

---

## Topic 6: Data / RAG / OCR / Search

**Merged from**: `06a` (RAG evaluation, Bleve/FAISS, book OCR) + `06b` (codebase browser, Readwise, co-read graph, knowledge base)

```mermaid
flowchart TD
    subgraph RAG["RAG Evaluation System"]
        Source[Source → Document → Chunk\n→ Embedding → Search → Evaluation]
        ChunkID[Strategy-aware chunk identity\ndocument_id + strategy_id + chunk_index]
        EmbedID[Provider-aware embedding identity\nchunk_id + provider + model + text_hash]
        TwoDB[Two-database architecture\ncorpus DB vs engine DB]
        TTC_corpus[TTC SQLite corpus\nWordPress/WooCommerce export]
        WPDump[WordPress/WooCommerce MySQL dump]
        RAGUI[React corpus explorer\nRTK Query + Vite]
    end

    subgraph Search["Search Index Layer"]
        SQLiteCanon[SQLite canonical store]
        DerivedIdx[Derived disposable index\nrebuildable from SQLite]
        BM25[Bleve BM25 lexical]
        VectorBrute[Brute-force vector\nscan SQLite embeddings]
        VectorFAISS[FAISS vector KNN\nCGO build-tag-gated]
        HybridRRF[Hybrid RRF fusion\nreciprocal-rank k=60]
        GojaBleve[goja-bleve\nrequire bleve for JS]
        XgojaVector[xgoja vector runtime\nbleve + geppetto + jsverbs]
    end

    subgraph OCR["Book OCR Workflow"]
        PageImg[Page images\nPyMuPDF render]
        VLM[VLM OCR model calls\nPinocchio provider]
        RawTurn[Persisted raw turns\nGeppetto evidence]
        StructJSON[StructuredPageOCR JSON\ntarget-page-only invariant]
        DetRender[Deterministic Markdown/PDF\nGo-owned rendering]
        Repair[Targeted repair loop\nrerun selected pages]
        WorkQueue[SQLite work queue\nBEGIN IMMEDIATE atomic claims]
    end

    subgraph Browsers["Local Corpus Browsers"]
        CodebaseBrowser[Codebase Browser\nGo/AST → SQLite → static SPA]
        Readwise[Readwise Viewer\nSQLite + FTS5 → Bleve design]
        CoRead[Document Co-Read Observatory\ntranscript → DuckDB → graph]
        RetroObsidian[Retro Obsidian Publish\nvault → Go+SPA + Bleve + SSR]
        KBPlaybook[KB Playbook\n304 reports → 18 entries]
        SmailnailMirror[Smailnail SQLite Mirror\nIMAP → mail KB]
    end

    subgraph FailureModes["Failure Modes"]
        ChunkBug[Chunking termination bug\noverlap loop unbounded]
        SparseEmb[Sparse embedding coverage\nsmall source-skewed samples]
        CorpusGaps[Corpus coverage gaps\nincomplete product text]
        SQLiteConc[SQLite concurrency hazard\nparallel OCR workers]
        FAISSFrag[FAISS build fragility\nmissing headers / CGO_LDFLAGS]
        OCRDrift[OCR hallucination\nlist-page drift / caption bleed]
        ViewFreeze[snapshot_refs view freeze\n60s browser freeze]
        GOWORKBug[GOWORK=off in worktrees\nsilent empty DBs]
        RegexFrag[Regex table extraction\nfails on quoted identifiers]
    end

    WPDump --> TTC_corpus --> Source
    Source --> ChunkID --> EmbedID
    SQLiteCanon --> DerivedIdx
    DerivedIdx --> BM25
    DerivedIdx --> VectorBrute
    VectorBrute --> VectorFAISS
    BM25 --> HybridRRF
    VectorFAISS --> HybridRRF
    GojaBleve --> XgojaVector

    PageImg --> VLM --> RawTurn --> StructJSON --> DetRender --> Repair
    VLM --> WorkQueue

    CodebaseBrowser --> SQLiteCanon
    Readwise --> SQLiteCanon
    CoRead --> SQLiteCanon
    RetroObsidian --> SQLiteCanon

    SQLiteCanon -.cross-link.-> Topic2[Topic 2: Durable Objects SQLite storage]
    SQLiteCanon -.cross-link.-> Topic5[Topic 5: minitrace normalized SQLite]
    GojaBleve -.cross-link.-> Topic2[Topic 2: Go-backed JS wrapper pattern]
    VLM -.cross-link.-> Topic5[Topic 5: Geppetto/Pinocchio profiles]
    CoRead -.cross-link.-> Topic5[Topic 5: go-minitrace transcript mining]
    RetroObsidian -.cross-link.-> Topic7[Topic 7: single-binary Go+SPA]
    RetroObsidian -.cross-link.-> Topic5[Topic 5: agent-readable / a14y]
    CodebaseBrowser -.cross-link.-> Topic7[Topic 7: browser SPA + Go/Wasm]
    DetRender -.cross-link.-> Topic3[Topic 3: Pretext print layout / PDF typography]
```

**Key architectural invariants**:
- SQLite is the canonical store; all search indexes and workflow artifacts are derived/rebuildable.
- Strategy-aware chunk identity and provider-aware embedding identity enable multi-strategy comparison and rerun-safety.
- Two-database architecture separates corpus reads from workflow orchestration to prevent WAL contention.
- Evidence-preserving model workflow: raw turns → structured JSON → deterministic rendering → targeted repair.
- Static browser artifacts run from `file://` with SQLite-as-browser-runtime (sql.js) or server-backed.

---

## Topic 7: Web UI / Apps / Media / Productivity

**Merged from**: `07a` (local app shells, backend-driven UI) + `07b` (chat overlays, media pipelines, browser extensions)

```mermaid
flowchart TD
    subgraph LocalShells["Local-First App Shells"]
        SingleBinary[Single-binary Go + SPA\ngo:embed pattern]
        GoWasm[Go/Wasm browser tool\nGOOS=js GOARCH=wasm]
        Wails[Wails desktop shell\nbound methods + events]
        mdview[md-view daemon\nstatus: migrated to Wails]
        GoGoParc[Go-Go Parc Website\nsingle-binary + git-sync]
        RetroObs[Retro Obsidian Publish\nvault browser + SSR + a14y]
        RenderBody[RenderBody fragment contract\nchrome-free HTML fragment]
        ReRunnable[Re-runnable DOM augmentation\nsurvives fragment swaps]
    end

    subgraph BackendUI["Backend-Driven UI Systems"]
        UIDSL[Backend-driven UI DSL\nUI as data transported from backend]
        WidgetIR[Widget IR\nJSON-compatible node tree]
        Renderer[Renderer-as-interpreter\nReact switches on node.kind]
        OpaqueAction[Opaque action ID\nbrowser dispatches, backend resolves]
        PageVersion[Page version scoping\nstale actions return effects]
        StorybookC[Storybook contract surface\nfixtures for every node/widget kind]
        ImportCap[Import-as-capability\nmodule registry rewrites specifiers]
        Fringe[Fringe Admin DSL\nrenderer + Goja + protobuf]
        WidgetRuntime[Browser-Side React Widget Runtime\nesbuild-wasm + blob URL]
        WidgetRenderer[WidgetRenderer Standalone\nGoja-authored React-rendered UI]
    end

    subgraph Chat["Chat Overlay and Web Chat"]
        ChatOverlay[Chatbot Overlay Framework\ntyped widget streaming + frontend tools]
        ChatProvider[Generic ChatProvider\nheadless provider runtime]
        CoinVaultChat[CoinVault Web Chat\nproduction adopter + debug export]
        ChatProtocol[Canonical Chat Event Protocol\nreducer-shaped provider adapters]
        FrontendTool[Frontend tool registry\nbrowser-advertised capabilities]
        HumanApproval[Human-in-the-loop tool mode\napproval as tool mode]
        SnapshotHydrate[Snapshot-before-live hydration\nbuffer frames until snapshot applied]
        StableEntity[Stable entity id across patch/terminal]
    end

    subgraph Media["Media Creation Pipelines"]
        Screencast[Screencast Studio\nDSL → plan → ffmpeg/GStreamer]
        Jingle[Jingle Extractor\nMiniMax + Demucs + WhisperX]
        RabbitHole[Rabbit Hole Podcast Intros\nRemotion video compositions]
        PlanCompiler[Compiled plan as central abstraction\nintent → config → plan → execution]
        SubprocessSup[Web server as runtime supervisor\nstaged shutdown ordering]
    end

    subgraph BrowserExt["Browser Automation and Extensions"]
        ChromeOverlay[Chrome DOM Overlay Extractor\nManifest V3 + html2canvas]
        HoverInspect[Hover Component Inspector\nshadow DOM overlay]
        TypoScope[TypoScope Firefox extension\ntypography measurement]
        TabTracker[Firefox Tab Tracker\nWebExtension + Native Messaging]
        SurfGo[surf-go Browser Verbs\nprobe → embed → dual-mode command]
        DOMScrape[DOM Scraping Experiment\njsdom + numbered scripts]
        BrowserLens[Browser overlay lens\nfixed-position viewport-coordinated]
        DOMGeometry[DOM geometry capture\ngetBoundingClientRect + computed CSS]
        LLMValidLoop[LLM-DOM validation loop\nLLM suggests selectors, DOM validates]
    end

    subgraph FailureModes["Failure Modes"]
        SPAWeak[SPA-only shells weak for agents/search]
        OneShotAug[One-shot DOM augmentation breaks on reload]
        SchemaGrowth[Schema/fixture growth outruns renderer]
        AbsentEmpty[Absent-vs-empty content overwrite\nprotobuf/JSON projection]
        EntityIDUnstable[Entity ID instability\npatch vs terminal events]
        SubprocessCancel[Subprocess cancellation/shutdown semantics]
        CoordTrap[getBoundingClientRect traps\nscrolling + fixed positioning]
        ExtBundling[Extension cross-context messaging complexity]
    end

    SingleBinary --> GoGoParc
    SingleBinary --> RetroObs
    GoWasm --> SingleBinary
    Wails --> mdview
    mdview --> Wails

    UIDSL --> WidgetIR --> Renderer
    Renderer --> StorybookC
    Renderer --> OpaqueAction --> PageVersion
    Fringe --> UIDSL
    WidgetRuntime --> ImportCap
    WidgetRenderer --> WidgetIR

    ChatOverlay --> ChatProvider
    ChatProvider --> CoinVaultChat
    ChatProvider --> ChatProtocol
    ChatProvider --> FrontendTool --> HumanApproval
    ChatProtocol --> SnapshotHydrate
    ChatProtocol --> StableEntity

    Screencast --> PlanCompiler
    Jingle --> PlanCompiler
    RabbitHole --> PlanCompiler
    PlanCompiler --> SubprocessSup

    ChromeOverlay --> BrowserLens --> DOMGeometry
    DOMGeometry --> LLMValidLoop
    TypoScope --> BrowserLens

    SingleBinary -.cross-link.-> Topic5[Topic 5: agent-readable mirrors / a14y / SSR sidecar]
    SingleBinary -.cross-link.-> Topic6[Topic 6: codebase browser / Readwise / Retro Obsidian]
    SingleBinary -.cross-link.-> Topic4[Topic 4: static sites deployment / GitOps]
    WidgetIR -.cross-link.-> Topic2[Topic 2: Goja UI DSL / Widget IR to xgoja]
    WidgetIR -.cross-link.-> Topic3[Topic 3: DMETA generated React / visual parity]
    ChatProvider -.cross-link.-> Topic5[Topic 5: Sessionstream hub / LLM proxy]
    ChatProvider -.cross-link.-> Topic2[Topic 2: Geppetto JS bindings]
    BrowserLens -.cross-link.-> Topic3[Topic 3: CSS visual diff / Pyxis baseline catalog]
    PlanCompiler -.cross-link.-> Topic1[Topic 1: firmware subprocess supervision]
    GoWasm -.cross-link.-> Topic6[Topic 6: sql.js / WASM SQLite in browser]
```

**Key architectural invariants**:
- Local-first: single binary serving API + static frontend; Go renderer/core reused across CLI, HTTP, and desktop shells.
- UI as data: page/node/action/widget IR transported from backend or Goja scripts; renderer is an interpreter, not arbitrary executable code.
- Chat mechanics separated from product rendering: headless ChatProvider owns WebSocket/timeline/tool registries; apps keep product UI and CSS.
- Media pipelines: declarative plan over raw commands; web server is runtime supervisor, not just transport.
- Browser overlays are inspection/selection lenses: DOM geometry and computed style capture feed visual diff, component extraction, and typography measurement.

---

## Cross-Topic Bridge Map

This map shows only the bridges between topics, omitting intra-topic detail.

```mermaid
flowchart LR
    T1[Topic 1\nHardware/ESP32]
    T2[Topic 2\nJS/Goja/xgoja]
    T3[Topic 3\nTypography/Design]
    T4[Topic 4\nInfra/GitOps]
    T5[Topic 5\nAgents/Observability]
    T6[Topic 6\nData/RAG/OCR]
    T7[Topic 7\nWeb UI/Apps]

    T1 --"browser as coprocessor"--> T7
    T1 --"Loupedeck JS API"--> T2
    T1 --"Almanach layout/raster"--> T3
    T1 --"transcript-mined serial bug"--> T5
    T1 --"book indexing / Obsidian sync"--> T6
    T1 --"Jellyfin/NFS outage"--> T4

    T2 --"Widget IR / Fringe DSL"--> T7
    T2 --"goja-bleve / RAG scripting"--> T6
    T2 --"Geppetto provider integration"--> T5
    T2 --"xgoja Keycloak auth host"--> T4
    T2 --"Loupedeck / browser firmware UI"--> T1
    T2 --"Durable Objects SQLite"--> T6

    T3 --"DMETA generated React"--> T7
    T3 --"CSS visual diff / Pyxis"--> T7
    T3 --"Goja DSL for visual diff"--> T2
    T3 --"transcript-driven design recovery"--> T5
    T3 --"Almanach print / thermal raster"--> T1
    T3 --"Pretext PDF typography"--> T6

    T4 --"static sites / GitOps deployment"--> T7
    T4 --"token families / device auth"--> T2
    T4 --"transcript-driven ops"--> T5
    T4 --"release trains / ecosystem"--> T2

    T5 --"ChatProvider / chat overlay"--> T7
    T5 --"Sessionstream xgoja binding"--> T2
    T5 --"go-minitrace / co-read graph"--> T6
    T5 --"agent-readable / a14y"--> T7
    T5 --"agent-readable / a14y"--> T6
    T5 --"transcript-mined serial bug"--> T1
    T5 --"Codex review signal"--> T4

    T6 --"single-binary Go+SPA"--> T7
    T6 --"SQLite canonical store"--> T2
    T6 --"SQLite / minitrace"--> T5
    T6 --"codebase browser / WASM"--> T7
    T6 --"Retro Obsidian / a14y"--> T5
    T6 --"OCR / Pretext PDF"--> T3

    T7 --"browser coprocessor / firmware UI"--> T1
    T7 --"Goja UI DSL / Widget IR"--> T2
    T7 --"CSS visual diff / browser lens"--> T3
    T7 --"static sites / GitOps"--> T4
    T7 --"ChatProvider / Sessionstream"--> T5
    T7 --"codebase browser / WASM SQLite"--> T6
```

---

## Refinement notes

- These v2 maps are denser than the v1 first-pass maps: they use evidence-backed typed nodes and labeled edges from 14 partition summaries rather than first-batch overview reports.
- Current-vs-historical status is marked for infra (Coolify→K3s) and runtime (RuntimePlan v1→v2, md-view→Wails).
- Failure modes are promoted to first-class nodes in every topic map, not buried in notes.
- The cross-topic bridge map makes explicit which concepts are shared between topics, preventing isolated maps.
- If a third pass is needed, the highest-value refinement would be: (1) deeper coverage of DMETA/TTC/Widget IR convergence, (2) Sessionstream/minitrace schema convergence question, (3) current-vs-deprecated hosted app inventory after the Argo CD reorg, and (4) the "browser as coprocessor" cross-cutting pattern as its own map.
