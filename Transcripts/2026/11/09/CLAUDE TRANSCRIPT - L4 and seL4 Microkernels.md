# L4 and seL4 microkernels

- uuid: 641aba0f-9801-463c-89c3-6798264d2774
- model: claude-opus-5-5


## Human

Literature and papers and textbooks and curriculums about l4 and sel4 and micro kernels


## Assistant

I'll pull together a reading list, checking current course pages and recent papers first.

_[WebSearch]_

_[WebSearch]_

_[WebSearch]_

_[WebSearch]_

_[WebSearch]_

_[WebSearch]_

_[WebSearch]_

_[WebSearch]_

_[WebSearch]_

_[WebSearch]_

_[WebSearch]_

_[WebSearch]_

_[WebFetch]_

_[WebFetch]_

There's no standard textbook on L4/seL4. People learn it from a fairly fixed set of papers and a few public university courses. Here's the list I'd work from.

**Start here**
- **Heiser, "The seL4 Microkernel – An Introduction"**: the free seL4 Foundation whitepaper, currently at revision 1.4 (January 2025).
- **Heiser & Elphinstone, "L4 Microkernels: The Lessons from 20 Years of Research and Deployment"** (ACM TOCS 2016). It's the longer version of their SOSP '13 paper "From L3 to seL4", and it argues that minimality, generality and fast IPC are still the main forces behind the design.

