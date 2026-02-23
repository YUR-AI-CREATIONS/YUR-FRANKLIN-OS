/**
 * ContextWindow
 * 
 * Information box component that mirrors Franklin's cognitive model.
 * Breaks complex info into compartmentalized, collapsible sections.
 * 
 * Types: connector, code, output, info, status
 */

import React from 'react';
import { ChevronDown, ChevronRight, X } from 'lucide-react';

const ContextWindow = ({
  id = `context-${Date.now()}`,
  type = 'info',           // connector, code, output, info, status
  title = 'Context',
  subtitle = null,
  children,
  onClose = null,
  collapsible = true,
  defaultOpen = true,
  badge = null,           // { text, color }
  icon = null,
  className = '',
  maxHeight = 'max-h-96',
  minHeight = 'min-h-32',
}) => {
  const [isOpen, setIsOpen] = React.useState(defaultOpen);

  const typeConfig = {
    connector: {
      accentColor: 'from-purple-500 to-purple-600',
      borderColor: 'border-purple-500/40',
      bgColor: 'bg-purple-500/5',
      textColor: 'text-purple-300',
      icon: '⚡',
    },
    code: {
      accentColor: 'from-blue-500 to-blue-600',
      borderColor: 'border-blue-500/40',
      bgColor: 'bg-blue-500/5',
      textColor: 'text-blue-300',
      icon: '<>',
    },
    output: {
      accentColor: 'from-cyan-500 to-cyan-600',
      borderColor: 'border-cyan-500/40',
      bgColor: 'bg-cyan-500/5',
      textColor: 'text-cyan-300',
      icon: '▓',
    },
    info: {
      accentColor: 'from-slate-400 to-slate-500',
      borderColor: 'border-slate-600/40',
      bgColor: 'bg-slate-500/5',
      textColor: 'text-slate-300',
      icon: 'ℹ',
    },
    status: {
      accentColor: 'from-emerald-500 to-emerald-600',
      borderColor: 'border-emerald-500/40',
      bgColor: 'bg-emerald-500/5',
      textColor: 'text-emerald-300',
      icon: '✓',
    },
  };

  const config = typeConfig[type] || typeConfig.info;

  return (
    <div
      id={id}
      className={`
        backdrop-blur-10 border rounded-lg overflow-hidden
        transition-all duration-300 animate-fade-in
        ${config.borderColor} ${config.bgColor}
        ${className}
      `}
    >
      {/* Header - Always visible */}
      <div className={`
        flex items-center justify-between px-4 py-3
        border-b ${config.borderColor}
        bg-gradient-to-r ${config.accentColor} opacity-5 hover:opacity-10 transition-opacity
        cursor-pointer
      `}
        onClick={() => collapsible && setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {/* Icon */}
          {icon ? (
            <div className={`${config.textColor} text-lg flex-shrink-0`}>
              {icon}
            </div>
          ) : (
            <div className={`${config.textColor} font-bold text-sm flex-shrink-0`}>
              {config.icon}
            </div>
          )}

          {/* Title and Subtitle */}
          <div className="min-w-0 flex-1">
            <h3 className={`text-sm font-semibold ${config.textColor} font-mono truncate`}>
              {title}
            </h3>
            {subtitle && (
              <p className="text-xs text-slate-500 truncate">
                {subtitle}
              </p>
            )}
          </div>

          {/* Badge */}
          {badge && (
            <div className={`
              px-2 py-1 rounded text-xs font-mono flex-shrink-0
              ${badge.color || 'bg-slate-700 text-slate-300'}
            `}>
              {badge.text}
            </div>
          )}
        </div>

        {/* Control Buttons */}
        <div className="flex items-center gap-1 flex-shrink-0 ml-2">
          {collapsible && (
            <>
              {isOpen ? (
                <ChevronDown className={`w-4 h-4 ${config.textColor} opacity-60`} />
              ) : (
                <ChevronRight className={`w-4 h-4 ${config.textColor} opacity-60`} />
              )}
            </>
          )}

          {onClose && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className={`
                p-1 rounded hover:bg-white/10 transition-colors
                ${config.textColor} opacity-60 hover:opacity-100
              `}
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Content - Collapsible */}
      {isOpen && (
        <div className={`${minHeight} ${maxHeight} overflow-auto`}>
          {children}
        </div>
      )}
    </div>
  );
};

export default ContextWindow;
