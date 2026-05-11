---
title: "SQL as First-Class Command Source — How We Do It"
aliases:
  - SQL as command source
  - SQL command files
  - sqleton format
  - SQL-first commands
tags: [knowledge-base, tribal, sql, glazed, cli, commands, duckdb]
status: active
type: knowledge-base
created: "2026-05-11"
---

# SQL as First-Class Command Source — How We Do It

> [!summary]
> SQL is not just a query language — it's a command definition format. We write `.sql` files with structured YAML metadata preambles, then compile them into Glazed CLI verbs, HTTP API endpoints, and UI forms. The SQL is the source of truth; the command infrastructure is generated. Two projects converged on this independently: Sqleton (origin) and Minitrace Query Commands (adoption).

## The pattern

A SQL command file has two parts: a machine-parseable metadata header and a human-readable SQL body. The header declares the command's name, description, flags, and arguments using the same field-definition system that Glazed uses everywhere. The body is a parameterized SQL template with safe helper functions for value injection.

```sql
/* sqleton
name: session-list
short: List minitrace sessions
flags:
  - name: framework
    type: stringList
    help: Filter by agent framework
  - name: limit
    type: int
    default: 100
    help: Limit the number of rows returned
*/
SELECT
  id,
  environment->>'agent_framework' AS framework,
  title
FROM {{TABLE_NAME}}
WHERE 1=1
{{ if .framework -}}
AND (environment->>'agent_framework') IN ({{ .framework | sqlStringIn }})
{{ end -}}
ORDER BY timing->>'started_at' DESC
LIMIT {{ .limit }};
```

The compilation pipeline is:

```
.sql file  →  split preamble  →  parse YAML metadata  →  validate spec
         →  compile to MinitraceCommand  →  Glazed CLI verb / HTTP endpoint / UI form
```

At execution time, the runtime resolves flag values, renders the SQL template with safe helpers, validates the result is read-only, opens a DuckDB connection, and executes. The output flows through Glazed's standard output processor (table, JSON, CSV, etc.).

## Why we do it this way

**SQL is the natural language for the problem domain.** Transcript analysis, database inspection, and data exploration are fundamentally SQL-shaped. Writing a Go function that builds a SQL query is indirection without benefit — the author already thinks in SQL, and the reader already reads SQL. Making SQL the source eliminates the translation layer.

**Metadata makes SQL discoverable.** A plain `.sql` file is an opaque string. Adding a structured preamble turns it into a named, documented, parameterized command that can be listed, searched, and rendered as a UI form. The preamble is what makes SQL a *command* instead of a *script*.

**The same format serves CLI, API, and UI.** Once a SQL file is compiled into a `MinitraceCommand` with `[]*fields.Definition`, the same type drives:
- a Cobra CLI verb with Glazed flags and output formatting
- an HTTP API endpoint with protobuf transport
- a UI form with dynamic parameter inputs and SQL preview

No adapters, no separate schema definitions, no drift between surfaces.

**Aliases provide lightweight specialization.** An `.alias.yaml` file references a parent command and pre-applies specific flag values:

```yaml
name: codex-framework-summary
short: Summarize only codex sessions
aliasFor: framework-summary
flags:
  framework:
    - codex
```

This lets teams customize shared commands without forking the SQL.

**Repositories compose with first-root-wins precedence.** Commands are loaded from multiple directory roots. If two roots contain a command at the same relative path, the first root wins. This lets teams override embedded commands by placing a file at the same path in an earlier repository.

Alternatives we considered:
- **Go functions that build SQL.** The Sqleton 1.0 approach. Works but creates a translation layer between the author's SQL intent and the Go code's SQL output. Hard to inspect, hard to review, hard to let non-Go-programmers contribute commands.
- **Stored procedures.** Database-side commands. Ties the command catalog to a running database instance. Can't be version-controlled in Git. Can't generate CLI/API/UI surfaces.
- **YAML-encapsulated SQL.** The older Sqleton format put SQL inside a YAML `query:` field. This inverted the natural reading order — you had to scroll past the metadata to find the SQL. The SQL-first preamble format puts the SQL where it belongs: at the top, readable, editable, reviewable.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `go-go-golems/sqleton` | `pkg/commands/`, `pkg/cmds/` | Origin: SQL command parsing, compilation, execution |
| `corporate-headquarters/go-minitrace` | `pkg/minitracecmd/` | Adoption: same format, adds catalog/repo/alias, CLI + API + UI |

