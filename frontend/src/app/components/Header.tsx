import { Logo } from './Logo';

export function Header() {
  return (
    <header className="h-16 border-b border-gray-200 bg-white flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <Logo />
        <h1 className="text-lg tracking-tight text-gray-900">Conversation Canvas</h1>
      </div>
      
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-sm text-gray-600">Live Session</span>
        </div>
        <span className="text-sm text-gray-400">24:13</span>
      </div>
    </header>
  );
}