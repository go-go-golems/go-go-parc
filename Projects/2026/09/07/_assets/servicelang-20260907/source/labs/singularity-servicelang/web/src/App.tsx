import { useEffect, useRef, useState } from "react";
import { actions, api, useAppDispatch, useAppSelector } from "./store";
import { CodeEditor } from "./CodeEditor";
import { Graph } from "./Graph";
import type { Block, FunctionView, Input, Preset, Report, Span } from "./types";

function nativeLines(report: Report) {
  return report.Output ? report.Output.Header.split("\n").length - 1 : 0;
}
function Summary({ report }: { report: Report }) {
  return (
    <div className="summary">
      <strong className={report.Accepted ? "good" : "bad"}>
        {report.Accepted ? "ACCEPTED" : "REJECTED"}
      </strong>
      <span>{report.Functions?.length ?? 0} functions</span>
      <span>
        {report.Functions?.reduce((n, f) => n + f.Blocks.length, 0) ?? 0} blocks
      </span>
      <span>
        {report.Output
          ? `${nativeLines(report)} C++ lines`
          : "no native output"}
      </span>
    </div>
  );
}
function Ownership({ fn, block }: { fn: FunctionView; block: Block }) {
  const [owners, setOwners] = useState(true);
  return (
    <>
      <label className="toggle">
        <input
          type="checkbox"
          checked={owners}
          onChange={(e) => setOwners(e.target.checked)}
        />{" "}
        Owned slots only
      </label>
      <p className="hint">
        U = uninitialized · L = live · D = consumed. These are static
        possibility sets, not runtime values.
      </p>
      {!block.In ? (
        <p className="empty">
          No facts recorded here: unreachable, not visited before rejection, or
          inspection limited.
        </p>
      ) : (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Slot / source</th>
                <th>Type</th>
                <th>IN</th>
                <th>OUT</th>
                <th>Origin byte</th>
              </tr>
            </thead>
            <tbody>
              {fn.Slots.filter((s) => !owners || s.Owned).map((s) => {
                const a = block.In?.find((x) => x.Slot === s.ID),
                  z = block.Out?.find((x) => x.Slot === s.ID);
                return (
                  <tr key={s.ID}>
                    <td>
                      %{s.ID} {s.Name || "temporary"}
                    </td>
                    <td>{s.Type}</td>
                    <td
                      className={
                        a?.States.includes("L") && a.States.length > 1
                          ? "bad"
                          : ""
                      }
                    >{`{${a?.States.join(",") ?? ""}}`}</td>
                    <td>{`{${z?.States.join(",") ?? ""}}`}</td>
                    <td>{z?.Origin?.Start ?? "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
export default function App() {
  const dispatch = useAppDispatch(),
    s = useAppSelector((s) => s.workbench);
  const { data: presets, error: presetError } = api.usePresetsQuery(),
    { data: implementation } = api.useImplementationQuery();
  const [analyze] = api.useAnalyzeMutation();
  const initialized = useRef(false);
  const [editMode, setEditMode] = useState<"Source" | "Plan">("Source"),
    [selection, setSelection] = useState<Span | null>(null),
    [implFile, setImplFile] = useState("check.go");
  const r = s.report,
    stale = !!r && s.reportRevision !== s.revision;
  const fn =
    r?.Functions?.find((f) => f.Name === s.selectedFunction) ??
    r?.Functions?.[0];
  const block =
    fn?.Blocks.find((b) => b.ID === s.selectedBlock) ?? fn?.Blocks[0];
  const compile = (input: Input = s.input, revision = s.revision) => {
    const request = analyze(input);
    dispatch(actions.started({ id: request.requestId, revision }));
    void request
      .unwrap()
      .then((report) =>
        dispatch(actions.finished({ id: request.requestId, revision, report })),
      )
      .catch((error: unknown) =>
        dispatch(
          actions.failed({
            id: request.requestId,
            message: JSON.stringify(error),
          }),
        ),
      );
  };
  const load = (p: Preset) => {
    dispatch(actions.presetLoaded(p));
    setEditMode("Source");
    setSelection(null);
    compile(
      { Source: p.Source, Filename: p.Filename, Plan: p.Plan },
      s.revision + 1,
    );
  };
  useEffect(() => {
    if (presets && !initialized.current) {
      initialized.current = true;
      load(presets[0]);
    }
  }, [presets]);
  const jump = (span: Span) => {
    if (stale) return;
    setEditMode("Source");
    setSelection({ ...span });
  };
  const selectBlock = (id: number) => {
    dispatch(actions.selectBlock(id));
    const b = fn?.Blocks.find((b) => b.ID === id);
    if (b)
      jump(b.Ops?.find((o) => o.Span.End > o.Span.Start)?.Span ?? b.End.Span);
  };
  const setPane = (pane: string) => dispatch(actions.pane(pane));
  return (
    <div className="app">
      <header>
        <div>
          <div className="eyebrow">SINGULARITY / SERVICELANG</div>
          <h1>Compiler Explorer</h1>
        </div>
        <p>
          One implementation. Inspect every ownership decision.
          <br />
          <span>Host compiler only · no native execution or RF access</span>
        </p>
      </header>
      <main>
        <aside className="presets">
          <div className="section-title">01 / COMPARE PRESETS</div>
          <p className="hint">
            Choose a program. Pin a result, then load its mutation.
          </p>
          {presetError && (
            <p role="alert" className="bad">
              Cannot load presets. Is the Go server running?
            </p>
          )}
          {presets?.map((p) => (
            <button
              key={p.ID}
              className={`preset ${s.preset === p.ID ? "active" : ""}`}
              onClick={() => load(p)}
            >
              <span className={p.Expected ? "dot good" : "dot bad"}>●</span>
              <strong>{p.Title}</strong>
              <small>{p.Description}</small>
            </button>
          ))}
          <div className="baseline-status">
            <div className="section-title">PINNED BASELINE</div>
            {s.baseline ? (
              <>
                <strong>{s.baseline.input.Filename}</strong>
                <span>
                  {s.baseline.report.Accepted ? "Accepted" : "Rejected"} ·{" "}
                  {s.baseline.report.SourceSHA256.slice(0, 10)}
                </span>
                <button onClick={() => setPane("compare")}>
                  Open comparison
                </button>
                <button
                  className="quiet"
                  onClick={() => dispatch(actions.clearBaseline())}
                >
                  Clear baseline
                </button>
              </>
            ) : (
              <p className="hint">
                Compile, then pin a baseline to preserve its source and result.
              </p>
            )}
          </div>
        </aside>
        <section
          className="editor-column"
          aria-label="Source and startup editors"
        >
          <div className="editor-heading">
            <span className="section-title">02 / EDIT THE PROGRAM</span>
            <code>{s.input.Filename}</code>
          </div>
          <div className="toolbar">
            <button
              className={editMode === "Source" ? "active" : ""}
              onClick={() => setEditMode("Source")}
            >
              Source
            </button>
            <button
              className={editMode === "Plan" ? "active" : ""}
              onClick={() => setEditMode("Plan")}
            >
              Startup plan{s.input.Plan ? " ●" : ""}
            </button>
            <span className="spacer" />
            <span className="revision">rev {s.revision}</span>
          </div>
          <CodeEditor
            value={s.input[editMode]}
            language={editMode === "Plan" ? "json" : "svc"}
            label={
              editMode === "Plan"
                ? "Startup plan editor"
                : "ServiceLang source editor"
            }
            selection={editMode === "Source" ? selection : null}
            onChange={(value) => {
              dispatch(actions.edited({ field: editMode, value }));
              setSelection(null);
            }}
            onRun={() => compile()}
          />
          <div className="run-bar">
            <button
              className="primary"
              onClick={() => compile()}
              disabled={!!s.pending}
            >
              {s.pending ? "Compiling…" : "Compile · Ctrl/⌘ Enter"}
            </button>
            <button
              onClick={() => dispatch(actions.pin())}
              disabled={!r || stale || !!s.pending}
            >
              Pin baseline
            </button>
          </div>
          <p className="hint editor-foot">
            Explicit move, exhaustive outcomes, checked exits. An empty startup
            plan checks source alone. Editing marks the previous result stale;
            it does not execute code.
          </p>
        </section>
        <section className="analysis" aria-label="Compiler analysis">
          <div className="analysis-heading">
            <span className="section-title">
              03 / INSPECT THE IMPLEMENTATION
            </span>
            {r && <code>{r.SourceSHA256.slice(0, 12)}</code>}
          </div>
          {s.error && (
            <div role="alert" className="notice bad">
              Request failed: {s.error}. Any result below is from the prior
              successful request.
            </div>
          )}
          {stale && (
            <div role="status" className="notice warning">
              STALE RESULT · source or plan changed. Compile to inspect this
              revision.
            </div>
          )}
          {r && <Summary report={r} />}
          <div className="stages">
            {r?.Stages.map((stage) => (
              <button
                key={stage.Name}
                className={`stage ${stage.Status}`}
                title={stage.Detail}
                onClick={() => {
                  setImplFile(stage.Detail.split(":")[0]);
                  setPane("implementation");
                }}
              >
                <span>
                  {stage.Status === "passed"
                    ? "✓"
                    : stage.Status === "rejected"
                      ? "×"
                      : "·"}
                </span>
                {stage.Name}
                <small>{stage.Status}</small>
              </button>
            ))}
          </div>
          <nav className="tabs" aria-label="Analysis views">
            {[
              "cfg",
              "ownership",
              "diagnostics",
              "cpp",
              "startup",
              "syntax",
              "implementation",
              "compare",
            ].map((pane) => (
              <button
                key={pane}
                className={s.pane === pane ? "active" : ""}
                aria-pressed={s.pane === pane}
                onClick={() => setPane(pane)}
              >
                {({ cfg: "CFG", cpp: "C++" } as Record<string, string>)[pane] ??
                  pane}
              </button>
            ))}
          </nav>
          {r && !r.Accepted && (
            <p className="notice bad">
              Rejected before native output. Solver facts on invalid paths are
              diagnostic approximations, not valid executions.
            </p>
          )}
          {r?.InspectionLimited && (
            <p className="notice warning">
              Inspection limited to 100,000 fact cells. All compiler checks
              still ran.
            </p>
          )}
          <div className="panel">
            {(s.pane === "cfg" || s.pane === "ownership") &&
              (fn && block ? (
                <>
                  <div className="toolbar">
                    <label>
                      Function{" "}
                      <select
                        value={fn.Name}
                        onChange={(e) =>
                          dispatch(actions.selectFunction(e.target.value))
                        }
                      >
                        {r?.Functions?.map((f) => (
                          <option key={f.Name}>{f.Name}</option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Block{" "}
                      <select
                        value={block.ID}
                        onChange={(e) => selectBlock(Number(e.target.value))}
                      >
                        {fn.Blocks.map((b) => (
                          <option key={b.ID} value={b.ID}>
                            b{b.ID} · {b.End.Kind}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                  {s.pane === "cfg" ? (
                    <>
                      <Graph
                        fn={fn}
                        selected={block.ID}
                        onSelect={selectBlock}
                      />
                      <h2>b{block.ID} / ordered operations</h2>
                      <ol className="operations">
                        {block.Ops?.map((op, i) => (
                          <li key={i}>
                            <button
                              disabled={stale}
                              onClick={() => jump(op.Span)}
                            >
                              <code>
                                {op.Dest >= 0 ? `%${op.Dest} = ` : ""}
                                {op.Kind} {op.Name}{" "}
                                {(op.Args ?? []).map((x) => `%${x}`).join(", ")}
                              </code>
                              <small>
                                bytes {op.Span.Start}–{op.Span.End}
                              </small>
                            </button>
                          </li>
                        ))}
                      </ol>
                      <p className="hint">
                        Terminator: {block.End.Kind}. Select a block, then
                        Ownership for its stabilized IN/OUT sets.
                      </p>
                    </>
                  ) : (
                    <Ownership fn={fn} block={block} />
                  )}
                </>
              ) : (
                <p className="empty">
                  No typed CFG available. Inspect diagnostics or compile a
                  preset.
                </p>
              ))}
            {s.pane === "diagnostics" && (
              <>
                {r?.Diagnostics?.length ? (
                  r.Diagnostics.map((d, i) => (
                    <article className="diagnostic" key={i}>
                      <strong>{d.Code}</strong>
                      <p>{d.Message}</p>
                      <button
                        disabled={stale || d.Code.startsWith("E_PLAN")}
                        onClick={() => jump(d.Span)}
                      >
                        Source bytes {d.Span.Start}–{d.Span.End}
                      </button>
                      {d.Related && (
                        <button
                          disabled={stale}
                          onClick={() => jump(d.Related!)}
                        >
                          Earlier ownership location · byte {d.Related.Start}
                        </button>
                      )}
                    </article>
                  ))
                ) : (
                  <p className="empty">
                    {r
                      ? "No compiler diagnostics for this result."
                      : "Compile a program to inspect diagnostics."}
                  </p>
                )}
              </>
            )}
            {s.pane === "cpp" &&
              (r?.Output ? (
                <>
                  <div className="metadata">
                    ABI {r.Output.RuntimeABI} · compiler{" "}
                    {r.Output.CompilerSHA256.slice(0, 12)}
                  </div>
                  <CodeEditor
                    value={r.Output.Header}
                    language="cpp"
                    readOnly
                    label="Generated C++"
                  />
                  <details>
                    <summary>
                      Source maps for {fn?.Name} / b{block?.ID}
                    </summary>
                    {r.Output.Mappings.filter(
                      (m) => m.Function === fn?.Name && m.Block === block?.ID,
                    ).map((m, i) => (
                      <button
                        key={i}
                        disabled={stale}
                        onClick={() => jump(m.Source)}
                      >
                        C++ lines {m.FirstLine}–{m.LastLine} ↔ source bytes{" "}
                        {m.Source.Start}–{m.Source.End}
                      </button>
                    ))}
                  </details>
                </>
              ) : (
                <p className="empty">
                  No C++ emitted for rejected or uncompiled input.
                </p>
              ))}
            {s.pane === "startup" &&
              (r?.Output?.Wiring ? (
                <>
                  <p className="hint">
                    Validated fixed endpoint wiring. Native acquisition cleanup
                    is fail-closed retirement, not rollback.
                  </p>
                  <CodeEditor
                    value={r.Output.Wiring}
                    language="cpp"
                    readOnly
                    label="Generated startup wiring"
                  />
                </>
              ) : (
                <p className="empty">
                  Choose the checked startup preset or add a valid plan.
                  Rejected plans publish no wiring.
                </p>
              ))}
            {s.pane === "syntax" && (
              <CodeEditor
                value={JSON.stringify(r?.AST ?? {}, null, 2)}
                language="json"
                readOnly
                label="Parser AST"
              />
            )}
            {s.pane === "implementation" && (
              <>
                <label>
                  Actual embedded implementation{" "}
                  <select
                    value={implFile}
                    onChange={(e) => setImplFile(e.target.value)}
                  >
                    {Object.keys(implementation ?? {})
                      .sort()
                      .map((f) => (
                        <option key={f}>{f}</option>
                      ))}
                  </select>
                </label>
                <p className="hint">
                  Read the Go compiler and trusted native headers packaged with
                  this server. Stage buttons select their implementation file.
                </p>
                <CodeEditor
                  value={
                    implementation?.[implFile] ?? "Loading implementation…"
                  }
                  language={implFile.endsWith(".hpp") ? "cpp" : "go"}
                  readOnly
                  label="Compiler implementation source"
                />
              </>
            )}
            {s.pane === "compare" &&
              (s.baseline && r ? (
                <>
                  <p className="hint">
                    Pinned input and report are immutable. Current result{" "}
                    {stale ? "is stale" : "matches the editor revision"}. This
                    compares compiler decisions, not RF behavior.
                  </p>
                  <div className="comparison">
                    <article>
                      <h2>Pinned · {s.baseline.input.Filename}</h2>
                      <Summary report={s.baseline.report} />
                      <CodeEditor
                        value={s.baseline.input.Source}
                        readOnly
                        label="Pinned baseline source"
                      />
                    </article>
                    <article>
                      <h2>Current result</h2>
                      <Summary report={r} />
                      <ul>
                        {r.Diagnostics?.map((d, i) => (
                          <li key={i}>
                            <strong>{d.Code}</strong> {d.Message}
                          </li>
                        ))}
                      </ul>
                      <p>
                        Baseline native lines: {nativeLines(s.baseline.report)}
                        <br />
                        Current native lines: {nativeLines(r)}
                      </p>
                      <p>
                        {r.SourceSHA256 === s.baseline.report.SourceSHA256
                          ? "Source text is identical; inspect plan differences."
                          : "Source hashes differ."}
                      </p>
                      {s.baseline.input.Plan && (
                        <details>
                          <summary>Pinned startup plan</summary>
                          <pre>{s.baseline.input.Plan}</pre>
                        </details>
                      )}
                    </article>
                  </div>
                </>
              ) : (
                <p className="empty">
                  Pin a compiled baseline, then choose another preset or edit
                  the source.
                </p>
              ))}
          </div>
        </section>
      </main>
      <footer>
        Actual Go analysis → checked C++17 · U/L/D is a finite static domain ·
        passing examples are evidence, not a soundness proof
      </footer>
    </div>
  );
}
