"""Hidden tests for the labelbook build task (chapter 11). Run with PYTHONPATH=work."""
import glob, json, os, tempfile, unittest
from labelbook import Ledger

AG = {"kind": "agent", "model": "m1", "prompt": "v2", "run": "r7"}
DET = {"kind": "detector", "name": "E19"}
P = {"kind": "person", "name": "ana"}


def files_snapshot(d):
    out = {}
    for f in glob.glob(os.path.join(d, "**", "*"), recursive=True):
        if os.path.isfile(f):
            out[f] = open(f, "rb").read()
    return out


class Ledgers(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.L = Ledger(self.dir)

    def test_append_only_history(self):                                   # note 4: never edit an event
        a = self.L.add_label("img1", "dust", AG)
        self.L.decide(a, "accept", "ana")
        before = files_snapshot(self.dir)
        self.L.decide(a, "undo", "ana")
        self.L.decide(a, "reject", "ana", reason="grain")
        after = files_snapshot(self.dir)
        for f, content in before.items():
            self.assertTrue(after[f].startswith(content), f"{f} was rewritten, not appended to")

    def test_undo_restores_previous_state(self):
        a = self.L.add_label("img1", "dust", AG)
        self.L.decide(a, "accept", "ana"); self.L.decide(a, "undo", "ana")
        self.assertEqual(self.L.state()[a]["status"], "pending")
        self.L.decide(a, "reject", "ana"); self.L.decide(a, "accept", "bo"); self.L.decide(a, "undo", "bo")
        self.assertEqual(self.L.state()[a]["status"], "rejected")

    def test_state_survives_reopening(self):                              # one fold over the stored log
        a = self.L.add_label("img1", "dust", AG); b = self.L.add_label("img2", "hair", DET)
        self.L.decide(a, "accept", "ana"); self.L.decide(b, "correct", "ana", new_label="scratch")
        s2 = Ledger(self.dir).state()
        self.assertEqual(s2[a]["status"], "accepted")
        self.assertEqual(s2[b]["status"], "corrected"); self.assertEqual(s2[b]["label"], "scratch")

    def test_actor_is_required(self):                                     # note 6: record who decided
        a = self.L.add_label("img1", "dust", AG)
        with self.assertRaises(ValueError):
            self.L.decide(a, "accept", None)

    def test_correction_overlays_and_keeps_the_original(self):            # note 10
        a = self.L.add_label("img1", "dust", AG)
        self.L.decide(a, "correct", "ana", new_label="hair")
        self.assertEqual(self.L.state()[a]["label"], "hair")
        src = self.L.source_of(a)
        self.assertEqual(src.get("maker", src).get("kind") if isinstance(src.get("maker", src), dict) else None, "agent")

    def test_acceptance_counts_rejections(self):                          # note 3
        ids = [self.L.add_label(f"i{k}", "dust", AG) for k in range(4)]
        dids = [self.L.add_label(f"j{k}", "dust", DET) for k in range(2)]
        self.L.decide(ids[0], "accept", "ana"); self.L.decide(ids[1], "reject", "ana")
        self.L.decide(ids[2], "correct", "ana", new_label="hair")          # ids[3] pending: not decided
        self.L.decide(dids[0], "reject", "ana"); self.L.decide(dids[1], "reject", "ana")
        acc = self.L.acceptance(by="kind")
        self.assertAlmostEqual(acc["agent"], 2 / 3)
        self.assertAlmostEqual(acc["detector"], 0.0)

    def test_made_by_finds_a_faulty_source(self):
        a = self.L.add_label("i1", "dust", AG)
        b = self.L.add_label("i2", "dust", dict(AG, prompt="v3"))
        c = self.L.add_label("i3", "dust", P)
        self.assertEqual(self.L.made_by(kind="agent", prompt="v2"), [a])
        self.assertEqual(sorted(self.L.made_by(kind="agent")), sorted([a, b]))

    def test_source_of_records_inputs_and_time(self):
        p = os.path.join(self.dir, "tile.txt"); open(p, "w").write("pixels")
        a = self.L.add_label("i1", "dust", AG, inputs=[p])
        s = json.dumps(self.L.source_of(a))
        self.assertIn("r7", s); self.assertIn("tile.txt", s)

    def test_export_plain_with_provenance_sidecar(self):                  # note 8
        p = os.path.join(self.dir, "src.txt"); open(p, "w").write("data")
        a = self.L.add_label("i1", "dust", AG, inputs=[p]); b = self.L.add_label("i2", "hair", P)
        c = self.L.add_label("i3", "dust", DET)
        self.L.decide(a, "accept", "ana"); self.L.decide(b, "correct", "ana", new_label="scratch"); self.L.decide(c, "reject", "ana")
        out = os.path.join(self.dir, "export.json")
        self.L.export(out)
        rows = json.load(open(out))
        self.assertIsInstance(rows, list)
        self.assertEqual(sorted((r["item"], r["label"]) for r in rows), [("i1", "dust"), ("i2", "scratch")])
        sidecars = [f for f in os.listdir(self.dir) if f.startswith("export.json") and f != "export.json"]
        self.assertTrue(sidecars, "no provenance sidecar next to the export")
        side = open(os.path.join(self.dir, sidecars[0])).read()
        self.assertIn("r7", side)


if __name__ == "__main__":
    unittest.main()
