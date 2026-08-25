---
title: Wyze Cam v2 — Direct Frame-Bus Streaming and Browser-Direct WebRTC
aliases:
  - Wyze Cam v2 capstone report
  - WYZECAM-DIRECT-STREAM final report
  - framebus + webrtc end state
tags:
  - project
  - embedded
  - firmware
  - streaming
  - rtsp
  - webrtc
  - ipc
  - go
  - mips
  - openmiko
  - kernel
  - optimization
  - reliability
status: active
type: project
created: 2026-08-25
repo: /home/manuel/code/wesen/2026-08-23--wyze-cam
---

# Deep-Dive Project Report: Direct Frame-Bus Streaming and Browser-Direct WebRTC on a Wyze Cam v2

This report is the capstone of a multi-phase engineering project on the Wyze Cam v2, an Ingenic T20-based IP camera running OpenMiko. It documents the full arc of work: from the discovery of a 31.69 MiB hidden memory cost in the stock streaming pipeline, through the design and implementation of a userspace frame-bus transport that eliminates it, the on-camera deployment and the IMP-lifecycle problems that had to be solved, the self-healing watchdog that keeps the stream stable, and the addition of a WebRTC endpoint that serves browsers directly from the camera over the LAN without a host bridge. It is written for an engineer who needs to understand the complete system, the decisions that shaped it, and the evidence that validates each part. It draws from the design documents and the fourteen-step investigation diary committed to the project ticket, and it is the successor to four prior reports that documented each phase as it was built.

The central result is measured and verified on the live camera. Removing the two `v4l2loopback` devices and replacing them with a userspace `AF_UNIX / SOCK_SEQPACKET` frame bus recovers 31.69 MiB of `vmalloc` and 23.96 MiB of free RAM, while delivering a verified H.264 Constrained Baseline 1920×1080 stream at 25 frames per second. A pion/webrtc endpoint added to the Go server serves this same stream directly to browsers at `http://192.168.0.55:8555/webrtc` with approximately one second of latency, over the LAN, with no host process. RTSP is preserved for VLC and NVR. A healthz-based watchdog restarts the capture process automatically when the camera's ISP firmware wedges. The system is persistent: it survives a reboot, with binaries on a vfat SD card and init scripts in the jffs2 overlay.

The architecture is additive, not replacing. The closed-source Ingenic `libimp` ownership stays in the existing C capture process. The Go streaming server consumes encoded frames over a userspace socket instead of a kernel loopback device. RTSP stays for the ecosystem. WebRTC is added alongside it, not instead of it. Each layer is config-gated and independently restartable.

> [!summary]
> - The motivating problem was structural: two 1080p `v4l2loopback` devices each reserve a 16,592,896-byte `vmalloc` backing store (`1920×1080×4×2 + 4096`), totaling 31.69 MiB — nearly all of the camera's 35,532 KiB `VmallocUsed` — even though the encoded H.264 and JPEG payloads are kilobytes. In stock mode the camera had 1,796 KiB free and was constantly swapping.
> - The bypass is a single sink substitution: the OpenMiko `videocapture` process already receives complete `IMPEncoderStream` objects in userspace (with sequence, timestamp, per-pack addresses, lengths, and NAL types) immediately before one `write()` to the loopback. Replacing that one `write()` with a frame-bus publish removes the kernel ownership without touching the sensor, ISP, encoder, or kernel.
> - The frame bus is a fragmented `AF_UNIX / SOCK_SEQPACKET` socket with a 56-byte big-endian wire protocol (verified by three independent implementations: C, Go, and Python golden vectors). The producer is nonblocking (drop-not-block, exactly-one `IMP_Encoder_ReleaseStream`); the consumer is bounded (soft caps, reset on sequence gap).
> - Persistence is a run-from-sdcard hybrid: the SD partition reformatted as vfat holds the large binaries (run directly, no zram copy), and the jffs2 `/config/overlay` holds the small init scripts and config. `ENABLE_SWAP=0` prevents the swap script from destroying the vfat.
> - An ISP watchdog (`/sdcard/wyze/wd.sh`, setsid-launched from the init script) polls `/healthz` every 30 seconds and restarts `videocapture` on sustained `degraded` (>60s) or `error` (>30s) with a 3-restart backoff. `autonight` is disabled to prevent the IR-cut night/day transition that triggers the ISP firmware wedge.
> - A pion/webrtc endpoint (ICE-Lite, host candidates, HTTP SDP signaling) serves the same H.264 stream directly to browsers. A frame fan-out delivers every frame to both RTSP and WebRTC. The `profile-level-id` was fixed to `42c028` (Constrained Baseline) to match the camera's actual SPS, eliminating artifacts.

