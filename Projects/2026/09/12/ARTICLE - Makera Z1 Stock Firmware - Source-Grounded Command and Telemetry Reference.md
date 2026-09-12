---
title: Makera Z1 Stock Firmware - Source-Grounded Command and Telemetry Reference
aliases:
  - Makera Z1 stock command reference
  - CarveraFirmware command extraction
  - MZ1-011 firmware reference
  - Z1 G-code shell and realtime commands
tags:
  - article
  - cnc
  - firmware
  - protocol
  - reverse-engineering
status: active
type: article
created: 2026-09-12
repo: /home/manuel/workspaces/2026-08-11/cnc-control-dropcut/dropcut-studio
source_firmware_commit: 1683b6fb5c7ec1d341c476c6fdb2a22f7a26220e
installed_firmware: 1.0.15.0.1.11
reference_status: 145-of-145-extracted-concrete-gm-tokens-represented
---

# Makera Z1 Stock Firmware — Source-Grounded Command and Telemetry Reference

The Makera Z1 command surface is not one language. It combines framed text, realtime control bytes, GRBL-compatible `$` commands, lowercase shell commands, job-player verbs, conventional G-code, inherited Smoothieware commands, model-specific automation, and configuration-defined output bindings. A command list built from observed examples alone misses hidden branches. A list built from source tokens alone overstates availability. A useful reference must connect syntax to dispatch, parameters, state transitions, responses, configuration, and evidence strength.

This article explains the command model found in MakeraInc/CarveraFirmware commit `1683b6fb5c7ec1d341c476c6fdb2a22f7a26220e`, how the MZ1-011 reference was extracted and audited, and which commands are most important when building a safe host controller. The installed Z1 reports firmware `1.0.15.0.1.11`, but no tag or build manifest proves that the checked source is byte-identical. Source behavior is therefore version-indicative unless supported by hardware evidence.

> [!summary]
> - Ordinary commands and realtime controls use different framed packet types. Realtime bytes such as hold, reset, jog stop, and jog keepalive are not interchangeable with G-code commands.
> - The reference combines automated extraction with manual semantic review. Its lexical audit represents all 145 concrete extracted G/M tokens, but representation does not imply that every command is compiled, configured, model-applicable, or safe to invoke.
> - M5, M957, M112, M119, M211, M400, M503, aggregate `?`, and the player commands are especially important because they expose the difference between dispatch, controller state, physical observation, and recovery.
> - Configuration-defined Switch and Temperature commands must remain conditional. Command numbers alone do not establish installed pins, polarity, output type, units, or attached hardware.

## 1. Scope and evidence labels

A firmware reference should answer five different questions:

1. Does a handler exist in the reviewed source?
2. Is that handler compiled for the relevant build?
3. Is it configured on the installed machine?
4. Does it apply to the Z1 model and attached hardware?
5. Has its external behavior been observed on the installed firmware?

MZ1-011 records these dimensions with compact confidence labels:

| Label | Meaning |
|---|---|
| `SRC` | The behavior is directly implemented in the pinned source at a cited location. |
| `HW` | The behavior was observed on the Z1 running `1.0.15.0.1.11`. |
| `CFG` | A handler exists, but registration, pin, polarity, subcode, or semantics depend on configuration. |
| `MODEL` | The branch applies only to a particular machine model or enabled module. |
| `UNK` | The source has a meaning, but installed applicability or physical semantics remain unverified. |

These labels are not a ranking from weak to strong. They describe different provenance. A command can be both source-grounded and configuration-dependent. A live observation can establish one output without identifying the exact source revision that produced it.

The reference is semantic documentation, not permission to send commands. Motion, spindle, homing, probing, tool changing, output control, configuration changes, reset, firmware update, and file mutation require separate admission in the host controller.

## 2. The three outer command languages

Before classifying individual verbs, the host must know how bytes reach the parser.

### 2.1 Ordinary framed text

On the reviewed Makera TCP dialect, ordinary text is carried in packet type `0xA2`:

```text
86 68 | length:u16-be | type:u8 | payload | crc:u16 | 55 aa
```

`GcodeDispatch` receives each textual line. Uppercase `G`, `M`, `T`, and `S` forms become G-code objects. Lowercase verbs and `$` forms are offered to shell and player modules. Comments begin at `;` or `(`. A single source line can be split into several G/M/S/T blocks, and bare axis or feed words can inherit a current modal motion mode.

