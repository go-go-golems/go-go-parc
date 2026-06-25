---
title: "ESP32-P4 QuickJS Internals: Porting, Runtime Ownership, and Extension APIs"
aliases:
  - ESP32-P4 QuickJS Internals
  - QuickJS ESP-IDF Porting Guide
  - QuickJS Runtime Ownership on ESP32-P4
  - Embedded QuickJS Extension APIs
  - PicoCalc QuickJS Engine Architecture
tags:
  - article
  - quickjs
  - esp32p4
  - esp-idf
  - firmware
  - embedded
  - javascript
  - runtime
  - api-design
status: active
type: article
created: 2026-06-24
updated: 2026-06-24
repo: /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5
---

# ESP32-P4 QuickJS Internals: Porting, Runtime Ownership, and Extension APIs

This report is a technical deep dive into the QuickJS layer of the ESP32-P4 firmware work. It focuses on how upstream QuickJS was brought into ESP-IDF, how the runtime is owned, how evaluation and output capture work, and how future firmware APIs such as WiFi, storage, display, keyboard, timers, and device status should be exposed safely to JavaScript.

The current system uses full upstream QuickJS as a native ESP-IDF component. QuickJS is not compiled to WebAssembly in the active native path. It is compiled as C code for the ESP32-P4 RISC-V target, wrapped by a FreeRTOS owner-task service, and consumed by both the UART console firmware (`0101-esp32-p4-native-quickjs`) and the PicoCalc visual REPL firmware (`0102-esp32-p4-visual-quickjs-repl`).

> [!summary]
> - QuickJS is vendored in `components/quickjs_native` as a small ESP-IDF component containing the core engine sources: `quickjs.c`, `cutils.c`, `dtoa.c`, `libregexp.c`, and `libunicode.c`.
> - The firmware deliberately excludes `quickjs-libc.c`. Device APIs are explicit globals installed by firmware, not the desktop `std`/`os` layer.
> - The runtime is owned by `components/qjs_service`. One FreeRTOS task owns `JSRuntime*` and `JSContext*`, and all eval/reset/status/native-job work is serialized through a queue.
> - The current default JavaScript API is intentionally small: `print(...)`, `millis()`, and `gc()`.
> - Future APIs for WiFi, storage, display, and system services should be added as native bindings or host objects through `qjs_service_run()` / `qjs_service_post()`, with clear ownership, lifetime, cancellation, and memory rules.

## Why this report exists

The earlier project report, [[ARTICLE - Native QuickJS on ESP32-P4 - Removing Wasm from the Firmware Stack]], explains why the firmware moved from QuickJS-through-WAMR to native QuickJS. The visual REPL report, [[ARTICLE - ESP32-P4 Visual QuickJS REPL - From Engine Bring-Up to PicoCalc Interface]], explains how the native engine became part of the PicoCalc LCD/keyboard UI. This report focuses only on the JavaScript engine layer.

A future maintainer will need to answer questions such as:

- Which parts of upstream QuickJS are compiled into firmware?
- Which upstream files were excluded, and why?
- How does the firmware prevent unsafe concurrent access to `JSRuntime*` and `JSContext*`?
- How are `print()`, `millis()`, and `gc()` implemented?
- How does timeout interruption work?
- How do output strings and error strings cross the C/JavaScript boundary?
- How should WiFi, storage, display, and other device APIs be added without making the runtime unstable?

The answers are architectural, not only mechanical. The port works because the engine, service, and host APIs have narrow boundaries. Extending the system safely means preserving those boundaries.

## Repository map

The source repository is:

```text
/home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5
```

The QuickJS-specific files are:

| Path | Role |
|---|---|
| `components/quickjs_native/` | ESP-IDF component that vendors upstream QuickJS core engine sources. |
| `components/quickjs_native/CMakeLists.txt` | Defines the QuickJS source list, include directory, version macro, forced compatibility include, and local warning suppressions. |
| `components/quickjs_native/quickjs_espidf_compat.h` | Declares `malloc_usable_size()` for ESP-IDF/newlib builds. |
| `components/quickjs_native/quickjs/quickjs.c` | Upstream engine implementation with one local ESP-IDF timezone portability condition. |
| `components/quickjs_native/quickjs/quickjs.h` | Public QuickJS C API used by `qjs_service`. |
| `components/qjs_service/include/qjs_service.h` | Public firmware service API for eval, reset, status, and native jobs. |
| `components/qjs_service/qjs_service.cpp` | Runtime owner task, queue protocol, globals, output capture, timeout handler, reset, status, and job execution. |
| `0101-esp32-p4-native-quickjs/main/app_main.cpp` | Starts `qjs_service` for the UART console firmware. |
| `0101-esp32-p4-native-quickjs/main/js_command.cpp` | UART console commands for `js status`, `js eval`, `js reset`, `js gc`, and `js bench`. |
| `0102-esp32-p4-visual-quickjs-repl/main/app_main.cpp` | Starts `qjs_service` for the PicoCalc visual REPL and routes visual input into eval/reset/status. |

The key ticket material is under:

```text
ttmp/2026/06/23/ESP32-P4-NATIVE-QUICKJS--native-quickjs-firmware-on-the-esp32-p4-intern-implementation-guide/
ttmp/2026/06/24/ESP32-P4-VISUAL-QUICKJS-REPL--visual-quickjs-repl-on-the-esp32-p4-picocalc-lcd/
```

## What QuickJS is in this firmware

QuickJS is an embeddable ECMAScript engine written in C. The firmware uses it as an interpreter linked directly into the ESP-IDF application. The engine creates a `JSRuntime`, creates one or more `JSContext` objects inside that runtime, compiles/evaluates JavaScript source text, exposes C functions as JavaScript functions, manages JavaScript heap objects, and reports exceptions through `JSValue` handles.

In this firmware there is one active runtime and one active context per service instance:

```text
qjs_service_t
  -> Service
       -> JSRuntime *rt
       -> JSContext *ctx
       -> owner FreeRTOS task
       -> request queue
```

The runtime is the memory-management and garbage-collection boundary. The context is the execution environment: global object, built-ins, current exception state, and host-installed functions. The firmware does not let arbitrary tasks store and use `JSContext*`. It treats the context as owned state.

This decision matters because the rest of the firmware is task-based. The UART console runs in one task. The visual keyboard editor runs in another task. Future WiFi and storage components may have their own event loops or callbacks. If each subsystem could call QuickJS directly, the code would need a global locking protocol that covers every QuickJS operation and every native object lifetime. The service avoids that problem by making ownership explicit.

## What was vendored

The native component builds the core upstream engine sources:

```cmake
idf_component_register(
    SRCS
        "quickjs/quickjs.c"
        "quickjs/cutils.c"
        "quickjs/dtoa.c"
        "quickjs/libregexp.c"
        "quickjs/libunicode.c"
    INCLUDE_DIRS
        "quickjs"
)
```

The source set includes the files needed for the engine itself:

| File | Purpose |
|---|---|
| `quickjs.c` | Core runtime, parser, bytecode compiler, interpreter, object model, standard built-ins, promises, modules, exceptions, garbage collector, memory accounting. |
| `quickjs.h` | Public embedding API used by firmware. |
| `quickjs-atom.h` | Generated atom definitions used by the engine. |
| `quickjs-opcode.h` | Bytecode opcode definitions used by the compiler/interpreter. |
| `cutils.c/.h` | Utility functions and data structures used by QuickJS. |
| `dtoa.c/.h` | Number-to-string/string-to-number conversion support. |
| `libregexp.c/.h` | Regular expression engine. |
| `libunicode.c/.h` | Unicode tables and helpers. |
| `unicode_gen_def.h`, `libunicode-table.h`, `libregexp-opcode.h`, `list.h` | Generated tables and internal support headers. |

The component defines `CONFIG_VERSION` from upstream `quickjs/VERSION`, so QuickJS source code expecting a version macro can compile:

```cmake
file(READ "${CMAKE_CURRENT_LIST_DIR}/quickjs/VERSION" QUICKJS_NATIVE_VERSION)
string(STRIP "${QUICKJS_NATIVE_VERSION}" QUICKJS_NATIVE_VERSION)

target_compile_definitions(${COMPONENT_LIB} PRIVATE
    CONFIG_VERSION="${QUICKJS_NATIVE_VERSION}"
)
```

The component intentionally keeps warning suppressions local:

```cmake
target_compile_options(${COMPONENT_LIB} PRIVATE
    -include ${CMAKE_CURRENT_LIST_DIR}/quickjs_espidf_compat.h
    -Wno-unused-function
    -Wno-unused-variable
    -Wno-format
    -Wno-type-limits
    -Wno-maybe-uninitialized
    -Wno-implicit-fallthrough
    -Wno-error=incompatible-pointer-types
)
```

This is an important containment rule. Upstream C code can require different warning settings than application firmware. Suppressing those warnings only for `quickjs_native` keeps the rest of the ESP-IDF project under the normal checks.

## What was not vendored into the runtime API

The first native firmware milestone excludes `quickjs-libc.c`. That file is useful for the desktop `qjs` command-line runtime because it provides `std`, `os`, file I/O, process-like helpers, and other host conveniences. The embedded firmware does not import that layer by default.

This exclusion is deliberate. A microcontroller device should not inherit a desktop host API accidentally. It should expose only the capabilities that the firmware is prepared to support, secure, test, document, and keep stable.

The current firmware therefore starts with three globals:

```js
print(...args)
millis()
gc()
```

These globals are installed explicitly by `qjs_service`:

```cpp
static bool install_globals(Service* s) {
  JSValue global = JS_GetGlobalObject(s->ctx);
  if (JS_IsException(global)) return false;
  const bool ok = set_global_function(s->ctx, global, "print", js_print, 1) &&
                  set_global_function(s->ctx, global, "millis", js_millis, 0) &&
                  set_global_function(s->ctx, global, "gc", js_gc, 0);
  JS_FreeValue(s->ctx, global);
  return ok;
}
```

That pattern is the extension model. Future APIs should be explicit globals or explicit namespace objects such as `wifi`, `storage`, `display`, or `system`. They should not appear because a desktop compatibility file happened to compile.

## ESP-IDF portability fixes

Two native-porting issues were significant.

### `malloc_usable_size()` declaration

QuickJS uses `malloc_usable_size()` in its default allocator accounting path on relevant libc targets. ESP-IDF provides the symbol through heap/newlib integration, but the declaration was not visible to QuickJS in this build. The component forces a compatibility header into the QuickJS compile:

```c
#pragma once
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

size_t malloc_usable_size(void *ptr);

#ifdef __cplusplus
}
#endif
```

The CMake file applies it only to the QuickJS component:

```cmake
-include ${CMAKE_CURRENT_LIST_DIR}/quickjs_espidf_compat.h
```

This keeps the compatibility declaration local. Application code does not need to include a QuickJS-specific header only because upstream QuickJS wants this symbol.

### Timezone offset calculation

Upstream QuickJS has code paths that rely on fields such as `tm_gmtoff` on platforms where `struct tm` provides them. ESP-IDF/newlib does not provide that field in this configuration. The vendored `quickjs.c` therefore uses the same fallback path as Windows when `ESP_PLATFORM` is defined:

```text
#if defined(_WIN32) || defined(ESP_PLATFORM)
    ... fallback using gmtime/localtime/mktime ...
#else
    ... use tm.tm_gmtoff ...
#endif
```

This matters for `Date` behavior. Without a valid timezone offset path, date/time operations can fail to compile or behave incorrectly. The fallback is a portability patch, not an application feature.

## Runtime creation and configuration

The service creates the runtime in one place:

```cpp
static esp_err_t create_runtime(Service* s) {
  destroy_runtime(s);

  s->rt = JS_NewRuntime();
  if (!s->rt) return ESP_ERR_NO_MEM;

  JS_SetRuntimeOpaque(s->rt, s);
  JS_SetMemoryLimit(s->rt, s->cfg.memory_limit_bytes);
  JS_SetMaxStackSize(s->rt, s->cfg.stack_limit_bytes);
  JS_SetCanBlock(s->rt, s->cfg.can_block ? 1 : 0);
  JS_SetInterruptHandler(s->rt, interrupt_handler, s);

  s->ctx = JS_NewContext(s->rt);
  if (!s->ctx) {
    destroy_runtime(s);
    return ESP_ERR_NO_MEM;
  }

  JS_SetContextOpaque(s->ctx, s);
  if (!install_globals(s)) {
    destroy_runtime(s);
    return ESP_FAIL;
  }
  return ESP_OK;
}
```

Each line has a reason.

| Call | Reason |
|---|---|
| `JS_NewRuntime()` | Allocates the QuickJS runtime and its memory-management state. |
| `JS_SetRuntimeOpaque(rt, s)` | Associates firmware service state with the runtime. The interrupt handler uses this pointer. |
| `JS_SetMemoryLimit(rt, limit)` | Bounds QuickJS-managed allocations. Current firmware uses 2 MiB. |
| `JS_SetMaxStackSize(rt, stack)` | Bounds the JavaScript stack. Current firmware uses 64 KiB. |
| `JS_SetCanBlock(rt, 0)` | Indicates that the runtime should not execute blocking operations through QuickJS internals. |
| `JS_SetInterruptHandler(rt, handler, s)` | Enables timeout interruption of long-running JavaScript. |
| `JS_NewContext(rt)` | Creates the execution context. |
| `JS_SetContextOpaque(ctx, s)` | Lets native functions such as `print()` find the service capture buffer. |
| `install_globals(s)` | Adds firmware-provided JavaScript functions. |

The default runtime limits are defined in the service:

```cpp
constexpr size_t kDefaultMemoryLimit = 2 * 1024 * 1024;
constexpr size_t kDefaultStackLimit = 64 * 1024;
```

The firmware apps override the task stack size and keep the runtime memory/stack limits explicit:

```cpp
cfg.task_name = "qjs0102";
cfg.task_stack_words = 32768;
cfg.task_priority = 8;
cfg.task_core_id = -1;
cfg.queue_len = 8;
cfg.memory_limit_bytes = 2 * 1024 * 1024;
cfg.stack_limit_bytes = 64 * 1024;
cfg.can_block = false;
```

The `task_stack_words = 32768` value is intentionally large. Earlier native tests showed that a smaller owner-task stack could fail under recursive JavaScript such as `fib(20)`. `JS_SetMaxStackSize()` limits the JavaScript engine's own stack accounting, but the C call stack used by the interpreter still lives on the FreeRTOS task stack. Both limits matter.

## The owner-task service

The service hides the runtime behind an opaque handle:

```c
typedef struct qjs_service qjs_service_t;
```

Internally, the handle points to a C++ `Service` object:

```cpp
struct Service {
  qjs_service_config_t cfg = {};
  TaskHandle_t task = nullptr;
  QueueHandle_t q = nullptr;
  SemaphoreHandle_t ready = nullptr;

  JSRuntime* rt = nullptr;
  JSContext* ctx = nullptr;
  std::string* capture = nullptr;
  int64_t deadline_us = 0;
  bool busy = false;
  uint32_t eval_count = 0;
  uint32_t reset_count = 0;
  uint32_t last_eval_ms = 0;
};
```

The service task receives a small set of message types:

```cpp
enum MsgType : uint8_t {
  MSG_EVAL = 1,
  MSG_JOB = 2,
  MSG_RESET = 3,
  MSG_STATUS = 4,
  MSG_STOP = 5,
};
```

The flow for a blocking eval request is:

```text
caller task
  -> create EvalPending on caller stack
  -> create static completion semaphore inside EvalPending
  -> enqueue MSG_EVAL with pointer to EvalPending
  -> wait for completion semaphore

owner task
  -> receive MSG_EVAL
  -> ensure runtime exists
  -> set output capture buffer
  -> set busy flag and deadline
  -> call JS_Eval
  -> collect output/error/result metadata
  -> signal caller semaphore
```

The key property is that `EvalPending` lives on the caller's stack only while the caller is blocked. That is safe because `qjs_service_eval()` does not return until the owner task signals completion. For asynchronous jobs, the service uses a heap-owned `JobPending` because the caller returns immediately.

This distinction is visible in the API:

```c
esp_err_t qjs_service_run(qjs_service_t* s, const qjs_job_t* job);
esp_err_t qjs_service_post(qjs_service_t* s, const qjs_job_t* job);
```

`qjs_service_run()` is synchronous. `qjs_service_post()` is asynchronous and heap-owns the pending request. Future extension code should choose between them deliberately.

## Evaluation and result construction

The eval path calls QuickJS like this:

```cpp
JSValue val = JS_Eval(s->ctx,
                      p->code,
                      p->len,
                      p->filename ? p->filename : "<eval>",
                      JS_EVAL_TYPE_GLOBAL);
```

The filename label is important. It appears in exceptions and diagnostics. The UART console uses labels such as `console-eval` or benchmark names. The visual REPL uses `<lcd-repl>`.

The service returns:

```c
typedef struct {
  bool ok;
  bool timed_out;
  uint32_t elapsed_ms;
  char* output;
  char* error;
} qjs_eval_result_t;
```

The caller owns `output` and `error` and must call:

```c
void qjs_eval_result_free(qjs_eval_result_t* r);
```

The eval path captures three classes of information:

1. Whether QuickJS returned a normal value or an exception.
2. Whether the configured deadline elapsed.
3. Text output produced by firmware-provided `print()` plus stringified non-`undefined` completion values.

The completion-value behavior matters. The service appends non-`undefined` eval results to `output`:

```cpp
if (!JS_IsUndefined(val)) {
  const char* text = JS_ToCString(s->ctx, val);
  if (text) {
    ... append text plus newline to output ...
    JS_FreeCString(s->ctx, text);
  }
}
```

This means a visual or UART REPL can show both:

```js
print(1 + 2)   // output from print
1 + 2          // completion value converted to string
```

A future UI may choose to style those two cases differently. At the service level, they both currently end up in `result.output`.

## Output capture and `print()`

The `print()` binding is implemented as a C function:

```cpp
static JSValue js_print(JSContext* ctx,
                        JSValueConst this_val,
                        int argc,
                        JSValueConst* argv) {
  auto* s = static_cast<Service*>(JS_GetContextOpaque(ctx));
  std::string line;
  for (int i = 0; i < argc; ++i) {
    const char* text = JS_ToCString(ctx, argv[i]);
    if (!text) return JS_EXCEPTION;
    if (i > 0) line.push_back(' ');
    line.append(text);
    JS_FreeCString(ctx, text);
  }
  line.push_back('\n');

  if (s && s->capture) {
    s->capture->append(line);
  } else {
    fwrite(line.data(), 1, line.size(), stdout);
    fflush(stdout);
  }
  return JS_UNDEFINED;
}
```

The important details are:

- Each argument is converted with `JS_ToCString()`.
- Each C string returned by QuickJS is released with `JS_FreeCString()`.
- Arguments are separated by a single space.
- A newline is appended.
- During eval, `s->capture` points to a local `std::string printed` in the owner task.
- Outside eval capture, `print()` writes to stdout.

The capture pointer is not shared across tasks because only the owner task calls QuickJS. It is still a mutable pointer, so the service sets and clears it tightly around `JS_Eval()`:

```cpp
std::string printed;
s->capture = &printed;
...
JSValue val = JS_Eval(...);
...
s->capture = nullptr;
```

A future API that produces asynchronous output must not write into this capture buffer from another FreeRTOS task. It should enqueue an event to the owner/UI task or store data in a firmware-owned queue that is drained at a defined point.

## Exceptions

When `JS_Eval()` returns an exception value, the service extracts the current exception from the context:

```cpp
static void fill_exception(Service* s, qjs_eval_result_t* out) {
  JSValue exc = JS_GetException(s->ctx);
  const char* text = JS_ToCString(s->ctx, exc);
  out->ok = false;
  out->error = dup_cstr(text ? text : "<exception stringify failed>");
  if (text) JS_FreeCString(s->ctx, text);
  JS_FreeValue(s->ctx, exc);
}
```

This currently captures the string form of the exception, not a structured stack trace. That is sufficient for `Error: boom`-style tests, but future tooling may want more information.

A more detailed exception path could inspect:

- the exception object string;
- a `stack` property when present;
- the filename label passed to `JS_Eval()`;
- whether the error was caused by timeout interruption.

That enhancement belongs in `qjs_service`, not in the LCD UI, because UART and visual REPL callers should receive the same exception structure.

## Timeout interruption

QuickJS supports an interrupt handler:

```c
void JS_SetInterruptHandler(JSRuntime *rt, JSInterruptHandler *cb, void *opaque);
```

The service installs:

```cpp
static int interrupt_handler(JSRuntime* rt, void* opaque) {
  auto* s = static_cast<Service*>(opaque);
  if (!s || s->deadline_us == 0) return 0;
  return esp_timer_get_time() > s->deadline_us;
}
```

Before eval, the service computes a deadline:

```cpp
s->deadline_us = p->timeout_ms
  ? (esp_timer_get_time() + (int64_t)p->timeout_ms * 1000)
  : 0;
```

After eval, it clears the deadline:

```cpp
const bool timed_out = (s->deadline_us != 0) &&
                       (esp_timer_get_time() > s->deadline_us);
s->deadline_us = 0;
```

The interrupt handler lets QuickJS stop long-running JavaScript at safe interpreter interruption points. It does not preempt arbitrary native C code that blocks inside a host binding. This is the most important extension rule for WiFi and storage: native bindings must not block indefinitely inside the QuickJS owner task.

If a host function performs a long ESP-IDF operation while running on the owner task, the QuickJS interrupt handler cannot make that operation return. The firmware must design those APIs so long operations are asynchronous, bounded, or executed outside the owner task with completion delivered back later.

## Reset

Reset destroys and recreates the runtime:

```cpp
if (msg.type == MSG_RESET) {
  s->busy = true;
  p->status = create_runtime(s);
  if (p->status == ESP_OK) s->reset_count++;
  s->busy = false;
  xSemaphoreGive(p->done);
  continue;
}
```

`create_runtime()` calls `destroy_runtime()` first:

```cpp
static void destroy_runtime(Service* s) {
  if (s->ctx) {
    JS_SetContextOpaque(s->ctx, nullptr);
    JS_FreeContext(s->ctx);
    s->ctx = nullptr;
  }
  if (s->rt) {
    JS_FreeRuntime(s->rt);
    s->rt = nullptr;
  }
  s->capture = nullptr;
  s->deadline_us = 0;
}
```

Reset clears JavaScript global state because the old context is freed and a new context is created. It also reinstalls firmware globals. Device API extensions must be written with reset in mind. Any JavaScript object that wraps native state must either:

1. be fully owned by the JavaScript runtime and freed during context teardown; or
2. be a lightweight handle to firmware state that remains valid across reset; or
3. explicitly detach during reset and reject future use.

For WiFi and storage, the second option is usually better. Resetting the JavaScript runtime should not necessarily disconnect WiFi or unmount storage unless the API contract says it does. JavaScript objects should be views over firmware services, not the owners of the hardware subsystem itself.

## Status and memory accounting

`qjs_service_get_status()` returns runtime and ESP heap information:

```c
typedef struct {
  bool ready;
  bool busy;
  uint32_t eval_count;
  uint32_t reset_count;
  uint32_t last_eval_ms;
  size_t memory_limit_bytes;
  size_t stack_limit_bytes;
  size_t malloc_size;
  size_t memory_used_size;
  size_t atom_count;
  size_t esp_heap_internal_free;
  size_t esp_heap_8bit_free;
  size_t esp_heap_psram_free;
} qjs_service_status_t;
```

The service fills QuickJS memory usage with:

```cpp
JSMemoryUsage mu = {};
JS_ComputeMemoryUsage(s->rt, &mu);
out->malloc_size = mu.malloc_size;
out->memory_used_size = mu.memory_used_size;
out->atom_count = mu.atom_count;
```

It fills ESP heap state with:

```cpp
heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
heap_caps_get_free_size(MALLOC_CAP_8BIT);
heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
```

This distinction matters on ESP32-P4. QuickJS allocations count against the runtime memory limit, but the firmware also needs internal DMA-capable memory for LCD buffers, driver state, queues, and ESP-IDF internals. A script can be within the QuickJS heap limit while the device is still under pressure elsewhere.

Future APIs should expose status in layers:

```js
system.status()       // coarse firmware status
qjs.status()          // runtime counters and memory
wifi.status()         // network state
storage.status()      // mounted volumes, free space, error state
display.status()      // geometry, render timing, palette
```

The implementation can reuse `qjs_service_get_status()` for the runtime part, but subsystem state should come from the owning firmware component.

## The current JavaScript surface

The current JavaScript API is intentionally small.

### `print(...args)`

`print()` converts arguments to strings, joins them with spaces, appends a newline, and sends the line to the current eval capture buffer. This is the primary output path for UART and the visual REPL.

Example:

```js
print("sum", 1 + 2)
```

Output:

```text
sum 3
```

### `millis()`

`millis()` returns `esp_timer_get_time() / 1000` as a JavaScript integer:

```cpp
return JS_NewInt64(ctx, esp_timer_get_time() / 1000);
```

It is useful for simple benchmark scripts:

```js
let t = millis();
let s = 0;
for (let i = 0; i < 100000; i++) s += i;
print("elapsed", millis() - t, "sum", s);
```

### `gc()`

`gc()` calls `JS_RunGC(rt)`:

```cpp
JSRuntime* rt = JS_GetRuntime(ctx);
JS_RunGC(rt);
return JS_UNDEFINED;
```

This gives scripts and diagnostics a way to request garbage collection. It should not be used as a substitute for correct value lifetime management in native bindings.

## How the UART console uses the service

The `0101` firmware starts the service and registers a `js` command:

```cpp
qjs_service_t *svc = start_quickjs_service();
register_js_commands(svc);
```

The command implementation uses a fixed maximum source buffer:

```cpp
constexpr size_t kMaxSrc = 2048;
constexpr uint32_t kDefaultEvalTimeoutMs = 1000;
```

The console commands are:

```text
js status
js eval <source>
js reset
js gc
js bench
```

The benchmark command runs three scripts:

```js
// 10k loop
(()=>{let t=millis(); let s=0; for(let i=0;i<10000;i++) s+=i; print('sum10k='+String(millis()-t)+',s='+String(s));})()

// 100k loop
(()=>{let t=millis(); let s=0; for(let i=0;i<100000;i++) s+=i; print('sum100k='+String(millis()-t)+',s='+String(s));})()

// fib(20)
(()=>{function fib(n){return n<2?n:fib(n-1)+fib(n-2)}; let t=millis(); print('fib20='+String(fib(20))+',ms='+String(millis()-t));})()
```

The UART console remains valuable even after the LCD REPL works. It is the recovery and diagnostic path. New QuickJS APIs should usually be testable from UART first, then surfaced visually.

## How the visual REPL uses the service

The `0102` firmware routes the current input line through the same service:

```cpp
qjs_service_eval(g_qjs,
                 source,
                 std::strlen(source),
                 kEvalTimeoutMs,
                 "<lcd-repl>",
                 &r);
```

Then it turns the result into visual records:

```text
prompt row:  > print(1+2)
status row:  OK=1 TIMEOUT=0 2MS
output row:  3
error row:   Error: boom
```

The visual REPL adds command handling before eval:

```text
/help
/status
/reset
```

This is a useful precedent. Some commands are UI/service commands rather than JavaScript source. They should remain outside the JavaScript runtime when they are primarily controlling the shell. Device capability APIs should be inside JavaScript when scripts need to call them programmatically.

## Designing future APIs

The next likely extensions are WiFi, storage, and richer device APIs. They should be designed as firmware services first and JavaScript bindings second.

A good extension process is:

1. Define the firmware component that owns the hardware or subsystem.
2. Define a small C/C++ service API for that component.
3. Decide which operations are synchronous, bounded, asynchronous, or event-driven.
4. Add native QuickJS bindings that call the firmware service without violating owner-task rules.
5. Add UART tests for the JavaScript API.
6. Add visual REPL examples after UART validation passes.
7. Document memory ownership, reset behavior, and error codes.

The wrong process is to expose low-level ESP-IDF calls directly to JavaScript because they are available in C. JavaScript APIs are product APIs. They need stable behavior, validation, and failure semantics.

## Binding pattern for synchronous functions

A simple bounded function can be exposed with `JS_NewCFunction()`.

Example target API:

```js
system.heap()
```

Possible JavaScript result:

```js
{
  internal: 123456,
  psram: 23456789,
  qjsUsed: 45678
}
```

Native binding sketch:

```cpp
static JSValue js_system_heap(JSContext* ctx,
                              JSValueConst this_val,
                              int argc,
                              JSValueConst* argv) {
  JSValue obj = JS_NewObject(ctx);
  JS_SetPropertyStr(ctx, obj, "internal",
      JS_NewInt64(ctx, heap_caps_get_free_size(MALLOC_CAP_INTERNAL)));
  JS_SetPropertyStr(ctx, obj, "psram",
      JS_NewInt64(ctx, heap_caps_get_free_size(MALLOC_CAP_SPIRAM)));
  return obj;
}
```

