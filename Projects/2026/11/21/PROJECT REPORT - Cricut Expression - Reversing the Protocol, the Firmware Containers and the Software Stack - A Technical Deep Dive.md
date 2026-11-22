---
title: "Reversing the Cricut Expression: Protocol, Firmware Containers, and the Software Stack — A Technical Deep Dive"
aliases:
  - libcutter report
  - cricut expression deep dive
  - cricut-re-001 report
tags:
  - project
  - reverse-engineering
  - cricut
  - firmware
  - wine
  - avr
  - xxtea
status: active
type: project
created: 2026-11-21
repo: /home/manuel/code/wesen/2026-11-21--cricut
---

# Reversing the Cricut Expression: Protocol, Firmware Containers, and the Software Stack — A Technical Deep Dive

The Cricut Expression (CRX001, sold 2006–2013) is an X/Y craft cutter driven by an ATmega1281 microcontroller and an FTDI FT232BM USB-serial bridge. ProvoCraft sold it with cartridges containing encrypted design data and PC software whose firmware updates ship inside encrypted `.enc` containers. This report documents the machine's serial protocol, the community reverse-engineering that made third-party control possible, the two software control paths available today (a Windows-only GUI host under wine, and a native Linux library), and a completed static analysis that locates the firmware-container decryption code in the host software with all cryptographic key material hardcoded in that same module. The report will be updated as work continues; sections written after the initial commit are marked by their diary step.

The report is organised in dependency order. Sections 2 to 4 establish the hardware, the serial protocol, and the cryptographic scheme. Sections 5 to 7 describe the software stack: the library, the plugin host, and the firmware-replacement firmware. Sections 8 and 9 cover the firmware images: where they were obtained, their container format, and where the decryption code lives. Section 10 records the open questions and next steps.

> [!summary]
> - **The serial protocol is fully published.** Packets are length-prefixed, 16-bit values are byte-swapped per value, and motion commands (0x40) carry XXTEA-encrypted coordinates. The link runs at 198,347 bps through an FTDI FT232BM, requiring either the D2XX driver or a custom Linux UART clock divisor.
> - **Eight 16-byte XXTEA keys were extracted and published.** Move, line-cut, and curve-cut each use a distinct key. The mapping matters: using the line key for curve cuts does not fail; it silently produces gapped cuts because each segment lifts the blade.
> - **Two control paths exist for stock firmware.** A Windows GUI host (Sure Cuts A Lot 5/6 plus a plugin built on the libcutter library) under wine, and the same library built natively on Linux with command-line SVG and G-code cutters plus a joystick-driven realtime mode.
> - **The firmware update containers are decryptable offline.** The host software performs the decryption: `Cricut USB.dll` contains textbook XXTEA encrypt and decrypt routines and hardcodes all eight protocol keys as immediate constants. The bootloader only receives plaintext blocks.
> - **A complete firmware set was recovered from community archives.** All eight published images, from Personal v1.1 through Expression v2.34 (a/b pair), are ASCII-hex-encoded encrypted containers, with two header generations corresponding to a container-format revision.

## 1. Scope, sources, and evidence

The work lives in ticket **CRICUT-001** at `/home/manuel/code/wesen/2026-11-21--cricut`, with a 13-step implementation diary at `ttmp/2026/11/21/CRICUT-001--get-libcutter-running-with-wine-for-cricut-expression/diary/01-diary-libcutter-under-wine.md`. Every claim in this report traces to one of three evidence classes:

| Evidence class | Where | Examples |
|---|---|---|
| Primary source code | `/tmp` clones, recorded by hash | libcutter `lib/device_c.cpp`, `include/btea.h` |
| Archived artifacts in-repo | `downloads/` | firmware `.enc` files, installers, keys.h |
| Archived web pages | `ttmp/.../sources/` | Cricut Hacking Wiki pages, forum threads, blog posts |

