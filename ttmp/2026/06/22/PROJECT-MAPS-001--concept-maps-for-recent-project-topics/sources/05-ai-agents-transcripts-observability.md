# Code Context

## Files Retrieved
1. `ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/01-initial-scan-and-subagent-fanout-plan.md` (lines 1-111) - parent scope, corpus size, and Agent 5 slice.
2. `Projects/2026/04/01/PROJ - go-minitrace - Web UI and Transcript Explorer.md` (lines 1-120) - go-minitrace UI/product entry point and transcript/query architecture.
3. `Projects/2026/05/07/ARTICLE - Observer Instrumentation - Geppetto Pinocchio Sessionstream Deep Dive.md` (lines 1-140) - core observability architecture across provider, event pipeline, transport, browser, and SQLite evidence.
4. `Projects/2026/05/13/PROJECT REPORT - Pi Extensions Shared Framework and Tool Surface Deep Dive.md` (lines 1-140) - Pi extension registry, tool surface, dashboard/widgets, and external-tool delegation model.
5. `Projects/2026/06/22/ARTICLE - Analyzing Agent Tool-Calling Behavior with go-minitrace.md` (lines 1-140) - newest normalized transcript-analysis pipeline and tool-calling behavior analysis.
6. `Projects/2026` grep results for `Pi|go-minitrace|sessionstream|Pinocchio|Geppetto|transcript|LLM|provider|tool-calling|observability|compaction|agent readability|dashboard` - broad inventory of candidate reports.

## Scope and search method

Scope was Markdown project/report/article corpus under `Projects/2026/{03,04,05,06}/`, as defined by the parent plan. I used:

- `find Projects/2026 - pattern {03,04,05,06}/**/*.md` for date/file inventory.
- Broad grep across project reports for agent/transcript/observability terms.
- Refined grep for high-signal titles and recurring terms: `go-minitrace`, `Sessionstream`, `Pinocchio`, `Geppetto`, `Pi Extension`, `provider replay`, `agent-readable`, `LLM Proxy`, `Dashboard`, `Compaction`.
- Selective reads of one representative file per major cluster rather than reading every matching report.

This report emphasizes concept-map construction, not source-code modification.

## Projects/reports found with paths

### Transcript analysis and go-minitrace

