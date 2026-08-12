#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)
GO_ROOT=$(cd "$ROOT/../go" && pwd)
TLC=${TLC:-"$HOME/.local/bin/tlc"}
RESULTS="$ROOT/results"
mkdir -p "$RESULTS"

reject_trace() {
    local jsonl=$1 capacity=$2 module=$3 result=$4 description=$5
    ./generate_trace.py "$jsonl" --capacity "$capacity" --output "$module.tla"
    set +e
    "$TLC" -config GeneratedTrace.cfg "$module.tla" > "$RESULTS/$result.txt" 2>&1
    local status=$?
    set -e
    if [[ $status -eq 0 ]] || ! grep -q 'Error: Deadlock reached.' "$RESULTS/$result.txt"; then
        echo "$description was not rejected as expected (status=$status)" >&2
        exit 1
    fi
    printf '%s: TLC rejected (exit=%d, deadlock)\n' "$description" "$status"
}

(
    cd "$GO_ROOT"
    go run ./cmd/tracegen -output "$ROOT/sample-valid.jsonl" \
        -interval-output "$ROOT/sample-intervals.jsonl"
)

cd "$ROOT"
./generate_trace.py sample-valid.jsonl --capacity 2 --output GeneratedTrace.tla
"$TLC" -config GeneratedTrace.cfg GeneratedTrace.tla > "$RESULTS/valid.txt" 2>&1
grep -q 'Model checking completed. No error has been found.' "$RESULTS/valid.txt"
printf 'valid Go trace: TLC accepted\n'

python3 - <<'PY'
import json
from pathlib import Path
root = Path.cwd()
events = [json.loads(line) for line in (root / "sample-valid.jsonl").read_text().splitlines()]
other = []
for event in events:
    event = dict(event)
    event["run_id"] = "tracegen-run-2"
    event["dispatcher_id"] = "observer-2"
    other.append(event)
(root / "sample-mixed.jsonl").write_text("".join(
    json.dumps(event, separators=(",", ":")) + "\n" for event in events + other
))
PY
set +e
./generate_trace.py sample-mixed.jsonl --capacity 2 --output GeneratedAmbiguousTrace.tla \
    > "$RESULTS/partition-rejection.txt" 2>&1
partition_status=$?
set -e
if [[ $partition_status -eq 0 ]] || ! grep -q 'trace contains 2 partitions' "$RESULTS/partition-rejection.txt"; then
    echo "mixed trace was not rejected without an explicit partition" >&2
    exit 1
fi
./generate_trace.py sample-mixed.jsonl --capacity 2 --run-id tracegen-run-2 \
    --dispatcher-id observer-2 --output GeneratedSelectedTrace.tla
"$TLC" -config GeneratedTrace.cfg GeneratedSelectedTrace.tla > "$RESULTS/partition-selected.txt" 2>&1
grep -q 'Model checking completed. No error has been found.' "$RESULTS/partition-selected.txt"
printf 'mixed trace: rejected without partition; selected run/dispatcher accepted\n'

./project_partial.py sample-valid.jsonl sample-partial.jsonl
./generate_trace.py sample-partial.jsonl --capacity 2 --output GeneratedPartialTrace.tla
"$TLC" -config GeneratedTrace.cfg GeneratedPartialTrace.tla > "$RESULTS/partial.txt" 2>&1
grep -q 'Model checking completed. No error has been found.' "$RESULTS/partial.txt"
printf 'partial trace with hidden evidence/actions: TLC reconstructed and accepted\n'

./generate_interval_trace.py sample-valid.jsonl sample-intervals.jsonl --capacity 2 \
    --output GeneratedIntervalTrace.tla
set +e
"$TLC" -config GeneratedIntervalTrace.cfg GeneratedIntervalTrace.tla \
    > "$RESULTS/interval-valid.txt" 2>&1
interval_status=$?
set -e
if [[ $interval_status -eq 0 ]] || ! grep -q 'Invariant NoCompleteLinearization is violated' "$RESULTS/interval-valid.txt"; then
    echo "operation intervals produced no legal complete linearization (status=$interval_status)" >&2
    exit 1
fi
printf 'operation intervals: TLC found a legal complete linearization witness\n'

python3 - <<'PY'
import json
from pathlib import Path
root = Path.cwd()
model = [json.loads(line) for line in (root / "sample-valid.jsonl").read_text().splitlines()]
intervals = [json.loads(line) for line in (root / "sample-intervals.jsonl").read_text().splitlines()]
target = next(event for event in model if event["action"] == "submit_rejected")
target["action"] = "submit_accepted"
target_operation = target["operation_id"]
for event in intervals:
    if event["operation_id"] == target_operation and event["phase"] == "linearize":
        event["action"] = "submit_accepted"
(root / "sample-invalid-interval-model.jsonl").write_text("".join(
    json.dumps(event, separators=(",", ":")) + "\n" for event in model
))
(root / "sample-invalid-intervals.jsonl").write_text("".join(
    json.dumps(event, separators=(",", ":")) + "\n" for event in intervals
))
PY
./generate_interval_trace.py sample-invalid-interval-model.jsonl sample-invalid-intervals.jsonl \
    --capacity 2 --output GeneratedInvalidIntervalTrace.tla
"$TLC" -config GeneratedIntervalTrace.cfg GeneratedInvalidIntervalTrace.tla \
    > "$RESULTS/interval-invalid.txt" 2>&1
if ! grep -q 'Model checking completed. No error has been found.' "$RESULTS/interval-invalid.txt"; then
    echo "invalid operation intervals unexpectedly reached completion" >&2
    exit 1
fi
printf 'post-close acceptance intervals: TLC proved no complete linearization reachable\n'

reject_trace sample-invalid.jsonl 2 GeneratedInvalidTrace invalid \
    "post-close-accept mutation"
reject_trace sample-invalid-instrumentation.jsonl 1 GeneratedInvalidInstrumentationTrace invalid-instrumentation \
    "delayed-receive instrumentation mutation"
