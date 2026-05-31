---
title: "RAG Evaluation Pipeline Architecture — Getting Started"
aliases:
  - RAG evaluation pipeline
  - RAG eval system
  - rag-eval architecture
  - TTC corpus pipeline
  - RAG intake pipeline
tags: [knowledge-base, on-ramp, rag, evaluation, sqlite, search, embedding, pipeline, workflow]
status: active
type: knowledge-base
created: 2026-05-31
repos:
  - /home/manuel/code/wesen/go-go-golems/rag-eval
---

# RAG Evaluation Pipeline Architecture — Getting Started

> [!summary]
> The RAG Evaluation System is a Go + SQLite + Glazed + HTTP + React system that makes RAG pipeline decisions inspectable. It stores every transformation — source, document, chunk, embedding, search index — as a first-class record so operators can evaluate retrieval quality. The intake pipeline flows `Source → Document → Chunk → Chunk Embedding → Search Index`. Two SQLite databases separate domain data (corpus DB) from workflow orchestration (engine DB). Chunk identity is strategy-aware: `(document_id, strategy_id, chunk_index)`. Embedding identity is provider+model+dimensions aware with SHA-256 `text_hash` freshness checks. BM25 indexes are disposable — derived from canonical chunks, rebuildable at any time. A scraper-backed workflow engine orchestrates the pipeline with leases, queues, dependencies, and retries.

## The architecture

The system has five layers, each backed by a shared Go service that both CLI commands and HTTP handlers call:

```
Sources          → scanner service, filesystem/Defuddle/WordPress dump
Documents        → ingest service, normalized text from source files
Chunks           → chunking service, strategy-aware identity
Embeddings       → embedding service, provider/model/dimensions identity + text_hash freshness
Search Indexes   → search service, BM25 + vector + hybrid RRF
```

### Two-database architecture

The system uses two SQLite databases with distinct responsibilities:

| Database | Contents | Purpose |
|---|---|---|
| **Corpus DB** | sources, documents, chunks, embeddings, preprocessing, enrichments | Domain data — the canonical artifacts |
| **Engine DB** | workflow runs, operations, dependencies, leases, retry state, compact results | Workflow orchestration — how the artifacts were produced |

The UI bridges both databases through separate API paths and merges data client-side. This separation means the corpus can be inspected without workflow metadata, and workflow state can be inspected without corpus details.

### Chunk identity is strategy-aware

A chunk is identified by `(document_id, strategy_id, chunk_index)`, not just `(document_id, chunk_index)`. The same document can be chunked by multiple strategies (fixed-size, sentence-boundary, semantic), and each strategy produces a different set of chunks. Chunk IDs hash `document_id`, `strategy_id`, and index.

This was discovered the hard way: the first implementation used `(document_id, chunk_index)` and a chunking termination bug caused an infinite loop because the system couldn't distinguish chunks from different strategies.

### Embedding identity is provider+model+dimensions aware

A stored vector is identified by `(chunk_id, strategy_id, provider, model, dimensions)` and protected by a SHA-256 `text_hash` freshness check. If the source text changes (re-chunked), the embedding is stale and must be recomputed.

The identity tuple prevents embedding model mismatch: if you switch embedding models without recomputing, vectors from different models would coexist in the index and produce wrong similarity scores. The `(provider, model, dimensions)` triple makes this a structural impossibility.

### BM25 indexes are disposable

BM25 indexes are derived from canonical SQLite chunks. They can be rebuilt from intake state at any time. The `search_indexes` table tracks metadata about when and how each index was built, but the index data itself is not canonical. Never treat BM25 indexes as irreplaceable data.

### Three retrieval modes

The search engine supports three retrieval modes:

| Mode | How it works | When to use |
|---|---|---|
| **BM25 lexical** | Full-text search over chunk text | Exact-match queries, known terms |
| **Vector search** | Cosine similarity over query embedding vs. stored embeddings | Semantic similarity, broader queries |
| **Hybrid RRF** | Reciprocal rank fusion of BM25 + vector results | General purpose, combines lexical and semantic signals |

### Scraper as workflow engine

The intake pipeline is orchestrated by a scraper-backed durable workflow system. Existing services remain canonical — workflow operations call `chunking.Service`, `embedding.Service`, `search.Service`, etc., rather than duplicating business logic.

The workflow engine provides:
- **Workflow runs**: named collections of operations
- **Operation specs**: typed, retry-safe operations (chunk, embed, index, preprocess, enrich)
- **Queues and leases**: operations are queued and claimed by workers with time-bounded leases
- **Dependencies**: an operation can depend on other operations completing first
- **Compact results**: operation outcomes stored as small JSON records, not full artifact data

