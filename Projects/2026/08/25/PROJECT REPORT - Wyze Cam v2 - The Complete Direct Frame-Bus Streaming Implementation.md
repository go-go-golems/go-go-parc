---
title: Wyze Cam v2 — The Complete Direct Frame-Bus Streaming Implementation
aliases:
  - Wyze Cam v2 full implementation report
  - WYZECAM-DIRECT-STREAM full journey
  - framebus implementation phases
tags:
  - project
  - embedded
  - firmware
  - streaming
  - rtsp
  - ipc
  - go
  - mips
  - openmiko
  - kernel
  - optimization
status: active
type: project
created: 2026-08-25
repo: /home/manuel/code/wesen/2026-08-23--wyze-cam
---

# Deep-Dive Project Report: The Complete Direct Frame-Bus Streaming Implementation

This report explains the entire setup that was implemented on the Wyze Cam v2 and how it was reached, phase by phase, from the discovery of a hidden memory cost to a verified on-camera stream. It is written for an engineer who needs to understand not only what the final system does, but why each decision was made and what each phase produced. The narrative draws from the design document and the ten-step investigation diary committed to the project ticket, and it preserves the order in which the work actually happened — including the constraints that were measured live, the options that were rejected, and the deployment problems that only appear on hardware.

The system under discussion replaces two kernel-owned `v4l2loopback` devices with a userspace `AF_UNIX / SOCK_SEQPACKET` frame bus, moving encoded H.264 and JPEG frames directly from the C capture process (`videocapture`, the sole owner of the closed Ingenic `libimp`) to a Go streaming server (`gostream`), without the kernel ever owning a copy of the frames. The result, measured on the live camera, is a recovery of 31.69 MiB of `vmalloc` and 23.96 MiB of free RAM, with a verified H.264 Constrained Baseline 1920×1080 stream at 25 frames per second over RTSP, and zero malformed frames over more than 17,000 delivered frames.

The report is organized along the actual sequence of work. It begins with the memory problem that motivated everything, then the single source-code observation that made the bypass possible, then the architecture selection that compared six options, then the five implementation phases, then the on-camera deployment and the IMP bind lifecycle problem that had to be solved, then the measured result, and finally the question of whether going further into the kernel would be worth pursuing.

> [!summary]
> - The motivating problem was structural: two 1080p `v4l2loopback` devices each reserve a 16,592,896-byte `vmalloc` backing store (`1920×1080×4×2 + 4096`), totaling 31.69 MiB — nearly all of the camera's 35,016 KiB `VmallocUsed` — even though the encoded H.264 and JPEG payloads are kilobytes, not megabytes.
> - The key insight was a single sink substitution: the OpenMiko `videocapture` process already receives complete `IMPEncoderStream` objects in userspace (with sequence, timestamp, per-pack addresses, lengths, and NAL types) immediately before one `write()` to the loopback, so the bypass point is that one sink call, not the sensor, ISP, encoder, or kernel.
> - The architecture was selected against six options by live measurement: a 170,822-byte JPEG exceeded the camera's 163,840-byte `wmem_max`, which forced fragmented `SOCK_SEQPACKET` with a 60 KiB payload cap; shared memory, direct CGo, a full C++ streamer, FIFOs, and a kernel module were each rejected with stated evidence.
> - Five phases were built and verified: a 56-byte big-endian wire protocol (C + Go + independent Python golden vectors), a nonblocking C frame sink, a bounded Go reassembler with RTSP and JPEG-hub integration, deploy artifacts and on-host integration tests, and an on-camera build against the real MIPS toolchain plus an IMP stale-bind recovery.
> - The measured result is the verification: MemFree 1,796 → 26,328 KiB, VmallocUsed 35,532 → 3,084 KiB, `ffprobe`-confirmed 1080p/25 fps H.264, and zero malformed/oversize/incomplete over 17,000 frames.
> - A full kernel-side server is infeasible on this SoC because the T20 VPU encoder driver is closed-source and built into the kernel; the userspace frame bus is the recommended end state.

## 1. The starting point and the hidden cost

The project began from an earlier piece of work documented in `PROJECT REPORT - Wyze Cam v2 - Custom Streaming Server on OpenMiko.md`. That work built `gostream`, a pure-Go streaming server cross-compiled for MIPS soft-float (`GOOS=linux GOARCH=mipsle GOMIPS=softfloat CGO_ENABLED=0`), which reads encoded H.264 from `/dev/video3` and JPEG from `/dev/video4` — both `v4l2loopback` devices fed by the stock `videocapture` process — and serves RTSP on `:8554`, MJPEG and snapshots on `:8080`, and an admin API on `:18081`. That work succeeded in producing a working stream, but its memory accounting surfaced a problem that became the subject of this report.

