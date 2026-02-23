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
// ELECTRIC WORKFLOW PAGE - Full Genesis Pipeline with Franklin Chat
// ============================================================================
const ElectricWorkflowPage = ({ onBack }) => {
  const [currentStage, setCurrentStage] = useState(0);
  const [convergence, setConvergence] = useState(0);
  const [qualityScores, setQualityScores] = useState(QUALITY_DIMENSIONS);
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [chatInput, setChatInput] = useState('');
  const [franklinChat, setFranklinChat] = useState([
    { role: 'franklin', content: 'Welcome to the Genesis Pipeline. I\'m Franklin, your AI guide. I can help you navigate and control this workflow.' },
    { role: 'franklin', content: 'Try commands like: "move to specification stage", "run ouroboros loop", "check quality gates", or just ask me anything about your project.' }
  ]);
  const [terminalOutput, setTerminalOutput] = useState([
    { type: 'system', text: '> GENESIS ENGINE v2.0 ONLINE' },
    { type: 'info', text: '> Ouroboros Loop: STANDBY' },
    { type: 'info', text: '> Quality Gates: 8 DIMENSIONS READY' },
    { type: 'success', text: '> System ready for project initialization' }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [ouroborosActive, setOuroborosActive] = useState(false);
  const franklinRef = useRef(null);
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

  useEffect(() => { if (franklinRef.current) franklinRef.current.scrollTop = franklinRef.current.scrollHeight; }, [franklinChat]);
  useEffect(() => { if (terminalRef.current) terminalRef.current.scrollTop = terminalRef.current.scrollHeight; }, [terminalOutput]);

  const addTerminal = (text, type = 'info') => setTerminalOutput(prev => [...prev, { type, text: `> ${text}` }]);

  // Parse natural language commands for pipeline control
  const parseCommand = (input) => {
    const lower = input.toLowerCase();
    
    // Stage navigation commands
    const stageKeywords = {
      'inception': 0, 'spec': 1, 'specification': 1, 'arch': 2, 'architecture': 2,
      'construction': 3, 'build': 3, 'validation': 4, 'test': 4, 'testing': 4,
      'evolution': 5, 'optimize': 5, 'deploy': 6, 'deployment': 6,
      'governance': 7, 'govern': 7, 'compliance': 7
    };
    
    // Check for stage movement
    if (lower.includes('move to') || lower.includes('go to') || lower.includes('jump to') || lower.includes('set stage')) {
      for (const [keyword, stageIdx] of Object.entries(stageKeywords)) {
        if (lower.includes(keyword)) {
          return { type: 'move_stage', stage: stageIdx, stageName: GENESIS_STAGES[stageIdx].name };
        }
      }
    }
    
    // Check for ouroboros
    if (lower.includes('ouroboros') || lower.includes('converge') || lower.includes('convergence')) {
      if (lower.includes('run') || lower.includes('start') || lower.includes('execute') || lower.includes('begin')) {
        return { type: 'run_ouroboros' };
      }
    }
    
    // Check for quality gate queries
    if (lower.includes('quality') || lower.includes('gate')) {
      return { type: 'quality_check' };
    }
    
    // Check for status
    if (lower.includes('status') || lower.includes('where am i') || lower.includes('current stage')) {
      return { type: 'status' };
    }
    
    // Check for reset
    if (lower.includes('reset') || lower.includes('restart') || lower.includes('start over')) {
      return { type: 'reset' };
    }
    
    // Check for genesis command
    if (lower.startsWith('/genesis ') || lower.includes('start project') || lower.includes('begin project') || lower.includes('initialize project')) {
      const projectName = input.replace(/^\/genesis\s+/i, '').replace(/start project|begin project|initialize project/i, '').trim();
      return { type: 'genesis', projectName: projectName || 'New Project' };
    }
    
    // Check for next/previous stage
    if (lower.includes('next stage') || lower.includes('advance') || lower.includes('proceed')) {
      return { type: 'next_stage' };
    }
    if (lower.includes('previous stage') || lower.includes('go back') || lower.includes('back stage')) {
      return { type: 'prev_stage' };
    }
    
    return { type: 'chat', message: input };
  };

  // Execute parsed commands
  const executeCommand = async (command) => {
    switch (command.type) {
      case 'move_stage':
        setCurrentStage(command.stage);
        addTerminal(`MOVED TO: ${command.stageName}`, 'system');
        highlightStage(command.stage);
        return `Moving to ${command.stageName} stage. This stage handles: ${GENESIS_STAGES[command.stage].desc}`;
      
      case 'run_ouroboros':
        if (ouroborosActive) {
          return 'Ouroboros loop is already running. Please wait for it to complete.';
        }
        runOuroborosLoop();
        return 'Initiating Ouroboros convergence loop. Target: 99% convergence across all quality dimensions.';
      
      case 'quality_check':
        const avgScore = qualityScores.reduce((a, b) => a + b.score, 0) / qualityScores.length;
        const qualityReport = qualityScores.map(q => `• ${q.name}: ${q.score.toFixed(1)}%`).join('\n');
        return `8-Dimensional Quality Gate Assessment:\n\nAverage Score: ${avgScore.toFixed(1)}%\n\n${qualityReport}\n\nUse "run ouroboros" to improve scores.`;
      
      case 'status':
        const stage = GENESIS_STAGES[currentStage];
        return `Current Status:\n• Stage: ${stage.name} (${currentStage + 1}/8)\n• Description: ${stage.desc}\n• Convergence: ${convergence.toFixed(1)}%\n• Ouroboros: ${ouroborosActive ? 'ACTIVE' : 'STANDBY'}`;
      
      case 'reset':
        setCurrentStage(0);
        setConvergence(0);
        setQualityScores(QUALITY_DIMENSIONS);
        addTerminal('PIPELINE RESET', 'system');
        setNodes(initialNodes);
        return 'Pipeline has been reset to INCEPTION stage. All quality scores cleared.';
      
      case 'genesis':
        addTerminal(`PROJECT: ${command.projectName}`, 'system');
        await runGenesisPipeline(command.projectName);
        return `Genesis Pipeline initiated for "${command.projectName}". Running through all 8 stages...`;
      
      case 'next_stage':
        if (currentStage < 7) {
          const nextStage = currentStage + 1;
          setCurrentStage(nextStage);
          addTerminal(`ADVANCED TO: ${GENESIS_STAGES[nextStage].name}`, 'system');
          highlightStage(nextStage);
          return `Advanced to ${GENESIS_STAGES[nextStage].name} stage.`;
        }
        return 'Already at the final stage (GOVERNANCE). Use "run ouroboros" to complete the loop.';
      
      case 'prev_stage':
        if (currentStage > 0) {
          const prevStage = currentStage - 1;
          setCurrentStage(prevStage);
          addTerminal(`RETURNED TO: ${GENESIS_STAGES[prevStage].name}`, 'system');
          highlightStage(prevStage);
          return `Returned to ${GENESIS_STAGES[prevStage].name} stage.`;
        }
        return 'Already at the first stage (INCEPTION).';
      
      default:
        return null; // Will be handled by AI chat
    }
  };

  const highlightStage = (stageIdx) => {
    setNodes(nds => nds.map(n => ({
      ...n,
      style: {
        ...n.style,
        boxShadow: n.id === GENESIS_STAGES[stageIdx]?.id ? '0 0 25px #00ff88, 0 0 50px #00ff88' : 'none'
      }
    })));
  };

  const runGenesisPipeline = async (projectName) => {
    for (let i = 0; i < GENESIS_STAGES.length; i++) {
      await new Promise(r => setTimeout(r, 800));
      setCurrentStage(i);
      addTerminal(`[${GENESIS_STAGES[i].name}] ${GENESIS_STAGES[i].desc}`, 'info');
      highlightStage(i);
      setFranklinChat(prev => [...prev, { role: 'franklin', content: `Stage ${i + 1}/8: ${GENESIS_STAGES[i].name} - ${GENESIS_STAGES[i].desc}` }]);
    }
    addTerminal('PIPELINE COMPLETE', 'success');
    addTerminal('Ready for Ouroboros convergence', 'info');
  };

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
        setFranklinChat(prev => [...prev, { role: 'franklin', content: '✓ Ouroboros Loop complete. 99% convergence achieved. Your project spine is now frozen and ready for deployment.' }]);
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
    setFranklinChat(prev => [...prev, { role: 'user', content: input }]);
    setIsProcessing(true);

    // Parse and try to execute command
    const command = parseCommand(input);
    const commandResult = await executeCommand(command);
    
    if (commandResult) {
      // Command was handled locally
      setFranklinChat(prev => [...prev, { role: 'franklin', content: commandResult }]);
      setIsProcessing(false);
      return;
    }

    // If not a command, chat with the AI
    try {
      const res = await axios.post(`${API}/api/build-orchestrator/chat`, { 
        message: input,
        context: `User is on the Genesis Pipeline workflow page. Current stage: ${GENESIS_STAGES[currentStage].name}. Convergence: ${convergence.toFixed(1)}%.`
      });
      setFranklinChat(prev => [...prev, { role: 'franklin', content: res.data.response || "I can help you with that. Try asking about the pipeline stages or use commands like 'move to specification'." }]);
    } catch {
      setFranklinChat(prev => [...prev, { role: 'franklin', content: "I'm here to help navigate the Genesis Pipeline. You can say things like 'move to architecture stage', 'run ouroboros', 'check quality gates', or 'what's my current status'." }]);
    }
    setIsProcessing(false);
  };

  const onConnect = useCallback((params) => setEdges((eds) => addEdge({ ...params, animated: true, style: { stroke: '#00ff88' } }, eds)), [setEdges]);

  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="workflow-page">
      <GalacticBackground />
      
      {/* GHOST FRANKLIN - Same as IDE page */}
      <div className="fixed inset-0 flex items-center justify-center pointer-events-none z-[1]">
        <h1 className="select-none" style={{ fontFamily: "'Orbitron', sans-serif", fontSize: '12vw', fontWeight: 600, letterSpacing: '0.3em', color: 'rgba(80,80,80,0.12)' }}>FRANKLIN</h1>
      </div>
      
      {/* HEADER */}
      <div className="absolute top-0 left-0 right-0 h-12 z-50 bg-black/80 backdrop-blur-md border-b border-white/10 flex items-center justify-between px-6">
        <button onClick={onBack} className="px-4 py-2 text-sm font-mono text-white/70 hover:text-white hover:bg-white/10 rounded flex items-center gap-2 transition-all" data-testid="back-to-ide">
          ◀ BACK TO IDE
        </button>
        <div className="text-center">
          <h1 className="text-lg font-mono tracking-[0.2em] text-white" style={{ fontFamily: "'Orbitron', sans-serif" }}>
            ◈ GENESIS PIPELINE
          </h1>
          <p className="text-[10px] text-white/40">OUROBOROS LOOP • 8 QUALITY GATES • FROZEN SPINE</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm font-mono">
            <span className="text-white/40">Convergence:</span>
            <span className={`ml-2 font-semibold ${convergence >= 99 ? 'text-green-400' : convergence >= 50 ? 'text-yellow-400' : 'text-white/60'}`}>{convergence.toFixed(1)}%</span>
          </div>
          <div className={`w-2.5 h-2.5 rounded-full ${ouroborosActive ? 'bg-green-400 animate-pulse shadow-lg shadow-green-400/50' : 'bg-white/20'}`} />
        </div>
      </div>

      {/* LEFT PANEL - Franklin Chat */}
      <div className={`absolute top-12 bottom-0 z-40 bg-black/70 backdrop-blur-sm border-r border-white/10 transition-all duration-300 flex flex-col ${leftPanelOpen ? 'left-0 w-80' : '-left-80 w-80'}`}>
        <button onClick={() => setLeftPanelOpen(!leftPanelOpen)} className="absolute -right-8 top-1/2 -translate-y-1/2 w-8 h-16 bg-black/70 backdrop-blur-sm border border-white/10 rounded-r flex items-center justify-center text-white/50 hover:text-white text-sm transition-all">
          {leftPanelOpen ? '◀' : '▶'}
        </button>
        
        {/* Franklin Header */}
        <div className="h-10 px-4 border-b border-white/10 flex items-center justify-between bg-black/50">
          <span className="text-sm font-mono text-cyan-400 font-semibold">◆ FRANKLIN</span>
          <span className="text-[10px] font-mono text-white/30">Pipeline Guide</span>
        </div>
        
        {/* Franklin Chat */}
        <div ref={franklinRef} className="flex-1 overflow-y-auto p-3 space-y-3">
          {franklinChat.map((msg, idx) => (
            <div key={idx} className={`text-sm font-mono ${msg.role === 'user' ? 'text-cyan-400' : 'text-white/70'}`}>
              <span className="text-[10px] text-white/30 uppercase">{msg.role === 'user' ? '◈ YOU' : '◈ FRANKLIN'}</span>
              <p className="mt-1 whitespace-pre-wrap leading-relaxed">{msg.content}</p>
            </div>
          ))}
          {isProcessing && <div className="text-purple-400 text-sm flex items-center gap-2"><span className="animate-spin">◈</span> Processing...</div>}
        </div>
        
        {/* Franklin Prompt */}
        <div className="h-12 px-3 border-t border-cyan-500/30 bg-black/60 flex items-center gap-2">
          <span className="text-sm font-mono text-cyan-400">Franklin ▶</span>
          <input 
            type="text" 
            value={chatInput} 
            onChange={(e) => setChatInput(e.target.value)} 
            onKeyDown={(e) => e.key === 'Enter' && handleChatSend()} 
            placeholder="Ask or command..." 
            className="flex-1 bg-transparent text-sm font-mono text-white placeholder-white/30 focus:outline-none" 
            data-testid="workflow-franklin-prompt"
          />
        </div>
        
        {/* Terminal Section */}
        <div className="h-36 flex flex-col border-t border-white/10">
          <div className="h-7 px-3 border-b border-white/10 flex items-center bg-black/50">
            <span className="text-xs font-mono text-purple-400">◆ TERMINAL</span>
          </div>
          <div ref={terminalRef} className="flex-1 overflow-y-auto p-2">
            {terminalOutput.map((line, idx) => (
              <div key={idx} className={`text-[11px] font-mono ${line.type === 'error' ? 'text-red-400' : line.type === 'success' ? 'text-green-400' : line.type === 'system' ? 'text-purple-400' : 'text-white/50'}`}>{line.text}</div>
            ))}
          </div>
        </div>
      </div>

      {/* RIGHT PANEL - Controls & Quality */}
      <div className={`absolute top-12 bottom-0 z-40 bg-black/70 backdrop-blur-sm border-l border-white/10 transition-all duration-300 flex flex-col ${rightPanelOpen ? 'right-0 w-72' : '-right-72 w-72'}`}>
        <button onClick={() => setRightPanelOpen(!rightPanelOpen)} className="absolute -left-8 top-1/2 -translate-y-1/2 w-8 h-16 bg-black/70 backdrop-blur-sm border border-white/10 rounded-l flex items-center justify-center text-white/50 hover:text-white text-sm transition-all">
          {rightPanelOpen ? '▶' : '◀'}
        </button>
        
        {/* Stage Progress */}
        <div className="p-3 border-b border-white/10">
          <div className="text-xs font-mono text-white/50 mb-2">GENESIS STAGES</div>
          <div className="space-y-1.5">
            {GENESIS_STAGES.map((stage, idx) => (
              <div 
                key={stage.id} 
                className={`flex items-center gap-2 px-2 py-1 rounded cursor-pointer transition-all ${idx === currentStage ? 'bg-cyan-500/20' : 'hover:bg-white/5'}`}
                onClick={() => { setCurrentStage(idx); highlightStage(idx); addTerminal(`JUMPED TO: ${stage.name}`, 'system'); }}
              >
                <div className={`w-3.5 h-3.5 rounded-full flex items-center justify-center text-[9px] ${idx < currentStage ? 'bg-green-400 text-black' : idx === currentStage ? 'bg-cyan-400 animate-pulse text-black' : 'bg-white/15 text-white/30'}`}>
                  {idx < currentStage ? '✓' : idx + 1}
                </div>
                <span className={`text-xs font-mono ${idx <= currentStage ? 'text-white' : 'text-white/35'}`}>{stage.name}</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Quality Gates */}
        <div className="flex-1 p-3 overflow-y-auto">
          <div className="text-xs font-mono text-white/50 mb-2">8D QUALITY GATES</div>
          <div className="space-y-2">
            {qualityScores.map(q => (
              <div key={q.name}>
                <div className="flex justify-between text-[10px] font-mono mb-0.5">
                  <span className="text-white/60">{q.name}</span>
                  <span className={q.score >= 80 ? 'text-green-400' : q.score >= 50 ? 'text-yellow-400' : 'text-white/30'}>{q.score.toFixed(0)}%</span>
                </div>
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div className={`h-full transition-all duration-500 ${q.score >= 80 ? 'bg-green-400' : q.score >= 50 ? 'bg-yellow-400' : 'bg-white/20'}`} style={{ width: `${q.score}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="p-3 border-t border-white/10 space-y-2">
          <button 
            onClick={runOuroborosLoop} 
            disabled={ouroborosActive} 
            className={`w-full py-2.5 text-xs font-mono rounded transition-all ${ouroborosActive ? 'bg-green-500/20 text-green-400 animate-pulse' : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'} border border-green-500/30`}
          >
            {ouroborosActive ? '∞ CONVERGING...' : '▶ RUN OUROBOROS'}
          </button>
          <button 
            onClick={() => { setCurrentStage(0); setConvergence(0); setQualityScores(QUALITY_DIMENSIONS); addTerminal('PIPELINE RESET', 'system'); setNodes(initialNodes); }} 
            className="w-full py-2.5 text-xs font-mono bg-white/5 border border-white/10 rounded text-white/50 hover:bg-white/10 hover:text-white/70 transition-all"
          >
            ⟳ RESET
          </button>
        </div>
      </div>

      {/* MAIN CANVAS - ReactFlow */}
      <div className={`absolute top-12 bottom-0 z-10 transition-all duration-300 ${leftPanelOpen ? 'left-80' : 'left-0'} ${rightPanelOpen ? 'right-72' : 'right-0'}`}>
        <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} fitView className="!bg-transparent">
          <Background color="rgba(0,255,136,0.02)" gap={40} />
          <Controls className="!bg-black/70 !backdrop-blur-sm !border-white/10 !rounded" />
        </ReactFlow>
        
        {/* Legend */}
        <div className="absolute bottom-3 left-3 bg-black/70 backdrop-blur-sm border border-white/10 rounded p-3">
          <div className="text-[10px] font-mono text-white/50 mb-1.5">LEGEND</div>
          <div className="space-y-1 text-[10px] font-mono">
            <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded bg-green-400" /><span className="text-white/40">Completed</span></div>
            <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded bg-cyan-400 animate-pulse" /><span className="text-white/40">In Progress</span></div>
            <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded bg-white/15" /><span className="text-white/40">Pending</span></div>
            <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full border border-green-400 border-dashed" /><span className="text-white/40">Ouroboros</span></div>
          </div>
        </div>
        
        {/* Quick Commands Hint */}
        <div className="absolute bottom-3 right-3 bg-black/70 backdrop-blur-sm border border-white/10 rounded p-3 max-w-xs">
          <div className="text-[10px] font-mono text-white/50 mb-1.5">QUICK COMMANDS</div>
          <div className="space-y-0.5 text-[9px] font-mono text-white/40">
            <div>"move to [stage]" - navigate stages</div>
            <div>"run ouroboros" - start convergence</div>
            <div>"check quality" - view gate scores</div>
            <div>"status" - current pipeline state</div>
          </div>
        </div>
      </div>

      {/* Made with Emergent */}
      <div className="fixed bottom-2 right-3 z-50 text-[10px] font-mono text-white/20">◎ Made with Emergent</div>
    </div>
  );
};

// ============================================================================
// IDE PAGE - THE ACTUAL BUILDER
// ============================================================================

// Available tech stacks
const TECH_STACKS = [
  { id: 'python', name: 'Python', icon: '🐍', desc: 'FastAPI, Flask, Django' },
  { id: 'javascript', name: 'JavaScript', icon: '⚡', desc: 'Node.js, Express, React' },
  { id: 'typescript', name: 'TypeScript', icon: '📘', desc: 'Node.js, Next.js, NestJS' },
  { id: 'go', name: 'Go', icon: '🔵', desc: 'Gin, Fiber, Echo' },
  { id: 'rust', name: 'Rust', icon: '🦀', desc: 'Actix, Rocket, Axum' },
  { id: 'java', name: 'Java', icon: '☕', desc: 'Spring Boot, Quarkus' }
];

const IDEPage = ({ onNavigate }) => {
  const [franklinInput, setFranklinInput] = useState('');
  const [grokInput, setGrokInput] = useState('');
  const [terminalInput, setTerminalInput] = useState('');
  const [selectedStack, setSelectedStack] = useState('python');
  const [showStackSelector, setShowStackSelector] = useState(false);
  const [franklinChat, setFranklinChat] = useState(() => {
    const saved = localStorage.getItem('franklin_chat_v2');
    return saved ? JSON.parse(saved) : [{ role: 'franklin', content: 'Welcome to FRANKLIN OS. Tell me what you want to build.\n\nCurrent stack: **Python** (click to change)\n\nJust describe what you want and I\'ll generate production-ready code.' }];
  });
  const [grokChat, setGrokChat] = useState(() => {
    const saved = localStorage.getItem('grok_chat_v2');
    return saved ? JSON.parse(saved) : [];
  });
  const [terminalOutput, setTerminalOutput] = useState([{ type: 'system', text: '> FRANKLIN OS Terminal v2.0' }, { type: 'info', text: '> Stack: Python | Ready to build...' }]);
  const [savedChats, setSavedChats] = useState(() => {
    const saved = localStorage.getItem('saved_chats_v2');
    return saved ? JSON.parse(saved) : [];
  });
  const [franklinLoading, setFranklinLoading] = useState(false);
  const [grokLoading, setGrokLoading] = useState(false);
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildResult, setBuildResult] = useState(null);
  const [generatedCode, setGeneratedCode] = useState('');
  const [activeTab, setActiveTab] = useState('code');
  const [certificationStatus, setCertificationStatus] = useState(null);
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

  // Detect if user wants to build something
  const detectBuildIntent = (message) => {
    const lower = message.toLowerCase();
    const buildKeywords = ['build', 'create', 'make', 'develop', 'generate', 'code', 'implement', 'write'];
    return buildKeywords.some(k => lower.includes(k));
  };

  // THE ACTUAL BUILD FUNCTION - Uses real file generation
  const executeBuild = async (mission) => {
    setIsBuilding(true);
    setGeneratedCode('');
    setBuildResult(null);
    setCertificationStatus(null);
    
    const stack = TECH_STACKS.find(s => s.id === selectedStack);
    
    addTerminal('═══════════════════════════════════════', 'system');
    addTerminal('FRANKLIN OS BUILD INITIATED', 'system');
    addTerminal(`Stack: ${stack.name}`, 'info');
    addTerminal(`Mission: ${mission}`, 'info');
    addTerminal('═══════════════════════════════════════', 'system');

    setFranklinChat(prev => [...prev, { role: 'franklin', content: `🚀 **BUILD INITIATED**\n\n**Stack:** ${stack.icon} ${stack.name}\n**Building:** "${mission}"\n\nGenerating real project files...` }]);

    try {
      addTerminal('Calling LLM (multi-provider fallback)...', 'info');
      
      // Use the new simple-build endpoint that creates REAL FILES
      const res = await axios.post(`${API}/api/simple-build/build`, { 
        prompt: mission, 
        tech_stack: stack.id 
      });
      
      if (res.data.success) {
        const { build_id, files, file_contents, stats, tree, checksums } = res.data;
        
        addTerminal(`[GENESIS] Created ${files.length} files`, 'success');
        addTerminal(`[GENESIS] ${stats.total_lines} lines, ${stats.total_bytes} bytes`, 'info');
        
        // Display all files in terminal
        files.forEach(f => {
          addTerminal(`  ├── ${f.path} (${f.lines} lines)`, 'info');
        });
        
        // Find main code file
        const mainFile = files.find(f => 
          f.path.endsWith('.py') || 
          f.path.endsWith('.js') || 
          f.path.endsWith('.ts')
        );
        
        // Set generated code to display (all files concatenated or main file)
        let displayCode = '';
        if (file_contents) {
          for (const [path, content] of Object.entries(file_contents)) {
            displayCode += `// ═══ ${path} ═══\n\n${content}\n\n`;
          }
        }
        setGeneratedCode(displayCode);
        
        addTerminal('═══════════════════════════════════════', 'success');
        addTerminal('REAL FILES CREATED ON DISK', 'success');
        addTerminal(`Build ID: ${build_id}`, 'success');

        // Run certification
        addTerminal('Running 8-Gate Certification...', 'info');
        try {
          const certRes = await axios.post(`${API}/api/simple-build/certify`, { build_id });
          const cert = certRes.data;
          
          cert.gates?.forEach(gate => {
            const status = gate.passed ? '✓' : '✗';
            addTerminal(`  ${status} Gate ${gate.gate_num}: ${gate.gate_name} - ${gate.score.toFixed(0)}%`, gate.passed ? 'success' : 'error');
          });
          
          if (cert.all_passed) {
            setCertificationStatus({
              certified: true,
              signedBy: 'FRANKLIN',
              certification: 'FRANKLIN_OS_CERTIFIED',
              score: cert.total_score,
              hash: cert.certification_hash,
              build_id,
              stack: stack.name
            });
            addTerminal('═══════════════════════════════════════', 'success');
            addTerminal('✓ FRANKLIN OS CERTIFIED', 'success');
            addTerminal(`Hash: ${cert.certification_hash?.slice(0, 16)}...`, 'success');
          } else {
            setCertificationStatus({
              certified: false,
              score: cert.total_score,
              passed: cert.passed_gates,
              total: 8,
              build_id
            });
            addTerminal(`Certification: ${cert.passed_gates}/8 gates passed`, 'warning');
          }
        } catch (certErr) {
          addTerminal('Certification check failed (build still saved)', 'warning');
        }

        setBuildResult({
          success: true,
          build_id,
          files,
          file_contents,
          stats,
          tree,
          stack: stack.name
        });

        setFranklinChat(prev => [...prev, { 
          role: 'franklin', 
          content: `✅ **BUILD COMPLETE**\n\n**Build ID:** \`${build_id}\`\n**Stack:** ${stack.icon} ${stack.name}\n**Files:** ${files.length}\n**Lines:** ${stats.total_lines}\n\n**Project Tree:**\n\`\`\`\n${tree}\n\`\`\`\n\nUse COPY to get all code, or DOWNLOAD to get the ZIP with all project files.` 
        }]);

      } else {
        throw new Error(res.data.error || 'Build failed');
      }
    } catch (err) {
      addTerminal('BUILD FAILED', 'error');
      addTerminal(err.message || 'Unknown error', 'error');
      setFranklinChat(prev => [...prev, { role: 'franklin', content: `❌ Build error: ${err.message || 'Unknown'}. Try being more specific.` }]);
    }
    
    setIsBuilding(false);
  };

  const handleFranklinSend = async () => {
    if (!franklinInput.trim() || franklinLoading || isBuilding) return;
    const input = franklinInput.trim();
    setFranklinInput('');
    setFranklinChat(prev => [...prev, { role: 'user', content: input }]);
    setFranklinLoading(true);

    // Check for commands
    if (input.toLowerCase() === '/workflow') { onNavigate(PAGES.WORKFLOW); setFranklinLoading(false); return; }
    if (input.toLowerCase() === '/clear') { 
      setFranklinChat([{ role: 'franklin', content: 'Cleared. Ready to build.' }]); 
      setGrokChat([]); 
      setTerminalOutput([{ type: 'system', text: '> Cleared' }]); 
      setGeneratedCode('');
      setBuildResult(null);
      setCertificationStatus(null);
      setFranklinLoading(false); 
      return; 
    }
    if (input.toLowerCase() === '/save') { 
      setSavedChats(prev => [...prev, { id: Date.now(), title: franklinChat[1]?.content?.slice(0, 25) + '...' || 'Chat', messages: franklinChat }]); 
      setFranklinChat(prev => [...prev, { role: 'franklin', content: 'Chat saved!' }]); 
      setFranklinLoading(false); 
      return; 
    }

    // Detect build intent and execute
    if (detectBuildIntent(input)) {
      setFranklinLoading(false);
      await executeBuild(input);
      return;
    }

    // Regular chat
    try {
      const res = await axios.post(`${API}/api/build-orchestrator/chat`, { message: input });
      const response = res.data.response || "I can help you build something. Just tell me what you want to create!";
      setFranklinChat(prev => [...prev, { role: 'franklin', content: response }]);
      
      // If the response suggests building, offer to start
      if (res.data.ready_to_build) {
        setFranklinChat(prev => [...prev, { role: 'franklin', content: "I can build that for you right now. Just say 'build it' or describe what you want more specifically." }]);
      }
    } catch { 
      setFranklinChat(prev => [...prev, { role: 'franklin', content: "I'm ready to build. Tell me what you want to create - a web app, API, tool, anything!" }]); 
    }
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
    else if (input === 'status') { addTerminal('FRANKLIN: Online', 'success'); addTerminal('GROK: Connected', 'success'); addTerminal(`Build Status: ${isBuilding ? 'IN PROGRESS' : 'IDLE'}`, 'info'); }
    else if (input === 'workflow' || input === '/workflow') onNavigate(PAGES.WORKFLOW);
    else if (input === 'help') {
      addTerminal('Available commands:', 'info');
      addTerminal('  status   - System status', 'info');
      addTerminal('  clear    - Clear terminal', 'info');
      addTerminal('  workflow - Go to workflow', 'info');
      addTerminal('  download - Download code', 'info');
    }
    else if (input === 'download' && generatedCode) {
      downloadCode();
    }
  };

  const downloadCode = () => {
    if (!generatedCode) return;
    const blob = new Blob([generatedCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `franklin-os-build-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    addTerminal('Code downloaded!', 'success');
  };

  const copyCode = () => {
    if (!generatedCode) return;
    navigator.clipboard.writeText(generatedCode);
    addTerminal('Code copied to clipboard!', 'success');
  };

  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="franklin-os">
      <GalacticBackground />
      
      {/* GHOST FRANKLIN */}
      <div className="fixed inset-0 flex items-center justify-center pointer-events-none z-[1]">
        <h1 className="select-none" style={{ fontFamily: "'Orbitron', sans-serif", fontSize: '12vw', fontWeight: 600, letterSpacing: '0.3em', color: 'rgba(80,80,80,0.15)' }}>FRANKLIN</h1>
      </div>
      
      {/* TECH STACK SELECTOR MODAL */}
      {showStackSelector && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100] flex items-center justify-center" onClick={() => setShowStackSelector(false)}>
          <div className="bg-black/90 border border-white/20 rounded-lg p-6 max-w-md" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-mono text-white mb-4">Select Tech Stack</h3>
            <div className="grid grid-cols-2 gap-3">
              {TECH_STACKS.map(stack => (
                <button
                  key={stack.id}
                  onClick={() => { setSelectedStack(stack.id); setShowStackSelector(false); addTerminal(`Stack changed to: ${stack.name}`, 'system'); }}
                  className={`p-3 rounded border text-left transition-all ${selectedStack === stack.id ? 'border-cyan-500 bg-cyan-500/20' : 'border-white/20 hover:border-white/40 hover:bg-white/5'}`}
                >
                  <div className="text-xl mb-1">{stack.icon}</div>
                  <div className="text-sm font-mono text-white">{stack.name}</div>
                  <div className="text-xs font-mono text-white/50">{stack.desc}</div>
                </button>
              ))}
            </div>
            <button onClick={() => setShowStackSelector(false)} className="mt-4 w-full py-2 text-sm font-mono text-white/60 border border-white/20 rounded hover:bg-white/10">Close</button>
          </div>
        </div>
      )}
      
      {/* HEADER */}
      <div className="absolute top-0 left-0 right-0 h-12 z-50 bg-black/90 border-b border-white/20 flex items-center px-6">
        <span className="text-base font-mono text-white tracking-wider" style={{ fontFamily: "'Orbitron', sans-serif" }}>◈ FRANKLIN OS</span>
        <div className="flex-1" />
        
        {/* Tech Stack Selector */}
        <button 
          onClick={() => setShowStackSelector(true)} 
          className="mr-4 px-3 py-1.5 text-sm font-mono text-cyan-400 border border-cyan-500/50 rounded hover:bg-cyan-500/20 transition-all flex items-center gap-2"
          data-testid="stack-selector"
        >
          <span>{TECH_STACKS.find(s => s.id === selectedStack)?.icon}</span>
          <span>{TECH_STACKS.find(s => s.id === selectedStack)?.name}</span>
          <span className="text-white/40">▼</span>
        </button>
        
        {isBuilding && (
          <div className="mr-4 px-4 py-1.5 text-sm font-mono text-yellow-400 border border-yellow-500/50 rounded animate-pulse flex items-center gap-2">
            <span className="animate-spin">◈</span> BUILDING...
          </div>
        )}
        {certificationStatus && (
          <div className="mr-4 px-4 py-1.5 text-sm font-mono text-green-400 border border-green-500/50 rounded flex items-center gap-2">
            ✓ CERTIFIED
          </div>
        )}
        <div className="flex items-center gap-6 text-xs font-mono">
          <span className="text-green-400 flex items-center gap-2"><span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />ONLINE</span>
        </div>
      </div>

      {/* MAIN CONTENT - 3 COLUMNS */}
      <div className="absolute top-12 bottom-0 left-0 right-0 flex">
        
        {/* LEFT COLUMN - FRANKLIN */}
        <div className="w-1/4 min-w-[280px] flex flex-col border-r border-white/20 bg-black/60">
          <div className="h-10 px-4 border-b border-white/20 flex items-center justify-between">
            <span className="text-sm font-mono text-cyan-400 font-semibold">◆ FRANKLIN</span>
            <span className="text-xs font-mono text-white/40">Builder</span>
          </div>
          <div ref={franklinRef} className="flex-1 overflow-y-auto p-4 space-y-4">
            {franklinChat.map((msg, idx) => (
              <div key={idx}>
                <span className="text-xs font-mono text-white/40">◈ {msg.role.toUpperCase()}</span>
                <p className={`text-sm font-mono mt-1 leading-relaxed whitespace-pre-wrap ${msg.role === 'user' ? 'text-cyan-400' : 'text-white/80'}`}>{msg.content}</p>
              </div>
            ))}
            {(franklinLoading || isBuilding) && <div className="text-purple-400 text-sm flex items-center gap-2"><span className="animate-spin">◈</span> {isBuilding ? 'Building...' : 'Processing...'}</div>}
          </div>
          <div className="h-14 px-4 border-t border-cyan-500/40 bg-black/80 flex items-center gap-3">
            <span className="text-sm font-mono text-cyan-400">▶</span>
            <input 
              type="text" 
              value={franklinInput} 
              onChange={(e) => setFranklinInput(e.target.value)} 
              onKeyDown={(e) => e.key === 'Enter' && handleFranklinSend()} 
              placeholder="Tell me what to build..." 
              className="flex-1 bg-transparent text-sm font-mono text-white placeholder-white/40 focus:outline-none" 
              data-testid="franklin-prompt" 
              disabled={isBuilding}
            />
          </div>
        </div>

        {/* CENTER COLUMN - CODE AREA */}
        <div className="flex-1 flex flex-col">
          {/* Tabs */}
          <div className="h-10 px-4 border-b border-white/20 bg-black/60 flex items-center gap-4">
            <button 
              onClick={() => setActiveTab('code')} 
              className={`text-sm font-mono transition-all ${activeTab === 'code' ? 'text-cyan-400' : 'text-white/40 hover:text-white/60'}`}
            >
              CODE
            </button>
            <button 
              onClick={() => setActiveTab('spec')} 
              className={`text-sm font-mono transition-all ${activeTab === 'spec' ? 'text-cyan-400' : 'text-white/40 hover:text-white/60'}`}
            >
              SPEC
            </button>
            <button 
              onClick={() => setActiveTab('arch')} 
              className={`text-sm font-mono transition-all ${activeTab === 'arch' ? 'text-cyan-400' : 'text-white/40 hover:text-white/60'}`}
            >
              ARCHITECTURE
            </button>
            <div className="flex-1" />
            {generatedCode && (
              <>
                <button onClick={copyCode} className="px-3 py-1 text-xs font-mono text-white/60 hover:text-white border border-white/20 rounded hover:bg-white/10 transition-all">
                  COPY
                </button>
                <button onClick={downloadCode} className="px-3 py-1 text-xs font-mono text-green-400 border border-green-500/40 rounded hover:bg-green-500/20 transition-all">
                  DOWNLOAD
                </button>
              </>
            )}
          </div>
          
          {/* Certification Badge */}
          {certificationStatus && (
            <div className="h-10 px-4 border-b border-green-500/30 bg-green-500/10 flex items-center gap-4">
              <span className="text-sm font-mono text-green-400">✓ FRANKLIN OS CERTIFIED</span>
              <span className="text-xs font-mono text-white/40">|</span>
              <span className="text-xs font-mono text-white/50">Signed: {certificationStatus.signedBy}</span>
              <span className="text-xs font-mono text-white/40">|</span>
              <span className="text-xs font-mono text-white/50">Agents: {certificationStatus.agents?.join(', ')}</span>
            </div>
          )}
          
          {/* Code Display */}
          <div className="flex-1 bg-black/40 p-4 overflow-auto">
            {activeTab === 'code' && (
              generatedCode ? (
                <pre className="text-sm font-mono text-green-400/90 leading-relaxed whitespace-pre-wrap">{generatedCode}</pre>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center">
                  <div className="text-6xl mb-4 opacity-20">◈</div>
                  <p className="text-lg font-mono text-white/40">Tell Franklin what to build</p>
                  <p className="text-sm font-mono text-white/25 mt-2">Example: "Build me a todo app API"</p>
                  <p className="text-sm font-mono text-white/25">Example: "Create a user authentication system"</p>
                </div>
              )
            )}
            {activeTab === 'spec' && (
              buildResult?.spec ? (
                <pre className="text-sm font-mono text-white/80 leading-relaxed whitespace-pre-wrap">{buildResult.spec}</pre>
              ) : (
                <p className="text-sm font-mono text-white/40 text-center py-8">Specification will appear here after build</p>
              )
            )}
            {activeTab === 'arch' && (
              buildResult?.architecture ? (
                <pre className="text-sm font-mono text-white/80 leading-relaxed whitespace-pre-wrap">{buildResult.architecture}</pre>
              ) : (
                <p className="text-sm font-mono text-white/40 text-center py-8">Architecture will appear here after build</p>
              )
            )}
          </div>
          
          {/* Terminal */}
          <div className="h-36 border-t border-white/20 bg-black/80 flex flex-col">
            <div className="h-8 px-4 border-b border-white/10 flex items-center justify-between">
              <span className="text-sm font-mono text-purple-400">◆ TERMINAL</span>
              {isBuilding && <span className="text-xs font-mono text-yellow-400 animate-pulse">Building...</span>}
            </div>
            <div ref={terminalRef} className="flex-1 overflow-y-auto px-4 py-2">
              {terminalOutput.map((line, idx) => (
                <div key={idx} className={`text-xs font-mono ${line.type === 'error' ? 'text-red-400' : line.type === 'success' ? 'text-green-400' : line.type === 'system' ? 'text-purple-400' : line.type === 'cmd' ? 'text-cyan-400' : 'text-white/60'}`}>{line.text}</div>
              ))}
            </div>
            <div className="h-8 px-4 border-t border-white/10 flex items-center">
              <span className="text-purple-400 mr-2">▶</span>
              <input type="text" value={terminalInput} onChange={(e) => setTerminalInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleTerminalSend()} placeholder="help, status, download..." className="flex-1 bg-transparent text-xs font-mono text-white placeholder-white/40 focus:outline-none" />
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN - GROK */}
        <div className="w-1/4 min-w-[280px] flex flex-col border-l border-white/20 bg-black/60">
          <div className="h-10 px-4 border-b border-white/20 flex items-center justify-between">
            <span className="text-sm font-mono text-green-400 font-semibold">◆ GROK</span>
            <span className="text-xs font-mono text-white/40">Analyst</span>
          </div>
          <div className="h-32 border-b border-white/10 flex items-center justify-center">
            <div className="w-24 h-24"><NeuralBrain themeColor="#22c55e" isThinking={grokLoading} size="lg" /></div>
          </div>
          <div ref={grokRef} className="flex-1 overflow-y-auto p-4 space-y-4">
            {grokChat.length === 0 ? (
              <div className="text-sm font-mono text-white/40 text-center py-8">Ask Grok to analyze code or explain concepts...</div>
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
          <div className="h-14 px-4 border-t border-green-500/40 bg-black/80 flex items-center gap-3">
            <span className="text-sm font-mono text-green-400">▶</span>
            <input type="text" value={grokInput} onChange={(e) => setGrokInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleGrokSend()} placeholder="Ask Grok..." className="flex-1 bg-transparent text-sm font-mono text-white placeholder-white/40 focus:outline-none" data-testid="grok-prompt" />
          </div>
        </div>
      </div>

      <div className="fixed bottom-2 right-6 z-50 text-xs font-mono text-white/30">◎ Made with Emergent</div>
    </div>
  );
};

// MAIN APP - TWO PAGES ONLY (Landing → IDE)
function App() {
  const [currentPage, setCurrentPage] = useState(PAGES.LANDING);
  if (currentPage === PAGES.LANDING) return <LandingPage onEnterApp={() => setCurrentPage(PAGES.IDE)} />;
  return <IDEPage onNavigate={setCurrentPage} />;
}

export default App;
