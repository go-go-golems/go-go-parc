# Data / RAG / OCR / Search Scout Report

## Scope and search method

Scope: Markdown project/report corpus under `Projects/2026/{03,04,05,06}/`, focused on data systems, RAG evaluation, OCR/book workflows, SQLite/Bleve/FAISS, codebase browser/indexing, Readwise, document co-read, corpus pipelines, search/reranking, data export/import, and knowledge-base workflows.

Method: targeted filename inventory plus keyword search for `rag`, `retriev`, `rerank`, `embedding`, `faiss`, `bleve`, `sqlite`, `fts`, `ocr`, `readwise`, `knowledge`, `corpus`, `index`, `search`, `co-read`, `document`, `export`, `import`. I then selectively read high-signal reports rather than the full 554-file corpus.

## Files retrieved

1. `Projects/2026/05/27/ARTICLE - RAG Evaluation System - Workflow-Driven Retrieval Evaluation.md` (lines 1-160) - main RAG evaluation architecture, DB/service/API/frontend layers, early status and missing pieces.
2. `Projects/2026/05/28/ARTICLE - RAG Evaluation System - Building a Database-Backed TTC Corpus Pipeline.md` (lines 1-110) - WordPress/WooCommerce MySQL dump to normalized SQLite corpus pipeline.
3. `Projects/2026/05/28/ARTICLE - RAG Evaluation System - Search Retrieval Foundation Deep Dive.md` (lines 1-100) - BM25/vector/hybrid retrieval stack and search service entry points.
4. `Projects/2026/05/28/ARTICLE - RAG Evaluation System - Corpus Explorer and Pipeline Visualization Website.md` (lines 1-80) - corpus explorer UI and corpus counts.
5. `Projects/2026/05/29/ARTICLE - RAG Evaluation - Workflow Intake UI Architecture and Data Exploration.md` (lines 1-80) - two-SQLite workflow/domain DB architecture.
6. `Projects/2026/06/07/ARTICLE - RAG Evaluation System - Frontend Architecture and Context Viewer Integration.md` (lines 1-80) - later frontend/component architecture around context viewer.
7. `Projects/2026/06/03/ARTICLE - Exporting WordPress WooCommerce Data into a RAG SQLite Corpus.md` (lines 1-90) - compact RAG-facing SQLite export and validation pipeline.
8. `Projects/2026/06/03/ARTICLE - Goja Bleve - Native Search Bindings for JavaScript RAG Pipelines.md` (lines 1-80) - Goja native Bleve bindings and typed wrapper model.
9. `Projects/2026/06/02/ARTICLE - Building FAISS for Bleve Vector Search.md` (lines 1-70) - FAISS/Bleve vector build constraints and failure modes.
10. `Projects/2026/06/06/ARTICLE - Goja Bleve - Shipping a Vector RAG Runtime with xgoja.md` (lines 1-100) - generated xgoja vector runtime, Geppetto embedding integration, FAISS build metadata.
11. `Projects/2026/05/20/ARTICLE - VLM OCR Pipeline for Scanned PDFs.md` (lines 1-75) - VLM OCR over scanned PDFs with SQLite work queue.
12. `Projects/2026/05/24/ARTICLE - Book OCR Quality Lab - Baseline Runs SQLite Log Filtering and Experiment Provenance.md` (lines 1-90) - OCR experiment provenance and quality loop.
13. `Projects/2026/05/26/ARTICLE - Book OCR Project Report - Structured Workflow Runtime and Manual PDF Repair.md` (lines 1-75) - productionized book OCR workflow runtime and repair loop.
14. `Projects/2026/04/20/PROJ - Codebase Browser - Static Analysis and Dagger Pipeline.md` (lines 1-80) - multi-language static index extraction and Dagger build pipeline.
15. `Projects/2026/04/23/PROJ - Codebase Browser - Static WASM Build and SQLite Prototype.md` (lines 1-90) - static browser and SQLite/FTS migration path.
16. `Projects/2026/05/21/PROJ - Readwise Viewer.md` (lines 1-80) - SQLite-backed Readwise workbench with planned Bleve/embeddings.
17. `Projects/2026/05/13/PROJECT REPORT - Document Co-Read Observatory - Transcript Mining to Recommender Workbench.md` (lines 1-90) - transcript-derived document graph/recommender using go-minitrace and DuckDB.
18. `Projects/2026/03/21/PROJ - DOM Scraping Experiment - Web to Markdown via JS DOM Queries.md` (grep hits around lines 32-81, 272-350) - web-to-Markdown extraction pipeline and reproducible numbered scripts.
19. `Projects/2026/03/23/PROJ - CozoDB Editor - Merge Resolution, SQLite Preset, and Editor Highlighting.md` (grep hits around lines 22-121, 134-197) - notebook/runtime architecture grows a SQLite preset and CodeMirror SQL editor.

