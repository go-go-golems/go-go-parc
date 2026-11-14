#!/usr/bin/env bash
# Run several chapter versions' scenarios with one shared pool of parallel workers, skipping answered runs.
# usage: multi.sh PARALLEL "NN:TAG" "NN:TAG" ...
set -uo pipefail
PAR=$1; shift
HERE=$(cd "$(dirname "$0")" && pwd)
for spec in "$@"; do
  n=${spec%%:*}; tag=${spec##*:}
  for s in "$HERE"/scenarios/"$n"-*.md; do
    sc=$(basename "$s" .md); sc=${sc#"$n"-}
    [ -f "$HERE/answers/$n-$sc-$tag.json" ] && continue
    printf '%s %s %s\n' "$n" "$sc" "$tag"
  done
done | xargs -P "$PAR" -L 1 "$HERE/run1.sh"
for spec in "$@"; do python3 "$HERE/score.py" "${spec%%:*}" "${spec##*:}"; done
