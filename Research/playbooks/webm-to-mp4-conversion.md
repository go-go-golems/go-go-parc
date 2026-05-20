---
title: "Webm to MP4 Conversion — How We Do It"
aliases: [webm to mp4, vp8 to h264, screen recording conversion, whatsapp video, ffmpeg webm mp4]
tags: [knowledge-base, tribal, ffmpeg, video-conversion, screen-recording, whatsapp]
status: active
type: knowledge-base
created: 2026-05-20
---

# webm → mp4 Conversion — How We Do It

> [!summary]
> One-liner to convert screen-recording webm (VP8) into a WhatsApp-friendly H.264 mp4. Covers the pitfalls that make "simple" ffmpeg calls produce broken files: bogus frame rates from screen recorders, odd dimensions, B-frame DTS ordering, and player compatibility.

## The command

```bash
ffmpeg -y -i recording.webm \
  -c:v libx264 -preset slow -crf 18 \
  -profile:v high -level 4.0 \
  -pix_fmt yuv420p \
  -bf 0 \
  -vf "crop=trunc(iw/2)*2:trunc(ih/2)*2,fps=25" \
  -video_track_timescale 90000 \
  -movflags +faststart \
  output.mp4
```

This produces a clean, maximum-compatibility mp4 that plays in browsers, WhatsApp, iOS, Android, and any media player.

## What each flag does

| Flag | Why |
|------|-----|
| `-c:v libx264` | H.264/AVC — universally supported codec |
| `-preset slow` | Better compression efficiency (takes longer, worth it) |
| `-crf 18` | Visually lossless quality. Use `0` for true lossless (large files). `23` is default but too soft for screen recordings |
| `-profile:v high` | High profile — better compression than baseline/main |
| `-level 4.0` | Proper H.264 level for ~HD resolution. Prevents "level 6.1" nonsense that breaks mobile decoders |
| `-pix_fmt yuv420p` | Only pixel format every player supports. Some webm sources are already this; explicit avoids surprises |
| `-bf 0` | No B-frames. Eliminates DTS reordering issues that cause non-monotonic timestamps. Maximum player compatibility |
| `-vf "crop=trunc(iw/2)*2:trunc(ih/2)*2"` | H.264 requires even dimensions. Screen recordings often have odd widths/heights (e.g. 1431×1129). This crops 1px off each odd edge |
| `-vf "fps=25"` | Forces constant 25fps. Screen recorders often write bogus `r_frame_rate` (like 1000/1) with VFR timestamps. Without this, ffmpeg duplicates thousands of frames or writes broken container metadata |
| `-video_track_timescale 90000` | Standard MPEG timescale. Prevents `r_frame_rate=2000/1` nonsense in the mp4 container |
| `-movflags +faststart` | Moves moov atom to file start. Required for streaming/WhatsApp — player can start without downloading the whole file |

## The pitfalls

### Pitfall 1: Screen recorders write bogus frame rates

GNOME screen recorder and similar tools produce webm with `r_frame_rate=1000/1` or similar nonsense. The actual frames are VFR with timestamps, but ffmpeg reads the container rate and either:
- **CFR mode** (default): duplicates ~1000 frames per second of video, encoding takes forever and produces garbage
- **VFR mode** (`-fps_mode vfr`): preserves timestamps but writes `r_frame_rate=2000/1` into the mp4, which confuses many players

**Fix**: force a real framerate with `-vf "fps=25"`.

### Pitfall 2: Odd dimensions break H.264

Screen recordings often capture at odd resolutions (1431×1129, 1281×721, etc.). H.264 requires even width and height. ffmpeg with libx264 will error or produce corrupt output on odd dimensions.

**Fix**: `crop=trunc(iw/2)*2:trunc(ih/2)*2` rounds down to even by cropping at most 1px per edge.

### Pitfall 3: B-frames cause non-monotonic DTS

VFR source + B-frame reordering = DTS timestamps that go backwards. Many players (especially hardware decoders and WhatsApp's transcoder) choke on this. You get "non monotonically increasing dts" errors in ffprobe and playback failures.

**Fix**: `-bf 0` disables B-frames. Slight compression loss, but screen recordings barely benefit from B-frames anyway (mostly static content).

### Pitfall 4: Level gets auto-set to nonsense

Without `-level`, libx264 auto-computes level from resolution × framerate. With a bogus 1000fps input, you get level 6.1 (which is for 4K@300fps). Most mobile decoders refuse level 6.1.

**Fix**: `-level 4.0` (covers up to 2048×1024@30fps, fine for typical screen recordings).

### Pitfall 5: No faststart = broken streaming

Without `-movflags +faststart`, the moov atom (metadata/index) is at the end of the file. Players must download the entire file before they can start playing. WhatsApp and browsers need it at the start.

**Fix**: always include `-movflags +faststart`.

## Quality guide

| CRF | Use case | Approx. size for 50s 1080p screen recording |
|-----|----------|----------------------------------------------|
| `0` | True lossless (huge) | ~50 MB+ |
| `18` | Visually lossless (recommended) | ~2.5 MB |
| `23` | Default (soft on text) | ~1.4 MB |
| `28` | Small but noticeably blurry | ~0.8 MB |

For screen recordings with text, CRF 18 is the sweet spot. CRF 23 makes text noticeably soft.

## No scaling

The command preserves the original resolution (only cropping 0-1px for even dimensions). Do not add `-vf scale=...` unless you explicitly want to resize.

## Validation checklist

After converting, verify the output:

```bash
# 1. Check stream metadata — should show h264, proper level, 25/1 fps, no B-frames
ffprobe -v error -show_entries stream=codec_name,profile,level,width,height,r_frame_rate,avg_frame_rate,pix_fmt,has_b_frames -of default=noprint_wrappers=1 output.mp4

# 2. Full decode check — should produce zero output (no errors)
ffmpeg -v error -i output.mp4 -f null -

# 3. Quick browser test — serve and open in Chrome
python3 -m http.server 8899 &
# open http://localhost:8899/output.mp4
```

Expected ffprobe output:
```
codec_name=h264
profile=High
width=1430          # even
height=1128         # even
pix_fmt=yuv420p
level=40            # 4.0
r_frame_rate=25/1   # clean
avg_frame_rate=25/1
has_b_frames=0      # no B-frames
```

## Variations

- **With audio**: add `-c:a aac -b:a 128k` if the source has an audio track
- **Smaller file for chat apps**: increase CRF to `23` or add `-vf scale=iw/2:-2` (half resolution)
- **True lossless**: change to `-crf 0 -preset veryslow` (file will be much larger)
- **Higher FPS**: change `fps=25` to `fps=30` for slightly smoother playback on 60Hz displays
