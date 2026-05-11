# KB Batch 10: Minitrace Analytics and Transcript-Analysis Workflows

## Batch scope

This batch processes the handoff document's **Batch F — Minitrace analytics and transcript-analysis workflows**.

Analyzed project reports:

1. [[PROJ - Claude Code Hook Analytics - Full-Stack Session Telemetry]]
2. [[PROJ - Claude Code Hook Events Logger - SQLite Analytics for Claude Sessions]]
3. [[PROJ - go-minitrace - Web UI and Transcript Explorer]]
4. [[PROJ - go-minitrace - Annotation System]]
5. [[PROJ - go-minitrace HTML Transcript Export - Reader Architecture]]
6. [[PROJ - Nightly Transcript Review - 2026-04-16]]
7. [[PROJ - Cross-Model Transcript Analysis - Minimax M2.7 vs GPT-5.4]]

## Executive summary

Batch F is one of the clearest Tribal clusters in the remaining backlog. The repeated pattern is not generic analytics; it is our concrete workflow for turning agent transcripts into reliable engineering evidence: capture or convert raw logs, preserve join keys, query with SQL/DuckDB, read the surrounding transcript before claiming meaning, annotate human judgments, and export durable review artifacts.

The batch created one new Tribal entry: [[Tribal/transcript-analysis-with-go-minitrace]]. It also reinforced several existing entries around SQL command surfaces and embedded web UIs, but the new minitrace entry is the main result.

## What was written

### New Tribal entry

- [[Tribal/transcript-analysis-with-go-minitrace]] — created because the same our-specific workflow appears across seven reports:
  - Hook Events Logger
  - Hook Analytics
  - go-minitrace Web UI
  - go-minitrace Annotation System
  - go-minitrace HTML Export
  - Nightly Transcript Review
  - Cross-Model Transcript Analysis

The entry documents the standard workflow: raw transcripts → minitrace archive / SQLite capture → DuckDB queries → transcript reader → annotations/reports/exports.

## What could / should be written later

### Tribal candidates promoted or reinforced

| Concept | Seen in | Status | Notes |
|---------|---------|--------|-------|
| **SQLite working store + DuckDB analytical read layer + JSON interchange** | Annotation System, Hook Analytics, go-minitrace Web UI | 3/3 — candidate, maybe variation of transcript-analysis entry | Strong storage pattern, but may be too narrow unless it appears outside transcript tooling. |
| **Backend transcript semantics, frontend navigation** | go-minitrace Web UI, Annotation System, HTML Export | 3/3 — candidate | Blocks, badges, indices, and annotation targeting are computed before the UI renders. |
| **Self-contained review artifact** | HTML Export, Nightly Review, handoff/report workflows | 2/3 | Exportable HTML / markdown reports as durable review objects. |
| **Silent telemetry hook failure** | Hook Events Logger, Hook Analytics | 2/3 | Hook must never interfere with agent execution; lose rows rather than hang sessions. |
| **Preserve raw JSON plus structured columns** | Hook Events Logger, Hook Analytics, minitrace conversion issues | 3/3 — candidate | Structured fields for fast queries, raw payload as escape hatch. |
| **Query-library as analysis workflow** | go-minitrace Web UI, Nightly Review, Cross-Model Analysis | 3/3 — partly covered by [[Tribal/sql-as-first-class-command-source]] | Stored SQL queries become repeatable investigations. |

### On-Ramp candidates

| Concept | Seen in | Status | What's missing from public docs |
|---------|---------|--------|--------------------------------|
| **DuckDB for local transcript analytics** | go-minitrace Web UI, Annotation System, Nightly Review, Cross-Model Analysis | 4/5 | DuckDB docs exist, but not the agent-transcript archive/query workflow. |
| **Claude Code hooks** | Hook Events Logger, Hook Analytics | 2/5 🌐 | Public hook docs do not cover durable SQLite telemetry and failure-safe hook behavior. |
| **Agent transcript evaluation methodology** | Nightly Review, Cross-Model Analysis, Hook Analytics | 3/5 🌐 | Existing eval material is benchmark-centric; our workflow is transcript-evidence-centric. |
| **SQLite JSON1 for telemetry queries** | Hook Events Logger, Hook Analytics | 2/5 | Docs exist, but not the raw-json-plus-indexed-columns pattern for tool telemetry. |

## What was updated / reinforced

- [[Tribal/sql-as-first-class-command-source]] is reinforced by go-minitrace query libraries, nightly query catalogs, and cross-model SQL scripts.
- [[Tribal/app-config-vs-command-config-separation]] is lightly reinforced by repeatable query roots, archive globs, preset dirs, and query dirs in the web UI.
- [[Tribal/js-defined-glazed-commands]] is adjacent but not directly reinforced; this batch is mostly SQL/query and transcript workflows rather than JS command definition.

## Per-project extraction

### 1. Claude Code Hook Analytics

**Role in batch**: full-stack observability system joining hook events, token snapshots, and transcripts.

**Tribal candidates**:
- Transcript analysis with go-minitrace / hook telemetry — created as [[Tribal/transcript-analysis-with-go-minitrace]].
- Join by `session_id` and `tool_use_id` — hook events, token snapshots, and transcript tool calls must preserve correlation keys.
- Silent telemetry hook failure — losing a row is acceptable; hanging a session is not.
- Raw JSON plus structured columns — indexed fields for common questions, raw payload for future fields.
- Retro/simple local web UI over SQLite telemetry — standard library server, localhost-only, read-only.

