# Code Context

## Files Retrieved
1. `ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/01-initial-scan-and-subagent-fanout-plan.md` (lines 1-92) - parent scope and this agent's topic slice.
2. `Projects/2026/03/16/PROJ - go-go-goja jsverbs - JavaScript to Glazed Commands.md` (lines 1-120) - first major jsverbs architecture report.
3. `Projects/2026/05/24/ARTICLE - xgoja - Generated Goja Applications Provider Architecture and Runtime Profiles.md` (lines 1-140) - xgoja generated-binary/provider architecture.
4. `Projects/2026/06/12/ARTICLE - Go Go Objects - Durable Objects Runtime on Goja.md` (lines 1-120) - durable object actor/runtime model.
5. `Projects/2026/06/22/ARTICLE - Designing DSLs with go-go-goja - Go-Backed JavaScript APIs.md` (lines 1-120) - latest DSL design synthesis.
6. `Projects/2026/06/13/ARTICLE - xgoja v2 RuntimePlan Hard Cutover - Technical Deep Dive.md` (lines 1-120) - RuntimePlan v2 cutover and source scoping.
7. `Projects/2026/06/16/PROJECT REPORT - xgoja Keycloak Auth Host - Production Deployment Deep Dive.md` (lines 1-100) - production auth host deployment.
8. `Projects/2026/06/09/ARTICLE - TypeScript Declarations from xgoja Generated Binaries.md` (lines 1-100) - generated `.d.ts` architecture.
9. `Projects/2026/06/10/ARTICLE - XGoja TypeScript Support - Esbuild, JSVerbs, and Hot Reload.md` (lines 1-100) - executable TypeScript support.
10. `Projects/2026/06/01/ARTICLE - Geppetto JS Bindings - Wrapper First Hard Cutover.md` (lines 1-100) - Geppetto wrapper-first bindings.
11. `Projects/2026/04/20/PROJ - JS Discord Bot - Building a Discord Bot with a JavaScript API.md` (lines 1-100) - early host-first JS API pattern.

## Scope and search method

Scope was Markdown reports under `Projects/2026/{03,04,05,06}/`. I used filename inventory plus targeted content search for `go-go-goja`, `xgoja`, `goja`, `jsverbs`, `Geppetto`, `durable objects`, `RuntimePlan`, `TypeScript`, `Go-backed`, `DSL`, and `auth host`. A broad grep produced 326 matching Markdown files, so I treated exact project titles and repeated high-signal hits as the primary corpus and sampled representative reports for architecture.

Important searches/commands:
- `find Projects/2026 -name '*.md'` for month inventory.
- `grep -RilE 'go-go-goja|xgoja|goja|jsverbs|Geppetto|geppetto|durable objects|TypeScript|Go-backed|DSL|RuntimePlan|auth host' Projects/2026/{03,04,05,06} --include='*.md'` found 326 topic-adjacent files.
- Targeted reads focused on canonical architecture reports rather than every incidental TypeScript/Geppetto mention.

## Projects and reports found

### Core go-go-goja / goja runtime evolution
- `Projects/2026/03/16/PROJ - go-go-goja jsverbs - JavaScript to Glazed Commands.md`
- `Projects/2026/03/18/PROJ - go-go-goja Plugins - Since origin main.md`
- `Projects/2026/04/03/PROJ - go-go-goja REPL API - Profiles, IIFE Rewriting, and AST-Driven Session Semantics.md`
- `Projects/2026/04/08/PROJ - Goja REPL Hardening.md`
- `Projects/2026/04/12/PROJ - Goja vs Sobek Deep Analysis.md`
- `Projects/2026/04/14/PROJ - Goja REPL Essay - Implementation Deep Dive.md`
- `Projects/2026/04/25/PROJ - go-go-goja Node-like Primitives - Technical Deep Dive.md`
- `Projects/2026/04/25/PROJ - Goja WASM Web REPL - A JavaScript Sandbox in the Browser.md`
- `Projects/2026/04/25/PROJ - WASM Plugin REPL - Goja wazero Deep Dive.md`
- `Projects/2026/04/25/RESEARCH - Go-Controlled Shell and Subprocess Sandboxing for JavaScript Runtimes.md`
- `Projects/2026/04/26/ARTICLE - Goja RuntimeHook Internals - Building Tracers, Debuggers, and TUI Visual Debuggers.md`
- `Projects/2026/04/26/ARTICLE - Report - Go Go Goja EventEmitter Implementation.md`
- `Projects/2026/04/26/ARTICLE - Report - Go Go Goja fswatch Implementation.md`
- `Projects/2026/04/27/PROJ - go-go-goja - YAML and Run Support.md`
- `Projects/2026/04/28/PROJ - RESEARCH PROPOSAL - Remote Capability Plugins for go-go-goja.md`
- `Projects/2026/05/15/ARTICLE - go-go-goja Context Management - Runtime Request and Async Call Context.md`
- `Projects/2026/05/23/ARTICLE - Goja Sandbox Architecture - Lessons from go-go-goja and vm-system.md`
- `Projects/2026/05/23/ARTICLE - go-go-goja Runtime System - Creation Context Scheduling and Modules.md`
- `Projects/2026/05/23/REVIEW - go-go-goja PR 38 - UIDSL attrs and per-call context propagation.md`
- `Projects/2026/05/26/ARTICLE - Runtime Context Ownership in go-go-goja.md`
- `Projects/2026/06/04/ARTICLE - go-go-goja - Runtime Architecture Cleanup and Geppetto Provider Integration.md`
- `Projects/2026/06/06/ARTICLE - Bump-Goja - A Go Ecosystem Migration Playbook.md`

