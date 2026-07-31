---
date: 2026-07-30
report_for: 2026-07-13
type: daily-report
generated_by: go-minitrace transcript analysis
tags: [daily-report, log]
---

# Daily Report — 2026-07-13

> Generated 2026-07-30 from go-minitrace transcript analysis of all Pi, Codex, and Claude Code sessions active on 2026-07-13. Evidence: converted minitrace archives, docmgr ticket changelogs where present, and git-verified repository history.

## Summary

A heavy implementation and reporting day across **5 major work streams**, driven by **16 coding-agent sessions** (10 Pi, 4 Codex, 2 Claude Code) totaling at least **15,357 turns** and **13,037 tool calls** from sessions with available counts. **65 commits** landed across **11 repositories**. The day's work fell into five streams: (1) PBUI packages, documentation, demo deployment, and typed widget shells; (2) Transcript RAG hybrid retrieval and self-contained Pi corpus experiments; (3) Claude artifact serving, search, and user-data features; (4) Upwork opportunity research and application workflows; and (5) smaller research-lab, tiny-idp reporting, and Cardcore embedded bring-up work.

## Sessions Active on 2026-07-13

| Session | Framework | Model | Title | Turns | Tools | Window (UTC) |
|---|---|---|---|---:|---:|---|
| `019ee82a` | Pi | gpt-5.6-terra | tinyidp Device DPoP and xgoja Auth PRs | 1,910 | 2,048 | 06-21 03:12 → 07-14 16:47 |
| `019f37ea` | Pi | gpt-5.6-sol | TinyIDP BYOK Phases Zero Through Five | 3,672 | 4,140 | 07-06 14:52 → 07-24 10:26 |
| `02ffebb3` | Claude Code | claude-opus-4-8 | Explore go-surf chrome integration and custom verbs | 4,807 | 2,088 | 07-06 20:53 → 07-15 13:11 |
| `019f3df2` | Pi | gpt-5.5 | Browser plugin VM stateful feed middleware | 387 | 438 | 07-07 18:59 → 07-15 12:54 |
| `019f47ee` | Pi | umans-glm-5.2 | Transcript RAG — agentsview analysis and JS recreation on go-go-golems | 506 | 522 | 07-09 17:30 → 07-13 21:59 |
| `rollout-` | Codex | — | prod-tiny-idp workspace | — | — | 07-09 17:40 → 07-18 10:50 |
| `rollout-` | Codex | — | transcript-rag-sol workspace | — | — | 07-09 17:43 → 07-13 21:50 |
| `rollout-` | Codex | — | transcript-rag-sol2 workspace | — | — | 07-09 17:58 → 07-17 16:20 |
| `019f4d1d` | Pi | gpt-5.6-sol | Controlled CPU Inference Research Lab | 264 | 314 | 07-10 17:40 → 07-13 22:13 |
| `019f5204` | Pi | gpt-5.6-terra | TrueNAS Mac Restic Backup Setup | 223 | 217 | 07-11 16:31 → 07-14 23:03 |
| `5031c2cd` | Claude Code | claude-fable-5 | Design shared PBUI TypeScript React package | 851 | 432 | 07-12 21:06 → 07-13 18:37 |
| `019f582f` | Pi | gpt-5.6-terra | Upwork Inspector Context Workflow | 1,601 | 1,777 | 07-12 21:15 → 07-15 02:07 |
| `019f5ba6` | Pi | gpt-5.6-terra | Upwork Search and Proposal Automation | 887 | 820 | 07-13 13:24 → 07-16 17:13 |
| `019f5bcd` | Pi | gpt-5.6-terra | Look at go-go-os-frontend and 2026-07-12--clim-jsx | 176 | 153 | 07-13 14:06 → 07-14 16:02 |
| `019f5de7` | Pi | gpt-5.6-terra | Cardputer-ADV MeshCore terminal with ESP-IDF | 73 | 88 | 07-13 23:54 → 07-14 00:40 |
| `rollout-` | Codex | — | prod-tiny-idp workspace | — | — | 07-13 23:57 → 07-15 00:31 |

## Commit Volume (git-verified)

| Repository | Commits on 07-13 |
|---|---:|
| `serve-claude-experiments` | 12 |
| `clim-jsx` | 10 |
| `transcript-rag-sol2` | 9 |
| `claw-stuff` | 7 |
| `go-go-parc` | 7 |
| `esp32-s3-m5` | 6 |
| `transcript-rag` | 5 |
| `rag-evaluation-system` | 4 |
| `hetzner-k3s` | 3 |
| `infra-tooling` | 1 |
| `research-lab` | 1 |
| **Total** | **65** |

