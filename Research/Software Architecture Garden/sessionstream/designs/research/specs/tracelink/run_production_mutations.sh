#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)
TLC=${TLC:-"$HOME/.local/bin/tlc"}
HARVEST=${HARVEST:-"$ROOT/results/production/gomaxprocs-2"}
RESULTS="$ROOT/results/production-mutations"
rm -rf "$RESULTS"
mkdir -p "$RESULTS"

"$ROOT/mutate_production.py" "$HARVEST" "$RESULTS"

# Broken operation identity must be rejected structurally before TLC.
set +e
"$ROOT/generate_interval_trace.py" "$RESULTS/bad-operation-model.jsonl" \
    "$RESULTS/bad-operation-intervals.jsonl" --capacity 1024 \
    --output "$RESULTS/BadOperationTrace.tla" > "$RESULTS/bad-operation.txt" 2>&1
status=$?
set -e
[[ $status -ne 0 ]] && grep -q 'missing operation interval' "$RESULTS/bad-operation.txt"
echo 'bad operation identity: rejected structurally'

check_no_witness() {
    local name=$1
    "$ROOT/generate_interval_trace.py" "$RESULTS/$name-model.jsonl" \
        "$RESULTS/$name-intervals.jsonl" --capacity 1024 \
        --output "$RESULTS/${name//-/}Trace.tla"
    cp "$ROOT/DispatcherTraceValidator.tla" "$ROOT/DispatcherIntervalValidator.tla" \
        "$ROOT/GeneratedIntervalTrace.cfg" "$RESULTS/"
    (
        cd "$RESULTS"
        "$TLC" -workers auto -config GeneratedIntervalTrace.cfg "${name//-/}Trace.tla" \
            > "$name.txt" 2>&1
    )
    grep -q 'Model checking completed. No error has been found.' "$RESULTS/$name.txt"
    ! grep -q 'Invariant NoCompleteLinearization is violated' "$RESULTS/$name.txt"
    echo "$name: no legal complete linearization"
}

check_no_witness bad-update
check_no_witness bad-boundary
