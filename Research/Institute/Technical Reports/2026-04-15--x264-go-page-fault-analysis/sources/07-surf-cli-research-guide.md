---
Title: Surf-CLI Research Guide for Deeper Analysis
Ticket: SCS-0017
Status: active
Topics:
    - screencast-studio
    - research
    - surf-go
DocType: reference
Intent: long-term
Owners: []
RelatedFiles: []
Summary: Guide for using surf-cli to do deeper research when browser extension is active.
LastUpdated: 2026-04-15T04:40:00-04:00
WhatFor: Instructions for deeper web research using surf-go browser automation.
WhenToUse: When you want ChatGPT synthesis or Kagi Assistant analysis of the page fault findings.
---

# Surf-CLI Research Guide

## Setup (Required Before Use)

### 1. Load Surf Extension in Chromium

Navigate to:
```
chrome://extensions/
```

Load unpacked extension from:
```
/home/manuel/code/others/llms/pi/nicobailon/surf-cli/dist
```

### 2. Verify Socket is Active

```bash
export SURF_SOCKET_PATH=/home/manuel/snap/chromium/common/surf-cli/surf.sock
ls -la $SURF_SOCKET_PATH
```

Should show: `srwxr-xr-x 1 manuel manuel ... /home/manuel/snap/chromium/common/surf-cli/surf.sock`

### 3. Log into Web Apps

In Chromium, log into:
- Kagi (kagi.com)
- ChatGPT (chat.openai.com)

---

## Recommended Surf Commands for This Research

### Option 1: Kagi Search for Additional Sources

```bash
export SURF_SOCKET_PATH=/home/manuel/snap/chromium/common/surf-cli/surf.sock

cd /home/manuel/code/others/llms/pi/nicobailon/surf-cli/go

# Search for Go memory arena internals
go run ./cmd/surf-go kagi search \
  --query "Go runtime heap arena 64MB 128MB allocation internals" \
  --keep-tab-open

# Search for CGO memory performance issues
go run ./cmd/surf-go kagi search \
  --query "CGO C.Go performance memory overhead site:go.dev OR site:github.com/golang" \
  --keep-tab-open

# Search for first-touch page fault optimization
go run ./cmd/surf-go kagi search \
  --query "Linux first touch page fault optimization mmap populate" \
  --keep-tab-open
```

### Option 2: Kagi Assistant for Synthesis

```bash
export SURF_SOCKET_PATH=/home/manuel/snap/chromium/common/surf-cli/surf.sock

cd /home/manuel/code/others/llms/pi/nicobailon/surf-cli/go

# Get structured analysis of Go heap behavior
go run ./cmd/surf-go kagi assistant \
  "Explain why Go pre-allocates large heap arenas and how this causes page faults in CGO applications. Compare with C malloc behavior." \
  --assistant Quick \
  --lens Programming \
  --web-search-mode on

# Analyze THP impact
go run ./cmd/surf-go kagi assistant \
  "How do Transparent Huge Pages interact with Go's garbage collector? What causes the page fault overhead during promotion?" \
  --assistant Quick \
  --lens Programming
```

### Option 3: ChatGPT for Deep Analysis

```bash
export SURF_SOCKET_PATH=/home/manuel/snap/chromium/common/surf-cli/surf.sock

cd /home/manuel/code/others/llms/pi/nicobailon/surf-cli/go

# Detailed root cause analysis
go run ./cmd/surf-go chatgpt ask \
  "I have a Go application using GStreamer/CGO for video encoding with x264. The Go process shows 10x more page faults than a pure C (gst-launch) equivalent. 

Data:
- Go RSS: 847 MB vs C RSS: 78 MB (10.8x)
- Go page faults: 27,754 vs C: 2,812 (10x)
- Go heap address: 0xC000000000 (pre-allocated ~1GB arena)
- C heap: grows on demand

Analysis shows Go's garbage collector pre-allocates heap arenas. The x264 encoder allocates ~2x more calls in Go but causes 10x more faults (5x per allocation).

Explain:
1. Why does Go pre-allocate such large heap arenas?
2. How does this interact with Linux demand paging to cause more faults?
3. What is the relationship with CGO and thread-local arenas (128MB per thread)?
4. Why don't MALLOC_ARENA_MAX, THP settings, or GODEBUG=madvdontneed=1 help?
5. What are the architectural solutions (subprocess, buffer pre-allocation, etc.)?"

# Then export the transcript
go run ./cmd/surf-go chatgpt transcript \
  --export-file /home/manuel/workspaces/2026-04-15/x264-test-debug/2026-04-09--screencast-studio/ttmp/2026/04/15/SCS-0017--x264-page-fault-deep-analysis/reference/chatgpt-analysis.md
```

