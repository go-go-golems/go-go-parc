---
title: "Project Report — Tracing Profile-Loading Adoption Across 119 Coding-Agent Sessions with go-minitrace"
aliases:
  - Profile Loading Transcript Analysis Report
  - go-minitrace Profile Loading Adoption Report
  - Profile Loading Playbook Transcript Method
tags:
  - project-report
  - article
  - go-minitrace
  - transcript-analysis
  - pinocchio
  - geppetto
  - profile-loading
  - coding-agent
  - sqlite
status: active
type: project-report
created: "2026-07-25"
repo: /home/manuel/code/wesen/claw-stuff
source_ticket: PROFILE-LOADING-PLAYBOOK-2026-07-25
source_report: /home/manuel/code/wesen/claw-stuff/ttmp/2026/07/25/PROFILE-LOADING-PLAYBOOK-2026-07-25--playbook-loading-pinocchio-geppetto-profiles-for-llm-and-embeddings-inference/analysis/01-session-attribution-analysis.md
related_docs:
  - /home/manuel/code/wesen/claw-stuff/scripts/2026/07/25/profile-loading-playbook/queries/
  - /home/manuel/code/wesen/go-go-golems/go-go-parc/Research/playbooks/loading-pinocchio-geppetto-profiles-for-llm-and-embeddings-inference.md
---

# Project Report — Tracing Profile-Loading Adoption Across 119 Coding-Agent Sessions with go-minitrace

## 1. Purpose and conclusions

This report documents how a coding-agent transcript corpus was reduced to an evidence-backed playbook. The subject is not the Pinocchio/Geppetto profile-loading mechanism itself — that is recorded in the companion playbook [[loading-pinocchio-geppetto-profiles-for-llm-and-embeddings-inference]]. The subject here is the method: how 119 archived sessions were discovered, narrowed, queried, and attributed, and how the distinction between building a mechanism and adopting one was enforced through query design rather than through narrative judgment.

The source ticket is `PROFILE-LOADING-PLAYBOOK-2026-07-25` in the `claw-stuff` repository. The committed queries, source lists, and result JSON live under `scripts/2026/07/25/profile-loading-playbook/`. This note preserves the project-level narrative of the analysis so that a future reader can reproduce the pipeline, audit the attribution, and adapt the query patterns to a different "who implemented this, and who else adopted it" question.

> [!summary]
> The investigation converted 99 Pi and 20 Codex sessions into normalized archives and ran 8 SQL queries to attribute two distinct populations: 6 sessions that built the profile-loading mechanism in `pinocchio`/`geppetto`, and 6 sessions that adopted it into other codebases.
>
> Attribution was anchored to git history first, then narrowed with transcripts. Commit hashes captured from transcript tool results were verified against the live repositories; only repository-verified hashes count as proven implementation.
>
> The decisive query was not the broad symbol match (109 raw `profilebootstrap` hits) but a precise "writes to known consumer files" query built from filesystem ground truth. Broad queries over-matched; precise queries built from external state attributed cleanly.

The short conclusion is that transcript-based attribution separates cleanly into two phases only when the question is stated in advance and the evidence standard is fixed before searching. The first phase — "who built this" — was answered by joining transcript writes to repository commits. The second phase — "who adopted this into their own code" — could not be answered by grepping transcripts for symbols, because the symbol `profilebootstrap` appears in 109 sessions across review, investigation, and implementation contexts. It was answered by inverting the search: starting from the filesystem to find which Go files import the relevant packages, then matching those file paths back against transcript writes. That inversion is the generalizable finding of this report.

## 2. The question and the evidence standard

The work began with a concrete request: find the sessions that added profile loading from Pinocchio/Geppetto for LLM and embeddings inference, and turn the result into a playbook. Before searching any transcript, the evidence standard was fixed. A session would count as an implementer only if the transcript showed repository-changing tool calls — file writes or patches — against the target packages, and those writes correlated with commits verifiable in the live repository.

The evidence hierarchy, applied before any query ran, was:

- **Strong:** a write or patch operation targeting an exact file in `pinocchio/pkg/cmds/profilebootstrap`, `geppetto/pkg/cli/bootstrap`, or `geppetto/pkg/sections`, combined with a commit hash captured in the transcript result and verified with `git show`.
- **Supporting:** an exec command whose workdir is the target repository, a user instruction requesting the implementation, or file reads around the relevant operation.
- **Weak:** cwd alone, a filename or title alone, keyword frequency, or quoted transcript content.