- `Projects/2026/03/17/PROJ - Claude Code Hook Events Logger - SQLite Analytics for Claude Sessions.md` - early capture-first session telemetry; hook events, tool invocations, permission checks, compaction, lifecycle, transcript path into SQLite.
- `Projects/2026/03/17/PROJ - Claude Code Hook Analytics - Full-Stack Session Telemetry.md` - likely companion/full-stack view of Claude hook analytics.
- `Projects/2026/04/01/PROJ - go-minitrace - Web UI and Transcript Explorer.md` - session browser, transcript reader, DuckDB SQL workbench; implemented `go-minitrace serve` UI.
- `Projects/2026/04/04/PROJ - go-minitrace - Annotation System.md` - annotation layer for transcript analysis.
- `Projects/2026/04/10/PROJ - Minitrace Query Commands - Sqleton-Inspired SQL Verb System.md` - structured query commands before/around JS query catalog.
- `Projects/2026/04/14/PROJ - go-minitrace HTML Transcript Export - Reader Architecture.md` - portable single-session HTML export.
- `Projects/2026/04/14/ARTICLE - Self-Contained HTML Transcript Exports - Under the Hood in go-minitrace.md` - systems deep dive on self-contained transcript export.
- `Projects/2026/04/21/PROJ - go-minitrace - JS Commands and Structured Query Catalog PR #6.md` - major PR adding JS-backed analysis commands, query catalog architecture, framework metadata, adapter tests, nightly workflow.
- `Projects/2026/04/22/ARTICLE - Playbook - Efficient Past Transcript Analysis with go-minitrace.md` - operational playbook.
- `Projects/2026/04/22/ARTICLE - Textbook - Transcript Analysis with go-minitrace.md` - longer-form textbook.
- `Projects/2026/04/22/ARTICLE - Project Report - Tracing the Loupedeck Serial Bug with Transcript Analysis.md` - applied transcript analysis as debugging method.
- `Projects/2026/05/06/ARTICLE - Conversation Export Pipelines - Pinocchio CoinVault Timeline Turns and Minitrace.md` - export bridge among Pinocchio/CoinVault timelines and minitrace.
- `Projects/2026/05/08/ARTICLE - Transcript Mining - Using go-minitrace to Find and Fix Tool-Call Churn in Agent Sessions.md` - tool-call churn analysis.
- `Projects/2026/05/13/PROJECT REPORT - GPT-5 Cache Behavior - Prompt Cache Analysis with go-minitrace.md` - prompt-cache behavior study.
- `Projects/2026/06/07/ARTICLE - Playbook - Analyzing Coding-Agent Sessions with go-minitrace.md` - agent-session analysis playbook.
- `Projects/2026/06/07/ARTICLE - Transcript-Driven Design System Recovery with go-minitrace.md` - recovering design-system knowledge from transcripts using converted Pi sessions, DuckDB, git.
- `Projects/2026/06/07/ARTICLE - Minitrace API Redesign - From Prototype Complexity to Normalized SQL and Fluent Builders.md` - normalized SQLite and Goja fluent builder direction.
- `Projects/2026/06/07/ARTICLE - Minitrace Viz API Redesign - Normalized SQL and Fluent Goja Builders.md` - visualization API counterpart.
- `Projects/2026/06/08/ARTICLE - SQLite Authorizer and Query Safety - Deep Dive Technical Analysis.md` - query safety for minitrace SQLite exposure.
- `Projects/2026/06/10/ARTICLE - Minitrace Viz - CLI Session Models and Token Provenance.md` - session model/token provenance visualization.
- `Projects/2026/06/11/ARTICLE - Minitrace Viz Workshop System - Daily Engineering Deep Dive.md` - workshop/reporting system around visualization.
- `Projects/2026/06/22/ARTICLE - Analyzing Agent Tool-Calling Behavior with go-minitrace.md` - latest normalized transcript/tool-calling behavior pipeline.

### Sessionstream, Pinocchio, Geppetto agent flows