## Projects and reports found

### RAG evaluation system / TTC corpus / retrieval

Core arc:

- `Projects/2026/05/27/ARTICLE - RAG Evaluation System - Workflow-Driven Retrieval Evaluation.md`
- `Projects/2026/05/28/ARTICLE - RAG Evaluation System - Building a Database-Backed TTC Corpus Pipeline.md`
- `Projects/2026/05/28/ARTICLE - RAG Evaluation System - Search Retrieval Foundation Deep Dive.md`
- `Projects/2026/05/28/ARTICLE - RAG Evaluation System - Corpus Explorer and Pipeline Visualization Website.md`
- `Projects/2026/05/29/ARTICLE - RAG Evaluation - Workflow Intake UI Architecture and Data Exploration.md`
- `Projects/2026/05/30/PROJ - RAG Evaluation - Workflow Intake UI Implementation Report.md` (found by inventory; not deeply read)
- `Projects/2026/06/03/ARTICLE - Deep Dive - xgoja Scripting for RAG Evaluation Systems.md` (found by inventory)
- `Projects/2026/06/03/ARTICLE - Exporting WordPress WooCommerce Data into a RAG SQLite Corpus.md`
- `Projects/2026/06/07/ARTICLE - RAG Evaluation System - Frontend Architecture and Context Viewer Integration.md`

Key shape: a Go + SQLite + Glazed + HTTP + React system whose pipeline is `Source -> Document -> Chunk -> Embedding -> Search -> Evaluation`. SQLite is canonical; search indexes and workflow artifacts are derived/rebuildable.

High-signal details:

- Initial architecture stores sources, documents, chunks, chunking strategies, embeddings, search indexes, evaluation queries/runs/results; CLI and HTTP share domain services (`Projects/2026/05/27/...`, lines 24-43, 91-137).
- TTC corpus pipeline loads a compressed WordPress/WooCommerce MySQL dump, exports normalized SQLite, imports 3,096 documents, creates 255 chunks, computes a small OpenAI embedding sample (`Projects/2026/05/28/...TTC Corpus...`, lines 24-35).
- Retrieval foundation supports BM25, query-vector search over stored embeddings, and hybrid reciprocal-rank fusion; smoke tests are explicitly not benchmarks (`Projects/2026/05/28/...Search Retrieval...`, lines 24-41).
- Corpus explorer made 3,117 documents / 481 chunks / 35 embeddings visible via browser UI (`Projects/2026/05/28/...Corpus Explorer...`, lines 24-47).
- Workflow intake UI separates corpus DB (`data/rag-eval.db`) from engine DB (`state/rag-eval-workflows.db`) to avoid orchestration churn contending with corpus reads (`Projects/2026/05/29/...Workflow Intake UI...`, lines 24-76).
- Later frontend work introduces a layered component library and context-viewer vocabulary (`Projects/2026/06/07/...Frontend Architecture...`, lines 24-67).

### Bleve / FAISS / Goja / xgoja vector search

Reports:

- `Projects/2026/06/02/ARTICLE - Building FAISS for Bleve Vector Search.md`
- `Projects/2026/06/03/ARTICLE - Goja Bleve - Native Search Bindings for JavaScript RAG Pipelines.md`
- `Projects/2026/06/06/ARTICLE - Goja Bleve - Shipping a Vector RAG Runtime with xgoja.md`
- `Projects/2026/06/03/ARTICLE - Goja Bleve - Native Search Bindings for JavaScript RAG Pipelines.md`
- `Projects/2026/06/06/xgoja env/*` (found by inventory; likely build/env flag follow-ups)

Key shape: `goja-bleve` exposes Bleve as `require("bleve")` for JavaScript RAG scripts. Normal builds are text-search capable; vector builds use `-tags=vectors` and FAISS via CGO.

High-signal details:

- FAISS support depends on Bleve's `vectors` build tag, `go-faiss`, `libfaiss_c.so`, `libfaiss.so`, and explicit `CGO_LDFLAGS` (`Projects/2026/06/02/...FAISS...`, lines 24-50).
- Goja binding uses fluent JS wrappers, but hidden Go refs (`__bleve_ref`) carry real Bleve mappings/queries/search requests (`Projects/2026/06/03/...Native Search Bindings...`, lines 24-70).
- Generated xgoja vector host composes `bleve`, `geppetto`, core helpers, host fs, and jsverbs, with build config captured in YAML including tags/ldflags/env (`Projects/2026/06/06/...Shipping...`, lines 24-90).
- Failure modes from review: reopened vector indexes need stored mapping, `.size(0)` must remain explicit, batch wrappers should become single-use only after successful execution (`Projects/2026/06/06/...Shipping...`, lines 24-35).

### Book OCR / scanned PDF workflows

Reports:

- `Projects/2026/05/20/ARTICLE - VLM OCR Pipeline for Scanned PDFs.md`
- `Projects/2026/05/24/ARTICLE - Book OCR Quality Lab - Baseline Runs SQLite Log Filtering and Experiment Provenance.md`
- `Projects/2026/05/24/ARTICLE - Building Book OCR on Scraper Job System - Workflow Runtime Deep Dive.md` (found by inventory)
- `Projects/2026/05/24/ARTICLE - Extracting Book OCR from Scraper - Workflow Runtime and External OCR Pipelines.md` (found by inventory)
- `Projects/2026/05/25/ARTICLE - VLM Separation Benchmark for Book OCR - Prompt Block Layouts and Turn Persistence.md` (found by inventory)
- `Projects/2026/05/26/ARTICLE - Book OCR Project Report - Structured Workflow Runtime and Manual PDF Repair.md`
- `Projects/2026/05/26/ARTICLE - Structured Book OCR - Target Page Contracts Workflow Runtime and Production Hardening.md` (found by inventory)
- `Projects/2026/05/21/ARTICLE - PDF Page Reordering with VLM and a Retro Mac Webapp.md` (found by inventory)

Key shape: model-based OCR became a durable workflow application with SQLite/workflow state, page-level artifacts, structured JSON, deterministic Markdown/PDF rendering, and manual repair.

High-signal details:

- VLM OCR pipeline uses PyMuPDF page rendering, Pinocchio VLM calls, SQLite work queue, parallel workers, and a universal prompt for page types (`Projects/2026/05/20/...VLM OCR...`, lines 24-75).
- SQLite work queue needs `BEGIN IMMEDIATE` to prevent workers from claiming the same page (`Projects/2026/05/20/...VLM OCR...`, lines 24-31, 71-75).
- Quality lab preserves manifests, prompts, logs, SQLite summaries, exported projections, comparison notes, diaries, final QA, and selected raw/deterministic artifacts (`Projects/2026/05/24/...Book OCR Quality Lab...`, lines 24-64).
- Production book OCR records raw model evidence, structured JSON, rendered Markdown, validation metadata, persisted Geppetto turns, workflow state, projection state, and final review artifacts (`Projects/2026/05/26/...Book OCR Project Report...`, lines 24-38).
- Major architectural correction: target-page-only structured JSON plus deterministic Markdown rendering, instead of neighboring-page freeform Markdown (`Projects/2026/05/26/...Book OCR Project Report...`, lines 24-35).

