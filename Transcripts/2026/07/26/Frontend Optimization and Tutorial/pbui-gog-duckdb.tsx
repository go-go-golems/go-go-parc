import React, { useState, useRef, useEffect, useCallback, useContext } from "react";

/* ============================================================
   PBUI — browser-native visual analysis workbench

   A chart document owns a dataset, an ordered transform pipeline,
   channel mappings, a geometry and a scale. Chart, table, pipeline
   and encoding tiles are linked views over that document. Rendered
   values remain typed objects with verbs, so analysis can continue
   directly from a mark, row, field, step or saved state.
   ============================================================ */

/* ---------------- palette ---------------- */
const C = {
  paper: "#ffffff", pane: "#ffffff", paneAlt: "#f1f1ee",
  ink: "#23262b", faint: "#7b8087", line: "#d9d9d4",
  sage: "#7cae9b", blue: "#7aa6c9", rose: "#d59a86",
  mustard: "#e0b95c", lavender: "#a99fc9", mint: "#8fc7b0",
  red: "#c2503a", green: "#3f9d6b", sel: "#fdeec6",
};
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const fmt = (v, d = 2) => {
  if (typeof v !== "number") return String(v);
  if (Number.isInteger(v) && Math.abs(v) < 1e6) return String(v);
  return Math.abs(v) >= 100 ? v.toFixed(0) : Math.abs(v) >= 10 ? v.toFixed(1) : v.toFixed(d);
};
const CAT_TONES = [C.blue, C.red, C.mustard, C.sage, C.lavender, C.rose, C.mint, "#8892a8"];
const TYPE_LABEL = { q: "quant", n: "nominal", t: "temporal" };
const TYPE_TONE = { q: C.blue, n: C.mustard, t: C.sage };

/* ============================================================
   PBUI CORE — presentations + accept
   ============================================================ */
const UICtx = React.createContext(null);
const useUI = () => useContext(UICtx);
const typeMatches = (want, have) =>
  want === "any" || (Array.isArray(want) ? want.includes(have) : want === have);

function P({ ptype, value, doc, children, block, svg, onActivate, activateDoc }) {
  const ui = useUI();
  const acceptable = ui.accepting && typeMatches(ui.accepting.ptype, ptype);
  /* inside an <svg> we must emit an SVG element — HTML <span>s are
     silently dropped by the renderer, so marks would never draw */
  const Tag = svg ? "g" : block ? "div" : "span";
  const clickDoc = acceptable ? "L: ACCEPT   R: menu"
    : onActivate ? "L: " + (activateDoc || "activate") + "   R: menu"
      : "L/R: menu";
  return (
    <Tag
      className={(svg ? "pres-svg" : "pres") + (acceptable ? " acceptable" : "")}
      onContextMenu={(e) => { e.preventDefault(); e.stopPropagation(); ui.openMenu(ptype, value, e.clientX, e.clientY); }}
      onClick={(e) => {
        e.stopPropagation();
        if (acceptable) { e.preventDefault(); ui.accepting.resolve({ ptype, value }); ui.setAccepting(null); }
        else if (onActivate) onActivate();
        else ui.openMenu(ptype, value, e.clientX, e.clientY);
      }}
      onMouseEnter={() => ui.setMouseDoc((doc || "<" + ptype + "> " + ui.labelFor(ptype, value)) + "   —   " + clickDoc)}
      onMouseLeave={() => ui.setMouseDoc(null)}
    >{children}</Tag>
  );
}

/* Pres — default visual for a (ptype, value), used when an app
   re-presents an object it did not originate (watchlist, etc). */
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

/* deterministic rng so mock data never jitters */
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
   field types: q = quantitative · n = nominal · t = temporal
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
      rows.push({
        origin: o.origin, cyl,
        hp, weight_kg: wt,
        mpg: +clamp((5200 / wt) * 12 * o.eff + gauss(r, 0, 2.2), 9, 52).toFixed(1),
      });
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
   step kinds: filter · derive · summarize · sort · limit
   ============================================================ */
let stepc = 0;
const mkStep = (kind, cfg) => ({ id: "s" + ++stepc, kind, on: true, ...cfg });
const AGGS = ["mean", "sum", "min", "max", "count"];
const DOPS = ["+", "-", "*", "/", "log10"];
const FOPS = ["=", "≠", ">", "<"];

function applyAgg(fn, vals) {
  if (fn === "count") return vals.length;
  if (!vals.length) return 0;
  let total = 0;
  let min = Infinity;
  let max = -Infinity;
  for (const value of vals) {
    total += value;
    if (value < min) min = value;
    if (value > max) max = value;
  }
  if (fn === "sum") return total;
  if (fn === "mean") return total / vals.length;
  return fn === "min" ? min : max;
}
const aggName = (fn, field) => (fn === "count" ? "count" : fn + "_" + field);

/* schema evolution only (no rows) — used for step editors */
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

