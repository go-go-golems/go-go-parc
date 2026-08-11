#!/usr/bin/env bash
# mutate.sh -- mutation experiments for the dispatcher verification harness.
#
# Each mutation breaks one contract clause in dispatcher.go. A verification
# harness is only trustworthy if it FAILS on these mutations (cf. the
# pre-fix sensitivity experiments in SESSIONSTREAM-005). Every mutation is
# applied to a scratch copy, tested, and restored; results go to results/.
#
# Mutation -> broken contract -> expected detector:
#   M1 remove closing guard    -> D7 (send after close)      -> panic / trace replay
#   M2 bypass panic recovery   -> D5 (panic kills worker)    -> process crash / Wait watchdog
#   M3 disable drop accounting -> D4 (Dropped diverges)      -> trace replay + fuzz oracle
#   M4 skip callback delivery  -> D8 (admitted not offered)  -> invoked == admitted checks
#   M5 remove close idempotence-> D6 (double close panics)   -> TestRepeatedCloseHarmless
set -u
cd "$(dirname "$0")"

SRC=dispatcher.go
BACKUP=dispatcher.go.mutbak
RESULTS=results/mutations.txt

cp "$SRC" "$BACKUP"
restore() { mv "$BACKUP" "$SRC"; }
trap restore EXIT

: > "$RESULTS"

run_mutation() {
  local name="$1" desc="$2" sedexpr="$3"
  cp "$BACKUP" "$SRC"
  sed -i "$sedexpr" "$SRC"
  {
    echo "================================================================"
    echo "MUTATION $name: $desc"
    echo "----------------------------------------------------------------"
    echo "--- go test -race -count=1 -timeout 90s ./..."
  } >> "$RESULTS"
  go test -race -count=1 -timeout 90s ./... >> "$RESULTS" 2>&1
  local test_status=$?
  {
    echo "--- exit status: $test_status (non-zero = harness caught the mutation)"
    echo ""
  } >> "$RESULTS"
  if [ "$test_status" -eq 0 ]; then
    echo "MUTATION $name NOT CAUGHT — harness is blind here" | tee -a "$RESULTS"
  else
    echo "MUTATION $name caught (exit $test_status)"
  fi
}

# M1: delete the closing guard in TrySubmit (the send may hit a closed channel).
run_mutation "M1" "remove closing guard (D7) — TLA/Alloy NoSendAfterClose counterpart" \
  '/MUTATION-POINT: closing-guard/,+4d'

# M2: bypass deliverSafe so a callback panic propagates and kills the worker.
run_mutation "M2" "bypass panic recovery (D5) — worker death" \
  's/d\.deliverSafe(item)/d.deliver(item)/'

# M3: stop incrementing the drop counter (trace replay + oracle compare Dropped).
run_mutation "M3" "disable drop accounting (D4)" \
  's/d\.dropped++/d.dropped += 0 \/\/ MUTATED/'

# M4: never invoke the callback (admitted items are never offered).
run_mutation "M4" "skip callback delivery (D8)" \
  's/d\.deliver(item)/_ = item \/\/ MUTATED: no delivery/'

# M5: delete the idempotence check in Close (second Close panics).
run_mutation "M5" "remove close idempotence (D6)" \
  '/MUTATION-POINT: close-idempotence/,+4d'

restore
trap - EXIT
echo "All mutations recorded in $RESULTS; original restored."