That last property makes generic text transmission dangerous. A string does not need to begin with `G0` or `G1` to cause movement if modal state already selects motion.

```text
strip line number and comments
inspect the first token
if uppercase G/M/T/S:
    split compound blocks
    publish each G-code event
else if lowercase or '$':
    offer the line to shell/player dispatch
else:
    ignore or report unsupported input
```

### 2.2 Realtime framed bytes

Realtime controls use packet type `0xA1`. They bypass ordinary line parsing and affect controller state through dedicated dispatch paths.

| Byte | Name | Source-level effect | Safety boundary |
|---|---|---|---|
| `?` (`0x3f`) | Status query | Emit aggregate bracketed status | Read-only |
| `!` (`0x21`) | Feed hold | Request motion hold | Does not establish spindle off or terminate a job |
| `~` (`0x7e`) | Cycle start | Release realtime hold | State-enabling |
| `0x18` | Soft reset / halt path | Reset controller state and invoke halt processing | Software stop, not physical E-stop |
| `0x19` | Jog stop | Stop continuous jog handshake | Stop-only |
| `0x1a` | Jog keepalive | Keep an active continuous jog alive | Enabling; only the owning jog session may send it |

The distinction between `0x19` and `0x1a` is operationally important. One ends continuous motion; the other prolongs it. A public API that accepts arbitrary realtime bytes cannot classify them all as diagnostics.

### 2.3 Textual response streams

Firmware replies are lines, reports, alarms, and operation-specific messages carried back through the framed channel. `ok` is not a universal completion proof. Some handlers print it immediately after dispatch. Some source paths refuse through human-readable text. Some return silently under unmet preconditions.

Host correlation therefore needs a controlled sentinel or an operation-specific terminal protocol. Even with correct correlation, physical completion requires later telemetry when the operation has a physical postcondition.

## 3. How the command reference was built

The extraction workflow was designed to avoid both incompleteness and false authority.

### 3.1 Pin the source tree

The first requirement was a stable source identity. The reference pins:

```text
MakeraInc/CarveraFirmware
commit 1683b6fb5c7ec1d341c476c6fdb2a22f7a26220e
```

Line citations, candidate catalogs, and semantic claims refer to that tree. Installed firmware identity remains separate.

### 3.2 Enumerate candidates mechanically

The script `01-extract-command-catalog.py` scans the full source for dispatch evidence, including:

- equality tests against `gcode->g` and `gcode->m`;
- `switch` cases over G-code numbers;
- shell dispatch tables;
- player command registrations;
- realtime control constants and branches;
- parameter letters and nearby effect clues.

The extraction produced a reproducible candidate catalog rather than a curated list. Earlier intermediate counts included 260 candidate command entries and 473 line-cited parameter/effect clues. The finalized artifact contains 333 candidate references and 145 unique concrete G/M tokens, plus shell, player, and realtime candidates. Duplicate and incidental references are retained because the artifact is evidence for later review, not the final interpretation.

```mermaid
flowchart LR
    SRC[Pinned firmware source] --> SCAN[Static candidate scanner]
    SCAN --> CAT[Candidate JSON catalog]
    CAT --> REVIEW[Manual handler and branch review]
    REVIEW --> REF[Semantic reference]
    REF --> AUDIT[Lexical coverage audit]
    AUDIT -->|missing token| REVIEW
    AUDIT -->|145 of 145 represented| DONE[Completed reference]
    style SRC fill:#e5e5e5,stroke:#333
    style REF fill:#d9f2ff,stroke:#006d8f
    style DONE fill:#dff5df,stroke:#287a28
```

### 3.3 Read dispatch and implementation together

A token match only says that a number appears near code. Semantic review follows the path from registration to handler and then through side effects. The review asks:

- What exact letters and subcodes are parsed?
- What defaults and units are used?
- Does the command wait for the conveyor?
- Does it return before a scripted action finishes?
- Does it emit `ok`, a report, silence, or an alarm?
- Does configuration choose the command number?
- Is the branch disabled by the preprocessor?
- Does the branch belong to SCARA, laser, ATC, heater, or another optional module?
- Which state variables change, and which telemetry later exposes them?

This step corrected several tempting but false conclusions. M0 appears in source but its Robot handler is commented out. M9999 appears in a `#if 0` debug block and is not compiled. M887 disables homing checks, while M888 enables them—the opposite direction from older local prose. A bare source token could not establish any of these facts.