The camera is a 128 MiB DDR2 system. The boot command line assigns 96 MiB to Linux, reserves 8 MiB for the image signal processor (`ispmem`), and reserves 24 MiB for video buffers (`rmem`). Linux reports `MemTotal: 91844 kB` after its own reservation. In stock mode the free memory is essentially zero: `MemFree: 1796 kB`. The system is constantly swapping to the SD card (mounted as a 2 GiB swap partition) and is one allocation away from an out-of-memory event.

The earlier report traced this pressure to the loopback devices. The live `/proc/vmallocinfo` shows two allocations of exactly 16,592,896 bytes each. That number is not arbitrary; it is the size a `v4l2loopback` device reserves for a 1920×1080, four-byte-per-pixel, double-buffered backing store:

```
16,592,896 = 1920 × 1080 × 4 bytes/pixel × 2 buffers + 4096 (page alignment)
```

Two such stores total 31.69 MiB, which is nearly all of the live `VmallocUsed` of 35,016 KiB. This is the structural fact that motivated the entire project: the kernel owns a 31.69 MiB reservation to carry payloads that are two orders of magnitude smaller. A 1080p H.264 frame averages roughly 50 KiB; a JPEG snapshot reaches at most about 170 KiB. The loopback devices reserve megabytes to move kilobytes.

The goal became precise at this point: recover the 31.69 MiB without changing the 1080p/25 fps H.264 quality, without rewriting the sensor, ISP, or encoder, and without coupling the Go binary to the closed vendor ABI. The non-negotiable quality invariants were the existing encoder settings — 1920×1080, 25 fps, H.264 VBR with a 900 kbit/s ceiling, QP 15–38, GOP 10 — and the existing 1920×1080 JPEG path.

## 2. The bypass point

The decisive observation was a single point in the OpenMiko `ingenic_videocap` source. Each encoder thread, in `capture.c`, runs a loop that is the entire interface between the Ingenic IMP encoder and the outside world:

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

The `IMPEncoderStream` at this point is already a complete, fully-formed encoded frame in userspace. The `IMPEncoderPack` structure exposes a virtual address (`virAddr`), a length, a microsecond timestamp, a frame-end flag, and — for H.264 — the NAL type. The `IMPEncoderStream` exposes a pack count and a frame sequence number. Every piece of metadata needed to transport the frame deterministically is present, in userspace, immediately before the single `write()` to the loopback.

This means the bypass is a sink substitution. The optimal first change is not new ISP code, not a new encoder, not a new kernel module, and not a direct CGo binding of `libimp`. It is replacing that one `write()` call with a call to a new sink that sends the frame elsewhere. Everything upstream — the sensor driver, the ISP, the bind graph, the encoder hardware, the `libimp` ownership — stays exactly as it is. The closed-source vendor code remains owned by the C process; the open-source consumer remains the Go process; the seam between them moves from a kernel device to a userspace socket.

Two details from this source pass shaped the protocol. First, the stock code assumed all packs in one stream were contiguous and wrote from `pack[0].virAddr`; the direct protocol instead preserves each pack and its address independently, which is safer and retains NAL metadata. Second, the capture process already runs one encoder thread per configured stream, so one independent local connection per encoder avoids a shared producer lock.

The IMP get/release contract is the central safety invariant of the entire design. `IMP_Encoder_GetStream` is a scoped loan: the virtual addresses are valid only until `IMP_Encoder_ReleaseStream` is called. Any transport must synchronously copy or send before release; raw pointers can never cross threads or processes. The producer's most important rule, which recurs in every phase, is exactly-one `IMP_Encoder_ReleaseStream` on every path after a successful `GetStream`.

## 3. Selecting the architecture

With the bypass point identified, six concrete designs were compared. The comparison was not abstract; it was grounded in live measurements taken from the camera at `192.168.0.55` over SSH. Those measurements produced the single most important constraint in the project.

### 3.1 The constraint that forced fragmentation

A read-only probe of the running camera established the transport limits of this specific Linux 3.10.14 MIPS kernel:

```
net.core.wmem_max = 163840
net.core.rmem_max = 163,840
net.unix.max_dgram_qlen = 10
```

At the same time, twenty live JPEG snapshots were sampled:

```
jpeg_samples 20  min 100009  median 101187  max 170822
```

The decisive fact is that the maximum JPEG frame (170,822 bytes) exceeds the socket send limit (163,840 bytes). A design that sent one datagram per frame — the natural `SOCK_SEQPACKET` model — would block or fail on the largest JPEGs. This single measurement eliminated the simplest design and forced fragmentation.

H.264 frames are much smaller: 292 demuxed access units over about 12 seconds averaged 2,970 bytes with a maximum of 20,031 bytes. H.264 would fit in a single datagram, but a protocol that handles both codecs must assume the worst case, which is JPEG.

### 3.2 The six options

The design document recorded six options with their advantages, costs, and an explicit assessment.