The Cricut Hacking Wiki (built-to-spec.com, 2010–2013, recovered and mirrored at jimlund.org) is the foundational document for hardware and protocol. The libcutter project (vangdfang, 2010, Cowtown Computer Congress KC) is the foundational implementation. This report's original contributions are: the live-mirror recovery of the installer and firmware artifacts (Sections 8–9), the static analysis locating the decryption code (Section 9), and the falsification test of one published key mapping (Section 4.3).

## 2. Hardware

The Expression mainboard pairs an **ATmega1281** at 16 MHz with an **FTDI FT232BM** USB-serial bridge. Two stepper motors (NEMA-17 class, driven by eight MOSFETs) move the mat on X and the cutting head on Y. The cutting tool is a drag knife in a solenoid holder; pressure is pulse-width-modulated at 12 V. Three front-panel dials (speed, pressure, size) are read by the firmware only at power-up.

The wiki's fuse analysis explains the machine's boot behaviour. The ATmega1281 reads with device signature `0x1E9704`, not the datasheet-standard `0x1E9702`; the difference is believed to mark a non-retail production batch. The fuse configuration is: low `0xFF` (external crystal, 16K clock cycles plus 65 ms startup delay), high `0xD8` (boot reset vector into a 4,096-word bootloader section), extended `0xFC` (watchdog always on, ATmega103 compatibility mode). Flash and EEPROM are security-locked: reads return `0xFF`. This is why the stock firmware cannot be dumped from a machine — and why recovering the *update images* from installer media (Section 8) is the only way to obtain it.

The cartridge interface uses the same ATmega family as the mainboard: each cartridge contains an ATmega16 and a 4-Mbit flash holding encrypted design data, exposed on a 6-pin in-circuit-programming header. The cartridge that ships with every machine, George and Basic Shapes, is an exception: it is a PCB with two shorted pins. It functions as an authorization key, not as storage.

## 3. The serial protocol

### 3.1 Physical layer

The FT232BM enumerates as a USB-serial converter, but the baud rate is non-standard: **198,347 bps**, 8N1, no flow control. The wiki derives this from FTDI application note AN232B-05 and observes that the FTDI's 3% clock tolerance allows communication at 200,000 bps in practice. Two consequences follow. On Windows, the host must use the FTDI D2XX driver, which permits arbitrary divisor values; standard serial APIs reject the rate. On Linux, a standard `ttyUSB` device accepts only standard rates, so a native driver must set a custom UART clock divisor through the FTDI-specific ioctl interface. This single number is the main reason the wine path exists at all: the Windows D2XX stack hides the divisor work inside a vendor driver.

Two empirical behaviours constrain any implementation. The LCD flashes "USB Active" whenever serial data arrives at any baud rate, which makes wrong-baud debugging observable. Large burst writes cause the device to reset itself; the FTDI's 384-byte receive buffer comfortably exceeds any single documented command, so the reset appears tied to sustained overrun rather than single-packet overflow.

### 3.2 Packet format

Every packet, in both directions, begins with a length byte counting the bytes that follow it. Commands are four bytes: the command byte followed by padding. Responses carry a length byte followed by 16-bit little-endian words. The wiki's example is worth reproducing because it demonstrates the byte-swap rule that produces the most common parsing error:

```
Send: 04 11 00 00 00      (Mat Bounds request, 0x11)
Recv: 08 01 3c 00 32 13 62 12 58
```

The response decodes as `01 3C` = 316, `00 32` = 50, `13 62` = 4,962, `12 58` = 4,696. Within each 16-bit value, the bytes arrive swapped relative to the value's natural order; the array as a whole is not reversed. A reversal of the full array produces four wrong values; a per-value swap produces the correct four.

The documented command set:

| Command | Code | First generation | Second generation |
|---|---|---|---|
| Mat Bounds | 0x11 | yes | yes |
| Firmware version | 0x12 | yes | yes |
| Status request | 0x14 | yes | yes |
| Cartridge name | 0x18 | yes | no |
| Start transaction | 0x21 | yes | no |
| Stop transaction | 0x22 | yes | no |
| Move command | 0x40 | yes | no |
| Unknown | 0x81 | yes | no |

