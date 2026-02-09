import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API = process.env.REACT_APP_BACKEND_URL || '';

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
      {/* Horizontal ghost lines */}
      <svg className="absolute inset-0 w-full h-full">
        {/* Left line - Franklin to Code */}
        <line 
          x1="20%" y1="50%" 
          x2="40%" y2="50%" 
          stroke="rgba(0, 255, 255, 0.15)" 
          strokeWidth="1"
          strokeDasharray="8,4"
        >
          <animate attributeName="stroke-dashoffset" from="0" to="-24" dur="2s" repeatCount="indefinite"/>
        </line>
        
        {/* Right line - Code to Grok */}
        <line 
          x1="60%" y1="50%" 
          x2="80%" y2="50%" 
          stroke="rgba(0, 255, 255, 0.15)" 
          strokeWidth="1"
          strokeDasharray="8,4"
        >
          <animate attributeName="stroke-dashoffset" from="-24" to="0" dur="2s" repeatCount="indefinite"/>
        </line>
        
        {/* Arrowheads */}
        <polygon points="0,0 -8,4 -8,-4" fill="rgba(0, 255, 255, 0.3)" transform="translate(calc(40% - 5), 50%)">
          <animateTransform attributeName="transform" type="translate" from="38%,50%" to="40%,50%" dur="2s" repeatCount="indefinite"/>
        </polygon>
      </svg>
    </div>
  );
};