## 1. PBUI packages, documentation, demo deployment, and typed shells

**Ticket:** no ticket recorded  
**Sessions:** Claude Code `5031c2cd` (claude-fable-5, implementer); Pi `019f5bcd` (gpt-5.6-terra, follow-up/investigation); Pi `019f3df2` (gpt-5.5, adjacent Widget DSL work)  
**Repo:** `clim-jsx` — 10 commits; `hetzner-k3s` — 3 commits; `infra-tooling` — 1 commit; `rag-evaluation-system` — 4 commits; `go-go-parc` — 1 report commit  
**Project reports:** [[PROJ - PBUI Documentation - Structure, Method, and Handoff]], [[PROJ - PBUI - Presentation-Based UIs in TypeScript and React]], [[ARTICLE - Presentation-Based UIs - Porting the CLIM Interaction Model to React]], [[ARTICLE - Widget DSL v3 - From Split Modules to a Real Host Migration]]

### What happened

The PBUI package work moved from implementation into documented release and deployment. `clim-jsx` gained a full documentation set (`5dd9fdb`), a thesis-grounded user-guide rewrite (`1aadb6c`), a guided tutorial pass (`47fd0ec`), and screenshot coverage for the seven demos (`d1ee4d5`). The release path then hardened around npm trusted publishing and OIDC-only publication (`f4529ee`, `b38d829`, `d829a47`) before shipping PBUI packages v0.1.1 (`a1b3116`). This is the code-side counterpart to [[PROJ - PBUI Documentation - Structure, Method, and Handoff|the PBUI documentation handoff]].

The same stream carried PBUI into production-style static delivery: `clim-jsx` added the static demo deployment (`74b2154`) and fixed the container build to avoid local npm config leakage (`5eec756`), `infra-tooling` learned to build non-Go GHCR artifacts (`bdee9fa`), and `hetzner-k3s` added and deployed the `pbui-demo-prod` static site (`d30c091`, `5ac0d4a`, `6a16dc9`). In parallel, `rag-evaluation-system` adopted typed application shells, root pages, semantic statuses, and side-effect-only shell navigation callbacks (`eee729a`, `2e76c79`, `667f177`, `d44597d`), extending the Widget DSL/PBUI pattern described in [[ARTICLE - Widget DSL v3 - From Split Modules to a Real Host Migration|the Widget DSL v3 migration]].

## 2. Transcript RAG hybrid retrieval and self-contained Pi corpus experiments

**Ticket:** no ticket recorded  
**Sessions:** Pi `019f47ee` (umans-glm-5.2, implementer/investigator); Codex `rollout-` in `transcript-rag-sol` and `transcript-rag-sol2` workspaces (implementer, counts unavailable)  
**Repo:** `transcript-rag` — 5 commits; `transcript-rag-sol2` — 9 commits; `go-go-parc` — 3 report commits  
**Project reports:** [[PROJECT REPORT - Transcript RAG - Final Hybrid Architecture and IVF Probe Auto-Tune]], [[PROJECT REPORT - Transcript RAG - Self-Contained Pi Corpus and Representation Retrieval]], [[PROJECT REPORT - Transcript RAG Bleve - goja-bleve 0.0.6 and the Native RRF Restoration]], [[PROJECT REPORT - Transcript RAG Bleve - Hybrid Search, Empirical Findings, and the Corrected Architecture]]

### What happened

The `transcript-rag` repository corrected and finalized the hybrid retrieval architecture around Bleve and native kNN. The day included the Bleve Phase 5 migration to native Bleve kNN with RRF (`bf6adc9`), a §16 re-evaluation against `goja-bleve 0.0.6` (`b534dd4`), README diagrams/benchmarks and cleanup (`29510f7`, `f6144ad`), and an auto-tuning step for `ivfNprobePct` from corpus size (`9de8a68`). The associated vault reports captured both the final architecture and the Bleve correction, including [[PROJECT REPORT - Transcript RAG - Final Hybrid Architecture and IVF Probe Auto-Tune|the auto-tune report]].

A second branch of the same research built self-contained Pi corpus ingestion and persistent representation retrieval in `transcript-rag-sol2`. The sequence fixed representation KNN filtering (`c41e54d`), designed and added persistent representation retrieval (`ae45d27`, `1019e23`, `ff196b9`), built a self-contained Pi corpus builder and manifest adapter (`b4154f0`, `0410b96`, `29574f1`), and added a real-corpus experiment runner (`91ff1c6`, `b702e17`). `go-go-parc` recorded the corpus retrieval and architecture reports (`03147c8`, `3eef31d`, `de1fbe3`), making the implementation traceable through [[PROJECT REPORT - Transcript RAG - Self-Contained Pi Corpus and Representation Retrieval|the self-contained Pi corpus report]].

