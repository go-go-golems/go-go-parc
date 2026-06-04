---
title: "Building a GitHub CLI Extension That Reads Git Tracking Information"
aliases:
  - gh-branch-open extension deep dive
  - gh extension build article
tags:
  - github-cli
  - gh-extension
  - git
  - bash
  - tooling
  - article
status: active
type: article
created: 2026-06-03
repo: /home/manuel/code/wesen/wesen-misc/scripts/gh
---

# Building a GitHub CLI Extension That Reads Git Tracking Information

The `gh` command-line tool provides a browse command (`gh browse`) that opens the current repository in a web browser. It accepts a `--branch` flag to open a specific branch. What it does not provide is a way to open the current branch on the remote that the branch actually tracks. This article explains how to build a `gh` extension that fills that gap, and the design decisions that arose from discovering that the "proper" remote is not always `upstream` or `origin`.

> [!summary]
> - `gh` extensions are executable scripts in repositories named `gh-<name>` that `gh` discovers and installs.
> - The initial approach used a hardcoded remote priority (`upstream` > `origin`), which fails when the tracked remote is neither.
> - The correct source of truth for the "proper" remote is `git rev-parse --abbrev-ref --symbolic-full-name @{upstream}`.
> - A tracked upstream like `wesen/task/goja-runtime-flags` encodes both the remote name and the branch name.
> - The extension parses the remote name from the upstream, converts the remote URL from git to https, and opens the branch page.

## Why this extension exists

When working with multiple remotes, the command `gh browse -b $(git branch --show-current)` opens the current branch on the repository's default remote, which is typically `origin`. This is insufficient for workflows where branches track a different remote. In the `go-go-goja` repository, for example, the active development branch `task/goja-runtime-flags` tracks `wesen/task/goja-runtime-flags`, not `origin`. The user wants to open the browser at the URL that corresponds to the branch's actual upstream, not at a fallback remote.

The problem is not selecting a remote from a list. It is determining which remote the current branch is configured to push to and pull from. That information is stored in git's branch configuration, not in any heuristic about repository naming.

## How gh extensions work

GitHub CLI supports extensions through a naming convention and a directory structure. An extension is a repository whose name starts with `gh-` and contains an executable file with the same name. When installed via `gh extension install owner/gh-extension-name`, the executable is placed in a local extensions directory and invoked as `gh extension-name`.

The `gh extension create` command scaffolds a repository with this structure:

```
gh-branch-open/
  gh-branch-open    # executable script
  .git/
```

The executable can be any script that runs on the user's system. The `gh` CLI passes all arguments after the extension name directly to the executable. There is no compilation step for script-based extensions. The script is responsible for parsing its own arguments, calling `git` commands, and performing its work.

Extensions cannot override core `gh` commands. If a name conflicts with a built-in command, the user must invoke it via `gh extension exec <name>`.

## The first approach: hardcoded remote priority

The initial implementation determined the "proper" remote by checking three candidates in order:

1. `upstream` - if a remote named `upstream` exists, use it.
2. `origin` - if `upstream` does not exist but `origin` does, use it.
3. The branch's tracked remote - if neither exists, fall back to whatever `@{upstream}` resolves to.

This heuristic works for the common case where `upstream` is the canonical repository and `origin` is the user's fork. But it fails when the branch tracks a remote that is neither `upstream` nor `origin`. In the `go-go-goja` workspace at `/home/manuel/workspaces/2026-06-03/goja-runtime-flags/go-go-goja`, the remotes are:

```
origin  git@github.com:go-go-golems/go-go-goja.git
wesen   git@github.com:wesen/go-go-goja.git
```

There is no `upstream` remote. The `main` branch tracks `wesen/main`. The `task/goja-runtime-flags` branch tracks `wesen/task/goja-runtime-flags`. Under the hardcoded priority, the extension would select `origin` (since `upstream` does not exist) and open the branch on `go-go-golems/go-go-goja`. This is the wrong repository for branches that are pushed to `wesen`.

The mistake was assuming that remote names encode repository roles. They do not. A remote named `wesen` can be the primary remote for one branch, while `origin` is the primary for another. The only authoritative source is git's own tracking configuration.

## The second approach: reading the tracked upstream

Git stores branch tracking information in the repository's config. For a branch named `task/goja-runtime-flags`, the relevant configuration entries are:

```
branch.task/goja-runtime-flags.remote = wesen
branch.task/goja-runtime-flags.merge = refs/heads/task/goja-runtime-flags
```

These can be read with:

```bash
git rev-parse --abbrev-ref --symbolic-full-name @{upstream}
```

For the `task/goja-runtime-flags` branch in the go-go-goja workspace, this command returns:

```
wesen/task/goja-runtime-flags
```

The output format is `remote-name/branch-name`. The remote name is everything before the first slash. This is the correct remote to use for opening the branch page.

The updated logic in the extension:

1. Get the current branch name with `git branch --show-current`.
2. Query the upstream with `git rev-parse --abbrev-ref --symbolic-full-name @{u}`.
3. If an upstream exists, extract the remote name (the part before the first `/`).
4. If no upstream exists, fall back to `upstream` > `origin`.
5. Get the remote URL with `git remote get-url <remote>`.
6. Convert the URL from git ssh format to https format.
7. Construct `https://github.com/{owner}/{repo}/tree/{branch}`.
8. Open the URL in the system browser, or print it if `-n` is passed.

## URL conversion

Git remote URLs come in multiple formats, and the extension must handle the common ones:

| Git URL | Web URL |
|---------|---------|
| `git@github.com:owner/repo.git` | `https://github.com/owner/repo` |
| `https://github.com/owner/repo.git` | `https://github.com/owner/repo` |
| `ssh://git@github.com/owner/repo.git` | `https://github.com/owner/repo` |

The conversion is performed by stripping the `.git` suffix and removing the git-specific prefix:

```bash
WEB_URL="${REMOTE_URL%.git}"
WEB_URL="${WEB_URL#git@github.com:}"
WEB_URL="${WEB_URL#ssh://git@github.com/}"
WEB_URL="${WEB_URL#https://github.com/}"
WEB_URL="https://github.com/${WEB_URL}"
```

This is a series of bash parameter expansions. Each `#` operator removes the matching prefix. The order matters: `git@github.com:` must be removed before `https://github.com/` because the latter is a substring that could appear in the former after the protocol is removed. The `%.git` removes the suffix. The final result is always `https://github.com/owner/repo`.

## The complete extension

```bash
#!/usr/bin/env bash
set -euo pipefail

# Usage: gh branch-open [-h|--help] [file-path]
#
# Examples:
#   gh branch-open                          # open branch root
#   gh branch-open cmd/gh/main.go           # open file on branch
#   gh branch-open --help                   # show this help

FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      sed -n '4,11p' "$0"
      exit 0
      ;;
    -*)
      echo "Unknown flag: $1" >&2
      echo "Usage: gh branch-open [-h|--help] [file-path]" >&2
      exit 1
      ;;
    *)
      if [[ -n "$FILE" ]]; then
        echo "Only one file path allowed. Got: $FILE and $1" >&2
        exit 1
      fi
      FILE="$1"
      shift
      ;;
  esac
done

if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo "gh-branch-open: not inside a git repository" >&2
  exit 1
fi

BRANCH=$(git branch --show-current 2>/dev/null || true)
if [[ -z "${BRANCH:-}" ]]; then
  echo "gh-branch-open: could not determine current branch" >&2
  exit 1
fi

REMOTE=""
UPSTREAM=$(git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>/dev/null || true)
if [[ -n "${UPSTREAM:-}" ]]; then
  REMOTE="${UPSTREAM%%/*}"
fi

if [[ -z "${REMOTE:-}" ]]; then
  if git remote get-url upstream &>/dev/null; then
    REMOTE="upstream"
  elif git remote get-url origin &>/dev/null; then
    REMOTE="origin"
  fi
fi

if [[ -z "${REMOTE:-}" ]]; then
  echo "gh-branch-open: no remote found (tried: tracked branch, upstream, origin)" >&2
  exit 1
fi

REMOTE_URL=$(git remote get-url "$REMOTE" 2>/dev/null || true)
if [[ -z "${REMOTE_URL:-}" ]]; then
  echo "gh-branch-open: could not get URL for remote '$REMOTE'" >&2
  exit 1
fi

WEB_URL="${REMOTE_URL%.git}"
WEB_URL="${WEB_URL#git@github.com:}"
WEB_URL="${WEB_URL#ssh://git@github.com/}"
WEB_URL="${WEB_URL#https://github.com/}"
WEB_URL="https://github.com/${WEB_URL}"

if [[ -n "$FILE" ]]; then
  URL="${WEB_URL}/blob/${BRANCH}/${FILE}"
else
  URL="${WEB_URL}/tree/${BRANCH}"
fi

if command -v xdg-open &>/dev/null; then
  xdg-open "$URL"
elif command -v open &>/dev/null; then
  open "$URL"
else
  python3 -m webbrowser "$URL"
fi
```

The script uses `set -euo pipefail` for error handling. The `-e` flag causes the script to exit on any command failure. The `-u` flag treats unset variables as errors. The `-o pipefail` flag causes a pipeline to fail if any command in it fails. These settings are standard for robust bash scripts and prevent silent failures when git commands return empty output.

## File path argument

If a file path is passed as a positional argument, the extension opens that file on the current branch instead of the branch root:

```bash
gh branch-open pkg/xgoja/providers/host/host.go
```

This constructs a `/blob` URL instead of a `/tree` URL:

```
https://github.com/wesen/go-go-goja/blob/task/goja-runtime-flags/pkg/xgoja/providers/host/host.go
```

The conversion is a single conditional on whether the `FILE` variable is non-empty:

```bash
if [[ -n "$FILE" ]]; then
  URL="${WEB_URL}/blob/${BRANCH}/${FILE}"
else
  URL="${WEB_URL}/tree/${BRANCH}"
fi
```

The script rejects multiple file paths to prevent the ambiguity of which file to open.

## Testing across repository configurations

The extension was tested on four repositories with different remote configurations:

### go-go-host: upstream, origin, and wesen remotes

```
upstream  git@github.com:go-go-golems/go-go-host.git
origin    git@github.com:go-go-golems/go-go-host.git
wesen     git@github.com:wesen/go-go-host.git
```

The `main` branch has no explicit tracking configuration in this checkout. The extension falls back to `upstream` and opens `go-go-golems/go-go-host/tree/main`. This is correct because `upstream` is the canonical repository.

### go-go-parc: origin only

```
origin  ssh://git@github.com/go-go-golems/go-go-parc
```

No tracking branch is configured. The extension falls back to `origin` and opens `go-go-golems/go-go-parc/tree/main`.

### go-go-goja main branch: tracks wesen/main

```
origin  git@github.com:go-go-golems/go-go-goja.git
wesen   git@github.com:wesen/go-go-goja.git
```

The `main` branch tracks `wesen/main`. The extension reads `@{upstream}` as `wesen/main`, extracts `wesen`, and opens `wesen/go-go-goja/tree/main`. This is the correct remote for this branch.

### go-go-goja task/goja-runtime-flags: tracks wesen/task/goja-runtime-flags

Same remotes as above, but on the `task/goja-runtime-flags` branch. The extension reads `@{upstream}` as `wesen/task/goja-runtime-flags`, extracts `wesen`, and opens `wesen/go-go-goja/tree/task/goja-runtime-flags`.

## Why reading @{upstream} is the right design

The `@{upstream}` syntax is git's canonical way to refer to the branch that the current branch tracks. It resolves correctly regardless of remote names, repository layout, or user conventions. It handles the case where different branches in the same repository track different remotes. It requires no additional configuration beyond what git already stores.

The alternative approaches and why they were rejected:

| Approach | Why it fails |
|----------|-------------|
| Hardcoded `upstream` > `origin` | Breaks when the tracked remote has a different name, like `wesen` |
| Use the first remote in `git remote` output | Order is arbitrary and does not reflect tracking configuration |
| Use the remote with the most branches | Does not indicate which remote the current branch pushes to |
| Parse `.git/config` directly | Fragile; git's config format can change, and `@{upstream}` is the public API |

## Failure modes

### "not inside a git repository"

Cause: the current directory is not inside a git work tree.
Fix: change to a git repository before running the command.

### "could not determine current branch"

Cause: the repository is in detached HEAD state.
Fix: checkout a branch, or the extension could be enhanced to open the commit page instead.

### "no remote found"

Cause: the repository has no remotes configured, and the branch has no upstream.
Fix: add a remote with `git remote add`.

### Wrong URL for non-GitHub remotes

Cause: the URL conversion assumes GitHub. A remote on GitLab or another host would produce a GitHub URL.
Fix: extend the URL parsing to handle other hosts, or use `gh browse -R owner/repo -b branch` which delegates to `gh`'s own remote resolution.

### Multiple file paths

Cause: more than one positional argument was provided.
Fix: pass only a single file path, or omit the argument entirely to open the branch root.

## Architecture

```mermaid
flowchart TD
    A[gh branch-open] --> B{Parse flags}
    B --> C[Validate git repo]
    C --> D[Get current branch]
    D --> E[Read @{upstream}]
    E -->|wesen/task/branch| F[Extract remote name]
    E -->|empty| G[Fallback: upstream > origin]
    F --> H[Get remote URL]
    G --> H
    H --> I[Convert git URL to https]
    I --> J{File arg?}
    J -->|yes| K[Build blob URL]
    J -->|no| L[Build tree URL]
    K --> M[Open browser]
    L --> M

    style E fill:#2d4a22,stroke:#4a7c3f
    style F fill:#2d4a22,stroke:#4a7c3f
```

The critical path is the `@{upstream}` read and remote extraction. This is the single operation that differentiates this extension from a naive wrapper around `gh browse`. Without it, the extension would be indistinguishable from `gh browse -b $(git branch --show-current)`.

## Installation

Script-based extensions can be installed from the local filesystem during development:

```bash
gh extension install /path/to/gh-branch-open --force
```

Or from a GitHub repository:

```bash
gh extension install wesen/gh-branch-open
```

The `--force` flag reinstalls the extension if it already exists, which is useful during iterative development.

## Related notes

- [[ARTICLE - xgoja - Building a Query Tool with Jsverbs and Embedded Modules]] - the xgoja diary-db tool from the same session
- [[ARTICLE - Data Pipeline - From GitHub API to Retro Browser]] - the data collection pipeline
- [[DAILY-CHANGELOG-2026-06-02]] - the docmgr ticket containing this extension
- [[gh browse --help]] - the built-in browse command
- [[gh extension --help]] - extension management commands