### Codebase browser / indexing / static SQL

Reports:

- `Projects/2026/04/20/PROJ - Codebase Browser - Embedded Go+TS Doc Server with Live Source Snippets.md` (found by inventory)
- `Projects/2026/04/20/PROJ - Codebase Browser - Static Analysis and Dagger Pipeline.md`
- `Projects/2026/04/23/ARTICLE - Playbook - Static Browser Code Indexes with TinyGo and SQLite.md` (found by inventory)
- `Projects/2026/04/23/ARTICLE - Textbook - Building a Git-Aware Codebase Index with SQLite.md` (found by inventory)
- `Projects/2026/04/23/ARTICLE - Textbook - Using the Codebase Browser History Index.md` (found by inventory)
- `Projects/2026/04/23/PROJ - Codebase Browser - Static WASM Build and SQLite Prototype.md`
- `Projects/2026/05/01/ARTICLE - Static SQL.js Codebase Browser - SQLite as the Browser Runtime.md` (found by inventory)
- `Projects/2026/05/02/ARTICLE - SQLite Introspection - Exact Page-Level Size Analysis with Go and React.md` (found by inventory)
- `Projects/2026/05/02/ARTICLE - Squeezing a SQLite Database From 32 MB to 1.4 MB - How We Found and Fixed 99 Pct Redundancy in Codebase-Browser.md` (found by inventory)
- `Projects/2026/05/03/ARTICLE - SQLite in the Browser - Measuring and Fixing sql.js Performance in Static Code Review Sites.md` (found by inventory)
- `Projects/2026/05/27/ARTICLE - Go AST Analysis - From JavaScript Bindings to Web Source Browser.md` and `...xgoja Bindings and Codebase Navigation.md` (found by inventory)

Key shape: codebase-browser starts as Go+TS static analysis and moves toward static, portable, SQLite/FTS-backed browser snapshots.

High-signal details:

- Multi-language extractor emits packages/files/symbols/refs from Go (`go/packages`) and TypeScript (Compiler API) into a shared schema with language-aware IDs (`Projects/2026/04/20/...Static Analysis...`, lines 24-41).
- Dagger runs Node 22 + pnpm hermetically from Go, with local fallback and sha256 equivalence checks (`Projects/2026/04/20/...Static Analysis...`, lines 24-41).
- Static build can run from `file://`; next step is replacing hand-rolled JSON indexes with relational SQLite and FTS5 (`Projects/2026/04/23/...Static WASM...`, lines 24-74).

### Readwise / personal library / local search

Reports:

- `Projects/2026/05/21/PROJ - Readwise Viewer.md`
- `Projects/2026/05/22/ARTICLE - Readwise Viewer Bleve Search Port.md` (found by inventory)

Key shape: local Readwise workbench with SQLite as canonical store, Go/Glazed CLI/API, CLIM-style web UI, and planned/partial Bleve/embedding hybrid search.

High-signal details:

- Local library has 13,848 documents; SQLite schema includes `documents`, `tags`, `document_tags`, `sync_runs`, `sync_state`, and `documents_fts` (`Projects/2026/05/21/PROJ - Readwise Viewer.md`, lines 24-57).
- Design path: SQLite remains canonical, Bleve becomes disposable derived index; planned embeddings + BM25/kNN + RRF and `/api/search` integration (`Projects/2026/05/21/PROJ - Readwise Viewer.md`, lines 24-64).
- UI pattern: typed `PresentationRef` envelopes and selectable action presentations (`Projects/2026/05/21/PROJ - Readwise Viewer.md`, lines 24-75).

