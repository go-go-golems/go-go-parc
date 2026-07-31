#!/usr/bin/env python3
"""Assign sessions to days based on activity windows from discovery JSON."""
import json
import os
from datetime import datetime

INVEST_DIR = os.path.dirname(os.path.abspath(__file__))
days = ["2026-07-21","2026-07-22","2026-07-23","2026-07-24","2026-07-25","2026-07-26","2026-07-27"]

sessions = []
for name,f in [('pi','pi-discovery.json'),('codex','codex-discovery.json'),('claude-code','claude-code-discovery.json')]:
    try:
        for s in json.load(open(os.path.join(INVEST_DIR,'results',f))):
            s['_framework'] = name
            sessions.append(s)
    except Exception as e:
        print(f"{name}: {e}")

def parse(ts):
    if not ts: return None
    ts = ts.replace('Z','+00:00')
    try:
        return datetime.fromisoformat(ts)
    except:
        return None

day_sessions = {d:[] for d in days}
for s in sessions:
    started = parse(s.get('started_at'))
    last = parse(s.get('last_activity_at'))
    if not started: continue
    end = last or started
    for d in days:
        day_start = datetime.fromisoformat(d+'T00:00:00+00:00')
        day_end = datetime.fromisoformat(d+'T23:59:59+00:00')
        if started <= day_end and end >= day_start:
            day_sessions[d].append(s)

summary = {}
for d in days:
    fw = {}
    for s in day_sessions[d]:
        fw[s['_framework']] = fw.get(s['_framework'],0)+1
    summary[d] = {'count': len(day_sessions[d]), 'frameworks': fw, 'sessions': day_sessions[d]}
    print(f"{d}: {len(day_sessions[d])} sessions  {fw}")

# Save full assignment
with open(os.path.join(INVEST_DIR,'results','day-assignment.json'),'w') as fh:
    # serialize sessions with key fields
    out = {}
    for d in days:
        out[d] = []
        for s in day_sessions[d]:
            out[d].append({
                'id': s.get('id'),
                'framework': s['_framework'],
                'model': s.get('model'),
                'title': s.get('title'),
                'cwd': s.get('cwd'),
                'started_at': s.get('started_at'),
                'last_activity_at': s.get('last_activity_at'),
                'source_path': s.get('source_path'),
            })
    json.dump(out, fh, indent=2)
print("\nSaved day-assignment.json")
