import unittest
from fractions import Fraction
from clocks import Barrier, ClockMap, DriftController, Epoch, MasterClock, moving_target, simulate_four, ticks_to_utc

class ClockTests(unittest.TestCase):
    def test_master_continuity(self):
        c = MasterClock(10_000_000)
        c.configure(1000, rate=2)
        self.assertEqual(c.now(1000), 11_000_000)
        self.assertEqual(c.now(1500), 12_000_000)
        c.configure(1500, running=False)
        self.assertEqual(c.now(4000), 12_000_000)
        c.configure(4000, running=True, rate=Fraction(1, 2))
        self.assertEqual(c.now(5000), 12_500_000)
        c.configure(5000, seek=0)
        self.assertEqual(c.now(5000), 0)
        with self.assertRaises(ValueError):
            c.now(4999)

    def test_mapping_gap_reset_and_ticks(self):
        mapping = ClockMap([Epoch('a', 0, 4_000_000), Epoch('b', 10_000_000, 14_000_000)])
        self.assertIsNone(mapping.to_media(4_000_000))
        self.assertIsNone(mapping.to_media(9_999_999))
        self.assertEqual(mapping.to_media(10_000_000), ('b', 0.0))
        self.assertEqual(mapping.to_utc('b', 1), 11_000_000)
        self.assertEqual(mapping.to_utc('a', 1), 1_000_000)
        self.assertIsNone(mapping.to_utc('a', 4))
        self.assertEqual(mapping.to_utc('a', 4-1e-10), 3_999_999)
        for tick in range(-1000, 1001):
            exact = Fraction(tick*1_000_000, 90_000)
            self.assertLessEqual(abs(ticks_to_utc(0, tick, 0, 90_000)-exact), Fraction(1,2))
        with self.assertRaises(ValueError):
            ClockMap([Epoch('a', 0, 5), Epoch('b', 4, 8)])

    def test_barrier_generation_and_deadline(self):
        b = Barrier(7, ['a', 'b'], 0)
        b.arrive(6, 'a')
        b.arrive(7, 'b')
        self.assertIsNone(b.poll(1999))
        self.assertEqual(b.poll(2000), {'reason':'deadline', 'ready':['b'], 'missing':['a']})
        b.arrive(7, 'a')
        self.assertIsNone(b.poll(3000))
        ready = Barrier(8, ['a'], 0)
        ready.arrive(8, 'a')
        self.assertEqual(ready.poll(10)['reason'], 'ready')

    def test_controller_boundaries(self):
        c = DriftController()
        self.assertEqual(c.decide(0, 50), ('normal', 1))
        self.assertEqual(c.decide(0, 51), ('rate', .95))
        self.assertEqual(c.decide(0, -200), ('rate', 1.05))
        self.assertEqual(c.decide(0, 201)[0], 'wait')
        self.assertEqual(c.decide(499, 201)[0], 'wait')
        self.assertEqual(c.decide(500, 201)[0], 'seek')
        self.assertEqual(c.decide(501, None)[0], 'unknown')
        self.assertEqual(c.decide(502, 100, 2), ('normal', 2))

    def test_recovery_and_four_processors(self):
        self.assertFalse(any(x['visible'] for x in moving_target(False)))
        self.assertEqual(moving_target(True)[0]['drift_ms'], -120)
        result = simulate_four()
        self.assertTrue(all(x['visible'] for x in result['summary']))
        self.assertEqual(result['summary'][3]['unknown_ticks'], 100)
        self.assertTrue(any(x.get('player') == 3 and x.get('epoch') == 'reset' for x in result['trace']))
        self.assertTrue(any(x.get('player') == 4 and x.get('status') == 'gap' for x in result['trace']))
        self.assertEqual(sum('barrier' in x for x in result['trace']), 1)
        self.assertTrue(all(.95 <= x['rate'] <= 1.05 for x in result['trace'] if 'rate' in x))
        self.assertLess(len(result['trace']), 200)

if __name__ == '__main__':
    unittest.main()
