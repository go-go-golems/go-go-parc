---
title: "Lazy Data Structures over goja Proxy - Go-Backed On-Demand JavaScript Objects"
aliases:
  - goja lazy proxy
  - lazy goja data structures
  - goja ProxyTrapConfig
  - flag-only descriptor goja
tags:
  - article
  - goja
  - go-go-goja
  - javascript
  - go
  - proxy
  - lazy-evaluation
  - architecture
status: active
type: article
created: 2026-06-23
repo: /home/manuel/workspaces/2026-06-23/benchmark-goja-proxy-object/go-go-goja
---

# Lazy Data Structures over goja Proxy

This article explains how to expose lazily-materialised Go data structures to JavaScript so that they appear as ordinary objects and arrays, while their values are produced on demand only at the moment JavaScript reads them. It covers the goja Proxy trap model, the dispatch path from a JavaScript operation to a Go function, the proxy invariants that constrain trap results, and one non-obvious failure mode in which naive enumeration silently materialises every value. The reference implementation is the `lazy` module in `go-go-goja/modules/lazy/`, developed under ticket `GOJA-LAZY-DS`.

The target reader writes Go and JavaScript and has used goja to run scripts, but has not implemented an ES Proxy from the Go side.

> [!summary]
> - goja exposes ES Proxy traps as ordinary Go functions through `vm.NewProxy(target, *goja.ProxyTrapConfig)`. A lazy data structure is a Go value behind those functions.
> - `Object.keys()` and `for...in` call `[[GetOwnProperty]]` for every key. If that trap builds the value, enumeration materialises the entire object. The fix is a flag-only descriptor that carries no value.
> - The flag-only descriptor is fragile: setting `Writable` to `true` routes through a fast path that reports `undefined`, which makes the key vanish from `Object.keys`. Leave `Writable` unset.
> - Proxy traps are constrained by invariants checked against the proxy's target object. A fresh, empty, extensible target satisfies every invariant trivially.
> - `JSON.stringify`, spread, and `Object.assign` read values through `[[Get]]`. That materialisation is inherent to those operations and cannot be avoided.

## Why this note exists

Embedding Go logic behind a JavaScript runtime is the central concern of [[ARTICLE - Designing DSLs with go-go-goja - Go-Backed JavaScript APIs|go-go-goja DSL design]]. The common pattern is to export Go functions and let JavaScript call them. That pattern is eager: the Go side produces a value only when JavaScript invokes a function, and the value is a plain object once produced.

A different class of problem appears when the data itself is the surface. A device descriptor where reading `device.wifis` should trigger a Wi-Fi scan. A result set where reading `rows[1000000]` should fetch only that row. An environment object where the set of keys is itself the product of a query. In each case the JavaScript side wants an ordinary object or array, and the Go side wants to defer work until a specific property is actually read.

The ES Proxy is the mechanism that makes this possible, and goja implements it with a Go-facing API. This note records how that API behaves, where its sharp edges are, and how the `lazy` module turns the mechanism into a reusable set of builders.

## The problem: exposing on-demand Go data as JavaScript objects

Consider a Go function that scans for Wi-Fi networks. It is slow and side-effecting. The goal is to let JavaScript write `device.wifis` and receive the scan result, while ensuring the scan runs only when that property is read, never when the object is enumerated or logged.

A first attempt is to build a plain object eagerly and hand it to the runtime:

```go
vm.Set("device", map[string]any{
    "name":    "atom-3r",
    "wifis":   scanWifis(),   // runs now, unconditionally
    "battery": readBattery(),
})
```

This defeats the purpose. The scan runs at construction time regardless of whether JavaScript ever reads `wifis`. For an infinite or very large structure, eager construction is not merely wasteful, it is impossible.

The required property is interception. Every operation JavaScript performs on the object, reading a property, testing membership with `in`, enumerating keys, serialising with `JSON.stringify`, must pass through Go code that can decide whether and when to do real work. The ES Proxy provides exactly this interception, and goja lets the intercepting code be written in Go.