### 3.4 Audit lexical coverage separately from semantics

The script `02-audit-reference-coverage.py` compares the extracted concrete G/M tokens with the prose reference. The final result is:

```text
145 represented
0 missing
```

This is a completeness backstop for the token inventory. It does not prove semantic correctness or installed availability. Each entry still needs source citations, parameter review, model/configuration labels, response semantics, and safety caveats.

## 4. GRBL-compatible `$` commands

The `$` surface is small enough to look familiar and different enough to require exact documentation.

| Command | Meaning | Notable behavior |
|---|---|---|
| `$G` | Report modal state | Calls `get state`, reports, then prints `ok`. |
| `$I` | Compatibility state report | Uses the state path but does not add the same final `ok` in its handler. |
| `$X` | Clear a resettable halt | Acts only when halted; prints caution and `ok` in that case. |
| `$#` | Report WCS/GRBL parameters | Read-only report followed by `ok`. |
| `$H` | Home | Clears an existing halt and dispatches literal `G28.2` in GRBL mode or `G28` otherwise. It prints `ok` immediately. |
| `$S...` | Switch command | Syntax and output are configuration-dependent. |
| `$J <axes> [F<scale>]` | Instant relative jog | `F` is a fraction of configured axis maximum, not mm/min; omitted F means 1.0. |

Two details have direct API consequences.

First, `$H X` is not proven single-axis homing. The shell ignores trailing arguments and creates a new literal home G-code. Direct `G28` axis handling is a different path. A host must not preserve familiar GRBL syntax while assuming familiar semantics.

Second, `$J` feed values are dimensionless scaling factors in this implementation. A UI labeled “mm/min” would send the wrong physical request.

## 5. Lowercase shell commands

The firmware registers a fixed shell dispatch table and matches names with a case-insensitive prefix comparison. Hosts should send exact full names. Depending on an abbreviation makes behavior sensitive to table order and later additions.

### 5.1 Observation and identity

The safest shell commands are still semantically varied:

- `version` reports firmware/build identity.
- `model` reports model and function setting.
- `diagnose` emits subsystem vectors, including E-stop and endstop/cover-related values whose arity and polarity are version-specific.
- `get state`, `get wcs`, and `get pos` expose structured controller data.
- `get fk` and `get ik` perform kinematic conversions and accept source-defined coordinate options.
- `mem` reports memory diagnostics.
- `time` can be a read or a write depending on arguments.
- `help` prints the shell's built-in list, which is not exhaustive of all event handlers.

A read allowlist must validate the complete grammar. Recognizing `time` as a familiar command is insufficient because `time <value>` mutates the controller clock. The same issue applies to network commands and configuration multiplexers.

### 5.2 Filesystem commands

| Command | Operation | Important semantics |
|---|---|---|
| `ls [options] [path]` | List directory | Path defaults to working directory; output forms are firmware-specific. |
| `cd <path>` / `pwd` | Change/report shell directory | `cd` mutates session state. |
| `cat <file>` | Print file | Installed firmware has returned `File not found` for apparently present files. |
| `echo <text>` | Echo text | Useful as a transaction sentinel; untrusted line separators must be rejected. |
| `rm`, `mv`, `mkdir` | Mutate filesystem | Destructive or state-changing. |
| `md5sum <path>` | Compute digest | Some installed behavior has returned a fixed placeholder; verify before treating it as integrity proof. |
| `M28 <filename>` | Enter stream upload | Firmware prepends `/sd/` and opens/truncates the destination. |
| `upload`, `download` | Enter binary transfer protocol | Not plain shell streaming. |
| `ftype` | Report accepted upload type | Pinned source says `lz`; live Z1 reported `nc`, demonstrating source/live divergence. |

Paths are part of a command grammar. They must be absolute, validated, and escaped exactly once. A filename containing a newline is not merely an unusual filename when embedded in a textual control channel; it can introduce another command.

### 5.3 Administrative commands

`config-get`, `config-set`, bulk config load/restore/default operations, `load`, `save`, `net`, `ap`, `wlan`, `sleep`, `power`, `dfu`, `reset`, thermal setup, and factory diagnostics have effects beyond ordinary job control. Several can disconnect the host, alter calibration, expose credentials, actuate outputs, or enter firmware-update state. They belong behind dedicated typed APIs, not a generic shell textbox.

