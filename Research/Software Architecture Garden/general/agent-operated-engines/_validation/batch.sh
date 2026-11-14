#!/usr/bin/env bash
# Run every scenario of one chapter version in parallel; skip those with an answer (re-running retries failures).
# usage: batch.sh NN TAG [PARALLEL] [MODEL] [THINKING]
set -euo pipefail
N=$1; TAG=$2; PAR=${3:-4}; MODEL=${4:-lunaroute/deepseek-4.1-flash}; THINK=${5:-high}
HERE=$(cd "$(dirname "$0")" && pwd); LOG="$HERE/batch.log"
for s in "$HERE"/scenarios/"$N"-*.md; do
  sc=$(basename "$s" .md); sc=${sc#"$N"-}
  if [ -f "$HERE/answers/$N-$sc-$TAG.json" ]; then continue; fi
  printf '%s\0' "$sc"
done | xargs -0 -n 1 -P "$PAR" sh -c 'echo "$(date +%T) start '"$N"' $0 '"$TAG"'" >> "'"$LOG"'"; "'"$HERE"'/validate.sh" '"$N"' "$0" '"$TAG"' '"$MODEL"' '"$THINK"' >/dev/null 2>&1; echo "$(date +%T) end '"$N"' $0 '"$TAG"' exit $?" >> "'"$LOG"'"'
python3 "$HERE/score.py" "$N" "$TAG"
