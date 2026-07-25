# Restic Backup to Crib NAS — Scripts

General-purpose, parameterized scripts for setting up an encrypted, deduplicated,
scheduled restic backup from a laptop to the crib TrueNAS NAS (`192.168.0.25`).

See the playbook: [[PLAYBOOK - Restic Backups to the Crib NAS]]

## Quick start

```bash
# 1. Set your machine identity (override the default "f")
export MACHINE=mimimi-2

# 2. Generate the SSH key and install the client
./03-install-client.sh

# 3. Provision the TrueNAS dataset and SSH-only account
./01-provision-truenas.sh ~/.ssh/id_restic_crib_mimimi2.pub

# 4. Apply quota and ZFS snapshot protection
./02-configure-truenas-protection.sh

# 5. Initialize the repository and run a smoke backup/restore
./04-init-and-smoke-test.sh

# 6. Run the first full backup (or use 05-backup.sh directly)
#    For a selected-source backup, create a sources file:
#    echo "$HOME/Dropbox/Photos" > ~/photos.txt
#    echo "$HOME/Pictures/Lightroom" >> ~/photos.txt
#    SOURCES_FILE=~/photos.txt ./05-backup.sh
./05-backup.sh

# 7. Validate the repository and test a restore
SNAPSHOT=latest VALIDATE_FILES="/path/to/representative/file" ./06-validate.sh

# 8. Install the scheduler
#    Linux:
./07-install-systemd-timer.sh
#    macOS (run with sudo):
sudo MACHINE=mimimi-2 ./08-install-launchdaemon.sh
```

## Scripts

| Script | Purpose |
|---|---|
| `00-restic-crib-env.sh` | Shared configuration (source this; override `MACHINE` etc.) |
| `01-provision-truenas.sh` | Create the TrueNAS dataset + SSH-only backup user (idempotent) |
| `02-configure-truenas-protection.sh` | Apply refquota + daily 14-day ZFS snapshot task |
| `03-install-client.sh` | Install restic client: dirs, env, password, excludes, SSH key |
| `04-init-and-smoke-test.sh` | SFTP preflight, `restic init`, smoke backup/restore |
| `05-backup.sh` | Recurring backup with retention + sampled check (overlap-protected) |
| `06-validate.sh` | Repository check + isolated restore with byte comparison |
| `07-install-systemd-timer.sh` | Install systemd `--user` timer (Linux) |
| `08-install-launchdaemon.sh` | Install system LaunchDaemon (macOS, run with sudo) |

## Configuration

All scripts source `00-restic-crib-env.sh`. Override any variable before sourcing:

```bash
MACHINE=mimimi-2 \
BACKUP_USER=backup-mimimi-2 \
REFQUOTA_BYTES=2199023255552 \
SCHEDULE_HOUR=2 SCHEDULE_MINUTE=30 \
source ./00-restic-crib-env.sh
```

Key variables:

| Variable | Default | Description |
|---|---|---|
| `MACHINE` | `f` | Short machine identifier |
| `BACKUP_USER` | `backup-${MACHINE}` | TrueNAS SSH-only account |
| `DATASET` | `media-pool/backups/laptops/${MACHINE}-restic` | TrueNAS ZFS dataset |
| `REFQUOTA_BYTES` | `1649267441664` (1.5 TiB) | Repository quota in bytes |
| `KEEP_DAILY/WEEKLY/MONTHLY` | `14/8/12` | Restic retention policy |
| `SCHEDULE_HOUR/MINUTE` | `1/15` | Daily schedule time |
| `SOURCES_FILE` | (unset) | File listing source paths for selected-source backups |

## Source implementations

These scripts generalize two production implementations:

- **Ubuntu laptop `f`** (June 2026): systemd `--user` timer, Vault-backed provisioning.
  Ticket: `claw-stuff/ttmp/2026/06/06/CRIB-BACKUP-01--ubuntu-to-proxmox-truenas-backup-design/`
- **macOS `mimimi-2`** (July 2026): LaunchDaemon, local password file.
  Ticket: `crib-k3s/ttmp/2026/07/11/CRIB-OPS-20260711--check-crib-runtime-and-establish-documented-backup-and-recovery-baseline/`
  Scripts (git commit `89ed55c`): `scripts/01-provision-mimimi-2-restic.sh` through `scripts/06-install-mimimi-2-restic-launchdaemon.sh`

## Security

- Never commit a restic password, TrueNAS API key, or SSH private key.
- The restic password must have a recovery-safe copy outside the source machine
  and outside the NAS (Vault on Linux, password manager on macOS).
- SFTP is the fail-closed transport. Do not add an NFS or local filesystem fallback.
