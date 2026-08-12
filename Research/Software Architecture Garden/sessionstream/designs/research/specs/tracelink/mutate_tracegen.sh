#!/usr/bin/env bash
# Require each contract mutation to prevent successful trace generation.
set -u

ROOT=$(cd "$(dirname "$0")" && pwd)
GO_ROOT=$(cd "$ROOT/../go" && pwd)
SRC="$GO_ROOT/dispatcher.go"
BACKUP="$GO_ROOT/dispatcher.go.tracebak"
RESULTS="$ROOT/results/mutations.txt"

cp "$SRC" "$BACKUP"
restore() { mv "$BACKUP" "$SRC"; }
trap restore EXIT
: > "$RESULTS"

run_mutation() {
    local name=$1 description=$2 sed_expression=$3
    cp "$BACKUP" "$SRC"
    sed -i "$sed_expression" "$SRC"
    {
        echo "================================================================"
        echo "$name: $description"
    } >> "$RESULTS"
    (
        cd "$GO_ROOT"
        timeout 30s go run ./cmd/tracegen -output /tmp/"$name"-trace.jsonl
    ) >> "$RESULTS" 2>&1
    status=$?
    echo "exit status: $status (nonzero required)" >> "$RESULTS"
    if [[ $status -eq 0 ]]; then
        echo "$name NOT CAUGHT: mutation produced a trace" | tee -a "$RESULTS"
        restore
        trap - EXIT
        exit 1
    fi
    rm -f /tmp/"$name"-trace.jsonl
    echo "$name caught at executable trace boundary (exit $status)"
}

run_mutation M1 "remove post-close admission guard" \
    '/MUTATION-POINT: closing-guard/,+4d'
run_mutation M2 "bypass callback panic recovery" \
    's/d\.deliverSafe(operationID, item)/d.deliver(item)/'
run_mutation M3 "disable drop accounting" \
    's/d\.dropped++/d.dropped += 0 \/\/ MUTATED/'
run_mutation M4 "skip callback invocation" \
    's/d\.deliver(item)/_ = item \/\/ MUTATED: no delivery/'
run_mutation M5 "remove close idempotence guard" \
    '/MUTATION-POINT: close-idempotence/,+4d'

restore
trap - EXIT
echo "all tracegen mutations caught"
