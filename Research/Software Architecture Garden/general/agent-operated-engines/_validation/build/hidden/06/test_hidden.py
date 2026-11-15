"""Hidden tests for the shopcli build task (chapter 06). Run with PYTHONPATH=work."""
import unittest
import shopcli
from shopcli import Shop


def err(script, shop=None):
    r = (shop or Shop()).run(script)
    assert not r["ok"] and r["error"], r
    return r["error"], r


class Shape(unittest.TestCase):
    def test_codes_are_closed(self):
        for script in ["item.ad name=a qty=1", "add name=a qty=1", "item.add name=a qty=1 colour=red",
                       "item.add name=a qty=lots", "price.get name=nope", "%%%", "zzzzzz"]:
            e, _ = err(script)
            self.assertIn(e["code"], shopcli.CODES, script)

    def test_where_and_path(self):
        e, _ = err("item.add name=a qty=1\n\nitem.ad name=b qty=2")
        self.assertEqual(e["where"]["line"], 3)
        self.assertIn("item.ad", e["where"]["source"])
        self.assertTrue(e["path"][-1].startswith("✗"))

    def test_results_before_failure_are_kept(self):
        e, r = err("item.add name=a qty=1\nitem.add name=b qty=2\nprice.get name=zz")
        self.assertEqual(len(r["results"]), 2)


class Suggestions(unittest.TestCase):
    def test_near_spelling_gives_fix_with_command(self):
        e, _ = err("item.ad name=a qty=1")
        self.assertEqual(e["code"], "E_UNKNOWN_COMMAND")
        self.assertIn("item.add", e["fix"] or "")

    def test_namespace_member_comes_first(self):
        e, _ = err("add name=a qty=1")
        self.assertEqual(e["code"], "E_NAMESPACE")
        self.assertIn("item.add", e["fix"] or "")

    def test_mined_redirect_beats_spelling_and_keeps_the_agents_arguments(self):
        shop = Shop(); shop.run("item.add name=apple qty=3")
        e, _ = err("rm name=apple", shop)
        self.assertIn("item.remove", e["fix"] or "")
        self.assertIn("name=apple", e["fix"] or "")

    def test_redirect_fix_runs(self):                                   # chapter note 11: fixes are tested
        shop = Shop(); shop.run("item.add name=apple qty=3")
        e, _ = err("delete name=apple", shop)
        self.assertTrue(shop.run(e["fix"])["ok"], e["fix"])

    def test_inventory_redirect(self):
        e, _ = err("inventory")
        self.assertIn("report.stock", e["fix"] or "")

    def test_valid_list_is_bounded_when_nothing_matches(self):
        e, _ = err("zzzzzz")
        self.assertTrue(0 < len(e["valid"]) <= 8)

    def test_unknown_option_lists_valid_options(self):
        e, _ = err("item.add name=a qty=1 colour=red")
        self.assertEqual(e["code"], "E_UNKNOWN_OPTION")
        self.assertIn("qty", e["valid"]); self.assertIn("name", e["valid"])


class Values(unittest.TestCase):
    def test_wrong_type_is_refused(self):
        e, _ = err("item.add name=a qty=lots")
        self.assertEqual(e["code"], "E_ARG_TYPE")

    def test_out_of_range_is_refused(self):
        e, _ = err("item.add name=a qty=-3")
        self.assertEqual(e["code"], "E_ARG_RANGE")

    def test_missing_argument(self):
        e, _ = err("item.add name=a")
        self.assertEqual(e["code"], "E_ARG_MISSING")


class HostAndWarnings(unittest.TestCase):
    def test_host_failure_has_closed_code_and_host_name(self):
        # A margin on a zero price divides by zero. Either the host exception is caught and reported with a closed
        # code and its name, or (better, and what all three first builders did) the case is anticipated and refused
        # as a repairable argument error. The first version demanded E_HOST and penalised the better design.
        shop = Shop(); shop.run("item.add name=a qty=1\nprice.set name=a value=0")
        e, _ = err("report.margin name=a cost=1", shop)
        self.assertEqual(e["where"]["line"], 1)
        if e["code"] == "E_HOST":
            self.assertEqual(e["host_name"], "ZeroDivisionError")
        else:
            self.assertIn(e["code"], shopcli.CODES)        # the task allows codes of one's own (E_STATE seen)
            self.assertTrue(e["fix"] or e["hint"], "an anticipated failure must say how to repair it")

    def test_warnings_in_a_repeat_fold_with_count(self):
        r = Shop().run("repeat 5: item.add name=a qty=5000")
        self.assertTrue(r["ok"])
        ws = [w for w in r["warnings"] if w["code"] == "RANGE"]
        self.assertEqual(len(ws), 1)
        self.assertEqual(ws[0]["count"], 5)
        self.assertEqual(ws[0]["line"], 1)

    def test_clean_script_has_no_warnings(self):
        r = Shop().run("item.add name=a qty=5\nitem.list")
        self.assertTrue(r["ok"]); self.assertEqual(r["warnings"], []); self.assertIsNone(r["error"])


if __name__ == "__main__":
    unittest.main()
