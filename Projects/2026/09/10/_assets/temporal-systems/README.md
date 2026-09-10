# Engineering Temporal Systems — executable educational examples

These examples accompany the eight-chapter writing program. They are **not product code** and are not evidence of browser, camera or hardware performance. Full chapters and other modules are still in progress.

## Timeline model

Requires Python 3 with only its standard library. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 timeline.py
```

`timeline.py` uses integer UTC microseconds and rational viewport arithmetic, independently selects numeric and image resolution, enumerates canonical half-open tiles, bounds row/rectangle work, and demonstrates stale-generation rejection after a cancelled pan. Fractions are converted to float only for output geometry. Integer rounding uses Python's ties-to-even rule; this is an educational model rather than a bit-identical translation of JavaScript rounding.

`outputs/timeline-tests.log` retains four passing tests, including 1,000 seeded coordinate/zoom cases. `outputs/timeline-demo.json` retains the day/zoom/pan/cancel example. Run results are model outputs. The first day view selects numeric L8 and image L11, six visible/overscan rows and 8,100 extents. Its 129,600-byte four-float32 equivalent is **not measured Python heap memory**.

The example checks a 512-reference limit, a 50,000-candidate instance limit and a 512 KiB equivalent packed-output limit before geometry allocation. The latter is stricter than the instance cap for this four-scalar format. It does not implement encoded caches, real textures, authority-scoped resource loading or a production parser. Those remain separate systems discussed in the chapter brief. The engine's publication predicate models generation alone; it must not be reused as a complete authorization check.

## Clock and synchronization model

`python3 clocks.py` emits the four-processor trace and the old/repaired moving-target comparison. `outputs/clocks-demo.json` and `outputs/clocks-tests.log` retain outputs; the shared suite now has nine tests. Clocks use injected monotonic milliseconds, integer UTC microseconds, explicit mapping epochs and rational tick conversion.

The generic scenario advances in 20 ms steps for fourteen seconds, with zero additional observation delay, requested seek delays of 0/80/120/40 ms and 200 ms initial decode readiness after seek application. Completions are polled on subsequent ticks, so zero delay becomes 20 ms. One processor stalls, one resets its timestamp epoch, and one has a two-second gap. Every processor ends visible, but the stalled processor's maximum observed error is 450 ms; final state must not hide that excursion.

The model enforces its cover predicate every tick; the product's reveal tolerance is not a continuous invariant. It is not a browser decoder, physical capture model, authorization state machine or arbitrary-delay stability proof. The separate moving-target experiment intentionally assumes 120 ms seek application and 200 ms subsequent decode latency. Under those assumptions, progressing behind cover changes first-frame lag from 320 to 120 ms. Other latency/capacity assumptions can fail to converge.

## Mergeable summaries

`python3 summaries.py` emits the sample/duration weighting examples, Decimal variance comparison, exact-median counterexample, canonical sparse hierarchy and disjoint coverage partition. `outputs/summaries-demo.json` and `outputs/summaries-tests.log` retain outputs. The shared suite now has thirteen tests, including 300 seeded partition/dropout cases and mixed-scale/large-offset checks.

The stable pairwise variance accumulator is an educational extension absent from the product pyramid. Merges require disjoint observations and unique `(UTC, identity)` ordering keys; the fixed-size summary cannot detect arbitrary duplicates. Missing points are empty leaves, not valid zeros, and no continuous coverage is inferred from sample spacing. Coverage intervals are separately supplied, nonoverlapping evidence.

The eight `1e12 + i/8` values produce centered M2 0.65625 in three tested reduction shapes and the Decimal reference; the naive squared-sum difference produces zero. This selected result is not a promise of exact binary64 behavior on arbitrary inputs. The balanced reducer materializes its input (O(n) storage); sparse retained hierarchies use O(depth * K) worst-case work/storage, with 4096 initial buckets and depth 16 admitted.

## Bounded asynchronous scheduler

`python3 scheduler.py` emits useful/blocked workloads and the percentile counterexample. `outputs/scheduler-demo.json` and `outputs/scheduler-tests.log` retain results. Eighteen shared tests now pass, including twenty seeded scheduler interleaving runs and independent generation/revision/authority invalidations.

Defaults: two active jobs, one per key, four waiting jobs, 8192 logical owned body bytes, 1024 bytes/second shared refill and 512-byte burst credit. The event clock admits 256 pending callbacks, diagnostic traces retain 256 entries, and completion latency retains 64 values. Bodies retain their full reservation until finish/abort, not just until byte submission. Downstream cache/render ownership and physical memory are not modeled.

Both six-second experiments run 61 pumps. The useful run publishes four 1024-byte bodies with completion p95 3550 ms; the blocked run publishes none and has no latency observations. Explicit terminal cleanup leaves zero owned bytes in both. Pinned-cache tests refuse eviction until lease release. The library assumes trusted finite configuration/metadata, not hostile-input protocol parsing, and makes no starvation-freedom or wire-throughput claim.
