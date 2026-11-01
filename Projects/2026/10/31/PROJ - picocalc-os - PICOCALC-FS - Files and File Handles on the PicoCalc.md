---
title: "picocalc-os, PICOCALC-FS: files and file handles on the PicoCalc"
aliases:
  - PICOCALC-FS
  - picocalc-os files
  - picocalc-os file handles
tags:
  - project
  - picocalc
  - esp32p4
  - filesystem
  - capabilities
status: active
type: project
created: 2026-10-31
updated: 2026-10-31
repo: /home/manuel/code/wesen/2026-10-20--ds-js-os
---

# picocalc-os, PICOCALC-FS: files and file handles on the PicoCalc

This note reports the first of five tickets that turn picocalc-os into a pocket computer with an editor,
a file browser, a calculator, an agenda and system tools; see
[[PROJ - picocalc-os - Project Overview - A JavaScript OS on Two Devices, With an Agent]] for the project as a
whole. Until this ticket, a program could keep only one small JSON record across a reboot. PICOCALC-FS adds a
filesystem, a way for one program to grant another access to exactly one file, and file operations that obey
the kernel's rule that a crashing program leaves no half-done effects. The device work also found and fixed a
fault that had made the PicoCalc's keyboard die after some resets.

> [!summary]
> - **Files are handles.** A world gets a directory handle from a manifest claim (`fs:/notes`), narrows it to
>   a subdirectory or one file with fewer rights, and passes that in a message. The receiver can use only that
>   file, cannot pass it on, and loses it when the giver revokes it.
> - **Every operation is a promise carried out after the segment ends.** A segment that throws writes nothing;
>   a restarted world never receives a result meant for its previous life. On the device the I/O runs on a
>   worker task, so a flash erase never stalls the screen or the keyboard.
> - **One POSIX layer, two roots.** A directory on Linux and an 11.8 MB FAT partition on the ESP32-P4's flash,
>   mounted in 3 ms. The SD card is deferred: its pins through the adapter are unknown.
> - **Resetting the P4 could wedge the keyboard controller** until the PicoCalc was power-cycled (1 reset in 5).
>   Holding the keyboard bus between transactions before a reset fixed it (10 of 10 clean).

## Why this ticket exists

The four tickets after this one need storage that the per-world store cannot provide: documents of tens of
kilobytes, directories, names the user chooses, and a way to hand a document from one program to another. The
store stays what it was, quota-bound private state for settings and sessions.

## Where files live

The PicoCalc's SD slot is wired to the Pico socket's SPI0 pins, but this PicoCalc carries an ESP32-P4 on a
same-position adapter, and only the keyboard and LCD pins were ever verified through it. The P4's 32 MB flash,
of which ESP-IDF can address 16 MB, had 11.8 MB unused after the application and the stores. A FAT partition
with ESP-IDF's wear-levelling layer went there, mounted at `/files`. The file layer takes only a root path, so
the SD card can later be mounted as a second root without changing anything above it.

```text
nvs         0x9000    24 KB   credentials, Wi-Fi
factory     0x10000    4 MB   application (2.2 MB used)
agentstore  0x410000 128 KB   per-world records
files       0x430000 11.8 MB  FAT + wear levelling, /files      (new)
```

## Implementation details

### The model: handles that carry a path

picocalc-os already had capability handles for hardware: an integer the kernel checks on every use, with read,
write and grant rights, narrowing to fewer rights, passing in messages, and revocation by the world that
narrowed it. A file handle is the same structure with a path relative to the root and a flag that says it names
one file:

```js
const root = hw.fs("fs:/");                  // only with the manifest claim "fs:/"
const one = root.at("notes/todo.txt", "rw"); // a child handle; this world is its minter
send("editor", "open", { file: one });       // the editor holds it now
await one.read();                             // in the editor: the file, and nothing else
one.revoke();                                 // in the browser: every later use fails
```

The kernel's existing grant rule decides who may pass a handle on: a handle with the grant right, or a handle
the sender narrowed itself. So the browser can give the editor a read-write handle that the editor cannot hand
to a third world, which the tests check.

