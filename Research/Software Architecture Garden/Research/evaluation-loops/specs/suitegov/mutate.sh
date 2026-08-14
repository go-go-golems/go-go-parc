#!/usr/bin/env bash
# Mutation-sensitivity harness for suitegov.
#
# Each mutation disables one governance mechanism in a scratch copy of the
# module and requires `go test` to FAIL there. A mutation that survives the
# test suite means the mechanism is not actually protected by a test, which
# is exactly the illusion this research family exists to prevent.
set -u

here="$(cd "$(dirname "$0")" && pwd)"
failures=0

run_mutation() {
  local name="$1" file="$2" old="$3" new="$4"
  local work
  work="$(mktemp -d)"
  cp -r "$here"/. "$work"/
  rm -rf "$work/results"
  python3 - "$work/$file" "$old" "$new" <<'PY'
import sys
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
source = open(path).read()
if old not in source:
    sys.exit("mutation target not found in " + path)
open(path, "w").write(source.replace(old, new, 1))
PY
  if [ $? -ne 0 ]; then
    echo "ERROR  $name: mutation target missing (stale script)"
    failures=$((failures + 1))
    rm -rf "$work"
    return
  fi
  if (cd "$work" && GOWORK=off go test ./... -count=1 >/dev/null 2>&1); then
    echo "SURVIVED  $name: tests passed with the mechanism disabled"
    failures=$((failures + 1))
  else
    echo "KILLED    $name"
  fi
  rm -rf "$work"
}

# M1: drop the reviewer!=author check → self-approval allowed.
run_mutation "M1-self-approval-bypass" "commit.go" \
  "if proposal.Author == request.Reviewer {" \
  "if false && (proposal.Author == request.Reviewer) {"

# M2: disable the refuse-overwrite mechanism entirely. The mechanism is
# implemented twice over (O_EXCL and mode 0444); an earlier version of this
# mutation removed only O_EXCL and SURVIVED, because the read-only mode still
# made the overwrite fail with EACCES for non-root users. A mutation must
# disable the mechanism, not one of its redundant layers.
run_mutation "M2-minted-set-overwrite" "commit.go" \
  "os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o444" \
  "os.O_CREATE|os.O_WRONLY, 0o644"

# M3: disable own-digest verification → tampered ledger records accepted.
run_mutation "M3-ledger-digest-skip" "ledger.go" \
  "if computed != record.Digest {" \
  "if false && (computed != record.Digest) {"

# M4: disable predecessor-link verification → deleted records accepted.
run_mutation "M4-ledger-chain-skip" "ledger.go" \
  "if record.PrevDigest != state.Head {" \
  "if false && (record.PrevDigest != state.Head) {"

# M5: disable sentinel detection → closed split loads as data (if it parsed).
run_mutation "M5-sentinel-ignore" "split.go" \
  "if probe.SchemaVersion != ClosedSentinelSchemaVersion {" \
  "if true || probe.SchemaVersion != ClosedSentinelSchemaVersion {"

# M6: BindRun stops comparing digests → any suite binds as reviewed.
run_mutation "M6-bind-run-skip" "lock.go" \
  "if entry.SemanticDigest != observed {" \
  "if false && (entry.SemanticDigest != observed) {"

if [ "$failures" -ne 0 ]; then
  echo "FAIL: $failures mutation(s) survived or errored"
  exit 1
fi
echo "PASS: all mutations killed"
