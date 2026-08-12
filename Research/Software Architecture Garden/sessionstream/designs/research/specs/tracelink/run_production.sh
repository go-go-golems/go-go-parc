#!/usr/bin/env bash
# Harvest and validate actual Sessionstream observer-dispatcher executions.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)
SESSIONSTREAM=${SESSIONSTREAM:-/home/manuel/code/wesen/go-go-golems/sessionstream}
TLC=${TLC:-"$HOME/.local/bin/tlc"}
RESULTS="$ROOT/results/production"
FAILURES="$ROOT/results/failures"
mkdir -p "$RESULTS" "$FAILURES"

fail_bundle() {
    local run_dir=$1 reason=$2
    local bundle="$FAILURES/$(basename "$run_dir")-$(date +%Y%m%dT%H%M%S)"
    mkdir -p "$bundle"
    cp -a "$run_dir"/. "$bundle"/ 2>/dev/null || true
    printf '%s\n' "$reason" > "$bundle/REASON.txt"
    echo "$reason; preserved artifacts in $bundle" >&2
    exit 1
}

for procs in 1 2 4; do
    run_dir="$RESULTS/gomaxprocs-$procs"
    rm -rf "$run_dir"
    mkdir -p "$run_dir"
    (
        cd "$SESSIONSTREAM"
        SESSIONSTREAM_OBSERVER_TRACE_DIR="$run_dir" GOMAXPROCS="$procs" \
            go test ./pkg/sessionstream/transport/ws \
            -run '^TestObserverTraceHarvestConcurrent$' -count=1 \
            -trace="$run_dir/runtime.trace" \
            > "$run_dir/go-test.txt" 2>&1
    ) || fail_bundle "$run_dir" "Go harvest failed for GOMAXPROCS=$procs"

    python3 - "$run_dir" <<'PY' || exit 1
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
for name in ("model", "intervals"):
    events = [json.loads(line) for line in (root / f"{name}.jsonl").read_text().splitlines()]
    assert events, f"empty {name} stream"
    assert [e["sequence"] for e in events] == list(range(1, len(events) + 1)), f"non-contiguous {name}"
    assert len({(e["run_id"], e["dispatcher_id"]) for e in events}) == 1, f"mixed {name} partition"
model = [json.loads(line) for line in (root / "model.jsonl").read_text().splitlines()]
actions = {e["action"] for e in model}
required = {"submit_accepted", "receive", "close_effective", "worker_exit", "wait_returned"}
assert required <= actions, f"missing required actions: {sorted(required-actions)}"
PY

    if ! go tool trace -d=parsed "$run_dir/runtime.trace" > "$run_dir/runtime-parsed.txt" 2>&1; then
        mv "$run_dir/runtime-parsed.txt" "$run_dir/runtime-parsed-attempt-1.txt"
        sleep 1
        go tool trace -d=parsed "$run_dir/runtime.trace" > "$run_dir/runtime-parsed.txt" 2>&1 \
            || fail_bundle "$run_dir" "runtime trace unreadable after retry for GOMAXPROCS=$procs"
    fi
    grep -q 'ws.observer_dispatcher' "$run_dir/runtime-parsed.txt" \
        || fail_bundle "$run_dir" "runtime task correlation missing for GOMAXPROCS=$procs"
    grep -q 'observer.linearize' "$run_dir/runtime-parsed.txt" \
        || fail_bundle "$run_dir" "runtime operation correlation missing for GOMAXPROCS=$procs"

    module="ProductionIntervalP${procs}"
    "$ROOT/generate_interval_trace.py" "$run_dir/model.jsonl" "$run_dir/intervals.jsonl" \
        --capacity 1024 --output "$run_dir/$module.tla" \
        || fail_bundle "$run_dir" "interval generation failed for GOMAXPROCS=$procs"
    cp "$ROOT/DispatcherTraceValidator.tla" "$ROOT/DispatcherIntervalValidator.tla" \
        "$ROOT/GeneratedIntervalTrace.cfg" "$run_dir/"
    (
        cd "$run_dir"
        set +e
        "$TLC" -workers auto -config GeneratedIntervalTrace.cfg "$module.tla" > tlc.txt 2>&1
        status=$?
        set -e
        [[ $status -ne 0 ]] && grep -q 'Invariant NoCompleteLinearization is violated' tlc.txt
    ) || fail_bundle "$run_dir" "TLC found no legal interval refinement for GOMAXPROCS=$procs"

    printf 'GOMAXPROCS=%d: harvested, runtime-correlated, TLC interval witness found\n' "$procs"
done
