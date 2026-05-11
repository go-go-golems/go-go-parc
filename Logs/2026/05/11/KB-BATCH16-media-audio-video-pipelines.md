---
title: "KB Batch 16 — Media, Audio, and Video Pipelines"
aliases:
  - KB-BATCH16-media-audio-video-pipelines
  - Batch H Media Audio Video
status: active
type: kb-review
created: 2026-05-11
tags: [knowledge-base, kb-review, media, audio, video, asr, webrtc]
---

# KB Batch 16 — Media, Audio, and Video Pipelines

## Scope

Batch H reviewed the media/audio/video cluster:

1. [[PROJ - Rabbit Hole Podcast Intros - Remotion Video Generation]]
2. [[PROJ - Jingle Extractor - AI Audio Pipeline with MiniMax Demucs WhisperX]]
3. [[PROJ - Transcription Go - Dagger Nemotron ASR Pipeline]]
4. [[PROJ - Transcription Go - Streaming Transcription Architecture and Implementation Report]]
5. [[PROJ - MiroTalk SFU on K3s - Video Realm and WebRTC Deployment]]
6. [[PROJ - Static Apple Music Player - Deep Dive]]
7. [[PROJ - Latent Space Podcast Downloader]]
8. [[PROJ - LibriVox Player]]

## Main conclusion

Batch H did not trigger a new KB entry by threshold, but it opened a strong media-domain candidate set. The strongest emerging On-Ramp is **ASR pipeline architecture** at 3/5, followed by **browser audio playback model** at 2/5. The media cluster is currently broad: Remotion video generation, AI audio clip mining, ASR batch/streaming, WebRTC deployment, static MusicKit playback, RSS/YouTube podcast download, and single-file browser audio playback.

## Written

No new Batch H KB entry was written. The batch mostly produced candidate evidence.

## Updated / reinforced

- [[Tribal/host-mediated-secret-delivery]] — reinforced by Static Apple Music Player's token-vending backend: browser owns playback; Go backend owns the `.p8` private key and short-lived developer-token signing.
- [[On-Ramp/go-cli-with-embedded-spa]] — reinforced by Static Apple Music Player as a small local Go server plus static frontend example.
- [[On-Ramp/oauth-2-oidc-flows]] and [[On-Ramp/vault-on-k3s-with-vso]] — reinforced by MiroTalk's Keycloak/Vault deployment shape.

## Could / should be written later

### ASR pipeline architecture

Status: **3/5 🌐**.

Seen in:

- Jingle Extractor — WhisperX alignment inside a stem-separation / clip-mining pipeline.
- Transcription Go batch — pure-Go conversion, Dagger ASR service, Go-owned outputs.
- Transcription Go streaming — replay, WebSocket sessions, partial/final transcript state, PTS timing.

Likely angle: a newcomer-oriented map of speech/audio pipelines: input conversion, sample rates, chunking, model serving, word alignment, partial vs final state, subtitle segmentation, SQLite output, and validation against reference transcripts.

### Browser audio playback model

Status: **2/5**.

Seen in:

- Static Apple Music Player — MusicKit JS, developer token boundary, user authorization, playback control.
- LibriVox Player — direct `Audio.src`, Archive.org URLs, browser media events, chapter/progress UI.

Likely angle: what the browser media stack owns and what the app must own: source URLs, autoplay policy, metadata events, playback state, credentials/tokens, and error handling.

### WebRTC/SFU deployment mental model

Status: **1/5 🌐**.

Seen in:

- MiroTalk SFU on K3s.

Likely angle: distinguish HTTPS UI/signaling from RTP/RTCP media plane, ICE candidates, announced public IP, RTC port ranges, firewall, and why Ingress alone is not a video deployment.

## New candidates

### Tribal candidates

| Concept | Seen in | Status |
|---|---|---|
| Programmatic media composition as code | Rabbit Hole Podcast Intros | 1/3 |
| Staged ML media pipeline with durable intermediates | Jingle Extractor | 1/3 |
| Beat/transient-scored clip mining | Jingle Extractor | 1/3 |
| ML service as narrow inference engine, Go owns artifacts | Transcription Go batch | 1/3 |
| Dagger host-tunnel lifecycle discipline | Transcription Go batch | 1/3 |
| Pending vs committed transcript state | Transcription Go streaming | 1/3 |
| Replay-driven validation for live media systems | Transcription Go streaming | 1/3 |
| Incoming PTS as authority for streaming timestamps | Transcription Go streaming | 1/3 |
| WebRTC media plane is not HTTPS ingress | MiroTalk SFU | 1/3 |
| Static frontend plus token-vending backend | Static Apple Music Player | 1/3 |
| Discovery ladder for podcast/audio downloads | Latent Space Podcast Downloader | 1/3 |
| Direct browser Audio.src over custom fetch wrappers | LibriVox Player | 1/3 |

### On-Ramp candidates

| Concept | Seen in | Status |
|---|---|---|
| ASR pipeline architecture | Jingle Extractor, Transcription Go batch, Transcription Go streaming | 3/5 🌐 |
| Browser audio playback model | Static Apple Music Player, LibriVox Player | 2/5 |
| WebRTC/SFU deployment mental model | MiroTalk SFU | 1/5 🌐 |
| Podcast RSS enclosure model | Latent Space Podcast Downloader | 1/5 |
| Remotion for code-generated video | Rabbit Hole Podcast Intros | 1/5 🌐 |
| Demucs stem separation | Jingle Extractor | 1/5 |
| WhisperX word-level alignment | Jingle Extractor | 1/5 |
| MusicKit JS / Apple Music developer token model | Static Apple Music Player | 1/5 🌐 |

## Project report updates

Added `## KB reviews` and `## Related KB entries` sections to all eight Batch H project reports. Where existing KB entries were relevant, linked those directly; otherwise linked this review and recorded candidate concepts.

## Index updates

Updated [[00-project-index-repos-and-concepts]] with analysis slots 80–87 and advanced campaign counts to:

- analyzed: 87
- remaining: 80
- Tribal entries: 22
- On-Ramp entries: 19
- Fundamentals: 5

## Notes for future review

If another ASR/transcription project appears, **ASR pipeline architecture** will likely become ready. If another browser media/player project appears, **Browser audio playback model** may become ready soon after. The media cluster is conceptually rich but still too broad to force one umbrella KB entry without losing specificity.
