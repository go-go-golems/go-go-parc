#!/usr/bin/env python3
"""Create contract-targeted corruptions from one production trace harvest."""

import argparse
import json
from pathlib import Path


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def save(path: Path, events: list[dict]) -> None:
    path.write_text("".join(json.dumps(event, separators=(",", ":")) + "\n" for event in events))


def resequence(events: list[dict]) -> None:
    for sequence, event in enumerate(events, 1):
        event["sequence"] = sequence


parser = argparse.ArgumentParser()
parser.add_argument("harvest", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)

model = load(args.harvest / "model.jsonl")
intervals = load(args.harvest / "intervals.jsonl")

# M1: one model event references no operation interval.
bad_ids = [dict(event) for event in model]
bad_ids[0]["operation_id"] = "missing-operation"
save(args.output / "bad-operation-model.jsonl", bad_ids)
save(args.output / "bad-operation-intervals.jsonl", intervals)

# M2: contradict the abstract Close transition with a partial next-state update.
bad_update = [dict(event) for event in model]
close_event = next(event for event in bad_update if event["action"] == "close_effective")
close_event["updates"] = {**close_event.get("updates", {}), "closing": False}
save(args.output / "bad-update-model.jsonl", bad_update)
save(args.output / "bad-update-intervals.jsonl", intervals)

# M3: force one accepted submission's complete interval after Close returned.
# This preserves action/operation linkage but changes the real-time boundary,
# making acceptance after sticky Close impossible.
bad_boundary_model = [dict(event) for event in model]
bad_boundary_intervals = [dict(event) for event in intervals]
accepted = next(event for event in bad_boundary_model if event["action"] == "submit_accepted")
accepted_id = accepted["operation_id"]
close = next(event for event in bad_boundary_model if event["action"] == "close_effective")
close_id = close["operation_id"]
accepted_events = [event for event in bad_boundary_intervals if event["operation_id"] == accepted_id]
remaining = [event for event in bad_boundary_intervals if event["operation_id"] != accepted_id]
close_return_index = next(
    index for index, event in enumerate(remaining)
    if event["operation_id"] == close_id and event["phase"] == "return"
)
bad_boundary_intervals = remaining[: close_return_index + 1] + accepted_events + remaining[close_return_index + 1 :]
resequence(bad_boundary_intervals)
save(args.output / "bad-boundary-model.jsonl", bad_boundary_model)
save(args.output / "bad-boundary-intervals.jsonl", bad_boundary_intervals)