Coordinate units are **404 ticks per inch**, separately on each axis (X is mat movement, Y is cutter movement). An Expression with a 12×12 mat reports bounds (316, 50, 4,962, 4,696), which is 4,646×4,646 ticks, or 11.5×11.5 inches.

### 3.3 Motion commands and encryption

The 0x40 move command carries three 32-bit values: a noise word, X, and Y, each stored byte-swapped at the 32-bit width. Before transmission, the 12-byte payload is encrypted with **XXTEA** (Corrected Block TEA), using a 16-byte key — four 32-bit words. Three operations use three distinct keys: move, line-cut, and curve-cut. The implementation in libcutter (`lib/device_c.cpp`) builds the packet, calls `btea(data, 3, key)`, and writes it through the serial port. The same file contains a deliberate design comment on the protocol's noise field: the developers set `get_rand()` to return the constant 12345, noting that the field adds no security once the keys are public.

## 4. Key material and the mapping that matters

### 4.1 The published keys

The full set was published on the wiki's companion blog in 2014:

| Key set | Words |
|---|---|
| KEY0 | 0x272D6C37, 0x342A6173, 0x3663255B, 0x2B265A4D |
| KEY1 | 0x7D316E22, 0x4A4A7133, 0x5A3C5C5F, 0x78613A61 |
| KEY2 | 0x47302A23, 0x5D31482F, 0x3B257A61, 0x3671382F |
| KEY3 | 0x303F6863, 0x71646D30, 0x4769457B, 0x6D342569 |
| KEY4 | 0x45356650, 0x3A386D69, 0x575A7037, 0x335F357D |
| KEY5 | 0x343A2148, 0x614F3925, 0x753F6953, 0x47463626 |
| KEY6 | 0x3F62626D, 0x7E555F44, 0x7E29425A, 0x52246268 |
| KEY7 | 0x47302A23, 0x342A6173, 0x4769457B, 0x335F357D |

Two sources disagree on the mapping, and the disagreement is functional rather than cosmetic.

### 4.2 The conflict

The wiki's libcutter setup page instructs: use KEY2 for move, KEY4 for line-cut, KEY6 for curve-cut. The same page's example `keys.h` follows that instruction. The blog post publishing the key set shows a sample `keys.h` that maps move to KEY2, line to **KEY3**, curve to **KEY1**. A decimal-to-hex cross-check confirms both files use genuine key-set values; the difference is the assignment.

### 4.3 Resolution and a falsification test

The wiki explains the consequence: KEY3 and KEY5 *appear* to work for line and curve cuts, but they "lift the blade after each cut, leaving gaps in your cuts." A key that decrypts into a valid but blade-lifting instruction set passes a connectivity test and fails a cut-quality test. This makes the wiki's mapping the falsifiable one: cut a square; if the perimeter is continuous, the mapping is KEY2/KEY4/KEY6. The canonical `keys.h` in this repository (`downloads/keys.h`) follows the wiki mapping and records the reasoning in comments.

The second-generation models (Mini, Expression 2, Imagine) use a different, undocumented scheme; the wiki reports that on the Mini the baud rate is ignored and most documented commands fail, and suspects separate keys. Second-generation machines are outside this project's scope.

## 5. libcutter: the native library

The libcutter repository exists in two generations, and the difference matters for anyone starting today. The 2010 original compiled keys into the library through a header file and never saw a CI system. The current repository builds Linux and macOS binaries on every push through GitHub Actions and takes keys at runtime from a text file:

```
MOVE_KEY_0  0x47302A23
...
CURVE_KEY_3 0x52246268
```

