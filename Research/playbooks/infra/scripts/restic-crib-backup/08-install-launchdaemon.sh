#!/usr/bin/env bash
# Install a system LaunchDaemon that runs the restic backup as the current user.
# macOS only. Run with sudo on the source machine: sudo ./08-install-launchdaemon.sh
#
# Usage:
#   sudo MACHINE=mimimi-2 ./08-install-launchdaemon.sh
#
# A LaunchDaemon runs outside a GUI session while still executing the backup as
# the user. This avoids the logged-in-GUI requirement of a LaunchAgent.
set -euo pipefail
source "$(dirname "$0")/00-restic-crib-env.sh"

[[ "$OS_TYPE" == "Darwin" ]] || { echo "This script is macOS-only. Use 07-install-systemd-timer.sh on Linux." >&2; exit 1; }
[[ "${EUID}" -eq 0 ]] || { echo "Run with sudo as root." >&2; exit 1; }

BACKUP_USER="${SUDO_USER:-$(whoami)}"
HOME_DIR="$(eval echo "~$BACKUP_USER")"
USER_UID="$(id -u "$BACKUP_USER")"
LABEL="dev.crib.restic-${MACHINE}-daemon"
AGENT_LABEL="dev.crib.restic-${MACHINE}"
SCRIPT_PATH="$HOME_DIR/.local/bin/restic-${MACHINE}-backup"
PLIST="/Library/LaunchDaemons/$LABEL.plist"
LOG_DIR="$HOME_DIR/Library/Logs/restic"

# Install the backup script (copy 05-backup.sh to the user bin dir)
mkdir -p "$(dirname "$SCRIPT_PATH")" "$LOG_DIR"
cp "$(dirname "$0")/05-backup.sh" "$SCRIPT_PATH"
chown "$BACKUP_USER":staff "$SCRIPT_PATH"
chmod 700 "$SCRIPT_PATH"
echo "installed backup script: $SCRIPT_PATH"

# Verify prerequisites
[[ -x "$RESTIC_BIN" ]] || { echo "restic missing: $RESTIC_BIN" >&2; exit 1; }
[[ -r "$SSH_KEY" && -r "$PASSWORD_FILE" ]] || { echo "Backup credentials are unreadable" >&2; exit 1; }
if pgrep -f "restic-${MACHINE}-backup" >/dev/null; then
  echo "A backup is currently running; wait for it before migrating schedulers." >&2
  exit 1
fi

chown "$BACKUP_USER":staff "$LOG_DIR"

# Preflight repository access as the user (without starting a backup)
sudo -u "$BACKUP_USER" env \
  HOME="$HOME_DIR" \
  PATH="/usr/bin:/bin:/usr/sbin:/sbin" \
  RESTIC_REPOSITORY="$REPOSITORY" \
  RESTIC_PASSWORD_FILE="$PASSWORD_FILE" \
  "$RESTIC_BIN" -o "sftp.args=-i $SSH_KEY -o BatchMode=yes -o IdentitiesOnly=yes" snapshots >/dev/null
echo "preflight-ok"

# Write the LaunchDaemon plist
cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>UserName</key>
  <string>$BACKUP_USER</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$SCRIPT_PATH</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>HOME</key><string>$HOME_DIR</string>
    <key>PATH</key><string>/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>$SCHEDULE_HOUR</integer>
    <key>Minute</key><integer>$SCHEDULE_MINUTE</integer>
  </dict>
  <key>ProcessType</key>
  <string>Background</string>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/${MACHINE}-daemon.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/${MACHINE}-daemon.stderr.log</string>
</dict>
</plist>
PLIST

plutil -lint "$PLIST"
chown root:wheel "$PLIST"
chmod 644 "$PLIST"

# Bootstrap the daemon
launchctl bootout "system/$LABEL" 2>/dev/null || true
launchctl bootstrap system "$PLIST"
launchctl print "system/$LABEL" >/dev/null

# Unload any old GUI LaunchAgent to prevent duplicate schedules
launchctl bootout "gui/$USER_UID/$AGENT_LABEL" 2>/dev/null || true

echo ""
echo "Installed $LABEL: daily ${SCHEDULE_HOUR}:${SCHEDULE_MINUTE} system schedule running as $BACKUP_USER."
echo "The old GUI LaunchAgent (if any) has been unloaded."
echo ""
echo "To start a real backup now (expect a potentially long run):"
echo "  sudo launchctl kickstart -k system/$LABEL"
echo "Inspect status with:"
echo "  sudo launchctl print system/$LABEL"
