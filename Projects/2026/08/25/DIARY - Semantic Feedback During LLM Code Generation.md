---
title: "Diary: Semantic Feedback During LLM Code Generation Report"
aliases:
  - Semantic Feedback Report Diary
tags:
  - diary
  - llm-inference
  - mlx
  - qwen
  - documentation
status: active
type: diary
created: 2026-08-25
repo: /Users/manuel/code/wesen/2026-08-25--mlx-inference
---

# Diary

## Goal

Create a detailed, evidence-backed deep-dive article for the `go-go-parc` Obsidian vault that explains the semantic-feedback generation project in a textbook writing style without analogies. Preserve a chronological record of source inspection, conclusions, validation, and vault delivery, then commit and push only the intended vault files.

## Step 1: Reconstruct the final project state

The existing ticket design and implementation diary documented the original mock, the first MLX adapter, and the first negative live runs. The source repository had continued to evolve after the last ticket-diary entry, so the report could not safely restate that document. I reconciled the design with the current implementation, recent commits, tests, and the successful live trace.

This reconstruction changed the central narrative. The earlier evidence showed that documentation injection alone did not repair the call. The final evidence showed that the harness had retained a sampled newline after deleting `)`. Once the edit removed both the delimiter and its following line terminator, the replay cursor ended exactly at `foobar(x`, tokenization checks passed, and Qwen generated the second argument.

### Prompt Context

**User prompt (verbatim):**

> Before we move forward:
>
>  write a detailed project report for the obsidian vault as a deep dive technical analysis blog post using a textbook writing style (no analogies, see skill).
>  Commit and push the bsidian vault when done (go-go-parc vault).
>
> ---
>
> commit at appropriate intervals and keep a detailed diary as you work (using the diary format from the skill)

**Assistant interpretation:** Write a new append-only technical article and companion diary in the dated `Projects` area of the `go-go-parc` vault. Base the article on final code and trace evidence, validate it, make focused vault commits, and push `main` without staging unrelated Obsidian state.

**Inferred user intent:** Preserve a durable explanation of what the prototype now proves, why earlier runs failed, and how the next engineer should extend and measure it.

### What I did

- Read the Obsidian vault-writing, textbook-authoring, diary, Obsidian Markdown, and Git commit instructions in full.
- Located the vault at `/Users/manuel/code/wesen/go-go-golems/go-go-parc`.
- Verified that the vault was clean on `main` and tracked `origin/main`.
- Inspected representative `ARTICLE` and `PROJ` notes to match frontmatter, naming, and prose conventions.
- Searched the vault for related MLX, Qwen, semantic-feedback, and code-generation notes.
- Inspected the source tree, ticket design, implementation diary, README, controller, trace, parser, validators, policy, MLX adapter, live fixture, tests, and recent Git history.
- Extracted the diagnostic, edit, and context-checkpoint records from `feedback-valid-rewind-snapshot-v2/qwen.json`.
- Ran `.venv-mlx/bin/python -m pytest -q -ra` in the prototype.

### Why

- The report needed to distinguish the current successful mechanism from earlier negative evidence.
- The user requested a deep technical analysis, so conclusions had to point to code, commits, test results, and live event records.
- Vault cleanliness had to be established before creating or committing notes.

### What worked

- The vault was clean and had no local `AGENTS.md` with additional rules.
- The source repository was clean on commit `3b7d41f`.
- The final live trace contained exact before/after text, patch spans, token IDs, round-trip equality, active-stream equality, and the repaired final output.
- The test suite completed with 19 passing tests and one intentional skip.

### What didn't work

- The first attempt to read the ticket design used the wrong filename: `01-qwen-semantic-feedback-harness-design-and-implementation-guide.md`. The actual file is `01-semantic-feedback-qwen-harness-design-and-implementation-guide.md`.
- Broad parallel inspection output was truncated. I replaced it with targeted reads and `rg`/`jq` queries for exact definitions and trace records.
- Shell startup repeatedly printed `pyenv: cannot rehash: /Users/manuel/.pyenv/shims isn't writable`. It did not affect read commands, Git inspection, or tests.

### What I learned

- The latest ticket diary ends before commits `1e01889`, `d93b8ae`, `6398cb1`, and `3b7d41f`; final source and artifacts are authoritative for the report.
- The successful intervention depends on deleting the newline that arrived with the closing delimiter.
- Text and token checkpoints are a more useful first validation interface than raw KV arrays.
- The hint must state the API contract directly and must not refer to an error branch removed from the active context.