**On-Ramp candidates**:
- Claude Code hooks (2/5 🌐).
- SQLite JSON1 for telemetry queries (2/5).

### 2. Claude Code Hook Events Logger

**Role in batch**: capture-first substrate for Claude hook events.

**Tribal candidates**:
- Capture everything, extract common fields, preserve raw JSON — repeated in later analytics UI.
- Single-table sparse telemetry schema — one table across 18 event types with NULLs for non-applicable fields.
- Hook must be invisible to the user — WAL, busy timeout, schema-on-run, swallowed errors.

**On-Ramp candidates**:
- Claude Code hooks (2/5 🌐).
- SQLite WAL / busy timeout for local telemetry (1/5).

### 3. go-minitrace Web UI and Transcript Explorer

**Role in batch**: interactive archive exploration loop.

**Tribal candidates**:
- Backend transcript semantics, frontend navigation — backend computes session summaries, blocks, badges, and DTOs.
- DuckDB in-process archive query layer — browser talks to an API, not directly to DB.
- Query library roots with deterministic shadowing — built-in, preset, and saved query roots merge predictably.
- File-backed query hot reload without clobbering editor edits.

**On-Ramp candidates**:
- DuckDB for local transcript analytics (4/5).
- React + CodeMirror SQL workbench (1/5).

### 4. go-minitrace Annotation System

**Role in batch**: human judgment layer over transcripts.

**Tribal candidates**:
- SQLite working store + DuckDB analytical read layer + JSON interchange.
- Explicit sync from working store to portable artifact.
- Annotation UX as navigation problem — cards, transcript targets, inline markers, target focus.
- `sqlite_scanner` live attach instead of stale export tables.
- Output-root inference as file-layout contract.

**On-Ramp candidates**:
- DuckDB `sqlite_scanner` (1/5).
- Human annotation taxonomies for agent review (1/5).

### 5. go-minitrace HTML Transcript Export

**Role in batch**: portable single-session review artifact.

**Tribal candidates**:
- Self-contained review artifact — one HTML file with payload, JS, and CSS.
- JSON-driven export reader — Go computes the reader payload; browser renders it read-only.
- Script-tag-safe payload embedding — escape `<`, `>`, `&`, U+2028, U+2029.
- Export-time indices — annotation and search indices built once, not reconstructed by browser heuristics.

**On-Ramp candidates**:
- Self-contained HTML app export (1/5).
- Safe JSON embedding in HTML script tags (1/5).

### 6. Nightly Transcript Review — 2026-04-16

**Role in batch**: repeatable management-report workflow over Pi/Codex sessions.

**Tribal candidates**:
- Nightly transcript review pipeline — discover, convert, query, synthesize report, write Obsidian note.
- Transcript fidelity before management conclusions — Pi `isError` mapping bug changed failure counts materially.
- Report from query artifacts, not from raw transcript rereading every time.
- Calendar-day analysis with workstream spillover caveat.

**On-Ramp candidates**:
- Agent transcript evaluation methodology (3/5 🌐).
- DuckDB for local transcript analytics (4/5).

### 7. Cross-Model Transcript Analysis — Minimax M2.7 vs GPT-5.4

**Role in batch**: controlled model-comparison methodology.

**Tribal candidates**:
- Same-task cross-model transcript comparison — isolate model behavior from task differences.
- Tool-ratio behavioral metrics — read/edit/write/bash ratios as evidence, not conclusions.
- SQL metrics plus code-quality review — quantitative transcript analysis followed by qualitative source inspection.
- Explicit query scripts for reproducibility.

**On-Ramp candidates**:
- Agent transcript evaluation methodology (3/5 🌐).
- DuckDB JSON query gotchas (1/5).

## Candidate decisions

### Created now

- [[Tribal/transcript-analysis-with-go-minitrace]] — threshold exceeded; this is our-specific, non-lookupable workflow.

### Do not create yet

- **DuckDB for local transcript analytics** — 4/5 On-Ramp candidate; strong but just below threshold.
- **Backend transcript semantics, frontend navigation** — strong 3/3 Tribal candidate, but currently covered as a variation in the new minitrace entry.
- **Raw JSON plus structured columns** — strong telemetry candidate, but may be a subpattern rather than separate entry.

## Suggested index changes

Add Batch 10 entries for all seven projects and update campaign counts:

- Analyzed so far: 62
- Remaining: 105
- Tribal entries: 19

Update candidate tracking:

- Add [[Tribal/transcript-analysis-with-go-minitrace]] as created.
- Add DuckDB for local transcript analytics as 4/5 On-Ramp candidate.
- Add Backend transcript semantics / frontend navigation as 3/3 Tribal candidate but covered by the new entry for now.

## Follow-up review questions

1. Should **DuckDB for local transcript analytics** be written early as a domain seed, or wait for one more project?
2. Should **backend transcript semantics, frontend navigation** become a separate Tribal entry, or stay inside the minitrace transcript-analysis entry?
3. Should Claude Code hook telemetry become its own narrow Tribal entry after one more hook-based project?
