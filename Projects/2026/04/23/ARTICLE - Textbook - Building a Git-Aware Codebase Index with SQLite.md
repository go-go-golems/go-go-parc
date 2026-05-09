---
title: "Textbook: Building a Git-Aware Codebase Index with SQLite"
aliases:
  - Textbook: Building a Git-Aware Codebase Index
  - Git-Aware Codebase Index Implementation
tags:
  - textbook
  - article
  - codebase-browser
  - sqlite
  - git
  - go
  - static-analysis
  - history
  - diff
  - concept-catalog
status: active
type: article
created: 2026-04-23
repo: /home/manuel/code/wesen/2026-04-19--go-codebase-browser
---

# Building a Git-Aware Codebase Index with SQLite

This chapter explains how to build a codebase index that tracks symbol locations across git commits, stores per-function body hashes for change detection, and exposes the whole thing through SQL queries and an interactive web UI. The goal is not to document every line of the codebase-browser project. The goal is to teach the architectural decisions that make a system like this work — why SQLite is the right storage shape, why git worktrees are the right extraction mechanism, and why `body_hash` is the single column that makes function-level diffing possible.

The system was built in nine phases across two weeks, and every design choice in this chapter was made during that implementation. The schemas are real. The failures are real. The queries that finally worked are real.

> [!summary]
> This system has three identities that reinforce each other:
> 1. A **SQLite-backed static index** that makes packages, files, symbols, and cross-references queryable through SQL
> 2. A **git-aware history layer** that extracts the full symbol table at every commit and computes per-function body hashes for change detection
> 3. A **structured query catalog** of named, parameterized SQL concepts that work against both the static index and the history database

## 1. The problem with static documentation

A codebase browser that documents a single snapshot is useful but incomplete. It tells you what exists right now. It does not tell you what changed, what was removed, or which functions are hotspots that change frequently. When you are trying to understand a codebase — whether you are onboarding, reviewing a PR, or debugging a regression — the history of the code is as important as its current state.

The common approach is to run `git log` or `git diff` and read the output. This works for a single file or a single function, but it does not scale. If you want to know which functions changed body between commit A and commit B, you need to parse both commits' symbol tables, join them, and classify every symbol as added, removed, modified, or moved. No amount of piping git output through `awk` will give you that reliably.

What you actually need is a database. Not a running server, not a distributed store — a single SQLite file that contains the symbol table for every commit you care about, with enough structure to answer questions like "which functions changed body hash between these two commits" in a single SQL query.

The challenge is building that database efficiently. Extracting the symbol table requires running the Go indexer at each commit, which requires having the source tree at that commit's state. Doing this naively — checking out each commit, running the indexer, checking out the next — works but is slow and destructive. The system needs a way to extract symbols from many commits in parallel without destroying the working directory.

## 2. Why SQLite is the right shape

The codebase index is naturally relational. A package contains files. A file contains symbols. A symbol references other symbols. These are not documents that should be stuffed into a key-value store. They are rows with foreign keys and indexes.

SQLite is the right choice for three reasons.

First, the data fits in memory. A typical Go project with 300 symbols, 80 files, and 27 packages produces a `codebase.db` under 2 MB. Even with 75 commits of history, the `history.db` stays under 30 MB. SQLite handles databases of this size without any tuning.

Second, the query patterns are known in advance. "Find all exported functions", "count symbols per package", "which functions changed between these two commits" — these are SQL queries, not full-text search problems. SQLite's query planner is more than sufficient.

Third, the deployment model is a single file. No server process, no connection pooling, no migrations framework. The database is a file that gets generated at build time and shipped inside the Go binary via `go:embed`. This eliminates an entire class of operational complexity.

The alternative — a JSON index — was the first approach. The project started with `index.json`, a single file containing the entire symbol table. JSON works fine for lookups: find a symbol by name, find a file by path. It breaks down the moment you need to join across tables. "Find all symbols that reference symbol X" requires walking the entire reference array. "Find all functions whose body changed between two commits" requires loading two full JSON blobs and diffing them in memory. These operations are natural in SQL and awkward in JSON.

The transition from JSON to SQLite was not a rewrite. The Go indexer still produces the same in-memory `Index` struct. The change was in the storage layer: instead of marshaling to JSON, the loader inserts into SQLite tables. The query layer changed from Go functions that walk arrays to SQL statements that join tables. The rest of the system — the web UI, the CLI, the concept catalog — did not need to change.