## The goja Proxy trap model

A Proxy wraps two things: a target object and a handler. The target is a real object that defines the baseline behaviour and the invariants the proxy must respect. The handler is a set of trap functions, one per fundamental object operation defined by the ECMAScript specification.

In goja, the handler is expressed as a Go struct of optional functions. The public entry point is `Runtime.NewProxy`:

```go
// goja/builtin_proxy.go
func (r *Runtime) NewProxy(target *Object, nativeHandler *ProxyTrapConfig) Proxy
```

`ProxyTrapConfig` is a struct with one field per trap. Each field is a function pointer. A `nil` field means no trap is installed for that operation, and the operation falls through to the target unchanged. The relevant traps for a read-only lazy object are:

| Trap field | JavaScript operation | Internal method |
| --- | --- | --- |
| `Get` / `GetIdx` / `GetSym` | `obj.k`, `obj[i]` | `[[Get]]` |
| `Has` / `HasIdx` / `HasSym` | `"k" in obj` | `[[HasProperty]]` |
| `GetOwnPropertyDescriptor` | `Object.getOwnPropertyDescriptor`, enumeration filter | `[[GetOwnProperty]]` |
| `OwnKeys` | `Object.keys`, `for...in`, `Object.getOwnPropertyNames` | `[[OwnPropertyKeys]]` |
| `Set` / `DeleteProperty` | `obj.k = v`, `delete obj.k` | `[[Set]]`, `[[Delete]]` |

The full set contains thirteen traps, including `GetPrototypeOf`, `IsExtensible`, `Apply`, and `Construct`. The last two apply only when the target is callable. For lazy data structures, the five traps above are sufficient; the rest are left `nil` and delegate to the target.

There are two layers beneath `ProxyTrapConfig`. The struct is adapted by an internal `nativeProxyHandler` to the unexported `proxyHandler` interface in `goja/proxy.go`, which carries one method per trap. The `ProxyTrapConfig` layer is the right abstraction for new work. It handles the detail that integer-valued string keys, such as `"0"` and `"123"`, are routed to the `*Idx` variant when one is installed, so the caller does not re-parse strings.

A proxy is a `goja.Value`. The `Proxy` Go type implements the unexported `valueContainer` interface (`toValue(*Runtime) Value`), and `Runtime.ToValue` dispatches on that interface, so a `Proxy` can be passed to `vm.Set`, returned from a Go function called by JavaScript, or stored in a slice. The same type exposes `Revoke()`, which nulls the handler so that further JavaScript operations throw `TypeError: Proxy already revoked`.

## How JavaScript operations reach Go traps

Understanding laziness requires understanding which trap each JavaScript idiom triggers. The dispatch is deterministic. The following traces show the path for the common idioms, anchored to the methods in `goja/proxy.go`.

Reading a property routes through `[[Get]]`:

```
device.wifis
  vm executes [[Get]]("wifis")
    proxyObject.getStr -> nativeProxyHandler.getStr
      ProxyTrapConfig.Get(target, "wifis", receiver)   <-- the Go function
```

Testing membership routes through `[[HasProperty]]`:

```
"wifis" in device
  vm executes [[HasProperty]]("wifis")
    nativeProxyHandler.hasStr -> ProxyTrapConfig.Has(...)
```

Enumeration is two-phase. The first phase calls `ownKeys`; the second phase calls `[[GetOwnProperty]]` for every key returned, to decide which keys are enumerable:

```
Object.keys(device)
  [[OwnPropertyKeys]]
    ProxyTrapConfig.OwnKeys(target) -> ["name","wifis","battery","uptime"]
  for EACH key:
    [[GetOwnProperty]](key)            <-- decides enumerability
      ProxyTrapConfig.GetOwnPropertyDescriptor(...)
```