### jsverbs and generated command surfaces
- `Projects/2026/03/16/PROJ - go-go-goja jsverbs - JavaScript to Glazed Commands.md`
- `Projects/2026/04/20/ARTICLE - Playbook - Adding jsverbs to Arbitrary Go Glazed Tools.md`
- `Projects/2026/04/21/PROJ - go-minitrace - JS Commands and Structured Query Catalog PR #6.md`
- `Projects/2026/04/22/GUIDE - Goja JS Verbs to CLI.md`
- `Projects/2026/05/22/ARTICLE - xgoja - Compile-Time Goja Module Composition and jsverbs Mounting.md`
- `Projects/2026/05/25/ARTICLE - xgoja Modules in Existing Runners - Discord Bot Case Study.md`
- `Projects/2026/06/03/ARTICLE - xgoja - Building a Query Tool with Jsverbs and Embedded Modules.md`
- `Projects/2026/06/04/ARTICLE - go-go-goja - HTTP Serve Support for xgoja Generated Verbs.md`

### xgoja generated binaries, providers, RuntimePlan, assets
- `Projects/2026/05/08/ARTICLE - Go Plugin Strategies - xgoja Compile-Time Module Composition.md`
- `Projects/2026/05/22/ARTICLE - xgoja - Compile-Time Goja Module Composition and jsverbs Mounting.md`
- `Projects/2026/05/24/ARTICLE - xgoja - Generated Goja Applications Provider Architecture and Runtime Profiles.md`
- `Projects/2026/05/24/PROJ - XGoja Provider Support - Third-Party Package Rollout.md`
- `Projects/2026/05/27/ARTICLE - Playbook - Building go-go-goja xgoja Provider Packages.md`
- `Projects/2026/05/31/ARTICLE - xgoja Provider-Shipped Glazed Help Documents.md`
- `Projects/2026/06/01/ARTICLE - XGOJA-016 - Embedded Assets in Generated xgoja Binaries.md`
- `Projects/2026/06/02/PROJ - xgoja Generated Binary Configuration.md`
- `Projects/2026/06/08/ARTICLE - xgoja - HTTP Serve, Hot Reload, and Runtime Service Architecture.md`
- `Projects/2026/06/12/ARTICLE - New XGoja - Source Graphs Provider Plans and the V2 Runtime Compiler.md`
- `Projects/2026/06/13/ARTICLE - xgoja v2 RuntimePlan Hard Cutover - Technical Deep Dive.md`
- `Projects/2026/06/14/ARTICLE - xgoja Sourcegraph Tree-sitter Import Resolution - Technical Deep Dive.md`

### TypeScript support and declarations
- `Projects/2026/06/09/ARTICLE - TypeScript Declarations from xgoja Generated Binaries.md`
- `Projects/2026/06/10/ARTICLE - XGoja TypeScript Support - Esbuild, JSVerbs, and Hot Reload.md`
- Adjacent but separate Pi/frontend TS: `Projects/2026/04/21/ARTICLE - Playbook - Building and Testing Pi Extensions.md`, `Projects/2026/04/21/PROJ - Pi Extension - Hello World Before Thinking Blocks.md`, many web UI reports.

