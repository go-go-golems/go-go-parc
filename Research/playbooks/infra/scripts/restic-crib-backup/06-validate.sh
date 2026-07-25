#!/usr/bin/env bash
# Validate the restic repository: structural check, 5% random data check, and
# an isolated restore with byte-for-byte comparison of representative files.
#
# Usage:
#   MACHINE=mimimi-2 SNAPSHOT=b9ba1402 VALIDATE_FILES="/path/to/photo /path/to/catalog" ./06-validate.sh
#   MACHINE=f SNAPSHOT=latest VALIDATE_FILES="/home/manuel/.ssh/id_restic_crib_f.pub" ./06-validate.sh
#
# Environment:
#   SNAPSHOT       Snapshot ID to validate and restore from (default: latest).
#   VALIDATE_FILES Space-separated list of file paths to restore and byte-compare.
#                  If unset, only the repository checks run (no restore test).
set -euo pipefail
source "$(dirname "$0")/00-restic-crib-env.sh"

SNAPSHOT="${SNAPSHOT:-latest}"
RESTORE_ROOT="${RESTORE_ROOT:-${TMPDIR:-/tmp}/restic-restore-validation}"

[[ -x "$RESTIC_BIN" ]] || { echo "restic not executable: $RESTIC_BIN" >&2; exit 1; }
[[ -f "$SSH_KEY" ]] || { echo "SSH key not found: $SSH_KEY" >&2; exit 1; }
[[ -s "$PASSWORD_FILE" ]] || { echo "Password file missing or empty: $PASSWORD_FILE" >&2; exit 1; }

export RESTIC_REPOSITORY="$REPOSITORY"
export RESTIC_PASSWORD_FILE="$PASSWORD_FILE"
RESTIC=("$RESTIC_BIN" -o "sftp.args=$RESTIC_SFTP_ARGS")

echo "=== Structural repository check ==="
"${RESTIC[@]}" check
echo ""

echo "=== 5% random data check ==="
"${RESTIC[@]}" check --read-data-subset=5%
echo ""

if [[ -z "${VALIDATE_FILES:-}" ]]; then
  echo "No VALIDATE_FILES set; skipping restore test."
  echo "To test a restore: VALIDATE_FILES='/path/to/file' $0"
  exit 0
fi

echo "=== Isolated restore and byte comparison ==="
mkdir -p "$RESTORE_ROOT"
TARGET="$(mktemp -d "$RESTORE_ROOT/restore.XXXXXX")"
printf 'Restore target: %s\n' "$TARGET"

# Build --include args for each file
INCLUDE_ARGS=()
for f in $VALIDATE_FILES; do
  INCLUDE_ARGS+=(--include "$f")
done

"${RESTIC[@]}" restore "$SNAPSHOT" --target "$TARGET" "${INCLUDE_ARGS[@]}"

# Byte-for-byte compare each file
all_ok=1
for f in $VALIDATE_FILES; do
  restored="$TARGET$f"
  if [[ ! -f "$restored" ]]; then
    echo "FAIL: restored file missing: $restored" >&2
    all_ok=0
    continue
  fi
  if cmp -s "$f" "$restored"; then
    echo "OK:   $f"
  else
    echo "FAIL: $f (byte mismatch)" >&2
    all_ok=0
  fi
done

if [[ "$all_ok" -eq 1 ]]; then
  echo ""
  echo "Restore validation passed: restored files byte-match their current sources."
  echo "Keep this isolated restore directory until manual review is complete: $TARGET"
else
  echo ""
  echo "Restore validation FAILED. Inspect: $TARGET" >&2
  exit 1
fi
