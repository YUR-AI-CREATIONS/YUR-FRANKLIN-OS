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
  
  const colorClasses = {
    zinc: 'border-zinc-600 bg-zinc-900 text-zinc-400',
    indigo: 'border-indigo-500 bg-indigo-500/10 text-indigo-300',
    emerald: 'border-emerald-500 bg-emerald-500/10 text-emerald-300',
    red: 'border-red-500 bg-red-500/10 text-red-300',
    amber: 'border-amber-500 bg-amber-500/10 text-amber-300',
  };
  
  const glowClasses = {
    indigo: 'shadow-[0_0_20px_rgba(99,102,241,0.4)]',
    emerald: 'shadow-[0_0_20px_rgba(16,185,129,0.4)]',
    red: 'shadow-[0_0_20px_rgba(239,68,68,0.4)]',
    amber: 'shadow-[0_0_20px_rgba(245,158,11,0.4)]',
  };

  const handleRunStage = (e) => {
    e.stopPropagation();
    if (data.onRunStage) {
      data.onRunStage(data.stage);
    }
  };

  return (
    <div 
      className={`sgp-node px-4 py-3 rounded-lg border-2 min-w-[140px] text-center ${
        colorClasses[config.color]
      } ${config.glow ? glowClasses[config.color] || '' : ''} ${
        selected ? 'ring-2 ring-white/20' : ''
      }`}
      data-testid={`stage-node-${data.stage}`}
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
          size={20} 
          className={config.animate ? 'animate-spin' : ''} 
        />
        <span className="font-mono text-xs uppercase tracking-wider">
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
        
        {/* Simple Run button - only show if stage is pending or active */}
        {(status === 'pending' || status === 'active') && data.onRunStage && (
          <button
            onClick={handleRunStage}
            className="mt-1 flex items-center gap-1 px-2 py-1 text-[10px] font-mono uppercase bg-emerald-500/20 hover:bg-emerald-500/40 border border-emerald-500/50 rounded text-emerald-300 transition-colors"
            data-testid={`run-stage-${data.stage}`}
          >
            <Play size={10} />
            Run
          </button>
        )}
      </div>
    </div>
  );
});

StageNode.displayName = 'StageNode';
export default StageNode;
