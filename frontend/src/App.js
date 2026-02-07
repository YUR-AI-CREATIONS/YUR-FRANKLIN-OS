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

// Stars Background Component
const StarsBackground = () => {
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
      for (let i = 0; i < 100; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          size: Math.random() * 1.5 + 0.5,
          speed: Math.random() * 0.5 + 0.2,
          phase: Math.random() * Math.PI * 2,
          type: 'regular'
        });
      }
      for (let i = 0; i < 12; i++) {
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
      
      // Subtle laser beams
      const lasers = [
        { x1: 0, y1: canvas.height * 0.3, angle: 15, alpha: 0.1, width: 1 },
        { x1: canvas.width, y1: canvas.height * 0.2, angle: 165, alpha: 0.08, width: 1 },
        { x1: 0, y1: canvas.height * 0.7, angle: 10, alpha: 0.08, width: 1 },
        { x1: canvas.width, y1: canvas.height * 0.8, angle: 170, alpha: 0.1, width: 1 },
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
  { id: 'neural_net', label: 'NEURAL_NET', icon: '◉' },
  { id: 'ouroboros', label: 'OUROBOROS', icon: '◈' },
  { id: 'lattice', label: 'LATTICE', icon: '▦' },
];

// Build Options
const BUILD_OPTIONS_ROW1 = [
  { id: 'frontend', label: 'Frontend' },
  { id: 'backend', label: 'Backend' },
  { id: 'database', label: 'Database' },
  { id: 'governance', label: 'Governance' },
];

const BUILD_OPTIONS_ROW2 = [
  { id: 'api', label: 'API' },
  { id: 'uiux', label: 'UI/UX' },
  { id: 'testing', label: 'Testing' },
  { id: 'deploy', label: 'Deploy' },
];

function App() {
  // State
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [showLanding, setShowLanding] = useState(true);
  
  // Panel states
  const [leftPanelView, setLeftPanelView] = useState('interface'); // 'interface' or 'project'
  const [rightTab, setRightTab] = useState('media'); // 'media', 'agents', 'workflows'
  
  // Selection states
  const [selectedMode, setSelectedMode] = useState('neural_chat');
  const [selectedBuildOptions, setSelectedBuildOptions] = useState([]);
  
  // Input/Loading states
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [session, setSession] = useState(null);
  
  // File tree state
  const [fileTree, setFileTree] = useState([
    { name: 'src', type: 'folder', expanded: true, children: [
      { name: 'components', type: 'folder', expanded: false, children: [] },
      { name: 'pages', type: 'folder', expanded: false, children: [] },
      { name: 'App.js', type: 'file' },
    ]},
    { name: 'backend', type: 'folder', expanded: false, children: [
      { name: 'routes', type: 'folder', expanded: false, children: [] },
      { name: 'models', type: 'folder', expanded: false, children: [] },
      { name: 'server.py', type: 'file' },
    ]},
    { name: 'README.md', type: 'file' },
  ]);
  const [fileTreeGlow, setFileTreeGlow] = useState(false);
  
  // Media/Agents/Workflows data
  const [mediaItems, setMediaItems] = useState([]);
  const [agents, setAgents] = useState([]);
  const [workflowNodes, setWorkflowNodes] = useState([]);

  const onConnect = useCallback((params) => {
    setEdges((eds) => addEdge({ ...params, animated: true }, eds));
  }, [setEdges]);

  // Toggle build option
  const toggleBuildOption = (id) => {
    setSelectedBuildOptions(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  // Handle send prompt
  const handleSendPrompt = async () => {
    if (!prompt.trim() || isLoading) return;
    
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/api/analyze`, {
        prompt: prompt.trim()
      });
      setSession(response.data);
      // Switch to workflows tab to show results
      setRightTab('workflows');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-save and glow effect when switching to project view
  const switchToProjectView = () => {
    setLeftPanelView('project');
    setFileTreeGlow(true);
    setTimeout(() => setFileTreeGlow(false), 2000);
  };

  // Render file tree recursively
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

  if (showLanding) {
    return <LandingPage onEnterApp={() => setShowLanding(false)} />;
  }

  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative">
      {/* Stars Background */}
      <StarsBackground />
      
      {/* Ghost FRANKLIN Text - 50% of landing opacity */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-[1]">
        <h1
          className="text-[clamp(2rem,10vw,8rem)] font-semibold tracking-[0.55em] select-none franklin-chrome-dim"
          style={{ fontFamily: "'Orbitron', sans-serif" }}
        >
          FRANKLIN
        </h1>
      </div>

      {/* LEFT PANEL */}
      <div className="absolute left-0 top-0 bottom-0 w-56 z-40 border-r border-white/10 bg-black/90 backdrop-blur-sm overflow-hidden">
        {/* Interface Mode View */}
        <div className={`absolute inset-0 transition-transform duration-300 ease-in-out ${leftPanelView === 'interface' ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="p-4 h-full flex flex-col">
            {/* Interface Mode */}
            <div className="mb-6">
              <div className="text-[10px] font-mono text-white/40 mb-3 tracking-wider">◆ INTERFACE_MODE</div>
              <div className="space-y-1">
                {INTERFACE_MODES.map(mode => (
                  <button
                    key={mode.id}
                    onClick={() => setSelectedMode(mode.id)}
                    className={`w-full text-left px-3 py-2 text-xs font-mono rounded transition-all ${
                      selectedMode === mode.id 
                        ? 'bg-white/10 text-white border-l-2 border-white/50' 
                        : 'text-white/50 hover:text-white/80 hover:bg-white/5'
                    }`}
                  >
                    <span className="mr-2 opacity-50">{mode.icon}</span>
                    {mode.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Workflow Industries */}
            <div className="mb-6">
              <div className="text-[10px] font-mono text-white/40 mb-2 tracking-wider cursor-pointer hover:text-white/60 flex items-center gap-2">
                <span>▶</span>
                <span>WORKFLOW_INDUSTRIES</span>
              </div>
            </div>

            {/* Spacer */}
            <div className="flex-1" />

            {/* Project Button */}
            <button
              onClick={switchToProjectView}
              className="w-full text-left px-3 py-3 text-xs font-mono text-white/50 hover:text-white/80 hover:bg-white/5 rounded border border-white/10 transition-all flex items-center gap-2"
            >
              <span>◀</span>
              <span>PROJECT</span>
            </button>
          </div>
        </div>

        {/* Project Files View */}
        <div className={`absolute inset-0 transition-transform duration-300 ease-in-out ${leftPanelView === 'project' ? 'translate-x-0' : 'translate-x-full'}`}>
          <div className={`p-4 h-full flex flex-col ${fileTreeGlow ? 'file-tree-glow' : ''}`}>
            {/* Back to Interface */}
            <button
              onClick={() => setLeftPanelView('interface')}
              className="w-full text-left px-3 py-2 text-xs font-mono text-white/50 hover:text-white/80 hover:bg-white/5 rounded mb-4 flex items-center gap-2"
            >
              <span>▶</span>
              <span>INTERFACE</span>
            </button>

            {/* Project Files Header */}
            <div className="text-[10px] font-mono text-white/40 mb-3 tracking-wider">◆ PROJECT_FILES</div>
            
            {/* File Tree */}
            <div className="flex-1 overflow-y-auto">
              {renderFileTree(fileTree)}
            </div>

            {/* Save Status */}
            <div className="text-[10px] font-mono text-green-400/70 mt-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              AUTO_SAVED
            </div>
          </div>
        </div>
      </div>

      {/* MAIN CANVAS */}
      <div className="absolute top-0 bottom-24 left-56 right-64 z-10">
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
      <div className="absolute right-0 top-0 bottom-24 w-64 z-40 border-l border-white/10 bg-black/90 backdrop-blur-sm">
        {/* Tabs */}
        <div className="flex border-b border-white/10">
          {['media', 'agents', 'workflows'].map(tab => (
            <button
              key={tab}
              onClick={() => setRightTab(tab)}
              className={`flex-1 py-3 text-[10px] font-mono uppercase tracking-wider transition-all ${
                rightTab === tab 
                  ? 'text-white border-b border-white/50 bg-white/5' 
                  : 'text-white/40 hover:text-white/60'
              }`}
            >
              {tab === 'media' && `Media (${mediaItems.length})`}
              {tab === 'agents' && 'Agents'}
              {tab === 'workflows' && 'Workflows'}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="p-4 h-full overflow-y-auto">
          {/* Media Tab */}
          {rightTab === 'media' && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="text-white/20 text-4xl mb-4">◇</div>
              <div className="text-[10px] font-mono text-white/40">NO_MEDIA_GENERATED</div>
              <div className="text-[9px] font-mono text-white/25 mt-2">Images and videos will appear here</div>
            </div>
          )}

          {/* Agents Tab */}
          {rightTab === 'agents' && (
            <div className="space-y-4">
              <div className="text-[10px] font-mono text-white/40 tracking-wider">◆ AGENTS</div>
              <div className="text-[10px] font-mono text-white/40 tracking-wider">◆ BOTS</div>
              <div className="text-[10px] font-mono text-white/40 tracking-wider">◆ CONNECTORS</div>
              <div className="pl-4 space-y-1 text-[10px] font-mono text-white/30">
                <div className="hover:text-white/60 cursor-pointer">○ Google Workspace</div>
                <div className="hover:text-white/60 cursor-pointer">○ Microsoft 365</div>
                <div className="hover:text-white/60 cursor-pointer">○ Notion</div>
                <div className="hover:text-white/60 cursor-pointer">○ Apple Music</div>
                <div className="hover:text-white/60 cursor-pointer">○ + Add Connector</div>
              </div>
            </div>
          )}

          {/* Workflows Tab */}
          {rightTab === 'workflows' && (
            <div className="space-y-4">
              <div className="text-[10px] font-mono text-white/40 tracking-wider">◆ ACTIVE_WORKFLOWS</div>
              {workflowNodes.length === 0 ? (
                <div className="text-[10px] font-mono text-white/30 text-center py-8">
                  No workflows yet.<br />
                  Select build options and send a prompt to begin.
                </div>
              ) : (
                <div className="space-y-2">
                  {workflowNodes.map((node, idx) => (
                    <div key={idx} className="p-2 bg-white/5 rounded text-xs font-mono text-white/70">
                      {node.label}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* BOTTOM PANEL - Build Options & Prompt */}
      <div className="absolute bottom-0 left-56 right-64 z-40 bg-black/90 border-t border-white/10 backdrop-blur-sm">
        <div className="p-4">
          {/* Build Options */}
          <div className="mb-3">
            <div className="text-[10px] font-mono text-white/40 mb-2 tracking-wider">◆ BUILD_OPTIONS</div>
            <div className="grid grid-cols-4 gap-2 mb-2">
              {BUILD_OPTIONS_ROW1.map(opt => (
                <button
                  key={opt.id}
                  onClick={() => toggleBuildOption(opt.id)}
                  className={`px-3 py-2 text-[10px] font-mono rounded border transition-all ${
                    selectedBuildOptions.includes(opt.id)
                      ? 'bg-white/15 border-white/30 text-white'
                      : 'bg-white/5 border-white/10 text-white/50 hover:border-white/20 hover:text-white/70'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
            <div className="grid grid-cols-4 gap-2">
              {BUILD_OPTIONS_ROW2.map(opt => (
                <button
                  key={opt.id}
                  onClick={() => toggleBuildOption(opt.id)}
                  className={`px-3 py-2 text-[10px] font-mono rounded border transition-all ${
                    selectedBuildOptions.includes(opt.id)
                      ? 'bg-white/15 border-white/30 text-white'
                      : 'bg-white/5 border-white/10 text-white/50 hover:border-white/20 hover:text-white/70'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Prompt Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendPrompt()}
              placeholder="Enter your prompt..."
              className="flex-1 bg-white/5 border border-white/10 rounded px-4 py-3 text-sm font-mono text-white placeholder-white/30 focus:outline-none focus:border-white/30"
            />
            <button
              onClick={handleSendPrompt}
              disabled={isLoading || !prompt.trim()}
              className="px-6 py-3 bg-white/10 border border-white/20 rounded text-white text-xs font-mono hover:bg-white/15 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
            >
              {isLoading ? (
                <span className="animate-spin">◐</span>
              ) : (
                <span>▶</span>
              )}
              SEND
            </button>
          </div>

          {/* Status */}
          <div className="text-[10px] font-mono text-white/30 mt-2">
            ◆ {selectedBuildOptions.length > 0 
              ? `SELECTED: ${selectedBuildOptions.map(id => id.toUpperCase()).join(' • ')}`
              : 'SELECT BUILD OPTIONS TO BEGIN'
            }
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
          filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.08));
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
      `}</style>
    </div>
  );
}

export default App;
