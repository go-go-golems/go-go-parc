import difflib, json, re

class RecordError(Exception):
    def __init__(self, code, msg=""): super().__init__(f"{code}: {msg}"); self.code = code

class Refusal(Exception):
    def __init__(self, code, message, valid=(), nearest=None, fix=None):
        super().__init__(f"{code}: {message}"); self.code, self.message, self.valid, self.nearest, self.fix = code, message, list(valid), nearest, fix

class Warning_:
    def __init__(self, code, message): self.code, self.message = code, message

class Call:
    def __init__(self, rec, args, warnings): self.record_name, self.on, self.args, self.warnings, self.rec = rec["name"], rec["on"], args, warnings, rec

TYPES = {"number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool), "string": lambda v: isinstance(v, str),
         "bool": lambda v: isinstance(v, bool), "enum": lambda v: isinstance(v, str),
         "rgb": lambda v: isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v) is not None}

class Registry:
    def __init__(self, confirm_required=()):
        self.recs, self.confirm = {}, set(confirm_required)
    def register(self, r):
        for k in ("name", "on", "doc", "args", "fields", "samples", "run"):
            if k not in r: raise RecordError("E_RECORD", f"missing {k}")
        if (r["on"], r["name"]) in self.recs: raise RecordError("E_DUPLICATE", r["name"])
        names = [a["name"] for a in r["args"]]
        if len(set(names)) != len(names): raise RecordError("E_RECORD", "duplicate arg")
        for a in r["args"]:
            if a.get("type") not in TYPES: raise RecordError("E_RECORD", "type")
            lo, hi = a.get("min"), a.get("max")
            if "default" in a:
                d = a["default"]
                if not TYPES[a["type"]](d) or (lo is not None and d < lo) or (hi is not None and d > hi) or (a["type"] == "enum" and d not in a["values"]):
                    raise RecordError("E_DEFAULT", a["name"])
            if "usual" in a:
                ul, uh = a["usual"]
                if (lo is not None and ul < lo) or (hi is not None and uh > hi): raise RecordError("E_USUAL", a["name"])
            for wrong, right in a.get("redirects", {}).items():
                if right not in names: raise RecordError("E_REDIRECT", wrong)
        if not r["samples"]: raise RecordError("E_SAMPLES", r["name"])
        self.recs[(r["on"], r["name"])] = r
        for wrong, right in r.get("redirects", {}).items():
            if (r["on"], right) not in self.recs and right != r["name"]: raise RecordError("E_REDIRECT", wrong)
    def _names(self, on): return sorted(n for (o, n) in self.recs if o == on)
    def bind(self, on, name, raw):
        r = self.recs.get((on, name))
        if r is None:
            fix = None
            for (o, n), x in self.recs.items():
                if o == on and name in x.get("redirects", {}): fix = x["redirects"][name]
            near = difflib.get_close_matches(name, self._names(on), 1)
            raise Refusal("E_UNKNOWN_ACTION", f"no {name} on {on}", self._names(on), near[0] if near else None, fix)
        specs = {a["name"]: a for a in r["args"]}
        for k in raw:
            if k not in specs:
                fix = next((a["redirects"][k] for a in r["args"] if k in a.get("redirects", {})), None)
                raise Refusal("E_UNKNOWN_OPTION", f"no option {k}", list(specs), (difflib.get_close_matches(k, list(specs), 1) or [None])[0], fix)
        args, warns = {}, []
        for a in r["args"]:
            if a["name"] in raw: v = raw[a["name"]]
            elif "default" in a: v = a["default"]
            elif a.get("optional"): continue
            else: raise Refusal("E_ARG_MISSING", a["name"], list(specs))
            if not TYPES[a["type"]](v): raise Refusal("E_ARG_TYPE", f"{a['name']}={v!r}")
            if a["type"] == "enum" and v not in a["values"]: raise Refusal("E_ARG_RANGE", a["name"], a["values"])
            if a["type"] == "number":
                if (a.get("min") is not None and v < a["min"]) or (a.get("max") is not None and v > a["max"]): raise Refusal("E_ARG_RANGE", a["name"])
                if "usual" in a and not (a["usual"][0] <= v <= a["usual"][1]): warns.append(Warning_("RANGE", a.get("usual_hint", "")))
            args[a["name"]] = v
        return Call(r, args, warns)
    def run(self, call, confirmed=False):
        r = call.rec
        if (r["name"] in self.confirm or r.get("flags", {}).get("confirm")) and not confirmed: raise Refusal("E_CONFIRM", r["name"])
        return r["run"](call.args)
    def tool_schemas(self):
        return [{"name": f"{o}.{n}", "description": r["doc"], "input_schema": {a["name"]: {k: a.get(k) for k in ("type", "unit", "min", "max", "default", "values")} for a in r["args"]}} for (o, n), r in self.recs.items()]
    def controls(self, on, name): return [{k: a.get(k) for k in ("name", "type", "unit", "min", "max", "default", "values")} for a in self.recs[(on, name)]["args"]]
    def help(self, on, name): return json.dumps(self.controls(on, name))
    def voice_phrases(self):
        return {f"{o}.{n}": [f"{n.replace('_', ' ')} on the {o}"] for (o, n) in self.recs}
    def walk(self):
        out = []
        for (o, n), r in self.recs.items():
            for s in r["samples"]:
                try:
                    v = r["run"](self.bind(o, n, s).args)
                    if set(v) != set(r["fields"]): out.append({"action": f"{o}.{n}", "problem": "fields"})
                except Exception as e: out.append({"action": f"{o}.{n}", "problem": repr(e)})
        return out

def demo_registry():
    reg = Registry(confirm_required={"lock_door"})
    reg.register({"name": "set_temperature", "on": "thermostat", "doc": "set", "fields": ["target", "mode"], "samples": [{"temperature": 20}],
                  "args": [{"name": "temperature", "type": "number", "unit": "°C", "doc": "t", "min": 5, "max": 35, "usual": [16, 24], "redirects": {"target": "temperature"}}],
                  "run": lambda a: {"target": a["temperature"], "mode": "heat"}})
    reg.register({"name": "set_color", "on": "light", "doc": "colour", "fields": ["color"], "samples": [{"color": "#ff8800"}],
                  "args": [{"name": "color", "type": "rgb", "unit": None, "doc": "c"}], "run": lambda a: {"color": a["color"]}})
    reg.register({"name": "dim", "on": "light", "doc": "dim", "fields": ["level"], "samples": [{}],
                  "args": [{"name": "level", "type": "number", "unit": "%", "doc": "l", "min": 0, "max": 100, "default": 50}], "run": lambda a: {"level": a["level"]}})
    reg.register({"name": "lock_door", "on": "door", "doc": "lock", "fields": ["locked"], "samples": [{}], "args": [], "run": lambda a: {"locked": True}})
    reg.register({"name": "run_scene", "on": "scene", "doc": "scene", "fields": ["scene"], "samples": [{"scene": "away"}],
                  "args": [{"name": "scene", "type": "enum", "unit": None, "doc": "s", "values": ["morning", "evening", "away"]}], "run": lambda a: {"scene": a["scene"]}})
    return reg
