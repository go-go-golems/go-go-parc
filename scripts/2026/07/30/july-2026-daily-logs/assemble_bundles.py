#!/usr/bin/env python3
"""Assemble per-day evidence bundles for the July daily-log batch.

Each bundle is fully self-contained: a subagent can write the report from it
WITHOUT running go-minitrace or git. The parent already did all discovery,
conversion, querying, git verification, and repo attribution.

Inputs (under <invest_dir>/results):
  - day-assignment.json       (assign_days.py: per-day session list)
  - touched-repos.json        (compute_touched_repos.py: per-day attributed
                               commit_counts + total_commits + commit_repos)
  - commit-subjects.json      (commit_subjects.py: {day: {repo: ["h|d|s"]}})
  - sessions-detail.json      (sessions-detail.sql: turns/tools/cwd per session)
  - july-project-reports.txt  ("YYYY-MM-DD|Note Name" per line)

Output: bundles/day-YYYY-MM-DD.json with:
  day, sessions[], commit_counts{}, total_commits, commit_subjects{},
  project_reports[]  (list of "YYYY-MM-DD|Note Name" relevant-ish, unfiltered —
                     the subagent picks by topic+date)
"""
import argparse, json, os, sys
from datetime import datetime


def parse(ts):
    if not ts:
        return None
    s = ts.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def fmt_win(started, last):
    s = parse(started)
    e = parse(last)
    if s and e:
        return f"{s.strftime('%m-%d %H:%M')} → {e.strftime('%m-%d %H:%M')}"
    if s:
        return f"{s.strftime('%m-%d %H:%M')} → ?"
    return "?"


def short_id(full):
    return (full or "?")[:8]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("invest_dir")
    ap.add_argument("--days", required=True)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()
    invest = args.invest_dir
    res = os.path.join(invest, "results")
    out_dir = args.out_dir or os.path.join(invest, "bundles")
    os.makedirs(out_dir, exist_ok=True)
    days = args.days.split(",")

    da = json.load(open(os.path.join(res, "day-assignment-corrected.json")))
    tr = json.load(open(os.path.join(res, "touched-repos.json")))
    cs = json.load(open(os.path.join(res, "commit-subjects.json")))

    sd = {}
    sdp = os.path.join(res, "sessions-detail.json")
    if os.path.exists(sdp):
        raw = json.load(open(sdp))
        rows = raw if isinstance(raw, list) else raw.get("rows", raw.get("data", []))
        for r in rows:
            sd[r["session_id"]] = r

    pr_path = os.path.join(res, "july-project-reports.txt")
    project_reports = [l.strip() for l in open(pr_path) if l.strip()] if os.path.exists(pr_path) else []

    summary = []
    for d in days:
        dsessions = da.get(d, [])
        enriched = []
        for s in dsessions:
            sid = s.get("id")
            det = sd.get(sid, {})
            turns = det.get("turn_count", s.get("turn_count"))
            tools = det.get("tool_call_count", s.get("tool_call_count"))
            started = s.get("started_at") or det.get("started_at")
            last = (s.get("last_activity_at") or det.get("last_tool_at")
                    or det.get("last_turn_at") or det.get("ended_at"))
            enriched.append({
                "short": short_id(sid),
                "id": sid,
                "framework": s.get("framework") or det.get("framework"),
                "model": s.get("model") or det.get("model"),
                "title": s.get("title") or det.get("title"),
                "cwd": s.get("cwd") or det.get("cwd"),
                "turns": turns,
                "tools": tools,
                "started_at": started,
                "last_activity_at": last,
                "window": fmt_win(started, last),
            })
        # sort sessions by started_at
        enriched.sort(key=lambda x: (x.get("started_at") or ""))

        t = tr.get(d, {})
        commit_counts = t.get("commit_counts", {})
        total_commits = t.get("total_commits", 0)
        commit_repos = set(t.get("commit_repos", []))

        # commit subjects filtered to attributed repos
        day_subjects_all = cs.get(d, {})
        day_subjects = {repo: subs for repo, subs in day_subjects_all.items() if repo in commit_repos}

        bundle = {
            "day": d,
            "sessions": enriched,
            "commit_counts": commit_counts,
            "total_commits": total_commits,
            "commit_subjects": day_subjects,
            "project_reports": project_reports,
        }
        with open(os.path.join(out_dir, f"day-{d}.json"), "w") as fh:
            json.dump(bundle, fh, indent=2)
        summary.append((d, len(enriched), total_commits, len(commit_counts)))

    print(f"=== Per-day bundles -> {out_dir} ===", file=sys.stderr)
    for d, ns, nc, nre in summary:
        flag = "" if (ns or nc) else "  (NO ACTIVITY)"
        print(f"{d}: {ns} sessions, {nc} commits, {nre} commit-repos{flag}", file=sys.stderr)


if __name__ == "__main__":
    main()