## 3. Claude artifact serving, search, and user-data features

**Ticket:** `SERVE-20260713-METASEARCH`, `SERVE-20260713-USERDATA`  
**Sessions:** no same-cwd implementer session is present in the bundle; attribution rests on git-verified commits, with long-running Claude Code/Codex sessions active elsewhere  
**Repo:** `serve-claude-experiments` — 12 commits; `go-go-parc` — 1 report commit  
**Project reports:** [[PROJ - claude.ai Artifact Archival - Browser Export, Diff Reconstruction, and Local Serving]], [[PROJ - serve-artifacts - From Static Viewer to Searchable, Organizable, Visual Gallery]]

### What happened

The Claude artifact serving work started by broadening artifact ingestion and search. `serve-claude-experiments` added support for modern file-based Claude artifacts (`86bb81c`), wrote improvement notes for managing thousands of artifacts (`df1329d`), ingested conversation export `meta.json` (`bf867ce`), and added search/discovery over a cached index (`1ceeac4`). `go-go-parc` recorded the archival deep dive (`84acdbe`) that corresponds to [[PROJ - claude.ai Artifact Archival - Browser Export, Diff Reconstruction, and Local Serving|the claude.ai archival report]].

The same repository then added the first multi-user organization layer. The user-data series introduced a SQLite user-data store and multi-user schema (`a5c6063`), favorites (`2e0f464`), user tags (`89e9620`), and collections/playlists (`c256734`), with diary commits after each task (`4c5e62d`, `2dfb910`, `b875032`) plus a diary format cleanup (`7501e8b`). This is the implementation base for the later [[PROJ - serve-artifacts - From Static Viewer to Searchable, Organizable, Visual Gallery|searchable and organizable gallery]] report.

## 4. Upwork opportunity research and application workflows

**Ticket:** Upwork Application Lab / application lifecycle workflow (no formal ID recorded)  
**Sessions:** Pi `019f582f` (gpt-5.6-terra, implementer); Pi `019f5ba6` (gpt-5.6-terra, implementer)  
**Repo:** `claw-stuff` — 7 commits; `go-go-parc` — 1 report commit  
**Project reports:** [[ARTICLE - SQLite-Backed Opportunity Research - Project Evidence and Proposal Metadata]], [[ARTICLE - Upwork Research Workflow - Search, Enrichment, and Deliverable Production]], [[PROJ - surf-go Upwork Bidding - Two-Phase Proposals, Automation Flakiness, and an Accidental Submit]]

### What happened

The Upwork stream connected opportunity research, proposal evidence, and application lifecycle tracking. `claw-stuff` added initial ticket/log scaffolding (`d7f3995`), restored the typed v3 sidebar shell (`b1f0173`), and closed the Widget DSL layout parity implementation in the diary (`d8fc294`). It then added a proposal and project-evidence application lab (`e77b3e7`) and closed that ticket (`aed3144`).

The final commits added a concrete application lifecycle workflow (`c9964b1`) and closed the lifecycle ticket (`6083ed8`). `go-go-parc` captured the corresponding SQLite-backed opportunity research report (`26fd43d`), tying the repository changes to [[ARTICLE - SQLite-Backed Opportunity Research - Project Evidence and Proposal Metadata|project evidence and proposal metadata]] and the later [[ARTICLE - Upwork Research Workflow - Search, Enrichment, and Deliverable Production|research workflow]] write-up.

## 5. Research-lab documentation, tiny-idp reporting, and Cardcore embedded bring-up

**Ticket:** no ticket recorded  
**Sessions:** Pi `019f4d1d` (gpt-5.6-sol, research-lab implementer); Pi `019f5de7` (gpt-5.6-terra, embedded bring-up implementer); Pi `019ee82a` and `019f37ea` (tiny-idp long-running context)  
**Repo:** `research-lab` — 1 commit; `esp32-s3-m5` — 6 commits; `go-go-parc` — 1 report commit  
**Project reports:** [[PROJ - Research Lab - Filesystem-First Evidence Infrastructure]], [[PROJECT REPORT - tiny-idp - Stylable Login and Consent UI]]

### What happened