## 1. The starting point

The project began from an earlier piece of work that built `gostream`: a pure-Go streaming server cross-compiled for MIPS soft-float (`GOOS=linux GOARCH=mipsle GOMIPS=softfloat CGO_ENABLED=0`), which read encoded H.264 and JPEG from the two `v4l2loopback` devices and served RTSP, MJPEG, and an admin API. That work succeeded in producing a working stream, but its memory accounting surfaced a problem: the camera had essentially no free memory in stock mode.

The camera is a 128 MiB DDR2 system. The boot command line assigns 96 MiB to Linux, reserves 8 MiB for the image signal processor, and reserves 24 MiB for video buffers. Linux reports `MemTotal: 91844 kB`. In stock mode, `MemFree` was 1,796 kB and `VmallocUsed` was 35,532 kB. The system was constantly swapping to the SD card (mounted as a 2 GiB swap partition) and was one allocation away from an out-of-memory event.

The earlier report traced this to the loopback devices. The live `/proc/vmallocinfo` showed two allocations of exactly 16,592,896 bytes each — the size a `v4l2loopback` device reserves for a 1920×1080, four-byte-per-pixel, double-buffered backing store. Two such stores total 31.69 MiB, which is nearly all of the `VmallocUsed`. The encoded payloads being moved through the system are two orders of magnitude smaller: a 1080p H.264 frame averages roughly 50 KiB, and a JPEG snapshot reaches at most about 170 KiB. The kernel owned a 31.69 MiB reservation to carry kilobytes.

The goal became precise: recover the 31.69 MiB without changing the 1080p/25 fps H.264 quality, without rewriting the sensor or encoder, and without coupling the Go binary to the closed vendor ABI. The quality invariants were the existing encoder settings — 1920×1080, 25 fps, H.264 VBR with a 900 kbit/s ceiling, QP 15–38, GOP 10 — and the JPEG path.

## 2. The bypass point

The decisive observation was a single point in the OpenMiko `ingenic_videocap` source. Each encoder thread runs a loop that is the entire interface between the Ingenic IMP encoder and the outside world:

```c
// sources/ingenic_videocap/src/capture.c (stock output loop, simplified)
for (;;) {
    IMP_Encoder_PollingStream(chn, &streamState);   // wait for an encoded frame
    IMP_Encoder_GetStream(chn, &stream);            // get the IMPEncoderStream
    // sum pack lengths across stream.packCount
    write(v4l2_fd, stream.pack[0].virAddr, total);   // the single sink call
    IMP_Encoder_ReleaseStream(chn, &stream);        // always release
}
```

The `IMPEncoderStream` at this point is already a complete, fully-formed encoded frame in userspace. The `IMPEncoderPack` structure exposes a virtual address, a length, a microsecond timestamp, a frame-end flag, and the H.264 NAL type. The stream exposes a pack count and a frame sequence number. Every piece of metadata needed to transport the frame deterministically is present, in userspace, immediately before the single `write()` to the loopback.

This means the bypass is a sink substitution. The optimal first change is not new ISP code, not a new encoder, not a kernel module, and not a direct CGo binding of `libimp`. It is replacing that one `write()` with a call to a new sink that sends the frame elsewhere. The closed-source vendor code remains owned by the C process; the open-source consumer remains the Go process; the seam between them moves from a kernel device to a userspace socket.

The IMP get/release contract is the central safety invariant. `IMP_Encoder_GetStream` is a scoped loan: the virtual addresses are valid only until `IMP_Encoder_ReleaseStream` is called. Any transport must synchronously copy or send before release; raw pointers can never cross threads or processes. The producer's most important rule, which recurs in every phase, is exactly-one `IMP_Encoder_ReleaseStream` on every path after a successful `GetStream`.