### What was tricky to build

- The report needed to preserve negative experimental results while making clear that one key negative result was confounded by a harness defect.
- Exact distinctions among character spans, detokenized fragments, token IDs, and KV-derived state had to remain explicit throughout the explanation.

### What warrants a second pair of eyes

- Verify that the article does not overstate one successful live repair as a measured quality improvement.
- Check the experimental-design section before implementing the paired seed sweep.
- Review the security language around `--trusted-tests`; subprocess isolation remains insufficient for hostile code.

### What should be done in the future

- Run the paired baseline/feedback seed sweep.
- Add the Tree-sitter parser behind the current parser interface.
- Treat KV-prefix reuse as an optimization tested against full replay.

### Code review instructions

- Start with the article sections “The operational model,” “The live `foobar` investigation,” and “Experimental design for measuring improvement.”
- Cross-check the successful trace at `sources/semantic-feedback-prototype/artifacts/live-qwen/feedback-valid-rewind-snapshot-v2/qwen.json`.
- Cross-check edit behavior in `src/semantic_feedback/policy.py` and context checks in `src/semantic_feedback/mlx_lm_model.py`.

### Technical details

```text
source repo: /Users/manuel/code/wesen/2026-08-25--mlx-inference
vault:       /Users/manuel/code/wesen/go-go-golems/go-go-parc
source HEAD: 3b7d41f Validate edited MLX replay contexts
tests:       19 passed, 1 skipped
```

## Step 2: Draft the vault article and companion diary

I drafted a new article rather than modifying an existing note. The document is organized foundationally: research question, state model, architecture, region recognition, semantic events, validation/policy separation, self-contained hints, MLX replay, context checkpoints, the live failure investigation, testing, reproduction, experiment design, Tree-sitter, and KV-prefix reuse.

The prose avoids analogies and separates demonstrated behavior from proposed work. Diagrams describe component and event relationships; pseudocode specifies contracts; tables summarize ownership, failures, and experimental conditions. The report links the exact source paths and commits needed for review.

### What I did

- Created `ARTICLE - Semantic Feedback During LLM Code Generation - Editable Context Replay with MLX.md`.
- Created `DIARY - Semantic Feedback During LLM Code Generation.md`.
- Added Obsidian frontmatter, an internal wikilink between the article and diary, callouts, Mermaid diagrams, tables, equations, code examples, source references, and commit references.
- Made the article explicit about the single-case status of the successful Qwen run.

### Why

- An `ARTICLE` is the correct vault type because the document develops reusable technical knowledge beyond the lifecycle of the current ticket.
- A separate `DIARY` keeps implementation chronology and delivery evidence out of the conceptual article.

### What worked

- The final structure supports both a first-time reader and an engineer preparing the next experiment.
- The worked trace demonstrates exactly how sampled text becomes a diagnostic, patch, replay context, and repaired continuation.

### What didn't work

- N/A during drafting.

### What I learned

- The most durable result is the validation order: exact text, tokenizer round trip, queued token equality, replay generation, then prompt or sampling experiments.

### What was tricky to build

- The report needed sufficient implementation detail without copying the entire ticket design or source code.
- The Mermaid sequence had to distinguish the model's sampled fragment from the controller's text edit and subsequent replay.

### What warrants a second pair of eyes

- Confirm that Obsidian renders the display equations and both Mermaid diagrams in the target vault theme.
- Review the local absolute `repo` frontmatter path if this vault is consumed on a second machine.

### What should be done in the future

- Add a follow-up article after the paired seed sweep yields aggregate evidence.

### Code review instructions

- Review both new files only. Do not include `.obsidian/workspace.json` or unrelated vault changes in the commit.

### Technical details

```text
target folder: Projects/2026/08/25/
article type: article
diary type:   diary
```

## Step 3: Validate and commit the report milestone

The completed article and diary were copied into a new dated vault folder and validated in place. Only the two intended files appeared in `git status`; the vault did not acquire `.obsidian/workspace.json` changes or other generated state. YAML frontmatter parsed successfully, all fenced code blocks were balanced, and Git's whitespace check completed without findings.

The first focused vault commit records the complete technical article and the diary through drafting. A separate diary-only commit will record this commit hash before publication.

### What I did

