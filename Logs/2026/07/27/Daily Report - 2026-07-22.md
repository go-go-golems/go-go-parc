---
date: 2026-07-27
report_for: 2026-07-22
type: daily-report
generated_by: go-minitrace transcript analysis
tags: [daily-report, log]
---

# Daily Report — 2026-07-22

> Generated 2026-07-27 from go-minitrace transcript analysis of all Pi, Codex, and Claude Code sessions active on 2026-07-22. Evidence: converted minitrace archives, docmgr ticket changelogs, and repository git history.

## Summary

A moderate implementation day across **eight repositories**, driven by **11 coding-agent sessions** (10 Pi, 1 Codex) totaling ~17,000 turns and ~16,000 tool calls. **53 commits** landed across eight repositories. The day's work fell into five streams: (1) tiny-idp local shared two-app compose and signup UX matrix completion, (2) researchctl experiment-plan lifecycle and legacy cleanup, (3) X11 window-manager paint/resize deep-dive articles, (4) k3s GitOps deployment of the Goja Auth host and Mailpit verified signup, and (5) the start of the real TTC RAG study readiness session.

## Sessions Active on 2026-07-22

| Session | Framework | Model | Title | Turns | Tools | Window (UTC) |
|---|---|---|---|---|---|---|
| `019f37ea` | Pi | gpt-5.6-sol | TinyIDP BYOK Phases Zero Through Five | 3,672 | 4,140 | 07-06 → 07-24 |
| `019f7666` | Pi | umans-glm-5.2 | Upwork Agent Job Audit Logs | 4,463 | 4,048 | 07-18 → 07-26 |
| `019f77c2` | Pi | gpt-5.6-terra | Workflow V3 External Operation Ledger | 6,943 | 6,597 | 07-19 → 07-24 |
| `019f7cf3` | Pi | umans-glm-5.2 | Fix code review issues & failing GitHub Actions | 650 | 637 | 07-20 → 07-23 |
| `019f765e` | Codex | gpt-5.6-sol | tiny-idp review / Goja identity microkernel | 1,913 | 7,647 | 07-18 → 07-24 |
| `019f8568` | Pi | umans-glm-5.2 | ChatGPT Discussion File Downloader for surf-go | 811 | 785 | 07-21 → 07-22 |
| `019f8592` | Pi | gpt-5.6-luna | ESP32 Display Validation Proposal | 779 | 778 | 07-21 → 07-23 |
| `019f85d9` | Pi | umans-glm-5.2 | Scrape latest artifacts and upload to live site | 170 | 170 | 07-21 → 07-22 |
| `019f8702` | Pi | umans-glm-5.2 | Set up new laptop on d.local | 312 | 317 | 07-21 → 07-22 03:13 |
| `019f8a59` | Pi | umans-glm-5.2 | Launch go-go-wm in a xephyr | 11 | 14 | 07-22 15:02 → 15:03 |
| `019f8bf1` | Pi | gpt-5.6-sol | Real TTC RAG Study Readiness | 2,879 | 3,178 | 07-22 22:27 → 07-24 |

## Commit Volume (git-verified)

| Repository | Commits on 07-22 |
|---|---|
| `go-go-golems/tiny-idp` | 22 |
| `go-go-golems/researchctl` | 10 |
| `go-go-golems/go-go-parc` | 8 |
| `2026-03-27--hetzner-k3s` | 7 |
| `go-go-golems/go-go-goja` | 2 |
| `go-go-golems/upwork` | 2 |
| `go-go-golems/homebrew-go-go-go` | 1 |
| `go-go-golems/rag-evaluation-system` | 1 |
| **Total** | **53** |

---

## 1. tiny-idp Local Shared Two-App Compose & Signup UX Matrix

**Ticket:** `TINYIDP-LOCAL-COMPOSE-2026-07-22` (tiny-idp)
**Sessions:** Pi `019f37ea` (gpt-5.6-sol) + Codex `019f765e` (gpt-5.6-sol)
**Repos:** `~/code/wesen/go-go-golems/tiny-idp` — 22 commits; `go-go-goja` — 2 commits

### What happened

The day closed the local shared two-app compose ticket and completed the authentication UX matrix, with email-code recovery, browser rate-limit rendering, and consent-redirect fixes. The go-go-goja repo remediated a `golang.org/x/text` vulnerability and shipped the auth host.

**Local compose & topology:**
- Made fresh local topology deterministic (`69f3283`); enforced durable invitation lifecycle (`48153c1`)
- Added SMTP message date header (`34f2b54`); isolated password work from lockout policy (`c52cc50`)
- Validated signup capability paths (`1925a40`); rejected capabilities on signup entry (`5aa8c4e`)
- Closed local compose ticket (`5f5509e`); recorded reMarkable publication (`1d693fd`)

