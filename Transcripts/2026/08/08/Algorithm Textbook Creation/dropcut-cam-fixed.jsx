import React, { useState, useRef, useEffect } from "react";
import * as THREE from "three";
import {
  PRESETS, heightfieldTris, parseSTL, buildModel, generateJob, verifyJob, toGcode, devColor
} from "./dropcut-core.mjs";

/* ================================================================
   UI
   ================================================================ */

const CSS = `
:root{
  --bg:#14171B; --panel:#1B2026; --panel2:#20262E; --line:#2C333D;
  --text:#D5DBE4; --dim:#8A93A1; --amber:#FFB100; --cyan:#4FC8DD;
  --mono:ui-monospace,SFMono-Regular,Consolas,monospace; --disp:system-ui,sans-serif;
}
*{box-sizing:border-box;margin:0}
.dc-app{height:100vh;display:flex;flex-direction:column;background:var(--bg);color:var(--text);font-family:var(--mono);font-size:13px;overflow:hidden}
.dc-head{display:flex;align-items:baseline;gap:14px;padding:10px 18px;border-bottom:1px solid var(--line);background:var(--panel)}
.dc-head h1{font-family:var(--disp);font-weight:700;font-size:17px;letter-spacing:.22em}
.dc-head h1 b{color:var(--amber)}
.dc-head span{color:var(--dim);font-size:11px}
.dc-main{flex:1;display:flex;min-height:0}
.dc-side{width:268px;flex-shrink:0;overflow-y:auto;border-right:1px solid var(--line);background:var(--panel);padding:12px 14px 24px}
.dc-grp{margin-bottom:15px}
.dc-grp>h2{font-size:10px;letter-spacing:.18em;color:var(--dim);text-transform:uppercase;border-bottom:1px solid var(--line);padding-bottom:5px;margin-bottom:9px;display:flex;justify-content:space-between;align-items:center}
.dc-row{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:7px}
.dc-row label{color:var(--dim);font-size:12px;flex:1}
.dc-row .u{color:var(--dim);font-size:10px;width:26px}
select,input[type=number]{background:var(--panel2);border:1px solid var(--line);color:var(--text);font-family:var(--mono);font-size:12px;padding:5px 7px;border-radius:3px;width:100%}
input[type=number]{width:76px;text-align:right}
input[type=checkbox]{accent-color:var(--amber);width:14px;height:14px}
select:focus,input:focus,button:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
.dc-btn{display:block;width:100%;padding:9px 10px;border-radius:3px;border:1px solid var(--line);background:var(--panel2);color:var(--text);font-family:var(--mono);font-size:12px;cursor:pointer;letter-spacing:.06em}
.dc-btn:hover{border-color:var(--dim)}
.dc-btn.primary{background:var(--amber);border-color:var(--amber);color:#1a1206;font-weight:600}
.dc-btn.primary:hover{background:#ffc23d}
.dc-btn:disabled{opacity:.45;cursor:default}
.dc-prog{height:4px;background:var(--panel2);border-radius:2px;margin-top:8px;overflow:hidden}
.dc-prog>div{height:100%;background:var(--amber);transition:width .15s}
.dc-stats{background:var(--panel2);border:1px solid var(--line);border-radius:4px;padding:9px 11px;font-size:11.5px;line-height:1.75}
.dc-stats b{color:var(--amber);font-weight:500}
.dc-stats .bad{color:#E06C5A}
.dc-view{flex:1;position:relative;min-width:0;background:#101318}
.dc-view canvas{display:block}
.dc-ovl{position:absolute;top:10px;left:12px;font-size:11px;color:var(--dim);line-height:1.7;pointer-events:none}
.dc-ovl b{color:var(--text);font-weight:500}
.dc-ovl .sw{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.dc-hint{position:absolute;bottom:8px;right:12px;font-size:10px;color:#5b6472;pointer-events:none}
.dc-foot{display:flex;align-items:center;gap:14px;padding:8px 16px;border-top:1px solid var(--line);background:var(--panel);flex-wrap:wrap}
.dc-dro{display:flex;gap:14px;background:#0d0f12;border:1px solid var(--line);border-radius:4px;padding:6px 14px}
.dc-dro .c{display:flex;gap:7px;align-items:baseline}
.dc-dro .l{color:var(--dim);font-size:11px}
.dc-dro .v{color:var(--amber);font-weight:600;font-size:15px;min-width:9ch;text-align:right;text-shadow:0 0 8px rgba(255,177,0,.45);font-variant-numeric:tabular-nums}
.dc-sim{display:flex;gap:8px;align-items:center}
.dc-sim button,.dc-sim select{width:auto;padding:6px 12px}
.dc-status{margin-left:auto;color:var(--dim);font-size:11px}
.dc-file{display:none}
@media(max-width:760px){.dc-main{flex-direction:column}.dc-side{width:100%;max-height:44vh}}
`;

