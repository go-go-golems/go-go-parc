# Building OS and Browser

- URL: https://chatgpt.com/c/6a708c1b-4684-83ea-8f5f-46e4eb4afd95
- Created: 2026-08-03T12:40:34.378Z

---

> I would have it explored the space of operating systems until I get a fully working web browser up running on raspberry pi 1. Including OS and whatever it takes. But it needs to be usable at 400 MHz
>
> —-
>
> What would it take to do that, and rethink everything. No reuse of any code, this is from the ground up rethinking what computer software / os / apps are

<details><summary>💭 Thinking</summary>

**Reframing the browser**

I’m treating this as a ground-up research challenge, not a normal port. A fully modern browser on Raspberry Pi 1 hardware is impractical, so I’m defining realistic compatibility tiers and a radically smaller architecture.

</details>

I’ll break this into feasibility, a clean-slate architecture, the minimum browser stack, and a staged path that can actually run at 400 MHz.

```json
{"system1_search_query":[{"q":"site:raspberrypi.com Raspberry Pi 1 Model B specifications ARM1176JZF-S 700 MHz RAM official"},{"q":"site:raspberrypi.com documentation Raspberry Pi boot process bootcode start.elf BCM2835 official"},{"q":"site:html.spec.whatwg.org HTML Living Standard scripting DOM networking browser requirements"},{"q":"site:rfc-editor.org RFC 8446 TLS 1.3 RFC 9110 HTTP Semantics RFC 9113 HTTP/2"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 15 websites**

**Shaping the architecture**

I’m drawing a firm boundary: original ARM-side software is realistic, but replacing immutable boot firmware isn’t. I’m targeting a lightweight, standards-focused browser with carefully measured features, memory budgets, and progressive implementation stages.

**Shaped the architecture**

</details>

```json
{"system1_search_query":[{"q":"site:web-platform-tests.org official Web Platform Tests browser interoperability test suite"},{"q":"site:github.com/web-platform-tests/wpt official browser test suite"},{"q":"site:test262.report ECMAScript conformance suite official Test262"},{"q":"site:tc39.es/ecma262 ECMAScript language specification current"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 14 websites**

</details>

## Feasibility

A clean-slate operating system and browser can be built for Raspberry Pi 1. A **fully compatible, entirely local modern browser that remains responsive at 400 MHz**, while reusing no existing implementation code, is a substantially different proposition. That combination is closer to a long-term browser-engine research program than an operating-system project.

The Raspberry Pi 1 uses the BCM2835 with one ARM1176JZF-S core. Its documented default ARM clock is 700 MHz, with a 250 MHz core clock and 400 MHz SDRAM clock. Running the CPU at 400 MHz therefore gives you considerably less than the already-limited nominal performance. citeturn947923search5turn981313search0

The four requirements cannot all remain absolute:

1. Broad compatibility with today’s web.
2. All execution local to the Pi.
3. Usability at 400 MHz.
4. No reused implementation code.

You can achieve any three reasonably. Achieving all four would require a large team, many years, and continued maintenance as the web changes.

## First define “no reuse”

A literal interpretation is impossible on a stock Raspberry Pi 1. The BCM2835 executes immutable boot ROM code, and the normal boot path loads precompiled VideoCore bootloader and GPU firmware. The official firmware repository explicitly distributes precompiled bootloader/GPU firmware. The public BCM2835 documentation also omits some GPU-controlled peripherals, making a complete replacement firmware partly a reverse-engineering project. citeturn863896search13turn601814view0

A workable clean-slate rule would be:

> No source code or target-side executable code from an existing OS, browser, runtime, library, driver, or application is incorporated into the new system. Published specifications, test suites, protocol vectors, hardware ROM and optionally the stock Pi boot firmware are treated as external interfaces.

That still permits:

- Reading ARM, Broadcom, IETF, WHATWG, Ecma and W3C specifications.
- Using externally defined data such as Unicode tables, root certificates and fonts.
- Initially using an existing development computer, editor and compiler as construction tools.
- Writing every shipped component yourself.

A stricter second stage could replace `bootcode.bin`, `start.elf`, the compiler, assembler and linker. The immutable BCM2835 ROM would remain.

## The central rethink: the browser is the operating system

Do not build a general-purpose Unix replacement and then place a browser on top. That recreates layers that consume memory, CPU and engineering time without helping the target use case.

Build an **interactive document machine**:

```text
BCM2835 ROM / minimal firmware
          ↓
small protection kernel
          ↓
hardware, storage and network brokers
          ↓
document runtime and JavaScript VM
          ↓
retained scene graph
          ↓
tile renderer and framebuffer
```

There is no desktop, terminal subsystem, package manager, POSIX layer, shell, conventional filesystem hierarchy or general application ABI.

The system boots directly into the browser interface.

### Kernel

The kernel should do only:

- Address-space isolation.
- Interrupt and timer handling.
- Memory-page ownership.
- Capability validation.
- Shared-memory message queues.
- Crash detection and process restart.

Avoid `fork`, signals, file descriptors and a large syscall interface. Use typed handles such as:

```text
DisplaySurface
NetworkStream
StoredObject
InputChannel
Timer
SharedRegion
```

A component can only use a resource if it possesses its capability.

Use several protection domains rather than one monolithic binary:

- Browser chrome and input.
- Network and TLS broker.
- Page renderer and script VM.
- Storage broker.
- Kernel and drivers.

A hostile or broken page may destroy its renderer, but not the URL bar, credentials, network policy or stored data.

### Storage

Replace the conventional filesystem with an append-only typed object store.

Objects would include:

- Browser configuration.
- Page cache entries.
- Cookies and origin state.
- History records.
- Certificates and trust data.
- Frozen page states.
- System images.

Use immutable objects, checksums and atomic root-pointer updates. This reduces SD-card corruption, eliminates directory traversal code and makes rollback straightforward.

Updates become complete, signed system images rather than packages.

### Scheduling

Use an event reactor, not a collection of permanently runnable threads.

Each component receives small execution budgets. Work is represented as resumable state machines:

```text
receive bytes
parse some tokens
recalculate affected layout
paint damaged tiles
wait
```

The browser UI must be in a different protection domain from page scripts. HTML scripting normally has run-to-completion semantics, so a large script cannot simply be allowed to interleave observably with unrelated page events. The VM can be internally suspended at safe points, but page-visible event ordering must remain intact. citeturn651644search36

## Hardware work

The minimum original driver stack is still substantial:

- ARM startup, exception vectors, caches and MMU.
- Timers and interrupt controller.
- UART for debugging.
- SD-card controller.
- Framebuffer and display mailbox.
- USB host controller.
- USB hub enumeration.
- USB keyboard and mouse.
- Ethernet controller.
- Optional audio.
- Power and clock management.

On a Raspberry Pi 1 Model B, Ethernet is connected through the LAN9512 USB hub/Ethernet device. That means networking requires a working USB host stack, hub driver and LAN95xx driver before the first packet can be sent. citeturn429153search24turn429153search7

For early development, it would be rational to avoid that dependency:

- Debug through UART.
- Use an SPI Ethernet module or serial network bridge.
- Use GPIO or serial input.
- Implement the BCM2835 USB host stack later.

That gets the browser architecture running before spending months debugging USB transfers.

## Network and security stack

A useful HTTPS browser needs much more than TCP:

- Ethernet framing and ARP.
- IPv4, then IPv6.
- DHCP.
- DNS.
- TCP congestion control and retransmission.
- A trustworthy wall-clock policy.
- TLS 1.3.
- X.509 and ASN.1 parsing.
- Certificate-chain and hostname validation.
- Root-store updates.
- HTTP caching, redirects, cookies and authentication.
- Content decompression.
- HTTP/1.1 and eventually HTTP/2.

TLS 1.3 is defined to protect against eavesdropping, tampering and forgery. HTTP semantics are shared between protocol versions, while HTTP/2 adds multiplexing and compressed headers. citeturn651644search16turn651644search11turn651644search10

For the first release:

- Implement HTTP/1.1 only.
- Pool and reuse connections.
- Support TLS 1.3 and the necessary TLS 1.2 compatibility.
- Implement SHA-256, HKDF, AES-GCM and ChaCha20-Poly1305.
- Support the certificate signature and key-exchange algorithms actually needed by the target site corpus.
- Add HTTP/2 only after profiling proves that connection concurrency is a major limitation.
- Do not implement QUIC or HTTP/3 initially.

Original cryptography is one of the highest-risk parts of the project. It would require independent review, differential testing, protocol test vectors, fuzzing and constant-time analysis. “It connects to HTTPS” is not equivalent to “it is secure.”

## The browser engine

The operating system is the smaller half. The browser dominates the project.

### HTML and DOM

HTML is not an XML-like tree parser. The specification defines detailed recovery behavior for malformed documents, and websites depend on it. citeturn651644search15

Use:

- A streaming tokenizer.
- A compact tree builder.
- Integer node identifiers rather than pointer-heavy objects.
- Arena allocation by document lifetime.
- Interned tag, attribute and property names.
- Lazy construction of rarely accessed DOM properties.
- Separate semantic, layout and paint trees.

Do not keep five redundant object models of the same page.

### CSS and layout

A serious compatibility target eventually needs:

- Cascading, inheritance and specificity.
- Selectors and pseudo-classes.
- Block and inline layout.
- Floats and positioning.
- Flexbox.
- Grid.
- Media queries.
- Transforms and clipping.
- Font metrics and line breaking.
- Incremental style and layout invalidation.

The key architectural decision is to compile styles into compact matching programs. A DOM mutation should identify a bounded set of affected nodes, not trigger complete restyling and layout.

### Graphics

Use a retained, tiled scene graph rather than immediate painting.

Recommended first target:

- 800×600 or approximately 1024×600.
- RGB565 rather than 32-bit RGBA where transparency is unnecessary.
- 32×32 or 64×64 damage tiles.
- One front buffer and a small tile cache rather than permanent full-screen triple buffering.
- Integer geometry where practical.
- Precomputed glyph masks.
- Image decoding at display resolution rather than full source resolution.
- No desktop compositor.

Scrolling should normally move cached tiles and render only newly exposed regions.

Do not begin with OpenGL. A small software renderer at modest resolution is simpler and predictable. VideoCore acceleration can be researched after the complete pipeline works.

### JavaScript

The current published language specification alone is extensive, before browser APIs are considered. Ecma publishes ECMAScript 2026, while TC39’s Test262 suite contains tens of thousands of conformance files. citeturn375401search2turn965721search0

A 400 MHz first implementation should use:

- Parser to compact bytecode.
- Direct-threaded or token-threaded interpreter.
- Superinstructions for common operation sequences.
- Hidden-class or shape-based object layouts.
- Monomorphic and polymorphic inline caches.
- Compact 32-bit tagged values.
- Incremental or generational garbage collection.
- Hard per-origin memory limits.
- VM safe points.
- No JIT initially.

A JIT would improve computation-heavy sites, but it introduces executable-memory management, code generation, cache coherency, security exposure and a second optimizer project. It is not a first-version feature.

The larger problem is not ECMAScript syntax. It is the browser environment:

- Events.
- Timers.
- Fetch.
- Promises.
- DOM mutation.
- URL handling.
- Forms.
- Cookies.
- Storage.
- Canvas.
- Workers.
- Streams.
- History and navigation.
- Security policies.
- Accessibility.
- Numerous other Web APIs.

## Performance contract for 400 MHz

“Usable” must be a measured contract, not a subjective description.

A credible initial contract would be:

| Property | Target |
|---|---:|
| CPU clock | Fixed 400 MHz during all acceptance tests |
| Supported RAM | Design around a 256 MB ceiling |
| Display | 800×600, 16-bit |
| Live pages | One |
| Frozen background pages | Zero to two |
| System working set | Under 128 MB |
| Input acknowledgement | Under 80 ms |
| Cached scrolling | 20–30 frames/s |
| Browser chrome | Never blocked by page script |
| Lightweight page first paint | Under 3 seconds, excluding slow network |
| Recovery after renderer crash | Under 1 second |

These are design targets, not predictions.

The implementation rules should be:

- Never repaint the entire screen unless required.
- Never parse, decode or lay out invisible material eagerly.
- Never retain decoded images larger than their displayed size without a reason.
- Never allow unbounded DOM, script heap, history or caches.
- Freeze or discard inactive pages.
- Prefer sequential memory scans over pointer-rich structures.
- Use arenas and lifetime regions in all non-JavaScript components.
- Measure every allocation and every full-layout operation.
- Keep browser chrome independent from content execution.
- Make resource exhaustion a normal, handled condition.

At 400 MHz, work avoidance matters more than sophisticated instruction-level optimization.

## Rethinking “applications”

Local applications should not be native executable programs.

They should be declarative documents plus state machines:

```text
semantic interface
+ persistent typed state
+ event transitions
+ explicit capabilities
+ optional verified bytecode
```

The same rendering system serves both local tools and web content.

A calculator, settings panel or file viewer would not launch a process with a private toolkit. It would instantiate a document and grant it specific capabilities.

That produces a different computing model:

- No installation scripts.
- No globally shared libraries.
- No arbitrary device access.
- No implicit ambient authority.
- No application-specific UI toolkit.
- No package dependency graph.
- No hidden background services.

The web compatibility layer becomes one translator into this internal model. The internal system itself does not need to imitate the web.

## The only credible route to broad modern-web usability

For arbitrary current websites, heavy JavaScript is the central performance barrier. A clean-slate interpreter on an ARM1176 at 400 MHz will not make large commercial web applications pleasant.

The radical solution is a **split browser**:

### On the Pi

- URL bar and security UI.
- Input handling.
- Semantic accessibility tree.
- Tile renderer.
- Text selection.
- Local cache.
- Password and credential broker.
- Scene-delta protocol.

### On a more powerful machine

- HTML, CSS and JavaScript execution.
- DOM and layout.
- Complex image and font decoding.
- Compatibility processing.

The remote side sends a compressed scene graph, semantic tree and changed tiles—not merely a video stream. The Pi retains local interaction, selection, accessibility and browser security indicators.

This does not reduce the clean-slate engineering needed for standards compatibility, but it removes the 400 MHz execution constraint. It is the most plausible architecture for “works with nearly every website” and “feels usable.”

Without a relay, the honest target is a **lean web browser**: documents, forms, modest JavaScript, images and selected web applications—not the entire modern web.

## Testing defines “fully working”

Do not use a statement such as “supports HTML5.” Maintain a versioned compatibility contract.

Use:

- Web Platform Tests for HTML, DOM, CSS and Web APIs.
- Test262 for ECMAScript.
- IETF protocol vectors.
- Parser and decoder fuzz corpora.
- A fixed representative site suite.
- Visual reference tests.
- Performance and memory tests on physical Pi hardware at 400 MHz.

Web Platform Tests exists specifically as a cross-browser compatibility suite. citeturn375401search0

A release could be defined as:

- Passes specified WPT directories.
- Passes a specified ECMAScript edition subset.
- Loads 100 named sites with documented feature expectations.
- Never exceeds the memory contract.
- Maintains input responsiveness under hostile pages.
- Survives malformed network, image, font, HTML and script inputs.

## Estimated effort

The following are planning estimates, not measured industry figures.

For a team of **six to ten senior systems, browser and security engineers**:

| Stage | Calendar estimate |
|---|---:|
| Boot, development protocol, kernel and memory system | 3–9 months |
| Display, storage, input and basic drivers | 6–12 months |
| Ethernet, TCP, TLS and HTTP | 9–18 months |
| Static HTML/CSS browser with forms | 18–30 months |
| DOM, JavaScript, cookies, storage and security model | 30–54 months |
| Broad site compatibility and serious optimization | 5–8 years |
| Standards, security and compatibility maintenance | Permanent |

For one highly capable developer:

- A clean-slate static browser could take three to five years.
- A useful JavaScript browser could take considerably longer.
- Broad current-web compatibility would probably remain a moving target beyond ten years.

The browser, not the kernel, determines the program’s scale.

## Recommended project definition

The most coherent version of the project is:

> Build a clean-slate interactive document operating system for BCM2835, with a locally executed lean web engine, an optional compatibility relay for demanding pages, one live document at a time, a strict 256 MB memory contract, and all performance qualification performed at a fixed 400 MHz.

The first concrete milestone should not be “boot an OS.” It should be:

> Power on, display a local structured document, accept keyboard and pointer input, update only damaged tiles, persist state atomically, and remain responsive at 400 MHz—with no POSIX layer and no imported target code.

That milestone tests the new computing model before the project becomes consumed by web compatibility.


---

> While we have no reusable foundation, how would you parallelize the development so that we can work on higher up parts of the stack without needing to first do all the lower layers

<details><summary>💭 Thinking</summary>

**Designing development foundations**

I’m organizing the architecture around shared contracts, deterministic simulation, and conformance tracing. Hosted and bare-metal backends can support parallel work, while versioning, capability discovery, and frequent hardware feedback reduce interface ossification.

**Designed development foundations**

</details>

The key is to make the **specification, simulator, and test harness** the first shared foundation—not the kernel or hardware drivers. Every subsystem then targets contracts that have both hosted and bare-metal implementations.

<details><summary>💭 Thinking</summary>

**Structuring the implementation**

I’m planning a staged design with a versioned machine contract, deterministic host runtime, reference models, and trace-based conformance tests. Higher-level components should depend on typed services, while hardware adapters remain replaceable and empirical feedback keeps abstractions grounded.

**Structured the implementation**

</details>

# Parallelize by defining contracts before implementations

Do not organize the project as:

```text
hardware → kernel → drivers → networking → browser
```

That forces most engineers to wait.

Organize it as replaceable components connected through executable contracts:

```text
                        ┌─ Hosted adapters
Component contracts ───┼─ Deterministic simulators
                        └─ Bare-metal implementations
```

Every higher-level component initially runs against a hosted or simulated implementation. The bare-metal teams replace those implementations without changing browser code.

The shared foundation is therefore not reusable OS code. It is:

1. Interface specifications.
2. Message formats.
3. Deterministic test fixtures.
4. Resource and performance contracts.
5. A component test environment.

## 1. Separate final code from development scaffolding

“No reused code” should apply to the shipped system. Development scaffolding can use an existing workstation OS and compiler without becoming part of the Raspberry Pi software.

Each component should have two parts:

```text
┌─────────────────────────────────┐
│ Pure component core             │
│ Parsers, state machines, VM,    │
│ layout, protocol logic          │
├─────────────────────────────────┤
│ Small environment adapter       │
│ Memory, time, I/O, events       │
└─────────────────────────────────┘
```

The component core must never call Linux, POSIX, libc or firmware APIs directly.

During development, the adapter maps your interfaces onto the host machine. On the Pi, another adapter maps them onto your kernel. The component itself is unchanged and consists entirely of original project code.

For maximum enforcement, compile higher-level code as freestanding code from the beginning:

- No host headers.
- No host filesystem calls.
- No host threads.
- No host sockets.
- No implicit allocator.
- No system clock access.
- No ambient global services.

Only the small hosted adapter is allowed to interact with the development machine.

## 2. Define a small platform contract

Create a project-specific machine interface. Do not emulate Unix.

A useful initial contract might expose:

```text
PageAllocator
SharedRegion
MessageChannel
TimerQueue
EntropySource
InputStream
TileSurface
FramePort
BlockDevice
CrashReporter
```

These interfaces must describe behavior, not implementation.

For example, the display contract should not expose Broadcom mailbox calls. It should expose operations such as:

```text
create_surface(width, height, format)
begin_frame()
submit_tile(x, y, pixels)
commit_damage(rectangles)
```

A host adapter can display those tiles in a workstation window. The Pi adapter can copy them into a framebuffer. The browser renderer does not know which one it is using.

The same applies throughout the stack:

| Final dependency | Early substitute | Stable contract |
|---|---|---|
| Pi framebuffer | Host window or image output | Tile surface |
| USB keyboard and mouse | Recorded event script | Input event stream |
| Ethernet controller | Virtual packet link | Raw frame port |
| SD card | Memory-backed block array | Block device |
| Hardware timer | Deterministic logical clock | Timer queue |
| Kernel isolation | Host processes or fault injection | Channels and capabilities |
| Network stack | Synthetic fetch server | Fetch request/response |
| Font engine | Synthetic fixed-metric font | Font measurement service |

This lets every team begin almost immediately.

## 3. Build a deterministic laboratory runtime

The first executable system should be a small development runtime on the workstation. It is not an OS emulator. It is a controller for your components.

It should provide:

- Logical time that advances only when instructed.
- Deterministic input and packet playback.
- Seeded entropy.
- Memory quotas.
- Message recording.
- Component restart and failure injection.
- Trace capture.
- The ability to substitute real or simulated components independently.

A complete browser session should be reproducible:

```text
initial image
+ network transcript
+ input event transcript
+ timer transcript
+ entropy seed
= identical result
```

This is critical because several teams can reproduce the same defect without sharing the same hardware setup.

The runtime should support mixed configurations:

```text
real HTML parser
real JavaScript VM
simulated network
simulated storage
host display
```

Later:

```text
real HTML parser
real JavaScript VM
real network
real storage
Pi framebuffer
```

Each simulated component is replaced independently.

## 4. Parallel workstreams

A practical division would look like this.

### Platform and kernel

This team defines the component runtime ABI and implements:

- Boot.
- MMU and memory ownership.
- Timers and interrupts.
- Channels and capability handles.
- Shared memory.
- Component startup and recovery.

Its first deliverable is not a complete kernel. It is the formal behavior of the runtime interface, followed by a minimal Pi implementation that can execute component tests.

### Hardware

This team works independently on:

- UART.
- Framebuffer.
- SD.
- USB.
- Ethernet.
- Input devices.
- Clock and power control.

Every driver must also have a host-side model and a device test protocol. The team can validate drivers using small standalone programs long before the browser boots.

### Document engine

This team works entirely against memory buffers and synthetic documents:

```text
byte chunks
→ HTML tokens
→ tree mutations
→ document model
```

Its outputs are deterministic tree snapshots and mutation traces.

It does not need networking, storage, display hardware or a kernel.

### CSS and layout

This team consumes a standardized document model and synthetic font metrics:

```text
document + stylesheets + viewport
→ computed styles
→ layout fragments
```

Its first output can be a textual layout dump:

```text
node 12: x=8 y=40 w=320 h=24
node 13: x=8 y=64 w=180 h=16
```

Pixel rendering is not required to develop or test layout.

### Graphics and text

This team consumes display lists:

```text
fill rectangle
clip rectangle
draw glyph run
draw image
transform
```

Initially it renders into a host memory buffer or image file. Later the same renderer writes damaged tiles to the Pi display service.

Text can begin with a deliberately simple project-owned bitmap font. Font parsing and advanced shaping are separate later workstreams.

### JavaScript runtime

The VM team can work independently using:

- Source strings.
- Bytecode tests.
- Synthetic host objects.
- A fake DOM binding layer.
- Deterministic timers and promises.

The initial VM does not need the real DOM. It can use a tiny test object model with operations such as:

```text
get_property
set_property
call_method
create_node
append_child
```

When the document model is ready, the fake binding is replaced.

### Networking and TLS

This team should divide the problem into pure state machines:

```text
Ethernet frames → IP packets → TCP byte stream
TCP byte stream → TLS plaintext stream
TLS plaintext stream → HTTP messages
HTTP messages → Fetch service
```

Each stage can be developed using recorded input and expected output.

TCP does not need a real Ethernet driver. TLS does not need TCP. HTTP does not need TLS. The browser initially talks to a fake Fetch service that returns deterministic page bodies.

### Storage and updates

This team develops the object store against a simulated block device that can:

- Lose writes.
- Corrupt sectors.
- Reorder operations.
- Reset at arbitrary points.
- Enforce SD-card-like write costs.

The browser initially uses an in-memory implementation of the same storage contract.

### Validation and performance

This should be an independent workstream from the beginning, not a final testing phase.

It owns:

- Test formats.
- Trace comparison.
- Fuzzing infrastructure.
- Memory accounting.
- Performance benchmarks.
- Compatibility corpora.
- Crash and corruption injection.
- Physical 400 MHz qualification.

## 5. Use soft and hard component boundaries

Do not turn every module into a separate process. At 400 MHz, excessive serialization and message passing would be expensive.

Use hard protection boundaries only where security or fault containment warrants them:

```text
browser chrome
renderer
network/TLS broker
storage broker
kernel
```

Inside the renderer, use ordinary module interfaces:

```text
HTML parser
DOM
CSS
layout
JavaScript
paint
```

These modules can be developed independently but linked into one renderer component for production.

The internal interface should use stable integer handles and compact arenas rather than general object RPC.

For example:

```text
NodeId
StyleId
LayoutFragmentId
PaintObjectId
```

DOM mutations should generate a journal:

```text
ATTRIBUTE_CHANGED node=42 name=class
CHILD_INSERTED parent=18 child=57
TEXT_CHANGED node=63
```

The style and layout modules consume that journal and recalculate only affected regions.

## 6. Integrate through vertical slices

Do not wait for each subsystem to be complete. Build increasingly real end-to-end slices.

### Slice 1: Local interactive document

```text
embedded document
→ parser
→ document tree
→ basic layout
→ display list
→ host and Pi framebuffer
```

Add scripted keyboard and pointer input.

No network, JavaScript, USB or persistent storage is required.

### Slice 2: Persisted local application

Add:

```text
input
→ document state mutation
→ object store
→ reboot
→ restored state
```

This validates the application model and storage semantics.

### Slice 3: Static remote page

Initially use a fake Fetch service. Then replace it progressively:

```text
fake fetch
→ HTTP over host socket adapter
→ project HTTP
→ project TLS
→ project TCP
→ project Ethernet driver
```

The document engine does not change during those replacements.

### Slice 4: Scripted page

Connect the JavaScript VM to the real document model:

```text
event
→ JavaScript
→ DOM mutation
→ style invalidation
→ layout
→ damaged tiles
```

This is the first major browser integration point.

### Slice 5: Security isolation

Move the renderer, fetch broker and storage broker into separate protection domains while preserving the same contracts.

## 7. Keep 400 MHz visible from the first month

The hosted system will conceal expensive designs. Every team therefore needs two performance paths.

First, build a minimal bare-metal **test executive** early. It only needs:

- UART loading or SD loading.
- Timer measurement.
- A memory arena.
- Result reporting.
- Enough display output for diagnostics.

Higher-level modules should compile as standalone tests that this executive can run on the Pi. The full OS is not required.

For example:

```text
parse 1 MB HTML fixture
match 20,000 CSS selectors
execute 1 million bytecode operations
layout 5,000 nodes
paint 100 damaged tiles
decode one representative image
```

Second, assign explicit budgets to every interface:

| Operation | Example budget |
|---|---:|
| Input-to-chrome acknowledgement | 30 ms |
| Small DOM mutation and repaint | 50 ms |
| One cached scroll step | 33–50 ms |
| HTML parsing | Defined bytes per second |
| JavaScript interpreter | Defined bytecodes per second |
| Full page memory | Fixed maximum |
| One component message | Fixed byte and cycle limit |

A component that passes correctness tests but exceeds its budget is not complete.

## 8. Use reference models and optimized implementations

For difficult subsystems, create two original implementations:

- A simple, obviously correct reference model.
- A compact target implementation.

This is particularly useful for:

- HTML tokenization.
- CSS cascade.
- Unicode decoding.
- Object storage.
- TCP state transitions.
- TLS record handling.
- JavaScript value semantics.

The reference version runs only on the development machine and acts as an oracle. The optimized implementation runs on both the host and Pi.

Both are project-owned code. No reference implementation is shipped.

Avoid creating two complete browser engines. Use dual implementations only for narrow, error-prone algorithms.

## 9. Version interfaces deliberately

Parallel work fails when teams silently reinterpret interfaces.

Every contract should include:

```text
version
message schema
ownership rules
memory limit
ordering guarantees
failure behavior
cancellation behavior
security authority
test vectors
```

Changes should be validated against recorded traces. For a period, the laboratory runtime can support two versions while components migrate.

Do not expose internal implementation details through the contracts. For example, the browser should request a page resource, not request a TCP connection. Otherwise network implementation decisions leak upward and become permanent.

## A sensible first 12 weeks

### Weeks 1–2

Define:

- Component boundaries.
- Machine contract.
- Message encoding.
- Document model.
- Display-list format.
- Fetch interface.
- Storage interface.
- Trace format.
- Performance budgets.

### Weeks 3–6

In parallel:

- Hosted laboratory runtime.
- Bare-metal UART, timer and framebuffer.
- HTML tokenizer and tree builder.
- Basic CSS parser and block layout.
- Software tile renderer.
- JavaScript lexer, parser and bytecode format.
- TCP, TLS and HTTP state-machine skeletons.
- Simulated block device and object store.

### Weeks 7–9

Produce the first local-document vertical slice on both workstation and Pi.

At the same time:

- Run parser, VM and renderer microbenchmarks at 400 MHz.
- Freeze the first interface versions.
- Start malformed-input and failure testing.

### Weeks 10–12

Produce:

- Interactive forms.
- Persisted document state.
- Synthetic network loading.
- Basic script-driven DOM changes.
- Component crash and restart behavior.

At that point, almost every workstream is productive even though USB, Ethernet, TLS, JavaScript and advanced layout remain incomplete.

## The central rule

Every subsystem must be able to receive deterministic inputs and produce inspectable outputs without the rest of the machine.

That means:

```text
drivers receive synthetic hardware events
network layers receive packet transcripts
TLS receives byte transcripts
HTTP receives plaintext streams
browser receives fetch responses
parser receives byte chunks
layout receives document snapshots
renderer receives display lists
storage receives block-operation scripts
```

The project is then integrated by replacing simulations with real components one boundary at a time, rather than waiting for a foundation to be completed from the bottom upward.


---

> What if we want to optimize over the search space of operating systems / browser architectures and discover novel approaches

Treat the OS/browser as a **search problem over architectures**, not a single design effort. I’ll frame the search space, objective function, experimental harness, and mechanisms for generating genuinely new designs.

```json
{"system1_search_query":[{"q":"site:arxiv.org STOKE stochastic superoptimization paper"},{"q":"site:arxiv.org MAP-Elites quality diversity paper"},{"q":"site:dl.acm.org syntax-guided synthesis SyGuS paper"},{"q":"site:arxiv.org Bayesian optimization multi-fidelity systems architecture search"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 13 websites**

**Designing architecture search**

I’m framing this as a research program: define a typed architecture language, search over state placement, representations, scheduling, isolation, caching, and computation location, then evaluate candidates with correctness, security, latency, memory, energy, and complexity constraints.

**Designed architecture search strategy**

**Expanding the search model**

I’m adding an architecture-neutral specification for state, authority, transformations, resources, and deadlines, so search can move boundaries rather than merely tune components. I’ll pair this with generated candidates, semantic oracles, and illustrative hypotheses.

**Expanded the search model**

</details>

```json
{"system1_search_query":[{"q":"Web Platform Tests official documentation browser interoperability test suite"},{"q":"TC39 Test262 official ECMAScript conformance suite"},{"q":"WHATWG HTML living standard event loop parsing official"},{"q":"W3C CSS test suites official"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 20 websites**

</details>

Then the project should not primarily build an operating system. It should build an **experimental system that generates, executes, measures, rejects, and evolves operating-system/browser designs**.

The principal artifact becomes a searchable architecture language plus a physical evaluation laboratory. Particular kernels and browsers are outputs of that system.

# 1. Search over semantics, not familiar components

Do not define the search space using inherited concepts such as:

- Processes
- Threads
- Files
- Sockets
- Windows
- DOM nodes
- Browser tabs
- System calls

Doing that would strongly bias the search toward rebuilding Unix and a conventional browser.

Define the problem in more fundamental terms:

```text
Events arrive.
Information is transformed.
State persists or is discarded.
Pixels and other user-observable outputs are produced.
Authority constrains access.
Resources have finite capacity.
Some outputs have deadlines.
Observable web behavior must be preserved.
```

An architecture is then a graph composed of primitives:

```text
sources       network bytes, input events, clocks
transforms    parse, decode, evaluate, match, lay out, rasterize
state         caches, logs, trees, tables, regions
boundaries    protection, restart, trust, remote/local
schedulers    deadline, priority, demand, batch, event
representations compact arrays, streams, trees, bytecode, tiles
sinks         display tiles, storage commits, network output
```

The search system may discover that several conventional components should be fused, eliminated, duplicated, deferred, moved, or replaced.

## Example architecture genome

A candidate could be represented approximately as:

```text
source NetworkBytes
    → transform DecodeHTTP
    → transform ParseMarkup [streaming=true]
    → state SemanticState [materialization=viewport_demand]
    → transform StyleResolve [incremental=journal]
    → transform Layout [strategy=constraint_fragments]
    → state Scene [retention=visible_plus_margin]
    → transform Raster [tile=32, format=RGB565]
    → sink Display

source Input
    → scheduler InteractionDeadline [budget=50ms]
    → transform Dispatch
    → state SemanticState
```

Each node includes:

- Observable semantics
- Memory ownership
- Authority
- Failure behavior
- Cost model
- Scheduling behavior
- Legal transformations

The candidate is compiled into both a hosted experiment and a Raspberry Pi executable.

# 2. Make boundaries searchable

The most consequential decisions are not local algorithm parameters. They concern where boundaries exist.

The search should be allowed to perform operations such as:

```text
fuse(A, B)
split(A)
move_state(A → B)
duplicate(A)
cache(edge)
remove_cache(edge)
materialize_lazily(state)
recompute_instead_of_store(state)
move_across_protection_boundary(A)
change_representation(edge)
batch(edge)
stream(edge)
specialize(A, workload_class)
replace_exact_with_progressive(A)
```

For example, the search might evaluate whether HTML parsing, style matching and partial layout should be:

- Three independent stages
- One fused streaming stage
- A generic parser followed by page-specific compiled stages
- A demand-driven computation initiated from the visible viewport
- An event-sourced transformation that does not maintain a conventional tree

This is where architectural novelty is more likely to emerge.

# 3. Search at four different levels

Trying to evolve an entire browser as arbitrary machine code would be computationally hopeless. Use progressively narrower search spaces.

## Architecture search

Searches:

- Component topology
- Placement of state
- Protection boundaries
- Local versus remote computation
- Streaming versus retained processing
- Scheduling and resource policy
- Exact versus progressive output
- Generic versus specialized execution

Use evolutionary and quality-diversity methods here.

## Representation and algorithm search

Searches:

- Tree versus array versus event log
- Index structures
- Incremental invalidation methods
- Cache policies
- Memory layouts
- Garbage-collection strategies
- Bytecode formats
- Image and text representations

Equality saturation is useful where transformations preserve semantics because it retains many equivalent alternatives simultaneously rather than committing to one rewrite order. That approach was originally developed to address destructive optimization and phase-ordering problems. citeturn936117academia40turn936117academia39

## Implementation-schedule search

Given a selected algorithm, search:

- Loop ordering
- Fusion
- Tiling
- Buffer sizes
- Prefetching
- Inlining
- Allocation-region sizes
- Dispatch methods
- Data placement

This is closer to compiler auto-scheduling.

## Instruction-level search

Apply stochastic or solver-based superoptimization only to small, hot kernels:

- Pixel blending
- UTF decoding
- Hashing
- Selector matching
- Bytecode dispatch
- Cryptographic arithmetic
- Memory copying

STOKE demonstrated that stochastic search with a combined correctness and performance cost could find short instruction sequences competitive with production compilers and, in some cases, handwritten assembly. It does not imply that stochastic search can invent an entire browser, but it validates the technique at the narrowest level. citeturn363246search0

# 4. Do not reduce the objective to one score

There is no single best system architecture. A design may have excellent scrolling but poor first paint; another may minimize memory but stall on script-heavy pages.

Use hard constraints plus a Pareto objective vector.

## Hard constraints

A candidate is invalid when it:

- Violates supported web semantics
- Crosses an authority boundary improperly
- Exceeds an absolute memory ceiling
- Crashes under required workloads
- Misses a non-negotiable UI deadline
- Incorporates prohibited external code
- Fails to boot or execute at 400 MHz
- Produces nondeterministic externally observable behavior where determinism is required

## Optimization objectives

Measure independently:

```text
p50 and p95 input latency
first useful paint
first interactive state
scroll frame latency
JavaScript throughput
network-to-paint latency
peak and steady-state RAM
bytes read and written
energy per interaction
binary size
restart time
site and standards coverage
failure containment
implementation complexity
```

Do not combine these prematurely.

A quality-diversity archive is preferable to keeping only the globally highest-scoring candidate. MAP-Elites-style methods preserve high-performing candidates occupying different behavioral niches; multi-objective variants can retain a Pareto set within each niche. citeturn363246search3turn363246search23

Possible archive dimensions include:

- Retained state versus recomputation
- Number of protection domains
- Degree of viewport laziness
- Bytes moved per interaction
- Generality versus specialization
- First-paint versus steady-state emphasis
- Local versus delegated computation
- Memory versus CPU use

This might retain one excellent architecture for static documents, another for interactive applications and another for very low-memory operation.

# 5. Use counterexamples to drive correctness

Architecture search must not treat compatibility as a statistical score alone. A browser that passes 99% of tests may fail on one behavior that breaks many real sites.

Use a counterexample-guided loop:

```text
generate candidate
        ↓
run known semantic tests
        ↓
find disagreement or failure
        ↓
minimize the failing input
        ↓
add it permanently to the candidate specification
        ↓
generate or repair candidates
```

This is analogous to counterexample-guided inductive synthesis, where candidate programs are repeatedly refined using inputs that disprove their current behavior. citeturn936117academia41

Correctness oracles should include:

- Small specification-derived reference models
- Project-owned mathematical models
- Metamorphic properties
- Differential observations from existing browsers used only as external oracles
- Web Platform Tests
- Test262
- Fault and security properties

WPT is explicitly designed as a cross-browser test suite for web-platform interoperability, while Test262 is the official ECMAScript conformance suite. Using their tests does not require incorporating another browser’s implementation. citeturn222781search0turn222781search1

For every failure, preserve:

```text
candidate architecture
candidate parameters
workload
logical event trace
memory trace
output difference
physical measurements
random seed
```

A rejected design should contribute information to the next generation.

# 6. Use multi-fidelity evaluation

Executing every candidate as a complete browser on physical hardware would make the search prohibitively slow.

Create an evaluation ladder.

## Fidelity 0: structural rejection

Cost: extremely low.

Check:

- Type and authority correctness
- Cycles and deadlocks visible in the graph
- Impossible memory bounds
- Unsupported semantic combinations
- Obviously excessive data movement
- Missing recovery paths

Most candidates should die here.

## Fidelity 1: analytical estimates

Estimate:

- Allocation volume
- State size
- Copies
- Message count
- Expected cache locality
- Worst-case operation count
- Critical-path length

These estimates need not be perfectly accurate. They only need to reject clearly poor designs.

## Fidelity 2: deterministic hosted execution

Run real original component code against:

- Synthetic documents
- Recorded pages
- Network transcripts
- Input traces
- Simulated faults
- Artificial memory limits

This produces correctness and approximate performance data.

## Fidelity 3: isolated Pi microbenchmarks

Compile selected stages for ARM1176 and measure:

- Cycles
- Cache misses where observable
- Memory use
- Branch behavior
- SD traffic
- Display bandwidth

This corrects inaccuracies in the host cost model.

## Fidelity 4: whole-system physical runs

Only promising candidates receive full tests on a Raspberry Pi fixed at 400 MHz.

## Fidelity 5: prolonged adversarial runs

Finalists receive:

- Malformed inputs
- Resource exhaustion
- Repeated navigation
- Power interruption
- Network loss
- Hostile script
- Storage corruption
- Long-running memory tests

Multi-fidelity Bayesian optimization is designed for this general situation: inexpensive approximate evaluations guide the selection of much more expensive high-fidelity experiments. citeturn363246search9turn363246academia84

# 7. Search for adaptive systems, not just fixed architectures

The best result may not be one static architecture.

Pages differ radically:

- A long article
- A dashboard
- A JavaScript application
- A mostly static form
- An animation-heavy site
- A page with thousands of DOM nodes
- A page dominated by images

Research on parallel browser execution has found that the benefit of parallelism depends on page characteristics and can be outweighed by coordination costs. The broader lesson is relevant even on a single-core target: the best execution strategy depends on the workload. citeturn587354academia36

The search output could therefore be a **policy**:

```text
inspect first 50 ms of page behavior
        ↓
classify workload
        ↓
select architecture parameters
```

Parameters might include:

- Streaming or retained parsing
- Amount of DOM materialization
- Layout invalidation strategy
- Image decoding policy
- Garbage-collection mode
- Script time budget
- Cache allocation
- Scene-retention depth
- Degree of component fusion
- Whether to specialize generated code

The search problem becomes:

> Discover a small family of execution architectures and a low-cost controller that selects among them.

That is more plausible than finding one universally optimal pipeline.

# 8. Search should be able to alter observability timing

A conventional browser often treats visual completeness as a single pipeline. At 400 MHz, it may be better to optimize for a sequence of progressively better states:

```text
1. Responsive browser chrome
2. Readable semantic content
3. Operable links and forms
4. Approximate layout
5. Fonts and images
6. Full decorative fidelity
7. Nonessential scripts and animation
```

The final result must preserve required semantics, but the timing of when information becomes available is an architectural degree of freedom.

Potential searchable policies include:

- Render text before complex style resolution
- Reserve approximate geometry and refine later
- Decode low-resolution images first
- Prioritize elements near the pointer or focus
- Construct accessibility and interaction structures before decorative paint
- Suspend nonvisible script-created subtrees
- Defer APIs not involved in the current interaction

The objective should reward **time to useful interaction**, not merely time to a fully completed frame.

# 9. Make memory representation a primary search dimension

On the Raspberry Pi 1, many unexpected gains may come from cache traffic rather than reducing arithmetic.

For example, recent layout work found that a computationally more demanding priority-queue method could outperform conventional traversal by avoiding auxiliary-node accesses and reducing cache stalls. That is exactly the type of counterintuitive tradeoff architecture search should expose. citeturn587354academia38

Searchable representation decisions should include:

- Pointer graph versus compact indexed arrays
- Array-of-structures versus structure-of-arrays
- Persistent tree versus mutation journal
- Full object versus compressed descriptor
- Decoded data versus source plus memoized fragments
- Cached result versus recomputation
- Fine-grained objects versus page-lifetime arenas
- General property dictionaries versus specialized shapes
- Full DOM nodes versus lazy proxy records

The cost model should measure bytes touched, not only operations performed.

# 10. Encourage novelty explicitly

Optimization alone tends to converge on variations of the first adequate family it encounters.

Use several anti-convergence mechanisms.

## Quality-diversity archive

Keep different behavioral families, not just top scores.

## Novelty score

Reward candidates whose execution traces, state distribution or dataflow differ from archived candidates.

## Architectural extinction events

Periodically remove dominant construction patterns and search without them.

Examples:

- No persistent DOM tree
- No protection-domain message passing
- No conventional framebuffer
- No heap garbage collector
- No general-purpose event queue
- No separate layout and paint stages

This does not assert that those restrictions are good. It forces exploration of alternatives.

## Minimal starting candidates

Begin some searches from nearly empty graphs instead of mutating a conventional reference design.

## Independent search populations

Maintain populations with different priors:

- Streaming-first
- Recompute-first
- Transactional-state-first
- Semantic-first
- Specialization-first
- Isolation-first

## Human-generated conjectures

Researchers can propose unusual transformations, but the experiment system determines whether they survive.

A language model may also generate architecture hypotheses or mutation operators, but it should not assign correctness or performance. Those must come from executable tests and physical measurements.

# 11. Candidate novel families worth exposing to search

These are hypotheses, not recommendations.

## Viewport-demand browser

The engine begins from visible and interactive outputs and requests only the semantic dependencies needed to produce them.

```text
visible output
→ required layout fragments
→ required styled elements
→ required semantic nodes
→ required source ranges
```

The complete logical DOM may be represented compactly but only partially materialized.

The main difficulty is preserving JavaScript’s ability to observe arbitrary document state.

## Event-sourced browser state

Instead of maintaining many mutable trees, the system stores:

```text
source
+ mutation log
+ indexes
+ visible derived state
```

Other representations are reconstructed, incrementally maintained or discarded according to cost.

## Page-specialized execution image

After observing a page or site family, the system generates:

- Specialized property shapes
- Compact event dispatch
- Fused style/layout operations
- Direct bytecode for common DOM operations
- A page-specific memory plan

A generic engine remains as the fallback.

## Semantic-first rendering

The first representation is based on meaning and interaction:

- Headings
- Paragraphs
- Links
- Controls
- Tables
- Images
- Navigation regions

Decorative CSS is applied progressively. This could provide a usable page before complete visual fidelity.

## Transactional interaction machine

Every user interaction receives a deadline and resource transaction:

```text
input
→ bounded computation
→ visible commit
→ deferred continuation
```

Page work that cannot complete before the deadline commits a safe partial state and resumes later without blocking browser chrome.

## Per-page synthesized micro-runtime

Instead of booting a generic set of browser services, each page receives a generated runtime containing only the mechanisms its observed behavior requires.

The difficult question is whether specialization cost and compatibility fallback outweigh memory and dispatch savings.

# 12. Separate discovery from production

Search-generated systems can be difficult to understand and maintain.

Every surviving architecture must pass an extraction stage:

1. Reduce the candidate to a minimal equivalent graph.
2. Remove transformations that do not materially contribute.
3. Produce a human-readable architecture explanation.
4. Generate invariants and interface specifications.
5. Re-run all tests without search instrumentation.
6. Confirm performance on independent workloads.
7. Verify that the result is not exploiting a benchmark artifact.
8. Require security review before promotion.

The search engine should preserve lineage:

```text
candidate 1842
derived from 921
mutation: fused style matching with visible layout
mutation: replaced node pointers with 24-bit indices
mutation: removed retained offscreen paint objects
```

This makes the resulting architecture a research result rather than an opaque accident.

# 13. The initial project becomes an architecture laboratory

Before building a full browser, build these six things:

```text
1. Architecture description language
2. Executable semantic contracts
3. Deterministic workload and fault laboratory
4. Candidate compiler for host and ARM1176
5. Multi-fidelity measurement system
6. Quality-diversity and counterexample search controller
```

Then implement only enough original primitives to populate the first search:

- Byte-stream parser
- Compact state store
- Event scheduler
- Elementary layout constraints
- Tile rasterizer
- Small bytecode interpreter
- Message/protection mechanism
- Memory-region allocator
- Block-store model
- Network-stream model

These primitives are not the final architecture. They are the atoms from which architectures are generated.

# Recommended research objective

A suitable formulation would be:

> Discover a family of browser-machine architectures that maximizes useful interactive web behavior on a single ARM1176 core at 400 MHz under a fixed memory ceiling, while satisfying explicit compatibility, authority, recovery and implementation-origin constraints.

The first major experiment should be narrower:

> Search over representations and pipelines for taking an HTML/CSS document plus an interaction trace to damaged display tiles, while varying state retention, pipeline fusion, incrementalization, scheduling and memory layout.

That experiment is large enough to produce genuinely unfamiliar designs, but bounded enough to evaluate thousands of candidates and verify them rigorously. Only after it works should the same machinery expand into JavaScript execution, networking, storage and kernel architecture.

