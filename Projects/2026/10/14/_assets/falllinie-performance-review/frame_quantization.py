#!/usr/bin/env python3
"""Re-analyse Falllinie frame CSVs as a mixture of display-refresh multiples.

Reads the committed frames.csv files from the spike repository's ticket evidence
and reports, per case, the share of post-warmup intervals that land in one,
two or more 16.667 ms refresh periods, plus conditional stage means for
"fast" (<25 ms) and "slow" (>=25 ms) frames.

Usage: frame_quantization.py <spike-repo-root> <output-json>
"""
import csv
import json
import statistics
import sys
from pathlib import Path

PERIOD = 1000.0 / 60.0
WARMUP = 60

CASES = {
    # label: relative path from ttmp/
    "AUDIO003 live, direct callback": "2026/10/13/FALLLINIE-AUDIO-003--buffered-native-audio-worker-and-callback-deadline-qualification/scripts/target/direct/frames.csv",
    "AUDIO003 live, buffered audio": "2026/10/13/FALLLINIE-AUDIO-003--buffered-native-audio-worker-and-callback-deadline-qualification/scripts/target/buffered/frames.csv",
    "PERF004 static dual, queries off": "2026/10/13/FALLLINIE-PERF-004--gl-pass-measurement-and-evidence-driven-native-optimization/scripts/evidence/target/01-static-off/frames.csv",
    "PERF004 static dual 512x384": "2026/10/13/FALLLINIE-PERF-004--gl-pass-measurement-and-evidence-driven-native-optimization/scripts/evidence/target/05-static-res/frames.csv",
    "PERF004 live dual, queries off": "2026/10/13/FALLLINIE-PERF-004--gl-pass-measurement-and-evidence-driven-native-optimization/scripts/evidence/target/07-live-off/frames.csv",
    "TRACE005 live baseline (audio muted)": "2026/10/13/FALLLINIE-TRACE-005--cpu-gpu-driver-and-scheduler-attribution-with-perf-ftrace-and-ebpf/scripts/evidence/target-20261014T020124Z/01-baseline/frames.csv",
    "TRACE005 live closing baseline": "2026/10/13/FALLLINIE-TRACE-005--cpu-gpu-driver-and-scheduler-attribution-with-perf-ftrace-and-ebpf/scripts/evidence/target-20261014T020124Z/08-baseline/frames.csv",
    "Mali counters live normal": "2026/10/13/FALLLINIE-PERF-004--gl-pass-measurement-and-evidence-driven-native-optimization/scripts/03-mali-counters/evidence/target-20261014T024712Z/03-live/frames.csv",
    "Mali counters live post-bypass": "2026/10/13/FALLLINIE-PERF-004--gl-pass-measurement-and-evidence-driven-native-optimization/scripts/03-mali-counters/evidence/target-20261014T024712Z/04-bypass/frames.csv",
    "PMU live, audio disabled (opening)": "2026/10/13/FALLLINIE-TRACE-005--cpu-gpu-driver-and-scheduler-attribution-with-perf-ftrace-and-ebpf/scripts/10-cpu-pmu/evidence/target-20261014T144623Z/01-none/frames.csv",
    "PMU live, audio disabled (closing)": "2026/10/13/FALLLINIE-TRACE-005--cpu-gpu-driver-and-scheduler-attribution-with-perf-ftrace-and-ebpf/scripts/10-cpu-pmu/evidence/target-20261014T144623Z/08-none/frames.csv",
    "Range draws off (01)": "2026/10/13/FALLLINIE-TRACE-005--cpu-gpu-driver-and-scheduler-attribution-with-perf-ftrace-and-ebpf/scripts/13-index-ranges/evidence/target-20261014T154415Z/01-range0/frames.csv",
    "Range draws on (02)": "2026/10/13/FALLLINIE-TRACE-005--cpu-gpu-driver-and-scheduler-attribution-with-perf-ftrace-and-ebpf/scripts/13-index-ranges/evidence/target-20261014T154415Z/02-range1/frames.csv",
    "Replay 384x288 dual (opening ref)": "2026/10/14/FALLLINIE-GPU-006--repeatable-gpu-workload-and-resolution-view-count-scaling/scripts/evidence/target-20261014T180649Z/01-384x288-v2-fps0/frames.csv",
    "Replay 256x192 dual": "2026/10/14/FALLLINIE-GPU-006--repeatable-gpu-workload-and-resolution-view-count-scaling/scripts/evidence/target-20261014T180649Z/03-256x192-v2-fps0/frames.csv",
    "Replay 384x288 single": "2026/10/14/FALLLINIE-GPU-006--repeatable-gpu-workload-and-resolution-view-count-scaling/scripts/evidence/target-20261014T180649Z/04-384x288-v1-fps0/frames.csv",
    "Replay 512x384 single": "2026/10/14/FALLLINIE-GPU-006--repeatable-gpu-workload-and-resolution-view-count-scaling/scripts/evidence/target-20261014T180649Z/05-512x384-v1-fps0/frames.csv",
    "Replay 512x384 dual": "2026/10/14/FALLLINIE-GPU-006--repeatable-gpu-workload-and-resolution-view-count-scaling/scripts/evidence/target-20261014T180649Z/06-512x384-v2-fps0/frames.csv",
    "Replay 384x288 dual, paced 60": "2026/10/14/FALLLINIE-GPU-006--repeatable-gpu-workload-and-resolution-view-count-scaling/scripts/evidence/target-20261014T180649Z/08-384x288-v2-fps60/frames.csv",
    "GPU007 512 dual baseline": "2026/10/14/FALLLINIE-GPU-007--replay-controlled-scene-and-post-shader-sensitivity/scripts/evidence/target-20261014T191037Z/01-baseline/frames.csv",
    "GPU007 512 dual post-copy": "2026/10/14/FALLLINIE-GPU-007--replay-controlled-scene-and-post-shader-sensitivity/scripts/evidence/target-20261014T191037Z/02-post-copy/frames.csv",
    "GPU007 512 dual scene-flat": "2026/10/14/FALLLINIE-GPU-007--replay-controlled-scene-and-post-shader-sensitivity/scripts/evidence/target-20261014T191037Z/03-scene-flat/frames.csv",
    "GPU007 512 dual both": "2026/10/14/FALLLINIE-GPU-007--replay-controlled-scene-and-post-shader-sensitivity/scripts/evidence/target-20261014T191037Z/04-both/frames.csv",
    "GPU008 512 dual original": "2026/10/14/FALLLINIE-GPU-008--shadow-footprint-rejection-and-fidelity-bounded-scene-optimization/scripts/evidence/target-20261014T194947Z/01-original/frames.csv",
    "GPU008 512 dual shadows off": "2026/10/14/FALLLINIE-GPU-008--shadow-footprint-rejection-and-fidelity-bounded-scene-optimization/scripts/evidence/target-20261014T194947Z/02-off/frames.csv",
    "GPU008 512 dual bounds": "2026/10/14/FALLLINIE-GPU-008--shadow-footprint-rejection-and-fidelity-bounded-scene-optimization/scripts/evidence/target-20261014T194947Z/03-bounds/frames.csv",
}

