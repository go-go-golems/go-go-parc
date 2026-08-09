# JS Compiler on FreeRTOS

- URL: https://chatgpt.com/c/6a787d39-2b4c-83ea-8b34-6cf7e1070ae7
- Created: 2026-08-09T13:14:47.516Z

---

> V8 on freertos or some other js compiler

If you’re targeting a microcontroller running FreeRTOS, **V8 is usually the wrong fit**. I’ll compare the practical embedded JavaScript engines and where each works best.

```json
{"system2_search_query":[{"q":"site:v8.dev V8 embedder platform threads memory JIT official"},{"q":"site:bellard.org quickjs official embeddable small javascript engine"},{"q":"site:jerryscript.net JerryScript official microcontrollers JavaScript engine"},{"q":"site:moddable.com XS JavaScript engine microcontrollers FreeRTOS"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 5 websites**

</details>

For **JavaScript on FreeRTOS**, I would **not use V8** unless you're on a relatively large SoC with lots of RAM/flash and are prepared for substantial porting work. V8 is designed around a much heavier C++ platform environment; its normal embedding setup uses threading/platform libraries, and its high-performance execution relies heavily on JIT compilation, although a JIT-less mode exists. citeturn319114search1turn319114search5

For an MCU, these are better choices:

| Engine | FreeRTOS / MCU fit | JS support | My pick |
|---|---|---|---|
| **Moddable XS** | Excellent | Modern ECMAScript | ⭐ Best overall |
| **JerryScript** | Excellent | Good subset/modern JS | ⭐ Best lightweight embed |
| **QuickJS** | Good with porting | Very complete JS | Great if you have more RAM |
| **V8** | Poor | Excellent | Avoid on MCU |

### 1. Moddable XS — probably what I'd choose

XS was specifically designed for microcontrollers. More importantly, Moddable already runs its **ESP32, QCA4020, and nRF52 runtimes on FreeRTOS**. citeturn319114search33

It also has a particularly useful architecture for embedded systems:

```text
Development PC
     │
     │ JavaScript
     ▼
 XS compiler/linker
     │
     │ bytecode
     ▼
┌───────────────────────────┐
│ FreeRTOS MCU              │
│                           │
│   XS VM                   │
│      │                    │
│      ├── GPIO             │
│      ├── SPI              │
│      ├── I2C              │
│      └── your C/C++ APIs  │
└───────────────────────────┘
```

The JS source can be compiled to bytecode **on your development machine**, so the MCU primarily executes the resulting VM bytecode rather than carrying a full source compiler at runtime. citeturn319114search30

That is a very good model for FreeRTOS.

### 2. JerryScript — good if you want to build your own integration

JerryScript was explicitly designed for constrained microcontrollers. Its project describes configurations with **under 64 KB RAM for the engine and under 200 KB ROM**, and it exposes an embedding API so you can connect JS functions to native C code/peripherals. citeturn319114search0turn319114search3

You could structure it as:

```cpp
// FreeRTOS task
void js_task(void *arg)
{
    jerry_init(JERRY_INIT_EMPTY);

    // register your native APIs:
    // gpio.write()
    // uart.send()
    // device.readSensor()
    // etc.

    for (;;) {
        run_js_events();
        vTaskDelay(1);
    }
}
```

JerryScript parses JavaScript into its own bytecode and executes that through its VM. citeturn319114search19

### 3. QuickJS — attractive if the MCU isn't tiny

QuickJS is also a strong candidate. The current official release describes it as a small, embeddable engine with only a few C files and no external dependencies; a minimal x86 build is around 210 KiB of code. citeturn319114search9

Its advantage is that you get a much more complete JavaScript implementation without V8's architecture.

I'd consider QuickJS for something like:

```text
ESP32-S3
STM32H7
i.MX RT
Cortex-A + FreeRTOS
large external PSRAM
```

but **XS/JerryScript are more naturally MCU-oriented**.

### What I'd build

If you're designing something like:

```text
FreeRTOS firmware
 ├── networking task
 ├── IO task
 ├── control task
 └── JavaScript task
        │
        ├── device.gpio()
        ├── device.send()
        ├── device.timer()
        └── application JS
