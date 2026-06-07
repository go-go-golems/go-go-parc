---
title: Analyzing Coding-Agent Sessions with go-minitrace
aliases:
  - Coding Agent Session Analysis
  - go-minitrace Session Analysis
  - Minitrace Diagram Generation
tags:
  - article
  - playbook
  - minitrace
  - coding-agents
  - duckdb
status: active
type: article
created: 2026-06-07
repo: /home/manuel/code/wesen/go-go-golems/go-minitrace
---

# Analyzing Coding-Agent Sessions with go-minitrace

This article explains how to inspect a coding-agent session from start to finish: convert raw transcripts into a structured archive, query the archive with SQL and JavaScript via DuckDB, and produce diagram visualizations in a custom JSON-based DSL. It is a complete working guide with every command, query, and script included in full so you can copy-paste and run it yourself.

> [!summary]
> - **The pipeline** is three stages: convert transcripts → query with DuckDB → compose diagram JSON. Each stage has well-defined interfaces.
> - **Tool calls are the interesting data**. Every action a coding agent takes is a tool call with structured input and output. Extracting these fields correctly is the central challenge.
> - **The Diagram DSL** is a JSON format for poster-style diagrams with strip, stack, loop, and transition types. It separates content from styling — you never set colors or coordinates, only semantic structure.

## When This Pipeline Matters

You reach for this pipeline when a coding-agent session raises questions you cannot answer by reading the raw transcript:

- How many tool calls were there, and what types?
- What files did the agent read or write across the session?
- Which tool invocations failed?
- How does the agent alternate between thinking, reading, executing, and writing?
- What does the session look like as a diagram?

The pipeline takes you from a raw JSONL transcript file to structured queries and finally to diagram JSON that a renderer can visualize.

## The Three Stages

The pipeline has three stages, each with a clear input and output.

```
raw JSONL transcript  →  .minitrace.json  →  SQL/JS queries  →  diagram JSON
```

Stage 1 is conversion: the raw transcript is normalized into a minitrace archive. Stage 2 is querying: the archive is loaded into DuckDB and you run SQL or JavaScript against it. Stage 3 is composition: query results are assembled into diagram DSL JSON.

Each stage is independent. You can replace the converter, swap DuckDB for another backend, or use a different diagram format. The interfaces between stages are fixed: `.minitrace.json` for stage 1 output, the DuckDB table for stage 2, and the diagram DSL schema for stage 3.

## Stage 1: Converting a Transcript

### The input format

Pi sessions are stored as JSONL files. Each line is one turn of the conversation. A typical session has one user turn followed by several assistant turns, each containing tool calls. The file lives under:

```
~/.pi/agent/sessions/--home-manuel-code-wesen-claw-stuff--/<timestamp>_uuid.jsonl
```

The session analyzed in this article was stored at:

```
~/.pi/agent/sessions/--home-manuel-code-wesen-claw-stuff--/2026-06-07T14-48-45-535Z_019ea28e-c2df-78b0-9b68-beab237ff85e.jsonl
```

It had 7 turns and 12 tool calls, using the model `umans-qwen3.6-35b-a3b`.

### The conversion command

The `go-minitrace convert pi` command reads a JSONL transcript and writes a `.minitrace.json` archive:

```bash
go-minitrace convert pi \
  --source-session ~/.pi/agent/sessions/--home-manuel-code-wesen-claw-stuff--/2026-06-07T14-48-45-535Z_019ea28e-c2df-78b0-9b68-beab237ff85e.jsonl \
  --output-dir ./minitrace-output
```

The output directory has the following structure:

```
minitrace-output/
  active/
    2026-06/
      019ea28e-c2df-78b0-9b68-beab237ff85e.minitrace.json
  manifest.json
```

The `.minitrace.json` file is the archive. The `manifest.json` is a small index that go-minitrace maintains.

### The minitrace schema

The archive is a single JSON object with these top-level fields:

| Field | Type | Purpose |
|-------|------|---------|
| `id` | string | Session UUID |
| `title` | string | Auto-extracted from first user turn |
| `turns` | array | Conversation turns in order |
| `tool_calls` | array | Every tool invocation |
| `metrics` | object | Computed counts and ratios |
| `environment` | object | Model name, framework, tools |
| `timing` | object | Timestamps and duration |
| `classification` | string | Always "internal" for locally converted sessions |
| `quality` | string | A (rich), B (has conversation), C (no conversation) |

