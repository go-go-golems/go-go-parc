---
Title: Bridge 1 — SQLite as Canonical Store and Product Boundary
Ticket: PROJECT-MAPS-001
Status: active
Topics:
    - research
    - projects
    - concept-maps
    - sqlite
    - architecture
DocType: bridges
Intent: long-term
Owners: []
RelatedFiles:
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/05-bridge-topic-reports-plan.md
      Note: Bridge topic plan; this is Bridge 1
    - Path: ttmp/2026/06/22/PROJECT-MAPS-001--concept-maps-for-recent-project-topics/design/04-refined-topic-concept-maps-v2.md
      Note: Refined concept maps where SQLite canonical store recurs across T2/T5/T6/T7
    - Path: Projects/2026/06/12/ARTICLE - Go Go Objects - Durable Objects Runtime on Goja.md
      Note: Per-object SQLite for actor state
    - Path: Projects/2026/06/07/ARTICLE - Minitrace API Redesign - From Prototype Complexity to Normalized SQL and Fluent Builders.md
      Note: Normalized transcript SQLite as canonical analysis substrate
    - Path: Projects/2026/05/27/ARTICLE - RAG Evaluation System - Workflow-Driven Retrieval Evaluation.md
      Note: Two-database architecture (corpus vs engine)
    - Path: Projects/2026/05/01/ARTICLE - Static SQL.js Codebase Browser - SQLite as the Browser Runtime.md
      Note: SQLite as product boundary and browser runtime
    - Path: Projects/2026/05/03/ARTICLE - SQLite in the Browser - Measuring and Fixing sql.js Performance in Static Code Review Sites.md
      Note: Query-plan-as-frontend-architecture failure mode
    - Path: Projects/2026/05/02/ARTICLE - Squeezing a SQLite Database From 32 MB to 1.4 MB - How We Found and Fixed 99 Pct Redundancy in Codebase-Browser.md
      Note: Normalized schema, GOWORK=off, integer FK invariants
    - Path: Projects/2026/06/08/ARTICLE - SQLite Authorizer and Query Safety - Deep Dive Technical Analysis.md
      Note: Authorizer as correct table-allowlist boundary
    - Path: Projects/2026/05/21/PROJ - Readwise Viewer.md
      Note: SQLite canonical store with disposable Bleve derived index
ExternalSources: []
Summary: Textbook-style report on SQLite as the canonical store and product boundary, recurring across T2/T5/T6/T7 with concrete instances, invariants, and failure modes.
LastUpdated: 2026-06-22T23:59:00-04:00
WhatFor: Read this to understand why SQLite recurs as the canonical store across durable objects, transcript analysis, RAG, OCR, codebase browsing, and app shells, and what invariants and failure modes it carries.
WhenToUse: Before designing a new pipeline that needs a stable fact base, before evaluating whether to add a server in front of a static artifact, or when diagnosing a SQLite-related freeze or correctness bug.
---

# SQLite as Canonical Store and Product Boundary

This chapter explains why a single SQLite file recurs as the canonical fact base across durable object runtimes, transcript-analysis tools, RAG evaluation systems, OCR work queues, codebase browsers, and personal-library viewers — and why treating that file as a product boundary (not just a private implementation detail) is the design move that makes the rest of the architecture tractable. The goal is not to argue that SQLite is universally the right store. The goal is to make the pattern legible: when SQLite owns the facts, every other surface (browser, CLI, LLM, script, search index) becomes a derived projection that can be rebuilt, replaced, or inspected without negotiating a new contract.

The pattern appears in seven concrete forms in the recent project record: per-actor durable storage in `go-go-objects`, the normalized `mt.db()` nine-table schema in `go-minitrace`, the two-database corpus/engine split in the RAG Evaluation System, the `BEGIN IMMEDIATE` work queue in Book OCR, the static `db/codebase.db` shipped to the browser with `sql.js`, the Readwise SQLite mirror with disposable Bleve search, and the vault-as-read-only-source-of-truth model in Retro Obsidian Publish. Each instance is a different product, but each makes the same architectural commitment: the database file is the source of truth, and everything that reads from it is rebuildable.

## 1. The canonical store

### 1.1 What "canonical" means here

A canonical store is the substrate that owns the facts. Other representations of those facts — search indexes, rendered HTML, JSON exports, vector embeddings, browser UI state — are derived. A derived artifact can be deleted and rebuilt from the canonical store without loss. The canonical store cannot be rebuilt from its derivatives without re-running the original ingestion work.

That definition sounds abstract, so it is worth grounding it in a concrete failure mode. In the early versions of `codebase-browser`, the static export directory contained a `precomputed.json` file that the browser loaded and queried through a TinyGo WASM module. The JSON file held answers to a curated set of questions the indexer had predicted the reader would ask. When the reader clicked into a symbol history that the exporter had not precomputed, the browser returned `STATIC_NOT_PRECOMPUTED` and could not proceed (`Projects/2026/05/01/ARTICLE - Static SQL.js Codebase Browser - SQLite as the Browser Runtime.md`, section 1).

That error is the signature of a non-canonical store. The JSON file was not the source of truth; the SQLite database that produced it was. The browser was reading a cache of predicted answers, not querying the facts. The fix was to ship the SQLite database itself to the browser and let `sql.js` query it locally. Once the database became the runtime artifact, the browser could answer any question the schema could express, not just the questions the exporter had foreseen.

This is the first invariant of the pattern:

> **The canonical store is the artifact that can answer any question the schema can express. A derived artifact can only answer questions its builder predicted.**

### 1.2 Why SQLite, and why it recurs

SQLite recurs as the canonical store across the project record because it satisfies four constraints simultaneously, and the alternatives each sacrifice at least one.

The first constraint is **portability as a single file**. A SQLite database is one file. It can be copied, attached to an email, served from a static file server, opened by a browser through WebAssembly, inspected by `sqlite3`, or archived with a pull request. PostgreSQL requires a running server. DuckDB stores its data on disk but is optimized for analytical queries over large data, not for being shipped as a browser artifact. A JSON file is portable but cannot express relational joins without re-implementing them in the consumer.

