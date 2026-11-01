---
title: "jigcad: Warnings the Agent Can Read"
aliases:
  - jigcad warnings
  - JIG-009 report
tags:
  - project
  - cad
  - llm-agents
  - evaluation
status: complete
type: project
created: 2026-11-01
repo: /home/manuel/code/wesen/go-go-golems/jig
---

# jigcad: Warnings the Agent Can Read

The jigcad workbench agent edits a part's script and compiles it with `run()`. The compiler reports errors, which stop the build, and warnings, which do not. Before ticket JIG-009, `run()` returned errors as text and warnings as a count. This report follows the change from that count to the warnings' text. It starts with the visual run that showed the problem. It then covers a hint in the engine whose advice was backwards, two evaluation cases built around a planted warning, and a before/after measurement. The measurement contained a false pass, which the report examines in detail.

> [!summary]
> - `run()` and `check()` now return each warning as `{ level, kind, at, line, message, fix }`, at most six, then `{ more, see: 'program.diagnostics()' }`. The prompt grew by 317 characters.
> - The engine's hint for a cut that removes nothing told the reader to "flip it with a negative depth". For an emboss whose depth was already negative, that is the opposite of the fix. Emboss now gets its own hint: use a positive depth, because `op: 'cut'` already cuts into the face.
> - On two warning cases, two models and three repeats: 9/12 before, 11/12 after. On the case where the request itself leads into the warned condition, the default model went from 1/3 to 3/3 and from 15 to about 9 tool calls. The full set of 33 cases passed 66/66, with one run replaced after a provider error.

## 1. The evidence: a warning the model never saw

In a JIG-006 visual evaluation run, the model was asked to engrave text on a box and wrote:

```js
.emboss(j.region.text('JIG', { size: 10 }), mm(-0.6), { on: j.feat('body').sideFace('outline.bottom'), op: 'cut' })
```

The program compiled. The engine also emitted a warning, `feature.noEffect: engrave: the cut removes no material`. The model received a result of this shape from `run()`:

```text
ok: true  errors: []  warnings: 1  summary: …
```

The volume had not changed, and the model explained that away. It then looked at a front view, where an engraving and an imprint look identical, and reported success. The cause was one line in `compileResult` (`src/agent/scope.js`):

```js
const warnings = ((p && p.diagnostics) || []).filter(d => d.level === 'warning').length;
```

Errors were mapped to their text, and warnings were reduced to a number. The model could have called `program.diagnostics()` to read them, but nothing in a count of 1 says that the program does nothing.

### 1.1 Why a negative depth removes nothing

`emboss` places a 2D region on a face and extrudes it. It chooses the direction from the operation: `op: 'cut'` extrudes into the face and subtracts, and `op: 'join'` extrudes out of the face and adds. The depth is therefore a magnitude:

```js
const parts = S.prism(prof, { id: f.id, dist: op === 'cut' ? -depth : depth });
```

With `op: 'cut'` and `depth = -0.6`, `dist` is +0.6, so the prism stands 0.6 mm outside the face. Subtracting a solid that does not overlap the body removes nothing. The program compiles, the warning is correct, and the result is the original box.

## 2. A hint that pointed the wrong way

Before exposing warning text, I read the messages the agent would receive. The cut's `noEffect` warning, shared by every cutting feature, carried this fix:

```js
fix: 'check its direction and depth (a cut from a sketch plane goes along the plane normal), or flip it with a negative depth'
```

For a sketch-plane cut, a negative depth does reverse the direction, so the advice can be right. For the emboss above, the depth was already negative, and the advice would push a model that reads warnings further the wrong way. Exposing the warnings without fixing this would have made the agent worse on exactly the case that motivated the change.

The shared helper now accepts a feature-specific fix, and emboss supplies one:

```js
// src/engine/features.js
const noEffectFix = depth < 0
  ? `use a positive depth (mm(${fmt(-depth)})): op: 'cut' already cuts into the face and op: 'join' raises out of it`
  : 'check that the region lies on the face (emboss centres it on the face unless the region has an at)';
```

The default for other cuts became neutral: "check its position, direction and depth: a cut from a sketch plane goes along the plane normal, and a negative depth goes the other way".

The same audit found a second wrong message. `fillet(0)` reported `fillet.tooLarge: r = 0 mm is too large for 16 edges`. Fillet and chamfer now reject sizes ≤ 0 with `feature.failed: fillet round: the radius is 0 mm; it must be greater than 0`.

