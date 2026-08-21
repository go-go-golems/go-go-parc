# Makera Z1 G-code Software

- URL: https://chatgpt.com/c/6a7b84c6-56cc-83ea-bbaa-17e1fb323499
- Created: 2026-08-11T20:23:55.965Z

---

> i want to write my own makera z1 application to send gcode, apparently it uses the same protocol and setup than previous machines, and there's some opensource software out there. What is it?

I’ll trace the Z1 back through Makera’s earlier Carvera machines, then identify the open-source sender/controller code and the protocol details you can reuse.

```json
{"system1_search_query":[{"q":"Makera Z1 protocol same as Carvera open source software G-code sender GitHub"},{"q":"Makera Carvera open source controller software GitHub protocol"},{"q":"Carvera Air gcode sender open source Makera GitHub"},{"q":"Makera Z1 developer protocol gcode websocket tcp serial"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

</details>

The key lead is better than a generic GRBL sender: there is a **Carvera-specific CLI** plus two open controller implementations. I’m checking which one exposes the wire protocol most cleanly.

```json
{"open":[{"ref_id":"turn378960view2","lineno":170},{"ref_id":"turn378960view3","lineno":170}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

Yes. The project you’re probably looking for is **Carvera Community Controller**:

**`Carvera-Community/Carvera_Controller`** — an open-source replacement for Makera’s controller software. Most importantly, its current **v2.2.0-RC1 explicitly adds “Initial Z1 support”**, including automatic detection of the older Smoothie protocol versus Makera’s newer communication protocol. citeturn378960view1turn824509view0

There are actually several useful repositories:

- **Carvera Community Controller** — best reference for the **Z1 specifically**. It is Python/Kivy and GPL-2.0. The August 4, 2026 v2.2.0-RC1 adds Z1 support and even Z1 camera support. citeturn824509view0
- **MakeraInc/CarveraController** — Makera's older controller source. This is extremely useful because the networking/protocol implementation is right there in Python. citeturn410261view0turn378960view0
- **`hagmonk/carvera-cli`** — small MIT-licensed Python command-line implementation supporting discovery, commands, G-code upload/download, Wi-Fi and USB. Probably the easiest codebase to understand, although I would use the Community Controller as the authoritative reference for **Z1 compatibility**. citeturn275053view0
- **`GridSpace/carve-control`** — MIT-licensed Node/JS implementation specifically designed for protocol inspection, command injection, uploading/downloading and proxying a Carvera connection. Useful for understanding/debugging the protocol. citeturn275053view1

### The protocol is quite approachable

For Wi-Fi, Makera's source shows:

```text
UDP 3333     machine discovery
TCP 2222     controller connection
```

The machine broadcasts discovery records resembling:

```text
machine_name,ip_address,tcp_port,busy
```

and the controller then opens a normal TCP socket to the advertised address, defaulting to port **2222**. citeturn616592view1

The interesting part is that newer firmware — which includes the protocol relevant to the Z1 — wraps commands in a simple binary frame. Makera's own source defines: citeturn274497view0turn313655view0

```text
HEADER       0x8668     2 bytes, big endian
LENGTH                   2 bytes, big endian
TYPE
PAYLOAD
CRC16                    2 bytes, big endian
FOOTER       0x55AA     2 bytes
```

Packet types currently visible in Makera's source include:

```text
0xA1   single-character control command
0xA2   normal / multi-character command
0xB0   start file-transfer command

responses:
0x81   status
0x82   diagnostics
0x83   load info
0x84   load finished
0x85   load error
0x90   normal informational output
```

The CRC is **CRC-16/CCITT using polynomial `0x1021`, initial CRC `0`**, computed over:

```text
length + packet_type + payload
```

—not over the `0x8668` header or `0x55AA` footer. citeturn313655view0

So a normal command is essentially:

```text
86 68
00 NN
A2
<ASCII command>
CC CC
55 AA
```

For example the logical payload could simply be:

```text
version
```

or a G-code/MDI command such as:

```text
G0 X10 Y10
```

The old firmware path was even simpler: newline-delimited text directly over the socket. The current controller contains both implementations and switches between them. citeturn769074view1turn824509view0

### Sending an actual G-code file

Makera doesn't appear to stream the entire job one G-code line at a time from the PC. The normal workflow is:

```text
PC
 │
 ├── upload /sd/.../part.nc
 │       │
 │       └── file data transfer
 │
 └── play /sd/.../part.nc
         │
         ▼
       machine runs locally
```

The official controller literally generates `upload <filename>`, performs the file transfer, then uses `play <filename>` to execute it. Pause/resume/abort use commands such as `suspend`, `resume`, `abort`, while GRBL-style realtime characters `!`, `~`, and `0x18` are also supported through the single-character packet type. citeturn313655view2

File transfers use an **XMODEM-derived implementation**, and Makera's Wi-Fi transport hooks that transfer directly onto the same TCP socket. citeturn616592view1turn790120view1

So for your own Z1 app, I would start with **Carvera Community Controller v2.2.0-RC1**, not GRBL/CNCjs. It already contains the newly added Z1 compatibility logic. Then pull the communications layer out into something like:

```text
MakeraClient
 ├── discover()          UDP :3333
 ├── connect()           TCP :2222 / USB serial
 ├── send_command()
 ├── query_status()
 ├── upload_file()
 ├── download_file()
 ├── play()
 ├── pause()
 ├── resume()
 └── abort()
```

The protocol is simple enough that writing a small native client in **TypeScript, Python, Rust, Swift, C#, etc.** shouldn't require much code.

If you tell me what language/platform you want your Z1 application in, I can next map the open-source implementation into a **minimal Z1 protocol library** and give you working code for discovery → connect → status → upload `.nc` → run.