The second constraint is **relational expressiveness without a server process**. The questions a codebase browser, RAG evaluation system, or transcript analyzer needs to ask are relational: "which symbols exist at `HEAD`", "which chunks belong to which document under which strategy", "which tool calls were issued in which turn in which session". SQLite answers these with SQL, including joins, window functions, CTEs, and JSON extraction. The consumer does not re-implement the relational model.

The third constraint is **concurrency model that fits a single-process host**. SQLite uses file-level locking with a write-ahead log (WAL). A single writer and many readers can coexist. This is the model that `go-minitrace`, `go-go-objects`, RAG Evaluation, and Book OCR need: one process writes, queries read concurrently, and there is no operational cost to running a separate database server. PostgreSQL would be operationally heavier than the workload requires; a custom file format would re-implement concurrency incorrectly.

The fourth constraint is **availability in the browser through WebAssembly**. `sql.js` is a WebAssembly build of SQLite. The browser can load a SQLite file, query it locally, and never make a network request after the initial fetch. This is what makes `codebase-browser`'s static export possible: the same database that the Go indexer built is the database the browser queries. No server translates between them. This constraint is unique to SQLite among the relational stores the project record uses.

When all four constraints matter, SQLite is the canonical store. When only the first three matter, SQLite still recurs because the cost of choosing something else is operational overhead with no benefit. The recurrence across T2 (Durable Objects), T5 (go-minitrace, Pinocchio reconcile export, CoinVault), T6 (RAG Evaluation, Book OCR, Codebase Browser, Readwise Viewer, Smailnail mirror, CozoDB SQLite preset), and T7 (Retro Obsidian Publish, SQLide Browser) is not coincidence. It is the same four constraints being satisfied by the same tool.

## 2. The product-boundary pattern

The deeper move is not "use SQLite." The deeper move is to treat the SQLite file as a product boundary — an interface between build time and read time that multiple consumers can query without coupling to each other.

### 2.1 SQLite as browser runtime

The cleanest instance of the product-boundary pattern is `codebase-browser`'s static export. The export directory contains:

```text
export/
├── index.html
├── assets/
├── manifest.json
├── db/
│   └── codebase.db
├── sql-wasm.wasm
└── sql-wasm-browser.wasm
```

The browser loads `manifest.json`, fetches `db/codebase.db`, initializes `sql.js`, and queries the database locally through a `SqlJsQueryProvider`. There is no Go server at runtime. Go's job is to build the database; once built, the database is the runtime (`Projects/2026/05/01/ARTICLE - Static SQL.js Codebase Browser - SQLite as the Browser Runtime.md`, sections 2–4).

The boundary is explicit in the manifest:

```json
{
  "queryEngine": "sql.js",
  "db": { "path": "db/codebase.db" },
  "hasGoRuntimeServer": false
}
```

`hasGoRuntimeServer: false` is not just metadata. It is a statement of architecture. It tells the browser, scripts, and future maintainers that there is no hidden process to rescue the UI if a query was not precomputed. There is only the database and the provider.

The product-boundary consequence is that the same `db/codebase.db` is useful to non-browser consumers. A reviewer can open it with `sqlite3`, ask which symbols changed, list references to a function, or inspect rendered review docs. An LLM can be handed the database as a structured artifact. A script can query it without parsing JSON. The database is the interface between build time and reading time, and reading time includes humans, browsers, scripts, and models.

### 2.2 SQLite as script and LLM artifact

When the SQLite file is the canonical store, it becomes the natural artifact to hand to a script or a language model. The `go-minitrace` project makes this explicit. A minitrace session archive (`.minitrace.json`, schema `minitrace-v0.2.0`) is converted into a normalized SQLite database via `mt.db()`:

```js
const mt = require("minitrace");
const db = mt.db().File("./sample-pi-session.jsonl").AutoConvert(true).SQLiteMemory().Build();
const rows = db.query(
  `SELECT tool_name, COUNT(*) AS calls FROM tool_calls GROUP BY tool_name ORDER BY calls DESC`
);
db.close();
```

The database has nine tables: `sessions`, `turns`, `tool_calls`, `turn_tool_calls`, `files`, `annotations`, `handovers`, `metrics`, and `events` (`Projects/2026/06/07/ARTICLE - Minitrace API Redesign - From Prototype Complexity to Normalized SQL and Fluent Builders.md`, "Normalized schema"). Each table has a `raw_json` column for source fields not yet promoted to scalar columns, so the database is both the analysis substrate and the provenance record.

The reason this matters is that a minitrace session is a structured object with hundreds of fields, nested arrays, and cross-references. Asking questions about it through JSON manipulation requires re-implementing joins, grouping, and filtering in every consumer. Asking questions through SQL lets the same database serve a JavaScript query repository, a CLI command, an HTML report generator, and an LLM inspection prompt — all through the same SQL surface.

The earlier prototype tried to provide seven parallel query surfaces (Go-backed report presets, a JavaScript trace query DSL, a typed JS lens registry, temporary SQL view materialization, raw SQL execution endpoints, an API workbench page, a guided walkthrough page, and a showcase endpoint). Each surface had different syntax and different assumptions about data shape. The redesign replaced all seven with one normalized schema and one Goja builder (`Projects/2026/06/07`, "What was removed"). The lesson is general: when the canonical store is well-shaped, parallel query surfaces collapse into one.

### 2.3 SQLite as operator surface

The third form of the product-boundary pattern is the operator surface. When SQLite is canonical, the same database that backs the HTTP API and the browser UI also backs the CLI. The RAG Evaluation System makes this explicit with its adapter rule:

```text
Glazed CLI command -> service method -> db.Queries
HTTP handler       -> same service method -> db.Queries
```

