import React, { useState, useEffect } from 'react';
import { Cloud, Server, Zap, Settings, Check, AlertTriangle, Loader2 } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LLM_MODES = [
  { 
    id: 'cloud', 
    label: 'Cloud', 
    icon: Cloud, 
    description: 'Claude via Emergent Key',
    color: 'indigo',
    costLabel: 'Pay per request'
  },
  { 
    id: 'local', 
    label: 'Local', 
    icon: Server, 
    description: 'Ollama (Llama 3.1)',
    color: 'emerald',
    costLabel: 'Free & Private'
  },
  { 
    id: 'hybrid', 
    label: 'Hybrid', 
    icon: Zap, 
    description: 'Local + Cloud Fallback',
    color: 'amber',
    costLabel: 'Smart routing'
  }
];

export const LLMSelector = ({ onStatusChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API}/llm/status`);
      setStatus(response.data);
      if (onStatusChange) onStatusChange(response.data);
    } catch (err) {
      setError('Failed to fetch LLM status');
    }
  };

  useEffect(() => {
    fetchStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const switchMode = async (mode) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API}/llm/config`, {
        mode: mode,
        fallback_to_cloud: true
      });
      setStatus({ ...status, configuration: response.data.configuration });
      if (onStatusChange) onStatusChange({ ...status, configuration: response.data.configuration });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to switch mode');
    } finally {
      setIsLoading(false);
    }
  };

  const currentMode = status?.configuration?.mode || 'cloud';
  const localAvailable = status?.configuration?.local_available || false;
  const requestCounts = status?.configuration?.request_counts || { local: 0, cloud: 0 };

  const getCurrentModeConfig = () => LLM_MODES.find(m => m.id === currentMode) || LLM_MODES[0];
  const currentConfig = getCurrentModeConfig();
  const ModeIcon = currentConfig.icon;

  return (
    <div className="relative" data-testid="llm-selector">
      {/* Compact Toggle Button */}
      <button
        data-testid="llm-selector-toggle"
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-3 py-1.5 rounded border transition-all ${
          currentMode === 'cloud' 
            ? 'bg-indigo-500/20 border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/30' 
            : currentMode === 'local'
            ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/30'
            : 'bg-amber-500/20 border-amber-500/30 text-amber-300 hover:bg-amber-500/30'
        }`}
      >
        <ModeIcon size={14} />
        <span className="text-xs font-mono">{currentConfig.label}</span>
        {!localAvailable && currentMode !== 'cloud' && (
          <AlertTriangle size={12} className="text-amber-400" />
        )}
        <Settings size={12} className="opacity-50" />
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div 
          className="absolute top-full right-0 mt-2 w-72 glass-panel rounded-lg border border-zinc-800 p-3 z-50 animate-slide-in"
          data-testid="llm-selector-dropdown"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono text-zinc-400 uppercase tracking-wider">LLM Provider</span>
            {isLoading && <Loader2 size={14} className="text-indigo-400 animate-spin" />}
          </div>

          {/* Mode Options */}
          <div className="space-y-2">
            {LLM_MODES.map((mode) => {
              const Icon = mode.icon;
              const isActive = currentMode === mode.id;
              const isDisabled = mode.id === 'local' && !localAvailable;
              
              return (
                <button
                  key={mode.id}
                  data-testid={`llm-mode-${mode.id}`}
                  onClick={() => !isDisabled && switchMode(mode.id)}
                  disabled={isDisabled || isLoading}
                  className={`w-full flex items-center gap-3 p-2.5 rounded-lg border transition-all text-left ${
                    isActive 
                      ? `bg-${mode.color}-500/20 border-${mode.color}-500/40` 
                      : isDisabled
                      ? 'bg-zinc-900/50 border-zinc-800/50 opacity-50 cursor-not-allowed'
                      : 'bg-zinc-900 border-zinc-800 hover:border-zinc-700'
                  }`}
                >
                  <div className={`w-8 h-8 rounded flex items-center justify-center ${
                    isActive ? `bg-${mode.color}-500/30` : 'bg-zinc-800'
                  }`}>
                    <Icon size={16} className={isActive ? `text-${mode.color}-400` : 'text-zinc-500'} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className={`text-sm font-mono ${isActive ? 'text-zinc-100' : 'text-zinc-400'}`}>
                        {mode.label}
                      </span>
                      {isActive && <Check size={12} className={`text-${mode.color}-400`} />}
                    </div>
                    <span className="text-xs text-zinc-500">{mode.description}</span>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded ${
                    mode.id === 'local' ? 'bg-emerald-500/20 text-emerald-400' :
                    mode.id === 'cloud' ? 'bg-indigo-500/20 text-indigo-400' :
                    'bg-amber-500/20 text-amber-400'
                  }`}>
                    {mode.costLabel}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Status Info */}
          <div className="mt-3 pt-3 border-t border-zinc-800">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${localAvailable ? 'bg-emerald-500' : 'bg-zinc-600'}`} />
                <span className="text-zinc-500">Local LLM</span>
                <span className={localAvailable ? 'text-emerald-400' : 'text-zinc-600'}>
                  {localAvailable ? 'Available' : 'Not Running'}
                </span>
              </div>
            </div>
            
            <div className="flex items-center gap-4 mt-2 text-xs text-zinc-500">
              <span>Requests: <span className="text-zinc-300">{requestCounts.cloud}</span> cloud</span>
              <span><span className="text-zinc-300">{requestCounts.local}</span> local</span>
            </div>

            {!localAvailable && (
              <div className="mt-2 p-2 rounded bg-amber-500/10 border border-amber-500/20">
                <p className="text-[10px] text-amber-400 font-mono">
                  Local LLM requires Ollama. Run: ollama pull llama3.1:8b
                </p>
              </div>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="mt-2 p-2 rounded bg-red-500/10 border border-red-500/20">
              <p className="text-xs text-red-400">{error}</p>
            </div>
          )}
        </div>
      )}

      {/* Click outside to close */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default LLMSelector;
