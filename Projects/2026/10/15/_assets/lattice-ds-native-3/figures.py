#!/usr/bin/env python3
"""Figure for the Lattice DS native report, part 3 (the arena). Usage: figures.py LATTICE_DS_REPO OUT_DIR
Reads DSUI-001 evidence: Phase 3 (C++ demo pages, device-perf5) and Phase 5 (the arena's JS view, device-ar1).
Palette: dataviz reference slots 1-2, validated with validate_palette.js (light); bars are directly labelled."""
import glob, re, sys
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
def exitperf(path, screen):
    for l in Path(path).read_text().splitlines():
        m = re.match(rf'^EXIT perf {screen} renders=\d+ ui_ms_p50=([\d.]+) p95=([\d.]+)', l)
        if m: v = (float(m.group(1)), float(m.group(2)))
    return v
p3 = ev / 'phase3/device-perf5-perf.log'; p5 = ev / 'phase5/device-ar1-arena.log'
groups = [('top screen\n(30 fps while robots move)', exitperf(p3, 'top'), exitperf(p5, 'top')),
          ('bottom screen\n(per page render)', exitperf(p3, 'bottom'), exitperf(p5, 'bottom'))]
fig, ax = plt.subplots(figsize=(8.0, 3.4))
w = 0.34
for i, (lab, c, j) in enumerate(groups):
    for k, (v, col, name) in enumerate([(c, S1, 'C++ pages (demo, Phase 3)'), (j, S2, "arena's view in V8 (Phase 5)")]):
        x = i + (k - 0.5) * (w + 0.03)
        ax.bar(x, v[0], w, color=col, label=name if i == 0 else None)
        ax.plot([x, x], [v[0], v[1]], color=INK2, lw=1)
        ax.plot([x - 0.05, x + 0.05], [v[1], v[1]], color=INK2, lw=1)
        ax.text(x, v[1] + 0.25, f'{v[0]:.2f}\np95 {v[1]:.2f}', ha='center', fontsize=8.5, color=INK)
ax.set_xticks(range(len(groups)), [g[0] for g in groups]); ax.set_ylabel('UI-thread ms per render (p50, whisker p95)')
ax.set_ylim(0, 12.5); ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True); ax.legend(frameon=False, loc='upper right')
fig.tight_layout(); fig.savefig(out / '01-ui-time-cpp-vs-js-view.svg')
print('wrote', out)
