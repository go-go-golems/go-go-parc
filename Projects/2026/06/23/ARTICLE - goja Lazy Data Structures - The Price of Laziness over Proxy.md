---
title: "goja Lazy Data Structures: The Price of Laziness over Proxy"
aliases:
  - goja Lazy Proxy Benchmark
  - lazy Proxy enumeration cost
  - goja flag-only descriptor benchmark
tags:
  - article
  - goja
  - go
  - javascript
  - performance
  - benchmark
  - js-bindings
  - lazy-evaluation
  - architecture
status: active
type: article
created: 2026-06-23
repo: /home/manuel/workspaces/2026-06-23/benchmark-goja-proxy-object
---

# goja Lazy Data Structures: The Price of Laziness over Proxy

This article measures and explains the performance of the `go-go-goja` `lazy` module, which exposes lazily-materialised Go data to JavaScript through an ES6 `Proxy`. The `lazy` module was designed around a specific claim, recorded in [[ARTICLE - Lazy Data Structures over goja Proxy - Go-Backed On-Demand JavaScript Objects|the lazy data structures design]]: a flag-only `GetOwnPropertyDescriptor` trap makes `Object.keys()` and `for...in` enumeration free of provider work, so a JavaScript caller can list an object's keys without triggering the Go provider (which may scan Wi-Fi, query a database, or page a large result set). This article benchmarks that claim and quantifies what the laziness costs in absolute terms.

The benchmark workspace is `/home/manuel/workspaces/2026-06-23/benchmark-goja-proxy-object`. The runnable benchmark is `go-go-goja/perf/goja/phase4_lazy_bench_test.go`. The full docmgr ticket is `GOJA-LAZY-BENCH`. A self-contained HTML report with the same figures lives at `go-go-goja/ttmp/2026/06/23/GOJA-LAZY-BENCH--benchmark-lazy-data-structures-over-goja-proxy/various/06-lazy-report.html`.

> [!summary]
> - The design goal is met and measurable. Enumerating a 100-key lazy map calls the Go provider **0 times**; the same enumeration through a naive value-materialising descriptor calls it **100 times**. That count is a deterministic code-path invariant.
> - "Free of provider work" is not "free." Lazy enumeration costs **15.8×** an eager object's `Object.keys`, because the Proxy constructs a descriptor object for every key. The flag-only descriptor eliminates the *expensive* work (the provider); it does not eliminate the *machinery* work.
> - `provider/op` is the load-bearing signal of this study, the direct analogue of `allocs/op` in [[ARTICLE - goja Binding Mechanisms - The Cost of Exposing Go to JavaScript|the binding-mechanism benchmark]]. It is identical across every sample. Nanoseconds corroborate it; the provider-call count proves laziness.
> - `JSON.stringify` reads every value and calls the provider once per key. That materialisation is inherent to serialisation, not a flaw in the descriptor.

## Why this note exists

The `lazy` module puts a Go value behind a Proxy so that JavaScript reads a property only at the moment it is read. Its central design decision is a *flag-only* `GetOwnPropertyDescriptor` trap: the trap reports a key as enumerable without building the value, so that `Object.keys()` and `for...in` can enumerate keys without ever calling the Go provider. The design article asserted this and stopped. The open question was whether the claim holds under measurement, and what the laziness costs in wall-clock terms once the provider work is removed.

The article is durable because the trap dispatch structure is a fixed property of the goja Proxy implementation. The nanoseconds will drift with hardware and goja versions, but the structure — which operations read values and which do not — does not change.

## The system under measurement

The `lazy` module exposes three Go types to JavaScript as Proxies: `Map` (string-keyed, keys known up front), `Array` (integer-indexed with a reported length), and `Record` (dynamic key set). Each installs a small set of traps: `Get` (the lazy read path), `Has` (cheap membership), `OwnKeys` (the key list), and `GetOwnPropertyDescriptor` (the flag-only descriptor). The provider is a Go function that produces a value for a key on demand; the module memoises the converted `goja.Value` so repeated reads return identical objects.

