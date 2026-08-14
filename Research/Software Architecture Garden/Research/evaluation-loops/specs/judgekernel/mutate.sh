#!/usr/bin/env bash
# Mutation sensitivity for the judgekernel admission relation: each mutation
# deletes or weakens one admission rule in a copy of the module and requires
# the test suite to FAIL. A mutation that survives means the suite does not
# protect that rule.
set -u

here="$(cd "$(dirname "$0")" && pwd)"
failures=0
run_mutation() {
  local name="$1" file="$2" pattern="$3" replacement="$4"
  local work
  work="$(mktemp -d)"
  cp -r "$here"/*.go "$here"/go.mod "$work"/
  python3 - "$work/$file" "$pattern" "$replacement" <<'PY'
import re, sys
path, pattern, replacement = sys.argv[1], sys.argv[2], sys.argv[3]
source = open(path).read()
mutated, count = re.subn(pattern, replacement, source, count=1, flags=re.S)
if count != 1:
    print(f"MUTATION DID NOT APPLY: {pattern!r}", file=sys.stderr)
    sys.exit(2)
open(path, "w").write(mutated)
PY
  if [ $? -ne 0 ]; then
    echo "ERROR  $name: mutation pattern did not apply"
    failures=$((failures + 1))
    rm -rf "$work"
    return
  fi
  if (cd "$work" && GOWORK=off go test ./... -count=1 >/dev/null 2>&1); then
    echo "SURVIVED  $name (suite passed with the rule deleted)"
    failures=$((failures + 1))
  else
    echo "caught    $name"
  fi
  rm -rf "$work"
}

# M1: drop supported-without-evidence enforcement.
run_mutation "M1-supported-without-evidence" "admit.go" \
  '\*verdict\.Supported && len\(labels\) == 0' \
  'false'

# M2: accept citations outside the universe.
run_mutation "M2-unknown-evidence" "admit.go" \
  'if !universe\.Contains\(label\) \{' \
  'if false {'

# M3: skip the verdict-count check.
run_mutation "M3-count-mismatch" "admit.go" \
  'if len\(payload\.Verdicts\) != len\(statements\) \{' \
  'if false {'

# M4: let abstained cells contribute to the faithfulness mean.
run_mutation "M4-abstention-buys-faithfulness" "estimate.go" \
  'score\.Abstained \|\| score\.Status == StatusVacuousAbstention' \
  'false'

# M5: allow unlimited repairs.
run_mutation "M5-unbounded-repair" "repair.go" \
  'if b == nil \|\| b\.used \{\n\t\treturn false\n\t\}' \
  'if b == nil { return false }'

# M6: make faithfulness an asked-for constant instead of a computed ratio.
run_mutation "M6-faithfulness-not-computed" "estimate.go" \
  'return Score\{\n\t\tStatus:       status,\n\t\tFaithfulness: Fraction\{Numerator: supported, Denominator: len\(verdicts\)\},' \
  'return Score{\n\t\tStatus:       status,\n\t\tFaithfulness: Fraction{Numerator: len(verdicts), Denominator: max(1, len(verdicts))},'

if [ "$failures" -ne 0 ]; then
  echo "mutation run FAILED: $failures mutation(s) not caught"
  exit 1
fi
echo "all mutations caught"
