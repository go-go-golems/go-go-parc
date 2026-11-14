#!/usr/bin/env bash
# Prepare a blind design review of all builds of one task (chapter runs and controls).
# usage: prepare.sh NN REV
#   collects ~/pattern-validation/builds/NN/*/*/snapshot-build (code and tests only: diaries, notes, the chapter and
#   answers removed), shuffles them into impl-A, impl-B, ... (seeded by NN and REV), and writes the reviewer's
#   directory ~/pattern-validation/reviews/NN/REV/work with CHAPTER.md, TASK.md, RUBRIC.md and NEXT.md.
#   The key (letter -> tag/agent/arm) goes only to _validation/reviews/NN-REV-key.json, away from the reviewer.
# The reviewer is then an Opus subagent (the user's choice) or review.sh's pi run; either writes REVIEW.json in work/.
set -euo pipefail
unset CDPATH
N=$1; REV=$2
HERE=$(cd "$(dirname "$0")" && pwd); VAL=$(cd "$HERE/../.." && pwd)
BUILDS=~/pattern-validation/builds/$N
OUT=~/pattern-validation/reviews/$N/$REV; rm -rf "$OUT"; mkdir -p "$OUT/work" "$VAL/reviews"
CH=$(ls -d "$BUILDS"/v*/*/work/CHAPTER.md 2>/dev/null | tail -1)
[ -n "$CH" ] || { echo "no chapter build for $N" >&2; exit 1; }
cp "$CH" "$OUT/work/CHAPTER.md"
cp "$HERE/../tasks/$N-TASK.md" "$OUT/work/TASK.md"
cp "$HERE/RUBRIC.md" "$OUT/work/RUBRIC.md"
cp "$HERE/NEXT-$N.md" "$OUT/work/NEXT.md"
python3 - "$BUILDS" "$OUT" "$REV" "$VAL/reviews/$N-$REV-key.json" <<'PY'
import json, pathlib, random, shutil, sys
builds, out, rev, keyf = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3], pathlib.Path(sys.argv[4])
runs = sorted(p for p in builds.glob("*/*/snapshot-build") if p.is_dir())
random.Random(f"{builds.name}-{rev}").shuffle(runs)
key = {}
for i, src in enumerate(runs):
    letter = chr(ord("A") + i)
    dst = out / "work" / f"impl-{letter}"
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "*.md"))
    tag, agent = src.parent.parent.name, src.parent.name
    key[letter] = {"tag": tag, "agent": agent, "arm": "control" if tag == "ctl" else "chapter"}
keyf.write_text(json.dumps(key, indent=2))
print(f"{len(runs)} implementations: " + " ".join(sorted(key)))
PY
