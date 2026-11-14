#!/usr/bin/env bash
# Run the transcript queries on one agent's converted session(s). usage: analyze.sh NN AGENT TAG [STAGE]
set -uo pipefail
N=$1; AG=$2; TAG=$3; ST=${4:-build}
HERE=$(cd "$(dirname "$0")" && pwd); OUT=~/pattern-validation/builds/$N/$TAG/$AG
for q in "$HERE"/queries/*.sql; do
  echo "### $(basename "$q")"
  go-minitrace query run --archive-glob "$OUT/trace-$ST/active/*/*.minitrace.json" --sql-file "$q" --max-rows 400 --max-cell-chars 240 2>&1
done
