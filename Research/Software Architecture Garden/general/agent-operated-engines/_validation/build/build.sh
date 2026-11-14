#!/usr/bin/env bash
# One pi agent builds real software from one chapter, in its own directory.
# usage: build.sh NN AGENT TAG [MODEL] [THINKING]
#   copies the chapter version (../versions/NN-TAG.md) as CHAPTER.md and tasks/NN-TASK.md as TASK.md into
#   ~/pattern-validation/builds/NN/TAG/AGENT/work, runs pi there with read, write, edit and bash only (no context
#   files, skills or prompt templates), then runs the hidden tests and converts the session with go-minitrace.
set -euo pipefail
unset CDPATH
N=$1; AG=$2; TAG=$3; MODEL=${4:-lunaroute/deepseek-4.1-flash}; THINK=${5:-high}
HERE=$(cd "$(dirname "$0")" && pwd); VAL=$(cd "$HERE/.." && pwd)
OUT=~/pattern-validation/builds/$N/$TAG/$AG; rm -rf "$OUT"; mkdir -p "$OUT/work" "$OUT/session"
awk 'NR==1 && /^---$/ {fm=1; next} fm && /^---$/ {fm=0; next} !fm' "$VAL/versions/$N-$TAG.md" > "$OUT/work/CHAPTER.md"
cp "$HERE/tasks/$N-TASK.md" "$OUT/work/TASK.md"
cat > "$OUT/prompt.md" <<PROMPT
You are a software engineer joining a project. Your working directory contains two files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface.
Read both completely first. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish. Your final message must follow the output format at the end of TASK.md.
PROMPT
cd "$OUT/work"
pi -p --mode json --tools read,write,edit,bash --no-context-files --no-skills --no-prompt-templates \
   --session-dir "$OUT/session" --model "$MODEL" --thinking "$THINK" \
   "$(cat "$OUT/prompt.md")" < /dev/null > "$OUT/events.jsonl" 2> "$OUT/stderr.log" || echo "pi exit $?" >> "$OUT/stderr.log"
"$HERE/after.sh" "$N" "$AG" "$TAG" build