## 3. Selecting the architecture

Six concrete designs were compared, grounded in live measurements taken from the camera. Those measurements produced the single most important constraint: a 170,822-byte JPEG exceeded the camera's 163,840-byte `wmem_max`, which forced fragmentation. H.264 frames are much smaller (averaging 2,970 bytes with a maximum of 20,031), but a protocol handling both codecs must assume the worst case.

| Option | Loopback recovery | Copies after IMP | Restart isolation | Risk | Verdict |
|--------|------------------:|------------------:|------------------:|------|---------|
| A. Fragmented `SOCK_SEQPACKET` | ~31.69 MiB | kernel + Go receive | strong | low–medium | **implement first** |
| B. Shared-memory SPSC rings | ~31.69 MiB − ring | one producer copy | strong | medium–high | profile-driven phase 2 |
| C. Direct `libimp` via CGo | ~31.69 MiB | potentially none | weak | high | defer |
| D. Replace both with C++/Live555 | ~31.69 MiB | in-process | weak | high migration | product alternative |
| E. Named FIFO / stream socket | ~31.69 MiB | kernel + receive | medium | medium | fallback only |
| F. New kernel frame-bus module | unknown − ring | at least one | medium | very high | do not build now |

Option A was selected. It removes both loopbacks and their cost, preserves process isolation and restart, preserves message boundaries, supports bidirectional control for IDR requests, uses mature Linux 3.10 APIs, requires no CGo and no kernel build, and can send directly from `IMPEncoderPack.virAddr` with no C-side concatenation buffer. The rejected options were rejected with evidence: shared memory adds cross-language atomic complexity; direct CGo changes the deployment model and couples capture to server crashes; a full C++ streamer is too large a change; FIFOs lose message boundaries; a kernel module would still copy bytes into another kernel-owned ring (reproducing the class of memory being removed) unless it integrated with proprietary IMP buffer ownership.

## 4. The wire protocol

The frame bus carries a versioned, bounded, metadata-rich message stream. Three implementations exist: a C codec (producer), a Go codec (consumer), and an independent Python generator of golden vectors. The third implementation is the guard against both codecs sharing the same bug.

Every datagram begins with a 56-byte big-endian header. The layout is fixed in `framebus/c/framebus_protocol.h` and `gostream/internal/framebus/protocol.go`: a 4-byte magic (`0x46525542`, "FRUB"), a version byte, a type byte (HELLO, FRAME_FRAGMENT, FRAME_END, CONTROL), a codec byte, flags (keyframe), stream id, frame sequence, microsecond timestamp, fragment index and count, payload length, a reserved field, a CRC32C checksum, and a final reserved field. Big-endian removes ambiguity about which side converts; the producer is MIPS32 and the host test machines are x86-64.

The 60 KiB payload cap comes directly from the `wmem_max` measurement. It keeps every datagram well under the 163,840-byte send limit, with headroom for the header and socket accounting. A frame larger than the cap is split into `FRAME_FRAGMENT` datagrams followed by one `FRAME_END`. The consumer reassembles by `frame_seq` and `fragment_idx` and emits a complete frame when it receives `FRAME_END` with all fragments present.

The backpressure policy is explicit and uniform: drop and release, then wait for or request an IDR — never block and preserve every frame. The producer sends with `MSG_DONTWAIT | MSG_NOSIGNAL`; any `EAGAIN`, `ENOBUFS`, or `EPIPE` is a transport drop. The consumer discards incomplete sequences on a gap and enters a wait-for-keyframe state, then rate-limits an `IMP_Encoder_RequestIDR` through the owning encoder thread.

## 5. The producer and consumer

The producer is a small C library, `frame_sink.c`, that takes neutral `FrameSinkPack` structs and publishes them over a `SOCK_SEQPACKET` socket. It is transport-only — no `libimp` dependency — so it is host-buildable and testable. The `videocapture` adapter converts an `IMPEncoderStream` into a `FrameSinkPack` at the integration boundary, keeping vendor-specific code in one place.