`M1000` deserves special mention. It takes the remainder of an uppercase G-code line, lowercases it, invokes the shell, and then prints `ok`. It is a broad administrative escape and should not be exposed as generic motion control.

## 6. Player and job lifecycle

The job player has its own state machine. Its commands are not synonyms for realtime controls.

| Command | Effect | Completion caveat |
|---|---|---|
| `play <path> [-v]` | Open an SD file and begin queued execution | Can return silently when the firmware's internal homed flag is false. |
| `progress` | Report played bytes and file size | Absence of playback fields elsewhere does not prove completion. |
| `suspend` | Suspend active file execution | May drain the conveyor and perform configured retract behavior. |
| `resume` | Resume a suspended player | Distinct from realtime cycle start `~`. |
| `abort` | Terminate active or paused playback and clean up | Do not infer spindle stop solely from acknowledgement. |
| `goto <line>` | Set a resume/start line | File-line semantics, not byte position. |
| `buffer` | Report or manage buffering | Source-defined behavior. |

Compatibility M-codes include M21, M23, M24, M25, M26, M27, M32, M600, and M601. Their implementation routes into the same player machinery, but details follow stock firmware rather than a generic printer profile.

A representative source path is:

```text
play(path):
  refuse if playing, suspended, or waiting
  if internal homed flag is false: return silently
  parse stock-supported options
  open the file
  initialize counters
  feed lines into the conveyor
```

Silence under the unhomed condition is why a transport-complete transaction cannot be promoted to accepted. The host must observe player state or a source-defined success marker.

## 7. Motion and coordinate commands

The core motion surface includes G0/G1 linear movement, G2/G3 arcs, G4 dwell, coordinate and offset commands, homing, probing, modal units, and distance modes.

### Modal commands that alter later interpretation

- G17/G18/G19 select the active plane.
- G20/G21 choose inch or millimeter units.
- G53 applies machine coordinates to the following motion block.
- G54 through G59.3 select work coordinate systems.
- G90/G91 select absolute or incremental distance mode.
- G92 variants introduce temporary coordinate offsets.
- G93/G94 select inverse-time or feed-per-minute behavior where enabled.

A command generator must either establish these modes or query and preserve them. A coordinate tuple has no complete physical meaning without unit, distance, WCS, transform, and offset state.

### Calibration and planner commands

Commands such as M92, M203, M203.1, M204, M205, M206, M306, M665, M666, and M670 alter steps, rates, acceleration, planner behavior, home offsets, kinematic parameters, or probe configuration. They are not ordinary “settings” in a low-risk sense. Incorrect values can produce unexpected travel or invalidate physical limits.

M211 controls soft endstops. With `S0` it disables them. With no `S`, it reports status and envelopes. A generic API must distinguish query and mutation by full parameter grammar.

M220 changes feed override from 10% through 1000% after clamping. M223 changes spindle override from 50% through 200%. Both can alter an already-running physical process without introducing a new motion command, so classifying only G0/G1/M3 as hazardous is insufficient.

## 8. Homing, limits, and probing

G28 and G28.2 enter configured homing paths. G29, G30, G31, G32, and G38.2/G38.3 invoke probe or leveling behavior whose meaning depends on the active strategy and physical probe setup. M557 defines three-point probe locations; M565 changes probe offset; M374/M375 save and load grid data.

Physical and software limits report different failures:

```text
Limit switch <direction><axis> was hit - reset or M999 required
Soft Endstop <axis> was exceeded - reset or $X or M999 required
```

They must not be collapsed into one Boolean. The first is a physical switch event while moving. The second is a software-envelope violation. On the observed machine, halt reason 10 corresponded to a soft limit, but that does not map every halt code or prove every hard-limit connection.

M119 is the source-grounded switch-observation command. It reports configured homing switches and physical limit pins; the probe module can append probe state. It is a better starting point for supervised topology mapping than assigning meanings to undocumented positions in a generic diagnostic vector.

Homing completion also requires care. `$H` prints `ok` immediately after publishing the home event. That acknowledgement says dispatch occurred, not that every axis reached its reference.

## 9. Spindle commands and diagnostics

### M3

In CNC mode, `M3 S<rpm>` checks that the controller is not halted and that the active tool is valid, waits for conveyor idle, sets the target, and turns the spindle on. Configuration can couple vacuum or external-output modes to spindle state. In laser mode, another subsystem handles M3.