**Classic L4 papers**
- Brinch Hansen, "The Nucleus of a Multiprogramming System" (CACM 1970). It's the original microkernel, from before the term existed.
- Liedtke: "Improving IPC by Kernel Design" (SOSP '93) and "On µ-Kernel Construction" (SOSP '95), plus "Toward Real µ-kernels" (CACM 1996)
- Härtig, Liedtke et al., "The Performance of µ-Kernel-Based Systems" (SOSP '97), the L4Linux paper

**seL4 and verification**
- Klein et al., "seL4: Formal Verification of an OS Kernel" (SOSP '09). At the time the kernel was 8,700 lines of C and 600 of assembler.
- Klein et al., "Comprehensive Formal Verification of an OS Microkernel" (TOCS 2014). It's 70 pages covering the verified IPC fastpath, the proof that the binary matches the C, and access-control enforcement.
- Murray et al., information-flow proof (IEEE S&P '13); Lyons et al., "Scheduling-Context Capabilities" (EuroSys '18, the real-time/MCS model); Ge et al., "Time Protection" (EuroSys '19, timing side channels)

**Recent (2024–26)**
- Heiser, Velickovic, Chubb, "Fast, Secure, Adaptable: LionsOS…" (arXiv 2025). This is the new seL4-based OS, and the paper claims it outperforms Linux. It's also where seL4 gets called the "assembly language of operating systems".
- Chen et al., "Atmosphere: Practical Verified Kernels with Rust and Verus" (SOSP '25). It took under a year and roughly two person-years of effort.
- Proof status: the confidentiality proof is now done for AArch64, and the MCS configuration is proved correct on RISC-V.

**Courses**
- **UNSW COMP9242 Advanced Operating Systems** (Heiser) is the main one. Students build their own OS on seL4. Lecture slides and the project code are public, and lecture videos are on YouTube.
- **UNSW COMP4161** covers the proof side with Isabelle/HOL.
- **TU Dresden, "Microkernel-based Operating Systems"** (Roitzsch). This semester's run began October 13, 2026. It covers L4Re and L4Linux, and its list of papers to read works well as a syllabus.
- **KIT "Microkernel Construction"** (Liedtke's old group). The old pages still have the reading list, including a summary of Liedtke's own 2000 lecture.

**Books and manuals**
- The seL4 Reference Manual and the tutorials at docs.sel4.systems. The Microkit tutorial is the easiest way in.
- Nipkow & Klein, *Concrete Semantics*. It teaches Isabelle/HOL, the proof assistant behind seL4's proofs.
- Feske, *Genode Foundations*. It's free and revised every year, and Genode's Sculpt OS can run on any of 5 kernels.
- Tanenbaum & Woodhull, *Operating Systems: Design and Implementation*, the classic textbook built around a microkernel (MINIX).

If you only read three, read the whitepaper, the TOCS 2016 paper and the SOSP '09 paper, in that order. I can turn this into a doc with links and a suggested reading order if you'd like to keep it.


## Human

How does l4 compare to our own js os? What can each learn from each other?


## Assistant

I'll read through your OS sources, the IDE and the paper first, then compare them to L4.

_[Bash]_

_[TaskCreate]_

_[TaskCreate]_

_[TaskCreate]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Agent]_

_[Read: nucleus.h]_

_[Read: kernel.c]_

_[Read: hw.c]_

_[Read: vm.c]_

_[Bash]_

_[TaskUpdate]_

_[Bash]_

_[Bash]_

_[Bash]_

_[WebSearch]_

_[Bash]_

_[Read: compositor.js]_

_[Read: display.js]_

_[Bash]_

_[Bash]_

_[TaskUpdate]_

_[TaskUpdate]_

Your OS's closest L4 relative isn't classic L4. It's seL4's Microkit/LionsOS stack: a static manifest, single-threaded event-driven components, and mechanism kept in a small kernel. Microkit's three entry points (`init`, `notified`, `protected`) map almost one-to-one onto your `onStart`, `on(...)` and ask/reply. Your book already covers the trusted-code-size trade and sketches endpoint capabilities. So below I've focused on specific seL4 designs that answer the open issues in your Appendix D.

| | seL4 + Microkit | PicoCalc OS |
|---|---|---|
| Isolation | hardware address spaces; ~10K-line proved kernel | one address space; QuickJS (~73K lines of C) is trusted code |
| Who may talk | only with a capability; channels declared in the system file | any world, by name; channels self-declared |
| Kernel memory | no kernel heap | shared fixed tables; unbounded mailboxes |
| CPU | preemptive; budgets throttle | one lane; an overrun is a crash |
| Failure | fault sent to a handler you write | built in: discard effects, restart with backoff |

**What PicoCalc can borrow from seL4**

1. **Make the manifest the whole capability map.** In Microkit, every channel is declared in the system file as two ends naming two components (for example a client and a server, with a channel between them). Declaring channels, and who may send to or ask whom, in `system.json` would close all three authority bugs at once: forged keys, forged frames and the flush confused deputy.
2. **Rule out ask cycles at boot.** In Microkit a call is only possible to a component of strictly higher priority, so the call graph is acyclic and nothing can call itself, even indirectly. Your ask graph nearly obeys this already. compositor→display and keys→keyboard go up in priority; only repl→sandbox and faults→sandbox go down. A boot-time check would turn the two-second A↔B deadlock into a manifest error. That deadlock happens because `pick()` gives no new messages to a world that is in a turn.
3. **Stop sharing kernel pools.** seL4 has no kernel heap: programs hand the kernel memory they own to make kernel objects, so a component can only use up what it was given. Five of your issues are really one problem: the 128 handles, the 1,024 ask slots, the 16 DMA buffers, unbounded mailboxes, and `msg_t` memory that is never counted against any world. The fix is per-world quotas from the manifest and a bounded mailbox that returns an error to the sender.
4. **Bill work to whoever caused it.** seL4's mixed-criticality scheduler lets a server run on its caller's time budget. In your ch. 12 trace the REPL's eval waited 1.6 ms behind other worlds; on an idle lane it takes 119 µs. Because you count steps exactly, charging the callee's segment to the asker (time and priority) is a small change.
5. **One driver per device.** keyboard and power both hold full rights to the STM32 at `i2c0:0x1f`, and the fix for their race is a bus-holding transaction inside the nucleus. LionsOS's sDDF framework instead keeps device virtualisation (sharing a device among clients) in a separate component. A single `stm32` driver world with keyboard and power as its clients removes both the race and the shared rights.
6. **Move supervision policy out of the nucleus.** The backoff schedule and the five-crash rule are hard-coded in `crash_at`. The L4 rule is all resource-management policy at user level. Keep teardown, epochs and effect-discarding in C, and let a supervisor world with `sys.admin` decide restarts per world.

seL4 also dropped IPC timeouts altogether (abandoned in seL4, OKL4). With acyclic asks, yours would only be needed to catch hangs, which is really the turn watchdog you're missing.

**What the L4 world can learn from PicoCalc**

1. **Atomic segments.** A segment's effects apply only when it ends, so a crash leaves nothing half done. seL4 components act as they go, and every restartable server has to design around partial effects.
2. **Failure is a message.** A crashed world's pending asks fail at once with the reason, `worlds.status` announces every crash and restart, and `#OCT1` frames put faults on the UART. seL4 gives you the mechanism and leaves the rest to each system.
3. **Epochs.** Timers and replies meant for a previous incarnation are dropped automatically. seL4 systems that restart components need the same idea, carried in badges or messages.
4. **Deterministic replay.** A calibrated virtual clock, exact step counting and seeded randomness give the same pixels on every run. That's how you caught the STM32 register race. Nothing like this exists for whole Microkit systems.
5. **An easy programming model.** LionsOS exists because of the low-level nature of seL4, and it already layers a MicroPython runtime over LionsOS components. PicoCalc goes a step further: every component is a scripting runtime, and handles travel inside JSON.

There's also an seL4 habit you could copy cheaply. seL4 was built against an executable spec, and you already have one: `minios`, the in-page model of the nucleus. Appendix D lists four ways it differs from the C nucleus. Running the same scripts through both and diffing the traces would catch more of those.

**The other files.** The Octavo IDE isn't OS-like. Presets run through `new Function` on the page's main thread with no isolation, so an infinite loop in a preset freezes the page. Running presets in a Worker would cheaply give it a world-style time limit. For *Small Worlds* I read the source chapters on concurrency, protection, capabilities and IPC plus Appendix D, not all 561 pages of the PDF.

I can patch the nucleus for the first three items (channels in the manifest, the ask-edge check, per-world quotas) if you'd like.


## Human

When you say “my issues”, what are you referring to?


## Assistant

By "your issues" I meant the **Known issues** list in your source zip. It's in `KNOWN-ISSUES.md`, and the same list is Appendix D ("Known issues") of *Small Worlds*. I should have named it. These are the entries I was pointing at:

- **Self-declared channels** (Authority). A world can declare `provides("keys")` and publish fake key presses.
- **Unauthenticated messages** (Authority). Any world can send to any world by name, which allows the forged `frames` message and the display-driver flush requests.
- **Handle-table exhaustion** (Authority). There is one shared table of 128 handles.
- **Not all memory is counted** (Messages and memory). Framebuffers and mailbox length aren't charged to any world.
- **No hang detection between segments** (Recovery). This is the missing turn watchdog.
- **Timed-out asks are still delivered** (Messages and memory).
- **Chapter 17 erratum**: the four ways `minios` differs from the nucleus.

I also overstated one thing. "Five of your issues are really one problem" was wrong. Only two of those five are on your list: handle-table exhaustion and uncounted mailbox memory. The other three I read from the code. The 1,024-slot ask table and the 16 DMA buffers are limits in `nucleus.h`. The unbounded mailboxes I inferred from `kernel.c`, which appends delivered messages with no cap.

Some other points came from elsewhere, not from the list:

- **The ask-cycle deadlock** is from chapter 3, the section on closed mailboxes.
- **Keyboard and power sharing the STM32** is from the README's "What the simulator caught" and from chapter 8, which notes that both drivers have full rights on one I2C device.
- **The 1.6 ms REPL ask** is from the trace in chapter 12.


## Human

Can you compile nucleus and wuickjs to webassembly, to effectively run a real vm in the browser without emulating anything except the lowest hardware level?


## Assistant

Your source tree already has a WebAssembly target (`make wasm`). I'll rebuild it from source here, check its output against the native build, and package it as a page you can open on your phone.

_[TaskCreate]_

_[TaskCreate]_

_[TaskCreate]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: about-side.png]_

_[TaskUpdate]_

_[TaskUpdate]_

_[TaskUpdate]_

_[Read: demo.html]_

_[mcp__claude-artifacts__guide]_

_[ToolSearch]_

_[mcp__claude-artifacts__list_types]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Write: template.html]_

_[Bash]_

_[Bash]_

_[Read: shot1-home.png]_

_[Read: shot2-repl.png]_

_[Read: shot4-crash.png]_

_[Read: shot5-after.png]_

_[Bash]_

_[Read: shot3-sysmon.png]_

_[Read: shot1-home.png]_

_[mcp__claude-artifacts__publish_files]_


## Assistant

I rebuilt it and put it on a page you can open on your phone. Your source tree already had a WebAssembly target (`make wasm`), so no code changes were needed. I built it from a clean tree with wasi-sdk 25 (clang 19), which gives a 1.2 MB module containing QuickJS, the nucleus and the 13 worlds. The only parts simulated are the bottom layer you meant: the ST7365P panel controller and the STM32 keyboard/battery chip, which the drivers talk to register by register.

The page includes on-screen keys and a box for typing. It also has buttons that crash the keyboard driver, the display driver or the compositor, plus the live worlds table and the UART log. I tested it in headless Chrome at phone size: `6*7` in the REPL came back `42` from the sandbox world. When I crashed the display driver, the panel went black and came back with a restart counted. I couldn't test it inside the claude.ai viewer itself; if that viewer blocks WebAssembly, the page says so instead of failing silently.

**Does it match the native build?** I ran all six scripts through the WebAssembly build in Node and through the native 32-bit build, and compared the 22 screen captures pixel by pixel:
- **21 of 22 are identical.** The exception is the About screen, which shows the total JS heap: 2,579 KB natively against 2,583 KB here, because the memory allocator differs. Turns, segments and message counts on that screen are the same.
- **The clean build is identical to the `picocalc.wasm` in your zip** on all 22 captures.

**Speed isn't a problem.** The snake script's 31.7 virtual seconds ran in 0.26 s. In the browser, simulating takes about 4–6% of real time.

One more thing besides the two chips is modelled: time. The nucleus charges each JavaScript step 665 ns, matching a measurement on the ESP32-P4, and the page paces that clock to real time. So the timings you see are the P4's, not your phone's. I could make the WebAssembly build use the browser's real clock, the way the device build would use the hardware clock, but scripts would then stop replaying identically.


## Human

Cool, now can you make a plan of what to port from l4 in a first pass?


## Assistant

_[Bash]_

_[Bash]_

Here's what I'd port in a first pass. Everything in it is decided at boot from `system.json`, the way Microkit fixes a whole system in its description file. There are no new runtime objects and no API changes, so every existing world runs unchanged; only the manifest grows. It closes four of your Known Issues outright and shrinks two more.

**Step 0: tests first**
- Add a `bench/worlds/rogue.js` with six attacks, each of which succeeds today:
  - forge a key by declaring `provides("keys")`
  - forge a frame with `send("compositor", "frames", …)`
  - ask the display driver to flush
  - narrow a handle until the table is full
  - flood a mailbox
  - set up an A↔B ask cycle
- After the pass, each must be refused with a clear error.
- Gate: the 22 captures stay pixel-identical on the native and WebAssembly builds (the comparison I just ran), and the AddressSanitizer build stays clean.

**Step 1: channels come from the manifest** (Microkit channels)
- `provides` and `needs` move into each world's manifest entry. `kernel_boot` reads them, and `read_meta` stops being the authority: a world whose own file declares a channel its entry doesn't give it fails to start, with that reason.
- At boot, check that each channel has exactly one provider. `keys` and `power` come from their drivers; the kernel owns `frames` and `worlds.status`.
- `send` and `ask` refuse a message type that is a channel name the receiver needs. Channel messages can then only arrive by publish, which stops forged frames even from worlds allowed to talk to the compositor.

**Step 2: who may send to or ask whom**
- Add per-world `sends` and `asks` lists, plus a `groups` table. The group is needed because the compositor sends `focus`, `blur` and `key` to whichever app is in front.
- Sending to yourself is always allowed. Checks go in `op_send` and the `ask` op in `host_ka`.
- Your whole message graph today:
  - launcher → compositor
  - compositor → display, power and the apps; it also asks display
  - repl asks sandbox; keys asks keyboard
  - faults sends to and asks flaky, and asks sandbox
- That closes unauthenticated messages and the flush problem, because only the compositor can reach the display driver.

**Step 3: no ask cycles** (Microkit's call rule)
- At boot, build the graph from `asks` and reject any cycle, printing it.
- Asks to a lower-priority world are allowed but logged. Microkit would forbid them, but your sandbox is deliberately the lowest priority, so repl → sandbox and faults → sandbox need to stay.
- Fix "timed-out asks are still delivered" in the same step: on timeout, remove the message from the callee's mailbox if its turn hasn't started.

**Step 4: fixed quotas for kernel objects** (seL4: no shared kernel pool)
- Per-world limits with defaults: handles, waiting asks, mailbox length and bytes, and framebuffers.
- Handles count against the world that made them, narrowed copies included. This is your chapter 9 exercise 11.
- At boot, check that the quotas sum to no more than the tables (128 handles, 1,024 asks, 16 buffers). Exhaustion then becomes impossible by construction, the static version of seL4's untyped memory.
- When a mailbox is full, `send` and `ask` fail at the sender. A `publish` drops the message for that subscriber and counts the drop, so you can show it in the system monitor.

**Step 5: a turn deadline instead of relying on timeouts**
- seL4 dropped IPC timeouts. What replaces them is a watchdog, and the nucleus already records `turn_started`.
- Add `turn_ms` per world, defaulting above the longest ask timeout in use (the REPL's 5 s). A world whose turn runs past it is crashed. This closes "no hang detection".

The manifest would look roughly like this:

```json
"groups": { "apps": ["launcher","sysmon","repl","snake","faults","keys","about"] },
"defaults": { "handles": 4, "asks": 8, "mbox": 32, "mbox_kb": 64, "turn_ms": 8000 },
{ "name": "keyboard", "provides": ["keys"], … },
{ "name": "compositor", "needs": ["frames","keys","power","worlds.status"],
  "sends": ["display","power","apps"], "asks": ["display"], "handles": 6, "bufs": 1, … }
```

Nearly all of it lands in `kernel.c` and `vm.c`, with the handle quota in `hw.c`. My rough estimate is 300–400 lines of C.

**Done when** the six attacks are refused and the captures are unchanged. At that point:
- **Closed:** self-declared channels, unauthenticated messages, handle-table exhaustion and no hang detection.
- **Shrunk:** timed-out asks and uncounted memory.

**Later passes** cover the bigger seL4 ideas:
- endpoint capabilities that can be passed in messages, and per-world handle numbering
- charging ask work to the asker, as seL4's mixed-criticality scheduler does
- one STM32 driver for keyboard and power
- supervision policy moved into a supervisor world
- PMP protection for the nucleus

Not worth porting at all: synchronous rendezvous IPC, hardware address spaces per world, seL4's capability-storage and untyped-memory machinery as such, and the proofs.

Want me to start on steps 0–2 and rerun the capture comparison?


## Human

Ok, build it. In fact, make it a whole workbench with agent in case we haven’t already. Look at our design system skate agent / workbench and attached on how to do a killer workbench and agent with eval that can then interact with the kernel or write and modify apps and drivers


## Assistant

Here's how I'm reading the request. First I'll build the first pass in the nucleus. Then I'll make a workbench page that runs the OS in WebAssembly, with an agent that can drive the kernel and edit apps and drivers, and an eval suite to check its changes. Your two workbenches and the Skate design system set the patterns and the look. I'll start by studying those and finding Skate, and implement the kernel changes in parallel.

_[Bash]_

_[Agent]_

_[Agent]_

_[ToolSearch]_

_[mcp__claude-artifacts__list_artifacts]_

_[mcp__claude-artifacts__list_artifacts]_

_[mcp__claude-artifacts__describe_capabilities]_

_[mcp__claude-artifacts__describe_capabilities]_

_[mcp__claude-artifacts__list_files]_

_[mcp__claude-artifacts__list_files]_

_[mcp__claude-artifacts__list_files]_

_[Agent]_

_[mcp__claude-artifacts__read_file: how-the-agent-works.md]_

_[mcp__claude-artifacts__read_file: the-eval-tool.md]_

_[mcp__claude-artifacts__read_file: system-prompt.md]_

_[mcp__claude-artifacts__read_file]_

_[mcp__claude-artifacts__read_file: modes-and-permissions.md]_

_[mcp__claude-artifacts__read_file: patterns.md]_

_[mcp__claude-artifacts__read_file: voice.md]_

_[mcp__claude-artifacts__read_file: bundle.css]_

_[mcp__claude-artifacts__read_file: README.md]_

_[mcp__claude-artifacts__read_file: tokens.json]_

_[mcp__claude-artifacts__read_file: layouts-and-dock.md]_

_[mcp__claude-artifacts__read_file: states-and-feedback.md]_

_[mcp__claude-artifacts__read_file: bundle.css]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[TaskCreate]_

_[TaskCreate]_

_[TaskCreate]_

_[TaskCreate]_

_[TaskCreate]_

_[Write: style.css]_

_[Bash]_

_[Write: core.js]_

_[Bash]_

_[Bash]_

_[Write: agent.js]_

_[Bash]_

_[Write: views.js]_

_[TaskUpdate]_

_[TaskUpdate]_

_[Write: main.js]_

_[Write: reference.md]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Write: evals.js]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: d1.png]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: d2-agent.png]_

_[Bash]_

_[Read: grid.png]_

_[Bash]_

_[Read: FIRST-PASS.md]_

_[Bash]_

_[Read: p1.png]_

_[Bash]_

_[Read: d1.png]_

_[Bash]_

_[Read: s-desk.png]_

_[Read: s-phone.png]_

_[Bash]_

_[Read: hdr.png]_

_[ToolSearch]_

_[mcp__claude-artifacts__publish_files]_

_[mcp__claude-artifacts__read_declaration]_

_[mcp__claude-artifacts__declare_capabilities]_

_[Bash]_

_[Bash]_

_[TaskUpdate]_

_[TaskUpdate]_

_[TaskUpdate]_

_[TaskUpdate]_

_[SendUserFile]_

_[sent picocalc-os-first-pass.zip]_

I've built the kernel's first pass and published the workbench as a single page. I checked both in headless Chrome, but the agent has only run against a stand-in for Claude, not the real thing.

**Kernel first pass.** The six attacks that all succeeded before are now refused:
- forging a key press
- forging another app's frame
- asking the display driver to flush
- filling the kernel's tables
- flooding a mailbox
- two worlds asking each other in a cycle

I re-ran the attack suite and the screen-capture comparison myself: the 22 captures are pixel-identical to the build before the change. The address-sanitizer build is clean, and the benchmark's virtual-time figures haven't moved. The manifest now carries channels, `sends`/`asks`, `groups`, quotas and `turn_ms`. One name differs from the plan: the quota on waiting asks is called `ask_slots`, because `asks` is already the list of whom a world may ask.

**The workbench** follows your Form Skate Agent and Workbench design systems.
- **Views:** Device, Code, Agent, Evals, Worlds, Messages, UART, Handles, a Graph of what the manifest allows, and a Reference.
- **Applying edits:** an edit to an app or driver reloads just that world; an edit to the manifest or prelude reboots the system.
- **The agent** works the Skate way: one `eval` tool, Auto/Ask/Read-only modes, a revert link on each step that changed files, and a live context block with every message. It can drive the kernel, edit apps and drivers, check its work in a fresh system with `test()`, and run the evals. An "Attach screen" option sends it a picture of the display.
- **The evals:** 19 of them, each on a freshly booted system: boot, opening each app, the REPL, recovery of each driver, crash-loop stop, determinism, lane load, key latency, and seven for the first pass. All 19 pass, in about 1 second total.
- **Tracking:** results are kept, and an eval that passed last run and now fails is marked REGRESSED. Neither reference workbench had that.

**What I tested.** Real Claude can't run here, so I used a stand-in. With it, the agent read the world table, edited Snake and hot-reloaded it, hit an edit error with the right line number, booted a fresh test system, and reverted the edit. I also checked the layout on desktop and phone sizes.

Things to know:
- The first message asks for consent, and each agent step uses your own Claude usage.
- Edits live in your browser's storage. "Copy edited files" in the ▦ menu gets them out.

`picocalc-os-first-pass.zip` has the updated OS source (with `FIRST-PASS.md` explaining the changes), the attack suite in `bench/`, and the workbench sources with a build script in `workbench/`.

Next, open the workbench, press **Run all** in Evals, then ask the agent to add a Clock app. That exercises a new file, a manifest entry and the launcher in one go.


## Assistant

_[Write: gen_notes.py]_


## Assistant

_[Write: notes_body.py]_


## Human

Write a proper book as well. Make sure to link research and references, show code snippets, etc…


## Assistant

_[Bash]_

_[AskUserQuestion]_


## Human

And what features would you tackle next? (Just answer)


## Assistant

What I'd tackle next, in order:

**The OS (a second pass)**
1. **Endpoint capabilities.** Replace world names with endpoints that can be passed in messages, as seL4 does, and give each world its own handle numbering. This closes the last authority gap. Today a world allowed to message another can send it *any* message type, and it can't hand someone the right to reply to it.
2. **Charge asks to the asker.** This is how seL4's scheduler runs a server on its caller's time budget. The sandbox would then evaluate REPL code at the REPL's priority and on its budget. The 1.6 ms ask behind other worlds becomes ~0.1 ms, and a runaway eval is billed to the app that asked for it.
3. **One STM32 driver.** Keyboard and power become its clients, as in LionsOS's driver framework. That removes the shared-chip race at the design level, and with it the bus-holding hack in the nucleus.
4. **Supervision policy into a supervisor world.** Restart, backoff and stop rules become per world in the manifest. The nucleus keeps only teardown and epochs.
5. **The device port with PMP.** The ESP32-P4's memory protection would fence the nucleus, so a QuickJS bug can corrupt only one world.

**The workbench**
6. **Before/after trace diff.** Run the same script on the old and new files and show which messages, segments and timings changed. That's the evidence an agent's edit needs.
7. **Record a session as an eval.** Keys and checks you perform on the Device become a new eval in one click.
8. **Evals of the agent itself.** A fixed set of tasks (add an app, fix a seeded bug, refuse an attack), graded by the OS evals, so you can compare model tiers and prompt changes. Neither Kiln nor Form Skate has this.

Starting on the book now: a companion volume in Small Worlds' pipeline, plus a Book tab in the workbench.

_[Skill]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

Now the companion's outline, the brief every chapter writer works from.

_[Write: outline.md]_

_[Write: front.md]_

_[Bash]_

_[Agent]_

_[Agent]_

_[Agent]_

_[Agent]_

_[Agent]_

_[Agent]_

_[Agent]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

Now the export additions (sources for excerpts, arrow defs), then the Book view itself.

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: book-desk-context.png]_

