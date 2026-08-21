# Makera Z1 Overview

- URL: https://chatgpt.com/c/6a6e39f1-a3a0-83ea-8bf4-52806d586386
- Created: 2026-08-01T18:25:21.022Z

---

> explain to me the whole constellation of opensource and firmware and makera studio and makeracam and makera controller and the protocol over wifi and usb and who has reversed engineered it for the makera z1 desktop cnc, which i just received yesterday.

I’ll map the Z1 stack from the top-level apps down to firmware and transport, then separate official open-source components from community reverse-engineering.

```json
{"system1_search_query":[{"q":"Makera Z1 official documentation Makera Studio MakeraCAM Makera Controller firmware WiFi USB protocol"},{"q":"site:github.com Makera Z1 CNC reverse engineering protocol"},{"q":"site:github.com Makera MakeraCAM Makera Studio controller firmware"},{"q":"site:forum.makera.com Z1 USB WiFi protocol firmware"}],"image_query":[{"q":"Makera Z1 desktop CNC official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 7 websites**

</details>

The machine is not a closed black box: its motion firmware is a Makera fork of Smoothieware, while the desktop controller is a separate application layer. The unresolved part is exactly how the newer Z1 software names map onto that older Carvera stack.

```json
{"system1_search_query":[{"q":"site:makera.com Makera Studio Z1 software"},{"q":"site:wiki.makera.com MakeraCAM Makera Studio Z1"},{"q":"site:github.com/MakeraInc MakeraCAM Makera Studio"},{"q":"\"Makera Studio\" CNC"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

</details>

```unknown
bash -lc rm -rf /tmp/carvera_controller /tmp/carvera_firmware /tmp/carvera_profiles /tmp/makeracam /tmp/community_docs && git clone --depth 1 https://github.com/Carvera-Community/Carvera_Controller.git /tmp/carvera_controller && git clone --depth 1 https://github.com/MakeraInc/CarveraFirmware.git /tmp/carvera_firmware && git clone --depth 1 https://github.com/MakeraInc/CarveraProfiles.git /tmp/carvera_profiles && git clone --depth 1 https://github.com/MakeraInc/MakeraCAM.git /tmp/makeracam && git clone --depth 1 https://github.com/Carvera-Community/docs.git /tmp/community_docs
```

<details><summary>💭 Thinking</summary>

**Cloned repositories for controller analysis**

</details>

Two concrete transport clues are already documented: USB enumerates as an FTDI FT232R serial port, and the controller uses UDP port 3333 for network discovery. The actual command/file-transfer channel needs source-level inspection.

```json
{"system1_search_query":[{"q":"site:github.com/Carvera-Community/Carvera_Controller \"3333\""},{"q":"site:github.com/Carvera-Community/Carvera_Controller socket serial usb wifi protocol"},{"q":"site:github.com/Carvera-Community/Carvera_Controller \"QuickLZ\""},{"q":"site:github.com/Carvera-Community \"Carvera CLI\""}],"response_length":"long"}
```

```json
{"paths":["GitHub"],"query":"search code"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search","args":{"query":"3333","repository_name":"Carvera-Community/Carvera_Controller","topn":20}}
```

<details><summary>💭 Thinking</summary>

**Searched GitHub for “3333” references and fetched WiFi and USB streams**

</details>

```json
{"open":[{"ref_id":"https://github.com/Carvera-Community/Carvera_Controller/blob/main/carveracontroller/WIFIStream.py"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search","args":{"query":"serial.Serial","repository_name":"Carvera-Community/Carvera_Controller","topn":20}}
```

<details><summary>💭 Thinking</summary>

**Searched repository for USB stream source**

</details>

```json
{"open":[{"ref_id":"https://github.com/Carvera-Community/Carvera_Controller/blob/main/carveracontroller/USBStream.py"},{"ref_id":"https://github.com/Carvera-Community/Carvera_Controller/blob/main/carveracontroller/XMODEM.py"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search","args":{"query":"stream.send","repository_name":"Carvera-Community/Carvera_Controller","topn":20}}
```

<details><summary>💭 Thinking</summary>

**Inspected command protocol logic**

</details>

```json
{"open":[{"ref_id":"https://github.com/Carvera-Community/Carvera_Controller/blob/main/carveracontroller/Controller.py"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search","args":{"query":"Z1","repository_name":["MakeraInc/CarveraFirmware","Carvera-Community/Carvera_Community_Firmware","Carvera-Community/Carvera_Controller","MakeraInc/CarveraController","MakeraInc/MakeraCAM"],"topn":50}}
```

<details><summary>💭 Thinking</summary>

**Searched GitHub repositories and branches for Makera Z1 firmware code**

</details>

```json
{"open":[{"ref_id":"https://github.com/MakeraInc/CarveraFirmware/releases"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Verifying Z1 documentation**

I’m checking official documentation and repositories to separate confirmed Z1 connectivity details from Carvera-specific firmware information. The available evidence supports caution: I shouldn’t assume Z1 firmware source is publicly published in the same repository.

**Separating findings**

I’m treating the absence of a public Z1-specific source branch as evidence, not proof. I’m also distinguishing public repositories from genuinely open-source projects, while reviewing community firmware and controller forks as related Carvera resources.

**Verified Z1 documentation and separated findings**

</details>

```json
{"open":[{"ref_id":"turn378874view4","lineno":150},{"ref_id":"turn378874view0","lineno":145},{"ref_id":"turn886303search3"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search_issues","args":{"query":"Z1","repository_full_name":"Carvera-Community/Carvera_Controller","topn":20,"state":"open"}}
```

<details><summary>💭 Thinking</summary>

**Searched Open Z1 issues**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_issue","args":{"issue_number":692,"repository_full_name":"Carvera-Community/Carvera_Controller"}}
```

<details><summary>💭 Thinking</summary>

**Investigated GitHub firmware issues, pull requests, comments, and model detection changes**

</details>

```json
{"open":[{"ref_id":"turn395558search1"},{"ref_id":"turn886303search0"},{"ref_id":"turn530556view2","lineno":210},{"ref_id":"turn530556view5","lineno":215}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

## The overall architecture

The Z1 software stack is easiest to understand as five separate layers:

```text
Design file
  ↓
CAM: Makera Studio / MakeraCAM / Fusion / Kiri:Moto
  ↓
G-code or NC file
  ↓
Machine controller: Studio Control / Makera App / Community Controller
  ↓
Wi-Fi or USB transport
  ↓
Z1 firmware → motors, spindle, probing, camera and auxiliary outputs
```

**Makera Studio collapses the middle three user-facing stages into one application.** It imports designs, generates toolpaths, simulates them, transfers the resulting NC file, and controls the machine. The Z1 documentation tells owners to use Studio’s **Control** tab on desktop or the **Device** page in the Makera App. citeturn118239search0turn633007view2

## What each Makera name means

### Makera Studio

This is the new desktop application and the main Z1 interface. Makera describes it as “CAM + Controller, unified.” It includes toolpath generation, tool selection, simulation, file management and machine operation. For the Z1, it is the prescribed software; for existing Carvera and Carvera Air owners, Makera’s software page still describes the current 2026 release as a closed beta. citeturn633007view2turn118239search0

Studio is therefore not merely a renamed Controller. It absorbs both:

- MakeraCAM’s toolpath-generation role.
- Carvera Controller’s machine-control role.

I found no public Studio source repository or published Studio protocol specification. Makera distributes Windows and macOS binaries directly.

### Makera App

This is the mobile companion and what Makera calls “the new Makera Controller.” It can discover the Z1, configure Wi-Fi, browse files, start jobs and monitor the built-in camera. Bluetooth is used to provision the Z1 onto Wi-Fi; normal operation is over USB, the Z1’s AP, or the local Wi-Fi network. Bluetooth is not presented as the normal machining-data channel. citeturn157010view1turn118239search0

### MakeraCAM

MakeraCAM is the older standalone CAM application, primarily for the Carvera and Carvera Air. It converts geometry into toolpaths and G-code but historically leaves connection, jogging, file transfer and execution to Carvera Controller.

Its GitHub repository is public, but it contains only four commits and explicitly says that it exists to manage **binary releases**. There is no public MakeraCAM source code there. citeturn633007view0

### Carvera Controller

This is the older control application. It handles:

- Machine discovery and connection.
- Jogging and probing.
- File upload/download and management.
- Running, pausing and resuming NC files.
- Firmware updates.
- Machine configuration.

Makera’s official repository has a GPL-3.0 license and an older source/release tree, although its README also describes it as the place that manages binary releases. It documents the older Carvera USB interface as an FTDI FT232R serial device. citeturn633007view1

The actively developed community fork is a separate repository called **Community Carvera Controller**, licensed GPL-2.0. It has additional probing, pendant, jogging, privacy and quality-of-life features. citeturn329887view1

### Makerables

Makerables is not firmware or control software. It is Makera’s project-sharing platform: models, prepared projects and potentially toolpath recipes that Studio can consume. It is conceptually equivalent to a CNC-oriented project library. citeturn157010view1

---

## What is actually open source

| Component | Public source status | Z1 relevance |
|---|---|---|
| Smoothieware | Open source | Foundation of the older Makera firmware family |
| Makera `CarveraFirmware` | GPL-3.0 source | Explicitly describes Carvera, not Z1 |
| Official Carvera Controller | GPL-3.0 repository and older source tree | Legacy Carvera/Air controller |
| MakeraCAM | Binary-release repository only | Legacy CAM |
| Makera Studio / App | No public source found | Official Z1 software |
| Z1 firmware | No public Z1-specific source found | Runs on your machine |
| Community Controller | GPL-2.0 | Initial Z1 support has already been merged |
| Community Firmware | Open-source Smoothieware fork | No completed Z1 firmware port yet |
| `carvera-cli` | Open-source Python CLI | Implements the legacy protocol; Z1 support is not yet formally documented |
| Community profiles | Open post-processors and tool libraries | Potentially useful once Z1 profiles stabilize |

Makera’s public `CarveraFirmware` is a branch of Smoothieware. Smoothieware is a C++ G-code interpreter and motion controller for the LPC17xx ARM Cortex-M3 platform, with motion-control ancestry from GRBL. The repository builds firmware for the LPC1768 and identifies itself specifically as firmware for the Makera Carvera. citeturn157010view2

The community firmware is a much more actively developed descendant. It is maintained by **Fae Corrigan** and adds functionality beyond Makera’s firmware. However, there is not yet a released Z1 community-firmware build, and the current Z1 discussion explicitly warns that the firmware updater presently offers an inappropriate older-machine image. Do not flash a Carvera or Carvera Air community firmware image onto the Z1. citeturn157010view3 fileciteturn8file0L25-L45

The available evidence suggests that Z1 firmware remains closely related at the command/configuration level to Makera’s Smoothieware-derived family. But because Makera has not published the Z1 source, its processor, bootloader, low-level USB implementation and proprietary additions should not be assumed to match the LPC1768 Carvera exactly.

---

# The legacy Makera wire protocol

The old protocol is surprisingly straightforward. It is not REST, HTTP, MQTT, WebSocket or gRPC. It is essentially:

> A persistent byte stream carrying line-oriented G-code and console commands, with XMODEM temporarily taking over the same stream for file transfers.

The command language is largely the same over Wi-Fi and USB. The transport underneath it changes.

## Wi-Fi

The open Community Controller implementation shows:

- **UDP port 3333** for discovery.
- **TCP port 2222** for the primary command and data stream.
- Discovery packets decoded as comma-separated UTF-8 fields:
  `machine name, IP address, TCP port, busy flag`.
- A plain TCP socket is opened for normal communication.
- Wi-Fi file transfers use an extended `xmodem8k` mode. citeturn241569view0turn241569view1turn241569view2

The controller listens on UDP 3333 for machine advertisements. It then connects to the advertised address, normally TCP 2222.

The open implementation does not put TLS around the TCP socket. Operationally, the machine should remain on a trusted LAN or its own isolated AP; port 2222 should not be forwarded to the internet.

## Text commands

Commands are normally UTF-8 text terminated by a newline. The controller accepts ordinary G-code plus Smoothieware/GRBL-style immediate characters such as:

- `?` — status query.
- `!` — feed hold.
- `~` — resume.
- `$...` — state/settings commands.
- `G...` and `M...` — motion and machine functions.

Makera also added many custom commands and M-codes. Examples visible in the open controller include:

- `version`
- `model`
- `ls -e -s`
- `cat`
- `rm`
- `mv`
- `mkdir`
- `md5sum`
- `wlan -e`
- `M493...`, `M495...` and `M496...` families for tools, probing, margins and predefined moves.

The client literally appends `\n` and writes the encoded bytes to whichever stream is active. citeturn329887view4turn329887view5

Some filename characters are escaped using small control-byte substitutions. For example, spaces become byte `0x01`, while `?`, `&`, `!` and `~` are substituted because those characters have real-time control meanings. citeturn329887view5

## File transfer

File management begins as a text command, such as an upload or download request. The connection then switches into XMODEM transfer mode.

The open implementations show:

- XMODEM over both USB and Wi-Fi.
- `xmodem8k` for Wi-Fi.
- Conventional XMODEM for older USB serial.
- MD5 checking.
- Optional compressed `.lz` files using QuickLZ-era support.

This is why a generic G-code sender may be able to issue basic commands but still fail at Makera-style file upload, firmware update or compressed transfer.

---

# USB: older Carvera versus the Z1

## Older Carvera and Carvera Air

The older USB connection is ordinary serial:

```text
FTDI FT232R
115200 baud
8 data bits
no parity
1 stop bit
no hardware or software flow control
```

The Community Controller opens the serial stream at 115200 8N1 and uses the same newline-oriented commands and XMODEM transfer method as Wi-Fi. citeturn241569view3turn241569view4

## Z1

The Z1 appears to have changed the **USB transport**. The current community investigation says that it appears to expose a **WinUSB** device rather than a conventional COM-port/FTDI serial device. The USB implementation remains one of the outstanding Z1 tasks. fileciteturn8file0L69-L89

That probably means:

```text
Same or closely related application-level command protocol
                    ↓
Different USB framing/driver layer using WinUSB
```

It does **not** currently justify assuming that opening a 115200-baud COM port will work. Avoid replacing the Z1’s driver with the older FTDI package.

Wi-Fi is therefore the easier route for current community experimentation.

---

# How much of the Z1 has been reverse engineered?

The answer is: **the network/control compatibility is now demonstrated, but USB and several Z1-specific functions remain unfinished.**

On July 22, 2026, GitHub user **Michael Ring (`michael-ring`)** opened the Z1-support issue in Community Controller and reported that the Z1 protocol appeared to be the same as recent Makera firmware and was already usable in principle. fileciteturn7file0L3-L21

His initial Z1 support pull request was merged into the Community Controller’s development branch on July 24. It required only a Z1 configuration file, model-specific dimensions and UI changes—not a new Wi-Fi protocol backend. That is strong practical evidence that the existing Carvera TCP protocol works with the Z1. fileciteturn10file0L2-L14 fileciteturn10file0L26-L33

The main people and projects currently visible are:

**Michael Ring**  
Produced and merged the initial Community Controller Z1 port and identified Z1 configuration values.

**Serge Bakharev**  
Has been coordinating the remaining controller work, documenting missing Z1 functions and identifying the likely WinUSB difference. The open items include camera integration, RSSI, dust/vacuum controls, auto-blow, bed cleaning, antistatic support and smoother jogging. fileciteturn8file0L3-L23 fileciteturn8file0L25-L67

**Carvera-Community**  
Maintains the open controller, firmware fork, profiles and documentation. Much of this is not clean-room reverse engineering because Makera published significant portions of the older firmware and controller under GPL. The community has extended and documented that source.

**Fae Corrigan**  
Maintains the Community Firmware branch. citeturn157010view3

**`hagmonk`**  
Created `carvera-cli`, a Python implementation that can discover machines over Wi-Fi or USB, send arbitrary commands, manage files, read configuration and upload firmware. It is one of the clearest independent, non-GUI expressions of the protocol. citeturn329887view0

There are also adjacent implementations such as GridSpace’s `carve-control`, AngryApostrophe’s Clout and generic Smoothieware-compatible senders such as CNCjs. They are part of the ecosystem, but they should not automatically be considered fully Z1-compatible. citeturn157010view3

---

# Current Z1 compatibility status

As of **August 1, 2026**:

**Working or substantially demonstrated**

- Z1 recognition in the Community Controller development branch.
- Existing Carvera-style Wi-Fi command protocol.
- Basic file/configuration access.
- Standard G-code and Makera command handling.
- Z1-specific machine dimensions and configuration presentation.

**Incomplete or under active investigation**

- Direct USB support through WinUSB.
- Z1 camera support; a work-in-progress pull request exists.
- Safe community-firmware installation.
- Some Z1-specific dust, air-blow, cleaning and antistatic controls.
- Complete mapping of new Z1-specific M-codes.
- 3D-probing behavior under Makera’s stock Z1 firmware.
- Pendant/jogging smoothness.

**Not publicly available**

- Z1 firmware source.
- Makera Studio source.
- Makera App source.
- A formal protocol specification.
- A finished Z1 community-firmware release.

---

# Sensible sequence for your new machine

For the first several jobs, use the official Studio/App workflow and the included example. Record your Z1 firmware version, model response and Studio version before experimenting.

For community work, use the Community Controller’s current development build over **Wi-Fi**, not USB. Restrict initial tests to read-only operations such as machine discovery, `version`, `model`, `?`, directory listing and configuration retrieval. Do not test movement or spindle commands while a tool or workpiece is installed.

A passive Wireshark capture while Studio connects should use:

```text
udp.port == 3333 || tcp.port == 2222
```

That should expose discovery and the command stream if the Z1 follows the demonstrated legacy network path. Expect the traffic to be largely readable text until an XMODEM file transfer begins.

Do not flash any Carvera, Carvera Air or Community Firmware image onto the Z1. The current community controller can talk to the stock Z1 firmware; that does not mean the older firmware binaries are hardware-compatible.

genui{"suggest_automation":{"label":"Notify me when Z1 USB or community firmware support lands"}}

