#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)
RESULTS="$ROOT/results"
mkdir -p "$RESULTS"

run_model() {
    local name=$1 guarded=$2 expected_errors=$3
    local work
    work=$(mktemp -d)
    trap 'rm -rf "$work"' RETURN
    cp "$ROOT/Dispatcher.pml" "$work/Dispatcher.pml"
    (
        cd "$work"
        spin -DGUARDED="$guarded" -a Dispatcher.pml
        gcc -O2 -o pan pan.c
        # pan may return zero even when it reports an assertion violation.
        # The parsed error count is therefore the authoritative verdict.
        ./pan -m100000 > "$RESULTS/$name.txt"
        errors=$(awk '/errors:/{for(i=1;i<=NF;i++) if($i=="errors:"){print $(i+1); exit}}' "$RESULTS/$name.txt")
        if [[ "$errors" != "$expected_errors" ]]; then
            echo "$name: got errors=$errors, want $expected_errors" >&2
            exit 1
        fi
        if [[ "$errors" != 0 ]]; then
            spin -DGUARDED="$guarded" -t -p -g -l Dispatcher.pml > "$RESULTS/$name-trail.txt"
        fi
    )
    rm -rf "$work"
    trap - RETURN
    echo "$name: expected errors=$expected_errors"
}

run_model guarded 1 0
run_model unguarded 0 1