- Copied the two drafts into `Projects/2026/08/25/`.
- Counted 4,749 words in the article and 1,331 words in the initial diary.
- Checked Markdown fences, trailing whitespace, placeholders, and YAML frontmatter.
- Staged the two exact paths and inspected `git diff --cached --name-status`, `git diff --cached --check`, and `git diff --cached --stat`.
- Committed the report milestone.

### Why

- Focused staging prevents Obsidian session state or unrelated notes from entering the project-report commit.
- Recording the report and its authorship diary together preserves the reasoning available at the time of publication.

### What worked

- The staged diff contained exactly 981 inserted lines across the article and diary.
- The commit completed successfully.

### What didn't work

- The first whitespace check found trailing spaces in two verbatim prompt lines and one extra blank line at the article's end. I corrected these formatting-only issues in the drafts, recopied them, and reran the checks successfully.

### What I learned

- The vault accepts the `article` and `diary` frontmatter types without requiring an update to an index note.

### What was tricky to build

- The user prompt contained visual trailing spaces. Removing those spaces preserved the prompt wording while satisfying repository whitespace checks.

### What warrants a second pair of eyes

- Inspect commit `b33954c` and confirm that both Mermaid diagrams render correctly in Obsidian.

### What should be done in the future

- Publish the two focused commits to `origin/main` and record the push result.

### Code review instructions

- Run `git show --stat b33954c`.
- Review only the two paths under `Projects/2026/08/25/`.

### Technical details

```text
Commit before rebase: 57a4ce9 — Document semantic feedback generation project
Commit after rebase:  b33954c — Document semantic feedback generation project
Files:                2
Inserted lines:       981
```

## Step 4: Integrate the updated remote branch without force

The first push attempt was rejected as a non-fast-forward update. Fetching `origin` showed that the local branch was two commits ahead and 550 commits behind `origin/main`. The local worktree had been clean before integration, so I rebased the two focused report commits onto the updated remote branch rather than forcing the push.

The rebase completed without conflicts and changed the report commit from `57a4ce9` to `b33954c` and the first diary commit from `686389f` to `5bb5af9`. After the rebase, three unrelated transcript paths appeared modified in the worktree. They were not part of either local commit, are excluded from staging, and must remain untouched by this report workflow.

### What I did

- Attempted `git push origin main`.
- Recorded the exact non-fast-forward rejection.
- Ran `git fetch origin` and inspected `main...origin/main` with left/right history.
- Ran `git rebase origin/main`; both commits replayed without conflicts.
- Inspected the rebased commit range with `git diff origin/main...HEAD --stat` and `--check`.
- Inspected the unexpected transcript modifications and kept them unstaged.

### Why

- A non-fast-forward push must integrate remote work; force-pushing a shared vault branch would risk discarding 550 remote commits.
- Exact-path staging allows the diary to be updated without absorbing unrelated worktree state.

### What worked

- Fetch advanced `origin/main` from `8c9acd4` to `55b30c4`.
- Rebase completed successfully with no merge conflicts.
- The committed range still contains only the article and diary.

### What didn't work

- The first push failed with:

```text
! [rejected] main -> main (fetch first)
error: failed to push some refs to 'github.com:go-go-golems/go-go-parc'
```

- The updated remote checkout exposed three unrelated transcript modifications in the case-sensitive Git index versus the macOS worktree. This report does not attempt to resolve or discard them.

### What I learned

- The vault receives frequent concurrent updates; publishing work should fetch immediately before the final push.
- A clean pre-rebase status does not guarantee a clean macOS worktree after checking out hundreds of new paths when the repository contains names that may interact on a case-insensitive filesystem.

### What was tricky to build

- The rebase changed commit hashes already cited by the diary, so the current hashes had to be recorded without erasing the chronological pre-rebase evidence.
- The unrelated transcript differences are large content substitutions, not whitespace noise, and must not be normalized or committed incidentally.

### What warrants a second pair of eyes

- Independently inspect the vault's transcript filename collisions on macOS. They are outside the semantic-feedback report scope.

### What should be done in the future

- Commit this diary update by exact path, push without force, then record the final remote state.

### Code review instructions

- Review `git diff origin/main...HEAD`; it should contain only the two semantic-feedback note paths.
- Do not stage the three modified `Transcripts/...` paths.

### Technical details

```text
remote before fetch: 8c9acd4
remote after fetch:  55b30c4
local divergence:    ahead 2, behind 550
rebased report:      b33954c
rebased diary:       5bb5af9
```