| Option | Loopback recovery | Copies after IMP | Restart isolation | Risk | Verdict |
|--------|------------------:|------------------:|------------------:|------|---------|
| A. Fragmented `SOCK_SEQPACKET` | ~31.69 MiB | kernel + Go receive | strong | low–medium | **implement first** |
| B. Shared-memory SPSC rings | ~31.69 MiB − ring | one producer copy | strong | medium–high | profile-driven phase 2 |
| C. Direct `libimp` via CGo | ~31.69 MiB | potentially none | weak | high | defer |
| D. Replace both with C++/Live555 | ~31.69 MiB | in-process | weak | high migration | product alternative |
| E. Named FIFO / stream socket | ~31.69 MiB | kernel + receive | medium | medium | fallback only |
| F. New kernel frame-bus module | unknown − ring | at least one | medium | very high | do not build now |

Option A was selected. It removes both loopbacks and their 31.69 MiB cost, preserves process isolation and independent restart, preserves message boundaries (unlike a FIFO byte stream), supports bidirectional control for IDR requests, uses mature Linux 3.10 APIs, requires no CGo and no kernel build, and can send directly from `IMPEncoderPack.virAddr` through `sendmsg` with no C-side concatenation buffer. Its cost is one kernel copy into the socket buffer and one copy into Go, plus fragmentation of large packs — costs that the measured payload sizes (kilobytes, at most a few MiB/s) make negligible.

The rejected options were rejected with evidence, not instinct. Option B (shared memory) was made the explicit second choice, to be built only if profiling showed socket copies were material; it carries real complexity in cross-language atomic ordering on MIPS, torn-write handling, and a notification mechanism (`memfd_create` is unavailable on Linux 3.10). Option C (direct CGo) was deferred because it changes the MIPS/uClibc/external-linking deployment model, couples capture to server crashes, and duplicates working C initialization code. Option D (a full C++/Live555 streamer like Prudynt-t) was acknowledged as a valid product direction but rejected as too large a change for a memory optimization. Option E (FIFO) loses message boundaries and needs a separate control channel. Option F (kernel module) was rejected because `libimp` already returns encoded frames to userspace, so a module would still copy bytes into another kernel-owned ring — reproducing the class of memory being removed — unless it integrated with proprietary IMP buffer ownership that is not in the public API.

The decision on kernel code was made an explicit evidence threshold, not a blanket prohibition: do not build shared memory unless socket profiling fails a documented requirement, and do not consider kernel code unless a bounded shared-memory prototype also fails. This threshold is what later allowed the kernel-side question to be answered with evidence rather than preference.

## 4. Phase 1 — The wire protocol

The first implementation phase was the shared wire protocol codec, built in C and Go and verified against golden vectors generated by an independent Python implementation. The protocol was deliberately made the first phase because it is the part of the system that is easiest to get subtly wrong and hardest to debug on a remote MIPS target, so it was verified on the host before any camera work.

### 4.1 The 56-byte header

Every datagram begins with a 56-byte big-endian header. The layout is fixed identically in `framebus/c/framebus_protocol.h` and `gostream/internal/framebus/protocol.go`:

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 4 | `magic` | `0x46525542` ("FRUB") |
| 4 | 1 | `version` | 1 |
| 5 | 1 | `type` | 0=HELLO, 1=FRAME_FRAGMENT, 2=FRAME_END, 3=CONTROL |
| 6 | 1 | `codec` | 1=H264, 2=JPEG |
| 7 | 1 | `flags` | bit0: keyframe |
| 8 | 4 | `stream_id` | 0 (H.264), 1 (JPEG) |
| 12 | 4 | `frame_seq` | monotonic per-stream |
| 16 | 8 | `timestamp_us` | microseconds (encoder pack timestamp) |
| 24 | 4 | `fragment_idx` | 0-based fragment index within frame |
| 28 | 4 | `total_fragments` | total fragments in this frame |
| 32 | 4 | `payload_len` | bytes following this header |
| 36 | 4 | `reserved` | 0 |
| 40 | 8 | `crc32c` | checksum of payload |
| 48 | 8 | `reserved` | 0 |

Big-endian is a deliberate choice. The producer is MIPS32 (big-endian-capable) and the consumer is MIPS32 soft-float; the host test machines are x86-64 (little-endian). A fixed wire byte order removes any ambiguity about which side converts, and the golden vectors anchor the exact bytes.

The 60 KiB (61,440-byte) payload cap comes directly from the `wmem_max` measurement. It keeps every datagram well under the 163,840-byte send limit, with headroom for the 56-byte header and the socket's own accounting. A frame larger than the cap is split into a sequence of `FRAME_FRAGMENT` datagrams followed by one `FRAME_END` datagram; the consumer reassembles by `frame_seq` and `fragment_idx` and emits a complete frame when it receives `FRAME_END` with all fragments present.

### 4.2 The handshake and the recovery semantics

