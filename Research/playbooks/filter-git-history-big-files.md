---
title: "Filtering Git History for Big Files — How We Do It"
aliases: [git history big files, git filter-repo, remove large blobs, GitHub GH001, purge big files]
tags: [knowledge-base, playbook, git, history-rewrite, github, large-files, filter-repo]
status: active
type: knowledge-base
created: 2026-05-20
---

# Filtering Git History for Big Files — How We Do It

> [!summary]
> Use this playbook when GitHub rejects a push because a historical blob is too large. The safe workflow is: back up uncommitted work outside Git refs, create a bundle backup, inspect large blobs, rewrite history with `git filter-repo`, restore the remote, verify no bad blobs remain, push with `--force-with-lease`, and then restore unrelated local work.

## When to use this playbook

Use this when `git push` fails with a message like:

```text
remote: error: GH001: Large files detected.
remote: error: File path/to/file is 126.73 MB; this exceeds GitHub's file size limit of 100.00 MB
```

This means the blob exists somewhere in the commit history being pushed. Removing the file from the current working tree is not enough. GitHub checks all objects in the pushed history, so the offending blob must be removed from every commit that contains it.

Use this playbook for files that should never have been committed: model caches, downloaded PDFs, build artifacts, databases, generated reports, videos, and other local artifacts. Do not use it casually on source files that other people may depend on, because rewriting history changes commit hashes.

## The complete workflow

The full sequence is:

1. Inspect the working tree.
2. Back up uncommitted work outside Git refs.
3. Clean the working tree.
4. Create a full bundle backup of the current repository history.
5. Identify large blobs and paths to remove.
6. Rewrite history with `git filter-repo`.
7. Restore the `origin` remote.
8. Verify the bad blobs are gone.
9. Add ignore rules so the files do not come back.
10. Commit the ignore rules and any diary/playbook updates.
11. Force-push with `--force-with-lease`.
12. Restore unrelated local work.

Do these steps in order. The order matters because both `git stash` and normal backup branches create Git refs that can keep the old large blob reachable. If the blob remains reachable from any ref, it will still appear in `git rev-list --objects --all`.

## Step 1: inspect the working tree

Start by seeing what is dirty:

```bash
git status --short
```

If there are no local changes, the rewrite is simpler. If there are unrelated modified or untracked files, protect them before rewriting history. Do not use `git stash` for this job unless you understand that `refs/stash` may keep old objects reachable.

## Step 2: back up uncommitted work outside Git refs

Create a backup directory under `.git/` and store two files:

- a binary patch for tracked modifications
- a tar archive for untracked files

```bash
set -euo pipefail

BACKUP_DIR=.git/history-rewrite-backup-$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

# Save modified tracked files as a binary patch.
git diff --binary > "$BACKUP_DIR/uncommitted-tracked.patch"

# Save untracked, non-ignored files as a tar archive.
git ls-files --others --exclude-standard -z > "$BACKUP_DIR/untracked-files.zlist"
if [ -s "$BACKUP_DIR/untracked-files.zlist" ]; then
  tar --null -T "$BACKUP_DIR/untracked-files.zlist" -cf "$BACKUP_DIR/untracked-files.tar"
else
  : > "$BACKUP_DIR/untracked-files.tar"
fi

printf '%s\n' "$BACKUP_DIR" > .git/latest-history-rewrite-backup-dir

echo "Saved uncommitted backup to $BACKUP_DIR"
echo "Tracked patch size: $(du -h "$BACKUP_DIR/uncommitted-tracked.patch" | cut -f1)"
echo "Untracked tar size: $(du -h "$BACKUP_DIR/untracked-files.tar" | cut -f1)"
```

This backup lives outside normal Git refs. It will not keep the bad blob reachable through branches or stashes.

## Step 3: clean the working tree

Restore tracked modifications and remove untracked files after they have been backed up:

```bash
# Restore tracked files that had local modifications.
git restore --worktree -- .

# Remove untracked files and directories.
git clean -fd

git status --short
```

Only run `git clean -fd` after confirming the tar backup exists. `git clean` deletes files. The backup is what makes this safe.

If you only want to restore a specific tracked file instead of all tracked files, use:

```bash
git restore --worktree -- path/to/file
```

## Step 4: create a full bundle backup

Before rewriting history, create a bundle containing all refs:

```bash
HEAD_BEFORE=$(git rev-parse HEAD)
BUNDLE=.git/history-rewrite-backup-before-filter-${HEAD_BEFORE}.bundle

git bundle create "$BUNDLE" --all
printf '%s\n' "$HEAD_BEFORE" > .git/history-rewrite-head-before-filter

echo "HEAD before rewrite: $HEAD_BEFORE"
echo "Bundle backup: $BUNDLE ($(du -h "$BUNDLE" | cut -f1))"
```