```

I'd use **XS + precompiled bytecode** if modern JS matters.

If you want the JS engine to be just a small scripting subsystem inside an existing C/C++ FreeRTOS firmware, I'd look closely at **JerryScript**.

I would choose **QuickJS** if you have substantially more RAM and want broad JavaScript compatibility.

I would **not attempt V8 on ESP32/STM32-class FreeRTOS hardware**. V8 solves a different problem; even V8's own embedding documentation assumes a considerably heavier runtime environment. citeturn319114search1

If you tell me the target—**ESP32-S3, STM32, RP2040, nRF, i.MX, etc.**—I can narrow this down to the best engine and show how I'd integrate it as a FreeRTOS task.


---

> I have a big ass arm that usually runs Linux

```json
{"system2_search_query":[{"q":"site:v8.dev docs embed V8 platform ARM64 JITless"},{"q":"site:v8.dev V8 supported platforms ARM64 Linux build"},{"q":"site:chromium.googlesource.com/v8/v8 FreeRTOS V8 platform page allocator OS"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

Ah — **that changes the recommendation substantially**.

If this is a **Cortex-A-class ARM/ARM64 SoC with an MMU and hundreds of MB or GB of RAM**, something that normally boots Linux, then **V8 becomes a legitimate option**. V8 has ARM/ARM64 backends and is routinely used on ARM systems. citeturn871341search3turn871341search20

The issue isn't the CPU anymore. It's **FreeRTOS versus the OS services V8 expects**.

### On a big ARM, I'd rank them

| Engine | Big ARM + FreeRTOS | Performance | Porting effort |
|---|---:|---:|---:|
| **V8** | ✅ possible | 🚀🚀🚀 | 🔴 high |
| **QuickJS** | ✅ excellent | 🚀 | 🟢 low |
| **XS** | ✅ excellent | 🚀 | 🟢 low |
| **JerryScript** | ✅ | 🐢/🚀 | 🟢 low |
| JavaScriptCore | ⚠️ possible | 🚀🚀🚀 | 🔴 high |

If you want **serious JavaScript performance**, I'd investigate **V8 first**.

## What makes V8 difficult under FreeRTOS

V8 already gives an embedder a `v8::Platform` abstraction for things such as worker tasks and memory/page allocation. citeturn871341search4turn871341search5

But a normal V8 build still assumes a fairly OS-like environment. For example, the standard embedding example links against pthreads and `dl` on Linux. citeturn871341search1

So your port ends up looking roughly like:

```text
                   JavaScript
                       │
                       ▼
                ┌────────────┐
                │     V8     │
                └─────┬──────┘
                      │
             custom V8 platform
                      │
       ┌──────────────┼───────────────┐
       ▼              ▼               ▼
    threads       page allocator    timers
       │              │               │
 FreeRTOS tasks      MMU          FreeRTOS timer
                      │
                 RAM allocator
```

The biggest thing I'd investigate is **virtual memory/page management**.

V8's platform interface explicitly has a `PageAllocator`, and V8 internally deals in page allocation/commit behavior. citeturn871341search4turn871341search13

On Linux you get things such as:

```text
mmap()
mprotect()
munmap()
virtual address reservation
RW -> RX memory permissions
threads
TLS
high-resolution clocks
```

essentially for free.

With FreeRTOS, **you'll need to provide equivalents or modify the relevant V8 platform/base layer**.

---

### JIT vs JIT-less is an important decision

With your hardware, you could theoretically run normal V8 JIT:

```text
JS
 ↓
Ignition bytecode
 ↓
Sparkplug / Maglev / TurboFan
 ↓
ARM64 machine code
```

That gets you the reason you'd bother bringing V8 over in the first place.

But JIT means you need to properly manage executable memory and instruction-cache coherency.

Alternatively, V8 officially supports **JIT-less operation**, specifically intended for environments where executable-memory generation isn't desirable or permitted. citeturn871341search24

So you could initially port:

```text
FreeRTOS
    │
    └── V8 --jitless
           │
           └── JavaScript
```

and get the basic runtime stable before worrying about executable page management.

---

## There's another option I would seriously consider

If what you really want is:

> "My big FreeRTOS application needs JavaScript scripting."

rather than:

> "I need Chrome/Node-class JavaScript performance."

then **QuickJS might save an enormous amount of engineering work**.

You could have something like:

```text
ARM64 SoC
================================================

FreeRTOS

 Task: networking
 Task: DSP
 Task: hardware control
 Task: storage

 Task: JavaScript
      │
      ├── QuickJS
      │
      ├── hw.gpio()
      ├── hw.can()
      ├── hw.i2c()
      ├── net.send()
      └── system.whatever()
```

No giant OS compatibility layer required.

---

## But if this thing has, say...

```text
ARM Cortex-A53/A55/A72/A76/etc
4-8 cores
MMU
512 MB - 8 GB RAM
FreeRTOS
```

then I **wouldn't dismiss V8 at all**.

In fact, this could be a pretty interesting architecture:

```text
                 ┌──────────────────────┐
                 │       FreeRTOS       │
                 │                      │
 Core 0          │ hard realtime tasks  │
 Core 1          │ networking           │
 Core 2          │ application          │
 Core 3          │                      │
                 │      V8 task         │
                 │        │             │
                 │        ▼             │
                 │   JS application     │
                 └──────────────────────┘
```

Keep V8 **out of hard-real-time paths** because garbage collection/JIT activity isn't something I'd want determining a real-time deadline.

If you tell me **which ARM SoC/CPU, RAM amount, and whether it's ARM32 or ARM64**, I can tell you whether I'd go **V8, V8 jitless, or QuickJS**, and what the actual FreeRTOS porting surface would look like.


---

> V8,  MT6765

MT6765 is a much better V8 candidate than an MCU-class target. The key question is not CPU horsepower; it’s whether your FreeRTOS environment can provide the Linux-like memory and threading primitives V8 expects.

```json
{"system1_search_query":[{"q":"site:mediatek.com MT6765 Cortex-A53 specifications"},{"q":"site:chromium.googlesource.com v8 arm64 build supported architectures v8"},{"q":"site:v8.dev jitless V8 official"},{"q":"site:chromium.googlesource.com v8 PageAllocator platform virtual memory"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

**Planning the V8 port**

I’m focusing on the practical path: treat this as a bare-metal/RTOS V8 port, target AArch64, and avoid assuming the MT6765 is identical to a specific MediaTek product. The biggest work is platform integration, memory, threading, and startup.

**Planned the V8 port**

</details>

For MT6765 specifically, I’d target **AArch64 V8**, not the 32-bit ARM build, provided your FreeRTOS BSP runs the application cores in AArch64. Android’s kernel tree already treats MT6765 as an ARM64 platform.

```json
{"system2_search_query":[{"q":"site:chromium.googlesource.com/v8/v8 \"V8_OS_STARBOARD\" platform starboard"},{"q":"site:chromium.googlesource.com/v8/v8 \"platform-starboard\""},{"q":"site:chromium.googlesource.com/v8/v8 \"V8_OS_FUCHSIA\" \"V8_OS_STARBOARD\""}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```json
{"system2_search_query":[{"q":"site:chromium.googlesource.com/v8/v8/+/refs/heads/main/BUILD.gn \"v8_enable_pointer_compression =\""},{"q":"site:chromium.googlesource.com/v8/v8/+/refs/heads/main/BUILD.gn \"v8_enable_sandbox =\""},{"q":"site:chromium.googlesource.com/v8/v8/+/refs/heads/main/BUILD.gn \"v8_enable_pointer_compression_shared_cage\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

Yes. **MT6765 + FreeRTOS is a credible V8 target.** The ARM64 backend itself is not the hard part; V8 already supports ARM64 extensively, and Android's kernel sources classify MT6765 support under ARM64. citeturn447938search14turn334087search2

The hard part is giving V8 enough of an **OS underneath FreeRTOS**.

### I would bring it up like this

```text
MT6765 / ARM64
        │
        ├── MMU + caches
        │
     FreeRTOS
        │
        ├── V8 OS abstraction
        │      ├── virtual memory
        │      ├── threads/tasks
        │      ├── mutex / condvar
        │      ├── TLS
        │      ├── timers
        │      └── entropy
        │
        └── V8 ARM64
               │
             JS app
```

**First milestone: JIT-less V8.** V8 explicitly supports `--jitless`, meaning it does not allocate executable memory at runtime. That eliminates a major chunk of the initial port. citeturn928146search7

I'd initially build approximately:

```gn
target_cpu = "arm64"
v8_target_cpu = "arm64"

is_component_build = false

v8_jitless = true

v8_enable_pointer_compression = false
v8_enable_pointer_compression_shared_cage = false
v8_enable_sandbox = false

v8_enable_webassembly = false
v8_enable_i18n_support = false
```

Exact GN plumbing will need modification for your FreeRTOS target, but those feature choices make the first port much simpler.

Disabling pointer compression initially matters because current ARM64 V8 normally uses pointer compression and caged address spaces; V8's build configuration includes a **4 GB heap reservation** for some caged configurations, while the V8 sandbox also assumes large amounts of virtual address space. citeturn603266search1turn334087search0 You don't want to solve all of that on day one.

### The big thing: implement virtual memory

A normal `pvPortMalloc()` is **not enough**.

V8's platform memory interface wants concepts like:

```cpp
AllocatePages(...)
FreePages(...)
SetPagePermissions(...)
RecommitPages(...)
DiscardSystemPages(...)
```

and guard regions/address-space reservations. citeturn603266search6turn603266search9

On the MT6765 you have an MMU, so I'd create a dedicated V8 virtual-address region:

```text
AArch64 virtual space

0x........
┌──────────────────────────────┐
│ FreeRTOS/kernel mappings     │
├──────────────────────────────┤
│ drivers / DMA / peripherals  │
├──────────────────────────────┤
│                              │
│       V8 VA ARENA            │
│                              │
│ initially unmapped           │
│ map physical pages on demand │
│                              │
├──────────────────────────────┤
│ stacks / heap                │
└──────────────────────────────┘
```

Then your V8 allocator becomes approximately:

```cpp
void* AllocatePages(size_t bytes, Permissions perms)
{
    // 1. reserve VA range
    // 2. obtain physical pages
    // 3. insert ARM64 page-table entries
    // 4. apply requested permissions
    // 5. TLB maintenance
    return va;
}
```

That's essentially your FreeRTOS equivalent of `mmap()`/`mprotect()`.

### Then enable the real V8 JIT

Once this works:

```js
print(1 + 2);
```

in JIT-less V8 reliably, I'd turn JIT back on.

Now your MMU abstraction needs:

```text
RW    while generating code
 ↓
cache maintenance
 ↓
RX    when executing code
```

This is particularly important on ARM64. V8's ARM64 implementation explicitly performs instruction-cache maintenance to make generated code visible to the instruction side of the CPU. citeturn356198search3

So your port must correctly handle:

```text
D-cache clean
DSB
I-cache invalidate
DSB
ISB
```

plus permission changes/TLB maintenance.

At that point you get the interesting configuration:

```text
                    MT6765
        ┌───────────────────────────┐
        │  Cortex-A / ARM64 cores   │
        └─────────────┬─────────────┘
                      │
                  FreeRTOS SMP
                      │
       ┌──────────────┼──────────────┐
       │              │              │
 realtime        networking       V8 workers
  tasks                             │
                                    ▼
                              V8 ARM64 JIT
                                    │
                            ┌───────┴───────┐
                            │ JavaScript app │
                            └───────────────┘
```

V8's `Platform` interface is already designed around embedder-provided scheduling, page allocation and worker functionality, so **FreeRTOS tasks can provide the worker implementation**. citeturn447938search6

One important distinction: a custom `v8::Platform` alone won't finish the job. V8 also has internal `base::OS` platform code, with existing POSIX/Linux implementations. FreeRTOS is not currently one of the OS targets listed by V8, so you'd be implementing/patching that layer as well. citeturn447938search0turn724039search5

**For MT6765, I'd absolutely try this rather than QuickJS if your actual objective is V8-class JS.** I would do it in this order:

1. AArch64 FreeRTOS + MMU.
2. V8 compile/link with most optional features disabled.
3. `--jitless`, pointer compression off.
4. Implement FreeRTOS threading/TLS/time/synchronization.
5. Implement V8 virtual-memory/page allocator.
6. Get Ignition executing JS.
7. Implement executable mappings + ARM64 cache maintenance.
8. Enable Sparkplug/TurboFan/Maglev.
9. Only then investigate pointer compression, WebAssembly and the V8 sandbox.

The **MMU/page allocator is the part I would design first**. Everything else is relatively conventional FreeRTOS porting.