The standard exists to prevent a specific failure: counting a session that merely *mentions* a symbol as one that *implemented* it. Review sessions receive the full history they are assessing, so their text contains every target signature. Keyword frequency is unreliable precisely in the case where it feels most informative.

A second question arrived partway through: which sessions adopted the mechanism into their own codebase, as distinct from those that built it. That question required a different evidence standard, defined in Section 9. The two questions are not symmetric, and treating them as one would have produced a single muddled population.

## 3. Data source

The native stores are the standard local transcript trees:

- Pi: `~/.pi/agent/sessions/--<slugged-cwd>--/<timestamp>_<uuid>.jsonl`
- Codex: `~/.codex/sessions/YYYY/MM/DD/rollout-<timestamp>-<uuid>.jsonl`

Native files were never modified. They were converted into an investigation-specific output directory under `scripts/2026/07/25/profile-loading-playbook/archives/`. The investigation directory is self-contained: source lists, queries, results, and archives all live there, so the analysis can be re-run or audited without touching the native stores.

The final corpus is 119 archives: 99 Pi and 20 Codex. That number is the result of narrowing, not of exhaustive conversion. The native stores contain thousands of sessions; converting all of them would have produced a database too large to reason about and would have introduced review and quotation false positives. The narrowing happened in two stages, described in Sections 5 and 9.

## 4. The external-state anchor

The first action was not a transcript search. It was a git log against both target repositories, filtered to profile-related subjects:

```bash
git -C geppetto log --date=iso-strict --pretty='%h%x09%aI%x09%s' --all \
  | rg -i 'profilebootstrap|profile.bootstrap|profile loading|embeddings.*profile'
git -C pinocchio log --date=iso-strict --pretty='%h%x09%aI%x09%s' --all \
  | rg -i 'profilebootstrap|ResolveCLIEngineSettings|MapPinocchioConfigFile'
```

This produced an implementation timeline before any transcript was opened:

| Window | Repository | Representative commits |
|---|---|---|
| 2026-02-23 → 02-25 | geppetto | `0f7a7a96` `js: hard-cut engines.fromProfile to profile registry` |
| 2026-03-18 → 03-19 | pinocchio | `495787d`/`81a17d3` `align pinocchio js profile loading with cli defaults`; `d285182` `refactor(profilebootstrap): wrap geppetto cli bootstrap` |
| 2026-04-14 → 04-18 | both | `56bb1f6` `profilebootstrap: add layered local config plan`; `6d2c944` `bootstrap: remove duplicated profile registry loading`; `a3e6603` `docs: record profile registry bootstrap implementation` |
| 2026-05-23 | geppetto | `bf38f712` `Add embedding profile validation tests`; `b1189660` merge of the embeddings profile PR |

The timeline did three things at once. It bounded the time windows to search. It supplied distinctive signatures (commit hashes, changed paths, symbols) that are unlikely to occur in review prose. And it established the verification target: any hash a transcript claimed to have committed would be checked against these objects with `git show`.

Anchoring to external state first is the single most important methodological choice in this investigation. A transcript can claim a commit succeeded; only the repository can confirm the commit object exists.

## 5. Discovery and content shortlisting

With the timeline as a filter, the next step was structured discovery plus raw content grep. The grep used distinctive symbols drawn from the user's own description of the work and from the git diff:

- `profilebootstrap` (package and commit prefix)
- `GetPinocchioCommandMiddlewares`
- `ResolveCLIEngineSettings`
- `MapPinocchioConfigFile`
- `profile_selection.go`

Each signature was grepped across both native stores and saved as a per-signature source list:

```bash
rg -l -F 'profilebootstrap' ~/.pi/agent/sessions ~/.codex/sessions > sources/sig-profilebootstrap.txt
```

The raw counts were immediately informative and immediately misleading. `profilebootstrap` matched 109 files. `profile_selection.go` matched 79. These numbers are shortlist signals, not attribution. The skill's own reference is explicit on this point: a cwd match, filename count, or topic count is never sufficient proof that a session implemented a change.

