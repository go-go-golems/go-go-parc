# Z1 Controller Development Guide

- URL: https://chatgpt.com/c/6a6f1e5e-0190-83ea-b7a7-dae835c9a6f5
- Created: 2026-08-02T10:39:31.864Z

---

> Looking at https://github.com/Carvera-Community/Carvera_Controller 
>
> I want to use this as a starting point to write my own controller, but I want some way to step by step check and learn how things work on the Makera Z1, how to connect to it, learn the GCOde, test the opcodes, etc...

I’ll map the repository’s communication stack, identify how it connects to the Z1, then turn that into a safe, incremental learning and test plan.

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/get_repo","args":{"repository_full_name":"Carvera-Community/Carvera_Controller"}}
```

<details><summary>💭 Thinking</summary>

**Inspected Carvera Z1 controller code, documentation, and communication interfaces**

</details>

The project is Python/Kivy rather than a thin serial-console app. I’m isolating the transport and machine-protocol layers so you can learn them without the UI.

```unknown
bash -lc rm -rf /tmp/Carvera_Controller && git clone --depth 1 https://github.com/Carvera-Community/Carvera_Controller.git /tmp/Carvera_Controller && find /tmp/Carvera_Controller -maxdepth 3 -type f | sed 's#/tmp/Carvera_Controller/##' | sort | head -250
```

<details><summary>💭 Thinking</summary>

**Cloned the Carvera Controller repository**

</details>

```json
{"system1_search_query":[{"q":"site:github.com/Carvera-Community/Carvera_Controller Carvera_Controller connection socket python"},{"q":"site:github.com/Carvera-Community/Carvera_Controller gcode protocol machine.py"},{"q":"site:carvera-community.gitbook.io/docs controller developer protocol Carvera Z1"},{"q":"Makera Z1 API G-code connection protocol"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"Carvera-Community/Carvera_Controller","path":"carveracontroller/WIFIStream.py"}}
```

<details><summary>💭 Thinking</summary>

**Inspected WiFi, USB, controller, and CNC stream implementations**

</details>

```json
{"open":[{"ref_id":"https://github.com/Carvera-Community/Carvera_Controller/blob/main/carveracontroller/Controller.py"},{"ref_id":"https://github.com/Carvera-Community/Carvera_Controller/blob/main/carveracontroller/WIFIStream.py"},{"ref_id":"https://github.com/Carvera-Community/Carvera_Controller/blob/main/carveracontroller/USBStream.py"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

The transport is plain-text command traffic over TCP or USB, with XMODEM only for file transfers. The next distinction is critical: safe read-only queries versus motion or actuator commands.

```json
{"find":[{"ref_id":"turn963606view0","pattern":"streamIO"},{"ref_id":"turn963606view0","pattern":"parseLine"},{"ref_id":"turn963606view0","pattern":"parseStatus"},{"ref_id":"turn963606view0","pattern":"sio_status"},{"ref_id":"turn963606view0","pattern":"Connected to machine!"},{"ref_id":"turn963606view0","pattern":"def open(self, conn_type, address)"},{"ref_id":"turn963606view0","pattern":"def executeCommand(self, line)"},{"ref_id":"turn963606view0","pattern":"queryVersion"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search","args":{"repository_name":"Carvera-Community/Carvera_Controller","query":"Z1","topn":50}}
```

<details><summary>💭 Thinking</summary>

**Investigated Carvera Z1 support, compatibility, configuration, and parser code**

</details>

```json
{"open":[{"ref_id":"https://github.com/Carvera-Community/Carvera_Controller/blob/develop/carveracontroller/main.py"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_pr_file_patch","args":{"repo_full_name":"Carvera-Community/Carvera_Controller","pr_number":693,"path":"carveracontroller/main.py"}}
```

<details><summary>💭 Thinking</summary>

**Clarifying the approach**

I’m outlining a safe, evidence-based way to study the firmware: first map documented commands, then classify them by risk, and only test read-only behavior before considering controlled state changes.

**Clarified the approach**

**Mapping firmware safely**

I’m treating the documented command list as a reference, not a complete Z1 contract. I’ll compare it with the connector’s actual parser, classify commands by risk, and start with read-only status queries before testing state changes.

**Fetched and inspected Main.py and Makera KV patches**

</details>

```unknown
from pathlib import Path

code = r'''#!/usr/bin/env python3
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
'''

path = Path("/mnt/data/z1_probe.py")
path.write_text(code, encoding="utf-8")
path.chmod(0o755)
print(f"Created {path} ({path.stat().st_size} bytes)")

```

Yes. The best route is to **avoid forking the entire UI initially**. Build a small protocol laboratory first:

**transport → raw command console → response parser → safety layer → G-code model → motion → file transfer → UI**

## Current Z1 status

As of **August 2, 2026**, initial Z1 support has been merged into the repository’s `develop` branch through PR #693, including a Z1 configuration file and model-specific UI changes. The broader Z1 support issue remains open. The maintainers report that the Wi-Fi protocol appears compatible with recent Carvera firmware, but Z1 USB connectivity is still unresolved and may use WinUSB rather than an ordinary serial port. Start with **Wi-Fi and the `develop` branch**, not USB or the `main` branch. fileciteturn13file0L5-L15 fileciteturn15file0L2-L5 fileciteturn10file0L4-L21 fileciteturn11file0L69-L88

```bash
git clone https://github.com/Carvera-Community/Carvera_Controller.git
cd Carvera_Controller
git switch develop
```

## What the repository is doing

The important files, in reading order, are:

1. **`WIFIStream.py`**  
   Opens a normal TCP socket on port **2222**. Machine announcements are received as UDP datagrams on port **3333**, formatted roughly as:

   ```text
   machine-name,ip-address,tcp-port,busy
   ```

   citeturn399063view0L622-L710turn399063view1L756-L787

2. **`Controller.py: executeCommand()`**  
   Most commands are UTF-8 text with a newline appended:

   ```text
   version\n
   G0 X10\n
   diagnose\n
   ```

   Real-time commands such as `?`, `!`, and `~` are sent as individual bytes without a newline. citeturn568191view6L2542-L2556 fileciteturn18file0L2-L2

3. **`Controller.py: streamIO()`**  
   Reads incoming bytes, assembles newline-terminated responses, polls status approximately every 0.2 seconds, and dispatches each completed line to a parser. fileciteturn18file0L2-L2

4. **`parseLine()` and `parseBracketAngle()`**  
   Response families include:

   ```text
   <...>   live status
   {...}   diagnostics
   [...]   coordinate systems or parameters
   #...    internal/transfer information
   error...
   alarm...
   ```

   A status report commonly looks like:

   ```text
   <Idle|MPos:...|WPos:...|F:...|S:...|T:...>
   ```

   Fields vary by firmware and machine model, so your parser should tolerate missing and additional fields. fileciteturn19file0L2-L2

5. **`XMODEM.py`**  
   File upload/download is a separate phase. The Wi-Fi implementation uses an `xmodem8k` variant, while the legacy serial implementation uses ordinary XMODEM. Do not begin there. fileciteturn5file0L2-L2 fileciteturn6file0L2-L2

## Starter protocol tool

I created a standard-library-only utility that:

- Listens for UDP machine announcements.
- Connects to TCP port 2222.
- Sends one command at a time.
- Parses basic `<...>` status reports.
- Records byte-exact JSONL transcripts.
- Refuses motion, spindle, laser, configuration, and unknown commands by default.
- Has no USB support.

[Download `z1_probe.py`](sandbox:/mnt/data/z1_probe.py)

The file has been syntax-tested, but not tested against physical Z1 hardware.

### 1. Prepare the machine

Use either the machine’s Wi-Fi hotspot or put the computer and Z1 on the same local network. Both Wi-Fi modes, along with USB, are documented connection methods for the Z1. citeturn535156search0

Disconnect Makera Studio before opening your own connection. Until demonstrated otherwise, treat the control connection as single-client; the Community Controller itself uses a TCP connection attempt to determine whether a machine is busy. citeturn399063view0L648-L661

### 2. Discover the machine

```bash
python z1_probe.py discover --seconds 10
```

Expected output resembles:

```json
{
  "name": "MAKERA_Z1_01001",
  "ip": "192.168.1.50",
  "port": 2222,
  "busy": false
}
```

Broadcast discovery may be blocked by the operating system, router, VLAN, or firewall. In that case, obtain the IP address from Makera Studio or the router.

### 3. Run only inspection commands

```bash
python z1_probe.py query 192.168.1.50 version \
  --transcript z1-session.jsonl

python z1_probe.py query 192.168.1.50 model \
  --transcript z1-session.jsonl

python z1_probe.py query 192.168.1.50 ftype \
  --transcript z1-session.jsonl

python z1_probe.py query 192.168.1.50 '?' \
  --transcript z1-session.jsonl

python z1_probe.py query 192.168.1.50 diagnose \
  --timeout 3 \
  --transcript z1-session.jsonl

python z1_probe.py query 192.168.1.50 '$G' \
  --transcript z1-session.jsonl

python z1_probe.py query 192.168.1.50 '$#' \
  --transcript z1-session.jsonl

python z1_probe.py query 192.168.1.50 'get wcs' \
  --transcript z1-session.jsonl
```

These correspond closely to query methods already present in `Controller.py`, including `version`, `model`, `ftype`, `$G`, `$#`, and `get wcs`. citeturn568191view7L2653-L2666 fileciteturn17file0L2-L2

For exploration:

```bash
python z1_probe.py shell 192.168.1.50 \
  --transcript z1-session.jsonl
```

## How to learn the command set

In this context, “opcodes” are primarily:

- Standard G-code words.
- Standard and manufacturer-specific M-codes.
- GRBL/Smoothieware-style `$` commands.
- Firmware shell commands such as `version`, `model`, `play`, `ls`, or `config-get-all`.

Use four classifications in your code:

| Class | Examples | Policy |
|---|---|---|
| Inspection | `?`, `version`, `model`, `diagnose`, `$G`, `$#`, `get wcs`, `M105` | Allowed by default |
| State-changing | `G20`, `G21`, `G90`, `G91`, `G54`, `M5`, `M9` | Require deliberate write mode |
| Motion/tooling | `G0`, `G1`, `$J`, `$H`, `G28`, `G38`, `M6` | Physical safety checklist required |
| Hazardous/admin | `M3`, laser commands, output controls, `config-set`, restore/default, reset, firmware update | Separate privileged API |

The official supported-codes reference is a useful baseline for common motion, coordinate-system, spindle, probing, and accessory commands. It is not necessarily a complete Z1 protocol specification. citeturn535156search1

Do **not** brute-force M-code numbers. The Z1 support discussion explicitly warns that stock Makera firmware commands may conflict with Community Firmware commands. Unknown commands belong in a blocked category until documented or observed in known software. fileciteturn11file0L48-L67

## Recommended development sequence

### Stage 1: Capture raw behavior

Record:

```text
timestamp
exact transmitted bytes
exact received bytes
command
firmware version
machine model
machine state before and after
```

Do not normalize away `\r`, `\n`, control bytes, or unexpected fields in the transcript. Raw captures become your protocol fixtures.

### Stage 2: Build a tolerant parser

Use a structure such as:

```text
z1controller/
    transport.py
    discovery.py
    framing.py
    responses.py
    commands.py
    safety.py
    state.py
    cli.py
tests/
    fixtures/
        version.jsonl
        status_idle.jsonl
        diagnose.jsonl
        wcs.jsonl
```

Keep transport separate from interpretation. A TCP test double should be able to replay a captured transcript without a machine attached.

### Stage 3: Learn G-code offline

Concentrate first on modal behavior:

- `G20` / `G21`: inches versus millimetres.
- `G90` / `G91`: absolute versus incremental.
- `G53` versus `G54` and other work coordinate systems.
- `G0` versus `G1`.
- `F`: feed rate.
- `S`: spindle or laser setting depending on mode.
- `M3` / `M5`: spindle start and stop.
- `M7` / `M9`: airflow.
- `T` and `M6`: tool selection and change.

Modal commands remain active after the line finishes. That is one of the major risks in interactive testing: a previous `G91`, `G20`, or alternate WCS can silently change the meaning of the next movement.

### Stage 4: Observe before reproducing motion

Before generating your own motion command:

1. Remove the cutting tool.
2. Remove stock and clamps from the travel area.
3. Keep the emergency stop physically accessible.
4. Confirm spindle and laser are off.
5. Home using the official application.
6. Confirm the machine reports `Idle`.
7. Perform the smallest available step jog in the official application.
8. Capture or log the exact command it sends.
9. Reproduce that exact command only after checking units, coordinate mode, direction, speed, and travel clearance.

This is preferable to assuming that a Carvera `$J` or continuous-jog variant behaves identically on current stock Z1 firmware. The open Z1 issue already notes imperfect jogging behavior with Makera firmware. fileciteturn11file0L25-L45

### Stage 5: Add file operations last

After query, state parsing, and controlled motion are reliable:

1. Implement `ls` and `cat`.
2. Implement MD5 verification.
3. Implement upload negotiation.
4. Add XMODEM8K.
5. Upload a harmless text or tiny test G-code file.
6. Verify it without executing it.
7. Implement `play`, pause, resume, and abort as a separate subsystem.

## Licensing point

The repository is GPL-2.0. Copying or adapting its implementation into your controller requires GPL compliance. A separately written protocol client with your own architecture is cleaner when you do not intend to inherit that codebase’s licensing model. citeturn355915view0L319-L321

The most useful next artifact is a redacted transcript containing `version`, `model`, `ftype`, `?`, `diagnose`, and `$G`. That will establish the actual Z1 response grammar before any motion code is introduced.


---

> can we build a proxy that advertises itself as another printer, and records everything?

<details><summary>💭 Thinking</summary>

**Building the proxy**

I’m inspecting the repository’s discovery and TCP behavior to design a compatible relay. The likely structure is a UDP advertiser plus a bidirectional TCP forwarder that records traffic without altering payloads.

**Built the proxy**

</details>

Yes. The clean design is a transparent TCP man-in-the-middle plus a UDP discovery beacon, with byte-exact duplex logging and no protocol interpretation in the forwarding path.

```json
{"paths":["GitHub"],"query":"search"}
```

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search","args":{"repository_name":"Carvera-Community/Carvera_Controller","query":"query_for_machines check_for_responses machine_list UDP_PORT 3333","topn":20}}
```

<details><summary>💭 Thinking</summary>

**Designing the relay**

I’m building a standalone TCP relay with periodic UDP discovery announcements. It will expose a distinct printer name, forward bytes unchanged, and write timestamped, direction-labeled traffic logs for later inspection.

**Designed the relay**

**Searched machine discovery code and documentation**

</details>

The proxy will use the discovery tuple the controller expects—name, proxy IP, TCP port, busy flag—then forward the TCP byte stream unchanged to the real Z1. The capture format will preserve binary file-transfer traffic as well as text commands.

```unknown
from pathlib import Path
import textwrap, zipfile, os

proxy_code = r'''#!/usr/bin/env python3
"""
z1_mitm_proxy.py

Transparent Makera/Carvera TCP recording proxy with UDP discovery advertising.

It advertises a separate machine name on UDP port 3333, listens for a controller
connection on TCP port 2222, connects to the real machine, and relays every byte
unchanged in both directions.

The proxy records:
  * A JSON Lines event stream with base64-encoded byte chunks and timestamps.
  * Raw client-to-machine bytes.
  * Raw machine-to-client bytes.
  * Session byte counts and SHA-256 hashes.

This is an application-stream capture. It preserves all TCP payload bytes seen
by the proxy, but it is not a packet capture: TCP retransmissions, ACKs, IP
headers, and Ethernet/Wi-Fi frames are not included.

Example:
    python z1_mitm_proxy.py \
        --upstream 192.168.1.50 \
        --name MAKERA_Z1_PROXY \
        --broadcast 192.168.1.255 \
        --log-dir captures

Use a unique advertised name. The Community Controller deduplicates discovery
entries by name, so impersonating the real machine name on the same network can
produce ambiguous results.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import ipaddress
import json
import os
import secrets
import socket
import socketserver
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Iterable, TextIO

DEFAULT_CONTROL_PORT = 2222
DEFAULT_DISCOVERY_PORT = 3333
DEFAULT_ADVERTISE_INTERVAL = 1.0
DEFAULT_RECV_SIZE = 65536


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def secure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(0o700)
    except OSError:
        pass


def secure_open_binary(path: Path) -> BinaryIO:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    return os.fdopen(fd, "wb", buffering=0)


def secure_open_text(path: Path) -> TextIO:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    return os.fdopen(fd, "w", encoding="utf-8", buffering=1)


def text_preview(data: bytes, limit: int = 512) -> str:
    sample = data[:limit]
    decoded = sample.decode("utf-8", errors="backslashreplace")
    if len(data) > limit:
        decoded += f"... <{len(data) - limit} more bytes>"
    return decoded


class JsonlJournal:
    """Thread-safe append-only JSONL journal."""

    def __init__(self, path: Path, fsync: bool = False) -> None:
        self.path = path
        self._stream = secure_open_text(path)
        self._lock = threading.Lock()
        self._sequence = 0
        self._fsync = fsync

    def write(self, event: str, **fields: Any) -> int:
        with self._lock:
            self._sequence += 1
            record = {
                "sequence": self._sequence,
                "utc": utc_now(),
                "monotonic_ns": time.monotonic_ns(),
                "event": event,
                **fields,
            }
            self._stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            self._stream.flush()
            if self._fsync:
                os.fsync(self._stream.fileno())
            return self._sequence

    def close(self) -> None:
        with self._lock:
            if not self._stream.closed:
                self._stream.flush()
                if self._fsync:
                    os.fsync(self._stream.fileno())
                self._stream.close()


class ProxyJournal:
    """Long-lived journal for proxy lifecycle and discovery advertisements."""

    def __init__(self, log_dir: Path, fsync: bool) -> None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.journal = JsonlJournal(log_dir / f"proxy-{stamp}.jsonl", fsync=fsync)

    def write(self, event: str, **fields: Any) -> None:
        self.journal.write(event, **fields)

    def close(self) -> None:
        self.journal.close()


class SessionRecorder:
    """Byte-exact recorder for one proxied TCP session."""

    def __init__(
        self,
        log_dir: Path,
        *,
        client_address: tuple[str, int],
        upstream_address: tuple[str, int],
        fsync: bool,
    ) -> None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        self.session_id = f"{stamp}-{secrets.token_hex(3)}"
        prefix = log_dir / f"session-{self.session_id}"

        self._events = JsonlJournal(prefix.with_suffix(".jsonl"), fsync=fsync)
        self._client_to_machine = secure_open_binary(
            log_dir / f"session-{self.session_id}-client-to-machine.bin"
        )
        self._machine_to_client = secure_open_binary(
            log_dir / f"session-{self.session_id}-machine-to-client.bin"
        )
        self._lock = threading.Lock()
        self._fsync = fsync
        self._closed = False
        self._started_monotonic = time.monotonic()

        self._counts = {
            "client_to_machine": 0,
            "machine_to_client": 0,
        }
        self._hashes = {
            "client_to_machine": hashlib.sha256(),
            "machine_to_client": hashlib.sha256(),
        }

        self._events.write(
            "session_start",
            session_id=self.session_id,
            client={"host": client_address[0], "port": client_address[1]},
            upstream={"host": upstream_address[0], "port": upstream_address[1]},
        )

    def event(self, event: str, **fields: Any) -> None:
        self._events.write(event, session_id=self.session_id, **fields)

    def data(self, direction: str, payload: bytes) -> None:
        if direction not in self._counts:
            raise ValueError(f"Unknown direction: {direction}")

        with self._lock:
            if self._closed:
                return

            if direction == "client_to_machine":
                raw_stream = self._client_to_machine
            else:
                raw_stream = self._machine_to_client

            raw_stream.write(payload)
            if self._fsync:
                os.fsync(raw_stream.fileno())

            self._counts[direction] += len(payload)
            self._hashes[direction].update(payload)

            self._events.write(
                "data",
                session_id=self.session_id,
                direction=direction,
                byte_count=len(payload),
                total_bytes=self._counts[direction],
                base64=base64.b64encode(payload).decode("ascii"),
                utf8_preview=text_preview(payload),
            )

    def close(self, reason: str) -> None:
        with self._lock:
            if self._closed:
                return

            duration = time.monotonic() - self._started_monotonic
            self._events.write(
                "session_end",
                session_id=self.session_id,
                reason=reason,
                duration_seconds=round(duration, 6),
                byte_counts=dict(self._counts),
                sha256={
                    key: value.hexdigest() for key, value in self._hashes.items()
                },
            )

            for stream in (self._client_to_machine, self._machine_to_client):
                try:
                    if self._fsync:
                        os.fsync(stream.fileno())
                    stream.close()
                except OSError:
                    pass

            self._closed = True
            self._events.close()


class ClientFilter:
    def __init__(self, specifications: Iterable[str]) -> None:
        self.networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
        for item in specifications:
            item = item.strip()
            if not item:
                continue
            if "/" not in item:
                address = ipaddress.ip_address(item)
                suffix = 32 if address.version == 4 else 128
                item = f"{item}/{suffix}"
            self.networks.append(ipaddress.ip_network(item, strict=False))

    def permits(self, address: str) -> bool:
        if not self.networks:
            return True
        parsed = ipaddress.ip_address(address)
        return any(parsed in network for network in self.networks)


class ProxyState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._busy = False

    def claim(self) -> bool:
        with self._lock:
            if self._busy:
                return False
            self._busy = True
            return True

    def release(self) -> None:
        with self._lock:
            self._busy = False

    @property
    def busy(self) -> bool:
        with self._lock:
            return self._busy


@dataclass(frozen=True)
class ProxyConfig:
    upstream_host: str
    upstream_port: int
    listen_host: str
    listen_port: int
    advertise_ip: str
    advertised_name: str
    broadcast_targets: tuple[str, ...]
    discovery_port: int
    advertise_interval: float
    log_dir: Path
    connect_timeout: float
    recv_size: int
    fsync: bool
    advertise: bool
    client_filter: ClientFilter


def tune_tcp_socket(sock: socket.socket) -> None:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except OSError:
        pass


def close_socket(sock: socket.socket) -> None:
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        sock.close()
    except OSError:
        pass


class DiscoveryAdvertiser(threading.Thread):
    def __init__(
        self,
        config: ProxyConfig,
        state: ProxyState,
        stop_event: threading.Event,
        journal: ProxyJournal,
    ) -> None:
        super().__init__(name="discovery-advertiser", daemon=True)
        self.config = config
        self.state = state
        self.stop_event = stop_event
        self.journal = journal

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            except OSError:
                pass

            while not self.stop_event.is_set():
                busy = 1 if self.state.busy else 0
                payload = (
                    f"{self.config.advertised_name},"
                    f"{self.config.advertise_ip},"
                    f"{self.config.listen_port},"
                    f"{busy}"
                ).encode("utf-8")

                for target in self.config.broadcast_targets:
                    try:
                        sock.sendto(
                            payload,
                            (target, self.config.discovery_port),
                        )
                        self.journal.write(
                            "advertisement_sent",
                            target=target,
                            port=self.config.discovery_port,
                            payload=payload.decode("utf-8"),
                            busy=bool(busy),
                        )
                    except OSError as exc:
                        self.journal.write(
                            "advertisement_error",
                            target=target,
                            port=self.config.discovery_port,
                            error=repr(exc),
                        )

                self.stop_event.wait(self.config.advertise_interval)


class RecordingProxyHandler(socketserver.BaseRequestHandler):
    server: "RecordingProxyServer"

    def handle(self) -> None:
        config = self.server.config
        client_host, client_port = self.client_address[:2]

        if not config.client_filter.permits(client_host):
            self.server.journal.write(
                "client_rejected",
                client={"host": client_host, "port": client_port},
                reason="client_not_in_allowlist",
            )
            return

        if not self.server.state.claim():
            self.server.journal.write(
                "client_rejected",
                client={"host": client_host, "port": client_port},
                reason="proxy_busy",
            )
            return

        upstream_address = (config.upstream_host, config.upstream_port)
        recorder = SessionRecorder(
            config.log_dir,
            client_address=(client_host, client_port),
            upstream_address=upstream_address,
            fsync=config.fsync,
        )
        upstream: socket.socket | None = None
        stop_relay = threading.Event()
        close_reason = "session_completed"

        try:
            tune_tcp_socket(self.request)
            recorder.event("client_connected")

            try:
                upstream = socket.create_connection(
                    upstream_address,
                    timeout=config.connect_timeout,
                )
                upstream.settimeout(None)
                tune_tcp_socket(upstream)
                recorder.event(
                    "upstream_connected",
                    upstream={
                        "host": config.upstream_host,
                        "port": config.upstream_port,
                    },
                )
            except OSError as exc:
                close_reason = "upstream_connect_error"
                recorder.event("upstream_connect_error", error=repr(exc))
                return

            def relay(
                source: socket.socket,
                destination: socket.socket,
                direction: str,
            ) -> None:
                nonlocal close_reason
                try:
                    while not stop_relay.is_set():
                        payload = source.recv(config.recv_size)
                        if not payload:
                            recorder.event("stream_eof", direction=direction)
                            close_reason = f"{direction}_eof"
                            break

                        # Record what the proxy observed before forwarding it.
                        recorder.data(direction, payload)
                        destination.sendall(payload)
                except OSError as exc:
                    if not stop_relay.is_set():
                        close_reason = f"{direction}_socket_error"
                        recorder.event(
                            "stream_error",
                            direction=direction,
                            error=repr(exc),
                        )
                finally:
                    stop_relay.set()
                    close_socket(source)
                    close_socket(destination)

            threads = [
                threading.Thread(
                    target=relay,
                    name=f"{recorder.session_id}-client-to-machine",
                    args=(
                        self.request,
                        upstream,
                        "client_to_machine",
                    ),
                    daemon=True,
                ),
                threading.Thread(
                    target=relay,
                    name=f"{recorder.session_id}-machine-to-client",
                    args=(
                        upstream,
                        self.request,
                        "machine_to_client",
                    ),
                    daemon=True,
                ),
            ]

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        except Exception as exc:
            close_reason = "handler_exception"
            recorder.event("handler_exception", error=repr(exc))
        finally:
            stop_relay.set()
            close_socket(self.request)
            if upstream is not None:
                close_socket(upstream)
            recorder.close(close_reason)
            self.server.state.release()
            self.server.journal.write(
                "session_closed",
                session_id=recorder.session_id,
                reason=close_reason,
            )


class RecordingProxyServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 8

    def __init__(
        self,
        server_address: tuple[str, int],
        config: ProxyConfig,
        state: ProxyState,
        journal: ProxyJournal,
    ) -> None:
        self.config = config
        self.state = state
        self.journal = journal
        super().__init__(server_address, RecordingProxyHandler)


def derive_local_ip(upstream_host: str, upstream_port: int) -> str:
    """Ask the OS which local IPv4 address it would use to reach the machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect((upstream_host, upstream_port))
        return str(sock.getsockname()[0])


def validate_port(value: int, label: str) -> int:
    if not 1 <= value <= 65535:
        raise SystemExit(f"{label} must be between 1 and 65535")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transparent Makera/Carvera TCP recording proxy"
    )
    parser.add_argument(
        "--upstream",
        required=True,
        help="Real Z1 IP address or hostname",
    )
    parser.add_argument(
        "--upstream-port",
        type=int,
        default=DEFAULT_CONTROL_PORT,
    )
    parser.add_argument(
        "--listen",
        help="Local interface to bind; defaults to the route toward --upstream",
    )
    parser.add_argument(
        "--listen-port",
        type=int,
        default=DEFAULT_CONTROL_PORT,
    )
    parser.add_argument(
        "--advertise-ip",
        help="IP placed in discovery packets; defaults to the route toward --upstream",
    )
    parser.add_argument(
        "--name",
        default="MAKERA_Z1_PROXY",
        help="Unique machine name shown to controllers",
    )
    parser.add_argument(
        "--broadcast",
        action="append",
        help=(
            "IPv4 broadcast destination; may be repeated. "
            "Default: 255.255.255.255"
        ),
    )
    parser.add_argument(
        "--discovery-port",
        type=int,
        default=DEFAULT_DISCOVERY_PORT,
    )
    parser.add_argument(
        "--advertise-interval",
        type=float,
        default=DEFAULT_ADVERTISE_INTERVAL,
    )
    parser.add_argument(
        "--no-advertise",
        action="store_true",
        help="Run as a TCP proxy without UDP discovery advertisements",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("z1-captures"),
    )
    parser.add_argument(
        "--connect-timeout",
        type=float,
        default=5.0,
    )
    parser.add_argument(
        "--recv-size",
        type=int,
        default=DEFAULT_RECV_SIZE,
    )
    parser.add_argument(
        "--fsync",
        action="store_true",
        help="Force capture data to disk after every chunk; safer but slower",
    )
    parser.add_argument(
        "--allow-client",
        action="append",
        default=[],
        metavar="IP_OR_CIDR",
        help=(
            "Only permit these client IPs/networks; may be repeated. "
            "With no entries, any client reaching the listener is accepted."
        ),
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    upstream_port = validate_port(args.upstream_port, "--upstream-port")
    listen_port = validate_port(args.listen_port, "--listen-port")
    discovery_port = validate_port(args.discovery_port, "--discovery-port")

    if args.advertise_interval <= 0:
        raise SystemExit("--advertise-interval must be greater than zero")
    if args.connect_timeout <= 0:
        raise SystemExit("--connect-timeout must be greater than zero")
    if args.recv_size < 1:
        raise SystemExit("--recv-size must be at least 1")
    if "," in args.name or "\n" in args.name or "\r" in args.name:
        raise SystemExit("--name may not contain commas or line breaks")

    try:
        routed_ip = derive_local_ip(args.upstream, upstream_port)
    except OSError as exc:
        raise SystemExit(
            f"Could not determine a local route to {args.upstream}:{upstream_port}: {exc}"
        ) from exc

    advertise_ip = args.advertise_ip or routed_ip
    listen_host = args.listen or advertise_ip
    broadcast_targets = tuple(args.broadcast or ["255.255.255.255"])

    try:
        ipaddress.ip_address(advertise_ip)
    except ValueError as exc:
        raise SystemExit(f"--advertise-ip is not a valid IP address: {exc}") from exc

    for target in broadcast_targets:
        try:
            ipaddress.ip_address(target)
        except ValueError as exc:
            raise SystemExit(f"Invalid --broadcast address {target!r}: {exc}") from exc

    secure_directory(args.log_dir)
    client_filter = ClientFilter(args.allow_client)

    config = ProxyConfig(
        upstream_host=args.upstream,
        upstream_port=upstream_port,
        listen_host=listen_host,
        listen_port=listen_port,
        advertise_ip=advertise_ip,
        advertised_name=args.name,
        broadcast_targets=broadcast_targets,
        discovery_port=discovery_port,
        advertise_interval=args.advertise_interval,
        log_dir=args.log_dir,
        connect_timeout=args.connect_timeout,
        recv_size=args.recv_size,
        fsync=args.fsync,
        advertise=not args.no_advertise,
        client_filter=client_filter,
    )

    state = ProxyState()
    stop_event = threading.Event()
    journal = ProxyJournal(config.log_dir, config.fsync)

    journal.write(
        "proxy_start",
        listen={"host": config.listen_host, "port": config.listen_port},
        upstream={"host": config.upstream_host, "port": config.upstream_port},
        discovery={
            "enabled": config.advertise,
            "name": config.advertised_name,
            "advertise_ip": config.advertise_ip,
            "targets": list(config.broadcast_targets),
            "port": config.discovery_port,
            "interval_seconds": config.advertise_interval,
        },
        allowed_clients=args.allow_client,
    )

    advertiser: DiscoveryAdvertiser | None = None
    if config.advertise:
        advertiser = DiscoveryAdvertiser(config, state, stop_event, journal)
        advertiser.start()

    try:
        with RecordingProxyServer(
            (config.listen_host, config.listen_port),
            config,
            state,
            journal,
        ) as server:
            print(
                f"Proxy:      {config.listen_host}:{config.listen_port}\n"
                f"Upstream:   {config.upstream_host}:{config.upstream_port}\n"
                f"Advertised: {config.advertised_name},"
                f"{config.advertise_ip},{config.listen_port},<busy>\n"
                f"Captures:   {config.log_dir.resolve()}\n"
                "Press Ctrl+C to stop."
            )
            if not args.allow_client:
                print(
                    "WARNING: no --allow-client restriction is active; "
                    "any host that can reach this listener may control the machine.",
                    file=sys.stderr,
                )
            server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        print("\nStopping proxy.")
    except OSError as exc:
        journal.write("proxy_bind_error", error=repr(exc))
        print(
            f"Could not listen on {config.listen_host}:{config.listen_port}: {exc}",
            file=sys.stderr,
        )
        return 2
    finally:
        stop_event.set()
        if advertiser is not None:
            advertiser.join(timeout=2.0)
        journal.write("proxy_stop")
        journal.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

readme = r'''# Makera Z1 recording proxy

`z1_mitm_proxy.py` is a byte-transparent TCP proxy for studying traffic between
Makera Studio or Community Carvera Controller and a Makera Z1.

## Network shape

```text
Controller application
        |
        | TCP to the advertised proxy IP:2222
        v
z1_mitm_proxy.py
        |
        | TCP to the real Z1 IP:2222
        v
Makera Z1
```

The proxy also broadcasts a discovery record on UDP port 3333:

```text
MAKERA_Z1_PROXY,<proxy-ip>,2222,<busy>
```

The final field changes to `1` while a controller is connected.

## Important limitations

- It records TCP **payload bytes**, not Ethernet/IP/TCP packet headers,
  retransmissions, ACKs, or Wi-Fi frames. Use Wireshark or tcpdump as well if
  packet-level information matters.
- It does not change or validate commands. Anything the controller sends reaches
  the machine.
- It is not an emulator. `version`, `model`, status, and all other replies still
  come from the real Z1.
- Use a unique advertised name. Do not use the real machine's name while both are
  broadcasting on the same LAN.
- Only one controller session is accepted at a time.
- Disconnect Makera Studio before starting another controller through the proxy.
- Captures can contain Wi-Fi settings, configuration data, filenames, and job
  contents. The proxy creates its capture directory with restrictive permissions
  where the operating system supports them.

## Start

Find the real Z1 IP address, then run:

```bash
python z1_mitm_proxy.py \
  --upstream 192.168.1.50 \
  --name MAKERA_Z1_PROXY \
  --broadcast 192.168.1.255 \
  --log-dir captures
```

Use the subnet-specific broadcast address where possible. For a `/24` network,
an address such as `192.168.1.50` normally uses `192.168.1.255`.

The proxy automatically derives the local IP used to reach the Z1. Override it
when needed:

```bash
python z1_mitm_proxy.py \
  --upstream 192.168.1.50 \
  --listen 192.168.1.20 \
  --advertise-ip 192.168.1.20 \
  --broadcast 192.168.1.255
```

Then open the controller application and select `MAKERA_Z1_PROXY`.

## Restrict who may connect

The proxy has no authentication. Restrict it to the computer running the
controller:

```bash
python z1_mitm_proxy.py \
  --upstream 192.168.1.50 \
  --broadcast 192.168.1.255 \
  --allow-client 192.168.1.20
```

CIDR networks are accepted too:

```bash
--allow-client 192.168.1.0/24
```

Use a host firewall in addition to this filter.

## Capture files

Each session produces:

```text
session-<id>.jsonl
session-<id>-client-to-machine.bin
session-<id>-machine-to-client.bin
```

The JSONL file contains timestamped events. Every data event includes:

- Direction
- Exact byte count
- Cumulative byte count
- Full base64 payload
- UTF-8 preview
- Monotonic and UTC timestamps

The session-ending event contains SHA-256 hashes for both raw streams.

A separate `proxy-<timestamp>.jsonl` records startup, advertisements, rejected
connections, session closure, and shutdown.

## Validate capture hashes

Example:

```bash
python - <<'PY'
from pathlib import Path
import hashlib

for path in Path("captures").glob("*.bin"):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(digest, path)
PY
```

## Run without discovery

For a controller that accepts a manual IP and port:

```bash
python z1_mitm_proxy.py \
  --upstream 192.168.1.50 \
  --no-advertise
```

Connect the application manually to the proxy computer's IP on port 2222.

## Packet-level capture

For Linux, run a packet capture in parallel when exact TCP/IP behavior matters:

```bash
sudo tcpdump -i any -s 0 -w z1-proxy.pcap \
  'tcp port 2222 or udp port 3333'
```

The application logs answer “what bytes did each side send, and when?” The PCAP
answers “how were those bytes transported on the network?”
'''

out_dir = Path("/mnt/data/z1_proxy")
out_dir.mkdir(parents=True, exist_ok=True)
proxy_path = out_dir / "z1_mitm_proxy.py"
readme_path = out_dir / "README.md"
proxy_path.write_text(proxy_code, encoding="utf-8")
readme_path.write_text(readme, encoding="utf-8")
proxy_path.chmod(0o755)

zip_path = Path("/mnt/data/z1-recording-proxy.zip")
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    zf.write(proxy_path, arcname=proxy_path.name)
    zf.write(readme_path, arcname=readme_path.name)

print(proxy_path)
print(readme_path)
print(zip_path)

```

Yes. I built a transparent recording proxy:

```text
Controller application
        │ TCP :2222
        ▼
Z1 recording proxy
        │ TCP :2222
        ▼
Real Makera Z1
```

The proxy broadcasts a separate discovery entry on UDP port **3333**, using the four fields expected by Community Controller: machine name, IP, TCP port, and busy state. It forwards the TCP stream without interpreting or modifying it. fileciteturn5file0L2-L2

### Files

[Download the complete proxy package](sandbox:/mnt/data/z1-recording-proxy.zip)

[Python proxy script](sandbox:/mnt/data/z1_proxy/z1_mitm_proxy.py)  
[Setup and capture guide](sandbox:/mnt/data/z1_proxy/README.md)

I tested it locally with text, binary data, null bytes, `0xff`, and control characters. The forwarded and recorded byte streams matched exactly, including their SHA-256 hashes.

## Run it

Assuming:

- Real Z1: `192.168.1.50`
- Proxy computer: on the same subnet
- Network broadcast: `192.168.1.255`

```bash
python z1_mitm_proxy.py \
  --upstream 192.168.1.50 \
  --name MAKERA_Z1_PROXY \
  --broadcast 192.168.1.255 \
  --log-dir captures
```

Then select **`MAKERA_Z1_PROXY`** in the controller application.

Use a unique name. Community Controller deduplicates discovery results by machine name, so using the real Z1’s name while both are broadcasting can cause unpredictable selection. fileciteturn5file0L2-L2

## What gets recorded

Each connection creates:

```text
session-<id>.jsonl
session-<id>-client-to-machine.bin
session-<id>-machine-to-client.bin
```

The JSONL capture contains:

- Exact base64-encoded payload bytes
- Direction
- UTC and monotonic timestamps
- Byte counts
- Human-readable UTF-8 preview
- Connection events and errors
- Final SHA-256 hashes

The raw `.bin` files contain the uninterrupted byte stream in each direction. This includes newline commands, real-time control bytes, status responses, and binary XMODEM transfers.

## Important boundaries

This is an **application-stream capture**, not a packet capture. It records every TCP payload byte seen by the proxy, but not TCP retransmissions, ACKs, packet headers, or Wi-Fi frames. For those, run Wireshark or `tcpdump` simultaneously:

```bash
sudo tcpdump -i any -s 0 -w z1-proxy.pcap \
  'tcp port 2222 or udp port 3333'
```

The proxy does not filter commands. A spindle, laser, motion, reset, or configuration command sent by the application will reach the physical machine unchanged. Disconnect other controller applications and keep the machine in a safe, cleared state.

The discovery implementation is based directly on Community Controller. It should also be testable with Makera Studio, but Makera Studio’s current discovery behavior is proprietary and has not been verified here.

The next logical extension is a replay mode that impersonates the Z1 without connecting to the physical machine, using these recordings as protocol fixtures.

