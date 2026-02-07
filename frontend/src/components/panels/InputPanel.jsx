import React, { useState } from 'react';
import { ChevronRight, Loader2, Zap } from 'lucide-react';

const DEMO_PROMPTS = [
  "Build an e-commerce store with product catalog, shopping cart, and checkout",
  "Build a project management app with tasks, teams, and deadlines",
  "Build a CRM system with contacts, deals, and pipeline management",
  "Build a blog platform with posts, comments, and user accounts",
  "Build an inventory management system with stock tracking and alerts"
];

export const InputPanel = ({ onSubmit, onQuickSimulate, isLoading, disabled }) => {
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

  const handleQuickSimulate = () => {
    const randomPrompt = DEMO_PROMPTS[Math.floor(Math.random() * DEMO_PROMPTS.length)];
    if (onQuickSimulate) {
      onQuickSimulate(randomPrompt);
    }
  };

  return (
    <div className="input-panel glass-panel rounded-lg" data-testid="input-panel">
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="font-mono text-xs text-zinc-400 uppercase tracking-wider">
              Socratic Input Terminal
            </span>
          </div>
          <button
            type="button"
            data-testid="quick-simulate-btn"
            onClick={handleQuickSimulate}
            disabled={disabled || isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 hover:from-emerald-500/30 hover:to-cyan-500/30 border border-emerald-500/50 text-emerald-300 text-[10px] font-mono uppercase tracking-wider transition-all disabled:opacity-50"
          >
            <Zap size={12} className="text-yellow-400" />
            <span>Quick Build</span>
          </button>
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
          Press Enter to submit • Shift+Enter for new line • Or click Quick Demo for instant simulation
        </div>
      </div>
    </div>
  );
};

export default InputPanel;