The `quality` field is important: it is computed during conversion and stored in the `manifest.json`, not in the individual archive files. This matters for querying, as we will see.

Each turn has an `index`, `role` (user or assistant), `content`, optional `thinking`, and `tool_calls_in_turn` (a list of tool call IDs). Each tool call has an `id`, `tool_name`, `operation_type`, `input` object, and `output` object.

The `input` field is polymorphic. For `read` tools, it has `file_path` and `arguments`. For `bash` tools, it has `command`. For `write` tools, it has `path` and `arguments.content`. Understanding this structure is critical for writing correct queries.

## Stage 2: Querying the Archive

### Loading into DuckDB

The `go-minitrace query duckdb` command loads one or more `.minitrace.json` files into DuckDB. It creates a table called `sessions_base` with the following columns:

| Column | Type | How it is loaded |
|--------|------|-----------------|
| `id` | VARCHAR | Direct extraction |
| `title` | VARCHAR | Direct extraction |
| `summary` | VARCHAR | Direct extraction |
| `classification` | VARCHAR | Direct extraction |
| `profile` | VARCHAR | Direct extraction |
| `provenance` | JSON | Nested object |
| `flags` | JSON | Nested object |
| `environment` | JSON | Nested object |
| `operational_context` | JSON | Nested object |
| `timing` | JSON | Nested object |
| `turns` | JSON[] | Array of JSON objects |
| `tool_calls` | JSON[] | Array of JSON objects |
| `annotations` | JSON[] | Array of JSON objects |
| `metrics` | JSON | Nested object |

Notice what is missing: `quality` is not a column. The `buildLoadSQL()` function in the codebase explicitly lists which top-level fields become VARCHAR columns. `quality` is intentionally excluded because it lives in the manifest, not the archive files. To filter by quality, you must either read the manifest or infer it from `metrics` (quality A = `turn_count > 5 AND tool_call_count > 10`).

### Querying arrays: UNNEST

The `turns`, `tool_calls`, and `annotations` columns are JSON arrays. To query individual elements, you must `UNNEST` the array:

```sql
SELECT
  REPLACE(CAST(json_extract(tc, '$.tool_name') AS VARCHAR), '"', '') AS tool,
  json_extract(tc, '$.operation_type') AS op_type
FROM sessions_base,
     UNNEST(tool_calls) AS t(tc)
ORDER BY CAST(json_extract(tc, '$.id') AS VARCHAR)
```

The `UNNEST(tool_calls) AS t(tc)` clause expands each tool call array element into a row. The variable `tc` holds one JSON element that you can query with `json_extract()`.

### Extracting tool call fields

This is the central challenge. The `input` field is a polymorphic JSON object. You cannot reliably extract it by casting the entire object to VARCHAR and then parsing it in JavaScript — DuckDB double-escapes the JSON, and `JSON.parse()` in JS will fail on the escaped output.

The correct approach is to extract individual sub-fields directly:

```sql
SELECT
  REPLACE(CAST(json_extract(tc, '$.tool_name') AS VARCHAR), '"', '') AS tool_name,
  CAST(json_extract(tc, '$.input.file_path') AS VARCHAR) AS input_file_path,
  CAST(json_extract(tc, '$.input.command') AS VARCHAR) AS input_command,
  CAST(json_extract(json_extract(tc, '$.input'), '$.arguments.path') AS VARCHAR) AS input_arg_path,
  CAST(json_extract(tc, '$.output.result') AS VARCHAR) AS output_result,
  CAST(json_extract(tc, '$.output.error') AS VARCHAR) AS output_error,
  CAST(json_extract(tc, '$.output.success') AS VARCHAR) AS output_success
FROM sessions_base,
     UNNEST(tool_calls) AS t(tc)
```

Key principles:

- Use `json_extract(tc, '$.input.file_path')` for `read` tool file paths.
- Use `json_extract(tc, '$.input.command')` for `bash` tool commands.
- Use nested `json_extract(json_extract(tc, '$.input'), '$.arguments.path')` for deeply nested arguments.
- Use `json_extract(tc, '$.output.result')` to keep output result as JSONB (no casting) when you need to check if it contains certain substrings.
- Use `json_extract(tc, '$.output.success')` as a VARCHAR to check `= 'true'` or `= 'false'`.

In JavaScript command handlers, you can use the shorter JSON arrow syntax instead:

```js
// In JS command handlers, arrow operators work directly:
call->>'tool_name'                        // returns string directly
call->>'operation_type'                   // returns string directly
json_extract(json_extract(call, '$.input'), '$.arguments.path')  // for nested args
```

The `REPLACE(CAST(json_extract(...) AS VARCHAR), '"', '')` pattern is only needed in pure SQL because DuckDB's `CAST(VARCHAR)` wraps strings in quotes. The `->>` arrow operator in JS handlers skips the quoting layer entirely.

### Querying turns

To get turn-level data, `UNNEST` the `turns` column:

```sql
SELECT
  CAST(json_extract(turn, '$.index') AS INT) AS turn_idx,
  REPLACE(CAST(json_extract(turn, '$.role') AS VARCHAR), '"', '') AS role,
  COALESCE(SUBSTR(CAST(json_extract(turn, '$.content') AS VARCHAR), 1, 120), '') AS content,
  COALESCE(SUBSTR(CAST(json_extract(turn, '$.thinking') AS VARCHAR), 1, 200), '') AS thinking,
  CAST(json_extract(turn, '$.tool_calls_in_turn') AS VARCHAR) AS tc_ids_raw
FROM sessions_base,
     UNNEST(turns) AS t(turn)
ORDER BY turn_idx
```

The `tool_calls_in_turn` field is a JSON array of tool call IDs. You parse it in JS with `JSON.parse()` and look up each ID in a pre-built map of tool call details.

### Querying session metadata

For aggregate session info, query a single column:

```sql
SELECT
  environment->>'model' AS model,
  CAST(metrics->>'turn_count' AS INT) AS turns,
  CAST(metrics->>'tool_call_count' AS INT) AS tools,
  ROUND(CAST(timing->>'duration_seconds' AS DOUBLE), 0) AS duration_s,
  classification
FROM sessions_base
```

Use `->>'model'` for `environment` because it is a JSON column (not VARCHAR). Use `metrics->>'turn_count'` the same way.

## Stage 3: Composing Diagram DSL JSON

### The Diagram DSL

The Diagram DSL is a JSON format for poster-style diagrams. A page has a title, subtitle, column layout, and an array of rows. Each row has a diagram on the left and notes on the right.

```json
{
  "page": {
    "title": "Pi Session Analysis",
    "subtitle": "umans-qwen3.6-35b-a3b · internal · 75s",
    "columns": { "diagram": 58, "notes": 42 }
  },
  "rows": [
    { "diagram": { ... }, "notes": { "heading": "...", "body": ["..."] } }
  ]
}
```

There are four diagram types:

**`strip`** — horizontal band with segments. Each segment has a `label`, `kind`, and relative `width`. Useful for turn flows and distributions.

```json
{
  "type": "strip",
  "caption": "7 turns · 12 tool calls · 75s",
  "segments": [
    { "label": "user input", "kind": "active", "width": 10 },
    { "kind": "separator" },
    { "label": "agent planning", "kind": "generated", "width": 4 },
    { "label": "tool execution", "kind": "active", "width": 40 },
    { "label": "result synthesis", "kind": "generated", "width": 30 },
    { "kind": "separator" },
    { "label": "model", "kind": "context", "width": 16 }
  ],
  "annotations": [
    { "text": "3 reads, 8 bash, 1 write", "to": "tool execution", "side": "bottom" }
  ]
}
```

**`stack`** — vertical layers. Each layer has a `label`, `kind`, and relative `height`. Useful for tool distributions.

```json
{
  "type": "stack",
  "caption": "tool usage (12 calls total)",
  "layers": [
    { "label": "read", "kind": "context", "height": 3 },
    { "label": "bash", "kind": "generated", "height": 8 },
    { "label": "write", "kind": "context", "height": 1 }
  ]
}
```

**`loop`** — perceive/think/act/observe cycle. Four fixed steps arranged in a ring.

```json
{
  "type": "loop",
  "steps": [
    { "id": "perceive", "label": "perceive", "note": "read input" },
    { "id": "think",    "label": "think",    "note": "process context" },
    { "id": "act",      "label": "act",      "note": "call tool" },
    { "id": "observe",  "label": "observe",  "note": "receive result" }
  ],
  "highlight": "think"
}
```

**`transition`** — before/after comparison. Two states with an arrow between them. Useful for showing context window changes.

### Writing JS command handlers