Serialisation is also multi-step. `JSON.stringify` first reads a `toJSON` method on the object, then reads each own enumerable key:

```
JSON.stringify(device)
  [[Get]]("toJSON")         (looked up first)
  for each OWN enumerable key:
    [[Get]](key)            (materialises the value)
```

The two-phase nature of enumeration is the source of the central failure mode described below. The trap that lists the keys is not the trap that decides whether a key appears in `Object.keys`. A key appears only if `ownKeys` returns it and `GetOwnPropertyDescriptor` reports it as enumerable.

## The four parts of a lazy proxy

Every lazy structure in the `lazy` module is built from the same four decisions.

**The target** controls the invariants. Proxy trap results are validated against the target's own properties. A fresh, empty, extensible target produced by `vm.NewObject()` has no own properties, so no trap result can violate an invariant. This is the recommended default. Deviating from it is necessary only when a specific prototype is required, such as an Array target so that `Array.isArray(proxy)` returns `true`.

**The provider** is a Go function that produces a value for a key or index. It receives a string for maps and records, an integer for arrays. It may block, because goja runs JavaScript synchronously on the goroutine that invoked it; a blocking provider simply stalls the JavaScript caller until it returns. Returning `nil` means the property is absent and is mapped to `undefined`.

**The cache** stores the converted `goja.Value`, not the raw Go value. Caching the converted value serves two purposes. It avoids running `Runtime.ToValue` more than once per key, which allocates a `*Object` for every map or slice. It preserves object identity, so `device.wifis === device.wifis` holds and downstream JavaScript caches keyed on identity remain valid. The cache is keyed by the same type the trap receives and is local to one `Proxy` construction, which keeps it bound to one `*goja.Runtime`.

**The traps** are the five described above. The `Get` trap is the lazy read path. The `Has` and `OwnKeys` traps are cheap and must never call the provider. The `GetOwnPropertyDescriptor` trap is where the failure mode lives.

## The enumeration sharp edge

The defining failure mode of a lazy proxy appears during enumeration. `Object.keys` and `for...in` do not stop at `ownKeys`. After obtaining the key list, the engine calls `[[GetOwnProperty]]` for each key to filter by enumerability. In goja this means `proxyObject.keys()` calls `getOwnProp(key)` for every key, and `getOwnPropStr` invokes the `getOwnPropertyDescriptorStr` trap.

If the `GetOwnPropertyDescriptor` trap builds the value, enumeration materialises the entire object. The implementation in `goja/proxy.go` makes this explicit:

```go
// proxyObject.keys() — simplified
for _, key := range ownKeysResult {
    prop := p.val.getOwnProp(key)   // invokes the GetOwnPropertyDescriptor trap
    if prop == nil || prop == _undefined { continue }
    if vp, ok := prop.(*valueProperty); ok && !vp.enumerable { continue }
    keep(key)
}
```

A naive `GetOwnPropertyDescriptor` that calls the provider to populate the descriptor's `Value` therefore triggers the provider for every key during enumeration. The following trace is from the `lazy` module's experiments, with a provider that records which keys it was asked for:

```
== Object.keys(device) ==
  keys: ["name","wifis","battery","uptime"]
  provider called for: [battery uptime]
```

Enumerating a four-key object called the provider for two keys. The other two were already cached from earlier reads in the same runtime. For a record with ten thousand keys, enumeration would call the provider ten thousand times. The laziness that motivated the design is destroyed by the very operation, listing the keys, that a caller would expect to be cheap.

## The fix: flag-only descriptors

The repair is to make `GetOwnPropertyDescriptor` return a descriptor that carries only flags and never a value. The provider is not called. Real values are produced only on the `Get` trap.

```go
// modules/lazy/lazy.go
func flagOnlyDescriptor(enumerable bool) goja.PropertyDescriptor {
    return goja.PropertyDescriptor{
        Enumerable:   goja.ToFlag(enumerable),
        Configurable: goja.FLAG_TRUE,
        // Value and Writable intentionally left unset
    }
}
```

