#!/usr/bin/env bash
# Runs every Alloy command as its own JVM in parallel; aggregates results.
set -u
JAR="$HOME/Downloads/org.alloytools.alloy.dist.jar"
cd "$(dirname "$0")"
CMDS="ExampleLifecycle QueueBound NoEnqueueAfterClose OfferedIsPrefix QueueIsSuffix DrainComplete WaitAfterExit ClosedSticky DropsMonotone"
run_one() {
  local file="$1" cmd="$2"
  timeout 1800 java -cp ".:$JAR" RunAlloy "$file" "$cmd" 2>/dev/null | grep -E "^(run|check)"
}
export JAR
export -f run_one 2>/dev/null || true
: > results/guarded.txt; : > results/unguarded.txt
for f in dispatcher_guarded dispatcher_unguarded; do
  out="results/${f#dispatcher_}.txt"
  printf '%s\n' $CMDS | xargs -P 6 -I{} bash -c 'run_one "$0" "$1" >> "$2"' "$f.als" {} "$out"
  sort -o "$out" "$out"
done
echo DONE
