---
title: Architecture Garden — go-go-datadrop
aliases:
  - go-go-datadrop architecture study
  - datadrop architecture garden
  - presentation based ui architecture study
  - command framework adoption study
tags:
  - architecture-garden
  - go-go-datadrop
  - typescript
  - react
  - redux
  - go
  - design-system
  - structural-tests
  - cli
  - framework-adoption
status: active
type: architecture-garden-project
created: 2026-07-26
analyzed: 2026-07-26
last_reviewed: 2026-07-26
repository: /home/manuel/code/wesen/go-go-golems/go-go-datadrop
repository_commit: ef996430f8a3a63e6812d961eb2bae5d631272a0
repository_branch: task/datadrop-mcp
repository_commit_count: 112
analysis_commit: 69b82257f75a4ca236d985629dc298844128409f
worktree_analyzed: /home/manuel/workspaces/2026-07-24/datadrop-mcp/go-go-datadrop
source_tickets:
  - DATADROP-4 (presentation protocol and design system)
  - DATADROP-6 (design system coverage and decomposition)
  - DATADROP-7 (embedded workbench instances)
  - DATADROP-9 (CLI conversion to a command framework)
related_files:
  - ui/src/pbui/types.ts
  - ui/src/pbui/verbs.ts
  - ui/src/pbui/registry.ts
  - ui/src/store/index.ts
  - ui/src/store/applyVerb.ts
  - ui/src/apps/useTable.ts
  - ui/src/appkit/registry.ts
  - ui/test/layers.test.ts
  - ui/test/no-raw-controls.test.ts
  - ui/test/render-path.test.ts
  - ui/test/tour.test.ts
  - ui/GUIDELINES.md
  - pkg/webui/webui.go
  - pkg/doc/doc.go
  - pkg/cli/root.go
  - pkg/cli/build.go
  - pkg/cli/section.go
  - pkg/cli/exit.go
  - cmd/datadrop/tree_test.go
---

# Architecture Garden — go-go-datadrop

`go-go-datadrop` is a single-binary append-only event store with a browser workbench. This directory studies how it is actually built, which of its structures are stable enough to name, and which of them the ecosystem should adopt.