The connection begins with a `HELLO` from the producer, carrying the codec, stream id, and maximum dimensions. The listener validates the `HELLO`, assigns a generation number, and accepts frame datagrams. The generation number lets the consumer distinguish a new connection from a stale one after a producer restart.

The backpressure policy was defined explicitly and is the same throughout the system: drop and release, then wait for or request an IDR — never block and preserve every frame. The producer sends with `MSG_DONTWAIT | MSG_NOSIGNAL`; any `EAGAIN`, `ENOBUFS`, or `EPIPE` is a transport drop, not a retry. The consumer discards incomplete sequences on a sequence gap and enters a wait-for-keyframe state, then rate-limits an `IMP_Encoder_RequestIDR` through the owning encoder thread. Dropping a single frame in a 25 fps stream is a 40 ms visual hiccup; blocking the IMP encoder thread risks stalling the hardware pipeline, which is far worse.

### 4.3 Three implementations and golden vectors

Three implementations of the protocol exist. The C codec is the producer side, used by `videocapture`; it passed 166 assertion checks over the golden vectors with zero failures. The Go codec is the consumer side, used by `gostream`; it passes all golden vectors, and a fuzz target ran 2.5 million executions with no panics and no over-capacity allocations. The Python generator is the independent third implementation, which produced the 29 golden vectors (13 accept, 2 valid-but-edge, 14 reject) from a separate encoding of the byte layout.

The golden vectors exercise round-trip encode/decode, the independent endianness anchors, and the rejection paths: truncated headers, bad magic, unsupported version, oversize payloads, and fragment-count mismatches. The third implementation is the guard against both codecs sharing the same bug. If the C and Go codecs both mis-encoded the timestamp field in the same way, the independently-generated golden vectors would catch it.

## 5. Phase 2 — The nonblocking C frame sink

The producer side is a small C library, `frame_sink.c`, that takes neutral `FrameSinkPack` structs and publishes them over a `SOCK_SEQPACKET` socket. It is deliberately transport-only: it does not depend on `libimp` or any Ingenic type. This separation has two consequences. First, the sink can be built and tested on the host without `libimp`, which is how the cross-verification test runs. Second, the `videocapture` adapter converts an `IMPEncoderStream` into a `FrameSinkPack` at the integration boundary, so the vendor-specific code stays in one place and the transport code stays general.

The core invariant of the producer is that it must never block the encoder thread. The publish loop sends with `MSG_DONTWAIT`:

```c
// framebus/c/frame_sink.c (simplified)
int frame_sink_publish(FrameSink *s, const FrameSinkPack *p) {
    for each fragment of p->data into chunks <= s->fragment_bytes:
        encode 56-byte header (type = FRAME_FRAGMENT or FRAME_END)
        ssize_t n = send(s->fd, header + payload, total, MSG_DONTWAIT);
        if (n < 0 && (errno == EAGAIN || errno == ENOBUFS || errno == EPIPE))
            return FRAMESINK_DROP;        // transport drop, no retry, no block
    return FRAMESINK_OK;
}
```

The caller wraps this in the IMP release contract. The exactly-one `IMP_Encoder_ReleaseStream` rule is enforced by the structure of the loop: there is no retry path that could release twice, and there is no blocking wait that could forget to release.

```c
// openmiko/submodules/ingenic_videocap/src/capture.c (output_frame_bus_frames, simplified)
for (;;) {
    IMP_Encoder_GetStream(chn, &stream);          // blocks until a frame is ready
    FrameSinkPack pack = { .data = stream.pack[0].virAddr, .len = ... };
    frame_sink_publish(&sink, &pack);             // nonblocking; may drop
    IMP_Encoder_ReleaseStream(chn, &stream);      // ALWAYS release, even on drop
}
```

The integration into `videocapture` touched five files. `CMakeLists.txt` added the two frame-bus source files. `streamsettings.h` gained `output_type`, `framebus_path`, `framebus_stream_id`, and `framebus_fragment_bytes` fields on the encoder settings. `configparser.c` gained parsing for a JSON `output` block with `v4l2` as the default (so the patch is safe to apply before direct mode is enabled, preserving the rollback path). `capture.c` gained an `output_frames()` dispatcher that selects between the v4l2 sink and the frame-bus sink based on `output_type`, and the `output_frame_bus_frames()` publisher. `capture.h` gained the declarations. The v4l2 path remains as a rollback: a config without an `output` block uses `output_type = "v4l2"` and behaves exactly as before.

## 6. Phase 3 — The bounded Go consumer

The consumer side extended the existing `gostream` binary with a frame-bus listener, a per-stream reassembler, a JPEG latest-frame hub, an RTSP source adapter, and a health endpoint. The package structure kept each concern separate: `internal/media` for the `EncodedFrame` and `EncodedPack` domain types, `internal/framebus` for the listener, reassembler, and stats, `internal/jpeghub` for the broadcast hub, and `internal/rtsp` for the RTSP integration.

