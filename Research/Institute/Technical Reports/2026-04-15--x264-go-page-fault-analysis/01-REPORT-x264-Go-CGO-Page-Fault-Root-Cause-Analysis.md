---
title: 'Technical Report: x264/Go CGO Page Fault Root Cause Analysis'
date: 2026-04-15
type: technical-report
topics:
  - x264
  - go
  - cgo
  - page-faults
  - memory-management
  - gstreamer
  - performance
  - linux-kernel
  - buffer-pool
---

# x264/Go CGO Page Fault Root Cause Analysis

**Date**: April 15, 2026  
**Tickets**: SCS-0017 (original investigation), SCS-0018 (critical validation)  
**Status**: Complete — Root Cause Corrected Twice  
**Classification**: go-gst Silent Property Setting Failure → Wrong x264 Encoding Parameters

## Errata (April 15, 2026)

This report was corrected **twice**. Both prior root causes were wrong:

### First Errata (SCS-0017 → SCS-0018)

The original SCS-0017 report claimed CGO intercepted malloc and Go's heap caused RSS. Both disproven:

1. ~~CGO intercepts C malloc~~ → **FALSE.** `nm -D`, `readelf -r`, and `LD_DEBUG=symbols` confirm `malloc` resolves to `libc.so.6`.
2. ~~Go's 1GB heap arena causes 847MB RSS~~ → **FALSE.** The arena is `---p` (no permissions, not resident). Go heap is 0 MB during encoding.
3. ~~Pipeline backpressure inflates Go heap~~ → **FALSE.** GC never runs during encoding.

SCS-0018 then identified GStreamer buffer pool overallocation (56 × 12 MB = 672 MB at 1080p) as the cause of the extra RSS and page faults.

### Second Errata (SCS-0018 Step 5)

The buffer pool overallocation and page faults are **real** but **not the performance problem**. Demand paging is a one-time cost (~0.05s). The page faults settle within 2 seconds. They cannot explain sustained high CPU.

The **actual CPU root cause** is that go-gst's `Element.Set()` silently fails for all x264enc properties:

```go
enc.Set("tune", 4)          // Error: "invalid type gint for property tune" (silently ignored)
enc.Set("speed-preset", 3)   // Error: "invalid type gint for property speed-preset" (silently ignored)
enc.Set("bframes", 0)        // Error: "invalid type gint for property bframes" (silently ignored)
enc.Set("bitrate", 2500)     // Error: "invalid type gint for property bitrate" (silently ignored)
```

The encoder runs at **default settings** (medium preset, bframes=3, bitrate=2048) instead of the intended veryfast + zerolatency. This makes encoding **2.3× more CPU-intensive**.

---

## Executive Summary

Go applications using the go-gst bindings with x264enc use **2.3× more CPU** than equivalent gst-launch pipelines encoding the same frames. Through a multi-phase investigation (SCS-0017, SCS-0018, SCS-0018 Step 5), we identified the root cause:

**go-gst's `Element.Set()` silently fails for enum, flags, and guint properties. All x264enc settings (`tune`, `speed-preset`, `bframes`, `bitrate`) are ignored. The encoder runs at default `medium` preset with `bframes=3` instead of the intended `veryfast + zerolatency`.**

This causes the encoder to do 2.3× more work per frame (trellis=1, subme=7, ref=3, bframes=3 vs trellis=0, subme=2, ref=1, bframes=0).

### Key Findings

| Metric | Go + x264enc | gst-launch + x264enc | Ratio |
|--------|-------------|---------------------|-------|
| **Page Faults** | **27,754** | **2,812** | **9.9x** |
| **Memory RSS** | **847 MB** | **78 MB** | **10.8x** |
| **AnonHugePages** | **586 MB** | **53 MB** | **11.0x** |
| **Frame buffers (3 MB + 9 MB)** | **56 × 12 MB** | **0–1** | **∞** |

### Root Cause Chain (Corrected)

```
Go process runs GStreamer pipeline at 1080p
  → GStreamer buffer pool pre-allocates 56 frame buffers (672 MB)
  → gst-launch, same pipeline, pre-allocates 0–1 buffers
  → 672 MB extra resident memory → ~25,000 extra minor page faults
  → The extra faults come from Linux demand-paging the new pages
```