The recommended approach for composing diagram JSON is to use a JS command handler. It runs inside go-minitrace's DuckDB-powered runtime, has access to `mt.query()` and `mt.queryOne()`, and can assemble complex output in JavaScript.

A command handler has three parts: the section declaration, the function, and the verb registration.

```javascript
__section__("filters", {
  fields: {},
});

function sessionToDiagram(filters) {
  const mt = require("minitrace");

  // Query tool usage
  const tools = mt.query(`
    SELECT
      REPLACE(CAST(json_extract(tc, '$.tool_name') AS VARCHAR), '"', '') AS tool,
      json_extract(tc, '$.operation_type') AS op_type
    FROM sessions_base,
         UNNEST(tool_calls) AS t(tc)
    ORDER BY CAST(json_extract(tc, '$.id') AS VARCHAR)
  `);

  // Query turn structure
  const turns = mt.query(`
    SELECT
      CAST(json_extract(turn, '$.index') AS INT) AS turn_idx,
      REPLACE(CAST(json_extract(turn, '$.role') AS VARCHAR), '"', '') AS role,
      CAST(json_extract(turn, '$.tool_calls') AS VARCHAR) AS has_tools
    FROM sessions_base,
         UNNEST(turns) AS t(turn)
    ORDER BY turn_idx
  `);

  // Query session metadata
  const meta = mt.queryOne(`
    SELECT
      environment->>'model' AS model,
      CAST(metrics->>'turn_count' AS INT) AS turns,
      CAST(metrics->>'tool_call_count' AS INT) AS tools,
      ROUND(CAST(timing->>'duration_seconds' AS DOUBLE), 0) AS duration_s,
      classification
    FROM ${mt.tableName}
  `);

  // Infer quality tier from metrics
  const quality = (meta.turns > 5 && meta.tools > 10) ? 'A' :
                  (meta.turns > 1 && meta.tools > 0) ? 'B' : 'C';

  // Count tools
  const toolCounts = {};
  for (const row of tools) {
    const key = row.tool;
    toolCounts[key] = (toolCounts[key] || 0) + 1;
  }

  const rows = [];

  // Row 1: Strip diagram — Turn flow
  rows.push({
    diagram: {
      type: "strip",
      caption: `${meta.turns} turns · ${meta.tools} tool calls · ${meta.duration_s}s`,
      segments: [
        { label: "user input", kind: "active", width: 10 },
        { kind: "separator" },
        { label: "agent planning", kind: "generated", width: 4 },
        { label: "tool execution", kind: "active", width: 40 },
        { label: "result synthesis", kind: "generated", width: 30 },
        { kind: "separator" },
        { label: "model", kind: "context", width: 16 },
      ],
    },
    notes: {
      heading: "1. Session Flow",
      body: [
        `The agent processed a single user request across ${meta.turns} turns and ${meta.tools} tool invocations.`,
        `Model: ${meta.model}. Duration: ${meta.duration_s}s. Quality: ${quality}.`
      ]
    }
  });

  // Row 2: Stack diagram — Tool distribution
  const stackLayers = Object.keys(toolCounts).map((name, i) => ({
    label: name,
    kind: i % 2 === 0 ? "context" : "generated",
    height: Math.max(toolCounts[name], 1),
  }));
  rows.push({
    diagram: {
      type: "stack",
      caption: `tool usage (${Object.values(toolCounts).reduce((a, b) => a + b, 0)} calls total)`,
      layers: stackLayers.length > 0 ? stackLayers : [{ label: "no tools", kind: "empty", height: 1 }],
    },
    notes: {
      heading: "2. Tool Distribution",
      body: Object.entries(toolCounts).map(([n, c]) => `${n}: ${c} call${c > 1 ? 's' : ''}`).concat(
        [`Total: ${Object.values(toolCounts).reduce((a, b) => a + b, 0)} tool calls across ${Object.keys(toolCounts).length} tool types`]
      )
    }
  });

  // Row 3: Loop diagram — Perceive-Think-Act-Observe
  rows.push({
    diagram: {
      type: "loop",
      steps: [
        { id: "perceive", label: "perceive", note: "read input / skills" },
        { id: "think",    label: "think",    note: "plan & select tools" },
        { id: "act",      label: "act",      note: "execute (bash/read/write)" },
        { id: "observe",  label: "observe",  note: "inspect results" },
      ],
      highlight: "think",
      center: `${meta.turns} iterations`,
    },
    notes: {
      heading: "3. Agent Cycle",
      body: [
        "The Pi agent loops through perceive → think → act → observe.",
        `Each turn involves reading context (${toolCounts["read"] || 0} reads), executing commands (${toolCounts["bash"] || 0} bash calls), and writing results (${toolCounts["write"] || 0} writes).`,
        "The agent classified this session as internal quality A."
      ]
    }
  });

  return JSON.stringify({
    page: {
      title: "Pi Session Analysis",
      subtitle: `${meta.model} · ${meta.classification} · ${meta.duration_s}s`,
      columns: { diagram: 58, notes: 42 },
    },
    rows,
  }, null, 2);
}

__verb__("sessionToDiagram", {
  name: "session-diagram",
  short: "Generate diagram DSL JSON from a Pi session",
  fields: { filters: { bind: "filters" } },
});
```