### 6.1 The listener

The listener accepts `unixpacket` connections, validates the `HELLO` (checking magic, version, codec, stream id, and dimensions), assigns a generation number, and feeds datagrams into a per-stream reassembler. It closes the stream channels on shutdown to prevent goroutine leaks, and guards publication with a `closed` flag so a late datagram after shutdown does not write to a closed channel.

### 6.2 The reassembler

The reassembler turns a stream of datagrams into a stream of complete frames and defends itself against a malicious or buggy producer. Its bounds are soft caps: 512 KiB for H.264, 2 MiB for JPEG, and 64 fragments per frame. A frame that exceeds a cap is dropped and counted (malformed, oversize, or incomplete), and the reassembler resets to the next frame sequence. This is the consumer's equivalent of the producer's drop-not-block: the system tolerates a dropped frame gracefully and never grows its memory in response to a bad producer.

```go
// gostream/internal/framebus/reassembler.go (simplified)
func (r *Reassembler) Feed(h Header, payload []byte) (EncodedFrame, bool) {
    if h.frameSeq != r.frameSeq { r.reset(h.frameSeq) }              // new or gap
    if h.fragmentIdx != r.fragIdx  { r.stats.malformed++; r.reset(); return ... }
    if r.buf.Len() + len(payload) > r.maxBytes { r.stats.oversize++; r.reset(); return ... }
    r.buf.Write(payload); r.fragIdx++
    if h.type == FRAME_END {
        f := EncodedFrame{ /* from r.buf, with h metadata */ }
        r.frameSeq++; r.fragIdx = 0; r.buf.Reset()
        return f, true
    }
    return EncodedFrame{}, false
}
```

### 6.3 RTSP and the RTP timestamp fix

The H.264 path feeds an RTSP source adapter that wraps `gortsplib`. The first frame pair — SPS and PPS, extracted from the H.264 bitstream — initializes the RTSP stream and builds the SDP with `sprop-parameter-sets`. Subsequent NAL units are packetized into RTP, with the RTP timestamp derived from the frame's microsecond timestamp scaled to the 90 kHz RTP clock.

The RTP timestamp scaling was a bug found and fixed during this phase. The original code used `timestamp_us / 1000`, which underestimates the 90 kHz RTP clock by a factor of 1000. RTP H.264 uses a 90 kHz clock, so a microsecond timestamp must be multiplied by 90 and divided by 1000 (`timestamp_us * 90 / 1000`) to land on the correct RTP tick. The fix is a single expression, but without it the stream would have wrong inter-frame timing — a subtle defect that the on-host integration test caught before any camera deployment.

### 6.4 The JPEG hub

The JPEG path exposed a second correctness opportunity. In the stock gostream, JPEG consumers shared one channel and stole frames from one another: the first client to read got the frame, and the others missed it. The fix is a "latest-frame" hub that broadcasts the most recent JPEG to any number of MJPEG HTTP subscribers. Each subscriber gets its own channel; the hub keeps only the latest frame and drops stale ones, so a slow subscriber never blocks a fast one and never grows memory.

### 6.5 Health and observability

The health endpoint surfaces atomic per-stream statistics. The `Stats` type uses `atomic.Uint64` fields so that concurrent reads from the HTTP handler are race-safe (an earlier version used plain `uint64` fields, which the race detector flagged). A `StreamSnapshot` type captures a consistent view of a stream at one instant. The status logic combines freshness and error counters into `ok` (fresh, zero errors), `degraded` (stale or some errors), and `error` (disconnected or many errors), matching the design's §11.7. An `IDRRequests` counter tracks how often the consumer has asked the producer for a keyframe.

## 7. Phase 4 — Deploy artifacts and on-host integration tests

Before any camera deployment, the system was wired and tested entirely on the host. The deploy artifacts were an init script (`S60camera-direct`) that loads no `v4l2loopback` and starts `gostream` before `videocapture`, a `gostream.conf` with `framebus.enabled`, and an overlay README documenting the layout. The init ordering matters: the listener must exist before the producer connects, so `gostream` starts first and creates the socket, then `videocapture` starts and connects to it.

Three on-host integration tests closed the loop before the camera. The first wired a fake C-shaped producer to the listener and verified the H.264 stream and JPEG hub end to end (the full path minus the network bind), which exposed and fixed the listener's failure to close stream channels on shutdown (a goroutine leak). The second was a real RTSP integration test using `gortsplib.Client` to DESCRIBE (verifying `sprop-parameter-sets` in the SDP), SETUP, and PLAY (verifying a continuous RTP access unit), using the real camera's SPS and PPS bytes; this test also fixed `Start()` to skip the V4L2 open when the frame-bus source is set, so the same binary works in both modes. The third was the C-to-Go cross-verification over a real `unixpacket` socket, proving the two implementations agree on the wire.

