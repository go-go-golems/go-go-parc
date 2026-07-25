#!/usr/bin/env bash
# Run a restic backup with retention and a sampled repository check.
# This is the recurring backup script invoked by the scheduler (systemd/launchd).
#
# Usage:
#   MACHINE=mimimi-2 SOURCES_FILE=~/photos.txt ./05-backup.sh
#   MACHINE=f ./05-backup.sh                          # backs up $HOME with excludes
#
# Environment:
#   SOURCES_FILE  Path to a file listing source paths (one per line) for a
#                 selected-source backup. If unset, backs up $HOME with excludes.
#   TAGS          Extra restic --tag values (space-separated), e.g. TAGS="lightroom photos"
set -euo pipefail
source "$(dirname "$0")/00-restic-crib-env.sh"

# macOS log/lock paths differ from Linux
if [[ "$OS_TYPE" == "Darwin" ]]; then
  LOG_DIR="${LOG_DIR:-$HOME/Library/Logs/restic}"
  LOCK_DIR="${LOCK_DIR:-$HOME/Library/Caches/restic/${MACHINE}-backup.lock}"
else
  LOG_DIR="${LOG_DIR:-$STATE_DIR}"
  LOCK_DIR="${LOCK_DIR:-$STATE_DIR}/${MACHINE}-backup.lock}"
fi
LOG_FILE="${LOG_FILE:-$LOG_DIR/${MACHINE}-backup.log}"

mkdir -p "$LOG_DIR" "$(dirname "$LOCK_DIR")"
exec > >(tee -a "$LOG_FILE") 2>&1

# Overlap protection: skip if a previous run is still alive
if [[ -d "$LOCK_DIR" ]]; then
  previous_pid="$(cat "$LOCK_DIR/pid" 2>/dev/null || true)"
  if [[ "$previous_pid" =~ ^[0-9]+$ ]] && kill -0 "$previous_pid" 2>/dev/null; then
    printf '[%s] Backup already running (pid %s); skipping overlapping run\n' \
      "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$previous_pid"
    exit 0
  fi
  rm -rf "$LOCK_DIR"
fi
mkdir "$LOCK_DIR"
printf '%s\n' "$$" > "$LOCK_DIR/pid"
trap 'rm -rf "$LOCK_DIR"' EXIT

printf '[%s] crib restic backup started (machine=%s)\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$MACHINE"

export RESTIC_REPOSITORY="$REPOSITORY"
export RESTIC_PASSWORD_FILE="$PASSWORD_FILE"
export RESTIC_CACHE_DIR="$CACHE_DIR"
RESTIC=("$RESTIC_BIN" -o "sftp.args=$RESTIC_SFTP_ARGS")

# --- Preflight (fail-closed: no NFS/local fallback) ---
command -v restic >/dev/null || { echo "restic not found" >&2; exit 1; }
[[ -r "$PASSWORD_FILE" ]] || { echo "password file unreadable" >&2; exit 1; }
ssh -i "$SSH_KEY" -o BatchMode=yes -o IdentitiesOnly=yes -o ConnectTimeout=10 \
  "${BACKUP_USER}@${TRUENAS_HOST}" "test -d ${BACKUP_HOME}"

# --- Build backup arguments ---
BACKUP_ARGS=("$RESTIC_BIN" -o "sftp.args=$RESTIC_SFTP_ARGS" backup)
BACKUP_ARGS+=(--tag "laptop-${MACHINE}")

if [[ -n "${SOURCES_FILE:-}" ]]; then
  # Selected-source backup (e.g. photos, Lightroom catalog)
  [[ -r "$SOURCES_FILE" ]] || { echo "SOURCES_FILE unreadable: $SOURCES_FILE" >&2; exit 1; }
  mapfile -t SOURCES < "$SOURCES_FILE"
  for source in "${SOURCES[@]}"; do
    [[ -e "$source" ]] || { echo "Configured source missing: $source" >&2; exit 1; }
  done
  BACKUP_ARGS+=("${SOURCES[@]}")
else
  # Whole-home backup with excludes
  [[ -r "$EXCLUDE_FILE" ]] || { echo "excludes file unreadable: $EXCLUDE_FILE" >&2; exit 1; }
  BACKUP_ARGS+=("$HOME" --one-file-system --exclude-file "$EXCLUDE_FILE")
fi

# Extra tags
for tag in ${TAGS:-}; do
  BACKUP_ARGS+=(--tag "$tag")
done

# --- Backup ---
"${BACKUP_ARGS[@]}"

# --- List snapshots ---
"${RESTIC[@]}" snapshots

# --- Retention (prune only after a successful backup) ---
"${RESTIC[@]}" forget --prune \
  --keep-daily "$KEEP_DAILY" \
  --keep-weekly "$KEEP_WEEKLY" \
  --keep-monthly "$KEEP_MONTHLY"

# --- Sampled repository check ---
"${RESTIC[@]}" check --read-data-subset=5%

printf '[%s] crib restic backup and retention completed\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')"
