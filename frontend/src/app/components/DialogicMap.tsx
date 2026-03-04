// src/app/components/DialogicMap.tsx
import type { Phrase, Quadrant } from "../types";
import { PhraseNode } from "./PhraseNode";
import { QuadrantOverrideMenu } from "./QuadrantOverrideMenu";

interface DialogicMapProps {
  phrases: Phrase[];
  hoveredPhraseId: number | null;
  selectedPhraseId: number | null;
  onHoverPhrase: (id: number | null) => void;

  // allow passing click position so the override menu can appear near the node
  onSelectPhrase: (id: number | null, menuPos?: { x: number; y: number }) => void;

  overrideMenuPosition: { x: number; y: number } | null;
  onQuadrantOverride: (phraseId: number, quadrant: Quadrant) => void;
}

export function DialogicMap({
  phrases,
  hoveredPhraseId,
  selectedPhraseId,
  onHoverPhrase,
  onSelectPhrase,
  overrideMenuPosition,
  onQuadrantOverride,
}: DialogicMapProps) {
  const handleBackgroundClick = () => {
    onSelectPhrase(null);
  };

  const handleNodeClick = (id: number, event: React.MouseEvent) => {
    event.stopPropagation();

    // event.currentTarget is the node element; we want the outer map container for relative coords
    const container = (event.currentTarget as HTMLElement).closest(".dialogic-map-container");
    const rect = container?.getBoundingClientRect();

    // Fallback: select without positioning
    if (!rect) {
      onSelectPhrase(id);
      return;
    }

    // Convert viewport coords -> container-relative coords
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Nudge so the menu doesn't sit directly under the cursor
    onSelectPhrase(id, { x: x + 8, y: y + 8 });
  };

  return (
    <div className="dialogic-map-container relative w-full h-full bg-white" onClick={handleBackgroundClick}>
      <svg viewBox="0 0 800 800" className="w-full h-full" style={{ maxWidth: "100%", maxHeight: "100%" }}>
        {/* Quadrant backgrounds (subtle) */}
        <g className="quadrant-backgrounds">
          {/* Preferred Future - top right */}
          <rect x="400" y="50" width="350" height="350" className="fill-green-50" opacity="0.22" />
          {/* Past Strengths - top left */}
          <rect x="50" y="50" width="350" height="350" className="fill-blue-50" opacity="0.22" />
          {/* Past Struggles - bottom left */}
          <rect x="50" y="400" width="350" height="350" className="fill-amber-50" opacity="0.22" />
          {/* Feared Future - bottom right */}
          <rect x="400" y="400" width="350" height="350" className="fill-rose-50" opacity="0.22" />
        </g>

        {/* Concentric rings for recency */}
        <g className="recency-rings">
          {[1, 2, 3, 4, 5].map((ring) => (
            <circle
              key={ring}
              cx="400"
              cy="400"
              r={ring * 60}
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="1"
              opacity="0.28"
            />
          ))}
        </g>

        {/* Axes */}
        <g className="axes">
          {/* Horizontal axis (Past ↔ Future) */}
          <line x1="50" y1="400" x2="750" y2="400" stroke="#9ca3af" strokeWidth="2" />
          {/* Arrow right */}
          <polygon points="750,400 740,395 740,405" fill="#9ca3af" />
          {/* Arrow left */}
          <polygon points="50,400 60,395 60,405" fill="#9ca3af" />

          {/* Vertical axis (Struggles ↔ Strengths) */}
          <line x1="400" y1="50" x2="400" y2="750" stroke="#9ca3af" strokeWidth="2" />
          {/* Arrow up */}
          <polygon points="400,50 395,60 405,60" fill="#9ca3af" />
          {/* Arrow down */}
          <polygon points="400,750 395,740 405,740" fill="#9ca3af" />
        </g>

        {/* Axis labels */}
        <g className="axis-labels">
          <text x="30" y="390" className="text-sm fill-gray-500 select-none" style={{ fontSize: "14px" }}>
            Past
          </text>
          <text x="745" y="390" className="text-sm fill-gray-500 select-none" style={{ fontSize: "14px" }}>
            Future
          </text>
          <text
            x="400"
            y="40"
            textAnchor="middle"
            className="text-sm fill-gray-500 select-none"
            style={{ fontSize: "14px" }}
          >
            Strengths
          </text>
          <text
            x="400"
            y="770"
            textAnchor="middle"
            className="text-sm fill-gray-500 select-none"
            style={{ fontSize: "14px" }}
          >
            Struggles
          </text>
        </g>

        {/* Phrase nodes */}
        <g className="phrase-nodes">
          {phrases.map((phrase) => (
            <PhraseNode
              key={phrase.id}
              phrase={phrase}
              isHovered={hoveredPhraseId === phrase.id}
              isSelected={selectedPhraseId === phrase.id}
              onHover={onHoverPhrase}
              onClick={handleNodeClick}
            />
          ))}
        </g>
      </svg>

      {/* Quadrant override menu */}
      {overrideMenuPosition && selectedPhraseId && (
        <QuadrantOverrideMenu
          position={overrideMenuPosition}
          onSelect={(quadrant) => onQuadrantOverride(selectedPhraseId, quadrant)}
        />
      )}
    </div>
  );
}