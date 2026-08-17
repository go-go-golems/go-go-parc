import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";
import COMMON_FIXTURE from "../fixtures/domain.json";
import {
  BindingError,
  canonicalStringify,
  checkIdentityCompatibility,
  createSessionFromFixture,
  displayPort,
  parsePortKey,
  portKey,
  portRef,
  runCompilerDifferential,
  runCurrentPlanChecks,
  semanticEqual,
  shortHash,
} from "./core.mjs";

/* ============================================================
   P06 · TYPED PORTS + BINDING QUOTIENT LAB

   The visual vocabulary adapts the supplied PBUI productivity-suite
   foundation: thick tile borders, a paper-like palette, typed live
   presentations, hover documentation, a global interaction mode, and a
   shell-level trace. The semantic core in this file is the P06 quotient
   compiler rather than the productivity application's accept protocol.
   ============================================================ */

const C = {
  paper: "#ffffff",
  pane: "#ffffff",
  paneAlt: "#f1f1ee",
  ink: "#23262b",
  faint: "#70767d",
  line: "#d9d9d4",
  sage: "#7cae9b",
  blue: "#7aa6c9",
  rose: "#d59a86",
  mustard: "#e0b95c",
  lavender: "#a99fc9",
  mint: "#8fc7b0",
  red: "#c2503a",
  green: "#3f9d6b",
  sel: "#fdeec6",
  add: "#e7f4ec",
  del: "#fbe9e4",
  warm: "#faf7ee",
};

const DOC_TONES = {
  "doc-a": C.blue,
  "doc-b": C.mustard,
  "doc-z": C.faint,
};

const DATA = {
  "doc-a": [
    { id: "row-1", station: "A", temperature: 18.4, pressure: 101.2 },
    { id: "row-2", station: "B", temperature: 21.1, pressure: 100.8 },
    { id: "row-3", station: "C", temperature: 16.8, pressure: 102.1 },
    { id: "row-4", station: "D", temperature: 23.7, pressure: 99.9 },
  ],
  "doc-b": [
    { id: "row-7", station: "E", temperature: 13.2, pressure: 98.7 },
    { id: "row-8", station: "F", temperature: 15.9, pressure: 97.8 },
    { id: "row-9", station: "G", temperature: 17.3, pressure: 99.1 },
  ],
  "doc-z": [],
};

const REFS = {
  chartDocument: portRef("chart-1", "document"),
  chartSelection: portRef("chart-1", "selection"),
  pipelineDocument: portRef("pipeline-1", "document"),
  pipelineFilter: portRef("pipeline-1", "filter"),
  pipelineOutput: portRef("pipeline-1", "outputDocument"),
  tableDocument: portRef("table-1", "document"),
  tableSelection: portRef("table-1", "selection"),
};

const LabCtx = createContext(null);
const useLab = () => useContext(LabCtx);

function createDemoSession(compiler = "union-find") {
  return createSessionFromFixture(COMMON_FIXTURE, {
    compiler,
    defaultsBySort: {
      document: { sort: "document", key: "doc-a" },
      "row-selection": { sort: "row-selection", rows: [] },
      "filter-expression": { sort: "filter-expression", op: "true" },
    },
  });
}

function asError(error) {
  if (error instanceof BindingError) return error;
  return new BindingError("ui-error", error?.message || String(error), [
    {
      code: "ui-error",
      severity: "error",
      message: error?.message || String(error),
      details: { stack: error?.stack || null },
    },
  ]);
}

function errorData(error) {
  const problem = asError(error);
  return {
    name: problem.name,
    code: problem.code,
    message: problem.message,
    diagnostics: problem.diagnostics || [],
    stack: problem.stack || null,
  };
}

function readyValue(session, ref) {
  const projection = session.projection(ref);
  const state = projection.resource.state;
  return state.kind === "ready" ? state.value : null;
}

function documentFor(session, ref) {
  const value = readyValue(session, ref);
  return COMMON_FIXTURE.subjects.documents.find((doc) => doc.key === value?.key) || null;
}

function rowsFor(session, ref) {
  const document = documentFor(session, ref);
  return document ? DATA[document.key] || [] : [];
}

function selectionFor(session, ref) {
  const value = readyValue(session, ref);
  return value?.sort === "row-selection" ? value.rows || [] : [];
}

function toggleRow(session, ref, rowId) {
  const current = selectionFor(session, ref);
  const rows = current.includes(rowId)
    ? current.filter((id) => id !== rowId)
    : [...current, rowId].sort();
  session.write(ref, { sort: "row-selection", rows });
}

function P({
  ptype,
  value,
  doc,
  children,
  block = false,
  onActivate,
  state,
  style,
  ariaLabel,
}) {
  const lab = useLab();
  const Tag = block ? "div" : "span";
  const activate = (event) => {
    if (!onActivate) return;
    event.preventDefault();
    event.stopPropagation();
    onActivate();
  };
  return (
    <Tag
      className={`pres ${state ? `pres-${state}` : ""}`}
      data-pbui="presentation"
      data-ptype={ptype}
      data-pstate={state || "ordinary"}
      tabIndex={onActivate ? 0 : undefined}
      role={onActivate ? "button" : undefined}
      aria-label={ariaLabel || doc}
      style={style}
      onClick={activate}
      onKeyDown={(event) => {
        if (onActivate && (event.key === "Enter" || event.key === " ")) activate(event);
      }}
      onContextMenu={(event) => {
        event.preventDefault();
        event.stopPropagation();
        lab.inspect({ ptype, value, doc });
      }}
      onMouseEnter={() => lab.setMouseDoc(doc || `<${ptype}>`)}
      onMouseLeave={() => lab.setMouseDoc(null)}
    >
      {children}
    </Tag>
  );
}

function Btn({ children, onClick, tone = C.blue, disabled = false, title, pressed }) {
  return (
    <button
      type="button"
      title={title}
      disabled={disabled}
      aria-pressed={pressed}
      onClick={onClick}
      style={{
        fontFamily: "inherit",
        fontSize: 10.5,
        fontWeight: 700,
        letterSpacing: "0.025em",
        background: disabled ? C.paneAlt : tone,
        color: C.ink,
        border: `2px solid ${C.ink}`,
        boxShadow: disabled ? "none" : `2px 2px 0 ${C.ink}`,
        padding: "2px 8px",
        cursor: disabled ? "default" : "pointer",
        opacity: disabled ? 0.5 : 1,
      }}
    >
      {children}
    </button>
  );
}