### Go-backed JavaScript APIs and DSL patterns
- `Projects/2026/04/11/ARTICLE - Loupedeck - Goja JavaScript Runtime and API Deep Dive.md`
- `Projects/2026/04/20/PROJ - JS Discord Bot - Building a Discord Bot with a JavaScript API.md`
- `Projects/2026/04/20/PROJ - JS Discord Bot - Adding jsverbs Support.md`
- `Projects/2026/04/22/ARTICLE - Go-Side JavaScript DSLs for Discord Bots - Types, Errors, and In-Place Updates.md`
- `Projects/2026/04/21/PROJ - CSS Visual Diff - Hair Booking Fringe Restyle Tooling.md`
- `Projects/2026/04/21/PROJ - css-visual-diff - Script Runtime and JS DSL.md`
- `Projects/2026/04/24/ARTICLE - Textbook - CSS Visual Diff Flexible JavaScript API Implementation.md`
- `Projects/2026/04/25/ARTICLE - Textbook - CSS Visual Diff JavaScript API Design and Implementation Deep Dive.md`
- `Projects/2026/04/25/ARTICLE - Textbook - Design Principles and Proxy Patterns in the CSS Visual Diff JavaScript API.md`
- `Projects/2026/04/29/ARTICLE - CSS Visual Diff - Retiring the Native YAML Runner for a JavaScript First Workflow Engine.md`
- `Projects/2026/05/03/ARTICLE - Kanban DSL - Server Rendered Boards with Goja Callbacks.md`
- `Projects/2026/05/08/ARTICLE - db-browser - Goja JavaScript SQLite App Runtime Deep Dive.md`
- `Projects/2026/05/08/ARTICLE - Server-Interactive ui.dsl - Backend-Dispatched UI Events.md`
- `Projects/2026/05/13/PROJECT REPORT - Fringe Go Host Modules Walkthrough.md`
- `Projects/2026/05/13/PROJECT REPORT - Fringe Interactive DSL and Goja Backend Runtime Deep Dive.md`
- `Projects/2026/05/13/PROJECT REPORT - Fringe UI DSL Pattern Backend Frontend Walkthrough.md`
- `Projects/2026/05/15/PROJECT REPORT - Fringe Admin DSL and React Renderer Technique Deep Dive.md`
- `Projects/2026/05/16/PROJECT REPORT - Fringe Admin DSL Backend Driven Admin Interfaces Deep Dive.md`
- `Projects/2026/06/02/PROJ - Goja Text - Go-Backed Markdown AST Bindings.md`
- `Projects/2026/06/02/PROJ - Goja Text - Sanitizing and Extracting Structured Data from Messy Text.md`
- `Projects/2026/06/05/ARTICLE - Building a Goja UI DSL from Scratch - Widget IR to xgoja.md`
- `Projects/2026/06/07/ARTICLE - Fluent Builders with Go-Backed Objects for JavaScript.md`
- `Projects/2026/06/07/ARTICLE - Minitrace Viz API Redesign - Normalized SQL and Fluent Goja Builders.md`
- `Projects/2026/06/07/PROJ - goja-text - Template and HTML Rendering Module.md`
- `Projects/2026/06/22/ARTICLE - Designing DSLs with go-go-goja - Go-Backed JavaScript APIs.md`

### Geppetto bindings and agent/runtime integration
- `Projects/2026/03/16/PROJ - Scopedjs Runtime and Demo - Geppetto and Pinocchio.md`
- `Projects/2026/03/17/PROJ - Scopedjs Runtime - Geppetto Final State.md`
- `Projects/2026/03/18/PROJ - Geppetto - Opinionated JS APIs and Engine Profiles.md`
- `Projects/2026/03/28/PROJ - Geppetto - Open Responses and Chat Boundary Cutover.md`
- `Projects/2026/04/22/PROJ - Geppetto - OpenAI Responses Image Support.md`
- `Projects/2026/04/29/ARTICLE - Building a Tool-Using Go Chat Agent - Geppetto Goja and Glazed.md`
- `Projects/2026/06/01/ARTICLE - Geppetto JS Bindings - Wrapper First Hard Cutover.md`
- `Projects/2026/06/02/ARTICLE - Geppetto JS Overhaul - Wrapper First Agents Events and Storage Boundaries.md`
- `Projects/2026/06/02/ARTICLE - Geppetto JS Session API - From Turns to Sessions.md`
- `Projects/2026/06/04/ARTICLE - go-go-goja - Runtime Architecture Cleanup and Geppetto Provider Integration.md`

