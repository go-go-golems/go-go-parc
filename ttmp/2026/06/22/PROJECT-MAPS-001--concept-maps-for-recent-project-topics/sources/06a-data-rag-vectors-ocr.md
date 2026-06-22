# Topic 6 Partition A: RAG Evaluation, Vector Search, and Book OCR

**Partition**: Data/RAG/OCR/Search — pipeline sections only (RAG evaluation system / TTC corpus / retrieval, Bleve / FAISS / Goja / xgoja vector search, Book OCR / scanned PDF workflows). Excludes codebase browser, Readwise, co-read graph, knowledge base, and data export/import (partition B).

**Ticket**: PROJECT-MAPS-001

---

## Executive summary

- The RAG Evaluation System (`RAGEVAL-001`/`002`/`004`/`006`/`007`) is the central arc: a Go + SQLite + Glazed + HTTP + React pipeline (`Source → Document → Chunk → Embedding → Search → Evaluation`) where SQLite is canonical and all indexes/workflow artifacts are derived/rebuildable.
- The Bleve/FAISS/Goja arc (`goja-bleve`, xgoja vector runtime) extends the RAG search layer with native Bleve vector KNN, hybrid RRF/RSF fusion, and JavaScript scripting via `require("bleve")` — all behind a CGO/FAISS build-tag boundary.
- The Book OCR arc (`BOOK-OCR-HQ-001`, structured workflow runtime) is a model-call-to-durable-artifact system that evolved from freeform Markdown OCR to target-page-only structured JSON with deterministic Markdown rendering, figure extraction, PDF generation, and targeted page repair.
- The concept-map spine is: **SQLite canonical store → derived search index → evidence-preserving model workflow → targeted repair loop**.
- Start with `Projects/2026/05/27/ARTICLE - RAG Evaluation System - Workflow-Driven Retrieval Evaluation.md` and `Projects/2026/05/26/ARTICLE - Book OCR Project Report - Structured Workflow Runtime and Manual PDF Repair.md`.

---

## Scope and search method

- **Corpus**: Markdown project/report files under `Projects/2026/{05,06}/`.
- **Search**: filename + content filtering for `rag`, `retriev`, `faiss`, `bleve`, `goja`, `xgoja`, `vector`, `ocr`, `book`, `vlm`, `scanned`, `pdf`, `ttc corpus`, `embedding`.
- **Selection**: deeply read canonical architecture reports for each arc; heading-scanned adjacent/variant reports; read the xgoja env variant articles by frontmatter only (two LLM-generated variants of the same content).
- **Partition boundary**: did NOT read codebase browser/indexing, Readwise, document co-read, knowledge base/Obsidian, or data export/import/scraping files.

---

## Evidence ledger

