---
title: "Analyzing Agent Tool-Calling Behavior with go-minitrace"
aliases:
  - go-minitrace transcript analysis playbook
  - mt.db() normalized transcript analysis
tags:
  - article
  - playbook
  - go-minitrace
  - transcript-analysis
  - go-go-goja
  - duckdb
  - sqlite
  - data-analysis
status: active
type: article
created: 2026-06-22
repo: /home/manuel/code/wesen/2026-06-22--analyze-tool-calls-gemma4
---

# Analyzing Agent Tool-Calling Behavior with go-minitrace

This article is a deep-dive technical analysis of one workflow: taking a raw agent transcript, turning it into a queryable database, and writing a repository of structured queries that explain how a model drove its tools during a single session. It documents the concrete pipeline used to analyze two Pi sessions — one driven by `gpt-5.5` coding a Discord bot, one driven by `gemma4:e4b` searching for vacation rentals — and the report-generation layer built on top of those queries.

The target reader writes Go or JavaScript, works with LLM agent transcripts, and wants to understand agent behavior from evidence rather than intuition. Nothing here is speculative; every number in the worked example comes from a named query that runs against a normalized database built from the transcript.

> [!summary]
> - `go-minitrace convert` turns a native agent JSONL transcript into a canonical minitrace archive; `mt.db()` materializes that archive into **normalized relational tables** (`sessions`, `turns`, `tool_calls`, `files`, `events`, `metrics`) inside an in-process SQLite database.
> - Analysis is a **repository of structured JS query commands** over those tables — not hand-written ad-hoc SQL. Each question (tool frequency, transition matrix, retry loops, timing) becomes a named, runnable verb.
> - Three JS access layers exist (`UNNEST` over DuckDB JSON arrays, `mt.queryOne("SELECT *")` document pull, `mt.db()` normalized tables). The normalized-table layer is the only one that is both robust and ergonomic for single-session analysis.
> - The report layer is a self-contained HTML file: an HTML template plus embedded CSS and JavaScript, with the transcript and statistics inlined as JSON. Markdown rendering of model answers uses `marked` and `DOMPurify` from a CDN.

## Why this note exists

Agent transcripts are verbose. A one-hour session is hundreds of thousands of tokens of conversation, tool inputs, and tool outputs, spread across thousands of JSON lines. Reading them linearly answers "what happened" but not "how does this model behave." Questions such as "does this model batch tool calls?", "which tool does it over-use?", and "how long does it actually wait between calls?" require aggregation, and aggregation requires a database.

This note preserves the reusable engineering knowledge from building such an analysis pipeline twice, so that the next transcript can be analyzed without re-deriving the schema, the query shapes, or the report structure. The triggering project is the `2026-06-22--analyze-tool-calls-gemma4` repository, but the pattern generalizes to any agent transcript that `go-minitrace` can convert.

## The pipeline at a glance

The workflow has four stages. Each stage is a distinct responsibility with a distinct artifact.

```mermaid
flowchart LR
  A["Pi JSONL\ntranscript"] -->|go-minitrace convert pi| B["minitrace archive\n(.minitrace.json)"]
  B -->|mt.db().RuntimeArchives| C[("normalized SQLite\nsessions/turns/tool_calls/files/events/metrics")]
  C -->|JS query repository| D["structured stats\n(JSON per command)"]
  D -->|Python driver\n+ HTML template| E["self-contained\nHTML report"]
```

The stages and their artifacts:

| Stage | Tool | Input | Output |
|-------|------|-------|--------|
| Convert | `go-minitrace convert pi` | `.jsonl` transcript | `.minitrace.json` archive |
| Materialize | `mt.db()` (in-process) | archive glob | normalized SQLite tables |
| Query | JS query repository | normalized tables | JSON statistics per command |
| Render | Python driver + HTML template | JSON stats + transcript | self-contained `.html` |

The first two stages are provided by `go-minitrace`. The last two are project-specific and are the substance of this article.

## The canonical transcript format and why conversion exists

