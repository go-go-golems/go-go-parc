# Next change (gridflow)

Add an operation `clip(lo, hi)` (values below `lo` become `lo`, above `hi` become `hi`; neutral when both are None), and
make the eviction policy selectable at construction (`Engine(cache_bytes=..., policy="lru" | "size")`, where "size"
evicts the largest values first).