### Directory structure for discovery

go-minitrace discovers JS command handlers by scanning a repository directory. The file must be in a subdirectory matching the `__section__` name:

```
query-commands/
  analysis/
    diagram-gen.js       → go-minitrace query commands analysis diagram-gen session-diagram
    turn-by-turn.js      → go-minitrace query commands analysis turn-by-turn
```

If a JS file defines exactly one verb with the same name as the file stem (minus `.js`), go-minitrace collapses the redundant level. The file `diagram-gen.js` with verb `sessionToDiagram` requires the full path `analysis diagram-gen session-diagram` because the verb name doesn't match the file stem. If the file were named `session-diagram.js` with verb `session-diagram`, the command would be `go-minitrace query commands analysis session-diagram`.

### Running the command

```bash
go-minitrace query commands \
  --query-repository ./query-commands \
  analysis session-diagram \
  --archive-glob './minitrace-output/active/*/*.minitrace.json' \
  --output json
```

The output is an array with a single row containing a `value` field with the JSON string. Extract it with `jq`:

```bash
go-minitrace query commands \
  --query-repository ./query-commands \
  analysis session-diagram \
  --archive-glob './minitrace-output/active/*/*.minitrace.json' \
  --output json | jq '.[0].value | fromjson' > session-diagram.json
```

## The Turn-by-Turn Diagram

The abstract diagrams above show aggregated views. For a detailed per-turn breakdown, you need a different approach that joins turns to their tool calls.

### The join pattern

Each turn has a `tool_calls_in_turn` array of tool call IDs. Each tool call has an `id` field. To join them, build a lookup map in JS:

```javascript
// Query turns
const turns = mt.query(`
  SELECT
    CAST(json_extract(turn, '$.index') AS INT) AS turn_idx,
    REPLACE(CAST(json_extract(turn, '$.role') AS VARCHAR), '"', '') AS role,
    COALESCE(SUBSTR(CAST(json_extract(turn, '$.content') AS VARCHAR), 1, 120), '') AS content,
    COALESCE(SUBSTR(CAST(json_extract(turn, '$.thinking') AS VARCHAR), 1, 200), '') AS thinking,
    CAST(json_extract(turn, '$.tool_calls_in_turn') AS VARCHAR) AS tc_ids_raw
  FROM ${mt.tableName},
       UNNEST(turns) AS t(turn)
  ORDER BY turn_idx
`);

// Query tool call details — extract fields directly
const toolCalls = mt.query(`
  SELECT
    REPLACE(CAST(json_extract(tc, '$.id') AS VARCHAR), '"', '') AS tc_id,
    REPLACE(CAST(json_extract(tc, '$.tool_name') AS VARCHAR), '"', '') AS tool_name,
    CAST(json_extract(tc, '$.input.file_path') AS VARCHAR) AS input_file_path,
    CAST(json_extract(tc, '$.input.command') AS VARCHAR) AS input_command,
    CAST(json_extract(json_extract(tc, '$.input'), '$.arguments.path') AS VARCHAR) AS input_arg_path,
    CAST(json_extract(tc, '$.output.result') AS VARCHAR) AS output_result,
    CAST(json_extract(tc, '$.output.error') AS VARCHAR) AS output_error,
    CAST(json_extract(tc, '$.output.success') AS VARCHAR) AS output_success
  FROM ${mt.tableName},
       UNNEST(tool_calls) AS t(tc)
`);

// Build lookup: tc_id -> tool call
const tcMap = {};
for (const tc of toolCalls) {
  tcMap[tc.tc_id] = tc;
}
```

