---
title: "RAG Evaluation System: Intake Pipeline Deep Dive"
aliases:
  - RAG Eval Intake Pipeline
  - RAGEVAL Intake Side Deep Dive
  - RAG Evaluation System Indexing Chunking Embedding Pipeline
  - Intake Pipeline Deep Dive
tags:
  - article
  - project-report
  - rag
  - ingestion
  - chunking
  - embeddings
  - bm25
  - sqlite
  - geppetto
  - pinocchio
  - corpus
  - workflow
  - scraper
  - orchestration
  - durable-execution
status: active
type: article
created: 2026-05-29
repo: /home/manuel/workspaces/2026-05-27/rag-evaluation-system/2026-05-27--rag-evaluation-system
---

# RAG Evaluation System: Intake Pipeline Deep Dive

This report explains the intake side of the RAG Evaluation System: how source material becomes database documents, how documents become chunks, how chunks become embeddings, and how operators can run those stages from the CLI. It deliberately does not analyze the search side. Search, BM25, vector query retrieval, hybrid ranking, and smoke-query evaluation are separate layers built on top of the intake artifacts described here.

> [!note] 2026-05-29 workflow update
> The original version of this report described the direct CLI/service intake pipeline before scraper orchestration existed. The project has since been transformed into a scraper-backed durable workflow system. The section [[#Part II: Turning Intake Into a Durable Scraper Workflow System]] records that implementation in detail: custom runner integration, workflow submission, worker execution, preprocessing and enrichment artifacts, live-provider smoke testing, and browser visibility.

The current intake implementation is intentionally explicit. The project stores every major intermediate artifact in SQLite: source records, document records, chunking strategy records, chunks, and chunk embeddings. That persistence model is the central design decision. It makes the pipeline inspectable, rerunnable, and suitable for comparing different chunking and embedding configurations without hiding the intermediate state behind an opaque indexing job.

> [!summary]
> - Intake currently means `source -> document -> chunk -> chunk_embedding`, backed by SQLite tables and shared Go services used by both CLI and HTTP handlers.
> - There are two corpus acquisition paths: filesystem/Defuddle Markdown scanning and a database-backed The Tree Center WordPress/WooCommerce dump pipeline.
> - Chunk identity is strategy-aware: a chunk is identified by `(document_id, strategy_id, chunk_index)`, and chunk IDs hash `document_id`, `strategy_id`, and index.
> - Embedding identity is provider-aware and model-aware: a stored vector is identified by `(chunk_id, strategy_id, provider, model, dimensions)` and protected by a SHA-256 `text_hash` freshness check.
> - BM25 indexing is a derived, disposable index-building step over canonical SQLite chunks; the index can be rebuilt from intake state and is tracked in `search_indexes` metadata.
> - The intake pipeline now also has a scraper-backed durable workflow layer: `rag-eval/intake` operations wrap the same services, while scraper stores workflow state, dependencies, leases, retries, and compact operation results.
> - New developers should start by reading `internal/db/db.go`, `internal/ingest/scanner.go`, `internal/chunking/chunker.go`, `internal/services/chunking/service.go`, `internal/services/embedding/service.go`, `internal/services/search/bm25.go`, `internal/workflow/intake_runner.go`, `internal/workflow/submit.go`, and the RAGEVAL-001/RAGEVAL-002/RAGEVAL-004/RAGEVAL-006 diaries.

## Scope of this report

This document covers the intake pipeline only.

Included:

- source registration;
- filesystem scanning;
- Defuddle-based web corpus acquisition;
- WordPress/WooCommerce dump parsing into a normalized SQLite corpus;
- importing normalized corpus rows into the app database;
- document persistence;
- chunking strategy registration;
- fixed-size, sentence, and Markdown-heading chunk algorithms;
- chunk persistence, idempotency, and migration decisions;
- embedding provider resolution through Geppetto and Pinocchio profiles;
- embedding batch computation, freshness checks, vector encoding, coverage, and source filtering;
- BM25 index building over persisted chunks as the first lexical retrieval artifact;
- current CLI usage for indexing documents and computing embeddings;
- current implementation risks and next intake-side work.

Not included:

- BM25 query behavior and ranking-quality analysis;
- vector query search;
- hybrid search and reciprocal rank fusion;
- search UI behavior;
- benchmark metrics and retrieval evaluation;
- answer generation.

Those excluded pieces consume the intake artifacts, but they are not part of the intake side itself. BM25 index building is covered here only as a derived indexing artifact because it is the first place chunks are materialized into an external index directory; BM25 query semantics remain search-side behavior.

## The intake pipeline as implemented today

The pipeline is best described as a sequence of persisted transformations.

```mermaid
flowchart TD
    SourceInput[External source material]
    SourceRow[(sources)]
    DocumentRows[(documents)]
    StrategyRows[(chunking_strategies)]
    ChunkRows[(chunks)]
    Provider[Geppetto embedding provider]
    EmbeddingRows[(chunk_embeddings)]

    SourceInput --> SourceRow
    SourceInput --> DocumentRows
    SourceRow --> DocumentRows
    DocumentRows --> ChunkRows
    StrategyRows --> ChunkRows
    ChunkRows --> Provider
    Provider --> EmbeddingRows

    style SourceRow fill:#eef,stroke:#335,stroke-width:2px
    style DocumentRows fill:#eef,stroke:#335,stroke-width:2px
    style StrategyRows fill:#ffe,stroke:#773,stroke-width:2px
    style ChunkRows fill:#ffe,stroke:#773,stroke-width:2px
    style EmbeddingRows fill:#efe,stroke:#373,stroke-width:2px
```

The main implementation files are:

| Layer | File | Responsibility |
|---|---|---|
| Database bootstrap | `internal/db/db.go` | Opens SQLite, enables WAL, runs schema creation, defines canonical intake tables. |
| Database repair | `internal/db/migrations.go` | Upgrades older development databases whose `chunks` table lacked `strategy_id`. |
| Query layer | `internal/db/queries.go` | Implements upserts, chunk listing, embedding staleness checks, and embedding coverage queries. |
| Filesystem ingest | `internal/ingest/scanner.go` | Walks text-readable files, extracts simple metadata, and inserts `documents`. |
| Source service | `internal/services/source/service.go` | Shared source creation and scan behavior for CLI/HTTP. |
| Document service | `internal/services/document/service.go` | Shared document list/get/chunks behavior for CLI/HTTP. |
| Chunk algorithms | `internal/chunking/chunker.go` | Implements fixed, sentence, and Markdown-heading chunkers. |
| Chunk service | `internal/services/chunking/service.go` | Applies strategies, rebuilds derived chunks, and marks documents chunked. |
| Embedding provider resolver | `internal/services/embedding/provider.go` | Resolves direct or profile-backed Geppetto embedding providers. |
| Embedding service | `internal/services/embedding/service.go` | Computes and stores chunk embeddings with batching and staleness checks. |
| Vector encoding | `internal/services/embedding/vector.go` | Encodes `[]float32` vectors as little-endian SQLite BLOBs. |
| Corpus dump exporter | `ttmp/.../RAGEVAL-002/scripts/03-export-mysql-to-sqlite.py` | Converts the TTC WordPress dump into normalized corpus SQLite. |
| Corpus app importer | `ttmp/.../RAGEVAL-002/scripts/04-import-corpus-into-rageval.py` | Imports normalized corpus rows into the app `documents` table. |
| Sample chunking script | `ttmp/.../RAGEVAL-002/scripts/05-chunk-ttc-sample.sh` | Chunks representative guide/article/product documents. |

The pipeline is service-oriented. CLI commands and HTTP handlers are adapters. The important behavior lives in `internal/services/*`, which was a deliberate correction made after the early implementation duplicated behavior between CLI and HTTP.

## Historical decisions from the ticket diaries

The intake side did not appear fully formed. Several important decisions came from incidents and follow-up stabilization work recorded in the RAGEVAL diaries.

### RAGEVAL-001: start broad, then stabilize before embeddings

The original RAGEVAL-001 design planned a workflow-driven RAG evaluation system with scraping, extraction, chunking, embeddings, enrichment, indexing, and an interactive playground. The first implementation scaffolded the Go CLI/server, SQLite schema, React frontend, ingestion commands, and chunking commands.

The important event in the diary is the chunking incident. A fixed-size chunker with overlap could keep emitting tail chunks forever when the final capped end offset reached the document length and the next start moved backward by the overlap. The observed symptom was a memory spike and a killed process. The fix introduced three invariants:

- `chunk_size` must be positive;
- `overlap` must be non-negative;
- `overlap` must be smaller than `chunk_size`;
- once `end >= totalRunes`, chunking terminates.

That incident changed the implementation style. Future intake commands needed bounded output by default, service-layer tests, and idempotent writes before moving to embeddings.

### RAGEVAL-001 Step 4: strategy-aware chunk identity

The next major stabilization decision was making chunks first-class strategy artifacts. The earlier schema could not safely support multiple chunking strategies per document. The corrected schema added `strategy_id` to `chunks` and made the unique key `(document_id, strategy_id, chunk_index)`.

This decision matters because comparing chunking strategies is one of the reasons the project exists. A document may be chunked as `fixed-500-50`, `fixed-1200-150`, `sentence-1000-100`, or `markdown-heading`. Those chunks cannot share the same `(document_id, chunk_index)` identity.

The implementation also changed chunk IDs from document/index-based IDs to IDs that include strategy:

```text
chunk_id = "chk-" + sha256(document_id + ":" + strategy_id + ":" + chunk_index)[0:16]
```

That is implemented in `internal/chunking/chunker.go` around `generateChunkID`.

### RAGEVAL-001 Step 6: embeddings after service tests

Embeddings were added only after source, document, chunking, and migration tests existed. This was a good sequencing decision. Stored embeddings depend on stable chunk identity and rerun-safe chunk application. If chunks are ambiguous, all embedding rows become ambiguous.

The embedding implementation adopted Geppetto's provider interface and Pinocchio profile resolution. It stores vectors as SQLite BLOBs and uses a `text_hash` field to avoid recomputing fresh embeddings.

### RAGEVAL-002: realistic corpus acquisition

RAGEVAL-002 introduced the database-backed The Tree Center corpus path. The project needed more than small local files. The TTC dump path created a reproducible corpus with 483 articles, 19 guides, and 2,594 products. That corpus is then imported into the app database and chunked in bounded samples.

This ticket also clarified a separation that new developers should preserve:

- the normalized corpus database (`data/corpus/ttc-dump/ttc-corpus.sqlite`) is a source artifact;
- the app database (`data/rag-eval.db`) is the operational RAG database;
- importing from corpus SQLite into the app database is an explicit bridge step.

### RAGEVAL-003: expose intake artifacts visually

RAGEVAL-003 built the Corpus Explorer. Although this report is not about the UI, the UI work confirms the intake model. The website can inspect sources, documents, chunks, chunk boundaries, and embedding coverage because those artifacts are persisted separately and have explicit identities.

## SQLite as the intake state model

SQLite is the canonical state store for the current intake pipeline. `internal/db/db.go` opens the database with WAL mode, foreign keys enabled, a busy timeout, and `MaxOpenConns(1)`. That single-writer setting is appropriate for the current local tool because ingestion, chunking, and embedding writes are sequential operator actions.

The important intake tables are `sources`, `documents`, `chunking_strategies`, `chunks`, and `chunk_embeddings`.

```mermaid
erDiagram
    sources ||--o{ documents : owns
    documents ||--o{ chunks : split_into
    chunking_strategies ||--o{ chunks : produces
    chunks ||--o{ chunk_embeddings : embedded_as
    chunking_strategies ||--o{ chunk_embeddings : names_strategy

    sources {
        text id PK
        text name
        text type
        text config_json
        text created_at
        text updated_at
    }

    documents {
        text id PK
        text source_id FK
        text external_id
        text title
        text url
        text content_type
        text raw_content
        text content_text
        text content_html
        int word_count
        text metadata_json
        text status
    }

    chunking_strategies {
        text id PK
        text name
        text type
        text config_json
        text description
    }

    chunks {
        text id PK
        text document_id FK
        text strategy_id FK
        int chunk_index
        text text
        int token_count
        int start_offset
        int end_offset
        text boundaries_json
    }

    chunk_embeddings {
        text chunk_id FK
        text strategy_id FK
        text provider
        text model
        int dimensions
        text text_hash
        blob embedding
    }
```

### `sources`

A source is a named origin of documents. Examples from the current local database include:

- `thetreecenter-guides` for Defuddle-downloaded guide Markdown;
- `ttc-dump-articles` for dump-derived WordPress posts;
- `ttc-dump-guides` for dump-derived `ttc_guide` records;
- `ttc-dump-products` for dump-derived products.

The source record stores `id`, `name`, `type`, and `config_json`. Source creation is an upsert in `InsertSource`, so repeating a source creation command updates metadata instead of failing.

### `documents`

A document is the normalized text unit that can be chunked. The current schema stores both source and derived content fields:

- `raw_content`: original raw representation when available;
- `content_text`: the text used for chunking and embeddings;
- `content_html`: HTML source when available;
- `metadata_json`: corpus-specific details that do not yet deserve first-class columns;
- `status`: currently values such as `extracted` and `chunked`.

Document insertion is an upsert in `InsertDocument`. The filesystem scanner and TTC importer both rely on this to make repeated ingestion safe.

### `chunking_strategies`

A strategy records how chunks were produced. `internal/services/chunking/service.go` constructs the strategy ID from CLI settings when the user does not provide one:

```text
strategy_id = "{strategy}-{chunk_size}-{overlap}"
```

Examples:

- `fixed-500-50`;
- `fixed-1200-150`;
- `sentence-1000-100`;
- a custom `--strategy-name` if provided.

The strategy row stores JSON configuration:

```json
{
  "type": "fixed",
  "chunk_size": 1200,
  "overlap": 150
}
```

### `chunks`

A chunk is derived text. It belongs to one document and one strategy. It stores:

- stable chunk ID;
- document ID;
- strategy ID;
- chunk index;
- text;
- estimated token count;
- rune start offset;
- rune end offset;
- `boundaries_json`.

The current `boundaries_json` is minimal and stores `strategy_id`. More detailed boundary metadata could be added later, especially for sentence and Markdown heading chunkers.

### `chunk_embeddings`

An embedding row stores the vector for one chunk under one embedding identity:

```text
(chunk_id, strategy_id, provider, model, dimensions)
```

The stored vector is a BLOB containing little-endian float32 values. The row also stores `text_hash`, a SHA-256 hash of the chunk text at compute time. That hash is the freshness mechanism: if the chunk text has not changed and `--force` is not set, compute skips that chunk.

## Source creation and filesystem scanning

The generic filesystem path begins with `rag-eval source create` and `rag-eval source scan`.

```bash
./rag-eval source create \
  --db data/rag-eval.db \
  --id my-docs \
  --name "My Documents" \
  --type filesystem \
  --config '{}'

./rag-eval source scan \
  --db data/rag-eval.db \
  --source-id my-docs \
  --dir ./docs
```

The source CLI command calls `internal/services/source.Service.Create`, which validates `id`, `name`, and `type`, marshals the config map, and calls `InsertSource`. The scan command calls `internal/services/source.Service.Scan`, which delegates to `internal/ingest.Scanner.ScanDir`.

`ScanDir` performs a deterministic directory walk:

1. walk the directory tree with `filepath.WalkDir`;
2. skip hidden directories and hidden files;
3. accept only known text-readable extensions;
4. read each file into memory;
5. compute a relative path from the scan root;
6. compute a stable document ID from `sourceID + ":" + relPath`;
7. extract a title from the first Markdown `# ` heading or fallback to filename;
8. compute word count with `strings.Fields`;
9. insert or update the document row.

The stable document ID matters. It lets repeated scans update the same document instead of creating duplicates:

```text
doc_id = "doc-" + sha256(source_id + ":" + relative_path)[0:16]
```

The scanner currently treats text parsing simply. It does not parse frontmatter into metadata, does not render Markdown, and does not strip HTML except in corpus-export scripts. For filesystem sources, `raw_content` and `content_text` are both set to the file content. That is a deliberate early-stage choice: the app stores source text with minimal transformation so the chunker sees exactly what the scanner read.

The supported extension set is defined in `isTextFile` in `internal/ingest/scanner.go`. It includes Markdown, text, code files, JSON/YAML/TOML, HTML/XML/SVG, SQL, CSS, CSV, and common script formats.

## Defuddle-based web corpus acquisition

The Defuddle path is a scripted acquisition stage outside the app's Go code. It is used for public website pages where the desired input is readable Markdown extracted from rendered HTML.

The script is:

```text
ttmp/2026/05/27/RAGEVAL-001--rag-evaluation-system-workflow-driven-document-indexing-with-interactive-playground/scripts/03-download-thetreecenter.py
```

It reads public WordPress sitemaps advertised by The Tree Center:

- `https://www.thetreecenter.com/wp-sitemap-posts-ttc_guide-1.xml` for guides;
- `https://www.thetreecenter.com/wp-sitemap-posts-post-1.xml` for blog posts.

The script is intentionally bounded:

- `--types guides|posts|all` selects which sitemap partitions to use;
- `--max N` limits processed pages;
- `--delay 1.0` rate-limits downloads;
- `--dry-run` prints URLs without downloading;
- existing files are skipped unless `--force` is supplied;
- a JSONL manifest records each attempted page.

The core extraction command is:

```bash
defuddle parse <url> --md
```

The script also tries:

```bash
defuddle parse <url> -p title
```

Each downloaded file receives YAML frontmatter with title, source URL, site, source type, and extraction tool. After download, the normal app ingestion path scans the Markdown files:

```bash
./rag-eval source create \
  --id thetreecenter-guides \
  --name "The Tree Center Guides" \
  --type filesystem

./rag-eval source scan \
  --source-id thetreecenter-guides \
  --dir data/corpus/thetreecenter/guides
```

The diary records that all 19 guide pages were downloaded and scanned. Chunking those guide documents with `fixed-1200-150` produced 226 chunks across 19 documents.

This path is useful for validating public-page extraction quality. It is not the best source for full product metadata because rendered pages do not necessarily expose all WordPress/WooCommerce fields in a structured way.

## Database-backed TTC corpus parsing

The database-backed corpus path is more involved but more reproducible for The Tree Center.

The input file is:

```text
/home/manuel/code/ttc/ttc/ttc_dev_dump.sql.bz2
```

The pipeline stages are:

```mermaid
flowchart TD
    Dump[Compressed MySQL dump]
    Inspect[Bounded dump inspection]
    MySQL[Isolated MySQL 8]
    Export[Python export script]
    Corpus[(ttc-corpus.sqlite)]
    Import[Python app import script]
    App[(data/rag-eval.db)]

    Dump --> Inspect
    Dump --> MySQL
    MySQL --> Export
    Export --> Corpus
    Corpus --> Import
    Import --> App
```

The implementation uses MySQL as an intermediate execution environment rather than trying to translate MySQL dump syntax directly into SQLite. That decision avoided reimplementing MySQL-specific dump semantics, character set declarations, large multi-row inserts, and WordPress-specific storage quirks.

### Dump inspection

The first script, `01-inspect-dump-schema.py`, was introduced because raw shell inspection was unsafe. A MySQL dump can place many inserted rows on one line, so `grep` can print enormous lines. The bounded script streams the compressed file and writes controlled summaries.

The relevant counts were:

| Content type | Published rows |
|---|---:|
| WordPress posts (`post`) | 483 |
| TTC guides (`ttc_guide`) | 19 |
| Products (`product`) | 2,594 |

These became the first three corpus kinds: `article`, `guide`, and `product`.

### MySQL import

The second stage uses an isolated MySQL 8 Docker Compose service under the ticket scripts. The diary records several operational fixes:

- readiness must check authenticated `SELECT 1`, not `mysqladmin ping`, because MySQL initialization has a temporary server phase;
- dump warning text and GTID/log-bin statements had to be filtered before SQL import;
- `--binary-mode=1` was needed for import robustness.

Those details are important for developers who rerun the pipeline. They are encoded in the ticket script rather than left as oral knowledge.

### Export to normalized corpus SQLite

The export script is:

```text
ttmp/2026/05/28/RAGEVAL-002--extract-the-tree-center-content-dump-into-ordered-sqlite-corpus/scripts/03-export-mysql-to-sqlite.py
```

It uses the MySQL CLI to emit JSON rows through `JSON_OBJECT(...)`, then Python writes SQLite. No Python MySQL driver is required. The script had to use `mysql --raw` so JSON strings were not double-escaped in batch output.

The target SQLite tables are:

- `content_items` for article/guide/product primary records;
- `item_terms` for taxonomy terms;
- `product_meta` for selected product fields.

The text extraction algorithm for `content_items.content_text` is deliberately simple and inspectable:

1. parse HTML with a custom `HTMLParser` subclass;
2. ignore `script`, `style`, and `noscript` content;
3. add newlines around block-like tags such as paragraphs, headings, divs, sections, articles, and list items;
4. unescape HTML entities;
5. normalize CRLF to LF;
6. collapse repeated spaces;
7. collapse excessive blank lines;
8. join title, excerpt, and extracted post content.

Product metadata is selected from WordPress postmeta keys:

- `_treeinfo_botanical_name`;
- `_treeinfo_hardiness_zone`;
- `_treeinfo_mature_height`;
- `_treeinfo_mature_width`;
- `_treeinfo_sunlight`;
- `_treeinfo_soil_conditions`;
- `_treeinfo_drought_tolerance`;
- `_thumbnail_id`.

WooCommerce lookup metadata supplies SKU, price range, and stock status from `wp_wc_product_meta_lookup`.

The output is:

```text
data/corpus/ttc-dump/ttc-corpus.sqlite
```

The export result recorded in the diary was:

| Kind | Items | Words |
|---|---:|---:|
| article | 483 | 605,850 |
| guide | 19 | 37,594 |
| product | 2,594 | 2,208,648 |

### Import into app database

The importer is:

```text
ttmp/2026/05/28/RAGEVAL-002--extract-the-tree-center-content-dump-into-ordered-sqlite-corpus/scripts/04-import-corpus-into-rageval.py
```

It bridges `content_items` into the app's `sources` and `documents` tables. It creates one source per kind:

- `ttc-dump-articles`;
- `ttc-dump-guides`;
- `ttc-dump-products`.

The imported app document ID is the corpus item ID, such as:

```text
ttc-guide-398454
ttc-article-12345
ttc-product-3708
```

This direct reuse of corpus IDs is an important traceability decision. A document can be traced back to the normalized corpus row and then to the WordPress ID.

The importer is rerun-safe. It uses `ON CONFLICT(id) DO UPDATE` for documents and `ON CONFLICT(id) DO UPDATE` for sources. That matches the rest of the intake philosophy: repeated operator commands should update canonical records rather than create duplicates.

One current limitation is product text composition. The importer currently writes `content_items.content_text` directly into app `documents.content_text`. RAGEVAL-005 identifies this as the next data-quality problem: product search and product embeddings will remain weaker until product metadata and taxonomy terms are deliberately composed into searchable text.

## Chunking as a derived-state operation

Chunking is the transformation from `documents.content_text` to `chunks`. It is derived state. The same document can be chunked with multiple strategies, and the same strategy can be safely rerun.

The CLI shape is:

```bash
./rag-eval chunk apply \
  --db data/rag-eval.db \
  --doc-id <document-id> \
  --strategy fixed \
  --chunk-size 1200 \
  --overlap 150 \
  --emit preview \
  --limit 20
```

Available strategies are:

- `fixed`;
- `sentence`;
- `markdown-heading`.

The shared service is `internal/services/chunking.Service.Apply`. It performs these steps:

1. validate document ID;
2. default strategy to `fixed`;
3. default chunk size to `500` when zero;
4. read `documents.content_text` with `GetDocumentContent`;
5. choose a strategy ID from `--strategy-name` or `{strategy}-{chunk_size}-{overlap}`;
6. upsert a `chunking_strategies` row with JSON config;
7. instantiate the chunker via `NewChunkerFromType`;
8. split the document text into chunks;
9. delete existing chunks for exactly `(document_id, strategy_id)`;
10. insert new chunks;
11. update document status to `chunked`;
12. return a summary and optional chunk rows.

The delete-before-insert behavior is important. It makes repeated chunking runs idempotent for one document/strategy pair. It also means that rechunking can delete downstream data through foreign-key cascades. Since `chunk_embeddings.chunk_id` references `chunks(id) ON DELETE CASCADE`, replacing chunks can remove associated embeddings. That is the correct behavior for derived state, but developers should be aware of it before running large rechunk operations.

## Fixed-size chunking algorithm

The fixed-size chunker is implemented in `internal/chunking/chunker.go` by `FixedSizeChunker.Chunk`.

Inputs:

- `ChunkSize`: target size in characters, implemented as runes;
- `Overlap`: overlap in runes;
- `StrategyID`: strategy identity for chunk IDs.

Validation:

```text
chunk_size > 0
overlap >= 0
overlap < chunk_size
```

Algorithm:

```text
runes = []rune(text)
start = 0
index = 0

while start < len(runes):
    end = min(start + chunk_size, len(runes))
    chunk_text = string(runes[start:end])
    emit chunk(index, start, end, chunk_text)

    if end >= len(runes):
        break

    next_start = end - overlap
    if next_start <= start:
        next_start = start + 1
    start = max(next_start, 0)
    index++
```

The terminal check is not optional. It fixes the earlier infinite-tail bug. Without `if end >= totalRunes: break`, a final chunk can reach document end, subtract overlap, and emit another final chunk repeatedly.

The implementation uses runes, not bytes, for offsets. `StartOffset` and `EndOffset` are rune offsets. That is safer for Unicode text than byte slicing, but developers should not treat these offsets as byte offsets into the original string.

Token count is estimated as:

```text
token_count = rune_count(text) / 4
```

This is a rough English-text heuristic, not tokenizer output. It is useful for display and approximate sizing. It is not a provider-specific token count.

Fixed-size chunking is the most tested and most used strategy so far. The TTC sample uses `fixed-1200-150`, which produced manageable chunks for guides, articles, and products.

## Sentence chunking algorithm

The sentence chunker targets chunk size while trying to end chunks at sentence-like boundaries. It is implemented by `SentenceChunker.Chunk` and `splitSentences`.

Sentence splitting is simple:

- append runes into a current buffer;
- if the rune is `.`, `!`, `?`, or newline, emit the current buffer as one sentence if non-empty;
- after the loop, emit remaining text.

This is not a language-aware sentence tokenizer. It does not handle abbreviations, decimal numbers, initials, ellipses, or quoted punctuation. It is a deterministic lightweight splitter.

Chunk assembly works as follows:

```text
current_text = ""
current_start = 0
chunk_start_offset = 0

for sentence in sentences:
    if rune_count(current_text) + rune_count(sentence) > chunk_size and current_text != "":
        emit trimmed current_text
        if overlap > 0 and current_text length > overlap:
            current_text = last overlap runes of current_text
            chunk_start_offset = current_start - rune_count(current_text)
        else:
            current_text = ""
            chunk_start_offset = current_start

    if current_text == "":
        chunk_start_offset = current_start
    current_text += sentence
    current_start += rune_count(sentence)

emit final current_text if non-empty
```

The overlap for sentence chunking is character/rune overlap, not sentence-count overlap. That means an overlapped chunk can begin in the middle of a sentence. A future implementation might prefer sentence-level overlap, but the current behavior is consistent with fixed-size overlap semantics.

Sentence chunking is useful when preserving sentence boundaries matters more than exact chunk size. New developers should treat it as a simple baseline, not as a production-quality linguistic segmenter.

## Markdown-heading chunking algorithm

The Markdown-heading chunker is implemented by `MarkdownHeadingChunker.Chunk` and `splitMarkdownSections`.

The section splitter:

1. split text by newline;
2. when a trimmed line starts with `#` and there is already accumulated text, emit the previous section;
3. append the heading line to the new section;
4. emit the last section at the end.

A section is therefore a heading plus all content until the next heading. The algorithm does not parse Markdown formally. Any trimmed line beginning with `#` counts as a heading, including lines that might occur inside fenced code blocks. That limitation is acceptable for a first implementation but should be documented for code-heavy Markdown corpora.

Large sections are sub-chunked with the fixed-size chunker. The max section size is currently set in `NewChunkerFromType` as `chunk_size * 2` for the `markdown-heading` strategy. If a section exceeds that max, the code creates a fixed-size subchunker with overlap `100`, reduced to `maxChunkSize / 5` when needed to preserve the `overlap < chunk_size` invariant.

When subchunks are emitted, their offsets are shifted by the section offset so the final chunks use document-level offsets. The chunk index is reassigned in global order across all sections.

Markdown-heading chunking is useful for documentation corpora where headings define meaningful semantic units. It is less appropriate for HTML-derived product text without Markdown structure.

## Chunk IDs, offsets, and boundaries

Every chunk ID is deterministic for a document, strategy, and index:

```text
chk-{sha256(document_id:strategy_id:index)[0:16]}
```

This means rerunning the same chunking strategy over unchanged text produces the same IDs. If the document text changes, the algorithm may still emit chunks with the same IDs at the same indexes but different text. That is why embeddings also store `text_hash` and why rechunking deletes and rebuilds chunks for the strategy.

Offsets are rune offsets. They allow the UI to show approximate chunk positions and overlap intervals. The Corpus Explorer uses start/end offsets and chunk lengths to draw timelines and coverage strips.

`boundaries_json` is currently underused. It contains strategy ID. Future improvements could store:

- heading path for Markdown chunks;
- sentence boundary flags;
- overlap source range;
- parser version;
- normalization version;
- byte offsets in addition to rune offsets.

Adding these fields would make chunk provenance stronger without changing the core `chunks` schema.

## Embedding provider resolution

Embedding computation uses Geppetto's embedding provider interface. The resolver is `internal/services/embedding/provider.go`.

The project supports two provider configuration modes.

### Direct mode

Direct mode is used when no `--profile` or `--base-profile` is supplied. The CLI flags map directly to Geppetto embedding settings:

```bash
./rag-eval embedding compute \
  --strategy-id fixed-1200-150 \
  --embeddings-type ollama \
  --embeddings-engine nomic-embed-text \
  --embeddings-dimensions 768 \
  --base-url http://localhost:11434 \
  --limit 10
```

Defaults are:

- provider type: `ollama`;
- engine: `nomic-embed-text`;
- dimensions: `768`;
- cache type: `none`;
- cache directory: `state/embedding-cache`.

If an API key is provided, it is inserted into the API settings under provider-specific keys. For OpenAI, it also maps to `openai-api-key`.

### Profile-backed mode

Profile-backed mode is used when `--profile` or `--base-profile` is supplied. It loads profile registries through Geppetto engineprofiles. If no registry is supplied, the default path is:

```text
~/.config/pinocchio/profiles.yaml
```

The diary records these profiles in the local Pinocchio setup:

| Profile | Provider | Model | Dimensions |
|---|---|---|---:|
| `openai-embedding-small` | OpenAI | `text-embedding-3-small` | 1536 |
| `openai-embedding-large` | OpenAI | `text-embedding-3-large` | 3072 |
| `ollama-nomic-embedding` | Ollama | `nomic-embed-text` | 768 |
| `ollama-all-minilm-embedding` | Ollama | `all-minilm` | 384 |

Profile usage:

```bash
./rag-eval embedding compute \
  --strategy-id fixed-1200-150 \
  --profile openai-embedding-small \
  --profile-registries ~/.config/pinocchio/profiles.yaml \
  --batch-size 5 \
  --limit 5 \
  --output table
```

The resolver validates inference settings for embeddings before constructing the provider. Provider construction does not necessarily make a network call. The network call happens when `GenerateBatchEmbeddings` is invoked.

## Embedding computation algorithm

The shared service is `internal/services/embedding.Service.Compute`.

Required inputs:

- strategy ID;
- embedding provider;
- provider type.

Optional inputs:

- source IDs;
- batch size;
- limit;
- force flag.

Algorithm:

```text
validate strategy_id
validate provider
batch_size = default 16 if <= 0
provider_type = "unknown" if empty
model = provider.GetModel()
validate model name and dimensions

chunks = ListChunksForStrategySources(strategy_id, source_ids, limit)

for chunk in chunks:
    hash = sha256(chunk.text)
    stored_hash = GetChunkEmbeddingTextHash(chunk.id, strategy_id, provider_type, model.name, model.dimensions)
    if stored_hash exists and stored_hash == hash and force == false:
        skipped_fresh++
    else:
        pending.append(chunk, hash)

for each batch in pending:
    texts = chunk.text for batch
    vectors = provider.GenerateBatchEmbeddings(ctx, texts)
    validate len(vectors) == len(batch)
    for each vector:
        validate len(vector) == model.dimensions
        blob = EncodeFloat32Vector(vector)
        UpsertChunkEmbedding(chunk_id, strategy_id, provider_type, model.name, model.dimensions, hash, blob)
        computed++
```

The freshness check is one of the most important details. It compares hashes for the exact embedding identity. A chunk can have several embeddings at once:

- OpenAI small, 1536 dimensions;
- OpenAI large, 3072 dimensions;
- Ollama Nomic, 768 dimensions;
- Ollama MiniLM, 384 dimensions.

A fresh OpenAI small embedding says nothing about whether an Ollama Nomic embedding exists or is fresh.

The service stores vectors by upsert. If the row already exists but `text_hash` differs or `--force` is set, the vector is replaced and `updated_at` changes.

## Vector BLOB encoding

Vectors are stored as little-endian float32 values in a SQLite BLOB. The encoder is `EncodeFloat32Vector` in `internal/services/embedding/vector.go`:

```text
allocate len(vector) * 4 bytes
for each float32 value:
    write math.Float32bits(value) using binary.LittleEndian
```

The decoder verifies that the BLOB length is divisible by four and then reconstructs float32 values.

This representation is compact and deterministic. It is not self-describing. The dimensions are stored in the row key and validated by services that read the vector. If a row says `dimensions=1536`, the BLOB should decode to exactly 1536 float32 values.

## Source-aware embedding compute and coverage

Source-aware compute was added after the TTC dump corpus was imported. The reason was practical cost control. `fixed-1200-150` could contain scraped guides, dump articles, dump guides, and dump products at the same time. Strategy-only compute could accidentally process a much larger set than intended.

The compute command now accepts `--source-ids`:

```bash
./rag-eval embedding compute \
  --strategy-id fixed-1200-150 \
  --source-ids ttc-dump-guides \
  --profile openai-embedding-small \
  --profile-registries ~/.config/pinocchio/profiles.yaml \
  --batch-size 5 \
  --limit 10
```

The database helper joins `chunks` to `documents` and adds `d.source_id IN (...)` when source IDs are supplied.

Coverage is a read-only count operation. It does not call providers:

```bash
./rag-eval embedding coverage \
  --strategy-id fixed-1200-150 \
  --provider-type openai \
  --model text-embedding-3-small \
  --dimensions 1536 \
  --output table
```

It groups by source and reports:

- total chunks;
- embedded chunks;
- missing chunks.

The diary recorded coverage after the mixed TTC OpenAI smoke:

| Source | Chunks | Embedded | Missing |
|---|---:|---:|---:|
| `thetreecenter-guides` | 226 | 5 | 221 |
| `ttc-dump-articles` | 162 | 10 | 152 |
| `ttc-dump-guides` | 42 | 10 | 32 |
| `ttc-dump-products` | 51 | 10 | 41 |

Coverage currently counts stored rows. It does not recompute text hashes to report stale rows. Freshness is enforced during compute, not during coverage. A future coverage implementation could load chunk text and classify rows as fresh, stale, or missing.

## BM25 indexing as a derived artifact

BM25 indexing sits at the boundary between intake and search. Query execution, ranking interpretation, and retrieval-quality analysis belong to the search side. Index construction, however, is an intake-adjacent materialization step: it reads canonical chunks from SQLite, writes a derived index directory on disk, and records metadata in SQLite so operators know which chunk strategy and source filters produced the index.

The implementation is in `internal/services/search/bm25.go`, with CLI wiring in `cmd/rag-eval/cmds/search/index.go` and database helpers in `internal/db/search_queries.go`. The service builds a Bleve index from persisted chunks. The index is disposable because the canonical state remains in SQLite. If documents are reimported, chunks are rebuilt, or source filters change, the correct response is to rebuild the BM25 index from the canonical tables.

The important design rule is:

```text
SQLite documents/chunks are source of truth.
Bleve BM25 index directories are derived state.
search_indexes rows describe derived indexes; they do not replace chunks.
```

### What goes into the BM25 index

The builder calls `ListChunksWithDocumentContext(strategyID, sourceIDs, limit)`. That query joins `chunks` to `documents` and returns the fields needed for indexing and result rendering:

- chunk ID;
- document ID;
- source ID;
- document title;
- document URL;
- strategy ID;
- chunk index;
- chunk text;
- token count;
- start offset;
- end offset.

The indexed document shape is represented by the internal `indexedChunk` struct:

```text
indexedChunk {
    chunk_id
    document_id
    source_id
    title
    url
    strategy_id
    chunk_index
    text
    token_count
    start_offset
    end_offset
}
```

Each Bleve document is keyed by the chunk ID. This means BM25 search returns chunk-level hits, not whole-document hits. That matches the rest of the system: chunks are the retrieval unit, documents are context, and sources are corpus partitions.

### Build algorithm

`Service.BuildBM25` is intentionally a rebuild operation rather than an incremental updater.

The algorithm is:

```text
validate strategy_id
source_ids = normalized source filters
index_id = provided index ID or derived from strategy/source filters
index_path = index_root/index_id

if index_path exists and force is false:
    fail and ask operator to use --force

chunks = ListChunksWithDocumentContext(strategy_id, source_ids, limit)

tmp_path = index_path + ".tmp"
remove tmp_path
create parent directory
create new Bleve index at tmp_path

batch = new Bleve batch
for each chunk:
    build indexedChunk record
    batch.Index(chunk_id, indexedChunk)
    every 500 chunks:
        flush batch

flush final batch
close index
if force:
    remove old index_path
rename tmp_path to index_path
upsert search_indexes metadata row
return counts
```

The temporary-directory pattern matters. The service writes a complete index into `index_path.tmp` first, closes it, then renames it into place. That avoids leaving a partially written final index path when a build fails. The current implementation still uses a local filesystem rename, so the source and destination should remain on the same filesystem.

The batch flush interval is 500 chunks. This keeps memory bounded while avoiding one disk write per chunk.

### Index identity and source filters

The index is scoped by chunking strategy and optional source filters. A typical TTC index build uses `fixed-1200-150` and selects article and guide sources:

```bash
./rag-eval search index \
  --db data/rag-eval.db \
  --strategy-id fixed-1200-150 \
  --source-ids ttc-dump-guides,ttc-dump-articles \
  --index-id bm25-ttc-guides-articles-fixed-1200-150 \
  --force \
  --output table
```

If `--index-id` is omitted, the service derives one from the strategy and source filters. Providing an explicit index ID is better for durable experiments because it makes later query and smoke-test commands easier to read.

The `--limit` flag exists for smoke builds:

```bash
./rag-eval search index \
  --strategy-id fixed-1200-150 \
  --source-ids ttc-dump-guides \
  --index-id bm25-guides-smoke \
  --limit 50 \
  --force
```

A limited index is not a benchmark-quality index. It is useful for validating that the indexer can read chunks, create a Bleve directory, and record metadata before processing a larger corpus.

### `search_indexes` metadata

After a successful build, `UpsertSearchIndex` writes a row to the `search_indexes` table. The row records:

- index ID;
- name;
- strategy ID;
- index type, currently `bm25`;
- index path;
- document count;
- chunk count;
- rebuild timestamp;
- status.

This table is metadata, not the index itself. The actual index lives under the index root, whose default is defined by the search service. In the current local project state, an example index path exists under:

```text
data/indexes/bm25/bm25-ttc-guides-articles-fixed-1200-150/
```

The metadata row lets CLI, HTTP, and future UI code find the index path and show which corpus slice was materialized.

### Why BM25 indexing belongs after chunking

BM25 indexing must happen after chunking because the index unit is a chunk. It should not index whole documents in the current design. Whole-document indexing would make search results harder to inspect and less consistent with embedding retrieval, which also operates on chunks.

The correct dependency order is:

```text
sources -> documents -> chunking_strategies -> chunks -> bm25 index
```

If chunking changes, the BM25 index is stale. If source filters change, the BM25 index is the wrong corpus slice. If document text changes and chunks are rebuilt, the BM25 index should be rebuilt. The current system does not automatically detect or rebuild stale BM25 indexes. Operators must rebuild with `--force` after intake changes.

### Query behavior is separate

`QueryBM25` uses the built index and searches the `text` field plus a boosted `title` field. That is useful to know when building an index because title and text must be present in the indexed record. The ranking behavior itself belongs to the search-side report.

For intake purposes, the key point is that the BM25 index contains enough stored fields for result rendering:

- chunk ID;
- document ID;
- source ID;
- title;
- URL;
- strategy ID;
- chunk index;
- text preview source.

This preserves the inspection loop. A BM25 hit can be traced back to a chunk row, then to a document row, then to a source row. That traceability is the same principle used for embeddings.

### Operational rules for BM25 indexing

Use these rules when building or changing BM25 indexes:

- Build BM25 only after the intended documents have been chunked with the intended strategy.
- Use explicit `--source-ids` for corpus-specific experiments.
- Use explicit `--index-id` for reproducible reports and smoke tests.
- Use `--limit` only for smoke builds, not for final comparisons.
- Use `--force` when rebuilding an existing index after intake changes.
- Treat the index directory as disposable derived state.
- Keep `search_indexes` metadata in sync by building through the service, not by manually creating Bleve directories.

## End-to-end CLI indexing workflow

A new developer should be able to run the intake path from an empty app database. The following sequence uses filesystem scanning first.

### 1. Build the CLI

```bash
go build -o rag-eval ./cmd/rag-eval
```

### 2. Create a source

```bash
./rag-eval source create \
  --db data/rag-eval.db \
  --id local-docs \
  --name "Local Docs" \
  --type filesystem \
  --config '{}'
```

### 3. Scan documents

```bash
./rag-eval source scan \
  --db data/rag-eval.db \
  --source-id local-docs \
  --dir ./docs \
  --output table
```

This inserts or updates document rows. The output lists document IDs.

### 4. Inspect documents

```bash
./rag-eval document list \
  --db data/rag-eval.db \
  --output table

./rag-eval document get \
  --db data/rag-eval.db \
  --id <document-id> \
  --output json
```

### 5. Chunk a document

```bash
./rag-eval chunk apply \
  --db data/rag-eval.db \
  --doc-id <document-id> \
  --strategy fixed \
  --chunk-size 1200 \
  --overlap 150 \
  --emit preview \
  --preview-runes 120 \
  --limit 20 \
  --output table
```

For no text output:

```bash
./rag-eval chunk apply \
  --db data/rag-eval.db \
  --doc-id <document-id> \
  --strategy fixed \
  --chunk-size 1200 \
  --overlap 150 \
  --emit none \
  --output table
```

### 6. List chunks

```bash
./rag-eval document chunks \
  --db data/rag-eval.db \
  --doc-id <document-id> \
  --emit preview \
  --limit 20 \
  --output table
```

### 7. List registered chunking strategies

```bash
./rag-eval chunk strategies \
  --db data/rag-eval.db \
  --output table
```

### 8. Compute embeddings through a Pinocchio profile

```bash
./rag-eval embedding compute \
  --db data/rag-eval.db \
  --strategy-id fixed-1200-150 \
  --profile openai-embedding-small \
  --profile-registries ~/.config/pinocchio/profiles.yaml \
  --batch-size 5 \
  --limit 5 \
  --output table
```

### 9. Check coverage

```bash
./rag-eval embedding coverage \
  --db data/rag-eval.db \
  --strategy-id fixed-1200-150 \
  --provider-type openai \
  --model text-embedding-3-small \
  --dimensions 1536 \
  --output table
```

### 10. Re-run compute safely

Repeating the same compute command should report fresh skips if text has not changed:

```text
considered=5
computed=0
skipped_fresh=5
```

Use `--force` only when you deliberately want to recompute stored vectors.

## End-to-end TTC dump intake workflow

The TTC dump path is a replayable ticket workflow.

### 1. Export normalized corpus SQLite

After the MySQL container is loaded through the ticket import script, export:

```bash
ttmp/2026/05/28/RAGEVAL-002--extract-the-tree-center-content-dump-into-ordered-sqlite-corpus/scripts/03-export-mysql-to-sqlite.py \
  --out data/corpus/ttc-dump/ttc-corpus.sqlite
```

### 2. Import corpus rows into app DB

```bash
ttmp/2026/05/28/RAGEVAL-002--extract-the-tree-center-content-dump-into-ordered-sqlite-corpus/scripts/04-import-corpus-into-rageval.py \
  --corpus data/corpus/ttc-dump/ttc-corpus.sqlite \
  --app-db data/rag-eval.db \
  --kinds article,guide,product
```

Expected imported document counts:

- 483 articles;
- 19 guides;
- 2,594 products.

### 3. Chunk a bounded representative sample

```bash
TTC_SAMPLE_PER_KIND=3 \
TTC_SAMPLE_CHUNK_SIZE=1200 \
TTC_SAMPLE_OVERLAP=150 \
ttmp/2026/05/28/RAGEVAL-002--extract-the-tree-center-content-dump-into-ordered-sqlite-corpus/scripts/05-chunk-ttc-sample.sh
```

The diary recorded:

| Source | Documents chunked | Chunks |
|---|---:|---:|
| `ttc-dump-articles` | 3 | 162 |
| `ttc-dump-guides` | 3 | 42 |
| `ttc-dump-products` | 3 | 51 |

### 4. Compute source-bounded embeddings

```bash
./rag-eval embedding compute \
  --strategy-id fixed-1200-150 \
  --source-ids ttc-dump-products \
  --profile openai-embedding-small \
  --profile-registries ~/.config/pinocchio/profiles.yaml \
  --batch-size 2 \
  --limit 2 \
  --output table
```

Use source filters for all live provider experiments on the TTC corpus. Products alone represent a much larger content volume than guides.

## Parsing and normalization decisions

The current project uses different parsing depths for different source paths.

### Filesystem scan parsing is minimal

For files scanned by `internal/ingest.Scanner`, the parser does not transform text beyond reading it and extracting a title. This keeps the scanner generic. It is suitable for Markdown, code, config files, and local text corpora.

Decision:

```text
raw_content = file bytes as string
content_text = file bytes as string
content_html = ""
```

The title rule is:

```text
first line whose trimmed text starts with "# " -> title
otherwise filename without extension -> title
```

### Defuddle parsing is external and Markdown-oriented

For website pages, Defuddle performs the page cleanup and Markdown extraction. The app then treats the Markdown files as filesystem documents. This decouples web extraction from app ingestion.

Decision:

```text
web page -> defuddle markdown file -> normal source scan
```

### TTC dump parsing is corpus-specific

For the WordPress/WooCommerce dump, parsing occurs in the export script. It strips HTML, stores HTML, preserves metadata, and separates taxonomy/product metadata into side tables.

Decision:

```text
WordPress operational tables -> normalized corpus SQLite -> app documents
```

The app importer currently does not enrich product `content_text` from `product_meta` and `item_terms`. RAGEVAL-005 identifies that as a next step. The right fix is likely to compose product text in `04-import-corpus-into-rageval.py`, because the normalized corpus should remain a faithful export while the app import can define retrieval-oriented text.

## Idempotency and rerun behavior

The current intake side is designed so common operator commands can be repeated.

| Operation | Rerun behavior |
|---|---|
| `source create` | Upserts source by ID. |
| `source scan` | Upserts documents by stable source/path document ID. |
| TTC corpus import | Upserts sources and documents by stable corpus IDs. |
| `chunk apply` | Deletes and rebuilds chunks for exactly one document/strategy pair. |
| `embedding compute` | Skips rows whose stored text hash is fresh unless `--force` is set. |
| `embedding coverage` | Read-only count operation. |

The main non-obvious behavior is chunk rebuilding. Rechunking a document/strategy pair deletes old chunks. Because embeddings reference chunks with cascade delete, those embeddings can disappear. This is desirable when chunks change, but operators should run coverage after rechunking and before assuming embeddings still exist.

## Bounded output decisions

The diaries repeatedly emphasize bounded output. This came from the early chunking incident and from large corpus work.

Current bounded-output mechanisms include:

- `chunk apply --emit preview|full|none`;
- `chunk apply --limit N`;
- `chunk apply --preview-runes N`;
- `document chunks --emit preview|full|none`;
- `document chunks --limit N`;
- `embedding compute --limit N`;
- `embedding compute --batch-size N`;
- `embedding compute --source-ids ...`;
- `embedding coverage` as a safe read-only planning command;
- TTC downloader `--max`, `--delay`, `--dry-run`;
- TTC sample chunking `TTC_SAMPLE_PER_KIND`.

New intake commands should follow this pattern. Any command that can emit document text, chunk text, provider calls, or many rows should have a bounded default and an explicit expansion flag.

## Current tests that protect intake behavior

The important tests are:

- `internal/chunking/chunker_test.go` for chunker behavior and overlap safety;
- `internal/db/migrations_test.go` for upgrading legacy chunks without `strategy_id`;
- `internal/services/source/service_test.go` for source creation and scan idempotency;
- `internal/services/chunking/service_test.go` for rerun-safe chunk application and multiple strategies;
- `internal/services/document/service_test.go` for document list/get/chunks behavior;
- `internal/services/embedding/service_test.go` for fake-provider compute, staleness, source filtering, and coverage;
- `internal/services/embedding/vector_test.go` for vector encoding/decoding;
- `internal/services/embedding/provider_test.go` for provider resolver validation behavior.

The recommended validation command for intake-side changes is:

```bash
GOMAXPROCS=2 GOMEMLIMIT=1024MiB \
  go test ./internal/db ./internal/ingest ./internal/chunking \
    ./internal/services/source ./internal/services/chunking \
    ./internal/services/document ./internal/services/embedding \
    -count=1 -timeout 60s
```

Then build:

```bash
GOMAXPROCS=2 GOMEMLIMIT=1024MiB go build ./cmd/rag-eval
```

If frontend Corpus Explorer behavior is affected, also build the web app and rebuild the Go binary that embeds it:

```bash
cd web && npm run build
cd .. && go build ./cmd/rag-eval
```

## What a new developer should read first

Read in this order:

1. `internal/db/db.go` to understand the schema and SQLite setup.
2. `internal/db/queries.go` to understand upserts, chunk listing, and embedding persistence.
3. `internal/ingest/scanner.go` to understand filesystem document creation.
4. `internal/chunking/chunker.go` to understand chunk algorithms and IDs.
5. `internal/services/chunking/service.go` to understand chunk application as derived-state rebuild.
6. `internal/services/embedding/provider.go` to understand Geppetto/Pinocchio provider resolution.
7. `internal/services/embedding/service.go` to understand batch compute and freshness.
8. RAGEVAL-001 diary steps 3 through 12 to understand why the implementation is shaped this way.
9. RAGEVAL-002 diary to understand the TTC corpus path.
10. `ttmp/.../RAGEVAL-002/scripts/04-import-corpus-into-rageval.py` before changing product ingestion.

Do not start with search code if your task is intake-side work. Search consumes these artifacts and can obscure intake invariants.

## Important current limitations

### Product text is not yet product-aware enough

The normalized TTC corpus preserves product metadata, but app `documents.content_text` for products currently uses the exported content text directly. Product facts such as hardiness zone, mature size, sunlight, soil, drought tolerance, botanical name, and taxonomy terms should be composed into retrieval text before full product embeddings are computed.

RAGEVAL-005 recommends implementing this in `04-import-corpus-into-rageval.py` first.

### Sentence splitting is lightweight

The sentence splitter is punctuation-based. It is deterministic but not linguistically complete. For high-quality prose chunking, a better sentence boundary detector may be needed.

### Markdown heading splitting is not a full Markdown parser

Any trimmed line starting with `#` is treated as a heading. Code fences are not recognized. This is acceptable for current documentation use but can misbehave on Markdown files containing shell comments or code blocks.

### Token counts are estimates

The system estimates tokens as `rune_count / 4`. This is not model-specific. If provider context limits become important, add tokenizer-specific sizing.

### Embedding coverage does not classify stale rows

Coverage reports stored rows, not fresh rows. Compute skips fresh rows and updates stale rows, but coverage does not currently calculate stale counts.

### Workflow integration is now implemented

The original version of this report said that scraper workflow integration was not implemented yet. That limitation has now been removed. The intake pipeline has a Go-native scraper runner, durable workflow submission, local worker commands, document preprocessing artifacts, chunk enrichment artifacts, live-provider smoke coverage, read-only workflow/artifact APIs, and Workflows/Corpus Explorer UI affordances. See [[#Part II: Turning Intake Into a Durable Scraper Workflow System]] for the complete technical report.

## Future intake-side work

The strongest next tasks are:

1. Compose product-aware `content_text` during TTC app import.
2. Add an embedding planning command that reports missing/fresh/stale counts and estimated provider calls before compute.
3. Extend embedding coverage to classify stale rows by comparing current chunk text hashes.
4. Store richer `boundaries_json` for chunk provenance.
5. Add source filters to more document/chunk listing commands.
6. Add server-side document search/filtering for Corpus Explorer document lists.
7. Add a real migration version table before schema changes become long-lived.
8. Add workflow engine operations only after CLI semantics are stable.

## Working rules for intake changes

Use these rules when modifying the intake side:

- Preserve explicit identities. Documents, chunking strategies, chunks, and embeddings should remain separately addressable.
- Keep CLI and HTTP as adapters. Put behavior in shared services.
- Make writes rerun-safe unless there is a clear reason not to.
- Bound all output and all provider calls by default.
- Treat chunking and embeddings as derived state.
- Do not compute large embedding batches until coverage and source filters show the intended scope.
- Prefer preserving source data and adding derived fields over destructive normalization.
- Update tests whenever identity, offsets, hashing, or provider semantics change.

## Closing

The intake pipeline is now a coherent foundation for RAG experiments. It is not just an import script and an embedding command. It is a persistent transformation system with explicit state at every stage: sources, documents, chunking strategies, chunks, and embeddings. The implementation decisions came from practical failures and corpus work: stable IDs, strategy-aware chunks, text-hash freshness, source-aware embedding scope, bounded outputs, and replayable ticket scripts.

New developers should understand those decisions before adding features. Most future retrieval quality problems will not be solved by tuning search first. They will be solved by improving intake artifacts: better normalized text, better chunk provenance, appropriate chunk sizes, correct source scoping, and embedding coverage that makes missing or stale vectors visible before queries are run.


---

# Part II: Turning Intake Into a Durable Scraper Workflow System

The direct intake pipeline was already a good foundation before the workflow work began. It had the most important property a workflow system needs: each meaningful transformation was expressed as an idempotent service operation over explicit database state. `chunk_document` could rebuild chunks for a document and strategy. `compute_embeddings` could skip vectors whose `text_hash` was still fresh. `build_bm25` could rebuild a derived index from canonical SQLite chunks. The workflow project did not replace that model. It wrapped it.

That distinction is the central lesson of the work. A durable workflow engine should orchestrate domain operations, not become the place where domain logic is reimplemented. Scraper provides workflow runs, operation specs, queues, leases, retries, dependencies, and result storage. Rag-eval provides source, document, chunk, embedding, preprocessing, enrichment, and index semantics. The integration is successful because those responsibilities stay separate.

> [!summary]
> - The intake pipeline was transformed from direct CLI/service execution into a scraper-backed durable workflow system by adding a Go-native `rag-eval/intake` runner.
> - Existing services remained canonical. Workflow operations call `chunking.Service`, `embedding.Service`, `search.Service`, `documentprocessing.Service`, and `chunkenrichment.Service` rather than duplicating business logic.
> - The workflow engine stores orchestration metadata and compact operation results; canonical artifacts remain in the rag-eval SQLite database or disposable index directories.
> - Document preprocessing and chunk enrichment were added as non-destructive derived artifacts, preparing the system for LLM preprocessing and postprocessing without overwriting source text.
> - The system now has CLI submission/worker commands, backend workflow APIs, a Workflows UI, artifact coverage in Corpus Explorer, and a bounded live smoke using the `gpt-5-nano-low` profile.

## The problem with a direct-only intake pipeline

The first intake pipeline was intentionally explicit. An operator could run commands such as `rag-eval chunk apply`, `rag-eval embedding compute`, and `rag-eval search index`. Those commands were useful because they were understandable and debuggable. They also forced good service boundaries: if a command needed to chunk a document, the chunking behavior belonged in `internal/services/chunking`, not in Cobra code.

The weakness of direct-only execution appears when intake becomes a multi-stage pipeline. A realistic run is not one command. It is a collection of related operations: select documents, preprocess them, chunk them, compute embeddings, build lexical indexes, enrich chunks, and inspect failures. Some operations are CPU-bound. Some call external providers. Some should retry. Some should not retry. Some depend on all chunking operations finishing first. Some should fan out per document or per chunk.

A shell script can sequence those steps, but it cannot easily answer the questions a developer asks while the pipeline is running:

- Which documents have finished chunking?
- Which LLM calls failed, and are they retryable?
- Which operation produced this artifact?
- Did this embedding run skip fresh chunks or call the provider again?
- Can I retry one failed operation without rerunning the entire pipeline?
- Can the browser show progress without scraping terminal logs?

The scraper engine gives those questions a durable representation. A workflow is a row. An operation is a row. Dependencies are rows. Results and errors are rows. The scheduler leases ready operations and advances workflow status. Once intake work is represented this way, the UI can inspect the pipeline as a system rather than as a stream of terminal output.

## The architectural shape after the transformation

The new architecture has two databases and two kinds of state. The rag-eval database remains the canonical corpus and artifact store. The scraper engine database stores workflow orchestration state.

```mermaid
flowchart TD
    subgraph Operator[Operator surfaces]
        CLI[rag-eval workflow CLI]
        UI[Workflows and Corpus Explorer UI]
        Direct[Direct debug commands]
    end

    subgraph Engine[Scraper engine database]
        WF[(workflows)]
        OPS[(ops)]
        DEPS[(op_dependencies)]
        RES[(results)]
        LEASES[(leases)]
    end

    subgraph Runner[Go-native rag-eval/intake runner]
        Dispatch[operation dispatch]
        ChunkOp[chunk_document]
        EmbedOp[compute_embeddings]
        BM25Op[build_bm25]
        PreOp[preprocess_document]
        EnrichOp[enrich_chunk]
    end

    subgraph RagEvalDB[Rag-eval SQLite database]
        Docs[(documents)]
        Chunks[(chunks)]
        Embeds[(chunk_embeddings)]
        DocArtifacts[(document_processing_artifacts)]
        ChunkArtifacts[(chunk_enrichments)]
        SearchMeta[(search_indexes)]
    end

    CLI --> WF
    UI --> WF
    WF --> OPS
    OPS --> DEPS
    OPS --> Runner
    Runner --> RES
    Runner --> Docs
    Runner --> Chunks
    Runner --> Embeds
    Runner --> DocArtifacts
    Runner --> ChunkArtifacts
    Runner --> SearchMeta
    Direct --> Docs
    Direct --> Chunks
    Direct --> Embeds
    Direct --> DocArtifacts
    Direct --> ChunkArtifacts

    style Engine fill:#eef,stroke:#335,stroke-width:2px
    style RagEvalDB fill:#efe,stroke:#373,stroke-width:2px
    style Runner fill:#ffe,stroke:#773,stroke-width:2px
```

The important boundary is between `ops/results` and domain artifacts. Scraper result rows should answer, "What happened when this operation ran?" They should not become a second copy of all chunks, vectors, summaries, and indexes. Those artifacts already have canonical homes in rag-eval tables. The workflow result is therefore compact: counts, IDs, provider identity, model identity, index path, skipped-fresh flags, and error metadata.

## Phase 0: proving scraper could host a Go-native runner

The first implementation step was deliberately small. Before building intake workflows, the project needed to prove that the rag-eval repo could import scraper engine packages, register a custom runner, create an engine store, submit an operation, and execute it with `scheduler.RunOnce`.

The new package began in `internal/workflow`:

| File | Role |
|---|---|
| `internal/workflow/constants.go` | Defines the runner kind and queue names. |
| `internal/workflow/echo_runner.go` | Minimal custom runner used to prove scraper integration. |
| `internal/workflow/echo_runner_test.go` | Temporary SQLite scheduler test for the custom runner. |

The runner kind became:

```text
rag-eval/intake
```

The queue names became:

```text
rag-eval:cpu
rag-eval:llm
rag-eval:embedding
rag-eval:index
```

These names encode an important scheduling assumption. Intake is not one homogeneous workload. Chunking and BM25 indexing are local CPU/filesystem work. Embeddings and LLM preprocessing involve provider calls. Keeping those operations on distinct queues gives the scheduler room to apply different concurrency or rate-limit policies later.

The main dependency issue was not in rag-eval code. Importing scraper pulled in scraper's JavaScript/site packages, which expected a `go-go-goja` API version different from the one selected by the module graph. The practical fix was a temporary module replacement:

```text
replace github.com/go-go-golems/go-go-goja => github.com/go-go-golems/go-go-goja v0.4.16
```

This is a useful example of an integration spike doing its job. The spike was not only about code compiling; it revealed the dependency boundary between scraper's engine packages and scraper's JS runtime packages.

## Phase 1: wrapping existing services as durable operations

Once the custom runner worked, the next step was to replace the echo operation with real intake operations. The implementation lives primarily in:

- `internal/workflow/ops.go`
- `internal/workflow/intake_runner.go`
- `internal/workflow/intake_runner_test.go`

The runner decodes a typed `IntakeOpInput`, switches on `operation`, opens the rag-eval database, calls the relevant service, and returns a compact `model.OpResult`.

The dispatch shape is intentionally simple:

```go
switch input.Operation {
case OperationChunkDocument:
    return r.runChunkDocument(ctx, runCtx, input)
case OperationPreprocessDocument:
    return r.runPreprocessDocument(ctx, runCtx, input)
case OperationEnrichChunk:
    return r.runEnrichChunk(ctx, runCtx, input)
case OperationComputeEmbeddings:
    return r.runComputeEmbeddings(ctx, runCtx, input)
case OperationBuildBM25:
    return r.runBuildBM25(ctx, runCtx, input)
default:
    return opErrorResult(..."unknown_operation"...), nil
}
```

This is not clever code, and that is a feature. The workflow runner is a boundary adapter. It should validate the operation type, call domain services, classify errors enough for retry behavior, and get out of the way.

The first real operation was `chunk_document`. It calls `chunking.Service.Apply`, which already knows how to create a chunking strategy, delete/rebuild chunks for a document/strategy pair, and update document status. The workflow result records only the document ID, strategy ID, and chunk count.

`compute_embeddings` came next. It calls `embedding.Service.Compute`, but the runner introduces a provider resolver seam:

```go
type ProviderResolver func(ctx context.Context, input IntakeOpInput) (*embeddingservice.ResolvedProvider, error)
```

That seam is essential. Unit and integration tests should not call OpenAI or Ollama. The workflow tests inject deterministic fake providers, while real runs use the existing profile/direct provider resolver. This preserved test determinism without creating a second embedding implementation.

`build_bm25` wraps `search.Service.BuildBM25`. Its output records index ID, strategy ID, source IDs, index path, chunk count, document count, and whether the index was rebuilt. The index files themselves remain disposable derived state under the configured index root.

The first important correction in this phase was downstream scoping. If a workflow is submitted for `--document-ids doc-a,doc-b`, the embedding and BM25 operations must not process every chunk in the database with the same strategy. The fix propagated `DocumentIDs` through:

- `internal/db/queries.go`
- `internal/db/search_queries.go`
- `internal/services/embedding/service.go`
- `internal/services/search/bm25.go`
- `internal/workflow/intake_runner.go`

That change is easy to miss because it looks like a small filter addition. It is actually a correctness condition. Without it, a small workflow could trigger large provider or indexing work simply because the strategy name matched older chunks.

## Phase 2: turning the runner into an operator surface

A runner and tests are not enough. Operators need to submit workflows, run workers, and inspect state without writing Go code. Phase 2 added the workflow CLI:

```text
rag-eval workflow submit-intake
rag-eval workflow run-once
rag-eval workflow run-worker
rag-eval workflow status
rag-eval workflow ops
```

The reusable logic lives in `internal/workflow/submit.go` and `internal/workflow/engine.go`. The Cobra package in `cmd/rag-eval/cmds/workflow` is deliberately thin. It parses flags, calls the internal workflow service, and prints JSON.

The submission function builds a workflow topology. For each selected document it creates a `chunk_document` op. It can also create preprocessing ops, aggregate embedding ops, aggregate BM25 ops, and bounded enrichment ops. The first topology looked like this:

```mermaid
flowchart TD
    D1[document A]
    D2[document B]
    C1[chunk_document A]
    C2[chunk_document B]
    E[compute_embeddings]
    B[build_bm25]

    D1 --> C1
    D2 --> C2
    C1 --> E
    C2 --> E
    C1 --> B
    C2 --> B

    style E fill:#efe,stroke:#373,stroke-width:2px
    style B fill:#eef,stroke:#335,stroke-width:2px
```

This structure encodes a policy decision. Chunking fans out per document. Embedding and BM25 fan in after chunking. That is the right shape for current services because embedding compute and BM25 build already accept filters and operate across many chunks.

The worker helper centralizes scheduler construction:

```go
func NewIntakeScheduler(ctx context.Context, cfg WorkerConfig) (*sqlitestore.Store, *scheduler.Scheduler, error)
```

This function registers `IntakeRunner` and opens the scraper engine store. Both CLI commands and tests use it, which keeps runner registration consistent.

A Phase 2 smoke test submits a workflow against temporary rag-eval and scraper engine databases, runs scheduler cycles with a fake embedding provider, and verifies the workflow reaches `succeeded`. That test proves the same topology used by the CLI is executable under scraper.

## Phase 3: document preprocessing as non-destructive derived state

The original direct intake pipeline treated `documents.content_text` as canonical text. LLM preprocessing introduces a risk: if the system writes cleaned or summarized text back into `documents.content_text`, experiments become destructive. Different prompts, providers, and models would overwrite each other.

Phase 3 solved this by adding `document_processing_artifacts`:

```mermaid
erDiagram
    documents ||--o{ document_processing_artifacts : has

    documents {
        text id PK
        text content_text
    }

    document_processing_artifacts {
        text document_id PK
        text artifact_type PK
        text prompt_version PK
        text provider PK
        text model PK
        text input_hash
        text output_text
        text output_json
        text status
        text error_code
        text error_message
    }
```

The primary key is the experimental identity:

```text
(document_id, artifact_type, prompt_version, provider, model)
```

The `input_hash` is the freshness identity. If canonical document text changes, the stored artifact is no longer fresh even if the prompt and provider are the same.

The service lives in `internal/services/documentprocessing`. It has a provider interface, a deterministic fake provider, a `Process` method, and a `Coverage` method. The tests prove the most important invariant:

```text
documents.content_text is read as input but never overwritten.
```

The workflow op `preprocess_document` stores a compact result containing document ID, artifact type, prompt version, provider, model, input hash, status, and whether the artifact was skipped as fresh. A direct debugging command was added as well:

```text
rag-eval document preprocess --document-id DOC --provider fake
```

The point of the direct command is not convenience only. It preserves the escape hatch. If a workflow preprocessing op fails, a developer can reproduce the service call outside scraper.

## Phase 4: chunk enrichment as retryable postprocessing

Document preprocessing works at document granularity. Chunk enrichment works at chunk granularity. It prepares the system for summaries, topics, entities, and hypothetical questions attached to chunks.

The implementation uses the existing `chunk_enrichments` table and adds helpers in `internal/db/chunk_enrichment_queries.go`. The service lives in `internal/services/chunkenrichment`. Like document preprocessing, it begins with a fake provider and strict validation.

The validation is worth calling out. A provider result must contain:

- a non-empty short summary;
- a non-empty long summary;
- non-nil key topics;
- non-nil entities;
- non-nil hypothetical questions;
- a quality score in `[0, 1]`.

This is a contract for future live providers. LLM output is not trusted just because it is JSON-shaped. The service validates the semantic shape before storage.

The workflow op is `enrich_chunk`. It skips fresh enrichments by comparing the current chunk text hash to the stored `text_hash`. The direct command is:

```text
rag-eval chunk enrich --chunk-id CHUNK --strategy-id STRATEGY --provider fake
```

There is one deliberate limitation. Workflow submission can create bounded enrichment ops only for chunks that already exist at submission time:

```text
--skip-chunk-enrichment=false
--chunks-per-document-to-enrich 1
```

That is not dynamic fan-out. It is a safe first slice. Fully dynamic fan-out would require an operation that creates new operations after chunking completes. The current scraper integration can support that direction later, but Phase 4 kept the topology simple and inspectable.

## Phase 5: the first live-provider smoke

Fake providers prove correctness of orchestration and storage. They do not prove that profile resolution and network-backed provider execution work inside the workflow path. Phase 5 added a bounded live smoke using the requested `gpt-5-nano-low` Pinocchio profile.

The live provider lives in `internal/services/documentprocessing/live_openai.go`. It resolves Pinocchio/Geppetto profile settings, reads the OpenAI Responses engine, and sends a small preprocessing request. In this environment, the profile resolves as:

```text
gpt-5-nano-low profile -> gpt-5-nano OpenAI Responses engine
reasoning_effort: low
```

The direct smoke ran one document through live preprocessing:

```text
rag-eval document preprocess \
  --db data/rag-eval.db \
  --document-id ttc-product-682105 \
  --artifact-type live_smoke_clean_text \
  --prompt-version phase5-gpt-5-nano-low-v1 \
  --provider openai-responses \
  --profile gpt-5-nano-low \
  --force
```

Then a two-document workflow smoke ran live preprocessing plus chunking, with all other expensive or unnecessary work disabled:

```text
rag-eval workflow submit-intake \
  --engine-db state/rageval006-phase5-live.db \
  --db data/rag-eval.db \
  --workflow-id phase5-live-gpt5nano-low-001 \
  --document-ids ttc-product-682105,ttc-product-817621 \
  --strategy fixed \
  --chunk-size 32 \
  --overlap 4 \
  --skip-preprocessing=false \
  --preprocess-artifact-type live_smoke_clean_text \
  --preprocess-prompt-version phase5-gpt-5-nano-low-v1 \
  --preprocess-provider openai-responses \
  --preprocess-model gpt-5-nano-low \
  --skip-embeddings \
  --skip-bm25 \
  --skip-chunk-enrichment
```

The workflow completed with four operations succeeded: two preprocessing operations and two chunking operations. One preprocessing op skipped fresh output from the direct smoke; the second made a live provider call. This is exactly the behavior the freshness model was meant to produce.

The interesting failure was mundane but important:

```text
Error: ensure schema_migrations table: unable to open database file: no such file or directory
```

The cause was that `state/` did not exist before creating `state/rageval006-phase5-live.db`. The immediate fix was `mkdir -p state`. The design lesson is that the engine DB path should get the same parent-directory creation treatment as the rag-eval database path.

## Phase 6 and 7: visibility, control, and the browser workflow cockpit

Once workflows exist, developers need to see them. Phase 6 added backend visibility endpoints, and the later UI work turned those endpoints into a browser surface.

The backend added read-only endpoints first:

```text
GET /api/v1/workflows
GET /api/v1/workflows/{id}
GET /api/v1/workflows/{id}/ops
GET /api/v1/artifacts/document-processing/coverage
GET /api/v1/artifacts/chunk-enrichment/coverage
GET /api/v1/documents/{id}/processing-artifacts
GET /api/v1/chunks/{id}/enrichments
```

Then the workflow API grew control endpoints:

```text
GET  /api/v1/workflows/{id}/results/{opId}
POST /api/v1/workflows/{id}/retry/{opId}
POST /api/v1/workflows/{id}/cancel
POST /api/v1/workflows/intake
GET  /api/v1/queues
```

These are thin HTTP adapters over scraper `engineview` services and rag-eval workflow submission. The server command gained an `--engine-db` flag so the API can read the scraper workflow database:

```text
rag-eval serve --db data/rag-eval.db --engine-db state/rag-eval-workflows.db
```

The frontend work added a `Workflows` tab with a workflow list, queue health, a submit-intake modal, workflow detail, progress bar, op graph, grouped operation summary, and op inspector. The most important UI design correction was grouping operations instead of returning every op. A large workflow can produce thousands of chunk operations. Returning all of them to the browser is not a visibility feature; it is a failure mode.

The grouped response reduces the detail view to operation/status groups:

```text
operation=chunk_document, status=succeeded, count=3117
operation=compute_embeddings, status=ready, count=1
operation=build_bm25, status=ready, count=1
```

Each group carries a sample op for inspection. Future work can add paginated drill-down for all failed ops in a group.

Corpus Explorer also gained artifact visibility:

- Source panels show preprocessing coverage next to embedding coverage.
- Document detail has an `Artifacts` tab for document preprocessing outputs.
- Chunk rows show enrichment status.
- Artifact rows can link back to the Workflows tab, connecting derived data to the workflow that produced it.

This completes the loop: a workflow produces artifacts; artifacts appear in corpus views; corpus views can point back to workflow execution state.

## The final operation vocabulary

The runner now supports five operation types:

| Operation | Queue | Canonical service | Canonical artifact |
|---|---|---|---|
| `chunk_document` | `rag-eval:cpu` | `internal/services/chunking.Service` | `chunks` |
| `compute_embeddings` | `rag-eval:embedding` | `internal/services/embedding.Service` | `chunk_embeddings` |
| `build_bm25` | `rag-eval:index` | `internal/services/search.Service` | `search_indexes` + Bleve index directory |
| `preprocess_document` | `rag-eval:llm` | `internal/services/documentprocessing.Service` | `document_processing_artifacts` |
| `enrich_chunk` | `rag-eval:llm` | `internal/services/chunkenrichment.Service` | `chunk_enrichments` |

That table is the practical API of the workflow runner. Every new operation should be judged against the same standard: it should wrap an existing or newly created service, write canonical state outside scraper, return compact workflow metadata, and have a direct debugging path.

## Why the transformation worked

The transformation worked because the direct pipeline had already been disciplined into service boundaries. The workflow runner could call services because those services existed. The tests could inject fake providers because provider resolution was already separable. The UI could show progress because scraper already had durable rows for workflows and operations. The artifact views could exist because preprocessing and enrichment were stored as first-class tables rather than hidden in logs or overwritten text columns.

The core pattern is reusable:

```text
1. Make the domain operation idempotent and testable without a workflow engine.
2. Store the operation's real output in the domain database or artifact store.
3. Add a workflow op that calls the domain service and returns compact metadata.
4. Add fake-provider tests before live-provider tests.
5. Add a direct CLI/debug path for the same service call.
6. Add workflow submission only after operation semantics are stable.
7. Add API and UI visibility only after workflow state is meaningful.
```

This sequence prevents the workflow engine from becoming a place to hide unstable domain behavior. The engine coordinates work. It does not make unclear work clear.

## Failure modes and design lessons

### Dependency boundaries matter

The first scraper import exposed a `go-go-goja` compatibility problem. This was not an intake bug, but it affected intake workflow integration because the engine packages were not isolated from scraper's JS/site packages. The temporary replacement unblocked development, but the long-term dependency boundary still deserves review.

### Scope filters are cost controls

The document ID filter propagation for embeddings and BM25 was a correctness fix and a cost-control fix. Without it, a small workflow could process a large corpus. Any operation that calls a provider or builds an index must make its scope visible in the input contract.

### Freshness is better than timestamps

Both embeddings and preprocessing/enrichment artifacts use content hashes for freshness. Timestamps tell when a row was written. Hashes tell whether the input still matches the row. For rerunnable intake, hashes are the stronger invariant.

### Fake providers are not throwaway code

The fake providers are part of the architecture. They let tests prove orchestration, skip semantics, coverage, storage, and UI behavior without credentials. Live providers should be opt-in additions, not the only implementation path.

### Dynamic fan-out should be introduced carefully

The current enrichment fan-out selects existing chunks at submission time. That is safe but limited. A more powerful workflow could create chunk enrichment ops after chunking completes. That should be added only when the UI can explain it and the scheduler behavior is easy to inspect.

## What a new developer should read now

The original read list at the end of this article is still useful for understanding direct intake. For workflow-based intake, read in this order:

1. `internal/workflow/ops.go` for the operation input/output vocabulary.
2. `internal/workflow/intake_runner.go` for dispatch and service wrapping.
3. `internal/workflow/submit.go` for workflow topology construction.
4. `internal/workflow/engine.go` for scheduler construction and runner registration.
5. `cmd/rag-eval/cmds/workflow/*` for operator-facing workflow commands.
6. `internal/services/documentprocessing/service.go` and `live_openai.go` for preprocessing artifacts and the live smoke provider.
7. `internal/services/chunkenrichment/service.go` for strict chunk enrichment validation.
8. `internal/api/workflow_artifact_handlers.go` for workflow/artifact HTTP visibility.
9. `web/src/components/workflows/WorkflowsView.tsx` for browser workflow inspection and submission.
10. `web/src/components/corpus/DocumentInspector.tsx` and `web/src/components/corpus/SourcePanel.tsx` for artifact visibility in Corpus Explorer.

## Current status after the workflow transformation

The scraper workflow transformation is no longer just a design. It is implemented through the backend, CLI, live smoke path, API, and UI.

Completed capabilities:

- custom scraper runner registration;
- durable chunk, embedding, BM25, preprocessing, and enrichment operations;
- workflow submission and worker CLI;
- direct debug commands for preprocessing and enrichment;
- fake-provider workflow tests;
- bounded live `gpt-5-nano-low` preprocessing smoke;
- workflow status, ops, result, retry, cancel, queue, and submit APIs;
- Workflows UI with list, detail, op graph, queue health, and submit modal;
- Corpus Explorer artifact coverage and detail visibility.

Important remaining questions:

- Should `chunk_enrichments` include provider/model in its primary key before serious live experiments?
- Should dynamic fan-out be added for post-chunk enrichment workflows?
- Should the live OpenAI Responses provider move into a shared LLM provider abstraction instead of living under document preprocessing?
- Should workflow APIs normalize scraper model structs to stable snake_case DTOs before more frontend code depends on their current JSON shape?
- Should engine DB parent directory creation happen in the scraper store, rag-eval workflow helper, or CLI layer?

## Closing the loop

The project started with an explicit intake pipeline: sources, documents, chunks, embeddings, and indexes. The workflow work did not discard that foundation. It made the same transformations durable, inspectable, retryable, and visible. That is the right kind of workflow integration. It preserves direct debugging while adding orchestration.

A future developer should see two valid paths through the system. If they need to understand one operation, they can run the direct command and read the service. If they need to run a pipeline, they can submit a scraper workflow, watch it in the browser, inspect operation results, retry failures, and see the artifacts appear in Corpus Explorer. The workflow engine is now part of the intake system, but it is not the whole system. It is the durable execution layer around well-defined, testable transformations.
