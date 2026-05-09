---
Title: x264 Page Fault Analysis Plan
Ticket: SCS-0017
Status: active
Topics:
    - screencast-studio
    - x264
    - performance
    - profiling
DocType: design-doc
Intent: long-term
Owners: []
RelatedFiles: []
ExternalSources:
    - URL: https://man7.org/linux/man-pages/man1/perf-stat.1.html
      Note: perf-stat software fault events including minor-faults, major-faults, page-faults
    - URL: https://github.com/kde/heaptrack
      Note: heap allocation profiler via LD_PRELOAD
    - URL: https://man7.org/linux/man-pages/man1/perf-probe.1.html
      Note: perf-probe for user-space dynamic probes
    - URL: https://bpftrace.org/docs/0.22
      Note: bpftrace for kernel tracepoints and user-space probes
Summary: Detailed 8-step plan to analyze Go+x264 page fault interaction problem.
LastUpdated: 2026-04-15T04:30:00-04:00
WhatFor: Guide systematic investigation with exact commands and expected artifacts.
WhenToUse: Execute steps sequentially; check interpretation at each checkpoint.
---

# x264 Page Fault Deep Analysis Plan

## Step 1: Lock Down the Repro Matrix

Run 4 cells with identical resolution (1920x1080), fps (30), bitrate (2500), runtime (10s), no preview/UI.

### Cells
1. Go host + x264enc
2. Go host + openh264enc
3. gst-launch + x264enc
4. gst-launch + openh264enc

### Metrics to Capture
- `task-clock`
- `cycles`
- `instructions`
- `minor-faults`
- `major-faults`
- `page-faults`
- RSS (from `/proc/[pid]/status`)
- `smaps_rollup` (from `/proc/[pid]/smaps_rollup`)

### Expected Commands

```bash
# Cell 1: Go + x264enc
cd /home/manuel/code/wesen/2026-04-09--screencast-studio
DURATION=10 perf stat -e task-clock,cycles,instructions,minor-faults,major-faults,page-faults \
  ./scripts/go-manual-encode-x264 --duration 10 --width 1920 --height 1080 --fps 30 --bitrate 2500

# Cell 2: Go + openh264enc
DURATION=10 perf stat -e task-clock,cycles,instructions,minor-faults,major-faults,page-faults \
  ./scripts/go-manual-encode-openh264 --duration 10 --width 1920 --height 1080 --fps 30 --bitrate 2500

# Cell 3: gst-launch + x264enc
cat > /tmp/test-x264enc.mp4
DURATION=10 perf stat -e task-clock,cycles,instructions,minor-faults,major-faults,page-faults \
  gst-launch-1.0 -e videotestsrc num-buffers=300 ! \
    video/x-raw,format=I420,width=1920,height=1080,framerate=30/1 ! \
    x264enc bitrate=2500 tune=zerolatency speed-preset=veryfast ! \
    mp4mux ! filesink location=/tmp/test-x264enc.mp4

# Cell 4: gst-launch + openh264enc
DURATION=10 perf stat -e task-clock,cycles,instructions,minor-faults,major-faults,page-faults \
  gst-launch-1.0 -e videotestsrc num-buffers=300 ! \
    video/x-raw,format=I420,width=1920,height=1080,framerate=30/1 ! \
    openh264enc bitrate=2500000 ! \
    mp4mux ! filesink location=/tmp/test-openh264.mp4
```

### Interpretation Checkpoint
- If **only Go+x264** explodes in minor faults → isolated interaction
- If **both x264** cells explode → x264 or system config issue
- If **both Go** cells explode → host/runtime issue

---

## Step 2: Trace User-Space Allocations

### Tool: heaptrack

heaptrack tracks allocation calls through LD_PRELOAD and records backtraces.

```bash
# Install heaptrack if needed
# sudo apt-get install heaptrack heaptrack-gui

# Cell 1: Go + x264enc with heaptrack
cd /home/manuel/code/wesen/2026-04-09--screencast-studio
heaptrack ./scripts/go-manual-encode-x264 --duration 10 --width 1920 --height 1080

# Cell 2: gst-launch + x264enc with heaptrack
heaptrack gst-launch-1.0 -e videotestsrc num-buffers=300 ! \
  video/x-raw,format=I420,width=1920,height=1080,framerate=30/1 ! \
  x264enc bitrate=2500 tune=zerolatency speed-preset=veryfast ! \
  mp4mux ! filesink location=/tmp/test-x264enc.mp4
```

### What to Look For
- Much higher allocation rate in Go+x264 vs gst-launch+x264
- Repeated large reallocations around bitstream/output buffers
- Allocator hot spots from libx264 vs GStreamer glue

---

## Step 3: Put Uprobes on libx264 Allocation Symbols

`perf probe` creates dynamic user-space probes in shared libraries.

### Commands

