---
title: Jingle Extractor UI Design Guide - Metadata and Features
aliases:
  - Jingle Extractor UI Design
  - UI Metadata Guide
tags:
  - article
  - ui-design
  - audio-processing
  - interface-design
  - metadata
status: active
type: article
created: 2026-04-13
repo: /home/manuel/code/wesen/2026-04-13--jingle-extraction
---

# Jingle Extractor UI Design Guide: Metadata and Features

A comprehensive inventory of all metadata available after track analysis, organized for building a high-quality jingle extraction interface. Based on the thrash metal test track (55.6s, 166.7 BPM) processed through the complete MiniMax → Demucs → WhisperX → librosa pipeline.

> [!summary]
> The pipeline generates **7 categories of metadata** suitable for UI visualization and interaction:
> 1. **Track metadata** (duration, BPM, stems)
> 2. **Rhythm data** (150 beats, 319 onsets, tempo)
> 3. **Transcription** (22 words with timestamps, 5 segments)
> 4. **Energy envelope** (4800 RMS samples over time)
> 5. **Candidates** (5 scored clip suggestions with quality metrics)
> 6. **Word-level confidence** (alignment scores 0.0-1.0)
> 7. **Derived metrics** (attack quality, ending quality, vocal clash detection)

## Complete Metadata Inventory

### 1. Track-Level Metadata

**Basic Properties:**
```json
{
  "input_audio": "path/to/track.mp3",
  "duration_seconds": 55.59,
  "duration_formatted": "0:55.59",
  "sample_rate": 44100,
  "detected_language": "en",
  "language_confidence": 0.76
}
```

**Stems (Separated Audio):**
```json
{
  "stems": {
    "vocals": {
      "path": ".../vocals.mp3",
      "size_bytes": 2223542,
      "size_mb": 2.12,
      "exists": true
    },
    "no_vocals": {
      "path": ".../no_vocals.mp3",
      "size_bytes": 2223542,
      "size_mb": 2.12,
      "exists": true
    }
  }
}
```

**UI Uses:**
- Display track info header
- Show stem availability (vocal/inst toggle buttons)
- Language badge (EN, FR, etc.)
- File size indicators

---

### 2. Rhythm Analysis Metadata (from librosa)

**Tempo & Timing:**
```json
{
  "tempo": {
    "bpm": 166.7,
    "confidence": "high",  // librosa beat tracking
    "category": "fast"     // <60 slow, 60-120 medium, >120 fast
  },
  "timing": {
    "hop_length": 512,
    "hop_duration_ms": 11.6,  // 512/44100 * 1000
    "total_hops": 4800
  }
}
```

**Beat Detection:**
```json
{
  "beats": {
    "count": 150,
    "times": [0.348, 0.708, 1.069, 1.429, ..., 54.789],
    "intervals": [0.360, 0.361, 0.360, ...],  // beat-to-beat
    "mean_interval": 0.371,  // 60/166.7 BPM
    "positions": [1, 2, 3, 4, 1, 2, 3, 4, ...]  // if 4/4 assumed
  }
}
```

**Onset Detection:**
```json
{
  "onsets": {
    "count": 319,
    "times": [0.116, 0.232, 0.348, ...],
    "strengths": [0.15, 0.23, 0.31, ...],  // onset envelope values
    "density": 5.74  // per second average
  }
}
```

**UI Uses:**
- **Timeline markers**: Show beats as vertical lines (major) and onsets as ticks (minor)
- **Tempo display**: "166.7 BPM - Fast Thrash"
- **Beat grid**: Snap selection to beats
- **Onset highlighting**: Show transient points for attack quality

---

### 3. Energy Envelope (RMS Analysis)

**Raw Energy Data:**
```json
{
  "rms": {
    "values": [0.001, 0.002, 0.015, 0.031, ...],  // ~4800 samples
    "time_resolution": 0.0116,  // seconds per sample (hop)
    "statistics": {
      "min": 0.001,
      "max": 0.312,
      "mean": 0.089,
      "median": 0.067,
      "std": 0.076,
      "dynamic_range_db": 49.9  // 20*log10(max/min)
    }
  }
}
```

**Energy Regions (auto-detected):**
```json
{
  "energy_regions": [
    {"type": "low", "start": 0.0, "end": 15.0, "mean_rms": 0.045},
    {"type": "medium", "start": 15.0, "end": 35.0, "mean_rms": 0.112},
    {"type": "high", "start": 35.0, "end": 45.0, "mean_rms": 0.178},
    {"type": "medium", "start": 45.0, "end": 55.6, "mean_rms": 0.095}
  ]
}
```

