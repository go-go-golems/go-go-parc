---
title: "Playbook: Static Browser Code Indexes with TinyGo and SQLite"
aliases:
  - Static Browser Code Indexes
  - TinyGo SQLite Browser Playbook
  - Browser Code Index Playbook
tags:
  - article
  - playbook
  - go
  - wasm
  - sqlite
  - browser
  - architecture
  - tinygo
  - sqljs
status: active
type: article
created: 2026-04-23
repo: /home/manuel/code/wesen/2026-04-19--go-codebase-browser
---

# Playbook: Static Browser Code Indexes with TinyGo and SQLite

This is a practical playbook for turning a code browser from a server-backed application into a static browser artifact, and then evolving that static artifact toward a SQLite-backed query model. The reference implementation is [[PROJ - Codebase Browser - Static WASM Build and SQLite Prototype|Codebase Browser — Static WASM Build and SQLite Prototype]], but the pattern itself is more general.

The basic idea is simple:

1. analyze source code at build time
2. ship the resulting index as data, not as a running service
3. let the browser answer queries locally
4. use SQLite when the query shape becomes relational enough to justify it

The difficult part is not the idea. The difficult part is keeping the user experience stable while the transport layer, storage layer, and query engine all change underneath.

> [!summary]
> This pattern is useful when a code browser or documentation browser has no need for live server state. It works especially well when the source tree is known ahead of time, the UI is already a React or Vite app, and the data you need naturally falls into packages, files, symbols, references, and docs.

## When to use this pattern

Use this pattern when all of the following are true:

- the codebase is indexed from source that already exists locally
- the query surface is mostly read-only
- the browser UI needs fast symbol lookup, source snippets, and cross references
- you want the result to run from a directory of files, not from a process
- you are willing to do more work at build time in exchange for less runtime machinery

This pattern is especially strong when you have a code browser, a documentation browser, or an internal knowledge browser whose primary operation is lookup rather than mutation.

Do **not** use this pattern when:

- the application depends on live user state or frequent writes
- the data source is remote and changes continuously
- you need a true multi-user database server
- the browser must work without any precomputation at all
- the query logic is so simple that a database would be unnecessary overhead

## The core design rule

The most important rule is this:

> **Move every deterministic transformation to build time unless the browser truly needs to do it at runtime.**

That rule sounds obvious, but it has a practical consequence. Many browser apps keep a server only because it is convenient to expose a handful of JSON endpoints. If the endpoints are purely derived from static source data, the server is probably just a delivery shim.

Once you recognize that, the architecture becomes easier to simplify.

## A good mental model

Think about the system in three layers:

1. **Source layer** — the codebase, markdown, docs, and metadata you want to browse
2. **Index layer** — a build artifact that normalizes the source into searchable records
3. **Query layer** — either a tiny WASM runtime or SQLite, depending on how rich the queries need to be

The browser should only see the query layer. It should not care whether the data came from a JSON file, a WASM module, a local SQLite database, or an embedded server.

That separation is what lets you refactor the backend without rewriting the UI.

## Architecture option A: static index + TinyGo WASM

The first useful step is usually a static index plus a browser-side WASM module.

### Why this step exists

A browser app often already has a stable UI. The problem is that the existing API contract assumes a server. TinyGo WASM gives you a way to keep the contract while changing the execution location.

In this model:

- the build produces a JSON index and any precomputed lookup tables
- a TinyGo module loads the JSON and exposes lookup functions to JavaScript
- the React UI keeps using the same conceptual API surface
- the transport changes from HTTP fetches to local function calls

### What this buys you

This stage is valuable because it proves several things at once:

- the app can run from `file://`
- the UI can survive without a server
- the browser can load and query project data locally
- the build pipeline is capable of producing a self-contained artifact

### What it costs you

This stage also reveals the costs of a custom runtime:

- you are maintaining a Go/WASM bridge
- you may need browser-specific runtime glue
- you often duplicate query logic in a form that SQLite already knows how to do
- you may end up with precomputed maps that are really just a database schema in disguise

That last point is the key. Once your JSON starts looking relational, the next step is probably SQLite.

## Architecture option B: SQLite as the query engine

SQLite is the natural next step when the data is shaped like a graph of related records.

A code index usually contains records like these:

- packages
- files
- symbols
- cross references
- docs
- snippets

That is not an arbitrary blob. It is a relational structure.

### Why SQLite is a good fit

SQLite gives you:

- tables with explicit columns
- joins between related records
- indexes for fast lookup
- full-text search with FTS5
- SQL as a stable, inspectable query language
- a file format that can be used by Go and by the browser

In practice, that means fewer special-purpose data structures and more declarative queries.

### The architectural benefit

The biggest benefit is not speed, although SQLite is usually fast enough.

The biggest benefit is that SQLite turns the code browser into a system you can reason about. Instead of asking, “How does this custom lookup function work?” you ask, “What query returns the answer?”

That is a better long-term maintenance story.

## Recommended schema shape

For a code browser, a minimal but expressive schema often looks like this:

- `packages`
- `files`
- `symbols`
- `refs`
- `docs` or `pages`
- optional `symbols_fts` for full-text search

A typical relationship layout looks like this:

```text
packages 1 ──< files
packages 1 ──< symbols
files    1 ──< symbols
symbols  1 ──< refs (from_id)
symbols  1 ──< refs (to_id)
files    1 ──< refs (location)
```

### What belongs in each table

**packages**
- package identifier
- import path
- display name
- language
- docs or summary text