The core invariant is that the producer must never block the encoder thread. The publish loop sends with `MSG_DONTWAIT`; on `EAGAIN`/`ENOBUFS`/`EPIPE` it returns a drop without retrying. The caller wraps this in the release contract: `IMP_Encoder_GetStream` → `frame_sink_publish` → `IMP_Encoder_ReleaseStream`, where the release happens regardless of the publish result.

The consumer extended `gostream` with a frame-bus listener, a per-stream reassembler, a JPEG latest-frame hub, an RTSP source adapter, and a health endpoint. The reassembler is bounded (512 KiB H.264, 2 MiB JPEG, 64 fragments) and resets on a sequence gap — the consumer's equivalent of drop-not-block. The RTSP source adapter extracts SPS/PPS from the first keyframe, initializes the RTSP stream with `sprop-parameter-sets` in the SDP, and packetizes NAL units into RTP with the 90 kHz clock derived from the microsecond timestamp (`timestamp_us * 90 / 1000`).

A bug found during this phase: the original RTP timestamp scaling used `timestamp_us / 1000`, underestimating the 90 kHz clock by a factor of 1000. The fix is a single expression, but without it the stream would have wrong inter-frame timing — a subtle defect caught by the on-host integration test.

## 6. On-camera deployment and the IMP bind lifecycle

Building on the host proved the protocol and consumer. Deploying to the camera required building against the real MIPS toolchain and `libimp` inside the OpenMiko Docker container, and then solving a problem that only appears on hardware.

The first on-camera run failed at `IMP_System_Bind(FrameSource → Encoder)` with "Error binding frame source to encoder group". The cause is a property of the IMP kernel module not documented in the header comments: a bind entry persists in the module's bind table even after the process that created it exits, and even after `IMP_System_Exit`. The stock `videocapture` signal handler calls `IMP_System_Exit` on SIGINT but does not unbind, so the bind table retains the edge. A new instance finds it present and `IMP_System_Bind` returns an error.

The IMP SDK documentation states the constraint: after the FrameSource is enabled, Bind and UnBind cannot be called dynamically; the FrameSource must be disabled before UnBind. The sequence that clears a stale bind is `IMP_FrameSource_DisableChn` followed by `IMP_System_UnBind`, then a new `IMP_System_Bind` can succeed.

Two earlier attempts failed instructively. An UnBind retry inside `setup_binding` failed because the FrameSource was already enabled (for the OSD edge). An unconditional `IMP_System_Exit` before `IMP_System_Init` crashed the camera — calling `Exit` on a system that had only had the ISP enabled is undefined behavior, and the process died with no output, leaving the camera unresponsive for several minutes.

The working solution is a pre-pass at the start of `load_bindings` that disables each unique source FrameSource channel and unbinds every stale edge before any new bind is created. It must run once, before all binds, because disabling a channel that has just been bound breaks that bind. This pre-pass is what makes the pipeline restartable without a reboot.

A final config detail completed the deployment: the frame-bus JSON had to carry a `v4l2_device_path` field, because the patched `configparser.c` parses it unconditionally, even in direct mode. Its absence caused a parse error that masqueraded as a bind failure.

## 7. The measured result

With the pre-pass and config in place, the pipeline comes up cleanly. The memory result, measured on the same camera minutes apart:

| Metric | Stock mode | Direct mode | Delta |
|--------|-----------|-------------|-------|
| `MemFree` | 1,796 kB | 26,328 kB | +24,532 kB (+23.96 MiB) |
| `VmallocUsed` | 35,532 kB | 3,084 kB | −32,448 kB (−31.69 MiB) |
| `v4l2loopback` refs | 2 | 0 | −31.69 MiB backing |
| `gostream` RSS | (stock daemons) | 9,148 kB | — |
| `videocapture` RSS | (stock) | 3,260 kB | — |

`ffprobe` over TCP confirmed H.264 Constrained Baseline, 1920×1080, 25 fps. A 10-second capture contained 247 frames (24.7 fps) at ~650 kbits/s. The `/healthz` endpoint reported 12,838 H.264 frames with zero malformed, zero oversize, zero incomplete over roughly ten minutes.

## 8. SD-card persistence

