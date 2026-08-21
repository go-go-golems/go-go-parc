# Makera Z1 recording proxy

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
