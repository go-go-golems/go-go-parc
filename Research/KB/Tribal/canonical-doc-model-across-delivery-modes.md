---
title: "Canonical Documentation Model Across Delivery Modes — How We Do It"
aliases:
  - canonical docs model
  - docs as portable data model
  - shared documentation model across delivery modes
  - static and live docs from one model
tags: [knowledge-base, tribal, documentation, go, cli, spa, sqlite, static-site, glazed, codebase-browser]
status: active
type: knowledge-base
created: 2026-05-11
---

# Canonical Documentation Model Across Delivery Modes — How We Do It

Related on-ramp: [[On-Ramp/go-cli-with-embedded-spa]]

> [!summary]
> When a documentation product needs a live server, a static snapshot, an embedded SPA, exports, or external-source serving, we keep one canonical model underneath all delivery modes. The delivery surface changes; the documentation data contract does not.

## The pattern

Our documentation tools increasingly have more than one way to reach the same content:

- a Go binary serves an embedded React SPA;
- the same content is exported as static files;
- markdown pages embed live source snippets;
- help pages are exported as JSON, markdown files, or SQLite;
- a browser serves documentation from another binary's export;
- a codebase index shifts from JSON to SQLite without changing the UI's conceptual API.

The durable pattern is: **make documentation a structured data model first, then add delivery modes around that model.**

```text
source docs / source code / help sections
        ↓
canonical model or database
        ↓
server API    static export    SQLite snapshot    external loader    embedded SPA
```

The canonical model can be different per product. In Codebase Browser, it is the `Index` schema: packages, files, symbols, references, ranges, docs, and source snapshots. In Glazed Help, it is `model.Section` backed by the help store: title, slug, type, topics, commands, flags, metadata, and markdown content. The specific schema is less important than the invariant: every delivery path reads or writes the same model.

This prevents a common failure mode in documentation products: the live server, static export, CLI help, and browser all drift into separate implementations. Once that happens, a bug fix in one mode does not fix the others, and users start asking which version is authoritative.

## Why we do it this way

Documentation rots when it is copy-pasted across surfaces. It also rots when every surface invents its own representation.

The Codebase Browser began as a Go HTTP server over a build-time code index. It could serve packages, files, symbols, snippets, and cross-references. The static build later removed the runtime server, but it did not create a second documentation stack. It kept the same conceptual API and moved the data into a static artifact. The SQLite prototype pushes the same idea further: the codebase is relational, so the next canonical model should be a database that both Go and the browser can query.

Glazed Help reached the same pattern from the opposite direction. The help system already had structured sections in memory and a SQLite-backed store. `glaze help export` made that model portable as JSON, files, and SQLite. `glaze serve --from-*` then loaded those portable forms back into the same help system. The browser did not need to know whether the content came from embedded docs, another binary, JSON, SQLite, or local markdown; it still saw help sections.

This is not only a cleanliness rule. It changes what documentation can do. Once docs are data, they can be searched, exported, linted, diffed, loaded from multiple producers, served offline, queried with SQL, and validated in CI.

## Where it lives

### Codebase Browser

| Path | Role |
|---|---|
| `/home/manuel/code/wesen/2026-04-19--go-codebase-browser/internal/indexer/types.go` | Canonical Go schema for packages/files/symbols/refs. |
| `/home/manuel/code/wesen/2026-04-19--go-codebase-browser/tools/ts-indexer/src/types.ts` | TypeScript mirror of the index schema. |
| `/home/manuel/code/wesen/2026-04-19--go-codebase-browser/internal/indexer/multi.go` | Merges per-language indexes and detects duplicate IDs. |
| `/home/manuel/code/wesen/2026-04-19--go-codebase-browser/internal/server` | Live API over the canonical index. |
| `/home/manuel/code/wesen/2026-04-19--go-codebase-browser/internal/docs` | Markdown renderer that resolves `codebase-snippet` directives against the index/source snapshot. |
| `/home/manuel/code/wesen/2026-04-19--go-codebase-browser/ui` | React SPA that consumes package/symbol/xref/doc data without owning the index model. |
| `/home/manuel/code/wesen/2026-04-19--go-codebase-browser/ttmp/2026/04/23/GCB-007--sqlite-codebase-index-query-symbols-files-and-xrefs-with-sql` | SQLite migration design and prototype scripts. |

### Glazed Help

| Path | Role |
|---|---|
| `/home/manuel/code/wesen/corporate-headquarters/glazed/pkg/help/cmd/export.go` | `glaze help export` as JSON/files/SQLite over the existing help model. |
| `/home/manuel/code/wesen/corporate-headquarters/glazed/pkg/help/loader/sources.go` | External source loaders for markdown, JSON, SQLite, and other Glazed binaries. |
| `/home/manuel/code/wesen/corporate-headquarters/glazed/pkg/help/server/serve.go` | `glaze serve --from-json --from-sqlite --from-glazed-cmd --with-embedded`. |
| `/home/manuel/code/wesen/corporate-headquarters/glazed/pkg/help/cmd/cobra.go` | Auto-registers `help export` at the standard help-system boundary. |
| `/home/manuel/code/wesen/corporate-headquarters/glazed/pkg/doc/topics/28-export-help-entries.md` | User documentation for export. |
| `/home/manuel/code/wesen/corporate-headquarters/glazed/pkg/doc/topics/29-serve-external-help-sources.md` | User documentation for external help sources. |

