# Makera Z1 Smoothieware Support

- URL: https://chatgpt.com/c/6a7fadeb-47cc-83ea-8d04-e70ef43a91a2
- Created: 2026-08-15T00:08:18.021Z

---

> smoothie firmware makera z1 support

I’m checking whether the Makera Z1’s controller can run Smoothieware directly, and whether there’s any community port or compatible replacement-controller route.

```json
{"system1_search_query":[{"q":"Makera Z1 Smoothieware support firmware controller"},{"q":"Makera Z1 CNC controller firmware Smoothieboard Smoothieware"},{"q":"site:makera.com Z1 firmware controller"},{"q":"site:github.com Makera Z1 firmware"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 13 websites**

</details>

The key distinction is: **Makera’s firmware lineage is Smoothieware-based, but that does not mean upstream Smoothieware is a drop-in Z1 firmware.** I’m verifying whether a Z1-specific community binary exists before recommending any flashing.

```json
{"system2_search_query":[{"q":"site:github.com/Carvera-Community/Carvera_Community_Firmware Z1 release"},{"q":"site:github.com/Carvera-Community/Carvera_Community_Firmware \"Z1\""},{"q":"site:github.com/MakeraInc/CarveraFirmware \"Z1\" firmware.bin"},{"q":"site:wiki.makera.com/en/z1 firmware update"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Checking Z1 support**

I’m finding that Makera firmware is based on a Smoothieware fork, while community projects mention initial Z1 support. I’m not seeing confirmation that generic upstream Smoothieware is a safe drop-in replacement, so machine-specific features may be at risk.

**Checked Z1 support**

**Searched 4 websites**

</details>

Yes, but with an important limitation: **the Makera firmware family is based on Smoothieware, but generic/upstream Smoothieware is not currently documented as a drop-in firmware for the Makera Z1.**

Makera’s official firmware repository explicitly describes its Carvera firmware as a branch of Smoothieware for LPC17xx controllers. citeturn742835view0turn194704search3 Makera’s documentation also states that its CNC firmware is based on Smoothieware. citeturn194704search6

For the **Z1 specifically**, the Carvera Community Controller added initial Z1 support and contains fixes specifically handling the Makera Z1 firmware, so third-party control of the Z1 is already developing. citeturn742835view3turn194704search2 The community CAM/profile project has also added Z1 machine definitions for Fusion 360 and FreeCAD. citeturn223204search4

I would **not flash vanilla Smoothieware onto a Z1**. I found no upstream Smoothieware release or documented Z1 configuration that Makera says is safe for the machine. The Z1 has machine-specific features such as its controlled spindle, probing, quick tool-change system, optional laser/4th axis, Wi-Fi, and other integrated functions, so a generic build would need the correct board configuration and Makera-specific extensions. The Z1 hardware itself uses NEMA 17 steppers (closed-loop on the Z1 Pro), a 150 W closed-loop spindle, and optional rotary/laser hardware. citeturn742835view1

So, as of **August 2026**:

- **Makera Z1 stock firmware:** yes, Smoothieware-derived.
- **Carvera Community Controller:** Z1 support exists. citeturn194704search2
- **Carvera Community Firmware:** I would not assume Z1 flashing support yet; its repository still describes the firmware primarily as being for the Carvera. citeturn194704search0
- **Vanilla Smoothieware:** no confirmed drop-in Z1 support.

If your goal is to **modify/compile the Z1 firmware yourself**, I can dig into the Makera source tree and identify the Z1 board/MCU, pin mapping, build flags, bootloader, and what would be required to make a Z1-specific Smoothieware build.