function evaluateJS(datasetId, steps) {
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
      if (!FOPS.includes(s.op)) { err = "filter uses an unsupported operator"; continue; }
      if (s.value === "" || s.value == null) continue; /* unconfigured filter passes everything */
      const val = t === "q" ? +s.value : s.value;
      rows = rows.filter((r) => {
        const v = r[s.field];
        if (s.op === "=") return String(v) === String(val);
        if (s.op === "≠") return String(v) !== String(val);
        if (s.op === ">") return +v > +val;
        return +v < +val;
      });
    } else if (s.kind === "derive") {
      const types = fmap();
      if (!DOPS.includes(s.op)) { err = "derive uses an unsupported operator"; continue; }
      if (!types[s.a] || (s.op !== "log10" && !types[s.b])) { err = "derive refers to a missing field"; continue; }
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
      const types = fmap();
      if (!AGGS.includes(s.fn)) { err = "summarize uses an unsupported aggregate"; continue; }
      if (!types[s.by] || (s.fn !== "count" && !types[s.field])) { err = "summarize refers to a missing field"; continue; }
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
      if (t === undefined) { err = "sort refers to missing field " + s.field; continue; }
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

/* ============================================================
   FRONTEND QUERY ENGINE — DuckDB-Wasm with a synchronous fallback

   The UI can render immediately from the small JavaScript evaluator.
   In parallel, the same pipeline is compiled to SQL and executed in a
   worker. Results are cached by semantic pipeline state, so subsequent
   chart/table renders are synchronous and do not repeat the query.
   ============================================================ */
const QUERY_CACHE_LIMIT = 160;

const quoteIdent = (value) => '"' + String(value).replace(/"/g, '""') + '"';
const quoteString = (value) => "'" + String(value).replace(/'/g, "''") + "'";
const semanticStep = (s) => {
  if (s.kind === "filter") return { kind: s.kind, on: s.on, field: s.field, op: s.op, value: s.value };
  if (s.kind === "derive") return { kind: s.kind, on: s.on, name: s.name, op: s.op, a: s.a, b: s.b };
  if (s.kind === "summarize") return { kind: s.kind, on: s.on, by: s.by, fn: s.fn, field: s.field };
  if (s.kind === "sort") return { kind: s.kind, on: s.on, field: s.field, dir: s.dir };
  return { kind: s.kind, on: s.on, n: s.n };
};
const pipelineCacheKey = (datasetId, steps) => JSON.stringify([datasetId, steps.map(semanticStep)]);

function compilePipelineSQL(datasetId, steps) {
  const dataset = DATASETS[datasetId];
  let fields = dataset.fields.map((field) => ({ ...field }));
  const ctes = [`p0 AS (SELECT * FROM ${quoteIdent(datasetId)})`];
  let previous = "p0";
  let index = 0;
  let err = null;
  const add = (sql) => {
    const name = "p" + ++index;
    ctes.push(`${name} AS (${sql})`);
    previous = name;
  };
  const fieldType = (name) => fields.find((field) => field.name === name)?.type;

  for (const step of steps) {
    if (!step.on) continue;

    if (step.kind === "filter") {
      const type = fieldType(step.field);
      if (!type) { err = "filter refers to missing field " + step.field; continue; }
      if (!FOPS.includes(step.op)) { err = "filter uses an unsupported operator"; continue; }
      if (step.value === "" || step.value == null) continue;
      const operator = step.op === "≠" ? "<>" : step.op === ">" ? ">" : step.op === "<" ? "<" : "=";
      const numericComparison = type === "q" || operator === ">" || operator === "<";
      const numeric = Number(step.value);
      if (numericComparison && !Number.isFinite(numeric)) {
        add(`SELECT * FROM ${previous} WHERE ${operator === "<>" ? "TRUE" : "FALSE"}`);
        continue;
      }
      const right = numericComparison ? String(numeric) : quoteString(step.value);
      const left = numericComparison
        ? `try_cast(${quoteIdent(step.field)} AS DOUBLE)`
        : quoteIdent(step.field);
      add(`SELECT * FROM ${previous} WHERE ${left} ${operator} ${right}`);
      continue;
    }

    if (step.kind === "derive") {
      const target = String(step.name || "derived");
      const aExists = Boolean(fieldType(step.a));
      const bExists = step.op === "log10" || Boolean(fieldType(step.b));
      if (!DOPS.includes(step.op)) { err = "derive uses an unsupported operator"; continue; }
      if (!aExists || !bExists) { err = "derive refers to a missing field"; continue; }
      const a = `try_cast(${quoteIdent(step.a)} AS DOUBLE)`;
      const b = step.op !== "log10" ? `try_cast(${quoteIdent(step.b)} AS DOUBLE)` : "NULL::DOUBLE";
      const arithmetic = step.op === "log10" ? null : step.op;
      const expression = step.op === "log10"
        ? `CASE WHEN ${a} > 0 THEN log10(${a}) ELSE NULL END`
        : arithmetic === "/"
          ? `${a} / NULLIF(${b}, 0)`
          : arithmetic ? `${a} ${arithmetic} ${b}` : "NULL::DOUBLE";
      const rounded = `round(${expression}, 3)`;
      const projection = fieldType(target)
        ? `* REPLACE (${rounded} AS ${quoteIdent(target)})`
        : `*, ${rounded} AS ${quoteIdent(target)}`;
      add(`SELECT * FROM (SELECT ${projection} FROM ${previous}) AS derived WHERE ${quoteIdent(target)} IS NOT NULL`);
      fields = [...fields.filter((field) => field.name !== target), { name: target, type: "q" }];
      continue;
    }

    if (step.kind === "summarize") {
      const byType = fieldType(step.by);
      const valueType = fieldType(step.field);
      if (!AGGS.includes(step.fn)) {
        err = "summarize uses an unsupported aggregate";
        continue;
      }
      if (!byType || (step.fn !== "count" && !valueType)) {
        err = "summarize refers to a missing field";
        continue;
      }
      const output = aggName(step.fn, step.field);
      const aggregateFunction = step.fn === "mean" ? "avg" : step.fn;
      const aggregate = step.fn === "count"
        ? "count(*)"
        : `${aggregateFunction}(try_cast(${quoteIdent(step.field)} AS DOUBLE))`;
      const projectedAggregate = step.fn === "count" ? aggregate : `round(${aggregate}, 3)`;
      add(`SELECT ${quoteIdent(step.by)}, ${projectedAggregate} AS ${quoteIdent(output)} FROM ${previous} GROUP BY ${quoteIdent(step.by)}`);
      fields = [{ name: step.by, type: byType }, { name: output, type: "q" }];
      continue;
    }

    if (step.kind === "sort") {
      const type = fieldType(step.field);
      if (!type) { err = "sort refers to missing field " + step.field; continue; }
      const order = step.dir === "asc" ? "ASC" : "DESC";
      const expression = type === "q"
        ? `try_cast(${quoteIdent(step.field)} AS DOUBLE)`
        : quoteIdent(step.field);
      add(`SELECT * FROM ${previous} ORDER BY ${expression} ${order} NULLS LAST`);
      continue;
    }

    if (step.kind === "limit") {
      const count = Math.max(1, Math.trunc(Number(step.n) || 10));
      add(`SELECT * FROM ${previous} LIMIT ${count}`);
    }
  }

  return {
    sql: `WITH\n  ${ctes.join(",\n  ")}\nSELECT * FROM ${previous}`,
    fields,
    err,
  };
}

function normalizeDuckValue(value) {
  if (typeof value === "bigint") {
    const numeric = Number(value);
    return Number.isSafeInteger(numeric) ? numeric : value.toString();
  }
  if (value instanceof Date) return value.toISOString();
  if (ArrayBuffer.isView(value)) return Array.from(value);
  return value;
}

function arrowTableToRows(table) {
  const names = table?.schema?.fields?.map((field) => field.name) || [];
  return table.toArray().map((row) => {
    const source = typeof row?.toJSON === "function" ? row.toJSON() : row;
    const out = {};
    names.forEach((name) => { out[name] = normalizeDuckValue(source[name]); });
    return out;
  });
}

class FrontendQueryEngine {
  constructor() {
    this.status = "idle";
    this.error = null;
    this.lastMs = null;
    this.cache = new Map();
    this.fallbackCache = new Map();
    this.failed = new Map();
    this.pending = new Map();
    this.subscribers = new Set();
    this.revision = 0;
    this.connection = null;
    this.database = null;
    this.worker = null;
    this.initializing = null;
    this.queue = Promise.resolve();
    this.emitQueued = false;
  }

  subscribe(fn) { this.subscribers.add(fn); return () => this.subscribers.delete(fn); }
  snapshot() {
    return {
      status: this.status,
      error: this.error,
      lastMs: this.lastMs,
      cached: this.cache.size,
      pending: this.pending.size,
    };
  }
  emitSoon() {
    if (this.emitQueued) return;
    this.emitQueued = true;
    Promise.resolve().then(() => {
      this.emitQueued = false;
      this.subscribers.forEach((fn) => fn());
    });
  }
  remember(map, key, value, limit = QUERY_CACHE_LIMIT) {
    if (map.has(key)) map.delete(key);
    map.set(key, value);
    while (map.size > limit) map.delete(map.keys().next().value);
  }

  ensureReady() {
    if (this.connection || this.status === "fallback") return Promise.resolve(this.connection);
    if (this.initializing) return this.initializing;
    if (typeof window === "undefined" || typeof Worker === "undefined") return Promise.resolve(null);

    this.status = "loading";
    this.emitSoon();
    this.initializing = this.initialize().catch((error) => {
      this.status = "fallback";
      this.error = error instanceof Error ? error.message : String(error);
      this.connection = null;
      this.emitSoon();
      return null;
    });
    return this.initializing;
  }

  async initialize() {
    const duckdb = await import("@duckdb/duckdb-wasm");
    const configured = (globalThis as any).__PBUI_DUCKDB_BUNDLES__;
    const bundles = configured || duckdb.getJsDelivrBundles();
    const bundle = await duckdb.selectBundle(bundles);
    if (!bundle.mainWorker || !bundle.mainModule) throw new Error("No compatible DuckDB-Wasm bundle was found");

    /* CDN workers need a same-origin Blob bootstrap. A supplied bundle is
       assumed to be self-hosted and can be constructed directly, which also
       avoids a blob-worker requirement under a stricter CSP. */
    const workerURL = configured
      ? bundle.mainWorker
      : URL.createObjectURL(new Blob([
        `importScripts(${JSON.stringify(bundle.mainWorker)});`,
      ], { type: "text/javascript" }));
    try {
      this.worker = new Worker(workerURL);
      const logger = new duckdb.ConsoleLogger();
      this.database = new duckdb.AsyncDuckDB(logger, this.worker);
      await this.database.instantiate(bundle.mainModule, bundle.pthreadWorker);
      this.connection = await this.database.connect();
    } finally {
      if (!configured) URL.revokeObjectURL(workerURL);
    }

    for (const dataset of Object.values(DATASETS)) {
      const fileName = `pbui-${dataset.id}.json`;
      await this.database.registerFileText(fileName, JSON.stringify(dataset.rows));
      await this.connection.insertJSONFromPath(fileName, { schema: "main", name: dataset.id });
    }

    this.status = "ready";
    this.error = null;
    this.emitSoon();
    return this.connection;
  }

  request(key, compiled) {
    if (this.cache.has(key) || this.failed.has(key) || this.pending.has(key) || this.status === "fallback") return;
    this.pending.set(key, true);
    this.ensureReady().then((connection) => {
      if (!connection) {
        this.pending.delete(key);
        this.emitSoon();
        return;
      }
      this.queue = this.queue.then(() => this.run(key, compiled));
    });
  }

  async run(key, compiled) {
    const started = typeof performance !== "undefined" ? performance.now() : Date.now();
    try {
      const result = await this.connection.query(compiled.sql);
      const elapsed = (typeof performance !== "undefined" ? performance.now() : Date.now()) - started;
      const value = {
        rows: arrowTableToRows(result),
        fields: compiled.fields,
        err: compiled.err,
        source: "duckdb",
        revision: ++this.revision,
        cacheKey: key,
      };
      this.lastMs = elapsed;
      this.error = null;
      this.remember(this.cache, key, value);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      this.error = "Last DuckDB query failed: " + message;
      this.remember(this.failed, key, message);
    } finally {
      this.pending.delete(key);
      this.emitSoon();
    }
  }

  evaluate(datasetId, steps) {
    const key = pipelineCacheKey(datasetId, steps);
    const cached = this.cache.get(key);
    if (cached) {
      this.remember(this.cache, key, cached);
      return cached;
    }

    let fallback = this.fallbackCache.get(key);
    if (!fallback) {
      fallback = {
        ...evaluateJS(datasetId, steps),
        source: "javascript",
        revision: 0,
        cacheKey: key,
      };
      this.remember(this.fallbackCache, key, fallback);
    }

    const compiled = compilePipelineSQL(datasetId, steps);
    this.request(key, compiled);
    return fallback;
  }
}

const queryEngine = new FrontendQueryEngine();
const evaluate = (datasetId, steps) => queryEngine.evaluate(datasetId, steps);

function ComputeBadge() {
  const state = queryEngine.snapshot();
  const label = state.status === "ready"
    ? `DuckDB · ${state.lastMs == null ? "ready" : state.lastMs.toFixed(1) + " ms"}`
    : state.status === "loading"
      ? "DuckDB · starting"
      : state.status === "fallback"
        ? "JavaScript fallback"
        : "DuckDB · queued";
  const title = state.status === "fallback"
    ? `DuckDB could not start; the local JavaScript evaluator remains active. ${state.error || ""}`
    : `${state.cached} cached quer${state.cached === 1 ? "y" : "ies"}${state.pending ? ` · ${state.pending} pending` : ""}${state.error ? ` · ${state.error}` : ""}`;
  return (
    <span title={title} style={{ border: "1px solid " + C.line, background: C.pane, color: state.status === "fallback" ? C.red : C.faint, padding: "2px 6px", fontSize: 9, lineHeight: 1.2, whiteSpace: "nowrap" }}>
      {label}
    </span>
  );
}

const stepLabel = (s) => {
  if (s.kind === "filter") return "filter " + s.field + " " + s.op + " " + s.value;
  if (s.kind === "derive") return "derive " + s.name + " = " + (s.op === "log10" ? "log10(" + s.a + ")" : s.a + " " + s.op + " " + s.b);
  if (s.kind === "summarize") return "group " + s.by + " → " + aggName(s.fn, s.field);
  if (s.kind === "sort") return "sort " + s.field + " " + (s.dir === "asc" ? "↑" : "↓");
  return "limit " + s.n;
};

/* ============================================================
   WORLD — shared state: N chart documents + snapshots
   a DOCUMENT (α, β, γ …) is a live chart: its own pipeline,
   encoding, geom, scale. doc-bound tiles are views onto one.
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
  constructor() {
    this.notify = null;
    this.trace = [];
    this.docs = [];
    this.activeId = null;
    this.snaps = [];
    this.pins = [null, null];
    this.watch = [{ id: ++notec, ptype: "dataset", value: "seabirds" }, { id: ++notec, ptype: "field", value: "mass_g" }];
    /* seed two documents so the multi-chart story is visible on load */
    const a = this.newDoc("seabirds", true);
    const b = this.newDoc("climate", true);
    b.chart.mapping = { x: "month", y: "temp_c", color: "city", size: null, facet: null };
    b.chart.geom = "line";
    this.activeId = a.id;
    this.seedSnaps();
    this.trace = [];
    this.inspected = { title: "<dataset> seabirds", value: describeDataset("seabirds") };
  }
  bump() { this.notify && this.notify(); }
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
    const d = { id: "d" + ++docc, name: DOC_NAMES[(docc - 1) % DOC_NAMES.length] + (docc > DOC_NAMES.length ? "'" : ""), chart: defaultChart(datasetId || "seabirds") };
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
    if (this.docs.length < 2) return; /* keep at least one */
    const d = this.doc(id); if (!d) return;
    this.docs = this.docs.filter((x) => x.id !== d.id);
    if (this.activeId === d.id) this.activeId = this.docs[0].id;
    this.log("doc_removed", { chart: d.name, note: "tiles that showed it fall back to " + this.active().name });
  }

  /* ---- per-document chart mutation (docId first; falls back to active) ---- */
  setDataset(docId, id) {
    const d = this.doc(docId); if (!d || d.chart.datasetId === id) return;
    d.chart = defaultChart(id);
    this.log("source_set", { chart: d.name, dataset: id, note: "pipeline reset, default encoding inferred" });
  }
  addStep(docId, step) { const d = this.doc(docId); d.chart.steps.push(step); this.log("step_added", { chart: d.name, step: stepLabel(step) }); }
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
  filterToCat(docId, field, value, keep) {
    this.addStep(docId, mkStep("filter", { field, op: keep ? "=" : "≠", value: String(value) }));
  }
  /* find which document owns a step (object menus don't know) */
  docOfStep(stepId) { return this.docs.find((d) => d.chart.steps.some((s) => s.id === stepId)); }

  /* ---- snapshots ---- */
  snapshot(docId, name) {
    const d = this.doc(docId);
    const s = { id: "snap" + ++snapc, name: name || d.name + "-" + snapc, chart: cloneChart(d.chart), at: new Date().toLocaleTimeString() };
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

  seedSnaps() {
    /* two authored example snapshots so the gallery starts alive */
    const c1 = defaultChart("climate");
    c1.mapping = { x: "month", y: "temp_c", color: "city", size: null, facet: null };
    c1.geom = "line";
    this.snaps.push({ id: "snap" + ++snapc, name: "city-temps", chart: c1, at: "seed" });
    const c2 = defaultChart("engines");
    c2.steps = [mkStep("summarize", { by: "origin", field: "mpg", fn: "mean" })];
    c2.mapping = { x: "origin", y: "mean_mpg", color: "origin", size: null, facet: null };
    c2.geom = "bar";
    this.snaps.push({ id: "snap" + ++snapc, name: "mpg-by-origin", chart: c2, at: "seed" });
  }
}

const FIELD_STATS_CACHE_LIMIT = 160;
const fieldStatsCache = new Map();

function rememberFieldStats(key, value) {
  if (fieldStatsCache.has(key)) fieldStatsCache.delete(key);
  fieldStatsCache.set(key, value);
  while (fieldStatsCache.size > FIELD_STATS_CACHE_LIMIT) fieldStatsCache.delete(fieldStatsCache.keys().next().value);
  return value;
}

function fieldStats(datasetId, steps, name) {
  const evaluation = evaluate(datasetId, steps);
  const key = `${evaluation.cacheKey}:${evaluation.revision}:${name}`;
  if (fieldStatsCache.has(key)) {
    const cached = fieldStatsCache.get(key);
    fieldStatsCache.delete(key);
    fieldStatsCache.set(key, cached);
    return cached;
  }

  const field = evaluation.fields.find((item) => item.name === name);
  if (!field) return rememberFieldStats(key, null);

  if (field.type === "q") {
    let n = 0;
    let mean = 0;
    let m2 = 0;
    let min = Infinity;
    let max = -Infinity;
    for (const row of evaluation.rows) {
      const value = Number(row[name]);
      if (!Number.isFinite(value)) continue;
      n += 1;
      const delta = value - mean;
      mean += delta / n;
      m2 += delta * (value - mean);
      if (value < min) min = value;
      if (value > max) max = value;
    }
    return rememberFieldStats(key, {
      type: "quantitative",
      n,
      min: n ? +min.toFixed(2) : null,
      max: n ? +max.toFixed(2) : null,
      mean: n ? +mean.toFixed(2) : null,
      sd: n ? +Math.sqrt(m2 / n).toFixed(2) : null,
    });
  }

  const levels = {};
  let n = 0;
  for (const row of evaluation.rows) {
    const value = String(row[name]);
    levels[value] = (levels[value] || 0) + 1;
    n += 1;
  }
  return rememberFieldStats(key, {
    type: field.type === "t" ? "temporal" : "nominal",
    n,
    distinct: Object.keys(levels).length,
    levels,
  });
}
function describeDataset(id) {
  const d = DATASETS[id];
  return { presentationType: "dataset", name: d.name, rows: d.rows.length, note: d.note, fields: Object.fromEntries(d.fields.map((f) => [f.name, TYPE_LABEL[f.type]])) };
}

/* ============================================================
   PLOT ENGINE — pure spec → drawable geometry
   builds panels (facets), shared scales, marks, ticks, legend.
   returned marks carry the source row so views can wrap them
   in <datum> presentations.
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

const PLOT_CACHE_LIMIT = 160;
const plotCache = new Map();

function rememberPlot(key, value) {
  if (plotCache.has(key)) plotCache.delete(key);
  plotCache.set(key, value);
  while (plotCache.size > PLOT_CACHE_LIMIT) plotCache.delete(plotCache.keys().next().value);
  return value;
}
function readPlot(key) {
  const value = plotCache.get(key);
  if (!value) return null;
  plotCache.delete(key);
  plotCache.set(key, value);
  return value;
}
function numericExtent(rows, field) {
  let lo = Infinity;
  let hi = -Infinity;
  let count = 0;
  for (const row of rows) {
    const value = Number(row[field]);
    if (!Number.isFinite(value)) continue;
    if (value < lo) lo = value;
    if (value > hi) hi = value;
    count += 1;
  }
  return count ? { lo, hi, count } : null;
}
function distinctFieldValues(rows, field, limit = Infinity) {
  const values = [];
  const seen = new Set();
  for (const row of rows) {
    const value = String(row[field]);
    if (seen.has(value)) continue;
    seen.add(value);
    values.push(value);
    if (values.length >= limit) break;
  }
  return values;
}
function evenlySample(rows, limit) {
  if (rows.length <= limit) return rows;
  if (limit <= 1) return [rows[0]];
  const sampled = [];
  const step = (rows.length - 1) / (limit - 1);
  for (let i = 0; i < limit; i++) sampled.push(rows[Math.round(i * step)]);
  return sampled;
}
/* Largest-Triangle-Three-Buckets keeps the shape of dense series while
   bounding path/circle count to the available horizontal resolution. */
function decimateSeries(rows, threshold, xValue, yValue) {
  if (threshold >= rows.length || threshold < 3) return rows;
  const sampled = [rows[0]];
  const every = (rows.length - 2) / (threshold - 2);
  let anchor = 0;

  for (let i = 0; i < threshold - 2; i++) {
    let averageStart = Math.floor((i + 1) * every) + 1;
    let averageEnd = Math.floor((i + 2) * every) + 1;
    averageEnd = Math.min(averageEnd, rows.length);
    if (averageStart >= averageEnd) averageStart = Math.max(0, averageEnd - 1);

    let averageX = 0, averageY = 0;
    const averageLength = Math.max(1, averageEnd - averageStart);
    for (let j = averageStart; j < averageEnd; j++) {
      averageX += xValue(rows[j], j);
      averageY += yValue(rows[j], j);
    }
    averageX /= averageLength;
    averageY /= averageLength;

    const rangeStart = Math.floor(i * every) + 1;
    const rangeEnd = Math.min(Math.floor((i + 1) * every) + 1, rows.length - 1);
    const anchorX = xValue(rows[anchor], anchor);
    const anchorY = yValue(rows[anchor], anchor);
    let maxArea = -1;
    let nextAnchor = rangeStart;

    for (let j = rangeStart; j < rangeEnd; j++) {
      const area = Math.abs(
        (anchorX - averageX) * (yValue(rows[j], j) - anchorY)
        - (anchorX - xValue(rows[j], j)) * (averageY - anchorY)
      );
      if (area > maxArea) { maxArea = area; nextAnchor = j; }
    }
    sampled.push(rows[nextAnchor]);
    anchor = nextAnchor;
  }
  sampled.push(rows[rows.length - 1]);
  return sampled;
}

function buildPlot(chart, W, H, mini) {
  const evaluation = evaluate(chart.datasetId, chart.steps);
  const { rows, fields, err } = evaluation;
  const plotKey = JSON.stringify([
    evaluation.cacheKey,
    evaluation.revision,
    W,
    H,
    Boolean(mini),
    chart.geom,
    chart.yScale,
    SLOTS.map((slot) => chart.mapping[slot] || null),
  ]);
  const cached = readPlot(plotKey);
  if (cached) return cached;
  const finish = (plot) => rememberPlot(plotKey, plot);

  const ftype = Object.fromEntries(fields.map((field) => [field.name, field.type]));
  const mapping = chart.mapping;
  const geom = chart.geom;
  const problems = [];
  if (err) problems.push(err);
  for (const slot of SLOTS) {
    if (mapping[slot] && !ftype[mapping[slot]]) problems.push(slot + " ↦ " + mapping[slot] + " is not in the pipeline output");
  }
  if (!mapping.x || !ftype[mapping.x]) problems.push("map x to a field");
  if (!mapping.y || !ftype[mapping.y]) problems.push("map y to a field");
  if (rows.length === 0) problems.push("pipeline output is empty — loosen or disable a filter");
  if (problems.length) return finish({ problems, rowsOut: rows.length, markStats: { input: 0, rendered: 0 } });

  const xType = ftype[mapping.x];
  const yType = ftype[mapping.y];
  if (geom === "bar" && xType === "q") problems.push("bar charts need a nominal or temporal x; group and summarize first, or remap x");
  if (yType !== "q") problems.push("y must be quantitative for geom_" + geom);
  const yExtent = numericExtent(rows, mapping.y);
  const xExtent = xType === "q" ? numericExtent(rows, mapping.x) : null;
  if (!yExtent) problems.push("y contains no finite values after the pipeline");
  if (xType === "q" && !xExtent) problems.push("x contains no finite values after the pipeline");
  if (problems.length) return finish({ problems, rowsOut: rows.length, markStats: { input: rows.length, rendered: 0 } });

  let facetValues = [null];
  let facetStats = null;
  if (mapping.facet && ftype[mapping.facet] !== "q") {
    const allFacets = distinctFieldValues(rows, mapping.facet);
    facetValues = allFacets.slice(0, 6);
    if (allFacets.length > facetValues.length) facetStats = { input: allFacets.length, rendered: facetValues.length };
  }
  const facetCount = facetValues.length;
  const columns = facetCount <= 1 ? 1 : facetCount === 2 ? 2 : facetCount <= 4 ? 2 : 3;
  const panelRows = Math.ceil(facetCount / columns);

  let colorMode = null;
  let categories = [];
  let colorRange = null;
  let colorStats = null;
  if (mapping.color) {
    if (ftype[mapping.color] === "q") {
      const extent = numericExtent(rows, mapping.color);
      colorMode = "q";
      colorRange = extent ? { lo: extent.lo, hi: extent.hi } : { lo: 0, hi: 1 };
    } else {
      colorMode = "n";
      const allCategories = distinctFieldValues(rows, mapping.color);
      categories = allCategories.slice(0, 8);
      if (allCategories.length > categories.length) colorStats = { input: allCategories.length, rendered: categories.length };
    }
  }
  const colorOf = (row) => {
    if (!colorMode) return C.blue;
    if (colorMode === "q") {
      const t = colorRange.hi > colorRange.lo ? (+row[mapping.color] - colorRange.lo) / (colorRange.hi - colorRange.lo) : 0.5;
      return hexLerp(C.blue, C.red, clamp(t, 0, 1));
    }
    const index = categories.indexOf(String(row[mapping.color]));
    return index < 0 ? C.faint : CAT_TONES[index % CAT_TONES.length];
  };

  let xCategories = null;
  let xIndex = null;
  let xLo = 0, xHi = 1;
  if (xType === "q") {
    xLo = xExtent.lo;
    xHi = xExtent.hi;
    if (xLo === xHi) { xLo -= 1; xHi += 1; }
    const pad = (xHi - xLo) * 0.05;
    xLo -= pad;
    xHi += pad;
  } else {
    /* Preserve pipeline order: a sort step should also order categorical bars. */
    xCategories = distinctFieldValues(rows, mapping.x);
    xIndex = new Map(xCategories.map((value, index) => [value, index]));
  }

  let yLo = yExtent.lo, yHi = yExtent.hi;
  const log = chart.yScale === "log" && yLo > 0;
  if ((geom === "bar" || geom === "area") && !log) {
    yLo = Math.min(0, yLo);
    yHi = Math.max(0, yHi);
  }
  if (yLo === yHi) { yLo -= 1; yHi += 1; }
  if (!log) {
    const pad = (yHi - yLo) * 0.06;
    yHi += pad;
    if (!(geom === "bar" || geom === "area")) yLo -= pad;
  }
  const log10 = (value) => Math.log10(value);

  let sizeLo = 0, sizeHi = 1;
  if (mapping.size && ftype[mapping.size] === "q") {
    const extent = numericExtent(rows, mapping.size);
    if (extent) { sizeLo = extent.lo; sizeHi = extent.hi; }
  }
  const radiusOf = (row) => {
    if (!mapping.size || ftype[mapping.size] !== "q") return mini ? 2.4 : 4;
    const t = sizeHi > sizeLo ? (+row[mapping.size] - sizeLo) / (sizeHi - sizeLo) : 0.5;
    return (mini ? 1.6 : 3) + Math.sqrt(clamp(t, 0, 1)) * (mini ? 4 : 8);
  };

  const legendW = colorMode && !mini ? 92 : 0;
  const padL = mini ? 26 : 40;
  const padB = mini ? 14 : 24;
  const padT = facetCount > 1 ? (mini ? 12 : 16) : mini ? 4 : 8;
  const padR = mini ? 4 : 8;
  const gapX = mini ? 6 : 12;
  const gapY = mini ? 6 : 14;
  const plotW = W - legendW;
  const panelW = (plotW - padL - padR - gapX * (columns - 1)) / columns;
  const panelH = (H - padT * panelRows - padB - gapY * (panelRows - 1)) / panelRows;

  const scaleX = (value) => {
    if (xType === "q") return ((+value - xLo) / (xHi - xLo)) * panelW;
    const index = xIndex.get(String(value)) ?? 0;
    return ((index + 0.5) / Math.max(1, xCategories.length)) * panelW;
  };
  const scaleY = (value) => {
    if (log) return (1 - (log10(+value) - log10(yLo)) / (log10(yHi) - log10(yLo))) * panelH;
    return (1 - (+value - yLo) / (yHi - yLo)) * panelH;
  };

  const yTicks = log
    ? niceTicks(log10(yLo), log10(yHi), 4).map((exponent) => ({ v: Math.pow(10, exponent), label: fmt(Math.pow(10, exponent)) }))
    : niceTicks(yLo, yHi, mini ? 3 : 5).map((value) => ({ v: value, label: fmt(value) }));
  const xTicks = xType === "q"
    ? niceTicks(xLo, xHi, mini ? 3 : 5).map((value) => ({ pos: scaleX(value), label: fmt(value) }))
    : xCategories.map((category, index) => ({ pos: scaleX(category), label: category, index })).filter((tick, index) => {
      const max = mini ? 4 : Math.max(3, Math.floor(panelW / 34));
      return index % Math.max(1, Math.ceil(xCategories.length / max)) === 0;
    });

  let inputMarks = 0;
  let renderedMarks = 0;
  const pointLimit = mini ? Math.max(240, Math.floor(panelW * 4)) : Math.min(8000, Math.max(1200, Math.floor(panelW * 12)));
  const seriesBudget = mini
    ? Math.max(120, Math.floor(panelW * 1.5))
    : Math.min(8000, Math.max(600, Math.floor(panelW * 4)));
  const barLimit = mini ? 480 : 2600;
  const drawable = (row) => Number.isFinite(+row[mapping.y]) && (xType !== "q" || Number.isFinite(+row[mapping.x]));

  const panels = facetValues.map((facetValue, panelIndex) => {
    const column = panelIndex % columns;
    const panelRow = Math.floor(panelIndex / columns);
    const x0 = padL + column * (panelW + gapX);
    const y0 = padT + panelRow * (panelH + gapY + (facetCount > 1 ? padT : 0));
    const panelData = facetValue === null ? rows : rows.filter((row) => String(row[mapping.facet]) === facetValue);
    const marks = [];
    const baseline = log ? panelH : scaleY(clamp(0, yLo, yHi));

    if (geom === "point") {
      const candidates = panelData.filter(drawable);
      const shown = evenlySample(candidates, pointLimit);
      inputMarks += candidates.length;
      renderedMarks += shown.length;
      shown.forEach((row) => {
        marks.push({ kind: "c", x: scaleX(row[mapping.x]), y: scaleY(row[mapping.y]), r: radiusOf(row), fill: colorOf(row), row });
      });
    } else if (geom === "line" || geom === "area") {
      const groups = new Map();
      panelData.filter(drawable).forEach((row) => {
        const key = colorMode === "n" ? String(row[mapping.color]) : "·";
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(row);
      });
      const groupEntries = [...groups.entries()];
      const shownGroups = evenlySample(groupEntries, mini ? 8 : 24);
      const perSeriesLimit = Math.max(3, Math.floor(seriesBudget / Math.max(1, shownGroups.length)));
      inputMarks += groupEntries.reduce((total, [, group]) => total + group.length, 0);
      shownGroups.forEach(([key, group]) => {
        const sorted = [...group].sort((a, b) => xType === "q"
          ? +a[mapping.x] - +b[mapping.x]
          : (xIndex.get(String(a[mapping.x])) ?? 0) - (xIndex.get(String(b[mapping.x])) ?? 0));
        const reduced = decimateSeries(
          sorted,
          perSeriesLimit,
          (row, index) => xType === "q" ? +row[mapping.x] : (xIndex.get(String(row[mapping.x])) ?? index),
          (row) => +row[mapping.y],
        );
        renderedMarks += reduced.length;
        const points = reduced.map((row) => [scaleX(row[mapping.x]), scaleY(row[mapping.y]), row]);
        if (points.length < 2) {
          points.forEach(([x, y, row]) => marks.push({ kind: "c", x, y, r: radiusOf(row), fill: colorOf(row), row }));
          return;
        }
        const tone = colorMode === "n"
          ? CAT_TONES[Math.max(0, categories.indexOf(key)) % CAT_TONES.length]
          : colorMode === "q" ? C.faint : C.blue;
        const path = points.map(([x, y], index) => (index ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" ");
        if (geom === "area") {
          const areaPath = path
            + " L" + points[points.length - 1][0].toFixed(1) + " " + baseline.toFixed(1)
            + " L" + points[0][0].toFixed(1) + " " + baseline.toFixed(1) + " Z";
          marks.push({ kind: "p", d: areaPath, fill: tone, fillOpacity: 0.25, stroke: "none" });
        }
        marks.push({ kind: "p", d: path, stroke: tone, fill: "none" });
        points.forEach(([x, y, row]) => marks.push({ kind: "c", x, y, r: mini ? 1.8 : 3.2, fill: colorOf(row), row }));
      });
    } else if (geom === "bar") {
      const candidates = panelData.filter(drawable);
      const groups = new Map();
      candidates.forEach((row) => {
        const key = String(row[mapping.x]);
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(row);
      });
      const groupEntries = [...groups.entries()];
      const shownGroups = evenlySample(groupEntries, Math.min(groupEntries.length, barLimit));
      const perGroupLimit = Math.max(1, Math.floor(barLimit / Math.max(1, shownGroups.length)));
      const band = panelW / Math.max(1, xCategories.length);
      inputMarks += candidates.length;
      shownGroups.forEach(([key, group]) => {
        const shown = evenlySample(group, perGroupLimit);
        renderedMarks += shown.length;
        const center = scaleX(key);
        const width = (band * 0.72) / Math.max(1, shown.length);
        shown.forEach((row, index) => {
          const yValue = scaleY(row[mapping.y]);
          const top = Math.min(yValue, baseline);
          const height = Math.abs(baseline - yValue);
          marks.push({ kind: "r", x: center - (band * 0.72) / 2 + index * width, y: top, w: Math.max(1, width - 1), h: Math.max(0.5, height), fill: colorOf(row), row });
        });
      });
    }
    return { x0, y0, w: panelW, h: panelH, title: facetValue, marks };
  });

  const legend = colorMode === "n"
    ? categories.map((category, index) => ({ label: category, value: category, color: CAT_TONES[index % CAT_TONES.length] }))
    : colorMode === "q"
      ? [{ label: fmt(colorRange.lo), color: C.blue }, { label: fmt(colorRange.hi), color: C.red }]
      : [];

  return finish({
    panels,
    legend,
    colorMode,
    colorField: mapping.color,
    W,
    H,
    padL,
    padB,
    legendW,
    yTicks: yTicks.map((tick) => ({ pos: scaleY(tick.v), label: tick.label })),
    xTicks,
    rowsOut: rows.length,
    markStats: { input: inputMarks, rendered: renderedMarks },
    facetStats,
    colorStats,
    querySource: evaluation.source,
    problems: [],
  });
}


/* ============================================================
   WINDOW MANAGER — split tree + workspaces (from the shell)
   ============================================================ */
let idc = 1;
const nid = () => "n" + idc++;
/* doc-bound apps show ONE chart document; the leaf remembers which */
const DOC_APPS = ["chart", "table", "pipeline", "encode"];
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
function countLeaves(node) { return node.type === "leaf" ? 1 : countLeaves(node.a) + countLeaves(node.b); }
function cloneTree(node) {
  return node.type === "leaf" ? { ...node, id: nid() } : { ...node, id: nid(), a: cloneTree(node.a), b: cloneTree(node.b) };
}
const SNAPS_R = [0.25, 1 / 3, 0.5, 2 / 3, 0.75];
const STICK = 0.022;
function snapFrac(f) { for (const s of SNAPS_R) if (Math.abs(f - s) < STICK) return { f: s, snapped: true }; return { f, snapped: false }; }

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
      <div style={{ display: "flex", alignItems: "center", gap: 6, background: app.color, borderBottom: "2px solid " + C.ink, padding: "2px 6px", flexShrink: 0 }}>
        <span onMouseDown={(e) => ui.wm.startDrag(leafNode.id, e)}
          onMouseEnter={() => ui.setMouseDoc("drag ⠿ — drop on a tile's CENTER to swap apps, or near an EDGE to split-dock there")} onMouseLeave={() => ui.setMouseDoc(null)}
          style={{ cursor: "grab", fontWeight: 700, userSelect: "none" }}>⠿</span>
        <P ptype="tile" value={leafNode.id} doc={"tile [" + app.title + (boundDoc ? " · " + boundDoc.name : "") + "] — split / close / swap"}>
          <b style={{ fontSize: 11, letterSpacing: "0.05em", textTransform: "uppercase" }}>{app.title}{boundDoc ? " · " + boundDoc.name : ""}</b>
        </P>
        <span style={{ flex: 1 }} />
        <select value={leafNode.app} onChange={(e) => ui.wm.setLeafApp(leafNode.id, e.target.value)} onMouseDown={(e) => e.stopPropagation()}
          style={{ border: "1px solid " + C.ink, background: C.pane, fontSize: 10, padding: "0 2px", fontFamily: "inherit" }}>
          {Object.entries(APPS).map(([id, a]) => <option key={id} value={id}>{a.title}</option>)}
        </select>
        <TBtn doc="split this tile: new tile to the RIGHT" onClick={() => ui.wm.splitLeaf(leafNode.id, "row")}>⬌</TBtn>
        <TBtn doc="split this tile: new tile BELOW" onClick={() => ui.wm.splitLeaf(leafNode.id, "col")}>⬍</TBtn>
        <TBtn doc="close this tile (its sibling absorbs the space)" disabled={!ui.wm.canClose} onClick={() => ui.wm.closeLeaf(leafNode.id)}>✕</TBtn>
      </div>
      <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}><Comp leafId={leafNode.id} docId={boundDoc ? boundDoc.id : null} /></div>
    </div>
  );
}