| Path | Evidence level | Lines / basis | Cluster | Why it matters |
|---|---|---|---|---|
| `Projects/2026/05/27/ARTICLE - RAG Evaluation System - Workflow-Driven Retrieval Evaluation.md` | read | lines 1-end | RAG eval core | Canonical RAG architecture: 5-layer model, identity rules, chunking termination bug, embedding service |
| `Projects/2026/05/28/ARTICLE - RAG Evaluation System - Building a Database-Backed TTC Corpus Pipeline.md` | read | lines 1-end | TTC corpus | WordPress dump → MySQL → normalized SQLite → RAG app DB; source-aware embedding; failure modes |
| `Projects/2026/05/28/ARTICLE - RAG Evaluation System - Search Retrieval Foundation Deep Dive.md` | read | lines 1-end | RAG retrieval | BM25/vector/hybrid RRF retrieval stack; smoke tests vs benchmarks; corpus coverage gaps |
| `Projects/2026/05/28/ARTICLE - RAG Evaluation System - Corpus Explorer and Pipeline Visualization Website.md` | read | lines 1-end | RAG frontend | React SPA embedded in Go binary; corpus explorer three-column layout; retro macOS design |
| `Projects/2026/05/29/ARTICLE - RAG Evaluation - Workflow Intake UI Architecture and Data Exploration.md` | read | lines 1-end | RAG workflow UI | Two-SQLite-DB architecture; ops grouping by (operation, status); artifact coverage; bidirectional navigation |
| `Projects/2026/05/29/ARTICLE - RAG Evaluation System - Intake Pipeline Deep Dive.md` | read | lines 1-120 | RAG intake | Intake pipeline: source→document→chunk→embedding; scraper-backed durable workflow layer |
| `Projects/2026/05/30/PROJ - RAG Evaluation - Workflow Intake UI Implementation Report.md` | heading-scanned | frontmatter + summary | RAG workflow UI | Implementation deep dive of RAGEVAL-007; same two-DB architecture |
| `Projects/2026/06/03/ARTICLE - Exporting WordPress WooCommerce Data into a RAG SQLite Corpus.md` | read | lines 1-end | TTC export | Compact RAG-facing SQLite schema with `view_products`/`view_documents`; base64 JSON transport; FTS5 |
| `Projects/2026/06/03/ARTICLE - Deep Dive - xgoja Scripting for RAG Evaluation Systems.md` | read | lines 1-end | RAG scripting | xgoja-generated `rag-eval-js` binary; `db`/`fs`/`express`/`goja-text` modules; dynamic SQL pattern |
| `Projects/2026/06/07/ARTICLE - RAG Evaluation System - Frontend Architecture and Context Viewer Integration.md` | read | lines 1-end | RAG frontend | Layered component library (tokens→atoms→organisms); context-viewer vocabulary; Widget IR path |
| `Projects/2026/06/02/ARTICLE - Building FAISS for Bleve Vector Search.md` | read | lines 1-end | FAISS build | FAISS CMake/build; CGO linker flags; Bleve KNN experiment validation |
| `Projects/2026/06/03/ARTICLE - Goja Bleve - Native Search Bindings for JavaScript RAG Pipelines.md` | read | lines 1-end | goja-bleve binding | Fluent JS wrappers backed by hidden Go refs; build-tag-safe vector support; hybrid RRF/RSF |
| `Projects/2026/06/06/ARTICLE - Goja Bleve - Shipping a Vector RAG Runtime with xgoja.md` | read | lines 1-end | goja-bleve shipping | xgoja vector host composition; `go.env` for CGO_LDFLAGS; jsverb field naming; review hardening |
| `Projects/2026/06/06/xgoja env/ARTICLE - xgoja - Build Environments and Jsverb Command Design for Vector RAG Tools (gpt-5.5 medium).md` | heading-scanned | frontmatter + summary | xgoja env | LLM variant of xgoja env article; same `go.env`/jsverb naming content |
| `Projects/2026/06/06/xgoja env/ARTICLE - xgoja - Build Environment Variables and Jsverb Command Design for Vector RAG Tools - qwen3.6 - thinking high.md` | heading-scanned | frontmatter + summary | xgoja env | Second LLM variant; confirms `go.env`, jsverb flag remapping, section preservation |
| `Projects/2026/05/20/ARTICLE - VLM OCR Pipeline for Scanned PDFs.md` | read | lines 1-end | VLM OCR | 202-page scanned PDF → VLM OCR; SQLite work queue with `BEGIN IMMEDIATE`; universal prompt; `[IMAGE:]` tokens |
| `Projects/2026/05/24/ARTICLE - Book OCR Quality Lab - Baseline Runs SQLite Log Filtering and Experiment Provenance.md` | read | lines 1-end | OCR quality lab | Experiment provenance system; prompt optimization loop; SQLite log capture; deterministic QA/cleanup |
| `Projects/2026/05/26/ARTICLE - Book OCR Project Report - Structured Workflow Runtime and Manual PDF Repair.md` | read | lines 1-end | Book OCR production | Target-page-only structured JSON; deterministic Markdown rendering; workflow-backed PDF; targeted reruns |
| `Projects/2026/05/24/ARTICLE - Building Book OCR on Scraper Job System - Workflow Runtime Deep Dive.md` | heading-scanned | frontmatter + summary | OCR workflow runtime | Scraper → workflow runtime shift; OCR MVP as validation workload |
| `Projects/2026/05/24/ARTICLE - Extracting Book OCR from Scraper - Workflow Runtime and External OCR Pipelines.md` | heading-scanned | frontmatter + summary | OCR boundary | Move all OCR out of `scraper/` into `book-ocr/`; runtime stays reusable |
| `Projects/2026/05/25/ARTICLE - VLM Separation Benchmark for Book OCR - Prompt Block Layouts and Turn Persistence.md` | heading-scanned | frontmatter + summary | OCR benchmark | Target-page isolation benchmark; Geppetto turn persistence; schema repair |
| `Projects/2026/05/26/ARTICLE - Structured Book OCR - Target Page Contracts Workflow Runtime and Production Hardening.md` | heading-scanned | frontmatter + summary | Structured OCR | StructuredPageOCR JSON contract; deterministic renderer; workflow promotion |
| `Projects/2026/05/21/ARTICLE - PDF Page Reordering with VLM and a Retro Mac Webapp.md` | heading-scanned | frontmatter + summary | PDF reordering | VLM page-number extraction; chapter-opener placement; retro Mac webapp; human-in-the-loop |

