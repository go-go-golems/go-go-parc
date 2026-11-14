"""Hidden tests for the jailfs build task (chapter 08). Run with PYTHONPATH=work."""
import os, tempfile, unittest
from jailfs import Workspace, Refused


class Setup(unittest.TestCase):
    def setUp(self):
        self.base = tempfile.mkdtemp()
        self.ws_dir = os.path.join(self.base, "ws"); self.data = os.path.join(self.base, "data")
        self.outside = os.path.join(self.base, "outside")
        for d in (self.ws_dir, self.data, self.outside):
            os.makedirs(d)
        open(os.path.join(self.data, "tile.txt"), "wb").write(b"gold")
        open(os.path.join(self.data, "lib.js"), "w").write("helpers")
        open(os.path.join(self.outside, "secret.txt"), "wb").write(b"secret")
        self.ws = Workspace(self.ws_dir, reads=[self.data])

    def refused(self, fn, *a, code=None):
        with self.assertRaises(Refused) as c:
            fn(*a)
        if code:
            self.assertEqual(c.exception.code, code)
        return c.exception


class Reading(Setup):
    def test_relative_read_finds_read_root(self):
        self.assertEqual(self.ws.read("tile.txt"), b"gold")

    def test_absolute_outside_refused(self):
        self.refused(self.ws.read, os.path.join(self.outside, "secret.txt"), code="E_ACCESS")

    def test_dotdot_refused(self):
        self.refused(self.ws.read, "../outside/secret.txt", code="E_ACCESS")

    def test_symlink_inside_root_pointing_out_refused(self):           # note 1: identity, not strings
        os.symlink(os.path.join(self.outside, "secret.txt"), os.path.join(self.ws_dir, "innocent.txt"))
        self.refused(self.ws.read, "innocent.txt", code="E_ACCESS")

    def test_symlinked_directory_inside_root_refused(self):
        os.symlink(self.outside, os.path.join(self.ws_dir, "sub"))
        self.refused(self.ws.read, "sub/secret.txt", code="E_ACCESS")

    def test_missing_file(self):
        self.refused(self.ws.read, "nope.txt", code="E_NOT_FOUND")


class Writing(Setup):
    def test_save_and_read_back_with_parents(self):
        self.ws.save("out/labels.json", b"[]")
        self.assertEqual(self.ws.read("out/labels.json"), b"[]")
        self.assertTrue(os.path.isfile(os.path.join(self.ws_dir, "out", "labels.json")))

    def test_save_into_read_root_refused(self):
        self.refused(self.ws.save, os.path.join(self.data, "tile.txt"), b"x", code="E_ACCESS")
        self.assertEqual(open(os.path.join(self.data, "tile.txt"), "rb").read(), b"gold")

    def test_save_through_symlink_refused_and_target_untouched(self):
        os.symlink(os.path.join(self.data, "tile.txt"), os.path.join(self.ws_dir, "link.txt"))
        self.refused(self.ws.save, "link.txt", b"overwrite", code="E_ACCESS")
        self.assertEqual(open(os.path.join(self.data, "tile.txt"), "rb").read(), b"gold")

    def test_dangling_symlink_does_not_create_outside(self):
        target = os.path.join(self.outside, "created.txt")
        os.symlink(target, os.path.join(self.ws_dir, "dangle.txt"))
        try:
            self.ws.save("dangle.txt", b"x")
        except Refused:
            pass
        self.assertFalse(os.path.exists(target))

    def test_save_never_replaces_a_file_the_session_read(self):        # note 2
        open(os.path.join(self.ws_dir, "input.txt"), "wb").write(b"original")
        self.ws.read("input.txt")
        self.refused(self.ws.save, "input.txt", b"new", code="E_ACCESS")
        self.assertEqual(open(os.path.join(self.ws_dir, "input.txt"), "rb").read(), b"original")

    def test_session_may_replace_its_own_file(self):
        self.ws.save("mine.txt", b"1"); self.ws.read("mine.txt")
        self.ws.save("mine.txt", b"2")
        self.assertEqual(self.ws.read("mine.txt"), b"2")

    def test_duplicate_save_in_one_batch_refused(self):
        with self.ws.batch():
            self.ws.save("a.txt", b"1")
            self.refused(self.ws.save, "a.txt", b"2", code="E_DUPLICATE")

    def test_shadowing_a_read_file_refused(self):                       # chapter 08 v2 note 6
        self.refused(self.ws.save, "tile.txt", b"fake", code="E_SHADOW")

    def test_dotdot_save_refused(self):
        self.refused(self.ws.save, "../outside/x.txt", b"x", code="E_ACCESS")
        self.assertFalse(os.path.exists(os.path.join(self.outside, "x.txt")))


class Loading(Setup):
    def test_load_finds_library_in_read_root(self):
        self.assertEqual(self.ws.load("lib.js"), "helpers")

    def test_load_outside_refused(self):
        open(os.path.join(self.outside, "evil.js"), "w").write("evil")
        self.refused(self.ws.load, os.path.join(self.outside, "evil.js"), code="E_ACCESS")


class Construction(unittest.TestCase):
    def test_two_writable_roots_refused(self):
        a, b = tempfile.mkdtemp(), tempfile.mkdtemp()
        with self.assertRaises(Refused):
            Workspace([a, b])


if __name__ == "__main__":
    unittest.main()
