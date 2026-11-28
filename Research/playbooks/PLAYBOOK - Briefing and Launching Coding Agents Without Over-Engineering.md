---
title: "Playbook: Briefing and Launching Coding Agents Without Over-Engineering"
aliases:
  - "agent briefing playbook"
  - "how to launch codex pi and claude agents"
  - "anti over-engineering policy for coding agents"
tags:
  - playbook
  - agents
  - codex
  - pi
  - claude
  - prompting
status: active
type: article
created: 2026-11-27
repo: /home/manuel/code/wesen/2026-11-24--compiler-workbench
---

# Playbook: briefing and launching coding agents without over-engineering

This is the self-contained entry point for running coding agents (OpenAI models through Codex, open models through Pi, Claude models as subagents) on design and implementation work. It holds the policy text that every agent gets, the brief structure, the exact launch commands, what each model family needs, the process rules that keep parallel agents from damaging each other, and how to judge the results. Everything here was measured in the IR Workbench experiments (IRWB-018, IRWB-019, IRWB-033 to IRWB-039); the two detailed playbooks linked at the end hold the evidence and the scripts.

> [!summary]
> - **Over-engineering has specific causes, and one rule per cause removes it.** A short developer policy (below) took gpt-6.2-sol's blind over-engineering score from 6.33 to 1.00 and its fitness from 6.67 to 8.67. An open-ended "review yourself" pass reached only 3.17 and 7.33.
> - **The policy outranks the brief.** Never put an example in the policy that could narrow a task's specification. Scope limits for a particular task go in that task's brief.
> - **Match the agent to the task's kind, not its size.** Cheap execution agents do well when the brief names the files, the change and a test that must flip; they fail on open design. Strong models are for the steps whose choice everything after copies.
> - **Judge with evidence a judge cannot bias:** hidden evaluators, flipped tests, verified error lists. A judge favours its own model family by more than the models differ.

## 1. The policy every agent gets

Give this text, unchanged, to every implementation or design agent. For Codex it is `developer_instructions` (a developer message, ranked above AGENTS.md); for Pi it is `--append-system-prompt`; for a Claude subagent it is a "Standing instructions" section at the top of the task text.

```text
When writing a design, specification or plan (as opposed to changing code now):
- State the supported input domain explicitly and specify behaviour only within it. Do not add status codes, error precedence or guarantees about state on failure for inputs outside it unless the user asks for them.
- For each significant decision, name the simplest alternative that would serve the goal and say why it was chosen or why it falls short. In design documents, decision records and reviews, comparing alternatives is requested; contrastive phrasing is allowed for that purpose.
- Covering every part of a request means addressing each requested item, not maximizing its depth. Where the brief invites new approaches, try at least one, measure it, and report what it gave, including a negative result. Keep everything else no larger than the goal needs, and list what you left out and why.
- Describe only what you build in this session, including new IRs, passes and framework changes the task needs. Work that depends on features you do not build gets one line each in a "Later" list.
- If a small piece of infrastructure is missing, propose the change instead of designing around it.
When you build or change a compiler, its IRs or its passes:
- Use the framework's concepts wherever they exist: analyses defined as framework analyses and declared as a pass's needs, edits through the IR layer's transactions with correspondence, rewrites through its patterns and schedules, pipelines through strategy plans. Before writing machinery inside a domain, look for the framework concept that does the job.
- If you build machinery inside a domain that duplicates a framework concept, or that the framework should provide, say so in your report: what it is, which concept it duplicates or which is missing, and why you built it there.
- When the framework lacks a concept, prefer adding it to the framework, domain-independently, stated in its standard theory (lattices and fixpoints, dependence analysis, rewriting, translation validation), with the second use it would have.
When the brief specifies a language, grammar or API:
- Accept everything the brief fixes; that surface is not yours to narrow. Cover it with the simplest method that works. Where full generality would need machinery no example uses, reject that case with an ordinary error and list the general case under "Later".
- Rely on the assumptions the brief states about inputs (for example "inputs are finite"). Do not specify checks, encodings or rules for inputs that violate them.
- Specify an error only by where it is detected and what its message says. Do not define error classes, codes, precedence or recovery beyond those the brief names.
- Build one path for each job. Do not plan a second implementation of the same job (a synchronous and an asynchronous checker, a fast and a reference verifier) unless the brief requires both.
- Justify every numeric threshold (a tolerance, a case count, a block size) by an error argument or a measurement, not by a round number.
In all tasks: before relying on a language, library, loader or tool feature you have not seen work in this repository, run a minimal probe and state the result.
Work only from the files in your worktree (and any outside repository your task names). Do not read other git branches, other worktrees, or other agents' tickets.
```

