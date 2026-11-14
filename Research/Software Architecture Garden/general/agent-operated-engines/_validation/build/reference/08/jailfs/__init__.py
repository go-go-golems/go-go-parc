"""Reference implementation for the chapter-08 build task (hidden-test yardstick)."""
import contextlib, os, secrets


class Refused(Exception):
    def __init__(self, code, message, fix=None):
        super().__init__(f"{code}: {message}"); self.code, self.fix = code, fix


def _inside(path, root):
    return os.path.commonpath([path, root]) == root


class Workspace:
    def __init__(self, root, reads=()):
        if isinstance(root, (list, tuple)):
            raise Refused("E_ACCESS", "one writable root only", fix="pass extra directories as reads=[...]")
        self.root = os.path.realpath(root)
        self.reads = [os.path.realpath(r) for r in reads]
        self.opened, self.written, self._batch = set(), set(), None

    def _rel(self, path):
        rel = os.path.normpath(path)
        if rel == ".." or rel.startswith(".." + os.sep):
            raise Refused("E_ACCESS", f"{path!r} leaves the workspace", fix=os.path.basename(path))
        return rel

    def _locate_read(self, path):
        roots = [self.root] + self.reads
        if os.path.isabs(path):
            real = os.path.realpath(path)
            for r in roots:
                if _inside(os.path.normpath(path), r) or _inside(real, r):
                    if not _inside(real, r):
                        raise Refused("E_ACCESS", "a link leaves the roots")
                    return real
            raise Refused("E_ACCESS", f"{path!r} is outside the roots", fix="add --read DIR")
        rel = self._rel(path)
        for r in roots:
            cand = os.path.join(r, rel)
            if os.path.lexists(cand):
                real = os.path.realpath(cand)
                if not _inside(real, r):
                    raise Refused("E_ACCESS", f"{path!r} goes through a link out of {r}")
                return real
        raise Refused("E_NOT_FOUND", f"no file {path!r}")

    def read(self, path):
        real = self._locate_read(path)
        if not os.path.isfile(real):
            raise Refused("E_NOT_FOUND", f"no file {path!r}")
        st = os.stat(real); self.opened.add((st.st_dev, st.st_ino))
        with open(real, "rb") as f:
            return f.read()

    def load(self, name):
        return self.read(name).decode()

    @contextlib.contextmanager
    def batch(self):
        self._batch = set()
        try:
            yield self
        finally:
            self._batch = None

    def save(self, path, data):
        if os.path.isabs(path):
            if not _inside(os.path.normpath(path), self.root):
                raise Refused("E_ACCESS", "saves go only to the writable root", fix=f"save({os.path.basename(path)!r}, ...)")
            rel = os.path.relpath(os.path.normpath(path), self.root)
        else:
            rel = self._rel(path)
        if any(os.path.lexists(os.path.join(r, rel)) for r in self.reads):
            raise Refused("E_SHADOW", f"{rel} exists in a read directory; a save would shadow it", fix="save under another name")
        if self._batch is not None:
            if rel in self._batch:
                raise Refused("E_DUPLICATE", f"{rel} saved twice in one run")
            self._batch.add(rel)
        target = os.path.join(self.root, rel)
        parent = os.path.dirname(target)
        os.makedirs(parent, exist_ok=True)
        if not _inside(os.path.realpath(parent), self.root):
            raise Refused("E_ACCESS", "the parent directory is a link out of the root")
        if os.path.islink(target):
            raise Refused("E_ACCESS", f"{rel} is a link; saves do not follow links", fix="save under another name")
        if os.path.exists(target):
            st = os.lstat(target); ident = (st.st_dev, st.st_ino)
            if ident in self.opened and ident not in self.written:
                raise Refused("E_ACCESS", f"{rel} was read by this session; it is not replaced")
        tmp = os.path.join(parent, ".tmp-" + secrets.token_hex(8))
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, target)
        st = os.lstat(target); self.written.add((st.st_dev, st.st_ino))

    def names(self):
        out = []
        for d, _, fs in os.walk(self.root):
            out += [os.path.relpath(os.path.join(d, f), self.root) for f in fs]
        return sorted(out)