- `Projects/2026/03/16/PROJ - Scopedjs Runtime and Demo - Geppetto and Pinocchio.md` - early runtime/demo linkage.
- `Projects/2026/03/17/PROJ - CoinVault - RAG Web Chat for Gold Coin Inventory.md` - concrete Pinocchio/Geppetto web chat app with safe SQL tools, semantic projection widgets, WebSocket timeline.
- `Projects/2026/03/18/PROJ - Geppetto - Opinionated JS APIs and Engine Profiles.md` - Geppetto JS APIs and engine/profile model.
- `Projects/2026/03/28/PROJ - Geppetto - Open Responses and Chat Boundary Cutover.md` - response/chat boundary migration.
- `Projects/2026/04/14/PROJ - PinocchioRC - Declarative Config Plans and Cleanup.md` - declarative Pinocchio configuration/profile plans.
- `Projects/2026/04/22/PROJ - Geppetto - OpenAI Responses Image Support.md` - provider capability expansion.
- `Projects/2026/04/29/ARTICLE - Building a Tool-Using Go Chat Agent - Geppetto Goja and Glazed.md` - tool-using Go chat agent pattern.
- `Projects/2026/04/29/ARTICLE - From eval_js to Persistent Agent Runtime - Replsession Logging and Streaming Events.md` - persistent runtime/logging/event evolution.
- `Projects/2026/04/29/PROJ - Sessionstream - Replay Store Remediation and Systemlab UI Refinement.md` - replay store and UI remediation.
- `Projects/2026/05/04/ARTICLE - Sessionstream Chatapp CoinVault Cleanup - Protobuf Ordinals and Transcript Segments.md` - schema/order/transcript cleanup.
- `Projects/2026/05/06/ARTICLE - Protobuf Payload Contracts and Sessionstream Schema Vet.md` - protocol/schema validation.
- `Projects/2026/05/07/ARTICLE - Devctl Trace Profiles - Pinocchio and CoinVault.md` - trace profiles.
- `Projects/2026/05/07/ARTICLE - Instrumenting Sessionstream and Browser Streaming Debug Pipelines.md` - streaming debug pipelines.
- `Projects/2026/05/07/ARTICLE - Observer Instrumentation - Geppetto Pinocchio Sessionstream Deep Dive.md` - strongest architecture source for observability.
- `Projects/2026/05/08/ARTICLE - Canonical Chat Event Protocol - Provider Streams to Browser State.md` and `Projects/2026/05/09/ARTICLE - Canonical Chat Event Protocol - Provider Streams to Browser State.md` - provider-to-browser event protocol.
- `Projects/2026/05/12/PROJECT REPORT - Packaging and Embedding a Shared Help SPA - Glazed and Pinocchio.md` - shared help SPA packaging.
- `Projects/2026/05/13/ARTICLE - Building a Sessionstream CLI Chat Runner - CoinVault Pinocchio Chatapp Deep Dive.md` - CLI chat runner.
- `Projects/2026/05/20/ARTICLE - Pinocchio Structured Streams - Protobuf JSONL RPC and Chatapp TUI Migration.md` - structured stream/RPC migration.
- `Projects/2026/05/22/ARTICLE - Sessionstream Runtime Events in Scraper.md` - runtime events in scraper.
- `Projects/2026/05/29/ARTICLE - Chat Overlay API - Sessionstream Widget Runtime Deep Dive.md` - overlay/widget runtime.
- `Projects/2026/06/01/ARTICLE - Pinocchio Web Chat Cleanup - Engineering Playbook and Technical Report.md` - web chat cleanup.
- `Projects/2026/06/01/ARTICLE - Geppetto JS Bindings - Wrapper First Hard Cutover.md` - JS binding cutover.
- `Projects/2026/06/02/ARTICLE - CoinVault Web Chat - Event Projection Debug Exports and Thinking Persistence.md` - event projection debug exports and thinking persistence.
- `Projects/2026/06/02/ARTICLE - Geppetto JS Overhaul - Wrapper First Agents Events and Storage Boundaries.md` - wrapper-first agents/events/storage boundaries.
- `Projects/2026/06/02/ARTICLE - Geppetto JS Session API - From Turns to Sessions.md` - session API migration.
- `Projects/2026/06/14/ARTICLE - goja-sessionstream - Deep Dive into xgoja Sessionstream Integration.md` - xgoja/sessionstream integration.
- `Projects/2026/06/22/ARTICLE - CozoDB Editor Modernization - Sessionstream Hard Cutover.md` - sessionstream substrate applied outside chat.

### Pi core and extensions