_[Read: book-phone-chapter.png]_

_[Read: book-desk-cite.png]_

_[Read: book-desk-search.png]_

_[Bash]_

_[ToolSearch]_

_[SendMessage]_

_[SendMessage]_

_[Bash]_

_[Bash]_

_[Bash]_

The Book tab works: it shows the book's chapters with figures and diagrams. Tapping a code excerpt's label opens that file in Code, or shows the surrounding lines for nucleus sources. Tapping a citation shows the full reference in a card, and you can search across the book. I've only tested it on two stand-in chapters on desktop and phone, because the real chapters aren't written yet.

The agent can also read and search the book now, and it's told to link the section behind any design decision it explains. The 19 evals still pass with the tab added.

The seven writers are still drafting the chapters, appendices and the fixes to *Small Worlds*. When they finish I'll check every reference and code excerpt, build the book and PDF, publish it, and update the workbench with the full book inside.


## Assistant


## Assistant

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

The appendices are written and *Small Worlds* builds clean again (all 24 broken excerpts fixed, Appendix D updated). I also corrected two small errors the review found in the workbench's Reference. Six chapter writers are still going.


## Assistant

_[Bash]_

Chapters 9–10 are in. The writer found three real limitations in the workbench: `apply` reports success before a broken world crashes, Read-only mode can be bypassed through page globals, and the 30 s step timeout cannot stop a synchronous loop. I've left them in place for now, because the book documents each one and two of them are set as exercises to fix. Five writers are still going.


