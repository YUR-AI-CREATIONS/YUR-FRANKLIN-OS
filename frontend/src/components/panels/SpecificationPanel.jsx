import React from 'react';
import { X, FileCode2, Download, Copy, Check } from 'lucide-react';
import { useState } from 'react';

export const SpecificationPanel = ({ specification, onClose }) => {
  const [copied, setCopied] = useState(false);
  
  if (!specification) return null;

  const spec = specification.specification || {};
  const specJson = JSON.stringify(spec, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(specJson);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([specJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `specification-${specification.session_id?.substring(0, 8) || 'spec'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-8 bg-black/60 backdrop-blur-sm animate-fade-in"
      data-testid="specification-panel"
    >
      <div className="w-full max-w-4xl max-h-[90vh] glass-panel rounded-xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-zinc-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
              <FileCode2 size={20} className="text-indigo-400" />
            </div>
            <div>
              <h2 className="font-mono text-lg font-bold text-zinc-100">
                {spec.specification?.title || 'Formal Specification'}
              </h2>
              <p className="text-xs text-zinc-500 font-mono">
                Generated: {specification.generated_at ? new Date(specification.generated_at).toLocaleString() : 'N/A'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-3 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm transition-colors"
              data-testid="copy-spec-btn"
            >
              {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
              <span>{copied ? 'Copied!' : 'Copy'}</span>
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-3 py-1.5 rounded bg-indigo-500 hover:bg-indigo-600 text-white text-sm transition-colors"
              data-testid="download-spec-btn"
            >
              <Download size={14} />
              <span>Download</span>
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded hover:bg-zinc-800 text-zinc-500 hover:text-zinc-300 transition-colors"
              data-testid="close-spec-btn"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          <pre className="spec-output text-sm">
            <SyntaxHighlight json={specJson} />
          </pre>
        </div>

        {/* Footer */}
        {spec.specification?.verification_checklist && (
          <div className="p-4 border-t border-zinc-800 bg-zinc-900/50">
            <h3 className="font-mono text-xs text-emerald-400 uppercase tracking-wider mb-2">
              Verification Checklist
            </h3>
            <ul className="space-y-1">
              {spec.specification.verification_checklist.slice(0, 5).map((item, i) => (
                <li key={i} className="text-sm text-zinc-400 flex items-start gap-2">
                  <span className="text-emerald-500 mt-1">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

const SyntaxHighlight = ({ json }) => {
  // Simple syntax highlighting for JSON
  const highlighted = json
    .replace(/"([^"]+)":/g, '<span class="key">"$1"</span>:')
    .replace(/: "([^"]*)"/g, ': <span class="string">"$1"</span>')
    .replace(/: (true|false)/g, ': <span class="value">$1</span>')
    .replace(/: (\d+)/g, ': <span class="value">$1</span>');

  return <code dangerouslySetInnerHTML={{ __html: highlighted }} />;
};

export default SpecificationPanel;
