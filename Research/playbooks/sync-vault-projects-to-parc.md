---
title: "Playbook: Sync Obsidian Vault Projects to go-go-parc"
doc-type: playbooks
topics: parc, vault-sync, go-go-golems
owners: manuel
created: "2026-05-11"
---

# Playbook: Sync Obsidian Vault Projects to go-go-parc

Mirror project notes from the Obsidian vault into the go-go-parc library so that the PARC contains a complete, up-to-date copy of all project documentation produced by the go-go-golems team.

## Context

- **Vault** (source of truth): `/home/manuel/code/wesen/obsidian-vault/Projects/2026/`
- **PARC** (mirror): `/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/`
- **Scope**: `Projects/2026/` and all subdirectories (months 03, 04, 05, …). Pre-2026 project notes at the vault's `Projects/` root are out of scope.
- **Direction**: Vault → PARC only. Never edit PARC files directly and expect them to survive a re-sync.
- **File types**: `.md` files primarily. A small number of embedded images may need to be copied to `go-go-parc/Attachments/`.

## What you need

- `rsync` — for efficient incremental copy
- `diff` — for verifying content drift
- `find` — for counting and listing files

---

## Step 1: Dry run — see what would change

Before copying anything, preview the delta:

```bash
VAULT=/home/manuel/code/wesen/obsidian-vault/Projects/2026/
PARC=/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/

# Show only new files (not yet in PARC)
rsync -avn --ignore-existing \
  "$VAULT" "$PARC" \
  --include="*.md" --exclude="*"
```

This lists files that exist in the vault but not in the PARC. Review the list to confirm it looks reasonable (should be recent dates only).

## Step 2: Copy new files

Copy only files that don't yet exist in the PARC:

```bash
rsync -av --ignore-existing \
  "$VAULT" "$PARC" \
  --include="*.md" --exclude="*"
```

The `--ignore-existing` flag skips files that already exist at the destination, so this is safe to re-run without overwriting any PARC file that may have been manually edited.

## Step 3: Check for content drift in existing files

The vault is the source of truth. If a vault note was updated after the last sync, the PARC copy is stale. Find and fix drift:

```bash
# List .md files that differ between vault and PARC
diff -rq "$VAULT" "$PARC" --exclude="*.md" 2>/dev/null || true

# Actually, we want the opposite — compare only .md files:
for f in $(cd "$VAULT" && find . -name "*.md" -type f); do
  if [ -f "$PARC/$f" ]; then
    if ! diff -q "$VAULT/$f" "$PARC/$f" >/dev/null 2>&1; then
      echo "DRIFT: $f"
    fi
  fi
done
```

If any files show drift, overwrite them from the vault:

```bash
# Overwrite drifted files (vault is source of truth)
rsync -av --update \
  "$VAULT" "$PARC" \
  --include="*.md" --exclude="*"
```

The `--update` flag copies files that are newer in the source than the destination. This is the right flag when vault timestamps are reliable. If they aren't (e.g., git has clobbered mtime), use `--checksum` instead (slower but content-aware).

## Step 4: Handle embedded images

A small number of vault notes use `![[image.png]]` embeds. These images typically live in `/home/manuel/code/wesen/obsidian-vault/Attachments/` or alongside the note.

```bash
# Find notes that embed images
grep -rl '!\[\[' "$VAULT" 2>/dev/null

# For each, extract the image filename and copy to PARC/Attachments/
# Example: ![[PicoCalc-photo.png]] → copy Attachments/PicoCalc-photo.png
```

The manual step here is reviewing which images are referenced and ensuring they exist in `go-go-parc/Attachments/`. This is a small, finite task — only 2 notes in the current vault have image embeds.

## Step 5: Verify counts

After the sync, confirm the PARC has at least as many files as the vault:

```bash
VAULT_COUNT=$(find "$VAULT" -name "*.md" -type f | wc -l)
PARC_COUNT=$(find "$PARC" -name "*.md" -type f | wc -l)
echo "Vault: $VAULT_COUNT | PARC: $PARC_COUNT"

# PARC count should equal vault count (or be higher if PARC has notes not from vault)
```

## Step 6: Handle the stray PROJ file

There is one file in both the vault and PARC at `05/05/PROJ` (no `.md` extension) that contains a wafer config dump. It is already synced. If desired, rename both sides to `PROJ - Wafer Config Reference.md` for consistency — but this is cosmetic and requires updating the vault, which is outside PARC's scope.

---

## One-liner for quick re-sync

After the first sync, subsequent runs are just:

```bash
VAULT=/home/manuel/code/wesen/obsidian-vault/Projects/2026/
PARC=/home/manuel/code/wesen/go-go-golems/go-go-parc/Projects/2026/
rsync -av --update "$VAULT" "$PARC" --include="*.md" --exclude="*"
```

This copies new files and updates any files that changed in the vault since the last sync.

---

## What NOT to do

- **Don't sync pre-2026 content** — `Projects/GO GO GOLEMS/`, `Projects/PROJ - *.md`, etc. are out of scope.
- **Don't delete from PARC** — the vault is additive; if a note exists in PARC but not in the vault, leave it.
- **Don't rewrite wikilinks** — vault notes use `[[wikilinks]]`; the PARC mirrors them verbatim.
- **Don't run as a daemon** — this is a manual sync, not a live filesystem mirror.
- **Don't use `--delete`** with rsync — this would remove PARC-only files.

---

## Edge cases

| Situation | What to do |
|-----------|------------|
| A vault note was renamed | The old name stays in PARC; the new name is copied as a new file. Manually remove the old one if desired. |
| A vault note has image embeds | Copy the image to `go-go-parc/Attachments/` and verify the embed path resolves. |
| A PARC file was manually edited | Re-sync overwrites it (vault is source of truth). Commit PARC changes to the vault first. |
| Month directory is new (e.g., 06/) | rsync creates it automatically. No action needed. |
| Non-.md files in vault (PROJ without extension) | rsync copies them if `--include="*.md"` is the only include. Use an additional `--include` for these edge cases, or add a `--include="PROJ"` pattern. |
