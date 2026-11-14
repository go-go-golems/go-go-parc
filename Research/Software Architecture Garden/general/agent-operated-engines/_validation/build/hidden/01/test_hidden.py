"""Hidden acceptance tests for the hubreg build task (chapter 01). Never shown to the agents.
Run from the agent's work directory: python3 -m unittest <this file>  (PYTHONPATH=work)."""
import json, unittest
import hubreg
from hubreg import Registry, RecordError, Refusal


def rec(name="set", on="dev", args=None, fields=("v",), samples=({},), run=None, **kw):
    r = {"name": name, "on": on, "doc": "d", "args": list(args or []), "fields": list(fields),
         "samples": list(samples), "run": run or (lambda a: {f: 1 for f in fields})}
    r.update(kw)
    return r


NUM = {"name": "x", "type": "number", "unit": "C", "doc": "x", "min": 0, "max": 100, "default": 10}


class Registration(unittest.TestCase):
    def test_valid_record_registers(self):
        Registry().register(rec(args=[dict(NUM)], samples=[{"x": 5}]))

    def test_default_outside_limits_refused(self):            # note 1: consistency, not only structure
        with self.assertRaises(RecordError):
            Registry().register(rec(args=[dict(NUM, default=500)], samples=[{"x": 5}]))

    def test_usual_outside_hard_limits_refused(self):
        with self.assertRaises(RecordError):
            Registry().register(rec(args=[dict(NUM, usual=[-10, 50])], samples=[{"x": 5}]))

    def test_redirect_to_missing_option_refused(self):
        with self.assertRaises(RecordError):
            Registry().register(rec(args=[dict(NUM, redirects={"temp": "nope"})], samples=[{"x": 5}]))

    def test_duplicate_kind_and_name_refused(self):
        reg = Registry(); reg.register(rec()); 
        with self.assertRaises(RecordError):
            reg.register(rec())

    def test_same_name_on_two_kinds_is_two_records(self):      # note 7
        reg = Registry()
        reg.register(rec(on="a", args=[dict(NUM)], samples=[{"x": 1}]))
        reg.register(rec(on="b", args=[dict(NUM, name="y")], samples=[{"y": 1}]))
        self.assertIn("x", reg.bind("a", "set", {}).args)
        self.assertIn("y", reg.bind("b", "set", {}).args)

    def test_missing_samples_refused_or_reported(self):
        reg = Registry()
        try:
            reg.register(rec(samples=[]))
        except RecordError:
            return
        self.assertTrue(any(p.get("action") for p in reg.walk()), "a record without samples must fail registration or the walk")


