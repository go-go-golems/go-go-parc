---
title: RES - Gao et al 2022 - HyDE Precise Zero-Shot Dense Retrieval (arXiv)
url: https://arxiv.org/abs/2212.10496
fetched: 2026-07-30
tags:
  - resource
type: resource
---

## Title:Precise Zero-Shot Dense Retrieval without Relevance Labels

Authors:[Luyu Gao](https://arxiv.org/search/cs?searchtype=author&query=Gao,+L), [Xueguang Ma](https://arxiv.org/search/cs?searchtype=author&query=Ma,+X), [Jimmy Lin](https://arxiv.org/search/cs?searchtype=author&query=Lin,+J), [Jamie Callan](https://arxiv.org/search/cs?searchtype=author&query=Callan,+J)

[View PDF](https://arxiv.org/pdf/2212.10496)

> Abstract:While dense retrieval has been shown effective and efficient across tasks and languages, it remains difficult to create effective fully zero-shot dense retrieval systems when no relevance label is available. In this paper, we recognize the difficulty of zero-shot learning and encoding relevance. Instead, we propose to pivot through Hypothetical Document Embeddings~(HyDE). Given a query, HyDE first zero-shot instructs an instruction-following language model (e.g. InstructGPT) to generate a hypothetical document. The document captures relevance patterns but is unreal and may contain false details. Then, an unsupervised contrastively learned encoder~(e.g. Contriever) encodes the document into an embedding vector. This vector identifies a neighborhood in the corpus embedding space, where similar real documents are retrieved based on vector similarity. This second step ground the generated document to the actual corpus, with the encoder's dense bottleneck filtering out the incorrect details. Our experiments show that HyDE significantly outperforms the state-of-the-art unsupervised dense retriever Contriever and shows strong performance comparable to fine-tuned retrievers, across various tasks (e.g. web search, QA, fact verification) and languages~(e.g. sw, ko, ja).

| Subjects: | Information Retrieval (cs.IR); Computation and Language (cs.CL) |
| --- | --- |
| Cite as: | [arXiv:2212.10496](https://arxiv.org/abs/2212.10496) \[cs.IR\] |
|  | (or [arXiv:2212.10496v1](https://arxiv.org/abs/2212.10496v1) \[cs.IR\] for this version) |
|  | [https://doi.org/10.48550/arXiv.2212.10496](https://doi.org/10.48550/arXiv.2212.10496) |

## Submission history

From: Luyu Gao \[[view email](https://arxiv.org/show-email/3a236f9f/2212.10496)\]  
**\[v1\]** Tue, 20 Dec 2022 18:09:52 UTC (7,003 KB)

[Which authors of this paper are endorsers?](https://arxiv.org/auth/show-endorsers/2212.10496) | Disable MathJax ([What is MathJax?](https://info.arxiv.org/help/mathjax.html))
