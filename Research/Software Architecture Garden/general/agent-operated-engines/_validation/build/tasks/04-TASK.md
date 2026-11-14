# Task: stencilpipe — compute only the part of a grid you ask for

Build `stencilpipe`, a Python 3 library (standard library only, no network, no pip installs) for pipelines over large
2D grids of floats (elevation maps, sensor fields). Users ask for small windows of results far more often than for
whole grids, so a request for a window must compute only what that window needs, and must give exactly the values a
whole-grid computation would give there. Apply the pattern described in `CHAPTER.md`; this is the situation it is for.

Work only inside this directory. Write tests under `tests/` and run them (`python3 -m unittest discover -s tests`).
Keep `DIARY.md` as described in `DIARY-FORMAT.md`.

## Required public interface (other code will be tested against it)

Package `stencilpipe` (`stencilpipe/__init__.py` exports these names). A grid is a list of rows of floats; `grid[y][x]`.
A window is a tuple `(x, y, w, h)` in the coordinates of the node it is asked of; windows are clipped to the node's
extent.

- `demo_engine() -> Engine` with these operations (their behaviour on whole grids is fixed; implement them so that a
  window gives the same values):
  - `add(k)`: `out[y][x] = in[y][x] + k`.
  - `box(r)`: the mean of `in` over the square of radius `r` around `(x, y)`, counting only cells inside the grid.
  - `dx()`: `in[y][min(x+1, W-1)] - in[y][max(x-1, 0)]` (a horizontal difference; it reads only along x).
  - `half()`: a grid of size `ceil(W/2) × ceil(H/2)`; `out[y][x]` is the mean of the input cells
    `(2x..2x+1, 2y..2y+1)` that exist.
  - `normalize()`: `out[y][x] = in[y][x] / m`, where `m` is the maximum of the whole input grid (0 stays 0 if `m` is 0).
- `eng.source(grid) -> Node`; `node.call(name, **args) -> Node` (building computes nothing).
- `eng.evaluate(node, window=None) -> grid`: the whole result, or the rows of the window.
- `eng.evaluate_many(node, windows) -> list of grids`: several windows of one node.
- `eng.reset_counters()` and `eng.cells_computed() -> int`: the total number of output cells that operations computed
  since the last reset (sources do not count). Every operation must count every cell it computes.

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
