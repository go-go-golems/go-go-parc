---
title: Chunking Theory - Cut Strategies and the Exact-Slice Invariant
aliases:
  - Chunking Theory
  - Chunking Strategies
tags:
  - article
  - rag
  - chunking
  - retrieval
  - text-processing
status: active
type: article
created: 2026-07-30
repo: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/rag-ttc
---

# Chunking Theory: Cut Strategies and the Exact-Slice Invariant

This article treats the segmentation of documents into retrieval chunks as a design space with measurable axes: cut position, chunk size, overlap, and the relationship between the unit that is retrieved and the unit that is presented as evidence. It also states the provenance invariant that constrains every strategy in the space, including strategies that delegate cut placement to a language model. The measurements cited come from [[PROJ - RAG-TTC Chunk Lab - Chunking and Representation Experiments on a Free LLM Gateway]].

> [!summary]
> 1. Chunk size trades matching precision against contextual completeness; it is a live, measurable lever, and its optimum is corpus-specific.
> 2. Cut *position* strategies (structure-aware, sentence-snapped, semantic) matter only when documents give them room to act; measure whether the lever is live before optimizing it.
> 3. Small-to-big retrieval dissolves the size trade by decoupling the retrieval unit from the evidence unit.
> 4. The exact-slice invariant — every chunk is a validated byte range of its source — is what keeps provenance intact under every strategy, including LLM-directed cutting, which may propose boundaries but never text.

## Why this note exists

Chunking is the first irreversible decision in an indexing pipeline: everything downstream — embeddings, lexical postings, evidence admission — is built per chunk, and re-chunking invalidates all of it. The decision is usually made once, by convention (a window size copied from a tutorial), and never measured. The laboratory work behind this note measured it, and found both a dead lever that folklore treats as important (the chunking *algorithm*, on that corpus) and a live lever that the convention had left mistuned (the chunk *size*, where the measured optimum sat at roughly twice the configured value). The general lesson is that the chunking design space is cheap to measure and expensive to assume.

## Core mental model

### Why chunking exists

Two independent constraints force segmentation. Embedding models accept bounded input, so documents beyond the bound cannot be embedded whole. More fundamentally, retrieval granularity and answer granularity differ from document granularity: a 30,000-word document is a poor retrieval result (which part answered the question?) and a poor unit of evidence (it overflows any bounded context). Chunking manufactures units small enough to match precisely and to admit as evidence.

The size parameter then trades two goods against each other. Small chunks match queries tightly — the matched terms constitute a large fraction of the chunk — and spend evidence budget efficiently; but they sever text from the context that makes it interpretable, and multi-part answers scatter across several of them. Large chunks carry their context and keep answers whole; but they match diffusely and exhaust evidence budgets quickly. Measured on the motivating corpus at unit-level scoring, recall and hit rate rose with size well past the configured 1,200 runes — Recall@10 from 0.7986 at 1,200 to 0.8212 at 2,400; HitRate@10 from 0.9236 to 0.9514 — with the knee between 1,600 and 2,400. The optimum is a property of the corpus and the query distribution, not of the algorithm; the only general statement is that the curve exists and can be traced in minutes with a proper evaluation harness.

Overlap — repeating the tail of each chunk at the head of the next — is conventionally justified as insurance against cutting an answer in half. Measured at unit granularity, overlap contributed nothing and slightly hurt (zero overlap scored marginally *above* the 10% convention), while inflating the index proportionally. Its remaining justification is generation-side (an admitted chunk carries a little of its neighborhood), which is a separate concern from retrieval and should be decided by generation-side evidence.

### Cut-position strategies

**Fixed windows** cut every $N$ runes regardless of content. They are the baseline: trivially correct, structure-blind.

**Structure-aware cutting** splits at document structure (headings), keeping sections whole and merging small ones. Its value is conditional on the corpus: when most sections *fit* the window, it aligns chunks with topical boundaries; when most sections *exceed* the window, the window fallback does all the cutting and the strategy degenerates to the baseline. The motivating corpus is the second case — roughly 90% of sections exceed 1,200 runes — and the measured metrics of the two strategies are identical to four decimal places. This is the dead-lever lesson in its sharpest form: the strategy is not wrong, it is *inert*, and only measurement distinguishes inert from important.

**Sentence snapping** retreats each window boundary to the last sentence-final position within a bounded distance, eliminating mid-word and mid-sentence cuts. Implementation requires one guard: a snap that would move the boundary to or before the window's start-plus-overlap stalls the sliding window; such snaps must revert to the unsnapped boundary, or pathological inputs (long runs without sentence boundaries, or consisting entirely of them) never terminate. Measured effect: small and positive (+5/−1 queries), consistent with cut cleanliness mattering at the margin.