### Document preprocessing and chunk enrichment

These are non-destructive derived artifacts:
- **Preprocessing**: LLM-based text cleanup (e.g., removing boilerplate, normalizing formatting) stored as a separate field, never overwriting source text
- **Enrichment**: LLM-based chunk metadata (e.g., summaries, keywords, categories) stored alongside chunks, not replacing them

Both are optional and tracked by provider identity so developers can switch between preprocessing providers (e.g., fake vs. openai-responses) to compare coverage.

## Why we do it this way

**Explicit identities make evaluation possible.** A RAG system is difficult to evaluate when its internal decisions are not stored in inspectable form. A query result is the final output of several earlier decisions: which documents were loaded, how text was extracted, how chunks were cut, which embedding model was used, how stale embeddings were detected, how text and vector search were combined. If these decisions are not first-class records, the system cannot answer basic evaluation questions.

**Strategy-aware chunk identity prevents termination bugs.** The first implementation used `(document_id, chunk_index)` and a chunking loop ran indefinitely because the system couldn't distinguish chunks from different strategies. The fix required explicit progress invariants and strategy-aware identity. The identity change was not cosmetic — it was a correctness fix.

**Two databases separate domain from orchestration.** A single database would mix "what are the chunks?" with "how were they produced?" That coupling makes it hard to inspect the corpus without workflow noise, and hard to debug workflows without corpus details. The two-database split lets each concern be inspected independently.

**Scraper orchestrates; services execute.** The workflow engine stores orchestration metadata and compact operation results. Canonical artifacts remain in the rag-eval SQLite database or disposable index directories. This separation means the workflow layer can be replaced (e.g., with a different queue system) without changing domain services.

**BM25 indexes are disposable because derived state should be rebuildable.** Canonical chunks live in SQLite. BM25 indexes are built from them. If an index is corrupted or outdated, rebuild it from intake state. This is the same principle as "generated files are rebuildable from source" — the chunks are the source, the index is the derived artifact.

## Evidence

| Report | Date | Contribution |
|---|---|---|
| [[ARTICLE - RAG Evaluation System - Workflow-Driven Retrieval Evaluation]] | 2026-05-27 | Canonical overview: Go+SQLite+Glazed+HTTP+React system, chunking termination bug, strategy-aware identity, service-layer tests |
| [[ARTICLE - RAG Evaluation System - Building a Database-Backed TTC Corpus Pipeline]] | 2026-05-28 | TTC WordPress dump → MySQL Docker → normalized SQLite → 3,096 documents, source-aware embedding coverage |
| [[ARTICLE - RAG Evaluation System - Corpus Explorer and Pipeline Visualization Website]] | 2026-05-28 | Corpus Explorer UI: identity bar, source panel, document browser, chunk timeline bar, coverage stats |
| [[ARTICLE - RAG Evaluation System - Search Retrieval Foundation Deep Dive]] | 2026-05-28 | Three retrieval modes: BM25, vector, hybrid RRF; smoke tests; corpus coverage gaps |
| [[ARTICLE - RAG Evaluation System - Intake Pipeline Deep Dive]] | 2026-05-29 | Strategy-aware chunk identity, provider-aware embedding identity, text_hash freshness, scraper workflow integration |
| [[ARTICLE - RAG Evaluation - Workflow Intake UI Architecture and Data Exploration]] | 2026-05-29 | Two-database architecture, operation grouping, cross-view navigation, artifact identity selection |
| [[PROJ - RAG Evaluation - Workflow Intake UI Implementation Report]] | 2026-05-30 | Op result inspection, artifact identity selector, preprocessing coverage per source, enrichment status per chunk |

## Working rules

1. **Always use strategy-aware chunk identity.** A chunk is `(document_id, strategy_id, chunk_index)`, never just `(document_id, chunk_index)`. The strategy is part of the chunk's identity, not an optional annotation.

2. **Always check embedding freshness via text_hash.** If source text changes (re-chunked), the embedding is stale. The `text_hash` field on embeddings enables detection of stale vectors before they produce wrong similarity scores.

3. **BM25 indexes are disposable.** Never treat them as canonical data — they can be rebuilt from intake state at any time. Track index metadata in `search_indexes` but don't treat the index files as irreplaceable.

4. **Group operations by (operation, status) in API responses.** A workflow with 6,236 individual operations returns 4 summary rows instead. This prevents context explosion in the UI.