Then iterate over turns, parse the `tool_calls_in_turn` array, and look up each tool call in `tcMap`.

### Handling polymorphic inputs

The `input` field varies by tool type:

| Tool | input.file_path | input.command | input.arguments |
|------|-----------------|---------------|-----------------|
| `read` | ✓ | null | path, justification |
| `bash` | null | ✓ | command, file_path |
| `write` | ✓ | null | path, content, justification |

The query extracts all possible fields, and the JS code selects the right one based on `tool_name`:

```javascript
function getFilePath(tc) {
  if (tc.input_file_path) return tc.input_file_path;
  if (tc.input_arg_path) return tc.input_arg_path;
  return "(unknown)";
}

for (const tcId of tcIds) {
  const tc = tcMap[tcId];
  if (!tc) continue;

  if (tc.tool_name === "read") {
    const fp = getFilePath(tc);
    // ... handle read
  } else if (tc.tool_name === "bash") {
    const cmd = tc.input_command || "";
    // ... handle bash
  } else if (tc.tool_name === "write") {
    const fp = getFilePath(tc);
    // ... handle write
  }
}
```

### Output format for turn-by-turn

Each turn becomes a strip diagram. For user turns, the diagram has one `user input` segment with the full prompt as an annotation. For assistant turns, the diagram has a `think` segment followed by a `separator` and one segment per tool call, with file paths and commands as annotations.

```json
{
  "page": {
    "title": "Turn-by-Turn Session Detail",
    "subtitle": "umans-qwen3.6-35b-a3b",
    "columns": { "diagram": 58, "notes": 42 }
  },
  "rows": [
    {
      "diagram": {
        "type": "strip",
        "caption": "turn 0 · user",
        "segments": [
          { "label": "user input", "kind": "active", "width": 100 }
        ],
        "annotations": [
          { "text": "Use go-minitrace help --all and then use it...", "to": "user input", "side": "bottom" }
        ]
      },
      "notes": {
        "heading": "Turn 0 — User Prompt",
        "body": ["Use go-minitrace help --all and then use it..."]
      }
    },
    {
      "diagram": {
        "type": "strip",
        "caption": "turn 1 · assistant · 4 tools",
        "segments": [
          { "label": "think", "kind": "generated", "width": 20 },
          { "kind": "separator" },
          { "label": "read", "kind": "context", "width": 20 },
          { "label": "read", "kind": "context", "width": 20 },
          { "label": "read", "kind": "context", "width": 20 },
          { "label": "bash", "kind": "active", "width": 20 }
        ],
        "annotations": [
          { "text": "~/.pi/agent/skills/go-minitrace-transcript-analysis/SKILL.md", "to": "read", "side": "bottom" },
          { "text": "~/code/wesen/claw-stuff/AGENTS.md", "to": "read", "side": "bottom" },
          { "text": "~/Downloads/diagram-dsl-spec.md", "to": "read", "side": "bottom" },
          { "text": "go-minitrace help --all 2>&1", "to": "bash", "side": "bottom" }
        ]
      },
      "notes": {
        "heading": "Turn 1 — Assistant",
        "body": [
          "Response: \"I'll start by loading the relevant skills and gathering information in parallel.\"",
          "Thinking: Let me break down this request:...",
          "Read: ~/.pi/agent/skills/go-minitrace-transcript-analysis/SKILL.md",
          "Read: ~/code/wesen/claw-stuff/AGENTS.md",
          "Read: ~/Downloads/diagram-dsl-spec.md",
          "Bash: go-minitrace help --all 2>&1"
        ]
      }
    }
  ]
}
```

## Complete Scripts

### Ad-hoc SQL: analyze-session.sql

```sql
-- Analyze the session to build diagram DSL rows
-- Row 1: Turn structure (strip)
SELECT
  id,
  CAST(metrics->>'turn_count' AS INT) AS turn_count,
  CAST(metrics->>'tool_call_count' AS INT) AS tool_call_count,
  environment->>'model' AS model,
  ROUND(CAST(timing->>'duration_seconds' AS DOUBLE), 0) AS duration_s,
  REPLACE(CAST(json_extract(tc, '$.tool_name') AS VARCHAR), '"', '') AS tool,
  json_extract(tc, '$.operation_type') AS op_type
FROM sessions_base,
     UNNEST(tool_calls) AS t(tc)
```

