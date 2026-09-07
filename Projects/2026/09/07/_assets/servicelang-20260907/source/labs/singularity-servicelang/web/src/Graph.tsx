import type { FunctionView } from "./types";
export function Graph({
  fn,
  selected,
  onSelect,
}: {
  fn: FunctionView;
  selected: number;
  onSelect: (id: number) => void;
}) {
  const depth = new Map<number, number>([[0, 0]]),
    rows = new Map<number, number>(),
    positions = new Map<number, { x: number; y: number }>();
  for (const b of fn.Blocks)
    for (const e of b.End.Edges ?? [])
      depth.set(
        e.Target,
        Math.max(depth.get(e.Target) ?? 0, (depth.get(b.ID) ?? 0) + 1),
      );
  for (const b of fn.Blocks) {
    const d = depth.get(b.ID) ?? 0,
      r = rows.get(d) ?? 0;
    rows.set(d, r + 1);
    positions.set(b.ID, { x: 20 + d * 300, y: 32 + r * 138 });
  }
  const width = Math.max(450, ...[...positions.values()].map((p) => p.x + 220)),
    height = Math.max(180, ...[...positions.values()].map((p) => p.y + 126));
  return (
    <div className="graph-scroll">
      <svg
        width={width}
        height={height}
        aria-label="Actual compiler control-flow graph"
      >
        <defs>
          <marker
            id="arrow"
            markerWidth="8"
            markerHeight="8"
            refX="7"
            refY="3"
            orient="auto"
          >
            <path d="M0,0 L0,6 L7,3 z" fill="#647b90" />
          </marker>
        </defs>
        {fn.Blocks.flatMap((b) =>
          (b.End.Edges ?? []).map((e, i) => {
            const a = positions.get(b.ID)!,
              z = positions.get(e.Target)!;
            return (
              <g key={`${b.ID}-${i}`}>
                <path
                  d={`M${a.x + 194},${a.y + 45} C${a.x + 220},${a.y + 45} ${z.x - 25},${z.y + 45} ${z.x},${z.y + 45}`}
                  stroke="#647b90"
                  fill="none"
                  markerEnd="url(#arrow)"
                />
                <text
                  x={a.x + 197}
                  y={a.y + 31 + i * 14}
                  className="edge-label"
                >
                  {e.Variant ||
                    (b.End.Kind === "branch"
                      ? i === 0
                        ? "true"
                        : "false"
                      : "")}
                </text>
              </g>
            );
          }),
        )}
        {fn.Blocks.map((b) => {
          const p = positions.get(b.ID)!;
          return (
            <g
              key={b.ID}
              role="button"
              tabIndex={0}
              aria-label={`Block ${b.ID}`}
              onClick={() => onSelect(b.ID)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelect(b.ID);
                }
              }}
              className={`graph-node ${selected === b.ID ? "selected" : ""}`}
              transform={`translate(${p.x},${p.y})`}
            >
              <rect width="194" height="90" rx="9" />
              <text x="14" y="24">
                b{b.ID} · {b.End.Kind}
              </text>
              <text x="14" y="46" className="node-detail">
                {(b.Ops ?? []).length} ordered operations
              </text>
              <text x="14" y="69" className="node-detail">
                {b.In ? "facts available" : "no facts recorded"}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
