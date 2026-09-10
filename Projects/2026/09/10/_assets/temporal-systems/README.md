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