### Related PARC project reports

- [[PROJ - Sqleton SQL Command Cleanup - Technical Project Report]] — origin: SQL-first format, app/command config separation, alias support
- [[PROJ - Minitrace Query Commands - Sqleton-Inspired SQL Verb System]] — adoption: catalog, multi-root repositories, CLI/API/UI integration

## Common mistakes

1. **Building SQL by string concatenation instead of template rendering.** The temptation is to interpolate flag values directly into SQL strings: `"WHERE framework = '" + framework + "'"`. This is SQL injection. The template helpers (`sqlString`, `sqlStringIn`, `sqlIntIn`, `sqlLike`) exist specifically to escape values. Always use the helpers. Never concatenate.

2. **Writing a command that mutates data.** The compilation pipeline validates that rendered SQL is a read-only query (SELECT, WITH, EXPLAIN, SHOW). If you write a command that contains INSERT, UPDATE, DELETE, or DROP, validation rejects it. This is deliberate: these commands are for inspection and analysis, not for data modification. If you need mutation, write a separate tool with different safety guards.

3. **Omitting the `/* sqleton */` preamble.** A plain `.sql` file without a preamble is silently skipped by the scanner. This is correct behavior — not every SQL file in a repository is a command. But if you wonder why your new command doesn't appear in the catalog, check that the preamble starts with `/* sqleton` (not `/* sql` or `/* command`).

4. **Forgetting `missingkey=zero` in the template engine.** The Go template engine defaults to `missingkey=error`, which panics if a referenced key is missing in the values map. Our rendering uses `missingkey=zero` so that omitted optional flags produce empty output instead of template errors. If you change the template options, every optional flag becomes a crash risk.

5. **Not normalizing optional bool flags.** In Go templates, an omitted boolean value renders as `<no value>` — not `false`. This produces broken SQL like `WHERE is_active = <no value>`. The compiler normalizes optional bool flags to `false` at compilation time, so `{{ .only_active }}` renders as `false`. If you bypass the compiler and render templates directly, you lose this normalization.

6. **Putting command-specific config in the app config.** The Sqleton cleanup separated app config (database connection, output format) from command config (SQL files, aliases). If you put command-specific settings (like a default `limit` value) in the app config instead of the command preamble, the command can't be shared across apps with different defaults. Command metadata lives in the command file; app config lives in the app.

7. **Making aliases that change the parent command's behavior.** An alias should only pre-apply flag values, not change the SQL or the parameter definitions. If an alias needs different SQL, it should be a separate command, not an alias. Aliases are for specialization (same query, narrowed scope), not for divergence (different query, same name).

## Variations

- **Sqleton standalone** (Sqleton). SQL commands as Glazed CLI verbs. Execution against PostgreSQL or SQLite. Direct CLI use, no web UI. The origin of the format.

- **Minitrace catalog** (Minitrace Query Commands). SQL commands against DuckDB-loaded minitrace archives. Multi-root repository discovery. CLI subgroup + v2 HTTP API + web UI form integration. Protobuf transport schema. The most complete implementation of the pattern.

- **Embedded-only commands** (Minitrace default). The embedded command set (`session-list`, `framework-summary`, `timing-analysis`) ships inside the binary via Go's `embed.FS`. No external repository needed for basic use. External repositories extend the catalog.

- **SQL-first with DSL preamble** (jsverbs, non-SQL instance). The same structural pattern — declarative metadata preamble + executable body — appears in jsverbs, where JavaScript files carry `__verb__` and `__package__` sentinel calls instead of SQL. See [[Tribal/dsl-normalized-config-compiled-plan]] for the general pipeline pattern.
