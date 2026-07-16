---
title: "Binding MicroQuickJS: Handles, Atoms, and the Compacting GC in the PULP OS Builder Layer"
aliases:
  - pulp os quickjs bindings deep dive
  - microquickjs binding internals
  - esp-51 binding layer report
tags: [project-report, microquickjs, javascript, embedded, esp32s3, gc, bindings, papers3, eink]
status: active
type: project-report
created: 2026-07-16
repo: /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5
ticket: ESP-51-PULP-OS-V2
---

# Binding MicroQuickJS: Handles, Atoms, and the Compacting GC in the PULP OS Builder Layer

This report is the low-level companion to the architecture report on PULP OS v2 ([[PROJECT REPORT - PULP OS v2 - Native Builder Classes over MicroQuickJS on an E-Ink Tablet]]). Where that report describes what was built, this one describes how the JavaScript boundary actually works: the engine's value representation and memory model, the build-time generation of the standard library and its atom table, the mechanics of user classes and opaque handles, the garbage-collection discipline every binding function must observe, the direct-call convention used for gesture dispatch, and the bytecode pipeline. It is written from the implementation in `0114-papers3-pulp-os` (the third-generation JavaScript layer for this hardware; the ABI version constant in the code is `2`, following the flat-function ABI that preceded it) and from the vendored engine sources in `0114/components/mquickjs`. Line references are to those files as committed on 2026-07-16.

> [!summary]
> - MicroQuickJS represents every JavaScript value as one machine word (`uint32_t` on the device) with low-bit tags; objects live in a single caller-provided arena managed by a compacting collector, so any native code holding a `JSValue` across an allocating call holds a potentially dangling word.
> - The standard library — including user-defined classes, their prototypes, and every interned string ("atom") — is generated at build time by a host program into one constant flash-resident table. Bytecode is coupled to that table by atom index, which forces a strict regeneration protocol.
> - The binding layer stores exactly one machine word per wrapper object: a packed `(generation << 16 | index) + 1` widget handle in the object's opaque slot. Staleness is detected by generation comparison in the widget arena, not by wrapper lifetime; the class finalizer is deliberately empty.
> - JavaScript closures never cross the boundary. They are rooted in a kernel-owned array (`__cbs`) and referenced from native code by integer index; invocation is a hand-built interpreter frame (`JS_StackCheck` / `JS_PushArg` × n / `JS_Call`), not an evaluated source string.
> - The report closes with the defects this design surfaced — a finalizer-table sizing constant that must be defined in two builds, the stricter dialect's array-hole error breaking the callback registry, and an argument-space collision in the console — and the measured outcomes (trace equivalence at 831 bytes, 804 ms deadline enforcement, flat heap over a 258-command soak).

## 1. The engine's data model, as the binding layer sees it

### 1.1 One word per value

`mquickjs.h` defines `JSValue` as `uint32_t` when `JSW == 4` (the Xtensa device build) and `uint64_t` on the 64-bit host. The low bits carry a tag:

- `JS_TAG_INT` (one tag bit): a 31-bit signed integer stored inline. This is why the binding layer can treat `JS_NewInt32` results as immediates — no allocation occurs, and the value cannot be moved by the collector because it is not a pointer.
- `JS_TAG_PTR` (two bits): a pointer into the context arena, referring to a heap cell (object, string, closure, array).
- `JS_TAG_SPECIAL` (five bits): `bool`, `null`, `undefined`, `exception`, short functions, uninitialized, string characters, and catch offsets, each encoded as `JS_VALUE_MAKE_SPECIAL(tag, v)`.
- `JS_TAG_SHORT_FLOAT` (three bits): floats packed into the remaining word bits.