### M5

M5 waits for conveyor idle, then calls spindle `turn_off()` when the local spindle state is on. It also disables mode-linked vacuum or external outputs. It is an ordinary queued G-code command, not an out-of-band stop.

The target RPM is retained after M5 by design. Stop confirmation must use measured RPM and state or PWM, not target zero.

### M957

M957 reports:

- local spindle state;
- current measured RPM;
- target RPM;
- PWM duty.

This makes it one of the most valuable diagnostic commands in the firmware. On the installed machine, stopped observations showed state off, current zero, and PWM 0.000. Running at a 6000 RPM target showed state on, current near 6000, and PWM around 0.27–0.30.

### M958 and the PWM loop

M958 changes runtime spindle gains. In the pinned Z1 PWM path, P contributes an incremental duty correction, loaded I is unused, and a D branch belongs to a Carvera Air-specific path.

The control loop is approximately:

```text
every 10 ms:
  update and filter measured RPM
  force measured RPM to zero after 1 s without pulses
  if spindle is on at the control interval:
      error = target * override - measured
      pwm = clamp(pwm + P * error, 0, max_pwm)
  else:
      pwm = 0
  write PWM, applying configured inversion
```

This incremental-P form can oscillate at low speed. Supervised 3000 RPM behavior showed a limit-cycle-like region, while 6000 RPM was stable enough for stop acceptance. The loop shape does not explain an M5 that remains in `Run`; that requires evidence around whether `turn_off()` was reached and what controller state changed.

### M112 and realtime Ctrl-X

M112 invokes the firmware halt path, disables through `ON_HALT`, clears queued work, and ignores later G-code until recovery. Realtime Ctrl-X also reaches reset/halt processing through its realtime route. Both are software mechanisms. Neither replaces the physical E-stop.

## 10. Aggregate status

Realtime `?` produces the bracketed aggregate report. The controller state uses this precedence:

```text
Sleep -> Suspend/Pause -> Wait -> Tool -> Alarm -> Home -> Hold
      -> Idle when conveyor idle and spindle flag false
      -> Run otherwise
```

The precedence explains an important spindle observation: once the source-level spindle flag is false and the conveyor is idle, state can become Idle while the rotor still has measured coast-down RPM. Idle is controller state, not an assertion that every mechanism has reached zero velocity.

Principal fields include:

| Field | Meaning | Interpretation limit |
|---|---|---|
| `MPos` | Machine coordinates | During Run may use current actuator position; otherwise a milestone. |
| `WPos` | Transformed work coordinates | Depends on WCS, offsets, and compensation. |
| `F` | Current/requested feed and override | Current is zero outside running state. |
| `S` | Measured RPM, retained target, override, vendor extensions | Retained target is not spindle-on evidence. |
| `T` | Active tool and tool-length data | Does not physically verify installed tool. |
| `L` | Laser/output data | Model and version dependent. |
| `C` | Vendor condition vector | Cover-related mappings require provenance. |
| `E` | Vendor diagnostic/network vector | Do not assume it is the same as `diagnose` solely because of its letter. |
| `H` | Halt reason | Preserve unknown numeric codes. |
| `P` | Playback state | Absence does not prove job completion. |
| `OTA` | Update state | Administrative telemetry. |

A parser should retain unknown appended fields, expected arity, and raw text. Mapping absent positions to zero destroys the difference between “reported zero” and “not reported.”

## 11. Configuration-defined outputs

The firmware's Switch module binds command numbers to output instances through configuration. The checked defaults contain examples such as:

| Commands | Indicative default use |
|---|---|
| M7 / M9 | Air on/off |
| M801 / M802 | Vacuum in one configuration; power fan in another board branch |
| M811 / M812 | Spindle fan |
| M821 / M822 | Work light |
| M831 / M832 | Tool-sensor power |
| M841 / M842 | Probe charger |
| M851 / M852 | Extension output |
| M861 / M862 | Beeper in one configuration |

These mappings are `CFG`, not universal protocol constants. Installed configuration determines whether a binding exists and selects pin, polarity, default value, output type, and subcode.

Optional `S` values also depend on output implementation:

- sigma-delta uses 0–255;
- hardware and software PWM clamp 0–100;
- digital-pwm uses configured minimum and maximum;
- a plain digital output can treat S only as retained bookkeeping while writing on/off.