Rules for this class of binding:

- It must finish quickly.
- It must not wait indefinitely on another subsystem.
- It must convert ESP-IDF errors into JavaScript exceptions or structured error objects consistently.
- Every `JSValue` created must either be returned, assigned to an object that owns it, or freed.
- Every C string received from QuickJS must be released with `JS_FreeCString()`.

## Binding pattern for namespace objects

Flat globals are acceptable for `print`, `millis`, and `gc`, but larger APIs should use namespace objects.

Example:

```js
wifi.status()
wifi.scan()
storage.readText("/scripts/demo.js")
display.clear()
display.print(0, 0, "hello")
```

Installation sketch:

```cpp
static bool install_wifi(JSContext* ctx, JSValue global) {
  JSValue wifi = JS_NewObject(ctx);
  JS_SetPropertyStr(ctx, wifi, "status",
      JS_NewCFunction(ctx, js_wifi_status, "status", 0));
  JS_SetPropertyStr(ctx, wifi, "scan",
      JS_NewCFunction(ctx, js_wifi_scan, "scan", 0));
  return JS_SetPropertyStr(ctx, global, "wifi", wifi) >= 0;
}
```

The service should eventually split `install_globals()` into smaller installers:

```cpp
install_console_globals(s);
install_system_api(s);
install_wifi_api(s);
install_storage_api(s);
install_display_api(s);
```

Each installer should live near the component it exposes or in a dedicated `qjs_bindings_*` file. That keeps `qjs_service.cpp` from becoming a large collection of unrelated hardware APIs.

## WiFi API design

WiFi is stateful and asynchronous. A JavaScript binding must not block the QuickJS owner task waiting for scans, DHCP, reconnection, or network I/O without a strict timeout. The firmware should own WiFi state in an ESP-IDF networking component. JavaScript should query or request actions through a narrow API.

A practical first WiFi API is status-only plus connect/disconnect:

```js
wifi.status()
wifi.connect({ ssid: "...", password: "..." })
wifi.disconnect()
```

Possible `wifi.status()` result:

```js
{
  mode: "station",
  state: "connected",
  ssid: "my-network",
  ip: "192.168.1.23",
  rssi: -55,
  lastError: null
}
```

`wifi.connect()` should not run a long blocking connection loop inside the QuickJS owner task. It should validate arguments, submit a request to the WiFi manager, and return a request result:

```js
let r = wifi.connect({ ssid: "lab", password: "secret" });
print(r.accepted, r.state);
```

The firmware can later add event polling:

```js
let ev = system.nextEvent(0);
if (ev && ev.type === "wifi.connected") print(ev.ip);
```

or a promise-like API if the firmware also implements a job/event pump for QuickJS promises. The current system does not yet pump asynchronous promise jobs as a product-level API, so event polling is simpler for the next milestone.

WiFi binding rules:

- Do not expose raw passwords through `status()`.
- Store credentials through an explicit storage/NVS path, not as global JavaScript variables that survive only until reset.
- Treat connection state as firmware-owned state, not JavaScript-owned state.
- Return structured errors: `{ ok: false, error: "..." }` or throw `Error`, but choose one convention per namespace.
- Keep network callbacks out of direct QuickJS calls. Callbacks should enqueue events; the owner task can expose those events when JavaScript asks.

## Storage API design

Storage has two separate concerns: persistent data for scripts and firmware-managed configuration. They should not be conflated.

A minimal script storage API could be:

```js
storage.list("/scripts")
storage.readText("/scripts/demo.js")
storage.writeText("/data/log.txt", "hello\n")
storage.remove("/data/log.txt")
storage.stat("/scripts/demo.js")
```

The first implementation should be synchronous only if the underlying operation is bounded and small. Reading a short script file is acceptable. Reading a multi-megabyte file into a JavaScript string is not.

Recommended constraints:

| Operation | Constraint |
|---|---|
| `readText(path)` | Limit file size, for example 16 KiB or 64 KiB. |
| `writeText(path, text)` | Limit text size and return bytes written. |
| `list(path)` | Limit number of returned entries. |
| `stat(path)` | Return metadata without reading contents. |
| `remove(path)` | Return structured success/error. |

Path validation should be strict. Scripts should not be able to access arbitrary mount internals accidentally. Use a virtual root such as `/scripts` and `/data`, and map that to firmware storage paths.

Native binding sketch for `readText`:

```cpp
static JSValue js_storage_read_text(JSContext* ctx,
                                    JSValueConst this_val,
                                    int argc,
                                    JSValueConst* argv) {
  const char* path = JS_ToCString(ctx, argv[0]);
  if (!path) return JS_EXCEPTION;

  StorageReadResult r = storage_read_text_limited(path, MAX_JS_FILE_BYTES);
  JS_FreeCString(ctx, path);

  if (!r.ok) {
    return JS_ThrowInternalError(ctx, "readText failed: %s", r.error);
  }
  return JS_NewStringLen(ctx, r.data, r.len);
}
```

Rules:

- Release the path string on every return path.
- Enforce size limits before allocating JavaScript strings.
- Decide whether failures throw or return `{ ok: false }`.
- Keep file handles firmware-owned and short-lived unless there is a strong reason to expose streaming handles.

## Display API design

The visual REPL already owns the screen. A JavaScript display API must not corrupt the REPL state by drawing arbitrary pixels behind the renderer unless the firmware defines a mode boundary.

There are two safe directions.

### Direction 1: REPL-safe output APIs

Expose functions that append visual records rather than drawing pixels:

```js
ui.print("hello")
ui.status("connected")
ui.error("failed")
```

These can map to `visual_repl_append_line()` or a future logical record API. They preserve scrollback and fit the current model.

### Direction 2: application canvas mode

Define a separate mode where JavaScript owns a canvas:

```js
display.mode("canvas")
display.clear("black")
display.rect(10, 10, 100, 20, "red")
display.text(10, 40, "hello")
display.present()
```

This requires an explicit transition out of REPL mode and a way to recover. It should not be mixed into the current terminal renderer casually.

The near-term recommendation is to expose REPL-safe APIs first. Canvas APIs should wait until mode switching, recovery keys, and memory limits are designed.

## Keyboard/input API design

The keyboard is already consumed by the REPL editor. JavaScript should not receive raw key events by default while the REPL is active because the same keypress cannot reliably both edit the command line and act as application input.

Possible future modes:

```js
input.readKey({ timeout: 1000 })
input.setMode("raw")
input.setMode("repl")
```

Raw input mode needs an escape hatch. The firmware must reserve a key sequence that returns to the REPL even if JavaScript code is waiting for input.

For now, input should remain a firmware/UI concern.

## Timers and asynchronous work

QuickJS supports promises and job queues internally, but this firmware has not yet defined an event-loop contract for scripts. Adding `setTimeout()` or promise-based WiFi APIs requires more than installing a function. It requires a policy for when the firmware drains pending jobs and how script execution is resumed.

A simple first timer API can be polling-based:

```js
let start = millis();
while (millis() - start < 100) {}
```

That works but consumes the owner task until the timeout. It is not appropriate for product APIs.

A better embedded event model is:

```js
system.pollEvent(timeoutMs)
system.postEvent(type, payload)
```

or, later:

```js
await wifi.connected()
```

The promise/`await` version requires the firmware to call QuickJS job execution APIs at defined points. That should be a separate design milestone. Until then, avoid promising asynchronous JavaScript semantics.

## Native jobs for advanced extensions

`qjs_service_run()` and `qjs_service_post()` are the extension hooks for code that must execute on the QuickJS owner task with direct `JSContext*` access.

The job type is:

```c
typedef esp_err_t (*qjs_job_fn_t)(JSContext* ctx, void* user);

typedef struct {
  qjs_job_fn_t fn;
  void* user;
  uint32_t timeout_ms;
} qjs_job_t;
```

Use `qjs_service_run()` when the caller needs to wait for the result:

```cpp
qjs_job_t job = {
  .fn = install_wifi_api_job,
  .user = &config,
  .timeout_ms = 1000,
};
esp_err_t err = qjs_service_run(svc, &job);
```

Use `qjs_service_post()` when the caller only needs to schedule owner-task work:

```cpp
qjs_job_t job = {
  .fn = deliver_event_job,
  .user = event_ptr,
  .timeout_ms = 100,
};
qjs_service_post(svc, &job);
```

For asynchronous jobs, the `user` pointer lifetime must be explicit. The current service heap-owns the `JobPending`, not the `user` payload. If the payload must survive until the owner task runs, allocate it and free it inside the job function, or use a firmware-owned queue with stable storage.

## Memory ownership rules for bindings

QuickJS bindings are easy to write incorrectly because values cross two memory systems: QuickJS-managed values and firmware-managed memory.

Use these rules:

1. If a function receives a `JSValueConst`, do not free it unless the API documentation says ownership transfers.
2. If a function creates a `JSValue` and returns it, the caller receives ownership through the return path.
3. If a function creates a `JSValue` and stores it as an object property with a successful `JS_SetProperty*` call, the property takes ownership.
4. If a function creates a `JSValue` and does not return or store it, it must call `JS_FreeValue()`.
5. If `JS_ToCString()` returns a non-null pointer, call `JS_FreeCString()` after use.
6. If firmware allocates memory for `qjs_eval_result_t.output` or `.error`, the caller must call `qjs_eval_result_free()`.
7. Do not keep raw `JSValue` handles in other FreeRTOS tasks unless the design includes a strict owner-task lifetime protocol.

A useful binding review checklist is:

```text
For every JS_New* call, where is ownership transferred or freed?
For every JS_ToCString call, where is JS_FreeCString called?
For every firmware allocation, who frees it?
Can this function block longer than the eval timeout?
Can this function be called during reset or while the subsystem is unavailable?
What JavaScript-visible error does it produce?
```

## Error conventions

The current service uses two layers of errors:

- `esp_err_t` for service-level failures such as invalid arguments, queue timeout, or allocation failure before eval starts.
- `qjs_eval_result_t.error` for JavaScript exceptions produced during eval.

Future JavaScript APIs should choose a JavaScript-level convention. Two viable conventions are:

### Throwing exceptions

```js
try {
  storage.readText("/missing.txt");
} catch (e) {
  print(e);
}
```

This is appropriate when the operation is expected to produce a value and failure should interrupt the script path.

### Structured results

```js
let r = wifi.connect({ ssid, password });
if (!r.ok) print(r.error);
```

This is appropriate for operations where failure is common and expected, such as network connection attempts.

Do not mix both styles randomly inside one namespace. A good rule is:

- Argument validation errors throw.
- Programmer errors throw.
- Operational failures return structured results if they are common.
- Unexpected internal failures throw.

## Security and capability boundaries

The device is not currently a hardened multi-user system, but capability boundaries still matter. JavaScript code should not receive unrestricted firmware access by default.

For WiFi:

- Do not expose stored passwords through status APIs.
- Avoid arbitrary socket/network APIs until there is a resource policy.
- Prefer explicit high-level operations first.

For storage:

- Use virtual roots.
- Enforce file size limits.
- Avoid arbitrary path traversal.
- Separate configuration storage from user script storage.

For display:

- Preserve a recovery path to the REPL.
- Avoid letting scripts permanently hide diagnostics without a reset gesture.

For system APIs:

- Treat restart, erase, flash update, and credential operations as privileged commands.
- Require explicit user confirmation or compile-time enablement for destructive functions.

## Testing strategy for QuickJS extensions

Every new binding should be tested at three levels.

### Host-level script tests

The separate JS worktree contains a portable script playbook:

```text
/home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5-js
feature/0102-js-scripts
```