The CLI is not a debugging convenience. It is the first stable operator surface, and it makes it possible to run controlled smoke tests without requiring the frontend to exist (`Projects/2026/05/27/ARTICLE - RAG Evaluation System - Workflow-Driven Retrieval Evaluation.md`, "CLI and HTTP adapter design"). The same service methods back both adapters, so behavior cannot drift between them.

Readwise Viewer repeats the pattern. The Go binary exposes Glazed CLI commands (`readwise-viewer documents`, `readwise-viewer search`, `readwise-viewer serve`) and HTTP API routes over the same `data/readwise.db` SQLite file (`Projects/2026/05/21/PROJ - Readwise Viewer.md`, "SQLite and Go backend"). The CLI and the CLIM-style web UI are two projections of the same canonical store. When the search backend was migrated from SQLite FTS5 to Bleve, the migration touched the derived index without touching the canonical store.

The operator-surface consequence is that the database is inspectable and drivable from the terminal. An operator can run `rag-eval chunk apply`, inspect the resulting rows with `sqlite3 data/rag-eval.db`, run a one-off SQL query to verify a hypothesis, and then trigger the same operation through the HTTP API. The database is the contract between these surfaces; each surface is a thin adapter over shared services.

## 3. Concrete instances

The seven instances below are the load-bearing evidence for the pattern. Each is a different product, but each makes the same architectural commitment.

### 3.1 Durable Objects: one SQLite per actor

`go-go-objects` is a local single-process Durable Objects runtime built on `go-go-goja`. A Durable Object is identified by `(namespace, name)`, lazily started as one JavaScript actor, and backed by one private SQLite database. Each live object owns one `engine.Runtime`; all JavaScript execution for that object runs through `RuntimeOwner.Call()` (`Projects/2026/06/12/ARTICLE - Go Go Objects - Durable Objects Runtime on Goja.md`, "The core mental model").

The storage layout is per-object:

```text
<storage-root>/<namespace>/<first-two-hash-chars>/<hash>.sqlite
```

Each object database stores KV data, metadata, and object-local alarm state:

```sql
CREATE TABLE IF NOT EXISTS kv (
  key TEXT PRIMARY KEY,
  value_json BLOB NOT NULL,
  updated_at_ms INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS alarms (
  singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
  due_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL
);
```

The JavaScript API is synchronous:

```js
state.storage.get(key)
state.storage.put(key, value)
state.storage.delete(key)
state.storage.list(prefixOrOptions)
state.storage.transaction(fn)
```

Synchronous storage is a deliberate choice. The MVP already serializes dispatch per object, so a read-modify-write sequence has a clear order without async coordination:

```js
const current = state.storage.get("count") || 0;
state.storage.put("count", current + 1);
```

The canonical-store commitment here is that each object's durable state is one SQLite file. Eviction removes the in-memory actor; the next dispatch recreates the actor from the same file. A central `alarms.sqlite` index tracks which objects have due alarms, and reconciliation restores the central index from object-local alarm rows if they drift. The pattern is per-actor canonical storage, not a shared database.

### 3.2 go-minitrace: normalized transcript SQLite

`go-minitrace` converts native agent session JSONL (Pi, Codex, Claude Code) into a canonical `.minitrace.json` archive, then materializes that archive into a normalized SQLite database via `mt.db()`. The redesign replaced an earlier prototype that had seven parallel query surfaces with one normalized schema and one Goja builder.

The nine-table schema is the canonical analysis substrate:

| Table | Rows per session | Purpose |
|-------|------------------|---------|
| `sessions` | 1 | Top-level session metadata, provenance, environment, timing, outcome |
| `turns` | N (turns) | Conversational turns with role/content, framework metadata, token usage |
| `tool_calls` | N (tools) | Tool invocations with input/output, context, framework metadata |
| `turn_tool_calls` | N (tools per turn) | Join table preserving which tool calls belong to which turn |
| `files` | N (file touches) | File paths touched by tool calls, with operation type and success |
| `annotations` | N (annotations) | Annotations with scope, content, taxonomy mappings |
| `handovers` | up to 2 | Received and produced handover documents |
| `metrics` | 1 | Per-session aggregate metrics: token totals, subagent metrics |
| `events` | N (turns + tools + annotations) | Timeline rows derived from turns, tool calls, and annotations |

Each table has a `raw_json` column so that source fields not yet promoted to scalar columns remain inspectable. Sixteen indexes cover common analyses: grouping by agent framework, filtering by working directory, joining tool calls to emitting turns, querying tool distribution, finding file access patterns, ordering timeline events.

The canonical-store commitment is that DuckDB `UNNEST` over JSON arrays was a documented dead end in the Goja path, and normalized SQLite is the substrate that replaced it (`ttmp/.../sources/05a-agents-transcripts-sessionstream.md`, "Arc 1"). The query repository — a set of named `__verb__`-declared JS commands discovered by a scanner — is a derived projection over the canonical schema. Adding a new analysis verb does not require changing the schema; it requires writing a new SQL query against the existing tables.

### 3.3 RAG Evaluation: corpus DB and engine DB split

The RAG Evaluation System introduces a refinement of the canonical-store pattern: **two SQLite databases, one for canonical corpus state and one for workflow orchestration state**. The corpus DB lives at `data/rag-eval.db` and stores sources, documents, chunks, chunking strategies, chunk embeddings, enrichments, search indexes, and evaluation tables. The engine DB lives at `state/rag-eval-workflows.db` and stores scraper workflow state: operations, queues, leases, retries, artifacts, and projections.

The reason for the split is WAL contention. Workflow orchestration writes frequently — operations transition states, leases are acquired and released, retries are scheduled. Corpus reads are frequent — the UI lists sources, documents, chunks, embeddings. If both lived in one database, the writer would block readers or vice versa, depending on the journal mode. Separating them lets each database use the WAL mode that fits its access pattern (`ttmp/.../sources/06a-data-rag-vectors-ocr.md`, "Two-database architecture"; `Projects/2026/05/29/ARTICLE - RAG Evaluation - Workflow Intake UI Architecture and Data Exploration.md`).

