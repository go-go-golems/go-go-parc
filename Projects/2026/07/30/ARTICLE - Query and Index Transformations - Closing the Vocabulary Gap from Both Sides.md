---
title: Query and Index Transformations - Closing the Vocabulary Gap from Both Sides
aliases:
  - Query Transformations
  - Multi-Query and HyDE
  - Vocabulary Gap
tags:
  - article
  - rag
  - retrieval
  - query-expansion
  - hyde
  - representations
  - go
status: active
type: article
created: 2026-07-30
repo: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/rag-ttc
---

# Query and Index Transformations: Closing the Vocabulary Gap from Both Sides

This article develops a unifying account of query expansion, hypothetical-document embedding (HyDE), and synthetic-question indexing as instances of one problem — queries and documents are drawn from different linguistic distributions — attackable from either side of the index boundary. It documents both sides as implemented in the `rag-ttc` system: the query-side strategies in `pkg/rag/answering/service.go` (`generateVariants`, `generateHypothetical`, the `StrategyMultiQuery` and `StrategyHyDE` retrieval cases) and the index-side family in `pkg/rag/representations/` (synthetic questions, entity expansion), together with the cost model that decides which side to pay.

> [!summary]
> 1. Users write short interrogatives; documents write declarative prose; lexical and vector retrieval both degrade across that distributional gap.
> 2. Query-side transformations (multi-query, HyDE) are paid per query at answer latency; index-side transformations (synthetic questions, entity expansion) are paid once at indexing time and cached.
> 3. HyDE and synthetic questions are mirror images: one moves the query toward document space, the other moves documents toward query space. The choice is a cost-and-staleness decision, not a quality doctrine.
> 4. Generation failure inside a retrieval path must degrade to the untransformed query, never to a failed turn — and the record must state what degraded.

## Why this note exists

The vocabulary gap is the dominant residual failure mode of a tuned retrieval system. In the motivating corpus (plant-care commerce), the judged misses concentrate on synonymy of exactly the terms BM25 weights most: a query says "arborvitae", the document says "Thuja"; a query says "Leyland Cypress", the document's binomial is "× Cupressocyparis leylandii". Both retrieval families fail here for different reasons — lexical retrieval because the tokens differ, vector retrieval less severely but still measurably for rare domain terms. The transformations in this note are the systematic responses, and the systems literature usually presents them as unrelated techniques; seeing them as one problem with two attack sides yields the cost rule that actually decides deployments.

## Core mental model

### The gap, stated distributionally

Let $Q$ be the query distribution and $D$ the document distribution over texts. Retrieval quality depends on the similarity structure between $E(q)$ and $E(d)$ (vector) or the token overlap of $q$ and $d$ (lexical); both degrade as $Q$ and $D$ diverge in register, length, and vocabulary. Transformations reduce the divergence by mapping one side toward the other:

```mermaid
flowchart LR
    subgraph query side - per query
        Q[question] --> MQ[multi-query:<br/>k paraphrases]
        Q --> HY[HyDE:<br/>hypothetical answer]
    end
    subgraph index side - once, cached
        C[chunk] --> SQ[synthetic questions]
        C --> EE[entity expansion line]
        C --> CX[contextual blurb]
    end
    MQ --> IDX[(index)]
    HY --> IDX
    SQ --> IDX
    EE --> IDX
    CX --> IDX
```

### Query-side transformations

**Multi-query expansion** hedges against a single unlucky phrasing by retrieving with several reformulations and fusing all the resulting channels. The implementation (`StrategyMultiQuery` in `pkg/rag/answering/service.go`) fans each variant out over both retrieval channels with suffixed names, so fusion sees the variants as additional evidence sources:

```go
queries := append([]rag.Query{query}, variantQueries(query, variants)...)
for index, variant := range queries {
    suffix := fmt.Sprintf(":q%d", index)
    lexical, _ := s.search(ctx, state, StageLexical, s.Lexical, variant, k)
    vector,  _ := s.search(ctx, state, StageVector,  s.Vector,  variant, k)
    result.Channels["bm25"+suffix]   = lexical
    result.Channels["vector"+suffix] = vector
}
fused, err := s.fuseChannels(ctx, state, result.Channels, request.Config)
```

