#!/usr/bin/env python3
"""Project a complete dispatcher trace to intentionally partial observations."""

import argparse
import json
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()

projected = []
for line in args.input.read_text().splitlines():
    if not line.strip():
        continue
    event = json.loads(line)
    event.pop("queue_len", None)
    event.pop("dropped", None)
    if event.get("action") in {"receive", "offered", "panic_recovered"}:
        # Hide the exact worker transition while retaining its abstraction class.
        event["action"] = "worker"
    projected.append(event)

args.output.write_text("".join(json.dumps(event, separators=(",", ":")) + "\n" for event in projected))
