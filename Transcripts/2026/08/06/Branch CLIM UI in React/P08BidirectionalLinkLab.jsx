import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  DEFAULT_SELECTION,
  WORKBENCH_ROWS,
  diffSelection,
  normalizeFilter,
  selectionFilterConsistent,
  selectionToExactFilter,
} from "../dist/src/domain.js";
import { createIdentitySession } from "../dist/src/identity.js";
import { runLawHarness } from "../dist/src/laws.js";
import {
  asymmetricSelectionLens,
  deltaSelectionFilterPolicy,
  directedReplacementPolicy,
  symmetricSelectionFilterPolicy,
} from "../dist/src/policies.js";
import { propagateBackward, propagateForward } from "../dist/src/policy-helpers.js";
import { resolveConflict } from "../dist/src/repair.js";
import { FEEDBACK_SCENARIOS, simulateFeedback } from "../dist/src/scheduler.js";
import { LINK_TAXONOMY } from "../dist/src/taxonomy.js";

const C = {
  paper: "#ffffff",
  pane: "#ffffff",
  paneAlt: "#f1f1ee",
  ink: "#23262b",
  faint: "#7b8087",
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
  warm: "#faf7ee",
};

const POLICY_OPTIONS = [
  { id: directedReplacementPolicy.metadata.id, label: "directed replacement", policy: directedReplacementPolicy },
  { id: asymmetricSelectionLens.metadata.id, label: "partial asymmetric lens", policy: asymmetricSelectionLens },
  { id: symmetricSelectionFilterPolicy.metadata.id, label: "symmetric repair", policy: symmetricSelectionFilterPolicy },
  { id: deltaSelectionFilterPolicy.metadata.id, label: "delta repair", policy: deltaSelectionFilterPolicy },
];

const UiContext = createContext(null);
const useUi = () => useContext(UiContext);

function Presentation({ ptype, value, doc, children, block, onActivate, disabled }) {
  const ui = useUi();
  const acceptable = !disabled && ui.accepting && ui.accepting.types.includes(ptype) && !ui.accepting.exclude?.includes(value?.endpoint);
  const Tag = block ? "div" : "span";
  const activate = () => {
    if (acceptable) {
      ui.accepting.resolve({ ptype, value });
      ui.setAccepting(null);
    } else if (onActivate) {
      onActivate();
    }
  };
  return (
    <Tag
      className={`p08-pres ${acceptable ? "p08-acceptable" : ""} ${disabled ? "p08-disabled" : ""}`}
      role={acceptable || onActivate ? "button" : undefined}
      tabIndex={acceptable || onActivate ? 0 : undefined}
      onClick={(event) => {
        event.stopPropagation();
        activate();
      }}
      onKeyDown={(event) => {
        if ((event.key === "Enter" || event.key === " ") && (acceptable || onActivate)) {
          event.preventDefault();
          activate();
        }
      }}
      onContextMenu={(event) => {
        event.preventDefault();
        event.stopPropagation();
        ui.setMenu({ x: event.clientX, y: event.clientY, ptype, value, doc });
      }}
      onMouseEnter={() => ui.setMouseDoc(doc ?? `<${ptype}>`)}
      onMouseLeave={() => ui.setMouseDoc(null)}
    >
      {children}
    </Tag>
  );
}

function Button({ children, onClick, tone = C.blue, disabled, title }) {
  return (
    <button
      type="button"
      className="p08-btn"
      style={{ background: disabled ? C.paneAlt : tone }}
      onClick={onClick}
      disabled={disabled}
      title={title}
    >
      {children}
    </button>
  );
}

function Tag({ children, tone = C.paneAlt }) {
  return <span className="p08-tag" style={{ borderLeftColor: tone }}>{children}</span>;
}

function Tile({ title, tone, children, right }) {
  return (
    <section className="p08-tile">
      <header className="p08-tile-head" style={{ background: tone }}>
        <strong>{title}</strong>
        <span className="p08-grow" />
        {right}
      </header>
      <div className="p08-tile-body">{children}</div>
    </section>
  );
}

