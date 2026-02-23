/**
 * GhostFranklin
 * 
 * Floating AI orchestrator component.
 * Shows Benjamin Franklin persona guiding the IDE experience.
 * Can be moved, minimized, or hidden.
 */

import React, { useState } from 'react';
import { X, Minimize2, Maximize2, Send } from 'lucide-react';

const GhostFranklin = ({
  isVisible = true,
  onClose = null,
  onMessage = null,
}) => {
  const [minimized, setMinimized] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [position, setPosition] = useState({ x: 20, y: 20 });
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Good morning. I perceive the genesis of your digital garden. Pray, what shall we build together?",
      timestamp: new Date(),
      isUser: false,
    }
  ]);
  const [inputValue, setInputValue] = useState('');

  const handleMouseDown = (e) => {
    if (e.target.closest('.context-window-content')) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    setPosition({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const newMessage = {
      id: messages.length + 1,
      text: inputValue,
      timestamp: new Date(),
      isUser: true,
    };

    setMessages([...messages, newMessage]);
    setInputValue('');

    if (onMessage) {
      onMessage(inputValue);
    }

    // Simulate Franklin's response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: prev.length + 1,
          text: "Your inquiry is noted. The gears of creation turn...",
          timestamp: new Date(),
          isUser: false,
        }
      ]);
    }, 1500);
  };

  if (!isVisible) return null;

  return (
    <div
      className="fixed z-[100]"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        cursor: isDragging ? 'grabbing' : 'grab',
      }}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* Container */}
      <div
        className={`
          w-96 backdrop-blur-20 border transition-all duration-300
          rounded-xl overflow-hidden select-none
          border-blue-500/40 bg-slate-900/80
          shadow-[0_0_40px_rgba(59,130,246,0.3),inset_0_1px_2px_rgba(255,255,255,0.1)]
          ${isDragging ? 'ring-2 ring-blue-500/60' : ''}
        `}
      >
        {/* Header (Draggable) */}
        <div
          onMouseDown={handleMouseDown}
          className="
            flex items-center justify-between px-4 py-3
            border-b border-blue-500/30 bg-gradient-to-r from-blue-500/10 to-purple-500/10
            hover:from-blue-500/15 hover:to-purple-500/15 transition-all
          "
        >
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-glow-pulse" />
            <h3 className="text-sm font-semibold text-blue-300 font-mono">
              Ghost Franklin
            </h3>
          </div>

          <div className="flex items-center gap-2">
            {/* Minimize Button */}
            <button
              onClick={() => setMinimized(!minimized)}
              className="
                p-1.5 rounded hover:bg-white/10 transition-colors
                text-slate-400 hover:text-slate-200
              "
            >
              {minimized ? (
                <Maximize2 className="w-4 h-4" />
              ) : (
                <Minimize2 className="w-4 h-4" />
              )}
            </button>

            {/* Close Button */}
            {onClose && (
              <button
                onClick={onClose}
                className="
                  p-1.5 rounded hover:bg-red-500/20 transition-colors
                  text-slate-400 hover:text-red-400
                "
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Messages (if not minimized) */}
        {!minimized && (
          <>
            <div className="h-64 overflow-y-auto bg-slate-800/30 p-4 space-y-3">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${msg.isUser ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`
                      px-3 py-2 rounded-lg max-w-xs text-sm font-mono text-slate-200
                      ${msg.isUser
                        ? 'bg-blue-500/20 border border-blue-500/40 text-blue-200'
                        : 'bg-purple-500/10 border border-purple-500/30 text-purple-200'
                      }
                    `}
                  >
                    {msg.text}
                  </div>
                  <span className="text-xs text-slate-600 mt-1">
                    {msg.timestamp.toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>

            {/* Input */}
            <div className="border-t border-blue-500/30 bg-slate-800/50 p-3 flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Speak to Franklin..."
                className="
                  flex-1 bg-slate-700/50 border border-slate-600/50 rounded px-3 py-2
                  text-sm text-slate-200 placeholder-slate-600
                  focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30
                  transition-all
                "
              />
              <button
                onClick={handleSendMessage}
                className="
                  p-2 rounded bg-blue-500/20 border border-blue-500/40
                  text-blue-400 hover:bg-blue-500/30 hover:text-blue-300
                  transition-all hover:shadow-[0_0_15px_rgba(59,130,246,0.4)]
                "
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </>
        )}
      </div>

      {/* Minimized State */}
      {minimized && (
        <div className="
          w-full h-10 flex items-center justify-between px-4
          backdrop-blur-20 border border-blue-500/40 rounded-lg
          bg-slate-900/80
        ">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-glow-pulse" />
            <span className="text-xs font-mono text-blue-300">Ghost Franklin</span>
          </div>
          <div className="w-2 h-2 rounded-full bg-blue-400/60" />
        </div>
      )}
    </div>
  );
};

export default GhostFranklin;
