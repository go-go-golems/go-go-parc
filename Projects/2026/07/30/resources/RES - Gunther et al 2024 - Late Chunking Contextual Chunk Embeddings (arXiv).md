---
title: RES - Gunther et al 2024 - Late Chunking Contextual Chunk Embeddings (arXiv)
url: https://arxiv.org/abs/2409.04701
fetched: 2026-07-30
tags:
  - resource
type: resource
---

## Title:Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models

Authors:[Michael Günther](https://arxiv.org/search/cs?searchtype=author&query=G%C3%BCnther,+M), [Isabelle Mohr](https://arxiv.org/search/cs?searchtype=author&query=Mohr,+I), [Daniel James Williams](https://arxiv.org/search/cs?searchtype=author&query=Williams,+D+J), [Bo Wang](https://arxiv.org/search/cs?searchtype=author&query=Wang,+B), [Han Xiao](https://arxiv.org/search/cs?searchtype=author&query=Xiao,+H)

[View PDF](https://arxiv.org/pdf/2409.04701) [HTML (experimental)](https://arxiv.org/html/2409.04701v3)

> Abstract:Many use cases require retrieving smaller portions of text, and dense vector-based retrieval systems often perform better with shorter text segments, as the semantics are less likely to be over-compressed in the embeddings. Consequently, practitioners often split text documents into smaller chunks and encode them separately. However, chunk embeddings created in this way can lose contextual information from surrounding chunks, resulting in sub-optimal representations. In this paper, we introduce a novel method called late chunking, which leverages long context embedding models to first embed all tokens of the long text, with chunking applied after the transformer model and just before mean pooling - hence the term late in its naming. The resulting chunk embeddings capture the full contextual information, leading to superior results across various retrieval tasks. The method is generic enough to be applied to a wide range of long-context embedding models and works without additional training. To further increase the effectiveness of late chunking, we propose a dedicated fine-tuning approach for embedding models.

| Comments: |
| --- |
| Subjects: | Computation and Language (cs.CL); Information Retrieval (cs.IR) |
| MSC classes: | 68T50 |
| ACM classes: | I.2.7 |
| Cite as: | [arXiv:2409.04701](https://arxiv.org/abs/2409.04701) \[cs.CL\] |
|  | (or [arXiv:2409.04701v3](https://arxiv.org/abs/2409.04701v3) \[cs.CL\] for this version) |
|  | [https://doi.org/10.48550/arXiv.2409.04701](https://doi.org/10.48550/arXiv.2409.04701) |

## Submission history

From: Han Xiao \[[view email](https://arxiv.org/show-email/082aa2e9/2409.04701)\]  
**[\[v1\]](https://arxiv.org/abs/2409.04701v1)** Sat, 7 Sep 2024 03:54:46 UTC (268 KB)  
**[\[v2\]](https://arxiv.org/abs/2409.04701v2)** Wed, 2 Oct 2024 15:07:09 UTC (273 KB)  
**\[v3\]** Mon, 7 Jul 2025 17:49:51 UTC (203 KB)

[Which authors of this paper are endorsers?](https://arxiv.org/auth/show-endorsers/2409.04701) | Disable MathJax ([What is MathJax?](https://info.arxiv.org/help/mathjax.html))
