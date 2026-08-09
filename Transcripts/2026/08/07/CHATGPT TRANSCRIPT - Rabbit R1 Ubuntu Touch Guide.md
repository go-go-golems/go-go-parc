# Rabbit R1 Ubuntu Touch Guide

- URL: https://chatgpt.com/c/6a7629ba-dca0-83ea-aaf3-fed9642313ad
- Created: 2026-08-07T18:53:50.214Z

---

> I am seeing "dm-verity corruption" after booting my rabbit-r1, I found this to maybe help: https\://github.com/jonathanprocter/rabbit-r1-deverity-recovery/blob/main/docs/rabbit-r1-de-verity-recovery-community-writeup.mdd I have been using https\://github.com/RabbitHoleEscapeR1/r1\_escapepe first to go into flashboot, and then I ran these commands: Explain to me what this actually all is about and how I get from here to running ubuntu touch on this device. Write a markdown and PDF textbook style document that explains it all \\--- code/others/rabbit-r1 ❯ git clone https\://github.com/RabbitHoleEscapeR1/r1\_escape.gitit Cloning into 'r1\\\_escape'... remote: Enumerating objects: 63, done. remote: Counting objects: 100% (20/20), done. remote: Compressing objects: 100% (14/14), done. remote: Total 63 (delta 12), reused 7 (delta 6), pack-reused 43 (from 1) Receiving objects: 100% (63/63), 20.71 KiB | 20.71 MiB/s, done. Resolving deltas: 100% (31/31), done. code/others/rabbit-r1 ❯ cat /etc/modprobe.d/blacklist-cdc\\\_acm.conf 2>/dev/null code/others/rabbit-r1 ❯ modprobe cdc\\\_acm code/others/rabbit-r1 ❯ >.... ### Step 14: Reboot \`\`\`bash fastboot reboot \`\`\` The device will show an "orange state" warning briefly (this is normal -- it indicates the bootloader is unlocked), then boot into CipherOS. ### Step 15: Configure ADB Access On the host, disable \`cdc\_acm\` so \`adb\` can connect: \`\`\`bash rmmod cdc\_acm # Re-enable the blacklist to persist across reboots mv /etc/modprobe.d/blacklist-cdc\_acm.conf.disabled /etc/modprobe.d/blacklist-cdc\_acm.conf # Verify ADB connection adb devices \`\`\` ### Step 16: Post-Install Setup \`\`\`bash # Wake the screen (it may appear off due to sleep) adb shell input keyevent KEYCODE\_WAKEUP # Set display density for R1's small screen adb shell wm density 190 \`\`\` You should now see the CipherOS home screen on the R1. ## Restoring Stock Firmware The R1 can always be restored to stock RabbitOS: 1. Enter fastboot mode via \`mtkbootcmd.py\` (Step 1 above) 2. Flash stock boot.img to both slots (Step 2) 3. Flash vbmeta with \`--disable-verity --disable-verification\` (Step 3) 4. Reboot to fastbootd (Step 4) 5. Flash stock super.img (Step 5) 6. Erase userdata: \`fastboot erase userdata\` 7. Reboot: \`fastboot reboot\` Stock firmware v0.8.293 is available at [rabbit-hmi-oss/firmware]\([https://github.com/rabbit-hmi-oss/firmware/releases](https://github.com/rabbit-hmi-oss/firmware/releases)). ## Final Configuration | Setting | Value | | ------------------------------------------------------------------------------- | -------------------------------------- | | ROM | CipherOS (cipher\\\_r1-userdebug) | | Android Version | 16 | | Build | BP2A.250605.031.A2 | | Architecture | arm64-v8a | | SDK Level | 36 | | Display Density | 190 | | Active Slot | a | | Boot Image | Stock v0.8.293 (for fastbootd support) | | System/Vendor/Product | CipherOS | | code/others/rabbit-r1 | | | ❯ python3 r1\\\_escape/mtkbootcmd.py FASTBOOT | | | Traceback (most recent call last): | | | File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkbootcmd.py", line 6, in | | \`\`\` import serial \`\`\` ModuleNotFoundError: No module named 'serial' code/others/rabbit-r1 ❯ pip3 install pyserial Collecting pyserial Downloading pyserial-3.5-py2.py3-none-any.whl.metadata (1.6 kB) Downloading pyserial-3.5-py2.py3-none-any.whl (90 kB) Installing collected packages: pyserial Successfully installed pyserial-3.5 [notice] A new release of pip is available: 24.3.1 -> 26.2 [notice] To update, run: pip install --upgrade pip code/others/rabbit-r1 took 2s ❯ python3 r1\\\_escape/mtkbootcmd.py FASTBOOT Listening for ports! Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface HWID: USB VID\\\:PID=0E8D:2000 LOCATION=3-1:1.0 Got port: /dev/ttyACM0 Initializing port /dev/ttyACM0 b'FASTBOOT' cmd sent code/others/rabbit-r1 took 38s ❯ fastboot devices code/others/rabbit-r1 ❯ fastboot devices code/others/rabbit-r1 ❯ fastboot devices code/others/rabbit-r1 ❯ sudo fastboot devices code/others/rabbit-r1 ❯ sudo su root\\@f:/home/manuel/code/others/rabbit-r1# fastboot devices root\\@f:/home/manuel/code/others/rabbit-r1# fastboot devices root\\@f:/home/manuel/code/others/rabbit-r1# sudo ^C root\\@f:/home/manuel/code/others/rabbit-r1# bluetoothctl info 08\\\:FF:44:2B:4C:90^C root\\@f:/home/manuel/code/others/rabbit-r1# python3 r1\\\_escape/mtkbootcmd.py FASTBOOT Listening for ports! Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface HWID: USB VID\\\:PID=0E8D:2000 LOCATION=3-1:1.0 Got port: /dev/ttyACM0 Initializing port /dev/ttyACM0 b'FASTBOOT' cmd sent root\\@f:/home/manuel/code/others/rabbit-r1# unzip \\\~/^C root\\@f:/home/manuel/code/others/rabbit-r1# exit code/others/rabbit-r1 took 1m55s ❯ unzip \\\~/Downloads/rabbit\\\_OS\\\_v0.8.293.zip Archive: /home/manuel/Downloads/rabbit\\\_OS\\\_v0.8.293.zip creating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/ inflating: \\\_\\\_MACOSX/.\\\_rabbit\\\_OS\\\_v0.8.293\\\_20250516110545 inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/sspm.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_sspm.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/preloader\\\_emmc.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_preloader\\\_emmc.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/scp.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_scp.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/MT6765\\\_Android\\\_scatter.xml inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_MT6765\\\_Android\\\_scatter.xml inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/tee.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_tee.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/boot.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_boot.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/lk.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_lk.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/super\\\_empty.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_super\\\_empty.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/vbmeta.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_vbmeta.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/preloader\\\_ufs.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_preloader\\\_ufs.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/MT6765\\\_Android\\\_scatter.txt inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_MT6765\\\_Android\\\_scatter.txt inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/preloader\\\_raw\\.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_preloader\\\_raw\\.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/gz.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_gz.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/preloader.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_preloader.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/preloader\\\_k65v1\\\_64\\\_bsp.bin inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_preloader\\\_k65v1\\\_64\\\_bsp.bin inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/md1img.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_md1img.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/super.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_super.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/dtbo.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_dtbo.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/spmfw\\.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_spmfw\\.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/vbmeta\\\_system.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_vbmeta\\\_system.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/logo.bin inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_logo.bin inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/userdata.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_userdata.img inflating: rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/vbmeta\\\_vendor.img inflating: \\\_\\\_MACOSX/rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/.\\\_vbmeta\\\_vendor.img code/others/rabbit-r1 took 14s ❯ fastboot flash boot\\\_a /path/to/stock\\\_firmware/boot.img fastboot: error: cannot load '/path/to/stock\\\_firmware/boot.img': No such file or directory code/others/rabbit-r1 ❯ fastboot flash boot\\\_a ./rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/boot.img Sending 'boot\\\_a' (32768 KB) OKAY [ 1.210s] Writing 'boot\\\_a' FAILED (remote: 'not allowed in locked state') fastboot: error: Command failed code/others/rabbit-r1 ❯ fastboot flash boot\\\_b ./rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/boot.img Sending 'boot\\\_b' (32768 KB) OKAY [ 1.209s] Writing 'boot\\\_b' FAILED (remote: 'not allowed in locked state') fastboot: error: Command failed code/others/rabbit-r1 ❯ fastboot oem unlock FAILED (remote: 'unknown command') fastboot: error: Command failed code/others/rabbit-r1 ❯ fastboot bootloader unlock fastboot: usage: unknown command bootloader code/others/rabbit-r1 ❯ fastboot fastboot: usage: no command code/others/rabbit-r1 ❯ fastboot help usage: fastboot [OPTION...] COMMAND... flashing: update ZIP Flash all partitions from an update.zip package. flashall Flash all partitions from $ANDROID\\\_PRODUCT\\\_OUT. On A/B devices, flashed slot is set as active. Secondary images may be flashed to inactive slot. flash PARTITION [FILENAME] Flash given partition, using the image from $ANDROID\\\_PRODUCT\\\_OUT if no filename is given. basics: devices [-l] List devices in bootloader (-l: with device paths). getvar NAME Display given bootloader variable. reboot [bootloader] Reboot device. locking/unlocking: flashing lock|unlock Lock/unlock partitions for flashing flashing lock\\\_critical|unlock\\\_critical Lock/unlock 'critical' bootloader partitions. flashing get\\\_unlock\\\_ability Check whether unlocking is allowed (1) or not(0). advanced: erase PARTITION Erase a flash partition. format[:FS\\\_TYPE] PARTITION Format a flash partition. set\\\_active SLOT Set the active slot. oem [COMMAND...] Execute OEM-specific command. gsi wipe|disable Wipe or disable a GSI installation (fastbootd only). wipe-super [SUPER\\\_EMPTY] Wipe the super partition. This will reset it to contain an empty set of default dynamic partitions. create-logical-partition NAME SIZE Create a logical partition with the given name and size, in the super partition. delete-logical-partition NAME Delete a logical partition with the given name. resize-logical-partition NAME SIZE Change the size of the named logical partition. snapshot-update cancel On devices that support snapshot-based updates, cancel an in-progress update. This may make the device unbootable until it is reflashed. snapshot-update merge On devices that support snapshot-based updates, finish an in-progress update if it is in the "merging" phase. fetch PARTITION OUT\\\_FILE Fetch a partition image from the device. boot image: boot KERNEL [RAMDISK [SECOND]] Download and boot kernel from RAM. flash\\\:raw PARTITION KERNEL [RAMDISK [SECOND]] Create boot image and flash it. \\--dtb DTB Specify path to DTB for boot image header version 2. \\--cmdline CMDLINE Override kernel command line. \\--base ADDRESS Set kernel base address (default: 0x10000000). \\--kernel-offset Set kernel offset (default: 0x00008000). \\--ramdisk-offset Set ramdisk offset (default: 0x01000000). \\--tags-offset Set tags offset (default: 0x00000100). \\--dtb-offset Set dtb offset (default: 0x01100000). \\--page-size BYTES Set flash page size (default: 2048). \\--header-version VERSION Set boot image header version. \\--os-version MAJOR[.MINOR[.PATCH]] Set boot image OS version (default: 0.0.0). \\--os-patch-level YYYY-MM-DD Set boot image OS security patch level. Android Things: stage IN\\\_FILE Sends given file to stage for the next command. get\\\_staged OUT\\\_FILE Writes data staged by the last command to a file. options: -w Wipe userdata. -s SERIAL Specify a USB device. -s tcp|udp\\\:HOST Specify a network device. -S SIZE[K|M|G] Break into sparse files no larger than SIZE. \\--force Force a flash operation that may be unsafe. \\--slot SLOT Use SLOT; 'all' for both slots, 'other' for non-current slot (default: current active slot). \\--set-active[=SLOT] Sets the active slot before rebooting. \\--skip-secondary Don't flash secondary slots in flashall/update. \\--skip-reboot Don't reboot device after flashing. \\--disable-verity Sets disable-verity when flashing vbmeta. \\--disable-verification Sets disable-verification when flashing vbmeta. \\--fs-options=OPTION[,OPTION] Enable filesystem features. OPTION supports casefold, projid, compress \\--unbuffered Don't buffer input or output. \\--verbose, -v Verbose output. \\--version Display version. \\--help, -h Show this message. code/others/rabbit-r1 ❯ fastboot flashing unlock (bootloader) Start unlock flow FAILED (remote: ' Unlock operation is not allowed ') fastboot: error: Command failed code/others/rabbit-r1 took 3s ❯ fastboot flashing get\\\_unlock\\\_capability fastboot: usage: unknown 'flashing' command get\\\_unlock\\\_capability code/others/rabbit-r1 ❯ fastboot flashing get\\\_unlock\\\_ability (bootloader) unlock\\\_ability = 0 OKAY [ 0.001s] Finished. Total time: 0.001s code/others/rabbit-r1 ❯ fastboot flashing unlock (bootloader) Start unlock flow FAILED (remote: ' Unlock operation is not allowed ') fastboot: error: Command failed code/others/rabbit-r1 took 3s ❯ fastboot flashing get\\\_unlock\\\_ability (bootloader) unlock\\\_ability = 0 OKAY [ 0.001s] Finished. Total time: 0.001s code/others/rabbit-r1 ❯ fastboot flashing unlock (bootloader) Start unlock flow FAILED (remote: ' Unlock operation is not allowed ') fastboot: error: Command failed code/others/rabbit-r1 took 3s ❯ fastboot flashing unlock (bootloader) Start unlock flow FAILED (remote: ' Unlock operation is not allowed ') fastboot: error: Command failed code/others/rabbit-r1 took 3s ❯ fastboot flashing unlock --help usage: fastboot [OPTION...] COMMAND... flashing: update ZIP Flash all partitions from an update.zip package. flashall Flash all partitions from $ANDROID\\\_PRODUCT\\\_OUT. On A/B devices, flashed slot is set as active. Secondary images may be flashed to inactive slot. flash PARTITION [FILENAME] Flash given partition, using the image from $ANDROID\\\_PRODUCT\\\_OUT if no filename is given. basics: devices [-l] List devices in bootloader (-l: with device paths). getvar NAME Display given bootloader variable. reboot [bootloader] Reboot device. locking/unlocking: flashing lock|unlock Lock/unlock partitions for flashing flashing lock\\\_critical|unlock\\\_critical Lock/unlock 'critical' bootloader partitions. flashing get\\\_unlock\\\_ability Check whether unlocking is allowed (1) or not(0). advanced: erase PARTITION Erase a flash partition. format[:FS\\\_TYPE] PARTITION Format a flash partition. set\\\_active SLOT Set the active slot. oem [COMMAND...] Execute OEM-specific command. gsi wipe|disable Wipe or disable a GSI installation (fastbootd only). wipe-super [SUPER\\\_EMPTY] Wipe the super partition. This will reset it to contain an empty set of default dynamic partitions. create-logical-partition NAME SIZE Create a logical partition with the given name and size, in the super partition. delete-logical-partition NAME Delete a logical partition with the given name. resize-logical-partition NAME SIZE Change the size of the named logical partition. snapshot-update cancel On devices that support snapshot-based updates, cancel an in-progress update. This may make the device unbootable until it is reflashed. snapshot-update merge On devices that support snapshot-based updates, finish an in-progress update if it is in the "merging" phase. fetch PARTITION OUT\\\_FILE Fetch a partition image from the device. boot image: boot KERNEL [RAMDISK [SECOND]] Download and boot kernel from RAM. flash\\\:raw PARTITION KERNEL [RAMDISK [SECOND]] Create boot image and flash it. \\--dtb DTB Specify path to DTB for boot image header version 2. \\--cmdline CMDLINE Override kernel command line. \\--base ADDRESS Set kernel base address (default: 0x10000000). \\--kernel-offset Set kernel offset (default: 0x00008000). \\--ramdisk-offset Set ramdisk offset (default: 0x01000000). \\--tags-offset Set tags offset (default: 0x00000100). \\--dtb-offset Set dtb offset (default: 0x01100000). \\--page-size BYTES Set flash page size (default: 2048). \\--header-version VERSION Set boot image header version. \\--os-version MAJOR[.MINOR[.PATCH]] Set boot image OS version (default: 0.0.0). \\--os-patch-level YYYY-MM-DD Set boot image OS security patch level. Android Things: stage IN\\\_FILE Sends given file to stage for the next command. get\\\_staged OUT\\\_FILE Writes data staged by the last command to a file. options: -w Wipe userdata. -s SERIAL Specify a USB device. -s tcp|udp\\\:HOST Specify a network device. -S SIZE[K|M|G] Break into sparse files no larger than SIZE. \\--force Force a flash operation that may be unsafe. \\--slot SLOT Use SLOT; 'all' for both slots, 'other' for non-current slot (default: current active slot). \\--set-active[=SLOT] Sets the active slot before rebooting. \\--skip-secondary Don't flash secondary slots in flashall/update. \\--skip-reboot Don't reboot device after flashing. \\--disable-verity Sets disable-verity when flashing vbmeta. \\--disable-verification Sets disable-verification when flashing vbmeta. \\--fs-options=OPTION[,OPTION] Enable filesystem features. OPTION supports casefold, projid, compress \\--unbuffered Don't buffer input or output. \\--verbose, -v Verbose output. \\--version Display version. \\--help, -h Show this message. code/others/rabbit-r1 ❯ fastboot flashing unlock --disable-verify --disable-verification fastboot: unrecognized option '--disable-verify' code/others/rabbit-r1 ❯ fastboot flashing unlock --disable-verify --disable-verification code/others/rabbit-r1 ❯ cd .. \\\~/code/others ❯ git clone https\://github.com/RabbitHoleEscapeR1/r1\_escape.gitit \\\~/code/others ❯ cd - \\\~/code/others/rabbit-r1 code/others/rabbit-r1 ❯ ls \\\_\\\_MACOSX r1\\\_escape rabbit\\\_OS\\\_v0.8.293\\\_20250516110545 code/others/rabbit-r1 ❯ cd r1\\\_escape r1\\\_escape on  main via 🐍 v3.13.2 ❯ ls mtkbootcmd.py r1.ps1 r1.sh README.md vbmeta.img r1\\\_escape on  main via 🐍 v3.13.2 ❯ cat r1.sh \\#!/bin/bash install\\\_debian() { sudo apt update [[ -x "$(command -v git)" ]] || sudo apt install -y git [[ -x "$(command -v python3)" ]] || sudo apt install -y python3 [[ -x "$(command -v pip3)" ]] || sudo apt install -y python3-pip [[ -x "$(command -v dos2unix)" ]] || sudo apt install -y dos2unix [[ -x "$(command -v curl)" ]] || sudo apt install -y curl [[ -x "$(command -v unzip)" ]] || sudo apt install -y unzip } install\\\_arch() { sudo pacman -Sy --noconfirm [[ -x "$(command -v git)" ]] || sudo pacman -S --noconfirm git [[ -x "$(command -v python3)" ]] || sudo pacman -S --noconfirm python [[ -x "$(command -v dos2unix)" ]] || sudo pacman -S --noconfirm dos2unix [[ -x "$(command -v curl)" ]] || sudo pacman -S --noconfirm curl [[ -x "$(command -v unzip)" ]] || sudo pacman -S --noconfirm unzip [[ -x "$(command -v virtualenv)" ]] || sudo pacman -S --noconfirm python-virtualenv } install\\\_fedora() { sudo dnf update -y [[ -x "$(command -v git)" ]] || sudo dnf install -y git [[ -x "$(command -v python3)" ]] || sudo dnf install -y python3 [[ -x "$(command -v pip3)" ]] || sudo dnf install -y python3-pip [[ -x "$(command -v dos2unix)" ]] || sudo dnf install -y dos2unix [[ -x "$(command -v curl)" ]] || sudo dnf install -y curl [[ -x "$(command -v unzip)" ]] || sudo dnf install -y unzip } if [[ "$OSTYPE" == "linux-gnu"\\\* ]]; then if command -v apt-get &>/dev/null; then install\\\_debian elif command -v pacman &>/dev/null; then install\\\_arch elif command -v dnf &>/dev/null; then install\\\_fedora else echo "Unsupported Linux distribution" exit 1 fi else echo "Unsupported OS" exit 1 fi if [[ "$OSTYPE" != "linux-gnu"\\\* || ! "$(command -v pacman)" ]]; then pip3 show virtualenv &>/dev/null || pip3 install virtualenv fi if [[ "$OSTYPE" == "linux-gnu"\\\* ]]; then if command -v apt-get &>/dev/null; then sudo apt install -y adb fastboot elif command -v pacman &>/dev/null; then sudo pacman -S --noconfirm android-tools elif command -v dnf &>/dev/null; then sudo dnf install -y android-tools fi fi # Setup virtualenv and install requirements python3 -m venv venv source venv/bin/activate chmod +x mtkbootcmd.py # Download mtkclient REPO\\\_URL="https\://github.com/AgentFabulous/mtkclientt" REPO\\\_NAME=$(basename "$REPO\\\_URL" .git) git clone "$REPO\\\_URL" cd "$REPO\\\_NAME" || exit pip3 install -r requirements.txt rm -f frp.bin read -p "[\\\*] Power off your device, press ENTER plug it into your PC" # Read FRP sudo python3 mtk r frp frp.bin sudo chown $USER frp.bin LAST\\\_BYTE=$(xxd -p -l 1 -s -1 frp.bin) if [[ "$LAST\\\_BYTE" == "00" ]]; then printf '\x01' | dd of=frp.bin bs=1 seek=$(($(stat -c%s frp.bin) - 1)) conv=notrunc fi # Write FRP sudo python3 mtk w frp frp.bin read -p "[\\\*] Unplug your device, press ENTER, plug it back in" cd .. sudo ./mtkbootcmd.py FASTBOOT echo "[\\\*] Waiting for fastboot..." while ! fastboot devices | grep -q "fastboot"; do sleep 1 done fastboot flashing unlock fastboot -w fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img fastboot reboot-fastboot fastboot flash system system.img fastboot reboot r1\\\_escape on  main via 🐍 v3.13.2 ❯ # Download mtkclient REPO\\\_URL="https\://github.com/AgentFabulous/mtkclientt" REPO\\\_NAME=$(basename "$REPO\\\_URL" .git) git clone "$REPO\\\_URL" cd "$REPO\\\_NAME" || exit pip3 install -r requirements.txt Cloning into 'mtkclient'... remote: Enumerating objects: 5833, done. remote: Counting objects: 100% (4/4), done. remote: Compressing objects: 100% (4/4), done. remote: Total 5833 (delta 0), reused 0 (delta 0), pack-reused 5829 (from 1) Receiving objects: 100% (5833/5833), 88.87 MiB | 25.00 MiB/s, done. Resolving deltas: 100% (4525/4525), done. Collecting wheel>=0.37.1 (from -r requirements.txt (line 1)) Downloading wheel-0.47.0-py3-none-any.whl.metadata (2.3 kB) Collecting pyusb>=1.2.1 (from -r requirements.txt (line 2)) Downloading pyusb-1.3.1-py3-none-any.whl.metadata (2.5 kB) Requirement already satisfied: pycryptodome>=3.15.0 in /home/manuel/.pyenv/versions/3.13.2/lib/python3.13/site-packages (from -r requirements.txt (line 3)) (3.23.0) Collecting pycryptodomex (from -r requirements.txt (line 4)) Downloading pycryptodomex-3.23.0-cp37-abi3-manylinux\\\_2\\\_17\\\_x86\\\_64.manylinux2014\\\_x86\\\_64.whl.metadata (3.4 kB) Collecting colorama>=0.4.4 (from -r requirements.txt (line 5)) Using cached colorama-0.4.6-py2.py3-none-any.whl.metadata (17 kB) Collecting shiboken6>=6.4.0.1 (from -r requirements.txt (line 6)) Downloading shiboken6-6.11.1-cp310-abi3-manylinux\\\_2\\\_34\\\_x86\\\_64.whl.metadata (2.4 kB) Collecting pyside6>=6.4.0.1 (from -r requirements.txt (line 7)) Downloading pyside6-6.11.1-cp310-abi3-manylinux\\\_2\\\_34\\\_x86\\\_64.whl.metadata (5.3 kB) Collecting mock>=4.0.3 (from -r requirements.txt (line 8)) Downloading mock-5.2.0-py3-none-any.whl.metadata (3.1 kB) Requirement already satisfied: pyserial>=3.5 in /home/manuel/.pyenv/versions/3.13.2/lib/python3.13/site-packages (from -r requirements.txt (line 9)) (3.5) Collecting flake8 (from -r requirements.txt (line 10)) Downloading flake8-7.3.0-py2.py3-none-any.whl.metadata (3.8 kB) Collecting keystone-engine (from -r requirements.txt (line 11)) Downloading keystone\\\_engine-0.9.2-py2.py3-none-manylinux1\\\_x86\\\_64.whl.metadata (1.8 kB) Collecting capstone (from -r requirements.txt (line 12)) Downloading capstone-5.0.9-py3-none-manylinux\\\_2\\\_17\\\_x86\\\_64.manylinux2014\\\_x86\\\_64.whl.metadata (3.3 kB) Collecting unicorn (from -r requirements.txt (line 13)) Downloading unicorn-2.1.4-cp37-abi3-manylinux\\\_2\\\_17\\\_x86\\\_64.manylinux2014\\\_x86\\\_64.whl.metadata (4.2 kB) Collecting fusepy (from -r requirements.txt (line 14)) Downloading fusepy-3.0.1.tar.gz (11 kB) Installing build dependencies ... done Getting requirements to build wheel ... done Preparing metadata (pyproject.toml) ... done Requirement already satisfied: packaging>=24.0 in /home/manuel/.pyenv/versions/3.13.2/lib/python3.13/site-packages (from wheel>=0.37.1->-r requirements.txt (line 1)) (26.0) Collecting PySide6\\\_Essentials==6.11.1 (from pyside6>=6.4.0.1->-r requirements.txt (line 7)) Downloading pyside6\\\_essentials-6.11.1-cp310-abi3-manylinux\\\_2\\\_34\\\_x86\\\_64.whl.metadata (3.6 kB) Collecting PySide6\\\_Addons==6.11.1 (from pyside6>=6.4.0.1->-r requirements.txt (line 7)) Downloading pyside6\\\_addons-6.11.1-cp310-abi3-manylinux\\\_2\\\_34\\\_x86\\\_64.whl.metadata (4.0 kB) Collecting mccabe<0.8.0,>=0.7.0 (from flake8->-r requirements.txt (line 10)) Downloading mccabe-0.7.0-py2.py3-none-any.whl.metadata (5.0 kB) Collecting pycodestyle<2.15.0,>=2.14.0 (from flake8->-r requirements.txt (line 10)) Downloading pycodestyle-2.14.0-py2.py3-none-any.whl.metadata (4.5 kB) Collecting pyflakes<3.5.0,>=3.4.0 (from flake8->-r requirements.txt (line 10)) Downloading pyflakes-3.4.0-py2.py3-none-any.whl.metadata (3.5 kB) Downloading wheel-0.47.0-py3-none-any.whl (32 kB) Downloading pyusb-1.3.1-py3-none-any.whl (58 kB) Downloading pycryptodomex-3.23.0-cp37-abi3-manylinux\\\_2\\\_17\\\_x86\\\_64.manylinux2014\\\_x86\\\_64.whl (2.3 MB) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.3/2.3 MB 22.8 MB/s eta 0:00:00 Using cached colorama-0.4.6-py2.py3-none-any.whl (25 kB) Downloading shiboken6-6.11.1-cp310-abi3-manylinux\\\_2\\\_34\\\_x86\\\_64.whl (272 kB) Downloading pyside6-6.11.1-cp310-abi3-manylinux\\\_2\\\_34\\\_x86\\\_64.whl (572 kB) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 572.1/572.1 kB 33.8 MB/s eta 0:00:00 Downloading pyside6\\\_addons-6.11.1-cp310-abi3-manylinux\\\_2\\\_34\\\_x86\\\_64.whl (175.1 MB) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 175.1/175.1 MB 36.3 MB/s eta 0:00:00 Downloading pyside6\\\_essentials-6.11.1-cp310-abi3-manylinux\\\_2\\\_34\\\_x86\\\_64.whl (79.9 MB) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 79.9/79.9 MB 39.8 MB/s eta 0:00:00 Downloading mock-5.2.0-py3-none-any.whl (31 kB) Downloading flake8-7.3.0-py2.py3-none-any.whl (57 kB) Downloading keystone\\\_engine-0.9.2-py2.py3-none-manylinux1\\\_x86\\\_64.whl (1.8 MB) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.8/1.8 MB 46.0 MB/s eta 0:00:00 Downloading capstone-5.0.9-py3-none-manylinux\\\_2\\\_17\\\_x86\\\_64.manylinux2014\\\_x86\\\_64.whl (1.5 MB) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.5/1.5 MB 37.2 MB/s eta 0:00:00 Downloading unicorn-2.1.4-cp37-abi3-manylinux\\\_2\\\_17\\\_x86\\\_64.manylinux2014\\\_x86\\\_64.whl (16.4 MB) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 16.4/16.4 MB 38.4 MB/s eta 0:00:00 Downloading mccabe-0.7.0-py2.py3-none-any.whl (7.3 kB) Downloading pycodestyle-2.14.0-py2.py3-none-any.whl (31 kB) Downloading pyflakes-3.4.0-py2.py3-none-any.whl (63 kB) Building wheels for collected packages: fusepy Building wheel for fusepy (pyproject.toml) ... done Created wheel for fusepy: filename=fusepy-3.0.1-py3-none-any.whl size=10538 sha256=b994d028c4f09522d8a767ac141c46bffad34f7ae7776df201eaeed73e08b7d9 Stored in directory: /home/manuel/.cache/pip/wheels/bf/00/76/7656e1c2cf529781f66582d758f5295c93f81f4c30ea8156ae Successfully built fusepy Installing collected packages: keystone-engine, fusepy, wheel, unicorn, shiboken6, pyusb, pyflakes, pycryptodomex, pycodestyle, mock, mccabe, colorama, capstone, PySide6\\\_Essentials, flake8, PySide6\\\_Addons, pyside6 Successfully installed PySide6\\\_Addons-6.11.1 PySide6\\\_Essentials-6.11.1 capstone-5.0.9 colorama-0.4.6 flake8-7.3.0 fusepy-3.0.1 keystone-engine-0.9.2 mccabe-0.7.0 mock-5.2.0 pycodestyle-2.14.0 pycryptodomex-3.23.0 pyflakes-3.4.0 pyside6-6.11.1 pyusb-1.3.1 shiboken6-6.11.1 unicorn-2.1.4 wheel-0.47.0 [notice] A new release of pip is available: 24.3.1 -> 26.2 [notice] To update, run: pip install --upgrade pip mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 took 24s ❯ sudo python3 mtk r frp frp.bin mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ fastboot fastboot: usage: no command mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ fastboot help usage: fastboot [OPTION...] COMMAND... flashing: update ZIP Flash all partitions from an update.zip package. flashall Flash all partitions from $ANDROID\\\_PRODUCT\\\_OUT. On A/B devices, flashed slot is set as active. Secondary images may be flashed to inactive slot. flash PARTITION [FILENAME] Flash given partition, using the image from $ANDROID\\\_PRODUCT\\\_OUT if no filename is given. basics: devices [-l] List devices in bootloader (-l: with device paths). getvar NAME Display given bootloader variable. reboot [bootloader] Reboot device. locking/unlocking: flashing lock|unlock Lock/unlock partitions for flashing flashing lock\\\_critical|unlock\\\_critical Lock/unlock 'critical' bootloader partitions. flashing get\\\_unlock\\\_ability Check whether unlocking is allowed (1) or not(0). advanced: erase PARTITION Erase a flash partition. format[:FS\\\_TYPE] PARTITION Format a flash partition. set\\\_active SLOT Set the active slot. oem [COMMAND...] Execute OEM-specific command. gsi wipe|disable Wipe or disable a GSI installation (fastbootd only). wipe-super [SUPER\\\_EMPTY] Wipe the super partition. This will reset it to contain an empty set of default dynamic partitions. create-logical-partition NAME SIZE Create a logical partition with the given name and size, in the super partition. delete-logical-partition NAME Delete a logical partition with the given name. resize-logical-partition NAME SIZE Change the size of the named logical partition. snapshot-update cancel On devices that support snapshot-based updates, cancel an in-progress update. This may make the device unbootable until it is reflashed. snapshot-update merge On devices that support snapshot-based updates, finish an in-progress update if it is in the "merging" phase. fetch PARTITION OUT\\\_FILE Fetch a partition image from the device. boot image: boot KERNEL [RAMDISK [SECOND]] Download and boot kernel from RAM. flash\\\:raw PARTITION KERNEL [RAMDISK [SECOND]] Create boot image and flash it. \\--dtb DTB Specify path to DTB for boot image header version 2. \\--cmdline CMDLINE Override kernel command line. \\--base ADDRESS Set kernel base address (default: 0x10000000). \\--kernel-offset Set kernel offset (default: 0x00008000). \\--ramdisk-offset Set ramdisk offset (default: 0x01000000). \\--tags-offset Set tags offset (default: 0x00000100). \\--dtb-offset Set dtb offset (default: 0x01100000). \\--page-size BYTES Set flash page size (default: 2048). \\--header-version VERSION Set boot image header version. \\--os-version MAJOR[.MINOR[.PATCH]] Set boot image OS version (default: 0.0.0). \\--os-patch-level YYYY-MM-DD Set boot image OS security patch level. Android Things: stage IN\\\_FILE Sends given file to stage for the next command. get\\\_staged OUT\\\_FILE Writes data staged by the last command to a file. options: -w Wipe userdata. -s SERIAL Specify a USB device. -s tcp|udp\\\:HOST Specify a network device. -S SIZE[K|M|G] Break into sparse files no larger than SIZE. \\--force Force a flash operation that may be unsafe. \\--slot SLOT Use SLOT; 'all' for both slots, 'other' for non-current slot (default: current active slot). \\--set-active[=SLOT] Sets the active slot before rebooting. \\--skip-secondary Don't flash secondary slots in flashall/update. \\--skip-reboot Don't reboot device after flashing. \\--disable-verity Sets disable-verity when flashing vbmeta. \\--disable-verification Sets disable-verification when flashing vbmeta. \\--fs-options=OPTION[,OPTION] Enable filesystem features. OPTION supports casefold, projid, compress \\--unbuffered Don't buffer input or output. \\--verbose, -v Verbose output. \\--version Display version. \\--help, -h Show this message. mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ fastboot mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ cd r1\\\_escape mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ cd .. r1\\\_escape on  main via 🐍 v3.13.2 ❯ ls mtkbootcmd.py mtkclient r1.ps1 r1.sh README.md vbmeta.img r1\\\_escape on  main via 🐍 v3.13.2 ❯ fastboot r1\\\_escape on  main via 🐍 v3.13.2 ❯ cat r1.sh \\#!/bin/bash install\\\_debian() { sudo apt update [[ -x "$(command -v git)" ]] || sudo apt install -y git [[ -x "$(command -v python3)" ]] || sudo apt install -y python3 [[ -x "$(command -v pip3)" ]] || sudo apt install -y python3-pip [[ -x "$(command -v dos2unix)" ]] || sudo apt install -y dos2unix [[ -x "$(command -v curl)" ]] || sudo apt install -y curl [[ -x "$(command -v unzip)" ]] || sudo apt install -y unzip } install\\\_arch() { sudo pacman -Sy --noconfirm [[ -x "$(command -v git)" ]] || sudo pacman -S --noconfirm git [[ -x "$(command -v python3)" ]] || sudo pacman -S --noconfirm python [[ -x "$(command -v dos2unix)" ]] || sudo pacman -S --noconfirm dos2unix [[ -x "$(command -v curl)" ]] || sudo pacman -S --noconfirm curl [[ -x "$(command -v unzip)" ]] || sudo pacman -S --noconfirm unzip [[ -x "$(command -v virtualenv)" ]] || sudo pacman -S --noconfirm python-virtualenv } install\\\_fedora() { sudo dnf update -y [[ -x "$(command -v git)" ]] || sudo dnf install -y git [[ -x "$(command -v python3)" ]] || sudo dnf install -y python3 [[ -x "$(command -v pip3)" ]] || sudo dnf install -y python3-pip [[ -x "$(command -v dos2unix)" ]] || sudo dnf install -y dos2unix [[ -x "$(command -v curl)" ]] || sudo dnf install -y curl [[ -x "$(command -v unzip)" ]] || sudo dnf install -y unzip } if [[ "$OSTYPE" == "linux-gnu"\\\* ]]; then if command -v apt-get &>/dev/null; then install\\\_debian elif command -v pacman &>/dev/null; then install\\\_arch elif command -v dnf &>/dev/null; then install\\\_fedora else echo "Unsupported Linux distribution" exit 1 fi else echo "Unsupported OS" exit 1 fi if [[ "$OSTYPE" != "linux-gnu"\\\* || ! "$(command -v pacman)" ]]; then pip3 show virtualenv &>/dev/null || pip3 install virtualenv fi if [[ "$OSTYPE" == "linux-gnu"\\\* ]]; then if command -v apt-get &>/dev/null; then sudo apt install -y adb fastboot elif command -v pacman &>/dev/null; then sudo pacman -S --noconfirm android-tools elif command -v dnf &>/dev/null; then sudo dnf install -y android-tools fi fi # Setup virtualenv and install requirements python3 -m venv venv source venv/bin/activate chmod +x mtkbootcmd.py # Download mtkclient REPO\\\_URL="https\://github.com/AgentFabulous/mtkclientt" REPO\\\_NAME=$(basename "$REPO\\\_URL" .git) git clone "$REPO\\\_URL" cd "$REPO\\\_NAME" || exit pip3 install -r requirements.txt rm -f frp.bin read -p "[\\\*] Power off your device, press ENTER plug it into your PC" # Read FRP sudo python3 mtk r frp frp.bin sudo chown $USER frp.bin LAST\\\_BYTE=$(xxd -p -l 1 -s -1 frp.bin) if [[ "$LAST\\\_BYTE" == "00" ]]; then printf '\x01' | dd of=frp.bin bs=1 seek=$(($(stat -c%s frp.bin) - 1)) conv=notrunc fi # Write FRP sudo python3 mtk w frp frp.bin read -p "[\\\*] Unplug your device, press ENTER, plug it back in" cd .. sudo ./mtkbootcmd.py FASTBOOT echo "[\\\*] Waiting for fastboot..." while ! fastboot devices | grep -q "fastboot"; do sleep 1 done fastboot flashing unlock fastboot -w fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img fastboot reboot-fastboot fastboot flash system system.img fastboot reboot r1\\\_escape on  main via 🐍 v3.13.2 ❯ sudo python3 mtk r frp frp.bin python3: can't open file '/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtk': [Errno 2] No such file or directory r1\\\_escape on  main via 🐍 v3.13.2 ❯ mtk zsh: command not found: mtk r1\\\_escape on  main via 🐍 v3.13.2 ❯ cd - \\\~/code/others/rabbit-r1/r1\\\_escape/mtkclient mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ ls LICENSE MANIFEST.in mtk mtk.bat mtkclient mtk\\\_console.spec mtk\\\_gui mtk\\\_gui.bat mtk\\\_standalone.spec pyproject.toml README.md requirements.txt run.example stage2 vbmeta.img.empty mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ cd - mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ sudo python3 mtk r frp frp.bin Traceback (most recent call last): File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkclient/mtk", line 5, in from mtkclient.Library.mtk\\\_main import Main, metamodes File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkclient/mtkclient/Library/mtk\\\_main.py", line 10, in from mtkclient.Library.mtk\\\_class import Mtk File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkclient/mtkclient/Library/mtk\\\_class.py", line 9, in from mtkclient.Library.pltools import PLTools File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkclient/mtkclient/Library/pltools.py", line 12, in from mtkclient.Library.Exploit.kamakiri import Kamakiri File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkclient/mtkclient/Library/Exploit/kamakiri.py", line 12, in from mtkclient.Library.Connection.usblib import usb File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkclient/mtkclient/Library/Connection/usblib.py", line 7, in import usb.core # pyusb ^^^^^^^^^^^^^^^ ModuleNotFoundError: No module named 'usb' mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ sudo pip3 install pyusb error: externally-managed-environment × This environment is externally managed ╰─> To install Python packages system-wide, try apt install python3-xyz, where xyz is the package you are trying to install. \`\`\` If you wish to install a non-Debian-packaged Python package, create a virtual environment using python3 -m venv path/to/venv. Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make sure you have python3-full installed. If you wish to install a non-Debian packaged Python application, it may be easiest to use pipx install xyz, which will manage a virtual environment for you. Make sure you have pipx installed. See /usr/share/doc/python3.12/README.venv for more information. \`\`\` note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages. hint: See PEP 668 for the detailed specification. mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ sudo pip3 install pyusb mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ pip3 install pyusb Requirement already satisfied: pyusb in /home/manuel/.pyenv/versions/3.13.2/lib/python3.13/site-packages (1.3.1) [notice] A new release of pip is available: 24.3.1 -> 26.2 [notice] To update, run: pip install --upgrade pip mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ sudo pip3 install pyusb error: externally-managed-environment × This environment is externally managed ╰─> To install Python packages system-wide, try apt install python3-xyz, where xyz is the package you are trying to install. \`\`\` If you wish to install a non-Debian-packaged Python package, create a virtual environment using python3 -m venv path/to/venv. Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make sure you have python3-full installed. If you wish to install a non-Debian packaged Python application, it may be easiest to use pipx install xyz, which will manage a virtual environment for you. Make sure you have pipx installed. See /usr/share/doc/python3.12/README.venv for more information. \`\`\` note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages. hint: See PEP 668 for the detailed specification. mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ sudo python3 mtk r frp frp.bin Traceback (most recent call last): File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkclient/mtk", line 5, in from mtkclient.Library.mtk\\\_main import Main, metamodes File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkclient/mtkclient/Library/mtk\\\_main.py", line 10, in from mtkclient.Library.mtk\\\_class import Mtk File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkclient/mtkclient/Library/mtk\\\_class.py", line 9, in from mtkclient.Library.pltools import PLTools File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkclient/mtkclient/Library/pltools.py", line 12, in from mtkclient.Library.Exploit.kamakiri import Kamakiri File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkclient/mtkclient/Library/Exploit/kamakiri.py", line 12, in from mtkclient.Library.Connection.usblib import usb File "/home/manuel/code/others/rabbit-r1/r1\\\_escape/mtkclient/mtkclient/Library/Connection/usblib.py", line 7, in import usb.core # pyusb ^^^^^^^^^^^^^^^ ModuleNotFoundError: No module named 'usb' mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ python3 mtk r frp frp.bin MTK Flash/Exploit Client Public V2.0.0 Beta (c) B.Kerler 2018-2023 Preloader - Status: Waiting for PreLoader VCOM, please reconnect mobile to brom mode Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ..........Preloader Preloader - [LIB]: Status: Handshake failed, retrying... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ..........Preloader Preloader - [LIB]: Status: Handshake failed, retrying... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Device detected :) Preloader - CPU: MT6765/MT8768t(Helio P35/G35) Preloader - HW version: 0x0 Preloader - WDT: 0x10007000 Preloader - Uart: 0x11002000 Preloader - Brom payload addr: 0x100a00 Preloader - DA payload addr: 0x201000 Preloader - CQ\\\_DMA addr: 0x10212000 Preloader - Var1: 0x25 Preloader - Disabling Watchdog... Preloader - HW code: 0x766 Preloader - Target config: 0x0 Preloader - SBC enabled: False Preloader - SLA enabled: False Preloader - DAA enabled: False Preloader - SWJTAG enabled: False Preloader - EPP\\\_PARAM at 0x600 after EMMC\\\_BOOT/SDMMC\\\_BOOT: False Preloader - Root cert required: False Preloader - Mem read auth: False Preloader - Mem write auth: False Preloader - Cmd 0xC8 blocked: False Preloader - Get Target info Preloader - HW subcode: 0x8a00 Preloader - HW Ver: 0xca00 Preloader - SW Ver: 0x0 Preloader - ME\\\_ID: 55C0B1FC67D69E5E1CD382EA8780F8B7 Preloader - SOC\\\_ID: 3DCB309F2C158F3FE2D1480E8E63B9CAA15C619AD66576D325D3DEC081CBFD71 DA\\\_handler - Device is unprotected. DA\\\_handler - Device is in Preloader-Mode. DAXFlash - Uploading xflash stage 1 from MTK\\\_DA\\\_V5.bin xflashext - Patching da1 ... Mtk - Patched "Patched loader msg" in preloader Mtk - Patched "hash\\\_check" in preloader xflashext xflashext - [LIB]: Error on patching da1 version check... Mtk - Patched "Patched loader msg" in preloader Mtk - Patched "get\\\_vfy\\\_policy" in preloader xflashext - Patching da2 ... xflashext - DA version anti-rollback patched DAXFlash - Successfully uploaded stage 1, jumping .. Preloader - Jumping to 0x200000 Preloader - Jumping to 0x200000: ok. DAXFlash - Successfully received DA sync DAXFlash - Uploading stage 2... DAXFlash - Upload data was accepted. Jumping to stage 2... DAXFlash - Successfully uploaded stage 2 DAXFlash - EMMC FWVer: 0x0 DAXFlash - EMMC ID: DV6DAB DAXFlash - EMMC CID: 150100445636444142025c10dc0d291f DAXFlash - EMMC Boot1 Size: 0x400000 DAXFlash - EMMC Boot2 Size: 0x400000 DAXFlash - EMMC GP1 Size: 0x0 DAXFlash - EMMC GP2 Size: 0x0 DAXFlash - EMMC GP3 Size: 0x0 DAXFlash - EMMC GP4 Size: 0x0 DAXFlash - EMMC RPMB Size: 0x1000000 DAXFlash - EMMC USER Size: 0x1d1ec00000 DAXFlash - HW-CODE : 0x766 DAXFlash - HWSUB-CODE : 0x8A00 DAXFlash - HW-VERSION : 0xCA00 DAXFlash - SW-VERSION : 0x0 DAXFlash - CHIP-EVOLUTION : 0x0 DAXFlash - DA-VERSION : 1.0 DAXFlash - Extensions were accepted. Jumping to extensions... DAXFlash - DA Extensions successfully added DA\\\_handler - Requesting available partitions .... DA\\\_handler - Dumping partition "frp" Progress: |██████████████████████████████████████████████████| 100.0% Read (Sector 0x800 of 0x800, ) 3.00 MB/s DA\\\_handler - Dumped sector 44096 with sector count 2048 as frp.bin. mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 took 1m17s ❯ cat r1.sh cat: r1.sh: No such file or directory mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ cat ../r1.sh \\#!/bin/bash install\\\_debian() { sudo apt update [[ -x "$(command -v git)" ]] || sudo apt install -y git [[ -x "$(command -v python3)" ]] || sudo apt install -y python3 [[ -x "$(command -v pip3)" ]] || sudo apt install -y python3-pip [[ -x "$(command -v dos2unix)" ]] || sudo apt install -y dos2unix [[ -x "$(command -v curl)" ]] || sudo apt install -y curl [[ -x "$(command -v unzip)" ]] || sudo apt install -y unzip } install\\\_arch() { sudo pacman -Sy --noconfirm [[ -x "$(command -v git)" ]] || sudo pacman -S --noconfirm git [[ -x "$(command -v python3)" ]] || sudo pacman -S --noconfirm python [[ -x "$(command -v dos2unix)" ]] || sudo pacman -S --noconfirm dos2unix [[ -x "$(command -v curl)" ]] || sudo pacman -S --noconfirm curl [[ -x "$(command -v unzip)" ]] || sudo pacman -S --noconfirm unzip [[ -x "$(command -v virtualenv)" ]] || sudo pacman -S --noconfirm python-virtualenv } install\\\_fedora() { sudo dnf update -y [[ -x "$(command -v git)" ]] || sudo dnf install -y git [[ -x "$(command -v python3)" ]] || sudo dnf install -y python3 [[ -x "$(command -v pip3)" ]] || sudo dnf install -y python3-pip [[ -x "$(command -v dos2unix)" ]] || sudo dnf install -y dos2unix [[ -x "$(command -v curl)" ]] || sudo dnf install -y curl [[ -x "$(command -v unzip)" ]] || sudo dnf install -y unzip } if [[ "$OSTYPE" == "linux-gnu"\\\* ]]; then if command -v apt-get &>/dev/null; then install\\\_debian elif command -v pacman &>/dev/null; then install\\\_arch elif command -v dnf &>/dev/null; then install\\\_fedora else echo "Unsupported Linux distribution" exit 1 fi else echo "Unsupported OS" exit 1 fi if [[ "$OSTYPE" != "linux-gnu"\\\* || ! "$(command -v pacman)" ]]; then pip3 show virtualenv &>/dev/null || pip3 install virtualenv fi if [[ "$OSTYPE" == "linux-gnu"\\\* ]]; then if command -v apt-get &>/dev/null; then sudo apt install -y adb fastboot elif command -v pacman &>/dev/null; then sudo pacman -S --noconfirm android-tools elif command -v dnf &>/dev/null; then sudo dnf install -y android-tools fi fi # Setup virtualenv and install requirements python3 -m venv venv source venv/bin/activate chmod +x mtkbootcmd.py # Download mtkclient REPO\\\_URL="https\://github.com/AgentFabulous/mtkclientt" REPO\\\_NAME=$(basename "$REPO\\\_URL" .git) git clone "$REPO\\\_URL" cd "$REPO\\\_NAME" || exit pip3 install -r requirements.txt rm -f frp.bin read -p "[\\\*] Power off your device, press ENTER plug it into your PC" # Read FRP sudo python3 mtk r frp frp.bin sudo chown $USER frp.bin LAST\\\_BYTE=$(xxd -p -l 1 -s -1 frp.bin) if [[ "$LAST\\\_BYTE" == "00" ]]; then printf '\x01' | dd of=frp.bin bs=1 seek=$(($(stat -c%s frp.bin) - 1)) conv=notrunc fi # Write FRP sudo python3 mtk w frp frp.bin read -p "[\\\*] Unplug your device, press ENTER, plug it back in" cd .. sudo ./mtkbootcmd.py FASTBOOT echo "[\\\*] Waiting for fastboot..." while ! fastboot devices | grep -q "fastboot"; do sleep 1 done fastboot flashing unlock fastboot -w fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img fastboot reboot-fastboot fastboot flash system system.img fastboot reboot mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ LAST\\\_BYTE=$(xxd -p -l 1 -s -1 frp.bin) if [[ "$LAST\\\_BYTE" == "00" ]]; then printf '\x01' | dd of=frp.bin bs=1 seek=$(($(stat -c%s frp.bin) - 1)) conv=notrunc fi 1+0 records in 1+0 records out 1 byte copied, 8.9455e-05 s, 11.2 kB/s mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ python3 mtk w frp frp.bin MTK Flash/Exploit Client Public V2.0.0 Beta (c) B.Kerler 2018-2023 DAXFlash - HW-CODE : 0x766 DAXFlash - HWSUB-CODE : 0x8A00 DAXFlash - HW-VERSION : 0xCA00 DAXFlash - SW-VERSION : 0x0 DAXFlash - CHIP-EVOLUTION : 0x0 DAXFlash - DA-VERSION : 1.0 Progress: |██████████████████████████████████████████████████| 100.0% Write (Sector 0x800 of 0x800, ) 3.57 MB/s Wrote frp.bin to sector 44096 with sector count 2048. mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ cd .. r1\\\_escape on  main via 🐍 v3.13.2 ❯ ./mtkbootcmd.py FASTBOOT Listening for ports! Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface HWID: USB VID\\\:PID=0E8D:2000 LOCATION=3-1:1.0 Got port: /dev/ttyACM0 Initializing port /dev/ttyACM0 b'FASTBOOT' cmd sent r1\\\_escape on  main via 🐍 v3.13.2 took 6s ❯ while ! fastboot devices | grep -q "fastboot"; do sleep 1 done r1\\\_escape on  main via 🐍 v3.13.2 ❯ fastboot devices 919109A491600019115B fastboot r1\\\_escape on  main via 🐍 v3.13.2 ❯ fastboot flashing unlock (bootloader) Start unlock flow OKAY [ 3.121s] Finished. Total time: 3.121s r1\\\_escape on  main via 🐍 v3.13.2 took 3s ❯ fastboot -w Erasing 'userdata' OKAY [ 1.454s] /usr/lib/android-sdk/platform-tools/mke2fs failed with status 1 fastboot: error: Cannot generate image for userdata r1\\\_escape on  main via 🐍 v3.13.2 ❯ fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img Rewriting vbmeta struct at offset: 0 Sending 'vbmeta\\\_b' (4 KB) OKAY [ 0.005s] Writing 'vbmeta\\\_b' OKAY [ 0.002s] Finished. Total time: 0.011s r1\\\_escape on  main via 🐍 v3.13.2 ❯ ls mtkbootcmd.py mtkclient r1.ps1 r1.sh README.md vbmeta.img r1\\\_escape on  main via 🐍 v3.13.2 ❯ fastboot reboot-fastboot Rebooting into fastboot OKAY [ 0.001s] < waiting for any device > Finished. Total time: 23.013s r1\\\_escape on  main via 🐍 v3.13.2 took 23s ❯ ls mtkbootcmd.py mtkclient r1.ps1 r1.sh README.md vbmeta.img r1\\\_escape on  main via 🐍 v3.13.2 ❯ cd .. code/others/rabbit-r1 ❯ find . -name system.img code/others/rabbit-r1 ❯ fastboot flashing unlock < waiting for any device > ^C code/others/rabbit-r1 took 54s ❯ fastboot flashing unlock code/others/rabbit-r1 ❯ python3 r1\\\_escape/mtkbootcmd.py FASTBOOT Listening for ports! Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface HWID: USB VID\\\:PID=0E8D:2000 LOCATION=3-1:1.0 Got port: /dev/ttyACM0 Initializing port /dev/ttyACM0 b'FASTBOOT' cmd sent code/others/rabbit-r1 ❯ fastboot devices 919109A491600019115B fastboot code/others/rabbit-r1 ❯ fastboot flash boot\\\_1 ./rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/boot.img Warning: skip copying boot\\\_1 image avb footer (boot\\\_1 partition size: 0, boot\\\_1 image size: 33554432). Sending 'boot\\\_1' (32768 KB) OKAY [ 1.245s] Writing 'boot\\\_1' FAILED (remote: 'This partition doesn't exist') fastboot: error: Command failed code/others/rabbit-r1 ❯ fastboot flash boot\\\_a ./rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/boot.img Sending 'boot\\\_a' (32768 KB) OKAY [ 1.198s] Writing 'boot\\\_a' OKAY [ 0.430s] Finished. Total time: 1.631s code/others/rabbit-r1 ❯ fastboot flash boot\\\_b ./rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/boot.img Sending 'boot\\\_b' (32768 KB) OKAY [ 1.206s] Writing 'boot\\\_b' OKAY [ 0.445s] Finished. Total time: 1.653s code/others/rabbit-r1 ❯ fastboot --disable-verity --disable-verification flash vbmeta\\\_a ./rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/vbmeta.img Rewriting vbmeta struct at offset: 0 Sending 'vbmeta\\\_a' (4 KB) OKAY [ 0.005s] Writing 'vbmeta\\\_a' OKAY [ 0.002s] Finished. Total time: 0.010s code/others/rabbit-r1 ❯ fastboot --disable-verity --disable-verification flash vbmeta\\\_b ./rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/vbmeta.img Rewriting vbmeta struct at offset: 0 Sending 'vbmeta\\\_b' (4 KB) OKAY [ 0.005s] Writing 'vbmeta\\\_b' OKAY [ 0.002s] Finished. Total time: 0.008s code/others/rabbit-r1 ❯ fastboot --disable-verity --disable-verification flash vbmeta\\\_system\\\_a ./rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/vbmeta\\\_system.img Sending 'vbmeta\\\_system\\\_a' (4 KB) OKAY [ 0.005s] Writing 'vbmeta\\\_system\\\_a' OKAY [ 0.002s] Finished. Total time: 0.010s code/others/rabbit-r1 ❯ fastboot --disable-verity --disable-verification flash vbmeta\\\_system\\\_b ./rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/vbmeta\\\_system.img Sending 'vbmeta\\\_system\\\_b' (4 KB) OKAY [ 0.005s] Writing 'vbmeta\\\_system\\\_b' OKAY [ 0.002s] Finished. Total time: 0.010s code/others/rabbit-r1 ❯ fastboot --disable-verity --disable-verification flash vbmeta\\\_vendor\\\_a ./rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/vbmeta\\\_vendor.img Sending 'vbmeta\\\_vendor\\\_a' (4 KB) OKAY [ 0.005s] Writing 'vbmeta\\\_vendor\\\_a' OKAY [ 0.002s] Finished. Total time: 0.009s code/others/rabbit-r1 ❯ fastboot --disable-verity --disable-verification flash vbmeta\\\_vendor\\\_b ./rabbit\\\_OS\\\_v0.8.293\\\_20250516110545/vbmeta\\\_vendor.img Sending 'vbmeta\\\_vendor\\\_b' (4 KB) OKAY [ 0.005s] Writing 'vbmeta\\\_vendor\\\_b' OKAY [ 0.002s] Finished. Total time: 0.009s code/others/rabbit-r1 ❯ fastboot reboot fastboot Rebooting into fastboot OKAY [ 0.001s] < waiting for any device > ^C code/others/rabbit-r1 took 31s ❯ fastboot reboot fastboot < waiting for any device > ^C code/others/rabbit-r1 took 21s ❯ python3 r1\\\_escape/mtkbootcmd.py FASTBOOT Listening for ports! Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface HWID: USB VID\\\:PID=0E8D:2000 LOCATION=3-1:1.0 Got port: /dev/ttyACM0 Initializing port /dev/ttyACM0 b'FASTBOOT' cmd sent code/others/rabbit-r1 took 2s ❯ fastboot reboot fastboot Rebooting into fastboot OKAY [ 0.001s] < waiting for any device > ^[[A^[[A^C code/others/rabbit-r1 took 2s ❯ python3 r1\\\_escape/mtkbootcmd.py FASTBOOT Listening for ports! Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface HWID: USB VID\\\:PID=0E8D:2000 LOCATION=3-1:1.0 Got port: /dev/ttyACM0 Initializing port /dev/ttyACM0 b'FASTBOOT' cmd sent code/others/rabbit-r1 ❯ fastboot reboot fastbootcd mtk code/others/rabbit-r1 ❯ cd .. code/others/rabbit-r1 ❯ ls \\\_\\\_MACOSX r1\\\_escape rabbit\\\_OS\\\_v0.8.293\\\_20250516110545 code/others/rabbit-r1 ❯ find . -name mtkclient ./r1\\\_escape/mtkclient ./r1\\\_escape/mtkclient/mtkclient code/others/rabbit-r1 ❯ cd r1\\\_escape/mtkclient mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ ls frp.bin logs mtk mtkclient mtk\\\_gui mtk\\\_standalone.spec README.md run.example vbmeta.img.empty LICENSE MANIFEST.in mtk.bat mtk\\\_console.spec mtk\\\_gui.bat pyproject.toml requirements.txt stage2 mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ python3 mtk r frp frp.bin MTK Flash/Exploit Client Public V2.0.0 Beta (c) B.Kerler 2018-2023 Preloader - Status: Waiting for PreLoader VCOM, please reconnect mobile to brom mode Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. ........... Port - Hint: Power off the phone before connecting. For brom mode, press and hold vol up, vol dwn, or all hw buttons and connect usb. For preloader mode, don't press any hw button and connect usb. If it is already connected and on, hold power for 10 seconds to reset. Port - Device detected :) Preloader - CPU: MT6765/MT8768t(Helio P35/G35) Preloader - HW version: 0x0 Preloader - WDT: 0x10007000 Preloader - Uart: 0x11002000 Preloader - Brom payload addr: 0x100a00 Preloader - DA payload addr: 0x201000 Preloader - CQ\\\_DMA addr: 0x10212000 Preloader - Var1: 0x25 Preloader - Disabling Watchdog... Preloader - HW code: 0x766 Preloader - Target config: 0x0 Preloader - SBC enabled: False Preloader - SLA enabled: False Preloader - DAA enabled: False Preloader - SWJTAG enabled: False Preloader - EPP\\\_PARAM at 0x600 after EMMC\\\_BOOT/SDMMC\\\_BOOT: False Preloader - Root cert required: False Preloader - Mem read auth: False Preloader - Mem write auth: False Preloader - Cmd 0xC8 blocked: False Preloader - Get Target info Preloader - HW subcode: 0x8a00 Preloader - HW Ver: 0xca00 Preloader - SW Ver: 0x0 Preloader - ME\\\_ID: 55C0B1FC67D69E5E1CD382EA8780F8B7 Preloader - SOC\\\_ID: 3DCB309F2C158F3FE2D1480E8E63B9CAA15C619AD66576D325D3DEC081CBFD71 DA\\\_handler - Device is unprotected. DA\\\_handler - Device is in Preloader-Mode. DAXFlash - Uploading xflash stage 1 from MTK\\\_DA\\\_V5.bin xflashext - Patching da1 ... Mtk - Patched "Patched loader msg" in preloader Mtk - Patched "hash\\\_check" in preloader xflashext xflashext - [LIB]: Error on patching da1 version check... Mtk - Patched "Patched loader msg" in preloader Mtk - Patched "get\\\_vfy\\\_policy" in preloader xflashext - Patching da2 ... xflashext - DA version anti-rollback patched DAXFlash - Successfully uploaded stage 1, jumping .. Preloader - Jumping to 0x200000 Preloader - Jumping to 0x200000: ok. DAXFlash - Successfully received DA sync DAXFlash - Uploading stage 2... DAXFlash - Upload data was accepted. Jumping to stage 2... DAXFlash - Successfully uploaded stage 2 DAXFlash - EMMC FWVer: 0x0 DAXFlash - EMMC ID: DV6DAB DAXFlash - EMMC CID: 150100445636444142025c10dc0d291f DAXFlash - EMMC Boot1 Size: 0x400000 DAXFlash - EMMC Boot2 Size: 0x400000 DAXFlash - EMMC GP1 Size: 0x0 DAXFlash - EMMC GP2 Size: 0x0 DAXFlash - EMMC GP3 Size: 0x0 DAXFlash - EMMC GP4 Size: 0x0 DAXFlash - EMMC RPMB Size: 0x1000000 DAXFlash - EMMC USER Size: 0x1d1ec00000 DAXFlash - HW-CODE : 0x766 DAXFlash - HWSUB-CODE : 0x8A00 DAXFlash - HW-VERSION : 0xCA00 DAXFlash - SW-VERSION : 0x0 DAXFlash - CHIP-EVOLUTION : 0x0 DAXFlash - DA-VERSION : 1.0 DAXFlash - Extensions were accepted. Jumping to extensions... DAXFlash - DA Extensions successfully added DA\\\_handler - Requesting available partitions .... DA\\\_handler - Dumping partition "frp" Progress: |██████████████████████████████████████████████████| 100.0% Read (Sector 0x800 of 0x800, ) 3.61 MB/s DA\\\_handler - Dumped sector 44096 with sector count 2048 as frp.bin. mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 took 23s ❯ fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ cd .. r1\\\_escape on  main via 🐍 v3.13.2 ❯ ls mtkbootcmd.py mtkclient r1.ps1 r1.sh README.md vbmeta.img r1\\\_escape on  main via 🐍 v3.13.2 ❯ cat r1.sh \\#!/bin/bash install\\\_debian() { sudo apt update [[ -x "$(command -v git)" ]] || sudo apt install -y git [[ -x "$(command -v python3)" ]] || sudo apt install -y python3 [[ -x "$(command -v pip3)" ]] || sudo apt install -y python3-pip [[ -x "$(command -v dos2unix)" ]] || sudo apt install -y dos2unix [[ -x "$(command -v curl)" ]] || sudo apt install -y curl [[ -x "$(command -v unzip)" ]] || sudo apt install -y unzip } install\\\_arch() { sudo pacman -Sy --noconfirm [[ -x "$(command -v git)" ]] || sudo pacman -S --noconfirm git [[ -x "$(command -v python3)" ]] || sudo pacman -S --noconfirm python [[ -x "$(command -v dos2unix)" ]] || sudo pacman -S --noconfirm dos2unix [[ -x "$(command -v curl)" ]] || sudo pacman -S --noconfirm curl [[ -x "$(command -v unzip)" ]] || sudo pacman -S --noconfirm unzip [[ -x "$(command -v virtualenv)" ]] || sudo pacman -S --noconfirm python-virtualenv } install\\\_fedora() { sudo dnf update -y [[ -x "$(command -v git)" ]] || sudo dnf install -y git [[ -x "$(command -v python3)" ]] || sudo dnf install -y python3 [[ -x "$(command -v pip3)" ]] || sudo dnf install -y python3-pip [[ -x "$(command -v dos2unix)" ]] || sudo dnf install -y dos2unix [[ -x "$(command -v curl)" ]] || sudo dnf install -y curl [[ -x "$(command -v unzip)" ]] || sudo dnf install -y unzip } if [[ "$OSTYPE" == "linux-gnu"\\\* ]]; then if command -v apt-get &>/dev/null; then install\\\_debian elif command -v pacman &>/dev/null; then install\\\_arch elif command -v dnf &>/dev/null; then install\\\_fedora else echo "Unsupported Linux distribution" exit 1 fi else echo "Unsupported OS" exit 1 fi if [[ "$OSTYPE" != "linux-gnu"\\\* || ! "$(command -v pacman)" ]]; then pip3 show virtualenv &>/dev/null || pip3 install virtualenv fi if [[ "$OSTYPE" == "linux-gnu"\\\* ]]; then if command -v apt-get &>/dev/null; then sudo apt install -y adb fastboot elif command -v pacman &>/dev/null; then sudo pacman -S --noconfirm android-tools elif command -v dnf &>/dev/null; then sudo dnf install -y android-tools fi fi # Setup virtualenv and install requirements python3 -m venv venv source venv/bin/activate chmod +x mtkbootcmd.py # Download mtkclient REPO\\\_URL="https\://github.com/AgentFabulous/mtkclientt" REPO\\\_NAME=$(basename "$REPO\\\_URL" .git) git clone "$REPO\\\_URL" cd "$REPO\\\_NAME" || exit pip3 install -r requirements.txt rm -f frp.bin read -p "[\\\*] Power off your device, press ENTER plug it into your PC" # Read FRP sudo python3 mtk r frp frp.bin sudo chown $USER frp.bin LAST\\\_BYTE=$(xxd -p -l 1 -s -1 frp.bin) if [[ "$LAST\\\_BYTE" == "00" ]]; then printf '\x01' | dd of=frp.bin bs=1 seek=$(($(stat -c%s frp.bin) - 1)) conv=notrunc fi # Write FRP sudo python3 mtk w frp frp.bin read -p "[\\\*] Unplug your device, press ENTER, plug it back in" cd .. sudo ./mtkbootcmd.py FASTBOOT echo "[\\\*] Waiting for fastboot..." while ! fastboot devices | grep -q "fastboot"; do sleep 1 done fastboot flashing unlock fastboot -w fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img fastboot reboot-fastboot fastboot flash system system.img fastboot reboot r1\\\_escape on  main via 🐍 v3.13.2 ❯ cd mtkclient mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ LAST\\\_BYTE=$(xxd -p -l 1 -s -1 frp.bin) if [[ "$LAST\\\_BYTE" == "00" ]]; then printf '\x01' | dd of=frp.bin bs=1 seek=$(($(stat -c%s frp.bin) - 1)) conv=notrunc fi mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ python3 mtk w frp frp.bin MTK Flash/Exploit Client Public V2.0.0 Beta (c) B.Kerler 2018-2023 DAXFlash - HW-CODE : 0x766 DAXFlash - HWSUB-CODE : 0x8A00 DAXFlash - HW-VERSION : 0xCA00 DAXFlash - SW-VERSION : 0x0 DAXFlash - CHIP-EVOLUTION : 0x0 DAXFlash - DA-VERSION : 1.0 Progress: |██████████████████████████████████████████████████| 100.0% Write (Sector 0x800 of 0x800, ) 3.02 MB/s Wrote frp.bin to sector 44096 with sector count 2048. mtkclient on  main is 📦 v2.0.0 via 🐍 v3.13.2 ❯ cd .. r1\\\_escape on  main via 🐍 v3.13.2 ❯ ./mtkbootcmd.py FASTBOOT Listening for ports! Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface HWID: USB VID\\\:PID=0E8D:2000 LOCATION=3-1:1.0 Got port: /dev/ttyACM0 Initializing port /dev/ttyACM0 b'FASTBOOT' cmd sent r1\\\_escape on  main via 🐍 v3.13.2 took 9s ❯ fastboot flashing unlock (bootloader) Start unlock flow OKAY [ 3.033s] Finished. Total time: 3.033s r1\\\_escape on  main via 🐍 v3.13.2 took 3s ❯ fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img Rewriting vbmeta struct at offset: 0 Sending 'vbmeta\\\_a' (4 KB) OKAY [ 0.005s] Writing 'vbmeta\\\_a' OKAY [ 0.002s] Finished. Total time: 0.008s r1\\\_escape on  main via 🐍 v3.13.2 ❯ fastboot reboot-fastboot Rebooting into fastboot OKAY [ 0.001s] < waiting for any device > ^[[A^C r1\\\_escape on  main via 🐍 v3.13.2 took 37s ❯ fastboot -w < waiting for any device > ^C r1\\\_escape on  main via 🐍 v3.13.2 took 4s ❯ ./mtkbootcmd.py FASTBOOT Listening for ports! Found /dev/ttyACM0 with description: MT65xx Preloader - CDC ACM Communication Interface HWID: USB VID\\\:PID=0E8D:2000 LOCATION=3-1:1.0 Got port: /dev/ttyACM0 Initializing port /dev/ttyACM0 b'FASTBOOT' cmd sent r1\\\_escape on  main via 🐍 v3.13.2 took 11s ❯ fastboot -w Erasing 'userdata' OKAY [ 0.320s] /usr/lib/android-sdk/platform-tools/mke2fs failed with status 1 fastboot: error: Cannot generate image for userdata r1\\\_escape on  main via 🐍 v3.13.2 ❯ fastboot flashing unlock (bootloader) Start unlock flow OKAY [ 3.033s] Finished. Total time: 3.033s r1\\\_escape on  main via 🐍 v3.13.2 took 3s ❯ fastboot -w Erasing 'userdata' OKAY [ 0.319s] /usr/lib/android-sdk/platform-tools/mke2fs failed with status 1 fastboot: error: Cannot generate image for userdata r1\\\_escape on  main via 🐍 v3.13.2 ❯ fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img Rewriting vbmeta struct at offset: 0 Sending 'vbmeta\\\_a' (4 KB) OKAY [ 0.005s] Writing 'vbmeta\\\_a' OKAY [ 0.002s] Finished. Total time: 0.009s r1\\\_escape on  main via 🐍 v3.13.2 ❯ fastboot reboot-fastboot Rebooting into fastboot OKAY [ 0.001s] < waiting for any device > pwd^C r1\\\_escape on  main via 🐍 v3.13.2 took 3m ❯ pwd /home/manuel/code/others/rabbit-r1/r1\\\_escape r1\\\_escape on  main via 🐍 v3.13.2 \\----