The reason is structural. `profilebootstrap` is both a package name and a commit prefix. It appears in system context, in generated reports, in review sessions that quote the implementation, and in investigation sessions like this one. A session that reads the code to write a report contains the same symbols as a session that wrote the code. The grep could not distinguish them. The narrowing had to happen at the query layer, against repository-changing operations.

From the per-signature lists, a focused set was built by intersecting with the workspace directory names implied by the git timeline. This produced `sources/pi-focused.txt` (82 sessions) and `sources/codex-focused.txt` (20 sessions). These were converted:

```bash
go-minitrace convert pi --source-list sources/pi-focused.txt --output-dir archives/pi
go-minitrace convert codex --source-list sources/codex-focused.txt \
  --output-dir archives/codex --run-record archives/codex/conversion-run.json
```

Conversion produced 102 archives. Validation reported only `conversion-receipt-output-missing` findings for two Codex archives written late in the run; this is cosmetic, because the receipt was written before those archive files existed. The archives themselves were valid.

## 6. The relevance-score query and its limits

The first query (`queries/01-profile-relevance.sql`) scored each session by counting tool calls whose command or file path touched the profile-loading symbols, then ordered sessions by that score. The result was a ranking, not an attribution.

```
session_id                           fw    cmd  file wr   ex   turns cwd
019d05b6-dec4-7072-bca1-0a0a1785d6e9 codex  303  110  368  921  1274 ~/workspaces/2026-03-17/add-opinionated-apis
2803ce85-fb9d-4181-95c8-e30de070b3a3 pi     173   66  146  411   639 ~/workspaces/2026-04-18/fix-piniocchio-profile-env
019d05b6...                          codex  108   20  209  994   430 ~/workspaces/2026-03-17/add-opinionated-apis
...
```

The ranking correctly surfaced the implementer sessions at the top. It also surfaced sessions that merely had high topic counts. A session with 303 command hits and 110 file hits is a strong candidate, but the score does not say whether those hits were writes, reads, or quoted text. The score is a sorting device. It reduced 102 sessions to a shortlist of roughly fifteen worth inspecting, but it could not finish the attribution.

This is the limit of any relevance score built from symbol frequency. The score measures exposure to a topic, not contribution to a codebase. Two sessions can have identical scores and opposite roles: one wrote the code, the other read it to write a report.

## 7. The decisive query: distinct files written

The attribution was settled by `queries/03-distinct-profile-files-written.sql`, which selected distinct `NEW` and `MODIFY` operations whose file paths matched the profile-loading packages, grouped by session. This query does work that symbol frequency cannot: it names the exact files each session changed.

```
019d05b6 (9 files):
  geppetto/pkg/cli/bootstrap/profile_selection.go
  geppetto/pkg/sections/profile_sections.go
  pinocchio/pkg/cmds/helpers/profile_engine_settings.go
  pinocchio/pkg/cmds/helpers/profile_selection.go
  pinocchio/pkg/cmds/profilebootstrap/engine_settings.go
  pinocchio/pkg/cmds/profilebootstrap/engine_settings_test.go
  pinocchio/pkg/cmds/profilebootstrap/inference_settings_trace.go
  pinocchio/pkg/cmds/profilebootstrap/profile_selection.go
  pinocchio/pkg/cmds/profilebootstrap/profile_selection_test.go

2803ce85 (18 files):
  geppetto/pkg/cli/bootstrap/{bootstrap_test,engine_settings,inference_debug,
    profile_registry_defaults,profile_runtime,profile_selection}.go
  pinocchio/pkg/cmds/profilebootstrap/{engine_settings,...,repositories}.go
  + the canonical-profile-runtime-API docmgr ticket docs
```

Two properties of this query made it decisive. First, it filtered on `operation_type IN ('NEW','MODIFY')`, excluding reads and searches. A session that only read `profile_selection.go` does not appear. Second, it grouped by session and listed distinct paths, so a session that edited the same file fifteen times counted once. The result was a small, readable table of "session → files it actually changed."

The query produced nine sessions that wrote at least one profile-loading file. Six of these were the implementers; three were follow-on or secondary. The distinction between implementer and secondary was made by cross-referencing with git, not by re-reading the transcript.

## 8. Commit verification

`queries/04-git-commits.sql` extracted exec calls whose command text contained `git commit`, `git rev-parse`, or `git log`, along with their result snippets. The result snippets contained candidate commit hashes. The hashes were then verified against the live repositories:

```bash
git -C geppetto show --no-patch --date=iso-strict --format='%H%n%aI%n%s' c2b5e4a
# c2b5e4a46a52a8f1b991e95b09b866916796130e
# 2026-03-19T08:11:44-04:00
# refactor(examples): reuse shared profile settings section
```

Four counts were kept separate, as the skill's attribution reference requires:

| Count | Meaning |
|---|---|
| Text matches | Tool rows whose serialized arguments contain `git commit` |
| Command attempts | Exec/shell calls whose actual command invokes `git commit` |
| Confirmed successful attempts | Attempts with a verified nested zero exit status |
| Verified commit hashes | Git objects present in the target repository, tied to the run |

Only the fourth count is an attribution. The first count is the largest; the fourth is the smallest. Reporting the first as the fourth is the canonical attribution error, and the query structure exists to prevent it.

Verified hashes anchored the implementer sessions:

- `019d05b6` → geppetto `c2b5e4a`, `34401d6`
- `2803ce85` → pinocchio `6d2c944`, `a3e6603`
- `019e55d6` → geppetto `bf38f712` (embeddings validation tests)

The user turns captured alongside the commits revealed the design intent verbatim. Session `2803ce85`, turn 75: *"the fix should be in geppetto if possible so that every tool that uses that logic can use it. The only thing pinocchio should do is provide the app name."* Session `019e55d6`, turn 54: *"use ~/.config/pinocchio/profiles.yaml, no os.Getenv(\"OPENAI_API_KEY\"), remove them all from everywhere."* These turns did not prove implementation; they explained the intent behind implementation that the writes and commits had already proven.

## 9. The adoption question and the inverted search

The second question — which sessions adopted the mechanism into their own codebase — broke the symmetry of the first. The building sessions were found by grepping transcripts for symbols. The adoption sessions could not be found that way, for the same reason: the symbol appears everywhere.

The search was inverted. Instead of starting from transcripts, it started from the filesystem. A single grep found every Go file that imports the relevant packages, excluding the mechanism repositories themselves:

```bash
rg -l 'go-go-golems/pinocchio/pkg/cmds/profilebootstrap' \
  /home/manuel/code/wesen /home/manuel/workspaces \
  | rg -v '/(pinocchio|geppetto)/'
rg -l 'go-go-golems/geppetto/pkg/cli/bootstrap' \
  /home/manuel/code/wesen /home/manuel/workspaces \
  | rg -v '/geppetto/'
```

This produced a closed set of known consumer files across eight codebases: `cozodb-editor/backend/main.go`, `readwise-viewer/pkg/profilebootstrap/bootstrap.go`, `css-visual-diff/internal/cssvisualdiff/llm/bootstrap.go`, `wesen-os/cmd/wesen-os-launcher/profile_bootstrap.go`, `chatbot-overlay-glm/cmd/chat-overlay/cmds/serve.go`, and others. Each is a real file on disk that imports the mechanism.

With a closed set of target file paths, attribution became a precise match. `queries/07-consumer-adoption-precise.sql` selected `NEW`/`MODIFY` operations whose file paths matched the known consumer files, joined to the session's working directory:

```sql
SELECT c.session_id, s.working_directory AS cwd, c.turn_index, c.operation_type, c.file_path
FROM tool_calls c JOIN sessions s USING (session_id)
WHERE c.operation_type IN ('NEW','MODIFY')
  AND ( lower(c.file_path) LIKE '%cozodb-editor/backend/main.go%'
     OR lower(c.file_path) LIKE '%readwise-viewer%profilebootstrap/bootstrap.go%'
     OR lower(c.file_path) LIKE '%css-visual-diff%llm/bootstrap.go%'
     ... )
```

The query returned 64 rows across five sessions, each writing the consumer bootstrap files in a non-mechanism repository. A broad query (`queries/06`) that matched on import strings in `arguments_json` had over-matched pinocchio-internal files; the precise, filesystem-grounded query did not. This is the generalizable technique: when the question is "who adopted X into their own code," anchor to the consumer file paths found on disk, not to import strings in session text.

The adoption commits were verified the same way as the implementation commits. Readwise-viewer produced four: `a1faccf` `Add Geppetto embedding profile smoke command`, `91bdbdd`, `74eb3b4`, `b92867d` `Use Geppetto embedding profile validation`. The css-visual-diff adoption produced `b667bcd` `Add Pinocchio profile bootstrap for LLM settings`.

