# rag-ttc semantic research project package

This directory contains 13 independently assignable research projects for validating and refining rag-ttc subsystem semantics, followed by a controlled composition pass.

## Start here

- Program charter: [Markdown](00-program-charter.md) · [PDF](00-program-charter.pdf)
- Composition pass playbook: [Markdown](90-composition-pass-playbook.md) · [PDF](90-composition-pass-playbook.pdf)
- Combined compendium: [Markdown](rag-ttc-research-projects-compendium.md) · [PDF](rag-ttc-research-projects-compendium.pdf)
- [Shared fixtures](fixtures/README.md)
- [Common result schema](schemas/project-result.schema.json)
- [Prior semantic handbook](reference/rag-ttc-semantic-handbook.pdf)

## Project handouts

| Code | Title | Markdown | PDF |
| --- | --- | --- | --- |
| P01 | Semantic Identity and Cache Fingerprints | [projects/p01-semantic-identity-cache-fingerprints.md](projects/p01-semantic-identity-cache-fingerprints.md) | [projects/p01-semantic-identity-cache-fingerprints.pdf](projects/p01-semantic-identity-cache-fingerprints.pdf) |
| P02 | Canonical Facts and Provenance Kernel | [projects/p02-canonical-facts-provenance-kernel.md](projects/p02-canonical-facts-provenance-kernel.md) | [projects/p02-canonical-facts-provenance-kernel.pdf](projects/p02-canonical-facts-provenance-kernel.pdf) |
| P03 | Lawful Merge and Deterministic Evidence Ledger | [projects/p03-lawful-merge-deterministic-ledger.md](projects/p03-lawful-merge-deterministic-ledger.md) | [projects/p03-lawful-merge-deterministic-ledger.pdf](projects/p03-lawful-merge-deterministic-ledger.pdf) |
| P04 | Candidate State and Ranked View Separation | [projects/p04-candidate-state-ranked-views.md](projects/p04-candidate-state-ranked-views.md) | [projects/p04-candidate-state-ranked-views.pdf](projects/p04-candidate-state-ranked-views.pdf) |
| P05 | Closure and Frontier Evaluation Engine | [projects/p05-closure-frontier-evaluation-engine.md](projects/p05-closure-frontier-evaluation-engine.md) | [projects/p05-closure-frontier-evaluation-engine.pdf](projects/p05-closure-frontier-evaluation-engine.pdf) |
| P06 | Flow Executor Semantics and Captured Effects | [projects/p06-flow-executor-semantics-effects.md](projects/p06-flow-executor-semantics-effects.md) | [projects/p06-flow-executor-semantics-effects.pdf](projects/p06-flow-executor-semantics-effects.pdf) |
| P07 | Knowledge Retrieval: Discovery versus Selection | [projects/p07-knowledge-discovery-selection.md](projects/p07-knowledge-discovery-selection.md) | [projects/p07-knowledge-discovery-selection.pdf](projects/p07-knowledge-discovery-selection.pdf) |
| P08 | Connected Retrieval Composition | [projects/p08-connected-retrieval-composition.md](projects/p08-connected-retrieval-composition.md) | [projects/p08-connected-retrieval-composition.pdf](projects/p08-connected-retrieval-composition.pdf) |
| P09 | Tool-Agent Evidence and Citation Contracts | [projects/p09-tool-agent-evidence-citations.md](projects/p09-tool-agent-evidence-citations.md) | [projects/p09-tool-agent-evidence-citations.pdf](projects/p09-tool-agent-evidence-citations.pdf) |
| P10 | Proof-Carrying Experiments and Replay | [projects/p10-proof-carrying-experiments-replay.md](projects/p10-proof-carrying-experiments-replay.md) | [projects/p10-proof-carrying-experiments-replay.pdf](projects/p10-proof-carrying-experiments-replay.pdf) |
| P11 | Incremental Maintenance, Updates, and Retractions | [projects/p11-incremental-updates-retractions.md](projects/p11-incremental-updates-retractions.md) | [projects/p11-incremental-updates-retractions.pdf](projects/p11-incremental-updates-retractions.pdf) |
| P12 | Backend Conformance and Schema Migration | [projects/p12-backend-conformance-schema-migration.md](projects/p12-backend-conformance-schema-migration.md) | [projects/p12-backend-conformance-schema-migration.pdf](projects/p12-backend-conformance-schema-migration.pdf) |
| P13 | Security Labels, Authorization, and Noninterference | [projects/p13-security-labels-noninterference.md](projects/p13-security-labels-noninterference.md) | [projects/p13-security-labels-noninterference.pdf](projects/p13-security-labels-noninterference.pdf) |

## Package structure

```text
assets/       architecture figures
fixtures/     neutral shared adversarial fixtures
projects/     one Markdown and PDF brief per project
reference/    prior handbook, inventory, and checksums
schemas/      common machine-readable contracts
```

Each project is self-contained: it specifies repository context, research questions, falsifiable hypotheses, API sketch, laws, scenarios, fault injection, metrics, milestones, acceptance gates, composition ports, risks, and required deliverables.
