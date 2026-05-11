---
title: Smalltalk-80 VM
aliases:
  - Smalltalk-80 VM
  - ST80 VM
  - Blue Book Interpreter in Go
tags:
  - project
  - smalltalk
  - vm
  - bluebook
  - go
  - interpreter
status: active
type: project
created: 2026-03-18
repo: /home/manuel/code/wesen/2026-03-17--smalltalk
---

# Smalltalk-80 VM

This project is a Blue-Book-first Smalltalk-80 interpreter in Go. The target is not a vaguely Smalltalk-like runtime, but a VM that matches the execution model described in *Smalltalk-80: The Language and its Implementation* closely enough to boot the image, run the scheduler correctly, honor the object-memory model, and execute the real image methods without leaning on another implementation as a hidden oracle.

> [!summary]
> The project currently has three important identities:
> 1. a Blue Book reconstruction project for the Smalltalk-80 VM and object memory
> 2. a debugging and verification project driven by traces, image artifacts, and ticket writeups
> 3. a practical Go implementation that is now beyond early boot, into real runtime/storage-management work, and far enough along that live UI exercise exposes genuine VM invariants instead of only host-backend problems

## Why this project exists

The interesting part of this repository is not merely "run an old image." The interesting part is to rebuild the VM from the canonical specification, keep the implementation legible, and discover which details actually matter when a real image starts depending on them.

That means the project has strict reference boundaries:

- the Blue Book is the primary specification
- local artifacts derived from the Blue Book are fair game:
  - `data/bluebook-spec-notes.md`
  - the OCR extracts under `ttmp/2026/03/18/ST80-003--smalltalk-80-graphical-ui-host-window-and-event-loop/reference/ocr-bluebook/`
- the local traces and image inventories are fair game:
  - `data/trace2`
  - `data/trace3`
  - `data/class.oops`
  - `data/method.oops`
- the Wolczko page is allowed as a historical resource boundary, but the project has explicitly avoided turning another implementation into the real design authority

This matters because several of the hardest bugs were not "missing feature" bugs. They were specification-interpretation bugs: bit numbering, header decoding, field order, selector cache hashing, object shape assumptions, and integer representation boundaries.

## Project scope

The center of gravity is the VM:

- image loading
- object pointer encoding and object table layout
- object memory access
- compiled method decoding
- bytecode dispatch
- message send and lookup
- context creation and return
- process scheduling and semaphores
- primitive dispatch
- enough display and input semantics for the image to proceed

This note intentionally does **not** focus on the host window/backend work. That exists and matters, but it is secondary here. The more important story is how the interpreter crossed from "boots a little" into "can run for millions of cycles, expose real image behavior, and now demand a more faithful Chapter 30 storage manager."

## Current status

At this point in the project:

- the image loader works
- the object memory model is implemented well enough to run the image
- all bytecodes are dispatched
- method lookup and caching work
- contexts and returns work well enough for long runs
- the VM matches the early reference traces
- the runtime can run for millions of cycles without the earlier interpreter corruption frontiers
- real BitBlt semantics now exist in the interpreter rather than a fake success stub
- primitive `97` snapshot support exists
- a real host UI path exists and is useful enough to expose VM bugs rather than only backend/input bugs
- the project now has a dedicated storage-management / GC ticket because live `Point` allocation exhausted the full 15-bit object-table space
- a first-pass mark/sweep reclaim path now exists and allocation retries after OT exhaustion instead of failing immediately

What is still incomplete on the VM side:

- there is still no full Blue Book Chapter 30 storage manager in the strong sense
- not every primitive family is fully implemented
- object memory is still a pragmatic subset of the Blue Book storage manager rather than a finished Chapter 30 reconstruction
- heap free-chunk lists and compaction are not implemented yet
- the new first-pass GC moved the frontier forward, but a later scheduler/process corruption still remains
- some remaining correctness work is now in the "audit and completeness" category rather than the "can it boot at all" category

In practical terms, the project is no longer blocked by early interpreter bring-up. It is now in the phase where the hard remaining work is long-run semantic fidelity.

## Repository shape

The core implementation is concentrated in a small number of files:

- `pkg/image/loader.go`
  - loads the virtual image
  - now also writes snapshot images back out
- `pkg/objectmemory/objectmemory.go`
  - implements the 16-bit OOP model, object table access, body access, and allocation helpers
- `pkg/interpreter/interpreter.go`
  - the actual bytecode interpreter, send machinery, context machinery, process scheduler state, and primitive implementations
- `pkg/interpreter/interpreter_test.go`
  - regression coverage for reference traces, specific primitive bugs, and long-run diagnostics
- `pkg/objectmemory/objectmemory_test.go`
  - allocator and shape-safety regressions

There are also a few utility commands that matter from a VM perspective:

- `cmd/st80-snapshot`
  - headless framebuffer snapshots
- `cmd/st80-exercise-snapshot`
  - direct interpreter-side input exercise plus before/after framebuffer comparison

The ticket documentation is unusually important in this repository. The interpreter history is not just encoded in Git; it is also encoded in deliberate writeups:

- `ttmp/2026/03/17/ST80-001--smalltalk-80-vm-in-go-with-sdl-display/`
- `ttmp/2026/03/17/ST80-002--smalltalk-80-interpreter-continuation-context-recovery-and-io-path/`
- `ttmp/2026/03/18/ST80-003--smalltalk-80-graphical-ui-host-window-and-event-loop/`
- `ttmp/2026/03/18/ST80-004--smalltalk-80-object-memory-garbage-collection-and-storage-management/`

For VM work, the current split is:

- `ST80-002`
  - interpreter continuation, context recovery, long-run send/control/runtime correctness
- `ST80-003`
  - host exercise path, OCR verification, and VM-visible display/input behavior
- `ST80-004`
  - object memory, garbage collection, and Blue Book Chapter 30 storage-management work

## Architectural shape

At a high level, the implementation looks like this:

```text
VirtualImage
  -> pkg/image/loader.go
  -> pkg/objectmemory/objectmemory.go
  -> pkg/interpreter/interpreter.go
  -> bytecode dispatch / message send / primitive response
  -> image-side Smalltalk methods and processes
```

The interpreter is intentionally organized around Blue Book concepts rather than generic VM abstractions:

- active context registers
- home context
- sender/caller distinction
- method cache
- primitive success flag
- semaphore and process-switch state
- designated display/cursor/input state for the I/O primitive surface

That is a good fit for this project. The Smalltalk-80 VM is not easiest to understand as a modern generic VM; it is easiest to understand when the implementation still resembles the book.

## Blue Book model that the code is trying to honor

### 1. Object pointers and SmallIntegers

The object model is the canonical 16-bit one:

- bit 0 set means immediate SmallInteger
- bit 0 clear means object-table-based OOP
- SmallInteger payload is a signed 15-bit value
- effective SmallInteger range is `-16384 .. 16383`

This is one of the first places where "just use Go ints" would have quietly broken the project. The image depends on the SmallInteger boundary being real. One of the later display bugs came directly from forgetting that a valid positive integer might no longer be a SmallInteger once it crosses the 16383 limit.

### 2. Object memory layout

The object memory follows the Blue Book shape:

- object table entries contain metadata and a location
- object bodies live in object space
- object bodies begin with size and class words, then fields/data
- the object-table metadata distinguishes pointer objects, word objects, byte objects, and odd-byte-length cases

The code in `pkg/objectmemory/objectmemory.go` mirrors the book's bit-level model closely, including the mismatch between Blue Book bit numbering and normal machine bit numbering. That translation was important enough to deserve explicit commentary in both the code and the OCR-based object-memory audit.

### 3. Class instance specification

Class instance specifications matter because they determine allocation and indexing semantics:

- pointers vs raw data
- words vs bytes
- fixed fields vs indexable payload

This project now has typed allocation support rather than a one-size-fits-all allocator. That turned out to be necessary for correct `new` / `new:` behavior and for display-related objects whose payloads are words rather than pointers.

### 4. CompiledMethod structure

Compiled methods are decoded according to the Blue Book header format:

- field `0` is the SmallInteger header
- literal frame follows
- bytecodes follow the literal frame
- flag bits encode argument count or primitive-related special cases
- header extension literals matter for primitive index and extended argument count

This is one of the most bug-sensitive parts of the implementation. A small mistake here does not merely make one method wrong; it contaminates context sizing, primitive decoding, and send activation in ways that explode much later.

### 5. Context model

The code respects the Blue Book distinction between `MethodContext` and `BlockContext`:

- sender/caller fields
- IP/SP slots
- method vs argument-count discriminator in field `3`
- home context for blocks
- temporary frame beginning at `TempFrameStart = 6`

The context machinery is central. Several of the project’s most time-consuming bugs were really context-shape and context-lifetime bugs disguised as unrelated send failures.

### 6. Bytecode categories

The interpreter dispatches the full bytecode space with the expected Blue Book grouping:

- stack bytecodes
- return bytecodes
- extended push/store variants
- send bytecodes
- jump bytecodes
- arithmetic and special-message bytecodes

The local `data/bluebook-spec-notes.md` file is a useful shorthand for this mapping and clearly influenced the current constant and dispatch organization.

### 7. Message sending and method cache

Send behavior follows the familiar Blue Book path:

1. identify receiver and argument count from the stack
2. find the receiver class
3. consult the method cache
4. fall back to dictionary lookup
5. decode primitive behavior if present
6. either satisfy the primitive or activate a new method context

The method cache exists because the Blue Book VM has it, but it also became a major debugging frontier. A wrong cache hash is not a performance bug first; it is a semantic corruption bug.

### 8. Process scheduling and semaphores

The interpreter carries explicit process/scheduler state:

- pending process switch bookkeeping
- semaphore list bookkeeping
- timer semaphore support

That allowed the runtime to move from startup into the scheduler idle loop and later out of some notifier/debugger frontiers once the right primitives existed.

## The practical source of truth

The practical source of truth has been a layered one:

1. the Blue Book itself
2. local Blue Book extraction notes in `data/bluebook-spec-notes.md`
3. reference traces:
   - `data/trace2`
   - `data/trace3`
4. image inventories:
   - `data/class.oops`
   - `data/method.oops`
5. the intern OCR pack under `reference/ocr-bluebook/`

That is a good project discipline. It gives enough grounding to debug real behavior without drifting into "I copied another VM."

## New frontier: Chapter 30 is now real

One of the most important shifts in the project happened only after the host exercise path became good enough to produce real VM pressure. A live run eventually failed with:

```text
panic: object table exhausted: otEntryCount=32768 class=0x001A bodySize=4
```

That failure matters because it is one of the cleanest possible confirmations that the project had reached the object-memory/storage-management boundary described in the Blue Book:

- `32768` is the full 15-bit object-table space
- `0x001A` is `Point`
- the image was allocating real temporary objects faster than the current pragmatic allocator/reuse model could reclaim them

This changed the project map immediately:

- before that panic, it was still possible to think mainly in terms of interpreter bugs and missing primitives
- after that panic, a real storage manager was clearly required

The project now has a dedicated Chapter 30 ticket (`ST80-004`) for exactly that reason.

### What the first GC/storage slice now does

The current implementation is not a full Blue Book storage manager, but it is no longer “no GC” either. The first pass now includes:

- a mark/sweep-style reclaim path
- interpreter-owned root discovery
- compiled-method literal-frame tracing during marking
- allocation retry after OT exhaustion
- continued exact-size body reuse for reclaimed objects

This is enough to move the frontier forward honestly. The VM no longer dies immediately at object-table exhaustion under the same path.

### What it does not yet do

The first pass is still deliberately narrower than full Chapter 30:

- no free-chunk lists by size
- no real non-append heap allocation policy
- no compaction
- no full reference-count rectification scheme
- no proof yet that all allocation sites are safe GC trigger points

That is acceptable for now because the immediate proven blocker was OT exhaustion, not heap fragmentation.

### What the next failure means

After the first-pass collector landed, a longer off-screen run moved farther and then failed later in scheduler/process switching. Importantly, the later panic reported `gcCount=0`, which means:

- the new later failure is not caused by the first-pass collector
- it is a separate interpreter/scheduler bug that had previously been masked by the earlier storage-management limit

That is healthy project progress. The VM is not “done,” but the failure surface is getting more honest.

## Major implementation phases so far

### Phase 1: image loading and basic interpreter bring-up

The earliest milestone was simply reaching the point where the image loaded, object addressing worked, and bytecodes could be dispatched against the real image.

By the time `ST80-001` was documented, the project already had:

- correct image loading with segment addressing
- all bytecodes dispatched
- arithmetic primitives
- method lookup with cache
- context creation and switching
- initial trace validation against `trace2`

That sounds impressive, but the runtime was still brittle. It had early context corruption and a large surface of stubbed primitives.

### Phase 2: early-boot semantic bugs

The next stretch of work was not about adding broad new subsystems. It was about eliminating a series of very precise semantic bugs that prevented the image from surviving real startup.

#### Tagged SmallInteger header decode bug

This was one of the most important fixes.

Problem:

- method headers, header extensions, and class instance specifications were being decoded incorrectly because tagged SmallInteger representation was not being handled properly

Effect:

- startup context sizing and metadata interpretation were wrong
- the VM hit the earlier startup context overflow

Fix:

- decode those metadata words as SmallInteger payloads first, then interpret the bit fields

Result:

- the immediate startup context overflow frontier disappeared

This is a good example of what this project is really about. The bug was not "Go crashed." The bug was "the VM forgot that even metadata words are still SmallInteger-encoded objects in the image."

#### Method cache hash translation bug

Problem:

- the translation of the Blue Book method-cache hash into the implementation’s indexing scheme was wrong

Effect:

- unrelated selector/class pairs aliased to the same cache slots
- cached lookups could return the wrong method

Fix:

- correct the Blue-Book-to-code hash translation

Result:

- cached selector/class lookup stopped corrupting dispatch
- the VM could run much longer, including clean 2,000,000-cycle runs

This is one of the clearest cases where a bug looked initially like "some send later went wrong" but was actually a very low-level VM invariant violation.

#### `become:` and typed allocation

The next major expansion introduced:

- `become:`
- typed pointer/word/byte allocation

Why it mattered:

- the image uses `become:` for real system behavior
- allocation shape matters for forms, arrays, and raw storage

This also moved the runtime frontier into more display-adjacent behavior, which in turn exposed the next class of integer-decoding bugs.

### Phase 3: context lifetime, block/value behavior, and allocation reuse

Once early bring-up and obvious missing primitives were addressed, the next bugs became harder:

- block/value corruption
- later send failures
- object-space growth suspicion
- context-body reuse mistakes

This is the phase where the project stopped being a toy interpreter and started becoming a real VM debugging project.

#### Block/value register handling and `String>>at:put:`

This slice fixed:

- block/value register handling
- `String at:put:`
- structural context checks
- guarded `MethodContext` OOP-slot recycling

That pushed the failure much later in execution, which is exactly what one wants in this kind of project. The frontier moved from startup to a late-runtime corruption around cycle `708768`.

#### Late `blockCopy:` / `value:` corruption

At that point the key diagnosis was:

- the receiver of a later `value:` send was already invalid immediately after `blockCopy:`

That was important because it narrowed the problem. The bug was not the visible late send. The bug was already present in the created block/context object.

#### Context body reuse and segment-wrap hardening

The decisive improvement here was pragmatic memory management for contexts:

- explicit reuse of freed context bodies
- tracking retired bodies for exact-shape reuse
- reserved recycled context OOPs
- segment-wrap guards
- stronger context-shape checks

This did **not** produce a full garbage collector, but it eliminated the concrete late corruption frontier that had been blocking progress.

This is a good place to state the project’s current storage-manager posture clearly:

- there is memory management work
- there is not yet a full Chapter 30 storage manager
- the implemented reuse logic is tactical and correct enough for the current runtime frontier, not the finished final answer

### Phase 4: closing long-run primitive gaps

Once the VM could survive longer runs, several primitives that had previously been "later" became immediate blockers.

Important fixes in this phase included:

- `perform:`
- `perform:withArguments:`
- `beCursor`
- `cursorLink:`
- correct `asOop`
- correct `asObject`

These are not glamorous, but they mattered because the image began falling into notifier/debugger behavior when the primitives were missing or semantically off.

The consequence of fixing them was significant:

- the old notifier/debugger path disappeared
- the image reached a stable low-priority scheduler loop

That is a genuine VM milestone.

### Phase 5: real BitBlt rather than a fake "success"

This sits near the display boundary, but it is still fundamentally VM work because `primitiveCopyBits` is part of the interpreter’s primitive surface and depends heavily on correct Blue Book field ordering and object representation.

The project went through three relevant stages:

1. a temporary headless `copyBits` success path just to remove a notifier/debugger frontier
2. a real in-memory BitBlt implementation
3. a series of BitBlt correctness fixes based on actual field order and source-form assumptions

Important bugs here included:

- assuming `Form bits` had to be a `DisplayBitmap` instead of accepting legal non-pointer word objects such as `WordArray`
- reading `BitBlt` fields in the wrong order

These are classic Blue Book reconstruction bugs:

- wrong class-shape assumption
- wrong slot ordering

Both are easy mistakes if the design is not constantly grounded in the spec.

## The most important bug pattern discovered so far

One recurring project pattern is:

> a primitive semantically expects a non-negative integer, but the implementation accidentally only accepts SmallInteger arguments

The clearest version of this was the designated display allocation bug.

Problem:

- startup performs `DisplayBitmap new: 19200`
- `19200` is outside the image’s SmallInteger range
- primitive `71` originally only accepted SmallInteger sizes

Effect:

- the designated display was allocated incorrectly
- the framebuffer shape was wrong

Fix:

- add proper positive-integer decoding and widen the obvious size/index primitives to use it

Why this matters beyond that one bug:

- it is a general VM audit pattern
- it is exactly the kind of mismatch a spec-faithful implementation needs to hunt systematically

This project now has a clearer distinction between:

- primitives that are genuinely SmallInteger-only
- primitives that should accept any non-negative integer representable as SmallInteger or LargePositiveInteger

That distinction is one of the best examples of the project maturing from "roughly working" to "semantically careful."

## Blue Book verification work

The Blue Book is no longer only being read informally. The project now also has a structured OCR/audit workflow.

The intern-produced OCR pack under:

- `ttmp/2026/03/18/ST80-003--smalltalk-80-graphical-ui-host-window-and-event-loop/reference/ocr-bluebook/`

now includes:

- class layout tables
- method-signature extraction
- primitive audit tables
- display/BitBlt audit notes
- object-memory audit notes

The post-OCR verification pass confirmed that the current code’s important class-layout and field-order constants match the extracted Blue Book material for:

- `Point`
- `Rectangle`
- `Form`
- `BitBlt`

That matters because field-order bugs have already occurred in this project. Having an audit artifact that can be checked mechanically is a real improvement.

## Current implementation boundaries

### What is implemented well enough to matter

- image loading
- object table access
- object-space access
- SmallInteger encoding/decoding
- class lookup
- compiled method header decoding
- bytecode dispatch
- message sending
- method cache
- context activation and return
- basic scheduler/semaphore machinery
- many important primitive families
- real BitBlt semantics
- snapshot writing

### What is implemented in a pragmatic rather than final form

- object reuse and context-body reclamation
- some storage-management behavior that substitutes for a fuller GC/compaction story
- some I/O/input plumbing that exists mainly to let the image proceed rather than to claim complete host integration

### What is still obviously incomplete

- a full Blue Book object-memory implementation with free-chunk management and compaction
- a real general collector rather than targeted reclamation tactics
- full primitive completeness across all categories
- a final interpreter audit proving there are no more subtle field-order or argument-order mismatches in the remaining primitive surface

## What the project has learned about the Blue Book

One useful lesson from this repository is that the Blue Book is precise, but not forgiving.

The mistakes that actually mattered were usually small:

- decoding a tagged SmallInteger as if it were already an untagged bitfield
- translating a bit numbering or hash rule incorrectly
- assuming a field order from memory instead of from the text
- assuming "integer argument" meant "SmallInteger argument"
- assuming a word object had to be of one class shape instead of another equivalent representation

