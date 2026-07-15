---
title: "Transcript-Driven Design System Recovery with go-minitrace"
aliases:
  - "go-minitrace frontend design recovery"
  - "minitrace SQL frontend search"
  - "Pi session transcript mining for design docs"
tags:
  - article
  - go-minitrace
  - frontend-architecture
  - design-system
  - react
  - transcript-analysis
  - duckdb
  - methodology
status: active
type: article
created: 2026-06-07
repo: /home/manuel/workspaces/2026-05-27/rag-evaluation-system/2026-05-27--rag-evaluation-system
---

# Transcript-Driven Design System Recovery with go-minitrace

> [!warning] Historical DuckDB commands
> This note contains `go-minitrace query duckdb` examples from an earlier engine generation. The transcript-recovery method remains useful, but use `go-minitrace query run` and the normalized SQLite schema. See [[ARTICLE - go-minitrace Query Engine Migration - DuckDB to Normalized SQLite]].

This article documents a complete method for recovering documented design-system knowledge from AI coding-agent transcripts using `go-minitrace`, DuckDB, and git. The method was applied to the `2026-05-27--rag-evaluation-system` repository to find prior frontend and design-system playbooks without manually reading through hundreds of session transcripts.

The method produces three outputs that together constitute a recoverable research trail: a ranked list of candidate sessions, a catalog of recovered documents with metadata, and the executable scripts that produced everything.

> [!summary]
> 
> 1. `go-minitrace convert pi` converts Pi session JSONL files into DuckDB-queryable `.minitrace.json` archives. The archives flatten turns and tool calls into a single JSON document per session.
> 2. DuckDB SQL with `UNNEST` on the `turns` and `tool_calls` arrays enables high-recall keyword searches across every prompt, response, command, and command output in the archive.
> 3. The same approach works with JS verb commands via `mt.query()` for reusable, parameterized queries with custom ranking logic.
> 4. The recovered documents included the RAG React design-system guidelines, a component audit, design references, Widget DSL guides, and the original Obsidian article on the design system.

## Why This Method Exists

When a project accumulates design-system documentation through coding-agent sessions, that documentation lives in two places: committed files in the repository (design docs in `ttmp/`, README files, design references) and ephemeral knowledge inside session transcripts (the reasoning, the file paths discovered, the context that led to each document).

When a new engineer joins or a previous context is lost, neither location alone is sufficient. The committed files are real but may not explain the thinking behind them. The transcripts contain the thinking but are too large and numerous to read manually.

The method bridges both. It converts the transcript archive into a queryable database and searches across it to answer the question: "Which prior sessions discussed design-system playbooks, and what concrete documents or file paths did they reference?"

## The Minitrace Schema

Each session produces one `.minitrace.json` file. The file contains a top-level object with these keys:

```
annotations | classification | condition | coordination | environment | flags
handover | id | metrics | operational_context | outcome | profile
provenance | quality | scenario_id | schema_version | summary | timing
title | tool_calls | turns
```

The keys relevant to this method are `turns` and `tool_calls`. Both are arrays.

The `turns` array represents the conversation. Each element has:

```json
{
  "index": 0,
  "timestamp": "2026-05-28T21:52:41.593Z",
  "role": "user",
  "source": "human",
  "model": "glm-5.1",
  "content": "Create a new docmgr ticket in 2026-05-27--rag-evaluation-system/ttmp using...",
  "thinking": null,
  "intent_markers": null,
  "streaming": { "was_streamed": false, "stream_log": null },
  "usage": null
}
```

The `tool_calls` array represents the tool invocations. Each element has:

```json
{
  "id": "call_eb9e281cc9564915bc47f5ce",
  "emitting_turn_index": 1,
  "timestamp": "2026-05-28T21:52:48.374Z",
  "tool_name": "bash",
  "operation_type": "EXECUTE",
  "input": {
    "command": "docmgr ticket list --ticket RAGEVAL-003",
    "arguments": { "command": "docmgr ticket list --ticket RAGEVAL-003" }
  },
  "output": {
    "success": true,
    "result": "Docs root: `/home/manuel/...`\n..."
  }
}
```

