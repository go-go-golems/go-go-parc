"""Hidden tests for the chapter-01 coaching stage (extension). Run with PYTHONPATH=work."""
import json, unittest
import hubreg
from hubreg import Refusal


class Extend(unittest.TestCase):
    def setUp(self):
        self.reg = hubreg.demo_registry()

    def test_set_color_binds_hex(self):
        self.assertEqual(self.reg.bind("light", "set_color", {"color": "#FF8800"}).args["color"].lower(), "#ff8800")

    def test_set_color_refuses_names_and_short_hex(self):
        for bad in ("red", "#ff00", "ff0000"):
            with self.assertRaises(Refusal) as c:
                self.reg.bind("light", "set_color", {"color": bad})
            self.assertEqual(c.exception.code, "E_ARG_TYPE", bad)

    def test_rgb_described_for_consumers(self):
        self.assertIn("rgb", json.dumps(self.reg.tool_schemas()))
        c = self.reg.controls("light", "set_color")
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0].get("type"), "rgb")

    def test_voice_phrases_cover_every_action(self):
        v = self.reg.voice_phrases()
        for name in ("thermostat.set_temperature", "light.dim", "door.lock_door", "scene.run_scene", "light.set_color"):
            self.assertIn(name, v)
            self.assertTrue(v[name] and all(isinstance(p, str) and p for p in v[name]), name)

    def test_renamed_argument_binds(self):
        self.assertEqual(self.reg.bind("thermostat", "set_temperature", {"temperature": 21}).args["temperature"], 21)

    def test_old_argument_name_refused_with_fix(self):
        with self.assertRaises(Refusal) as c:
            self.reg.bind("thermostat", "set_temperature", {"target": 21})
        self.assertEqual(c.exception.code, "E_UNKNOWN_OPTION")
        self.assertIn("temperature", str(c.exception.fix or ""))

    def test_walk_still_clean(self):
        self.assertEqual(self.reg.walk(), [])


if __name__ == "__main__":
    unittest.main()