Every agent framework stores its sessions differently. Pi records newline-delimited JSON where each line is a typed event: `session`, `message`, `model_change`, `thinking_level_change`. A `message` carries a `role` (`user`, `assistant`, `toolResult`) and a `content` array of typed blocks (`text`, `thinking`, `toolCall`). The tool-call block in Pi is typed `toolCall` with `name` and `arguments` fields; the result is a separate `toolResult` message keyed by `toolCallId`.

This shape is close to, but not identical to, Anthropic's `tool_use` / `tool_result` convention, and it is unrelated to Codex or Claude Code's on-disk layouts. A query written against the raw Pi JSONL would not work on a Codex transcript, and vice versa. `go-minitrace convert` exists to erase that difference: each framework adapter reads its native format and emits the same canonical minitrace archive.

The archive is a single JSON document conforming to `minitrace-v0.2.0`. Its top-level fields are stable across sources:

```
id, schema_version, profile, quality, title, classification,
provenance, flags, environment, operational_context, timing,
turns[], tool_calls[], metrics, ...
```

The `tool_calls` array is the analytical center of gravity. Each entry has a normalized shape regardless of source framework:

```json
{
  "id": "call_...",
  "emitting_turn_index": 1,
  "timestamp": "2026-05-01T20:09:25.723Z",
  "tool_name": "read",
  "operation_type": "READ",
  "input": { "file_path": "...", "command": null, "arguments": {...} },
  "output": { "success": true, "result": "...", "error": null, "exit_code": null, "duration_ms": null },
  "context": { "position_in_session": 0.0, "tools_before": [...], "time_since_last_user": 49.7 }
}
```

Two fields matter for later sections. First, `operation_type` is a normalized enum (`READ`, `MODIFY`, `NEW`, `EXECUTE`, `DELEGATE`, `OTHER`) assigned by the adapter — it lets you ask "how much does this agent read before acting?" without parsing tool arguments. Second, the `output` object's `duration_ms` and `exit_code` are frequently **not populated** by adapters; the Pi adapter leaves both null. This single fact determines how timing analysis must be done, as the section on timing explains.

## Stage 1: Conversion

Conversion is a single command. For a Pi transcript:

```bash
go-minitrace convert pi \
  --source-session ./2026-06-22T16-11-33-998Z_019ef019-f6ee-7500-b781-cc1a7486bac5.jsonl \
  --output-dir ./analysis
```

The output lands at `analysis/active/YYYY-MM/<id>.minitrace.json`, plus a `manifest.json` at the output root. The manifest is advisory — repeated `--source-session` calls into the same directory can leave it reflecting only the last invocation — but the `.minitrace.json` files themselves are always queryable. For analysis, query the file glob directly rather than trusting the manifest.

The converter assigns a quality tier (A, B, or C) based on content richness. A session needs rich conversation plus tool I/O plus more than ten tools and more than five turns to earn an A. Both worked examples here are quality A.

The two sessions used throughout this article, after conversion:

| Session | Model | Task | Turns | Tool calls | Duration | Cost |
|---------|-------|------|------:|-----------:|---------:|-----:|
| `019de528…` | gpt-5.5 (openai-codex) | Discord bot coding | 201 | 181 | 49 min | $12.93 |
| `019ef019…` | gemma4:e4b (Ollama) | Liguria vacation search | 68 | 16 | 48 min | $0.00 |

They are deliberately different in character. The gpt-5.5 session is a long coding session with file and shell tools. The gemma4 session is a short conversational web-search session with browser tools run on a local model. The same query repository analyzes both without code changes; only the rendered reports differ.

## Stage 2: Three ways to query an archive, and which one to use

This section is the most important in the article because it records a dead end and the reason for it. A reader who skips to the queries will repeat the dead end.

An archive stores `turns` and `tool_calls` as JSON arrays nested inside one document. There are three ways to get rows out of that structure from JavaScript. They are not equivalent.

### Approach 1: UNNEST over DuckDB JSON arrays (fragile)

The archive can be loaded into DuckDB as a single-row table and the arrays unnested with DuckDB's `UNNEST(...) AS t(call)` plus JSON arrow operators:

```sql
SELECT call->>'tool_name' AS tool, COUNT(*) AS uses
FROM sessions_base, UNNEST(tool_calls) AS t(call)
GROUP BY tool
ORDER BY uses DESC;
```

This works for simple aggregates and runs correctly through `go-minitrace query duckdb --sql-file`. It fails, however, inside the JavaScript command-handler path. Certain `WHERE` predicates over the unnested column — for example `WHERE call->>'timestamp' IS NOT NULL` or `WHERE turn->>'role' = 'assistant'` — trigger a DuckDB cast-inference error surfaced as:

```
Conversion Error: Failed to cast value to numerical: {"id":"call_..."}
when casting from source column call
```

The identical SQL run through the DuckDB CLI path succeeds. The failure is specific to the wrapping that `mt.query()` applies inside the Goja runtime. The practical consequence is that any command that filters on an unnested JSON column is one predicate change away from breaking, with no compile-time signal. This is not a usable foundation for a query repository.

### Approach 2: Document pull (robust but unergonomic)

A workaround that avoids `UNNEST` entirely is to pull the whole document once and iterate the arrays in JavaScript:

```js
const mt = require("minitrace");
const doc = mt.queryOne(`SELECT * FROM ${mt.tableName}`);
for (const call of doc.tool_calls) { ... }
```

`mt.queryOne("SELECT *")` returns `tool_calls` and `turns` as real JavaScript arrays — verified as `array[181]` and `array[201]` for the gpt-5.5 session. Every field on every element is a plain JavaScript value. This sidesteps the UNNEST cast quirk completely and is robust for single-session analysis.

The cost is that the relational work moves into JavaScript. Transition matrices, gap-and-island run detection, and percentile timing all become hand-written loops. The resulting code is correct but longer, harder to review, and harder to reuse across questions. It also couples every command to the assumption that exactly one session is loaded: `queryOne` returns the first row, so a glob that matches multiple sessions silently analyzes only one.

### Approach 3: Normalized tables via `mt.db()` (the right answer)

The `mt.db()` API, available in `go-minitrace` from June 2026 onward, materializes the archive into a normalized relational schema inside an in-process SQLite database. The JavaScript surface is a fluent builder:

```js
const mt = require("minitrace");
const db = mt.db().RuntimeArchives().QueryCommandDefaults().Build();
try {
  return db.query(`SELECT tool_name, COUNT(*) AS n FROM tool_calls GROUP BY tool_name`);
} finally {
  db.close();
}
```

The schema is first-class relational. There is no JSON extraction and no `UNNEST`. The ten tables, with the row counts for the gemma4 session:

| Table | Rows | Purpose |
|-------|-----:|---------|
| `sessions` | 1 | One row per session, with model, framework, timing, token totals |
| `turns` | 201 / 68 | One row per conversational turn, with role, tokens, thinking |
| `tool_calls` | 181 / 16 | One row per tool invocation, typed columns for success/error/command |
| `turn_tool_calls` | 181 / 16 | Join table: which turn emitted which call, with ordinal |
| `files` | 103 / 0 | One row per file touch extracted from tool calls |
| `events` | 383 / — | Derived renderable timeline rows (one per user/assistant/tool event) |
| `metrics` | 1 | Pre-computed session metrics (cost, ratios, token sums) |
| `annotations` | 0–1 | Human or automated annotations |
| `attachments` | 0 | Media attached to events |
| `handovers` | 0 | Session handover documents |

The `tool_calls` table has typed columns where they matter most: `success` (boolean), `error` (text), `command` (text), `file_path` (text), `operation_type` (enum text), `emitting_turn_index` (integer), `timestamp` (text), `duration_ms` (integer, often null). This is what makes the queries in the next section short and declarative.

The `mt.db()` layer is the only approach that is both robust and ergonomic. The rest of this article assumes it. The dead end recorded above is worth knowing because the older APIs are still present in the binary and in documentation; a reader who starts with the UNNEST recipes in the embedded help will hit the same wall.

### A note on module loading