The canonical-store commitment is unchanged: the corpus DB is canonical, and derived artifacts (Bleve BM25 indexes, FAISS vector indexes, evaluation runs) are rebuildable from it. The engine DB is canonical for workflow state but disposable in the sense that a workflow can be re-run. The split is about write contention, not about deriving one from the other.

Identity is the central design rule that makes this work. A document is `(source_id, relative_path)`. A chunk is `(document_id, strategy_id, chunk_index)`. An embedding is `(chunk_id, strategy_id, provider, model, dimensions)` with a `text_hash` freshness check. These composite keys mean that a chunk can exist under multiple chunking strategies for the same document, and an embedding can exist under multiple providers, models, and dimension counts for the same chunk. Derived state is rebuilt or skipped based on stable keys.

### 3.4 Book OCR: SQLite work queue with `BEGIN IMMEDIATE`

Book OCR is a model-call-to-durable-artifact system: page images go in, structured JSON comes out, deterministic Markdown and PDF are rendered, and a targeted repair loop re-runs selected pages. The work queue is a SQLite database with `BEGIN IMMEDIATE` for atomic page claims.

The workflow starts as a Python script with a SQLite work queue. Each page is a row with a status. Parallel workers claim pages by running:

```sql
BEGIN IMMEDIATE;
UPDATE pages SET status='claimed', worker_id=? WHERE id IN (
  SELECT id FROM pages WHERE status='ready' LIMIT ?
);
COMMIT;
```

`BEGIN IMMEDIATE` acquires a write lock immediately, before the query planner decides what locks the statement needs. Without it, SQLite uses deferred locking: the `SELECT` acquires a read lock, the `UPDATE` tries to upgrade to a write lock, and two workers can deadlock or one can see a stale snapshot. With `BEGIN IMMEDIATE`, the lock is acquired up front, the `SELECT` and `UPDATE` run atomically, and concurrent workers do not double-claim (`ttmp/.../sources/06a-data-rag-vectors-ocr.md`, "VLM OCR work queue"; `Projects/2026/05/20/ARTICLE - VLM OCR Pipeline for Scanned PDFs.md`).

The canonical-store commitment here is that the work queue is the source of truth for what has been processed, what is in progress, and what failed. Raw turns, structured JSON, rendered Markdown, and validation JSON are all preserved per page. A targeted repair loop requeues selected page ops (setting their status to `ready`) and downstream ops (setting their status to `pending`), preserving dependency semantics. The work queue is the contract between the VLM, the renderer, and the human reviewer.

### 3.5 Codebase Browser: static SQLite + sql.js

The Codebase Browser is the deepest instance of the product-boundary pattern. The pipeline is:

```text
Git commit range + source tree + Markdown review docs
    -> Go review/history indexer
    -> SQLite database
    -> Static export packager
    -> Export directory with React SPA + db/codebase.db + sql-wasm.wasm
    -> Browser opens SQLite with sql.js and queries locally
```

Go does not disappear. It moves to the correct side of the line. Go is good at walking repositories, reading Git history, parsing source, resolving symbols, rendering Markdown directives, and creating a high-fidelity SQLite artifact. It is not asked to be present at runtime (`Projects/2026/05/01/ARTICLE - Static SQL.js Codebase Browser`, section 2).

The database schema is normalized to avoid the redundancy that plagued the earlier snapshot-per-commit design:

```sql
-- One row per unique symbol version (keyed by stable_id + body_hash)
CREATE TABLE symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stable_id TEXT NOT NULL,
    body_hash TEXT NOT NULL DEFAULT '',
    UNIQUE(stable_id, body_hash)
);

-- Narrow mapping table: which symbol version appears in which commit
CREATE TABLE commit_symbols (
    commit_id INTEGER NOT NULL REFERENCES commits(id),
    symbol_id INTEGER NOT NULL REFERENCES symbols(id),
    PRIMARY KEY (commit_id, symbol_id)
) WITHOUT ROWID;
```

The old schema stored one row per (commit, entity) — a project with 500 symbols and 100 commits got 50,000 symbol rows, even though most symbols were identical across commits. The new schema stores each unique entity once and uses narrow integer mapping tables to record which version appears in which commit. The result was a 23× size reduction: a 50-commit review that was 32 MB became 1.4 MB (`Projects/2026/05/02/ARTICLE - Squeezing a SQLite Database From 32 MB to 1.4 MB...`, "Results: the numbers").

Compatibility views recreate the old snapshot-shaped interface over the normalized tables, so the React frontend's SQL queries run unchanged:

```sql
CREATE VIEW snapshot_symbols AS
SELECT
    c.hash AS commit_hash,
    s.stable_id AS id,
    s.kind, s.name,
    p.stable_id AS package_id,
    f.stable_id AS file_id
FROM commit_symbols cs
JOIN commits c ON c.id = cs.commit_id
JOIN symbols s ON s.id = cs.symbol_id
JOIN packages p ON p.id = s.package_id
JOIN files f ON f.id = s.file_id;
```

This is the canonical-store commitment in its strongest form. The database is the product boundary: Go builds it, the browser queries it, scripts inspect it, LLMs consume it, and static file servers host it. The export is a compiler pass, not a server startup.

### 3.6 Readwise Viewer: local SQLite mirror

Readwise Viewer is a local workbench for a personal Readwise Reader library of 13,848 documents. A Python sync script populates a SQLite database with `documents`, `tags`, `document_tags`, `sync_runs`, and `sync_state` tables, plus an FTS5 table `documents_fts` over `title, author, site_name, summary, source_url, notes` (`Projects/2026/05/21/PROJ - Readwise Viewer.md`, "SQLite and Go backend").

