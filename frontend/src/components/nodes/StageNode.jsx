import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Layers, CheckCircle2, AlertTriangle, Loader2, Play } from 'lucide-react';

const statusConfig = {
  pending: { color: 'zinc', icon: Layers, glow: false },
  active: { color: 'indigo', icon: Loader2, glow: true, animate: true },
  passed: { color: 'emerald', icon: CheckCircle2, glow: true },
  completed: { color: 'emerald', icon: CheckCircle2, glow: true },
  failed: { color: 'red', icon: AlertTriangle, glow: true },
  drift: { color: 'amber', icon: AlertTriangle, glow: true },
};

const StageNode = memo(({ data, selected }) => {
  const status = data.status || 'pending';
  const config = statusConfig[status] || statusConfig.pending;
  const Icon = config.icon;
  const isProcessing = data.isProcessing || false;
  
  const colorClasses = {
    zinc: 'border-zinc-600 bg-zinc-900/80 text-zinc-400',
    indigo: 'border-indigo-500 bg-indigo-500/10 text-indigo-300',
    emerald: 'border-emerald-500 bg-emerald-500/10 text-emerald-300',
    red: 'border-red-500 bg-red-500/10 text-red-300',
    amber: 'border-amber-500 bg-amber-500/10 text-amber-300',
  };
  
  const glowClasses = {
    indigo: 'shadow-[0_0_30px_rgba(99,102,241,0.6)]',
    emerald: 'shadow-[0_0_30px_rgba(16,185,129,0.6)]',
    red: 'shadow-[0_0_30px_rgba(239,68,68,0.6)]',
    amber: 'shadow-[0_0_30px_rgba(245,158,11,0.6)]',
  };

  const handleRunStage = (e) => {
    e.stopPropagation();
    if (data.onRunStage) {
      data.onRunStage(data.stage);
    }
  };

  return (
    <div 
      className={`stage-node-container relative ${status === 'active' || isProcessing ? 'stage-active-tracer' : ''}`}
      data-testid={`stage-node-${data.stage}`}
    >
      {/* Tracer animation ring for active/processing stages */}
      {(status === 'active' || isProcessing) && (
        <div className="absolute inset-0 rounded-xl stage-tracer-ring" />
      )}
      <div 
        className={`sgp-node px-5 py-4 rounded-xl border-2 min-w-[160px] text-center backdrop-blur-sm ${
          colorClasses[config.color]
        } ${config.glow ? glowClasses[config.color] || '' : ''} ${
          selected ? 'ring-2 ring-white/30' : ''
        } transition-all duration-300`}
      >
      <Handle 
        type="target" 
        position={Position.Left} 
        className={`!bg-${config.color}-500 !w-3 !h-3 !border-2 !border-zinc-900`}
      />
      <Handle 
        type="source" 
        position={Position.Right} 
        className={`!bg-${config.color}-500 !w-3 !h-3 !border-2 !border-zinc-900`}
      />
      
      <div className="flex flex-col items-center gap-2">
        <Icon 
          size={24} 
          className={config.animate ? 'animate-spin' : ''} 
        />
        <span className="font-mono text-xs uppercase tracking-wider font-semibold">
          {data.label}
        </span>
        {data.score > 0 && (
          <div className={`text-lg font-bold ${
            data.score >= 99 ? 'text-emerald-400' : 
            data.score >= 70 ? 'text-amber-400' : 'text-red-400'
          }`}>
            {data.score.toFixed(1)}%
          </div>
        )}
        {data.iterations && (
          <div className="text-[10px] text-zinc-500">
            {data.iterations} iterations
          </div>
        )}
        
        {/* Processing indicator */}
        {isProcessing && (
          <div className="text-[10px] text-indigo-300 font-mono animate-pulse">
            Processing...
          </div>
        )}
        
        {/* Run button - only show if stage is pending or active and not processing */}
        {(status === 'pending' || status === 'active') && data.onRunStage && !isProcessing && (
          <button
            onClick={handleRunStage}
            className="mt-1 flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-mono uppercase bg-emerald-500/20 hover:bg-emerald-500/40 border border-emerald-500/50 rounded-lg text-emerald-300 transition-all hover:scale-105"
            data-testid={`run-stage-${data.stage}`}
          >
            <Play size={12} />
            Run
          </button>
        )}
      </div>
    </div>
    </div>
  );
});

StageNode.displayName = 'StageNode';
export default StageNode;