`require("minitrace")` is not a default-registry module in the current `go-minitrace` release. Unlike `goja-text`'s `template` module, the `minitracejs` package has no `init()` that calls `modules.Register(...)`. It is wired through its provider package and the `providerapi.ProviderRegistry`, which the generated `xgoja` host uses automatically. A hand-written Go host that boots a runtime with `engine.NewRuntimeFactoryBuilder().Build()` will find `fs`, `console`, and `template` but not `minitrace`. The `WithModules(engine.NativeModuleRegistrar{...})` workaround loads `minitrace` but, because explicit module registration is exclusive rather than additive, drops the default modules. This is a known gap filed as `go-go-golems/go-minitrace` issue #20.

## Stage 3: A query repository, not a pile of SQL

The analysis layer is a directory of JavaScript files that `go-minitrace` discovers and turns into CLI commands. Each file declares one or more verbs; each verb is a named question with typed filter fields and a SQL or JavaScript body. The repository for this project lives at `ttmp/2026/06/22/TOOL-CALLS-GEMMA4--.../scripts/queries/` and contains 14 JS files organized by concern:

```
queries/
├── lib/
│   ├── normdb.js          # shared mt.db() loader: withDb(fn) builds + closes the handle
│   └── helpers.js         # percentile, share-of-total, bash classifier, path normalize
├── overview/
│   └── session-snapshot.js
├── tools/
│   ├── tool-frequency.js   # counts, operation-mix
│   ├── tool-errors.js
│   ├── bash-anatomy.js
│   ├── file-activity.js
│   ├── timeline.js         # tool-timeline
│   ├── tool-timing.js      # inter-call-gaps, turn-latency
│   ├── tool-sequence.js    # tool-transitions, per-turn-batching, sequential-runs
│   ├── retries-loops.js    # repeated-calls, retry-chains
│   └── cost-tokens.js      # token-distribution
└── debug/
    ├── col-probe.js        # schema introspection
    └── schema-probe.js
```

A command file has three parts: a `__section__` declaring the filter fields, one or more handler functions, and `__verb__` declarations that bind handlers to CLI names. The shared loader concentrates the `mt.db()` lifecycle into one place so handlers never leak a handle:

```js
// lib/normdb.js
function withDb(fn) {
  const mt = require("minitrace");
  const db = mt.db().RuntimeArchives().QueryCommandDefaults().Build();
  try {
    return fn(db, mt);
  } finally {
    db.close();
  }
}
exports.withDb = withDb;
```

Every handler follows the same shape: open the database, run one or more SQL queries, post-process in JavaScript only when SQL is the wrong shape, return rows. The discipline of closing the handle in `finally` matters because the database is an in-process SQLite file; an unclosed handle holds the connection.

The queries below are the substantive ones. Each is shown in its essential form, with the full version in the repository.

### Tool frequency and operation mix

The simplest question is "which tools does this model use, and how often." Against the normalized table it is a single `GROUP BY`:

```sql
SELECT tool_name AS tool,
       COUNT(*) AS uses,
       SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) AS failed
FROM tool_calls
GROUP BY tool_name
ORDER BY uses DESC;
```

For the gemma4 session the result is three rows: `show_user_in_browser` 10, `web_search` 5, `fetch_content` 1. For the gpt-5.5 session it is four: `bash` 78, `read` 54, `edit` 31, `write` 18. The query is the same; the difference in behavior is visible immediately. The operation-mix query pivots `operation_type` per tool and shows that gemma4's tools are all `OTHER` (web tools have no file-system operation type) while gpt-5.5's split cleanly: `read` is 100% READ, `edit` is 100% MODIFY, `bash` is 81% EXECUTE.

### Sequencing: transitions, batching, runs

Three questions about how tools follow one another. Each uses a standard SQL window-function pattern.

**Batching** — how many tool calls the model emits per assistant turn — reads the join table:

```sql
SELECT turn_index AS idx, COUNT(*) AS n
FROM turn_tool_calls
GROUP BY turn_index
ORDER BY turn_index;
```