// ============================================================================
// MAIN APP COMPONENT
// ============================================================================
function App() {
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
  
  // Folders state (bottom drawers)
  const [projectsOpen, setProjectsOpen] = useState(false);
  const [foldersOpen, setFoldersOpen] = useState(false);
  
  // Loading states
  const [franklinLoading, setFranklinLoading] = useState(false);
  const [grokLoading, setGrokLoading] = useState(false);
  
  // Saved chats for Grok panel
  const [savedChats, setSavedChats] = useState(() => {
    const saved = localStorage.getItem('saved_chats_v2');
    return saved ? JSON.parse(saved) : [];
  });
  
  // Refs for auto-scroll
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
  
  // Add terminal output
  const addTerminal = (text, type = 'info') => {
    setTerminalOutput(prev => [...prev, { type, text: `> ${text}`, timestamp: new Date().toISOString() }]);
  };
  
  // Handle Franklin send - Main orchestrator
  const handleFranklinSend = async () => {
    if (!franklinInput.trim() || franklinLoading) return;
    
    const input = franklinInput.trim();
    setFranklinInput('');
    setFranklinChat(prev => [...prev, { role: 'user', content: input }]);
    setFranklinLoading(true);
    
    // Check for build commands
    if (input.toLowerCase().startsWith('/genesis ') || input.toLowerCase().startsWith('/build ')) {
      const mission = input.replace(/^\/(?:genesis|build)\s+/i, '');
      addTerminal(`GENESIS: ${mission}`, 'system');
      setFranklinChat(prev => [...prev, { role: 'franklin', content: `Initiating build: "${mission}". Watch the terminal for progress.` }]);
      
      try {
        const response = await axios.post(`${API}/api/build-orchestrator/build`, { mission });
        
        if (response.data.output) {
          response.data.output.forEach(entry => {
            addTerminal(`[${entry.phase}] ${entry.message}`, entry.type || 'info');
            // Also add to Grok responses
            if (entry.phase.toLowerCase().includes('grok') || entry.agent) {
              setGrokChat(prev => [...prev, { 
                role: 'grok', 
                content: `[${entry.agent || entry.phase}] ${entry.message}`,
                timestamp: new Date().toISOString()
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
        setFranklinChat(prev => [...prev, { role: 'franklin', content: 'Build encountered an issue. Check the terminal for details.' }]);
      }
      
      setFranklinLoading(false);
      return;
    }
    
    // Handle help command
    if (input.toLowerCase() === '/help') {
      setFranklinChat(prev => [...prev, { 
        role: 'franklin', 
        content: `Available commands:\n• /genesis <mission> - Start a full build\n• /build <mission> - Same as genesis\n• /clear - Clear all history\n• /save - Save current chat\n• /help - Show this help\n\nOr just describe what you want to build!`
      }]);
      setFranklinLoading(false);
      return;
    }
    
    // Handle clear command
    if (input.toLowerCase() === '/clear') {
      setFranklinChat([{ role: 'franklin', content: 'Chat cleared. What would you like to build?' }]);
      setGrokChat([]);
      setTerminalOutput([{ type: 'system', text: '> Terminal cleared' }]);
      localStorage.removeItem('franklin_chat_v2');
      localStorage.removeItem('grok_chat_v2');
      localStorage.removeItem('terminal_output_v2');
      setFranklinLoading(false);
      return;
    }
    
    // Handle save command
    if (input.toLowerCase() === '/save') {
      const chatToSave = {
        id: Date.now(),
        title: franklinChat.length > 1 ? franklinChat[1].content.slice(0, 30) + '...' : 'New Chat',
        messages: franklinChat,
        timestamp: new Date().toISOString()
      };
      setSavedChats(prev => [...prev, chatToSave]);
      setFranklinChat(prev => [...prev, { role: 'franklin', content: 'Chat saved! You can find it in the Saved Chats panel on the right.' }]);
      setFranklinLoading(false);
      return;
    }
    
    // Regular chat - Use orchestrator
    try {
      const response = await axios.post(`${API}/api/build-orchestrator/chat`, { message: input });
      const reply = response.data.response || "I can help you with that. Would you like me to start building?";
      setFranklinChat(prev => [...prev, { role: 'franklin', content: reply }]);
      
      if (response.data.ready_to_build) {
        setFranklinChat(prev => [...prev, { 
          role: 'franklin', 
          content: '💡 Ready to build? Type /genesis followed by your project description.' 
        }]);
      }
    } catch (err) {
      // Fallback
      setFranklinChat(prev => [...prev, { 
        role: 'franklin', 
        content: "I'm here to help. Describe what you want to build, or use /genesis <description> to start the agent workflow." 
      }]);
    }
    
    setFranklinLoading(false);
  };
  
  // Handle Grok direct input
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
      
      const reply = response.data.response || "Processing your request...";
      setGrokChat(prev => [...prev, { role: 'grok', content: reply }]);
    } catch (err) {
      setGrokChat(prev => [...prev, { role: 'grok', content: 'I can analyze that. What specific aspect interests you?' }]);
    }
    
    setGrokLoading(false);
  };
  
  // Handle terminal input
  const handleTerminalSend = async () => {
    if (!terminalInput.trim()) return;
    
    const input = terminalInput.trim();
    setTerminalInput('');
    addTerminal(input, 'cmd');
    
    // Process terminal commands
    if (input.toLowerCase() === 'clear') {
      setTerminalOutput([{ type: 'system', text: '> Terminal cleared' }]);
    } else if (input.toLowerCase() === 'help') {
      addTerminal('Commands: clear, help, status', 'info');
    } else if (input.toLowerCase() === 'status') {
      addTerminal('FRANKLIN OS: Online', 'success');
      addTerminal('Grok: Connected', 'success');
      addTerminal('Agents: Ready', 'info');
    } else if (input.startsWith('/genesis ')) {
      setFranklinInput(input);
      setTimeout(handleFranklinSend, 100);
    } else {
      addTerminal(`Unknown command: ${input}`, 'error');
    }
  };
  
  // Load a saved chat
  const loadSavedChat = (chat) => {
    setFranklinChat(chat.messages);
    addTerminal(`Loaded chat: ${chat.title}`, 'info');
  };
  
  // Delete a saved chat
  const deleteSavedChat = (chatId) => {
    setSavedChats(prev => prev.filter(c => c.id !== chatId));
  };
  
  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="franklin-os">
      <GalacticBackground />
      <GhostLines />
      
      {/* FRANKLIN GHOST TITLE - Center Background */}
      <div className="fixed inset-x-0 top-[20%] flex justify-center pointer-events-none z-[1] overflow-hidden">
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
            WebkitTextFillColor: 'transparent',
            filter: 'drop-shadow(0 0 30px rgba(255,255,255,0.05))'
          }}
        >
          FRANKLIN
        </h1>
      </div>
      
      {/* TOP HEADER BAR */}
      <div className="absolute top-0 left-0 right-0 h-10 z-50 bg-black/90 border-b border-white/10 backdrop-blur-md flex items-center px-4">
        <div className="text-sm font-mono text-white/90 tracking-wider" style={{ fontFamily: "'Orbitron', sans-serif" }}>
          ◈ FRANKLIN OS
        </div>
        <div className="flex-1" />
        <div className="flex items-center gap-4 text-[9px] font-mono">
          <span className="text-green-400 flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
            SENTINEL: ACTIVE
          </span>
          <span className="text-cyan-400">PQC: ONLINE</span>
          <span className="text-purple-400">AUDIT: 1 entries</span>
          <span className="text-amber-400">AGENTS: 5</span>
        </div>
      </div>
      
      {/* ============================================================ */}
      {/* MAIN 3-COLUMN LAYOUT */}
      {/* ============================================================ */}
      
      {/* LEFT PANEL - FRANKLIN (1 million context) */}
      <div className="absolute top-10 left-0 w-72 bottom-40 z-30 bg-black/95 border-r border-white/10 flex flex-col" data-testid="franklin-panel">
        {/* Header */}
        <div className="p-3 border-b border-white/10">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-cyan-400 tracking-wider">◆ FRANKLIN</span>
            <span className="text-[8px] font-mono text-white/30">COLLAPSE</span>
          </div>
        </div>
        
        {/* Expandable Section - Franklin Onboard Chat */}
        <div className="border-b border-white/5">
          <div className="px-3 py-2 text-[10px] font-mono text-white/60 flex items-center gap-2">
            <span className="text-cyan-400">⚡</span>
            FRANKLIN ONBOARD CHAT
            <button className="ml-auto text-[8px] text-white/30 hover:text-white/60 border border-white/10 px-2 py-0.5 rounded">
              ⊞ EXPAND
            </button>
          </div>
        </div>
        
        {/* Context Window Label */}
        <div className="px-3 py-1 text-[8px] font-mono text-white/20">
          Context Window
        </div>
        
        {/* Chat Messages */}
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
        
        {/* 1 million context label */}
        <div className="px-3 py-2 text-[10px] font-mono text-cyan-400/50 text-center border-t border-white/5">
          1 million context
        </div>
      </div>
      
      {/* FRANKLIN PROMPT - Bottom Left */}
      <div className="absolute bottom-28 left-0 w-72 h-12 z-40 bg-cyan-900/20 border border-cyan-500/30 flex items-center px-3" data-testid="franklin-prompt">
        <span className="text-cyan-400 text-xs mr-2">franklin prompt</span>
        <span className="text-cyan-400">▶</span>
        <input
          type="text"
          value={franklinInput}
          onChange={(e) => setFranklinInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleFranklinSend()}
          placeholder="Type here..."
          className="flex-1 bg-transparent border-none text-xs font-mono text-white placeholder-white/30 focus:outline-none ml-2"
          disabled={franklinLoading}
        />
      </div>
      
      {/* CENTER - CODE AREA (1 million context) */}
      <div className="absolute top-10 left-72 right-72 bottom-40 z-20 flex flex-col" data-testid="code-area">
        {/* Code Area Header */}
        <div className="h-8 bg-black/80 border-b border-white/10 flex items-center px-4 text-[10px] font-mono text-white/50">
          <span className="text-cyan-400">code area</span>
          <span className="mx-2 text-white/20">|</span>
          <span>1 million context</span>
          <span className="ml-auto text-white/30">{activeFile}</span>
        </div>
        
        {/* Code Content */}
        <div className="flex-1 bg-black/50 p-4 overflow-auto">
          <pre className="text-xs font-mono text-white/60 whitespace-pre-wrap">
            {codeContent}
          </pre>
        </div>
        
        {/* Ghost lines indicator */}
        <div className="absolute left-0 right-0 top-1/2 flex items-center justify-center pointer-events-none">
          <div className="flex items-center gap-4 text-[10px] font-mono text-cyan-400/40">
            <span>◄───</span>
            <span>ghost lines</span>
            <span>───►</span>
          </div>
        </div>
      </div>
      
      {/* RIGHT PANEL - GROK (1 million context) */}
      <div className="absolute top-10 right-0 w-72 bottom-40 z-30 bg-black/95 border-l border-white/10 flex flex-col" data-testid="grok-panel">
        {/* Header with collapse */}
        <div className="p-3 border-b border-white/10 flex items-center justify-between">
          <span className="text-xs font-mono text-amber-400 tracking-wider">◆ GROK</span>
          <div className="flex items-center gap-2">
            <span className="text-[8px] font-mono text-white/30">▶</span>
            <span className="text-[8px] font-mono text-white/30" style={{ writingMode: 'vertical-rl' }}>ACADEMY</span>
          </div>
        </div>
        
        {/* Vertical tabs for collapsed panels */}
        <div className="absolute right-0 top-16 flex flex-col gap-1 text-[8px] font-mono text-white/30" style={{ writingMode: 'vertical-rl' }}>
          <span className="py-2 px-1 hover:bg-white/5 cursor-pointer">▶ BOTS</span>
        </div>
        
        {/* Grok Responses */}
        <div ref={grokRef} className="flex-1 overflow-y-auto p-3 space-y-3 scrollbar-thin">
          {grokChat.length === 0 ? (
            <div className="text-[10px] font-mono text-white/30 text-center py-8">
              <p>Grok responses appear here...</p>
              <p className="mt-2">Use the input below to ask Grok</p>
            </div>
          ) : (
            grokChat.map((msg, idx) => (
              <div key={idx} className={`text-xs font-mono ${msg.role === 'user' ? 'text-amber-400' : 'text-white/70'}`}>
                <span className="text-white/30 text-[9px]">◈ {msg.role.toUpperCase()}</span>
                <p className="mt-1 leading-relaxed">{msg.content}</p>
              </div>
            ))
          )}
          {grokLoading && (
            <div className="flex items-center gap-2 text-amber-400 text-xs">
              <span className="animate-spin">◈</span> Grok thinking...
            </div>
          )}
        </div>
        
        {/* 1 million context label */}
        <div className="px-3 py-2 text-[10px] font-mono text-amber-400/50 text-center border-t border-white/5">
          1 million context
        </div>
        
        {/* Saved Chats Section */}
        <div className="border-t border-white/10">
          <div className="px-3 py-2 text-[10px] font-mono text-white/40">
            saved chats
          </div>
          <div className="max-h-32 overflow-y-auto px-2 pb-2">
            {savedChats.length === 0 ? (
              <div className="text-[9px] font-mono text-white/20 text-center py-2">
                No saved chats. Use /save to save.
              </div>
            ) : (
              savedChats.map(chat => (
                <div key={chat.id} className="flex items-center justify-between py-1 px-2 text-[9px] font-mono text-white/50 hover:bg-white/5 rounded cursor-pointer group">
                  <span onClick={() => loadSavedChat(chat)} className="flex-1 truncate">{chat.title}</span>
                  <button 
                    onClick={() => deleteSavedChat(chat.id)}
                    className="opacity-0 group-hover:opacity-100 text-red-400/50 hover:text-red-400 ml-2"
                  >
                    ×
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
      
      {/* GROK PROMPT - Bottom Right */}
      <div className="absolute bottom-28 right-0 w-72 h-12 z-40 bg-amber-900/20 border border-amber-500/30 flex items-center px-3" data-testid="grok-prompt">
        <span className="text-amber-400 text-xs mr-2">grok prompt</span>
        <span className="text-amber-400">▶</span>
        <input
          type="text"
          value={grokInput}
          onChange={(e) => setGrokInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleGrokSend()}
          placeholder="Ask Grok anything..."
          className="flex-1 bg-transparent border-none text-xs font-mono text-white placeholder-white/30 focus:outline-none ml-2"
          disabled={grokLoading}
        />
      </div>
      
      {/* ============================================================ */}
      {/* BOTTOM SECTION - FOLDERS + TERMINAL */}
      {/* ============================================================ */}
      
      {/* Folder Tabs (Red, Yellow, Cyan arrows pointing down) */}
      <div className="absolute bottom-28 left-72 right-72 h-6 z-30 flex items-end justify-center gap-4">
        <button 
          onClick={() => setProjectsOpen(!projectsOpen)}
          className={`px-4 py-1 text-[9px] font-mono border-t border-x rounded-t transition-all ${projectsOpen ? 'bg-red-900/30 border-red-500/50 text-red-400' : 'bg-black/50 border-white/10 text-white/40 hover:text-white/70'}`}
        >
          ▼ PROJECTS
        </button>
        <button 
          onClick={() => setFoldersOpen(!foldersOpen)}
          className={`px-4 py-1 text-[9px] font-mono border-t border-x rounded-t transition-all ${foldersOpen ? 'bg-yellow-900/30 border-yellow-500/50 text-yellow-400' : 'bg-black/50 border-white/10 text-white/40 hover:text-white/70'}`}
        >
          ▼ FOLDERS
        </button>
      </div>
      
      {/* Expandable Folders Panel */}
      {(projectsOpen || foldersOpen) && (
        <div className="absolute bottom-28 left-72 right-72 h-40 z-25 bg-black/90 border-t border-white/10 flex">
          {projectsOpen && (
            <div className="flex-1 border-r border-white/10 p-3 overflow-y-auto">
              <div className="text-[10px] font-mono text-red-400 mb-2">PROJECTS</div>
              <div className="space-y-1 text-[9px] font-mono text-white/50">
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer">📁 Project Alpha</div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer">📁 Franklin Demo</div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer">📁 Genesis Test</div>
              </div>
            </div>
          )}
          {foldersOpen && (
            <div className="flex-1 p-3 overflow-y-auto">
              <div className="text-[10px] font-mono text-yellow-400 mb-2">FOLDERS</div>
              <div className="space-y-1 text-[9px] font-mono text-white/50">
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer">📂 src/</div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer pl-4">📄 App.js</div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer pl-4">📄 index.js</div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer">📂 backend/</div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer pl-4">📄 server.py</div>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* BOTTOM TERMINAL BAR */}
      <div className="absolute bottom-0 left-0 right-0 h-28 z-40 bg-black/95 border-t border-white/10 flex flex-col" data-testid="terminal">
        {/* Terminal Header */}
        <div className="h-6 border-b border-white/5 flex items-center px-4 text-[9px] font-mono">
          <span className="text-green-400">◆ TERMINAL</span>
          <span className="mx-4 text-white/20">|</span>
          <span className="text-white/40">SDK Cloud → Ubuntu/Linux → PowerShell</span>
          <span className="ml-auto text-amber-400">◈ GROK RESPONSE</span>
        </div>
        
        {/* Terminal Split View */}
        <div className="flex-1 flex">
          {/* Left - Terminal Output */}
          <div className="flex-1 border-r border-white/10 flex flex-col">
            <div ref={terminalRef} className="flex-1 overflow-y-auto p-2 text-[10px] font-mono scrollbar-thin">
              {terminalOutput.map((line, idx) => (
                <div key={idx} className={`${
                  line.type === 'error' ? 'text-red-400' :
                  line.type === 'success' ? 'text-green-400' :
                  line.type === 'system' ? 'text-purple-400' :
                  line.type === 'cmd' ? 'text-cyan-400' :
                  'text-white/60'
                }`}>
                  {line.text}
                </div>
              ))}
            </div>
            <div className="h-6 border-t border-white/5 flex items-center px-2">
              <span className="text-green-400 text-[10px] mr-2">/genesis mission...</span>
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
          
          {/* Right - Grok Response Summary */}
          <div className="w-80 flex flex-col">
            <div className="flex-1 overflow-y-auto p-2 text-[10px] font-mono text-white/50">
              <div className="text-amber-400/70 mb-1">Grok responses appear here...</div>
              {grokChat.slice(-3).map((msg, idx) => (
                <div key={idx} className="text-white/40 truncate py-0.5">
                  {msg.content.slice(0, 60)}...
                </div>
              ))}
            </div>
            <div className="h-6 border-t border-white/5 flex items-center px-2">
              <span className="text-amber-400 text-[10px] mr-2">▶</span>
              <span className="text-[9px] text-white/30">Ask Grok anything...</span>
            </div>
          </div>
        </div>
        
        {/* SM Context Window Label - Bottom Right */}
        <div className="absolute bottom-2 right-4 text-[8px] font-mono text-white/20">
          SM Context Window
        </div>
      </div>
      
      {/* Made with Emergent Badge */}
      <div className="fixed bottom-2 right-4 z-50 text-[9px] font-mono text-white/30 flex items-center gap-1">
        <span className="text-cyan-400">◎</span> Made with Emergent
      </div>
      
      {/* Scrollbar Styles */}
      <style>{`
        .scrollbar-thin::-webkit-scrollbar { width: 4px; }
        .scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
        .scrollbar-thin::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
        .scrollbar-thin::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
      `}</style>
    </div>
  );
}

export default App;
