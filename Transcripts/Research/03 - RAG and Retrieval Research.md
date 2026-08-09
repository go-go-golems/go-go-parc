---
title: RAG and Retrieval Research Cluster
tags:
  - research
  - rag
  - retrieval
  - transcripts
---

# RAG and Retrieval Research Cluster

## What this cluster is about

The RAG material develops from practical retrieval pipelines into a semantics-first architecture for evidence, provenance, evaluation, and durable execution. The central concern is not merely “how to retrieve better chunks.” It is how a retrieval system can know what it indexed, which source revision produced an artifact, how evidence was merged, what was evaluated, what can be replayed, and what is safe to publish.

The cluster has four layers:

1. **Semantic retrieval foundations:** identity, canonical provenance, lawful merge, representations, retrieval, fusion, reranking, context assembly, grounding, and information-retrieval metrics.
2. **Research-program decomposition:** rag-ttc’s P01–P13 projects and composition playbook.
3. **Durable orchestration:** queues/jobs, change-driven indexing, evaluation, publication, leases, retries, idempotence, and content-addressed artifacts.
4. **Architectural consolidation:** the relationship among `ragkit`, `ragopt`, rag-ttc, GEC, and the TTC Garden assistant.

## Core research claims

- The main architectural risk is **duplicate semantic authority**: several products independently decide identity, lineage, evaluation, and promotion.
- A small evidence kernel should own versioned canonical encoding, content identity, immutable artifact references, ordering, outcomes, observations, append-only ledgers, and law tests.
- RAG semantics should remain in a RAG-specific layer; optimization should remain domain-neutral; product-native artifacts should remain authoritative.
- Plans must be inspectable before execution so the system can derive cache identity, budgets, trust-boundary checks, and audit graphs.
- Exactly-once side effects are not assumed. Observable idempotence is assembled from immutable artifacts, semantic keys, inbox/outbox patterns, provider idempotency keys, fenced leases, monotone revisions, and compare-and-swap publication.
- The asynchronous data plane is part of the semantic system: indexing, evaluation, and publication are not merely infrastructure details.

## Research progression

### P01–P03: compositional retrieval foundations

The P01–P03 thesis establishes semantic identity, canonical provenance, lawful merge, and evidence-gated retrieval composition. It treats transformations as typed artifacts and asks which identities, lineage edges, and observations survive composition.

### P06 and the research compendium

The P06 implementation report and the research-projects compendium turn the foundation into a staged research program: bounded projects, evidence contracts, executable experiments, and a composition pass. This is the RAG analogue of the PBUI capsule program.

### Retrieval-system synthesis

*Compositional Retrieval Systems* compares `ragkit`, `ragopt`, `rag-ttc`, GEC, and the TTC Garden assistant. Its thesis is that the shared boundary should be a small, domain-neutral evidence kernel rather than a universal RAG framework. *The Semantics and Dynamics of RAG* develops the semantic/dynamic model from a different angle.

### Durable production orchestration

The job-system thesis adds a queue-neutral operational semantics: finite versioned dependency graphs, readiness, fenced claims, heartbeats, success, semantic reuse, retries, lease recovery, cancellation, failure propagation, finalization, evaluation, and alias publication. This is the bridge from a research pipeline to a long-lived production data plane.

## Major deliverables

- [[Transcripts/2026/08/06/RAG DSL for Retrieval/rag-ttc-p01-p03-doctoral-thesis|rag-ttc P01–P03 doctoral thesis]] — semantic identity, canonical provenance, and lawful merge.
- [[Transcripts/2026/08/06/RAG DSL for Retrieval/rag-ttc-research-projects-compendium|rag-ttc research projects compendium]] — charter, project briefs, and composition playbook.
- [[Transcripts/2026/08/06/RAG DSL for Retrieval/rag-ttc-semantic-handbook|rag-ttc semantic handbook]].
- [[Transcripts/2026/08/06/RAG DSL for Retrieval/rag-ttc-p01-p03-delivery-README|P01–P03 delivery README]] and [[Transcripts/2026/08/06/RAG DSL for Retrieval/rag-ttc-p06-implementation-report|P06 implementation report]].
- [[Transcripts/2026/08/07/Designing RAG Abstractions/Compositional_Retrieval_Systems_Thesis|Compositional Retrieval Systems thesis]].
- [[Transcripts/2026/08/07/Designing RAG Abstractions/The_Semantics_and_Dynamics_of_RAG|The Semantics and Dynamics of RAG]].
- [[Transcripts/2026/08/08/Job System Design Thesis/Compositional_RAG_Job_System_Thesis_MathJax|Compositional durable RAG job-system thesis]].
- [[Transcripts/2026/08/08/Job System Design Thesis/Compositional_RAG_Job_System_Thesis_MathJax.md|Compositional RAG job-system thesis, alternate export]].
- [[Transcripts/2026/07/29/Researchctl Analysis for Scientists/researchctl2_rag_architecture_guide|researchctl RAG architecture guide]].
- [[Transcripts/2026/07/29/Researchctl Analysis for Scientists/durable_boundaries_workflowv3_textbook|Durable boundaries workflow textbook]].
- [[Transcripts/2026/07/29/Researchctl Analysis for Scientists/scraper_workflow_v3_scientist_new_user_analysis|Scientist/new-user scraper workflow analysis]].

## Source conversations

- [[Transcripts/2026/08/06/CHATGPT TRANSCRIPT - RAG DSL for Retrieval|RAG DSL for Retrieval]].
- [[Transcripts/2026/08/07/CHATGPT TRANSCRIPT - Designing RAG Abstractions|Designing RAG Abstractions]].
- [[Transcripts/2026/08/08/CHATGPT TRANSCRIPT - Job System Design Thesis|Job System Design Thesis]].
- [[Transcripts/2026/07/29/CHATGPT TRANSCRIPT - Researchctl Analysis for Scientists|Researchctl Analysis for Scientists]].
- [[Transcripts/2026/07/31/CHATGPT TRANSCRIPT - Recent RAG Papers|Recent RAG Papers]].
- [[Transcripts/2026/08/06/CHATGPT TRANSCRIPT - DAG Task Network Sync|DAG Task Network Sync]].

## How to read it

Read the P01–P03 thesis first for the semantic vocabulary. Then read *Compositional Retrieval Systems* for the cross-codebase architectural argument, followed by the job-system thesis for operational semantics. Finish with the researchctl artifacts to see how the abstractions become a user-facing research workflow.

> [!warning] Generated-research caveat
> The documents contain substantial architecture, API sketches, proof obligations, and executable-reference claims. Treat repository-specific counts and “validated” statements as snapshot evidence that still requires independent reproduction.