Aggregating the `n` values into a histogram answers the parallelism question. Both worked sessions are overwhelmingly sequential: gpt-5.5 emits one call in 95.7% of tool turns (max batch 5, all reads), gemma4 emits one call in 100% of tool turns. Neither model parallelizes writes or executions.

**Transitions** — the tool-to-tool Markov chain — uses `LAG()` over the time-ordered calls:

```sql
WITH ordered AS (
  SELECT tool_name AS to_tool,
         LAG(tool_name) OVER (ORDER BY timestamp, tool_call_id) AS from_tool
  FROM tool_calls
)
SELECT from_tool, to_tool, COUNT(*) AS count
FROM ordered
WHERE from_tool IS NOT NULL
GROUP BY from_tool, to_tool
ORDER BY count DESC;
```

The dominant transition for gpt-5.5 is `bash -> bash` (26% of transitions); for gemma4 it is `show_user_in_browser -> show_user_in_browser` (47%). Both indicate same-tool momentum, but of different kinds: gpt-5.5 chains shell commands, gemma4 chains result presentations.

**Sequential runs** — the longest streaks of the same tool back-to-back — is the classic gap-and-island problem. The islands are detected by subtracting a per-tool row number from the global row number:

```sql
WITH ordered AS (
  SELECT tool_name AS tool, emitting_turn_index AS start_turn,
         ROW_NUMBER() OVER (ORDER BY timestamp, tool_call_id) AS rn,
         ROW_NUMBER() OVER (PARTITION BY tool_name ORDER BY timestamp, tool_call_id) AS tool_rn
  FROM tool_calls
)
SELECT tool, MIN(start_turn) AS start_turn, COUNT(*) AS run_length
FROM ordered
GROUP BY tool, (rn - tool_rn)
HAVING COUNT(*) >= 2
ORDER BY run_length DESC;
```

The expression `rn - tool_rn` is constant within a contiguous run of the same tool and changes at every boundary, so grouping by it collapses each run into one row. For gpt-5.5 this surfaces a 15-call `read` streak at turn 16 — a deep file-exploration burst before the model proposes an implementation. This is exactly the kind of behavioral signal that linear reading would not reveal.

### Timing derived from timestamps

Tool-call timing requires care because of the data-quality caveat noted earlier: the Pi adapter does not populate `output.duration_ms` or `output.exit_code`. Verified across the gpt-5.5 session, both fields are null for all 181 calls. There is no direct measure of how long a tool took to execute.

The workaround is to derive timing from wall-clock timestamps. The gap between consecutive tool-call timestamps is an **upper bound** on execution latency: it includes tool execution but also the model's reasoning time before the next call, and for interactive sessions it includes the user's think-time. Stating this caveat explicitly in the report is necessary to avoid overstating precision.

```sql
SELECT tool_name AS tool, timestamp AS ts
FROM tool_calls
ORDER BY timestamp, tool_call_id;
```

The per-tool gap percentiles are computed in JavaScript from the ordered rows. For the gemma4 session the inter-call gaps are large and human-paced: `web_search` averages 229s with a maximum of 804s (13 minutes), consistent with a user reviewing vacation listings between turns. For gpt-5.5 the gaps are tighter: `read` p50 is 5.1s, `bash` p95 is 120s. The number means "time from one call to the next," not "time the tool ran," and the report says so.

Per-turn latency — time from one assistant turn to the next — brackets a batch of tool execution plus the following model turn and is the cleanest proxy for how long a step took. For gemma4 the per-turn latency p50 is 3.5s; for gpt-5.5 it is 7.2s. These numbers are model-side and reflect how quickly the model produced the next turn.

### Errors, retries, and repetition

Errors read directly from the typed `success` and `error` columns:

```sql
SELECT tool_name AS tool, COUNT(*) AS failed, COUNT(DISTINCT error) AS distinct_errors
FROM tool_calls
WHERE success = 0
GROUP BY tool_name
ORDER BY failed DESC;
```

For gpt-5.5 all 15 failures are in `bash` (10), `edit` (4), and `write` (1); gemma4 has zero failures. Inspecting the `error` text shows that gpt-5.5's edit failures are the "oldText must be unique" ambiguity error, and its bash failures are `docmgr` argument mistakes and Go first-build downloads.