A bundle is a real Git repository archive. If the rewrite goes wrong, you can inspect or clone it:

```bash
git clone .git/history-rewrite-backup-before-filter-<sha>.bundle /tmp/recovered-repo
```

## Step 5: identify large blobs

List the largest blobs reachable from all refs:

```bash
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1 == "blob" {printf "%12d %s %s\n", $3, $2, substr($0, index($0,$4))}' \
  | sort -nr \
  | head -30
```

To list only blobs over GitHub's hard limit:

```bash
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1 == "blob" && $3 > 100000000 {print}'
```

Typical offenders:

| Offender | Usually remove? | Why |
|---|---:|---|
| `local_cache/` | yes | Model caches are reproducible local artifacts. |
| `*.onnx`, `*.safetensors`, `*.pt`, `*.pth`, `*.bin` | usually | Model weights should use LFS or external storage. |
| `resources/*.pdf` under ticket dirs | usually | Downloaded books and papers should not be in source history. |
| `output/` | yes | Generated outputs should be ignored. |
| SQLite databases | depends | Small fixture DBs may be OK; generated DBs should usually be ignored. |
| screenshots under docs | depends | Small screenshots are often OK; large videos/images should be reviewed. |

## Step 6: rewrite history with git-filter-repo

Check that `git-filter-repo` is installed:

```bash
git filter-repo --help >/dev/null
```

Remove exact paths with `--path ... --invert-paths`:

```bash
git filter-repo --force \
  --path 'path/to/local_cache/' \
  --path 'path/to/resources/' \
  --invert-paths
```

Example from the incident that created this playbook:

```bash
git filter-repo --force \
  --path 'ttmp/2026/05/15/THERAPIST-VEC-2026--therapist-vector-search-entity-extraction-and-bleve-hybrid-search/scripts/02-fastembed-go/local_cache/' \
  --path 'ttmp/2026/04/25/container-books--download-linux-container-related-books/resources/' \
  --invert-paths
```

`git filter-repo` rewrites commit history and repacks the repository. It also removes remotes by design as a safety measure. This is expected.

## Step 7: restore the remote

After `git filter-repo`, check remotes:

```bash
git remote -v
```

If `origin` is gone, restore it:

```bash
git remote add origin git@github.com:wesen/claw-stuff.git
# or, if it exists but is wrong:
git remote set-url origin git@github.com:wesen/claw-stuff.git
```

Use the repository's actual remote URL.

## Step 8: verify the bad blobs are gone

Verify specific removed paths:

```bash
git rev-list --objects --all | grep 'local_cache' || true
git rev-list --objects --all | grep 'container-books.*resources' || true
```

Verify no blobs over 100 MB remain:

```bash
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1 == "blob" && $3 > 100000000 {print}'
```

This command should print nothing.

List the largest remaining blobs as a sanity check:

```bash
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1 == "blob" {printf "%12d %s %s\n", $3, $2, substr($0, index($0,$4))}' \
  | sort -nr \
  | head -30
```

## Step 9: add ignore rules

Add rules that prevent recurrence. Example:

```gitignore
# Downloaded books, model caches, and ML artifacts (large binaries)
ttmp/**/resources/
tmp/**/resources/
ttmp/**/local_cache/
**/local_cache/
*.onnx
*.safetensors
*.pt
*.pth
*.bin
```

Tune the patterns to the repository. Be careful with broad ignores such as `ttmp/**/resources/` if some tickets intentionally track small source resources.

Commit the ignore rule change:

```bash
git add .gitignore
git commit -m "Ignore model caches and large generated resources"
```

## Step 10: push safely

Fetch the remote first so `--force-with-lease` has an up-to-date lease:

```bash
git fetch origin main
```

Check whether a force push is required:

```bash
git merge-base --is-ancestor origin/main main \
  && echo 'normal push should work' \
  || echo 'history diverged; force-with-lease required'
```

Push:

```bash
git push --force-with-lease origin main
```

Use `--force-with-lease`, not `--force`. The lease prevents overwriting remote commits that appeared after your last fetch.

If this succeeds, GitHub accepted the rewritten history.

## Step 11: restore local work

Restore the untracked files and tracked modifications that were backed up before the rewrite:

```bash
BACKUP_DIR=$(cat .git/latest-history-rewrite-backup-dir)
echo "Restoring from $BACKUP_DIR"

# Restore untracked files.
if [ -s "$BACKUP_DIR/untracked-files.tar" ]; then
  tar -xf "$BACKUP_DIR/untracked-files.tar"
fi

# Restore tracked modifications.
if [ -s "$BACKUP_DIR/uncommitted-tracked.patch" ]; then
  git apply --whitespace=nowarn "$BACKUP_DIR/uncommitted-tracked.patch"
fi

git status --short
```

If `git apply` fails, the patch is still present. Inspect it manually:

```bash
git apply --check "$BACKUP_DIR/uncommitted-tracked.patch"
git apply --reject "$BACKUP_DIR/uncommitted-tracked.patch"
```

## Recovery procedures

### If the rewrite removed too much

Use the bundle backup:

```bash
git clone .git/history-rewrite-backup-before-filter-<sha>.bundle /tmp/recovered-repo
```

You can inspect files or recover commits from `/tmp/recovered-repo`.

### If `git filter-repo` refuses to run

`git filter-repo` often refuses to run on a dirty working tree. Clean or back up local changes first. Avoid bypassing this safety check unless you know why it is failing.

### If the push still fails with a large file

Run the over-100MB check again:

```bash
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1 == "blob" && $3 > 100000000 {print}'
```

If it prints a path, add that path to the `git filter-repo` command and rewrite again. If it prints nothing but GitHub rejects the push, check whether another ref is being pushed or whether your local refs still include backup refs that retain old history.

### If `git rev-list --objects --all` still shows the removed file

Some ref still points to old history. Check refs:

```bash
git show-ref | grep -E 'stash|backup|original|filter-repo|refs/replace' || true
```

Delete refs that intentionally preserve the old history only after confirming you have an external bundle backup.

## Checklist

Before rewriting:

- [ ] `git status --short` reviewed.
- [ ] Uncommitted tracked changes saved to `.git/.../uncommitted-tracked.patch`.
- [ ] Untracked files saved to `.git/.../untracked-files.tar`.
- [ ] Working tree cleaned.
- [ ] Bundle backup created.
- [ ] Largest blobs listed.

After rewriting:

- [ ] `origin` remote restored.
- [ ] Removed path no longer appears in `git rev-list --objects --all`.
- [ ] No blobs over 100MB remain.
- [ ] Ignore rules added and committed.
- [ ] `git fetch origin main` completed.
- [ ] `git push --force-with-lease origin main` succeeded.
- [ ] Local uncommitted work restored.

## Minimal command block

Use this when you already know the bad paths and want the compact version:

```bash
set -euo pipefail

# Back up local work outside Git refs.
BACKUP_DIR=.git/history-rewrite-backup-$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"
git diff --binary > "$BACKUP_DIR/uncommitted-tracked.patch"
git ls-files --others --exclude-standard -z > "$BACKUP_DIR/untracked-files.zlist"
if [ -s "$BACKUP_DIR/untracked-files.zlist" ]; then
  tar --null -T "$BACKUP_DIR/untracked-files.zlist" -cf "$BACKUP_DIR/untracked-files.tar"
else
  : > "$BACKUP_DIR/untracked-files.tar"
fi
printf '%s\n' "$BACKUP_DIR" > .git/latest-history-rewrite-backup-dir

git restore --worktree -- .
git clean -fd

# Bundle backup.
HEAD_BEFORE=$(git rev-parse HEAD)
git bundle create ".git/history-rewrite-backup-before-filter-${HEAD_BEFORE}.bundle" --all

# Rewrite history. Replace paths with the actual offenders.
git filter-repo --force \
  --path 'path/to/local_cache/' \
  --path 'path/to/resources/' \
  --invert-paths

# Restore remote and verify.
git remote add origin git@github.com:wesen/claw-stuff.git || git remote set-url origin git@github.com:wesen/claw-stuff.git

git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1 == "blob" && $3 > 100000000 {print}'

# Push safely.
git fetch origin main
git push --force-with-lease origin main

# Restore local work.
BACKUP_DIR=$(cat .git/latest-history-rewrite-backup-dir)
tar -xf "$BACKUP_DIR/untracked-files.tar"
git apply --whitespace=nowarn "$BACKUP_DIR/uncommitted-tracked.patch" || true
```

## Notes for shared repositories

A force-pushed history rewrite changes commit hashes. Anyone else with a clone must reconcile their local repository. The cleanest path for collaborators is often:

```bash
git fetch origin
git checkout main
git reset --hard origin/main
```

They should save any local work first. If they have local commits, they need to rebase those commits onto the new `origin/main` or cherry-pick them onto a fresh branch.
