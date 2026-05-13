---
title: "Document Co-Read Observatory — Transcript Mining to Recommender Workbench"
aliases:
  - Document Co-Read Observatory
  - Document Co-Read Recommender Report
  - go-minitrace Document Relationship Mining
  - Transcript Document Recommender Workbench
tags:
  - project-report
  - article
  - go-minitrace
  - pi
  - transcripts
  - recommender-systems
  - document-graphs
  - dashboard
  - javascript
  - duckdb
status: active
type: project-report
created: 2026-05-13
repo: /home/manuel/code/wesen/trace-analysis
source_ticket: DOC-COREAD-RECOMMENDER-2026-05-13
source_ticket_dir: /home/manuel/code/wesen/trace-analysis/ttmp/2026/05/13/DOC-COREAD-RECOMMENDER-2026-05-13--document-co-read-analysis-and-recommender-design
related_docs:
  - /home/manuel/code/wesen/trace-analysis/ttmp/2026/05/13/DOC-COREAD-RECOMMENDER-2026-05-13--document-co-read-analysis-and-recommender-design/design/01-document-co-read-analysis-and-recommender-design-guide.md
  - /home/manuel/code/wesen/trace-analysis/ttmp/2026/05/13/DOC-COREAD-RECOMMENDER-2026-05-13--document-co-read-analysis-and-recommender-design/design/02-document-coread-observatory-implementation-guide.md
  - /home/manuel/code/wesen/trace-analysis/ttmp/2026/05/13/DOC-COREAD-RECOMMENDER-2026-05-13--document-co-read-analysis-and-recommender-design/scripts/query-commands/docs/coread.js
  - /home/manuel/code/wesen/trace-analysis/ttmp/2026/05/13/DOC-COREAD-RECOMMENDER-2026-05-13--document-co-read-analysis-and-recommender-design/dashboard/index.html
commits:
  - c7554397b3497abe294c589bd0ba75536fbaf074
  - 37c266ae72f592b104eabd1ea79f8a3e504819d5
  - ce5dce7e7c4072f9a32bd5a98b5810fb8c678813
  - c81aedd5a25cbca2fec3c0f4a91032cc4cecf14b
---

# Document Co-Read Observatory — Transcript Mining to Recommender Workbench

This project report explains the document co-read analysis work in `trace-analysis`. The project starts with a practical question: when a coding agent reads one document, what other documents are usually useful nearby? The answer is not available in a single source file or ticket. It has to be recovered from transcript history, because transcript history records the documents the agent actually opened while performing real tasks.

The result is a first version of a document relationship mining system. It extracts document-like `read` tool calls from go-minitrace session archives, classifies the paths, computes co-read relationships, exposes the analysis through reusable JavaScript query verbs, and renders the result in a local dashboard called the Document Co-Read Observatory.

> [!summary]
> The project converts Pi transcript history into a document interaction graph. Nodes are documents, and weighted edges mean that two documents were read close together in coding-agent sessions.
>
> The implementation uses go-minitrace JavaScript query commands backed by DuckDB. The important verbs are `read-events`, `doc-frequency`, `global-pairs`, `session-pairs`, `recommend`, `association-rules`, `graph`, and `session-timeline`.
>
> The dashboard is a static local application generated from JSON exports. It lets a reader inspect document frequencies, association rules, graph edges, and session-level read timelines before turning the analysis into a runtime recommender.

## Why this project exists

Coding agents routinely consult local documents: skills, README files, design documents, ticket diaries, implementation guides, and project reports. Those reads are not random. A docmgr task often reads the docmgr skill, then a diary skill, then reMarkable upload instructions, then a ticket design file. A frontend review task may read Storybook notes, visual-diff playbooks, and component architecture reports. A go-minitrace task may read the transcript-analysis skill, minitrace schema docs, and query command examples.

Those patterns are operational knowledge. They answer questions that are difficult to encode manually:

- Which skills are usually loaded together?
- Which ticket documents are read in the same task segment?
- Which README files precede deeper design documents?
- Which documents are workflow hubs, and which documents are specific companions?
- If a future agent reads a document, what else should it consider reading next?

