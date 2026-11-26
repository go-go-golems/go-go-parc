#!/usr/bin/env bash
# Resume each agent of an earlier round with one follow-up prompt (for example an open-ended self-review).
# Usage: 02-resume-codex-round.sh <round> <from-round> <prompt-file> <item>...
#   Session ids come from $OUT/<from-round>/logs/<item>.log; each agent continues in its own worktree, so its branch
#   gets new commits. The from-round's heads.json keeps the earlier revisions, which 06-blind-pack.mjs uses.
#   "<ID>" in the prompt is replaced by the item. codex exec resume takes no -s/--add-dir, hence the -c overrides.
set -u
round=$1; from=$2; pfile=$3; shift 3
: "${REPO:?}" "${OUT:?}" "${MODEL:?}" "${EFFORT:?}"
L=$OUT/$round/logs; mkdir -p "$L"
# CODEX_EXTRA: further codex arguments, split on spaces, e.g. "-c sandbox_workspace_write.network_access=true"
read -ra EXTRA <<< "${CODEX_EXTRA:-}"
DEV=()
if [ -n "${DEV_INSTRUCTIONS_FILE:-}" ]; then
  # Codex prepends developer_instructions to its second developer message, ahead of AGENTS.md (a user message).
  # A JSON string is also a valid TOML basic string, which is what -c expects.
  DEV=(-c "developer_instructions=$(node -e 'process.stdout.write(JSON.stringify(require("fs").readFileSync(process.argv[1], "utf8")))' "$DEV_INSTRUCTIONS_FILE")")
fi
for item in "$@"; do
  sid=$(grep -m1 "session id:" "$OUT/$from/logs/$item.log" | awk '{print $3}')
  w=$(node -e 'console.log(require(process.argv[1])[process.argv[2]].worktree)' "$OUT/$from/heads.json" "$item")
  ( cd "$w" && timeout "${AGENT_TIMEOUT:-3600}" codex exec resume -m "$MODEL" -c model_reasoning_effort="$EFFORT" "${DEV[@]}" "${EXTRA[@]}" \
      -c sandbox_mode=\"workspace-write\" -c "sandbox_workspace_write.writable_roots=[\"$REPO/.git\"]" \
      -o "$L/$item.last-message.md" "$sid" "$(sed "s/<ID>/$item/g" "$pfile")" \
      > "$L/$item.log" 2>&1; echo "$item exit $?" >> "$L/exits.txt" ) &
done
wait
node -e '
const [out, round, from, ...items] = process.argv.slice(1);
const { execFileSync } = require("child_process");
const prev = require(`${out}/${from}/heads.json`), heads = {};
for (const item of items) {
  const w = prev[item].worktree;
  heads[item] = { ...prev[item], resumedFrom: from, base: prev[item].rev,
    rev: execFileSync("git", ["-C", w, "rev-parse", "--short", "HEAD"], { encoding: "utf8" }).trim() };
}
require("fs").writeFileSync(`${out}/${round}/heads.json`, JSON.stringify(heads, null, 1));
' "$OUT" "$round" "$from" "$@"
echo "round $round done; heads in $OUT/$round/heads.json"
