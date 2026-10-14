#!/usr/bin/env python3
"""Figures for the Falllinie performance review.

Usage: figures.py <spike-repo-root> <quantization.json> <counters_per_frame.json> <out-dir>
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3df"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
PERIOD = 1000.0 / 60.0

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.facecolor": SURFACE, "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none",
})


def style(ax):
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def fig_mixture(q, out):
    cases = [
        ("Live, audio muted (TRACE005)", "TRACE005 live baseline (audio muted)"),
        ("Live, audio disabled (PMU)", "PMU live, audio disabled (opening)"),
        ("Live, range draws on", "Range draws on (02)"),
        ("Live, post bypass (non-parity)", "Mali counters live post-bypass"),
        ("Replay 384×288 single", "Replay 384x288 single"),
        ("Replay 384×288 dual", "Replay 384x288 dual (opening ref)"),
        ("Replay 512×384 dual, original", "GPU008 512 dual original"),
        ("Replay 512×384 dual, shadow bounds", "GPU008 512 dual bounds"),
        ("Replay 512×384 dual, flat scene", "GPU007 512 dual scene-flat"),
    ]
    fig, ax = plt.subplots(figsize=(9.6, 4.4))
    style(ax)
    ax.grid(True, axis="x", color=GRID)
    ax.grid(False, axis="y")
    for i, (label, key) in enumerate(cases):
        r = q[key]
        one = r["share_one_period_lt25"] * 100
        slow = 100 - one
        y = len(cases) - 1 - i
        ax.barh(y, one, color=S1, height=0.62, edgecolor=SURFACE, linewidth=2)
        ax.barh(y, slow, left=one, color=S2, height=0.62, edgecolor=SURFACE, linewidth=2)
        ax.text(101.5, y, f"mean {r['mean_ms']:.2f} ms", va="center", color=INK, fontsize=9)
    ax.set_yticks(range(len(cases)))
    ax.set_yticklabels([c[0] for c in reversed(cases)], color=INK)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of post-warmup frame intervals (%)")
    ax.set_title("Share of frame intervals at or above 25 ms", loc="left", color=INK, fontsize=12)
    ax.legend(["interval < 25 ms", "interval ≥ 25 ms"], loc="upper center",
              bbox_to_anchor=(0.45, -0.14), ncol=2, frameon=False)
    fig.subplots_adjust(left=0.36, right=0.86, bottom=0.22, top=0.9)
    fig.savefig(out / "01-refresh-mixture.svg")
    plt.close(fig)


def load_intervals(path):
    with open(path, newline="") as fh:
        return [float(r["interval_ms"]) for r in csv.DictReader(fh) if int(r["frame"]) >= 60]


def fig_histograms(root, q, out):
    panels = [
        ("Live, audio muted (TRACE005)", "TRACE005 live baseline (audio muted)"),
        ("Live, audio disabled (PMU baseline)", "PMU live, audio disabled (opening)"),
        ("Replay 512×384 dual, original shadows", "GPU008 512 dual original"),
        ("Replay 512×384 dual, shadow bounds", "GPU008 512 dual bounds"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(8.6, 5.4), sharex=True)
    for ax, (title, key) in zip(axes.flat, panels):
        style(ax)
        iv = load_intervals(Path(root) / "ttmp" / q[key]["source"])
        n = len(iv)
        bins = [10 + 0.5 * i for i in range(61)]
        weights = [100.0 / n] * n
        ax.hist(iv, bins=bins, weights=weights, color=S1, edgecolor=SURFACE, linewidth=0.6)
        for k in (1, 2):
            ax.axvline(k * PERIOD, color=INK2, linestyle="--", linewidth=1)
        ax.set_title(title, loc="left", fontsize=10, color=INK)
        ax.set_xlim(10, 40)
        ax.text(0.98, 0.9, f"n={n}\nmean {q[key]['mean_ms']:.2f} ms", transform=ax.transAxes,
                ha="right", va="top", fontsize=8.5, color=INK2)
    for ax in axes[1]:
        ax.set_xlabel("Frame interval (ms); dashed: 16.67 and 33.33 ms")
    for ax in axes[:, 0]:
        ax.set_ylabel("% of intervals per 0.5 ms")
    fig.suptitle("Interval distributions from the committed frame CSVs", x=0.07, ha="left", color=INK, fontsize=12)
    fig.tight_layout()
    fig.savefig(out / "02-interval-histograms.svg")
    plt.close(fig)


def fig_cycles(c, out):
    pts = {"single": [], "dual": []}
    for r in c:
        if r["source"] != "replay-scaling" or not r["case"].startswith("cases/"):
            continue
        name = r["case"].split()[0].split("/")[1]
        size = name.split("-")[1]
        w, h = (int(v) for v in size.split("x"))
        views = "dual" if "-v2-" in name else "single"
        if name.startswith("07") or name.endswith("fps60"):
            continue
        pts[views].append((w * h / 1000.0, r["gpu_active_Mcy_per_frame"], size))
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    style(ax)
    budget = 800.0 / 60.0
    ax.axhline(budget, color=INK2, linestyle="--", linewidth=1)
    ax.text(10, budget + 0.25, "800 MHz × 16.67 ms = 13.33 M cycles", color=INK2, fontsize=8.5)
    for views, color in (("single", S1), ("dual", S2)):
        p = sorted(pts[views])
        xs = [a for a, _, _ in p]
        ys = [b for _, b, _ in p]
        ax.plot(xs, ys, color=color, linewidth=2, marker="o", markersize=8,
                markeredgecolor=SURFACE, markeredgewidth=2, label=f"{views} view")
        for x, y, s in p:
            ax.annotate(f"{s}: {y:.1f}", (x, y), textcoords="offset points", xytext=(6, -14 if views == "single" else 8),
                        fontsize=8.5, color=INK)
    ax.set_xlim(0, 215)
    ax.set_ylim(0, 21)
    ax.set_xlabel("Internal pixels per view (thousands)")
    ax.set_ylabel("GPU-active cycles per loop frame (millions)")
    ax.set_title("A large share of GPU time does not scale with internal resolution", loc="left", color=INK, fontsize=12)
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.93))
    fig.tight_layout()
    fig.savefig(out / "03-gpu-cycles-per-frame.svg")
    plt.close(fig)


def fig_bytes(c, out):
    rows = []
    for r in c:
        if r["source"] == "replay-scaling" and r["case"].startswith("cases/0") and not r["case"].startswith("cases/07") and "fps60" not in r["case"]:
            name = r["case"].split()[0].split("/")[1]
            size = name.split("-")[1]
            views = "dual" if "-v2-" in name else "single"
            rows.append((views, int(size.split("x")[0]), f"{size}\n{views}", r["read_MB_per_frame"], r["write_MB_per_frame"]))
    rows.sort()
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    style(ax)
    ax.grid(False, axis="x")
    xs = range(len(rows))
    wbar = 0.38
    ax.bar([x - wbar / 2 for x in xs], [r[3] for r in rows], width=wbar, color=S1, edgecolor=SURFACE, linewidth=2, label="external reads")
    ax.bar([x + wbar / 2 for x in xs], [r[4] for r in rows], width=wbar, color=S2, edgecolor=SURFACE, linewidth=2, label="external writes")
    for x, r in zip(xs, rows):
        ax.text(x - wbar / 2, r[3] + 0.4, f"{r[3]:.1f}", ha="center", fontsize=8.5, color=INK)
        ax.text(x + wbar / 2, r[4] + 0.4, f"{r[4]:.1f}", ha="center", fontsize=8.5, color=INK)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([r[2] for r in rows], color=INK)
    ax.set_ylabel("MB per loop frame (whole device)")
    ax.set_title("Memory traffic per frame barely follows internal resolution", loc="left", color=INK, fontsize=12)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(out / "04-bytes-per-frame.svg")
    plt.close(fig)


def main():
    root, qpath, cpath, out = sys.argv[1:5]
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    q = json.load(open(qpath))
    c = json.load(open(cpath))
    fig_mixture(q, out)
    fig_histograms(root, q, out)
    fig_cycles(c, out)
    fig_bytes(c, out)


if __name__ == "__main__":
    main()