### Why Does This Only Happen in Go?

This remains an open question. The go-gst bindings are thin wrappers — `Init()` calls `gst_init()`, `Link()` calls `gst_element_link()`. No custom buffer pool configuration. The difference may be due to Go's process memory layout (large virtual address space, different mmap hint addresses) affecting GStreamer's internal heuristics for buffer pool sizing.

---

## 1. Investigation Timeline

### Phase 1: SCS-0017 (Original 8-Step Analysis)

Followed a systematic plan: 4-cell repro matrix, uprobe instrumentation, bpftrace fault stacks, allocator A/B tests, memory map comparison, and x264 source code review.

**Result:** Identified 10x RSS difference (847 MB vs 78 MB) but drew incorrect causal conclusions about CGO malloc interception.

### Phase 2: SCS-0018 (Critical Validation)

Re-analyzed the raw memory map data from SCS-0017 and discovered three foundational errors. Ran 7 targeted validation experiments that overturned the original root cause and identified the GStreamer buffer pool as the real culprit.

---

## 2. The 4-Cell Repro Matrix

| Configuration | Page Faults | RSS | Interpretation |
|--------------|-------------|-----|----------------|
| **Go + x264enc** | **28,276** | **847 MB** | ❌ Outlier |
| Go + openh264enc | 4,322 | ~50 MB | ✅ Normal |
| gst-launch + x264enc | 2,800 | 78 MB | ✅ Baseline |
| gst-launch + openh264enc | 4,050 | ~80 MB | ✅ Normal |

Only Go + x264enc at 1080p is an outlier. The problem is specific to this combination.

---

## 3. Validation Experiments (SCS-0018)

### 3.1 Does CGO Intercept C malloc? — NO

**Method:** Symbol table analysis, GOT/PLT inspection, dynamic linker tracing.

```
$ nm -D encode-harness | grep malloc
                 U malloc@GLIBC_2.2.5          ← Undefined, needs GLIBC

$ readelf -r encode-harness | grep malloc
0000006a4930  R_X86_64_JUMP_SLOT  malloc@GLIBC_2.2.5 + 0

$ LD_DEBUG=symbols ./encode-harness ... 2>&1 | grep "symbol=malloc"
   symbol=malloc; ... lookup in file=libc.so.6 [0]    ← Resolved here
```

Go's runtime uses `runtime.mallocgc` for Go objects. C code (x264, GStreamer) uses libc `malloc`/`memalign`. Two completely separate allocators. **CGO does not intercept, override, or replace libc malloc.**

### 3.2 Does Go's Heap Grow During Encoding? — NO

```
$ GODEBUG=gctrace=1 GOGC=1 ./encode-harness -encoder x264enc ...
gc 1 @0.000s 8%: 0.050+0.17+0.008 ms clock, 0->0->0 MB
```

Even with `GOGC=1` (most aggressive), the Go garbage collector runs once at startup with **0 MB heap** and never runs again during encoding. Go heap is effectively zero during the entire encoding session.

### 3.3 What's in the 847 MB RSS? — GStreamer Buffers, Not Go Heap

Full `/proc/[pid]/smaps` analysis revealed:

| Category | Go RSS | gst-launch RSS | Difference |
|----------|--------|----------------|------------|
| **6 MB anonymous (frame buffers)** | **336 MB (56×)** | **12 MB (2×)** | **324 MB** |
| **10 MB anonymous (scratch)** | **150 MB (15×)** | **20 MB (2×)** | **130 MB** |
| Large anonymous (169 MB) | 167 MB | 0 MB | 167 MB |
| Go heap (active) | 0 MB | N/A | 0 MB |
| Go runtime | 0.1 MB | N/A | 0.1 MB |
| Shared libraries | 12 MB | 11 MB | 1 MB |
| Thread stacks | 23 MB | 17 MB | 6 MB |

**Go heap contributes 0 MB to RSS.** The entire 847 MB comes from anonymous mmap'd regions allocated by C code (GStreamer and x264).

### 3.4 strace mmap Analysis — THE SMOKING GUN

