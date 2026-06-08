---
title: "Docmgrignore: Building a Workspace-Owned Ignore Policy"
aliases:
  - Docmgrignore Workspace Ignore Policy
  - Workspace-Owned docmgrignore
  - docmgr ignore implementation report
tags:
  - article
  - docmgr
  - go
  - gitignore
  - architecture
  - testing
status: active
type: article
created: 2026-06-08
repo: /home/manuel/code/wesen/go-go-golems/docmgr
source_ticket: DOCMGR-IGNORE-001
pull_request: https://github.com/go-go-golems/docmgr/pull/40
---

# Docmgrignore: Building a Workspace-Owned Ignore Policy

This report explains the implementation of workspace-wide `.docmgrignore` support in `docmgr`. The work started with a concrete failure: a ticket-local `scripts/node_modules` directory contained Markdown files from Playwright, and `docmgr doctor` treated those files as managed documentation. The symptom was a set of frontmatter errors for files that were never intended to be part of the documentation workspace.

The final design makes ignore policy a property of the workspace. `Workspace` constructs one matcher, indexing uses that matcher before frontmatter parsing, `doctor` consumes the indexed result instead of reimplementing ignore semantics, and `docmgr ignore explain` exposes the decision path for a given file. The implementation uses `github.com/denormal/go-gitignore` rather than a handwritten glob engine.

> [!summary]
> - `.docmgrignore` moved from a doctor-specific post-filter to workspace-owned ingest policy.
> - Ignored directories and ignored files are skipped before `ReadDocumentWithFrontmatter`, so dependency Markdown no longer becomes a repair diagnostic.
> - `go-gitignore` handles repository and nested `.docmgrignore` behavior; docmgr adds built-in defaults, path normalization, workspace integration, and explanation output.
> - Scenario validation now covers ignored `scripts/node_modules` files and nested `.docmgrignore` file-level patterns.

## Why this note exists

The interesting part of this change is not that `node_modules` became ignored. The interesting part is where ignore decisions belong in a documentation system that has a workspace index, a frontmatter parser, query APIs, command-specific validation, and scenario tests. If ignore handling lives too late in the pipeline, ignored files can still consume parser time, produce diagnostics, and affect secondary filesystem walks. If ignore handling lives in only one command, other commands will disagree about what the workspace contains.

The final implementation treats ignored files as outside the indexed workspace. That decision affects the architecture: every index-backed command receives a cleaner document universe, and command-specific code no longer needs to know how `.docmgrignore` files are loaded.

## The failure mode

The original failure had this shape:

```text
ttmp/2026/06/08/MINIVIZ-008--.../scripts/node_modules/.pnpm/playwright-core@.../README.md
```

That file was ordinary package documentation. It did not begin with docmgr YAML frontmatter. The old `doctor` flow still found it because `.docmgrignore` patterns were applied after the workspace index had already parsed Markdown files. The observed diagnostic was the expected result of applying the frontmatter parser to the wrong input:

```text
YAML/frontmatter syntax error
Problem: frontmatter delimiters '---' not found
```

The immediate patch could have been a larger `doctor` filter. That would not have fixed the real issue. `doctor` is only one consumer of the workspace index. Search, list, status, SQLite export, and future index-backed commands would still have a chance to see paths that the user intended to exclude.

## The old architecture

Before this change, ignore handling was distributed across several mechanisms:

| Layer | Existing behavior | Limitation |
| --- | --- | --- |
| `internal/documents.WalkDocuments` | Recursively visited Markdown files and skipped underscore directories. | It had no file-level skip hook and no `.docmgrignore` matcher. |
| `internal/workspace.DefaultIngestSkipDir` | Hard-skipped `.meta` and underscore directories. | It was intentionally narrow and not user-configurable. |
| `Workspace.InitIndex` | Parsed Markdown and stored successful docs plus parse errors in SQLite. | It ingested files before doctor-specific ignore filters ran. |
| `Workspace.QueryDocs` | Returned indexed docs according to scope and visibility flags. | Query visibility is not the same as filesystem ignore policy. |
| `pkg/commands/doctor.go` | Loaded `.docmgrignore` from repo/docs root and post-filtered query results. | It was command-specific and too late to prevent parse errors. |
| Duplicate-index scan | Walked the filesystem separately to find extra `index.md` files. | It needed its own ignore handling, including file-level ignores. |

