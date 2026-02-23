import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Terminal } from 'lucide-react';

const InputNode = memo(({ data, selected }) => {
  return (
    <div 
      className={`sgp-node px-4 py-3 rounded-lg border bg-zinc-900 min-w-[200px] max-w-[280px] ${
        selected ? 'border-indigo-500 glow-brand' : 'border-zinc-700'
      }`}
      data-testid="input-node"
    >
      <Handle 
        type="source" 
        position={Position.Right} 
        className="!bg-indigo-500 !w-3 !h-3 !border-2 !border-zinc-900"
      />
      
      <div className="flex items-center gap-2 mb-2">
        <Terminal size={14} className="text-indigo-400" />
        <span className="font-mono text-xs text-indigo-400 uppercase tracking-wider">
          {data.label || 'User Input'}
        </span>
      </div>
      
      <div className="text-sm text-zinc-300 font-mono leading-relaxed break-words">
        {data.content?.length > 100 
          ? `${data.content.substring(0, 100)}...` 
          : data.content
        }
      </div>
    </div>
  );
});

InputNode.displayName = 'InputNode';
export default InputNode;
