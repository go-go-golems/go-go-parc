# Benchmark report

Generated: `2026-08-04T23:22:00.385Z`.

## Environment

- Node: `v22.16.0`
- Platform: `linux/x64`
- CPU reported by the host: `AMD EPYC 9V74 80-Core Processor`
- Logical CPUs visible: `5`
- Total memory visible: `6,368,813,056` bytes
- Clock: `performance.now`
- Warm-up runs per engine and size: `1`

The benchmark compiles deterministic chain-and-skip graphs. It excludes browser rendering, network work, dynamic resource allocation, and topology editing. Sizes and repetitions can be configured with `P06_BENCH_SIZES` and `P06_BENCH_REPEATS`.

## Results

| Ports | Links | Samples | Reference median (ms) | Reference p95 (ms) | Optimized median (ms) | Optimized p95 (ms) |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 8 | 20 | 0.081 | 0.274 | 0.041 | 0.144 |
| 100 | 94 | 20 | 0.592 | 1.089 | 0.399 | 0.639 |
| 1,000 | 947 | 8 | 15.594 | 15.889 | 16.015 | 19.306 |
| 5,000 | 4,739 | 4 | 324.694 | 334.671 | 314.942 | 319.697 |
| 10,000 | 9,480 | 4 | 1366.365 | 1375.172 | 1329.384 | 1334.321 |

## Interpretation

The optimized compiler does not uniformly or materially outperform the reference compiler in this prototype. At some sizes it is faster; at 1,000 ports in this run it is slightly slower. Both engines spend substantial time in shared validation, sorting, canonical class construction, hashing, and normalized-plan production. Union-find improves the asymptotic closure operation, but that operation is not the dominant cost for these fixtures and implementation choices.

This is a useful negative result. It prevents a false performance narrative and suggests three next experiments:

1. profile closure separately from canonical plan construction;
2. replace quadratic or repeated canonicalization work before changing the connectivity algorithm again;
3. incrementally maintain normalization and persistent-ID matching across small edits rather than recompiling the complete plan.

The results are empirical observations from one host. The sample counts at the largest sizes give only coarse tail estimates, and the benchmark does not control garbage collection or CPU frequency.