The benchmark holds everything constant except the binding and the operation. A fresh goja runtime is created for each configuration, a one-expression JavaScript program is compiled once, and that program is run repeatedly. Compilation and runtime construction sit outside the timed loop, so the only thing measured is the act of touching the lazy object. The provider returns a pre-built string, so the measurement isolates trap and dispatch overhead rather than string formatting. This is the conservative choice: a real provider doing I/O would widen every gap in the lazy direction, because the provider calls the naive path performs would each be far more expensive than the few hundred nanoseconds measured here.

> [!important]
> The load-bearing signal is `provider/op`. Each benchmark reports a custom metric: the number of times the Go provider was called per operation. It is a deterministic invariant — identical across all five samples, because it is a property of the code path. Where a configuration claims to be lazy, `provider/op = 0` is the proof. Where it materialises, `provider/op` equals the key count.

## Reads: cached is cheap, cold pays the provider

A single property read is the cheapest operation, and the cached read is the realistic hot path. Once a key has been read once, its `goja.Value` is memoised; every subsequent read returns the cached value with no provider call and no `ToValue`. A cached lazy read costs **582 ns** — about **3.7×** the **159 ns** of reading an eager object, paying one extra allocation for the Proxy machinery.

![[lazy-bench-fig4-read-latency.png]]

*Figure 1. Single-read latency by mechanism (min—median—max, mean as a tick). The cached lazy read sits at the Proxy machinery floor (2 allocs, 0 provider). The cold, non-caching read pays the provider once (1 provider/op) and re-converts the value each time.*

The cold read — a Proxy with no cache, so every read calls the provider and re-converts — costs **1161 ns** with 4 allocations and 1 provider/op. This is the cost a lazy read pays the first time, and what a non-caching lazy object pays every time. The module caches by default, so the cold cost is paid once per key per runtime; the steady state is the cached read.

## Enumeration: the flag-only win, measured

This is the regime the flag-only descriptor was built for. Enumerating a 100-key lazy map through the module's descriptor calls the provider **0 times**. The same enumeration through a naive value-materialising descriptor calls it **100 times** — once per key.

![[lazy-bench-fig1-enum-cost.png]]

*Figure 2. `Object.keys` cost per mechanism, log scale. Provider-call counts are annotated on each bar. The flag-only and naive bars are close in time because the provider is cheap; they are worlds apart in provider work — 0 versus 100. The eager bar is far left: a plain object enumerates in a fraction of the time because it skips the per-key descriptor trap entirely.*

| Mechanism | ns / Object.keys | allocs | provider/op |
| --- | ---: | ---: | ---: |
| Eager object (plain JS object) | 37,874 | 115 | 0 |
| Lazy map (flag-only, the module) | 596,866 | 1,033 | 0 |
| Naive lazy (materialising descriptor) | 643,475 | 1,333 | 100 |
| Lazy map (for...in) | 731,646 | 1,470 | 0 |

The naive descriptor is only modestly slower in nanoseconds, because the provider here does trivial work. With a real provider, those 100 calls would dominate the measurement. The provider-call count, not the time, is then the decision metric.

> [!note]
> Lazy enumeration is **not** faster than eager enumeration — it is **15.8×** slower, because the Proxy builds a descriptor object for every key. The flag-only descriptor wins on the dimension that matters: it does **zero** provider work, where the naive descriptor does **N**. When the provider is a Wi-Fi scan, that is the difference between listing keys instantly and scanning 100 times. When the provider is a pre-built string, the machinery cost dominates and an eager snapshot would be faster. Choose by what the provider does, not by the nanoseconds alone.

## The deterministic signal

Plotting `provider/op` across every operation collapses the report to a single picture. Operations that read values materialise them; operations that only list keys do not. The boundary is sharp and it is exactly where the design said it would be.

![[lazy-bench-fig2-provider-signal.png]]

*Figure 3. Provider calls per operation. Green bars perform no provider work; orange bars materialise values. `Object.keys` and `for...in` sit at zero; `JSON.stringify` sits at the key count because it reads every value; a cold read sits at one.*

This chart is the reason the report can make confident claims from five-sample runs. Nanosecond measurements wobble; `provider/op` pins each configuration to a fixed position, and the position is determined entirely by whether the operation reads values. A future goja version may change the nanoseconds; it cannot change the fact that `Object.keys` does not read values and `JSON.stringify` does.

## Scaling