The important distinction is between **visibility** and **ingestion**. A query option can hide a document after it has been indexed. An ingest policy prevents a path from becoming a document candidate in the first place. `.docmgrignore` is ingest policy.

## The design decision

The design originally considered an incremental option: pass an optional matcher through `BuildIndexOptions`, keep old doctor post-filtering for compatibility, then migrate callers over time. That approach was rejected because it preserved two interpretations of ignore behavior.

The implemented design is direct:

```text
DiscoverWorkspace / NewWorkspaceFromContext
  -> construct WorkspaceContext
  -> construct paths.Resolver
  -> load internal/ignore.Matcher
  -> return Workspace{resolver, ignore, db=nil}

Workspace.InitIndex
  -> WalkDocuments(root,
       WithSkipDir(ignore directory decision),
       WithSkipFile(ignore file decision))
  -> parse only non-ignored Markdown
  -> insert non-ignored docs into SQLite

QueryDocs / doctor / list / search
  -> operate on the same indexed document set
```

The result is a single source of truth. The workspace owns the matcher, indexing respects it, and commands consume the resulting document set.

## Implementation structure

The work introduced one new internal package and changed three existing runtime paths:

```text
internal/ignore/ignore.go
  LoadOptions
  Matcher
  Decision
  TraceStep
  BuiltinPatterns

internal/workspace/workspace.go
  Workspace.ignore
  Workspace.IgnoreMatcher()
  matcher construction in NewWorkspaceFromContext

internal/documents/walk.go
  WithSkipFile

internal/workspace/index_builder.go
  WithSkipDir + WithSkipFile applied before parsing

pkg/commands/doctor.go
  removed doctor-local .docmgrignore loading
  duplicate-index scan uses file-level skip decisions

pkg/commands/ignore_explain.go
  docmgr ignore explain <path>
```

The implementation is small because `go-gitignore` already understands repository traversal and nested ignore files. Docmgr does not parse every ignore pattern itself. It composes matchers, normalizes paths, adds built-in defaults, and records decisions in a form commands can display.

## The matcher

The core matcher lives in `internal/ignore/ignore.go`. It defines built-in patterns, source metadata, and a `Decision` object that can be returned to callers.

```go
const FileName = ".docmgrignore"

var BuiltinPatterns = []string{
    ".git/",
    "**/.git/**",
    "node_modules/",
    "**/node_modules/**",
    ".pnpm/",
    "**/.pnpm/**",
    "dist/",
    "**/dist/**",
    "build/",
    "**/build/**",
    "coverage/",
    "**/coverage/**",
    ".venv/",
    "**/.venv/**",
    "__pycache__/",
    "**/__pycache__/**",
}
```

The doubled patterns are deliberate. A simple directory-only pattern works for directory decisions, but built-ins are held in a single matcher created with `gitignore.New(...)`, not a repository hierarchy loaded from disk. Tests showed that `node_modules/` alone did not ignore descendants in that form. Adding `**/node_modules/**` makes the built-in policy explicit for files below the directory.

The matcher loads three kinds of sources:

```go
type SourceKind string

const (
    SourceBuiltin    SourceKind = "builtin"
    SourceRepository SourceKind = "repository"
    SourceDocsRoot   SourceKind = "docs-root"
)
```

The repository matcher is the important one:

```go
gi, err := gitignore.NewRepositoryWithFile(repoRoot, FileName)
```

That call gives docmgr nested `.docmgrignore` support without writing a recursive loader. If the docs root is outside the repository root, docmgr also creates a docs-root repository matcher. In the normal case, the repository matcher sees `.docmgrignore` files in the repo, the docs root, ticket directories, and nested `scripts/` directories.

## Decision objects

`Matcher.Match` returns a `Decision` rather than a boolean:

```go
type Decision struct {
    Path          string
    IsDir         bool
    Ignored       bool
    Matched       bool
    SourceKind    SourceKind
    SourceName    string
    Pattern       string
    PatternFile   string
    PatternLine   int
    PatternColumn int
    Trace         []TraceStep
}
```

This type exists because ignore decisions need to be inspectable. A boolean is enough for pruning. It is not enough for debugging a workspace. The `docmgr ignore explain` command uses the same decision object that indexing uses, which means diagnostic output and runtime behavior are connected to the same matcher.

The match algorithm performs three steps:

```go
func (m *Matcher) Match(path string, isDir bool) Decision {
    abs := m.resolvePath(path)
    decision := Decision{Path: filepath.ToSlash(abs), IsDir: isDir}

    for _, src := range m.sources {
        if src.gi == nil || !isWithin(src.base, abs) || abs == src.base {
            append non-match trace
            continue
        }

        match := src.gi.Absolute(abs, isDir)
        if match == nil {
            append non-match trace
            continue
        }

        decision.Matched = true
        decision.Ignored = match.Ignore()
        decision.Pattern = match.String()
        decision.PatternLine = match.Position().Line
    }

    return decision
}
```

There is a guard for `abs == src.base`. This guard was added after workspace tests found that `go-gitignore.Absolute` panicked when asked to match the repository base path itself. `WalkDocuments` calls skip predicates for the root directory, so the matcher must treat the root path as a non-match.

## Path normalization

The matcher accepts absolute paths, repo-relative paths, and docs-root-relative paths. That flexibility matters because docmgr commands print and accept different path forms.

The first implementation treated every relative path as docs-root-relative. That caused this command:

```bash
docmgr ignore explain --root ttmp ttmp/2026/06/08/TICKET--slug/scripts/node_modules/pkg/README.md
```

to display a resolved path containing `ttmp/ttmp`. The fix was to recognize paths beginning with the docs-root base name as repo-relative docs-root paths:

```go
cleanRel := filepath.Clean(path)
if m.repoRoot != "" && m.docsRoot != "" {
    docsBase := filepath.Base(m.docsRoot)
    if cleanRel == docsBase || strings.HasPrefix(cleanRel, docsBase+string(filepath.Separator)) {
        return filepath.Clean(filepath.Join(m.repoRoot, cleanRel))
    }
}
```

This is a small detail, but it is the kind of detail that determines whether a debugging command is trustworthy. The displayed path must correspond to the path that was actually matched.

## Workspace ownership

The `Workspace` type now owns the matcher:

```go
type Workspace struct {
    ctx      WorkspaceContext
    resolver *paths.Resolver
    ignore   *docignore.Matcher
    db       *sql.DB
    ftsAvailable bool
}
```

The matcher is constructed in `NewWorkspaceFromContext`:

```go
ignoreMatcher, err := docignore.Load(context.Background(), docignore.LoadOptions{
    RepoRoot:       ctx.RepoRoot,
    DocsRoot:       ctx.Root,
    IncludeBuiltin: true,
    IncludeNested:  true,
})
```

This placement means tests that construct a workspace directly receive production ignore behavior. It also means every command that calls `DiscoverWorkspace` receives the same matcher. There is no separate doctor loader, search loader, or export loader.

The public accessor is intentionally narrow:

```go
func (w *Workspace) IgnoreMatcher() *docignore.Matcher {
    return w.ignore
}
```

Most commands should not need it. Index-backed commands should rely on `InitIndex` to prune ignored paths. `doctor` needs it because it still performs additional filesystem walks for missing-index and duplicate-index checks.

## Index-time pruning

The critical runtime change is in `internal/workspace/index_builder.go`. `Workspace.InitIndex` now passes the matcher into `documents.WalkDocuments` through directory and file skip hooks:

```go
documents.WithSkipDir(func(path string, d fs.DirEntry) bool {
    if DefaultIngestSkipDir(path, d) {
        return true
    }
    if ignoreMatcher != nil && ignoreMatcher.Ignore(path, true) {
        return true
    }
    return false
}),

documents.WithSkipFile(func(path string, d fs.DirEntry) bool {
    if ignoreMatcher != nil && ignoreMatcher.Ignore(path, false) {
        return true
    }
    return false
})
```

The `WithSkipFile` hook was not part of the initial implementation. The first pass only skipped ignored directories. Scenario testing exposed the missing case: a nested `.docmgrignore` containing `*.md` should ignore a file below a directory that remains traversable. Directory pruning cannot catch that. The file-level hook must run before `ReadDocumentWithFrontmatter`.

The final walk order is:

```go
if d.IsDir() {
    if underscore directory { SkipDir }
    if cfg.skipDir(path, d) { SkipDir }
    return nil
}

if cfg.skipFile(path, d) { return nil }
if ext != ".md" { return nil }

ReadDocumentWithFrontmatter(path)
```