5. **Let developers select artifact identity.** Replace hardcoded provider assumptions with a selector UI. Developers should be able to switch between preprocessing providers (e.g., fake vs. openai-responses) to see coverage for the identity that matters to them.

6. **Scraper handles orchestration; services handle business logic.** Workflow operations call `chunking.Service`, `embedding.Service`, `search.Service`, etc. — never duplicate logic in workflow runners.

7. **Every backend capability starts as a service method with a temporary-SQLite test.** CLI and HTTP are adapters over services. Unit tests do not call live embedding providers.

8. **Make writes rerun-safe by default.** Chunking, embedding, and indexing operations should be idempotent unless there is a clear reason not to. The text_hash freshness check makes embedding computation naturally idempotent.

9. **Bound all output and all provider calls by default.** Commands that can emit document text, chunk text, or vectors use bounded output. Large embedding batches should not be computed until coverage and source filters show the intended scope.

10. **Preprocessing and enrichment are non-destructive derived artifacts.** They never overwrite source text. They are tracked by provider identity so different preprocessing strategies can be compared.

## Gotchas

1. **Chunking termination bug.** The first implementation path exposed a bug where chunking could loop indefinitely. The fix required explicit progress invariants and strategy-aware chunk identity. If you write a new chunking strategy, verify that it terminates by checking that each iteration advances the chunk index.

2. **Embedding model mismatch.** If you switch embedding models without recomputing, vectors from different models coexist in the index and produce wrong similarity scores. The `(chunk_id, strategy_id, provider, model, dimensions)` identity prevents this structurally — but only if you actually query by the full identity tuple, not just chunk_id.

3. **Cross-view navigation is essential.** The Workflows tab must link to Corpus Explorer and back. Without it, developers can't trace artifacts from submission through consumption. The UI must bridge both databases through separate endpoints and merge client-side.

4. **Two databases means two API paths.** The corpus DB and engine DB have separate endpoints. The UI merges them client-side. If you add a new API endpoint, decide which database it targets and document that decision.

5. **BM25 field modeling matters for quality.** The default BM25 setup may not weight fields optimally for your corpus. Field-level boosting (title vs. body vs. metadata) can significantly improve exact-match performance.

6. **Corpus coverage gaps affect retrieval quality more than search tuning.** Most retrieval quality problems are not solved by tuning search first. They are solved by improving intake artifacts: better normalized text, better chunk provenance, appropriate chunk sizes, correct source scoping, and embedding coverage that makes missing or stale vectors visible before queries are run.

7. **Operation grouping prevents UI overload but hides individual failures.** A 6,236-op workflow returns 4 summary rows. To find the specific failed operations, you need to drill into the group. The API must support both summary and detail views.

8. **The scraper workflow lease timeout must be tuned for your workload.** If embedding provider calls are slow and the lease timeout is short, workers will lose their leases mid-operation. The retry mechanism will then re-queue the operation, potentially running it twice if the first attempt's side effects were not idempotent.

## Where to start as a new developer

Read these files in order:

1. `internal/db/db.go` — schema definitions, all table structures
2. `internal/ingest/scanner.go` — filesystem and Defuddle source scanning
3. `internal/chunking/chunker.go` — chunking strategies and the strategy-aware identity model
4. `internal/services/chunking/service.go` — chunking business logic
5. `internal/services/embedding/service.go` — embedding computation, provider resolution, text_hash freshness
6. `internal/services/search/bm25.go` — BM25 index building and querying
7. `internal/workflow/intake_runner.go` — scraper-backed workflow orchestration

Then run the smoke test:

```bash
rag-eval source create --name test --kind filesystem --path ./test-data
rag-eval document scan --source test
rag-eval chunk apply --strategy fixed-512
rag-eval embedding compute --provider openai --model text-embedding-small
rag-eval search index build --kind bm25
rag-eval search query "test query" --kind hybrid
```

## Related KB entries

- [[Tribal/sqlite-as-application-database]] — SQLite as application database in Go. The RAG system extends this with two-database architecture: corpus DB (domain data) + engine DB (workflow state).
- [[Tribal/dsl-normalized-config-compiled-plan]] — The DSL→Config→Plan pattern. The scraper workflow is a compiled plan: the intake spec is the DSL, the service operations are the plan, the workflow engine executes it.
- [[On-Ramp/go-cli-with-embedded-spa]] — Go CLI with embedded SPA. The RAG evaluation website follows this pattern: Go backend + React frontend + SQLite.
