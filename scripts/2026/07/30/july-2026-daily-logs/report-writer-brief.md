# Daily Report Writer Brief (July 2026 batch)

You are writing ONE evidence-backed daily work report for a single day in July 2026,
from a pre-computed evidence bundle. The parent agent has already done ALL
discovery, conversion, go-minitrace querying, git verification, and repo
attribution. **Do NOT run `git` or `go-minitrace`.** All evidence you need is in
the bundle. Do NOT commit anything — the parent commits the whole batch once at
the end.

## Inputs (read these three files)

1. **Your day's bundle** (the path is given in your task):
   `scripts/2026/07/30/july-2026-daily-logs/bundles/day-YYYY-MM-DD.json`
   Fields:
   - `day` — the target day (YYYY-MM-DD)
   - `sessions` — list of `{short, id, framework, model, title, cwd, turns, tools, started_at, last_activity_at, window}`. These are the agent sessions active on that day (Pi, Codex, Claude Code). `window` is a pre-formatted "MM-DD HH:MM → MM-DD HH:MM" UTC string.
   - `commit_counts` — `{repo_path: N}` of git-verified (HEAD-only, local tz) commits in that repo on that day. **These are facts.**
   - `total_commits` — sum of `commit_counts`.
   - `commit_subjects` — `{repo_path: ["hash|date|subject", ...]}`. **This is your narrative backbone.** Read the subjects to understand what each repo's work was, and group them into work streams.
   - `project_reports` — list of `"YYYY-MM-DD|Note Name"` strings: every project report / article / PROJ note in the Obsidian vault's `Projects/2026/07/` tree. Use these for crosslinks (see below).

2. **Report template**: `~/.pi/agent/skills/daily-log/references/report-template.md`
3. **Evidence hierarchy**: `~/.pi/agent/skills/daily-log/references/evidence-hierarchy.md`

## Output

Write exactly ONE file:
```
/home/manuel/code/wesen/go-go-golems/go-go-parc/Logs/2026/07/30/Daily Report - <TARGET_DAY>.md
```
where `<TARGET_DAY>` is the bundle's `day` (e.g. `2026-07-15`). Create the file
with `write`. Do not touch any other file. Do not stage or commit.

## Frontmatter

```yaml
---
date: 2026-07-30
report_for: <TARGET_DAY>
type: daily-report
generated_by: go-minitrace transcript analysis
tags: [daily-report, log]
---
```

## Required sections (follow the template)

1. **Title + provenance note** — `# Daily Report — <TARGET_DAY>` and the `>` blockquote stating evidence sources (converted minitrace archives, git history). Mention all three frameworks where present.
2. **Summary** — one paragraph: heavy/moderate/light, number of major projects, number of sessions (break down Pi/Codex/Claude Code from the bundle), total turns/tools (sum or estimate from sessions), **total commits** (lead with the verified number from `total_commits`), number of repos, and the 2–5 work streams.
3. **Sessions Active on <TARGET_DAY>** — a markdown table. Columns: `Session` (the `short` id, backticked), `Framework`, `Model`, `Title`, `Turns`, `Tools`, `Window (UTC)` (use the `window` field). If there are many sessions (e.g. >12), you may list the most significant and collapse a trailing cluster as a single `+ N <Framework> sessions` row with aggregated turns/tools — but only if it keeps the table readable. Prefer listing all when feasible. Use `None`/empty for missing title/model.
4. **Commit Volume (git-verified)** — table of `Repository` (basename of the repo path, or a short readable form like `go-go-golems/go-go-datadrop`) and `Commits on MM-DD`, sorted descending, with a `**Total**` row. Use `total_commits`.
5. **One section per work stream** (2–5 streams). For each:
   - Header `## N. <Work stream title>`
   - Lines: `**Ticket:**` (infer from commit subjects if a ticket ID like DATADROP-11 appears; else omit or say "no ticket recorded"), `**Sessions:**` (pick the session(s) whose cwd/title match — use `short` id, framework, model), `**Repo:**` (basename) `— N commits`, `**Project reports:**` wikilinks (see crosslink rules).
   - `### What happened` — 1–2 paragraphs synthesizing the commit subjects into a narrative. Group related commits as bullets with commit hashes (`abc1234`) where they add precision. Use inline wikilinks to connect to related/preceding work.