## Assistant

Chapters 5–6 are in, with fresh before/after traces measured on the original nucleus. Four writers are still drafting.


## Assistant

Chapters 11–12 are in. The writer planted 12 bugs in the system: the shipped evals caught 6, and five new evals shown in the chapter raise that to 11. Three writers are still going.


## Assistant

Chapters 1–2 are in. Two writers are still going: seL4 and Microkit (3–4), and quotas and evidence (7–8).


## Assistant

_[Bash]_

_[Bash]_

_[Bash]_

All twelve chapters and both appendices now pass the build check together: about 83,000 words, with no problems reported. Waiting on the last writer (7–8) before an independent review pass.


## Assistant

All chapters are in. Next, two independent reviewers will check the book against the code and its sources, while I run the full build with the PDF.

_[Agent]_

_[Agent]_

Meanwhile, a trial full build with the PDF to shake out rendering problems:

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

Outline fixed. Now a look at representative PDF pages:

_[Bash]_

_[Read: strip.png]_

_[Bash]_

_[Read: hi-105.png]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: hi-105.png]_

_[Bash]_

_[Read: hi-105.png]_

_[mcp__claude-artifacts__list_artifacts]_

_[mcp__claude-artifacts__guide]_

The trial build works: 324 pages, chapter page numbers in the contents, a clean PDF outline, and long code lines now wrap readably in print. I'm waiting on the two reviewers.


