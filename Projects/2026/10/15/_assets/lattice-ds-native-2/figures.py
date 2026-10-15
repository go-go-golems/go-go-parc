#!/usr/bin/env python3
"""Figures for the Lattice DS native report, part 2 (shell and V8 layer). Usage: figures.py LATTICE_DS_REPO OUT_DIR
Reads the DSUI-001 evidence files; writes SVG figures. Palette: dataviz reference slots 1-4, validated
(validate_palette.js, light): all hard checks pass; slots 3-4 below 3:1 contrast, so every segment is labelled."""
import glob, json, re, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
SURFACE, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
C = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.facecolor': SURFACE, 'figure.facecolor': SURFACE,
                     'savefig.facecolor': SURFACE, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'svg.fonttype': 'none'})
repo, out = Path(sys.argv[1]), Path(sys.argv[2])
ev = Path(glob.glob(str(repo / 'ttmp/2026/10/15/DSUI-001*/scripts/evidence'))[0])
def kv(line, key):   # "key_p50=1.2 p95=3.4" -> (1.2, 3.4)
    m = re.search(key + r'_p50=([\d.]+) p95=([\d.]+)', line); return float(m.group(1)), float(m.group(2))
def grep(path, pat): return [l for l in Path(path).read_text().splitlines() if re.search(pat, l)]
def stacked(ax, ys, rows, labels, minlab=0.25):
    for y, vals in zip(ys, rows):
        x = 0
        for i, v in enumerate(vals):
            ax.barh(y, v, left=x, color=C[i], height=0.56, edgecolor=SURFACE, linewidth=2, label=labels[i] if y == ys[0] else None)
            if v >= minlab: ax.text(x + v / 2, y, f'{v:.2f}', ha='center', va='center', fontsize=8, color=INK)
            x += v
        ax.text(x + 0.08, y, f'{x:.2f} ms', va='center', fontsize=9, color=INK)

# Figure 1: robots page on the device, JavaScript description to laid-out page, p50
node = next(s for s in json.loads((ev / 'device-rgdsplus-node-build-encode.json').read_text())['screens'] if s['screen'] == 'robots')
core = next(json.loads(l) for l in (ev / 'phase1/device-rgdsplus-core-bench.jsonl').read_text().splitlines() if l.strip() and json.loads(l)['screen'] == 'robots')
old = grep(ev / 'phase4/device-js-dev1-old-encoder-js.log', r'jsbench robots')[-1]
new = grep(ev / 'phase4/device-js-dev2-js.log', r'jsbench robots')[-1]
cpp = lambda l: kv(l, 'decode')[0] + kv(l, 'layout')[0] + kv(l, 'paint')[0]
rows = [('Node 24 (V8 13.6),\nsketch encoder (Phase 0)', [node['build_med'], node['encode_med'], core['total_med']]),
        ('embedded V8 10.2,\nfirst wire v1 encoder', [kv(old, 'build')[0], kv(old, 'encode')[0], cpp(old)]),
        ('embedded V8 10.2,\nrewritten encoder', [kv(new, 'build')[0], kv(new, 'encode')[0], cpp(new)])]
fig, ax = plt.subplots(figsize=(8.4, 3.2))
ys = list(range(len(rows)))[::-1]
stacked(ax, ys, [r[1] for r in rows], ['JS builders (lui.js)', 'JS encode (wire)', 'C++ decode + layout + paint'])
ax.set_yticks(ys, [r[0] for r in rows]); ax.set_xlabel('ms on the Cortex-A55 (p50), robots page: 94 nodes, 508 ops')
ax.grid(axis='x', color=GRID, lw=0.8); ax.set_axisbelow(True); ax.set_xlim(0, 6.6)
ax.legend(frameon=False, loc='lower right', fontsize=8.5)
fig.tight_layout(); fig.savefig(out / '01-robots-page-js-cost.svg')

