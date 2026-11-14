"""Reference implementation for the chapter-11 build task (hidden-test yardstick)."""
import hashlib, json, os, time, uuid


def _append(path, obj):
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n")


def _read(path):
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path) if l.strip()]


def _hash(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except OSError:
        return None


class Ledger:
    def __init__(self, directory):
        os.makedirs(directory, exist_ok=True)
        self.labels_f, self.events_f = os.path.join(directory, "labels.jsonl"), os.path.join(directory, "decisions.jsonl")

    def add_label(self, item, label, maker, inputs=()):
        lid = uuid.uuid4().hex[:12]
        _append(self.labels_f, {"id": lid, "item": item, "label": label, "maker": dict(maker),
                                "inputs": [{"path": p, "sha256": _hash(p)} for p in inputs], "at": time.time()})
        return lid

    def decide(self, label_id, decision, actor, reason=None, new_label=None):
        if not actor:
            raise ValueError("a decision needs an actor")
        if decision not in ("accept", "reject", "correct", "undo"):
            raise ValueError(decision)
        if decision == "correct" and new_label is None:
            raise ValueError("correct needs new_label")
        _append(self.events_f, {"label": label_id, "decision": decision, "actor": actor, "reason": reason,
                                "new_label": new_label, "at": time.time()})

    def _labels(self):
        return {r["id"]: r for r in _read(self.labels_f)}

    def _fold(self):
        stacks = {}
        for e in _read(self.events_f):
            st = stacks.setdefault(e["label"], [])
            if e["decision"] == "undo":
                if st: st.pop()
            else:
                st.append(e)
        return stacks

    def state(self):
        labels, stacks, out = self._labels(), self._fold(), {}
        status = {"accept": "accepted", "reject": "rejected", "correct": "corrected"}
        for lid, r in labels.items():
            st = stacks.get(lid) or []
            last = st[-1] if st else None
            out[lid] = {"item": r["item"], "label": last["new_label"] if last and last["decision"] == "correct" else r["label"],
                        "status": status[last["decision"]] if last else "pending"}
        return out

    def source_of(self, label_id):
        r = self._labels()[label_id]
        return {"maker": r["maker"], "inputs": r["inputs"], "at": r["at"], "original_label": r["label"]}

    def made_by(self, **q):
        return [lid for lid, r in self._labels().items() if all(r["maker"].get(k) == v for k, v in q.items())]

    def acceptance(self, by):
        labels, st, tally = self._labels(), self.state(), {}
        for lid, s in st.items():
            if s["status"] == "pending":
                continue
            key = labels[lid]["maker"].get(by)
            ok, n = tally.get(key, (0, 0))
            tally[key] = (ok + (s["status"] in ("accepted", "corrected")), n + 1)
        return {k: ok / n for k, (ok, n) in tally.items()}

    def export(self, path):
        labels, st = self._labels(), self.state()
        keep = [lid for lid, s in st.items() if s["status"] in ("accepted", "corrected")]
        json.dump([{"item": st[l]["item"], "label": st[l]["label"]} for l in keep], open(path, "w"))
        json.dump({"exported_at": time.time(), "labels": {l: {"maker": labels[l]["maker"], "inputs": labels[l]["inputs"],
                   "status": st[l]["status"]} for l in keep}}, open(path + ".provenance.json", "w"))
