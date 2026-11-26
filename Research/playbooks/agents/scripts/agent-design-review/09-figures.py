#!/usr/bin/env python3
"""Small-multiple bar charts: one panel per measure, items on the x axis, one bar per round.

Usage: python3 09-figures.py <scores.json> <blind-key.json> <out.png> [--order r1,r2,r3] [--labels "Baseline|Revised brief|Self-review"]
Panels: words, judge over_engineering (0-10), judge fitness (0-10). Colors are the dataviz reference categorical slots
1-3 (validated together: worst adjacent CVD dE 12.6); slots 2 and 3 are below 3:1 on white, so table the values too.
"""
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

scores_path, key_path, out = sys.argv[1:4]
opts = dict(zip(sys.argv[4::2], sys.argv[5::2]))
key = {k["name"]: k for k in json.load(open(key_path))}
scores = json.load(open(scores_path))
rows = [{**s, **{"item": key[s["doc"]].get("item") or key[s["doc"]].get("id"), "round": key[s["doc"]]["round"], "words": key[s["doc"]]["words"]}} for s in scores]
rounds = opts.get("--order", ",".join(dict.fromkeys(r["round"] for r in rows))).split(",")
labels = opts.get("--labels", "|".join(rounds)).split("|")
items = sorted({r["item"] for r in rows})
colors = ["#257de0", "#f47230", "#00b894", "#f2a600", "#ee7fac"]
TEXT, TEXT2, GRID = "#191919", "#666666", "#e6e6e6"
panels = [("words", "Words in the document", None), ("over_engineering", "Judge: over-engineering (0-10)", 10), ("fitness", "Judge: fitness for purpose (0-10)", 10)]
fig, axes = plt.subplots(1, len(panels), figsize=(4.4 * len(panels), 4.2), dpi=150)
w = 0.8 / len(rounds)
for ax, (field, title, ymax) in zip(axes, panels):
    for i, rd in enumerate(rounds):
        xs = [j + (i - (len(rounds) - 1) / 2) * w for j in range(len(items))]
        ys = [next((float(r[field]) for r in rows if r["item"] == it and r["round"] == rd), 0) for it in items]
        ax.bar(xs, ys, width=w * 0.92, color=colors[i % len(colors)], label=labels[i] if i < len(labels) else rd, edgecolor="white", linewidth=1.5)
    ax.set_xticks(range(len(items))); ax.set_xticklabels(items, fontsize=8, rotation=30 if len(items) > 6 else 0)
    ax.set_title(title, loc="left", color=TEXT, fontsize=11)
    if ymax: ax.set_ylim(0, ymax)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(GRID)
    ax.tick_params(colors=TEXT2, labelsize=9); ax.yaxis.grid(True, color=GRID, linewidth=0.8); ax.set_axisbelow(True)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="upper center", ncol=len(rounds), frameon=False, fontsize=10, labelcolor=TEXT, bbox_to_anchor=(0.5, 1.02))
fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig(out, facecolor="white"); print("wrote", out)
