#!/usr/bin/env bash
# Resume each Pi agent of an earlier round with one follow-up prompt, in its own worktree (the Pi counterpart of
# 02-resume-codex-round.sh). Usage: 13-resume-pi-round.sh <round> <from-round> <prompt-file> <item>...
#   The session is $OUT/<from-round>/sessions/<item>/*.jsonl; Pi appends the new turn to it. "<ID>" in the prompt is
#   replaced by the item. Needs REPO OUT WORKTREES MODEL EFFORT; DEV_INSTRUCTIONS_FILE and PI_FLAGS as in 12-.
set -u
round=$1; from=$2; pf=$3; shift 3
: "${REPO:?}" "${OUT:?}" "${WORKTREES:?}" "${MODEL:?}" "${EFFORT:?}"
L=$OUT/$round/logs; mkdir -p "$L"
read -ra FLAGS <<< "${PI_FLAGS:---no-extensions --no-mcp}"
APP=(); [ -n "${DEV_INSTRUCTIONS_FILE:-}" ] && APP=(--append-system-prompt "$DEV_INSTRUCTIONS_FILE")
for item in "$@"; do
  w=$WORKTREES/$from-${item,,}; s=$(ls "$OUT/$from/sessions/$item"/*.jsonl | head -1)
  prompt="$(sed "s/<ID>/$item/g" "$pf")"
  ( cd "$w" && timeout "${AGENT_TIMEOUT:-3600}" pi -p "${FLAGS[@]}" --model "$MODEL" --thinking "$EFFORT" \
      --session "$s" "${APP[@]}" "$prompt" < /dev/null > "$L/$item.log" 2>&1
    echo "$item exit $?" >> "$L/exits.txt"; grep -v '^Warning: ' "$L/$item.log" > "$L/$item.last-message.md" ) &
done
wait
node -e '
const [out, round, from, wt, ...items] = process.argv.slice(1);
const { execFileSync } = require("child_process");
const heads = {};
for (const item of items) {
  const w = `${wt}/${from}-${item.toLowerCase()}`;
  heads[item] = { worktree: w, branch: `${from}/${item.toLowerCase()}`, harness: "pi", resumedFrom: from,
    rev: execFileSync("git", ["-C", w, "rev-parse", "--short", "HEAD"], { encoding: "utf8" }).trim() };
}
require("fs").writeFileSync(`${out}/${round}/heads.json`, JSON.stringify(heads, null, 1));
' "$OUT" "$round" "$from" "$WORKTREES" "$@"
echo "round $round done: $(wc -l < "$L/exits.txt") agents"
