---
title: Representation Theory for Retrieval - Indexing Descriptions Instead of Content
aliases:
  - Representation Theory for Retrieval
  - Retrieval Representations
tags:
  - article
  - rag
  - retrieval
  - representations
  - contextual-retrieval
  - go
status: active
type: article
created: 2026-07-30
repo: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/rag-ttc
---

# Representation Theory for Retrieval: Indexing Descriptions Instead of Content

This article develops the representation layer of a retrieval system: the separation between the text a system *searches over* and the text it *presents as evidence*, the invariant that keeps the separation safe, the taxonomy of representation kinds ordered by cost, and the mechanics by which a lossy description of a text can outperform the text itself as a retrieval key. The reference implementation is `pkg/rag/representations/` in the `rag-ttc` repository, whose measured results anchor the claims.

> [!summary]
> 1. The retrieval index is a place for search-optimized descriptions of content; the evidence path is a place for source text with provenance. Conflating the two roles forces one text to serve both badly.
> 2. The hydration invariant — every representation carries its source chunk's identity, and every hit resolves to that chunk before downstream use — is the single rule that makes arbitrary generated text safe to index.
> 3. A lossy representation beats the complete text whenever the loss falls on scoring noise: measured, an extractive one-sentence summary as sole indexed text raised MRR from 0.8366 to 0.8585.
> 4. Representation provenance (kind, generating model, prompt digest) must travel on the representation itself, because a bundle full of generated text without provenance is unauditable.

## Why this note exists

Most retrieval systems index exactly one representation of each chunk: the chunk. The alternative — indexing derived texts that point back to their source — appears in the literature piecemeal (doc2query, contextual retrieval, summary indexes) and is usually presented per technique. The consolidated view is more useful: all of these are the *same architectural move*, enabled by one invariant, differing only in what the derived text is and what it costs to produce. Once the layer exists, every new representation idea is a one-function experiment rather than a system change; the motivating laboratory ran nine generated-representation arms in a day on exactly this property.

## Core mental model

### Two roles, one text — until they separate

A chunk's text serves two masters. As *evidence*, it must be complete, contextual, and verbatim from source — properties that make answers correct and citable. As a *retrieval key*, it should be dense in discriminative terms and free of filler — properties that make it findable. These optimization targets conflict: completeness adds the very text that dilutes term density (see the BM25 length-normalization analysis in [[ARTICLE - Retrieval Models - Lexical, Vector, and Hybrid Retrieval in RAG Systems]]).

The representation layer separates the roles. A `Representation` is searchable text derived from a chunk:

```go
// pkg/rag/types.go
type Representation struct {
    ID            string  // digest of chunk, kind, and text
    ChunkID       string  // lineage: the source chunk
    Kind          string  // "raw", "summary", "question", "contextual", ...
    Text          string  // what the index sees
    ContentDigest string
    Model         string  // provenance: who wrote it
    PromptDigest  string  // provenance: under what instruction
}
```

Indexes are built over representations; hits are resolved back to chunks:

```go
// pkg/rag/representations/representations.go
// Hydrate maps non-raw hits back to their source chunks. It is the
// enforcement of the rule that a summary or question representation is
// retrieval material, never final evidence.
func Hydrate(hits []rag.Hit, chunks []rag.Chunk) ([]rag.Chunk, error)
```

This is the **hydration invariant**, and everything else in the layer is a consequence of it. Because no representation text ever reaches a generator or a user, the layer is free to index *anything* — model-written paragraphs, synthetic questions, keyword lines — without any generated token contaminating the evidence path. The invariant converts a trust problem ("can we show users model output?") into a non-problem ("model output steers search and is then discarded").

### The taxonomy, ordered by cost

| kind | derivation | cost | targets |
| --- | --- | --- | --- |
| `raw` | the chunk itself | zero | baseline; the only kind that is its own evidence |
| `breadcrumb` | heading path prepended (`Breadcrumbs`, deterministic from document structure) | zero | lost document context |
| `summary` (extractive) | lead sentence (`ExtractiveSummarizer`) | zero | term density |
| `summary` (abstractive) | model-written, sentence or keyword form | 1 call/chunk | term density + normalization of phrasing |
| `contextual` | model-written situating paragraph + chunk body (`Contextual`) | 1 call/chunk | lost document context (the contextual-retrieval hypothesis) |
| `question` | 2–3 model-written questions, each its own representation (`GeneratedQuestions`) | 1 call/chunk | query-distribution match; see [[ARTICLE - Query and Index Transformations - Closing the Vocabulary Gap from Both Sides]] |
| `entities` | chunk + model-written synonym/species line (`EntityExpansions`) | 1 call/chunk | rare-term synonymy |
| `small` | small chunk's text under its *parent* chunk's identity (`SmallToBig`) | zero | precision/context decoupling; see [[ARTICLE - Chunking Theory - Cut Strategies and the Exact-Slice Invariant]] |

