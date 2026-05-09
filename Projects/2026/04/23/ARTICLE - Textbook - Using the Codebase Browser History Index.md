---
title: "Textbook: Using the Codebase Browser History Index"
aliases:
  - Textbook: Using the Codebase Browser History Index
  - Codebase Browser Usage Guide
tags:
  - textbook
  - article
  - codebase-browser
  - sqlite
  - git
  - history
  - diff
  - concepts
  - usage
status: active
type: article
created: 2026-04-23
repo: /home/manuel/code/wesen/2026-04-19--go-codebase-browser
---

# Using the Codebase Browser History Index

This chapter explains how to use the git-aware history index in `codebase-browser`. The goal is to teach a single workflow: how to scan commits, explore changes through the CLI and web UI, write reusable SQL concepts, and navigate function history interactively. Every command in this chapter is real and can be run against the codebase-browser repository itself.

The system is designed around a single principle: if you have per-commit symbol snapshots with body hashes in a SQLite database, every question about code history becomes a SQL query. The CLI gives you direct SQL access. The web UI gives you interactive exploration. The concept catalog gives you reusable named queries.

## 1. The full pipeline in four commands

The workflow has four steps. Each step produces a file or a running server.

```bash
# Step 1: Generate the static codebase index
codebase-browser index build

# Step 2: Scan git history into history.db
codebase-browser history scan --range HEAD --db history.db --worktrees --incremental

# Step 3: Run queries against either database
codebase-browser query --db history.db commands history hotspots --limit 10

# Step 4: Serve the interactive browser
codebase-browser serve --addr :3011 --db codebase.db --history-db history.db --repo-root .
```

Each step does one job. Step 1 builds the static `codebase.db` used for package/symbol browsing. Step 2 builds `history.db` used for commit-level analysis. Step 3 runs SQL queries directly. Step 4 serves both databases through a web UI.

The two databases are separate by design. `codebase.db` is small (under 2 MB) and ships inside the Go binary. `history.db` can be large (30+ MB for 75 commits) and is optional — the browser works without it, just without history features.

## 2. Scanning commits

The `history scan` command discovers commits, creates git worktrees, runs the Go indexer at each commit, and stores the results in `history.db`.

### Basic scan

```bash
# Scan the last 20 commits
codebase-browser history scan --range "HEAD~20..HEAD" --db history.db --worktrees
```

The `--range` flag accepts any git revision range: `HEAD~20..HEAD`, `HEAD~5..HEAD`, `v1.0..HEAD`, or just `HEAD` (all reachable commits). The `--worktrees` flag enables parallel extraction using git worktrees. Without it, the scanner indexes from the working directory, which is only accurate for HEAD.

### Incremental scanning

```bash
# Scan only new commits since the last scan
codebase-browser history scan --range HEAD --db history.db --worktrees --incremental
```

The `--incremental` flag checks which commits are already in `history.db` and skips them. This makes repeated scans fast: only new commits are extracted.

### Parallelism

```bash
# Use 4 concurrent worktrees
codebase-browser history scan --range HEAD --db history.db --worktrees --parallelism 4
```

The `--parallelism` flag controls how many worktrees exist simultaneously. Each worktree holds a full checkout of a commit, so disk space usage scales with parallelism. On a typical laptop, 4 is a safe default.

### Listing scanned commits

```bash
codebase-browser history list --db history.db
```

This shows a formatted table with hash, date, symbol count, and message for every indexed commit.

## 3. CLI diff queries

### Commit diff

```bash
# Diff two commits by hash or ref
codebase-browser history diff HEAD~10 HEAD --db history.db

# Diff with more detail
codebase-browser history diff abc1234 def5678 --db history.db --format json
```

The output shows files added, removed, and modified, plus symbols classified as added, removed, modified, signature-changed, or moved. The `--format json` flag produces machine-readable output.

### Symbol body diff

```bash
# Show what changed inside a specific function
codebase-browser history symbol-diff HEAD~10 HEAD \
  --symbol "sym:github.com/.../func.main" \
  --db history.db
```

This reads the source file at both commits, extracts the function body using byte offsets, and produces a unified diff showing every line with ` ` (context), `-` (removed), or `+` (added) prefixes. The output includes the full function — signature, body, and closing brace.

### Symbol history

```bash
# Show every commit where a function appeared
codebase-browser history symbol-history \
  --symbol "sym:github.com/.../method.Server.Handler" \
  --db history.db \
  --limit 50
```

