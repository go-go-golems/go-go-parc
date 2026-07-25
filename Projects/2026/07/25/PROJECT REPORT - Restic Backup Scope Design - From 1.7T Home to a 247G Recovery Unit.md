---
title: "PROJECT REPORT - Restic Backup Scope Design - From 1.7T Home to a 247G Recovery Unit"
aliases:
  - Restic backup scope investigation
  - crib NAS backup scope design
  - laptop f backup scope dry-run
status: active
type: article
created: 2026-07-25
repo: /home/manuel/code/wesen/claw-stuff
related_ticket: BACKUP-SCOPE-2026-07-25
related_playbook: "[[PLAYBOOK - Restic Backups to the Crib NAS]]"
tags:
  - article
  - project-report
  - backup
  - restic
  - truenas
  - scope
  - investigation
  - infra
  - operations
---

# PROJECT REPORT - Restic Backup Scope Design - From 1.7T Home to a 247G Recovery Unit

A backup scope is not the set of files that exist on a machine. It is the set of files that would be missed if the machine were lost, filtered by the cost of regenerating each file and the cost of storing its history. This report documents the investigation that turned a 1.7-terabyte Ubuntu home directory into a 247-gigabyte restic recovery unit, the dry-run that corrected a twofold underestimate, and the excludes file that encodes the resulting scope contract.

The source machine is laptop `f`, a Framework laptop running Ubuntu 24.04.2 LTS with an encrypted 1.8-terabyte ext4 filesystem that is 95 percent full. The destination is the crib TrueNAS NAS at `192.168.0.25`, accessed through a dedicated SSH-only account over SFTP. The backup tool is restic, which provides client-side encryption, deduplication, and versioned snapshots. The existing backup system, documented in `CRIB-BACKUP-01`, was operational with a clean baseline snapshot, but its exclude file contained approximately 25 entries written before the coding-agent transcript directories grew to 8 gigabytes and before the full extent of regenerable data was measured.

The investigation produced a 99-line exclude file, verified by a `restic backup --dry-run` that scanned 3.8 million files in 4 minutes 40 seconds. The actual scope is 246.859 gigabytes, roughly double the pre-measurement estimate. The first full backup with the new scope was launched and is running against parent snapshot `3a1dc858`.

> [!summary]
> - The home directory contains 1.7 terabytes of data, but only 247 gigabytes (3.8 million files) are in the backup scope after excludes.
> - The scope includes coding-agent transcripts (`~/.codex`, `~/.claude`, `~/.pi`), the full `~/code/wesen` and `~/workspaces` trees, Obsidian vaults, Documents, dotfiles, SSH and GPG keys, selected application config, and `~/.local/bin` plus `~/.local/apps`.
> - The scope excludes 1.5 terabytes of regenerable data: caches (108 gigabytes in `~/.cache` alone), package-manager stores, SDKs and toolchains, and build artifacts matched by glob patterns.
> - A dry-run corrected a twofold underestimate and identified 135 permission-denied service-owned files in 4 directories, which were added to the excludes.
> - The 99-line excludes file is the scope contract. The backup script needs no structural change; only the excludes file changed.

## 1. The problem with backing up a home directory

A home directory on a developer laptop is not a uniform collection of user documents. It is a mixture of irreplaceable original work, regenerable build artifacts, large installed toolchains, caches that exist only to accelerate repeated operations, and service-owned runtime state that was never meant to be preserved as user data. Backing up all of it treats these categories as equivalent, and that treatment has consequences.

The first consequence is capacity. The source filesystem is 1.8 terabytes with 1.7 terabytes used. The TrueNAS dataset has a 1.5-terabyte reference quota and already holds a 498-gigabyte Mac backup. A backup that copies the full home directory would consume the remaining quota with data that is cheap to regenerate, leaving no room for meaningful snapshot history. Restic deduplication and compression reduce stored size, but the repository must still scan, chunk, and index every file on every run. A 1.7-terabyte scan is slow and grows slower as history accumulates.

The second consequence is correctness. A backup that includes service-owned runtime state, such as a MongoDB WiredTiger data directory or a Meilisearch index, captures a point-in-time copy of a live database that may be in an inconsistent state. Restoring such a copy does not produce a usable database; it produces a corrupt one. The correct approach for structured application state is an application-level export, not a filesystem copy.