- `Projects/2026/04/07/PROJ - pi Mono - Investigating LLM Thinking Content Truncation.md` - Pi core/provider thinking content truncation.
- `Projects/2026/04/21/ARTICLE - Playbook - Building and Testing Pi Extensions.md` - extension lifecycle, event system, UI API, debugging, failure modes.
- `Projects/2026/04/21/PROJ - Pi Extension - Hello World Before Thinking Blocks.md` - first extension authoring/stream seam reference.
- `Projects/2026/04/23/PROJ - Pi Extension - A Textbook on Writing and Testing Pi Extensions.md` - textbook-style extension guide.
- `Projects/2026/04/25/PROJ - Pi Session Summary Extension - Textbook Report.md` - session summary extension.
- `Projects/2026/04/26/PROJ - Pi Extensions - Agent Env and Response Capture.md` - agent environment and response capture.
- `Projects/2026/04/27/ARTICLE - Textbook - Building Beautiful TUIs for Pi Extensions.md` - TUI extension design.
- `Projects/2026/04/27/PROJ - Pi Extensions - Compaction Title Extension.md` - compaction-title extension.
- `Projects/2026/04/27/PROJ - Pi Extensions - Direnv Bash Extension.md` - shell/env extension.
- `Projects/2026/05/05/ARTICLE - Pi Scoped Models Configuration.md` - model configuration.
- `Projects/2026/05/05/PROJ - Configuring Wafer Models in Pi.md` - model/provider configuration.
- `Projects/2026/05/11/ARTICLE - Selective Compaction Extension - Rewriting Middle Session Context.md` - compaction/search-related extension.
- `Projects/2026/05/13/PROJECT REPORT - Pi Extensions Shared Framework and Tool Surface Deep Dive.md` - extension registry and shared framework.
- `Projects/2026/05/14/ARTICLE - Pi Agent Dashboard - RPC Streaming Presets and Protobuf Deep Dive.md` - dashboard, RPC streaming presets, protobuf.
- `Projects/2026/05/15/ARTICLE - Pi Claw Runtime Packaging - Scenario Driven LLM Extraction and Auditable Agent Runs.md` - auditable extraction/agent runs.
- `Projects/2026/05/19/ARTICLE - Building a Session Search Extension for Pi - Searching Tool Call History and Navigating Fork Points.md` - session-search extension.
- `Projects/2026/05/21/ARTICLE - Response Viewer - A Pi Extension for Browsing and Opening Assistant Responses in a Markdown Viewer.md` - response viewer.
- `Projects/2026/05/27/ARTICLE - Pi Command Palette - Keyboard-Driven Hierarchical Action Menu.md` - command palette.
- `Projects/2026/05/28/ARTICLE - Pi Agent Command Palette Extension Architecture - Shared Registry and Keyboard-Driven Actions.md` - command palette architecture over registry.
- `Projects/2026/05/28/ARTICLE - Pi Agent Modals and Terminal Shortcuts - Debugging Overlay Shortcut Behavior.md` - shortcut/modal debugging.
- `Projects/2026/05/29/ARTICLE - Playbook - Debugging and Fixing Pi Provider Replay Bugs.md` - provider replay failure mode.
- `Projects/2026/05/29/PROJ - Pi Core - Umans GLM DeepSeek Reasoning Fix Report.md` - core reasoning fix.
- `Projects/2026/05/29/PROJ - Pi Extensions - Response Viewer Metadata Report.md` - response-viewer metadata.
- `Projects/2026/05/29/PROJ - Pi Extensions - Umans GLM Compaction Fix Report.md` - compaction fix.
- `Projects/2026/06/04/PROJ - pi-launcher - Declarative YAML Profiles for Pi.md` - reviewable launch profile compiler for Pi.

### LLM proxy/provider work and tool-calling behavior

- `Projects/2026/04/07/ARTICLE - Investigating LLM Thinking Content in Tool-Rich Coding Agent Contexts.md` - thinking content in tool-rich contexts.
- `Projects/2026/04/17/ARTICLE - Dialectic Agent - Implementing Tool-Calling Reasoning for AI Memory Systems.md` - tool-calling reasoning/memory.
- `Projects/2026/04/17/ARTICLE - Hermes Agent - Self-Improving AI Agent with Persistent Memory and Skills.md` - persistent memory/skills.
- `Projects/2026/04/17/ARTICLE - Browser-Owned Capability Execution for Chat - Narrative Field Guide.md` - browser-owned capability execution.
- `Projects/2026/04/17/ARTICLE - Playbook - Building a Sandboxed Agent Runner with Go Glazed and Firecracker.md` - sandboxed agent runner.
- `Projects/2026/04/17/PROJ - Client-side Tool Broker for Chat - Intern Research Guide.md` - client-side tool broker.
- `Projects/2026/04/29/ARTICLE - Building a Tool-Using Go Chat Agent - Geppetto Goja and Glazed.md` - Go agent tool calls.
- `Projects/2026/05/08/ARTICLE - Transcript Mining - Using go-minitrace to Find and Fix Tool-Call Churn in Agent Sessions.md` - behavioral failure mode.
- `Projects/2026/05/29/ARTICLE - Chatbot Overlay Framework - TypeScript and Frontend Tool Calling Deep Dive.md` - frontend tool calling.
- `Projects/2026/05/29/ARTICLE - Playbook - Debugging and Fixing Pi Provider Replay Bugs.md` - provider replay.
- `Projects/2026/05/31/ARTICLE - ChatProvider Web Chat Cleanup - Provider Runtime Timeline Adapters and Example Architecture.md` - provider runtime adapters.
- `Projects/2026/06/01/ARTICLE - Generic ChatProvider - From Overlay Runtime to Provider Backed Web Chat.md` - generic provider-backed chat.
- `Projects/2026/06/04/ARTICLE - LLM Proxy - Chat Completions Tools and Pinocchio Smoke Technical Report.md` - LLM proxy tools and smoke testing.
- `Projects/2026/06/04/ARTICLE - LLM Proxy - Geppetto Engine OpenAI Completions Prototype Deep Dive.md` - Geppetto engine OpenAI completions prototype.
- `Projects/2026/06/05/ARTICLE - Geppetto Gemini SDK Modernization - Gemini 3 Flash Deep Dive.md` - Gemini provider modernization.
- `Projects/2026/06/22/ARTICLE - Analyzing Agent Tool-Calling Behavior with go-minitrace.md` - concrete cross-model tool-call analysis.