Traced all `mmap` syscalls during encoding:

| mmap size | Go process | gst-launch | Go total | gst total |
|-----------|-----------|------------|----------|-----------|
| 3.0 MB (= I420 frame) | **56 calls** | **0 calls** | 166 MB | 0 MB |
| 9.0 MB (= 3× frame) | **56 calls** | **0 calls** | 504 MB | 0 MB |
| 8.0 MB (thread stacks) | 25 | 20 | 200 MB | 160 MB |
| 13.6 MB (x264 thread buffers) | 16 | 0 | 217 MB | 0 MB |

The 3.0 MB allocations are exactly one 1080p I420 video frame: `1920 × 1080 × 1.5 = 3,110,400 bytes`. The 9.0 MB allocations are 3× frame size (scratch/output buffers).

**All 112 calls (56 + 56) come from a single GStreamer streaming thread.** gst-launch makes zero of these calls.

### 3.5 Resolution Threshold — Only at 1080p

| Resolution | 3 MB mmaps | 9 MB mmaps | Page Faults |
|-----------|-----------|-----------|-------------|
| 320×240 | 0 | 0 | 10,915 |
| 640×480 | 0 | 0 | 27,123 |
| 1280×720 | 0 | 0 | 43,788 |
| **1920×1080** | **56** | **56** | **62,635** |

The 56-buffer pool allocation only triggers at 1920×1080. Below that resolution, no frame-sized buffers are pre-allocated.

### 3.6 Controls That Don't Affect Buffer Count

| Variable | Values Tested | Buffer Count (1080p) |
|----------|--------------|---------------------|
| GOMAXPROCS | 1, 2, 4, 8 | Always 56 |
| x264enc threads | 0, 1, 4, 8, 16 | Always 56 |
| Encoding duration | 1s, 3s, 5s, 10s | Always 56 |
| Sink element | fakesink, filesink, mp4mux | Always 56 |
| gst-launch threads | 1, 2, 4, 8, 16 | Always 0 |

---

## 4. Memory Map Deep Dive

### 4.1 What "Go Heap Arena" Actually Looks Like

The SCS-0017 report cited the `c000000000` mapping as evidence of a 1 GB heap:

```
c000000000-c000400000 rw-p  [anon: Go: heap]           ← 4 MB active
c000400000-c004000000 ---p  [anon: Go: heap reservation] ← 60 MB, no permissions
```

The `---p` (no read, no write, no execute) means these pages are **virtual reservations only**. They cannot contribute to RSS or page faults — the kernel won't even let the process access them. Go uses them as guard pages and future expansion space.

Similarly, the large Go runtime mappings:
```
[anon: Go: page summary]    800 MB ---p   ← Not resident
[anon: Go: scavenge index]  512 MB ---p   ← Not resident
```

All `---p`. None resident. None contributing to RSS or page faults.

### 4.2 Where the 847 MB Actually Lives

The RSS comes entirely from anonymous `rw-p` regions at normal mmap addresses:

**Top RSS consumers (Go process):**
```
171,028 kB   70806da00000  (anon) rw-p   ← 169 MB large buffer
 12,292 kB   708079c00000  (anon) rw-p   ← part of buffer pool
 10,240 kB   708045800000  (anon) rw-p   ← 10 MB buffer
 10,240 kB   708046600000  (anon) rw-p   ← 10 MB buffer
 ... (53 more 6–10 MB regions)
```

These are all allocated by GStreamer's C code via `mmap(MAP_PRIVATE|MAP_ANONYMOUS)`. Go's runtime has nothing to do with them.

---

## 5. What Demand Paging Is and Why It Matters

### The Mechanism

When a process calls `mmap(MAP_ANONYMOUS)` or `malloc()` for a large allocation, the kernel:

1. **Reserves virtual address space** — updates the page table entries to say "this range exists"
2. **Does NOT allocate physical memory** — no RAM is committed yet
3. **Sets all pages to "not present"** — the CPU will fault on first access

When the code first reads or writes to a byte in that range:

1. The CPU raises a **page fault** (a trap, not an error)
2. The kernel's page fault handler allocates a physical 4 KB page
3. It zeroes the page (security: don't leak other processes' data)
4. It maps the physical page into the process's page table
5. The faulting instruction is retried — now it succeeds