Those bugs do not announce themselves at the source. They reappear later as:

- wrong context sizes
- bogus sends
- impossible block objects
- display corruption
- stable but incorrect scheduler behavior

So the real discipline of this project is not "write a lot of code." It is "keep the implementation close enough to the specification that later image behavior can still be reasoned about."

## Important repo-local reference material

The most useful repo-local references right now are:

- `data/bluebook-spec-notes.md`
- `data/trace2`
- `data/trace3`
- `data/class.oops`
- `data/method.oops`

Important ticket writeups for later review:

- `ttmp/2026/03/17/ST80-002--smalltalk-80-interpreter-continuation-context-recovery-and-io-path/reference/02-tagged-smallinteger-header-decode-bug-writeup.md`
- `ttmp/2026/03/17/ST80-002--smalltalk-80-interpreter-continuation-context-recovery-and-io-path/reference/03-method-cache-hash-collision-writeup.md`
- `ttmp/2026/03/17/ST80-002--smalltalk-80-interpreter-continuation-context-recovery-and-io-path/reference/04-context-body-reuse-and-segment-wrap-writeup.md`
- `ttmp/2026/03/17/ST80-002--smalltalk-80-interpreter-continuation-context-recovery-and-io-path/reference/07-real-bitblt-wordarray-source-form-bug-writeup.md`
- `ttmp/2026/03/18/ST80-003--smalltalk-80-graphical-ui-host-window-and-event-loop/reference/02-displaybitmap-new-largepositiveinteger-size-bug-writeup.md`
- `ttmp/2026/03/18/ST80-003--smalltalk-80-graphical-ui-host-window-and-event-loop/reference/04-bitblt-field-order-bug-writeup.md`
- `ttmp/2026/03/18/ST80-003--smalltalk-80-graphical-ui-host-window-and-event-loop/reference/10-blue-book-ocr-verification-pass.md`

If someone needed to reconstruct the project’s actual VM story, those documents would matter more than a generic README.

## Near-term VM work

The most important remaining VM-facing work is not "make the SDL shell nicer." It is:

1. continue the systematic Blue Book audit across the remaining primitive and object-memory surface
2. decide how far to go toward a fuller Chapter 30 storage manager
3. keep tightening the distinction between:
   - temporary host integration work
   - true VM semantic correctness
4. keep converting one-off debugging discoveries into lasting regression tests

That last point is probably the project’s strongest habit so far. The implementation has improved because major bugs were not merely fixed; they were written up, reduced, and then pinned with tests.

## The real project status in one sentence

This repository is no longer "an interpreter skeleton with many stubs." It is now a real, Blue-Book-driven Smalltalk-80 VM implementation whose remaining problems are mostly about semantic completeness, storage-manager fidelity, and careful audit of the parts that are easiest to get subtly wrong.

## Working rule

> [!important]
> When behavior diverges, assume a specification mismatch before assuming the image is strange.
> In this project, the winning debugging move has usually been to go back to representation details: tag bits, field indices, argument shape, header format, or object class/size assumptions.

## Related KB entries

These knowledge base entries provide orientation for the concepts this project depends on:

- [[Tribal/goja-embedding-in-go]] — goja is our standard JS interpreter; this project's spec-first discipline contrasts with goja's pragmatic embedding approach
- [[On-Ramp/wasm-from-go]] — if this VM were browser-deployed, it would follow the Go→WASM patterns documented here

**Tribal candidates** (our-specific patterns not yet at 3-project threshold):
- Spec-first implementation discipline (1/3) — building from a formal specification instead of referencing another implementation as an oracle
- Regression-trace-driven debugging (1/3) — comparing VM execution against known-good image traces to find divergence
- Go struct packing for VM word formats (1/3) — mapping Smalltalk's object-pointer encoding onto Go structs

## KB reviews

- [[KB-BATCH4-embedded-hardware]] (2026-05-11) — concept extraction + classification

## Related KB entries

- [[Tribal/goja-embedding-in-go]] — contrast: spec-first discipline vs pragmatic embedding
