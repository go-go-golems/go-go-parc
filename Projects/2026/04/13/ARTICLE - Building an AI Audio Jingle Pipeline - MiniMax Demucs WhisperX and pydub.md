---
title: Building an AI Audio Jingle Pipeline - MiniMax, Demucs, WhisperX, and pydub
aliases:
  - AI Audio Pipeline Pattern
  - ML Audio Processing Pipeline
  - Building a Jingle Extractor
tags:
  - article
  - audio-processing
  - machine-learning
  - music-generation
  - python
  - pattern
  - ml-audio
  - demucs
  - whisperx
  - pydub
status: active
type: article
created: 2026-04-13
repo: /home/manuel/code/wesen/2026-04-13--jingle-extraction
---

# Building an AI Audio Jingle Pipeline: MiniMax, Demucs, WhisperX, and pydub

A deep technical exploration of combining multiple ML audio models into a cohesive production pipeline. This article explains how to integrate AI music generation, neural stem separation, and speech recognition with word-level alignment to automatically extract short audio clips from music. Based on the Jingle Extractor project, tested across multiple genres including death metal and thrash metal.

> [!summary]
> This pattern combines four technologies into a production audio pipeline:
> 1. **MiniMax** for AI music generation from text prompts
> 2. **Demucs** for neural stem separation (vocals vs instrumental)
> 3. **WhisperX** for word-level transcription with alignment
> 4. **librosa + pydub** for beat detection, clip mining, and export
> 
> The result is a system that can generate music, analyze it, and extract production-ready jingles automatically.

## Why this pattern exists

Content creators need short audio clips constantly—stings, transitions, underscoring, emphasis hits. Traditional workflows involve:

1. Searching through music libraries
2. Manually cutting clips in a DAW
3. Trying to find beats and avoiding vocal clashes
4. Exporting with proper fades

This is tedious and slow. The ML audio pipeline automates this by:

- Generating original music from descriptions
- Separating stems so you always have instrumental beds
- Detecting vocals and transcribing them
- Finding musically coherent moments algorithmically
- Exporting ready-to-use clips

## When to use this pattern

### Good fit when:

- You need many short clips (2-5 seconds) from longer music
- You want instrumental beds for under-dialogue work
- You're working across genres and need consistent processing
- You want to generate original music rather than license existing tracks
- You need vocal isolation for remixing or analysis

### Less good when:

- You need real-time processing (this pipeline is batch/offline)
- CPU time is expensive (WhisperX is slow on CPU)
- You need broadcast-quality separation (Demucs is good but not perfect)
- You need clips longer than 5 seconds (algorithm optimized for short stings)

## Core mental model

The pipeline treats audio production as a **three-stage refinement process**:

```mermaid
flowchart LR
    A[Raw Audio] -->|Separate| B[Stems]
    B -->|Analyze| C[Features]
    C -->|Mine| D[Clips]
```

1. **Separation** breaks the audio into parallel streams (vocals, instrumental)
2. **Analysis** extracts semantic and rhythmic features (transcription, beats, energy)
3. **Mining** uses those features to select optimal time ranges
4. **Export** renders the selections with production polish (fades, format)

