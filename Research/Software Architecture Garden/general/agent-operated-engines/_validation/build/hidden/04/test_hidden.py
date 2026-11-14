"""Hidden tests for the stencilpipe build task (chapter 04). Run with PYTHONPATH=work."""
import math, random, unittest
import stencilpipe

random.seed(4)
W, H = 60, 45
GRID = [[round(random.uniform(0, 10), 3) for _ in range(W)] for _ in range(H)]


def cut(g, win):
    x, y, w, h = win
    return [row[x:x + w] for row in g[y:y + h]]


def close(a, b):
    return len(a) == len(b) and all(len(r) == len(s) and all(abs(p - q) < 1e-9 for p, q in zip(r, s)) for r, s in zip(a, b))


CHAINS = {
    "add": lambda s: s.call("add", k=2),
    "box": lambda s: s.call("box", r=3),
    "dx": lambda s: s.call("dx"),
    "box_box": lambda s: s.call("box", r=2).call("box", r=3),
    "add_box_dx": lambda s: s.call("add", k=1).call("box", r=1).call("dx"),
    "half_box": lambda s: s.call("half").call("box", r=2),
    "box_half": lambda s: s.call("box", r=2).call("half"),
    "box_normalize": lambda s: s.call("box", r=2).call("normalize"),
    "normalize_box": lambda s: s.call("normalize").call("box", r=1),
}


def windows_for(n_w, n_h):
    return [(5, 5, 7, 6), (0, 0, 5, 4), (n_w - 6, n_h - 5, 6, 5), (0, n_h - 3, 4, 3), (n_w - 1, 0, 1, 1), (10, 3, 1, 1)]


class Exactness(unittest.TestCase):
    def test_window_equals_cut_of_whole(self):
        for name, mk in CHAINS.items():
            e = stencilpipe.demo_engine(); n = mk(e.source(GRID))
            full = e.evaluate(n)
            for win in windows_for(len(full[0]), len(full)):
                e2 = stencilpipe.demo_engine(); n2 = mk(e2.source(GRID))
                self.assertTrue(close(e2.evaluate(n2, win), cut(full, win)), f"{name} {win}")

    def test_many_windows_equal_cuts(self):
        e = stencilpipe.demo_engine(); n = e.source(GRID).call("box", r=2).call("dx")
        full = stencilpipe.demo_engine().evaluate(stencilpipe.demo_engine().source(GRID).call("box", r=2).call("dx"))
        wins = [(2, 2, 5, 5), (50, 38, 6, 5)]
        for got, win in zip(e.evaluate_many(n, wins), wins):
            self.assertTrue(close(got, cut(full, win)))


class Economy(unittest.TestCase):
    def setUp(self):
        random.seed(5)
        self.big = [[random.uniform(0, 1) for _ in range(200)] for _ in range(200)]

    def cells(self, mk, win):
        e = stencilpipe.demo_engine(); n = mk(e.source(self.big)); e.reset_counters()
        e.evaluate(n, win)
        return e.cells_computed()

    def test_neighbourhood_window_computes_little(self):
        c = self.cells(lambda s: s.call("box", r=3), (100, 100, 10, 10))
        self.assertLessEqual(c, 200)

    def test_chain_window_computes_footprints_only(self):
        c = self.cells(lambda s: s.call("box", r=2).call("box", r=3), (100, 100, 10, 10))
        self.assertLessEqual(c, (10 + 6) ** 2 + 100 + 60)            # box(2) over 16x16, box(3) over 10x10

    def test_directional_footprint_is_not_square(self):
        c = self.cells(lambda s: s.call("box", r=1).call("dx"), (100, 100, 10, 10))
        self.assertLessEqual(c, 12 * 12 + 100 - 1)                    # a square margin would be 144 + 100

    def test_resample_maps_the_window(self):
        c = self.cells(lambda s: s.call("box", r=1).call("half"), (40, 40, 10, 10))
        self.assertLessEqual(c, 22 * 22 + 100)                        # box over the mapped 20x20 (+ margin)

    def test_scattered_windows_do_not_cost_their_bounding_box(self):
        e = stencilpipe.demo_engine(); n = e.source(self.big).call("box", r=2); e.reset_counters()
        e.evaluate_many(n, [(5, 5, 8, 8), (180, 180, 8, 8)])
        self.assertLessEqual(e.cells_computed(), 2 * 64 * 2)

    def test_cached_whole_result_serves_windows(self):
        e = stencilpipe.demo_engine(); n = e.source(self.big).call("box", r=2)
        e.evaluate(n); e.reset_counters()
        e.evaluate(n, (50, 50, 10, 10))
        self.assertEqual(e.cells_computed(), 0)

    def test_global_operation_reads_whole_input_but_stays_exact(self):
        mk = lambda s: s.call("box", r=1).call("normalize")
        e = stencilpipe.demo_engine(); full = e.evaluate(mk(e.source(self.big)))
        e2 = stencilpipe.demo_engine(); got = e2.evaluate(mk(e2.source(self.big)), (10, 10, 5, 5))
        self.assertTrue(close(got, cut(full, (10, 10, 5, 5))))


if __name__ == "__main__":
    unittest.main()
