---
title: "Playbook: Comparing Coding-Agent Configurations on the Same Design-and-Implement Tasks"
aliases:
  - "agent matrix experiments"
  - "harness x model x effort comparison"
  - "comparing codex and pi on the same tasks"
tags:
  - playbook
  - agents
  - codex
  - pi
  - evaluation
status: draft
type: article
created: 2026-11-26
repo: /home/manuel/code/wesen/2026-11-24--compiler-workbench
---

# Playbook: comparing coding-agent configurations on the same design-and-implement tasks

This playbook describes how to give one engineering task to several agent configurations at once and compare what they produce. A configuration is a harness, a model and a reasoning effort, such as Codex CLI with gpt-6.2-sol at high effort, or Pi with gpt-6.2-astra at medium. The output to compare is the design, the implementation and the agent's behaviour along the way, so that the differences can be attributed to the configuration.

It extends [[PLAYBOOK - Measuring and Reducing Over-Engineering in Agent-Written Designs]], which compares prompts on one configuration and judges designs only. This playbook adds four things: several configurations, an implementation phase scored by hidden tests, a review loop between design and implementation, and two harnesses.

> [!summary]
> - **Fix what you compare on, free what you study.** Fix the language core and a small API in the brief, so that one hidden test suite can score every implementation. Leave the IR, the contract and the internals to the agents.
> - **Blind by construction.** Assign ticket letters to configurations at random. Branch from a revision that predates the experiment's own ticket. Keep the key and the hidden suite outside the repository. Give the judge and the reviewer documents without frontmatter.
> - **One session per agent, in turns:** design, then a blind score and a blind review, then revision and implementation, then hidden acceptance, then the agent's own report.
> - **Shared infrastructure the agents should not each build:** a remote runner with a lock for timed runs, and the network setting a sandbox needs.

Status: draft, written during the first application (IRWB-019, tensor programs in Tix, eight configurations), and updated as that experiment proceeds. Sections marked *(to be filled)* are not yet tested.

## 1. When to use this

Use it when the question is "which configuration should do this kind of work", or "what does the harness contribute", and the task is substantial enough to have a design and an implementation. The task must also be specifiable precisely enough for a hidden suite. For prompt-wording questions on a single configuration, the earlier playbook is cheaper.

## 2. The matrix

The first application crossed three factors at two levels each:

| Factor | Levels | How it is set |
|---|---|---|
| Harness | Codex CLI 0.172, Pi 1.5.1 | the launcher (`01-` or `12-`) |
| Model | gpt-6.2-sol, gpt-6.2-astra | `MODEL` (Codex: `gpt-6.2-sol`; Pi: `openai-codex/gpt-6.2-sol`) |
| Effort | medium, high | `EFFORT` (Codex: `model_reasoning_effort`; Pi: `--thinking`) |

That is eight agents per task, one per cell. The user then added `xhigh` (12 cells: 2 harnesses × 2 models × 3 efforts), and Claude cells: Opus 5.5 and Fable 5.2 at medium and xhigh, four cells, on stage 1 only. The Claude cells are kept few on purpose, because they draw on the same quota as the coordinating session ("don't launch a whole fleet, keep an eye on usage"). A full factorial separates the effects: Codex against Pi on the same model and effort isolates the harness, Sol against Astra the model, and medium against high the effort. With one agent per cell no difference is statistically secure. Repeat the cells that matter, rather than adding factors.

Give every cell the same context except the factor under study:
- the same brief, byte for byte;
- the same base revision;
- the same policy text. For Codex it goes in `developer_instructions`. For Pi it goes in `--append-system-prompt`, where it lands in the system message's `addendum` section.

What then differs between the harnesses is their own text and tools. Measure both from the transcripts.

