import React, { useState, useRef, useEffect, useCallback, useContext } from "react";

/* ============================================================
   PBUI · GRAMMAR OF GRAPHICS — TUTORIAL LANDING PAGE

   A scrolling page with FIVE independently sandboxed instances
   of the real workbench embedded in it: one hero, and one per
   lesson track (A objects · B layout · C grammar · D modules).

   Nothing here is a mockup. Each widget owns its own World,
   its own workspaces, its own accept plumbing. Lesson steps
   complete by OBSERVING world state, so any route to the goal
   counts — including ones this file never anticipated.
   ============================================================ */

/* ---------------- palette (from the workbench) ---------------- */
const C = {
  paper: "#ffffff", pane: "#ffffff", paneAlt: "#f1f1ee",
  ink: "#23262b", faint: "#7b8087", line: "#d9d9d4",
  sage: "#7cae9b", blue: "#7aa6c9", rose: "#d59a86",
  mustard: "#e0b95c", lavender: "#a99fc9", mint: "#8fc7b0",
  red: "#c2503a", green: "#3f9d6b", sel: "#fdeec6",
  wash: "#f7f7f4",
};
const MONO = "'IBM Plex Mono', ui-monospace, Menlo, Consolas, monospace";
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const fmt = (v, d = 2) => {
  if (typeof v !== "number") return String(v);
  if (Number.isInteger(v) && Math.abs(v) < 1e6) return String(v);
  return Math.abs(v) >= 100 ? v.toFixed(0) : Math.abs(v) >= 10 ? v.toFixed(1) : v.toFixed(d);
};
const CAT_TONES = [C.blue, C.red, C.mustard, C.sage, C.lavender, C.rose, C.mint, "#8892a8"];
const TYPE_LABEL = { q: "quant", n: "nominal", t: "temporal" };
const TYPE_TONE = { q: C.blue, n: C.mustard, t: C.sage };

/* deterministic rng so the mock data never jitters */
function rng(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const gauss = (r, m, sd) => {
  const u = 1 - r(), v = 1 - r();
  return m + sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
};

/* ============================================================
   DATASETS — three fictional tidy tables
   ============================================================ */
function makeSeabirds() {
  const r = rng(4021);
  const rows = [];
  const spec = [
    { species: "Petrel", wing: [212, 9], mass: [3720, 340], bill: [39, 2.2] },
    { species: "Skua", wing: [231, 8], mass: [4460, 390], bill: [47, 2.6] },
    { species: "Tern", wing: [196, 7], mass: [3110, 270], bill: [34, 1.9] },
  ];
  const islands = ["Brant", "Corr", "Dune"];
  spec.forEach((s, si) => {
    for (let i = 0; i < 30; i++) {
      const sex = r() < 0.5 ? "F" : "M";
      const k = sex === "M" ? 1.05 : 0.96;
      rows.push({
        species: s.species,
        island: islands[Math.floor(r() * (si === 2 ? 2 : 3))],
        sex,
        wing_mm: +gauss(r, s.wing[0] * k, s.wing[1]).toFixed(1),
        mass_g: Math.round(gauss(r, s.mass[0] * k, s.mass[1])),
        bill_mm: +gauss(r, s.bill[0] * k, s.bill[1]).toFixed(1),
      });
    }
  });
  return rows;
}
function makeClimate() {
  const r = rng(977);
  const cities = [
    { city: "Aster", base: 11, amp: 9, rain: 74 },
    { city: "Brine", base: 16, amp: 5, rain: 38 },
    { city: "Cobalt", base: 4, amp: 13, rain: 52 },
    { city: "Dell", base: 21, amp: 3, rain: 110 },
  ];
  const rows = [];
  cities.forEach((c) => {
    for (let m = 0; m < 24; m++) {
      const yr = 1 + Math.floor(m / 12), mo = (m % 12) + 1;
      const season = Math.sin(((m % 12) / 12) * 2 * Math.PI - Math.PI / 2);
      rows.push({
        city: c.city,
        month: "Y" + yr + "-" + String(mo).padStart(2, "0"),
        temp_c: +(c.base + c.amp * season + gauss(r, 0, 1.1)).toFixed(1),
        rain_mm: Math.max(2, Math.round(c.rain * (1 - 0.5 * season) + gauss(r, 0, 12))),
      });
    }
  });
  return rows;
}
function makeEngines() {
  const r = rng(15300);
  const origins = [
    { origin: "NA", hp: [175, 45], wt: [1620, 260], eff: 0.86 },
    { origin: "EU", hp: [128, 34], wt: [1330, 190], eff: 1.04 },
    { origin: "JP", hp: [108, 26], wt: [1180, 150], eff: 1.16 },
  ];
  const rows = [];
  origins.forEach((o) => {
    for (let i = 0; i < 14; i++) {
      const hp = Math.round(clamp(gauss(r, o.hp[0], o.hp[1]), 55, 320));
      const wt = Math.round(clamp(gauss(r, o.wt[0] + hp * 1.6, o.wt[1]), 850, 2600));
      const cyl = hp > 190 ? "8" : hp > 120 ? "6" : "4";
      rows.push({ origin: o.origin, cyl, hp, weight_kg: wt, mpg: +clamp((5200 / wt) * 12 * o.eff + gauss(r, 0, 2.2), 9, 52).toFixed(1) });
    }
  });
  return rows;
}
const DATASETS = {
  seabirds: {
    id: "seabirds", name: "seabirds", note: "90 field observations of 3 fictional seabird species",
    fields: [
      { name: "species", type: "n" }, { name: "island", type: "n" }, { name: "sex", type: "n" },
      { name: "wing_mm", type: "q" }, { name: "mass_g", type: "q" }, { name: "bill_mm", type: "q" },
    ],
    rows: makeSeabirds(),
  },
  climate: {
    id: "climate", name: "climate", note: "24 months × 4 fictional cities, temperature & rainfall",
    fields: [
      { name: "city", type: "n" }, { name: "month", type: "t" },
      { name: "temp_c", type: "q" }, { name: "rain_mm", type: "q" },
    ],
    rows: makeClimate(),
  },
  engines: {
    id: "engines", name: "engines", note: "42 fictional car models: power, weight, economy",
    fields: [
      { name: "origin", type: "n" }, { name: "cyl", type: "n" },
      { name: "hp", type: "q" }, { name: "weight_kg", type: "q" }, { name: "mpg", type: "q" },
    ],
    rows: makeEngines(),
  },
};

/* ============================================================
   PIPELINE ENGINE — tidyverse verbs over plain row objects
   ============================================================ */
let stepc = 0;
const mkStep = (kind, cfg) => ({ id: "s" + ++stepc, kind, on: true, ...cfg });
const AGGS = ["mean", "sum", "min", "max", "count"];
const DOPS = ["+", "-", "*", "/", "log10"];
const FOPS = ["=", "≠", ">", "<"];

function applyAgg(fn, vals) {
  if (fn === "count") return vals.length;
  if (!vals.length) return 0;
  if (fn === "sum") return vals.reduce((a, b) => a + b, 0);
  if (fn === "mean") return vals.reduce((a, b) => a + b, 0) / vals.length;
  if (fn === "min") return Math.min(...vals);
  return Math.max(...vals);
}
const aggName = (fn, field) => (fn === "count" ? "count" : fn + "_" + field);

function schemaAfter(datasetId, steps, uptoExclusive) {
  let fields = DATASETS[datasetId].fields.map((f) => ({ ...f }));
  const n = uptoExclusive == null ? steps.length : uptoExclusive;
  for (let i = 0; i < n; i++) {
    const s = steps[i];
    if (!s.on) continue;
    if (s.kind === "derive") fields = [...fields.filter((f) => f.name !== s.name), { name: s.name, type: "q" }];
    if (s.kind === "summarize") {
      const by = fields.find((f) => f.name === s.by);
      fields = [...(by ? [by] : []), { name: aggName(s.fn, s.field), type: "q" }];
    }
  }
  return fields;
}

function evaluate(datasetId, steps) {
  const ds = DATASETS[datasetId];
  let rows = ds.rows;
  let fields = ds.fields.map((f) => ({ ...f }));
  const fmap = () => Object.fromEntries(fields.map((f) => [f.name, f.type]));
  let err = null;
  for (const s of steps) {
    if (!s.on) continue;
    if (s.kind === "filter") {
      const t = fmap()[s.field];
      if (t === undefined) { err = "filter refers to missing field " + s.field; continue; }
      if (s.value === "" || s.value == null) continue;
      const val = t === "q" ? +s.value : s.value;
      rows = rows.filter((r) => {
        const v = r[s.field];
        if (s.op === "=") return String(v) === String(val);
        if (s.op === "≠") return String(v) !== String(val);
        if (s.op === ">") return +v > +val;
        return +v < +val;
      });
    } else if (s.kind === "derive") {
      rows = rows.map((r) => {
        let v;
        if (s.op === "log10") { const a = +r[s.a]; v = a > 0 ? Math.log10(a) : NaN; }
        else {
          const a = +r[s.a], b = +r[s.b];
          v = s.op === "+" ? a + b : s.op === "-" ? a - b : s.op === "*" ? a * b : b === 0 ? NaN : a / b;
        }
        return { ...r, [s.name]: Number.isFinite(v) ? +v.toFixed(3) : null };
      }).filter((r) => r[s.name] !== null);
      fields = [...fields.filter((f) => f.name !== s.name), { name: s.name, type: "q" }];
    } else if (s.kind === "summarize") {
      const groups = new Map();
      rows.forEach((r) => {
        const k = String(r[s.by]);
        if (!groups.has(k)) groups.set(k, []);
        groups.get(k).push(r);
      });
      const out = [];
      const byType = fmap()[s.by] || "n";
      groups.forEach((grp, k) => {
        const vals = s.fn === "count" ? grp : grp.map((r) => +r[s.field]).filter(Number.isFinite);
        out.push({ [s.by]: k, [aggName(s.fn, s.field)]: +applyAgg(s.fn, vals).toFixed(3) });
      });
      rows = out;
      fields = [{ name: s.by, type: byType }, { name: aggName(s.fn, s.field), type: "q" }];
    } else if (s.kind === "sort") {
      const t = fmap()[s.field];
      rows = [...rows].sort((a, b) => {
        const va = a[s.field], vb = b[s.field];
        const c = t === "q" ? +va - +vb : String(va).localeCompare(String(vb));
        return s.dir === "asc" ? c : -c;
      });
    } else if (s.kind === "limit") {
      rows = rows.slice(0, Math.max(1, +s.n || 10));
    }
  }
  return { rows, fields, err };
}

const stepLabel = (s) => {
  if (s.kind === "filter") return "filter " + s.field + " " + s.op + " " + s.value;
  if (s.kind === "derive") return "derive " + s.name + " = " + (s.op === "log10" ? "log10(" + s.a + ")" : s.a + " " + s.op + " " + s.b);
  if (s.kind === "summarize") return "group " + s.by + " → " + aggName(s.fn, s.field);
  if (s.kind === "sort") return "sort " + s.field + " " + (s.dir === "asc" ? "↑" : "↓");
  return "limit " + s.n;
};

/* the spec as tidyverse/ggplot source — used by the spec strip */
function asGgplot(chart) {
  const c = chart, m = c.mapping;
  const L = [c.datasetId];
  c.steps.filter((s) => s.on).forEach((s) => {
    if (s.kind === "filter" && s.value !== "" && s.value != null) {
      const op = s.op === "=" ? "==" : s.op === "≠" ? "!=" : s.op;
      const v = isNaN(+s.value) ? '"' + s.value + '"' : s.value;
      L.push("filter(" + s.field + " " + op + " " + v + ")");
    }
    if (s.kind === "derive") L.push("mutate(" + s.name + " = " + (s.op === "log10" ? "log10(" + s.a + ")" : s.a + " " + s.op + " " + s.b) + ")");
    if (s.kind === "summarize") L.push("group_by(" + s.by + ") |> summarise(" + aggName(s.fn, s.field) + " = " + (s.fn === "count" ? "n()" : s.fn + "(" + s.field + ")") + ")");
    if (s.kind === "sort") L.push("arrange(" + (s.dir === "desc" ? "desc(" + s.field + ")" : s.field) + ")");
    if (s.kind === "limit") L.push("slice_head(n = " + s.n + ")");
  });
  const aes = ["x = " + (m.x || "?"), "y = " + (m.y || "?")];
  if (m.color) aes.push("colour = " + m.color);
  if (m.size) aes.push("size = " + m.size);
  let out = L.join(" |>\n  ") + " |>\n  ggplot(aes(" + aes.join(", ") + ")) +\n  geom_" + c.geom + "()";
  if (m.facet) out += " +\n  facet_wrap(~" + m.facet + ")";
  if (c.yScale === "log") out += " +\n  scale_y_log10()";
  return out;
}

/* ============================================================
   WORLD — shared state for ONE embedded instance.
   Every widget on the page constructs its own; they never
   see each other. Subscribers instead of a single notify hook
   so a lesson rail and a workbench can both listen.
   ============================================================ */
let seqc = 0, notec = 0, snapc = 0, docc = 0;
const GEOMS = ["point", "line", "bar", "area"];
const SLOTS = ["x", "y", "color", "size", "facet"];
const DOC_NAMES = ["α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ", "λ", "μ"];

function defaultChart(datasetId) {
  const ds = DATASETS[datasetId];
  const qs = ds.fields.filter((f) => f.type === "q").map((f) => f.name);
  const nom = ds.fields.find((f) => f.type === "n");
  const temp = ds.fields.find((f) => f.type === "t");
  return {
    datasetId, steps: [],
    geom: temp ? "line" : "point",
    mapping: { x: temp ? temp.name : qs[0] || null, y: qs[temp ? 0 : 1] || qs[0] || null, color: nom ? nom.name : null, size: null, facet: null },
    yScale: "linear",
  };
}
const cloneChart = (c) => JSON.parse(JSON.stringify(c));

class World {
  constructor(setup) {
    this.subs = new Set();
    this.docn = 0;   /* names (α, β…) count per world, not globally */
    this.snapn = 0;
    this.trace = [];
    this.docs = [];
    this.activeId = null;
    this.snaps = [];
    this.pins = [null, null];
    this.watch = [];
    this.inspected = { title: "nothing inspected yet", value: { hint: "right-click any object on screen, then choose Inspect" } };
    if (setup) setup(this);
    if (!this.docs.length) this.newDoc("seabirds", true);
    if (!this.activeId) this.activeId = this.docs[0].id;
    this.trace = [];
  }
  sub(fn) { this.subs.add(fn); return () => this.subs.delete(fn); }
  bump() { this.subs.forEach((f) => f()); }
  log(type, data) { this.trace.push({ seq: ++seqc, type, data: data || {} }); this.bump(); }
  inspect(title, value) { this.inspected = { title, value }; this.log("inspected", { title }); }

  /* ---- documents ---- */
  doc(id) {
    return this.docs.find((d) => d.id === id)
      || this.docs.find((d) => d.id === this.activeId)
      || this.docs[0];
  }
  active() { return this.doc(this.activeId); }
  newDoc(datasetId, quiet) {
    const d = { id: "d" + ++docc, name: DOC_NAMES[this.docn++ % DOC_NAMES.length], chart: defaultChart(datasetId || "seabirds") };
    this.docs.push(d);
    this.activeId = d.id;
    if (!quiet) this.log("doc_added", { chart: d.name, dataset: d.chart.datasetId });
    return d;
  }
  setActive(id) { const d = this.doc(id); if (d && this.activeId !== d.id) { this.activeId = d.id; this.log("doc_activated", { chart: d.name, note: "object-menu verbs now act on it" }); } }
  renameDoc(id, name) { const d = this.doc(id); if (d && name) { d.name = name; this.log("doc_renamed", { chart: name }); } }
  dupDoc(id) {
    const src = this.doc(id); if (!src) return;
    const d = { id: "d" + ++docc, name: src.name + "′", chart: cloneChart(src.chart) };
    this.docs.push(d); this.activeId = d.id;
    this.log("doc_duplicated", { from: src.name, chart: d.name });
    return d;
  }
  deleteDoc(id) {
    if (this.docs.length < 2) return;
    const d = this.doc(id); if (!d) return;
    this.docs = this.docs.filter((x) => x.id !== d.id);
    if (this.activeId === d.id) this.activeId = this.docs[0].id;
    this.log("doc_removed", { chart: d.name, note: "tiles that showed it fall back to " + this.active().name });
  }

  /* ---- per-document chart mutation ---- */
  setDataset(docId, id) {
    const d = this.doc(docId); if (!d || d.chart.datasetId === id) return;
    d.chart = defaultChart(id);
    this.log("source_set", { chart: d.name, dataset: id, note: "pipeline reset, default encoding inferred" });
  }
  addStep(docId, step) { const d = this.doc(docId); d.chart.steps.push(step); this.log("step_added", { chart: d.name, step: stepLabel(step), kind: step.kind }); }
  updateStep(docId, id, patch) {
    const d = this.doc(docId);
    d.chart.steps = d.chart.steps.map((s) => (s.id === id ? { ...s, ...patch } : s));
    this.bump();
  }
  toggleStep(docId, id) { const d = this.doc(docId); const s = d.chart.steps.find((x) => x.id === id); if (s) { s.on = !s.on; this.log("step_toggled", { chart: d.name, step: stepLabel(s), on: s.on }); } }
  removeStep(docId, id) { const d = this.doc(docId); const s = d.chart.steps.find((x) => x.id === id); d.chart.steps = d.chart.steps.filter((x) => x.id !== id); this.log("step_removed", { chart: d.name, step: s ? stepLabel(s) : id }); }
  moveStep(docId, id, dir) {
    const d = this.doc(docId);
    const i = d.chart.steps.findIndex((s) => s.id === id);
    const j = i + dir;
    if (i < 0 || j < 0 || j >= d.chart.steps.length) return;
    const a = d.chart.steps;
    [a[i], a[j]] = [a[j], a[i]];
    this.log("step_moved", { chart: d.name, step: stepLabel(a[j]), dir: dir < 0 ? "up" : "down" });
  }
  setMapping(docId, slot, field) {
    const d = this.doc(docId);
    d.chart.mapping = { ...d.chart.mapping, [slot]: field };
    this.log("encoded", { chart: d.name, slot, field: field || "(none)" });
  }
  setGeom(docId, g) { const d = this.doc(docId); d.chart.geom = g; this.log("geom_set", { chart: d.name, geom: g }); }
  setYScale(docId, s) { const d = this.doc(docId); d.chart.yScale = s; this.log("scale_set", { chart: d.name, y: s }); }
  filterToCat(docId, field, value, keep) { this.addStep(docId, mkStep("filter", { field, op: keep ? "=" : "≠", value: String(value) })); }
  docOfStep(stepId) { return this.docs.find((d) => d.chart.steps.some((s) => s.id === stepId)); }

  /* ---- snapshots ---- */
  snapshot(docId, name) {
    const d = this.doc(docId);
    const s = { id: "snap" + ++snapc, name: name || d.name + "-" + ++this.snapn, chart: cloneChart(d.chart), at: new Date().toLocaleTimeString() };
    this.snaps.push(s);
    this.log("snapshotted", { from: d.name, chart: s.name });
    return s;
  }
  restoreSnap(id, docId) { const s = this.snaps.find((x) => x.id === id); if (s) { const d = this.doc(docId); d.chart = cloneChart(s.chart); this.log("restored", { chart: s.name, into: d.name }); } }
  restoreAsNew(id) {
    const s = this.snaps.find((x) => x.id === id); if (!s) return;
    const d = this.newDoc(s.chart.datasetId, true);
    d.chart = cloneChart(s.chart);
    this.log("restored", { chart: s.name, into: d.name + " (new document)" });
    return d;
  }
  deleteSnap(id) { const s = this.snaps.find((x) => x.id === id); this.snaps = this.snaps.filter((x) => x.id !== id); this.pins = this.pins.map((p) => (p === id ? null : p)); this.log("snap_deleted", { chart: s ? s.name : id }); }
  pinSnap(slot, id) { this.pins[slot] = id; this.log("pinned", { slot: slot === 0 ? "A" : "B", chart: (this.snaps.find((s) => s.id === id) || {}).name }); }
  watchAdd(ptype, value) { this.watch.push({ id: ++notec, ptype, value }); this.log("watched", { ptype }); }
  watchRemove(id) { this.watch = this.watch.filter((n) => n.id !== id); this.log("watch_removed", { id }); }
}

function fieldStats(datasetId, steps, name) {
  const { rows, fields } = evaluate(datasetId, steps);
  const f = fields.find((x) => x.name === name);
  if (!f) return null;
  const vals = rows.map((r) => r[name]);
  if (f.type === "q") {
    const nums = vals.map(Number).filter(Number.isFinite);
    const mean = nums.reduce((a, b) => a + b, 0) / (nums.length || 1);
    const sd = Math.sqrt(nums.reduce((a, b) => a + (b - mean) * (b - mean), 0) / (nums.length || 1));
    return { type: "quantitative", n: nums.length, min: +Math.min(...nums).toFixed(2), max: +Math.max(...nums).toFixed(2), mean: +mean.toFixed(2), sd: +sd.toFixed(2) };
  }
  const counts = {};
  vals.forEach((v) => { counts[v] = (counts[v] || 0) + 1; });
  return { type: f.type === "t" ? "temporal" : "nominal", n: vals.length, distinct: Object.keys(counts).length, levels: counts };
}
function describeDataset(id) {
  const d = DATASETS[id];
  return { presentationType: "dataset", name: d.name, rows: d.rows.length, note: d.note, fields: Object.fromEntries(d.fields.map((f) => [f.name, TYPE_LABEL[f.type]])) };
}

/* ============================================================
   PLOT ENGINE — pure spec → drawable geometry
   ============================================================ */
function niceTicks(lo, hi, n = 5) {
  if (!(hi > lo)) return [lo];
  const span = hi - lo, raw = span / n;
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const norm = raw / mag;
  const step = (norm < 1.5 ? 1 : norm < 3.5 ? 2 : norm < 7.5 ? 5 : 10) * mag;
  const t0 = Math.ceil(lo / step) * step;
  const out = [];
  for (let v = t0; v <= hi + 1e-9; v += step) out.push(+v.toFixed(10));
  return out;
}
const hexLerp = (a, b, t) => {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  return "#" + pa.map((v, i) => Math.round(v + (pb[i] - v) * t).toString(16).padStart(2, "0")).join("");
};

function buildPlot(chart, W, H, mini) {
  const { rows, fields, err } = evaluate(chart.datasetId, chart.steps);
  const ftype = Object.fromEntries(fields.map((f) => [f.name, f.type]));
  const m = chart.mapping, geom = chart.geom;
  const problems = [];
  if (err) problems.push(err);
  for (const slot of SLOTS) if (m[slot] && !ftype[m[slot]]) problems.push(slot + " ↦ " + m[slot] + " is not in the pipeline output");
  if (!m.x || !ftype[m.x]) problems.push("map x to a field");
  if (!m.y || !ftype[m.y]) problems.push("map y to a field");
  if (rows.length === 0) problems.push("pipeline output is empty — a filter step is too strict");
  if (problems.length) return { problems, rows };
  const xT = ftype[m.x], yT = ftype[m.y];
  if (geom === "bar" && xT === "q") problems.push("geom_bar wants a nominal or temporal x — x is currently " + m.x + " (quantitative). group∑ first, or map x to a category.");
  if (yT !== "q") problems.push("y must be quantitative for geom_" + geom);
  if (problems.length) return { problems, rows };

  let facetVals = [null];
  if (m.facet && ftype[m.facet] !== "q") facetVals = [...new Set(rows.map((r) => String(r[m.facet])))].sort().slice(0, 6);
  const nf = facetVals.length;
  const cols = nf <= 1 ? 1 : nf === 2 ? 2 : nf <= 4 ? 2 : 3;
  const rws = Math.ceil(nf / cols);

  let colorMode = null, cats = [], cramp = null;
  if (m.color) {
    if (ftype[m.color] === "q") {
      const vals = rows.map((r) => +r[m.color]).filter(Number.isFinite);
      colorMode = "q"; cramp = { lo: Math.min(...vals), hi: Math.max(...vals) };
    } else {
      colorMode = "n";
      cats = [...new Set(rows.map((r) => String(r[m.color])))].sort().slice(0, 8);
    }
  }
  const colorOf = (r) => {
    if (!colorMode) return C.blue;
    if (colorMode === "q") { const t = cramp.hi > cramp.lo ? (+r[m.color] - cramp.lo) / (cramp.hi - cramp.lo) : 0.5; return hexLerp(C.blue, C.red, clamp(t, 0, 1)); }
    const i = cats.indexOf(String(r[m.color]));
    return i < 0 ? C.faint : CAT_TONES[i % CAT_TONES.length];
  };

  let xCats = null, xLo = 0, xHi = 1;
  if (xT === "q") {
    const vals = rows.map((r) => +r[m.x]).filter(Number.isFinite);
    xLo = Math.min(...vals); xHi = Math.max(...vals);
    if (xLo === xHi) { xLo -= 1; xHi += 1; }
    const pad = (xHi - xLo) * 0.05; xLo -= pad; xHi += pad;
  } else {
    xCats = [...new Set(rows.map((r) => String(r[m.x])))].sort();
  }

  const yvals = rows.map((r) => +r[m.y]).filter(Number.isFinite);
  let yLo = Math.min(...yvals), yHi = Math.max(...yvals);
  const log = chart.yScale === "log" && yLo > 0;
  if (geom === "bar" || geom === "area") { if (!log) { yLo = Math.min(0, yLo); yHi = Math.max(0, yHi); } }
  if (yLo === yHi) { yLo -= 1; yHi += 1; }
  if (!log) { const pad = (yHi - yLo) * 0.06; yHi += pad; if (!(geom === "bar" || geom === "area")) yLo -= pad; }
  const ly = (v) => Math.log10(v);

  let sLo = 0, sHi = 1;
  if (m.size && ftype[m.size] === "q") {
    const vals = rows.map((r) => +r[m.size]).filter(Number.isFinite);
    sLo = Math.min(...vals); sHi = Math.max(...vals);
  }
  const rOf = (r) => {
    if (!m.size || ftype[m.size] !== "q") return mini ? 2.4 : 4;
    const t = sHi > sLo ? (+r[m.size] - sLo) / (sHi - sLo) : 0.5;
    return (mini ? 1.6 : 3) + Math.sqrt(clamp(t, 0, 1)) * (mini ? 4 : 8);
  };

  const legendW = colorMode && !mini ? 92 : 0;
  const padL = mini ? 26 : 40, padB = mini ? 14 : 24, padT = nf > 1 ? (mini ? 12 : 16) : mini ? 4 : 8, padR = mini ? 4 : 8;
  const gapX = mini ? 6 : 12, gapY = mini ? 6 : 14;
  const plotW = W - legendW;
  const pw = (plotW - padL - padR - gapX * (cols - 1)) / cols;
  const ph = (H - padT * rws - padB - gapY * (rws - 1)) / rws;

  const sx = (v) => {
    if (xT === "q") return ((+v - xLo) / (xHi - xLo)) * pw;
    const i = xCats.indexOf(String(v));
    return ((i + 0.5) / xCats.length) * pw;
  };
  const syRaw = (v) => {
    if (log) return (1 - (ly(+v) - ly(yLo)) / (ly(yHi) - ly(yLo))) * ph;
    return (1 - (+v - yLo) / (yHi - yLo)) * ph;
  };

  const yTicks = log
    ? niceTicks(ly(yLo), ly(yHi), 4).map((e) => ({ v: Math.pow(10, e), label: fmt(Math.pow(10, e)) }))
    : niceTicks(yLo, yHi, mini ? 3 : 5).map((v) => ({ v, label: fmt(v) }));
  const xTicks = xT === "q"
    ? niceTicks(xLo, xHi, mini ? 3 : 5).map((v) => ({ pos: sx(v), label: fmt(v) }))
    : xCats.map((c, i) => ({ pos: sx(c), label: c, i })).filter((t, i) => {
      const max = mini ? 4 : Math.max(3, Math.floor(pw / 34));
      return i % Math.ceil(xCats.length / max) === 0;
    });

  const panels = facetVals.map((fv, pi) => {
    const col = pi % cols, row = Math.floor(pi / cols);
    const x0 = padL + col * (pw + gapX);
    const py0 = padT + row * (ph + gapY + (nf > 1 ? padT : 0));
    const prows = fv === null ? rows : rows.filter((r) => String(r[m.facet]) === fv);
    const marks = [];
    const baseline = log ? ph : syRaw(clamp(0, yLo, yHi));

    if (geom === "point") {
      prows.forEach((r) => {
        if (!Number.isFinite(+r[m.y])) return;
        marks.push({ kind: "c", x: sx(r[m.x]), y: syRaw(r[m.y]), r: rOf(r), fill: colorOf(r), row: r });
      });
    } else if (geom === "line" || geom === "area") {
      const groups = new Map();
      prows.forEach((r) => {
        const k = colorMode === "n" ? String(r[m.color]) : "·";
        if (!groups.has(k)) groups.set(k, []);
        groups.get(k).push(r);
      });
      groups.forEach((grp, k) => {
        const sorted = [...grp].sort((a, b) => (xT === "q" ? +a[m.x] - +b[m.x] : xCats.indexOf(String(a[m.x])) - xCats.indexOf(String(b[m.x]))));
        const pts = sorted.filter((r) => Number.isFinite(+r[m.y])).map((r) => [sx(r[m.x]), syRaw(r[m.y]), r]);
        if (pts.length < 2) { pts.forEach(([x, y, r]) => marks.push({ kind: "c", x, y, r: rOf(r), fill: colorOf(r), row: r })); return; }
        const tone = colorMode === "n" ? CAT_TONES[Math.max(0, cats.indexOf(k)) % CAT_TONES.length] : colorMode === "q" ? C.faint : C.blue;
        const d = pts.map(([x, y], i) => (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" ");
        if (geom === "area") {
          const ad = d + " L" + pts[pts.length - 1][0].toFixed(1) + " " + baseline.toFixed(1) + " L" + pts[0][0].toFixed(1) + " " + baseline.toFixed(1) + " Z";
          marks.push({ kind: "p", d: ad, fill: tone, fillOpacity: 0.25, stroke: "none" });
        }
        marks.push({ kind: "p", d, stroke: tone, fill: "none" });
        pts.forEach(([x, y, r]) => marks.push({ kind: "c", x, y, r: mini ? 1.8 : 3.2, fill: colorOf(r), row: r }));
      });
    } else if (geom === "bar") {
      const byX = new Map();
      prows.forEach((r) => {
        const k = String(r[m.x]);
        if (!byX.has(k)) byX.set(k, []);
        byX.get(k).push(r);
      });
      const band = pw / xCats.length;
      byX.forEach((grp, k) => {
        const cx = sx(k), n = grp.length, bw = (band * 0.72) / n;
        grp.forEach((r, i) => {
          if (!Number.isFinite(+r[m.y])) return;
          const yv = syRaw(r[m.y]);
          const top = Math.min(yv, baseline), h = Math.abs(baseline - yv);
          marks.push({ kind: "r", x: cx - (band * 0.72) / 2 + i * bw, y: top, w: Math.max(1, bw - 1), h: Math.max(0.5, h), fill: colorOf(r), row: r });
        });
      });
    }
    return { x0, y0: py0, w: pw, h: ph, title: fv, marks };
  });

  const legend = colorMode === "n"
    ? cats.map((c, i) => ({ label: c, value: c, color: CAT_TONES[i % CAT_TONES.length] }))
    : colorMode === "q" ? [{ label: fmt(cramp.lo), color: C.blue }, { label: fmt(cramp.hi), color: C.red }] : [];

  return {
    panels, legend, colorMode, colorField: m.color, W, H, padL, padB, legendW,
    yTicks: yTicks.map((t) => ({ pos: syRaw(t.v), label: t.label })),
    xTicks, rowsOut: rows.length, problems: [],
  };
}

/* ============================================================
   PBUI CORE — presentations + accept
   ============================================================ */
const UICtx = React.createContext(null);
const useUI = () => useContext(UICtx);
const typeMatches = (want, have) => want === "any" || (Array.isArray(want) ? want.includes(have) : want === have);

function P({ ptype, value, doc, children, block, svg, onActivate, activateDoc }) {
  const ui = useUI();
  const acceptable = ui.accepting && typeMatches(ui.accepting.ptype, ptype);
  const Tag = svg ? "g" : block ? "div" : "span";
  const clickDoc = acceptable ? "L: ACCEPT   R: menu"
    : onActivate ? "L: " + (activateDoc || "activate") + "   R: menu"
      : "L/R: menu";
  const line = (doc || "<" + ptype + "> " + ui.labelFor(ptype, value)) + "   —   " + clickDoc;
  const primary = (x, y) => {
    if (acceptable) { ui.accepting.resolve({ ptype, value }); ui.setAccepting(null); }
    else if (onActivate) onActivate();
    else ui.openMenu(ptype, value, x, y);
  };
  /* chart marks are not put in the tab order — 90 focusable dots is a trap.
     everything else is reachable: Enter/Space is L, the Menu key is R. */
  const kb = svg ? {} : {
    tabIndex: 0, role: "button", "aria-label": line,
    onFocus: () => ui.setMouseDoc(line),
    onBlur: () => ui.setMouseDoc(null),
    onKeyDown: (e) => {
      const r = e.currentTarget.getBoundingClientRect();
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); e.stopPropagation(); primary(r.left + 8, r.bottom + 2); }
      else if (e.key === "ContextMenu" || (e.shiftKey && e.key === "F10")) {
        e.preventDefault(); e.stopPropagation(); ui.openMenu(ptype, value, r.left + 8, r.bottom + 2);
      }
    },
  };
  return (
    <Tag
      {...kb}
      className={(svg ? "pres-svg" : "pres") + (acceptable ? " acceptable" : "")}
      onContextMenu={(e) => { e.preventDefault(); e.stopPropagation(); ui.openMenu(ptype, value, e.clientX, e.clientY); }}
      onClick={(e) => { e.stopPropagation(); if (acceptable) e.preventDefault(); primary(e.clientX, e.clientY); }}
      onMouseEnter={() => ui.setMouseDoc(line)}
      onMouseLeave={() => ui.setMouseDoc(null)}
    >{children}</Tag>
  );
}
function Pres({ ptype, value }) {
  const ui = useUI();
  const label = ui.labelFor(ptype, value);
  const tone = ptype === "field" ? C.blue : ptype === "dataset" ? C.sage : ptype === "chart" ? C.mustard
    : ptype === "doc" ? C.red : ptype === "step" ? C.lavender : ptype === "cat" ? C.rose : C.paneAlt;
  return (
    <P ptype={ptype} value={value}>
      <span style={{ background: C.pane, border: "1px solid " + C.ink, borderLeft: "4px solid " + tone, padding: "0 5px", fontSize: 11, whiteSpace: "nowrap" }}>{label}</span>
    </P>
  );
}