## 3. The schema design

The schema has two database files with different purposes. `codebase.db` holds the static index for the current checkout. `history.db` holds per-commit snapshots for diff and timeline queries.

### The static index schema (`codebase.db`)

The static index has four main tables:

```sql
CREATE TABLE packages (
    id TEXT PRIMARY KEY,
    import_path TEXT NOT NULL,
    name TEXT NOT NULL,
    doc TEXT NOT NULL DEFAULT ''
);

CREATE TABLE files (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    package_id TEXT NOT NULL,
    size INTEGER NOT NULL DEFAULT 0,
    sha256 TEXT NOT NULL DEFAULT ''
);

CREATE TABLE symbols (
    id TEXT PRIMARY KEY,       -- e.g. "sym:github.com/.../func.main"
    kind TEXT NOT NULL,        -- func, method, type, var, const
    name TEXT NOT NULL,
    package_id TEXT NOT NULL,
    file_id TEXT NOT NULL,
    start_line INTEGER NOT NULL DEFAULT 0,
    end_line INTEGER NOT NULL DEFAULT 0,
    start_offset INTEGER NOT NULL DEFAULT 0,
    end_offset INTEGER NOT NULL DEFAULT 0,
    signature TEXT NOT NULL DEFAULT '',
    exported INTEGER NOT NULL DEFAULT 0,
    body_hash TEXT NOT NULL DEFAULT ''
);

CREATE TABLE refs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_symbol_id TEXT NOT NULL,
    to_symbol_id TEXT NOT NULL,
    kind TEXT NOT NULL
);
```

Three things are worth noting about this schema.

The symbol ID scheme uses a structured format: `sym:<importPath>.<kind>.<name>`. For a method like `Server.Handler`, the ID is `sym:github.com/wesen/codebase-browser/internal/server.method.Server.Handler`. This scheme is stable across commits because import paths do not change when file contents change. If you need to track a function across the history of a project, the symbol ID is the join key.

The `start_offset` and `end_offset` columns store byte offsets into the source file. Line numbers are useful for display, but byte offsets are necessary for extracting the function body accurately. When you need to diff two versions of a function, you read the file content at both commits and slice `[startOffset:endOffset]` to get the exact body text.

The `body_hash` column is a SHA-256 hash of the function body. It is the single most important column in the history schema. Without it, detecting whether a function changed requires reading both files and extracting both bodies. With it, detecting change is a single comparison: `old.body_hash != new.body_hash`.

The `refs` table uses `AUTOINCREMENT` rather than a structured ID because references do not have stable identities across commits. A reference from function A to function B exists or it does not; it does not need to be tracked individually.

### The history schema (`history.db`)

The history schema adds a `commit_hash` dimension to every table. The tables become `snapshot_packages`, `snapshot_files`, `snapshot_symbols`, and `snapshot_refs`, each with `commit_hash` as part of the primary key:

```sql
CREATE TABLE snapshot_symbols (
    commit_hash TEXT NOT NULL REFERENCES commits(hash),
    id TEXT NOT NULL,
    kind TEXT NOT NULL,
    name TEXT NOT NULL,
    -- ... same columns as the static schema ...
    body_hash TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (commit_hash, id)
);
```

The `commits` table stores metadata for every indexed commit:

```sql
CREATE TABLE commits (
    hash TEXT PRIMARY KEY,
    short_hash TEXT NOT NULL,
    message TEXT NOT NULL,
    author_time INTEGER NOT NULL,
    parent_hashes TEXT NOT NULL DEFAULT '[]',
    indexed_at INTEGER NOT NULL DEFAULT 0,
    error TEXT NOT NULL DEFAULT ''
);
```

A `file_contents` table caches file content blobs keyed by SHA-256, so that repeated body extraction does not need to shell out to `git show` for every query.

The `symbol_history` view joins `snapshot_symbols` with `commits` to provide a timeline query surface:

```sql
CREATE VIEW symbol_history AS
SELECT
    s.id AS symbol_id, s.name, s.kind, s.body_hash,
    c.hash AS commit_hash, c.short_hash, c.message, c.author_time
FROM snapshot_symbols s
JOIN commits c ON c.hash = s.commit_hash;
```