The project treats transcript history as implicit feedback. A document read is a weak signal that the document mattered to a task. A close co-read is a stronger signal that two documents were relevant in the same local context. Repeated close co-reads across sessions become recommendation evidence.

## Source material

The source material is the local Pi transcript archive converted into go-minitrace format. The first implementation reused the converted archive from the previous cache-analysis ticket:

```text
/home/manuel/code/wesen/trace-analysis/ttmp/2026/05/13/CACHE-HITS-PROGRESSION-2026-05-13--analyze-prompt-cache-hits-across-conversation-progression/analysis/pi/active/*/*.minitrace.json
```

The new ticket lives at:

```text
/home/manuel/code/wesen/trace-analysis/ttmp/2026/05/13/DOC-COREAD-RECOMMENDER-2026-05-13--document-co-read-analysis-and-recommender-design
```

The most important project files are:

```text
scripts/01-doc-read-events.sql
scripts/02-global-coread-pairs.sql
scripts/query-commands/docs/coread.js
scripts/03-generate-doc-coread-dashboard-data.sh
scripts/04-serve-doc-coread-dashboard.sh
dashboard/index.html
design/01-document-co-read-analysis-and-recommender-design-guide.md
design/02-document-coread-observatory-implementation-guide.md
reference/01-investigation-diary.md
```

The project was committed incrementally:

| Commit | Purpose |
|---|---|
| `c755439` | Initial document co-read ticket, SQL scripts, JS verbs, samples, and design guide. |
| `37c266a` | Detailed observatory implementation guide and task breakdown. |
| `ce5dce7` | Association-rule, graph, and session-timeline verbs. |
| `c81aedd` | Dashboard generator, server helper, and dashboard UI. |

## The transcript analysis model

A go-minitrace archive stores a session as structured JSON. For this project, the important field is `tool_calls`. A tool call records what the agent invoked, when it invoked it, and what arguments were passed. A file read appears as a tool call whose `tool_name` is `read` or whose `operation_type` is `READ`.

The tool-call shape looks like this:

```json
{
  "tool_name": "read",
  "operation_type": "READ",
  "emitting_turn_index": 33,
  "timestamp": "2026-04-23T20:00:01.457Z",
  "input": {
    "arguments": {
      "path": "/home/manuel/.pi/agent/skills/docmgr/SKILL.md"
    },
    "file_path": "/home/manuel/.pi/agent/skills/docmgr/SKILL.md"
  },
  "output": {
    "success": true,
    "error": null
  }
}
```

The extractor uses three path fields because different adapters and conversions may place the path in different locations:

```text
input.arguments.path
input.file_path
input.path
```

The extraction logic chooses the first non-empty value. It then normalizes `~` to `/home/manuel`, extracts a file extension, and classifies the path into a document kind.

The first attempt used `tool_calls[].context.position_in_session` to order reads. Inspection showed that this value could be zero for many calls. The implementation now uses DuckDB ordinality instead:

```sql
FROM sessions_base s,
     UNNEST(s.tool_calls) WITH ORDINALITY AS u(tc, ord)
```

The `ord` value becomes `tool_seq`. This is the stable order used for proximity windows.

## Document classification

The first version uses path heuristics. This is the correct starting point because minitrace records file paths, not semantic document identities.

The classifier produces these kinds:

| Kind | Rule |
|---|---|
| `skill` | `SKILL.md` under `.pi/agent/skills` or `.agents/skills`. |
| `docmgr-ticket` | Documentation-like file under a `ttmp/` ticket workspace. |
| `docs-tree` | Documentation-like file under a repository `docs/` directory. |
| `readme` | `README.md` or README variants. |
| `markdown` | Other Markdown or MDX file. |
| `text-doc` | `rst`, `adoc`, or `txt` file. |

The classifier deliberately excludes most source files. This detail matters because docmgr tickets often include source snapshots under `ttmp/.../sources/`. A path can contain `ttmp/` and still be a C, Go, or TypeScript source file. The recommender should not treat those files as documentation unless the mode explicitly asks for source recommendations.