### Durable objects, HTTP composition, auth hosts
- `Projects/2026/06/12/ARTICLE - Go Go Objects - Durable Objects Runtime on Goja.md`
- `Projects/2026/06/14/ARTICLE - Go Go Objects - Async Behavior in Durable Objects.md`
- `Projects/2026/06/14/ARTICLE - Go Go Objects - Async Durable Objects Dispatch and xgoja v2 Integration.md`
- `Projects/2026/06/12/ARTICLE - Goja HTTP Composition - Mountable Handlers and Sessionstream WebSockets.md`
- `Projects/2026/06/12/ARTICLE - go-go-goja Express Auth - Go Backed Fluent Route Plans.md`
- `Projects/2026/06/14/ARTICLE - go-go-goja Express Auth - From Planned Routes to Generated Host Auth.md`
- `Projects/2026/06/16/PROJECT REPORT - xgoja Keycloak Auth Host - Production Deployment Deep Dive.md`
- `Projects/2026/06/20/ARTICLE - go-go-goja Planned Route Rate Limiting - Deep Dive.md`
- `Projects/2026/06/20/ARTICLE - go-go-goja Programmatic Auth After Rate Limiting - Deep Dive.md`
- `Projects/2026/06/20/PROJECT REPORT - go-go-goja Programmatic Agent Fetch Auth - End-to-End Deep Dive.md`
- `Projects/2026/06/21/PROJECT REPORT - go-go-goja Token Families and Device Authorization Flow - Deep Dive.md`

## Key Code

### jsverbs as JS-to-Glazed compiler pipeline

From `Projects/2026/03/16/PROJ - go-go-goja jsverbs - JavaScript to Glazed Commands.md` (lines 43-96):

```text
JS files / embed.FS / raw source strings
  -> pkg/jsverbs/scan.go
  -> Registry + VerbSpec + SectionSpec + diagnostics
  -> pkg/jsverbs/binding.go
  -> shared binding plan
  -> pkg/jsverbs/command.go
  -> Glazed command descriptions
  -> pkg/jsverbs/runtime.go
  -> Goja runtime + source overlay loader
  -> JS function execution
  -> structured rows or text output
```

Critical concepts: static sentinel metadata (`__package__`, `__section__`, `__verb__`), AST literal parsing instead of JS-to-JSON rewriting, shared binding plan to avoid parse/invoke drift, source-overlay loader preserving relative `require()`, promise polling as a known v1 tradeoff.

### xgoja compile-time composition and runtime profiles

From `Projects/2026/05/24/ARTICLE - xgoja - Generated Goja Applications Provider Architecture and Runtime Profiles.md` (lines 18-40, 98-137): xgoja reads `xgoja.yaml`, generates Go source, imports selected provider packages, embeds a normalized runtime specification, and compiles a normal Go binary. Provider packages are build-time imports; runtime profiles decide which compiled modules are visible to a command.

Conceptual edge: `xgoja.yaml packages` -> generated `main.go` imports providers -> binary contains modules; `runtimes.modules` + `commands.runtime` -> per-command capability boundary.

### RuntimePlan v2

From `Projects/2026/06/13/ARTICLE - xgoja v2 RuntimePlan Hard Cutover - Technical Deep Dive.md` (lines 18-35, 94-120): generated binaries now embed `app.RuntimePlan` JSON with schema `xgoja/runtime/v2`; old top-level keys are rejected in active runtime code; provider command sets receive command-scoped sources through `SourceRegistry`. The key repair was removing v2-to-legacy metadata conversion that lost `commands[].sources`.

### Durable Objects on Goja

From `Projects/2026/06/12/ARTICLE - Go Go Objects - Durable Objects Runtime on Goja.md` (lines 18-38, 47-84): a durable object is `(namespace, name)`, lazily started as one JavaScript actor, owns one `go-go-goja/pkg/engine.Runtime`, runs through `RuntimeOwner.Call()`, and has private SQLite storage. The HTTP gateway maps `/rpc/...` and `/fetch/...` to manager dispatch envelopes. This is a local single-process Durable Objects kernel, not Cloudflare compatibility.

