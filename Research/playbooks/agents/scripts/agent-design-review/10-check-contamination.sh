#!/usr/bin/env bash
# List commands in a round's logs that touch other rounds' branches or worktrees, or enumerate refs.
# Usage: 10-check-contamination.sh <out> <round> <other-round>...
# Each hit needs reading: "git branch --show-current" names the agent's own branch and is harmless.
set -u
out=$1; round=$2; shift 2
pat="--all|for-each-ref|worktree list|git branch( |$)"
for other in "$@"; do pat="$pat|(^|[[:space:]\x27\":=])$other/|worktrees/$other-"; done  # a branch "<round>/item", not a path like ~/.codex/
for log in "$out/$round"/logs/*.log; do
  hits=$(grep -E -- "-lc " "$log" | grep -E -- "$pat" | grep -v -- "--show-current")
  printf '%s: %s\n' "$(basename "$log" .log)" "$( [ -z "$hits" ] && echo clean || echo "$(echo "$hits" | wc -l) hit(s)")"
  [ -n "$hits" ] && echo "$hits" | cut -c1-220 | sed 's/^/    /'
done
