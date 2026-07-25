#!/usr/bin/env bash
# Shared configuration for restic-to-crib-NAS backup scripts.
# Source this from the other scripts:  source ./00-restic-crib-env.sh
#
# Override any variable before sourcing to customize for a new machine:
#   MACHINE=mimimi-2 BACKUP_USER=backup-mimimi-2 source ./00-restic-crib-env.sh
#
# This file is NOT a restic env file. It defines shell variables used by the
# provisioning, backup, and scheduler scripts. The restic runtime env file is
# generated separately at ~/.config/restic/<MACHINE>/env by 02-install-client.sh.

set -euo pipefail

# --- Machine identity (override per source machine) ---
MACHINE="${MACHINE:-f}"                       # short machine identifier, e.g. f, mimimi-2
BACKUP_USER="${BACKUP_USER:-backup-${MACHINE}}"
DATASET="${DATASET:-media-pool/backups/laptops/${MACHINE}-restic}"
BACKUP_HOME="${BACKUP_HOME:-/mnt/${DATASET}}"

# --- TrueNAS target ---
TRUENAS_HOST="${TRUENAS_HOST:-192.168.0.25}"
TRUENAS_ADMIN="${TRUENAS_ADMIN:-admin}"

# --- Source machine paths ---
# Linux: $HOME/.config/restic/<MACHINE>/... ; macOS: same layout.
RESTIC_BIN="${RESTIC_BIN:-$HOME/.local/bin/restic}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_restic_crib_${MACHINE}}"
PASSWORD_FILE="${PASSWORD_FILE:-$HOME/.config/restic/${MACHINE}/password}"
ENV_FILE="${ENV_FILE:-$HOME/.config/restic/${MACHINE}/env}"
EXCLUDE_FILE="${EXCLUDE_FILE:-$HOME/.config/restic/${MACHINE}/excludes}"
CACHE_DIR="${CACHE_DIR:-$HOME/.cache/restic}"
STATE_DIR="${STATE_DIR:-$HOME/.local/state/restic}"

# --- Repository ---
REPOSITORY="${REPOSITORY:-sftp:${BACKUP_USER}@${TRUENAS_HOST}:${BACKUP_HOME}}"

# --- Capacity (TrueNAS middleware requires a byte integer) ---
# 1.5 TiB = 1649267441664 bytes. Adjust to your source size + history headroom.
REFQUOTA_BYTES="${REFQUOTA_BYTES:-1649267441664}"

# --- Retention ---
KEEP_DAILY="${KEEP_DAILY:-14}"
KEEP_WEEKLY="${KEEP_WEEKLY:-8}"
KEEP_MONTHLY="${KEEP_MONTHLY:-12}"

# --- ZFS snapshot protection ---
SNAPSHOT_SCHEMA="${SNAPSHOT_SCHEMA:-restic-${MACHINE}-%Y-%m-%d_%H-%M}"

# --- Schedule ---
# Linux systemd timer: OnCalendar=*-*-* 03:30:00
# macOS LaunchDaemon: Hour=1 Minute=15
SCHEDULE_HOUR="${SCHEDULE_HOUR:-1}"
SCHEDULE_MINUTE="${SCHEDULE_MINUTE:-15}"

# --- restic SFTP args (the critical option; see playbook section 7) ---
RESTIC_SFTP_ARGS="${RESTIC_SFTP_ARGS:--i ${SSH_KEY} -o BatchMode=yes -o IdentitiesOnly=yes}"

# --- Detect OS for scheduler selection ---
OS_TYPE="$(uname -s)"
export MACHINE BACKUP_USER DATASET BACKUP_HOME TRUENAS_HOST TRUENAS_ADMIN
export RESTIC_BIN SSH_KEY PASSWORD_FILE ENV_FILE EXCLUDE_FILE CACHE_DIR STATE_DIR
export REPOSITORY REFQUOTA_BYTES KEEP_DAILY KEEP_WEEKLY KEEP_MONTHLY
export SNAPSHOT_SCHEMA SCHEDULE_HOUR SCHEDULE_MINUTE RESTIC_SFTP_ARGS OS_TYPE
