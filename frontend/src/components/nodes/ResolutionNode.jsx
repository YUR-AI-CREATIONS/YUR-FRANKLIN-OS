import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { CheckCircle2 } from 'lucide-react';

const ResolutionNode = memo(({ data, selected }) => {
  return (
    <div 
      className={`sgp-node px-4 py-3 rounded-lg border-2 border-emerald-500 bg-emerald-500/10 min-w-[200px] max-w-[280px] ${
        selected ? 'glow-resolution' : ''
      }`}
      data-testid="resolution-node"
    >
      <Handle 
        type="target" 
        position={Position.Left} 
        className="!bg-emerald-500 !w-3 !h-3 !border-2 !border-zinc-900"
      />
      <Handle 
        type="source" 
        position={Position.Right} 
        className="!bg-emerald-500 !w-3 !h-3 !border-2 !border-zinc-900"
      />
      
      <div className="flex items-center gap-2 mb-2">
        <CheckCircle2 size={14} className="text-emerald-400" />
        <span className="font-mono text-xs text-emerald-400 uppercase tracking-wider">
          {data.label || 'Resolved'}
        </span>
      </div>
      
      <div className="text-xs text-zinc-400 font-mono mb-1">
        {data.ambiguity_id}
      </div>
      
      <div className="text-sm text-emerald-200 font-medium leading-relaxed break-words">
        {data.answer?.length > 100 
          ? `${data.answer.substring(0, 100)}...` 
          : data.answer
        }
      </div>
    </div>
  );
});

ResolutionNode.displayName = 'ResolutionNode';
export default ResolutionNode;
