#!/usr/bin/env python3
"""Generate a TLC root module from dispatcher model-event JSONL."""

import argparse
import json
import re
from pathlib import Path


def tla_string(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


ACTIONS = {
    "submit_accepted",
    "submit_dropped",
    "submit_rejected",
    "close_effective",
    "close_noop",
    "receive",
    "offered",
    "panic_recovered",
    "worker_exit",
    "wait_returned",
    "worker",  # reviewed abstraction class: receive/offered/panic_recovered
}


def record(event: dict) -> str:
    required = {"schema_version", "run_id", "dispatcher_id", "sequence", "action"}
    missing = required - event.keys()
    if missing:
        raise ValueError(f"event missing fields {sorted(missing)}: {event}")
    if event["schema_version"] != 1:
        raise ValueError(f"unsupported schema version: {event['schema_version']}")
    if event["sequence"] <= 0:
        raise ValueError(f"invalid sequence: {event['sequence']}")

    action = event["action"]
    if action not in ACTIONS:
        raise ValueError(f"unsupported action or abstraction class: {action!r}")
    has_action = True
    updates = event.get("updates") or {}
    if not isinstance(updates, dict):
        raise ValueError(f"updates must be an object: {updates!r}")
    evidence = event.get("evidence") or {}
    if not isinstance(evidence, dict):
        raise ValueError(f"evidence must be an object: {evidence!r}")
    allowed_updates = {"queue_len", "dropped", "closing", "worker_done", "waited", "offered_item"}
    unknown_updates = set(updates) - allowed_updates
    if unknown_updates:
        raise ValueError(f"unsupported abstract updates: {sorted(unknown_updates)}")

    value = event.get("value", event.get("item_id", 0))
    if not isinstance(value, int):
        raise ValueError(f"prototype accepts integer values only: {value!r}")
    has_value = bool(event.get("has_value", bool(event.get("item_id")) or "value" in event))
    queue_len = updates.get("queue_len", event.get("queue_len", 0))
    dropped = updates.get("dropped", event.get("dropped", 0))
    closing = updates.get("closing", False)
    worker_done = updates.get("worker_done", False)
    waited = updates.get("waited", False)
    offered_item = updates.get("offered_item", 0)
    has_queue_len = "queue_len" in updates or "queue_len" in event
    has_dropped = "dropped" in updates or "dropped" in event
    has_closing = "closing" in updates
    has_worker_done = "worker_done" in updates
    has_waited = "waited" in updates
    has_offered_item = "offered_item" in updates

    fields = [
        f"schema_version |-> {event['schema_version']}",
        f"sequence |-> {event['sequence']}",
        f"action |-> {tla_string(action if has_action else '')}",
        f"has_action |-> {'TRUE' if has_action else 'FALSE'}",
        f"value |-> {value}",
        f"has_value |-> {'TRUE' if has_value else 'FALSE'}",
        f"queue_len |-> {queue_len}",
        f"has_queue_len |-> {'TRUE' if has_queue_len else 'FALSE'}",
        f"dropped |-> {dropped}",
        f"has_dropped |-> {'TRUE' if has_dropped else 'FALSE'}",
        f"closing |-> {'TRUE' if closing else 'FALSE'}",
        f"has_closing |-> {'TRUE' if has_closing else 'FALSE'}",
        f"worker_done |-> {'TRUE' if worker_done else 'FALSE'}",
        f"has_worker_done |-> {'TRUE' if has_worker_done else 'FALSE'}",
        f"waited |-> {'TRUE' if waited else 'FALSE'}",
        f"has_waited |-> {'TRUE' if has_waited else 'FALSE'}",
        f"offered_item |-> {offered_item}",
        f"has_offered_item |-> {'TRUE' if has_offered_item else 'FALSE'}",
    ]
    return "[" + ", ".join(fields) + "]"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("--capacity", type=int, required=True)
    parser.add_argument("--run-id", help="select one run partition from mixed JSONL")
    parser.add_argument("--dispatcher-id", help="select one dispatcher partition from mixed JSONL")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.capacity <= 0:
        raise SystemExit("capacity must be positive")

    events = [json.loads(line) for line in args.jsonl.read_text().splitlines() if line.strip()]
    for event in events:
        if not event.get("run_id") or not event.get("dispatcher_id"):
            raise SystemExit(f"event has empty partition key: {event}")

    if bool(args.run_id) != bool(args.dispatcher_id):
        raise SystemExit("--run-id and --dispatcher-id must be provided together")
    if args.run_id:
        events = [
            event
            for event in events
            if event["run_id"] == args.run_id and event["dispatcher_id"] == args.dispatcher_id
        ]
        if not events:
            raise SystemExit(f"partition not found: {args.run_id}/{args.dispatcher_id}")

    partitions = {(event["run_id"], event["dispatcher_id"]) for event in events}
    if len(partitions) != 1:
        raise SystemExit(f"trace contains {len(partitions)} partitions; select exactly one with --run-id/--dispatcher-id")
    run_id, dispatcher_id = next(iter(partitions))

    for expected, event in enumerate(events, 1):
        if event.get("sequence") != expected:
            raise SystemExit(f"sequence {event.get('sequence')} at line {expected}, expected {expected}")

    trace = ",\n        ".join(record(event) for event in events)
    item_values = sorted({
        event.get("value", event.get("item_id"))
        for event in events
        if isinstance(event.get("value", event.get("item_id")), int)
        and event.get("value", event.get("item_id")) != 0
    })
    if not item_values:
        item_values = [0]
    items = "{" + ", ".join(str(value) for value in item_values) + "}"
    module_name = args.output.stem
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", module_name):
        raise SystemExit(f"output stem must be a TLA+ identifier: {module_name!r}")
    module = f'''---- MODULE {module_name} ----
RunID == {tla_string(run_id)}
DispatcherID == {tla_string(dispatcher_id)}

VARIABLES queue, admitted, offered, current, closing, dropped,
          closeCount, exited, waited, pos

TraceData == <<
        {trace}
    >>

TraceInstance == INSTANCE DispatcherTraceValidator
    WITH Capacity <- {args.capacity}, Items <- {items}, Trace <- TraceData,
         queue <- queue, admitted <- admitted, offered <- offered,
         current <- current, closing <- closing, dropped <- dropped,
         closeCount <- closeCount, exited <- exited, waited <- waited, pos <- pos

Spec == TraceInstance!Spec
QueueBound == TraceInstance!QueueBound
CloseOnce == TraceInstance!CloseOnce
Shape == TraceInstance!Shape
ExitSound == TraceInstance!ExitSound
WaitSound == TraceInstance!WaitSound
TraceConsumed == TraceInstance!TraceConsumed

====
'''
    args.output.write_text(module)


if __name__ == "__main__":
    main()