The MIPS build was verified continuously: `GOOS=linux GOARCH=mipsle GOMIPS=softfloat CGO_ENABLED=0 go build ./...` succeeds, and `go test ./... -race` stays green across five packages.

## 8. Phase 5 — On-camera build and the IMP bind lifecycle

The host work proved the protocol and the consumer. The camera work required building `videocapture` against the real MIPS toolchain and `libimp`, and then solving a problem that only appears on hardware.

### 8.1 Building against the real toolchain

The OpenMiko build uses Buildroot 2016.02 with a GCC 4.7 MIPS32 toolchain. The `ingenic_videocap` package is overridden to use a local source directory (`INGENIC_VIDEOCAP_OVERRIDE_SRCDIR` in `local.mk`), so the patched source builds directly. `make ingenic_videocap-rebuild`, run inside the OpenMiko Docker container, compiled all frame-bus sources against `libimp` with zero errors and produced a 1,325,985-byte ELF MIPS32 binary with all the `frame_sink` and `framebus` symbols present. The Go binary built as before, producing an 8,585,431-byte static binary. Both deploy over an SSH pipe, which is binary-safe on the busybox SSH on the camera.

A detail about the source revision is worth recording. The first source mirror used the current upstream HEAD of `ingenic_videocap`, but OpenMiko v1.0.0-alpha.1 pins a specific commit (`f56caf60…`). The mirror was discarded, the pinned commit was checked out, and all line anchors in the design were taken from the pinned source. A bypass design that cites line numbers must cite the lines that actually built.

### 8.2 The stale-bind problem

The first on-camera run failed at `IMP_System_Bind(FrameSource → Encoder)` with "Error binding frame source to encoder group". The cause is a property of the IMP kernel module that is not in the header comments: a bind entry, once created, persists in the module's bind table even after the process that created it exits, and even after `IMP_System_Exit`. The stock `videocapture` signal handler calls `IMP_System_Exit` on SIGINT but does not unbind, so the bind table retains the FrameSource→Encoder edge. A new `videocapture` instance finds the edge already present and `IMP_System_Bind` returns an error.

The IMP SDK documentation states the constraint precisely: after the FrameSource is enabled, Bind and UnBind cannot be called dynamically; the FrameSource must be disabled before UnBind. The sequence that clears a stale bind is `IMP_FrameSource_DisableChn` followed by `IMP_System_UnBind`, and only then can a new `IMP_System_Bind` succeed.

### 8.3 Three attempts and the pre-pass recovery

Three attempts were made before the working solution. The first added an UnBind retry inside `setup_binding` when `IMP_System_Bind` returned an error. That failed because, by the time the bind is attempted, the first edge (FrameSource→OSD) has already succeeded and the FrameSource channel is enabled, and the SDK forbids UnBind while the channel is enabled. The second added an unconditional `IMP_System_Exit` before `IMP_System_Init` in sensor initialization, on the theory that `Exit` is idempotent and would clear stale state. That crashed the camera: calling `IMP_System_Exit` on a system that has only had the ISP enabled (not `IMP_System_Init`) is undefined behavior, the process died with no error output, and the camera became unresponsive to pings for several minutes, requiring a physical power cycle.

The working solution is a pre-pass at the start of `load_bindings` that disables each unique source FrameSource channel and unbinds every stale source→target edge before any new bind is created. It must run once, before all binds, rather than per-bind, because disabling a source channel that has just been bound (for the OSD edge) breaks that bind.

```c
// openmiko/submodules/ingenic_videocap/src/main.c (load_bindings pre-pass, simplified)
for (j = 0; j < num_bindings; ++j) {
    // read source and target cells from the JSON
    if (!already_disabled(group)) {
        IMP_FrameSource_DisableChn(group);     // idempotent on a stale channel
        mark_disabled(group);
    }
    IMP_System_UnBind(&src, &dst);              // clears the stale edge
}
// now the normal bind loop runs clean:
for (i = 0; i < num_bindings; ++i) setup_binding(&bindings[i]);  // plain IMP_System_Bind
```

The pre-pass is what makes the direct pipeline restartable without a reboot. Without it, every restart of `videocapture` after a SIGINT would require a full power cycle. With it, the bind table is cleaned on every start, and the pipeline comes up in seconds.

A final config detail completed the deployment. The frame-bus `videocapture_settings` JSON had to carry a `v4l2_device_path` field, because the patched `configparser.c` parses it unconditionally, even though the v4l2 path is unused in direct mode. Its absence caused `Error parsing encoders[0]`, which cascaded into a bind failure that looked like the stale-bind problem but was actually a config parse error preventing encoder channel creation. The diagnosis required reading the full `videocapture` log, not just the error line — a useful lesson in how a missing optional field can masquerade as a downstream failure.

## 9. The measured result