Two adopters were filesystem-confirmed but session-unresolved. The css-visual-diff `llm/bootstrap.go` file exists and its commit `b667bcd` is verified, but no converted session wrote that exact path; the converted css-visual-diff sessions wrote a different file (`internal/cssvisualdiff/verbcli/bootstrap.go`). The book-ocr `geppetto_ocr.go` import is confirmed on disk, but no session that wrote it was converted. These were documented as unresolved rather than forced into a match. Forcing a match would have violated the evidence standard; documenting the limit preserves it.

## 10. The query inventory

Eight queries were written and saved. Each answers a distinct sub-question, and together they form a reusable pipeline for a "who did this" investigation.

| Query | Purpose | Why it is necessary |
|---|---|---|
| `01-profile-relevance.sql` | Rank sessions by symbol-hit count | Shortlists 102 → ~15; cannot attribute |
| `02-profile-writes-and-commands.sql` | All writes/patches + exec commands targeting the packages | Broad repository-changing evidence |
| `03-distinct-profile-files-written.sql` | Distinct files written per session | Decisive for implementer attribution |
| `04-git-commits.sql` | Git commit/rev-parse calls with result hashes | Source of candidate commit hashes |
| `05-key-user-turns.sql` | First and key user turns for top sessions | Captures design intent verbatim |
| `06-consumer-adoption-writes.sql` | Broad: .go writes importing the packages, excluding mechanism repos | Over-matches; kept for breadth |
| `07-consumer-adoption-precise.sql` | Writes to known consumer files from filesystem ground truth | Decisive for adoption attribution |
| `08-consumer-user-turns.sql` | User turns for adoption sessions | Captures adoption intent |

The pairing of `06` (broad) and `07` (precise) is deliberate. The broad query establishes that consumer adoption activity exists across many sessions. The precise query, built from external state, attributes it. A single broad query would have produced a noisy list with false positives; a single precise query without the broad one first would have hidden how much over-matching the broad approach generates. Keeping both makes the narrowing legible to an auditor.

## 11. What the queries do not prove

Several limits were enforced throughout and are worth stating directly.

SQL finds candidate turns and tool calls. It does not prove authorship by itself. Every attribution in the report rests on the join of a transcript write to a repository-verified commit, not on a row count.

A `success = 1` value on a Codex exec call may describe transport success rather than the success of the nested process. The commit verification path ignores the success flag and checks the repository object instead.

The `sessions.source_path` field is importer provenance, not necessarily the original native path. Native paths are preserved in the saved source lists, so provenance can be audited independently of the archive.

The relevance score (Query 01) and the broad adoption query (Query 06) both over-match. They are shortlisting tools. The decisive queries (03 and 07) filter on operation type and on exact external file paths. Treating the shortlisting queries as attribution queries would reproduce the exact error the evidence standard was designed to prevent.

The two unresolved adopters (css-visual-diff `llm/bootstrap.go`, book-ocr `geppetto_ocr.go`) are real adoptions verified on disk. The absence of a matching converted session means the session that wrote them was not converted, predates the converted set, or was manual. The limit is in the converted corpus, not in the method.

## 12. How to reproduce the analysis

The investigation is fully reproducible from the committed artifacts.

```bash
# 1. Rebuild the source lists from the native stores
cd scripts/2026/07/25/profile-loading-playbook
for sig in profilebootstrap GetPinocchioCommandMiddlewares \
           ResolveCLIEngineSettings MapPinocchioConfigFile profile_selection.go; do
  rg -l -F "$sig" ~/.pi/agent/sessions ~/.codex/sessions > "sources/sig-${sig//\//_}.txt"
done

# 2. Convert the focused sets
go-minitrace convert pi --source-list sources/pi-focused.txt --output-dir archives/pi
go-minitrace convert codex --source-list sources/codex-focused.txt --output-dir archives/codex

# 3. Run the attribution queries
GLOB='./archives/*/active/*/*.minitrace.json'
go-minitrace query run --archive-glob "$GLOB" \
  --sql-file queries/03-distinct-profile-files-written.sql --output json > results/q3-files.json
go-minitrace query run --archive-glob "$GLOB" \
  --sql-file queries/07-consumer-adoption-precise.sql --output json > results/q7-consumer-precise.json

# 4. Verify commit hashes against the live repositories
git -C /home/manuel/code/wesen/go-go-golems/geppetto show --no-patch c2b5e4a 34401d6 bf38f712
git -C /home/manuel/code/wesen/go-go-golems/pinocchio show --no-patch 6d2c944 a3e6603
git -C /home/manuel/code/wesen/2026-05-21--readwise-viewer show --stat a1faccf b92867d
```