### TypeScript support

From `Projects/2026/06/09/ARTICLE - TypeScript Declarations from xgoja Generated Binaries.md` (lines 25-57): `.d.ts` generation has three layers: module descriptors (`modules.TypeScriptDeclarer`), xgoja descriptor bundling (`pkg/xgoja/dtsgen`), and deterministic rendering (`pkg/tsgen/render`).

From `Projects/2026/06/10/ARTICLE - XGoja TypeScript Support - Esbuild, JSVerbs, and Hot Reload.md` (lines 17-44): executable TypeScript is a compilation layer around existing execution paths. `pkg/tsscript` wraps esbuild; jsverbs get scan-time and runtime transforms; HTTP hot reload extends the existing blue/green reload manager.

### Go-backed DSL design rule

From `Projects/2026/06/22/ARTICLE - Designing DSLs with go-go-goja - Go-Backed JavaScript APIs.md` (lines 14-57): JavaScript should usually own composition; Go should own domain state, validation, resources, lifecycle, and typed host boundary values. Fluent Go-owned wrapper/builder objects are preferred when intermediate state has invariants.

### Geppetto wrapper-first bindings

From `Projects/2026/06/01/ARTICLE - Geppetto JS Bindings - Wrapper First Hard Cutover.md` (lines 18-45, 57-90): Geppetto exposes Go-owned wrapper objects for inference settings, engines, agents, turns, schemas, tools, and registries. Profile registries resolve inference config; JavaScript does not build provider/model settings directly. Legacy permissive namespaces were removed.

## Architecture

The overall corpus shows a clear progression:

1. **Embedded runtime primitive**: goja plus CommonJS-style modules, runtime ownership, context scheduling, async/promise handling, node-like primitives.
2. **Command authoring layer**: jsverbs lets `.js` files define Glazed/Cobra commands with static metadata and Go-managed execution.
3. **Application generator**: xgoja turns runtime/module/provider choices into generated Go binaries; compile-time provider selection avoids dynamic Go plugin risks.
4. **RuntimePlan v2**: xgoja moves from legacy generated metadata to source graphs, command-scoped source registries, artifacts, and runtime-native command plans.
5. **Authoring ergonomics**: `.d.ts` export, executable TypeScript via esbuild, hot reload, provider-shipped help, embedded assets.
6. **Domain DSLs**: Discord bot APIs, CSS visual diff workflows, db-browser SQLite API, Fringe/UI DSL, goja-text Markdown/template builders, Widget IR, Minitrace query/viz builders.
7. **Stateful and hosted runtimes**: Durable Objects, HTTP composition, Express/auth route planners, Keycloak auth host, rate limiting, token families, programmatic agent fetch auth.
8. **Agent integration**: Geppetto/Pinocchio use Goja as a bounded scripting/tool surface while Go keeps profile, credential, session, and tool registry ownership.

The recurring dependency pattern is:

```text
Go host resources and invariants
  -> Go-backed module/provider wrappers
  -> go-go-goja runtime owner / factory
  -> xgoja runtime profile or command plan
  -> JS/TS authored composition code
  -> jsverbs / HTTP / DSL / agent-facing command surface
  -> structured Go/Glazed/HTTP/event outputs
```

## Clusters and subclusters

### Cluster A: Runtime kernel and lifecycle
Subclusters: `RuntimeOwner.Call()` serialization; request/async context propagation; per-call vs per-session runtime; REPL session semantics; RuntimeHook tracing; Goja vs Sobek evaluation; shell/subprocess sandboxing. Failure modes: unsafely shared runtime execution, lost async context, promise polling, unclear cancellation, runtime state leaking across commands.

### Cluster B: jsverbs and Glazed command generation
Subclusters: static JS metadata scanning; binding plan; source overlay require loader; text vs row output; mounted commands; help generation; jsverbs in minitrace/CSS diff/Discord/xgoja HTTP serve. Failure modes: schema/execution binding drift, metadata parser fragility, unsupported text output in some integrations, relative require regressions.

### Cluster C: xgoja build/runtime system
Subclusters: buildspec/planner; provider packages; runtime profiles; generated main/app package; embedded assets/help; source graphs; RuntimePlan v2; provider command sets; HTTP serve/hot reload; third-party provider rollout. Failure modes: legacy DTO losing v2 semantics, build-time vs runtime module confusion, source scoping bugs, provider package API churn.

