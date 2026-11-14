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
OUT=~/pattern-validation/reviews/$N/$REV; rm -rf "$OUT"; mkdir -p "$OUT/work" "$OUT/session"
CH=$(ls -d "$BUILDS"/v*/*/work/CHAPTER.md 2>/dev/null | tail -1)
[ -n "$CH" ] || { echo "no chapter build for $N" >&2; exit 1; }
cp "$CH" "$OUT/work/CHAPTER.md"
cp "$HERE/../tasks/$N-TASK.md" "$OUT/work/TASK.md"
cp "$HERE/RUBRIC.md" "$OUT/work/RUBRIC.md"
cp "$HERE/NEXT-$N.md" "$OUT/work/NEXT.md"
python3 - "$BUILDS" "$OUT" "$REV" <<'PY'
import json, pathlib, random, shutil, sys
builds, out, rev = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
runs = sorted(p for p in builds.glob("*/*/snapshot-build") if p.is_dir())
random.Random(f"{builds.name}-{rev}").shuffle(runs)
key = {}
for i, src in enumerate(runs):
    letter = chr(ord("A") + i)
    dst = out / "work" / f"impl-{letter}"
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    for f in dst.glob("*.md"):          # diaries, notes, the chapter and the task: keep the review blind
        f.unlink()
    tag, agent = src.parent.parent.name, src.parent.name
    key[letter] = {"tag": tag, "agent": agent, "arm": "control" if tag == "ctl" else "chapter"}
(out / "key.json").write_text(json.dumps(key, indent=2))
print(" ".join(f"{k}={v['tag']}/{v['agent']}" for k, v in key.items()))
PY
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
cp "$OUT/key.json" "$VAL/reviews/$N-$REV-key.json"
f=$(ls -t "$OUT"/session/*.jsonl 2>/dev/null | head -1 || true)
if [ -n "$f" ]; then
  rm -rf "$OUT/trace"; go-minitrace convert pi --source-session "$f" --output-dir "$OUT/trace" >/dev/null 2>&1 || true
fi
echo "== review $N $REV: $( [ -f "$OUT/answer.json" ] && echo ok || echo 'no answer')"
