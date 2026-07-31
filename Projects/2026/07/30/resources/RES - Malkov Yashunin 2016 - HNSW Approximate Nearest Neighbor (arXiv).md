---
title: RES - Malkov Yashunin 2016 - HNSW Approximate Nearest Neighbor (arXiv)
url: https://arxiv.org/abs/1603.09320
fetched: 2026-07-30
tags:
  - resource
type: resource
---

## Title:Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs

Authors:[Yu. A. Malkov](https://arxiv.org/search/cs?searchtype=author&query=Malkov,+Y+A), [D. A. Yashunin](https://arxiv.org/search/cs?searchtype=author&query=Yashunin,+D+A)

[View PDF](https://arxiv.org/pdf/1603.09320)

> Abstract:We present a new approach for the approximate K-nearest neighbor search based on navigable small world graphs with controllable hierarchy (Hierarchical NSW, HNSW). The proposed solution is fully graph-based, without any need for additional search structures, which are typically used at the coarse search stage of the most proximity graph techniques. Hierarchical NSW incrementally builds a multi-layer structure consisting from hierarchical set of proximity graphs (layers) for nested subsets of the stored elements. The maximum layer in which an element is present is selected randomly with an exponentially decaying probability distribution. This allows producing graphs similar to the previously studied Navigable Small World (NSW) structures while additionally having the links separated by their characteristic distance scales. Starting search from the upper layer together with utilizing the scale separation boosts the performance compared to NSW and allows a logarithmic complexity scaling. Additional employment of a heuristic for selecting proximity graph neighbors significantly increases performance at high recall and in case of highly clustered data. Performance evaluation has demonstrated that the proposed general metric space search index is able to strongly outperform previous opensource state-of-the-art vector-only approaches. Similarity of the algorithm to the skip list structure allows straightforward balanced distributed implementation.

| Comments: |
| --- |
| Subjects: | Data Structures and Algorithms (cs.DS); Computer Vision and Pattern Recognition (cs.CV); Information Retrieval (cs.IR); Social and Information Networks (cs.SI) |
| Cite as: | [arXiv:1603.09320](https://arxiv.org/abs/1603.09320) \[cs.DS\] |
|  | (or [arXiv:1603.09320v4](https://arxiv.org/abs/1603.09320v4) \[cs.DS\] for this version) |
|  | [https://doi.org/10.48550/arXiv.1603.09320](https://doi.org/10.48550/arXiv.1603.09320) |

## Submission history

From: Yury Malkov A \[[view email](https://arxiv.org/show-email/f24a1b34/1603.09320)\]  
**[\[v1\]](https://arxiv.org/abs/1603.09320v1)** Wed, 30 Mar 2016 19:29:44 UTC (1,613 KB)  
**[\[v2\]](https://arxiv.org/abs/1603.09320v2)** Sat, 21 May 2016 07:27:25 UTC (1,590 KB)  
**[\[v3\]](https://arxiv.org/abs/1603.09320v3)** Sun, 30 Jul 2017 12:07:54 UTC (2,481 KB)  
**\[v4\]** Tue, 14 Aug 2018 19:29:07 UTC (2,575 KB)

[Which authors of this paper are endorsers?](https://arxiv.org/auth/show-endorsers/1603.09320) | Disable MathJax ([What is MathJax?](https://info.arxiv.org/help/mathjax.html))