/* ============================================================
   SHARED UI BITS
   ============================================================ */
const AppBody = ({ children, style }) => (<div style={{ flex: 1, minHeight: 0, overflow: "auto", padding: "6px 8px", ...style }}>{children}</div>);
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
/* a <field> chip — the atom of the whole workbench */
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
/* a <doc> chip — a live chart document (α, β, …) */
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
/* strip shown atop every doc-bound tile: which document am I a view of? */
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
   CHART RENDERERS
   PlotSVG — interactive: marks are <datum> presentations,
             legend swatches are <cat> presentations.
   MiniPlot — inert thumbnail for the gallery / compare.
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
function AxisLabels({ plot, first, last }) {
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
function markKey(mk, i) { return mk.kind + i; }

function PlotSVG({ chart, W, H, docId }) {
  const plot = buildPlot(chart, W, H, false);
  if (plot.problems && plot.problems.length) {
    return (
      <div style={{ border: "2px dashed " + C.line, padding: 14, fontSize: 11.5, color: C.faint, lineHeight: 1.5 }}>
        <b style={{ color: C.ink }}>chart not drawable yet:</b>
        {plot.problems.map((p, i) => <div key={i}>· {p}</div>)}
      </div>
    );
  }
  const first = plot.panels[0];
  const mkDatum = (r) => ({ row: r, docId });
  const datumDoc = (r) => {
    const keys = Object.keys(r).slice(0, 3);
    return "datum " + keys.map((k) => k + "=" + fmt(r[k])).join(" · ") + "  — R: filter this chart's pipeline to it";
  };
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "flex-start", flexWrap: "wrap" }}>
      <svg role="img" aria-label={`${chart.geom} chart with ${plot.rowsOut} output rows`} preserveAspectRatio="xMidYMid meet" viewBox={"0 0 " + (W - plot.legendW) + " " + H} style={{ width: "100%", maxWidth: W - plot.legendW, display: "block" }}>
        {plot.panels.map((p, pi) => <PanelFrame key={pi} p={p} plot={plot} />)}
        <AxisLabels plot={plot} first={first} last={plot.panels[plot.panels.length - 1]} />
        {plot.panels.map((p, pi) => (
          <g key={"m" + pi}>
            {p.marks.map((mk, i) => {
              if (mk.kind === "p") return <path key={markKey(mk, i)} d={mk.d} transform={"translate(" + p.x0 + " " + p.y0 + ")"} fill={mk.fill || "none"} fillOpacity={mk.fillOpacity} stroke={mk.stroke} strokeWidth="2" />;
              if (mk.kind === "r") return (
                <P key={markKey(mk, i)} svg ptype="datum" value={mkDatum(mk.row)} doc={datumDoc(mk.row)}>
                  <rect x={p.x0 + mk.x} y={p.y0 + mk.y} width={mk.w} height={mk.h} fill={mk.fill} fillOpacity="0.75" stroke={C.ink} strokeWidth="0.8" style={{ cursor: "pointer" }} />
                </P>
              );
              return (
                <P key={markKey(mk, i)} svg ptype="datum" value={mkDatum(mk.row)} doc={datumDoc(mk.row)}>
                  <circle cx={p.x0 + mk.x} cy={p.y0 + mk.y} r={mk.r} fill={mk.fill} fillOpacity="0.72" stroke={C.ink} strokeWidth="0.8" style={{ cursor: "pointer" }} />
                </P>
              );
            })}
          </g>
        ))}
      </svg>
      {plot.legend.length > 0 && (
        <div style={{ minWidth: 86, display: "flex", flexDirection: "column", gap: 3 }}>
          <div style={{ fontSize: 9, fontWeight: 700, color: C.faint, letterSpacing: "0.06em" }}>{plot.colorField}</div>
          {plot.colorMode === "n" ? plot.legend.map((l) => (
            <P key={l.value} ptype="cat" value={{ field: plot.colorField, value: l.value, docId }}
              doc={"category " + plot.colorField + "=" + l.value + "  — R: keep / exclude via a filter step"}>
              <span style={{ display: "inline-flex", alignItems: "center", gap: 5, fontSize: 10.5, cursor: "pointer" }}>
                <span style={{ width: 11, height: 11, background: l.color, border: "1px solid " + C.ink, flexShrink: 0 }} />{l.label}
              </span>
            </P>
          )) : (
            <div style={{ fontSize: 10 }}>
              <div style={{ height: 10, width: 70, border: "1px solid " + C.ink, background: "linear-gradient(90deg," + C.blue + "," + C.red + ")" }} />
              <span>{plot.legend[0].label} … {plot.legend[1].label}</span>
            </div>
          )}
        </div>
      )}
      {plot.markStats && plot.markStats.input > plot.markStats.rendered && (
        <div style={{ flexBasis: "100%", color: C.faint, fontSize: 9.5, lineHeight: 1.35 }}>
          Rendering {plot.markStats.rendered.toLocaleString()} representative marks from {plot.markStats.input.toLocaleString()} rows. Domains and ticks use the full query result.
        </div>
      )}
      {plot.facetStats && (
        <div style={{ flexBasis: "100%", color: C.faint, fontSize: 9.5, lineHeight: 1.35 }}>
          Showing {plot.facetStats.rendered} of {plot.facetStats.input} facet values. Filter or regroup to inspect the remainder.
        </div>
      )}
      {plot.colorStats && (
        <div style={{ flexBasis: "100%", color: C.faint, fontSize: 9.5, lineHeight: 1.35 }}>
          The legend lists the first {plot.colorStats.rendered} of {plot.colorStats.input} color categories; remaining categories render in a neutral tone.
        </div>
      )}
    </div>
  );
}
function MiniPlot({ chart, W, H }) {
  const plot = buildPlot(chart, W, H, true);
  if (plot.problems && plot.problems.length) return <div style={{ width: W, height: H, border: "1px dashed " + C.line, fontSize: 9, color: C.faint, padding: 4 }}>not drawable</div>;
  return (
    <svg aria-hidden="true" preserveAspectRatio="xMidYMid meet" viewBox={"0 0 " + W + " " + H} style={{ width: W, height: H, display: "block" }}>
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
   APP · DATA BROWSER — datasets and their fields
   ============================================================ */
function DataApp() {
  const w = useUI().world;
  const act = w.active();
  return (
    <AppBody>
      <Hint>every dataset and field is a live presentation. L-click a dataset → source of the ACTIVE chart (<DocChip id={act.id} />). R-click a field → map it, filter on it, or inspect its distribution.</Hint>
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

/* ============================================================
   APP · TABLE — the pipeline's live output relation
   ============================================================ */
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
      {rows.length === 0 && <div style={{ color: C.red, fontSize: 11 }}>pipeline output is empty — a filter is probably too strict.</div>}
    </AppBody>
    </>
  );
}

/* ============================================================
   APP · PIPELINE — the tidyverse chain, each step live
   ============================================================ */
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
      const r = await ui.accept("field", "FILTER (chart " + d.name + ") — click the FIELD to filter on (any tile: browser, table header, chart legend…)");
      if (!r) return;
      const f = schema.find((x) => x.name === r.value);
      w.addStep(d.id, mkStep("filter", { field: r.value, op: f && f.type === "q" ? ">" : "=", value: "" }));
    } else if (kind === "derive") {
      w.addStep(d.id, mkStep("derive", { name: "ratio", a: qs[0] ? qs[0].name : "", op: "/", b: qs[1] ? qs[1].name : (qs[0] ? qs[0].name : "") }));
    } else if (kind === "summarize") {
      const r = await ui.accept("field", "GROUP BY (chart " + d.name + ") — click a nominal/temporal FIELD anywhere");
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
        <Hint>a tidyverse chain: each step is a &lt;step&gt; presentation — R-click to toggle / reorder / remove. ✓ toggles without deleting, so you can A/B a step.</Hint>
        <div style={{ display: "flex", gap: 6, alignItems: "baseline", marginBottom: 6 }}>
          <span style={{ fontSize: 10, color: C.faint }}>SOURCE</span>
          <DatasetChip id={c.datasetId} big docId={d.id} />
          <span style={{ color: C.faint, fontSize: 10 }}>{DATASETS[c.datasetId].rows.length} rows in</span>
        </div>
        {steps.map((s, i) => (
          <div key={s.id} style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 4, opacity: s.on ? 1 : 0.45 }}>
            <span style={{ color: C.faint, fontSize: 12 }}>{i === 0 ? "⊳" : "⊳"}</span>
            <span onClick={() => w.toggleStep(d.id, s.id)} title="toggle step" style={{ cursor: "pointer", border: "1px solid " + C.ink, width: 14, height: 14, display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 10, background: s.on ? C.sel : C.pane, flexShrink: 0 }}>{s.on ? "✓" : ""}</span>
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

/* ============================================================
   APP · ENCODING — aesthetic mappings + geom + scales
   ============================================================ */
function EncodeApp({ leafId, docId }) {
  const ui = useUI(); const w = ui.world;
  const d = w.doc(docId); const c = d.chart;
  const m = c.mapping;
  const schema = schemaAfter(c.datasetId, c.steps);
  const findT = (n) => { const f = schema.find((x) => x.name === n); return f ? f.type : null; };
  const slotDocs = { x: "position →", y: "position ↑ (quantitative)", color: "hue (nominal palette / quant ramp)", size: "mark radius (quantitative)", facet: "small multiples (nominal/temporal)" };
  return (
    <>
    <DocBar docId={d.id} leafId={leafId} />
    <AppBody>
      <Hint>the aesthetic mapping of the grammar: <b>slot ↦ field</b>. hit <b>⌖</b> then click any field chip in ANY tile — data browser, table header, pipeline out-schema.</Hint>
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
                  const r = await ui.accept("field", "MAP " + slot.toUpperCase() + " of chart " + d.name + " ↦ click a FIELD anywhere (Esc cancels)");
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
        {c.yScale === "log" && <span style={{ color: C.faint, fontSize: 9.5 }}>(falls back to linear if y ≤ 0)</span>}
      </div>
    </AppBody>
    </>
  );
}

/* ============================================================
   APP · CHART — the composed plot, fully live
   ============================================================ */
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
        <Hint>marks are &lt;datum&gt; presentations (L: inspect · R: filter THIS chart's pipeline to that datum's category). legend swatches are &lt;cat&gt; presentations — R-click to keep / exclude.</Hint>
        <PlotSVG chart={c} W={560} H={300} docId={d.id} />
      </AppBody>
    </>
  );
}

/* ============================================================
   APP · GALLERY — chart snapshots as first-class objects
   ============================================================ */
function GalleryApp() {
  const ui = useUI(); const w = ui.world;
  return (
    <>
      <div style={{ display: "flex", gap: 6, alignItems: "center", padding: "6px 8px 4px", flexShrink: 0 }}>
        <Btn tone={C.mustard} onClick={() => w.snapshot()}>⚑ snapshot active chart</Btn>
        <DocChip id={w.activeId} />
      </div>
      <AppBody style={{ paddingTop: 2 }}>
        <Hint>a snapshot freezes a whole pipeline + encoding as a frozen &lt;chart&gt; object. L-click a name → restore into the ACTIVE document. R-click → restore as a NEW document, pin to compare A/B, inspect its spec, delete.</Hint>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {w.snaps.map((s) => (
            <div key={s.id} style={{ border: "1px solid " + C.ink, padding: 5, background: C.pane }}>
              <div style={{ display: "flex", gap: 5, alignItems: "center", marginBottom: 3 }}>
                <P ptype="chart" value={s.id} onActivate={() => w.restoreSnap(s.id)} activateDoc={"restore into the ACTIVE document (" + w.active().name + ")"}
                  doc={"chart snapshot " + s.name + " (" + s.chart.datasetId + " · geom_" + s.chart.geom + ") — R: restore as new doc / pin / delete"}>
                  <b style={{ fontSize: 11, borderBottom: "1px dotted " + C.faint, cursor: "pointer" }}>{s.name}</b>
                </P>
                <span style={{ color: C.faint, fontSize: 9 }}>{s.at}</span>
                <span onClick={() => w.deleteSnap(s.id)} style={{ cursor: "pointer", color: C.red, fontWeight: 700 }} title="delete">×</span>
              </div>
              <MiniPlot chart={s.chart} W={190} H={112} />
              <div style={{ fontSize: 9, color: C.faint, marginTop: 2 }}>
                {s.chart.datasetId} ⊳ {s.chart.steps.filter((x) => x.on).length} steps · {s.chart.mapping.x}×{s.chart.mapping.y}
                {w.pins[0] === s.id && <b style={{ color: C.red }}> · pinned A</b>}{w.pins[1] === s.id && <b style={{ color: C.blue }}> · pinned B</b>}
              </div>
            </div>
          ))}
          {w.snaps.length === 0 && <div style={{ color: C.faint, fontSize: 11 }}>no snapshots yet.</div>}
        </div>
      </AppBody>
    </>
  );
}

/* ============================================================
   APP · COMPARE — two <chart> objects side by side
   ============================================================ */
function CompareApp() {
  const ui = useUI(); const w = ui.world;
  const pick = async (slot) => {
    const r = await ui.accept("chart", "COMPARE " + (slot === 0 ? "A" : "B") + " — click a CHART snapshot name in the gallery (Esc cancels)");
    if (r) w.pinSnap(slot, r.value);
  };
  const cell = (slot) => {
    const id = w.pins[slot];
    const s = w.snaps.find((x) => x.id === id);
    return (
      <div style={{ flex: 1, minWidth: 200, border: "1px dashed " + C.line, padding: 6 }}>
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
        {s && <MiniPlot chart={s.chart} W={250} H={150} />}
        {s && <div style={{ fontSize: 9.5, color: C.faint, marginTop: 3 }}>
          {s.chart.datasetId} ⊳ {s.chart.steps.filter((x) => x.on).map(stepLabel).join(" ⊳ ") || "(no steps)"}<br />
          geom_{s.chart.geom} · x↦{s.chart.mapping.x} y↦{s.chart.mapping.y}{s.chart.mapping.color ? " color↦" + s.chart.mapping.color : ""}{s.chart.mapping.facet ? " facet↦" + s.chart.mapping.facet : ""}
        </div>}
      </div>
    );
  };
  return (
    <AppBody>
      <Hint>side-by-side A/B of two snapshots. "accept…" then click any &lt;chart&gt; name — in the gallery, the watchlist, anywhere.</Hint>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>{cell(0)}{cell(1)}</div>
    </AppBody>
  );
}

/* ============================================================
   APP · INSPECTOR / WATCHLIST / TRACE / ABOUT / LAUNCHER
   ============================================================ */
function InspectorApp() {
  const w = useUI().world;
  return (
    <AppBody>
      <div style={{ fontWeight: 700, marginBottom: 4, borderBottom: "1px dashed " + C.line }}>{w.inspected.title}</div>
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
          const r = await ui.accept(["field", "dataset", "chart", "doc", "step", "datum", "cat"], "Click any field, dataset, chart doc, snapshot, step, datum or category — any tile — to watch it");
          if (r) w.watchAdd(r.ptype, r.value);
        }}>Watch… (accept anything)</Btn>
      </div>
      <Hint>watched objects stay LIVE — a watched field can still be mapped, filtered or inspected from here; a watched chart can be restored.</Hint>
      {w.watch.map((n) => (
        <div key={n.id} style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 4 }}>
          <span style={{ color: C.faint, fontSize: 9.5 }}>&lt;{n.ptype}&gt;</span>
          <Pres ptype={n.ptype} value={n.value} />
          <span onClick={() => w.watchRemove(n.id)} style={{ cursor: "pointer", color: C.red, fontWeight: 700, marginLeft: "auto" }} title="remove">×</span>
        </div>
      ))}
      {w.watch.length === 0 && <div style={{ color: C.faint }}>Nothing watched yet.</div>}
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
            {Object.entries(e.data).filter(([k]) => k !== "note").map(([k, v]) => <span key={k}>{k}={String(v)} </span>)}
            {e.data.note && <span style={{ color: C.faint }}>· {e.data.note}</span>}
          </span>
        </div>
      ))}
      {w.trace.length === 0 && <div style={{ color: C.faint }}>Nothing yet — map a field, add a step.</div>}
      <div ref={endRef} />
    </AppBody>
  );
}
/* ============================================================
   APP · CHARTS — the document manager (α, β, γ …)
   ============================================================ */
