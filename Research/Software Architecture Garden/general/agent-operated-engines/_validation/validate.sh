#!/usr/bin/env bash
# One isolated pi run on one chapter version and one scenario (Research/playbooks/pi-coding-subagents-handbook.md).
# usage: validate.sh NN SCENARIO TAG [MODEL] [THINKING]
#   NN        chapter number (01..13)
#   SCENARIO  a, b, ... : tasks in scenarios/NN-SCENARIO.md (quiz, transfer, a not-fit control)
#   TAG       the chapter variant, e.g. v1; frozen as versions/NN-TAG.md on first use (never edited afterwards)
#   reads  versions/NN-TAG.md, ../00-overview.md (notation section), prompt-head.md, prompt-contract.md
#   writes ~/pattern-validation/agent-operated-engines/NN/TAG/SCENARIO/ (prompt.md, events.jsonl, transcript.html)
#          answers/NN-SCENARIO-TAG.json
# The agent gets no tools and no files; answer keys (keys/) are never in the prompt.
set -euo pipefail
unset CDPATH
N=$1; SC=$2; TAG=$3; MODEL=${4:-lunaroute/deepseek-4.1-flash}; THINK=${5:-high}
HERE=$(cd "$(dirname "$0")" && pwd); LANG_DIR=$(cd "$HERE/.." && pwd)
V="$HERE/versions/$N-$TAG.md"
if [ ! -f "$V" ]; then cp "$(ls "$LANG_DIR/$N-"*.md | head -1)" "$V"; fi
OUT=~/pattern-validation/agent-operated-engines/$N/$TAG/$SC; rm -rf "$OUT"; mkdir -p "$OUT"
{
  cat "$HERE/prompt-head.md"
  echo
  echo "=== NOTATION (from the language's overview) ==="
  awk '/^## Pseudocode conventions/ {on=1; next} on && /^## / {exit} on' "$LANG_DIR/00-overview.md"
  echo
  echo "=== THE CHAPTER ==="
  awk 'NR==1 && /^---$/ {fm=1; next} fm && /^---$/ {fm=0; next} !fm' "$V"
  echo
  echo "=== YOUR TASKS ==="
  cat "$HERE/scenarios/$N-$SC.md"
  echo
  cat "$HERE/prompt-contract.md"
} > "$OUT/prompt.md"
cd "$OUT"
pi -p --mode json --no-builtin-tools --no-context-files --no-skills --no-prompt-templates \
   --session-dir "$OUT/session" --model "$MODEL" --thinking "$THINK" \
   "$(cat "$OUT/prompt.md")" < /dev/null > "$OUT/events.jsonl" 2> "$OUT/stderr.log" || echo "pi exit $?" >> "$OUT/stderr.log"
f=$(ls -t "$OUT"/session/*.jsonl 2>/dev/null | head -1 || true)
if [ -n "$f" ]; then pi --export "$f" "$OUT/transcript.html" >/dev/null 2>&1 || true; fi
python3 "$HERE/extract.py" "$OUT/events.jsonl" "$HERE/answers/$N-$SC-$TAG.json"
