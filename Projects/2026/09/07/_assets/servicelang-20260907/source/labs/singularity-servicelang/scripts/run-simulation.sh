#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
build=${1:-build}
mode=${2:-simulation}
case "$mode" in simulation|application) ;; *) echo "unknown host mode" >&2; exit 2;; esac
run=$(mktemp -d "$build/$mode-XXXXXX")
if [[ "$mode" == application ]]; then
  "$build/servicec" emit-app examples/sensor.svc examples/sensor.plan.json --out "$run/generated"
else
  "$build/servicec" emit-cpp examples/sensor.svc --out "$run/generated"
fi
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti -pthread \
  -I "$run/generated/artifacts" -I runtime \
  -I ../singularity-local/core/include -I ../singularity-rpc/core/include \
  "host/$mode.cpp" -o "$run/$mode"
"$run/$mode"
printf 'ARTIFACTS %s\n' "$run"