The `tool_calls.input.command` field captures the command text. The `tool_calls.output.result` field captures stdout. Both are searchable text.

The session also carries metadata at the top level:

```json
{
  "id": "019e7092-4203-7529-862e-eabdca26a302",
  "title": "Work on the docmgr ticket RAGEVAL-003...",
  "timing": {
    "started_at": "2026-05-28T21:51:33Z",
    "ended_at": "2026-05-29T01:58:52Z",
    "duration_seconds": 14838.684
  },
  "environment": {
    "model": "glm-5.1",
    "agent_framework": "pi"
  },
  "metrics": {
    "turn_count": 365,
    "tool_call_count": 365,
    "read_count": 79
  }
}
```

DuckDB reads these files directly from the filesystem. The table name is `sessions_base`. No ETL is required.

```sql
SELECT id, title,
       environment->>'model' AS model,
       CAST(metrics->>'turn_count' AS INTEGER) AS turns
FROM sessions_base;
```

## Converting Pi Sessions

Pi sessions live under `~/.pi/agent/sessions/` with directories named after the source code path, such as `--home-manuel-workspaces-2026-05-27-rag-evaluation-system--`. Each directory contains JSONL files, one per session.

The conversion command creates a DuckDB-compatible JSON archive:

```bash
go-minitrace convert pi \
  --source-dir ~/.pi/agent/sessions/--home-manuel-workspaces-2026-05-27-rag-evaluation-system-- \
  --output-dir ./analysis/pi
```

The command outputs `.minitrace.json` files organized by session date. Each file is a single JSON object matching the schema described above.

For the RAG evaluation workspace, two session directories were relevant:

- `~/.pi/agent/sessions/--home-manuel-workspaces-2026-05-27-rag-evaluation-system--` — the outer workspace. This contained 16 sessions from May 27 through June 7.
- `~/.pi/agent/sessions/--home-manuel-workspaces-2026-05-27-rag-evaluation-system-2026-05-27--rag-evaluation-system--` — the nested git checkout. This contained 2 sessions from May 28 and May 29.

The total converted archive contained 18 sessions.

The sessions ranged from 10 to 1,336 tool calls. The longest sessions were from June 3 (sessions `019e8af1` with 990 calls and `019e8afc` with 1,336 calls). These were the sessions that built the UI DSL, Widget IR, and related frontend infrastructure.

## The SQL Search Strategy

The core idea is to unnest the `turns` and `tool_calls` arrays and search the text content of every element. A single session produces many rows when unnested — a session with 1,000 tool calls produces 1,000 rows from the `tool_calls` side alone. This is intentional: it gives us coverage of every command, every output, every prompt, and every assistant response.

The first query searched both turns and tool calls simultaneously, classified each hit into a category, and ranked sessions by a weighted formula:

```sql
WITH turn_hits AS (
  SELECT
    id,
    title,
    timing->>'started_at' AS started_at,
    environment->>'model' AS model,
    CAST(t->>'index' AS INTEGER) AS turn_index,
    t->>'role' AS role,
    LEFT(t->>'content', 500) AS snippet,
    CASE
      WHEN regexp_matches(lower(COALESCE(t->>'content', '')), 'design system|design-system') THEN 'design-system'
      WHEN regexp_matches(lower(COALESCE(t->>'content', '')), 'playbook|handbook|contributing|contribution') THEN 'playbook'
      WHEN regexp_matches(lower(COALESCE(t->>'content', '')), 'web/|react|atoms|molecules|foundation|storybook') THEN 'frontend-structure'
      WHEN regexp_matches(lower(COALESCE(t->>'content', '')), 'context window|transcript|annotation|course') THEN 'target-page'
      ELSE 'other'
    END AS hit_kind
  FROM sessions_base, UNNEST(turns) AS u(t)
  WHERE regexp_matches(lower(COALESCE(t->>'content', '')),
    'design system|design-system|playbook|handbook|contributing|contribution|web/|react|atoms|molecules|foundation|storybook|context window|transcript|annotation|course')
),
tool_hits AS (
  SELECT
    id,
    title,
    timing->>'started_at' AS started_at,
    environment->>'model' AS model,
    CAST(tc->>'emitting_turn_index' AS INTEGER) AS turn_index,
    'tool:' || (tc->>'tool_name') AS role,
    LEFT(COALESCE(tc->'input'->>'command', tc->'input'->>'path', tc->'output'->>'result', ''), 500) AS snippet,
    CASE
      WHEN regexp_matches(lower(COALESCE(tc->'input'->>'command', tc->'input'->>'path', tc->'output'->>'result', '')), 'design system|design-system') THEN 'design-system'
      WHEN regexp_matches(lower(COALESCE(tc->'input'->>'command', tc->'input'->>'path', tc->'output'->>'result', '')), 'playbook|handbook|contributing|contribution') THEN 'playbook'
      WHEN regexp_matches(lower(COALESCE(tc->'input'->>'command', tc->'input'->>'path', tc->'output'->>'result', '')), 'web/|react|atoms|molecules|foundation|storybook') THEN 'frontend-structure'
      WHEN regexp_matches(lower(COALESCE(tc->'input'->>'command', tc->'input'->>'path', tc->'output'->>'result', '')), 'context window|transcript|annotation|course') THEN 'target-page'
      ELSE 'other'
    END AS hit_kind
  FROM sessions_base, UNNEST(tool_calls) AS u(tc)
  WHERE regexp_matches(lower(COALESCE(tc->'input'->>'command', tc->'input'->>'path', tc->'output'->>'result', '')),
    'design system|design-system|playbook|handbook|contributing|contribution|web/|react|atoms|molecules|foundation|storybook|context window|transcript|annotation|course')
),
all_hits AS (
  SELECT * FROM turn_hits
  UNION ALL
  SELECT * FROM tool_hits
)
SELECT
  id,
  title,
  started_at,
  model,
  COUNT(*) AS hit_count,
  SUM(CASE WHEN hit_kind = 'design-system' THEN 1 ELSE 0 END) AS design_system_hits,
  SUM(CASE WHEN hit_kind = 'playbook' THEN 1 ELSE 0 END) AS playbook_hits,
  SUM(CASE WHEN hit_kind = 'frontend-structure' THEN 1 ELSE 0 END) AS frontend_hits,
  SUM(CASE WHEN hit_kind = 'target-page' THEN 1 ELSE 0 END) AS target_page_hits,
  MIN(turn_index) AS first_hit_turn,
  STRING_AGG(DISTINCT hit_kind, ', ' ORDER BY hit_kind) AS hit_kinds,
  ARG_MIN(snippet, turn_index) AS first_snippet
FROM all_hits
GROUP BY id, title, started_at, model
ORDER BY (playbook_hits * 5 + design_system_hits * 3 + frontend_hits * 2 + target_page_hits) DESC, hit_count DESC
LIMIT 25;
```

Several design decisions shaped this query:

1. **Both turns and tool_calls.** Design-system discussions appear in prompts ("search for playbook files"), in assistant responses ("I found these docs"), in commands (`docmgr ticket list`, `rg -n ...`), and in command output (file paths, ticket names). Searching only turns would miss command-level evidence.

