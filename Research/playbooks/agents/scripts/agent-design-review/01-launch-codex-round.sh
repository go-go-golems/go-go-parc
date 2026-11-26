#!/usr/bin/env bash
# Launch one fresh Codex agent per item, each in its own git worktree and branch, all in parallel.
# Usage: 01-launch-codex-round.sh <round> <prompt-dir> <item>...
#   The prompt is <prompt-dir>/common.md followed by <prompt-dir>/<item>.md; "<ID>" in either is replaced by the item.
#   Needs: REPO BASE OUT WORKTREES MODEL EFFORT (see 00-env.example.sh). Optional: DEV_INSTRUCTIONS_FILE, whose content
#   is passed as developer_instructions (a developer message, ranked above AGENTS.md).
# Writes: $OUT/<round>/logs/<item>.log, <item>.last-message.md, exits.txt, and $OUT/<round>/heads.json
#   ({item: {worktree, branch, base, rev}}) once every agent has exited. Commit the logs; they are the run's record.
set -u
round=$1; prompts=$2; shift 2
: "${REPO:?}" "${BASE:?}" "${OUT:?}" "${WORKTREES:?}" "${MODEL:?}" "${EFFORT:?}"
L=$OUT/$round/logs; mkdir -p "$L"
base=$(git -C "$REPO" rev-parse --short "$BASE")
# CODEX_EXTRA: further codex arguments, split on spaces, e.g. "-c sandbox_workspace_write.network_access=true"
read -ra EXTRA <<< "${CODEX_EXTRA:-}"
DEV=()
if [ -n "${DEV_INSTRUCTIONS_FILE:-}" ]; then
  # Codex prepends developer_instructions to its second developer message, ahead of AGENTS.md (a user message).
  # A JSON string is also a valid TOML basic string, which is what -c expects.
  DEV=(-c "developer_instructions=$(node -e 'process.stdout.write(JSON.stringify(require("fs").readFileSync(process.argv[1], "utf8")))' "$DEV_INSTRUCTIONS_FILE")")
fi
for item in "$@"; do
  w=$WORKTREES/$round-${item,,}; br=$round/${item,,}
  [ -d "$w" ] || git -C "$REPO" worktree add -q -b "$br" "$w" "$base"
  prompt="$(cat "$prompts/common.md" "$prompts/$item.md" | sed "s/<ID>/$item/g")"
  ( cd "$w" && timeout "${AGENT_TIMEOUT:-3600}" codex exec -m "$MODEL" -c model_reasoning_effort="$EFFORT" "${DEV[@]}" "${EXTRA[@]}" \
      -s workspace-write --add-dir "$REPO/.git" -o "$L/$item.last-message.md" "$prompt" \
      > "$L/$item.log" 2>&1; echo "$item exit $?" >> "$L/exits.txt" ) &
done
wait
node -e '
const [out, round, base, wt, ...items] = process.argv.slice(1);
const { execFileSync } = require("child_process");
const heads = {};
for (const item of items) {
  const w = `${wt}/${round}-${item.toLowerCase()}`;
  heads[item] = { worktree: w, branch: `${round}/${item.toLowerCase()}`, base,
    rev: execFileSync("git", ["-C", w, "rev-parse", "--short", "HEAD"], { encoding: "utf8" }).trim() };
}
require("fs").writeFileSync(`${out}/${round}/heads.json`, JSON.stringify(heads, null, 1));
' "$OUT" "$round" "$base" "$WORKTREES" "$@"
echo "round $round done: $(wc -l < "$L/exits.txt") agents; heads in $OUT/$round/heads.json"
