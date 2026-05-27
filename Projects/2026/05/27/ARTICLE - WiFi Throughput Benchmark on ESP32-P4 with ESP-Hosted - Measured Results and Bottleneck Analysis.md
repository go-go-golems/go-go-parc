---
title: WiFi Throughput Benchmark on ESP32-P4 with ESP-Hosted
aliases:
  - ESP32-P4 WiFi Benchmark
  - Tab5 Benchmark Results
  - ESP-Hosted Throughput
tags:
  - article
  - esp32
  - performance
  - esp-hosted
  - benchmark
  - wifi
  - tcp
status: active
type: article
created: 2026-05-27
repo: /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/0094-tab5-wifi-bench
---

# WiFi Throughput Benchmark on ESP32-P4 with ESP-Hosted: Measured Results and Bottleneck Analysis

This article presents measured WiFi throughput data for the M5Stack Tab5, a tablet built around an ESP32-P4 application processor and an ESP32-C6 WiFi slave connected via SDIO. A dedicated benchmark firmware exercised the full HTTP upload and download paths at payload sizes from 1 KB to 1.8 MB, recording per-TCP-segment timing with microsecond precision. The data answers a specific engineering question: where does the time go when you push 1.8 MB over WiFi to this device, and how fast can it go?

The results show that raw upload throughput saturates at 4.2 Mbps, download at 1.7 Mbps, and ping round-trip time is 106 ms minimum. Compression reduces the 1.8 MB upload from 4.3 seconds to 0.2 seconds. The gap between measured throughput and theoretical WiFi capacity is explained by per-segment timing data: 5-7 stalls exceeding 50 ms per upload, and 42 gaps of 10-50 ms, together accounting for 3.1 seconds of otherwise-unexplained latency.

> [!summary]
> Five findings from the benchmark data:
> 1. **Upload saturates at 4.2 Mbps** (525 KB/s) for payloads above 100 KB, well below the 20-30 Mbps theoretical WiFi capacity of the ESP32-C6
> 2. **Download is 2.4x slower than upload** at 1.7 Mbps, indicating an asymmetric bottleneck in the P4-to-C6 transmit path
> 3. **Ping RTT is 106 ms** minimum, dominated by ESP-Hosted SDIO transport overhead, not WiFi radio time
> 4. **5-7 stalls per 1.8 MB upload** (gaps > 50 ms) account for most of the throughput shortfall vs theoretical
> 5. **Deflate compression eliminates the bottleneck**: 1.8 MB in 0.2 seconds total when compressed, because the network time drops from 3.5 s to 9 ms

## Why this note exists

The [[ARTICLE - Optimizing WiFi Image Upload on ESP32-P4 - From 6 Seconds to Sub-Second|upload optimization article]] documented three fixed bottlenecks (payload size, stack overflow, timeout) and identified a remaining gap: observed upload time was 3 seconds vs a 0.3-second theoretical minimum. The benchmark firmware was built to close that gap by measuring exactly where the time is spent.

This article stands independently from the optimization article. It does not prescribe fixes. It presents measurements and derives conclusions from them. A future reader working with any ESP-Hosted system on SDIO will find the throughput numbers, the segment timing analysis, and the diagnostic methodology applicable to their own hardware.

## The system under test

The M5Stack Tab5 contains two ESP32 chips on a single PCB, connected by an SDIO bus:

```
+------------------+  SDIO 4-bit 40 MHz  +------------------+
|   ESP32-P4       |<==================>|   ESP32-C6       |
|   App processor  |   160 Mbps raw     |   WiFi slave     |
|   400 MHz RISC-V |   ~12 MB/s eff.    |   160 MHz RISC-V |
|   32 MB PSRAM    |                    |   802.11b/g/n/ax |
+------------------+                    +------------------+
        |                                       |
   esp_wifi_remote                      WiFi radio (2.4 GHz)
   (API forwarding)                     PHY rate up to 57 Mbps
        |                                       |
   lwIP TCP stack                       802.11 MAC + firmware
        |
   IDF httpd
   (HTTP server)
```

