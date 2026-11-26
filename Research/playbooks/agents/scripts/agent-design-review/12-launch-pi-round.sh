#!/usr/bin/env bash
# Launch one fresh Pi agent per item, each in its own git worktree and branch, all in parallel (the Pi counterpart of
# 01-launch-codex-round.sh, for comparing harnesses on the same model).
# Usage: 12-launch-pi-round.sh <round> <prompt-dir> <item>...
#   The prompt is <prompt-dir>/common.md followed by <prompt-dir>/<item>.md; "<ID>" is replaced by the item.
#   Needs: REPO BASE OUT WORKTREES MODEL EFFORT. MODEL is a Pi model id such as openai-codex/gpt-6.2-sol; EFFORT is a
#   Pi thinking level (low, medium, high, xhigh). Optional: DEV_INSTRUCTIONS_FILE, appended to Pi's system prompt
#   (--append-system-prompt; it lands in the system message's "addendum" section), and PI_FLAGS (default
#   "--no-extensions --no-mcp": the harness is then Pi's base prompt, its four tools and the skills catalogue).
#   Pi has no sandbox: the agent's commands run as the user. State isolation rules in the prompt and check with 10-.
# Writes: $OUT/<round>/logs/<item>.log (Pi's final text), <item>.last-message.md, exits.txt,
#   $OUT/<round>/sessions/<item>/*.jsonl (the session, including the system message), and heads.json.
set -u
round=$1; prompts=$2; shift 2
: "${REPO:?}" "${BASE:?}" "${OUT:?}" "${WORKTREES:?}" "${MODEL:?}" "${EFFORT:?}"
L=$OUT/$round/logs; mkdir -p "$L"
base=$(git -C "$REPO" rev-parse --short "$BASE")
read -ra FLAGS <<< "${PI_FLAGS:---no-extensions --no-mcp}"
APP=(); [ -n "${DEV_INSTRUCTIONS_FILE:-}" ] && APP=(--append-system-prompt "$DEV_INSTRUCTIONS_FILE")
for item in "$@"; do
  w=$WORKTREES/$round-${item,,}; br=$round/${item,,}; s=$OUT/$round/sessions/$item; mkdir -p "$s"
  [ -d "$w" ] || git -C "$REPO" worktree add -q -b "$br" "$w" "$base"
  prompt="$(cat "$prompts/common.md" "$prompts/$item.md" | sed "s/<ID>/$item/g")"
  ( cd "$w" && timeout "${AGENT_TIMEOUT:-3600}" pi -p "${FLAGS[@]}" --model "$MODEL" --thinking "$EFFORT" \
      --session-dir "$s" "${APP[@]}" "$prompt" < /dev/null > "$L/$item.log" 2>&1
    echo "$item exit $?" >> "$L/exits.txt"; grep -v '^Warning: ' "$L/$item.log" > "$L/$item.last-message.md" ) &
done
wait
node -e '
const [out, round, base, wt, ...items] = process.argv.slice(1);
const { execFileSync } = require("child_process");
const heads = {};
for (const item of items) {
  const w = `${wt}/${round}-${item.toLowerCase()}`;
  heads[item] = { worktree: w, branch: `${round}/${item.toLowerCase()}`, base, harness: "pi",
    rev: execFileSync("git", ["-C", w, "rev-parse", "--short", "HEAD"], { encoding: "utf8" }).trim() };
}
require("fs").writeFileSync(`${out}/${round}/heads.json`, JSON.stringify(heads, null, 1));
' "$OUT" "$round" "$base" "$WORKTREES" "$@"
echo "round $round done: $(wc -l < "$L/exits.txt") agents; heads in $OUT/$round/heads.json"
