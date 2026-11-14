---
title: Playbook - Extracting a pattern language from codebases, and validating it with agents
aliases:
  - pattern extraction playbook
  - pattern language from code
  - validating patterns with subagents
tags:
  - playbook
  - patterns
  - architecture
  - agents
  - evaluation
status: active
type: article
created: 2026-11-14
repo: /Users/manuel/code/wesen/chromobench
---

# Playbook: extracting a pattern language from codebases, and validating it with agents

This playbook describes how to turn one or more built systems into a pattern language (chapters in the style of
*Design Patterns* and *A Pattern Language*), and then how to find out whether the patterns are true and useful: first
by checking that agents understand them, then by having agents build software with them and judging the results.
It was worked out on 14 November 2026 on chromobench (a WebGPU darkroom), with Editor lab (a browser photo editor
with a tiled engine) and goja-cv (a lazy image-analysis engine) as second and third implementations. The result is in
`chromobench/docs/patterns/` (overview + 12 chapters) and on the reMarkable under `/ai/2026/11/14/patterns/`.

> [!summary]
> - **Extract from repetition.** The strongest evidence for a pattern is the same idea built twice, independently.
>   Look across several codebases; consolidate what they share; keep each one's mistakes as lessons.
> - **Map first, write second.** The extraction map (seam, generic share, blockers, three other domains) is the cheap
>   checkpoint where the person redirects; writing chapters is the expensive part.
> - **Lessons are the gold.** Bugs, debts and corrections from the projects become implementation notes, named
>   plainly ("this is the bug the originating project shipped").
> - **Validate in two stages.** Comprehension (isolated agents answer control questions, including ones whose answer
>   is not in the chapter, and apply the pattern to two unfamiliar domains), then construction (agents implement
>   tasks with and without the chapter; hidden tests, transcripts, diaries and a blind design review judge them).
> - **Judge like Alexander, Gabriel and Fowler**, not only by pass rates: were the forces resolved, is the structure
>   adapted to its context, is the code habitable and does it grow piecemeal, where does it smell.

## 1. Survey (mechanical, cheap)

Map the code before reading it deeply. For each codebase:

- line counts per package and largest files (where the weight is);
- the import graph (cycles block extraction; leaf packages are free already);
- module-level mutable state (caches, registries, "active" anything: blockers for two instances in one process);
- the authors' own view: READMEs, architecture notes, handoff guides, ticket diaries, tests.

```bash
find packages/*/src -name '*.ts' | grep -v test | xargs wc -l | sort -n | tail -15
for p in packages/*; do echo "$p -> $(grep -rhoE "from '@scope/[a-z-]+" $p/src | sort -u | tr '\n' ' ')"; done
grep -rnE "^(let|var) |^export let " packages/*/src --include='*.ts' | grep -v test
```

Do the same for the other implementations. A second codebase that solved the same problem is worth more than a
deeper read of the first: it turns a project idiom into a candidate pattern.

## 2. Recognise candidates

Signals, strongest first: the same idea written twice (in one codebase or across several); a domain-free core with a
domain-specific edge whose seam fits in about five functions; several callers of one thing (UI, agent, tests); a
small interface over a large implementation; a surface people or agents touch (errors, controls, undo); a trade-off
resolved on purpose. Anti-signals: the domain vocabulary itself, glue, anything an established library does better.

For each candidate write one row: **seam** (the interface in a line), **generic share** (rough %), **blockers**,
**three other domains** (fewer than three: an idiom, not a pattern), **cost**. Group as "cleanest", "with surgery",
"ambitious". Give the composition (which completes which), prerequisites, what stays in place, and a writing order.

**Stop and show the map.** The person trims, reorders or redirects here. In our run the person first approved the
list as given ("your first list was great"); a proposal to consolidate further was rejected in favour of the original
twelve, with cross-project evidence added inside them.

## 3. Write the language

Overview first: kit and quality, running example, how each pattern is written (★★ near-invariant, ★ one good form
among several), pseudocode conventions, pattern map, chapter list, order of introduction, one sketch using every
pattern, a table of the same language in four other kinds of system, what to leave out, further reading.

