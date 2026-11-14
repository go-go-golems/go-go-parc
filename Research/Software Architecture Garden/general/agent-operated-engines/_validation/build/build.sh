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
V="$VAL/versions/$N-$TAG.md"
if [ ! -f "$V" ]; then cp "$(ls "$VAL/.."/"$N"-*.md | head -1)" "$V"; fi
awk 'NR==1 && /^---$/ {fm=1; next} fm && /^---$/ {fm=0; next} !fm' "$V" > "$OUT/work/CHAPTER.md"
if [ ! -s "$OUT/work/CHAPTER.md" ]; then echo "empty chapter for $N $TAG" >&2; exit 1; fi
cp "$HERE/tasks/$N-TASK.md" "$OUT/work/TASK.md"
cp "$HERE/DIARY-FORMAT.md" "$OUT/work/DIARY-FORMAT.md"
cat > "$OUT/prompt.md" <<PROMPT
You are a software engineer joining a project. Your working directory contains three files:
- CHAPTER.md: a chapter of a design-pattern book describing the pattern you must apply;
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read all three completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md.
PROMPT
cd "$OUT/work"
pi -p --mode json --tools read,write,edit,bash --no-context-files --no-skills --no-prompt-templates \
   --session-dir "$OUT/session" --model "$MODEL" --thinking "$THINK" \
   "$(cat "$OUT/prompt.md")" < /dev/null > "$OUT/events.jsonl" 2> "$OUT/stderr.log" || echo "pi exit $?" >> "$OUT/stderr.log"
"$HERE/after.sh" "$N" "$AG" "$TAG" build