function ChartsApp() {
  const ui = useUI(); const w = ui.world;
  return (
    <>
      <div style={{ display: "flex", gap: 6, alignItems: "center", padding: "6px 8px 4px", flexShrink: 0, flexWrap: "wrap" }}>
        {Object.keys(DATASETS).map((ds) => (
          <Btn key={ds} tone={C.mint} onClick={() => w.newDoc(ds)}>＋ chart from {ds}</Btn>
        ))}
      </div>
      <AppBody style={{ paddingTop: 2 }}>
        <Hint>every card is a LIVE chart document with its own pipeline + encoding. the <b style={{ color: C.red }}>red-edged</b> one is ACTIVE: object-menu verbs (map to x, keep only…) act on it. any chart / table / pipeline / encoding tile can be re-pointed at any document via its DOC strip.</Hint>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {w.docs.map((d) => (
            <div key={d.id} style={{ border: (w.activeId === d.id ? "2px solid " + C.red : "1px solid " + C.ink), padding: 6, background: C.pane }}>
              <div style={{ display: "flex", gap: 5, alignItems: "center", marginBottom: 4 }}>
                <DocChip id={d.id} big />
                <input value={d.name} onChange={(e) => w.renameDoc(d.id, e.target.value)}
                  title="rename this chart document"
                  style={{ border: "1px solid " + C.line, background: C.pane, fontFamily: "inherit", fontSize: 10.5, padding: "0 3px", width: 54 }} />
              </div>
              <MiniPlot chart={d.chart} W={190} H={112} />
              <div style={{ fontSize: 9, color: C.faint, margin: "3px 0" }}>
                {d.chart.datasetId} ⊳ {d.chart.steps.filter((s) => s.on).length} steps ⊳ geom_{d.chart.geom} · x↦{d.chart.mapping.x} y↦{d.chart.mapping.y}
              </div>
              <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                {w.activeId !== d.id && <TBtn doc="make it the ACTIVE chart" onClick={() => w.setActive(d.id)}>set active</TBtn>}
                <TBtn doc="duplicate this document (pipeline + encoding copied)" onClick={() => w.dupDoc(d.id)}>⧉ dup</TBtn>
                <TBtn doc="freeze its spec as a snapshot in the gallery" onClick={() => w.snapshot(d.id)}>⚑ snap</TBtn>
                <TBtn doc={w.docs.length < 2 ? "the last document cannot be deleted" : "delete this document — tiles showing it fall back to another"} disabled={w.docs.length < 2} onClick={() => w.deleteDoc(d.id)}>✕</TBtn>
              </div>
            </div>
          ))}
        </div>
      </AppBody>
    </>
  );
}