function MiniBtn({ children, onClick, title, disabled = false, tone = C.paneAlt }) {
  return (
    <button
      type="button"
      title={title}
      disabled={disabled}
      onClick={onClick}
      style={{
        fontFamily: "inherit",
        fontSize: 9.5,
        fontWeight: 700,
        border: `1px solid ${C.ink}`,
        background: tone,
        padding: "1px 5px",
        cursor: disabled ? "default" : "pointer",
        opacity: disabled ? 0.45 : 1,
      }}
    >
      {children}
    </button>
  );
}

function Tag({ children, tone = C.paneAlt, title }) {
  return (
    <span
      title={title}
      style={{
        border: `1px solid ${C.ink}`,
        borderLeft: `4px solid ${tone}`,
        background: C.pane,
        padding: "0 5px",
        fontSize: 9.5,
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </span>
  );
}

function Head({ children, right }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        borderBottom: `2px solid ${C.ink}`,
        paddingBottom: 3,
        marginBottom: 6,
      }}
    >
      <b style={{ fontSize: 10, letterSpacing: "0.08em", textTransform: "uppercase" }}>
        {children}
      </b>
      <span style={{ flex: 1 }} />
      {right}
    </div>
  );
}

function Tile({ title, color, children, subtitle, right }) {
  return (
    <section
      style={{
        minWidth: 0,
        minHeight: 260,
        display: "flex",
        flexDirection: "column",
        border: `2px solid ${C.ink}`,
        background: C.pane,
      }}
    >
      <header
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          minHeight: 24,
          padding: "2px 6px",
          background: color,
          borderBottom: `2px solid ${C.ink}`,
        }}
      >
        <span aria-hidden="true" style={{ fontWeight: 700 }}>⠿</span>
        <b style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.06em" }}>
          {title}
        </b>
        {subtitle && <span style={{ fontSize: 9.5, opacity: 0.75 }}>{subtitle}</span>}
        <span style={{ flex: 1 }} />
        {right}
      </header>
      <div style={{ flex: 1, minHeight: 0, overflow: "auto", padding: 7 }}>{children}</div>
    </section>
  );
}

function PortPresentation({ refValue, compact = false }) {
  const lab = useLab();
  const { session, linkMode, linkSource, pickPort } = lab;
  const port = session.plan.port(refValue);
  const bindingClass = session.plan.bindingOf(refValue);
  const resource = session.runtime.resourceFor(refValue);
  const selected = linkSource && portKey(linkSource) === portKey(refValue);
  let compatibility = null;
  if (linkMode && linkSource && !selected) {
    try {
      compatibility = session.checkLink(linkSource, refValue);
    } catch (error) {
      compatibility = { compatible: false, explanation: { summary: asError(error).message } };
    }
  }
  const state = selected
    ? "source"
    : compatibility
      ? compatibility.compatible
        ? compatibility.alreadySameBinding
          ? "same"
          : "compatible"
        : "incompatible"
      : resource.state.kind === "conflict"
        ? "conflict"
        : "ordinary";
  const tone = state === "source"
    ? C.mustard
    : state === "compatible"
      ? C.green
      : state === "same"
        ? C.blue
        : state === "incompatible" || state === "conflict"
          ? C.red
          : C.lavender;
  const doc = `<port> ${displayPort(refValue)} · ${port.contract.semanticTag} · ${port.contract.mode} · ${bindingClass.bindingId} → ${resource.resourceId}`;

  return (
    <P
      ptype="port"
      value={refValue}
      doc={doc}
      block
      state={state}
      onActivate={() => (linkMode ? pickPort(refValue) : lab.inspect({ ptype: "port", value: refValue, doc }))}
      style={{
        display: "grid",
        gap: 2,
        border: `1px solid ${C.ink}`,
        borderLeft: `5px solid ${tone}`,
        background: selected ? C.sel : C.pane,
        padding: compact ? "3px 5px" : "5px 6px",
        cursor: "pointer",
        userSelect: "none",
      }}
    >
      <div style={{ display: "flex", alignItems: "baseline", gap: 5, minWidth: 0 }}>
        <b style={{ fontSize: compact ? 9.5 : 10.5 }}>{port.name}</b>
        <span style={{ fontSize: 8.5, color: C.faint }}>{port.contract.semanticTag}</span>
        <span style={{ flex: 1 }} />
        <span style={{ fontSize: 8.5, color: C.faint }}>{port.contract.mode}</span>
      </div>
      {!compact && (
        <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
          <Tag tone={tone}>{bindingClass.bindingId}</Tag>
          <Tag tone={resource.state.kind === "ready" ? C.sage : C.red}>{resource.resourceId}</Tag>
          <Tag tone={C.paneAlt}>{bindingClass.portKeys.length} port{bindingClass.portKeys.length === 1 ? "" : "s"}</Tag>
        </div>
      )}
    </P>
  );
}

function ResourceConflict({ refValue }) {
  const lab = useLab();
  const resource = lab.session.runtime.resourceFor(refValue);
  if (resource.state.kind !== "conflict") return null;
  const candidates = resource.state.candidates || [];
  return (
    <div style={{ border: `2px solid ${C.red}`, background: C.del, padding: 6, marginBottom: 6 }}>
      <b style={{ fontSize: 10 }}>UNRESOLVED SHARED RESOURCE</b>
      <div style={{ fontSize: 10, margin: "2px 0 5px", lineHeight: 1.4 }}>
        The quotient class exists, but its previous cells contained different values. Quotienting does not choose one.
      </div>
      <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
        {candidates.map((candidate, index) => {
          const state = candidate.state || candidate;
          if (state.kind !== "ready") return null;
          return (
            <MiniBtn
              key={index}
              tone={C.mustard}
              onClick={() => lab.mutate((session) => session.write(refValue, state.value))}
            >
              use {state.value?.key || canonicalStringify(state.value)}
            </MiniBtn>
          );
        })}
      </div>
    </div>
  );
}

