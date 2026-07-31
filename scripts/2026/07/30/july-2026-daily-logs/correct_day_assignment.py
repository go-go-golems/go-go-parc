#!/usr/bin/env python3
"""Recompute per-day session assignment using TRUE last-event timestamps.

assign_days.py uses the discovery `last_activity_at`, which for some Pi
sessions equals a stale `ended_at` (file/metadata time) far past the real
last turn/tool event. That over-assigns idle spanning sessions to days they
were not active on.

This script reads day-assignment.json (session metadata + discovery windows)
and sessions-detail.json (true last_turn_at / last_tool_at), recomputes each
session's activity window as [started_at, max(last_turn_at, last_tool_at)]
(falling back to discovery last_activity_at only if both event timestamps are
absent), and writes day-assignment-corrected.json with the same shape.

Usage:
  correct_day_assignment.py <invest_dir> [--days DAY1,DAY2,...]
"""
import argparse, json, os, sys
from datetime import datetime, timezone, timedelta


def parse(ts):
    if not ts:
        return None
    s = ts.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("invest_dir")
    ap.add_argument("--days", required=True)
    args = ap.parse_args()
    res = os.path.join(args.invest_dir, "results")
    days = args.days.split(",")

    # original assignment (for the full session metadata list per framework)
    orig = {}
    da = json.load(open(os.path.join(res, "day-assignment.json")))
    # collect all sessions seen anywhere
    all_sessions = {}
    for d, lst in da.items():
        for s in lst:
            all_sessions[s["id"]] = s

    # true event timestamps from sessions-detail
    sd = {}
    sdp = os.path.join(res, "sessions-detail.json")
    raw = json.load(open(sdp))
    rows = raw if isinstance(raw, list) else raw.get("rows", raw.get("data", []))
    for r in rows:
        sd[r["session_id"]] = r

    def activity_window(s):
        det = sd.get(s["id"], {})
        start = parse(det.get("started_at") or s.get("started_at"))
        lt = parse(det.get("last_turn_at"))
        tl = parse(det.get("last_tool_at"))
        true_end = max([x for x in (lt, tl) if x], default=None)
        if true_end is None:
            true_end = parse(s.get("last_activity_at"))
        if start is None:
            return None, None
        end = true_end or start
        return start, end

    day_sessions = {d: [] for d in days}
    dropped = 0
    for sid, s in all_sessions.items():
        start, end = activity_window(s)
        if start is None:
            continue
        for d in days:
            ds = datetime.fromisoformat(d + "T00:00:00+00:00")
            de = datetime.fromisoformat(d + "T23:59:59+00:00")
            if start <= de and end >= ds:
                day_sessions[d].append(s)

    out = {}
    for d in days:
        fw = {}
        for s in day_sessions[d]:
            fw[s["framework"]] = fw.get(s["framework"], 0) + 1
        out[d] = day_sessions[d]
        print(f"{d}: {len(day_sessions[d])} sessions  {fw}", file=sys.stderr)

    with open(os.path.join(res, "day-assignment-corrected.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nSaved {res}/day-assignment-corrected.json", file=sys.stderr)


if __name__ == "__main__":
    main()