With this descriptor, enumeration stops calling the provider:

```
== Object.keys(device) ==
  keys: ["name","wifis","battery","uptime"]
  provider called for: []
== for..in over device ==
  provider called for: []
== read still works ==
  wifis.length: 3
  provider called for: [wifis]
```

Enumeration is now proportional to the number of keys and performs no provider work. Reads still materialise values lazily, and the cache ensures a second read of the same key does not call the provider again.

## Why the flag-only descriptor survives

The flag-only descriptor is correct, but it is correct for reasons that are not obvious and that a small change can break. Understanding those reasons requires following the descriptor through goja's internals.

`PropertyDescriptor` is a Go struct with a `Value` field and three `Flag` fields: `Writable`, `Configurable`, and `Enumerable`. A `Flag` is tri-state, with values `FLAG_NOT_SET`, `FLAG_FALSE`, and `FLAG_TRUE`. When the `GetOwnPropertyDescriptor` Go callback returns, goja converts the struct to a JavaScript descriptor object through `PropertyDescriptor.toValue` in `goja/object.go`, then processes the result.

The processing path in `proxyObject.proxyGetOwnPropertyDescriptor` calls `complete()` on the descriptor. `complete()` fills gaps: a missing `Value` becomes `undefined`, and a missing `Writable` becomes `FLAG_FALSE`. The flag-only descriptor therefore becomes `{Value: undefined, Writable: FLAG_FALSE, Enumerable: FLAG_TRUE, Configurable: FLAG_TRUE}`.

The final branch then decides what the proxy reports as the own property:

```go
// proxyObject.proxyGetOwnPropertyDescriptor — final branch
if resultDesc.Writable == FLAG_TRUE &&
   resultDesc.Configurable == FLAG_TRUE &&
   resultDesc.Enumerable == FLAG_TRUE {
    return resultDesc.Value
}
return r.toValueProp(trapResultObj)
```

Because `complete()` set `Writable` to `FLAG_FALSE`, the fast path does not run. Execution falls through to `toValueProp` in `goja/builtin_object.go`, which builds a `valueProperty` with `enumerable` set to `true`. That is the value `keys()` inspects, so the key is kept.

The danger is the fast path. If `Writable` were `FLAG_TRUE`, alongside `Configurable` and `Enumerable` both `FLAG_TRUE`, the fast path would run and return `resultDesc.Value`. With no value supplied, that value is `undefined`. The enumeration loop then sees `prop == _undefined` and skips the key. The key vanishes from `Object.keys` even though `ownKeys` returned it and the descriptor declared it enumerable.

This is the trap. A caller who sets `Writable: FLAG_TRUE` intending to make a property writable and enumerable produces a descriptor that enters the fast path and reports `undefined`, silently dropping the key from enumeration. The `flagOnlyDescriptor` helper exists precisely to prevent callers from constructing this descriptor by hand. The rule it encodes is: set `Configurable` to `FLAG_TRUE`, set `Enumerable` explicitly, and leave `Writable` unset.

The regression test `TestMap_EnumerationIsFree` in `modules/lazy/lazy_test.go` asserts that `Object.keys` returns the full declared key set and that the provider is called zero times. It will fail loudly if a goja upgrade changes the `complete()` defaults or the fast-path condition.

## Proxy invariants and the empty target

Proxy traps are not unconstrained. The specification, and goja in `proxy.go`, validate trap results against the target's own properties. The constraints that matter for lazy structures are:

- `ownKeys` must include every non-configurable property of the target.
- When the target is non-extensible, `ownKeys` may not introduce keys the target lacks.
- `get`, `set`, and `getOwnPropertyDescriptor` results must be compatible with any non-configurable, non-writable property of the target.

