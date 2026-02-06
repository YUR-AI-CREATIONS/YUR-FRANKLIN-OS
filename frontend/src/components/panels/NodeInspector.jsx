import React from 'react';
import { X, Terminal, AlertTriangle, CheckCircle2, FileCode2, Cpu } from 'lucide-react';

const typeIcons = {
  input: Terminal,
  ambiguity: AlertTriangle,
  resolution: CheckCircle2,
  spec: FileCode2,
  processing: Cpu
};

const typeColors = {
  input: 'text-indigo-400',
  ambiguity: 'text-amber-400',
  resolution: 'text-emerald-400',
  spec: 'text-indigo-400',
  processing: 'text-zinc-400'
};

export const NodeInspector = ({ node, onClose }) => {
  if (!node) return null;

  const Icon = typeIcons[node.type] || Cpu;
  const colorClass = typeColors[node.type] || 'text-zinc-400';

  return (
    <div className="node-inspector glass-panel rounded-lg animate-fade-in" data-testid="node-inspector-panel">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Icon size={16} className={colorClass} />
            <span className={`font-mono text-sm font-bold uppercase tracking-wider ${colorClass}`}>
              {node.type} Node
            </span>
          </div>
          <button
            onClick={onClose}
            className="w-6 h-6 flex items-center justify-center rounded hover:bg-zinc-800 text-zinc-500 hover:text-zinc-300 transition-colors"
            data-testid="close-inspector-btn"
          >
            <X size={14} />
          </button>
        </div>

        {/* Node ID */}
        <div className="mb-4 p-2 bg-zinc-950 rounded border border-zinc-800">
          <span className="text-[10px] text-zinc-500 font-mono uppercase">Node ID</span>
          <div className="text-xs text-zinc-300 font-mono mt-1">{node.id}</div>
        </div>

        {/* Node Data */}
        <div className="space-y-3">
          {node.data && Object.entries(node.data).map(([key, value]) => (
            <DataRow key={key} label={key} value={value} />
          ))}
        </div>

        {/* Position */}
        <div className="mt-4 pt-4 border-t border-zinc-800">
          <span className="text-[10px] text-zinc-500 font-mono uppercase">Position</span>
          <div className="text-xs text-zinc-400 font-mono mt-1">
            x: {node.position?.x?.toFixed(0)} • y: {node.position?.y?.toFixed(0)}
          </div>
        </div>
      </div>
    </div>
  );
};

const DataRow = ({ label, value }) => {
  const formatValue = (val) => {
    if (val === null || val === undefined) return 'null';
    if (typeof val === 'boolean') return val ? 'true' : 'false';
    if (typeof val === 'object') return JSON.stringify(val, null, 2);
    if (typeof val === 'string' && val.length > 200) return val.substring(0, 200) + '...';
    return String(val);
  };

  const isObject = typeof value === 'object' && value !== null;

  return (
    <div className="p-2 bg-zinc-900/50 rounded">
      <span className="text-[10px] text-zinc-500 font-mono uppercase">{label}</span>
      <div className={`mt-1 text-sm ${
        isObject ? 'font-mono text-xs text-zinc-400 whitespace-pre-wrap max-h-[150px] overflow-y-auto' : 'text-zinc-300'
      }`}>
        {formatValue(value)}
      </div>
    </div>
  );
};

export default NodeInspector;