The middle block ("When you build or change a compiler…") is domain-specific: replace it with the equivalent for your codebase's framework, or drop it.

### Why each rule is there

Each rule answers a cause observed in transcripts and blind-judged designs, not a general preference.

| Rule | Observed cause it removes |
|---|---|
| Valid inputs only; no invented status codes | designs specified error contracts, codes and failure-state guarantees nobody asked for (28 such items in one round, 0 after the rule) |
| Name the simplest alternative | Codex's own system prompt discourages unsolicited comparison, so designs never said why the big option beat the small one; once asked, they often chose the small one |
| Address each item, not maximize depth | "cover the request" was read as "cover it exhaustively" |
| Describe only what you build; "Later" list | designs promised features for later sessions in the same detail as this one's |
| One path per job | a synchronous and an asynchronous checker, a fast and a reference verifier, designed side by side |
| Justify thresholds | round-number tolerances and case counts with no argument |
| Probe before relying on a feature | designs built on loader and library behaviour that did not hold in the repository |
| Accept everything the brief fixes | an earlier rule with an example ("reject affine expressions in parameter types") contradicted the brief's grammar, and every agent followed the policy over the brief |
| Framework first; report domain-local machinery | domains rebuilt framework concepts (a strategy interpreter, a dataflow solver, rewrite engines) without saying so |

### Research rounds get a different policy

Anti-over-engineering rules cap creativity, and a policy outranks the brief. For a research or review round, replace the policy with a short neutral one:

```text
In this research review:
- Be creative. Where the evidence suggests that the system should change at its root, say so and argue it; do not limit proposals to what is easy to build now. Mark which proposals are evidenced by the material and which are conjecture.
- Ground every proposed concept in established theory and name it precisely; cite sources only when you have verified them.
- Every claim about the repository cites path:line. Before relying on a behaviour you have not seen work in this repository, run a minimal probe and state the result. Keep every probe in your ticket's scripts/ directory and commit it.
- Write no production code. Change files only in your own worktree; other worktrees the brief lists are read-only material.
- Never use git stash: every worktree of this repository shares one stash stack. To set work aside, make a temporary commit.
```

## 2. The brief

A brief is the task, written once and given byte for byte to every cell. It has five parts.

1. **Orientation.** What the repository is, in a paragraph; the files to read first; "Your ticket is <ID>" (the launcher substitutes the ID).
2. **The task.** What to achieve, the facts the agent needs (measured numbers, where earlier work lives), and what is fixed. Fix only what the comparison or the merge needs, at the generality the inputs actually use: a brief's specification is read as a requirement, and an unused generality in it (an affine expression no program uses) gets designed for by most agents.
3. **Acceptance.** The checks that decide "done": a test that must pass, a baseline that must not change, a measurement. For an execution agent this is the most important part (§4).
4. **Repository facts.** The standing block below.
5. **Final message.** Exactly what to report: paths, numbers, the last commit hash.

Repository-facts block (adapt the paths):

```markdown
## Repository facts
- **Build and test:** build with `npm run build`. Tests are `node --test tests/<dir>/<name>.test.mjs`; on Node 24, pass files, not a bare directory. Run <the suites> before your last commit. Do not run the full suite: other agents share this machine. Prettier: <settings>; run it only on files that were formatted before you changed them.
- **Scope:** you may change <dirs>. Do not change <dirs>, unless your task says so.
- **Scripts:** put every probe, benchmark and temporary program you write in your ticket's `scripts/` directory, numbered in the order you write them (`01-name.mjs`), and commit them. Nothing you ran should exist only in a scratch directory or a one-off command.
- **Sandboxed sessions:** a test that spawns `node` can fail with EPERM. Request escalation for that command.
- **Tickets and commits:** use your docmgr and diary skills. Commit on your current branch with messages starting `<ID>:`, as you go, so that your last commit always holds working code. Do not push.
- **Never use `git stash`:** every worktree of this repository shares one stash stack with other agents' worktrees. To set work aside, make a temporary commit.
- **Outside your worktree,** use nothing.
```

