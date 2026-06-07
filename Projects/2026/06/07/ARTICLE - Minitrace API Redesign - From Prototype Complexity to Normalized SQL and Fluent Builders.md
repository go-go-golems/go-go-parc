---
title: "Minitrace API Redesign — From Prototype Complexity to Normalized SQL and Fluent Builders"
aliases:
  - MINIVIZ-002 Final Report
  - Minitrace API Architecture
  - mt.db Builder
  - Minitrace Normalized SQL
  - go-minitrace SQL API
tags:
  - article
  - architecture
  - go
  - goja
  - xgoja
  - sql
  - sqlite
  - minitrace
  - design
status: complete
type: article
created: 2026-06-07
repo: /home/manuel/workspaces/2026-06-07/club-meetup-site/go-minitrace
---

# Minitrace API Redesign: From Prototype Complexity to Normalized SQL and Fluent Builders

This note documents the redesign of the minitrace analysis API in `go-minitrace`, which replaced an accumulated collection of custom query languages, typed lenses, and report DSLs with a single, clean API centered on normalized SQLite and a fluent Goja builder. The work is documented in ticket MINIVIZ-002, which is now closed.

## Why this note exists

The previous minitrace-viz prototype had grown too many parallel analysis surfaces. It had a JavaScript trace query DSL, a typed JS lens registry, temporary SQL view materialization, raw SQL execution endpoints, an API workbench page, a guided walkthrough page, and a showcase endpoint. Each surface worked independently, but together they created a system where a user had to learn five different ways to ask the same question about a minitrace session. New contributors would add features to whichever surface was most convenient.

The redesign kept the useful Go-backed report presets and the turn-block JSON endpoint, then replaced everything else with a normalized SQL layer and a single Goja builder API.

## What was implemented

### The problem: accidental complexity

When a prototype proves many API shapes, each one becomes a surface to maintain. The minitrace-viz prototype had seven independent paths for a user to query session data:

- Go-backed report presets
- JavaScript trace query DSL
- Typed JS lens registry (six return types)
- Temporary SQL view materialization
- Raw SQL execution endpoints
- API workbench page
- Guided walkthrough page
- Showcase endpoint

Each path had different syntax, different assumptions about data shape, and different ways of handling errors. The result was unclear which API was the recommended one.

### The solution: normalization + one API

The redesign reduced the surface to two components:

1. A single, normalized relational schema that captures all minitrace session data in nine tables.
2. A Goja `mt.db()` fluent builder that materializes sessions into that schema and exposes raw SQL queries through the DB handle.

```js
const mt = require("minitrace");
const db = mt.db().File("./sample-pi-session.jsonl").AutoConvert(true).SQLiteMemory().Build();
const rows = db.query(`SELECT tool_name, COUNT(*) AS calls FROM tool_calls GROUP BY tool_name ORDER BY calls DESC`);
db.close();
```

The Go side owns source discovery, format detection, conversion, schema creation, materialization, caching, and safe query execution. JavaScript gets a compact handle with `query`, `queryOne`, `queryResult`, `tables`, `schema`, `cacheInfo`, and `close`. The API follows the `goja-text` pattern: small Go-backed builders with fluent methods, explicit `Validate()` and `Build()`, and strongly shaped results.

### What was removed

The old `mt.legacy.*` namespace was removed entirely. All checked-in JavaScript query-command examples were migrated to `mt.db().RuntimeArchives().Build()`. The old minitrace-viz prototype stack (trace query DSL, lens registry, raw SQL views, prompt report, API workbench page, API walkthrough page, showcase endpoint) was removed. Eighty-four lines of prototype code were deleted.

The removed APIs are not accessible from any checked-in scripts. The migration path was:

```js
// Old (removed)
mt.legacy.query(`SELECT id, title, environment->>'agent_framework' FROM table WHERE ...`)

// New
const db = mt.db().RuntimeArchives().Build();
db.query(`SELECT session_id AS id, title, agent_framework AS framework FROM sessions WHERE ...`)
```

DuckDB JSON operators (`environment->>...`, `UNNEST(tool_calls)`) were replaced with normalized SQLite columns. Nested archive columns became first-class scalar columns.

## Architecture

### Normalized schema

The schema captures nine entities. Every table has a `raw_json` column for inspecting source fields not yet promoted to scalar columns.

