---
Title: 05a Agents Transcripts Sessionstream (Partition A)
Ticket: PROJECT-MAPS-001
Status: active
Topics:
    - research
    - projects
    - concept-maps
    - agents
    - observability
DocType: sources
Intent: long-term
Owners: []
RelatedFiles:
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/sources/05-ai-agents-transcripts-observability.md
      Note: Parent first-batch report; this file is the condensed partition-A slice
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/03-first-pass-topic-concept-maps.md
      Note: First-pass concept map containing existing nodes/edges for cross-linking
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/02-first-batch-source-report-guidelines.md
      Note: Reporting contract (evidence levels, typed nodes, labeled edges)
ExternalSources: []
Summary: Condensed, map-ready summary of partition A (transcript analysis + go-minitrace, and Sessionstream/Pinocchio/Geppetto agent flows) for topic 05.
LastUpdated: 2026-06-22T22:00:00-04:00
WhatFor: Feed typed nodes and labeled edges into the topic-05 concept map and cross-topic bridge map.
WhenToUse: After this slice is summarized and before map synthesis merges partitions A and B.
---

# 05a Agents / Transcripts / Sessionstream (Partition A)

## Executive summary

- Partition A covers two intertwined but separable architectures: (1) **retrospective transcript analysis** via go-minitrace, and (2) **live streaming-agent observability** via Geppetto/Pinocchio/Sessionstream. The first-pass map already names this split; this condensed slice sharpens the nodes and edges.
- The transcript arc converged on a four-stage pipeline: native JSONL → canonical minitrace archive → normalized SQLite (`mt.db()`) → JS query repository → self-contained HTML report. DuckDB `UNNEST` over JSON arrays is a documented dead end; normalized SQLite is the canonical substrate.
- The streaming arc converged on a layered evidence chain: provider stream → Geppetto provider engine → chatapp runtime sink → sessionstream Hub projections → WebSocket transport → browser reducer → durable timeline. The strongest invariant is **provider-to-browser traceability** joined by typed `events.Correlation`.
- Both arcs share a design rule: **reusable packages emit neutral records; the application owns storage, debug APIs, and exports.** This is the same rule repeated at the minitrace query-safety authorizer and at the Pinocchio recorder/SQLite reconcile export.
- Canonical starting files: `Projects/2026/05/07/ARTICLE - Observer Instrumentation - Geppetto Pinocchio Sessionstream Deep Dive.md` (live observability) and `Projects/2026/06/22/ARTICLE - Analyzing Agent Tool-Calling Behavior with go-minitrace.md` (retrospective analysis).

## Scope and search method

- Corpus: Markdown project/article reports under `Projects/2026/{03,04,05,06}/` filtered to partition A of `sources/05` — namely "Transcript analysis and go-minitrace" and "Sessionstream, Pinocchio, Geppetto agent flows."
- Excluded (partition B): "Pi core and extensions", "LLM proxy/provider work and tool-calling behavior", "Dashboards, observability, readability/a14y."
- Selection rule: deeply read canonical architecture files (the two "start here" reports plus files defining invariants, schema, or hard cutovers); heading-scan or first-100-line reads for origin/cleanup/adjacent reports to confirm cross-links without duplicating detail.

## Evidence ledger

