#!/usr/bin/env python3
"""
z1_probe.py — minimal, safety-gated Makera Z1 protocol explorer.

This utility intentionally supports Wi-Fi/TCP only. The current Community
Controller discussion indicates that Z1 USB behavior still needs investigation.

Examples:
    python z1_probe.py discover
    python z1_probe.py query 192.168.1.50 version
    python z1_probe.py query 192.168.1.50 "?"
    python z1_probe.py shell 192.168.1.50 --transcript z1-session.jsonl

Unsafe commands are refused unless BOTH flags are supplied:
    --unsafe --confirm I_UNDERSTAND_MACHINE_CAN_MOVE
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DEFAULT_TCP_PORT = 2222
DEFAULT_DISCOVERY_PORT = 3333

# Conservative allowlist. These commands are intended to inspect machine state
# without requesting motion, changing configuration, or energizing actuators.
READ_ONLY_COMMANDS = {
    "?",
    "version",
    "model",
    "ftype",
    "time",
    "help",
    "diagnose",
    "$G",
    "$#",
    "$I",
    "get wcs",
    "config-get-all -e",
    "wlan -e",
    "M105",
}

UNSAFE_CONFIRMATION = "I_UNDERSTAND_MACHINE_CAN_MOVE"


@dataclass(frozen=True)
class Reply:
    raw: bytes
    elapsed_s: float


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_command(command: str) -> str:
    return command.strip()


def is_read_only(command: str) -> bool:
    return normalize_command(command).casefold() in {
        item.casefold() for item in READ_ONLY_COMMANDS
    }


def encode_command(command: str) -> bytes:
    command = normalize_command(command)
    # The controller sends real-time status request "?" without a newline.
    return b"?" if command == "?" else command.encode("utf-8") + b"\n"


def decode_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def append_transcript(
    path: Path | None,
    *,
    direction: str,
    payload: bytes,
    command: str | None = None,
) -> None:
    if path is None:
        return

    record = {
        "timestamp_utc": utc_now(),
        "direction": direction,
        "command": command,
        "text": decode_text(payload),
        "hex": payload.hex(" "),
        "length": len(payload),
    }
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")


def receive_until_quiet(
    sock: socket.socket,
    *,
    overall_timeout_s: float,
    quiet_period_s: float,
) -> Reply:
    start = time.monotonic()
    last_data_at = start
    chunks: list[bytes] = []

    while True:
        now = time.monotonic()
        if now - start >= overall_timeout_s:
            break
        if chunks and now - last_data_at >= quiet_period_s:
            break

        remaining = max(0.01, min(quiet_period_s, overall_timeout_s - (now - start)))
        sock.settimeout(remaining)
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            continue

        if not chunk:
            break

        chunks.append(chunk)
        last_data_at = time.monotonic()

    return Reply(raw=b"".join(chunks), elapsed_s=time.monotonic() - start)


def parse_status_lines(text: str) -> list[dict[str, Any]]:
    """Parse angle-bracket status reports without assuming every field exists."""
    reports: list[dict[str, Any]] = []

    for raw_line in text.replace("\r", "").split("\n"):
        line = raw_line.strip()
        if not (line.startswith("<") and line.endswith(">")):
            continue

        fields = line[1:-1].split("|")
        report: dict[str, Any] = {"state": fields[0], "raw": line}

        for field in fields[1:]:
            if ":" not in field:
                report.setdefault("unparsed", []).append(field)
                continue
            key, value = field.split(":", 1)
            values = value.split(",")
            parsed_values: list[Any] = []
            for item in values:
                try:
                    parsed_values.append(float(item))
                except ValueError:
                    parsed_values.append(item)
            report[key] = parsed_values

        reports.append(report)

    return reports


def print_reply(reply: Reply) -> None:
    text = decode_text(reply.raw)
    print(f"RX {len(reply.raw)} bytes in {reply.elapsed_s:.3f}s")
    if reply.raw:
        print(text, end="" if text.endswith("\n") else "\n")
        reports = parse_status_lines(text)
        if reports:
            print("\nParsed status:")
            print(json.dumps(reports, indent=2))
    else:
        print("<no response>")


def validate_command(command: str, unsafe: bool, confirmation: str | None) -> None:
    if is_read_only(command):
        return
    if not unsafe or confirmation != UNSAFE_CONFIRMATION:
        allowed = ", ".join(sorted(READ_ONLY_COMMANDS))
        raise SystemExit(
            "Refusing a non-read-only command.\n"
            f"Read-only allowlist: {allowed}\n"
            "To deliberately override, supply:\n"
            f"  --unsafe --confirm {UNSAFE_CONFIRMATION}"
        )


def run_query(
    host: str,
    port: int,
    command: str,
    *,
    connect_timeout_s: float,
    response_timeout_s: float,
    quiet_period_s: float,
    transcript: Path | None,
    unsafe: bool,
    confirmation: str | None,
) -> Reply:
    validate_command(command, unsafe, confirmation)
    payload = encode_command(command)

    print(f"Connecting to {host}:{port} …")
    with socket.create_connection((host, port), timeout=connect_timeout_s) as sock:
        append_transcript(
            transcript, direction="tx", payload=payload, command=normalize_command(command)
        )
        print(f"TX {payload!r}")
        sock.sendall(payload)

        reply = receive_until_quiet(
            sock,
            overall_timeout_s=response_timeout_s,
            quiet_period_s=quiet_period_s,
        )
        append_transcript(transcript, direction="rx", payload=reply.raw, command=command)
        return reply


def discover(port: int, duration_s: float) -> int:
    """Listen for the comma-separated UDP announcements used by the controller."""
    found: dict[tuple[str, int], dict[str, Any]] = {}
    deadline = time.monotonic() + duration_s

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", port))
        sock.settimeout(0.25)

        print(f"Listening on UDP 0.0.0.0:{port} for {duration_s:g}s …")
        while time.monotonic() < deadline:
            try:
                payload, sender = sock.recvfrom(1024)
            except socket.timeout:
                continue

            text = decode_text(payload).strip()
            fields = text.split(",")
            item: dict[str, Any] = {
                "sender": f"{sender[0]}:{sender[1]}",
                "raw": text,
            }

            if len(fields) >= 4:
                name, ip, advertised_port, busy = fields[:4]
                try:
                    parsed_port = int(advertised_port)
                except ValueError:
                    parsed_port = DEFAULT_TCP_PORT
                item.update(
                    {
                        "name": name,
                        "ip": ip,
                        "port": parsed_port,
                        "busy": busy == "1",
                    }
                )
                found[(ip, parsed_port)] = item
            else:
                found[(sender[0], DEFAULT_TCP_PORT)] = item

            print(json.dumps(item, ensure_ascii=False))

    if not found:
        print(
            "No announcements received. Obtain the Z1 IP from Makera Studio "
            "or your router, then use the query command directly.",
            file=sys.stderr,
        )
        return 1
    return 0


def shell(args: argparse.Namespace) -> int:
    print("Read-only commands:")
    print("  " + "\n  ".join(sorted(READ_ONLY_COMMANDS)))
    print("Enter 'quit' to exit.")

    while True:
        try:
            command = input("z1> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not command:
            continue
        if command.casefold() in {"quit", "exit"}:
            return 0

        try:
            reply = run_query(
                args.host,
                args.port,
                command,
                connect_timeout_s=args.connect_timeout,
                response_timeout_s=args.timeout,
                quiet_period_s=args.quiet,
                transcript=args.transcript,
                unsafe=args.unsafe,
                confirmation=args.confirm,
            )
            print_reply(reply)
        except (ConnectionError, OSError) as exc:
            print(f"Connection error: {exc}", file=sys.stderr)


def add_connection_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("host", help="Z1 IP address or hostname")
    parser.add_argument("--port", type=int, default=DEFAULT_TCP_PORT)
    parser.add_argument("--connect-timeout", type=float, default=2.0)
    parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="Maximum response wait in seconds",
    )
    parser.add_argument(
        "--quiet",
        type=float,
        default=0.30,
        help="Finish after this many seconds without new bytes",
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        help="Append TX/RX records as JSON Lines",
    )
    parser.add_argument(
        "--unsafe",
        action="store_true",
        help="Permit commands outside the read-only allowlist",
    )
    parser.add_argument(
        "--confirm",
        help=f"Required unsafe confirmation: {UNSAFE_CONFIRMATION}",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="subcommand", required=True)

    discover_parser = sub.add_parser(
        "discover", help="Listen for UDP machine announcements"
    )
    discover_parser.add_argument("--port", type=int, default=DEFAULT_DISCOVERY_PORT)
    discover_parser.add_argument("--seconds", type=float, default=5.0)

    query_parser = sub.add_parser("query", help="Send one command and print raw reply")
    add_connection_arguments(query_parser)
    query_parser.add_argument("command", help='For example: version, model, "?"')

    shell_parser = sub.add_parser("shell", help="Interactive command explorer")
    add_connection_arguments(shell_parser)

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.subcommand == "discover":
        return discover(args.port, args.seconds)

    if args.subcommand == "query":
        try:
            reply = run_query(
                args.host,
                args.port,
                args.command,
                connect_timeout_s=args.connect_timeout,
                response_timeout_s=args.timeout,
                quiet_period_s=args.quiet,
                transcript=args.transcript,
                unsafe=args.unsafe,
                confirmation=args.confirm,
            )
        except (ConnectionError, OSError) as exc:
            print(f"Connection error: {exc}", file=sys.stderr)
            return 2
        print_reply(reply)
        return 0

    if args.subcommand == "shell":
        return shell(args)

    raise AssertionError(f"Unhandled subcommand: {args.subcommand}")


if __name__ == "__main__":
    raise SystemExit(main())
