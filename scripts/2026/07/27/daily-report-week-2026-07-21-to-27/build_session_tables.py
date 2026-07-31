#!/usr/bin/env python3
"""Build per-day session tables with time windows from minitrace archives."""
import json, os, glob
from datetime import datetime

INVEST_DIR = os.path.dirname(os.path.abspath(__file__))
days = ["2026-07-21","2026-07-22","2026-07-23","2026-07-24","2026-07-25","2026-07-26","2026-07-27"]

# Load session-list (has started_at, turns, tools, model, title)
sl = json.load(open(os.path.join(INVEST_DIR,'results','session-list.json')))
sl_map = {s['id']: s for s in sl}

# Load day assignment
da = json.load(open(os.path.join(INVEST_DIR,'results','day-assignment.json')))

# For time windows, we need first/last activity per session from the archives.
# The discovery JSON has last_activity_at; session-list has started_at.
# Let's read discovery JSON for last_activity_at.
disc = {}
for name in ['pi','codex','claude-code']:
    try:
        for s in json.load(open(os.path.join(INVEST_DIR,'results',f'{name}-discovery.json'))):
            disc[s['id']] = s
    except: pass

def parse(ts):
    if not ts: return None
    ts = ts.replace('Z','+00:00')
    try: return datetime.fromisoformat(ts)
    except: return None

out = {}
for day in days:
    rows = []
    for s in da[day]:
        sid = s['id']
        sls = sl_map.get(sid, {})
        d = disc.get(sid, {})
        started = parse(s.get('started_at') or sls.get('started_at'))
        last = parse(d.get('last_activity_at') or s.get('last_activity_at'))
        # window for THIS day
        day_start = datetime.fromisoformat(day+'T00:00:00+00:00')
        day_end = datetime.fromisoformat(day+'T23:59:59+00:00')
        ws = max(started, day_start) if started else day_start
        we = min(last, day_end) if last else day_end
        rows.append({
            'id': sid,
            'short_id': sid[:8],
            'framework': s['framework'],
            'model': sls.get('model') or d.get('model') or '?',
            'title': (sls.get('title') or d.get('title') or '?'),
            'turns': sls.get('turns', 0),
            'tools': sls.get('tools', 0),
            'cwd': s.get('cwd',''),
            'started_at': sls.get('started_at') or s.get('started_at'),
            'last_activity_at': d.get('last_activity_at') or s.get('last_activity_at'),
            'day_window_start': ws.isoformat() if ws else None,
            'day_window_end': we.isoformat() if we else None,
        })
    # sort by window start
    rows.sort(key=lambda r: r.get('day_window_start') or '')
    out[day] = rows

with open(os.path.join(INVEST_DIR,'results','per-day-sessions.json'),'w') as fh:
    json.dump(out, fh, indent=2)

for day in days:
    print(f"\n=== {day}: {len(out[day])} sessions ===")
    for r in out[day]:
        ws = (r['day_window_start'] or '')[5:16].replace('T',' ')
        we = (r['day_window_end'] or '')[5:16].replace('T',' ')
        print(f"  {r['short_id']}  {r['framework']:11s}  {r['model']:16s}  t={r['turns']:>5}  {r['title'][:50]:50s}  {ws}->{we}")