It is the **fifth** project in the Garden, after `rag-evaluation-system`, `publish-vault`, `zitadel-go-test` and `rag-ttc`. That position matters more than its own content. The [[Research/Software Architecture Garden/README|Garden's promotion path]] requires a candidate to be compared in a second project before it becomes guidance, and two of the four existing entries proposed candidates without comparing them. [[Research/Software Architecture Garden/go-go-datadrop/09 - Candidate Ecosystem Guidelines|Document 09]] compares against `rag-evaluation-system` and `rag-ttc`, and supplies a **third** independent occurrence of the embedded-SPA pattern that `publish-vault` had already confirmed as a second.

> [!summary]
> - The repository is architected unevenly on purpose, and saying so precisely is the first useful observation: a conventional Go server, a heavily architected browser workbench, and a documentation system that is arguably the most designed part of the whole thing.
> - Its strongest transferable pattern is not a runtime structure. It is a **genre of test** — thirteen instances of one shape that asserts a structural invariant over the source tree and carries an allowlist in which every exemption states its reason in a sentence.
> - Four of `rag-evaluation-system`'s fifteen candidates are independently confirmed here, three of them arrived at for different stated reasons — and one pattern now has its third occurrence across the Garden.
> - `rag-ttc`'s candidate about tests protecting architectural invariants is confirmed and **split**: this project shows that structural invariants over the source tree and runtime invariants over behaviour are different mechanisms that fail differently.
> - One finding is not project-local at all: a defect in `glazed`'s Cobra builder that silently destroys the exit-code contract of any CLI that adopts it. Filed as [glazed#611](https://github.com/go-go-golems/glazed/issues/611), and since shipped around, at a cost that is now measured.
> - The command-framework adoption that followed produced a **failure taxonomy** — four ways adoption goes wrong, all of them silent — which is document 10 and the second-strongest transferable result here after the test genre.

## What this project is

A self-hostable research data inbox. Producers append events over HTTP; the server stores them in one SQLite file and serves latest-*N* queries, time-range queries, live SSE streams, bulk dataset versions, and CSV/NDJSON/JSON export. The same binary serves a browser workbench in which a chart is not a picture but a live composition — `source ⊳ pipeline steps ⊳ encoding ⊳ geom` — and every visible part of that composition is an object with verbs.

Measured at the analyzed commit:

| Area | Lines | Notes |
|---|---|---|
| Go runtime | 13 714 | server, store, blob, auth, CLI, tabular projection |
| Go tests | 9 606 | including end-to-end smoke tests that shell out to a built binary |
| Browser source | 17 130 | excluding stories |
| Storybook stories | 7 303 in 82 files | 308 story exports |
| Browser tests | 3 765 in 20 files | 233 assertions-bearing tests |
| Ticket documentation | 42 820 | design guides, task lists, implementation diaries |

The last row is not a mistake. There is more prose about this system in `ttmp/` than there is code in it, and [[Research/Software Architecture Garden/go-go-datadrop/07 - Single Binary Delivery and Operational Surface|document 07]] and [[Research/Software Architecture Garden/go-go-datadrop/06 - Executable Documentation|document 06]] both argue that this is a deliberate structure rather than an excess.

## The documents

| Document | Subject | Maturity of the pattern studied |
|---|---|---|
| [[Research/Software Architecture Garden/go-go-datadrop/01 - Project Architecture Overview]] | The three tiers, and why they are architected unevenly | — |
| [[Research/Software Architecture Garden/go-go-datadrop/02 - The Presentation Protocol]] | Typed objects on screen, verbs as serialisable data, one seam to reducers | Established, deliberately **not** a candidate guideline |
| [[Research/Software Architecture Garden/go-go-datadrop/03 - The Store as an Instance Boundary]] | A factory with no module singleton; per-instance capability injection | Established |
| [[Research/Software Architecture Garden/go-go-datadrop/04 - The Enforced Layer Graph and the Container Panel Split]] | A one-way import graph checked by walking every import | Established |
| [[Research/Software Architecture Garden/go-go-datadrop/05 - Structural Guard Tests as a Genre]] | Thirteen tests sharing one shape, and the allowlist convention | Established — strongest candidate |
| [[Research/Software Architecture Garden/go-go-datadrop/06 - Executable Documentation]] | Tutorials that dispatch real actions; completion as a predicate over state | Emergent → Established |
| [[Research/Software Architecture Garden/go-go-datadrop/07 - Single Binary Delivery and Operational Surface]] | Embedded SPA, embedded help, addressable log areas, exit codes as API | Established, with one defect |
| [[Research/Software Architecture Garden/go-go-datadrop/08 - Architecture Debt and Patterns Not to Repeat]] | Five open items, two repaired ones and what their repair taught | Architecture debt |
| [[Research/Software Architecture Garden/go-go-datadrop/09 - Candidate Ecosystem Guidelines]] | Comparison against `rag-evaluation-system`, and eight new candidates | — |
| [[Research/Software Architecture Garden/go-go-datadrop/10 - Adopting a Command Framework]] | Four silent failure modes of framework adoption; the adapter-at-the-seam pattern | Established |

## Reading order

For a reader who wants the transferable material and nothing else: **05, then 10, then 09, then 03.**

Document 05 is the genre this project should be remembered for, and it is stronger than it was: at the first analysis all thirteen instances were TypeScript, which left open the objection that the genre was an artefact of that stack. It now has Go instances that assert properties of an assembled command tree rather than of a source tree, which both answers the objection and widens the pattern — a guard needs an assembled artefact and a property no unit can see, not necessarily a file walk.

Document 10 is the newest and the most immediately actionable. It is a failure taxonomy for adopting a framework that contributes flags, owns output, or owns error handling, derived from one complete adoption in which **every significant problem was silent**. Its §5 is an ordering: the namespace audit it recommends takes minutes in phase one and costs two forced flag renames if deferred to phase five, which is what happened.

Document 09 is where the Garden does its actual work, because it is the first place in the vault where a candidate guideline is tested against a second implementation. Document 03 is the cleanest single runtime pattern here — small, well-motivated, and with every failure mode written down before it was fixed.

Documents 02 and 06 are the interesting-but-local ones. Both are excellent; neither should be copied wholesale, and 02 says so explicitly.

## A note on evidence

Every claim in this directory is grounded in the [[Research/Software Architecture Garden/README|Garden's evidence hierarchy]]. Where a number appears — 144 ms, 6 329×, thirteen tests, 86 files citing a decision record — it was measured at the analyzed commit and the command that measured it is stated. Where a failure is described as historical, it happened and the diary entry recording it is cited. Where a concern is theoretical it is labelled a risk.

Two claims in this directory come from the analysis session itself rather than from the repository's history, and are marked where they appear: the exit-code defect was reproduced against `glazed v1.3.8` with a purpose-built two-command program, and the GritQL capability boundary was probed with three call shapes rather than read from documentation.

Document 10 adds a third category — claims measured during an *implementation* rather than an analysis. Its streaming-capability table is byte counts taken from a live pipe one second after a known write, under seven output configurations, and it exists because the same question could not be answered from the framework's help text or from reading its source. Where this directory reports that a framework's flag "does nothing," a measurement is cited.

## Maintenance

This directory is pruned rather than only appended to. At the 2026-07-26 review, document 08 was reorganised into open and repaired debt: two of its seven original items are repaired, and each is kept only because the repair produced knowledge the original entry did not have. A repaired item whose repair taught nothing should be deleted, not archived.

## Related notes

- [[Research/Software Architecture Garden/README|Software Architecture Garden]]
- [[Research/Software Architecture Garden/rag-evaluation-system/README|Architecture Garden — rag-evaluation-system]]
- [[PROJECT REPORT - go-go-datadrop v0.8 - Nineteen Verbs, and the Four Silences of Framework Adoption]]
- [[PROJECT REPORT - go-go-datadrop v0.7 - What Makes a Defect Findable]]
- [[PROJECT REPORT - go-go-datadrop v0.6 - Six Workbenches on One Page, and a Tutorial That Cannot Rot]]
- [[PROJECT REPORT - go-go-datadrop v0.5 - The Missing Middle, and Six Copies of One Style Object]]
