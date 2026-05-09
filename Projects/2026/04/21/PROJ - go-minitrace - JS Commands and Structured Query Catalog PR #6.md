---
title: go-minitrace PR #6 — JS Commands, Structured Query Catalog, and Framework Metadata
aliases:
  - go-minitrace PR #6
  - go-minitrace task/minitrace-js
tags:
  - project
  - go-minitrace
  - javascript
  - duckdb
  - query-catalog
  - structured-commands
  - goja
  - framework-metadata
  - transcript-analysis
  - minitrace
status: active
type: project
created: 2026-04-21
repo: /home/manuel/code/wesen/corporate-headquarters/go-minitrace
---

# go-minitrace PR #6 — JS Commands, Structured Query Catalog, and Framework Metadata

This is a large PR — 233 files changed, 23,526 insertions, 389 deletions — that adds JavaScript-backed analysis commands to the minitracecmd catalog system, extends the structured query command architecture to support both SQL and JS sources, preserves framework-specific metadata in the Claude Code adapter, adds comprehensive adapter converter tests, and establishes a nightly transcript review workflow. The work spans three months of focused development and represents the maturation of go-minitrace from a CLI for session conversion into a full analysis platform.

> [!summary]
> This PR has four intertwined identities:
> 1. A scanner-first JS verb command system that lets JavaScript files define typed, executable analysis commands alongside SQL
> 2. A structured query command catalog that provides discoverability, typed parameters, and alias support for reusable queries
> 3. A framework metadata preservation pass that captures adapter-specific fields (entrypoint, slug, parent_uuid, is_sidechain) in the Claude Code converter
> 4. A nightly transcript review workflow built from structured commands that can generate a narrative summary of a day's agent work

## The Starting Point

go-minitrace started as a Go port of the Python minitrace tool for analyzing AI agent session transcripts. Before this PR, its main capabilities were:

- Discovery commands for Claude Code, Codex, Pi, claude.ai, and ChatGPT session stores
- Conversion of those sessions into a normalized minitrace JSON archive format
- A DuckDB-backed `query duckdb` command for running SQL against loaded archives
- A basic web UI served by `go-minitrace serve`

The gap was analysis workflow. Running `query duckdb --sql "SELECT ..."` is fine for one-off exploration, but not for repeatable team workflows. When a query becomes part of the daily review process, it needs a stable name, typed parameters, discoverability in `--help`, and ideally a matching form in the web UI. This PR builds that layer.

## Architecture: Two Command Definition Languages, One Command System

The core architectural decision was to keep `minitracecmd` as the single owner of the command catalog while supporting two definition languages: SQL (the existing sqleton style) and JavaScript (the new scanner-first approach). Neither system rewrites the other; they coexist in the same catalog with a clean runtime dispatch.

### SQL Commands (Sqleton Style)

SQL commands use a YAML preamble in SQL comments:

```sql
/* sqleton
name: session-list
short: List sessions
flags:
  - name: limit
    type: int
    default: 10
*/
SELECT id, title, framework, created_at
FROM {{TABLE_NAME}}
LIMIT {{limit}}
```

The sqleton preamble defines the command name, help text, and typed flags. The SQL body is a template rendered against the loaded DuckDB table. This is the existing pattern and it works well for data retrieval.

### JS Commands (Scanner-First)

JS commands use a different surface that maps to the same command model:

```javascript
__section__("filters", {
  fields: {
    limit: { type: "int", default: 10 }
  }
});

function sessionList(filters) {
  const mt = require("minitrace");
  return mt.query(`
    SELECT id, title
    FROM ${mt.tableName}
    LIMIT ${filters.limit}
  `);
}

__verb__("sessionList", {
  name: "session-list",
  short: "List sessions",
  fields: {
    filters: { bind: "filters" }
  }
});
```

The `__verb__` macro defines the command metadata. The `__section__` defines typed parameters. The function body is the execution logic. The `require("minitrace")` module provides the host API for interacting with the loaded DuckDB connection.