### Document co-read / knowledge graph / recommender

Reports:

- `Projects/2026/05/13/PROJECT REPORT - Document Co-Read Observatory - Transcript Mining to Recommender Workbench.md`

Key shape: go-minitrace transcript history becomes an implicit document graph. Documents are nodes; weighted edges indicate documents read near each other in coding-agent sessions.

High-signal details:

- Uses go-minitrace JavaScript query commands backed by DuckDB; important verbs are `read-events`, `doc-frequency`, `global-pairs`, `session-pairs`, `recommend`, `association-rules`, `graph`, and `session-timeline` (`Projects/2026/05/13/...Document Co-Read...`, lines 24-38).
- Dashboard inspects document frequencies, association rules, graph edges, and session timelines before runtime recommender integration (`Projects/2026/05/13/...Document Co-Read...`, lines 32-38).

### Knowledge base / publishing / Obsidian

Reports found by inventory:

- `Projects/2026/05/11/ARTICLE - Building a Knowledge Base Playbook - From 304 Project Reports to 18 Entries.md`
- `Projects/2026/05/15/ARTICLE - Retro Obsidian Publish - Building a Self-Hosted Knowledge Base from Markdown Files.md`
- `Projects/2026/06/06/PROJ - Retro Obsidian Publish - A Retro Monochrome Vault Browser.md`
- `Projects/2026/06/07/PROJ - Retro Obsidian Publish - React Router SSR Hydration Cleanup.md`
- `Projects/2026/05/04/ARTICLE - Obsidian to reMarkable Sync - Native Delta Upload and Vault Report Pipeline.md`

These overlap with web/app/productivity and infra slices but are relevant because they turn project reports and Markdown vaults into browsable/searchable knowledge surfaces.

### Data export/import / scraping / notebooks / SQLite preset

Reports:

- `Projects/2026/03/21/PROJ - DOM Scraping Experiment - Web to Markdown via JS DOM Queries.md`
- `Projects/2026/03/23/PROJ - CozoDB Editor - Merge Resolution, SQLite Preset, and Editor Highlighting.md`
- `Projects/2026/04/02/PROJ - Smailnail SQLite Mirror, Merge, Enrich, and Annotation Report.md` (found by inventory)
- `Projects/2026/04/14/PROJ - WASM JSON Flattener - Go CLI and WebAssembly Tool.md` and `Projects/2026/04/15/PROJ - JSON Flattener - Go WASM JSON Conversion Tool.md` (found by inventory)
- `Projects/2026/05/07/ARTICLE - SQLite Trace Browser - Building a db-browser JavaScript Inspection App.md` and `Projects/2026/05/08/ARTICLE - db-browser - Goja JavaScript SQLite App Runtime Deep Dive.md` (found by inventory)
- `Projects/2026/06/08/ARTICLE - SQLite Authorizer and Query Safety - Deep Dive Technical Analysis.md` plus `Projects/2026/06/08/sqldive-sources/*` (found by inventory)

Key shape: recurring movement from raw external or source formats into typed, queryable local stores, usually SQLite, with CLIs/UIs for inspection.

## Clusters and subclusters

### Cluster A: SQLite as canonical local truth

Subclusters:

- RAG corpus DB: sources/documents/chunks/embeddings/evaluation records.
- Workflow engine DB: ops/dependencies/retry state separate from domain DB.
- Readwise local mirror: documents/tags/sync state/FTS.
- Codebase browser static DB: packages/files/symbols/refs/history/FTS.
- OCR work queue/provenance DB: page status, logs, artifacts, projections.
- WordPress/WooCommerce export DB: compact RAG-facing schema/views over product/editorial content.

Recurring concept-map node: `SQLite canonical store`.

Edges:

- `SQLite canonical store -> derived Bleve/FAISS index` labeled `rebuildable derived artifact`.
- `SQLite canonical store -> React/CLIM inspector` labeled `local visible state`.
- `SQLite canonical store -> Glazed CLI` labeled `operator surface`.
- `Workflow engine SQLite -> corpus SQLite` labeled `orchestrates but does not own domain records`.

