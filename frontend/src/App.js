import React, { useState, useCallback, useEffect, useRef } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
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

// Stars Background Component (matching landing page)
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
      
      // Draw stars
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
  { id: 'genesis', label: 'GENESIS', icon: '⚡' },
  { id: 'neural_net', label: 'NEURAL_NET', icon: '◉' },
  { id: 'ouroboros', label: 'OUROBOROS', icon: '◈' },
  { id: 'lattice', label: 'LATTICE', icon: '▦' },
];

// AI Models
const AI_MODELS = [
  { id: 'chatgpt', label: 'ChatGPT 4.0' },
  { id: 'gemini_pro', label: 'Gemini Pro 3' },
  { id: 'gemini_flash', label: 'Gemini Flash' },
  { id: 'gemini_nano', label: 'Gemini Nano' },
  { id: 'voice', label: 'Voice 3 (V0)' },
];

function App() {
  // State
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [showLanding, setShowLanding] = useState(true);
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [selectedMode, setSelectedMode] = useState('neural_chat');
  const [selectedModel, setSelectedModel] = useState('chatgpt');
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [session, setSession] = useState(null);
  const [coreStatus, setCoreStatus] = useState('online');
  const [mediaItems, setMediaItems] = useState([]);
  const [fileTree, setFileTree] = useState([]);
  const [fileTreeGlow, setFileTreeGlow] = useState(false);

  // Import LandingPage
  const LandingPage = React.lazy(() => import('./components/LandingPage'));

  const onConnect = useCallback((params) => {
    setEdges((eds) => addEdge({ ...params, animated: true }, eds));
  }, [setEdges]);

  // Handle send prompt
  const handleSendPrompt = async () => {
    if (!prompt.trim() || isLoading) return;
    
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/api/analyze`, {
        prompt: prompt.trim()
      });
      setSession(response.data);
      // Add nodes based on response
      // This will be expanded with the workflow nodes
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-save and glow effect
  const triggerAutoSave = () => {
    setFileTreeGlow(true);
    setTimeout(() => setFileTreeGlow(false), 2000);
  };

  // Close chat panel triggers auto-save
  const handleCloseChatPanel = () => {
    setLeftPanelOpen(false);
    triggerAutoSave();
  };

  if (showLanding) {
    return (
      <React.Suspense fallback={<div className="min-h-screen bg-black" />}>
        <LandingPage onEnterApp={() => setShowLanding(false)} />
      </React.Suspense>
    );
  }

  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative">
      {/* Stars Background */}
      <StarsBackground />
      
      {/* Ghost FRANKLIN Text - 50% opacity of landing */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-[1]">
        <h1
          className="text-[clamp(2rem,10vw,8rem)] font-semibold tracking-[0.55em] select-none franklin-chrome-dim"
          style={{ fontFamily: "'Orbitron', sans-serif" }}
        >
          FRANKLIN
        </h1>
      </div>

      {/* Header */}
      <header className="absolute top-0 left-0 right-0 z-50 flex items-center justify-between px-4 py-2 border-b border-white/10">
        <div className="flex items-center gap-4">
          <span className="text-xs text-cyan-400 font-mono">GROK</span>
          <span className="text-sm font-mono tracking-wider">SOVEREIGN XAI</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-white/50">CORE_STATUS</span>
          <span className={`w-2 h-2 rounded-full ${coreStatus === 'online' ? 'bg-red-500' : 'bg-green-500'}`} />
        </div>
      </header>

      {/* Left Panel - File Tree (static) + Chat (slides over) */}
      <div className={`absolute left-0 top-10 bottom-0 z-40 transition-all duration-300 ${leftPanelOpen ? 'w-64' : 'w-48'}`}>
        {/* File Tree (always visible when chat closed) */}
        <div className={`absolute inset-0 bg-black/80 border-r border-white/10 backdrop-blur-sm transition-opacity duration-300 ${leftPanelOpen ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
          <div className={`p-4 ${fileTreeGlow ? 'file-tree-glow' : ''}`}>
            <div className="text-xs font-mono text-cyan-400 mb-4">◆ PROJECT_FILES</div>
            <div className="space-y-1 text-xs font-mono text-white/60">
              <div className="flex items-center gap-2 hover:text-white/90 cursor-pointer">
                <span>▼</span> <span>src/</span>
              </div>
              <div className="ml-4 space-y-1">
                <div className="hover:text-white/90 cursor-pointer">▶ components/</div>
                <div className="hover:text-white/90 cursor-pointer">▶ pages/</div>
                <div className="hover:text-white/90 cursor-pointer">App.js</div>
              </div>
              <div className="flex items-center gap-2 hover:text-white/90 cursor-pointer">
                <span>▶</span> <span>backend/</span>
              </div>
              <div className="hover:text-white/90 cursor-pointer">README.md</div>
            </div>
          </div>
        </div>

        {/* Chat Panel (slides over file tree) */}
        <div className={`absolute inset-0 bg-black/90 border-r border-cyan-500/30 backdrop-blur-sm transition-transform duration-300 ${leftPanelOpen ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="p-4 h-full flex flex-col">
            {/* Interface Mode */}
            <div className="mb-4">
              <div className="text-xs font-mono text-cyan-400 mb-2">◆ INTERFACE_MODE</div>
              <div className="space-y-1">
                {INTERFACE_MODES.map(mode => (
                  <button
                    key={mode.id}
                    onClick={() => setSelectedMode(mode.id)}
                    className={`w-full text-left px-3 py-2 text-xs font-mono rounded transition-all ${
                      selectedMode === mode.id 
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' 
                        : 'text-white/60 hover:text-white/90 hover:bg-white/5'
                    }`}
                  >
                    <span className="mr-2">{mode.icon}</span>
                    {mode.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Workflow Industries */}
            <div className="mb-4">
              <div className="text-xs font-mono text-white/50 mb-2 cursor-pointer hover:text-white/70">
                {'>'} WORKFLOW_INDUSTRIES
              </div>
            </div>

            {/* Close button */}
            <button
              onClick={handleCloseChatPanel}
              className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-8 flex items-center justify-center text-white/30 hover:text-white/70"
            >
              ◀
            </button>
          </div>
        </div>

        {/* Toggle button when closed */}
        {!leftPanelOpen && (
          <button
            onClick={() => setLeftPanelOpen(true)}
            className="absolute -right-4 top-1/2 -translate-y-1/2 w-4 h-8 flex items-center justify-center text-white/30 hover:text-white/70 z-50"
          >
            ▶
          </button>
        )}
      </div>

      {/* Main Canvas */}
      <div className={`absolute top-10 bottom-0 z-10 transition-all duration-300 ${leftPanelOpen ? 'left-64' : 'left-48'} ${rightPanelOpen ? 'right-64' : 'right-12'}`}>
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
          <Controls className="!bg-black/50 !border-white/10" />
          <MiniMap 
            className="!bg-black/50 !border-white/10"
            nodeColor={() => '#00C8FF'}
            maskColor="rgba(0, 0, 0, 0.8)"
          />
        </ReactFlow>
      </div>

      {/* Right Panel - Media & Status */}
      <div className={`absolute right-0 top-10 bottom-0 z-40 transition-all duration-300 ${rightPanelOpen ? 'w-64' : 'w-12'}`}>
        <div className="h-full bg-black/80 border-l border-white/10 backdrop-blur-sm">
          {rightPanelOpen ? (
            <div className="p-4">
              {/* Tabs */}
              <div className="flex border-b border-white/10 mb-4">
                <button className="flex-1 py-2 text-xs font-mono text-cyan-400 border-b-2 border-cyan-400">
                  ◆ MEDIA (0)
                </button>
                <button className="flex-1 py-2 text-xs font-mono text-white/50 hover:text-white/70">
                  ◆ STATUS
                </button>
              </div>

              {/* Media Content */}
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <div className="text-cyan-400 text-2xl mb-4">◇</div>
                <div className="text-xs font-mono text-white/50">NO_MEDIA_GENERATED</div>
                <div className="text-[10px] font-mono text-white/30 mt-2">Images and videos will appear here</div>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center">
              <span className="text-white/30 text-xs writing-mode-vertical">MEDIA</span>
            </div>
          )}

          {/* Toggle */}
          <button
            onClick={() => setRightPanelOpen(!rightPanelOpen)}
            className="absolute -left-4 top-1/2 -translate-y-1/2 w-4 h-8 flex items-center justify-center text-white/30 hover:text-white/70"
          >
            {rightPanelOpen ? '▶' : '◀'}
          </button>
        </div>
      </div>

      {/* Bottom Panel - AI Model Selection & Prompt */}
      <div className={`absolute bottom-0 z-40 transition-all duration-300 ${leftPanelOpen ? 'left-64' : 'left-48'} ${rightPanelOpen ? 'right-64' : 'right-12'}`}>
        <div className="bg-black/90 border-t border-white/10 backdrop-blur-sm p-4">
          {/* AI Model Selection */}
          <div className="mb-4">
            <div className="text-xs font-mono text-cyan-400 mb-2">◆ AI_MODEL_SELECTION</div>
            <div className="grid grid-cols-2 gap-2 mb-2">
              {AI_MODELS.slice(0, 4).map(model => (
                <button
                  key={model.id}
                  onClick={() => setSelectedModel(model.id)}
                  className={`px-4 py-2 text-xs font-mono rounded border transition-all ${
                    selectedModel === model.id
                      ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400'
                      : 'bg-white/5 border-white/10 text-white/60 hover:border-white/30'
                  }`}
                >
                  {model.label}
                </button>
              ))}
            </div>
            <button
              onClick={() => setSelectedModel('voice')}
              className={`w-full px-4 py-2 text-xs font-mono rounded border transition-all ${
                selectedModel === 'voice'
                  ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400'
                  : 'bg-white/5 border-white/10 text-white/60 hover:border-white/30'
              }`}
            >
              Voice 3 (V0)
            </button>
          </div>

          {/* Prompt Input */}
          <div className="text-center text-xs font-mono text-white/30 mb-2">
            {'>> SELECT INDUSTRY TO START...'}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendPrompt()}
              placeholder="Enter your prompt..."
              className="flex-1 bg-white/5 border border-white/10 rounded px-4 py-3 text-sm font-mono text-white placeholder-white/30 focus:outline-none focus:border-cyan-500/50"
            />
            <button
              onClick={handleSendPrompt}
              disabled={isLoading || !prompt.trim()}
              className="px-6 py-3 bg-cyan-500/20 border border-cyan-500/50 rounded text-cyan-400 text-xs font-mono hover:bg-cyan-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              ▶ SEND
            </button>
          </div>
          <div className="text-xs font-mono text-cyan-400 mt-2">
            ◆ NO WORKFLOW SELECTED • SELECT INDUSTRY TO BEGIN
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
          0% { box-shadow: 0 0 0 rgba(0, 200, 255, 0); }
          50% { box-shadow: 0 0 30px rgba(0, 200, 255, 0.5); }
          100% { box-shadow: 0 0 0 rgba(0, 200, 255, 0); }
        }

        .writing-mode-vertical {
          writing-mode: vertical-rl;
          text-orientation: mixed;
        }
      `}</style>
    </div>
  );
}

export default App;
