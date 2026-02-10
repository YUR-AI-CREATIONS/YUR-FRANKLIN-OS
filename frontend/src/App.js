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
import NeuralBrain from './components/NeuralBrain';
import './App.css';

const API = process.env.REACT_APP_BACKEND_URL || '';

const PAGES = { LANDING: 'landing', IDE: 'ide', WORKFLOW: 'workflow' };

// ============================================================================
// GALACTIC BACKGROUND
// ============================================================================
const GalacticBackground = ({ opacity = 1 }) => {
  const canvasRef = useRef(null);
  const starsRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationId, time = 0;
    
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      starsRef.current = [];
      for (let i = 0; i < 150; i++) starsRef.current.push({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, size: Math.random() * 1 + 0.3, speed: Math.random() * 1.5 + 0.5, phase: Math.random() * Math.PI * 2, type: 'regular' });
      for (let i = 0; i < 20; i++) starsRef.current.push({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, size: Math.random() * 1.5 + 1, speed: Math.random() * 2 + 1, phase: Math.random() * Math.PI * 2, type: 'sparkle' });
    };
    
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (starsRef.current) {
        starsRef.current.forEach(star => {
          const twinkle = Math.sin(time * star.speed * 0.06 + star.phase) * 0.5 + 0.5;
          if (star.type === 'sparkle') {
            ctx.shadowBlur = 8;
            ctx.shadowColor = `rgba(255, 255, 255, ${twinkle * 0.4 * opacity})`;
          }
          ctx.beginPath();
          ctx.arc(star.x, star.y, star.size * (twinkle * 0.3 + 0.7), 0, Math.PI * 2);
          ctx.fillStyle = `rgba(255, 255, 255, ${twinkle * 0.7 * opacity})`;
          ctx.fill();
          ctx.shadowBlur = 0;
        });
      }
      time += 1;
      animationId = requestAnimationFrame(draw);
    };
    
    resize();
    draw();
    window.addEventListener('resize', resize);
    return () => { cancelAnimationFrame(animationId); window.removeEventListener('resize', resize); };
  }, [opacity]);
  
  return <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none" />;
};