The canonical-store commitment is explicit: SQLite stays canonical, and Bleve becomes a disposable derived index. When the search backend was migrated from SQLite FTS5 to Bleve BM25, the migration removed FTS5 triggers and the `--backend` flag entirely. The Bleve index is rebuilt from SQLite on demand. If the Bleve index is corrupted or lost, it can be rebuilt from the canonical store without re-syncing from Readwise.

The search query is a boosted field disjunction: title at 5.0, tags at 4.0, summary at 2.5, notes at 2.0, content_text at 1.0, search_text at 0.5. The API hydrates Bleve hits back through SQLite for canonical display data, because the Bleve index stores only what Bleve needs for ranking, not the full document. The separation between canonical store and derived index is what makes this safe: the derived index can be optimized for search without worrying about losing display data.

### 3.7 Retro Obsidian Publish: vault as read-only source

Retro Obsidian Publish is a single-binary Go+React vault publisher. The vault directory is the read-only source of truth; all data (HTML, Bleve search index, backlinks, file tree) is derived from the Markdown files. There is no database in the traditional sense — the canonical store is the filesystem — but the architectural commitment is the same: derived artifacts are rebuildable from the canonical source.

The Go binary serves an API and an embedded React SPA. A Node.js Express sidecar pre-fetches data, renders via `renderToString()`, and returns HTML for agent readability and SEO. Agent-readable mirrors (`/index.md`, `/note/{slug}.md`) are served before the SPA fallback, with `Accept: text/markdown` content negotiation. The `a14y` score went from 62 to 99 (`ttmp/.../sources/05b-agents-pi-providers-dashboards.md`, "Retro Obsidian Publish").

This instance is included to mark the boundary of the pattern. When the canonical source is a directory of Markdown files rather than a SQLite database, the same invariants apply: the source is read-only, derived artifacts (search index, backlinks graph, rendered HTML) are rebuildable, and the product boundary is the source itself, not a server process that interprets it. SQLite is the most common canonical store in the project record, but it is not the only one.

## 4. Architectural invariants

The seven instances above share three invariants. Each invariant is a rule that, when violated, produces a concrete failure mode. The failure modes are documented in section 5.

### 4.1 Canonical vs derived

The first invariant is the distinction between canonical and derived state. Canonical state is the source of truth; derived state is rebuildable from it. The distinction must be explicit in the schema, not implicit in the code.

The RAG Evaluation System encodes this invariant in its identity rules. A document is `(source_id, relative_path)` — a stable key derived from the source and the file's position within it. A chunk is `(document_id, strategy_id, chunk_index)` — a stable key that lets the same document be chunked under multiple strategies. An embedding is `(chunk_id, strategy_id, provider, model, dimensions)` with a `text_hash` freshness check — a stable key that lets the same chunk be embedded by multiple providers and models (`Projects/2026/05/27/ARTICLE - RAG Evaluation System`, "State model and identity").

The `text_hash` is the freshness mechanism. When the embedding service runs, it computes `sha256(chunk.text)` and compares it to the stored `text_hash`. If they match and `force` is not set, the embedding is skipped. If they differ, the embedding is recomputed. This means the embedding is derived state: it can be deleted and rebuilt from the chunk, and the chunk is canonical state because it is identified by stable keys.

The Readwise Viewer's migration from FTS5 to Bleve is another instance. FTS5 was a derived index built from the `documents` table. Bleve is a derived index built from the same table. The migration touched the derived index without touching the canonical store. The canonical store did not need to know that the search backend had changed.

The codebase-browser static export encodes this invariant in its working rule: "If derived data is worth shipping, prefer a SQLite table or view over an ad hoc file" (`Projects/2026/05/01`, section 16). Derived data lives in the database, not in sidecar JSON files, because sidecar files are not rebuildable from the canonical schema without a re-export step.

The invariant, stated precisely:

> **Canonical state has stable identity keys that do not depend on derived state. Derived state is identified by reference to canonical state and carries a freshness signal (hash, version, timestamp) that lets it be rebuilt or skipped.**

### 4.2 Two-database architecture

The second invariant is the two-database architecture: separate the canonical corpus database from the workflow engine database. The RAG Evaluation System introduces this invariant to prevent WAL contention between frequent workflow writes and frequent corpus reads.

The corpus DB stores domain data: sources, documents, chunks, embeddings. The engine DB stores workflow state: operations, queues, leases, retries, artifacts. Cross-database joins happen in the UI, not in the backend. The UI fetches from both APIs and stitches the results in React, because a SQL join across two SQLite files is not a query the database can execute.

The two-database architecture is not always needed. `go-minitrace` uses one in-memory SQLite database per session because the access pattern is read-heavy after materialization. `go-go-objects` uses one SQLite database per actor because each actor's state is independent. Readwise Viewer uses one SQLite database because the sync script is the only writer and it runs infrequently.

The invariant is needed when the workload has both a frequent writer (a workflow engine transitioning operation states) and frequent readers (a UI listing corpus state) against the same logical database. In that case, separating them prevents the writer from blocking the readers.

The invariant, stated precisely:

> **When a workflow engine and a corpus reader share a logical database and both have high-frequency access, split them into two physical databases. Cross-database joins happen in the consumer, not in the database.**

### 4.3 Query-plan-as-frontend-architecture

The third invariant is unique to the browser-runtime form of the pattern. When SQLite runs in the browser through `sql.js`, the query plan is part of frontend architecture. A query that is correct in native SQLite can freeze the browser if its plan forces broad view expansion before constraints are applied.

The `snapshot_refs` view in `codebase-browser` is the canonical example. The view expands `locations_json` into one row per reference location:

```sql
CREATE VIEW snapshot_refs AS
SELECT
    c.hash AS commit_hash,
    row_number() OVER (PARTITION BY c.id ORDER BY rv.id, j.key) AS id,
    s.stable_id AS from_symbol_id,
    rv.to_stable_id AS to_symbol_id,
    rv.kind,
    f.stable_id AS file_id,
    json_extract(j.value, '$.start_line') AS start_line,
    json_extract(j.value, '$.start_offset') AS start_offset,
    json_extract(j.value, '$.end_offset') AS end_offset
FROM commit_refs cr
JOIN commits c ON c.id = cr.commit_id
JOIN ref_versions rv ON rv.id = cr.ref_version_id
JOIN symbols s ON s.id = rv.from_symbol_id
JOIN files f ON f.id = rv.file_id,
    json_each(rv.locations_json) AS j;
```