**UI Uses:**
- **Waveform visualization**: Plot RMS values as area chart
- **Energy coloring**: Low=green, Medium=yellow, High=red background
- **Dynamic range indicator**: "High dynamic range (50dB)"
- **Peak detection**: Mark the loudest moments

---

### 4. Transcription Metadata (from WhisperX)

**Language Detection:**
```json
{
  "language": {
    "code": "en",
    "name": "English",
    "confidence": 0.76,
    "detected_from": "first_30s"
  }
}
```

**Segments (Vocal Phrases):**
```json
{
  "segments": [
    {
      "id": 1,
      "text": "YOW!",
      "start": 17.245,
      "end": 18.006,
      "duration": 0.761,
      "word_count": 1,
      "type": "short_phrase",  // <1s
      "avg_logprob": -0.353,
      "intensity": "high"  // derived from caps/exclamation
    },
    {
      "id": 2,
      "text": "SPINNIN' POWER!",
      "start": 29.834,
      "end": 31.035,
      "duration": 1.201,
      "word_count": 2,
      "type": "phrase",  // 1-3s
      "avg_logprob": -0.353,
      "intensity": "high"
    },
    {
      "id": 4,
      "text": "NO RETREAT UNTIL THE LAST!",
      "start": 35.778,
      "end": 39.421,
      "duration": 3.643,
      "word_count": 5,
      "type": "long_phrase",  // 3-5s
      "avg_logprob": -0.353,
      "intensity": "high"
    },
    {
      "id": 5,
      "text": "Stress attack, no turning back Metal force, we will not crack Crack",
      "start": 41.175,
      "end": 50.244,
      "duration": 9.069,
      "word_count": 12,
      "type": "section",  // >5s
      "avg_logprob": -0.399,
      "intensity": "medium"
    }
  ]
}
```

**Word-Level Data:**
```json
{
  "words": [
    {
      "word": "YOW!",
      "start": 17.245,
      "end": 18.006,
      "duration": 0.761,
      "score": 0.934,  // wav2vec2 alignment confidence
      "confidence_level": "high",  // >0.8
      "in_segment": 1
    },
    {
      "word": "SPINNIN'",
      "start": 29.834,
      "end": 30.314,
      "duration": 0.480,
      "score": 0.373,
      "confidence_level": "low",  // <0.5
      "in_segment": 2
    },
    {
      "word": "POWER!",
      "start": 30.374,
      "end": 31.035,
      "duration": 0.661,
      "score": 0.591,
      "confidence_level": "medium",  // 0.5-0.8
      "in_segment": 2
    }
    // ... 19 more words
  ],
  "confidence_distribution": {
    "high": 16,    // >0.8
    "medium": 4,   // 0.5-0.8
    "low": 2       // <0.5
  }
}
```

**Vocal Coverage:**
```json
{
  "vocals": {
    "total_duration": 19.469,  // sum of all vocal segments
    "coverage_percent": 35.0,   // 19.469/55.59
    "segments": 5,
    "gaps": [
      {"start": 0, "end": 17.245, "duration": 17.245},
      {"start": 18.006, "end": 29.834, "duration": 11.828},
      {"start": 31.035, "end": 32.876, "duration": 1.841},
      {"start": 33.677, "end": 35.778, "duration": 2.101},
      {"start": 39.421, "end": 41.175, "duration": 1.754},
      {"start": 50.244, "end": 55.59, "duration": 5.346}
    ],
    "longest_gap": 17.245  // intro/instrumental section
  }
}
```

**UI Uses:**
- **Lyric display**: Show "YOW!" at 17.2s on timeline
- **Vocal regions**: Color background of timeline where vocals exist
- **Word confidence**: Green=high, Yellow=medium, Red=low
- **Gap highlighting**: Show "Instrumental gap: 17.2s (no vocals)" 
- **Click-to-play**: Click word to preview from that point
- **Phrase navigation**: "Next phrase" / "Previous phrase" buttons

---

### 5. Candidate Mining Metadata