The essential pseudocode is:

```pseudo
for each session in minitrace_archive:
    for each tool_call with ordinality:
        if tool_call is not read-like:
            continue

        path = first_non_empty(
            tool_call.input.arguments.path,
            tool_call.input.file_path,
            tool_call.input.path,
        )

        if path is empty:
            continue

        path_norm = normalize_home(path)
        extension = extension(path_norm)
        doc_kind = classify(path_norm, extension)

        if doc_kind == other_read:
            continue

        if extension is not documentation_like and doc_kind not in {skill, readme}:
            continue

        if output.success is false:
            continue

        emit document_read_event
```

The emitted event contains:

```text
session_id
session_title
provider
session_model
session_turns
tool_seq
emitting_turn_index
timestamp
path_raw
path_norm
extension
doc_kind
success
error
```

The actual extraction SQL is a four-stage CTE. The first stage extracts candidate read calls and gives every tool call an ordinal. The second stage normalizes paths. The third stage classifies the path. The fourth stage filters to documentation-like files.

```sql
WITH read_calls AS (
  SELECT
    s.id AS session_id,
    COALESCE(s.title, '') AS session_title,
    s.environment->>'provider_hint' AS provider,
    s.environment->>'model' AS session_model,
    ord AS tool_seq,
    TRY_CAST(tc->>'emitting_turn_index' AS BIGINT) AS emitting_turn_index,
    tc->>'timestamp' AS timestamp,
    COALESCE(
      tc->'input'->'arguments'->>'path',
      tc->'input'->>'file_path',
      tc->'input'->>'path'
    ) AS path_raw,
    TRY_CAST(tc->'output'->>'success' AS BOOLEAN) AS success
  FROM sessions_base s,
       UNNEST(s.tool_calls) WITH ORDINALITY AS u(tc, ord)
  WHERE lower(COALESCE(tc->>'tool_name', '')) = 'read'
     OR upper(COALESCE(tc->>'operation_type', '')) = 'READ'
), normalized AS (
  SELECT
    *,
    regexp_replace(path_raw, '^~', '/home/manuel') AS path_norm,
    lower(regexp_extract(COALESCE(path_raw, ''), '\.[A-Za-z0-9]+$', 0)) AS extension_with_dot
  FROM read_calls
  WHERE path_raw IS NOT NULL AND path_raw <> ''
), classified AS (
  SELECT
    *,
    regexp_replace(extension_with_dot, '^\.', '') AS extension,
    CASE
      WHEN lower(path_norm) LIKE '%/.pi/agent/skills/%/skill.md'
        OR lower(path_norm) LIKE '%/.agents/skills/%/skill.md' THEN 'skill'
      WHEN lower(path_norm) LIKE '%/ttmp/%' THEN 'docmgr-ticket'
      WHEN lower(path_norm) LIKE '%/docs/%' THEN 'docs-tree'
      WHEN lower(path_norm) LIKE '%/readme.md'
        OR lower(path_norm) LIKE '%/readme.%' THEN 'readme'
      WHEN regexp_replace(extension_with_dot, '^\.', '') IN ('md', 'mdx', 'markdown') THEN 'markdown'
      WHEN regexp_replace(extension_with_dot, '^\.', '') IN ('rst', 'adoc', 'txt') THEN 'text-doc'
      ELSE 'other-read'
    END AS doc_kind
  FROM normalized
), doc_reads AS (
  SELECT *
  FROM classified
  WHERE doc_kind <> 'other-read'
    AND (
      extension IN ('md', 'mdx', 'markdown', 'rst', 'adoc', 'txt')
      OR doc_kind IN ('skill', 'readme')
    )
    AND COALESCE(success, true)
)
```

The last condition is important. It prevents source files inside ticket workspaces from entering the document graph simply because their paths contain `ttmp/`.

## Building the first SQL scripts

The first SQL script, `scripts/01-doc-read-events.sql`, extracts the document read events. It exists for two reasons. First, it is the most direct way to validate the minitrace schema. Second, it gives future readers a readable DuckDB query that does not require understanding the JavaScript query-command layer.

