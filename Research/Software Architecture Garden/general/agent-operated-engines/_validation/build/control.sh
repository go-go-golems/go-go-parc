#!/usr/bin/env bash
# A control build: the same task as build.sh, without the chapter. Shows what the chapter adds over the model's own
# design sense (playbook "pattern-extraction-with-agent-validation", section 5).
# usage: control.sh NN AGENT [MODEL] [THINKING]     -> ~/pattern-validation/builds/NN/ctl/AGENT
# The task text loses its "Apply the pattern described in CHAPTER.md" sentence, and the output contract asks for the
# design and its trade-offs instead of a pattern mapping. Everything else (tools, isolation, diary, hidden tests,
# transcript, go-minitrace) is as in build.sh. Kept as a separate file: never edit a script while batches run it.
set -euo pipefail
unset CDPATH
N=$1; AG=$2; MODEL=${3:-lunaroute/deepseek-4.1-flash}; THINK=${4:-high}; TAG=ctl
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=~/pattern-validation/builds/$N/$TAG/$AG; rm -rf "$OUT"; mkdir -p "$OUT/work" "$OUT/session"
python3 - "$HERE/tasks/$N-TASK.md" "$OUT/work/TASK.md" <<'PY'
import re, sys
s = open(sys.argv[1]).read()
s, k = re.subn(r"\s*Apply\s+the\s+pattern\s+described\s+in\s+`CHAPTER\.md`;\s+this\s+is\s+(exactly\s+)?the\s+situation\s+it"
               r"\s+is\s+for\.", "", s)
if k != 1:
    sys.exit("could not remove the chapter sentence")
s, k = re.subn(r'  "pattern_mapping":.*?\n  "notes_applied":.*?\n',
               '  "design": {"<part of your design>": "what it is responsible for and why it exists"},\n'
               '  "tradeoffs": ["a design decision you made, the alternative, and why"],\n', s)
if k != 1:
    sys.exit("could not rewrite the output contract")
s = re.sub(r'  "chapter_feedback":.*?\n', '  "unclear": ["where the task left you to guess"]\n', s)
if "CHAPTER" in s:
    sys.exit("task still mentions CHAPTER.md")
open(sys.argv[2], "w").write(s)
PY
cp "$HERE/DIARY-FORMAT.md" "$OUT/work/DIARY-FORMAT.md"
cat > "$OUT/prompt.md" <<PROMPT
You are a software engineer joining a project. Your working directory contains two files:
- TASK.md: the software to build, with its required public interface;
- DIARY-FORMAT.md: how to keep your work diary.
Read both completely first. Keep DIARY.md as you go, one step per phase of work, in that format. Then design, build and test the software in this directory. Work only inside this
directory (do not read or write outside it). Use only the Python 3 standard library. Run your tests and fix what
fails before you finish, and make sure DIARY.md is complete. Your final message must follow the output format at the end of TASK.md.
PROMPT
cd "$OUT/work"
pi -p --mode json --tools read,write,edit,bash --no-context-files --no-skills --no-prompt-templates \
   --session-dir "$OUT/session" --model "$MODEL" --thinking "$THINK" \
   "$(cat "$OUT/prompt.md")" < /dev/null > "$OUT/events.jsonl" 2> "$OUT/stderr.log" || echo "pi exit $?" >> "$OUT/stderr.log"
"$HERE/after.sh" "$N" "$AG" "$TAG" build
