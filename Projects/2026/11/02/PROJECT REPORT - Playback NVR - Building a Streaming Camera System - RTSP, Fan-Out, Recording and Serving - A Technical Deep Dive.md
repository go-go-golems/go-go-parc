---
title: "Playback NVR: Building a Streaming Camera System — RTSP, Fan-Out, Recording and Serving — A Technical Deep Dive"
aliases:
  - Playback NVR deep dive
  - Building a streaming camera system
  - RTSP camera system deep dive
  - Go NVR deep dive
tags: [project-report, rtsp, rtp, video, h264, h265, nvr, go, streaming, cameras]
status: active
type: project-report
created: 2026-11-02
repo: /Users/manuel.odendahl/code/tulip/playback
source_commit: e0d38e36e
code_paths:
  - services/nvr-go/pkg/ingest/session.go
  - services/nvr-go/pkg/ingest/assembler.go
  - services/nvr-go/pkg/ingest/supervisor.go
  - services/nvr-go/pkg/ingest/errors.go
  - services/nvr-go/pkg/ingest/policy.go
  - services/nvr-go/pkg/media/media.go
  - services/nvr-go/pkg/timeline/timeline.go
  - services/nvr-go/pkg/timeline/ntp.go
  - services/nvr-go/pkg/bus/bus.go
  - services/nvr-go/pkg/recorder/recorder.go
  - services/nvr-go/pkg/recorder/health.go
  - services/nvr-go/pkg/recorder/fs.go
  - services/nvr-go/pkg/recorder/stream.go
  - services/nvr-go/pkg/mux/ts.go
  - services/nvr-go/pkg/mux/fmp4.go
  - services/nvr-go/pkg/mux/clip.go
  - services/nvr-go/pkg/testcam/camera.go
  - services/nvr-go/internal/camhub/camhub.go
  - services/nvr-go/internal/recmgr/manager.go
  - services/nvr-go/internal/rtspserver/server.go
  - services/nvr-go/internal/live/live.go
  - services/nvr-go/internal/ring/manager.go
  - services/nvr-go/internal/playback/concat.go
  - services/nvr-go/internal/decode/pool.go
  - services/nvr-go/internal/privacy/privacy.go
  - services/nvr-go/internal/redaction/redaction.go
  - services/nvr-go/test/pkgdeps/pkgdeps_test.go
related_vault_notes:
  - "[[01 - Index-Governed Reclamation - A Bounded Store Deletes Only What Its Index Names Under Its Root]]"
  - "[[PROJ - Screencast Studio - GStreamer Migration and Media Runtime Intern Guide]]"
---

# Playback NVR: Building a Streaming Camera System — A Technical Deep Dive

This report explains how a network video recorder for factory cameras works from end to end. The worked example is the Go NVR in Playback (`services/nvr-go`). The report covers the protocols a camera system has to speak: RTSP, RTP, RTCP, the H.264 and H.265 bitstreams, MPEG-TS and fragmented MP4. It then covers the architecture, in which one camera session feeds many consumers, and the problems that take most of the effort: time, storage, serving and privacy. Few of the hard lessons are about bytes. Most are about clocks, and about failures that look like success.

Playback is the on-premises computer-vision component of a manufacturing platform. Its NVR does the following:

- records every enabled camera continuously as six-second MPEG-TS segments;
- indexes those segments in TimescaleDB;
- serves live video to browsers;
- re-serves RTSP to a DeepStream analytics pipeline;
- produces snapshots and thumbnails, and exports clips;
- gates every frame behind a per-camera privacy setting that triggers person redaction.

The first implementation was a TypeScript service. It drove go2rtc, which held the camera sessions, and one ffmpeg process per media job. The Go port, written in October 2026, dials the cameras itself with gortsplib and does the media work inside its own process. The exception is decoding, which runs in separate worker processes.

> [!summary]
> 1. **One camera session per stream, shared inside the process.** A shared hub opens the camera once per source and quality. A bus with a bounded queue per consumer hands the video to the recorder, the live viewers, the RTSP re-server and the snapshot path. A consumer that falls behind loses whole GOPs and is told so in-band; it never blocks the others.
> 2. **Time is the hardest problem.** The NVR has four time sources: RTP timestamps, the arrival time of packets, the camera's sender-report clock and the host clock. None is right on its own. The NVR anchors each camera session to the lower envelope of arrival times, and trusts the camera's NTP only when it agrees with what arrival proves. Segment boundaries are chained so that one segment ends exactly where the next begins.
> 3. **Fail visibly, and never serve raw video when unsure.** Failures have types (auth, not found, timeout, stall, TLS). A camera shows green only when its video is on disk and in the index. Any doubt about the privacy setting means privacy is on.
> 4. **Test against real clients and a camera built to misbehave.** A fake camera can stall, flap, burst old frames, reset its clock and lie about NTP. ffprobe, GStreamer's `rtspsrc` and headless Chrome serve as independent judges of the output.

## 1. What the system has to do

A camera on a factory LAN produces a stream of compressed pictures. The NVR's job is easy to state:

1. Get the stream, from as many cameras as the host can carry.
2. Keep all of it for as long as the disk allows, each picture stamped with the time it was taken.
3. Show it live to people and to the analytics pipeline.
4. Find and replay any period later.
5. Hide people's faces and bodies whenever the site requires it.

Each item is harder than it looks.

**Cameras are unreliable.** They reboot. They drop their network link, which the NVR sees as a "flap". They change passwords and resolutions. Some restart their RTP clock at random, advertise features they do not have, or deliver several seconds of old video in a rush on connect, called a "join burst". The network between camera and NVR adds delay and loss. An operator can edit a camera's configuration at any moment.

**Consumers vary.** The recorder wants every frame and can tolerate seconds of latency. A browser wants low latency and can lose frames. DeepStream wants a plain RTSP stream and has its own reconnect logic, which has bugs. A snapshot wants one decoded picture, now.

The requirement that shapes the design most is that nothing reports health it does not have. A green camera that is not recording is worse than a red one, because nobody goes to fix it. An analytics pipeline that silently stopped is worse than one that crashed.

## 2. Vocabulary

| Term | Meaning here |
| --- | --- |
| NAL unit | Network Abstraction Layer unit: one piece of an H.264/H.265 bitstream, such as a slice of a picture or a parameter set |
| AU | Access unit: all NAL units of one picture, the unit everything downstream handles |
| Parameter sets | SPS/PPS (H.264) and VPS/SPS/PPS (H.265): the decoder configuration (profile, resolution, reorder depth) |
| IDR / IRAP | A picture a decoder can start from. IRAP (H.265) covers IDR, CRA and BLA |
| CRA, RASL | H.265 open-GOP random access: pictures after a CRA in decode order that reference pictures *before* it (RASL) cannot be decoded when decoding starts at that CRA |
| GOP | Group of pictures: an IDR and everything until the next one. Typical factory cameras use 1–2 s; some use 40 s |
| PTS / DTS | Presentation and decode timestamps; they differ when B-frames are reordered |
| Epoch | One continuous run of a camera's RTP clock, normally one RTSP session; a new session or a clock reset starts a new epoch |
| Timeline | The per-epoch mapping from RTP time to wall-clock time |
| Segment | One recorded MPEG-TS file (target 6 s, always cut at an IDR) plus its index row |
| Source / quality | A camera sensor (`camera_sources` row) and one of its streams (`high`, `medium`, `low`) |
| Lease | A consumer's reference to a shared camera session |
| Gap | A marker in the bus telling a consumer that AUs were dropped or the epoch ended |

## 3. The protocols

### 3.1 RTSP: the control channel

RTSP (RFC 2326 for 1.0, RFC 7826 for 2.0) controls a stream. It does not carry the video. A client speaks it over TCP, port 554 by convention, in an HTTP-like text format:

```text
OPTIONS   rtsp://camera/stream1          what methods do you support?
DESCRIBE  rtsp://camera/stream1          → SDP: tracks, codecs, parameter sets
SETUP     rtsp://camera/stream1/track1   → transport (UDP ports or TCP channels), Session id
PLAY      (Session)                      → RTP-Info: first sequence number and RTP time
GET_PARAMETER (Session)                  keep-alive (a session times out, 60 s by default in RFC 2326)
PAUSE / TEARDOWN
```

The DESCRIBE answer is an SDP document. It lists the media tracks, the RTP payload type of each, the codec (`H264/90000`) and usually the parameter sets (`sprop-parameter-sets`, or `sprop-vps/sps/pps` for H.265). The SETUP answer fixes the transport and returns the session id.

A few status codes matter in practice:

- 401 with a `WWW-Authenticate` challenge;
- 404 for an unknown path;
- 461 Unsupported Transport, for UDP asked of a TCP-only camera;
- 503 with `Retry-After`.

There are two authentication schemes. Basic sends the password base64-encoded. Digest is a challenge–response: MD5 in RFC 2617, and SHA-256 since RFC 7616. gortsplib reads the user and password from the URL's userinfo when it receives a 401. It prefers a SHA-256 Digest challenge, and lets any later challenge header replace Basic.

### 3.2 Getting the packets: UDP, TCP and TLS

The video travels as RTP packets in one of two ways:

- **RTP over UDP.** Each track uses a pair of ports, one for RTP and one for RTCP. It has the lowest latency, but packets can be lost and reordered, and firewalls or NAT can block it.
- **RTP interleaved on the RTSP TCP connection.** Each packet is framed as `$`, a channel byte and a 2-byte length. Nothing is lost, but a stalled connection blocks everything behind it, and a slow reader eventually stops the sender.

Playback uses TCP by default. The more interesting decision is that the transport is always set explicitly. gortsplib falls back from UDP to TCP automatically, but only when no protocol was configured. Setting one disables the fallback, so a camera that refuses the configured transport fails with a typed 461 error. The alternative is a session that quietly ran on something else. The policy is set per source with `NVR_GO_INGEST_TRANSPORT` and `NVR_GO_INGEST_SOURCES=<uuid>=udp+pin:<sha256>,...`.