A fresh target from `vm.NewObject()` is extensible and has no own properties. Every one of these constraints is satisfied vacuously. There are no non-configurable properties to include, no extensibility boundary to respect, and no properties to be compatible with. This is why the empty-extensible target is the recommended default, and why the lazy map and record types use it.

The invariants become load-bearing when the target is not empty. Returning an absent descriptor for a property the target owns as non-configurable causes a panic. The `Array` type encounters this directly.

## The Array length invariant

The lazy array uses an Array target so that `Array.isArray(proxy)` returns `true`. An Array target owns a `length` property that is non-configurable. This single fact prevents the flag-only pattern from transferring directly.

Consider installing a `GetOwnPropertyDescriptor` trap that returns a flag-only enumerable descriptor for valid indices and an empty, absent descriptor for everything else, including `length`. Returning absent for `length` violates the invariant. The target owns `length` as a non-configurable property, and `proxyGetOwnPropertyDescriptor` panics when a trap reports a non-configurable target property as absent.

The `Array` type avoids the conflict by not installing `GetOwnPropertyDescriptor` or `OwnKeys` at all. Those operations fall through to the empty Array target. Indices are surfaced only through `Get`, `GetIdx`, and `HasIdx`. The `length` property is handled in the `Get` trap, which returns the declared length for `"length"` and delegates everything else to the target. The get-invariant for `length` is satisfied because the target's `length` is writable, and the invariant only panics when a non-writable, non-configurable property is reported with a different value.

```go
// modules/lazy/lazy.go — Array traps
cfg := &goja.ProxyTrapConfig{
    GetIdx: func(t *goja.Object, i int, receiver goja.Value) goja.Value {
        if i < 0 || i >= a.Len { return goja.Undefined() }
        return lazyGetInt(vm, cache, a.Provider, i)
    },
    HasIdx: func(t *goja.Object, i int) bool { return i >= 0 && i < a.Len },
    Get: func(t *goja.Object, p string, receiver goja.Value) goja.Value {
        if p == "length" { return vm.ToValue(a.Len) }
        return t.Get(p)
    },
}
```

The consequence is a documented asymmetry. `5 in arr` returns `true` because `HasIdx` is installed, but `Object.getOwnPropertyDescriptor(arr, 5)` returns `undefined` because indices are not own properties of the empty target. For the intended use, iterating with a length-bounded index loop, this is correct and cheap. For consumers that rely on own-property semantics for indices, it is a known limitation.

## Caching, identity, and the single-threaded contract

The cache stores `goja.Value` per runtime. A `goja.Value` is bound to one `*goja.Runtime`. The proxy's own `toValue` panics on cross-runtime use, so a cache must not outlive its runtime or be shared across runtimes. The `lazy` types are configured once and have `ToValue(vm)` called per runtime; each call constructs a fresh proxy with a fresh cache. This is the correct lifetime.

Caching the converted value preserves identity. Without caching, two reads of `device.wifis` would call `ToValue` twice and return two distinct `*Object` values, so `device.wifis === device.wifis` would be `false` and any JavaScript map keyed on the value would misbehave. With caching, the second read returns the same value, and the provider runs at most once per key.

goja runs JavaScript on the goroutine that calls `RunString` or the equivalent. Traps execute on that same goroutine. A blocking provider therefore blocks JavaScript, which is usually acceptable and is the simplest correct behaviour. The contract has two consequences. The cache and the provider's backing store are accessed by one goroutine, so they need no mutex when the proxy is used within one runtime. If a provider needs to fan work out to background goroutines, it must do so in Go and block the JavaScript caller only on the result, not on shared mutable state accessed concurrently.

For data that changes over time, such as a Wi-Fi scan whose result becomes stale, the module exposes the cache as the single source of truth and recommends an explicit invalidation step rather than silent caching. The `Mutable` flag installs `Set` and `DeleteProperty` traps so that writes are captured into the cache and key list, keeping reads and writes consistent within the runtime.

