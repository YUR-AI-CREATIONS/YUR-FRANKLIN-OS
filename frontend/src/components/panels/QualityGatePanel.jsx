import React from 'react';
import { X, Shield, AlertCircle, CheckCircle, RefreshCw, Loader2 } from 'lucide-react';

export const QualityGatePanel = ({ assessment, stage, onClose, onRunOuroboros, isLoading }) => {
  if (!assessment) return null;
  
  const { aggregate_score, passed, dimension_scores, gaps_count, improvement_priority } = assessment;
  
  const getScoreColor = (score) => {
    if (score >= 90) return 'text-emerald-400';
    if (score >= 70) return 'text-amber-400';
    return 'text-red-400';
  };
  
  const getBarColor = (score) => {
    if (score >= 90) return 'bg-emerald-500';
    if (score >= 70) return 'bg-amber-500';
    return 'bg-red-500';
  };

  return (
    <div 
      className="fixed top-20 right-6 w-[420px] max-h-[calc(100vh-120px)] glass-panel rounded-xl overflow-hidden animate-slide-in z-40"
      data-testid="quality-gate-panel"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-zinc-800">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            passed ? 'bg-emerald-500/20' : 'bg-amber-500/20'
          }`}>
            <Shield size={20} className={passed ? 'text-emerald-400' : 'text-amber-400'} />
          </div>
          <div>
            <h2 className="font-mono text-sm font-bold text-zinc-100 uppercase tracking-wider">
              Quality Gate
            </h2>
            <p className="text-xs text-zinc-500 font-mono">
              Stage: {stage}
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="w-8 h-8 flex items-center justify-center rounded hover:bg-zinc-800 text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          <X size={18} />
        </button>
      </div>
      
      {/* Aggregate Score */}
      <div className="p-4 border-b border-zinc-800">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-zinc-400">Aggregate Score</span>
          <div className="flex items-center gap-2">
            {passed ? (
              <CheckCircle size={16} className="text-emerald-400" />
            ) : (
              <AlertCircle size={16} className="text-amber-400" />
            )}
            <span className={`text-2xl font-mono font-bold ${getScoreColor(aggregate_score)}`}>
              {aggregate_score.toFixed(1)}%
            </span>
          </div>
        </div>
        <div className="w-full h-3 bg-zinc-800 rounded-full overflow-hidden">
          <div 
            className={`h-full transition-all duration-500 ${getBarColor(aggregate_score)}`}
            style={{ width: `${aggregate_score}%` }}
          />
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-[10px] text-zinc-600 font-mono">0%</span>
          <span className="text-[10px] text-emerald-600 font-mono">99% Target</span>
          <span className="text-[10px] text-zinc-600 font-mono">100%</span>
        </div>
      </div>
      
      {/* Dimension Scores */}
      <div className="p-4 max-h-[300px] overflow-y-auto">
        <h3 className="text-xs font-mono text-zinc-500 uppercase tracking-wider mb-3">
          Quality Dimensions ({gaps_count} gaps)
        </h3>
        <div className="space-y-3">
          {dimension_scores?.map((dim) => (
            <div key={dim.dimension} className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs text-zinc-300 capitalize">
                  {dim.dimension.replace('_', ' ')}
                </span>
                <span className={`text-xs font-mono font-bold ${getScoreColor(dim.score)}`}>
                  {dim.score.toFixed(0)}%
                </span>
              </div>
              <div className="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all ${getBarColor(dim.score)}`}
                  style={{ width: `${dim.score}%` }}
                />
              </div>
              {dim.findings?.length > 0 && (
                <p className="text-[10px] text-amber-400/80 pl-2 border-l border-amber-500/30">
                  {dim.findings[0]}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
      
      {/* Improvement Priority */}
      {improvement_priority?.length > 0 && (
        <div className="p-4 border-t border-zinc-800 bg-zinc-900/50">
          <h3 className="text-xs font-mono text-zinc-500 uppercase tracking-wider mb-2">
            Improvement Priority
          </h3>
          <div className="flex flex-wrap gap-1">
            {improvement_priority.map((dim, i) => (
              <span 
                key={dim}
                className="text-[10px] px-2 py-1 rounded bg-amber-500/20 text-amber-300 font-mono"
              >
                {i + 1}. {dim}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {/* Action Button */}
      {!passed && (
        <div className="p-4 border-t border-zinc-800">
          <button
            data-testid="run-ouroboros-btn"
            onClick={onRunOuroboros}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-indigo-500 hover:bg-indigo-600 disabled:bg-zinc-800 disabled:cursor-not-allowed text-white font-medium transition-colors"
          >
            {isLoading ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <RefreshCw size={18} />
            )}
            <span>{isLoading ? 'Running Ouroboros Loop...' : 'Execute Ouroboros (99% Convergence)'}</span>
          </button>
          <p className="text-[10px] text-zinc-600 text-center mt-2 font-mono">
            Self-referential improvement until quality threshold met
          </p>
        </div>
      )}
      
      {passed && (
        <div className="p-4 border-t border-zinc-800 bg-emerald-500/10">
          <div className="flex items-center justify-center gap-2 text-emerald-400">
            <CheckCircle size={20} />
            <span className="font-mono font-bold">QUALITY GATE PASSED</span>
          </div>
          <p className="text-xs text-emerald-300/70 text-center mt-1">
            Ready to advance to next stage
          </p>
        </div>
      )}
    </div>
  );
};

export default QualityGatePanel;
