import React from 'react';
import { Zap, RotateCcw } from 'lucide-react';

export const Header = ({ session, onClear }) => {
  return (
    <header className="sgp-header" data-testid="sgp-header">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-indigo-500/20 flex items-center justify-center">
            <Zap size={18} className="text-indigo-400" />
          </div>
          <div>
            <h1 className="font-mono text-sm font-bold tracking-tight text-zinc-100">
              SOVEREIGN GENESIS
            </h1>
            <p className="text-[10px] text-zinc-500 font-mono uppercase tracking-widest">
              Neural-Symbolic Engine
            </p>
          </div>
        </div>
        
        {session && (
          <div className="ml-6 flex items-center gap-3">
            <div className="h-6 w-px bg-zinc-800" />
            <div className="flex items-center gap-2">
              <div className={`status-dot ${
                session.can_proceed ? 'bg-emerald-500' : 
                session.confidence_score >= 70 ? 'bg-amber-500' : 'bg-red-500'
              }`} />
              <span className="text-xs font-mono text-zinc-400">
                Session: {session.session_id?.substring(0, 8)}...
              </span>
            </div>
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-3">
        {session && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded bg-zinc-900 border border-zinc-800">
            <span className="text-xs text-zinc-500 font-mono">Confidence:</span>
            <span className={`text-sm font-mono font-bold ${
              session.confidence_score >= 99.5 ? 'text-emerald-400' : 
              session.confidence_score >= 70 ? 'text-amber-400' : 'text-red-400'
            }`}>
              {session.confidence_score?.toFixed(1) || 0}%
            </span>
          </div>
        )}
        
        <button
          data-testid="clear-canvas-btn"
          onClick={onClear}
          className="flex items-center gap-2 px-3 py-1.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700 transition-colors"
        >
          <RotateCcw size={14} />
          <span className="text-xs font-mono">Clear</span>
        </button>
      </div>
    </header>
  );
};

export default Header;