---

## Condensed per-arc summaries

### Arc 1: RAG evaluation system / TTC corpus / retrieval

- **Five-layer architecture with service-first invariant**: SQLite state → domain services → Glazed CLI adapters → HTTP API adapters → React frontend. CLI and HTTP are thin adapters over shared services — never implement behavior directly in handlers (`Projects/2026/05/27/...`, lines 24-43, 91-137).
- **Identity is the central design rule**: document = `(source_id, relative_path)`; chunk = `(document_id, strategy_id, chunk_index)`; embedding = `(chunk_id, strategy_id, provider, model, dimensions)` with `text_hash` freshness. Derived state is rebuilt or skipped via stable keys (`Projects/2026/05/27/...`, lines 24-60).
- **Two-database architecture**: corpus DB (`data/rag-eval.db`) for domain data vs. engine DB (`state/rag-eval-workflows.db`) for workflow orchestration state. Separation prevents WAL write contention; cross-DB joins happen in UI, not backend (`Projects/2026/05/29/...Workflow Intake UI...`, lines 24-76).
- **TTC corpus pipeline**: WordPress/WooCommerce MySQL dump → isolated MySQL 8 Docker container → normalized SQLite corpus → app DB import. Two export paths: original RAGEVAL-002 (3,096 docs, 255 chunks) and later RAGEVAL-TTC-SQLITE-EXPORT (3,258 docs, FTS5, bot-facing views `view_products`/`view_documents`). Base64 JSON transport solves MySQL CLI escaping (`Projects/2026/05/28/...TTC Corpus...`, `Projects/2026/06/03/...Exporting WordPress...`).
- **Retrieval foundation**: BM25 (Bleve v2, disposable index at `data/indexes/bm25/`), brute-force vector search over stored embeddings, hybrid RRF (`k=60`). Smoke tests are explicitly not benchmarks — they catch broken request paths, not relevance. Key lesson: weak retrieval is usually corpus/text-composition failure, not ranking failure (`Projects/2026/05/28/...Search Retrieval...`, lines 24-100).

### Arc 2: Bleve / FAISS / Goja / xgoja vector search

