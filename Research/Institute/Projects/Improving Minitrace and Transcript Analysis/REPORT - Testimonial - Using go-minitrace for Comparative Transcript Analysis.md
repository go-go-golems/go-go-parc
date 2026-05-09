---
title: Testimonial - Using go-minitrace for Comparative Transcript Analysis
aliases:
  - Minitrace Comparative Analysis Testimonial
  - go-minitrace Field Report
  - Transcript Analysis Testimonial
tags:
  - research
  - institute
  - report
  - minitrace
  - transcript-analysis
  - agent-tooling
  - duckdb
  - annotations
status: active
type: report
created: 2026-04-09
repo: /home/manuel/workspaces/2026-04-08/sqleton-minitrace/go-minitrace
source_ticket: MINIMAX-VS-GPT-COMPARE
related_project:
  - "[[PROJ - Improving Minitrace and Transcript Analysis]]"
---

# Testimonial — Using go-minitrace for Comparative Transcript Analysis

This report records a detailed operator experience using `go-minitrace` to study two coding-agent sessions that implemented the same feature to different stopping points. It is written as a precise testimonial rather than a marketing note. The goal is to preserve what `go-minitrace` made possible, where it created friction, and what concrete improvements would most increase its value for transcript-driven engineering review.

> [!summary]
> `go-minitrace` was strong enough to support a rigorous, evidence-first comparison of two coding-agent implementation paths, but the investigation also exposed several missing first-class concepts.
> 
> The strongest positives were:
> - archive conversion was straightforward and trustworthy
> - transcript annotations were powerful once established
> - DuckDB querying over sessions made timing/churn/failure analysis practical
> 
> The strongest gaps were:
> - annotations are not yet first-class enough in DuckDB query workflows
> - path normalization across repos/sessions is too manual
> - implementation-window / phase-span reasoning is common but under-modeled
> - failure analysis still relies too heavily on freeform shell output parsing

## 1. Study context

The triggering task was a comparison of two coding-agent sessions implementing `GMT-002` (“sqleton-style verb query loading”) in separate repositories:

- GPT-5.4 repo:
  - `/home/manuel/workspaces/2026-04-08/sqleton-minitrace/go-minitrace`
- MiniMax repo:
  - `/home/manuel/workspaces/2026-04-08/sqleton-minitrace-minimax/go-minitrace`

The user wanted a review of:

1. the **state of the code at the end of Phase 1**
2. the **quality of the code implementing Phase 1**
3. **why MiniMax took longer** to reach that Phase 1 boundary

The user also insisted that the analysis should use `go-minitrace` properly rather than relying primarily on raw transcript reading. That methodological correction was important and shaped the rest of the work.

Relevant output ticket:

- `/home/manuel/workspaces/2026-04-08/sqleton-minitrace/go-minitrace/ttmp/2026/04/08/MINIMAX-VS-GPT-COMPARE--compare-minimax-vs-gpt-5-4-implementation-approaches-sqleton-minitrace`

Relevant vault guideline:

- [[Code Review with go-minitrace]]

## 2. What `go-minitrace` made possible

The investigation would have been much weaker without `go-minitrace`. The tool was not a cosmetic extra; it changed the quality of the final answer.

### 2.1 Ticket-local archive creation

I converted both Pi sessions into one ticket-local archive tree and then analyzed them together. That gave me:

- a shared archive namespace
- one place to store annotations
- reproducible query inputs
- a basis for storing numbered SQL/bash scripts under the ticket

This was a strong workflow. Converting sessions into a neutral archive before analyzing them made the investigation much more disciplined.

### 2.2 Phase-boundary annotation

The single most important methodological move was annotating tool-call IDs corresponding to:

- `phase-1-code-complete`
- `phase-1-bookkeeping-complete`

for both sessions.

That converted a fuzzy prose concept (“end of phase 1”) into a concrete archive fact. Once those annotations existed, the rest of the comparison became much more robust.

### 2.3 DuckDB-driven comparative analysis

With the converted archive and synced annotations, I was able to query for:

- implementation-window timing
- tool frequencies before the boundary
- file-touch concentration
- build/test/lint churn
- concrete `bash` failure snippets
- cross-session file overlap
- annotation boundary events

That made it possible to answer not just “what changed?” but “why did one agent take longer?” with evidence instead of intuition.

