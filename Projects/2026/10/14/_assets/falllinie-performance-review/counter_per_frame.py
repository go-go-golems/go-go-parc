#!/usr/bin/env python3
"""Normalise published Mali counter rates by loop frame rate.

The published summaries deliberately avoid per-frame normalisation because the
counter window is narrower than the frame window. This script performs that
normalisation anyway, as an approximation, so that geometry and memory traffic
can be compared with a per-frame cost model. Results are estimates.

Usage: counter_per_frame.py <summary.json> [<summary.json> ...]
"""
import json
import sys


def walk(node, path=()):
    if isinstance(node, dict):
        if "rates_per_second" in node and ("loop_frames_per_second" in node or "mean_ms" in node):
            yield path, node
        for key, value in node.items():
            yield from walk(value, path + (str(key),))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, path + (str(index),))


def label(path, case):
    parts = []
    for key in ("render_size", "dual_screen", "fps_cap", "mode", "case", "name", "label"):
        if key in case:
            parts.append(f"{key}={case[key]}")
    return "/".join(path[-2:]) + (" " + " ".join(parts) if parts else "")


def main():
    rows = []
    for name in sys.argv[1:]:
        data = json.load(open(name))
        for path, case in walk(data):
            rates = case["rates_per_second"]
            fps = case.get("loop_frames_per_second") or 1000.0 / case["mean_ms"]
            gpu = rates.get("MaliGPUActiveCy")
            row = {
                "source": name.split("/")[-2],
                "case": label(path, case),
                "fps": round(fps, 2),
                "read_MB_per_frame": round(rates.get("MaliExtBusRdBy", 0) / fps / 1e6, 2),
                "write_MB_per_frame": round(rates.get("MaliExtBusWrBy", 0) / fps / 1e6, 2),
                "gpu_active_Mcy_per_frame": round(gpu / fps / 1e6, 2) if gpu else None,
                "frag_over_gpu": round(rates["MaliFragActiveCy"] / gpu, 3) if gpu and "MaliFragActiveCy" in rates else None,
                "nonfrag_over_gpu": round(rates["MaliNonFragActiveCy"] / gpu, 3) if gpu and "MaliNonFragActiveCy" in rates else None,
                "tiler_over_gpu": round(rates["MaliTilerActiveCy"] / gpu, 3) if gpu and "MaliTilerActiveCy" in rates else None,
            }
            rows.append(row)
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
