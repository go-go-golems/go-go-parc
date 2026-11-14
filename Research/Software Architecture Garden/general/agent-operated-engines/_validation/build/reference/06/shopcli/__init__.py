"""Reference implementation for the chapter-06 build task (hidden-test yardstick)."""
import difflib, re

CODES = ["E_UNKNOWN_COMMAND", "E_NAMESPACE", "E_UNKNOWN_OPTION", "E_ARG_TYPE", "E_ARG_RANGE", "E_ARG_MISSING",
         "E_NOT_FOUND", "E_HOST", "E_SYNTAX"]
REDIRECTS = {"rm": "item.remove", "delete": "item.remove", "ls": "item.list", "inventory": "report.stock"}


class Fail(Exception):
    def __init__(self, code, message, element, valid=(), hint=None, fix=None, host_name=None):
        super().__init__(message)
        self.code, self.message, self.element = code, message, element
        self.valid, self.hint, self.fix, self.host_name = list(valid), hint, fix, host_name


def A(name, typ, required=True, default=None, lo=None, usual=None):
    return dict(name=name, type=typ, required=required, default=default, lo=lo, usual=usual)


class Shop:
    def __init__(self):
        self.stock, self.prices = {}, {}
        self.cmds = {
            "item.add": ([A("name", "str"), A("qty", "int", lo=0, usual=(0, 1000))], self._add),
            "item.remove": ([A("name", "str"), A("qty", "int", required=False, lo=0)], self._remove),
            "item.list": ([], lambda a: [{"name": k, "qty": v} for k, v in sorted(self.stock.items())]),
            "price.set": ([A("name", "str"), A("value", "num", lo=0)], self._set),
            "price.get": ([A("name", "str")], self._get),
            "report.stock": ([], lambda a: {"items": len(self.stock), "units": sum(self.stock.values())}),
            "report.margin": ([A("name", "str"), A("cost", "num")], self._margin),
        }

    def _need(self, table, name):
        if name not in table:
            raise Fail("E_NOT_FOUND", f"no item {name!r}", name, valid=sorted(table)[:8])
        return table[name]

    def _add(self, a):
        self.stock[a["name"]] = self.stock.get(a["name"], 0) + a["qty"]
        return {"name": a["name"], "qty": self.stock[a["name"]]}

    def _remove(self, a):
        have = self._need(self.stock, a["name"])
        left = 0 if a.get("qty") is None else max(0, have - a["qty"])
        if left: self.stock[a["name"]] = left
        else: del self.stock[a["name"]]
        return {"name": a["name"], "qty": left}

    def _set(self, a):
        self.prices[a["name"]] = a["value"]; return {"name": a["name"], "value": a["value"]}

    def _get(self, a):
        return {"name": a["name"], "value": self._need(self.prices, a["name"])}

    def _margin(self, a):
        v = self._need(self.prices, a["name"])
        return {"name": a["name"], "margin": (v - a["cost"]) / v}

    def _suggest(self, cmd, argtext):
        tail = (" " + argtext) if argtext else ""
        if "." not in cmd:
            for c in self.cmds:
                if c.split(".", 1)[1] == cmd:
                    raise Fail("E_NAMESPACE", f"{cmd} lives in a namespace", cmd, hint=f"use {c}", fix=c + tail)
        if cmd in REDIRECTS:
            raise Fail("E_UNKNOWN_COMMAND", f"no command {cmd}", cmd, hint=f"{cmd} means {REDIRECTS[cmd]}", fix=REDIRECTS[cmd] + tail)
        near = difflib.get_close_matches(cmd, list(self.cmds), 1, 0.75)
        if near:
            raise Fail("E_UNKNOWN_COMMAND", f"no command {cmd}", cmd, hint=f"did you mean {near[0]}?", fix=near[0] + tail)
        ranked = sorted(self.cmds, key=lambda c: -difflib.SequenceMatcher(None, cmd, c).ratio())
        raise Fail("E_UNKNOWN_COMMAND", f"no command {cmd}", cmd, valid=ranked[:8])

    def _bind(self, cmd, kv, warn):
        specs, fn = self.cmds[cmd]
        names = [s["name"] for s in specs]
        for k in kv:
            if k not in names:
                raise Fail("E_UNKNOWN_OPTION", f"{cmd} has no option {k}", k, valid=names)
        args = {}
        for s in specs:
            if s["name"] not in kv:
                if s["required"]:
                    raise Fail("E_ARG_MISSING", f"{cmd} needs {s['name']}", s["name"], valid=names)
                args[s["name"]] = s["default"]; continue
            raw = kv[s["name"]]
            try:
                v = {"str": str, "int": int, "num": float}[s["type"]](raw)
            except ValueError:
                raise Fail("E_ARG_TYPE", f"{s['name']}={raw!r} is not a {s['type']}", s["name"])
            if s["lo"] is not None and v < s["lo"]:
                raise Fail("E_ARG_RANGE", f"{s['name']} must be ≥ {s['lo']}", s["name"], fix=f"{s['name']}={s['lo']}")
            if s["usual"] and not (s["usual"][0] <= v <= s["usual"][1]):
                warn("RANGE", f"{s['name']}={v} is outside the usual range {s['usual']}", "check the quantity")
            args[s["name"]] = v
        return fn, args

    def run(self, script):
        results, warns, error = [], {}, None
        for no, line in enumerate(script.split("\n"), 1):
            if not line.strip():
                continue
            def warn(code, msg, hint):
                k = (code, no, msg)
                w = warns.setdefault(k, {"code": code, "message": msg, "line": no, "count": 0, "hint": hint}); w["count"] += 1
            body, n = line.strip(), 1
            m = re.match(r"repeat\s+(\d+)\s*:\s*(.*)$", body)
            if m:
                n, body = int(m.group(1)), m.group(2)
            parts = body.split()
            cmd = parts[0]
            try:
                if not re.fullmatch(r"[A-Za-z_][\w.]*", cmd):
                    raise Fail("E_SYNTAX", f"not a command: {cmd}", cmd)
                kv = {}
                for t in parts[1:]:
                    if "=" not in t:
                        raise Fail("E_SYNTAX", f"expected key=value, got {t}", t)
                    k, v = t.split("=", 1); kv[k] = v
                if cmd not in self.cmds:
                    self._suggest(cmd, " ".join(parts[1:]))
                for _ in range(n):
                    fn, args = self._bind(cmd, kv, warn)
                    try:
                        results.append(fn(args))
                    except Fail:
                        raise
                    except Exception as e:
                        raise Fail("E_HOST", f"{cmd} failed: {e}", cmd, host_name=type(e).__name__)
            except Fail as f:
                error = {"code": f.code, "message": f.message, "path": ([cmd] if f.element != cmd else []) + ["✗ " + f.element],
                         "where": {"line": no, "source": line}, "valid": f.valid, "hint": f.hint, "fix": f.fix,
                         "host_name": f.host_name}
                break
        return {"ok": error is None, "results": results, "warnings": list(warns.values()), "error": error}