### Cluster B: RAG evaluation as observable pipeline

Subclusters:

- Intake: filesystem, Defuddle/web extraction, WordPress dump extraction.
- Transformation: preprocessing, chunking strategies, enrichment.
- Embeddings: Geppetto/Pinocchio profiles, text-hash freshness, dimension validation.
- Retrieval: BM25, vector, hybrid RRF, smoke tests.
- Evaluation: not fully mature yet; metrics and benchmark dashboard are repeatedly deferred.
- UI: corpus explorer, workflow intake dashboard, context viewer.

Recurring node: `RAG pipeline stage visibility`.

Edges:

- `Source -> Document -> Chunk -> Embedding -> Search -> Evaluation`.
- `Chunking strategy -> chunk identity` labeled `must be strategy-aware and rerun-safe`.
- `Embedding provider profile -> embedding records` labeled `profile-backed reproducibility`.
- `Smoke query -> retrieval defects` labeled `diagnoses before formal metrics`.

### Cluster C: Search index as disposable acceleration layer

Subclusters:

- Bleve BM25 over persisted chunks.
- Brute-force vector search over SQLite embeddings.
- Bleve vector KNN through FAISS.
- Hybrid fusion: RRF/RSF.
- FTS5 in SQLite for static browser / Readwise.

Recurring node: `Derived search index`.

Edges:

- `Chunks in SQLite -> Bleve BM25 index` labeled `rebuild`.
- `Embeddings in SQLite -> brute-force vector search` labeled `small-set correctness baseline`.
- `Bleve vectors -> FAISS` labeled `native CGO build dependency`.
- `BM25 + vector -> RRF hybrid result`.

### Cluster D: Workflow/provenance-first model operations

Subclusters:

- Book OCR structured workflow runtime.
- RAG intake workflow UI.
- Scraper job/workflow runtime.
- Persistent Geppetto turns and artifacts.
- Experiment manifests, prompts, logs, exported projections.

Recurring node: `Evidence-preserving model workflow`.

Edges:

- `Model call -> persisted raw turn`.
- `Raw turn -> structured JSON -> deterministic Markdown/PDF`.
- `Workflow op -> artifact coverage UI`.
- `Manual review -> targeted rerun`.

### Cluster E: Static/local knowledge browsers

Subclusters:

- Codebase browser: source code -> schema/index -> static SPA.
- Retro Obsidian Publish: Markdown vault -> self-hosted knowledge site.
- Readwise Viewer: personal library -> CLIM workbench.
- Document Co-Read Observatory: transcript reads -> document graph dashboard.

Recurring node: `Browsable local corpus`.

Edges:

- `Source corpus -> normalized index -> static/browser UI`.
- `Interaction logs/transcripts -> implicit knowledge graph`.
- `Typed presentations -> commandable UI objects`.

## Recurring concepts and technologies

- **SQLite**: canonical state, queue coordination, local mirrors, static browser DBs, FTS5, trace inspection, workflow engine state.
- **Bleve**: BM25, vector fields, KNN, hybrid fusion, JavaScript bindings.
- **FAISS / CGO**: native vector search dependency; repeated linker/header/library path risks.
- **Geppetto / Pinocchio profiles**: embedding and VLM provider resolution; persistent model turns.
- **Glazed CLI**: operator commands sharing service layers with HTTP APIs.
- **React/Vite/RTK Query**: inspection dashboards and corpus explorers.
- **Goja/xgoja/jsverbs**: JavaScript orchestration over Go-backed search/data modules.
- **Dagger**: hermetic build/extraction pipeline for Node/TS codebase indexing.
- **DuckDB**: document co-read transcript mining backend.
- **FTS5**: SQLite-native search for static/local corpora.
- **Workflow DAGs**: durable ops, dependencies, leases, retries, queues, artifact coverage.
- **Reproducible numbered scripts**: especially WordPress dump export and DOM scraping experiments.