- **Go-backed wrappers with hidden refs**: `goja-bleve` exposes Bleve as `require("bleve")` with fluent JS builders, but real state (mappings, queries, indexes, batches, search requests) lives in Go-backed refs attached via non-enumerable `__bleve_ref`. JS cannot forge typed objects (`Projects/2026/06/03/...Native Search Bindings...`, lines 24-70).
- **Build-tag-safe vector support**: `vector_api.go` (non-vector stubs) and `vector_api_vectors.go` (`-tags=vectors`) split. Normal builds work without FAISS; vector builds expose Bleve KNN via `go-faiss` CGO. KNN validated against index mapping at search time (`Projects/2026/06/03/...Native Search Bindings...`, lines 70-end).
- **FAISS build fragility**: requires `blevesearch/faiss@fff814d`, CMake with `FAISS_ENABLE_C_API=ON`, `BUILD_SHARED_LIBS=ON`, `-DCMAKE_CXX_FLAGS="-I$PWD"`. Go link needs `CGO_LDFLAGS="-L/usr/local/lib -lfaiss_c -lfaiss -lstdc++ -lm"` and `-ldflags "-r /usr/local/lib"`. Missing `libfaiss.so` → unresolved `faiss::` symbols (`Projects/2026/06/02/...FAISS...`, lines 24-70).
- **xgoja vector host**: `xgoja-vectors.yaml` composes `bleve` + `geppetto` + `fs` + core helpers into one generated binary. `go.env` (new xgoja feature) encodes `CGO_LDFLAGS` in the spec, not shell. jsverb field remapping separates CLI kebab-case from JS camelCase. Three review fixes: reopened indexes load stored mapping, `.size(0)` preserved explicitly, batch marked executed only after success (`Projects/2026/06/06/...Shipping...`, lines 24-90).
- **Bleve-native hybrid vs. manual RRF**: goja-bleve exposes one `SearchRequest` with text query + KNN clauses + `Score: "rrf"`, replacing the rag-eval system's manual two-call merge. This is the structural upgrade path for RAG retrieval (`Projects/2026/06/03/...Native Search Bindings...`, lines 70-end).

### Arc 3: Book OCR / scanned PDF workflows

- **Evolution from script to durable workflow**: VLM OCR started as a Python script with SQLite work queue (`BEGIN IMMEDIATE` for atomic page claims) and evolved into a Go-native workflow runtime (`scraper/pkg/workflow`) with ops, queues, leases, retries, artifacts, and projections (`Projects/2026/05/20/...VLM OCR...`, `Projects/2026/05/24/...Building Book OCR on Scraper...`).
- **Target-page-only structured JSON is the production boundary**: freeform Markdown OCR with neighboring-page context caused adjacent figure-caption bleed. Fix: model sees exactly one page image, returns `StructuredPageOCR` JSON; Go renders deterministic Markdown. Raw evidence (turns, raw response, structured JSON, rendered MD, validation JSON) preserved per page (`Projects/2026/05/26/...Book OCR Project Report...`, lines 24-90).
- **Evidence-preserving experiment system**: BOOK-OCR-HQ-001 established the prompt optimization loop: baseline → classify failures → vision-validate disputed details → change one variable → targeted pages → QA → deterministic cleanup. Logs become SQLite data, not terminal scrollback. Raw and normalized artifacts kept separately (`Projects/2026/05/24/...Book OCR Quality Lab...`, lines 24-90).
- **Targeted repair loop**: `structured-rerun-pages` requeues selected page ops (→ `ready`) and downstream ops (→ `pending`), preserving dependency semantics. Manual PDF review → map defects to source page → inspect right stage (JSON vs rendered MD vs embedded MD vs PDF) → fix smallest layer → rerun affected pages only (`Projects/2026/05/26/...Book OCR Project Report...`, lines 90-end).
- **Boundary decision**: all OCR logic moved from `scraper/` into `book-ocr/` repository. `scraper/` retains reusable workflow runtime; `book-ocr/` owns OCR application. This keeps the runtime reusable for other workloads (`Projects/2026/05/24/...Extracting Book OCR from Scraper...`).

---

## Candidate concept-map material

### Nodes

