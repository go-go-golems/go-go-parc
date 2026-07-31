---
date: 2026-07-30
report_for: 2026-07-04
type: daily-report
generated_by: go-minitrace transcript analysis
tags: [daily-report, log]
---

# Daily Report — 2026-07-04

> Generated 2026-07-30 from go-minitrace transcript analysis of all Pi and Claude Code sessions active on 2026-07-04. Evidence: converted minitrace archives, docmgr ticket changelogs where present, and repository git history. The bundle contained no Codex sessions for this day.

## Summary

A heavy implementation day across **3 major work streams**, driven by **13 coding-agent sessions** (9 Pi, 0 Codex, 4 Claude Code) totaling **8,669 turns** and **6,788 tool calls**. **44 git-verified commits** landed across **7 repositories**. The day's work fell into three streams: (1) a multi-model `mdlinkcheck` / MDLC implementation bake-off, (2) the ATProto HyperCard sandboxed FRP/runtime and static deployment, and (3) static live-demo deployment work for the codebase-browser/HyperCard demo stack.

## Sessions Active on 2026-07-04

| Session | Framework | Model | Title | Turns | Tools | Window (UTC) |
|---|---|---|---|---:|---:|---|
| `019ee82a` | Pi | gpt-5.6-terra | tinyidp Device DPoP and xgoja Auth PRs | 1,910 | 2,048 | 06-21 03:12 → 07-14 16:47 |
| `7a31e95d` | Claude Code | claude-sonnet-5 | Research Foo Camp attendees and populate database | 158 | 76 | 06-26 08:15 → 07-06 15:02 |
| `019f19aa` | Pi | glm-5.2 | RESEARCHCTL-007 web workbench and REPL visualizers | 1,580 | 1,553 | 06-30 17:54 → 07-05 16:32 |
| `019f2520` | Pi | gpt-5.5 | GCB-017 No-sqljs Live Demo PR | 744 | 716 | 07-02 23:18 → 07-05 22:12 |
| `019f2554` | Pi | gpt-5.5 | ATProto HyperCard Browser Runtime | 189 | 205 | 07-03 00:15 → 07-05 17:02 |
| `b780255a` | Claude Code | claude-fable-5 | Update wesen-os to latest APIs and create intern guide | 2,219 | 1,040 | 07-03 18:59 → 07-05 17:51 |
| `474d7b7e` | Claude Code | claude-fable-5 | Build CMS design system components and documentation | 1,407 | 753 | 07-03 20:50 → 07-05 20:00 |
| `019f2df1` | Pi | glm-5.2 | Create a new docmgr ticket to implement @TASK.md.txt . Create a glossary for the | 75 | 77 | 07-04 16:23 → 07-04 16:56 |
| `019f2df3` | Pi | gpt-5.5 | Create a new docmgr ticket to implement @TASK.md.txt . | 52 | 57 | 07-04 16:25 → 07-04 16:55 |
| `a4b6434f` | Claude Code | claude-fable-5 | Create docmgr ticket with intern onboarding guide | 133 | 61 | 07-04 16:26 → 07-04 16:59 |
| `019f2dfe` | Pi | gpt-5.5 | Run the blind tests in this directory against /home/manuel/code/wesen/2026-07-04 | 47 | 39 | 07-04 16:37 → 07-04 16:51 |
| `019f2e12` | Pi | umans-qwen3.6-35b-a3b | /momdel | 104 | 113 | 07-04 17:00 → 07-04 17:07 |
| `019f2e1b` | Pi | umans-kimi-k2.7 | Create a new docmgr ticket to implement @TASK.md.txt . | 51 | 50 | 07-04 17:09 → 07-04 17:23 |

## Commit Volume (git-verified)

| Repository | Commits on 07-04 |
|---|---:|
| `2026-07-04--mdlint-qwen3` | 9 |
| `2026-07-04--mdlint-glm5` | 7 |
| `2026-07-04--mdlint-gpt5` | 7 |
| `2026-07-02--atproto-hypercard` | 6 |
| `2026-07-04--mdlint-fable` | 6 |
| `2026-07-04--mdlint-kimi2.7` | 5 |
| `2026-03-27--hetzner-k3s` | 4 |
| **Total** | **44** |

## 1. Multi-model MDLC / mdlinkcheck implementation bake-off

**Ticket:** `MDLC-001` where recorded; qwen used `mdp-1` in its ticket scaffold
**Sessions:** implementers `019f2df1` (Pi, glm-5.2), `019f2df3` (Pi, gpt-5.5), `a4b6434f` (Claude Code, claude-fable-5), `019f2e12` (Pi, umans-qwen3.6-35b-a3b), `019f2e1b` (Pi, umans-kimi-k2.7); evaluator `019f2dfe` (Pi, gpt-5.5)
**Repo:** `2026-07-04--mdlint-qwen3` — 9 commits; `2026-07-04--mdlint-glm5` — 7 commits; `2026-07-04--mdlint-gpt5` — 7 commits; `2026-07-04--mdlint-fable` — 6 commits; `2026-07-04--mdlint-kimi2.7` — 5 commits
**Project reports:** [[PROJECT REPORT - External Agent Validation Loop - Isolated Skill Experiments and Transcript Evaluation]]

### What happened

Five isolated agent/model workspaces implemented the same Markdown link-checking assignment. The verified commits show a repeated pattern in each workspace: create the task/ticket scaffold, produce intern-facing design or implementation notes, implement a pure-stdlib `mdlinkcheck` CLI, and close out with diary/task bookkeeping. This reads as a small external-agent validation exercise, later connected to [[PROJECT REPORT - External Agent Validation Loop - Isolated Skill Experiments and Transcript Evaluation|isolated skill experiments and transcript evaluation]].