Every result JSON is committed alongside its query, so an auditor can compare a claim to the rows that produced it without re-running the database build. The source lists preserve the native paths, so conversion provenance is auditable even though `sessions.source_path` is importer-derived.

## 13. Recommended next work

The pipeline generalizes to any "who implemented this, and who adopted it" question over a transcript corpus. Three improvements would make it more durable.

First, the filesystem-grounded adoption search should be packaged as a reusable step. The inversion — start from the import graph on disk, then match against transcript writes — is the technique that made the adoption attribution clean. It currently lives as a one-off grep plus a precise SQL query. Encapsulating it as a query command would make it available to the next investigation without re-deriving the approach.

Second, the two unresolved adopters point at a corpus gap. The css-visual-diff `llm/bootstrap.go` commit `b667bcd` is dated 2026-04-21, but the converted css-visual-diff sessions are later. Converting sessions active before that date, using `--active-since`, would close the gap. The same applies to book-ocr. An unresolved attribution is acceptable; closing it is better.

Third, the four-count commit separation (text matches, command attempts, confirmed attempts, verified hashes) should be enforced structurally rather than by discipline. A query command that emits all four counts in one pass, with the verified-hash count clearly labeled as the only attribution count, would prevent the canonical error at the query layer rather than at the reporting layer.

## 14. Final interpretation

The investigation produced a playbook and an attribution analysis. The playbook records what the profile-loading mechanism is and how to adopt it. The attribution analysis records who built it and who adopted it. This report records how those conclusions were reached.

The methodological claim is narrow and worth restating. Transcript-based attribution works when the question is stated in advance, the evidence standard is fixed before searching, and external state — git history and the filesystem — anchors every conclusion. Symbol frequency narrows; it does not conclude. The decisive evidence is always the join between a transcript operation and a verified repository object. When the question turns from building to adopting, the search inverts: the filesystem, not the transcript, supplies the target set, and the transcript is queried only to attribute what the filesystem already proved exists.

## 15. Updating the skill from the investigation

An investigation that produces a reusable method should leave the method reusable. The transcript-analysis skill is a set of files under `~/.pi/agent/skills/go-minitrace-transcript-analysis/`: a `SKILL.md` entry point and three reference documents. After this investigation closed, the skill was audited against what the work had actually surfaced, and three gaps were found. This section records what was added, what was left alone, and why.

The audit was structured as a comparison between what the investigation did and what the skill instructed. The skill's implementation-attribution workflow — git history first, then content grep, then convert, then query writes, then verify commits — held up exactly as written. The investigation followed it step for step, and it produced correct results. That workflow was not modified. Changing a method that works is unfounded drift, and the audit exists to distinguish a real gap from a preference.

The gaps were all downstream of a distinction the skill did not make: the difference between building a mechanism and adopting one.

### The missing concept: adoption as a distinct question

The skill had a reference document, `attribution.md`, with thirteen sections on implementation attribution. It answered the question "which session implemented this repository work?" It had no concept of the question "which session adopted this mechanism into a different codebase?" The two questions share symbols but not target files, and they require opposite search directions.

Implementation attribution starts from the mechanism's own repository and moves outward into transcripts. Adoption attribution cannot start there, because the mechanism's symbols appear in review, investigation, and report sessions — not only in adoption sessions. The investigation established this concretely: a raw grep for `profilebootstrap` returned 109 files, of which 6 were implementers. Symbol frequency could not separate an adopter from a reviewer who quoted the same symbols.

The technique that resolved this was the inverted search, described in Section 9. The investigation derived it from scratch. A future investigation that faces the same question should not have to derive it again. The skill update encodes the technique so the next agent starts from the solution, not from the problem.

### What was added

Three changes were made, each tied to a specific finding from the investigation.