Brief-writing rules that held up:

- **Facts anchor ideas.** A facts section that leads with one result makes every design centre on it. If breadth is the point, give facts without a lead.
- **Ask for the strongest claim the evidence supports.** Agents default to the familiar weaker claim (a tolerance) even when their own probe shows the stronger one (bit-exact). Write "the strongest relation your evidence supports, and the probe that would settle it".
- **Name the specific unwanted default.** Some defaults no general rule reaches (unrequested contract statuses, rules for non-finite values when inputs are finite). A brief that wants them gone says so for the case.
- **Tell implementers what existing tests already cover,** and put repository conventions (line widths, file layout) in the repository's AGENTS.md, not only in a brief.
- **Grant narrow access instead of banning a directory.** "You may fix `tools/x.mjs` where the task needs it" beats "do not touch `tools/`".
- **Bound expensive probes.** One agent spent hours computing a CPU reference for a 4096³ matmul outside its ticket. State the largest size a probe may run, or a time limit.

## 3. Launching

Every agent gets its own git worktree and branch from one fixed base revision, so cells cannot see or break each other, and each cell's work survives as a branch.

```bash
git worktree add -b <round>/<item> <worktrees>/<round>-<item> <base>
```

### Codex (OpenAI: gpt-6.2-sol, gpt-6.2-astra, gpt-6.1-terra)

```bash
cd <worktree> && timeout <seconds> codex exec \
  -m <model> -c model_reasoning_effort=<low|medium|high|xhigh> \
  -c "developer_instructions=<policy as a JSON string>" \
  -s workspace-write --add-dir <repo>/.git \
  -o <logs>/<item>.last-message.md "<brief>" \
  < /dev/null > <logs>/<item>.log 2>&1
```

- `< /dev/null` is required: `codex exec` reads extra prompt input from a non-terminal stdin and a backgrounded command waits forever otherwise.
- `--add-dir <repo>/.git` lets a worktree commit (its git directory lives in the main checkout).
- A JSON string is a valid TOML basic string, so `node -e 'process.stdout.write(JSON.stringify(fs.readFileSync(f,"utf8")))'` produces the `-c` value.
- The sandbox is not a boundary: an agent that needs the network escalates on its first call and the approval sidecar grants it. Grant what a task legitimately needs (`-c sandbox_workspace_write.network_access=true` for ssh to a GPU host) so the use stays on the record.
- Web search: `-c web_search=live` (`codex exec` has no `--search`).
- Only `gpt-6.1-terra` runs on a ChatGPT account; `gpt-6.2-terra` is refused.
- Transcripts: `~/.codex/sessions/.../rollout-*.jsonl`; resume with `codex exec resume <id>`.

### Pi (open models through a provider: GLM 5.3, GLM 5.3 Flash, DeepSeek 4.1 Flash)

```bash
cd <worktree> && timeout <seconds> pi -p --no-extensions --no-mcp -e <provider extension> \
  --tools read,bash,edit,write --model <provider>/<model> --thinking <level> \
  --session-dir <kit>/sessions/<item> --append-system-prompt <policy file> "<brief>" \
  < /dev/null > <logs>/<item>.log 2>&1
```

- `--no-extensions` removes the provider's models too; load its extension explicitly with `-e`.
- Pi has no sandbox. The isolation rules in the brief are the only boundary; check afterwards that no agent touched another worktree.
- Read the model's thinking-level map (`~/.pi/agent/models-store.json`) first: GLM 5.3 and GLM 5.3 Flash have no `xhigh`, so asking for it silently gives another level.
- The LunaRoute provider ends one streamed response at 20 minutes. A max-effort cell that plans a large task in one response fails there without a commit (GLM 5.3 Flash at max failed twice). Check a cell's longest single request in earlier rounds before giving it a long task; do not retry a systematic failure.

### Claude (Opus, Fable) as subagents of the coordinating session

A headless `claude -p --dangerously-skip-permissions` is refused by the coordinator's auto-mode classifier as undermining oversight. Do not route around it. Use the coordinator's Agent tool:

- create the worktree yourself, at the same base;
- the prompt is a wrapper: "Your git worktree is <path> (branch <branch>). Run every command in it (cd there first), and change files only there.", then "## Standing instructions" with the policy, then "## The task" with the brief;
- set `model` (`opus`, `fable`); set `effort` only when the user names a level;
- continue the agent later with SendMessage.

Confounds to record: the agent also gets the Claude Code subagent prompt; the policy arrives in the task text, not the system prompt; shell state does not persist, so every command starts with `cd <worktree> &&`. Claude cells draw on the coordinator's own quota, so keep them few unless the user says otherwise.

### Launcher scripts

- **Never edit a launcher while it runs.** Bash reads a script as it executes it and resumes at its old byte offset in the edited file; in one run that re-launched two finished agents over their own logs. Copy it first.
- In zsh, a glob in an assignment stays literal, an unmatched glob aborts a loop, and `$VAR` holding several paths is not split. Write launchers in bash, with arrays.
- `cmd | while read …; do … & done; wait` does not wait (the loop runs in a subshell). Use `while …; done < <(cmd)`.
- Pass absolute paths to `node -e 'require(…)'`: it resolves against node's directory.
- Record per round: each agent's log, its final message, exit codes and a `heads.json` of the branches. Keep raw transcripts out of public repositories: they carry system prompts and account details.

## 4. Which agent for which task

The record from IRWB-019 (one run per cell, so differences under about a rubric point are noise):

| Agent | Precisely specified fixes | Open design-and-implement tasks | Research and design rounds |
|---|---|---|---|
| Codex · gpt-6.1-terra, low | good: three fix rounds done in 4–6 minutes each, at most one review round | poor: stopped early (two stages), committed nothing (one), incomplete (one) | — |
| Pi · GLM 5.3, high | — | mid-pack (−1.8% where the best cell reached −9.0%) | below the OpenAI and Anthropic cells |
| Pi · DeepSeek 4.1 Flash, xhigh | — | unreliable: left work uncommitted; wrote a script that never terminated | below; documents 2–5× longer, some fabricated references |
| Pi · GLM 5.3 Flash, high | — | one cell's generated code failed to compile | below |
| Codex · gpt-6.2-astra, medium | — | solid and small; best Codex group in both design stages | over-engineers least of the OpenAI models |
| Codex · gpt-6.2-sol, medium | — | solid, conservative | needs the policy most |
| Opus, Fable (subagents) | — | won the open stages | widest reviews; judges listed more errors in their designs |