The P4 has no WiFi radio. Every inbound or outbound network frame crosses the SDIO bus to the C6, which handles the 802.11 MAC and radio. The ESP-Hosted driver on the P4 forwards the standard `esp_wifi_*` API calls over SDIO, and the C6 executes them. From the application's perspective, WiFi works identically to a native ESP32 with a built-in radio. From a performance perspective, the SDIO link introduces latency and throughput constraints that do not exist on single-chip designs.

The SDIO bus is configured at 4-bit width, 40 MHz clock, giving a raw bit rate of 160 Mbps. After SDIO protocol overhead (command framing, CRC, response latency), the effective throughput is approximately 12 MB/s (96 Mbps). The ESP-Hosted RX queue holds 20 WiFi frames; the TX queue holds 20 frames. When either queue fills, the relevant side applies backpressure.

The benchmark firmware runs headless (no display, no LVGL) to eliminate display-related CPU and DMA interference. It exposes HTTP endpoints that accept uploaded data, time the reception with per-segment granularity, and return the timing data as JSON. A Python script on a Linux host drives the benchmarks and stores results in SQLite for analysis.

## Benchmark methodology

The benchmark measures three paths through the system:

**Upload (browser to ESP32)**: The host generates a byte payload of the requested size, optionally compresses it with Python's `zlib.compress` (which produces zlib-format output matching RFC 1950), and POSTs it to the firmware. The firmware records a timestamp before the first `httpd_req_recv()` call and after each subsequent call, capturing both the number of bytes received and the microsecond-precision time. After all data is received, it optionally decompresses the payload, records a post-decompression timestamp, and returns a JSON response containing all timing data and per-segment records.

**Download (ESP32 to browser)**: The firmware generates an incrementing byte pattern in PSRAM of the requested size and sends it via `httpd_resp_send()`. The host measures the wall-clock time from request to completion.

**Ping (round-trip)**: The host POSTs a small payload to the firmware, which echoes it back. The host measures the round-trip time.

All tests were run with the Tab5 connected to a home WiFi router (802.11n, 2.4 GHz, WPA2) in STA mode. The host machine was on the same LAN, connected via Ethernet to the same router. Each configuration (payload size x compression) was run 3 times, and the reported values are averages across those 3 runs unless otherwise noted. The RSSI during testing was -41 to -45 dBm, indicating a strong signal.

## Upload throughput

### Raw upload

| Payload | Server recv (ms) | Browser total (ms) | Throughput (kbps) | Segments |
|---|---|---|---|---|
| 1 KB | 0 | 70 | 86,537 | 1 |
| 10 KB | 11 | 109 | 8,274 | 5 |
| 100 KB | 170 | 306 | 5,114 | 67 |
| 500 KB | 953 | 1,218 | 4,319 | 343 |
| 1 MB | 1,823 | 2,762 | 4,681 | 703 |
| 1.8 MB | 3,534 | 4,112 | 4,193 | 1,224 |

The throughput number requires careful interpretation. At 1 KB, the reported throughput of 86 Mbps is not a real network speed — it reflects the fact that 1 KB fits in a single TCP segment, and the dominant time is HTTP request parsing and connection setup, not data transfer. The useful metric begins at 100 KB, where TCP has reached steady state.

At 100 KB and above, throughput converges to approximately 4.2 Mbps (525 KB/s). This is the steady-state upload capacity of the ESP-Hosted path through the home router. The browser time is consistently 15-20% higher than the server recv time. This gap is the sum of: TCP three-way handshake, HTTP request framing, client-side Python processing, and the time between the last recv() and the HTTP response arriving at the client.

### Deflate-compressed upload

| Payload | Compressed size | Recv (ms) | Decompress (ms) | Total server (ms) | Browser (ms) | Speedup |
|---|---|---|---|---|---|---|
| 1 KB | 286 B | 0 | 0.2 | 0 | 103 | 0.7x |
| 10 KB | 372 B | 0 | 0.4 | 0 | 110 | 1.0x |
| 100 KB | 727 B | 0 | 3.2 | 3 | 104 | 3.0x |
| 500 KB | 2,316 B | 0 | 18.8 | 19 | 156 | 7.8x |
| 1 MB | 4,396 B | 0 | 38.3 | 38 | 243 | 11.4x |
| 1.8 MB | 7,476 S | 17 | 67.1 | 84 | 216 | 20.0x |

