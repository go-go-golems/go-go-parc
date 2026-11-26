# agent-design-review

Scripts for running parallel Codex design agents in rounds, analysing their native transcripts, and scoring their documents with a blind judge. The procedure, the reasoning behind each step, and the pitfalls are in [[PLAYBOOK - Measuring and Reducing Over-Engineering in Agent-Written Designs]] (`Research/playbooks/agents/`).

The first application was IRWB-018 in `/home/manuel/code/wesen/2026-11-24--compiler-workbench`. Every script here was run against that data and reproduces its numbers.

## Requirements
- `git`, `codex` CLI (tested with 0.172.0), `node` 20 or later, `python3` with `matplotlib`. For harness comparisons, `pi` (tested with 1.5.1).
- Codex rollouts under `$CODEX_HOME/sessions` (default `~/.codex`). They are read, never modified.

## Quick start

```bash
cp 00-env.example.sh env.sh && $EDITOR env.sh && source env.sh
K=/path/to/go-go-parc/Research/playbooks/agents/scripts/agent-design-review

# 1. Baseline round. Prompts: prompts/baseline/common.md and prompts/baseline/<item>.md
#    (start common.md from templates/baseline-brief-skeleton.md).
bash $K/01-launch-codex-round.sh baseline prompts/baseline ITEM-1 ITEM-2 ITEM-3

# 2. Review the baseline by hand, then analyse what the agents saw and did.
node $K/03-collect-rollouts.mjs $OUT baseline
node $K/04-extract-codex-sessions.mjs $OUT/baseline/rollouts/sessions.tsv $OUT/baseline/extract

# 3. Interventions, started together. Round 2 gets a revised common.md (templates/policy-brief-section.md inserted)
#    and the same item files. Round 3 resumes the baseline sessions with templates/self-review-prompt.md.
bash $K/01-launch-codex-round.sh revised prompts/revised ITEM-1 ITEM-2 ITEM-3 &
bash $K/02-resume-codex-round.sh selfreview baseline $K/templates/self-review-prompt.md ITEM-1 ITEM-2 ITEM-3 &
wait
node $K/03-collect-rollouts.mjs $OUT revised
node $K/03-collect-rollouts.mjs $OUT selfreview --turn 2      # resume appends turn 2 to the baseline rollouts
bash $K/10-check-contamination.sh $OUT revised baseline selfreview

# 4. Blind judge. Fill templates/rubric.template.md and judge-prompt.template.md first; specs/ holds the item specs.
node $K/06-blind-pack.mjs $OUT $JUDGE --rounds baseline,revised,selfreview --doc-regex 'design-doc/.*\.md$'
cp rubric.md $JUDGE/RUBRIC.md && mkdir -p $JUDGE/specs && cp prompts/baseline/ITEM-*.md $JUDGE/specs/
#    ...run the judge agent with the filled judge prompt; it writes $JUDGE/scores.json...
node $K/07-verify-quotes.mjs $JUDGE

# 5. Results.
node $K/08-aggregate.mjs $JUDGE/scores.json $OUT/results/blind-key.json --order baseline,revised,selfreview --md $OUT/results/summary.md
python3 $K/09-figures.py $JUDGE/scores.json $OUT/results/blind-key.json $OUT/results/rounds.png --order baseline,revised,selfreview --labels "Baseline|Revised brief|Self-review"
node $K/05-content-metrics.mjs $(node -e 'for (const k of require(process.argv[1])) console.log(`${k.item}-${k.round}=${process.argv[2]}/docs/${k.name}`)' $OUT/results/blind-key.json $JUDGE)
```

Keep `$JUDGE` outside `$OUT`, so that the judge never sees the key. Commit `$OUT`: logs, `heads.json`, extracts, key, scores.

If `$OUT` lies inside a docmgr ticket, `docmgr doctor` will reject the raw material the scripts write (prompts, `*.last-message.md`, and the extracts `system-prompt.md`, `skills-catalogue.md`, `agents-md.md`, `multi-agent.md`, `messages.md`), because none of it has frontmatter. `.docmgrignore` matches file and directory *names*, not paths, so add name globs to `ttmp/.docmgrignore`: those names, `*.last-message.md`, your prompt file names, and `*judge-rubric*.md`. IRWB-018's commit `230fec2` in the compiler-workbench repository is an example.

## Scripts

| Script | Does |
|---|---|
| `00-env.example.sh` | Settings: repo, base revision, output, worktree root, model, effort |
| `01-launch-codex-round.sh` | One fresh `codex exec` per item, each in its own worktree and branch, in parallel. Records `heads.json`. With `DEV_INSTRUCTIONS_FILE` set, passes that file as `developer_instructions` |
| `02-resume-codex-round.sh` | `codex exec resume` of each agent of an earlier round with one prompt. Records the new heads |
| `03-collect-rollouts.mjs` | Maps session ids to rollouts, cuts a resumed rollout to one turn, finds approval sidecars by worktree and time window |
| `04-extract-codex-sessions.mjs` | Extracts system prompt, skills catalogue, AGENTS.md, commands, reads, skill loads, interpreter runs, minutes, tokens |
| `05-content-metrics.mjs` | Keyword-family shares, guarantee phrases, contrast markers, semicolons, "would … but" weighings per 1,000 words |
| `06-blind-pack.mjs` | Shuffled, frontmatter-free documents for a judge (resumed rounds read at recorded revisions), plus the key |
| `07-verify-quotes.mjs` | Checks that every judge quote occurs verbatim in its document |
| `08-aggregate.mjs` | Per-round sums and means, plus per-item over-engineering and fitness |
| `09-figures.py` | Small multiples: words, over-engineering, fitness by item and round |
| `10-check-contamination.sh` | Commands in a round that touch other rounds' branches or worktrees |
| `11-snapshot-round.mjs` | Live or final snapshot of a round: lines added per category (source, test, harness, docs, data), test cases, assertions, functions in test and harness code, edits under `src/` or `tools/`, and from the live rollout minutes, test runs, builds, latest commentary. Appends to `snapshots.jsonl` |
| `12-launch-pi-round.sh` | The Pi counterpart of `01`: one `pi -p` per item in its own worktree, with `--no-extensions --no-mcp` (Pi's base prompt, four tools, skills) and `DEV_INSTRUCTIONS_FILE` appended to the system prompt. Sessions go to `$OUT/<round>/sessions/<item>/`. Pi has no sandbox |
| `13-resume-pi-round.sh` | The Pi counterpart of `02`: continue each Pi session with one prompt (`--session <file>`) |
| `14-extract-pi-sessions.mjs` | The Pi counterpart of `04`: commands, reads, skill loads, interpreter runs, minutes, tokens, per-tool counts, and the system message's section sizes (`system-sections.json`). `--turn N` for resumed sessions |
| `templates/` | Baseline brief skeleton, policy section, self-review prompt, rubric, judge prompt |
