# dm-verity corruption fix

- URL: https://chatgpt.com/c/6a7628c6-4a44-83ea-a0bd-abacd6197c7c
- Created: 2026-08-07T18:49:44.290Z

---

> I am seeing "dm-verity corruption" after booting my rabbit-r1, I found this to maybe help:
>
> https://github.com/jonathanprocter/rabbit-r1-deverity-recovery/blob/main/docs/rabbit-r1-de-verity-recovery-community-writeup.md
>
> I have been using https://github.com/RabbitHoleEscapeR1/r1_escape first to go into flashboot, and then I ran these commands

I’ll compare both procedures to isolate the verity failure. Paste the commands and complete terminal/device output; meanwhile, don’t flash, erase, factory-reset, or relock anything.

<details><summary>💭 Thinking</summary>

**Clarifying the next step**

I’m seeing the repository links, but not the commands or their output yet. Please paste the exact commands, responses, and current goal so I can trace the issue accurately without guessing.

**Awaiting command details**

I’m ready to trace the failure, but the actual commands and output still aren’t included. Please paste them exactly, along with the device’s current mode and any error text, while redacting serial numbers or personal paths.

**Awaited command details**

**Assessed r1_escape recovery documentation and dm-verity steps**

**Requesting exact outputs**

I still need the commands and complete responses to diagnose this safely. Please paste them, plus whether the device reaches recovery or fastboot. I’ll distinguish a mismatched image, wrong slot, or incomplete flashing before suggesting any write operation.

**Requested exact outputs**

**Narrowing the diagnosis**

I’m separating bootloader state, active slot, and image consistency before recommending repairs. Please send the exact command transcript and platform-tools version; I’ll avoid further flashing until those details identify the mismatch.

**Narrowed the diagnosis**

**Documented Rabbit R1 dm-verity recovery and restoration paths**

</details>

```json
{"paths":["GitHub"],"query":"content"}
```

It looks like the commands and output did not come through. Paste them exactly as displayed, preferably in a fenced code block.

For now, **do not**:

- Relock the bootloader.
- Flash any `vbmeta_disabled*.img` files.
- Erase or overwrite `seccfg`.
- Erase `preloader`, `nvram`, `nvdata`, `protect1`, or `protect2`.
- Repeatedly reboot the device, because repeated failed A/B boots can exhaust slot retry counts.

The `r1_escape` process unlocks the bootloader, disables AVB, and flashes a userdebug AOSP system image. fileciteturn1file0L2-L2 The recovery write-up specifically warns that relocking while disabled or modified vbmeta images are installed can produce signature and bad-state failures; its raw `seccfg` procedure is a last-resort repair, not the first step. fileciteturn0file0L2-L2

While the r1 is still in **fastboot**, these commands are read-only and useful for diagnosis:

```bash
fastboot devices

fastboot getvar current-slot
fastboot getvar slot-retry-count:a
fastboot getvar slot-unbootable:a
fastboot getvar slot-successful:a
fastboot getvar slot-retry-count:b
fastboot getvar slot-unbootable:b
fastboot getvar slot-successful:b

fastboot getvar unlocked
fastboot getvar secure
```

Fastboot often writes results to stderr, so capture everything with:

```bash
{
  fastboot devices
  fastboot getvar current-slot
  fastboot getvar slot-retry-count:a
  fastboot getvar slot-unbootable:a
  fastboot getvar slot-successful:a
  fastboot getvar slot-retry-count:b
  fastboot getvar slot-unbootable:b
  fastboot getvar slot-successful:b
  fastboot getvar unlocked
  fastboot getvar secure
} 2>&1
```

Paste:

1. The commands you already ran.
2. Their complete output.
3. The exact on-screen error.
4. Whether the bootloader is currently unlocked.
5. Whether you used stock `vbmeta.img` or a disabled/custom vbmeta image.
6. Your computer OS: Windows, Linux, or macOS.