<details><summary>💭 Thinking</summary>

**Preparing the guide**

I’m researching the device’s current Ubuntu Touch feasibility, the cited repositories, and the recovery logs. I’ll then structure a textbook-style Markdown guide and matching PDF with cautious, reproducible steps and clear warnings.

**Prepared the guide**

</details>

I’ll turn your terminal history into a state diagnosis first, then trace the verified Rabbit R1 boot/AVB flow and the current Ubuntu Touch porting path. The final deliverables will be a textbook-style `.md` plus a rendered PDF, with recovery checkpoints and commands separated from conceptual explanation.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Read PDF creation guidelines and DOCX skill instructions**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/get_repo","args":{"repository_full_name":"jonathanprocter/rabbit-r1-deverity-recovery"}}
```

<details><summary>💭 Thinking</summary>

**Reviewed Rabbit R1 recovery documentation and verified repository details**

</details>

Your logs already show one important transition: the FRP edit changed `unlock_ability` from `0` to a working bootloader unlock, and subsequent writes to `boot_a`, `boot_b`, and the vbmeta partitions succeeded. The remaining problem is no longer “how do I unlock it”; it is “what exact boot-chain/slot/verity state did those mixed recovery steps leave behind, and what base should an Ubuntu Touch port use?”

```json
{"system1_search_query":[{"q":"site:docs.ubports.com porting Ubuntu Touch Halium 13 Android 13 2026"},{"q":"site:devices.ubuntu-touch.io rabbit r1 Ubuntu Touch"},{"q":"site:ubports.com Ubuntu Touch rabbit r1"},{"q":"site:docs.halium.org porting guide Android 13 Halium 13"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 4 websites**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"ubports/installer-configs","path":"v2/devices/r1.yml"}}
```

<details><summary>💭 Thinking</summary>

**Fetched installer configuration and recovery steps before UBports installation**

</details>

```json
{"system2_search_query":[{"q":"github MinatiScape ubtouch-on-r1 release v0.2 Rabbit R1 Ubuntu Touch"},{"q":"site:github.com/MinatiScape/ubtouch-on-r1 Rabbit R1 Ubuntu Touch v0.2"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 11 websites**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/get_repo","args":{"repository_full_name":"rabbit-hmi-oss/firmware"}}
```

<details><summary>💭 Thinking</summary>

**Inspected Rabbit firmware repository and fetched its README**

</details>

```json
{"system1_search_query":[{"q":"site:github.com/rabbit-hmi-oss/firmware/releases rabbitOS v0.8.293"},{"q":"site:github.com/rabbit-hmi-oss/firmware \"v0.8.293\""}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Refining the recovery path**

I’m distinguishing the stock-repair workflow from Ubuntu Touch installation. The most reliable next step is confirming the phone’s bootloader state and restoring a consistent stock base before attempting the community Ubuntu Touch port.

</details>

```json
{"system2_search_query":[{"q":"site:android.googlesource.com platform system core fastboot mke2fs format userdata fastboot"},{"q":"site:android.googlesource.com fastboot mke2fs failed with status 1 format partition"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

The key result is better than the original premise: **you do not need to create an Ubuntu Touch port for the R1.** UBports now has a Rabbit R1 target and installer configuration. The recovery goal is therefore: restore a coherent **unlocked stock rabbitOS v0.8 base**, clear any persistent R1-specific verity error only if it survives a clean stock flash, then let the UBports installer replace `boot`, `vbmeta`, and `super`.

```unknown
bash -lc mkdir -p /mnt/data/rabbit_r1_textbook && cat > /mnt/data/rabbit_r1_textbook/rabbit-r1-dm-verity-to-ubuntu-touch.md <<'EOF'
# Rabbit R1: From `dm-verity corruption` to Ubuntu Touch

## A practical textbook on MediaTek boot modes, Android Verified Boot, A/B slots, dynamic partitions, recovery, and the supported UBports path

**Edition:** August 7, 2026  
**Target device:** rabbit r1 (`r1`, MediaTek MT6765 / Helio P35)  
**Starting point:** bootloader now unlocks successfully; stock `boot`/`vbmeta*` images have been flashed in several combinations; `fastbootd` has been unreliable; the device reports or has reported `dm-verity corruption`.

> **Scope and risk**  
> This is a device-recovery and OS-installation guide, not a generic “run these commands blindly” recipe. Several commands erase user data or rewrite boot-critical partitions. Read the whole recovery chapter before executing the destructive blocks. Keep the bootloader **unlocked** throughout the Ubuntu Touch path. Never relock while modified or verification-disabled images are installed.

---

## Contents

1. The short answer
2. What the Rabbit R1 actually is
3. The boot chain: from power-on to Android/Linux userspace
4. Android Verified Boot, AVB, `vbmeta`, and `dm-verity`
5. Why “dm-verity corruption” can persist
6. A/B slots and why slot state matters
7. `super`, dynamic partitions, bootloader fastboot, and fastbootd
8. MediaTek BROM, preloader, `mtkclient`, and `mtkbootcmd.py`
9. What the FRP edit did in `r1_escape`
10. Reading your terminal history as a state machine
11. Host-side problems in your log: Python, `sudo`, USB, and `mke2fs`
12. What state your R1 is probably in now
13. Recovery strategy: establish a coherent stock base first
14. Non-destructive inspection checklist
15. Manual stock recovery path for your v0.8.293 files
16. Slot recovery and first stock boot
17. Last-resort R1-specific `seccfg` dm-verity recovery
18. Why you do **not** need to port Ubuntu Touch yourself
19. How Ubuntu Touch on the R1 is architected
20. Installing Ubuntu Touch with the UBports Installer
21. Why the Ubuntu Touch path does not depend on your failing fastbootd step
22. After Ubuntu Touch boots
23. Troubleshooting matrix
24. Command reference
25. Glossary
26. Sources and further reading

---

# 1. The short answer

Your logs show that the most difficult prerequisite has already been crossed: you changed the R1's unlock permission state, entered bootloader fastboot, and `fastboot flashing unlock` returned `OKAY`. After that, writes to `boot_a`, `boot_b`, and the AVB metadata partitions were accepted.

The correct route from here is **not** to keep following the `r1_escape` AOSP/CipherOS flow and it is **not** to build a new Ubuntu Touch port. The rabbit r1 already has a UBports device target and an installer configuration. UBports lists the R1 as an installer-supported device and the installer config names the device `r1`.[^ubports-device][^installer-config]

The practical sequence is:

1. Stop mixing stock images, `r1_escape`'s disabled `vbmeta`, and unrelated custom-ROM instructions.
2. Inspect the current slot and lock state without writing anything.
3. Restore one coherent **stock rabbitOS v0.8** boot chain and `super` image while keeping the bootloader unlocked.
4. Boot stock once. If stock still produces `dm-verity corruption`, diagnose the R1-specific persistent `seccfg` state described by the community recovery write-up; do not jump to this step before a clean stock test.[^deverity-recovery]
5. Once stock v0.8 boots and the bootloader is unlocked, run the UBports Installer as a normal user, select **rabbit r1**, leave **Bootstrap** enabled, select the current stable channel offered by the installer, and wipe userdata when switching from Android.
6. Let the installer flash its own `vbmeta`, `boot`, and complete `super` image, boot UBports recovery, and install the Ubuntu Touch system image.[^installer-config]
7. After the first successful Ubuntu Touch boot, update through **System Settings -> Updates**. Rabbit R1 is included in the Ubuntu Touch 24.04 support list.[^ut-2404]

A critical distinction: **the supported R1 Ubuntu Touch bootstrap flashes a complete `super` image from bootloader fastboot. It does not require you to make the `fastboot reboot-fastboot` step from the CipherOS workflow work first.**[^installer-config]

---

# 2. What the Rabbit R1 actually is

For recovery purposes, treat the R1 as a small MediaTek Android device with unusual controls, not as a fundamentally new computer architecture. The UBports device database identifies it as an ARM64 device based on the MediaTek Helio P35 family, with Android/rabbitOS as the vendor base.[^ubports-device]

This matters because nearly every concept in your terminal log comes from the Android/MediaTek boot stack:

- MediaTek **BROM** and **preloader** run before Android's normal bootloader interface.
- Android's bootloader exposes **fastboot**.
- Android Verified Boot (**AVB**) authenticates the partitions that make up the operating system.
- Large read-only filesystems are protected at runtime by **dm-verity**.
- The device uses **A/B slot metadata**, so bootability is not determined only by the contents of `boot.img`.
- Android's `system`, `vendor`, and related logical partitions live inside a physical **`super`** partition.
- Ubuntu Touch on this device reuses the Android hardware enablement through **Halium** instead of replacing every vendor component with mainline Linux drivers.

A useful mental model is:

```text
Power button / USB insertion
          |
          v
+-------------------+
| MediaTek Boot ROM |
|       BROM        |
+-------------------+
          |
          v
+-------------------+
| MTK Preloader     |  <-- /dev/ttyACM0, VID:PID 0e8d:2000 in your log
+-------------------+
          |
          v
+-------------------+
| Android bootloader|  <-- bootloader fastboot
|  + AVB policy     |
|  + A/B slot logic |
+-------------------+
          |
          +---------------------------+
          |                           |
          v                           v
+-------------------+       +--------------------+
| boot_a / boot_b   |       | recovery/fastbootd |
| kernel + ramdisk  |       | userspace fastboot |
+-------------------+       +--------------------+
          |
          v
+-------------------+
| super             |
| system/vendor/... |
+-------------------+
          |
          v
+-------------------+
| Android / Halium  |
| or Ubuntu Touch   |
+-------------------+
```

---

# 3. The boot chain: from power-on to userspace

A “boot failure” can occur at several distinct layers. The symptoms look similar from the outside, but the fixes are different.

## 3.1 BROM and preloader

MediaTek chips contain immutable boot ROM code. The preloader is the next vendor-specific stage. In your log, `mtkclient` recognized the chip as `MT6765/MT8768t` and reported the target as unprotected. That is why `mtkclient` could upload its download-agent stages and read/write raw eMMC partitions.

This layer is below normal Android fastboot. It is the reason you can recover a device that cannot boot Android at all.

## 3.2 Android bootloader

The Android bootloader performs several jobs:

- expose bootloader fastboot;
- decide which A/B slot to boot;
- load `boot`, device-tree, and other boot-critical images;
- enforce Android Verified Boot policy;
- pass boot parameters such as the slot suffix and dm-verity mode into the kernel.

The orange unlocked-device warning belongs to this layer. An unlocked bootloader changes trust policy; it does not, by itself, guarantee that the images form a coherent system.

## 3.3 Kernel and early userspace

`boot.img` contains the Linux kernel and ramdisk components needed for early boot. A correct `boot.img` can still fail if its expected vendor/system partitions do not match, if AVB descriptors are inconsistent, or if the bootloader has marked the slot unbootable.

## 3.4 The Android logical partitions

Modern Android devices group logical partitions such as `system`, `vendor`, `product`, and others inside `super`. Android calls these **dynamic partitions**.[^dynamic-partitions]

This is the layer that a custom Android GSI, CipherOS, or the R1 Ubuntu Touch bootstrap changes most dramatically.

---

# 4. Android Verified Boot, AVB, `vbmeta`, and `dm-verity`

The words in your error message are often confused because several integrity mechanisms work together.

## 4.1 Verified Boot is the overall trust chain

Android Verified Boot aims to ensure that executable code and read-only system data come from an expected, authenticated build. Android 8 and newer use AVB 2.0 as the reference implementation.[^avb]

Small boot-critical partitions can be verified by hashing the entire image before execution. Large filesystem partitions are generally verified using hash trees while blocks are read.[^verified-boot]

## 4.2 What `vbmeta` is

`vbmeta` is metadata that describes what should be trusted and how. It may contain or chain to descriptors for other partitions. On the R1 you have seen:

```text
vbmeta_a / vbmeta_b
vbmeta_system_a / vbmeta_system_b
vbmeta_vendor_a / vbmeta_vendor_b
```

Conceptually:

```text
hardware / bootloader root of trust
              |
              v
        +-------------+
        |   vbmeta    |
        +-------------+
           /       \
          v         v
  vbmeta_system   vbmeta_vendor
       |               |
       v               v
 system/product/...   vendor/...
```

Flashing a stock `boot.img` while leaving modified or mismatched `vbmeta` metadata can still produce a boot failure. Conversely, flashing verification-disabled `vbmeta` while later relocking the bootloader creates a different trust contradiction: a locked device expects a valid trusted chain but sees content intended for an unlocked development state.

## 4.3 What `--disable-verity --disable-verification` actually means

When fastboot is asked to flash a `vbmeta` image with these options, it modifies AVB flags in the image it sends. In your log, fastboot explicitly printed:

```text
Rewriting vbmeta struct at offset: 0
```

That is evidence that the data written was **not byte-for-byte the original stock vbmeta image**, even though the input filename was the stock file.

This can be useful for development, but it is a poor diagnostic state when trying to answer “does clean stock AVB boot correctly?” For that test, flash the original stock `vbmeta*` files **without** the disable flags while leaving the bootloader unlocked.

## 4.4 What dm-verity is

`dm-verity` is a Linux device-mapper target that checks filesystem blocks against a cryptographic hash tree as they are read. Android uses it for large verified partitions.[^dm-verity]

A simplified tree:

```text
trusted root hash
       |
   +---+---+
   |       |
 hash    hash
 /  \    /  \
D0  D1  D2  D3    <- data blocks
```

Change a data block and the chain to the trusted root no longer matches.

---

# 5. Why `dm-verity corruption` can persist

AOSP documents a managed dm-verity error flow in which the bootloader can switch the next boot into `eio` mode after a verification failure. In `eio` mode, corrupted reads return I/O errors rather than immediately restarting; the bootloader is expected to return to normal mode after a new valid OS is installed.[^verified-boot]

The Rabbit R1 community recovery write-up reports a device-specific complication: on at least the investigated R1 build, a dm-verity error state remained persisted in the MediaTek `seccfg` partition even after stock images were restored. The bootloader continued passing:

```text
androidboot.veritymode=eio
androidboot.veritymode.managed=yes
```

and recreated the managed-verity state until the relevant authenticated `seccfg` header state and persistent AVB record were corrected.[^deverity-recovery]

That does **not** mean every R1 showing `dm-verity corruption` needs a raw `seccfg` write. The correct diagnostic order is:

```text
clean stock images + unlocked bootloader
                |
                v
         Does stock boot?
          /            \
        yes             no
        |               |
        v               v
 proceed to UT     inspect slots + logs
                        |
                        v
              managed verity=eio persists?
                    /          \
                  no            yes
                  |              |
          fix ordinary         seccfg becomes
          image/slot issue     evidence-based
                               last resort
```

---

# 6. A/B slots and why slot state matters

A/B devices keep two bootable sets of slot-aware partitions. The active slot can fail several times and eventually be marked unbootable. Android's boot-control design exposes variables such as `current-slot`, `slot-successful`, `slot-unbootable`, and `slot-retry-count` through fastboot.[^ab-implement]

The important point is that **correct bytes are not sufficient**. A slot with valid images may still be skipped if metadata says it is unbootable.

Typical inspection:

```bash
fastboot getvar current-slot
fastboot getvar slot-count
fastboot getvar slot-successful:a
fastboot getvar slot-unbootable:a
fastboot getvar slot-retry-count:a
fastboot getvar slot-successful:b
fastboot getvar slot-unbootable:b
fastboot getvar slot-retry-count:b
```

AOSP specifies that setting a slot active should clear its unbootable state and reset its retry count.[^ab-updating]

Therefore the first recovery action for bad slot metadata is usually:

```bash
fastboot set_active a
```

and then inspect the variables again. The R1 community recovery notes additionally describe erasing `boot_para` and `para` when both slots had been “burned down” and ordinary slot reset behavior was insufficient. Treat that as a device-specific escalation, not as the first thing to do.[^deverity-recovery]

---

# 7. `super`, dynamic partitions, bootloader fastboot, and fastbootd

This distinction explains a large portion of your confusion.

## 7.1 `super` is a physical container

Android dynamic partitions place logical `system`, `vendor`, `product`, and related partitions inside a physical `super` partition.[^dynamic-partitions]

## 7.2 Bootloader fastboot versus fastbootd

**Bootloader fastboot** runs in the bootloader. **fastbootd** is a userspace fastboot implementation reached through the recovery/userspace boot path. AOSP introduced it so Android could safely manipulate dynamic logical partitions.[^fastbootd]

Check which one you are in:

```bash
fastboot getvar is-userspace
```

Interpretation:

```text
is-userspace: no   -> bootloader fastboot
is-userspace: yes  -> fastbootd
```

## 7.3 Why your `fastboot reboot-fastboot` hangs

AOSP describes `reboot fastboot` as a transition into userspace fastboot/recovery.[^fastbootd] If the device's recovery/userspace boot path is broken, mismatched, or unable to complete AVB/slot boot, the host can print:

```text
< waiting for any device >
```

because the bootloader fastboot USB interface disappeared but fastbootd never appeared.

This is exactly different from “fastboot itself is broken”: you repeatedly proved that bootloader fastboot works after sending `FASTBOOT` through the MediaTek preloader.

## 7.4 Why this is not a blocker for the supported Ubuntu Touch installer

The current UBports `r1` installer configuration downloads a Rabbit-R1-specific `boot.img`, a packaged `super.img`, and a `vbmeta.img`; in the bootstrap step it flashes the **physical `vbmeta`, `boot`, and `super` partitions** from bootloader fastboot, then reboots into UBports recovery for the system-image installation.[^installer-config]

In other words:

```text
CipherOS / generic system.img path
bootloader fastboot -> fastbootd -> flash logical system

Ubuntu Touch R1 installer path
bootloader fastboot -> flash whole super -> UBports recovery -> system-image install
```

Do not spend hours fixing fastbootd just because an unrelated custom-ROM guide needed it.

---

# 8. MediaTek BROM, preloader, `mtkclient`, and `mtkbootcmd.py`

Your R1 exposes several USB personalities during recovery. In your own log, `mtkbootcmd.py` found:

```text
MT65xx Preloader - CDC ACM Communication Interface
VID:PID = 0E8D:2000
/dev/ttyACM0
```

and wrote the ASCII string:

```text
FASTBOOT
```

The script is not “flashing fastboot.” It is asking the running MediaTek preloader to branch into the Android bootloader's fastboot mode.

`mtkclient` is lower-level. It talks to BROM/preloader, uploads MediaTek download-agent code, enumerates eMMC, and can read/write named partitions even when Android cannot boot.

That is why this pair is so useful:

```text
mtkclient     -> raw partition access / last-resort recovery
mtkbootcmd.py -> convenient preloader -> bootloader-fastboot transition
fastboot      -> normal unlocked bootloader flashing
```

For routine Ubuntu Touch installation, prefer normal fastboot and the UBports installer. Keep `mtkclient` as a recovery tool rather than the default installation mechanism.

---

# 9. What the FRP edit did in `r1_escape`

The current `r1_escape` script documents this sequence:[^r1-escape-script]

1. read the `frp` partition;
2. examine the final byte;
3. change a final `0x00` to `0x01`;
4. write `frp` back;
5. enter fastboot;
6. run `fastboot flashing unlock`.

Your terminal history demonstrates the effect directly:

```text
before FRP edit:
  fastboot flashing get_unlock_ability
  unlock_ability = 0

fastboot flashing unlock
  Unlock operation is not allowed
```

After the FRP edit and reconnect:

```text
fastboot flashing unlock
  Start unlock flow
  OKAY
```

So in this workflow the FRP edit is not “disabling dm-verity.” It is altering the device state that gates whether the bootloader unlock flow is permitted.

This distinction matters because three independent concepts were changing at once:

| Concept | Your action | Effect |
|---|---|---|
| Unlock permission | FRP final-byte edit | Allowed `fastboot flashing unlock` |
| Bootloader lock state | `fastboot flashing unlock` | Allowed protected partition writes |
| AVB enforcement metadata | flashing `vbmeta` with disable flags | Changed verification behavior |

Treat them as separate switches.

---

# 10. Reading your terminal history as a state machine

This chapter converts the long shell log into a smaller sequence of state transitions.

## 10.1 Initial fastboot command injection worked, but USB fastboot did not appear

You installed `pyserial`, then:

```text
python3 r1_escape/mtkbootcmd.py FASTBOOT
...
b'FASTBOOT' cmd sent
```

but `fastboot devices` initially returned nothing. That means “the serial command was written” and “the host successfully enumerated the next fastboot USB personality” were two separate events. Later runs did enumerate fastboot correctly.

## 10.2 Stock boot flashing failed because the device was locked

You tried:

```text
fastboot flash boot_a .../boot.img
```

and got:

```text
FAILED (remote: 'not allowed in locked state')
```

This is normal bootloader policy, not a bad `boot.img`.

## 10.3 The bootloader explicitly told you unlocking was disabled

You then saw:

```text
unlock_ability = 0
Unlock operation is not allowed
```

This was the central blocker that `r1_escape` addresses.

## 10.4 `sudo python3` used a different Python environment

You installed `pyusb` under your pyenv Python:

```text
/home/manuel/.pyenv/versions/3.13.2/...
```

but then ran:

```bash
sudo python3 mtk ...
```

which used the system/root Python environment and failed with:

```text
ModuleNotFoundError: No module named 'usb'
```

When you ran `python3 mtk ...` without `sudo`, the pyenv interpreter could import PyUSB and `mtkclient` worked.

This is a host Python environment issue, not a MediaTek issue.

## 10.5 The FRP edit succeeded

`mtkclient` dumped `frp`, you changed its final byte, and `mtkclient` wrote it back. After sending `FASTBOOT` again, the host saw:

```text
919109A491600019115B    fastboot
```

Then:

```text
fastboot flashing unlock
OKAY
```

The bootloader was now unlocked.

## 10.6 `fastboot -w` only partially succeeded

Your output was:

```text
Erasing 'userdata' OKAY
/usr/lib/android-sdk/platform-tools/mke2fs failed with status 1
fastboot: error: Cannot generate image for userdata
```

This has two stages:

1. the device accepted the **erase**;
2. the host failed to generate a fresh filesystem image for the subsequent **format** operation.

Android's fastboot build distributes filesystem-generation utilities such as `mke2fs` alongside fastboot because formatting can involve creating a filesystem image on the host before it is sent to the device.[^fastboot-mke2fs]

So the useful conclusion is not “userdata could not be erased.” It is “the erase happened, but this host fastboot package cannot currently finish the format step.”

For the stock-recovery test, your firmware package already includes `userdata.img`, so you can avoid relying on `fastboot -w`. For Ubuntu Touch, use a current supported UBports Installer and, if formatting still fails, fix/update the host platform-tools rather than repeatedly erasing the device.

## 10.7 You flashed several different `vbmeta` states

The history includes all of these patterns:

- `r1_escape/vbmeta.img` with disable flags;
- stock `vbmeta_a` and `vbmeta_b` with disable flags;
- stock `vbmeta_system_*` and `vbmeta_vendor_*`;
- later another flash of `r1_escape/vbmeta.img`.

This makes the current AVB state difficult to infer from filenames. A “clean stock test” must overwrite this ambiguity with one known set.

## 10.8 You restored stock `boot_a` and `boot_b`

These writes succeeded after unlocking. That is good, but `boot` is only one piece of the boot chain. You did not show a corresponding clean stock flash of the complete `super` filesystem in the provided history.

## 10.9 The fastbootd transition kept failing

After `fastboot reboot-fastboot`, bootloader fastboot disappeared and userspace fastboot did not enumerate. This is compatible with a broken userspace/recovery boot path. It does not invalidate the working preloader -> bootloader-fastboot path.

---

# 11. Host-side problems in your log: Python, `sudo`, USB, and `mke2fs`

Before doing more device writes, reduce host-side ambiguity.

## 11.1 Use one Python interpreter deliberately

From the R1 working directory:

```bash
cd /home/manuel/code/others/rabbit-r1/r1_escape
python3 -m venv .venv-r1
. .venv-r1/bin/activate
python -m pip install --upgrade pip
python -m pip install pyserial
python -m pip install -r mtkclient/requirements.txt
```

Confirm:

```bash
which python
python -V
python -c 'import serial, usb.core; print("serial+usb OK")'
```

If a command truly must run as root, invoke the same interpreter explicitly rather than silently switching Python installations:

```bash
sudo "$PWD/.venv-r1/bin/python" mtkclient/mtk --help
```

Prefer working udev permissions and unprivileged execution when possible; it avoids root-owned dumps and Python-environment mismatches.

## 11.2 Understand `cdc_acm`

For your `mtkbootcmd.py` method, the MediaTek preloader appears as a CDC ACM serial device (`/dev/ttyACM0`), so the `cdc_acm` driver is useful at that moment.

Some R1 custom-ROM notes remove `cdc_acm` later because of a device-specific USB-interface conflict with ADB. Do not generalize that into “cdc_acm must always be off.” Think in phases:

```text
Need preloader serial (/dev/ttyACM0) -> cdc_acm loaded
Need ordinary fastboot                -> unrelated to ttyACM serial driver
Need R1 ADB after a custom ROM        -> follow that ROM's USB guidance
```

## 11.3 Stop using `fastboot -w` as a diagnostic loop

The command is destructive and your host package has already shown that its formatting helper fails. Repeating it does not tell you anything new.

Use the stock `userdata.img` during stock recovery, or fix/update the host fastboot stack before relying on format operations.

---

# 12. What state your R1 is probably in now

Based strictly on the provided history, the strongest conclusions are:

**Known:**

- the FRP unlock gate was changed successfully;
- `fastboot flashing unlock` now succeeds;
- protected partition flashing is allowed;
- stock `boot.img` was written to both `boot_a` and `boot_b` at least once;
- stock AVB metadata was written to both slots, but top-level `vbmeta` was at times modified with disable flags;
- `r1_escape`'s own `vbmeta.img` was also flashed later;
- userdata was erased at least once, but host-side reformatting failed;
- bootloader fastboot is recoverable through `mtkbootcmd.py`;
- userspace fastboot/fastbootd is not reliably reached.

**Unknown from the history:**

- which slot is currently active;
- whether either slot is marked unbootable;
- the exact contents of the current physical `super` partition;
- the current top-level `vbmeta` flags on the active slot;
- whether `seccfg` still contains a persistent managed-verification error state;
- whether stock rabbitOS can boot if given one coherent, fully restored stock set.

This is why the next step should be **inspection**, not another guess-flash.

---

# 13. Recovery strategy: establish a coherent stock base first

The UBports R1 installer asks users to begin from stock rabbitOS v0.8 and an unlocked bootloader.[^ubports-device][^installer-config]

That requirement is technically sensible: the Ubuntu Touch port still depends on the device's Android-era firmware/vendor hardware support. A random mixture of CipherOS, AOSP GSI, stock boot images, and disabled AVB metadata is not a reliable base.

Use this escalation ladder:

```text
Level 0  Non-destructive inspection
   |
   v
Level 1  Clean stock v0.8 boot chain + super, bootloader stays unlocked
   |
   +---- stock boots -> go directly to UBports Installer
   |
   v
Level 2  Repair A/B slot metadata if necessary
   |
   +---- stock boots -> go to UBports Installer
   |
   v
Level 3  Capture evidence of persistent managed dm-verity=eio
   |
   v
Level 4  seccfg recovery (raw MTK write; last resort)
   |
   +---- stock boots -> go to UBports Installer
```

Do not relock the bootloader anywhere in this ladder.

---

# 14. Non-destructive inspection checklist

Start from your current working directory:

```bash
cd /home/manuel/code/others/rabbit-r1
```

Enter bootloader fastboot using the method that already works:

```bash
python3 r1_escape/mtkbootcmd.py FASTBOOT
```

Wait for:

```bash
fastboot devices -l
```

Then save a diagnostic snapshot:

```bash
mkdir -p diagnostics
{
  date -Is
  fastboot --version
  fastboot devices -l
  fastboot getvar product
  fastboot getvar current-slot
  fastboot getvar slot-count
  fastboot getvar is-userspace
  fastboot getvar slot-successful:a
  fastboot getvar slot-unbootable:a
  fastboot getvar slot-retry-count:a
  fastboot getvar slot-successful:b
  fastboot getvar slot-unbootable:b
  fastboot getvar slot-retry-count:b
  fastboot flashing get_unlock_ability
  fastboot getvar all
} 2>&1 | tee diagnostics/fastboot-state.txt
```

Do not worry if one vendor variable returns “unknown variable”; keep the rest.

### What you want to see

At minimum:

```text
fastboot device is present
bootloader is still unlocked
current-slot is a or b
at least one slot is not unbootable
is-userspace: no
```

If both slots report unbootable, go to Chapter 16 after the stock flash rather than before it.

---

# 15. Manual stock recovery path for your v0.8.293 files

## 15.1 Preferred method: official Rabbit flashing path

The community de-verity recovery notes explicitly recommend official Rabbit firmware/flashing tools as the starting point and reserve raw MediaTek `seccfg` work for last-resort recovery.[^deverity-recovery]

If the official Rabbit flasher accepts your device in its current state, use it. Keep the bootloader unlocked afterward if your next goal is Ubuntu Touch.

## 15.2 Manual path matching the files you already extracted

You extracted:

```text
rabbit_OS_v0.8.293_20250516110545/
```

Set a shell variable:

```bash
cd /home/manuel/code/others/rabbit-r1
FW="$PWD/rabbit_OS_v0.8.293_20250516110545"
```

Check the files before flashing:

```bash
ls -lh \
  "$FW/boot.img" \
  "$FW/dtbo.img" \
  "$FW/lk.img" \
  "$FW/tee.img" \
  "$FW/md1img.img" \
  "$FW/spmfw.img" \
  "$FW/scp.img" \
  "$FW/sspm.img" \
  "$FW/gz.img" \
  "$FW/vbmeta.img" \
  "$FW/vbmeta_system.img" \
  "$FW/vbmeta_vendor.img" \
  "$FW/super.img" \
  "$FW/userdata.img"
```

If any named file is absent, stop and adapt to the exact official package rather than substituting a similarly named file from another guide.

## 15.3 Enter bootloader fastboot

```bash
python3 r1_escape/mtkbootcmd.py FASTBOOT
fastboot devices -l
```

Confirm the bootloader is unlocked by attempting only read-only queries first. Do **not** run `fastboot flashing lock`.

## 15.4 Restore the slot-aware stock boot chain

The goal here is coherence, not de-verification. Flash the stock AVB images **without** `--disable-verity` and **without** `--disable-verification`.

```bash
fastboot flash md1img_a "$FW/md1img.img"
fastboot flash spmfw_a  "$FW/spmfw.img"
fastboot flash scp_a    "$FW/scp.img"
fastboot flash sspm_a   "$FW/sspm.img"
fastboot flash gz_a     "$FW/gz.img"
fastboot flash lk_a     "$FW/lk.img"
fastboot flash boot_a   "$FW/boot.img"
fastboot flash dtbo_a   "$FW/dtbo.img"
fastboot flash tee_a    "$FW/tee.img"
fastboot flash vbmeta_a        "$FW/vbmeta.img"
fastboot flash vbmeta_system_a "$FW/vbmeta_system.img"
fastboot flash vbmeta_vendor_a "$FW/vbmeta_vendor.img"
```

Mirror the supplied stock boot-chain images to slot B as a recovery measure:

```bash
fastboot flash md1img_b "$FW/md1img.img"
fastboot flash spmfw_b  "$FW/spmfw.img"
fastboot flash scp_b    "$FW/scp.img"
fastboot flash sspm_b   "$FW/sspm.img"
fastboot flash gz_b     "$FW/gz.img"
fastboot flash lk_b     "$FW/lk.img"
fastboot flash boot_b   "$FW/boot.img"
fastboot flash dtbo_b   "$FW/dtbo.img"
fastboot flash tee_b    "$FW/tee.img"
fastboot flash vbmeta_b        "$FW/vbmeta.img"
fastboot flash vbmeta_system_b "$FW/vbmeta_system.img"
fastboot flash vbmeta_vendor_b "$FW/vbmeta_vendor.img"
```

If `logo.bin` is present and you want the full stock presentation layer restored:

```bash
fastboot flash logo "$FW/logo.bin"
```

## 15.5 Restore the stock `super` filesystem

Your package contains `super.img`. Flash the physical `super` partition:

```bash
fastboot flash super "$FW/super.img"
```

This is different from `fastboot flash system system.img`: you are replacing the dynamic-partition container as a whole, which bootloader fastboot can support.

## 15.6 Restore userdata without relying on your broken host `mke2fs` path

Because `fastboot -w` has already failed at host-side filesystem creation, use the stock userdata image for this recovery test:

```bash
fastboot flash userdata "$FW/userdata.img"
fastboot erase metadata
```

This is destructive to personal data, but your earlier unlock/wipe attempts have already made data preservation unrealistic.

### Do not erase FRP for the Ubuntu Touch goal

The generic factory-recovery write-up includes an FRP erase as part of returning a device to factory behavior. Your objective is different: the FRP modification is what made bootloader unlocking possible. Preserve your current FRP and keep a backup rather than erasing it unnecessarily.

---

# 16. Slot recovery and first stock boot

After the coherent stock flash:

```bash
fastboot set_active a
```

Inspect:

```bash
fastboot getvar current-slot
fastboot getvar slot-retry-count:a
fastboot getvar slot-unbootable:a
fastboot getvar slot-successful:a
fastboot getvar slot-retry-count:b
fastboot getvar slot-unbootable:b
fastboot getvar slot-successful:b
```

If slot A is no longer marked unbootable, try:

```bash
fastboot reboot
```

Expected behavior for an unlocked but otherwise stock device:

1. an unlocked/orange-state style warning may appear;
2. the device proceeds into stock boot;
3. first boot may take longer than a normal reboot because userdata was replaced.

## 16.1 If both slots remain unbootable

The R1 community recovery notes used this device-specific reset after both slot retry counters had been exhausted:[^deverity-recovery]

```bash
fastboot erase boot_para
fastboot erase para
fastboot reboot bootloader
```

Re-enter/catch fastboot, then:

```bash
fastboot set_active a
```

Re-check slot variables before booting.

Use this only when the slot variables show that ordinary `set_active` did not recover bootability.

## 16.2 If stock boots successfully

Stop recovering. Do not “improve” the stock state by flashing disabled vbmeta again. You have reached the correct base for the Ubuntu Touch installer:

```text
stock rabbitOS v0.8 base
+
bootloader unlocked
+
working bootloader fastboot
```

Proceed to Chapter 20.

---

# 17. Last-resort R1-specific `seccfg` dm-verity recovery

This chapter is deliberately separated from the normal path.

## 17.1 When to consider it

Consider `seccfg` repair only if all of these are true:

- you restored a coherent stock boot chain and stock `super`;
- you kept the bootloader unlocked;
- the slot metadata is bootable;
- stock still shows or loops on `dm-verity corruption`;
- fresh boot diagnostics indicate that the bootloader is still forcing managed verity into `eio` mode.

The community write-up's crucial evidence was the boot parameter pair:

```text
androidboot.veritymode=eio
androidboot.veritymode.managed=yes
```

persisting after a stock flash.[^deverity-recovery]

## 17.2 Capture evidence first

Use `mtkclient` to read diagnostic partitions rather than immediately writing `seccfg`. For example, after reproducing one failed boot, reconnect to preloader/BROM and dump `expdb`:

```bash
cd /home/manuel/code/others/rabbit-r1/r1_escape/mtkclient
python3 mtk r expdb /tmp/r1-expdb.bin
strings -a /tmp/r1-expdb.bin | grep -Ei 'verity|avb|slot|boot' | tail -n 200
```

Also back up `seccfg` and FRP before any last-resort write:

```bash
python3 mtk r seccfg /tmp/r1-seccfg-before.bin
python3 mtk r frp    /tmp/r1-frp-before.bin
sha256sum /tmp/r1-seccfg-before.bin /tmp/r1-frp-before.bin
```

Keep copies somewhere outside the working directory.

## 17.3 What the community recovery found

For the investigated R1 `seccfg` V4 format, the write-up identifies:

- `lock_state` at offset `0x0c`; value `3` represented the unlocked state in that case;
- a critical/dm-verity state word at offset `0x10`; the bad state was `1` and the recovered state was `0`;
- a persistent managed-verity record in the range `0x240..0x2bf`.

The important warning is that the V4 header is authenticated. **Do not treat `seccfg` as an ordinary plaintext structure and hand-edit one integer in a hex editor.** The recovery procedure used `mtkclient`'s seccfg implementation to generate a valid authenticated header, then combined that generated header with the full partition and cleared the persistent managed-verity record.[^deverity-recovery]

## 17.4 Safe conceptual procedure

The evidence-based last-resort flow is:

```text
1. backup full seccfg
2. patch/use mtkclient so an "unlock" candidate is generated with:
      lock_state = unlocked
      critical/dm-verity state = 0
3. capture the generated authenticated header before direct DA write
4. copy that authenticated header into a full seccfg backup
5. zero only the known managed-verity record region
6. verify the resulting bytes and file size
7. write the complete corrected seccfg
8. stop sending commands immediately if the device begins a real boot
```

The community repository contains the exact patch strategy and should be treated as the authoritative device-specific reference for this escalation.[^deverity-recovery]

## 17.5 Why this is a last resort

A wrong `seccfg` write is qualitatively different from flashing `boot.img`. You are modifying MediaTek security/configuration state outside the normal Android OS partitions. That is recoverable in some scenarios because BROM/preloader access exists, but it is also easier to make the device harder to recover.

Do not perform this step merely because the screen once printed “dm-verity corruption.” Perform it because a clean stock test plus fresh diagnostics show the persistent R1-specific state described above.

---

# 18. Why you do **not** need to port Ubuntu Touch yourself

Older Ubuntu Touch advice often starts with “build Halium for your device.” That is correct for an unsupported device. It is no longer the right starting point for the R1.

The current UBports device page lists:

- device codename `r1`;
- a Halium-based R1 target;
- installer availability;
- stock rabbitOS v0.8 as the required starting firmware;
- an unlocked bootloader as a prerequisite.[^ubports-device]

The UBports infrastructure metadata also identifies a Rabbit R1 community port and device/kernel source locations.[^ubports-device-data]

Ubuntu Touch 24.04-1.0 explicitly included the Rabbit R1 in its supported-device list.[^ut-2404]

So your job is now an **installation/recovery job**, not a new-port engineering project.

---

# 19. How Ubuntu Touch on the R1 is architected

Ubuntu Touch is Linux, but on Android-derived devices it is not equivalent to taking an Ubuntu Desktop ARM image and writing it to storage.

UBports explains a modern port as a combination of:[^ut-porting]

- the Ubuntu Touch root filesystem;
- Halium components, including the device kernel/system-side hardware adaptation;
- vendor blobs from the Android base.

Conceptually:

```text
+----------------------------------------------------+
| Ubuntu Touch userspace                             |
| Lomiri shell, system services, apps, Ubuntu rootfs |
+----------------------------------------------------+
| Halium / libhybris / Android compatibility layer   |
+----------------------------------------------------+
| Android vendor services and proprietary blobs      |
+----------------------------------------------------+
| R1 Linux kernel + device drivers                    |
+----------------------------------------------------+
| MT6765 hardware                                     |
+----------------------------------------------------+
```

This explains why the installer cares about the Android/rabbitOS firmware family: the proprietary firmware and hardware interfaces remain part of the usable device stack.

It also explains why “Ubuntu Touch” is not identical to “desktop Ubuntu on a tiny screen.” Ubuntu Touch uses OTA system images and generally keeps its root filesystem read-only; UBports documents Libertine/other mechanisms for installing conventional desktop packages without treating the base OS like a normal mutable Debian workstation.[^libertine]

---

# 20. Installing Ubuntu Touch with the UBports Installer

Once stock v0.8 boots correctly and the bootloader remains unlocked, stop using the `r1_escape` flashing script.

## 20.1 Prerequisites

You want this state:

```text
[ ] rabbit r1 hardware confirmed
[ ] stock rabbitOS v0.8 base restored
[ ] bootloader unlocked
[ ] bootloader fastboot visible to the host
[ ] no unresolved persistent stock dm-verity loop
[ ] USB cable stable
[ ] host fastboot stack functional
```

The current R1 installer config requires an installer compatible with version `>=0.9.2-beta`; use a current UBports Installer release rather than an old package.[^installer-config]

## 20.2 Run the installer as your normal user

UBports documentation explicitly advises **not** to run the installer with `sudo`, because root execution can create permission problems in its cache.[^ubports-install]

Start the UBports Installer normally.

## 20.3 Select the device

If automatic detection is unreliable because you are not booted into Android, manually select:

```text
rabbit r1
codename: r1
```

Confirm the installer warnings about model, stock v0.8 firmware, and unlocked bootloader.[^installer-config]

## 20.4 Choose the install options

For the first switch from Android/rabbitOS to Ubuntu Touch:

- choose the **stable channel currently offered by the installer**;
- enable **Wipe Userdata**;
- leave **Bootstrap** enabled.

Do not choose a development channel just because a blog post mentions a newer release candidate. Your first goal is a known-good boot.

## 20.5 Enter bootloader fastboot when asked

The current R1 config describes a hardware route using the scroll wheel and power button.[^installer-config]

If that is awkward and your proven preloader method works, you can place the device in bootloader fastboot yourself:

```bash
python3 /home/manuel/code/others/rabbit-r1/r1_escape/mtkbootcmd.py FASTBOOT
fastboot devices -l
```

Then let the installer continue.

## 20.6 What the installer actually flashes

The R1 bootstrap currently downloads:

- an R1-specific `boot.img`;
- an R1-specific packaged `super.img`;
- a `vbmeta.img` used by the installation bootstrap.

It verifies checksums, unpacks the super archive, and performs the equivalent high-level sequence:[^installer-config]

```text
bootloader fastboot
    |
    +--> flash vbmeta
    +--> flash boot
    +--> flash super
    +--> format userdata (when wipe selected)
    |
    v
reboot to UBports recovery
    |
    v
system-image installation
    |
    v
reboot / finish
```

This is why you should **not pre-flash** `r1_escape/vbmeta.img` immediately before running the installer. Let the installer establish the image set it expects.

## 20.7 If userdata formatting fails again

If the UBports Installer reports a host-side format failure similar to your `/usr/lib/android-sdk/platform-tools/mke2fs` error:

1. save the installer log;
2. update/fix the host Android platform-tools stack instead of repeatedly wiping;
3. re-run the installer as a normal user;
4. do not add random manual `fastboot -w` cycles between installer attempts.

Your earlier message proves the device can erase userdata; the problem was in the host filesystem-generation stage.

---

# 21. Why the Ubuntu Touch path does not depend on your failing fastbootd step

This deserves a direct answer because it is the main place your earlier workflow went sideways.

`r1_escape` is designed to install an Android AOSP userdebug **`system.img`**. Its script therefore:

```text
unlock
wipe
flash disabled vbmeta
reboot to fastbootd
flash logical system
```

That makes sense for a dynamic logical `system` partition.[^r1-escape-script][^fastbootd]

The R1 Ubuntu Touch installer, by contrast, flashes a complete `super` image in its bootstrap.[^installer-config]

Therefore:

- **do not continue debugging `fastboot reboot-fastboot` as the next required Ubuntu Touch step;**
- first fix the stock/verity state;
- then use the supported installer bootstrap.

Fastbootd may still be useful for Android ROM work, but it is no longer the critical path to your stated goal.

---

# 22. After Ubuntu Touch boots

## 22.1 Update through the supported mechanism

Ubuntu Touch 24.04-1.0 lists Rabbit R1 as a supported device. UBports' normal upgrade path for existing devices is through **System Settings -> Update**.[^ut-2404]

Because channel metadata and release rollouts change over time, do not hard-code an old channel string from a forum guide. Use the stable update offered to the device.

## 22.2 Expect Ubuntu Touch behavior, not desktop Ubuntu behavior

The Ubuntu Touch root filesystem is designed around OTA image updates and is normally read-only. Conventional desktop packages are not managed exactly as on an Ubuntu laptop; UBports documents containers such as Libertine for traditional desktop applications.[^libertine]

## 22.3 Keep the bootloader unlocked

The installed Ubuntu Touch boot chain is not the original locked Rabbit trust chain. Relocking after installation can put you back into a “correct signature”/bad-state failure.

## 22.4 Keep your recovery assets

Archive these on another machine:

```text
rabbitOS v0.8.293 firmware archive
original FRP backup (if you have one)
current FRP backup
pre-repair seccfg backup (if created)
mtkclient version/commit used
r1_escape mtkbootcmd.py
UBports Installer logs from the successful installation
```

That turns a future failure from archaeology into a reproducible recovery.

---

# 23. Troubleshooting matrix

| Symptom | Layer | Likely meaning | Next action |
|---|---|---|---|
| `fastboot devices` empty immediately after `FASTBOOT` serial write | USB transition | preloader command sent, fastboot USB personality not yet enumerated | reconnect/reset; verify no process owns tty; retry proven `mtkbootcmd.py` flow |
| `not allowed in locked state` | bootloader policy | bootloader locked | do not flash; confirm unlock path/state |
| `unlock_ability = 0` | unlock gate | bootloader refuses unlock request | FRP/OEM-unlock gate not enabled; your `r1_escape` FRP step solved this previously |
| `fastboot flashing unlock` returns `OKAY` | bootloader policy | unlock complete | proceed; expect data wipe/security warning |
| `mke2fs failed with status 1` after `Erasing 'userdata' OKAY` | host fastboot tools | erase succeeded; host format image generation failed | stop repeating `-w`; use stock userdata for recovery; update host platform-tools for installer |
| `fastboot reboot-fastboot` -> waiting forever | userspace/recovery boot | bootloader fastboot exited, fastbootd never enumerated | not a UT blocker; recover stock, then use UBports bootstrap |
| `dm-verity corruption` after mixed custom flashes | AVB/dm-verity | image/metadata mismatch or persisted managed error | first restore coherent stock boot chain + super |
| stock images restored but `veritymode=eio` persists | R1 security state | evidence for `seccfg` managed-verity persistence | back up, then follow R1 de-verity recovery last-resort procedure |
| both slots `unbootable: yes` | A/B metadata | retry state exhausted | after stock flash, `set_active`; if R1 still stuck, use documented `boot_para`/`para` reset |
| UBports installer cannot auto-detect | ADB/device detection | device not in Android/ADB or unusual USB state | select `rabbit r1` manually; enter bootloader when requested |
| UBports install boots recovery but system-image install fails | recovery/install layer | installation payload or userdata/log issue | save installer/recovery logs; retry supported path, not `r1_escape` custom vbmeta |

---

# 24. Command reference

## 24.1 Read-only fastboot state capture

```bash
fastboot devices -l
fastboot getvar current-slot
fastboot getvar is-userspace
fastboot getvar slot-successful:a
fastboot getvar slot-unbootable:a
fastboot getvar slot-retry-count:a
fastboot getvar slot-successful:b
fastboot getvar slot-unbootable:b
fastboot getvar slot-retry-count:b
fastboot flashing get_unlock_ability
fastboot getvar all 2>&1 | tee fastboot-all.txt
```

## 24.2 Proven R1 preloader -> bootloader-fastboot entry

```bash
python3 r1_escape/mtkbootcmd.py FASTBOOT
fastboot devices -l
```

## 24.3 Stock AVB diagnostic principle

For a clean stock test:

```text
YES: stock vbmeta images, flashed normally, bootloader remains unlocked
NO:  --disable-verity / --disable-verification
NO:  relocking the bootloader
NO:  mixing r1_escape vbmeta with stock boot/super
```

## 24.4 Slot activation

```bash
fastboot set_active a
```

## 24.5 R1-specific deeper slot reset only when needed

```bash
fastboot erase boot_para
fastboot erase para
fastboot reboot bootloader
```

## 24.6 Backup raw security/config partitions before last-resort work

```bash
python3 mtk r seccfg /tmp/r1-seccfg-before.bin
python3 mtk r frp    /tmp/r1-frp-before.bin
sha256sum /tmp/r1-seccfg-before.bin /tmp/r1-frp-before.bin
```

---

# 25. Glossary

**ADB**  
Android Debug Bridge. A userspace debugging/communication protocol. Different from fastboot.

**A/B slots**  
Two bootable sets of slot-aware Android partitions, normally `a` and `b`, used for seamless updates and rollback.

**AVB**  
Android Verified Boot 2.0. The signed metadata and verification framework used by modern Android.

**BROM**  
MediaTek Boot ROM: immutable first-stage code in the SoC.

**boot.img**  
Android boot image containing the Linux kernel and early userspace/ramdisk components.

**bootloader fastboot**  
Fastboot implemented in the bootloader. Available before Android/recovery userspace.

**dm-verity**  
Linux device-mapper integrity target used to verify large read-only block-device filesystems using hash trees.

**FRP**  
Factory Reset Protection partition. In the `r1_escape` flow, a byte in this partition is used to alter the R1's bootloader-unlock permission state.

**fastbootd**  
Userspace fastboot, normally entered through recovery. Designed to manipulate Android dynamic logical partitions.

**GSI**  
Generic System Image. Android's Treble architecture and Halium both use generic system-image concepts to separate generic OS code from vendor hardware support.

**Halium**  
Hardware abstraction project that lets GNU/Linux mobile systems reuse Android kernels, vendor services, and blobs. Ubuntu Touch Android-device ports use it.

**preloader**  
MediaTek vendor boot stage after BROM. On your R1 it exposes a CDC ACM serial interface that `mtkbootcmd.py` uses.

**`seccfg`**  
MediaTek security/configuration partition. The R1 community de-verity recovery found persistent lock/managed-verity state here.

**`super`**  
Physical Android dynamic-partition container holding logical partitions such as `system`, `vendor`, and `product`.

**`vbmeta`**  
AVB metadata image containing or chaining the signed descriptors used to verify partitions.

---

# 26. Sources and further reading

The technical model and installation path in this document were cross-checked against current upstream/vendor/community material on August 7, 2026.

[^avb]: Android Open Source Project, **Android Verified Boot**, https://source.android.com/docs/security/features/verifiedboot/avb
[^verified-boot]: Android Open Source Project, **Use Verified Boot**, https://source.android.com/docs/security/features/verifiedboot/verified-boot
[^dm-verity]: Android Open Source Project, **Implement dm-verity**, https://source.android.com/docs/security/features/verifiedboot/dm-verity
[^dynamic-partitions]: Android Open Source Project, **Dynamic partitions**, https://source.android.com/docs/core/ota/dynamic_partitions
[^fastbootd]: Android Open Source Project, **Move fastboot to userspace**, https://source.android.com/docs/core/architecture/bootloader/fastbootd
[^ab-implement]: Android Open Source Project, **Implement A/B updates**, https://source.android.com/docs/core/ota/ab/ab_implement
[^ab-updating]: Android Open Source Project, **Implement OTA updates / A/B bootloader interactions**, https://source.android.com/docs/core/architecture/bootloader/updating
[^fastboot-mke2fs]: Android Open Source Project source tree, fastboot build packaging includes host filesystem tools such as `mke2fs`, https://android.googlesource.com/platform/system/core/
[^r1-escape-script]: RabbitHoleEscapeR1, **r1_escape / r1.sh**, https://github.com/RabbitHoleEscapeR1/r1_escape/blob/main/r1.sh
[^deverity-recovery]: Jonathan Procter, **Rabbit R1 Recovery Notes: Bad State, dm-verity/de-verity Corruption, Boot Loops, and Factory Restore**, https://github.com/jonathanprocter/rabbit-r1-deverity-recovery/blob/main/docs/rabbit-r1-de-verity-recovery-community-writeup.md
[^ubports-device]: UBports, **rabbit r1 device page**, https://devices.ubuntu-touch.io/device/r1/
[^ubports-device-data]: UBports device infrastructure, **rabbit r1 metadata**, https://gitlab.com/ubports/infrastructure/devices.ubuntu-touch.io/-/blob/main/data/devices/r1/data.md
[^installer-config]: UBports, **Installer configuration for `r1`**, https://github.com/ubports/installer-configs/blob/master/v2/devices/r1.yml
[^ut-porting]: UBports documentation, **Introduction to porting**, https://docs.ubports.com/en/latest/porting/introduction/Intro.html
[^ubports-install]: UBports documentation, **Install Ubuntu Touch**, https://docs.ubports.com/en/latest/userguide/install.html
[^ut-2404]: UBports, **Ubuntu Touch 24.04-1.0 release**, https://ubports.com/blog/ubports-news-1/ubuntu-touch-24-04-1-0-release-3973
[^libertine]: UBports documentation, **Run desktop applications / Libertine**, https://docs.ubports.com/en/latest/userguide/dailyuse/libertine.html

---

## Final checklist for your exact situation

Before your next write operation, answer these in order:

```text
1. Can I enter bootloader fastboot?             YES - your logs proved this.
2. Is the bootloader unlocked?                  It was; verify again.
3. What is the current slot?                    Inspect now.
4. Are either/both slots marked unbootable?     Inspect now.
5. Have I restored one coherent stock v0.8 set? Not yet, based on the supplied log.
6. Does clean stock boot without dm-verity?     Test after coherent restore.
7. Only if no: is managed verity=eio persistent? Capture evidence.
8. Only if yes: use the seccfg recovery path.
9. Once stock boots: run UBports Installer.
10. Do I need fastbootd first for Ubuntu Touch? NO.
```

The single most useful change in approach is to stop treating each error as a new command to try. Treat the device as a chain of stateful layers, restore each layer to one known configuration, and only move downward into raw MediaTek state when the higher-level stock test proves it is necessary.
EOF
wc -l /mnt/data/rabbit_r1_textbook/rabbit-r1-dm-verity-to-ubuntu-touch.md
wc -w /mnt/data/rabbit_r1_textbook/rabbit-r1-dm-verity-to-ubuntu-touch.md
```

<details><summary>💭 Thinking</summary>

**Created Rabbit R1 Ubuntu Touch community patch guide**

</details>

```unknown
bash -lc cat > /mnt/data/rabbit_r1_textbook/build_textbook.py <<'PY'
from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_BREAK
from docx.enum.section import WD_ORIENT

SRC = Path('/mnt/data/rabbit_r1_textbook/rabbit-r1-dm-verity-to-ubuntu-touch.md')
OUT = Path('/mnt/data/rabbit_r1_textbook/rabbit-r1-dm-verity-to-ubuntu-touch.docx')
text = SRC.read_text()
lines = text.splitlines()

# Collect footnote definitions and map in appearance order.
defs = {}
content_lines=[]
for line in lines:
    m = re.match(r'^\[\^([^\]]+)\]:\s*(.*)$', line)
    if m:
        defs[m.group(1)] = m.group(2)
    else:
        content_lines.append(line)

order=[]
for line in content_lines:
    for key in re.findall(r'\[\^([^\]]+)\]', line):
        if key not in order:
            order.append(key)
num = {k:i+1 for i,k in enumerate(order)}

def replace_refs(s):
    return re.sub(r'\[\^([^\]]+)\]', lambda m: f'[{num.get(m.group(1), "?")}]', s)

# Markdown inline cleanup, preserving backtick code via font changes later.
def tokenize_inline(s):
    # returns list of (text, kind) kind: normal,bold,code,italic
    s = replace_refs(s)
    tokens=[]
    pos=0
    pattern=re.compile(r'(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)')
    for m in pattern.finditer(s):
        if m.start()>pos: tokens.append((s[pos:m.start()], 'normal'))
        t=m.group(0)
        if t.startswith('**'): tokens.append((t[2:-2],'bold'))
        elif t.startswith('`'): tokens.append((t[1:-1],'code'))
        elif t.startswith('*'): tokens.append((t[1:-1],'italic'))
        pos=m.end()
    if pos<len(s): tokens.append((s[pos:],'normal'))
    return tokens

def add_inline(p, s):
    # basic markdown links [text](url) -> text (url)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'\1 (\2)', s)
    for txt,kind in tokenize_inline(s):
        r=p.add_run(txt)
        if kind=='bold': r.bold=True
        elif kind=='italic': r.italic=True
        elif kind=='code':
            r.font.name='DejaVu Sans Mono'
            r.font.size=Pt(8.5)
            r.font.color.rgb=RGBColor(50,50,50)


def set_cell_shading(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = tcPr.find(qn('w:shd'))
    if shd is None:
        shd = OxmlElement('w:shd'); tcPr.append(shd)
    shd.set(qn('w:fill'), fill)


def set_cell_margins(cell, top=90, start=90, bottom=90, end=90):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = tcPr.first_child_found_in('w:tcMar')
    if tcMar is None:
        tcMar = OxmlElement('w:tcMar'); tcPr.append(tcMar)
    for m, v in [('top',top),('start',start),('bottom',bottom),('end',end)]:
        node = tcMar.find(qn('w:'+m))
        if node is None:
            node=OxmlElement('w:'+m); tcMar.append(node)
        node.set(qn('w:w'), str(v)); node.set(qn('w:type'),'dxa')


def add_page_field(paragraph):
    run = paragraph.add_run()
    fldChar1=OxmlElement('w:fldChar'); fldChar1.set(qn('w:fldCharType'),'begin')
    instr=OxmlElement('w:instrText'); instr.set(qn('xml:space'),'preserve'); instr.text=' PAGE '
    fldChar2=OxmlElement('w:fldChar'); fldChar2.set(qn('w:fldCharType'),'end')
    run._r.extend([fldChar1,instr,fldChar2])


doc=Document()
sec=doc.sections[0]
sec.top_margin=Inches(0.7); sec.bottom_margin=Inches(0.7); sec.left_margin=Inches(0.78); sec.right_margin=Inches(0.78)
sec.header_distance=Inches(0.28); sec.footer_distance=Inches(0.28)

styles=doc.styles
styles['Normal'].font.name='DejaVu Sans'; styles['Normal'].font.size=Pt(9.5)
styles['Normal'].paragraph_format.space_after=Pt(5)
styles['Normal'].paragraph_format.line_spacing=1.08
for sname,size,color in [('Title',28,'17365D'),('Heading 1',18,'17365D'),('Heading 2',14,'2F5597'),('Heading 3',11.5,'44546A')]:
    st=styles[sname]; st.font.name='DejaVu Sans'; st.font.size=Pt(size); st.font.bold=True; st.font.color.rgb=RGBColor.from_string(color)
    st.paragraph_format.space_before=Pt(11 if sname!='Title' else 0); st.paragraph_format.space_after=Pt(5)
    if sname=='Heading 1': st.paragraph_format.page_break_before=True
styles['Heading 1'].paragraph_format.keep_with_next=True
styles['Heading 2'].paragraph_format.keep_with_next=True
styles['Heading 3'].paragraph_format.keep_with_next=True

# custom styles
for name, base, size in [('Code Block','Normal',8.2),('Callout','Normal',9.2),('Source Ref','Normal',8.2)]:
    if name not in styles:
        st=styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH); st.base_style=styles[base]
    st=styles[name]; st.font.name='DejaVu Sans Mono' if name=='Code Block' else 'DejaVu Sans'; st.font.size=Pt(size)

# Header/footer
header=sec.header.paragraphs[0]
header.text='Rabbit R1: dm-verity recovery -> Ubuntu Touch'
header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
for r in header.runs:
    r.font.name='DejaVu Sans'; r.font.size=Pt(7.5); r.font.color.rgb=RGBColor(100,100,100)
footer=sec.footer.paragraphs[0]
footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=footer.add_run('Page '); r.font.size=Pt(8); r.font.name='DejaVu Sans'
add_page_field(footer)

# Parse content
in_code=False
code_buf=[]
first_h1=True
i=0
while i < len(content_lines):
    line=content_lines[i]
    if line.startswith('```'):
        if not in_code:
            in_code=True; code_buf=[]
        else:
            p=doc.add_paragraph(style='Code Block')
            p.paragraph_format.left_indent=Inches(0.18); p.paragraph_format.right_indent=Inches(0.18)
            p.paragraph_format.space_before=Pt(3); p.paragraph_format.space_after=Pt(6)
            p.paragraph_format.keep_together=True
            pPr=p._p.get_or_add_pPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),'F2F4F7'); pPr.append(shd)
            r=p.add_run('\n'.join(code_buf)); r.font.name='DejaVu Sans Mono'; r.font.size=Pt(8.0)
            in_code=False
        i+=1; continue
    if in_code:
        code_buf.append(line); i+=1; continue
    if line.strip()=='---':
        p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(3); p.paragraph_format.space_after=Pt(3)
        pPr=p._p.get_or_add_pPr(); pbdr=OxmlElement('w:pBdr'); bottom=OxmlElement('w:bottom'); bottom.set(qn('w:val'),'single'); bottom.set(qn('w:sz'),'6'); bottom.set(qn('w:space'),'1'); bottom.set(qn('w:color'),'D9E2F3'); pbdr.append(bottom); pPr.append(pbdr)
        i+=1; continue
    if not line.strip():
        i+=1; continue
    # markdown table detection
    if line.startswith('|') and i+1 < len(content_lines) and re.match(r'^\|?\s*[-:]+', content_lines[i+1].strip('|').split('|')[0].strip()):
        rows=[]
        header_cells=[c.strip() for c in line.strip().strip('|').split('|')]
        i+=2
        while i < len(content_lines) and content_lines[i].startswith('|'):
            rows.append([c.strip() for c in content_lines[i].strip().strip('|').split('|')]); i+=1
        table=doc.add_table(rows=1+len(rows), cols=len(header_cells))
        table.alignment=WD_TABLE_ALIGNMENT.CENTER; table.style='Table Grid'
        for c_idx,c in enumerate(header_cells):
            cell=table.rows[0].cells[c_idx]; cell.text=''; set_cell_shading(cell,'D9E2F3'); set_cell_margins(cell)
            p=cell.paragraphs[0]; add_inline(p,c); p.runs[0].bold=True if p.runs else None
        for r_idx,row in enumerate(rows, start=1):
            for c_idx in range(len(header_cells)):
                cell=table.rows[r_idx].cells[c_idx]; cell.text=''; set_cell_margins(cell)
                cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP
                p=cell.paragraphs[0]; add_inline(p,row[c_idx] if c_idx < len(row) else '')
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.space_after=Pt(1.5)
                    for r in p.runs: r.font.size=Pt(8.2)
        doc.add_paragraph().paragraph_format.space_after=Pt(1)
        continue
    # headings
    m=re.match(r'^(#{1,3})\s+(.*)$', line)
    if m:
        level=len(m.group(1)); title=replace_refs(m.group(2))
        if level==1 and first_h1:
            p=doc.add_paragraph(style='Title'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; add_inline(p,title)
            first_h1=False
        else:
            p=doc.add_paragraph(style=f'Heading {level}'); add_inline(p,title)
        i+=1; continue
    # blockquote
    if line.startswith('>'):
        block=[]
        while i<len(content_lines) and content_lines[i].startswith('>'):
            block.append(content_lines[i].lstrip('> ').rstrip()); i+=1
        p=doc.add_paragraph(style='Callout')
        p.paragraph_format.left_indent=Inches(0.25); p.paragraph_format.right_indent=Inches(0.15)
        p.paragraph_format.space_before=Pt(4); p.paragraph_format.space_after=Pt(6)
        pPr=p._p.get_or_add_pPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),'FFF2CC'); pPr.append(shd)
        add_inline(p,' '.join(block))
        continue
    # numbered/bullet list
    m=re.match(r'^\s*(\d+)\.\s+(.*)$', line)
    if m:
        p=doc.add_paragraph(style='List Number'); add_inline(p,m.group(2)); i+=1; continue
    m=re.match(r'^\s*[-*]\s+(.*)$', line)
    if m:
        p=doc.add_paragraph(style='List Bullet'); add_inline(p,m.group(1)); i+=1; continue
    # text lines with markdown hard break often two spaces; merge adjacent prose until structural marker
    para=[line.strip()]
    i+=1
    while i<len(content_lines):
        nxt=content_lines[i]
        if (not nxt.strip() or nxt.startswith('#') or nxt.startswith('```') or nxt.startswith('>') or nxt.startswith('|') or nxt.strip()=='---' or re.match(r'^\s*(\d+)\.\s+',nxt) or re.match(r'^\s*[-*]\s+',nxt)):
            break
        para.append(nxt.strip()); i+=1
    p=doc.add_paragraph()
    add_inline(p,' '.join(para))

# Append a compact references section from defs if not already converted in prose.
doc.add_heading('Reference notes', level=1)
for key in order:
    if key in defs:
        p=doc.add_paragraph(style='Source Ref')
        r=p.add_run(f'[{num[key]}] '); r.bold=True
        add_inline(p, defs[key])

# Title-page-ish metadata: center the early subtitle/edition lines if near top.
# We can't easily reposition after parse, but style first few paragraphs.
for idx,p in enumerate(doc.paragraphs[:8]):
    if idx in (1,2,3):
        p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        if idx==1:
            for r in p.runs: r.font.size=Pt(13); r.font.italic=True; r.font.color.rgb=RGBColor(68,84,106)

# Make hyperlinks/URLs smaller in reference notes? leave readable.

# Set keep-with-next for headings and captions; widow control default.
for p in doc.paragraphs:
    if p.style.name.startswith('Heading'):
        p.paragraph_format.keep_with_next=True

# Save
doc.save(OUT)
print(OUT)
PY
python /mnt/data/rabbit_r1_textbook/build_textbook.py
ls -lh /mnt/data/rabbit_r1_textbook/rabbit-r1-dm-verity-to-ubuntu-touch.docx
```

<details><summary>💭 Thinking</summary>

**Generated and rendered DOCX, then counted textbook pages**

</details>

```unknown
bash -lc python - <<'PY'
from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
pages=sorted(Path('/mnt/data/rabbit_r1_textbook/rendered').glob('page-*.png'), key=lambda p:int(p.stem.split('-')[1]))
out=Path('/mnt/data/rabbit_r1_textbook/contact'); out.mkdir(exist_ok=True)
for g in range(0,len(pages),4):
    subset=pages[g:g+4]
    thumbs=[]
    for p in subset:
        im=Image.open(p).convert('RGB')
        # scale to 850px wide preserving aspect
        w=850; h=round(im.height*w/im.width)
        im=im.resize((w,h))
        canvas=Image.new('RGB',(w,h+40),'white')
        canvas.paste(im,(0,40))
        d=ImageDraw.Draw(canvas); d.text((10,10),p.stem,fill='black')
        thumbs.append(canvas)
    cw=max(im.width for im in thumbs); ch=max(im.height for im in thumbs)
    sheet=Image.new('RGB',(cw*2,ch*2),(230,230,230))
    for j,im in enumerate(thumbs): sheet.paste(im,((j%2)*cw,(j//2)*ch))
    sheet.save(out/f'contact-{g//4+1:02d}.jpg',quality=88)
print(len(list(out.glob('*.jpg'))))
PY
```

<details><summary>💭 Thinking</summary>

**Building the recovery guide**

I’m assembling a cautious, device-specific path: stabilize the stock firmware first, explain the dm-verity state, then evaluate whether the community Ubuntu Touch port can be installed without relying on the failed fastbootd transition.

**Clarifying the recovery state**

I’m separating the unlocked bootloader, modified AVB metadata, and possible dm-verity record, since they’re distinct. The next guide should inspect slots and restore a complete stock base before attempting Ubuntu Touch.

**Finalizing the textbook**

I’m correcting the manuscript’s list numbering, rebuilding the DOCX and PDF, and checking the rendered pages again so the downloadable guides are clean and consistent.

**Built the recovery guide and clarified recovery state**

</details>

```unknown
bash -lc grep -n -A8 -B4 "List Number" /mnt/data/rabbit_r1_textbook/build_textbook.py && ls -lh /mnt/data/rabbit_r1_textbook | sed -n '1,30p'
```

<details><summary>💭 Thinking</summary>

**Generated contact sheets, analyzed images, and rebuilt the textbook document**

</details>

```unknown
bash -lc set -e
cp /mnt/data/rabbit_r1_textbook/rabbit-r1-dm-verity-to-ubuntu-touch.md /mnt/data/rabbit-r1-dm-verity-to-ubuntu-touch.md
cp /mnt/data/rabbit_r1_textbook/rendered/rabbit-r1-dm-verity-to-ubuntu-touch.pdf /mnt/data/rabbit-r1-dm-verity-to-ubuntu-touch.pdf
rm -rf /mnt/data/rabbit_r1_pdf_qa
python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/rabbit-r1-dm-verity-to-ubuntu-touch.pdf --out_dir /mnt/data/rabbit_r1_pdf_qa --dpi 160
pdfinfo /mnt/data/rabbit-r1-dm-verity-to-ubuntu-touch.pdf | sed -n '1,20p'
wc -l /mnt/data/rabbit-r1-dm-verity-to-ubuntu-touch.md
ls -lh /mnt/data/rabbit-r1-dm-verity-to-ubuntu-touch.{md,pdf}

```

<details><summary>💭 Thinking</summary>

**Validated and rendered final PDF artifacts**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
from PIL import Image, ImageDraw
import re
src=Path('/mnt/data/rabbit_r1_pdf_qa')
imgs=list(src.glob('*.png'))
def nkey(p):
    m=re.search(r'(\d+)(?=\.png$)',p.name)
    return int(m.group(1)) if m else 9999
imgs=sorted(imgs,key=nkey)
out=Path('/mnt/data/rabbit_r1_pdf_qa_contact'); out.mkdir(exist_ok=True)
for k in range(0,len(imgs),4):
    batch=imgs[k:k+4]
    sheet=Image.new('RGB',(1440,2060),'white')
    for j,p in enumerate(batch):
        im=Image.open(p).convert('RGB'); im.thumbnail((700,990))
        canvas=Image.new('RGB',(720,1030),'white')
        canvas.paste(im,((720-im.width)//2,20))
        ImageDraw.Draw(canvas).text((10,1005),p.name,fill='black')
        sheet.paste(canvas,((j%2)*720,(j//2)*1030))
    sheet.save(out/f'pdf-contact-{k//4+1:02d}.jpg',quality=90)
print('inputs',len(imgs),'contacts',len(list(out.glob('*.jpg'))))
print([p.name for p in imgs[:5]], [p.name for p in imgs[-5:]])
PY
```

<details><summary>💭 Thinking</summary>

**Created naturally sorted PDF contact sheets and analyzed images**

</details>

Completed. I created a textbook-style guide based on your terminal history, the R1 community recovery notes, `r1_escape`, Android/AOSP documentation, and the current UBports Rabbit R1 installer configuration.

The main conclusion is that **you do not need to port Ubuntu Touch yourself**. Rabbit R1 already has an Ubuntu Touch target and installer configuration, and it is included in UBports' supported-device releases. citeturn882415search0turn767406search0 The current R1 installer bootstrap explicitly flashes its own `vbmeta`, `boot`, and complete `super` image before entering UBports recovery. fileciteturn6file0L2-L2

Your logs also show that you successfully crossed the hardest initial boundary: after changing the R1's FRP unlock state, `fastboot flashing unlock` began succeeding. The problem now is that the machine has been left in an **ambiguous mixture of stock boot images, verification-disabled vbmeta images, possible slot-state damage, and unknown `super` contents**. I therefore would **not issue another speculative flash command yet**.

The guide explains why your `fastboot -w` result is also less catastrophic than it looks: the device reported that `userdata` was erased successfully; the subsequent failure was the host-side `mke2fs` filesystem-generation stage. It also explains why your repeated failure to enter `fastbootd` is **not a prerequisite blocker for Ubuntu Touch**: that `fastbootd` step belongs to the `r1_escape`/CipherOS-style approach of flashing a logical `system` partition, whereas the R1 Ubuntu Touch installer flashes the whole physical `super` image from bootloader fastboot. fileciteturn5file0L2-L2 fileciteturn6file0L2-L2

The recovery strategy in the book is:

1. **Stop changing state and inspect it first.**
2. Re-establish one coherent, unlocked **stock rabbitOS v0.8** boot chain plus stock `super`.
3. Restore normal stock vbmeta **without** `--disable-verity` or `--disable-verification`.
4. Recover A/B slot metadata only if inspection shows it is necessary.
5. Boot stock once.
6. Only if a clean stock installation still produces persistent managed `dm-verity`/`eio` state, investigate the R1-specific `seccfg` problem from the community recovery write-up. That is deliberately treated as a last-resort operation.
7. Once stock v0.8 boots and the bootloader remains unlocked, run the normal UBports installer with **Bootstrap** and **Wipe userdata** enabled and let it install its own boot chain and `super` image.

The PDF is **34 pages** and was rendered and visually checked page-by-page, including command blocks, diagrams, tables, glossary, troubleshooting matrix, and references.

[Download the Markdown textbook](sandbox:/mnt/data/rabbit-r1-dm-verity-to-ubuntu-touch.md)

[Download the PDF textbook](sandbox:/mnt/data/rabbit-r1-dm-verity-to-ubuntu-touch.pdf)

The most useful immediate section for you is **Chapter 14, “Non-destructive inspection checklist.”** Run that block before doing another write. It will tell us the active slot, whether either slot has been marked unbootable, and the bootloader/fastboot state. From that output, the next operation can be chosen deterministically rather than continuing the flash/reboot loop.

