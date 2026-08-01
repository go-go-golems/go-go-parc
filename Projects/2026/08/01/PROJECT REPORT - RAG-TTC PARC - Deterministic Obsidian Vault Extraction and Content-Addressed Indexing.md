---
title: "RAG-TTC PARC: Deterministic Obsidian Vault Extraction and Content-Addressed Indexing"
aliases:
  - RAG-TTC PARC indexing report
  - Deterministic Obsidian vault extraction
  - PARC content-addressed indexing
tags:
  - project-report
  - rag
  - obsidian
  - go
  - indexing
  - reproducibility
  - content-addressing
status: active
type: project-report
created: 2026-08-01
repo: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/rag-ttc
source_ticket: RAG-TTC-PARC-001
---

# RAG-TTC PARC: Deterministic Obsidian Vault Extraction and Content-Addressed Indexing

This report examines the first implementation step in `RAG-TTC-PARC-001`: converting the go-go-parc Obsidian vault into the corpus contract consumed by `rag-ttc indexes build`. The extractor is small, but it defines the identity of every later artifact. A path decision changes document identity. A normalization decision changes document content. A serialization decision changes the corpus digest. Those decisions must be explicit before generation and embedding begin.

The implementation lives in `scripts/parc-corpus/` in `/home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/rag-ttc`. It produces ordinary `rag.Document` values, writes `corpus.json` and a frontmatter sidecar, and leaves chunking, representations, embedding, retrieval, and answer generation to the existing RAG-TTC system. The live-vault smoke test produced 1,317 indexed Markdown notes. Running the extractor twice produced byte-identical corpus and sidecar files.

> [!summary]
> 1. The extractor establishes a stable document identity: the vault-relative POSIX path is both `Document.ID` and `source_uri`, while the normalized body receives a SHA-256 content digest.
> 2. Frontmatter is metadata, not searchable body text. The first sidecar preserves aliases, tags, and type; the title remains part of the document record.
> 3. Determinism is tested at two levels: sorted traversal and canonical JSON serialization, then a live-vault two-run comparison. The first indexing bundle is intentionally a later phase.
> 4. Historical notes with malformed unrelated YAML are accepted through a narrow recovery parser. The extractor still fails on an unclosed frontmatter block because the document boundary is then ambiguous.

## 1. Why the extractor is the first system boundary

The downstream RAG-TTC machinery already accepts a JSON corpus. `dataset.LoadDocuments` decodes an array of `rag.Document` values, rejects an empty corpus, and passes the documents to the index builder. The builder can then chunk the text, create raw or generated representations, embed those representations, build BM25 and vector indexes, and emit an immutable bundle. None of those components should know that the source documents originated in Obsidian.

The vault does not yet have a corpus identity. It has Markdown files, YAML frontmatter, directory structure, generated tool files, Obsidian links, attachment embeds, and historical notes written under different levels of YAML strictness. A direct recursive file read would create an unstable and semantically noisy input:

- File order would depend on filesystem traversal order.
- Frontmatter would be sent to chunking and retrieval even though it describes the note rather than its body.
- A note rename would be indistinguishable from a deletion followed by a new note if the ID were derived from content.
- Obsidian syntax would remain in lexical terms even when the visible link label is the useful retrieval text.
- A malformed field in one unrelated frontmatter key could prevent the entire corpus from being built.

The extractor therefore has one responsibility: produce a deterministic, minimal, explicit corpus representation. It does not attempt to resolve links, infer categories, summarize notes, choose chunk sizes, or judge retrieval quality. Those operations belong to later stages with their own identities and measurements.

## 2. System boundary and data flow

The source ticket describes five phases. The implementation in this report completes Phase 1 only.

```mermaid
flowchart TD
    VAULT[go-go-parc vault\nMarkdown notes + frontmatter] --> WALK[parc-corpus extractor\nordered selection]
    WALK --> PARSE[frontmatter parser\nstrict + owned-field recovery]
    PARSE --> NORMALIZE[body normalization\nstrip metadata, rewrite links, drop embeds]
    NORMALIZE --> CORPUS[datasets/parc/corpus.json\n[]rag.Document]
    PARSE --> SIDECAR[datasets/parc/frontmatter.json\npath -> aliases/tags/type]
    CORPUS --> BUILD[rag-ttc indexes build\nchunk, represent, embed, index]
    SIDECAR --> ARMS[later alias/tag representation\nand metadata filtering]
    BUILD --> BUNDLE[immutable RAG-TTC index bundle]
    BUNDLE --> QUERY[workspace/chat retrieval\nwith exact source hydration]
```