That ordering preserves the old hard skip for underscore directories, adds user-configurable directory pruning, and ensures file-level patterns can skip generated Markdown before parsing.

## Doctor after the cutover

`doctor` changed from owning ignore parsing to using the workspace policy. It now discovers the workspace first and reuses its matcher:

```go
ws, err := workspace.DiscoverWorkspace(ctx, workspace.DiscoverOptions{RootOverride: settings.Root})
ignoreMatcher := ws.IgnoreMatcher()
```

It still has command-specific `--ignore-dir` and `--ignore-glob` flags. Those are treated as explicit doctor filters, not as `.docmgrignore` semantics. This distinction keeps compatibility without reintroducing two sources of `.docmgrignore` truth.

The duplicate-index scan was an important follow-up. The workspace index pruned ignored files, but duplicate-index detection uses a separate filesystem walk. A review comment on PR #40 pointed out that an ignored `design-doc/index.md` file could still be appended by that walk. The fix was to apply ignore decisions to files as well as directories:

```go
if info.IsDir() {
    if shouldSkipPath != nil && shouldSkipPath(path, base, true) {
        return filepath.SkipDir
    }
    return nil
}
if shouldSkipPath != nil && shouldSkipPath(path, base, false) {
    return nil
}
if info.Name() == "index.md" {
    indexFiles = append(indexFiles, path)
}
```

This pattern should be the rule for future doctor filesystem walks: directory pruning is necessary, but not sufficient.

## Explanation command

`docmgr ignore explain` was added to make matcher behavior observable:

```bash
docmgr ignore explain --root ttmp \
  ttmp/2026/06/08/TICKET--slug/scripts/node_modules/pkg/README.md \
  --with-glaze-output --output json
```

A representative output row is:

```json
{
  "ignored": true,
  "matched": true,
  "pattern": "**/node_modules/**",
  "source_kind": "builtin",
  "docs_root": "/home/manuel/code/wesen/go-go-golems/docmgr/ttmp",
  "repo_root": "/home/manuel/code/wesen/go-go-golems/docmgr"
}
```

The command is implemented as a Glazed command in `pkg/commands/ignore_explain.go` and wired under `cmd/docmgr/cmds/ignorecmd`. It supports `--trace`, which emits one row per matcher source. The trace output is intentionally structured because this command is also useful for automated regression tests.

## Scenario coverage

The end-to-end scenario is `test-scenarios/testing-doc-manager/21-ignore-policy.sh`. It creates two invalid Markdown files:

```text
scripts/node_modules/pkg/README.md
scripts/local-cache/bad.md
```

The first is ignored by built-in or repository-root dependency rules. The second is ignored by a nested `.docmgrignore`:

```gitignore
*.md
```

The scenario verifies both decisions with `docmgr ignore explain`, then runs:

```bash
docmgr doctor --ticket MEN-4242 --stale-after 30 --fail-on error
```

The success condition is that neither ignored file appears in doctor output, and doctor reports no error. This scenario caught the missing file-level skip hook. Unit tests had verified directory pruning; the scenario exercised the whole command path.

The full scenario suite also required a separate repair. The nested `scenariolog` module imported the newer Glazed facade packages but still depended on `github.com/go-go-golems/glazed v0.7.3`. Bumping it to `v1.0.5` made the scenario harness build again. The full suite requires the docmgr binary to be built with `-tags sqlite_fts5`, because search scenarios require FTS5:

```bash
go build -tags sqlite_fts5 -o /tmp/docmgr-ignore ./cmd/docmgr
cd scenariolog && go build -tags sqlite_fts5 -o /tmp/scenariolog-local ./cmd/scenariolog
DOCMGR_PATH=/tmp/docmgr-ignore \
SCENARIOLOG_PATH=/tmp/scenariolog-local \
bash test-scenarios/testing-doc-manager/run-all.sh /tmp/docmgr-scenario-full-fts
```

The final run reached step 21 and completed successfully.

## What changed in the codebase

The implementation was split into focused commits:

| Commit | Purpose |
| --- | --- |
| `55fff68` | Added `internal/ignore` with `go-gitignore` matching and tests. |
| `8b95d7b` | Made `Workspace` own the matcher and prune ignored paths during indexing. |
| `050d9e6` | Removed doctor-local `.docmgrignore` loading and used workspace ignores. |
| `e29b36b` | Added `docmgr ignore explain`. |
| `4894f5c` | Updated docs, added scenario coverage, and added file-level walk skips. |
| `1070d2f` | Fixed the `scenariolog` Glazed dependency so the full scenario suite could run. |
| `0b2bcde` | Honored ignored `index.md` files in doctor duplicate-index scans. |

