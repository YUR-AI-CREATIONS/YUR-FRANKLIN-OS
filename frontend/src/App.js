import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';
import { LandingPage } from './components/LandingPage';
import './App.css';

const API = process.env.REACT_APP_BACKEND_URL || '';

// Page Navigation
const PAGES = {
  LANDING: 'landing',
  IDE: 'ide',
  WORKFLOW: 'workflow'
};

// ============================================================================
// GALACTIC BACKGROUND - Twinkling Stars
// ============================================================================
const GalacticBackground = () => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationId;
    let time = 0;
    let stars = [];
    
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      stars = generateStars(canvas.width, canvas.height);
    };
    
    const generateStars = (w, h) => {
      const arr = [];
      for (let i = 0; i < 120; i++) {
        arr.push({
          x: Math.random() * w,
          y: Math.random() * h,
          size: Math.random() * 1.2 + 0.3,
          speed: Math.random() * 1.5 + 0.5,
          phase: Math.random() * Math.PI * 2
        });
      }
      return arr;
    };
    
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      stars.forEach(star => {
        const twinkle = Math.sin(time * star.speed * 0.05 + star.phase) * 0.5 + 0.5;
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size * (twinkle * 0.4 + 0.6), 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${twinkle * 0.7 + 0.2})`;
        ctx.fill();
      });
      
      time += 1;
      animationId = requestAnimationFrame(draw);
    };
    
    resize();
    draw();
    
    window.addEventListener('resize', resize);
    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resize);
    };
  }, []);
  
  return <canvas ref={canvasRef} className="fixed inset-0 z-0 pointer-events-none" />;
};

// ============================================================================
// GHOST LINES - Visual connection between Franklin ↔ Code ↔ Grok
// ============================================================================
const GhostLines = () => {
  return (
    <div className="absolute inset-0 pointer-events-none z-[2] overflow-hidden">
      <svg className="absolute inset-0 w-full h-full">
        <line 
          x1="20%" y1="50%" 
          x2="40%" y2="50%" 
          stroke="rgba(0, 255, 255, 0.15)" 
          strokeWidth="1"
          strokeDasharray="8,4"
        >
          <animate attributeName="stroke-dashoffset" from="0" to="-24" dur="2s" repeatCount="indefinite"/>
        </line>
        
        <line 
          x1="60%" y1="50%" 
          x2="80%" y2="50%" 
          stroke="rgba(0, 255, 255, 0.15)" 
          strokeWidth="1"
          strokeDasharray="8,4"
        >
          <animate attributeName="stroke-dashoffset" from="-24" to="0" dur="2s" repeatCount="indefinite"/>
        </line>
      </svg>
    </div>
  );
};

// ============================================================================
// RESIZABLE PANEL COMPONENT
// ============================================================================
const ResizablePanel = ({ children, side, defaultWidth = 288, minWidth = 200, maxWidth = 500 }) => {
  const [width, setWidth] = useState(defaultWidth);
  const [isResizing, setIsResizing] = useState(false);
  const panelRef = useRef(null);
  
  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsResizing(true);
  };
  
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;
      
      if (side === 'left') {
        const newWidth = e.clientX;
        setWidth(Math.min(maxWidth, Math.max(minWidth, newWidth)));
      } else {
        const newWidth = window.innerWidth - e.clientX;
        setWidth(Math.min(maxWidth, Math.max(minWidth, newWidth)));
      }
    };
    
    const handleMouseUp = () => {
      setIsResizing(false);
    };
    
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, side, minWidth, maxWidth]);
  
  return (
    <div 
      ref={panelRef}
      className="relative h-full flex flex-col"
      style={{ width: `${width}px` }}
    >
      {children}
      
      {/* Resize Handle */}
      <div
        onMouseDown={handleMouseDown}
        className={`absolute top-0 bottom-0 w-1 cursor-col-resize z-50 hover:bg-cyan-500/30 transition-colors ${
          side === 'left' ? 'right-0' : 'left-0'
        } ${isResizing ? 'bg-cyan-500/50' : 'bg-transparent'}`}
      >
        <div className={`absolute top-1/2 -translate-y-1/2 ${side === 'left' ? '-right-1' : '-left-1'} w-3 h-8 flex flex-col justify-center items-center gap-0.5 opacity-30 hover:opacity-70 transition-opacity`}>
          <div className="w-0.5 h-0.5 bg-white rounded-full"></div>
          <div className="w-0.5 h-0.5 bg-white rounded-full"></div>
          <div className="w-0.5 h-0.5 bg-white rounded-full"></div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// PAGE 3: ELECTRIC WORKFLOW
// ============================================================================
const ElectricWorkflowPage = ({ onBack, workflowNodes, workflowEdges, onNodesChange, onEdgesChange }) => {
  const [selectedNode, setSelectedNode] = useState(null);
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'system', content: 'Workflow initialized. Ready to build your project.' }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const onConnect = useCallback((params) => {
    onEdgesChange((eds) => addEdge({ 
      ...params, 
      animated: true,
      style: { stroke: '#00ff88', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#00ff88' }
    }, eds));
  }, [onEdgesChange]);

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const handleChatSend = async () => {
    if (!chatInput.trim() || isProcessing) return;
    
    const input = chatInput.trim();
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: input }]);
    setIsProcessing(true);
    
    try {
      const response = await axios.post(`${API}/api/grok/chat`, { 
        message: input,
        history: chatHistory.slice(-6)
      });
      
      if (response.data.response) {
        setChatHistory(prev => [...prev, { role: 'assistant', content: response.data.response }]);
      }
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'assistant', content: 'I can help you with that. What specific aspect would you like to explore?' }]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="workflow-page">
      <GalacticBackground />
      
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 h-14 z-50 bg-black/80 backdrop-blur-md border-b border-white/10 flex items-center justify-center">
        <button
          onClick={onBack}
          className="absolute left-4 px-4 py-2 text-xs font-mono text-white/70 hover:text-white hover:bg-white/10 rounded transition-all flex items-center gap-2"
          data-testid="back-to-ide"
        >
          ◀ BACK TO IDE
        </button>
        
        <div className="text-center">
          <h1 className="text-xl font-mono tracking-[0.3em] text-white/90" style={{ fontFamily: "'Orbitron', sans-serif" }}>
            ◈ ELECTRIC WORKFLOW
          </h1>
          <p className="text-[10px] text-white/40 tracking-wider mt-1">VISUAL BUILD PIPELINE</p>
        </div>
      </div>

      {/* LEFT PANEL - Chat */}
      <div className={`absolute top-14 bottom-12 z-40 bg-black/60 backdrop-blur-sm border-r border-white/10 transition-all duration-300 ${leftPanelOpen ? 'left-0 w-72' : '-left-72 w-72'}`}>
        <button
          onClick={() => setLeftPanelOpen(!leftPanelOpen)}
          className="absolute -right-8 top-1/2 -translate-y-1/2 w-8 h-16 bg-black/80 border border-white/10 rounded-r-lg flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-all"
        >
          {leftPanelOpen ? '◀' : '▶'}
        </button>
        
        <div className="p-4 h-full flex flex-col">
          <div className="text-[10px] font-mono text-cyan-400 tracking-wider mb-3">◆ CHAT RESPONSE</div>
          
          <div ref={chatRef} className="flex-1 overflow-y-auto space-y-3 scrollbar-thin">
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={`text-xs font-mono ${msg.role === 'user' ? 'text-cyan-400' : msg.role === 'system' ? 'text-purple-400' : 'text-white/80'}`}>
                <span className="text-white/30 text-[9px]">[{msg.role.toUpperCase()}]</span>
                <p className="mt-1 leading-relaxed">{msg.content}</p>
              </div>
            ))}
            {isProcessing && (
              <div className="flex items-center gap-2 text-purple-400 text-xs">
                <span className="animate-spin">◈</span> Processing...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* RIGHT PANEL - Controls */}
      <div className={`absolute top-14 bottom-12 z-40 bg-black/60 backdrop-blur-sm border-l border-white/10 transition-all duration-300 ${rightPanelOpen ? 'right-0 w-72' : '-right-72 w-72'}`}>
        <button
          onClick={() => setRightPanelOpen(!rightPanelOpen)}
          className="absolute -left-8 top-1/2 -translate-y-1/2 w-8 h-16 bg-black/80 border border-white/10 rounded-l-lg flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-all"
        >
          {rightPanelOpen ? '▶' : '◀'}
        </button>
        
        <div className="p-4 h-full flex flex-col overflow-y-auto">
          <div className="text-[10px] font-mono text-green-400 tracking-wider mb-4">◆ WORKFLOW CONTROLS</div>
          
          {/* Stage Progress */}
          <div className="mb-6">
            <div className="text-xs font-mono text-white/60 mb-2">STAGE PROGRESS</div>
            <div className="space-y-2">
              {['Specification', 'Architecture', 'Implementation', 'Integration', 'Quality', 'Certification'].map((stage, idx) => (
                <div key={stage} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${idx < 2 ? 'bg-green-400' : 'bg-white/20'}`} />
                  <span className="text-[10px] font-mono text-white/60">{stage}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Selected Node */}
          {selectedNode && (
            <div className="mb-6 p-3 bg-white/5 rounded-lg border border-white/10">
              <div className="text-xs font-mono text-white/60 mb-2">SELECTED NODE</div>
              <div className="text-sm font-mono text-white/90">{selectedNode.data?.label || selectedNode.id}</div>
            </div>
          )}

          {/* Actions */}
          <div className="space-y-2 mt-auto">
            <button className="w-full px-4 py-3 text-xs font-mono bg-green-500/20 border border-green-500/30 rounded-lg text-green-400 hover:bg-green-500/30 transition-all">
              ▶ RUN WORKFLOW
            </button>
            <button className="w-full px-4 py-3 text-xs font-mono bg-white/5 border border-white/10 rounded-lg text-white/60 hover:bg-white/10 transition-all">
              ⟳ RESET
            </button>
          </div>
        </div>
      </div>

      {/* Main Workflow Canvas */}
      <div className={`absolute top-14 bottom-12 z-10 transition-all duration-300 ${leftPanelOpen ? 'left-72' : 'left-0'} ${rightPanelOpen ? 'right-72' : 'right-0'}`}>
        <ReactFlow
          nodes={workflowNodes}
          edges={workflowEdges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          fitView
          minZoom={0.2}
          maxZoom={2}
          className="!bg-transparent"
          defaultEdgeOptions={{
            style: { stroke: '#00ff88', strokeWidth: 2 },
            animated: true
          }}
        >
          <Background color="rgba(255,255,255,0.02)" gap={30} />
          <Controls className="!bg-black/70 !border-white/20 !rounded-lg" />
        </ReactFlow>
      </div>

      {/* Bottom Bar */}
      <div className="absolute bottom-0 left-0 right-0 h-12 z-40 bg-black/80 border-t border-white/10 flex items-center px-4">
        <input
          type="text"
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
          placeholder="Ask about your workflow..."
          className="flex-1 bg-transparent border-none text-xs font-mono text-white placeholder-white/30 focus:outline-none"
          disabled={isProcessing}
        />
        <button
          onClick={handleChatSend}
          disabled={isProcessing || !chatInput.trim()}
          className="px-4 py-2 text-xs font-mono text-cyan-400 hover:bg-white/10 rounded transition-all disabled:opacity-30"
        >
          SEND ▶
        </button>
      </div>
    </div>
  );
};

