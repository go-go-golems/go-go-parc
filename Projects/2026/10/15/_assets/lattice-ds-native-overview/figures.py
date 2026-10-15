#!/usr/bin/env python3
"""Figure for the Lattice DS Native overview report: every device budget of the design guide (8.9) against its
final measurement, as a fraction of the budget. Usage: figures.py OUT_DIR. Values are taken from the DSUI-001
evidence files named in provenance.json; each bar is labelled with its measured value and budget."""
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
SURFACE, INK, INK2, GRID, OK, OVER = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df', '#2a78d6', '#eb6834'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.facecolor': SURFACE, 'figure.facecolor': SURFACE,
                     'savefig.facecolor': SURFACE, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'svg.fonttype': 'none'})
out = Path(sys.argv[1])
rows = [  # label, measured, budget, unit
    ('top screen per frame (p50, race)', 2.19, 4.0, 'ms'),
    ('GPU per screen (p50)', 1.83, 2.0, 'ms'),
    ('start-up to both screens (cold)', 0.905, 1.0, 's'),
    ('memory, peak over a race series', 140.3, 150e6 / 2**20, 'MiB'),
    ('CPU temperature after 10 min (max)', 48.3, 70.0, '°C'),
    ('bottom page per render (p50)', 5.55, 3.0, 'ms'),
]
fig, ax = plt.subplots(figsize=(8.4, 3.4))
ys = list(range(len(rows)))[::-1]
for y, (lab, v, b, u) in zip(ys, rows):
    f = v / b
    ax.barh(y, f, color=OK if f <= 1 else OVER, height=0.56)
    ax.text(0.02, y, f'{v:g} / {b:.4g} {u}', va='center', fontsize=8.5, color='#ffffff')
ax.axvline(1, color=INK2, lw=1, ls=(0, (3, 3))); ax.text(1.0, ys[0] + 0.55, 'budget', ha='center', fontsize=8.5, color=INK2)
ax.set_yticks(ys, [r[0] for r in rows]); ax.set_xlabel('measured / budget (device, RG DS Plus)'); ax.set_xlim(0, 2.3)
ax.grid(axis='x', color=GRID, lw=0.8); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(out / '01-budget-scorecard.svg')
print('wrote', out)