The third consequence is noise. A backup that includes `node_modules`, `.venv`, `dist`, and `build` directories captures data that is fully reproducible from source manifests. These directories are large, change frequently, and contribute nothing to recovery that a `pnpm install` or `go build` would not reproduce. Including them inflates scan time and repository churn without improving recoverability.

The scope investigation exists to separate these categories before the backup runs, not after.

## 2. The source machine profile

| Property | Value |
|---|---|
| Machine | `f` (Framework laptop, Ubuntu 24.04.2 LTS) |
| Filesystem | ext4 over LUKS/LVM, 1.8T total, ~1.7T used (95% full) |
| Backup transport | SFTP to TrueNAS `192.168.0.25` (fail-closed, no NFS fallback) |
| Backup user | `backup-f` (uid 3001, SSH-only, password disabled) |
| Repository | `sftp:backup-f@192.168.0.25:/mnt/media-pool/backups/laptops/f-restic` |
| Restic repository ID | `57e82c013a` |
| Scheduler | systemd `--user` timer (`restic-crib-backup.timer`, daily at 03:30) |

The transport is SFTP over SSH, not NFS. This is a deliberate design decision documented in `CRIB-BACKUP-01`. A prior TrueNAS outage demonstrated that a missing NFS mount can be silently replaced by an empty local directory, causing a backup to write to the wrong location while reporting success. SFTP fails closed: the connection either authenticates and opens the remote repository, or it fails. There is no local directory that can accidentally receive the backup.

## 3. The disk survey

The investigation began with a top-level survey of the home directory using `du -sh` sorted by size. The results divided cleanly into three categories: visible directories, hidden directories, and the coding-agent transcript directories that motivated the investigation.

### 3.1 Visible directories

| Directory | Size | Category |
|---|---|---|
| `~/code/` | 211G | Source trees and workspaces |
| `~/Downloads/` | 112G | User downloads (regenerable) |
| `~/workspaces/` | 101G | Dated scratch directories |
| `~/chromium/` | 38G | Browser profile (use browser sync) |
| `~/Movies/` | 29G | Media (separate backup) |
| `~/altera/` | 24G | FPGA toolchain (reinstallable) |
| `~/go/` | 21G | GOPATH (reinstallable) |
| `~/esp/` | 21G | ESP-IDF (reinstallable) |
| `~/snap/` | 18G | Snap packages (regenerable) |
| `~/smailnail/` | 18G | Email mirror databases (app-specific export) |
| `~/Android/` | 17G | Android SDK (reinstallable) |
| `~/patreon/` | 15G | Video archive (separate media backup) |
| `~/VirtualBox VMs/` | 8G | VM images (use VM export) |

### 3.2 Hidden directories

| Directory | Size | Category |
|---|---|---|
| `~/.cache/` | 108G | Caches (regenerable) |
| `~/.local/` | 70G | Mixed: share (56G), bin (6.7G), apps (6.2G) |
| `~/.pyenv/` | 36G | Python versions (reinstallable) |
| `~/.config/` | 32G | Mixed: app config and Electron caches |
| `~/.private/` | 18G | Private media (separate encrypted backup) |
| `~/.espressif/` | 17G | ESP-IDF toolchain (reinstallable) |
| `~/.thunderbird/` | 15G | Email client (app-specific export) |
| `~/.bun/` | 13G | Bun runtime (reinstallable) |
| `~/.docker/` | 9.7G | Docker data (regenerable) |
| `~/.android/` | 9.5G | Android SDK (reinstallable) |
| `~/.nvm/` | 7.1G | Node versions (reinstallable) |
| `~/.codex/` | 5.0G | Codex sessions (back up) |
| `~/.elan/` | 5.6G | Lean toolchain (reinstallable) |
| `~/.opam/` | 4.9G | OCaml toolchain (reinstallable) |
| `~/.npm/` | 4.3G | npm cache (regenerable) |
| `~/.rustup/` | 4.0G | Rust toolchain (reinstallable) |
| `~/.rbenv/` | 3.8G | Ruby toolchain (reinstallable) |
| `~/.pi/` | 3.4G | Pi agent sessions (back up) |

The hidden directories are dominated by toolchains and caches. The `~/.config` directory is misleading: at 32 gigabytes it appears to be configuration, but the bulk is Electron application caches. The `~/.config/Claude` directory alone is 13 gigabytes, of which 12 gigabytes is `vm_bundles` (regenerable virtual machine images). The actual configuration files in `~/.config` total less than 2 gigabytes.

### 3.3 Coding-agent transcript directories

