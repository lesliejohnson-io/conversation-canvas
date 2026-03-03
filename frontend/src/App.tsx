import { useEffect, useMemo, useState } from "react";
import { getPhrases, getQuadrantMap, patchPhraseQuadrant } from "./api";
import type { Phrase, QuadrantNode } from "./api";

const QUADRANTS = [
  { key: "resourceful_past", label: "Resourceful Past" },
  { key: "preferred_future", label: "Preferred Future" },
  { key: "troubled_past", label: "Troubled Past" },
  { key: "dreaded_future", label: "Dreaded Future" },
] as const;

function Chip({
  label,
  selected,
  onClick,
}: {
  label: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        border: "1px solid #ccc",
        borderRadius: 999,
        padding: "4px 10px",
        fontSize: 12,
        cursor: "pointer",
        background: selected ? "#111" : "transparent",
        color: selected ? "#fff" : "#111",
      }}
    >
      {label}
    </button>
  );
}

function Badge({ n }: { n: number }) {
  if (n <= 1) return null;
  return (
    <span
      style={{
        marginLeft: 8,
        fontSize: 12,
        padding: "2px 8px",
        borderRadius: 999,
        border: "1px solid #ddd",
      }}
    >
      ×{n}
    </span>
  );
}

function QuadrantMap({ nodes }: { nodes: QuadrantNode[] }) {
  const size = 560;
  const half = size / 2;

  // Map quadrant -> sign multipliers for x/y
  // Backend coords are ring-based x/y around origin.
  // We remap based on quadrant meaning:
  // - past = left, future = right
  // - resourceful = up, troubled = down
  const quadrantToSigns: Record<string, { sx: number; sy: number }> = {
    resourceful_past: { sx: -1, sy: +1 },
    preferred_future: { sx: +1, sy: +1 },
    troubled_past: { sx: -1, sy: -1 },
    dreaded_future: { sx: +1, sy: -1 },
  };

  const scale = half - 34; // inner padding

  const axisColor = "#111";
  const axisOpacity = 0.55;

  return (
    <div style={{ width: size, height: size, position: "relative" }}>
      <div style={{ fontWeight: 800, marginBottom: 10 }}>Conversation Map</div>

      <svg width={size} height={size} style={{ display: "block" }}>
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="8"
            markerHeight="8"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill={axisColor} opacity={axisOpacity} />
          </marker>
        </defs>

        {/* Axes */}
        <line
          x1={half}
          y1={18}
          x2={half}
          y2={size - 18}
          stroke={axisColor}
          strokeOpacity={axisOpacity}
          strokeWidth={2}
          markerStart="url(#arrow)"
          markerEnd="url(#arrow)"
        />
        <line
          x1={18}
          y1={half}
          x2={size - 18}
          y2={half}
          stroke={axisColor}
          strokeOpacity={axisOpacity}
          strokeWidth={2}
          markerStart="url(#arrow)"
          markerEnd="url(#arrow)"
        />

        {/* Center dot */}
        <circle cx={half} cy={half} r={4} fill={axisColor} opacity={0.22} />

        {/* Labels */}
        <text x={28} y={half - 10} fontSize="12" fill={axisColor} opacity={0.7}>
          Past
        </text>
        <text x={size - 60} y={half - 10} fontSize="12" fill={axisColor} opacity={0.7}>
          Future
        </text>
        <text x={half + 10} y={28} fontSize="12" fill={axisColor} opacity={0.7}>
          Resourceful
        </text>
        <text x={half + 10} y={size - 22} fontSize="12" fill={axisColor} opacity={0.7}>
          Troubled
        </text>

        {/* Nodes */}
        {nodes.map((n) => {
          const signs = quadrantToSigns[n.quadrant] ?? { sx: 1, sy: 1 };

          // convert normalized [-1..1-ish] ring coords into quadrant-mapped screen coords
          let nx = Math.abs(n.x);
          let ny = Math.abs(n.y);

          // Axis nudge: keep nodes off the divider lines so they don’t sit on the axes
          const EPS = 0.06; // tweak 0.04–0.08 based on taste
          if (nx < 0.0001) nx = EPS;
          if (ny < 0.0001) ny = EPS;

          const px = half + signs.sx * nx * scale;
          const py = half - signs.sy * ny * scale;

          const r = Math.max(3, Math.min(10, n.dot_radius ?? 6));
          const opacity = n.opacity ?? 0.85;

          // label positioning
          const labelOffsetX = 10;
          const labelOffsetY = 4;

          return (
            <g key={n.phrase_id} opacity={opacity}>
              {/* dot */}
              <circle cx={px} cy={py} r={r} fill={axisColor} />

              {/* number (centered) */}
              <text
                x={px}
                y={py + 3}
                textAnchor="middle"
                fontSize={Math.max(9, Math.min(12, r + 3))}
                fill="#fff"
                style={{ fontWeight: 700 }}
              >
                {n.number ?? ""}
              </text>

              {/* short label */}
              <text
                x={px + labelOffsetX + r}
                y={py + labelOffsetY}
                fontSize="12"
                fill={axisColor}
                opacity={1}
              >
                {n.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

export default function App() {
  const [sessionId, setSessionId] = useState("sess_626429e7c3a3");
  const [phrases, setPhrases] = useState<Phrase[]>([]);
  const [nodes, setNodes] = useState<QuadrantNode[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const [p, n] = await Promise.all([getPhrases(sessionId), getQuadrantMap(sessionId)]);
      setPhrases(p);
      setNodes(n);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function onSelectQuadrant(phraseId: number, quadrant: string) {
    const current = phrases.find((p) => p.id === phraseId)?.quadrant_final ?? null;
    const next = current === quadrant ? null : quadrant;
    await patchPhraseQuadrant(phraseId, next);
    await refresh();
  }

  return (
    <div style={{ padding: 18, fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Arial" }}>
      <h2 style={{ margin: 0 }}>Paloma Session Canvas (MVP)</h2>

      <div style={{ marginTop: 8, display: "flex", gap: 10, alignItems: "center", color: "#555" }}>
        <div>Session ID:</div>
        <input
          value={sessionId}
          onChange={(e) => setSessionId(e.target.value)}
          style={{ padding: "6px 8px", borderRadius: 8, border: "1px solid #ddd", width: 240 }}
        />
        <button
          onClick={refresh}
          style={{ padding: "6px 10px", borderRadius: 8, border: "1px solid #ddd", cursor: "pointer" }}
        >
          Refresh
        </button>
        {loading && <div style={{ fontSize: 12 }}>Loading…</div>}
      </div>

      {error && (
        <div style={{ marginTop: 12, padding: 10, border: "1px solid #f66", borderRadius: 10 }}>
          <b>Error:</b> {error}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: 18, marginTop: 16 }}>
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
          <div style={{ fontWeight: 700, marginBottom: 10 }}>Ranked phrases</div>

          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {phrases.map((p) => (
              <div key={p.id} style={{ borderBottom: "1px solid #f5f5f5", paddingBottom: 10 }}>
                <div style={{ fontSize: 14, lineHeight: 1.35 }}>
                  {p.phrase_text}
                  <Badge n={p.recurrence_count} />
                </div>

                <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {QUADRANTS.map((q) => (
                    <Chip
                      key={q.key}
                      label={q.label}
                      selected={p.quadrant_final === q.key}
                      onClick={() => onSelectQuadrant(p.id, q.key)}
                    />
                  ))}
                </div>

                <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
                  sentence #{p.source_sentence_index} • extract {p.extraction_confidence.toFixed(2)} • classify{" "}
                  {p.classification_confidence.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
          <div style={{ fontWeight: 700, marginBottom: 10 }}>DOQ Quadrant Map</div>
          <QuadrantMap nodes={nodes} />
        </div>
      </div>
    </div>
  );
}