## Recurring failure modes

- **Chunking loop/identity bugs**: unsafe chunking path exposed termination and rerun/idempotency issues; fix was progress invariants and strategy-aware chunk IDs.
- **Sparse or biased embedding coverage**: early RAG search results are constrained by tiny/source-skewed embedding samples.
- **Corpus coverage/composition gaps**: product discovery and broad care queries expose missing or weak product text composition.
- **Benchmark premature formalism**: reports emphasize smoke tests before recall/MRR/NDCG because ranked lists must first be stable and inspectable.
- **SQLite concurrency hazards**: parallel OCR workers need atomic claims (`BEGIN IMMEDIATE`); workflow/domain DBs are split to reduce contention.
- **Long MySQL dump inspection hazards**: `grep | head` on compressed dump can still emit huge single-line inserts; bounded streaming scripts are safer.
- **FAISS build/link fragility**: missing headers, missing `libfaiss.so`, incomplete `CGO_LDFLAGS`, runtime library path issues.
- **Goja wrapper lifecycle bugs**: hidden refs and batch execution need careful state/lifetime rules.
- **Model OCR drift**: page-type ambiguity, list-page style drift, caption bleed from neighboring pages, duplicated text, hallucinated structure.
- **Frontend context explosion**: workflow UI groups ops by operation/status because thousands of individual ops overwhelm the UI/API response.
- **Static browser data bloat/performance**: codebase-browser has follow-up reports about reducing SQLite size and sql.js performance.

## Candidate concept-map nodes

High-level nodes:

- Recent project corpus
- Local corpus workbench
- SQLite canonical store
- Derived search index
- RAG evaluation system
- Corpus ingestion path
- WordPress/WooCommerce dump
- TTC SQLite corpus
- Defuddle/web extraction
- Document/chunk/embedding records
- Chunking strategy
- Embedding provider profile
- Geppetto/Pinocchio
- BM25 retrieval
- Vector retrieval
- Hybrid RRF retrieval
- Bleve
- FAISS/go-faiss/CGO
- Goja/xgoja search runtime
- Glazed CLI
- HTTP API
- React corpus explorer
- Workflow engine DB
- Durable workflow DAG
- Evidence-preserving model workflow
- Book OCR pipeline
- Structured OCR JSON
- Deterministic Markdown/PDF renderer
- Targeted repair loop
- Codebase browser index
- Static browser SQLite
- Readwise local mirror
- Document co-read graph
- Retro Obsidian Publish / knowledge base
- Reproducible numbered scripts

## Candidate concept-map edges

- `WordPress/WooCommerce dump -> TTC SQLite corpus` (`extracts normalized RAG-facing schema`)
- `TTC SQLite corpus -> RAG app DB` (`imports documents by source`)
- `RAG app DB -> chunks` (`chunking strategies produce retrievable units`)
- `chunks -> embeddings` (`Geppetto/Pinocchio provider computes vectors`)
- `chunks -> Bleve BM25 index` (`builds lexical index`)
- `embeddings -> vector retrieval` (`brute-force baseline or Bleve KNN`)
- `BM25 retrieval + vector retrieval -> hybrid RRF` (`rank fusion`)
- `SQLite canonical store -> derived search index` (`index is rebuildable, not source of truth`)
- `workflow engine DB -> RAG app DB` (`orchestrates artifact production without cross-DB joins`)
- `React corpus explorer -> corpus DB` (`makes hidden pipeline state inspectable`)
- `Glazed CLI -> shared domain services <- HTTP API` (`same behavior through operator and UI surfaces`)
- `Book page images -> VLM OCR -> structured JSON -> Markdown/PDF` (`model evidence to review artifact`)
- `manual PDF review -> targeted page rerun` (`localized repair loop`)
- `goja-bleve -> Bleve` (`JavaScript builders wrap Go search objects`)
- `Bleve vectors -> FAISS` (`requires native build/tag/env setup`)
- `Readwise API -> SQLite mirror -> FTS/Bleve/embedding search` (`personal library search pipeline`)
- `source code -> AST extractors -> SQLite/JSON index -> static browser` (`codebase browser pipeline`)
- `transcript read events -> co-read graph -> recommender dashboard` (`implicit workflow knowledge`)

