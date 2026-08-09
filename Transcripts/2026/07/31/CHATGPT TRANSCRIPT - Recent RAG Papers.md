# Recent RAG Papers

- URL: https://chatgpt.com/c/6a6c1cb1-ebd4-83ea-9ecf-3f53fd7ba12b
- Created: 2026-07-31T03:55:32.963Z

---

> 3recent papers about rag and chunking and reranking

I’ll identify three recent, technically relevant papers spanning RAG, chunking, and reranking, then summarize why each matters.

```json
{"system1_search_query":[{"q":"site:arxiv.org 2025 retrieval augmented generation chunking reranking paper"},{"q":"site:aclanthology.org 2025 RAG chunking reranking"},{"q":"site:openreview.net 2025 retrieval augmented generation reranking chunking"},{"q":"site:arxiv.org 2026 RAG chunking reranking"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Selecting recent papers**

I’m choosing three recent works that together cover semantic chunking, learned chunking, and reranking. I’ll prioritize useful methodological variety and credible publication status over forcing one paper to cover every component.

**Selected recent papers**

**Searched 6 websites**

</details>


---

> recent survey article too

```json
{"system1_search_query":[{"q":"site:arxiv.org 2026 retrieval augmented generation chunking reranking paper"},{"q":"site:arxiv.org 2025 RAG chunking paper retrieval augmented generation"},{"q":"site:aclanthology.org 2025 reranking retrieval augmented generation paper"},{"q":"site:arxiv.org 2025 survey retrieval augmented generation RAG survey"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Curating a reading list**

I’m balancing broad RAG evaluation with focused work on chunking and reranking. I’ll label preprints clearly, emphasize practical relevance, and avoid overstating findings beyond what each paper supports.

**Curated a reading list**

</details>

```json
{"open":[{"ref_id":"turn933367search20"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 14 websites**

</details>

Here is a balanced **three-paper reading set plus one recent survey**, current to July 2026:

1. **General RAG evaluation:** *LaRA: Benchmarking Retrieval-Augmented Generation and Long-Context LLMs — No Silver Bullet for LC or RAG Routing* — Kuan Li et al., **ICML 2025**.  
   LaRA evaluates RAG against long-context prompting using 2,326 cases, four QA task categories, three long-document types, and eleven models. The main result is that neither RAG nor long-context processing is universally superior; performance depends on the task, model, context length, and retrieved-chunk quality. This is useful for deciding whether a system should retrieve, pass the full document, or route dynamically between the two. citeturn256566search1turn673725view4

2. **Chunking:** *Chunking Methods on Retrieval-Augmented Generation — Effectiveness Evaluation Against Computational Cost and Limitations* — Mateusz Śmigielski et al., **arXiv, May 2026**.  
   This preprint compares fixed-size, semantic, clustering-based, graph-based, classical and LLM-based chunkers across retrieval and end-to-end generation experiments. A particularly practical finding is that computationally expensive chunkers frequently provide only marginal gains, while fixed-size and recursive-semantic approaches remain strong and substantially more stable baselines. citeturn209237view0turn658249view0

3. **Reranking:** *InfoGain-RAG: Boosting Retrieval-Augmented Generation through Document Information Gain-based Reranking and Filtering* — Zihan Wang et al., **EMNLP 2025**.  
   The paper defines Document Information Gain, measuring how much a retrieved document changes the generator’s confidence in the correct answer. Those scores are then used to train a specialized reranker that filters misleading passages and prioritizes documents based on their usefulness to generation—not merely query-document similarity. citeturn209237view1

### Recent survey

**Retrieval-Augmented Generation for AI-Generated Content: A Survey** — Penghao Zhao et al., *Data Science and Engineering*, **January 2026**.  
This is the broadest recent overview among these selections. It covers RAG foundations, retrievers and generators, augmentation and enhancement methods, multimodal applications, benchmarks, limitations and future directions. It is a good starting point before reading the three specialized papers. citeturn673725view0turn193683view0

**Suggested order:** survey → LaRA → chunking study → InfoGain-RAG.


---

> more specialized papers? why these in particular? did they stick out?

The earlier set was intentionally broad, not the most specialized possible. I’m checking narrower papers that isolate chunking, retrieval scoring, and reranking rather than benchmarking whole RAG systems.

```json
{"system1_search_query":[{"q":"site:arxiv.org RAG chunking semantic chunking paper 2024 2025"},{"q":"site:aclanthology.org reranking retrieval augmented generation paper 2024 2025"},{"q":"site:arxiv.org late chunking long context embeddings paper"},{"q":"site:arxiv.org contextual document embeddings reranking RAG 2025"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Verifying research quality**

I’m narrowing the literature to confirmed papers and proceedings, checking publication status and distinguishing surveys from focused studies. I’ll emphasize work that directly compares chunking, routing, reranking, and generation utility.

**Verified research quality**

</details>

```json
{"system1_search_query":[{"q":"site:aclanthology.org \"set-wise passage selection\" RAG ACL 2025"},{"q":"site:proceedings.neurips.cc RankRAG 2024"},{"q":"site:aclanthology.org REAR relevance-aware retrieval augmented 2024"},{"q":"site:openreview.net \"Mixtures of Text Chunking Learners\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Refining the literature**

I’m revising the earlier list because it emphasized coverage over specialization. I’m separating papers by chunking, reranking, routing, and generation utility, while distinguishing established work from newer preprints.

**Refined the literature**

</details>

```json
{"open":[{"ref_id":"turn871310search0"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 19 websites**

</details>

Yes. I would revise the earlier recommendation: it was optimized for **coverage**, not because all three papers were equally specialized or influential.

### Why the earlier papers were selected

**LaRA** stood out as a strong **system-level benchmark**. It evaluates when RAG should be preferred over simply passing a long context, using 2,326 test cases, four QA task types, three long-context types, and eleven models. That makes it useful for architecture decisions, but it does not deeply study chunking or reranker design. citeturn305953search0

The **2026 chunking comparison** stood out because it examines many chunking methods alongside computational cost. However, it is currently an arXiv v1 submitted in May 2026 rather than an established peer-reviewed reference. I would treat it as a useful recent comparison, but not as the first paper to cite for a specialized literature review. citeturn305953search1

**InfoGain-RAG** genuinely did stand out. Most rerankers optimize query–passage relevance; InfoGain-RAG instead scores a document according to how much it improves the generator’s confidence in the correct answer. That directly connects reranking supervision to downstream generation utility. citeturn116517view6

## More specialized papers

### Chunking and retrieval granularity

**1. Dense X Retrieval: What Retrieval Granularity Should We Use? — EMNLP 2024**

This is one of the more fundamental chunking-related papers. Rather than proposing another boundary heuristic, it asks what the indexed retrieval unit should be: document, passage, sentence, or proposition. It introduces proposition-level units—short, self-contained atomic facts—and reports improvements in retrieval and downstream QA under fixed computational budgets. citeturn844226view0

**Why it stands out:** it separates **retrieval granularity** from ordinary chunk-boundary selection. This is often the more important design decision.

**2. Is Semantic Chunking Worth the Computational Cost? — Findings of NAACL 2025**

This is the strongest skeptical baseline. It evaluates semantic chunking through document retrieval, evidence retrieval, and retrieval-based answer generation, finding that its additional cost does not produce consistent improvements over simpler approaches. citeturn116517view1

**Why it stands out:** it reports a useful negative result and tests whether popular semantic-chunking claims survive end-to-end evaluation.

**3. MoC: Mixtures of Text Chunking Learners for RAG — ACL 2025**

MoC introduces two intrinsic chunk-quality measures, **Boundary Clarity** and **Chunk Stickiness**, and uses a granularity-aware mixture of chunkers. Its LLM produces structured chunking rules, which are subsequently applied to the source document. citeturn116517view0

**Why it stands out:** it tackles both missing pieces in chunking research—how to evaluate chunks independently and how to adapt the chunker to document granularity.

**Conceptual companion: Late Chunking**

Late Chunking embeds the long document before pooling token representations into individual chunks. Consequently, a chunk representation retains information from its surrounding document context. It is an important and practically influential idea, although I would place the peer-reviewed ACL/NAACL papers above it when constructing a formal literature review. citeturn998614search1turn998614search10

### Reranking, selection and pruning

**4. Shifting from Ranking to Set Selection for RAG — ACL 2025**

SetR argues that independently scoring every passage is inadequate for multi-hop questions. It identifies the query’s information requirements and chooses a collection of passages that jointly covers them. citeturn116517view4

**Why it stands out:** it explicitly addresses redundancy and complementary evidence. Two individually relevant passages may contain the same fact, while a slightly lower-ranked passage may supply the missing reasoning step.

**5. Provence: Efficient and Robust Context Pruning for RAG — ICLR 2025**

Provence jointly performs passage reranking and sentence-level context pruning. It dynamically determines how much of each retrieved passage to retain and integrates pruning into an already-required reranking pass. citeturn844226view3turn379147view0

**Why it stands out:** it is unusually operational. It optimizes relevance, context length and generation cost together rather than treating reranking and compression as separate modules.

**6. RankRAG: Unifying Context Ranking with RAG — NeurIPS 2024**

RankRAG instruction-tunes one model for both context ranking and answer generation. The authors report that adding a relatively small amount of ranking data to the training mixture can outperform dedicated ranking models. citeturn116517view5

**Why it stands out:** it challenges the conventional modular design in which the reranker and generator are independently trained.

## Focused recent survey

**Test-time Corpus Feedback: From Retrieval to RAG — Findings of EACL 2026**

This is a better specialized survey than a generic RAG overview for your topic. It organizes adaptive retrieval and ranking methods according to where feedback originates and whether it modifies the query, retrieved context, or document pool. Its central focus is retrieval as an iterative, learnable process rather than a one-shot preprocessing stage. citeturn219640view0

### My recommended core set

For a compact but technically focused reading list, I would use:

1. **Dense X Retrieval** — retrieval unit and granularity.  
2. **Is Semantic Chunking Worth the Computational Cost?** — rigorous chunking baseline.  
3. **SetR** — set-wise reranking and evidence coverage.  
4. **Provence** — reranking combined with context pruning.  
5. **InfoGain-RAG** — generator-aware reranking objective.  
6. **Test-time Corpus Feedback** — focused survey and taxonomy.