The direct pipeline was not yet persistent: the rootfs is a writable zram overlay lost on every reboot, and the SD card had been repurposed as swap by the `S31swap` script (which ran `mkswap /dev/mmcblk0p1; swapon`, destroying the vfat signature). The jffs2 `/config` partition persists but is only 256 KiB — too small for the 8.6 MiB gostream binary.

The solution is a run-from-sdcard hybrid. The SD partition was reformatted as vfat (by building an empty 256 MiB vfat image on the host and `dd`-ing it to the partition, since the camera has no `mkfs.vfat`). The large binaries (gostream, videocapture, settings) live at `/sdcard/wyze/` and are exec'd directly — no copy to zram, preserving memory (file-backed pages can be evicted under pressure). The small init scripts and config live in the jffs2 `/config/overlay` (persists across reboot): the direct `S60camera`, no-op `S67gostream`/`S70mjpg_streamer`, the framebus `gostream.conf`, and `ENABLE_SWAP=0` in `openmiko.conf` (the critical guard that prevents `S31swap` from `mkswap`-ing the vfat again). The old 248 KiB gostream was removed from jffs2 to free space (98% → 42%).

After a reboot, `general_init.sh` mounts `/sdcard` (vfat succeeds), copies `/config/overlay → rootfs`, and the init scripts run: `S31swap` skips (ENABLE_SWAP=0), `S60camera` starts gostream + videocapture from `/sdcard/wyze/`, and v4l2loopback never loads. The stream comes up in ~30 seconds with ~11 MB free (lower than the manual-start 26 MB because a fresh boot runs all the wifi/network daemons; the 38 MB page cache is reclaimable).

## 9. The ISP watchdog and autonight

After approximately one hour of uptime — and specifically after an `autonight` night/day IR-cut-filter transition — the stream degraded. The ISP firmware thread `apical_isp_fw_p` entered state `D` (uninterruptible disk sleep) on `down_timeout`. The FrameSource tick thread cascaded into `release_tx_isp_video_in_device`. The H.264 encoder thread survived (it had queued frames), but the JPEG encoder thread wedged in `vpu_wait_complete` — it issued a VPU encode that never completed. The healthz status went `degraded`.

Two independent mitigations were implemented. First, `autonight` was disabled by setting `ENABLE_AUTONIGHT=0` in the jffs2 `openmiko.conf`, so the IR-cut night/day transition that triggers the ISP wedge never fires. The camera runs in color mode permanently.

Second, a healthz-based watchdog (`/sdcard/wyze/wd.sh`, setsid-launched from `S60camera-direct` at boot) polls `http://127.0.0.1:18081/healthz` every 30 seconds. It parses the `"status"` field (`ok`/`degraded`/`error`) and restarts `videocapture` on sustained `degraded` (>60s) or `error` (>30s) with a 3-restart backoff. The restart uses SIGINT (the clean `sensor_cleanup` path, not SIGKILL), which relies on the pre-pass stale-bind recovery to allow the new instance to bind. The watchdog is a child of the init process, not of `videocapture`, so a `videocapture` restart does not kill it.

During this work, a deeper finding emerged: the T20 VPU JPEG encode channel has an independent, recurring firmware-level instability (`vpu_wait_complete`) that wedges within seconds regardless of the IR-cut state or load. Adding a per-frame `usleep` throttle to the frame-bus output path (it was missing, unlike the v4l2 path) was correct but did not fix the wedge. Lowering the JPEG encoder to 2 fps reduced VPU pressure but the wedge still recurs. The watchdog recovers it; the H.264 RTSP stream is unaffected (24.9 fps verified). The MJPEG/snapshot path is treated as a secondary, watchdog-recovered stream.

## 10. WebRTC browser-direct streaming

Browsers cannot play RTSP natively (they speak WebRTC, HLS, and MSE). The first browser path was a host-based `go2rtc` bridge — a separate process on a laptop that pulls RTSP and re-serves WebRTC. That works but depends on the host being on and adds an extra hop. The goal was to serve browsers directly from the camera over the LAN with no host bridge, while keeping RTSP for VLC/NVR.