The output shows commit hash, date, line range, body hash, and commit message for each commit where the symbol existed. Body hashes highlighted in orange indicate commits where the function body actually changed.

You can also search by name instead of full symbol ID:

```bash
codebase-browser history symbol-history --name main --db history.db
```

This finds the first symbol matching `main` and shows its history.

## 4. SQL concepts for history analysis

The concept catalog provides named, parameterized queries that work against `history.db`. Concepts live in `concepts/history/` and are executed through the query CLI.

### Hotspots: most frequently changed symbols

```bash
codebase-browser query --db history.db commands history hotspots --limit 10
```

This returns symbols ranked by distinct body hash versions. A symbol with 5 distinct body hashes across 75 commits is a hotspot — it changes frequently and is worth understanding carefully.

Output:

```
symbol_id                                          name      distinct_versions  commit_count
sym:.../method.Server.Handler                      Handler   6                  80
sym:.../func.main                                  main      5                  81
sym:.../func.Extract                               Extract   3                  81
```

### Commit timeline

```bash
codebase-browser query --db history.db commands history commits-timeline --limit 10
```

Lists commits in reverse chronological order with symbol counts. Useful for seeing how the codebase grew or shrank over time.

### Symbol changes between two commits

```bash
codebase-browser query --db history.db commands history symbol-changes \
  --base HEAD~10 --head HEAD
```

Shows every symbol that changed between two commits, classified as added, removed, or modified. This is the SQL equivalent of `history diff` but with full parameterization.

### File changes between two commits

```bash
codebase-browser query --db history.db commands history file-changes \
  --base HEAD~10 --head HEAD
```

Shows files that changed between two commits with line count deltas.

### Writing your own concept

Create a file in `concepts/history/` with a comment preamble and a SQL body:

```sql
/* codebase-browser concept
name: my-symbol-search
short: Find symbols by name pattern
params:
  - name: pattern
    type: string
    help: SQL LIKE pattern for symbol name
  - name: limit
    type: int
    default: 20
tags: [custom]
*/
SELECT s.id, s.name, s.kind, s.body_hash, c.short_hash, c.message
FROM snapshot_symbols s
JOIN commits c ON c.hash = s.commit_hash
WHERE s.name LIKE {{.pattern}}
ORDER BY c.author_time DESC
LIMIT {{.limit}};
```

Run it:

```bash
codebase-browser query --db history.db commands history my-symbol-search \
  --pattern '%Handler%'
```

The concept system renders the Go template (`{{.pattern}}` becomes `'%Handler%'`), executes the SQL, and returns the results.

## 5. The web UI

Start the server with both databases:

```bash
codebase-browser serve --addr :3011 --history-db history.db --repo-root .
```

The `--repo-root` flag is required for body diffs. The server needs access to the git repository to read file contents at specific commits via `git show`.

### Browsing the commit timeline

Navigate to `http://localhost:3011/#/history`. The page shows a commit list on the left with "old" and "new" buttons per commit. Select two commits to see the diff.

The diff panel shows:
- **Stats bar**: file and symbol change counts
- **Changed files**: paths linked to source pages
- **Changed symbols**: names that are clickable buttons

### Viewing a function diff

Click any symbol name in the "Changed symbols" table. A "Function diff" panel opens showing the full function body diff between the sidebar-selected commits. The diff shows every line:
- Gray lines with `  ` prefix: unchanged context (signature, closing brace)
- Red lines with `- ` prefix: removed lines
- Green lines with `+ ` prefix: added lines

The sidebar highlights commits where the selected symbol's body changed, marked with an orange background. This lets you see at a glance which of the 80+ commits touched the function you are investigating.

### Viewing symbol history from a symbol page

On any symbol detail page, click "📜 View change history". This navigates to the history page with that symbol pre-loaded. A standalone view shows every commit where the symbol appeared, with per-row "from" and "to" selectors. Pick any two commits to see the body diff.

### Running concepts in the browser

Navigate to `http://localhost:3011/#/queries/history/hotspots`. The concept page shows:
- **Parameters**: typed input fields with defaults
- **Concept source**: collapsible section with Prism.js syntax highlighting
- **Results**: clickable table where symbol IDs link to symbol pages, file paths link to source pages, package IDs link to package pages

Click "Run query" to execute. The rendered SQL (with parameters filled in) is shown above the results.

## 6. The query concepts page in detail

The query concepts page is organized by directory. Concepts in `concepts/history/` appear under the "history" group. Concepts in `concepts/symbols/` appear under "symbols". The sidebar shows all groups with concept counts.