A query that filters this view by `commit_hash` and `file_id` looks selective from the SQL text. But the view body expands the entire `commit_refs` × `ref_versions` × `json_each` space before the outer query's constraints are applied. On a 199 MB database with 6,074,525 `commit_refs` rows, this query took about 60 seconds in native SQLite and froze the browser through `sql.js` (`Projects/2026/05/03/ARTICLE - SQLite in the Browser...`, "How the freeze was measured").

The fix was to rewrite the hot query against normalized base tables, constraining by commit and file identity before expanding JSON:

```sql
SELECT s.stable_id AS fromSymbolId,
       rv.to_stable_id AS toSymbolId,
       rv.kind,
       f.stable_id AS fileId,
       json_extract(j.value, '$.start_offset') AS startOffset,
       json_extract(j.value, '$.end_offset') AS endOffset
FROM commits c
JOIN commit_refs cr ON cr.commit_id = c.id
JOIN ref_versions rv ON rv.id = cr.ref_version_id
JOIN symbols s ON s.id = rv.from_symbol_id
JOIN files f ON f.id = rv.file_id
JOIN json_each(rv.locations_json) j
WHERE c.hash = ?
  AND f.stable_id = ?
ORDER BY startOffset, endOffset;
```

The same 82 rows returned in 9 ms in native SQLite and 19 ms in `sql.js`. The difference is not subtle. It is the difference between expanding a large conceptual snapshot and walking a constrained part of a normalized graph.

The deeper lesson is that `sql.js` runs on the browser's main thread (or in a Web Worker, if configured). A slow query does not manifest as a slow backend; it manifests as a frozen page. The query planner is part of frontend performance, and a view that works for a small export can become a UI freeze at full repository scale.

The invariant, stated precisely:

> **When SQLite runs in the browser, the query plan is a frontend performance concern. Hot queries must constrain by stable entity identity and commit membership before expanding JSON or windowed compatibility views. Measure query plans in native SQLite before blaming WebAssembly.**

## 5. Failure modes

Each failure mode below is a concrete bug from the project record. They are included not as warnings but as design drivers: each one reveals a place where the canonical-store pattern breaks if a specific invariant is not held.

### 5.1 Chunking termination bug

The RAG Evaluation System's fixed-size chunker originally contained a termination bug. With overlap enabled, the algorithm could emit a final chunk that reached the end of the text, subtract the overlap, and then emit another final chunk with the same end offset. The loop did not terminate. The observed symptom was a killed process during `chunk apply` even though the input document was small (`Projects/2026/05/27/ARTICLE - RAG Evaluation System`, "Failure modes and corrections").

The corrected chunker enforces three rules:

```go
if c.ChunkSize <= 0 { error }
if c.Overlap < 0 { error }
if c.Overlap >= c.ChunkSize { error }

for start < totalRunes:
    end = min(start + chunkSize, totalRunes)
    emit chunk [start:end]

    if end >= totalRunes:
        break

    nextStart = end - overlap
    if nextStart <= start:
        nextStart = start + 1
    start = nextStart
```

The two invariants are explicit: if a chunk reaches the end of the text, the loop exits; if the loop continues, the next start is greater than the previous start. The bug was not just a patch — it changed the development rules. After the fix, the project added `GOMAXPROCS=2 GOMEMLIMIT=1024MiB` to the test command to bound the cost of future algorithmic mistakes.

The lesson is that derived-state generators (chunkers, embedders, indexers) need explicit termination invariants. A loop that "should" terminate because it appears to make progress can fail to terminate when the progress invariant is not actually enforced.

### 5.2 SQLite concurrency hazards

Book OCR's parallel workers need `BEGIN IMMEDIATE` for atomic page claims. Without it, SQLite uses deferred locking: a `SELECT` acquires a read lock, an `UPDATE` tries to upgrade to a write lock, and two workers can either deadlock or one can see a stale snapshot.

The hazard is general to any SQLite workload with concurrent writers. SQLite's WAL mode allows one writer and many readers, but the writer acquires the write lock at the first write statement, not at `BEGIN`. If two transactions both `BEGIN` (deferred), run a `SELECT`, and then try to `UPDATE`, one of them will get `SQLITE_BUSY` when the `UPDATE` tries to upgrade. `BEGIN IMMEDIATE` acquires the write lock at `BEGIN`, before any statement runs, so the transaction is serialized from the start.

The `go-go-objects` runtime avoids this hazard by serializing dispatch per actor. Each actor has one runtime and one dispatch gate; storage calls are synchronous within a dispatch. There is no concurrency within an actor's storage because there is no concurrency within an actor's dispatch. The concurrency model is per-actor, not per-database.

The lesson is that SQLite's concurrency model is file-level, not row-level. Workloads that need row-level concurrency should use a different store. Workloads that fit file-level concurrency should use `BEGIN IMMEDIATE` for write transactions and accept that readers may see a snapshot from before the write committed.

### 5.3 snapshot_refs view freeze

The `snapshot_refs` view freeze is documented in section 4.3 above. The failure mode is that a compatibility view — intended to let the frontend's SQL queries run unchanged after a schema normalization — became a performance trap when used on a hot path against a large database.

The fix had two parts. First, hot reference helpers in `ui/src/api/sqlJsQueryProvider.ts` stopped using `snapshot_refs` and now query normalized base tables directly. Second, a Web Worker layer was added to move `sql.js` stepping off the main thread (`Projects/2026/05/03/ARTICLE - SQLite in the Browser...`, "The Web Worker implementation").

