#!/usr/bin/env bash
# Verify SFTP preflight, initialize the restic repository, and run a smoke
# backup/restore to prove the full path before a large backup.
#
# Usage:
#   MACHINE=mimimi-2 ./04-init-and-smoke-test.sh
#   MACHINE=f ./04-init-and-smoke-test.sh
set -euo pipefail
source "$(dirname "$0")/00-restic-crib-env.sh"

[[ -x "$RESTIC_BIN" ]] || { echo "restic not executable: $RESTIC_BIN" >&2; exit 1; }
[[ -f "$SSH_KEY" ]] || { echo "SSH key not found: $SSH_KEY" >&2; exit 1; }
[[ -s "$PASSWORD_FILE" ]] || { echo "Password file missing: $PASSWORD_FILE" >&2; exit 1; }

export RESTIC_REPOSITORY="$REPOSITORY"
export RESTIC_PASSWORD_FILE="$PASSWORD_FILE"
export RESTIC_CACHE_DIR="$CACHE_DIR"
RESTIC=("$RESTIC_BIN" -o "sftp.args=$RESTIC_SFTP_ARGS")

echo "=== SFTP preflight (fail-closed) ==="
ssh -i "$SSH_KEY" -o BatchMode=yes -o IdentitiesOnly=yes -o ConnectTimeout=10 \
  "${BACKUP_USER}@${TRUENAS_HOST}" "test -d ${BACKUP_HOME}"
echo "preflight-ok: ${BACKUP_USER}@${TRUENAS_HOST} can reach ${BACKUP_HOME}"
echo ""

echo "=== Initialize repository (if absent) ==="
if ! "${RESTIC[@]}" cat config >/dev/null 2>&1; then
  "${RESTIC[@]}" init
else
  echo "repository already initialized"
fi
echo ""

echo "=== Smoke backup ==="
SMOKE_DIR="$STATE_DIR/smoke-source"
SMOKE_RESTORE="$STATE_DIR/smoke-restore"
rm -rf "$SMOKE_DIR" "$SMOKE_RESTORE"
mkdir -p "$SMOKE_DIR"
printf 'crib restic smoke test %s\n' "$(date --iso-8601=seconds)" > "$SMOKE_DIR/hello.txt"
"${RESTIC[@]}" backup "$SMOKE_DIR" --tag "$MACHINE" --tag smoke-test
echo ""

echo "=== Snapshots ==="
"${RESTIC[@]}" snapshots --tag smoke-test
echo ""

echo "=== Restore and verify ==="
mkdir -p "$SMOKE_RESTORE"
"${RESTIC[@]}" restore latest --tag smoke-test --target "$SMOKE_RESTORE"
echo "restored file:"
find "$SMOKE_RESTORE" -type f -print -exec sed -n '1p' {} \;
echo ""

echo "Smoke test passed. Next: run the first full backup with 05-backup.sh"
