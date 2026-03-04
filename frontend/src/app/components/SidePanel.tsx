import type { Phrase } from '../types';
import { PhraseRow } from './PhraseRow';

interface SidePanelProps {
  phrases: Phrase[];
  hoveredPhraseId: number | null;
  selectedPhraseId: number | null;
  onHoverPhrase: (id: number | null) => void;
  onSelectPhrase: (id: number | null) => void;
}

export function SidePanel({
  phrases,
  hoveredPhraseId,
  selectedPhraseId,
  onHoverPhrase,
  onSelectPhrase,
}: SidePanelProps) {
  // Phrases are already sorted and numbered by App.tsx
  return (
    <div className="h-full bg-white border-l border-gray-200 flex flex-col">
      <div className="px-4 py-4 border-b border-gray-200">
        <h2 className="text-sm text-gray-900">Captured Phrases</h2>
        <p className="text-xs text-gray-500 mt-1">{phrases.length} phrases</p>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {phrases.map((phrase) => (
          <PhraseRow
            key={phrase.id}
            phrase={phrase}
            isHovered={hoveredPhraseId === phrase.id}
            isSelected={selectedPhraseId === phrase.id}
            onHover={onHoverPhrase}
            onClick={onSelectPhrase}
          />
        ))}
      </div>
    </div>
  );
}