/* ============================================================
   PRODUCT GUIDE — four short, live exercises
   ============================================================ */
const Sec = ({ t, children }) => (
  <div style={{ marginBottom: 11 }}>
    <div style={{ fontWeight: 760, letterSpacing: "0.08em", textTransform: "uppercase", fontSize: 10.25, background: C.sel, display: "inline-block", padding: "1px 6px", border: "1px solid " + C.ink }}>{t}</div>
    <div style={{ marginTop: 5, fontSize: 11.5, lineHeight: 1.5 }}>{children}</div>
  </div>
);
function GoWs({ name }) {
  const ui = useUI();
  return (
    <span onClick={() => ui.goSpace(name)}
      onMouseEnter={() => ui.setMouseDoc("switch to workspace " + name)} onMouseLeave={() => ui.setMouseDoc(null)}
      style={{ cursor: "pointer", border: "1px solid " + C.ink, background: C.paneAlt, fontWeight: 700, padding: "1px 7px", fontSize: 10.5, whiteSpace: "nowrap" }}>open {name} →</span>
  );
}
function TutStep({ n, run, runLabel, children }) {
  const ui = useUI();
  const [done, setDone] = useState(false);
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "flex-start", marginBottom: 9 }}>
      <span style={{ flexShrink: 0, width: 19, height: 19, border: "1.5px solid " + C.ink, background: done ? C.green : C.sel, color: done ? C.paper : C.ink, display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 10.5, fontWeight: 760 }}>{done ? "✓" : n}</span>
      <div style={{ flex: 1, minWidth: 0, fontSize: 11.5, lineHeight: 1.5 }}>
        {children}
        {run && (
          <div style={{ marginTop: 5 }}>
            <button onClick={async () => { await run(ui); setDone(true); }}
              onMouseEnter={() => ui.setMouseDoc("apply this move to the live workbench")} onMouseLeave={() => ui.setMouseDoc(null)}
              style={{ cursor: "pointer", border: "1.5px solid " + C.ink, boxShadow: "2px 2px 0 " + C.ink, background: done ? C.paneAlt : C.mint, color: C.ink, fontFamily: "inherit", fontWeight: 760, padding: "2px 8px", fontSize: 10.5 }}>
              {runLabel || "Show this move"}
            </button>
            {done && <span style={{ color: C.green, fontSize: 10, marginLeft: 7 }}>applied</span>}
          </div>
        )}
      </div>
    </div>
  );
}
const TutHead = ({ t, children }) => (
  <div style={{ marginBottom: 12 }}>
    <div style={{ fontWeight: 780, fontSize: 12, letterSpacing: "0.045em", textTransform: "uppercase", borderBottom: "2px solid " + C.ink, paddingBottom: 3, marginBottom: 5 }}>{t}</div>
    <div style={{ color: C.faint, fontSize: 11, lineHeight: 1.5 }}>{children}</div>
  </div>
);
const ensureDs = (world, datasetId) => {
  const document = world.active();
  if (document.chart.datasetId !== datasetId) world.setDataset(document.id, datasetId);
  return world.active();
};
const clearSteps = (world, document) => {
  [...document.chart.steps].forEach((step) => world.removeStep(document.id, step.id));
};