## 4. The gitutil layer

Before you can index commits, you need to interact with git. The `internal/gitutil/` package wraps three git commands: `log`, `worktree`, and `show`.

`LogCommits` runs `git log --format` with a custom format string that produces one JSON-like record per line. The format is:

```
hash%n%h%n%s%n%an%n%ae%n%at%n%P%n%T%n---END---
```

Each commit record is delimited by `---END---`. The parser reads line by line, accumulates fields, and emits a `Commit` struct when it hits the delimiter. This approach avoids shell quoting issues and handles multi-line commit messages correctly because the format only captures the first line (`%s`).

`ChangedFiles` runs `git diff-tree -r --no-commit-id <hash>` to list the files that changed in a given commit. This is used during scanning to filter out commits that do not touch Go source files.

`ShowFile` runs `git show <hash>:<path>` to read a file at a specific commit. This is the fallback for body extraction when the file content is not in the cache.

The important thing about this layer is that it uses the git CLI directly rather than a Go git library. The reason is pragmatism: `go/packages.Load` requires a real filesystem with a real `go.mod`. No pure-Go git library can provide that. Git worktrees can. So the system shells out to `git` for discovery and content access, but uses `go/packages` for the actual symbol extraction.

## 5. The worktree approach to per-commit extraction

The central design problem is this: `go/packages.Load` needs a real filesystem directory containing Go source code at a specific commit. You cannot pass a git hash to the Go type checker. You need the files on disk.

The naive approach is to check out each commit, run the indexer, check out the next commit. This works but has three problems. It destroys the working directory, preventing parallel extraction. It is slow because `git checkout` touches every file. And it is not thread-safe.

The solution is git worktrees. A worktree is a lightweight checkout of a commit into a separate directory. The command is:

```bash
git worktree add --detach /tmp/worktree-abc123 <hash>
```

This creates a directory at `/tmp/worktree-abc123` containing the source tree at that commit. The main working directory is untouched. Multiple worktrees can exist simultaneously. When extraction is done, the worktree is removed with `git worktree remove /tmp/worktree-abc123`.

The implementation uses a goroutine pool with a semaphore:

```go
func indexWithWorktrees(ctx context.Context, repoRoot string, commits []gitutil.Commit, opts IndexOptions) (*IndexResult, error) {
    sem := make(chan struct{}, opts.Parallelism)
    var wg sync.WaitGroup
    var mu sync.Mutex
    result := &IndexResult{}

    for _, commit := range commits {
        wg.Add(1)
        go func(c gitutil.Commit) {
            defer wg.Done()
            sem <- struct{}{}        // acquire slot
            defer func() { <-sem }() // release slot

            wt, err := gitutil.CreateWorktree(repoRoot, c.Hash)
            if err != nil { /* record error */ return }
            defer gitutil.RemoveWorktree(wt)

            idx, err := indexer.Extract(wt.Dir())
            if err != nil { /* record error */ return }

            loader.LoadSnapshot(store, c, idx, wt.Dir())
        }(commit)
    }
    wg.Wait()
    return result, nil
}
```

The `Parallelism` field controls how many worktrees exist at once. The default is 1 (sequential). On a machine with enough disk space and RAM, setting it to 4 or 8 speeds up indexing significantly — 75 commits indexed in under 2 minutes on a standard laptop.

## 6. The loading pipeline

Each commit goes through a three-stage pipeline: discover, extract, load.

**Discover.** The scanner calls `gitutil.LogCommits` with a range spec like `HEAD~50..HEAD` or just `HEAD` (which means all reachable commits). It filters out commits that do not touch Go source files by checking `gitutil.ChangedFiles`. When `--incremental` is set, it skips commits already present in `history.db`.

**Extract.** For each discovered commit, a worktree is created. The existing Go indexer (`internal/indexer.Extract`) runs against the worktree directory. This produces an `Index` struct containing packages, files, symbols, and refs — the same struct used by the static JSON build.

**Load.** The `LoadSnapshot` function inserts the index into `history.db` in a single transaction. It computes `body_hash` by reading the source file from the worktree, seeking to `[startOffset:endOffset]`, and hashing the content with SHA-256. This is the step that makes function-level diff possible.

The body hash computation is worth understanding in detail:

```go
func computeBodyHash(dir, filePath string, startOffset, endOffset int) (string, error) {
    full := filepath.Join(dir, filePath)
    data, err := os.ReadFile(full)
    if err != nil { return "", err }
    if startOffset < 0 || endOffset > len(data) || startOffset > endOffset {
        return "", nil // invalid range, skip
    }
    body := data[startOffset:endOffset]
    hash := sha256.Sum256(body)
    return hex.EncodeToString(hash[:]), nil
}
```

The hash covers exactly the bytes between `startOffset` and `endOffset` in the source file. For a function like `func (s *Server) Handler() http.Handler { ... }`, this includes the signature, the opening brace, the body, and the closing brace. It does not include the doc comment above the function, because the Go AST reports the function's start position after the comment.

This means that if you add a comment to a function without changing its body, the `body_hash` stays the same. That is the right behavior: you want to detect code changes, not documentation changes.

## 7. The diff engine

With per-commit snapshots in the database, computing a diff between two commits becomes a SQL problem. The diff engine uses FULL OUTER JOIN on the symbol ID.

```sql
SELECT
    COALESCE(a.id, b.id) AS symbol_id,
    CASE
        WHEN a.id IS NULL THEN 'added'
        WHEN b.id IS NULL THEN 'removed'
        WHEN a.body_hash != b.body_hash THEN 'modified'
        WHEN a.signature != b.signature THEN 'signature-changed'
        ELSE 'unchanged'
    END AS change_type
FROM snapshot_symbols a
FULL OUTER JOIN snapshot_symbols b
  ON a.id = b.id AND a.commit_hash = ? AND b.commit_hash = ?
WHERE (a.id IS NULL OR b.id IS NULL
    OR a.body_hash != b.body_hash
    OR a.signature != b.signature)
```

The FULL OUTER JOIN is essential. An INNER JOIN would miss symbols that were added or removed. A LEFT JOIN would show removed symbols but not added ones. Only FULL OUTER JOIN produces the complete picture: symbols that exist in both commits, symbols that only exist in the old commit (removed), and symbols that only exist in the new commit (added).

The WHERE clause filters out unchanged symbols. Without this filter, a diff between two commits that share 330 symbols would return 330 rows even if only 3 changed. The filter turns a noisy result into a precise one.

The file diff uses the same pattern with `snapshot_files` and the `sha256` column instead of `body_hash`.

### Body diff: extracting function bodies from git history

The symbol diff tells you *that* a function changed. The body diff tells you *what* changed. Computing a body diff requires three steps:

1. Look up the symbol in both commits to get the file path and byte offsets.
2. Read the source file at both commits.
3. Extract the body bytes and compute a line-by-line diff.

The file reading uses a cache layer. `GetFileContent` first checks the `file_contents` table in `history.db`. If the content is not cached, it falls back to `gitutil.ShowFile(repoRoot, hash, path)`. The content is then stored in the cache for future queries.

```go
func extractBody(ctx context.Context, store *Store, repoRoot, commitHash, symbolID string) (string, error) {
    var filePath string
    var startOffset, endOffset int

    store.db.QueryRowContext(ctx, `
        SELECT f.path, s.start_offset, s.end_offset
        FROM   snapshot_symbols s
        JOIN   snapshot_files f ON f.commit_hash = s.commit_hash AND f.id = s.file_id
        WHERE  s.commit_hash = ? AND s.id = ?`, commitHash, symbolID
    ).Scan(&filePath, &startOffset, &endOffset)

    content, _ := GetFileContent(ctx, store, repoRoot, commitHash, filePath)
    return string(content[startOffset:endOffset]), nil
}
```

The unified diff is simple but effective. It finds the common prefix and suffix of the old and new bodies, then marks the middle as changed. Every line gets a prefix: ` ` for context, `-` for removed, `+` for added. The output shows the entire function — signature, body, and closing brace — not just the changed region.

