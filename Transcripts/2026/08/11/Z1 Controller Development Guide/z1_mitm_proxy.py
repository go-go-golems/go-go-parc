#!/usr/bin/env python3
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