A typed host profile must preserve those units. Converting every accessory power field into a percentage would be wrong for sigma-delta outputs.

## 12. Tool changer, probing automation, and factory commands

The ATC range includes M6, M480 variants, M490 through M499, and associated detector, calibration, EEPROM, and beeper operations. These commands often create internal scripts rather than execute one direct hardware action.

M6 requires T, waits for conveyor idle, attempts spindle shutdown, checks tool range and mode, then runs drop, pick, calibration, or manual-change behavior. Missing or invalid tool data can halt the machine.

M480 corner and pocket variants and M495 probe workflows parse geometry, verify homing, push modal state, optionally select a probe tool, and append a sequence of clearance, probing, rotation, or leveling scripts. Their immediate response is not the terminal result of every scripted move.

Several notable commands demonstrate why source reading matters:

- M493.2 persists the active tool; special T9999 changes wired-probe detector output.
- M496 contains a source defect in which B writes the A-position field.
- M498.2 erases EEPROM data.
- M887 disables homed checks and is extremely unsafe.
- M888 restores homed checks.
- M490 has materially different behavior with and without ATC support.

A generic “send M-code” UI cannot present these safely. Parameters and model branches must be explicit.

## 13. Wi-Fi, radio, and maintenance commands

The vendor command surface includes wireless-probe serial operations, 2.4 GHz radio tests, Wi-Fi reset and diagnostics, credential queries, aggregate status, and placeholders.

M482 and M483 subcommands can print station and access-point passwords. Their inclusion in firmware does not make them suitable for ordinary diagnostic logs. M481.6 uses a hard-coded developer IP calculation, M481.7 prints a placeholder string, and M481.5 has no effect in the pinned branch. These are examples where enumeration without semantic review would produce a misleading polished API.

M999 clears a resettable halt and is therefore state-enabling recovery. `$X` has related but not identical dispatch behavior. Neither is a read-only acknowledgement command.

M500 waits idle and asks subscribed modules to serialize settings into an override file. M501 loads an override, M502 deletes it, M503 reports live settings, and M504 saves to an optional suffix. Because modules subscribe independently, these commands have compositional effects; there is no single small structure containing the whole configuration.

## 14. Temperature commands are inherited and conditional

The source includes Smoothieware temperature-control and PID autotune machinery. Its presence does not prove that the Z1 has an installed heater or that default M104/M105/M109 registrations are active.

The configured get, set, and set-and-wait command numbers default to familiar values but can be changed. M143 modifies maximum temperature, M301 changes PID/output parameters, M303 starts asynchronous autotune, M304 aborts it, and M305 changes sensor-driver options. These are heating and calibration hazards when active.

The correct classification is `CFG` plus model/attachment uncertainty. A controller should discover or configure a concrete capability profile rather than infer it from compiled source.

## 15. Commands worth remembering

The complete reference is broad, but a smaller set clarifies the firmware's operating model:

### `?`

Use it for fresh aggregate status. Preserve field presence, arity, unknown extensions, and timestamps. Do not derive homing, tool identity, or physical stop from Idle alone.

### `M957`

Use it for spindle-local diagnostics. Its state, measured RPM, target, and PWM help distinguish retained setpoint from active output and complement aggregate status.

### `M5`

Use it as the normal source-grounded spindle stop. It is queued and waits for conveyor idle. Send it once and observe the result; do not assume `ok` means zero physical RPM.

### `M112`

Keep it available as a software emergency halt. Do not put it behind motion preflight. Continue to treat the physical E-stop as final authority.

### `M119`

Use it when mapping switches and probe state under supervision. It is more direct than inventing meanings for undocumented positions in a diagnostic vector.

### `M211`

Query it to understand soft-endstop state and ranges. Treat `S0` as a high-risk operation because it disables software travel protection.

### `M400`

Use it when an operation requires the conveyor to become idle. It establishes queue idleness, not spindle zero, homing, or job success.

### `M503`

Use it to inspect the compositional live configuration. Expect multiple modules to contribute lines.

### `$H`, `$X`, and `$J`

Document their stock semantics rather than assuming generic GRBL behavior: `$H` ignores axis suffixes in its shell path, `$X` is state-enabling halt recovery, and `$J` uses a maximum-speed fraction.

### `play`, `progress`, `suspend`, `resume`, and `abort`