**Signup UX matrix:**
- Completed signup validation matrix (`647d540`); recorded signup matrix completion (`071396d`)
- Recovered email verification after attempt exhaustion (`a41087c`); covered email code exhaustion recovery (`263603a`)
- Rendered browser rate limits safely (`595742b`); recorded browser throttling diagnosis (`f2ddb82`)
- Allowed post-signup consent redirect (`cfc1d08`); recorded consent redirect fix (`486bfaf`)
- Added Message Desk signup journey (`eb548ea`); closed authentication UX matrix (`573c63b`)

**go-go-goja:**
- Remediated `golang.org/x/text` vulnerability (`e970f6b`); merged PR #102 (`32a94aa`)

---

## 2. researchctl Experiment-Plan Lifecycle & Legacy Cleanup

**Ticket:** `RESEARCHCTL-EXPERIMENT-PLAN` (researchctl)
**Session:** Pi `019f77c2` (gpt-5.6-terra)
**Repo:** `~/code/wesen/go-go-golems/researchctl` — 10 commits

### What happened

The Workflow V3 session designed and implemented a generic experiment-plan lifecycle, then audited and cleaned up legacy researchctl code.

**Experiment-plan lifecycle:**
- Designed scriptable experiment platform convergence (`81ad2f3`)
- Created Researchctl legacy cleanup audit (`a990420`); classified legacy cleanup (`a756140`)
- Finalized cleanup handoff (`3d378e8`); recorded cleanup execution (`8a6936a`)
- Added generic experiment plans (`83e83b5`); recorded core implementation (`448975c`)
- Completed experiment plan lifecycle (`10dc747`); recorded lifecycle diary (`6e44ccc`)
- Removed manifest import prototype (`2384a94`)

---

## 3. X11 Window-Manager Deep-Dive Articles

**Session:** Pi `019f7cf3` (umans-glm-5.2)
**Repo:** `~/code/wesen/go-go-golems/go-go-parc` — 8 commits

### What happened

The go-go-wm code-review session produced a series of X11 window-manager performance deep-dive articles, plus ChatGPT transcript archiving and a Workflow V3 instrumentation report.

**X11 deep dives:**
- Measuring before optimizing an X11 window manager resize path (`817ec72`)
- Completed the X11 resize deep dive with implementation results (`6c2c303`)
- Rewrote around five diagnoses; corrected the harness-bug finding (`99f3574`)
- Optimizing an X11 window manager paint path (`74af197`)

**Vault docs:**
- Added Workflow V3 operation instrumentation report (`2ecf70e`)
- Added ChatGPT output artifacts from PBUI widget DSL conversation (`5b978c6`)
- Restructured ChatGPT outputs alongside transcripts + reMarkable upload (`fe8349d`)
- Archived ChatGPT transcripts for 2026-07-22 — 15 transcripts, 99 files (`c2d1f91`)

---

## 4. k3s GitOps: Goja Auth Host & Mailpit Verified Signup

**Session:** Pi `019f85d9` (umans-glm-5.2)
**Repo:** `~/code/wesen/2026-03-27--hetzner-k3s` — 7 commits

### What happened

GitOps deployment of the Goja Auth host and a private Mailpit-backed verified signup flow, plus the tiny-message-desk-prod rollout.

- Deployed tiny-message-desk-prod using `ghcr.io/go-go-golems/tiny-idp:sha-...` (`e2aea5b`)
- Deployed private Mailpit verified signup flow (`78308e6`); documented verified signup acceptance (`62025f1`)
- Deployed Goja Auth host `sha-32a94aa` (`0c9a27d`); merged deploy PRs #193–#195

**Homebrew:** Brew cask update for tinyidp version v0.0.4 (`dfc3181`).

---

## 5. Real TTC RAG Study Readiness (start)

**Session:** Pi `019f8bf1` (gpt-5.6-sol)
**Repo:** (no commits yet on 07-22; session started 22:27 UTC)

### What happened

A new session began the real TTC RAG study readiness work, continuing into 07-23/24. The upwork session also added triage comments and fact pinning (`4fcac7b`, `80f8f95`), and the rag-evaluation-system added a DataTable multiselect design ticket (`d36be0b`).

---

## Analysis Notes & Caveats

- **Method:** Sessions discovered via `go-minitrace discover --active-since 2026-07-22` across Pi, Codex, and Claude Code stores, converted to minitrace archives, then queried with `session-list`. Commit counts verified directly against repository git history (HEAD only, local timezone).
- **Spanning sessions:** Six sessions (`019f37ea`, `019f7666`, `019f77c2`, `019f7cf3`, `019f765e`, `019f8568`) started before 07-22 and continued past it. Their 07-22 activity is included; commit attribution is by commit-date.
- **Codex adapter caveat:** For the Codex session (`019f765e`), `operation_type` is `OTHER` for exec/patch operations. The tiny-idp commits were verified via git.
- **No Claude Code sessions** were active on 07-22.
- **Attribution:** All commit counts are git-verified against the live repositories. Changelog step numbers come from the docmgr ticket changelogs, corroborated by commit subjects.
- **Investigation artifacts:** Converted archives, source lists, and per-day commit subjects are stored under `go-go-parc/scripts/2026/07/27/daily-report-week-2026-07-21-to-27/`.