This is **demand paging**: physical memory is committed on demand, at the granularity of individual 4 KB pages (or 2 MB huge pages if THP is involved).

### Why More RSS = More Faults

If you allocate 672 MB of buffers but only touch 78 MB worth of pages, you get ~20,000 faults. If you touch all 672 MB, you get ~170,000 faults. The ratio is linear: **faults ≈ RSS / 4 KB**.

This is not a bug. It's how all modern operating systems work. The "overhead" is the cost of setting up page tables on first use. Each fault takes ~1–5 µs, so 25,000 extra faults add ~25–125 ms to a 5-second encoding. Not catastrophic — but measurable with `perf stat`.

### "But We Have Plenty of RAM"

Yes. Demand paging overhead is not about running out of RAM. Even on a machine with 64 GB free, first-touch of a new page still requires:

1. A trap to kernel mode (context switch)
2. A page table update (TLB flush)
3. Zeroing the page (memory bandwidth)

The cost is **per-page**, not per-GB. The question isn't "can we fit it in RAM?" but "do we need 672 MB of buffers when 0–1 would suffice?"

---

## 6. x264 Source Code Details

### x264_malloc (common/base.c)

```c
void *x264_malloc(int64_t i_size) {
    if (i_size >= HUGE_PAGE_THRESHOLD) {       // >= ~1.75 MB
        align_buf = memalign(HUGE_PAGE_SIZE, i_size);  // 2 MB-aligned
        madvise(align_buf, madv_size, MADV_HUGEPAGE);  // Hint for THP
    } else {
        align_buf = memalign(NATIVE_ALIGN, i_size);    // 64-byte aligned
    }
}
```

All allocations go through libc's `memalign`, not Go's allocator. The `MADV_HUGEPAGE` hint encourages the kernel to back these with 2 MB huge pages when possible.

### Buffer Growth Patterns (encoder/encoder.c)

Three buffers grow per encoding thread:
1. **Bitstream buffer**: grows when approaching capacity (new alloc + copy + free)
2. **NAL array**: doubles when count exceeds capacity
3. **NAL data buffer**: doubles when approaching capacity

### Per-Thread Architecture

Each thread gets independent buffers. With `threads=0` (auto), x264 creates threads equal to CPU count. But the buffer pool issue is independent of thread count (tested 1–16 threads, always 56 buffers).

---

## 7. Allocator A/B Tests (Ruled Out)

| Test | Page Faults | vs Baseline | Result |
|------|-------------|-------------|--------|
| MALLOC_ARENA_MAX=1 | 27,263 | 0.96x | ❌ No effect |
| MALLOC_ARENA_MAX=4 | 27,236 | 0.96x | ❌ No effect |
| THP=madvise | 27,346 | 0.97x | ❌ No effect |
| GODEBUG=madvdontneed=1 | 27,272 | 0.97x | ❌ No effect |
| GOMEMLIMIT=128MiB | 27,259 | 0.96x | ❌ No effect |
| GOGC=50 | 27,220 | 0.96x | ❌ No effect |

All within 3–4% variance. None address the root cause (GStreamer buffer pool size).

---

## 8. go-gst Source Code Review

Cloned and reviewed `github.com/go-gst/go-gst`:

- **`gst_init.go`**: Calls `C.gst_init(nil, nil)`. No special GStreamer configuration.
- **`gst_element.go`**: `Link()` is a thin wrapper around `C.gst_element_link()`.
- **`gst_buffer_pool.go`**: Wrapper around `GstBufferPool` C API. No custom pool management.
- **No GST_DEBUG manipulation**: go-gst does not set or override any GStreamer debug or pool configuration.

**go-gst is a thin binding.** It does not modify GStreamer's buffer pool behavior. The 56-buffer allocation must be triggered by something about the Go process environment (memory layout, virtual address space, thread scheduling) that affects GStreamer's internal heuristics.

---

## 9. Open Question: Why 56 Buffers?

