---
title: "Transcript Analysis with go-minitrace — How We Do It"
aliases: [go-minitrace transcript analysis, minitrace workflow, coding-agent transcript analysis, transcript archaeology]
tags: [knowledge-base, tribal, go-minitrace, transcript-analysis, duckdb, agents]
status: active
type: knowledge-base
created: 2026-05-11
---

# Transcript Analysis with go-minitrace — How We Do It

> [!warning] Deprecated engine references — see migration guide
> This Tribal entry describes the workflow as "convert logs into `.minitrace.json`, query with DuckDB". The DuckDB backend (`go-minitrace query duckdb`) has been removed. The workflow shape is unchanged — convert, query, then read the transcript for evidence — but the query step now uses `go-minitrace query run` against the normalized SQLite schema (`sessions`, `turns`, `tool_calls` tables). The diagram line `DuckDB SQL / query catalog` should be read as `SQLite SQL / query catalog`. Full deprecation map and SQL rewrite table: [[ARTICLE - go-minitrace Query Engine Migration - DuckDB to Normalized SQLite]].

> [!summary]
> Our standard workflow for turning agent session transcripts into analyzable evidence: convert raw Pi/Codex/Claude logs into minitrace archives, query them with DuckDB/SQL, read sessions through structured transcript views, and preserve human judgments through annotations and exported reports.

## The pattern

A minitrace analysis starts from raw session logs, not memory or vibes. We convert logs into `.minitrace.json`, query with DuckDB, then drill back into the transcript when numbers point at something interesting.

```text
raw Pi / Codex / Claude transcripts
  -> go-minitrace discover / convert
  -> .minitrace.json archive
  -> DuckDB SQL / query catalog
  -> transcript reader / web UI / HTML export
  -> annotations, reports, follow-up tasks
```

The key rule is that SQL finds candidates, but the transcript provides evidence. A table can show 59 failed tool calls or a 3.3x read-ratio difference. The report is not trustworthy until the analyst opens the session and checks what the metric means.

## Why we do it this way

Agent work leaves behind too much evidence for manual review and too much context for raw metrics alone. A transcript is both conversation and execution trace: prompts, tool inputs, tool results, errors, file edits, commits, ticket operations, and timing. Plain text loses structure; rows lose narrative.

`go-minitrace` keeps both views alive. DuckDB gives fast aggregate questions: which tools failed, which files were touched, how long did sessions run, which model read more before editing. The transcript viewer gives the narrative view: what did the human ask, what did the agent infer, which tool call failed, and what changed afterward.

Annotations stay separate from raw session data while editing. SQLite is the working store, DuckDB the analytical read layer, and `.minitrace.json` the portable format updated by explicit sync. Review stays fast without turning the archive into a fragile mutable database.

## Where it lives

| Repo / area | Path | Use |
|-------------|------|-----|
| `corporate-headquarters/go-minitrace` | `cmd/go-minitrace/cmds/serve/` | web UI, session browser, transcript blocks, query API |
| `corporate-headquarters/go-minitrace` | `pkg/annotate/`, `cmd/go-minitrace/cmds/annotate/` | SQLite annotation store, CLI, JSON sync, DuckDB attach |
| `corporate-headquarters/go-minitrace` | `pkg/exporthtml/`, `web/src/export/` | self-contained HTML transcript export |
| Claude hook analytics repo | `.claude/hooks/log-to-sqlite.py`, `statusline.py`, `hook-events-server.py` | raw hook/token/transcript collection and exploration |

### Related PARC project reports

- [[PROJ - Claude Code Hook Events Logger - SQLite Analytics for Claude Sessions]] — capture layer: every hook event into SQLite with raw JSON preserved.
- [[PROJ - Claude Code Hook Analytics - Full-Stack Session Telemetry]] — joins hook events, token snapshots, and transcripts by `session_id` / `tool_use_id`.
- [[PROJ - go-minitrace - Web UI and Transcript Explorer]] — browser workflow: session list, transcript blocks, SQL workbench, query libraries.
- [[PROJ - go-minitrace - Annotation System]] — human-authored metadata layer over sessions, turns, and tool calls.
- [[PROJ - go-minitrace HTML Transcript Export - Reader Architecture]] — single-file reader export for offline review and handoff.
- [[PROJ - Nightly Transcript Review - 2026-04-16]] — repeatable nightly report pipeline from raw sessions to manager-readable summary.
- [[PROJ - Cross-Model Transcript Analysis - Minimax M2.7 vs GPT-5.4]] — model-comparison methodology using converted archives and DuckDB metrics.

## Common mistakes

### Mistake 1: Trusting metrics without reopening the transcript

The Cross-Model report found that MiniMax wrote 2.5x more test code and GPT-5.4 read 3.3x more files. Those facts are useful, but the conclusion came from reading code and transcript context too. Tool ratios are signals; they are not the final analysis.

### Mistake 2: Flattening away failure detail during conversion

The Nightly Transcript Review found a real Pi adapter bug: message-level `toolResult.isError` was not mapped into output success/failure correctly. The fix surfaced 59 failed tool calls in the Jellyfin session. If the converter drops failure shape, every downstream report becomes too optimistic.

### Mistake 3: Treating one storage layer as enough

The annotation system works because each storage layer has one job. SQLite is for fast writes. DuckDB is for read-side analysis. `.minitrace.json` is the portable artifact. Trying to make JSON handle every edit, or DuckDB handle every mutation, would make the workflow brittle.

### Mistake 4: Losing the join keys

Claude hook analytics depends on `session_id` across hook events, token snapshots, and transcript files, and on `tool_use_id` between hook events and transcript tool calls. If those keys are missing or normalized inconsistently, the UI cannot jump from a hook event to the exact transcript call that caused it.

### Mistake 5: Reconstructing transcript semantics only in the frontend

The go-minitrace web UI computes transcript blocks, badges, and artifact summaries on the backend. The frontend renders and navigates. If every browser component reinterprets raw transcript turns independently, the UI becomes inconsistent and hard to validate.

### Mistake 6: Exporting a reader that still depends on server state

The HTML export exists because a review artifact must be portable. A self-contained export embeds payload, JavaScript, and CSS in one file. If the export needs a running server, database, or external assets, it is not a durable handoff artifact.

## Variations

- **Hook analytics first** — Claude Code Hook Analytics starts at live hook capture, then joins SQLite rows with transcript files and token snapshots.
- **Archive-first analysis** — go-minitrace starts from converted `.minitrace.json` archives, then uses DuckDB and the web UI to inspect them.
- **Human review layer** — annotations add judgments that raw transcripts cannot infer: AI failure, user error, environment issue, success, question, follow-up.
- **Nightly management report** — a scheduled or repeatable workflow converts sessions, runs query bundles, and synthesizes a readable report for a date.
- **Cross-model comparison** — the same archive/query machinery compares agent behavior across models on the same task.
- **Self-contained export** — a single-session reader artifact for offline review, tickets, and handoffs.