```go
func simpleUnifiedDiff(old, new_ string) string {
    oldLines := splitLines(old)
    newLines := splitLines(new_)

    prefix := commonPrefix(oldLines, newLines)
    suffix := commonSuffix(oldLines[prefix:], newLines[prefix:])

    var out string
    for i := 0; i < prefix; i++ {
        out += fmt.Sprintf("  %s\n", oldLines[i])       // context
    }
    for i := prefix; i < len(oldLines)-suffix; i++ {
        out += fmt.Sprintf("- %s\n", oldLines[i])       // removed
    }
    for i := prefix; i < len(newLines)-suffix; i++ {
        out += fmt.Sprintf("+ %s\n", newLines[i])       // added
    }
    for i := len(oldLines)-suffix; i < len(oldLines); i++ {
        out += fmt.Sprintf("  %s\n", oldLines[i])       // context
    }
    return out
}
```

This is not a patience diff or an LCS diff. It is a simple prefix-suffix detection that handles the most common case well: a function where the top and bottom are unchanged but the middle changed. For an MVP, this is sufficient. A proper diff library can be swapped in later without changing the database schema or the API.

## 8. The structured query concept catalog

The concept catalog is a system for defining named, parameterized SQL queries that live alongside the code. A concept is a SQL file with a YAML-like preamble in a comment block:

```sql
/* codebase-browser concept
name: hotspots
short: Most frequently changed symbols (by body hash)
params:
  - name: limit
    type: int
    default: 20
    help: Max results
  - name: min_versions
    type: int
    default: 2
    help: Minimum distinct body versions to be considered a hotspot
tags: [history, analysis]
*/
SELECT
    s.id AS symbol_id,
    s.name,
    COUNT(DISTINCT s.body_hash) AS distinct_versions,
    COUNT(DISTINCT c.hash) AS commit_count
FROM snapshot_symbols s
JOIN commits c ON c.hash = s.commit_hash
WHERE s.body_hash != ''
GROUP BY s.id
HAVING COUNT(DISTINCT s.body_hash) >= {{.min_versions}}
ORDER BY distinct_versions DESC
LIMIT {{.limit}};
```

The preamble defines the command metadata: name, description, typed parameters, and tags. The SQL body is a Go template rendered against the user's parameter values. The `{{.limit}}` syntax is standard Go `text/template`.

The catalog loads concepts from two sources: embedded files compiled into the Go binary, and external repositories specified via flags. External repositories take precedence over embedded ones. This lets teams maintain their own query library without forking.

The catalog routes queries to the correct database. Concepts under `history/` execute against `history.db`. All others execute against `codebase.db`. This routing happens transparently in the server — the user does not need to know which database a concept targets.

The concept system is deliberately SQL-only. There is no JavaScript runtime, no plugin system, no external dependency beyond the Go standard library. A concept is a SQL file with a comment header. It can be created, edited, and tested with any text editor and a SQLite client. This simplicity is a feature: the barrier to creating a new concept is zero.

### Concept naming and path mapping

Concepts are organized into directories that map to both CLI paths and web UI groups. A concept at `concepts/history/hotspots.sql` becomes:

- CLI: `codebase-browser query commands history hotspots`
- Web: `/#/queries/history/hotspots`
- API: `GET /api/query-concepts/history/hotspots`

The directory structure is the namespace. There is no separate registry or manifest file. Drop a SQL file into the right directory and it appears everywhere.

### Parameter template constraints

One non-obvious constraint: concept parameter names cannot contain hyphens. Go's `text/template` package rejects `{{.my-param}}` because `-` is not a valid identifier character in Go. All parameter names must use underscores: `symbol_id`, not `symbol-id`. This is a Go template limitation, not a design choice.

## 9. The server API

The server exposes the index through a REST API under `/api/`. It is a thin layer: each endpoint runs a SQL query against the database and returns JSON. There is no ORM, no caching layer, no WebSocket push.

### Static index endpoints

| Method | Path | Purpose |
|--------|------|--------|
| GET | `/api/index` | Package/file/symbol counts |
| GET | `/api/packages` | All packages |
| GET | `/api/symbol/{id}` | Symbol detail with doc and signature |
| GET | `/api/source?path=...` | Source file content |
| GET | `/api/xref/{symbolID}` | Cross-references for a symbol |

### History endpoints

| Method | Path | Purpose |
|--------|------|--------|
| GET | `/api/history/commits` | List indexed commits |
| GET | `/api/history/commits/{hash}` | Single commit detail |
| GET | `/api/history/diff?from=X&to=Y` | File and symbol diff between two commits |
| GET | `/api/history/symbols/{id}/history` | Per-symbol commit timeline |
| GET | `/api/history/symbol-body-diff?from=X&to=Y&symbol=Z` | Full function body diff |

