---
title: "jigcad: Harder Agent Cases, Traps, and Why the Models Still Passed"
aliases:
  - jigcad harder cases
  - JIG-005 report
tags:
  - project
  - llm
  - agents
  - evaluation
status: complete
type: project
created: 2026-11-01
repo: /home/manuel/code/wesen/go-go-golems/jig
---

# jigcad: Harder Agent Cases, Traps, and Why the Models Still Passed

The first evaluation of jigcad's workbench agent passed 84 of 84 turns on both models. That result, described in [[PROJECT REPORT - jigcad - Measuring the Workbench Agent, an Evaluation Harness and a Promise Hint]], said more about the case set than about the models. Ticket JIG-005 set out to write cases that the models would fail. It added assemblies, configurations, print jobs, multi-feature edits, a planted sketch conflict, a refusal and two conversations, and gave most cases a *trap*: an edit that looks complete and is wrong. This report explains how those cases were built and how their expected values were computed. It then covers what 178 model turns showed. The headline is not the one the ticket aimed for. After the harness's own errors were removed, glm-5.3-flash passed 40 of 42 harder runs and deepseek-4.1-flash passed 42 of 42. The traps failed because the preset scripts explain them in their comments, and both models read the scripts. The runs still exposed two genuine failure modes, one of them dangerous, and they showed that neither model ever asks a clarifying question.

> [!summary]
> - Every expected number came from compiling the edited files on the engine. Every trap was checked the same way: the naive edit either fails to compile (gear teeth collide) or compiles to a measurably wrong part (a large pot on a medium saucer).
> - The uncorrected baseline was 77/84 on both tiers. Of its failures, six of eight classes were the harness's or the infrastructure's: answer regexes that did not allow LaTeX, a follow-up whose meaning depended on what the agent had guessed, and lunaroute rate limits. Answer checks now match a normalised plain-text form of the answer, and a rescore tool re-applies corrected checks to recorded runs.
> - The traps did not trap. M-07's script says above the joint that the wheel "starts at 5°, half a tooth"; every run that finished changed the phase too. A trap explained in a comment tests reading, and both models read before they edit.
> - Two genuine glm failures: it treated a brief's instruction to *report* the plate count as a reason not to apply the edit; and it wrote a tool call into its answer as text, followed by an invented result, reporting an edit that never happened. Given "Make the box bigger", 12 of 12 runs guessed a size; none asked.

## 1. What makes a case hard

The first 14 cases were all on two simple presets: A-01, a 60 × 40 × 30 mm box with 2 mm walls, and A-03, a plate with a constrained sketch. Every edit was one parameter or one line. Finding the line and changing a number is something both models do reliably, so the set could not tell them apart.

A case is harder when the right answer needs something beyond finding the line. JIG-005 used six kinds of difficulty:

| Difficulty | What the agent must do | Cases |
|---|---|---|
| Reading an assembly | find joints, ports and gear parameters across parts | m07-ratio-centre, m07-tooth-gap, m09-travel-per-turn, m08-hinge-clearance |
| A coupled change | change two places that must agree | m07-wheel-30, h01-large |
| Configurations | know `.config(name)`, choose the right row, read its units | h04-decora-size, h04-switch-toggle, h01-large |
| New features | write an operation the script does not have | a01-mount-holes, a01-engrave |
| Diagnosis | read a solver diagnostic and remove the right constraint | a03-conflict |
| Refusal | notice that the request names something that does not exist | a01-no-holes |
| Conversation | keep state across turns, undo, act on a clarification | a01-undo-change, a01-bigger-clarify |

### 1.1 Traps

A trap makes a case discriminate. It is an edit that a hurried agent would make, that looks complete, and that the checks reject. Five cases have one:

- **m07-wheel-30.** The M-07 preset meshes an 18-tooth pinion with a 36-tooth wheel. The request: "Change the wheel to 30 teeth. The pair must still mesh without the gears touching. Tell me the new centre distance." Changing `teeth: 36` to `teeth: 30` leaves the wheel's joint angle at `deg(180 / 36)`, the half-tooth offset for 36 teeth, and the teeth collide: the engine reports `asm.interference: pinion and wheel touch or overlap` with a gap of 0.000 mm. The correct edit also changes the angle to `deg(180 / 30)`, which restores a 0.203 mm gap. The centre distance becomes m(z₁ + z₂)/2 = 2 · 48 / 2 = 48 mm.
- **h01-large.** H-01 is a print job with two parts, a pot and a saucer, and each part has its own `.configs(sizes).config('M')`. "Make the large size of the plant pot, with a saucer that fits it." Changing the first `.config('M')` compiles and makes a large pot on a medium saucer, with a volume of 166,268 mm³ instead of 189,986 mm³.
- **a03-conflict.** The setup adds `.dim('l1', 90)` next to the existing `.dim('l1', 'w')`. The solver reports the minimal conflicting set: `length(l1) = 80 mm · length(l1) = 90 mm`. Removing the wrong one compiles and makes a 90 mm plate, but the request says it "should stay 80 mm long".
- **h04-switch-toggle.** "I have a US toggle switch, not a Euro module." The configurations are `eu86`, `us_decora` and `us_toggle`. The decoy, `us_decora`, has the same outer size (69.85 × 114.3 mm); only the volume, 13,505 against 17,062 mm³, tells them apart.
- **a01-no-holes.** "Make the mounting holes 1 mm bigger" on a box without holes. Inventing holes changes the file and fails the `unchanged` check.

A test in the harness (`the harder cases reject the naive edit`) runs the naive edit of three traps through the real engine and requires each to fail. That test keeps the traps honest as the presets change.

### 1.2 Ground truth from the engine

No expected value came from a preset's comments or from arithmetic alone. Each was obtained by compiling the edited files with `worker.handle` in Node, the same engine the harness uses:

| Case | Variant | Engine result |
|---|---|---|
| m07-wheel-30 | teeth 30 only | `asm.interference`, pinion–wheel gap ≈ 0.000 mm |
| | teeth 30, angle `deg(180 / 30)` | ok, volume 34,129.47 mm³, gap ≈ 0.203 mm |
| m07-tooth-gap | as published | gaps base–pinion ≈ 0.200, base–wheel ≈ 0.200, pinion–wheel ≈ 0.203 mm |
| m09-travel-per-turn | pinion 18 teeth, module 2 | π · m · z = 113.10 mm per turn |
| h04 configs | `us_decora`, `us_toggle` | 69.85 × 114.3 × 7 mm; 13,504.54 and 17,062.33 mm³ |
| h01-large | both parts L / pot only | 189,985.93 / 166,268.44 mm³ |
| a01-mount-holes | four Ø3.4 mm through holes at (±22, ±12) | 15,271.63 mm³ (−72.63), 23 faces |
| a01-engrave | `BOX`, 8 mm, 0.6 mm deep, bottom face | 15,277.39 mm³; the check accepts 15,200–15,340 |
| a03-conflict | repaired | 12,672.77 mm³, 80 × 40 × 4 mm |

The process caught one of my own errors before any case existed. I had guessed the H-04 configuration names as `euro`, `decora` and `toggle`; all six guesses failed with `compile.failed`, and the script's actual rows are `eu86`, `us_decora` and `us_toggle`.

### 1.3 Conversations

A case may carry `followUps`, further requests in the same thread. The runner sends them one after another through the same `runTurn` and `thread`, so the model sees its earlier turns. The checks judge the state after the last turn:

```js
const requests = [c.request, ...(c.followUps || [])];
for (const text of requests) {
  if (ctl.signal.aborted) break;                        // one deadline for the conversation
  await runTurn({ host, sample, thread, text, images: text === c.request ? images : [], settings, reference, signal });
}
const agentTurns = thread.turns.filter(t => t.role !== 'user');
const turn  = agentTurns.at(-1);                        // answer checks read the last answer
const steps = agentTurns.flatMap(t => t.steps);         // step checks see every step
```

Usage is summed over the turns, and the record keeps every answer. An oracle for a conversation is a list of scripted turns, one per request.

`a01-undo-change` asks for a 2.4 mm wall and then says "put the wall back to what it was and make the box 35 mm tall instead"; "what it was" refers to the first turn. `a01-bigger-clarify` starts with "Make the box bigger", which is ambiguous on purpose, and follows with exact dimensions.

## 2. The run