RTSPS is RTSP over TLS. Cameras almost always present self-signed certificates, so the TLS policy has three modes:

| Mode | Behaviour |
| --- | --- |
| `skip-verify` | The default; encrypts but authenticates nothing |
| `verify` | System roots or a configured CA |
| `pin:<sha256>` | Skips chain validation, then compares the SHA-256 of the leaf certificate's DER bytes in `VerifyConnection`; colons in the hex are ignored |

The minimum version is TLS 1.2 and `ServerName` is the camera's host. Six tests cover the modes: zero value, skip, verify against system roots (which must fail), verify against the camera's CA, pin match, and pin mismatch.

### 3.3 Credentials in a URL

Camera credentials travel in the URL's userinfo: `rtsp://user:pass@host/path`. Two bugs in this repository come from that.

**Encoding.** The userinfo has to be percent-encoded as RFC 3986 specifies. The TypeScript side built URLs with the WHATWG URL encoder, whose userinfo set leaves `%` literal. Go's `url.Parse` then rejects the result. go2rtc 1.9.14 had the opposite problem: it answered "wrong user/pass" for passwords whose `:` or `@` was percent-encoded. The Go NVR builds dial URLs with `url.UserPassword`. Its test password contains `: @ % / space ? #`.

**Leaks.** RTSP, HTTP and ONVIF libraries all echo URLs in their error messages, so every error that may contain a URL passes through a scrubber before it is logged, stored, published or returned:

- `RedactURL` removes the userinfo and replaces the query with `?***`.
- `RedactText` also removes `user:pass` and the password itself, in raw and query-escaped form.
- A wrong-password test asserts that the password does not appear in the error.

Credentials that the operator typed into the URL themselves (an "operator-owned" stream) are used exactly as written.

### 3.4 RTP payload formats for H.264 and H.265

An RTP packet has a 12-byte header:

- payload type;
- a 16-bit sequence number, which detects loss;
- a 32-bit timestamp;
- the SSRC, which identifies the sender;
- a marker bit.

Video uses a 90 kHz clock. A 32-bit timestamp therefore wraps every 2³²/90000 s, about 13.3 hours. Any system that runs for days has to unwrap it into 64 bits.

The payload format says how NAL units fit into packets:

- **H.264 (RFC 6184), packetization mode 1:**
  - single-NAL packets;
  - STAP-A, which aggregates several small NAL units, such as SPS and PPS, into one packet;
  - FU-A, which fragments a large slice across packets.
  - STAP-B, MTAP and FU-B belong to the interleaved mode, which cameras do not use, and are refused.
- **H.265 (RFC 7798):** aggregation packets (AP) and fragmentation units (FU). PACI is not supported.

The marker bit should flag the last packet of an access unit. Some H.264 cameras never set it; gortsplib's code mentions a FLIR model. For H.264, gortsplib therefore also ends an AU when the timestamp changes. For H.265 only the marker ends an AU.

### 3.5 The bitstream: parameter sets and random access

A decoder needs its parameter sets before it can decode anything. They arrive in two places: in the SDP, and in-band before keyframes. The SDP copy may be missing, incomplete or out of date. Cameras change resolution or bitrate on the fly, and many put the new parameter sets only in-band.

The ingest therefore absorbs in-band parameter sets on every AU. A byte-level change produces a new `ParamSet` and increments `ParamChanges`. The current set is prepended to every random-access AU. One test starts a session with the SDP parameters removed and checks that the first published AU is an IRAP with complete parameter sets in front of it.

There are two framings of NAL units:

- **Annex B**: start codes `00 00 00 01`. MPEG-TS and the decode workers use it.
- **AVCC/HVCC**: length-prefixed. MP4 uses it, with the parameter sets moved into the `avcC`/`hvcC` box of the init segment.

`pkg/media` converts between them. It also drops access-unit delimiters and empty NAL units.

Random-access pictures:

- **H.264:** NAL type 5 (IDR).
- **H.265:** types 16–21 (BLA, IDR, CRA). A **CRA** begins an open GOP. The pictures that follow it in decode order may include **RASL** pictures (types 8–9), which reference pictures before the CRA. A file that starts at a CRA therefore begins with RASL pictures nobody can decode.

Design decision D15 drops RASL pictures after a file-initial CRA. `mux.RASLFilter` arms itself when the first AU is an H.265 CRA and drops RASL pictures until the first non-RASL one. Without the filter, a decoder silently produced 99 frames from a file that held 100.

### 3.6 Presentation time, decode time and B-frames

B-frames are predicted from pictures on both sides, so the encoder sends them after the later picture they reference. Decode order is then `I0 P2 B1`, while display order is `I0 B1 P2`. The RTP timestamp is the **presentation** time. The decode time is not on the wire and has to be reconstructed from the bitstream:

- picture order counts;
- the reorder depth (`sps_max_num_reorder_pics` in H.265; H.264 needs heuristics, and mediacommon caps reordering at 10 frames).

mediacommon's `DTSExtractor` does this. Every container downstream needs DTS to increase monotonically and PTS ≥ DTS. A violation does not show up at ingest. It shows up much later, when the muxer refuses the segment.

Chapter 6.3 tells how this went wrong. The H.264 extractor learns the reorder depth from the stream. A session that starts at `I0 P2 B1` already shows a deeper reordering than the extractor has seen. For that frame it returns the previous DTS plus 90 without checking it against PTS, which puts B1's decode time after its presentation time.

### 3.7 RTCP sender reports: the camera's wall clock

Alongside RTP, the camera sends RTCP **sender reports** (SRs). Each pairs an NTP wall-clock timestamp with the RTP timestamp of the same instant. If the camera's clock is synchronised, the SR says when each frame was *captured*. Arrival time cannot say that, because it includes network delay, encoder delay and any connect burst.

A relay that drops SRs destroys that information for everyone downstream. go2rtc 1.9.14 drops them, and that was one of the reasons to dial cameras directly (chapter 4.1). gortsplib exposes the SR-derived NTP time of every packet (`PacketNTP`).

### 3.8 Containers

| Container | Where it is used | What matters |
| --- | --- | --- |
| MPEG-TS | Recorded segments, HLS | 188-byte packets; PES headers with 33-bit PTS/DTS at 90 kHz (wraps every ~26.5 h); a PCR clock; self-synchronising and readable when truncated — the right format to write while a camera may vanish mid-file |
| Fragmented MP4 | Live view in the browser (MSE), playback | An init segment (`ftyp`+`moov`, holding the codec configuration) and then `moof`+`mdat` fragments; MSE needs an RFC 6381 codec string such as `avc1.64001f` or `hvc1.1.6.L93.B0` |
| Progressive MP4 | Clips for the vision pipeline | `moov` before `mdat` (playable while downloading); `ctts` version 1 allows negative composition offsets, so B-frames need no edit list |
| HLS | VOD and live playlists | `m3u8` lists of TS segments; `#EXT-X-DISCONTINUITY` where recording had a gap (> 1.5 s here) |

The TS muxer adds ffmpeg's default PTS offset of 126000 ticks (1.4 s). The offset has to exceed both mediacommon's PCR lead (DTS − 0.1 s) and the largest lead of PTS over DTS from B-frames, or timestamps near the start of a segment go negative. The muxer refuses `dts < 0 || pts < dts` with a "bad timestamps" error. That error is how the DTS bug of chapter 3.6 surfaced.

## 4. The shape of the system

### 4.1 Where it came from: go2rtc and a process per consumer

The TypeScript NVR was a single Node process: 27,154 production lines in 93 files. It handled:

- camera drivers, ONVIF and PTZ;
- provisioning, recording and housekeeping;
- delivery, the ring buffer, privacy and evidence.

go2rtc held the camera sessions, and the NVR `PATCH`ed streams into it. Every consumer opened its own RTSP connection to go2rtc over loopback:

```mermaid
flowchart LR
  CAM["Camera"] -->|RTSP| G2R["go2rtc<br/>holds the camera session"]
  G2R -->|loopback RTSP| FREC["ffmpeg recorder<br/>6 s TS segments"]
  G2R -->|loopback RTSP| FRING["ffmpeg ring<br/>HLS on tmpfs"]
  G2R -->|loopback RTSP| SE["stream-engine<br/>DeepStream"]
  G2R -->|frame.jpeg| FSNAP["ffmpeg per snapshot"]
  TSNVR["TypeScript NVR"] -.->|"PATCH streams, scrape /api/log"| G2R
  TSNVR -.->|spawn and supervise| FREC
  TSNVR -.->|spawn| FRING
  FREC --> DISK[("segments on disk")]
  TSNVR -->|"poll and index"| DB[("TimescaleDB")]
```

The design kept every component simple and pushed the hard parts into the gaps between them. Its known defects:

- **Errors without a reason.** go2rtc answered a flat RTSP 404 for every failure: a wrong password, an unreachable camera and a missing path all looked the same. To recover the reason, the NVR scraped go2rtc's `/api/log`. That depended on go2rtc's logging defaults; if they changed, every lookup would silently return null.
- **Lost configuration.** go2rtc forgot the `PATCH`ed streams when it restarted.
- **Missing features.** go2rtc never answered `PAUSE`, dropped RTCP sender reports, and crashed on `GET /api` (upstream issue #2443).
- **A process per snapshot.** Every JPEG snapshot started an ffmpeg process.
- **Three clocks for segment time:**
  - ffmpeg's local-time `strftime` epoch second, hence `TZ=UTC` everywhere;
  - the HLS program date-time, which go2rtc's connect burst pushed 1–14 s ahead, so it was believed only within 1 s;
  - PTS, which reset with every session and had no handling for the 26.5-hour wrap.
- **Hidden flaps.** The recorder's health stayed `running` while its segment files held 100–117 of the expected 150 frames.

Two incidents in October 2026 showed what that costs:

- **2026-10-01.** go2rtc lost a whole subnet for 27 minutes, and 12 of 15 sources were never retried. Analytics stopped for four hours while `/health` stayed green.
- **2026-10-05.** One source sat in a reset loop for 15 hours, and restarting go2rtc stuck four more.

The study before the port weighed three options:

| Option | Why it was or was not chosen |
| --- | --- |
| Keep go2rtc | Sender-report timing is lost at go2rtc |
| Fork go2rtc | About 50 modules and one maintainer |
| Dial cameras directly with gortsplib | Exposes the SR-derived NTP of every packet and the camera's real errors; chosen |

The plan had two steps. First, port the NVR as a go2rtc consumer. Second, dial the cameras directly and serve RTSP to stream-engine, opening one camera-side session per sensor and quality. A spike measured the whole pure-Go media core at about 2 % of one M1 Pro core per stream.

### 4.2 The Go NVR

```mermaid
flowchart LR
  CAM["Camera<br/>RTSP or RTSPS"] -->|"one session per source and quality"| SESS["ingest.Supervisor<br/>+ Session"]
  subgraph NVR["Go NVR process"]
    SESS --> BUS["bus.Bus<br/>access units"]
    BUS -->|"queue 750"| REC["recorder"]
    BUS -->|"queue 512"| RING["ring<br/>GOPs in memory"]
    BUS -->|"queue 128 per viewer"| LIVE["live fMP4"]
    BUS -->|"queue 250 per reader"| RS["RTSP server"]
    BUS -.->|"last IDR, cached GOP"| SNAP["snapshot and MJPEG"]
    SNAP <-->|pipes| DEC["decode workers<br/>separate processes, libav"]
  end
  REC --> DISK[("MPEG-TS segments")]
  REC --> DB[("segment index")]
  RS -->|"RTSP over TCP"| SE["stream-engine<br/>DeepStream"]
  LIVE -->|HTTP| BROWSER["browser MSE"]
  DISK --> PB["playback, export, HLS"]
  PB <--> RED["redaction service"]
```

Each camera stream is opened once. Its access units go onto one bus, and every consumer subscribes with its own bounded queue. The process starts no other process except the decode workers. The parts are:

- **camhub** owns the sessions, keyed by NVR system, source and quality.
- **recmgr** decides which streams are recorded and runs one recorder per stream.
- **rtspserver** re-serves the streams to stream-engine under go2rtc's old stream names, so stream-engine's URLs changed only in host and port.

The switch is a hard cutover per host. With `PLAYBACK_NVR_IMPL=go`, deploy runs `nvr-go` and removes both the TypeScript `nvr` and go2rtc. `nvr-go` uses host networking, which camera LANs and ONVIF multicast need, serves its API on 3002 and RTSP on 8554, and owns every subsystem. Rollback is `PLAYBACK_NVR_IMPL=ts` and a redeploy, with no data migration. stream-engine has to restart on every swap, because its reconciler keeps the `rtsp_url` it got first.

### 4.3 Package layering

The media core lives in `pkg/`: `timeline`, `scrub`, `media`, `bus`, `mux`, `ingest`, `recorder` and `testcam`. These packages never import the application (`internal/`, `cmd/`, `test/`). Between themselves, they import only along the edges of a table in `test/pkgdeps/pkgdeps_test.go`. The test parses every file's imports, whatever its build tags, and fails on any edge the table does not list. A new dependency therefore has to be added to the table on purpose.

Where a `pkg/` package needs something from the application, the dependency is inverted. For example, the recorder takes an indexer interface rather than a database. `internal/recmgr` is the single seam that converts the application's typed camera ids into the plain strings `pkg/recorder` uses.

There is no cgo in the core. `cmd/playback-nvr` builds with `CGO_ENABLED=0` into a static binary. `import "C"` is allowed only under the decode worker (`cmd/playback-decode/internal/libav`), and CI enforces this with `go list`.

## 5. Identity: which camera is this?

A camera system has more identities than it first appears to. Mixing them up fails silently: the code compiles, and every query returns zero rows.

| Identity | Type | Names | Used for |
| --- | --- | --- | --- |
| `nvr.cameras.id` | `CameraID` | The camera as the product knows it | API routes, foreign keys, settings, privacy, NATS subjects |
| `nvr.camera_sources.id` (= `cameras.external_id` for recorder cameras) | `CameraSourceID` | One sensor of a physical device | On-disk paths, stream names; never a foreign key target |
| NVR system id | `NvrSystemID` | Which NVR (built-in recorder or a vendor box) owns the camera | Driver selection, stream names |
| Quality | `StreamQuality` (closed enum) | `high`/`medium`/`low` | The stream within a source |

Each identity space has its own named type in `internal/ids`, so passing a `CameraSourceID` where a `CameraID` belongs does not compile. On the TypeScript side, PR #387 swapped the two at seven call sites and broke live streams across the fleet. The TypeScript side now has branded types too.

Path UUIDs are validated with zod's exact grammar, which is stricter than `uuid.Parse`, and echoed back exactly as received.

The stream name is `<nvrId>__<sourceId>__<quality>`, each part encoded with JavaScript's `encodeURIComponent`. That is the format go2rtc used.

camhub refuses non-canonical spellings, such as upper-case UUIDs. Postgres compares UUIDs case-insensitively, so a second spelling would find the same camera row and open a second session to the same camera. A review caught this.

Some more identity rules:

- One ONVIF device can have several sensors (`VideoSource` tokens), each its own source. Its media profiles map to qualities.
- Camera sync upserts on `(nvr_id, external_id)`, so a camera keeps its UUID across reconnects.
- Cameras are archived, never deleted, because the vision tables reference them with `ON DELETE RESTRICT`.

## 6. Ingest: from a URL to access units

### 6.1 The session

`pkg/ingest.Session.Run` drives one RTSP session from connect to close:

```text
parse URL                       → ErrProtocol on failure
client{Scheme, Host, Protocol, TLSConfig (rtsps only), Read/WriteTimeout}
Start → Describe → pick track   → first H.264, else first H.265, else ErrProtocol
Setup(track) → OnReady(params from SDP) → OnPacketRTP(decoder → assembler) → Play → Wait
ctx cancelled                   → a watcher closes the client; the cause is returned
```

Only one media is set up, so audio is ignored. Depacketization is gortsplib's (chapter 3.4). Two of its errors are normal and are not counted as decode errors: "more packets needed" and "non-starting packet without a previous one". Every other decode error, and gortsplib's own decode-error callback, increments `DecodeErrors`.

An AU's arrival time is the moment its first packet with a new RTP timestamp arrived.

### 6.2 Typed failures

A session fails with one of seven kinds, each its own error value. Classification uses types and status codes, never message text:

| Kind | From |
| --- | --- |
| `ErrTLS` | pin mismatch, x509 and TLS errors |
| `ErrAuth` | 401, 403, gortsplib's auth-setup error |
| `ErrNotFound` | 404, 410 |
| `ErrTimeout` | 408, TCP/UDP/request timeouts, deadline errors |
| `ErrConnection` | EOF, connection refused/reset, broken pipe, DNS |
| `ErrProtocol` | any other status, malformed streams, no usable track |
| `ErrStall` | the supervisor's watchdog (6.5) |

`Error{Kind, Op, URL, Status, Msg}` unwraps to its kind only. It does not keep the raw library error, which might contain a URL with credentials.

This table replaces the flat 404 of go2rtc. A camera whose password was rotated shows `auth` on the status page. A camera that is off shows `connection` or `timeout`.

### 6.3 The assembler

The assembler turns depacketized pictures into `media.AU` values. These carry:

- the epoch;
- a 64-bit RTP time and a reconstructed DTS;
- the arrival time, the NTP time and the wall time;
- whether the AU is an IDR;
- the NAL units, the parameter sets and the timeline.

Its per-AU logic, slightly simplified:

```text
push(nalus, rtp32, arrival, ntp):
    rtp64 = unwrap(rtp32)                       # signed int32 steps: reordering is never a wrap
    if resetDetector.check(rtp64, arrival):     # back > 1 s, or ahead of elapsed + 5 s
        endEpoch(); epoch = next(); timeline = new(); waitIDR = true; extractor = nil
    nalus, params = absorbParams(params, nalus) # in-band VPS/SPS/PPS
    if waitIDR:
        if not randomAccess(nalus) or not params.complete(): skippedPreIDR++; return
        waitIDR = false; extractor = extractor or new DTSExtractor(codec)
    if randomAccess(nalus): nalus = prependParams(params, nalus)
    dts, err = extractor.extract(nalus, rtp64)
    if err:          waitIDR = true; extractor = nil; return   # lost POC state: start afresh
    if dts > rtp64:  waitIDR = true; return                    # keep the extractor (see below)
    timeline.observe(rtp64, arrival); timeline.observeNTP(rtp64, ntp, arrival)
    return AU{..., Wall: timeline.mediaWall(rtp64)}

onPacketsLost(n): waitIDR = true; extractor = nil             # the GOP may not decode
```

```mermaid
stateDiagram-v2
  [*] --> WaitRAP
  WaitRAP --> Emitting: random-access AU with complete parameter sets
  Emitting --> WaitRAP: packet loss or extractor error, extractor discarded
  Emitting --> WaitRAP: DTS after PTS, extractor kept
  Emitting --> WaitRAP: RTP reset, new epoch and timeline
```

The DTS-after-PTS rule comes from a production failure. One camera of four never recorded, and its health said `quarantined: mux: bad timestamps pts=132000 dts=132090`. At session start, its GOP began `I0 P2 B1`, and the DTS extractor gave B1 the previous DTS plus 90, past B1's own PTS (chapter 3.6). The rejection hit 32, 32 and 6 of 150 GOP starts in three runs.

The fix drops the AU and waits for the next random-access AU. It keeps the extractor, because the reorder depth the extractor has now learned is what stops the drop from happening again. The cost is up to one GOP for every consumer, once per session.

The test fixtures had hidden the bug. ffmpeg's `testsrc2` encodes B-frames strictly in pairs, which never shows the reordering that triggers it.

### 6.4 Epochs: when the camera's clock restarts

The reset detector treats RTP time as reset in two cases:

- it goes back by more than 1 s, which is more than any B-frame reordering;
- it jumps ahead of the elapsed wall time by more than 5 s.

A reset ends the epoch and starts a new one with a fresh timeline, inside the same RTSP session. One test checks that a camera which resets its RTP clock mid-stream still uses one session and one PLAY.

The epoch matters downstream:

- the recorder closes its segment;
- live fMP4 starts a new run;
- playback inserts a discontinuity.

### 6.5 The supervisor

`ingest.Supervisor` keeps a session running for as long as its context lives:

```mermaid
stateDiagram-v2
  [*] --> starting
  starting --> running: first AU
  starting --> error: session failed
  running --> error: failure, 10 s stall or kick
  error --> starting: after backoff
  running --> stopped: context ended
  error --> stopped: context ended
```

**Every session is a new epoch.** A clean end of a session (nil or cancelled) still counts as a failure, `ErrConnection` "session ended". A camera that closes the connection is not healthy.

**Backoff** climbs 2, 4, 8, 16, 32, 60, 60 s. The ladder resets only after a session that delivered media. A camera that accepts PLAY and then sends nothing keeps climbing. Jitter of ±20 % is applied after the cap, so 60 s becomes 48–72 s, which spreads the reconnects when a whole subnet comes back at once.

**A stall watchdog** is armed at session start. If no AU arrives within 10 s, the session is cancelled with `ErrStall`. The message says whether any media had arrived.

**`Kick(err)`** cancels the current session with a given cause. The recorder uses it when its segments stop arriving. The cause of a stall or a kick replaces the client's close error, so status shows why the session ended, not just that the socket closed.

**`OnAuthFailure`** is a hook that fires once per authentication-failure episode, to raise an alert without spamming. It re-arms after a session that delivered media. It is tested (2 calls over 6 failures), but production does not wire it yet.

## 7. Sharing a camera session: camhub

Cameras limit how many sessions they accept, and every session costs the camera encoder time. The TypeScript design opened one per consumer. camhub opens one per `Key{NvrID, SourceID, Quality}` and hands out leases:

```text
Acquire(ctx, key) → *Lease
    refuse non-canonical keys           # before calling the resolver at all
    resolve(key) once                   # 10 s timeout; only ErrUnknownStream fails Acquire
    wait while the key's previous stream is still stopping   # the camera never sees two sessions
    take a reference, cancel any pending linger

Lease: Bus(), Watch(fn), Kick(err), Status(), WaitReady(ctx), Done(), Release()
```

Some details make this work:

- **The resolver runs on every session attempt,** not just on Acquire. A camera whose URL or password was edited reconnects with the new one. A resolver failure becomes `ErrNotFound` or `ErrConnection` with op `resolve`.
- **`Revalidate`** runs after every configuration reconcile. It re-resolves each live stream and kicks those whose target changed (URL, transport, TLS mode, pin or CAs) or whose source was removed. This fixed two bugs found in review: a source edit had kicked every quality, and removing a source had kicked nothing.
- **Linger.** The last `Release` keeps the session open for 30 s, so a page reload or a stream-engine reconnect does not reconnect to the camera. A generation counter (`lingerGen`) makes the timers of earlier releases harmless.
- **`Watch(fn)`** replays the current session's transitions and then follows them, so a late subscriber sees the same history as an early one.
- **`Status.Ready()`** is running *and* parameter sets known. The last error survives the start of the next retry, so status keeps showing why the last attempt failed.
- **`ErrNotServed`** marks a camera that belongs to a vendor NVR system the Go build does not drive.

Every live consumer goes through a lease: the recorder, the RTSP server, live viewers, MJPEG and the ring. They share the recorded quality, through `RecordedQuality`, instead of opening another one.

## 8. Fan-out: the bus

`pkg/bus` is the single point where one producer meets many consumers. Its package documentation states four rules:

1. There is one publisher goroutine per bus.
2. `Publish` never blocks.
3. A consumer that overflows sees only whole GOPs.
4. A gap is delivered in-band, attached to the first item after it.

```text
offer(sub, au):                                   # under the bus lock, called by Publish
    if sub.waitingForIDR and not au.IDR: sub.pending.Dropped++; return
    if sub.queue has room: send Item{AU: au, Gap: sub.takePending()}; return
    sub.waitingForIDR = true                       # queue full: drop to the next IDR
    sub.pending = sub.pending or Gap{Reason: overflow, Epoch, At: au.Wall}; sub.pending.Dropped++
```

A consumer never receives the middle of a GOP, so its output always decodes. The gap tells it why time jumped and how many AUs it lost.

The parts around `offer`:

- **`EndEpoch`** relabels a pending overflow gap as `epoch_end`, or queues a marker item, so the recorder can tell "I was slow" from "the camera's clock restarted".
- **ReplayGOP.** A new subscriber can ask to start with the cached current GOP. It gets `min(gop, capacity)` AUs queued under the same lock, so there is neither a gap nor a duplicate when live AUs take over. A truncated replay records an overflow gap for the rest.
- **The GOP cache** starts at an IDR. Each IDR starts a new backing array, so replays in flight keep the old one.
- **`LastIDR`** is an atomic pointer that survives `EndEpoch`. Snapshots read it without subscribing.

Queue sizes per consumer:

| Consumer | Queue | ReplayGOP |
| --- | --- | --- |
| Recorder | 750 AUs (30 s at 25 fps) | no — it must see the live edge, not old frames |
| Ring | 512 | yes |
| RTSP reader | 250 | yes |
| Live fMP4 viewer | 128 | yes |

One known gap: packet loss inside ingest is not reported to consumers as a bus gap. The assembler skips to the next IDR, and consumers see only the jump in time.

## 9. Time

### 9.1 Four clocks, and why none is enough

A recorded frame needs a wall-clock time accurate to tens of milliseconds, stable for days, and continuous across segment files. Four sources are available:

| Clock | Precise? | Absolute? | Failure mode |
| --- | --- | --- | --- |
| RTP timestamp | yes (90 kHz, encoder-paced) | no | Arbitrary start, wraps every 13.3 h, resets on reboot or at random, drifts against real time |
| Arrival time | no (network, encoder and buffering delay) | yes | A join burst delivers seconds of old frames at once; delay varies |
| Camera NTP (RTCP SR) | yes, if the camera is synced | yes | Camera unsynchronised, set wrong, or stepped; relays drop it |
| Host clock | — | yes | Only tells you when *you* saw something |

The design (decision D6) takes media time from RTP, anchors it to the wall clock with arrival evidence, uses camera NTP when it proves trustworthy, and stores every piece of evidence beside the result.

### 9.2 The lower envelope

Each AU gives an estimate of when the epoch's first frame happened:

```text
estimate = arrival − (rtp64 − rtp0) / 90 kHz
```

Every estimate is late by that AU's delivery delay. Live frames are late by network and encoder latency. Burst frames are late by seconds. The **minimum**, the lower envelope, is therefore the best estimate, and it only improves as frames arrive. With a window greater than zero it is a sliding-window minimum, which lets the anchor move later too when the camera clock runs slow. Ingest uses 60 s.

```text
MediaWall(rtp64) = anchor + (rtp64 − rtp0) / 90 kHz
```

The 500 ppm correction bound of 9.4 is Moonfire NVR's rule: media duration / 2000.

### 9.3 Camera NTP as evidence

An NTP-synchronised camera knows the capture time better than arrival ever can: no network delay, no join burst. But a camera's clock may be wrong, stepped or unsynchronised. `ObserveNTP` therefore uses the camera's mapping as the anchor only while it is consistent with what arrival proves:

- **Capture cannot follow arrival.** The NTP-implied anchor may be later than the envelope by at most 20 ms (`NTPTolerance`).
- **Capture does not precede arrival by more than 1 s** (`NTPMaxLead`, for encoder and network latency). A camera clock further behind than that is not believed.
- **Once trusted, the mapping may move only by 50 ms plus 1000 ppm of the elapsed time** between samples. A larger move is a clock step, and NTP is then rejected for the rest of the epoch. The next session may trust it again.

The states are `none`, `pending`, `trusted` and `rejected`. Until the first consistent sample, the envelope is used. That includes a join burst, whose envelope is seconds late and therefore inconsistent with any correct camera clock.


### 9.4 Boundaries that abut: the chain

Segment *n* must end exactly where segment *n+1* begins. Otherwise playback shows gaps or overlaps at every file boundary. `timeline.Chain` produces boundaries like this:

```text
boundary(n+1) = boundary(n) + media_duration(n) + clamp(pull toward MediaWall, ±500 ppm × media_duration(n))
```

Within an epoch, time never jumps, never drifts unboundedly, and `end(n) == start(n+1)` by construction. 500 ppm is 1 ms per 2 s of media, or 3 ms per 6-second segment. That is enough to track a drifting camera clock and small enough that nobody sees it. A correction that hits the clamp is counted and logged as a timing event: an encoder flush, a relay replaying ahead of the live edge, or a camera clock step.

```mermaid
flowchart TD
  A["AU: rtp64, arrival, optional NTP"] --> E["estimate = arrival minus media time since rtp0"]
  E --> ENV["anchor = lower envelope of estimates"]
  A --> N{"NTP consistent with arrival?"}
  N -->|yes| T["anchor follows camera NTP"]
  N -->|"no, or clock step"| ENV
  ENV --> MW["MediaWall = anchor + media time"]
  T --> MW
  MW --> CH["Chain: next boundary = previous + media + clamped pull toward MediaWall"]
  CH --> SEG["segment start and end, abutting"]
```

### 9.5 The join burst, and settling

The clamp has a consequence that a test exposed. `TestFaultJoinBurst` connects to a fake camera that replays its cached GOP on PLAY, as go2rtc did and some cameras do. The test failed 4 runs of 7. The first segment started 165–643 ms away from the true capture time, against a 100 ms bound.

The cause: the recorder fixed its first boundary while the burst was still arriving. At that moment the anchor was still moving earlier with every burst frame. The chain then carried that error forward, and at 1 ms per 2 s it would need many minutes to absorb a 400 ms error. Per-row logging proved it: the first row's anchor moved by exactly the start error, 408.70 ms against 407.91 ms.

The fix adds a notion of a **settled** timeline. The anchor is settled once one of these holds:

- it has not moved earlier by more than 20 ms in total during the last 500 ms of arrivals;
- the camera's NTP anchor is trusted.

Moves are measured against the anchor at the last counted move, not against the previous AU, so a high-frame-rate burst whose every frame moves the anchor by less than 20 ms still counts.

The recorder waits for settling, up to 5 s (`SettleWait`), before it fixes an epoch's *first* boundary. It does not wait at any later boundary, because those are chained from the first and waiting cannot improve them. It does not wait at the epoch's last boundary either, which has no following frame. A timeline that never settles costs one 5 s wait per epoch, and the timeout is counted as `UnsettledBoundaries`.

After the fix the test passed 8 of 8 runs, with first-segment errors of 0.27–1.34 ms. Seven mutations, each deleting one guard in a scratch copy, were each caught by the test named for that guard.

## 10. Recording

### 10.1 Cutting segments

The recorder consumes its bus subscription and cuts a segment on these events:

| Close reason | When |
| --- | --- |
| `target` | At an IDR, once the open segment holds ≥ 6 s of media; the IDR opens the next segment and the two share a boundary |
| `overflow` | A gap from a bus overflow: the recorder fell behind |
| `epoch_end` | A gap from the end of an epoch |
| `epoch` | An AU of a different epoch arrives (even without a marker) |
| `shutdown` | The subscription closed |
| `error` | An item failed to write |

A segment opens only at a random-access AU, so every file decodes from its first byte. The 6 s target is a minimum, not a maximum: a camera with a 40 s GOP produces 40 s segments. The end of a segment is the next segment's start when there is a following IDR. Otherwise it is the last presentation time plus one frame period.

Each index row carries the whole time evidence, not just a start and an end:

- source, quality, path, start, end, epoch;
- first and end RTP time, first NTP time;
- raw start (`MediaWall` of the first AU), anchor and correction;
- frame count, RASL pictures dropped;
- size, codec, width, height, close reason.

### 10.2 Writing files that never appear half-written

Each segment is written to a hidden name, `.seg_pending_<n>.ts`, in the stream's directory, and renamed into place when it closes:

```text
<recordings>/<sourceId>/<quality>/YYYY/MM/DD/HH/seg_<10-digit epoch second>.ts   (UTC)
```

- **Renames are atomic.** A file under its final name is always complete. The path function must stay on the filesystem of the pending file, or the rename would be a copy.
- **Name collisions** happen when two segments start in the same second, for example after a quick reconnect. The recorder then tries the next second, up to 60 times.
- **Startup cleanup.** `MkdirAll` creates the directory and stale `.seg_pending_*.ts` files from a crashed run are deleted.
- **Buffering.** Bytes go to the writer in chunks of 64 KiB.

The path grammar mirrors `shared/storage/layout.ts`, with golden vectors shared between the languages. The index stores absolute paths and matches them by exact string. Spelling a path differently makes every existing row look orphaned to housekeeping.

A per-process directory registry refuses a second recorder on the same directory (`ErrDirBusy`). The TypeScript stack once had two ffmpegs writing one directory, because a stop/start cycle reset its state flag. Across processes, the same exclusion comes from a Postgres advisory lock that the owning process holds.

### 10.3 Hung disks

A dead NFS mount or a failing disk does not return errors. It blocks: a `write` sits in uninterruptible sleep, and nothing can cancel it. The TypeScript stack found an ffmpeg wedged in such a state that ignored SIGTERM.

The Go recorder runs every file operation on a single goroutine, the `asyncWriter`, fed through an unbuffered channel. One deadline (10 s) covers both handing the operation over and waiting for its result. When the deadline passes:

- the writer is **abandoned**;
- every later call fails with `ErrWriterAbandoned`;
- the recorder is quarantined (10.6);
- the abandoned goroutine releases its directory lease only when the blocked call finally returns, if it ever does.

The filesystem sits behind an interface, so tests can simulate a mount that never answers.

### 10.4 The index

Each renamed segment is inserted into `nvr.recording_segments` in one READ COMMITTED transaction:

```sql
SELECT pg_advisory_xact_lock(hashtextextended(lower($camera) || '|' || $quality, 0));
SELECT max(media_sequence) FROM nvr.recording_segments WHERE camera_id = $camera AND quality = $quality;
INSERT ... media_sequence = max + 1 ...;
```

The lock key is spelled exactly like the TypeScript writer's. During a migration both writers can run, and they serialise on the same key. `test/crosslock` checks this by racing 150 TypeScript inserts (run under `tsx`) against 150 Go inserts and requiring a gapless sequence 1..300.

A unique-violation error (23505) means the row is already indexed, which counts as success.

A failed insert stays pending. It is retried in order at the next segment close, and pending rows survive into the next run. There is no timer-driven retry. Each insert has a 10 s timeout that does not depend on the recorder's context, so a shutdown does not abandon an insert halfway.

### 10.5 What "recording" means: health

The rule from the TypeScript incident history is that **a healthy indicator must be backed by recorded video, never by a live process or a configuration bit.** In code it works like this:

- A stream becomes `running` only when a segment *from the current session* is indexed. The recorder compares the segment's epoch against an epoch floor set at session start. The supervisor's own `running` state is deliberately not mapped to recorder health.
- **Progress is measured at the rename,** not at the insert. A database outage therefore does not look like a camera stall, while the index still governs what counts as recorded.
- **The stall window** is `max(4 × min(largest segment seen, 10 min), 30 s)`. It scales with the largest segment actually observed, because a 40 s GOP makes 40 s segments. The TypeScript stack once killed such a camera at 30 s, forever. The window is checked once per second, and a stall kicks the shared session (`Lease.Kick`).
- **States** are idle, starting, running, error and stopped. Transitions are delivered in order and deduplicated.

`is_connected` and `is_recording` on the camera row are derived from that state. Only components that observe the stream may write them: the recorder's status writer and camera sync. A lint rule (`no-camera-observation-write`) enforces this on the TypeScript side. It exists because a third writer, the API's create and update paths, once showed new, unreachable cameras as Online and REC.

### 10.6 Restart, not quarantine

At first, every recorder error quarantined the stream until the NVR restarted. On a shared session, one bad AU then stopped recording for good. Now:

- **Writer deadline or abandonment** quarantines the stream. A hung disk will not be fixed by retrying, and retrying would leak goroutines. Quarantine is sticky: the health record ignores every transition except stop.
- **Any other error** closes the segment with reason `error`. The recorder drops its subscription and waits a backoff: 1 s doubling to 30 s, reset after a run longer than 30 s. It then takes a fresh subscription. The shared session keeps running for the other consumers.

Four tests cover this, and each was checked by deleting its guard.

### 10.7 The reconciler

`internal/recmgr` owns the set of recorders. It reconciles on start, on `Reload()` (a coalescing channel), on a 60 s timer and when recording is paused or resumed:

```text
reconcile:
    systems: find the built-in recorder's NVR system (retry every pass while missing)
    sources: load enabled camera sources            # failure: keep the current workers
    for removed sources: retire
    for new sources: start a worker
    for changed SourceHash: stop and start again    # sha256 of the sorted-key JSON of type, config, streams, credentials, recording config
    camhub.Revalidate()
```

A source is recorded only when all of these hold:

- `recording_config.enabled` is truthy in the JavaScript sense;
- its quality is `quality ?? 'high'`;
- its camera row exists;
- `streams[quality]` exists. There is no fallback to another quality.

A worker acquires its camhub lease with a 30 s timeout and builds the recorder configuration with an indexer closure over the typed ids. It runs detached from the request that started it.

The status writer coalesces state changes, keeping only the newest. It skips writes the row already reflects, and re-asserts the live state 30 s after a failed write.

The recorder's metrics are segments written and indexed, index errors, RASL pictures dropped, abandoned writers, clamp events, name collisions, bytes and unsettled boundaries. They are exposed through the stream status, but not yet exported to Prometheus.

## 11. Keeping the disk from filling

Continuous recording fills any disk, so housekeeping deletes old segments. It follows a pattern written up separately in the architecture garden, [[01 - Index-Governed Reclamation - A Bounded Store Deletes Only What Its Index Names Under Its Root]]. In short:

- **Eviction is index-governed.** It deletes the oldest *indexed* segments when usage crosses a high-water mark, which is capped so that a minimum free margin always remains. It stops once usage has fallen by the band between the high and low marks.
- **Recording pauses** when free space falls to the margin, and resumes above twice the margin, so the disk cannot fill while eviction catches up.
- **Every delete is checked against the root,** lexically and again after resolving symlinks. A corrupt row cannot delete outside the recordings tree.
- **Orphan sweeps are braked.** Files on disk with no index row are swept only once they are an hour old. The sweep stops when the orphan ratio looks like an index outage rather than real litter: more than 5 orphans and more than 5 % of candidates once there are more than 100. It processes one bucket at a time.
- **A missing verdict is not an absence.** A path that the layout parser cannot classify (`nil`, no verdict) is never treated as absent and never deleted on that basis.

## 12. Serving

### 12.1 Re-serving RTSP to the analytics pipeline

stream-engine is one DeepStream 9.1 process per box, measured stable at 64 cameras. Its pipeline is:

```text
nvmultiurisrcbin → one nvurisrcbin/rtspsrc per camera → YOLOX → NvSORT → probes
```

It asks the NVR for a URL with `POST /internal/cameras/{id}/stream/ensure`. Under the Go NVR the answer points at the Go RTSP server, `rtsp://<host>:8554/<nvrId>__<sourceId>__<quality>`. The ensure call acquires and releases a lease and returns at once. It does not wait for the camera.

The server is a gortsplib server, written to be a better upstream than go2rtc:

- **DESCRIBE** acquires a lease and waits up to 5 s for the stream to be ready. The SDP comes from a description-only stream object, one per stream key and parameter set, to which nothing is ever written. DESCRIBE then releases its lease, and camhub's 30 s linger keeps the camera session warm for the SETUP that follows.
- **Failures have codes.** A malformed or unknown name gets 404 `Stream Not Found`. A camera that is not ready gets 503 `Source Not Ready: <kind>` with `Retry-After: 5`. Only the error kind is sent, never the camera's address.
- **Each reader is independent.** A SETUP session has its own bus subscription (ReplayGOP, 250 AUs), its own RTP encoder and gortsplib write queue (8192 packets). It writes nothing before PLAY and drops everything before the first IDR.
- **Slow readers** drop to the next IDR when their queue is full. They are evicted after 20 s of refusals, or after gortsplib's 10 s write timeout. An evicted connection is closed with RST (`SO_LINGER 0`).
- **Timing continues across reconnects.** A reader's RTP clock is continuous across camera reconnects (epochs) and PAUSE/PLAY, stepping at least one 25 fps frame. PAUSE stops the reader's pump; PLAY resumes with a GOP replay. GET_PARAMETER answers 200.
- **Sender reports** carry the epoch timeline's `MediaWall` as packet NTP, pairing each AU's own RTP time with its own wall time. Pairing them any other way had left B-frame streams 40–80 ms off. An explicit SR goes out whenever the mapping moves by more than 1 ms, at most every 200 ms.
- **New parameter sets** mark the old description stale; it closes once its last session ends. A codec change closes the reader's session so that it reconnects and gets a new SDP.
- **The network posture is narrow.** Transport is TCP interleaved only; no UDP ports are opened. Only loopback and the cluster's internal subnet may connect. There is no RTSP authentication and no privacy gate on this path, since the consumer is internal.

The consumer side has its own traps, all from incidents:

- **The reconnect watchdog.** nvurisrcbin has one: `rtsp-reconnect-interval` 10 s with unlimited attempts. But `init-rtsp-reconnect-interval` defaults to 0, so the first rtspsrc warning disabled the watchdog on exactly the source that needed it. Both are now set to 10.
- **Upstream timestamps are ignored.** DeepStream runs with `attach-sys-ts`, a choice made when go2rtc's timestamps were jittery. Under the Go NVR, the quality of the sender reports therefore does not affect stream-engine's timestamps.
- **A deadlock in reset.** The stock nvurisrcbin reset could deadlock the GLib main loop (2026-10-07). The image ships a patch that tears down from the sink end (decodebin, depayloaders, `rtpbin`) before `rtspsrc`, waking the push parked in a full jitterbuffer. The patch's native test must fail against the stock image, which proves it still reproduces the bug.
- **Stuck sources** restart only when all of these hold:
  - 120 s without frames after that source had produced frames;
  - the NVR says the camera was recording all that time;
  - 600 s since the last restart.
- **REST answers that lie.** DeepStream's REST server answered 200 to removals that had failed.
- **gortsplib's GStreamer delay.** gortsplib delays every SETUP answer by 1 s for a `GStreamer` User-Agent, so stream-engine starts about a second late.

### 12.2 Live video in the browser: fMP4 over MSE

Browsers cannot play RTSP. The live path sends fragmented MP4 over a plain HTTP response, which the page feeds to Media Source Extensions:

```text
GET /nvr/{nvrId}/cameras/{externalId}/fmp4
  privacy gate first (12.6)
  hub.Open(key, generation) → lease → bus subscription (ReplayGOP, 128 AUs)
  at the replayed IDR:        init segment (ftyp + moov, codec string)
  at every following IDR:     moof + mdat of the previous GOP
  on a parameter-set change:  a new init segment
```

Each fragment holds one GOP and is sent when the next IDR arrives, so latency is one GOP. The codec string is computed from the SPS following RFC 6381. `avc1.64000d` and `hvc1.1.6.L60.90` were verified to play in headless Chrome 156.

A slow viewer is never evicted for falling behind. The bus resumes it at the next IDR, and `LiveFMP4` keeps media time continuous. A new run never presents before the previous one ended.

That last guarantee was a bug fix. After a bus overflow, the next run had overlapped the cut GOP, and ffmpeg reported non-monotonic DTS. The fix estimates the end of a run as `max(lastDTS + period, maxPTS + period − IDR offset)`.

The route's 10 s write deadline handles a dead client. A privacy reload bumps the hub's generation and closes every viewer (12.6).

**MJPEG** (`…/mjpeg`) is the fallback for clients without MSE: multipart JPEG at 10 fps, decoded by the worker pool.

### 12.3 Snapshots, thumbnails and MJPEG: decoding out of process

Decoding needs libav. libav is C, can crash or hang on a bad bitstream, and must not take the recorder with it. Decoding therefore runs in separate worker processes (`cmd/playback-decode`). The core talks to them over pipes:

- **Protocol v1.** Each message is a u32 length, a strict JSON header (≤ 1 MiB) and a payload (≤ 64 MiB). The worker sends a hello, then handles strictly one job at a time. There is no cancellation message: cancelling a job means killing the worker.
- **The worker never opens files.** The core demuxes and sends Annex B access units, and selects pictures by exact PTS. A compromised or confused worker sees only the bytes of its job.
- **Each job is bounded:** 20,000 AUs, 256 wanted pictures, output size 2..8192, and at most 8192×4320 pixels. Snapshot routes tighten this to 4096² and 8 MiB.
- **The pool** runs 2 workers with a queue of 32, and answers `ErrBusy` when full:
  - job timeout 10 s, with a cap of 2 minutes;
  - kill grace 250 ms;
  - recycling after 1000 jobs or 1 GiB of RSS.

  A crash, hang or garbage output kills and replaces the worker and fails the job with a typed error. While a worker respawns, with backoff from 200 ms to 30 s, jobs fail fast with `ErrUnavailable`.
- **Worker hygiene.** Workers run with a minimal environment: `TZ=UTC`, `PATH` and the library path, no secrets. Their stderr goes through the bounded scrubbing collector. libav decodes and scales; Go's `image/jpeg` and `image/png` encode.

A **live snapshot** decodes the last IDR, or with `Latest` the cached GOP up to its newest AU. It refuses a cache older than 30 s. The frame's time is the timeline's `MediaWall`, not the time of the request.

**Segment thumbnails** decode up to 256 pictures in one pass. **Exact frames** for evidence are lossless PNG, located with `SeekContaining`.

One gap remains: workers do not set `Pdeathsig`, so a worker stuck inside libav outlives a dead core.

### 12.4 Recorded playback and export

Playback joins recorded segments without re-encoding. `playback.Concat` is a pure-Go replacement for `ffmpeg -f concat -c copy`, with three differences from ffmpeg:

- **Placement.** File *n* is placed at the sum of the earlier files' durations (`EndPTS − StartPTS`, computed the way ffmpeg computes `start_time`). Wall-clock gaps between files are closed, and a colliding DTS shifts the file forward.
- **Decision D15 at every file start.** RASL pictures after a file-initial CRA are dropped, so every boundary decodes. ffmpeg loses 40 ms per open-GOP boundary. Over the same H.265 open-GOP test material, Go gives 16.000 s where ffmpeg gives 15.760 s.
- **Bounded reads.** Reads are bounded by the context, at most 512 MiB per file. A read hung on a dead mount is abandoned rather than waited for.

On top of `Concat`:

- **VOD HLS.** Playlists insert `#EXT-X-DISCONTINUITY` at gaps over 1.5 s. Segments are served with Range support.
- **fMP4 playback and export.** Export is limited to 30 minutes. One fragment is written per GOP, and a parameter-set change emits a second init segment.
- **Export cache.** A redacted export is accepted from the cache only when its redacted frame rate is at least the original's. Misses are rendered one segment ahead, and the path fails closed when redaction is unavailable.

### 12.5 Short clips for vision: the ring

The vision pipeline asks for short clips of the recent past ("the 20 seconds around this event"). The TypeScript stack kept an ffmpeg HLS segmenter running per camera on tmpfs.

The Go **ring** is an in-memory list of whole GOPs per camera and quality. It has no camera session of its own: it subscribes to the shared bus (queue 512) and keeps 60 s, capped at 256 MiB. Runs are cut at every gap, epoch change and parameter change. Vision keeps a ring alive by posting `media/ensure` every 30 s; a ring expires after 90 s without one.

`media/materialize` decides where a clip comes from:

1. A window that ends in the future → 409.
2. The ring reaches back to the window start → clip from the ring. It waits for the IDR after the window end, but never longer than the window end plus 1.5 segment durations.
3. The stream is recorded → clip from the recordings, checking coverage, segment size (≥ 1024 bytes) and age (mtime ≥ 1 s).
4. Otherwise the ring, else 500.

Clips are progressive MP4 (`WriteClip`): `moov` first, `ctts` v1 and D15 at the start. Each is written to `<final>.tmp-<uuid>`, fsynced and renamed.

### 12.6 Privacy: the gate fails closed

Privacy is a per-camera flag with a deployment-wide fallback:

```sql
SELECT (coalesce(
          (SELECT cs.privacy_enabled FROM vision.camera_settings cs WHERE cs.camera_id = $1),
          (SELECT p.privacy_enabled FROM vision.privacy_config p WHERE p.id = 1),
          true) IS NOT FALSE) AS privacy_enabled
```

The camera's own row wins, then the deployment setting, then privacy on. Only an exact stored `false` turns privacy off. The Go query is byte for byte the TypeScript one. Every historical-video, snapshot, thumbnail, fMP4 and MJPEG handler asks the gate *before* it opens a file or a stream. Any error from the gate means privacy is on: database down, timeout, cancelled context or unknown camera. No code path serves raw bytes when privacy is on or unknown.

```mermaid
flowchart TD
  R["request for camera media"] --> G{"privacy gate"}
  G -->|"false"| RAW["serve raw"]
  G -->|"true"| ON["privacy on"]
  G -->|"error, timeout, unknown camera"| ON
  ON --> K{"which surface"}
  K -->|"recorded segment or export"| C{"redacted companion ready?"}
  C -->|yes| SR["serve .redacted.ts"]
  C -->|no| SYN["redact now, or 503 Redaction unavailable"]
  K -->|thumbnail| P["403 with redactedUrl, then 202 Retry-After until ready"]
  K -->|snapshot| IMG["redact the JPEG, 503 on failure"]
  K -->|"live fMP4 or MJPEG"| D["451; 503 when the privacy state is unavailable"]
```

The mechanics:

- **The cache** is per camera, with lookups deduplicated per version and camera. A lookup runs detached from the caller, with a 30 s timeout. A lookup that straddles an invalidation is answered but not cached.
- **Two invalidations.** A quiet one runs on every configuration poll. A loud one runs on `system.vision.reload` and closes every live fMP4 and MJPEG viewer. The live route reads the hub generation *before* its privacy check and retries once if the generation moved, so no viewer opened under the old verdict survives a reload.
- **Redaction** is a separate service. Segments are posted as file paths with a 120 s timeout, and identical requests are deduplicated. JPEG bytes are posted with a 15 s timeout and an 8 MiB cap; a 204 answer means no persons were found. Results are validated strictly and fail closed. A redacted segment is a companion file (`.redacted.ts` plus `.redact.json`) next to the raw one. A redacted thumbnail is served raw only when the sidecar confirms that no persons were found.
- **Tests.** The table-driven privacy tests cover every gated route crossed with off, ready, missing, redaction down and gate error.

Some paths are deliberately ungated in the NVR:

- the internal analysis snapshots, which feed the vision pipeline by contract;
- the ring and clip routes, which serve vision inside the cluster;
- the RTSP re-serve;
- the raw live HLS, which the API gates instead.

## 13. Managing cameras

### 13.1 Drivers and vendors

A camera system usually has to talk to other NVRs too: Hanwha, Frigate, UniFi Protect and others, each with its own API. The driver interface covers:

- identity, status and lifecycle;
- the camera list, refresh and system info;
- optional source reconciliation;
- two capability flags: redacted export and exact trim.

The Go build implements only the built-in recorder and a mock. Every other vendor gets an `Unsupported` driver. It reports status `error`, refuses camera and system calls, and never syncs or archives that system's cameras. This deliberately differs from TypeScript, where an unknown vendor threw and aborted the reconcile, and at boot the whole process.

Vendor drivers and ONVIF discovery and PTZ stay in TypeScript, so a host with vendor NVR systems cannot cut over yet.

A circuit breaker protects each vendor system. It opens after 5 failures, counts auth failures double, resets after 30 s and lets one half-open attempt through.

The built-in driver derives a camera's connection state in priority order:

1. Another process records it. The status columns are left to that process.
2. A worker exists. Only `running` counts as connected, and that verdict is observed.
3. No worker, but recording is on. The camera is offline, which is a fault.
4. No worker, recording off. The state follows `source.enabled`, optimistically, and does not advance `last_seen_at`.

### 13.2 A green dot means recorded video

Chapter 10.5 gave the rule. The TypeScript history behind it is a list of green dots without video:

- `running` was a latch: once set, nothing cleared it;
- a 30 s survival timer reset the retry ladder, so a crash-looping recorder looked healthy;
- the ladder itself hid failures for about 62 s;
- an API path wrote `is_connected = true` for cameras nobody had reached.

### 13.3 Capabilities that cameras lie about: zoom

Cameras advertise capabilities they do not have. Some Dahua-OEM fixed-lens models acknowledge ONVIF zoom commands and do not move. The `hasZoom` verdict therefore has three states: true, false and absent, which means unknown. It has two writers:

- **Discovery** writes it once per source, only when the key is absent. A probe that could not actually ask the camera persists nothing.
- **Jog retraction** demotes true to false when two `GetStatus` reads around a zoom jog prove that the lens did not move. Measurability is a precondition, checked in the raw SOAP, because the library renders an absent zoom position as `0`.

Both writes are compare-and-set on the whole source configuration. Retraction is sticky: only re-running the ONVIF import undoes it.

The general lesson: treat every capability a camera reports as a claim, store "unknown" as its own state, and demote a claim only on measured evidence.

## 14. Testing a camera system

### 14.1 A camera that misbehaves on purpose

`pkg/testcam` is a gortsplib server that serves pre-encoded H.264 or H.265. The source is ffmpeg's `testsrc2`, or a real video file letterboxed and looped. The fixture spec sets codec, size, frame rate, GOP, B-frames, H.265 open GOP and frame count. Fixtures are cached under a SHA-256 of the recipe version, the spec and the ffmpeg arguments, and written to a temporary name and renamed.

The fake camera is paced on a virtual clock: a frame is captured at `Start + PTS` and sent at `Start + DTS + reorder delay + latency`. Every RTP packet carries NTP = true capture time + a configurable offset, and `CaptureTime(rtp)` returns the ground truth. Timing tests can therefore assert accuracy, not just plausibility.

Its faults reproduce what real cameras and relays do:

| Fault | Behaviour | What it exercises |
| --- | --- | --- |
| `nodata` | DESCRIBE/SETUP/PLAY succeed, then nothing is sent | stall watchdog, "no media" error, backoff that does not reset |
| `stall` | sending stops after a delay, the connection stays open | stall detection on a live session |
| `flap` | every session closes a fixed time after PLAY | reconnect, new epoch, VOD discontinuity |
| `unauthorized` | every DESCRIBE gets 401; set at runtime, live sessions are closed so clients reconnect into it | `ErrAuth`, password rotation |
| `burst` | on PLAY, replay from the last IDR at least N seconds old | join burst, settling (9.5) |
| `rtp_reset` | once per session, RTP time jumps back one hour and sequence numbers jump by 20000 | epoch reset inside a session |
| `ntp_jump` | once per session, the sender-report clock steps, with an explicit SR | NTP rejection (9.3) |

`cmd/nvr-camsim` serves a set of these cameras, one RTSP server per camera and one path per quality, for the local stack. It has a loopback-only control API for injecting faults at runtime. It also renders the seed SQL and a manifest, so the database and the simulated cameras agree on ids.

The local stack runs camsim, throwaway TimescaleDB and NATS containers, and the NVR on the host. Ids are deterministic v8 UUIDs in separate namespaces for `CameraID` and `CameraSourceID`, so a mix-up cannot pass by accident. Privacy is on by default.

### 14.2 Real clients as oracles

The `media` test tier judges the system's output with independent implementations:

- **ffprobe** counts decoded frames (`nb_read_frames`) in recorded segments and from the RTSP server.
- **GStreamer `rtspsrc`**, the element inside nvurisrcbin, reads from the Go RTSP server, including across camera flaps.
- **Headless Chrome** plays the live fMP4 through MSE.
- **ffmpeg** is the reference for durations, start times and exact frames.
- **The TypeScript path** is the reference for the ring.

The tiers:

- **unit:** `go test ./...`, no Docker.
- **media:** `-tags media`, needs ffmpeg, GStreamer and Chrome.
- **integration:** `-tags integration`, against Postgres and NATS.

Tag-gated tests fail rather than skip when `CI=true`. A CI grader rejects zero-test runs and required skips. Until this month, though, no CI job ran the media tier of `pkg/recorder` and `pkg/ingest` at all. Every timing test, including `TestFaultJoinBurst`, ran only on developer machines. A CI step that runs the media tier is being added. It has a floor on the number of passing tests and a list of tests that must have run.

### 14.3 The contract suite

The TypeScript NVR is the specification: every consumer was written against it. The contract suite drives a running TypeScript or Go NVR and writes one JSONL exchange per response, keyed by a stable case id. A validator then checks each exchange:

- the route is registered;
- the status is in the contract;
- the body parses under the consumer's own zod schema;
- instants are formatted the way JavaScript formats them;
- no keys were stripped;
- every route is covered.

A differ joins the two logs by case id. JSON is compared after masking volatile fields; playlists and media bytes are compared byte for byte.

Deliberate differences go into a `KNOWN_DIVERGENCES` list. Each must *still* differ in the declared way, or the diff fails, so a divergence cannot quietly turn into an accident. Examples:

- invalid quality answered 400 instead of 500;
- Go enforcing the raw-access 403 the TypeScript side lacked;
- the go2rtc URL replaced by the Go RTSP URL.

### 14.4 Proving a test tests something

A test that names a guard is checked against that guard's deletion. A script copies the tree to a scratch directory, deletes the guard and runs the named test, which must fail.

The settle fix had seven such mutations, and all were caught. The recorder's restart-versus-quarantine rules had four.

The rule exists because comments like "fails without X" were wrong six times in one branch. The causes were:

- a call-count assertion that a once-latch satisfies either way;
- a negative-only assertion that an empty value satisfies;
- expectations computed with the module under test;
- a guard made redundant by a second guard added in the same commit.

## 15. Failure catalogue

| Failure | Symptom | Cause | Fix or rule |
| --- | --- | --- | --- |
| DTS after PTS at join | One camera of four quarantined, `mux: bad timestamps` | DTS extractor learns reorder depth late (`I0 P2 B1`) | Drop to the next random-access AU, keep the extractor |
| Fixtures hid the DTS bug | All tests green | `testsrc2` B-frames always paired | Vary fixtures; test against real-camera patterns |
| Join-burst start error | First segment 165–643 ms off | Boundary fixed while the anchor was still converging; 500 ppm clamp cannot absorb it | Wait for the timeline to settle before an epoch's first boundary |
| Recorder quarantined on any error | One bad AU stopped recording until restart | Error handling did not separate writer faults from data faults | Restart with backoff; quarantine only on writer deadline or abandonment |
| LiveFMP4 overlap | Non-monotonic DTS after an overflow | New run started before the cut GOP's end | Conservative end estimate; a run never starts before the previous one ended |
| RASL at file start | 99 of 100 frames decoded, silently | Open-GOP CRA start | D15: drop RASL after a file-initial CRA, at every file start |
| go2rtc credentials | "wrong user/pass" | Percent-encoded `:`/`@` mishandled | Dial cameras directly; RFC 3986 userinfo |
| WHATWG URL spelling | `url.Parse` fails | `%` left literal in userinfo | `url.UserPassword` |
| Lost sender reports | No camera NTP | Relay drops RTCP SR | Direct ingest |
| Hidden flaps | `running` with 100–117 of 150 frames | Relay reconnects silently | Per-session epochs; health from indexed segments |
| Upper-case UUID | Second camera session | Postgres compares case-insensitively | Canonical keys only, refused before resolving |
| Source edit kicked every quality, removal kicked nothing | Needless reconnects, stale sessions | Refresh was coarse | `Revalidate` per target |
| Subnet outage behind go2rtc | 12 of 15 sources never retried, 4 h without analysis, `/health` green | Relay retry state invisible | Supervisor per session, typed errors, honest health |
| 40 s GOP camera | Killed at 30 s, looped forever | Fixed stall timeout | Stall window scales with the largest observed segment |
| Wedged process | Ignored SIGTERM | Uninterruptible I/O | Single-goroutine writer with deadline and abandonment |
| Two writers, one directory | Interleaved files | State flag reset on stop/start | Directory registry plus advisory lock |
| Third `is_connected` writer | Unreachable cameras Online/REC | API wrote observation columns | Only observers write; lint rule |
| DeepStream watchdog off | Source never reconnected | `init-rtsp-reconnect-interval` defaults to 0 | Set both intervals |
| GLib deadlock on RTSP reset | Pipeline frozen | Teardown order in nvurisrcbin | Patched teardown from the sink end; native test must fail on stock |
| REST 200 on failed removal | Every removal silently failed | Upstream bug | Verify effects, not status codes |
| Fixed-lens zoom | Zoom buttons that do nothing | Firmware advertises zoom | Tri-state capability, retraction on measured evidence |
| Bridge-address port mapping | Recorder workers broken fleet-wide while the Docker bridge was down | Docker port mapping on the bridge-gateway address fails silently | Bind loopback or all interfaces, never the bridge address; filter peers at accept |

## 16. Working rules

These rules apply to any streaming camera system, not just this one.

1. **Open each camera stream once and share it in-process.** Cameras limit sessions, and every extra session is another place for timing and failures to diverge.
2. **Never let one consumer block another.** Bounded queues per consumer; an overflowing consumer drops to the next keyframe and is told in-band how much it lost.
3. **Deliver whole GOPs or nothing.** Every consumer's output must decode from its first byte; start everything at a random-access picture with complete parameter sets.
4. **Absorb parameter sets in-band.** The SDP is a hint. Cameras change resolution mid-stream.
5. **Reconstruct DTS, and handle the reorderings it gets wrong.** Containers fail long after ingest when PTS < DTS.
6. **Unwrap RTP time to 64 bits and detect clock resets.** A reset is a new epoch, not an error.
7. **Anchor time on the lower envelope of arrival; trust camera NTP only when arrival agrees.** Record all the evidence beside the result, so a wrong time can be explained later.
8. **Chain segment boundaries.** `end(n) == start(n+1)` by construction, corrections clamped to a few hundred ppm, and do not fix the first boundary of an epoch until the clock has settled.
9. **Classify failures by type, never by message text, and scrub every URL** before it leaves the process.
10. **Set the transport explicitly.** A silent UDP→TCP fallback hides the real network.
11. **Green means recorded video in the index.** Not a live process, not a config bit, not "the session is open".
12. **Write files under a hidden name and rename; put every write behind a deadline** and abandon a writer that misses it — a dead mount blocks, it does not fail.
13. **Delete only what the index names, under the root you own.** A missing verdict is not an absence.
14. **Fail closed on privacy.** Any doubt — error, timeout, unknown camera — means privacy on; serve the redacted companion, ask the client to retry, or refuse.
15. **Keep C decoders in a separate process.** Bounded jobs, minimal environment, kill on deadline; the recorder must survive any bitstream.
16. **Treat camera capabilities as claims.** Store "unknown" as its own state; demote only on measured evidence.
17. **Test with a camera built to misbehave, judge with independent clients, and run the media tier in CI.** A timing test that runs only on a laptop is not a guard.

## 17. Limitations and open questions

- **Real hardware.** The Go NVR is not yet validated on real cameras at scale, on a DeepStream host with nvurisrcbin, or against camera session limits. macOS loopback absorbs 350–550 kB per connection, which slows eviction tests.
- **Unverified paths.** UDP ingest, the 13.3-hour RTP wrap and the 26.5-hour MPEG-TS wrap over real uptime, and ONVIF and vendor URL quirks are all unverified.
- **Not ported.** Vendor drivers, ONVIF discovery and PTZ remain TypeScript-only. Hosts with vendor NVR systems cannot cut over.
- **Packet loss** is not reported to consumers as a gap, and skip-to-IDR after loss is not tested end to end.
- **`OnAuthFailure`** is not wired in production. A rotated password shows as `auth` in status but raises no alert.
- **Metrics.** Recorder metrics are not exported to Prometheus.
- **Decode workers** lack `Pdeathsig`. A worker stuck in libav outlives a dead core.
- **Clip durations.** Rows drift about 16 ppm and open-GOP clips come out 40 ms long, so vision rejects multi-segment clips from the recordings branch of materialize.
- **Second writer.** When a second writer is active, a Go segment whose start collides with a TypeScript row is silently not indexed.
- **Stale comments.** Some comments in `pkg/ingest` (`session.go`, `policy.go`) still describe go2rtc as present.
- **Planned refactors.** The next phase plans three:
  - a stream lease type that replaces string-keyed sources in `pkg/recorder`;
  - a bounded segment reader that unifies hung-read accounting across playback and housekeeping;
  - a shared `pkg/backoff`, since there are four backoff ladders today: ingest, recorder restart, decode respawn and ring retry.

## Related notes

- [[01 - Index-Governed Reclamation - A Bounded Store Deletes Only What Its Index Names Under Its Root]] — the housekeeping pattern of chapter 11, written as a design pattern.
- [[PROJ - Screencast Studio - GStreamer Migration and Media Runtime Intern Guide]] — another media pipeline in the vault, built on GStreamer rather than an in-process core.

## Repository map

| Path | Contents |
| --- | --- |
| `services/nvr-go/pkg/media` | `AU`, `ParamSet`, codec helpers, MSE codec strings |
| `services/nvr-go/pkg/ingest` | RTSP session, assembler, supervisor, typed errors, transport/TLS policy |
| `services/nvr-go/pkg/timeline` | RTP unwrapping, reset detection, lower-envelope anchor, NTP trust, chain, settling |
| `services/nvr-go/pkg/bus` | Fan-out with per-consumer queues, in-band gaps, GOP replay |
| `services/nvr-go/pkg/recorder` | Segmenting, pending-file writes, async writer, health, restart loop |
| `services/nvr-go/pkg/mux` | MPEG-TS, fMP4, live fMP4, progressive MP4 clips, TS demux, RASL filter |
| `services/nvr-go/pkg/testcam` | Fake RTSP camera with fault modes and ground-truth capture times |
| `services/nvr-go/internal/camhub` | Shared camera sessions, leases, linger, revalidation |
| `services/nvr-go/internal/recmgr` | Which streams record, reconciliation, status writer, direct-ingest policy |
| `services/nvr-go/internal/rtspserver` | RTSP re-serve for stream-engine |
| `services/nvr-go/internal/live` | Live fMP4 hub for browsers |
| `services/nvr-go/internal/ring` | In-memory GOP ring and clip materialization |
| `services/nvr-go/internal/playback` | Concat, VOD/live HLS, export, redacted companions |
| `services/nvr-go/internal/decode`, `cmd/playback-decode` | Decode worker pool and the libav worker |
| `services/nvr-go/internal/privacy`, `internal/redaction` | Privacy gate and redaction client |
| `services/nvr-go/internal/housekeeping` | Disk eviction, root guard, orphan sweep |
| `services/nvr-go/internal/layout` | Storage path grammar (mirror of `shared/storage/layout.ts`) |
| `services/nvr-go/cmd/nvr-camsim`, `test/localstack` | Camera simulator and local stack |
| `services/nvr-go/test/contract`, `test/crosslock`, `test/pkgdeps` | Contract suite, cross-language lock test, package layering |
| `services/stream-engine` | DeepStream consumer, patched nvurisrcbin |
| `docs/vision/recorder-health.md`, `docs/vision/stream-engine.md`, `docs/vision/cameras.md` | Health contract, analytics pipeline, camera identity |