### 2.4 Better than raw transcript reading

Before the analysis was fully rebuilt around minitrace, the comparison risked being too ad hoc. Once the archive/query workflow was in place, the analysis improved in several ways:

- the phase cutoff became explicit
- whole-session versus implementation-window confusion became fixable
- repetitive claims could be backed by stored SQL files
- the resulting docs became auditable by re-running the scripts

## 3. What was hard in practice

This section is intentionally concrete. These are not abstract wishes; they are the specific points where the analysis became slower, more error-prone, or less direct than it should have been.

### 3.1 Annotations are powerful but awkward in DuckDB

The biggest surprise was that `annotate add` writes to working-state SQLite, while `query duckdb` only sees annotations after `annotate sync` pushes them back into the archive JSON.

That model is understandable, but it is not obvious during live analysis. The most visible symptom was the failed query assumption that there would be a first-class `annotations` table inside DuckDB.

Actual error encountered:

```text
Error: executing query: Catalog Error: Table with name annotations does not exist!
Did you mean "pg_settings"?
```

The fix was to query annotations through synced JSON arrays with patterns like:

```sql
FROM sessions_base sb,
UNNEST(sb.annotations) AS a(ann)
```

and then extract titles/target IDs with JSON paths.

That is workable, but it is too indirect for a concept as central as annotations.

### 3.2 Path normalization was too manual

A core part of the comparison involved asking questions like:

- which files did each run touch?
- which files were rewritten repeatedly?
- where do the two sessions overlap in logical package space?

But the two runs lived in different repo clones, and tool outputs mixed:

- absolute paths
- repo-relative paths
- cwd-relative paths
- shell output paths embedded inside freeform stdout/stderr

I had to normalize paths manually in SQL and shell. That was tedious and fragile. It is the kind of work that should be built into the archive or the standard views.

### 3.3 “Compare only the implementation window” is common but under-modeled

A major methodological issue was that the GPT session included earlier design/research work, while the MiniMax session was already close to implementation. If I had compared whole-session counts, the result would have been misleading.

The correct analysis compared only:

- implementation start prompt
- to `phase-1-code-complete`

That required a custom `start_turns` CTE and hand-built timing queries.

This kind of windowing is common in transcript review. It should not require bespoke SQL every time.

### 3.4 Failure analysis relied on regex and shell-output reading

One of the most valuable parts of the study was identifying why MiniMax took longer. The answer came from concrete failures, including:

- wrong-directory test invocation
- YAML schema issue
- root/path handling test failures
- alias validation bug
- lint failures
- wrong-directory git commit attempt

But the path to those findings still depended too much on parsing freeform `bash` output. There was no first-class view for:

- exit code
- success/failure
- command category
- duration
- cwd
- structured stdout/stderr separation

The information was recoverable, but the workflow was noisier than it should be.

### 3.5 Continuation/split-turn lineage is not explicit enough

The MiniMax session involved split-turn continuation context. That made implementation-start detection less clean than the GPT session. I could still find a defensible start marker, but it took interpretation rather than simply querying a first-class continuation lineage model.

### 3.6 The system is powerful, but still too close to the raw event stream

This is the most general complaint.

`go-minitrace` is already strong enough for real studies, but many common analytical questions still require the operator to re-derive the same intermediate facts again and again:

- flattened tool calls
- file touches
- annotations
- command categories
- failure classes
- spans/windows
- repo-relative identities

The raw event model is valuable. The problem is that the most common derived concepts are not yet elevated enough.

## 4. Dedicated section: improvements

This section stores the full list of improvements that emerged from the study. I am preserving them here in full because they represent the most valuable output of the experience, beyond the immediate comparison itself.

## 4.1 Highest-value improvements

### 4.1.1 Make annotations first-class in DuckDB queries

**Observed friction:** annotations exist conceptually as first-class review artifacts, but in query practice they are second-class unless explicitly synced and manually unnested from JSON.

**Current behavior:**

- `annotate add` writes to SQLite working state
- `query duckdb` reads the archive JSON
- the user must `annotate sync`
- queries then need `UNNEST(sb.annotations)` and JSON extraction boilerplate

**Improvement options:**

- expose a built-in `annotations` table or view in `query duckdb`
- let `query duckdb` merge working annotations automatically
- add a helper view like `annotation_events`