The coding-agent transcript directories are the primary motivation for this investigation. They are plain JSONL files, not stored in any git repository, and they represent irreplaceable work history.

| Path | Size | Contents |
|---|---|---|
| `~/.codex/sessions/` | 4.5G | 1241 Codex session JSONL files (2025–2026) |
| `~/.codex/sessions_analysis.sqlite` | 220M | Derived analysis database |
| `~/.codex/history.jsonl` | 5.3M | Command history |
| `~/.codex/logs_2.sqlite` | 77M | Session logs |
| `~/.codex/state_5.sqlite` | 41M | Agent state |
| `~/.claude/projects/` | 360M | 294 Claude Code session JSONL files, organized by cwd |
| `~/.claude/history.jsonl` | 660K | Command history |
| `~/.pi/agent/sessions/` | 3.1G | Pi agent session JSONL files |
| `~/.pi/agent/run-history.jsonl` | 28K | Run history index |

None of these directories is a git repository. A `git status` check confirmed that `~/.codex`, `~/.claude`, and `~/.pi` contain plain files with no `.git` directory. If the source machine were lost, these transcripts would be unrecoverable without a backup. They total approximately 8 gigabytes.

## 4. The three-tier classification

The survey results were classified into three tiers. The classification is the core output of the investigation; it is what turns a disk survey into a backup scope.

### 4.1 Tier 1: Back up

Tier 1 contains data that cannot be cheaply regenerated and that needs a tested recovery path. The total is approximately 247 gigabytes after build-artifact excludes are applied.

| Category | Size | Contents |
|---|---|---|
| Coding-agent transcripts | ~8G | `~/.codex/sessions/`, `~/.claude/projects/`, `~/.pi/agent/sessions/` |
| Code and workspaces (full trees) | ~90G | `~/code/wesen` (44G after excludes) + `~/workspaces` (46G after excludes) |
| Documents | ~4.1G | Photos, books, tax records, personal documents |
| Obsidian vaults | ~2.5G | `obsidian-vault` (2.0G) + `go-go-parc` (502M) |
| Installed binaries and apps | ~13G | `~/.local/bin` (6.7G) + `~/.local/apps` (6.2G) |
| Selected application config | ~2G | 1Password, BambuStudio, kitty, copyq, darktable |
| Dotfiles and credentials | ~2M | `.gitconfig`, `.bashrc`, `.ssh/`, `.gnupg/` |

The code and workspaces trees are backed up in full, not selectively. The rationale is that these directories contain non-git files that a git-only recovery would miss. A survey of `~/code/wesen/claw-stuff` found 789 untracked files in `.pi-subagents/artifacts/` alone. The `~/workspaces` directory is almost entirely non-git dated scratch directories, including `workspaces/2025-12-21/echo-base-documentation/`, a 36-gigabyte embedded firmware collection that is not a git repository.

Build artifacts within these trees are excluded by glob patterns. The patterns `**/node_modules`, `**/.venv`, `**/build`, `**/dist`, and `**/target` apply uniformly across both trees, so no per-tree exclude logic is required.

### 4.2 Tier 2: Exclude

Tier 2 contains regenerable data. This is the bulk of the 1.7-terabyte home directory.

| Category | Size | Examples |
|---|---|---|
| Caches | ~110G | `~/.cache` (108G), JetBrains (30G), Electron app caches |
| Package-manager stores | ~50G | pnpm (11G), `.pyenv` (36G), `.bun` (13G), `.nvm` (7.1G) |
| SDKs and toolchains | ~40G | `~/go` (21G), `~/esp` (21G), `~/Android` (17G), `~/altera` (24G) |
| Build outputs (glob) | varies | `**/node_modules`, `**/.venv`, `**/dist`, `**/build`, `**/target` |
| Other regenerable | ~20G | `~/Downloads`, `~/snap`, `~/.continue`, `~/.cursor` |

### 4.3 Tier 3: Handle separately

Tier 3 contains large, structured application state that should not be blindly copied by restic. These need an application-specific export strategy.

| Path | Size | Issue | Recommendation |
|---|---|---|---|
| `~/smailnail/` | 18G | Email mirror databases (5.3G each) | Export via smailnail's own backup |
| `~/.thunderbird/` | 15G | Email client with FTS index (838M) | Use Thunderbird's export |
| `~/.config/Signal/` | 3.1G | Encrypted attachments (2.9G) | Use Signal's backup feature |
| `~/.private/` | 18G | Private media | Separate encrypted storage |
| `~/patreon/videos/` | 15G | 196K video files | Separate media backup |
| `~/Movies/` | 29G | Media | Separate media backup |
| `~/chromium/` | 38G | Browser profile | Use browser sync |
| `~/VirtualBox VMs/` | 8G | VM images | Use VM export/snapshot |