**files**
- file identifier
- relative path
- package identifier
- line count
- byte size

**symbols**
- symbol identifier
- symbol kind
- name
- package identifier
- file identifier
- line or range information
- signature
- docs
- receiver type if relevant
- exported flag

**refs**
- reference identifier
- source symbol
- target symbol
- kind of reference
- file identifier
- line location

This layout is intentionally boring. Boring schemas are good schemas.

## Search design: FTS5 first, fallback second

If a code browser supports search, it should search more than one thing.

Useful search fields usually include:

- symbol name
- package path
- signature text
- doc comment text
- file path

SQLite FTS5 is a strong fit because it supports ranking and tokenization while keeping the search logic close to the data.

### The recommended approach

1. create the core relational tables
2. create an FTS5 virtual table over the text fields you want to search
3. keep the FTS table in sync with triggers or with explicit rebuilds
4. add a simple fallback query for environments where FTS5 is unavailable

The fallback matters because browser SQLite builds do not all expose the same extensions.

### Why the fallback matters

The browser is not always the same as the host machine. A host-side SQLite build may include FTS5, while a browser-side build may not. A portable design should be honest about that.

So the rule should be:

- prefer FTS5 when it exists
- fail gracefully when it does not
- keep the UI usable either way

## Transport design: keep the UI contract stable

This pattern works best when the UI does not know or care what backend sits behind it.

That means the browser-facing contract should stay conceptually the same even as the implementation changes.

For example, the UI may still ask for:

- the index summary
- search results
- a single symbol
- a source snippet
- a doc page
- cross references

The only thing that should change is how those answers are produced.

### Transport options

There are three common transport shapes:

1. **HTTP API** — the original server-backed model
2. **WASM function calls** — good for static, local lookup logic
3. **SQLite queries** — good when the data is relational and you want richer search

A healthy migration path often moves through all three.

## Build pipeline pattern

The build should be thought of as a data pipeline, not just a compilation step.

A practical pipeline looks like this:

1. index the source tree
2. normalize the output into a schema
3. precompute anything expensive or repetitive
4. package the data for the browser
5. bundle the browser app
6. verify the artifact in a real browser

### Why build-time work matters

Build-time work gives you:

- faster runtime performance
- less code in the browser
- fewer moving parts in production
- deterministic output
- easier debugging when something goes wrong

If a task can be done once during the build instead of every time a user opens the app, it usually should be.

## Browser delivery options

There are two common ways to ship the browser artifact.

### Option 1: static directory

Ship:

- `index.html`
- bundled JS/CSS assets
- source snapshot
- database or JSON index
- runtime support files such as `wasm_exec.js` or `sql.js`

This is the easiest model to understand and the easiest to share.

### Option 2: single-file browser entry plus supporting assets

Sometimes you can collapse more of the runtime into one entry point, but for code browsers it is usually not worth fighting the browser too hard. A clean static directory is better than a heroic single-file design.

## The implementation lessons that matter most

### 1. TinyGo is a bridge, not the destination

TinyGo is useful when you want Go logic in the browser. It is especially useful as a transition tool.

But if the browser is only performing data lookup, TinyGo should not become the permanent query engine unless it is really buying you something SQLite cannot.

### 2. SQLite is the destination when the data is relational

If the data model naturally contains joins, filters, and search fields, SQLite is a better final shape than a custom JSON lookup runtime.

### 3. Keep the frontend API stable

The best migrations preserve component structure.

The React app should keep rendering the same conceptual objects:

- packages
- files
- symbols
- xrefs
- docs

If you can preserve those interfaces, you can swap the engine beneath them without a UI rewrite.

### 4. Validate the result in a real browser

A static browser system is only real when it works in a browser.

Test the artifact with an actual browser session, not just with unit tests:

- page loads
- navigation works
- search works
- snippets render
- back/forward works
- console stays clean

If the app is meant to be opened from `file://`, test it that way.

## Common failure modes

### Missing or incorrect WASM runtime glue

If you use TinyGo, make sure the browser gets the matching runtime support file. Go and TinyGo are not interchangeable here.

### Browser routing assumptions

If your app uses clean URLs, it may accidentally depend on a server. Hash-based routing is often safer for static delivery.

### SQLite build differences

Not all SQLite builds have the same extensions. FTS5 may exist on the host and be missing in the browser build.

### Index shape drift

If the UI expects arrays but the backend returns counts, the app will fail in a way that looks like a frontend bug even though the real problem is the data contract.

### Overfitting the prototype

A prototype should validate the architecture, not become a permanent miniature copy of the production system.

## A practical migration checklist

If you are applying this pattern to a new project, work through the following list:

- define the data model in plain language
- identify which fields are relational
- decide what can be precomputed at build time
- preserve the frontend API shape
- choose either TinyGo lookup logic or SQLite as the runtime query engine
- add a browser test that opens the artifact locally
- test search and navigation before calling the project done
- document the failure modes while they are fresh

## Reference implementation

The reference implementation for this playbook is the Codebase Browser project:

- [[PROJ - Codebase Browser - Embedded Go+TS Doc Server with Live Source Snippets]]
- [[PROJ - Codebase Browser - Static WASM Build and SQLite Prototype]]

The first note documents the earlier server-based architecture. The second note documents the static WASM build and the SQLite direction. Read them together if you want the full story.

## Final rule of thumb

If your code browser is spending its runtime pretending to be a database, make it an actual database.

That is the central lesson of this pattern.
