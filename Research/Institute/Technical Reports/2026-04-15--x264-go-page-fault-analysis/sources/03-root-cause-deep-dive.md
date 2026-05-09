---
Title: Root Cause Deep Dive Plan
Ticket: SCS-0017
Status: active
Topics:
    - screencast-studio
    - x264
    - performance
    - memory
DocType: design-doc
Intent: long-term
Owners: []
RelatedFiles: []
Summary: Targeted diagnostics to isolate the exact mechanism causing 5x more faults per allocation in Go.
LastUpdated: 2026-04-15T04:30:00-04:00
WhatFor: Identify the specific memory behavior difference, not just workarounds.
WhenToUse: Execute when you need to understand the "why" before choosing a fix.
---

# Root Cause Deep Dive: Why Do the Same Allocations Fault More in Go?

## Current State

We know:
- x264_malloc calls: 2.0x ratio (Go vs gst-launch)
- Page faults: 10.1x ratio
- Faults per allocation: ~5x ratio
- NOT caused by: arena count, THP, Go scavenger, allocation frequency

## Hypotheses to Test

### H1: Memory Map Layout Hypothesis
**Theory:** Go's heap is placed at a different virtual address than C processes, causing different kernel page table behavior or cache effects.

**Test:** Compare `/proc/[pid]/maps` between Go and gst-launch processes

**What to look for:**
- Different heap base addresses
- Different anonymous mapping patterns
- Different library loading addresses (ASLR interactions)
- Huge page reservation differences

---

### H2: Allocation Timing Hypothesis  
**Theory:** Go faults happen at different times - immediately at allocation vs later at first use, or spread across different system calls.

**Test:** Trace `mmap`, `munmap`, `mprotect`, `mremap` syscalls with timing

**What to look for:**
- Different syscall patterns (more mprotect? more mremap?)
- Timing: faults during allocation vs during encoder use
- Different flags to mmap (MAP_POPULATE, MAP_LOCKED, etc.)

---

### H3: Thread-Local Touch Hypothesis
**Theory:** x264 allocates memory in one thread, but Go touches it from a different thread (CGO callback thread), causing cross-NUMA or cache coherency faults.

**Test:** Trace which thread calls x264_malloc vs which thread faults on that memory

**What to look for:**
- Different thread IDs in allocation vs fault stacks
- Thread migration patterns
- NUMA node differences (if applicable)

---

### H4: Stack Growth vs Heap Growth Hypothesis
**Theory:** The extra faults are from Go stack growth during CGO calls, not from x264 heap allocations.

**Test:** Separate stack faults from heap faults using fault address analysis

**What to look for:**
- Fault addresses in stack ranges vs heap ranges
- cgocallback stack frames in fault stacks
- Correlation between CGO calls and fault bursts

---

### H5: Memory Initialization Pattern Hypothesis
**Theory:** x264 expects zeroed memory or certain patterns, but Go's allocator provides memory that requires more kernel intervention to prepare.

**Test:** Check if faults correlate with memory initialization (zeroing) patterns

**What to look for:**
- MAP_UNINITIALIZED or similar flags
- Differences in faulting addresses - are they always new pages?
- memset calls in x264 following allocations

---

## Diagnostic Tools

### 1. Memory Map Comparison Script

```bash
#!/bin/bash
# Run both processes, capture /proc/[pid]/maps, compare
```

Key comparisons:
- Heap segment size and location
- Anonymous mapping count and sizes
- Shared library addresses
- [heap] vs [anon] regions

### 2. mmap/munmap Syscall Tracer

```bash
# Using strace
strace -e trace=mmap,munmap,mprotect,mremap,brk -tt -T \
    ./encode-harness -encoder x264enc 2>&1 | tee go-mmap.log

strace -e trace=mmap,munmap,mprotect,mremap,brk -tt -T \
    gst-launch-1.0 ... x264enc ... 2>&1 | tee gst-mmap.log
```

Compare:
- Number of each syscall type
- Sizes passed to mmap
- Flags (MAP_PRIVATE, MAP_ANONYMOUS, MAP_POPULATE)
- Timing relative to encoding phases

### 3. Thread-Aware Fault Tracer (bpftrace)

```bpftrace
#!/usr/bin/env bpftrace

tracepoint:exceptions:page_fault_user {
    if (comm == "encode-harness") {
        // Record fault address, thread ID, and stack
        @[pid, tid, ustack(5), args->address] = count();
    }
}

// Also trace x264_malloc to correlate allocation address with fault address
uprobe:/usr/lib/x86_64-linux-gnu/libx264.so.164:x264_malloc {
    @["malloc", pid, tid] = count();
}
```

### 4. Address Space Analysis

For each fault, determine if it's in:
- Go heap (check against /proc/[pid]/maps [heap] range)
- Go stacks (check [stack] ranges)
- x264 heap (anonymous mappings after encoder startup)
- Code pages (executable libraries)

### 5. Fault Timing Analysis

Trace:
1. When x264_malloc returns an address
2. When that address page-faults
3. Time delta between allocation and fault

If faults happen immediately → allocation-time issue
If faults happen later during encoding → use-time issue

---

## Decision Tree

After these diagnostics, we should know:

**If H1 (Memory Layout) is true:**
→ The virtual address space placement matters
→ Solution: mmap with specific hints, or use fixed addresses

**If H2 (Allocation Timing) is true:**
→ Different syscall patterns cause different kernel paths
→ Solution: Pre-populate pages (touch after alloc), use MAP_POPULATE

**If H3 (Thread-Local) is true:**
→ Thread migration or NUMA effects
→ Solution: Pin threads, use thread-local allocators, NUMA-aware allocation

**If H4 (Stack Growth) is true:**
→ CGO stack overhead is the real culprit, not x264 heap
→ Solution: Increase initial stack sizes, reduce CGO call frequency

**If H5 (Initialization) is true:**
→ Zeroing patterns differ between allocators
→ Solution: Use calloc instead of malloc, or pre-touch pages

---

## Success Criteria

We will have found the root cause when we can:
1. **Predict** the fault count given a memory configuration
2. **Reproduce** the fault difference with a minimal C program that mimics Go's behavior
3. **Measure** the specific behavior difference (e.g., "Go's heap starts at 0x7f0000000000 vs C at 0x55...")

---

## First Priority Test

Start with **Memory Map Comparison (H1)** because:
- Non-invasive (just read /proc/[pid]/maps)
- High information density
- May immediately reveal address space differences