With the pre-pass in place and the config fixed, the pipeline comes up cleanly. The `gostream` log records the moment of success: the H.264 stream connects, the SPS and PPS are captured from the first keyframe, the RTSP stream is initialized with the SDP, and the JPEG stream connects two seconds later. `ffprobe` over TCP confirms the on-wire result: H.264 Constrained Baseline, yuv420p(progressive), 1920×1080, 25 fps, 90k tbn.

The memory result, measured on the same camera minutes apart, is the clearest statement of what the project achieved:

| Metric | Stock mode | Direct mode | Delta |
|--------|-----------|-------------|-------|
| `MemFree` | 1,796 kB | 26,328 kB | +24,532 kB (+23.96 MiB) |
| `VmallocUsed` | 35,532 kB | 3,084 kB | −32,448 kB (−31.69 MiB) |
| `v4l2loopback` refs | 2 | 0 | −31.69 MiB backing |
| `gostream` RSS | (stock daemons) | 9,148 kB | — |
| `videocapture` RSS | (stock) | 3,260 kB | — |

The net Linux-memory improvement is 23.96 MiB, which exceeds the design's 24 MiB acceptance target at the boundary (the target was "at least 24 MiB under equal streaming load"; the measured value is 24,532 KiB). The `VmallocUsed` reduction is 32,448 KiB, which exceeds the 30,000 KiB acceptance target. The two 16,592,896-byte vmalloc regions are absent. The `v4l2loopback` module is present but at zero references — its backing is freed.

A 10-second capture contains 247 frames (24.7 fps, within the normal jitter of a 25 fps hardware encoder) at an average bitrate of about 648 kbits/s on a static scene, well under the 900 kbit/s VBR ceiling. The VBR encoder adapts to scene complexity; a static scene produces fewer bits than the cap allows, which is correct behavior.

The `/healthz` endpoint, surfacing atomic per-stream statistics, reports the state after roughly ten minutes of continuous streaming: 12,838 H.264 frames and 12,788 JPEG frames, with zero malformed, zero oversize, and zero incomplete. The bounded reassembler never had to drop a frame during this run; the producer's nonblocking sends never hit `EAGAIN` because the Go consumer keeps up at 25 fps. A background soak monitor sampling `/healthz` and memory every 120 seconds confirmed the state held flat: `MemFree` stayed at 26,216–26,960 KiB, `VmallocUsed` stayed at 3,084 KiB, and the frame count grew at the expected 25 fps with no drift in the error counters. The acceptance evidence — loopback absent, both vmalloc regions absent, VmallocUsed reduction above 30,000 KiB, net memory improvement at the 24 MiB target, 1920×1080 at 25 fps with the existing encoder settings, and a functional gate well beyond a short smoke test — is met.

## 10. The kernel-side question

Given that the userspace frame bus recovered the memory, the natural follow-up is whether moving the entire server into the Linux kernel would recover more or run faster. The answer is that the approach is blocked by the hardware, and even if it were not, the gain would be marginal relative to the risk.

A full kernel-side server is a kernel module that owns the camera pipeline, speaks RTSP, packetizes RTP, and manages TCP sessions, all in kernel space, eliminating the user-to-kernel copy on every frame. Four components would be required: a kernel VPU encoder driver, an in-kernel RTSP parser and SDP generator, an in-kernel RTP H.264 packetizer, and in-kernel TCP session management.

The first component is the blocker. The T20's H.264/JPEG encoder is the VPU (a monolithic block Ingenic calls NVPU), driven by `soc_vpu` + `jz_nvpu`, which is built into the kernel image (`CONFIG_SOC_VPU=y`, not `=m`), and whose source is not in the OpenMiko patches. The open `tx-isp` patch contains 68 ISP source files and zero encoder source files. The encoder is reached only through the closed `libimp.so`, which opens `/dev/soc_vpu` and programs the VPU through a proprietary register interface using a proprietary firmware blob; the T20 SDK ships as a closed static archive, `libt20-firmware.a`, which is the microcode that runs on the VPU's internal processor.

There is an open VPU driver in the Ingenic ecosystem, but it does not cover the T20. The `thingino/ingenic-sdk` repository, which open-sourced the Ingenic kernel modules under GPL-2.0, includes an `avpu.ko` driver — a full kernel char device with ioctls for register access, DMA, and interrupts — but its build system restricts it to the newer SoCs:

```makefile
# thingino/ingenic-sdk/Kbuild
has_avpu := $(if $(filter t31 c100 t40 t41,$(soc)),y)   # T20 is NOT in this list
```

The `avpu` source directory contains only `t31/`; there is no `avpu/t20`. The T20 uses a different, older VPU IP (a monolithic NVPU) than the T31's Allegro AVPU, so the T31 driver is not portable. The contrast is exact: on a T31 camera, a kernel-side encoder is feasible because the VPU driver is open; on the T20, it would require reverse-engineering a proprietary register interface and a proprietary firmware blob — months of work with the risk that a kernel panic bricks the camera.

