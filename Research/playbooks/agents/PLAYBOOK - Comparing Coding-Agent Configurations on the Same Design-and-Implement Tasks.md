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

That is eight agents per task, one per cell. A full factorial separates the effects: Codex against Pi on the same model and effort isolates the harness, Sol against Astra the model, and medium against high the effort. With one agent per cell no difference is statistically secure. Repeat the cells that matter, rather than adding factors.

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

If every implementation fails the same test, suspect the reference first.

## 5. The turn structure

One session per agent, continued across turns:
1. **Design.** The agent creates its ticket, writes the design, starts its diary, and commits. The brief says "design only; a reviewer will reply in this session".
2. **Blind score.** A judge subagent scores all designs of the task at once with a rubric: over-engineering counts with quotes, plus fitness criteria specific to the task.
3. **Blind review.** A reviewer subagent writes an engineering review of each design, following a fixed protocol: must change, cut, framework changes, keep, with quotes, at most 350 words. The coordinator checks the reviews against the designs before sending each one to its author. *(to be filled: what review content changes behaviour)*
4. **Revise and implement.** The agent receives its review, revises the design and implements it in the same turn, with a diary and commits.
5. **Hidden acceptance.** The coordinator builds each worktree and runs the hidden suite against it. *(to be filled)*
6. **Report.** The agent writes its report draft in its ticket. The coordinator publishes it.

Scoring the design (step 2) before the review (step 3) keeps the design score a measurement of the configuration, not of the review.

## 6. Shared infrastructure

Build once, for every configuration, anything that is transport rather than the work under study. Otherwise each agent builds its own version, and the comparison measures that.

- **Remote GPU runner:** `tools/cuda-remote.mjs <dir> [--timed]`.
  - It copies the directory to `bling:~/irwb-cuda/<hash>/`, keyed by content, so identical inputs compile once.
  - It runs `nvcc -O3 -arch=sm_121`, runs the program, and brings `out/` back.
  - `--timed` takes an exclusive `flock` on the GPU, so concurrent agents do not distort each other's timings.
- **Network for sandboxed agents:** pass `-c sandbox_workspace_write.network_access=true` to the Codex cells that need `ssh`. Without it, `ssh` fails with "Could not resolve hostname". Pi needs nothing.

## 7. Measuring behaviour

- **Codex:** `03-collect-rollouts.mjs` and `04-extract-codex-sessions.mjs` (minutes, tool calls, commands, interpreter runs, skill files read, tokens).
- **Pi:** `14-extract-pi-sessions.mjs` (the same measures, per-tool counts, and the system message's section sizes).
- **During implementation:** `11-snapshot-round.mjs` every few minutes, giving lines per category, test blocks, assertions, helper functions, and edits outside the agent's scope.
- **First observation:** in the Codex cells, Astra read no skill file in three of its four agents, and Sol read docmgr and diary in all four. Record which skills each cell reads, because the skills carry conventions such as diaries and tickets.

## 8. Pitfalls met so far

- **zsh does not expand a glob in an assignment.** `S=dir/*/x.sh` leaves the pattern literal. Use `S=$(ls dir/*/x.sh)`.
- **zsh aborts a loop on an unmatched glob** ("no matches found"). Monitors that watch files which do not exist yet must run under `bash -c` with `shopt -s nullglob`.
- **`cmd | while read …; do … & done; wait` does not wait.** The loop runs in a pipeline subshell. Use `while …; done < <(cmd)`.
- **`codex exec` run in the foreground waits on stdin** ("Reading additional input from stdin..."). Pass `< /dev/null`.
- **`node -e 'require(relativePath)'`** resolves against node's own directory, not the shell's working directory. Pass absolute paths.

## 9. Open questions *(to be filled as the experiment proceeds)*

- Does a review change designs in the same direction for every configuration?
- How do design scores predict hidden-suite results?
- What does the harness change, with the same model and policy?

## Related notes

- [[PLAYBOOK - Measuring and Reducing Over-Engineering in Agent-Written Designs]]
- [[PROJECT REPORT - IR Workbench - Tensor Programs on the v6 Framework - Tix, CUDA on a GB10, and Four Codex Configurations on the Same Tasks - A Technical Deep Dive]]
- [[PROJECT REPORT - IR Workbench - Codex Agents as Designers - Where the Over-Engineering Comes From, and What a Revised Brief and a Self-Review Change - A Technical Deep Dive]]