### Dashboards, observability, readability/a14y

- `Projects/2026/04/07/ARTICLE - Playbook - Building Prometheus and Grafana into a Go Application from Scraper.md` - app observability stack.
- `Projects/2026/04/15/ARTICLE - Screencast Studio - Prometheus Metrics Architecture and Field Guide.md` - metrics architecture.
- `Projects/2026/04/23/ARTICLE - Go Logging Landscape - Zerolog, Slog, and Per-Component Control.md` - logging patterns.
- `Projects/2026/04/25/ARTICLE - Observability - Hetzner K3s Metrics Logging and Alerting.md` - infrastructure observability; overlaps Agent 4.
- `Projects/2026/05/12/ARTICLE - Streaming Agent Dashboard - Server Side Implementation Deep Dive.md` - dashboard server side.
- `Projects/2026/05/14/ARTICLE - Pi Agent Dashboard - RPC Streaming Presets and Protobuf Deep Dive.md` - Pi dashboard.
- `Projects/2026/05/19/ARTICLE - Presentation-Based UI for Log Viewing.md` - log-view UI model.
- `Projects/2026/05/25/ARTICLE - Agent a14y for Go-Hosted React Docs - Converting docsctl from SPA Shell to Agent-Readable Site.md` - explicit agent readability/a14y.
- `Projects/2026/06/06/PROJ - Retro Obsidian Publish - A Retro Monochrome Vault Browser.md` - agent-readable site with markdown mirrors/a14y score.

## Key Code / critical excerpts

### go-minitrace UI identity

`Projects/2026/04/01/PROJ - go-minitrace - Web UI and Transcript Explorer.md` lines 23-31 define the product:

> The web UI currently has three closely related identities: a session browser, a transcript reader, and a file-backed SQL workbench.

Lines 44-53 show current implementation: `go-minitrace serve`, embedded React SPA, session browser, transcript viewer with block decomposition/tool-call expansion, CodeMirror query editor, preset/saved query libraries.

### Sessionstream/Geppetto/Pinocchio observability ownership

`Projects/2026/05/07/ARTICLE - Observer Instrumentation - Geppetto Pinocchio Sessionstream Deep Dive.md` lines 25-34 summarize the ownership model:

- Sessionstream emits neutral Hub pipeline and WebSocket transport observations.
- Geppetto emits neutral provider and publish-boundary observations.
- Pinocchio owns recorder, debug HTTP endpoints, browser stream recorder, SQLite export.
- Provider-to-browser traceability is the invariant.

Lines 57-64 make the core principle explicit: reusable packages emit neutral records; the application decides what to store, expose, and export.

### Pi extension registry