Retry detection — the same tool called back-to-back with the same key argument, one of which failed — is a `LAG()` over a computed signature:

```sql
WITH ordered AS (
  SELECT tool_name AS tool, success AS ok,
         COALESCE(command, file_path, '') AS key,
         LAG(tool_name) OVER w AS prev_tool,
         LAG(COALESCE(command, file_path, '')) OVER w AS prev_key,
         LAG(success) OVER w AS prev_ok
  FROM tool_calls
  WINDOW w AS (ORDER BY timestamp, tool_call_id)
)
SELECT tool,
       CASE WHEN prev_ok = 0 THEN 1 ELSE 0 END AS looks_like_retry
FROM ordered
WHERE prev_tool = tool AND prev_key = key AND key != '';
```

The `WINDOW w AS (...)` clause names the window frame so three `LAG()` calls share it without repeating the ordering. For gpt-5.5 this finds 4 consecutive duplicate calls and **zero** error-then-retry loops: when a call fails, the model changes approach (it re-reads the file, then edits with more context) rather than blindly retrying. The absence of retry loops is itself a finding worth reporting.

### Token distribution and cost

Per-turn token usage lives on the `turns` table (`output_tokens`, `input_tokens`, `cache_read_tokens`). Session cost lives on `metrics`. Per-call cost attribution is not available in the schema, so the report reports session cost as an anchor number and token usage per turn.

The interesting derived quantity is the shape of the output-token distribution. For gpt-5.5 the median assistant turn emits 145 tokens but the mean is 360 and the max is 3388 — a heavily right-skewed distribution where most turns are short tool-call emissions and a few are long planning turns. Deciling the sorted output-token counts and plotting the average per decile shows whether output grows over the session (context bloat) or stays flat. Both worked sessions are flat.

## Stage 4: The report layer

The queries produce JSON. A human-readable report turns that JSON into a document. The design goal is a single self-contained HTML file that anyone can open without a server.

### The render pipeline

A Python driver (`build-reports.py`) runs the full pipeline for every `.jsonl` in the repo root. For each transcript:

1. Convert to a per-session minitrace archive under `analysis/<slug>/`.
2. Run the 15 analysis commands via `run-all.sh`, writing JSON + table output to a per-session `_outputs/` directory. The shell driver accepts `REPORT_GLOB` and `REPORT_OUT` environment variables so it can be retargeted per session.
3. Assemble the per-command JSONs into one `report-stats.json` shape (snapshot, tool counts, transitions, timing, timeline, etc.).
4. Build `report-data.json` by parsing the raw transcript into the row shape the client JavaScript expects (user/assistant/toolResult rows with text, thinking, and call arrays).
5. Render the HTML by substituting the two JSON blobs plus the CSS and JS assets into an HTML template, and write it to `reports/<slug>.html`.

The HTML builder (`build-report.py`) exposes one function:

```python
def render_html(data, stats, headline=None, lede=None, title=None) -> str:
    ...
```

