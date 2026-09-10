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