Enumeration cost grows linearly with the key count, and the provider-call count stays at zero throughout.

![[lazy-bench-fig3-scaling.png]]

*Figure 4. `Object.keys` on a lazy map as the key count grows. The cost is linear in N (roughly 4 µs per key), and provider/op is 0 at every scale. The allocation count grows at the same rate — about 10 allocations per key — which is the descriptor-construction cost the flag-only design carries.*

The per-key cost is stable: from 10 to 1000 keys, each key adds roughly 4 µs and 10 allocations. A 1000-key lazy map enumerates in under four milliseconds without a single provider call. For a provider that scans or queries, that is the difference between an instant key listing and a thousand fetches.

## Serialisation is inherently materialising

`JSON.stringify` is the operation the flag-only descriptor cannot help. By definition, serialisation reads every value, so it calls the provider once per key. The measurement uses a non-caching lazy map so the per-call cost is visible; with the module's cache, only the *first* stringify materialises, and subsequent ones read cached values.

| Mechanism | ns / stringify | allocs | provider/op |
| --- | ---: | ---: | ---: |
| Eager object | 41,714 | 425 | 0 |
| Lazy map (no cache) | 239,059 | 1,648 | 101 |

The lazy stringify reads every value (101 provider/op) and costs **5.7×** the eager stringify. This is not a flaw in the descriptor; it is the definition of serialisation. The guidance follows: for large lazy objects, do not `JSON.stringify` the whole proxy. Read specific keys, or install a `toJSON` trap that returns an explicit, compact shape.

## Working rules

- **`provider/op` is the decision metric for lazy objects**, not nanoseconds. A configuration is lazy when `provider/op = 0` for the operation in question. Measure it; it is deterministic.
- **Enumeration is free of provider work, not free of machinery work.** Reserve lazy Proxies for cases where the point is to avoid paying for unread values. For tight loops that enumerate millions of times over cheap providers, snapshot eagerly.
- **Cache the converted `goja.Value`, not the raw Go value.** The cache preserves identity (`obj.k === obj.k`) and avoids re-running `ToValue`. It is per-runtime by necessity; construct a fresh proxy per runtime.
- **Do not serialise large lazy proxies.** `JSON.stringify` reads every value. Install a `toJSON` trap or read specific keys instead.
- **The flag-only descriptor is load-bearing.** A value-materialising descriptor makes enumeration do N provider calls. Use the module's `flagOnlyDescriptor` helper rather than constructing descriptors by hand.

## Threats to validity

The measurements are single-threaded, interpreted goja numbers taken on a shared laptop. Absolute latency is illustrative (±10–20%); the `provider/op` counts and the ratios between mechanisms are robust. Five samples is enough to show the enumeration ordering and the deterministic provider counts. The provider does trivial work, which makes the naive path's 100 calls look cheap; a real provider would make the flag-only win far larger than the nanoseconds suggest. Enumeration is measured at N=100 with scaling to 1000; the linear scaling in Figure 4 makes the behaviour at other sizes predictable.

## Reproducibility

The harness is `go-go-goja/perf/goja/phase4_lazy_bench_test.go`. From the `go-go-goja` module root:

```
go test ./perf/goja -run '^$' \
  -bench 'LazyRead|LazyEnumeration|LazyScale|LazyMaterialize' \
  -benchtime=1s -count=5 -benchmem | tee raw.txt
```

The ticket also ships the full pipeline: `03-parse-lazy-stats.py` (raw → stats), `04-lazy-charts.py` (SVG figures), `05-lazy-report-template.html` + `06-make-lazy-report.py` (fill the template). The figures embedded in this note were produced by that pipeline and copied into `Attachments/`. The self-contained HTML report with the same figures is `various/06-lazy-report.html` in the ticket.

## Related notes

- [[ARTICLE - Lazy Data Structures over goja Proxy - Go-Backed On-Demand JavaScript Objects]] — the design article this benchmark validates: the Proxy trap model, the enumeration sharp edge, and the flag-only descriptor fix.
- [[ARTICLE - goja Binding Mechanisms - The Cost of Exposing Go to JavaScript]] — the sibling benchmark of every goja Go→JS binding mechanism, whose `allocs/op` invariant is the direct analogue of this article's `provider/op`.
