---
title: Architecture Garden — rag-ttc
aliases:
  - rag-ttc architecture study
  - TTC RAG architecture garden
tags:
  - architecture-garden
  - rag-ttc
  - go
  - rag
  - experiments
  - reproducibility
status: active
type: architecture-garden-project
created: 2026-07-26
analyzed: 2026-07-26
repository: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/rag-ttc
repository_remote: git@github.com:wesen/rag-ttc.git
repository_commit: 3583bc92cd738fe5175b2369e546794f850c7fae
repository_branch: task/ttc-live-rag-quality-experiment
repository_worktree_dirty: true
vault_base_commit: 69b82257f75a4ca236d985629dc298844128409f
source_tickets:
  - RAG-TTC-CLEAN-SLATE-001
  - RAG-TTC-PROD-BACKENDS-001
  - RAG-TTC-LIVE-E2E-001
  - RAG-TTC-SUMMARY-PERF-001
  - RAG-TTC-SIMPLIFY-001
related_files:
  - pkg/rag/components.go
  - pkg/rag/types.go
  - pkg/rag/execution/map.go
  - pkg/rag/execution/cache.go
  - pkg/rag/execution/cached_map.go
  - pkg/experiment/run.go
  - cmd/rag-ttc/cmds/experiments/answerquality/runner.go
  - cmd/rag-ttc/cmds/experiments/summaryperf/runner.go
---

# Architecture Garden — rag-ttc

`rag-ttc` is a plain-Go laboratory for retrieval-augmented generation experiments. Its architecture is interesting because the repository began as a deliberate rejection of a larger workflow system, then accumulated enough reusable execution machinery that it had to confront the boundary between a toolbox and a framework.

This study examines the repository at source commit `3583bc92cd738fe5175b2369e546794f850c7fae`. The worktree was dirty during analysis because active answer-quality and simplification-ticket work was present. Claims about implemented behavior are grounded in committed source. Proposed reorganizations are identified as proposals and sourced from `RAG-TTC-SIMPLIFY-001`.

> [!summary]
> - Plain Go experiment programs retain scientific policy while small interfaces and packages supply reusable mechanisms.
> - Bounded concurrency, budgets, rate admission, and per-item durable caching form one coherent execution model for expensive work.
> - Experiment directories treat inputs, observations, intermediate results, terminal state, and completed result records as first-class research data.
> - Provider adapters isolate Geppetto and Pinocchio configuration from RAG domain contracts.
> - The current simplification work demonstrates a general architectural rule: package code by semantic dependency, not by the first application that happened to need it.

## Documents in this study

| Document | Subject | Pattern maturity |
|---|---|---|
| [[01 - Project Architecture Overview]] | How commands, RAG components, execution controls, providers, and run directories compose | Established |
| [[02 - Plain Go Experiments and the Mechanism Policy Boundary]] | Why experiment orchestration remains direct code | Candidate ecosystem pattern |
| [[03 - Recoverable Bounded Execution for Expensive Work]] | Workers, rates, budgets, caching, ordering, and recovery | Established |
| [[04 - Experiment Directories as Result Custody]] | Atomic artifacts, JSONL observations, terminal state, and partial results | Established |
| [[05 - Typed RAG Contracts and Backend Adapters]] | Small interfaces, stable records, lexical/vector backends, and provider adapters | Established |
| [[06 - Semantic Identity Versioning and Validation]] | Digests, cache keys, strict validation, and replay correctness | Emergent |
| [[07 - Architecture Debt and Patterns Not to Repeat]] | Cross-experiment imports, mixed package ownership, large runners, and artifact duplication | Architecture debt |
| [[08 - Candidate Ecosystem Guidelines]] | Rules to compare across go-go-golems repositories | Candidate guidelines |

## Reading order

Read document 01 first. It defines the complete runtime and package topology. Documents 02 through 06 then isolate the strongest patterns. Document 07 prevents successful mechanisms from being confused with current organizational debt. Document 08 extracts candidate rules for comparison with other Garden projects.

For a shorter path, read 02, 03, and 08. These documents contain the most transferable material.

## Evidence boundary

The study distinguishes three kinds of statements:

- **Implemented behavior** is supported by committed code and tests at the analyzed commit.
- **Observed experiment behavior** is supported by ticket artifacts and recorded live runs.
- **Proposed architecture** comes from `RAG-TTC-SIMPLIFY-001` and is not described as already implemented.

This distinction matters because the repository is in an active refactor. For example, generic execution still lives under `pkg/rag/execution` at the analyzed commit, while the accepted design moves domain-neutral execution into `pkg/execution`.

## Related notes

- [[Research/Software Architecture Garden/README|Software Architecture Garden]]
- [[Research/KB/Projects/rag-ttc|rag-ttc project MOC]]
- [[Research/Software Architecture Garden/rag-evaluation-system/README|rag-evaluation-system architecture study]]
- [[ARTICLE - rag-ttc - Architecture of a Reproducible Go RAG Evaluation System]]