`Projects/2026/05/13/PROJECT REPORT - Pi Extensions Shared Framework and Tool Surface Deep Dive.md` lines 26-34 summarize the design:

- `registerPiExtension()` registers metadata, actions, docs, settings, widgets, commands, and tools.
- Extensions stay thin at boundaries by delegating to external programs (`pinocchio`, `surf`, `md-view`).
- Correctness depends on precise sources of truth: explicit tool parameters, Pi session history, tmux smoke tests.

Lines 65-85 show the canonical registration shape, including `actions`, `docs`, `settings`, `widgets`.

### Latest tool-call analysis pipeline

`Projects/2026/06/22/ARTICLE - Analyzing Agent Tool-Calling Behavior with go-minitrace.md` lines 27-34 summarize the pipeline:

- `go-minitrace convert` canonicalizes native agent transcripts.
- `mt.db()` materializes normalized relational tables: `sessions`, `turns`, `tool_calls`, `files`, `events`, `metrics`.
- Analysis lives as structured JS query commands, not ad-hoc SQL.
- Report layer is self-contained HTML.

Lines 54-64 diagram the flow: Pi JSONL -> `.minitrace.json` -> normalized SQLite -> JS query repository -> self-contained HTML report.

## Clusters and subclusters

### 1. Capture-first transcript telemetry

Early March reports start with hook/event capture and SQLite analytics. The concept is to preserve all agent/session events before deciding which aggregations matter. Later go-minitrace work generalizes this into canonical archives, query catalogs, normalized SQLite, self-contained exports, and visual reports.

Subclusters:
- Claude Code hook events and SQLite logger.
- go-minitrace conversion/adapters.
- query commands and JS repository.
- HTML export and reader UI.
- normalized SQLite/authorizer/query safety.
- transcript mining as debugging method.

### 2. Provider-to-browser streaming observability

Sessionstream/Geppetto/Pinocchio reports center on the path from provider stream chunks to browser-rendered state. The recurring model is a layered evidence chain: provider engine -> chat plugin -> event hub -> transport -> browser parser -> Redux/timeline -> SQLite debug export.

Subclusters:
- provider/event observability in Geppetto.
- Sessionstream Hub pipeline and WebSocket transport records.
- Pinocchio app-owned recorder/debug API/SQLite export.
- canonical chat event protocol.
- protobuf schema and ordinal contracts.
- structured streams / JSONL RPC / TUI migration.

### 3. Pi as extensible local coding-agent surface

Pi reports form a separate but overlapping arc: authoring extensions, event seams, TUI widgets, registry/dashboards, compaction/search/response browsing, provider replay fixes, and launcher profiles.

Subclusters:
- extension authoring and testing.
- shared registry and `/px`/dashboard discovery.
- TUI overlays/widgets/modals/shortcuts.
- LLM-callable tools that delegate to external programs.
- compaction/session-search/response-viewer extensions.
- model/provider configuration and replay bugs.
- launch profile compiler (`pi-launcher`).

### 4. Tool-calling and provider/runtime behavior

This is the behavioral-analysis layer on top of transcripts and provider adapters: how agents batch, retry, churn, overuse tools, preserve thinking content, replay provider state, and expose frontend/browser tool calls.

Subclusters:
- tool-using Go chat agents.
- browser/client-side tool brokers.
- frontend tool-calling overlays.
- LLM proxy and provider engines.
- Gemini/OpenAI/Responses/Chat Completions providers.
- tool-call churn, transition matrices, retry loops, timing analysis.

### 5. Dashboards, debug UX, and agent readability

Dashboards and readability surfaces appear as a cross-cutting product concern: make runtime state browsable by humans and agents. This includes Pi Agent Dashboard, Streaming Agent Dashboard, minitrace web UI, presentation-based log viewing, agent-readable docs/sites, and self-contained transcript reports.

Subclusters:
- streaming dashboards.
- SQL/transcript browsers.
- log viewers and presentation-based UI.
- self-contained HTML reports.
- agent-readable SSR/static mirrors and markdown fallbacks.

