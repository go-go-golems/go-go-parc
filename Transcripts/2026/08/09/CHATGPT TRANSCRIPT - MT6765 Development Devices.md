# MT6765 Development Devices

- URL: https://chatgpt.com/c/6a787b5f-f930-83ea-bef3-2b649715ef14
- Created: 2026-08-09T13:06:55.766Z

---

> Other devices with MT6765 Android/Linux platform that I could program on? I have a rabbit r1 but don’t want to brick it

The safest substitute is a cheap, bootloader-unlockable phone using the same MT6765/Helio P35 family. I’ll separate “same SoC” from “actually useful for low-level experimentation,” because those are not the same thing.

```json
{"system1_search_query":[{"q":"MT6765 Helio P35 devices bootloader unlock kernel source Samsung Galaxy A12 SM-A125F MT6765"},{"q":"site:github.com MT6765 device tree Android MT6765 Helio P35"},{"q":"MT6765 phone list Helio P35 official specs Oppo A5s vivo Y17 Nokia 2.4"},{"q":"Rabbit R1 MT6765 Helio P35 specs"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 21 websites**

</details>

One especially relevant non-phone option turned up: the **Senraise H10**, an MT6765 handheld/POS device with postmarketOS work and reported near-mainline Linux support. That is closer to a “Linux hacking target” than most carrier phones.

```json
{"system1_search_query":[{"q":"Senraise H10 MT6765 GitHub Linux mainline device tree"},{"q":"Vsmart Star 4 MT6765 bootloader unlock GitHub postmarketOS"},{"q":"Samsung Galaxy A04 MT6765 bootloader unlock postmarketOS Linux"},{"q":"LG K40 MT6765 bootloader unlock postmarketOS"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 10 websites**

**Comparing device targets**

I’m separating exact SoC matches from practical development targets. Vortex CG65 looks like the strongest sacrificial Android candidate, while Senraise H10 may be better for Linux experimentation. I’ll flag unlockability, RAM, kernel support, and variant differences.

**Compared device targets**

</details>

Yes. The **MT6765 / Helio P35** has several much cheaper devices you can use as sacrificial development hardware. The Rabbit r1 itself is confirmed to use the Helio P35/MT6765 with Cortex-A53 cores and PowerVR GE8320. citeturn797376search1turn797376search9

My picks would be:

| Device | MT6765/P35 | Why useful | Recommendation |
|---|---|---|---|
| **Vortex CG65** | ✅ | Android 13, 4 GB RAM, A/B, Treble, TWRP/OFRP tree, ROM tree, stock dump | **Best overall** |
| **Senraise H10** | ✅ | postmarketOS work; particularly interesting for Linux/mainline experimentation | **Best Linux target** |
| **LG K40** | ✅ | postmarketOS work; MTKClient-based unlocking documented | Good cheap target |
| **OPPO A12 / A11k** | ✅ | Device trees + MT6765 kernel source available | Good for Android/AOSP work |
| **OPPO A5s** | ✅ | MT6765 kernel/device-tree work exists | Good older cheap option |
| **Samsung Galaxy A04** | ✅ | postmarketOS work exists | Okay, but bootloader situation matters |
| **Vsmart Star 4** | ✅ | postmarketOS images/community work | Interesting, but unlocking is less convenient |

### I would buy a Vortex CG65

It's unusually well suited to what you're describing. Community work identifies it as:

- MT6765 / Helio P35
- 4 GB RAM
- Android 13
- Linux 4.19.191
- A/B partitions
- Project Treble
- existing TWRP/OFRP device tree
- custom-ROM device tree
- vendor tree / stock ROM dumps

There is also documented CG65 bootloader/root/custom-ROM work. citeturn294084search2turn294084search13turn294084search18

That gives you a disposable platform for experimenting with **boot images, DTBs/DTBOs, AVB, recovery, Android init, kernel builds, AOSP, MTKClient and partition layouts** before touching the r1.

The **Senraise H10** is more interesting if your goal is actual Linux rather than Android ROM development. postmarketOS specifically lists it as an MT6765 device and indicates work toward close-to-mainline Linux. citeturn294084search14

### One important limitation

Don't treat another MT6765 device as an r1 clone.

The CPU/SoC may be the same, but the r1 has its own **PMIC configuration, display, touch controller, rotating camera/motor, GPIO assignments, partition layout, DTB/DTBO and bootloader configuration**. So an OPPO/Vortex/Samsung `boot.img`, `preloader`, `lk`, `vendor_boot`, or DTB should **never** be flashed onto the Rabbit just because both say MT6765.

The useful transferable part is the knowledge and tooling—not the firmware images.

For example, OPPO has publicly available MT6765 kernel sources, and there are AOSP device trees for the A11k/A12/A5s family. citeturn294084search10turn294084search21

### For keeping your r1 unbricked

Before doing anything involving writes, I would make your first Rabbit project **recovery**, not customization:

1. Dump its partition table and every important partition.
2. Preserve **preloader, bootloader, boot/vendor_boot, vbmeta, dtbo, super/vendor/system and NVRAM/NVDATA/protect partitions**.
3. Save the dumps and SHA-256 hashes on your computer and somewhere else.
4. Verify that you can enter MediaTek preloader/BROM mode from a completely powered-off r1.
5. Prefer temporarily booting an image over flashing it wherever possible.
6. Don't modify `preloader` until you have a proven unbrick procedure.

The r1 is slightly awkward because it doesn't have normal volume keys; current community documentation notes that fastboot entry involves its MediaTek preloader interface rather than the usual phone key combination. citeturn797376search19

If you tell me whether you're mainly interested in **(a) custom Android/AOSP, (b) kernel/driver development, or (c) booting real Linux/postmarketOS**, I can also give you a specific MT6765 development setup and the safest device to buy for it.

