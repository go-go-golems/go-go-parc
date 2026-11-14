#!/usr/bin/env bash
# Resume an agent's build session with feedback (a hint) and let it continue in the same directory.
# usage: coach.sh NN AGENT TAG STAGE HINT_FILE [MODEL] [THINKING]
set -euo pipefail
unset CDPATH
N=$1; AG=$2; TAG=$3; ST=$4; HINT=$5; MODEL=${6:-lunaroute/deepseek-4.1-flash}; THINK=${7:-high}
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=~/pattern-validation/builds/$N/$TAG/$AG
f=$(ls -t "$OUT"/session/*.jsonl | head -1)
cp "$HINT" "$OUT/hint-$ST.md"
cd "$OUT/work"
pi -p --mode json --tools read,write,edit,bash --no-context-files --no-skills --no-prompt-templates \
   --session "$f" --session-dir "$OUT/session" --model "$MODEL" --thinking "$THINK" \
   "$(cat "$HINT"; printf '\n\nAdd a new step to DIARY.md for this request, in the format of DIARY-FORMAT.md.\n')" < /dev/null > "$OUT/events-$ST.jsonl" 2> "$OUT/stderr-$ST.log" || echo "pi exit $?" >> "$OUT/stderr-$ST.log"
"$HERE/after.sh" "$N" "$AG" "$TAG" "$ST"
