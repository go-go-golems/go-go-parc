---
title: "ESP32 WiFi Architecture Comparison: ESP-Hosted (P4+C6) vs Native WiFi (S3) — Measured HTTP Throughput Across Three Devices"
aliases:
  - ESP32 WiFi Architecture Comparison
  - ESP-Hosted vs Native WiFi
  - Tab5 vs CoreS3 Benchmark
  - M5Dial Benchmark
tags:
  - article
  - esp32
  - performance
  - esp-hosted
  - benchmark
  - wifi
  - tcp
  - comparison
status: active
type: article
created: 2026-05-27
repo: /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5
---

# ESP32 WiFi Architecture Comparison: ESP-Hosted vs Native WiFi

This is the Wi-Fi architecture and measurement branch of the [[esp32]] project map.

This article compares measured WiFi/HTTP throughput across three M5Stack devices that share the same 2.4 GHz 802.11n radio but differ in how that radio connects to the application processor. The M5Stack Tab5 uses an ESP32-P4 application processor with an ESP32-C6 WiFi slave connected over SDIO (the ESP-Hosted architecture). The M5Stack CoreS3 and M5Dial both use an ESP32-S3 with integrated WiFi — the radio and the CPU share the same silicon die.

The central question is practical: how much does the SDIO interconnect cost, and how much can TCP stack tuning recover? The answer is not what intuition suggests. The default-configured native WiFi device uploads data *slower* than the ESP-Hosted device. After TCP window tuning, it is nearly four times faster. The SDIO link itself is not the bottleneck. The TCP receive window is.

> [!summary]
> Six findings from the three-device comparison:
> 1. **Default ESP32-S3 uploads at 3.7 Mbps — slower than ESP-Hosted's 4.2 Mbps.** The IDF default TCP window of 5,744 bytes strangles throughput more than the SDIO interconnect does.
> 2. **Optimized ESP32-S3 uploads at 16.0 Mbps — 3.8x faster than ESP-Hosted.** TCP window set to 65,535 bytes, WiFi buffers doubled, A-MPDU enabled. The native radio can sustain this; the ESP-Hosted C6's TCP stack controls the window and cannot be tuned from the P4 side.
> 3. **Download asymmetry reverses direction.** ESP-Hosted download is 1.7 Mbps (2.4x slower than its upload). Native download is 7.7 Mbps (2x slower than its upload but 4.5x faster than ESP-Hosted in absolute terms).
> 4. **Segment timing tells the story.** ESP-Hosted delivers many small segments (1,495 bytes avg) with frequent short gaps. Native WiFi delivers fewer, larger segments (up to 65,535 bytes) with fewer but longer pauses. The gap histogram shape distinguishes SDIO-bound from TCP-window-bound behavior.
> 5. **PSRAM availability determines maximum payload.** The M5Dial (no PSRAM, 224 KB free internal RAM) cannot accept uploads above 100 KB. The CoreS3 (8 MB PSRAM) handles 1.8 MB. The Tab5 (32 MB PSRAM) handles 1.8 MB.
> 6. **Ping RTT is architecture-independent at ~90-110 ms.** The SDIO transport adds only a few milliseconds over the WiFi radio round trip. The dominant cost is the IDF HTTP server's request dispatch, not the SDIO framing.

## Why this note exists

The [[ARTICLE - WiFi Throughput Benchmark on ESP32-P4 with ESP-Hosted - Measured Results and Bottleneck Analysis|Tab5 benchmark article]] established that ESP-Hosted upload saturates at 4.2 Mbps and download at 1.7 Mbps, with the gap explained by per-segment stall events. But the article could not answer a natural follow-up: is the SDIO link the cause, and would a single-chip design be faster?

Building the same benchmark firmware for the CoreS3 (ESP32-S3 with native WiFi) and the M5Dial (ESP32-S3 without PSRAM) answers that question. The answer requires nuance. The hardware architecture matters less than the software configuration. A misconfigured native WiFi stack is slower than ESP-Hosted. A well-configured native WiFi stack is dramatically faster. The difference is a few lines in `sdkconfig.defaults`.