Run with:
```bash
go-minitrace query duckdb \
  --archive-glob './minitrace-output/active/*/*.minitrace.json' \
  --sql-file ./scripts/01-analyze-session.sql
```

### JS: diagram-gen.js (abstract summary view)

This script produces three diagram rows: a strip showing the session flow, a stack showing tool distribution, and a loop showing the perceive-think-act-observe cycle. The full script is in the `scripts/analysis/diagram-gen.js` file.

### JS: turn-by-turn.js (detailed per-turn view)

This script produces one strip diagram per turn, showing the user prompt, assistant response, thinking text, and each tool call with its file path or command. The full script is in `scripts/analysis/turn-by-turn.js`.

## Common Pitfalls

### The `quality` column is not in DuckDB

This is the most common point of confusion. The `quality` field (A/B/C) lives in the manifest file, not in the DuckDB table. The `buildLoadSQL()` function explicitly defines which top-level fields become columns, and `quality` is not among them. To work around this, infer quality from metrics:

```
quality A: turn_count > 5 AND tool_call_count > 10
quality B: turn_count > 1 AND tool_call_count > 0
quality C: everything else
```

### `--archive-glob` must go after the command verb

The `--archive-glob` flag goes AFTER the full command path, not before it:

```bash
# Correct:
go-minitrace query commands analysis session-diagram \
  --archive-glob './minitrace-output/active/*/*.minitrace.json'

# Wrong (flag not recognized):
go-minitrace query commands \
  --archive-glob './minitrace-output/active/*/*.minitrace.json' \
  analysis session-diagram
```

### `__section__` must use a built-in name

The section name must be one of the built-in sections (`filters`, `analysis`, `overview`). Using an arbitrary name like `__section__("diagram")` will fail with "references unknown section 'diagram'".

### The file must be in the matching subdirectory

A JS file with `__section__("filters")` must be in a `filters/` subdirectory. A file in `analysis/` with `__section__("filters")` will not be discovered.

### Don't cast entire `input`/`output` to VARCHAR

Casting the entire `input` or `output` JSON object to VARCHAR and then calling `JSON.parse()` in JS will fail because DuckDB double-escapes the JSON. Always extract individual sub-fields with `json_extract(tc, '$.input.file_path')` and cast those individually.

### `->>` vs `json_extract()` in JS handlers

In pure SQL queries, `REPLACE(CAST(json_extract(tc, '$.tool_name') AS VARCHAR), '"', '')` is the standard pattern because DuckDB's `CAST(VARCHAR)` adds quotes. In JS command handlers, `call->>'tool_name'` is preferred because the JSON arrow operator returns the string directly without the quoting layer.

## Summary of the Pipeline

```
raw JSONL ──convert pi──→ .minitrace.json ──query duckdb──→ DuckDB table
                                                        │
                                                  UNNEST tool_calls
                                                  UNNEST turns
                                                  json_extract fields
                                                        │
                                                  JS command handler
                                                  (mt.query + mt.queryOne)
                                                        │
                                               assemble diagram DSL JSON
                                                        │
                                              jq '.[0].value | fromjson'
                                                        │
                                              session-diagram.json
                                              session-turns.json
```

The key insight is that every stage has a fixed interface. The converter produces `.minitrace.json`. DuckDB loads it into a table with known columns. SQL queries `UNNEST` and `json_extract` to extract data. JavaScript handlers compose that data into diagram JSON. Understanding the data flow between stages — and knowing the right `json_extract()` paths for tool call fields — is what makes the whole pipeline work.

## Working Rules

- Always extract tool call fields individually via `json_extract(tc, '$.input.file_path')`. Never cast the entire `input` or `output` to VARCHAR and parse in JS.
- In JS command handlers, use `call->>'tool_name'` instead of `REPLACE(CAST(json_extract(...), '"', ''))` for cleaner code.
- Infer quality from metrics: `turn_count > 5 AND tool_call_count > 10` means quality A.
- The `tool_calls_in_turn` array on turns links to tool call IDs. Build a `tcMap` lookup in JS for the join.
- Section names must be built-in (`filters`, `analysis`, `overview`). Files must be in matching subdirectories.
- `--archive-glob` goes AFTER the command verb, not before it.
- Use `COALESCE(SUBSTR(CAST(json_extract(...), 1, N), ''), '')` to safely truncate text fields.
