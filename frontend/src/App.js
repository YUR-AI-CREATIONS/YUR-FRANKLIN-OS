import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactFlow, { Background, Controls, useNodesState, useEdgesState, addEdge, MarkerType } from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';
import { LandingPage } from './components/LandingPage';
import NeuralBrain from './components/NeuralBrain';
import './App.css';

const API = process.env.REACT_APP_BACKEND_URL || '';
const PAGES = { LANDING: 'landing', IDE: 'ide', WORKFLOW: 'workflow' };

// Genesis Pipeline Stages
const GENESIS_STAGES = [
  { id: 'inception', name: 'INCEPTION', desc: 'Requirement validation' },
  { id: 'specification', name: 'SPECIFICATION', desc: 'Detailed spec generation' },
  { id: 'architecture', name: 'ARCHITECTURE', desc: 'System design' },
  { id: 'construction', name: 'CONSTRUCTION', desc: 'Code generation' },
  { id: 'validation', name: 'VALIDATION', desc: 'Testing' },
  { id: 'evolution', name: 'EVOLUTION', desc: 'Optimization' },
  { id: 'deployment', name: 'DEPLOYMENT', desc: 'Deployment prep' },
  { id: 'governance', name: 'GOVERNANCE', desc: 'Compliance check' }
];

// Quality Gate Dimensions
const QUALITY_DIMENSIONS = [
  { name: 'Completeness', weight: 1.5, score: 0 },
  { name: 'Coherence', weight: 1.3, score: 0 },
  { name: 'Correctness', weight: 1.5, score: 0 },
  { name: 'Security', weight: 1.4, score: 0 },
  { name: 'Performance', weight: 1.0, score: 0 },
  { name: 'Scalability', weight: 1.0, score: 0 },
  { name: 'Maintainability', weight: 1.1, score: 0 },
  { name: 'Compliance', weight: 1.2, score: 0 }
];

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
      for (let i = 0; i < 150; i++) stars.push({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, size: Math.random() * 1.5 + 0.5, speed: Math.random() * 2 + 0.5, phase: Math.random() * Math.PI * 2 });
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