function DocumentSelector({ refValue }) {
  const lab = useLab();
  const resource = lab.session.runtime.resourceFor(refValue);
  const current = resource.state.kind === "ready" ? resource.state.value?.key || "" : "";
  const port = lab.session.plan.port(refValue);
  const writable = port.contract.mode === "write" || port.contract.mode === "read-write";
  return (
    <select
      aria-label={`Document through ${displayPort(refValue)}`}
      value={current}
      disabled={!writable}
      onChange={(event) =>
        lab.mutate((session) =>
          session.write(refValue, { sort: "document", key: event.target.value }),
        )
      }
      style={{
        border: `1px solid ${C.ink}`,
        background: C.pane,
        fontFamily: "inherit",
        fontSize: 10.5,
        padding: "2px 4px",
        maxWidth: 180,
      }}
    >
      {resource.state.kind !== "ready" && <option value="">resolve conflict…</option>}
      {COMMON_FIXTURE.subjects.documents.map((doc) => (
        <option key={doc.key} value={doc.key} disabled={doc.status === "tombstone"}>
          {doc.title}{doc.status === "tombstone" ? " (deleted)" : ""}
        </option>
      ))}
    </select>
  );
}

function PortStrip({ refs }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: `repeat(${refs.length}, minmax(0, 1fr))`, gap: 5, marginBottom: 7 }}>
      {refs.map((refValue) => <PortPresentation key={portKey(refValue)} refValue={refValue} compact />)}
    </div>
  );
}

function SourceBrowser() {
  const lab = useLab();
  const targets = [
    ["chart", REFS.chartDocument],
    ["pipeline", REFS.pipelineDocument],
    ["table", REFS.tableDocument],
  ];
  return (
    <Tile title="source browser" color={C.warm} subtitle="domain objects">
      <div style={{ fontSize: 10, color: C.faint, lineHeight: 1.4, marginBottom: 6 }}>
        These are document presentations. The small target buttons write through a component port; if ports are linked, every projection observes the same cell.
      </div>
      {COMMON_FIXTURE.subjects.documents.map((doc) => (
        <P
          key={doc.key}
          ptype="document"
          value={{ sort: "document", key: doc.key }}
          doc={`<document> ${doc.title} · ${doc.key} · ${doc.status}`}
          block
          onActivate={() => lab.inspect({ ptype: "document", value: doc, doc: doc.title })}
          style={{
            border: `2px solid ${C.ink}`,
            borderLeft: `6px solid ${DOC_TONES[doc.key] || C.line}`,
            background: doc.status === "tombstone" ? C.paneAlt : C.pane,
            opacity: doc.status === "tombstone" ? 0.55 : 1,
            padding: 6,
            marginBottom: 6,
          }}
        >
          <div style={{ display: "flex", gap: 5, alignItems: "center", flexWrap: "wrap" }}>
            <b style={{ fontSize: 11 }}>{doc.title}</b>
            <Tag tone={DOC_TONES[doc.key]}>{doc.key}</Tag>
            <Tag tone={doc.status === "active" ? C.sage : C.line}>{doc.status}</Tag>
            <span style={{ flex: 1 }} />
            {targets.map(([label, refValue]) => (
              <MiniBtn
                key={label}
                disabled={doc.status !== "active"}
                title={`Write ${doc.key} through ${displayPort(refValue)}`}
                onClick={(event) => {
                  event?.stopPropagation?.();
                  lab.mutate((session) =>
                    session.write(refValue, { sort: "document", key: doc.key }),
                  );
                }}
              >
                → {label}
              </MiniBtn>
            ))}
          </div>
          <div style={{ marginTop: 4, display: "flex", gap: 3, flexWrap: "wrap" }}>
            {COMMON_FIXTURE.subjects.fields
              .filter((field) => field.document === doc.key)
              .map((field) => (
                <Tag key={field.key} tone={field.internal ? C.red : field.dataType === "number" ? C.blue : C.mint}>
                  {field.name}:{field.dataType}
                </Tag>
              ))}
          </div>
        </P>
      ))}
    </Tile>
  );
}

function ChartWidget() {
  const lab = useLab();
  const doc = documentFor(lab.session, REFS.chartDocument);
  const rows = rowsFor(lab.session, REFS.chartDocument);
  const selection = selectionFor(lab.session, REFS.chartSelection);
  const max = Math.max(1, ...rows.map((row) => row.temperature));
  return (
    <Tile title="chart" color={C.blue} subtitle="chart-1">
      <PortStrip refs={[REFS.chartDocument, REFS.chartSelection]} />
      <ResourceConflict refValue={REFS.chartDocument} />
      <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 7 }}>
        <b style={{ fontSize: 10 }}>DOCUMENT</b>
        <DocumentSelector refValue={REFS.chartDocument} />
        <span style={{ flex: 1 }} />
        <Tag tone={C.mustard}>{selection.length} selected</Tag>
      </div>
      {!doc ? (
        <div style={{ color: C.red, fontSize: 10.5 }}>Resolve the document binding before rendering.</div>
      ) : (
        <div style={{ border: `1px solid ${C.line}`, background: C.warm, padding: 6 }}>
          <div style={{ fontSize: 10, marginBottom: 6 }}>
            <b>{doc.title}</b> · temperature
          </div>
          <div style={{ display: "flex", alignItems: "end", gap: 8, height: 128, borderBottom: `1px solid ${C.ink}` }}>
            {rows.map((row) => {
              const selected = selection.includes(row.id);
              return (
                <P
                  key={row.id}
                  ptype="row"
                  value={{ sort: "row", key: row.id }}
                  doc={`<row> ${row.id} · ${row.station} · ${row.temperature}°`}
                  onActivate={() => lab.mutate((session) => toggleRow(session, REFS.chartSelection, row.id))}
                  style={{ flex: 1, alignSelf: "stretch", display: "flex", alignItems: "end", justifyContent: "center" }}
                >
                  <span
                    style={{
                      display: "grid",
                      placeItems: "end center",
                      width: "70%",
                      height: `${Math.max(10, (row.temperature / max) * 105)}px`,
                      background: selected ? C.red : C.blue,
                      border: `1px solid ${C.ink}`,
                      fontSize: 8.5,
                      fontWeight: 700,
                    }}
                  >
                    {row.temperature}
                  </span>
                </P>
              );
            })}
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 2 }}>
            {rows.map((row) => (
              <span key={row.id} style={{ flex: 1, textAlign: "center", fontSize: 8.5 }}>{row.station}</span>
            ))}
          </div>
        </div>
      )}
    </Tile>
  );
}