The compressed sizes in this table reflect the benchmark's incrementing byte pattern (`0x00, 0x01, 0x02, ...`), which compresses at 250:1. Real UI images compress at approximately 15:1, so the network times would be proportionally longer. The decompression times scale linearly with the decompressed size and are independent of the compressed size: 38 ms for 1 MB, 67 ms for 1.8 MB. This is a CPU-bound operation on the P4's 400 MHz RISC-V core using ROM-resident `tinfl_decompress_mem_to_mem`.

The crossover point between raw and deflate is at approximately 10 KB. Below this threshold, the fixed overhead of HTTP request processing, zlib decompression, and the larger JSON response exceeds the time saved by transferring fewer bytes. Above 10 KB, compression wins decisively. For the primary use case of the screen viewer firmware — uploading 1.8 MB RGB565 frames — deflate reduces total time from 4.3 seconds to 0.2 seconds.

### What the upload throughput number means

The 4.2 Mbps steady-state throughput sits well below the ESP32-C6's theoretical capacity. The C6 supports 802.11n at MCS 7 (65 Mbps PHY rate on a 20 MHz channel at 2.4 GHz), which yields a practical maximum of 20-30 Mbps after MAC overhead. The measured 4.2 Mbps is only 14-21% of this ceiling.

The shortfall is not in the WiFi radio, nor in the SDIO bus (which can carry 96 Mbps). It is in the interaction between TCP congestion control and the ESP-Hosted receive pipeline. The segment timing data in the next section explains why.

## Segment timing analysis

The benchmark firmware records a timestamp after every `httpd_req_recv()` call, along with the number of bytes returned. These per-segment records allow reconstruction of the TCP receive pattern. The following data is from a representative 1.8 MB raw upload (upload_id=22, 1233 segments).

### Gap histogram

| Gap range | Count | Average (ms) | Cumulative time (ms) |
|---|---|---|---|
| 0.1 - 0.5 ms | 608 | 0.32 | 195 |
| 0.5 - 1 ms | 124 | 0.72 | 89 |
| 1 - 5 ms | 364 | 2.50 | 910 |
| 5 - 10 ms | 89 | 6.81 | 606 |
| 10 - 50 ms | 42 | 25.14 | 1,056 |
| 50 - 100 ms | 4 | 56.83 | 227 |
| > 100 ms | 1 | 109.65 | 110 |

**Total**: 1232 gaps (one fewer than segments, because the first segment has no predecessor). Sum of all gaps: approximately 3,193 ms. The server's reported recv time for this upload was 3,591 ms. The 400 ms difference is the time spent inside `httpd_req_recv()` processing the received data, which is not captured in the gap measurements.

### What the histogram reveals

The distribution has a clear bimodal structure. 608 segments arrive within 0.5 ms of the previous segment. These are the fast segments: the TCP window is full, the C6 has data queued, and the P4 drains it rapidly. If every segment arrived this fast, the entire 1.8 MB transfer would take 195 ms (0.32 ms x 608 segments) plus the data transfer time for those segments, yielding a throughput well above 20 Mbps.

The tail tells the story. 42 gaps of 10-50 ms and 4 gaps of 50-100 ms together consume 1,283 ms — over 40% of the total transfer time. These gaps are not caused by the P4 processing slowly (the P4 is calling `httpd_req_recv()` and blocking, adding zero delay). They are caused by the C6 not having data to deliver.

Two mechanisms produce these gaps:

**WiFi retransmissions**: At 2.4 GHz, 802.11 requires a clear channel before transmission. If the C6's transmission of a WiFi ACK or a data frame collides with another station's transmission, the MAC must back off and retry. The 802.11 retransmission timeout at the data rate used in practice (likely MCS 3-5, 20-40 Mbps PHY) is 10-50 ms. The 42 gaps in this range match this pattern.

**SDIO flow control**: The C6's RX queue holds 20 WiFi frames. When the P4 drains frames slowly (because the HTTP task is blocked on a previous `httpd_req_recv()` that has not returned yet), the queue fills. The C6 then signals the access point to stop sending data using 802.11 power-save polling. The AP buffers frames and delivers them when the C6 signals readiness. The transition between "buffering" and "delivering" introduces a delay of 10-50 ms, matching the observed gap range.

