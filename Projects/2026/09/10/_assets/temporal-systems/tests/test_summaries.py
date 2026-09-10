import math
import random
import unittest
from summaries import Summary, coverage, demo, hierarchy, leaf, merge, reduce_balanced, summarize, weighted_mean

class SummaryTests(unittest.TestCase):
    def test_empty_zero_and_ties(self):
        empty = leaf(0, 0, None)
        zero = leaf(0, 0, 0)
        self.assertEqual(empty.n, 0)
        self.assertIsNone(empty.minimum)
        self.assertIsNone(empty.variance())
        self.assertEqual(zero.minimum, 0)
        self.assertEqual(zero.variance(), 0)
        self.assertIsNone(zero.variance(sample=True))
        self.assertEqual(merge(empty, zero), zero)
        self.assertEqual(merge(zero, empty), zero)
        a, b = leaf(3, 1, 7), leaf(3, 2, -1)
        self.assertEqual(merge(a, b), merge(b, a))
        self.assertEqual(merge(a, b).last.identity, 2)
        with self.assertRaises(ValueError):
            leaf(0, 0, float('nan'))

    def test_partition_tree_properties(self):
        rng = random.Random(71)
        for _ in range(300):
            observations = [(i*7, i, None if rng.random()<.2 else rng.uniform(-100,100))
                            for i in range(rng.randrange(1,100))]
            values = [x for _, _, x in observations if x is not None]
            direct = summarize(observations)
            if not values:
                continue
            mean = math.fsum(values)/len(values)
            m2 = math.fsum((x-mean)**2 for x in values)
            chunks, cursor = [], 0
            while cursor < len(observations):
                size = rng.randrange(1, 8)
                chunks.append(summarize(observations[cursor:cursor+size]))
                cursor += size
            rng.shuffle(chunks)
            sequential = Summary()
            for chunk in chunks:
                sequential = merge(sequential, chunk)
            for actual in (direct, reduce_balanced(chunks), sequential):
                self.assertEqual(actual.n, len(values))
                self.assertEqual(actual.minimum, min(values))
                self.assertEqual(actual.maximum, max(values))
                self.assertEqual(actual.first, direct.first)
                self.assertEqual(actual.last, direct.last)
                self.assertAlmostEqual(actual.total, math.fsum(values), delta=1e-9)
                self.assertAlmostEqual(actual.mean, mean, delta=1e-11)
                self.assertAlmostEqual(actual.m2, m2, delta=1e-8)

    def test_large_offset_quantiles_and_weights(self):
        output = demo()
        self.assertEqual(output['stable']['m2'], .65625)
        self.assertEqual(float(output['reference_m2']), .65625)
        self.assertNotEqual(output['naive_m2'], .65625)
        for result in output['large_offset_tree_m2'].values():
            self.assertAlmostEqual(result, .65625, delta=1e-3)
        mixed = [-1e6, 1e-6, 1e6, 0., -1e-6]
        reference_mean = math.fsum(mixed)/len(mixed)
        reference_m2 = math.fsum((x-reference_mean)**2 for x in mixed)
        for values in (mixed, list(reversed(mixed))):
            result = summarize((i, i, x) for i, x in enumerate(values))
            self.assertTrue(math.isclose(result.m2, reference_m2, rel_tol=1e-12))
        a, b = output['quantile_counterexample']
        self.assertEqual((a['sum'], a['sum_squares']), (b['sum'], b['sum_squares']))
        sa, sb = [summarize((i, i, x) for i, x in enumerate(z['values'])) for z in (a, b)]
        self.assertAlmostEqual(sa.m2, sb.m2)
        self.assertEqual((sa.n, sa.minimum, sa.maximum, sa.first, sa.last),
                         (sb.n, sb.minimum, sb.maximum, sb.first, sb.last))
        self.assertNotEqual(a['median'], b['median'])
        self.assertEqual(weighted_mean([(10,9),(100,1)]), 19)
        self.assertEqual(weighted_mean([(0,9),(10,1)]), 1)
        self.assertIsNone(weighted_mean([(1,0)]))

    def test_alignment_and_coverage(self):
        buckets = {i: leaf(i, i, float(i)) for i in (3,4,5)}
        levels = hierarchy(buckets, 2)
        self.assertEqual(set(levels[1]), {1,2})
        self.assertEqual(levels[1][1].total, 3)
        self.assertEqual(levels[1][2].total, 9)
        self.assertEqual(hierarchy({-1:leaf(-1,0,0)},1)[1][-1].n, 1)
        self.assertEqual(coverage(0,10,[(0,4,'available'),(4,6,'missing')]),
                         {'available':4,'missing':2,'unknown':4})
        with self.assertRaises(ValueError):
            coverage(0,10,[(0,6,'available'),(5,8,'missing')])
        with self.assertRaises(ValueError):
            hierarchy({}, 17)

if __name__ == '__main__':
    unittest.main()