The second SQL script, `scripts/02-global-coread-pairs.sql`, computes global close co-read pairs. A pair is counted when two different documents appear in the same session within a bounded tool-call and turn window:

```text
same session
AND different document paths
AND later tool call is within windowTools calls
AND later emitting turn is within windowTurns turns
```

The starter defaults are:

```text
windowTools = 100
windowTurns = 20
minSessions = 2
```

Those defaults are not a claim about the correct semantic boundary. They are working parameters. The dashboard exposes the results so the team can inspect whether the window is too narrow or too broad.

The pair query uses a self-join over `doc_reads`. The `a.tool_seq < b.tool_seq` condition avoids duplicate event pairs, while `LEAST` and `GREATEST` canonicalize the unordered pair identity.

```sql
pairs AS (
  SELECT
    a.session_id,
    LEAST(a.path_norm, b.path_norm) AS doc_a,
    GREATEST(a.path_norm, b.path_norm) AS doc_b,
    ABS(b.tool_seq - a.tool_seq) AS tool_distance,
    ABS(
      COALESCE(b.emitting_turn_index, b.tool_seq)
      - COALESCE(a.emitting_turn_index, a.tool_seq)
    ) AS turn_distance
  FROM doc_reads a
  JOIN doc_reads b
    ON a.session_id = b.session_id
   AND a.path_norm <> b.path_norm
   AND a.tool_seq < b.tool_seq
   AND ABS(b.tool_seq - a.tool_seq) <= 100
   AND ABS(
     COALESCE(b.emitting_turn_index, b.tool_seq)
     - COALESCE(a.emitting_turn_index, a.tool_seq)
   ) <= 20
)
SELECT
  doc_a,
  doc_b,
  COUNT(*) AS pair_events,
  COUNT(DISTINCT session_id) AS sessions,
  ROUND(AVG(tool_distance), 2) AS avg_tool_distance,
  ROUND(AVG(turn_distance), 2) AS avg_turn_distance
FROM pairs
GROUP BY doc_a, doc_b
HAVING COUNT(DISTINCT session_id) >= 2
```

This query gives the first graph edge table. It does not yet know about confidence, lift, or PMI. Those metrics are added in the JavaScript command layer.

## Moving from SQL to JavaScript go-minitrace verbs

SQL is enough for extraction and pair counting, but the project is intended to become a reusable analysis surface. The JavaScript query-command layer is the right place for that because it provides named verbs, typed flags, reusable helper functions, and richer command composition.

The command file is:

```text
scripts/query-commands/docs/coread.js
```

It defines shared sections and helper functions:

```js
__section__("filters", {
  fields: {
    provider: { type: "stringList" },
    model: { type: "stringList" },
    sessionId: { type: "string" },
    docKind: { type: "stringList" },
    pathLike: { type: "string" },
    includeSkills: { type: "bool", default: true },
    windowTools: { type: "int", default: 100 },
    windowTurns: { type: "int", default: 20 },
    minSessions: { type: "int", default: 2 },
    limit: { type: "int", default: 100 },
  },
});
```

The key helper is `docReadsCte(filters, options)`. It returns a SQL common table expression with four stages:

```text
read_calls -> normalized -> classified -> doc_reads
```

This keeps every verb consistent. `read-events`, `doc-frequency`, `global-pairs`, `recommend`, `association-rules`, `graph`, and `session-timeline` all use the same extraction and classification rules.

The command file uses small JS helpers to assemble SQL safely. This is the pattern used throughout the file:

```js
function docFilter(filters, options) {
  const mt = require("minitrace");
  const clauses = [];
  const ignorePathLike = options?.ignorePathLike === true;

  if (filters.docKind?.length) {
    clauses.push(`doc_kind IN (${mt.sql.stringIn(filters.docKind)})`);
  }
  if (!ignorePathLike && filters.pathLike) {
    clauses.push(`lower(path_norm) LIKE ${mt.sql.like(String(filters.pathLike).toLowerCase())}`);
  }
  if (filters.includeSkills === false) {
    clauses.push(`doc_kind <> 'skill'`);
  }

  return clauses.length ? `AND ${clauses.join(" AND ")}` : "";
}
```

