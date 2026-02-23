/**
 * GlassPanel
 * 
 * Base component for all glassmorphism panels in Franklin IDE.
 * Provides: frosted glass background, perimeter glow, blur effect
 */

import React from 'react';

const GlassPanel = ({
  children,
  variant = 'default',  // default, blue, purple, cyan, floating
  className = '',
  title = null,
  collapsible = false,
  onToggle = null,
  isOpen = true,
  rounded = 'lg',
}) => {
  const [collapsed, setCollapsed] = React.useState(!isOpen);

  const handleToggle = () => {
    setCollapsed(!collapsed);
    if (onToggle) onToggle(!collapsed);
  };

  // Get variant styles
  const getVariantStyles = () => {
    const baseClass = 'backdrop-blur-10 border transition-all duration-300';
    
    switch (variant) {
      case 'blue':
        return `${baseClass} bg-slate-800/60 border-blue-500/30 shadow-[0_0_20px_rgba(59,130,246,0.2),inset_0_1px_2px_rgba(255,255,255,0.05)]`;
      case 'purple':
        return `${baseClass} bg-slate-800/60 border-purple-500/30 shadow-[0_0_20px_rgba(168,85,247,0.2),inset_0_1px_2px_rgba(255,255,255,0.05)]`;
      case 'cyan':
        return `${baseClass} bg-slate-800/60 border-cyan-500/30 shadow-[0_0_20px_rgba(45,212,191,0.2),inset_0_1px_2px_rgba(255,255,255,0.05)]`;
      case 'floating':
        return `${baseClass} bg-slate-900/80 border-blue-500/40 shadow-[0_0_40px_rgba(59,130,246,0.3),inset_0_1px_2px_rgba(255,255,255,0.1)]`;
      default:
        return `${baseClass} bg-slate-800/60 border-slate-700/40 shadow-[inset_0_1px_2px_rgba(255,255,255,0.05),0_8px_32px_rgba(0,0,0,0.3)]`;
    }
  };

  const roundedClass = {
    sm: 'rounded-md',
    md: 'rounded-lg',
    lg: 'rounded-xl',
  }[rounded] || 'rounded-lg';

  return (
    <div className={`${getVariantStyles()} ${roundedClass} overflow-hidden ${className}`}>
      {/* Header (if title provided) */}
      {title && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700/40">
          <h3 className="text-sm font-semibold text-slate-100 font-mono">{title}</h3>
          {collapsible && (
            <button
              onClick={handleToggle}
              className="text-slate-400 hover:text-slate-200 transition-colors"
            >
              {collapsed ? '▶' : '▼'}
            </button>
          )}
        </div>
      )}

      {/* Content */}
      {!collapsed && (
        <div className="animate-fade-in">
          {children}
        </div>
      )}

      {collapsed && title && (
        <div className="px-4 py-2 text-xs text-slate-500 italic">
          [collapsed]
        </div>
      )}
    </div>
  );
};

export default GlassPanel;
