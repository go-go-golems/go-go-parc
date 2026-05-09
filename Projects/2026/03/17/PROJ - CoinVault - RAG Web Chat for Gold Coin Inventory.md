---
title: CoinVault
aliases:
  - CoinVault
  - CoinVault RAG
  - gec-rag
  - GEC RAG Web Chat
tags:
  - project
  - gec
  - rag
  - webchat
  - go
  - react
  - pinocchio
  - geppetto
  - sql
status: active
type: project
created: 2026-03-16
repo: /home/manuel/code/gec/2026-03-16--gec-rag
---

# CoinVault

CoinVault is a full-stack RAG-powered web chat application for a gold coin shop. It lets an operator ask natural-language questions about inventory, pricing, and stock levels and get answers grounded in real MySQL data through safe, validated SQL queries. The backend is Go (Pinocchio/Geppetto), the frontend is React with Redux, and the two communicate over WebSocket with a semantic event model that projects assistant responses into rich widgets.

> [!summary]
> The project has four important layers:
> 1. a Go backend built on Pinocchio's webchat runtime with configurable chat loops, tool catalogs, and profile-based personas
> 2. a React/Redux/Vite frontend with real-time WebSocket chat, a widget projection pipeline, and a retro System 7 aesthetic
> 3. a safe SQL tooling layer (MySQL via PingCAP parser, PostgreSQL via pg_query_go) that validates, normalizes, and clamps all queries before execution
> 4. a projection system that parses structured `<gec:TYPE:v1>` markup from assistant responses and renders them as inventory cards, tables, KPI rows, and stock alerts
>
> If you are new to this code: the main idea is "give an AI assistant read-only access to a shop's inventory database through parser-validated SQL, and project its answers into purpose-built widgets instead of raw text."

## Why this project exists

The gold coin shop (GEC) has a MySQL inventory database with products, pricing, quantities, and stock status. The shop operator needs to query this data conversationally --- asking things like "what's our total gold inventory value?" or "which items are low stock?" --- without writing SQL or using a traditional dashboard.

CoinVault exists to make that interaction safe, fast, and visually rich. The safety constraint is critical: the assistant has SQL access to production data, so every query must be parser-validated as read-only before execution. The visual richness matters because raw text answers about inventory are harder to act on than formatted cards and tables.

The project also serves as a concrete adoption proof for the go-go-golems stack. It exercises Pinocchio's webchat runtime, Geppetto's inference tools, Clay's SQL integration, and Glazed's CLI framework in a real application rather than a demo. Several architectural patterns discovered here --- projection blocks, tool catalogs, configurable loop runners --- are candidates for upstreaming.

## Current project status

The project completed 20 implementation tickets (COINVAULT-001 through COINVAULT-020) across an intensive 22-hour build session on 2026-03-16 and 2026-03-17. The codebase is functional end-to-end.

What already exists:

- a Go CLI (`coinvault serve`) that starts the backend with MySQL connection probing
- live `/chat`, `/ws`, `/api/timeline`, `/api/stats`, `/api/profiles` endpoints
- a React SPA with WebSocket-driven chat, conversation timeline, profile selectors, and widget rendering
- safe MySQL tooling with PingCAP TiDB parser validation (SELECT-only, LIMIT clamping, timeout enforcement)
- safe PostgreSQL tooling with pg_query_go/v6 (parallel implementation, same safety contract)
- a shared `safesqlcore` execution package extracted from both SQL implementations
- a projection block system that parses `<gec:inventory_cards:v1>`, `<gec:inventory_table:v1>`, `<gec:sql_table:v1>`, `<gec:stats_row:v1>`, `<gec:stock_alert:v1>` from assistant text
- widget renderers for each projection type (CoinCard, InventoryTable, StatsRow, StockAlert)
- application profiles (`default` for general assistant, `analyst` for SQL-capable assistant)
- a configurable loop runner decomposed into lifecycle, preparation, and execution phases
- a run registry with cancellation support (POST `/chat/{id}/cancel`)
- conversation URL rehydration (refresh-safe, shareable conversation URLs)
- turn and timeline persistence to SQLite
- Storybook stories for all widget components
- 20 docmgr ticket workspaces with diaries, design docs, changelogs, and playbooks

What is still incomplete or rough:

- PostgreSQL tooling is implemented but not wired to a live database (MySQL is the production target)
- tool policy enforcement (`tool-policy.yaml`) is scaffolded but not yet active
- the frontend has some copied scaffolding that could be extracted
- no authentication or multi-user support
- no automated test suite for the frontend

## Project shape

### 1. Backend chat runtime

