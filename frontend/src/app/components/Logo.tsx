export function Logo() {
  return (
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Conversation bubbles forming a map-like pattern */}
      <g>
        {/* Top-left bubble (Past Strengths) - Blue */}
        <circle cx="10" cy="10" r="4" fill="#3B82F6" opacity="0.8" />
        <circle cx="10" cy="10" r="2" fill="#3B82F6" />
        
        {/* Top-right bubble (Preferred Future) - Green */}
        <circle cx="22" cy="10" r="4.5" fill="#10B981" opacity="0.8" />
        <circle cx="22" cy="10" r="2.5" fill="#10B981" />
        
        {/* Bottom-left bubble (Past Struggles) - Amber */}
        <circle cx="10" cy="22" r="3.5" fill="#F59E0B" opacity="0.8" />
        <circle cx="10" cy="22" r="1.5" fill="#F59E0B" />
        
        {/* Bottom-right bubble (Feared Future) - Rose */}
        <circle cx="22" cy="22" r="3" fill="#F43F5E" opacity="0.8" />
        <circle cx="22" cy="22" r="1" fill="#F43F5E" />
        
        {/* Center connecting lines forming crosshairs */}
        <line x1="16" y1="4" x2="16" y2="28" stroke="#6B7280" strokeWidth="0.5" opacity="0.3" />
        <line x1="4" y1="16" x2="28" y2="16" stroke="#6B7280" strokeWidth="0.5" opacity="0.3" />
        
        {/* Central point */}
        <circle cx="16" cy="16" r="1.5" fill="#6B7280" opacity="0.4" />
      </g>
    </svg>
  );
}
