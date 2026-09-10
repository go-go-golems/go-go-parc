import random
import unittest
from fractions import Fraction
from timeline import Domain, Engine, SECOND, geometry, level, tile_indices, time_to_x, x_to_time, visible_rows, zoom

class TimelineTests(unittest.TestCase):
    def test_round_trip_and_anchor(self):
        rng = random.Random(91)
        for _ in range(1000):
            start = rng.randrange(-10**18, 10**18)
            span = rng.randrange(4 * SECOND, 7 * 86400 * SECOND)
            d = Domain(start, start + span)
            width = rng.randrange(1, 2000)
            u = rng.randrange(d.start, d.end)
            self.assertEqual(x_to_time(time_to_x(u, d, width), d, width), u)
            x = Fraction(rng.randrange(width * 100), 100)
            next_domain = zoom(d, x, width, Fraction(3, 2))
            self.assertLessEqual(abs(x_to_time(x, next_domain, width) - x_to_time(x, d, width)), 1)

    def test_grid_and_lod(self):
        self.assertEqual(list(tile_indices(Domain(-64*SECOND, 0), 0)), [-1])
        day = Domain(0, 86400*SECOND)
        self.assertEqual(level(day, 1400, 'numeric'), 8)
        self.assertEqual(level(day, 1400, 'image'), 11)
        self.assertEqual(list(tile_indices(Domain(0, 64*SECOND), 0)), [0])

    def test_cancel_does_not_restore_request_identity(self):
        initial = Domain(0, 3600*SECOND)
        engine = Engine(initial)
        old = engine.generation
        engine.begin_pan(100, 1000)
        engine.move(150)
        self.assertFalse(engine.eligible(old))
        moved = engine.generation
        engine.cancel()
        self.assertEqual(engine.domain, initial)
        self.assertGreater(engine.generation, moved)
        self.assertFalse(engine.eligible(old))

    def test_bounded_geometry(self):
        day = Domain(0, 86400*SECOND)
        rows = visible_rows(16, 232, 0, 720)
        self.assertEqual(list(rows), list(range(6)))
        result = geometry(day, 1400, rows, 8)
        self.assertLessEqual(len(result), 50000)
        self.assertTrue(all(0 <= left < right <= 1400 for _, left, right, _ in result))
        with self.assertRaises(ValueError):
            geometry(day, 1400, range(128), 8)
        with self.assertRaises(ValueError):
            tile_indices(day, 0)

if __name__ == '__main__':
    unittest.main()