The heart of the backend is the configurable loop runner in `internal/webchat/`. It orchestrates a Pinocchio/Geppetto tool-calling loop: the model generates responses or tool calls, tools execute (calculator, inventory summary, product search, SQL query, schema introspection), results feed back into the loop up to a configurable iteration limit. The runner is decomposed into four files:

- `configurable_loop_runner.go` --- coordinator and public API
- `configurable_loop_runner_prepare.go` --- session setup, history loading, runtime composition
- `configurable_loop_runner_execute.go` --- execution start and tool loop
- `configurable_loop_runner_lifecycle.go` --- run lifecycle (start, stop, completion)

Server initialization follows a dependency-injection pattern in `server_bootstrap.go` with explicit build phases: database deps, chat infrastructure deps, runtime deps, handler mounting.

### 2. Safe SQL tooling

The SQL layer is the most carefully designed safety boundary in the project. Both `internal/sqltool/` (MySQL) and `internal/pgsqltool/` (PostgreSQL) follow the same contract:

1. parse the query into an AST (PingCAP parser or pg_query_go)
2. validate: reject anything that is not a SELECT (no INSERT, UPDATE, DELETE, DROP, etc.)
3. normalize: enforce LIMIT clamping, strip comments, canonicalize whitespace
4. execute: run with timeout and row-count constraints via `internal/safesqlcore/`

The MySQL implementation is the production path. The PostgreSQL implementation was built in parallel as a proof that the pattern generalizes.

### 3. Projection system

The projection system bridges unstructured assistant text and structured UI widgets. It has three layers:

- `internal/projectionblocks/` --- parses `<gec:TYPE:v1>` markup blocks from streaming assistant text into typed block structs
- `internal/projectionsem/` --- wraps Geppetto's event sink to extract projection blocks as semantic events
- `internal/projectionlookup/` --- resolves block data against the database (e.g., hydrating product IDs into full product records) and renders widget payloads

On the frontend, `web/src/components/widgets/WidgetRenderer.tsx` dispatches each widget type to its renderer component.

### 4. Frontend

The React frontend uses Redux Toolkit for state management and Vite for builds. Key subsystems:

- WebSocket manager for real-time chat streaming
- Timeline store that accumulates semantic events into a browsable conversation
- Widget renderers for each projection type (cards, tables, stats, alerts)
- Profile selectors for switching between application personas and inference models
- Conversation URL management for refresh-safe, shareable sessions
- A retro System 7 Finder aesthetic in the conversation browser

## Architecture

```text
Browser (React/Redux/Vite)
  -> WebSocket /ws
  -> POST /chat (start conversation turn)
  -> POST /chat/{id}/cancel (cancel active run)
  -> GET /api/timeline (conversation history)
  -> GET /api/stats (quick inventory stats)
  -> GET /api/profiles (available profiles)

Go Backend (Pinocchio webchat runtime)
  -> ConfigurableLoopRunner
  -> Geppetto inference (Claude API)
  -> Tool catalog:
     - calc (arithmetic)
     - inventory_summary (canned queries)
     - search_products (product search)
     - sql_schema (table/column introspection)
     - sql_query (validated SELECT execution)
  -> Projection runtime:
     - parse <gec:TYPE:v1> blocks from assistant text
     - hydrate against MySQL
     - emit widget payloads via Watermill/Redis Stream
  -> Turn/timeline persistence (SQLite)

MySQL 5.7 (shop inventory)
  -> products, pricing, stock levels
  -> read-only access via safe SQL tools
```

Key code locations:

- `cmd/coinvault/main.go` --- CLI entry point
- `cmd/coinvault/cmds/serve.go` --- serve command with Clay SQL flags
- `internal/webchat/server.go` --- server initialization
- `internal/webchat/server_bootstrap.go` --- dependency injection phases
- `internal/webchat/configurable_loop_runner.go` --- chat loop coordinator
- `internal/webchat/tools.go` --- tool definitions (calc, inventory, search)
- `internal/webchat/tool_catalog.go` --- tool registration
- `internal/webchat/run_registry.go` --- active run tracking and cancellation
- `internal/sqltool/` --- MySQL safe tooling (validate, normalize, execute, schema)
- `internal/pgsqltool/` --- PostgreSQL safe tooling
- `internal/safesqlcore/` --- shared SQL execution core
- `internal/projectionblocks/` --- markup parser
- `internal/projectionsem/` --- semantic event extraction
- `internal/projectionlookup/` --- widget data hydration
- `internal/config/` --- server configuration
- `internal/stats/` --- quick inventory stats API
- `web/src/app/CoinVaultApp.tsx` --- main frontend component
- `web/src/components/widgets/` --- widget renderers
- `web/src/store/` --- Redux state management
- `web/src/ws/` --- WebSocket client