| Node | Type | Confidence | Notes |
|---|---|---|---|
| RAG Evaluation System | project | high | Central data/search arc; RAGEVAL-001/002/004/006/007 |
| SQLite canonical store | concept | high | Canonical state for RAG corpus, workflow engine, OCR queue/provenance |
| Derived search index | concept | high | Bleve BM25 + FAISS vector indexes; rebuildable from SQLite |
| RAG pipeline stage visibility | concept | high | Every derived artifact connected to input/config; inspectable per stage |
| Strategy-aware chunk identity | concept | high | `(document_id, strategy_id, chunk_index)`; enables multi-strategy comparison |
| Provider-aware embedding identity | concept | high | `(chunk_id, strategy_id, provider, model, dimensions)` + `text_hash` freshness |
| Two-database architecture | concept | high | Corpus DB vs. engine DB; prevents WAL contention |
| TTC SQLite corpus | artifact | high | Normalized WordPress/WooCommerce content for RAG ingestion |
| WordPress/WooCommerce dump | artifact | high | Source for TTC corpus; MySQL dump → SQLite export |
| Defuddle/web extraction | workflow | high | Alternative corpus acquisition path (public page scraping → Markdown) |
| BM25 retrieval | technology | high | Bleve v2 lexical search; disposable index under `data/indexes/bm25/` |
| Vector retrieval (brute-force) | technology | high | Scan stored embeddings from SQLite; cosine similarity in Go |
| Hybrid RRF retrieval | technology | high | Reciprocal-rank fusion, `k=60`; manual merge in rag-eval, Bleve-native in goja-bleve |
| Bleve | technology | high | Full-text search library for Go; BM25 + vector KNN + hybrid fusion |
| FAISS / go-faiss / CGO | technology | high | Native C++ vector search; build-tag-gated behind `-tags=vectors` |
| Geppetto / Pinocchio profiles | technology | high | Embedding + VLM provider resolution; profile-backed reproducibility |
| goja-bleve | project | high | Native Bleve bindings for JavaScript RAG pipelines |
| xgoja vector runtime | project | high | Generated binary composing bleve + geppetto + fs + jsverbs |
| Go-backed wrapper pattern | concept | high | Hidden Go refs on JS wrappers; fluent API with type safety |
| Build-tag-safe vector support | concept | high | Non-vector stubs + vector implementations; normal builds work without FAISS |
| FAISS build fragility | failure-mode | high | Missing headers, incomplete CGO_LDFLAGS, stale libfaiss.so |
| goja wrapper lifecycle bugs | failure-mode | medium | Reopened index mapping, `.size(0)` default, batch execution timing |
| Book OCR pipeline | project | high | VLM OCR → structured JSON → deterministic Markdown → PDF → repair |
| Evidence-preserving model workflow | concept | high | Raw turns, structured JSON, rendered MD, validation JSON per page |
| StructuredPageOCR JSON contract | artifact | high | Model returns structured blocks; Go renders deterministic Markdown |
| Deterministic Markdown/PDF renderer | workflow | high | Go-owned rendering from structured OCR; pandoc+xelatex for PDF |
| Targeted repair loop | workflow | high | Rerun selected pages; preserve dependency semantics |
| Target-page-only OCR invariant | concept | high | Production OCR sees exactly one page image; no neighboring context |
| VLM OCR work queue | workflow | high | SQLite queue with `BEGIN IMMEDIATE`; parallel workers; resumable |
| Prompt optimization loop | workflow | high | Baseline → classify failures → change one variable → QA → cleanup |
| Chunking termination bug | failure-mode | high | Overlap loop emitted unbounded chunks; fix: explicit progress invariants |
| Sparse embedding coverage | failure-mode | high | Small source-skewed samples limit vector search validity |
| Corpus coverage gaps | failure-mode | high | Product text composition incomplete; missing structured facts |
| OCR hallucination / style drift | failure-mode | high | Duplicated paragraphs, list-page style drift, caption bleed |
| SQLite concurrency hazard | failure-mode | high | Parallel OCR workers need `BEGIN IMMEDIATE` for atomic claims |
| Workflow dependency race | failure-mode | medium | Targeted rerun set downstream ops `ready` instead of `pending` |
| Glazed CLI | technology | high | Operator surface sharing service layers with HTTP API |
| React corpus explorer | platform | high | React+Vite+RTK Query SPA embedded in Go binary via `go:embed` |
| Scraper workflow runtime | technology | high | Durable execution engine: ops, queues, leases, retries, artifacts, projections |
| xgoja `go.env` | concept | high | Build-time env vars in YAML spec; reproducible CGO builds |
| jsverb field remapping | concept | medium | CLI kebab-case ↔ JS camelCase; stable function signatures |
| TTC WordPress SQLite export | artifact | high | `view_products`/`view_documents`; FTS5; base64 JSON transport |
| Should evaluation metrics be formalized now? | open-question | high | Smoke tests are not benchmarks; relevance labels not yet created |
| Should OCR be mapped as OCR or as general durable workflow? | open-question | medium | Connects to both data/search and workflow/provenance topics |