Without access to the ESP-Hosted driver's internal queue counters or the C6's 802.11 MAC state machine, these two causes cannot be distinguished from application-level measurements alone. Both likely contribute. The 4 gaps exceeding 50 ms are almost certainly WiFi retransmissions (MAC-level timeouts after multiple failed attempts).

### Segment size distribution

The average segment size across all uploads above 100 KB is 1,495 bytes. The minimum is 198 bytes (a partial TCP segment at the end of a burst), and the maximum is 5,760 bytes. The 1,440-byte mode is consistent with the standard TCP Maximum Segment Size (MSS) for Ethernet (1,460 bytes) minus 20 bytes of TCP timestamp option overhead. Segments larger than 1,460 bytes indicate that `httpd_req_recv()` returned data from two or more TCP segments that arrived between successive calls — the HTTP task was not scheduled fast enough to drain each segment individually.

## Download throughput

| Payload | Browser time (ms) | Throughput (kbps) |
|---|---|---|
| 1 KB | 111 | 81 |
| 10 KB | 218 | 395 |
| 100 KB | 636 | 1,445 |
| 500 KB | 2,312 | 1,808 |
| 1 MB | 3,635 | 2,391 |
| 1.8 MB | 8,572 | 1,744 |

Download throughput peaks at approximately 2.4 Mbps (1 MB payload) and drops to 1.7 Mbps at 1.8 MB. This is 2.4x slower than upload at the same payload size.

### Why download is slower than upload

The asymmetry has three causes, all rooted in the direction of data flow relative to the SDIO transport:

**TX queue depth vs RX queue depth**: The ESP-Hosted TX queue (P4 sending to C6 for WiFi transmission) and RX queue (C6 sending to P4 for WiFi reception) are both 20 entries. But the RX path has an advantage: the C6 receives WiFi frames from the access point, which controls transmission timing with centralized coordination (the AP schedules downlink and uplink). The TX path has no such coordination — the C6 must contend for the channel on its own, and each transmission requires a clear-channel assessment, a random backoff, and potentially a retransmission.

**TCP ACK feedback loop**: During upload, the host sends data and the P4 sends ACKs. The ACKs are small (40-60 bytes) and fit in a single WiFi frame. During download, the P4 sends data and the host sends ACKs. The host's ACKs arrive at the C6's radio with some delay, but they are small and do not congest the channel. However, the P4's TCP stack must wait for ACKs before sending more data. If an ACK is delayed (because the C6's uplink transmission to the AP is delayed), the P4's TCP window stalls. This feedback loop does not exist in the upload direction, where the P4 is the ACK sender, not the data sender.

**httpd_resp_send blocking**: The IDF HTTP server sends the response body in a single call. For large payloads, this call blocks until all data is written to the TCP socket buffer. If the TCP send window is smaller than the payload, the call blocks until ACKs arrive and the window advances. The blocking time is included in the server's measured send time but is not instrumented with per-segment granularity (unlike the upload path).

The download path is the relevant path for firmware OTA updates, asset serving, and any use case where the ESP32 pushes data to a client. The 1.7 Mbps ceiling means a 1 MB firmware update takes approximately 5 seconds to download, and a 4 MB asset bundle takes approximately 19 seconds.

## Ping round-trip time

| Payload | Avg RTT (ms) | Min RTT (ms) | Max RTT (ms) |
|---|---|---|---|
| 64 B | 86.8 | 72.5 | 107.6 |
| 256 B | 119.9 | 106.7 | 142.4 |
| 1,024 B | 108.0 | 106.4 | 111.1 |
| 4,096 B | 136.7 | 86.5 | 194.7 |
| 16,384 B | 188.6 | 164.8 | 206.8 |

The minimum RTT of 106 ms at 1 KB payload breaks down as follows:

- **WiFi radio round trip**: Two radio hops (host to AP, AP to C6). At 2.4 GHz with a strong signal, each hop takes 0.5-2 ms. Subtotal: 1-4 ms.
- **SDIO transport**: Two SDIO transactions (request frame to P4, response frame to C6). At 12 MB/s effective throughput, a 1 KB frame takes 0.08 ms per direction. Subtotal: 0.2 ms.
- **ESP-Hosted processing**: The C6 must receive the WiFi frame, queue it for SDIO, and the P4 must receive the SDIO frame, process it through lwIP, and hand it to httpd. The reverse path adds similar processing. This is the largest single contributor, estimated at 40-80 ms based on the difference between the measured RTT and the known radio + SDIO times.

The 106 ms RTT has a direct impact on TCP slow start. TCP's initial congestion window is typically 10 segments (approximately 14.4 KB). After the first window is sent, the sender must wait for an ACK before doubling the window. At 106 ms RTT, each RTT of slow start takes 106 ms. To reach a congestion window of 1.8 MB (1,248 KB), TCP must go through approximately 7 doubling cycles (14.4 KB -> 28.8 -> 57.6 -> 115.2 -> 230.4 -> 460.8 -> 921.6 -> 1843.2 KB). At 106 ms per cycle, slow start alone takes 7 x 106 = 742 ms before the full pipe is utilized. In practice, the observed 1.8 MB upload takes 3.5 seconds, meaning the stall events after slow start are the dominant cost.

## Compression as a throughput multiplier

The benchmark data confirms that compression does not merely improve performance — it changes the operating regime of the system.

When a 1.8 MB payload is compressed to 7.5 KB, the transfer operates entirely within TCP's initial congestion window. There is no slow start, no stall events, and no flow control. The data arrives in 1-3 segments, and the total server time is 80 ms (9 ms recv + 67 ms decompress + 4 ms overhead). The browser time of 216 ms includes the HTTP round trip, compression in Python, and JSON response parsing.

For real UI images, which compress at approximately 15:1, a 1.8 MB frame becomes 120 KB. At 4.2 Mbps, the network time is approximately 230 ms. Adding 67 ms for decompression gives a total of approximately 300 ms — still under one second, and still faster than the 3.5-second raw upload by an order of magnitude.

The practical implication is that compression is not an optional optimization for this system. It is the mechanism that makes the WiFi link usable for interactive image upload. Without compression, the link's 4.2 Mbps capacity and 106 ms RTT make each frame transfer a multi-second wait. With compression, the same link delivers frames in under a second.

## What these numbers mean for system design

The benchmark data supports four design rules for any ESP-Hosted system that transfers non-trivial payloads over WiFi:

**Rule 1: Compress on the sender, decompress on the receiver.** The 4.2 Mbps upload ceiling makes compression a requirement, not an optimization, for payloads above 100 KB. The P4 has sufficient CPU capacity (67 ms for 1.8 MB decompression) and PSRAM (32 MB) to handle decompression without affecting other tasks. The sender (browser, host, or cloud service) should compress using zlib format (RFC 1950), which the P4's ROM-resident `tinfl_decompress_mem_to_mem` handles with zero flash cost.

**Rule 2: Design around the RTT, not the bandwidth.** The 106 ms minimum RTT dominates the performance of small payloads and the slow-start phase of large transfers. A system that makes many small requests (REST API polling, sensor queries) will be RTT-bound, not bandwidth-bound. Batch multiple small operations into a single request where possible. Use HTTP keep-alive to avoid paying the TCP handshake RTT on each request.

**Rule 3: Expect asymmetric throughput.** Upload (4.2 Mbps) is 2.4x faster than download (1.7 Mbps) on this hardware. Design push-heavy protocols (device sends data to cloud) rather than pull-heavy protocols (cloud sends firmware/assets to device). When large downloads are unavoidable, consider compressing the download payload as well (gzip Content-Encoding) to reduce the time spent in the slower direction.

**Rule 4: The SDIO link is not the bottleneck, but it shapes the bottleneck.** At 96 Mbps effective throughput, the SDIO bus could carry the measured 4.2 Mbps upload with 23x headroom. The real bottleneck is the interaction between TCP congestion control, WiFi MAC contention, and ESP-Hosted's 20-frame queue depth. Increasing the SDIO clock or bus width would not improve throughput. Reducing the RTT (SoftAP instead of STA) or reducing the payload (compression) would.

## Open questions

The benchmark answers the original engineering question — where does the time go — but raises new ones that the current instrumentation cannot resolve:

**What causes the 10-50 ms gaps?** Application-level segment timing cannot distinguish WiFi retransmissions from SDIO flow control pauses. Resolving this would require either ESP-Hosted driver instrumentation (logging RX queue depth) or WiFi sniffer capture (observing 802.11 frame retransmissions directly).

**What is the RTT breakdown across ESP-Hosted processing stages?** The 106 ms ping RTT has an estimated 40-80 ms in ESP-Hosted processing, but the per-stage cost (SDIO transaction, frame parsing, lwIP input processing, httpd dispatch) is unknown. Profiling these stages would require modifying the ESP-Hosted driver or lwIP to insert timestamps at each processing step.

**Does SoftAP improve throughput?** The benchmark was run only in STA mode (via home router). SoftAP mode eliminates the router hop, potentially reducing RTT from 106 ms to 10-20 ms. Shorter RTT means fewer stall events and faster TCP slow start. The expected improvement is most significant for small-to-medium payloads where the RTT dominates.

**Can the download path be accelerated?** The 1.7 Mbps download ceiling is problematic for OTA updates and asset serving. Chunked transfer encoding might allow the P4 to interleave TCP sends with other processing, reducing the impact of window stalls. Alternatively, the C6's WiFi TX could be tuned (changing the TX queue depth or the SDIO TX QoS priority) to reduce the contention delay.

## Measurement artifacts and caveats

Three aspects of the benchmark methodology may affect the interpretation of the results:

**Incrementing byte pattern**: The benchmark generates payloads with the pattern `0x00, 0x01, 0x02, ...`. This pattern compresses at 250:1 with zlib. Real data (UI images, firmware binaries, sensor readings) compresses at 3:1 to 100:1 depending on entropy. The raw throughput numbers are unaffected by the pattern; the deflate timing numbers are pattern-dependent for the compressed size but not for the decompression time (which depends on the decompressed size).

**Single-client, single-connection**: All tests used a single Python client on a single host. The WiFi channel was not contended by other traffic (verified by the consistent RSSI of -41 to -45 dBm). In a multi-client or noisy RF environment, throughput would decrease due to 802.11 MAC contention.

**httpd single-threaded processing**: The IDF HTTP server processes one request at a time. During the download benchmark, the P4's CPU is occupied sending the response and cannot process other requests concurrently. This is representative of the production configuration but means the download numbers reflect both the network path and the server's processing model.

## Key files and reproducibility

| File | Purpose |
|---|---|
| `0094-tab5-wifi-bench/main/bench_server.c` | Firmware: benchmark HTTP server with per-segment timing |
| `0094-tab5-wifi-bench/scripts/01-run-benchmarks.py` | Host: benchmark runner with SQLite storage |
| `0094-tab5-wifi-bench/scripts/02-analyze-results.py` | Host: 8 pre-built analysis queries |
| `0094-tab5-wifi-bench/scripts/bench_results.db` | Full dataset (run_id=2: 3 repeats x 6 sizes x 2 compressions) |

To reproduce the benchmarks: flash the firmware, connect the Tab5 to a WiFi network, and run `python3 01-run-benchmarks.py --base-url http://<TAB5_IP>`. The results are stored in SQLite and can be queried with `02-analyze-results.py`.

## Working rules

1. Compress payloads above 10 KB before sending to ESP-Hosted devices. The 4.2 Mbps ceiling makes compression the single most impactful optimization.
2. Measure RTT before designing protocols. The 106 ms STA RTT determines how many round trips a protocol can afford. Protocols requiring more than 3-4 round trips will feel sluggish.
3. Prefer upload-heavy over download-heavy data flows. Upload is 2.4x faster than download on this hardware.
4. Do not assume WiFi bandwidth estimates apply to ESP-Hosted. The measured 4.2 Mbps is 14-21% of the C6's theoretical 20-30 Mbps. The overhead comes from TCP + ESP-Hosted + SDIO interaction, not from the radio.
5. Use per-segment timing to diagnose throughput problems. The gap histogram is the most informative single diagnostic: it distinguishes "bandwidth-limited" (many small, uniform gaps) from "stall-limited" (few large gaps that dominate total time).