## Assistant

_[SendMessage]_

The Part III reviewer is done. It checked about 60 claims against the system and about 30 against sources, and fixed what it found; it also flagged one error in Chapter 5, which I've passed to the other reviewer. Waiting on the Parts I–II review.


## Assistant

Both reviews are done and the check is clean. Building the final book, *Small Worlds*, and the workbench:

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: final-desk-context.png]_

_[Read: final-phone-contents.png]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[ToolSearch]_

_[mcp__claude-artifacts__list_files]_

_[mcp__claude-artifacts__read_file: index.html]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: l4page-desk.png]_

_[mcp__claude-artifacts__get_artifact]_

_[mcp__claude-artifacts__get_artifact]_

_[mcp__claude-artifacts__list_files]_

_[mcp__claude-artifacts__publish_files]_

_[mcp__claude-artifacts__publish_files]_

_[mcp__claude-artifacts__publish_files]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[SendUserFile]_

_[sent from-l4-to-small-worlds.pdf, picocalc-os-l4book.zip]_

I've written and published the companion book, *From L4 to Small Worlds*: 12 chapters and 2 appendices, about 83,000 words, 325 pages in print. You can also read it in the workbench's new Book tab.

**What's in it**
- **Part I** follows the L4 line: Brinch Hansen's RC 4000, Mach, Liedtke's L3/L4, seL4 (capabilities, untyped memory, scheduling contexts, time protection, what the proofs cover) and the Microkit with LionsOS.
- **Part II** covers the first pass, one fix per chapter: who may message whom, asks that can't deadlock, per-world limits on shared tables, and how strong the evidence is without a proof. Each chapter shows the attack, the L4 idea behind the fix, the nucleus code, and the attack being refused afterwards.
- **Part III** covers the workbench, the agent with its single `eval` tool, the evals, and a design sketch for the second pass.
- **Appendices:** the full manifest format with every error message, and the workbench's API.

