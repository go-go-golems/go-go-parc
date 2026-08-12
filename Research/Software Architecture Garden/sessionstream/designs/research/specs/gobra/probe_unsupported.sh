#!/usr/bin/env bash
# Pin current Gobra v26.02 frontend limitations that block a complete proof of
# the production-shaped dispatcher shell. A future Gobra upgrade making either
# probe succeed intentionally fails this script so the feasibility decision is
# revisited rather than preserving stale assumptions.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)
GOBRA=${GOBRA:-"$HOME/.local/bin/gobra"}
RESULTS="$ROOT/results/unsupported.txt"
: > "$RESULTS"

expect_unsupported() {
    local source=$1 expected=$2
    set +e
    PATH="$HOME/.local/bin:$PATH" "$GOBRA" -i "$ROOT/probes/$source" >> "$RESULTS" 2>&1
    status=$?
    set -e
    if [[ $status -eq 0 ]] || ! grep -q "$expected" "$RESULTS"; then
        echo "$source no longer exhibits expected limitation; revisit shell proof" >&2
        exit 1
    fi
    echo "$source: confirmed unsupported"
}

expect_unsupported SelectDefault.gobra 'scala.NotImplementedError'
expect_unsupported Recover.gobra 'unknown identifier recover'
