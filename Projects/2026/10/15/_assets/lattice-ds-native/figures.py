#!/usr/bin/env python3
"""Figures for the Lattice DS native report. Usage: figures.py LATTICE_DS_REPO OUT_DIR
Reads the DSUI-001 evidence files; writes SVG figures. Palette validated with the dataviz validator."""
import glob, json, re, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
SURFACE, INK, INK2, GRID, S1, S2 = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df', '#2a78d6', '#eb6834'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.facecolor': SURFACE, 'figure.facecolor': SURFACE,
                     'savefig.facecolor': SURFACE, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'svg.fonttype': 'none'})
repo, out = Path(sys.argv[1]), Path(sys.argv[2])
ev = Path(glob.glob(str(repo / 'ttmp/2026/10/15/DSUI-001*/scripts/evidence'))[0])
def screen(path, name): return next(s for s in json.loads(Path(path).read_text())['screens'] if s['screen'] == name)
def jsonl(path, name): return next(json.loads(l) for l in Path(path).read_text().splitlines() if l.strip() and json.loads(l)['screen'] == name)

# Figure 1: the robots page (508 ops) per implementation on the device, ms per frame (median)
q = screen(ev / 'device-rgdsplus-qjs-pinned-run1.json', 'robots')
v8 = screen(ev / 'device-rgdsplus-node-unpinned.json', 'robots')
v8r = screen(ev / 'device-rgdsplus-node-unpinned.json', 'robots-reused-tree')
proto = jsonl(ev / 'device-rgdsplus-cpp-proto-bench.jsonl', 'robots')
core = jsonl(ev / 'phase1/device-rgdsplus-core-bench.jsonl', 'robots')
enc = screen(ev / 'device-rgdsplus-node-build-encode.json', 'robots')
rows = [('lui.js in QuickJS-ng', q['gl_path_median_ms']), ('lui.js in V8 (Node 24)', v8['gl_path_median_ms']),
        ('lui.js in V8, tree reused', v8r['gl_path_median_ms']),
        ('JS build + encode (V8)\n+ lattice-core (C++)', enc['build_med'] + enc['encode_med'] + core['total_med']),
        ('C++ prototype', proto['total_med']), ('lattice-core (C++)', core['total_med'])]
fig, ax = plt.subplots(figsize=(8.2, 3.4))
ys = list(range(len(rows)))[::-1]
ax.barh(ys, [r[1] for r in rows], color=S1, height=0.58)
for y, (lab, v) in zip(ys, rows): ax.text(v + 0.5, y, f'{v:.2f} ms', va='center', color=INK, fontsize=9)
ax.set_yticks(ys, [r[0] for r in rows]); ax.set_xlabel('ms per frame on the Cortex-A55 (median), robots page: 94 nodes, 508 ops')
ax.axvline(33.3, color=INK2, lw=1, ls=(0, (3, 3))); ax.text(33.0, ys[0] + 0.45, '33 ms = one 30 fps frame', ha='right', color=INK2, fontsize=8.5)
ax.grid(axis='x', color=GRID, lw=0.8); ax.set_axisbelow(True); ax.set_xlim(0, 47)
fig.tight_layout(); fig.savefig(out / '01-robots-page-cost.svg')

# Figure 2: GPU time per screen on the Mali-G52, ablation of the two fixes
abl = {}
for line in (ev / 'phase2/device-ablation.txt').read_text().splitlines():
    m = re.match(r'^(none|discard|nofold|discard,nofold): .*gpu_top p50=([\d.]+).*gpu_bottom p50=([\d.]+)', line)
    if m: abl[m.group(1)] = (float(m.group(2)), float(m.group(3)))
cfg = [('discard,nofold', 'discard clip +\nbackground quad'), ('nofold', 'background quad\nonly'), ('discard', 'discard clip\nonly'), ('none', 'neither\n(shipped)')]
fig, ax = plt.subplots(figsize=(7.6, 3.3))
w = 0.36
for i, (k, lab) in enumerate(cfg):
    t, b = abl[k]
    ax.bar(i - w / 2 - 0.01, t, w, color=S1, label='top screen (board)' if i == 0 else None)
    ax.bar(i + w / 2 + 0.01, b, w, color=S2, label='bottom screen (robots)' if i == 0 else None)
    ax.text(i - w / 2 - 0.01, t + 0.08, f'{t:.2f}', ha='center', fontsize=8.5, color=INK)
    ax.text(i + w / 2 + 0.01, b + 0.08, f'{b:.2f}', ha='center', fontsize=8.5, color=INK)
ax.set_xticks(range(len(cfg)), [c[1] for c in cfg]); ax.set_ylabel('GPU ms per screen (p50)')
ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True); ax.legend(frameon=False, loc='upper right')
fig.tight_layout(); fig.savefig(out / '02-mali-gpu-ablation.svg')
print('wrote', out)