## Overlaps with other topic slices

- **Agent transcripts / observability**: Document Co-Read Observatory, go-minitrace query commands, transcript mining, RAG context viewer, OCR persistent Geppetto turns. Coordinate with Agent 5.
- **JavaScript runtimes / Goja / xgoja DSLs**: goja-bleve, xgoja vector runtime, jsverbs, widgetdsl, Go-backed fluent builders. Coordinate with Agent 2.
- **Web UI / productivity surfaces**: Readwise Viewer, Corpus Explorer, Workflow Intake UI, Codebase Browser, Retro Obsidian Publish. Coordinate with Agent 7.
- **Typography/layout/design systems**: RAG frontend layered component library, context viewer, Retro UI, PDF/rendering artifacts. Coordinate with Agent 3.
- **Infra/deployment**: embedded Go binaries and static sites are local-first, but Retro Obsidian Publish/docs publishing may touch GitOps. Coordinate lightly with Agent 4.
- **Hardware/reMarkable/book workflows**: Book OCR and Obsidian-to-reMarkable sync overlap with reMarkable/e-reader work. Coordinate with Agent 1 for tablet/book reading surfaces.

## Open questions

1. Is `RAG Evaluation System` the central concept-map hub for this slice, with Bleve/FAISS/OCR/Readwise/codebase-browser as satellite patterns, or should the map be organized around `Local corpus workbench` instead?
2. How far did the formal evaluation layer progress after the retrieval smoke tests? Inventory shows many RAG UI/search reports, but metrics/benchmark dashboard may still be incomplete.
3. Which Readwise Bleve search pieces are implemented versus only designed in `RWVEC-001`? The main Readwise report says design path; a follow-up Bleve Search Port likely has implementation details.
4. Did codebase-browser fully migrate to SQLite/FTS, or did it remain a prototype plus performance work? Several May reports probably answer this.
5. Should Book OCR be mapped as an OCR topic or as a general durable workflow/model provenance topic? It strongly connects to both.
6. Are Retro Obsidian Publish and Knowledge Base Playbook in scope for this data/search map, or should they primarily live in web/productivity?
7. For concept-map edges, should technologies (SQLite/Bleve/FAISS) be nodes or annotations on pipeline edges? The corpus repeatedly treats SQLite as an architectural invariant, so it probably deserves a first-class node.

## Report-format lessons

- A useful structure for this slice is `project arc -> architectural invariant -> failure modes -> concept-map candidates`, not a flat list of files.
- Include both deeply read files and inventory-only files, but mark inventory-only clearly; this avoids pretending exhaustive reading while preserving leads.
- Quote line ranges around summaries/architecture blocks; most reports have excellent `[!summary]` blocks early, so first 80-110 lines are often enough for scouting.
- Keep technologies separate from projects: SQLite/Bleve/FAISS/Geppetto recur across unrelated projects and should become reusable map nodes.
- Record failure modes as first-class findings; they are often more map-worthy than implementation details because they explain why patterns recur.

## Start here

Start with `Projects/2026/05/27/ARTICLE - RAG Evaluation System - Workflow-Driven Retrieval Evaluation.md`. It is the best entry point because it names the central pipeline (`Source -> Document -> Chunk -> Embedding -> Search -> Evaluation`), establishes SQLite/service/CLI/HTTP/frontend architecture, and lists what was implemented versus deferred. Then read the 2026-05-28 retrieval and TTC corpus reports to understand how the abstract pipeline became a real corpus/search system.
