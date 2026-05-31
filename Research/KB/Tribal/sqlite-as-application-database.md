---
title: "SQLite as Application Database in Go — How We Do It"
aliases:
  - sqlite go
  - go sqlite
  - sqlite as app db
  - go sqlite3
tags: [knowledge-base, tribal, sqlite, go, database, persistence]
status: active
type: knowledge-base
created: 2026-05-11
---

# SQLite as Application Database in Go — How We Do It

> [!summary]
> How we use SQLite as the primary database for Go services and tools: WAL mode for concurrent reads, `modernc.org/sqlite` for CGo-free builds, schema migrations embedded in the binary, and the discipline of treating SQLite as an application database (not a server database). The key insight: SQLite replaces both "a config file plus a separate database" and "a full Postgres deployment for a single-user tool."

## The pattern

SQLite is our default persistence layer for Go services that serve a single user or a small team. The database is a single file on disk. There is no server process, no connection string, no network. The Go binary opens the file, creates the schema if it doesn't exist, and closes it on shutdown. State survives restarts with zero operational effort.

The RAG Evaluation System extends this pattern with a **two-database architecture**: a corpus database for domain data (documents, chunks, embeddings) and an engine database for workflow orchestration state. See [[On-Ramp/rag-evaluation-pipeline-architecture]].

```go
// Open SQLite with WAL mode for concurrent reads
db, err := sql.Open("sqlite", "file:data/broker.db?_journal_mode=WAL&_busy_timeout=5000")
if err != nil {
    return fmt.Errorf("open database: %w", err)
}

// Run embedded migrations
for _, migration := range migrations {
    if _, err := db.Exec(migration.SQL); err != nil {
        return fmt.Errorf("migration %s: %w", migration.Name, err)
    }
}

// Connection pool settings — critical for WAL mode
db.SetMaxOpenConns(1) // Only 1 writer; readers can proceed concurrently
db.SetMaxIdleConns(2)
```

Three decisions that distinguish our approach from "just using SQLite":

1. **`modernc.org/sqlite` over `mattn/go-sqlite3`.** The `mattn` driver requires CGo, which breaks cross-compilation and WASM builds. The `modernc` driver is a pure Go translation of SQLite's C code. It compiles everywhere Go compiles. The tradeoff: ~2× slower for write-heavy workloads. For our use cases (single-user services, low write rates), this is irrelevant.

2. **WAL mode always.** The default journal mode (`DELETE`) uses a rollback journal that prevents concurrent readers while a write is in progress. WAL (Write-Ahead Log) mode allows readers and one writer to operate simultaneously. This matters because our services typically have a web UI polling for state while the backend processes requests.

3. **Schema migrations as Go code, not SQL files.** The migration list is a Go slice of structs, embedded in the binary. No external SQL files to lose, no migration tool to install, no "which version is this database at?" guessing. Each migration has a name and SQL; they run in order on startup.

## Why we do it this way

**SQLite replaces both config files and server databases.** Before we standardized on SQLite, our tools used a mix of YAML/JSON config files (no querying, no relations, no transactions) and Postgres (operational overhead for a single-user tool). SQLite gives us SQL, transactions, relations, and querying — in a single file that you can copy, back up with `cp`, and inspect with `sqlite3` CLI.

**No CGo means no build pain.** Cross-compiling from macOS to Linux, building WASM, deploying as a single binary — all of these break with CGo. The `modernc` driver eliminates this entirely. We've paid the performance cost and found it acceptable for every project we've built.

**Embedded migrations mean zero-configuration deployment.** The binary creates and upgrades its own database on first run. No `createdb`, no `psql -f schema.sql`, no migration runner. This is especially important for tools distributed to end users who should never need to know the database exists.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `2026-04-17--byok-host` | `internal/store/` | Broker persistence: users, connections, grants, tokens, audit |
| `corporate-headquarters/pinocchio` | `internal/store/` | Tool call history, session state |
| `corporate-headquarters/evtstream` | `internal/store/` | Event store, projections (testing) |

### Related PARC project reports

- [[PROJ - BYOK Host - Project Report]] — SQLite as the sole persistence layer for a Keycloak-integrated broker
- [[ARTICLE - SQLite Introspection - Exact Page-Level Size Analysis with Go and React]] — our SQLite size analysis tooling
- [[ARTICLE - Squeezing a SQLite Database From 32 MB to 1.4 MB - How We Found and Fixed 99 Pct Redundancy in Codebase-Browser]] — SQLite optimization case study

## Common mistakes

1. **More than one open writer connection.** SQLite allows one writer at a time. If you open two connections and both try to write, one gets `SQLITE_BUSY`. The fix: `db.SetMaxOpenConns(1)` for the writer, or use a dedicated writer connection plus separate reader connections. In WAL mode, readers don't block the writer and the writer doesn't block readers — but two writers still conflict.

2. **Missing `_busy_timeout` in the connection string.** Without it, a write conflict returns `SQLITE_BUSY` immediately. With `_busy_timeout=5000`, SQLite retries for 5 seconds before giving up. This is almost always what you want — the conflicting write will likely finish within milliseconds.

3. **Not running `PRAGMA journal_mode=WAL` on every connection.** WAL mode is persistent — it survives process restarts and database closes. But if you open a new connection without specifying WAL in the connection string, it opens in the default (DELETE) mode. Our convention: always specify `_journal_mode=WAL` in the connection string.

4. **Storing large blobs in SQLite.** SQLite handles blobs, but large blobs (images, PDFs) bloat the database file, make backups expensive, and prevent efficient page caching. Store large blobs on disk (a file per blob) and store the path in SQLite. The database stays small and fast.

5. **No schema version tracking.** If you run migrations on every startup without checking which ones have already been applied, you'll get "table already exists" errors on the second run. Track applied migrations in a `_migrations` table and skip already-applied ones.

## Variations

- **Postgres for multi-user services**: Wish Git uses Postgres instead of SQLite because it needs concurrent writers (multiple agents pushing simultaneously) and Postgres's row-level locking. The choice between SQLite and Postgres is: single-writer or multi-writer? For single-user tools and small-team services, SQLite. For multi-user services with concurrent writes, Postgres.

- **In-memory SQLite for testing**: `sql.Open("sqlite", ":memory:")` creates a database that exists only in the process's memory. It's perfect for tests: fast, isolated, no cleanup. But it doesn't survive across connections — each `sql.Open` creates a new database. Use `file:test.db?mode=memory&cache=shared` if you need multiple connections to the same in-memory database.
