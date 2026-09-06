#!/usr/bin/env python3
"""Rebuild the saved view montage from its fourteen firmware PNGs.

Requires ImageMagick montage. Pixel filtering follows ImageMagick's defaults,
matching the original command; metadata/encoder versions may change file hashes.
The saved montage is preserved and never overwritten by this script.
"""
import argparse
import pathlib
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=pathlib.Path, required=True)
args = parser.parse_args()
if args.output.exists():
    parser.error('output already exists; choose a fresh path')
assets = pathlib.Path(__file__).resolve().parent
views = ('activity', 'call-details', 'dashboard', 'health-details', 'led-details', 'sensor-details', 'setup')
inputs = [assets / f'singularity-rpc-console-{board}-{view}.png' for board in ('A', 'B') for view in views]
for image in inputs:
    if not image.is_file():
        raise FileNotFoundError(image)
subprocess.run(['montage', *map(str, inputs), '-tile', '4x', '-geometry', '480x270+6+6', str(args.output)], check=True)
print(args.output)