STAGES = ["events_ms", "physics_ms", "player_ms", "top_submit_ms", "top_swap_ms",
          "bottom_submit_ms", "bottom_swap_ms", "pace_wait_ms"]


def load(path):
    with open(path, newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if int(r["frame"]) >= WARMUP]
    return rows


def fnum(row, key):
    value = row.get(key)
    if value in (None, ""):
        return None
    return float(value)


def summarize(rows):
    iv = [float(r["interval_ms"]) for r in rows]
    n = len(iv)
    one = sum(1 for x in iv if x < 25.0)
    two = sum(1 for x in iv if 25.0 <= x < 41.667)
    more = n - one - two
    near1 = sum(1 for x in iv if abs(x - PERIOD) <= 1.5)
    near2 = sum(1 for x in iv if abs(x - 2 * PERIOD) <= 1.5)
    mean = statistics.fmean(iv)
    # Mean predicted if every interval were exactly k refresh periods.
    k_mean = statistics.fmean(max(1, round(x / PERIOD)) for x in iv) * PERIOD
    out = {
        "n": n,
        "mean_ms": round(mean, 4),
        "median_ms": round(statistics.median(iv), 4),
        "share_one_period_lt25": round(one / n, 4),
        "share_two_periods_25_41": round(two / n, 4),
        "share_more_ge41": round(more / n, 4),
        "share_within_1p5_of_16p67": round(near1 / n, 4),
        "share_within_1p5_of_33p33": round(near2 / n, 4),
        "quantized_mean_ms": round(k_mean, 4),
        "fps_equivalent": round(1000.0 / mean, 2),
    }
    fast = [r for r in rows if float(r["interval_ms"]) < 25.0]
    slow = [r for r in rows if float(r["interval_ms"]) >= 25.0]
    for label, group in (("fast", fast), ("slow", slow)):
        stage_means = {}
        for s in STAGES:
            vals = [v for v in (fnum(r, s) for r in group) if v is not None]
            if vals:
                stage_means[s] = round(statistics.fmean(vals), 4)
        out[f"{label}_stage_means"] = stage_means
    return out


def main():
    root = Path(sys.argv[1]) / "ttmp"
    results = {}
    for label, rel in CASES.items():
        path = root / rel
        if not path.exists():
            results[label] = {"missing": rel}
            continue
        results[label] = {"source": rel, **summarize(load(path))}
    Path(sys.argv[2]).write_text(json.dumps(results, indent=2))
    hdr = f"{'case':42s} {'n':>5s} {'mean':>7s} {'1x':>6s} {'2x':>6s} {'>2x':>6s} {'@16.7':>6s} {'@33.3':>6s} {'qmean':>7s}"
    print(hdr)
    for label, r in results.items():
        if "missing" in r:
            print(f"{label:42s} MISSING")
            continue
        print(f"{label:42s} {r['n']:5d} {r['mean_ms']:7.3f} {r['share_one_period_lt25']:6.3f} "
              f"{r['share_two_periods_25_41']:6.3f} {r['share_more_ge41']:6.3f} "
              f"{r['share_within_1p5_of_16p67']:6.3f} {r['share_within_1p5_of_33p33']:6.3f} {r['quantized_mean_ms']:7.3f}")


if __name__ == "__main__":
    main()