A new reference document, `references/adoption-attribution.md`, records the inverted-search technique. It is structured to mirror `attribution.md` so the two read as a pair: a statement of why the implementation workflow fails for adoption, the four-step inverted search (filesystem grep, convert consumer-workspace sessions, query writes to known consumer files, verify adoption commits), the broad-versus-precise query pairing and why both are kept, the handling of unresolved adopters with the `--active-since` recovery, the two adoption shapes, and a decision table for when to use it against `attribution.md`. The unresolved-adopter handling is documented as a pattern, not as a failure, because the investigation produced two such cases and the correct response — document the limit, do not force a match — is itself a methodological rule worth stating.

Two query patterns were added to `references/queries.md`. The first is the symbol-relevance score, the ranking query from Section 6, with explicit framing that it is a narrowing device and not an attribution. The worked CTE counts tool calls whose command or file path touches a set of distinctive symbols, plus write and exec totals for context, and orders sessions by symbol-hit count. The framing states the limit directly: two sessions can have identical scores and opposite roles. The second is the distinct-files-written-per-session query, the decisive query from Section 7, with the two properties that made it decisive stated as design requirements — `operation_type IN ('NEW','MODIFY')` to exclude reads, and `DISTINCT` to collapse repeated edits to one row per session per file.

Two additions were made to `SKILL.md` itself. The "Load references selectively" section now points at `adoption-attribution.md` alongside the existing `attribution.md` pointer, so an agent that reads the entry point knows the adoption reference exists. The Discovery caveats section gained two bolded statements: that symbol frequency narrows but does not attribute, and that adoption is a different question from implementation. Each statement cross-references the document that develops the technique. These are short pointers, not rederivations, because the skill entry point should route to depth rather than contain it.

### What was left alone

The audit distinguished three categories: what worked, what was missing, and what was a matter of preference. Only the second category was changed.

The implementation-attribution workflow was left untouched. The evidence hierarchy (strong, supporting, weak) was left untouched. The four-count commit separation was left untouched. The role-classification query, the built-in query-commands section, the Codex parent/subagent collision guidance, and every existing flag and command example were left untouched. These held up under real use, and the investigation is the evidence that they held up.

No preference-driven edits were made. The skill's section ordering, its prose style, and its choice to keep query commands in the binary rather than in the skill are not things this investigation tested. Editing them would express a taste, not a finding.

### Why encode the method in the skill rather than only in the report

The report and the skill serve different readers. The report is a narrative record of one investigation; it is read to understand what happened. The skill is a reusable instruction set; it is read to perform the next investigation. A technique that lives only in a report must be rediscovered each time. A technique that lives in the skill is available to every future session that loads it, without any agent having to find the report first.

The inverted search is the technique most worth encoding, because it is non-obvious and generalizable. The report's Section 9 derives it. The skill's `adoption-attribution.md` states it as a method. The derivation stays in the report; the method lives in the skill. An agent that later faces an adoption question loads the skill, reads the reference, and starts from the solution. That is the reason for the update, and the measure of whether it succeeded is whether the next adoption investigation needs to re-derive the inversion.

## File reference

| Artifact | Path |
|---|---|
| Investigation root | `claw-stuff/scripts/2026/07/25/profile-loading-playbook/` |
| Source lists | `sources/{pi-focused,codex-focused,consumer-workspaces,consumer-new,sig-*}.txt` |
| Queries | `queries/01-profile-relevance.sql` … `queries/08-consumer-user-turns.sql` |
| Results | `results/q1-relevance.json` … `results/q8-consumer-user-turns.json` |
| Archives | `archives/{pi,codex}/active/YYYY-MM/*.minitrace.json` (119 total) |
| Attribution analysis | ticket `PROFILE-LOADING-PLAYBOOK-2026-07-25`, `analysis/01-session-attribution-analysis.md` |
| Diary | ticket `PROFILE-LOADING-PLAYBOOK-2026-07-25`, `reference/01-diary.md` |
| Companion playbook | [[loading-pinocchio-geppetto-profiles-for-llm-and-embeddings-inference]] |
| Skill: adoption reference | `~/.pi/agent/skills/go-minitrace-transcript-analysis/references/adoption-attribution.md` (new) |
| Skill: query patterns | `~/.pi/agent/skills/go-minitrace-transcript-analysis/references/queries.md` (symbol-relevance score + distinct-files-written added) |
| Skill: entry point | `~/.pi/agent/skills/go-minitrace-transcript-analysis/SKILL.md` (adoption reference + two caveats added) |
