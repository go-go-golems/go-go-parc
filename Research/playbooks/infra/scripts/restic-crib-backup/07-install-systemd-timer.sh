#!/usr/bin/env bash
# Install a systemd --user timer and service for the recurring restic backup.
# Linux only. Run as the backup user on the source machine.
#
# Usage:
#   MACHINE=f ./07-install-systemd-timer.sh
set -euo pipefail
source "$(dirname "$0")/00-restic-crib-env.sh"

[[ "$OS_TYPE" == "Linux" ]] || { echo "This script is Linux-only. Use 08-install-launchdaemon.sh on macOS." >&2; exit 1; }

BACKUP_SCRIPT="$HOME/.local/bin/restic-${MACHINE}-backup"
SYSTEMD_DIR="$HOME/.config/systemd/user"
SERVICE_NAME="restic-${MACHINE}-backup"

# Install the backup script (copy 05-backup.sh to the user bin dir)
mkdir -p "$HOME/.local/bin" "$SYSTEMD_DIR"
cp "$(dirname "$0")/05-backup.sh" "$BACKUP_SCRIPT"
chmod +x "$BACKUP_SCRIPT"
echo "installed backup script: $BACKUP_SCRIPT"

# Create the systemd service
cat > "$SYSTEMD_DIR/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=Restic backup of ${MACHINE} to crib TrueNAS
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
ExecStart=${BACKUP_SCRIPT}
Nice=10
IOSchedulingClass=best-effort
IOSchedulingPriority=7
EOF
echo "wrote service: $SYSTEMD_DIR/${SERVICE_NAME}.service"

# Create the systemd timer
cat > "$SYSTEMD_DIR/${SERVICE_NAME}.timer" <<EOF
[Unit]
Description=Nightly restic backup of ${MACHINE} to crib TrueNAS

[Timer]
OnCalendar=*-*-* ${SCHEDULE_HOUR}:${SCHEDULE_MINUTE}:00
Persistent=true
RandomizedDelaySec=45m

[Install]
WantedBy=timers.target
EOF
echo "wrote timer: $SYSTEMD_DIR/${SERVICE_NAME}.timer"

# Reload and enable
systemctl --user daemon-reload
systemctl --user enable --now "${SERVICE_NAME}.timer"

echo ""
echo "Timer enabled. Verify with:"
echo "  systemctl --user list-timers ${SERVICE_NAME}.timer --no-pager"
echo "  systemctl --user list-timers ${SERVICE_NAME}.timer --no-pager"
echo ""
echo "If the laptop is often asleep at ${SCHEDULE_HOUR}:${SCHEDULE_MINUTE}, consider:"
echo "  loginctl enable-linger \$(whoami)"