| Path | Evidence level | Lines / basis | Cluster | Why it matters |
|---|---|---|---|---|
| `Projects/2026/06/22/ARTICLE - Analyzing Agent Tool-Calling Behavior with go-minitrace.md` | read | lines 1-end | Transcript analysis | Canonical normalized-SQL pipeline; documents UNNEST dead end and `mt.db()` as the right substrate |
| `Projects/2026/05/07/ARTICLE - Observer Instrumentation - Geppetto Pinocchio Sessionstream Deep Dive.md` | read | lines 1-end | Live observability | Defines the neutral-record ownership model and provider-to-browser evidence chain |
| `Projects/2026/04/01/PROJ - go-minitrace - Web UI and Transcript Explorer.md` | read | lines 1-end | Transcript analysis | Web UI identity (session browser / transcript reader / SQL workbench); block decomposition |
| `Projects/2026/04/21/PROJ - go-minitrace - JS Commands and Structured Query Catalog PR #6.md` | read | lines 1-end | Transcript analysis | Scanner-first JS verb system; structured query catalog; nightly review workflow |
| `Projects/2026/06/07/ARTICLE - Minitrace API Redesign - From Prototype Complexity to Normalized SQL and Fluent Builders.md` | read | lines 1-end | Transcript analysis | Hard removal of legacy surfaces; nine-table normalized schema; `mt.db()` fluent builder |
| `Projects/2026/06/08/ARTICLE - SQLite Authorizer and Query Safety - Deep Dive Technical Analysis.md` | read | lines 1-end | Transcript analysis | Defense-in-depth query safety; regex table extraction failure mode; authorizer fix |
| `Projects/2026/05/09/ARTICLE - Canonical Chat Event Protocol - Provider Streams to Browser State.md` | read | lines 1-end | Live observability | Canonical event lifecycles; reducer-shaped provider adapters; sparse-patch contract |
| `Projects/2026/06/02/ARTICLE - Geppetto JS Overhaul - Wrapper First Agents Events and Storage Boundaries.md` | read | lines 1-end | Live observability | Wrapper-first API; hidden-ref enforcement; runAsync EventEmitter; storage boundary |
| `Projects/2026/05/20/ARTICLE - Pinocchio Structured Streams - Protobuf JSONL RPC and Chatapp TUI Migration.md` | read | lines 1-~1176 (50KB truncation) | Live observability | Protobuf JSONL RPC; TUI migration onto chatapp/sessionstream; debug-events-jsonl |
| `Projects/2026/06/14/ARTICLE - goja-sessionstream - Deep Dive into xgoja Sessionstream Integration.md` | read | lines 1-end | Live observability | xgoja binding for sessionstream; Promise-native APIs; Redis/Watermill host-owned distribution |
| `Projects/2026/03/17/PROJ - CoinVault - RAG Web Chat for Gold Coin Inventory.md` | read | lines 1-120 | Live observability | Concrete Pinocchio/Geppetto app; safe SQL tooling; projection widgets |
| `Projects/2026/03/17/PROJ - Claude Code Hook Events Logger - SQLite Analytics for Claude Sessions.md` | read | lines 1-100 | Transcript analysis | Capture-first telemetry origin; SQLite + views over hook events |
| `Projects/2026/04/29/PROJ - Sessionstream - Replay Store Remediation and Systemlab UI Refinement.md` | read | lines 1-120 | Live observability | Event cursor vs projection cursor split; SQLite hydration store |
| `Projects/2026/05/06/ARTICLE - Protobuf Payload Contracts and Sessionstream Schema Vet.md` | read | lines 1-120 | Live observability | Top-level `Struct` rejection; `sessionstream-lint` vettool; typed protobuf contracts |
| `Projects/2026/06/02/ARTICLE - Geppetto JS Session API - From Turns to Sessions.md` | read | lines 1-100 | Live observability | Turn→session API migration; Go-backed `AgentSession` invariants |
| `Projects/2026/05/22/ARTICLE - Sessionstream Runtime Events in Scraper.md` | read | lines 1-100 | Live observability | Sessionstream as generic substrate outside chat; domain-owned schema |
| `Projects/2026/06/22/ARTICLE - CozoDB Editor Modernization - Sessionstream Hard Cutover.md` | read | lines 1-100 | Live observability | Hard cutover pattern; notebook owns stream domain; sessionstream as substrate |
| `Projects/2026/05/04/ARTICLE - Sessionstream Chatapp CoinVault Cleanup - Protobuf Ordinals and Transcript Segments.md` | read | lines 1-100 | Live observability | Ordinal vocabulary; reusable ReasoningPlugin/ToolCallPlugin; widget schema separation |

## Condensed per-arc summaries

### Arc 1 — Transcript analysis and go-minitrace