class Binding(unittest.TestCase):
    def setUp(self):
        self.reg = Registry()
        self.reg.register(rec(args=[dict(NUM, usual=[16, 24], usual_hint="comfort range",
                                         redirects={"temp": "x"}),
                                    {"name": "mode", "type": "enum", "unit": None, "doc": "m",
                                     "values": ["heat", "cool"], "default": "heat"}],
                              samples=[{"x": 20}], redirects={"sett": "set"}))

    def test_defaults_filled(self):
        self.assertEqual(self.reg.bind("dev", "set", {}).args, {"x": 10, "mode": "heat"})

    def test_wrong_type_refused_not_coerced(self):             # note 3: nothing falls back silently
        with self.assertRaises(Refusal) as c:
            self.reg.bind("dev", "set", {"x": "hot"})
        self.assertEqual(c.exception.code, "E_ARG_TYPE")

    def test_out_of_hard_range_refused(self):
        with self.assertRaises(Refusal) as c:
            self.reg.bind("dev", "set", {"x": 150})
        self.assertEqual(c.exception.code, "E_ARG_RANGE")

    def test_out_of_usual_range_warns_and_binds(self):         # note 2
        call = self.reg.bind("dev", "set", {"x": 30})
        self.assertEqual(call.args["x"], 30)
        self.assertTrue(any("RANGE" in w.code for w in call.warnings))

    def test_inside_usual_range_no_warning(self):
        self.assertEqual(self.reg.bind("dev", "set", {"x": 20}).warnings, [])

    def test_unknown_option_redirect_names_fix(self):          # note 4
        with self.assertRaises(Refusal) as c:
            self.reg.bind("dev", "set", {"temp": 20})
        self.assertEqual(c.exception.code, "E_UNKNOWN_OPTION")
        self.assertIn("x", str(c.exception.fix or ""))

    def test_unknown_option_lists_valid(self):
        with self.assertRaises(Refusal) as c:
            self.reg.bind("dev", "set", {"bogus": 1})
        self.assertEqual(c.exception.code, "E_UNKNOWN_OPTION")
        self.assertIn("x", c.exception.valid)

    def test_unknown_action_redirect_and_nearest(self):
        with self.assertRaises(Refusal) as c:
            self.reg.bind("dev", "sett", {})
        self.assertEqual(c.exception.code, "E_UNKNOWN_ACTION")
        self.assertIn("set", (c.exception.fix or "") + str(c.exception.nearest or ""))

    def test_bad_enum_value_refused(self):
        with self.assertRaises(Refusal) as c:
            self.reg.bind("dev", "set", {"mode": "dry"})
        self.assertIn(c.exception.code, ("E_ARG_TYPE", "E_ARG_RANGE"))

    def test_missing_required_refused(self):
        reg = Registry()
        reg.register(rec(args=[{"name": "n", "type": "number", "unit": None, "doc": "n"}], samples=[{"n": 1}]))
        with self.assertRaises(Refusal) as c:
            reg.bind("dev", "set", {})
        self.assertEqual(c.exception.code, "E_ARG_MISSING")


class Policy(unittest.TestCase):
    def test_plugin_cannot_lower_host_confirm(self):           # flags: host decides
        reg = Registry(confirm_required={"lock"})
        reg.register(rec(name="lock", on="door", fields=("locked",), flags={"confirm": False}))
        call = reg.bind("door", "lock", {})
        with self.assertRaises(Refusal) as c:
            reg.run(call)
        self.assertEqual(c.exception.code, "E_CONFIRM")
        self.assertEqual(reg.run(call, confirmed=True), {"locked": 1})


class Walker(unittest.TestCase):
    def test_extra_result_key_reported(self):                  # note 5, both directions
        reg = Registry()
        reg.register(rec(fields=("v",), run=lambda a: {"v": 1, "extra": 2}))
        self.assertTrue(reg.walk())

    def test_missing_result_key_reported(self):
        reg = Registry()
        reg.register(rec(fields=("v", "w"), run=lambda a: {"v": 1}))
        self.assertTrue(reg.walk())

    def test_exception_reported(self):
        reg = Registry()
        reg.register(rec(run=lambda a: 1 / 0))
        self.assertTrue(reg.walk())

    def test_clean_registry_walks_clean(self):
        self.assertEqual(hubreg.demo_registry().walk(), [])


class Consumers(unittest.TestCase):
    def test_tool_schemas_json_with_units_and_ranges(self):
        s = json.dumps(hubreg.demo_registry().tool_schemas())
        self.assertIn("set_temperature", s)
        self.assertIn("35", s)
        self.assertTrue("°C" in s or '"C"' in s or "celsius" in s.lower() or "\\u00b0C" in s)

    def test_controls_one_per_argument(self):
        c = hubreg.demo_registry().controls("thermostat", "set_temperature")
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0].get("max"), 35)

    def test_demo_lock_needs_confirmation(self):
        reg = hubreg.demo_registry()
        with self.assertRaises(Refusal) as c:
            reg.run(reg.bind("door", "lock_door", {}))
        self.assertEqual(c.exception.code, "E_CONFIRM")


if __name__ == "__main__":
    unittest.main()
