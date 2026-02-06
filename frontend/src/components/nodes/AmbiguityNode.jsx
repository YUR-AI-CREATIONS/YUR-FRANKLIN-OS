import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { AlertTriangle } from 'lucide-react';

const priorityColors = {
  CRITICAL: 'border-red-500 bg-red-500/10',
  HIGH: 'border-amber-500 bg-amber-500/10',
  MEDIUM: 'border-blue-500 bg-blue-500/10',
  LOW: 'border-zinc-500 bg-zinc-500/10'
};

const priorityTextColors = {
  CRITICAL: 'text-red-400',
  HIGH: 'text-amber-400',
  MEDIUM: 'text-blue-400',
  LOW: 'text-zinc-400'
};

const AmbiguityNode = memo(({ data, selected }) => {
  const priority = data.priority || 'MEDIUM';
  const colorClass = priorityColors[priority] || priorityColors.MEDIUM;
  const textColor = priorityTextColors[priority] || priorityTextColors.MEDIUM;

  return (
    <div 
      className={`sgp-node px-4 py-3 rounded-lg border-2 min-w-[220px] max-w-[300px] ${
        colorClass
      } ${selected ? 'glow-ambiguity' : ''}`}
      data-testid="ambiguity-node"
    >
      <Handle 
        type="target" 
        position={Position.Left} 
        className="!bg-amber-500 !w-3 !h-3 !border-2 !border-zinc-900"
      />
      <Handle 
        type="source" 
        position={Position.Right} 
        className="!bg-amber-500 !w-3 !h-3 !border-2 !border-zinc-900"
      />
      
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <AlertTriangle size={14} className={textColor} />
          <span className={`font-mono text-xs uppercase tracking-wider ${textColor}`}>
            {data.label || data.id}
          </span>
        </div>
        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${colorClass} ${textColor}`}>
          {priority}
        </span>
      </div>
      
      <div className="text-xs text-zinc-400 font-mono mb-2 uppercase">
        {data.category}
      </div>
      
      <div className="text-sm text-zinc-200 leading-relaxed">
        {data.question?.length > 80 
          ? `${data.question.substring(0, 80)}...` 
          : data.question
        }
      </div>
      
      {data.options && data.options.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {data.options.slice(0, 3).map((opt, i) => (
            <span 
              key={i}
              className="text-[10px] px-1.5 py-0.5 bg-zinc-800 rounded text-zinc-400 truncate max-w-[80px]"
            >
              {opt}
            </span>
          ))}
          {data.options.length > 3 && (
            <span className="text-[10px] text-zinc-500">+{data.options.length - 3}</span>
          )}
        </div>
      )}
    </div>
  );
});

AmbiguityNode.displayName = 'AmbiguityNode';
export default AmbiguityNode;