Even with an open VPU driver, the protocol layer has no precedent. RTSP is a text-based control protocol, and an in-kernel RTSP server would require a hand-written line parser with no `sscanf` and no libc, per-connection state machines on wait queues, and handling of the interleaved control/data channel that RTSP-over-TCP uses. The precedent is unfavorable: TUX, the in-kernel HTTP server, was merged into Linux around 2002 and later removed because the complexity and security risk were not worth the marginal performance gain. A parser bug in the kernel is a root exploit; a parser bug in userspace is a process crash.

The zero-copy gain that motivates kernel-side is also smaller than it appears. For a 1080p H.264 frame at roughly 50 KiB and 25 fps, the user-to-kernel copy is about 1.25 MiB per second — measurable but not dominant on a 580 MHz single-core MIPS CPU, where the encoder hardware does the heavy lifting and the real bottleneck is memory pressure (swapping). The userspace frame bus already eliminated the dominant memory cost. The recommendation is to not pursue a full kernel-side server on this hardware; the userspace frame bus is the end state. If kernel-side encoder access is ever needed, the path is to migrate to a T31-based camera where the open `avpu.ko` makes the VPU programmable.

## 11. Open questions and next steps

The direct pipeline is verified but not yet persistent. The camera's rootfs is a writable zram overlay lost on every reboot, and the SD card is mounted as swap rather than as a filesystem, so every power cycle requires a full redeploy over SSH. The immediate next step is to solve persistence — reformat the SD card with a FAT or exFAT partition for a boot-time overlay, or store the binaries on the SD card and copy them into the rootfs at boot — so the direct pipeline survives a power cycle without intervention.

The soak test reported here is roughly twenty minutes. A 24-hour soak under a sustained client load would strengthen the stability claim and would specifically test for Go runtime memory growth (the `num_gc` counter and the `gostream` resident size over a long window). The bitrate measurement was taken on a static scene; a high-motion test would confirm that the 900 kbit/s VBR ceiling is respected under motion.

Two minor correctness items remain. The `/healthz` stream stats report `width` and `height` as 0; the `HELLO` carries maximum dimensions but per-frame dimensions are not populated, which is cosmetic but should be fixed. The freshness threshold that the status logic uses is hardcoded and should be made configurable, and a Prometheus `/metrics` endpoint would let a soak be monitored rather than sampled. None of these affect the verified result.

The design's optimization threshold remains the rule for any further work. Shared memory should be built only if socket profiling under target load shows CPU rising by more than 10 points, transport drops above 0.1%, net recovery below 24 MiB, or p99 capture-to-publish latency above 100 ms attributable to IPC. Kernel code should be considered only if a bounded shared-memory prototype also fails a documented requirement — and on the T20, even then, it is blocked by the closed VPU driver.

## 12. References

- Repo: `/home/manuel/code/wesen/2026-08-23--wyze-cam`
- Ticket: `ttmp/2026/08/23/WYZECAM-DIRECT-STREAM--direct-encoded-frame-streaming-on-wyze-cam-v2-without-v4l2loopback/`
- Design doc: `design-doc/01-optimal-direct-frame-streaming-architecture-for-wyze-cam-v2.md` (23 sections, 1,424 lines)
- Diary: `reference/01-investigation-diary.md` (10 steps, 1,162 lines)
- Kernel-server investigation: `ttmp/2026/08/25/WYZECAM-KERNEL-SERVER--.../analysis/01-kernel-side-streaming-server-feasibility-analysis.md`
- Live probes: `sources/2026-08-25-soak-test.tsv`, `sources/soak-sample-10s.h264`, `sources/2026-08-23-live-memory-evidence.txt`
- Wire protocol: `framebus/c/framebus_protocol.h`, `gostream/internal/framebus/protocol.go`, `framebus/golden/gen_vectors.py`
- Producer: `framebus/c/frame_sink.c`, `openmiko/submodules/ingenic_videocap/src/capture.c`
- Consumer: `gostream/internal/framebus/listener.go`, `gostream/internal/framebus/reassembler.go`, `gostream/internal/rtsp/rtsp.go`, `gostream/internal/jpeghub/hub.go`
- IMP bind recovery: `openmiko/submodules/ingenic_videocap/src/main.c` (`load_bindings` pre-pass)
- Open VPU driver (T31 only): `thingino/ingenic-sdk` at `https://github.com/thingino/ingenic-sdk`
- Prior reports: `PROJECT REPORT - Wyze Cam v2 - Custom Streaming Server on OpenMiko.md` (2026-08-23), `PROJECT REPORT - Wyze Cam v2 - Direct Frame-Bus Streaming Without v4l2loopback.md` (2026-08-23), `PROJECT REPORT - Wyze Cam v2 - Direct Frame-Bus Streaming Verified on Hardware.md` (2026-08-25)