### Concept endpoints

| Method | Path | Purpose |
|--------|------|--------|
| GET | `/api/query-concepts` | List all concepts |
| POST | `/api/query-concepts/{path}` | Execute a concept with parameters |

The concept execution endpoint accepts a JSON body with `params` (a map of parameter values) and `renderOnly` (boolean, to preview SQL without executing). The response includes `renderedSql`, `columns`, and `rows`.

A critical detail: the `symbol-body-diff` endpoint returns JSON with **camelCase** field names. Go's `encoding/json` defaults to the struct field name, which is PascalCase. The `BodyDiffResult` struct needs explicit `json` tags:

```go
type BodyDiffResult struct {
    SymbolID    string `json:"symbolId"`
    OldBody     string `json:"oldBody"`
    NewBody     string `json:"newBody"`
    UnifiedDiff string `json:"unifiedDiff"`
    OldRange    string `json:"oldRange"`
    NewRange    string `json:"newRange"`
}
```

Without these tags, the React client receives `SymbolID`, `OldBody`, etc. TypeScript accesses `data.oldBody` which is `undefined`, and the diff silently fails with "No body changes between these commits" because `undefined === undefined` is `true`.

## 10. The React UI

The web UI is a single-page React application that runs inside the Go binary's embedded web server. It uses HashRouter (not BrowserRouter) because the Go server serves the SPA from `/` and handles API routes under `/api/`. A BrowserRouter would require server-side route matching for every path; a HashRouter keeps all routing client-side.

This has one non-obvious consequence: query parameters work, but they live after the hash. A URL like `http://host:3011/#/history?symbol=sym:...` is parsed by `useLocation().search` inside HashRouter. The `useSearchParams` hook from React Router does not work reliably with HashRouter in all versions, so the code uses `useLocation` and `new URLSearchParams(location.search)` directly.

### The history page

The history page has two modes. The default mode shows a commit timeline sidebar on the left and a diff panel on the right. The user selects an "old" and a "new" commit by clicking buttons in the sidebar. The diff panel shows file changes and symbol changes between those two commits.

When the user clicks a symbol name in the diff table, a body diff panel opens directly below. The body diff calls `/api/history/symbol-body-diff` with the sidebar's already-selected old and new commits. There is no secondary from/to selection — the sidebar already defined the commit range.

The second mode is a standalone symbol history view, reached from a "View change history" link on any symbol page. It navigates to `/#/history?symbol=<id>` and shows the full commit timeline for that symbol with per-row from/to selectors. This mode is necessary because the user arrived from a symbol page, not from the commit diff view, so there is no pre-selected commit range.

The state flow is:

```
CommitTimeline (owns selectedOld, selectedNew)
  ├── Sidebar: commits list with old/new buttons
  └── Right panel:
       ├── if initialSymbol → StandaloneSymbolHistory
       │     └── SymbolHistoryPanel (with from/to selectors)
       └── else → DiffView (shows file + symbol diff)
             └── click symbol → SymbolBodyDiffView (body diff for selectedOld→selectedNew)
```

### Commit highlighting in the sidebar

When a symbol is selected in the diff view, the `DiffView` component queries the symbol's history and computes which commits modified that symbol's body. The set of modified commit hashes is passed up to `CommitTimeline`, which highlights those commits in the sidebar with an orange background.

This is the information that was previously visible in the history panel's from/to table, now surfaced directly in the commit list. The user can see at a glance which of the 82 indexed commits changed the function they are investigating.

### The query concepts page

The query concepts page lists all available concepts in a grouped sidebar and shows the selected concept's parameters, source, and results. The concept source is shown in a collapsible section with Prism.js syntax highlighting. The preamble (the `/* ... */` comment block) is rendered as muted text, and the SQL body gets proper token coloring for keywords, strings, and comments.

The page uses Prism.js for SQL highlighting. The import pattern requires care: `import 'prismjs'` and `import 'prismjs/components/prism-sql'` must both be present to register the SQL grammar on the global `Prism` object. The highlight function is then called as `Prism.highlight(code, Prism.languages.sql, 'sql')` and injected via `dangerouslySetInnerHTML`.

## 11. Key implementation files

