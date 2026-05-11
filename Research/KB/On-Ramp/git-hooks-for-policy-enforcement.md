---
title: "Git Hooks for Policy Enforcement"
aliases:
  - git hooks
  - pre-receive hook
  - git server hooks
  - policy hooks
tags: [knowledge-base, on-ramp, git, hooks, policy, security, enforcement]
status: active
type: knowledge-base
created: 2026-05-11
---

# Git Hooks for Policy Enforcement

> [!summary]
> Git hooks are scripts that Git runs at specific points in its workflow. Server-side hooks — especially `pre-receive` — let you enforce policy before changes enter the repository. This entry covers which hooks matter for enforcement, how a `pre-receive` hook inspects incoming objects, and why the hook is the *last line of defense*, not the only one.

## The idea in one paragraph

A Git hook is a script that Git executes at a specific workflow event. Client-side hooks (pre-commit, post-commit) run on the developer's machine and can be bypassed. Server-side hooks (pre-receive, update, post-receive) run on the Git server and cannot be bypassed — if the hook rejects the push, the push fails. For policy enforcement, only server-side hooks matter.

## The server-side hooks

| Hook | When it runs | What it can do | What we use it for |
|------|-------------|----------------|-------------------|
| `pre-receive` | Before any ref is updated | Accept or reject the entire push | Main policy enforcement |
| `update` | Before each ref is updated | Accept or reject per-ref | Per-branch policy |
| `post-receive` | After refs are updated | Trigger side effects (CI, notifications) | None currently |

The `pre-receive` hook receives all proposed ref updates on stdin. Each line is: `<old-sha> <new-sha> <ref-name>`. The hook reads all lines, decides whether the push complies with policy, and exits 0 (accept) or 1 (reject). If it exits 1, the entire push is rejected — no refs are updated.

## What a pre-receive hook can inspect

The hook receives old and new SHAs for each ref. Using `git` commands, it can inspect:

- **Which files changed**: `git diff --name-only $old_sha $new_sha`
- **The diff content**: `git diff $old_sha $new_sha`
- **The commit messages**: `git log $old_sha..$new_sha --format=%s`
- **The author/committer**: `git log $old_sha..$new_sha --format=%an`
- **Object types**: `git cat-file -t $sha`

In Wish Git, the `forge-hook` binary is installed as the `pre-receive` hook. It:

1. Reads all ref update lines from stdin.
2. Looks up the agent run associated with the SSH certificate (from the `principals` field) in the Postgres database.
3. Checks each proposed ref update against the agent run's allowed refs.
4. Checks each changed file against the agent run's allowed paths.
5. Exits 0 if all checks pass; exits 1 with an error message if any check fails.

```bash
#!/bin/bash
# pre-receive hook — installed in bare repository
while read old_sha new_sha ref_name; do
    # Look up policy from database
    policy=$(forge-hook check \
        --principal "$SSH_PRINCIPAL" \
        --ref "$ref_name" \
        --old "$old_sha" \
        --new "$new_sha")

    if [ $? -ne 0 ]; then
        echo "REJECTED: $policy"
        exit 1
    fi
done
exit 0
```

## Why the hook is the last line of defense

Wish Git enforces policy at three layers:

1. **SSH server**: Checks the certificate's `force-command` and `principals`. Limits what commands the agent can run (`git-receive-pack` or `git-upload-pack`).

2. **Git protocol**: The SSH server's exec callback inspects the requested repository and command, checking against the agent run's scope.

3. **Pre-receive hook**: Inspects the actual content of the push — which refs are being updated, which files are being changed. This is the only layer that can see *what* is being pushed, not just *that* something is being pushed.

If the SSH server somehow allows an unauthorized command, or the Git protocol check has a bug, the hook catches it. The hook runs inside the Git process on the server — it cannot be bypassed by modifying the client.

## The gotchas we've hit

**The hook must be fast.** `pre-receive` runs synchronously — Git waits for it to exit before proceeding. If the hook takes 5 seconds per push, every push takes 5+ seconds. Keep the hook fast: cache database lookups, avoid spawning processes unnecessarily, and use a compiled binary (Go) instead of a shell script for complex logic.

**The hook sees all refs at once.** A single push can update multiple branches and tags. The hook must process all of them before deciding. A common mistake: accepting the first ref and rejecting the second, but Git has already started processing the first one. Read all lines first, then decide.

**`00...00` as old SHA means "new ref."** If the old SHA is all zeros, the ref is being created (a new branch or tag). If the new SHA is all zeros, the ref is being deleted. Handle both cases explicitly.

**Environment variables may not be what you expect.** The hook runs in a minimal environment — no shell profile, no `PATH` guarantee. Use absolute paths for all commands and binaries. In Wish Git, the `forge-hook` binary is at a known absolute path.

**Hooks must be installed per-repository.** There is no global `pre-receive` hook for all repositories on a server. Each bare repository needs its own `hooks/pre-receive`. For Wish Git, the server installs the hook when creating a new bare repository.

## Where to go deeper

- **`githooks(5)`** — The official documentation for all hook types, their arguments, and their environment.
- **Pro Git, Chapter 8.3** — "Customizing Git - Git Hooks" — Good introduction to both client and server-side hooks.
- **Wish Git project report** in this PARC library — The full three-layer enforcement architecture.
- [[PROJ - Wish Git - OAuth Scoped Git over SSH for Coding Agents]] — forge-hook pre-receive hook, three-credential separation, database-owned authorization
- [[Fundamentals/access-control-models]] — The delegation model that explains *why* hooks are the enforcement layer for scoped credentials.