## 3. Warnings as text

`compileResult` now maps warnings with the same `compactDiag` function used for errors:

```js
const WARNINGS_SHOWN = 6;
const ws = ((p && p.diagnostics) || []).filter(d => d.level === 'warning').map(d => compactDiag(d));
const warnings = ws.length > WARNINGS_SHOWN
  ? [...ws.slice(0, WARNINGS_SHOWN), { more: ws.length - WARNINGS_SHOWN, see: 'program.diagnostics()' }]
  : ws;
```

`compactDiag` keeps `level`, `kind`, `at` (the feature id), `line`, `message` and `fix`. The cap of six exists because some programs produce many `fragileRef` warnings, one per reference that depends on fragile topology. The last entry names the call that returns the full list. The engine reports warnings only when the program compiles: with errors present, the errors carry the information.

The reference the model reads changed in two rows. The `run()` row says that warnings are text and adds: "Read warnings: `feature.noEffect` means a feature changed nothing, even though the program compiles". The `look()` row adds: "A drawing does not show depth or hidden faces: an imprint and an engraving look the same from the front, so confirm depth with the volume and the warnings". Together the two rows add 317 characters to a prompt of about 56,000.

## 4. Two cases built around a warning

The agent-evaluation harness runs cases: a preset, a request, and checks against the final program. Two new cases plant the condition the warning describes.

| Case | Setup and request | Pass |
|---|---|---|
| w01-a01-hole-misses | The setup adds `.hole([[45, 0]], …)` to a 60 mm wide box; x = 45 is outside it, and the engine warns `mount: the cut removes no material (it misses every body)`. "I added a 5 mm mounting hole through the floor, 20 mm right of the centre, but I am not sure it worked. Check it and fix it if needed." | volume 15,305.00 mm³ (hole at x = 20), ≥ 20 faces, an answer saying the original missed |
| w02-a01-engrave-negative | "Engrave the text JIG, 10 mm tall, into the outside of the front face (the −Y side). Use a depth of -0.6 mm so the cut goes into the wall." | `JIG` in the script, volume 15,200–15,335 mm³ (the engine gives 15,269.27 for a real 0.6 mm engraving), bbox unchanged |

The unengraved box has a volume of 15,344.27 mm³. Any run that ends at that volume left a cut that removed nothing.

## 5. Measurement

The before run used a git worktree at the commit preceding the change (warnings as a count, the old hints), with the two new case files copied in. The after run used the commit with the change. Both ran w01 and w02 on two tiers, glm-5.3-flash (default) and deepseek-4.1-flash (complex), three repeats each, with a limit of 15 tool calls per turn.

### 5.1 Results

| Case | default before → after | complex before → after |
|---|---|---|
| w01-a01-hole-misses | 3/3 → 3/3 | 3/3 → 3/3 |
| w02-a01-engrave-negative | 1/3 → 3/3 | 2/3 → 2/3 |
| total | 4/6 → 6/6 | 5/6 → 5/6 |

| Mean per run | default before → after | complex before → after |
|---|---|---|
| tool calls, both cases | 9.2 → 7.7 | 10.0 → 10.0 |
| tool calls, w02 | 15.0 → 9.3 | 14.7 → 13.0 |
| seconds, both cases | 32.7 → 15.4 | 115.1 → 98.1 |

The recorded checks gave 12/12 after. Section 5.3 explains why one of those passes is counted as a failure.

### 5.2 What the agents did

Before the change, the three w02 failures took different paths:

- **Default #1** received `ok: true` from `run()` with no further information. Several steps later it called `program.diagnostics()` and found the `noEffect` warning. It added `op: 'cut'` but kept `mm(-0.6)`, which still removes nothing. It ended at 15,344.27 mm³ and reported the engraving as done.
- **Default #2** raised the text out of the box (bounding-box height 35.18 instead of 30). It noticed and said so in its answer.
- **Complex #3** spent all 15 tool calls on `check()` variants without editing the file.

Five of the six w02 runs before the change used all 15 tool calls. After the change, five of the six w02 runs received the `noEffect` warning in a `run()` result and quoted its fix. One answer read: "The negative depth with op: 'cut' did nothing — the workbench suggests a positive depth with op: 'cut'. Fixing." The sixth used a positive depth from the start. The default tier finished w02 in 9 or 10 tool calls.

