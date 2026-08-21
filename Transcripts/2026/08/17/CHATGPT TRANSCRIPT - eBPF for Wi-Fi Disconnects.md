# eBPF for Wi-Fi Disconnects

- URL: https://chatgpt.com/c/6a807b52-8b68-83ea-9b5f-244e596c32e4
- Created: 2026-08-15T14:45:48.294Z

---

> My wifi disconnects often on the rabbit r1 and I’m pretty sure it’s something with the drivers power saving (in Ubuntu), but I think I can’t pinpoint it exactly from nm logs and kernel logs. what could I achieve with ebpf ? Since the device disconnects it’s often tedious to collect data after reconnecting, here we could potentially log while we’re disconnected as well

<details><summary>💭 Thinking</summary>

**Planning Wi‑Fi observability**

I’m mapping eBPF to Ubuntu’s wireless stack: driver events, mac80211/cfg80211 behavior, power-management transitions, interrupts, wakeups, and packet activity. I’ll distinguish observability from actually fixing firmware or hardware power states.

**Planned Wi-Fi observability**

</details>

Yes—eBPF is well suited here because it can keep tracing locally in the kernel while Wi-Fi is down, then persist the event stream to local storage for inspection after reconnect. The useful part is correlating **power-management callbacks → driver/mac80211/cfg80211 events → carrier loss/disconnect reason**, rather than trying to infer that sequence from NetworkManager logs alone.

