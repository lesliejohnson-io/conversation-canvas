export type Phrase = {
    id: number;
    phrase_text: string;
    phrase_norm: string;
    source_sentence_index: number;
    extraction_confidence: number;
    classification_confidence: number;
    quadrant_model: string | null;
    quadrant_final: string | null;
    recurrence_count: number;
  };
  
  export type QuadrantNode = {
    phrase_id: number;
    phrase_text: string;
    quadrant_final: string;
    recurrence_count: number;
    ring_index: number;
    x: number;
    y: number;
  };
  
  const API_BASE = "http://127.0.0.1:8000";
  
  export async function getPhrases(sessionId: string): Promise<Phrase[]> {
    const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/phrases`);
    if (!res.ok) throw new Error(`getPhrases failed: ${res.status}`);
    const data = await res.json();
    return data.phrases as Phrase[];
  }
  
  export async function getQuadrantMap(sessionId: string): Promise<QuadrantNode[]> {
    const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/quadrant_map`);
    if (!res.ok) throw new Error(`getQuadrantMap failed: ${res.status}`);
    const data = await res.json();
    return data.nodes as QuadrantNode[];
  }
  
  export async function patchPhraseQuadrant(phraseId: number, quadrantFinal: string | null): Promise<void> {
    const res = await fetch(`${API_BASE}/api/phrases/${phraseId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quadrant_final: quadrantFinal }),
    });
    if (!res.ok) {
      const txt = await res.text();
      throw new Error(`patchPhraseQuadrant failed: ${res.status} ${txt}`);
    }
  }