| Table | Rows per session | Columns | Purpose |
|-------|-----------------|---------|---------|
| `sessions` | 1 | 50+ columns | Top-level session metadata, provenance, flags, environment, operational context, timing, coordination, outcome, and metric summary. |
| `turns` | N (turns) | 22 columns | Conversational turns with role/content, framework metadata, intent markers, streaming fields, and token usage. |
| `tool_calls` | N (tools) | 29 columns | Tool invocations with input/output fields, context, framework metadata, and spawned-agent details. |
| `turn_tool_calls` | N (tools per turn) | 4 columns | Join table preserving which tool calls belong to which turn and their ordinal position. |
| `files` | N (file touches) | 7 columns | File paths touched by tool calls with operation type and success. |
| `annotations` | N (annotations) | 15 columns | Annotations with scope, content, taxonomy mappings, and classification. |
| `handovers` | up to 2 | 7 columns | Received and produced handover documents. |
| `metrics` | 1 | 24 columns | Per-session aggregate metrics: token totals, subagent metrics, model-switch metrics, response-token metrics. |
| `events` | N (turns + tools + annotations) | 14 columns | Timeline rows derived from turns, tool calls, and annotations. |

Each table has CREATE TABLE SQL, column descriptors with types and nullability, and indexes covering common query patterns.

### Indexes

Sixteen indexes support common analyses across sessions, turns, tool calls, files, annotations, handovers, and events. They cover grouping by agent framework, filtering by working directory, joining tool calls to emitting turns, querying tool distribution, finding file access patterns, and ordering timeline events.

### The builder pattern

The builder exposes fifteen source methods, fifteen policy methods, and eight lifecycle methods. The fluent pattern borrows directly from `goja-text`:

```js
const mt = require("minitrace");

// Source selection
mt.db().File("path.minitrace.json")
mt.db().Files(["a.json", "b.jsonl"])
mt.db().Dir("./sessions")
mt.db().Glob("./sessions/*.json")
mt.db().Content(content, {name: "inline.jsonl"})
mt.db().Archive("archive.minitrace.json")
mt.db().RuntimeArchives()  // for query-command runtimes

// Policy
mt.db().SQLiteMemory()
mt.db().SQLiteDiskCache("./cache")
mt.db().Cache("none" | "memory" | "disk" | "auto")
mt.db().CacheDir(dir)
mt.db().ForceRebuild(true)
mt.db().AutoConvert(true)
mt.db().StrictConversion(true)
mt.db().MaxRows(1000)
mt.db().MaxColumns(128)
mt.db().MaxCellChars(4000)
mt.db().Timeout(5000)
mt.db().RequireOrderBy(true)

// Lifecycle
mt.db().Validate()
mt.db().Build()
db.close()
```

### Auto-conversion

The builder loads native minitrace JSON directly. With `.AutoConvert(true)`, it detects and converts supported JSONL formats:

- **Pi JSONL** — records with `session`, `message`, `model_change`, `thinking_level_change` types.
- **Codex JSONL** — records with `session_meta`, `turn_context`, `response_item`, `event_msg` types.
- **Claude Code JSONL** — records with `system`, `user`, `assistant` types and a `message` field.

Format detection inspects the first N records' types. Each adapter (`pi`, `codex`, `claudecode`) produces a `minitrace.Session` from the JSONL records. Conversion diagnostics are available through `db.diagnostics()`.

### Cache modes

Cache keys are deterministic and versioned. They include the schema version, importer version, converter version, backend/storage options, auto-convert setting, and sorted source fingerprints. Four cache modes are available:

| Mode | Builder | Behavior |
|------|---------|----------|
| none | `.Cache("none")` or default | Materialize a fresh in-memory DB. |
| memory | `.Cache("memory")` | Reuse a process-local SQLite DB by cache key. Tracks ref counts and last-used timestamps. |
| disk | `.Cache("disk").CacheDir(dir)` or `.SQLiteDiskCache(dir)` | Build `<cacheDir>/<cacheKey>.sqlite` via temp file + atomic rename. Reopen hits read-only/immutable. |
| auto | `.Cache("auto").CacheDir(dir)` | Check memory first, then disk, then rebuild disk and install into memory. |

Memory cache entries use a package-level map keyed by cache key. On a hit, the builder returns the shared DB with an incremented ref count. On `close()`, the ref count decrements but the entry stays available. If a second caller misses the memory cache but a concurrent builder wins, the duplicate is closed.

