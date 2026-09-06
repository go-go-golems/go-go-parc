#!/usr/bin/env python3
"""Reproduce the report's SVG figures using only Python's standard library.

Normal use: python3 singularity-rpc-figures.py
One-time import: add --import-source /path/to/esp32-s3-m5
Import refuses to overwrite existing evidence; figure regeneration is deterministic.
"""
import argparse
import csv
import html
import json
import pathlib
import statistics

HERE = pathlib.Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--import-source', type=pathlib.Path)
args = parser.parse_args()

def write_csv(path, rows, fields):
    with path.open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in rows)

if args.import_source:
    ticket = args.import_source / 'ttmp/2026/09/06/SINGULARITY-LORA-RPC--bounded-datagram-rpc-and-unreliable-link-semantics-for-the-singularity-lora-labs'
    load = lambda name: json.loads((ticket / 'analysis' / name).read_text())
    data = {'source_revision': '78862a6', 'normal_run': load('68-e-final-rpc/results.json'),
            'fault_run': load('71-e-extended-faults/results.json'),
            'firmware_provenance': load('73-e-explicit-transport-provenance.json'),
            'handoff_audit': load('74-final-handoff-audit.json')}
    data['trace_excerpts'] = {}
    for label in ('A', 'B'):
        lines = (ticket / f'analysis/71-e-extended-faults/{label}.txt').read_text().splitlines()
        data['trace_excerpts'][label] = [line for line in lines if any(marker in line for marker in (
            'RPC RESULT id=2 ', 'RPC RESULT id=5 ', 'RPC SERVER id=2 ', 'RPC DROP REPLY id=2 ',
            'LIVE TX RECOVERED', 'LIVE IDENTITY'))]
    with (HERE / 'singularity-rpc-evidence.json').open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')
    write_csv(HERE / 'singularity-rpc-normal-calls.csv', data['normal_run']['calls'],
              ['source', 'target', 'sf', 'id', 'service', 'outcome', 'attempts', 'elapsed_us', 'driver_busy', 'body'])
    write_csv(HERE / 'singularity-rpc-timing.csv', data['fault_run']['timings'],
              ['board', 'sf', 'bytes', 'expected_us', 'edge_us'])

def rows(name):
    with (HERE / name).open() as stream: return list(csv.DictReader(stream))

class Svg:
    def __init__(self, title, subtitle, height=480):
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img">',
                      '<rect width="100%" height="100%" fill="white"/>',
                      f'<title>{html.escape(title)}</title>']
        self.text(35, 32, title, 23, '#142536')
        self.text(35, 57, subtitle, 13)
    def text(self, x, y, text, size=12, color='#34495e', anchor='start'):
        self.parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="sans-serif" font-size="{size}" fill="{color}">{html.escape(str(text))}</text>')
    def line(self, x1, y1, x2, y2, color='#d9e0e5', dash=''):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-dasharray="{dash}"/>')
    def dot(self, x, y, color):
        self.parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.5" fill="{color}"/>')
    def save(self, name):
        (HERE / name).write_text('\n'.join(self.parts + ['</svg>']) + '\n')

calls = rows('singularity-rpc-normal-calls.csv')
assert len(calls) == 40 and all(row['outcome'] == row['attempts'] == '1' for row in calls)
svg = Svg('Real LoRa RPC: forty normal calls', '915 MHz / nominal BW500 / 0 dBm. Each point is one completed first-attempt call.')
for panel, sf in enumerate((7, 9)):
    data = [row for row in calls if int(row['sf']) == sf]
    assert len(data) == 20
    left, right, top, bottom = 75 + panel * 480, 480 + panel * 480, 110, 365
    y = lambda ms: bottom - ms / 400 * (bottom - top)
    for value in range(0, 401, 100):
        svg.line(left, y(value), right, y(value))
        svg.text(left - 10, y(value) + 4, value, anchor='end')
    svg.text(left, 93, f'SF{sf}: 20 calls', 17)
    svg.text(left, 390, 'Call within profile: A to B first 10; B to A next 10', 11)
    for index, row in enumerate(data):
        x = left + (index + .5) / 20 * (right - left)
        svg.dot(x, y(int(row['elapsed_us']) / 1000), '#087f8c' if row['source'] == 'A' else '#a43f7b')
    median = statistics.median(int(row['elapsed_us']) / 1000 for row in data)
    svg.line(left, y(median), right, y(median), '#566573', '5 4')
    svg.text(right, 414, f'Median {median:.1f} ms', 13, anchor='end')
svg.text(35, 440, 'Vertical axis: call latency (ms), including pacing, turnaround, FIFO work and scheduling.', 13)
svg.text(35, 461, 'This is an ordered bench sample, not a population latency distribution or pure RF airtime.', 12)
svg.save('singularity-rpc-normal-calls.svg')

timings = rows('singularity-rpc-timing.csv')
timings.sort(key=lambda row: int(row['sf']))
assert len(timings) == 30
svg = Svg('Calculated airtime and the physical completion edge', 'SetTx-request-to-DIO1 time minus calculated BW500 airtime; expanded vertical scale.')
left, right, top, bottom = 85, 950, 105, 360
y = lambda us: bottom - (us - 590) / 20 * (bottom - top)
for value in (590, 595, 600, 605, 610):
    svg.line(left, y(value), right, y(value))
    svg.text(left - 12, y(value) + 4, f'{value} us', anchor='end')
for index, row in enumerate(timings):
    delta = int(row['edge_us']) - int(row['expected_us'])
    assert 599 <= delta <= 604
    svg.dot(left + (index + .5) / 30 * (right - left), y(delta), '#087f8c' if row['sf'] == '7' else '#a43f7b')
svg.line(left + 20 / 30 * (right - left), top, left + 20 / 30 * (right - left), bottom, '#8c99a5', '4 4')
svg.text(230, 390, 'SF7: 20 observations', 14)
svg.text(725, 390, 'SF9: 10 observations', 14)
svg.text(85, 422, 'Observed overhead: 599-604 us; median 603 us in both profiles.', 15)
svg.text(35, 452, 'Includes command, synthesizer/startup, ramp and ISR overhead. Not a spectrum or bandwidth measurement.', 12)
svg.save('singularity-rpc-timing.svg')
print('Generated two SVG figures from 40 call rows and 30 timing rows.')