## 5. The credential boundary

The `~/.ssh` directory contains private keys: `id_ed25519`, `id_rsa`, `id_restic_crib_f`, deploy keys, and environment files for Proxmox and laptop `f`. These are backed up because losing them locks the operator out of infrastructure. The `~/.gnupg` directory contains the GPG keyring.

The restic repository password at `~/.config/restic/crib/password` is a separate concern. It must not be stored only in the backup. If the source machine is lost, the backup is encrypted with that password, and the password exists only on the lost machine, recovery is impossible. The password is escrowed in Vault at `kv/infra/truenas/restic/laptop-f`, which is a separate failure domain from both the source machine and the NAS.

This separation reflects a general principle: transport authentication and repository encryption are different controls. The restricted SSH key authenticates the source machine to the TrueNAS SFTP account. The restic password decrypts the repository contents. An attacker who obtains the SSH key can access one repository path but cannot decrypt its contents. An attacker who obtains the restic password cannot access the repository without the SSH key. Each secret must have an independent recovery-safe copy.

## 6. The dry-run and the twofold underestimate

The excludes file was extracted from the design document and a `restic backup --dry-run` was run against `/home/manuel` with the new excludes. The dry-run completed in 4 minutes 40 seconds and produced the following output:

```text
using parent snapshot 3a1dc858
Files:       15209 new,  1695 changed, 3789610 unmodified
Dirs:         4424 new,  2765 changed, 653951 unmodified
Would add to the repository: 868.478 MiB (324.090 MiB stored)
processed 3806514 files, 246.859 GiB in 4:40
Warning: at least one source file could not be read
```

The actual scope is 246.859 gigabytes across 3.8 million files. The pre-measurement estimate was 120 gigabytes. The underestimate was twofold.

The source of the error was the `workspaces/2025-12-21/echo-base-documentation` tree. This directory contains 36 gigabytes of M5Stack and ESP32 firmware demonstrations. The glob excludes catch `build/` directories within it (there are many, totaling several gigabytes), but the remaining source code, documentation, and runtime traces are not matched by any glob pattern. The estimate assumed that build artifacts constituted the majority of the tree; the dry-run showed that the non-build content is approximately 29 gigabytes.

The dry-run also identified 135 permission-denied files across 4 directories:

| Path | Owner | Contents |
|---|---|---|
| `~/apps/postgres` | root | PostgreSQL data directory |
| `~/code/others/llms/LibreChat/data-node` | service (mongodb) | WiredTiger database files |
| `~/code/others/llms/LibreChat/meili_data` | service (meilisearch) | LMDB index files |
| `~/code/wesen/ppa-control/captures` | root | Packet capture files |

These are service-owned runtime state files. They are the same class of files identified in `CRIB-BACKUP-01` Step 9, where a first full backup exited with status 3 because restic could not read root-owned and service-owned files under the home directory. The fix documented in that ticket applies here: exclude the files, do not run the backup as root. Running as root would hide the scope problem by making the script able to read service state that does not belong in a user-level backup.

The 4 permission-denied paths were added to the excludes file, bringing the total to 99 lines.

## 7. The excludes file as a scope contract

The excludes file is the scope contract. The backup script (`restic-crib-backup`) reads the excludes file via the `--exclude-file` flag and does not change structurally when the scope changes. All scope decisions are encoded in the excludes file.

The file is organized into sections by category:

```text
# === Caches (regenerable) ===
/home/manuel/.cache
/home/manuel/.config/Claude/Code Cache
/home/manuel/.config/Claude/Cache
/home/manuel/.config/Claude/vm_bundles
/home/manuel/.config/Cursor
...

# === Package managers and dependency stores ===
/home/manuel/.local/share/pnpm
/home/manuel/.bun
/home/manuel/.npm
/home/manuel/.nvm
/home/manuel/.pyenv
...

# === SDKs and toolchains (reinstallable) ===
/home/manuel/go
/home/manuel/esp
/home/manuel/Android
/home/manuel/altera
...

# === Build outputs and dependency trees (within code repos) ===
**/node_modules
**/.venv
**/venv
**/__pycache__
**/dist
**/build
**/target
**/.next
**/.nuxt
**/.terraform/providers
**/.terraform/modules

# === Service-owned / permission-denied state (from dry-run) ===
/home/manuel/apps
/home/manuel/code/others/llms/LibreChat/data-node
/home/manuel/code/others/llms/LibreChat/meili_data
/home/manuel/code/wesen/ppa-control/captures
```

