import type { Phrase } from '../types';
import { QuadrantChip } from './QuadrantChip';

interface PhraseRowProps {
  phrase: Phrase;
  isHovered: boolean;
  isSelected: boolean;
  onHover: (id: number | null) => void;
  onClick: (id: number) => void;
}

export function PhraseRow({ phrase, isHovered, isSelected, onHover, onClick }: PhraseRowProps) {
  return (
    <div
      className={`px-4 py-3 border-b border-gray-100 cursor-pointer transition-colors ${
        isHovered || isSelected ? 'bg-gray-50' : 'bg-white hover:bg-gray-50'
      }`}
      onMouseEnter={() => onHover(phrase.id)}
      onMouseLeave={() => onHover(null)}
      onClick={() => onClick(phrase.id)}
    >
      <div className="flex items-start gap-3">
        <span className="text-sm text-gray-400 mt-0.5 shrink-0">{phrase.displayNumber}</span>
        <div className="flex-1 min-w-0">
          <div className="text-sm text-gray-900 mb-1.5">{phrase.text}</div>
          <div className="flex items-center gap-2 mb-1">
            <QuadrantChip quadrant={phrase.quadrant} />
          </div>
          <div className="text-xs text-gray-400">
            sentence {phrase.sentenceNumber} | extract {phrase.extractScore?.toFixed(2) ?? '0.00'} | confidence {phrase.confidence?.toFixed(2) ?? '0.00'}
          </div>
        </div>
      </div>
    </div>
  );
}