```bash
# Add uprobes on x264_malloc and x264_free
sudo perf probe -x /usr/lib/x86_64-linux-gnu/libx264.so.164 x264_malloc
sudo perf probe -x /usr/lib/x86_64-linux-gnu/libx264.so.164 x264_free

# List available probes
perf probe -l

# Record allocation events during Go+x264 run
sudo perf record -e probe_libx264:x264_malloc,probe_libx264:x264_free \
  -- ./scripts/go-manual-encode-x264 --duration 10

# Generate report with call stacks
sudo perf report --stdio

# Count events
sudo perf stat -e probe_libx264:x264_malloc,probe_libx264:x264_free \
  -- ./scripts/go-manual-encode-x264 --duration 10
```

### What to Learn
- Does Go+x264 call x264_malloc much more often?
- Are allocation sizes different?
- Is there a specific caller stack uniquely hot in Go case?

---

## Step 4: Attribute Page Faults to Exact User Stacks

bpftrace supports kernel tracepoints and user-space probes with in-kernel filtering.

### Commands

```bash
# Check if bpftrace is available and can run
sudo bpftrace -e 'BEGIN { printf("bpftrace ok\n"); exit(); }'

# Trace user page faults and aggregate by user stack for Go+x264
sudo bpftrace -e '
tracepoint:exceptions:page_fault_user {
    if (comm == "go-manual-encod" || comm == "screencast-stud" || comm == "gst-launch-1.0") {
        @[ustack(), comm] = count();
    }
}
interval:s:10 {
    exit();
}
'

# Also trace with fault address information
sudo bpftrace -e '
tracepoint:exceptions:page_fault_user {
    if (comm == "go-manual-encod" || comm == "screencast-stud") {
        @[ustack(), args->address, comm] = count();
    }
}
interval:s:10 {
    exit();
}
'
```

### What to Answer
- Are faults occurring from stacks inside libx264?
- Are they coming from malloc/memset/memcpy paths?
- Are they concentrated in a small number of stacks?

---

## Step 5: Trace Kernel MM Events

The kernel has tracepoints for memory-management events.

### Commands

```bash
# List MM-related tracepoints
perf list 'vmscan:*' 'compaction:*' 'kmem:*' 'memory:*'

# Record compaction and reclaim events during Go+x264
sudo perf record -e vmscan:mm_vmscan_direct_reclaim_begin,vmscan:mm_vmscan_direct_reclaim_end \
                 -e compaction:mm_compaction_begin,compaction:mm_compaction_end \
                 -e kmem:mm_page_alloc \
  -- ./scripts/go-manual-encode-x264 --duration 10

# Or use tracepoint stat mode
sudo perf stat -e vmscan:mm_vmscan_direct_reclaim_begin \
               -e compaction:mm_compaction_begin \
               -e kmem:mm_page_alloc \
  -- ./scripts/go-manual-encode-x264 --duration 10
```

### What to Watch For
- Compaction activity during Go+x264 but not gst-launch+x264
- Reclaim activity patterns
- Huge-page allocation attempts
- Anonymous page allocation bursts

---

## Step 6: Allocator-Policy A/B Tests

### Test A: MALLOC_ARENA_MAX=1

```bash
# Go + x264 with single arena
MALLOC_ARENA_MAX=1 perf stat -e page-faults,minor-faults,major-faults \
  ./scripts/go-manual-encode-x264 --duration 10

# Compare against default
perf stat -e page-faults,minor-faults,major-faults \
  ./scripts/go-manual-encode-x264 --duration 10
```

### Test B: THP Policy Change

```bash
# Check current THP setting
cat /sys/kernel/mm/transparent_hugepage/enabled

# Test with THP disabled (if not already never)
sudo bash -c 'echo never > /sys/kernel/mm/transparent_hugepage/enabled'
perf stat -e page-faults,minor-faults,major-faults \
  ./scripts/go-manual-encode-x264 --duration 10

# Restore previous setting
sudo bash -c 'echo madvise > /sys/kernel/mm/transparent_hugepage/enabled'
```

### Interpretation
- If MALLOC_ARENA_MAX collapses fault gap → focus on malloc behavior
- If THP policy changes gap → focus on first-touch/compaction/huge-page
- If neither matters → back to user-space allocation tracing

---

## Step 7: Inspect x264 Allocation Behavior

Review x264 source patterns around:
- Buffer-growth strategies
- Per-thread scratch buffer allocation
- Per-frame temporary allocations

Key questions:
- Is there a large buffer grown incrementally vs reserved once?
- Are worker-thread buffers allocated lazily per thread?
- Are per-frame temps that OpenH264 avoids?
- Size thresholds where allocator behavior changes?

---

## Step 8: Synthesis and Recommendations

Based on evidence from steps 1-7, determine:

1. **Which hypothesis is supported?**
   - Allocation churn (Step 2, 3)
   - Fault attribution (Step 4)
   - Allocator policy (Step 6)

2. **What is the concrete fix direction?**
   - Encoder settings change
   - Buffer pre-allocation
   - Host allocator tuning
   - THP policy adjustment

3. **What additional instrumentation is needed?**
   - More targeted uprobes?
   - Custom bpftrace aggregations?
   - x264 rebuild with debug symbols?
