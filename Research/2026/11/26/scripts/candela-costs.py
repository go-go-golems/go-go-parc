"""Reproduce the 64-spp JIG-029 timing figure; all inputs are saved run artifacts.

Extract: python candela-costs.py extract receipt.json render.log submission.log reel-receipt-2048spp.json candela-timings.json
Plot:    python candela-costs.py plot candela-timings.json candela-costs.png
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def extract(receipt, renderlog, submission, reel):
    job = json.loads(receipt.read_text())
    records = job['native']
    preview_log = renderlog.read_text()
    reported = [line for line in preview_log.splitlines() if line.startswith('Jig-Stage optix')]
    assert len(reported) == len(records)
    total_wall = int(re.search(r'fetched after (\d+) s', submission.read_text())[1])
    def log_ms(pattern):
        return sum(float(match) for line in reported for match in re.findall(pattern, line))
    parts = {
        'Candela scene build': log_ms(r'build ([\d.]+) ms') / 1000,
        'Tracing-program NVRTC compile': log_ms(r'nvrtc ([\d.]+) ms') / 1000,
        'OptiX pipeline setup': log_ms(r'pipeline ([\d.]+) ms') / 1000,
        'Native frame render interval': sum(r['renderMs'] for r in records) / 1000,
        'Native output interval': log_ms(r'output ([\d.]+) ms') / 1000,
    }
    parts['Remaining elapsed time'] = total_wall - sum(parts.values())
    # Source phase boundaries are the four long groups and the gaps between them.
    boundaries = {0, job['frames']}
    for r in records:
        if r['first'] != r['last']:
            boundaries.update((r['first'], r['last'] + 1))
    phases = []
    boundaries = sorted(boundaries)
    for first, stop in zip(boundaries, boundaries[1:]):
        local = [r for r in records if first <= r['first'] and r['last'] < stop]
        reuse = sum(r['reused'] for r in local)
        traced = sum(r['traced'] for r in local)
        phases.append({'first': first, 'last': stop - 1, 'traced': traced, 'reused': reuse,
                       'noBeauty': stop - first - traced - reuse, 'calls': len(local),
                       'renderSeconds': round(sum(r['renderMs'] for r in local) / 1000, 4)})
    old = json.loads(reel.read_text())
    compare = []
    for chapter in old['chapters']:
        if chapter['slug'] not in ('PT-C03-rack-focus', 'PT-L01-strip-travel', 'PT-L07-three-point-studio'):
            continue
        panels = sum(n['last'] - n['first'] + 1 for n in chapter['native'])
        elapsed = sum(n['renderMs'] for n in chapter['native']) / 1000
        compare.append({'chapter': chapter['slug'], 'spp': old['spp'], 'panelFrames': panels,
                        'nativeSeconds': elapsed, 'secondsPerPanel': round(elapsed / panels, 4)})
    return {
        'film': 'PT-S02 Singer orbit, preview A', 'width': job['width'], 'height': job['height'],
        'fps': job['fps'], 'frames': job['frames'], 'spp': job['spp'], 'movieSha256': job['sha256'],
        'inputDigests': {role: hashlib.sha256(p.read_bytes()).hexdigest() for role, p in
                         [('stageReceipt', receipt), ('sparkNativeLog', renderlog), ('submitterLog', submission), ('earlierReelReceipt', reel)]},
        'submitToFetchedSeconds': total_wall, 'intervalSeconds': {k: round(v, 4) for k, v in parts.items()},
        'launches': int(log_ms(r'in (\d+) launches')), 'singleFrameGroups': sum(r['first'] == r['last'] for r in records),
        'nvrtcCacheHits': sum('nvrtc cached' in line for line in reported),
        'countsBySourceInterval': phases, 'earlier2048sppDifferentWorkloads': compare,
        'measurementNotes': [
            'Submit timer starts with an existing browser-generated ZIP. It ends on verified download, before local full decode and playback.',
            'Scene build times openRender after JS bundle and content reads. Native output covers postprocessing, readback and PNG generation.',
            'Render interval includes setSample, scene upload/update, sample launches and GPU synchronization. GPU-only active time was not measured.',
            'NVRTC counts apply to the tracing program. AS and JS helper timers are excluded from the partition because their scopes intersect other operations.',
            'The remaining elapsed time is a residual. It includes job transfer, process/scene setup outside logged intervals, compositing, encoding and fetch, plus log rounding. No allocation within this residual was measured.',
            'Single-panel preview. Source frames without beauty views contribute directly through deterministic drafting plates.',
        ],
    }


def plot(data, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, (a, b) = plt.subplots(1, 2, figsize=(12.9, 5), gridspec_kw={'width_ratios': [1, 1.15]})
    fig.patch.set_facecolor('white')
    fig.subplots_adjust(left=.20, right=.98, top=.73, bottom=.21, wspace=.58)
    fig.text(.03, .94, 'Where the Singer orbit preview spent time', weight='bold', fontsize=21)
    fig.text(.03, .875, 'DGX Spark   ·   40 seconds of film   ·   1,200 frames   ·   1280 × 720   ·   64 spp', color='#496070', fontsize=12)
    times = data['intervalSeconds']
    names = ['Native frame render interval', 'Candela scene build', 'OptiX pipeline setup',
             'Tracing-program NVRTC compile', 'Native output interval', 'Remaining elapsed time']
    labels = ['Frame render interval', 'Scene build', 'Pipeline setup', 'NVRTC compile', 'Native output', 'Unattributed remainder']
    values = [times[k] for k in names]
    bars = a.barh(range(len(names)), values, color=['#225d71', '#5691a1', '#5691a1', '#5691a1', '#5691a1', '#9ba6aa'])
    a.set(yticks=range(len(names)), yticklabels=labels, xlim=(0, max(values) * 1.26), xlabel='Elapsed seconds'); a.invert_yaxis()
    a.bar_label(bars, labels=[f'{v:.1f}' for v in values], padding=3, fontsize=9)
    a.set_title('658 s from submit to fetch', loc='left', fontweight='bold')
    p = data['countsBySourceInterval']
    offsets = [0] * len(p)
    colors = ['#225d71', '#e6a43c', '#d3dade']; legend = []
    for key, name, color in zip(['traced', 'reused', 'noBeauty'], ['Fresh trace', 'Reused beauty', 'CAD only'], colors):
        count = [x[key] for x in p]
        block = b.barh(range(len(p)), count, left=offsets, color=color, label=name)
        offsets = [o+c for o, c in zip(offsets, count)]
        legend.append(block)
    b.set(yticks=range(len(p)), yticklabels=[f'{x["first"]}–{x["last"]}' for x in p],
          xlabel='Output frames in interval', ylabel='Source frame range')
    b.invert_yaxis(); b.set_title('Which frames requested rays?', loc='left', fontweight='bold')
    b.legend(handles=legend, loc='upper left', bbox_to_anchor=(0,-.24), frameon=False, ncol=3, fontsize=8, borderaxespad=0)
    for ax in (a,b):
        ax.spines[['top','right','left']].set_visible(False); ax.spines['bottom'].set_color('#aeb9bf')
        ax.tick_params(axis='y',length=0); ax.grid(axis='x',color='#ddd',linewidth=.6); ax.set_axisbelow(True)
    fig.savefig(out, dpi=175)
    plt.close(fig)


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    subs = cli.add_subparsers(dest='cmd', required=True)
    e = subs.add_parser('extract')
    for arg in ['receipt', 'renderlog', 'submission', 'reel', 'jsonpath']:
        e.add_argument(arg, type=Path)
    p = subs.add_parser('plot')
    p.add_argument('jsonpath', type=Path); p.add_argument('out', type=Path)
    args = cli.parse_args()
    if args.cmd == 'extract':
        data = extract(args.receipt, args.renderlog, args.submission, args.reel)
        args.jsonpath.write_text(json.dumps(data, indent=2) + '\n')
    else:
        plot(json.loads(args.jsonpath.read_text()), args.out)