It deep-copies the data, truncates long message bodies to keep the file size reasonable, derives a title/headline/lede from the snapshot when none are given, and substitutes five placeholders in the template. The title and headline come from `stats.snapshot.title` (the minitrace archive's auto-extracted title), not from the raw JSONL `session` line, because the raw line has no title field.

### The self-contained HTML

The report is a single file with three inlined payloads. The `<head>` contains the `<style>` block (the CSS asset) and two CDN `<script>` tags for markdown rendering. The `<body>` contains six numbered sections — key numbers, tool mix, sequencing, timing, the tool-call timeline strip, and the full transcript — each rendered client-side from the inlined `STATS` JSON. At the bottom, a single `<script>` block defines `DATA` and `STATS` from the inlined JSON and then includes the client JS asset.

```html
<script>
const DATA  = <inlined transcript JSON>;
const STATS = <inlined statistics JSON>;
<inlined client JavaScript>
</script>
```

The client JavaScript reads `DATA` and `STATS` and populates the section placeholders. This split — Python assembles the file, JavaScript renders it — keeps each side simple: Python does string substitution and file I/O; JavaScript does DOM rendering and interactivity (the transcript filter buttons and search box).

### Markdown rendering of model answers

Model answers are markdown. Rendering them as escaped plain text loses structure: headings collapse, bullet lists show literal asterisks, tables become unreadable. The report renders message bodies as real HTML using two CDN libraries:

```html
<script src="https://cdn.jsdelivr.net/npm/marked@14/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3/dist/purify.min.js"></script>
```

A small helper parses with `marked` and sanitizes with `DOMPurify`, with a fallback to escaped plain text if the CDN libraries fail to load:

```js
const md = text => {
  if (!text) return "";
  if (typeof marked === "undefined" || typeof DOMPurify === "undefined")
    return "<p>" + esc(text) + "</p>";
  const raw = marked.parse(String(text), { breaks: true, gfm: true });
  return DOMPurify.sanitize(raw, { ADD_ATTR: ["target", "rel"] });
};
```

`DOMPurify` is mandatory because the markdown source is model output. A model can emit arbitrary text, and `marked` alone will happily turn `<script>` in a code block or a malformed link into executable HTML. Sanitizing after parsing is the correct order: parse the markdown to HTML, then strip anything dangerous.

The rendered markdown is styled with its own CSS block scoped to a `.md` class, so list markers pick up the report's accent color, headings are sized for inline use rather than full-page use, and tables reuse the report's hairline borders. Across the 54 message bodies in the gemma4 report this produces 16 bullet lists, 13 headings, 108 bold spans, 63 inline code spans, and one table — all from the model's own markdown.

Thinking blocks and tool results are deliberately not rendered as markdown. Thinking is shown in a monospace block because it is internal reasoning, not prose. Tool results are shown preformatted because they are command output or structured data.

### Swiss minimalist typography

The report's visual style is deliberate and worth naming because it constrains the implementation. The palette is black ink on white paper with a single red-orange accent (`#E8470C`). Typography is a system sans-serif stack for prose and a monospace stack for code, data, and labels. The layout is a strict grid: a max-width column, hairline rules between sections, tabular-numeric alignment for all numbers, and uppercase monospace labels with wide letter-spacing for section markers and metadata.

The accent is used sparingly and meaningfully: section numbers, the "tool calls" KPI, list markers in rendered markdown, links, and the left border of insight callouts. Everything else is black, white, or gray. This restraint is what makes the accent read as emphasis rather than decoration.

## Worked example: what the two reports show

Running the pipeline on both sessions produces two reports that contrast sharply despite using identical queries. The contrast is the point: the same analytical framework surfaces behavioral differences that intuition would miss.

**gpt-5.5 (Discord bot coding).** 181 tool calls across 201 turns. `bash` is 43% of calls, and within bash, 70% are chained commands (`&&`, `;`, `|`). The model packs multiple intents into single shell invocations. It is overwhelmingly sequential (95.7% of tool turns emit one call) but occasionally batches reads. Same-tool momentum dominates: 26% of transitions are `bash -> bash`, 15% are `read -> read`. The longest run is 15 consecutive `read` calls at turn 16. All 15 failures are orchestration friction (docmgr argument errors, Go first-build downloads, edit-ambiguity errors), and there are zero error-then-retry loops. One file — `examples/discord-bots/adventure/index.js` — is touched 13 times, driven by edit-ambiguity failures.

**gemma4:e4b (Liguria vacation search).** 16 tool calls across 68 turns. The tool mix is `show_user_in_browser` (10), `web_search` (5), `fetch_content` (1). The model is strictly sequential (100% of tool turns emit one call) with zero failures, zero retries, and zero file activity. Timing is human-paced: inter-call gaps average 130–230 seconds with a 13-minute maximum, reflecting the user reviewing listings between turns. The model itself is fast (per-turn latency p50 of 3.5s) and free (local model, $0 cost). The cadence is the finding: this is a conversation, not a batch job.

The framework — frequency, sequencing, timing, errors — is identical across both. The behavior is not.

## Common failure modes and working rules

Several non-obvious problems recurred across the two analyses. They are recorded here as rules.

> [!warning] The Pi adapter does not populate `duration_ms` or `exit_code`.
> Verified null for all 181 gpt-5.5 calls and all 16 gemma4 calls. Any timing analysis must derive durations from timestamps and must state that the result is an upper bound including model reasoning and user think-time. Treating timestamp gaps as pure execution time overstates precision.

> [!warning] `UNNEST` over DuckDB JSON arrays is fragile inside JS command handlers.
> Simple aggregates work; certain arrow-operator predicates in `WHERE` clauses trigger a cast-inference error in the Goja path that the same SQL does not trigger in the DuckDB CLI path. Use `mt.db()` normalized tables instead. If you must use `UNNEST`, validate every predicate in the JS path before trusting it.

> [!warning] `mt.queryOne("SELECT *")` returns only the first session.
> The document-pull approach is safe for single-session analysis and silently wrong for multi-session globs. If the archive glob can match more than one session, use normalized tables with an explicit `WHERE session_id = ...` predicate.

> [!warning] The `convert` manifest is advisory.
> Repeated `--source-session` calls into one output directory can leave `manifest.json` reflecting only the last call. Query the `.minitrace.json` file glob directly. Do not gate analysis on manifest counts.

> [!warning] Sanitize model output before injecting it as HTML.
> Model answers are markdown that may contain anything. `marked` alone will render raw HTML embedded in the markdown. Always pass `marked`'s output through `DOMPurify` before inserting into the DOM. The order is non-negotiable: parse, then sanitize.

The working rules that follow from these:

- Default to `mt.db()` normalized tables for any new query. Fall back to document-pull only for single-session work where a table doesn't yet exist, and never use `UNNEST` for new code.
- State every timing number with its derivation. "p50 5.1s, derived from inter-call timestamp gaps including reasoning time" is honest; "p50 5.1s" is not.
- Make each analytical question a named verb in the repository, not a one-off SQL string. Named verbs are discoverable (`go-minitrace query commands --help`), reproducible (`run-all.sh`), and reusable across sessions.
- Keep the report self-contained. Inline the data, the CSS, and the client JS. The only external dependencies should be the two CDN libraries for markdown rendering, and those should degrade gracefully.
- Separate Python's responsibilities (substitution, file I/O, driving the pipeline) from JavaScript's (DOM rendering, interactivity). Neither side should do the other's job.

## Open questions and near-term directions

The pipeline has two known gaps that future work should close.

The first is packaging. The ideal end state is a single Go binary that converts, queries, renders, and writes — replacing the current Python driver, the bash runner, and the separate `go-minitrace` CLI. Every piece has an in-process equivalent: `mt.session().File(path)` converts and normalizes in one call, `require("template")` renders HTML, `require("fs")` writes output. The blocker is module registration: `require("minitrace")` is not a default-registry module, so a hand-written host cannot load it alongside `fs` and `template` without non-obvious work. This is filed as `go-go-golems/go-minitrace` issue #20.

The second is cross-session analysis. The current repository analyzes one session at a time. The normalized schema supports multi-session queries directly — `session_id` is a column on every table — so comparing cohorts of sessions (e.g., "do Codex sessions retry more than Pi sessions?") is a matter of loading multiple archives and grouping by session. The query shapes do not change; only the interpretation does.

## Related notes

The queries and report code live in the source repository at `/home/manuel/code/wesen/2026-06-22--analyze-tool-calls-gemma4`. The `mt.db()` normalized schema and the `xgoja` provider pattern are documented in the `go-minitrace` help pages (`go-minitrace help js-api-reference`, `go-minitrace help minitrace-schema`) and in the `MINIVIZ-002` design doc in the `club-meetup-site` workspace. The module-registration gap is `go-go-golems/go-minitrace` issue #20.

For the broader pattern of building Go-backed JavaScript APIs in go-go-goja, see [[ARTICLE - Designing DSLs with go-go-goja - Go-Backed JavaScript APIs]].