Two consequences matter for bindings. First, `JS_EXCEPTION` is a *value* (`JS_VALUE_MAKE_SPECIAL(JS_TAG_EXCEPTION, ...)`), not an out-of-band signal: any API that can fail returns it in-band, and forgetting `JS_IsException` on one call site lets an exception value flow into the next API, where it produces confusing secondary errors (the ESP-50 spike's "bytecode function expected" was exactly an unchecked exception fed onward). Second, only `JS_TAG_PTR` values are unstable across allocation; integers, booleans, and undefined can be held in C variables indefinitely.

### 1.2 The arena and the compacting collector

`JS_NewContext(mem, size, &js_stdlib)` receives one caller-provided memory block — 160 KB of PSRAM in this firmware — and never allocates outside it. Heap cells are `JSMemBlockHeader`-prefixed blocks with a five-bit type tag (`mtag`); free blocks are explicit (`JSFreeBlock`) and, per the comment at `mquickjs.c:100`, "may not be always compacted", meaning compaction runs when allocation pressure requires it (`js_malloc` retries after `JS_GC(ctx)` at `mquickjs.c:504–508`).

Compaction moves objects. Every root the collector knows about — the interpreter stack, the global object, ROM-table references — is rewritten to the moved addresses. A `JSValue` sitting in a C local or static is not a root, is not rewritten, and after the next collection may point at the middle of an unrelated cell. This single fact shapes the whole binding design:

1. Native code may hold a pointer-tagged `JSValue` only between two points with no allocating engine call in between.
2. Long-lived references live in JavaScript-reachable containers. The engine's sanctioned pattern is `JS_SetPropertyUint32(ctx, array, idx, v)` — the array roots the value and the collector rewrites the slot on every move.
3. Where the engine must let native code hold values across allocations (rare in this codebase), it offers `JSGCRef` / `JS_PushGCRef` / `JS_PopGCRef`, which register a stack slot as a root. The PULP bindings avoid this API entirely by ordering operations so it is never needed.

### 1.3 The interpreter stack and the C recursion budget

The interpreter operates on a value stack inside the same arena. `JS_StackCheck(ctx, len)` (`mquickjs.c:519`) verifies that `len + JS_STACK_SLACK` (slack is 16) words fit below the current stack pointer, growing `stack_bottom` — and can itself trigger a collection through `check_free_mem`. `JS_PushArg` is a raw push: `*--ctx->sp = val;`. Reentrant `JS_Call` from inside a C function called from the interpreter is bounded by `JS_MAX_CALL_RECURSE = 8` (`mquickjs.c:68`), after which the engine throws `InternalError: C stack overflow` rather than exhausting the real Xtensa stack. PULP's dispatch depth is at most two (interpreter → native gesture handler → JS callback), comfortably inside the budget.

### 1.4 How C functions are entered

The dispatch site in the interpreter (`mquickjs.c`, the `c_function:` label) documents the calling convention precisely:

- `argc` as passed to the C function is `call_flags & FRAME_CF_ARGC_MASK` — the *actual* argument count from the call site, with `FRAME_CF_CTOR` (bit 16) ored in when invoked as a constructor.
- If the caller supplied fewer arguments than the declared arity in the stdlib table, the engine pushes `JS_UNDEFINED` values until the declared count is met, so `argv[i]` for `i < declared_arity` is always a valid read even when `argc` is smaller. Extra arguments beyond the declared arity are also present and counted — variadic functions such as the builder's `add(...)` simply iterate `argc`.
- `this_val` is passed as a *pointer into the frame* (`&fp[FRAME_OFFSET_THIS_OBJ]`). Because frames are collector roots, `*this_val` re-read after an allocating call yields the post-move value. This is why every fluent method ends with `return *this_val;` — the dereference happens after all allocations in the method body, and the returned word is current.

## 2. Generating the standard library and its atoms

### 2.1 The declarative tables

The stdlib is not registered at runtime. A host program (`tools/js/pulp_stdlib.c` compiled together with the engine's `mquickjs_build.c`) declares everything in constant macro tables and calls `build_atoms("js_stdlib", js_global_object, js_c_function_decl, argc, argv)`. The macro layer is worth reading once, because its behavior explains most of the pipeline's failure modes. `JS_CLASS_DEF` stringifies its function and class-id arguments:

```c
#define JS_CLASS_DEF(name, length, func_name, class_id, class_props, \
                     proto_props, parent_class, finalizer_name)       \
    { name, length, "constructor", #func_name, #class_id,            \
      class_props, proto_props, parent_class, #finalizer_name }
```

The generator therefore never links the implementations; it emits their *names* as identifiers into the generated header. The device pairs the header with real symbols by including it in a translation unit that has all the prototypes in scope (`main/js_stdlib_table.c` includes `app_js_bindings.h` and then `js_stdlib.h`); the host bytecode compiler pairs it with no-op stubs, because a compilation-only context never calls them.

The Widget class declaration in this firmware:

```c
static const JSPropDef js_widget_proto[] = {
    JS_CFUNC_DEF("pad", 4, js_w_pad),
    /* ... 26 methods total, including the ESP-52 canvas set ... */
    JS_PROP_END,
};
static const JSClassDef js_widget_class =
    JS_CLASS_DEF("Widget", 0, js_widget_ctor, JS_CLASS_WIDGET,
                 NULL, js_widget_proto, NULL, js_widget_finalizer);
```

The prototype table becomes a flash-resident object; method lookup on a Widget instance walks to it without touching the arena. This is the concrete meaning of "prototypes in ROM": twenty-six method entries that in the v1 design were arena-allocated properties of an evaluated facade object now cost zero bytes of the 160 KB heap.

### 2.2 Atoms, and why the engine copy is per-firmware

Every property name, class name, and keyword the generated stdlib mentions is interned into the atom table, an array of string cells with fixed indices baked into both output headers:

- `main/js_stdlib.h` — the 32-bit stdlib table for the device (generated with `-m32`, because `JSW` differs between host and device and the table stores `JSValue`-typed words).
- `components/mquickjs/mquickjs_atom.h` — the atom definitions the engine core itself compiles against (generated with `-m32 -a`).

Compiled bytecode references identifiers by atom index. Three rules follow, each learned at some cost in the prior tickets and now encoded in the build scripts:

1. Regenerate both headers together after any stdlib edit; a mismatch produces parse-time nonsense because the tokenizer's keyword atoms move.
2. Rebuild every bytecode image after regeneration (`build_bytecode_apps.sh` re-runs unconditionally).
3. Never share an engine component between firmwares with different stdlibs. `0112` and `0114` each vendor their own `components/mquickjs` for exactly this reason, with provenance READMEs.

The generator also emits a diagnostic worth understanding rather than fearing: `Too many properties, consider increasing ATOM_ALIGN`. Property lookup within one ROM object uses a hash table whose size is bounded by `ATOM_ALIGN / JSW` (`mquickjs_build.c:475`, `ATOM_ALIGN = 64`, so 16 buckets on the device). A global object with more than sixteen entries — this firmware's has roughly fifty — gets its hash clamped, degrading lookups toward linear scans within the object. Correctness is unaffected; the message is a performance note, and global lookups are not on any hot path here (dispatch resolves `__cbs` once per gesture).

### 2.3 The host toolchain and the quoted-include trap

The bytecode compiler `pulpjsc` links the *engine source* on the host. `mquickjs.c` includes its atom header with quotes, and C's quoted-include rule searches the including file's directory first. Compiling the engine in place would therefore bind the host tool to the device's `-m32` atom header while its stdlib table is the 64-bit host variant — a silent mismatch whose observable symptom is that `var x = 1;` fails to parse (the `var` keyword atom is at the wrong index). The build script's countermeasure is mechanical: copy `mquickjs.c` into `tools/js/host/` next to the host-generated atom header before compiling. This is the kind of failure that costs an afternoon the first time and a comment forever after.

### 2.4 Class identifiers and the finalizer table

User classes occupy identifiers from `JS_CLASS_USER` upward; this firmware defines `JS_CLASS_WIDGET = JS_CLASS_USER + 0` and `JS_CLASS_PAGE = JS_CLASS_USER + 1`. The generated header ends with:

```c
#ifndef JS_CLASS_COUNT
#define JS_CLASS_COUNT JS_CLASS_USER
#endif
static const JSCFinalizer js_c_finalizer_table[JS_CLASS_COUNT - JS_CLASS_USER] = {
  [JS_CLASS_WIDGET - JS_CLASS_USER] = js_widget_finalizer,
  [JS_CLASS_PAGE   - JS_CLASS_USER] = js_page_finalizer,
};
```

The default makes the table zero-length; any translation unit that includes the header without pre-defining `JS_CLASS_COUNT` to cover the user classes fails with "array index in initializer exceeds array bounds". This bit twice — once in the device pairing TU, once in `pulpjsc` — because the constant must be defined in *both* builds, and nothing ties them together except discipline. `app_js_bindings.h` now owns the definition for the device; `pulpjsc.c` repeats it with a comment.

The engine invokes finalizers at two points (`mquickjs.c:3646` during collection of an unreachable user object, and `:12153` during context teardown), passing the opaque pointer: `c_finalizer_table[class_id - JS_CLASS_USER](ctx, p->u.user.opaque)`.

## 3. Opaque handles: one word of native identity

### 3.1 Object layout and the opaque slot

`JS_NewObjectClassUser(ctx, class_id)` allocates a `JSObjectUserData`-sized object on the class prototype and nulls its opaque slot (`mquickjs.c:2387–2397`). `JS_SetOpaque`/`JS_GetOpaque` assert the object is pointer-tagged, is an object cell, and has a user class id, then store or read `p->u.user.opaque` — a single `void *` the collector treats as *opaque bytes*, copying it verbatim when the object moves and never interpreting it as a reference. That property is precisely what the binding layer needs: a place to keep native identity that survives compaction without participating in it.

### 3.2 The packing

```cpp
void *PackWidget(s3paper::WidgetHandle h) {
    return reinterpret_cast<void *>(static_cast<uintptr_t>(
        (static_cast<uint32_t>(h.generation) << 16 | h.index) + 1));
}
```

The widget arena's handle is `{index : uint16, generation : uint16}`. The pack shifts the generation into the high half-word, ors the index, and adds one so that a legitimate handle can never equal the null opaque that `JS_NewObjectClassUser` initialized — an unpacked null decodes to the null widget handle rather than slot zero of the arena. Unpacking reverses the bias and splits the halves. Page wrappers use the identical scheme over the twelve-entry native page table.

### 3.3 Staleness by generation, not by wrapper lifetime

Every prototype method funnels through one resolver:

```cpp
s3paper::WidgetNode *ThisNode(JSContext *ctx, JSValue *this_val,
                              s3paper::WidgetHandle *out, JSValue *err) {
    if (JS_GetClassID(ctx, *this_val) != JS_CLASS_WIDGET) {
        *err = JS_ThrowTypeError(ctx, "expecting Widget"); return nullptr;
    }
    const auto h = UnpackWidget(JS_GetOpaque(ctx, *this_val));
    s3paper::WidgetNode *n = s3paper_runtime::Arena().Configure(h);
    if (n == nullptr) {
        *err = JS_ThrowTypeError(ctx, "stale widget handle"); return nullptr;
    }
    if (out) *out = h;
    return n;
}
```

`Configure` (arena lookup) checks index bounds, the in-use flag, and generation equality; a node destroyed or a tree reset since the wrapper was created advances the slot's generation, so the lookup fails and the method throws at the exact call site. The class finalizer is intentionally empty:

```cpp
void js_widget_finalizer(JSContext *, void *) { /* tree owns nodes */ }
```

This inverts the conventional binding pattern in which the wrapper owns the native resource and the finalizer frees it. Here the retained tree is the owner; wrappers are revocable views. The payoff is `resetTree()`: it resets the arena (bumping every slot generation), clears the page table (bumping page generations), zeroes the dynamic-value table, and replaces the callback array — after which every wrapper any application ever created is stale and throws, with no per-wrapper bookkeeping and no interaction with collection order. An amusing empirical footnote from the debugging sessions: the arena is placement-new'd into PSRAM without zeroing, so initial generations are memory garbage (values like 15377 were observed) — and this is harmless by construction, because generations are opaque equality tokens whose absolute value never matters.

### 3.4 GC-safety of the creation path

```cpp
JSValue MakeWidget(JSContext *ctx, s3paper::Result<s3paper::WidgetHandle> r) {
    if (!r.ok()) return JS_ThrowTypeError(ctx, "widget arena full");
    const JSValue obj = JS_NewObjectClassUser(ctx, JS_CLASS_WIDGET); // allocates
    if (JS_IsException(obj)) return obj;
    JS_SetOpaque(ctx, obj, PackWidget(r.value));                     // no alloc
    return obj;
}
```

The one allocating call happens before the local `obj` is used, and nothing allocates between obtaining `obj` and returning it; the value is therefore never held across a collection point. The native handle in `r` is not a JS value and needs no protection. This ordering rule — *native work first, wrapper creation last, nothing after* — recurs in every factory.

## 4. Strings, arguments, and the copy-out rule

`JS_ToCStringLen(ctx, &len, val, &buf)` returns a pointer into the arena (or into the small stack buffer `JSCStringBuf` for values needing conversion). The pointer is invalid after the next allocation, so the binding layer's universal helper copies immediately into caller storage:

```cpp
bool ArgString(JSContext *ctx, JSValue arg, char *out, size_t cap, JSValue *err) {
    JSCStringBuf buf; size_t len;
    const char *str = JS_ToCStringLen(ctx, &len, arg, &buf);
    if (str == nullptr) { *err = JS_EXCEPTION; return false; }
    snprintf(out, cap, "%.*s", (int)len, str);
    return true;
}
```

Widget text lands in the node's fixed 64-byte value field — bounded, copied, never a borrowed pointer, matching the tree's POD contract. Integer parsing uses `JS_ToInt32`, whose nonzero return indicates a pending exception (conversion of objects can invoke `valueOf` and therefore allocate and throw); every parse site propagates with `return JS_EXCEPTION;`.

The canvas methods added under ESP-52 illustrate how far one shared parser carries: `CanvasMethod(ctx, this_val, argc, argv, kind, n_coords, has_thickness, usage)` resolves the node, verifies `WidgetKind::Canvas`, reads up to four coordinates plus gray plus optional thickness, clamps coordinates to `int16` (the command store's field width), builds the 12-byte POD `CanvasCmd`, and appends through the arena, converting `CapacityExceeded` into a `TypeError`. Six JavaScript methods (`line/disc/ring/box/paint/wipe`) are one-line wrappers over it.

## 5. Closures: the `__cbs` registry and direct dispatch

### 5.1 Registration

The kernel — the entire remaining JavaScript support layer, two lines evaluated once at context creation — declares the registry and the gesture constants:

```js
var __cbs = [null];
var G = {TAP:0, LONG:1, LEFT:2, RIGHT:3, UP:4, DOWN:5, TICK:100};
```

Native registration stores the function into the array and keeps only the index:

```cpp
int32_t RegisterCb(JSContext *ctx, JSValue fn) {
    const int32_t id = g_next_cb++;
    const JSValue global = JS_GetGlobalObject(ctx);
    const JSValue cbs = JS_GetPropertyStr(ctx, global, "__cbs");
    if (JS_IsException(cbs)) return 0;
    if (JS_IsException(JS_SetPropertyUint32(ctx, cbs, (uint32_t)id, fn)))
        return 0;
    return id;
}
```

Two details are load-bearing. First, `fn` is `argv[0]` of the calling method — a frame slot, hence a root, hence safe across the allocating property store. Second, identifiers are consecutive from 1, so each store appends at exactly `array.length`; this matters because the engine's stricter dialect makes array *holes* a `TypeError` ("invalid array subscript"), which produced the registry's one real defect: the reset path originally replaced `__cbs` with an empty array, after which the first store at index 1 attempted to skip index 0. The fix seeds slot 0 with `null` — and re-fetches the array after installing it on the global object, because `JS_SetPropertyStr` allocates a property slot and may move the freshly created array.

`onTap(fn)` writes the returned identifier into the widget node's `hit_id` field. The identifier the compile-time hit-region table carries, the identifier the hit-test returns for a tapped point, and the index into `__cbs` are the same number; there is no translation layer to desynchronize.

### 5.2 Invocation

```cpp
JSValue CallCb(int32_t cb_id, int32_t a, int32_t b, int32_t c, int argc) {
    if (g_ctx == nullptr || cb_id <= 0) return JS_UNDEFINED;
    const JSValue global = JS_GetGlobalObject(g_ctx);
    const JSValue cbs = JS_GetPropertyStr(g_ctx, global, "__cbs");
    const JSValue fn = JS_GetPropertyUint32(g_ctx, cbs, (uint32_t)cb_id);
    if (!JS_IsFunction(g_ctx, fn)) return JS_UNDEFINED;
    if (JS_StackCheck(g_ctx, (uint32_t)argc + 2)) return JS_UNDEFINED;
    if (argc >= 3) JS_PushArg(g_ctx, JS_NewInt32(g_ctx, c));
    if (argc >= 2) JS_PushArg(g_ctx, JS_NewInt32(g_ctx, b));
    if (argc >= 1) JS_PushArg(g_ctx, JS_NewInt32(g_ctx, a));
    JS_PushArg(g_ctx, fn);
    JS_PushArg(g_ctx, JS_NULL);            /* this */
    s_deadline_us = esp_timer_get_time() + 1'000'000;
    const JSValue out = JS_Call(g_ctx, argc);
    s_deadline_us = 0;
    if (JS_IsException(out)) { RecordException("<callback>"); return JS_UNDEFINED; }
    return out;
}
```

The GC analysis of this function, step by step: the global-object fetch does not allocate; the two property reads may allocate only in degenerate cases and `fn` is consumed immediately by `JS_IsFunction` (a tag/class inspection); `JS_StackCheck` may collect, but at that point the only live JS value in C locals is `fn` — and here is the one subtle ordering fact: `fn` is pushed *after* the stack check and after three `JS_NewInt32` calls, which are non-allocating because 31-bit integers are immediates. Were the arguments strings, this function would be wrong as written and would need the push-first-then-build order or a `JSGCRef`. The arguments are integers by ABI design partly for this reason.

The deadline wrapper is the same interrupt mechanism used for `eval`: `JS_SetInterruptHandler` installs a callback the interpreter polls; the handler compares `esp_timer_get_time()` against the armed deadline. Probe 13 measured the enforcement: an infinite loop under an 800 ms budget returned in 804 ms with the context intact, after which fifty consecutive thrown-and-recorded exceptions left it still able to evaluate (`"context alive after storm"`).

Contrast with the v1 dispatch, which built `"s3Dispatch(0,270,480,3)"` into a `char[80]` and evaluated it: that path ran the tokenizer and parser per gesture, created RAM atoms for any identifier not yet interned, and passed arguments through decimal serialization. The direct-call path touches the parser not at all.

### 5.3 The dispatch and tick state machines

Gesture routing is a fixed native order — taps consult the hit-region table first (`HitTest` returns the topmost `hit_id`, i.e., a callback index); any gesture then consults the current page's per-kind handler array (`gesture_cb[6]`, plus `tick_cb` registered via kind 100); an unhandled swipe-down falls through to the `paper.home` callback; and everything is consumed while a JS page owns the panel, ownership being defined as `PresentCount()` unchanged since the page's own last present. The timer tick re-arms from the page's `every_ms`, invokes the tick callback, then re-evaluates every live entry of the dynamic-value table — `{WidgetHandle, cb_id}` pairs recorded when `text(fn)` detected a function argument — writing results through `SetText`, whose no-op-on-equal check feeds the render-state diff, which feeds the refresh planner. The net behavior, measured over a 36-minute soak: 1,944 ticks, 36 panel updates (exactly the minute changes), zero exceptions, and a heap whose minimum free tracked within 2.7 KB of its resting value.

## 6. The bytecode pipeline

### 6.1 Host compilation

`pulpjsc` creates a 4 MB host context (`JS_NewContext2(mem, size, &js_stdlib, 1)` — the trailing flag selects a compilation-only context), parses the application source with `JS_Parse(..., JS_EVAL_STRIP_COL)`, and converts the resulting function to the device word size with `JS_PrepareBytecode64to32(ctx, &hdr, &data, &data_len, parsed)`. The output header is the 32-bit projection of:

```c
typedef struct {
    uint16_t magic;          /* 0xacfb */
    uint16_t version;
    uintptr_t base_addr;     /* address the image was laid out against */
    JSValue unique_strings;  /* interned-string table of the image */
    JSValue main_func;       /* entry closure */
} JSBytecodeHeader;
```

Header and payload are emitted as a C byte array (`kJsBytecode_pulp`, 29,372 bytes for the eight-application image) and compiled into the firmware.

### 6.2 Device loading, and the zero-RAM-atom rule

Loading is a three-step sequence in `JsInit`, and its position in the initialization order is a hard constraint:

```cpp
memcpy(buf, kJsBytecode_pulp, sizeof(...));            /* buf: malloc'd, never freed */
JS_IsBytecode(buf, len)                                 /* magic/version check      */
JS_RelocateBytecode(g_ctx, buf, len)                    /* rebase to buf's address  */
s_bc_main = JS_LoadBytecode(g_ctx, buf);                /* register as ROM atoms    */
```

`JS_LoadBytecode` registers the image's string table as an additional ROM atom table; the engine supports exactly one beyond the stdlib's (`N_ROM_ATOM_TABLES_MAX = 2`), which is why the whole OS ships as a single image. The call throws `InternalError: "no atom must be defined in RAM"` (`mquickjs.c:12948`) if any evaluation has already interned a runtime atom — atom indices assigned at compile time on the host must remain valid, so the load must precede the kernel evaluation and everything else. The relocated buffer holds the bytecode the interpreter executes in place; it must outlive the context, and `s_bc_main` — pointing into that buffer, not into the arena — is one of the few `JSValue`s legitimately stored in a C static, precisely because ROM-table values are not subject to compaction. `JS_Run(ctx, s_bc_main)` executes the main closure and may be invoked repeatedly (`js pulp` re-enters the launcher through it).

## 7. Verification machinery at the boundary

Three permanent console facilities were built or extended during this work, and each earned its place by shortening a real debugging session:

- **Probes** (`js probe N`, `main/js_probes.cpp`): fourteen embedded ES5 programs, each exercising one boundary area with deterministic printed evidence — factories and 13 countable draw ops, fault containment (stale handle, invalid property, arena exhaustion), tap dispatch with a diff-update, dynamic-value ticking, the row-variant matrix that bisected the vanished-glyph bug, the canvas primitive set, the runaway/storm battery, and trace equivalence.
- **Traced probes** (9, 10, 12): the same programs presented through the fake backend with the full op list printed — geometry truth when op counts alone are ambiguous.
- **Hit-region dump** (`js hits`): the live `HitRegion` table with callback ids and rectangles. Before it existed, validating tap targets meant estimating y-coordinates from font metrics; two sessions of that were enough.

The strongest single result is probe 14: a deterministic native widget tree (built through the C++ API) and its JavaScript mirror (built through the class bindings) produce byte-identical normalized draw-op traces — 831 bytes each, `EQUAL` — through invert chips, centered text, gray levels, and dividers. Equivalence of this strength means the binding layer adds no rendering semantics of its own; it is a pure construction interface over the same pipeline.

## 8. Defect catalogue at the boundary

| Defect | Layer | Symptom | Root cause | Fix |
|---|---|---|---|---|
| `JS_CLASS_COUNT` unset | generated header | array-bounds compile error, twice (device TU, host tool) | default sizes the finalizer table to zero user classes | define in `app_js_bindings.h` and `pulpjsc.c`; documented in both |
| `__cbs` reset hole | kernel/registry | `TypeError: invalid array subscript` on first `onTap` after reset | stricter dialect rejects array holes; empty array + write at index 1 | seed slot 0 with null; re-fetch array after installing (GC move) |
| probe/pulp arg collision | console plumbing | `js probe 10` returned Unimplemented | probe number shared the integer op-space with the pulp op | probes moved to a 20+N band |
| vanished row glyph | core, exposed via binding | one glyph missing from JS-built trees only | `MeasureText`/`BreakLines` gated on the bitmap-fallback font table, rejecting TTF-only faces; row layout uses measured width | `IsTtfFont(id) ||` at both call sites + host regression test (same defect class as the backend's glyph guard, one layer down) |
| per-second present log | tick machinery | log noise on every zero-damage tick | `PresentPage(page, 2)` logs before knowing damage was zero | noted for demotion to debug level (cosmetic) |

The generalizable lesson from the third and fourth rows: when a legacy assumption (two fonts; op-code integer spaces) is found violated once, grep for the *pattern*, not the symptom — its siblings are usually a few lines away.

## 9. Measured outcomes

| Measure | Value |
|---|---|
| JS heap arena | 160 KB PSRAM, single block, compacting |
| Stdlib surface | ~50 globals, 26 Widget + 8 Page prototype methods, all flash-resident |
| Remaining runtime JS support code | 2 lines (`__cbs`, `G`) |
| Bytecode image (launcher + 8 apps + Ink) | 29,372 bytes, loaded once, run repeatedly |
| Deadline enforcement | 804 ms observed on an 800 ms budget |
| Exception containment | 51 recorded exceptions, context functional throughout |
| Trace equivalence (native vs bindings) | EQUAL, 831/831 bytes |
| Mixed soak | 258 console commands, 0 dropped/reordered; ~29k internal events, 18 counted tick drops; heap flat |
| Callback registry growth | monotonic per app session; truncated wholesale by `resetTree()` at every app switch |

## 10. Assessment

The binding layer's design reduces to three decisions, each forced by an engine property. The compacting collector forces the no-native-`JSValue` rule, which forces closures into a JS-side registry and native references into integers. The build-time atom table forces the full ABI surface to be declared before any application exists, which forces stubs-now-implementations-later discipline and the strict regeneration protocol. And the fixed-arena, revocable-handle widget tree forces wrapper semantics to be views rather than owners, which makes the empty finalizer and generation-checked staleness the natural lifetime model. None of these decisions is independently novel; their value is that together they leave *no* code path where JavaScript lifetime and native lifetime must be reconciled dynamically — the class of bug that dominates binding layers on larger engines simply has no habitat here.

What remains open at this layer is small: a wall-clock binding (`rtcNow()` over the BM8563) so the Ink clock tells time rather than uptime, demotion of the zero-damage tick log, and — as an architectural note for any successor — the observation that `CallCb`'s integer-only argument convention is not an accident but a GC-safety boundary, and widening it to strings or objects requires re-deriving the push ordering in §5.2.
