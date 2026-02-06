import React, { useState } from 'react';
import { ChevronRight, Loader2 } from 'lucide-react';

export const InputPanel = ({ onSubmit, isLoading, disabled }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSubmit(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="input-panel glass-panel rounded-lg" data-testid="input-panel">
      <div className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-2 h-2 rounded-full bg-emerald-500" />
          <span className="font-mono text-xs text-zinc-400 uppercase tracking-wider">
            Socratic Input Terminal
          </span>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="flex items-start gap-2 bg-zinc-950 rounded border border-zinc-800 p-3">
            <span className="text-indigo-500 font-mono text-sm mt-0.5">{'>'}</span>
            <textarea
              data-testid="prompt-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe your system requirements..."
              disabled={disabled}
              className="terminal-input flex-1 resize-none text-sm leading-relaxed min-h-[60px] max-h-[120px]"
              rows={2}
            />
            <button
              type="submit"
              data-testid="submit-prompt-btn"
              disabled={disabled || !input.trim()}
              className="flex items-center justify-center w-8 h-8 rounded bg-indigo-500 hover:bg-indigo-600 disabled:bg-zinc-800 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <Loader2 size={16} className="text-white animate-spin" />
              ) : (
                <ChevronRight size={16} className="text-white" />
              )}
            </button>
          </div>
        </form>
        
        <div className="mt-2 text-[10px] text-zinc-600 font-mono">
          Press Enter to submit • Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default InputPanel;