**How it was checked**
- About 150 references, each confirmed against its source and linked; quotations are exact and under 15 words.
- Every code excerpt is checked by the build against the current source, so it can't drift.
- Every number about PicoCalc OS was measured, and two separate reviewers re-checked about 180 claims against the code and about 105 against sources.
- The agent has still only been run with a stand-in model, not with Claude, and the book says so.

**Book tab and the other pages**
- In the workbench's Book tab you can tap a code excerpt to open that file in Code, or to see the lines around it for nucleus code. Tapping a citation shows the full reference, and search works across the book.
- The agent can now search and read the book, and is told to link the section behind any design it explains.
- *Small Worlds* is republished with its 24 broken code excerpts fixed, notes where the first pass changed things, an updated Appendix D, and the new system running in its live demos.

**Problems the writing turned up, still open**
- `apply` reports success before a broken app crashes on reload.
- Read-only mode can be bypassed from the page.
- Timers left by crashed worlds pile up without limit.
- The sandbox stays stopped after five REPL crashes in ten seconds.
- The shipped evals caught 6 of 12 planted bugs; five new evals shown in Chapter 11 raise that to 11, but they aren't added to the suite yet.

I left the code as it is because the book documents each of these and sets several as exercises; I can fix them next if you'd like.

The PDF and the updated repository zip (book sources in `l4book/`) are attached; the published book appears as a card in the conversation.


## Human

Implement workbench improvements and The OS (a second pass)

	1.	Endpoint capabilities. Replace world names with endpoints that can be passed in messages, as seL4 does, and give each world its own handle numbering. This closes the last authority gap. Today a world allowed to message another can send it any message type, and it can't hand someone the right to reply to it.
	2.	Charge asks to the asker. This is how seL4's scheduler runs a server on its caller's time budget. The sandbox would then evaluate REPL code at the REPL's priority and on its budget. The 1.6 ms ask behind other worlds becomes ~0.1 ms, and a runaway eval is billed to the app that asked for it.
	3.	One STM32 driver. Keyboard and power become its clients, as in LionsOS's driver framework. That removes the shared-chip race at the design level, and with it the bus-holding hack in the nucleus.
	4.	Supervision policy into a supervisor world. Restart, backoff and stop rules become per world in the manifest. The nucleus keeps only teardown and epochs.