function Tut1App() {
  const ui = useUI();
  const world = ui.world;
  return (
    <AppBody>
      <TutHead t="1 · read the workspace">Three rules cover most of PBUI: hover for documentation, right-click for verbs, and let a command ask you for an object when it needs one.</TutHead>
      <TutStep n={1}>
        <b>Start with the status line.</b> Hover <FieldChip name="mass_g" type="q" />. The black line at the bottom names the object and tells you what the left and right mouse buttons will do. Use it before guessing.
      </TutStep>
      <TutStep n={2} run={(ui2) => {
        const active = ui2.world.active();
        ui2.world.inspect("<field> mass_g", {
          presentationType: "field",
          name: "mass_g",
          stats_in_active_chart: fieldStats(active.chart.datasetId, active.chart.steps, "mass_g") || "not present in this result",
        });
      }} runLabel="Inspect mass_g">
        <b>Right-click exposes the full verb set.</b> A field can be inspected, mapped, filtered, grouped or watched. The verbs belong to the object, so the same field behaves consistently in the data browser, a table header or an encoding slot.
      </TutStep>
      <TutStep n={3}>
        <b>Left-click performs the expected action.</b> A dataset becomes the active source. A document chip becomes active. A snapshot restores. The status line states the default before you invoke it.
      </TutStep>
      <TutStep n={4} run={async (ui2) => {
        const result = await ui2.accept("field", "Select a field to add to the watchlist");
        if (result) ui2.world.watchAdd("field", result.value);
      }} runLabel="Select a field for the watchlist">
        <b>Commands can request an argument.</b> Start this move, then click any highlighted field in any tile. PBUI passes that object to the waiting command. Press Esc to cancel.
      </TutStep>
      <TutStep n={5}>
        Every applied verb is recorded in the trace. Continue with <GoWs name="2·pipeline" /> to turn these object-level actions into a reproducible analysis.
      </TutStep>
    </AppBody>
  );
}

function Tut2App() {
  const ui = useUI();
  const world = ui.world;
  return (
    <AppBody>
      <TutHead t="2 · shape the relation">Build a small answer in the pipeline: remove one species, derive a measure, summarize by species, then rank the result. The table beside this guide shows every intermediate state.</TutHead>
      <TutStep n={1} run={(ui2) => {
        const document = ensureDs(ui2.world, "seabirds");
        clearSteps(ui2.world, document);
        ui2.world.addStep(document.id, mkStep("filter", { field: "species", op: "≠", value: "Tern" }));
      }} runLabel="Keep Petrel and Skua">
        <b>Filter first.</b> Add <code>species ≠ Tern</code>. The relation gets smaller; the chart and table remain views of the same document.
      </TutStep>
      <TutStep n={2} run={(ui2) => {
        const document = ensureDs(ui2.world, "seabirds");
        ui2.world.addStep(document.id, mkStep("derive", { name: "load", a: "mass_g", op: "/", b: "wing_mm" }));
      }} runLabel="Derive load = mass_g / wing_mm">
        <b>Derive a reusable field.</b> The new <FieldChip name="load" type="q" /> column appears in the output schema and can be mapped, filtered or sorted like a source column.
      </TutStep>
      <TutStep n={3} run={(ui2) => {
        const document = ensureDs(ui2.world, "seabirds");
        ui2.world.addStep(document.id, mkStep("summarize", { by: "species", fn: "mean", field: "mass_g" }));
      }} runLabel="Compute mean mass by species">
        <b>Summarize at the grain of the question.</b> One row per species is the correct relation for comparing species means. The output becomes <b>species</b> plus <FieldChip name="mean_mass_g" type="q" />.
      </TutStep>
      <TutStep n={4} run={(ui2) => {
        const document = ui2.world.active();
        ui2.world.addStep(document.id, mkStep("sort", { field: "mean_mass_g", dir: "desc" }));
        ui2.world.addStep(document.id, mkStep("limit", { n: 2 }));
      }} runLabel="Rank and keep the top two">
        <b>Sort and limit last.</b> Their position is visible and editable. Move a step and the result changes because the pipeline is an ordered program, not a log of past clicks.
      </TutStep>
      <TutStep n={5} run={(ui2) => {
        const document = ui2.world.active();
        const first = document.chart.steps[0];
        if (first) ui2.world.toggleStep(document.id, first.id);
      }} runLabel="Disable the filter">
        <b>Test an assumption without deleting it.</b> Disable the first step and compare the answer with Tern restored. Re-enable it from the pipeline when you are done.
      </TutStep>
      <TutStep n={6} run={(ui2) => clearSteps(ui2.world, ui2.world.active())} runLabel="Clear the pipeline">
        Reset the relation, then open <GoWs name="3·encode" /> to map an answer rather than decorate raw rows.
      </TutStep>
    </AppBody>
  );
}