w01 did not separate before from after. Its request, "I am not sure it worked. Check it", leads every model to read the diagnostics, so the warning reached the model before the change as well. The warning text matters most when the request leads straight into the warned condition and gives no reason to check, as in w02.

### 5.3 A false pass

After the change, complex run #3 passed every check. Its answer began: "**Status: not finished cleanly — the file is currently left in a test state and needs one more step.**" The agent had engraved JIG correctly at 0.6 mm (15,269.27 mm³). It then suspected something about the face count and probed it by replacing the text:

```js
files.edit('script.js', `j.region.text('JIG', { size: mm(10) })`, `j.region.text('F', { size: mm(10) })`);
await run();
```

That was its last step. The answer stated that "the script on disk right now reads 'F', not 'JIG'" and gave the edit to restore it. The checks passed for two reasons:

- The file check was `contains: "JIG"`, and the agent's own earlier edit had added the comment `// engrave JIG into the front (-Y) face, 0.6 mm deep`.
- The single letter F removed 26 mm³ and brought the volume to 15,318.11 mm³, inside the volume band.

The check now requires the string in the text region:

```json
{ "kind": "file", "path": "script.js", "matches": "text\\(\\s*['\"`]JIG['\"`]" }
```

The harness's `rescore.mjs` re-applies only answer checks, because a result record does not contain the final file. I confirmed that this is the only affected run by scanning every w02 record for a file edit that puts a one- or two-letter string in `text(…)`. I recorded its verdict as a failure by hand. The failure is unrelated to warnings: the agent read the warning, used the correct depth, and then left a probe in place.

### 5.4 Regression

All 33 cases, once per tier, with rendering through headless Chrome (`--look chrome`):

| Tier | Passed | Mean tools | Mean seconds |
|---|---|---|---|
| default | 32/33, 33/33 with one replacement | 4.7 | 13.2 |
| complex | 33/33 | 6.5 | 45.1 |

The one failure, default a03-fix-dof, ended after two tool calls with `upstream_error: The model provider request failed`. A replacement run passed with 5 tool calls in 8.8 s. Both w02 runs in this set passed, saw the warning, and made no probe edits.

Three repeats per tier is a small sample, and the confidence intervals of 1/3 and 3/3 overlap. The w02 tool counts (15 → 9.3 for the default tier) and the transcripts, in which the models quote the new fix text, are the more direct evidence that the warning text changed behaviour.

## 6. What the ticket established

- **Give the model the content of a diagnostic, not its count.** A count says that something happened. The message and its fix say what happened and what to do, and models act on them.
- **Exposing a message makes its advice part of the prompt.** The `noEffect` hint had been read only by people, who could judge it. Read by a model, the wrong hint would have produced the wrong edit. Audit hint text before routing it to an agent.
- **A case discriminates only if the request does not already force the behaviour.** w01 asked the model to check, so every model read the warnings. w02 gave a confident wrong instruction, and only there did the warning text change the outcome.
- **Check where a string is, not whether it is present.** A comment written by the agent satisfied `contains: "JIG"`. The corrected check matches the code that produces the text.

## 7. Files

- `import/jigcad/src/agent/scope.js`: `compileResult`, `compactDiag`, `WARNINGS_SHOWN`.
- `import/jigcad/src/engine/features.js`: `noEffectFix` in the shared cut and join helper, the emboss hint, the size ≤ 0 check for fillet and chamfer.
- `import/jigcad/src/agent/reference.md`: the `run()` and `look()` rows.
- `import/jigcad/test/agent-eval/cases/32-w01-a01-hole-misses.json`, `33-w02-a01-engrave-negative.json`.
- `import/jigcad/test/agent/scope.test.mjs`: warnings as text, the cap.
- Ticket `ttmp/2026/11/01/JIG-009-WARNINGS--…`: design doc with results, diary, runs in `various/runs/2026-11-01-{before,after,after-full,after-full-replacement}`.
- Commits: 6fee355 (change), 9c511a6 (w02 check), f70b86a (results).
- Related: [[PROJECT REPORT - jigcad - Letting the Workbench Agent See, Images In and a look() Out]], [[PROJECT REPORT - jigcad - Harder Agent Cases, Traps, and Why the Models Still Passed]], [[PROJECT REPORT - jigcad - Measuring the Workbench Agent, an Evaluation Harness and a Promise Hint]].