The baseline ran 28 cases (the 14 old and the 14 new) on both tiers with three repeats: 168 turns in about 75 minutes. It ran from a git worktree at the commit before the image work, because that work had added a row to the reference the model reads, and the measurement should not mix the two changes. As recorded, both tiers passed 77 of 84.

### 2.1 Reading every failure

Each failing record's answers and last steps were read before it was counted. The failures fell into four classes:

| Records | Class | Evidence | Action |
|---|---|---|---|
| m09-travel-per-turn (glm, 2 runs) | check bug | the answer was `… = 113.097\ \text{mm}` | normalise LaTeX before answer checks |
| a03-dof-question (glm, 1 run) | check bug | `$$\text{DOF} = 22 - 21 = 1$$ … only center.x is free` | pattern for "DOF … = 1" added |
| a01-bigger-clarify (all 6) | case bug | the model guessed 80 × 60 × 40; "same height and walls" then kept 40 | follow-up reworded |
| 4 deepseek runs | infrastructure | lunaroute `rate_limited` mid-turn, answer `Thinking…` | one replacement run each |
| h01-large (glm, 1 run) | model | see §3.2 | none |

The two answer-check bugs had the same cause as two bugs found in the previous ticket: models write numbers in LaTeX, so a regex such as `113([.,][01]\d*)?\s*mm` does not see the `\ \text{` between the number and the unit. Loosening each regex fixes one case at a time. The `answer` check now matches a plain form of the text instead:

```js
export function plainAnswer(t) {
  return String(t)
    .replace(/\\(?:text|mathrm|mathit|mathbf|operatorname)\{([^{}]*)\}/g, '$1')
    .replace(/\\(?:times|cdot)/g, m => (m === '\\times' ? '×' : '·'))
    .replace(/\{:\}/g, ':').replace(/\\approx/g, '≈').replace(/\\pi/g, 'π')
    .replace(/\\(?:,|;|:|!| |quad|qquad)/g, ' ').replace(/~/g, ' ')
    .replace(/\\[()[\]]/g, '').replace(/\$+/g, '').replace(/\*\*|__/g, '')
    .replace(/[ \t]+/g, ' ');
}
// '$$\pi \cdot 2\ \text{mm} \cdot 18 = 113.097\ \text{mm}$$'  →  'π · 2 mm · 18 = 113.097 mm'
```

A new tool, `tools/agent-eval/rescore.mjs`, re-evaluates the answer checks of a recorded `results.jsonl` with the current case files and check code. It keeps the recorded verdicts of the other checks, which need the final program that the record does not hold. Correcting a check no longer requires paying for new model turns.

The `a01-bigger-clarify` bug was in my wording. After a model has guessed a height in the first turn, "same height" can mean the guessed height or the original one. A follow-up must fix the final state whatever the agent did earlier; it now says "Keep the original 30 mm height and the 2 mm walls".

### 2.2 Corrected numbers

The rescored baseline was merged with six reruns of the corrected case and four replacements for the rate-limited runs. Replacing those runs, rather than dropping them, keeps long turns in the sample; rate limits hit long turns more often.

| Tier | Set | Passed | 95 % CI | Tool calls mean (max) | Seconds median |
|---|---|---|---|---|---|
| default (glm-5.3-flash) | first 14 | 42/42 | 92–100 % | 3.2 (7) | 6.4 |
| default | harder 14 | 40/42 | 84–99 % | 5.6 (18) | 10.7 |
| complex (deepseek-4.1-flash) | first 14 | 42/42 | 92–100 % | 4.5 (12) | 27.1 |
| complex | harder 14 | 42/42 | 92–100 % | 7.7 (16) | 68.4 |

The harder cases cost about 1.7 times as many tool calls on both models. They do not separate the models by pass rate. deepseek's seconds include rate-limit waits and a slow backend hour, so its tool calls are the more stable measure of its cost.

## 3. What the runs show

### 3.1 The traps were explained in the scripts

The presets are teaching material, and their comments say what the traps exploit. Above the gear pair's joints, M-07 says:

```js
// The pair, assembled: each gear on a revolute joint. The wheel's joint
// starts at 5°, half a tooth, so a pinion tooth sits in a wheel gap.
const pair = j.assembly('gear-pair')
  .params({ wheel: deg(180 / 36) })
```