The extractor is deliberately outside `pkg/rag`. It is a source-specific adapter. The RAG domain model remains independent of Obsidian, while the PARC adapter records the source-specific normalization rules in one versionable command.

## 3. The vault input and selection policy

The design survey described a vault dominated by `Projects/` and `Research/`, with additional `Transcripts/`, `ttmp/`, `Logs/`, and `Tickets/` content. The first version includes those areas. The evaluation set, not a prior assumption, will decide whether transcripts should later use a separate population or retrieval channel.

The extractor selects regular files whose extension is exactly `.md`. It walks the vault with `filepath.WalkDir`, records relative paths, converts them to slash-separated form, and sorts them before reading documents. Sorting uses the normalized relative path rather than the host operating system's directory order.

Generated or operational directories are excluded before descent:

| Exclusion | Reason |
| --- | --- |
| `Attachments/` | Binary assets are outside the Markdown corpus and can be very large. |
| `scripts/` | The vault contains operational scripts, not durable note content, under this path. |
| `.obsidian/` | Obsidian application configuration is not knowledge content. |
| `.pi/` | Local Pi dependencies and generated documentation are tool artifacts. |
| `.git/` | Repository internals are not vault notes. |
| `.trash/` | Deleted material should not enter the active corpus. |
| `.publish/` | Publishing artifacts are derived output rather than source notes. |
| `favicon*` files | Site assets are not knowledge notes. |

The `.pi/` exclusion was added after the live-vault smoke test exposed 46 Markdown files under local JavaScript dependencies. The ticket's original survey predated that generated content. Excluding it keeps the corpus aligned with the vault's durable note areas.

The selection rule has a useful negative property: it does not exclude `ttmp/`, `Transcripts/`, or other ordinary Markdown directories in the first version. Those directories remain visible to the evaluation process, where their retrieval behavior can be measured rather than guessed.

## 4. Document identity and incremental refresh

Each selected file becomes one `rag.Document`:

| Field | Value | Purpose |
| --- | --- | --- |
| `id` | Vault-relative path with `/` separators | Stable identity across edits to the same path. |
| `source_uri` | Same relative path | Human-readable provenance without leaking an absolute machine path. |
| `title` | YAML `title`, or filename stem | Display title and document-level context. |
| `text` | Normalized Markdown body | Input to chunking and representation builders. |
| `content_digest` | SHA-256 of normalized text | Detects body changes and participates in downstream identity. |
| `metadata` | Omitted in v1 | Frontmatter fields are kept in the sidecar instead. |

The relative path is an intentional choice. If the ID were the content digest, every edit would produce a new document identity. The cache would lose the relationship between an edited note and its previous chunks, summaries, and embeddings. A path-based ID preserves that relationship while still allowing the content digest to invalidate the changed body.

The trade-off is explicit: a rename is a new document. The old path disappears, and the new path receives a new identity. This is preferable to silently treating a rename as an edit because a path is the user's durable locator inside the vault. If rename continuity becomes important, it should be implemented as a separate, explicit identity map rather than weakening the document contract.

The body digest is calculated after normalization. That means changing the extractor's normalization rules changes the content digest even when the source file bytes stay the same. This is correct: the searchable text changed. A normalization rule change must be treated as a new extractor version and should deliberately cause downstream cache misses.

## 5. Frontmatter is metadata, not retrieval text

Obsidian frontmatter commonly contains `title`, `aliases`, `tags`, `status`, `type`, `created`, and `repo`. The extractor removes the complete YAML block from the body. It uses `title` for the document record and writes the first sidecar schema with these fields:

```json
{
  "Projects/2026/05/13/example.md": {
    "aliases": ["OAuth Device Flow in Go CLI"],
    "tags": ["project-report", "oauth", "go"],
    "type": "project-report"
  }
}
```

The sidecar is keyed by the same relative document ID as the corpus. That relationship is important: a future alias or tag representation can hydrate to the note's chunks without inventing another source identity. A future metadata filter can use the sidecar without changing raw body bytes or invalidating raw representation identity.

The first implementation accepts both YAML list and scalar shorthand forms:

```yaml
aliases:
  - RAG evaluation

tags: [rag, evaluation]

aliases: RAG evaluation
```

It also handles a common YAML mistake in existing notes: an unquoted list item containing a colon. YAML parses `- Textbook: Retrieval` as a mapping node. For an aliases or tags list, the extractor recovers the intended string `Textbook: Retrieval`.