## Development timeline

The entire codebase was built in a single intensive session (~22 hours, 112 commits).

**Phase 1 --- Foundation (COINVAULT-001 through 005):**
Prototype modularization, backend CLI scaffolding, Pinocchio webchat runtime integration, React/Redux decomposition, live frontend-backend WebSocket integration.

**Phase 2 --- Safe SQL and Projections (COINVAULT-006 through 009):**
MySQL parser-validated tooling, PostgreSQL parallel implementation, SEM timeline entity projections, inventory widgets, markdown rendering, retro UI styling.

**Phase 3 --- Profiles and Frontend Pipeline (COINVAULT-010 through 013):**
Decoupled application/inference profiles, frontend timeline entity pipeline, configurable loop runner, conversation URL rehydration, chat cancellation.

**Phase 4 --- Architecture Review and Decomposition (COINVAULT-014 through 020):**
Backend code review and architecture analysis, server and runner decomposition, projection runtime de-globalization, safe SQL architecture cleanup, tool catalog consolidation, cancellation semantics cleanup.

## Ticket documentation

Every ticket has a structured workspace in `ttmp/2026/03/{16,17}/COINVAULT-XXX--slug/` containing:

- `README.md` --- ticket overview
- `index.md` --- metadata and task index
- `tasks.md` --- granular work items
- `changelog.md` --- chronological change log
- `design-doc/` --- implementation guides and architecture docs
- `reference/` --- diaries, investigation notes
- `scripts/` --- validation and smoke test scripts
- `playbooks/` --- QA procedures

The most instructive diaries for understanding the project evolution are:

- COINVAULT-004 diary: Pinocchio runtime integration decisions
- COINVAULT-005 diary: frontend-backend integration (645 lines, five implementation steps)
- COINVAULT-006 diary: MySQL safe tooling design (557 lines)
- COINVAULT-013 diary: conversation rehydration and cancellation architecture
- COINVAULT-014 diary: backend architecture review findings (global state, context propagation, oversized orchestration)

## Relationship to go-go-golems ecosystem

CoinVault is a consumer of the go-go-golems stack, not a contributor to it (yet). The dependencies are:

- **Pinocchio** (v0.10.9) --- webchat runtime, WebSocket transport, turn/timeline stores, chat infrastructure
- **Geppetto** (v0.10.16) --- AI inference, tool-calling loop, semantic event model, step controllers
- **Clay** (v0.4.0) --- SQL connection management, database probing
- **Glazed** (v1.0.5) --- CLI framework, command registration, help system

Patterns discovered here that are candidates for upstreaming:

- The safe SQL tooling pattern (parser-validate, normalize, clamp, execute) could become a reusable Geppetto tool package
- The projection block system (parse structured markup from assistant text, hydrate against data, render as widgets) could generalize
- The configurable loop runner decomposition pattern could inform Pinocchio's own runner design
- The tool catalog abstraction could become a standard Pinocchio pattern

## Running the project

```bash
# Start MySQL
docker-compose up -d

# Build backend
make build

# Run server (connects to MySQL, serves frontend)
make serve
# or: ./bin/coinvault serve --host localhost --port 17851

# Frontend dev mode (Vite dev server proxying to Go backend)
cd web && npm install && npm run dev
```

Environment variables (see `.env.example`):

- `GEC_MYSQL_HOST`, `GEC_MYSQL_PORT`, `GEC_MYSQL_DATABASE`
- `GEC_MYSQL_USER`, `GEC_MYSQL_PASSWORD`
- `GEC_MYSQL_RO_USER`, `GEC_MYSQL_RO_PASSWORD` (read-only user for safe SQL tools)

## Open questions

- Should the safe SQL tooling be extracted into a reusable Geppetto or Clay package?
- Should the projection block system be generalized for other webchat applications?
- How should authentication and multi-user support be added?
- Should the PostgreSQL tooling be wired to a live database or remain a proof-of-concept?
- Should the frontend widget components be extracted into a shared package for other Pinocchio webchat apps?

## Near-term next steps

- wire tool policy enforcement from `tool-policy.yaml`
- add frontend tests (currently no automated coverage)
- evaluate whether to upstream safe SQL tooling into Geppetto
- consider adding more application profiles (e.g., a `support` persona)
- connect to a real inventory dataset and validate projection rendering at scale

## Project working rule

> [!important]
> Every SQL query the assistant generates must pass through parser-based validation before execution.
> Never trust query text directly --- parse it into an AST, reject non-SELECT statements, enforce LIMIT clamping, and run with timeouts.
> The safety of the system depends on this boundary being airtight.