**Semantic-breakpoint cutting** embeds sentences and places boundaries at similarity minima between neighbors — cuts where the topic measurably shifts. It costs one embedding pass and is worth running only when cruder levers leave headroom.

**Late chunking** inverts the pipeline: embed the whole document with a long-context embedder, then pool per-chunk vectors from the token embeddings afterward, so each chunk's vector reflects its full-document context. It is gated on embedder capability (input limits) and is a research-grade arm rather than a default.

### Small-to-big: dissolving the trade

The size trade assumes the retrieved unit and the evidence unit are the same object. They need not be. In small-to-big retrieval, small chunks (say 300 runes) provide the *searchable text*, but each small chunk's representation carries the identity of its enclosing *parent* chunk (say 1,200–2,400 runes); a hit on the precise small text hydrates to the contextual parent. Matching precision and evidence completeness are then set independently.

The implementation reduces to a mapping problem — assign each small chunk to the parent whose byte range overlaps it most — and to an existing invariant: if representations already carry a chunk identity and hits already hydrate through it, small-to-big requires *no new machinery*, only a representation whose text and identity come from different chunks. The correctness check is characteristic: at unit-level scoring, the small-to-big configuration must reproduce the small-chunk configuration's metrics exactly (identical searchable text, identical collapse), and in the motivating laboratory it did, to every decimal — which validated the plumbing while deferring the strategy's real payoff (better evidence at equal retrieval) to generation-side measurement.

### LLM-directed cutting and the exact-slice invariant

The invariant first: **a chunk is an exact byte range of its source document, and validation asserts the equality**. Every downstream consumer — citation, display, audit — depends on chunk text being source text. A model may therefore decide *where* text is cut, but no model output may ever *become* chunk text.

This constrains the contract for LLM-directed chunking. Byte offsets from a model are plausible-looking and wrong; verbatim copies drift in case and truncation. The robust contract asks the model, given the whole document, for boundary *markers* only — the verbatim first eight to twelve words of each proposed chunk — and performs alignment locally:

```
words      = whitespace-tokenized document with byte offsets, lowercased
boundaries = [0]                       # first chunk starts the document
cursor     = 1
for marker in markers[1:]:
    m = tokenize(lowercase(marker))
    pos = first index >= cursor where words[pos : pos+len(m)]
          equals m  (final word compared as prefix)
    if pos found:
        boundaries.append(words[pos].offset)
        cursor = pos + 1
    # else: drop the marker — its chunk merges into the previous one
ranges = consecutive boundary pairs, last ending at len(document)
chunks = FromRanges(document, "llm-chunk", ranges)   # validates every slice
```

The failure semantics are the design: an unmatched marker degrades *granularity* (two proposed chunks merge) but can never corrupt a *range*; an entirely unparseable response degrades to one whole-document chunk. Search is forward-only and case-insensitive, with the final marker word matched as a prefix because models truncate. Cost is one call per document, which — under the batching economics described in [[ARTICLE - Measurement Discipline and LLM IO - Throughput, Batching, and Structured Output]] — makes model-directed cutting one of the *cheapest* strategies in the space rather than one of the most expensive.

## Common failure modes

- **Optimizing a dead lever.** Elaborate cut-position strategies on a corpus whose sections exceed the window all degenerate to the window. Measure liveness first: if two strategies produce near-identical chunk populations, their metrics are decided before evaluation runs.
- **Assuming the configured size is near the optimum.** The size/recall curve is cheap to trace and its knee is corpus-specific.
- **Justifying overlap by intuition.** Its retrieval value is measurable and was measured at zero; its index cost is proportional and certain.
- **Trusting model-produced offsets or model-copied text.** Both violate provenance; the marker-alignment contract exists because the invariant is non-negotiable.
- **Window strategies without stall guards.** Any boundary-adjustment rule (snapping, merging) interacting with overlap can freeze the slide on adversarial input; termination requires an explicit revert condition.

## Working rules

- Trace the size/recall curve before any other chunking work; it is the highest-information cheap measurement in the space.
- Set overlap to zero for retrieval; reintroduce it only on generation-side evidence.
- Verify a cut strategy is live (changes the chunk population materially) before spending effort on it.
- Keep the exact-slice invariant absolute; models propose boundaries as verbatim markers, alignment happens locally, and unmatched proposals merge rather than guess.
- When precision and context conflict, reach for small-to-big before compromising either.

## Related notes

- [[PROJ - RAG-TTC Chunk Lab - Chunking and Representation Experiments on a Free LLM Gateway]]
- [[ARTICLE - Representation Theory for Retrieval - Indexing Descriptions Instead of Content]]
- [[ARTICLE - Retrieval Evaluation - Judged Sets, Ranking Metrics, and Per-Query Analysis]]