Scripts there use the contract:

```text
Available: print(...args), millis(), gc()
Avoid: console.log, require, import, fs, path, process, Buffer, std, os, browser APIs
```

This is useful for logic that does not depend on device hardware.

### UART firmware tests

New native APIs should first be tested through `0101` or the `0102` UART console because UART output is easier to capture and inspect than LCD output.

Example:

```text
js eval "print(system.heap().internal)"
js eval "print(storage.readText('/scripts/smoke.js'))"
js eval "print(JSON.stringify(wifi.status()))"
```

### Visual REPL tests

After UART tests pass, run the same scripts from the PicoCalc keyboard and validate rendering, wrapping, errors, and recovery.

For each binding, capture:

- successful output;
- invalid argument behavior;
- subsystem unavailable behavior;
- timeout behavior if relevant;
- memory/status before and after repeated calls;
- reset behavior.

## Extension sequence recommendation

The safest sequence is:

1. Refactor `install_globals()` so API installers are modular.
2. Add a `system` namespace with `heap()`, `status()`, and `version()`.
3. Add structured exception helpers so native bindings report errors consistently.
4. Add read-only WiFi `status()` before connect/scan.
5. Add storage `stat()` and `list()` before `readText()` and `writeText()`.
6. Add size-limited `storage.readText()` for scripts.
7. Add a script loader command outside JavaScript, such as `/run /scripts/demo.js`, so the REPL can load stored scripts without exposing arbitrary filesystem semantics first.
8. Add WiFi connect/disconnect as firmware-service requests, not blocking owner-task loops.
9. Add event polling if asynchronous features become necessary.
10. Only then consider promise-based APIs or a richer JavaScript event loop.

This sequence keeps the engine stable while expanding capabilities.

## What to watch when modifying QuickJS itself

Most future work should not modify upstream `quickjs.c`. Add bindings around the engine instead. Modify QuickJS source only when there is a portability bug or a deliberate engine-level change.

If updating upstream QuickJS:

1. Replace files under `components/quickjs_native/quickjs/` from the selected release.
2. Reapply or re-evaluate the ESP-IDF timezone patch.
3. Verify `quickjs_espidf_compat.h` is still needed and still sufficient.
4. Keep the `CMakeLists.txt` source list aligned with upstream source requirements.
5. Build `0101-esp32-p4-native-quickjs`.
6. Run UART smoke: `js status`, `js eval "print(1+2)"`, exception, `js reset`, `js bench`.
7. Build and flash `0102`.
8. Run visual smoke: `/status`, `print(1+2)`, exception, `/reset`.
9. Record version, source changes, build warnings, and device behavior in the ticket diary.

Do not hide new compiler warnings globally. If upstream code requires suppression, keep it local to `quickjs_native`.

## Common failure modes

| Failure | Likely cause | Correct place to fix |
|---|---|---|
| Compile error about `malloc_usable_size` | ESP-IDF declaration not visible to QuickJS. | `quickjs_espidf_compat.h` / component compile options. |
| Compile error about `tm_gmtoff` | ESP-IDF/newlib `struct tm` lacks field. | QuickJS timezone portability patch. |
| FreeRTOS stack overflow during recursive JS | Owner task stack too small. | App service config `task_stack_words`. |
| Script runs too long | Missing/too-large timeout or interruption not reached. | Eval timeout and binding design. |
| Timeout does not stop native operation | Host binding blocks inside C/ESP-IDF. | Redesign binding as asynchronous/bounded. |
| Heap drops after repeated eval | JS values, C strings, or result buffers leaked. | Binding/service memory ownership review. |
| Crash when another task uses `JSContext*` | Runtime ownership violation. | Route through `qjs_service_run()` / `post()`. |
| Reset leaves stale JS object wrapping native state | Finalizer/lifetime contract missing. | Binding design and reset policy. |
| Visual REPL shows no result for a command | Script produced no `print()` and completion value was `undefined`. | UI expectation or service result formatting. |

## Current state

The current firmware has reached this state:

- Native QuickJS builds and runs on ESP32-P4.
- The service starts in about a few milliseconds on device-level measurements from the native ticket.
- UART eval/status/reset/gc/bench commands are validated in `0101`.
- The PicoCalc visual REPL in `0102` can route keyboard-submitted source through `qjs_service_eval()`.
- The visual REPL can render output, errors, status, `/help`, `/status`, and `/reset`.
- Boot now clears the LCD to black before the first REPL render.
- The JavaScript API surface remains intentionally small.

The next engineering phase should not be to add many APIs quickly. It should be to add one namespace at a time, with a test script, UART validation, visual validation, and a clear reset/lifetime policy.

## Review map

A reviewer should read the QuickJS layer in this order:

1. `components/quickjs_native/README.md` for source set and porting notes.
2. `components/quickjs_native/CMakeLists.txt` for the exact build boundary.
3. `components/quickjs_native/quickjs_espidf_compat.h` for the ESP-IDF declaration shim.
4. `components/qjs_service/include/qjs_service.h` for the public firmware API.
5. `components/qjs_service/qjs_service.cpp` for runtime creation, owner-task serialization, eval, reset, status, and jobs.
6. `0101-esp32-p4-native-quickjs/main/js_command.cpp` for UART command usage.
7. `0102-esp32-p4-visual-quickjs-repl/main/app_main.cpp` for visual REPL usage.

The central review question is simple: does any code outside `qjs_service` touch `JSRuntime*` or `JSContext*` directly? If yes, it needs a strong justification. The default answer should be no.

## Related notes

- [[ARTICLE - Native QuickJS on ESP32-P4 - Removing Wasm from the Firmware Stack]]
- [[ARTICLE - ESP32-P4 Visual QuickJS REPL - From Engine Bring-Up to PicoCalc Interface]]
- [[ARTICLE - QuickJS Wasm on ESP32-P4 - Device Bring-Up and Two WAMR Embedding Crashes]]
