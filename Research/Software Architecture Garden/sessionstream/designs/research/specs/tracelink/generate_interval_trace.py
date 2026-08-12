#!/usr/bin/env python3
"""Generate a TLC linearization search from model and operation-interval JSONL."""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from generate_trace import record, tla_string


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def tla_set(values: set[int]) -> str:
    return "{" + ", ".join(str(value) for value in sorted(values)) + "}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model_jsonl", type=Path)
    parser.add_argument("interval_jsonl", type=Path)
    parser.add_argument("--capacity", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    model = load(args.model_jsonl)
    intervals = load(args.interval_jsonl)
    if not model or not intervals:
        raise SystemExit("model and interval traces must be non-empty")
    partitions = {(e.get("run_id"), e.get("dispatcher_id")) for e in model + intervals}
    if len(partitions) != 1 or None in next(iter(partitions)) or "" in next(iter(partitions)):
        raise SystemExit(f"interval validation requires exactly one non-empty partition: {partitions}")
    run_id, dispatcher_id = next(iter(partitions))

    for expected, event in enumerate(model, 1):
        if event.get("sequence") != expected:
            raise SystemExit(f"model sequence at line {expected} is not contiguous")
    for expected, event in enumerate(intervals, 1):
        if event.get("sequence") != expected:
            raise SystemExit(f"interval sequence at line {expected} is not contiguous")

    by_operation: dict[str, list[dict]] = defaultdict(list)
    for event in intervals:
        operation_id = event.get("operation_id")
        if not operation_id:
            raise SystemExit(f"interval event lacks operation ID: {event}")
        by_operation[operation_id].append(event)

    bounds: dict[str, tuple[int, int]] = {}
    linear_actions: dict[str, list[str]] = {}
    cancelled: set[str] = set()
    for operation_id, events in by_operation.items():
        operations = {event.get("operation") for event in events}
        if len(operations) != 1 or None in operations or "" in operations:
            raise SystemExit(f"operation metadata changes within {operation_id}: {operations}")
        phases = [event.get("phase") for event in events]
        if phases == ["invoke", "cancel"]:
            cancelled.add(operation_id)
            continue
        if phases[0] != "invoke" or phases[-1] != "return" or phases.count("invoke") != 1 or phases.count("return") != 1:
            raise SystemExit(f"operation {operation_id} is not invoke..linearize..return or invoke..cancel: {phases}")
        if any(phase != "linearize" for phase in phases[1:-1]):
            raise SystemExit(f"operation {operation_id} has invalid interior phase: {phases}")
        bounds[operation_id] = (events[0]["sequence"], events[-1]["sequence"])
        linear_actions[operation_id] = [event["action"] for event in events[1:-1]]

    model_actions: dict[str, list[str]] = defaultdict(list)
    step_by_operation: dict[str, list[int]] = defaultdict(list)
    for index, event in enumerate(model, 1):
        operation_id = event.get("operation_id")
        if operation_id not in by_operation:
            raise SystemExit(f"model event references missing operation interval: {operation_id}")
        model_actions[operation_id].append(event["action"])
        step_by_operation[operation_id].append(index)
    active_operations = set(by_operation) - cancelled
    if set(model_actions) != active_operations:
        missing = active_operations - set(model_actions)
        extra = set(model_actions) - active_operations
        raise SystemExit(f"model/interval operation mismatch: missing={sorted(missing)} extra={sorted(extra)}")
    for operation_id in active_operations:
        if model_actions[operation_id] != linear_actions[operation_id]:
            raise SystemExit(
                f"linearization actions disagree for {operation_id}: "
                f"model={model_actions[operation_id]} interval={linear_actions[operation_id]}"
            )

    predecessors = [set() for _ in model]
    # Preserve multiple abstract steps belonging to one operation.
    for indices in step_by_operation.values():
        for previous, current in zip(indices, indices[1:]):
            predecessors[current - 1].add(previous)
    # Real-time order: an operation returning before another invocation must
    # linearize before every abstract step of the latter operation.
    for before, (_, return_sequence) in bounds.items():
        for after, (invoke_sequence, _) in bounds.items():
            if before != after and return_sequence < invoke_sequence:
                for after_step in step_by_operation[after]:
                    predecessors[after_step - 1].update(step_by_operation[before])

    projected = []
    for event in model:
        event = dict(event)
        event.pop("queue_len", None)
        event.pop("dropped", None)
        projected.append(event)
    steps = ",\n        ".join(record(event) for event in projected)
    pred_data = ", ".join(tla_set(values) for values in predecessors)
    item_values = sorted({
        event.get("value", event.get("item_id"))
        for event in model
        if isinstance(event.get("value", event.get("item_id")), int)
        and event.get("value", event.get("item_id")) != 0
    }) or [0]
    items = "{" + ", ".join(str(value) for value in item_values) + "}"

    module_name = args.output.stem
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", module_name):
        raise SystemExit(f"output stem must be a TLA+ identifier: {module_name!r}")
    module = f'''---- MODULE {module_name} ----
RunID == {tla_string(run_id)}
DispatcherID == {tla_string(dispatcher_id)}

VARIABLES queue, admitted, offered, current, closing, dropped,
          closeCount, exited, waited, kernelPos, consumed

StepData == <<
        {steps}
    >>
PredecessorData == <<{pred_data}>>

IntervalInstance == INSTANCE DispatcherIntervalValidator
    WITH Capacity <- {args.capacity}, Items <- {items}, Steps <- StepData,
         Predecessors <- PredecessorData,
         queue <- queue, admitted <- admitted, offered <- offered,
         current <- current, closing <- closing, dropped <- dropped,
         closeCount <- closeCount, exited <- exited, waited <- waited,
         kernelPos <- kernelPos, consumed <- consumed

Spec == IntervalInstance!Spec
QueueBound == IntervalInstance!QueueBound
CloseOnce == IntervalInstance!CloseOnce
Shape == IntervalInstance!Shape
ExitSound == IntervalInstance!ExitSound
WaitSound == IntervalInstance!WaitSound
NoCompleteLinearization == IntervalInstance!NoCompleteLinearization

====
'''
    args.output.write_text(module)


if __name__ == "__main__":
    main()