**Implementation and acceptance backbone:**
- Qwen produced the largest run: ticket and guide creation (`3ecfafc`), metadata/frontmatter fixes (`ef9d7f1`), saved testing/fix scripts (`d456dde`), an implementation commit reporting **26/26 acceptance tests passing** (`0b61414`), and final task/diary completion (`6b29cc3`, `d0a3e4a`).
- GLM and GPT-5 both built a pure-stdlib CLI after scaffolding their tickets and guides: GLM implemented `mdlinkcheck` at `eb049a3` and cleaned bytecode tracking at `4cd4abd`; GPT-5 implemented its CLI at `64241db` after docs/ticket setup (`3212c8e`, `73bc3d0`, `4344e1c`).
- Fable and Kimi completed parallel deliveries: Fable added the task spec and held-out acceptance suite (`e934851`) before implementing per the MDLC-001 design guide (`81aaaaf`); Kimi implemented parser/resolver/reporter/tests in one commit (`a89f7ab`) and then recorded push/reMarkable completion (`58d7556`).

## 2. ATProto HyperCard browser runtime and static deployment

**Ticket:** no ticket recorded
**Sessions:** implementer `019f2554` (Pi, gpt-5.5)
**Repo:** `2026-07-02--atproto-hypercard` — 6 commits; `2026-03-27--hetzner-k3s` — 3 HyperCard deployment commits out of 4 total
**Project reports:** [[ARTICLE - ATProto HyperCard - Browser Sandboxed FRP Runtime]], [[PROJECT REPORT - Browser Plugin VM - Stateful Feed Middleware Runtime Deep Dive]]

### What happened

The ATProto HyperCard work moved from a static-hosted spike into an interactive browser runtime. The atproto repo records a static host spike (`0baeff3`) and diary (`af9bb9e`), followed by an interactive FRP HyperCard viewer (`0514afa`) and matching diary (`8d957d5`), then a sandbox CSP fix plus expanded sample cards (`57a4bcd`, `d622465`). This stream is directly connected to [[ARTICLE - ATProto HyperCard - Browser Sandboxed FRP Runtime|the later ATProto HyperCard runtime write-up]] and adjacent sandbox/plugin runtime work in [[PROJECT REPORT - Browser Plugin VM - Stateful Feed Middleware Runtime Deep Dive]].

Deployment commits in `hetzner-k3s` mirrored the application progress: add the static site (`6b9737a`), deploy the interactive viewer (`bc47bdb`), and deploy the expanded sample stack (`bd9dc19`). Those commits make the runtime visible outside the local spike repo and tie the application work to the cluster/static-site delivery path.

## 3. Codebase-browser live demo deployment

**Ticket:** `GCB-017` inferred from session title
**Sessions:** implementer `019f2520` (Pi, gpt-5.5)
**Repo:** `2026-03-27--hetzner-k3s` — 1 codebase-browser deployment commit out of 4 total
**Project reports:** [[ARTICLE - Codebase Browser Live Demo - Removing Browser SQLite from a History-Rich Review UI]]

### What happened

The remaining `hetzner-k3s` commit deployed the codebase-browser live demo image (`bc92125`). The active session title identifies this as the `GCB-017 No-sqljs Live Demo PR`, and the related project report frames the same effort as removing browser SQLite from a history-rich code review UI: [[ARTICLE - Codebase Browser Live Demo - Removing Browser SQLite from a History-Rich Review UI|codebase-browser live demo]].

This was a smaller deployment stream than the MDLC bake-off or HyperCard runtime, but it matters because it put an independently developed demo image into the same cluster delivery repository used for the day's HyperCard static-site updates.

## Related Project Reports

- [[PROJECT REPORT - External Agent Validation Loop - Isolated Skill Experiments and Transcript Evaluation]] — context for isolated model/agent implementation experiments and transcript-based comparison.
- [[ARTICLE - ATProto HyperCard - Browser Sandboxed FRP Runtime]] — later deep dive for the sandboxed FRP HyperCard runtime work.
- [[PROJECT REPORT - Browser Plugin VM - Stateful Feed Middleware Runtime Deep Dive]] — adjacent browser sandbox/plugin runtime architecture.
- [[ARTICLE - Codebase Browser Live Demo - Removing Browser SQLite from a History-Rich Review UI]] — project write-up for the no-sqljs codebase-browser live demo.

## Analysis Notes & Caveats

- **Method:** The parent investigation discovered sessions via `--active-since`, converted agent transcripts to minitrace archives, queried the resulting evidence bundle, and verified commit counts against git HEAD-only local-time history. This report uses the supplied bundle only and did not rerun `git` or `go-minitrace`.
- **Spanning sessions:** Several active sessions span beyond 2026-07-04: `019ee82a` (06-21 03:12 → 07-14 16:47), `7a31e95d` (06-26 08:15 → 07-06 15:02), `019f19aa` (06-30 17:54 → 07-05 16:32), `019f2520` (07-02 23:18 → 07-05 22:12), `019f2554` (07-03 00:15 → 07-05 17:02), `b780255a` (07-03 18:59 → 07-05 17:51), and `474d7b7e` (07-03 20:50 → 07-05 20:00). Their transcript activity may include adjacent-day context not attributable to this report day.
- **Codex adapter caveat:** No Codex sessions were present in the 2026-07-04 bundle. If later investigation adds Codex data, its exec/patch operations may be typed as `OTHER` and paths may reside in `arguments_json`; commit facts should still be verified from git.
- **Attribution:** Commit counts are git-verified facts from the bundle. Repo attribution is based on the parent investigation's session file-writes/cwd mapping; `hetzner-k3s` deployment commits are reported even though no listed session has that repository as its cwd.
- **Investigation artifacts:** `scripts/2026/07/30/july-2026-daily-logs`.