- **Four-stage pipeline is now canonical**: native agent JSONL → `go-minitrace convert` → `.minitrace.json` archive (schema `minitrace-v0.2.0`) → `mt.db()` normalized SQLite (9–10 tables) → JS query repository → self-contained HTML report. DuckDB remains available but `UNNEST` over JSON arrays is a documented dead end inside the Goja path; normalized SQLite is the robust+ergonomic substrate (`Projects/2026/06/22` lines 27-34, 54-64; `Projects/2026/06/07` redesign).
- **Analysis is a repository of named verbs, not ad-hoc SQL.** Each question (tool frequency, transition matrix, retry loops, timing, token distribution) is a `__verb__`-declared JS command discovered by the scanner and exposed via `go-minitrace query commands`. SQL and JS sources coexist in one catalog with alias support; repository discovery precedence is `--query-repository` > env > config > embedded (`Projects/2026/04/21` PR #6).
- **Query safety is defense-in-depth.** Regex table extraction fails on quoted identifiers and CTE aliases; the SQLite authorizer (firing during `prepare` on parser-resolved names) is the correct primary check, layered with read-only prepared-statement check and text-based prefix validation (`Projects/2026/06/08`).
- **Self-contained HTML report is a deliberate artifact.** Python assembles the file (substitution + I/O); JavaScript renders client-side from inlined `DATA`/`STATS` JSON; `marked`+`DOMPurify` sanitize model markdown. Swiss minimalist typography (single red-orange accent) is a constraint, not decoration (`Projects/2026/06/22` Stage 4).
- **Timing analysis must derive from timestamps and state caveats.** The Pi adapter does not populate `output.duration_ms` or `exit_code`; inter-call gaps are upper bounds including model reasoning and user think-time. This data-quality rule shapes every timing query (`Projects/2026/06/22` warnings).

### Arc 2 — Sessionstream, Pinocchio, Geppetto agent flows

- **Neutral-record ownership model is the spine.** Sessionstream emits Hub pipeline + WebSocket transport observations; Geppetto emits provider + publish-boundary observations; Pinocchio owns the recorder, debug API, browser stream recorder, and SQLite reconcile export. Reusable packages must not learn about app storage (`Projects/2026/05/07` lines 25-34, 57-64).
- **Provider-to-browser traceability is the strongest invariant.** A provider reasoning delta can be related to a Geppetto record, a Sessionstream UI event, a frontend parsed frame, and a durable timeline entity. Provider IDs (`response_id`, `item_id`, `output_index`, `summary_index`) are carried into `ReasoningUpdate` protobuf and segment keys — sequence order is a fallback, not a contract (`Projects/2026/05/07` reasoning identity section).
- **Streaming chat is protocol design, not callback plumbing.** Canonical event lifecycles separate provider-call, text segment, reasoning segment, and tool call. Provider adapters are reducer-shaped (setup → consume → complete → persist). Sparse updates are patches, not replacements; `missing field ≠ clear value`. `events.Correlation` is first-class identity, not debug decoration (`Projects/2026/05/09`).
- **Protobuf contracts are enforced, not conventional.** Top-level `google.protobuf.Struct` is rejected by `sessionstream-lint` vettool; every command/event/UI-event/timeline-entity payload must be a concrete, feature-owned protobuf message. Pinocchio chatapp has reusable `ReasoningPlugin` and `ToolCallPlugin`; CoinVault owns only widget-specific schemas (`Projects/2026/05/06`; `Projects/2026/05/04`).
- **The substrate generalizes beyond chat.** Scraper runtime events and CozoDB notebook hints both use sessionstream as a generic typed-command/event/projection/hydration/websocket substrate, keeping domain schemas local. The hard-cutover pattern (delete legacy SEM/raw-forwarder paths, do not wrap) is the recurring migration discipline (`Projects/2026/05/22`; `Projects/2026/06/22` CozoDB).

## Candidate concept-map material

### Nodes

| Node | Type | Confidence | Notes |
|---|---|---|---|
| go-minitrace | project | high | Central transcript-analysis tool; converts native transcripts to canonical archives |
| Canonical minitrace archive | artifact | high | `.minitrace.json` schema `minitrace-v0.2.0`; stable top-level fields + `tool_calls` analytical center |
| Normalized transcript SQLite | concept | high | 9-10 tables via `mt.db()`; replaces DuckDB UNNEST and legacy `mt.legacy.*` |
| JS query repository | workflow | high | Scanner-first `__verb__`/`__section__` commands; coexists with sqleton SQL in one catalog |
| Self-contained HTML report | artifact | high | Inlined DATA/STATS JSON + CDN markdown libs; Python assembles, JS renders |
| go-minitrace web UI | platform | high | `go-minitrace serve`; session browser / transcript reader / SQL workbench; block decomposition |
| SQLite authorizer | concept | high | Compile-time table allowlist; fixes regex extraction failure mode |
| Tool-call churn analysis | workflow | high | Frequency/transition/retry-loop queries over normalized `tool_calls` table |
| Pi adapter duration_ms gap | failure-mode | high | Null `duration_ms`/`exit_code`; timing must derive from timestamps with caveats |
| UNNEST DuckDB fragility | failure-mode | high | Cast-inference errors in Goja path; documented dead end |
| Manifest advisory drift | failure-mode | medium | `manifest.json` can reflect only last `--source-session`; query file globs directly |
| Claude Code hook events logger | project | high | Capture-first telemetry origin; Python hook → SQLite + 6 views |
| Sessionstream Hub | concept | high | Generic event runtime; commands → backend events → UI/timeline projections → fanout |
| Sessionstream WebSocket transport | technology | high | Protobuf-defined frames; snapshot-before-live subscribe hydration |
| Geppetto provider engine | concept | high | Normalizes provider stream events; emits neutral observability records |
| Pinocchio chatapp | project | high | Web-chat runtime owning recorder, debug API, SQLite reconcile export |
| Pinocchio StreamDebugRecorder | artifact | high | Implements all three observer interfaces; bounded in-memory ring (default 10k) |
| Reconcile SQLite export | artifact | high | Joins backend pipeline + transport + Geppetto + frontend + timeline state |
| Canonical chat event protocol | concept | high | Provider-call/text/reasoning/tool lifecycles; `events.Correlation` identity |
| Reducer-shaped provider adapter | concept | high | setup → consume → complete → persist; per-provider native fixtures, shared lifecycle scenarios |
| Sparse-patch contract | concept | high | Missing field = absent update; empty meaningful field = provider sent empty |
| Protobuf payload contract | concept | high | Concrete feature-owned messages; `Struct` rejected at top level |
| sessionstream-lint vettool | technology | high | `go vet` analyzer enforcing typed payload registration |
| ReasoningPlugin / ToolCallPlugin | concept | high | Reusable chatapp plugins; projection of reasoning/tool lifecycle |
| Provider-to-browser traceability | concept | high | Invariant: provider delta → Geppetto record → UI event → frontend frame → timeline entity |
| Reasoning identity / provider IDs | concept | high | `response_id`/`item_id`/`output_index`/`summary_index` carried into `ReasoningUpdate` |
| Geppetto wrapper-first JS API | concept | high | Hidden-ref `__geppetto_ref`; wrappers not plain maps; explicit turns/sessions |
| runAsync EventEmitter | technology | high | Builder-level `.events(emitter)`; run-scoped refs; owner-thread settlement |
| Pinocchio protobuf JSONL RPC | technology | high | `RpcLine` protojson frames; `--rpc`/`--output jsonl`; `--debug-events-jsonl` |
| chatapp TUI migration | workflow | high | Bubble Tea over chatapp/sessionstream; removed raw Geppetto forwarders |
| goja-sessionstream xgoja binding | technology | high | `require("sessionstream")`; Promise-native; host-owned Redis/Watermill |
| Redis/Watermill event distribution | technology | medium | Host-owned; distributes events not commands; empty consumer group for fanout |
| Event cursor vs projection cursor | concept | high | Separate cursors diagnose "event stored but projection failed" |
| Sessionstream as generic substrate | concept | high | Scraper runtime events + CozoDB notebook hints reuse the substrate |
| Hard-cutover migration discipline | workflow | high | Delete legacy paths once typed substrate exists; do not wrap |
| Profile-to-browser reasoning duplication bug | failure-mode | medium | `reasoning-summary` created second thinking entity; fixed by segment-key identity |
| Subscribe hydration race | failure-mode | high | Old flow missed live events during snapshot load; fixed by hydrating-then-live ordering |
| CoinVault safe SQL tooling | project | high | PingCAP/pg_query_go parser validation; SELECT-only; LIMIT clamping |
| CoinVault projection widgets | artifact | high | `<gec:TYPE:v1>` markup → typed protobuf widget events |
| Should minitrace and sessionstream converge on one event schema? | open-question | medium | Live-vs-retrospective systems currently separate |
| Is `mt.db()` normalized SQLite the sole canonical analysis substrate? | open-question | medium | DuckDB still present but demoted for single-session analysis |

### Edges

```text
Native agent JSONL --converted by--> go-minitrace convert [high] (Projects/2026/06/22 Stage 1)
go-minitrace convert --emits--> Canonical minitrace archive [high] (Projects/2026/06/22 Stage 1)
Canonical minitrace archive --materialized by--> mt.db() normalized SQLite [high] (Projects/2026/06/22 Stage 2; Projects/2026/06/07)
mt.db() normalized SQLite --queried by--> JS query repository [high] (Projects/2026/04/21 PR #6; Projects/2026/06/22 Stage 3)
JS query repository --renders--> Self-contained HTML report [high] (Projects/2026/06/22 Stage 4)
UNNEST DuckDB fragility --superseded by--> mt.db() normalized SQLite [high] (Projects/2026/06/22 Approach 1 vs 3)
mt.db() normalized SQLite --protected by--> SQLite authorizer [high] (Projects/2026/06/08)
Pi adapter duration_ms gap --forces--> timestamp-derived timing with caveats [high] (Projects/2026/06/22 warnings)
Tool-call churn analysis --runs over--> mt.db() normalized SQLite [high] (Projects/2026/06/22 Stage 3 queries)
Claude Code hook events logger --precedes--> go-minitrace convert [medium] (Projects/2026/03/17 origin; Projects/2026/04/01 UI)
go-minitrace web UI --wraps--> JS query repository [high] (Projects/2026/04/01; Projects/2026/04/21)

LLM provider stream --decoded by--> Geppetto provider engine [high] (Projects/2026/05/07)
Geppetto provider engine --emits--> Geppetto observability Record [high] (Projects/2026/05/07)
Pinocchio chatapp --publishes--> Canonical chat event protocol events [high] (Projects/2026/05/09)
Canonical chat event protocol events --projected by--> Sessionstream Hub [high] (Projects/2026/05/07; 2026/05/04)
Sessionstream Hub --emits--> PipelineRecord [high] (Projects/2026/05/07)
Sessionstream WebSocket transport --emits--> TransportRecord [high] (Projects/2026/05/07)
Pinocchio StreamDebugRecorder --implements--> Geppetto + Sessionstream observer interfaces [high] (Projects/2026/05/07)
Pinocchio StreamDebugRecorder --exports--> Reconcile SQLite export [high] (Projects/2026/05/07)
Provider-to-browser traceability --joins--> Geppetto record + UI event + frontend frame + timeline entity [high] (Projects/2026/05/07)
Reasoning identity / provider IDs --carried into--> Pinocchio ReasoningUpdate protobuf [high] (Projects/2026/05/07)
Reducer-shaped provider adapter --normalizes--> Canonical chat event protocol events [high] (Projects/2026/05/09)
Sparse-patch contract --preserves--> previous accumulated state [high] (Projects/2026/05/09)
Protobuf payload contract --enforced by--> sessionstream-lint vettool [high] (Projects/2026/05/06)
Pinocchio chatapp --registers--> ReasoningPlugin / ToolCallPlugin [high] (Projects/2026/05/04)
Geppetto wrapper-first JS API --enforces--> hidden-ref wrappers not plain maps [high] (Projects/2026/06/02)
runAsync EventEmitter --settles on--> runtime owner thread [high] (Projects/2026/06/02)
Pinocchio protobuf JSONL RPC --routes through--> chatapp Runner + Sessionstream Hub [high] (Projects/2026/05/20)
chatapp TUI migration --removed--> raw Geppetto forwarder path [high] (Projects/2026/05/20)
goja-sessionstream xgoja binding --exposes--> Sessionstream Hub to JavaScript [high] (Projects/2026/06/14)
Redis/Watermill event distribution --injected by--> custom Go host via host services [high] (Projects/2026/06/14)
Event cursor vs projection cursor --diagnoses--> projection failure without losing events [high] (Projects/2026/04/29)
Sessionstream as generic substrate --reused by--> Scraper runtime events [high] (Projects/2026/05/22)
Sessionstream as generic substrate --reused by--> CozoDB notebook hints [high] (Projects/2026/06/22 CozoDB)
Hard-cutover migration discipline --deletes--> legacy SEM / raw-forwarder paths [high] (Projects/2026/06/22 CozoDB; 2026/05/20)
CoinVault safe SQL tooling --validates--> SELECT-only via PingCAP parser [high] (Projects/2026/03/17 CoinVault)
CoinVault projection widgets --parsed from--> <gec:TYPE:v1> markup in assistant text [high] (Projects/2026/03/17 CoinVault)
Subscribe hydration race --fixed by--> hydrating-then-live ordinal ordering [high] (Projects/2026/05/07)
Profile-to-browser reasoning duplication bug --fixed by--> segment-key identity [medium] (Projects/2026/05/07)
```

## Cross-links to other topic slices

- **Topic 02 (JavaScript/Goja/xgoja/DSLs):** go-minitrace JS query commands and the `mt.db()` fluent builder follow the `goja-text` wrapper-first builder pattern. Geppetto's `require("geppetto")` and `require("sessionstream")` are xgoja provider-registered modules; `goja-sessionstream` is the canonical xgoja integration example. The hidden-ref `__geppetto_ref` enforcement and `Validate()`/`Build()` lifecycle are shared DSL rules.
- **Topic 06 (Data/RAG/OCR/search):** CoinVault is a RAG web chat over a MySQL inventory database with safe SQL tooling — a data system with a chat surface. Transcript-driven design-system recovery (`Projects/2026/06/07`) uses DuckDB/SQLite/git over converted Pi sessions. SQLite canonical store recurs across minitrace, reconcile export, and CoinVault turn/timeline persistence.
- **Topic 07 (Web UI/apps/media/productivity):** React/Redux timeline reducers, WebSocket chat overlays, and the single-binary Go+SPA pattern (`go-minitrace serve`, Pinocchio web-chat, CozoDB editor) are shared. Self-contained HTML reports and `--debug-events-jsonl` traces are agent-readable/portable artifacts. Bubble Tea TUI migration is a terminal-app-shell concern.
- **Topic 04 (Infra/auth/deployment/gitops):** SQLite canonical store and query safety (`go-go-host/internal/sitejs/dbguard` first-token classification is referenced as a sibling but not importable by go-minitrace). The authorizer analysis explicitly notes `dbguard` lives under a different module's `internal/`.
- **Topic 01 (Hardware/embedded/ESP32):** Applied transcript analysis was used to trace the Loupedeck serial bug (`Projects/2026/04/22` — title-only in this slice, referenced by parent report).
- **Topic 03 (Typography/design-systems):** Transcript-driven design-system recovery (`Projects/2026/06/07`) bridges transcript analysis and design-system knowledge extraction.

## Start here

1. `Projects/2026/05/07/ARTICLE - Observer Instrumentation - Geppetto Pinocchio Sessionstream Deep Dive.md` — defines the live streaming-agent observability architecture, the neutral-record ownership model, and the provider-to-browser evidence chain. Read the summary, the end-to-end path diagram, and the "Reading the artifact" section.
2. `Projects/2026/06/22/ARTICLE - Analyzing Agent Tool-Calling Behavior with go-minitrace.md` — defines the retrospective transcript-analysis pipeline, the `mt.db()` normalized SQLite substrate, and the JS query repository pattern. Read the pipeline-at-a-glance diagram and Stage 2 (three ways to query).

## Report-format notes

- The two arcs are best kept as separate map regions with a bridge edge `Provider-to-browser traceability --diagnosed retrospectively by--> go-minitrace convert` because provider replay bugs and tool-call churn feed back into transcript analysis.
- The `events.Correlation` identity model and the SQLite canonical store are the strongest bridge concepts to other topic slices.
- Failure modes (UNNEST fragility, duration_ms gap, subscribe hydration race, reasoning duplication, `Struct` payload drift) should be first-class nodes, not footnotes — they explain why later projects changed direction.
- Several Sessionstream files are very long (the Pinocchio Structured Streams report exceeded the 50KB read limit); a second pass on the TUI turns-persistence design section would strengthen the persistence boundary node.
