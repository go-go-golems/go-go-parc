---
title: "KB Batch 15 — Codebase Browser and Docs-as-Product"
aliases:
  - KB-BATCH15-codebase-browser-docs-product
  - Batch L Codebase Browser docs product
status: active
type: kb-review
created: 2026-05-11
tags: [knowledge-base, kb-review, codebase-browser, glazed, documentation, spa, sqlite]
---

# KB Batch 15 — Codebase Browser and Docs-as-Product

## Scope

Batch L reviewed the Codebase Browser / docs-as-product cluster:

1. [[PROJ - Codebase Browser - Embedded Go+TS Doc Server with Live Source Snippets]]
2. [[PROJ - Codebase Browser - Static Analysis and Dagger Pipeline]]
3. [[PROJ - Codebase Browser - Static WASM Build and SQLite Prototype]]
4. [[PROJ - Glazed Help Export and External Serve Sources - Technical Project Report]]

## Main conclusion

The cluster has one strong Tribal pattern: **documentation products should keep one canonical documentation/index/help model and project it into multiple delivery modes**. Live server, static export, embedded SPA, SQLite snapshot, and external-source serving should not become separate documentation stacks.

That pattern is now documented as:

- [[Tribal/canonical-doc-model-across-delivery-modes]]

## Written

### Tribal/canonical-doc-model-across-delivery-modes

Created [[Tribal/canonical-doc-model-across-delivery-modes]].

The entry consolidates recurring docs/product decisions from Glazed and Codebase Browser:

- Codebase Browser has one `Index` model for packages, files, symbols, refs, source ranges, docs, and snippets.
- Glazed Help has one `model.Section` / help-store model for terminal help, serve, export, imports, and snapshots.
- Static export should be a projection of the same model, not a second help stack.
- Embedded SPAs should render the model rather than define the model.
- SQLite is appropriate when documentation/index data becomes relational and queryable.
- Exported JSON/files/SQLite become data contracts, not just pretty output.

## Could / should be written later

### Go CLI with embedded SPA

Status: **5/5 — ready.**

Seen in:

- Glazed Serve
- Glazed Static Help Export
- Codebase Browser embedded server
- Codebase Browser static build
- Glazed Help Export / serve browser

This is now ready for an On-Ramp unless we decide it is already covered well enough by existing Go/web embed playbooks and skills. The likely angle is not generic `embed.FS`, but the 10-minute orientation for a newcomer reading reports about single-binary Go CLIs that serve a React/Vite SPA, optionally also producing static snapshots.

### Dagger-orchestrated Node tooling from Go

Status: **2/5.**

The Codebase Browser reports show a strong build pattern: Go orchestrates a Dagger `node:22` container, uses a CacheVolume-backed pnpm store, and provides a local fallback. This may become an On-Ramp if more Go projects need build-time Node/TS tooling without runtime Node.

### TypeScript Compiler API for code intelligence

Status: **2/5.**

The Codebase Browser indexer reports show enough scar tissue to seed an On-Ramp later: `TypeChecker`, alias symbols, declaration maps, ref extraction, JSX/generic ambiguity, and stable IDs.

## Updated / reinforced

- [[On-Ramp/wasm-from-go]] — reinforced by Codebase Browser's static WASM/TinyGo path.
- [[Tribal/canonical-doc-model-across-delivery-modes]] — new central entry for Glazed/Codebase Browser docs-as-product patterns.

## New candidates

### Tribal candidates

| Concept | Seen in | Status |
|---|---|---|
| Stable symbol IDs as documentation contract | Codebase Browser embedded server | 1/3 |
| Schema-first multi-language code index | Codebase Browser embedded server, Codebase Browser static analysis drill-down | 2/3 |
| Dagger/local build paths must produce byte-identical artifacts | Codebase Browser static analysis drill-down | 1/3 |
| Documentation export as subsystem contract | Glazed Help Export | 1/3 |
| External documentation sources as loaders into canonical store | Glazed Help Export | 1/3 |
| Unsafe slugs become security-sensitive when exported as files | Glazed Help Export | 1/3 |

### On-Ramp candidates

| Concept | Seen in | Status |
|---|---|---|
| Go CLI with embedded SPA | Glazed Serve, Glazed Static Help Export, Codebase Browser embedded server, Codebase Browser static build, Glazed Help Export | 5/5 — ready |
| Dagger-orchestrated Node tooling from Go | Codebase Browser embedded server, static analysis drill-down | 2/5 |
| TypeScript Compiler API for code intelligence | Codebase Browser embedded server, static analysis drill-down | 2/5 |
| SQLite as documentation snapshot format | Glazed Help Export | 1/5 |
| Static browser artifact with HashRouter/file delivery | Codebase Browser static build | 1/5 |

## Project report updates

Added `## KB reviews` and `## Related KB entries` links to all four Batch L project reports. Each links back to this review and to [[Tribal/canonical-doc-model-across-delivery-modes]].

## Index updates

Updated [[00-project-index-repos-and-concepts]] with analysis slots 76–79 and advanced campaign counts to:

- analyzed: 79
- remaining: 88
- Tribal entries: 22
- On-Ramp entries: 18
- Fundamentals: 5

## Notes for future review

The strongest next write from this cluster is probably the On-Ramp `Go CLI with embedded SPA`. It should orient a reader to `embed.FS`, Vite/React build artifacts, Go API/static serving, SPA fallback routing, static export variants, and why the frontend should sit over a stable backend model rather than define it.