function Tut3App() {
  const ui = useUI();
  const world = ui.world;
  return (
    <AppBody>
      <TutHead t="3 · map the answer">A chart specification has separate parts: the relation, the channel mappings, the geometry and the scale. Change one part at a time and keep the table nearby.</TutHead>
      <TutStep n={1} run={(ui2) => {
        const document = ensureDs(ui2.world, "seabirds");
        clearSteps(ui2.world, document);
        ui2.world.setGeom(document.id, "point");
        ui2.world.setMapping(document.id, "x", "wing_mm");
        ui2.world.setMapping(document.id, "y", "mass_g");
        ui2.world.setMapping(document.id, "color", "species");
        ui2.world.setMapping(document.id, "size", null);
        ui2.world.setMapping(document.id, "facet", null);
        ui2.world.setYScale(document.id, "linear");
      }} runLabel="Build the mass–wing scatterplot">
        <b>Map fields to channels.</b> Wing length drives x, mass drives y and species drives color. The point geometry says how each row should appear.
      </TutStep>
      <TutStep n={2} run={(ui2) => {
        const document = ui2.world.active();
        ui2.world.setMapping(document.id, "facet", "island");
      }} runLabel="Facet by island">
        <b>Split the comparison without copying the chart.</b> Faceting creates one panel per island while keeping shared scales, so position remains comparable across panels.
      </TutStep>
      <TutStep n={3} run={(ui2) => {
        const document = ui2.world.active();
        ui2.world.setMapping(document.id, "size", "bill_mm");
      }} runLabel="Map bill_mm to size">
        <b>Add a channel only when it carries a useful variable.</b> Size now represents bill length; remove it from the encoding slot to return to a uniform mark size.
      </TutStep>
      <TutStep n={4} run={(ui2) => {
        const document = ensureDs(ui2.world, "seabirds");
        clearSteps(ui2.world, document);
        ui2.world.addStep(document.id, mkStep("summarize", { by: "species", fn: "mean", field: "mass_g" }));
        ui2.world.setMapping(document.id, "x", "species");
        ui2.world.setMapping(document.id, "y", "mean_mass_g");
        ui2.world.setMapping(document.id, "color", "species");
        ui2.world.setMapping(document.id, "size", null);
        ui2.world.setMapping(document.id, "facet", null);
        ui2.world.setGeom(document.id, "bar");
      }} runLabel="Build mean mass by species">
        <b>Change the relation before the geometry.</b> The summary creates three rows; the bar chart maps those rows directly. This answers “which species is heaviest on average?” without asking the chart to aggregate implicitly.
      </TutStep>
      <TutStep n={5} run={(ui2) => ui2.world.setYScale(ui2.world.active().id, "log")} runLabel="Use a log y scale">
        <b>Scales transform position, not the data pipeline.</b> Toggle back to linear in the encoding tile. The table values do not change.
      </TutStep>
      <TutStep n={6}>
        Right-click a mark or legend category to write a real filter step back into the document. Then open <GoWs name="4·charts" /> to preserve and branch the result.
      </TutStep>
    </AppBody>
  );
}

function Tut4App() {
  const ui = useUI();
  const world = ui.world;
  return (
    <AppBody>
      <TutHead t="4 · branch without losing context">Documents hold analysis state. Tiles show that state. Workspaces arrange tiles. Snapshots freeze a specification. Keeping those roles separate makes comparison cheap.</TutHead>
      <TutStep n={1} run={(ui2) => ui2.world.newDoc("engines")} runLabel="Create an engines document">
        <b>Start a second line of inquiry.</b> The new document has its own source, pipeline, mappings, geometry and scale. The existing bird and climate work remains intact.
      </TutStep>
      <TutStep n={2}>
        <b>Re-point views instead of duplicating state.</b> Every chart, table, pipeline and encoding tile has a DOC control. Two tiles can show one document in sync, or different documents side by side.
      </TutStep>
      <TutStep n={3} run={(ui2) => {
        const first = ui2.world.docs[0];
        if (first) ui2.world.setActive(first.id);
      }} runLabel="Activate the first document">
        <b>The active document receives object-menu verbs.</b> Its chip is marked, and menu headers name the target before a filter or mapping is written.
      </TutStep>
      <TutStep n={4} run={(ui2) => ui2.world.snapshot(ui2.world.activeId)} runLabel="Snapshot the active document">
        <b>Freeze the specification, not a screenshot.</b> A snapshot stores the source, ordered steps, mappings, geometry and scale. Later edits do not alter it.
      </TutStep>
      <TutStep n={5} run={(ui2) => {
        const { snaps } = ui2.world;
        if (snaps[0]) ui2.world.pinSnap(0, snaps[0].id);
        if (snaps[1]) ui2.world.pinSnap(1, snaps[1].id);
      }} runLabel="Pin two snapshots for comparison">
        <b>Compare states directly.</b> Restore a snapshot into the active document, restore it as a new document, or pin two versions in the compare view.
      </TutStep>
      <TutStep n={6}>
        The everyday workspace is <GoWs name="build" />. The <GoWs name="help" /> workspace keeps the reference beside the product rather than sending you to a separate manual.
      </TutStep>
    </AppBody>
  );
}

function AboutApp() {
  const ui = useUI();
  const world = ui.world;
  const snapshot = world.snaps[0];
  const glossaryRow = (chip, text) => (
    <div style={{ display: "grid", gridTemplateColumns: "minmax(108px, 0.42fr) 1fr", gap: 9, alignItems: "baseline", marginBottom: 5 }}>
      <span style={{ minWidth: 0 }}>{chip}</span>
      <span style={{ color: C.faint, fontSize: 10.5, lineHeight: 1.4 }}>{text}</span>
    </div>
  );
  return (
    <AppBody>
      <Sec t="product">
        PBUI is a browser-native visual analysis workbench. A document keeps its <b>dataset, ordered pipeline, channel mappings, geometry and scale</b> together. The chart, table, pipeline and encoding panels are linked views over that document.
      </Sec>
      <Sec t="working model">
        Shape the relation first, then map the result. Filters, derives, summaries, sorts and limits remain visible as editable steps. Encodings remain explicit slot-to-field assignments. A chart mark can write a filter back into the same pipeline.
      </Sec>
      <Sec t="interaction">
        Hover for the status line. Left-click for the common action. Right-click for all type-appropriate verbs. Some commands pause in <b>accept mode</b>; click any highlighted compatible object in any tile, or press Esc to cancel.
      </Sec>
      <Sec t="documents, views and states">
        Documents own analysis state. Tiles are views that can be re-pointed through their DOC controls. Workspaces own layout. Snapshots freeze complete chart specifications for restore, branching and comparison.
      </Sec>
      <Sec t="object glossary">
        {glossaryRow(<DatasetChip id="seabirds" />, "source relation; left-click makes it the active document's source")}
        {glossaryRow(<FieldChip name="mass_g" type="q" />, "typed column; can be inspected, mapped, filtered, grouped or watched")}
        {glossaryRow(<Pres ptype="doc" value={world.activeId} />, "live chart document; object-menu verbs target the active one")}
        {snapshot && glossaryRow(<Pres ptype="chart" value={snapshot.id} />, "frozen chart specification; restore, fork or pin for comparison")}
        {glossaryRow(<span style={{ border: "1px solid " + C.ink, borderLeft: "4px solid " + C.lavender, background: C.pane, padding: "0 5px", fontSize: 10, fontWeight: 700 }}>FILTER</span>, "ordered pipeline step; disable, move or remove without hiding its role")}
      </Sec>
      <Sec t="runtime">
        Visible pipeline steps compile to SQL and run in a DuckDB-Wasm worker. A small JavaScript evaluator supplies the first frame and remains available as a fallback. Query results, field summaries and built plot geometry are cached by semantic state. <span style={{ marginLeft: 4 }}><ComputeBadge /></span>
      </Sec>
      <Sec t="guided exercises">
        Each guide uses the live product and changes real state. Start with objects, then build a relation, map an answer and preserve the branch.
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 5 }}>
          <GoWs name="1·objects" /><GoWs name="2·pipeline" /><GoWs name="3·encode" /><GoWs name="4·charts" />
        </div>
      </Sec>
      <Sec t="design note">
        The document model follows a grammar-of-graphics decomposition. The object-level interaction is inspired by presentation systems such as Genera and CLIM: rendered values retain type and behavior instead of becoming inert pixels or strings.
      </Sec>
      <Sec t="sample data">
        The included seabirds, climate and engines tables are deterministic fictional datasets. They keep the examples reproducible and contain no production data.
      </Sec>
    </AppBody>
  );
}

