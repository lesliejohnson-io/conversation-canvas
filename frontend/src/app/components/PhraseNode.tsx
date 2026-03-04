import type { Phrase } from '../types';

interface PhraseNodeProps {
  phrase: Phrase;
  isHovered: boolean;
  isSelected: boolean;
  onHover: (id: number | null) => void;
  onClick: (id: number, event: React.MouseEvent) => void;
}

export function PhraseNode({ phrase, isHovered, isSelected, onHover, onClick }: PhraseNodeProps) {
  // Convert normalized coordinates to SVG coordinates
  const x = 400 + phrase.x * 350; // Center at 400, scale by 350
  const y = 400 - phrase.y * 350; // Invert Y axis (SVG Y increases downward)

  // Size based on whether it's repeated (not importance)
  const baseSize = phrase.isRepeated ? 12 : 8;
  const size = isHovered || isSelected ? baseSize * 1.2 : baseSize;

  const handleMouseEnter = () => {
    onHover(phrase.id);
  };

  const handleMouseLeave = () => {
    onHover(null);
  };

  const handleClick = (event: React.MouseEvent) => {
    onClick(phrase.id, event);
  };

  return (
    <g
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
      className="cursor-pointer"
      style={{ transition: 'all 0.2s ease' }}
    >
      {/* Phrase circle */}
      <circle
        cx={x}
        cy={y}
        r={size}
        className={`fill-indigo-600 ${isHovered || isSelected ? 'opacity-100' : 'opacity-80'}`}
        style={{
          transition: 'all 0.2s ease',
          stroke: isSelected ? '#4f46e5' : 'none',
          strokeWidth: isSelected ? 3 : 0,
        }}
      />

      {/* Sentence number inside the circle */}
      <text
        x={x}
        y={y + 1}
        textAnchor="middle"
        dominantBaseline="middle"
        className="text-xs fill-white pointer-events-none select-none font-semibold"
        style={{ fontSize: '11px' }}
      >
        {phrase.displayNumber}
      </text>

      {/* Phrase text */}
      <text
        x={x}
        y={y + size + 14}
        textAnchor="middle"
        className="text-xs fill-gray-700 pointer-events-none select-none"
        style={{
          fontWeight: isHovered || isSelected ? 600 : 400,
          transition: 'all 0.2s ease',
        }}
      >
        {phrase.label}
      </text>
    </g>
  );
}