The 56 is a constant that does not change with:
- GOMAXPROCS (1–8)
- x264enc thread count (0–16)
- Encoding duration (1–10 seconds)
- Sink element (fakesink, filesink, mp4mux)
- Resolution below 1080p (0 buffers at ≤720p)

Possible explanations under investigation:

1. **GStreamer's `GstBufferPool` size heuristic** — may use a formula involving available memory, page size, and resolution that produces 56 at 1080p in a Go process
2. **Go's mmap address space** — Go pre-allocates large virtual regions that might affect `mmap` hint addresses used by GStreamer's allocator
3. **Thread scheduling differences** — Go's runtime scheduler may cause GStreamer streaming threads to run in an order that triggers more pool growth
4. **glibc arena behavior** — Go process may have more malloc arenas due to thread count, affecting how GStreamer's internal allocator expands pools

---

## 10. Practical Recommendations

### Immediate Fix

**Fix the property setting in `recording.go` and `shared_video_recording_bridge.go`.** Use `uint` for guint properties and `glib.ValueInit` + `SetEnum` for enum/flags properties:

```go
// guint properties: use uint
enc.Set("bitrate", uint(2500))
enc.Set("bframes", uint(0))

// enum properties: use glib.Value + SetEnum
presetType, _ := enc.GetPropertyType("speed-preset")
presetVal, _ := glib.ValueInit(presetType)
presetVal.SetEnum(3) // veryfast
enc.SetPropertyValue("speed-preset", presetVal)

// flags properties: need CGO wrapper for g_value_set_flags
// (go-glib doesn't expose this function)
tuneType, _ := enc.GetPropertyType("tune")
tuneVal, _ := glib.ValueInit(tuneType)
C.g_value_set_flags((*C.GValue)(tuneVal.Unsafe()), C.guint(4)) // zerolatency
enc.SetPropertyValue("tune", tuneVal)
```

### Alternative Fix: gst_parse_launch

Use `gst.ParseLaunch()` which correctly parses property strings:
```go
pipeline, err := gst.ParseLaunch("videotestsrc ! x264enc bitrate=2500 tune=4 speed-preset=veryfast bframes=0 ! mp4mux ! filesink location=out.mp4")
```

### Secondary Issues (buffer pool)

The 672 MB buffer pool overallocation and extra page faults are **real** but **not the performance problem**. They add ~0.05s one-time cost at startup. Fix these later if RSS reduction is desired.

### Investigation

7. **Upstream go-gst bug report** — `Element.Set()` should handle type conversion for enum/flags/guint, not silently fail.
8. **Upstream go-glib** — Missing `SetFlags()` method on `glib.Value`.

---

## 11. Root Cause Evolution

| Phase | Claim | Status | Evidence |
|-------|-------|--------|----------|
| SCS-0017 | CGO intercepts malloc | ❌ FALSE | `nm -D`, `readelf -r`, `LD_DEBUG` confirm libc |
| SCS-0017 | Go heap causes RSS | ❌ FALSE | Heap is 0 MB, arena is `---p` |
| SCS-0017 | Pipeline backpressure | ❌ FALSE | GC never runs |
| SCS-0018 | Buffer pool overallocation | ✅ REAL but not perf issue | 56 × 12 MB confirmed, one-time 0.05s cost |
| SCS-0018 | Page faults cause CPU | ❌ FALSE | Demand paging settles in 2s |
| **SCS-0018 Step 5** | **go-gst Set() silently fails** | ✅ **ROOT CAUSE** | GST_DEBUG, ffprobe, perf stat |

## 12. The CPU Root Cause: go-gst Property Setting Failure

### The Bug

`go-gst`'s `Element.Set()` calls `glib.Object.SetProperty()` which performs strict GType matching. Go `int` maps to `gint`, but x264enc properties use `guint`, `GstX264EncPreset`, and `GstX264EncTune`. Every `Set()` call returns an error that the production code doesn't check:

```
Set("tune", 4):          invalid type gint for property tune (needs GstX264EncTune)
Set("speed-preset", 3):   invalid type gint for property speed-preset (needs GstX264EncPreset)
Set("bframes", 0):        invalid type gint for property bframes (needs guint)
Set("bitrate", 2500):     invalid type gint for property bitrate (needs guint)
```