The `recommend` verb uses the same base CTE, but it deliberately ignores `pathLike` during extraction. It applies `pathLike` only to seed rows. That bug was found during implementation: applying `pathLike` to the whole CTE removed every possible neighbor.

```js
function recommend(filters) {
  const mt = require("minitrace");
  if (!filters.pathLike) {
    throw new Error("recommend requires --pathLike to identify the seed document/path substring");
  }

  return mt.query(`${docReadsCte(filters, { ignorePathLike: true })}
, seed_reads AS (
  SELECT *
  FROM doc_reads
  WHERE lower(path_norm) LIKE ${mt.sql.like(String(filters.pathLike).toLowerCase())}
), neighbors AS (
  SELECT
    s.path_norm AS seed_doc,
    d.path_norm AS neighbor_doc,
    d.doc_kind AS neighbor_kind,
    s.session_id,
    ABS(d.tool_seq - s.tool_seq) AS tool_distance
  FROM seed_reads s
  JOIN doc_reads d
    ON s.session_id = d.session_id
   AND s.path_norm <> d.path_norm
   AND ABS(d.tool_seq - s.tool_seq) <= 100
)
SELECT neighbor_doc, COUNT(DISTINCT session_id) AS sessions
FROM neighbors
GROUP BY neighbor_doc
ORDER BY sessions DESC`);
}
```

The first JS verbs were:

```text
docs coread read-events
docs coread doc-frequency
docs coread global-pairs
docs coread session-pairs
docs coread recommend
```

The second implementation pass added:

```text
docs coread association-rules
docs coread graph
docs coread session-timeline
```

## Association rules

Raw co-read counts are useful, but they are biased toward common documents. The association-rule verb adds directional metrics.

The relevant quantities are:

```text
N = number of sessions with document reads
sessions(A) = number of sessions where A appears
sessions(B) = number of sessions where B appears
support(A,B) = number of sessions where A and B are close co-reads
```

The directional metrics are:

```text
confidence(A => B) = support(A,B) / sessions(A)
lift(A => B) = confidence(A => B) / (sessions(B) / N)
PMI(A,B) = log2( (support(A,B) / N) / ((sessions(A) / N) * (sessions(B) / N)) )
```

The row shape is:

```text
seed_doc
seed_kind
candidate_doc
candidate_kind
support_sessions
seed_sessions
candidate_sessions
pair_events
confidence
lift
pmi
avg_tool_distance
avg_turn_distance
hybrid_score
```

The `hybrid_score` is intentionally simple:

```text
hybrid_score =
    1.5 * log1p(support_sessions)
  + confidence
  + log1p(lift)
  + 0.5 * max(pmi, 0)
  - 0.05 * avg_turn_distance
```

This score is not final recommender science. It is an inspectable default. The dashboard lets a user sort by support, confidence, lift, PMI, or hybrid score. That is important because each metric teaches a different property of the document graph.

The `association-rules` verb implements the calculation with a sequence of CTEs. The key move is to build undirected close-pair support, then expand each pair into two directional rows.

```sql
session_docs AS (
  SELECT DISTINCT session_id, path_norm AS doc, doc_kind
  FROM doc_reads
), totals AS (
  SELECT COUNT(DISTINCT session_id) AS total_sessions
  FROM doc_reads
), doc_counts AS (
  SELECT doc, COUNT(DISTINCT session_id) AS doc_sessions
  FROM session_docs
  GROUP BY doc
), pair_counts AS (
  SELECT
    doc_a,
    doc_b,
    COUNT(*) AS pair_events,
    COUNT(DISTINCT session_id) AS support_sessions
  FROM undirected
  GROUP BY doc_a, doc_b
), directional AS (
  SELECT doc_a AS seed_doc, doc_b AS candidate_doc, pair_events, support_sessions
  FROM pair_counts
  UNION ALL
  SELECT doc_b AS seed_doc, doc_a AS candidate_doc, pair_events, support_sessions
  FROM pair_counts
)
SELECT
  d.seed_doc,
  d.candidate_doc,
  d.support_sessions,
  ROUND(1.0 * d.support_sessions / sdc.doc_sessions, 4) AS confidence,
  ROUND(
    (1.0 * d.support_sessions / sdc.doc_sessions)
    / NULLIF(1.0 * cdc.doc_sessions / t.total_sessions, 0),
    4
  ) AS lift
FROM directional d
JOIN doc_counts sdc ON sdc.doc = d.seed_doc
JOIN doc_counts cdc ON cdc.doc = d.candidate_doc
CROSS JOIN totals t
```