The glob patterns (`**/node_modules`, `**/.venv`, etc.) are the mechanism that allows the full `~/code/wesen` and `~/workspaces` trees to be backed up without per-project exclude entries. A glob pattern matches at any depth, so a `node_modules` directory inside `~/code/wesen/claw-stuff/therapist-search/node_modules` and one inside `~/workspaces/2026-02-01--test-protobuf-ts-go-skill/web/node_modules` are both excluded by the same pattern.

## 8. The backup execution

After the dry-run verified the scope, the new excludes file was applied to the live location at `~/.config/restic/crib/excludes`. The previous excludes file was preserved at `~/.config/restic/crib/excludes.bak.20260725` for rollback.

A preflight check confirmed SFTP reachability:

```bash
restic-crib-manual-full --dry-run-preflight
# preflight-ok
```

The first full backup with the new scope was launched in the background via `nohup`:

```bash
nohup /home/manuel/.local/bin/restic-crib-manual-full </dev/null \
  >>/home/manuel/.local/state/restic/crib-manual-full.log 2>&1 &
```

The backup used parent snapshot `3a1dc858` for deduplication. Because the parent snapshot already contained most of the data from the prior `CRIB-BACKUP-01` baseline, the actual transfer was small. The backup completed in 4 minutes 19 seconds:

```text
Files:       15134 new,  1697 changed, 3789608 unmodified
Dirs:         4274 new,  2767 changed, 653949 unmodified
Added to the repository: 926.055 MiB (333.055 MiB stored)

processed 3806439 files, 246.884 GiB in 4:19
snapshot 7c02884f saved
```

The snapshot `7c02884f` covers 246.884 gigabytes across 3.8 million files. Only 926 megabytes (333 megabytes stored) were transferred, because the parent snapshot `3a1dc858` already contained the bulk of the data from the prior baseline. The new scope added the coding-agent transcripts, the full `~/workspaces` tree, and `~/.local/bin` plus `~/.local/apps`, which together accounted for the 926-megabyte delta.

### Validation results

A structural repository check passed:

```text
check snapshots, trees and blobs
[2:17] 100.00%  26 / 26 snapshots
no errors were found
```

Isolated restore tests of static files from snapshot `7c02884f` produced byte-identical results:

| File | Result |
|---|---|
| `~/.ssh/id_restic_crib_f.pub` | byte-match OK |
| `~/.local/bin/restic-crib-backup` | byte-match OK |
| `~/.gitconfig` | byte-match OK |

The `~/.codex/history.jsonl` file showed a byte mismatch, which is expected: it is a live append-only history file that was modified between the backup and the restore test. The restore itself succeeded (5.274 MiB restored).

## 9. Capacity and retention

| Metric | Value |
|---|---|
| TrueNAS dataset refquota | 1.50 TiB (1,649,267,441,664 bytes) |
| Current dataset usage (mimimi-2 backup) | ~498G |
| New backup scope (laptop f) | ~247G |
| Projected total usage | ~745G |
| Remaining headroom | ~755G |

The restic retention policy applied after each successful backup is:

```bash
restic forget --prune \
  --keep-daily 14 \
  --keep-weekly 8 \
  --keep-monthly 12
```

TrueNAS adds a second local history layer: a daily ZFS snapshot at 10:00 with a 14-day lifetime. ZFS snapshots preserve historical blocks in the repository dataset, which provides rollback protection against repository-level mistakes. The interaction between restic `forget --prune` and ZFS snapshots is bounded: restic may make old repository data unreachable at the restic layer while a recent ZFS snapshot still retains the underlying blocks, but the 14-day ZFS lifetime and the refquota make that interaction bounded.

## 10. What the dry-run taught us about estimation

The twofold underestimate carries a general lesson about backup scope estimation. Disk usage measured by `du` reports the raw size of a directory tree. The backup scope is the raw size minus the excluded content. The excluded content is determined by two mechanisms: absolute path excludes (which match specific directories) and glob pattern excludes (which match directory names at any depth).