// ============================================================================
// ELECTRIC WORKFLOW PAGE - Full Genesis Pipeline
// ============================================================================
const ElectricWorkflowPage = ({ onBack }) => {
  const [currentStage, setCurrentStage] = useState(0);
  const [convergence, setConvergence] = useState(0);
  const [qualityScores, setQualityScores] = useState(QUALITY_DIMENSIONS);
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'system', content: 'Genesis Pipeline initialized. Ready to build your project.' },
    { role: 'system', content: 'Enter your requirements or use /genesis <description> to start.' }
  ]);
  const [terminalOutput, setTerminalOutput] = useState([
    { type: 'system', text: '> GENESIS ENGINE v2.0 ONLINE' },
    { type: 'info', text: '> Ouroboros Loop: STANDBY' },
    { type: 'info', text: '> Quality Gates: 8 DIMENSIONS READY' },
    { type: 'success', text: '> System ready for project initialization' }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [ouroborosActive, setOuroborosActive] = useState(false);
  const chatRef = useRef(null);
  const terminalRef = useRef(null);

  // Workflow nodes for ReactFlow - 8 stage pipeline
  const initialNodes = [
    { id: 'inception', position: { x: 100, y: 100 }, data: { label: 'INCEPTION' }, style: { background: '#1a1a2e', border: '2px solid #00ff88', color: '#fff', padding: 20, borderRadius: 8, width: 140 } },
    { id: 'specification', position: { x: 300, y: 100 }, data: { label: 'SPECIFICATION' }, style: { background: '#1a1a2e', border: '2px solid #00d4ff', color: '#fff', padding: 20, borderRadius: 8, width: 140 } },
    { id: 'architecture', position: { x: 500, y: 100 }, data: { label: 'ARCHITECTURE' }, style: { background: '#1a1a2e', border: '2px solid #a855f7', color: '#fff', padding: 20, borderRadius: 8, width: 140 } },
    { id: 'construction', position: { x: 700, y: 100 }, data: { label: 'CONSTRUCTION' }, style: { background: '#1a1a2e', border: '2px solid #f59e0b', color: '#fff', padding: 20, borderRadius: 8, width: 140 } },
    { id: 'validation', position: { x: 100, y: 250 }, data: { label: 'VALIDATION' }, style: { background: '#1a1a2e', border: '2px solid #ef4444', color: '#fff', padding: 20, borderRadius: 8, width: 140 } },
    { id: 'evolution', position: { x: 300, y: 250 }, data: { label: 'EVOLUTION' }, style: { background: '#1a1a2e', border: '2px solid #22c55e', color: '#fff', padding: 20, borderRadius: 8, width: 140 } },
    { id: 'deployment', position: { x: 500, y: 250 }, data: { label: 'DEPLOYMENT' }, style: { background: '#1a1a2e', border: '2px solid #3b82f6', color: '#fff', padding: 20, borderRadius: 8, width: 140 } },
    { id: 'governance', position: { x: 700, y: 250 }, data: { label: 'GOVERNANCE' }, style: { background: '#1a1a2e', border: '2px solid #ec4899', color: '#fff', padding: 20, borderRadius: 8, width: 140 } },
    // Ouroboros center node
    { id: 'ouroboros', position: { x: 400, y: 400 }, data: { label: '∞ OUROBOROS' }, style: { background: '#0f0f23', border: '3px solid #00ff88', color: '#00ff88', padding: 25, borderRadius: '50%', width: 120, height: 120, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 'bold' } },
  ];

  const initialEdges = [
    { id: 'e1', source: 'inception', target: 'specification', animated: true, style: { stroke: '#00ff88' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'e2', source: 'specification', target: 'architecture', animated: true, style: { stroke: '#00d4ff' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'e3', source: 'architecture', target: 'construction', animated: true, style: { stroke: '#a855f7' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'e4', source: 'construction', target: 'validation', animated: true, style: { stroke: '#f59e0b' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'e5', source: 'validation', target: 'evolution', animated: true, style: { stroke: '#ef4444' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'e6', source: 'evolution', target: 'deployment', animated: true, style: { stroke: '#22c55e' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'e7', source: 'deployment', target: 'governance', animated: true, style: { stroke: '#3b82f6' }, markerEnd: { type: MarkerType.ArrowClosed } },
    // Ouroboros loop connections
    { id: 'e8', source: 'governance', target: 'ouroboros', animated: true, style: { stroke: '#00ff88', strokeDasharray: '5,5' }, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: 'e9', source: 'ouroboros', target: 'inception', animated: true, style: { stroke: '#00ff88', strokeDasharray: '5,5' }, markerEnd: { type: MarkerType.ArrowClosed } },
  ];

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => { if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight; }, [chatHistory]);
  useEffect(() => { if (terminalRef.current) terminalRef.current.scrollTop = terminalRef.current.scrollHeight; }, [terminalOutput]);

  const addTerminal = (text, type = 'info') => setTerminalOutput(prev => [...prev, { type, text: `> ${text}` }]);

  const runOuroborosLoop = () => {
    setOuroborosActive(true);
    addTerminal('OUROBOROS LOOP INITIATED', 'system');
    addTerminal('Target: 99% convergence', 'info');
    
    let conv = convergence;
    const interval = setInterval(() => {
      conv += Math.random() * 5 + 2;
      if (conv >= 99) {
        conv = 99;
        clearInterval(interval);
        setOuroborosActive(false);
        addTerminal('CONVERGENCE ACHIEVED: 99%', 'success');
        addTerminal('Frozen Spine: LOCKED', 'success');
        setChatHistory(prev => [...prev, { role: 'system', content: '✓ Ouroboros Loop complete. 99% convergence achieved. Frozen Spine locked.' }]);
      }
      setConvergence(conv);
      
      // Update quality scores
      setQualityScores(prev => prev.map(q => ({
        ...q,
        score: Math.min(100, q.score + Math.random() * 10)
      })));
    }, 500);
  };

  const handleChatSend = async () => {
    if (!chatInput.trim() || isProcessing) return;
    const input = chatInput.trim();
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: input }]);
    setIsProcessing(true);

    if (input.toLowerCase().startsWith('/genesis ')) {
      const mission = input.replace(/^\/genesis\s+/i, '');
      addTerminal(`PROJECT: ${mission}`, 'system');
      setChatHistory(prev => [...prev, { role: 'system', content: `Initializing Genesis Pipeline for: "${mission}"` }]);
      
      // Simulate pipeline progression
      for (let i = 0; i < GENESIS_STAGES.length; i++) {
        await new Promise(r => setTimeout(r, 800));
        setCurrentStage(i);
        addTerminal(`[${GENESIS_STAGES[i].name}] ${GENESIS_STAGES[i].desc}`, 'info');
        setChatHistory(prev => [...prev, { role: 'system', content: `Stage ${i + 1}/8: ${GENESIS_STAGES[i].name} - ${GENESIS_STAGES[i].desc}` }]);
        
        // Highlight current node
        setNodes(nds => nds.map(n => ({
          ...n,
          style: {
            ...n.style,
            boxShadow: n.id === GENESIS_STAGES[i].id ? '0 0 20px #00ff88' : 'none'
          }
        })));
      }
      
      addTerminal('PIPELINE COMPLETE', 'success');
      addTerminal('Ready for Ouroboros convergence loop', 'info');
      setChatHistory(prev => [...prev, { role: 'system', content: '✓ Genesis Pipeline complete. Click "RUN OUROBOROS" to achieve convergence.' }]);
      setIsProcessing(false);
      return;
    }

    if (input.toLowerCase() === '/quality') {
      setChatHistory(prev => [...prev, { role: 'system', content: '8-Dimensional Quality Gate Assessment:\n' + qualityScores.map(q => `• ${q.name}: ${q.score.toFixed(1)}% (${q.weight}x weight)`).join('\n') }]);
      setIsProcessing(false);
      return;
    }

    // Regular chat with Grok
    try {
      const res = await axios.post(`${API}/api/grok/chat`, { message: input, history: chatHistory.slice(-6) });
      setChatHistory(prev => [...prev, { role: 'grok', content: res.data.response || "I can help analyze that." }]);
    } catch {
      setChatHistory(prev => [...prev, { role: 'grok', content: "I'm here to assist with your project pipeline." }]);
    }
    setIsProcessing(false);
  };

  const onConnect = useCallback((params) => setEdges((eds) => addEdge({ ...params, animated: true, style: { stroke: '#00ff88' } }, eds)), [setEdges]);

  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="workflow-page">
      <GalacticBackground />
      
      {/* HEADER */}
      <div className="absolute top-0 left-0 right-0 h-14 z-50 bg-black/90 border-b border-white/20 flex items-center justify-between px-6">
        <button onClick={onBack} className="px-4 py-2 text-sm font-mono text-white/70 hover:text-white hover:bg-white/10 rounded flex items-center gap-2" data-testid="back-to-ide">
          ◀ BACK TO IDE
        </button>
        <div className="text-center">
          <h1 className="text-xl font-mono tracking-[0.2em] text-white" style={{ fontFamily: "'Orbitron', sans-serif" }}>
            ◈ ELECTRIC WORKFLOW
          </h1>
          <p className="text-xs text-white/50">GENESIS PIPELINE • OUROBOROS LOOP • QUALITY GATES</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm font-mono">
            <span className="text-white/50">Convergence:</span>
            <span className={`ml-2 ${convergence >= 99 ? 'text-green-400' : 'text-yellow-400'}`}>{convergence.toFixed(1)}%</span>
          </div>
          <div className={`w-3 h-3 rounded-full ${ouroborosActive ? 'bg-green-400 animate-pulse' : 'bg-white/30'}`} />
        </div>
      </div>

      {/* LEFT PANEL - Chat & Terminal */}
      <div className={`absolute top-14 bottom-0 z-40 bg-black/90 border-r border-white/20 transition-all duration-300 flex flex-col ${leftPanelOpen ? 'left-0 w-96' : '-left-96 w-96'}`}>
        <button onClick={() => setLeftPanelOpen(!leftPanelOpen)} className="absolute -right-10 top-1/2 -translate-y-1/2 w-10 h-20 bg-black/90 border border-white/20 rounded-r-lg flex items-center justify-center text-white/60 hover:text-white text-lg">
          {leftPanelOpen ? '◀' : '▶'}
        </button>
        
        {/* Chat Section */}
        <div className="flex-1 flex flex-col border-b border-white/20">
          <div className="h-10 px-4 border-b border-white/10 flex items-center">
            <span className="text-sm font-mono text-cyan-400">◆ GROK RESPONSE</span>
          </div>
          <div ref={chatRef} className="flex-1 overflow-y-auto p-4 space-y-3">
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={`text-sm font-mono ${msg.role === 'user' ? 'text-cyan-400' : msg.role === 'grok' ? 'text-green-400' : 'text-white/70'}`}>
                <span className="text-white/40 text-xs">[{msg.role.toUpperCase()}]</span>
                <p className="mt-1 whitespace-pre-wrap">{msg.content}</p>
              </div>
            ))}
            {isProcessing && <div className="text-purple-400 text-sm flex items-center gap-2"><span className="animate-spin">◈</span> Processing...</div>}
          </div>
        </div>
        
        {/* Terminal Section */}
        <div className="h-48 flex flex-col">
          <div className="h-8 px-4 border-b border-white/10 flex items-center">
            <span className="text-sm font-mono text-purple-400">◆ TERMINAL</span>
          </div>
          <div ref={terminalRef} className="flex-1 overflow-y-auto p-3">
            {terminalOutput.map((line, idx) => (
              <div key={idx} className={`text-xs font-mono ${line.type === 'error' ? 'text-red-400' : line.type === 'success' ? 'text-green-400' : line.type === 'system' ? 'text-purple-400' : 'text-white/60'}`}>{line.text}</div>
            ))}
          </div>
          <div className="h-10 px-4 border-t border-white/10 flex items-center gap-2">
            <span className="text-purple-400">▶</span>
            <input type="text" value={chatInput} onChange={(e) => setChatInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleChatSend()} placeholder="/genesis <project> or ask Grok..." className="flex-1 bg-transparent text-sm font-mono text-white placeholder-white/40 focus:outline-none" />
          </div>
        </div>
      </div>

      {/* RIGHT PANEL - Controls & Quality */}
      <div className={`absolute top-14 bottom-0 z-40 bg-black/90 border-l border-white/20 transition-all duration-300 flex flex-col ${rightPanelOpen ? 'right-0 w-80' : '-right-80 w-80'}`}>
        <button onClick={() => setRightPanelOpen(!rightPanelOpen)} className="absolute -left-10 top-1/2 -translate-y-1/2 w-10 h-20 bg-black/90 border border-white/20 rounded-l-lg flex items-center justify-center text-white/60 hover:text-white text-lg">
          {rightPanelOpen ? '▶' : '◀'}
        </button>
        
        {/* Stage Progress */}
        <div className="p-4 border-b border-white/20">
          <div className="text-sm font-mono text-white/60 mb-3">GENESIS PIPELINE STAGES</div>
          <div className="space-y-2">
            {GENESIS_STAGES.map((stage, idx) => (
              <div key={stage.id} className="flex items-center gap-3">
                <div className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] ${idx < currentStage ? 'bg-green-400 text-black' : idx === currentStage ? 'bg-cyan-400 animate-pulse text-black' : 'bg-white/20 text-white/40'}`}>
                  {idx < currentStage ? '✓' : idx + 1}
                </div>
                <span className={`text-sm font-mono ${idx <= currentStage ? 'text-white' : 'text-white/40'}`}>{stage.name}</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Quality Gates */}
        <div className="flex-1 p-4 overflow-y-auto">
          <div className="text-sm font-mono text-white/60 mb-3">8-DIMENSIONAL QUALITY GATES</div>
          <div className="space-y-3">
            {qualityScores.map(q => (
              <div key={q.name}>
                <div className="flex justify-between text-xs font-mono mb-1">
                  <span className="text-white/70">{q.name}</span>
                  <span className={q.score >= 80 ? 'text-green-400' : q.score >= 50 ? 'text-yellow-400' : 'text-white/40'}>{q.score.toFixed(0)}%</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div className={`h-full transition-all duration-500 ${q.score >= 80 ? 'bg-green-400' : q.score >= 50 ? 'bg-yellow-400' : 'bg-white/30'}`} style={{ width: `${q.score}%` }} />
                </div>
                <div className="text-[10px] text-white/30 mt-0.5">Weight: {q.weight}x</div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="p-4 border-t border-white/20 space-y-2">
          <button onClick={runOuroborosLoop} disabled={ouroborosActive} className={`w-full py-3 text-sm font-mono rounded-lg transition-all ${ouroborosActive ? 'bg-green-500/20 text-green-400 animate-pulse' : 'bg-green-500/30 text-green-400 hover:bg-green-500/40'} border border-green-500/40`}>
            {ouroborosActive ? '∞ CONVERGING...' : '▶ RUN OUROBOROS'}
          </button>
          <button onClick={() => { setCurrentStage(0); setConvergence(0); setQualityScores(QUALITY_DIMENSIONS); addTerminal('PIPELINE RESET', 'system'); }} className="w-full py-3 text-sm font-mono bg-white/5 border border-white/20 rounded-lg text-white/60 hover:bg-white/10">
            ⟳ RESET PIPELINE
          </button>
        </div>
      </div>

      {/* MAIN CANVAS - ReactFlow */}
      <div className={`absolute top-14 bottom-0 z-10 transition-all duration-300 ${leftPanelOpen ? 'left-96' : 'left-0'} ${rightPanelOpen ? 'right-80' : 'right-0'}`}>
        <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} fitView className="!bg-transparent">
          <Background color="rgba(0,255,136,0.03)" gap={50} />
          <Controls className="!bg-black/80 !border-white/20 !rounded-lg" />
        </ReactFlow>
        
        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-black/80 border border-white/20 rounded-lg p-4">
          <div className="text-xs font-mono text-white/60 mb-2">PIPELINE LEGEND</div>
          <div className="space-y-1 text-xs font-mono">
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded bg-green-400" /><span className="text-white/50">Completed</span></div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded bg-cyan-400 animate-pulse" /><span className="text-white/50">In Progress</span></div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded bg-white/20" /><span className="text-white/50">Pending</span></div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full border-2 border-green-400 border-dashed" /><span className="text-white/50">Ouroboros Loop</span></div>
          </div>
        </div>
      </div>

      {/* Made with Emergent */}
      <div className="fixed bottom-2 right-4 z-50 text-xs font-mono text-white/30">◎ Made with Emergent</div>
    </div>
  );
};

// ============================================================================
// IDE PAGE
// ============================================================================
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
      addTerminal(`Redirecting to Electric Workflow...`, 'system');
      setTimeout(() => onNavigate(PAGES.WORKFLOW), 500);
      setFranklinLoading(false);
      return;
    }
    if (input.toLowerCase() === '/workflow') { onNavigate(PAGES.WORKFLOW); setFranklinLoading(false); return; }
    if (input.toLowerCase() === '/clear') { setFranklinChat([{ role: 'franklin', content: 'Cleared.' }]); setGrokChat([]); setTerminalOutput([{ type: 'system', text: '> Cleared' }]); setFranklinLoading(false); return; }
    if (input.toLowerCase() === '/save') { setSavedChats(prev => [...prev, { id: Date.now(), title: franklinChat[1]?.content?.slice(0, 25) + '...' || 'Chat', messages: franklinChat }]); setFranklinChat(prev => [...prev, { role: 'franklin', content: 'Saved!' }]); setFranklinLoading(false); return; }
    try {
      const res = await axios.post(`${API}/api/build-orchestrator/chat`, { message: input });
      setFranklinChat(prev => [...prev, { role: 'franklin', content: res.data.response || "I can help." }]);
    } catch { setFranklinChat(prev => [...prev, { role: 'franklin', content: "Use /genesis <desc> or /workflow to start building." }]); }
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
    else if (input === 'workflow' || input === '/workflow') onNavigate(PAGES.WORKFLOW);
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
        <button onClick={() => onNavigate(PAGES.WORKFLOW)} className="mr-4 px-4 py-1.5 text-sm font-mono text-purple-400 border border-purple-500/50 rounded hover:bg-purple-500/20 transition-all">
          ◈ ELECTRIC WORKFLOW
        </button>
        <div className="flex items-center gap-6 text-xs font-mono">
          <span className="text-green-400 flex items-center gap-2"><span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />SENTINEL: ACTIVE</span>
          <span className="text-cyan-400">PQC: ONLINE</span>
          <span className="text-purple-400">AGENTS: 5</span>
        </div>
      </div>

      {/* MAIN CONTENT - 3 COLUMNS */}
      <div className="absolute top-12 bottom-0 left-0 right-0 flex">
        
        {/* LEFT COLUMN - FRANKLIN */}
        <div className="w-1/4 min-w-[300px] flex flex-col border-r border-white/20 bg-black/60">
          <div className="h-10 px-4 border-b border-white/20 flex items-center justify-between">
            <span className="text-sm font-mono text-cyan-400 font-semibold">◆ FRANKLIN</span>
            <span className="text-xs font-mono text-white/40">1M context</span>
          </div>
          <div ref={franklinRef} className="flex-1 overflow-y-auto p-4 space-y-4">
            {franklinChat.map((msg, idx) => (
              <div key={idx}>
                <span className="text-xs font-mono text-white/40">◈ {msg.role.toUpperCase()}</span>
                <p className={`text-sm font-mono mt-1 leading-relaxed ${msg.role === 'user' ? 'text-cyan-400' : 'text-white/80'}`}>{msg.content}</p>
              </div>
            ))}
            {franklinLoading && <div className="text-purple-400 text-sm flex items-center gap-2"><span className="animate-spin">◈</span> Processing...</div>}
          </div>
          <div className="h-14 px-4 border-t border-cyan-500/40 bg-black/80 flex items-center gap-3">
            <span className="text-sm font-mono text-cyan-400">Franklin ▶</span>
            <input type="text" value={franklinInput} onChange={(e) => setFranklinInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleFranklinSend()} placeholder="Type here..." className="flex-1 bg-transparent text-sm font-mono text-white placeholder-white/40 focus:outline-none" data-testid="franklin-prompt" />
          </div>
          <div className="h-24 border-t border-white/20 bg-black/80 p-3">
            <div className="text-xs font-mono text-red-400 mb-2">CONNECTORS</div>
            <div className="space-y-1">
              <div className="text-sm font-mono text-white/60 hover:text-white cursor-pointer">📁 Project Alpha</div>
              <div className="text-sm font-mono text-white/60 hover:text-white cursor-pointer">📁 Franklin Demo</div>
            </div>
          </div>
        </div>

        {/* CENTER COLUMN - CODE AREA */}
        <div className="flex-1 flex flex-col">
          <div className="h-10 px-6 border-b border-white/20 bg-black/60 flex items-center">
            <span className="text-sm font-mono text-cyan-400">code area</span>
            <span className="text-sm font-mono text-white/30 mx-3">|</span>
            <span className="text-sm font-mono text-white/50">1 million context</span>
          </div>
          <div className="h-10 px-6 border-b border-white/10 bg-black/50 flex items-center gap-8">
            <span className="text-sm font-mono text-cyan-400 cursor-pointer">front end</span>
            <span className="text-sm font-mono text-white/50 hover:text-white cursor-pointer">backend</span>
            <span className="text-sm font-mono text-white/50 hover:text-white cursor-pointer">database</span>
            <span className="text-sm font-mono text-white/50 hover:text-white cursor-pointer">deploy</span>
          </div>
          <div className="flex-1 bg-black/40 p-6 overflow-auto relative">
            <pre className="text-sm font-mono text-white/60 leading-relaxed">// Your code will appear here...{'\n'}// Use /genesis or go to Electric Workflow</pre>
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-4 text-sm font-mono text-cyan-400/40">
              <span>◄────</span><span>ghost lines</span><span>────►</span>
            </div>
          </div>
          <div className="h-32 border-t border-white/20 bg-black/80 flex flex-col">
            <div className="h-8 px-6 border-b border-white/10 flex items-center">
              <span className="text-sm font-mono text-purple-400">◆ TERMINAL</span>
            </div>
            <div ref={terminalRef} className="flex-1 overflow-y-auto px-6 py-2">
              {terminalOutput.map((line, idx) => (
                <div key={idx} className={`text-sm font-mono ${line.type === 'error' ? 'text-red-400' : line.type === 'success' ? 'text-green-400' : line.type === 'system' ? 'text-purple-400' : 'text-white/60'}`}>{line.text}</div>
              ))}
            </div>
            <div className="h-8 px-6 border-t border-white/10 flex items-center">
              <input type="text" value={terminalInput} onChange={(e) => setTerminalInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleTerminalSend()} placeholder="Enter command..." className="flex-1 bg-transparent text-sm font-mono text-white placeholder-white/40 focus:outline-none" />
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN - GROK */}
        <div className="w-1/4 min-w-[300px] flex flex-col border-l border-white/20 bg-black/60">
          <div className="h-10 px-4 border-b border-white/20 flex items-center justify-between">
            <span className="text-sm font-mono text-green-400 font-semibold">◆ GROK</span>
            <span className="text-xs font-mono text-white/40">1M context</span>
          </div>
          <div className="h-40 border-b border-white/10 flex items-center justify-center">
            <div className="w-32 h-32"><NeuralBrain themeColor="#22c55e" isThinking={grokLoading} size="lg" /></div>
          </div>
          <div ref={grokRef} className="flex-1 overflow-y-auto p-4 space-y-4">
            {grokChat.length === 0 ? (
              <div className="text-sm font-mono text-white/40 text-center py-8">Grok responses appear here...</div>
            ) : (
              grokChat.map((msg, idx) => (
                <div key={idx}>
                  <span className="text-xs font-mono text-white/40">◈ {msg.role.toUpperCase()}</span>
                  <p className={`text-sm font-mono mt-1 leading-relaxed ${msg.role === 'user' ? 'text-green-400' : 'text-white/80'}`}>{msg.content}</p>
                </div>
              ))
            )}
            {grokLoading && <div className="text-green-400 text-sm flex items-center gap-2"><span className="animate-spin">◈</span> Thinking...</div>}
          </div>
          <div className="h-20 border-t border-white/20 p-3">
            <div className="text-xs font-mono text-white/50 mb-1">saved chats</div>
            {savedChats.length === 0 ? <div className="text-xs font-mono text-white/30">No saved chats</div> : savedChats.slice(-3).map(c => <div key={c.id} className="text-sm font-mono text-white/50 truncate cursor-pointer hover:text-white">{c.title}</div>)}
          </div>
          <div className="h-14 px-4 border-t border-green-500/40 bg-black/80 flex items-center gap-3">
            <span className="text-sm font-mono text-green-400">Grok ▶</span>
            <input type="text" value={grokInput} onChange={(e) => setGrokInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleGrokSend()} placeholder="Ask Grok..." className="flex-1 bg-transparent text-sm font-mono text-white placeholder-white/40 focus:outline-none" data-testid="grok-prompt" />
          </div>
          <div className="h-24 border-t border-white/20 bg-black/80 flex">
            <div className="w-1/2 p-2 border-r border-white/10">
              <div className="text-xs font-mono text-yellow-400 mb-2">CI/CD • MCP TOOLS</div>
              <div className="grid grid-cols-2 gap-1">
                {['Deploy', 'Build', 'Monitor', 'Config'].map(t => <button key={t} className="text-xs font-mono text-white/60 py-1 bg-white/5 hover:bg-white/10 rounded">{t}</button>)}
              </div>
            </div>
            <div className="w-1/2 p-2">
              <div className="text-xs font-mono text-green-400">GROK RESPONSE</div>
              <div className="text-xs font-mono text-white/40 mt-1">Responses...</div>
            </div>
          </div>
        </div>
      </div>

      <div className="fixed bottom-2 right-6 z-50 text-xs font-mono text-white/30">◎ Made with Emergent</div>
    </div>
  );
};

// MAIN APP
function App() {
  const [currentPage, setCurrentPage] = useState(PAGES.LANDING);
  if (currentPage === PAGES.LANDING) return <LandingPage onEnterApp={() => setCurrentPage(PAGES.IDE)} />;
  if (currentPage === PAGES.WORKFLOW) return <ElectricWorkflowPage onBack={() => setCurrentPage(PAGES.IDE)} />;
  return <IDEPage onNavigate={setCurrentPage} />;
}

export default App;
