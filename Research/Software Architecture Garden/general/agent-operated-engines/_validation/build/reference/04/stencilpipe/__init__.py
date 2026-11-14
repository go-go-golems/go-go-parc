"""Reference implementation for the chapter-04 build task (hidden-test yardstick)."""
import math


def clip(win, ext):
    x, y, w, h = win; W, H = ext
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    return (x0, y0, max(0, x1 - x0), max(0, y1 - y0))


class View:
    """Values of a node over a window, read by absolute coordinates."""
    def __init__(self, win, rows, ext):
        self.x, self.y = win[0], win[1]; self.rows, self.ext = rows, ext
    def at(self, x, y):
        return self.rows[y - self.y][x - self.x]


class Node:
    def __init__(self, eng, name, args, inputs, grid=None):
        self.eng, self.name, self.args, self.inputs, self.grid = eng, name, args, inputs, grid
        self.whole = None
        if grid is not None:
            self.ext = (len(grid[0]), len(grid))
        else:
            self.ext = OPS[name][3](inputs[0].ext)
    def call(self, name, **args):
        return Node(self.eng, name, args, [self])


def grow(win, mx, my):
    return (win[0] - mx, win[1] - my, win[2] + 2 * mx, win[3] + 2 * my)


def k_add(win, ins, a):
    return [[ins[0].at(x, y) + a["k"] for x in range(win[0], win[0] + win[2])] for y in range(win[1], win[1] + win[3])]


def k_box(win, ins, a):
    r = a["r"]; W, H = ins[0].ext; out = []
    for y in range(win[1], win[1] + win[3]):
        row = []
        for x in range(win[0], win[0] + win[2]):
            vals = [ins[0].at(xx, yy) for yy in range(max(0, y - r), min(H, y + r + 1)) for xx in range(max(0, x - r), min(W, x + r + 1))]
            row.append(sum(vals) / len(vals))
        out.append(row)
    return out


def k_dx(win, ins, a):
    W, _ = ins[0].ext
    return [[ins[0].at(min(x + 1, W - 1), y) - ins[0].at(max(x - 1, 0), y) for x in range(win[0], win[0] + win[2])]
            for y in range(win[1], win[1] + win[3])]


def k_half(win, ins, a):
    W, H = ins[0].ext; out = []
    for y in range(win[1], win[1] + win[3]):
        row = []
        for x in range(win[0], win[0] + win[2]):
            vals = [ins[0].at(xx, yy) for yy in (2 * y, 2 * y + 1) for xx in (2 * x, 2 * x + 1) if xx < W and yy < H]
            row.append(sum(vals) / len(vals))
        out.append(row)
    return out


def k_norm(win, ins, a):
    W, H = ins[0].ext
    m = max(ins[0].at(x, y) for y in range(H) for x in range(W))
    return [[(ins[0].at(x, y) / m if m else 0.0) for x in range(win[0], win[0] + win[2])] for y in range(win[1], win[1] + win[3])]


same = lambda ext: ext
OPS = {  # kernel, footprint(win, args), _, extent(input ext)
    "add": (k_add, lambda w, a: w, None, same),
    "box": (k_box, lambda w, a: grow(w, a["r"], a["r"]), None, same),
    "dx": (k_dx, lambda w, a: grow(w, 1, 0), None, same),
    "half": (k_half, lambda w, a: (2 * w[0], 2 * w[1], 2 * w[2], 2 * w[3]), None, lambda e: (math.ceil(e[0] / 2), math.ceil(e[1] / 2))),
    "normalize": (k_norm, lambda w, a: "whole", None, same),
}


class Engine:
    def __init__(self):
        self.cells = 0
    def source(self, grid):
        return Node(self, "source", {}, [], [[float(v) for v in r] for r in grid])
    def reset_counters(self):
        self.cells = 0
    def cells_computed(self):
        return self.cells
    def _whole(self, n):
        if n.grid is not None:
            return n.grid
        if n.whole is None:
            n.whole = self._compute(n, (0, 0) + n.ext)
        return n.whole
    def _compute(self, n, win):
        kernel, fp, _, _ = OPS[n.name]
        f = fp(win, n.args)
        inp = n.inputs[0]
        if f == "whole":
            iv = View((0, 0), self._whole(inp), inp.ext)
        else:
            fw = clip(f, inp.ext)
            iv = View(fw, self._window(inp, fw), inp.ext)
        out = kernel(win, [iv], n.args)
        self.cells += win[2] * win[3]
        return out
    def _window(self, n, win):
        win = clip(win, n.ext)
        if n.grid is not None or n.whole is not None:
            g = self._whole(n)
            return [row[win[0]:win[0] + win[2]] for row in g[win[1]:win[1] + win[3]]]
        return self._compute(n, win)
    def evaluate(self, node, window=None):
        if window is None:
            return [r[:] for r in self._whole(node)]
        return self._window(node, window)
    def evaluate_many(self, node, windows):
        return [self.evaluate(node, w) for w in windows]


def demo_engine():
    return Engine()
