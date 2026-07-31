---
title: RES - Kwon et al 2023 - vLLM PagedAttention LLM Serving (arXiv)
url: https://arxiv.org/abs/2309.06180
fetched: 2026-07-30
tags:
  - resource
type: resource
---

## Title:Efficient Memory Management for Large Language Model Serving with PagedAttention

[View PDF](https://arxiv.org/pdf/2309.06180)

> Abstract:High throughput serving of large language models (LLMs) requires batching sufficiently many requests at a time. However, existing systems struggle because the key-value cache (KV cache) memory for each request is huge and grows and shrinks dynamically. When managed inefficiently, this memory can be significantly wasted by fragmentation and redundant duplication, limiting the batch size. To address this problem, we propose PagedAttention, an attention algorithm inspired by the classical virtual memory and paging techniques in operating systems. On top of it, we build vLLM, an LLM serving system that achieves (1) near-zero waste in KV cache memory and (2) flexible sharing of KV cache within and across requests to further reduce memory usage. Our evaluations show that vLLM improves the throughput of popular LLMs by 2-4 $	imes$ with the same level of latency compared to the state-of-the-art systems, such as FasterTransformer and Orca. The improvement is more pronounced with longer sequences, larger models, and more complex decoding algorithms. vLLM's source code is publicly available at [this https URL](https://github.com/vllm-project/vllm)

| Comments: |
| --- |
| Subjects: | Machine Learning (cs.LG); Distributed, Parallel, and Cluster Computing (cs.DC) |
| Cite as: | [arXiv:2309.06180](https://arxiv.org/abs/2309.06180) \[cs.LG\] |
|  | (or [arXiv:2309.06180v1](https://arxiv.org/abs/2309.06180v1) \[cs.LG\] for this version) |
|  | [https://doi.org/10.48550/arXiv.2309.06180](https://doi.org/10.48550/arXiv.2309.06180) |

## Submission history

From: Woosuk Kwon \[[view email](https://arxiv.org/show-email/2fbc22fc/2309.06180)\]  
**\[v1\]** Tue, 12 Sep 2023 12:50:04 UTC (831 KB)

[Which authors of this paper are endorsers?](https://arxiv.org/auth/show-endorsers/2309.06180) | Disable MathJax ([What is MathJax?](https://info.arxiv.org/help/mathjax.html))