function PipelineWidget() {
  const lab = useLab();
  const doc = documentFor(lab.session, REFS.pipelineDocument);
  const filter = readyValue(lab.session, REFS.pipelineFilter);
  const output = documentFor(lab.session, REFS.pipelineOutput);
  return (
    <Tile title="pipeline" color={C.sage} subtitle="pipeline-1">
      <PortStrip refs={[REFS.pipelineDocument, REFS.pipelineFilter, REFS.pipelineOutput]} />
      <ResourceConflict refValue={REFS.pipelineDocument} />
      <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 8 }}>
        <b style={{ fontSize: 10 }}>INPUT</b>
        <DocumentSelector refValue={REFS.pipelineDocument} />
      </div>
      <div style={{ display: "grid", gap: 6 }}>
        {[
          ["01", "load", doc ? doc.title : "unresolved document", C.blue],
          ["02", "filter", filter?.op === "true" ? "all rows" : canonicalStringify(filter), C.mustard],
          ["03", "derive", "normalize pressure + annotate station", C.mint],
          ["04", "output", output ? output.title : "uninitialized", C.rose],
        ].map(([n, title, detail, tone]) => (
          <div key={n} style={{ display: "flex", gap: 7, alignItems: "center", border: `1px solid ${C.ink}`, borderLeft: `6px solid ${tone}`, padding: 5 }}>
            <b style={{ fontSize: 10 }}>{n}</b>
            <b style={{ fontSize: 10.5 }}>{title}</b>
            <span style={{ fontSize: 10, color: C.faint }}>{detail}</span>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 8, border: `1px dashed ${C.red}`, padding: 5, background: C.del, fontSize: 10, lineHeight: 1.4 }}>
        <b>NOT AN IDENTITY LINK:</b> table.selection and pipeline.filter carry different semantic tags, payload sorts, and update algebras. They need P08's transformed-link layer.
      </div>
    </Tile>
  );
}

function TableWidget() {
  const lab = useLab();
  const doc = documentFor(lab.session, REFS.tableDocument);
  const rows = rowsFor(lab.session, REFS.tableDocument);
  const selection = selectionFor(lab.session, REFS.tableSelection);
  return (
    <Tile title="table" color={C.mustard} subtitle="table-1">
      <PortStrip refs={[REFS.tableDocument, REFS.tableSelection]} />
      <ResourceConflict refValue={REFS.tableDocument} />
      <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 7 }}>
        <b style={{ fontSize: 10 }}>DOCUMENT</b>
        <DocumentSelector refValue={REFS.tableDocument} />
        <span style={{ flex: 1 }} />
        <Tag tone={C.red}>{selection.length} selected</Tag>
      </div>
      {!doc ? (
        <div style={{ color: C.red, fontSize: 10.5 }}>Resolve the document binding before rendering.</div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 10 }}>
          <thead>
            <tr style={{ background: C.paneAlt }}>
              {['', 'station', 'temperature', 'pressure'].map((key) => (
                <th key={key} style={{ textAlign: "left", borderBottom: `2px solid ${C.ink}`, padding: "3px 4px" }}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const selected = selection.includes(row.id);
              return (
                <tr
                  key={row.id}
                  onClick={() => lab.mutate((session) => toggleRow(session, REFS.tableSelection, row.id))}
                  style={{ cursor: "pointer", background: selected ? C.sel : C.pane, borderBottom: `1px dotted ${C.line}` }}
                >
                  <td style={{ padding: 3 }}><span style={{ display: "block", width: 10, height: 10, border: `2px solid ${C.ink}`, background: selected ? C.red : C.pane }} /></td>
                  <td style={{ padding: 3 }}>{row.station}</td>
                  <td style={{ padding: 3 }}>{row.temperature}</td>
                  <td style={{ padding: 3 }}>{row.pressure}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </Tile>
  );
}

function BindingClassesPanel() {
  const lab = useLab();
  const { session } = lab;
  return (
    <div style={{ display: "grid", gap: 7 }}>
      {session.plan.classes.map((bindingClass) => {
        const resource = session.runtime.resources.get(bindingClass.bindingId);
        return (
          <section key={bindingClass.bindingId} style={{ border: `2px solid ${C.ink}`, padding: 6, background: C.pane }}>
            <div style={{ display: "flex", gap: 5, alignItems: "center", flexWrap: "wrap" }}>
              <Tag tone={C.lavender}>{bindingClass.bindingId}</Tag>
              <Tag tone={resource.state.kind === "ready" ? C.sage : C.red}>{resource.resourceId}</Tag>
              <b style={{ fontSize: 10.5 }}>{bindingClass.contract.semanticTag}</b>
              <span style={{ fontSize: 9.5, color: C.faint }}>{bindingClass.contract.payloadSort} · {bindingClass.contract.mode}</span>
              <span style={{ flex: 1 }} />
              <span style={{ fontSize: 9.5, color: C.faint }}>{bindingClass.linkIds.length} equation{bindingClass.linkIds.length === 1 ? "" : "s"}</span>
            </div>
            <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginTop: 5 }}>
              {bindingClass.portKeys.map((key) => {
                const refValue = parsePortKey(key);
                return <Tag key={key} tone={C.blue}>{displayPort(refValue)}</Tag>;
              })}
            </div>
            <pre style={{ margin: "6px 0 0", padding: 5, background: C.paneAlt, border: `1px solid ${C.line}`, fontSize: 9.5, whiteSpace: "pre-wrap" }}>
              {canonicalStringify(resource.state)}
            </pre>
          </section>
        );
      })}
    </div>
  );
}

