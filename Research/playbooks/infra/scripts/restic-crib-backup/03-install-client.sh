#!/usr/bin/env bash
# Install the restic client on the source machine: directory layout, env file,
# password file, excludes file, and (optional) Vault password escrow.
#
# Usage:
#   MACHINE=mimimi-2 ./03-install-client.sh
#   MACHINE=f ESCROW_VAULT=1 ./03-install-client.sh
#
# Environment:
#   ESCROW_VAULT=1   Escrow the restic password in Vault (Linux only).
#                    Requires VAULT_ADDR and vault login.
#   SOURCES_FILE     Path to a file listing source paths (one per line) for a
#                    selected-source backup. If unset, backs up $HOME with excludes.
set -euo pipefail
source "$(dirname "$0")/00-restic-crib-env.sh"

echo "Installing restic client for machine: $MACHINE"
echo ""

# 1. Create directory layout
mkdir -p -m 0700 "$(dirname "$PASSWORD_FILE")" "$HOME/.local/bin" "$STATE_DIR" "$CACHE_DIR" "$HOME/.ssh"

# 2. Generate the dedicated SSH key if absent
if [[ ! -f "$SSH_KEY" ]]; then
  ssh-keygen -q -t ed25519 -N "" -f "$SSH_KEY" -C "restic backup from ${MACHINE} to TrueNAS"
  echo "generated SSH key: $SSH_KEY"
fi
chmod 600 "$SSH_KEY"
chmod 644 "$SSH_KEY.pub"

# 3. Create the restic env file
cat > "$ENV_FILE" <<EOF
RESTIC_REPOSITORY=$REPOSITORY
RESTIC_PASSWORD_FILE=$PASSWORD_FILE
RESTIC_CACHE_DIR=$CACHE_DIR
RESTIC_EXCLUDE_FILE=$EXCLUDE_FILE
RESTIC_SFTP_ARGS="-i $SSH_KEY -o BatchMode=yes -o IdentitiesOnly=yes"
EOF
chmod 0600 "$ENV_FILE"
echo "wrote env file: $ENV_FILE"

# 4. Generate the restic repository password if absent
if [[ ! -s "$PASSWORD_FILE" ]]; then
  umask 077
  openssl rand -base64 48 > "$PASSWORD_FILE"
  chmod 0600 "$PASSWORD_FILE"
  echo "generated restic password file: $PASSWORD_FILE"
else
  echo "password file already exists: $PASSWORD_FILE"
fi

# 5. Create the excludes file (for whole-home backups; skip if SOURCES_FILE is set)
if [[ -z "${SOURCES_FILE:-}" && ! -f "$EXCLUDE_FILE" ]]; then
  cat > "$EXCLUDE_FILE" <<'EOF'
# Caches and regenerable data
**/.cache
**/.npm/_cacache
**/.pnpm-store
**/.yarn/cache
**/.bun/install/cache
**/.cargo/registry
**/.cargo/git
**/.rustup/toolchains
**/.gradle/caches
**/.m2/repository
**/.pyenv/cache
**/.local/share/Trash
# Dependency trees (reproducible from source manifests)
**/node_modules
**/.venv
**/venv
**/__pycache__
# Build outputs
**/dist
**/build
**/target
**/.next
**/.nuxt
**/.terraform/providers
**/.terraform/modules
# Browser caches
**/.config/chromium/Default/Cache
**/.config/google-chrome/*/Cache
# VMs and containers
**/VirtualBox VMs
**/.docker
EOF
  echo "wrote excludes file: $EXCLUDE_FILE"
fi

# 6. Optional: escrow the password in Vault (Linux)
if [[ "${ESCROW_VAULT:-0}" == "1" && "$OS_TYPE" == "Linux" ]]; then
  : "${VAULT_ADDR:?ESCROW_VAULT=1 requires VAULT_ADDR}"
  restic_pw="$(cat "$PASSWORD_FILE")"
  vault kv put "kv/infra/truenas/restic/laptop-${MACHINE}" \
    repository="$REPOSITORY" \
    password="${restic_pw}" \
    purpose="Restic repository password escrow for ${MACHINE}" \
    owner="$(whoami)" >/dev/null
  unset restic_pw
  echo "escrowed password in Vault at kv/infra/truenas/restic/laptop-${MACHINE}"
elif [[ "${ESCROW_VAULT:-0}" == "1" && "$OS_TYPE" == "Darwin" ]]; then
  echo "WARNING: ESCROW_VAULT=1 is Linux-only. Store the password in a password manager on macOS." >&2
fi

echo ""
echo "Client installed. Next:"
echo "  1. Copy the public key to TrueNAS:  $SSH_KEY.pub"
echo "  2. Run 01-provision-truenas.sh with this public key"
echo "  3. Run 04-init-and-smoke-test.sh"
echo ""
echo "Public key:"
cat "$SSH_KEY.pub"
