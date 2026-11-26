"""Regenerate the two-panel comparison from recorded evidence in the ticket."""
import argparse
from pathlib import Path
import json
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--sources", type=Path, default=Path(__file__).resolve().parents[1] / "sources",
                    help="Directory containing gb10-backend-timings.txt and shadow-query-probe.json")
base = parser.parse_args().sources
log = (base / "gb10-backend-timings.txt").read_text()
rows = re.findall(r"^([BKXV]-\d+)\s+(\d+) ms\s+(\d+) ms\s+(\d+) ms", log, re.M)
assert len(rows) == 4
jobs = json.loads((base / "shadow-query-probe.json").read_text())["workloads"]
fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.2), layout="constrained")
styles = [("#645a93", "Plain CUDA"), ("#197466", "OptiX")]
for i, (color, label) in enumerate(styles):
    axes[0].barh(np.arange(4) + (i - 0.5) * .33, [int(r[2+i]) for r in rows], .30, label=label, color=color)
for i, (key, label) in enumerate([("full", "Closest hit"), ("early", "First blocker")]):
    axes[1].barh(np.arange(4) + (i - 0.5) * .33, [j[key]["triangles"] for j in jobs], .30, label=label, color=styles[i][0])
for ax, labels, title, unit in zip(axes, [[r[0] for r in rows], [j["name"] for j in jobs]],
    ["Measured native render times", "Counted triangle tests on one mesh"],
    ["milliseconds per frame · GB10 · 256 spp", "triangle tests per grid of 9,216 rays · CPU probe"]):
    ax.set_yticks(range(len(labels)), labels)
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel(unit)
    ax.legend(frameon=False)
    ax.spines[["right", "top"]].set_visible(False)
fig.savefig(base / "query-costs.png", dpi=145)
