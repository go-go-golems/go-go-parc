# Task: gridflow — a lazy, cached engine for grid computations

Build `gridflow`, a Python 3 library (standard library only, no network, no pip installs) that analysts and an
assistant use to compute on small 2D grids of floats (think heat maps, sensor fields). They build pipelines step by
step, often repeating the same steps in new scripts, and ask for results piecemeal; computations can be slow. Apply
the pattern described in `CHAPTER.md`; this is the situation it is for.

Work only inside this directory. Write tests under `tests/` and run them (`python3 -m unittest discover -s tests`).
Keep `DIARY.md` as described in `DIARY-FORMAT.md`.

## Required public interface (other code will be tested against it)

Package `gridflow` (`gridflow/__init__.py` exports these names). A grid is a list of rows of floats (or tuples).

- `Engine(cache_bytes=10_000_000)`.
- `eng.op(name, fn, version=1, identity=None)` registers an operation. `fn(inputs, args, ctx)` receives the input
  grids (a list), the keyword arguments (a dict) and a context with `ctx.scale` (the evaluation scale) and
  `ctx.warn(message)`; it returns a grid. `identity(args) -> bool`, if given, says the arguments are neutral (the
  output equals the first input). Registering the same name again replaces the operation.
- `eng.source(grid) -> Node`: a source node. Two sources with equal content are the same node.
- `node.call(name, *inputs, **args) -> Node`: a node applying operation `name` to `node` (and any further input
  nodes) with keyword arguments. Building a node never runs an operation.
- `eng.evaluate(node, scale=1.0) -> Result` with `.value` (a grid) and `.warnings` (a list of strings). `scale` is in
  (0, 1]. On failure it raises `EvalError` whose message names the failing operation.
- `eng.runs(node) -> int`: how many times that node's operation actually ran.
- `eng.stats() -> dict` with integer keys `hits`, `misses`, `bytes`, `evictions`.
- `eng.within(node, mask, build) -> Node`: applies the sub-pipeline that `build(placeholder)` returns only where
  `mask` (a grid node of 0/1) is 1, and keeps `node`'s values elsewhere; `build` receives a placeholder node and returns
  a node built from it.

Include a few demo operations in `gridflow.demo_engine()`: `add` (adds a constant `k`), `gain` (multiplies by `k`;
neutral when `k == 1`), `blur` (box mean with `radius` in grid cells at scale 1; at a smaller scale the radius shrinks
proportionally), and `threshold` (1 where value > `t`, else 0).

When you are done, give a final message containing exactly one JSON object in a ```json fenced block:

```json
{
  "summary": "what you built, in three sentences",
  "files": ["paths you created"],
  "pattern_mapping": {"<participant from CHAPTER.md>": "where it is in your code"},
  "notes_applied": ["implementation notes from CHAPTER.md you applied, and how"],
  "tests": "how many tests you wrote, and the last result",
  "chapter_feedback": ["where the chapter helped, misled you or left you to guess"]
}
```