### Cluster D: Go-backed DSL and host APIs
Subclusters: host-first Discord bot API; CSS visual diff JavaScript workflow engine; db-browser SQLite runtime; UI/Fringe DSL; goja-text Markdown/template builders; protobuf fluent builders; planned route/auth DSLs. Failure modes: letting JS own too much domain state, plain-object drift, type conversion losing structure, weak error taxonomy, insufficient fluent builder invariants.

### Cluster E: TypeScript developer experience
Subclusters: TypeScript declaration descriptors; generated binary `.d.ts` export; esbuild compilation facade; TS jsverbs; TS hot reload; IDE completions. Failure modes: declarations not matching selected runtime profile, scan-time vs runtime transform divergence, stale embedded/generated artifacts.

### Cluster F: Agent/Geppetto bindings
Subclusters: scopedjs tools; Geppetto wrapper-first API; profile-backed inference settings; agent/turn/tool wrappers; events/storage boundaries; Geppetto provider integration into go-go-goja/xgoja. Failure modes: permissive JS API bypassing credentials/profile boundaries, session/turn model drift, multimodal transport ambiguity.

### Cluster G: Hosted/stateful services
Subclusters: Durable Objects actor runtime; HTTP composition; WebSocket/sessionstream integration; Express/auth planned routes; Keycloak auth host; rate limiting; token/device authorization. Failure modes: deployment config/schema drift, source code vs GitOps manifest mismatch, persistent actor storage/eviction races, auth secret naming and redirect URI mismatch.

## Recurring concepts, technologies, and failure modes

Recurring technologies:
- Go, goja, `go-go-goja/pkg/engine`, `runtimeowner`, CommonJS `require`.
- Glazed/Cobra command surfaces and structured rows.
- xgoja generated binaries, provider packages, runtime profiles/plans.
- Tree-sitter/AST parsing for JS metadata and source graphs.
- esbuild for TypeScript lowering.
- SQLite for durable/runtime state and application data.
- Geppetto/Pinocchio for LLM/agent bindings.
- HTTP serving, hot reload, K3s/Argo CD/Vault/Keycloak for hosted auth examples.

Repeated design maxims:
- JavaScript owns composition; Go owns invariants, resources, lifecycle, and final typed values.
- Compile-time Go module composition is safer than dynamic native plugins for this ecosystem.
- Runtime profile selection is a capability boundary, not just a convenience.
- Command/source scoping must be explicit and survive build generation.
- Wrapper-first APIs are used when credentials, provider config, sessions, or typed domain state matter.
- Generated artifacts need validation to prevent source/generated/runtime drift.

Common failure modes:
- Schema drift between frontend/backend or buildspec/runtime DTOs.
- JS metadata extraction too permissive or not statically analyzable.
- Go structs crossing to JS as opaque single `value` columns unless converted to plain JSON-like values.
- Runtime sharing without serialization or clear per-session semantics.
- TypeScript declarations not connected to executable runtime support.
- Deployment failures caused by names/URLs/secrets/command args diverging across source, image, manifests, Vault, Keycloak, and Argo CD.

## Candidate concept-map nodes and edges

Nodes:
- `go-go-goja runtime kernel`
- `runtime owner serialization`
- `CommonJS module registry`
- `Go-backed module provider`
- `jsverbs scanner`
- `binding plan`
- `Glazed command surface`
- `xgoja buildspec`
- `xgoja provider package`
- `runtime profile`
- `RuntimePlan v2`
- `SourceRegistry / source graph`
- `embedded assets/help`
- `TypeScript descriptor`
- `pkg/tsscript/esbuild`
- `HTTP serve provider`
- `hot reload manager`
- `Durable Object manager`
- `actor-owned goja runtime`
- `SQLite object storage`
- `Geppetto wrapper API`
- `profile-backed inference settings`
- `Go-backed fluent builder DSL`
- `auth planned routes`
- `Keycloak auth host`

