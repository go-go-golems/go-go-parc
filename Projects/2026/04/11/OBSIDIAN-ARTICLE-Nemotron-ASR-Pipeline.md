---
title: Nemotron ASR Transcript Extraction - Multi-Level Database Pipeline
aliases:
  - Nemotron Transcription Pipeline
  - ASR Word-Level Extraction
  - Multi-Pyramid Transcript Database
tags:
  - article
  - asr
  - nemotron
  - nvidia
  - nemo
  - speech-to-text
  - sqlite
  - python
  - pipeline
  - transcription
  - screen-capture
status: complete
type: article
created: 2026-04-11
repo: /home/manuel/code/wesen/patreon/videos/002-sqrt
video_source: /home/manuel/code/wesen/2026-04-09--screencast-studio/recordings/rabbit-hole-2026-04-10--2/Full Desktop.mov
---

# Nemotron ASR Transcript Extraction - Multi-Level Database Pipeline

A complete pipeline for extracting transcripts from long-form video content using NVIDIA's Nemotron-Speech-Streaming-0.6b ASR model, storing word-level timestamps in SQLite for multi-resolution analysis, and synchronizing screen captures to transcript moments for visual documentation.

> [!summary]
> - Extracted **4,248 words** with precise timestamps from 27.7 minutes of audio using Nemotron-0.6b on CPU
> - Built **multi-level SQLite database** storing: words → chunks → SRT segments with filtering capabilities
> - Developed **word-level timestamp extraction** enabling split-on-keyword SRT generation (e.g., split at "spider", "Newton")
> - Created **screen capture synchronization** system that extracts frames at exact transcript timestamps
> - Generated **HTML analysis reports** combining audio transcripts with visual screen analysis
> - Full pipeline processes audio → words → database → configurable SRT exports → visual documentation

---

## Why This Note Exists

Traditional speech-to-text tools output flat text files or simple SRT captions. This pipeline solves three problems that arise when working with long-form educational content:

1. **Temporal precision**: Need to know exactly when specific words occur (e.g., "Newton" at 760.480s)
2. **Re-segmentation**: Want to restructure subtitles based on content (split on keywords, merge fillers, adjust timing)
3. **Audio-visual sync**: Must correlate transcript moments with screen recordings for documentation

The key insight is treating the transcript as a **queryable database** rather than a static file. By storing word-level timing in SQLite, we can regenerate SRTs with arbitrary segmentation rules, filter out filler words, and join against video frames for visual analysis.

---

## When To Use This Pattern

This pipeline is valuable when:

- Creating documentation from screen recordings where you need to quote exact moments
- Building searchable archives of video content with precise word-level retrieval
- Producing multiple SRT variants (clean version without fillers, short segments for accessibility, keyword-split for navigation)
- Analyzing speech patterns, filler word frequency, or timing distributions
- Synchronizing transcripts with external events (slides, code execution, UI interactions)