function LauncherApp({ leafId }) {
  const ui = useUI();
  return (
    <AppBody>
      <Hint>empty tile — choose an application. chart / table / pipeline / encoding tiles bind to a chart DOCUMENT (re-pointable via their DOC strip; several tiles on one document stay in sync). the rest are shared singletons over the world.</Hint>
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
  gallery: { title: "snapshots", color: C.lavender, comp: GalleryApp },
  compare: { title: "compare a/b", color: C.rose, comp: CompareApp },
  watch: { title: "watchlist", color: C.mustard, comp: WatchlistApp },
  inspector: { title: "inspector", color: C.lavender, comp: InspectorApp },
  trace: { title: "trace", color: C.sage, comp: TraceApp },
  about: { title: "about / help", color: C.sel, comp: AboutApp },
  tut1: { title: "tutorial 1 · objects", color: C.sel, comp: Tut1App },
  tut2: { title: "tutorial 2 · pipeline", color: C.sel, comp: Tut2App },
  tut3: { title: "tutorial 3 · encoding", color: C.sel, comp: Tut3App },
  tut4: { title: "tutorial 4 · charts", color: C.sel, comp: Tut4App },
};

/* ============================================================
   SHELL — workspaces, object menus, accept plumbing
   ============================================================ */
const initialSpaces = (world) => {
  const dA = world.docs[0] ? world.docs[0].id : null;   /* α · seabirds */
  const dB = world.docs[1] ? world.docs[1].id : null;   /* β · climate  */
  return [
    {
      id: nid(), name: "build",
      tree: split("row",
        split("col", leaf("pipeline", dA), leaf("encode", dA), 0.52),
        split("col", leaf("chart", dA), leaf("table", dA), 0.58),
        0.42),
    },
    {
      id: nid(), name: "explore",
      tree: split("row", leaf("data"), split("col", leaf("chart", dB), leaf("inspector"), 0.6), 0.36),
    },
    {
      id: nid(), name: "gallery",
      tree: split("row", leaf("gallery"), split("col", leaf("compare"), leaf("trace"), 0.55), 0.46),
    },
    { id: nid(), name: "help", tree: split("row", leaf("about"), split("col", leaf("watch"), leaf("trace"), 0.5), 0.5) },
    { id: nid(), name: "1·objects", tree: split("row", leaf("tut1"), split("col", leaf("data"), leaf("inspector"), 0.55), 0.44) },
    { id: nid(), name: "2·pipeline", tree: split("row", leaf("tut2"), split("col", leaf("pipeline", dA), leaf("table", dA), 0.5), 0.42) },
    { id: nid(), name: "3·encode", tree: split("row", leaf("tut3"), split("col", leaf("encode", dA), leaf("chart", dA), 0.44), 0.42) },
    { id: nid(), name: "4·charts", tree: split("row", leaf("tut4"), split("col", leaf("charts"), leaf("gallery"), 0.55), 0.42) },
  ];
};

export default function App() {
  const [, force] = useState(0);
  const bump = useCallback(() => force((x) => x + 1), []);
  const worldRef = useRef(null);
  if (!worldRef.current) worldRef.current = new World();
  const world = worldRef.current;
  useEffect(() => { world.notify = bump; }, [bump, world]);
  useEffect(() => queryEngine.subscribe(bump), [bump]);

  const [spaces, setSpaces] = useState(() => initialSpaces(world));
  const [cur, setCur] = useState(() => spaces[0].id);
  const [renaming, setRenaming] = useState(null);
  const [menu, setMenu] = useState(null);
  const [accepting, setAccepting] = useState(null);
  const [mouseDoc, setMouseDoc] = useState(null);
  const [drag, setDrag] = useState(null);
  const dragRef = useRef(null); dragRef.current = drag;
  const leafRefs = useRef({});

  const space = spaces.find((s) => s.id === cur) || spaces[0];
  const tree = space.tree;

  const mutateTree = (fn) => setSpaces((ss) => ss.map((s) => (s.id === space.id ? { ...s, tree: fn(s.tree) } : s)));
  const setRatio = (id, r) => mutateTree((t) => updateNode(t, id, (n) => ({ ...n, ratio: r })));
  const splitLeaf = (id, dir) => { mutateTree((t) => updateNode(t, id, (n) => split(dir, n, leaf("launcher"), 0.5))); world.log("split_tile", { dir: dir === "row" ? "⬌" : "⬍" }); };
  const closeLeaf = (id) => { mutateTree((t) => removeLeaf(t, id)); world.log("close_tile", {}); };
  const setLeafApp = (id, app) => { mutateTree((t) => updateNode(t, id, (n) => ({ ...n, app, doc: DOC_APPS.includes(app) ? (n.doc || world.activeId) : n.doc }))); world.log("app_changed", { app: APPS[app].title }); };
  const setLeafDoc = (id, docId) => { mutateTree((t) => updateNode(t, id, (n) => ({ ...n, doc: docId }))); world.bump(); };
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
  const cloneSpace = (id) => { const s = spaces.find((x) => x.id === id); if (!s) return; const c = { id: nid(), name: s.name + "′", tree: cloneTree(s.tree) }; setSpaces((ss) => [...ss, c]); setCur(c.id); world.log("workspace_cloned", { from: s.name }); };

  const accept = (ptype, prompt) => new Promise((resolve) => setAccepting({ ptype, prompt, resolve: (r) => { if (r) world.log("accepted", { ptype: r.ptype, value: labelFor(r.ptype, r.value) }); resolve(r); } }));
  useEffect(() => { const esc = (e) => { if (e.key === "Escape") { setMenu(null); if (accepting) { accepting.resolve(null); setAccepting(null); } } }; window.addEventListener("keydown", esc); return () => window.removeEventListener("keydown", esc); }, [accepting]);

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
    if (ptype === "geom") return { presentationType: "geom", geom: value, needs: value === "bar" ? "nominal x + quantitative y" : "x + quantitative y" };
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
      acts.push({
        label: "Filter on this field", run: () => {
          world.addStep(null, mkStep("filter", { field: value, op: f && f.type === "q" ? ">" : "=", value: "" }));
        }
      });
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
      const dId = value && value.docId ? value.docId : null;
      const dd = world.doc(dId);
      const row = value && value.row ? value.row : value || {};
      const dSchema = schemaAfter(dd.chart.datasetId, dd.chart.steps);
      const nomKeys = Object.keys(row).filter((k) => { const f = dSchema.find((x) => x.name === k); return f && f.type !== "q"; }).slice(0, 3);
      nomKeys.forEach((k) => {
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
      acts.push({ label: "Add to watchlist", run: () => world.watchAdd("chart", value) });
    }
    if (ptype === "tile") {
      acts.push({ label: "Split ⬌ (new tile right)", run: () => splitLeaf(value, "row") });
      acts.push({ label: "Split ⬍ (new tile below)", run: () => splitLeaf(value, "col") });
      acts.push({ label: "Swap app with…  (accept a tile)", run: async () => { const r = await accept("tile", "SWAP — click another TILE's title (Esc cancels)"); if (r && r.value !== value) swapTiles(value, r.value); } });
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

  const goSpace = (name) => { const s = spaces.find((x) => x.name === name); if (s) setCur(s.id); };
  const ui = {
    world, accepting, setAccepting, setMouseDoc, accept, labelFor, describe, drag, spaces, goSpace,
    openMenu: (ptype, value, x, y) => setMenu({ ptype, value, x, y }),
    wm: { setRatio, splitLeaf, closeLeaf, setLeafApp, setLeafDoc, startDrag, registerRef, canClose: tree.type !== "leaf" },
  };
  const dragSrcLeaf = drag && findLeaf(tree, drag.from);

  return (
    <UICtx.Provider value={ui}>
      <div onClick={() => setMenu(null)} style={{ fontFamily: "'IBM Plex Mono', ui-monospace, Menlo, monospace", background: C.paper, color: C.ink, height: "100vh", display: "flex", flexDirection: "column", fontSize: 12 }}>
        <style>{`
          .pres { cursor: pointer; }
          .pres:hover { outline: 1px dotted ${C.ink}; background: ${C.sel}; }
          .pres.acceptable { outline: 2px solid ${C.red}; background: ${C.sel}; animation: pulse 0.9s infinite; cursor: pointer; }
          .pres-svg { cursor: pointer; }
          .pres-svg:hover { filter: drop-shadow(0 0 1.5px ${C.ink}); }
          .pres-svg.acceptable { filter: drop-shadow(0 0 2.5px ${C.red}); }
          @keyframes pulse { 50% { outline-color: ${C.mustard}; } }
          ::-webkit-scrollbar { width: 12px; height: 12px; }
          ::-webkit-scrollbar-thumb { background: ${C.line}; border: 3px solid ${C.pane}; }
          ::-webkit-scrollbar-track { background: ${C.pane}; }
          table th { font-weight: 700; }
          @media (prefers-reduced-motion: reduce) { .pres.acceptable { animation: none; } }
        `}</style>

        <div style={{ background: C.ink, color: C.paper, textAlign: "center", padding: "4px 0", fontWeight: 700, letterSpacing: "0.28em", fontSize: 13, flexShrink: 0 }}>
          P B U I &nbsp;—&nbsp; G R A M M A R &nbsp; O F &nbsp; G R A P H I C S
        </div>

        {accepting && (
          <div style={{ background: C.red, color: C.paper, padding: "3px 10px", fontWeight: 700, flexShrink: 0 }}>
            ACCEPTING &lt;{Array.isArray(accepting.ptype) ? accepting.ptype.join("|") : accepting.ptype}&gt; — {accepting.prompt} — works across tiles AND workspaces
          </div>
        )}

        <div style={{ display: "flex", gap: 6, alignItems: "center", padding: "5px 8px 0", flexShrink: 0, flexWrap: "wrap" }}>
          <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.08em" }}>WORKSPACES</span>
          {spaces.map((s) =>
            renaming === s.id ? (
              <input key={s.id} autoFocus defaultValue={s.name}
                onKeyDown={(e) => { if (e.key === "Enter") { const name = e.target.value.trim() || s.name; setSpaces((ss) => ss.map((x) => (x.id === s.id ? { ...x, name } : x))); world.log("workspace_renamed", { name }); setRenaming(null); } }}
                onBlur={() => setRenaming(null)}
                style={{ border: "2px solid " + C.ink, background: C.pane, fontFamily: "inherit", fontSize: 11, padding: "1px 5px", width: 90 }} />
            ) : (
              <P key={s.id} ptype="workspace" value={s.id} onActivate={() => setCur(s.id)} activateDoc="switch to it" doc={"workspace " + s.name + " (" + countLeaves(s.tree) + " tiles)"}>
                <span style={{ border: "2px solid " + C.ink, background: cur === s.id ? C.sel : C.paneAlt, padding: "1px 9px", fontWeight: cur === s.id ? 700 : 400, cursor: "pointer" }}>{s.name}</span>
              </P>
            ))}
          <Btn tone={C.mint} onClick={addSpace}>+ workspace</Btn>
          <span style={{ color: C.faint, fontSize: 10.5 }}>chip: L switches · R for rename / duplicate / delete</span>
          <span style={{ flex: 1 }} />
          <ComputeBadge />
        </div>

        <div style={{ flex: 1, display: "flex", padding: 8, minHeight: 0 }}><NodeView node={tree} /></div>

        <div style={{ background: C.ink, color: C.paper, padding: "3px 10px", fontSize: 11, flexShrink: 0, display: "flex", gap: 16 }}>
          <span style={{ color: C.mustard, fontWeight: 700 }}>{accepting ? "ACCEPT MODE" : drag ? "MOVING APP" : "READY"}</span>
          <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {mouseDoc || (accepting ? accepting.prompt + "   (Esc: abort)" : "⌖ maps a field from any tile · R-click a mark filters ITS chart · DOC strips re-point tiles between chart documents · ⚑ snapshots · start with 1·objects, then 2·pipeline, 3·encode and 4·charts")}
          </span>
          <span style={{ color: C.faint }}>{countLeaves(tree)} tiles · {spaces.length} workspaces</span>
        </div>

        {drag && dragSrcLeaf && (
          <div style={{ position: "fixed", left: drag.x + 12, top: drag.y + 12, zIndex: 200, pointerEvents: "none", background: APPS[dragSrcLeaf.app].color, border: "2px solid " + C.ink, boxShadow: "3px 3px 0 " + C.ink, padding: "1px 8px", fontSize: 11, fontWeight: 700 }}>
            {APPS[dragSrcLeaf.app].title} → {drag.over && drag.over !== drag.from ? (drag.zone === "center" ? "swap apps" : "dock " + ({ left: "⇤", right: "⇥", top: "⤒", bottom: "⤓" }[drag.zone] || "") + " (source closes)") : "drop on a tile · center swaps · edges split"}
          </div>
        )}

        {menu && (
          <div onClick={(e) => e.stopPropagation()} style={{ position: "fixed", left: Math.min(menu.x, (typeof window !== "undefined" ? window.innerWidth : 800) - 320), top: Math.min(menu.y, (typeof window !== "undefined" ? window.innerHeight : 600) - 300), zIndex: 100, background: C.pane, border: "2px solid " + C.ink, boxShadow: "4px 4px 0 " + C.ink, minWidth: 260, maxHeight: 300, overflow: "auto" }}>
            <div style={{ background: C.ink, color: C.paper, padding: "2px 8px", fontSize: 10, fontWeight: 700, letterSpacing: "0.06em" }}>
              &lt;{menu.ptype}&gt; {labelFor(menu.ptype, menu.value).slice(0, 30)}
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