| | Codex CLI | Pi (`--no-extensions --no-mcp`) |
|---|---|---|
| Harness text | 27,750-character system prompt with coding and writing rules | about 2.3K characters (preamble, tools, rules, docs) |
| Skills catalogue | about 46.8K characters | 27.5K characters |
| Tools | code-mode `exec` with `exec_command` | `read`, `bash`, `edit`, `write` |
| Sandbox | workspace-write; network off unless `-c sandbox_workspace_write.network_access=true`; escalations go to an auto-reviewer | none: commands run as the user |
| Transcript | `~/.codex/sessions/.../rollout-*.jsonl`, plus approval sidecars | `--session-dir <dir>`, one JSONL per session, including the system message's sections |
| Resume | `codex exec resume <id>`, appended to the same rollout | `pi -p --session <file>`, appended to the same session |

### Claude cells

A headless `claude -p` with `--dangerously-skip-permissions` is refused by the coordinating session's auto-mode classifier as undermining oversight. Do not route around it. Run Claude cells with the coordinator's own Agent tool instead:
- Set `model` (`opus`, `fable`) and `effort` (`low`, `medium`, `high`, `xhigh`). Setting effort is allowed only when the user asks for those levels.
- Create the worktree yourself, at the same base.
- Give the agent a short prompt that points to its brief, kept in a file outside the repository.
- Continue the agent later with `SendMessage`.

The confounds, to record:
- The agent gets the Claude Code subagent prompt.
- The policy arrives in the task text, not the system prompt.
- Shell state does not persist between commands, so the brief says "start every command with `cd <worktree> && `".

## 3. Blinding