Under reciprocal rank fusion with zero-for-absence semantics (see [[ARTICLE - Rank Fusion - Weighted Reciprocal Rank Fusion over Heterogeneous Channels]]), the fan-out is a soft vote: a chunk that several phrasings retrieve accumulates several reciprocal-rank terms. The measured effect in the motivating system was exactly this promotion pattern — a judged-relevant chunk moved from fused rank 2 to rank 1 because three variant channels agreed on it.

The variant generation itself (`generateVariants`) is a strict-contract call — "Return exactly one JSON object: {\"variants\": [...]}" — with defensive post-processing: variants are trimmed, deduplicated against the original question, and capped at the requested count. The governing rule is stated in the code's comment and deserves elevation to principle: **reformulation failure degrades to the plain question, never to a failed turn**, and the retrieval record carries both the variants used (`result.Variants`) and the failure reason when generation failed (`result.VariantError`). A turn must not become less reliable because an optional enhancement misfired; a record must not pretend the enhancement ran.

**HyDE** (Gao et al. 2022) replaces the query on the *vector channel only* with a generated hypothetical answer, on the observation that an answer written in document register embeds nearer to relevant documents than an interrogative does. The implementation (`StrategyHyDE`) keeps the lexical channel on the original question — exact terms the user typed remain valuable lexical evidence — and swaps only the vector query:

```go
hypothetical, variantErr := s.generateHypothetical(ctx, state, query)
vectorQuery := query
if hypothetical != "" {
    result.Variants = []string{hypothetical}   // recorded for inspection
    vectorQuery.Text = hypothetical
}
lexical, _ := s.search(..., s.Lexical, query,       k)  // original question
vector,  _ := s.search(..., s.Vector,  vectorQuery, k)  // hypothetical answer
```

The prompt constrains register and length ("a short plausible answer … as it would appear in a plant-care guide"), because the transformation's entire value lies in matching the document distribution; an essay-length hypothetical re-introduces the length mismatch it was meant to cure. The hypothetical is retrieval material in the same moral sense as an indexed summary — it steers search and is never evidence — so recording it in `result.Variants` for the inspection screens is a provenance requirement, not a nicety.

### Index-side transformations

**Synthetic questions** — document expansion by query prediction, introduced as doc2query (Nogueira et al. 2019) and scaled as docTTTTTquery — generate, per chunk, the questions the chunk answers, and index each question as its own representation whose identity points back to the source chunk (`GeneratedQuestions` and `GeneratedQuestionsBatched` in `pkg/rag/representations/`; kind `question`; the hydration invariant of [[ARTICLE - Representation Theory for Retrieval - Indexing Descriptions Instead of Content]] does the rest). This is HyDE reflected across the index boundary: instead of transforming each query toward document space at answer time, every chunk is transformed toward query space at indexing time. When evaluation queries are questions — the usual case, and this corpus's case — the indexed questions are drawn from the *same distribution as the queries themselves*, the strongest distributional match available to either side.

**Entity expansion** targets the synonymy failure directly: one generation per chunk lists "the plant species, common names, botanical synonyms, and product names this text concerns" (prompt constant `PromptEntities` in `pkg/rag/representations/prompts.go`), appended to the chunk text as an expansion line (kind `entities`). The design prediction, checkable in per-query deltas: improvements should concentrate on the species-synonymy queries identified in the judged-miss audit, and an improvement smeared evenly across queries would indicate the arm is working by some other mechanism than the hypothesis.