/* ============================================================
   CHART RENDERERS
   ============================================================ */
function PanelFrame({ p, plot }) {
  return (
    <g>
      <rect x={p.x0} y={p.y0} width={p.w} height={p.h} fill={C.pane} stroke={C.ink} strokeWidth="1.4" />
      {plot.yTicks.map((t, i) => t.pos >= -1 && t.pos <= p.h + 1 && (
        <line key={i} x1={p.x0} y1={p.y0 + t.pos} x2={p.x0 + p.w} y2={p.y0 + t.pos} stroke={C.line} strokeWidth="0.7" />
      ))}
      {p.title != null && <text x={p.x0 + 3} y={p.y0 - 3} fontSize="9" fontWeight="700" fill={C.ink}>{p.title}</text>}
    </g>
  );
}
function AxisLabels({ plot, first }) {
  return (
    <g>
      {plot.yTicks.map((t, i) => t.pos >= -1 && t.pos <= first.h + 1 && (
        <text key={"y" + i} x={first.x0 - 4} y={first.y0 + t.pos + 3} fontSize="8.5" fill={C.faint} textAnchor="end">{t.label}</text>
      ))}
      {plot.panels.map((p, pi) => plot.xTicks.map((t, i) => (
        <text key={pi + "x" + i} x={p.x0 + t.pos} y={p.y0 + p.h + 10} fontSize="8.5" fill={C.faint} textAnchor="middle">{String(t.label).slice(0, 7)}</text>
      )))}
    </g>
  );
}
function PlotSVG({ chart, W, H, docId }) {
  const plot = buildPlot(chart, W, H, false);
  if (plot.problems && plot.problems.length) {
    return (
      <div style={{ border: "2px dashed " + C.red, background: "#fffaf7", padding: 12, fontSize: 11.5, color: C.ink, lineHeight: 1.55 }}>
        <b style={{ display: "block", marginBottom: 3 }}>⚠ this spec does not describe a drawable chart</b>
        {plot.problems.map((p, i) => <div key={i} style={{ color: C.faint }}>· {p}</div>)}
      </div>
    );
  }
  const first = plot.panels[0];
  const mkDatum = (r) => ({ row: r, docId });
  const datumDoc = (r) => "datum " + Object.keys(r).slice(0, 3).map((k) => k + "=" + fmt(r[k])).join(" · ") + "  — R: filter this chart's pipeline to it";
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "flex-start", flexWrap: "wrap" }}>
      <svg viewBox={"0 0 " + (W - plot.legendW) + " " + H} style={{ width: "100%", maxWidth: W - plot.legendW, display: "block" }}>
        {plot.panels.map((p, pi) => <PanelFrame key={pi} p={p} plot={plot} />)}
        <AxisLabels plot={plot} first={first} />
        {plot.panels.map((p, pi) => (
          <g key={"m" + pi}>
            {p.marks.map((mk, i) => {
              if (mk.kind === "p") return <path key={mk.kind + i} d={mk.d} transform={"translate(" + p.x0 + " " + p.y0 + ")"} fill={mk.fill || "none"} fillOpacity={mk.fillOpacity} stroke={mk.stroke} strokeWidth="2" />;
              if (mk.kind === "r") return (
                <P key={mk.kind + i} svg ptype="datum" value={mkDatum(mk.row)} doc={datumDoc(mk.row)}>
                  <rect x={p.x0 + mk.x} y={p.y0 + mk.y} width={mk.w} height={mk.h} fill={mk.fill} fillOpacity="0.75" stroke={C.ink} strokeWidth="0.8" style={{ cursor: "pointer" }} />
                </P>
              );
              return (
                <P key={mk.kind + i} svg ptype="datum" value={mkDatum(mk.row)} doc={datumDoc(mk.row)}>
                  <circle cx={p.x0 + mk.x} cy={p.y0 + mk.y} r={mk.r} fill={mk.fill} fillOpacity="0.72" stroke={C.ink} strokeWidth="0.8" style={{ cursor: "pointer" }} />
                </P>
              );
            })}
          </g>
        ))}
      </svg>
      {plot.legend.length > 0 && (
        <div style={{ minWidth: 82, display: "flex", flexDirection: "column", gap: 3 }}>
          <div style={{ fontSize: 9, fontWeight: 700, color: C.faint, letterSpacing: "0.06em" }}>{plot.colorField}</div>
          {plot.colorMode === "n" ? plot.legend.map((l) => (
            <P key={l.value} ptype="cat" value={{ field: plot.colorField, value: l.value, docId }}
              doc={"category " + plot.colorField + "=" + l.value + "  — R: keep only / exclude / facet by"}>
              <span style={{ display: "inline-flex", alignItems: "center", gap: 5, fontSize: 10.5, cursor: "pointer" }}>
                <span style={{ width: 11, height: 11, background: l.color, border: "1px solid " + C.ink, flexShrink: 0 }} />{l.label}
              </span>
            </P>
          )) : (
            <div style={{ fontSize: 10 }}>
              <div style={{ height: 10, width: 66, border: "1px solid " + C.ink, background: "linear-gradient(90deg," + C.blue + "," + C.red + ")" }} />
              <span>{plot.legend[0].label} … {plot.legend[1].label}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
function MiniPlot({ chart, W, H }) {
  const plot = buildPlot(chart, W, H, true);
  if (plot.problems && plot.problems.length) return <div style={{ width: W, height: H, border: "1px dashed " + C.line, fontSize: 9, color: C.faint, padding: 4 }}>not drawable</div>;
  return (
    <svg viewBox={"0 0 " + W + " " + H} style={{ width: W, height: H, display: "block" }}>
      {plot.panels.map((p, pi) => (
        <g key={pi}>
          <rect x={p.x0} y={p.y0} width={p.w} height={p.h} fill={C.pane} stroke={C.ink} strokeWidth="1" />
          {p.title != null && <text x={p.x0 + 2} y={p.y0 - 2} fontSize="7" fontWeight="700" fill={C.ink}>{p.title}</text>}
          {p.marks.map((mk, i) => {
            if (mk.kind === "p") return <path key={i} d={mk.d} transform={"translate(" + p.x0 + " " + p.y0 + ")"} fill={mk.fill || "none"} fillOpacity={mk.fillOpacity} stroke={mk.stroke} strokeWidth="1.3" />;
            if (mk.kind === "r") return <rect key={i} x={p.x0 + mk.x} y={p.y0 + mk.y} width={mk.w} height={mk.h} fill={mk.fill} fillOpacity="0.8" stroke={C.ink} strokeWidth="0.5" />;
            return <circle key={i} cx={p.x0 + mk.x} cy={p.y0 + mk.y} r={mk.r} fill={mk.fill} fillOpacity="0.8" stroke={C.ink} strokeWidth="0.4" />;
          })}
        </g>
      ))}
    </svg>
  );
}

/* ============================================================
   WINDOW MANAGER — split tree
   ============================================================ */
let idc = 1;
const nid = () => "n" + idc++;
const DOC_APPS = ["chart", "table", "pipeline", "encode", "spec"];
const leaf = (app, doc) => ({ id: nid(), type: "leaf", app, doc: doc || null });
const split = (dir, a, b, ratio = 0.5) => ({ id: nid(), type: "split", dir, a, b, ratio });
function updateNode(node, id, fn) {
  if (node.id === id) return fn(node);
  if (node.type === "split") {
    const a = updateNode(node.a, id, fn), b = updateNode(node.b, id, fn);
    if (a !== node.a || b !== node.b) return { ...node, a, b };
  }
  return node;
}
function removeLeaf(node, id) {
  if (node.type === "split") {
    if (node.a.id === id) return node.b;
    if (node.b.id === id) return node.a;
    const a = removeLeaf(node.a, id), b = removeLeaf(node.b, id);
    if (a !== node.a || b !== node.b) return { ...node, a, b };
  }
  return node;
}
function findLeaf(node, id) {
  if (node.type === "leaf") return node.id === id ? node : null;
  return findLeaf(node.a, id) || findLeaf(node.b, id);
}
function allLeaves(node) { return node.type === "leaf" ? [node] : [...allLeaves(node.a), ...allLeaves(node.b)]; }
function countLeaves(node) { return node.type === "leaf" ? 1 : countLeaves(node.a) + countLeaves(node.b); }
function cloneTree(node) {
  return node.type === "leaf" ? { ...node, id: nid() } : { ...node, id: nid(), a: cloneTree(node.a), b: cloneTree(node.b) };
}
const SNAPS_R = [0.25, 1 / 3, 0.5, 2 / 3, 0.75];
function snapFrac(f) { for (const s of SNAPS_R) if (Math.abs(f - s) < 0.022) return { f: s, snapped: true }; return { f, snapped: false }; }

function WMDivider({ dir, containerRef, onRatio }) {
  const [mode, setMode] = useState(0);
  const row = dir === "row";
  const down = (e) => {
    e.preventDefault();
    const prev = document.body.style.userSelect; document.body.style.userSelect = "none";
    const move = (ev) => {
      const el = containerRef.current; if (!el) return;
      const r = el.getBoundingClientRect();
      let f = row ? (ev.clientX - r.left) / r.width : (ev.clientY - r.top) / r.height;
      f = clamp(f, 0.1, 0.9);
      const s = snapFrac(f); setMode(s.snapped ? 3 : 2); onRatio(s.f);
    };
    const up = () => { document.body.style.userSelect = prev; setMode(0); window.removeEventListener("mousemove", move); window.removeEventListener("mouseup", up); };
    window.addEventListener("mousemove", move); window.addEventListener("mouseup", up);
  };
  const size = row ? { width: 8, cursor: "col-resize", alignSelf: "stretch" } : { height: 8, cursor: "row-resize" };
  return (
    <div onMouseDown={down} onMouseEnter={() => mode === 0 && setMode(1)} onMouseLeave={() => mode === 1 && setMode(0)}
      style={{ ...size, flexShrink: 0, background: mode === 3 ? C.mustard : mode === 2 ? C.sage : mode === 1 ? C.paneAlt : "transparent", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={row ? { width: 2, height: 26, borderLeft: "2px dotted " + C.line } : { height: 2, width: 26, borderTop: "2px dotted " + C.line }} />
    </div>
  );
}
function NodeView({ node }) { return node.type === "leaf" ? <TileView leafNode={node} /> : <SplitView node={node} />; }
function SplitView({ node }) {
  const ui = useUI(); const ref = useRef(null); const row = node.dir === "row";
  return (
    <div ref={ref} style={{ flex: 1, display: "flex", flexDirection: row ? "row" : "column", minWidth: 0, minHeight: 0, alignItems: "stretch" }}>
      <div style={{ flex: node.ratio + " 1 0px", display: "flex", minWidth: 0, minHeight: 0 }}><NodeView node={node.a} /></div>
      <WMDivider dir={node.dir} containerRef={ref} onRatio={(r) => ui.wm.setRatio(node.id, r)} />
      <div style={{ flex: (1 - node.ratio) + " 1 0px", display: "flex", minWidth: 0, minHeight: 0 }}><NodeView node={node.b} /></div>
    </div>
  );
}
function TBtn({ onClick, children, doc, disabled }) {
  const ui = useUI();
  return (
    <span onMouseEnter={() => ui.setMouseDoc(doc)} onMouseLeave={() => ui.setMouseDoc(null)}
      onClick={disabled ? undefined : (e) => { e.stopPropagation(); onClick(); }}
      style={{ cursor: disabled ? "default" : "pointer", opacity: disabled ? 0.35 : 1, border: "1px solid " + C.ink, background: C.paneAlt, padding: "0 5px", fontSize: 10, fontWeight: 700, userSelect: "none", lineHeight: "15px" }}>{children}</span>
  );
}
function TileView({ leafNode }) {
  const ui = useUI(); const app = APPS[leafNode.app]; const Comp = app.comp; const drag = ui.drag;
  const docBound = DOC_APPS.includes(leafNode.app);
  const boundDoc = docBound ? ui.world.doc(leafNode.doc) : null;
  const isTarget = drag && drag.over === leafNode.id && drag.from !== leafNode.id;
  const isSource = drag && drag.from === leafNode.id;
  const zone = isTarget ? drag.zone : null;
  const zoneRect =
    zone === "left" ? { left: 0, top: 0, bottom: 0, width: "50%" } :
      zone === "right" ? { right: 0, top: 0, bottom: 0, width: "50%" } :
        zone === "top" ? { top: 0, left: 0, right: 0, height: "50%" } :
          zone === "bottom" ? { bottom: 0, left: 0, right: 0, height: "50%" } :
            zone === "center" ? { inset: 0 } : null;
  return (
    <div ref={(el) => ui.wm.registerRef(leafNode.id, el)} style={{
      flex: 1, display: "flex", flexDirection: "column", border: "2px solid " + C.ink, background: C.pane,
      minWidth: 0, minHeight: 0, position: "relative", opacity: isSource ? 0.75 : 1,
    }}>
      {zoneRect && (
        <div style={{ position: "absolute", ...zoneRect, zIndex: 5, pointerEvents: "none", background: "rgba(194,80,58,0.16)", border: "3px dashed " + C.red, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <span style={{ background: C.pane, border: "2px solid " + C.ink, boxShadow: "2px 2px 0 " + C.ink, padding: "1px 8px", fontSize: 10.5, fontWeight: 700 }}>{zone === "center" ? "⇄ swap apps" : "split-dock here · old tile closes"}</span>
        </div>
      )}
      <div style={{ display: "flex", alignItems: "center", gap: 6, background: app.color, borderBottom: "2px solid " + C.ink, padding: "2px 6px", flexShrink: 0, overflow: "hidden", minWidth: 0 }}>
        <span onMouseDown={(e) => ui.wm.startDrag(leafNode.id, e)}
          onMouseEnter={() => ui.setMouseDoc("drag ⠿ — drop on a tile's CENTRE to swap apps, or near an EDGE to split-dock there")} onMouseLeave={() => ui.setMouseDoc(null)}
          style={{ cursor: "grab", fontWeight: 700, userSelect: "none" }}>⠿</span>
        <P ptype="tile" value={leafNode.id} doc={"tile [" + app.title + (boundDoc ? " · " + boundDoc.name : "") + "] — split / close / swap"}>
          <b style={{ fontSize: 11, letterSpacing: "0.05em", textTransform: "uppercase", whiteSpace: "nowrap" }}>{app.title}{boundDoc ? " · " + boundDoc.name : ""}</b>
        </P>
        <span style={{ flex: 1 }} />
        <select value={leafNode.app} onChange={(e) => ui.wm.setLeafApp(leafNode.id, e.target.value)} onMouseDown={(e) => e.stopPropagation()}
          style={{ border: "1px solid " + C.ink, background: C.pane, fontSize: 10, padding: "0 2px", fontFamily: "inherit", minWidth: 0, flexShrink: 1, maxWidth: 96 }}>
          {Object.entries(APPS).map(([id, a]) => <option key={id} value={id}>{a.title}</option>)}
        </select>
        <TBtn doc="split this tile: new tile to the RIGHT" onClick={() => ui.wm.splitLeaf(leafNode.id, "row")}>⬌</TBtn>
        <TBtn doc="split this tile: new tile BELOW" onClick={() => ui.wm.splitLeaf(leafNode.id, "col")}>⬍</TBtn>
        <TBtn doc="close this tile (its sibling absorbs the space; the document is untouched)" disabled={!ui.wm.canClose} onClick={() => ui.wm.closeLeaf(leafNode.id)}>✕</TBtn>
      </div>
      <div style={{ flex: 1, minHeight: 0, minWidth: 0, display: "flex", flexDirection: "column" }}><Comp leafId={leafNode.id} docId={boundDoc ? boundDoc.id : null} /></div>
    </div>
  );
}

/* ============================================================
   SHARED UI BITS
   ============================================================ */
const AppBody = ({ children, style }) => (<div style={{ flex: 1, minHeight: 0, minWidth: 0, overflow: "auto", padding: "6px 8px", ...style }}>{children}</div>);
const Hint = ({ children }) => <div style={{ color: C.faint, fontSize: 10.5, marginBottom: 6, lineHeight: 1.35 }}>{children}</div>;
function Btn({ onClick, children, tone, disabled, title }) {
  return (
    <button title={title} disabled={disabled} onClick={onClick} style={{
      fontFamily: "inherit", fontSize: 11, fontWeight: 700, letterSpacing: "0.03em",
      background: disabled ? C.paneAlt : (tone || C.blue), color: C.ink, border: "2px solid " + C.ink,
      boxShadow: "2px 2px 0 " + C.ink, padding: "3px 10px", cursor: disabled ? "default" : "pointer", opacity: disabled ? 0.5 : 1,
    }}>{children}</button>
  );
}
function Sel({ value, onChange, options, width }) {
  return (
    <select value={value == null ? "" : value} onChange={(e) => onChange(e.target.value)}
      style={{ border: "1px solid " + C.ink, background: C.pane, fontSize: 10.5, padding: "1px 2px", fontFamily: "inherit", maxWidth: width || 110 }}>
      {options.map((o) => <option key={o.v} value={o.v}>{o.l}</option>)}
    </select>
  );
}
function Num({ value, onChange, width }) {
  return <input type="number" value={value} onChange={(e) => onChange(e.target.value)}
    style={{ border: "1px solid " + C.ink, background: C.pane, fontSize: 10.5, padding: "1px 3px", fontFamily: "inherit", width: width || 58 }} />;
}
function FieldChip({ name, type, doc }) {
  return (
    <P ptype="field" value={name} doc={doc || ("field " + name + " (" + (TYPE_LABEL[type] || "?") + ")")}>
      <span style={{ border: "1px solid " + C.ink, background: C.pane, borderLeft: "4px solid " + (TYPE_TONE[type] || C.paneAlt), padding: "0 5px", fontSize: 10.5, whiteSpace: "nowrap" }}>
        {name}<span style={{ color: C.faint, fontSize: 8.5 }}> {type || "?"}</span>
      </span>
    </P>
  );
}
function DatasetChip({ id, big, docId }) {
  const ui = useUI(); const d = ui.world.doc(docId);
  return (
    <P ptype="dataset" value={id} onActivate={() => ui.world.setDataset(docId, id)} activateDoc={"use as source of chart " + (d ? d.name : "")}
      doc={"dataset " + id + " · " + DATASETS[id].rows.length + " rows"}>
      <span style={{ border: "1px solid " + C.ink, background: d && d.chart.datasetId === id ? C.sel : C.paneAlt, fontWeight: 700, padding: big ? "1px 8px" : "0 6px", fontSize: big ? 12 : 10.5 }}>{id}</span>
    </P>
  );
}
function DocChip({ id, big }) {
  const ui = useUI(); const w = ui.world; const d = w.doc(id);
  if (!d) return null;
  const isActive = w.activeId === d.id;
  return (
    <P ptype="doc" value={d.id} onActivate={() => w.setActive(d.id)} activateDoc="make it the ACTIVE chart (object-menu verbs act on it)"
      doc={"chart document " + d.name + " · " + d.chart.datasetId + " ⊳ " + d.chart.steps.filter((s) => s.on).length + " steps ⊳ geom_" + d.chart.geom + (isActive ? " · ACTIVE" : "")}>
      <span style={{ border: "1px solid " + C.ink, borderLeft: "4px solid " + (isActive ? C.red : C.line), background: isActive ? C.sel : C.pane, fontWeight: 700, padding: big ? "1px 9px" : "0 6px", fontSize: big ? 12 : 10.5 }}>{d.name}</span>
    </P>
  );
}
function DocBar({ docId, leafId }) {
  const ui = useUI(); const w = ui.world;
  return (
    <div style={{ display: "flex", gap: 5, alignItems: "center", padding: "4px 8px 0", flexShrink: 0, flexWrap: "wrap" }}>
      <span style={{ fontSize: 9, fontWeight: 700, color: C.faint, letterSpacing: "0.08em" }}>DOC</span>
      <DocChip id={docId} />
      <select value={docId || ""} onChange={(e) => ui.wm.setLeafDoc(leafId, e.target.value)} onMouseDown={(e) => e.stopPropagation()}
        style={{ border: "1px solid " + C.ink, background: C.pane, fontSize: 10, padding: "0 2px", fontFamily: "inherit" }}
        title="re-point this tile at another chart document">
        {w.docs.map((d) => <option key={d.id} value={d.id}>{d.name} · {d.chart.datasetId}</option>)}
      </select>
      <TBtn doc="new chart document — this tile re-points to it" onClick={() => { const d = w.newDoc(); ui.wm.setLeafDoc(leafId, d.id); }}>＋</TBtn>
      {w.activeId !== docId && <TBtn doc={"make " + (w.doc(docId) || {}).name + " the ACTIVE chart"} onClick={() => w.setActive(docId)}>set active</TBtn>}
    </div>
  );
}

/* ============================================================
   APPS
   ============================================================ */
function DataApp() {
  const w = useUI().world;
  const act = w.active();
  return (
    <AppBody>
      <Hint>every dataset and field is a live presentation. L-click a dataset → source of the ACTIVE chart (<DocChip id={act.id} />). R-click a field → map it, filter on it, inspect its distribution.</Hint>
      {Object.values(DATASETS).map((d) => (
        <div key={d.id} style={{ border: "1px solid " + C.line, borderLeft: "4px solid " + (act.chart.datasetId === d.id ? C.red : C.line), padding: "5px 7px", marginBottom: 7, background: act.chart.datasetId === d.id ? "#fffdf4" : "transparent" }}>
          <div style={{ display: "flex", gap: 8, alignItems: "baseline", marginBottom: 3 }}>
            <DatasetChip id={d.id} big />
            <span style={{ color: C.faint, fontSize: 10 }}>{d.rows.length} rows</span>
            {act.chart.datasetId === d.id && <span style={{ color: C.red, fontSize: 9.5, fontWeight: 700 }}>← SOURCE of {act.name}</span>}
          </div>
          <div style={{ color: C.faint, fontSize: 10, marginBottom: 4 }}>{d.note}</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
            {d.fields.map((f) => <FieldChip key={f.name} name={f.name} type={f.type} />)}
          </div>
        </div>
      ))}
    </AppBody>
  );
}

function TableApp({ leafId, docId }) {
  const w = useUI().world;
  const d = w.doc(docId); const c = d.chart;
  const { rows, fields, err } = evaluate(c.datasetId, c.steps);
  const show = rows.slice(0, 80);
  return (
    <>
      <DocBar docId={d.id} leafId={leafId} />
      <AppBody>
        <Hint>output of <b>{c.datasetId}</b> ⊳ {c.steps.filter((s) => s.on).length} steps → <b>{rows.length}</b> rows. headers are &lt;field&gt; presentations; row № cells are &lt;datum&gt; presentations.</Hint>
        {err && <div style={{ color: C.red, fontSize: 10.5, marginBottom: 4 }}>⚠ {err}</div>}
        <table style={{ borderCollapse: "collapse", fontSize: 10.5, width: "100%" }}>
          <thead>
            <tr>
              <th style={{ textAlign: "right", color: C.faint, fontWeight: 400, padding: "1px 4px" }}>№</th>
              {fields.map((f) => (
                <th key={f.name} style={{ textAlign: "left", padding: "1px 4px", borderBottom: "2px solid " + C.ink }}>
                  <FieldChip name={f.name} type={f.type} />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {show.map((r, i) => (
              <tr key={i} style={{ background: i % 2 ? C.paneAlt : "transparent" }}>
                <td style={{ textAlign: "right", padding: "0 4px" }}>
                  <P ptype="datum" value={{ row: r, docId: d.id }} doc={"row " + (i + 1) + " — R: inspect / filter to its categories"}>
                    <span style={{ color: C.faint, borderBottom: "1px dotted " + C.faint, cursor: "pointer" }}>{i + 1}</span>
                  </P>
                </td>
                {fields.map((f) => (
                  <td key={f.name} style={{ padding: "0 6px", textAlign: f.type === "q" ? "right" : "left", fontVariantNumeric: "tabular-nums" }}>{fmt(r[f.name])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length > show.length && <div style={{ color: C.faint, fontSize: 10, marginTop: 4 }}>… {rows.length - show.length} more rows</div>}
        {rows.length === 0 && <div style={{ color: C.red, fontSize: 11 }}>pipeline output is empty — a filter is too strict. Switch a step off with its ✓ box.</div>}
      </AppBody>
    </>
  );
}

function StepEditor({ s, schema, docId }) {
  const w = useUI().world;
  const c = w.doc(docId).chart;
  const qs = schema.filter((f) => f.type === "q").map((f) => ({ v: f.name, l: f.name }));
  const all = schema.map((f) => ({ v: f.name, l: f.name }));
  const noms = schema.filter((f) => f.type !== "q").map((f) => ({ v: f.name, l: f.name }));
  const u = (patch) => w.updateStep(docId, s.id, patch);
  const catOptions = (fieldName) => {
    const f = schema.find((x) => x.name === fieldName);
    if (!f || f.type === "q") return null;
    const { rows } = evaluate(c.datasetId, c.steps.slice(0, c.steps.findIndex((x) => x.id === s.id)));
    return [...new Set(rows.map((r) => String(r[fieldName])))].sort().map((v) => ({ v, l: v }));
  };
  if (s.kind === "filter") {
    const cats = catOptions(s.field);
    return (<span style={{ display: "inline-flex", gap: 3, alignItems: "center", flexWrap: "wrap" }}>
      <Sel value={s.field} onChange={(v) => u({ field: v, value: "" })} options={all} />
      <Sel value={s.op} onChange={(v) => u({ op: v })} options={FOPS.map((o) => ({ v: o, l: o }))} width={40} />
      {cats ? <Sel value={s.value} onChange={(v) => u({ value: v })} options={[{ v: "", l: "…" }, ...cats]} />
        : <Num value={s.value} onChange={(v) => u({ value: v })} />}
    </span>);
  }
  if (s.kind === "derive") {
    return (<span style={{ display: "inline-flex", gap: 3, alignItems: "center", flexWrap: "wrap" }}>
      <input value={s.name} onChange={(e) => u({ name: e.target.value.replace(/\W/g, "_") || "f" })}
        style={{ border: "1px solid " + C.ink, background: C.pane, fontSize: 10.5, padding: "1px 3px", fontFamily: "inherit", width: 66 }} />
      <span>=</span>
      <Sel value={s.a} onChange={(v) => u({ a: v })} options={qs} />
      <Sel value={s.op} onChange={(v) => u({ op: v })} options={DOPS.map((o) => ({ v: o, l: o }))} width={54} />
      {s.op !== "log10" && <Sel value={s.b} onChange={(v) => u({ b: v })} options={qs} />}
    </span>);
  }
  if (s.kind === "summarize") {
    return (<span style={{ display: "inline-flex", gap: 3, alignItems: "center", flexWrap: "wrap" }}>
      <span style={{ color: C.faint }}>by</span><Sel value={s.by} onChange={(v) => u({ by: v })} options={noms.length ? noms : all} />
      <Sel value={s.fn} onChange={(v) => u({ fn: v })} options={AGGS.map((a) => ({ v: a, l: a }))} width={58} />
      {s.fn !== "count" && <Sel value={s.field} onChange={(v) => u({ field: v })} options={qs} />}
    </span>);
  }
  if (s.kind === "sort") {
    return (<span style={{ display: "inline-flex", gap: 3, alignItems: "center" }}>
      <Sel value={s.field} onChange={(v) => u({ field: v })} options={all} />
      <Sel value={s.dir} onChange={(v) => u({ dir: v })} options={[{ v: "asc", l: "↑ asc" }, { v: "desc", l: "↓ desc" }]} width={62} />
    </span>);
  }
  return <span style={{ display: "inline-flex", gap: 3, alignItems: "center" }}><Num value={s.n} onChange={(v) => u({ n: v })} width={48} /> rows</span>;
}

function PipelineApp({ leafId, docId }) {
  const ui = useUI(); const w = ui.world;
  const d = w.doc(docId); const c = d.chart;
  const steps = c.steps;
  const outSchema = schemaAfter(c.datasetId, steps);
  const { rows } = evaluate(c.datasetId, steps);
  const addVia = async (kind) => {
    const schema = schemaAfter(c.datasetId, steps);
    const qs = schema.filter((f) => f.type === "q");
    if (kind === "filter") {
      const r = await ui.accept("field", "FILTER (chart " + d.name + ") — click the FIELD to filter on, in any tile");
      if (!r) return;
      const f = schema.find((x) => x.name === r.value);
      w.addStep(d.id, mkStep("filter", { field: r.value, op: f && f.type === "q" ? ">" : "=", value: "" }));
    } else if (kind === "derive") {
      w.addStep(d.id, mkStep("derive", { name: "ratio", a: qs[0] ? qs[0].name : "", op: "/", b: qs[1] ? qs[1].name : (qs[0] ? qs[0].name : "") }));
    } else if (kind === "summarize") {
      const r = await ui.accept("field", "GROUP BY (chart " + d.name + ") — click a nominal or temporal FIELD anywhere");
      if (!r) return;
      w.addStep(d.id, mkStep("summarize", { by: r.value, fn: "mean", field: qs[0] ? qs[0].name : "" }));
    } else if (kind === "sort") {
      w.addStep(d.id, mkStep("sort", { field: outSchema[0].name, dir: "desc" }));
    } else w.addStep(d.id, mkStep("limit", { n: 10 }));
  };
  return (
    <>
      <DocBar docId={d.id} leafId={leafId} />
      <div style={{ display: "flex", gap: 4, flexWrap: "wrap", padding: "6px 8px 4px", flexShrink: 0 }}>
        <Btn tone={C.blue} onClick={() => addVia("filter")}>+ filter…</Btn>
        <Btn tone={C.mint} onClick={() => addVia("derive")}>+ derive</Btn>
        <Btn tone={C.mustard} onClick={() => addVia("summarize")}>+ group∑…</Btn>
        <Btn tone={C.lavender} onClick={() => addVia("sort")}>+ sort</Btn>
        <Btn tone={C.paneAlt} onClick={() => addVia("limit")}>+ limit</Btn>
      </div>
      <AppBody style={{ paddingTop: 2 }}>
        <Hint>a tidyverse chain. each step is a &lt;step&gt; presentation — R-click to toggle, reorder, remove. ✓ disables without deleting, so you can A/B your own transform.</Hint>
        <div style={{ display: "flex", gap: 6, alignItems: "baseline", marginBottom: 6 }}>
          <span style={{ fontSize: 10, color: C.faint }}>SOURCE</span>
          <DatasetChip id={c.datasetId} big docId={d.id} />
          <span style={{ color: C.faint, fontSize: 10 }}>{DATASETS[c.datasetId].rows.length} rows in</span>
        </div>
        {steps.map((s, i) => (
          <div key={s.id} style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 4, opacity: s.on ? 1 : 0.45 }}>
            <span style={{ color: C.faint, fontSize: 12 }}>⊳</span>
            <span onClick={() => w.toggleStep(d.id, s.id)} title="toggle this step without deleting it" style={{ cursor: "pointer", border: "1px solid " + C.ink, width: 14, height: 14, display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 10, background: s.on ? C.sel : C.pane, flexShrink: 0 }}>{s.on ? "✓" : ""}</span>
            <P ptype="step" value={s.id} doc={"step " + stepLabel(s) + " (chart " + d.name + ") — R: move / toggle / remove"}>
              <span style={{ border: "1px solid " + C.ink, borderLeft: "4px solid " + C.lavender, background: C.pane, padding: "0 5px", fontSize: 10, fontWeight: 700, textTransform: "uppercase" }}>{s.kind}</span>
            </P>
            <StepEditor s={s} schema={schemaAfter(c.datasetId, steps, i)} docId={d.id} />
            <span onClick={() => w.removeStep(d.id, s.id)} style={{ cursor: "pointer", color: C.red, fontWeight: 700, marginLeft: "auto" }} title="remove step">×</span>
          </div>
        ))}
        {steps.length === 0 && <div style={{ color: C.faint, fontSize: 11, marginBottom: 4 }}>no steps — the chart draws the raw table. add a verb above.</div>}
        <div style={{ borderTop: "1px dashed " + C.line, marginTop: 6, paddingTop: 5 }}>
          <span style={{ fontSize: 10, color: C.faint, marginRight: 6 }}>OUT → {rows.length} rows</span>
          <span style={{ display: "inline-flex", flexWrap: "wrap", gap: 4 }}>
            {outSchema.map((f) => <FieldChip key={f.name} name={f.name} type={f.type} />)}
          </span>
        </div>
      </AppBody>
    </>
  );
}

function EncodeApp({ leafId, docId }) {
  const ui = useUI(); const w = ui.world;
  const d = w.doc(docId); const c = d.chart;
  const m = c.mapping;
  const schema = schemaAfter(c.datasetId, c.steps);
  const findT = (n) => { const f = schema.find((x) => x.name === n); return f ? f.type : null; };
  const slotDocs = { x: "position →", y: "position ↑ (quantitative)", color: "hue", size: "mark radius (quantitative)", facet: "small multiples" };
  return (
    <>
      <DocBar docId={d.id} leafId={leafId} />
      <AppBody>
        <Hint>the aesthetic mapping: <b>slot ↦ field</b>. hit <b>⌖</b> then click any field chip in ANY tile — data browser, table header, pipeline out-schema.</Hint>
        <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginBottom: 8 }}>
          <span style={{ fontSize: 10, fontWeight: 700, alignSelf: "center" }}>GEOM</span>
          {GEOMS.map((g) => (
            <P key={g} ptype="geom" value={g} onActivate={() => w.setGeom(d.id, g)} activateDoc={"use this geom in chart " + d.name} doc={"geom_" + g}>
              <span style={{ cursor: "pointer", fontSize: 10.5, fontWeight: 700, padding: "1px 8px", border: "1px solid " + C.ink, background: c.geom === g ? C.sel : C.paneAlt }}>{g}</span>
            </P>
          ))}
        </div>
        <table style={{ borderCollapse: "collapse", fontSize: 11 }}>
          <tbody>
            {SLOTS.map((slot) => (
              <tr key={slot}>
                <td style={{ padding: "3px 8px 3px 0", fontWeight: 700, verticalAlign: "middle" }}>{slot}</td>
                <td style={{ padding: "3px 6px", verticalAlign: "middle" }}>
                  {m[slot] ? <FieldChip name={m[slot]} type={findT(m[slot])} /> : <span style={{ color: C.faint }}>— unmapped —</span>}
                  {m[slot] && !findT(m[slot]) && <span style={{ color: C.red, fontSize: 9.5 }}> ⚠ not in output</span>}
                </td>
                <td style={{ padding: "3px 2px" }}>
                  <TBtn doc={"accept a <field> for " + slot + " — click one anywhere"} onClick={async () => {
                    const r = await ui.accept("field", "MAP " + slot.toUpperCase() + " of chart " + d.name + " ↦ click a FIELD anywhere");
                    if (r) w.setMapping(d.id, slot, r.value);
                  }}>⌖</TBtn>
                </td>
                <td style={{ padding: "3px 2px" }}>
                  <TBtn doc={"clear " + slot} disabled={!m[slot]} onClick={() => w.setMapping(d.id, slot, null)}>×</TBtn>
                </td>
                <td style={{ padding: "3px 6px", color: C.faint, fontSize: 9.5 }}>{slotDocs[slot]}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div style={{ marginTop: 8, display: "flex", gap: 6, alignItems: "center" }}>
          <span style={{ fontSize: 10, fontWeight: 700 }}>Y SCALE</span>
          {["linear", "log"].map((s) => (
            <span key={s} onClick={() => w.setYScale(d.id, s)} style={{ cursor: "pointer", fontSize: 10.5, fontWeight: 700, padding: "1px 8px", border: "1px solid " + C.ink, background: c.yScale === s ? C.sel : C.paneAlt }}>{s}</span>
          ))}
        </div>
      </AppBody>
    </>
  );
}

function ChartApp({ leafId, docId }) {
  const ui = useUI(); const w = ui.world;
  const d = w.doc(docId); const c = d.chart;
  const nOn = c.steps.filter((s) => s.on).length;
  return (
    <>
      <DocBar docId={d.id} leafId={leafId} />
      <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap", padding: "6px 8px 4px", flexShrink: 0 }}>
        <DatasetChip id={c.datasetId} docId={d.id} />
        <span style={{ color: C.faint, fontSize: 10 }}>⊳ {nOn} step{nOn === 1 ? "" : "s"} ⊳ geom_{c.geom}</span>
        <span style={{ flex: 1 }} />
        <Btn tone={C.mustard} onClick={() => w.snapshot(d.id)}>⚑ snapshot</Btn>
      </div>
      <AppBody style={{ paddingTop: 2 }}>
        <Hint>marks are &lt;datum&gt; presentations · legend swatches are &lt;cat&gt; — R-click either to filter this chart.</Hint>
        <PlotSVG chart={c} W={520} H={280} docId={d.id} />
      </AppBody>
    </>
  );
}

/* SPEC STRIP — the whole composition as one live sentence */
function SpecApp({ leafId, docId }) {
  const ui = useUI(); const w = ui.world;
  const d = w.doc(docId); const c = d.chart;
  const [src, setSrc] = useState(false);
  const schema = schemaAfter(c.datasetId, c.steps);
  const t = (n) => { const f = schema.find((x) => x.name === n); return f ? f.type : null; };
  return (
    <>
      <DocBar docId={d.id} leafId={leafId} />
      <AppBody>
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 5 }}>
          <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.08em", color: C.faint }}>THE WHOLE CHART, AS ONE SENTENCE</span>
          <span style={{ flex: 1 }} />
          <TBtn doc="show the same spec as tidyverse + ggplot2 source" onClick={() => setSrc(!src)}>{src ? "as objects" : "as ggplot"}</TBtn>
        </div>
        {src ? (
          <pre style={{ margin: 0, fontSize: 10.5, lineHeight: 1.5, background: C.paneAlt, border: "1px solid " + C.line, padding: 8, whiteSpace: "pre-wrap" }}>{asGgplot(c)}</pre>
        ) : (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 5, alignItems: "center", lineHeight: 2 }}>
            <DatasetChip id={c.datasetId} docId={d.id} />
            {c.steps.map((s) => (
              <React.Fragment key={s.id}>
                <span style={{ color: C.faint }}>⊳</span>
                <P ptype="step" value={s.id} doc={"step " + stepLabel(s) + " — R: move / toggle / remove"}>
                  <span style={{ border: "1px solid " + C.ink, borderLeft: "4px solid " + C.lavender, background: s.on ? C.pane : C.paneAlt, opacity: s.on ? 1 : 0.5, padding: "0 5px", fontSize: 10 }}>{stepLabel(s)}</span>
                </P>
              </React.Fragment>
            ))}
            <span style={{ color: C.faint }}>│</span>
            {SLOTS.filter((s) => c.mapping[s]).map((s) => (
              <span key={s} style={{ display: "inline-flex", alignItems: "center", gap: 3, fontSize: 10.5 }}>
                <span style={{ color: C.faint }}>{s}↦</span><FieldChip name={c.mapping[s]} type={t(c.mapping[s])} />
              </span>
            ))}
            <span style={{ color: C.faint }}>│</span>
            <P ptype="geom" value={c.geom} doc={"geom_" + c.geom + " — R: use another geometry, inspect its type requirements"}>
              <span style={{ border: "1px solid " + C.ink, background: C.sel, fontWeight: 700, padding: "0 6px", fontSize: 10.5 }}>geom_{c.geom}</span>
            </P>
            <span style={{ color: C.faint, fontSize: 10 }}>│ y: {c.yScale}</span>
          </div>
        )}
      </AppBody>
    </>
  );
}

function GalleryApp() {
  const w = useUI().world;
  return (
    <>
      <div style={{ display: "flex", gap: 6, alignItems: "center", padding: "6px 8px 4px", flexShrink: 0 }}>
        <Btn tone={C.mustard} onClick={() => w.snapshot()}>⚑ snapshot active chart</Btn>
        <DocChip id={w.activeId} />
      </div>
      <AppBody style={{ paddingTop: 2 }}>
        <Hint>a snapshot freezes a whole pipeline + encoding as a frozen &lt;chart&gt; object. L-click a name → restore into the ACTIVE document. R-click → restore as NEW, pin to compare A/B, inspect, delete.</Hint>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {w.snaps.map((s) => (
            <div key={s.id} style={{ border: "1px solid " + C.ink, padding: 5, background: C.pane }}>
              <div style={{ display: "flex", gap: 5, alignItems: "center", marginBottom: 3 }}>
                <P ptype="chart" value={s.id} onActivate={() => w.restoreSnap(s.id)} activateDoc={"restore into the ACTIVE document (" + w.active().name + ")"}
                  doc={"chart snapshot " + s.name + " (" + s.chart.datasetId + " · geom_" + s.chart.geom + ") — R: restore as new / pin / delete"}>
                  <b style={{ fontSize: 11, borderBottom: "1px dotted " + C.faint, cursor: "pointer" }}>{s.name}</b>
                </P>
                <span style={{ color: C.faint, fontSize: 9 }}>{s.at}</span>
                <span onClick={() => w.deleteSnap(s.id)} style={{ cursor: "pointer", color: C.red, fontWeight: 700 }} title="delete">×</span>
              </div>
              <MiniPlot chart={s.chart} W={180} H={106} />
              <div style={{ fontSize: 9, color: C.faint, marginTop: 2 }}>
                {s.chart.datasetId} ⊳ {s.chart.steps.filter((x) => x.on).length} steps · {s.chart.mapping.x}×{s.chart.mapping.y}
                {w.pins[0] === s.id && <b style={{ color: C.red }}> · pinned A</b>}{w.pins[1] === s.id && <b style={{ color: C.blue }}> · pinned B</b>}
              </div>
            </div>
          ))}
          {w.snaps.length === 0 && <div style={{ color: C.faint, fontSize: 11 }}>No snapshots yet. Press ⚑ above to freeze the active chart.</div>}
        </div>
      </AppBody>
    </>
  );
}

function CompareApp() {
  const ui = useUI(); const w = ui.world;
  const pick = async (slot) => {
    const r = await ui.accept("chart", "COMPARE " + (slot === 0 ? "A" : "B") + " — click a CHART snapshot name in the snapshots tile");
    if (r) w.pinSnap(slot, r.value);
  };
  const cell = (slot) => {
    const s = w.snaps.find((x) => x.id === w.pins[slot]);
    return (
      <div style={{ flex: 1, minWidth: 190, border: "1px dashed " + C.line, padding: 6 }}>
        <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 4 }}>
          <b style={{ fontSize: 11, color: slot === 0 ? C.red : C.blue }}>{slot === 0 ? "A" : "B"}</b>
          {s ? (
            <P ptype="chart" value={s.id} onActivate={() => w.restoreSnap(s.id)} activateDoc="restore live">
              <span style={{ fontSize: 11, borderBottom: "1px dotted " + C.faint, cursor: "pointer" }}>{s.name}</span>
            </P>
          ) : <span style={{ color: C.faint, fontSize: 10.5 }}>empty</span>}
          <span style={{ flex: 1 }} />
          <Btn tone={C.paneAlt} onClick={() => pick(slot)}>accept…</Btn>
        </div>
        {s && <MiniPlot chart={s.chart} W={230} H={136} />}
        {s && <div style={{ fontSize: 9.5, color: C.faint, marginTop: 3 }}>
          {s.chart.datasetId} ⊳ {s.chart.steps.filter((x) => x.on).map(stepLabel).join(" ⊳ ") || "(no steps)"}<br />
          geom_{s.chart.geom} · x↦{s.chart.mapping.x} y↦{s.chart.mapping.y}
        </div>}
      </div>
    );
  };
  return (
    <AppBody>
      <Hint>side-by-side A/B of two frozen specs. "accept…" then click any &lt;chart&gt; name — in the snapshots tile, the watchlist, anywhere.</Hint>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>{cell(0)}{cell(1)}</div>
    </AppBody>
  );
}

function InspectorApp() {
  const w = useUI().world;
  return (
    <AppBody>
      <div style={{ fontWeight: 700, marginBottom: 4, borderBottom: "1px dashed " + C.line, fontSize: 11 }}>{w.inspected.title}</div>
      <pre style={{ margin: 0, fontSize: 10.5, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{JSON.stringify(w.inspected.value, null, 2)}</pre>
    </AppBody>
  );
}

function WatchlistApp() {
  const ui = useUI(); const w = ui.world;
  return (
    <AppBody>
      <div style={{ marginBottom: 6 }}>
        <Btn tone={C.mustard} onClick={async () => {
          const r = await ui.accept(["field", "dataset", "chart", "doc", "step", "datum", "cat"], "Click any field, dataset, chart, snapshot, step, datum or category — in any tile — to watch it");
          if (r) w.watchAdd(r.ptype, r.value);
        }}>Watch… (accept anything)</Btn>
      </div>
      <Hint>watched objects stay LIVE — a watched field can still be mapped or inspected from here; a watched snapshot can be restored.</Hint>
      {w.watch.map((n) => (
        <div key={n.id} style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 4 }}>
          <span style={{ color: C.faint, fontSize: 9.5 }}>&lt;{n.ptype}&gt;</span>
          <Pres ptype={n.ptype} value={n.value} />
          <span onClick={() => w.watchRemove(n.id)} style={{ cursor: "pointer", color: C.red, fontWeight: 700, marginLeft: "auto" }} title="remove">×</span>
        </div>
      ))}
      {w.watch.length === 0 && <div style={{ color: C.faint, fontSize: 11 }}>Nothing watched yet. Press the button, then click any object on screen.</div>}
    </AppBody>
  );
}

const EV_COLOR = {
  source_set: C.sage, step_added: C.blue, step_removed: C.rose, step_toggled: C.blue, step_moved: C.blue,
  encoded: C.mustard, geom_set: C.mustard, scale_set: C.mustard,
  snapshotted: C.mint, restored: C.mint, snap_deleted: C.rose, pinned: C.lavender,
  watched: C.sage, watch_removed: C.rose, inspected: C.paneAlt, accepted: C.mustard,
  split_tile: C.lavender, close_tile: C.lavender, swap_tiles: C.lavender, move_split: C.lavender, app_changed: C.lavender,
  workspace_added: C.mint, workspace_removed: C.rose, workspace_renamed: C.mint, workspace_cloned: C.mint,
  doc_added: C.red, doc_removed: C.rose, doc_renamed: C.red, doc_activated: C.red, doc_duplicated: C.red,
};
function TraceApp() {
  const w = useUI().world; const endRef = useRef(null);
  useEffect(() => { endRef.current && endRef.current.scrollIntoView({ block: "nearest" }); }, [w.trace.length]);
  return (
    <AppBody>
      {w.trace.map((e) => (
        <div key={e.seq} style={{ display: "flex", gap: 6, alignItems: "baseline", marginBottom: 1 }}>
          <span style={{ color: C.faint, fontSize: 10, width: 26, textAlign: "right", flexShrink: 0 }}>{e.seq}</span>
          <span style={{ background: EV_COLOR[e.type] || C.paneAlt, border: "1px solid " + C.ink, padding: "0 4px", fontSize: 9.5, fontWeight: 700 }}>{e.type}</span>
          <span style={{ fontSize: 10.5, wordBreak: "break-word" }}>
            {Object.entries(e.data).filter(([k]) => k !== "note" && k !== "kind").map(([k, v]) => <span key={k}>{k}={String(v)} </span>)}
            {e.data.note && <span style={{ color: C.faint }}>· {e.data.note}</span>}
          </span>
        </div>
      ))}
      {w.trace.length === 0 && <div style={{ color: C.faint, fontSize: 11 }}>Nothing yet. Map a field, add a step — every verb lands here.</div>}
      <div ref={endRef} />
    </AppBody>
  );
}

function ChartsApp() {
  const w = useUI().world;
  return (
    <>
      <div style={{ display: "flex", gap: 6, alignItems: "center", padding: "6px 8px 4px", flexShrink: 0, flexWrap: "wrap" }}>
        {Object.keys(DATASETS).map((ds) => (
          <Btn key={ds} tone={C.mint} onClick={() => w.newDoc(ds)}>＋ chart from {ds}</Btn>
        ))}
      </div>
      <AppBody style={{ paddingTop: 2 }}>
        <Hint>every card is a LIVE chart document with its own pipeline and encoding. the <b style={{ color: C.red }}>red-edged</b> one is ACTIVE: object-menu verbs act on it.</Hint>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {w.docs.map((d) => (
            <div key={d.id} style={{ border: (w.activeId === d.id ? "2px solid " + C.red : "1px solid " + C.ink), padding: 6, background: C.pane }}>
              <div style={{ display: "flex", gap: 5, alignItems: "center", marginBottom: 4 }}>
                <DocChip id={d.id} big />
                <input value={d.name} onChange={(e) => w.renameDoc(d.id, e.target.value)} title="rename this chart document"
                  style={{ border: "1px solid " + C.line, background: C.pane, fontFamily: "inherit", fontSize: 10.5, padding: "0 3px", width: 54 }} />
              </div>
              <MiniPlot chart={d.chart} W={180} H={106} />
              <div style={{ fontSize: 9, color: C.faint, margin: "3px 0" }}>
                {d.chart.datasetId} ⊳ {d.chart.steps.filter((s) => s.on).length} steps ⊳ geom_{d.chart.geom}
              </div>
              <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                {w.activeId !== d.id && <TBtn doc="make it the ACTIVE chart" onClick={() => w.setActive(d.id)}>set active</TBtn>}
                <TBtn doc="duplicate this document" onClick={() => w.dupDoc(d.id)}>⧉ dup</TBtn>
                <TBtn doc="freeze its spec as a snapshot" onClick={() => w.snapshot(d.id)}>⚑ snap</TBtn>
                <TBtn doc={w.docs.length < 2 ? "the last document cannot be deleted" : "delete this document"} disabled={w.docs.length < 2} onClick={() => w.deleteDoc(d.id)}>✕</TBtn>
              </div>
            </div>
          ))}
        </div>
      </AppBody>
    </>
  );
}

function LauncherApp({ leafId }) {
  const ui = useUI();
  return (
    <AppBody>
      <Hint>Empty tile. Pick an application — chart / table / pipeline / encoding / spec bind to a chart DOCUMENT; the rest are one shared thing over the whole world.</Hint>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
        {Object.entries(APPS).filter(([id]) => id !== "launcher").map(([id, a]) => (
          <Btn key={id} tone={a.color} onClick={() => ui.wm.setLeafApp(leafId, id)}>{a.title}</Btn>
        ))}
      </div>
    </AppBody>
  );
}

const APPS = {
  launcher: { title: "new tile", color: C.paneAlt, comp: LauncherApp },
  data: { title: "data browser", color: C.sage, comp: DataApp },
  charts: { title: "charts", color: C.rose, comp: ChartsApp },
  pipeline: { title: "pipeline", color: C.blue, comp: PipelineApp },
  encode: { title: "encoding", color: C.mustard, comp: EncodeApp },
  chart: { title: "chart", color: C.rose, comp: ChartApp },
  table: { title: "table", color: C.mint, comp: TableApp },
  spec: { title: "spec", color: C.sel, comp: SpecApp },
  gallery: { title: "snapshots", color: C.lavender, comp: GalleryApp },
  compare: { title: "compare a/b", color: C.rose, comp: CompareApp },
  watch: { title: "watchlist", color: C.mustard, comp: WatchlistApp },
  inspector: { title: "inspector", color: C.lavender, comp: InspectorApp },
  trace: { title: "trace", color: C.sage, comp: TraceApp },
};

/* ============================================================
   WORKBENCH — the whole shell, embeddable.
   Every section of the landing page mounts one of these with
   its own World. They share no state whatsoever.
   ============================================================ */
function Workbench({ world, buildSpaces, height, probeRef, showTrace }) {
  const [, force] = useState(0);
  const bump = useCallback(() => force((x) => x + 1), []);
  useEffect(() => world.sub(bump), [world, bump]);

  const [spaces, setSpaces] = useState(() => buildSpaces(world));
  const [cur, setCur] = useState(() => spaces[0].id);
  const [renaming, setRenaming] = useState(null);
  const [menu, setMenu] = useState(null);
  const [accepting, setAccepting] = useState(null);
  const [mouseDoc, setMouseDoc] = useState(null);
  const [drag, setDrag] = useState(null);
  const dragRef = useRef(null); dragRef.current = drag;
  const leafRefs = useRef({});
  const rootRef = useRef(null);

  const space = spaces.find((s) => s.id === cur) || spaces[0];
  const tree = space.tree;

  const mutateTree = (fn) => setSpaces((ss) => ss.map((s) => (s.id === space.id ? { ...s, tree: fn(s.tree) } : s)));
  const setRatio = (id, r) => mutateTree((t) => updateNode(t, id, (n) => ({ ...n, ratio: r })));
  const splitLeaf = (id, dir) => { mutateTree((t) => updateNode(t, id, (n) => split(dir, n, leaf("launcher"), 0.5))); world.log("split_tile", { dir: dir === "row" ? "⬌" : "⬍" }); };
  const closeLeaf = (id) => { mutateTree((t) => removeLeaf(t, id)); world.log("close_tile", { note: "the document it showed is untouched" }); };
  const setLeafApp = (id, app) => { mutateTree((t) => updateNode(t, id, (n) => ({ ...n, app, doc: DOC_APPS.includes(app) ? (n.doc || world.activeId) : n.doc }))); world.log("app_changed", { app: APPS[app].title }); };
  const setLeafDoc = (id, docId) => { mutateTree((t) => updateNode(t, id, (n) => ({ ...n, doc: docId }))); world.log("tile_repointed", { chart: (world.doc(docId) || {}).name }); };
  const swapTiles = (a, b) => {
    mutateTree((t) => { const la = findLeaf(t, a), lb = findLeaf(t, b); if (!la || !lb) return t; return updateNode(updateNode(t, a, (n) => ({ ...n, app: lb.app, doc: lb.doc })), b, (n) => ({ ...n, app: la.app, doc: la.doc })); });
    world.log("swap_tiles", { note: "apps traded places; their state lives in the world, not the tile" });
  };
  const moveSplit = (fromId, targetId, zone) => {
    mutateTree((t) => {
      if (fromId === targetId) return t;
      const src = findLeaf(t, fromId); if (!src || !findLeaf(t, targetId)) return t;
      const t2 = removeLeaf(t, fromId); if (findLeaf(t2, fromId)) return t;
      const dir = zone === "left" || zone === "right" ? "row" : "col";
      const before = zone === "left" || zone === "top";
      return updateNode(t2, targetId, (n) => (before ? split(dir, src, n) : split(dir, n, src)));
    });
    world.log("move_split", { zone });
  };

  const registerRef = useCallback((id, el) => { if (el) leafRefs.current[id] = el; else delete leafRefs.current[id]; }, []);
  const zoneFor = (r, x, y) => {
    const dl = x - r.left, dr = r.right - x, dt = y - r.top, db = r.bottom - y;
    const band = Math.min(Math.min(r.width, r.height) * 0.3, 110);
    const m = Math.min(dl, dr, dt, db);
    if (m > band) return "center"; if (m === dl) return "left"; if (m === dr) return "right"; if (m === dt) return "top"; return "bottom";
  };
  const hitLeaf = (x, y) => {
    for (const [id, el] of Object.entries(leafRefs.current)) {
      if (!el || !el.isConnected) continue;
      const r = el.getBoundingClientRect();
      if (x >= r.left && x <= r.right && y >= r.top && y <= r.bottom) return { id, zone: zoneFor(r, x, y) };
    }
    return null;
  };
  const startDrag = (leafId, e) => { e.preventDefault(); document.body.style.userSelect = "none"; setDrag({ from: leafId, x: e.clientX, y: e.clientY, over: null, zone: null }); };
  useEffect(() => {
    if (!drag) return;
    const move = (e) => setDrag((d) => { if (!d) return d; const h = hitLeaf(e.clientX, e.clientY); return { ...d, x: e.clientX, y: e.clientY, over: h && h.id, zone: h && h.zone }; });
    const up = () => { const d = dragRef.current; document.body.style.userSelect = ""; if (d && d.over && d.over !== d.from) { if (d.zone === "center") swapTiles(d.from, d.over); else moveSplit(d.from, d.over, d.zone); } setDrag(null); };
    window.addEventListener("mousemove", move); window.addEventListener("mouseup", up);
    return () => { window.removeEventListener("mousemove", move); window.removeEventListener("mouseup", up); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [!!drag]);

  const addSpace = () => { const s = { id: nid(), name: "ws-" + (spaces.length + 1), tree: leaf("launcher") }; setSpaces((ss) => [...ss, s]); setCur(s.id); world.log("workspace_added", { name: s.name }); };
  const removeSpace = (id) => { if (spaces.length < 2) return; setSpaces((ss) => ss.filter((s) => s.id !== id)); if (cur === id) setCur(spaces.find((s) => s.id !== id).id); world.log("workspace_removed", {}); };
  const cloneSpace = (id) => { const s = spaces.find((x) => x.id === id); if (!s) return; const c2 = { id: nid(), name: s.name + "′", tree: cloneTree(s.tree) }; setSpaces((ss) => [...ss, c2]); setCur(c2.id); world.log("workspace_cloned", { from: s.name }); };

  const accept = (ptype, prompt) => new Promise((resolve) => setAccepting({ ptype, prompt, resolve: (r) => { if (r) world.log("accepted", { ptype: r.ptype, value: labelFor(r.ptype, r.value) }); resolve(r); } }));
  useEffect(() => {
    if (!accepting && !menu) return;
    const esc = (e) => { if (e.key === "Escape") { setMenu(null); if (accepting) { accepting.resolve(null); setAccepting(null); } } };
    window.addEventListener("keydown", esc);
    return () => window.removeEventListener("keydown", esc);
  }, [accepting, menu]);

  const labelFor = (ptype, value) => {
    if (ptype === "field") return String(value);
    if (ptype === "dataset") return DATASETS[value] ? DATASETS[value].name : "?";
    if (ptype === "doc") { const d = world.docs.find((x) => x.id === value); return d ? d.name : "(deleted chart)"; }
    if (ptype === "step") { const s = world.docs.flatMap((d) => d.chart.steps).find((x) => x.id === value); return s ? stepLabel(s) : "(removed step)"; }
    if (ptype === "geom") return "geom_" + value;
    if (ptype === "datum") { const r = value && value.row ? value.row : value || {}; const ks = Object.keys(r); return ks.slice(0, 2).map((k) => k + "=" + fmt(r[k])).join(" "); }
    if (ptype === "cat") return value ? value.field + "=" + value.value : "?";
    if (ptype === "chart") { const s = world.snaps.find((x) => x.id === value); return s ? s.name : "(deleted snapshot)"; }
    if (ptype === "tile") { const l = findLeaf(tree, value); return l ? "[" + APPS[l.app].title + "]" : "(closed tile)"; }
    if (ptype === "workspace") { const s = spaces.find((x) => x.id === value); return s ? s.name : "?"; }
    return String(value);
  };
  const describe = (ptype, value) => {
    if (ptype === "dataset") return describeDataset(value);
    if (ptype === "field") {
      const a = world.active();
      const stats = fieldStats(a.chart.datasetId, a.chart.steps, value);
      const inSrc = Object.values(DATASETS).filter((d) => d.fields.some((f) => f.name === value)).map((d) => d.id);
      return { presentationType: "field", name: value, in_datasets: inSrc, ["stats_in_chart_" + a.name]: stats || "(not in that chart's output)" };
    }
    if (ptype === "doc") { const d = world.docs.find((x) => x.id === value); return d ? { presentationType: "chart document", name: d.name, active: world.activeId === d.id, spec: d.chart } : null; }
    if (ptype === "step") { const sd = world.docOfStep(value); const s = sd && sd.chart.steps.find((x) => x.id === value); return s ? { presentationType: "step", in_chart: sd.name, enabled: s.on, ...s } : { presentationType: "step", note: "removed" }; }
    if (ptype === "geom") return { presentationType: "geom", geom: value, needs: value === "bar" ? "nominal or temporal x + quantitative y" : "x + quantitative y" };
    if (ptype === "datum") { const r = value && value.row ? value.row : value; const dc = value && value.docId ? world.doc(value.docId) : null; return { presentationType: "datum", from_chart: dc ? dc.name : "(active)", ...r }; }
    if (ptype === "cat") { const dc = value && value.docId ? world.doc(value.docId) : null; return { presentationType: "category", field: value.field, value: value.value, chart: dc ? dc.name : world.active().name }; }
    if (ptype === "chart") { const s = world.snaps.find((x) => x.id === value); return s ? { presentationType: "chart", name: s.name, at: s.at, spec: s.chart } : null; }
    if (ptype === "tile") { const l = findLeaf(tree, value); return { presentationType: "tile", app: l ? APPS[l.app].title : "(closed)", workspace: space.name }; }
    if (ptype === "workspace") { const s = spaces.find((x) => x.id === value); return { presentationType: "workspace", name: s && s.name, tiles: s && countLeaves(s.tree) }; }
    return { presentationType: ptype, value: String(value) };
  };

  const actionsFor = (ptype, value) => {
    const acts = [{ label: "Inspect", run: () => world.inspect("<" + ptype + "> " + labelFor(ptype, value), describe(ptype, value)) }];
    const act = world.active();
    const schema = schemaAfter(act.chart.datasetId, act.chart.steps);
    if (ptype === "dataset") {
      acts.push({ label: "Use as source of chart " + act.name, run: () => world.setDataset(null, value) });
      acts.push({ label: "New chart document from it", run: () => world.newDoc(value) });
      acts.push({ label: "Add to watchlist", run: () => world.watchAdd("dataset", value) });
    }
    if (ptype === "field") {
      const f = schema.find((x) => x.name === value);
      SLOTS.forEach((slot) => acts.push({ label: "Map to " + slot + "  (chart " + act.name + ")", run: () => world.setMapping(null, slot, value) }));
      acts.push({ label: "Filter on this field", run: () => world.addStep(null, mkStep("filter", { field: value, op: f && f.type === "q" ? ">" : "=", value: "" })) });
      if (f && f.type !== "q") acts.push({ label: "Group by + count", run: () => world.addStep(null, mkStep("summarize", { by: value, fn: "count", field: value })) });
      acts.push({ label: "Sort output by (desc)", run: () => world.addStep(null, mkStep("sort", { field: value, dir: "desc" })) });
      acts.push({ label: "Add to watchlist", run: () => world.watchAdd("field", value) });
    }
    if (ptype === "doc") {
      const d = world.docs.find((x) => x.id === value);
      if (d) {
        if (world.activeId !== d.id) acts.push({ label: "Make ACTIVE chart", run: () => world.setActive(d.id) });
        acts.push({ label: "⚑ Snapshot it", run: () => world.snapshot(d.id) });
        acts.push({ label: "Duplicate document", run: () => world.dupDoc(d.id) });
        if (world.docs.length > 1) acts.push({ label: "Delete document", run: () => world.deleteDoc(d.id) });
        acts.push({ label: "Add to watchlist", run: () => world.watchAdd("doc", d.id) });
      }
    }
    if (ptype === "step") {
      const sd = world.docOfStep(value);
      const s = sd && sd.chart.steps.find((x) => x.id === value);
      if (s) {
        acts.push({ label: s.on ? "Disable (keep in chain)" : "Enable", run: () => world.toggleStep(sd.id, value) });
        acts.push({ label: "Move up ↑", run: () => world.moveStep(sd.id, value, -1) });
        acts.push({ label: "Move down ↓", run: () => world.moveStep(sd.id, value, 1) });
        acts.push({ label: "Remove", run: () => world.removeStep(sd.id, value) });
      }
    }
    if (ptype === "geom") acts.push({ label: "Use this geom  (chart " + act.name + ")", run: () => world.setGeom(null, value) });
    if (ptype === "datum") {
      const dd = world.doc(value && value.docId ? value.docId : null);
      const row = value && value.row ? value.row : value || {};
      const dSchema = schemaAfter(dd.chart.datasetId, dd.chart.steps);
      Object.keys(row).filter((k) => { const f = dSchema.find((x) => x.name === k); return f && f.type !== "q"; }).slice(0, 3).forEach((k) => {
        acts.push({ label: "Keep only " + k + " = " + row[k] + "  (chart " + dd.name + ")", run: () => world.filterToCat(dd.id, k, row[k], true) });
        acts.push({ label: "Exclude " + k + " = " + row[k], run: () => world.filterToCat(dd.id, k, row[k], false) });
      });
      acts.push({ label: "Add to watchlist", run: () => world.watchAdd("datum", value) });
    }
    if (ptype === "cat") {
      const dd = world.doc(value && value.docId ? value.docId : null);
      acts.push({ label: "Keep only " + value.field + " = " + value.value + "  (chart " + dd.name + ")", run: () => world.filterToCat(dd.id, value.field, value.value, true) });
      acts.push({ label: "Exclude " + value.field + " = " + value.value, run: () => world.filterToCat(dd.id, value.field, value.value, false) });
      acts.push({ label: "Facet by " + value.field, run: () => world.setMapping(dd.id, "facet", value.field) });
      acts.push({ label: "Add to watchlist", run: () => world.watchAdd("cat", value) });
    }
    if (ptype === "chart") {
      acts.push({ label: "Restore into ACTIVE document (" + act.name + ")", run: () => world.restoreSnap(value) });
      acts.push({ label: "Restore as NEW document", run: () => world.restoreAsNew(value) });
      acts.push({ label: "Pin as compare A", run: () => world.pinSnap(0, value) });
      acts.push({ label: "Pin as compare B", run: () => world.pinSnap(1, value) });
      acts.push({ label: "Delete snapshot", run: () => world.deleteSnap(value) });
    }
    if (ptype === "tile") {
      acts.push({ label: "Split ⬌ (new tile right)", run: () => splitLeaf(value, "row") });
      acts.push({ label: "Split ⬍ (new tile below)", run: () => splitLeaf(value, "col") });
      acts.push({ label: "Swap app with…  (accept a tile)", run: async () => { const r = await accept("tile", "SWAP — click another TILE's title"); if (r && r.value !== value) swapTiles(value, r.value); } });
      if (tree.type !== "leaf") acts.push({ label: "Close tile", run: () => closeLeaf(value) });
    }
    if (ptype === "workspace") {
      acts.push({ label: "Switch to", run: () => setCur(value) });
      acts.push({ label: "Rename", run: () => setRenaming(value) });
      acts.push({ label: "Duplicate", run: () => cloneSpace(value) });
      if (spaces.length > 1) acts.push({ label: "Delete", run: () => removeSpace(value) });
    }
    return acts;
  };

  const ui = {
    world, accepting, setAccepting, setMouseDoc, accept, labelFor, describe, drag, spaces,
    goSpace: (name) => { const s = spaces.find((x) => x.name === name); if (s) setCur(s.id); },
    openMenu: (ptype, value, x, y) => setMenu({ ptype, value, x, y }),
    wm: { setRatio, splitLeaf, closeLeaf, setLeafApp, setLeafDoc, startDrag, registerRef, canClose: tree.type !== "leaf" },
  };

  /* published to the lesson rail — written during render so the rail's
     effect (which runs after ours) always sees the current layout */
  if (probeRef) {
    probeRef.current = {
      spaces, cur, tree, leaves: allLeaves(tree), nLeaves: countLeaves(tree),
      docsShown: new Set(allLeaves(tree).filter((l) => DOC_APPS.includes(l.app)).map((l) => l.doc)),
      apps: allLeaves(tree).map((l) => l.app),
      api: { accept, setLeafApp, setLeafDoc, splitLeaf, addSpace, setCur, swapTiles },
    };
  }

  const dragSrcLeaf = drag && findLeaf(tree, drag.from);
  const tail = world.trace.slice(-3).reverse();
  const nLit = accepting && rootRef.current ? rootRef.current.querySelectorAll(".pres.acceptable, .pres-svg.acceptable").length : 0;

  return (
    <UICtx.Provider value={ui}>
      <div ref={rootRef} onClick={() => setMenu(null)}
        style={{ fontFamily: MONO, background: C.paper, color: C.ink, height, display: "flex", flexDirection: "column", fontSize: 12, border: "2px solid " + C.ink, boxShadow: "4px 4px 0 " + C.ink, minWidth: 0, overflow: "hidden" }}>

        {accepting && (
          <div style={{ background: C.red, color: C.paper, padding: "3px 10px", fontWeight: 700, flexShrink: 0, fontSize: 11, display: "flex", gap: 10, alignItems: "center" }}>
            <span>ACCEPTING &lt;{Array.isArray(accepting.ptype) ? accepting.ptype.join("|") : accepting.ptype}&gt;</span>
            <span style={{ flex: 1, fontWeight: 400, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{accepting.prompt}</span>
            <span style={{ fontWeight: 400, flexShrink: 0, fontSize: 10 }}>
              {nLit > 0 ? nLit + " target" + (nLit === 1 ? "" : "s") + " here"
                : "nothing of that type on screen — try another workspace or tile"}
            </span>
            <span onClick={() => { accepting.resolve(null); setAccepting(null); }}
              style={{ cursor: "pointer", border: "1px solid " + C.paper, padding: "0 6px", fontSize: 10, flexShrink: 0 }}>Esc — cancel</span>
          </div>
        )}

        <div style={{ display: "flex", gap: 5, alignItems: "center", padding: "4px 7px", flexShrink: 0, flexWrap: "wrap", borderBottom: "1px solid " + C.line }}>
          <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.1em", color: C.faint }}>WORKSPACES</span>
          {spaces.map((s) =>
            renaming === s.id ? (
              <input key={s.id} autoFocus defaultValue={s.name}
                onKeyDown={(e) => { if (e.key === "Enter") { const name = e.target.value.trim() || s.name; setSpaces((ss) => ss.map((x) => (x.id === s.id ? { ...x, name } : x))); world.log("workspace_renamed", { name }); setRenaming(null); } }}
                onBlur={() => setRenaming(null)}
                style={{ border: "2px solid " + C.ink, background: C.pane, fontFamily: "inherit", fontSize: 11, padding: "1px 5px", width: 90 }} />
            ) : (
              <P key={s.id} ptype="workspace" value={s.id} onActivate={() => setCur(s.id)} activateDoc="switch to it" doc={"workspace " + s.name + " (" + countLeaves(s.tree) + " tiles)"}>
                <span style={{ border: "2px solid " + C.ink, background: cur === s.id ? C.sel : C.paneAlt, padding: "0 8px", fontSize: 11, fontWeight: cur === s.id ? 700 : 400, cursor: "pointer" }}>{s.name}</span>
              </P>
            ))}
          <TBtn doc="add an empty workspace — a new layout over the same world" onClick={addSpace}>+ workspace</TBtn>
        </div>

        <div style={{ flex: 1, display: "flex", padding: 6, minHeight: 0 }}><NodeView node={tree} /></div>

        {showTrace !== false && (
          <div style={{ borderTop: "1px solid " + C.line, padding: "2px 8px", flexShrink: 0, display: "flex", gap: 10, alignItems: "center", overflow: "hidden", background: C.wash }}>
            <span style={{ fontSize: 8.5, fontWeight: 700, letterSpacing: "0.1em", color: C.faint, flexShrink: 0 }}>TRACE</span>
            {tail.length === 0 && <span style={{ fontSize: 10, color: C.faint }}>every verb you fire is recorded here</span>}
            {tail.map((e) => (
              <span key={e.seq} style={{ fontSize: 9.5, whiteSpace: "nowrap", display: "inline-flex", gap: 4, alignItems: "center", opacity: 1 }}>
                <span style={{ background: EV_COLOR[e.type] || C.paneAlt, border: "1px solid " + C.ink, padding: "0 3px", fontWeight: 700 }}>{e.type}</span>
                <span style={{ color: C.faint }}>{Object.entries(e.data).filter(([k]) => k !== "note" && k !== "kind").slice(0, 2).map(([k, v]) => k + "=" + v).join(" ")}</span>
              </span>
            ))}
          </div>
        )}

        <div style={{ background: C.ink, color: C.paper, padding: "3px 9px", fontSize: 10.5, flexShrink: 0, display: "flex", gap: 12 }}>
          <span style={{ color: C.mustard, fontWeight: 700, flexShrink: 0 }}>{accepting ? "ACCEPT" : drag ? "MOVING" : "READY"}</span>
          <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {mouseDoc || (accepting ? accepting.prompt : "point at anything — this line says what it is and what a click will do")}
          </span>
          <span style={{ color: C.faint, flexShrink: 0 }}>{countLeaves(tree)} tiles</span>
        </div>

        {drag && dragSrcLeaf && (
          <div style={{ position: "fixed", left: drag.x + 12, top: drag.y + 12, zIndex: 200, pointerEvents: "none", background: APPS[dragSrcLeaf.app].color, border: "2px solid " + C.ink, boxShadow: "3px 3px 0 " + C.ink, padding: "1px 8px", fontSize: 11, fontWeight: 700 }}>
            {APPS[dragSrcLeaf.app].title} → {drag.over && drag.over !== drag.from ? (drag.zone === "center" ? "swap apps" : "dock " + ({ left: "⇤", right: "⇥", top: "⤒", bottom: "⤓" }[drag.zone] || "")) : "drop on a tile · centre swaps · edges split"}
          </div>
        )}

        {menu && (
          <div onClick={(e) => e.stopPropagation()} style={{ position: "fixed", left: Math.min(menu.x, (typeof window !== "undefined" ? window.innerWidth : 800) - 320), top: Math.min(menu.y, (typeof window !== "undefined" ? window.innerHeight : 600) - 300), zIndex: 100, background: C.pane, border: "2px solid " + C.ink, boxShadow: "4px 4px 0 " + C.ink, minWidth: 250, maxHeight: 300, overflow: "auto" }}>
            <div style={{ background: C.ink, color: C.paper, padding: "2px 8px", fontSize: 10, fontWeight: 700, letterSpacing: "0.06em" }}>
              &lt;{menu.ptype}&gt; {labelFor(menu.ptype, menu.value).slice(0, 28)}
              {["field", "dataset", "geom"].includes(menu.ptype) && <span style={{ color: C.mustard }}> → chart {world.active().name}</span>}
            </div>
            {actionsFor(menu.ptype, menu.value).map((a, i) => (
              <div key={i} onClick={() => { setMenu(null); a.run(); }}
                style={{ padding: "4px 10px", cursor: "pointer", borderTop: i ? "1px dotted " + C.line : "none", fontSize: 11.5 }}
                onMouseEnter={(e) => (e.currentTarget.style.background = C.sel)} onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                {a.label}
              </div>
            ))}
          </div>
        )}
      </div>
    </UICtx.Provider>
  );
}

/* ============================================================
   LESSON RAIL
   A step is complete when a PREDICATE over world state says so
   — not when a button was pressed. Any route counts, including
   routes this file never anticipated. Steps you performed
   yourself tick green; steps you watched "do it for me" tick
   grey, because watching is not the same as knowing.
   ============================================================ */
/* states the app can legitimately reach that leave a lesson unreachable.
   phrased as a teaching moment, never as an apology. */
function wedgeOf(world) {
  const d = world.active(); if (!d) return null;
  const c = d.chart;
  const { rows } = evaluate(c.datasetId, c.steps);
  if (c.steps.some((s) => s.on) && rows.length === 0)
    return "chart " + d.name + " has no rows left — a filter step is too strict. Switch one off with its ✓ box, or";
  const schema = schemaAfter(c.datasetId, c.steps);
  const lost = SLOTS.filter((sl) => c.mapping[sl] && !schema.some((f) => f.name === c.mapping[sl]));
  if (lost.length)
    return "chart " + d.name + " maps " + lost.join(" and ") + " to a field the pipeline no longer produces — a group∑ step changes the schema. Re-map it, or";
  return null;
}

/* one binary question per track, asked BEFORE the reveal. costs a line of
   content and converts instruction-following into model-building. */
function Predict({ spec }) {
  const [pick, setPick] = useState(null);
  return (
    <div style={{ border: "1px dashed " + C.line, background: C.paper, padding: "5px 7px", marginTop: 7 }}>
      <div style={{ fontSize: 8.5, fontWeight: 700, letterSpacing: "0.1em", color: C.faint, marginBottom: 3 }}>PREDICT — BEFORE YOU LOOK</div>
      <div style={{ fontSize: 11.5, lineHeight: 1.45, marginBottom: 5 }}>{spec.q}</div>
      <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
        {spec.options.map((o, i) => (
          <span key={i} onClick={() => pick == null && setPick(i)}
            style={{
              cursor: pick == null ? "pointer" : "default", border: "1px solid " + C.ink, padding: "0 7px", fontSize: 10.5,
              background: pick == null ? C.paneAlt : i === spec.answer ? C.mint : i === pick ? C.paneAlt : C.pane,
              fontWeight: pick != null && i === spec.answer ? 700 : 400,
              opacity: pick != null && i !== spec.answer && i !== pick ? 0.45 : 1,
            }}>{o}{pick != null && i === spec.answer ? " ✓" : ""}</span>
        ))}
      </div>
      {pick != null && <div style={{ fontSize: 11, lineHeight: 1.45, marginTop: 5, color: C.faint }}>{spec.reveal}</div>}
    </div>
  );
}

function Tick({ state, n }) {
  const bg = state === "self" ? C.green : state === "watched" ? C.line : C.sel;
  const fg = state === "self" ? C.paper : C.ink;
  return (
    <span style={{
      flexShrink: 0, width: 17, height: 17, border: "1.5px solid " + C.ink, background: bg, color: fg,
      display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700,
    }}>{state ? "✓" : n}</span>
  );
}

function LessonRail({ lessons, world, probeRef, onReset, title }) {
  const [done, setDone] = useState({});
  const [open, setOpen] = useState(lessons[0].id);
  const ranRef = useRef({});
  const [, force] = useState(0);
  useEffect(() => world.sub(() => force((x) => x + 1)), [world]);

  useEffect(() => {
    setDone((d) => {
      let changed = false; const next = { ...d };
      lessons.forEach((l) => {
        if (next[l.id] || !l.done) return;
        let ok = false;
        try { ok = !!l.done(world, probeRef.current || {}); } catch (e) { ok = false; }
        if (ok) { next[l.id] = ranRef.current[l.id] ? "watched" : "self"; changed = true; }
      });
      return changed ? next : d;
    });
  });

  useEffect(() => {
    if (!done[open]) return;
    const i = lessons.findIndex((l) => l.id === open);
    const nxt = lessons.slice(i + 1).find((l) => !done[l.id]) || lessons.find((l) => !done[l.id]);
    if (nxt && nxt.id !== open) setOpen(nxt.id);
  }, [done, open, lessons]);

  const nDone = lessons.filter((l) => done[l.id]).length;
  const wedge = wedgeOf(world);

  return (
    <div style={{ border: "2px solid " + C.ink, boxShadow: "4px 4px 0 " + C.ink, background: C.pane, display: "flex", flexDirection: "column", minWidth: 0 }}>
      <div style={{ background: C.ink, color: C.paper, padding: "3px 9px", display: "flex", alignItems: "center", gap: 8, fontSize: 10, fontWeight: 700, letterSpacing: "0.1em" }}>
        <span>{title || "LESSONS"}</span>
        <span style={{ flex: 1 }} />
        <span style={{ color: C.mustard, letterSpacing: 0 }}>{nDone}/{lessons.length}</span>
        <span onClick={onReset} title="reset this workspace to how it started"
          style={{ cursor: "pointer", border: "1px solid " + C.paper, padding: "0 5px", letterSpacing: 0, fontWeight: 400 }}>↺ reset</span>
      </div>

      {wedge && (
        <div style={{ background: "#fffaf7", borderBottom: "2px solid " + C.red, padding: "5px 9px", fontSize: 11, lineHeight: 1.45 }}>
          <b style={{ color: C.red }}>The panel is stuck: </b>{wedge}{" "}
          <span onClick={onReset} style={{ cursor: "pointer", borderBottom: "1px solid " + C.ink, fontWeight: 700 }}>↺ start this panel over</span>
        </div>
      )}

      <div style={{ overflow: "auto", flex: 1 }}>
        {lessons.map((l, i) => {
          const st = done[l.id];
          const isOpen = open === l.id;
          return (
            <div key={l.id} style={{ borderBottom: "1px dotted " + C.line, background: isOpen ? "#fffdf4" : "transparent" }}>
              <div onClick={() => setOpen(isOpen ? null : l.id)}
                style={{ display: "flex", gap: 7, alignItems: "center", padding: "5px 9px", cursor: "pointer" }}>
                <Tick state={st} n={i + 1} />
                <span style={{ fontSize: 11.5, fontWeight: isOpen ? 700 : 400, flex: 1 }}>{l.title}</span>
                {st === "watched" && <span style={{ fontSize: 8.5, color: C.faint, letterSpacing: "0.05em" }}>WATCHED</span>}
                <span style={{ color: C.faint, fontSize: 10 }}>{isOpen ? "▾" : "▸"}</span>
              </div>
              {isOpen && (
                <div style={{ padding: "0 9px 9px 33px", fontSize: 11.5, lineHeight: 1.55 }}>
                  {l.body}
                  {l.predict && <Predict spec={l.predict} />}
                  <div style={{ display: "flex", gap: 6, marginTop: 7, flexWrap: "wrap", alignItems: "center" }}>
                    {l.run && !st && (
                      <span onClick={async () => {
                        ranRef.current[l.id] = true;
                        const pr = probeRef.current || {};
                        await l.run(world, pr.api || {}, pr);
                      }}
                        style={{ cursor: "pointer", border: "1.5px solid " + C.ink, boxShadow: "2px 2px 0 " + C.ink, background: C.paneAlt, fontWeight: 700, padding: "1px 8px", fontSize: 10.5 }}>
                        ▶ do it for me
                      </span>
                    )}
                    {l.manual && !st && (
                      <span onClick={() => setDone((d) => ({ ...d, [l.id]: "self" }))}
                        style={{ cursor: "pointer", border: "1.5px solid " + C.ink, boxShadow: "2px 2px 0 " + C.ink, background: C.mint, fontWeight: 700, padding: "1px 8px", fontSize: 10.5 }}>
                        ✓ got it
                      </span>
                    )}
                    {l.run && !st && <span style={{ fontSize: 10, color: C.faint }}>— or do it yourself, and this ticks green</span>}
                    {st === "watched" && <span style={{ fontSize: 10, color: C.faint }}>you watched this one. try the same move by hand in the panel.</span>}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ============================================================
   CHECKLIST — the capstone. No lesson steps and no ▶ buttons:
   one question, and goals that tick when the world satisfies
   them, by whatever route the person found.
   ============================================================ */
function Checklist({ question, items, nudges, world, probeRef, onReset, taller, onTaller }) {
  const [done, setDone] = useState({});
  const [shown, setShown] = useState(0);
  const [, force] = useState(0);
  useEffect(() => world.sub(() => force((x) => x + 1)), [world]);
  useEffect(() => {
    setDone((d) => {
      let ch = false; const next = { ...d };
      items.forEach((it) => {
        if (next[it.id]) return;
        let ok = false;
        try { ok = !!it.done(world, probeRef.current || {}); } catch (e) { ok = false; }
        if (ok) { next[it.id] = true; ch = true; }
      });
      return ch ? next : d;
    });
  });
  const n = items.filter((i) => done[i.id]).length;
  const wedge = wedgeOf(world);
  return (
    <div style={{ border: "2px solid " + C.ink, boxShadow: "4px 4px 0 " + C.ink, background: C.pane, display: "flex", flexDirection: "column", minWidth: 0 }}>
      <div style={{ background: C.ink, color: C.paper, padding: "3px 9px", display: "flex", alignItems: "center", gap: 8, fontSize: 10, fontWeight: 700, letterSpacing: "0.1em" }}>
        <span>THE BRIEF</span>
        <span style={{ flex: 1 }} />
        <span style={{ color: n === items.length ? C.mint : C.mustard, letterSpacing: 0 }}>{n}/{items.length}</span>
        <span onClick={onReset} style={{ cursor: "pointer", border: "1px solid " + C.paper, padding: "0 5px", letterSpacing: 0, fontWeight: 400 }}>↺ reset</span>
      </div>
      <div style={{ padding: "9px", borderBottom: "1px dotted " + C.line, fontSize: 12.5, lineHeight: 1.55 }}>{question}</div>
      {wedge && (
        <div style={{ background: "#fffaf7", borderBottom: "2px solid " + C.red, padding: "5px 9px", fontSize: 11, lineHeight: 1.45 }}>
          <b style={{ color: C.red }}>Stuck: </b>{wedge}{" "}
          <span onClick={onReset} style={{ cursor: "pointer", borderBottom: "1px solid " + C.ink, fontWeight: 700 }}>↺ start over</span>
        </div>
      )}
      <div style={{ padding: "8px 9px", flex: 1, overflow: "auto" }}>
        {items.map((it) => (
          <div key={it.id} style={{ display: "flex", gap: 8, alignItems: "flex-start", marginBottom: 6 }}>
            <span style={{
              flexShrink: 0, width: 15, height: 15, marginTop: 1, border: "1.5px solid " + C.ink,
              background: done[it.id] ? C.green : C.pane, color: C.paper,
              display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 9.5, fontWeight: 700,
            }}>{done[it.id] ? "✓" : ""}</span>
            <span style={{ fontSize: 11.5, lineHeight: 1.45, opacity: done[it.id] ? 0.55 : 1 }}>{it.label}</span>
          </div>
        ))}
        {n === items.length && (
          <div style={{ marginTop: 8, border: "2px solid " + C.ink, background: C.sel, padding: "6px 8px", fontSize: 11.5, lineHeight: 1.5 }}>
            <b>That is the whole system.</b> Live objects, typed verbs, one shared world, any number of
            compositions over it. Nothing above was a special tutorial mode — this panel is the application.
          </div>
        )}
        <div style={{ marginTop: 10, borderTop: "1px dotted " + C.line, paddingTop: 7 }}>
          {nudges.slice(0, shown).map((h, i) => (
            <div key={i} style={{ fontSize: 11, lineHeight: 1.45, color: C.faint, marginBottom: 4 }}>· {h}</div>
          ))}
          {shown < nudges.length ? (
            <span onClick={() => setShown(shown + 1)}
              style={{ cursor: "pointer", border: "1.5px solid " + C.ink, boxShadow: "2px 2px 0 " + C.ink, background: C.paneAlt, fontWeight: 700, padding: "1px 8px", fontSize: 10.5 }}>
              I'm stuck — one hint
            </span>
          ) : <span style={{ fontSize: 10, color: C.faint }}>that is every hint. the rest is yours.</span>}
          <span onClick={onTaller} style={{ marginLeft: 8, cursor: "pointer", border: "1px solid " + C.ink, background: C.pane, padding: "1px 7px", fontSize: 10.5 }}>
            {taller ? "⤡ shrink panel" : "⤢ more room"}
          </span>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   MODULE RACK — §D. Not lessons: a reference with a live
   specimen. Picking a module swaps the big tile to it.
   ============================================================ */
function ModuleRack({ modules, probeRef, focusRef, world }) {
  const [sel, setSel] = useState(modules[0].id);
  const [, force] = useState(0);
  useEffect(() => world.sub(() => force((x) => x + 1)), [world]);
  const m = modules.find((x) => x.id === sel) || modules[0];
  const show = (id) => {
    setSel(id);
    const api = (probeRef.current || {}).api;
    if (api && focusRef.current) api.setLeafApp(focusRef.current, id);
  };
  const Row = ({ k, v }) => (
    <div style={{ display: "flex", gap: 8, marginBottom: 3 }}>
      <span style={{ flexShrink: 0, width: 62, fontSize: 8.5, fontWeight: 700, letterSpacing: "0.08em", color: C.faint, paddingTop: 2 }}>{k}</span>
      <span style={{ fontSize: 11, lineHeight: 1.45 }}>{v}</span>
    </div>
  );
  const group = (kind) => modules.filter((x) => x.kind === kind);
  const chip = (x) => (
    <span key={x.id} onClick={() => show(x.id)}
      style={{
        cursor: "pointer", border: "1px solid " + C.ink, padding: "1px 6px", fontSize: 10.5,
        background: sel === x.id ? C.sel : C.pane, fontWeight: sel === x.id ? 700 : 400,
        borderLeft: "4px solid " + x.color,
      }}>{x.title}</span>
  );
  return (
    <div style={{ border: "2px solid " + C.ink, boxShadow: "4px 4px 0 " + C.ink, background: C.pane, display: "flex", flexDirection: "column", minWidth: 0 }}>
      <div style={{ background: C.ink, color: C.paper, padding: "3px 9px", fontSize: 10, fontWeight: 700, letterSpacing: "0.1em" }}>MODULE RACK</div>
      <div style={{ padding: "7px 9px", borderBottom: "1px dotted " + C.line }}>
        <div style={{ fontSize: 8.5, fontWeight: 700, letterSpacing: "0.08em", color: C.faint, marginBottom: 3 }}>
          DOC-BOUND VIEWS — carry a DOC strip; several tiles on one document stay in sync
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 7 }}>{group("doc").map(chip)}</div>
        <div style={{ fontSize: 8.5, fontWeight: 700, letterSpacing: "0.08em", color: C.faint, marginBottom: 3 }}>
          WORLD SINGLETONS — no DOC strip; one shared thing, visible from anywhere
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>{group("world").map(chip)}</div>
      </div>
      <div style={{ padding: "8px 9px", overflow: "auto", flex: 1 }}>
        <div style={{ fontSize: 12.5, fontWeight: 700, letterSpacing: "0.05em", textTransform: "uppercase", borderBottom: "2px solid " + C.ink, paddingBottom: 2, marginBottom: 6 }}>
          {m.title}
        </div>
        <Row k="FOR" v={m.what} />
        <Row k="EMITS" v={m.emits} />
        <Row k="ACCEPTS" v={m.accepts} />
        <Row k="L / R" v={m.lr} />
        <Row k="NOT TO BE" v={m.vs} />
      </div>
    </div>
  );
}

/* ============================================================
   PAGE FURNITURE
   ============================================================ */
const Eyebrow = ({ children }) => (
  <div style={{ fontSize: 9.5, fontWeight: 700, letterSpacing: "0.18em", color: C.faint, textTransform: "uppercase", marginBottom: 6 }}>{children}</div>
);
const Prose = ({ children, wide }) => (
  <div style={{ fontSize: 13, lineHeight: 1.65, maxWidth: wide ? 900 : 720, marginBottom: 14 }}>{children}</div>
);
const Kbd = ({ children }) => (
  <span style={{ border: "1px solid " + C.ink, background: C.paneAlt, padding: "0 4px", fontSize: 11, fontWeight: 700, whiteSpace: "nowrap" }}>{children}</span>
);
function CheatCard({ title, rows }) {
  return (
    <div style={{ border: "2px solid " + C.ink, background: C.pane, boxShadow: "3px 3px 0 " + C.ink, maxWidth: 560, marginTop: 18 }}>
      <div style={{ background: C.sel, borderBottom: "2px solid " + C.ink, padding: "2px 9px", fontSize: 9.5, fontWeight: 700, letterSpacing: "0.14em" }}>
        {title}
      </div>
      <div style={{ padding: "7px 9px" }}>
        {rows.map((r, i) => (
          <div key={i} style={{ display: "flex", gap: 9, marginBottom: 3, fontSize: 11.5, lineHeight: 1.45 }}>
            <span style={{ flexShrink: 0, width: 108, fontWeight: 700 }}>{r[0]}</span>
            <span style={{ color: C.faint }}>{r[1]}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function useNarrow(bp = 760) {
  const [n, setN] = useState(false);
  useEffect(() => {
    const on = () => setN(window.innerWidth < bp);
    on(); window.addEventListener("resize", on);
    return () => window.removeEventListener("resize", on);
  }, [bp]);
  return n;
}

/* one section = one sandboxed world + one workbench + a rail */
function SectionBody({ build, lessons, modules, capstone, height, onReset, taller, onTaller }) {
  const worldRef = useRef(null);
  if (!worldRef.current) worldRef.current = new World(build.world);
  const world = worldRef.current;
  const probeRef = useRef({});
  const focusRef = useRef(null);
  const [, force] = useState(0);
  useEffect(() => world.sub(() => force((x) => x + 1)), [world]);
  const buildSpaces = useCallback((w) => build.spaces(w, focusRef), [build]);
  const narrow = useNarrow();
  return (
    <div style={{ display: "flex", gap: 14, alignItems: "stretch", flexWrap: "wrap" }}>
      <div style={{ flex: narrow ? "1 1 100%" : "1 1 290px", minWidth: 0, maxWidth: narrow ? "none" : 400, display: "flex" }}>
        <div style={{ flex: 1, display: "flex" }}>
          {modules ? <ModuleRack modules={modules} probeRef={probeRef} focusRef={focusRef} world={world} />
            : capstone ? <Checklist {...capstone} world={world} probeRef={probeRef} onReset={onReset} taller={taller} onTaller={onTaller} />
              : <LessonRail lessons={lessons} world={world} probeRef={probeRef} onReset={onReset} />}
        </div>
      </div>
      <div style={{ flex: narrow ? "1 1 100%" : "3 1 540px", minWidth: 0 }}>
        <Workbench world={world} buildSpaces={buildSpaces} height={height} probeRef={probeRef} />
      </div>
    </div>
  );
}

function Section({ id, tag, title, blurb, build, lessons, modules, capstone, height, cheat }) {
  const [nonce, setNonce] = useState(0);
  const [taller, setTaller] = useState(false);
  return (
    <section id={id} style={{ padding: "44px 0 10px", borderTop: "1px solid " + C.line }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 10, flexWrap: "wrap" }}>
        <span style={{ background: C.ink, color: C.paper, padding: "3px 12px", fontSize: 12, fontWeight: 700, letterSpacing: "0.2em" }}>§ {tag}</span>
        <h2 style={{ margin: 0, fontSize: 19, fontWeight: 700, letterSpacing: "0.03em" }}>{title}</h2>
      </div>
      <Prose wide>{blurb}</Prose>
      <SectionBody key={nonce} build={build} lessons={lessons} modules={modules} capstone={capstone}
        height={taller ? height + 260 : height} taller={taller} onTaller={() => setTaller((t) => !t)}
        onReset={() => setNonce((n) => n + 1)} />
      {cheat && <CheatCard title={cheat.title} rows={cheat.rows} />}
    </section>
  );
}

/* ============================================================
   CONTENT — the four tracks
   ============================================================ */
const clearSteps = (w, d) => { [...d.chart.steps].forEach((s) => w.removeStep(d.id, s.id)); };
const pointChart = (w, d) => {
  clearSteps(w, d);
  w.setGeom(d.id, "point");
  w.setMapping(d.id, "x", "wing_mm"); w.setMapping(d.id, "y", "mass_g");
  w.setMapping(d.id, "color", "species"); w.setMapping(d.id, "size", null); w.setMapping(d.id, "facet", null);
};

const buildHero = {
  world: (w) => { const d = w.newDoc("seabirds", true); d.chart.geom = "point"; d.chart.mapping = { x: "wing_mm", y: "mass_g", color: "species", size: null, facet: null }; },
  spaces: (w) => [{ id: nid(), name: "start", tree: split("row", leaf("chart", w.docs[0].id), leaf("pipeline", w.docs[0].id), 0.56) }],
};

const buildA = {
  world: (w) => { const d = w.newDoc("seabirds", true); d.chart.geom = "point"; d.chart.mapping = { x: "wing_mm", y: "mass_g", color: "species", size: null, facet: null }; },
  spaces: () => [{ id: nid(), name: "objects", tree: split("row", leaf("data"), split("col", leaf("inspector"), leaf("watch"), 0.56), 0.46) }],
};
const lessonsA = [
  {
    id: "a1", title: "Pointing is asking", manual: true,
    body: <>Sweep the pointer slowly across the field chips in the data browser and watch the <b>black line at the bottom of the panel</b>. It never stops telling you what you are pointing at and what a click will do. This is the whole safety net: nothing in this interface has to be memorised, because the screen describes itself as you move.</>,
  },
  {
    id: "a2", title: "Right-click gives every verb",
    body: <>Right-click the <b>mass_g</b> chip. The menu you get is the list of things a <i>field</i> can do — map to x, map to colour, filter on it, group by it, inspect it. Choose <b>Inspect</b> and its distribution lands in the inspector tile. Now right-click the <b>seabirds</b> chip instead: a different type, so a different menu. That is the entire idea of the system in two clicks. <i>(Trackpad: two-finger click or ⌃-click. Touch: long-press.)</i></>,
    run: (w) => w.inspect("<field> mass_g", { presentationType: "field", name: "mass_g", in_datasets: ["seabirds"], stats: fieldStats(w.active().chart.datasetId, w.active().chart.steps, "mass_g") }),
    done: (w) => w.trace.some((e) => e.type === "inspected"),
    predict: {
      q: "Right-click the seabirds chip instead of a field. Do you get the same menu?",
      options: ["the same menu", "a different menu"], answer: 1,
      reveal: "A dataset is a different type, so it offers different verbs — use as source, new chart from it. The menu is not attached to the pixel; it is attached to what the pixel is.",
    },
  },
  {
    id: "a3", title: "Left-click does the obvious thing",
    body: <>Some objects have one clearly primary verb and just do it on left-click. Left-click the <b>climate</b> dataset chip: it becomes the source of the active chart, and the browser re-marks which dataset is in play. The doc line always announces the default <i>before</i> you commit — and left-click never does anything the right-click menu could not.</>,
    run: (w) => w.setDataset(w.activeId, "climate"),
    done: (w) => w.active().chart.datasetId === "climate",
  },
  {
    id: "a4", title: "Accept: a command reaching out for its argument",
    body: <>Press <b>Watch… (accept anything)</b> in the watchlist tile. A red banner appears, everything acceptable starts pulsing, and the next object you click is consumed by the waiting command. Think of it as an eyedropper: the command has paused with its hand out. Click a field chip over in the <i>data browser</i> — a different tile — and watch it get swallowed. <Kbd>Esc</Kbd> aborts. Map-to-slot, compare A/B and swap-tiles all work this way.</>,
    run: async (w, api) => { const r = await api.accept("field", "TUTORIAL — click any FIELD chip, in any tile"); if (r) w.watchAdd("field", r.value); },
    done: (w) => w.watch.length > 0,
  },
  {
    id: "a5", title: "Everything you did is on the record", manual: true,
    body: <>Look at the <b>TRACE</b> strip along the bottom of the panel. It has been filling since lesson one without being mentioned. Every verb — yours or the tutorial's — is appended there with the object it acted on. Not a debug log: a transcript of the session.</>,
  },
];

const buildB = {
  world: (w) => {
    const a = w.newDoc("seabirds", true);
    a.chart.geom = "point"; a.chart.mapping = { x: "wing_mm", y: "mass_g", color: "species", size: null, facet: null };
    const b = w.newDoc("climate", true);
    b.chart.geom = "line"; b.chart.mapping = { x: "month", y: "temp_c", color: "city", size: null, facet: null };
    w.activeId = a.id;
  },
  spaces: (w) => [
    { id: nid(), name: "two views", tree: split("row", leaf("chart", w.docs[0].id), leaf("table", w.docs[0].id), 0.56) },
    { id: nid(), name: "spare", tree: leaf("launcher") },
  ],
};
const lessonsB = [
  {
    id: "b1", title: "Two tiles, one document",
    body: <>Both tiles are pointed at document <b>α</b> — look at their DOC strips. Right-click any dot in the chart and choose <b>Keep only species = …</b>. A filter step is written into α's pipeline, so the chart redraws <i>and</i> the table's rows drop, together. Nothing is wired between them: they are two views of one object.</>,
    run: (w) => w.filterToCat(w.docs[0].id, "species", "Skua", true),
    done: (w) => w.docs[0].chart.steps.length > 0,
  },
  {
    id: "b2", title: "Layouts are disposable",
    body: <>Split a tile with <Kbd>⬌</Kbd> or <Kbd>⬍</Kbd> in its title bar, then pick an app in the empty one. Drag a title bar's <Kbd>⠿</Kbd> onto another tile: the <b>centre</b> swaps the two apps, an <b>edge</b> docks it there. Drag the dividers — they snap at ¼ ⅓ ½ ⅔ ¾. Nothing you do here can lose work, because no app keeps its state in the tile.</>,
    run: (w, api, p) => api.splitLeaf(p.leaves[0].id, "col"),
    done: (w, p) => (p.nLeaves || 0) > 2,
  },
  {
    id: "b3", title: "Re-point a view at another document",
    body: <>The world holds two documents: <b>α</b> on seabirds and <b>β</b> on climate. Use the dropdown in any DOC strip to point a tile at <b>β</b>. The tile changes what it is looking at; α is untouched. <Kbd>＋</Kbd> in the same strip spawns a brand-new document into that tile.</>,
    run: (w, api, p) => { const ds = (p.leaves || []).filter((l) => DOC_APPS.includes(l.app)); if (ds[1] && w.docs[1]) api.setLeafDoc(ds[1].id, w.docs[1].id); },
    done: (w, p) => (p.docsShown ? p.docsShown.size : 0) > 1,
    predict: {
      q: "You are about to point the right-hand tile at β. Does the left-hand chart change too?",
      options: ["yes, they are linked", "no, they are separate"], answer: 1,
      reveal: "They were only moving together because they were looking at the same document. Re-point one and the link is gone — nothing was ever wired between the tiles.",
    },
  },
  {
    id: "b4", title: "Workspaces are camera positions",
    body: <>The strip at the top of the panel switches whole layouts. Nothing is saved or loaded — the world is identical in all of them. Press <b>+ workspace</b>, build something different, switch back to <i>two views</i>: exactly as you left it. Right-click a workspace chip to rename, duplicate or delete it.</>,
    run: (w, api) => api.addSpace(),
    done: (w, p) => (p.spaces ? p.spaces.length : 0) > 2,
  },
  {
    id: "b5", title: "Closing a tile destroys nothing", manual: true,
    body: <>Close a tile with <Kbd>✕</Kbd>. Its sibling absorbs the space. Now open a new tile and point it back at the same document: everything is still there — pipeline, encoding, geometry. Views are cheap. State is not in them.</>,
  },
];

const buildC = {
  world: (w) => { const d = w.newDoc("seabirds", true); d.chart.geom = "point"; d.chart.mapping = { x: "wing_mm", y: "mass_g", color: "species", size: null, facet: null }; },
  spaces: (w) => {
    const dA = w.docs[0].id;
    return [{
      id: nid(), name: "build",
      tree: split("col",
        leaf("spec", dA),
        split("row",
          split("col", leaf("pipeline", dA), leaf("encode", dA), 0.54),
          split("col", leaf("chart", dA), leaf("table", dA), 0.66),
          0.44),
        0.15),
    }];
  },
};
const nFilters = (w) => w.trace.filter((e) => e.type === "step_added" && e.data.kind === "filter").length;
const lessonsC = [
  {
    id: "c1", title: "Read the sentence first", manual: true,
    body: <>The strip along the top of the panel is the whole chart written as one line: <b>dataset ⊳ steps │ slot ↦ field │ geom │ scale</b>. Every segment is a live object — hover them, right-click them. Press <b>as ggplot</b> to see the same spec as tidyverse source. Nothing else in this section will be new; you are just going to edit this sentence.</>,
  },
  {
    id: "c2", title: "filter — the data half",
    body: <>In the pipeline tile press <b>+ filter…</b>. It does not ask you to type a field name; it <i>accepts</i> one, so click <b>species</b> anywhere — the browser, a table header, the OUT schema. Then set the operator to <b>≠</b> and the value to <b>Tern</b>. Row count drops in the table, points vanish from the chart, and the sentence at the top grows a clause.</>,
    run: (w) => w.addStep(w.activeId, mkStep("filter", { field: "species", op: "≠", value: "Tern" })),
    done: (w) => nFilters(w) >= 1,
  },
  {
    id: "c3", title: "A deliberate mistake",
    body: <>In the encoding tile, click the <b>bar</b> geom while x is still <b>wing_mm</b>, a quantitative field. The chart does not draw nonsense and does not fail silently — it states the problem: a bar geom wants a category on x. Geoms have <i>type requirements</i>, which is exactly what a chart-type picker hides from you.</>,
    run: (w) => w.setGeom(w.activeId, "bar"),
    done: (w) => w.active().chart.geom === "bar",
    predict: {
      q: "A bar geom needs categories on x. x is currently wing_mm, a measurement. What happens?",
      options: ["it buckets the numbers for you", "it says what is wrong"], answer: 1,
      reveal: "Guessing would be worse than useless — you would get a chart you had not asked for and could not reason about. Instead the spec reports that it does not describe a drawable chart, and names the reason.",
    },
  },
  {
    id: "c4", title: "Fix it with the other half",
    body: <>Add <b>+ group∑…</b> and accept <b>species</b>, with <i>mean</i> of <i>mass_g</i>. The output schema collapses to two columns. Now re-map x to <b>species</b> and y to <b>mean_mass_g</b> — use <Kbd>⌖</Kbd> and click the chips in the pipeline's OUT strip. The bar chart appears. Transforms change the schema; encodings consume it.</>,
    run: (w) => {
      const d = w.active();
      w.addStep(d.id, mkStep("summarize", { by: "species", fn: "mean", field: "mass_g" }));
      w.setMapping(d.id, "x", "species"); w.setMapping(d.id, "y", "mean_mass_g");
      w.setMapping(d.id, "color", "species"); w.setGeom(d.id, "bar");
    },
    done: (w) => { const c = w.active().chart; return c.geom === "bar" && c.steps.some((s) => s.kind === "summarize" && s.on) && !!c.mapping.y && c.mapping.y.indexOf("mean_") === 0; },
  },
  {
    id: "c5", title: "A facet is just one more slot",
    body: <>Back to points: clear the steps, map x to <b>wing_mm</b>, y to <b>mass_g</b>, then point the <b>facet</b> slot at <b>island</b>. Small multiples, one panel per level, scales shared so the panels are comparable. Un-map it and they collapse back. Faceting is not a different kind of chart.</>,
    run: (w) => { const d = w.active(); pointChart(w, d); w.setMapping(d.id, "color", "sex"); w.setMapping(d.id, "facet", "island"); },
    done: (w) => w.active().chart.mapping.facet != null,
  },
  {
    id: "c6", title: "The picture is an editable surface",
    body: <>Right-click a legend swatch and choose <b>Keep only …</b>, or right-click a dot and exclude its island. A real filter step appears in the pipeline — visible, reorderable, and switchable with its <Kbd>✓</Kbd> box. The chart was never a dead-end render; it is one more surface of the same object graph.</>,
    run: (w) => w.filterToCat(w.activeId, "island", "Dune", false),
    done: (w) => nFilters(w) >= 2,
  },
];

const buildD = {
  world: (w) => {
    const a = w.newDoc("seabirds", true);
    a.chart.geom = "point"; a.chart.mapping = { x: "wing_mm", y: "mass_g", color: "species", size: null, facet: null };
    a.chart.steps = [mkStep("filter", { field: "mass_g", op: ">", value: "3000" })];
    const b = w.newDoc("climate", true);
    b.chart.geom = "line"; b.chart.mapping = { x: "month", y: "temp_c", color: "city", size: null, facet: null };
    w.activeId = a.id;
    const c1 = defaultChart("climate");
    c1.mapping = { x: "month", y: "temp_c", color: "city", size: null, facet: null }; c1.geom = "line";
    w.snaps.push({ id: "snap" + ++snapc, name: "city-temps", chart: c1, at: "seed" });
    const c2 = defaultChart("engines");
    c2.steps = [mkStep("summarize", { by: "origin", field: "mpg", fn: "mean" })];
    c2.mapping = { x: "origin", y: "mean_mpg", color: "origin", size: null, facet: null }; c2.geom = "bar";
    w.snaps.push({ id: "snap" + ++snapc, name: "mpg-by-origin", chart: c2, at: "seed" });
    w.pins = [w.snaps[0].id, w.snaps[1].id];
    w.watch = [{ id: ++notec, ptype: "dataset", value: "seabirds" }, { id: ++notec, ptype: "field", value: "mass_g" }];
  },
  spaces: (w, focusRef) => {
    const f = leaf("data");
    focusRef.current = f.id;
    return [{ id: nid(), name: "rack", tree: split("row", f, split("col", leaf("charts"), leaf("inspector"), 0.56), 0.58) }];
  },
};
const MODULES = [
  {
    id: "chart", title: "chart", kind: "doc", color: C.rose,
    what: "The composed picture for one document.",
    emits: <><b>&lt;datum&gt;</b> for every mark, <b>&lt;cat&gt;</b> for every legend swatch, <b>&lt;dataset&gt;</b> in its header.</>,
    accepts: "—",
    lr: "R on a mark or swatch writes a filter step into this chart's own pipeline.",
    vs: <>a picture. it is a view, and editing it edits the document.</>,
  },
  {
    id: "table", title: "table", kind: "doc", color: C.mint,
    what: "The pipeline's live output relation, after every enabled step.",
    emits: <><b>&lt;field&gt;</b> in the headers, <b>&lt;datum&gt;</b> in the row-number cells.</>,
    accepts: "—",
    lr: "R a row № to keep or exclude its categories; R a header to map or sort by it.",
    vs: <>the <b>pipeline</b> — that is the recipe, this is the food.</>,
  },
  {
    id: "pipeline", title: "pipeline", kind: "doc", color: C.blue,
    what: "The chain of tidyverse verbs that produces the data: filter, derive, group∑, sort, limit.",
    emits: <><b>&lt;step&gt;</b> per row, <b>&lt;field&gt;</b> in the OUT schema, <b>&lt;dataset&gt;</b> as SOURCE.</>,
    accepts: <><b>&lt;field&gt;</b> — “+ filter…” and “+ group∑…” pause and wait for you to click one.</>,
    lr: "✓ disables a step in place; R gives move ↑↓ and remove. Order is semantics.",
    vs: <>an undo history. steps are objects you can reorder, not events that happened.</>,
  },
  {
    id: "encode", title: "encoding", kind: "doc", color: C.mustard,
    what: "The aesthetic mapping — which field drives which visual channel — plus the geom and the y scale.",
    emits: <><b>&lt;field&gt;</b> per filled slot, <b>&lt;geom&gt;</b> per geometry chip.</>,
    accepts: <><b>&lt;field&gt;</b> — one ⌖ per slot: x, y, colour, size, facet.</>,
    lr: "L a geom chip to use it. × clears a slot.",
    vs: <>a chart-type menu. there is no “bar chart”, only a bar geom over a mapping.</>,
  },
  {
    id: "spec", title: "spec", kind: "doc", color: C.sel,
    what: "The entire composition as one line: dataset ⊳ steps │ slot ↦ field │ geom │ scale.",
    emits: <>every segment is the same live object the other tiles show.</>,
    accepts: "—",
    lr: "“as ggplot” prints the same spec as tidyverse + ggplot2 source.",
    vs: <>a summary. it is the document, rendered as a sentence.</>,
  },
  {
    id: "data", title: "data browser", kind: "world", color: C.sage,
    what: "Every source table and its typed columns. The starting point of everything.",
    emits: <><b>&lt;dataset&gt;</b> and <b>&lt;field&gt;</b>.</>,
    accepts: "—",
    lr: "L a dataset → source of the ACTIVE chart. R a field → map, filter, group, inspect.",
    vs: <>a file picker. these fields are the same objects the encoding tile consumes.</>,
  },
  {
    id: "charts", title: "charts", kind: "world", color: C.rose,
    what: "The document manager: every live chart in the world, α, β, γ…",
    emits: <><b>&lt;doc&gt;</b> per card.</>,
    accepts: "—",
    lr: "L a doc chip makes it ACTIVE — the target of every object-menu verb fired from anywhere.",
    vs: <>the <b>snapshots</b> tile — these are alive and still changing.</>,
  },
  {
    id: "gallery", title: "snapshots", kind: "world", color: C.lavender,
    what: "Frozen copies of a whole spec, kept as immutable objects with live thumbnails.",
    emits: <><b>&lt;chart&gt;</b> per card.</>,
    accepts: "—",
    lr: "L restores into the ACTIVE document. R restores as a NEW one, or pins it to compare A / B.",
    vs: <>a document. ⚑ copies the spec; the snapshot does not move afterwards.</>,
  },
  {
    id: "compare", title: "compare a/b", kind: "world", color: C.rose,
    what: "Two frozen specs side by side, with their pipelines and encodings spelled out.",
    emits: <><b>&lt;chart&gt;</b> for each pinned side.</>,
    accepts: <><b>&lt;chart&gt;</b> — “accept…” then click a snapshot name anywhere.</>,
    lr: "L a pinned name restores it into the active document.",
    vs: <>a diff tool. it shows two specs; you do the reading.</>,
  },
  {
    id: "watch", title: "watchlist", kind: "world", color: C.mustard,
    what: "A scratchpad of objects you want to keep within reach, of any type at all.",
    emits: <>re-presents whatever you put in it — still live, still right-clickable.</>,
    accepts: <><b>any type</b> — the broadest accept in the system.</>,
    lr: "Same verbs as wherever the object came from. × removes it from the list.",
    vs: <>the <b>inspector</b> — that shows the last thing you looked at, this shows what you kept.</>,
  },
  {
    id: "inspector", title: "inspector", kind: "world", color: C.lavender,
    what: "The full description of the last object you inspected, printed as data.",
    emits: "—",
    accepts: "—",
    lr: "Fed by the Inspect verb, which every object type offers.",
    vs: <>a properties panel. it is a reader, not an editor.</>,
  },
  {
    id: "trace", title: "trace", kind: "world", color: C.sage,
    what: "The session transcript: every verb, with the object and the chart it acted on.",
    emits: "—",
    accepts: "—",
    lr: "Read-only. The strip at the bottom of every panel is its last three lines.",
    vs: <>the <b>pipeline</b> — that is what the chart does, this is what you did.</>,
  },
];

/* ============================================================
   CAPSTONE — one real question, no rail, no ▶.
   Goals are predicates over the world, so they tick for any
   route to the same state, including ones not anticipated here.
   ============================================================ */
const buildE = {
  world: (w) => { const d = w.newDoc("seabirds", true); d.chart.geom = "point"; d.chart.mapping = { x: "wing_mm", y: "mass_g", color: "species", size: null, facet: null }; },
  spaces: (w) => {
    const dA = w.docs[0].id;
    return [
      { id: nid(), name: "build", tree: split("row", split("col", leaf("pipeline", dA), leaf("encode", dA), 0.55), leaf("chart", dA), 0.46) },
      { id: nid(), name: "explore", tree: split("row", leaf("data"), split("col", leaf("chart", dA), leaf("inspector"), 0.58), 0.4) },
      { id: nid(), name: "keep", tree: split("row", leaf("gallery"), leaf("compare"), 0.5) },
    ];
  },
};
/* rows as they stand just before any grouping — lets the first goal tick
   whether you kept Terns or excluded the other two species */
const preGroup = (c) => {
  const i = c.steps.findIndex((s) => s.on && s.kind === "summarize");
  return evaluate(c.datasetId, i < 0 ? c.steps : c.steps.slice(0, i)).rows;
};
const capstoneE = {
  question: <>Which island's <b>terns</b> are the heaviest — and can you put the numbers next to the picture that convinced you?</>,
  items: [
    {
      id: "e1", label: <>only terns are left in the data</>,
      done: (w) => w.docs.some((d) => { const r = preGroup(d.chart); return r.length > 0 && r.every((x) => String(x.species) === "Tern"); }),
    },
    {
      id: "e2", label: <>one number per island — grouped and summarised</>,
      done: (w) => w.docs.some((d) => { const f = schemaAfter(d.chart.datasetId, d.chart.steps); return f.length === 2 && f[0].name === "island" && f[1].type === "q"; }),
    },
    {
      id: "e3", label: <>a bar chart that actually draws</>,
      done: (w) => w.docs.some((d) => d.chart.geom === "bar" && !(buildPlot(d.chart, 400, 200, true).problems || []).length),
    },
    { id: "e4", label: <>frozen as a snapshot, so it survives what you do next</>, done: (w) => w.snaps.length > 0 },
    {
      id: "e5", label: <>the evidence beside the picture — a table and a chart, on one document, at once</>,
      done: (w, p) => {
        const ls = p.leaves || [];
        return ls.filter((l) => l.app === "table").some((t) => ls.some((c) => c.app === "chart" && c.doc === t.doc));
      },
    },
  ],
  nudges: [
    "No data browser in this layout? Every tile has an app dropdown in its title bar — or split one with ⬌ and pick from the launcher.",
    "Terns are one of three species. A filter step keeps rows — and right-clicking a Tern dot in the chart writes one for you.",
    "Three islands, one number each: that is group∑ by island, summarising mass_g.",
    "After a group∑ the schema collapses to two columns, so the x and y you had before will need re-pointing.",
    "geom_bar wants the category on x and the aggregate on y.",
    "⚑ snapshot sits in the chart tile's header, and again in the snapshots tile.",
    "For the last one: split a tile, set it to table, and check its DOC strip names the same document as the chart.",
  ],
};

/* ============================================================
   HERO
   ============================================================ */
function HeroWidget() {
  const worldRef = useRef(null);
  if (!worldRef.current) worldRef.current = new World(buildHero.world);
  const probeRef = useRef({});
  const buildSpaces = useCallback((w) => buildHero.spaces(w), []);
  return <Workbench world={worldRef.current} buildSpaces={buildSpaces} height={330} probeRef={probeRef} showTrace={false} />;
}

const NAV = [
  { id: "objects", tag: "A", label: "objects and verbs" },
  { id: "layout", tag: "B", label: "tiles and workspaces" },
  { id: "grammar", tag: "C", label: "the grammar" },
  { id: "modules", tag: "D", label: "the modules" },
  { id: "brief", tag: "✦", label: "the brief" },
];

export default function App() {
  const [navOn, setNavOn] = useState(false);
  const narrow = useNarrow();
  const heroRef = useRef(null);
  useEffect(() => {
    const el = heroRef.current; if (!el) return;
    const io = new IntersectionObserver(([e]) => setNavOn(!e.isIntersecting), { threshold: 0 });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  const go = (id) => { const el = document.getElementById(id); if (el) el.scrollIntoView({ behavior: "smooth", block: "start" }); };

  return (
    <div style={{ fontFamily: MONO, background: C.wash, color: C.ink, minHeight: "100vh", fontSize: 13 }}>
      <style>{`
        .pres { cursor: pointer; }
        .pres:hover { outline: 1px dotted ${C.ink}; background: ${C.sel}; }
        .pres:focus-visible { outline: 2px solid ${C.red}; outline-offset: 1px; background: ${C.sel}; }
        .pres:focus:not(:focus-visible) { outline: none; }
        .pres.acceptable { outline: 2px solid ${C.red}; background: ${C.sel}; animation: pbuipulse 0.9s infinite; cursor: pointer; }
        .pres-svg { cursor: pointer; }
        .pres-svg:hover { filter: drop-shadow(0 0 1.5px ${C.ink}); }
        .pres-svg.acceptable { filter: drop-shadow(0 0 2.5px ${C.red}); }
        @keyframes pbuipulse { 50% { outline-color: ${C.mustard}; } }
        ::-webkit-scrollbar { width: 11px; height: 11px; }
        ::-webkit-scrollbar-thumb { background: ${C.line}; border: 3px solid ${C.pane}; }
        ::-webkit-scrollbar-track { background: ${C.pane}; }
        table th { font-weight: 700; }
        a { color: inherit; }
        @media (prefers-reduced-motion: reduce) {
          .pres.acceptable { animation: none; }
          html { scroll-behavior: auto; }
        }
      `}</style>

      {/* masthead */}
      <div style={{ background: C.ink, color: C.paper, textAlign: "center", padding: "6px 10px", fontWeight: 700, letterSpacing: narrow ? "0.14em" : "0.28em", fontSize: narrow ? 10.5 : 13 }}>
        P B U I &nbsp;—&nbsp; G R A M M A R &nbsp; O F &nbsp; G R A P H I C S
      </div>

      {/* sticky section index, appears once the hero is past */}
      <div style={{
        position: "sticky", top: 0, zIndex: 40, background: C.paper, borderBottom: "1px solid " + C.line,
        padding: navOn ? (narrow ? "5px 12px" : "5px 22px") : "0 12px", height: navOn ? "auto" : 0, overflow: "hidden",
        display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", transition: "padding 120ms linear",
      }}>
        <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.14em", color: C.faint }}>TOUR</span>
        {NAV.map((n) => (
          <span key={n.id} onClick={() => go(n.id)}
            style={{ cursor: "pointer", border: "1px solid " + C.ink, background: C.paneAlt, padding: "0 8px", fontSize: 10.5 }}>
            <b>{n.tag}</b> · {n.label}
          </span>
        ))}
      </div>

      <div style={{ maxWidth: 1180, margin: "0 auto", padding: narrow ? "0 12px 60px" : "0 22px 70px" }}>

        {narrow && (
          <div style={{ marginTop: 14, border: "2px solid " + C.ink, background: C.sel, padding: "6px 10px", fontSize: 11.5, lineHeight: 1.5 }}>
            <b>This is built for a mouse and a wide screen.</b> The panels below are the real thing, tiled four
            ways, and they will be cramped here. Read on if you like — but open it on a desktop to actually use it.
          </div>
        )}

        {/* ---------------- hero ---------------- */}
        <div ref={heroRef} style={{ padding: "38px 0 8px" }}>
          <Eyebrow>a workbench built on presentations · after Genera and CLIM</Eyebrow>
          <h1 style={{ margin: "0 0 12px", fontSize: 27, lineHeight: 1.25, fontWeight: 700, letterSpacing: "0.01em", maxWidth: 760 }}>
            The thing on screen is the thing.
          </h1>
          <Prose>
            Every label, chip, axis tick and dot below is a typed object with the real value attached — not a
            picture of one. Right-click a dot in the chart and choose <b>Keep only species = …</b>: a filter step
            is written into the pipeline beside it, and the chart redraws. That single move is the whole system.
            The rest of this page is four workspaces you can take apart.
          </Prose>
          <HeroWidget />
          <div style={{ display: "flex", gap: 10, alignItems: "center", marginTop: 12, flexWrap: "wrap" }}>
            <span onClick={() => go("objects")} style={{ cursor: "pointer", border: "2px solid " + C.ink, boxShadow: "3px 3px 0 " + C.ink, background: C.sel, padding: "4px 14px", fontSize: 12, fontWeight: 700 }}>
              start the tour ↓
            </span>
            <span style={{ fontSize: 11, color: C.faint }}>
              four tracks and a brief · about twenty-five minutes · every panel has its own world and its own ↺ reset
            </span>
          </div>
        </div>

        {/* ---------------- §A ---------------- */}
        <Section
          id="objects" tag="A" title="Objects and verbs"
          height={520}
          build={buildA} lessons={lessonsA}
          blurb={<>
            The one idea underneath everything: whatever is displayed stays a first-class handle on the real
            object. It carries its type, so it carries a menu of verbs appropriate to that type — and any command
            can pause and ask you to point at an argument, anywhere on screen. Three moves to learn:
            hover, right-click, accept.
          </>}
          cheat={{
            title: "CHEAT SHEET · OBJECTS", rows: [
              ["hover", "the doc line names the object and what L and R will do"],
              ["left-click", "the default verb — or the menu, if the object has none"],
              ["right-click", "every verb this type has"],
              ["red banner", "a command is accepting an argument · Esc aborts"],
              ["the types", "dataset · field · doc · chart · step · datum · cat · geom · tile · workspace"],
            ],
          }}
        />

        {/* ---------------- §B ---------------- */}
        <Section
          id="layout" tag="B" title="Tiles, documents, workspaces"
          height={520}
          build={buildB} lessons={lessonsB}
          blurb={<>
            The confusion worth clearing up before anything else: <b>tiles are windows, documents are the
            thing</b>. A chart, table, pipeline or encoding tile is a <i>view</i> of one document, named in the DOC
            strip at its top. Point two tiles at the same document and they move together, because they are not
            copies. Then the layout itself — splitting, docking, whole workspaces — becomes safe to play with.
          </>}
          cheat={{
            title: "CHEAT SHEET · SHELL", rows: [
              ["⠿ drag", "centre swaps two apps · edge docks the tile there"],
              ["⬌ ⬍ ✕", "split right · split below · close (the document survives)"],
              ["DOC strip", "which document this view shows · ＋ spawns a new one"],
              ["ACTIVE doc", "the target of verbs fired from object menus — the menu header names it"],
              ["workspaces", "independent layouts over one shared world"],
            ],
          }}
        />

        {/* ---------------- §C ---------------- */}
        <Section
          id="grammar" tag="C" title="The grammar of graphics"
          height={660}
          build={buildC} lessons={lessonsC}
          blurb={<>
            A chart here is not a type you pick from a menu. It is a composition — <b>dataset ⊳ steps ↦ mapping ·
              geom · scale</b> — and the strip along the top of this panel shows that composition as one live
            sentence you can edit from either end. The left half is dplyr; the right half is <i>aes()</i>. Watch what
            happens when you ask for a geometry the data cannot support.
          </>}
          cheat={{
            title: "CHEAT SHEET · GRAMMAR", rows: [
              ["the spec", "dataset ⊳ steps ↦ mapping · geom · scale"],
              ["steps", "filter · derive · group∑ · sort · limit — order is semantics"],
              ["slots", "x · y · colour · size · facet"],
              ["geoms", "point · line · bar · area — each states its type requirements"],
              ["✓ on a step", "disables it in place, so you can A/B your own transform"],
            ],
          }}
        />

        {/* ---------------- §D ---------------- */}
        <Section
          id="modules" tag="D" title="The modules"
          height={560}
          build={buildD} modules={MODULES}
          blurb={<>
            Twelve applications share one world. The distinction that makes them legible: if a tile carries a
            <b> DOC strip</b> it is a view of a single chart document and can be re-pointed; if it does not, it is
            the whole world and there is only one of it. Pick any module to swap the large tile to it and read
            what it emits, what it accepts, and which other module people confuse it with.
          </>}
          cheat={{
            title: "CHEAT SHEET · MODULES", rows: [
              ["doc-bound", "chart · table · pipeline · encoding · spec"],
              ["singletons", "data browser · charts · snapshots · compare · watchlist · inspector · trace"],
              ["emits", "which presentation types are born in this tile"],
              ["accepts", "which types its commands will pause and ask you for"],
              ["the pairs", "pipeline≠table · charts≠snapshots · watchlist≠inspector · trace≠pipeline"],
            ],
          }}
        />

        {/* ---------------- capstone ---------------- */}
        <Section
          id="brief" tag="✦" title="The brief"
          height={560}
          build={buildE} capstone={capstoneE}
          blurb={<>
            No lesson rail this time, and no <b>▶ do it for me</b>. A question, a workbench, and five things that
            have to be true when you are finished. They tick by watching the world, not by watching you — so any
            route that reaches the same state counts, including one nobody wrote down. <i>I'm stuck</i> gives you
            one hint at a time and never the answer.
          </>}
        />

        {/* ---------------- closing ---------------- */}
        <section style={{ padding: "44px 0 0", borderTop: "1px solid " + C.line }}>
          <Eyebrow>where this comes from</Eyebrow>
          <Prose wide>
            The interaction model is from the Lisp machines — Symbolics <b>Genera</b>'s Dynamic Windows and its
            standardised descendant <b>CLIM</b>. Their claim was that programs should never print dead text: they
            <i> present</i> objects with the type attached, so anything ever displayed stays a handle on the real
            value, with a menu of type-appropriate verbs and the ability to be handed to a command waiting in a
            different window. The domain model is Wilkinson's <i>Grammar of Graphics</i> by way of <b>ggplot2</b>
            and the tidyverse: pipeline is dplyr, encoding is <i>aes()</i>, the geometry chips are geom_*, the facet
            slot is facet_wrap, the y toggle is scale_y_log10. Because the spec is data, freezing it and diffing
            two of them are trivial operations rather than features.
          </Prose>
          <Prose wide>
            The three datasets are invented and generated deterministically from fixed seeds, so every panel on
            this page starts identically on every load — and ↺ reset really does put one back.
          </Prose>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 16 }}>
            {NAV.map((n) => (
              <span key={n.id} onClick={() => go(n.id)}
                style={{ cursor: "pointer", border: "2px solid " + C.ink, boxShadow: "2px 2px 0 " + C.ink, background: C.pane, padding: "3px 12px", fontSize: 11.5 }}>
                ▸ §{n.tag} {n.label}
              </span>
            ))}
          </div>
          <div style={{ marginTop: 26, paddingTop: 10, borderTop: "1px solid " + C.line, fontSize: 10.5, color: C.faint, display: "flex", gap: 16, flexWrap: "wrap" }}>
            <span>hover documents · L is the default verb · R is every verb · Esc aborts an accept</span>
            <span style={{ flex: 1 }} />
            <span>six sandboxed worlds on this page · they share nothing</span>
          </div>
        </section>
      </div>
    </div>
  );
}
