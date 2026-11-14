"""Hidden tests for the gridflow build task (chapter 03). Run with PYTHONPATH=work."""
import threading, time, unittest
from gridflow import Engine, EvalError

G = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]


def as_lists(g):
    return [list(r) for r in g]


def engine(**kw):
    e = Engine(**kw)
    e.op("add", lambda ins, a, ctx: [[v + a["k"] for v in r] for r in ins[0]])
    e.op("gain", lambda ins, a, ctx: [[v * a["k"] for v in r] for r in ins[0]], identity=lambda a: a["k"] == 1)
    return e


class Building(unittest.TestCase):
    def test_equal_calls_are_one_node(self):
        e = engine(); s = e.source(G)
        self.assertIs(s.call("add", k=1), s.call("add", k=1))
        self.assertIsNot(s.call("add", k=1), s.call("add", k=2))

    def test_equal_sources_are_one_node(self):
        e = engine()
        self.assertIs(e.source(G), e.source([row[:] for row in G]))
        self.assertIsNot(e.source(G), e.source([[0.0]]))

    def test_building_runs_nothing(self):
        e = engine(); n = e.source(G).call("add", k=1).call("gain", k=2)
        self.assertEqual(e.runs(n), 0)


class Caching(unittest.TestCase):
    def test_second_evaluation_is_cached(self):
        e = engine(); n = e.source(G).call("add", k=1)
        self.assertEqual(as_lists(e.evaluate(n).value)[0], [2.0, 3.0, 4.0])
        e.evaluate(n)
        self.assertEqual(e.runs(n), 1)
        self.assertGreaterEqual(e.stats()["hits"], 1)

    def test_rebuilt_chain_shares_work(self):
        e = engine()
        e.evaluate(e.source(G).call("add", k=1).call("gain", k=3))
        n2 = e.source([row[:] for row in G]).call("add", k=1).call("gain", k=3)
        e.evaluate(n2)
        self.assertEqual(e.runs(n2), 1)

    def test_operation_version_is_part_of_the_key(self):              # chapter 03 v2 note 2
        e = engine(); n = e.source(G).call("add", k=1)
        e.evaluate(n)
        e.op("add", lambda ins, a, ctx: [[v + a["k"] + 100 for v in r] for r in ins[0]], version=2)
        self.assertEqual(as_lists(e.evaluate(e.source(G).call("add", k=1)).value)[0][0], 102.0)

    def test_scale_is_quantised_and_computed_at_the_quantised_value(self):
        e = engine(); seen = []
        e.op("probe", lambda ins, a, ctx: (seen.append(ctx.scale), ins[0])[1])
        n = e.source(G).call("probe")
        e.evaluate(n, scale=0.5); e.evaluate(n, scale=0.500001)
        self.assertEqual(e.runs(n), 1)
        self.assertEqual(seen, [0.5])

    def test_different_scale_is_a_different_key(self):
        e = engine(); n = e.source(G).call("add", k=1)
        e.evaluate(n, scale=1.0); e.evaluate(n, scale=0.5)
        self.assertEqual(e.runs(n), 2)

    def test_warnings_replayed_on_cache_hit(self):                     # note 8
        e = engine()
        e.op("noisy", lambda ins, a, ctx: (ctx.warn("careful"), ins[0])[1])
        n = e.source(G).call("noisy")
        self.assertIn("careful", " ".join(e.evaluate(n).warnings))
        self.assertIn("careful", " ".join(e.evaluate(n).warnings))
        self.assertEqual(e.runs(n), 1)

    def test_identity_shortcut_does_not_run_and_does_not_share_mutable_state(self):   # note 7
        e = engine(); s = e.source(G); n = s.call("gain", k=1)
        v = e.evaluate(n).value
        self.assertEqual(as_lists(v), G)
        self.assertEqual(e.runs(n), 0)
        try:
            v[0][0] = 999.0                                            # if the value is mutable, mutate it
        except TypeError:
            pass
        self.assertEqual(as_lists(e.evaluate(s).value)[0][0], 1.0)

    def test_budget_evicts_and_stays_correct(self):
        e = engine(cache_bytes=200)
        big = [[float(i)] * 20 for i in range(20)]
        nodes = [e.source(big).call("add", k=k) for k in range(5)]
        for n in nodes:
            e.evaluate(n)
        self.assertGreater(e.stats()["evictions"], 0)
        self.assertLessEqual(e.stats()["bytes"], 200 + 8 * 20 * 20 * 2)
        self.assertEqual(as_lists(e.evaluate(nodes[0]).value)[0][0], 0.0)

    def test_concurrent_requests_compute_once(self):                   # note 6
        e = engine()
        e.op("slow", lambda ins, a, ctx: (time.sleep(0.3), ins[0])[1])
        n = e.source(G).call("slow")
        ts = [threading.Thread(target=e.evaluate, args=(n,)) for _ in range(4)]
        [t.start() for t in ts]; [t.join() for t in ts]
        self.assertEqual(e.runs(n), 1)


class Functions(unittest.TestCase):
    def test_build_function_runs_once_at_build_time(self):            # note 5
        e = engine(); calls = []
        s = e.source(G); m = e.source([[1.0, 0.0, 0.0]] * 3)
        def build(p):
            calls.append(1)
            return p.call("gain", k=10)
        n = e.within(s, m, build)
        self.assertEqual(len(calls), 1)
        out = as_lists(e.evaluate(n).value)
        e.evaluate(n)
        self.assertEqual(len(calls), 1)
        self.assertEqual(out[0], [10.0, 2.0, 3.0])

    def test_equal_within_calls_share(self):
        e = engine(); s = e.source(G); m = e.source([[1.0, 0.0, 0.0]] * 3)
        self.assertIs(e.within(s, m, lambda p: p.call("gain", k=10)), e.within(s, m, lambda p: p.call("gain", k=10)))

    def test_placeholder_outside_builder_fails(self):
        e = engine(); s = e.source(G); m = e.source([[1.0, 0.0, 0.0]] * 3); holder = []
        def build(p):
            holder.append(p)
            return p.call("gain", k=10)
        e.within(s, m, build)
        with self.assertRaises(EvalError):
            e.evaluate(holder[0])

    def test_failure_names_the_operation(self):
        e = engine()
        e.op("boom", lambda ins, a, ctx: 1 / 0)
        with self.assertRaises(EvalError) as c:
            e.evaluate(e.source(G).call("boom"))
        self.assertIn("boom", str(c.exception))


class Demo(unittest.TestCase):
    def test_demo_blur_radius_scales(self):
        import gridflow
        e = gridflow.demo_engine()
        g = [[0.0] * 9 for _ in range(9)]; g[4][4] = 81.0
        full = as_lists(e.evaluate(e.source(g).call("blur", radius=2)).value)
        self.assertAlmostEqual(full[4][4], 81.0 / 25)


if __name__ == "__main__":
    unittest.main()
