#!/usr/bin/env bash
# Blind design review of all builds of one task (chapter runs and controls), in the spirit of Alexander, Gabriel and
# Fowler (RUBRIC.md; playbook "pattern-extraction-with-agent-validation", section 6).
# usage: review.sh NN REV [MODEL] [THINKING]
#   collects ~/pattern-validation/builds/NN/*/*/snapshot-build (code and tests; no diaries, notes, chapter or answers),
#   shuffles them into impl-A, impl-B, ... (seeded by REV; the key is kept outside the reviewer's directory), and runs
#   one pi reviewer with read-only tools in ~/pattern-validation/reviews/NN/REV/work.
set -euo pipefail
unset CDPATH
N=$1; REV=$2; MODEL=${3:-lunaroute/deepseek-4.1-flash}; THINK=${4:-high}
HERE=$(cd "$(dirname "$0")" && pwd); VAL=$(cd "$HERE/../.." && pwd)
BUILDS=~/pattern-validation/builds/$N
"$HERE/prepare.sh" "$N" "$REV"
OUT=~/pattern-validation/reviews/$N/$REV; mkdir -p "$OUT/session"
cat > "$OUT/prompt.md" <<'PROMPT'
You are a senior software designer doing a design review. Your working directory contains RUBRIC.md (what to do and
the output format), TASK.md, CHAPTER.md, NEXT.md and several implementation directories (impl-A, impl-B, ...).
Read RUBRIC.md first and follow it exactly. Read every implementation's code and tests before judging. Work only
inside this directory; do not modify anything. Your final message must follow the output format in RUBRIC.md.
PROMPT
cd "$OUT/work"
pi -p --mode json --tools read,ls,find,grep --no-context-files --no-skills --no-prompt-templates \
   --session-dir "$OUT/session" --model "$MODEL" --thinking "$THINK" \
   "$(cat "$OUT/prompt.md")" < /dev/null > "$OUT/events.jsonl" 2> "$OUT/stderr.log" || echo "pi exit $?" >> "$OUT/stderr.log"
python3 "$VAL/extract.py" "$OUT/events.jsonl" "$OUT/answer.json" >/dev/null 2>&1 || echo "no final json" > "$OUT/answer.err"
mkdir -p "$VAL/reviews"
cp "$OUT/answer.json" "$VAL/reviews/$N-$REV.json" 2>/dev/null || true
f=$(ls -t "$OUT"/session/*.jsonl 2>/dev/null | head -1 || true)
if [ -n "$f" ]; then
  rm -rf "$OUT/trace"; go-minitrace convert pi --source-session "$f" --output-dir "$OUT/trace" >/dev/null 2>&1 || true
fi
echo "== review $N $REV: $( [ -f "$OUT/answer.json" ] && echo ok || echo 'no answer')"