## Recurring concepts and technologies

- Canonical event/transcript formats: minitrace archive, Sessionstream UI events, protobuf payloads, JSONL RPC.
- Normalized relational analysis: SQLite/DuckDB, `sessions`, `turns`, `tool_calls`, metrics tables, query catalogs.
- Go + React SPAs embedded in Go binaries: minitrace UI, dashboards, docs/help surfaces.
- Goja/xgoja as analysis/runtime extension substrate: JS query commands, fluent builders, generated providers.
- Provider-neutral interfaces: Geppetto provider records, ChatProvider adapters, LLM proxy OpenAI-compatible fronts.
- App-owned observability: reusable libraries emit neutral records; app owns recorder, debug APIs, exports.
- Self-contained artifacts: single HTML exports, static/readable mirrors, portable reports.
- Tool delegation: Pi extensions expose tools but delegate to `pinocchio`, `surf`, `md-view`, etc.
- Typed registries: Pi extension registry, command catalogs, profile configs, schema/payload contracts.

## Recurring failure modes

- Thinking/reasoning content truncation or duplication in tool-rich contexts.
- Provider replay bugs: timeline/adapters cannot faithfully replay provider states.
- Tool-call churn: repeated unproductive loops, retries, excessive reads/shell calls.
- Fragile JSON/DuckDB unnesting and adapter-specific query errors; migration toward normalized SQLite.
- Missing provider identity or stream item IDs breaks correlation.
- Sessionstream projection/fanout/transport failures appear as browser symptoms much later.
- Schema drift: protobuf ordinals, event payload contracts, generated routes/providers.
- UI/debug gaps: raw event streams are too verbose; require readers, block decomposition, and dashboards.
- Extension boundary mistakes: runtime imports where type-only imports are required; unclear source of truth; hard-to-test TUI behavior.
- Query safety issues: regex table extraction misses quoted identifiers/CTEs/system tables; authorizer recommended.

## Candidate concept-map nodes

- AI agent session
- native transcript JSONL
- canonical minitrace archive
- normalized transcript database
- tool call
- operation type
- timing / retry / transition analysis
- JS query repository
- self-contained HTML report
- go-minitrace web UI
- transcript reader
- query catalog
- Sessionstream Hub
- pipeline observer
- WebSocket transport observer
- Geppetto provider engine
- provider observability record
- Pinocchio recorder/debug API
- browser stream recorder
- SQLite reconcile export
- canonical chat event protocol
- protobuf payload contract
- Pi extension
- Pi shared registry
- Pi dashboard widget
- Pi tool surface
- compaction extension
- session search extension
- response viewer extension
- provider replay bug
- LLM proxy
- ChatProvider adapter
- tool-call churn
- agent readability / a14y
- portable review artifact

## Candidate concept-map edges

- Native transcript JSONL -> converted by -> `go-minitrace convert`.
- `go-minitrace convert` -> emits -> canonical minitrace archive.
- Minitrace archive -> materialized by -> `mt.db()` normalized SQLite.
- Normalized SQLite -> queried by -> JS query repository.
- JS query repository -> renders -> self-contained HTML report.
- Tool-call rows -> analyzed for -> frequency / transitions / retry loops / churn.
- Provider stream -> decoded by -> Geppetto provider engine.
- Geppetto -> emits -> provider observability records.
- Chat plugin -> publishes -> Sessionstream UI events.
- Sessionstream Hub -> emits -> pipeline records.
- WebSocket transport -> emits -> transport records.
- Browser parser -> records -> stream debug entries.
- Pinocchio -> joins -> provider, pipeline, transport, browser, timeline evidence.
- Pi extension -> registers via -> shared registry.
- Shared registry -> feeds -> launcher / dashboard / docs / settings / widgets.
- Pi LLM-callable tool -> delegates to -> external CLI/service.
- Compaction/session-search/response-viewer extensions -> improve -> local agent operator workflow.
- Agent-readable site -> improves -> coding-agent documentation consumption.
- LLM proxy -> adapts -> provider APIs to OpenAI-compatible/Geppetto engines.
- Query safety authorizer -> protects -> transcript analysis database.