- **Ticket identifiers** carry a letter (IRWB-020-A to H). A seeded shuffle assigns letters to cells, and the key goes to `results/<task>-config-key.json` with `harness`, `model`, `effort` and `round`.
- **The base revision** is chosen before the experiment's own ticket is committed, so no agent can read the briefs, the key or the rubrics.
- **The hidden acceptance suite** stays outside the repository (the coordinator's scratch directory) until every implementation is done, then is committed.
- **The judge and the reviewer** get a blind pack: shuffled `doc-A…` files without frontmatter (`06-blind-pack.mjs`), the brief as `specs/brief.md`, the rubric or protocol, and no key.
- **Every agent gets an isolation line:** "work only from the files in your worktree; do not read other git branches, other worktrees, or other agents' tickets". Check compliance from the transcripts (`10-check-contamination.sh`). Pi has no sandbox, so the line is the only barrier there.

## 4. Fix the comparison surface in the brief

A hidden suite needs a common interface. In the first application the brief fixed three things:
- the language core: grammar, precedence, a rule for how far a reduction's body extends, and the f32 meaning down to rounding and the order of accumulation;
- a three-function API: `compileTix`, `runTix` and `optimizeTix(program, passNames)`;
- the names of the two passes.

Everything else was the agents' to design. The fixed part should be small, precise, and checkable bit for bit. The free part is what the experiment studies.

Write the hidden suite against the brief alone, before seeing any implementation:
- hand-written references that follow the brief's rules literally;
- inputs chosen so that the rules matter, for example magnitudes that make the order of accumulation change the f32 result;
- a few error cases;
- the passes, checked through the API.

Then read the suite against the brief, rule by rule, before any implementation exists, as a reviewer reads a design:
- **Every test program must be valid under the brief.** In the first application, one test used an output index with no use at all. The brief makes that a compile error, so the test would have failed exactly the implementations that follow the brief.
- **Every test must exercise the rule it names.** The `inline` test ran on programs where the brief's inline condition (pointwise, single use) never held, so a pass that did nothing would have passed. Add programs where the rule applies, including one that catches the typical wrong variant (here a transposed read).
- **Assert inside the test that the data separates right from wrong,** for example that row-major and column-major accumulation give different f32 results on the chosen inputs.

If every implementation fails the same test, suspect the reference first.

## 5. The turn structure

One session per agent, continued across turns:
1. **Design.** The agent creates its ticket, writes the design, starts its diary, and commits. The brief says "design only; a reviewer will reply in this session".
2. **Blind score.** A judge subagent scores all designs of the task at once with a rubric: over-engineering counts with quotes, plus fitness criteria specific to the task.
3. **Blind review.** A reviewer subagent writes an engineering review of each design, following a fixed protocol: must change, cut, framework changes, keep, with quotes, at most 350 words. It works in a clean checkout at the agents' base revision, so it can verify repository claims without seeing the experiment. For GPU work it may run a few short probes.
   - **The coordinator verifies the reviewer's load-bearing claims before sending.** In stage 1 there were four framework facts (an unconditional `beginEdit`, a throwing registry, a store that rejects unknown revisions); in stage 2, lazy CUDA module loading inflating the first timed launch. Each was rechecked in the source or on the GPU.
   - **The coordinator checks that no review mentions another document,** and replaces each review's title, which names the author's blind letter. Check both spellings ("doc-A", "doc A").
   - **What review content changed behaviour:** implementers accepted nearly every must-change and cut. But they also implemented less than the reviewed design. In stage 1, all sixteen designs and their reviews included a lazy-edit framework change, and only four of fourteen implementations made it, because the synchronous path made it unnecessary.
4. **Revise and implement.** The agent receives its review, revises the design and implements it in the same turn, with a diary and commits.
5. **Hidden acceptance.** The coordinator builds each worktree and runs three measures, each written before any implementation was read:
   - **A hidden suite of the fixed API,** frozen by hash after its first use.
   - **A differential cross-check:** random valid programs from a generator that evaluates its own syntax trees under the brief's semantics, so the reference needs no parser. Run each implementation in its own process.
   - **A sensitivity variant for any rule the brief turns out not to specify,** reported next to the frozen score, never instead of it.
   
   Report rates over the cases where a measure applies. A pass that cannot change a program counts as "accepted" in most APIs (N's report pointed this out).
6. **Report, with the agent's own results.** The agent receives its evaluation results, including the inputs it failed on, must not change code, and must diagnose every failure with `file:line` before writing its final report in its ticket.
   - This measures something the earlier turns cannot: whether a configuration reports its own failures faithfully, and whether it disputes a result or accepts it. In stage 1 all fourteen reported their results accurately. The two Claude cells conceded their failure ("The suite's result is right and the failure is mine"). The Pi Astra cells framed theirs as "a real accuracy violation, not a rewrite regression".
   - Give every failing input. Agents correctly declined to diagnose the rejections for which only the count was given.
   - Release the hidden material into the repository after this turn, not before.
   - Publish the merged implementation's report to the vault with a note on its provenance. The others stay in their tickets, and the coordinator's report compares all of them.

Scoring the design (step 2) before the review (step 3) keeps the design score a measurement of the configuration, not of the review.

## 6. Shared infrastructure

- **Keep every script in a ticket.** The briefs tell agents to put probes, prototypes and temporary programs in their ticket's `scripts/` directory and commit them. The coordinator does the same: a probe or analysis run only inline or in a session scratchpad is lost to a reboot or a context compaction. IRWB-019 had to archive 38 such scripts after the fact (`scripts/27-scratchpad-archive/`, with an index). A scratchpad holds only bulky generated data that a committed script can rebuild.
Build once, for every configuration, anything that is transport rather than the work under study. Otherwise each agent builds its own version, and the comparison measures that.

- **Remote GPU runner:** `tools/cuda-remote.mjs <dir> [--timed]`.
  - It copies the directory to `bling:~/irwb-cuda/<hash>/`, keyed by content, so identical inputs compile once.
  - It runs `nvcc -O3 -arch=sm_121`, runs the program, and brings `out/` back.
  - `--timed` takes an exclusive `flock` on the GPU, so concurrent agents do not distort each other's timings.
- **Network for sandboxed agents:** pass `-c sandbox_workspace_write.network_access=true` to the Codex cells that need `ssh`. Without it, `ssh` fails with "Could not resolve hostname". Pi needs nothing.

## 7. Measuring behaviour

**Coordinator scripts** (in the experiment's ticket, `scripts/`; they keep the coordinator's own token use small):
- `08-status.mjs [task]`: one line per agent, for every task and harness, from the config keys, the exit files and each worktree's git state. It shows the state, commits, design words, lines added per area, other paths touched, and the last commit subject.
- `09-judge-pack.sh <task> <dir> <rubric>`: writes missing `heads.json` (for Claude cells), packs every design blind, renames the key per task, and copies in the rubric and the neutralized brief.
- `10-dispatch-turn.sh <task> <turn> <template> [reviews|results] [--network]`: one prompt per agent, with its review spliced in through the blind key (or a per-item `<item>.md`, for the results of the report turn). Codex and Pi cells are resumed with the kit's scripts; Claude cells get a prompt file to send with `SendMessage`.
- `12-acceptance.mjs`, `14-impl-summary.mjs`, `15-turn3-results.mjs`: build and test every worktree; one row per implementation (correctness, size, framework diff, commands and output tokens of the implementation turn); each agent's own results as text.
- **Pack designs from the design turn, not from the worktree.** The implementation turn revises the design document in place. A later comparison (a prompting variant against the original designs) must use the turn-1 copies kept in the first blind pack.
- **Evaluation harness hygiene:** a timeout helper must clear its timer, or a finished worker waits out every pending timer before exiting (up to 10 minutes per implementation in stage 2). Exit explicitly after writing the result.
- **Status relative to the right base:** when a stage branches from a merged earlier stage, measure each worktree against its own base (from `heads.json`), or the earlier stage's code appears as each agent's work.
- The kit's Codex launchers accept `CODEX_EXTRA`, for example `-c sandbox_workspace_write.network_access=true`.


- **Codex:** `03-collect-rollouts.mjs` and `04-extract-codex-sessions.mjs` (minutes, tool calls, commands, interpreter runs, skill files read, tokens).
- **Pi:** `14-extract-pi-sessions.mjs` (the same measures, per-tool counts, and the system message's section sizes).
- **During implementation:** `11-snapshot-round.mjs` every few minutes, giving lines per category, test blocks, assertions, helper functions, and edits outside the agent's scope.
- **Count commands from the authoritative record.** Codex rollouts contain one `item_completed` event of type `CommandExecution` for every command run, with the command, a parsed form (`{type: read, path}`) and the exit code. Models differ in how they issue commands. Sol writes one `tools.exec_command({cmd})` call per command. Astra batches several in a JavaScript array mapped over `exec_command`. A regex over the tool-call text therefore undercounts Astra badly (15 against 80 in one session), and Sol by up to 2.6×. An early "Astra skips the skills under Codex" finding was this artifact: all twelve Codex cells read docmgr and diary. `04-` and `11-` now use the events.

## 8. Pitfalls met so far

- **Never edit a launcher script while it runs.** Bash reads a script as it executes it. After the agent it launched exits, bash resumes reading at its old byte offset in the edited file. In IRWB-019 that landed on the launch line twice, and re-ran two finished agents in their own worktrees. Each re-run overwrote its agent's log, and its own final message said the work was "already complete". Copy a launcher before changing it, or kill the outer launcher (not the agents) first. Codex's rollout files (`~/.codex/sessions/`) keep every session, so the lost logs could be recovered from them.
- **zsh does not expand a glob in an assignment.** `S=dir/*/x.sh` leaves the pattern literal. Use `S=$(ls dir/*/x.sh)`.
- **zsh aborts a loop on an unmatched glob** ("no matches found"). Monitors that watch files which do not exist yet must run under `bash -c` with `shopt -s nullglob`.
- **`cmd | while read …; do … & done; wait` does not wait.** The loop runs in a pipeline subshell. Use `while …; done < <(cmd)`.
- **`codex exec` run in the foreground waits on stdin** ("Reading additional input from stdin..."). Pass `< /dev/null`.
- **`node -e 'require(relativePath)'`** resolves against node's own directory, not the shell's working directory. Pass absolute paths.
- **A headless `claude -p --dangerously-skip-permissions` is blocked** in an auto-mode session. Use the Agent tool (see §2).
- **The kit's blind-pack writes `results/blind-key.json` under a fixed name.** With several tasks, rename it per task, or the second pack overwrites the first. `09-judge-pack.sh` does the rename.

- **A sandbox setting is not necessarily a boundary.** Under Codex `workspace-write` with network access off, an agent that needed the network requested escalation on its first call, and the approval-assessor sidecar granted it. Check the rollout for `require_escalated` and for sidecar sessions before relying on a sandbox setting to keep agents apart. Where agents legitimately need a resource, grant it explicitly, so that their use of it stays inside the sandbox and on the record.

- **A policy outranks the brief.** A developer policy rule whose example contradicted the brief's fixed grammar ("reject affine expressions in parameter types") was followed by all four agents over the brief. Write policy rules in terms of the task's own specification ("accept everything the brief fixes"), never with examples that could narrow it.
- **Score policy variants in one judge session.** Two judges differed by up to 4 excess items and 2 fitness points on the same documents. Rescore the baseline documents in the same session as each variant.
- **Don't cap counts unless you mean to.** "Count each kind at most once per document" made a criterion binary (1 in all twelve documents) and hid a difference that an uncapped session had shown.

## 9. Choosing tasks that separate configurations

A task can be too easy to measure anything. In the first application, all twelve configurations derived streaming attention correctly, a design-only research question whose answer is in the literature. Four of the seven rubric criteria were 5 out of 5 for every document. The differences that remained were half a point, with one run per cell.

Prefer tasks where:
- **the answer is not known**, so that the design has to find something;
- **an implementation is scored objectively**, by a hidden suite or a measurement;
- **the brief leaves real choices open**, such as the IR, the contract or framework changes, while fixing the surface the comparison needs.

Use a known-answer question only as a calibration of the rubric.

**Fix only what the comparison needs, and fix it narrowly.** The first stage-1 brief allowed affine expressions in parameter types ("dim := affine expression of shape names and integers"), which no program used. Twelve of sixteen designs then planned a general shape solver. A brief's specification is read as a requirement, and the policy's "keep the domain narrow" does not override it. Write the fixed surface at the generality the corpus uses.

## 10. Prompting the OpenAI models (Sol and Astra)

What two stages, three policies and two harnesses showed about gpt-6.2-sol and gpt-6.2-astra. Each cell had one run, so treat differences under about one rubric point as noise: two judges differed by up to two fitness points on the same document.

**The model matters more than the harness or the effort.**
- Astra over-engineered less than Sol in both harnesses, in both stages: over-engineering 1.8–3.0 against 3.2–4.0.
- Codex · Astra was the best group in both stages.
- Astra's implementations were also smaller (805–1,086 lines of source against Sol's 1,278–1,380 in stage 1), equally correct, and cheaper in output tokens.
- Reasoning effort (medium, high, xhigh) had no consistent effect on any measure. For design and implementation work at this size, medium is enough.
- When the task allows, prefer Astra. Where Sol is needed, give it the policy below.

**The harness effect is not stable.** In stage 1, with the same policy, Codex cells specified half as much excess as Pi cells. In stage 2, Codex · Sol was the weakest group. Report the harness × model interaction, not a harness main effect.

**The policy (developer instructions).**
- v1 (report 10's rules) is the baseline.
- Adding task-specific rules (v3: "accept everything the brief fixes; cover it with the simplest method; reject only what would need unused machinery; rely on stated input assumptions; one path per job; justify every threshold") reduced Sol's excess by one or two items per cell and its over-engineering by about one point, at a fitness cost of about half a point.
- **A policy outranks the brief.** v2's rule carried an example that narrowed the brief's fixed grammar, and every agent followed the policy over the brief. Never put examples in a policy that could contradict a task's specification.
- **Some defaults no wording reached:** unrequested contract statuses, evidence formats, and rules for non-finite values in a brief that says inputs are finite. A brief that wants them gone has to say so for the specific case ("the contract returns only accepted, relation and reason").

**Agents default to the familiar claim.** In stage 2, every design chose a tolerance relation for the GPU lowering. Four had probed the operations that decide exactness and found no mismatch. One implementation (J) built a backend that is bit-exact by construction, with explicit round-to-nearest arithmetic and transcendentals in double, which an exhaustive check over all 2³² inputs confirmed. It still checked and reported it under tolerance. Ask explicitly for "the strongest relation your evidence supports, and the probe that would settle it". Otherwise the agent states the weaker claim even when its own measurement supports the stronger one.

**They implement less than they design, which is usually right.** Implementers dropped proposed framework changes that the final code did not need. Score the implementation, not the design's promises.

**Infrastructure notes for OpenAI agents:**
- Codex agents escalate a blocked command on the first call, and the approval sidecar grants it. Grant needed access (network for ssh) explicitly, so their work stays in the sandbox.
- Astra batches commands in one script, so count commands from `CommandExecution` events.
- A `node --test <dir>` invocation fails on Node 24; give file globs in every brief.

## 11. Judging across model families, and research rounds

Round R2 (IRWB-023) asked Sol and Astra (in Codex), Opus and Fable the same open research question: what compiler work would make Tix best in class? Two blind judges, a Claude subagent and Codex · Sol, scored the designs twice each.

**A judge favours its own family by more than the models differ.**
- The Claude judge scored the two Claude designs 1.5 points higher (out of 10) than the two Codex designs.
- The Codex judge scored the Codex designs 1.75 points higher.
- Their rankings are close to reversed (Claude judge: Opus, Fable, Astra, Sol; Codex judge: Astra, Sol, then Fable and Opus).
- Averaged over both, the largest gap between models was 1.0.
- Each judge repeated itself within 1 point per model, so the bias is systematic, not noise.

Blinding hides the author's name, not their family's style. So:
- **Never rank configurations from different model families with one judge.** Use one judge from each family, report both, and average them. Report how far the families disagree as a result in its own right.
- **Prefer scores that a judge cannot bias:** listed errors, which the coordinator adjudicates, and reproduced experiments.
  - In R2, both judges, in all four runs, listed more errors in the Claude designs (7–19 against 0–4). Every error I re-checked held.
  - The judges differed in rigour more than in direction. The Codex judge listed about three times as many errors.
- **Verify the load-bearing claims yourself before reporting a ranking.** Four of four headline experiments reproduced in R2, and one of them exposed a real hole in the merged base (F21 in the backlog).

**Build the blind pack carefully.**
- **Check completeness, not only leaks.** My first R2 pack copied files by an extension list that missed `.jsonl`. It dropped 21 result logs from three of the four tickets, and none from the fourth, so the error was not neutral. Compare file counts against the source.
- **Neutralize the coordinator's own text.** Claude subagents quote their launch prompt in their diaries, and a different wrapper sets them apart. Replace it, and the scratchpad paths it names.
- **Shuffle with a seed whose permutation actually moves the letters.** A small linear congruential seed can give the identity.

**Research rounds need their own policy and brief.**
- Anti-over-engineering rules cap creativity. v1's "describe only what can be built with the current code" and "prefer the smallest deliverable" would cap a creativity round, and a policy outranks the brief. R2 gave all four cells the same two neutral rules: probe before relying on a feature, and stay isolated.
- **Facts in the brief anchor the ideas.** R2's facts section led with the bit-exact result, and all four designs centred on exactness. If breadth is the point, give facts without a lead.
- **Give every cell the same research tools.** Codex `exec` has no `--search` flag, but `-c web_search=live` works.
- **Expect agents to finish early.** All four finished in 16–62 minutes of a three-hour budget.

**Running Codex headless:** `codex exec` reads extra prompt input from a non-terminal stdin. A command inside a backgrounded shell inherits an open one and waits forever ("Reading additional input from stdin…"). Always pass `< /dev/null`.

## 12. More model families, and implementation stages with hidden evaluators

IRWB-019 added DeepSeek 4.1 Flash, GLM 5.3 and GLM 5.3 Flash (through Pi and the LunaRoute provider) to both research rounds. It then ran stage 3, checked CUDA fusion, on a ten-cell matrix: Codex Sol and Astra medium, Terra low; Opus; Fable; and five Pi cells.

**Adding a provider through Pi.**
- **Read the model's thinking-level map** (`~/.pi/agent/models-store.json`) before choosing efforts. GLM 5.3 and GLM 5.3 Flash map `xhigh` to nothing, so "xhigh" there silently means something else.
- **A provider can cap one streamed response.** LunaRoute ends a response at exactly 20 minutes ("the upstream stream failed before completion"). GLM 5.3 Flash at max thinks longer than that while planning a large implementation, and failed twice in the same way, without a commit. Before a long task, measure each max-effort cell's longest single request in earlier rounds; a cell near the cap will fail. Do not retry a systematic failure.
- **Load the provider's extension explicitly** (`--no-extensions --no-mcp -e <extension>`), because `--no-extensions` alone removes its models.

**Blind packs with several families.**
- **Scan for leaks with word boundaries.** A substring scan flags "fable" inside "diffable" and "Glm" inside base64. Neutralize lowercase and hyphenless ticket IDs too (`irwb-023e` in a script).
- **Choose the ticket directory with the most files.** One agent left an empty directory literally named `IRWB-023-E--*`, an unexpanded glob, which sorted first and packed an empty ticket.
- **Audit the judges from their session records.** A script that scans each Codex judge's tool calls for paths outside the pack and the base repository (the blind key, the config keys, the coordinator's ticket, other worktrees) found none in seven sessions. The Claude judges' transcripts need the same check.
- **Claude judges cost the most.** Scoring 19 and 11 documents took 445K and 527K tokens, and the second judge spawned its own citation-checking subagents.

**What the new families showed.**
- **Research and design:** both judges placed every new cell below every OpenAI and Anthropic cell. Their documents were two to five times longer, with real mathematical errors and some fabricated references. The two judges' rankings agreed at 0.88–0.89, because neither belonged to the new families.
- **Implementation:** under a precise brief and an exact hidden evaluator, all nine stage-3 cells that ran were correct. The new families' fusion speed-ups came close to Opus's and Fable's. So research rounds separate the configurations far more than implementation stages do.
- **Time:** the Codex cells finished in 4–15 minutes, and the others in 43–77.

**Make the hidden programs differ in structure from the visible ones.** Stage 3's hidden programs (from stage 1's hidden suite) divide inside reductions: `sum(d) x / D`. The visible corpus divides the reduced value. Every agent measured layernorm 2–3× faster on the visible corpus. On the hidden programs, fused layernorm and attention were mostly slower than unfused, because the division ran in one thread's serial loop.
- Without the structural difference, the agents' performance claims would have gone unchallenged.
- When the next brief names such variants, the hidden evaluation needs held-out programs that the brief does not name. Write them before the agents start.

**Verify contradictory findings before recording either.** Two cells reported opposite results on the same framework check: made-up correspondence IDs accepted, and an undeclared ID rejected. Reading the code showed one gap: the entity lists are declared by the caller and never compared with the artifacts.

## 13. Open questions *(to be filled as the experiment proceeds)*

- Does a review change designs in the same direction for every configuration?
- **How do design scores predict hidden results?** In stage 1, not at all at the level of correctness: every implementation was correct, whatever its design score. Design scores did predict size and contract quality.
- What does the harness change, with the same model and policy? The answer so far is: something for Astra, nothing stable for Sol (§10).
- *(Answered.)* Do the stage-1 and stage-2 design scores, judged by Claude subagents alone, carry the family effect §11 measured? Yes, across families. On stage 1 (12 OpenAI and 4 Claude designs) a Codex judge's fitness ranking correlates at −0.29 with the Claude judge's. On stage 2 (OpenAI designs only) the two judges agree, at 0.62.
- Do the differences survive repeated runs per cell? This needs M2: three runs of the cells that differ most.
- Does effort help the weaker families? DeepSeek and GLM scored higher at higher effort in R2 (under both judges, all but one pair), but not in R1. One run per setting.

## Related notes

- [[PLAYBOOK - Measuring and Reducing Over-Engineering in Agent-Written Designs]]
- [[PROJECT REPORT - IR Workbench - Tensor Programs on the v6 Framework - Tix, CUDA on a GB10, and Four Codex Configurations on the Same Tasks - A Technical Deep Dive]]
- [[PROJECT REPORT - IR Workbench - Codex Agents as Designers - Where the Over-Engineering Comes From, and What a Revised Brief and a Self-Review Change - A Technical Deep Dive]]