### Edges

```text
WordPress/WooCommerce dump --extracts normalized schema--> TTC SQLite corpus [high] (Projects/2026/05/28/...TTC Corpus...)
TTC SQLite corpus --imports documents by source--> RAG Evaluation System [high] (Projects/2026/05/28/...TTC Corpus..., Projects/2026/06/03/...Exporting WordPress...)
SQLite canonical store --rebuilds into--> Derived search index [high] (Projects/2026/05/28/...Search Retrieval..., Projects/2026/05/27/...)
Derived search index --builds--> BM25 retrieval [high] (Projects/2026/05/28/...Search Retrieval...)
Derived search index --builds--> Vector retrieval (brute-force) [high] (Projects/2026/05/28/...Search Retrieval...)
BM25 retrieval --fuses with--> Vector retrieval --via--> Hybrid RRF retrieval [high] (Projects/2026/05/28/...Search Retrieval...)
Strategy-aware chunk identity --enables--> Provider-aware embedding identity [high] (Projects/2026/05/27/..., Projects/2026/05/29/...Intake Pipeline...)
Geppetto / Pinocchio profiles --resolves--> Provider-aware embedding identity [high] (Projects/2026/05/27/..., Projects/2026/05/28/...TTC Corpus...)
Two-database architecture --separates--> SQLite canonical store --from--> Scraper workflow runtime [high] (Projects/2026/05/29/...Workflow Intake UI...)
Glazed CLI --shares services with--> React corpus explorer --via--> HTTP API [high] (Projects/2026/05/27/..., Projects/2026/05/28/...Corpus Explorer...)
Scraper workflow runtime --orchestrates--> RAG Evaluation System [high] (Projects/2026/05/29/...Intake Pipeline..., Projects/2026/05/29/...Workflow Intake UI...)
FAISS / go-faiss / CGO --enables--> Bleve --vector KNN via--> goja-bleve [high] (Projects/2026/06/02/...FAISS..., Projects/2026/06/03/...Native Search Bindings...)
goja-bleve --exposes as--> require("bleve") --for--> xgoja vector runtime [high] (Projects/2026/06/03/...Native Search Bindings..., Projects/2026/06/06/...Shipping...)
xgoja `go.env` --encodes--> FAISS / go-faiss / CGO --linker flags in--> xgoja vector runtime [high] (Projects/2026/06/06/...Shipping..., Projects/2026/06/06/xgoja env/...)
Go-backed wrapper pattern --protects--> Bleve --from--> untyped JS object forgery [high] (Projects/2026/06/03/...Native Search Bindings...)
Build-tag-safe vector support --gates--> FAISS / go-faiss / CGO --behind--> -tags=vectors [high] (Projects/2026/06/03/...Native Search Bindings...)
Hybrid RRF retrieval --upgraded by--> Bleve-native RRF/RSF --in--> goja-bleve [high] (Projects/2026/06/03/...Native Search Bindings...)
VLM OCR work queue --uses--> SQLite canonical store --with--> BEGIN IMMEDIATE [high] (Projects/2026/05/20/...VLM OCR...)
Book OCR pipeline --enforces--> Target-page-only OCR invariant [high] (Projects/2026/05/26/...Book OCR Project Report...)
Book OCR pipeline --returns--> StructuredPageOCR JSON contract [high] (Projects/2026/05/26/...Book OCR Project Report..., Projects/2026/05/26/...Structured Book OCR...)
StructuredPageOCR JSON contract --rendered by--> Deterministic Markdown/PDF renderer [high] (Projects/2026/05/26/...Book OCR Project Report...)
Evidence-preserving model workflow --preserves--> Geppetto / Pinocchio profiles --turns in--> SQLite canonical store [high] (Projects/2026/05/26/...Book OCR Project Report...)
Targeted repair loop --requeues--> Book OCR pipeline --selected pages only--> Deterministic Markdown/PDF renderer [high] (Projects/2026/05/26/...Book OCR Project Report...)
Prompt optimization loop --drives--> Book OCR pipeline --through--> Evidence-preserving model workflow [high] (Projects/2026/05/24/...Book OCR Quality Lab...)
Chunking termination bug --corrected by--> Strategy-aware chunk identity [high] (Projects/2026/05/27/...)
FAISS build fragility --mitigated by--> xgoja `go.env` + Makefile test-vectors target [high] (Projects/2026/06/02/...FAISS..., Projects/2026/06/06/...Shipping...)
OCR hallucination / style drift --corrected by--> Target-page-only OCR invariant + Prompt optimization loop [high] (Projects/2026/05/20/...VLM OCR..., Projects/2026/05/24/...Book OCR Quality Lab...)
```