This approach is called "scanner-first" because the command spec is extracted at scan time (before execution), not at runtime. The scanner reads the `__verb__` and `__section__` declarations and produces a `MinitraceCommandSpec` that looks identical to the SQL sqleton preamble. The runtime then dispatches to either SQL rendering or JS execution based on a `CommandRuntimeKind` field.

## The Catalog System

The catalog is the heart of the structured query commands feature. It loads command sources from embedded and external repositories, compiles them into `MinitraceCommand` instances, and makes them available to both the CLI and the web UI.

### Source Kinds

The `source_kind.go` file defines the source detection:

```go
type SourceKind int

const (
    SourceUnknown SourceKind = iota
    SourceSQLCommand
    SourceJSCommand
    SourceYAMLAlias
)

func DetectSourceKind(path string) SourceKind {
    lower := strings.ToLower(path)
    switch {
    case strings.HasSuffix(lower, ".alias.yaml"), strings.HasSuffix(lower, ".alias.yml"):
        return SourceYAMLAlias
    case strings.HasSuffix(lower, ".sql"):
        return SourceSQLCommand
    case strings.HasSuffix(lower, ".js"), strings.HasSuffix(lower, ".cjs"):
        return SourceJSCommand
    default:
        return SourceUnknown
    }
}
```

The catalog walks each source root and routes files to the appropriate parser based on extension. Alias files (`.alias.yaml`) can wrap any previously-loaded command to provide prefilled defaults.

### Loading and Compilation

The `LoadCatalog` function walks each source root, detects source kinds, parses specs, and compiles them into commands:

```go
func LoadCatalog(roots []SourceRoot) (*Catalog, error) {
    compiler := &Compiler{}
    catalog := &Catalog{
        Commands:    []*MinitraceCommand{},
        ByPath:      map[string]*MinitraceCommand{},
        ByName:      map[string]*MinitraceCommand{},
        SourceRoots: map[string]SourceRoot{},
    }

    for _, root := range roots {
        err := fs.WalkDir(root.FS, rootDir, func(path string, d fs.DirEntry, err error) error {
            kind := DetectSourceKind(path)
            parsed, err := parseSourceSpecs(path, rel, kind, contents)
            // compile and add to catalog
        })
    }

    if err := resolveAliases(catalog); err != nil {
        return nil, err
    }
    return catalog, nil
}
```

The catalog maintains three indexes: by full path, by command name, and by source root. Command paths are logical — a command at `overview/session-list.sql` becomes the CLI path `query commands overview session-list`.

### Repository Discovery

External repositories are discovered with clear precedence:

1. `--query-repository` flags (highest priority)
2. `GO_MINITRACE_QUERY_REPOSITORIES` environment variable
3. `queryRepositories` in app config
4. Embedded catalog (lowest priority)

Higher-priority repositories mount first so they can override embedded commands. This lets teams maintain their own query library without forking the embedded commands.

## The JS Command Runtime

The JS runtime is where the JavaScript execution happens. It bridges the minitrace catalog system with the goja JavaScript engine.

### The minitrace Module

The `minitrace` module is the host API exposed to JS command functions. It provides:

```javascript
// The module loaded via require("minitrace")
mt.query(sqlText, ...args)       // Execute a read-only SQL query
mt.queryOne(sqlText, ...args)    // Execute and return first row
mt.tableName                     // The loaded DuckDB table name
mt.runtime.tableName             // Runtime settings
mt.runtime.dbPath               // Database path
mt.runtime.archiveGlob          // Archive glob pattern
mt.sql.string(value)            // Safe SQL string escaping
mt.sql.stringIn(array)          // Safe SQL IN list
mt.sql.like(value)              // Safe SQL LIKE pattern
```

The module is loaded per-command with the DuckDB connection injected at invocation time:

```go
func minitraceModuleLoader(
    ctx context.Context,
    conn *sql.Conn,
    command *MinitraceCommand,
    runtimeSettings *MinitraceQueryRuntimeSettings,
) noderequire.ModuleLoader {
    return func(vm *goja.Runtime, moduleObj *goja.Object) {
        exports := moduleObj.Get("exports").(*goja.Object)
        _ = exports.Set("query", func(sqlText string, args ...any) ([]map[string]any, error) {
            return minitraceQuery(ctx, conn, sqlText, args...)
        })
        _ = exports.Set("queryOne", func(sqlText string, args ...any) (map[string]any, error) {
            rows, err := minitraceQuery(ctx, conn, sqlText, args...)
            // return first row or nil
        })
        // ... expose tableName, runtime, sql helpers
    }
}
```

### Error Handling

JS commands can fail in two ways: by throwing a synchronous error or by returning a rejected Promise. Both paths must be handled:

```javascript
// Synchronous throw
function sessionList() {
  throw new Error("boom");
}

// Async rejection
function sessionList() {
  return Promise.reject(new Error("promise boom"));
}
```

The runtime uses goja's Promise support to await async functions and surface both error types as Go errors:

```go
result, err := registry.InvokeInRuntime(ctx, runtime, verb, parsedValues)
if err != nil {
    return err  // surfaces both throw and reject
}
```

The tests explicitly verify both error paths:

```go
func TestMinitraceCatalogGlazeCommand_RunIntoGlazeProcessorReturnsThrownJSError(t *testing.T) {
    // verifies that throw new Error(...) surfaces as a Go error
}

func TestMinitraceCatalogGlazeCommand_RunIntoGlazeProcessorReturnsRejectedPromiseError(t *testing.T) {
    // verifies that Promise.reject(...) surfaces as a Go error
}
```

## The Command Runtime Dispatch

The `command_runtime.go` file changed significantly to support both SQL and JS execution:

```go
func (c *MinitraceCatalogGlazeCommand) RunIntoGlazeProcessor(...) error {
    // ... resolve command and values

    switch resolvedCommand.Runtime {
    case minitracecmd.CommandRuntimeSQL, minitracecmd.CommandRuntimeUnknown:
        sqlText, err := minitracecmd.RenderCommand(resolvedCommand, RenderContext{...})
        if err := queryengine.ValidateReadOnlyQuery(sqlText); err != nil {
            return err
        }
        return queryengine.RunIntoProcessor(ctx, conn, sqlText, gp)

    case minitracecmd.CommandRuntimeJS:
        return RunJSCommandIntoProcessor(ctx, c.catalog, resolvedCommand,
            runtimeSettings, vals, resolvedValues, conn, gp)

    default:
        return errors.Errorf("unsupported command runtime %q", resolvedCommand.Runtime)
    }
}
```

The `WithSchema` vs `WithFlags` split is important: JS commands use Glazed schemas (a newer typed parameter system) rather than the older flag-based system:

```go
if command.Schema != nil {
    options = append(options, cmds.WithSchema(command.Schema.Clone()))
} else {
    options = append(options, cmds.WithFlags(command.Flags...))
}
```

## Framework Metadata Preservation

The Claude Code adapter received a significant upgrade to preserve framework-specific metadata fields. Previously, fields like `entrypoint`, `slug`, `parent_uuid`, and `is_sidechain` were discarded during conversion. This PR captures them on turns and tool calls.

### The Metadata Functions

```go
func claudeTurnMetadata(record map[string]any, message map[string]any) any {
    metadata := map[string]any{}
    if entrypoint := stringValue(record["entrypoint"]); entrypoint != "" {
        metadata["entrypoint"] = entrypoint
    }
    if slug := stringValue(record["slug"]); slug != "" {
        metadata["slug"] = slug
    }
    if parentUUID, ok := record["parentUuid"]; ok {
        metadata["parent_uuid"] = parentUUID
    }
    if isSidechain, ok := record["isSidechain"]; ok {
        metadata["is_sidechain"] = isSidechain
    }
    if message != nil {
        if stopReason, ok := message["stop_reason"]; ok {
            metadata["stop_reason"] = stopReason
        }
        // ... cache_creation, stop_sequence
    }
    return metadata
}
```

The metadata flows onto turns via `turn.FrameworkMetadata = claudeTurnMetadata(...)` and onto tool calls via `toolCall.FrameworkMetadata = mergeMetadataMap(...)`. The `mergeMetadataMap` function handles the case where tool results already have metadata from the pending call:

```go
func mergeMetadataMap(existing any, fields map[string]any) any {
    metadata := map[string]any{}
    if current, ok := existing.(map[string]any); ok {
        for key, value := range current {
            metadata[key] = value
        }
    }
    for key, value := range fields {
        metadata[key] = value
    }
    return metadata
}
```

Framework config at the session level (like `entrypoint` on the session record) is stored in `session.OperationalContext.FrameworkConfig`.

## The Adapter Converter Tests

The PR added substantial test coverage for the adapter converters. The tests verify that metadata is preserved through the full conversion pipeline:

```go
func TestConvertRecordsPreservesClaudeFrameworkMetadata(t *testing.T) {
    records := []map[string]any{
        {
            "type":        "assistant",
            "timestamp":   "2026-03-29T10:00:10Z",
            "entrypoint":  "sdk-ts",
            "slug":        "curious-otter",
            "parentUuid":  "parent-1",
            "isSidechain": false,
            "message": map[string]any{
                "model":         "claude-opus-4-1",
                "stop_reason":   "tool_use",
                // ...
            },
        },
        // ...
    }

    session, err := ConvertRecords(records, "test-session", "/tmp/test")
    require.NoError(t, err)
    require.Len(t, session.Turns, 1)

    turn := session.Turns[0]
    require.NotNil(t, turn.FrameworkMetadata)

    metadata := turn.FrameworkMetadata.(map[string]any)
    assert.Equal(t, "sdk-ts", metadata["entrypoint"])
    assert.Equal(t, "curious-otter", metadata["slug"])
    assert.Equal(t, "parent-1", metadata["parent_uuid"])
}
```

Similar tests were added for the Codex and Pi adapters, covering the `ExitCode` and `Justification` fields that distinguish Codex exec sessions.

## The Nightly Review Workflow

The PR established a nightly transcript review workflow built from structured commands. The workflow is a pipeline that:

1. Discovers Pi and Codex sessions from the previous day
2. Converts them into a temporary minitrace archive
3. Runs a bundle of structured analysis commands against the archive
4. Renders the outputs into a markdown review document

### The Shell Orchestrator

The nightly review script orchestrates the whole pipeline:

```bash
#!/bin/bash
set -euo pipefail

DAY="${1:-$(date -d 'yesterday' +%Y-%m-%d)}"
OUTPUT_DIR="/tmp/nightly-review-run/$DAY"

# Pi discovery and conversion
go-minitrace discover pi --source-dir ~/.pi/agent/sessions --output json \
  | jq ".[] | select(.created_at | startswith(\"$DAY\"))" \
  > "$OUTPUT_DIR/pi-sources.json"

# ... similar for Codex

# Run the structured command bundle
go-minitrace query commands nightly session-inventory \
  --archive-glob "$OUTPUT_DIR/output/*/*.minitrace.json" \
  --day "$DAY" --output json > "$OUTPUT_DIR/report/session-inventory.json"

# Render to markdown
python scripts/render-nightly-report.py "$OUTPUT_DIR"
```

### The Structured Command Bundle

Five canonical structured commands now live under the `nightly` subverb:

- `nightly session-inventory` — list sessions grouped by workspace
- `nightly workspace-summary` — per-workspace aggregates (turn count, tool count, annotation count)
- `nightly tool-breakdown` — tool usage distribution
- `nightly followup-candidates` — sessions with unresolved annotations
- `nightly annotation-summary` — annotation counts by status

These commands use `sqlDate` and `sqlDateTime` helpers to work with date-typed parameters:

```sql
/* sqleton
name: session-inventory
short: Session inventory for a given day
flags:
  - name: day
    type: date
*/
SELECT
    operational_context->>'working_directory' AS workspace,
    COUNT(*) AS session_count,
    COUNT(DISTINCT framework) AS framework_count,
    MIN(created_at) AS first_session,
    MAX(created_at) AS last_session
FROM {{TABLE_NAME}}
WHERE DATE(created_at) = DATE('{{day}}', 'localtime')
GROUP BY operational_context->>'working_directory'
ORDER BY session_count DESC
```

