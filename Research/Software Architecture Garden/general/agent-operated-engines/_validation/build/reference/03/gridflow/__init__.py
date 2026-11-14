"""Reference implementation for the chapter-03 build task (hidden-test yardstick)."""
import hashlib, json, threading
from collections import OrderedDict


class EvalError(Exception):
    pass


class Result:
    def __init__(self, value, warnings):
        self.value, self.warnings = value, list(warnings)


class _Ctx:
    def __init__(self, scale):
        self.scale, self.warnings = scale, []

    def warn(self, m):
        self.warnings.append(str(m))


class Node:
    def __init__(self, eng, kind, name, args, inputs, key, data=None):
        self.eng, self.kind, self.name, self.args, self.inputs, self.key, self.data = eng, kind, name, args, inputs, key, data

    def call(self, name, *inputs, **args):
        return self.eng._intern("op", name, args, (self,) + tuple(inputs))


def _h(*parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()


class Engine:
    def __init__(self, cache_bytes=10_000_000):
        self.cap, self.ops, self.nodes, self.cache, self.bytes = cache_bytes, {}, {}, OrderedDict(), 0
        self._runs, self.hits, self.misses, self.evictions = {}, 0, 0, 0
        self.lock, self.inflight = threading.Lock(), {}

    def op(self, name, fn, version=1, identity=None):
        self.ops[name] = (fn, version, identity)

    def _intern(self, kind, name, args, inputs, data=None):
        key = _h(kind, name, sorted(args.items()), [i.key for i in inputs], data)
        with self.lock:
            n = self.nodes.get(key)
            if n is None:
                n = self.nodes[key] = Node(self, kind, name, dict(args), tuple(inputs), key, data)
        return n

    def source(self, grid):
        data = [[float(v) for v in r] for r in grid]
        return self._intern("source", "source", {}, (), data)

    def within(self, node, mask, build):
        hole = self._intern("placeholder", "placeholder", {"of": node.key}, ())
        inner = build(hole)
        edited = self._subst(inner, hole, node)
        return self._intern("op", "__select", {}, (node, mask, edited))

    def _subst(self, n, hole, by):
        if n is hole:
            return by
        if not n.inputs:
            return n
        return self._intern(n.kind, n.name, n.args, tuple(self._subst(i, hole, by) for i in n.inputs), n.data)

    def runs(self, node):
        return self._runs.get(node.key, 0)

    def stats(self):
        return {"hits": self.hits, "misses": self.misses, "bytes": self.bytes, "evictions": self.evictions}

    def _sig(self, n, scale):
        if n.kind == "source":
            return n.key
        if n.kind == "placeholder":
            raise EvalError("a placeholder can only be used inside the function given to within()")
        version = self.ops[n.name][1] if n.name in self.ops else 0
        return _h(n.key, version, scale, [self._sig(i, scale) for i in n.inputs])

    def evaluate(self, node, scale=1.0):
        q = max(round(scale, 4), 1e-4)
        v, w = self._eval(node, q)
        return Result(v, w)

    def _eval(self, n, q):
        if n.kind == "source":
            return [r[:] for r in n.data], []
        sig = self._sig(n, q)
        with self.lock:
            if sig in self.cache:
                self.cache.move_to_end(sig); self.hits += 1
                v, w, _ = self.cache[sig]
                return [r[:] for r in v], w
            ev = self.inflight.get(sig)
            owner = ev is None
            if owner:
                ev = self.inflight[sig] = threading.Event()
            self.misses += 1
        if not owner:
            ev.wait()
            return self._eval(n, q)
        try:
            ins, warns = [], []
            for i in n.inputs:
                v, w = self._eval(i, q); ins.append(v); warns += w
            if n.name == "__select":
                base, mask, edit = ins
                out = [[e if m >= 0.5 else b for b, m, e in zip(br, mr, er)] for br, mr, er in zip(base, mask, edit)]
            else:
                if n.name not in self.ops:
                    raise EvalError(f"no operation {n.name}")
                fn, _, identity = self.ops[n.name]
                if identity and identity(n.args):
                    return [r[:] for r in ins[0]], warns
                ctx = _Ctx(q)
                try:
                    out = fn(ins, n.args, ctx)
                except EvalError:
                    raise
                except Exception as e:
                    raise EvalError(f"{n.name} failed: {e!r}")
                out = [[float(v) for v in r] for r in out]
                with self.lock:
                    self._runs[n.key] = self._runs.get(n.key, 0) + 1
                warns += ctx.warnings
            size = 8 * sum(len(r) for r in out)
            with self.lock:
                self.cache[sig] = (out, warns, size); self.bytes += size
                while self.bytes > self.cap and len(self.cache) > 1:
                    k, (_, _, sz) = self.cache.popitem(last=False)
                    self.bytes -= sz; self.evictions += 1
            return [r[:] for r in out], warns
        finally:
            with self.lock:
                self.inflight.pop(sig, None)
            ev.set()


def demo_engine():
    e = Engine()
    e.op("add", lambda ins, a, ctx: [[v + a["k"] for v in r] for r in ins[0]])
    e.op("gain", lambda ins, a, ctx: [[v * a["k"] for v in r] for r in ins[0]], identity=lambda a: a["k"] == 1)
    e.op("threshold", lambda ins, a, ctx: [[1.0 if v > a["t"] else 0.0 for v in r] for r in ins[0]])

    def blur(ins, a, ctx):
        g = ins[0]; r = max(0, round(a["radius"] * ctx.scale)); h, w = len(g), len(g[0])
        out = []
        for y in range(h):
            row = []
            for x in range(w):
                vals = [g[yy][xx] for yy in range(max(0, y - r), min(h, y + r + 1)) for xx in range(max(0, x - r), min(w, x + r + 1))]
                row.append(sum(vals) / len(vals))
            out.append(row)
        return out
    e.op("blur", blur)
    return e