Paths are checked before any I/O. They are relative, at most 95 bytes, without empty, `.` or `..` segments and
without names starting with a dot, which the layer reserves for its temporary files. Joining a handle's path
and an operation's path therefore cannot leave the handle's directory.

### The operations: asynchronous, deferred, on a worker

Every file operation, reads included, is a kernel promise:

```text
JS:   await d.write("todo.txt", text)
vm:   check rights and path -> create a promise -> defer(run_fs, job)
      (the segment ends cleanly; had it thrown, the job would be discarded with it)
host: fs_execute(job) now; settle after 2 ms + 1 us/byte of virtual time
P4:   queue to the "fs" worker task -> fs_execute(job) -> back to the kernel task -> settle
```

Reads are asynchronous too, so a slower SD card later changes nothing above the port. `fs_execute` is plain
POSIX (`opendir`, `stat`, `fopen`, `fsync`, `rename`, `unlink`, `mkdir`, `rmdir`) and runs unchanged on both
roots. A write goes to `dir/.w-name`, is synced, and then replaces the file; FAT cannot rename over an existing
name, so the layer removes the old file first and recovers a leftover temporary file the next time the
directory or the file is looked at. Files are text: at most 64 KB, UTF-8 checked on read and write.

### Tests

Nine native tests run small worlds through the real host binary with a fresh root: claims, path rules, rights,
narrowing, passing and revoking a handle between worlds, a crashing segment that writes nothing, sizes and
UTF-8, rename/remove/recovery, and a restarted world that must not receive a stale result. They pass, also
under AddressSanitizer with leak detection and UndefinedBehaviorSanitizer set to halt.

One side effect showed up in the screenshot regression: the prelude's new methods cost about 4 KB of heap per
world on the 64-bit host, which pushed the `flaky` test world past its 256 KB limit at boot. It now has 320 KB
like the other small worlds.

## The keyboard controller and resets

The PicoCalc's keyboard and battery are read from an STM32 over I2C at 10 kHz; a transaction holds the bus for
about 5.6 ms of every 20 ms poll. During the device tests the controller stopped acknowledging its address after
a reset of the P4, and stayed silent until the whole PicoCalc was power-cycled; the power driver, which reads the
battery from the same chip, crashed on every attempt and was stopped by the supervisor ("power crashed").

The first theory was the classic one: the reset cut a byte in half and the slave holds SDA low. A bus recovery
(nine clocks and a STOP before the driver starts) was added with a log line for the case it handles. In a test
of ten resets the controller wedged at the fifth, and the log line never appeared: SDA was free, and the STM32
simply no longer answered. The recovery was removed. What works is not interrupting the controller: a console
command `hold` stops the I2C worker between transactions, `reboot` holds and then restarts, and the capture tool
sends `hold` before it pulls the reset line. Ten held resets in a row were clean. The power driver now logs I2C
failures instead of crashing, as the keyboard driver already did.

## Current status

- Done: commits `e16fa7d` (host), `6f12990` (device), docs `06d5b49`. Guide and diary on the reMarkable under
  `/ai/2026/10/31/PICOCALC-FS`.
- The first world-level use of files on the device is the Files app in the next ticket.

## Open questions

- The SD card: map the adapter's SPI0 pins (GP16–19, card detect GP22) to P4 GPIOs and mount it as a second root.
- The PaperS3 build has the file layer but no root; its MicroQuickJS binding has no file operations yet.
- Flashing still resets through RTS; a flash script should send `hold` first.

## Next

PICOCALC-EDIT: a text editor and a file browser built on these handles, and the agent's notes moved into files.

## Important files

- `picocalc-os/nucleus/fs.c` — path rules and the POSIX layer
- `picocalc-os/nucleus/vm.c` — `hw.fs`, `fs.at`, `ka_fs`
- `picocalc-os/js/prelude.js` — file methods on `Handle`
- `picocalc-os/port/esp32p4/main/fs_p4.c` — mount, worker, console `ls`/`cat`/`df`
- `picocalc-os/port/esp32p4/main/bus_p4.c` — `bus_p4_hold`
- `picocalc-os/tests/test_fs_native.py`
- Ticket: `ttmp/2026/10/31/PICOCALC-FS--files-on-the-picocalc-a-filesystem-file-handles-and-a-file-service/`
