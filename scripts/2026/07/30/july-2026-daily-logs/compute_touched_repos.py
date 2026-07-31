#!/usr/bin/env python3
"""Compute per-day "touched repos" from files sessions wrote + cwd, then
filter the all-repo git commit counts to those repos.

This is the attribution step: a repo counts toward a day's work only if at
least one session active that day wrote a file inside it (NEW/MODIFY in the
`files` table), or had its cwd inside it, or had a cwd that is an ancestor of
the repo. This excludes repos with only human/automated commits.

Inputs (under <invest_dir>/results):
  - day-assignment.json
  - files-written.json   (session_id, path, operation_type)
  - git-commits-per-day.json
  - all-repos.txt        (one absolute repo path per line)
  - sessions-detail.json (for cwd per session)

Output:
  results/touched-repos.json  {day: {touched_repos: [...], commit_counts: {repo:n},
                                     total_commits: n, commit_repos: [...]}}
"""
import argparse, json, os, sys
from bisect import insort

HOME = os.path.expanduser("~")


def norm(p):
    if not p:
        return ""
    if p.startswith("~"):
        p = HOME + p[1:]
    return os.path.normpath(p)


def load_repos(path):
    repos = []
    for l in open(path):
        l = l.strip()
        if l:
            repos.append(norm(l))
    # sort longest-first for prefix matching
    repos.sort(key=lambda r: (-len(r), r))
    return repos


def repo_of(path, repos):
    """Longest repo path that `path` is inside (== repo or under repo/)."""
    p = norm(path)
    if not p:
        return None
    for r in repos:
        if p == r or p.startswith(r + os.sep):
            return r
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("invest_dir")
    ap.add_argument("--days", required=True)
    args = ap.parse_args()
    res = os.path.join(args.invest_dir, "results")
    days = args.days.split(",")

    da = json.load(open(os.path.join(res, "day-assignment-corrected.json")))
    gc = json.load(open(os.path.join(res, "git-commits-per-day.json")))
    repos = load_repos(os.path.join(res, "all-repos.txt"))

    # files-written
    fw = json.load(open(os.path.join(res, "files-written.json")))
    frows = fw if isinstance(fw, list) else fw.get("rows", fw.get("data", []))
    files_by_session = {}
    for r in frows:
        files_by_session.setdefault(r["session_id"], []).append(r["path"])

    # sessions-detail for cwd
    sd = {}
    sdp = os.path.join(res, "sessions-detail.json")
    if os.path.exists(sdp):
        raw = json.load(open(sdp))
        rows = raw if isinstance(raw, list) else raw.get("rows", raw.get("data", []))
        for r in rows:
            sd[r["session_id"]] = r

    # git_commits repos that had commits on a given day
    def day_gc_repos(day):
        out = []
        for repo, counts in gc.items():
            if counts.get(day, 0) > 0:
                out.append(norm(repo))
        return out

    out = {}
    for d in days:
        dsessions = da.get(d, [])
        touched = set()
        # 1) repos from written file paths
        for s in dsessions:
            sid = s.get("id")
            for pth in files_by_session.get(sid, []):
                r = repo_of(pth, repos)
                if r:
                    touched.add(r)
        # 2) repos from cwd (cwd inside a repo, or cwd is a repo)
        cwds = set()
        for s in dsessions:
            sid = s.get("id")
            cwd = s.get("cwd") or (sd.get(sid, {}) or {}).get("cwd")
            if cwd:
                cwds.add(norm(cwd))
        for cwd in cwds:
            r = repo_of(cwd, repos)
            if r:
                touched.add(r)
        # 3) git_commits repos for the day that are under a session cwd ancestor
        #    (catches multi-repo parent cwds like ~/code/wesen/go-go-golems)
        gc_repos = day_gc_repos(d)
        for gcr in gc_repos:
            for cwd in cwds:
                if gcr == cwd or gcr.startswith(cwd + os.sep):
                    touched.add(gcr)
                    break

        # filter commit counts to touched repos
        commit_counts = {}
        for repo, counts in gc.items():
            rn = norm(repo)
            if rn in touched and counts.get(d, 0) > 0:
                commit_counts[repo] = counts[d]
        total = sum(commit_counts.values())
        out[d] = {
            "touched_repos": sorted(touched),
            "commit_counts": commit_counts,
            "total_commits": total,
            "commit_repos": sorted(commit_counts.keys()),
        }

    with open(os.path.join(res, "touched-repos.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    print(f"=== touched-repos -> {res}/touched-repos.json ===", file=sys.stderr)
    for d in days:
        t = out[d]
        print(f"{d}: {len(t['commit_repos'])} commit-repos, {t['total_commits']} commits, "
              f"{len(t['touched_repos'])} touched", file=sys.stderr)


if __name__ == "__main__":
    main()