---

## Research Questions to Ask

### For Kagi Search

1. **Go Runtime Internals**
   - "Go runtime heap arena size allocation strategy internals"
   - "Go mheap arena growth 64MB 128MB spans"
   
2. **CGO Specifics**
   - "CGO memory arena thread local allocation C.CString"
   - "CGO performance overhead memory allocation"
   
3. **Page Fault Deep Dive**
   - "Linux page fault first touch demand paging anonymous mmap"
   - "minor page fault vs major page fault performance cost"

4. **THP and Go**
   - "Transparent huge pages THP madvise performance latency"
   - "Go runtime MADV_NOHUGEPAGE huge page"

5. **Solutions**
   - "Go subprocess isolation CGO ffmpeg encoding"
   - "Go shared memory mmap C library buffer pool"

### For Kagi Assistant

1. **Mechanism Explanation**
   - "Why does Go allocate heap memory in large arenas instead of growing like C malloc?"
   
2. **Performance Comparison**
   - "Compare Go garbage collector heap growth vs C malloc sbrk/mmap strategies"
   
3. **CGO Optimization**
   - "How to optimize CGO performance when calling C libraries that allocate memory?"
   
4. **Page Fault Analysis**
   - "What causes high minor page fault rates in applications with large pre-allocated heaps?"

### For ChatGPT

1. **Root Cause Synthesis**
   - Detailed analysis of why 2x allocations cause 10x faults
   - Memory layout and first-touch patterns
   
2. **Solution Evaluation**
   - Pros/cons of each architectural fix
   - When to use subprocess vs buffer pooling
   
3. **Code Examples**
   - Example of buffer pre-allocation in Go for C libraries
   - Example of subprocess isolation pattern

---

## Integration with Docmgr

After surf research, relate findings to ticket:

```bash
# Add ChatGPT transcript to ticket
docmgr doc relate \
  --doc /home/manuel/workspaces/2026-04-15/x264-test-debug/2026-04-09--screencast-studio/ttmp/2026/04/15/SCS-0017--x264-page-fault-deep-analysis/reference/04-final-synthesis-and-recommendations.md \
  --file-note "/path/to/chatgpt-transcript.md:ChatGPT deep analysis of root cause"

# Check off research task
docmgr task check --ticket SCS-0017 --id <research-task-id>
```

---

## Current Web Research Summary (Already Completed)

Without surf-cli, I already gathered authoritative sources via web search:

### Key Findings from Web Research

1. **Go Never Frees Heap to OS** (mtardy.com)
   - "Go basically never frees heap memory back to the operating system"
   
2. **128MB CGO Arenas** (Reddit)
   - Go allocates 128MB heap arenas per thread for CGO calls
   - "Shouldn't affect RSS unless someone paged it all in"
   
3. **Demand Paging First-Touch** (offlinemark.com)
   - Page faults happen on first access, not allocation
   - Kernel returns pointer immediately, waits for touch
   
4. **MADV_DONTNEED vs MADV_FREE** (GitHub)
   - Go 1.16+ uses MADV_DONTNEED when releasing memory
   - GODEBUG=madvdontneed=1 affects release, not initial allocation
   
5. **Official Go GC Guide** (go.dev)
   - Go GC has explicit control over heap size
   - Target heap based on GOGC percentage of live data

### Authoritative Sources List

See [reference/06-web-research-sources.md](reference/06-web-research-sources.md) for full citations.

---

## Next Steps

1. **Activate Surf Extension** (if deeper research needed)
   - Load extension in Chromium
   - Verify socket path
   - Log into Kagi/ChatGPT

2. **Run Kagi Assistant Query**
   - Get structured synthesis of Go heap behavior
   - Compare with C malloc strategies

3. **Run ChatGPT Deep Analysis**
   - Export detailed root cause explanation
   - Get architectural solution recommendations

4. **Integrate Findings**
   - Add surf research outputs to docmgr ticket
   - Update synthesis document with new insights