```json
{"system2_search_query":[{"q":"site:kernel.org Linux tracepoints cfg80211 mac80211 power runtime_pm eBPF tracepoints"},{"q":"site:docs.kernel.org BPF ring buffer tracing fentry kprobe tracepoints"},{"q":"site:github.com/torvalds/linux include trace events cfg80211 runtime_pm_callback trace power.h"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

**Tracing the failure path**

I’m narrowing the design to a local eBPF flight recorder: capture wireless stack transitions, runtime power events, interrupts, wakeups, and driver calls, then persist evidence when connectivity fails—even without network access.

**Traced the failure path**

</details>

The key distinction is **802.11 power save** versus **device runtime PM**. They can fail in similar-looking ways, but eBPF can tell you which transition happens first. On mac80211 drivers, there are tracepoints for driver suspend/resume and configuration changes including the virtual-interface `ps` state; separately, the runtime-PM core exposes `rpm_suspend`, `rpm_resume`, `rpm_status`, and return values for the actual device.

```json
{"find":[{"ref_id":"turn156086view0","pattern":"disconnect"},{"ref_id":"turn156086view0","pattern":"deauth"},{"ref_id":"turn156086view0","pattern":"roam"},{"ref_id":"turn156086view0","pattern":"cqm"},{"ref_id":"turn260084view3","pattern":"connection_loss"},{"ref_id":"turn260084view3","pattern":"beacon"},{"ref_id":"turn260084view3","pattern":"set_key"},{"ref_id":"turn260084view3","pattern":"sta_state"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Tracing failure evidence**

I’m focusing on a local eBPF flight recorder that preserves events during outages. It can correlate Wi‑Fi power-save changes, runtime suspend/resume, driver callbacks, interrupts, wakeups, and disconnect timing for later analysis.

**Traced failure evidence**

</details>

```json
{"system2_search_query":[{"q":"site:bpftrace.org docs tracepoint bpftrace -l -lv kprobe kstack current"},{"q":"site:kernel.org Linux eBPF ring buffer BPF_MAP_TYPE_RINGBUF documentation"},{"q":"site:docs.kernel.org tracepoints power runtime pm rpm_status rpm_suspend"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 5 websites**

</details>

For a first capture, I would **not start by writing a custom eBPF program**. Use the existing kernel tracepoints as the baseline “black box”; then add BPF only where you need filtering, stacks, per-device state, or a trigger around the failure. Tracepoints are generally a more stable attachment surface than arbitrary kprobes.

```json
{"system1_search_query":[{"q":"site:github.com/torvalds/linux net/wireless/trace.h cfg80211 disconnected trace event"},{"q":"site:github.com/torvalds/linux net/mac80211/trace.h drv_vif_cfg_changed drv_suspend drv_resume"},{"q":"site:github.com/torvalds/linux include/trace/events/rpm.h rpm_suspend rpm_status rpm_return_int"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching raw.githubusercontent.com**

</details>

Yes. In this case eBPF is most useful as a **kernel-side flight recorder**. The Wi-Fi connection itself is irrelevant to collection: the probes keep running while the interface is disconnected, and a local userspace process can continuously append the events to disk. One caveat is that a BPF ring buffer itself is memory-backed, so for evidence you want to keep, have the collector drain it into a file rather than relying on the ring buffer alone. citeturn505781search0

What I would try to determine is the exact ordering around one failure:

1. Did runtime PM suspend the Wi-Fi device?
2. Did 802.11 power-save state change?
3. Did the firmware/driver stop responding?
4. Did the driver report a disconnect to cfg80211?
5. Was the disconnect locally generated or caused by the AP/link?
6. Did a resume happen, and did it return an error?
7. Which kernel call path initiated the suspicious transition?

That is exactly the sort of cross-layer timeline where eBPF is much better than looking at `journalctl -u NetworkManager` and `dmesg` independently.

### First, establish which PM mechanism you're dealing with

There are two different things that are easy to conflate.

**802.11 power saving** is part of the Wi-Fi stack/driver. On a mac80211-based driver, the kernel has tracepoints such as `drv_vif_cfg_changed`; its trace payload includes the current `ps` state. `drv_config` exposes things including `power_level` and `dynamic_ps_timeout`. There are also `drv_suspend`, `drv_resume`, and `drv_stop` events. citeturn854967view2turn854967view3

**Runtime PM** is the generic Linux device power-management layer underneath it. Current kernels expose `rpm_suspend`, `rpm_resume`, `rpm_idle`, `rpm_usage`, `rpm_return_int`, and `rpm_status`; critically, these include the device name, PM state and—in the return event—the return code. citeturn854967view4turn854967view5

So I'd start by identifying what the actual R1 Ubuntu driver looks like:

```bash
IF=wlan0

uname -a
ethtool -i "$IF" 2>/dev/null
readlink -f /sys/class/net/"$IF"/device
readlink -f /sys/class/net/"$IF"/device/driver
iw dev "$IF" get power_save
```

Then see what trace infrastructure your exact kernel provides:

```bash
sudo bpftrace -l 'tracepoint:rpm:*'
sudo bpftrace -l 'tracepoint:power:*'
sudo bpftrace -l 'tracepoint:cfg80211:*'
sudo bpftrace -l 'tracepoint:mac80211:*'
```

`bpftrace -l` is specifically intended for discovering probes supported by the running system; `-lv` will also show their argument layouts. citeturn505781search1turn505781search4

For example:

```bash
sudo bpftrace -lv 'tracepoint:rpm:rpm_suspend'
sudo bpftrace -lv 'tracepoint:rpm:rpm_return_int'
sudo bpftrace -lv 'tracepoint:mac80211:drv_vif_cfg_changed'
```

### I would actually start with `trace-cmd`

You don't need eBPF merely to solve the "I lose Wi-Fi and can't collect anything" problem. Kernel tracing already works locally while networking is unavailable, and Linux wireless specifically documents tracing the `cfg80211` and `mac80211` trace systems with `trace-cmd`. citeturn491458search18

See what's available:

```bash
sudo trace-cmd list -e | grep -E '^(rpm|power|cfg80211|mac80211):'
```

If those groups exist, something along these lines gives you a very useful first recording:

```bash
sudo trace-cmd record \
    -o /var/tmp/r1-wifi.trace \
    -e rpm \
    -e cfg80211 \
    -e mac80211 \
    -e power:device_pm_callback_start \
    -e power:device_pm_callback_end
```

Leave that running until the failure occurs. Reconnect whenever convenient, stop it, then:

```bash
sudo trace-cmd report /var/tmp/r1-wifi.trace > /var/tmp/r1-wifi.txt
```

Now instead of trying to line up two journals, you might see a sequence resembling:

```text
... rpm_suspend       wifi-device ...
... rpm_status        wifi-device -> SUSPENDED
... drv_vif_cfg_changed ... ps=...
... rpm_resume        wifi-device ...
... rpm_return_int    wifi-device ret=-...
... cfg80211 / driver disconnect activity ...
```

If the same sequence repeats before every outage, you've got a much stronger causal lead.

### Where eBPF becomes substantially more useful

After the first trace, I'd use BPF to make the recording **stateful and triggered** rather than just recording everything.

For example, your BPF program could remember:

```text
last runtime suspend
last runtime resume
last Wi-Fi PS transition
last association state
last driver PM callback return
last 20 interesting events
```

Then when a disconnect occurs, emit one structured record containing that history and kernel stack(s).

An especially interesting probe is `cfg80211_disconnected()` **if it exists in your kernel and is probeable**. In current upstream Linux that function receives the netdevice, 802.11 reason code, and a `locally_generated` boolean. Internally cfg80211 eventually reports whether the disconnection came from the AP. citeturn695720view0turn695720view2

So first:

```bash
sudo bpftrace -l 'kprobe:*cfg80211*disconnect*'
sudo bpftrace -l 'fentry:*cfg80211*disconnect*'
```

If `cfg80211_disconnected` is available, a probe there is potentially extremely revealing because you can distinguish something like:

```text
runtime_suspend
     ↓
driver gets unhappy
     ↓
cfg80211_disconnected(reason=..., locally_generated=true)
```

from:

```text
AP deauth/disassoc / link-loss handling
     ↓
cfg80211_disconnected(...)
     ↓
power-management activity afterwards
```

Those are very different bugs.

And this is where eBPF adds something plain kernel logs usually don't: on a suspicious function you can capture a `kstack()` and discover **who actually got you there**. bpftrace supports kernel-function probes and stack aggregation/capture for exactly this kind of tracing. citeturn505781search6turn505781search12

### You can also do a very clean A/B diagnosis

Before doing anything invasive, I'd run three separate experiments.

Baseline: everything as it is now.

Then disable only Wi-Fi PS:

```bash
sudo iw dev wlan0 set power_save off
iw dev wlan0 get power_save
```

Linux wireless documents `iw ... set power_save` as the interface for this power-save mode. citeturn446209search7

Separately, if you identify the correct backing device and it exposes runtime PM:

```bash
DEV="$(readlink -f /sys/class/net/wlan0/device)"

cat "$DEV/power/control"
cat "$DEV/power/runtime_status"
```

For a diagnostic run, setting:

```bash
echo on | sudo tee "$DEV/power/control"
```

forbids runtime PM for that device; `auto` allows runtime PM again. This can increase power consumption, so I would use it as an isolation test rather than immediately treating it as the fix. citeturn446209search3

Do **not** disable both mechanisms for the first experiment. If:

```text
802.11 PS off       -> still disconnects
runtime PM off      -> disconnects disappear
```

you've narrowed it considerably.

If the inverse happens, you've isolated a different layer.

### One R1-specific complication

I wouldn't assume the R1's Ubuntu Wi-Fi driver is a normal upstream mac80211 driver. Rabbit's published kernel/module source contains a vendor `connectivity/wlan` tree with multiple MediaTek driver generations and separate Wi-Fi power-management/glue components. That means the exact Ubuntu port may expose only some of the mac80211 events—or none—and the most valuable probes may instead be directly inside the MediaTek module. citeturn826277view0turn304826view0turn304826view1

That's actually another place where eBPF helps. Once we know the module, we can inspect its available symbols:

```bash
DRIVER=$(basename "$(readlink -f /sys/class/net/wlan0/device/driver)")
echo "$DRIVER"

sudo bpftrace -l "kprobe:${DRIVER}:*" | \
    grep -Ei 'suspend|resume|power|sleep|wake|disconnect|reset|timeout|fw'
```

The exact syntax/support will depend on how that kernel and module were built, so I wouldn't write those probes blind.

**If you paste the output of these four commands:**

```bash
uname -r
ethtool -i wlan0
readlink -f /sys/class/net/wlan0/device/driver
sudo bpftrace -l 'tracepoint:{rpm,power,cfg80211,mac80211}:*'
```

I can narrow this to the R1's actual driver and construct a small bpftrace "Wi-Fi flight recorder" that writes a timestamped local log and captures the relevant PM/disconnect sequence rather than generating megabytes of indiscriminate tracing.