Then one chapter per pattern, 1,500–2,500 words, with the same sections: Intent; Also known as; Motivation (two to
four concrete failures from the running example, then other domains); Problem (one bold sentence); Forces (tensions
between two goods); Solution (one bold "Therefore:" paragraph that stands alone); Applicability (including "do not
use it when"); Structure (participants); Collaborations (numbered, a small diagram only when the shape is the point);
Sketch (language-neutral pseudocode ending with the pattern in use); Implementation notes (8–11, each a decision or a
trap with a bold lead); Variations (3–4 with trade-offs); Consequences (+ and −); Known uses (real only); Related.

Rules that mattered in practice:

- **Verify every claim about the project against the code before writing it.** We caught ourselves several times: a
  claim about a machine's architecture that was not measured; a "history" of failures that had not happened (rewritten
  as failure modes); API names in sketches that did not exist (marked "proposed").
- **Gloss each project at first mention** in every chapter; chapters are read alone.
- **Use real numbers** from the projects (measurements, line references, error codes), and the projects' real codes
  and names in examples.
- **Hedge or qualify known uses** you cannot fully stand behind; reviewers will flag the loose ones.
- **Keep code lines under ~98 characters** if the document goes to PDF (pandoc does not wrap code blocks).

## 4. Validate comprehension (cheap, before construction)

Run isolated `pi` agents (see [[pi-coding-subagents-handbook]]) on a few chapters, no tools, everything in one saved
prompt (`docs/patterns/review/run-review.py`):

- **Controls:** five questions per chapter, four answerable from the text and one that is *not* (correct answer:
  "not stated in the chapter"). The unanswerable one catches invention.
- **Transfer:** two contexts the chapter never mentions (we used grading scopes, streaming diffusion previews, a VFX
  compositor on a farm, WebGPU shader variants, a generative inpainting editor, AI tool packs with a forensic
  workspace rule); the agent maps participants, sketches, names the most important note, says where it would fail.
- **Review notes:** does the Solution stand alone; what is unclear, wrong, missing, too long; suggested edits.
- **Output:** one fenced JSON block, extracted defensively (repairs needed in practice: raw newlines in strings,
  unescaped quotes inside prose).

DeepSeek 4.1 flash answered 20/20 controls (all four traps refused) and produced 20–34 substantive review items per
chapter. **Check every finding against the code before applying it**: one reviewer found a real behaviour (a
same-key request rendering twice) that the code confirmed; another called a true claim "doubtful", which we kept and
cited instead. The transfer exercises produced new Variations (a shared generation for dependent views; step-ordered
streams; content-addressed assets for generated pixels). Lessons from early reviews were applied to chapters written
later (define every term the Solution uses; state lifecycles and error paths).

## 5. Validate construction (the real test)

Comprehension does not show that a pattern helps build good software. For that, agents build things.

**Design.**

- One small, dependency-free task per pattern (we used TypeScript on Node 24 with `node --test`), stated as
  *requirements and an API*, never as the solution. The requirements come from the chapter's Problem and Motivation in
  domain terms; the pattern's mechanism must not leak into the task text.
- **Variants:** four runs with the chapter in the prompt, two without (controls), per pattern. Four with the chapter
  show how robustly the pattern is applied; the controls show what the chapter adds over the model's own design sense.
- **Working rules in the prompt:** work only in the run directory; the project in `project/`; own tests for every
  requirement; a diary in `project/DIARY.md` following the diary skill (copied into the run directory, since runs
  load no skills); `NOTES.md`; a final JSON self-report (requirements met, own test counts, and for chapter runs:
  which parts were used, what was unclear, where and why they deviated).
- **Tools:** `pi --tools read,write,edit,bash,ls,find,grep --no-context-files --no-skills --no-prompt-templates`,
  per-run `--session-dir` so the native transcript stays with the run. `bash` is not sandboxed: say so to the person,
  keep everything in scratch directories, and measure boundary crossings in the transcripts.
- **Hidden acceptance tests**, written by you, kept outside every run directory until scoring. Write them against the
  requirements, and add a separate "robustness" group for properties the pattern implies but the task does not spell
  out (the difference between the groups is part of the signal).
- **Check every test is satisfiable before launching.** We wrote a quick implementation of the hardest case (a wide
  blur approximated within a memory budget) and found the first tolerance unreachable by any reasonable approach;
  the requirement was rewritten to what a sound approach achieves. An unfair test penalises every run alike and
  teaches nothing.
- **Smoke-test one run** for two minutes (files appear, tools work, tests run) before launching the batch.