function Num({ label, unit, value, set, step = 1, min, max, dis }) {
  return (
    <div className="dc-row">
      <label>{label}</label>
      <input type="number" value={value} step={step} min={min} max={max} disabled={dis}
        onChange={(e) => set(parseFloat(e.target.value) || 0)} />
      <span className="u">{unit}</span>
    </div>
  );
}

export default function DropcutCAM() {
  const [source, setSource] = useState({ type: "preset", id: "sprite" });
  const [scale, setScale] = useState(1);
  const [model, setModel] = useState(null);
  const [tool, setTool] = useState({ type: "ball", diameter: 3 });
  const [prm, setPrm] = useState({
    strategy: "raster", scallop: 0.01, stepoverPct: 40, chordTol: 0.01,
    margin: 2, direction: "X", steepDeg: 45,
    roughOn: true, stepdown: 1.5, roughStepPct: 45, allowance: 0.2,
    entryMode: "auto", rampAngle: 3, scallopMetric: "surface-graph",
    arcFit: true, arcTol: 0.01, feed: 600, clearance: 5, rpm: 10000, floorZ: 0,
  });
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState(0);
  const [job, setJob] = useState(null);
  const [verif, setVerif] = useState(null);
  const [showVerif, setShowVerif] = useState(false);
  const [vBusy, setVBusy] = useState(false);
  const [vProg, setVProg] = useState(0);
  const [err, setErr] = useState("");
  const stlRef = useRef(null);
  const generateCancelRef = useRef(false);
  const verifyCancelRef = useRef(false);
  const fileInput = useRef(null);

  const setP = (k) => (v) => setPrm((s) => ({ ...s, [k]: v }));

  useEffect(() => {
    try {
      setErr("");
      let raw, name;
      if (source.type === "preset") {
        raw = heightfieldTris(PRESETS[source.id]);
        name = PRESETS[source.id].label;
      } else {
        raw = stlRef.current;
        name = source.name;
        if (!raw) return;
      }
      setModel(buildModel(raw, scale || 1, name));
      setJob(null); setVerif(null); setShowVerif(false);
    } catch (e) { setErr(String(e.message || e)); }
  }, [source, scale]);

  const onFile = async (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    try {
      const buf = await f.arrayBuffer();
      stlRef.current = parseSTL(buf);
      setSource({ type: "stl", name: f.name });
    } catch (ex) { setErr("STL parse failed: " + ex.message); }
    e.target.value = "";
  };

  const onGenerate = async () => {
    if (!model || busy) return;
    generateCancelRef.current = false;
    setBusy(true); setJob(null); setVerif(null); setShowVerif(false); setProgress(0);
    try {
      const res = await generateJob(model, tool, prm, setProgress, generateCancelRef);
      if (res) setJob(res);
    } catch (ex) { setErr("Generation failed: " + ex.message); console.error(ex); }
    setBusy(false);
  };

  const onVerify = async () => {
    if (!job || !model || vBusy) return;
    verifyCancelRef.current = false;
    setVBusy(true); setVerif(null); setVProg(0);
    try {
      const res = await verifyJob(job, model, prm, tool, setVProg, verifyCancelRef);
      if (res) { setVerif(res); setShowVerif(true); }
    } catch (ex) { setErr("Verification failed: " + ex.message); console.error(ex); }
    setVBusy(false);
  };

  const onExport = () => {
    if (!job || !model) return;
    const g = toGcode(job, tool, prm, model.name);
    const blob = new Blob([g.text], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "dropcut.nc";
    a.click();
    URL.revokeObjectURL(a.href);
  };

  /* ---------- three.js viewport ---------- */
  const mountRef = useRef(null);
  const threeRef = useRef({});
  const simRef = useRef({ playing: false, t: 0, mult: 8 });
  const [, forceSim] = useState(0);
  const droX = useRef(null), droY = useRef(null), droZ = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
    mount.appendChild(renderer.domElement);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x101318);
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 2000);
    camera.up.set(0, 0, 1);

    scene.add(new THREE.HemisphereLight(0x9fb4cc, 0x22262c, 0.9));
    const dl = new THREE.DirectionalLight(0xffffff, 0.85);
    dl.position.set(40, -55, 80);
    scene.add(dl);
    const grid = new THREE.GridHelper(120, 24, 0x2b323c, 0x1c2229);
    grid.rotation.x = Math.PI / 2;
    scene.add(grid);
    const axGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0.02), new THREE.Vector3(14, 0, 0.02),
      new THREE.Vector3(0, 0, 0.02), new THREE.Vector3(0, 14, 0.02),
      new THREE.Vector3(0, 0, 0.02), new THREE.Vector3(0, 0, 14),
    ]);
    axGeo.setAttribute("color", new THREE.BufferAttribute(new Float32Array([
      1, .45, .35, 1, .45, .35, .45, .85, .5, .45, .85, .5, .4, .7, 1, .4, .7, 1,
    ]), 3));
    scene.add(new THREE.LineSegments(axGeo, new THREE.LineBasicMaterial({ vertexColors: true })));

    const ctl = { theta: -Math.PI / 3.2, phi: 1.05, radius: 90, target: new THREE.Vector3(0, 0, 5) };
    const applyCam = () => {
      const s = Math.sin(ctl.phi);
      camera.position.set(
        ctl.target.x + ctl.radius * s * Math.cos(ctl.theta),
        ctl.target.y + ctl.radius * s * Math.sin(ctl.theta),
        ctl.target.z + ctl.radius * Math.cos(ctl.phi));
      camera.lookAt(ctl.target);
    };
    applyCam();

    let drag = null;
    const el = renderer.domElement;
    el.addEventListener("contextmenu", (e) => e.preventDefault());
    el.addEventListener("pointerdown", (e) => {
      drag = { x: e.clientX, y: e.clientY, btn: e.button, shift: e.shiftKey };
      el.setPointerCapture(e.pointerId);
    });
    el.addEventListener("pointermove", (e) => {
      if (!drag) return;
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      drag.x = e.clientX; drag.y = e.clientY;
      if (drag.btn === 2 || drag.shift) {
        const k = ctl.radius * 0.0016;
        const right = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 0);
        const up = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 1);
        ctl.target.addScaledVector(right, -dx * k).addScaledVector(up, dy * k);
      } else {
        ctl.theta -= dx * 0.008;
        ctl.phi = Math.min(Math.PI - 0.05, Math.max(0.05, ctl.phi - dy * 0.008));
      }
      applyCam();
    });
    el.addEventListener("pointerup", () => (drag = null));
    el.addEventListener("wheel", (e) => {
      e.preventDefault();
      ctl.radius = Math.min(600, Math.max(5, ctl.radius * Math.exp(e.deltaY * 0.0011)));
      applyCam();
    }, { passive: false });

    const ro = new ResizeObserver(() => {
      const w = mount.clientWidth, h = mount.clientHeight;
      renderer.setSize(w, h);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    });
    ro.observe(mount);

    const clock = new THREE.Clock();
    let raf;
    const fmt = (v) => (v < 0 ? "-" : "+") + Math.abs(v).toFixed(3).padStart(7, "0");
    const tick = () => {
      raf = requestAnimationFrame(tick);
      const dt = Math.min(0.05, clock.getDelta());
      const st = threeRef.current;
      const sim = simRef.current;
      if (st.job && st.toolGroup) {
        const { cumT, pos, nPts } = st.job;
        const total = cumT[nPts - 1];
        if (sim.playing) {
          sim.t += sim.mult * dt;
          if (sim.t >= total) { sim.t = total; sim.playing = false; forceSim((n) => n + 1); }
        }
        let lo = 0, hi = nPts - 1;
        while (lo < hi - 1) { const md = (lo + hi) >> 1; (cumT[md] <= sim.t ? (lo = md) : (hi = md)); }
        const segT = cumT[hi] - cumT[lo] || 1;
        const tt = Math.min(1, Math.max(0, (sim.t - cumT[lo]) / segT));
        const x = pos[lo * 3] + (pos[hi * 3] - pos[lo * 3]) * tt;
        const y = pos[lo * 3 + 1] + (pos[hi * 3 + 1] - pos[lo * 3 + 1]) * tt;
        const z = pos[lo * 3 + 2] + (pos[hi * 3 + 2] - pos[lo * 3 + 2]) * tt;
        st.toolGroup.position.set(x, y, z);
        if (droX.current) {
          droX.current.textContent = fmt(x);
          droY.current.textContent = fmt(y);
          droZ.current.textContent = fmt(z);
        }
      }
      renderer.render(scene, camera);
    };
    tick();

    threeRef.current = { renderer, scene, camera, ctl, applyCam };
    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, []);

  /* ---------- part mesh ---------- */
  useEffect(() => {
    const st = threeRef.current;
    if (!st.scene || !model) return;
    if (st.partMesh) {
      st.scene.remove(st.partMesh);
      st.partMesh.geometry.dispose();
      st.partMesh.material.dispose();
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(model.tris), 3));
    g.computeVertexNormals();
    const mesh = new THREE.Mesh(g, new THREE.MeshPhongMaterial({
      color: 0x33383f, shininess: 42, specular: 0x556070, side: THREE.DoubleSide,
    }));
    st.scene.add(mesh);
    st.partMesh = mesh;
    const bx = model.bbox;
    const diag = Math.hypot(bx.maxX - bx.minX, bx.maxY - bx.minY, bx.maxZ);
    st.ctl.target.set(0, 0, bx.maxZ / 2);
    st.ctl.radius = Math.max(20, diag * 1.7);
    st.applyCam();
  }, [model]);

  /* ---------- verification heatmap mesh ---------- */
  useEffect(() => {
    const st = threeRef.current;
    if (!st.scene) return;
    if (st.verifMesh) {
      st.scene.remove(st.verifMesh);
      st.verifMesh.geometry.dispose();
      st.verifMesh.material.dispose();
      st.verifMesh = null;
    }
    if (!verif) return;
    const { nx, ny, hx, hy, x0, y0, H, dev, partMask, stats } = verif;
    const NN = (nx + 1) * (ny + 1);
    const posA = new Float32Array(NN * 3);
    const colA = new Float32Array(NN * 3);
    for (let j = 0; j <= ny; j++)
      for (let i = 0; i <= nx; i++) {
        const k = j * (nx + 1) + i;
        posA[k * 3] = x0 + i * hx;
        posA[k * 3 + 1] = y0 + j * hy;
        posA[k * 3 + 2] = H[k];
        const c = devColor(dev[k], stats.band, stats.gougeTol);
        colA[k * 3] = c[0]; colA[k * 3 + 1] = c[1]; colA[k * 3 + 2] = c[2];
      }
    const idx = [];
    for (let j = 0; j < ny; j++)
      for (let i = 0; i < nx; i++) {
        const a = j * (nx + 1) + i, bq = a + 1, c = a + nx + 1, d = c + 1;
        if (!partMask || partMask[a] || partMask[bq] || partMask[c] || partMask[d])
          idx.push(a, bq, d, a, d, c);
      }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(posA, 3));
    g.setAttribute("color", new THREE.BufferAttribute(colA, 3));
    g.setIndex(idx);
    g.computeVertexNormals();
    const mesh = new THREE.Mesh(g, new THREE.MeshPhongMaterial({
      vertexColors: true, shininess: 18, side: THREE.DoubleSide,
    }));
    st.scene.add(mesh);
    st.verifMesh = mesh;
  }, [verif]);

  /* visibility toggles */
  useEffect(() => {
    const st = threeRef.current;
    if (st.partMesh) st.partMesh.visible = !showVerif;
    if (st.verifMesh) st.verifMesh.visible = showVerif;
  }, [showVerif, verif, model]);

  /* ---------- job path rendering + tool ---------- */
  useEffect(() => {
    const st = threeRef.current;
    if (!st.scene) return;
    for (const key of ["lineFin", "lineRough", "lineTravel"]) {
      if (st[key]) {
        st.scene.remove(st[key]);
        st[key].geometry.dispose();
        st[key].material.dispose();
        st[key] = null;
      }
    }
    if (st.toolGroup) { st.scene.remove(st.toolGroup); st.toolGroup = null; }
    st.job = null;
    if (!job) return;

    const { pos, kinds, nPts, zMin, zMax } = job;
    const finV = [], finC = [], roughV = [], travV = [];
    const span = Math.max(1e-6, zMax - zMin);
    const colAt = (z) => {
      const t = Math.min(1, Math.max(0, (z - zMin) / span));
      return [0.31 + t * 0.69, 0.78 - t * 0.09, 0.87 - t * 0.87];
    };
    for (let i = 1; i < nPts; i++) {
      const k = kinds[i];
      const x0 = pos[(i - 1) * 3], y0 = pos[(i - 1) * 3 + 1], z0 = pos[(i - 1) * 3 + 2];
      const x1 = pos[i * 3], y1 = pos[i * 3 + 1], z1 = pos[i * 3 + 2];
      if (k === 3) {
        finV.push(x0, y0, z0 + 0.02, x1, y1, z1 + 0.02);
        finC.push(...colAt(z0), ...colAt(z1));
      } else if (k === 2 || k === 4) roughV.push(x0, y0, z0 + 0.02, x1, y1, z1 + 0.02);
      else travV.push(x0, y0, z0, x1, y1, z1);
    }
    const mk = (verts, mat, cols) => {
      if (!verts.length) return null;
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(verts), 3));
      if (cols) g.setAttribute("color", new THREE.BufferAttribute(new Float32Array(cols), 3));
      const l = new THREE.LineSegments(g, mat);
      st.scene.add(l);
      return l;
    };
    st.lineRough = mk(roughV, new THREE.LineBasicMaterial({ color: 0x5b7089, transparent: true, opacity: 0.55 }));
    st.lineTravel = mk(travV, new THREE.LineBasicMaterial({ color: 0xb4543f, transparent: true, opacity: 0.4 }));
    st.lineFin = mk(finV, new THREE.LineBasicMaterial({ vertexColors: true }), finC);

    const R = tool.diameter / 2;
    const grp = new THREE.Group();
    const mat = new THREE.MeshPhongMaterial({ color: 0xffb100, shininess: 90 });
    if (tool.type === "ball") {
      const s = new THREE.Mesh(new THREE.SphereGeometry(R, 20, 14), mat);
      s.position.z = R;
      grp.add(s);
      const c = new THREE.Mesh(new THREE.CylinderGeometry(R, R, 16, 20), mat);
      c.rotation.x = Math.PI / 2; c.position.z = R + 8;
      grp.add(c);
    } else {
      const c = new THREE.Mesh(new THREE.CylinderGeometry(R, R, 16, 20), mat);
      c.rotation.x = Math.PI / 2; c.position.z = 8;
      grp.add(c);
    }
    grp.position.set(pos[0], pos[1], pos[2]);
    st.scene.add(grp);
    st.toolGroup = grp;
    st.job = job;
    simRef.current.t = 0;
    simRef.current.playing = false;
  }, [job, tool.type, tool.diameter]); // eslint-disable-line

  const R = tool.diameter / 2;
  const stepPreview = tool.type === "ball"
    ? 2 * Math.sqrt(Math.max(0, tool.diameter * prm.scallop - prm.scallop ** 2))
    : tool.diameter * prm.stepoverPct / 100;
  const sim = simRef.current;
  const bx = model?.bbox;
  const S = job?.stats;
  const VS = verif?.stats;

  return (
    <div className="dc-app">
      <style>{CSS}</style>
      <header className="dc-head">
        <h1>DROP<b>CUT</b></h1>
        <span>rough · finish · verify — coverage-first hybrid, surface-metric spacing, and dexel verification</span>
      </header>

      <div className="dc-main">
        <aside className="dc-side">
          <div className="dc-grp">
            <h2>Geometry</h2>
            <div className="dc-row">
              <select
                value={source.type === "preset" ? source.id : "__current"}
                onChange={(e) => {
                  const v = e.target.value;
                  if (v === "__stl") fileInput.current.click();
                  else if (v !== "__current") setSource({ type: "preset", id: v });
                }}>
                {Object.entries(PRESETS).map(([id, p]) => (
                  <option key={id} value={id}>{p.label}</option>
                ))}
                {source.type === "stl" && <option value="__current">{source.name}</option>}
                <option value="__stl">Upload STL…</option>
              </select>
            </div>
            <input ref={fileInput} className="dc-file" type="file" accept=".stl" onChange={onFile} />
            <Num label="Scale" unit="×" value={scale} set={setScale} step={0.1} min={0.01} />
            {bx && (
              <div className="dc-stats">
                {model.nTri.toLocaleString()} triangles<br />
                <b>{(bx.maxX - bx.minX).toFixed(1)}</b> × <b>{(bx.maxY - bx.minY).toFixed(1)}</b> × <b>{bx.maxZ.toFixed(1)}</b> mm
              </div>
            )}
          </div>

          <div className="dc-grp">
            <h2>Tool</h2>
            <div className="dc-row">
              <label>Type</label>
              <select style={{ width: 110 }} value={tool.type}
                onChange={(e) => setTool((t) => ({ ...t, type: e.target.value }))}>
                <option value="ball">Ball nose</option>
                <option value="flat">Flat end</option>
              </select>
            </div>
            <Num label="Diameter" unit="mm" value={tool.diameter} step={0.5} min={0.1}
              set={(v) => setTool((t) => ({ ...t, diameter: v }))} />
          </div>

          <div className="dc-grp">
            <h2>
              Roughing
              <input type="checkbox" checked={prm.roughOn}
                onChange={(e) => setP("roughOn")(e.target.checked)} />
            </h2>
            <Num label="Stepdown" unit="mm" value={prm.stepdown} set={setP("stepdown")} step={0.25} min={0.2} dis={!prm.roughOn} />
            <Num label="Stepover" unit="%D" value={prm.roughStepPct} set={setP("roughStepPct")} step={5} min={10} max={90} dis={!prm.roughOn} />
            <Num label="Allowance" unit="mm" value={prm.allowance} set={setP("allowance")} step={0.05} min={0} dis={!prm.roughOn} />
            <div className="dc-row">
              <label>Entry</label>
              <select style={{ width: 110 }} value={prm.entryMode} disabled={!prm.roughOn}
                onChange={(e) => setP("entryMode")(e.target.value)}>
                <option value="auto">Helix → ramp</option>
                <option value="ramp">Ramp only</option>
                <option value="plunge">Plunge</option>
              </select>
            </div>
            <Num label="Ramp angle" unit="°" value={prm.rampAngle} set={setP("rampAngle")} step={0.5} min={0.5} max={20} dis={!prm.roughOn || prm.entryMode === "plunge"} />
          </div>

          <div className="dc-grp">
            <h2>Finishing</h2>
            <div className="dc-row">
              <label>Strategy</label>
              <select style={{ width: 130 }} value={prm.strategy} onChange={(e) => setP("strategy")(e.target.value)}>
                <option value="raster">Raster</option>
                <option value="hybrid">Hybrid + waterline</option>
                <option value="scallop">Constant scallop</option>
              </select>
            </div>
            {prm.strategy === "scallop" && (
              <div className="dc-row">
                <label>Spacing metric</label>
                <select style={{ width: 130 }} value={prm.scallopMetric} onChange={(e) => setP("scallopMetric")(e.target.value)}>
                  <option value="surface-graph">Surface graph</option>
                  <option value="slope-eikonal">Legacy slope PDE</option>
                </select>
              </div>
            )}
            {tool.type === "ball" ? (
              <Num label="Max scallop" unit="mm" value={prm.scallop} set={setP("scallop")} step={0.005} min={0.001} />
            ) : (
              <Num label="Stepover" unit="%D" value={prm.stepoverPct} set={setP("stepoverPct")} step={5} min={5} max={90} />
            )}
            <Num label="Chord tol" unit="mm" value={prm.chordTol} set={setP("chordTol")} step={0.005} min={0.001} />
            <Num label="Margin" unit="mm" value={prm.margin} set={setP("margin")} step={0.5} min={0} />
            {prm.strategy === "hybrid" && (
              <Num label="Steep angle" unit="°" value={prm.steepDeg} set={setP("steepDeg")} step={5} min={15} max={80} />
            )}
            {prm.strategy !== "scallop" && (
              <div className="dc-row">
                <label>Direction</label>
                <select style={{ width: 110 }} value={prm.direction} onChange={(e) => setP("direction")(e.target.value)}>
                  <option value="X">Along X</option>
                  <option value="Y">Along Y</option>
                </select>
              </div>
            )}
            <div className="dc-row">
              <label>→ stepover</label>
              <span style={{ color: "var(--amber)" }}>{stepPreview.toFixed(3)}</span>
              <span className="u">mm</span>
            </div>
          </div>

          <div className="dc-grp">
            <h2>
              Arc fitting
              <input type="checkbox" checked={prm.arcFit}
                onChange={(e) => setP("arcFit")(e.target.checked)} />
            </h2>
            <Num label="Arc tol" unit="mm" value={prm.arcTol} set={setP("arcTol")} step={0.005} min={0.001} dis={!prm.arcFit} />
          </div>

          <div className="dc-grp">
            <h2>Cutting</h2>
            <Num label="Feed" unit="mm/m" value={prm.feed} set={setP("feed")} step={50} min={10} />
            <Num label="Spindle" unit="rpm" value={prm.rpm} set={setP("rpm")} step={500} min={0} />
            <Num label="Clearance" unit="mm" value={prm.clearance} set={setP("clearance")} step={1} min={1} />
          </div>

          <div className="dc-grp">
            {!busy ? (
              <button className="dc-btn primary" onClick={onGenerate} disabled={!model}>
                GENERATE JOB
              </button>
            ) : (
              <button className="dc-btn" onClick={() => (generateCancelRef.current = true)}>
                CANCEL ({Math.round(progress * 100)}%)
              </button>
            )}
            {busy && <div className="dc-prog"><div style={{ width: `${progress * 100}%` }} /></div>}
            {err && <div style={{ color: "#E06C5A", marginTop: 8, fontSize: 11 }}>{err}</div>}
          </div>

          {S && (
            <div className="dc-grp">
              <h2>Result</h2>
              <div className="dc-stats">
                {S.roughLevels > 0 && (<>
                  rough: <b>{S.roughLevels}</b> levels · <b>{S.roughMin.toFixed(1)}</b> min<br />
                </>)}
                {S.finDesc} · <b>{S.finishMin.toFixed(1)}</b> min<br />
                {S.arc && (<>
                  arcs: <b>{S.arc.raw.toLocaleString()}</b> pts → <b>{(S.arc.arcs + S.arc.lines).toLocaleString()}</b> moves
                  {" "}(<b>{S.arc.arcs.toLocaleString()}</b> G2/G3)<br />
                </>)}
                total <b>{S.timeMin.toFixed(1)}</b> min · {(S.cutLenMM / 1000).toFixed(2)} m cut
              </div>
              <button className="dc-btn" style={{ marginTop: 8 }} onClick={onExport}>
                EXPORT G-CODE (.nc)
              </button>
              {!vBusy ? (
                <button className="dc-btn" style={{ marginTop: 6 }} onClick={onVerify}>
                  VERIFY CUT (DEXEL SIM)
                </button>
              ) : (
                <button className="dc-btn" style={{ marginTop: 6 }} onClick={() => (verifyCancelRef.current = true)}>
                  CANCEL VERIFY ({Math.round(vProg * 100)}%)
                </button>
              )}
              {vBusy && <div className="dc-prog"><div style={{ width: `${vProg * 100}%` }} /></div>}
            </div>
          )}

          {VS && (
            <div className="dc-grp">
              <h2>Verification</h2>
              <div className="dc-stats">
                gouge: <b className={VS.minDev < -VS.gougeTol ? "bad" : ""}>{VS.minDev.toFixed(3)}</b> mm
                {VS.minDev < -VS.gougeTol ? " ⚠" : " ✓"}<br />
                max excess: <b>{VS.maxDev.toFixed(3)}</b> mm<br />
                rms on part: <b>{VS.rms.toFixed(3)}</b> mm<br />
                within tol: <b>{VS.pctOK.toFixed(1)}</b>%
              </div>
              <button className="dc-btn" style={{ marginTop: 8 }} onClick={() => setShowVerif((v) => !v)}>
                {showVerif ? "SHOW PART" : "SHOW MACHINED STOCK"}
              </button>
            </div>
          )}
        </aside>

        <div className="dc-view" ref={mountRef}>
          <div className="dc-ovl">
            {model && (<><b>{model.name}</b><br /></>)}
            {showVerif && verif ? (<>
              <span className="sw" style={{ background: "#E05545" }} />gouge&nbsp;&nbsp;
              <span className="sw" style={{ background: "#3AA675" }} />in&nbsp;tolerance&nbsp;&nbsp;
              <span className="sw" style={{ background: "#5B8CC4" }} />excess&nbsp;stock
            </>) : job ? (<>
              <span className="sw" style={{ background: "#5B7089" }} />roughing&nbsp;&nbsp;
              <span className="sw" style={{ background: "linear-gradient(90deg,#4FC8DD,#FFB100)" }} />finishing&nbsp;&nbsp;
              <span className="sw" style={{ background: "#B4543F" }} />rapids
            </>) : (<>no job — set parameters and generate</>)}
          </div>
          <div className="dc-hint">drag rotate · shift-drag pan · wheel zoom</div>
        </div>
      </div>

      <footer className="dc-foot">
        <div className="dc-dro">
          <div className="c"><span className="l">X</span><span className="v" ref={droX}>+000.000</span></div>
          <div className="c"><span className="l">Y</span><span className="v" ref={droY}>+000.000</span></div>
          <div className="c"><span className="l">Z</span><span className="v" ref={droZ}>+000.000</span></div>
        </div>
        <div className="dc-sim">
          <button className="dc-btn" disabled={!job}
            onClick={() => { sim.playing = !sim.playing; forceSim((n) => n + 1); }}>
            {sim.playing ? "❚❚ PAUSE" : "▶ RUN"}
          </button>
          <button className="dc-btn" disabled={!job}
            onClick={() => { sim.t = 0; sim.playing = false; forceSim((n) => n + 1); }}>
            ⟲
          </button>
          <select style={{ width: 84 }} defaultValue={8}
            onChange={(e) => { sim.mult = +e.target.value; }}>
            {[1, 8, 32, 128].map((m) => <option key={m} value={m}>{m}× time</option>)}
          </select>
        </div>
        <div className="dc-status">
          {busy ? `computing… ${Math.round(progress * 100)}%`
            : vBusy ? `verifying… ${Math.round(vProg * 100)}%`
              : job ? "job ready — simulate, verify, or export"
                : "idle"}
        </div>
      </footer>
    </div>
  );
}
