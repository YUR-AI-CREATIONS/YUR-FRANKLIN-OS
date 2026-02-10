import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactFlow, { Background, Controls, useNodesState, useEdgesState, addEdge, MarkerType } from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';
import { LandingPage } from './components/LandingPage';
import NeuralBrain from './components/NeuralBrain';
import './App.css';

const API = process.env.REACT_APP_BACKEND_URL || '';
const PAGES = { LANDING: 'landing', IDE: 'ide', WORKFLOW: 'workflow' };

// GALACTIC BACKGROUND
const GalacticBackground = () => {
  const canvasRef = useRef(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationId, time = 0, stars = [];
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      stars = [];
      for (let i = 0; i < 100; i++) stars.push({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, size: Math.random() * 1.5 + 0.5, speed: Math.random() * 2 + 0.5, phase: Math.random() * Math.PI * 2 });
    };
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      stars.forEach(star => {
        const twinkle = Math.sin(time * star.speed * 0.05 + star.phase) * 0.5 + 0.5;
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size * (twinkle * 0.4 + 0.6), 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${twinkle * 0.8 + 0.2})`;
        ctx.fill();
      });
      time++;
      animationId = requestAnimationFrame(draw);
    };
    resize(); draw();
    window.addEventListener('resize', resize);
    return () => { cancelAnimationFrame(animationId); window.removeEventListener('resize', resize); };
  }, []);
  return <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none" />;
};

// WORKFLOW PAGE
const ElectricWorkflowPage = ({ onBack, workflowNodes, workflowEdges, onNodesChange, onEdgesChange }) => {
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([{ role: 'system', content: 'Workflow initialized.' }]);
  const [isProcessing, setIsProcessing] = useState(false);
  const chatRef = useRef(null);
  useEffect(() => { if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight; }, [chatHistory]);
  const onConnect = useCallback((params) => onEdgesChange((eds) => addEdge({ ...params, animated: true, style: { stroke: '#00ff88', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#00ff88' } }, eds)), [onEdgesChange]);
  const handleChatSend = async () => {
    if (!chatInput.trim() || isProcessing) return;
    setChatHistory(prev => [...prev, { role: 'user', content: chatInput }]);
    setChatInput(''); setIsProcessing(true);
    try {
      const res = await axios.post(`${API}/api/grok/chat`, { message: chatInput, history: chatHistory.slice(-6) });
      if (res.data.response) setChatHistory(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    } catch { setChatHistory(prev => [...prev, { role: 'assistant', content: 'I can help with that.' }]); }
    setIsProcessing(false);
  };
  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative">
      <GalacticBackground />
      <div className="absolute top-0 left-0 right-0 h-14 z-50 bg-black/80 border-b border-white/10 flex items-center justify-center">
        <button onClick={onBack} className="absolute left-4 px-4 py-2 text-sm font-mono text-white/70 hover:text-white" data-testid="back-to-ide">◀ BACK TO IDE</button>
        <h1 className="text-xl font-mono tracking-widest" style={{ fontFamily: "'Orbitron', sans-serif" }}>◈ ELECTRIC WORKFLOW</h1>
      </div>
      <div className={`absolute top-14 bottom-14 z-40 bg-black/90 border-r border-white/10 transition-all ${leftOpen ? 'left-0 w-80' : '-left-80 w-80'}`}>
        <button onClick={() => setLeftOpen(!leftOpen)} className="absolute -right-10 top-1/2 -translate-y-1/2 w-10 h-20 bg-black border border-white/10 rounded-r-lg flex items-center justify-center text-white/50 hover:text-white text-lg">{leftOpen ? '◀' : '▶'}</button>
        <div className="p-4 h-full flex flex-col">
          <div className="text-sm font-mono text-white/50 mb-4">◆ CHAT RESPONSE</div>
          <div ref={chatRef} className="flex-1 overflow-y-auto space-y-4">
            {chatHistory.map((msg, idx) => <div key={idx} className={`text-sm font-mono ${msg.role === 'user' ? 'text-cyan-400' : 'text-white/80'}`}><span className="text-white/40 text-xs">[{msg.role.toUpperCase()}]</span><p className="mt-1">{msg.content}</p></div>)}
          </div>
        </div>
      </div>
      <div className={`absolute top-14 bottom-14 z-40 bg-black/90 border-l border-white/10 transition-all ${rightOpen ? 'right-0 w-80' : '-right-80 w-80'}`}>
        <button onClick={() => setRightOpen(!rightOpen)} className="absolute -left-10 top-1/2 -translate-y-1/2 w-10 h-20 bg-black border border-white/10 rounded-l-lg flex items-center justify-center text-white/50 hover:text-white text-lg">{rightOpen ? '▶' : '◀'}</button>
        <div className="p-4 h-full flex flex-col">
          <div className="text-sm font-mono text-white/50 mb-4">◆ CONTROLS</div>
          <div className="space-y-3">{['Specification', 'Architecture', 'Implementation', 'Quality', 'Certification'].map((s, i) => <div key={s} className="flex items-center gap-3"><div className={`w-4 h-4 rounded-full ${i < 2 ? 'bg-green-400' : 'bg-white/20'}`} /><span className="text-sm font-mono text-white/60">{s}</span></div>)}</div>
          <div className="mt-auto space-y-3">
            <button className="w-full py-3 text-sm font-mono bg-green-500/20 border border-green-500/30 rounded-lg text-green-400">▶ RUN WORKFLOW</button>
            <button className="w-full py-3 text-sm font-mono bg-white/5 border border-white/10 rounded-lg text-white/60">⟳ RESET</button>
          </div>
        </div>
      </div>
      <div className={`absolute top-14 bottom-14 z-10 transition-all ${leftOpen ? 'left-80' : 'left-0'} ${rightOpen ? 'right-80' : 'right-0'}`}>
        <ReactFlow nodes={workflowNodes} edges={workflowEdges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} fitView className="!bg-transparent">
          <Background color="rgba(255,255,255,0.03)" gap={40} />
          <Controls className="!bg-black/70 !border-white/20" />
        </ReactFlow>
      </div>
      <div className="absolute bottom-0 left-0 right-0 h-14 z-40 bg-black/90 border-t border-white/10 flex items-center px-6">
        <input type="text" value={chatInput} onChange={(e) => setChatInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleChatSend()} placeholder="Ask about workflow..." className="flex-1 bg-transparent text-sm font-mono text-white placeholder-white/30 focus:outline-none" />
        <button onClick={handleChatSend} className="px-4 py-2 text-sm font-mono text-cyan-400">SEND ▶</button>
      </div>
    </div>
  );
};

// IDE PAGE - PROPER PROPORTIONS AND READABLE TEXT
const IDEPage = ({ onNavigate }) => {
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
  const [terminalOutput, setTerminalOutput] = useState([{ type: 'system', text: '> FRANKLIN OS Terminal v2.0' }, { type: 'info', text: '> Ready...' }]);
  const [savedChats, setSavedChats] = useState(() => {
    const saved = localStorage.getItem('saved_chats_v2');
    return saved ? JSON.parse(saved) : [];
  });
  const [franklinLoading, setFranklinLoading] = useState(false);
  const [grokLoading, setGrokLoading] = useState(false);
  const franklinRef = useRef(null);
  const grokRef = useRef(null);
  const terminalRef = useRef(null);

  useEffect(() => { localStorage.setItem('franklin_chat_v2', JSON.stringify(franklinChat.slice(-50))); }, [franklinChat]);
  useEffect(() => { localStorage.setItem('grok_chat_v2', JSON.stringify(grokChat.slice(-50))); }, [grokChat]);
  useEffect(() => { localStorage.setItem('saved_chats_v2', JSON.stringify(savedChats.slice(-20))); }, [savedChats]);
  useEffect(() => { if (franklinRef.current) franklinRef.current.scrollTop = franklinRef.current.scrollHeight; }, [franklinChat]);
  useEffect(() => { if (grokRef.current) grokRef.current.scrollTop = grokRef.current.scrollHeight; }, [grokChat]);
  useEffect(() => { if (terminalRef.current) terminalRef.current.scrollTop = terminalRef.current.scrollHeight; }, [terminalOutput]);

  const addTerminal = (text, type = 'info') => setTerminalOutput(prev => [...prev, { type, text: `> ${text}` }]);

  const handleFranklinSend = async () => {
    if (!franklinInput.trim() || franklinLoading) return;
    const input = franklinInput.trim();
    setFranklinInput('');
    setFranklinChat(prev => [...prev, { role: 'user', content: input }]);
    setFranklinLoading(true);
    if (input.toLowerCase().startsWith('/genesis ')) {
      const mission = input.replace(/^\/genesis\s+/i, '');
      addTerminal(`GENESIS: ${mission}`, 'system');
      setFranklinChat(prev => [...prev, { role: 'franklin', content: `Initiating build: "${mission}"` }]);
      try {
        const res = await axios.post(`${API}/api/build-orchestrator/build`, { mission });
        if (res.data.output) res.data.output.forEach(e => { addTerminal(`[${e.phase}] ${e.message}`, e.type || 'info'); if (e.phase.toLowerCase().includes('grok')) setGrokChat(prev => [...prev, { role: 'grok', content: `[${e.phase}] ${e.message}` }]); });
        if (res.data.success) addTerminal('BUILD COMPLETE ✓', 'success');
      } catch (err) { addTerminal(`Error: ${err.message}`, 'error'); }
      setFranklinLoading(false); return;
    }
    if (input.toLowerCase() === '/workflow') { onNavigate(PAGES.WORKFLOW); setFranklinLoading(false); return; }
    if (input.toLowerCase() === '/clear') { setFranklinChat([{ role: 'franklin', content: 'Cleared.' }]); setGrokChat([]); setTerminalOutput([{ type: 'system', text: '> Cleared' }]); setFranklinLoading(false); return; }
    if (input.toLowerCase() === '/save') { setSavedChats(prev => [...prev, { id: Date.now(), title: franklinChat[1]?.content?.slice(0, 25) + '...' || 'Chat', messages: franklinChat }]); setFranklinChat(prev => [...prev, { role: 'franklin', content: 'Saved!' }]); setFranklinLoading(false); return; }
    try {
      const res = await axios.post(`${API}/api/build-orchestrator/chat`, { message: input });
      setFranklinChat(prev => [...prev, { role: 'franklin', content: res.data.response || "I can help." }]);
    } catch { setFranklinChat(prev => [...prev, { role: 'franklin', content: "Use /genesis <desc> to build." }]); }
    setFranklinLoading(false);
  };

  const handleGrokSend = async () => {
    if (!grokInput.trim() || grokLoading) return;
    const input = grokInput.trim();
    setGrokInput('');
    setGrokChat(prev => [...prev, { role: 'user', content: input }]);
    setGrokLoading(true);
    try {
      const res = await axios.post(`${API}/api/grok/chat`, { message: input, history: grokChat.slice(-6).map(m => ({ role: m.role === 'grok' ? 'assistant' : m.role, content: m.content })) });
      setGrokChat(prev => [...prev, { role: 'grok', content: res.data.response || "Analyzing..." }]);
    } catch { setGrokChat(prev => [...prev, { role: 'grok', content: "I can help analyze that." }]); }
    setGrokLoading(false);
  };

  const handleTerminalSend = () => {
    if (!terminalInput.trim()) return;
    const input = terminalInput.trim();
    setTerminalInput('');
    addTerminal(input, 'cmd');
    if (input === 'clear') setTerminalOutput([{ type: 'system', text: '> Cleared' }]);
    else if (input === 'status') { addTerminal('FRANKLIN: Online', 'success'); addTerminal('GROK: Connected', 'success'); }
  };

  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="franklin-os">
      <GalacticBackground />
      
      {/* GHOST FRANKLIN */}
      <div className="fixed inset-0 flex items-center justify-center pointer-events-none z-[1]">
        <h1 className="select-none" style={{ fontFamily: "'Orbitron', sans-serif", fontSize: '12vw', fontWeight: 600, letterSpacing: '0.3em', color: 'rgba(80,80,80,0.15)' }}>FRANKLIN</h1>
      </div>
      
      {/* HEADER */}
      <div className="absolute top-0 left-0 right-0 h-12 z-50 bg-black/90 border-b border-white/20 flex items-center px-6">
        <span className="text-base font-mono text-white tracking-wider" style={{ fontFamily: "'Orbitron', sans-serif" }}>◈ FRANKLIN OS</span>
        <div className="flex-1" />
        <div className="flex items-center gap-6 text-xs font-mono">
          <span className="text-green-400 flex items-center gap-2"><span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />SENTINEL: ACTIVE</span>
          <span className="text-cyan-400">PQC: ONLINE</span>
          <span className="text-purple-400">AUDIT: 1 entries</span>
          <span className="text-green-400">AGENTS: 5</span>
        </div>
      </div>

      {/* MAIN CONTENT - 3 COLUMNS */}
      <div className="absolute top-12 bottom-0 left-0 right-0 flex">
        
        {/* LEFT COLUMN - FRANKLIN (25% width) */}
        <div className="w-1/4 min-w-[300px] flex flex-col border-r border-white/20 bg-black/60">
          {/* Header */}
          <div className="h-10 px-4 border-b border-white/20 flex items-center justify-between">
            <span className="text-sm font-mono text-cyan-400 font-semibold">◆ FRANKLIN</span>
            <span className="text-xs font-mono text-white/40">COLLAPSE</span>
          </div>
          {/* Subheader */}
          <div className="h-8 px-4 border-b border-white/10 flex items-center">
            <span className="text-xs font-mono text-white/50">code area</span>
            <span className="text-xs font-mono text-white/30 mx-2">|</span>
            <span className="text-xs font-mono text-white/50">1 million context</span>
          </div>
          {/* FRANKLIN ONBOARD CHAT */}
          <div className="h-8 px-4 border-b border-white/10 flex items-center justify-between">
            <span className="text-xs font-mono text-white/60">FRANKLIN ONBOARD CHAT</span>
            <span className="text-xs font-mono text-white/40 border border-white/20 px-2 py-0.5 rounded">⊞ EXPAND</span>
          </div>
          {/* Context Window label */}
          <div className="px-4 py-1 text-xs font-mono text-white/30">Context Window</div>
          {/* Chat */}
          <div ref={franklinRef} className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
            {franklinChat.map((msg, idx) => (
              <div key={idx}>
                <span className="text-xs font-mono text-white/40">◈ {msg.role.toUpperCase()}</span>
                <p className={`text-sm font-mono mt-1 leading-relaxed ${msg.role === 'user' ? 'text-cyan-400' : 'text-white/80'}`}>{msg.content}</p>
              </div>
            ))}
            {franklinLoading && <div className="text-purple-400 text-sm flex items-center gap-2"><span className="animate-spin">◈</span> Processing...</div>}
          </div>
          {/* 1 million context */}
          <div className="h-8 px-4 border-t border-white/10 flex items-center justify-center">
            <span className="text-xs font-mono text-cyan-400/70">1 million context</span>
          </div>
          {/* Franklin Prompt */}
          <div className="h-14 px-4 border-t border-cyan-500/40 bg-black/80 flex items-center gap-3">
            <span className="text-sm font-mono text-cyan-400">Franklin Prompt</span>
            <span className="text-cyan-400 text-lg">▶</span>
            <input type="text" value={franklinInput} onChange={(e) => setFranklinInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleFranklinSend()} placeholder="Type here..." className="flex-1 bg-transparent text-sm font-mono text-white placeholder-white/40 focus:outline-none" data-testid="franklin-prompt" />
          </div>
          {/* Connectors */}
          <div className="h-24 border-t border-white/20 bg-black/80">
            <div className="px-4 py-2 text-xs font-mono text-red-400 border-b border-white/10">connectors</div>
            <div className="px-4 py-2 space-y-1">
              <div className="text-sm font-mono text-white/60 hover:text-white cursor-pointer">📁 Project Alpha</div>
              <div className="text-sm font-mono text-white/60 hover:text-white cursor-pointer">📁 Franklin Demo</div>
            </div>
          </div>
        </div>

        {/* CENTER COLUMN - CODE AREA (50% width) */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="h-10 px-6 border-b border-white/20 bg-black/60 flex items-center">
            <span className="text-sm font-mono text-cyan-400">code area</span>
            <span className="text-sm font-mono text-white/30 mx-3">|</span>
            <span className="text-sm font-mono text-white/50">1 million context</span>
            <span className="ml-auto text-sm font-mono text-white/40">untitled.</span>
          </div>
          {/* Tabs */}
          <div className="h-10 px-6 border-b border-white/10 bg-black/50 flex items-center gap-8">
            <span className="text-sm font-mono text-cyan-400 cursor-pointer">front end</span>
            <span className="text-sm font-mono text-white/50 hover:text-white cursor-pointer">backend</span>
            <span className="text-sm font-mono text-white/50 hover:text-white cursor-pointer">database</span>
            <span className="text-sm font-mono text-white/50 hover:text-white cursor-pointer">deploy</span>
          </div>
          {/* Code content */}
          <div className="flex-1 bg-black/40 p-6 overflow-auto relative">
            <pre className="text-sm font-mono text-white/60 leading-relaxed">// Your code will appear here...{'\n'}// Use /genesis &lt;mission&gt; to start building</pre>
            {/* Ghost lines */}
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-4 text-sm font-mono text-cyan-400/40">
              <span>◄────</span><span>ghost lines</span><span>────►</span>
            </div>
          </div>
          {/* Terminal */}
          <div className="h-32 border-t border-white/20 bg-black/80 flex flex-col">
            <div className="h-8 px-6 border-b border-white/10 flex items-center">
              <span className="text-sm font-mono text-purple-400">◆ TERMINAL</span>
              <span className="text-sm font-mono text-white/30 mx-4">|</span>
              <span className="text-xs font-mono text-white/40">SDK Cloud → Ubuntu/Linux → PowerShell</span>
            </div>
            <div ref={terminalRef} className="flex-1 overflow-y-auto px-6 py-2">
              {terminalOutput.map((line, idx) => (
                <div key={idx} className={`text-sm font-mono ${line.type === 'error' ? 'text-red-400' : line.type === 'success' ? 'text-green-400' : line.type === 'system' ? 'text-purple-400' : line.type === 'cmd' ? 'text-cyan-400' : 'text-white/60'}`}>{line.text}</div>
              ))}
            </div>
            <div className="h-8 px-6 border-t border-white/10 flex items-center">
              <span className="text-sm font-mono text-purple-400 mr-3">/genesis mission...</span>
              <input type="text" value={terminalInput} onChange={(e) => setTerminalInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleTerminalSend()} placeholder="Enter command..." className="flex-1 bg-transparent text-sm font-mono text-white placeholder-white/40 focus:outline-none" />
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN - GROK (25% width) */}
        <div className="w-1/4 min-w-[300px] flex flex-col border-l border-white/20 bg-black/60">
          {/* Header */}
          <div className="h-10 px-4 border-b border-white/20 flex items-center justify-between">
            <span className="text-sm font-mono text-green-400 font-semibold">◆ GROK</span>
            <div className="flex items-center gap-2 text-xs font-mono text-white/40">
              <span>untitled.</span>
              <span>▶</span>
              <span>ACADEMY</span>
            </div>
          </div>
          {/* SPARKLY BRAIN */}
          <div className="h-40 border-b border-white/10 flex items-center justify-center relative">
            <div className="w-32 h-32">
              <NeuralBrain themeColor="#22c55e" isThinking={grokLoading} size="lg" />
            </div>
            <span className="absolute bottom-2 right-3 text-xs font-mono text-white/30">sparkly brain</span>
          </div>
          {/* Grok chat */}
          <div ref={grokRef} className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
            {grokChat.length === 0 ? (
              <div className="text-sm font-mono text-white/40 text-center py-8">
                <p>Grok responses appear here...</p>
                <p className="mt-2">Use the input below to ask Grok</p>
              </div>
            ) : (
              grokChat.map((msg, idx) => (
                <div key={idx}>
                  <span className="text-xs font-mono text-white/40">◈ {msg.role.toUpperCase()}</span>
                  <p className={`text-sm font-mono mt-1 leading-relaxed ${msg.role === 'user' ? 'text-green-400' : 'text-white/80'}`}>{msg.content}</p>
                </div>
              ))
            )}
            {grokLoading && <div className="text-green-400 text-sm flex items-center gap-2"><span className="animate-spin">◈</span> Grok thinking...</div>}
          </div>
          {/* 1 million context */}
          <div className="h-8 px-4 border-t border-white/10 flex items-center justify-center">
            <span className="text-xs font-mono text-green-400/70">1 million context</span>
          </div>
          {/* Saved chats */}
          <div className="h-20 border-t border-white/20">
            <div className="px-4 py-2 text-xs font-mono text-white/50">saved chats</div>
            <div className="px-4 overflow-y-auto max-h-12">
              {savedChats.length === 0 ? (
                <div className="text-xs font-mono text-white/30">No saved chats. Use /save</div>
              ) : (
                savedChats.map(c => <div key={c.id} className="text-sm font-mono text-white/50 truncate cursor-pointer hover:text-white">{c.title}</div>)
              )}
            </div>
          </div>
          {/* Grok Prompt */}
          <div className="h-14 px-4 border-t border-green-500/40 bg-black/80 flex items-center gap-3">
            <span className="text-sm font-mono text-green-400">Grok Prompt</span>
            <span className="text-green-400 text-lg">▶</span>
            <input type="text" value={grokInput} onChange={(e) => setGrokInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleGrokSend()} placeholder="Ask Grok anything..." className="flex-1 bg-transparent text-sm font-mono text-white placeholder-white/40 focus:outline-none" data-testid="grok-prompt" />
          </div>
          {/* CI/CD + Grok Response */}
          <div className="h-24 border-t border-white/20 bg-black/80 flex">
            <div className="w-1/2 p-2 border-r border-white/10">
              <div className="text-xs font-mono text-yellow-400 mb-2">◈ CI/CD - MCP SERVER TOOLS</div>
              <div className="grid grid-cols-2 gap-1">
                {['🚀 Deploy', '🔄 Build', '📊 Monitor', '🔧 Config'].map(t => <button key={t} className="text-xs font-mono text-white/60 py-1 bg-white/5 hover:bg-white/10 rounded">{t}</button>)}
              </div>
            </div>
            <div className="w-1/2 p-2">
              <div className="text-xs font-mono text-green-400 mb-1">GROK RESPONSE</div>
              <div className="text-xs font-mono text-white/40">Grok responses...</div>
            </div>
          </div>
        </div>
      </div>

      {/* Workflow button */}
      <button onClick={() => onNavigate(PAGES.WORKFLOW)} className="fixed top-2 right-6 z-50 px-3 py-1 text-xs font-mono text-purple-400 border border-purple-500/40 rounded hover:bg-purple-500/20">◈ WORKFLOW</button>
      
      {/* Made with Emergent */}
      <div className="fixed bottom-2 right-6 z-50 text-xs font-mono text-white/30">◎ Made with Emergent</div>
    </div>
  );
};

// MAIN APP
function App() {
  const [currentPage, setCurrentPage] = useState(PAGES.LANDING);
  const [workflowNodes,, onNodesChange] = useNodesState([
    { id: '1', position: { x: 250, y: 50 }, data: { label: 'Genesis' } },
    { id: '2', position: { x: 100, y: 150 }, data: { label: 'Architect' } },
    { id: '3', position: { x: 400, y: 150 }, data: { label: 'Implementer' } },
    { id: '4', position: { x: 250, y: 250 }, data: { label: 'Quality' } },
  ]);
  const [workflowEdges,, onEdgesChange] = useEdgesState([
    { id: 'e1-2', source: '1', target: '2', animated: true },
    { id: 'e1-3', source: '1', target: '3', animated: true },
    { id: 'e2-4', source: '2', target: '4', animated: true },
    { id: 'e3-4', source: '3', target: '4', animated: true },
  ]);
  if (currentPage === PAGES.LANDING) return <LandingPage onEnterApp={() => setCurrentPage(PAGES.IDE)} />;
  if (currentPage === PAGES.WORKFLOW) return <ElectricWorkflowPage onBack={() => setCurrentPage(PAGES.IDE)} workflowNodes={workflowNodes} workflowEdges={workflowEdges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} />;
  return <IDEPage onNavigate={setCurrentPage} />;
}

export default App;