# Figure 2: the bottom screen through the shell, C++ pages vs JavaScript pages (real input, p50), with the JS layer split
nat = grep(ev / 'phase4/device-pf-native-perf.log', r'^CTL perf bottom detail')[-1]
nat_ui = grep(ev / 'phase4/device-pf-native-perf.log', r'^CTL perf bottom renders')[-1]
js_ui = grep(ev / 'phase4/device-pf-js2-perf.log', r'^CTL perf bottom renders')[-1]
js_det = grep(ev / 'phase4/device-pf-js2-perf.log', r'^CTL perf bottom detail')[-1]
jsp = grep(ev / 'phase4/device-pf-js2-perf.log', r'^CTL jsperf')[-1]
split = {k: float(re.search(k + r'=([\d.]+)/', jsp).group(1)) for k in ('build', 'data', 'encode', 'adopt')}
nat_rest = kv(nat_ui, 'ui_ms')[0]
js_rest = max(0.0, kv(js_ui, 'ui_ms')[0] - sum(split.values()))
fig, ax = plt.subplots(figsize=(8.4, 2.6))
ys = [1, 0]
stacked(ax, ys, [[0, 0, 0, nat_rest], [split['build'] + split['data'], split['encode'], split['adopt'], js_rest]],
        ['JS builders + app data', 'JS encode', 'C++ decode + keys', 'C++ build/layout/paint/hits, focus ring'])
ax.set_yticks(ys, ['C++ pages', 'JavaScript pages\n(apps/demo/pages.js)']); ax.set_xlabel('bottom-screen UI-thread ms per render on the device (p50, real button input)')
ax.grid(axis='x', color=GRID, lw=0.8); ax.set_axisbelow(True); ax.set_xlim(0, 8.2)
ax.legend(frameon=False, loc='upper right', fontsize=8, ncol=2, bbox_to_anchor=(1.0, 1.32))
fig.tight_layout(); fig.savefig(out / '02-bottom-screen-cpp-vs-js.svg')

# Figure 3: resident memory through the device gate (VmRSS is in KiB; plotted in MiB)
mem = {}
for l in (ev / 'phase4/device-js-dev2-mem.txt').read_text().splitlines():
    m = re.match(r'^(\S+) .*VmRSS: (\d+) kB', l)
    if m: mem[m.group(1)] = int(m.group(2)) / 1024
stages = [('nojs-8s', 'no V8'), ('js-start', 'V8 loaded'), ('js-live-30s', 'live card, 30 s'), ('js-after-drive', 'after cards,\nrecipes, drive'), ('js-after-bench', 'after jsbench\n(allocation-heavy)')]
fig, ax = plt.subplots(figsize=(8.4, 3.0))
xs = range(len(stages))
ax.bar(xs, [mem[k] for k, _ in stages], color=C[0], width=0.56)
for x, (k, _) in zip(xs, stages): ax.text(x, mem[k] - 9, f'{mem[k]:.1f}', ha='center', fontsize=9, color='#ffffff')
ax.axhline(120, color=INK2, lw=1, ls=(0, (3, 3))); ax.text(-0.45, 123, '120 MiB target', ha='left', fontsize=8.5, color=INK2)
ax.set_xticks(list(xs), [s[1] for s in stages]); ax.set_ylabel('RSS (MiB)'); ax.set_ylim(0, 160)
ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(out / '03-rss.svg')

# Figure 4: Phase 3, bottom-screen UI time p95 across the fixes
p3 = [(f, grep(ev / f'phase3/device-{f}-perf.log', r'^EXIT perf bottom')[-1]) for f in ('perf1', 'perf4', 'perf5')]
labels = ['first measurement', 'layout memo +\ncheap second scroll pass\n(+ window 1/2)', '+ virtual window\n1/4 screen']
fig, ax = plt.subplots(figsize=(7.4, 3.0))
vals = [kv(l, 'ui_ms')[1] for _, l in p3]
ax.bar(range(3), vals, color=C[0], width=0.5)
for i, v in enumerate(vals): ax.text(i, v - 0.45, f'{v:.2f} ms', ha='center', fontsize=9, color='#ffffff')
ax.axhline(3, color=INK2, lw=1, ls=(0, (3, 3))); ax.text(0.3, 3.12, '3 ms budget', ha='left', fontsize=8.5, color=INK2)
ax.set_xticks(range(3), labels); ax.set_ylabel('bottom UI ms per render (p95)')
ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(out / '04-phase3-bottom-p95.svg')
print('wrote', out)
