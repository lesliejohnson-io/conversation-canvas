export type Quadrant =
  | "past-strengths"
  | "preferred-future"
  | "past-struggles"
  | "feared-future";

export type Phrase = {
  id: number;
  text: string; // Full thought
  label: string; // Short label for map
  quadrant: Quadrant;
  x: number;
  y: number;
  recency: number;
  importance: number;
  sentenceNumber: number;
  isRepeated?: boolean;
  displayNumber?: number;
  extractScore?: number;
  confidence?: number;
};

export const QUADRANT_LABELS: Record<Quadrant, string> = {
  'past-strengths': 'Past Strengths',
  'preferred-future': 'Preferred Future',
  'past-struggles': 'Past Struggles',
  'feared-future': 'Feared Future',
};

export const QUADRANT_COLORS: Record<Quadrant, string> = {
  'past-strengths': 'bg-blue-50',
  'preferred-future': 'bg-green-50',
  'past-struggles': 'bg-amber-50',
  'feared-future': 'bg-rose-50',
};