`pion/webrtc` v4 compiles cleanly for mipsle soft-float (verified: an 11 MB static binary). `gostream` already pulled in `pion/rtp`, `pion/srtp`, `pion/sdp`, and `pion/transport` via gortsplib; adding `pion/webrtc` adds the DTLS and ICE layers. The CPU cost is negligible (SRTP AES-CTR at ~80 KiB/s is trivial on a 580 MHz MIPS). Memory is ~13 MB free with the WebRTC-enabled gostream (the 17.3 MB binary is +8.7 MB for pion/webrtc).

A new `internal/webrtc` package wraps pion. The server creates an ICE-Lite `PeerConnection` (host candidates only, no STUN/TURN), adds an H.264 `TrackLocalStaticSample`, and exchanges SDP over a single HTTP POST (`/webrtc/offer`) — non-trickle, with all host candidates gathered synchronously and included in the answer. A frame pump reads from a derived H.264 channel, builds Annex-B samples (start-code-prefixed NAL units), and writes them to all active peer tracks via pion's `H264Payloader` (which packetizes to single-NAL, STAP-A, or FU-A). An embedded `player.html` page does the browser-side offer/answer and renders the video.

A frame fan-out in `startFrameBus` delivers each `EncodedFrame` to both RTSP and WebRTC: RTSP gets a buffered channel (blocking, never drops), WebRTC gets a capacity-1 channel (nonblocking drop-on-full, so a slow peer never blocks RTSP). The `RequestKeyFrame` hook on the WebRTC server calls `h264Stream.RequestIDR` (the frame-bus control path to the C encoder).

Two bugs were found and fixed during WebRTC implementation. First, the stream froze after the first frame: `Sample.Duration` was set to 0, so pion never advanced the 90 kHz RTP clock and the browser could not distinguish frames. The fix computes Duration from the previous frame's PTS (inter-frame delta), with a 40 ms (25 fps) fallback. Second, the WebRTC stream had artifacts and lower quality: the hardcoded `profile-level-id` was `42e0` (missing the level byte, wrong constraint flags). Extracting the camera's real SPS from the RTSP stream and decoding it gave `42c028` (Constrained Baseline, profile 66, constraint 0xc0, level 40). Fixing the SDP to match eliminated the artifacts.

A follow-up remains: PLI/FIR keyframe recovery. When the browser loses packets over UDP, it sends a PLI (Picture Loss Indication) requesting an immediate IDR. pion v4 does not expose `pc.OnPLI` (it uses an interceptor pattern); the C side now forwards `FB_CMD_REQUEST_IDR` to `IMP_Encoder_RequestIDR`, and the Go `RequestKeyFrame` hook is in place, but a pion RTCP interceptor is needed to receive the browser's PLI and trigger it. Without it, the browser shows artifacts until the next natural keyframe (every 2.5s at GOP 10) after packet loss.

## 11. The end-state architecture

```mermaid
flowchart TD
    VC[videocapture C<br/>libimp owner] -->|frame bus<br/>SOCK_SEQPACKET| FB[framebus listener]
    FB -->|fanout H.264| RTSP[RTSP :8554<br/>VLC/NVR]
    FB -->|fanout H.264| W[WebRTC :8555<br/>browser direct]
    FB -->|JPEG| MJPEG[MJPEG/snapshot :8080]
    FB -->|healthz| ADM[admin :18081]
    WD[ISP watchdog] -->|poll healthz 30s| ADM
    WD -->|SIGINT + pre-pass rebind| VC
    AUTONIGHT[autonight DISABLED<br/>ENABLE_AUTONIGHT=0] -.prevents IR-cut transition.-> VC
    SDCARD[/sdcard/wyze vfat<br/>gostream + videocapture] --> VC
    SDCARD --> W
    JFFS2[/config/overlay jffs2<br/>S60camera-direct + config] -.persists.-> VC
```

The camera runs four network endpoints: RTSP `:8554` (VLC/NVR), WebRTC `:8555` (browser), MJPEG `:8080` (snapshot, secondary), and admin `:18081` (healthz). The binaries run from vfat on the SD card. The init scripts and config persist in jffs2. The watchdog keeps the stream alive. Autonight is disabled. RTSP and WebRTC share the frame-bus H.264 source via the fan-out.

## 12. The kernel-side question

The natural follow-up to recovering the memory is whether moving the entire server into the Linux kernel would recover more or run faster. The answer is that it is blocked by the hardware on this SoC, and even if it were not, the gain would be marginal relative to the risk.