This SQL shape is the beginning of the recommender. The seed document is the current document, the candidate document is the recommendation, and the metrics explain why the candidate was ranked.

## Graph export

The graph verb emits a mixed row set with `record_type = node` or `record_type = edge`. This keeps the export simple and makes it easy for the dashboard generator to write one JSON file.

Node rows contain:

```text
record_type = node
id
label
doc_kind
read_events
sessions
```

Edge rows contain:

```text
record_type = edge
source
target
pair_events
support_sessions
avg_turn_distance
```

The dashboard currently uses a compact SVG network view. It is not intended to be a full graph-analysis interface. It is a first inspection tool: node size represents session coverage, edge width represents support, and color represents document kind.

## Session timeline

The session timeline verb emits ordered document reads. It is the main audit tool for false positives.

A global pair can look convincing in aggregate, but a session timeline shows what actually happened locally. It answers:

- Were the documents read in the same turn burst?
- Was the pair caused by startup skill loading?
- Did the session later switch to a different project context?
- Are repeated reads evidence of importance or evidence of a retry loop?

The row shape is:

```text
session_id
session_title
provider
session_model
session_turns
tool_seq
emitting_turn_index
timestamp
path_norm
label
doc_kind
```

This view is essential for learning from the recommender before trusting it.

## Dashboard data generation

The dashboard generator is:

```text
scripts/03-generate-doc-coread-dashboard-data.sh
```

It calls the JS verbs and writes static JSON files:

```text
dashboard/data/meta.json
dashboard/data/doc-read-events.json
dashboard/data/doc-frequency.json
dashboard/data/global-pairs.json
dashboard/data/association-rules.json
dashboard/data/graph.json
dashboard/data/session-timeline.json
dashboard/data/recommend-seed.json
```

Useful environment variables:

```bash
ARCHIVE_GLOB='.../*.minitrace.json'
SEED_PATHLIKE='docmgr/SKILL.md'
MIN_SESSIONS=2
WINDOW_TOOLS=100
WINDOW_TURNS=20
LIMIT_FREQ=300
LIMIT_RULES=500
LIMIT_GRAPH=700
LIMIT_TIMELINE=5000
LIMIT_READS=5000
```

The generator prints row counts. A bounded smoke run produced:

```text
association-rules.json: 200 rows
doc-frequency.json: 100 rows
doc-read-events.json: 1000 rows
global-pairs.json: 200 rows
graph.json: 300 rows
recommend-seed.json: 100 rows
session-timeline.json: 1000 rows
```

The dashboard server helper is:

```text
scripts/04-serve-doc-coread-dashboard.sh
```

It generates data if missing and serves the static dashboard on `127.0.0.1`.

The generator is intentionally a thin shell wrapper around the go-minitrace verbs. This makes every dashboard file reproducible from a command-line query:

```bash
run_cmd read-events --limit "$LIMIT_READS" > "$OUT_DIR/doc-read-events.json"
run_cmd doc-frequency --limit "$LIMIT_FREQ" > "$OUT_DIR/doc-frequency.json"
run_cmd global-pairs --limit "$LIMIT_RULES" --minSessions "$MIN_SESSIONS" > "$OUT_DIR/global-pairs.json"
run_cmd association-rules --limit "$LIMIT_RULES" --minSessions "$MIN_SESSIONS" > "$OUT_DIR/association-rules.json"
run_cmd graph --limit "$LIMIT_GRAPH" --minSessions "$MIN_SESSIONS" > "$OUT_DIR/graph.json"
run_cmd session-timeline --limit "$LIMIT_TIMELINE" > "$OUT_DIR/session-timeline.json"
run_cmd recommend --pathLike "$SEED_PATHLIKE" --limit 100 --minSessions 1 > "$OUT_DIR/recommend-seed.json"
```