The library's structure is small and legible. `include/device.hpp` defines the interface: `move_to`, `cut_to`, `curve_to` (a cubic Bézier), `start`, `stop`, `get_dimensions`. `include/device_c.hpp` implements it for Cricut devices over `serial_port`. The utilities are the practical value: `draw_svg` cuts an SVG file, `draw_gcode` cuts G-code, and `jsdrive` drives the machine in real time from an SDL joystick. `lib/cutter.i` is a SWIG interface for Python bindings.

Firmware compatibility, from the current README: Expression 2.31 verified working; 2.34 and 2.43 expected to work; 2.00 too old. The practical implication: a machine at stock 2.00-era firmware needs an update (Section 8) before any third-party path works.

## 6. The GUI path: Sure Cuts A Lot and the plugin

Sure Cuts A Lot (SCAL) is commercial design-and-cut software from CraftEdge. Releases 4 and 5 support third-party cutter plugins; the LibCutterPlugin.dll (32-bit PE, prebuilt in the DThunder1000 repository) plugs the Cricut into that system through a manifest declaring model `Personal/Expression/Create` and connection types `usb` and `serial`.

The distribution history explains the current friction. ProvoCraft sued CraftEdge in 2011 over SCAL 2's Cricut support; the settlement ended official support and installed a self-disabling update mechanism, which produced the famous hosts-file patches. The modern route, documented by the hobbycutters and familygardentrains articles, is SCAL 5 (or 6) with the community plugin installer. The installer exists in "with keys" and "no keys" variants; the with-keys variant generates `keys.h` during installation. The original file-hosting links expired, and the community re-hosted the installers on MEGA and Google Drive; this project recovered the Windows installer from a Google Drive mirror (sha256 `55fcd1d5…`), and also recovered the plugin DLL directly from source control as a no-installer fallback.

SCAL itself is commercial: the purchase route is craftedge.com, with a trial mode adequate for connection testing. The plugin loads into `Documents/SCALCutPlugins/` alongside the manifest and the keys file.

## 7. Firmware replacement: FreeExpression and Librecut