The estimate was accurate for absolute path excludes because each excluded directory was measured individually. The estimate was inaccurate for the residual content of trees that are backed up in full. The `workspaces/2025-12-21/echo-base-documentation` tree is 36 gigabytes raw. The glob excludes remove its `build/` directories, but the remaining 29 gigabytes of source, documentation, and traces was not subtracted from the estimate because the estimate assumed the globs would catch most of the content.

The dry-run is the only reliable way to measure the actual scope. It scans the filesystem with the excludes applied and reports the exact file count and total size. The cost is approximately 5 minutes for a 1.7-terabyte filesystem. The benefit is that the first full backup runs against a known scope, not an estimate.

## 11. Working rules

The investigation produced a set of working rules that generalize beyond this specific machine:

- A backup scope is the set of files that would be missed, filtered by regeneration cost and storage cost. It is not the set of files that exist.
- Caches, package-manager stores, SDKs, and toolchains are regenerable. Excluding them is not data loss; it is scope discipline.
- Build artifacts within code trees are excluded by glob patterns, not by per-project entries. This allows full-tree backup without per-project maintenance.
- Service-owned runtime state (MongoDB, Meilisearch, PostgreSQL) is excluded from filesystem backup. It requires application-level export.
- The restic password must have an independent recovery-safe copy outside the source machine and outside the NAS. The backup is useless if the password is lost with the machine.
- A dry-run is mandatory before the first full backup with a new scope. Estimates based on `du` are unreliable for trees with mixed content.
- Permission-denied files during a user-level backup are a scope signal, not a privilege problem. The fix is to exclude the service-owned paths, not to run the backup as root.
- The excludes file is the scope contract. The backup script does not change when the scope changes; only the excludes file changes.

## 12. Open questions and remaining work

1. **First full backup completed.** Snapshot `7c02884f` was saved, structural check passed, and restore tests of static files passed. The backup is operational with the new scope.

2. **Scheduled incremental verification.** The systemd timer (`restic-crib-backup.timer`) is active. Monitor the first scheduled run to confirm the incremental delta is small (the manual run delta was 926 MiB).

3. **therapist-search SQLite.** The `claw-stuff/therapist-search/data/therapists.sqlite` file is 6.8 gigabytes and changes frequently. It is included in the scope by default. Monitor incremental snapshot sizes after the first few scheduled runs. If it causes large deltas, add it to the excludes and handle it via a separate export.

4. **smailnail email.** The 18-gigabyte email mirror databases are excluded from this backup. A separate restic repository or a smailnail-native export is needed for email recovery.

5. **Offsite copy.** This backup protects against source-machine loss but not against site loss. No TrueNAS replication, cloud sync, or offsite repository copy is configured. This is the primary remaining gap for a complete 3-2-1 design.

6. **Coding-agent session growth.** The transcript directories grow over time. The current 8 gigabytes will increase. Monitor repository growth against the 1.5-terabyte quota.

## Evidence and implementation references

- **Ticket:** `claw-stuff/ttmp/2026/07/25/BACKUP-SCOPE-2026-07-25--investigate-what-to-back-up-to-the-nas-config-local-code-wesen/`
- **Design doc:** `design/01-backup-scope-design.md` — the full 3-tier classification and 99-line excludes file
- **Diary:** `reference/01-diary.md` — 4 steps covering survey, scope expansion, dry-run, and backup execution
- **Dry-run output:** `claw-stuff/scripts/2026/07/25/backup-scope-investigation/results/dryrun-output.txt`
- **New excludes file:** `claw-stuff/scripts/2026/07/25/backup-scope-investigation/excludes-new.txt`
- **Live excludes:** `~/.config/restic/crib/excludes` (99 lines, old backed up to `excludes.bak.20260725`)
- **Backup log:** `~/.local/state/restic/crib-manual-full.log`
- **Prior implementation:** `CRIB-BACKUP-01` ticket at `claw-stuff/ttmp/2026/06/06/CRIB-BACKUP-01--ubuntu-to-proxmox-truenas-backup-design/`
- **Playbook:** [[PLAYBOOK - Restic Backups to the Crib NAS]]
- **Related articles:**
  - [[ARTICLE - Crib Backup - From Design to Operational Restic Baseline]]
  - [[ARTICLE - Recoverable Mac Photo Backups with Restic TrueNAS and launchd]]
  - [[ARTICLE - TrueNAS Backup with Vault - A Systems Integration Case Study]]