2. **Category classification.** Each hit is classified into one of four categories: design-system, playbook, frontend-structure, or target-page. This lets the ranking formula weight each type differently. Playbook hits get weight 5 (they directly answer the user's question). Design-system hits get weight 3. Frontend-structure hits get weight 2.

3. **Weighted ranking.** Sessions with more playbook hits rank higher. The formula is `playbook_hits * 5 + design_system_hits * 3 + frontend_hits * 2 + target_page_hits`. This is a heuristic, not a statistical model. It worked for this search space.

4. **LIMIT 25.** The top hits are reviewed by hand. There is no point scanning beyond 25 because the bottom entries are typically noise.

The query runs via:

```bash
go-minitrace query duckdb \
  --archive-glob './sources/minitrace/*/active/*/*.minitrace.json' \
  --sql-file ./scripts/03_candidate_session_search.sql \
  --output json > ./sources/candidate-session-search.json
```

## The JS Verb Command

The SQL query was effective for a first pass. For a second pass with more nuanced ranking, the JS verb command approach was used. This demonstrates the `require("minitrace")` API and the `__verb__` / `__section__` metadata markers that make JS commands discoverable through the CLI.

```js
__section__("filters", {
  fields: {
    limit: { type: "int", default: 50, help: "Maximum rows to return" },
  },
});

function webPlaybookEvidence(filters) {
  const mt = require("minitrace");
  const limit = filters.limit || 50;
  return mt.query(`
    WITH tool_text AS (
      SELECT
        id,
        title,
        timing->>'started_at' AS started_at,
        CAST(tc->>'emitting_turn_index' AS INTEGER) AS turn_index,
        tc->>'tool_name' AS tool_name,
        COALESCE(tc->'input'->>'command', '') AS command,
        COALESCE(tc->'input'->>'path', tc->'input'->>'file_path', '') AS input_path,
        COALESCE(tc->'output'->>'result', '') AS output_result
      FROM ${mt.tableName}, UNNEST(tool_calls) AS u(tc)
    ), scored AS (
      SELECT
        id,
        title,
        started_at,
        turn_index,
        tool_name,
        input_path,
        command,
        LEFT(output_result, 700) AS output_snippet,
        (CASE WHEN regexp_matches(lower(command || ' ' || input_path || ' ' || output_result), 'design system|design-system') THEN 8 ELSE 0 END) +
        (CASE WHEN regexp_matches(lower(command || ' ' || input_path || ' ' || output_result), 'playbook|handbook|contributing|contribution|guide') THEN 6 ELSE 0 END) +
        (CASE WHEN regexp_matches(lower(command || ' ' || input_path || ' ' || output_result), 'web/|packages/rag-evaluation-site|src/components|atoms|molecules|foundation|storybook') THEN 5 ELSE 0 END) +
        (CASE WHEN regexp_matches(lower(command || ' ' || input_path || ' ' || output_result), 'docmgr doc add|docmgr doc relate|write[(]|design-doc|reference|[.]md') THEN 3 ELSE 0 END) AS score
      FROM tool_text
      WHERE regexp_matches(lower(command || ' ' || input_path || ' ' || output_result),
        'design system|design-system|playbook|handbook|contributing|contribution|guide|web/|packages/rag-evaluation-site|src/components|atoms|molecules|foundation|storybook')
    )
    SELECT *
    FROM scored
    WHERE score > 0
    ORDER BY score DESC, started_at DESC, turn_index ASC
    LIMIT ${Number(limit)}
  `);
}

__verb__("webPlaybookEvidence", {
  name: "web-playbook-evidence",
  short: "Find transcript tool evidence for web/design-system playbooks",
  fields: { filters: { bind: "filters" } },
});
```

The JS approach differs from the SQL approach in three significant ways.

First, it only searches `tool_calls`, not `turns`. The rationale was that tool calls (commands and their output) are more likely to contain concrete file paths, ticket names, and docmgr commands. Turn content (prompts and responses) contains the reasoning but is less likely to contain the exact file paths we needed.

Second, it uses a four-tier scoring system instead of four category classifications. The highest score (8) goes to hits containing "design system". The next tier (6) goes to "playbook", "handbook", or "guide". The third tier (5) goes to concrete filesystem paths like `packages/rag-evaluation-site` or `src/components`. The fourth tier (3) goes to docmgr command patterns like `docmgr doc add` or `.md` file references.

Third, it filters to rows with `score > 0`, which means every returned row has confirmed document-relevance.

The command runs via:

```bash
go-minitrace query commands \
  --query-repository ./scripts/query-commands \
  design web-playbook-search web-playbook-evidence \
  --archive-glob './sources/minitrace/*/active/*/*.minitrace.json' \
  --limit 30 \
  --output json > ./sources/web-playbook-evidence.json
```

## What the Searches Found

The SQL search ranked 18 sessions. The top-ranked session was `019e8afc` (June 3, 2026, model gpt-5.5, 1,336 tool calls) with 350 total hits: 30 playbook hits, 14 design-system hits, 301 frontend-structure hits, and 5 target-page hits. Its first snippet contained the prompt:

```
Create a new docmgr ticket in 2026-05-27--rag-evaluation-system/ttmp using
docmgr --root 2026-05-27--rag-evaluation-system/ttmp to create a ui.dsl and
kanban dsl like in 2026-05-03--goja-hosting-site/ to create webpages using
the widgets and primitives in 2026-05-27--rag-evaluation-system/web/ .
Create a detailed analysis / design / implementation guide that is for a new
intern, explaining all the parts of the system needed to understand what it is
```

This session was the one that built the UI DSL and created the initial intern guide. It directly discussed the `web/` directory, the widget primitives, and the component architecture.

The second-ranked session was `019ea2e3` (June 7, 2026, model gpt-5.5) with 239 hits, all design-system and frontend-structure. Its first snippet contained:

```
Create a new docmgr to create a HTML render of the design system reference
sheet for 2026-05-27--rag-evaluation-system/web/ .
We created an extensive and structured design system for this website,
which then also has a structured widget rendering system, see
/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/06/02/ARTICLE
- RAG React Design System - From Prototype Dashboard to Structured Design
System.md
```

This session directly referenced the Obsidian article and the design system reference sheet ticket. It was the source of the `RAGEVAL-DS-RAGEVAL-QWEN36-HIGH` ticket.

The JS command returned 30 rows, all tool calls. The top results confirmed the same sessions: the UI DSL builder, the design system reference creator, and the code-review-PR session. Each row included the command that produced the hit, the output snippet, and the score.

## Recovered Documents

The Python catalog script processed nine known document paths and one Obsidian article, extracting title, summary, WhatFor, and first headings from each. The recovered documents were:

| Document | Date | Type | Key Topics |
|---|---|---|---|
| RAG React Design System Guidelines | 2026-06-01 | Design doc | Layer ownership rules, Storybook requirements, CSS reduction strategy, phased work plan |
| RAG Design System Guideline Audit | 2026-06-01 | Analysis | Component-by-component compliance audit, CSS debt inventory, extraction recommendations |
| Styling and Design Reference | 2026-06-07 | Design doc | Retro monochrome visual language, token system, typography roles, CSS architecture |
| Widget Hierarchy and Interaction Reference | 2026-06-07 | Design doc | Composition hierarchy (tokens→foundation→atoms→layout→molecules→organisms→pages), Widget IR, Goja authoring |
| Widget DSL Visual Quality Analysis and Implementation Guide | 2026-06-05 | Design doc | Token contract mismatch, visual gaps, phased fix plan, visual-test selectors |
| WidgetRenderer Packaging Architecture and Implementation Guide | 2026-06-04 | Design doc | npm package, Go embed default app, WidgetRenderer architecture |
| UI DSL and Kanban DSL Design and Implementation Guide | 2026-06-02 | Design doc | Go backend, React frontend, Goja runtime, UI DSL AST, Kanban DSL |
| RAG Widget DSL Design — Component-to-HTML Mapping | 2026-06-02 | Design doc | One-to-one component mapping, props-to-attributes, CSS hard-coding |
| Review and Revised Implementation Guide for the RAG Widget DSL | 2026-06-02 | Design doc | What previous work got right/wrong, corrected architecture (IR over HTML cloning) |
| ARTICLE - RAG React Design System - From Prototype Dashboard to Structured Design System | 2026-06-02 | Article | Pass-by-pass architecture evolution: documentation → tokens → atoms → molecules → Search as first vertical slice |

The most important document for this method's purposes is the **RAG React Design System Guidelines**. It was written on June 1, 2026, in commit `1cb51dd` (`docs: audit RAG design system guidelines`), and defines the layer ownership rules that became the governing principle for all subsequent frontend work:

> Every visual decision has one owner:
> - tokens own values;
> - foundation primitives own typography, code text, captions, status text, accessibility, and separators;
> - layout primitives own structure and spacing recipes;
> - molecules own reusable data-display patterns;
> - organisms own feature panels with DTO-shaped props;
> - pages own composition of organisms and page-level state;
> - containers own RTK Query, mutations, navigation events, and side effects;
> - CSS Modules own local anatomy that is not reusable.

This is the exact guideline that any future frontend contributor would need to read before adding components.

## The Git History Supplement

SQL and JS searches recover evidence from session transcripts. But committed files exist independently of transcripts, and `docmgr` indexes them separately from `git`. The git history search was used to confirm the document trail and identify the exact commit that added the design-system guidelines.

```bash
git log --date=iso --pretty=format:'%h%x09%ad%x09%s' \
  -- web packages/rag-evaluation-site internal/web pkg/widgetdsl pkg/widgetserver pkg/widgetrunner \
  > sources/git/frontend-history.tsv

git log --name-only --date=iso \
  --pretty=format:'--COMMIT--%x09%H%x09%ad%x09%s' \
  -- web packages/rag-evaluation-site internal/web pkg/widgetdsl pkg/widgetserver pkg/widgetrunner \
  > sources/git/frontend-history-with-files.txt
```

The git history showed 51 commits affecting frontend/design paths, with the design-system evolution concentrated between May 27 and June 7, 2026. The most relevant commit was:

```
1cb51dd  2026-06-01  ttmp/.../RAG-WEB-DESIGN-SYSTEM-REVIEW--.../design-doc/02-rag-react-design-system-guidelines.md
         ttmp/.../RAG-WEB-DESIGN-SYSTEM-REVIEW--.../analysis/01-rag-design-system-guideline-audit.md
```

This confirmed that the design-system guidelines lived in the `RAG-WEB-DESIGN-SYSTEM-REVIEW` ticket workspace.

## How the Scripts Were Organized

All reusable commands are stored under the ticket's `scripts/` directory. This ensures the full research trail is reproducible: anyone with the ticket can rerun the exact same searches.

| Script | Type | Purpose |
|---|---|---|
| `01_capture_go_minitrace_help.sh` | Shell | Captures `go-minitrace help --all` and focused help pages |
| `02_convert_relevant_pi_sessions.sh` | Shell | Converts two Pi session directories into DuckDB archives |
| `03_candidate_session_search.sql` | SQL | DuckDB query ranking sessions by design-system keywords |
| `query-commands/design/web-playbook-search.js` | JS | Go-minitrace JS verb with four-tier scoring |
| `04_git_frontend_history.sh` | Shell | Captures git log history for frontend paths |
| `05_catalog_recovered_design_docs.py` | Python | Extracts title/summary/headings from recovered docs |

Each script is self-contained. It takes no arguments beyond the ticket directory (inferred from `BASH_SOURCE` or `__file__`). It writes output to a `sources/` subdirectory. The `sources/` directory is the only place that is not committed — it contains transient query results.

## Failure Modes and Fixes

Three failures occurred during this process, each revealing a constraint worth documenting.

### DuckDB regexp error in JS command

The first run of the JS command failed with:

```
Error: GoError: executing js query: Invalid Input Error: missing ):
docmgr doc add|docmgr doc relate|write(|design-doc|reference|.md
```

The error was in the regex pattern: `docmgr doc add|docmgr doc relate|write(|design-doc|reference|.md`. The `(` character inside the regex was interpreted by DuckDB as the start of a subexpression, but there was no closing `)`. The fix was to escape the parentheses as bracket expressions: `write[(]` and `[.]md`.

This revealed that DuckDB's regexp_matches follows POSIX ERE syntax, not JavaScript regex syntax. Characters that are literal in JavaScript (`(`, `.`, `|` inside character classes) may have special meaning in ERE.

### Wrong repo root in shell script

The first run of `04_git_frontend_history.sh` failed with:

```
fatal: not a git repository (or any of the parent directories): .git
```

The script computed the repo root from the script's own directory: `REPO_ROOT="$(cd "$TICKET_DIR/../../../../../../.." && pwd)"`. But `TICKET_DIR` pointed to a directory six levels deep inside `ttmp/2026/06/07/...`, and counting `..` from there went past the git repository root into a parent workspace directory that did not contain `.git`.

The fix was to count one fewer `..` segments: `../../../../..`. The exact number depends on the depth of the ticket directory, which varies by ticket. A more robust approach would be to find the git root with `git rev-parse --show-toplevel` rather than counting path segments.

### Wrong repo root in Python script

The first run of `05_catalog_recovered_design_docs.py` silently produced only "Missing" entries for all repo-local docs. The root cause was `REPO = Path(__file__).resolve().parents[5]`, which resolved to `ttmp/` rather than the repository root.

The fix was `REPO = Path(__file__).resolve().parents[6]`. Like the shell script fix, this is fragile — it depends on the depth of the ticket directory. A robust Python approach would use `Path(__file__).resolve().parents[N].parent.parent` with N adjusted dynamically, or search upward for a file that exists at the repo root (such as `go.mod`).

These failures share a common root cause: the ticket directory is deeply nested inside the repository, and scripts that compute absolute paths by counting `..` segments are fragile. The correct fix for any script that needs the repo root is to use a command-line tool that finds it: `git rev-parse --show-toplevel` for git repos, or `docmgr status --summary-only` for docmgr projects.

## Comparison: SQL vs JS Commands

| Dimension | SQL | JS |
|---|---|---|
| Entry point | `go-minitrace query duckdb --sql-file ...` | `go-minitrace query commands --query-repository ... verb-name` |
| Search scope | `UNNEST(turns)` and `UNNEST(tool_calls)` | Configurable |
| Ranking | ORDER BY formula in SQL | Scoring in SQL, post-processing in JS |
| Reusability | SQL file, one-off | Registered verb with `--help`, `--limit` flag |
| Debugging | Full SQL visible in file | JS function + SQL template, harder to see intermediate state |
| Error surface | DuckDB regexp syntax | Python/JS string formatting + DuckDB regexp |
| When to use | One-off searches, broad sweeps | Repeated searches, complex scoring, multi-query joins |

The SQL approach is better for the initial discovery pass because it is simple, visible, and fast to write. The JS approach is better when the scoring logic is complex enough that SQL becomes unwieldy, or when the query should become a named, reusable command with typed flags and `--help`.

## What the Recovered Documents Tell Us

The recovered documents collectively establish four governing principles for any frontend work on this project:

1. **Layer ownership is non-negotiable.** Every visual decision has exactly one owner at a specific layer. Components at layer N cannot redefine the visual behavior of components from layer N-1.

2. **Storybook coverage is part of done.** No component is considered complete without Storybook stories covering default, themed, and edge states. This applies to primitives, molecules, organisms, and presentational page boundaries.

3. **Widget IR is for authoring, not rendering.** The Widget IR + WidgetRenderer + React components pipeline exists so that Goja/JavaScript authors can produce JSON-compatible data that React renders into real component-library widgets. The rendering logic lives in React, not in the IR or the DSL.

4. **The visual identity is retro monochrome, dense, and square.** The system uses zero border radius, black panel headers, thin borders, monospace typography, and small semantic color accents. Any new design must conform to this identity.

## Working Rules

From the recovered documents, these rules emerged as consistently applied:

- Use `packages/rag-evaluation-site/src/components/` for standalone package components. Each component lives in its own directory with `Component.tsx`, `Component.module.css`, and `index.ts`.
- Use `packages/rag-evaluation-site/src/widgets/` for Widget IR rendering (WidgetRenderer, cellRenderers, actions, ir types).
- Use `web/src/components/` for the legacy RAG application components. Same directory-per-component pattern.
- Theme tokens are defined in `packages/rag-evaluation-site/src/theme.css` (standalone) and `web/src/styles/tokens.css` (legacy). The two files must stay in sync.
- CSS Modules own only local anatomy. Token usage, typography roles, and spacing are consumers of foundation primitives, not owners of them.

## Limitations

The method has several limitations worth stating explicitly.

First, it only searches within converted sessions. If design-system work happened in Codex sessions, in human-to-human discussions, or in external documents not referenced in any session transcript, the method will not find it. The `go-minitrace discover codex` command could be used to also convert Codex sessions and broaden the search.

Second, the search depends on keyword matching. A session that implemented a design-system component without mentioning the words "design system," "playbook," "atoms," "molecules," or "web/" would be missed. The search keywords were chosen based on what the user's question was likely to contain, not based on an exhaustive taxonomy.

Third, the ranking formula is a heuristic. It weights playbook hits most heavily because that was the user's primary goal. If the goal were different (e.g., "find sessions about Widget IR architecture"), the formula would need to change.

Fourth, the method does not deduplicate. A session that discusses "design system" 50 times in its prompts will appear with 50 design-system hits, even though the actual unique information may be limited to a few sentences.

## How to Reuse This Method

To apply this method to a different repository or topic:

1. Identify the session store directories. For Pi sessions, these are under `~/.pi/agent/sessions/`. For Codex sessions, under `~/.codex/sessions/`.

2. Write `02_convert_*.sh` to convert the relevant session directories. Include all directories that contain sessions from the repository in question.

3. Write `03_*.sql` with a keyword list that matches your search terms. Classify hits into categories that matter for your goal. Weight them according to what you want to find first.

4. Optionally write a JS verb command with `require("minitrace")` and `mt.query(...)` if you need multi-tier scoring or post-processing logic.

5. Run the SQL query, review the top sessions, and inspect the `first_snippet` column to verify relevance.

6. Write a catalog script (Python, shell, or any language) to extract metadata from the documents that the search identified.

7. Store all scripts in the ticket's `scripts/` directory so the full trail is reproducible.

The scripts from this method are located at:

```
ttmp/2026/06/07/RAGEVAL-CONTEXT-WINDOWS-DESIGN--transcript-context-window-annotation-and-course-page-design-integration/scripts/
```

The output files are located at:

```
ttmp/2026/06/07/RAGEVAL-CONTEXT-WINDOWS-DESIGN--transcript-context-window-annotation-and-course-page-design-integration/sources/
```

## Related Notes

- The RAG React Design System Guidelines: `ttmp/2026/06/01/RAG-WEB-DESIGN-SYSTEM-REVIEW--rag-evaluation-web-architecture-and-design-system-review/design-doc/02-rag-react-design-system-guidelines.md`
- The Widget Hierarchy and Interaction Reference: `ttmp/2026/06/07/RAGEVAL-DS-RAGEVAL-QWEN36-HIGH--rag-design-system-reference-sheet-styling-design-widget-interaction-hierarchy/design-doc/02-widget-hierarchy-and-interaction-reference.md`
- The Styling and Design Reference: `ttmp/2026/06/07/RAGEVAL-DS-RAGEVAL-QWEN36-HIGH--rag-design-system-reference-sheet-styling-design-widget-interaction-hierarchy/design-doc/01-styling-and-design-reference.md`
- The article on the design system's evolution: `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/06/02/ARTICLE - RAG React Design System - From Prototype Dashboard to Structured Design System.md`