**Why this matters:**

This would have removed one of the biggest sources of confusion and cut down a large amount of query boilerplate.

---

### 4.1.2 Add built-in normalized file path fields

**Observed friction:** comparing file activity across sessions living in different repo clones required manual path normalization.

**Proposed fields:**

- `cwd`
- `repo_root`
- `repo_rel_path`
- possibly `logical_project_path`

**Why this matters:**

Cross-session file-touch and churn analysis is a core retrospective task. It should not depend on each operator inventing their own path-normalization SQL.

---

### 4.1.3 Add explicit session/window markers

**Observed friction:** the crucial comparison was not whole-session to whole-session, but implementation-window to implementation-window.

**Proposed improvement:**

Introduce first-class window/span concepts such as:

- `phase:start`
- `phase:end`
- `implementation:start`
- `implementation:end`

or a generic span model with:

- `start_event_id`
- `end_event_id`
- `label`
- `notes`

**Why this matters:**

A very large share of transcript analysis is really span analysis. The format and tooling should acknowledge that directly.

---

### 4.1.4 Add structured command outcome fields for `bash` and similar tool calls

**Observed friction:** failure analysis relied on freeform `output.result` text and regex classification.

**Proposed fields:**

- `exit_code`
- `stderr`
- `stdout`
- `success`
- `duration_ms`
- `command_kind` (for example `go-test`, `git-commit`, `lint`, `build`)
- optional `cwd`

**Why this matters:**

This would make failure-loop analysis much more robust and would eliminate a large amount of ad hoc parsing.

## 4.2 Format improvements

### 4.2.1 Promote common derived structures from JSON blobs to typed relational views

**Observed friction:** useful concepts exist, but many of them have to be flattened manually before they become easy to query.

**Candidate built-in views:**

- `tool_calls_flat`
- `annotations_flat`
- `file_touches`
- `turn_messages`
- `git_events`
- `bash_commands`
- `bash_failures`

**Why this matters:**

A large amount of comparative analysis starts with the same flattening boilerplate. Shipping the common views would speed up almost every serious study.

---

### 4.2.2 Better support for continuation/split-turn lineage

**Observed friction:** split-turn continuation made implementation-start detection messier than it should have been.

**Proposed fields:**

- `continued_from_session_id`
- `continued_from_turn_id`
- `continuation_reason`
- perhaps a synthetic `conversation_thread_id`

**Why this matters:**

This would improve analysis of resumed work, interrupted sessions, and multi-session projects.

---

### 4.2.3 Store repo/VCS state more explicitly

**Observed friction:** code-boundary comparison often required jumping between transcript evidence and Git state.

**Proposed metadata:**

- branch
- HEAD commit before/after relevant tool calls
- dirty state
- staged files
- worktree root

**Why this matters:**

Coding-agent transcript analysis depends heavily on repository state. More first-class repo metadata would make code-boundary review much easier.

## 4.3 Tooling improvements in `go-minitrace`

### 4.3.1 Add a built-in `compare sessions` workflow

**Observed friction:** a very common comparison workflow had to be rebuilt manually with many one-off scripts.

**Example command shape:**

```bash
go-minitrace compare sessions \
  --left <session-a> \
  --right <session-b> \
  --start-annotation implementation-start \
  --end-annotation phase-1-code-complete
```

**Suggested outputs:**

- timing comparison
- tool frequency deltas
- churn hotspots
- failure summary
- touched-file overlap

**Why this matters:**

The triggering study required 15 numbered scripts. That is acceptable for a one-off investigation, but common enough to justify product support.

---

### 4.3.2 Add built-in failure clustering / command classification

**Observed friction:** categories like `rootdir-bug`, `wrong-directory`, `lint-fix-loop`, and `alias-yaml-schema-bug` had to be inferred manually.

**Proposed improvement:**

A helper like:

```bash
go-minitrace analyze failures --session ...
```

or standard SQL views that classify:

- compile/test/lint/build/git categories
- success/failure extraction
- repeated failure clusters

**Why this matters:**

Failure clustering is one of the most valuable outputs of transcript retrospectives. It should be easier.

---

### 4.3.3 Make `annotate sync` easier or more automatic