This article stands independently. A reader choosing between ESP-Hosted and native WiFi for a new design will find the throughput comparison, the TCP tuning guidance, and the PSRAM implications directly applicable. A reader working with an existing ESP-Hosted system will find the segment timing comparison useful for understanding where their throughput goes.

## The three architectures under test

```
┌─────────────────────────────────────────────────────────────┐
│                      Tab5 (ESP-Hosted)                      │
│                                                             │
│  ┌──────────────┐  SDIO 4-bit 40 MHz  ┌──────────────┐     │
│  │  ESP32-P4    │◄═══════════════════►│  ESP32-C6    │     │
│  │  400 MHz     │   160 Mbps raw      │  160 MHz     │     │
│  │  RISC-V      │   ~12 MB/s eff.     │  RISC-V      │     │
│  │  32 MB PSRAM │                     │  WiFi radio  │     │
│  │              │  esp_wifi_remote    │  802.11b/g/n/│     │
│  │  lwIP TCP    │  (API forwarding)  │  ax (WiFi 6) │     │
│  │  IDF httpd   │                     │              │     │
│  └──────────────┘                     └──────┬───────┘     │
│                                              │              │
└──────────────────────────────────────────────┼──────────────┘
                                               │ 2.4 GHz
                                               ▼
┌─────────────────────────────────────────────────────────────┐
│           CoreS3 / M5Dial (Native WiFi)                      │
│                                                             │
│  ┌──────────────────────────────────────────────┐           │
│  │  ESP32-S3                                    │           │
│  │  240 MHz Dual-core Xtensa LX7                │           │
│  │  WiFi radio on-die (802.11b/g/n)             │           │
│  │                                              │           │
│  │  CoreS3: 16 MB flash + 8 MB Quad PSRAM      │           │
│  │  M5Dial:  8 MB embedded flash, no PSRAM     │           │
│  │                                              │           │
│  │  lwIP TCP ←→ esp_wifi ←→ 802.11 MAC/radio   │           │
│  │  IDF httpd                                   │           │
│  └──────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

The Tab5's ESP-Hosted architecture splits the network stack across two chips. The P4 runs the application, the TCP stack (lwIP), and the HTTP server. The C6 runs the 802.11 MAC, the radio, and the WiFi firmware. They communicate over a 4-bit SDIO bus at 40 MHz. The `esp_wifi_remote` driver on the P4 intercepts the standard `esp_wifi_*` API calls, serializes them into SDIO frames, and the C6 executes them. From the application's perspective, WiFi works identically. From a performance perspective, every frame crosses the SDIO bus, and the C6's TCP stack controls the advertised receive window.

The CoreS3 and M5Dial use a single ESP32-S3 chip. The WiFi radio, MAC, and CPU share the same die. There is no SDIO interconnect. The `esp_wifi` driver talks directly to the 802.11 MAC. The lwIP TCP stack runs on the same cores as the application. The application controls the TCP receive window directly.

### Hardware specifics

| Parameter | Tab5 | CoreS3 | M5Dial |
|---|---|---|---|
| Application CPU | ESP32-P4, 400 MHz RISC-V | ESP32-S3, 240 MHz Xtensa LX7 | ESP32-S3, 240 MHz Xtensa LX7 |
| WiFi chip | ESP32-C6, 160 MHz RISC-V | On-die | On-die |
| WiFi standard | 802.11b/g/n/ax | 802.11b/g/n | 802.11b/g/n |
| Interconnect | SDIO 4-bit 40 MHz | None (on-die) | None (on-die) |
| Flash | External, QIO 80 MHz | External, QIO 80 MHz | Embedded 8 MB |
| PSRAM | 32 MB Octal | 8 MB Quad | None |
| Free heap (after boot) | ~250 KB internal + 31 MB PSRAM | ~200 KB internal + 7 MB PSRAM | ~224 KB internal |

The M5Dial's lack of PSRAM is the most consequential hardware difference. The benchmark firmware allocates receive buffers in PSRAM when available. Without PSRAM, it falls back to internal RAM, which limits the maximum payload to approximately 100 KB (the free heap after boot is 224 KB, and the receive buffer, segment array, and HTTP stack must all fit).

## Benchmark methodology

The benchmark firmware, host script, and analysis queries are shared across all three devices with minor adaptations (PSRAM vs internal RAM allocation, maximum payload size). The methodology is identical to the one described in the [[ARTICLE - WiFi Throughput Benchmark on ESP32-P4 with ESP-Hosted - Measured Results and Bottleneck Analysis|Tab5 benchmark article]]:

- **Upload**: Host POSTs a byte payload to the ESP32. The firmware records per-segment timing (bytes + microsecond timestamp after each `httpd_req_recv()` call). Returns JSON with all timing data.
- **Download**: Firmware generates an incrementing byte pattern and sends it via `httpd_resp_send()`. Host measures wall-clock time.
- **Ping**: Host POSTs a small payload, firmware echoes it. Host measures RTT.
- **Repeats**: 3 per configuration. Reported values are averages.
- **Network**: All devices connected to the same home WiFi router (802.11n, 2.4 GHz, WPA2, SSID "yolobolo"). Host machine on the same LAN via Ethernet.

The CoreS3 and M5Dial were tested in two configurations:

**Default**: IDF default `sdkconfig` — TCP window 5,744 bytes, WiFi RX/TX buffers 32/32, no explicit A-MPDU configuration. This is what you get from `idf.py set-target esp32s3` with no additional settings.

**Optimized**: iperf-derived `sdkconfig` overrides — TCP window 65,535 bytes, WiFi RX/TX buffers 64/64, A-MPDU TX/RX enabled with BA window 32, 32 KB instruction cache with wrap. These settings come from the ESP-IDF iperf example, which represents Espressif's own recommended configuration for maximum throughput.

The Tab5 was tested only in its default configuration. The ESP-Hosted architecture prevents TCP window tuning on the P4 side — the C6's lwIP stack controls the advertised receive window, and there is no API to change it from the P4.

## Upload throughput

### Raw upload — all devices, all configurations

| Payload | Tab5 (default) | CoreS3 (default) | CoreS3 (optimized) | M5Dial (optimized) |
|---|---|---|---|---|
| 1 KB | 86.5 Mbps | 48.6 Mbps | 76.3 Mbps | 81.5 Mbps |
| 10 KB | 8.3 Mbps | 9.5 Mbps | 61.4 Mbps | 11.0 Mbps |
| 100 KB | 5.1 Mbps | 5.3 Mbps | 16.2 Mbps | 11.5 Mbps |
| 500 KB | 4.3 Mbps | 4.1 Mbps | 16.3 Mbps | — |
| 1 MB | 4.7 Mbps | 4.3 Mbps | 10.3 Mbps | — |
| 1.8 MB | 4.2 Mbps | 3.7 Mbps | 16.0 Mbps | — |

*Throughput in kbps (server recv time basis). The 1 KB and 10 KB numbers are inflated by HTTP overhead and do not represent real network throughput. The useful comparison starts at 100 KB.*

The data contradicts a straightforward reading of the hardware. The default-configured CoreS3 — with native WiFi, no SDIO, no ESP-Hosted — uploads 100 KB+ payloads at 3.7-5.3 Mbps, which is *slower* than the ESP-Hosted Tab5 at 4.2-5.1 Mbps. The native radio's advantage is erased by the IDF's default TCP receive window of 5,744 bytes, which limits the number of unacknowledged bytes in flight. At a 90-110 ms RTT, the bandwidth-delay product is:

```
BDP = RTT × bandwidth = 0.1 s × 20 Mbps = 2.5 MB
```

The default window of 5,744 bytes (5.6 KB) is 450x smaller than the bandwidth-delay product. The TCP sender cannot push more than 5.6 KB per RTT without receiving an acknowledgment. At 100 ms RTT, this yields:

```
max throughput = window / RTT = 5,744 / 0.1 = 57,440 bytes/s = 459 kbps
```

The observed 3.7-4.2 Mbps is higher than this theoretical floor because TCP uses window scaling (RFC 7323), which allows the effective window to exceed 65,535 bytes even with a 16-bit window field. The IDF enables window scaling by default, but the initial window and the window growth rate are still constrained by the configured `TCP_WND` value.

### What the TCP window tuning changes

The optimized configuration sets `CONFIG_LWIP_TCP_WND_DEFAULT=65535` and `CONFIG_LWIP_TCP_SND_BUF_DEFAULT=65535`. This tells the TCP stack to advertise a 64 KB receive window and to buffer up to 64 KB of unsent data. Combined with doubled WiFi RX/TX buffers (64 each) and A-MPDU aggregation, this allows the WiFi radio to deliver multiple MAC frames per TCP segment, and the TCP sender to keep the pipe full without waiting for per-segment acknowledgments.

The effect is dramatic. Upload throughput jumps from 3.7 Mbps to 16.0 Mbps at 1.8 MB — a 4.3x improvement. The same radio, the same antenna, the same physical channel. Only the software configuration changed.

On the Tab5, this tuning is not accessible. The C6's lwIP stack controls the receive window. The P4's `CONFIG_LWIP_TCP_WND_DEFAULT` setting has no effect because the P4 is not the TCP endpoint for the WiFi interface — it forwards frames to the C6, and the C6's TCP stack advertises its own window. The C6 firmware is closed-source and cannot be reconfigured.

### Why the ESP-Hosted default is faster than the native default

The ESP-Hosted Tab5 achieves 4.2 Mbps upload at 1.8 MB, while the default-configured CoreS3 achieves only 3.7 Mbps. The SDIO link does not make the Tab5 faster. The C6's default TCP window configuration makes it faster. The C6 ships with a different `sdkconfig` than the ESP32-S3's default, and the C6's WiFi firmware may use a larger receive window or different buffering strategy than the IDF default for the ESP32-S3.

The segment timing data supports this interpretation. The Tab5's segments average 1,495 bytes with many fast arrivals (608 segments within 0.5 ms of each other). The CoreS3 default segments average 3,754 bytes with far fewer fast arrivals (only 7 segments within 0.5 ms). The Tab5's smaller, faster segments indicate a more responsive receive pipeline — the C6 returns data to the P4 more frequently, which means the C6's receive buffers are draining faster, which means the TCP window is advancing faster. The CoreS3's larger, slower segments indicate that data accumulates in the WiFi driver's receive buffers and is delivered in larger chunks with longer pauses between them.

### M5Dial: same chip, no PSRAM

The M5Dial uses the same ESP32-S3 chip as the CoreS3 but with 8 MB embedded flash and no PSRAM. It was tested only with the optimized configuration. At 100 KB (the maximum payload that fits in internal RAM), it uploads at 11.5 Mbps — slower than the CoreS3's 16.2 Mbps at the same payload size.

The difference has two likely causes. First, the M5Dial's RSSI during testing was -50 dBm vs the CoreS3's -42 dBm, indicating a weaker WiFi signal. Second, the M5Dial has no PSRAM, so the benchmark firmware allocates its receive buffer and segment array from internal RAM. This competes with the WiFi driver's own buffer allocations, which also use internal RAM. When the WiFi driver cannot allocate sufficient RX buffers, it drops frames or signals the access point to pause transmission, creating the stalls visible in the segment timing.

The M5Dial's ping RTT (159 ms avg at 64 bytes) is significantly higher than the CoreS3's (89 ms). The RSSI difference (-50 vs -42 dBm) explains some but not all of this gap. The M5Dial's antenna may have different gain or orientation than the CoreS3's, or the M5Dial may be physically farther from the access point.

## Download throughput

### Download — all devices

| Payload | Tab5 (default) | CoreS3 (default) | CoreS3 (optimized) | M5Dial (optimized) |
|---|---|---|---|---|
| 1 KB | 81 kbps | 165 kbps | 82 kbps | 78 kbps |
| 10 KB | 395 kbps | 571 kbps | 717 kbps | 676 kbps |
| 100 KB | 1,445 kbps | 1,764 kbps | 4,262 kbps | 3,344 kbps |
| 500 KB | 1,808 kbps | 3,237 kbps | 5,900 kbps | — |
| 1 MB | 2,391 kbps | 3,122 kbps | 7,690 kbps | — |
| 1.8 MB | 1,744 kbps | 2,703 kbps | 7,692 kbps | — |

Download throughput shows the same pattern as upload, with one important addition: the upload/download asymmetry reverses between architectures.

On the Tab5, upload (4.2 Mbps) is 2.4x faster than download (1.7 Mbps). On the CoreS3 optimized, upload (16.0 Mbps) is 2.1x faster than download (7.7 Mbps). In both architectures, the device receives data faster than it sends it. But in absolute terms, the CoreS3's download at 7.7 Mbps is 4.5x faster than the Tab5's download at 1.7 Mbps.

### Why download is slower than upload on both architectures

The asymmetry is not caused by the SDIO link or by the WiFi radio's physical layer (802.11n uses the same modulation for uplink and downlink). It is caused by the interaction between TCP flow control and the WiFi MAC's contention mechanism.

During upload, the host sends data and the ESP32 sends TCP ACKs. The ACKs are small (40-60 bytes) and fit in a single WiFi frame. The ESP32's WiFi driver can send an ACK at any time — it contends for the channel, wins, transmits, and returns to receiving. The ACK delay is bounded by the channel contention time (0.5-2 ms on an uncongested channel).

During download, the ESP32 sends data and the host sends ACKs. The ESP32's TCP stack must wait for ACKs before sending more data (because the send window is limited by the receiver's advertised window). When an ACK is delayed — because the host's ACK must traverse the router, or because the WiFi uplink is momentarily contended — the ESP32's TCP window stalls. The `httpd_resp_send()` call blocks until the window advances.

The TCP window tuning helps in both directions. On the CoreS3 optimized, the 64 KB send buffer allows the ESP32 to push 64 KB of data before waiting for any acknowledgment. At 7.7 Mbps, 64 KB takes approximately 66 ms to transmit, which is within one RTT. This means the send buffer covers the full bandwidth-delay product, and the TCP stack can sustain throughput without stalling.

On the Tab5, the C6's default send buffer (likely 5,744 bytes, matching the receive window) is too small. At 1.7 Mbps, 5,744 bytes takes approximately 27 ms to transmit, but the RTT is 106 ms. The C6 must wait 79 ms for the first ACK before it can send the next window. This idle time dominates the download transfer time.

## Ping round-trip time

### Ping RTT — all devices

| Payload | Tab5 (default) | CoreS3 (default) | CoreS3 (optimized) | M5Dial (optimized) |
|---|---|---|---|---|
| 64 B | 87 ms | 94 ms | 89 ms | 160 ms |
| 256 B | 120 ms | 104 ms | 109 ms | 226 ms |
| 1,024 B | 108 ms | 173 ms | 140 ms | 271 ms |
| 4,096 B | 137 ms | 114 ms | 141 ms | 288 ms |
| 16,384 B | 189 ms | 203 ms | 202 ms | 312 ms |

The Tab5's minimum RTT of 87 ms and the CoreS3's minimum of 89 ms are within measurement noise of each other. The SDIO interconnect adds at most a few milliseconds — the SDIO round-trip for a 1 KB frame is approximately 0.2 ms (1 KB at 12 MB/s per direction). The dominant cost in both architectures is the IDF HTTP server's request dispatch path: receiving the HTTP request, routing it to the handler, processing the handler, and sending the response.

The M5Dial's higher RTT (160 ms at 64 bytes) correlates with its weaker RSSI (-50 dBm vs -42 dBm on the CoreS3). A weaker signal increases the 802.11 MAC's retransmission probability and may trigger lower MCS rates, both of which increase per-frame latency.

The TCP window tuning has minimal effect on ping RTT because ping payloads are small (well within any TCP window size). The slightly lower optimized RTT at 64 B (89 ms vs 94 ms) may reflect reduced WiFi driver buffering overhead when the RX buffer pool is larger.

## Segment timing comparison

The per-segment timing data reveals how differently the two architectures deliver data to the application. This comparison uses 1.8 MB raw uploads from each device.

### Segment count and size

| Metric | Tab5 (default) | CoreS3 (default) | CoreS3 (optimized) |
|---|---|---|---|
| Segment count | 1,233 | 491 | 57 |
| Average segment size | 1,495 B | 3,754 B | 32,337 B |
| Max segment size | 5,760 B | 5,760 B | 65,535 B |
| Avg inter-segment gap | 2.6 ms | 7.7 ms | 16.8 ms |
| Stalls > 50 ms | 5 | 6 | 2 |
| Gaps > 10 ms | 47 | 70 | 30 |

The Tab5 delivers data in many small segments (1,495 bytes on average) arriving frequently (2.6 ms average gap). The CoreS3 default delivers data in fewer, larger segments (3,754 bytes average) arriving less frequently (7.7 ms average gap). The CoreS3 optimized delivers data in very few, very large segments (32 KB average, up to 65 KB) arriving even less frequently (16.8 ms average gap) but with fewer stalls.

### Gap histogram comparison (1.8 MB upload)

| Gap range | Tab5 (default) | CoreS3 (default) | CoreS3 (optimized) |
|---|---|---|---|
| 0.1 - 0.5 ms | 608 | 7 | — |
| 0.5 - 1 ms | 124 | 38 | 1 |
| 1 - 5 ms | 364 | 213 | 3 |
| 5 - 10 ms | 89 | 162 | 22 |
| 10 - 50 ms | 42 | 64 | 28 |
| 50 - 100 ms | 4 | 5 | 2 |
| > 100 ms | 1 | 1 | — |

The Tab5's gap histogram is dominated by the 0.1-0.5 ms bin: 608 fast segments arrive nearly back-to-back. These are the segments where the P4 calls `httpd_req_recv()`, the SDIO driver returns data from the C6's receive buffer, and the P4 immediately calls `httpd_req_recv()` again. The C6's receive pipeline delivers data faster than the P4 can drain it — the 0.32 ms average gap is the P4's `recv()` processing time, not a network delay.

The CoreS3 default's gap histogram has almost no fast segments (7 in the 0.1-0.5 ms bin). Most gaps fall in the 1-10 ms range (375 total), with a long tail of 10-50 ms gaps (64) and 50-100 ms stalls (5). The absence of fast segments means the TCP receive window is not advancing fast enough to keep data flowing. Each time the window fills, the sender pauses until an ACK arrives and the window advances. The 1-10 ms gaps are the time the sender waits for an ACK round trip after the window fills. The 10-50 ms gaps are the time the sender waits after a retransmission timeout or a MAC-layer backoff.

The CoreS3 optimized's gap histogram has only 56 gaps total (57 segments, 56 gaps). The 28 gaps in the 10-50 ms range are the dominant cost, but there are only 2 stalls > 50 ms. The total gap time is:

```
(1 × 1 ms) + (3 × 2.5 ms) + (22 × 7.4 ms) + (28 × 23.4 ms) + (2 × 57 ms) = 937 ms
```

The server recv time for this upload was 933 ms. The gaps account for nearly all of it. The data transfer itself (1.8 MB at the WiFi PHY rate) takes approximately 100-200 ms. The remaining 730-830 ms is spent waiting for the TCP window to advance, for WiFi retransmissions, and for MAC-layer backoff.

### What the segments reveal about the bottleneck

The Tab5's many small fast segments indicate a *responsive but narrow* pipeline. The C6 returns data frequently but in small chunks. The P4's `recv()` calls return quickly because the C6 always has data in its SDIO TX buffer. The throughput ceiling is set by the TCP window size (controlled by the C6) and the SDIO frame size, not by the P4's processing speed.

The CoreS3 default's few slow segments indicate a *starved* pipeline. The TCP receive window fills, the sender pauses, data accumulates in the WiFi driver's RX buffers, the window advances (when the application reads data and ACKs are sent), and then a burst of data arrives. The throughput ceiling is set by the TCP window size (5,744 bytes), which is far too small for the 90 ms RTT.

The CoreS3 optimized's very few very large segments indicate a *saturated* pipeline. The 64 KB TCP window covers the bandwidth-delay product. The sender pushes data continuously, the WiFi driver buffers multiple MAC frames, and `httpd_req_recv()` returns large chunks (up to 65,535 bytes) that span many TCP segments. The throughput ceiling is now set by the WiFi PHY rate and MAC overhead, not by the TCP window.

## The TCP window as the primary throughput control

The benchmark data supports a single dominant conclusion: the TCP receive window is the primary throughput control on ESP32 WiFi, and the ESP-Hosted architecture prevents the application developer from adjusting it.

On a native ESP32-S3, the TCP window is configured in `sdkconfig.defaults`:

```
# TCP window — the single most impactful setting for WiFi throughput
CONFIG_LWIP_TCP_SND_BUF_DEFAULT=65535
CONFIG_LWIP_TCP_WND_DEFAULT=65535

