---
title: "go-minitrace Query Engine Migration: DuckDB to Normalized SQLite"
aliases:
  - go-minitrace DuckDB Deprecation Map
  - go-minitrace SQLite Migration Guide
  - go-minitrace query run Migration
  - Minitrace Stale DuckDB Articles
tags:
  - article
  - go-minitrace
  - sqlite
  - duckdb
  - deprecation
  - transcript-analysis
  - migration
status: active
type: article
created: 2026-07-15
repo: /home/manuel/code/wesen/corporate-headquarters/go-minitrace
skill_commit: 064f187
---

# go-minitrace Query Engine Migration: DuckDB to Normalized SQLite

`go-minitrace` has replaced its analytical backend. The legacy DuckDB engine — exposed through the `go-minitrace query duckdb` command family — has been removed. All SQL against converted `.minitrace.json` archives now runs on a normalized SQLite engine through the single command `go-minitrace query run`. This article is the authoritative deprecation map for the vault: it records which existing notes still describe the removed engine, marks them deprecated, and gives the concrete rewrites a reader needs to move their saved SQL onto the current engine.

The removal is not cosmetic. A reader who follows an older note verbatim will invoke a command that no longer exists. Because several of those notes are otherwise high-quality engineering references, the goal here is to keep them findable while making their staleness impossible to miss, rather than deleting them.

> [!warning] DuckDB commands are removed
> Any vault note instructing `go-minitrace query duckdb …` describes a command that no longer runs. Substitute `go-minitrace query run …` with the same `--archive-glob`, `--sql`, `--sql-file`, and `--preset` flags. The SQL syntax itself also changed: the normalized schema replaces JSON-blob access and `UNNEST` with real tables and columns. See the migration table at the end of this note.

> [!summary]
> - The DuckDB backend (`go-minitrace query duckdb`) is removed; the replacement is `go-minitrace query run`, a sandboxed read-only SQLite runner that builds its database from the archive glob automatically.
> - Seven vault notes still reference the removed engine and are marked **deprecated** below until their SQL is migrated; four clean notes are unaffected.
> - The normalized schema exposes real tables (`sessions`, `turns`, `tool_calls`, `annotations`, `metrics`, `files`, `events`, `attachments`, `handovers`) plus a `sessions_base` compatibility view for legacy session-level SQL.
> - `go-minitrace help query-duckdb` is now a migration guide, not a command reference; `help duckdb-query-recipes` and `help writing-duckdb-queries` redirect to `help query-recipes` and `help writing-queries`.

## Why this note exists

This vault contains a growing body of `go-minitrace` articles: playbooks, project reports, a knowledge-base entry, and an Institute guideline. They were written against different points in the tool's evolution. When the analytical engine changed, the older articles did not become wrong about transcript analysis as a discipline — their methodology, join-key discipline, and "SQL finds candidates, the transcript provides evidence" rule remain correct. They became wrong about the specific commands and SQL dialect needed to execute that methodology.

The useful response to that drift is not to rewrite every historical note. Historical notes are append-only records of how a piece of work was done. The useful response is a single, current, discoverable article that a reader lands on before following stale commands, that points at each affected note, and that carries the complete rewrite table. This is that article.

## What changed in the engine

`go-minitrace query run` builds or reuses a normalized SQLite database from the given archive glob and runs either a named preset or ad hoc SQL through a sandboxed read-only query runner. There is no separate import step and no long-lived database to manage. The command surface is:

```bash
go-minitrace query run \
  --archive-glob './analysis/*/active/*/*.minitrace.json' \
  --preset session-list
```

```bash
go-minitrace query run \
  --archive-glob './analysis/*/active/*/*.minitrace.json' \
  --sql-file ./queries/tool-frequency.sql \
  --max-rows 5000
```

The available flags are `--sql`, `--sql-file`, `--preset`, `--archive-glob` (repeatable), `--max-rows`, `--max-cell-chars`, and `--timeout-ms`. The built-in presets are `session-list`, `framework-summary`, `annotations`, `timing-analysis`, `tool-operation-breakdown`, `tool-failures`, `read-ratio-distribution`, `file-operations`, and `file-timeline`.

The schema is normalized into real tables rather than a single JSON blob. The tables a reader will query most are:

- `sessions` — one row per session, with real columns such as `session_id`, `title`, `agent_framework`, `model`, `working_directory`, `started_at`, `ended_at`, `turn_count`, `tool_call_count`, `read_count`, `modify_count`, `create_count`, `execute_count`, and `git_branch`.
- `turns` — one row per message, joined to `sessions` by `session_id` and ordered by `turn_index`; columns include `role`, `content`, `timestamp`, `model`, `thinking`, and per-turn token usage.
- `tool_calls` — one row per tool invocation, joined by `session_id` and `emitting_turn_index`; columns include `tool_name`, `operation_type`, `command`, `file_path`, `success`, `error`, `duration_ms`, and `result`.