For machines where the stock firmware is expendable, two open-source replacements exist. **FreeExpression** (markawilliamson, derived from Arlet's freecut) targets the Expression and Cake. **Librecut** targets the CRV001 Personal only. Both flash through the J5 header (Section 2) with an ISP programmer, and both are irreversible: the stock image is read-protected, so nothing can back it up first.

FreeExpression's feature set quantifies what stock firmware withholds: HPGL and G-code input, 9-step speed and pressure control over the full physical range, X/Y origin setting, direct cutter up/down, and an 80-inch cut length (the roller mechanism feeds material continuously; stock firmware clips to the loaded mat). Its command interface is a 115200 8N1 serial console — the non-standard baud rate disappears with the stock firmware.

The physics comparison resolves as follows. Resolution (404 ticks/inch), motor mechanics, drag-knife behaviour, and the absence of closed-loop feedback are identical in both worlds; those are hardware properties. Stock firmware's actual limitations are control-plane: dial-quantized speed/pressure read once at boot, an opaque internal interpolation profile, mat-bound clipping, and the idle serial timeout. For vinyl and cardstock at ordinary speeds, stock firmware driven through libcutter produces cuts indistinguishable from the open firmware. The open path earns its irreversibility only for thin/fussy materials, production-length cuts, or scripted pipelines.

## 8. Recovering the firmware images

The stock firmware ships as update containers, not as standalone flashable files. Three sources were located and harvested; all are archived in-repo with hashes in `downloads/FIRMWARE_MANIFEST.md`.

### 8.1 The v1.0 CD image

Archive.org item `design-studio-v-1.0` (live; a separate, better-known item `cricut-design-studio-v-1.0` is dark — hidden after a metadata flag in December 2023) contains a BIN/CUE CD image of Design Studio v1.0. The image is a raw MODE2/2352 CD sector dump. Converting it required stripping 24 bytes (12 sync + 4 header + 8 subheader) from each 2,352-byte sector, yielding 2,048-byte user data. The result is not an ISO9660 filesystem: the disc payload is a single NSIS installer. Extracting it produces the 2007-era CDS install with `Firmware Releases/cricut_v1_1.enc` (1,223,491 bytes, entropy 7.992 bits/byte) and a `cricut_v2_1.enc` that extracts as zero bytes (extraction artifact or disc placeholder, unresolved).

### 8.2 The font-update item: the complete set

Archive.org item `font-update-v-121009` is live and contains the community's consolidated legacy-era archive. Its `CDS_10404220.exe` (Design Studio 1.0.4.04220, files dated 2010-04-19) extracts to a complete firmware set:

| File | Size | sha256 (16 hex) |
|---|---|---|
| cricut_v1_3.enc | 127,264 | 770c8a02e2320409 |
| cricut_v1_34.enc | 127,792 | 7f43f666013ba2c2 |
| cricut_v1_34b.enc | 127,792 | 4c9a55ced6e441ae |
| cricut_v15_1.enc | 170,424 | 72c0a818ea89a47a |
| cricut_v15_4.enc | 170,752 | 2d1c077594b91be1 |
| cricut_v2_3.enc | 218,256 | 41de1e72a7a5dcbe |
| **cricut_v2_34.enc** | **218,880** | **df45836690ce2b8e** |
| cricut_v2_34b.enc | 218,880 | 31b3b8448da0a0b7 |

The same item holds `FontUpdate_V121009.exe` (the .NET firmware updater), `cricutdrivers.zip` (FTDI drivers), manuals, and a SCAL 2.008 package with an activation crack — which this project recorded for provenance but did not use; the SCAL 5 route does not require the hosts-file technique.

### 8.3 The container format

All `.enc` files are **ASCII-hex text**, not binary. Every file begins with the 16 characters `011268E3C1972335` — except the 1.34/2.34 generation, which begins `01129032E8180BE1`. Two observations constrain interpretation. As an unsigned 64-bit little-endian value, `0x011268E3C1972335` = 77,239,471,033,492,277, far larger than any file, so the header is not a simple length field. The header change coincides exactly with the 1.34/2.34 generation, indicating a container revision at that point. After hex-decoding, the v2.3 payload is 109,128 bytes — 8 × 3 × 4,547 with 4,547 prime — not a multiple of any AVR flash page size, consistent with an encrypted container carrying framing rather than a raw image.

## 9. Where the decryption lives

This section is the report's principal original finding. The question was whether the firmware-decryption code lives in the host software or in the machine's bootloader. Static analysis of the extracted installer answers it: **the host software performs the decryption; the bootloader only receives plaintext blocks.**

### 9.1 The two crypto systems in Design Studio

`Cricut DesignStudio.exe` is a .NET assembly. Parsing it with `dnfile` reveals two unrelated cryptographic systems:

- **`RijndaelSimple`**, an AES/Rijndael wrapper with SHA1 key derivation, used for activation and licensing. Its caller (`Form1.getMACAddress`) passes a machine fingerprint and the strings `SG8WU1J8e4GZp4F6q8nOi1bC5w2XcR3q5y8P` (passphrase), `0123456789` (digits filter), `SHA1`, and `trI1lylmsEPWoGTe` (salt). This system has nothing to do with firmware.
- **`UpdateCricutFirmware`**, whose methods (`read`, `update`, `decodeHexByte`, `hex_to_char`) orchestrate the firmware flow: locate the file under `Firmware Releases\`, decode the ASCII-hex container, and stream the result. The .NET code contains no crypto of its own — the method bodies are small and string-free — because the actual work is **P/Invoked into `Cricut USB.dll`** under obfuscated export names.

### 9.2 Inside Cricut USB.dll

`Cricut USB.dll` is a 32-bit native DLL whose exports pair FTDI wrappers (`FT_Open`, `FT_SetDivisor`, `FT_Write`…) with obfuscated crypto functions. Disassembly with pefile and capstone finds the XXTEA delta `0x9E3779B9` and two complete routines:

- **Encrypt at RVA 0x1610**: the round function with `sub eax, 0x61c88647` (equivalent to adding the delta), the `(sum>>2)&3` key-index selection, and the `(v<<4)^((v>>3)+((p<<4)^(p>>3)))` mixing chain that identifies XXTEA unambiguously.
- **Decrypt at RVA 0x16f0**: the mirror routine, with the round count computed as `(0x34/n) * 0x9E3779B9` — the standard `6 + 52/n` rounds.

Adjacent, at RVA 0x17e7–0x18c6, the DLL hardcodes **all eight protocol keys from Section 4.1 as immediate constants** — `0x47302A23` (KEY2) at 0x17fc, `0x272D6C37` (KEY0) at 0x1803, and so on through KEY7. The DLL therefore ships with the complete key material for both the cutting protocol and, by strong implication, the update container: whatever key the container uses, it is either one of these eight or derived from material in this module. The community's separate distribution of `keys.h` was necessary for the open-source library, not for Cricut's own software.

### 9.3 What this means for decryption

The practical consequence is that firmware decryption requires no key discovery — the candidate keys are known and the algorithm implementation is in-hand. The remaining unknowns are container framing: the header's semantics (IV, checksum, or identifier), the block segmentation applied before XXTEA, and the key selection rule per block or per file. The detection oracle is strong: a correct decryption of an AVR firmware image yields an interrupt vector table in the first bytes (`jmp` opcodes, `0x94 0x0C` little-endian word patterns at even word offsets). A framing search across the eight keys and a small set of framings is a bounded computation.

The dynamic route exists as a fallback: running CDS under wine with instrumentation on the DLL exports would capture the exact key and framing from a real update session without any search. The static route is attempted first because it needs no machine present.

## 10. Status and next steps

Completed: artifact recovery (installer, plugin, keys, full firmware set, wiki archive), protocol documentation, key-mapping falsification test defined, two control paths documented, flashing playbook written with hardware photography, crypto location identified with disassembly evidence.

Open, in priority order:

1. **Container framing search.** Implement XXTEA in Python; search framings × 8 keys × 8 firmware files against the vector-table oracle. This is the highest-value next step: success converts the `.enc` set into flashable, analyzable ATmega1281 images.
2. **Stock firmware update path.** Install CDS under wine, verify the 198,347 bps link through D2XX, and update the Expression to v2.34 using the recovered images (with the known a/b two-pass sequence). This unblocks the SCAL 5/plugin GUI path on a stock machine.
3. **SCAL 5 trial under wine.** The commercial host's trial mode plus the recovered plugin; the GUI-path baseline.
4. **Native libcutter validation.** CI-built binaries plus the canonical keys file; `draw_svg` as the scripted end-to-end test.

The report will be revised as these steps complete; each revision will note its diary step.

## Sources

- Cricut Hacking Wiki (recovered mirror): jimlund.org/build-to-spec — Main Page, Cricut Commands, Cricut Communication Specs, First/Second Generation Hardware, Cricut Carts, Setting Up Libcutter, To Explore, Explored (archived in `ttmp/.../sources/cricutwiki/`)
- vangdfang/libcutter (current, CI-built) and DThunder1000/libcutter (SCAL plugin generation), both GitHub
- markawilliamson/FreeExpression, arlet/freecut, Gilbertindustries/Librecut, all GitHub
- hobbycutters.com SCAL4/5 add-on directions; familygardentrains.com "Using Sure-Cuts-A-Lot With Legacy Cricuts"; jimlund.org blog p=316 (key publication)
- forum.surecutsalot.com thread 43418 (mirror hub for installers)
- Archive.org items: `design-studio-v-1.0` (CD image), `font-update-v-121009` (firmware set, updaters, drivers)
- christianmeurer/cricut-re-toolkit (modern protocol documentation)
