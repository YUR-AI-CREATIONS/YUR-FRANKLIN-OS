import React from 'react';
import { X, GitBranch, Users, ListTodo, Plug } from 'lucide-react';

export const PipelinePanel = ({ project, currentStage, stages, onClose }) => {
  if (!project) return null;

  return (
    <div 
      className="fixed top-20 left-6 w-[320px] glass-panel rounded-xl overflow-hidden animate-fade-in z-40"
      data-testid="pipeline-panel"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <GitBranch size={18} className="text-indigo-400" />
          <h2 className="font-mono text-sm font-bold text-zinc-100 uppercase tracking-wider">
            Genesis Pipeline
          </h2>
        </div>
        <button
          onClick={onClose}
          className="w-6 h-6 flex items-center justify-center rounded hover:bg-zinc-800 text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          <X size={14} />
        </button>
      </div>
      
      {/* Project Info */}
      <div className="p-4 border-b border-zinc-800">
        <div className="text-[10px] text-zinc-500 font-mono uppercase mb-1">Orchestrator ID</div>
        <div className="text-xs text-zinc-300 font-mono truncate">
          {project.orchestrator_id}
        </div>
      </div>
      
      {/* Stages */}
      <div className="p-4">
        <h3 className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider mb-3">
          Pipeline Stages
        </h3>
        <div className="space-y-2">
          {stages.map((stage, index) => {
            const isCurrent = stage === currentStage;
            const isPast = stages.indexOf(currentStage) > index;
            
            return (
              <div 
                key={stage}
                className={`flex items-center gap-3 px-3 py-2 rounded ${
                  isCurrent ? 'bg-indigo-500/20 border border-indigo-500/30' :
                  isPast ? 'bg-emerald-500/10 border border-emerald-500/20' :
                  'bg-zinc-900 border border-zinc-800'
                }`}
              >
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono ${
                  isCurrent ? 'bg-indigo-500 text-white' :
                  isPast ? 'bg-emerald-500 text-white' :
                  'bg-zinc-800 text-zinc-500'
                }`}>
                  {index + 1}
                </div>
                <span className={`text-xs font-mono capitalize ${
                  isCurrent ? 'text-indigo-300' :
                  isPast ? 'text-emerald-300' :
                  'text-zinc-500'
                }`}>
                  {stage}
                </span>
                {isCurrent && (
                  <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-indigo-500 text-white font-mono">
                    ACTIVE
                  </span>
                )}
                {isPast && (
                  <span className="ml-auto text-[10px] text-emerald-400">✓</span>
                )}
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Agents Summary */}
      {project.agents && (
        <div className="p-4 border-t border-zinc-800">
          <h3 className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider mb-2 flex items-center gap-2">
            <Users size={12} />
            Active Agents
          </h3>
          <div className="flex flex-wrap gap-1">
            {project.agents.slice(0, 4).map((agent) => (
              <span 
                key={agent.id}
                className="text-[10px] px-2 py-1 rounded bg-zinc-800 text-zinc-400 font-mono"
              >
                {agent.name}
              </span>
            ))}
            {project.agents.length > 4 && (
              <span className="text-[10px] px-2 py-1 text-zinc-500 font-mono">
                +{project.agents.length - 4} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PipelinePanel;