## Assistant

I'll start by reading Chapter 12's designs and the nucleus code they change, then plan the second pass.

_[Bash]_

_[Read: 12-next.md]_

_[Read: nucleus.h]_

_[Read: kernel.c]_

_[Read: vm.c]_

_[Read: hw.c]_

_[Read: prelude.js]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Agent]_

_[TaskCreate]_

_[TaskCreate]_

_[TaskCreate]_

_[TaskCreate]_

_[TaskCreate]_

_[TaskCreate]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

Before changing the nucleus, I'll write one measurement script that runs on both the old and new builds, and record the first-pass baseline.

_[Write: passes.py]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Write: stm32.js]_

_[Write: power.js]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: 40-keys.png]_

_[Bash]_

The orphan bound holds: about 1,440 queued events after 300 s, down from 92,445 before. A duplicate claim on 0x1F is now refused at boot. Next, the supervisor world.

_[Bash]_

_[Bash]_

_[Read: kernel.c]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Write: super.js]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: 05-sysmon-handles.png]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

Endpoints work. All 14 worlds run on typed endpoints (17 handles in all), and sysmon lists them. The numbers are unchanged: REPL ask 1.615 ms, recoveries within 0.3 ms. Next, the passive sandbox.

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

Now the REPL change that removes the 1.6 ms. The REPL will ask first and redraw only once the answer arrives, or after 30 ms if the answer is slow.

_[Bash]_

The ask is now 0.085 ms, down from 1.6 ms: donation plus the REPL redrawing only after the answer. Checking the REPL on screen:

_[Bash]_

_[Bash]_

_[Read: strip.png]_

_[Bash]_

_[Bash]_

Updating the two existing benches to grant authority by endpoints when the manifest has them:

_[Bash]_

_[Bash]_

Every first-pass attack and check still passes on the second pass, now refused by endpoints. Next, the second pass's own checks:

_[Bash]_

_[Write: secondpass.py]_

_[Write: orphans.js]_

_[Bash]_

_[Bash]_

All 16 second-pass checks pass. Next, the sanitizer, 32-bit and WebAssembly builds:

_[Bash]_

_[Bash]_

The only sanitizer report is the known QuickJS one, already documented in Chapter 8. Nothing new in our C. Building WebAssembly:

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: dab.png]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

Now the before/after record and the write-up:

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

Everything passes. Writing SECOND-PASS.md:

_[Write: SECOND-PASS.md]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: faults.png]_

_[Bash]_

_[Write: repoint_excerpts.py]_

_[Bash]_

_[Bash]_

Both books check clean, with 70 excerpts now quoting `history/first-pass/`. Now short notes in the books saying the second pass exists:

_[Bash]_

_[Bash]_

_[Bash]_

Now Small Worlds' Appendix D, to match KNOWN-ISSUES.md:

_[Bash]_

Both books check clean. While the helper finishes, I'll map what the workbench needs for the second pass:

_[Bash]_

_[Bash]_

_[Bash]_

_[Write: manifest-schema.md]_

_[Write: evals-second.js]_

_[Bash]_

_[Bash]_

_[Bash]_

Deterministic. I'm waiting on the helper's workbench changes before merging the second-pass evals and views into the workbench.


## Assistant

_[Write: lib.js]_


## Assistant

_[Write: probe.js]_


## Assistant

_[Write: features.js]_


## Human

Hello


## Assistant

Hi. The second pass is built and working; the last stretch is the workbench.

**Done in the OS:**
- **Endpoint capabilities.** Every send and ask now goes through a typed endpoint handle. Endpoints can be narrowed, passed on and revoked, and each world numbers its handles from 1. A transfer that would let asks form a cycle is refused.
- **Passive sandbox.** It runs on the asker's priority and budget, and its time is billed to the asker.
  - Beside a busy app, the REPL's answer comes in 40 ms; before, it timed out after 5 s.
  - The Faults app's endless loop now stops at its own 50 ms budget instead of the sandbox's 200 ms.
- **The REPL's ask is now 0.085 ms**, down from 1.6 ms. As the book predicted, donation alone left it at 1.6 ms, because the compositor and display redraw first, above the sandbox. It took a REPL change as well: the REPL now asks before it redraws. The cost is that during a long evaluation the typed line stays in the input box for up to 200 ms.
- **One STM32 driver** for keys, battery and backlight, with a power service in front of it. The nucleus no longer holds the bus through a wait, and two claims on one chip are refused at boot.
- **Supervisor world** applies a restart policy given per world in the manifest. The REPL now survives five loops. The nucleus keeps teardown, epochs, a fallback policy and a hard limit of 50 crashes in 10 s.
- Recovery times moved by less than 0.3 ms. Idle lane time rose from 0.72% to 1.22%, because each STM32 register read is now three steps.

**Checks:** the 16 new checks, the six old attacks and the five first-pass checks all pass, including under the sanitizer build. Runs are deterministic. The browser build matches native on 19 of 22 screenshots; the other three differ only in heap totals. Both books still build cleanly, now quoting the saved first-pass sources where the code changed.

**Still in progress:** the helper is adding the workbench tools (trace diff, pinned baseline, record-a-session-as-an-eval, randomised evals, an `apply` that reports real failures, a Read-only mode that holds, a timeout that stops endless loops). After that I'll add 11 new evals for the second pass, update the Graph view for endpoints, rebuild, test, and republish everything.


## Human

Continue and update book and publish once done


## Assistant

I'll keep going. "Update the book" means more than the notes I've added. *From L4 to Small Worlds* gets a new Chapter 13, "The second pass, built", plus Appendix A (manifest) and Appendix B (workbench API) revised to the current system. A writer starts Chapter 13 now on the OS parts, which are final; the workbench parts wait until the helper is done.

