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

## Archive index and real media

`PYTHONDONTWRITEBYTECODE=1 python3 build_media.py` regenerates only owned `outputs/media/no-b/` and `outputs/media/b-frames/` fixtures. It requires FFmpeg/ffprobe with libx264 and the named DejaVu font. Each variant is six seconds, 160×90 at 10 fps, three two-second fMP4 fragments plus initialization. Every subprocess has a 30-second timeout; each variant's final output is checked below 4 MiB. The generation audit retains commands and versions; temporary concatenations are deleted.

`archive_index.py` resolves a target at UTC anchor +2.75 s into init plus a whole second-fragment range, decodes from that fragment's independent start and discards eight preceding frames. Both variants retain source frame 28 at UTC +2.8 s. Actual retained PTS differs (2.8 s versus 3.0 s) because the reordered fixture has a 0.2-second presentation offset. Probe frame metadata shows 36 B pictures in the reordered clip; 60 packets with PTS != DTS is a different count.

The shared suite now has 21 tests and uses retained real-media evidence. Regenerate media before running those tests if assets are absent. `outputs/archive-tests.log`, packet/frame JSON, decode logs, plans and PNGs retain the verification. Plans use whole-fragment byte ranges; packet positions refer to temporary init+fragment files and are not arbitrary payload grants. This is a bounded closed-GOP educational index, not an authorization server or the product's fragment/PDT client.

## Applied historical coordination

`python3 historical.py` emits a distinct archive/session scenario and writes `outputs/historical-availability.svg` from its model indexes. It reuses the clock/controller/barrier, bounded event queue and archive resolver rather than duplicating them. The shared suite now has 24 tests; retained output/log are `historical-demo.json` and `historical-tests.log`.

The scenario opens four cameras, releases a two-second barrier with one camera late, encounters a camera-specific gap, commits two in-window seeks, pauses/resumes at 2x, reopens outside the admitted window and closes. It creates/releases two sessions, reuses one twice, rejects sixteen stale reports and performs one hard drift correction. Observation delay is explicitly paired with the master sampled at the observation time.

Indexes use fictional media names/lengths; they are not generated-file evidence. Observations are continuous modeled playback positions, not decoded frame timestamps. `visible` is a policy flag, not compositor evidence. The model continuously reevaluates its tolerance, unlike the product's reveal-only gate. The separate archive-coordinate moving-target traces reuse Chapter 2's selected delay model and do not constitute an additional browser measurement.

## Presentation eligibility and lifetimes

`python3 presentation.py` emits two required races and a 120-permutation result. `outputs/presentation-demo.json` and `outputs/presentation-tests.log` retain the evidence. Current full suite: **30 tests**; smaller counts above describe earlier chapter milestones.

The immutable transition function consumes trusted model events and emits effects. The executor reuses `EventClock`, tracks four logical resources per session, and delays disposal by two model milliseconds. Both close and revoke invalidate eligibility before disposal; old callbacks at 11 ms are rejected while all four resources remain owned, then each resource is released once. The scenario drains obsolete expiry timers too, leaving no events.

This is not a browser decoder or production security service. `open` is trusted completed admission, frame metadata is injected, visibility is explicit, and expiry uses an exact model clock. The strict frame-callback evidence policy and independent document visibility are stronger than the product's fallback/IntersectionObserver-only component path. Resource/event limits reject excess fixture input before committing a transition; production revocation needs independently available control/cleanup capacity.