# WiFi buffers — allow the driver to hold more frames in flight
CONFIG_ESP_WIFI_DYNAMIC_RX_BUFFER_NUM=64
CONFIG_ESP_WIFI_DYNAMIC_TX_BUFFER_NUM=64

# A-MPDU — aggregate multiple MAC frames into one transmission opportunity
CONFIG_ESP_WIFI_AMPDU_TX_ENABLED=y
CONFIG_ESP_WIFI_TX_BA_WIN=32
CONFIG_ESP_WIFI_AMPDU_RX_ENABLED=y
CONFIG_ESP_WIFI_RX_BA_WIN=32
```

These six lines transform the CoreS3 from 3.7 Mbps to 16.0 Mbps upload and from 2.7 Mbps to 7.7 Mbps download. They cost nothing in flash or RAM beyond the buffer allocations, and they have no negative side effects on stability or latency for small payloads.

On the ESP-Hosted Tab5, the C6's TCP stack controls the receive window. The P4's `CONFIG_LWIP_TCP_WND_DEFAULT` has no effect because the P4 is not the TCP endpoint for the WiFi interface. The C6 firmware is a prebuilt binary with its own configuration. There is no documented API to change the C6's TCP window size from the P4 side.

This is the architectural cost of ESP-Hosted: not the SDIO latency, not the SDIO bandwidth, but the loss of control over the TCP stack parameters. The SDIO link could carry 96 Mbps, the C6's radio could sustain 20-30 Mbps, but the C6's default 5,744-byte TCP window limits throughput to 4.2 Mbps. And there is nothing the P4 application can do about it.

## PSRAM and maximum payload

The M5Dial's lack of PSRAM imposes a hard limit on the maximum payload size. The benchmark firmware allocates its receive buffer and segment timing array at runtime. With PSRAM, these allocations come from the PSRAM pool (hundreds of MB available). Without PSRAM, they come from the internal RAM pool (224 KB free after boot).

The practical maximum on the M5Dial is 100 KB. At this size, the firmware allocates a 100 KB receive buffer, a segment array for up to 1,024 segments (each 16 bytes of timing data), and the HTTP server's 8 KB stack. Total: approximately 118 KB, leaving 106 KB for the WiFi driver, the lwIP stack, and other system tasks.

This has implications for the screen viewer use case. A 720×1280 RGB565 frame is 1.8 MB. With PSRAM, the firmware allocates a 1.8 MB receive buffer, decompresses the frame into another 1.8 MB buffer, and blits it to the display. Without PSRAM, this is impossible — the frame does not fit in memory. Compression helps (the compressed size is 120 KB for real images), but the decompressed frame still needs 1.8 MB of RAM for the blit operation.

For the M5Dial, the screen viewer use case requires either: (a) a smaller display (the M5Dial's 240×240 round display needs only 115 KB for a full frame), or (b) a chunked blit that decompresses and displays in strips, never holding the full frame in RAM.

## Working rules

1. **Always set `TCP_WND` and `TCP_SND_BUF` to 65,535 on native ESP32 WiFi.** This is the single most impactful throughput optimization. It costs six lines in `sdkconfig.defaults` and delivers 3-4x improvement.

2. **Do not assume native WiFi is faster than ESP-Hosted by default.** The default TCP window of 5,744 bytes on the ESP32-S3 produces 3.7 Mbps upload — slower than the ESP-Hosted Tab5's 4.2 Mbps. The C6's default window is apparently more generous.

3. **ESP-Hosted throughput is capped by the C6's TCP configuration, not by the SDIO link.** The SDIO bus has 23x headroom over the measured 4.2 Mbps. The real constraint is the C6's TCP receive window, which the P4 cannot control.

4. **Measure segment timing before diagnosing WiFi throughput.** The gap histogram distinguishes SDIO-bound behavior (many fast small segments) from TCP-window-bound behavior (few large segments with long gaps). This distinction determines which optimization will help.

5. **PSRAM availability determines which workloads are possible.** Without PSRAM, the M5Dial is limited to ~100 KB payloads. The screen viewer use case (1.8 MB frames) requires PSRAM. When evaluating an ESP32 board for a WiFi-intensive application, check for PSRAM first.

6. **Design around the RTT, not the bandwidth.** All three devices show 90-160 ms RTT for small payloads. This dominates the performance of request-response protocols. Batch operations, use HTTP keep-alive, and compress payloads to stay within one RTT when possible.

## Key files and reproducibility

| File | Purpose |
|---|---|
| `0094-tab5-wifi-bench/` | Tab5 benchmark firmware + scripts + SQLite results |
| `0095-cores3-wifi-bench/` | CoreS3 benchmark firmware + scripts + SQLite results (default + optimized) |
| `0095-m5dial-wifi-bench/` | M5Dial benchmark firmware + scripts + SQLite results (optimized only) |

Each directory contains:
- `main/bench_server.c` — HTTP benchmark server with per-segment timing
- `main/wifi_app.c` — WiFi initialization (native or ESP-Hosted)
- `scripts/01-run-benchmarks.py` — Host-side benchmark runner
- `scripts/02-analyze-results.py` — 8 pre-built SQLite analysis queries
- `scripts/bench_results.db` — Full benchmark dataset

To reproduce: flash the firmware, connect the device to WiFi, run `python3 01-run-benchmarks.py --base-url http://<DEVICE_IP>`.

## Related notes

- [[ARTICLE - WiFi Throughput Benchmark on ESP32-P4 with ESP-Hosted - Measured Results and Bottleneck Analysis|Tab5 benchmark article]] — detailed segment timing analysis for the ESP-Hosted architecture
- [[ARTICLE - Optimizing WiFi Image Upload on ESP32-P4 - From 6 Seconds to Sub-Second|Upload optimization article]] — the screen viewer firmware's compression and buffer optimization work