The insight is that ML models give us **semantic information** (what's being said, where the beats are) that traditional audio editing tools don't have. By combining multiple models, we get a rich feature set for intelligent clip selection.

## Architecture pattern

### The Multi-Model Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT (Prompt or File)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  GENERATION LAYER                                           │
│  MiniMax music-2.6 → 130s MP3                                │
│  - Text-to-music                                            │
│  - Optional lyrics with [Verse]/[Chorus] tags              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  SEPARATION LAYER                                           │
│  Demucs htdemucs → vocals.mp3 + no_vocals.mp3              │
│  - Neural source separation                                 │
│  - Two-stems mode (vocals vs rest)                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────┴───────┐
                    ↓               ↓
        ┌─────────────────┐ ┌─────────────────┐
        │ VOCAL STREAM    │ │ INST STREAM     │
        │ WhisperX        │ │ librosa         │
        │ - Transcription │ │ - Beat track    │
        │ - Word align    │ │ - Onset detect  │
        │ - VAD           │ │ - RMS energy    │
        └─────────────────┘ └─────────────────┘
                    ↓               ↓
                    └───────┬───────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  MINING LAYER                                               │
│  - Score candidates using combined features                │
│  - Select non-overlapping high-scorers                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  EXPORT LAYER                                               │
│  pydub → vocal/inst/mixed MP3s with fades                   │
└─────────────────────────────────────────────────────────────┘
```

### Model Responsibilities

| Model | Input | Output | Value for Mining |
|-------|-------|--------|------------------|
| MiniMax | Text prompt | 130s MP3 | Original source material |
| Demucs | Mixed audio | 2 stems | Isolated streams for independent processing |
| WhisperX | Vocals stem | JSON with word timestamps | **When** vocals occur, what words |
| librosa | Any audio | Beat times, onsets, tempo, energy | **Where** musically coherent moments are |

### Key Integration Points

**1. Time Alignment**
All models operate on the same timeline. Demucs outputs stems that are sample-aligned with input. WhisperX and librosa both output timestamps in seconds. This allows correlation: "the word 'YOW!' happens at 17.25s, which is just after beat 42 at 17.1s."

**2. Stem-Driven Analysis**
By separating first, we can:
- Run WhisperX only on vocals (cleaner input)
- Mine clips from no_vocals (always have instrumental option)
- Create vocal-only, inst-only, and mixed variants

**3. Feature Fusion for Scoring**
The mining algorithm combines:
- librosa: "beat at 17.1s, high energy, onset at 17.0s"
- WhisperX: "vocal from 17.2s-18.0s"
- Result: "avoid 17.0s-18.0s for instrumental clips (vocals there), but that onset at 17.0s is a great clip start"

## Implementation pattern

### The Mining Algorithm

This is the core intelligence of the pipeline. Pseudocode:

```python
def mine_candidates(audio_path, min_len=2.0, max_len=5.0, top_n=12):
    # 1. Analyze rhythm
    features = analyze_rhythm(audio_path)
    beat_times = features['beat_times']
    onset_times = features['onset_times']
    rms = features['rms_energy']
    
    candidates = []
    
    # 2. Try windows starting at each beat
    for start_beat in beat_times:
        for duration in [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
            end = start_beat + duration
            
            # 3. Calculate score components
            avg_energy = mean_rms(rms, start_beat, end)
            start_onset_dist = distance_to_nearest(onset_times, start_beat)
            end_onset_dist = distance_to_nearest(onset_times, end)
            end_beat_dist = distance_to_nearest(beat_times, end)
            tail_drop = avg_energy - mean_rms(rms, end-0.18, end)
            
            # 4. Weighted scoring
            score = (
                avg_energy * 3.0 +                    # loud is good
                max(0, 0.12 - start_onset_dist) * 6.0 +  # clean attack
                max(0, 0.10 - end_onset_dist) * 4.0 +    # clean ending
                max(0, 0.08 - end_beat_dist) * 3.0 +     # ends on beat
                max(0, tail_drop) * 1.5                  # tail energy drop
            )
            
            candidates.append(Candidate(
                start=start_beat, end=end, 
                duration=duration, score=score
            ))
    
    # 5. Sort and select non-overlapping
    candidates.sort(key=lambda c: c.score, reverse=True)
    
    selected = []
    for cand in candidates:
        if not overlaps_by_50percent(cand, selected):
            selected.append(cand)
        if len(selected) >= top_n:
            break
    
    return selected
```

**Key insight**: The weights (3x, 6x, 4x, 3x, 1.5x) reflect production priorities. Clean attack matters most (6x) because clicks and bad starts ruin clips. Ending on a beat matters (3x) because it feels resolved. Raw energy matters (3x) because quiet clips get lost in mixes.

### Vocal Jingle Extraction Pattern

When you have word-level timestamps, you can extract clips centered on vocal moments:

```python
# Load transcription
transcription = json.load(open('lyrics_aligned.json'))
vocals = AudioSegment.from_file('vocals.mp3')
inst = AudioSegment.from_file('no_vocals.mp3')

for segment in transcription['segments']:
    text = segment['text']
    start = segment['start']
    end = segment['end']
    
    # Add padding for context
    clip_start = max(0, start - 0.5)
    clip_end = min(duration, end + 0.5)
    
    # Extract both stems
    vocal_clip = vocals[clip_start:clip_end]
    inst_clip = inst[clip_start:clip_end]
    
    # Create mixed version
    mixed = inst_clip.overlay(vocal_clip)
    
    # Export all three
    vocal_clip.export(f'vocal_{text}.mp3')
    inst_clip.export(f'inst_{text}.mp3')
    mixed.export(f'mixed_{text}.mp3')  # Ready to use!
```

This gives you **three variants per vocal phrase**, maximizing flexibility:
- Use `vocal_*.mp3` for acapella moments
- Use `inst_*.mp3` for under-dialogue beds
- Use `mixed_*.mp3` for drop-in jingles

## Common failure modes

### Failure: WhisperX timeout on instrumental tracks

**Symptom**: WhisperX runs for minutes then times out on tracks with no speech.

**Cause**: WhisperX's VAD (Voice Activity Detection) finds no speech segments, but the pipeline keeps waiting for alignment.

**Fix**: Add `--skip-transcribe` flag for known instrumental tracks, or detect VAD failure and skip gracefully.

```python
if not args.skip_transcribe:
    try:
        result = whisperx_transcribe(vocals_path)
    except Exception as e:
        print(f"Transcription failed (likely instrumental): {e}")
        result = {'segments': []}  # Empty result
```

### Failure: Demucs progress bar hangs in non-interactive shells

**Symptom**: Demucs subprocess appears to hang even though CPU is working.

**Cause**: Progress bar rendering stalls in non-TTY environments.

**Fix**: Use longer timeouts and don't rely on stdout for progress.

### Failure: MiniMax always outputs 130s regardless of prompt

**Symptom**: Generated tracks are always the same length, not matching desired duration in prompt.

**Cause**: MiniMax music-2.6 model has fixed output duration.

**Workaround**: Accept the 130s output and mine shorter clips from it. For the full pipeline, this is actually fine—you generate once, then extract multiple short clips.

### Failure: Death metal growls don't transcribe

**Symptom**: WhisperX produces garbage or timeout on extreme vocal styles.

**Cause**: Whisper is trained primarily on clean speech, not extreme vocal distortion.

**Fix**: Use `--skip-transcribe` for growled vocals. The beat mining still works fine on the instrumental stem.

## Anti-patterns

### Anti-pattern: Running everything sequentially without caching

```python
# Bad: Re-analyzes the same file every time
for clip in clips:
    features = analyze_rhythm(audio_path)  # Redundant!
    process(clip, features)
```

**Better**: Analyze once, then mine:

```python
# Good: Analyze once, mine many
features = analyze_rhythm(audio_path)
for duration in [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
    candidates = mine_candidates(features, duration)
```

### Anti-pattern: Mining from the full mix instead of stems

```python
# Bad: Mining from mixed audio includes vocal energy
features = analyze_rhythm('mixed_track.mp3')  # Vocals affect energy!
```

**Better**: Mine from no_vocals stem:

```python
# Good: Mining from instrumental only
demucs_split(input_audio, out_dir)
features = analyze_rhythm(stems['no_vocals'])  # Clean energy envelope
```

### Anti-pattern: Using default argparse with `--instrumental`

```python
# Bad: Cannot disable instrumental mode
parser.add_argument("--instrumental", action="store_true", default=True)
# Always True! store_true + default=True is wrong.
```

**Better**: Default to False, allow explicit enable:

```python
# Good: Can enable or disable
parser.add_argument("--instrumental", action="store_true", default=False)
# Default: vocals allowed. Use --instrumental to enable instrumental-only.
```

## Recommended implementation sequence

1. **Start with MiniMax integration** - Get music generation working first. This is the most straightforward API integration.

2. **Add Demucs separation** - Process generated tracks into stems. Verify quality across a few genres.

3. **Add librosa analysis** - Beat detection and energy analysis on the no_vocals stem. Visualize the results to verify accuracy.

4. **Implement basic mining** - Start with simple duration windows, add scoring gradually. Listen to extracted clips to validate quality.

5. **Add WhisperX** - This is the slowest component, add it last. Use `--skip-transcribe` flag for instrumental workflows.

6. **Add vocal jingle extraction** - Only after transcription works well on your target genres.

7. **Add mixed output** - pydub overlay is simple once you have both stems.

## Working rules

> [!important]
> **Rule 1**: Always mine from the `no_vocals` stem for instrumental clips. Vocal energy corrupts the energy envelope analysis.

> [!important]
> **Rule 2**: Expect WhisperX to be slow on CPU. Budget 10-15 minutes per track for the transcription stage.

> [!important]
> **Rule 3**: Test across genres early. What works for pop may not work for metal. The scoring algorithm needs genre-specific tuning.

> [!important]
> **Rule 4**: Keep stems. The separated audio is useful for remixing, not just mining. Don't delete vocals.mp3 after transcription.

> [!important]
> **Rule 5**: Use mixed output for ready-to-use clips, not just separate files. Most users want the full sound, not stems.

## Performance characteristics

Based on the thrash metal test track (55.6s):

| Stage | Time | Notes |
|-------|------|-------|
| MiniMax generation | ~10s | API call + hex decode |
| Demucs separation | ~90s | Includes 80MB model download on first run |
| WhisperX transcription | ~13min | Includes 360MB wav2vec2 download on first run |
| librosa analysis | ~2s | Beat/onset detection |
| Candidate mining | ~6s | Scoring and selection |
| Clip export | ~3s | pydub with fades |
| **Total first run** | ~15min | Includes model downloads |
| **Total subsequent** | ~2min | Models cached |

**Optimization**: Use GPU for WhisperX (10x speedup). Add `--device cuda` when available.

## Real-world application: Thrash metal jingles

To validate this pattern, I generated thrash metal with the prompt:

> "Thrash metal, fast palm-muted riffs, double kick drums, aggressive shouting, 160 BPM, intense energy"

With lyrics:
> [Verse] Speed and power, burning fast / No retreat, until the last
> [Chorus] Thrash attack, no turning back / Metal force, we will not crack

The pipeline produced:

**Detected lyrics** (WhisperX):
- "YOW!" at 17.2s (single word, high confidence 0.93)
- "SPINNIN' POWER!" at 29.8s (aggressive 2-word punch)
- "BURNING FAST!" at 32.9s (4-word phrase)
- "NO RETREAT UNTIL THE LAST!" at 35.8s (5-word dramatic phrase)
- "Stress attack...Metal force..." at 41.2s (longer section)

**Rhythm analysis**:
- Tempo: 166.7 BPM (prompt asked for 160, close!)
- Beats: 150 detected
- Onsets: 319 detected (high energy density)

**Extracted jingles**: 15 total files (5 vocal-only, 5 inst-only, 5 mixed)

The mixed jingles are production-ready and can be dropped directly into video timelines. The 2.2-2.3s clips work as stings, the 4.6s as hooks, and the 10.1s as transition beds.

## Extending the pattern

### Adding GPU support

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"
model = whisperx.load_model("large-v2", device, compute_type=compute_type)
```

### Adding batch processing

```python
for input_file in input_directory.glob("*.mp3"):
    analyze(input_file, out_dir / input_file.stem)
```

### Adding YouTube integration

Use `yt-dlp` to download audio, then process:

```python
subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", youtube_url])
analyze(output_mp3)
```

### Custom scoring weights

```python
parser.add_argument("--energy-weight", type=float, default=3.0)
parser.add_argument("--attack-weight", type=float, default=6.0)
```

## Related notes

- [[PROJ - Jingle Extractor - AI Audio Pipeline]] - Full project documentation
- [[ARTICLE - Self-Contained Go Wasm and JavaScript Browser Applications]] - Related pattern for browser audio
- [[PROJ - Transcription Go - Dagger Nemotron ASR Pipeline]] - Related ASR work

## References

- MiniMax API Docs: https://platform.minimax.io/docs/api-reference/music-generation
- Demucs GitHub: https://github.com/facebookresearch/demucs
- WhisperX GitHub: https://github.com/m-bain/whisperX
- librosa docs: https://librosa.org/doc/latest/index.html
- pydub docs: https://github.com/jiaaro/pydub