_[Bash]_

_[Agent]_

_[Bash]_

_[Bash]_

A writer is drafting Chapter 13 now; I've also pointed the preface and Chapter 12 at it. Still waiting on the workbench helper.


## Assistant

The workbench helper is done: 25 evals pass and its 91 feature checks pass. I'll merge the second pass into the workbench now.

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

Fixed: 76.6 ms under load, the same as the first pass (76.4 ms). Re-running everything:

_[Bash]_

That also brought idle lane time back to 0.77% (it was 1.22%), and keys at rest to 30.8 ms. The Chapter 13 writer started from the old numbers, so I'll tell it now.

_[SendMessage]_

_[Bash]_

Now the docs, to the corrected numbers:

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

All 36 evals pass on the second pass. Three of the helper's 91 feature tests fail on the new build, and one step times out; checking whether those are bugs or expectations tied to first-pass numbers:

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

All 91 feature checks and all 36 evals pass on the second-pass workbench. Telling the Chapter 13 writer the workbench is final, and keeping the headless tests in the repository:

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

Both books check clean. A second writer now brings Appendices A and B up to date with the current manifest and workbench, alongside Chapter 13:

_[Agent]_

While the two writers work, I'll check the workbench README and the WebAssembly demo page, which also needs the new build:

_[Bash]_

_[mcp__claude-artifacts__list_files]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: demo.png]_

The demo page works with the new build: 14 of 14 worlds running after an STM32 crash. Rebuilding *Small Worlds* while the writers finish:

_[Bash]_

*Small Worlds* is rebuilt. Waiting on Chapter 13 and the appendices; after an independent review of the new text I'll do the final builds and publish everything.


## Assistant

_[Write: boot.py]_


## Assistant

_[Write: run.py]_


## Assistant

Chapter 13 is in (about 5,900 words, 11 exercises). Its writer re-ran the measurements and they match the committed results. One headless check failed only because the suite took 3.17 s against a 3 s wall-clock limit; I'll relax that to 4 s, since it measures the test machine's load.

_[Bash]_

_[Bash]_

Chapter 13 reads well. Waiting on the appendices, then a review pass.


## Assistant

Both appendices are rewritten (about 60 manifest messages confirmed against the build). The writer also found seven disagreements between code and docs, two of them real bugs:

- **History bug.** A crash charged to an asker still counted toward the server's later stop.
- **Crash-loop bug.** A world that crashes on start with a 0 ms backoff floods status posts until the compositor's own redraw request fails, and that takes the compositor down.

Fixing both, and the docs:

_[Bash]_

_[Bash]_

_[Bash]_

The compositor now stays up, and the broken sandbox is stopped by the nucleus's ceiling after 50 crashes. Extending the charged-crash check to cover the history bug:

_[Bash]_

Now the docs, for these fixes and the writer's other points:

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

Now the reference.md fixes for `t.diff` and `apply`:

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Agent]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Read: demo.png]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[Bash]_

_[ToolSearch]_

_[mcp__claude-artifacts__list_files]_

_[mcp__claude-artifacts__list_files]_

_[mcp__claude-artifacts__list_files]_

_[mcp__claude-artifacts__list_files]_

_[Bash]_

_[Bash]_

_[mcp__claude-artifacts__publish_files]_

_[mcp__claude-artifacts__publish_files]_

_[mcp__claude-artifacts__publish_files]_

_[mcp__claude-artifacts__publish_files]_

_[Bash]_

_[Bash]_

_[SendUserFile]_

_[sent from-l4-to-small-worlds.pdf, small-worlds.pdf, picocalc-os-second-pass.zip]_

I've finished the second pass, updated both books and republished all four pages: the companion book, Small Worlds, the workbench and the WebAssembly demo. All checks pass: the 17 second-pass checks, the attack tests, the first-pass checks, the sanitizer build (only the known QuickJS warning), all 36 workbench evals and all 91 feature tests.

**What changed, measured before and after:**

| | First pass | Second pass |
|---|---|---|
| REPL ask | 1.61 ms | 0.085 ms |
| REPL ask beside a busy app | 5 s (timed out) | 40.3 ms |
| Faults app's endless loop stopped after | 200 ms | 50.6 ms |
| Five loops typed at the REPL | sandbox stopped | still answers |
| I2C bus time held per 10 s | 3.0 s | 2.0 s |

Key-to-screen latency, idle load and recovery times moved by 0.12 ms or less.

**The book:** the companion now has Chapter 13, "The second pass, built", and rewritten Appendices A and B. Small Worlds has notes on what the second pass fixed. A separate reviewer checked Chapter 13 and both appendices against the code and found 14 wrong claims, mostly stale numbers and message wording. I fixed all of them.

**Two bugs turned up during review, both fixed:**
- **Broken start took the screen down.** If a world threw as it started and had no backoff (the sandbox's policy), it restarted in a tight loop and crashed the compositor. The supervisor now waits at least 100 ms after a crash at startup, and the compositor survives a full mailbox.
- **Charged crashes counted against the server.** A crash billed to the world that asked for the work used to count toward the server being stopped. It no longer does.

**Trade-offs still open:**
- **The REPL can lag.** During a long evaluation the typed line can sit in the input box for up to 200 ms.
- **Keys and battery fail together.** A crash of the one STM32 driver takes both down until it restarts.
- **The sandbox can still be stopped.** The supervisor never stops it, but the nucleus still stops any world that crashes 50 times in ten seconds.

Files are attached:
- from-l4-to-small-worlds.pdf
- small-worlds.pdf
- picocalc-os-second-pass.zip


## Assistant