H-01's header says "a config changes all of them". A scan of the recorded steps shows the effect. Every run of m07-wheel-30 that finished (all but the rate-limited one) changed the phase as well as the tooth count, most within the first three steps. Two glm runs edited the teeth first, saw `asm.interference` and recovered. All passing h01-large runs changed both configurations. Every a03-conflict run removed the planted dimension that the solver's diagnostic named. Both models begin an edit by reading the script, so a trap documented in a comment is a reading test, and they read well.

That is a property of the presets more than a limit of evaluation. A user's own script may not be commented. A case set that wants to measure engineering judgement must strip the comments in its setup, or use parts written without them.

### 3.2 Two genuine failure modes

**A brief read as a refusal.** H-01's agent brief has a fragment that is on by default: "After a size change, report the plate count and suggest a smaller saucer flare if the pair no longer fits one plate." In one glm run, the model compiled the L configuration with `check()`, found that it needs two plates, and swept the saucer's flare to find one that fits. It then answered "Per the plate rule I should report that and suggest a smaller saucer flare", and never applied the size change. The brief asks for a report after the change; the model turned it into a reason not to make the change.

**A tool call written as text.** In one glm run of the corrected `a01-bigger-clarify`, the second answer contains this:

```text
[eval] files.edit('script.js', "w: mm(90), d: mm(60),\n h: mm(45)", "w: mm(80), d: mm(50),\n h: mm(30)"); …
→ ok: true ms: 52 errors: [] warnings: 0 summary: … volume: 23216.565 mass: 28.786 bbox: [80, 50, 30] …
Done — edited `script.js` …
```

No tool call was made. The text imitates the panel's rendering of a step, and the "result" is invented: the volume 23,216.565 mm³ is not the volume of any state the box was in, and the files stayed at 90 × 60 × 45 mm. This is the more dangerous of the two failures. The person reads a confident report of success, with numbers, for an edit that did not happen. The checks caught it only because they judge the final files, not the answer. A dedicated check could catch it directly: an answer that claims an edit while the turn has no step that changed the files.

### 3.3 Nobody asked

Given "Make the box bigger", 12 of 12 runs across both tiers and both runs guessed a size: 90 × 60 × 50, 80 × 60 × 40, 80 × 55 × 40, or "1.5× in every direction". None asked how much bigger. The checks cannot see this, because the follow-up fixes the final state either way. Measuring it needs a check that the first answer contains a question when the request is ambiguous.

## 4. Lessons

- **A trap must not be explained next to itself.** Commented presets defuse their own traps. Harder cases need uncommented scripts, or requirements that the comments do not address.
- **Normalise answers once.** Models format numbers in LaTeX and markdown. A normalisation step in the check fixes the class; per-regex fixes keep failing on the next model's style.
- **A follow-up must not depend on the agent's earlier choices.** Otherwise the case tests the case author's wording.
- **Replace infrastructure failures; do not drop them.** Dropping rate-limited runs would bias the sample toward short turns.
- **Judge final state, and add checks for what the answer claims.** The text-as-tool-call failure passed every answer check and failed only the file and metric checks.

## 5. Next steps

- Cases with comments stripped in `setup`, five-turn conversations with corrections, and requests that need a documented feature no preset uses.
- A check that the answer's claims match the steps: "edited" requires a step with `changed: true`.
- A check that an ambiguous request gets a question.
- The reference change deferred from JIG-004: mark async functions with `await` in the API table, measured on this set.

## 6. Files

- `import/jigcad/test/agent-eval/cases/15-…json` to `28-…json`: the harder cases.
- `import/jigcad/tools/agent-eval/runner.mjs`: `followUps`, `sumUsage`, `oracleSample`, `caseImages`.
- `import/jigcad/tools/agent-eval/checks.mjs`: `plainAnswer`; `tools/agent-eval/rescore.mjs`.
- `import/jigcad/test/agent-eval/harness.test.mjs`: the trap test and the multi-turn test.
- Ticket `ttmp/2026/10/31/JIG-005-HARD-CASES--…`: design doc with ground truth and results (§7), diary, `scripts/01-analyze.py`, runs under `various/runs/`.
- Commits: fb629fc (cases and runner), c4d8a5d and 3e326ad (check fixes, rescore), c23e38c (baseline and results).