Some historical notes contain invalid YAML in fields the extractor does not own. For example, a scalar containing an unquoted colon can make the complete YAML document fail to parse even though `title`, `tags`, and `type` remain readable. When strict parsing fails, the extractor runs a narrow line-oriented recovery pass for those owned fields. It does not pretend that the entire frontmatter document was valid, and it does not import arbitrary malformed fields into the corpus. An unclosed frontmatter block still fails because the extractor cannot determine where searchable body text begins.

## 6. Body normalization

Normalization is intentionally minimal. It performs three transformations in a fixed order:

1. Remove Obsidian attachment embeds matching `![[...]]`.
2. Replace aliased wikilinks `[[target|label]]` with `label`.
3. Replace plain wikilinks `[[target]]` with `target`.

The order matters. Attachment embeds must be removed before plain-link replacement or the extractor would leave the image target as searchable text. Aliased links must be processed before plain links so the pipe form does not leave brackets or target syntax behind.

The transformation preserves headings, paragraphs, punctuation, and whitespace. It does not resolve links to files, prepend aliases, infer tags, rewrite Markdown links, or perform semantic cleanup. Preserving headings is important because the configured Markdown chunker can use heading boundaries later, and the headings carry structure in project reports and articles.

The core transformation is small enough to inspect directly:

```go
func normalizeBody(body []byte) string {
    text := string(body)
    text = attachmentRE.ReplaceAllString(text, "")
    text = labelLinkRE.ReplaceAllString(text, "$1")
    text = plainLinkRE.ReplaceAllString(text, "$1")
    return text
}
```

This is not a full Obsidian parser. It is a versioned retrieval normalization rule. If the vault later requires block references, transclusion resolution, callout-specific handling, or nested link syntax, each addition should be measured as a new extractor behavior rather than inserted as an unrecorded cleanup.

## 7. Deterministic output

Determinism has two independent requirements.

First, the document sequence must be deterministic. `WalkDir` produces candidates, but the extractor stores relative paths and sorts them after converting to slash-separated form. The resulting document array is independent of filesystem enumeration order.

Second, the serialized bytes must be deterministic. The command uses `encoding/json.MarshalIndent` with a fixed two-space indent and appends one newline. Go's JSON encoder sorts string map keys, so the frontmatter sidecar has stable key ordering as well. There are no timestamps, random IDs, absolute paths, or map-iteration-derived document order in either output.

The tests verify the pure extraction result twice and compare JSON encodings. The live smoke test goes further: it runs the command twice against the actual vault and compares the generated output files byte-for-byte.

The identity chain is therefore:

```text
vault-relative path
    -> Document.ID
normalized body
    -> Document.ContentDigest
ordered []Document + canonical JSON
    -> corpus digest
corpus digest + chunker configuration + representation configuration
    -> immutable index bundle identity
```

The extractor is the first link in that chain. If it is nondeterministic, every later artifact becomes difficult to reproduce even when the indexing code is correct.

## 8. Implementation structure

The command is intentionally self-contained in `scripts/parc-corpus/main.go`:

- `main` parses `--vault-root`, `--corpus-output`, and `--frontmatter-output`.
- `Extract` validates the root, walks and sorts Markdown paths, parses each document, and constructs `rag.Document` values.
- `parseDocument` separates the frontmatter block from the body and selects strict parsing or owned-field recovery.
- `normalizeBody` applies the fixed Obsidian syntax transformations.
- `writeJSON` creates parent directories and writes canonical indented JSON.

The command has no environment-variable dependency. A normal invocation from the RAG-TTC repository is:

```sh
go run ./scripts/parc-corpus \
  --vault-root /home/manuel/code/wesen/go-go-golems/go-go-parc
```

The default outputs are `datasets/parc/corpus.json` and `datasets/parc/frontmatter.json`, relative to the process working directory. Output paths can be overridden when testing or when the corpus is stored outside the RAG-TTC checkout.

## 9. Validation results

The focused package tests cover:

- stable ordering and byte-identical repeated extraction;
- title extraction and filename fallback;
- scalar and sequence aliases/tags;
- unquoted colon aliases;
- attachment and wikilink normalization;
- exclusion of generated directories;
- malformed unrelated YAML recovery;
- rejection of an unclosed frontmatter block.

The commands used for validation were:

```sh
GOCACHE=/tmp/rag-ttc-gocache go test ./scripts/parc-corpus
GOCACHE=/tmp/rag-ttc-gocache go build -buildvcs=false \
  -o /tmp/rag-ttc-parc-corpus ./scripts/parc-corpus
```

The live-vault run reported:

```text
extracted 1317 markdown documents
```

The two output files were 37.4 MB for the corpus and 470 KB for the sidecar. Two independent full-vault runs compared equal with `cmp`. The count differs from the earlier 1,361-note survey because the current vault contains generated `.pi` Markdown and an operational script; those files are excluded by the implemented selection policy.

The repository-wide `go test ./...` attempt was not used as the acceptance gate for this change. In this sandbox it produced no output for an extended period and was stopped. The new package compiles and its focused tests pass; the next repository-wide sweep should run in the normal development environment with the complete Go build cache available.

## 10. What is deliberately not implemented yet

The extractor does not build an index. That separation is necessary because the expensive stages require their own resource plans and run custody.

Still-open PARC phases are:

1. Run `indexes build --dry-run` against the generated corpus and record document, chunk, representation, generation, and embedding counts before provider calls.
2. Build the first `raw,summary` bundle using the tested DeepSeek ballast profile and OpenAI embeddings, with budgets derived from the dry-run output.
3. Add a refresh command that runs extraction and indexing again, then prove that an unchanged vault returns `reused=true` and performs no provider work.
4. Ask ten real questions through the workspace query surface and record retrieval failures as evaluation seeds.
5. Build a small judged evaluation set, then test breadcrumb, alias/tag expansion, summary, and question representations as experiment arms.

The refresh property depends directly on the extractor decisions made here. An unchanged note must produce the same document ID, normalized body, content digest, chunk IDs, and representation cache keys. A changed note should invalidate only its affected downstream work. The immutable bundle remains the consumer-facing unit; a new bundle is selected only after it has completed successfully.

## 11. Failure modes and operating rules

The implementation records several rules that should remain stable as the project grows:

- Do not derive document IDs from content. Path identity is what makes edits incremental and provenance readable.
- Do not prepend aliases or tags to raw body text. Use the sidecar for future representation arms and filtering.
- Do not add a “helpful” normalization step without versioning and measuring its effect. Body bytes are part of representation identity.
- Do not run the provider build before the dry-run establishes exact resource ceilings.
- Do not overwrite an existing bundle during refresh. Build a new immutable bundle and switch consumers only after completion.
- Do not treat malformed unrelated frontmatter as a reason to discard an otherwise useful note, but do not silently claim that malformed metadata was fully preserved.
- Do not include generated tool directories simply because they contain Markdown. Selection is part of corpus policy.

The most important operational test remains simple: run the extractor twice and compare the bytes. If that fails, stop before spending on generation or embeddings.

## Current project status

Phase 1 is implemented and validated. The extractor is ready to generate the PARC corpus artifacts. The first enriched bundle, refresh script, query smoke, and judged evaluation remain open under `RAG-TTC-PARC-001`.

The implementation is intentionally conservative. It gives the existing RAG-TTC pipeline a stable input without creating a second indexing architecture. The next technical risk is no longer extraction correctness; it is whether the chosen corpus population and representation strategy answer real questions over the vault with acceptable citation coverage.

## Related documents

- Ticket design: `rag-ttc/ttmp/2026/07/31/RAG-TTC-PARC-001--index-the-go-go-parc-obsidian-vault-corpus-extraction-enriched-bundle-and-refresh-workflow/design-doc/01-strategy-indexing-go-go-parc-with-the-flow-era-rag-ttc-pipeline.md`
- Intern handoff: `rag-ttc/ttmp/2026/07/31/RAG-TTC-PARC-001--index-the-go-go-parc-obsidian-vault-corpus-extraction-enriched-bundle-and-refresh-workflow/reference/02-handoff-guide-the-go-go-parc-indexing-job-a-guided-tour-of-rag-ttc.md`
- Extractor: `/home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/rag-ttc/scripts/parc-corpus/`
- RAG-TTC architecture: [[ARTICLE - rag-ttc - Architecture of a Reproducible Go RAG Evaluation System]]
- RAG evaluation dataset design: [[ARTICLE - RAG Evaluation - Building and Validating an Initial Fixed-Truth Dataset]]
- Vault indexing strategy: [[Research/playbooks/building-knowledge-base]]

## Project working rule

> [!important]
> Establish deterministic source identity before running expensive retrieval work. Every later cache, metric, and citation depends on the bytes emitted at this boundary.
