import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { FileCode2 } from 'lucide-react';

const SpecNode = memo(({ data, selected }) => {
  const spec = data.spec?.specification || data.spec || {};
  
  return (
    <div 
      className={`sgp-node px-4 py-3 rounded-lg border-2 border-indigo-500 bg-indigo-500/10 min-w-[220px] max-w-[300px] ${
        selected ? 'glow-brand' : ''
      }`}
      data-testid="spec-node"
    >
      <Handle 
        type="target" 
        position={Position.Left} 
        className="!bg-indigo-500 !w-3 !h-3 !border-2 !border-zinc-900"
      />
      
      <div className="flex items-center gap-2 mb-2">
        <FileCode2 size={14} className="text-indigo-400" />
        <span className="font-mono text-xs text-indigo-400 uppercase tracking-wider">
          {data.label || 'Specification'}
        </span>
      </div>
      
      {spec.title && (
        <div className="text-sm text-indigo-200 font-medium mb-2">
          {spec.title}
        </div>
      )}
      
      <div className="space-y-1">
        {spec.architecture?.pattern && (
          <div className="text-xs text-zinc-400">
            <span className="text-zinc-500">Pattern:</span> {spec.architecture.pattern}
          </div>
        )}
        {spec.architecture?.components && (
          <div className="text-xs text-zinc-400">
            <span className="text-zinc-500">Components:</span> {spec.architecture.components.length}
          </div>
        )}
        {spec.security?.authentication && (
          <div className="text-xs text-zinc-400">
            <span className="text-zinc-500">Auth:</span> {spec.security.authentication}
          </div>
        )}
      </div>
      
      <div className="mt-2 text-[10px] text-indigo-400 font-mono">
        Click to view full spec
      </div>
    </div>
  );
});

SpecNode.displayName = 'SpecNode';
export default SpecNode;