function LinksPanel() {
  const lab = useLab();
  const links = lab.session.links;
  return (
    <div>
      <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 7 }}>
        <b style={{ fontSize: 10 }}>UNLINK INITIALIZATION</b>
        <select
          value={lab.splitPolicy}
          onChange={(event) => lab.setSplitPolicy(event.target.value)}
          style={{ fontFamily: "inherit", fontSize: 10, border: `1px solid ${C.ink}`, padding: 2 }}
        >
          <option value="copy-current">copy current shared value</option>
          <option value="restore-history">restore pre-link private values</option>
          <option value="reset">reset from declared defaults</option>
        </select>
      </div>
      {!links.length && <div style={{ fontSize: 10.5, color: C.faint }}>No identity-link declarations. Every port is a singleton binding class.</div>}
      {links.map((link) => (
        <div key={link.linkId} style={{ display: "flex", gap: 6, alignItems: "center", borderBottom: `1px dotted ${C.line}`, padding: "4px 0" }}>
          <Tag tone={C.mustard}>{link.linkId}</Tag>
          <code style={{ fontSize: 10 }}>{displayPort(link.left)}</code>
          <b>≡</b>
          <code style={{ fontSize: 10 }}>{displayPort(link.right)}</code>
          <span style={{ flex: 1 }} />
          <MiniBtn
            tone={C.del}
            title="Remove this declaration and recompile the quotient"
            onClick={() =>
              lab.mutate((session) =>
                session.edit({
                  kind: "unlink",
                  linkId: link.linkId,
                  splitPolicy: { kind: lab.splitPolicy },
                }),
              )
            }
          >
            unlink
          </MiniBtn>
        </div>
      ))}
      <div style={{ marginTop: 8, fontSize: 10, lineHeight: 1.45, background: C.warm, border: `1px solid ${C.line}`, padding: 6 }}>
        The session persists declarations, not union-find parents. Removing an equation recompiles the generated equivalence relation. If another path still connects the endpoints, the class remains linked.
      </div>
    </div>
  );
}

function CompatibilityPanel() {
  const lab = useLab();
  const cases = [
    ["primary documents", REFS.chartDocument, REFS.pipelineDocument],
    ["row selections", REFS.chartSelection, REFS.tableSelection],
    ["same payload, different semantic/mode", REFS.pipelineDocument, REFS.pipelineOutput],
    ["selection versus filter", REFS.tableSelection, REFS.pipelineFilter],
  ];
  const authorityLeft = lab.session.plan.port(REFS.chartDocument).contract;
  const authorityRight = {
    ...authorityLeft,
    contractId: "admin-document/0.1",
    authorityDomain: "admin",
  };
  const authorityCheck = checkIdentityCompatibility(authorityLeft, authorityRight);
  return (
    <div style={{ display: "grid", gap: 6 }}>
      {cases.map(([label, left, right]) => {
        const check = lab.session.checkLink(left, right);
        return (
          <div key={label} style={{ border: `1px solid ${C.ink}`, borderLeft: `5px solid ${check.compatible ? C.green : C.red}`, padding: 6 }}>
            <div style={{ display: "flex", gap: 5, alignItems: "center", flexWrap: "wrap" }}>
              <b style={{ fontSize: 10.5 }}>{label}</b>
              <code style={{ fontSize: 9.5 }}>{displayPort(left)}</code>
              <span>↔</span>
              <code style={{ fontSize: 9.5 }}>{displayPort(right)}</code>
              <span style={{ flex: 1 }} />
              <Tag tone={check.compatible ? C.green : C.red}>{check.compatible ? "IDENTITY-COMPATIBLE" : "REJECTED"}</Tag>
            </div>
            {!check.compatible && (
              <div style={{ marginTop: 4, fontSize: 9.5, color: C.faint }}>
                {check.mismatches.map((mismatch) => mismatch.field).join(", ")}
              </div>
            )}
          </div>
        );
      })}
      <div style={{ border: `1px solid ${C.ink}`, borderLeft: `5px solid ${C.red}`, padding: 6 }}>
        <div style={{ display: "flex", gap: 5, alignItems: "center", flexWrap: "wrap" }}>
          <b style={{ fontSize: 10.5 }}>same everything except authority</b>
          <span style={{ flex: 1 }} />
          <Tag tone={C.red}>REJECTED</Tag>
        </div>
        <div style={{ marginTop: 4, fontSize: 9.5, color: C.faint }}>
          mismatch: {authorityCheck.mismatches.map((item) => item.field).join(", ")}. Raw payload type equality is intentionally insufficient.
        </div>
      </div>
    </div>
  );
}

function PlanChecksPanel() {
  const lab = useLab();
  const checks = runCurrentPlanChecks(lab.session);
  const rows = [
    ["every declared port has one projection", checks.laws.checks.totalProjection],
    ["every port belongs to exactly one class", checks.laws.checks.oneClassPerPort],
    ["linked endpoints project equally", checks.laws.checks.linkedEndpointsEqual],
    ["classes are contract-homogeneous", checks.laws.checks.homogeneousClasses],
    ["reference and union-find plans agree", checks.compilerAgreement],
    ["all projections in a class alias one resource", checks.allProjectionsAlias],
    ["binding certificate checks", checks.certificate.valid],
  ];
  return (
    <div style={{ display: "grid", gap: 4 }}>
      {rows.map(([label, pass]) => (
        <div key={label} style={{ display: "flex", alignItems: "center", gap: 6, borderBottom: `1px dotted ${C.line}`, padding: "3px 0" }}>
          <span aria-hidden="true" style={{ color: pass ? C.green : C.red, fontWeight: 700 }}>{pass ? "✓" : "✕"}</span>
          <span style={{ fontSize: 10.5 }}>{label}</span>
          <span style={{ flex: 1 }} />
          <Tag tone={pass ? C.green : C.red}>{pass ? "checked" : "failed"}</Tag>
        </div>
      ))}
      <div style={{ fontSize: 9.5, color: C.faint, lineHeight: 1.45, marginTop: 5 }}>
        These are executable checks of the current finite plan. The bundled Lean file supplies proof terms for relation-to-quotient and factorization theorems in a small indexed model; Lean was unavailable to check it here, and it does not certify this JavaScript process.
      </div>
    </div>
  );
}