Disk cache uses atomic build/rename to prevent partial files from becoming cache hits. The `os.Rename(temp, final)` ensures the file is fully written before any new handle can open it. Cached handles open the file with `mode=ro&immutable=1` for read-only access.

Auto cache checks memory first, then disk, then rebuilds. When a disk rebuild occurs, the new DB is also installed into the memory cache for subsequent handles.

### Query safety

The DB handle exposes raw SQL with five defense layers:

1. **Prefix validation** — accepts only `SELECT` and `WITH` queries (with or without trailing whitespace including newlines and tabs).
2. **Single statement** — rejects multiple statements (semicolon-separated).
3. **Table allow-list** — rejects queries referencing tables not in the normalized schema.
4. **Prepared statement readonly check** — uses SQLite's `SQLiteStmt.Readonly()` to verify the query cannot modify data.
5. **Connection-level authorizer** — denies `INSERT`, `UPDATE`, `DELETE`, `PRAGMA`, `CREATE`, `DROP`, and `TRANSACTION` operations at execution time.

Additionally, configurable limits on rows, columns, and cell characters prevent excessive output.

## Cookbook report examples

The checked-in JS showcase repository includes raw-SQL report commands under:

```
testdata/query-repositories/js-showcase/analysis/report-cookbook.js
```

| Command | What it reports | Tables used |
|---------|----------------|-------------|
| `session-inventory` | Session list with framework, workspace, model, turns/tools, token totals, cost, annotation count, handover count | `sessions`, `metrics`, `annotations`, `handovers` |
| `tool-risk-matrix` | Tool usage with failure count, spawned-agent calls, annotation hits, avg duration, max payload size, and risk label | `tool_calls`, `sessions`, `annotations` |
| `file-heatmap` | File touches grouped by path and operation with session counts and failure counts | `files`, `sessions` |
| `prompt-instruction-audit` | System prompt coverage with length, existence, and keyword heuristics | `sessions` |
| `turn-timeline` | Normalized turn/tool/annotation event timeline with kind, role, severity, tool call ID, annotation ID | `events`, `sessions` |

Example invocation:

```bash
go run ./cmd/go-minitrace query commands \
  --query-repository ./testdata/query-repositories/js-showcase \
  analysis report-cookbook tool-risk-matrix \
  --archive-glob './output/active/*/*.minitrace.json' \
  --output json
```

## Validation

All changes are covered by tests:

- Package-level tests for schema, materialization, query runner, cache keys, and conversion.
- Goja provider integration tests for `mt.db()`, file/dir/glob loading, auto-conversion, non-strict conversion, cache key exposure, memory cache reuse with ref-count/release/source-change invalidation, disk cache build/hit/force-rebuild, and auto cache memory-disk-rebuild ordering.
- Query-command runtime tests for all cookbook commands against enriched fixture archives with system prompts, file paths, durations, annotations, and spawned-agent data.
- Golden materialization tests comparing normalized row counts and key columns against fixture `minitrace.Session` values.

```bash
cd /home/manuel/workspaces/2026-06-07/club-meetup-site/go-minitrace
GOTOOLCHAIN=auto go test ./... -count=1
```

## What warrants a second pair of eyes

- Whether the `cacheInfo()` method should distinguish `hitSource: "memory" | "disk" | "rebuild"` instead of a single boolean.
- Whether disk cache entries should need metadata sidecar files for diagnostics and source display information.
- Whether the report cookbook commands should move from testdata into a built-in query repository once the API stabilizes.
- Whether `tool-risk-matrix` should use weighted numeric scoring instead of a categorical `risk_label`.
- Whether `prompt-instruction-audit` should become a text-analysis recipe later instead of pure SQL heuristics.

## What should be done in the future

- Add a Markdown-generating report command that composes the five cookbook row sets into one human-readable document.
- Add cache cleanup/listing utilities if persistent disk cache usage grows.
- Add real-format fixture golden tests for converted Pi/Codex/Claude sessions.
- If a concrete large-analytics workload appears, revisit the optional DuckDB backend that was deferred.

## Related notes

- [[ARTICLE - Minitrace Viz API Redesign - Normalized SQL and Fluent Goja Builders]] — earlier snapshot of this article from before full implementation.
- [[PROJ - ZK Tool]] — reference for article note structure.