The T20's H.264/JPEG encoder is the VPU (a monolithic block Ingenic calls NVPU), driven by `soc_vpu` + `jz_nvpu`, which is built into the kernel image (`CONFIG_SOC_VPU=y`, not `=m`), and whose source is not in the OpenMiko patches. The open `tx-isp` patch contains 68 ISP source files and zero encoder files. The encoder is reached only through the closed `libimp.so`, which opens `/dev/soc_vpu` and programs the VPU through a proprietary register interface using a proprietary firmware blob (`libt20-firmware.a`). There is an open VPU driver in the Ingenic ecosystem (`thingino/ingenic-sdk`), but its build system restricts it to the newer T31/T40/T41 SoCs — the T20 is excluded. No production in-kernel RTSP/RTP server has ever been built; the precedent (TUX in-kernel HTTP) was removed from mainline Linux. The recommendation is to not pursue a full kernel-side server on this hardware; the userspace frame bus is the end state.

## 13. Open questions and next steps

The WebRTC PLI/FIR keyframe-recovery interceptor is the most immediate follow-up. A 24-hour soak under sustained load would confirm both H.264 RTSP and WebRTC stability and measure the watchdog restart frequency. The `profile-level-id` is hardcoded to `42c028`; a more robust approach would parse the SPS dynamically. STUN/TURN support would enable remote (non-LAN) browser access. Authentication on the WebRTC signaling endpoint would be needed if the camera is exposed beyond a fully-trusted LAN. The hardware watchdog (`/dev/watchdog`) could be armed so a persistent ISP wedge triggers an automatic full reboot rather than a log message.

The JPEG VPU wedge is a known limitation of the T20 firmware. The watchdog recovers it, but the MJPEG path is necessarily secondary (low fps, intermittent stalls). If the MJPEG/snapshot path is not needed, disabling the JPEG encoder entirely (H.264-only config) would eliminate the VPU JPEG wedge and its watchdog restarts, yielding the most stable configuration.

## 14. References

- Repo: `/home/manuel/code/wesen/2026-08-23--wyze-cam`
- Ticket: `ttmp/2026/08/23/WYZECAM-DIRECT-STREAM--direct-encoded-frame-streaming-on-wyze-cam-v2-without-v4l2loopback/`
- Design docs: `01-optimal-direct-frame-streaming-architecture-for-wyze-cam-v2.md`, `02-isp-watchdog-and-autonight-disable.md`, `03-webrtc-endpoint-for-browser-direct-streaming.md`
- Diary: `reference/01-investigation-diary.md` (14 steps)
- Wire protocol: `framebus/c/framebus_protocol.h`, `gostream/internal/framebus/protocol.go`, `framebus/golden/gen_vectors.py`
- Producer: `framebus/c/frame_sink.c`, `openmiko/submodules/ingenic_videocap/src/capture.c`
- Consumer: `gostream/internal/framebus/listener.go`, `gostream/internal/framebus/reassembler.go`, `gostream/internal/rtsp/rtsp.go`, `gostream/internal/jpeghub/hub.go`
- WebRTC: `gostream/internal/webrtc/server.go`, `gostream/cmd/gostream/main.go` (`startFrameBus`, `fanoutH264`)
- Watchdog: `framebus/deploy/overlay/sdcard/wyze/wd.sh`, `framebus/deploy/overlay/etc/init.d/S60camera-direct`
- Persistence: `ttmp/.../scripts/04-sdcard-persistence.sh`
- Open VPU driver (T31 only): `thingino/ingenic-sdk` at `https://github.com/thingino/ingenic-sdk`
- Prior reports: `PROJECT REPORT - Wyze Cam v2 - Custom Streaming Server on OpenMiko.md` (2026-08-23), `PROJECT REPORT - Wyze Cam v2 - Direct Frame-Bus Streaming Without v4l2loopback.md` (2026-08-23), `PROJECT REPORT - Wyze Cam v2 - Direct Frame-Bus Streaming Verified on Hardware.md` (2026-08-25), `PROJECT REPORT - Wyze Cam v2 - The Complete Direct Frame-Bus Streaming Implementation.md` (2026-08-25)