| File | Lines | Purpose |
|------|-------|--------|
| `internal/gitutil/log.go` | 163 | `LogCommits`, `ChangedFiles`, `ResolveRef` via git CLI |
| `internal/gitutil/worktree.go` | 106 | `CreateWorktree`, `RemoveWorktree`, goroutine-safe pool |
| `internal/gitutil/show.go` | 34 | `ShowFile` reads a file at a specific commit |
| `internal/history/schema.go` | 133 | Table DDL for `commits`, `snapshot_*`, `file_contents`, views |
| `internal/history/store.go` | 156 | Open, Create, Close, ListCommits, HasCommit |
| `internal/history/loader.go` | 207 | LoadSnapshot: bulk-insert per-commit index + body_hash |
| `internal/history/scanner.go` | 80 | ScanCommits: discover, filter, incremental skip |
| `internal/history/indexer.go` | 165 | IndexCommits: parallel worktree pool orchestration |
| `internal/history/diff.go` | 190 | DiffCommits: FULL OUTER JOIN symbol/file diff |
| `internal/history/bodydiff.go` | 191 | DiffSymbolBodyWithContent, simpleUnifiedDiff, extractBody |
| `internal/history/cache.go` | 110 | GetFileContent: cache → git show fallback |
| `internal/concepts/types.go` | 111 | Concept, Param, SourceRoot type definitions |
| `internal/concepts/catalog.go` | 128 | LoadCatalog from embedded + external roots |
| `internal/concepts/render.go` | 223 | RenderConcept: template rendering with safe helpers |
| `internal/concepts/repositories.go` | 107 | External repository discovery and precedence |
| `internal/server/api_history.go` | 177 | 6 HTTP endpoints for history queries |
| `internal/server/api_concepts.go` | 240 | Concept list, execute, DB routing |
| `ui/src/features/history/HistoryPage.tsx` | 570 | Commit timeline, diff view, symbol history, body diff |
| `ui/src/features/query/QueryConceptsPage.tsx` | 574 | Concept browser with Prism highlighting |

Total implementation: approximately 3,400 lines of Go and 1,300 lines of TypeScript/React.

## 12. What failed along the way

The implementation went through several cycles of mistakes and fixes. The most instructive failures:

**PascalCase JSON fields.** The `BodyDiffResult` struct had no `json` tags. Go's `encoding/json` marshals struct fields as-is (PascalCase). TypeScript expected camelCase. Every field was `undefined`. The diff always said "No body changes" because `undefined === undefined` is `true`. The fix was adding `json:"camelCase"` tags to every field.

**`useLocation` after conditional returns.** The `HistoryPage` component called `useLocation()` after `if (isLoading) return ...`. React requires all hooks to be called unconditionally, in the same order, on every render. Moving the hook above the early returns fixed the crash.

**Concept param names with hyphens.** Parameters named `symbol-id` or `min-versions` caused Go template parse errors: `bad character U+002D '-'`. The fix was renaming to `symbol_id` and `min_versions`.

**`FULL OUTER JOIN` compatibility.** Some SQLite builds handle FULL OUTER JOIN differently. The `pr-summary` concept was rewritten to use `LEFT JOIN ... UNION ALL` as a safer alternative.

**Source page in serve mode.** The `SourcePage` component used `./source/${path}` for static file serving. In serve mode, source files are at `/api/source?path=...`. The fix was a dual-mode fetch: try the API endpoint first, fall back to static file.

**Stale RTK Query cache.** After fixing the Go JSON tags, the browser still showed old responses because RTK Query cached the PascalCase response. A hard reload was needed to pick up the new camelCase response.

## 13. Closing

The git-aware codebase index is not a complex system. It is a SQLite database, a git worktree pool, a SQL query catalog, and a thin web UI. The value is not in any individual component but in the combination: once you have per-commit symbol snapshots with body hashes, every question about code history becomes a SQL query.

The architecture has a clear extension path. Adding a new language means adding a new extractor. Adding a new query means adding a new SQL file. Adding a new visualization means adding a new React component that calls an existing API endpoint. None of these extensions require changing the database schema, the server, or the indexing pipeline.

The key insight is that `body_hash` is the foundation. Without it, you have a symbol catalog. With it, you have a change detection system. And once you have change detection, every downstream feature — hotspots, timelines, per-function diffs — follows naturally.