Not recommended for:
- Real-time transcription (Nemotron-0.6b on CPU processes ~1x real-time)
- Simple one-off transcriptions where a flat SRT is sufficient
- Content requiring speaker diarization (Nemotron doesn't distinguish speakers)

---

## Core Mental Model

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Audio File    │────▶│   Nemotron   │────▶│   Word-Level    │
│   (WAV/MP3)     │     │   ASR 0.6b   │     │   Timestamps    │
└─────────────────┘     └──────────────┘     └────────┬────────┘
                                                      │
                                                      ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Regenerated   │◀────│   SQLite     │◀────│   SQLite DB     │
│   SRT Files     │     │   Queries    │     │   (words table) │
│   (filtered)    │     └──────────────┘     └─────────────────┘
└─────────────────┘              │                     │
                                  │                     │
                                  ▼                     ▼
                         ┌──────────────┐     ┌─────────────────┐
                         │  FFmpeg      │◀────│  Screen Capture │
                         │  Frame Grab  │     │  Synchronization│
                         └──────────────┘     └─────────────────┘
```

The **Multi-Pyramid** concept:
- **Base layer**: Individual words with start/end times (4,248 entries)
- **Mid layer**: Chunks (grouped words for display, ~196 segments)
- **Top layer**: SRT exports (configurable segmentation for delivery)

Each layer can be filtered, re-segmented, and regenerated without re-running the expensive ASR step.

---

## Architecture

### Data Flow

```mermaid
flowchart TD
    subgraph Input["Input Layer"]
        A[Audio: audio-mix.wav<br/>27.7min, 48kHz stereo] --> B[FFmpeg Conversion<br/>16kHz mono]
        V[Video: Full Desktop.mov<br/>1920x1080] --> F[Frame Extraction<br/>ffmpeg -ss]
    end
    
    subgraph ASR["ASR Processing"]
        B --> C[Nemotron-0.6b<br/>Cache-Aware FastConformer-RNNT]
        C --> D[Word Timestamps<br/>time_stride = 8 * window_stride]
    end
    
    subgraph Database["SQLite Storage"]
        D --> W[words table<br/>id, word, start_time, end_time<br/>is_filler, is_removed]
        W --> CW[chunk_words<br/>mapping table]
        CW --> CH[chunks table<br/>segment groupings]
        W --> SE[srt_exports<br/>export history]
        SE --> SS[srt_segments<br/>per-export segments]
    end
    
    subgraph Output["Output Generation"]
        W --> SRT1[Default SRT<br/>segment_separators=?!,]
        W --> SRT2[Short Segments<br/>max_duration=5s]
        W --> SRT3[Keyword Split<br/>split_on=spider,Newton]
        W --> SRT4[Clean Version<br/>is_removed=1 for fillers]
        F --> IMG[Frame Analysis<br/>HTML reports]
    end
    
    style Database fill:#667eea,stroke:#333,stroke-width:2px,color:#fff
    style ASR fill:#e94560,stroke:#333,stroke-width:2px,color:#fff
```

### Database Schema

```sql
-- Words: atomic units with precise timing
CREATE TABLE words (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    duration REAL GENERATED ALWAYS AS (end_time - start_time) STORED,
    chunk_id INTEGER,
    is_filler BOOLEAN DEFAULT 0,  -- 'um', 'uh', 'like', etc.
    is_removed BOOLEAN DEFAULT 0, -- soft delete for filtering
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chunks: display segments
CREATE TABLE chunks (
    id INTEGER PRIMARY KEY,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    duration REAL GENERATED ALWAYS AS (end_time - start_time) STORED,
    text TEXT NOT NULL,
    word_count INTEGER,
    source_type TEXT DEFAULT 'auto',
    metadata TEXT
);

-- Many-to-many: words ↔ chunks
CREATE TABLE chunk_words (
    chunk_id INTEGER,
    word_id INTEGER,
    position INTEGER,
    PRIMARY KEY (chunk_id, word_id)
);
```

---

## Implementation Details

### Nemotron ASR Configuration

The model uses a **Cache-Aware FastConformer-RNNT** architecture with 600M parameters:

```python
# Model loading and configuration
asr_model = nemo_asr.models.ASRModel.from_pretrained(
    "nvidia/nemotron-speech-streaming-en-0.6b"
)

# Configure for word-level timestamps
decoding_cfg = asr_model.cfg.decoding
with open_dict(decoding_cfg):
    decoding_cfg.preserve_alignments = True
    decoding_cfg.compute_timestamps = True
    decoding_cfg.segment_separators = []  # Disable auto-segmentation
    decoding_cfg.word_separator = " "
    asr_model.change_decoding_strategy(decoding_cfg)

# Time conversion: model outputs frame indices
time_stride = 8 * asr_model.cfg.preprocessor.window_stride
# Each frame = 80ms (8 * 10ms window_stride)
word_start = frame_start * time_stride
```

**Why segment_separators=[]?**

By disabling auto-segmentation, we get raw word timestamps without the model injecting punctuation-based boundaries. This gives us maximum flexibility to re-segment later based on our own rules.

### Chunked Processing for Long Audio

Processing 27.7 minutes on CPU risks memory exhaustion. Solution: 60-second overlapping chunks:

```python
def process_long_audio(audio_path, chunk_size=60):
    """Process audio in chunks to stay within memory limits"""
    info = sf.info(audio_path)
    duration = info.duration
    all_words = []
    
    for start in range(0, int(duration), chunk_size):
        end = min(start + chunk_size + 2, duration)  # +2s overlap
        
        # Extract chunk
        ffmpeg -ss start -t (end-start) -i input.wav chunk.wav
        
        # Transcribe
        hypotheses = asr_model.transcribe([chunk_file], 
                                         return_hypotheses=True, 
                                         batch_size=1)
        
        # Adjust timestamps for chunk offset
        for word in extract_words(hypotheses):
            word['start'] += start
            word['end'] += start
            all_words.append(word)
    
    return all_words
```

**Overlap handling**: The 2-second overlap prevents word boundaries from being cut off at chunk edges. Words are deduplicated naturally by their sequential position in the database.

### Word-Level Timestamp Extraction

Nemotron provides timestamps at the frame level. We convert these to seconds:

```python
def extract_word_timestamps(hypothesis, time_stride, chunk_offset=0):
    """Extract word-level timestamps from ASR hypothesis"""
    words = []
    
    if 'word' in hypothesis.timestamp:
        # Direct word timestamps (preferred)
        for stamp in hypothesis.timestamp['word']:
            word = stamp.get('word', '') or stamp.get('char', '')
            start = stamp.get('start_offset', 0) * time_stride + chunk_offset
            end = stamp.get('end_offset', 0) * time_stride + chunk_offset
            words.append({'word': word, 'start': start, 'end': end})
    
    elif 'char' in hypothesis.timestamp:
        # Character timestamps - group into words
        chars = []
        for stamp in hypothesis.timestamp['char']:
            char = stamp.get('char', '')
            start = stamp.get('start_offset', 0) * time_stride + chunk_offset
            end = stamp.get('end_offset', 0) * time_stride + chunk_offset
            chars.append((char, start, end))
        
        # Group by spaces
        current_word = []
        word_start = None
        for char, start, end in chars:
            if char == ' ':
                if current_word:
                    word = ''.join([c[0] for c in current_word])
                    words.append({
                        'word': word,
                        'start': current_word[0][1],
                        'end': current_word[-1][2]
                    })
                    current_word = []
            else:
                current_word.append((char, start, end))
        
        # Handle final word
        if current_word:
            word = ''.join([c[0] for c in current_word])
            words.append({
                'word': word,
                'start': current_word[0][1],
                'end': current_word[-1][2]
            })
    
    return words
```

### Filler Word Detection

Identifying removable filler words at ingestion time:

```python
FILLER_WORDS = {'um', 'uh', 'er', 'ah', 'like', 'you know', 'sort of', 'kind of'}

def classify_filler(word):
    """Check if word is a filler/pause word"""
    normalized = word.lower().strip('.,!?')
    return normalized in FILLER_WORDS
```

**Results**: 173 filler words detected in 4,248 total (4.1% of speech):
- `like`: 87 occurrences
- `um`: 42 occurrences  
- `uh`: 36 occurrences

### SRT Segmentation Strategies

The database enables multiple export strategies:

#### Strategy 1: Punctuation-Based (Default)

```python
def create_punctuation_segments(words, max_duration=15.0):
    """Split on sentence-ending punctuation"""
    segments = []
    current = []
    chunk_start = None
    
    for word_info in words:
        if not current:
            chunk_start = word_info['start']
        
        current.append(word_info['word'])
        
        # Split on punctuation
        if any(word_info['word'].endswith(p) for p in ['.', '?', '!']):
            segments.append({
                'start': chunk_start,
                'end': word_info['end'],
                'text': ' '.join(current)
            })
            current = []
    
    return segments
```

#### Strategy 2: Keyword-Based (Split on Target Words)

```python
def create_keyword_segments(words, split_words, max_chars=100):
    """Create new segment after each target word"""
    segments = []
    current = []
    chunk_start = None
    
    for word_info in words:
        if not current:
            chunk_start = word_info['start']
        
        current.append(word_info['word'])
        
        # Split on target word
        should_split = word_info['word'].lower() in [w.lower() for w in split_words]
        
        # Also split on size constraints
        text = ' '.join(current)
        if len(text) > max_chars or (word_info['end'] - chunk_start) > 15.0:
            should_split = True
        
        if should_split and current:
            segments.append({
                'start': chunk_start,
                'end': word_info['end'],
                'text': ' '.join(current)
            })
            current = []
            chunk_start = None
    
    return segments
```

**Example**: Splitting on `"spider"` at 8.0s creates:
- Segment 1: "Welcome back to the Go Go Golems lab fuck spider" (2.240s - 8.400s)
- Segment 2: "welcome back to the welcome back to the Go Go Golems lab..." (9.040s+)

### Screen Capture Synchronization

Extracting video frames at exact transcript timestamps:

```python
VIDEO = "rabbit-hole-2026-04-10--2/Full Desktop.mov"

def extract_frame_at_timestamp(video_path, timestamp_seconds, output_file):
    """Extract single frame at exact transcript time"""
    cmd = [
        'ffmpeg', '-y', 
        '-ss', str(timestamp_seconds),  # Seek to exact time
        '-i', video_path,
        '-vframes', '1',                 # Extract 1 frame
        '-q:v', '2',                     # High quality
        output_file
    ]
    subprocess.run(cmd, capture_output=True)
```

**Analysis workflow**:
1. Query database for word (e.g., "Newton" at 760.480s)
2. Extract frames at -10s, -5s, 0s, +5s, +10s for context
3. Run AI image analysis on extracted frames
4. Generate HTML report combining transcript + visual analysis

### Regeneration After Filtering

The key benefit of the database approach: edit the transcript without re-running ASR:

```python
# Remove all fillers
db.execute("UPDATE words SET is_removed = 1 WHERE is_filler = 1")
removed = db.cursor.rowcount  # 173 words marked

# Regenerate chunks excluding removed words
db.regenerate_chunks()

# Export new SRT
db.export_srt("clean_no_fillers.srt", include_removed=False)
```

---

## Files and Artifacts

### Pipeline Scripts

| File | Purpose |
|------|---------|
| `transcribe_to_srt.py` | Initial transcription script (word-level extraction) |
| `transcript_db.py` | Database initialization and management |
| `word_level_srt.py` | Word-level timestamp extraction with keyword splitting |
| `query_transcript.py` | Query tool and custom SRT export |
| `srt_config_example.py` | Configuration examples for SRT generation |

### Generated Outputs

| File | Description |
|------|-------------|
| `audio_transcript.db` | SQLite database (792KB, 4,248 words, 196 chunks) |
| `audio-mix.srt` | Default SRT (139 segments, sentence-based) |
| `audio-mix_word_split.srt` | Keyword-split SRT (150 segments) |
| `no_fillers.srt` | Clean version with 173 fillers removed (192 segments) |
| `short_segments.srt` | Max 5s duration (303 segments) |
| `newton_algorithm_analysis.html` | HTML report on Newton algorithm section |
| `interactive_playbook_analysis.html` | HTML report on visualization sections |

### Frame Extracted Directories

- `screen_grabs/`: 5 frames around Newton algorithm (750s-770s)
- `playbook_frames/`: 9 frames around interactive playbook moments (461s, 1051s, 1058s, 1064s, 1080s, 1100s, 1202s, 1473s)

---

## Common Failure Modes

### Memory Exhaustion on Long Audio

**Problem**: Processing full 27.7min audio at once causes OOM kill on CPU

**Solution**: Chunked processing with 60s windows and 2s overlap

```python
# Anti-pattern: Don't do this for long audio
hypotheses = asr_model.transcribe(["27min_audio.wav"])  # OOM risk

# Correct: Process in chunks
for chunk in split_audio(audio, chunk_size=60):
    hypotheses = asr_model.transcribe([chunk])
```

### Timestamp Drift at Chunk Boundaries

**Problem**: Without overlap, words at chunk edges get cut off or mis-timed

**Solution**: 2-second overlap between chunks, deduplication by word sequence

### Missing Word-Level Timestamps

**Problem**: Model only provides segment timestamps, not individual words

**Solution**: Check for `word` key in `hypothesis.timestamp`, fall back to `char` grouping if needed

### Filler Words in Final Output

**Problem**: SRT files include "um", "uh", "like" which clutter reading

**Solution**: Database soft-delete (`is_removed`) lets you regenerate without re-transcribing

---

## Recommended Implementation Sequence

For someone reproducing this pipeline on a new video:

1. **Prepare audio** (5 min)
   ```bash
   ffmpeg -i input.mp4 -ar 16000 -ac 1 -c:a pcm_s16le audio_16k_mono.wav
   ```

2. **Install dependencies** (10 min)
   ```bash
   pip install nemo_toolkit[asr] soundfile
   ```

3. **Run initial transcription** (30-60 min for 30min audio on CPU)
   ```python
   python transcript_db.py  # Creates audio_transcript.db
   ```

4. **Query and explore** (5 min)
   ```python
   python query_transcript.py --cli
   > search algorithm
   > fillers
   ```

5. **Generate custom SRTs** (instant)
   ```python
   db.export_srt("clean.srt", exclude_words=["um", "uh", "like"])
   ```

6. **Extract screen frames** (5 min)
   ```bash
   ffmpeg -ss 760.480 -i video.mov -vframes 1 frame.jpg
   ```

7. **Create HTML reports** (10 min)
   - Copy template from `newton_algorithm_analysis.html`
   - Substitute frames and transcript context

---

## Working Rules

1. **Always use word-level timestamps** for maximum flexibility
2. **Store in SQLite immediately** - don't work with flat files
3. **Mark fillers at ingestion** - easier than detecting later
4. **Use soft deletes** (`is_removed`) rather than hard deletes - preserves ability to regenerate
5. **Extract video frames from database timestamps** - ensures exact sync
6. **Create dated directories for frames** - prevents confusion on multiple runs

---

## Related Notes

- [[PROJ - Rabbit Hole Square Root]] - The parent video project
- [[ARTICLE - FFmpeg Video Processing]] - Frame extraction techniques
- [[ARTICLE - SQLite for Media Projects]] - Database patterns for AV workflows
- [[NVIDIA NeMo Documentation]] - External: https://docs.nvidia.com/nemo/

---

## Metrics and Statistics

| Metric | Value |
|--------|-------|
| Audio duration | 27.7 minutes (1664.75s) |
| Words extracted | 4,248 |
| Unique words | ~1,200 |
| Filler words | 173 (4.1%) |
| Avg word duration | 390ms |
| Database size | 792 KB |
| ASR processing time | ~25 minutes (CPU) |
| Frame extraction time | <1 second per frame |

---

## Command Reference

### Database Queries

```sql
-- Find specific word with context
SELECT id, word, start_time, 
       (SELECT GROUP_CONCAT(word, ' ') 
        FROM words w2 
        WHERE w2.id BETWEEN w1.id-5 AND w1.id+5) as context
FROM words w1
WHERE word = 'Newton';

-- List all filler words with counts
SELECT word, COUNT(*) as count 
FROM words 
WHERE is_filler = 1 
GROUP BY LOWER(word) 
ORDER BY count DESC;

-- Export words in time range
SELECT word, start_time, end_time 
FROM words 
WHERE start_time BETWEEN 750 AND 770 
  AND is_removed = 0
ORDER BY start_time;
```

### FFmpeg Frame Extraction

```bash
# Extract at exact timestamp
ffmpeg -ss 760.480 -i video.mov -vframes 1 -q:v 2 frame.jpg

# Extract range of frames (1 frame per second)
ffmpeg -ss 750 -t 20 -i video.mov -vf fps=1 frames/%03d.jpg
```

---

*Report generated: 2026-04-11 from `/home/manuel/code/wesen/patreon/videos/002-sqrt`*
*Video source: 2026-04-10 rabbit-hole square root deep dive*