### The Render Pipeline

The render pipeline uses clay's SQL template helpers (`sqlDate`, `sqlDateTime`, `sqliteDate`, `sqliteDateTime`) for date formatting. The sharp edge was that clay's default string helpers differ from the safer local versions the nightly workflow was using — a direct switch exposed unescaped LIKE values and malformed IN lists.

The fix was selective reuse: keep clay's date helpers, override the string helpers locally:

```go
// In render.go, using clay's CreateTemplate but with local overrides:
func RenderCommand(cmd *MinitraceCommand, ctx RenderContext) (string, error) {
    template, err := sql.CreateTemplate(cmd.Query,
        sql.WithFuncs(localStringHelpers),  // safe overrides
        sql.WithFuncs(clayDateHelpers),     // borrowed from clay
    )
    // ...
}
```

## The Structured Query Commands Help Page

The PR added a durable Glazed help page (`pkg/doc/structured-query-commands.md`) that explains the structured commands system. This is important because the feature is non-obvious — users need to understand that repository subdirectories become CLI groups, that JS commands add an extra nesting level, and that alias files can wrap any command with prefilled defaults.

Key points the help page covers:

- The command path mapping: `pkg/minitracecmd/core/overview/session-list.sql` → `go-minitrace query commands overview session-list`
- How JS commands add a file-stem group level: `overview/session-tools.js` with `name: session-list` → `go-minitrace query commands overview session-tools session-list`
- Repository discovery precedence and the `--query-repository` flag
- The three source kinds: SQL, JS, and YAML alias
- Example repository layouts

## Key Implementation Files

| File | Purpose |
|------|---------|
| `pkg/minitracecmd/source_kind.go` | Source kind detection (SQL, JS, YAML) |
| `pkg/minitracecmd/catalog.go` | Catalog loading, compilation, and indexing |
| `pkg/minitracecmd/types.go` | Command spec types and validation |
| `pkg/minitracecmd/parse_javascript.go` | JS command spec extraction from `__verb__` and `__section__` |
| `cmd/go-minitrace/cmds/query/js_runtime.go` | JS command execution via goja |
| `cmd/go-minitrace/cmds/query/command_runtime.go` | Runtime dispatch (SQL vs JS) |
| `cmd/go-minitrace/cmds/query/command_runtime_js_test.go` | JS runtime integration tests |
| `pkg/adapters/claudecode/convert.go` | Framework metadata preservation |
| `pkg/adapters/claudecode/convert_test.go` | Claude adapter tests |
| `pkg/minitracecmd/core/nightly/*.sql` | Nightly review structured commands |
| `pkg/doc/structured-query-commands.md` | Durable help page |

## Open Questions

- **Text output mode** — JS commands can currently only emit row-based output. Text-mode commands (for printing summary text) are explicitly rejected: `if strings.TrimSpace(command.JS.OutputMode) == jsverbs.OutputModeText { return fmt.Errorf("js text output mode is not supported") }`. This is a deferred feature.

- **DuckDB build conflict** — The full CLI binary build fails with multiple definition errors from DuckDB's static library when combined with certain linker flags. Package-level tests (`go test ./pkg/minitracecmd`) pass, but the full binary requires further dependency alignment.

- **Multi-run guideline linking** — In the annotation UI, batch review with guideline linking across multiple runs is intentionally rejected. The same concern applies here: should the nightly workflow support cross-framework analysis commands, or should it remain framework-scoped?

## Near-Term Next Steps

- Enable text output mode for JS commands
- Fix the DuckDB build conflict to support `go build` of the full binary
- Add JS command examples to the embedded catalog
- Extend the nightly workflow with more analysis dimensions (token usage, cache hit rates)
- Add Storybook/MSW coverage for the web UI command forms

## Related Notes

- [[PROJ - go-minitrace]] — parent project note
- `pkg/doc/structured-query-commands.md` — the durable help page
- `pkg/doc/nightly-review-playbook.md` — the review workflow documentation
