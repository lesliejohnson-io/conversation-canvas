import { QUADRANT_LABELS, QUADRANT_COLORS } from "../types";
import type { Quadrant } from "../types";

interface QuadrantChipProps {
  quadrant: Quadrant;
  size?: 'sm' | 'md';
}

const chipColors: Record<Quadrant, string> = {
  'past-strengths': 'bg-blue-100 text-blue-700',
  'preferred-future': 'bg-green-100 text-green-700',
  'past-struggles': 'bg-amber-100 text-amber-700',
  'feared-future': 'bg-rose-100 text-rose-700',
};

export function QuadrantChip({ quadrant, size = 'sm' }: QuadrantChipProps) {
  const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1';
  
  return (
    <span className={`inline-flex items-center rounded-full ${chipColors[quadrant]} ${sizeClasses}`}>
      {QUADRANT_LABELS[quadrant]}
    </span>
  );
}