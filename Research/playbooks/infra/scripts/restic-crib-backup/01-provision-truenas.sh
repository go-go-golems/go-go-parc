#!/usr/bin/env bash
# Provision the isolated TrueNAS dataset and SSH-only account for a source machine.
# Run from an authorized operator workstation; requires admin@<TRUENAS_HOST> SSH access.
#
# Usage:
#   MACHINE=mimimi-2 ./01-provision-truenas.sh /path/to/id_restic_crib_mimimi2.pub
#   ./01-provision-truenas.sh                    # uses MACHINE=f by default
#
# This script is idempotent: it creates the dataset and user only if absent.
set -euo pipefail
source "$(dirname "$0")/00-restic-crib-env.sh"

PUBKEY_FILE="${1:?Usage: $0 /path/to/id_restic_crib_${MACHINE}.pub}"
[[ -r "$PUBKEY_FILE" ]] || { echo "Cannot read public key: $PUBKEY_FILE" >&2; exit 1; }
PUB_B64="$(base64 < "$PUBKEY_FILE" | tr -d '\n')"

echo "Provisioning TrueNAS for machine: $MACHINE"
echo "  dataset:     $DATASET"
echo "  backup user: $BACKUP_USER"
echo "  refquota:    $REFQUOTA_BYTES bytes ($(awk -v b="$REFQUOTA_BYTES" 'BEGIN{printf "%.2f TiB", b/1024/1024/1024/1024}'))"
echo ""

ssh -o BatchMode=yes -o ConnectTimeout=10 "${TRUENAS_ADMIN}@${TRUENAS_HOST}" \
  "PUB_B64='${PUB_B64}' DATASET='${DATASET}' BACKUP_USER='${BACKUP_USER}' BACKUP_HOME='${BACKUP_HOME}' bash -s" <<'REMOTE'
set -euo pipefail
PUBKEY="$(printf '%s' "$PUB_B64" | base64 -d)"

# Create the dataset if absent
if [[ "$(midclt call pool.dataset.query "[[\"id\",\"=\",\"$DATASET\"]]")" == "[]" ]]; then
  midclt call pool.dataset.create \
    "{\"name\":\"$DATASET\",\"type\":\"FILESYSTEM\",\"comments\":\"Encrypted restic repository for backup\",\"atime\":\"OFF\",\"compression\":\"LZ4\"}" \
    >/dev/null
  echo "created dataset: $DATASET"
else
  echo "dataset already exists: $DATASET"
fi

# Create the SSH-only backup user if absent
if [[ "$(midclt call user.query "[[\"username\",\"=\",\"$BACKUP_USER\"]]")" == "[]" ]]; then
  payload="$(jq -nc \
    --arg username "$BACKUP_USER" \
    --arg full_name "$BACKUP_USER restic SFTP backup user" \
    --arg home "$BACKUP_HOME" \
    --arg shell "/usr/bin/bash" \
    --arg sshpubkey "$PUBKEY" \
    '{username:$username,full_name:$full_name,group_create:true,home:$home,home_mode:"700",shell:$shell,password_disabled:true,ssh_password_enabled:false,smb:false,sshpubkey:$sshpubkey}')"
  midclt call user.create "$payload" >/dev/null
  echo "created SSH-only backup user: $BACKUP_USER"
else
  echo "backup user already exists: $BACKUP_USER"
fi

# Verify (non-secret fields only)
echo ""
echo "--- dataset ---"
midclt call pool.dataset.query "[[\"id\",\"=\",\"$DATASET\"]]" |
  jq -c '.[] | {id,mountpoint,atime,compression,used,available,comments}'
echo "--- user ---"
midclt call user.query "[[\"username\",\"=\",\"$BACKUP_USER\"]]" |
  jq -c '.[] | {username,uid,home,shell,password_disabled,ssh_password_enabled,smb,sshpubkey:(.sshpubkey != "")}'
REMOTE

echo ""
echo "Next: apply quota and ZFS snapshots with 02-configure-truenas-protection.sh"
