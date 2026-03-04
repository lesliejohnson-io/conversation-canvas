// frontend/src/App.tsx
import { useMemo, useState } from "react";

// IMPORTANT: these are almost certainly default exports in the Figma code.
// If your component files use `export function Header()` etc, switch back to { Header } form.
import { Header } from "./app/components/Header";
import { DialogicMap } from "./app/components/DialogicMap";
import { SidePanel } from "./app/components/SidePanel";

import type { Phrase, Quadrant } from "./app/types";
import { examplePhrases } from "./app/data";

type Point = { x: number; y: number };

export default function App() {
  const [phrases, setPhrases] = useState<Phrase[]>(examplePhrases);
  const [hoveredPhraseId, setHoveredPhraseId] = useState<number | null>(null);
  const [selectedPhraseId, setSelectedPhraseId] = useState<number | null>(null);
  const [overrideMenuPosition, setOverrideMenuPosition] = useState<Point | null>(null);

  // Display numbers based on chronological order (sentenceNumber)
  const phrasesWithDisplayNumbers = useMemo(() => {
    return [...phrases]
      .sort((a, b) => a.sentenceNumber - b.sentenceNumber)
      .map((phrase, index) => ({
        ...phrase,
        displayNumber: index + 1,
      }));
  }, [phrases]);

  const handleSelectPhrase = (id: number | null, menuPos?: Point) => {
    if (id === null) {
      setSelectedPhraseId(null);
      setOverrideMenuPosition(null);
      return;
    }

    setSelectedPhraseId(id);

    // If the map provides a click position, use it. Otherwise fall back.
    setOverrideMenuPosition(menuPos ?? { x: 600, y: 300 });
  };

  const getQuadrantPosition = (q: Quadrant): Point => {
    // Small random offset to reduce stacking
    const jitter = () => (Math.random() - 0.5) * 0.25;

    switch (q) {
      case "past-strengths":
        return { x: -0.5 + jitter(), y: 0.5 + jitter() };
      case "preferred-future":
        return { x: 0.5 + jitter(), y: 0.5 + jitter() };
      case "past-struggles":
        return { x: -0.5 + jitter(), y: -0.5 + jitter() };
      case "feared-future":
        return { x: 0.5 + jitter(), y: -0.5 + jitter() };
      default: {
        // Safety for future enum changes
        const _exhaustive: never = q;
        return _exhaustive;
      }
    }
  };

  const handleQuadrantOverride = (phraseId: number, quadrant: Quadrant) => {
    const newPos = getQuadrantPosition(quadrant);

    setPhrases((prev) =>
      prev.map((p) => (p.id === phraseId ? { ...p, quadrant, x: newPos.x, y: newPos.y } : p))
    );

    setOverrideMenuPosition(null);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Header />

      <div className="flex-1 flex overflow-hidden">
        {/* Left panel - Dialogic Map (70%) */}
        <div className="w-[70%] p-8">
          <DialogicMap
            phrases={phrasesWithDisplayNumbers}
            hoveredPhraseId={hoveredPhraseId}
            selectedPhraseId={selectedPhraseId}
            onHoverPhrase={setHoveredPhraseId}
            onSelectPhrase={handleSelectPhrase}
            overrideMenuPosition={overrideMenuPosition}
            onQuadrantOverride={handleQuadrantOverride}
          />
        </div>

        {/* Right panel - Side Panel (30%) */}
        <div className="w-[30%]">
          <SidePanel
            phrases={phrasesWithDisplayNumbers}
            hoveredPhraseId={hoveredPhraseId}
            selectedPhraseId={selectedPhraseId}
            onHoverPhrase={setHoveredPhraseId}
            onSelectPhrase={handleSelectPhrase}
          />
        </div>
      </div>
    </div>
  );
}