**Generated Candidates:**
```json
{
  "candidates": [
    {
      "rank": 1,
      "start": 39.102,
      "end": 43.102,
      "duration": 4.0,
      "score": 1.792,
      "score_percentile": 100,  // best of 5
      "source": "no_vocals.mp3",
      
      // Score breakdown (for UI quality meters)
      "score_components": {
        "rms_energy": 0.089,      // × 3.0 = 0.267
        "attack_proximity": 0.05,  // distance to onset
        "attack_bonus": 0.07,      // 0.12 - 0.05 = 0.07 × 6.0 = 0.420
        "ending_proximity": 0.03,
        "ending_bonus": 0.09,      // × 4.0 = 0.360
        "beat_alignment": 0.08,
        "beat_bonus": 0.04,        // × 3.0 = 0.120
        "tail_drop": 0.025,        // × 1.5 = 0.038
        // Total: ~1.205 (normalized to 1.792)
      },
      
      // Quality flags
      "quality": {
        "starts_on_beat": false,
        "starts_near_onset": true,   // <0.12s
        "ends_on_beat": true,        // <0.08s
        "ends_near_onset": true,
        "has_energy_drop": true,     // tail_drop > 0
        "rms_above_average": true
      },
      
      // Vocal analysis
      "vocals": {
        "overlap": false,            // no vocals in this range!
        "distance_to_nearest_vocal": 2.1,  // gap to "Stress attack..."
        "context": "clean_instrumental"
      }
    },
    {
      "rank": 2,
      "start": 15.464,
      "end": 17.964,
      "duration": 2.5,
      "score": 1.732,
      "score_percentile": 80,
      // ... similar structure
    }
    // ... 3 more
  ]
}
```

**Candidate Statistics:**
```json
{
  "candidates_summary": {
    "total_generated": 5,
    "duration_range": {"min": 2.5, "max": 4.0},
    "score_range": {"min": 1.71, "max": 1.79, "mean": 1.73},
    "coverage": {
      "total_candidate_time": 17.0,
      "percent_of_track": 30.6
    },
    "non_overlapping": true  // algorithm ensures <50% overlap
  }
}
```

**UI Uses:**
- **Ranked list**: Show #1, #2, #3 with scores
- **Score bars**: Visual meter showing 1.71-1.79 range
- **Quality badges**: "Starts on onset ✓", "Ends on beat ✓"
- **Vocal clash warning**: Red badge if vocals overlap
- **Duration chips**: "2.5s" | "4.0s" filter buttons
- **One-click export**: "Export candidate #1" button

---

### 6. Exported Clips Metadata

**Final Outputs:**
```json
{
  "clips": [
    {
      "filename": "thrash_metal_01_01_4.0s.mp3",
      "path": "out/thrash_analysis/clips/thrash_metal_01_01_4.0s.mp3",
      "size_bytes": 97846,
      "size_kb": 95.6,
      "duration": 4.0,
      "start": 39.102,
      "end": 43.102,
      "format": "mp3",
      "bitrate": 192,
      "sample_rate": 44100,
      "channels": 2,
      "fades": {"in_ms": 8, "out_ms": 18}
    },
    // ... 4 more clips
  ],
  "export_summary": {
    "total_clips": 5,
    "total_size_bytes": 416506,
    "total_size_mb": 0.40,
    "format": "mp3",
    "source": "no_vocals"  // all from instrumental stem
  }
}
```

**UI Uses:**
- **Download buttons**: Show file size (95.6 KB)
- **Preview players**: Inline audio playback
- **Batch download**: "Download all 5 clips (400KB)"
- **Format badge**: "MP3 192kbps"

---

### 7. Derived/Calculated Metrics

#### Time-Based Calculations
```javascript
// For any timestamp t, you can calculate:
{
  "time_context": {
    "time_since_last_beat": 0.15,     // seconds
    "time_to_next_beat": 0.22,        // seconds
    "time_since_last_onset": 0.08,    // good attack if <0.12
    "time_to_next_onset": 0.45,
    "time_since_last_vocal": 2.1,     // clean if >1.0
    "time_to_next_vocal": 5.3,
    "beat_phase": 0.4  // 0.0=beat, 0.5=offbeat
  }
}
```

#### Quality Scores (0-100)
```javascript
{
  "quality_metrics": {
    // Attack quality: how clean is the start?
    "attack_quality": 92,  // 0-100, based on onset proximity
    "attack_calculation": "max(0, (0.12 - onset_distance) / 0.12 * 100)",
    
    // Ending quality: how resolved is the end?
    "ending_quality": 85,  // based on beat + onset proximity
    "ending_calculation": "beat_proximity * 0.6 + onset_proximity * 0.4",
    
    // Energy quality: is it loud enough?
    "energy_quality": 78,  // normalized RMS vs track max
    "energy_calculation": "clip_mean_rms / track_max_rms * 100",
    
    // Overall score (the algorithm's output)
    "overall_score": 91,  // normalized from raw 1.792
    
    // Vocal clash warning
    "vocal_clash": false,
    "vocals_in_clip": [],
    "vocals_nearby": ["Stress attack..."],  // within 2.1s
    
    // Suitability flags
    "suitable_for": ["sting", "transition", "emphasis"],
    "not_suitable_for": ["bed_under_dialogue"]  // has energy spike
  }
}
```