The browser application then treats these files as its API. There is no hidden backend process behind the dashboard.

## Dashboard application

The dashboard is:

```text
dashboard/index.html
```

It is a static application. It loads JSON from `dashboard/data/` and renders:

- a corpus overview,
- a document frequency table,
- a recommendations / association-rules table,
- a compact co-read graph,
- a session timeline table.

The dashboard uses direct technical explanatory text near each panel. It intentionally avoids opaque claims. A reader should always see the metric behind a recommendation.

The control panel supports:

```text
seed document substring
kind filter
scoring mode
apply/reset
```

The scoring mode can be:

```text
hybrid_score
support_sessions
confidence
lift
pmi
```

This is important because the same data looks different under different metrics. Sorting by support surfaces common workflow hubs. Sorting by lift or PMI surfaces more specific relationships.

The dashboard code is deliberately plain JavaScript. It loads the exported JSON files, stores them in a local `state` object, and re-renders tables and the SVG graph when controls change.

```js
async function load() {
  const [meta, freq, rules, graph, timeline] = await Promise.all(
    ['meta', 'doc-frequency', 'association-rules', 'graph', 'session-timeline']
      .map(n => fetch(`data/${n}.json`).then(r => r.json()))
  );
  Object.assign(state, { meta, freq, rules, graph, timeline });
  render();
}

function filteredRules() {
  let rows = state.rules.filter(r => kindFilter(r, 'seed_kind'));
  if (state.seed) {
    rows = rows.filter(r =>
      (r.seed_doc || '').toLowerCase().includes(state.seed.toLowerCase()) ||
      (r.candidate_doc || '').toLowerCase().includes(state.seed.toLowerCase())
    );
  }
  return rows.sort((a, b) => Number(b[state.score] || 0) - Number(a[state.score] || 0));
}
```

The graph view uses the mixed node/edge export. It is compact rather than comprehensive, but it is enough to inspect whether the strongest exported edges form sensible clusters.

## What we found during exploration

The first useful result is that the data is present and structured enough. Minitrace tool calls contain path, timestamp, turn index, operation type, and success information. That is enough to reconstruct a document-read event stream.

The second result is that skill files dominate the global graph. This is expected. Skills are loaded together at the start of many workflows. The strongest relationships include operational combinations such as:

```text
docmgr/SKILL.md
diary/SKILL.md
remarkable-upload/SKILL.md
ticket-research-docmgr-remarkable/SKILL.md
obsidian-vault-writing/SKILL.md
textbook-authoring/SKILL.md
```

This is not a problem. It means the graph is capturing real workflow structure. But it means a production recommender needs modes:

| Mode | Include skills | Purpose |
|---|---:|---|
| `workflow` | yes | Recommend operational support documents. |
| `project-docs` | no | Recommend project documentation without skill hubs. |
| `ticket-docs` | no or optional | Recommend nearby ticket documents. |
| `skills-only` | yes | Discover skill bundles. |
| `all` | yes | Exploratory graph mining. |

The third result is that `docmgr/SKILL.md` produces plausible neighbors. The `recommend` verb returns documents such as `diary/SKILL.md`, `remarkable-upload/SKILL.md`, and `ticket-research-docmgr-remarkable/SKILL.md`. Those are valid operational companions in doc-heavy workflows.

The fourth result is that path identity is the next major quality issue. The same conceptual document can appear under absolute paths, relative paths, home-relative paths, or worktree-specific paths. The current implementation normalizes `~`, but it does not yet resolve relative paths against session working directories. That limits the accuracy of support counts.

## Failure modes and design constraints