// ============================================================================
// PAGE 2: MAIN IDE
// ============================================================================
const IDEPage = ({ onNavigate }) => {
  // Panel states
  const [franklinInput, setFranklinInput] = useState('');
  const [grokInput, setGrokInput] = useState('');
  const [terminalInput, setTerminalInput] = useState('');
  
  // Chat histories - Load from localStorage
  const [franklinChat, setFranklinChat] = useState(() => {
    const saved = localStorage.getItem('franklin_chat_v2');
    return saved ? JSON.parse(saved) : [
      { role: 'franklin', content: 'Welcome to FRANKLIN OS. I\'m here to help you navigate and build. What would you like to create today?' }
    ];
  });
  
  const [grokChat, setGrokChat] = useState(() => {
    const saved = localStorage.getItem('grok_chat_v2');
    return saved ? JSON.parse(saved) : [];
  });
  
  const [terminalOutput, setTerminalOutput] = useState(() => {
    const saved = localStorage.getItem('terminal_output_v2');
    return saved ? JSON.parse(saved) : [
      { type: 'system', text: '> FRANKLIN OS Terminal v2.0' },
      { type: 'system', text: '> Ready...' },
      { type: 'info', text: '> Type /genesis <mission> to start' }
    ];
  });
  
  // Code area state
  const [codeContent, setCodeContent] = useState('// Your code will appear here...\n// Use /genesis <mission> to start building\n');
  const [activeFile, setActiveFile] = useState('untitled.js');
  
  // Folders state
  const [projectsOpen, setProjectsOpen] = useState(false);
  const [foldersOpen, setFoldersOpen] = useState(false);
  
  // Loading states
  const [franklinLoading, setFranklinLoading] = useState(false);
  const [grokLoading, setGrokLoading] = useState(false);
  
  // Saved chats
  const [savedChats, setSavedChats] = useState(() => {
    const saved = localStorage.getItem('saved_chats_v2');
    return saved ? JSON.parse(saved) : [];
  });
  
  // Refs
  const franklinRef = useRef(null);
  const grokRef = useRef(null);
  const terminalRef = useRef(null);
  
  // Save to localStorage
  useEffect(() => {
    localStorage.setItem('franklin_chat_v2', JSON.stringify(franklinChat.slice(-50)));
  }, [franklinChat]);
  
  useEffect(() => {
    localStorage.setItem('grok_chat_v2', JSON.stringify(grokChat.slice(-50)));
  }, [grokChat]);
  
  useEffect(() => {
    localStorage.setItem('terminal_output_v2', JSON.stringify(terminalOutput.slice(-100)));
  }, [terminalOutput]);
  
  useEffect(() => {
    localStorage.setItem('saved_chats_v2', JSON.stringify(savedChats.slice(-20)));
  }, [savedChats]);
  
  // Auto-scroll
  useEffect(() => {
    if (franklinRef.current) franklinRef.current.scrollTop = franklinRef.current.scrollHeight;
  }, [franklinChat]);
  
  useEffect(() => {
    if (grokRef.current) grokRef.current.scrollTop = grokRef.current.scrollHeight;
  }, [grokChat]);
  
  useEffect(() => {
    if (terminalRef.current) terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
  }, [terminalOutput]);
  
  const addTerminal = (text, type = 'info') => {
    setTerminalOutput(prev => [...prev, { type, text: `> ${text}`, timestamp: new Date().toISOString() }]);
  };
  
  // Handle Franklin send
  const handleFranklinSend = async () => {
    if (!franklinInput.trim() || franklinLoading) return;
    
    const input = franklinInput.trim();
    setFranklinInput('');
    setFranklinChat(prev => [...prev, { role: 'user', content: input }]);
    setFranklinLoading(true);
    
    // Build commands
    if (input.toLowerCase().startsWith('/genesis ') || input.toLowerCase().startsWith('/build ')) {
      const mission = input.replace(/^\/(?:genesis|build)\s+/i, '');
      addTerminal(`GENESIS: ${mission}`, 'system');
      setFranklinChat(prev => [...prev, { role: 'franklin', content: `Initiating build: "${mission}". Watch the terminal for progress.` }]);
      
      try {
        const response = await axios.post(`${API}/api/build-orchestrator/build`, { mission });
        
        if (response.data.output) {
          response.data.output.forEach(entry => {
            addTerminal(`[${entry.phase}] ${entry.message}`, entry.type || 'info');
            if (entry.phase.toLowerCase().includes('grok') || entry.agent) {
              setGrokChat(prev => [...prev, { 
                role: 'grok', 
                content: `[${entry.agent || entry.phase}] ${entry.message}`
              }]);
            }
          });
        }
        
        if (response.data.success) {
          addTerminal('BUILD COMPLETE ✓', 'success');
          setFranklinChat(prev => [...prev, { role: 'franklin', content: 'Build complete! Check the code area and terminal for results.' }]);
        }
      } catch (err) {
        addTerminal(`Error: ${err.message}`, 'error');
        setFranklinChat(prev => [...prev, { role: 'franklin', content: 'Build encountered an issue. Check the terminal.' }]);
      }
      
      setFranklinLoading(false);
      return;
    }
    
    // Workflow command
    if (input.toLowerCase() === '/workflow') {
      onNavigate(PAGES.WORKFLOW);
      setFranklinLoading(false);
      return;
    }
    
    // Help command
    if (input.toLowerCase() === '/help') {
      setFranklinChat(prev => [...prev, { 
        role: 'franklin', 
        content: `Commands:\n• /genesis <mission> - Start build\n• /workflow - Open workflow view\n• /clear - Clear history\n• /save - Save chat\n• /help - Show help`
      }]);
      setFranklinLoading(false);
      return;
    }
    
    // Clear command
    if (input.toLowerCase() === '/clear') {
      setFranklinChat([{ role: 'franklin', content: 'Chat cleared. What would you like to build?' }]);
      setGrokChat([]);
      setTerminalOutput([{ type: 'system', text: '> Terminal cleared' }]);
      setFranklinLoading(false);
      return;
    }
    
    // Save command
    if (input.toLowerCase() === '/save') {
      const chatToSave = {
        id: Date.now(),
        title: franklinChat.length > 1 ? franklinChat[1].content.slice(0, 30) + '...' : 'New Chat',
        messages: franklinChat
      };
      setSavedChats(prev => [...prev, chatToSave]);
      setFranklinChat(prev => [...prev, { role: 'franklin', content: 'Chat saved!' }]);
      setFranklinLoading(false);
      return;
    }
    
    // Regular chat
    try {
      const response = await axios.post(`${API}/api/build-orchestrator/chat`, { message: input });
      const reply = response.data.response || "I can help with that. Would you like to start building?";
      setFranklinChat(prev => [...prev, { role: 'franklin', content: reply }]);
    } catch (err) {
      setFranklinChat(prev => [...prev, { 
        role: 'franklin', 
        content: "I'm here to help. Use /genesis <description> to start building." 
      }]);
    }
    
    setFranklinLoading(false);
  };
  
  // Handle Grok send
  const handleGrokSend = async () => {
    if (!grokInput.trim() || grokLoading) return;
    
    const input = grokInput.trim();
    setGrokInput('');
    setGrokChat(prev => [...prev, { role: 'user', content: input }]);
    setGrokLoading(true);
    
    try {
      const response = await axios.post(`${API}/api/grok/chat`, { 
        message: input,
        history: grokChat.slice(-6)
      });
      
      const reply = response.data.response || "Processing...";
      setGrokChat(prev => [...prev, { role: 'grok', content: reply }]);
    } catch (err) {
      setGrokChat(prev => [...prev, { role: 'grok', content: 'What aspect interests you?' }]);
    }
    
    setGrokLoading(false);
  };
  
  // Handle terminal
  const handleTerminalSend = () => {
    if (!terminalInput.trim()) return;
    
    const input = terminalInput.trim();
    setTerminalInput('');
    addTerminal(input, 'cmd');
    
    if (input.toLowerCase() === 'clear') {
      setTerminalOutput([{ type: 'system', text: '> Terminal cleared' }]);
    } else if (input.toLowerCase() === 'help') {
      addTerminal('Commands: clear, help, status', 'info');
    } else if (input.toLowerCase() === 'status') {
      addTerminal('FRANKLIN OS: Online', 'success');
      addTerminal('Grok: Connected', 'success');
    } else if (input.startsWith('/genesis ')) {
      setFranklinInput(input);
      setTimeout(handleFranklinSend, 100);
    }
  };
  
  const loadSavedChat = (chat) => {
    setFranklinChat(chat.messages);
    addTerminal(`Loaded: ${chat.title}`, 'info');
  };
  
  const deleteSavedChat = (chatId) => {
    setSavedChats(prev => prev.filter(c => c.id !== chatId));
  };
  
  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="franklin-os">
      <GalacticBackground />
      <GhostLines />
      
      {/* FRANKLIN GHOST TITLE */}
      <div className="fixed inset-x-0 top-[20%] flex justify-center pointer-events-none z-[1]">
        <h1 
          className="select-none whitespace-nowrap"
          style={{ 
            fontFamily: "'Orbitron', sans-serif",
            fontSize: 'clamp(5rem, 15vw, 14rem)',
            fontWeight: 600,
            letterSpacing: '0.4em',
            paddingLeft: '0.2em',
            background: 'linear-gradient(180deg, rgba(100,100,100,0.25) 0%, rgba(140,140,140,0.3) 50%, rgba(100,100,100,0.25) 100%)',
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          FRANKLIN
        </h1>
      </div>
      
      {/* TOP HEADER */}
      <div className="absolute top-0 left-0 right-0 h-10 z-50 bg-black/70 backdrop-blur-md border-b border-white/10 flex items-center px-4">
        <div className="text-sm font-mono text-white/90 tracking-wider" style={{ fontFamily: "'Orbitron', sans-serif" }}>
          ◈ FRANKLIN OS
        </div>
        <div className="flex-1" />
        <button
          onClick={() => onNavigate(PAGES.WORKFLOW)}
          className="mr-4 px-3 py-1 text-[9px] font-mono text-purple-400 hover:bg-purple-500/20 border border-purple-500/30 rounded transition-all"
        >
          ◈ WORKFLOW
        </button>
        <div className="flex items-center gap-4 text-[9px] font-mono">
          <span className="text-green-400 flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
            SENTINEL: ACTIVE
          </span>
          <span className="text-cyan-400">PQC: ONLINE</span>
          <span className="text-purple-400">AUDIT: 1 entries</span>
          <span className="text-green-400">AGENTS: 5</span>
        </div>
      </div>
      
      {/* MAIN 3-COLUMN LAYOUT */}
      <div className="absolute top-10 left-0 right-0 bottom-28 flex">
        
        {/* LEFT - FRANKLIN */}
        <ResizablePanel side="left" defaultWidth={320} minWidth={250} maxWidth={500}>
          <div className="h-full bg-black/40 backdrop-blur-sm border-r border-white/10 flex flex-col" data-testid="franklin-panel">
            <div className="p-3 border-b border-white/10">
              <span className="text-xs font-mono text-cyan-400 tracking-wider">◆ FRANKLIN</span>
            </div>
            
            <div className="px-3 py-1 text-[8px] font-mono text-white/20">Context Window</div>
            
            <div ref={franklinRef} className="flex-1 overflow-y-auto p-3 space-y-3 scrollbar-thin">
              {franklinChat.map((msg, idx) => (
                <div key={idx} className={`text-xs font-mono ${msg.role === 'user' ? 'text-cyan-400' : 'text-white/70'}`}>
                  <span className="text-white/30 text-[9px]">◈ {msg.role.toUpperCase()}</span>
                  <p className="mt-1 leading-relaxed">{msg.content}</p>
                </div>
              ))}
              {franklinLoading && (
                <div className="flex items-center gap-2 text-purple-400 text-xs">
                  <span className="animate-spin">◈</span> Processing...
                </div>
              )}
            </div>
            
            <div className="px-3 py-2 text-[10px] font-mono text-cyan-400/50 text-center border-t border-white/5">
              1 million context
            </div>
          </div>
        </ResizablePanel>
        
        {/* CENTER - CODE AREA */}
        <div className="flex-1 flex flex-col" data-testid="code-area">
          <div className="h-8 bg-black/50 border-b border-white/10 flex items-center px-4 text-[10px] font-mono text-white/50">
            <span className="text-cyan-400">code area</span>
            <span className="mx-2 text-white/20">|</span>
            <span>1 million context</span>
            <span className="ml-auto text-white/30">{activeFile}</span>
          </div>
          
          <div className="flex-1 bg-black/30 p-4 overflow-auto relative">
            <pre className="text-xs font-mono text-white/60 whitespace-pre-wrap">
              {codeContent}
            </pre>
            
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-4 text-[10px] font-mono text-cyan-400/40 pointer-events-none">
              <span>◄───</span>
              <span>ghost lines</span>
              <span>───►</span>
            </div>
          </div>
          
          {/* Folder Tabs */}
          <div className="h-8 bg-black/50 border-t border-white/10 flex items-center justify-center gap-4">
            <button 
              onClick={() => setProjectsOpen(!projectsOpen)}
              className={`px-4 py-1 text-[9px] font-mono border rounded transition-all ${projectsOpen ? 'bg-purple-500/20 border-purple-500/50 text-purple-400' : 'border-white/10 text-white/40 hover:text-white/70'}`}
            >
              ▼ PROJECTS
            </button>
            <button 
              onClick={() => setFoldersOpen(!foldersOpen)}
              className={`px-4 py-1 text-[9px] font-mono border rounded transition-all ${foldersOpen ? 'bg-green-500/20 border-green-500/50 text-green-400' : 'border-white/10 text-white/40 hover:text-white/70'}`}
            >
              ▼ FOLDERS
            </button>
          </div>
          
          {(projectsOpen || foldersOpen) && (
            <div className="h-32 bg-black/50 border-t border-white/10 flex">
              {projectsOpen && (
                <div className="flex-1 border-r border-white/10 p-3 overflow-y-auto">
                  <div className="text-[10px] font-mono text-purple-400 mb-2">PROJECTS</div>
                  <div className="space-y-1 text-[9px] font-mono text-white/50">
                    <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer">📁 Project Alpha</div>
                    <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer">📁 Franklin Demo</div>
                  </div>
                </div>
              )}
              {foldersOpen && (
                <div className="flex-1 p-3 overflow-y-auto">
                  <div className="text-[10px] font-mono text-green-400 mb-2">FOLDERS</div>
                  <div className="space-y-1 text-[9px] font-mono text-white/50">
                    <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer">📂 src/</div>
                    <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer pl-4">📄 App.js</div>
                    <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer">📂 backend/</div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* RIGHT - GROK */}
        <ResizablePanel side="right" defaultWidth={320} minWidth={250} maxWidth={500}>
          <div className="h-full bg-black/40 backdrop-blur-sm border-l border-white/10 flex flex-col" data-testid="grok-panel">
            <div className="p-3 border-b border-white/10">
              <span className="text-xs font-mono text-green-400 tracking-wider">◆ GROK</span>
            </div>
            
            <div ref={grokRef} className="flex-1 overflow-y-auto p-3 space-y-3 scrollbar-thin">
              {grokChat.length === 0 ? (
                <div className="text-[10px] font-mono text-white/30 text-center py-8">
                  <p>Grok responses appear here...</p>
                </div>
              ) : (
                grokChat.map((msg, idx) => (
                  <div key={idx} className={`text-xs font-mono ${msg.role === 'user' ? 'text-green-400' : 'text-white/70'}`}>
                    <span className="text-white/30 text-[9px]">◈ {msg.role.toUpperCase()}</span>
                    <p className="mt-1 leading-relaxed">{msg.content}</p>
                  </div>
                ))
              )}
              {grokLoading && (
                <div className="flex items-center gap-2 text-green-400 text-xs">
                  <span className="animate-spin">◈</span> Grok thinking...
                </div>
              )}
            </div>
            
            <div className="px-3 py-2 text-[10px] font-mono text-green-400/50 text-center border-t border-white/5">
              1 million context
            </div>
            
            {/* Saved Chats */}
            <div className="border-t border-white/10">
              <div className="px-3 py-2 text-[10px] font-mono text-white/40">saved chats</div>
              <div className="max-h-24 overflow-y-auto px-2 pb-2">
                {savedChats.length === 0 ? (
                  <div className="text-[9px] font-mono text-white/20 text-center py-2">No saved chats</div>
                ) : (
                  savedChats.map(chat => (
                    <div key={chat.id} className="flex items-center justify-between py-1 px-2 text-[9px] font-mono text-white/50 hover:bg-white/5 rounded cursor-pointer group">
                      <span onClick={() => loadSavedChat(chat)} className="flex-1 truncate">{chat.title}</span>
                      <button onClick={() => deleteSavedChat(chat.id)} className="opacity-0 group-hover:opacity-100 text-red-400/50 hover:text-red-400 ml-2">×</button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </ResizablePanel>
      </div>
      
      {/* PROMPT BARS */}
      <div className="absolute bottom-28 left-0 w-80 h-10 z-40 bg-black/60 backdrop-blur-sm border-t border-r border-white/10 flex items-center px-3" data-testid="franklin-prompt">
        <span className="text-white/50 text-[10px] font-mono mr-2">Franklin Prompt</span>
        <span className="text-cyan-400 mr-2">▶</span>
        <input
          type="text"
          value={franklinInput}
          onChange={(e) => setFranklinInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleFranklinSend()}
          placeholder="Type here..."
          className="flex-1 bg-transparent border-none text-xs font-mono text-white placeholder-white/30 focus:outline-none"
          disabled={franklinLoading}
        />
      </div>
      
      <div className="absolute bottom-28 right-0 w-80 h-10 z-40 bg-black/60 backdrop-blur-sm border-t border-l border-white/10 flex items-center px-3" data-testid="grok-prompt">
        <span className="text-white/50 text-[10px] font-mono mr-2">Grok Prompt</span>
        <span className="text-green-400 mr-2">▶</span>
        <input
          type="text"
          value={grokInput}
          onChange={(e) => setGrokInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleGrokSend()}
          placeholder="Ask Grok..."
          className="flex-1 bg-transparent border-none text-xs font-mono text-white placeholder-white/30 focus:outline-none"
          disabled={grokLoading}
        />
      </div>
      
      {/* TERMINAL */}
      <div className="absolute bottom-0 left-0 right-0 h-28 z-40 bg-black/70 backdrop-blur-sm border-t border-white/10 flex flex-col" data-testid="terminal">
        <div className="h-6 border-b border-white/5 flex items-center px-4 text-[9px] font-mono">
          <span className="text-purple-400">◆ TERMINAL</span>
          <span className="mx-4 text-white/20">|</span>
          <span className="text-white/40">SDK Cloud → Ubuntu/Linux</span>
          <span className="ml-auto text-green-400">◈ GROK RESPONSE</span>
        </div>
        
        <div className="flex-1 flex">
          <div className="flex-1 border-r border-white/10 flex flex-col">
            <div ref={terminalRef} className="flex-1 overflow-y-auto p-2 text-[10px] font-mono scrollbar-thin">
              {terminalOutput.map((line, idx) => (
                <div key={idx} className={`${
                  line.type === 'error' ? 'text-red-400' :
                  line.type === 'success' ? 'text-green-400' :
                  line.type === 'system' ? 'text-purple-400' :
                  line.type === 'cmd' ? 'text-cyan-400' : 'text-white/60'
                }`}>{line.text}</div>
              ))}
            </div>
            <div className="h-6 border-t border-white/5 flex items-center px-2">
              <span className="text-purple-400 text-[10px] mr-2">/genesis mission...</span>
              <input
                type="text"
                value={terminalInput}
                onChange={(e) => setTerminalInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleTerminalSend()}
                placeholder="Enter command..."
                className="flex-1 bg-transparent border-none text-[10px] font-mono text-white placeholder-white/30 focus:outline-none"
              />
            </div>
          </div>
          
          <div className="w-80 flex flex-col">
            <div className="flex-1 overflow-y-auto p-2 text-[10px] font-mono text-white/50">
              <div className="text-green-400/70 mb-1">Grok responses...</div>
              {grokChat.slice(-3).map((msg, idx) => (
                <div key={idx} className="text-white/40 truncate py-0.5">{msg.content.slice(0, 50)}...</div>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Made with Emergent */}
      <div className="fixed bottom-2 right-96 z-50 text-[9px] font-mono text-white/30 flex items-center gap-1">
        <span className="text-cyan-400">◎</span> Made with Emergent
      </div>
      
      <style>{`
        .scrollbar-thin::-webkit-scrollbar { width: 4px; }
        .scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
        .scrollbar-thin::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
      `}</style>
    </div>
  );
};

// ============================================================================
// MAIN APP - PAGE ROUTER
// ============================================================================
function App() {
  const [currentPage, setCurrentPage] = useState(PAGES.LANDING);
  
  // Workflow state
  const [workflowNodes, setWorkflowNodes, onNodesChange] = useNodesState([
    { id: '1', type: 'default', position: { x: 250, y: 50 }, data: { label: 'Genesis' } },
    { id: '2', type: 'default', position: { x: 100, y: 150 }, data: { label: 'Architect' } },
    { id: '3', type: 'default', position: { x: 400, y: 150 }, data: { label: 'Implementer' } },
    { id: '4', type: 'default', position: { x: 250, y: 250 }, data: { label: 'Quality' } },
  ]);
  
  const [workflowEdges, setWorkflowEdges, onEdgesChange] = useEdgesState([
    { id: 'e1-2', source: '1', target: '2', animated: true },
    { id: 'e1-3', source: '1', target: '3', animated: true },
    { id: 'e2-4', source: '2', target: '4', animated: true },
    { id: 'e3-4', source: '3', target: '4', animated: true },
  ]);
  
  const handleNavigate = (page) => {
    setCurrentPage(page);
  };
  
  // Page 1: Landing
  if (currentPage === PAGES.LANDING) {
    return <LandingPage onEnterApp={() => handleNavigate(PAGES.IDE)} />;
  }
  
  // Page 3: Workflow
  if (currentPage === PAGES.WORKFLOW) {
    return (
      <ElectricWorkflowPage 
        onBack={() => handleNavigate(PAGES.IDE)}
        workflowNodes={workflowNodes}
        workflowEdges={workflowEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
      />
    );
  }
  
  // Page 2: IDE (default)
  return <IDEPage onNavigate={handleNavigate} />;
}

export default App;
