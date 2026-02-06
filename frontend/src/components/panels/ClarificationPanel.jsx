import React from 'react';
import { AlertTriangle, Send, Loader2 } from 'lucide-react';

const priorityOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };

export const ClarificationPanel = ({ 
  ambiguities, 
  answers, 
  onAnswerChange, 
  onSubmit, 
  isLoading,
  confidenceScore 
}) => {
  const sortedAmbiguities = [...ambiguities].sort(
    (a, b) => (priorityOrder[a.priority] || 3) - (priorityOrder[b.priority] || 3)
  );

  const answeredCount = Object.keys(answers).length;
  const totalCount = ambiguities.length;
  const canSubmit = answeredCount > 0;

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
          <div className="text-[10px] text-zinc-600 mt-1 font-mono">
            Target: 99.5% required for specification generation
          </div>
        </div>

        {/* Questions */}
        <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
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
      
      {/* Options */}
      {ambiguity.options && ambiguity.options.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {ambiguity.options.map((opt, i) => (
            <button
              key={i}
              type="button"
              onClick={() => onChange(opt, opt)}
              className={`option-btn ${selectedOption === opt ? 'selected' : ''}`}
            >
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