### Related PARC project reports

- [[PROJ - Glazed Serve - Help Browser, Embedded Docs, and SPA]] — embedded SPA over the canonical Glazed help model.
- [[PROJ - Glazed Static Help Export - render-site and Static Snapshot Publishing]] — static delivery as another view of the same help system.
- [[PROJ - Codebase Browser - Embedded Go+TS Doc Server with Live Source Snippets]] — schema-shared code index, embedded source snapshot, live snippets, and self-hosted docs.
- [[PROJ - Codebase Browser - Static Analysis and Dagger Pipeline]] — schema-first multi-language extraction and Dagger-scoped build-time TS tooling.
- [[PROJ - Codebase Browser - Static WASM Build and SQLite Prototype]] — static delivery and SQLite migration path for the codebase index.
- [[PROJ - Glazed Help Export and External Serve Sources - Technical Project Report]] — portable help export/import protocol around the Glazed help store.

## Common mistakes

### Building a second documentation stack for static export

The mistake is to treat static export as a separate product: separate routes, separate data shape, separate renderer, separate search, separate docs. That works for the first demo and then drifts immediately.

The Glazed Static Help Export project avoided this by making static export another delivery mode for the same help sections. Codebase Browser followed the same direction: the static build changed the transport, not the conceptual model the UI asks for.

### Letting frontend components own the data model

A React component should not be the authoritative definition of a help section, symbol, cross-reference, or doc page. It should render a model that exists independently.

This matters in Codebase Browser because the same symbol model feeds server endpoints, snippets, search, xrefs, and the frontend. If the UI had invented a separate symbol shape for convenience, the TS extractor, Go extractor, and doc renderer would have had to translate through a moving target.

### Treating exports as pretty output instead of data contracts

`glaze help export --output json` is not just a nice CLI feature. Once users save that JSON and `glaze serve --from-json` accepts it, the row shape becomes a data contract. The importer must accept real exported shapes, not only idealized structs. Invalid fields should fail clearly, and historical variants should be accepted when practical.

The Glazed project hardened this after review: invalid section types now fail loudly, and JSON import accepts both `type` and `section_type` variants where the meaning is clear.

### Using user-derived slugs as paths without validation

File export turns documentation identity into filesystem paths. A slug that was harmless as a database key becomes dangerous when it becomes a filename.

The Glazed export project added `safeSectionFilePath` because slugs like `..`, `foo/bar`, or path-traversal variants should not escape the export directory. Any documentation export command that writes files needs the same paranoia.

### Hiding stale snippets through copy-paste

The Codebase Browser exists largely to avoid copied source snippets in markdown. `codebase-snippet sym=...` directives resolve against the embedded index and source snapshot at render time. If the symbol disappears, the page should fail loudly. A copied snippet would keep rendering and lie.

The pattern is not “never show code in docs.” The pattern is “reference code by stable identity when the doc claims to show live source.”

### Letting build-time toolchains become runtime dependencies

The Codebase Browser TypeScript extractor needs Node and the TS Compiler API. The browser runtime does not. Dagger keeps the Node toolchain scoped to build time, and the final product can still be a Go binary or static artifact.

This distinction is important for documentation products. Build-time richness is allowed; runtime distribution should stay simple.

### Migrating to SQLite while keeping JSON-shaped thinking

The Codebase Browser SQLite prototype matters because the index is naturally relational. Packages contain files, files contain symbols, symbols reference symbols, and search wants ranking. If the project adopts SQLite but continues to treat it as a blob store for JSON-ish records, it misses the point.

The working rule from the project is: if a future change can be expressed as a SQL query, it probably should be.

## Variations

### Live server

A live server is useful during development or when content is loaded from local files, external binaries, or dynamically selected sources. Glazed `serve` and the original Codebase Browser server both fit here.

The server should still read from the canonical model. It should not create an independent runtime-only model.

### Static snapshot

A static snapshot is best when all content is known at build time and the goal is distribution. The Codebase Browser static build and Glazed static export both use this shape.

The key invariant is that static export is a projection of the same model, not a fork.

### Portable exchange format

JSON, markdown files, and SQLite exports are exchange formats. They are useful when another process, browser, or archive needs to consume docs without linking to the producer's internals.

The exchange format should be complete by default. Metadata-only export is useful for inventories, but the default should preserve enough content to reconstruct or serve the docs later.

### SQLite as canonical model

SQLite is appropriate when the data is relational and users want ad-hoc queries, FTS, joins, or browser-side querying. It is a stronger model than a JSON blob when search and analysis become product features.

Use SQLite when it simplifies the questions users ask. Do not add it merely because a database sounds more serious.

### Embedded SPA

An embedded SPA is a distribution strategy: one Go binary can ship the browser, the API, and the data snapshot. It works when the frontend is a view over a stable backend model.

If the SPA starts defining product semantics that the CLI/server/export paths do not share, the system has split and should be pulled back to the canonical model.