function PortCard({ endpoint, ptype, label, contract, tone, onBeginLink, linked, value }) {
  return (
    <Presentation
      ptype={ptype}
      value={{ endpoint, contract, value }}
      doc={`<${ptype}> ${endpoint} · ${contract}`}
      block
    >
      <div className={`p08-port ${linked ? "p08-port-linked" : ""}`} style={{ borderLeftColor: tone }}>
        <div>
          <strong>{label}</strong>
          <div className="p08-micro">{endpoint}</div>
        </div>
        <span className="p08-grow" />
        <Tag tone={tone}>{contract}</Tag>
        {onBeginLink && <Button tone={C.paneAlt} onClick={(event) => {
          event?.stopPropagation?.();
          onBeginLink();
        }}>link…</Button>}
      </div>
    </Presentation>
  );
}

function FilterCode({ filter }) {
  return <pre className="p08-code">{JSON.stringify(normalizeFilter(filter), null, 2)}</pre>;
}

function RepairPanel({ repair, onChoose }) {
  if (!repair) return <div className="p08-empty">No repair has run yet.</div>;
  return (
    <div className="p08-repair">
      <div className="p08-row">
        <Tag tone={repair.kind === "conflict" || repair.kind === "invalid" ? C.red : repair.kind === "updated" ? C.mustard : C.sage}>
          {repair.kind}
        </Tag>
        <strong>{repair.evidence.summary}</strong>
      </div>
      {!!repair.evidence.informationLoss.length && (
        <div className="p08-callout p08-callout-warn">
          <b>information loss</b>
          <ul>{repair.evidence.informationLoss.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
      )}
      {!!repair.evidence.preservedIntent.length && (
        <div className="p08-callout">
          <b>preserved intent</b>
          <ul>{repair.evidence.preservedIntent.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
      )}
      {repair.kind === "conflict" && (
        <div>
          <div className="p08-section-label">explicit choices</div>
          {repair.choices.map((choice) => (
            <button key={choice.choiceId} type="button" className="p08-choice" onClick={() => onChoose(choice)}>
              <span><b>{choice.label}</b><br /><span className="p08-micro">{choice.explanation}</span></span>
              <Tag tone={C.mustard}>score {choice.score.toFixed(2)}</Tag>
            </button>
          ))}
        </div>
      )}
      <details>
        <summary>evidence record</summary>
        <pre className="p08-code">{JSON.stringify(repair.evidence, null, 2)}</pre>
      </details>
    </div>
  );
}

function ChartTile({ selection, onToggle, document, setDocument, linked, beginIdentityLink }) {
  const max = Math.max(...WORKBENCH_ROWS.map((row) => row.temperature));
  return (
    <Tile
      title="chart"
      tone={C.blue}
      right={<select aria-label="Chart document" value={document} onChange={(event) => setDocument(event.target.value)}>
        <option value="doc-a">Weather stations</option>
        <option value="doc-b">Pressure study</option>
      </select>}
    >
      <div className="p08-chart" role="img" aria-label="Temperature bars; press a bar to toggle the corresponding row selection">
        {WORKBENCH_ROWS.map((row) => {
          const selected = selection.rows.includes(row.id);
          return (
            <Presentation key={row.id} ptype="row" value={row} doc={`<row> ${row.id} · station ${row.station}`} onActivate={() => onToggle(row.id)}>
              <button type="button" className={`p08-bar-row ${selected ? "selected" : ""}`} onClick={(event) => {
                event.stopPropagation();
                onToggle(row.id);
              }}>
                <span className="p08-row-id">{row.id}</span>
                <span className="p08-bar" style={{ width: `${Math.round(row.temperature / max * 100)}%` }} />
                <b>{row.temperature.toFixed(1)}°</b>
              </button>
            </Presentation>
          );
        })}
      </div>
      <PortCard
        endpoint="chart.document"
        ptype="document-port"
        label="primary document"
        contract="document · read-write · identity candidate"
        tone={C.blue}
        linked={linked}
        value={document}
        onBeginLink={beginIdentityLink}
      />
      <PortCard
        endpoint="chart.selection"
        ptype="row-selection-port"
        label="brush selection"
        contract="row-selection · set-delta"
        tone={C.mustard}
        value={selection}
      />
    </Tile>
  );
}

function TableTile({ selection, onToggle, beginTransformedLink }) {
  return (
    <Tile title="table" tone={C.mustard} right={<Tag tone={C.mustard}>{selection.rows.length} selected</Tag>}>
      <table className="p08-table">
        <thead>
          <tr><th>row</th><th>station</th><th>temperature</th><th>pressure</th></tr>
        </thead>
        <tbody>
          {WORKBENCH_ROWS.map((row) => {
            const selected = selection.rows.includes(row.id);
            return (
              <tr key={row.id} className={selected ? "selected" : ""}>
                <td>
                  <Presentation ptype="row" value={row} doc={`<row> ${row.id}`} onActivate={() => onToggle(row.id)}>
                    <button type="button" className="p08-row-button" onClick={(event) => {
                      event.stopPropagation();
                      onToggle(row.id);
                    }}>{selected ? "☑" : "☐"} {row.id}</button>
                  </Presentation>
                </td>
                <td>{row.station}</td><td>{row.temperature}</td><td>{row.pressure}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <PortCard
        endpoint="table.selection"
        ptype="row-selection-port"
        label="row selection"
        contract="row-selection · set-delta"
        tone={C.mustard}
        value={selection}
        onBeginLink={beginTransformedLink}
      />
    </Tile>
  );
}

function PipelineTile({ filter, setPreset, document, setDocument, linked, transformedLinked, beginIdentityLink }) {
  return (
    <Tile
      title="pipeline"
      tone={C.sage}
      right={<select aria-label="Pipeline document" value={document} onChange={(event) => setDocument(event.target.value)}>
        <option value="doc-a">Weather stations</option>
        <option value="doc-b">Pressure study</option>
      </select>}
    >
      <div className="p08-row p08-wrap">
        <Button tone={C.paneAlt} onClick={() => setPreset("true")}>true</Button>
        <Button tone={C.paneAlt} onClick={() => setPreset("exact")}>exact rows</Button>
        <Button tone={C.paneAlt} onClick={() => setPreset("station")}>station A ∨ B</Button>
        <Button tone={C.paneAlt} onClick={() => setPreset("enriched")}>enriched filter</Button>
      </div>
      <FilterCode filter={filter} />
      <PortCard
        endpoint="pipeline.document"
        ptype="document-port"
        label="primary document"
        contract="document · read-write · identity candidate"
        tone={C.sage}
        linked={linked}
        value={document}
        onBeginLink={beginIdentityLink}
      />
      <PortCard
        endpoint="pipeline.filter"
        ptype="filter-port"
        label="filter expression"
        contract="filter-expression · read-write · replace"
        tone={C.rose}
        linked={transformedLinked}
        value={filter}
      />
    </Tile>
  );
}

function SourceBrowserTile() {
  const fields = [
    { name: "station", type: "string" },
    { name: "temperature", type: "number" },
    { name: "pressure", type: "number" },
    { name: "internal_id", type: "number", internal: true },
  ];
  return (
    <Tile title="source browser" tone={C.lavender} right={<Tag tone={C.lavender}>typed subjects</Tag>}>
      <div className="p08-doc-card">
        <b>Weather stations</b><span className="p08-micro">document doc-a</span>
      </div>
      {fields.map((field) => (
        <Presentation key={field.name} ptype="field" value={field} doc={`<field> doc-a/${field.name}`} block>
          <div className={`p08-field ${field.internal ? "internal" : ""}`}>
            <span>{field.name}</span><span className="p08-grow" /><Tag tone={field.type === "number" ? C.blue : C.lavender}>{field.type}</Tag>
            {field.internal && <Tag tone={C.red}>internal</Tag>}
          </div>
        </Presentation>
      ))}
      <div className="p08-callout">
        This tile retains the presentation-based shell idea: visible subjects and ports are typed interaction opportunities rather than anonymous callbacks.
      </div>
    </Tile>
  );
}

function PolicyLab({
  policyId,
  setPolicyId,
  conflictStrategy,
  setConflictStrategy,
  forward,
  backward,
  repair,
  onChoose,
  transformedLinked,
}) {
  const [tab, setTab] = useState("policy");
  const [laws, setLaws] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const policy = POLICY_OPTIONS.find((entry) => entry.id === policyId) ?? POLICY_OPTIONS[2];
  return (
    <aside className="p08-lab">
      <div className="p08-lab-head">
        <div><strong>P08 · consistency restoration</strong><div className="p08-micro">identity ≠ derivation ≠ lens ≠ replicated merge</div></div>
        <Tag tone={transformedLinked ? C.sage : C.line}>{transformedLinked ? "ports linked" : "not linked"}</Tag>
      </div>
      <div className="p08-tabs" role="tablist">
        {["policy", "repair", "laws", "feedback", "taxonomy"].map((name) => (
          <button key={name} type="button" role="tab" aria-selected={tab === name} onClick={() => setTab(name)}>{name}</button>
        ))}
      </div>
      <div className="p08-lab-body">
        {tab === "policy" && (
          <>
            <label className="p08-field-label">link policy
              <select value={policyId} onChange={(event) => setPolicyId(event.target.value)}>
                {POLICY_OPTIONS.map((entry) => <option key={entry.id} value={entry.id}>{entry.label}</option>)}
              </select>
            </label>
            <div className="p08-callout"><b>{policy?.policy.metadata.kind}</b><br />{policy?.policy.metadata.description}</div>
            <label className="p08-field-label">ambiguity policy
              <select value={conflictStrategy} onChange={(event) => setConflictStrategy(event.target.value)}>
                <option value="automatic">automatic if unique best</option>
                <option value="ranked">rank, do not commit</option>
                <option value="dialog">explicit dialog</option>
                <option value="refuse">refuse ambiguity</option>
              </select>
            </label>
            <div className="p08-row p08-wrap">
              <Button tone={C.mustard} onClick={forward}>selection → filter</Button>
              <Button tone={C.rose} onClick={backward}>selection ← filter</Button>
            </div>
            <div className="p08-section-label">declared laws</div>
            <ul>{policy?.policy.metadata.declaredLaws.map((law) => <li key={law}>{law}</li>)}</ul>
            <div className="p08-section-label">assumptions</div>
            <ul>{policy?.policy.metadata.assumptions.map((assumption) => <li key={assumption}>{assumption}</li>)}</ul>
          </>
        )}
        {tab === "repair" && <RepairPanel repair={repair} onChoose={onChoose} />}
        {tab === "laws" && (
          <>
            <Button tone={C.mint} onClick={() => setLaws(runLawHarness(20260808))}>run generated laws</Button>
            {laws && (
              <>
                <div className="p08-score-row">
                  <Tag tone={C.sage}>{laws.passed} passed</Tag><Tag tone={C.red}>{laws.failed} failed</Tag><Tag>{laws.unsupported} unsupported</Tag>
                </div>
                {laws.results.map((result) => (
                  <div key={`${result.policyId}:${result.lawId}`} className="p08-law-row">
                    <span>{result.lawId}</span><Tag tone={result.status === "passed" ? C.sage : C.red}>{result.status}</Tag>
                    {result.counterexample && <pre className="p08-code">{JSON.stringify(result.counterexample.minimizedInput, null, 2)}</pre>}
                  </div>
                ))}
              </>
            )}
          </>
        )}
        {tab === "feedback" && (
          <>
            {FEEDBACK_SCENARIOS.map((scenario) => (
              <Button key={scenario.id} tone={C.paneAlt} onClick={() => setFeedback(simulateFeedback(scenario, 24))}>{scenario.label}</Button>
            ))}
            {feedback && <pre className="p08-code">{JSON.stringify(feedback, null, 2)}</pre>}
          </>
        )}
        {tab === "taxonomy" && (
          <div>
            {LINK_TAXONOMY.map((entry) => (
              <div key={entry.id} className="p08-taxonomy-row">
                <div><b>{entry.id}</b> {entry.left} ↔ {entry.right}</div>
                <div className="p08-row"><Tag tone={entry.recommendedKind === "identity-reference" ? C.blue : entry.recommendedKind === "directed" ? C.sage : entry.recommendedKind === "replicated-merge" ? C.red : C.mustard}>{entry.recommendedKind}</Tag><Tag>{entry.confidence}</Tag></div>
                <div className="p08-micro">{entry.rationale}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}

export default function P08BidirectionalLinkLab() {
  const [selection, setSelection] = useState(DEFAULT_SELECTION);
  const [previousSelection, setPreviousSelection] = useState(DEFAULT_SELECTION);
  const [filter, setFilter] = useState({ op: "true" });
  const [policyId, setPolicyId] = useState(symmetricSelectionFilterPolicy.metadata.id);
  const [conflictStrategy, setConflictStrategy] = useState("dialog");
  const [repair, setRepair] = useState(null);
  const [transformedLinked, setTransformedLinked] = useState(false);
  const [accepting, setAccepting] = useState(null);
  const [mouseDoc, setMouseDoc] = useState(null);
  const [menu, setMenu] = useState(null);
  const [chartDoc, setChartDoc] = useState("doc-a");
  const [pipelineDoc, setPipelineDoc] = useState("doc-b");
  const [identityLinked, setIdentityLinked] = useState(false);
  const [, force] = useState(0);
  const identityRef = useRef(null);

  const policy = useMemo(() => POLICY_OPTIONS.find((entry) => entry.id === policyId)?.policy ?? symmetricSelectionFilterPolicy, [policyId]);
  const consistency = useMemo(() => selectionFilterConsistent(selection, filter), [selection, filter]);

  const runForward = useCallback((left = selection, target = filter) => {
    let result;
    if (policy.metadata.id === deltaSelectionFilterPolicy.metadata.id) {
      result = propagateForward(deltaSelectionFilterPolicy, {
        before: previousSelection,
        after: left,
        delta: diffSelection(previousSelection, left),
      }, target);
    } else {
      result = propagateForward(policy, left, target);
    }
    setRepair(result);
    if (result.kind === "updated" || result.kind === "unchanged") setFilter(result.value);
    setPreviousSelection(left);
    return result;
  }, [filter, policy, previousSelection, selection]);

  const runBackward = useCallback((target = filter, left = selection) => {
    if (policy.metadata.id === deltaSelectionFilterPolicy.metadata.id) {
      const result = propagateBackward(deltaSelectionFilterPolicy, {
        before: previousSelection,
        after: left,
        delta: diffSelection(previousSelection, left),
      }, target, { requireExplicitAmbiguity: true, conflictStrategy });
      setRepair(result);
      if (result.kind === "updated" || result.kind === "unchanged") {
        setPreviousSelection(result.value.before);
        setSelection(result.value.after);
      }
      return result;
    }
    const result = propagateBackward(policy, left, target, {
      requireExplicitAmbiguity: true,
      conflictStrategy,
    });
    setRepair(result);
    if (result.kind === "updated" || result.kind === "unchanged") setSelection(result.value);
    else if (result.kind === "conflict" && conflictStrategy === "automatic") {
      const resolution = resolveConflict(result, "automatic");
      if (resolution.outcome.kind === "chosen") setSelection(resolution.outcome.choice.value);
    }
    return result;
  }, [conflictStrategy, filter, policy, previousSelection, selection]);

  const toggleRow = (rowId) => {
    const next = selection.rows.includes(rowId)
      ? { rows: selection.rows.filter((row) => row !== rowId) }
      : { rows: [...selection.rows, rowId] };
    setSelection(next);
    if (transformedLinked) runForward(next, filter);
    else setPreviousSelection(selection);
  };

  const setFilterPreset = (preset) => {
    const next = preset === "exact"
      ? selectionToExactFilter(selection)
      : preset === "station"
        ? { op: "stationIn", stations: ["A", "B"] }
        : preset === "enriched"
          ? { op: "and", args: [{ op: "opaque", id: "owner", label: "owner=analyst" }, selectionToExactFilter(selection)] }
          : { op: "true" };
    setFilter(next);
    if (transformedLinked) runBackward(next, selection);
  };

  const beginTransformedLink = () => {
    setAccepting({
      types: ["filter-port"],
      prompt: "LINK MODE — choose a filter port for the table row-selection port",
      resolve: ({ value }) => {
        if (value.endpoint === "pipeline.filter") {
          setTransformedLinked(true);
          runForward(selection, filter);
        }
      },
    });
  };

  const beginIdentityLink = (sourceEndpoint) => {
    setAccepting({
      types: ["document-port"],
      exclude: [sourceEndpoint],
      prompt: `LINK MODE — choose another primary-document port for ${sourceEndpoint}`,
      resolve: ({ value }) => {
        const initial = sourceEndpoint.startsWith("chart") ? chartDoc : pipelineDoc;
        identityRef.current = createIdentitySession("document-binding-1", [sourceEndpoint, value.endpoint], { sort: "document", key: initial });
        setIdentityLinked(true);
        setChartDoc(initial);
        setPipelineDoc(initial);
        force((revision) => revision + 1);
      },
    });
  };

  const setLinkedDocument = (endpoint, key) => {
    if (!identityLinked || !identityRef.current) {
      if (endpoint.startsWith("chart")) setChartDoc(key);
      else setPipelineDoc(key);
      return;
    }
    identityRef.current.projections[endpoint]?.set({ sort: "document", key });
    const chart = identityRef.current.projections["chart.document"]?.get()?.key ?? key;
    const pipeline = identityRef.current.projections["pipeline.document"]?.get()?.key ?? key;
    setChartDoc(chart);
    setPipelineDoc(pipeline);
    force((revision) => revision + 1);
  };

  const chooseRepair = (choice) => {
    setSelection(choice.value.after ?? choice.value);
    setRepair(null);
  };

  const ui = { accepting, setAccepting, mouseDoc, setMouseDoc, menu, setMenu };
  return (
    <UiContext.Provider value={ui}>
      <div className="p08-root" onClick={() => setMenu(null)}>
        <style>{STYLES}</style>
        <header className="p08-shell-head">
          <div><strong>PBUI · P08 BIDIRECTIONAL LINK LAB</strong><span className="p08-subtitle">consistency relations · partial repair · deltas · feedback</span></div>
          <div className="p08-row">
            <Tag tone={consistency.consistent ? C.sage : C.red}>{consistency.consistent ? "consistent" : "inconsistent"}</Tag>
            <Tag tone={identityLinked ? C.blue : C.line}>{identityLinked ? "document identity active" : "documents independent"}</Tag>
            <Tag tone={transformedLinked ? C.mustard : C.line}>{transformedLinked ? "selection/filter linked" : "selection/filter independent"}</Tag>
          </div>
        </header>
        {accepting && (
          <div className="p08-accept-bar">
            <b>{accepting.prompt}</b><span className="p08-grow" /><Button tone={C.paper} onClick={() => setAccepting(null)}>Esc · cancel</Button>
          </div>
        )}
        <main className="p08-main">
          <div className="p08-workspace">
            <SourceBrowserTile />
            <ChartTile
              selection={selection}
              onToggle={toggleRow}
              document={chartDoc}
              setDocument={(key) => setLinkedDocument("chart.document", key)}
              linked={identityLinked}
              beginIdentityLink={() => beginIdentityLink("chart.document")}
            />
            <TableTile selection={selection} onToggle={toggleRow} beginTransformedLink={beginTransformedLink} />
            <PipelineTile
              filter={filter}
              setPreset={setFilterPreset}
              document={pipelineDoc}
              setDocument={(key) => setLinkedDocument("pipeline.document", key)}
              linked={identityLinked}
              transformedLinked={transformedLinked}
              beginIdentityLink={() => beginIdentityLink("pipeline.document")}
            />
          </div>
          <PolicyLab
            policyId={policyId}
            setPolicyId={setPolicyId}
            conflictStrategy={conflictStrategy}
            setConflictStrategy={setConflictStrategy}
            forward={() => runForward()}
            backward={() => runBackward()}
            repair={repair}
            onChoose={chooseRepair}
            transformedLinked={transformedLinked}
          />
        </main>
        <footer className="p08-status">
          <span>{accepting ? accepting.prompt : mouseDoc ?? `relation: ${consistency.relation} · ${consistency.summary}`}</span>
          <span className="p08-grow" />
          <span>right-click any presentation to inspect · keyboard: Tab, Enter, Space</span>
        </footer>
        {menu && (
          <div className="p08-menu" style={{ left: menu.x, top: menu.y }} role="menu">
            <div className="p08-menu-title">&lt;{menu.ptype}&gt;</div>
            <button type="button" onClick={() => {
              setRepair({
                kind: "unchanged",
                value: menu.value,
                evidence: {
                  evidenceId: "ui-inspection",
                  policyId: "ui",
                  policyKind: "directed",
                  direction: "forward",
                  summary: menu.doc ?? "Presentation inspection",
                  consistencyBefore: { consistent: true, relation: "inspection", summary: "n/a", facts: [], informationLoss: [] },
                  consistencyAfter: { consistent: true, relation: "inspection", summary: "n/a", facts: [], informationLoss: [] },
                  informationLoss: [], preservedIntent: [], discardedIntent: [], provenance: ["React presentation adapter"], assumptions: [],
                },
              });
              setMenu(null);
            }}>Inspect in repair panel</button>
          </div>
        )}
      </div>
    </UiContext.Provider>
  );
}

const STYLES = `
  .p08-root{height:100vh;min-height:720px;display:flex;flex-direction:column;background:${C.paper};color:${C.ink};font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;overflow:hidden}
  .p08-shell-head{display:flex;align-items:center;gap:12px;padding:7px 10px;border-bottom:3px solid ${C.ink};background:${C.warm};letter-spacing:.04em}.p08-shell-head>div:first-child{display:flex;align-items:baseline;gap:12px}.p08-subtitle{font-size:10px;color:${C.faint}}
  .p08-main{display:grid;grid-template-columns:minmax(700px,1fr) 390px;gap:5px;flex:1;min-height:0;padding:5px;background:${C.ink}}
  .p08-workspace{display:grid;grid-template-columns:1fr 1.15fr;grid-template-rows:1fr 1.15fr;gap:5px;min-width:0;min-height:0}
  .p08-tile{display:flex;flex-direction:column;min-width:0;min-height:0;background:${C.pane};border:2px solid ${C.ink};overflow:hidden}.p08-tile-head{display:flex;align-items:center;gap:6px;padding:3px 6px;border-bottom:2px solid ${C.ink};text-transform:uppercase;letter-spacing:.08em;font-size:11px}.p08-tile-head select{max-width:150px}.p08-tile-body{padding:7px;overflow:auto;min-height:0;flex:1}
  .p08-grow{flex:1}.p08-row{display:flex;align-items:center;gap:5px}.p08-wrap{flex-wrap:wrap}.p08-micro{font-size:9.5px;color:${C.faint};line-height:1.35}.p08-section-label{margin:10px 0 4px;font-size:9px;color:${C.faint};letter-spacing:.1em;text-transform:uppercase}
  .p08-btn{font:inherit;font-size:10px;font-weight:700;border:2px solid ${C.ink};box-shadow:2px 2px 0 ${C.ink};padding:2px 7px;cursor:pointer;color:${C.ink}}.p08-btn:disabled{opacity:.45;cursor:default}.p08-btn:focus-visible,.p08-pres:focus-visible,.p08-choice:focus-visible,.p08-tabs button:focus-visible{outline:3px solid ${C.red};outline-offset:2px}
  .p08-tag{display:inline-block;border:1px solid ${C.ink};border-left:5px solid ${C.paneAlt};background:${C.pane};padding:1px 5px;font-size:9.5px;white-space:nowrap}
  .p08-port{display:flex;align-items:center;gap:5px;border:1px solid ${C.ink};border-left:6px solid ${C.line};padding:4px 5px;margin-top:6px;background:${C.paneAlt}}.p08-port-linked{box-shadow:inset 0 0 0 2px ${C.sage}}
  .p08-pres{position:relative}.p08-pres[role=button]{cursor:pointer}.p08-disabled{opacity:.45}.p08-acceptable{animation:p08pulse .9s infinite alternate;outline:3px solid ${C.red};outline-offset:2px}@keyframes p08pulse{from{filter:none}to{filter:brightness(1.12);background:${C.sel}}}
  .p08-accept-bar{display:flex;align-items:center;gap:8px;background:${C.red};color:white;padding:4px 9px;border-bottom:3px solid ${C.ink};font-size:11px;letter-spacing:.04em}
  .p08-chart{display:grid;gap:4px}.p08-bar-row{display:grid;grid-template-columns:52px 1fr 46px;align-items:center;gap:5px;width:100%;border:1px solid ${C.line};background:${C.pane};padding:2px 4px;text-align:left;font:inherit;cursor:pointer}.p08-bar-row.selected{background:${C.sel};border-color:${C.ink}}.p08-bar{height:12px;background:${C.blue};border:1px solid ${C.ink};min-width:2px}.p08-row-id{font-size:9.5px;color:${C.faint}}
  .p08-table{border-collapse:collapse;width:100%;font-size:10px}.p08-table th,.p08-table td{border-bottom:1px dotted ${C.line};padding:3px 4px;text-align:left}.p08-table tr.selected{background:${C.sel}}.p08-row-button{font:inherit;border:0;background:transparent;cursor:pointer;padding:0}
  .p08-code{background:${C.paneAlt};border:1px solid ${C.line};padding:6px;max-height:240px;overflow:auto;white-space:pre-wrap;word-break:break-word;font-size:9.5px;line-height:1.35}
  .p08-field{display:flex;align-items:center;gap:5px;padding:4px;border-bottom:1px dotted ${C.line}}.p08-field.internal{opacity:.6}.p08-doc-card{display:flex;justify-content:space-between;border:2px solid ${C.ink};border-left:6px solid ${C.lavender};padding:5px;margin-bottom:5px}
  .p08-lab{display:flex;flex-direction:column;min-width:0;min-height:0;background:${C.pane};border:2px solid ${C.ink}}.p08-lab-head{display:flex;align-items:center;gap:8px;padding:6px;border-bottom:2px solid ${C.ink};background:${C.rose}}.p08-tabs{display:grid;grid-template-columns:repeat(5,1fr);border-bottom:2px solid ${C.ink}}.p08-tabs button{font:inherit;font-size:9px;border:0;border-right:1px solid ${C.ink};padding:5px;background:${C.paneAlt};cursor:pointer;text-transform:uppercase}.p08-tabs button[aria-selected=true]{background:${C.sel};font-weight:700}.p08-lab-body{padding:7px;overflow:auto;min-height:0;flex:1}.p08-field-label{display:grid;gap:3px;margin-bottom:8px;font-size:9px;text-transform:uppercase;letter-spacing:.08em}.p08-field-label select{font:inherit;font-size:10px;padding:3px}
  .p08-callout{border:1px solid ${C.ink};border-left:5px solid ${C.sage};background:${C.warm};padding:5px;margin:6px 0;line-height:1.4}.p08-callout-warn{border-left-color:${C.red}}.p08-callout ul,.p08-repair ul{margin:4px 0 0;padding-left:18px}
  .p08-choice{display:flex;align-items:center;gap:6px;width:100%;text-align:left;font:inherit;border:1px solid ${C.ink};background:${C.pane};padding:5px;margin-bottom:4px;cursor:pointer}.p08-choice>span:first-child{flex:1}.p08-empty{color:${C.faint};padding:10px;text-align:center}.p08-score-row{display:flex;gap:4px;margin:8px 0}.p08-law-row,.p08-taxonomy-row{border-bottom:1px dotted ${C.line};padding:4px 0}.p08-law-row>.p08-tag{float:right}
  .p08-status{display:flex;gap:8px;align-items:center;padding:3px 8px;border-top:3px solid ${C.ink};background:${C.paneAlt};font-size:9.5px;min-height:18px}.p08-menu{position:fixed;z-index:100;background:${C.pane};border:2px solid ${C.ink};box-shadow:3px 3px 0 ${C.ink};padding:4px;max-width:260px}.p08-menu-title{font-size:9px;color:${C.faint};padding:2px}.p08-menu button{display:block;width:100%;text-align:left;font:inherit;border:0;background:${C.pane};padding:4px;cursor:pointer}.p08-menu button:hover{background:${C.sel}}
  select{font-family:inherit;font-size:10px;border:1px solid ${C.ink};background:${C.pane};color:${C.ink}}
  @media(max-width:1050px){.p08-main{grid-template-columns:1fr}.p08-lab{min-height:420px}.p08-root{height:auto;overflow:auto}.p08-main{min-height:1300px}.p08-workspace{min-height:850px}}
`;
