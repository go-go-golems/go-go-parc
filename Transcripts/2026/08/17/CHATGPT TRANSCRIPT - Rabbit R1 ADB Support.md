# Rabbit R1 ADB Support

- URL: https://chatgpt.com/c/6a805e2a-6434-83ea-8ea8-f465beea174a
- Created: 2026-08-15T12:40:37.828Z

---

> I want to add adb support to the rabbit r1 ubuntu touch port, how and how far is it already and what are the issues

I’ll check the current Ubuntu Touch/rabbit r1 port status, then trace where ADB should be enabled in the boot image/initramfs and what is blocking it on this device.

```json
{"system1_search_query":[{"q":"rabbit r1 Ubuntu Touch port GitHub adb"},{"q":"rabbit r1 ubuntu touch ubports port"},{"q":"rabbit r1 halium port ubuntu touch"},{"q":"rabbit r1 ubuntu touch port rabbit os linux kernel"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 18 websites**

</details>

The current UBports device page is more advanced than older discussions suggest: rabbit r1 is now on Ubuntu Touch 24.04 stable, but **ADB is explicitly marked “Partial,” not working**. MTP is also partial, so this is probably a USB gadget/configuration problem rather than “just install `adbd`.”

```json
{"system1_search_query":[{"q":"site:gitlab.com/ubports rabbit-r1 adb r1 adbd usb gadget"},{"q":"site:github.com/MinatiScape/ubtouch-on-r1 adb"},{"q":"site:github.com/MinatiScape/ubtouch-on-r1 usb configfs adbd"},{"q":"site:docs.ubports.com ADB Ubuntu Touch enable adb developer mode adbd"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

The port already contains most of the expected ADB plumbing: MediaTek USB VID/PIDs are configured, `usb-moded` is configured for MTP+ADB/RNDIS+ADB, and the device overlay explicitly does `start adbd`. So the missing work is likely below that layer—FunctionFS/configfs binding, UDC state, or Android-container permissions/startup.

```json
{"open":[{"ref_id":"https://gitlab.com/api/v4/groups/ubports%2Fporting%2Fcommunity-ports%2Fandroid12%2Frabbit-r1/projects?include_subgroups=true&per_page=100"},{"ref_id":"https://gitlab.com/api/v4/projects/67348022/search?scope=blobs&search=usb"},{"ref_id":"https://gitlab.com/api/v4/projects/67348022/search?scope=blobs&search=adbd"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```json
{"open":[{"ref_id":"https://gitlab.com/api/v4/projects/67348285/search?scope=blobs&search=CONFIG_USB_CONFIGFS_F_FS&ref=halium-12.0"},{"ref_id":"https://gitlab.com/api/v4/projects/67348285/search?scope=blobs&search=CONFIG_USB_F_FS&ref=halium-12.0"},{"ref_id":"https://gitlab.com/api/v4/projects/67348285/search?scope=blobs&search=CONFIG_USB_CONFIGFS&ref=halium-12.0"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Checking config dependencies**

I’m validating whether FunctionFS support is enabled. The configuration includes several gadget functions but appears to omit the FunctionFS option required for `ffs.adb`, which could directly explain why ADB remains unavailable.

**Checked config dependencies**

</details>

```json
{"find":[{"ref_id":"turn250354view0","pattern":"CONFIG_USB_CONFIGFS_F_FS"},{"ref_id":"turn250354view0","pattern":"CONFIG_USB_F_FS"},{"ref_id":"turn250354view0","pattern":"CONFIG_USB_CONFIGFS="}],"open":[{"ref_id":"https://gitlab.com/api/v4/projects/67348285/repository/files/drivers%2Fusb%2Fgadget%2FKconfig/raw?ref=halium-12.0"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
git clone --depth 1 --branch halium-12.0 https://gitlab.com/ubports/porting/community-ports/android12/rabbit-r1/kernel-rabbit-mt6765.git /tmp/r1kernel
```

<details><summary>💭 Thinking</summary>

**Cloned Halium kernel source for configuration inspection**

</details>

```json
{"system1_search_query":[{"q":"site:gitlab.com/ubports/porting/community-ports/android12/rabbit-r1/kernel-rabbit-mt6765 \"MTK_ANDROID_DEFAULT_SETTING\""},{"q":"site:gitlab.com/ubtouch-on-rabbit/android_kernel_rabbit_mt6765 \"MTK_ANDROID_DEFAULT_SETTING\""}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searching gitlab.com**

</details>

You do **not** need to add ADB support from scratch. The rabbit r1 port already has most of the Ubuntu Touch ADB stack wired up; the remaining problem appears to be the last part of USB gadget/FunctionFS bring-up and possibly some r1-specific USB configuration. UBports currently marks both **ADB and MTP as “Partial”** on the r1, running Ubuntu Touch 24.04/Noble. The port is actively maintained—the device repo had commits as recently as August 13, 2026. citeturn828928view0turn828928view1

### What is already implemented

The r1 overlay already has the normal `usb-moded` configuration:

```ini
IDVENDOR=0E8D
IDPRODUCT_MTP=2008
IDPRODUCT_MTP_ADB=201D
IDPRODUCT_RNDIS=2004
IDPRODUCT_RNDIS_ADB=2005
USB_MODED_ARGS=
```

Those values correspond exactly to the MediaTek example in the UBports porting documentation. So `usb-moded` already knows that developer mode should expose an MTP+ADB gadget as `0e8d:201d`. citeturn626371view3turn959999view0

There is also r1-specific Android init configuration:

```rc
on init
    setprop sys.usb.configfs 1
    setprop sys.usb.controller "musb-hdrc"
    setprop sys.usb.ffs.aio_compat 1

on fs
    write /sys/class/udc/musb-hdrc/device/cmode 2
    start adbd

on boot
    setprop sys.usb.configfs 1
    setprop vendor.usb.controller "musb-hdrc"
```

Most of that was added in the February 2025 commit specifically called `r1: Usb fixes`. citeturn626371view2turn561539view0turn959999view3

There is an important detail here, though: **Ubuntu Touch does not normally use the Android container's `adbd`.** `usb-moded` switches into `mtp_adb`, then starts the Ubuntu-side `adbd.service`. That service creates the ConfigFS `ffs.adb` function and mounts FunctionFS at `/dev/usb-ffs/adb`. Meanwhile, `lxc-android-config` deliberately deletes `/sbin/adbd` from the Android container. citeturn327934view0turn327934view1turn327934view2turn327934view3turn327934view4

So this line in the r1 Android rc:

```rc
start adbd
```

is **not the mechanism that should make ADB work on Ubuntu Touch**. I would treat it as an old workaround/leftover until proven otherwise.

### The most suspicious r1-specific issue

There is a fairly significant provenance problem with the USB configuration. The Git history for the current `device-specific-config.conf` says those VID/PID values were originally taken from:

```text
/vendor/etc/init/hw/init.mt6768.usb.rc
```

That commit dates to December 2022—before the rabbit r1 existed—and came from earlier port history. The rabbit uses **MT6765**, not MT6768. The generic MediaTek values may still be correct, but they should be verified against stock rabbitOS rather than assumed. citeturn959999view2turn828928view0

There is another thing I would verify before touching userspace. The r1 build specifies:

```text
deviceinfo_kernel_defconfig="r1_defconfig halium.config"
```

The r1 defconfig clearly has the MediaTek MUSB controller and several ConfigFS functions enabled, but neither of those two visible fragments explicitly contains `CONFIG_USB_CONFIGFS_F_FS`. The kernel tree's Android base configuration *does* specify `CONFIG_USB_GADGET=y`, `CONFIG_USB_CONFIGFS=y`, and `CONFIG_USB_CONFIGFS_F_FS=y`. Because the final Kconfig is generated/merged, this isn't proof that FunctionFS is missing—but it is important enough to check on the actual running kernel. citeturn626371view0turn250354view0turn666699view0turn905851view0turn930060view0

### What I would do first

Use the device's terminal or SSH and run these in order:

1. **Force ADB mode and inspect the actual gadget state.**

```bash
sudo touch /userdata/.force-adb
sudo reboot
```

UBports officially supports `/userdata/.force-adb` specifically for port bring-up. If authorization is getting in your way during development, `/etc/default/adbd` can temporarily use `ADBD_SECURE=0`. Don't ship a build that way. citeturn959999view0turn959999view1

After reboot:

```bash
systemctl status usb-moded.service adbd.service --no-pager

journalctl -b \
    -u usb-moded.service \
    -u adbd.service \
    --no-pager
```

Then:

```bash
ls -l /sys/class/udc

cat /sys/kernel/config/usb_gadget/g1/UDC 2>/dev/null

find /sys/kernel/config/usb_gadget/g1/functions \
    -maxdepth 1 -mindepth 1 -printf '%f\n' 2>/dev/null

mount | grep -E 'functionfs|usb-ffs'

ls -la /dev/usb-ffs/adb 2>/dev/null
```

And check the kernel configuration:

```bash
if [ -r /proc/config.gz ]; then
    zcat /proc/config.gz | grep -E \
      'CONFIG_USB_(GADGET|CONFIGFS|CONFIGFS_F_FS|F_FS|CONFIGFS_UEVENT)'
fi
```

At the PC, simultaneously run:

```bash
watch -n 0.5 lsusb
```

and:

```bash
ADB_TRACE=usb adb devices -l
```

The result tells you almost exactly which layer is broken. If **nothing new appears in `lsusb`**, look at `musb-hdrc`, UDC binding, peripheral mode and `cmode`. If it appears as **`0e8d:2008`**, the device stayed in MTP-only mode and `usb-moded` isn't performing the developer-mode transition. If it appears as **`0e8d:201d` but `adb devices` remains empty**, the USB controller/configfs portion is mostly working and you should concentrate on `adbd.service`, FunctionFS, authorization and host-side permissions. If `adbd.service` is running but there is no `functions/ffs.adb` or FunctionFS mount, that is almost directly the failure point, because UBports' ADB setup explicitly creates and mounts those. citeturn626371view3turn327934view0turn327934view1turn327934view2turn327934view3

### What I expect the eventual patch to look like

I **wouldn't add another ADB daemon or custom ADB startup script**. The Ubuntu Touch side already provides that.

First validate the final kernel config. If these are absent at runtime:

```text
CONFIG_USB_GADGET=y
CONFIG_USB_CONFIGFS=y
CONFIG_USB_CONFIGFS_F_FS=y
CONFIG_USB_CONFIGFS_UEVENT=y
```

I'd add the missing options to the r1's `arch/arm64/configs/halium.config` and rebuild the boot image. FunctionFS is specifically what supplies the userspace USB function used by `adbd`. citeturn930060view0turn905851view0

Then boot stock rabbitOS v0.8—the version UBports currently requires as the installation base—and measure the actual USB IDs/configuration rather than trusting the inherited MT6768 values. UBports' own documentation recommends deriving these values from the stock device's USB init/HAL or probing the Android USB modes. citeturn828928view0turn959999view0

I would also probably remove:

```rc
start adbd
```

from `init.mt6765.usb.rc` once the Ubuntu-side ADB path is verified. The Android container intentionally has its `adbd` executable removed; maintaining a second apparent ADB startup path makes diagnosis harder. citeturn626371view2turn327934view4

One complication is that there is currently an **open UBports `usb-moded` bug from March 2026** where Noble devices sometimes only become visible to ADB after unplugging/replugging. Reports include the OnePlus 5T and Fairphone 4, with ConfigFS-related messages in `usb-moded` logs. That doesn't establish that the rabbit has the same bug, but it's something to separate from the r1-specific issue during testing. citeturn903260view2

### How far along is it?

I'd describe it as **“the architecture is there; hardware bring-up/debugging isn't finished.”** You already have:

```text
Developer Mode
      │
      ▼
   usb-moded
      │
      ├── MTP
      │
      └── starts adbd.service
                │
                ▼
         FunctionFS ffs.adb
                │
                ▼
       ConfigFS USB gadget
                │
                ▼
           musb-hdrc
                │
                ▼
               PC
```

The r1 already has configuration for essentially every box in that chain. citeturn327934view0turn327934view1turn327934view2turn626371view2

So I would **not start by writing code**. Start by collecting those six pieces of runtime state. The particularly useful outputs are:

```bash
systemctl status adbd usb-moded
journalctl -b -u adbd -u usb-moded
ls -la /sys/kernel/config/usb_gadget/g1/functions/
cat /sys/kernel/config/usb_gadget/g1/UDC
mount | grep functionfs
zcat /proc/config.gz | grep -E 'USB_CONFIGFS|USB_F_FS'
```

If you paste those outputs from your r1, I can narrow it down to the exact layer and likely give you the specific change for the `rabbit-r1`/kernel repo rather than guessing.


---

> What’s the best way to do this work is there another debug interface or serial I can use ?

For this kind of USB bring-up, I’d avoid making ADB the only debug channel. I’m checking whether the r1 exposes a documented UART/test-point interface and which software-side channels survive early boot.

```json
{"system1_search_query":[{"q":"rabbit r1 UART serial test points teardown PCB MT6765"},{"q":"rabbit r1 schematic UART test point serial console"},{"q":"rabbit r1 Ubuntu Touch SSH serial console porting"},{"q":"site:gitlab.com/ubports/porting/community-ports rabbit r1 uart serial"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 18 websites**

**Planning the debug path**

I’m comparing independent access methods: Wi-Fi SSH avoids USB entirely, UART is best for early boot and kernel logs, and rescue USB networking could isolate ADB if the broader gadget stack still works.

**Planned the debug path**

**Expanding debug options**

I’m prioritizing Wi-Fi SSH for userspace, UART for boot and kernel output, persistent crash logs where available, and fastboot or BootROM recovery for controlled image testing. JTAG remains uncertain because its header and pinout aren’t established.

**Expanded debug options**

</details>

```json
{"open":[{"ref_id":"turn775388search12"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

iturn327230image0

Yes. The r1 has a **known, working hardware UART**, and for ADB bring-up I would use it. The TX/RX pads are visible on the right side of the mainboard in the iFixit photo above. A researcher used those exact pads to capture the r1's entire MediaTek boot chain. citeturn397007view0turn437983view0

The best development setup is **UART for boot/kernel logs + Wi-Fi SSH for an interactive shell + USB-C dedicated entirely to the thing you're debugging**. That way, when you break the USB gadget configuration, you don't simultaneously lose your debugger.

### 1. Wire up the UART

The pads are **1.8 V logic**. Although one researcher reported that his unit survived 3.3 V signaling, I would not rely on that; use a genuinely 1.8-V-capable USB-UART adapter or a level shifter. Do **not** connect the adapter's VCC pin. Connect only:

```text
Rabbit TX  ─────> USB-UART RX
Rabbit RX  <───── USB-UART TX
Rabbit GND ───── USB-UART GND
```

For initial work, you can connect **only Rabbit TX → adapter RX plus GND**. That's enough to capture logs and eliminates any chance of your adapter transmitting garbage into the r1. The documented boot baud rates are **115200 for BROM** and **921600 after BROM**. For Ubuntu Touch/ADB work, 921600 is the important one. citeturn397007view0

On the host:

```bash
picocom -b 921600 /dev/ttyUSB0
```

or:

```bash
screen /dev/ttyUSB0 921600
```

### 2. The current Ubuntu Touch kernel is already set up well for serial debugging

This is particularly useful: the current r1 kernel already enables the MediaTek UART driver and serial console support:

```text
CONFIG_SERIAL_8250=y
CONFIG_SERIAL_8250_CONSOLE=y
CONFIG_SERIAL_8250_NR_UARTS=2
CONFIG_SERIAL_8250_MT6577=y
```

It also has `CONFIG_DYNAMIC_DEBUG=y`, function tracing, and pstore support enabled. So you shouldn't need significant kernel work just to get useful debug output. citeturn223469view0

There is one inconsistency worth checking before changing anything. The current UBports MT6765 DT contains:

```text
console=tty0 console=ttyS0,921600...
```

and defines both `uart0` and `uart1`. citeturn793504view0turn800723view0

But David Buchanan's r1 research used:

```text
earlycon console=ttyS1,921600
```

for the physical debug UART. citeturn397007view0

So on your currently booting UT image, first run:

```bash
cat /proc/cmdline
dmesg | grep -Ei 'ttyS|uart|serial'
ls -l /dev/ttyS*
```

That will tell us whether the current build enumerates those physical pads as `ttyS0` or `ttyS1`.

The current r1 port's `deviceinfo_kernel_cmdline` does **not** explicitly contain `earlycon` or a serial console. citeturn597317view0 For a dedicated debug build I'd add the appropriate one, probably starting by testing:

```text
earlycon console=ttyS0,921600
```

and switching to `ttyS1` if the physical pads don't produce Linux output.

Once that is right, you should see kernel messages while USB is being initialized, which is exactly what you need.

### 3. Use Wi-Fi SSH as your normal shell

This should be your primary interactive debug connection. It is completely independent of the USB gadget problem.

Ubuntu Touch officially supports SSH using public-key authentication:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# put your PC's public key into:
~/.ssh/authorized_keys

chmod 600 ~/.ssh/authorized_keys

sudo systemctl enable --now ssh.socket
```

Then from the PC:

```bash
ssh phablet@<r1-wifi-ip>
```

UBports specifically recommends SSH for system debugging and supports enabling `ssh.socket` at boot. citeturn622935view1

This gives you a very productive setup:

```text
                   ┌──────── Wi-Fi ─────── SSH shell
                   │
Development PC ────┤
                   │
                   ├──────── UART ──────── kernel/boot logs
                   │
                   └──────── USB-C ─────── device under test
                                            MTP
                                            RNDIS
                                            ADB
                                            configfs
                                            FunctionFS
```

Now you can completely destroy/rebuild the USB gadget configuration and keep your shell open.

### 4. `usb-moded` rescue SSH is also extremely useful for this specific bug

Ubuntu Touch has another debugging mechanism that is almost tailor-made for your investigation. Create:

```bash
sudo rm -f /userdata/.force-adb
sudo touch /userdata/.force-ssh
sudo reboot
```

UBports says `.force-ssh` forces `usb-moded` into its **rescue USB-networking mode**. In that mode the phone exposes a network gadget, uses `10.15.19.82`, and runs an emergency SSH server on port `8022`. citeturn622935view2

Try on the host:

```bash
ip link
```

If necessary give the new USB network interface an address:

```bash
sudo ip addr add 10.15.19.100/24 dev <usb-interface>
sudo ip link set <usb-interface> up
```

Then:

```bash
ssh -p 8022 phablet@10.15.19.82
```

This experiment is extremely informative.

**If USB rescue SSH/RNDIS works but ADB doesn't**, you've established that:

```text
MUSB controller
    ↓
UDC
    ↓
ConfigFS
    ↓
USB enumeration
    ↓
RNDIS
```

are fundamentally functional.

Your investigation can then move upward to:

```text
ffs.adb
FunctionFS mount
adbd.service
usb-moded ADB mode creation
ADB authorization
```

Conversely, if rescue RNDIS also fails, I'd stop looking at `adbd` entirely and investigate the lower-level `musb-hdrc`/UDC/configfs/USB-role path. UBports documents rescue mode specifically as a porter debugging facility. citeturn622935view2

### 5. Turn on kernel USB debugging

The current r1 kernel has `CONFIG_DYNAMIC_DEBUG=y`. citeturn223469view0 That means once Wi-Fi SSH is running you can get substantially more information from the MUSB driver without blindly adding `printk()` calls.

First look at what's available:

```bash
sudo mount -t debugfs debugfs /sys/kernel/debug 2>/dev/null || true

sudo grep -iE 'musb|configfs|functionfs|f_fs' \
    /sys/kernel/debug/dynamic_debug/control | head -100
```

You can then selectively enable the relevant MUSB messages. For example, depending on the source paths shown by that command:

```bash
echo 'file drivers/usb/musb/* +p' | \
    sudo tee /sys/kernel/debug/dynamic_debug/control
```

Then use two terminals:

```bash
sudo dmesg -w
```

and:

```bash
sudo journalctl -f \
    -u usb-moded.service \
    -u adbd.service
```

Now plug/unplug the USB cable and toggle developer mode. You'll see both the kernel side and userspace side in real time.

### 6. You also have a very good brick-recovery mechanism

The r1's MediaTek platform gives you another interface below Linux entirely: **BROM/Preloader USB**.

The r1 can be forced into BROM USB mode by grounding a test pad near the reset button while resetting; the pad is reportedly accessible through the SIM-slot area. Researchers have used `mtkclient` and MediaTek Download Agents against this interface. citeturn397007view0turn437983view2

That makes the r1 unusually nice for kernel/boot experimentation:

```text
Normal boot broken
       ↓
Fastboot if available
       ↓
BROM/Preloader USB
       ↓
mtkclient / recovery / reflash
```

I'd make sure you know how to enter BROM and have backups of important partitions **before** starting to iterate on USB/kernel changes.

### What about JTAG?

There may be one. Buchanan noted what looked like an **unpopulated JTAG header**, but he hadn't investigated or mapped it. citeturn397007view0

I wouldn't spend any time on JTAG for this problem. UART already gives you bootloader/kernel visibility, SSH gives you interactive access, and the MediaTek BROM interface gives you recovery. JTAG would add considerable reverse-engineering work without giving you much that you need for an ADB gadget issue.

### The setup I'd actually build

I'd dedicate one r1 to port development, open the rear, attach thin wires permanently to **TX/RX/GND**, and add strain relief. Then keep these running on the host:

```bash
# Terminal 1
picocom -b 921600 /dev/ttyUSB0

# Terminal 2
ssh phablet@<r1-ip>

# Terminal 3
sudo dmesg -w

# Terminal 4
watch -n .5 'lsusb; echo; ip -br link'
```

Then test USB modes in this order:

```text
1. USB completely unconfigured
2. .force-ssh / RNDIS
3. plain MTP
4. plain ADB
5. MTP + ADB
```

That should let you identify the broken layer much faster than trying patches blindly.

**For this r1 ADB issue in particular, I would do UART + Wi-Fi SSH first, then test `.force-ssh`.** Those three things will probably tell us within one debugging session whether the actual failure is MediaTek MUSB/UDC, ConfigFS, or FunctionFS/adbd.


---

> What 1.8v units are out there ?

For the r1, the cleanest choice is a **USB-UART adapter whose I/O logic is explicitly 1.8 V**, not merely one that has a “1.8 V” power pin. I’ll separate true 1.8 V UART interfaces from boards that need a level shifter.

```json
{"product_query":{"search":["FTDI 1.8V USB UART TTL-232R-1V8 cable","USB UART 1.8V logic adapter","1.8V USB serial TTL adapter FT232"]},"system1_search_query":[{"q":"site:ftdichip.com TTL-232R-1V8 1.8V USB TTL serial cable"},{"q":"site:ftdichip.com TTL-232RG-VREG1V8-WE 1.8V UART"},{"q":"site:adafruit.com 1.8V UART level shifter USB serial"},{"q":"site:sparkfun.com 1.8V UART level shifter USB serial"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 7 websites**

</details>

Yes. For the r1 I’d buy a **native 1.8 V USB-UART adapter** rather than putting a level shifter in between.

products{"selections":[["turn199599product0","FTDI TTL-232RG-VREG1V8-WE 1.8V UART Cable"],["turn199599product7","Coolgear Selectable 1.8V TTL/CMOS USB Adapter"],["turn199599product4","CH343G 5V/3.3V/2.5V/1.8V USB-UART"],["turn199599product1","FT232 USB-to-TTL Multi-Voltage Module"],["turn199599product6","FTDI USB-to-TTL Multi-Voltage Cable"],["turn199599product9","FT232RL Multi-Voltage USB-UART Module"],["turn199599product11","FT232RL 1.8V/3.3V USB-UART Adapter"],["turn199599product13","FT232RL 1.8V/3.3V/5V Module"]],"tags":["Best choice","Robust bench option","Good inexpensive option","Multi-voltage","Cable format","Adjustable module","Budget option","Budget option"]}

My choices would be:

- **FTDI TTL-232RG-VREG1V8-WE — best overall.** This is an actual FTDI product specifically designed for **1.8 V UART logic**, rather than a generic FT232 board with questionable jumper labeling. It supports up to **3 Mbaud**, so the r1's 921600-baud console is comfortably within range. FTDI also provides a 1.8 V/100 mA output, though I would **not use it to power the r1**—connect GND, RX and TX only. citeturn199599search0turn199599search3
- **Coolgear USB-2323TTLMOS — good bench tool.** It has selectable **1.8/2.5/3.3/5 V logic levels**, so it's useful for other embedded devices too. The terminal block is convenient if you're going to leave wires attached to a development r1. citeturn388180search1
- **Waveshare CH343 USB UART Board — good inexpensive reusable option.** The CH343 supports UART I/O at **1.8, 2.5, 3.3 and 5 V**, up to 6 Mbps. One caveat: for 1.8 V operation, Waveshare says you remove the normal voltage jumper and provide an external 1.8 V reference to the I/O supply. citeturn388180search0turn388180search2
- **Pi Hut FT232 module — inexpensive direct option.** Their current module explicitly lists **5 V / 3.3 V / 1.8 V TTL output**. citeturn388180search6

### What I'd buy for your r1

I'd spend the ~$30–45 and get the genuine:

**FTDI `TTL-232RG-VREG1V8-WE`**

It removes a variable from the debugging process. With some cheap FT232RL boards, a jumper labelled `1.8V` can mean the **power output** is 1.8 V while TX still swings at another voltage. The genuine FTDI cable explicitly specifies **1.8-V UART signal levels**. citeturn199599search0

Wire it:

```text
FTDI GND  ───────── r1 GND
FTDI RXD  <──────── r1 TX
FTDI TXD  ────────> r1 RX

FTDI 1.8V ── X     DO NOT CONNECT
```

For the first test, I'd actually use only:

```text
FTDI GND  ───────── r1 GND
FTDI RXD  <──────── r1 TX
```

That gives you a **receive-only console**, so there is essentially no chance of the UART adapter driving something incorrectly on the r1. Once you confirm clean boot output at `921600`, add TX.

Then:

```bash
picocom -b 921600 /dev/ttyUSB0
```

For what we're doing with Ubuntu Touch, **the genuine 1.8-V FTDI cable is the one I'd choose**. The Coolgear is attractive if you want a more general-purpose embedded debugging tool for 1.8/2.5/3.3/5-V devices.