6. **Related Project Reports** — bulleted index of the vault project reports you linked, as `[[Note Name]] — one-phrase description`.
7. **Analysis Notes & Caveats** — required. Include: method (discover via `--active-since`, converted, queried; commit counts verified against git HEAD-only local tz); spanning sessions (list any session whose `window` starts before or ends after the target day — common for long Pi/Claude Code sessions); Codex adapter caveat (if Codex sessions present: operation_type OTHER for exec/patch, paths may be in arguments_json, commits verified via git); attribution note (commits are git-verified facts; repos attributed from session file-writes/cwd, which can attribute commits even when no session cwd equals the repo, e.g. work done from a workspace clone or a parent cwd); investigation artifacts path (`scripts/2026/07/30/july-2026-daily-logs`).
   - **For 2026-07-30 only:** add a **Partial day** caveat — the report covers activity through the time of generation (~late evening UTC); later commits/sessions are not captured.

## Crosslink rules (important)

The vault's `Projects/2026/07/<DD>/` notes document work streams as long-form
reports. Crosslink them with Obsidian wikilinks (`[[Note Name]]` or
`[[Note Name|alias]]`), NEVER markdown links.

- From `project_reports` (each `"YYYY-MM-DD|Note Name"`), pick notes whose **topic matches** a work stream's repo/subject, preferring notes whose date is **on or within a few days after** the target day (deep-dives are usually written shortly after the work). A note dated exactly on the target day that documents that day's repo is the strongest match.
- Match by keyword in the note name: the repo name (e.g. `go-go-datadrop`, `glazed`, `devctl`, `tiny-idp`, `serve-artifacts`, `hetzner-k3s`, `rag-ttc`, `go-minitrace`, `go-go-wm`, `prompto`, `widget`, `goja`, `datadrop`, `zitadel`), a ticket ID, or a concept from the commit subjects.
- Do not link a note that has no topical connection to the day's work. When unsure, prefer the most topically relevant same-week note.
- Every work-stream section must have a `**Project reports:**` line (it may be omitted only if no project report matches — then say `**Project reports:** _(none in vault)_`).
- Add inline wikilinks in the "What happened" prose to connect to preceding/following work where natural.

## Writing rules (strict)

- **Lead with verified numbers.** The commit counts are git facts — never invent or round them. `total_commits` is the headline.
- **Commit subjects are the backbone.** Group them logically into streams; do not dump every commit verbatim unless the day is small (≤ ~20 commits). Use commit hashes for precision on key commits.
- **Never report a commit that isn't in `commit_subjects`.** Do not invent hashes.
- **Classify sessions** by role where obvious from title/cwd: implementer, reviewer, investigator, reference-only. A session with a huge turn count and matching repo is an implementer; a short "check X" or "address review" session is lighter.
- **Caveats are mandatory and honest.** If a repo's commits lack a same-cwd session (attributed via file-writes or parent cwd), you may still report them (they are git-verified and the subjects show real agent work) but it's fine to note it.
- **Tone:** match the existing reports in the vault (concise, evidence-led, no hype).
- **Wikilinks only** for project report crosslinks.
- Use the bundle's `window` strings verbatim in the sessions table.

## Edge cases

- If a day has very few commits/sessions (e.g. a weekend), write a short honest report: small sessions table, one or two streams or a single "Other Work" note, and a caveat that it was a light day.
- If `commit_subjects` is empty for a repo in `commit_counts` (shouldn't happen), omit that repo and flag it in caveats.
- Titles that are `None`/missing: show as `—` or a short inferred label.

When done, return a one-line confirmation with the output path, the total commits, and the number of work streams you wrote.