## What is unavoidably materialising

Some operations read values by definition. `JSON.stringify` calls `[[Get]]` on each own enumerable key after looking up `toJSON`. Spread, destructuring with defaults, and `Object.assign` all read values through `[[Get]]`. `structuredClone` reads the values it copies. None of these can be made lazy, because their semantics are defined in terms of the values, not the keys.

The flag-only descriptor keeps the cheap operations cheap. `Object.keys`, `for...in`, and the `in` operator do not read values. `JSON.stringify` and spread do. The following trace from the experiments confirms the boundary:

```
== JSON.stringify(device) ==
  json: {"name":"atom-3r","wifis":["scapegoat","freifunk","eduroam"],"battery":87,"uptime":"3d 4h"}
  provider called for: [toJSON name battery uptime]
```

The `toJSON` lookup appears first, as a `Get` on the object for the `"toJSON"` key. Then each enumerable key is read. For a large lazy object, the implication is that `JSON.stringify` is the wrong serialisation strategy. Consumers should read specific keys, or the module should install a `toJSON` trap that returns a compact, explicit shape.

## The lazy module

The `lazy` package in `go-go-goja/modules/lazy/` turns the mechanism into reusable Go types and a JavaScript module. Three types cover the common shapes.

`Map` is for objects whose keys are known up front. The `Keys` slice drives `OwnKeys`; the `Provider` function produces each value on demand. `Array` is for integer-indexed sequences with a declared length, where element `i` is produced by `Provider(i)`. `Record` is for objects whose key set is itself produced on demand, such as an environment or a live registry; a `Keys` function returns the current key list, and an optional `Has` function provides membership without scanning.

```go
// modules/lazy/lazy.go — the Map type
type Map struct {
    Keys     []string
    Provider func(key string) any
    Mutable  bool
}

func (m *Map) Build(vm *goja.Runtime) goja.Proxy {
    cache := map[string]goja.Value{}
    target := vm.NewObject()
    cfg := &goja.ProxyTrapConfig{
        Get: func(t *goja.Object, p string, receiver goja.Value) goja.Value {
            if containsString(m.Keys, p) { return lazyGetStr(vm, cache, m.Provider, p) }
            return t.Get(p)  // inherited properties (toString, valueOf)
        },
        Has: func(t *goja.Object, p string) bool {
            if containsString(m.Keys, p) { return true }
            v := t.Get(p)
            return v != nil && !goja.IsUndefined(v) && !goja.IsNull(v)
        },
        GetOwnPropertyDescriptor: func(t *goja.Object, p string) goja.PropertyDescriptor {
            if !containsString(m.Keys, p) { return absentDescriptor() }
            return flagOnlyDescriptor(true)
        },
        OwnKeys: func(t *goja.Object) *goja.Object { return strArray(vm, m.Keys) },
    }
    return vm.NewProxy(target, cfg)
}
```

The `Get` trap falls through to the target for non-declared keys, so inherited properties such as `toString` and `valueOf` remain available. This keeps `"" + device` working through the inherited `Object.prototype.toString`. The `GetOwnPropertyDescriptor` trap returns an absent descriptor for non-declared keys, so inherited properties are not reported as own.

The JavaScript surface is `require("lazy")`, with three builders. Each builder accepts a configuration object with a `keys` or `length` field and a `get` function, and constructs the corresponding Go type behind a proxy.

```javascript
const lazy = require("lazy");

const device = lazy.map({
    keys: ["name", "wifis", "battery"],
    get: (k) => {
        if (k === "wifis") return scanWifis();   // runs only on read
        if (k === "battery") return readBattery();
        return "atom-3r";
    }
});

device.wifis;          // triggers the scan, once
Object.keys(device);   // ["name","wifis","battery"], no scan
```