**Scoring** (`docs/patterns/experiments/score.py`): per run, hidden tests pass/fail per test, the agent's own tests
re-run (to check its self-report), diary steps, source size. Compare chapter and control runs per test, not only in
total: the interesting results are the tests where the chapter changes the outcome.

**Transcripts** with go-minitrace (`convert pi --source-dir <run>/session`, then `query run --sql-file`): did the
agent read the chapter, and when relative to its first source write; how many test runs, how many failed; diary
writes; tool mix; use of `/tmp` and attempts to reach outside its directory. Behaviour explains outcomes (the handbook
found the prompt *is* the behaviour; a chapter read after the first design is written cannot have shaped it).

**Diaries:** read for whether the agent *thinks in the pattern's forces* (names the tension, chooses deliberately) or
only mentions the pattern; collect every "unclear" and "deviated because" into a list per chapter.

## 6. Judge the code like Alexander, Gabriel and Fowler

Pass rates say whether it works. The design review asks whether the pattern generated living structure. Use a blind
reviewer (an agent that sees the chapter as the yardstick and the anonymised implementations of one task side by
side, but not which had the chapter), with this rubric:

| Lens | Question | Evidence to look for |
|---|---|---|
| **Forces resolved** (Alexander) | Which of the chapter's forces did the code resolve, which left in tension, which never noticed? | the trade-off visible in code, not just in comments |
| **Adapted, not copied** (Alexander) | Is the instance shaped by this task's context, or a transcription of the sketch (including parts this task does not need)? | names and structure from the task's domain; absence of irrelevant participants |
| **Generativity** (Alexander) | Across the four chapter runs, did similar structure emerge (same seams, same participants), each different in detail? Compared with the controls' spread? | convergence of seams; diversity of surface |
| **Wholeness** (Alexander) | Does every part serve the whole; is there dead or ornamental structure? | unused abstractions, pattern parts with no caller |
| **Habitability** (Gabriel) | Could a newcomer live in this code and change it comfortably? Is it over-compressed or over-abstracted? | locality of change, names, size of units, density |
| **Piecemeal growth** (Gabriel) | Is adding the next operation, slot or field a local change? | where a new requirement would touch |
| **Smells** (Fowler) | Duplicated knowledge, long functions, primitive obsession (ids as concatenated strings), shotgun surgery, speculative generality | concrete file:line findings |
| **Tests as laws** | Do the agent's tests state the forces (properties, laws) or only examples? | property tests, negative controls |
| **Worse is better?** (Gabriel) | Did a simpler control implementation reach the same quality with less? Then the chapter may be teaching too much. | lines, concepts, pass rate per line |

## 7. Close the loop

For each chapter, combine: tests that chapter runs pass and controls fail (the pattern's value), tests both fail (a
gap in the chapter or the task), tests chapter runs fail and controls pass (the chapter misleads), diary "unclear"
items, deviations, transcript behaviour, and the design review. Revise the chapter (Solution, notes, variations,
"do not use it when"), keep the old version, and rerun the same tasks on the new version: the variant is the document,
the items stay fixed (handbook §"Applying this to documentation").

## 8. Publish

Commit the language, the review method and the experiment (tasks, runner, scoring, analysis SQL; hidden tests after
the runs). Upload the bundle without ceremony (`PATH=/Library/TeX/texbin:$PATH remarquee upload bundle …`; reflow long
code lines first). Write a short report of what the experiments changed.

## Pitfalls we hit

- A reviewer's confident "error" can be wrong; verify against the source before editing.
- An agent's self-report can be optimistic; always re-run its tests and the hidden ones.
- Agents leave their directory (one wrote scratch files to `/tmp` within two minutes); state the rule and measure it.
- Context runs out on long sessions: write the plan, the run layout and the scoring commands into files early, so the
  work survives a summary.

## Files (chromobench)

- `docs/patterns/00-overview.md` … `12-shared-handle-vocabulary.md` — the language.
- `docs/patterns/review/` — comprehension runs: `run-review.py`, specs, answers, README with results.
- `docs/patterns/experiments/` — construction runs: `tasks/<task>/TASK.md`, `run-impl.py`, `batch.py`, `score.py`,
  `analysis/*.sql`.

## Related notes

- [[pi-coding-subagents-handbook]]
- [[extracting-tribal-knowledge-into-kb-entries]]
