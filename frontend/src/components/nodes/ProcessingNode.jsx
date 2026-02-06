import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Cpu, Loader2, CheckCircle } from 'lucide-react';

const ProcessingNode = memo(({ data, selected }) => {
  const status = data.status || 'idle';
  const isProcessing = status === 'analyzing' || status === 'processing';
  const isComplete = status === 'complete' || status === 'ready';

  return (
    <div 
      className={`sgp-node px-4 py-3 rounded-lg border bg-zinc-900 min-w-[180px] ${
        selected ? 'border-indigo-500 glow-brand' : 'border-zinc-700'
      } ${isProcessing ? 'animate-pulse-glow' : ''}`}
      data-testid="processing-node"
    >
      <Handle 
        type="target" 
        position={Position.Left} 
        className="!bg-indigo-500 !w-3 !h-3 !border-2 !border-zinc-900"
      />
      <Handle 
        type="source" 
        position={Position.Right} 
        className="!bg-indigo-500 !w-3 !h-3 !border-2 !border-zinc-900"
      />
      
      <div className="flex items-center gap-2 mb-2">
        {isProcessing ? (
          <Loader2 size={14} className="text-indigo-400 animate-spin" />
        ) : isComplete ? (
          <CheckCircle size={14} className="text-emerald-400" />
        ) : (
          <Cpu size={14} className="text-zinc-400" />
        )}
        <span className={`font-mono text-xs uppercase tracking-wider ${
          isProcessing ? 'text-indigo-400' : isComplete ? 'text-emerald-400' : 'text-zinc-400'
        }`}>
          {data.label || 'Processing'}
        </span>
      </div>
      
      <div className={`text-xs font-mono ${
        isProcessing ? 'text-indigo-300' : isComplete ? 'text-emerald-300' : 'text-zinc-500'
      }`}>
        {isProcessing ? 'Analyzing...' : isComplete ? 'Complete' : 'Idle'}
      </div>
      
      {data.confidence !== undefined && (
        <div className="mt-2">
          <div className="confidence-meter">
            <div 
              className="confidence-fill"
              style={{ 
                width: `${data.confidence}%`,
                backgroundColor: data.confidence >= 99.5 ? '#10B981' : 
                                 data.confidence >= 70 ? '#F59E0B' : '#EF4444'
              }}
            />
          </div>
          <div className="text-[10px] text-zinc-500 mt-1 text-right font-mono">
            {data.confidence.toFixed(1)}%
          </div>
        </div>
      )}
    </div>
  );
});

ProcessingNode.displayName = 'ProcessingNode';
export default ProcessingNode;
