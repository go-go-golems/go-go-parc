#!/usr/bin/env python3
"""Render measured host batches as a self-contained SVG; standard library only."""
import csv
import pathlib
import statistics

root = pathlib.Path(__file__).resolve().parent
rows = list(csv.DictReader((root / "singularity-local-copy-move.csv").open()))
assert len(rows) == 30 and sum(int(r["completed"]) for r in rows) == 30000
parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 490" role="img" aria-labelledby="title desc">',
         '<title id="title">Measured copy and move batch durations</title>',
         '<desc id="desc">Five batches of one thousand host round trips per size and mode. Dots are observed batches; connected squares are medians. Debug build, not ESP32 timing.</desc>',
         '<rect width="760" height="490" fill="#ffffff"/>',
         '<g font-family="sans-serif" fill="#172033">',
         '<text x="70" y="30" font-size="20">Local owner handoff versus explicit copying</text>',
         '<text x="70" y="53" font-size="13">Elapsed milliseconds per 1,000 completed host round trips</text>']
def y(ms):
    return 370 - ms * 5.6
for tick in range(0, 51, 10):
    yy = y(tick)
    parts.append(f'<path d="M70 {yy} H710" stroke="#dbe1e8"/>')
    parts.append(f'<text x="55" y="{yy+5}" text-anchor="end" font-size="13">{tick}</text>')
xs = {16: 170, 64: 390, 128: 610}
for size, xx in xs.items():
    parts.append(f'<text x="{xx}" y="397" text-anchor="middle" font-size="14">{size} bytes</text>')
for mode, color, shift in (("move", "#1764a8", -15), ("copy", "#bb4d17", 15)):
    medians = []
    for size, xx in xs.items():
        samples = [int(r["elapsed_us"]) / 1000 for r in rows if r["mode"] == mode and int(r["bytes"]) == size]
        center = xx + shift
        median = statistics.median(samples)
        medians.append((center, y(median)))
        for i, value in enumerate(samples):
            parts.append(f'<circle cx="{center+(i-2)*5}" cy="{y(value):.3f}" r="3" fill="{color}" opacity="0.65"/>')
        parts.append(f'<rect x="{center-4}" y="{y(median)-4:.3f}" width="8" height="8" fill="{color}"/>')
        parts.append(f'<text x="{center}" y="{y(median)-14:.3f}" text-anchor="middle" font-size="12" fill="{color}">{median:.3f}</text>')
    points = ' '.join(f'{xx},{yy:.3f}' for xx, yy in medians)
    parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="1.5"/>')
parts += ['<text x="90" y="432" font-size="14" fill="#1764a8">Move: no payload handoff copies</text>',
          '<text x="390" y="432" font-size="14" fill="#bb4d17">Copy: two copies per round trip</text>',
          '<text x="70" y="458" font-size="12">Dots: five measured batches. Squares and labels: medians. No latency percentiles implied.</text>',
          '<text x="70" y="477" font-size="12">GNU C++ 13.3 Debug; uncontrolled affinity; move always precedes copy; no separate warmup.</text>',
          '</g></svg>']
output = root / 'singularity-local-copy-move.svg'
output.write_text('\n'.join(parts) + '\n')
print(output)