Treat these as a player state machine. Realtime hold/cycle start and player suspend/resume are distinct mechanisms.

## 16. Response semantics

The response rules can be stated precisely:

- `ok` proves that a particular handler printed `ok`; its timing depends on that handler.
- A controlled echo sentinel proves host-side transaction correlation, not firmware acceptance.
- A known textual refusal should set acceptance to refused even if transport succeeded.
- Unknown text remains unknown.
- `$H` can print `ok` before physical homing completes.
- `play` can return silently when unhomed.
- M5 can finish its command exchange before measured RPM reaches zero.
- Idle does not prove homing, clearance, installed tool identity, or job completion.

A safe host uses operation-specific postconditions:

```text
home:
  dispatch + later homing evidence

spindle stop:
  one M5 + fresh state/current-RPM dwell

file download:
  transfer completion + byte count + digest agreement

job start:
  dispatch + observed player transition
```

There is no single generic definition of “done” that covers all commands.

## 17. How to extend the reference

Future updates should follow the same evidence sequence:

1. Pin the exact source revision before changing citations.
2. Rerun candidate extraction across the full source tree.
3. Compare the generated catalog with the previous artifact.
4. Review registration, parameters, units, defaults, branches, and side effects for every new candidate.
5. Mark configuration and model dependencies explicitly.
6. Record response timing and terminal semantics.
7. Run the lexical coverage audit.
8. Keep hardware observations labeled with machine firmware, binary identity where relevant, timestamps, and physical supervision conditions.
9. Never use a fake transport as proof of firmware behavior; use it only to verify host invariants.

A useful new entry includes more than a command number. It should answer:

```text
syntax
registration path
handler path
parameter grammar and units
defaults and clamping
preconditions
state changes
response text and timing
later observable evidence
configuration/model applicability
risk and admission requirements
```

## 18. Limits of the current reference

The 145/145 result means every extracted concrete G/M token is represented in the long-form reference. It does not mean:

- every token is compiled into the installed firmware;
- every handler is configured on the Z1;
- every inherited module has corresponding hardware;
- every parameter has been exercised physically;
- every diagnostic vector position is mapped;
- every command is appropriate to expose;
- the installed binary was built from the pinned commit.

M0, disabled M9999, model-only SCARA calibration, configurable temperature commands, and variable Switch bindings demonstrate these limits directly.

## 19. Primary artifacts and source locations

The complete source-grounded reference is:

```text
/home/manuel/workspaces/2026-08-11/cnc-control-dropcut/dropcut-studio/
ttmp/2026/09/12/MZ1-011--makera-z1-stock-firmware-source-grounded-command-reference/
reference/01-stock-firmware-command-and-telemetry-reference.md
```

The extraction diary is:

```text
ttmp/2026/09/12/MZ1-011--makera-z1-stock-firmware-source-grounded-command-reference/
reference/02-extraction-diary.md
```

Key implementation areas in the pinned firmware include:

- `src/modules/communication/GcodeDispatch.cpp`
- `src/modules/utils/simpleshell/SimpleShell.cpp`
- `src/modules/utils/player/Player.cpp`
- `src/modules/robot/Robot.cpp`
- `src/modules/robot/Endstops.cpp`
- `src/modules/tools/spindle/SpindleControl.cpp`
- `src/modules/tools/spindle/PWMSpindleControl.cpp`
- `src/modules/tools/atc/ATCHandler.cpp`
- `src/modules/tools/switch/Switch.cpp`
- `src/modules/tools/temperaturecontrol/TemperatureControl.cpp`
- `src/modules/utils/wifi/WifiProvider.cpp`

Exact paths vary slightly by module layout in the checkout; the MZ1-011 reference carries line-level citations against the pinned tree.

## 20. Related notes

- [[PROJ - Makera Z1 Control - Reverse-Specifying a CNC Wire Protocol]]
- [[PROJ - Makera Z1 Control - Crossing into Motion]]
- [[PROJ - Makera Z1 Control - What the Machine Does Not Say]]
- [[PROJ - Makera Z1 Control - Typed Interfaces and Explicit Uncertainty]]
- [[PROJ - Makera Z1 Control - Protocol Hardening and Spindle Stop Safety]]

The durable rule for firmware research is: **enumerate mechanically, interpret from handlers and state transitions, label provenance, and require operation-specific evidence before converting a response into a physical claim.**