The Web Worker does not fix the query plan. A bad SQL query still has to be fixed at the SQL level, because a Web Worker does not change the query plan. The Worker changes where synchronous SQLite stepping happens, so a slow query does not monopolize the main thread. The query rewrite and the Worker layer are complementary: the rewrite makes the query fast, the Worker makes the UI responsive while the query runs.

The lesson is that compatibility views are abstraction boundaries, not performance boundaries. A view that works for exploration or for small databases can become a UI freeze on a hot path against a large database. Hot paths must query normalized base tables directly, and view usage should be monitored with query-plan regression checks.

### 5.4 GOWORK=off in worktrees

The `codebase-browser` indexer uses Git worktrees to extract source at each commit in a review range. The Go AST extractor calls `golang.org/x/tools/go/packages.Load()` with patterns like `./cmd/...`. If the project's parent directory contains a `go.work` file (Go workspace mode), `packages.Load` walks up, finds the parent `go.work`, and refuses to load the worktree's packages because the worktree directory is not listed in `go.work`. The result is silently empty databases: only package rows are inserted, no symbols, files, or refs (`Projects/2026/05/02/ARTICLE - Squeezing a SQLite Database...`, "The bug we found along the way").

The bug was invisible in single-commit mode because single commits use `indexDirect` (indexing the working directory directly, which *is* listed in `go.work`). Only multi-commit mode triggered the worktree path, so only multi-commit mode produced empty databases.

The fix is one line:

```go
Env: append(os.Environ(), "GOWORK=off"),
```

Setting `GOWORK=off` in `packages.Config.Env` disables workspace mode during extraction, so `packages.Load` uses the local `go.mod` instead of the parent `go.work`.

The lesson is that silent empty databases are a failure mode of the canonical-store pattern. When the canonical store is built by an extractor, the extractor's environment must be controlled. A `go.work` file in a parent directory is not a SQLite concern, but it produces a SQLite symptom: a database that looks valid but is missing rows. The fix is to log extraction errors as warnings, not to swallow them with a "we tolerate packages with errors" comment.

### 5.5 Regex table extraction fragility

`go-minitrace` exposes a query endpoint that accepts user-supplied SQL against the normalized SQLite database. The goal is to allow analysis queries to access only the minitrace tables while blocking access to system tables such as `sqlite_master`.

The original implementation used a text-based approach: strip literals and comments, then use a regular expression to extract table names from `FROM` and `JOIN` clauses, and check each extracted name against an allowlist. This approach has two documented failure modes (`Projects/2026/06/08/ARTICLE - SQLite Authorizer and Query Safety...`, "Why This Analysis Exists"):

1. **Quoted identifiers.** A query like `SELECT name FROM "sqlite_master"` has its quoted identifier stripped to spaces by the literal remover, so the regex never sees it and the allowlist check is bypassed.
2. **CTE aliases.** A query like `WITH recent AS (...) SELECT * FROM recent` causes the regex to extract `recent` as a table name, which is then rejected even though the query only accesses `sessions` — the CTE body.

The fix is to move authorization from text-based parsing into the SQLite authorizer itself. The authorizer fires during statement preparation, not execution. It receives fully resolved table names including schema qualifiers, but never sees the runtime values bound to parameters. When the parser encounters `SELECT * FROM "sqlite_master"`, it has already recognized that the double-quoted identifier refers to the database object named `sqlite_master`. The authorizer receives `sqlite_master` as the table name argument, not the quoted token.

The authorizer pattern is defense in depth. Three layers execute sequentially:

1. **Text-based prefix check.** Validate that the query starts with `SELECT` or `WITH` and contains no semicolons. This provides fast rejection and a useful error message.
2. **SQLite authorizer.** Install a callback that denies `SQLITE_READ` for tables not in the allowlist, denies all write operations, and allows `SQLITE_SELECT` and `SQLITE_FUNCTION`.
3. **Read-only prepared statement check.** Use `SQLiteStmt.Readonly()` to verify that the query plan does not contain write opcodes.

The lesson is that any text-based approach to SQL parsing inherits the fragility of pattern matching over structured syntax. The SQLite parser already resolves identifiers, expands CTEs, and follows schema qualifiers. The authorizer operates on the parser's output, so it does not have the regex's blind spots. When a security boundary depends on knowing which tables a query touches, the authorizer is the correct mechanism.

## 6. A learning path

This section is for someone encountering the pattern for the first time. The goal is to build the mental model in the order that makes each step legible.

### Step 1: Read the Static SQL.js Codebase Browser article

Start with `Projects/2026/05/01/ARTICLE - Static SQL.js Codebase Browser - SQLite as the Browser Runtime.md`. This article is the cleanest instance of the product-boundary pattern. It shows the decision to ship the database itself to the browser rather than manufacturing a second, smaller, more fragile API-shaped export. Read sections 1 (the problem), 2 (the new mental model), 3 (the database is the product boundary), and 14 (what this project teaches).

The key insight to absorb: a static browser should not depend on knowing every question in advance. If the database already contains the facts, the browser should query the database, not a cache of predicted answers.

### Step 2: Read the Squeezing a SQLite Database article

Continue with `Projects/2026/05/02/ARTICLE - Squeezing a SQLite Database From 32 MB to 1.4 MB...`. This article shows the normalization invariant: store each unique entity once, and use narrow integer mapping tables to record which version appears in which commit. Read the "Root cause: snapshot-per-commit" and "The fix: normalized schema with mapping tables" sections.

The key insight to absorb: SQLite indexes on long string keys are expensive. Integer foreign keys shrink indexes by 10–20×. `WITHOUT ROWID` mapping tables are physically compact because the primary key is the storage order.

### Step 3: Read the SQLite in the Browser article

Read `Projects/2026/05/03/ARTICLE - SQLite in the Browser - Measuring and Fixing sql.js Performance in Static Code Review Sites.md`. This article shows the query-plan-as-frontend-architecture invariant. Read "The source page data path", "The better query shape", and "Working rules for SQLite in the browser".