### Skill dominance

Skill files are frequent and clustered. They can hide project-specific documents if raw support is used as the only ranking criterion.

Mitigations:

- Add an include/exclude skill toggle.
- Compute separate graphs by document kind.
- Use lift and PMI for specificity.
- Penalize globally common documents in hybrid scoring.

### Long-session contamination

A long session can contain multiple tasks. Whole-session co-occurrence can connect documents that were not actually related.

Mitigations:

- Prefer sliding windows over whole-session baskets.
- Use turn distance and tool distance.
- Add time-gap segmentation later.
- Use session timelines for audit.

### Rare-pair inflation

PMI and lift can over-rank rare pairs.

Mitigations:

- Require minimum support.
- Display support alongside lift and PMI.
- Do not use PMI alone for recommendations.

### Path fragmentation

Path variants split evidence.

Mitigations:

- Resolve `~`.
- Resolve relative paths against session working directory.
- Map paths to repository-relative identities.
- Map skills to stable IDs such as `skill:docmgr`.

### Source files inside ticket workspaces

A `ttmp/` path is not always documentation. Ticket workspaces often contain copied source files.

Mitigation:

- Require documentation-like extensions unless the path is a known skill or README.

## Implementation sequence that worked

The project followed a useful order:

1. Inspect the minitrace schema manually.
2. Write raw SQL to extract read events.
3. Correct ordering with `WITH ORDINALITY`.
4. Add path classification.
5. Write raw SQL for global pairs.
6. Move repeated logic into JS query-command helpers.
7. Add named JS verbs.
8. Generate sample JSON outputs.
9. Write design documents.
10. Add association metrics and graph export.
11. Add static dashboard data generation.
12. Build the static dashboard.
13. Smoke-test in the browser.
14. Commit at each stable boundary.

This sequence is worth preserving. It keeps each layer testable before building on it.

## Running the system

From the ticket directory:

```bash
scripts/03-generate-doc-coread-dashboard-data.sh
scripts/04-serve-doc-coread-dashboard.sh
```

Then open:

```text
http://127.0.0.1:8768
```

To run query commands directly:

```bash
go-minitrace query commands \
  --query-repository scripts/query-commands \
  docs coread association-rules \
  --archive-glob '<archive-glob>' \
  --limit 50 \
  --output table
```

To inspect recommendations around a seed:

```bash
go-minitrace query commands \
  --query-repository scripts/query-commands \
  docs coread recommend \
  --archive-glob '<archive-glob>' \
  --pathLike 'docmgr/SKILL.md' \
  --limit 20 \
  --output table
```

## Current state

The current system is a working v1. It is not yet a production recommender, but it has the necessary internal structure:

- It extracts document read events.
- It classifies document paths.
- It computes close co-read pairs.
- It computes directional association metrics.
- It exports graph rows.
- It exports session timelines.
- It renders an interactive static dashboard.

The system already supports exploration. A reader can see which documents are frequent, which association rules are strongest, how the graph is shaped, and which reads occurred in session order.

## Next improvements

The highest-value next improvements are:

1. Implement canonical document IDs.
2. Add mode presets: `workflow`, `project-docs`, `ticket-docs`, `skills-only`, `all`.
3. Add a supporting-sessions drill-down for each recommendation.
4. Add time-gap segmentation for long sessions.
5. Add a graph export that separates nodes and edges into separate JSON arrays.
6. Add manual evaluation labels for a small set of seed documents.
7. Add a runtime API that can accept current session reads and return recommendations with explanations.

## Final interpretation

The document co-read project demonstrates that transcript history contains a usable document relationship signal. The strongest early signal is workflow-level: skills and operational guides are loaded in repeatable bundles. Project-specific recommendation will require better filtering and canonicalization, but the extraction and metric layers are already in place.

The dashboard is the correct next interface because recommender quality cannot be evaluated from aggregate counts alone. A user needs to inspect frequencies, association metrics, graph edges, and session timelines together. The Document Co-Read Observatory provides that inspection surface and gives the next engineer a concrete place to improve the recommender.