The module is registered in the default registry through a blank import in `pkg/engine/runtime.go`, alongside `fs`, `os`, and the other standard modules. Registration is a build-time concern: a `NativeModule`'s `init` function runs only in binaries that transitively import the package. The canonical import in `runtime.go` is what makes `require("lazy")` available in any runtime built with the engine factory. Forgetting it produces `Error: Invalid module` at runtime, with no compile-time indication.

## Failure modes

**Enumeration materialises every value.** The provider is called for each key during `Object.keys` or `for...in`. Cause: `GetOwnPropertyDescriptor` builds a descriptor with a `Value`. Fix: use `flagOnlyDescriptor`, which returns flags only and never calls the provider.

**Keys vanish from `Object.keys`.** The key is returned by `OwnKeys` but does not appear in `Object.keys`. Cause: the descriptor has `Writable`, `Configurable`, and `Enumerable` all set to `FLAG_TRUE`, so goja takes the fast path and returns `Value`, which is `undefined`, and `keys()` skips `undefined`. Fix: leave `Writable` unset. Use `flagOnlyDescriptor` rather than constructing the descriptor by hand.

**`require("lazy")` throws `Invalid module`.** The module is not registered. Cause: the binary does not import `modules/lazy`, so its `init` never runs. Fix: ensure the blank import in `pkg/engine/runtime.go` is present, or import the package directly in the binary.

**Proxy panic on `getOwnPropertyDescriptor` for `length`.** An `Array`-targeted proxy panics when a trap reports `length` as absent. Cause: the Array target owns `length` as a non-configurable property, and the invariant forbids reporting a non-configurable target property as absent. Fix: do not install `GetOwnPropertyDescriptor` on the `Array` type; surface indices through `Get` and `GetIdx` only.

**Cross-runtime panic.** A cached `goja.Value` used in a different runtime panics with `Illegal runtime transition`. Cause: values are bound to one runtime. Fix: construct a fresh proxy per runtime through `ToValue(vm)`; do not share a cache or a `Proxy` across runtimes.

**`getOwnPropertyDescriptor(k).value` is `undefined`.** The descriptor reports the key as enumerable, but its `value` is `undefined` while reading `obj.k` returns the real value. Cause: the flag-only descriptor carries no value; the real value comes from `[[Get]]`. This is the documented tradeoff. `Object.assign` and spread use `[[Get]]` and receive the real value; only explicit `getOwnPropertyDescriptor(k).value` is affected.

## Working rules

- Implement `Get`, `Has`, `OwnKeys`, and `GetOwnPropertyDescriptor`. Leave the rest `nil` unless a specific behaviour is required.
- `Has`, `OwnKeys`, and `GetOwnPropertyDescriptor` must not call the provider. Only `Get` materialises values.
- Return a flag-only descriptor from `GetOwnPropertyDescriptor`. Set `Configurable` to `FLAG_TRUE`, set `Enumerable` explicitly, and leave `Writable` unset. Use the `flagOnlyDescriptor` helper.
- Use a fresh, empty, extensible target for maps and records. Use an Array target only when `Array.isArray` must return `true`, and do not install `GetOwnPropertyDescriptor` on it.
- Cache `goja.Value` per runtime. Construct a fresh proxy per runtime through `ToValue(vm)`.
- Treat the proxy as single-goroutine. Block the JavaScript caller on provider results; do background work in Go.
- For an `Array`, surface indices through `Get` and `GetIdx`. Document that indices are not own properties.

## Related notes

- [[ARTICLE - Designing DSLs with go-go-goja - Go-Backed JavaScript APIs]] — the broader pattern of exposing Go logic to JavaScript through go-go-goja, of which lazy data structures are one instance.
- [[PROJ - go-go-goja Node-like Primitives - Technical Deep Dive]] — the runtime ownership and module registration machinery that `require("lazy")` depends on.
- [[PROJ - goja-text - Template and HTML Rendering Module]] — a sibling native module; the same `NativeModule` / `Loader` / `TypeScriptDeclarer` pattern.
