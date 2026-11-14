#!/usr/bin/env bash
# After a build or coaching stage: hidden tests, final JSON, transcript export and go-minitrace conversion.
# usage: after.sh NN AGENT TAG STAGE
set -uo pipefail
N=$1; AG=$2; TAG=$3; ST=$4
HERE=$(cd "$(dirname "$0")" && pwd); VAL=$(cd "$HERE/.." && pwd)
OUT=~/pattern-validation/builds/$N/$TAG/$AG
EV="$OUT/events.jsonl"; [ "$ST" != build ] && EV="$OUT/events-$ST.jsonl"
python3 "$VAL/extract.py" "$EV" "$OUT/answer-$ST.json" >/dev/null 2>&1 || echo "no final json" > "$OUT/answer-$ST.err"
( cd "$OUT/work" && PYTHONPATH="$OUT/work" timeout 120 python3 "$HERE/hidden/$N/test_hidden.py" -v ) > "$OUT/hidden-$ST.txt" 2>&1
( cd "$OUT/work" && timeout 120 python3 -m unittest discover -s tests ) > "$OUT/own-tests-$ST.txt" 2>&1
if [ "$ST" != build ] && [ -f "$HERE/hidden/$N/test_hidden_$ST.py" ]; then
  ( cd "$OUT/work" && PYTHONPATH="$OUT/work" timeout 120 python3 "$HERE/hidden/$N/test_hidden_$ST.py" -v ) > "$OUT/hidden-$ST-extra.txt" 2>&1
fi
f=$(ls -t "$OUT"/session/*.jsonl 2>/dev/null | head -1 || true)
if [ -n "$f" ]; then
  pi --export "$f" "$OUT/transcript-$ST.html" >/dev/null 2>&1 || true
  rm -rf "$OUT/trace-$ST"; go-minitrace convert pi --source-session "$f" --output-dir "$OUT/trace-$ST" >/dev/null 2>&1 || true
fi
rm -rf "$OUT/snapshot-$ST"; rsync -a --exclude __pycache__ "$OUT/work/" "$OUT/snapshot-$ST/"
PREV=$(ls -d "$OUT"/snapshot-* 2>/dev/null | grep -v "snapshot-$ST$" | tail -1)
if [ -n "$PREV" ]; then diff -rq "$PREV" "$OUT/snapshot-$ST" > "$OUT/changes-$ST.txt" 2>&1; fi
mkdir -p "$VAL/builds"
{ echo "== $N $TAG $AG $ST"; tail -3 "$OUT/hidden-$ST.txt"; tail -3 "$OUT/hidden-$ST-extra.txt" 2>/dev/null; tail -3 "$OUT/own-tests-$ST.txt"; } > "$VAL/builds/$N-$AG-$TAG-$ST.txt"
cp "$OUT/answer-$ST.json" "$VAL/builds/$N-$AG-$TAG-$ST.json" 2>/dev/null || true