// ============================================================================
// WORKFLOW PAGE (UNCHANGED)
// ============================================================================
const ElectricWorkflowPage = ({ onBack, workflowNodes, workflowEdges, onNodesChange, onEdgesChange }) => {
  const [selectedNode, setSelectedNode] = useState(null);
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([{ role: 'system', content: 'Workflow initialized.' }]);
  const [isProcessing, setIsProcessing] = useState(false);
  const chatRef = useRef(null);

  useEffect(() => { if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight; }, [chatHistory]);

  const onConnect = useCallback((params) => {
    onEdgesChange((eds) => addEdge({ ...params, animated: true, style: { stroke: '#00ff88', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#00ff88' } }, eds));
  }, [onEdgesChange]);

  const onNodeClick = useCallback((event, node) => { setSelectedNode(node); }, []);

  const handleChatSend = async () => {
    if (!chatInput.trim() || isProcessing) return;
    const input = chatInput.trim();
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: input }]);
    setIsProcessing(true);
    try {
      const response = await axios.post(`${API}/api/grok/chat`, { message: input, history: chatHistory.slice(-6) });
      if (response.data.response) setChatHistory(prev => [...prev, { role: 'assistant', content: response.data.response }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'assistant', content: 'I can help. What would you like to explore?' }]);
    } finally { setIsProcessing(false); }
  };

  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="workflow-page">
      <GalacticBackground opacity={1} />
      <div className="absolute top-0 left-0 right-0 h-16 z-50 bg-black/80 backdrop-blur-md border-b border-white/10 flex items-center justify-center">
        <button onClick={onBack} className="absolute left-4 px-4 py-2 text-xs font-mono text-white/70 hover:text-white hover:bg-white/10 rounded" data-testid="back-to-ide">◀ BACK TO IDE</button>
        <div className="text-center">
          <h1 className="text-2xl font-mono tracking-[0.3em] text-white/90" style={{ fontFamily: "'Orbitron', sans-serif" }}>◈ ELECTRIC WORKFLOW</h1>
          <p className="text-[10px] text-white/40 tracking-wider mt-1">VISUAL BUILD PIPELINE</p>
        </div>
      </div>
      <div className={`absolute top-16 bottom-12 z-40 bg-black/90 border-r border-white/10 transition-all duration-300 ${leftPanelOpen ? 'left-0 w-72' : '-left-72 w-72'}`}>
        <button onClick={() => setLeftPanelOpen(!leftPanelOpen)} className="absolute -right-8 top-1/2 -translate-y-1/2 w-8 h-16 bg-black/80 border border-white/10 rounded-r-lg flex items-center justify-center text-white/50 hover:text-white">{leftPanelOpen ? '◀' : '▶'}</button>
        <div className="p-4 h-full flex flex-col">
          <div className="text-[10px] font-mono text-white/40 mb-3">◆ CHAT RESPONSE</div>
          <div ref={chatRef} className="flex-1 overflow-y-auto space-y-3 scrollbar-thin">
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={`text-xs font-mono ${msg.role === 'user' ? 'text-cyan-400' : 'text-white/80'}`}>
                <span className="text-white/30 text-[9px]">[{msg.role.toUpperCase()}]</span>
                <p className="mt-1">{msg.content}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className={`absolute top-16 bottom-12 z-40 bg-black/90 border-l border-white/10 transition-all duration-300 ${rightPanelOpen ? 'right-0 w-72' : '-right-72 w-72'}`}>
        <button onClick={() => setRightPanelOpen(!rightPanelOpen)} className="absolute -left-8 top-1/2 -translate-y-1/2 w-8 h-16 bg-black/80 border border-white/10 rounded-l-lg flex items-center justify-center text-white/50 hover:text-white">{rightPanelOpen ? '▶' : '◀'}</button>
        <div className="p-4 h-full flex flex-col overflow-y-auto">
          <div className="text-[10px] font-mono text-white/40 mb-4">◆ WORKFLOW CONTROLS</div>
          <div className="space-y-2">
            {['Specification', 'Architecture', 'Implementation', 'Integration', 'Quality', 'Certification'].map((stage, idx) => (
              <div key={stage} className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${idx < 2 ? 'bg-green-400' : 'bg-white/20'}`} />
                <span className="text-[10px] font-mono text-white/60">{stage}</span>
              </div>
            ))}
          </div>
          {selectedNode && (
            <div className="mt-4 p-3 bg-white/5 rounded-lg border border-white/10">
              <div className="text-xs font-mono text-white/60 mb-2">SELECTED NODE</div>
              <div className="text-sm font-mono text-white/90">{selectedNode.data?.label || selectedNode.id}</div>
            </div>
          )}
          <div className="space-y-2 mt-auto">
            <button className="w-full px-4 py-3 text-xs font-mono bg-green-500/20 border border-green-500/30 rounded-lg text-green-400">▶ RUN WORKFLOW</button>
            <button className="w-full px-4 py-3 text-xs font-mono bg-white/5 border border-white/10 rounded-lg text-white/60">⟳ RESET</button>
          </div>
        </div>
      </div>
      <div className={`absolute top-16 bottom-12 z-10 transition-all duration-300 ${leftPanelOpen ? 'left-72' : 'left-0'} ${rightPanelOpen ? 'right-72' : 'right-0'}`}>
        <ReactFlow nodes={workflowNodes} edges={workflowEdges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} onNodeClick={onNodeClick} fitView className="!bg-transparent">
          <Background color="rgba(255,255,255,0.02)" gap={30} />
          <Controls className="!bg-black/70 !border-white/20 !rounded-lg" />
        </ReactFlow>
      </div>
      <div className="absolute bottom-0 left-0 right-0 h-12 z-40 bg-black/95 border-t border-white/10 flex items-center px-4">
        <input type="text" value={chatInput} onChange={(e) => setChatInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleChatSend()} placeholder="Ask about workflow..." className="flex-1 bg-transparent text-[10px] font-mono text-white placeholder-white/30 focus:outline-none" />
        <button onClick={handleChatSend} className="px-3 py-1 text-xs font-mono text-cyan-400">▶</button>
      </div>
      <style>{`.scrollbar-thin::-webkit-scrollbar { width: 4px; } .scrollbar-thin::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); }`}</style>
    </div>
  );
};

// ============================================================================
// IDE PAGE - EXACTLY MATCHING YOUR WIREFRAME
// ============================================================================
const IDEPage = ({ onNavigate }) => {
  const [leftWidth, setLeftWidth] = useState(300);
  const [rightWidth, setRightWidth] = useState(300);
  const [isResizingLeft, setIsResizingLeft] = useState(false);
  const [isResizingRight, setIsResizingRight] = useState(false);
  
  const [franklinInput, setFranklinInput] = useState('');
  const [grokInput, setGrokInput] = useState('');
  const [terminalInput, setTerminalInput] = useState('');
  
  const [franklinChat, setFranklinChat] = useState(() => {
    const saved = localStorage.getItem('franklin_chat_v2');
    return saved ? JSON.parse(saved) : [{ role: 'franklin', content: 'Welcome to FRANKLIN OS. I\'m here to help you navigate and build. What would you like to create today?' }];
  });
  
  const [grokChat, setGrokChat] = useState(() => {
    const saved = localStorage.getItem('grok_chat_v2');
    return saved ? JSON.parse(saved) : [];
  });
  
  const [terminalOutput, setTerminalOutput] = useState([
    { type: 'system', text: '> FRANKLIN OS Terminal v2.0' },
    { type: 'system', text: '> Ready...' }
  ]);
  
  const [savedChats, setSavedChats] = useState(() => {
    const saved = localStorage.getItem('saved_chats_v2');
    return saved ? JSON.parse(saved) : [];
  });
  
  const [codeContent] = useState('// Your code will appear here...\n// Use /genesis <mission> to start building\n');
  const [franklinLoading, setFranklinLoading] = useState(false);
  const [grokLoading, setGrokLoading] = useState(false);
  
  const franklinRef = useRef(null);
  const grokRef = useRef(null);
  const terminalRef = useRef(null);
  
  // Resize
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isResizingLeft) setLeftWidth(Math.min(500, Math.max(220, e.clientX)));
      else if (isResizingRight) setRightWidth(Math.min(500, Math.max(220, window.innerWidth - e.clientX)));
    };
    const handleMouseUp = () => { setIsResizingLeft(false); setIsResizingRight(false); };
    if (isResizingLeft || isResizingRight) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }
    return () => { document.removeEventListener('mousemove', handleMouseMove); document.removeEventListener('mouseup', handleMouseUp); };
  }, [isResizingLeft, isResizingRight]);
  
  // Persist
  useEffect(() => { localStorage.setItem('franklin_chat_v2', JSON.stringify(franklinChat.slice(-50))); }, [franklinChat]);
  useEffect(() => { localStorage.setItem('grok_chat_v2', JSON.stringify(grokChat.slice(-50))); }, [grokChat]);
  useEffect(() => { localStorage.setItem('saved_chats_v2', JSON.stringify(savedChats.slice(-20))); }, [savedChats]);
  
  // Scroll
  useEffect(() => { if (franklinRef.current) franklinRef.current.scrollTop = franklinRef.current.scrollHeight; }, [franklinChat]);
  useEffect(() => { if (grokRef.current) grokRef.current.scrollTop = grokRef.current.scrollHeight; }, [grokChat]);
  useEffect(() => { if (terminalRef.current) terminalRef.current.scrollTop = terminalRef.current.scrollHeight; }, [terminalOutput]);
  
  const addTerminal = (text, type = 'info') => setTerminalOutput(prev => [...prev, { type, text: `> ${text}` }]);
  
  // Franklin handler
  const handleFranklinSend = async () => {
    if (!franklinInput.trim() || franklinLoading) return;
    const input = franklinInput.trim();
    setFranklinInput('');
    setFranklinChat(prev => [...prev, { role: 'user', content: input }]);
    setFranklinLoading(true);
    
    if (input.toLowerCase().startsWith('/genesis ') || input.toLowerCase().startsWith('/build ')) {
      const mission = input.replace(/^\/(?:genesis|build)\s+/i, '');
      addTerminal(`GENESIS: ${mission}`, 'system');
      setFranklinChat(prev => [...prev, { role: 'franklin', content: `Initiating build: "${mission}". Watch the terminal.` }]);
      try {
        const response = await axios.post(`${API}/api/build-orchestrator/build`, { mission });
        if (response.data.output) {
          response.data.output.forEach(entry => {
            addTerminal(`[${entry.phase}] ${entry.message}`, entry.type || 'info');
            if (entry.phase.toLowerCase().includes('grok') || entry.agent) {
              setGrokChat(prev => [...prev, { role: 'grok', content: `[${entry.agent || entry.phase}] ${entry.message}` }]);
            }
          });
        }
        if (response.data.success) addTerminal('BUILD COMPLETE ✓', 'success');
      } catch (err) { addTerminal(`Error: ${err.message}`, 'error'); }
      setFranklinLoading(false);
      return;
    }
    if (input.toLowerCase() === '/workflow') { onNavigate(PAGES.WORKFLOW); setFranklinLoading(false); return; }
    if (input.toLowerCase() === '/clear') { setFranklinChat([{ role: 'franklin', content: 'Cleared.' }]); setGrokChat([]); setTerminalOutput([{ type: 'system', text: '> Cleared' }]); setFranklinLoading(false); return; }
    if (input.toLowerCase() === '/save') { setSavedChats(prev => [...prev, { id: Date.now(), title: franklinChat[1]?.content?.slice(0, 30) + '...' || 'New Chat', messages: franklinChat }]); setFranklinChat(prev => [...prev, { role: 'franklin', content: 'Chat saved!' }]); setFranklinLoading(false); return; }
    if (input.toLowerCase() === '/help') { setFranklinChat(prev => [...prev, { role: 'franklin', content: 'Commands:\n• /genesis <mission>\n• /workflow\n• /clear\n• /save\n• /help' }]); setFranklinLoading(false); return; }
    
    try {
      const response = await axios.post(`${API}/api/build-orchestrator/chat`, { message: input });
      setFranklinChat(prev => [...prev, { role: 'franklin', content: response.data.response || "I can help with that." }]);
    } catch (err) { setFranklinChat(prev => [...prev, { role: 'franklin', content: "Use /genesis <description> to start building." }]); }
    setFranklinLoading(false);
  };
  
  // Grok handler
  const handleGrokSend = async () => {
    if (!grokInput.trim() || grokLoading) return;
    const input = grokInput.trim();
    setGrokInput('');
    setGrokChat(prev => [...prev, { role: 'user', content: input }]);
    setGrokLoading(true);
    try {
      const response = await axios.post(`${API}/api/grok/chat`, { message: input, history: grokChat.slice(-6).map(m => ({ role: m.role === 'grok' ? 'assistant' : m.role, content: m.content })) });
      setGrokChat(prev => [...prev, { role: 'grok', content: response.data.response || "I'm analyzing..." }]);
    } catch (err) { setGrokChat(prev => [...prev, { role: 'grok', content: "I can help analyze that." }]); }
    setGrokLoading(false);
  };
  
  // Terminal handler
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
      <div className="fixed inset-x-0 top-[15%] flex justify-center pointer-events-none z-[1]">
        <h1 className="select-none" style={{ fontFamily: "'Orbitron', sans-serif", fontSize: 'clamp(4rem, 12vw, 11rem)', fontWeight: 600, letterSpacing: '0.35em', background: 'linear-gradient(180deg, rgba(100,100,100,0.18) 0%, rgba(140,140,140,0.22) 50%, rgba(100,100,100,0.18) 100%)', WebkitBackgroundClip: 'text', backgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>FRANKLIN</h1>
      </div>
      
      {/* TOP HEADER */}
      <div className="absolute top-0 left-0 right-0 h-8 z-50 bg-black/80 border-b border-white/10 flex items-center px-4">
        <div className="text-xs font-mono text-white/90 tracking-wider" style={{ fontFamily: "'Orbitron', sans-serif" }}>◈ FRANKLIN OS</div>
        <div className="flex-1" />
        <button onClick={() => { setFranklinChat([{ role: 'franklin', content: 'Cleared.' }]); setGrokChat([]); setTerminalOutput([{ type: 'system', text: '> Cleared' }]); }} className="mr-2 px-2 py-0.5 text-[8px] font-mono text-white/40 hover:text-white border border-white/10 rounded">🗑 CLEAR</button>
        <div className="flex items-center gap-3 text-[8px] font-mono">
          <span className="text-green-400 flex items-center gap-1"><span className="w-1 h-1 bg-green-400 rounded-full animate-pulse" />SENTINEL: ACTIVE</span>
          <span className="text-cyan-400">PQC: ONLINE</span>
          <span className="text-purple-400">AUDIT: 1 entries</span>
          <span className="text-green-400">AGENTS: 5</span>
        </div>
      </div>
      
      {/* ======================================================================== */}
      {/* LEFT COLUMN - FRANKLIN CHAT WINDOW (as you drew it) */}
      {/* ======================================================================== */}
      <div className="absolute top-8 bottom-32 left-0 z-30 bg-black/50 backdrop-blur-sm border-r border-white/10 flex flex-col" style={{ width: leftWidth }} data-testid="franklin-panel">
        {/* Header: FRANKLIN | COLLAPSE */}
        <div className="h-7 px-3 border-b border-white/10 flex items-center justify-between">
          <span className="text-[10px] font-mono text-cyan-400">◆ FRANKLIN</span>
          <span className="text-[7px] font-mono text-white/30">COLLAPSE</span>
        </div>
        {/* code area | 1 million context */}
        <div className="h-5 px-3 border-b border-white/5 flex items-center">
          <span className="text-[8px] font-mono text-white/40">code area</span>
          <span className="text-[8px] font-mono text-white/20 mx-2">|</span>
          <span className="text-[8px] font-mono text-white/40">1 million context</span>
        </div>
        {/* FRANKLIN ONBOARD CHAT */}
        <div className="h-5 px-3 border-b border-white/5 flex items-center justify-between">
          <span className="text-[8px] font-mono text-white/50">FRANKLIN ONBOARD CHAT</span>
          <span className="text-[6px] font-mono text-white/30 border border-white/10 px-1 rounded">⊞ EXPAND</span>
        </div>
        {/* Context Window */}
        <div className="px-3 py-0.5 text-[7px] font-mono text-white/20">Context Window</div>
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
        {/* 1 million context */}
        <div className="h-5 px-3 border-t border-white/5 flex items-center justify-center">
          <span className="text-[8px] font-mono text-cyan-400/60">1 million context</span>
        </div>
        {/* Resize handle */}
        <div onMouseDown={() => setIsResizingLeft(true)} className="absolute top-0 bottom-0 right-0 w-1 cursor-col-resize hover:bg-cyan-400/30" />
      </div>
      
      {/* FRANKLIN PROMPT */}
      <div className="absolute left-0 bottom-20 h-12 z-40 bg-black/70 border border-cyan-500/30 flex items-center px-3" style={{ width: leftWidth }} data-testid="franklin-prompt">
        <span className="text-[8px] font-mono text-cyan-400 mr-2">Franklin Prompt</span>
        <span className="text-cyan-400 mr-1">▶</span>
        <input type="text" value={franklinInput} onChange={(e) => setFranklinInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleFranklinSend()} placeholder="Type here..." className="flex-1 bg-transparent text-[10px] font-mono text-white placeholder-white/30 focus:outline-none" disabled={franklinLoading} />
      </div>
      
      {/* ======================================================================== */}
      {/* CENTER COLUMN - CODE AREA */}
      {/* ======================================================================== */}
      <div className="absolute top-8 bottom-32 z-20 flex flex-col" style={{ left: leftWidth, right: rightWidth }} data-testid="code-area">
        {/* Header: code area | 1 million context | untitled. */}
        <div className="h-6 bg-black/60 border-b border-white/10 flex items-center px-4 text-[8px] font-mono">
          <span className="text-cyan-400">code area</span>
          <span className="mx-2 text-white/20">|</span>
          <span className="text-white/40">1 million context</span>
          <span className="ml-auto text-white/30">untitled.</span>
        </div>
        {/* Tabs: front end | backend | database | deploy */}
        <div className="h-6 bg-black/50 border-b border-white/5 flex items-center px-4 gap-4">
          {['front end', 'backend', 'database', 'deploy'].map((tab, idx) => (
            <span key={tab} className={`text-[8px] font-mono cursor-pointer transition-colors ${idx === 0 ? 'text-cyan-400' : 'text-white/40 hover:text-white/70'}`}>{tab}</span>
          ))}
        </div>
        {/* Code content */}
        <div className="flex-1 bg-black/30 p-4 overflow-auto relative">
          <pre className="text-[10px] font-mono text-white/50 whitespace-pre-wrap">{codeContent}</pre>
          {/* ghost lines */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-3 text-[9px] font-mono text-cyan-400/30 pointer-events-none">
            <span>◄───</span><span>ghost lines</span><span>───►</span>
          </div>
        </div>
      </div>
      
      {/* ======================================================================== */}
      {/* RIGHT COLUMN - GROK with SPARKLY BRAIN (as you drew it) */}
      {/* ======================================================================== */}
      <div className="absolute top-8 bottom-32 right-0 z-30 bg-black/50 backdrop-blur-sm border-l border-white/10 flex flex-col" style={{ width: rightWidth }} data-testid="grok-panel">
        {/* Header: GROK | untitled. | ACADEMY */}
        <div className="h-7 px-3 border-b border-white/10 flex items-center justify-between">
          <span className="text-[10px] font-mono text-green-400">◆ GROK</span>
          <div className="flex items-center gap-2 text-[7px] font-mono text-white/30">
            <span>untitled.</span>
            <span>▶</span>
            <span>ACADEMY</span>
          </div>
        </div>
        
        {/* SPARKLY BRAIN - prominent as you drew */}
        <div className="h-32 border-b border-white/5 flex items-center justify-center relative">
          <div className="w-28 h-28">
            <NeuralBrain themeColor="#22c55e" isThinking={grokLoading} size="md" />
          </div>
          <span className="absolute bottom-1 right-2 text-[7px] font-mono text-white/20">sparkly brain</span>
        </div>
        
        {/* Grok responses */}
        <div ref={grokRef} className="flex-1 overflow-y-auto px-3 py-2 space-y-2 scrollbar-thin">
          {grokChat.length === 0 ? (
            <div className="text-[9px] font-mono text-white/30 text-center py-4">
              <p>Grok responses appear here...</p>
              <p className="mt-1">Use the input below to ask Grok</p>
            </div>
          ) : (
            grokChat.map((msg, idx) => (
              <div key={idx} className={`text-[10px] font-mono ${msg.role === 'user' ? 'text-green-400' : 'text-white/70'}`}>
                <span className="text-white/30 text-[8px]">◈ {msg.role.toUpperCase()}</span>
                <p className="mt-0.5 leading-relaxed">{msg.content}</p>
              </div>
            ))
          )}
          {grokLoading && <div className="text-green-400 text-[10px] flex items-center gap-1"><span className="animate-spin">◈</span> Grok thinking...</div>}
        </div>
        
        {/* 1 million context */}
        <div className="h-5 px-3 border-t border-white/5 flex items-center justify-center">
          <span className="text-[8px] font-mono text-green-400/60">1 million context</span>
        </div>
        
        {/* SAVED CHATS section (yellow box in your drawing) */}
        <div className="border-t border-white/10">
          <div className="px-3 py-1 text-[8px] font-mono text-white/40">saved chats</div>
          <div className="max-h-20 overflow-y-auto px-2 pb-1">
            {savedChats.length === 0 ? (
              <div className="text-[7px] font-mono text-white/20 text-center py-1">No saved chats. Use /save</div>
            ) : (
              savedChats.map(chat => (
                <div key={chat.id} className="py-0.5 px-2 text-[7px] font-mono text-white/40 hover:bg-white/5 rounded cursor-pointer truncate">{chat.title}</div>
              ))
            )}
          </div>
        </div>
        
        {/* Resize handle */}
        <div onMouseDown={() => setIsResizingRight(true)} className="absolute top-0 bottom-0 left-0 w-1 cursor-col-resize hover:bg-green-400/30" />
      </div>
      
      {/* GROK PROMPT */}
      <div className="absolute right-0 bottom-20 h-12 z-40 bg-black/70 border border-green-500/30 flex items-center px-3" style={{ width: rightWidth }} data-testid="grok-prompt">
        <span className="text-[8px] font-mono text-green-400 mr-2">Grok Prompt</span>
        <span className="text-green-400 mr-1">▶</span>
        <input type="text" value={grokInput} onChange={(e) => setGrokInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleGrokSend()} placeholder="Ask Grok anything..." className="flex-1 bg-transparent text-[10px] font-mono text-white placeholder-white/30 focus:outline-none" disabled={grokLoading} />
      </div>
      
      {/* ======================================================================== */}
      {/* BOTTOM ROW: CONNECTORS | TERMINAL | CI/CD + GROK RESPONSE */}
      {/* ======================================================================== */}
      
      {/* CONNECTORS - Bottom Left (as you drew) */}
      <div className="absolute left-0 bottom-0 h-20 z-40 bg-black/80 border-t border-r border-white/10 flex flex-col" style={{ width: leftWidth }}>
        <div className="px-3 py-1 text-[8px] font-mono text-red-400 border-b border-white/5">connectors</div>
        <div className="flex-1 overflow-y-auto px-2 py-1">
          <div className="text-[7px] font-mono text-white/40 py-0.5 px-1 hover:bg-white/5 rounded cursor-pointer">📁 Project Alpha</div>
          <div className="text-[7px] font-mono text-white/40 py-0.5 px-1 hover:bg-white/5 rounded cursor-pointer">📁 Franklin Demo</div>
        </div>
      </div>
      
      {/* TERMINAL - Bottom Center */}
      <div className="absolute bottom-0 h-20 z-40 bg-black/80 border-t border-white/10 flex flex-col" style={{ left: leftWidth, right: rightWidth }} data-testid="terminal">
        <div className="h-5 px-3 border-b border-white/5 flex items-center text-[8px] font-mono">
          <span className="text-purple-400">◆ TERMINAL</span>
          <span className="mx-3 text-white/20">|</span>
          <span className="text-white/30">SDK Cloud → Ubuntu/Linux → PowerShell</span>
        </div>
        <div ref={terminalRef} className="flex-1 overflow-y-auto px-3 py-1 scrollbar-thin">
          {terminalOutput.map((line, idx) => (
            <div key={idx} className={`text-[8px] font-mono ${line.type === 'error' ? 'text-red-400' : line.type === 'success' ? 'text-green-400' : line.type === 'system' ? 'text-purple-400' : line.type === 'cmd' ? 'text-cyan-400' : 'text-white/50'}`}>{line.text}</div>
          ))}
        </div>
        <div className="h-5 px-3 border-t border-white/5 flex items-center">
          <span className="text-purple-400 text-[7px] mr-2">/genesis mission...</span>
          <input type="text" value={terminalInput} onChange={(e) => setTerminalInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleTerminalSend()} placeholder="Enter command..." className="flex-1 bg-transparent text-[8px] font-mono text-white placeholder-white/30 focus:outline-none" />
        </div>
      </div>
      
      {/* CI/CD MCP SERVER TOOLS + GROK RESPONSE - Bottom Right (as you drew) */}
      <div className="absolute right-0 bottom-0 h-20 z-40 bg-black/80 border-t border-l border-white/10 flex flex-col" style={{ width: rightWidth }}>
        <div className="h-5 px-3 border-b border-white/5 flex items-center justify-between">
          <span className="text-[7px] font-mono text-yellow-400">◈ CI/CD - MCP SERVER TOOLS</span>
          <span className="text-[7px] font-mono text-green-400">GROK RESPONSE</span>
        </div>
        <div className="flex-1 flex">
          {/* CI/CD buttons */}
          <div className="w-1/2 p-1 grid grid-cols-2 gap-1">
            {['🚀 Deploy', '🔄 Build', '📊 Monitor', '🔧 Config'].map((tool, idx) => (
              <button key={idx} className="text-[6px] font-mono text-white/50 py-1 px-1 bg-white/5 hover:bg-white/10 rounded border border-white/10">{tool}</button>
            ))}
          </div>
          {/* Grok response area */}
          <div className="w-1/2 border-l border-white/10 p-1 overflow-y-auto">
            <div className="text-[7px] font-mono text-white/30">Grok responses...</div>
            {grokChat.slice(-2).map((msg, idx) => (
              <div key={idx} className="text-[6px] font-mono text-white/40 truncate py-0.5">{msg.content?.slice(0, 30)}...</div>
            ))}
          </div>
        </div>
        <div className="px-2 py-0.5 text-[6px] font-mono text-white/20 text-right">SM Context Window</div>
      </div>
      
      {/* Made with Emergent */}
      <div className="fixed bottom-1 left-1/2 -translate-x-1/2 z-50 text-[7px] font-mono text-white/20 flex items-center gap-1">
        <span className="text-cyan-400">◎</span> Made with Emergent
      </div>
      
      {/* Workflow button */}
      <button onClick={() => onNavigate(PAGES.WORKFLOW)} className="fixed top-1 right-4 z-50 px-2 py-0.5 text-[8px] font-mono text-purple-400 hover:bg-purple-500/20 border border-purple-500/30 rounded">◈ WORKFLOW</button>
      
      <style>{`.scrollbar-thin::-webkit-scrollbar { width: 3px; } .scrollbar-thin::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); }`}</style>
    </div>
  );
};

// ============================================================================
// MAIN APP
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
  
  if (currentPage === PAGES.LANDING) return <LandingPage onEnterApp={() => handleNavigate(PAGES.IDE)} />;
  if (currentPage === PAGES.WORKFLOW) return <ElectricWorkflowPage onBack={() => handleNavigate(PAGES.IDE)} workflowNodes={workflowNodes} workflowEdges={workflowEdges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} />;
  return <IDEPage onNavigate={handleNavigate} />;
}

export default App;