The most important runtime files are:

- `/home/manuel/code/wesen/go-go-golems/docmgr/internal/ignore/ignore.go`
- `/home/manuel/code/wesen/go-go-golems/docmgr/internal/workspace/workspace.go`
- `/home/manuel/code/wesen/go-go-golems/docmgr/internal/workspace/index_builder.go`
- `/home/manuel/code/wesen/go-go-golems/docmgr/internal/documents/walk.go`
- `/home/manuel/code/wesen/go-go-golems/docmgr/pkg/commands/doctor.go`
- `/home/manuel/code/wesen/go-go-golems/docmgr/pkg/commands/ignore_explain.go`
- `/home/manuel/code/wesen/go-go-golems/docmgr/test-scenarios/testing-doc-manager/21-ignore-policy.sh`

## Important lessons

### Ignore policy belongs before parsing

The central lesson is placement. If a file is ignored, it should not be parsed as a document. Applying ignore rules after parsing can hide output, but it cannot prevent parse errors, wasted indexing work, or inconsistencies between commands.

### Directory ignores and file ignores are separate checks

A directory skip hook handles `node_modules/`. It does not handle a nested `.docmgrignore` pattern such as `*.md` inside a traversable directory. The walker needs both `WithSkipDir` and `WithSkipFile`, and the file hook must run before frontmatter parsing.

### Secondary filesystem walks must share the policy

`doctor` still has filesystem walks that are not part of the workspace index. Missing-index detection and duplicate-index detection must consult the same matcher. The PR review comment about ignored duplicate `index.md` files exposed this exact class of bug.

### Debuggability is part of the feature

`docmgr ignore explain` is not just a convenience command. It is a way to preserve confidence in the new architecture. When a user asks why a path is absent from search or doctor, the answer should come from the same matcher that made the runtime decision.

### Dependency drift can block validation

The ignore implementation was correct before the full scenario suite passed, but the harness could not run because `scenariolog` had drifted from Glazed's facade package migration. The fix was small, but the failure was significant: validation tools are part of the system being maintained.

## Remaining design questions

The implementation is complete enough for the current use case, but a few questions remain worth tracking:

- `Workspace.NewWorkspaceFromContext` currently loads the ignore matcher with `context.Background()`. If ignore loading becomes more expensive or remote-aware in the future, the constructor API may need a context.
- Built-in ignores can be overridden by later `go-gitignore` matches in the decision object, but directory pruning can make re-inclusion under a built-in ignored directory difficult. If re-inclusion becomes a requirement, it needs explicit tests and possibly a more conservative pruning strategy.
- `ignore explain` currently reports the repository matcher as the source for nested matches. The decision is correct, and pattern position is available, but source display could become more precise.
- `--ignore-dir` and `--ignore-glob` remain as doctor-specific compatibility flags. A future cleanup could either remove them or fold them into a command-override source in `internal/ignore`.

## Recommended implementation sequence for similar changes

A similar change should be implemented in this order:

1. Define the policy at the lowest correct layer. For ignore handling, that layer is workspace ingestion, not command output.
2. Add a small package that owns the policy and returns inspectable decisions.
3. Integrate the package into the central runtime path before changing command behavior.
4. Update command-specific filesystem walks to call the same policy.
5. Add an explanation command or debug mode that uses the same runtime decision object.
6. Write unit tests for matching semantics and integration tests for the indexing boundary.
7. Add a scenario test that creates a realistic failure case with invalid input below an ignored path.
8. Run the full scenario harness with the same build tags used by CI or production validation.

## Closing

The `.docmgrignore` work is a small feature at the command-line surface, but it changes an important invariant inside docmgr: the workspace index should contain managed documentation, not every Markdown file that happens to live below `ttmp`. That invariant makes validation quieter, search more predictable, and command behavior easier to reason about.

The implementation is also a useful pattern for future docmgr changes. Shared workspace behavior should live in the workspace layer. Commands should consume the workspace contract. When a command must perform extra filesystem work, it should call the same policy object rather than rebuilding a partial version of the rule set.
