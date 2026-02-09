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
const GalacticBackground = ({ opacity = 1 }) => {
  const canvasRef = useRef(null);
  const starsRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationId;
    let time = 0;
    
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      starsRef.current = generateStars(canvas.width, canvas.height);
    };
    
    const generateStars = (w, h) => {
      const stars = [];
      for (let i = 0; i < 150; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          size: Math.random() * 1 + 0.3,
          speed: Math.random() * 1.5 + 0.5,
          phase: Math.random() * Math.PI * 2,
          type: 'regular'
        });
      }
      for (let i = 0; i < 20; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          size: Math.random() * 1.5 + 1,
          speed: Math.random() * 2 + 1,
          phase: Math.random() * Math.PI * 2,
          type: 'sparkle'
        });
      }
      for (let i = 0; i < 5; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          size: Math.random() * 2 + 1.5,
          speed: Math.random() * 2.5 + 1.5,
          phase: Math.random() * Math.PI * 2,
          type: 'super'
        });
      }
      return stars;
    };
    
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      if (starsRef.current) {
        starsRef.current.forEach(star => {
          const twinkle = Math.sin(time * star.speed * 0.06 + star.phase) * 0.5 + 0.5;
          const sparkle = Math.sin(time * star.speed * 0.1 + star.phase * 2) * 0.3 + 0.7;
          
          if (star.type === 'super') {
            const intensity = twinkle * sparkle;
            ctx.shadowBlur = 12;
            ctx.shadowColor = `rgba(255, 255, 255, ${intensity * 0.5 * opacity})`;
            ctx.strokeStyle = `rgba(255, 255, 255, ${intensity * 0.3 * opacity})`;
            ctx.lineWidth = 0.5;
            const len = star.size * 2 * intensity;
            ctx.beginPath();
            ctx.moveTo(star.x - len, star.y);
            ctx.lineTo(star.x + len, star.y);
            ctx.moveTo(star.x, star.y - len);
            ctx.lineTo(star.x, star.y + len);
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.size * intensity + 0.3, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${intensity * 0.9 * opacity})`;
            ctx.fill();
            ctx.shadowBlur = 0;
          } else if (star.type === 'sparkle') {
            const intensity = twinkle * sparkle;
            ctx.shadowBlur = 8;
            ctx.shadowColor = `rgba(255, 255, 255, ${intensity * 0.4 * opacity})`;
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.size * intensity + 0.3, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${(intensity * 0.85 + 0.1) * opacity})`;
            ctx.fill();
            ctx.shadowBlur = 0;
          } else {
            const intensity = twinkle * 0.6 + 0.4;
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.size * (intensity * 0.3 + 0.7), 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${intensity * 0.7 * opacity})`;
            ctx.fill();
          }
        });
      }
      
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
  }, [opacity]);
  
  return <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none" />;
};

// ============================================================================
// PAGE 3: ELECTRIC WORKFLOW (RESTORED FROM BACKUP)
// ============================================================================
const ElectricWorkflowPage = ({ onBack, workflowNodes, workflowEdges, onNodesChange, onEdgesChange }) => {
  const [selectedNode, setSelectedNode] = useState(null);
  const [buildStatus, setBuildStatus] = useState(null);
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'system', content: 'Workflow initialized. Ready to build your project.' }
  ]);
  const [terminalOutput, setTerminalOutput] = useState([
    { type: 'info', text: '> FRANKLIN OS Workflow Terminal v2.0' },
    { type: 'info', text: '> Type commands or use natural language' },
    { type: 'success', text: '> System ready.' }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const chatRef = useRef(null);

  useEffect(() => {
    const loadStatus = async () => {
      try {
        const response = await axios.get(`${API}/api/quality/builds`);
        if (response.data.builds?.length > 0) {
          setBuildStatus(response.data.builds[response.data.builds.length - 1]);
        }
      } catch (err) {
        console.error('Failed to load build status:', err);
      }
    };
    loadStatus();
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, []);

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
    setTerminalOutput(prev => [...prev, { type: 'cmd', text: `> ${input}` }]);
    
    try {
      const response = await axios.post(`${API}/api/grok/chat`, { 
        message: input,
        history: chatHistory.slice(-6)
      });
      
      if (response.data.response) {
        setChatHistory(prev => [...prev, { role: 'assistant', content: response.data.response }]);
        setTerminalOutput(prev => [...prev, { type: 'success', text: '> Response received' }]);
      }
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'assistant', content: 'I can help you with that. What specific aspect would you like to explore?' }]);
      setTerminalOutput(prev => [...prev, { type: 'error', text: `> Error: ${err.message}` }]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="workflow-page">
      <GalacticBackground opacity={1} />
      
      {/* Pulsing Chrome Header */}
      <div className="absolute top-0 left-0 right-0 h-16 z-50 bg-black/80 backdrop-blur-md border-b border-white/10 flex items-center justify-center">
        <button
          onClick={onBack}
          className="absolute left-4 px-4 py-2 text-xs font-mono text-white/70 hover:text-white hover:bg-white/10 rounded transition-all flex items-center gap-2"
          data-testid="back-to-ide"
        >
          ◀ BACK TO IDE
        </button>
        
        <div className="text-center">
          <h1 className="workflow-chrome-title text-2xl font-mono tracking-[0.3em]" style={{ fontFamily: "'Orbitron', sans-serif" }}>
            ◈ ELECTRIC WORKFLOW
          </h1>
          <p className="text-[10px] text-white/40 tracking-wider mt-1">VISUAL BUILD PIPELINE</p>
        </div>
        
        {buildStatus && (
          <div className="absolute right-4 text-[10px] font-mono text-white/50">
            BUILD: <span className="text-cyan-400">{buildStatus.build_id}</span>
            <span className={`ml-2 ${buildStatus.status === 'certified' ? 'text-green-400' : 'text-amber-400'}`}>
              {buildStatus.status?.toUpperCase()}
            </span>
          </div>
        )}
      </div>

      {/* LEFT SLIDE PANEL - Chat Response */}
      <div className={`absolute top-16 bottom-12 z-40 bg-black/90 border-r border-white/10 backdrop-blur-md transition-all duration-300 ${leftPanelOpen ? 'left-0 w-72' : '-left-72 w-72'}`}>
        <button
          onClick={() => setLeftPanelOpen(!leftPanelOpen)}
          className="absolute -right-8 top-1/2 -translate-y-1/2 w-8 h-16 bg-black/80 border border-white/10 rounded-r-lg flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-all"
        >
          {leftPanelOpen ? '◀' : '▶'}
        </button>
        
        <div className="p-4 h-full flex flex-col">
          <div className="text-[10px] font-mono text-white/40 tracking-wider mb-3">◆ CHAT RESPONSE</div>
          
          <div ref={chatRef} className="flex-1 overflow-y-auto space-y-3 scrollbar-thin">
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={`text-xs font-mono ${msg.role === 'user' ? 'text-cyan-400' : msg.role === 'system' ? 'text-amber-400' : 'text-white/80'}`}>
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

      {/* RIGHT SLIDE PANEL - Workflow Controls */}
      <div className={`absolute top-16 bottom-12 z-40 bg-black/90 border-l border-white/10 backdrop-blur-md transition-all duration-300 ${rightPanelOpen ? 'right-0 w-72' : '-right-72 w-72'}`}>
        <button
          onClick={() => setRightPanelOpen(!rightPanelOpen)}
          className="absolute -left-8 top-1/2 -translate-y-1/2 w-8 h-16 bg-black/80 border border-white/10 rounded-l-lg flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-all"
        >
          {rightPanelOpen ? '▶' : '◀'}
        </button>
        
        <div className="p-4 h-full flex flex-col overflow-y-auto">
          <div className="text-[10px] font-mono text-white/40 tracking-wider mb-4">◆ WORKFLOW CONTROLS</div>
          
          <div className="mb-6">
            <div className="text-xs font-mono text-white/60 mb-2">STAGE PROGRESS</div>
            <div className="space-y-2">
              {['Specification', 'Architecture', 'Implementation', 'Integration', 'Quality', 'Certification'].map((stage, idx) => (
                <div key={stage} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${
                    buildStatus?.stages_completed > idx ? 'bg-green-400' :
                    buildStatus?.stages_completed === idx ? 'bg-cyan-400 animate-pulse' :
                    'bg-white/20'
                  }`} />
                  <span className="text-[10px] font-mono text-white/60">{stage}</span>
                </div>
              ))}
            </div>
          </div>

          {selectedNode && (
            <div className="mb-6 p-3 bg-white/5 rounded-lg border border-white/10">
              <div className="text-xs font-mono text-white/60 mb-2">SELECTED NODE</div>
              <div className="text-sm font-mono text-white/90">{selectedNode.data?.label || selectedNode.id}</div>
              <div className={`text-[10px] mt-2 ${
                selectedNode.data?.status === 'completed' ? 'text-green-400' :
                selectedNode.data?.status === 'active' ? 'text-cyan-400' : 'text-white/40'
              }`}>
                {selectedNode.data?.status?.toUpperCase() || 'PENDING'}
              </div>
            </div>
          )}

          <div className="mb-6">
            <div className="text-xs font-mono text-white/60 mb-2">ADD NODE</div>
            <div className="grid grid-cols-2 gap-2">
              {['Stage', 'Decision', 'Action', 'Check'].map(type => (
                <button key={type} className="px-3 py-2 text-[10px] font-mono bg-white/5 border border-white/10 rounded hover:bg-white/10 transition-all">
                  + {type}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2 mt-auto">
            <button className="w-full px-4 py-3 text-xs font-mono bg-green-500/20 border border-green-500/30 rounded-lg text-green-400 hover:bg-green-500/30 transition-all">
              ▶ RUN WORKFLOW
            </button>
            <button className="w-full px-4 py-3 text-xs font-mono bg-white/5 border border-white/10 rounded-lg text-white/60 hover:bg-white/10 transition-all">
              ⟳ RESET
            </button>
            <button className="w-full px-4 py-3 text-xs font-mono bg-white/5 border border-white/10 rounded-lg text-white/60 hover:bg-white/10 transition-all">
              ↓ EXPORT
            </button>
          </div>
        </div>
      </div>

      {/* Main Workflow Canvas */}
      <div className={`absolute top-16 bottom-12 z-10 transition-all duration-300 ${leftPanelOpen ? 'left-72' : 'left-0'} ${rightPanelOpen ? 'right-72' : 'right-0'}`}>
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
          <Background color="rgba(255,255,255,0.02)" gap={30} style={{ opacity: 0.3 }} />
          <Controls className="!bg-black/70 !border-white/20 !rounded-lg" />
        </ReactFlow>
      </div>

      {/* BOTTOM BAR */}
      <div className="absolute bottom-0 left-0 right-0 h-12 z-40 bg-black/95 border-t border-white/10 backdrop-blur-md flex items-center">
        <div className="w-48 h-full border-r border-white/10 px-3 flex items-center gap-2">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
            placeholder="Ask about your workflow..."
            className="flex-1 bg-transparent border-none text-[10px] font-mono text-white placeholder-white/30 focus:outline-none"
            disabled={isProcessing}
          />
          <button
            onClick={handleChatSend}
            disabled={isProcessing || !chatInput.trim()}
            className="px-2 py-1 text-[9px] font-mono text-cyan-400 hover:bg-white/10 rounded transition-all disabled:opacity-30"
          >
            ▶
          </button>
        </div>

        <div className="w-64 h-full border-r border-white/10 px-3 flex items-center">
          <div className="text-[9px] font-mono text-white/50">
            <span className="text-white/30">PROJECT:</span> <span className="text-cyan-400">{buildStatus?.project_name || 'No Project'}</span>
            <span className="mx-2 text-white/20">|</span>
            <span className="text-white/30">STATUS:</span> <span className={buildStatus?.status === 'certified' ? 'text-green-400' : 'text-amber-400'}>{buildStatus?.status?.toUpperCase() || 'IDLE'}</span>
          </div>
        </div>

        <div className="flex-1 h-full px-4 flex items-center overflow-hidden">
          <div className="text-[9px] font-mono text-green-400 truncate">
            {terminalOutput.length > 0 ? terminalOutput[terminalOutput.length - 1].text : '> System ready.'}
          </div>
        </div>
      </div>

      {/* Chrome Pulsing Title Styles */}
      <style>{`
        .workflow-chrome-title {
          background: linear-gradient(90deg, rgba(100,100,100,0.8) 0%, rgba(180,180,180,1) 25%, rgba(255,255,255,1) 50%, rgba(180,180,180,1) 75%, rgba(100,100,100,0.8) 100%);
          background-size: 200% 100%;
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: chromePulse 3s ease-in-out infinite;
          filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
        }
        @keyframes chromePulse {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        .scrollbar-thin::-webkit-scrollbar { width: 4px; }
        .scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
        .scrollbar-thin::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
      `}</style>

      {/* Electric Grid Overlay */}
      <div className="absolute inset-0 pointer-events-none z-[5] opacity-10">
        <div className="w-full h-full" style={{
          backgroundImage: `linear-gradient(rgba(0, 255, 136, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 136, 0.1) 1px, transparent 1px)`,
          backgroundSize: '50px 50px'
        }} />
      </div>
    </div>
  );
};

// ============================================================================
// PAGE 2: MAIN IDE - MATCHING WIREFRAME EXACTLY
// ============================================================================
const IDEPage = ({ onNavigate }) => {
  // Panel widths (resizable)
  const [leftWidth, setLeftWidth] = useState(280);
  const [rightWidth, setRightWidth] = useState(280);
  const [isResizingLeft, setIsResizingLeft] = useState(false);
  const [isResizingRight, setIsResizingRight] = useState(false);
  
  // Chat states
  const [franklinInput, setFranklinInput] = useState('');
  const [grokInput, setGrokInput] = useState('');
  const [terminalInput, setTerminalInput] = useState('');
  
  const [franklinChat, setFranklinChat] = useState(() => {
    const saved = localStorage.getItem('franklin_chat_v2');
    return saved ? JSON.parse(saved) : [
      { role: 'franklin', content: 'Welcome to FRANKLIN OS. I\'m here to help you navigate and build. What would you like to create today?' }
    ];
  });
  
  const [grokResponses, setGrokResponses] = useState(() => {
    const saved = localStorage.getItem('grok_responses_v2');
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
  
  const [savedChats, setSavedChats] = useState(() => {
    const saved = localStorage.getItem('saved_chats_v2');
    return saved ? JSON.parse(saved) : [];
  });
  
  // UI states
  const [codeContent] = useState('// Your code will appear here...\n// Use /genesis <mission> to start building\n');
  const [projectsOpen, setProjectsOpen] = useState(false);
  const [foldersOpen, setFoldersOpen] = useState(false);
  const [franklinLoading, setFranklinLoading] = useState(false);
  
  // Refs
  const franklinRef = useRef(null);
  const grokRef = useRef(null);
  const terminalRef = useRef(null);
  
  // Resize handlers
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isResizingLeft) {
        setLeftWidth(Math.min(450, Math.max(200, e.clientX)));
      } else if (isResizingRight) {
        setRightWidth(Math.min(450, Math.max(200, window.innerWidth - e.clientX)));
      }
    };
    
    const handleMouseUp = () => {
      setIsResizingLeft(false);
      setIsResizingRight(false);
    };
    
    if (isResizingLeft || isResizingRight) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizingLeft, isResizingRight]);
  
  // Save to localStorage
  useEffect(() => { localStorage.setItem('franklin_chat_v2', JSON.stringify(franklinChat.slice(-50))); }, [franklinChat]);
  useEffect(() => { localStorage.setItem('grok_responses_v2', JSON.stringify(grokResponses.slice(-50))); }, [grokResponses]);
  useEffect(() => { localStorage.setItem('terminal_output_v2', JSON.stringify(terminalOutput.slice(-100))); }, [terminalOutput]);
  useEffect(() => { localStorage.setItem('saved_chats_v2', JSON.stringify(savedChats.slice(-20))); }, [savedChats]);
  
  // Auto-scroll
  useEffect(() => { if (franklinRef.current) franklinRef.current.scrollTop = franklinRef.current.scrollHeight; }, [franklinChat]);
  useEffect(() => { if (grokRef.current) grokRef.current.scrollTop = grokRef.current.scrollHeight; }, [grokResponses]);
  useEffect(() => { if (terminalRef.current) terminalRef.current.scrollTop = terminalRef.current.scrollHeight; }, [terminalOutput]);
  
  const addTerminal = (text, type = 'info') => {
    setTerminalOutput(prev => [...prev, { type, text: `> ${text}` }]);
  };
  
  const addGrokResponse = (text, phase = 'GROK') => {
    setGrokResponses(prev => [...prev, { phase, content: text, timestamp: new Date().toISOString() }]);
  };
  
  // Handle Franklin send
  const handleFranklinSend = async () => {
    if (!franklinInput.trim() || franklinLoading) return;
    
    const input = franklinInput.trim();
    setFranklinInput('');
    setFranklinChat(prev => [...prev, { role: 'user', content: input }]);
    setFranklinLoading(true);
    
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
              addGrokResponse(`[${entry.agent || entry.phase}] ${entry.message}`, entry.phase);
            }
          });
        }
        if (response.data.success) {
          addTerminal('BUILD COMPLETE ✓', 'success');
          addGrokResponse('Build complete! All agents have finished.', 'COMPLETE');
        }
      } catch (err) {
        addTerminal(`Error: ${err.message}`, 'error');
      }
      setFranklinLoading(false);
      return;
    }
    
    if (input.toLowerCase() === '/workflow') {
      onNavigate(PAGES.WORKFLOW);
      setFranklinLoading(false);
      return;
    }
    
    if (input.toLowerCase() === '/clear') {
      setFranklinChat([{ role: 'franklin', content: 'Chat cleared. What would you like to build?' }]);
      setGrokResponses([]);
      setTerminalOutput([{ type: 'system', text: '> Terminal cleared' }]);
      setFranklinLoading(false);
      return;
    }
    
    if (input.toLowerCase() === '/save') {
      setSavedChats(prev => [...prev, { id: Date.now(), title: franklinChat[1]?.content?.slice(0, 30) + '...' || 'New Chat', messages: franklinChat }]);
      setFranklinChat(prev => [...prev, { role: 'franklin', content: 'Chat saved!' }]);
      setFranklinLoading(false);
      return;
    }
    
    if (input.toLowerCase() === '/help') {
      setFranklinChat(prev => [...prev, { role: 'franklin', content: 'Commands:\n• /genesis <mission>\n• /workflow\n• /clear\n• /save\n• /help' }]);
      setFranklinLoading(false);
      return;
    }
    
    try {
      const response = await axios.post(`${API}/api/build-orchestrator/chat`, { message: input });
      setFranklinChat(prev => [...prev, { role: 'franklin', content: response.data.response || "I can help with that." }]);
    } catch (err) {
      setFranklinChat(prev => [...prev, { role: 'franklin', content: "Use /genesis <description> to start building." }]);
    }
    setFranklinLoading(false);
  };
  
  // Handle Grok send
  const handleGrokSend = async () => {
    if (!grokInput.trim()) return;
    const input = grokInput.trim();
    setGrokInput('');
    addGrokResponse(`[USER] ${input}`, 'USER');
    
    try {
      const response = await axios.post(`${API}/api/grok/chat`, { message: input, history: grokResponses.slice(-6) });
      addGrokResponse(response.data.response || "Processing...", 'GROK');
    } catch (err) {
      addGrokResponse("I can analyze that. What interests you?", 'GROK');
    }
  };
  
  // Handle terminal
  const handleTerminalSend = () => {
    if (!terminalInput.trim()) return;
    const input = terminalInput.trim();
    setTerminalInput('');
    addTerminal(input, 'cmd');
    
    if (input === 'clear') setTerminalOutput([{ type: 'system', text: '> Cleared' }]);
    else if (input === 'help') addTerminal('Commands: clear, help, status', 'info');
    else if (input === 'status') { addTerminal('FRANKLIN OS: Online', 'success'); addTerminal('Grok: Connected', 'success'); }
    else if (input.startsWith('/genesis ')) { setFranklinInput(input); setTimeout(handleFranklinSend, 100); }
  };
  
  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="franklin-os">
      <GalacticBackground opacity={1} />
      
      {/* FRANKLIN GHOST TITLE */}
      <div className="fixed inset-x-0 top-[18%] flex justify-center pointer-events-none z-[1]">
        <h1 className="select-none whitespace-nowrap" style={{ 
          fontFamily: "'Orbitron', sans-serif",
          fontSize: 'clamp(5rem, 14vw, 12rem)',
          fontWeight: 600,
          letterSpacing: '0.4em',
          paddingLeft: '0.2em',
          background: 'linear-gradient(180deg, rgba(100,100,100,0.2) 0%, rgba(140,140,140,0.25) 50%, rgba(100,100,100,0.2) 100%)',
          WebkitBackgroundClip: 'text',
          backgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>FRANKLIN</h1>
      </div>
      
      {/* TOP HEADER */}
      <div className="absolute top-0 left-0 right-0 h-8 z-50 bg-black/80 border-b border-white/10 flex items-center px-4">
        <div className="text-xs font-mono text-white/90 tracking-wider" style={{ fontFamily: "'Orbitron', sans-serif" }}>◈ FRANKLIN OS</div>
        <div className="flex-1" />
        <button onClick={() => { setFranklinChat([{ role: 'franklin', content: 'Cleared.' }]); setGrokResponses([]); setTerminalOutput([{ type: 'system', text: '> Cleared' }]); }} className="mr-2 px-2 py-0.5 text-[8px] font-mono text-white/40 hover:text-white border border-white/10 rounded">🗑 CLEAR</button>
        <div className="flex items-center gap-3 text-[8px] font-mono">
          <span className="text-green-400 flex items-center gap-1"><span className="w-1 h-1 bg-green-400 rounded-full animate-pulse" />SENTINEL: ACTIVE</span>
          <span className="text-cyan-400">PQC: ONLINE</span>
          <span className="text-purple-400">AUDIT: 1 entries</span>
          <span className="text-green-400">AGENTS: 5</span>
        </div>
      </div>
      
      {/* ============================================================ */}
      {/* MAIN LAYOUT - EXACTLY MATCHING WIREFRAME */}
      {/* ============================================================ */}
      
      {/* LEFT PANEL - FRANKLIN */}
      <div className="absolute top-8 bottom-40 left-0 z-30 bg-black/50 backdrop-blur-sm border-r border-white/10 flex flex-col" style={{ width: leftWidth }} data-testid="franklin-panel">
        {/* Header */}
        <div className="h-8 px-3 border-b border-white/10 flex items-center justify-between">
          <span className="text-[10px] font-mono text-cyan-400">◆ FRANKLIN</span>
          <span className="text-[8px] font-mono text-white/30">COLLAPSE</span>
        </div>
        
        {/* FRANKLIN ONBOARD CHAT section */}
        <div className="h-6 px-3 border-b border-white/5 flex items-center justify-between">
          <span className="text-[9px] font-mono text-white/50">FRANKLIN ONBOARD CHAT</span>
          <span className="text-[7px] font-mono text-white/30 border border-white/10 px-1 rounded">⊞ EXPAND</span>
        </div>
        
        {/* Context Window label */}
        <div className="px-3 py-1 text-[8px] font-mono text-white/20">Context Window</div>
        
        {/* Chat messages */}
        <div ref={franklinRef} className="flex-1 overflow-y-auto px-3 py-2 space-y-2 scrollbar-thin">
          {franklinChat.map((msg, idx) => (
            <div key={idx} className={`text-[10px] font-mono ${msg.role === 'user' ? 'text-cyan-400' : 'text-white/70'}`}>
              <span className="text-white/30 text-[8px]">◈ {msg.role.toUpperCase()}</span>
              <p className="mt-0.5 leading-relaxed">{msg.content}</p>
            </div>
          ))}
          {franklinLoading && <div className="text-purple-400 text-[10px] flex items-center gap-1"><span className="animate-spin">◈</span> Processing...</div>}
        </div>
        
        {/* 1 million context label */}
        <div className="h-6 px-3 border-t border-white/5 flex items-center justify-center">
          <span className="text-[9px] font-mono text-cyan-400/60">1 million context</span>
        </div>
        
        {/* Resize handle */}
        <div onMouseDown={() => setIsResizingLeft(true)} className="absolute top-0 bottom-0 right-0 w-1 cursor-col-resize hover:bg-cyan-400/30 transition-colors" />
      </div>
      
      {/* FRANKLIN PROMPT - Bottom of left panel */}
      <div className="absolute left-0 bottom-28 h-12 z-40 bg-black/70 border border-cyan-500/30 flex items-center px-3" style={{ width: leftWidth }} data-testid="franklin-prompt">
        <span className="text-[9px] font-mono text-cyan-400 mr-2">Franklin Prompt</span>
        <span className="text-cyan-400 mr-2">▶</span>
        <input
          type="text"
          value={franklinInput}
          onChange={(e) => setFranklinInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleFranklinSend()}
          placeholder="Type here..."
          className="flex-1 bg-transparent text-[10px] font-mono text-white placeholder-white/30 focus:outline-none"
          disabled={franklinLoading}
        />
      </div>
      
      {/* CENTER - CODE AREA */}
      <div className="absolute top-8 bottom-40 z-20 flex flex-col" style={{ left: leftWidth, right: rightWidth }} data-testid="code-area">
        {/* Code area header */}
        <div className="h-6 bg-black/60 border-b border-white/10 flex items-center px-4 text-[9px] font-mono text-white/40">
          <span className="text-cyan-400">code area</span>
          <span className="mx-2 text-white/20">|</span>
          <span>1 million context</span>
          <span className="ml-auto text-white/30">untitled.js</span>
        </div>
        
        {/* Code content */}
        <div className="flex-1 bg-black/30 p-4 overflow-auto relative">
          <pre className="text-[10px] font-mono text-white/50 whitespace-pre-wrap">{codeContent}</pre>
          
          {/* Ghost lines indicator */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-3 text-[9px] font-mono text-cyan-400/30 pointer-events-none">
            <span>◄───</span>
            <span>ghost lines</span>
            <span>───►</span>
          </div>
        </div>
      </div>
      
      {/* RIGHT PANEL - GROK */}
      <div className="absolute top-8 bottom-40 right-0 z-30 bg-black/50 backdrop-blur-sm border-l border-white/10 flex flex-col" style={{ width: rightWidth }} data-testid="grok-panel">
        {/* Header */}
        <div className="h-8 px-3 border-b border-white/10 flex items-center justify-between">
          <span className="text-[10px] font-mono text-green-400">◆ GROK</span>
          <div className="flex items-center gap-1 text-[8px] font-mono text-white/30" style={{ writingMode: 'horizontal-tb' }}>
            <span>▶</span>
            <span>ACADEMY</span>
          </div>
        </div>
        
        {/* Vertical tabs for BOTS */}
        <div className="absolute right-0 top-10 text-[7px] font-mono text-white/20" style={{ writingMode: 'vertical-rl' }}>
          <span className="py-2">▶ BOTS</span>
        </div>
        
        {/* Grok Responses */}
        <div ref={grokRef} className="flex-1 overflow-y-auto px-3 py-2 space-y-2 scrollbar-thin">
          {grokResponses.length === 0 ? (
            <div className="text-[9px] font-mono text-white/30 text-center py-4">
              <p>Grok responses appear here...</p>
              <p className="mt-1">Use the input below to ask Grok</p>
            </div>
          ) : (
            grokResponses.map((msg, idx) => (
              <div key={idx} className="text-[10px] font-mono text-white/70">
                <span className="text-white/30 text-[8px]">◈ {msg.phase}</span>
                <p className="mt-0.5 leading-relaxed">{msg.content}</p>
              </div>
            ))
          )}
        </div>
        
        {/* 1 million context label */}
        <div className="h-6 px-3 border-t border-white/5 flex items-center justify-center">
          <span className="text-[9px] font-mono text-green-400/60">1 million context</span>
        </div>
        
        {/* Saved chats section */}
        <div className="border-t border-white/10">
          <div className="px-3 py-1 text-[9px] font-mono text-white/40">saved chats</div>
          <div className="max-h-20 overflow-y-auto px-2 pb-2">
            {savedChats.length === 0 ? (
              <div className="text-[8px] font-mono text-white/20 text-center py-1">No saved chats. Use /save</div>
            ) : (
              savedChats.map(chat => (
                <div key={chat.id} className="py-0.5 px-2 text-[8px] font-mono text-white/40 hover:bg-white/5 rounded cursor-pointer truncate">{chat.title}</div>
              ))
            )}
          </div>
        </div>
        
        {/* Resize handle */}
        <div onMouseDown={() => setIsResizingRight(true)} className="absolute top-0 bottom-0 left-0 w-1 cursor-col-resize hover:bg-green-400/30 transition-colors" />
      </div>
      
      {/* GROK PROMPT - Bottom of right panel */}
      <div className="absolute right-0 bottom-28 h-12 z-40 bg-black/70 border border-green-500/30 flex items-center px-3" style={{ width: rightWidth }} data-testid="grok-prompt">
        <span className="text-[9px] font-mono text-green-400 mr-2">Grok Prompt</span>
        <span className="text-green-400 mr-2">▶</span>
        <input
          type="text"
          value={grokInput}
          onChange={(e) => setGrokInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleGrokSend()}
          placeholder="Ask Grok anything..."
          className="flex-1 bg-transparent text-[10px] font-mono text-white placeholder-white/30 focus:outline-none"
        />
      </div>
      
      {/* ============================================================ */}
      {/* BOTTOM SECTION - FOLDERS + TERMINAL */}
      {/* ============================================================ */}
      
      {/* Folder tabs - centered between panels, aligned */}
      <div className="absolute bottom-28 z-35 flex items-end justify-center gap-2" style={{ left: leftWidth, right: rightWidth }}>
        <button onClick={() => setProjectsOpen(!projectsOpen)} className={`px-3 py-1 text-[8px] font-mono border rounded-t transition-all ${projectsOpen ? 'bg-red-900/30 border-red-500/40 text-red-400' : 'bg-black/50 border-white/10 text-white/40'}`}>
          ▼ PROJECTS
        </button>
        <button onClick={() => setFoldersOpen(!foldersOpen)} className={`px-3 py-1 text-[8px] font-mono border rounded-t transition-all ${foldersOpen ? 'bg-yellow-900/30 border-yellow-500/40 text-yellow-400' : 'bg-black/50 border-white/10 text-white/40'}`}>
          ▼ FOLDERS
        </button>
      </div>
      
      {/* PROJECTS section - below Franklin prompt */}
      <div className="absolute left-0 bottom-0 h-28 z-40 bg-black/80 border-t border-r border-white/10 flex flex-col" style={{ width: leftWidth }}>
        <div className="px-3 py-1 text-[9px] font-mono text-red-400 border-b border-white/5">projects</div>
        <div className="flex-1 overflow-y-auto px-2 py-1">
          <div className="text-[8px] font-mono text-white/40 py-0.5 px-2 hover:bg-white/5 rounded cursor-pointer">📁 Project Alpha</div>
          <div className="text-[8px] font-mono text-white/40 py-0.5 px-2 hover:bg-white/5 rounded cursor-pointer">📁 Franklin Demo</div>
        </div>
      </div>
      
      {/* TERMINAL - Center */}
      <div className="absolute bottom-0 h-28 z-40 bg-black/80 border-t border-white/10 flex flex-col" style={{ left: leftWidth, right: rightWidth }} data-testid="terminal">
        {/* Terminal header */}
        <div className="h-5 px-3 border-b border-white/5 flex items-center text-[8px] font-mono">
          <span className="text-purple-400">◆ TERMINAL</span>
          <span className="mx-3 text-white/20">|</span>
          <span className="text-white/30">SDK Cloud → Ubuntu/Linux → PowerShell</span>
        </div>
        
        {/* Terminal output */}
        <div ref={terminalRef} className="flex-1 overflow-y-auto px-3 py-1 scrollbar-thin">
          {terminalOutput.map((line, idx) => (
            <div key={idx} className={`text-[9px] font-mono ${
              line.type === 'error' ? 'text-red-400' :
              line.type === 'success' ? 'text-green-400' :
              line.type === 'system' ? 'text-purple-400' :
              line.type === 'cmd' ? 'text-cyan-400' : 'text-white/50'
            }`}>{line.text}</div>
          ))}
        </div>
        
        {/* Terminal input */}
        <div className="h-5 px-3 border-t border-white/5 flex items-center">
          <span className="text-purple-400 text-[8px] mr-2">/genesis mission...</span>
          <input
            type="text"
            value={terminalInput}
            onChange={(e) => setTerminalInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleTerminalSend()}
            placeholder="Enter command..."
            className="flex-1 bg-transparent text-[9px] font-mono text-white placeholder-white/30 focus:outline-none"
          />
        </div>
      </div>
      
      {/* SAVED CHATS / GROK RESPONSE - Right side bottom */}
      <div className="absolute right-0 bottom-0 h-28 z-40 bg-black/80 border-t border-l border-white/10 flex flex-col" style={{ width: rightWidth }}>
        <div className="h-5 px-3 border-b border-white/5 flex items-center justify-end">
          <span className="text-[8px] font-mono text-green-400">◈ GROK RESPONSE</span>
        </div>
        <div className="flex-1 overflow-y-auto px-3 py-1">
          <div className="text-[8px] font-mono text-white/40">Grok responses appear here...</div>
          {grokResponses.slice(-3).map((msg, idx) => (
            <div key={idx} className="text-[8px] font-mono text-white/30 truncate py-0.5">{msg.content?.slice(0, 40)}...</div>
          ))}
        </div>
        <div className="h-5 px-3 border-t border-white/5 flex items-center">
          <span className="text-green-400 text-[8px] mr-2">▶</span>
          <span className="text-[8px] font-mono text-white/30">Ask Grok anything...</span>
        </div>
        
        {/* SM Context Window label */}
        <div className="absolute bottom-1 right-2 text-[7px] font-mono text-white/15">SM Context Window</div>
      </div>
      
      {/* Made with Emergent */}
      <div className="fixed bottom-1 right-2 z-50 text-[8px] font-mono text-white/20 flex items-center gap-1">
        <span className="text-cyan-400">◎</span> Made with Emergent
      </div>
      
      {/* Workflow button */}
      <button onClick={() => onNavigate(PAGES.WORKFLOW)} className="fixed top-1 right-4 z-50 px-2 py-0.5 text-[8px] font-mono text-purple-400 hover:bg-purple-500/20 border border-purple-500/30 rounded">
        ◈ WORKFLOW
      </button>
      
      <style>{`
        .scrollbar-thin::-webkit-scrollbar { width: 3px; }
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
  
  const handleNavigate = (page) => setCurrentPage(page);
  
  if (currentPage === PAGES.LANDING) {
    return <LandingPage onEnterApp={() => handleNavigate(PAGES.IDE)} />;
  }
  
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
  
  return <IDEPage onNavigate={handleNavigate} />;
}

export default App;