Kinds compose by set union with identity-based deduplication (`Compose`), and a guard (`EnsureRaw`) enforces that enrichment adds to raw rather than replacing it in production bundles — raw is the only kind that is its own evidence, and a bundle that can only retrieve over summaries could cite nothing.

Note the `small` kind's structure: text from one chunk, identity of another. The type permits it because `ChunkID` is data, not derivation, and hydration then performs small-to-big retrieval with zero dedicated machinery — the clearest demonstration that the invariant, not any specific representation, is the load-bearing design.

### Why lossy beats complete

Two mechanisms, one per retrieval family.

**Lexical.** BM25's length normalization discounts matches in long documents. A representation containing the chunk's discriminative terms and nothing else concentrates the same matches in a shorter document, and outscores the original whenever the removed text contributed more length than term coverage. The measured case: indexing *only* lead-sentence extractive summaries (arm `summary-only`) against the same 148-query evaluation set yielded MRR 0.8585 / Recall@10 0.8079 / HitRate@10 0.9306 versus the raw baseline's 0.8366 / 0.7986 / 0.9236, improving ten queries and regressing two. The two regressions matter as much as the ten improvements: they are queries whose key terms lived *outside* the lead sentence, which bounds how far pure extraction can go and motivates the model-written arms.

**Vector.** An embedding represents its input's dominant semantics; filler dilutes the representation of the discriminative content. A condensed surrogate embeds closer to the query distribution — and the limiting case is the `question` kind, whose text is drawn from the query distribution itself.

The general statement: the raw chunk is optimized for *being evidence*; a representation can be optimized for *being found*; the invariant lets each text serve its single role.

### Provenance and promotion

Generated representations carry `Model` and `PromptDigest`, and their `ID` digests the generated text — so a changed prompt yields new identities, and a bundle's representation list (which enters the bundle digest) can never silently mix generations from different instructions. The bundle builder (`cmd/rag-ttc/cmds/indexes/`, flag `--representations raw,summary,contextual,question,entities`) shares the canonical prompt constants and generation-cache identity with the experiment harness (`pkg/rag/representations/prompts.go`), which makes *promotion* — turning a screening winner into a production bundle — a cache replay rather than a second generation spend. The economics of this arrangement are treated in [[ARTICLE - Reproducibility Engineering - Digests, Caches, Budgets, and Provenance]].

## Common failure modes

- **Indexing generated text as evidence.** The moment a summary can be cited, every hallucinated detail in it becomes a system output. The hydration invariant exists to make this structurally impossible, not merely discouraged.
- **Replacing raw instead of augmenting it** in production bundles. `summary-only` is a legitimate *experimental* arm; a production bundle without raw representations cannot present source evidence. `EnsureRaw` encodes the rule.
- **Provenance-free generation.** A bundle of model-written text without model and prompt identity cannot be audited, regenerated, or invalidated correctly.
- **Judging representations instead of sources downstream.** Rerankers and generators must consume hydrated chunks; a cross-encoder scoring a one-line summary scores the summary.
- **Treating a representation experiment as a chunking experiment.** The axes are orthogonal by construction (representations derive from a fixed chunk population); conflating them in one arm destroys attribution.

## Working rules

- Every representation carries its source chunk identity; every hit hydrates before any downstream use. No exceptions, including display.
- Raw is always present in production bundles; enrichment adds, never replaces.
- Stamp `Model` and `PromptDigest` on every generated representation; a changed prompt is a new representation population and a new experiment arm.
- Screen representation ideas with the cheapest retrieval that can rank them (lexical, in-memory) before spending embeddings on them.
- Read the regressed queries of every winning representation: they mark the boundary of its mechanism.

## Related notes

- [[PROJ - RAG-TTC Chunk Lab - Chunking and Representation Experiments on a Free LLM Gateway]]
- [[ARTICLE - Retrieval Models - Lexical, Vector, and Hybrid Retrieval in RAG Systems]]
- [[ARTICLE - Chunking Theory - Cut Strategies and the Exact-Slice Invariant]]
- [[ARTICLE - Query and Index Transformations - Closing the Vocabulary Gap from Both Sides]]
