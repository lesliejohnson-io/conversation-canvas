import { QUADRANT_LABELS } from "../types";
import type { Quadrant } from "../types";

interface QuadrantOverrideMenuProps {
  onSelect: (quadrant: Quadrant) => void;
  position: { x: number; y: number };
}

const quadrants: Quadrant[] = [
  "past-strengths",
  "preferred-future",
  "past-struggles",
  "feared-future",
];

export function QuadrantOverrideMenu({ onSelect, position }: QuadrantOverrideMenuProps) {
  return (
    <div
      className="absolute z-50 bg-white rounded-lg shadow-lg border border-gray-200 py-1.5 px-1.5 min-w-[180px]"
      style={{
        left: position.x,
        top: position.y,
        transform: "translate(8px, 8px)", // slight offset so it appears beside the click
      }}
      onClick={(e) => e.stopPropagation()}
    >
      <div className="text-xs text-gray-500 px-2 py-1.5 mb-1">
        Move to quadrant
      </div>

      <div className="space-y-1">
        {quadrants.map((quadrant) => (
          <button
            key={quadrant}
            onClick={() => onSelect(quadrant)}
            className="w-full text-left px-2 py-1.5 text-sm rounded hover:bg-gray-50 transition-colors"
          >
            {QUADRANT_LABELS[quadrant]}
          </button>
        ))}
      </div>
    </div>
  );
}