---

## Topic architecture / spine

```mermaid
flowchart TD
    subgraph RAG Pipeline
        Source[Source] --> Document[Document]
        Document --> Chunk[Chunk\nstrategy-aware identity]
        Chunk --> Embedding[Embedding\nprovider-aware identity]
        Embedding --> Search[Search / retrieval]
        Search --> Eval[Evaluation\nnot yet mature]
    end

    SQLite[(SQLite canonical store)] --> Chunk
    SQLite --> Embedding
    SQLite --> WorkflowDB[Workflow engine DB\nseparate orchestration state]
    WorkflowDB --> RAG Pipeline

    subgraph Search Stack
        BM25[Bleve BM25\n disposable index]
        Vector[Vector retrieval\n brute-force or FAISS KNN]
        Hybrid[Hybrid RRF\n k=60]
        BM25 --> Hybrid
        Vector --> Hybrid
    end

    SQLite --rebuilds--> BM25
    SQLite --rebuilds--> Vector

    subgraph JS Runtime Layer
        GojaBleve[goja-bleve\n require bleve]
        XgojaVector[xgoja vector runtime\n bleve + geppetto + fs]
        GojaBleve --> XgojaVector
        GojaBleve --Go-backed wrappers--> BM25
        GojaBleve --KNN via CGO--> FAISS[FAISS / CGO\n -tags=vectors]
        FAISS --> Vector
        XgojaVector --go.env--> FAISS
    end

    subgraph OCR Pipeline
        PageImages[Page images] --> VLM[VLM OCR\ntarget-page-only]
        VLM --> StructuredJSON[StructuredPageOCR JSON]
        StructuredJSON --> RenderMD[Deterministic Markdown]
        RenderMD --> PDF[PDF via pandoc]
        PDF --> Review[Manual review]
        Review --> Rerun[Targeted page rerun]
        Rerun --> VLM
    end

    SQLite --> VLM
    Geppetto[Geppetto / Pinocchio] --> Embedding
    Geppetto --> VLM
```

---

## Cross-links to other topic slices

- **Topic 2 (JavaScript/Goja/xgoja DSLs)**: `goja-bleve`, `xgoja vector runtime`, `jsverbs`, `go.env`, jsverb field remapping, `Go-backed wrapper pattern` — all belong to both Data/RAG and Goja/xgoja. The xgoja `go.env` feature and provider section preservation fix were driven by goja-bleve's vector build needs.
- **Topic 5 (AI agents/transcripts/observability)**: Geppetto/Pinocchio provider profiles, persisted model turns, provider replay bugs, and `go-minitrace` transcript analysis are shared infrastructure. The Book OCR turn persistence (`chatstore.SQLiteTurnStore`) and the RAG embedding provider resolution use the same Geppetto provider interface. The Document Co-Read Observatory (partition B) uses go-minitrace, which is the same transcript mining ecosystem.
- **Topic 7 (Web UI/apps/productivity)**: React corpus explorer, retro macOS monochrome design system, RTK Query data flow, `go:embed` single-binary deployment, Widget IR/component library — all connect to web/app surfaces. The RAG frontend layered component library (tokens→atoms→organisms) and Storybook/css-visual-diff workflow are shared with the web productivity slice.
- **Topic 3 (Typography/layout/design systems)**: The RAG frontend's context-viewer vocabulary (ContextBudgetBar, ContextStripDiagram, ContextTreemap) and Storybook visual regression defense connect to the design-systems slice. The Book OCR PDF rendering (pandoc + xelatex) touches typography/PDF concerns.
- **Topic 4 (Infra/auth/deployment)**: FAISS build requires system-level C++ library installation (`/usr/local/lib`), `ldconfig`, and CGO linker configuration — a deployment/environment concern. The `xgoja-vectors.yaml` spec encoding `CGO_LDFLAGS` is a reproducible build contract similar to GitOps/IaC patterns.
- **Topic 1 (Hardware/embedded)**: Book OCR and reMarkable book workflows (PDF page reordering, Obsidian-to-reMarkable sync) share the scanned-book/e-reader surface. The retro Mac webapp for PDF page reordering connects to retro UI patterns seen in hardware display projects.

