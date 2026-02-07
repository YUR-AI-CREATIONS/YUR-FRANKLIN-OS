import React, { useState, useCallback, useEffect, useRef } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
} from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';

import StageNode from './components/nodes/StageNode';
import AmbiguityNode from './components/nodes/AmbiguityNode';
import ResolutionNode from './components/nodes/ResolutionNode';
import SpecNode from './components/nodes/SpecNode';
import { LandingPage } from './components/LandingPage';

import './App.css';

const API = process.env.REACT_APP_BACKEND_URL || '';

const nodeTypes = {
  stage: StageNode,
  ambiguity: AmbiguityNode,
  resolution: ResolutionNode,
  spec: SpecNode,
};

// Stars & Galactic Background Component
const GalacticBackground = () => {
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
      for (let i = 0; i < 120; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          size: Math.random() * 1.5 + 0.5,
          speed: Math.random() * 0.5 + 0.2,
          phase: Math.random() * Math.PI * 2,
          type: 'regular'
        });
      }
      for (let i = 0; i < 15; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          size: Math.random() * 1.5 + 1.5,
          speed: Math.random() * 0.3 + 0.1,
          phase: Math.random() * Math.PI * 2,
          type: 'bright'
        });
      }
      return stars;
    };
    
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const lasers = [
        { x1: 0, y1: canvas.height * 0.3, angle: 15, alpha: 0.12, width: 1 },
        { x1: canvas.width, y1: canvas.height * 0.2, angle: 165, alpha: 0.08, width: 1 },
        { x1: 0, y1: canvas.height * 0.7, angle: 10, alpha: 0.08, width: 1 },
        { x1: canvas.width, y1: canvas.height * 0.8, angle: 170, alpha: 0.12, width: 1 },
      ];
      
      lasers.forEach(laser => {
        const length = Math.max(canvas.width, canvas.height) * 1.5;
        const rad = laser.angle * Math.PI / 180;
        const x2 = laser.x1 + Math.cos(rad) * length;
        const y2 = laser.y1 + Math.sin(rad) * length;
        
        ctx.shadowBlur = 15;
        ctx.shadowColor = `rgba(255, 255, 255, ${laser.alpha})`;
        ctx.beginPath();
        ctx.strokeStyle = `rgba(255, 255, 255, ${laser.alpha})`;
        ctx.lineWidth = laser.width;
        ctx.moveTo(laser.x1, laser.y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        ctx.shadowBlur = 0;
      });
      
      if (starsRef.current) {
        starsRef.current.forEach(star => {
          const twinkle = Math.sin(time * star.speed * 0.05 + star.phase) * 0.5 + 0.5;
          
          if (star.type === 'bright') {
            ctx.shadowBlur = 12;
            ctx.shadowColor = `rgba(255, 255, 255, ${twinkle * 0.6})`;
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.size * twinkle + 0.5, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${twinkle * 0.9 + 0.1})`;
            ctx.fill();
            ctx.shadowBlur = 0;
          } else {
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.size * (twinkle * 0.3 + 0.7), 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${twinkle * 0.6 + 0.2})`;
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
  }, []);
  
  return <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none" />;
};

// Interface Mode Items
const INTERFACE_MODES = [
  { id: 'neural_chat', label: 'NEURAL_CHAT', icon: '⚡' },
  { id: 'vision_ai', label: 'VISION_AI', icon: '◐' },
  { id: 'code_editor', label: 'CODE_EDITOR', icon: '▣' },
  { id: 'genesis', label: 'GENESIS', icon: '⬡' },
  { id: 'agent_builder', label: 'AGENT_BUILDER', icon: '◉' },
  { id: 'workflow', label: 'WORKFLOW', icon: '◈' },
];

// Build Categories with nested subcategories
const BUILD_CATEGORIES = [
  { 
    id: 'frontend', 
    label: 'Frontend',
    subcategories: ['React', 'Vue', 'Angular', 'Svelte', 'Next.js', 'Components', 'Styling']
  },
  { 
    id: 'backend', 
    label: 'Backend',
    subcategories: ['Node.js', 'Python', 'FastAPI', 'Express', 'GraphQL', 'REST API', 'Auth']
  },
  { 
    id: 'database', 
    label: 'Database',
    subcategories: ['PostgreSQL', 'MongoDB', 'MySQL', 'Redis', 'Supabase', 'Firebase', 'Schema']
  },
  { 
    id: 'deploy', 
    label: 'Deploy',
    subcategories: ['Vercel', 'Render', 'AWS', 'Docker', 'CI/CD', 'Governance', 'Testing']
  },
];

function App() {
  // State
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [showLanding, setShowLanding] = useState(true);
  
  // Panel states
  const [leftPanelView, setLeftPanelView] = useState('interface');
  const [rightTab, setRightTab] = useState('agents');
  
  // Selection states
  const [selectedMode, setSelectedMode] = useState('neural_chat');
  const [expandedCategory, setExpandedCategory] = useState(null);
  const [selectedSubcategories, setSelectedSubcategories] = useState([]);
  
  // Data states
  const [dashboard, setDashboard] = useState(null);
  const [marketplaceAgents, setMarketplaceAgents] = useState([]);
  const [botTiers, setBotTiers] = useState([]);
  const [academyPrograms, setAcademyPrograms] = useState([]);
  
  // Chat/Output states
  const [chatInput, setChatInput] = useState('');
  const [outputLog, setOutputLog] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // File tree state
  const [fileTree, setFileTree] = useState([
    { name: 'src', type: 'folder', expanded: true, children: [
      { name: 'components', type: 'folder', expanded: false, children: [] },
      { name: 'pages', type: 'folder', expanded: false, children: [] },
      { name: 'App.js', type: 'file' },
    ]},
    { name: 'backend', type: 'folder', expanded: false, children: [
      { name: 'routes', type: 'folder', expanded: false, children: [] },
      { name: 'server.py', type: 'file' },
    ]},
    { name: 'README.md', type: 'file' },
  ]);
  const [fileTreeGlow, setFileTreeGlow] = useState(false);
  
  const outputRef = useRef(null);

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        const [dashRes, agentsRes, tiersRes, programsRes] = await Promise.all([
          axios.get(`${API}/api/franklin/dashboard`),
          axios.get(`${API}/api/marketplace/agents/summary`),
          axios.get(`${API}/api/bots/tiers`),
          axios.get(`${API}/api/academy/programs`)
        ]);
        setDashboard(dashRes.data);
        setMarketplaceAgents(agentsRes.data.agents || []);
        setBotTiers(tiersRes.data.tiers || []);
        setAcademyPrograms(programsRes.data.programs || []);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      }
    };
    if (!showLanding) {
      loadData();
    }
  }, [showLanding]);

  // Auto-scroll output
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [outputLog]);

  const onConnect = useCallback((params) => {
    setEdges((eds) => addEdge({ ...params, animated: true }, eds));
  }, [setEdges]);

  // Add output message
  const addOutput = (phase, message, type = 'info') => {
    setOutputLog(prev => [...prev, {
      phase,
      message,
      type,
      timestamp: new Date().toISOString()
    }]);
  };

  // Handle Genesis command
  const handleGenesis = async (mission) => {
    setIsLoading(true);
    addOutput('GENESIS', `Starting mission: ${mission}`, 'system');
    
    try {
      const response = await axios.post(`${API}/api/grok/genesis`, {
        mission: mission
      });
      
      if (response.data.output) {
        response.data.output.forEach(entry => {
          addOutput(entry.phase.toUpperCase(), entry.message, 
            entry.phase === 'success' ? 'success' : 
            entry.phase === 'failure' || entry.phase === 'fatal' ? 'error' : 'info');
        });
      }
      
      if (response.data.success) {
        addOutput('COMPLETE', `Task completed successfully!`, 'success');
        // Trigger file tree glow
        setFileTreeGlow(true);
        setTimeout(() => setFileTreeGlow(false), 2000);
      } else {
        addOutput('FAILED', `Task failed after ${response.data.task?.attempts || 0} attempts`, 'error');
      }
    } catch (err) {
      addOutput('ERROR', err.response?.data?.detail || err.message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle chat/command input
  const handleChatSend = async () => {
    if (!chatInput.trim() || isLoading) return;
    
    const input = chatInput.trim();
    setChatInput('');
    
    // Check for Genesis command
    if (input.toLowerCase().startsWith('/genesis ') || input.toLowerCase().startsWith('/build ')) {
      const mission = input.replace(/^\/(?:genesis|build)\s+/i, '');
      await handleGenesis(mission);
      return;
    }
    
    // Regular chat - analyze prompt
    addOutput('USER', input, 'user');
    setIsLoading(true);
    
    try {
      const response = await axios.post(`${API}/api/analyze`, { prompt: input });
      addOutput('FRANKLIN', `Analysis complete. Confidence: ${response.data.confidence_score}%`, 'system');
      
      if (response.data.analysis?.ambiguities?.length > 0) {
        response.data.analysis.ambiguities.forEach(amb => {
          addOutput('QUESTION', `[${amb.priority}] ${amb.question}`, 'warning');
        });
      }
      
      if (response.data.can_proceed) {
        addOutput('READY', 'Specification ready. Use /genesis or /build to proceed.', 'success');
      }
    } catch (err) {
      addOutput('ERROR', err.response?.data?.detail || err.message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Toggle category expansion
  const toggleCategory = (id) => {
    setExpandedCategory(expandedCategory === id ? null : id);
  };

  // Toggle subcategory selection
  const toggleSubcategory = (sub) => {
    setSelectedSubcategories(prev => 
      prev.includes(sub) ? prev.filter(x => x !== sub) : [...prev, sub]
    );
  };

  // Switch to project view with glow
  const switchToProjectView = () => {
    setLeftPanelView('project');
    setFileTreeGlow(true);
    setTimeout(() => setFileTreeGlow(false), 2000);
  };

  // Render file tree
  const renderFileTree = (items, depth = 0) => {
    return items.map((item, idx) => (
      <div key={idx} style={{ marginLeft: depth * 12 }}>
        <div 
          className="flex items-center gap-2 py-1 px-2 hover:bg-white/5 rounded cursor-pointer text-xs font-mono text-white/60 hover:text-white/90"
          onClick={() => {
            if (item.type === 'folder') {
              item.expanded = !item.expanded;
              setFileTree([...fileTree]);
            }
          }}
        >
          <span className="text-white/40">
            {item.type === 'folder' ? (item.expanded ? '▼' : '▶') : '○'}
          </span>
          <span>{item.name}</span>
        </div>
        {item.type === 'folder' && item.expanded && item.children && (
          renderFileTree(item.children, depth + 1)
        )}
      </div>
    ));
  };

  // Get phase color
  const getPhaseColor = (type) => {
    switch(type) {
      case 'success': return 'text-green-400';
      case 'error': return 'text-red-400';
      case 'warning': return 'text-amber-400';
      case 'user': return 'text-cyan-400';
      case 'system': return 'text-purple-400';
      default: return 'text-white/70';
    }
  };

  if (showLanding) {
    return <LandingPage onEnterApp={() => setShowLanding(false)} />;
  }

  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="franklin-os">
      {/* Galactic Background with Stars */}
      <GalacticBackground />
      
      {/* Galactic Liquid Glassmorphism Overlay */}
      <div className="absolute inset-0 z-[1] pointer-events-none">
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            background: `
              radial-gradient(ellipse at 20% 30%, rgba(100, 100, 120, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at 80% 20%, rgba(80, 80, 100, 0.1) 0%, transparent 40%),
              radial-gradient(ellipse at 50% 80%, rgba(60, 60, 80, 0.12) 0%, transparent 45%)
            `
          }}
        />
      </div>
      
      {/* Ghost FRANKLIN Text */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-[2]">
        <h1
          className="text-[clamp(3rem,12vw,10rem)] font-semibold tracking-[0.55em] select-none franklin-chrome-dim"
          style={{ fontFamily: "'Orbitron', sans-serif" }}
        >
          FRANKLIN
        </h1>
      </div>

      {/* LEFT PANEL */}
      <div className="absolute left-0 top-0 bottom-0 w-56 z-40 border-r border-white/10 bg-black/80 backdrop-blur-md overflow-hidden">
        {/* Interface Mode View */}
        <div className={`absolute inset-0 transition-transform duration-300 ease-in-out ${leftPanelView === 'interface' ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="p-4 h-full flex flex-col">
            <div className="text-[10px] font-mono text-white/40 mb-4 tracking-wider">◆ INTERFACE_MODE</div>
            
            <div className="space-y-1">
              {INTERFACE_MODES.map(mode => (
                <button
                  key={mode.id}
                  onClick={() => setSelectedMode(mode.id)}
                  data-testid={`mode-${mode.id}`}
                  className={`w-full text-left px-3 py-2 rounded text-xs font-mono transition-all flex items-center gap-3 ${
                    selectedMode === mode.id 
                      ? 'bg-white/10 text-white border border-white/20' 
                      : 'text-white/50 hover:text-white/80 hover:bg-white/5'
                  }`}
                >
                  <span className="text-sm">{mode.icon}</span>
                  <span>{mode.label}</span>
                </button>
              ))}
            </div>

            <div className="flex-1" />
            
            <button
              onClick={switchToProjectView}
              data-testid="project-btn"
              className="w-full px-3 py-3 text-xs font-mono text-white/80 hover:bg-white/5 rounded border border-white/10 transition-all flex items-center gap-2"
            >
              <span>◀</span>
              <span>PROJECT</span>
            </button>
          </div>
        </div>

        {/* Project Files View */}
        <div className={`absolute inset-0 transition-transform duration-300 ease-in-out ${leftPanelView === 'project' ? 'translate-x-0' : 'translate-x-full'}`}>
          <div className={`p-4 h-full flex flex-col ${fileTreeGlow ? 'file-tree-glow' : ''}`}>
            <button
              onClick={() => setLeftPanelView('interface')}
              className="w-full text-left px-3 py-2 text-xs font-mono text-white/50 hover:text-white/80 hover:bg-white/5 rounded mb-4 flex items-center gap-2"
            >
              <span>▶</span>
              <span>INTERFACE</span>
            </button>

            <div className="text-[10px] font-mono text-white/40 mb-3 tracking-wider">◆ PROJECT_FILES</div>
            
            <div className="flex-1 overflow-y-auto">
              {renderFileTree(fileTree)}
            </div>

            <div className="text-[10px] font-mono text-green-400/70 mt-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              AUTO_SAVED
            </div>
          </div>
        </div>
      </div>

      {/* CENTER OUTPUT AREA - Scrolling Output */}
      <div className="absolute top-4 left-60 right-68 bottom-72 z-30 flex justify-center">
        <div 
          ref={outputRef}
          className="w-[500px] h-full overflow-y-auto px-4 py-6 space-y-2 scrollbar-thin"
          data-testid="output-area"
        >
          {outputLog.length === 0 ? (
            <div className="text-center text-white/30 font-mono text-sm pt-20">
              <div className="text-4xl mb-4 opacity-30">⬡</div>
              <p>FRANKLIN OS Ready</p>
              <p className="text-xs mt-2">Type a command or describe what you want to build...</p>
              <p className="text-xs text-white/20 mt-4">Commands: /genesis, /build</p>
            </div>
          ) : (
            outputLog.map((entry, idx) => (
              <div key={idx} className="font-mono text-sm animate-fade-in">
                <span className="text-white/40 text-xs">[{entry.phase}]</span>
                <span className={`ml-2 ${getPhaseColor(entry.type)}`}>{entry.message}</span>
              </div>
            ))
          )}
          {isLoading && (
            <div className="font-mono text-sm text-purple-400 animate-pulse flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-purple-400 rounded-full animate-ping" />
              Processing...
            </div>
          )}
        </div>
      </div>

      {/* MAIN CANVAS (Hidden behind output, for workflow) */}
      <div className="absolute top-0 left-56 right-64 bottom-64 z-10 opacity-30">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.1}
          maxZoom={4}
          className="bg-transparent"
        >
          <Background color="transparent" />
          <Controls className="!bg-black/50 !border-white/10 !rounded" />
          <MiniMap 
            className="!bg-black/50 !border-white/10 !rounded"
            nodeColor={() => '#ffffff'}
            maskColor="rgba(0, 0, 0, 0.8)"
          />
        </ReactFlow>
      </div>

      {/* RIGHT PANEL - 3 Tabs */}
      <div className="absolute right-0 top-0 bottom-64 w-64 z-40 border-l border-white/10 bg-black/80 backdrop-blur-md">
        <div className="flex border-b border-white/10">
          {['agents', 'bots', 'academy'].map(tab => (
            <button
              key={tab}
              onClick={() => setRightTab(tab)}
              data-testid={`tab-${tab}`}
              className={`flex-1 py-3 text-[10px] font-mono uppercase tracking-wider transition-all ${
                rightTab === tab 
                  ? 'text-white border-b border-white/50 bg-white/5' 
                  : 'text-white/40 hover:text-white/60'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="p-4 h-full overflow-y-auto">
          {/* Agents Tab */}
          {rightTab === 'agents' && (
            <div className="space-y-3">
              <div className="text-[10px] font-mono text-white/40 tracking-wider mb-2">◆ ELITE_AGENTS</div>
              {marketplaceAgents.map((agent, idx) => (
                <div 
                  key={idx} 
                  className="p-3 rounded bg-white/5 border border-white/10 hover:border-white/20 transition-all cursor-pointer"
                  data-testid={`agent-card-${idx}`}
                >
                  <div className="text-xs font-mono text-white/90">{agent.name}</div>
                  <div className="text-[9px] text-white/50 mt-1 truncate">{agent.primary_specialization}</div>
                  <div className="flex justify-between mt-2 text-[9px]">
                    <span className="text-green-400">★ {agent.client_satisfaction}</span>
                    <span className="text-cyan-400">${agent.starter_price}/mo</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Bots Tab */}
          {rightTab === 'bots' && (
            <div className="space-y-3">
              <div className="text-[10px] font-mono text-white/40 tracking-wider mb-2">◆ BOT_TIERS</div>
              {botTiers.map((tier, idx) => (
                <div 
                  key={idx} 
                  className="p-3 rounded bg-white/5 border border-white/10 hover:border-white/20 transition-all cursor-pointer"
                  data-testid={`tier-card-${idx}`}
                >
                  <div className="text-xs font-mono text-white/90">{tier.name}</div>
                  <div className="text-[9px] text-white/50 mt-1">{tier.description.slice(0, 60)}...</div>
                  <div className="flex justify-between mt-2 text-[9px]">
                    <span className="text-amber-400">{tier.autonomy_level.toUpperCase()}</span>
                    <span className="text-cyan-400">${tier.min_usd.toLocaleString()}-${tier.max_usd.toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Academy Tab */}
          {rightTab === 'academy' && (
            <div className="space-y-3">
              <div className="text-[10px] font-mono text-white/40 tracking-wider mb-2">◆ TRAINING_PROGRAMS</div>
              {academyPrograms.slice(0, 5).map((program, idx) => (
                <div 
                  key={idx} 
                  className="p-3 rounded bg-white/5 border border-white/10 hover:border-white/20 transition-all cursor-pointer"
                  data-testid={`program-card-${idx}`}
                >
                  <div className="text-xs font-mono text-white/90 truncate">{program.name}</div>
                  <div className="text-[9px] text-white/50 mt-1">{program.field} • {program.duration_weeks} weeks</div>
                  <div className="flex justify-between mt-2 text-[9px]">
                    <span className="text-purple-400">{program.level}</span>
                    <span className="text-cyan-400">${program.cost.toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* BOTTOM PANEL - Build Categories + Chat Input */}
      <div className="absolute bottom-0 left-56 right-64 h-64 z-40 bg-black/90 border-t border-white/10 backdrop-blur-md flex flex-col">
        {/* Build Category Buttons - Top Row */}
        <div className="flex border-b border-white/10 shrink-0">
          {BUILD_CATEGORIES.map(cat => (
            <button
              key={cat.id}
              onClick={() => toggleCategory(cat.id)}
              data-testid={`cat-${cat.id}`}
              className={`flex-1 py-2 text-[10px] font-mono uppercase tracking-wider transition-all border-r border-white/10 last:border-r-0 ${
                expandedCategory === cat.id 
                  ? 'text-white bg-white/10' 
                  : 'text-white/50 hover:text-white/80 hover:bg-white/5'
              }`}
            >
              {cat.label}
              <span className="ml-1 opacity-50">{expandedCategory === cat.id ? '▼' : '▶'}</span>
            </button>
          ))}
        </div>

        {/* Expanded Subcategories */}
        {expandedCategory && (
          <div className="flex flex-wrap gap-2 p-2 border-b border-white/10 bg-white/5 shrink-0">
            {BUILD_CATEGORIES.find(c => c.id === expandedCategory)?.subcategories.map(sub => (
              <button
                key={sub}
                onClick={() => toggleSubcategory(sub)}
                className={`px-3 py-1 text-[9px] font-mono rounded transition-all ${
                  selectedSubcategories.includes(sub)
                    ? 'bg-white/20 text-white border border-white/30'
                    : 'bg-white/5 text-white/50 border border-white/10 hover:border-white/20'
                }`}
              >
                {sub}
              </button>
            ))}
          </div>
        )}

        {/* Dashboard Status Bar */}
        {dashboard && (
          <div className="flex items-center gap-4 px-4 py-2 border-b border-white/10 bg-white/5 text-[9px] font-mono shrink-0">
            <span className="text-green-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
              SENTINEL: {dashboard.runtime?.sentinel?.status || 'ACTIVE'}
            </span>
            <span className="text-cyan-400">PQC: ONLINE</span>
            <span className="text-purple-400">AUDIT: {dashboard.runtime?.audit?.total_entries || 0} entries</span>
            <span className="text-amber-400">AGENTS: {marketplaceAgents.length}</span>
            <span className="text-white/40">BOTS: {botTiers.length} tiers</span>
          </div>
        )}

        {/* Main Chat/Command Input */}
        <div className="flex-1 flex flex-col min-h-0 p-4">
          <div className="text-[9px] font-mono text-white/40 mb-2">◆ COMMAND_INPUT</div>
          <div className="flex-1 flex items-end">
            <div className="w-full flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
                placeholder="Describe what you want to build or type /genesis <mission>..."
                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm font-mono text-white placeholder-white/30 focus:outline-none focus:border-white/30"
                data-testid="command-input"
                disabled={isLoading}
              />
              <button
                onClick={handleChatSend}
                disabled={isLoading || !chatInput.trim()}
                data-testid="send-btn"
                className="px-6 py-3 bg-white/10 border border-white/20 rounded-lg text-sm font-mono text-white hover:bg-white/20 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
              >
                {isLoading ? '◐' : 'SEND ▶'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Styles */}
      <style>{`
        .franklin-chrome-dim {
          background: linear-gradient(
            135deg,
            rgba(60, 60, 60, 1) 0%,
            rgba(100, 100, 100, 1) 15%,
            rgba(160, 160, 160, 1) 30%,
            rgba(200, 200, 200, 1) 45%,
            rgba(160, 160, 160, 1) 55%,
            rgba(100, 100, 100, 1) 70%,
            rgba(60, 60, 60, 1) 85%,
            rgba(120, 120, 120, 1) 100%
          );
          background-size: 200% 200%;
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: chromeShimmer 25s ease-in-out infinite;
          filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.1));
          opacity: 0.35;
        }
        
        @keyframes chromeShimmer {
          0% { background-position: 200% 200%; }
          50% { background-position: 0% 0%; }
          100% { background-position: 200% 200%; }
        }

        .file-tree-glow {
          animation: glowPulse 2s ease-out;
        }

        @keyframes glowPulse {
          0% { box-shadow: inset 0 0 0 rgba(100, 200, 255, 0); }
          50% { box-shadow: inset 0 0 30px rgba(100, 200, 255, 0.3); }
          100% { box-shadow: inset 0 0 0 rgba(100, 200, 255, 0); }
        }

        @keyframes fade-in {
          from { opacity: 0; transform: translateY(-4px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }

        .scrollbar-thin::-webkit-scrollbar {
          width: 4px;
        }

        .scrollbar-thin::-webkit-scrollbar-track {
          background: transparent;
        }

        .scrollbar-thin::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 2px;
        }
      `}</style>
    </div>
  );
}

export default App;