## Architecture

The topic slice has two intertwined architectures.

First, the transcript-analysis architecture: native agent sessions are captured or discovered, converted to a canonical minitrace archive, loaded into either DuckDB or normalized SQLite, queried through SQL/JS command catalogs, and presented as web UI, diagrams, or self-contained HTML. This architecture is about retrospective evidence: understanding what an agent did, why it churned, which tools it used, and what artifacts it produced.

Second, the live streaming-agent architecture: providers emit streaming chunks; Geppetto normalizes provider events; Pinocchio chat plugins publish typed events; Sessionstream projects and transports those events; the browser mutates timeline state; Pinocchio records cross-layer evidence for reconciliation. This architecture is about online observability and correctness: prove where a missing/duplicated/stale UI event originated.

Pi extensions sit adjacent to both. They expose local agent affordances (tools, dashboards, command palettes, compaction, search, response viewers) and increasingly use typed registries, TUI surfaces, and delegated CLIs. Pi core/provider work supplies the failure cases that transcript analysis and observability then diagnose.

## Overlaps with other topic slices

- Agent 2 JavaScript/Goja/xgoja: go-minitrace JS query commands, fluent builders, Geppetto JS bindings, xgoja/sessionstream integration, go-go-goja provider integration.
- Agent 4 infra/auth/deployment: dashboards, Prometheus/Grafana, Keycloak/GitOps deployments, LLM proxy hosting, go-go-host auth/token families.
- Agent 6 data/RAG/OCR/search: CoinVault RAG, RAG eval transcripts, search extensions, Readwise/Bleve, transcript-driven design-system recovery.
- Agent 7 web UI/apps: minitrace web UI, Sessionstream overlays, Pi dashboards, ChatProvider web chat, React/Redux timelines, self-contained report UIs.
- Agent 1 hardware: applied transcript analysis to Loupedeck serial bug and hardware-debug sessions.
- Agent 3 design systems: transcript-driven design-system recovery and agent-readable docs/a14y.

## Start Here

Start with `Projects/2026/05/07/ARTICLE - Observer Instrumentation - Geppetto Pinocchio Sessionstream Deep Dive.md` for the live-agent observability architecture. Then read `Projects/2026/06/22/ARTICLE - Analyzing Agent Tool-Calling Behavior with go-minitrace.md` for the retrospective transcript-analysis architecture. These two files define the main north-south data flows.

## Open questions

- Is `go-minitrace` now standardizing on normalized SQLite over DuckDB for all serious transcript analysis, or is DuckDB still first-class for archive-scale/batch queries?
- Which Pi extension registry APIs are considered stable enough for future concept-map nodes: `actions`, `docs`, `widgets`, `tools`, `settings`, or all of them?
- Should Sessionstream observability records and minitrace archives converge into a common event schema, or remain separate live-vs-retrospective systems?
- Which provider bugs were fixed permanently versus documented as known failure modes: reasoning truncation, replay bugs, missing stream item IDs, thinking persistence?
- Are self-contained HTML reports meant as long-term archival artifacts, review handoffs, or temporary debugging outputs?
- How should “agent readability” be measured consistently across docsctl, Retro Obsidian Publish, Pi extension docs, and generated help sites?

## Recommended report-format lessons

- For this slice, a useful report format should separate **live streaming observability** from **retrospective transcript analysis**; otherwise Sessionstream and go-minitrace blur together.
- Include both `projects found` and `concept-map nodes/edges`: the corpus is dense, and path inventories alone do not reveal the architecture.
- Prefer one or two exact “start here” files; there are too many adjacent reports to read linearly.
- Record failure modes explicitly. They are the strongest edges between otherwise separate systems.
- For broad sweeps, cite representative line ranges plus path inventories; exhaustive per-file line extraction would be slower than useful for first-batch mapping.