The remaining tables are `annotations`, `metrics`, `files`, `events`, `attachments`, and `handovers`. A `sessions_base` compatibility view is preserved so that legacy session-level SQL using the `->` / `->>` JSON arrow operators continues to work; per-tool-call and per-turn SQL must move to the `tool_calls` and `turns` tables. The sandbox blocks `sqlite_master`, so schema introspection uses `go-minitrace help minitrace-schema` or the `db.tables()` / `db.schema()` helpers from a JavaScript command handler.

## How the skill was updated

The `go-minitrace-transcript-analysis` skill was corrected after a real session that located the go-go-goja PR #95 work. The session exposed seven concrete defects in the skill, all now fixed in commit `064f187` in the skill repository at `/home/manuel/.codex/skills/go-minitrace-transcript-analysis`:

- `query duckdb` references throughout `SKILL.md` were replaced with `query run`.
- The JavaScript command example was rewritten to the current builder-composed API (`mt.db().RuntimeArchives().QueryCommandDefaults().Build()` → `db.query()`), replacing the removed `mt.query()` / `mt.tableName` helpers.
- The workspace-cwd blind spot was documented: `discover pi --cwd-contains <repo>` returns nothing for sessions launched from a workspace directory, because it matches the recorded `cwd` rather than the topic of conversation.
- `convert pi --source-list` was documented as the preferred method for converting a narrow subset of sessions.
- `references/queries.md` was fully rewritten for the normalized schema with verified column names, and `scripts/query_minitrace.sh` was fixed to call `query run`.

Readers who learned the workflow from the skill before this commit should re-read `SKILL.md` and `references/queries.md`.

## Deprecation map of vault articles

Each entry below was checked by grepping the note for DuckDB references and confirming against the current tool. The status column states whether the note's commands still run as written.

| Article | Status | DuckDB refs | Action |
| --- | --- | --- | --- |
| [[Code Review with go-minitrace]] | **Deprecated** | 5 | Uses `go-minitrace query duckdb` in four code blocks. Methodology sound; commands must be rewritten. |
| [[transcript-analysis-with-go-minitrace]] | **Deprecated** | 10 | Tribal knowledge-base entry. Workflow diagram and prose say "DuckDB". Rewrite for SQLite. |
| [[KB-BATCH10-minitrace-transcript-analysis]] | **Deprecated** | 13 | Batch summary. References "DuckDB queries" and "DuckDB analytical read layer" throughout. |
| [[PROJ - go-minitrace - Annotation System]] | **Deprecated** | 24 | Heaviest DuckDB usage. SQL examples and the SQLite-working-store / DuckDB-read-layer split need migration. |
| [[PROJ - go-minitrace - Web UI and Transcript Explorer]] | **Deprecated** | 16 | SQL workbench and query-library examples use DuckDB dialect. |
| [[PROJ - Nightly Transcript Review - 2026-04-16]] | **Deprecated** | 5 | Nightly query bundle uses `query duckdb`. |
| [[PROJ - Cross-Model Transcript Analysis - Minimax M2.7 vs GPT-5.4]] | **Deprecated** | 5 | Model-comparison metrics use DuckDB queries. |
| [[PROJECT REPORT - go-go-goja - Personal Inbox Auth, Programmatic Access, and Device Login]] | Current | 0 | No query commands. Unaffected. |
| [[PROJECT REPORT - go-go-goja Token Families and Device Authorization Flow - Deep Dive]] | Current | 0 | No query commands. Unaffected. |
| [[PROJ - go-minitrace HTML Transcript Export - Reader Architecture]] | Current | 0 | Export-focused; no SQL. Unaffected. |
| [[PROJ - Claude Code Hook Analytics - Full-Stack Session Telemetry]] | Current | 0 | Uses its own SQLite capture layer, not the minitrace query engine. Unaffected. |
| [[PROJ - Claude Code Hook Events Logger - SQLite Analytics for Claude Sessions]] | Current | 0 | Same — independent SQLite hooks. Unaffected. |

A note marked **Deprecated** here is deprecated specifically with respect to its `go-minitrace` command and SQL examples. Its analysis conclusions, join-key discipline, and process guidance remain valid. Readers should treat the command snippets as pseudocode to be re-expressed in the normalized schema, not as copy-paste instructions.

## What to do when you land on a deprecated note

When a reader opens one of the deprecated articles, the intended path is:

1. Read the note for its methodology and conclusions. These are still the most valuable part.
2. Stop before running any `go-minitrace query duckdb` block.
3. Re-express the query using `go-minitrace query run` and the normalized schema, using the migration table below.
4. If the note is one you own and use regularly, migrate its SQL in place and drop the deprecation status here.

The deprecation is mechanical, not intellectual. A query that counted tool calls via `UNNEST(tool_calls)` becomes a query that joins the `tool_calls` table. A query that read `metrics->>'turn_count'` becomes a query that reads `sessions.turn_count`. The analysis does not change.

## Migration table: DuckDB to normalized SQLite

| Legacy DuckDB pattern | Normalized SQLite equivalent |
| --- | --- |
| `go-minitrace query duckdb` | `go-minitrace query run` |
| `environment->>'agent_framework'` | `sessions.agent_framework` column |
| `metrics->>'turn_count'` | `sessions.turn_count` (more rollups in the `metrics` table) |
| `->` / `->>` on other blob columns | prefer the real `sessions` columns; unchanged SQL keeps working against the `sessions_base` compat view |
| `UNNEST(tool_calls) AS t(tc)` | query the `tool_calls` table, join `USING (session_id)` |
| `UNNEST(turns) WITH ORDINALITY` | query the `turns` table (`turn_index` column) |
| `LEFT(x, n)` | `substr(x, 1, n)` |
| `CAST(x AS DATE)` | `date(x)` |
| `REPLACE(CAST(json_extract(...) AS VARCHAR), '"', '')` | plain `json_extract(...)` — SQLite returns unquoted values |
| `DESCRIBE` / `SHOW TABLES` | `db.schema()` / `db.tables()` from JS (the sandbox blocks `sqlite_master`), or `go-minitrace help minitrace-schema` |
| `read_json(...)` | not needed — the database is built from archives automatically |

## Worked example: the topic-grep query

A common task that appears across the deprecated notes is "find the sessions that mention a topic." Under DuckDB this required unnesting turns from the session blob. Under the normalized schema it is a direct table query:

```sql
SELECT session_id, turn_index,
       substr(coalesce(content, ''), 1, 160) AS snippet
FROM turns
WHERE role = 'user'
  AND (content LIKE '%go-go-goja%' OR content LIKE '%xgoja%')
ORDER BY session_id, turn_index;
```

This pattern — query the `turns` table directly, filter on `role = 'user'`, and order by `turn_index` — is the replacement for every "search the transcript" recipe that previously used `UNNEST`.

## Working rules

- Treat any `go-minitrace query duckdb` instruction in the vault as a stale command. The command is removed; substitute `go-minitrace query run`.
- Prefer real columns over JSON-blob access. If a column exists on `sessions`, `turns`, or `tool_calls`, read the column rather than `json_extract` against `raw_json`.
- When migrating a note, preserve its conclusions and rewrite only its commands and SQL. The deprecation is about execution, not about the analysis itself.
- Keep this deprecation map current. When a deprecated note is migrated, move it from the deprecated set to the current set in the table above.
- For new `go-minitrace` notes, link to this article so future readers hit the current engine documentation first.

## Related notes

- [[Code Review with go-minitrace]] — deprecated; post-session analysis playbook.
- [[transcript-analysis-with-go-minitrace]] — deprecated; the Tribal knowledge-base entry for the standard workflow.
- [[KB-BATCH10-minitrace-transcript-analysis]] — deprecated; batch summary of the transcript-analysis cluster.
- [[PROJ - go-minitrace - Annotation System]] — deprecated; heaviest DuckDB usage.
- [[PROJ - go-minitrace - Web UI and Transcript Explorer]] — deprecated; SQL workbench examples.
- [[PROJ - Nightly Transcript Review - 2026-04-16]] — deprecated; nightly query bundle.
- [[PROJ - Cross-Model Transcript Analysis - Minimax M2.7 vs GPT-5.4]] — deprecated; cross-model metrics.
- [[PROJECT REPORT - go-go-goja - Personal Inbox Auth, Programmatic Access, and Device Login]] — current; the PR #95 deep dive that motivated re-checking the engine.
- [[PROJECT REPORT - go-go-goja Token Families and Device Authorization Flow - Deep Dive]] — current; earlier auth deep dive.
- [[PROJ - go-minitrace HTML Transcript Export - Reader Architecture]] — current; export architecture, no SQL.
- [[ARTICLE - Transcript RAG Playground - Conversation Units, Immutable Generations, and Embedding Identity]] — current; composes `go-minitrace` into a JavaScript retrieval system; uses the normalized engine correctly.