Edges:
- `jsverbs scanner` -> `binding plan`: produces shared invocation/schema binding.
- `binding plan` -> `Glazed command surface`: avoids parse/invoke drift.
- `xgoja buildspec` -> `provider package`: compiles native modules into binary.
- `runtime profile` -> `CommonJS module registry`: selects visible `require()` modules.
- `RuntimePlan v2` -> `SourceRegistry`: preserves command-scoped source declarations.
- `SourceRegistry` -> `HTTP serve provider`: limits hot-reloaded/jsverb HTTP routes to declared sources.
- `TypeScript descriptor` -> `.d.ts bundle`: IDE/static typing for selected modules.
- `pkg/tsscript/esbuild` -> `jsverbs scanner`: compiles TS before metadata scan.
- `pkg/tsscript/esbuild` -> `goja runtime`: lowers executable TS to JS.
- `Durable Object manager` -> `actor-owned goja runtime`: lazy identity-bound actor startup.
- `actor-owned goja runtime` -> `SQLite object storage`: durable per-object state.
- `Geppetto wrapper API` -> `profile-backed inference settings`: prevents JS from owning credentials/provider config.
- `Go-backed fluent builder DSL` -> `Go invariants`: Go stores state and validates transitions.
- `auth planned routes` -> `Keycloak auth host`: planned/generated auth becomes deployed OIDC host.
- `Keycloak auth host` -> `Infra/Auth slice`: shares K3s, Argo CD, Vault, Postgres, Keycloak concerns.

## Overlaps with other topic slices

- **Infra/auth/deployment/GitOps**: Keycloak auth host, Argo CD deployment, Vault secrets, K3s, GitOps drift, rate limiting and token families.
- **AI agents/transcripts/observability**: Geppetto bindings, scopedjs, go-minitrace JS commands, sessionstream, agent tool surfaces.
- **Data/RAG/search**: db-browser, Goja Bleve, RAG xgoja scripts, SQLite bindings, goja-text extraction.
- **Web UI/apps/productivity**: Fringe UI DSL, Widget IR, Kanban DSL, CSS Visual Diff, Loupedeck JS APIs, Pi extensions TypeScript surfaces.
- **Design systems/typography**: Widget IR/DMETA and UI DSL reports overlap with DSL patterns; CSS Visual Diff overlaps with design validation.
- **Hardware/embedded**: Loupedeck runtime and ESP32 browser-to-display examples touch JS APIs for devices, but not core goja runtime architecture.

## Open questions

1. Which reports should be considered canonical for each generation of xgoja: May 24 provider architecture, June 12 new xgoja plans, or June 13 RuntimePlan cutover?
2. Should concept maps distinguish `go-go-goja` the runtime library from `xgoja` the generator as separate top-level maps, or as layers in one map?
3. How should incidental TypeScript/frontend reports be filtered from TypeScript-as-xgoja-runtime support?
4. Which DSLs are production enough to map as exemplars: CSS Visual Diff, Fringe, goja-text, Durable Objects, auth routes, or Geppetto?
5. Does `go-go-objects` belong primarily to this slice, infra/runtime services, or agent/runtime systems?
6. Are `go-go-host` hosted runtimes part of the same family as xgoja auth hosts, or a distinct hosting/control-plane map?
7. How much of the implementation path lives outside `Projects/2026` in referenced workspaces and should be followed in later source-level review?

## Recommended report-format lessons

- Start with a **clustered inventory**, not a flat dump. The search hits are too numerous; exact project titles grouped by subsystem are more useful.
- Include **canonical line-cited snippets** only for architectural pivots: jsverbs pipeline, xgoja provider/profile split, RuntimePlan v2, durable actors, TypeScript layers, wrapper-first APIs.
- Separate **core runtime concepts** from **example applications**; many applications are proofs of the same pattern.
- Record **failure modes as first-class map nodes** because these reports repeatedly exist to explain drift, lifecycle bugs, or boundary corrections.
- Add an **overlap section** because this topic cuts across infra, agents, data, UI, and design-system slices.

## Start Here

Start with `Projects/2026/05/24/ARTICLE - xgoja - Generated Goja Applications Provider Architecture and Runtime Profiles.md`. It gives the clearest system-level explanation of xgoja as compile-time provider composition plus runtime profiles. Then read `Projects/2026/06/13/ARTICLE - xgoja v2 RuntimePlan Hard Cutover - Technical Deep Dive.md` for the current v2 runtime representation, and `Projects/2026/06/22/ARTICLE - Designing DSLs with go-go-goja - Go-Backed JavaScript APIs.md` for the cross-project DSL design synthesis.
