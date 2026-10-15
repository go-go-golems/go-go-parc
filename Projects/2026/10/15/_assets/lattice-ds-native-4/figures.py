#!/usr/bin/env python3
"""Figures for the Lattice DS native report, part 4 (performance hardening). Usage: figures.py LATTICE_DS_REPO OUT_DIR
Reads DSUI-001 evidence (phase5, phase6). Palette: dataviz reference slots 1-2, validated (light); lines 2 px,
legends present, lines directly labelled at their ends."""
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
def topui(path):
    v = None
    for l in Path(path).read_text().splitlines():
        m = re.search(r'^CTL perf top renders=\d+ .*ui_ms_p50=([\d.]+) p95=([\d.]+)', l)   # measured at the race's end
        if m: v = (float(m.group(1)), float(m.group(2)))
    return v
def samples(path):
    by = {}   # one sample per time: some files hold the soak's summary (first and last sample) before the series
    for l in Path(path).read_text().splitlines():
        m = re.match(r'^t=(\d+) cpu-thermal=(\d+) gpu-thermal=(\d+)\s+VmRSS: (\d+) kB', l)
        if m: by.setdefault(int(m.group(1)), (int(m.group(2)) / 1000, int(m.group(3)) / 1000, int(m.group(4)) / 1024))
    ts = sorted(by)
    return [x / 60 for x in ts], [by[x][2] for x in ts], [by[x][0] for x in ts], [by[x][1] for x in ts]

# Figure 1: top-screen UI time per frame during a race, performance governor, three steps
steps = [('Phase 5:\nview in JavaScript', topui(ev / 'phase5/device-ar1-arena.log')),
         ('+ hud cached\nby key', topui(ev / 'phase6/device-ar2-hudcache.log')),
         ('+ dynamic layer\nin C++', topui(ev / 'phase6/device-ar4-nativedyn.log'))]
fig, ax = plt.subplots(figsize=(7.6, 3.2))
for i, (lab, (p50, p95)) in enumerate(steps):
    ax.bar(i, p50, 0.52, color=S1)
    ax.plot([i, i], [p50, p95], color=INK2, lw=1); ax.plot([i - 0.06, i + 0.06], [p95, p95], color=INK2, lw=1)
    ax.text(i, p95 + 0.25, f'p50 {p50:.2f}\np95 {p95:.2f}', ha='center', fontsize=8.5, color=INK)
ax.axhline(4, color=INK2, lw=1, ls=(0, (3, 3))); ax.text(2.42, 4.15, '4 ms budget', ha='right', fontsize=8.5, color=INK2)
ax.set_xticks(range(3), [s[0] for s in steps]); ax.set_ylabel('top-screen UI ms per frame'); ax.set_ylim(0, 12.5)
ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(out / '01-top-screen-steps.svg')

# Figure 2: RSS over ten minutes of back-to-back races, before and after the memory changes
fig, ax = plt.subplots(figsize=(7.6, 3.2))
S3 = '#1baf7a'   # dataviz reference slot 3 (validated with slots 1-2; directly labelled)
for path, col, lab in [(ev / 'phase6/device-soak1-10min-samples.txt', S2, '16 MB young generation, no GC relief'),
                       (ev / 'phase6/device-soak3-10min-memrelief-samples.txt', S1, '6 MB young generation, GC relief whenever idle'),
                       (ev / 'phase6/device-soak-5min-young6mb.txt', S3, 'shipped: 6 MB, GC relief between races (5 min)')]:
    t, rss, _, _ = samples(path)
    ax.plot(t, rss, color=col, lw=2, label=lab)
    ax.text(t[-1] + 0.1, rss[-1], f'{rss[-1]:.0f}', va='center', fontsize=8.5, color=INK)
budget = 150e6 / 2**20   # the guide's 150 MB, in MiB
ax.axhline(budget, color=INK2, lw=1, ls=(0, (3, 3))); ax.text(5.6, budget + 1.8, 'budget: 150 MB = 143 MiB', ha='left', fontsize=8.5, color=INK2)
ax.set_xlabel('minutes, races back to back'); ax.set_ylabel('RSS (MiB)'); ax.set_ylim(80, 185); ax.set_xlim(0, 10.8)
ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True); ax.legend(frameon=False, loc='lower right', fontsize=8.5)
fig.tight_layout(); fig.savefig(out / '02-rss-soak.svg')

# Figure 3: temperature over the first ten-minute soak (device starting cold)
t, _, cpu, gpu = samples(ev / 'phase6/device-soak1-10min-samples.txt')
fig, ax = plt.subplots(figsize=(7.6, 2.8))
ax.plot(t, cpu, color=S1, lw=2, label='CPU (cpu-thermal)'); ax.plot(t, gpu, color=S2, lw=2, label='GPU (gpu-thermal)')
ax.text(t[-1] + 0.1, cpu[-1] - 2.2, f'CPU {cpu[-1]:.1f} °C', fontsize=8.5, color=INK); ax.text(t[-1] + 0.1, gpu[-1] + 1.4, f'GPU {gpu[-1]:.1f} °C', fontsize=8.5, color=INK)
ax.axhline(70, color=INK2, lw=1, ls=(0, (3, 3))); ax.text(0.1, 66.5, '70 °C limit', fontsize=8.5, color=INK2)
ax.set_xlabel('minutes'); ax.set_ylabel('°C'); ax.set_ylim(30, 75); ax.set_xlim(0, 12)
ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True); ax.legend(frameon=False, loc='center right', fontsize=8.5)
fig.tight_layout(); fig.savefig(out / '03-temperature-soak.svg')
print('wrote', out)
