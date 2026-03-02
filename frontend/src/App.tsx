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
  const size = 320;
  const half = size / 2;

  const byQuadrant = useMemo(() => {
    const m = new Map<string, QuadrantNode[]>();
    for (const q of QUADRANTS) m.set(q.key, []);
    for (const n of nodes) m.get(n.quadrant_final)?.push(n);
    return m;
  }, [nodes]);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
      {QUADRANTS.map((q) => {
        const items = byQuadrant.get(q.key) ?? [];
        return (
          <div key={q.key} style={{ border: "1px solid #eee", borderRadius: 12, padding: 10 }}>
            <div style={{ fontWeight: 600, marginBottom: 8 }}>{q.label}</div>

            <div
              style={{
                width: size,
                height: size,
                border: "1px solid #f0f0f0",
                borderRadius: 12,
                position: "relative",
                overflow: "hidden",
                background: "#fff",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  left: half - 3,
                  top: half - 3,
                  width: 6,
                  height: 6,
                  borderRadius: 999,
                  background: "#111",
                  opacity: 0.25,
                }}
              />

              {items.map((n) => {
                const px = half + n.x * (half - 20);
                const py = half - n.y * (half - 20);

                return (
                  <div
                    key={n.phrase_id}
                    title={`${n.phrase_text} (×${n.recurrence_count})`}
                    style={{
                      position: "absolute",
                      left: px,
                      top: py,
                      transform: "translate(-50%, -50%)",
                      padding: "4px 8px",
                      borderRadius: 999,
                      border: "1px solid #ddd",
                      fontSize: 12,
                      background: "#fff",
                      whiteSpace: "nowrap",
                      maxWidth: 190,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {n.phrase_text}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
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