The key insight to absorb: when SQLite runs in the browser, a slow query is a frozen page, not a slow backend. Measure query plans in native SQLite before blaming WebAssembly. The query planner is part of frontend performance.

### Step 4: Read the Minitrace API Redesign article

Read `Projects/2026/06/07/ARTICLE - Minitrace API Redesign - From Prototype Complexity to Normalized SQL and Fluent Builders.md`. This article shows the canonical-vs-derived invariant in the context of transcript analysis. Read "The problem: accidental complexity", "The solution: normalization + one API", and "Normalized schema".

The key insight to absorb: when the canonical store is well-shaped, parallel query surfaces collapse into one. The nine-table normalized schema replaced seven prototype surfaces (a JS trace query DSL, a typed lens registry, temporary SQL views, raw SQL endpoints, an API workbench, a guided walkthrough, a showcase endpoint) with one Goja builder over one schema.

### Step 5: Read the RAG Evaluation System article

Read `Projects/2026/05/27/ARTICLE - RAG Evaluation System - Workflow-Driven Retrieval Evaluation.md`. This article shows the two-database architecture and the identity-rules invariant. Read "State model and identity", "Chunking and the termination bug", and "CLI and HTTP adapter design".

The key insight to absorb: identity is the central design rule. A document is `(source_id, relative_path)`. A chunk is `(document_id, strategy_id, chunk_index)`. An embedding is `(chunk_id, strategy_id, provider, model, dimensions)` with a `text_hash` freshness check. Derived state is rebuilt or skipped based on stable keys.

### Step 6: Read the Durable Objects article

Read `Projects/2026/06/12/ARTICLE - Go Go Objects - Durable Objects Runtime on Goja.md`. This article shows the per-actor canonical storage form of the pattern. Read "The core mental model", "Storage: private SQLite per object", and "Design decisions that should remain explicit".

The key insight to absorb: one SQLite database per actor identity. Synchronous storage is deliberate because dispatch is already serialized per actor. Eviction removes the in-memory actor; the next dispatch recreates it from the same database file. The canonical store is the actor's durable state.

### Step 7: Read the SQLite Authorizer article

Read `Projects/2026/06/08/ARTICLE - SQLite Authorizer and Query Safety - Deep Dive Technical Analysis.md`. This article shows the correct boundary for query safety when accepting user-supplied SQL against a canonical store. Read "How the SQLite Parser Produces Authorizer Events", "The SQLITE_READ Action Code", and "Defense in Depth: Multiple Layers".

The key insight to absorb: text-based SQL parsing is fragile because it pattern-matches over structured syntax. The SQLite authorizer operates on the parser's output, so it correctly resolves quoted identifiers, CTEs, and schema qualifiers. When a security boundary depends on knowing which tables a query touches, the authorizer is the correct mechanism.

### Step 8: Read the Readwise Viewer article

Read `Projects/2026/05/21/PROJ - Readwise Viewer.md`. This article shows the canonical-store-with-disposable-derived-index form of the pattern. Read "SQLite and Go backend" and the architecture diagram.

The key insight to absorb: SQLite stays canonical; Bleve is a disposable derived index. When the search backend was migrated from FTS5 to Bleve, the migration touched the derived index without touching the canonical store. The API hydrates Bleve hits back through SQLite for canonical display data, because the derived index stores only what it needs for ranking.

## Key points

- **SQLite is the canonical store because it satisfies four constraints simultaneously**: portability as a single file, relational expressiveness without a server process, a concurrency model that fits a single-process host, and availability in the browser through WebAssembly. When all four constraints matter, no other store in the project record competes.
- **The product-boundary pattern treats the SQLite file as an interface, not an implementation detail.** Go builds the database; the browser, CLI, scripts, and LLMs all query the same file. The export is a compiler pass, not a server startup.
- **Canonical state has stable identity keys; derived state carries a freshness signal.** A document is `(source_id, relative_path)`. An embedding is `(chunk_id, strategy_id, provider, model, dimensions)` with a `text_hash`. Derived state can be deleted and rebuilt from canonical state without loss.
- **The two-database architecture separates corpus reads from workflow writes.** When a workflow engine and a corpus reader share a logical database and both have high-frequency access, split them into two physical databases. Cross-database joins happen in the consumer.
- **When SQLite runs in the browser, the query plan is frontend architecture.** A compatibility view that works for exploration can freeze the browser on a hot path against a large database. Hot queries must constrain by stable entity identity before expanding JSON or windowed views.
- **Failure modes are design drivers.** The chunking termination bug enforced explicit progress invariants. The `snapshot_refs` view freeze enforced direct base-table queries on hot paths. The `GOWORK=off` bug enforced environment control during extraction. The regex table extraction fragility enforced the authorizer as the correct boundary.
- **The pattern is not universal.** SQLite is the canonical store when the four constraints matter. When the canonical source is a directory of Markdown files (Retro Obsidian Publish) or a directory of source files (Codebase Browser before indexing), the same invariants apply to a different substrate: the source is read-only, derived artifacts are rebuildable, and the product boundary is the source itself.

## Closing

The canonical-store pattern recurs across T2, T5, T6, and T7 because it solves a problem that recurs across those topics: how to carry facts from build time to reading time without coupling the reader to the builder's predictions. SQLite is the tool that satisfies the four constraints (portability, relational expressiveness, single-process concurrency, browser availability) that make the pattern work. The product-boundary pattern is the move that makes the database file an interface, not an implementation detail.

The next bridge reports build on this substrate. Bridge 2 (Go-Backed JavaScript DSLs) shows how `goja-bleve` and the `mt.db()` builder expose the canonical store to JavaScript. Bridge 7 (Single-Binary Go + SPA) shows how the canonical store is served alongside a React frontend in one binary. Bridge 8 (Derived Rebuildable Artifacts) generalizes the canonical-vs-derived invariant to search indexes, generated React scaffolds, and static sites. The canonical store is the foundation; the other bridges are projections over it.