The research-lab side of the day was small but git-backed: `research-lab` added its project README (`1ea7685`), aligning with [[PROJ - Research Lab - Filesystem-First Evidence Infrastructure|the filesystem-first evidence infrastructure]] note. Separately, `go-go-parc` recorded a tiny-idp stylable interaction UI report (`102036b`) that connects to the same-week [[PROJECT REPORT - tiny-idp - Stylable Login and Consent UI|tiny-idp stylable login and consent UI]] documentation; the active tiny-idp Pi and Codex sessions provide context, while the report commit is the verified artifact for this day.

The embedded branch brought up a Cardputer/Cardcore MeshCore terminal in `esp32-s3-m5`. The commit series added the design ticket (`8f775cf`), scaffolded the ESP-IDF terminal (`eded12a`), recorded scaffold and runtime-validation docs (`687dc43`, `f597d44`), added Cardputer Cap bring-up diagnostics (`0059094`), and recorded the diagnostics (`2e0d0cd`). No same-day vault project report matched the Cardcore work, so it is reported here from the git-verified commits only.

## Related Project Reports

- [[PROJ - PBUI Documentation - Structure, Method, and Handoff]] — same-day PBUI documentation handoff.
- [[PROJ - PBUI - Presentation-Based UIs in TypeScript and React]] — preceding PBUI project overview.
- [[ARTICLE - Presentation-Based UIs - Porting the CLIM Interaction Model to React]] — PBUI conceptual background.
- [[ARTICLE - Widget DSL v3 - From Split Modules to a Real Host Migration]] — typed Widget DSL migration context.
- [[PROJECT REPORT - Transcript RAG - Final Hybrid Architecture and IVF Probe Auto-Tune]] — same-day Transcript RAG final architecture report.
- [[PROJECT REPORT - Transcript RAG - Self-Contained Pi Corpus and Representation Retrieval]] — same-day Pi corpus and representation retrieval report.
- [[PROJECT REPORT - Transcript RAG Bleve - goja-bleve 0.0.6 and the Native RRF Restoration]] — follow-up on the Bleve correction.
- [[PROJECT REPORT - Transcript RAG Bleve - Hybrid Search, Empirical Findings, and the Corrected Architecture]] — follow-up hybrid-search analysis.
- [[PROJ - claude.ai Artifact Archival - Browser Export, Diff Reconstruction, and Local Serving]] — same-day artifact archival deep dive.
- [[PROJ - serve-artifacts - From Static Viewer to Searchable, Organizable, Visual Gallery]] — follow-up serving/search/user-data report.
- [[ARTICLE - SQLite-Backed Opportunity Research - Project Evidence and Proposal Metadata]] — same-day Upwork opportunity research report.
- [[ARTICLE - Upwork Research Workflow - Search, Enrichment, and Deliverable Production]] — follow-up Upwork research workflow article.
- [[PROJ - surf-go Upwork Bidding - Two-Phase Proposals, Automation Flakiness, and an Accidental Submit]] — preceding Upwork automation context.
- [[PROJ - Research Lab - Filesystem-First Evidence Infrastructure]] — research-lab infrastructure context.
- [[PROJECT REPORT - tiny-idp - Stylable Login and Consent UI]] — same-week tiny-idp UI report related to the go-go-parc note.

## Analysis Notes & Caveats

- **Method:** Sessions were discovered by the parent investigation via `--active-since`, converted to minitrace archives, then queried; commit counts were verified against git HEAD-only history in local time. This report uses the provided bundle as the evidence source and does not rerun `git` or `go-minitrace`.
- **Spanning sessions:** All 16 listed sessions cross a 2026-07-13 boundary by starting before the day, ending after it, or both: `019ee82a`, `019f37ea`, `02ffebb3`, `019f3df2`, `019f47ee`, the three 07-09 `rollout-` Codex sessions, `019f4d1d`, `019f5204`, `5031c2cd`, `019f582f`, `019f5ba6`, `019f5bcd`, `019f5de7`, and the 07-13 `rollout-` Codex session. Their transcript activity may include adjacent-day work.
- **Codex adapter caveat:** Codex sessions are present. The adapter records exec/patch activity as operation type `OTHER`, and file paths may live in `arguments_json`; the commit counts and subjects above are therefore anchored in git-verified repository history rather than Codex path extraction alone.
- **Attribution:** Commits are git-verified facts from the bundle. Repository/session attribution uses cwd, titles, and parent investigation file-write evidence; several repositories with commits (`serve-claude-experiments`, `hetzner-k3s`, `infra-tooling`, `rag-evaluation-system`) do not have a same-cwd session row in the bundle, so their completed work is reported from commit subjects and crosslinked reports rather than cwd alone.
- **Investigation artifacts:** `scripts/2026/07/30/july-2026-daily-logs`.