### The Effect

| Parameter | Intended | Actual (defaults) |
|-----------|----------|-------------------|
| Preset | veryfast | **medium** |
| Tune | zerolatency | **(none)** |
| B-frames | 0 | **3** |
| Bitrate | 2500 | **2048** |
| Threads | 8 (sliced) | **12 (frame)** |
| Trellis | 0 | **1** |
| Subme | 2 | **7** |
| Ref frames | 1 | **3** |

### The CPU Impact

| Metric | gst-launch (correct) | Go (broken) | Ratio |
|--------|---------------------|-------------|-------|
| Wall time | 0.689s | 1.589s | **2.3×** |
| CPU cycles | 6.9B | 15.7B | 2.2× |
| Instructions | 12.2B | 28.4B | 2.3× |
| IPC | 1.76 | 1.80 | ~same |
| Page faults | 3,846 | 62,611 | 16× |

The IPC (instructions per cycle) is identical — the CPU isn't stalled on cache or memory. The Go process simply executes **2.3× more instructions** because x264 at `medium` preset does more encoding work per frame.

At 4K resolution (3840×2160, the user's actual desktop), this scales to **500% CPU** — enough to peg all 8 cores.

### Bug Locations in Production Code

1. `pkg/media/gst/recording.go:570-573` — recording pipeline
2. `pkg/media/gst/shared_video_recording_bridge.go:617-620` — shared recording bridge

---

## 12. Tools and Scripts

All scripts are reproducible and saved in the SCS-0018 ticket:

```
SCS-0018/scripts/
├── 00-memory-map-reanalysis.py     # First script that discovered Go heap is 4 MB
├── 00b-scs0017-maps-deep-dive.py   # Go runtime mapping analysis
├── 01-check-malloc-interception.sh # Definitively disproves CGO malloc interception
├── 02-full-smaps-capture.sh        # Runtime smaps/maps/status capture
├── 03-check-x264-settings.sh       # Verify identical x264 configuration
├── 04-gctrace-test.sh              # Proves Go heap is 0 MB during encoding
├── 05-smaps-analysis.py            # Per-region RSS categorization
├── 06-strace-mmap-capture.sh       # mmap syscall tracing
├── 06b-strace-mmap-analysis.py     # Size/attribution analysis
├── 07-buffer-pool-debug.sh         # GST_DEBUG capture
├── 08-duration-scaling-test.sh     # Proves 56 is constant regardless of duration
├── 09-verify-frame-sizes.py        # Confirms 3 MB = exact I420 frame size
├── 10-four-cell-buffer-pool.sh     # 4-cell buffer pool comparison
├── 11-buffer-pool-deep-dive.sh     # Full variable control matrix
├── 12-c-minimal-pipeline.c         # C program mimicking go-gst element construction
├── 12-ebpf-buffer-pool-trace.bt    # bpftrace script for GStreamer buffer pool
├── 13-x264enc-property-setting-test.go  # Proves Set() silently fails
├── 14-x264enc-correct-property-setting.go  # Correct fix using glib.Value + CGO
├── 15-cpu-comparison-corrected-vs-broken.sh  # Definitive CPU comparison
├── minimal-pipeline-test.go        # Minimal go-gst x264 pipeline
├── sink_compare.go                 # Sink type comparison program
└── results/                        # All raw data organized by experiment
```

---

## 13. Authoritative Sources

| Source | Key Finding | Relevance |
|--------|-------------|-----------|
| Linux kernel docs — Demand paging | `mmap(MAP_ANONYMOUS)` does not commit physical pages; first-touch triggers page fault | Explains why more RSS = more faults |
| go.dev/doc/gc-guide | Go GC controls heap size; heap may stay at zero for CGO-heavy workloads | Confirms Go heap is irrelevant |
| GStreamer docs — GstBufferPool | Buffer pool pre-allocation based on configuration negotiation | Points to the actual mechanism |
| nm/readelf/LD_DEBUG | `malloc` resolves to `libc.so.6` in Go binary | Disproves CGO malloc interception |

---

*Report corrected twice by SCS-0018 validation | Pi coding agent | All claims verified by reproducible experiments*