Each concept detail page has four sections:

1. **Header**: concept path, description, source location, tags
2. **Concept source** (collapsed by default): the raw SQL file with preamble shown as muted comment and SQL body with syntax highlighting. Expand it to see the exact query that will run.
3. **Parameters**: typed form fields. Fill in values or accept defaults. Parameters are persisted in the URL (e.g., `?p.limit=10&p.pattern=%Handler%`), so you can bookmark or share a specific query configuration.
4. **Results**: the query output as a table. Cells are linked where possible — symbol IDs link to symbol pages, package IDs to package pages, file paths to source pages.

The "Render SQL only" button shows the rendered SQL without executing it. This is useful for debugging templates or understanding what the query will do before running it against a large database.

## 7. Common workflows

### "What changed in the last 10 commits?"

```bash
codebase-browser history diff HEAD~10 HEAD --db history.db
```

In the browser: select HEAD as "new" and HEAD~10 as "old" on the history page.

### "Which functions change the most?"

```bash
codebase-browser query --db history.db commands history hotspots --limit 20 --min_versions 3
```

In the browser: navigate to `/#/queries/history/hotspots`, set `min_versions` to 3, click "Run query".

### "Show me the diff of Server.Handler between Phase 1 and now"

```bash
codebase-browser history symbol-diff 33d10c6 HEAD \
  --symbol "sym:github.com/.../method.Server.Handler" \
  --db history.db
```

In the browser: go to the symbol page for `Server.Handler`, click "View change history", then click "from" on the Phase 1 commit row.

### "Which commits touched the indexer?"

```bash
codebase-browser query --db history.db commands history file-changes \
  --base HEAD~30 --head HEAD \
  | grep indexer
```

### "Give me a full PR summary"

```bash
codebase-browser query --db history.db commands history pr-summary \
  --base HEAD~10 --head HEAD
```

This returns added, removed, and modified symbol counts with file breakdowns.

## 8. Working rules

**Rule 1: Always use `--worktrees` for scanning.** Without it, the scanner indexes from the working directory, which is only accurate for HEAD. Worktrees give you accurate per-commit extraction.

**Rule 2: Use `--incremental` for repeated scans.** Scanning is the most expensive operation. Incremental mode skips already-indexed commits and only processes new ones.

**Rule 3: Keep `--repo-root` when serving with history.** The body diff endpoint needs to read file contents from git. Without `--repo-root`, body diffs will return errors.

**Rule 4: Write concepts for repeated queries.** If you find yourself typing the same SQL more than twice, it should be a concept file. Concepts are version-controlled, testable, and shareable.

**Rule 5: Use underscores in concept parameter names.** Go templates reject hyphens. `symbol_id` works, `symbol-id` does not.

**Rule 6: Check the concept source before debugging results.** The "Concept source" section shows the exact SQL that runs. Template rendering can produce surprising results — always verify the rendered SQL before assuming the data is wrong.

**Rule 7: `history.db` is separate from `codebase.db` on purpose.** The static index is small and ships in the binary. The history index can be large and is optional. Do not merge them.

## 9. Reference: all CLI commands

### History commands

```
codebase-browser history scan     --range HEAD --db history.db --worktrees --incremental --parallelism 4
codebase-browser history list     --db history.db
codebase-browser history diff     <old> <new> --db history.db [--format json]
codebase-browser history symbol-diff <old> <new> --symbol <id> --db history.db
codebase-browser history symbol-history --symbol <id> --name <name> --limit 50 --db history.db
```

### Query commands (concepts)

```
codebase-browser query --db <db> commands [group] [concept] [--param value]...
codebase-browser query --db <db> --sql "SELECT ..."        # raw SQL
codebase-browser query --db <db> --file queries/foo.sql     # SQL from file
```

### Serve command

```
codebase-browser serve --addr :3011 --db codebase.db --history-db history.db --repo-root .
```

## 10. Related notes

- [[ARTICLE - Textbook - Building a Git-Aware Codebase Index with SQLite]] — the implementation companion to this usage guide
- [[PROJ - Codebase Browser - Embedded Go+TS Doc Server with Live Source Snippets]] — project overview
- `/home/manuel/code/wesen/2026-04-19--go-codebase-browser/ttmp/2026/04/24/GCB-009--git-aware-codebase-index-track-symbol-locations-across-commits-for-per-function-diff-and-change-history/` — design doc and implementation diary