**Contextual blurbs** (Anthropic's contextual retrieval, 2024 — reporting up to a 49% reduction in retrieval failure rate when combined with BM25 on their corpora) address a different gap — chunks lose their document context when cut — but travel the same machinery: generated once per chunk, indexed as retrieval material, hydrated to source.

### The cost rule

Let $|C|$ be chunk count, $q$ the query rate, and let the corpus churn with representation half-life $T$. Index-side transformation costs $O(|C|)$ generations per corpus build, amortized over $q \cdot T$ queries and fully cached (in the motivating system the cache spans producers, so even a rebuilt bundle replays screening-time generations — see [[ARTICLE - Reproducibility Engineering - Digests, Caches, Budgets, and Provenance]]). Query-side transformation costs 1–2 generations per query, *at answer latency*, forever. The rule:

- stable corpus, high or long-lived query volume → pay the index side once;
- rapidly churning corpus, or exploratory/low query volume → pay the query side per use;
- the sides compose: index-side questions and query-side variants are not exclusive, and the motivating system's experiment grid measures them jointly (chunk-lab arms on the index side, `experiments answer-quality --arms bm25,vector,rrf,multi-query,hyde` on the strategy side).

A second, quieter asymmetry: index-side transformations are *inspectable at rest* — every generated question and entity line sits in the bundle, attributable and auditable — while query-side transformations exist only in per-turn records. Systems with strong provenance requirements lean index-side for that reason alone.

## Common failure modes

- **Enhancement failure failing the turn.** A generator outage should cost the reformulation, not the answer; degrade to the plain query and record the degradation.
- **Unrecorded transformations.** A turn retrieved with three paraphrases that the record does not show is undebuggable; `Variants`/`VariantError` exist precisely for the inspection screens.
- **HyDE on the lexical channel.** The hypothetical's invented terms pollute exact-match retrieval; keep the original question on lexical, swap only the vector query.
- **Unconstrained hypothetical length or register.** The transformation works by distribution matching; a mismatched hypothetical is worse than none.
- **Index-side generation without caching or budgets.** $O(|C|)$ generation without a cache is re-paid per rebuild; without a budget gate it is an unbounded spend. Both disciplines are prerequisites, not refinements.
- **Evaluating expansion without per-channel provenance.** The variant channels' contributions are the evidence that the mechanism (soft voting) and not some confound moved the metric.

## Working rules

- Degrade, never fail: every generated enhancement falls back to the untransformed query with a recorded reason.
- Record every transformation product (variants, hypotheticals) in the turn record; index-side products carry provenance fields (model, prompt digest) on the representation.
- Keep HyDE vector-only; keep multi-query fused with family-resolved weights.
- Choose the side by the cost rule (corpus stability × query volume), then measure both jointly; the sides compose.
- Validate index-side arms against their *mechanism* via per-query deltas, not only against aggregate lift.

## Sources and further reading

- Gao, L., Ma, X., Lin, J. & Callan, J. (2022). *Precise Zero-Shot Dense Retrieval without Relevance Labels.* [arXiv:2212.10496](https://arxiv.org/abs/2212.10496) · [ACL 2023](https://aclanthology.org/2023.acl-long.99/) · [[RES - Gao et al 2022 - HyDE Precise Zero-Shot Dense Retrieval (arXiv)]] — the HyDE paper; note its framing as *zero-shot* retrieval, where no relevance-tuned encoder exists.
- Nogueira, R., Yang, W., Lin, J. & Cho, K. (2019). *Document Expansion by Query Prediction.* [arXiv:1904.08375](https://arxiv.org/abs/1904.08375) · [[RES - Nogueira Cho 2019 - Document Expansion by Query Prediction doc2query (arXiv)]] — the index-side original; expansion before indexing so plain BM25 benefits.
- Anthropic (2024). *Introducing Contextual Retrieval.* [anthropic.com/engineering/contextual-retrieval](https://www.anthropic.com/engineering/contextual-retrieval) · [[RES - Anthropic 2024 - Introducing Contextual Retrieval]] — contextual embeddings + contextual BM25, prompt-caching economics, and the reported failure-rate reductions the lab's E6 tests against.
- Implementation discussed: `pkg/rag/answering/service.go` (`generateVariants`, `generateHypothetical`, `StrategyMultiQuery`, `StrategyHyDE`) and `pkg/rag/representations/` in the rag-ttc repository.

## Related notes

- [[PROJ - RAG-TTC Chunk Lab - Chunking and Representation Experiments on a Free LLM Gateway]]
- [[ARTICLE - Rank Fusion - Weighted Reciprocal Rank Fusion over Heterogeneous Channels]]
- [[ARTICLE - Representation Theory for Retrieval - Indexing Descriptions Instead of Content]]
- [[ARTICLE - Retrieval Models - Lexical, Vector, and Hybrid Retrieval in RAG Systems]]
