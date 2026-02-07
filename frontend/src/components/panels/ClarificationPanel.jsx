import React from 'react';
import { AlertTriangle, Send, Loader2, Sparkles, Zap, Star } from 'lucide-react';

const priorityOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };

export const ClarificationPanel = ({ 
  ambiguities, 
  answers, 
  onAnswerChange, 
  onSubmit, 
  onSimulate,
  isLoading,
  confidenceScore 
}) => {
  const sortedAmbiguities = [...ambiguities].sort(
    (a, b) => (priorityOrder[a.priority] || 3) - (priorityOrder[b.priority] || 3)
  );

  const answeredCount = Object.keys(answers).length;
  const totalCount = ambiguities.length;
  const canSubmit = answeredCount > 0;

  // Auto-select all AI recommended answers
  const handleSelectAllRecommended = () => {
    sortedAmbiguities.forEach(amb => {
      if (amb.options && amb.options.length > 0) {
        const recommended = amb.options[0]; // First option is AI recommended
        onAnswerChange(amb.id, recommended, recommended);
      }
    });
  };

  return (
    <div className="clarification-panel glass-panel rounded-lg animate-slide-in" data-testid="clarification-panel">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} className="text-amber-500" />
            <span className="font-mono text-sm font-bold text-amber-400 uppercase tracking-wider">
              Ambiguities Detected
            </span>
          </div>
          <span className="text-xs font-mono text-zinc-500">
            {answeredCount}/{totalCount} answered
          </span>
        </div>

        {/* Confidence Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] font-mono text-zinc-500 uppercase">Specification Confidence</span>
            <span className={`text-xs font-mono font-bold ${
              confidenceScore >= 99.5 ? 'text-emerald-400' : 
              confidenceScore >= 70 ? 'text-amber-400' : 'text-red-400'
            }`}>
              {confidenceScore?.toFixed(1) || 0}%
            </span>
          </div>
          <div className="confidence-meter">
            <div 
              className="confidence-fill"
              style={{ 
                width: `${confidenceScore || 0}%`,
                backgroundColor: confidenceScore >= 99.5 ? '#10B981' : 
                                 confidenceScore >= 70 ? '#F59E0B' : '#EF4444'
              }}
            />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex gap-2 mb-4">
          <button
            data-testid="select-recommended-btn"
            onClick={handleSelectAllRecommended}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded bg-indigo-500/20 hover:bg-indigo-500/30 border border-indigo-500/50 text-indigo-300 text-xs font-mono transition-all"
          >
            <Star size={14} className="text-yellow-400" />
            <span>Use AI Recommendations</span>
          </button>
          <button
            data-testid="simulate-build-btn"
            onClick={onSimulate}
            disabled={isLoading}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 hover:from-emerald-500/30 hover:to-cyan-500/30 border border-emerald-500/50 text-emerald-300 text-xs font-mono transition-all disabled:opacity-50"
          >
            <Zap size={14} className="text-yellow-400" />
            <span>Auto Build All Stages</span>
          </button>
        </div>

        {/* Questions */}
        <div className="space-y-3 max-h-[350px] overflow-y-auto pr-1">
          {sortedAmbiguities.map((amb) => (
            <QuestionCard
              key={amb.id}
              ambiguity={amb}
              answer={answers[amb.id]}
              onChange={(answer, option) => onAnswerChange(amb.id, answer, option)}
            />
          ))}
        </div>

        {/* Submit Button */}
        <div className="mt-4 pt-4 border-t border-zinc-800">
          <button
            data-testid="submit-answers-btn"
            onClick={onSubmit}
            disabled={!canSubmit || isLoading}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded bg-amber-500 hover:bg-amber-600 disabled:bg-zinc-800 disabled:cursor-not-allowed text-black font-medium transition-colors"
          >
            {isLoading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Send size={16} />
            )}
            <span>{isLoading ? 'Processing...' : 'Submit Answers'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

const QuestionCard = ({ ambiguity, answer, onChange }) => {
  const priorityClass = {
    CRITICAL: 'critical',
    HIGH: 'high',
    MEDIUM: 'medium',
    LOW: 'low'
  }[ambiguity.priority] || 'medium';

  const selectedOption = answer?.selected_option;
  const customAnswer = answer?.answer;

  return (
    <div 
      className={`question-card ${priorityClass} bg-zinc-900/50 rounded p-3`}
      data-testid={`question-${ambiguity.id}`}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="font-mono text-[10px] text-zinc-500 uppercase">
          {ambiguity.category} • {ambiguity.id}
        </span>
        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
          ambiguity.priority === 'CRITICAL' ? 'bg-red-500/20 text-red-400' :
          ambiguity.priority === 'HIGH' ? 'bg-amber-500/20 text-amber-400' :
          ambiguity.priority === 'MEDIUM' ? 'bg-blue-500/20 text-blue-400' :
          'bg-zinc-500/20 text-zinc-400'
        }`}>
          {ambiguity.priority}
        </span>
      </div>
      
      <p className="text-sm text-zinc-200 mb-3 leading-relaxed">
        {ambiguity.question}
      </p>
      
      {/* Options with AI Recommendation */}
      {ambiguity.options && ambiguity.options.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {ambiguity.options.map((opt, i) => (
            <button
              key={i}
              type="button"
              onClick={() => onChange(opt, opt)}
              className={`relative option-btn ${selectedOption === opt ? 'selected' : ''} ${i === 0 ? 'ai-recommended' : ''}`}
              style={i === 0 ? {
                background: selectedOption === opt 
                  ? 'linear-gradient(135deg, #10B981 0%, #059669 100%)' 
                  : 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%)',
                borderColor: '#10B981',
                boxShadow: selectedOption !== opt ? '0 0 10px rgba(16, 185, 129, 0.3)' : 'none'
              } : {}}
            >
              {i === 0 && (
                <span className="absolute -top-2 -right-2 flex items-center gap-0.5 px-1.5 py-0.5 bg-emerald-500 text-[8px] text-white font-bold rounded-full shadow-lg">
                  <Sparkles size={8} />
                  AI
                </span>
              )}
              {opt}
            </button>
          ))}
        </div>
      )}
      
      {/* Custom Input */}
      <input
        type="text"
        placeholder="Or type custom answer..."
        value={customAnswer || ''}
        onChange={(e) => onChange(e.target.value, null)}
        className="w-full px-3 py-2 bg-zinc-950 border border-zinc-800 rounded text-sm text-zinc-300 placeholder:text-zinc-600 focus:border-indigo-500 focus:outline-none font-mono"
      />
    </div>
  );
};

export default ClarificationPanel;
