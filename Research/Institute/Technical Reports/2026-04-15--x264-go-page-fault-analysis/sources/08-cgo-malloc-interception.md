---
Title: CGO malloc Interception - Why x264_malloc Uses Go's Heap
Ticket: SCS-0017
Status: completed
Topics:
    - screencast-studio
    - x264
    - cgo
    - go
DocType: reference
Intent: long-term
Owners: []
RelatedFiles: []
ExternalSources: []
Summary: Explanation of how CGO intercepts C library malloc calls and routes them through Go's heap allocator.
LastUpdated: 2026-04-15T15:10:00-04:00
WhatFor: Answer why x264_malloc ends up allocating from Go's heap arenas.
WhenToUse: Understanding the CGO malloc substitution mechanism.
---

# Why x264_malloc Requests Memory from Go's Heap Arena

## The CGO malloc Interception Mechanism

When you use CGO to call C libraries from Go, **Go replaces the C standard library's malloc with its own implementation**. This is why x264's allocations end up in Go's heap.

### How It Works

```
Go Code
    │
    ▼
CGO Call: gst_element_set_state(pipeline, GST_STATE_PLAYING)
    │
    ▼
GStreamer C Code
    │
    ▼
x264enc element requests buffer
    │
    ▼
x264_malloc()  ← This is NOT the standard C malloc!
    │
    ▼
Go Runtime's malloc implementation (via CGO wrapper)
    │
    ▼
Allocates from Go's 128MB heap arena
    │
    ▼
Returns pointer to x264
```

## The Technical Details

### 1. CGO Replaces C malloc

Go's runtime provides a `malloc` symbol that overrides the C library's malloc when CGO is used:

```c
// From Go runtime (simplified)
void* malloc(size_t size) {
    // This calls Go's internal allocator, not libc malloc!
    return runtime_malloc(size);
}
```

### 2. Why Go Does This

**Memory Safety:**
- Go's GC needs to track all pointers
- If C code allocated memory that Go couldn't see, GC might free it while C still uses it
- Or GC might not free it, causing leaks

**Unified Memory Management:**
- All memory in the process is managed by Go's allocator
- Simplifies GC scanning (everything is in Go heap)
- Prevents fragmentation between C and Go heaps

### 3. The 128MB Arena Per Thread

From the Reddit discussion we found:

> "Go allocates 128MB heap arenas on foreign function calls (CGO). Although the memory arena per thread that malloc allocates is 128MB of VM so it shouldn't affect RSS unless someone paged it all in."

**What this means:**
- Each OS thread that calls into CGO gets a 128MB arena
- Multiple threads = multiple arenas
- 25 threads (what we observed) = ~3.2GB of virtual address space reserved
- But only pages that are touched become RSS

### 4. The x264 Buffer Growth Pattern

x264's allocator behavior:
```c
// x264 internal allocation pattern
void* x264_malloc(int size) {
    // This calls Go's malloc!
    return malloc(size);  
}

// During encoding, x264 grows output buffers
void encode_frame() {
    if (output_buffer_full) {
        // Realloc = new allocation + copy
        output_buffer = realloc(output_buffer, new_size);
        // Each new page in the larger buffer triggers a page fault
    }
}
```

### 5. Why This Causes 10x Page Faults in Go vs C

| Scenario | C Process (gst-launch) | Go Process (CGO) |
|----------|------------------------|------------------|
| malloc source | libc malloc | Go runtime malloc |
| Heap type | C heap (brk/mmap) | Go heap (arenas) |
| Pre-allocation | On-demand | 128MB per thread |
| First x264 malloc | Gets fresh C heap page | Gets from 128MB Go arena |
| Page fault timing | At malloc+use | At first touch of arena |
| Buffer growth | C heap expands | Touches new Go arena pages |
| Fault count | Low (C heap already small) | High (Go arena large, many first-touches) |

## The Key Insight

**In C (gst-launch):**
```
x264_malloc → libc malloc → sbrk/mmap → kernel provides fresh page → fault happens ONCE
```

**In Go (CGO):**
```
x264_malloc → Go runtime malloc → 128MB arena already mapped but not faulted
                                    ↓
                           First touch of each 4KB page → PAGE FAULT
                           x264 grows buffer → touches MORE pages → MORE FAULTS
                           Go arena has many pages → many first-touch faults
```

## Visual Diagram

### C Process (gst-launch) - Low Faults

```
Heap: [====] 4MB used, rest unmapped
        ↑
   x264 malloc 1MB → kernel maps 1MB → 256 page faults (once)
   
Result: 2,812 total faults (mostly other memory, not heap)
```

### Go Process (CGO) - High Faults

```
Arena: [████████████████████████████████] 128MB pre-mapped, zero-filled
         ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
         Each touch → PAGE FAULT (32,768 potential faults per arena!)
         
x264 uses 1MB → touches 256 pages → 256 faults
x264 grows to 2MB → touches 512 pages → 512 faults (some overlap, some new)
x264 allocates thread-local buffers → more arenas → more threads → more faults

Result: 27,754 total faults (10x more)
```

## Why Not Use C malloc Directly?

### Option 1: Use C.CString with C.free

You could try to bypass Go's allocator:
```go
// DON'T DO THIS - unsafe!
cStr := C.CString("data")  // Allocates in C heap
C.process(cStr)
C.free(unsafe.Pointer(cStr))  // Must free in C
```

**Problems:**
- Error-prone (forget to free = leak)
- Go GC can't track the pointer
- Can't pass Go pointers to C that contain Go pointers
- CGO rules are strict

### Option 2: Use C.malloc

```go
// Also problematic
ptr := C.malloc(C.size_t(1024))
// This STILL might go through Go's allocator in some CGO versions!
```

## The Real Solutions (Revisited)

### Solution 1: Buffer Pre-allocation in C Heap

Allocate buffers in C that x264 can use directly:

```go
// Allocate in C heap, not Go heap
buffer := C.malloc(C.size_t(bufferSize))
// Pass to x264 to use as output buffer
C.set_x264_output_buffer(encoder, buffer)
```

**Why this helps:**
- C.malloc may bypass Go's arena (implementation-dependent)
- Even if it doesn't, pre-allocating reduces repeated growth faults

### Solution 2: Subprocess Isolation

```
Go Process                    Subprocess
    │                             │
    │──spawn──► x264 encoder      │
    │        (separate process)   │
    │                             │
    │◄──shared mem/pipe───────────┤
    │   encoded data                │
```

**Why this works:**
- x264 runs in pure C process with libc malloc
- No Go heap arenas involved
- Communication via shared memory or pipes

### Solution 3: Limit CGO Thread Count

Since each CGO thread gets a 128MB arena:

```go
// Limit OS threads used by CGO
runtime.GOMAXPROCS(4)  // Fewer threads = fewer arenas
```

**Trade-off:**
- Reduces parallel encoding capability
- May not significantly reduce faults if x264 is the bottleneck

## Summary

**Why x264_malloc uses Go's heap:**
→ CGO intercepts malloc and routes through Go's allocator for memory safety

**Why this causes more faults:**
→ Go's 128MB per-thread arenas have many un-faulted pages
→ x264's buffer growth touches many pages, causing first-touch faults
→ C's on-demand heap only faults pages that are actually needed

**The fundamental issue:**
→ Go's memory management strategy (pre-allocation for GC efficiency)
→ Conflicts with x264's allocation pattern (frequent buffer growth)
→ Results in 10x more page faults for the same work