---

## Open questions and second-pass targets

1. **Did the formal evaluation layer (recall/MRR/NDCG) ever progress beyond smoke tests?** The 2026-05-28 retrieval report explicitly defers benchmarks. Later RAG frontend reports (2026-06-07) show context-viewer work but no mention of evaluation metrics. Likely still incomplete.
2. **Did goja-bleve's Bleve-native hybrid replace the rag-eval manual RRF?** The goja-bleve article describes the structural upgrade, but the rag-eval search service still uses manual merge as of 2026-05-28. Unclear if integration happened later.
3. **Should Book OCR be mapped as an OCR topic or as a general durable workflow/provenance topic?** It strongly connects to both. The scraper workflow runtime is reusable; the OCR application is one workload. The concept map should probably show both the runtime and the OCR application as separate nodes.
4. **Are the xgoja env variant articles (gpt-5.5 medium vs qwen3.6 thinking high) substantively different?** Heading scan suggests same content with different reasoning depth. A second pass could confirm whether either adds unique architectural detail.
5. **Did the TTC WordPress SQLite export (`view_products`/`view_documents` with FTS5) supersede the earlier RAGEVAL-002 corpus pipeline?** Both exist as of 2026-06-03. The later export is more compact and bot-facing, but the earlier pipeline feeds the RAG app DB directly. Relationship unclear.

---

## Start here

1. `Projects/2026/05/27/ARTICLE - RAG Evaluation System - Workflow-Driven Retrieval Evaluation.md` — establishes the central pipeline, five-layer architecture, identity rules, the chunking termination bug, and the service-first invariant. Every other file in this partition builds on or complements this architecture.
2. `Projects/2026/05/26/ARTICLE - Book OCR Project Report - Structured Workflow Runtime and Manual PDF Repair.md` — the most comprehensive OCR report: covers the evolution from freeform to structured OCR, the target-page-only invariant, workflow runtime, figure extraction, PDF rendering, targeted repair, and the manual validation loop. It connects the OCR arc to the workflow runtime and Geppetto provider infrastructure.

For the vector search arc specifically, start with `Projects/2026/06/03/ARTICLE - Goja Bleve - Native Search Bindings for JavaScript RAG Pipelines.md` — it explains the Go-backed wrapper pattern and build-tag-safe vector support that the other two goja-bleve files build upon.

---

## Report-format notes

- The first-batch report for this topic was already strong. This partition report adds: deeper reading of the TTC export schema (bot-facing views, base64 transport), the xgoja scripting layer, the full Book OCR quality lab methodology, the structured OCR production pipeline, and the goja-bleve shipping/review-hardening details.
- The xgoja env directory contains two LLM-generated variant articles of the same content. Future scouts should read one and heading-scan the other to avoid redundant deep reads.
- The Book OCR arc has many closely related reports (8 files across 6 days). The 2026-05-26 project report is the most comprehensive; the others are best treated as evolutionary steps unless a specific earlier-stage decision needs tracing.
- Cross-topic bridges are dense for this partition: Geppetto/Pinocchio, SQLite, Go-backed DSLs, React component libraries, and retro macOS design all recur across 4+ topic slices.
