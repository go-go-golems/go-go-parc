# Rabbit-R1 Ubuntu Touch Setup

- URL: https://chatgpt.com/c/6a7628fc-1b94-83ea-be46-274170ac6c93
- Created: 2026-08-07T18:50:37.003Z

---

> I am seeing "dm-verity corruption" after booting my rabbit-r1, I found this to maybe help: https\://github.com/jonathanprocter/rabbit-r1-deverity-recovery/blob/main/docs/rabbit-r1-de-verity-recovery-community-writeup.md I have been using https\://github.com/RabbitHoleEscapeR1/r1\_escape first to go into flashboot, and then I ran these commands:
>
>
>
> Explain to me what this actually all is about and how I  get from here to running ubuntu touch on this device. 
>
>
>
> Write a markdown and PDF textbook style document that explains it all
>
>
>
> \---
>
> code/others/rabbit-r1
> ❯ git clone https\://github.com/RabbitHoleEscapeR1/r1\_escape.git
> Cloning into 'r1\_escape'...
> remote: Enumerating objects: 63, done.
> remote: Counting objects: 100% (20/20), done.
> remote: Compressing objects: 100% (14/14), done.
> remote: Total 63 (delta 12), reused 7 (delta 6), pack-reused 43 (from 1)
> Receiving objects: 100% (63/63), 20.71 KiB | 20.71 MiB/s, done.
> Resolving deltas: 100% (31/31), done.
> code/others/rabbit-r1
> ❯ cat /etc/modprobe.d/blacklist-cdc\_acm.conf 2>/dev/null
> code/others/rabbit-r1
> ❯ modprobe cdc\_acm
> code/others/rabbit-r1
> ❯ >....
>
> ### Step 14: Reboot
>
> ```bash
> fastboot reboot
> ```
>
> The device will show an "orange state" warning briefly (this is normal -- it indicates the bootloader is unlocked), then boot into CipherOS.
>
> ### Step 15: Configure ADB Access
>
> On the host, disable `cdc_acm` so `adb` can connect:
>
> ```bash
> rmmod cdc_acm
>
> # Re-enable the blacklist to persist across reboots
> mv /etc/modprobe.d/blacklist-cdc_acm.conf.disabled /etc/modprobe.d/blacklist-cdc_acm.conf
>
> # Verify ADB connection
> adb devices
> ```
>
> ### Step 16: Post-Install Setup
>
> ```bash
> # Wake the screen (it may appear off due to sleep)
> adb shell input keyevent KEYCODE_WAKEUP
>
> # Set display density for R1's small screen
> adb shell wm density 190
> ```
>
> You should now see the CipherOS home screen on the R1.
>
> ## Restoring Stock Firmware
>
> The R1 can always be restored to stock RabbitOS:
>
> 1. Enter fastboot mode via `mtkbootcmd.py` (Step 1 above)
> 2. Flash stock boot.img to both slots (Step 2)
> 3. Flash vbmeta with `--disable-verity --disable-verification` (Step 3)
> 4. Reboot to fastbootd (Step 4)
> 5. Flash stock super.img (Step 5)
> 6. Erase userdata: `fastboot erase userdata`
> 7. Reboot: `fastboot reboot`
>
> Stock firmware v0.8.293 is available at [rabbit-hmi-oss/firmware](https://github.com/rabbit-hmi-oss/firmware/releases).
>
> ## Final Configuration
>
> | Setting                                                                         | Value                                  |
> | ------------------------------------------------------------------------------- | -------------------------------------- |
> | ROM                                                                             | CipherOS (cipher\_r1-userdebug)        |
> | Android Version                                                                 | 16                                     |
> | Build                                                                           | BP2A.250605.031.A2                     |
> | Architecture                                                                    | arm64-v8a                              |
> | SDK Level                                                                       | 36                                     |
> | Display Density                                                                 | 190                                    |
> | Active Slot                                                                     | a                                      |
> | Boot Image                                                                      | Stock v0.8.293 (for fastbootd support) |
> | System/Vendor/Product                                                           | CipherOS                               |
> | code/others/rabbit-r1                                                           |                                        |
> | ❯ python3 r1\_escape/mtkbootcmd.py FASTBOOT                                     |                                        |
> | Traceback (most recent call last):                                              |                                        |
> | File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkbootcmd.py", line 6, in  |                                        |
>
> ```
> import serial
> ```
>
> ModuleNotFoundError: No module named 'serial'
> code/others/rabbit-r1
> ❯ pip3 install pyserial
> Collecting pyserial
> Downloading pyserial-3.5-py2.py3-none-any.whl.metadata (1.6 kB)
> Downloading pyserial-3.5-py2.py3-none-any.whl (90 kB)
> Installing collected packages: pyserial
> Successfully installed pyserial-3.5
>
> [notice] A new release of pip is available: 24.3.1 -> 26.2
> [notice] To update, run: pip install --upgrade pip
> code/others/rabbit-r1 took 2s
> ❯ python3 r1\_escape/mtkbootcmd.py FASTBOOT
> Listening for ports!
> Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface
> HWID: USB VID\:PID=0E8D:2000 LOCATION=3-1:1.0
> Got port: /dev/ttyACM0
> Initializing port /dev/ttyACM0
> b'FASTBOOT' cmd sent
> code/others/rabbit-r1 took 38s
> ❯ fastboot devices
> code/others/rabbit-r1
> ❯ fastboot devices
> code/others/rabbit-r1
> ❯ fastboot devices
> code/others/rabbit-r1
> ❯ sudo fastboot devices
> code/others/rabbit-r1
> ❯ sudo su
> root\@f:/home/manuel/code/others/rabbit-r1# fastboot devices
> root\@f:/home/manuel/code/others/rabbit-r1# fastboot devices
> root\@f:/home/manuel/code/others/rabbit-r1# sudo ^C
> root\@f:/home/manuel/code/others/rabbit-r1# bluetoothctl info 08\:FF:44:2B:4C:90^C
> root\@f:/home/manuel/code/others/rabbit-r1# python3 r1\_escape/mtkbootcmd.py FASTBOOT
> Listening for ports!
> Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface
> HWID: USB VID\:PID=0E8D:2000 LOCATION=3-1:1.0
> Got port: /dev/ttyACM0
> Initializing port /dev/ttyACM0
> b'FASTBOOT' cmd sent
> root\@f:/home/manuel/code/others/rabbit-r1# unzip \~/^C
> root\@f:/home/manuel/code/others/rabbit-r1#
> exit
> code/others/rabbit-r1 took 1m55s
> ❯ unzip \~/Downloads/rabbit\_OS\_v0.8.293.zip
> Archive:  /home/manuel/Downloads/rabbit\_OS\_v0.8.293.zip
> creating: rabbit\_OS\_v0.8.293\_20250516110545/
> inflating: \_\_MACOSX/.\_rabbit\_OS\_v0.8.293\_20250516110545
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/sspm.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_sspm.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/preloader\_emmc.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_preloader\_emmc.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/scp.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_scp.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/MT6765\_Android\_scatter.xml
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_MT6765\_Android\_scatter.xml
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/tee.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_tee.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/boot.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_boot.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/lk.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_lk.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/super\_empty.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_super\_empty.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/vbmeta.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_vbmeta.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/preloader\_ufs.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_preloader\_ufs.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/MT6765\_Android\_scatter.txt
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_MT6765\_Android\_scatter.txt
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/preloader\_raw\.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_preloader\_raw\.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/gz.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_gz.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/preloader.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_preloader.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/preloader\_k65v1\_64\_bsp.bin
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_preloader\_k65v1\_64\_bsp.bin
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/md1img.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_md1img.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/super.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_super.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/dtbo.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_dtbo.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/spmfw\.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_spmfw\.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/vbmeta\_system.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_vbmeta\_system.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/logo.bin
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_logo.bin
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/userdata.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_userdata.img
> inflating: rabbit\_OS\_v0.8.293\_20250516110545/vbmeta\_vendor.img
> inflating: \_\_MACOSX/rabbit\_OS\_v0.8.293\_20250516110545/.\_vbmeta\_vendor.img
> code/others/rabbit-r1 took 14s
> ❯ fastboot flash boot\_a /path/to/stock\_firmware/boot.img
> fastboot: error: cannot load '/path/to/stock\_firmware/boot.img': No such file or directory
> code/others/rabbit-r1
> ❯ fastboot flash boot\_a ./rabbit\_OS\_v0.8.293\_20250516110545/boot.img
> Sending 'boot\_a' (32768 KB)                        OKAY [  1.210s]
> Writing 'boot\_a'                                   FAILED (remote: 'not allowed in locked state')
> fastboot: error: Command failed
> code/others/rabbit-r1
> ❯ fastboot flash boot\_b ./rabbit\_OS\_v0.8.293\_20250516110545/boot.img
> Sending 'boot\_b' (32768 KB)                        OKAY [  1.209s]
> Writing 'boot\_b'                                   FAILED (remote: 'not allowed in locked state')
> fastboot: error: Command failed
> code/others/rabbit-r1
> ❯ fastboot oem unlock
> FAILED (remote: 'unknown command')
> fastboot: error: Command failed
> code/others/rabbit-r1
> ❯ fastboot bootloader unlock
> fastboot: usage: unknown command bootloader
> code/others/rabbit-r1
> ❯ fastboot
> fastboot: usage: no command
> code/others/rabbit-r1
> ❯ fastboot help
> usage: fastboot [OPTION...] COMMAND...
>
> flashing:
> update ZIP                 Flash all partitions from an update.zip package.
> flashall                   Flash all partitions from $ANDROID\_PRODUCT\_OUT.
> On A/B devices, flashed slot is set as active.
> Secondary images may be flashed to inactive slot.
> flash PARTITION [FILENAME] Flash given partition, using the image from
> $ANDROID\_PRODUCT\_OUT if no filename is given.
>
> basics:
> devices [-l]               List devices in bootloader (-l: with device paths).
> getvar NAME                Display given bootloader variable.
> reboot [bootloader]        Reboot device.
>
> locking/unlocking:
> flashing lock|unlock       Lock/unlock partitions for flashing
> flashing lock\_critical|unlock\_critical
> Lock/unlock 'critical' bootloader partitions.
> flashing get\_unlock\_ability
> Check whether unlocking is allowed (1) or not(0).
>
> advanced:
> erase PARTITION            Erase a flash partition.
> format[:FS\_TYPE] PARTITION
> Format a flash partition.
> set\_active SLOT            Set the active slot.
> oem [COMMAND...]           Execute OEM-specific command.
> gsi wipe|disable           Wipe or disable a GSI installation (fastbootd only).
> wipe-super [SUPER\_EMPTY]   Wipe the super partition. This will reset it to
> contain an empty set of default dynamic partitions.
> create-logical-partition NAME SIZE
> Create a logical partition with the given name and
> size, in the super partition.
> delete-logical-partition NAME
> Delete a logical partition with the given name.
> resize-logical-partition NAME SIZE
> Change the size of the named logical partition.
> snapshot-update cancel     On devices that support snapshot-based updates, cancel
> an in-progress update. This may make the device
> unbootable until it is reflashed.
> snapshot-update merge      On devices that support snapshot-based updates, finish
> an in-progress update if it is in the "merging"
> phase.
> fetch PARTITION OUT\_FILE   Fetch a partition image from the device.
> boot image:
> boot KERNEL [RAMDISK [SECOND]]
> Download and boot kernel from RAM.
> flash\:raw PARTITION KERNEL [RAMDISK [SECOND]]
> Create boot image and flash it.
> \--dtb DTB                  Specify path to DTB for boot image header version 2.
> \--cmdline CMDLINE          Override kernel command line.
> \--base ADDRESS             Set kernel base address (default: 0x10000000).
> \--kernel-offset            Set kernel offset (default: 0x00008000).
> \--ramdisk-offset           Set ramdisk offset (default: 0x01000000).
> \--tags-offset              Set tags offset (default: 0x00000100).
> \--dtb-offset               Set dtb offset (default: 0x01100000).
> \--page-size BYTES          Set flash page size (default: 2048).
> \--header-version VERSION   Set boot image header version.
> \--os-version MAJOR[.MINOR[.PATCH]]
> Set boot image OS version (default: 0.0.0).
> \--os-patch-level YYYY-MM-DD
> Set boot image OS security patch level.
>
> Android Things:
> stage IN\_FILE              Sends given file to stage for the next command.
> get\_staged OUT\_FILE        Writes data staged by the last command to a file.
>
> options:
> -w                         Wipe userdata.
> -s SERIAL                  Specify a USB device.
> -s tcp|udp\:HOST     Specify a network device.
> -S SIZE[K|M|G]             Break into sparse files no larger than SIZE.
> \--force                    Force a flash operation that may be unsafe.
> \--slot SLOT                Use SLOT; 'all' for both slots, 'other' for
> non-current slot (default: current active slot).
> \--set-active[=SLOT]        Sets the active slot before rebooting.
> \--skip-secondary           Don't flash secondary slots in flashall/update.
> \--skip-reboot              Don't reboot device after flashing.
> \--disable-verity           Sets disable-verity when flashing vbmeta.
> \--disable-verification     Sets disable-verification when flashing vbmeta.
> \--fs-options=OPTION[,OPTION]
> Enable filesystem features. OPTION supports casefold, projid, compress
> \--unbuffered               Don't buffer input or output.
> \--verbose, -v              Verbose output.
> \--version                  Display version.
> \--help, -h                 Show this message.
> code/others/rabbit-r1
> ❯ fastboot flashing unlock
> (bootloader) Start unlock flow
>
> FAILED (remote: '
> Unlock operation is not allowed
> ')
> fastboot: error: Command failed
> code/others/rabbit-r1 took 3s
> ❯ fastboot flashing get\_unlock\_capability
> fastboot: usage: unknown 'flashing' command get\_unlock\_capability
> code/others/rabbit-r1
> ❯ fastboot flashing get\_unlock\_ability
> (bootloader) unlock\_ability = 0
> OKAY [  0.001s]
> Finished. Total time: 0.001s
> code/others/rabbit-r1
> ❯ fastboot flashing unlock
> (bootloader) Start unlock flow
>
> FAILED (remote: '
> Unlock operation is not allowed
> ')
> fastboot: error: Command failed
> code/others/rabbit-r1 took 3s
> ❯ fastboot flashing get\_unlock\_ability
> (bootloader) unlock\_ability = 0
> OKAY [  0.001s]
> Finished. Total time: 0.001s
> code/others/rabbit-r1
> ❯ fastboot flashing unlock
> (bootloader) Start unlock flow
>
> FAILED (remote: '
> Unlock operation is not allowed
> ')
> fastboot: error: Command failed
> code/others/rabbit-r1 took 3s
> ❯ fastboot flashing unlock
> (bootloader) Start unlock flow
>
> FAILED (remote: '
> Unlock operation is not allowed
> ')
> fastboot: error: Command failed
> code/others/rabbit-r1 took 3s
> ❯ fastboot flashing unlock --help
> usage: fastboot [OPTION...] COMMAND...
>
> flashing:
> update ZIP                 Flash all partitions from an update.zip package.
> flashall                   Flash all partitions from $ANDROID\_PRODUCT\_OUT.
> On A/B devices, flashed slot is set as active.
> Secondary images may be flashed to inactive slot.
> flash PARTITION [FILENAME] Flash given partition, using the image from
> $ANDROID\_PRODUCT\_OUT if no filename is given.
>
> basics:
> devices [-l]               List devices in bootloader (-l: with device paths).
> getvar NAME                Display given bootloader variable.
> reboot [bootloader]        Reboot device.
>
> locking/unlocking:
> flashing lock|unlock       Lock/unlock partitions for flashing
> flashing lock\_critical|unlock\_critical
> Lock/unlock 'critical' bootloader partitions.
> flashing get\_unlock\_ability
> Check whether unlocking is allowed (1) or not(0).
>
> advanced:
> erase PARTITION            Erase a flash partition.
> format[:FS\_TYPE] PARTITION
> Format a flash partition.
> set\_active SLOT            Set the active slot.
> oem [COMMAND...]           Execute OEM-specific command.
> gsi wipe|disable           Wipe or disable a GSI installation (fastbootd only).
> wipe-super [SUPER\_EMPTY]   Wipe the super partition. This will reset it to
> contain an empty set of default dynamic partitions.
> create-logical-partition NAME SIZE
> Create a logical partition with the given name and
> size, in the super partition.
> delete-logical-partition NAME
> Delete a logical partition with the given name.
> resize-logical-partition NAME SIZE
> Change the size of the named logical partition.
> snapshot-update cancel     On devices that support snapshot-based updates, cancel
> an in-progress update. This may make the device
> unbootable until it is reflashed.
> snapshot-update merge      On devices that support snapshot-based updates, finish
> an in-progress update if it is in the "merging"
> phase.
> fetch PARTITION OUT\_FILE   Fetch a partition image from the device.
> boot image:
> boot KERNEL [RAMDISK [SECOND]]
> Download and boot kernel from RAM.
> flash\:raw PARTITION KERNEL [RAMDISK [SECOND]]
> Create boot image and flash it.
> \--dtb DTB                  Specify path to DTB for boot image header version 2.
> \--cmdline CMDLINE          Override kernel command line.
> \--base ADDRESS             Set kernel base address (default: 0x10000000).
> \--kernel-offset            Set kernel offset (default: 0x00008000).
> \--ramdisk-offset           Set ramdisk offset (default: 0x01000000).
> \--tags-offset              Set tags offset (default: 0x00000100).
> \--dtb-offset               Set dtb offset (default: 0x01100000).
> \--page-size BYTES          Set flash page size (default: 2048).
> \--header-version VERSION   Set boot image header version.
> \--os-version MAJOR[.MINOR[.PATCH]]
> Set boot image OS version (default: 0.0.0).
> \--os-patch-level YYYY-MM-DD
> Set boot image OS security patch level.
>
> Android Things:
> stage IN\_FILE              Sends given file to stage for the next command.
> get\_staged OUT\_FILE        Writes data staged by the last command to a file.
>
> options:
> -w                         Wipe userdata.
> -s SERIAL                  Specify a USB device.
> -s tcp|udp\:HOST     Specify a network device.
> -S SIZE[K|M|G]             Break into sparse files no larger than SIZE.
> \--force                    Force a flash operation that may be unsafe.
> \--slot SLOT                Use SLOT; 'all' for both slots, 'other' for
> non-current slot (default: current active slot).
> \--set-active[=SLOT]        Sets the active slot before rebooting.
> \--skip-secondary           Don't flash secondary slots in flashall/update.
> \--skip-reboot              Don't reboot device after flashing.
> \--disable-verity           Sets disable-verity when flashing vbmeta.
> \--disable-verification     Sets disable-verification when flashing vbmeta.
> \--fs-options=OPTION[,OPTION]
> Enable filesystem features. OPTION supports casefold, projid, compress
> \--unbuffered               Don't buffer input or output.
> \--verbose, -v              Verbose output.
> \--version                  Display version.
> \--help, -h                 Show this message.
> code/others/rabbit-r1
> ❯ fastboot flashing unlock --disable-verify --disable-verification
> fastboot: unrecognized option '--disable-verify'
> code/others/rabbit-r1
> ❯ fastboot flashing unlock --disable-verify --disable-verification
> code/others/rabbit-r1
> ❯ cd ..
> \~/code/others
> ❯ git clone https\://github.com/RabbitHoleEscapeR1/r1\_escape.git
> \~/code/others
> ❯ cd -
> \~/code/others/rabbit-r1
> code/others/rabbit-r1
> ❯ ls
> \_\_MACOSX  r1\_escape  rabbit\_OS\_v0.8.293\_20250516110545
> code/others/rabbit-r1
> ❯ cd r1\_escape
> r1\_escape on  main via 🐍 v3.13.2
> ❯ ls
> mtkbootcmd.py  r1.ps1  r1.sh  README.md  vbmeta.img
> r1\_escape on  main via 🐍 v3.13.2
> ❯ cat r1.sh
> \#!/bin/bash
>
> install\_debian() {
> sudo apt update
> [[ -x "$(command -v git)" ]] || sudo apt install -y git
> [[ -x "$(command -v python3)" ]] || sudo apt install -y python3
> [[ -x "$(command -v pip3)" ]] || sudo apt install -y python3-pip
> [[ -x "$(command -v dos2unix)" ]] || sudo apt install -y dos2unix
> [[ -x "$(command -v curl)" ]] || sudo apt install -y curl
> [[ -x "$(command -v unzip)" ]] || sudo apt install -y unzip
> }
>
> install\_arch() {
> sudo pacman -Sy --noconfirm
> [[ -x "$(command -v git)" ]] || sudo pacman -S --noconfirm git
> [[ -x "$(command -v python3)" ]] || sudo pacman -S --noconfirm python
> [[ -x "$(command -v dos2unix)" ]] || sudo pacman -S --noconfirm dos2unix
> [[ -x "$(command -v curl)" ]] || sudo pacman -S --noconfirm curl
> [[ -x "$(command -v unzip)" ]] || sudo pacman -S --noconfirm unzip
> [[ -x "$(command -v virtualenv)" ]] || sudo pacman -S --noconfirm python-virtualenv
> }
>
> install\_fedora() {
> sudo dnf update -y
> [[ -x "$(command -v git)" ]] || sudo dnf install -y git
> [[ -x "$(command -v python3)" ]] || sudo dnf install -y python3
> [[ -x "$(command -v pip3)" ]] || sudo dnf install -y python3-pip
> [[ -x "$(command -v dos2unix)" ]] || sudo dnf install -y dos2unix
> [[ -x "$(command -v curl)" ]] || sudo dnf install -y curl
> [[ -x "$(command -v unzip)" ]] || sudo dnf install -y unzip
> }
>
> if [[ "$OSTYPE" == "linux-gnu"\* ]]; then
> if command -v apt-get &>/dev/null; then
> install\_debian
> elif command -v pacman &>/dev/null; then
> install\_arch
> elif command -v dnf &>/dev/null; then
> install\_fedora
> else
> echo "Unsupported Linux distribution"
> exit 1
> fi
> else
> echo "Unsupported OS"
> exit 1
> fi
>
> if [[ "$OSTYPE" != "linux-gnu"\* || ! "$(command -v pacman)" ]]; then
> pip3 show virtualenv &>/dev/null || pip3 install virtualenv
> fi
>
> if [[ "$OSTYPE" == "linux-gnu"\* ]]; then
> if command -v apt-get &>/dev/null; then
> sudo apt install -y adb fastboot
> elif command -v pacman &>/dev/null; then
> sudo pacman -S --noconfirm android-tools
> elif command -v dnf &>/dev/null; then
> sudo dnf install -y android-tools
> fi
> fi
>
> # Setup virtualenv and install requirements
>
> python3 -m venv venv
> source venv/bin/activate
>
> chmod +x mtkbootcmd.py
>
> # Download mtkclient
>
> REPO\_URL="https\://github.com/AgentFabulous/mtkclient"
> REPO\_NAME=$(basename "$REPO\_URL" .git)
> git clone "$REPO\_URL"
> cd "$REPO\_NAME" || exit
> pip3 install -r requirements.txt
>
> rm -f frp.bin
>
> read -p "[\*] Power off your device, press ENTER plug it into your PC"
>
> # Read FRP
>
> sudo python3 mtk r frp frp.bin
>
> sudo chown $USER frp.bin
>
> LAST\_BYTE=$(xxd -p -l 1 -s -1 frp.bin)
> if [[ "$LAST\_BYTE" == "00" ]]; then
> printf '\x01' | dd of=frp.bin bs=1 seek=$(($(stat -c%s frp.bin) - 1)) conv=notrunc
> fi
>
> # Write FRP
>
> sudo python3 mtk w frp frp.bin
>
> read -p "[\*] Unplug your device, press ENTER, plug it back in"
>
> cd ..
>
> sudo ./mtkbootcmd.py FASTBOOT
>
> echo "[\*] Waiting for fastboot..."
> while ! fastboot devices | grep -q "fastboot"; do
> sleep 1
> done
>
> fastboot flashing unlock
> fastboot -w
> fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img
> fastboot reboot-fastboot
> fastboot flash system system.img
> fastboot reboot
> r1\_escape on  main via 🐍 v3.13.2
> ❯ # Download mtkclient
> REPO\_URL="https\://github.com/AgentFabulous/mtkclient"
> REPO\_NAME=$(basename "$REPO\_URL" .git)
> git clone "$REPO\_URL"
> cd "$REPO\_NAME" || exit
> pip3 install -r requirements.txt
> Cloning into 'mtkclient'...
> remote: Enumerating objects: 5833, done.
> remote: Counting objects: 100% (4/4), done.
> remote: Compressing objects: 100% (4/4), done.
> remote: Total 5833 (delta 0), reused 0 (delta 0), pack-reused 5829 (from 1)
> Receiving objects: 100% (5833/5833), 88.87 MiB | 25.00 MiB/s, done.
> Resolving deltas: 100% (4525/4525), done.
> Collecting wheel>=0.37.1 (from -r requirements.txt (line 1))
> Downloading wheel-0.47.0-py3-none-any.whl.metadata (2.3 kB)
> Collecting pyusb>=1.2.1 (from -r requirements.txt (line 2))
> Downloading pyusb-1.3.1-py3-none-any.whl.metadata (2.5 kB)
> Requirement already satisfied: pycryptodome>=3.15.0 in /home/manuel/.pyenv/versions/3.13.2/lib/python3.13/site-packages (from -r requirements.txt (line 3)) (3.23.0)
> Collecting pycryptodomex (from -r requirements.txt (line 4))
> Downloading pycryptodomex-3.23.0-cp37-abi3-manylinux\_2\_17\_x86\_64.manylinux2014\_x86\_64.whl.metadata (3.4 kB)
> Collecting colorama>=0.4.4 (from -r requirements.txt (line 5))
> Using cached colorama-0.4.6-py2.py3-none-any.whl.metadata (17 kB)
> Collecting shiboken6>=6.4.0.1 (from -r requirements.txt (line 6))
> Downloading shiboken6-6.11.1-cp310-abi3-manylinux\_2\_34\_x86\_64.whl.metadata (2.4 kB)
> Collecting pyside6>=6.4.0.1 (from -r requirements.txt (line 7))
> Downloading pyside6-6.11.1-cp310-abi3-manylinux\_2\_34\_x86\_64.whl.metadata (5.3 kB)
> Collecting mock>=4.0.3 (from -r requirements.txt (line 8))
> Downloading mock-5.2.0-py3-none-any.whl.metadata (3.1 kB)
> Requirement already satisfied: pyserial>=3.5 in /home/manuel/.pyenv/versions/3.13.2/lib/python3.13/site-packages (from -r requirements.txt (line 9)) (3.5)
> Collecting flake8 (from -r requirements.txt (line 10))
> Downloading flake8-7.3.0-py2.py3-none-any.whl.metadata (3.8 kB)
> Collecting keystone-engine (from -r requirements.txt (line 11))
> Downloading keystone\_engine-0.9.2-py2.py3-none-manylinux1\_x86\_64.whl.metadata (1.8 kB)
> Collecting capstone (from -r requirements.txt (line 12))
> Downloading capstone-5.0.9-py3-none-manylinux\_2\_17\_x86\_64.manylinux2014\_x86\_64.whl.metadata (3.3 kB)
> Collecting unicorn (from -r requirements.txt (line 13))
> Downloading unicorn-2.1.4-cp37-abi3-manylinux\_2\_17\_x86\_64.manylinux2014\_x86\_64.whl.metadata (4.2 kB)
> Collecting fusepy (from -r requirements.txt (line 14))
> Downloading fusepy-3.0.1.tar.gz (11 kB)
> Installing build dependencies ... done
> Getting requirements to build wheel ... done
> Preparing metadata (pyproject.toml) ... done
> Requirement already satisfied: packaging>=24.0 in /home/manuel/.pyenv/versions/3.13.2/lib/python3.13/site-packages (from wheel>=0.37.1->-r requirements.txt (line 1)) (26.0)
> Collecting PySide6\_Essentials==6.11.1 (from pyside6>=6.4.0.1->-r requirements.txt (line 7))
> Downloading pyside6\_essentials-6.11.1-cp310-abi3-manylinux\_2\_34\_x86\_64.whl.metadata (3.6 kB)
> Collecting PySide6\_Addons==6.11.1 (from pyside6>=6.4.0.1->-r requirements.txt (line 7))
> Downloading pyside6\_addons-6.11.1-cp310-abi3-manylinux\_2\_34\_x86\_64.whl.metadata (4.0 kB)
> Collecting mccabe<0.8.0,>=0.7.0 (from flake8->-r requirements.txt (line 10))
> Downloading mccabe-0.7.0-py2.py3-none-any.whl.metadata (5.0 kB)
> Collecting pycodestyle<2.15.0,>=2.14.0 (from flake8->-r requirements.txt (line 10))
> Downloading pycodestyle-2.14.0-py2.py3-none-any.whl.metadata (4.5 kB)
> Collecting pyflakes<3.5.0,>=3.4.0 (from flake8->-r requirements.txt (line 10))
> Downloading pyflakes-3.4.0-py2.py3-none-any.whl.metadata (3.5 kB)
> Downloading wheel-0.47.0-py3-none-any.whl (32 kB)
> Downloading pyusb-1.3.1-py3-none-any.whl (58 kB)
> Downloading pycryptodomex-3.23.0-cp37-abi3-manylinux\_2\_17\_x86\_64.manylinux2014\_x86\_64.whl (2.3 MB)
> ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.3/2.3 MB 22.8 MB/s eta 0:00:00
> Using cached colorama-0.4.6-py2.py3-none-any.whl (25 kB)
> Downloading shiboken6-6.11.1-cp310-abi3-manylinux\_2\_34\_x86\_64.whl (272 kB)
> Downloading pyside6-6.11.1-cp310-abi3-manylinux\_2\_34\_x86\_64.whl (572 kB)
> ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 572.1/572.1 kB 33.8 MB/s eta 0:00:00
> Downloading pyside6\_addons-6.11.1-cp310-abi3-manylinux\_2\_34\_x86\_64.whl (175.1 MB)
> ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 175.1/175.1 MB 36.3 MB/s eta 0:00:00
> Downloading pyside6\_essentials-6.11.1-cp310-abi3-manylinux\_2\_34\_x86\_64.whl (79.9 MB)
> ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 79.9/79.9 MB 39.8 MB/s eta 0:00:00
> Downloading mock-5.2.0-py3-none-any.whl (31 kB)
> Downloading flake8-7.3.0-py2.py3-none-any.whl (57 kB)
> Downloading keystone\_engine-0.9.2-py2.py3-none-manylinux1\_x86\_64.whl (1.8 MB)
> ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.8/1.8 MB 46.0 MB/s eta 0:00:00
> Downloading capstone-5.0.9-py3-none-manylinux\_2\_17\_x86\_64.manylinux2014\_x86\_64.whl (1.5 MB)
> ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.5/1.5 MB 37.2 MB/s eta 0:00:00
> Downloading unicorn-2.1.4-cp37-abi3-manylinux\_2\_17\_x86\_64.manylinux2014\_x86\_64.whl (16.4 MB)
> ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 16.4/16.4 MB 38.4 MB/s eta 0:00:00
> Downloading mccabe-0.7.0-py2.py3-none-any.whl (7.3 kB)
> Downloading pycodestyle-2.14.0-py2.py3-none-any.whl (31 kB)
> Downloading pyflakes-3.4.0-py2.py3-none-any.whl (63 kB)
> Building wheels for collected packages: fusepy
> Building wheel for fusepy (pyproject.toml) ... done
> Created wheel for fusepy: filename=fusepy-3.0.1-py3-none-any.whl size=10538 sha256=b994d028c4f09522d8a767ac141c46bffad34f7ae7776df201eaeed73e08b7d9
> Stored in directory: /home/manuel/.cache/pip/wheels/bf/00/76/7656e1c2cf529781f66582d758f5295c93f81f4c30ea8156ae
> Successfully built fusepy
> Installing collected packages: keystone-engine, fusepy, wheel, unicorn, shiboken6, pyusb, pyflakes, pycryptodomex, pycodestyle, mock, mccabe, colorama, capstone, PySide6\_Essentials, flake8, PySide6\_Addons, pyside6
> Successfully installed PySide6\_Addons-6.11.1 PySide6\_Essentials-6.11.1 capstone-5.0.9 colorama-0.4.6 flake8-7.3.0 fusepy-3.0.1 keystone-engine-0.9.2 mccabe-0.7.0 mock-5.2.0 pycodestyle-2.14.0 pycryptodomex-3.23.0 pyflakes-3.4.0 pyside6-6.11.1 pyusb-1.3.1 shiboken6-6.11.1 unicorn-2.1.4 wheel-0.47.0
>
> [notice] A new release of pip is available: 24.3.1 -> 26.2
> [notice] To update, run: pip install --upgrade pip
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 took 24s
> ❯ sudo python3 mtk r frp frp.bin
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ fastboot
> fastboot: usage: no command
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ fastboot help
> usage: fastboot [OPTION...] COMMAND...
>
> flashing:
> update ZIP                 Flash all partitions from an update.zip package.
> flashall                   Flash all partitions from $ANDROID\_PRODUCT\_OUT.
> On A/B devices, flashed slot is set as active.
> Secondary images may be flashed to inactive slot.
> flash PARTITION [FILENAME] Flash given partition, using the image from
> $ANDROID\_PRODUCT\_OUT if no filename is given.
>
> basics:
> devices [-l]               List devices in bootloader (-l: with device paths).
> getvar NAME                Display given bootloader variable.
> reboot [bootloader]        Reboot device.
>
> locking/unlocking:
> flashing lock|unlock       Lock/unlock partitions for flashing
> flashing lock\_critical|unlock\_critical
> Lock/unlock 'critical' bootloader partitions.
> flashing get\_unlock\_ability
> Check whether unlocking is allowed (1) or not(0).
>
> advanced:
> erase PARTITION            Erase a flash partition.
> format[:FS\_TYPE] PARTITION
> Format a flash partition.
> set\_active SLOT            Set the active slot.
> oem [COMMAND...]           Execute OEM-specific command.
> gsi wipe|disable           Wipe or disable a GSI installation (fastbootd only).
> wipe-super [SUPER\_EMPTY]   Wipe the super partition. This will reset it to
> contain an empty set of default dynamic partitions.
> create-logical-partition NAME SIZE
> Create a logical partition with the given name and
> size, in the super partition.
> delete-logical-partition NAME
> Delete a logical partition with the given name.
> resize-logical-partition NAME SIZE
> Change the size of the named logical partition.
> snapshot-update cancel     On devices that support snapshot-based updates, cancel
> an in-progress update. This may make the device
> unbootable until it is reflashed.
> snapshot-update merge      On devices that support snapshot-based updates, finish
> an in-progress update if it is in the "merging"
> phase.
> fetch PARTITION OUT\_FILE   Fetch a partition image from the device.
> boot image:
> boot KERNEL [RAMDISK [SECOND]]
> Download and boot kernel from RAM.
> flash\:raw PARTITION KERNEL [RAMDISK [SECOND]]
> Create boot image and flash it.
> \--dtb DTB                  Specify path to DTB for boot image header version 2.
> \--cmdline CMDLINE          Override kernel command line.
> \--base ADDRESS             Set kernel base address (default: 0x10000000).
> \--kernel-offset            Set kernel offset (default: 0x00008000).
> \--ramdisk-offset           Set ramdisk offset (default: 0x01000000).
> \--tags-offset              Set tags offset (default: 0x00000100).
> \--dtb-offset               Set dtb offset (default: 0x01100000).
> \--page-size BYTES          Set flash page size (default: 2048).
> \--header-version VERSION   Set boot image header version.
> \--os-version MAJOR[.MINOR[.PATCH]]
> Set boot image OS version (default: 0.0.0).
> \--os-patch-level YYYY-MM-DD
> Set boot image OS security patch level.
>
> Android Things:
> stage IN\_FILE              Sends given file to stage for the next command.
> get\_staged OUT\_FILE        Writes data staged by the last command to a file.
>
> options:
> -w                         Wipe userdata.
> -s SERIAL                  Specify a USB device.
> -s tcp|udp\:HOST     Specify a network device.
> -S SIZE[K|M|G]             Break into sparse files no larger than SIZE.
> \--force                    Force a flash operation that may be unsafe.
> \--slot SLOT                Use SLOT; 'all' for both slots, 'other' for
> non-current slot (default: current active slot).
> \--set-active[=SLOT]        Sets the active slot before rebooting.
> \--skip-secondary           Don't flash secondary slots in flashall/update.
> \--skip-reboot              Don't reboot device after flashing.
> \--disable-verity           Sets disable-verity when flashing vbmeta.
> \--disable-verification     Sets disable-verification when flashing vbmeta.
> \--fs-options=OPTION[,OPTION]
> Enable filesystem features. OPTION supports casefold, projid, compress
> \--unbuffered               Don't buffer input or output.
> \--verbose, -v              Verbose output.
> \--version                  Display version.
> \--help, -h                 Show this message.
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ fastboot
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ cd r1\_escape
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ cd ..
> r1\_escape on  main via 🐍 v3.13.2
> ❯ ls
> mtkbootcmd.py  mtkclient  r1.ps1  r1.sh  README.md  vbmeta.img
> r1\_escape on  main via 🐍 v3.13.2
> ❯ fastboot
> r1\_escape on  main via 🐍 v3.13.2
> ❯ cat r1.sh
> \#!/bin/bash
>
> install\_debian() {
> sudo apt update
> [[ -x "$(command -v git)" ]] || sudo apt install -y git
> [[ -x "$(command -v python3)" ]] || sudo apt install -y python3
> [[ -x "$(command -v pip3)" ]] || sudo apt install -y python3-pip
> [[ -x "$(command -v dos2unix)" ]] || sudo apt install -y dos2unix
> [[ -x "$(command -v curl)" ]] || sudo apt install -y curl
> [[ -x "$(command -v unzip)" ]] || sudo apt install -y unzip
> }
>
> install\_arch() {
> sudo pacman -Sy --noconfirm
> [[ -x "$(command -v git)" ]] || sudo pacman -S --noconfirm git
> [[ -x "$(command -v python3)" ]] || sudo pacman -S --noconfirm python
> [[ -x "$(command -v dos2unix)" ]] || sudo pacman -S --noconfirm dos2unix
> [[ -x "$(command -v curl)" ]] || sudo pacman -S --noconfirm curl
> [[ -x "$(command -v unzip)" ]] || sudo pacman -S --noconfirm unzip
> [[ -x "$(command -v virtualenv)" ]] || sudo pacman -S --noconfirm python-virtualenv
> }
>
> install\_fedora() {
> sudo dnf update -y
> [[ -x "$(command -v git)" ]] || sudo dnf install -y git
> [[ -x "$(command -v python3)" ]] || sudo dnf install -y python3
> [[ -x "$(command -v pip3)" ]] || sudo dnf install -y python3-pip
> [[ -x "$(command -v dos2unix)" ]] || sudo dnf install -y dos2unix
> [[ -x "$(command -v curl)" ]] || sudo dnf install -y curl
> [[ -x "$(command -v unzip)" ]] || sudo dnf install -y unzip
> }
>
> if [[ "$OSTYPE" == "linux-gnu"\* ]]; then
> if command -v apt-get &>/dev/null; then
> install\_debian
> elif command -v pacman &>/dev/null; then
> install\_arch
> elif command -v dnf &>/dev/null; then
> install\_fedora
> else
> echo "Unsupported Linux distribution"
> exit 1
> fi
> else
> echo "Unsupported OS"
> exit 1
> fi
>
> if [[ "$OSTYPE" != "linux-gnu"\* || ! "$(command -v pacman)" ]]; then
> pip3 show virtualenv &>/dev/null || pip3 install virtualenv
> fi
>
> if [[ "$OSTYPE" == "linux-gnu"\* ]]; then
> if command -v apt-get &>/dev/null; then
> sudo apt install -y adb fastboot
> elif command -v pacman &>/dev/null; then
> sudo pacman -S --noconfirm android-tools
> elif command -v dnf &>/dev/null; then
> sudo dnf install -y android-tools
> fi
> fi
>
> # Setup virtualenv and install requirements
>
> python3 -m venv venv
> source venv/bin/activate
>
> chmod +x mtkbootcmd.py
>
> # Download mtkclient
>
> REPO\_URL="https\://github.com/AgentFabulous/mtkclient"
> REPO\_NAME=$(basename "$REPO\_URL" .git)
> git clone "$REPO\_URL"
> cd "$REPO\_NAME" || exit
> pip3 install -r requirements.txt
>
> rm -f frp.bin
>
> read -p "[\*] Power off your device, press ENTER plug it into your PC"
>
> # Read FRP
>
> sudo python3 mtk r frp frp.bin
>
> sudo chown $USER frp.bin
>
> LAST\_BYTE=$(xxd -p -l 1 -s -1 frp.bin)
> if [[ "$LAST\_BYTE" == "00" ]]; then
> printf '\x01' | dd of=frp.bin bs=1 seek=$(($(stat -c%s frp.bin) - 1)) conv=notrunc
> fi
>
> # Write FRP
>
> sudo python3 mtk w frp frp.bin
>
> read -p "[\*] Unplug your device, press ENTER, plug it back in"
>
> cd ..
>
> sudo ./mtkbootcmd.py FASTBOOT
>
> echo "[\*] Waiting for fastboot..."
> while ! fastboot devices | grep -q "fastboot"; do
> sleep 1
> done
>
> fastboot flashing unlock
> fastboot -w
> fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img
> fastboot reboot-fastboot
> fastboot flash system system.img
> fastboot reboot
> r1\_escape on  main via 🐍 v3.13.2
> ❯ sudo python3 mtk r frp frp.bin
> python3: can't open file '/home/manuel/code/others/rabbit-r1/r1\_escape/mtk': [Errno 2] No such file or directory
> r1\_escape on  main via 🐍 v3.13.2
> ❯ mtk
> zsh: command not found: mtk
> r1\_escape on  main via 🐍 v3.13.2
> ❯ cd -
> \~/code/others/rabbit-r1/r1\_escape/mtkclient
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ ls
> LICENSE  MANIFEST.in  mtk  mtk.bat  mtkclient  mtk\_console.spec  mtk\_gui  mtk\_gui.bat  mtk\_standalone.spec  pyproject.toml  README.md  requirements.txt  run.example  stage2  vbmeta.img.empty
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ cd -
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ sudo python3 mtk r frp frp.bin
> Traceback (most recent call last):
> File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkclient/mtk", line 5, in 
> from mtkclient.Library.mtk\_main import Main, metamodes
> File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkclient/mtkclient/Library/mtk\_main.py", line 10, in 
> from mtkclient.Library.mtk\_class import Mtk
> File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkclient/mtkclient/Library/mtk\_class.py", line 9, in 
> from mtkclient.Library.pltools import PLTools
> File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkclient/mtkclient/Library/pltools.py", line 12, in 
> from mtkclient.Library.Exploit.kamakiri import Kamakiri
> File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkclient/mtkclient/Library/Exploit/kamakiri.py", line 12, in 
> from mtkclient.Library.Connection.usblib import usb
> File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkclient/mtkclient/Library/Connection/usblib.py", line 7, in 
> import usb.core  # pyusb
> ^^^^^^^^^^^^^^^
> ModuleNotFoundError: No module named 'usb'
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ sudo pip3 install pyusb
> error: externally-managed-environment
>
> × This environment is externally managed
> ╰─> To install Python packages system-wide, try apt install
> python3-xyz, where xyz is the package you are trying to
> install.
>
> ```
> If you wish to install a non-Debian-packaged Python package,
> create a virtual environment using python3 -m venv path/to/venv.
> Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
> sure you have python3-full installed.
>
> If you wish to install a non-Debian packaged Python application,
> it may be easiest to use pipx install xyz, which will manage a
> virtual environment for you. Make sure you have pipx installed.
>
> See /usr/share/doc/python3.12/README.venv for more information.
> ```
>
> note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
> hint: See PEP 668 for the detailed specification.
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ sudo pip3 install pyusb
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ pip3 install pyusb
> Requirement already satisfied: pyusb in /home/manuel/.pyenv/versions/3.13.2/lib/python3.13/site-packages (1.3.1)
>
> [notice] A new release of pip is available: 24.3.1 -> 26.2
> [notice] To update, run: pip install --upgrade pip
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ sudo pip3 install pyusb
> error: externally-managed-environment
>
> × This environment is externally managed
> ╰─> To install Python packages system-wide, try apt install
> python3-xyz, where xyz is the package you are trying to
> install.
>
> ```
> If you wish to install a non-Debian-packaged Python package,
> create a virtual environment using python3 -m venv path/to/venv.
> Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
> sure you have python3-full installed.
>
> If you wish to install a non-Debian packaged Python application,
> it may be easiest to use pipx install xyz, which will manage a
> virtual environment for you. Make sure you have pipx installed.
>
> See /usr/share/doc/python3.12/README.venv for more information.
> ```
>
> note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
> hint: See PEP 668 for the detailed specification.
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ sudo python3 mtk r frp frp.bin
> Traceback (most recent call last):
> File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkclient/mtk", line 5, in 
> from mtkclient.Library.mtk\_main import Main, metamodes
> File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkclient/mtkclient/Library/mtk\_main.py", line 10, in 
> from mtkclient.Library.mtk\_class import Mtk
> File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkclient/mtkclient/Library/mtk\_class.py", line 9, in 
> from mtkclient.Library.pltools import PLTools
> File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkclient/mtkclient/Library/pltools.py", line 12, in 
> from mtkclient.Library.Exploit.kamakiri import Kamakiri
> File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkclient/mtkclient/Library/Exploit/kamakiri.py", line 12, in 
> from mtkclient.Library.Connection.usblib import usb
> File "/home/manuel/code/others/rabbit-r1/r1\_escape/mtkclient/mtkclient/Library/Connection/usblib.py", line 7, in 
> import usb.core  # pyusb
> ^^^^^^^^^^^^^^^
> ModuleNotFoundError: No module named 'usb'
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ python3 mtk r frp frp.bin
> MTK Flash/Exploit Client Public V2.0.0 Beta (c) B.Kerler 2018-2023
>
> Preloader - Status: Waiting for PreLoader VCOM, please reconnect mobile to brom mode
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ..........Preloader
> Preloader - [LIB]: Status: Handshake failed, retrying...
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ..........Preloader
> Preloader - [LIB]: Status: Handshake failed, retrying...
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
> Port - Device detected :)
> Preloader - 	CPU:			MT6765/MT8768t(Helio P35/G35)
> Preloader - 	HW version:		0x0
> Preloader - 	WDT:			0x10007000
> Preloader - 	Uart:			0x11002000
> Preloader - 	Brom payload addr:	0x100a00
> Preloader - 	DA payload addr:	0x201000
> Preloader - 	CQ\_DMA addr:		0x10212000
> Preloader - 	Var1:			0x25
> Preloader - Disabling Watchdog...
> Preloader - HW code:			0x766
> Preloader - Target config:		0x0
> Preloader - 	SBC enabled:		False
> Preloader - 	SLA enabled:		False
> Preloader - 	DAA enabled:		False
> Preloader - 	SWJTAG enabled:		False
> Preloader - 	EPP\_PARAM at 0x600 after EMMC\_BOOT/SDMMC\_BOOT:	False
> Preloader - 	Root cert required:	False
> Preloader - 	Mem read auth:		False
> Preloader - 	Mem write auth:		False
> Preloader - 	Cmd 0xC8 blocked:	False
> Preloader - Get Target info
> Preloader - 	HW subcode:		0x8a00
> Preloader - 	HW Ver:			0xca00
> Preloader - 	SW Ver:			0x0
> Preloader - ME\_ID:			55C0B1FC67D69E5E1CD382EA8780F8B7
> Preloader - SOC\_ID:			3DCB309F2C158F3FE2D1480E8E63B9CAA15C619AD66576D325D3DEC081CBFD71
> DA\_handler - Device is unprotected.
> DA\_handler - Device is in Preloader-Mode.
> DAXFlash - Uploading xflash stage 1 from MTK\_DA\_V5.bin
> xflashext - Patching da1 ...
> Mtk - Patched "Patched loader msg" in preloader
> Mtk - Patched "hash\_check" in preloader
> xflashext
> xflashext - [LIB]: Error on patching da1 version check...
> Mtk - Patched "Patched loader msg" in preloader
> Mtk - Patched "get\_vfy\_policy" in preloader
> xflashext - Patching da2 ...
> xflashext - DA version anti-rollback patched
> DAXFlash - Successfully uploaded stage 1, jumping ..
> Preloader - Jumping to 0x200000
> Preloader - Jumping to 0x200000: ok.
> DAXFlash - Successfully received DA sync
> DAXFlash - Uploading stage 2...
> DAXFlash - Upload data was accepted. Jumping to stage 2...
> DAXFlash - Successfully uploaded stage 2
> DAXFlash - EMMC FWVer:      0x0
> DAXFlash - EMMC ID:         DV6DAB
> DAXFlash - EMMC CID:        150100445636444142025c10dc0d291f
> DAXFlash - EMMC Boot1 Size: 0x400000
> DAXFlash - EMMC Boot2 Size: 0x400000
> DAXFlash - EMMC GP1 Size:   0x0
> DAXFlash - EMMC GP2 Size:   0x0
> DAXFlash - EMMC GP3 Size:   0x0
> DAXFlash - EMMC GP4 Size:   0x0
> DAXFlash - EMMC RPMB Size:  0x1000000
> DAXFlash - EMMC USER Size:  0x1d1ec00000
> DAXFlash - HW-CODE         : 0x766
> DAXFlash - HWSUB-CODE      : 0x8A00
> DAXFlash - HW-VERSION      : 0xCA00
> DAXFlash - SW-VERSION      : 0x0
> DAXFlash - CHIP-EVOLUTION  : 0x0
> DAXFlash - DA-VERSION      : 1.0
> DAXFlash - Extensions were accepted. Jumping to extensions...
> DAXFlash - DA Extensions successfully added
> DA\_handler - Requesting available partitions ....
> DA\_handler - Dumping partition "frp"
> Progress: |██████████████████████████████████████████████████| 100.0% Read (Sector 0x800 of 0x800, ) 3.00 MB/s
> DA\_handler - Dumped sector 44096 with sector count 2048 as frp.bin.
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 took 1m17s
> ❯ cat r1.sh
> cat: r1.sh: No such file or directory
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ cat ../r1.sh
> \#!/bin/bash
>
> install\_debian() {
> sudo apt update
> [[ -x "$(command -v git)" ]] || sudo apt install -y git
> [[ -x "$(command -v python3)" ]] || sudo apt install -y python3
> [[ -x "$(command -v pip3)" ]] || sudo apt install -y python3-pip
> [[ -x "$(command -v dos2unix)" ]] || sudo apt install -y dos2unix
> [[ -x "$(command -v curl)" ]] || sudo apt install -y curl
> [[ -x "$(command -v unzip)" ]] || sudo apt install -y unzip
> }
>
> install\_arch() {
> sudo pacman -Sy --noconfirm
> [[ -x "$(command -v git)" ]] || sudo pacman -S --noconfirm git
> [[ -x "$(command -v python3)" ]] || sudo pacman -S --noconfirm python
> [[ -x "$(command -v dos2unix)" ]] || sudo pacman -S --noconfirm dos2unix
> [[ -x "$(command -v curl)" ]] || sudo pacman -S --noconfirm curl
> [[ -x "$(command -v unzip)" ]] || sudo pacman -S --noconfirm unzip
> [[ -x "$(command -v virtualenv)" ]] || sudo pacman -S --noconfirm python-virtualenv
> }
>
> install\_fedora() {
> sudo dnf update -y
> [[ -x "$(command -v git)" ]] || sudo dnf install -y git
> [[ -x "$(command -v python3)" ]] || sudo dnf install -y python3
> [[ -x "$(command -v pip3)" ]] || sudo dnf install -y python3-pip
> [[ -x "$(command -v dos2unix)" ]] || sudo dnf install -y dos2unix
> [[ -x "$(command -v curl)" ]] || sudo dnf install -y curl
> [[ -x "$(command -v unzip)" ]] || sudo dnf install -y unzip
> }
>
> if [[ "$OSTYPE" == "linux-gnu"\* ]]; then
> if command -v apt-get &>/dev/null; then
> install\_debian
> elif command -v pacman &>/dev/null; then
> install\_arch
> elif command -v dnf &>/dev/null; then
> install\_fedora
> else
> echo "Unsupported Linux distribution"
> exit 1
> fi
> else
> echo "Unsupported OS"
> exit 1
> fi
>
> if [[ "$OSTYPE" != "linux-gnu"\* || ! "$(command -v pacman)" ]]; then
> pip3 show virtualenv &>/dev/null || pip3 install virtualenv
> fi
>
> if [[ "$OSTYPE" == "linux-gnu"\* ]]; then
> if command -v apt-get &>/dev/null; then
> sudo apt install -y adb fastboot
> elif command -v pacman &>/dev/null; then
> sudo pacman -S --noconfirm android-tools
> elif command -v dnf &>/dev/null; then
> sudo dnf install -y android-tools
> fi
> fi
>
> # Setup virtualenv and install requirements
>
> python3 -m venv venv
> source venv/bin/activate
>
> chmod +x mtkbootcmd.py
>
> # Download mtkclient
>
> REPO\_URL="https\://github.com/AgentFabulous/mtkclient"
> REPO\_NAME=$(basename "$REPO\_URL" .git)
> git clone "$REPO\_URL"
> cd "$REPO\_NAME" || exit
> pip3 install -r requirements.txt
>
> rm -f frp.bin
>
> read -p "[\*] Power off your device, press ENTER plug it into your PC"
>
> # Read FRP
>
> sudo python3 mtk r frp frp.bin
>
> sudo chown $USER frp.bin
>
> LAST\_BYTE=$(xxd -p -l 1 -s -1 frp.bin)
> if [[ "$LAST\_BYTE" == "00" ]]; then
> printf '\x01' | dd of=frp.bin bs=1 seek=$(($(stat -c%s frp.bin) - 1)) conv=notrunc
> fi
>
> # Write FRP
>
> sudo python3 mtk w frp frp.bin
>
> read -p "[\*] Unplug your device, press ENTER, plug it back in"
>
> cd ..
>
> sudo ./mtkbootcmd.py FASTBOOT
>
> echo "[\*] Waiting for fastboot..."
> while ! fastboot devices | grep -q "fastboot"; do
> sleep 1
> done
>
> fastboot flashing unlock
> fastboot -w
> fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img
> fastboot reboot-fastboot
> fastboot flash system system.img
> fastboot reboot
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ LAST\_BYTE=$(xxd -p -l 1 -s -1 frp.bin)
> if [[ "$LAST\_BYTE" == "00" ]]; then
> printf '\x01' | dd of=frp.bin bs=1 seek=$(($(stat -c%s frp.bin) - 1)) conv=notrunc
> fi
> 1+0 records in
> 1+0 records out
> 1 byte copied, 8.9455e-05 s, 11.2 kB/s
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ python3 mtk w frp frp.bin
> MTK Flash/Exploit Client Public V2.0.0 Beta (c) B.Kerler 2018-2023
>
> DAXFlash - HW-CODE         : 0x766
> DAXFlash - HWSUB-CODE      : 0x8A00
> DAXFlash - HW-VERSION      : 0xCA00
> DAXFlash - SW-VERSION      : 0x0
> DAXFlash - CHIP-EVOLUTION  : 0x0
> DAXFlash - DA-VERSION      : 1.0
> Progress: |██████████████████████████████████████████████████| 100.0% Write (Sector 0x800 of 0x800, ) 3.57 MB/s
> Wrote frp.bin to sector 44096 with sector count 2048.
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ cd ..
> r1\_escape on  main via 🐍 v3.13.2
> ❯ ./mtkbootcmd.py FASTBOOT
> Listening for ports!
> Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface
> HWID: USB VID\:PID=0E8D:2000 LOCATION=3-1:1.0
> Got port: /dev/ttyACM0
> Initializing port /dev/ttyACM0
> b'FASTBOOT' cmd sent
> r1\_escape on  main via 🐍 v3.13.2 took 6s
> ❯ while ! fastboot devices | grep -q "fastboot"; do
> sleep 1
> done
> r1\_escape on  main via 🐍 v3.13.2
> ❯ fastboot devices
> 919109A491600019115B	fastboot
>
> r1\_escape on  main via 🐍 v3.13.2
> ❯ fastboot flashing unlock
> (bootloader) Start unlock flow
>
> OKAY [  3.121s]
> Finished. Total time: 3.121s
> r1\_escape on  main via 🐍 v3.13.2 took 3s
> ❯ fastboot -w
> Erasing 'userdata'                                 OKAY [  1.454s]
> /usr/lib/android-sdk/platform-tools/mke2fs failed with status 1
> fastboot: error: Cannot generate image for userdata
> r1\_escape on  main via 🐍 v3.13.2
> ❯ fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img
> Rewriting vbmeta struct at offset: 0
> Sending 'vbmeta\_b' (4 KB)                          OKAY [  0.005s]
> Writing 'vbmeta\_b'                                 OKAY [  0.002s]
> Finished. Total time: 0.011s
> r1\_escape on  main via 🐍 v3.13.2
> ❯ ls
> mtkbootcmd.py  mtkclient  r1.ps1  r1.sh  README.md  vbmeta.img
> r1\_escape on  main via 🐍 v3.13.2
> ❯ fastboot reboot-fastboot
> Rebooting into fastboot                            OKAY [  0.001s]
> < waiting for any device >
> Finished. Total time: 23.013s
> r1\_escape on  main via 🐍 v3.13.2 took 23s
> ❯ ls
> mtkbootcmd.py  mtkclient  r1.ps1  r1.sh  README.md  vbmeta.img
> r1\_escape on  main via 🐍 v3.13.2
> ❯ cd ..
> code/others/rabbit-r1
> ❯ find . -name system.img
> code/others/rabbit-r1
> ❯ fastboot flashing unlock
> < waiting for any device >
> ^C
> code/others/rabbit-r1 took 54s
> ❯ fastboot flashing unlock
> code/others/rabbit-r1
> ❯ python3 r1\_escape/mtkbootcmd.py FASTBOOT
> Listening for ports!
> Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface
> HWID: USB VID\:PID=0E8D:2000 LOCATION=3-1:1.0
> Got port: /dev/ttyACM0
> Initializing port /dev/ttyACM0
> b'FASTBOOT' cmd sent
> code/others/rabbit-r1
> ❯ fastboot devices
> 919109A491600019115B	fastboot
>
> code/others/rabbit-r1
> ❯ fastboot flash boot\_1 ./rabbit\_OS\_v0.8.293\_20250516110545/boot.img
> Warning: skip copying boot\_1 image avb footer (boot\_1 partition size: 0, boot\_1 image size: 33554432).
> Sending 'boot\_1' (32768 KB)                        OKAY [  1.245s]
> Writing 'boot\_1'                                   FAILED (remote: 'This partition doesn't exist')
> fastboot: error: Command failed
> code/others/rabbit-r1
> ❯ fastboot flash boot\_a ./rabbit\_OS\_v0.8.293\_20250516110545/boot.img
> Sending 'boot\_a' (32768 KB)                        OKAY [  1.198s]
> Writing 'boot\_a'                                   OKAY [  0.430s]
> Finished. Total time: 1.631s
> code/others/rabbit-r1
> ❯ fastboot flash boot\_b ./rabbit\_OS\_v0.8.293\_20250516110545/boot.img
> Sending 'boot\_b' (32768 KB)                        OKAY [  1.206s]
> Writing 'boot\_b'                                   OKAY [  0.445s]
> Finished. Total time: 1.653s
> code/others/rabbit-r1
> ❯ fastboot --disable-verity --disable-verification flash vbmeta\_a ./rabbit\_OS\_v0.8.293\_20250516110545/vbmeta.img
> Rewriting vbmeta struct at offset: 0
> Sending 'vbmeta\_a' (4 KB)                          OKAY [  0.005s]
> Writing 'vbmeta\_a'                                 OKAY [  0.002s]
> Finished. Total time: 0.010s
> code/others/rabbit-r1
> ❯ fastboot --disable-verity --disable-verification flash vbmeta\_b ./rabbit\_OS\_v0.8.293\_20250516110545/vbmeta.img
> Rewriting vbmeta struct at offset: 0
> Sending 'vbmeta\_b' (4 KB)                          OKAY [  0.005s]
> Writing 'vbmeta\_b'                                 OKAY [  0.002s]
> Finished. Total time: 0.008s
> code/others/rabbit-r1
> ❯ fastboot --disable-verity --disable-verification flash vbmeta\_system\_a ./rabbit\_OS\_v0.8.293\_20250516110545/vbmeta\_system.img
> Sending 'vbmeta\_system\_a' (4 KB)                   OKAY [  0.005s]
> Writing 'vbmeta\_system\_a'                          OKAY [  0.002s]
> Finished. Total time: 0.010s
> code/others/rabbit-r1
> ❯ fastboot --disable-verity --disable-verification flash vbmeta\_system\_b ./rabbit\_OS\_v0.8.293\_20250516110545/vbmeta\_system.img
> Sending 'vbmeta\_system\_b' (4 KB)                   OKAY [  0.005s]
> Writing 'vbmeta\_system\_b'                          OKAY [  0.002s]
> Finished. Total time: 0.010s
> code/others/rabbit-r1
> ❯ fastboot --disable-verity --disable-verification flash vbmeta\_vendor\_a ./rabbit\_OS\_v0.8.293\_20250516110545/vbmeta\_vendor.img
> Sending 'vbmeta\_vendor\_a' (4 KB)                   OKAY [  0.005s]
> Writing 'vbmeta\_vendor\_a'                          OKAY [  0.002s]
> Finished. Total time: 0.009s
> code/others/rabbit-r1
> ❯ fastboot --disable-verity --disable-verification flash vbmeta\_vendor\_b ./rabbit\_OS\_v0.8.293\_20250516110545/vbmeta\_vendor.img
> Sending 'vbmeta\_vendor\_b' (4 KB)                   OKAY [  0.005s]
> Writing 'vbmeta\_vendor\_b'                          OKAY [  0.002s]
> Finished. Total time: 0.009s
> code/others/rabbit-r1
> ❯ fastboot reboot fastboot
> Rebooting into fastboot                            OKAY [  0.001s]
> < waiting for any device >
> ^C
> code/others/rabbit-r1 took 31s
> ❯ fastboot reboot fastboot
> < waiting for any device >
> ^C
> code/others/rabbit-r1 took 21s
> ❯ python3 r1\_escape/mtkbootcmd.py FASTBOOT
> Listening for ports!
> Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface
> HWID: USB VID\:PID=0E8D:2000 LOCATION=3-1:1.0
> Got port: /dev/ttyACM0
> Initializing port /dev/ttyACM0
> b'FASTBOOT' cmd sent
> code/others/rabbit-r1 took 2s
> ❯ fastboot reboot fastboot
> Rebooting into fastboot                            OKAY [  0.001s]
> < waiting for any device >
> ^[[A^[[A^C
> code/others/rabbit-r1 took 2s
> ❯ python3 r1\_escape/mtkbootcmd.py FASTBOOT
> Listening for ports!
> Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface
> HWID: USB VID\:PID=0E8D:2000 LOCATION=3-1:1.0
> Got port: /dev/ttyACM0
> Initializing port /dev/ttyACM0
> b'FASTBOOT' cmd sent
> code/others/rabbit-r1
> ❯ fastboot reboot fastbootcd mtk
> code/others/rabbit-r1
> ❯ cd ..
> code/others/rabbit-r1
> ❯ ls
> \_\_MACOSX  r1\_escape  rabbit\_OS\_v0.8.293\_20250516110545
> code/others/rabbit-r1
> ❯ find . -name mtkclient
> ./r1\_escape/mtkclient
> ./r1\_escape/mtkclient/mtkclient
> code/others/rabbit-r1
> ❯ cd r1\_escape/mtkclient
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ ls
> frp.bin  logs	     mtk      mtkclient	mtk\_gui      mtk\_standalone.spec  README.md	    run.example  vbmeta.img.empty
> LICENSE  MANIFEST.in  mtk.bat  mtk\_console.spec  mtk\_gui.bat  pyproject.toml	  requirements.txt  stage2
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ python3 mtk r frp frp.bin
> MTK Flash/Exploit Client Public V2.0.0 Beta (c) B.Kerler 2018-2023
>
> Preloader - Status: Waiting for PreLoader VCOM, please reconnect mobile to brom mode
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> ...........
>
> Port - Hint:
>
> Power off the phone before connecting.
> For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb.
> For preloader mode, don't press any hw button and connect usb.
> If it is already connected and on, hold power for 10 seconds to reset.
>
> Port - Device detected :)
> Preloader - 	CPU:			MT6765/MT8768t(Helio P35/G35)
> Preloader - 	HW version:		0x0
> Preloader - 	WDT:			0x10007000
> Preloader - 	Uart:			0x11002000
> Preloader - 	Brom payload addr:	0x100a00
> Preloader - 	DA payload addr:	0x201000
> Preloader - 	CQ\_DMA addr:		0x10212000
> Preloader - 	Var1:			0x25
> Preloader - Disabling Watchdog...
> Preloader - HW code:			0x766
> Preloader - Target config:		0x0
> Preloader - 	SBC enabled:		False
> Preloader - 	SLA enabled:		False
> Preloader - 	DAA enabled:		False
> Preloader - 	SWJTAG enabled:		False
> Preloader - 	EPP\_PARAM at 0x600 after EMMC\_BOOT/SDMMC\_BOOT:	False
> Preloader - 	Root cert required:	False
> Preloader - 	Mem read auth:		False
> Preloader - 	Mem write auth:		False
> Preloader - 	Cmd 0xC8 blocked:	False
> Preloader - Get Target info
> Preloader - 	HW subcode:		0x8a00
> Preloader - 	HW Ver:			0xca00
> Preloader - 	SW Ver:			0x0
> Preloader - ME\_ID:			55C0B1FC67D69E5E1CD382EA8780F8B7
> Preloader - SOC\_ID:			3DCB309F2C158F3FE2D1480E8E63B9CAA15C619AD66576D325D3DEC081CBFD71
> DA\_handler - Device is unprotected.
> DA\_handler - Device is in Preloader-Mode.
> DAXFlash - Uploading xflash stage 1 from MTK\_DA\_V5.bin
> xflashext - Patching da1 ...
> Mtk - Patched "Patched loader msg" in preloader
> Mtk - Patched "hash\_check" in preloader
> xflashext
> xflashext - [LIB]: Error on patching da1 version check...
> Mtk - Patched "Patched loader msg" in preloader
> Mtk - Patched "get\_vfy\_policy" in preloader
> xflashext - Patching da2 ...
> xflashext - DA version anti-rollback patched
> DAXFlash - Successfully uploaded stage 1, jumping ..
> Preloader - Jumping to 0x200000
> Preloader - Jumping to 0x200000: ok.
> DAXFlash - Successfully received DA sync
> DAXFlash - Uploading stage 2...
> DAXFlash - Upload data was accepted. Jumping to stage 2...
> DAXFlash - Successfully uploaded stage 2
> DAXFlash - EMMC FWVer:      0x0
> DAXFlash - EMMC ID:         DV6DAB
> DAXFlash - EMMC CID:        150100445636444142025c10dc0d291f
> DAXFlash - EMMC Boot1 Size: 0x400000
> DAXFlash - EMMC Boot2 Size: 0x400000
> DAXFlash - EMMC GP1 Size:   0x0
> DAXFlash - EMMC GP2 Size:   0x0
> DAXFlash - EMMC GP3 Size:   0x0
> DAXFlash - EMMC GP4 Size:   0x0
> DAXFlash - EMMC RPMB Size:  0x1000000
> DAXFlash - EMMC USER Size:  0x1d1ec00000
> DAXFlash - HW-CODE         : 0x766
> DAXFlash - HWSUB-CODE      : 0x8A00
> DAXFlash - HW-VERSION      : 0xCA00
> DAXFlash - SW-VERSION      : 0x0
> DAXFlash - CHIP-EVOLUTION  : 0x0
> DAXFlash - DA-VERSION      : 1.0
> DAXFlash - Extensions were accepted. Jumping to extensions...
> DAXFlash - DA Extensions successfully added
> DA\_handler - Requesting available partitions ....
> DA\_handler - Dumping partition "frp"
> Progress: |██████████████████████████████████████████████████| 100.0% Read (Sector 0x800 of 0x800, ) 3.61 MB/s
> DA\_handler - Dumped sector 44096 with sector count 2048 as frp.bin.
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 took 23s
> ❯ fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ cd ..
> r1\_escape on  main via 🐍 v3.13.2
> ❯ ls
> mtkbootcmd.py  mtkclient  r1.ps1  r1.sh  README.md  vbmeta.img
> r1\_escape on  main via 🐍 v3.13.2
> ❯ cat r1.sh
> \#!/bin/bash
>
> install\_debian() {
> sudo apt update
> [[ -x "$(command -v git)" ]] || sudo apt install -y git
> [[ -x "$(command -v python3)" ]] || sudo apt install -y python3
> [[ -x "$(command -v pip3)" ]] || sudo apt install -y python3-pip
> [[ -x "$(command -v dos2unix)" ]] || sudo apt install -y dos2unix
> [[ -x "$(command -v curl)" ]] || sudo apt install -y curl
> [[ -x "$(command -v unzip)" ]] || sudo apt install -y unzip
> }
>
> install\_arch() {
> sudo pacman -Sy --noconfirm
> [[ -x "$(command -v git)" ]] || sudo pacman -S --noconfirm git
> [[ -x "$(command -v python3)" ]] || sudo pacman -S --noconfirm python
> [[ -x "$(command -v dos2unix)" ]] || sudo pacman -S --noconfirm dos2unix
> [[ -x "$(command -v curl)" ]] || sudo pacman -S --noconfirm curl
> [[ -x "$(command -v unzip)" ]] || sudo pacman -S --noconfirm unzip
> [[ -x "$(command -v virtualenv)" ]] || sudo pacman -S --noconfirm python-virtualenv
> }
>
> install\_fedora() {
> sudo dnf update -y
> [[ -x "$(command -v git)" ]] || sudo dnf install -y git
> [[ -x "$(command -v python3)" ]] || sudo dnf install -y python3
> [[ -x "$(command -v pip3)" ]] || sudo dnf install -y python3-pip
> [[ -x "$(command -v dos2unix)" ]] || sudo dnf install -y dos2unix
> [[ -x "$(command -v curl)" ]] || sudo dnf install -y curl
> [[ -x "$(command -v unzip)" ]] || sudo dnf install -y unzip
> }
>
> if [[ "$OSTYPE" == "linux-gnu"\* ]]; then
> if command -v apt-get &>/dev/null; then
> install\_debian
> elif command -v pacman &>/dev/null; then
> install\_arch
> elif command -v dnf &>/dev/null; then
> install\_fedora
> else
> echo "Unsupported Linux distribution"
> exit 1
> fi
> else
> echo "Unsupported OS"
> exit 1
> fi
>
> if [[ "$OSTYPE" != "linux-gnu"\* || ! "$(command -v pacman)" ]]; then
> pip3 show virtualenv &>/dev/null || pip3 install virtualenv
> fi
>
> if [[ "$OSTYPE" == "linux-gnu"\* ]]; then
> if command -v apt-get &>/dev/null; then
> sudo apt install -y adb fastboot
> elif command -v pacman &>/dev/null; then
> sudo pacman -S --noconfirm android-tools
> elif command -v dnf &>/dev/null; then
> sudo dnf install -y android-tools
> fi
> fi
>
> # Setup virtualenv and install requirements
>
> python3 -m venv venv
> source venv/bin/activate
>
> chmod +x mtkbootcmd.py
>
> # Download mtkclient
>
> REPO\_URL="https\://github.com/AgentFabulous/mtkclient"
> REPO\_NAME=$(basename "$REPO\_URL" .git)
> git clone "$REPO\_URL"
> cd "$REPO\_NAME" || exit
> pip3 install -r requirements.txt
>
> rm -f frp.bin
>
> read -p "[\*] Power off your device, press ENTER plug it into your PC"
>
> # Read FRP
>
> sudo python3 mtk r frp frp.bin
>
> sudo chown $USER frp.bin
>
> LAST\_BYTE=$(xxd -p -l 1 -s -1 frp.bin)
> if [[ "$LAST\_BYTE" == "00" ]]; then
> printf '\x01' | dd of=frp.bin bs=1 seek=$(($(stat -c%s frp.bin) - 1)) conv=notrunc
> fi
>
> # Write FRP
>
> sudo python3 mtk w frp frp.bin
>
> read -p "[\*] Unplug your device, press ENTER, plug it back in"
>
> cd ..
>
> sudo ./mtkbootcmd.py FASTBOOT
>
> echo "[\*] Waiting for fastboot..."
> while ! fastboot devices | grep -q "fastboot"; do
> sleep 1
> done
>
> fastboot flashing unlock
> fastboot -w
> fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img
> fastboot reboot-fastboot
> fastboot flash system system.img
> fastboot reboot
> r1\_escape on  main via 🐍 v3.13.2
> ❯ cd mtkclient
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ LAST\_BYTE=$(xxd -p -l 1 -s -1 frp.bin)
> if [[ "$LAST\_BYTE" == "00" ]]; then
> printf '\x01' | dd of=frp.bin bs=1 seek=$(($(stat -c%s frp.bin) - 1)) conv=notrunc
> fi
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯  python3 mtk w frp frp.bin
> MTK Flash/Exploit Client Public V2.0.0 Beta (c) B.Kerler 2018-2023
>
> DAXFlash - HW-CODE         : 0x766
> DAXFlash - HWSUB-CODE      : 0x8A00
> DAXFlash - HW-VERSION      : 0xCA00
> DAXFlash - SW-VERSION      : 0x0
> DAXFlash - CHIP-EVOLUTION  : 0x0
> DAXFlash - DA-VERSION      : 1.0
> Progress: |██████████████████████████████████████████████████| 100.0% Write (Sector 0x800 of 0x800, ) 3.02 MB/s
> Wrote frp.bin to sector 44096 with sector count 2048.
> mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2
> ❯ cd ..
> r1\_escape on  main via 🐍 v3.13.2
> ❯ ./mtkbootcmd.py FASTBOOT
> Listening for ports!
> Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface
> HWID: USB VID\:PID=0E8D:2000 LOCATION=3-1:1.0
> Got port: /dev/ttyACM0
> Initializing port /dev/ttyACM0
> b'FASTBOOT' cmd sent
> r1\_escape on  main via 🐍 v3.13.2 took 9s
> ❯ fastboot flashing unlock
> (bootloader) Start unlock flow
>
> OKAY [  3.033s]
> Finished. Total time: 3.033s
> r1\_escape on  main via 🐍 v3.13.2 took 3s
> ❯ fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img
> Rewriting vbmeta struct at offset: 0
> Sending 'vbmeta\_a' (4 KB)                          OKAY [  0.005s]
> Writing 'vbmeta\_a'                                 OKAY [  0.002s]
> Finished. Total time: 0.008s
> r1\_escape on  main via 🐍 v3.13.2
> ❯ fastboot reboot-fastboot
> Rebooting into fastboot                            OKAY [  0.001s]
> < waiting for any device >
> ^[[A^C
> r1\_escape on  main via 🐍 v3.13.2 took 37s
> ❯ fastboot -w
> < waiting for any device >
> ^C
> r1\_escape on  main via 🐍 v3.13.2 took 4s
> ❯ ./mtkbootcmd.py FASTBOOT
> Listening for ports!
> Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface
> HWID: USB VID\:PID=0E8D:2000 LOCATION=3-1:1.0
> Got port: /dev/ttyACM0
> Initializing port /dev/ttyACM0
> b'FASTBOOT' cmd sent
> r1\_escape on  main via 🐍 v3.13.2 took 11s
> ❯ fastboot -w
> Erasing 'userdata'                                 OKAY [  0.320s]
> /usr/lib/android-sdk/platform-tools/mke2fs failed with status 1
> fastboot: error: Cannot generate image for userdata
> r1\_escape on  main via 🐍 v3.13.2
> ❯ fastboot flashing unlock
> (bootloader) Start unlock flow
>
> OKAY [  3.033s]
> Finished. Total time: 3.033s
> r1\_escape on  main via 🐍 v3.13.2 took 3s
> ❯ fastboot -w
> Erasing 'userdata'                                 OKAY [  0.319s]
> /usr/lib/android-sdk/platform-tools/mke2fs failed with status 1
> fastboot: error: Cannot generate image for userdata
> r1\_escape on  main via 🐍 v3.13.2
> ❯ fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img
> Rewriting vbmeta struct at offset: 0
> Sending 'vbmeta\_a' (4 KB)                          OKAY [  0.005s]
> Writing 'vbmeta\_a'                                 OKAY [  0.002s]
> Finished. Total time: 0.009s
> r1\_escape on  main via 🐍 v3.13.2
> ❯ fastboot reboot-fastboot
> Rebooting into fastboot                            OKAY [  0.001s]
> < waiting for any device >
> pwd^C
> r1\_escape on  main via 🐍 v3.13.2 took 3m
> ❯ pwd
> /home/manuel/code/others/rabbit-r1/r1\_escape
> r1\_escape on  main via 🐍 v3.13.2
>
>
>
> \----

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

I’ll trace your boot-chain failure, verify the Rabbit R1 and Ubuntu Touch porting landscape, then produce a cited textbook-style Markdown document and matching PDF covering recovery and porting paths.

<details><summary>💭 Thinking</summary>

**Planning the research**

I’m checking the linked documentation and current Ubuntu Touch porting guidance to assess feasibility. I’ll distinguish between a ready-made port, a generic-image workaround, and the substantial device-porting work that may be required.

**Planned the research**

**Read PDF skill creation and conversion instructions**

</details>

```json
{"open":[{"ref_id":"https://github.com/jonathanprocter/rabbit-r1-deverity-recovery/blob/main/docs/rabbit-r1-de-verity-recovery-community-writeup.md"},{"ref_id":"https://github.com/RabbitHoleEscapeR1/r1_escape"},{"ref_id":"https://github.com/rabbit-hmi-oss/firmware/releases"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```json
{"find":[{"ref_id":"turn851974view1","pattern":"README"},{"ref_id":"turn851974view1","pattern":"FRP"},{"ref_id":"turn851974view1","pattern":"system.img"},{"ref_id":"turn851974view2","pattern":"v0.8.293"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Searched Rabbit R1 Ubuntu Touch repositories**

</details>

```json
{"search_query":[{"q":"\"rabbit r1\" \"Ubuntu Touch\""},{"q":"\"rabbit-r1\" halium"},{"q":"\"rabbit r1\" ubports"},{"q":"site:github.com \"rabbit-r1\" linux kernel MT6765"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Tracing the device state**

I’m reconstructing the flashing sequence: bootloader unlocking succeeded, userdata was erased without formatting, verification metadata was modified, and stock boot images were restored. I’m checking whether the remaining failure comes from partition state, rollback protection, or filesystem setup.

**Traced the device state**

</details>

Your unlock bypass succeeded; the immediate task is restoring a coherent A/B boot chain. I’m also resolving conflicting findings about whether Rabbit R1 already has ready-made Ubuntu Touch support.

The safest path uses the R1-specific UBports bootstrap to flash `super.img` from bootloader fastboot, avoiding fastbootd. Your `fastboot -w` failure occurred after userdata was erased.

<details><summary>💭 Thinking</summary>

**Searched 13 websites**

</details>

```json
{"click":[{"ref_id":"turn299912view0","id":115},{"ref_id":"turn299912view0","id":116},{"ref_id":"turn299912view0","id":118},{"ref_id":"turn299912view0","id":136}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Assessing the installation path**

I’m comparing the installer’s expected starting point with the current state. Because it replaces the core boot, verification, and system images, restoring Android first may be unnecessary, though the persistent verification error still needs consideration.

**Assessed the installation path**

**Validating verification behavior**

I’m checking official Android documentation on verified boot, dm-verity, dynamic partitions, and slot handling. I’m also comparing those principles with the installer configuration before explaining why the current error may persist.

**Validated verification behavior**

</details>

```json
{"open":[{"ref_id":"https://rabbit-hmi-oss.github.io/flashing/"},{"ref_id":"https://github.com/rabbit-hmi-oss/firmware"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc rm -rf /tmp/r1-ut-port /tmp/r1-kernel /tmp/installer-configs && git clone --depth 1 https://gitlab.com/ubports/porting/community-ports/android12/rabbit-r1/rabbit-r1.git /tmp/r1-ut-port && git clone --depth 1 https://github.com/ubports/installer-configs.git /tmp/installer-configs && find /tmp/r1-ut-port -maxdepth 3 -type f | sort | sed -n '1,120p'
```

<details><summary>💭 Thinking</summary>

**Cloned Rabbit R1 porting repositories**

</details>

```json
{"search_query":[{"q":"site:gitlab.com/ubports/porting/community-ports/android12/rabbit-r1/rabbit-r1/-/blob deviceinfo"},{"q":"site:gitlab.com/ubports/porting/community-ports/android12/rabbit-r1/rabbit-r1/-/blob README"},{"q":"site:gitlab.com/ubports/porting/community-ports/android12/rabbit-r1/rabbit-r1/-/tree main"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Mapping the Ubuntu Touch route**

I’m comparing the device’s current state with the official Rabbit R1 Ubuntu Touch installer. The supported path appears to require stock rabbitOS v0.8, an unlocked bootloader, and a clean installer-driven wipe.

**Documenting the recovery path**

I’m assembling the final guide around the official installer, the device’s verified-boot state, and the community-identified persistent metadata issue. I’ll clearly separate confirmed facts from diagnoses and provide a cautious recovery sequence with references.

**Mapped the Ubuntu Touch route and documented recovery path**

**Searched 1 website**

</details>

```json
{"search_query":[{"q":"site:ubports.com/blog rabbit r1 Ubuntu Touch 24.04-2.0 release August 2026"},{"q":"site:devices.ubuntu-touch.io/device/r1 Rabbit R1 Ubuntu Touch installer"},{"q":"site:docs.ubports.com UBports Installer Rabbit R1 bootloader unlock stock rabbitOS v0.8"},{"q":"site:github.com/ubports/installer-configs r1.yml rabbit r1"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

```unknown
bash -lc sed -n '1,240p' /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Read PDF guidelines and inspected creation instructions**

</details>

```json
{"open":[{"ref_id":"turn529907view1","lineno":188},{"ref_id":"turn529907view1","lineno":235},{"ref_id":"turn529907view1","lineno":263},{"ref_id":"turn529907view1","lineno":308},{"ref_id":"turn529907view1","lineno":344},{"ref_id":"turn529907view1","lineno":415},{"ref_id":"turn529907view1","lineno":451},{"ref_id":"turn529907view1","lineno":556},{"ref_id":"turn529907view2","lineno":164},{"ref_id":"turn529907view2","lineno":200},{"ref_id":"turn529907view3","lineno":195},{"ref_id":"turn529907view4","lineno":182},{"ref_id":"turn529907view5","lineno":188},{"ref_id":"turn529907view6","lineno":255},{"ref_id
```

<details><summary>💭 Thinking</summary>

**Searched 5 websites**

</details>

```unknown
bash -lc command -v pandoc; command -v xelatex; command -v dot; command -v pdftoppm; python - <<'PY'
import reportlab, PIL
print('reportlab', reportlab.Version)
print('PIL ok')
PY
```

<details><summary>💭 Thinking</summary>

**Checked document conversion tools and PDF script options**

</details>

```json
{"open":[{"ref_id":"turn529907view10","lineno":174},{"ref_id":"turn529907view10","lineno":230},{"ref_id":"turn529907view10","lineno":265}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc set -euo pipefail
WORK=/mnt/data/_rabbit_r1_work
OUT=/mnt/data
rm -rf "$WORK"
mkdir -p "$WORK"
cat > "$WORK/header.tex" <<'EOF'
\usepackage{fontspec}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{tcolorbox}
\usepackage{fancyhdr}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{enumitem}
\usepackage{listings}
\usepackage{needspace}
\usepackage{titlesec}
\usepackage{etoolbox}
\setmainfont{TeX Gyre Pagella}
\setsansfont{TeX Gyre Heros}
\setmonofont{DejaVu Sans Mono}[Scale=0.82]
\definecolor{R1Orange}{HTML}{C4551A}
\definecolor{R1Blue}{HTML}{1F4E79}
\definecolor{R1Gray}{HTML}{F2F3F5}
\definecolor{R1DarkGray}{HTML}{444444}
\hypersetup{
  colorlinks=true,
  linkcolor=R1Blue,
  urlcolor=R1Blue,
  citecolor=R1Blue,
  pdfauthor={OpenAI},
  pdftitle={Rabbit R1 Boot Integrity, Recovery, and Ubuntu Touch}
}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small Rabbit R1 Boot Integrity and Ubuntu Touch}
\fancyhead[R]{\small\nouppercase{\leftmark}}
\fancyfoot[C]{\thepage}
\setlength{\headheight}{14pt}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}
\setlist{itemsep=0.25em, topsep=0.35em, parsep=0em}
\setlist[enumerate]{leftmargin=*}
\setlist[itemize]{leftmargin=*}
\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  breakatwhitespace=false,
  columns=fullflexible,
  keepspaces=true,
  frame=single,
  framerule=0.3pt,
  backgroundcolor=\color{R1Gray},
  rulecolor=\color{R1DarkGray},
  xleftmargin=0.5em,
  xrightmargin=0.5em,
  aboveskip=0.8em,
  belowskip=0.8em,
  showstringspaces=false
}
\renewenvironment{quote}
  {\begin{tcolorbox}[breakable,colback=R1Gray,colframe=R1Blue,boxrule=0.6pt,arc=1.5mm,left=2mm,right=2mm,top=1.5mm,bottom=1.5mm]}
  {\end{tcolorbox}}
\titleformat{\chapter}[display]
  {\normalfont\bfseries\color{R1Blue}}
  {\filleft\Large\chaptertitlename\ \thechapter}
  {1ex}
  {\titlerule\vspace{1ex}\Huge}
\titleformat{\section}
  {\needspace{4\baselineskip}\Large\bfseries\color{R1Blue}}
  {\thesection}{0.7em}{}
\titleformat{\subsection}
  {\needspace{3\baselineskip}\large\bfseries\color{R1DarkGray}}
  {\thesubsection}{0.7em}{}
\AtBeginEnvironment{longtable}{\small}
EOF

cat > "$WORK/rabbit-r1-boot-integrity-and-ubuntu-touch.md" <<'EOF'
---
title: "Rabbit R1 Boot Integrity, Recovery, and Ubuntu Touch"
subtitle: "A practical textbook for MediaTek preloader mode, fastboot, A/B slots, Android Verified Boot, dm-verity, stock recovery, and the UBports installer"
author: "Prepared from the supplied Rabbit R1 terminal transcript"
date: "Research snapshot: 2026-08-07"
lang: en-US
documentclass: scrreprt
classoption:
  - 11pt
  - oneside
  - open=any
papersize: letter
geometry:
  - top=0.80in
  - bottom=0.78in
  - left=0.82in
  - right=0.82in
toc: true
toc-depth: 3
numbersections: true
link-citations: true
---

# Preface {-}

This book explains the boot failure shown in the supplied terminal transcript and gives a controlled route from that state to Ubuntu Touch on a Rabbit R1. It is written for a Linux host and assumes comfort with a terminal, USB device modes, hashes, and destructive storage operations.

> **Risk notice.** Unlocking and flashing erase user data. Raw MediaTek writes can permanently damage boot, radio calibration, or device identity data. The conservative order is: collect evidence, preserve backups, restore a matched stock image set, verify slot state, and only then consider the `seccfg` procedure. Never relock the bootloader while modified or verification-disabled images are installed.

The document distinguishes three very different problems that can produce similar screens:

1. a mismatched set of `boot`, `vbmeta`, and `super` images;
2. A/B metadata that has marked one or both slots unbootable; and
3. a persistent MediaTek bootloader dm-verity state stored outside the ordinary Android images.

The official Rabbit flash tool and the official UBports Installer should be preferred over manual partition-by-partition flashing. The community `seccfg` method is a last-resort recovery technique, not a routine Ubuntu Touch installation step.[^recovery-warning]

## How to use this book {-}

Read Chapter 1 first. It gives the shortest safe path for the specific device state in the transcript. Chapters 2 through 8 explain the architecture and reconstruct what each command did. Chapters 9 through 14 are the recovery and installation runbook. The appendices provide compact command sheets, an error dictionary, and source notes.

Identifiers from the supplied log, including the fastboot serial, Bluetooth address, ME ID, and SoC ID, are intentionally omitted. Device owners should redact those values before posting logs publicly.

# The one-page answer

## What happened

The unlock bypass worked. At first, fastboot rejected writes because the device was locked and reported `unlock_ability = 0`. The `r1_escape` process then used `mtkclient` to read the `frp` partition, changed the script-selected byte, wrote the partition back, and returned to fastboot. After that, `fastboot flashing unlock` completed successfully. The later successful writes to `boot_a`, `boot_b`, and the vbmeta partitions confirm that the bootloader was no longer rejecting flashes.

The intended `r1_escape` installation did **not** complete. That project expects a separately downloaded Android GSI named `system.img`; your `find . -name system.img` returned nothing. The stock Rabbit firmware contains `super.img`, not a standalone `system.img`, because modern Android stores `system`, `vendor`, `product`, and related logical partitions inside the physical `super` partition. The script therefore stopped after unlock, data erasure, and vbmeta modification, leaving no complete replacement operating system.[^r1escape][^dynamic]

You then restored stock `boot.img` to both A/B slots and flashed stock vbmeta-family files with `--disable-verity --disable-verification`. That is not a fully stock verified-boot state: the image payload came from stock, but fastboot rewrote its verification flags. Repeated boot attempts and slot changes may also have consumed A/B retries. The red `dm-verity corruption` screen means that the bootloader is entering AVB's `eio` error mode; an orange warning alone merely means the bootloader is unlocked.[^bootflow]

## The recommended route from here

1. **Stop relocking and stop mixing individual images.** Keep the bootloader unlocked.
2. **Record the current fastboot variables and back up critical MediaTek partitions.** At minimum, preserve `seccfg` and `frp`; preserve radio/calibration partitions if they exist in the GPT, but never erase or rewrite them casually.
3. **Restore one coherent stock rabbitOS v0.8.293 set using Rabbit's official WebUSB flash tool.** Do not add disable-verification flags to the stock restore. Do not relock afterward.[^rabbitflash]
4. **Check and normalize A/B slot metadata.** Select slot A and confirm that it is not marked unbootable. Use the Rabbit-specific `boot_para`/`para` reset only if a full matched stock flash still leaves bad slot metadata.
5. **Boot stock once.** If stock reaches setup, the persistent verity state is clear. Return to fastboot and run the UBports Installer.
6. **If a full stock restore still gives the same red dm-verity screen, treat `seccfg` as the remaining suspect.** Follow the community procedure only after backing up the original partition and verifying the generated V4 header. The corrected state described in that recovery has `lock_state = 3`, the word at offset `0x10` set to `0`, and the managed-verity record at `0x240:0x2c0` cleared.[^seccfg]
7. **Install Ubuntu Touch with the official UBports Installer.** Select Rabbit R1, enable **Bootstrap**, enable **Wipe Userdata**, and choose the stable channel currently offered by the installer. The installer downloads checksummed `boot.img`, `super.img`, and `vbmeta.img`, flashes them from bootloader fastboot, formats `userdata`, enters UBports recovery, and installs the system image. It does not require your broken `fastbootd` transition.[^installer-config]
8. **Leave the bootloader unlocked.** The orange warning on every boot is expected.

## What not to do next

- Do not run `fastboot flashing lock` or any OEM relock command.
- Do not keep reflashing `vbmeta` with different flag combinations.
- Do not erase `nvram`, `nvdata`, `proinfo`, `protect1`, `protect2`, or calibration partitions.
- Do not assume `fastboot -w` failed completely: your log shows `userdata` was erased before the host-side formatter failed.
- Do not chase a missing stock `system.img`; stock logical partitions are inside `super.img`.
- Do not keep multiple serial watchers or `mtkclient` sessions open while the device is changing USB modes.

# Part I - The system you are modifying

# The Rabbit R1 boot chain

## A layered boot, not one program

The Rabbit R1 uses a MediaTek MT6765-family platform. Several independent components run before Android or Ubuntu Touch appears:

```text
Power-on or USB reset
        |
        v
+-------------------------+
| Boot ROM (BROM)         |  Immutable code in the SoC
+-------------------------+
        |
        v
+-------------------------+
| MediaTek preloader      |  Initializes memory and USB
| USB 0e8d:2000           |  CDC ACM serial in your log
+-------------------------+
        |
        | ASCII "FASTBOOT" or normal boot policy
        v
+-------------------------+
| LK / Android bootloader |  Lock state, slot selection,
|                         |  AVB policy, fastboot protocol
+-------------------------+
        |
        +---- selects slot A or B
        |
        v
+-------------------------+
| vbmeta chain            |  Signed hashes and hashtrees
+-------------------------+
        |
        v
+-------------------------+
| boot.img                |  Linux kernel + ramdisk
+-------------------------+
        |
        v
+-------------------------+
| first-stage init        |  Reads super metadata and
|                         |  creates logical partitions
+-------------------------+
        |
        v
+-------------------------+
| system/vendor/product   |  Android, Halium, or Ubuntu
| logical partitions      |  Touch userspace components
+-------------------------+
```

A failure at each layer looks different. `mtkbootcmd.py` only asks the preloader to enter bootloader fastboot. It does not unlock anything and it does not repair AVB. `mtkclient` works below fastboot and can access raw eMMC through MediaTek's Download Agent path. Fastboot works in LK and obeys LK's lock policy. Android Verified Boot begins when LK selects and verifies a boot slot.

## Why fastboot could be locked while mtkclient could write

The transcript shows `mtkclient` reporting that the target was unprotected and that memory read/write authentication was not required. That allowed a Download Agent to read and write the raw `frp` partition. Fastboot, however, initially returned `not allowed in locked state`. These statements are not contradictory: the two tools use different protocols at different layers.

A useful mental model is:

```text
mtkclient authority:  BROM/preloader/Download Agent -> raw storage
fastboot authority:   LK bootloader -> policy-controlled partitions
ADB authority:        running Android/Ubuntu userspace -> OS services
```

The fact that one path works says little about another path.

## Normal warning colors

Android's reference boot flow defines an orange warning for an unlocked device and a red `eio` warning for dm-verity corruption. An unlocked device can show orange and still boot normally. A red `eio` screen means the bootloader found an OS but is reporting a hashtree verification error mode to the kernel.[^bootflow]

Therefore:

- **Orange only:** expected after unlock and expected with Ubuntu Touch.
- **Red dm-verity corruption:** not merely an unlock warning; diagnose image consistency, slot state, and persistent managed-verity state.
- **No valid OS / signature error:** usually a more fundamental boot-chain or lock-state mismatch.

# Partitions, A/B slots, and `super`

## Physical partitions and logical partitions

Modern Android devices combine old-style physical GPT partitions with dynamic logical partitions.

```text
Physical GPT partitions (selected examples)

boot_a        boot_b        kernel and ramdisk for each slot
vbmeta_a      vbmeta_b      top-level AVB metadata
vbmeta_system_a/b           chained system AVB metadata
vbmeta_vendor_a/b           chained vendor AVB metadata
dtbo_a        dtbo_b        device-tree overlays
lk_a          lk_b          bootloader stage
tee_a         tee_b         trusted execution environment
super                        container for dynamic partitions
userdata                     mutable user data
metadata                     encryption/update metadata
frp                          factory reset / OEM-unlock policy data
seccfg                       MediaTek security state
nvram, nvdata, protect*      identity, radio, or calibration data
```

Inside `super`, Android creates logical devices such as:

```text
super
  +-- system_a / system_b
  +-- vendor_a / vendor_b
  +-- product_a / product_b
  +-- system_ext_a / system_ext_b
  +-- odm_a / odm_b, if used
```

The exact logical layout is stored in `super` metadata. This is why the Rabbit stock archive can contain one large `super.img` instead of separate `system.img`, `vendor.img`, and `product.img` files. A factory `super.img` bundles the logical-partition content and can be flashed directly to the physical `super` partition without entering fastbootd.[^dynamic]

## A/B boot slots

A/B devices maintain two bootable sets so an update can be written to the inactive slot and rolled back if it fails. The bootloader stores metadata for each slot:

- active/current slot;
- successful flag;
- unbootable flag;
- remaining retry count.

Fastboot defaults to the current slot when a partition name has an A/B suffix but the command omits it. This explains why your unsuffixed command first reported `Sending 'vbmeta_b'` and later reported `Sending 'vbmeta_a'`: the active slot had changed. The AOSP fastboot interface exposes `current-slot`, `slot-successful:<slot>`, `slot-unbootable:<slot>`, and `slot-retry-count:<slot>`; selecting a slot should clear its unbootable flag and reset retries.[^ab]

Repeated failed boots can exhaust retry counts. The bootloader then falls back to the other slot. If both slots are invalid or marked unbootable, the device may bounce between the logo, preloader enumeration, and power-off without ever starting a userspace that provides ADB or fastbootd.

## Why `boot_1` failed

Android slot suffixes are `_a` and `_b`, not `_1` and `_2`. The failure:

```text
Writing 'boot_1' FAILED (remote: 'This partition doesn't exist')
```

was literal. The correct names are `boot_a` and `boot_b`, which then flashed successfully.

# Android Verified Boot and dm-verity

## AVB is the signed manifest; dm-verity is the block checker

Android Verified Boot 2.0 uses signed vbmeta structures to describe what must be trusted. A top-level `vbmeta` image can contain hashes for small partitions and hashtree descriptors for large read-only filesystems. It can also delegate verification to chained metadata such as `vbmeta_system` and `vbmeta_vendor`. Android's reference AVB tooling can verify a signed vbmeta object, a boot hash, a system hashtree, and chained partition keys as one trust graph.[^avb]

`dm-verity` is the kernel device-mapper target that checks filesystem blocks against a Merkle hashtree while they are read. In simplified form:

```text
signed vbmeta
    |
    +-- hash(boot.img)
    +-- chain(vbmeta_system)
    |       +-- hashtree(system)
    |       +-- hashtree(product)
    +-- chain(vbmeta_vendor)
            +-- hashtree(vendor)
```

A complete image set must agree across this graph. Flashing a stock `boot.img` with a vbmeta generated for another build, or flashing a new `super.img` while leaving old chained metadata, can trigger verification errors even though every individual file is valid by itself.

## What the fastboot disable flags actually do

When used while flashing a vbmeta image:

```bash
fastboot --disable-verity --disable-verification flash vbmeta vbmeta.img
```

fastboot rewrites flags in the vbmeta structure before writing it. Conceptually:

- `--disable-verification` disables descriptor/signature enforcement for the chain rooted there;
- `--disable-verity` disables AVB hashtree enforcement.

These flags are development tools. They do not unlock the bootloader. They are meaningful for `flash vbmeta ...`, not for `fastboot flashing unlock`. The command:

```bash
fastboot flashing unlock --disable-verification
```

therefore does not make sense: unlock policy and vbmeta flags are separate mechanisms.

## Managed dm-verity and persistent EIO state

AVB supports a managed error mode that can persist state outside ordinary boot images. The reference implementation names its persistent value `avb.managed_verity_mode` and maps the managed restart/EIO mode to kernel parameters including `androidboot.veritymode=eio` and `androidboot.veritymode.managed=yes`.[^managed]

The Rabbit community recovery found an additional MediaTek-specific representation in `seccfg`: a V4 header word at offset `0x10` remained `1` while `lock_state` at `0x0c` was `3` (unlocked). LK treated this as a persistent dm-verity error state and regenerated the managed-verity record after ordinary reflashes. Clearing only Android images therefore did not clear the red screen.[^seccfg]

This is why a full stock reflash is the diagnostic boundary:

- If a matched stock set boots, the problem was image/slot consistency.
- If a matched stock set verifies but the bootloader still emits `veritymode=eio ... managed=yes`, investigate `seccfg`.

Do not jump directly to `seccfg` merely because the screen says dm-verity. Most dm-verity failures are fixed by restoring a coherent chain.

# USB modes and the tools that see them

## The four modes relevant here

| Mode | Typical host interface | Main tool | Purpose |
|---|---|---|---|
| BROM | MediaTek USB device | `mtkclient` | Earliest SoC recovery path |
| Preloader | `0e8d:2000`, CDC ACM, `/dev/ttyACM0` | `mtkbootcmd.py`, `mtkclient` | Initialize hardware; request fastboot or load DA |
| Bootloader fastboot | MediaTek fastboot USB PID | `fastboot` | Flash physical partitions, unlock, choose slot |
| OS/recovery userspace | ADB/MTP, or fastbootd | `adb`, UBports Installer, sometimes `fastboot` | Install system image, manipulate logical partitions |

The USB device disconnecting and reappearing is expected. Each transition changes USB descriptors and often the Linux driver binding.

## `cdc_acm` in your log

`mtkbootcmd.py` imports `pyserial`, waits for a MediaTek preloader CDC ACM port, opens `/dev/ttyACM0`, and writes `FASTBOOT`. The Linux `cdc_acm` driver is therefore required for that step. After the R1 re-enumerates as bootloader fastboot, the serial port disappears and `fastboot` uses a different USB interface. There is no benefit to repeatedly loading or unloading `cdc_acm` while the device is already in fastboot.

Some community Android instructions unload `cdc_acm` later to avoid a host-specific ADB binding conflict. Treat that as a mode-specific workaround, not as a universal requirement. For your immediate recovery, load it for the preloader-to-fastboot transition and leave module blacklisting alone until the operating system is booting.

## `fastboot` versus `fastbootd`

Bootloader fastboot runs in LK and can flash physical partitions such as `boot`, `vbmeta`, and a factory `super.img`. Fastbootd is a userspace implementation launched from recovery so it can understand and resize logical partitions inside `super`.

The `r1_escape` script wanted fastbootd because it intended to flash one logical `system` partition from a GSI. Your device disappeared after `fastboot reboot-fastboot`, likely because the current boot/recovery path could not keep fastbootd alive. That failure does not block the official Ubuntu Touch route: the Rabbit R1 installer configuration flashes a complete factory-style `super.img` directly from bootloader fastboot.[^installer-config]

# Part II - Reading your terminal transcript
EOF
```

<details><summary>💭 Thinking</summary>

**Formatted PDF header and appended forensic transcript reconstruction**

</details>

```unknown
bash -lc set -euo pipefail
DOC=/mnt/data/_rabbit_r1_work/rabbit-r1-boot-integrity-and-ubuntu-touch.md
cat >> "$DOC" <<'EOF'

# Ubuntu Touch, Halium, and the Rabbit port

## Ubuntu Touch is not desktop Ubuntu copied onto a phone

Ubuntu Touch combines several layers:

```text
+------------------------------------------------------+
| Lomiri shell, Ubuntu applications, system services   |
| Ubuntu Touch root filesystem                         |
+------------------------------------------------------+
| Halium adaptation layer                              |
| libhybris and Android-compatible hardware services   |
+------------------------------------------------------+
| Device-specific kernel, init, SELinux/AppArmor work  |
+------------------------------------------------------+
| Proprietary vendor blobs from the Android base       |
| GPU, camera, audio, modem, sensors, Wi-Fi, Bluetooth  |
+------------------------------------------------------+
| Rabbit R1 hardware                                   |
+------------------------------------------------------+
```

The Rabbit port is identified as `r1` and uses Halium 12.0. Halium provides a common adaptation surface so an Ubuntu userspace can use an Android-derived kernel and vendor interfaces. Porting is therefore not equivalent to booting a generic ARM64 Ubuntu root filesystem; the kernel, ramdisk, hardware services, vendor libraries, permissions, and display stack must match the device.[^halium]

## Why stock rabbitOS v0.8 is a prerequisite

The official Rabbit R1 Ubuntu Touch page requires:

1. the Rabbit R1 model;
2. stock rabbitOS v0.8 firmware;
3. an unlocked bootloader.[^ut-device]

The stock requirement supplies the expected non-`super` firmware and hardware interfaces: bootloader, modem firmware, trusted execution components, device-tree data, and other vendor-specific partitions. The Ubuntu Touch bootstrap replaces the main boot, vbmeta, and dynamic system image, but it does not reconstruct every low-level MediaTek partition from scratch.

This is why restoring a coherent v0.8.293 base before installation is more reliable than continuing from a partially modified Android state.

## Current support status and realistic expectations

At the research date, the official device page describes the port as booting and running well for advanced users and lists working camera, Wi-Fi, Bluetooth, audio, touchscreen, charging, sensors, and Waydroid support. USB MTP and ADB are marked partial. It also lists hardware limitations including no incoming/outgoing calls, no VoLTE, no NFC, no automatic brightness, no flashlight, and no wired external display.[^ut-features]

The channel information is in transition. The device page currently advertises Ubuntu Touch 20.04 OTA-12 as its stable channel, while UBports' official Ubuntu Touch 24.04-1.0 release announcement explicitly includes Rabbit R1, and the 24.04-2.0 test program also included it.[^ut-device][^ut-2404][^ut-24042]

For a fresh installation, the correct rule is:

> Select the **stable channel actually offered for Rabbit R1 by the current UBports Installer**. Do not manually force a daily, release-candidate, or development channel merely because a newer platform release exists.

Device-page and release metadata can lag one another. The installer queries the image service and is the operational source of truth for the available channel at install time.

## No supported dual boot

UBports explicitly discourages manual installation when an installer configuration exists and states that dual boot is not supported.[^ut-devices] Installing Ubuntu Touch should be treated as replacing the Android userspace on the active device, not adding a selectable second operating system.

# What the UBports Installer actually does

The Rabbit R1 installer configuration is unusually useful because it makes the bootstrap sequence explicit.[^installer-config]

## Device-specific button actions

The configuration defines:

- **Bootloader:** power off, move the scroll wheel up while pressing power; if a menu appears, select Fastboot.
- **Recovery:** power off, move the scroll wheel down while pressing power.

Your preloader serial method remains a valid recovery entrance when the button route is unreliable:

```bash
"$R1ESC/.venv/bin/python" "$R1ESC/mtkbootcmd.py" FASTBOOT
fastboot devices -l
```

## Installer prerequisites

The configuration asks the user to confirm stock rabbitOS v0.8 and an unlocked bootloader. It can invoke the standardized `fastboot flashing unlock` handler when it detects a locked bootloader, but in your case the unlock is already complete.

The installer requires a sufficiently recent installer application and exposes two important options:

- **Wipe Userdata:** required when switching from Android;
- **Bootstrap:** flash system partitions with fastboot; enabled by default.

For your device state, both should be enabled.

## Downloaded bootstrap images

The configuration downloads three checksum-pinned artifacts:

1. a Rabbit port `super.zip`, unpacked to `super.img`;
2. a Rabbit port `boot.img`;
3. a known `vbmeta.img` from Google's GSI resources.

The exact URLs and SHA-256 sums are maintained in the installer configuration. This is materially safer than manually mixing files found in multiple community guides.

## Flash order

The bootstrap sequence is:

```text
reboot or ask user to enter bootloader fastboot
        |
        v
flash vbmeta.img
        |
        v
flash boot.img
        |
        v
flash complete super.img
        |
        v
format userdata if Wipe Userdata is selected
        |
        v
reboot to UBports recovery
        |
        v
install the selected Ubuntu Touch system image
```

There is no `fastboot reboot-fastboot` step in this device configuration. The complete port `super.img` is flashed as a physical factory image from bootloader fastboot, which is consistent with Android's documented factory-image support for dynamic-partition devices.[^dynamic]

## Why this can repair an ordinary mismatch

A successful bootstrap writes a mutually intended trio:

- the port's kernel and ramdisk in `boot`;
- the port's AVB policy in `vbmeta`;
- the port's logical system/vendor/product layout in `super`.

That removes the most common source of dm-verity errors: a boot image from one build, metadata from another, and filesystems from a third. It cannot necessarily clear a MediaTek-specific persistent `seccfg` error state, which is why the stock-restore and `seccfg` decision gate remain relevant.

# Part IV - Recovery and installation runbook

# Safety preparation

## Stop conditions

Stop immediately and reassess if any of the following occurs:

- the firmware directory does not exactly match the expected Rabbit release;
- a command names a partition that is absent from `fastboot getvar all` or `mtkclient printgpt`;
- `fastboot` reports a locked state after you believed unlock succeeded;
- the device disconnects during a write and does not return to preloader or fastboot;
- a candidate `seccfg` image has a different size from the original partition dump;
- a `seccfg` candidate does not show the expected lock and verity fields before writing;
- the device begins booting while a low-level recovery script is still running.

Do not improvise around those conditions.

## Host checklist

Use a native x86-64 Linux host, a short data-capable USB cable, and a direct USB port. Avoid an unpowered hub. Charge the R1 before beginning. Close serial terminals, modem-manager probes, and duplicate `mtkclient` processes.

Install the host tools from the distribution or Google's current platform-tools package:

```bash
# Debian/Ubuntu example
sudo apt update
sudo apt install android-sdk-platform-tools-common adb fastboot \
                 python3-venv python3-pip git unzip e2fsprogs usbutils
```

Package names vary. The important binaries are:

```bash
command -v fastboot
command -v adb
command -v python3
fastboot --version
```

## Use one Python environment

```bash
R1ROOT="$HOME/code/others/rabbit-r1"
R1ESC="$R1ROOT/r1_escape"

cd "$R1ESC"
python3 -m venv .venv
"$R1ESC/.venv/bin/python" -m pip install --upgrade pip wheel
"$R1ESC/.venv/bin/python" -m pip install pyserial
"$R1ESC/.venv/bin/python" -m pip install -r "$R1ESC/mtkclient/requirements.txt"
```

Test imports explicitly:

```bash
"$R1ESC/.venv/bin/python" - <<'PY'
import serial
import usb.core
print("pyserial and pyusb are available")
PY
```

For `mtkclient`, prefer udev rules that allow normal-user USB access. If root is unavoidable, use the exact virtual-environment interpreter:

```bash
sudo "$R1ESC/.venv/bin/python" "$R1ESC/mtkclient/mtk" printgpt
```

Do not use bare `sudo python3`.

## Preserve the firmware archive and hashes

Your extracted stock directory is:

```text
rabbit_OS_v0.8.293_20250516110545/
```

Set a variable and inventory it:

```bash
FW="$R1ROOT/rabbit_OS_v0.8.293_20250516110545"

find "$FW" -maxdepth 1 -type f -printf '%f\n' | sort
sha256sum "$FW"/* > "$R1ROOT/rabbitOS-v0.8.293-files.sha256"
```

Keep the original ZIP as well. Do not rename files to satisfy a command copied from a different firmware package. For example, the community recovery writeup mentions `super_sparse_backup.img`, while your archive lists `super.img`. Use the official flasher, which reads the package's actual scatter and filenames, rather than substituting one for the other.

## Back up critical persistent partitions

This step uses raw MediaTek access and should be read-only. First print the partition table:

```bash
cd "$R1ESC/mtkclient"
sudo "$R1ESC/.venv/bin/python" ./mtk printgpt | tee "$R1ROOT/mtk-gpt.txt"
```

Only for partition names actually present, create a backup directory and read them one at a time:

```bash
mkdir -p "$R1ROOT/r1-backup"

sudo "$R1ESC/.venv/bin/python" ./mtk r seccfg \
  "$R1ROOT/r1-backup/seccfg-original.bin"

sudo "$R1ESC/.venv/bin/python" ./mtk r frp \
  "$R1ROOT/r1-backup/frp-current.bin"
```

If the GPT includes `nvram`, `nvdata`, `proinfo`, `protect1`, or `protect2`, preserve them as well, but do not erase or write them. Calculate hashes and make an offline copy:

```bash
sha256sum "$R1ROOT/r1-backup"/* > "$R1ROOT/r1-backup/SHA256SUMS"
```

The exact connection timing is the same as your successful FRP dump: start the read command, power the R1 off, and reconnect it in preloader/BROM mode when prompted.

## Enter bootloader fastboot cleanly

Use only one transition method at a time.

Button method:

```text
Power off -> scroll wheel up + power -> select Fastboot if prompted
```

Preloader serial method:

```bash
sudo modprobe cdc_acm
"$R1ESC/.venv/bin/python" "$R1ESC/mtkbootcmd.py" FASTBOOT
fastboot devices -l
```

Do not start another watcher after `fastboot devices` already lists the R1.

## Capture the preflight state

Run the diagnostic block from Chapter 8 and save it. Confirm at minimum:

```text
unlocked: yes                 or an equivalent true value
slot-count: 2
is-userspace: no              for bootloader fastboot
```

If fastboot still rejects writes as locked, do not proceed. Re-check the FRP backup and unlock state rather than flashing around the policy.

# Phase 1 - Restore a coherent stock base

## Preferred method: Rabbit's official WebUSB flash tool

Rabbit publishes an official browser-based flash tool and instructs users to download the latest firmware ZIP, enter preloader fastboot, select the fastboot device, and choose **Flash Stock ROM**.[^rabbitflash]

Use a Chromium-family browser with WebUSB support:

1. Keep the bootloader unlocked.
2. Open the official Rabbit R1 Flash Tool.
3. Power off and disconnect the R1.
4. Choose **Enter Fastboot Mode**.
5. Connect the R1 and quickly select the `MT65xx Preloader` device.
6. When the R1 displays fastboot, choose **Select Device in Fastboot**.
7. Select the extracted `rabbit_OS_v0.8.293_20250516110545` folder.
8. Choose **Flash Stock ROM** and allow the complete operation to finish.
9. Do **not** relock afterward.

This method is preferred because the tool and scatter file determine the intended partition set. It reduces the risk of omitting a boot-chain partition or applying flags intended for a GSI.

## What a stock restore should and should not do

A correct stock restore should write a matched set from one release, including the boot chain and `super`. It should use the stock vbmeta images without `--disable-verity` or `--disable-verification` rewriting.

It should not:

- erase identity/calibration partitions;
- relock the bootloader;
- use files from CipherOS, a GSI, or Ubuntu Touch in the same pass;
- substitute `preloader_raw.img` for another preloader format without knowing the official flasher's selection logic.

## Manual restore is a fallback, not the first choice

The community recovery describes a manual full pass that flashes the A-slot boot-chain set, a complete shared `super`, stock `userdata`, mirrors boot-chain images to B, and resets slot metadata.[^manual-stock] That sequence was written for a particular extracted package whose filenames differ from yours.

If the official tool cannot be used, derive the manual command list from **your** `MT6765_Android_scatter.xml` or `.txt`, not from filenames in another archive. At minimum:

- inspect every partition name and `is_download` setting;
- verify each file exists;
- use the stock vbmeta images without disable flags;
- flash the complete `super.img` to `super`, not to `system`;
- do not write a preloader image unless the exact storage type and format are confirmed.

A generic-looking command can still be wrong for a specific scatter. This is the point where using Rabbit's official tool is materially safer.

# Phase 2 - Normalize A/B state

## Inspect before erasing metadata

After the stock flash, re-enter bootloader fastboot and run:

```bash
for v in \
  current-slot \
  slot-successful:a slot-unbootable:a slot-retry-count:a \
  slot-successful:b slot-unbootable:b slot-retry-count:b; do
  fastboot getvar "$v"
done 2>&1 | tee "$R1ROOT/post-stock-slot-state.txt"
```

Then select A:

```bash
fastboot set_active a
fastboot reboot bootloader
```

Catch fastboot again and re-check the variables. AOSP specifies that selecting a slot should clear its unbootable flag and reset its retry count, although vendor implementations can have additional metadata behavior.[^ab]

## Rabbit-specific metadata reset

The community recovery found that the R1 sometimes needed:

```bash
fastboot erase boot_para
fastboot erase para
fastboot reboot bootloader
# Re-enter fastboot if necessary
fastboot set_active a
```

Treat this as a device-specific escalation, not a routine first command. Use it only after a complete stock image set is present and after saving the pre-reset slot variables. These partitions affect boot-control metadata; erasing them while images are still mismatched can make diagnosis harder.[^manual-stock]

## Attempt one stock boot

```bash
fastboot reboot
```

Expected outcomes:

- **Orange warning, then stock setup:** success. The bootloader is unlocked, but the stock chain is coherent.
- **Red warning that continues after a single side-button press:** capture the exact behavior. If stock then reaches setup, do not relock; the persistent warning state still deserves attention before changing OS.
- **Red warning followed by a loop or preloader re-enumeration:** proceed to the `seccfg` decision gate.
- **Signature/bad-state message:** the device is locked or the flashed vbmeta/boot chain is not truly stock. Return to fastboot and resolve that inconsistency first.

# Phase 3 - The `seccfg` decision gate

## Enter this phase only when all conditions are true

Do not modify `seccfg` unless:

1. the bootloader remains unlocked;
2. a complete, matched stock v0.8.293 set has just been flashed;
3. slot A has been selected and is not marked unbootable;
4. the same red dm-verity/EIO behavior persists;
5. the original `seccfg` has been dumped and hashed;
6. you can reproduce and inspect the community procedure against the exact `mtkclient` source revision you are using.

If any condition is false, go back rather than guessing.

## What the community recovery found

On the recovered device, the V4 `seccfg` header contained:

```text
offset 0x00  magic                  "MMMM"
offset 0x04  version                4
offset 0x08  size                   0x3c
offset 0x0c  lock_state             3  (unlocked)
offset 0x10  critical/dm-verity     1  (latched error)
offset 0x14  sboot_runtime          0
offset 0x18  end marker             "EEEE"
```

The recovery kept `lock_state = 3`, generated a valid authenticated V4 header with the offset `0x10` field set to `0`, and cleared the persistent managed-verity record at `0x240:0x2c0`. After that, the device booted.[^seccfg]

## Why a hex editor alone is unsafe

The V4 header includes authenticated/encrypted state. Directly changing byte `0x10` in an existing partition dump can invalidate the header integrity data. The community method patched `mtkclient`'s V4 `seccfg` generator so it produced a correctly authenticated unlocked header with the critical state set to zero. It then combined that generated header with the rest of the device's own full partition dump.

The safe invariant is:

```text
same device's full seccfg body
+ valid generated V4 header
+ lock_state still unlocked
+ critical/dm-verity state zero
+ managed-verity record zero
+ unchanged total partition size
```

## Required verification before any write

Inspect the backup first:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path("r1-backup/seccfg-original.bin")
b = p.read_bytes()
print("size:", len(b))
print("magic:", b[0:4])
print("version:", int.from_bytes(b[0x04:0x08], "little"))
print("header-size-field:", int.from_bytes(b[0x08:0x0c], "little"))
print("lock_state:", int.from_bytes(b[0x0c:0x10], "little"))
print("critical_or_verity:", int.from_bytes(b[0x10:0x14], "little"))
print("managed_record_nonzero:", any(b[0x240:0x2c0]))
PY
```

A candidate must be checked with the same script and with hashes:

```bash
sha256sum r1-backup/seccfg-original.bin candidate-seccfg.bin
cmp -l r1-backup/seccfg-original.bin candidate-seccfg.bin | head -100
```

Differences should be explainable by the generated header and the managed-record clearing. The candidate length must exactly equal the original length.

## Use the source procedure, not an abbreviated copy

The community writeup includes the two `mtkclient` patches, environment variables used to generate the 512-byte header, the merge script, expected field values, and the final write command.[^seccfg-procedure] Because those patches target code that can change between `mtkclient` revisions, this book intentionally does not present the raw write step as a blind copy-and-paste recipe.

When executing it:

- pin the repository commit;
- save `git diff` showing only the intended changes;
- generate the candidate before writing;
- verify `lock_state = 3`;
- verify the offset `0x10` value is `0`;
- verify the managed record is all zero;
- write once;
- stop all tools if the camera moves or the UI starts.

A late write error does not automatically mean the beginning of the partition was not written, but it is also not permission to retry repeatedly. Observe the device and compare a fresh read-back before another write.

# Phase 4 - Install Ubuntu Touch

## Establish the prerequisite state

The ideal starting point is:

```text
Bootloader: unlocked
Firmware base: complete stock rabbitOS v0.8.293
Active slot: A, bootable
Screen on stock boot: orange unlock warning only, then setup
USB: bootloader fastboot visible to normal user
Backups: seccfg, frp, and calibration partitions stored offline
```

If stock setup is not usable but a matched stock set is present and the red EIO state has been cleared, the installer may still succeed from bootloader fastboot. The critical requirement is a coherent low-level v0.8 base, not preserving Rabbit user data.

## Obtain and run the official installer

Download the Linux package linked from the official Rabbit R1 Ubuntu Touch device page. Use the current `.deb` or AppImage for x86-64. Run the application as your normal desktop user; UBports troubleshooting guidance generally expects normal-user USB access rather than launching the whole GUI with `sudo`.[^ut-install]

For an AppImage, the pattern is:

```bash
chmod +x ubports-installer-*.AppImage
./ubports-installer-*.AppImage
```

If the application cannot see fastboot, fix udev permissions rather than running an untrusted GUI as root. A quick distinction is:

```bash
fastboot devices -l
sudo fastboot devices -l
```

If only the second command sees the device, install appropriate Android udev rules, reconnect, and re-login or reload rules.

## Installer selections for this device

Choose:

```text
Device: rabbit r1 (codename r1)
Channel: stable, as offered by the installer
Wipe Userdata: enabled
Bootstrap: enabled
```

Confirm stock rabbitOS v0.8 and unlocked bootloader when prompted.

Do not choose:

- an unrelated generic Android device;
- a manual GSI image;
- `devel` or `rc` solely to obtain a larger version number;
- no-wipe when switching from Android;
- no-bootstrap while the existing boot/super/vbmeta state is damaged.

## During the bootstrap

Keep a separate terminal available for passive observation:

```bash
watch -n 0.5 'fastboot devices -l; adb devices -l'
```

Do not issue competing flash or reboot commands while the installer is active.

If the installer asks for bootloader mode:

```text
Power off -> scroll wheel up + power -> choose Fastboot
```

If that route fails and the installer is waiting, close any serial watchers and use the preloader command once, then return control to the installer.

The expected high-level progress is:

```text
download and verify artifacts
unpack super.zip
flash vbmeta
flash boot
flash super
format userdata
reboot recovery
push/install Ubuntu Touch image
reboot
```

A temporary USB disappearance between those stages is normal. A repeated red dm-verity screen immediately after the newly flashed Ubuntu boot chain is not normal and points back to an uncleared persistent state or an interrupted/mismatched bootstrap.

## First boot

An orange unlocked-bootloader warning is expected. Do not interpret it as a failed Ubuntu installation. Continue past it according to the on-screen prompt. The first system startup performs initialization that subsequent boots do not repeat; avoid power cycling merely because the screen pauses during that phase.

Leave the bootloader unlocked. Relocking would make the device demand a boot chain signed by the configured trusted key and can return it to a signature/bad-state failure.

# Phase 5 - Validate the installation

## Basic functional checks

After the Ubuntu Touch setup UI appears, check in this order:

1. touchscreen and rotation;
2. Wi-Fi association and DNS;
3. speaker, microphone, and volume keys;
4. charging and battery reporting;
5. camera photo/video and camera rotation;
6. Bluetooth;
7. mobile data or SMS only if a SIM is installed and the port's current status supports the intended function;
8. reboot and shutdown;
9. recovery entry;
10. system update channel.

Record the OS build shown in System Settings before changing channels.

## Expected limitations

Do not use a missing feature as evidence of a corrupt flash when the official device page marks it unsupported or partial. In particular, Rabbit R1 is not expected to provide conventional voice-call or VoLTE functionality under this port, and MTP/ADB may be partial. The device page classifies the port for advanced users rather than as a fully polished mainstream phone.[^ut-features]

## Preserve a recovery notebook

Save:

- Rabbit stock ZIP and its hash;
- extracted firmware hash list;
- original `seccfg` and FRP backups;
- the pre- and post-stock fastboot variable snapshots;
- UBports Installer log;
- installed Ubuntu Touch channel and build;
- any `mtkclient` commit hash and patches used.

This turns future recovery from guesswork into a reproducible state transition.

# Phase 6 - Return to stock if needed

## Preferred rollback

1. Back up Ubuntu Touch user data that can be exported.
2. Power off the R1.
3. Enter preloader fastboot using the official Rabbit tool or `mtkbootcmd.py`.
4. Use Rabbit's official flash tool with the complete v0.8.293 folder.
5. Select slot A if needed and boot stock.
6. Keep the bootloader unlocked until stock has booted successfully and all stock vbmeta images are confirmed.

Relocking is not required for stock to operate and should not be part of troubleshooting. Only consider it if Rabbit provides a documented, supported relock procedure for an entirely stock verified chain and you accept the possibility of another data wipe or boot failure.

## Why `gsi wipe` is not the rollback plan

The Ubuntu Touch installer flashes a complete port `super.img` and boot image, not merely a temporary GSI layer. Use the complete stock firmware restore rather than relying on `fastboot gsi wipe`, whose scope is limited to Android's GSI mechanisms.

# Part V - Diagnostic reasoning and field reference
EOF
```

<details><summary>💭 Thinking</summary>

**Appended Ubuntu Touch porting runbook**

</details>

```json
{"search_query":[{"q":"MinatiScape ubtouch-on-r1 GitHub README Rabbit R1 Ubuntu Touch"},{"q":"site:github.com/MinatiScape/ubtouch-on-r1 Rabbit R1 Ubuntu Touch v0.2"},{"q":"site:gitlab.com/ubports/porting/community-ports/android12/rabbit-r1 Ubuntu Touch Rabbit R1"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 5 websites**

</details>

```unknown
bash -lc set -euo pipefail
DOC=/mnt/data/_rabbit_r1_work/rabbit-r1-boot-integrity-and-ubuntu-touch.md
cat >> "$DOC" <<'EOF'

# The recovery decision tree

```text
START: R1 reaches preloader or bootloader fastboot
  |
  +-- Does `fastboot devices` list it?
  |      |
  |      +-- NO -> load cdc_acm, send FASTBOOT once, fix USB permissions
  |      |
  |      +-- YES
  |            |
  |            +-- Does fastboot permit partition writes?
  |                   |
  |                   +-- NO -> bootloader policy still locked
  |                   |         verify FRP/unlock flow; do not flash around it
  |                   |
  |                   +-- YES
  |                         |
  |                         +-- Backups and state snapshot complete?
  |                                |
  |                                +-- NO -> dump seccfg/FRP and record slots
  |                                |
  |                                +-- YES
  |                                      |
  |                                      +-- Full matched stock v0.8.293 flash
  |                                             |
  |                                             +-- Stock boots after orange warning
  |                                             |      |
  |                                             |      +-- Run UBports Installer
  |                                             |          Bootstrap + Wipe + stable
  |                                             |
  |                                             +-- Stock still red/loops
  |                                                    |
  |                                                    +-- Select/reset slot A
  |                                                    |
  |                                                    +-- Still red/loops?
  |                                                           |
  |                                                           +-- NO -> Installer
  |                                                           |
  |                                                           +-- YES -> seccfg gate
  |                                                                    backup, generate,
  |                                                                    inspect, write once
  |
  +-- Ubuntu bootstrap flashes boot/vbmeta/super successfully?
         |
         +-- NO -> preserve installer log; restore stock; fix USB/flash error
         |
         +-- YES
               |
               +-- UBports recovery starts?
                      |
                      +-- NO -> persistent boot state or interrupted bootstrap
                      |
                      +-- YES -> let system-image install finish
```

# May the installer be tried immediately?

Technically, a single direct UBports Installer attempt can repair an ordinary boot/vbmeta/super mismatch because its bootstrap overwrites those three components with a matched set. Your log also shows that the bootloader is unlocked and reachable.

However, the official Rabbit port requires a stock v0.8 firmware base, and your current state is only partly known. The conservative route is therefore to restore stock first. A direct attempt is reasonable only when all of these are true:

- the low-level partitions are already from v0.8.293;
- `fastboot` is unlocked and stable;
- critical persistent partitions have been backed up;
- no manual `seccfg` write has been made;
- you accept that a failed attempt may still require the full stock restore.

If you take the shortcut, select **Bootstrap** and **Wipe Userdata**. If the installer flashes its images but the same red EIO loop remains, stop after that one attempt. Repeatedly alternating stock and Ubuntu images will consume slot retries and obscure the persistent-state diagnosis.

# Installer-stage troubleshooting

| Installer stage | Symptom | Interpretation | Controlled response |
|---|---|---|---|
| Device detection | Installer sees no R1 | udev permissions or wrong USB mode | Verify `fastboot devices -l` as normal user; re-enter bootloader |
| Unlock check | Installer says locked | LK still reports locked | Stop; verify `fastboot getvar unlocked`; do not bypass with vbmeta flags |
| Download | Hash or network failure | Artifact was not verified | Retry download; do not use the partial file |
| Flash `vbmeta`/`boot` | `not allowed in locked state` | unlock was lost or misdetected | Return to unlock diagnosis |
| Flash `super` | transfer/write failure | cable, host USB, image, or eMMC problem | Save log; reconnect to bootloader; do not flash random logical partitions |
| Format `userdata` | format failure | host tooling or filesystem issue | Let installer retry once; use current platform-tools/e2fsprogs; avoid repeated `-w` |
| Reboot recovery | device returns to preloader | boot/recovery did not start | Re-enter bootloader, verify bootstrap completed, assess persistent EIO state |
| System image install | ADB/recovery lost | recovery USB or interrupted install | Re-enter UBports recovery with wheel down + power; preserve installer log |
| First Ubuntu boot | orange warning | unlocked bootloader | expected; continue |
| First Ubuntu boot | red dm-verity warning and loop | persistent EIO or interrupted/mismatched bootstrap | stock restore, slot check, `seccfg` gate |

# Why common alternative approaches fail

## Flashing only `boot.img`

`boot.img` supplies the kernel and ramdisk, but its AVB hash and its expected userspace must match vbmeta and `super`. A new boot image against an old system may fail before or during first-stage init.

## Flashing only `vbmeta.img`

A disabled vbmeta can suppress one layer of verification, but it does not install a compatible kernel or userspace. It can also leave chained vbmeta partitions or persistent managed-verity state unchanged.

## Flashing a GSI `system.img` without a stable fastbootd

A logical `system` image requires userspace fastboot or another tool that understands the dynamic layout. The R1 was not maintaining fastbootd in the shown state. The Ubuntu installer avoids this by flashing a complete `super.img`.

## Relocking to "make verification normal"

Relocking does not repair a modified chain. It changes policy from "modified images allowed" to "only an accepted signed chain may boot." If the current images are disabled, unsigned, or signed by a different key, relocking converts a recoverable warning state into a signature failure. The community recovery explicitly warns against relocking with disabled vbmeta installed.[^recovery-warning]

## Erasing everything MediaTek exposes

`mtkclient` can expose partitions that ordinary fastboot intentionally protects. Erasing `nvram`, `nvdata`, `proinfo`, `protect*`, RPMB-related data, or calibration partitions can destroy radio identity, camera tuning, sensor calibration, or factory provisioning. More access is not the same as more safety.

# Command semantics reference

## MediaTek and serial commands

### `python mtkbootcmd.py FASTBOOT`

Waits for the preloader CDC ACM interface and sends an ASCII boot command. It does not flash, unlock, or verify images.

### `mtk printgpt`

Reads the device's partition table through the MediaTek DA path. Use it to verify names and sizes before raw reads.

### `mtk r PARTITION FILE`

Reads one raw partition into a host file. Appropriate for backups when the partition name is verified.

### `mtk w PARTITION FILE`

Writes one raw partition. This bypasses much of fastboot's safety policy. Reserve it for a reviewed recovery procedure.

## Fastboot state commands

### `fastboot devices -l`

Lists bootloader-fastboot or fastbootd devices. An empty result says nothing about preloader/BROM mode.

### `fastboot getvar NAME`

Asks the current fastboot implementation for state. Output commonly goes to standard error.

### `fastboot flashing get_unlock_ability`

Reports whether the unlock operation may be initiated. It is not a universal substitute for `getvar unlocked` after unlock.

### `fastboot flashing unlock`

Starts the standardized unlock flow. It changes bootloader policy and generally wipes data. It does not by itself install an OS or rewrite vbmeta flags.

### `fastboot set_active a`

Selects slot A and should reset its A/B bootability metadata. Reboot the bootloader and re-check rather than trusting one line of output.

## Fastboot write commands

### `fastboot flash boot_a boot.img`

Writes the slot-A kernel/ramdisk image.

### `fastboot flash vbmeta_a vbmeta.img`

Writes the image exactly as supplied.

### `fastboot --disable-verity --disable-verification flash vbmeta_a vbmeta.img`

Rewrites vbmeta flags before writing. Use only when the intended installation specifically requires disabled verification and keep the device unlocked.

### `fastboot flash super super.img`

Writes a complete factory-style dynamic partition image to the physical `super` partition. This is different from `fastboot flash system system.img`.

### `fastboot format userdata`

Asks fastboot to create a filesystem on `userdata`. Host and device implementation details vary.

### `fastboot -w`

Composite wipe/format behavior. Read every line; an erase may succeed even if a later host-side format fails.

## Reboot commands

### `fastboot reboot`

Leaves fastboot and attempts normal boot.

### `fastboot reboot bootloader`

Restarts LK fastboot and is useful after changing slot metadata.

### `fastboot reboot-fastboot`

Requests userspace fastbootd. It depends on a viable recovery/boot path and is not required by the official Rabbit Ubuntu Touch installer.

# A compact command sheet for your next session

This sheet assumes the repositories and stock firmware are already present at the paths used in your transcript.

## 1. Set paths and environment

```bash
R1ROOT="$HOME/code/others/rabbit-r1"
R1ESC="$R1ROOT/r1_escape"
FW="$R1ROOT/rabbit_OS_v0.8.293_20250516110545"

cd "$R1ESC"
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/python -m pip install -U pip wheel
.venv/bin/python -m pip install pyserial
.venv/bin/python -m pip install -r mtkclient/requirements.txt
```

## 2. Back up persistent state

```bash
mkdir -p "$R1ROOT/r1-backup"
cd "$R1ESC/mtkclient"

sudo "$R1ESC/.venv/bin/python" ./mtk printgpt \
  | tee "$R1ROOT/mtk-gpt.txt"

sudo "$R1ESC/.venv/bin/python" ./mtk r seccfg \
  "$R1ROOT/r1-backup/seccfg-original.bin"

sudo "$R1ESC/.venv/bin/python" ./mtk r frp \
  "$R1ROOT/r1-backup/frp-current.bin"

sha256sum "$R1ROOT/r1-backup"/*.bin \
  > "$R1ROOT/r1-backup/SHA256SUMS"
```

Reconnect the R1 as directed for each preloader operation. Add other calibration partitions only after confirming their exact names in the GPT.

## 3. Enter bootloader fastboot and record state

```bash
sudo modprobe cdc_acm
"$R1ESC/.venv/bin/python" "$R1ESC/mtkbootcmd.py" FASTBOOT
fastboot devices -l

{
  fastboot getvar unlocked
  fastboot getvar current-slot
  fastboot getvar slot-successful:a
  fastboot getvar slot-unbootable:a
  fastboot getvar slot-retry-count:a
  fastboot getvar slot-successful:b
  fastboot getvar slot-unbootable:b
  fastboot getvar slot-retry-count:b
  fastboot getvar is-userspace
} > "$R1ROOT/pre-restore-fastboot.txt" 2>&1

cat "$R1ROOT/pre-restore-fastboot.txt"
```

## 4. Restore stock with the official Rabbit tool

Use the official browser flash tool and select:

```text
$FW
```

Do not append disable-verification flags and do not relock.

## 5. Select and inspect slot A

```bash
fastboot set_active a
fastboot reboot bootloader
# Re-enter fastboot if the USB device does not return automatically.

for v in current-slot \
         slot-successful:a slot-unbootable:a slot-retry-count:a \
         slot-successful:b slot-unbootable:b slot-retry-count:b; do
  fastboot getvar "$v"
done 2>&1 | tee "$R1ROOT/post-restore-slots.txt"
```

Only if full stock is present and metadata remains bad, apply the Rabbit-specific reset from the community recovery:

```bash
fastboot erase boot_para
fastboot erase para
fastboot reboot bootloader
# Re-enter fastboot
fastboot set_active a
```

## 6. Test stock

```bash
fastboot reboot
```

- Orange then setup: continue to installer.
- Red EIO and loop: use the `seccfg` gate; do not relock.

## 7. Run UBports Installer

```text
rabbit r1
stable channel offered by installer
Wipe Userdata = on
Bootstrap = on
```

Do not run competing fastboot commands during installation.

# Concept checks

## Why did `fastboot devices` initially show nothing even though `FASTBOOT` was sent?

Because the preloader serial write and bootloader USB enumeration are separate events. The command could be accepted while the device later failed to remain in fastboot, enumerated too briefly, or lacked host permissions.

## Why did changing FRP affect unlock ability?

On this Rabbit firmware, the community script uses a byte in FRP as the persistent OEM-unlock eligibility switch. The transcript's unlock behavior changed immediately after that write. This is device/build-specific and should not be generalized to every Android device.

## Why is a stock `super.img` not the same thing as the GSI's `system.img`?

`system.img` is one logical filesystem image. `super.img` is a physical container image that includes dynamic-partition metadata and multiple logical partitions. Flashing one where the other is expected changes both scope and target.

## Why can an unlocked device still show dm-verity corruption?

Unlocking permits modification; it does not guarantee that the selected images agree or clear every persistent error state. AVB/dm-verity policy and bootloader lock policy are related but distinct.

## Why restore stock before Ubuntu Touch if the installer overwrites the main images?

The port expects a particular low-level firmware base outside `boot`, `vbmeta`, and `super`. A stock restore also gives a diagnostic control: if stock cannot boot, the problem is below or outside the Ubuntu userspace image.

## Why leave the bootloader unlocked after Ubuntu Touch boots?

The Ubuntu Touch image is not the Rabbit factory signed chain expected by a stock locked bootloader. Relocking can make LK reject it before Linux starts.

# Glossary

**A/B device**  
A device with two boot slots so updates can be written to one while the other remains a fallback.

**ADB**  
Android Debug Bridge. A userspace protocol available only when a running OS or recovery exposes its daemon and authorizes the host.

**Android Verified Boot (AVB)**  
The signed metadata and verification framework used to authenticate the Android boot chain and read-only partitions.

**BROM**  
Boot ROM. Immutable first-stage code inside the MediaTek SoC.

**Bootstrap**  
In the UBports Installer, the fastboot phase that writes the device-specific boot, vbmeta, and system partition images needed to start UBports recovery.

**CDC ACM**  
A USB serial class used by the R1 preloader and exposed on Linux as `/dev/ttyACM*` through the `cdc_acm` driver.

**Chained vbmeta**  
An AVB arrangement where top-level vbmeta delegates verification of groups such as system or vendor to another signed vbmeta partition.

**Download Agent (DA)**  
MediaTek code uploaded through BROM/preloader to provide storage operations. `mtkclient` uses this path.

**dm-linear**  
Linux device-mapper target used to map extents inside `super` into logical partitions.

**dm-verity**  
Linux device-mapper target that verifies read-only blocks against a Merkle hashtree.

**EIO mode**  
An AVB hashtree error mode represented to Android as `androidboot.veritymode=eio`; the reference boot UI uses a red corruption warning for this state.

**fastboot**  
A flashing protocol. On the R1, bootloader fastboot runs in LK and obeys bootloader lock policy.

**fastbootd**  
Userspace fastboot, normally launched from recovery to manipulate dynamic logical partitions.

**FRP partition**  
Persistent Factory Reset Protection and policy storage. The `r1_escape` script modifies a byte here to enable the Rabbit unlock flow.

**GSI**  
Generic System Image. A generic Android `system.img` intended for Project Treble-compatible devices; it does not include all device-specific firmware.

**Halium**  
Compatibility and adaptation infrastructure that lets Ubuntu Touch use an Android-derived kernel and vendor hardware stack.

**LK**  
Little Kernel, commonly used as a MediaTek Android bootloader stage. It implements fastboot, slot selection, and AVB decisions on this device family.

**Logical partition**  
A virtual block device such as `system_a` whose extents are allocated inside `super`.

**Orange state**  
The expected warning state for an unlocked Android bootloader.

**Preloader**  
MediaTek's early boot stage loaded after BROM; it initializes memory and exposes transient USB protocols.

**`seccfg`**  
MediaTek security configuration storage. On the community-recovered Rabbit build, it held both lock state and a persistent dm-verity-related state.

**Slot metadata**  
Boot-control information recording active, successful, unbootable, and retry-count state for slots A and B.

**`super` partition**  
A physical dynamic-partition container holding system, vendor, product, and related logical images.

**vbmeta**  
The AVB metadata image containing signed descriptors, flags, hashes, hashtrees, or chained-partition information.

# Selected source notes

The most important operational sources are listed below. Access dates are 2026-08-07.

1. Android Open Source Project, [Boot flow](https://source.android.com/docs/security/features/verifiedboot/boot-flow).
2. Android Open Source Project, [Android Verified Boot](https://source.android.com/docs/security/features/verifiedboot/avb).
3. Android Open Source Project, [Device state](https://source.android.com/docs/security/features/verifiedboot/device-state).
4. Android Open Source Project, [Implement A/B updates](https://source.android.com/docs/core/ota/ab/ab_implement).
5. Android Open Source Project, [Implement dynamic partitions](https://source.android.com/docs/core/ota/dynamic_partitions/implement).
6. Android AVB source and README, [platform/external/avb](https://android.googlesource.com/platform/external/avb/).
7. UBports, [Rabbit R1 device page](https://devices.ubuntu-touch.io/device/r1/).
8. UBports, [Rabbit R1 installer configuration](https://github.com/ubports/installer-configs/blob/master/v2/devices/r1.yml).
9. UBports documentation, [Introduction to porting](https://docs.ubports.com/en/latest/porting/introduction/Intro.html).
10. Rabbit HMI OSS, [Rabbit R1 Flash Tool](https://rabbit-hmi-oss.github.io/flashing/).
11. Rabbit HMI OSS, [Firmware releases](https://github.com/rabbit-hmi-oss/firmware/releases).
12. RabbitHoleEscapeR1, [`r1_escape`](https://github.com/RabbitHoleEscapeR1/r1_escape).
13. Jonathan Procter, [Rabbit R1 dm-verity recovery community writeup](https://github.com/jonathanprocter/rabbit-r1-deverity-recovery/blob/main/docs/rabbit-r1-de-verity-recovery-community-writeup.md).
14. UBports, [Ubuntu Touch 24.04-1.0 release](https://ubports.com/blog/ubports-news-1/ubuntu-touch-24-04-1-0-release-3973).
15. UBports, [Ubuntu Touch 24.04-2.0 beta announcement](https://ubports.com/blog/ubports-news-1/ubuntu-touch-24-04-2-0-beta-is-now-ready-for-testing-4000).

# Footnotes {-}

[^recovery-warning]: The community recovery explicitly recommends official Rabbit tools first, describes raw `seccfg` work as a last resort, and warns not to relock with disabled vbmeta installed. See source note 13.

[^r1escape]: The `r1_escape` README states that its script enables OEM unlocking, unlocks the bootloader, disables AVB, and flashes an AOSP 13 userdebug GSI. Its script expects a separately provided `system.img`. See source note 12.

[^dynamic]: AOSP documents that `super` contains dynamic-partition metadata and logical partitions, and that a factory `super.img` bundles system/vendor/etc. and may be flashed directly without fastbootd. See source note 5.

[^bootflow]: AOSP's reference boot flow defines orange for unlocked devices and red `eio` for dm-verity corruption. See source note 1.

[^rabbitflash]: Rabbit's official WebUSB tool instructs users to download the firmware release, enter preloader fastboot, select the fastboot device, and flash the stock ROM folder. See source notes 10 and 11.

[^seccfg]: The community recovery reports a Rabbit-specific persistent dm-verity state in V4 `seccfg`, with lock state at `0x0c`, a critical/dm-verity field at `0x10`, and a managed-verity record at `0x240:0x2c0`. See source note 13.

[^installer-config]: The official UBports installer configuration for `r1` requires stock rabbitOS v0.8 and an unlocked bootloader, downloads checksum-pinned boot/super/vbmeta artifacts, flashes those physical partitions, formats userdata, and reboots to UBports recovery. See source note 8.

[^avb]: AOSP and the AVB source describe signed vbmeta descriptors, partition hashes, hashtrees, and chained partitions. See source notes 2 and 6.

[^managed]: The AVB source documents persistent storage named `avb.managed_verity_mode` and the mapping of managed EIO mode to `androidboot.veritymode` parameters. See source note 6.

[^ab]: AOSP documents default-current-slot fastboot behavior and the slot variables for successful, unbootable, and retry state. See source note 4.

[^device-state]: AOSP distinguishes locked devices, which prevent modification, from unlocked devices, which allow it, and describes the standardized unlock transition. See source note 3.

[^halium]: UBports' porting documentation explains the Ubuntu Touch root filesystem, Halium adaptation, Android-derived kernel, and vendor blob relationship. See source note 9.

[^ut-device]: The official Rabbit R1 device page lists Halium 12.0, the UBports Installer, stock rabbitOS v0.8, and an unlocked bootloader as the installation prerequisites. See source note 7.

[^ut-features]: The official device page reports its current feature matrix, partial USB status, advanced-user classification, and unsupported hardware features. See source note 7.

[^ut-2404]: UBports' Ubuntu Touch 24.04-1.0 release announcement includes Rabbit R1 among the supported devices. See source note 14.

[^ut-24042]: UBports' Ubuntu Touch 24.04-2.0 test announcement includes Rabbit R1. At the research date, current stable availability should be taken from the installer. See source note 15.

[^ut-devices]: UBports' supported-devices guidance says dual boot is unsupported and manual installation is discouraged when the installer is available. See https://devices.ubuntu-touch.io/.

[^manual-stock]: The community recovery provides a package-specific full stock flash and Rabbit-specific slot metadata reset. It also warns that archive filenames and protected partitions matter. See source note 13.

[^seccfg-procedure]: The community writeup includes the patched `mtkclient` V4 header generation, full-partition merge, field verification, and write sequence. See source note 13.

[^ut-install]: Official installer links and platform packages are published from the Rabbit R1 device page. UBports troubleshooting documentation should be consulted for current udev and installer details. See source note 7.
EOF

cp "$DOC" /mnt/data/rabbit-r1-boot-integrity-and-ubuntu-touch.md
wc -w "$DOC"
wc -l "$DOC"
```

<details><summary>💭 Thinking</summary>

**Appended recovery decision tree documentation and removed empty footnotes heading**

</details>

```unknown
bash -lc set -euo pipefail
WORK=/mnt/data/_rabbit_r1_work
python /home/oai/skills/pdfs/scripts/md_to_pdf.py \
  "$WORK/rabbit-r1-boot-integrity-and-ubuntu-touch.md" \
  -o /mnt/data/rabbit-r1-boot-integrity-and-ubuntu-touch.pdf \
  --pdf_engine xelatex \
  --resource_path "$WORK" \
  --extra=--include-in-header="$WORK/header.tex" \
  --extra=--listings \
  --extra=--top-level-division=chapter \
  --extra=--standalone \
  --extra=-V \
  --extra=titlepage=true
```

<details><summary>💭 Thinking</summary>

**Compiled and refined Rabbit R1 Boot Integrity PDF with LaTeX fixes**

</details>

```unknown
bash -lc pdfinfo /mnt/data/rabbit-r1-boot-integrity-and-ubuntu-touch.pdf | sed -n '1,30p'; printf '\nUNICODE NON-ASCII:\n'; python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/_rabbit_r1_work/rabbit-r1-boot-integrity-and-ubuntu-touch.md')
s=p.read_text()
for i,line in enumerate(s.splitlines(),1):
    chars=sorted({c for c in line if ord(c)>127})
    if chars:
        print(i, ''.join(chars), repr(line[:240]))
PY
```

<details><summary>💭 Thinking</summary>

**Inspected PDF rendering, metadata, fonts, links, and Unicode glyphs**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/_rabbit_r1_work/header.tex')
s=p.read_text().replace('\\setmainfont{EB Garamond}', '\\setmainfont{Noto Serif}')
p.write_text(s)
PY
rm -f /mnt/data/rabbit-r1-boot-integrity-and-ubuntu-touch.pdf
python /home/oai/skills/pdfs/scripts/md_to_pdf.py /mnt/data/_rabbit_r1_work/rabbit-r1-boot-integrity-and-ubuntu-touch.md -o /mnt/data/rabbit-r1-boot-integrity-and-ubuntu-touch.pdf --pdf_engine xelatex --resource_path /mnt/data/_rabbit_r1_work --extra=--include-in-header=/mnt/data/_rabbit_r1_work/header.tex --extra=--listings --extra=--top-level-division=chapter --extra=--standalone --extra=-V --extra=titlepage=true
```

<details><summary>💭 Thinking</summary>

**Rebuilt and validated PDF rendering, metadata, contact sheets, and deliverables**

</details>

```unknown
bash -lc rm -rf /mnt/data/_rabbit_r1_work
for f in /mnt/data/rabbit-r1-boot-integrity-and-ubuntu-touch.md /mnt/data/rabbit-r1-boot-integrity-and-ubuntu-touch.pdf; do test -s "$f" && echo "OK $f $(stat -c '%s bytes' "$f")"; done
find /mnt/data -maxdepth 1 -type f -printf '%f\n' | sort | sed -n '1,120p'
```

<details><summary>💭 Thinking</summary>

**Removed intermediate deliverables and verified final files**

</details>

```json
{"paths":["GitHub"],"query":"search"}
```

# Rabbit R1 Boot Integrity, Recovery, and Ubuntu Touch

The completed textbook-style guide is available in both formats:

- [Download the Markdown textbook](sandbox:/mnt/data/rabbit-r1-boot-integrity-and-ubuntu-touch.md)
- [Download the PDF textbook — 70 pages](sandbox:/mnt/data/rabbit-r1-boot-integrity-and-ubuntu-touch.pdf)

## Central diagnosis

Your transcript shows that the **bootloader-unlock workaround succeeded**. Initially, `unlock_ability = 0` prevented writes. After `r1_escape` modified the final byte of the FRP partition, `fastboot flashing unlock` returned `OKAY`, and you successfully wrote `boot_a`, `boot_b`, and the various `vbmeta` partitions.

The installation did not then produce a complete operating system:

- `r1_escape` expected a separately supplied `system.img`.
- Your `find . -name system.img` returned nothing.
- The stock Rabbit archive instead contained `super.img`, which packages Android’s logical `system`, `vendor`, and related partitions.
- You restored stock boot images but flashed the AVB metadata with verification-disabling flags.
- The resulting device therefore has an unlocked but internally mixed boot chain rather than a coherent stock installation or a coherent Ubuntu Touch installation.

The recommended route in the textbook is:

1. Preserve backups of `seccfg`, FRP, the GPT, and device-specific calibration partitions.
2. Restore a complete, mutually matched rabbitOS v0.8.293 installation while keeping the bootloader unlocked.
3. Normalize the active A/B slot and confirm stock can boot once.
4. Use the official UBports Installer with **Bootstrap** and **Wipe Userdata** enabled.
5. Leave the bootloader unlocked after Ubuntu Touch is installed.

Rabbit R1 is an official UBports target, and its documented prerequisite is stock rabbitOS v0.8 with an unlocked bootloader. The current installer configuration flashes a matched Ubuntu Touch `vbmeta.img`, `boot.img`, and complete `super.img` from ordinary bootloader fastboot, formats `userdata`, and then starts UBports recovery. It does **not** require the `fastboot reboot-fastboot` transition that repeatedly failed in your session. citeturn529907view10turn529907view0

The persistent `seccfg`/managed-verity repair described in the community write-up is treated as a **last-resort decision gate**, not the first action. It becomes relevant only when a verified, full stock restore still produces the red dm-verity/EIO loop. The document explains the relevant fields, why direct hex editing is unsafe, what must be backed up, and how to validate a generated candidate before any write. citeturn822673view0turn252751view3turn252751view4