**IRWB-039's matrix** (seven framework-refactor steps × Terra low, GLM 5.3 high, DeepSeek xhigh; each brief carried a `todo` test of the correct behaviour, a baseline that must not move, and the probe that showed the defect):
- 19 of 21 cells met the full acceptance. GLM and DeepSeek passed all seven, including steps I had predicted needed Sol, Astra or Fable (a coverage policy, atomic publication, a library's first module). Terra passed five; it stopped at the design of atomic publication, and left one test that asserted the old defect failing because the brief told it not to weaken tests.
- Tests could not see the differences that mattered: a library interface that left scope implicit, a publication fix that left the rejected candidate's analyses cached, and one agent that rewrote the coordinator's baseline file instead of reporting the difference. Read every design-bearing diff.
- The preparation is the strong-model work: turning a design question into a test that must flip and a baseline that must not move. With that done, cheap agents carry the implementation.

**IRWB-039 phases 2–4** (17 more cells; every cell scored on its commit and its diff reviewed):
- **Library extraction, two cheap cells per lane** (GLM high, DeepSeek xhigh): 10 of 10 cells passed every check. In every lane the review, not the tests, chose the cell: one moved the second client and one did not; one hid a 5× slowdown and one fixed it; one met "classification as a query" only by calling the old classifier.
- **An open design question as a spike** (Sol low, Astra low, Fable): all three converged on the same design, which is evidence that the design is the natural one. Fable then migrated every pass in 28 minutes, and later did the fusion-and-scheduling rewrite in 25.
- **A decision point as the experiment's acceptance** (Sol low on `solveFor` and `pe`): the cell measured its own gate (652 lines against a limit of 324), withdrew the idea, restored the code and kept the part that earned its place. A gate stated as a number, in the brief, gets honoured.
- **Forbidding edits to the coordinator's ticket worked:** no cell touched the baselines after the brief said so, and the scorer checks it (`oracleFilesTouched`).
- **Sandboxed Codex cells can misreport test failures.** A Terra cell saw four failing test files inside the sandbox; the scorer, outside it, found none. Score outside the sandbox.

Working rules:

- **An execution agent can do a step if the brief names the files, the change, and a test that must flip.** Write the test first (as a `todo` test of the correct behaviour) and the step becomes mechanical.
- **Tell agents what to do with tests that assert the defect** (update them, and say which), and **forbid editing the coordinator's oracles** (baselines, evaluators): report a difference instead.
- **A strong model is needed where the step makes a choice that later steps copy:** a new API, a library's layering, a policy that applies across domains. Run two or three strong cells on a spike, judge them on the tests, then let one implementer migrate.
- **Effort (medium, high, xhigh) had no consistent effect** on design or implementation quality at this size. Medium is enough for the OpenAI models.
- **The model matters more than the harness.** Codex against Pi on the same model changed results inconsistently across stages; report the interaction, not a harness effect.
- **Implementers build less than their designs promise, and that is usually right.** Score the implementation, not the design.
- **Codex cells finish in minutes; Pi and Claude cells take most of an hour.** Expect agents to finish research rounds early (16–62 minutes of three hours).

Process safeguards that cheap agents need:

- **"Commit as you go so your last commit holds working code."** After the run, snapshot any uncommitted work as a labelled commit on the cell's branch before judging, so nothing is lost and nothing is credited that was not committed.
- **Check the commit, not the final message.** Execution agents report success they did not achieve.
- **Timeouts on every agent** (`timeout <seconds>`), and a look at stray processes afterwards: kill by exact PID after checking, never by pattern.

## 5. Shared machine and repository hazards

- **`git stash` is shared** by every worktree of a repository. One agent's stash emptied the stack other sessions relied on. The rule is in every brief and policy.
- **Agents share CPU and memory.** Briefs forbid the full test suite; heavy jobs run one at a time under a memory cap.
- **Scripts live in the ticket.** Every probe an agent runs is a numbered file in its ticket's `scripts/`, committed, so results can be reproduced and audited.
- **Public repositories:** scan every branch's added lines for secrets and private strings before pushing. Never write the private strings themselves into a scanning script; pass them through an environment variable.

## 6. Judging and merging

- **Hidden evaluators, written before reading any cell's code,** decide implementation stages: exactness, a measured metric at the agents' seed and at a held-out seed the brief never names, the suites, and the scope of changes. Evaluate the current main in the same run, as the baseline.
- **Held-out inputs must differ in structure from the visible ones.** Stage-3 agents all measured layernorm 2–3× faster on the visible corpus; on hidden programs that divide inside the reduction, fused code was slower. Held-out programs later exposed a 6.6× regression no visible program showed.
- **Blind judges favour their own family** by 1.5–1.75 points out of 10, more than the models differ. Use one judge per family and average; prefer scores a judge cannot bias (listed errors the coordinator adjudicates, reproduced experiments).
- **Blind packs:** check completeness (file counts against the source), neutralize the coordinator's wrapper text, scan for leaks with word boundaries, and shuffle with a seed that actually permutes.
- **Verify load-bearing claims yourself** before reporting a ranking or recording a backlog item, and keep a corrections list when later evidence overturns an earlier claim.
- **Merge by cherry-pick, never by merging branches.** Keep framework edits only where the merged domain code needs them; record what a cell built inside its domain that duplicates a framework concept.
- **Push every cell's branch,** merged or not, so unmerged experiments stay linkable from reports.

## Related notes

- [[PLAYBOOK - Measuring and Reducing Over-Engineering in Agent-Written Designs]]: the method behind §1, with the blind-judging kit (`agents/scripts/agent-design-review/`).
- [[PLAYBOOK - Comparing Coding-Agent Configurations on the Same Design-and-Implement Tasks]]: the matrix method, harness comparison and pitfalls in full.
- Repository: `/home/manuel/code/wesen/2026-11-24--compiler-workbench`, tickets IRWB-018, IRWB-019 (the coordinator's diary and every brief under `various/prompts/`), IRWB-039 (the v7 refactor and the execution-agent matrix).