function ExperimentsPanel() {
  const lab = useLab();
  const [result, setResult] = useState(null);
  const run = (name, thunk) => {
    const started = performance.now();
    try {
      const payload = thunk();
      setResult({ name, ok: true, durationMs: performance.now() - started, payload });
    } catch (error) {
      setResult({ name, ok: false, durationMs: performance.now() - started, error: errorData(error) });
    }
  };
  return (
    <div>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 8 }}>
        <Btn
          tone={C.blue}
          onClick={() => run("compiler differential", () => runCompilerDifferential({ cases: 200, seed: 17, portCount: 40, linkCount: 90 }))}
        >
          compare 200 random graphs
        </Btn>
        <Btn
          tone={C.sage}
          onClick={() => run("transitive quotient", () => {
            lab.reset();
            lab.mutate((session) => session.edit({ kind: "link", link: { linkId: "demo-cp", left: REFS.chartDocument, right: REFS.pipelineDocument }, mergePolicy: { kind: "prefer-left" } }));
            lab.mutate((session) => session.edit({ kind: "link", link: { linkId: "demo-pt", left: REFS.pipelineDocument, right: REFS.tableDocument }, mergePolicy: { kind: "require-equal" } }));
            return { binding: lab.getSession().plan.bindingIdOf(REFS.chartDocument) };
          })}
        >
          build chart ≡ pipeline ≡ table
        </Btn>
        <Btn
          tone={C.mustard}
          onClick={() => run("unlink is not inverse", () => {
            lab.reset();
            lab.mutate((session) => session.edit({ kind: "link", link: { linkId: "demo-unlink", left: REFS.chartDocument, right: REFS.pipelineDocument }, mergePolicy: { kind: "prefer-left" } }));
            lab.mutate((session) => session.write(REFS.pipelineDocument, { sort: "document", key: "doc-b" }));
            lab.mutate((session) => session.edit({ kind: "unlink", linkId: "demo-unlink", splitPolicy: { kind: "restore-history" } }));
            return {
              chart: lab.getSession().read(REFS.chartDocument),
              pipeline: lab.getSession().read(REFS.pipelineDocument),
            };
          })}
        >
          restore private values after unlink
        </Btn>
        <Btn
          tone={C.rose}
          onClick={() => run("duplicate equation", () => {
            lab.reset();
            lab.mutate((session) => session.edit({ kind: "link", link: { linkId: "edge-1", left: REFS.chartDocument, right: REFS.pipelineDocument }, mergePolicy: { kind: "prefer-left" } }));
            lab.mutate((session) => session.edit({ kind: "link", link: { linkId: "edge-2", left: REFS.pipelineDocument, right: REFS.chartDocument }, mergePolicy: { kind: "require-equal" } }));
            const before = lab.getSession().plan.bindingIdOf(REFS.chartDocument);
            lab.mutate((session) => session.edit({ kind: "unlink", linkId: "edge-1", splitPolicy: { kind: "copy-current" } }));
            const current = lab.getSession();
            const after = current.plan.bindingIdOf(REFS.chartDocument);
            return {
              before,
              after,
              stillLinked:
                current.plan.bindingIdOf(REFS.chartDocument) ===
                current.plan.bindingIdOf(REFS.pipelineDocument),
            };
          })}
        >
          duplicate equation is idempotent
        </Btn>
      </div>
      {result && (
        <div style={{ border: `2px solid ${result.ok ? C.green : C.red}`, background: result.ok ? C.add : C.del, padding: 6 }}>
          <div style={{ display: "flex", gap: 6 }}>
            <b style={{ fontSize: 10.5 }}>{result.name}</b>
            <span style={{ flex: 1 }} />
            <span style={{ fontSize: 9.5 }}>{result.durationMs.toFixed(2)} ms</span>
          </div>
          <pre style={{ fontSize: 9.5, whiteSpace: "pre-wrap", margin: "5px 0 0" }}>{JSON.stringify(result.ok ? result.payload : result.error, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

function TheoryPanel() {
  return (
    <div style={{ fontSize: 10.5, lineHeight: 1.55 }}>
      <p><b>Typed fibers.</b> Ports are partitioned by their normalized identity contract τ. Links are accepted only within one fiber P<sub>τ</sub>.</p>
      <div style={{ border: `1px solid ${C.ink}`, background: C.warm, padding: 8, textAlign: "center", fontSize: 13 }}>
        s<sub>τ</sub>, t<sub>τ</sub> : R<sub>τ</sub> ⇉ P<sub>τ</sub> &nbsp;&nbsp; and &nbsp;&nbsp; q<sub>τ</sub> : P<sub>τ</sub> → Q<sub>τ</sub>
      </div>
      <p>The compiler forms the smallest equivalence relation containing every declared endpoint equation. The class projection satisfies q<sub>τ</sub>∘s<sub>τ</sub> = q<sub>τ</sub>∘t<sub>τ</sub>.</p>
      <div style={{ border: `1px solid ${C.ink}`, background: C.paneAlt, padding: 8, textAlign: "center", fontSize: 13 }}>
        local port p &nbsp; —q→ &nbsp; binding class [p] &nbsp; —v→ &nbsp; mutable resource &nbsp; —render→ &nbsp; widget
      </div>
      <p><b>Universal factorization.</b> A port interpretation g that gives equal results to every linked pair factors through Q: there is a unique ḡ with g = ḡ∘q. The API method <code>plan.factor(g)</code> checks the premise and constructs the factor.</p>
      <p><b>Boundary.</b> The quotient explains aliasing. It does not choose merge values, define transaction atomicity, schedule feedback, grant authority, or provide an inverse for unlinking. Those decisions appear as explicit runtime policies.</p>
    </div>
  );
}

function InspectorPanel() {
  const lab = useLab();
  const inspected = lab.inspected;
  if (!inspected) return <div style={{ color: C.faint, fontSize: 10.5 }}>Right-click or activate a port outside link mode to inspect it.</div>;
  let value = inspected.value;
  if (inspected.ptype === "port") {
    value = lab.session.explain([inspected.value]);
  }
  return (
    <div>
      <div style={{ display: "flex", gap: 5, alignItems: "center", marginBottom: 5 }}>
        <Tag tone={C.lavender}>&lt;{inspected.ptype}&gt;</Tag>
        <b style={{ fontSize: 10.5 }}>{inspected.doc}</b>
      </div>
      <pre style={{ margin: 0, padding: 7, border: `1px solid ${C.line}`, background: C.paneAlt, maxHeight: 380, overflow: "auto", whiteSpace: "pre-wrap", fontSize: 9.5 }}>
        {JSON.stringify(value, null, 2)}
      </pre>
    </div>
  );
}

function ConflictPrompt() {
  const lab = useLab();
  if (!lab.pendingLink) return null;
  const { left, right, leftState, rightState } = lab.pendingLink;
  return (
    <div style={{ background: C.red, color: C.paper, borderBottom: `2px solid ${C.ink}`, padding: "6px 10px", display: "flex", gap: 7, alignItems: "center", flexWrap: "wrap" }}>
      <b>MERGE VALUE REQUIRED</b>
      <span style={{ fontSize: 10.5 }}>{displayPort(left)} and {displayPort(right)} currently differ.</span>
      <span style={{ flex: 1 }} />
      <Btn tone={C.mustard} onClick={() => lab.commitPendingLink({ kind: "prefer-left" })}>
        keep {leftState.value?.key || "left"}
      </Btn>
      <Btn tone={C.sage} onClick={() => lab.commitPendingLink({ kind: "prefer-right" })}>
        keep {rightState.value?.key || "right"}
      </Btn>
      <Btn tone={C.paneAlt} onClick={lab.cancelPendingLink}>cancel</Btn>
    </div>
  );
}

const PANELS = [
  ["classes", "binding classes"],
  ["links", "link declarations"],
  ["compatibility", "compatibility matrix"],
  ["checks", "plan checks"],
  ["experiments", "experiments"],
  ["theory", "semantics"],
  ["inspector", "inspector"],
  ["trace", "trace"],
];

export default function App() {
  const sessionRef = useRef(null);
  if (!sessionRef.current) sessionRef.current = createDemoSession();
  const [, setVersion] = useState(0);
  const [mouseDoc, setMouseDoc] = useState(null);
  const [notice, setNotice] = useState({ tone: C.sage, text: "Ready. Enter LINK PORTS mode to add endpoint equations." });
  const [linkMode, setLinkMode] = useState(false);
  const [linkSource, setLinkSource] = useState(null);
  const [pendingLink, setPendingLink] = useState(null);
  const [splitPolicy, setSplitPolicy] = useState("copy-current");
  const [panel, setPanel] = useState("classes");
  const [inspected, setInspected] = useState(null);
  const linkCounter = useRef(1);
  const session = sessionRef.current;

  const refresh = useCallback(() => setVersion((value) => value + 1), []);

  const mutate = useCallback((operation) => {
    try {
      const result = operation(sessionRef.current);
      setNotice({ tone: C.sage, text: `OK · ${result?.kind || "state updated"}` });
      refresh();
      return result;
    } catch (error) {
      const problem = asError(error);
      setNotice({ tone: C.red, text: `${problem.code} · ${problem.message}` });
      setInspected({ ptype: "error", value: errorData(problem), doc: problem.message });
      setPanel("inspector");
      refresh();
      return null;
    }
  }, [refresh]);

  const reset = useCallback((compiler = sessionRef.current.compiler === "compare" ? "union-find" : sessionRef.current.compiler) => {
    sessionRef.current = createDemoSession(compiler);
    setLinkMode(false);
    setLinkSource(null);
    setPendingLink(null);
    setNotice({ tone: C.sage, text: "Fixture reset: chart=doc-a, pipeline=doc-b, table=doc-a." });
    refresh();
  }, [refresh]);

  const inspect = useCallback((item) => {
    setInspected(item);
    setPanel("inspector");
  }, []);

  const addLink = useCallback((left, right, mergePolicy) => {
    const linkId = `link-${linkCounter.current++}-${shortHash([displayPort(left), displayPort(right)].sort().join("|"), 6)}`;
    const result = mutate((current) =>
      current.edit({
        kind: "link",
        link: {
          linkId,
          left,
          right,
          provenance: { source: "interactive-demo", actor: "user" },
        },
        mergePolicy,
      }),
    );
    if (result) {
      setNotice({ tone: C.sage, text: `${displayPort(left)} ≡ ${displayPort(right)} compiled as ${sessionRef.current.plan.bindingIdOf(left)}.` });
    }
    setLinkSource(null);
    setPendingLink(null);
    setLinkMode(false);
  }, [mutate]);

  const pickPort = useCallback((refValue) => {
    if (!linkSource) {
      setLinkSource(refValue);
      setNotice({ tone: C.mustard, text: `SOURCE ${displayPort(refValue)} · choose an identity-compatible target.` });
      return;
    }
    if (portKey(linkSource) === portKey(refValue)) {
      setLinkSource(null);
      setNotice({ tone: C.paneAlt, text: "Link source cleared." });
      return;
    }
    try {
      const check = sessionRef.current.checkLink(linkSource, refValue);
      if (!check.compatible) {
        setNotice({ tone: C.red, text: check.explanation.summary });
        setInspected({ ptype: "compatibility-rejection", value: check, doc: check.explanation.summary });
        setPanel("inspector");
        return;
      }
      const leftResource = sessionRef.current.runtime.resourceFor(linkSource);
      const rightResource = sessionRef.current.runtime.resourceFor(refValue);
      const leftState = leftResource.snapshot().state;
      const rightState = rightResource.snapshot().state;
      if (leftState.kind === "ready" && rightState.kind === "ready" && !semanticEqual(leftState.value, rightState.value)) {
        setPendingLink({ left: linkSource, right: refValue, leftState, rightState });
        return;
      }
      addLink(linkSource, refValue, { kind: "require-equal" });
    } catch (error) {
      const problem = asError(error);
      setNotice({ tone: C.red, text: `${problem.code} · ${problem.message}` });
    }
  }, [addLink, linkSource]);

  const commitPendingLink = useCallback((policy) => {
    if (!pendingLink) return;
    addLink(pendingLink.left, pendingLink.right, policy);
  }, [addLink, pendingLink]);

  const labValue = useMemo(() => ({
    session,
    getSession: () => sessionRef.current,
    mutate,
    reset,
    mouseDoc,
    setMouseDoc,
    notice,
    setNotice,
    linkMode,
    linkSource,
    pickPort,
    pendingLink,
    commitPendingLink,
    cancelPendingLink: () => setPendingLink(null),
    splitPolicy,
    setSplitPolicy,
    inspect,
    inspected,
  }), [
    session,
    mutate,
    reset,
    mouseDoc,
    notice,
    linkMode,
    linkSource,
    pickPort,
    pendingLink,
    commitPendingLink,
    splitPolicy,
    inspect,
    inspected,
  ]);

  const activePanel = {
    classes: <BindingClassesPanel />,
    links: <LinksPanel />,
    compatibility: <CompatibilityPanel />,
    checks: <PlanChecksPanel />,
    experiments: <ExperimentsPanel />,
    theory: <TheoryPanel />,
    inspector: <InspectorPanel />,
    trace: (
      <pre style={{ margin: 0, maxHeight: 420, overflow: "auto", border: `1px solid ${C.line}`, background: C.paneAlt, padding: 7, fontSize: 9.5, whiteSpace: "pre-wrap" }}>
        {JSON.stringify([...session.events].reverse(), null, 2)}
      </pre>
    ),
  }[panel];

  return (
    <LabCtx.Provider value={labValue}>
      <div style={{ fontFamily: "'IBM Plex Mono', ui-monospace, Menlo, Consolas, monospace", background: C.paper, color: C.ink, minHeight: "100vh", display: "flex", flexDirection: "column", fontSize: 12 }}>
        <style>{`
          * { box-sizing: border-box; }
          button, select, input, textarea { font-family: inherit; }
          .pres { outline: none; }
          .pres[role="button"] { cursor: pointer; }
          .pres[role="button"]:hover, .pres[role="button"]:focus-visible { outline: 2px dotted ${C.ink}; outline-offset: 1px; }
          .pres-compatible { animation: compatiblePulse 1s infinite; }
          .pres-source { outline: 3px solid ${C.mustard} !important; }
          .pres-incompatible { opacity: .62; }
          .pres-conflict { animation: conflictPulse .8s infinite; }
          @keyframes compatiblePulse { 50% { background: ${C.add}; } }
          @keyframes conflictPulse { 50% { background: ${C.del}; } }
          @media (prefers-reduced-motion: reduce) { .pres-compatible, .pres-conflict { animation: none; } }
          ::-webkit-scrollbar { width: 11px; height: 11px; }
          ::-webkit-scrollbar-thumb { background: ${C.line}; border: 3px solid ${C.pane}; }
        `}</style>

        <header style={{ background: C.ink, color: C.paper, display: "flex", alignItems: "center", gap: 12, padding: "5px 10px", flexWrap: "wrap" }}>
          <b style={{ letterSpacing: "0.22em", fontSize: 12 }}>P B U I</b>
          <span style={{ color: C.mustard, fontSize: 10.5, letterSpacing: "0.1em" }}>P06 · BINDING QUOTIENT LAB</span>
          <span style={{ flex: 1 }} />
          <label style={{ fontSize: 10, display: "flex", alignItems: "center", gap: 4 }}>
            compiler
            <select
              value={session.compiler}
              onChange={(event) => mutate((current) => current.setCompiler(event.target.value))}
              style={{ fontFamily: "inherit", fontSize: 10, border: `1px solid ${C.paper}`, background: C.ink, color: C.paper }}
            >
              <option value="union-find">union-find</option>
              <option value="reference">reference closure</option>
              <option value="compare">compare both</option>
            </select>
          </label>
          <span style={{ fontSize: 9.5, color: C.faint }}>{session.plan.ports.length} ports · {session.plan.links.length} equations · {session.plan.classes.length} classes</span>
        </header>

        <ConflictPrompt />

        {linkMode && (
          <div style={{ background: C.mustard, color: C.ink, borderBottom: `2px solid ${C.ink}`, padding: "4px 10px", fontWeight: 700, fontSize: 10.5 }}>
            LINK PORTS — {linkSource ? `source ${displayPort(linkSource)}; choose a green compatible target` : "choose a source port"} — Escape/cancel exits
          </div>
        )}

        <div style={{ display: "flex", gap: 6, alignItems: "center", padding: "6px 8px", borderBottom: `1px solid ${C.line}`, flexWrap: "wrap" }}>
          <Btn
            tone={linkMode ? C.mustard : C.blue}
            pressed={linkMode}
            onClick={() => {
              setLinkMode((value) => !value);
              setLinkSource(null);
              setPendingLink(null);
            }}
          >
            {linkMode ? "cancel linking" : "link ports"}
          </Btn>
          <Btn tone={C.paneAlt} onClick={() => reset()}>reset fixture</Btn>
          <Btn tone={C.sage} onClick={() => setPanel("checks")}>check current plan</Btn>
          <Btn tone={C.lavender} onClick={() => setPanel("theory")}>show semantics</Btn>
          <span style={{ flex: 1 }} />
          <Tag tone={session.runtime.churn.createdResources ? C.mustard : C.sage}>
            churn: {session.runtime.churn.reusedResources} reused / {session.runtime.churn.createdResources} new / {session.runtime.churn.disposedResources} disposed
          </Tag>
          <Tag tone={C.paneAlt}>{session.plan.revision}</Tag>
        </div>

        <main style={{ display: "grid", gridTemplateColumns: "minmax(250px, .8fr) minmax(300px, 1fr)", gap: 7, padding: 8, minHeight: 0 }}>
          <SourceBrowser />
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(280px, 1fr))", gap: 7, minWidth: 0 }}>
            <ChartWidget />
            <PipelineWidget />
            <div style={{ gridColumn: "1 / -1" }}><TableWidget /></div>
          </div>
        </main>

        <section style={{ margin: "0 8px 8px", border: `2px solid ${C.ink}`, background: C.pane }}>
          <div style={{ display: "flex", gap: 4, padding: "5px 6px 0", flexWrap: "wrap", background: C.paneAlt, borderBottom: `2px solid ${C.ink}` }}>
            {PANELS.map(([id, label]) => (
              <button
                key={id}
                type="button"
                onClick={() => setPanel(id)}
                style={{
                  fontFamily: "inherit",
                  border: `1px solid ${C.ink}`,
                  borderBottom: panel === id ? `4px solid ${C.red}` : `1px solid ${C.ink}`,
                  background: panel === id ? C.sel : C.pane,
                  padding: "3px 7px",
                  fontSize: 9.5,
                  fontWeight: panel === id ? 700 : 400,
                  cursor: "pointer",
                }}
              >
                {label}
              </button>
            ))}
          </div>
          <div style={{ padding: 8, maxHeight: 480, overflow: "auto" }}>{activePanel}</div>
        </section>

        <footer style={{ background: C.ink, color: C.paper, padding: "4px 10px", display: "flex", gap: 12, alignItems: "center", fontSize: 10.5 }}>
          <span style={{ color: notice.tone, fontWeight: 700 }}>{linkMode ? "LINK MODE" : "READY"}</span>
          <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{mouseDoc || notice.text}</span>
          <span style={{ color: C.faint }}>right-click presentations to inspect</span>
        </footer>
      </div>
    </LabCtx.Provider>
  );
}