#### Vocal Analysis Derivations
```javascript
{
  "vocal_analysis": {
    "words_per_minute": 23.7,  // 22 words / 55.6s * 60
    "average_word_duration": 0.885,  // 19.469s vocal / 22 words
    "average_confidence": 0.72,  // mean of all word scores
    "vocal_density": "medium",  // <15 low, 15-30 medium, >30 high
    "lyrics_repetition": 0.0,  // no repeated phrases
    "complexity_score": 6.5  // unique words / total words ratio
  }
}
```

---

## UI Feature Recommendations

### 1. Main Timeline Visualization

```
┌──────────────────────────────────────────────────────────────────┐
│  THRASH METAL - 166.7 BPM - EN - 55.6s                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Energy  ▓▓▓▓▓░░░▓▓▓▓▓▓▓▓▓░░░░░▓▓▓▓▓▓▓▓░░░░▓▓▓▓▓▓▓▓▓▓░░░▓▓▓▓  │
│ (RMS)  0s                  20s                 40s          55s │
│        │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │
│ Beats: |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | │
│        · ·   · ·   · ·   · ·   · ·   · ·   · ·   · ·   · ·   · ·│
│ Onsets:                                                       │
│        ╔═══════════════════════════════════════════════════════╗ │
│ Vocals:║  YOW!    SPINNIN'   BURNING   NO RETREAT   Stress  ║ │
│        ║    │         │         │          │         │      ║ │
│        ╚════╧═════════╧═════════╧══════════╧═════════╧══════╝ │
│                                                                  │
│ Candidates:                                                      │
│ [█1] 15.5s-18.0s (2.5s) Score: 87 ✓Attack ✓Ending              │
│ [█2] 39.1s-43.1s (4.0s) Score: 92 ✓Attack ✓Ending ⭐BEST       │
│ [█3] 35.1s-39.1s (4.0s) Score: 91 ✓Attack ✓Ending              │
│ [█4] 45.7s-48.2s (2.5s) Score: 89 ✓Attack ✓Ending              │
│ [█5] 26.0s-30.0s (4.0s) Score: 88 ✓Attack ✓Ending              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Components:**
- **Energy waveform**: RMS values as filled area chart
- **Beat markers**: Vertical lines with numbers (1, 2, 3, 4...)
- **Onset ticks**: Smaller marks below beats
- **Vocal regions**: Colored background bands with lyrics
- **Candidate bars**: Horizontal bars at bottom, width = duration
- **Score badges**: Numeric score + quality icons

### 2. Candidate Detail Panel

When user clicks a candidate:

```
┌─ Candidate #2 (BEST) ──────────────────────────┐
│ Score: 92/100  |  Duration: 4.0s               │
│                                                 │
│ Time: 39.1s → 43.1s                            │
│                                                 │
│ Quality Breakdown:                             │
│ ├─ Attack quality:    95 ████████████████████ │
│ ├─ Ending quality:    88 ████████████████░░ │
│ ├─ Energy quality:    78 █████████████░░░░░ │
│ ├─ Beat alignment:   90 █████████████████░ │
│ └─ Overall:           92 ███████████████████░ │
│                                                 │
│ Context:                                         │
│ ├─ Vocals in clip: None ✓                      │
│ ├─ Nearest vocal: "NO RETREAT..." at 35.8s     │
│ ├─ Distance to vocal: 3.3s (safe gap)           │
│ ├─ Starts near onset: 0.05s ✓                 │
│ └─ Ends on beat: 0.03s ✓                      │
│                                                 │
│ [🔊 Preview] [⬇ Export MP3] [✚ Add to list]  │
└─────────────────────────────────────────────────┘
```

### 3. Smart Filters Panel

```
┌─ Filters ──────────────────────────────────────┐
│                                                 │
│ Duration: [✓] 2.0s  [✓] 2.5s  [✓] 3.0s      │
│           [✓] 3.5s  [✓] 4.0s  [ ] 4.5s      │
│                                                 │
│ Vocals: (○) Any  (●) Instrumental only       │
│          (○) Vocal only  (○) Mixed           │
│                                                 │
│ Min Score: [━━●━━━━] 80+                       │
│                                                 │
│ Energy: [Low──────●───────High]               │
│                                                 │
│ Location: (●) Anywhere                        │
│           ( ) Beginning (first 20s)           │
│           ( ) Middle (20s-40s)                │
│           ( ) End (last 15s)                  │
│                                                 │
│ Quality Requirements:                          │
│ [✓] Must start near beat/onset                │
│ [✓] Must end on beat                          │
│ [ ] Must have energy drop at end              │
│                                                 │
│ [Apply Filters] [Reset]                       │
└─────────────────────────────────────────────────┘
```

### 4. Word-Level Lyric Timeline

```
┌─ Lyrics ───────────────────────────────────────┐
│                                                 │
│ 17.2s ┤ YOW!                    [▶]           │
│        │  ↑ Score: 93%                          │
│        │                                        │
│ 29.8s ┤ SPINNIN'                [▶]           │
│        │ POWER!                                 │
│        │  ↑ Score: 37% / 59%                      │
│        │                                        │
│ 32.9s ┤ BURNING FAST!           [▶]           │
│        │  ↑ Score: 90% / 81%                      │
│        │                                        │
│ 35.8s ┤ NO RETREAT UNTIL THE    [▶]           │
│        │ LAST!                                  │
│        │  ↑ All scores 67-99%                     │
│        │                                        │
│ [Extract vocal jingle] [Extract inst jingle]   │
│ [Extract mixed jingle]                         │
└─────────────────────────────────────────────────┘
```

### 5. Export Queue Panel

```
┌─ Export Queue ─────────────────────────────────┐
│                                                 │
│ Selected Jingles (7):                          │
│ ├─ ☑ Candidate #2 (39.1s, Score 92)          │
│ ├─ ☑ Candidate #3 (35.1s, Score 91)          │
│ ├─ ☑ "YOW!" vocal jingle (17.2s)            │
│ ├─ ☑ "YOW!" mixed jingle (17.2s)            │
│ ├─ ☑ "POWER!" inst jingle (29.8s)          │
│ ├─ ☑ "NO RETREAT" mixed (35.8s)             │
│ └─ ☑ "BURNING FAST" mixed (32.9s)            │
│                                                 │
│ Formats: [MP3 ●] [WAV ○]                      │
│ Bitrate: [192kbps ●] [320kbps ○]             │
│                                                 │
│ [Export 7 clips (approx 670KB)]               │
│                                                 │
│ [Clear Queue] [Save Preset]                   │
└─────────────────────────────────────────────────┘
```

---

## JSON Schema for UI Data API

```json
{
  "track": {
    "id": "thrash_metal_01",
    "path": ".../thrash_metal_01.mp3",
    "duration": 55.59,
    "bpm": 166.7,
    "language": "en"
  },
  
  "timeline": {
    "duration": 55.59,
    "beats": [0.348, 0.708, ...],
    "onsets": [0.116, 0.232, ...],
    "rms": [0.001, 0.002, 0.015, ...]
  },
  
  "vocals": {
    "segments": [
      {"start": 17.245, "end": 18.006, "text": "YOW!", "words": [...]}
    ]
  },
  
  "candidates": [
    {
      "id": 1,
      "start": 39.102,
      "end": 43.102,
      "score": 1.792,
      "quality": {
        "attack": 95,
        "ending": 88,
        "energy": 78
      }
    }
  ],
  
  "clips": [
    {
      "id": "thrash_metal_01_01",
      "path": "...",
      "duration": 4.0,
      "size_kb": 95.6
    }
  ]
}
```

---

## Performance Notes for UI

- **RMS array**: ~4800 values, can be downsampled for display (every 10th value = 480 points)
- **Beat/onset arrays**: 150 + 319 = 469 events, lightweight
- **Transcription**: 22 words, trivial size
- **Audio files**: 2 stems × 2.1MB = 4.2MB, load lazily
- **Candidates**: 5-12 objects, negligible
- **Total JSON size**: ~50KB without audio data

---

## Related Notes

- [[PROJ - Jingle Extractor - AI Audio Pipeline]] - Main project documentation
- [[ARTICLE - Building an AI Audio Jingle Pipeline]] - Technical deep dive
- [[2026-04-13--jingle-extraction]] - Source repository
