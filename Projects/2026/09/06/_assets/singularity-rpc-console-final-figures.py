#!/usr/bin/env python3
"""Rebuild final-report montages from preserved frames; no firmware or network."""
import argparse
import hashlib
import json
import pathlib
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--assets', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parent)
parser.add_argument('--output-dir', type=pathlib.Path, required=True)
args = parser.parse_args()
manifest = json.loads((args.assets / 'singularity-rpc-console-final-manifest.json').read_text())
args.output_dir.mkdir(parents=True, exist_ok=False)
for name, entry in manifest.items():
    if 'inputs' not in entry: continue
    inputs = [args.assets / p for p in entry['inputs']]
    for path in inputs:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest[path.name]['sha256'], path
    subprocess.run(['montage', *map(str, inputs), '-tile', '2x', '-geometry', '480x270+6+6', str(args.output_dir/name)], check=True)
    print(args.output_dir/name)