**Observed friction:** annotations are easy to create but easy to forget to sync before querying.

**Possible improvements:**

- auto-sync on `annotate add`
- `query duckdb --include-working-annotations`
- a warning when unsynced annotations exist

**Why this matters:**

The current model is understandable but easy to trip over in interactive use.

---

### 4.3.4 Ship more official query packs

**Observed friction:** the docs are helpful, but a lot of serious analysis still starts by writing the same family of SQL queries from scratch.

**Suggested query packs:**

- coding-session review
- tool churn
- git commit cadence
- file rewrite hotspots
- failure loops
- annotation timelines
- multi-session comparison

**Why this matters:**

This would reduce one-off SQL, improve consistency, and accelerate serious studies.

## 4.4 Format-level design idea: separate raw trace from derived facts

**Observed friction:** important analytical facts are currently latent inside raw events and must be re-derived repeatedly.

**Proposed model layers:**

- `raw_events`
- `derived_events`
- `annotations`
- `spans`

**Examples of `derived_events`:**

- file touches
- command classifications
- git commit events
- failure events
- repo-relative path facts

**Why this matters:**

This would preserve the raw ingest faithfully while giving analysis a much more stable substrate.

## 4.5 If I had to pick only three improvements

If only three improvements could be made soon, I would choose these:

1. **First-class annotations table/view in DuckDB**
2. **Normalized repo-relative file path fields**
3. **Built-in session comparison / implementation-window analysis**

Those three changes alone would have made the triggering study significantly faster, cleaner, and less error-prone.

## 5. Concrete observations from the study that support the improvement agenda

These observations are useful because they connect the proposals above to real pain rather than abstract product wishes.

### 5.1 Real benefit of annotations

The phase comparison only became methodologically sound after explicit annotation of the code-complete boundary. That is strong evidence that annotations are not a niche feature; they are a central unit of transcript review.

### 5.2 Real cost of missing path normalization

Cross-session file overlap and churn analysis required manual path rewriting because two repos with similar structure lived at different absolute roots. That is exactly the kind of repetitive translational work a format/view layer should absorb.

### 5.3 Real value of implementation-window spans

The whole-session comparison would have produced the wrong answer about why MiniMax took longer. The correct answer emerged only after narrowing the comparison to the implementation window. This is strong evidence that span/window analysis should be first-class.

### 5.4 Real value of failure clustering

The most valuable process explanation in the study was not tool counts in isolation. It was the clustering of failures into local repair loops:

- wrong-directory commands
- schema bug
- rootdir/path bug
- alias validation gap
- lint loop

This suggests that transcript tooling should help analysts move from raw command output toward repeated failure patterns much faster.

## 6. What I would say to someone deciding whether to use `go-minitrace`

I would strongly recommend using it for serious transcript review, especially when:

- boundaries matter
- code-state comparison matters
- the difference between “whole session” and “implementation slice” matters
- you need reproducible evidence rather than anecdotal transcript reading

But I would also warn them that they should expect to invest some effort in:

- boundary annotation and sync discipline
- query writing
- path normalization
- interpreting tool-output structure

So my current judgment is:

> `go-minitrace` is already good enough to do serious work, but it is still one abstraction layer short of being truly ergonomic for repeated coding-agent retrospectives.

## 7. Recommended next research steps for this project

1. Collect more field reports from other transcript-analysis tasks.
2. Identify which pain points recur across all studies versus which were specific to this comparison.
3. Separate proposals into:
   - archive format changes
   - CLI changes
   - official query-pack additions
4. Prototype at least one improvement in each category:
   - annotations-first DuckDB access
   - repo-relative path normalization
   - built-in comparison command
5. Re-run a later transcript study and compare:
   - number of custom SQL files needed
   - number of shell glue commands needed
   - number of methodological mistakes prevented

## 8. Bottom line

The experience was valuable enough that I would absolutely use `go-minitrace` again for transcript-driven engineering review. It materially improved the rigor of the final analysis.

At the same time, the experience made it very clear where the next tranche of value lies. The biggest opportunity is not in raw ingestion anymore. It is in elevating common analytical concepts — annotations, spans, normalized file identities, structured command outcomes, and comparison workflows — into first-class parts of the system.

That is the difference between a tool that can support excellent studies and a tool that makes excellent studies the default outcome.
