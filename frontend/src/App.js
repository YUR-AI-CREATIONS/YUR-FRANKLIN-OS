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
import NeuralBrain from './components/NeuralBrain';

import './App.css';

const API = process.env.REACT_APP_BACKEND_URL || '';

const nodeTypes = {
  stage: StageNode,
  ambiguity: AmbiguityNode,
  resolution: ResolutionNode,
  spec: SpecNode,
};

// Folder Item Component for nested files
const FolderItem = ({ name, files = [], defaultOpen = false }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  return (
    <div className="mb-1">
      <div 
        className="cursor-pointer py-1 px-1 text-[10px] font-mono tracking-wider flex items-center gap-1.5 hover:bg-white/5 rounded"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className={`w-2.5 text-white/40 transition-transform text-[8px] ${isOpen ? 'rotate-90' : ''}`}>▶</span>
        <span className="text-white/70">{name}</span>
      </div>
      {isOpen && (
        <div className="ml-3 border-l border-white/10 pl-2">
          {files.map((file, idx) => (
            <div key={idx} className="py-0.5 px-1 text-[9px] font-mono text-white/50 hover:text-white/70 hover:bg-white/5 rounded cursor-pointer">
              {file}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Full-Height Stacked Folder Component
// Black panels with faint line, small tab sticks out when closed for re-opening
const StackedFolder = ({ title, zIndex = 10, isOpen, onToggle, children, side = 'left', stackOffset = 0 }) => {
  // When closed, slide most of the way off but leave a clickable tab (24px) sticking out
  // Stack offset ensures each closed tab is visible and doesn't overlap
  const closedPosition = side === 'left' 
    ? `calc(-100% + ${24 + (stackOffset * 20)}px)`
    : `calc(100% - ${24 + (stackOffset * 20)}px)`;
  
  const slideAmount = isOpen ? '0' : closedPosition;
  
  return (
    <div 
      className="absolute inset-0 transition-all duration-500 ease-in-out"
      style={{ 
        zIndex,
        transform: `translateX(${slideAmount})`
      }}
    >
      {/* The folder content - black with faint border */}
      <div className="h-full w-full bg-black/98 backdrop-blur-md flex flex-col" style={{ borderRight: side === 'left' ? '1px solid rgba(255,255,255,0.08)' : 'none', borderLeft: side === 'right' ? '1px solid rgba(255,255,255,0.08)' : 'none' }}>
        {/* Button at top to toggle */}
        <button
          onClick={onToggle}
          className="w-full py-2 px-3 text-[10px] font-mono tracking-wider flex items-center justify-between hover:bg-white/5 transition-all border-b border-white/5"
        >
          <span className="text-white/60">{isOpen ? '◀' : '▶'} {title}</span>
          <span className="text-white/30 text-[8px]">{isOpen ? 'COLLAPSE' : 'EXPAND'}</span>
        </button>
        {/* Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {children}
        </div>
      </div>
      
      {/* Clickable edge when closed - the reveal tab */}
      {!isOpen && (
        <div 
          onClick={onToggle}
          className="absolute top-0 bottom-0 w-6 cursor-pointer hover:bg-white/5 transition-all flex items-center justify-center"
          style={{ 
            [side === 'left' ? 'right' : 'left']: 0,
            borderLeft: side === 'right' ? '1px solid rgba(255,255,255,0.1)' : 'none',
            borderRight: side === 'left' ? '1px solid rgba(255,255,255,0.1)' : 'none'
          }}
        >
          <span className="text-white/40 text-[10px]" style={{ writingMode: 'vertical-rl' }}>{title}</span>
        </div>
      )}
    </div>
  );
};

// Nested Expandable Section inside folders
const NestedSection = ({ title, icon = '◆', color = 'text-white/60', defaultOpen = false, children }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  return (
    <div className="border-b border-white/5">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full py-2 px-3 text-[10px] font-mono tracking-wider flex items-center gap-2 hover:bg-white/5 transition-all"
      >
        <span className={`transition-transform ${isOpen ? 'rotate-90' : ''}`}>▶</span>
        <span className={color}>{icon}</span>
        <span className="text-white/80">{title}</span>
      </button>
      {isOpen && (
        <div className="px-4 pb-2">
          {children}
        </div>
      )}
    </div>
  );
};

// Page Navigation
const PAGES = {
  LANDING: 'landing',
  IDE: 'ide',
  WORKFLOW: 'workflow'
};

// Stars & Galactic Background Component - SPARKLY STARS (toned down)
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
      // Regular twinkling stars
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
      // Sparkle stars (reduced)
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
      // Super bright sparkle stars (reduced)
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
            
            // Draw subtle cross sparkle
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

// Interface Mode Items
const INTERFACE_MODES = [
  { id: 'neural_chat', label: 'NEURAL_CHAT', icon: '⚡' },
  { id: 'vision_ai', label: 'VISION_AI', icon: '◐' },
  { id: 'code_editor', label: 'CODE_EDITOR', icon: '▣' },
  { id: 'genesis', label: 'GENESIS', icon: '⬡' },
  { id: 'agent_builder', label: 'AGENT_BUILDER', icon: '◉' },
  { id: 'workflow', label: 'WORKFLOW', icon: '◈' },
];

// Build Categories
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

// ============================================================================
// PAGE 3: ELECTRIC WORKFLOW
// ============================================================================
const ElectricWorkflowPage = ({ onBack, workflowNodes, workflowEdges, onNodesChange, onEdgesChange }) => {
  const [selectedNode, setSelectedNode] = useState(null);
  const [buildStatus, setBuildStatus] = useState(null);
  
  // Panel collapse states
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  
  // Chat/Terminal states
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

  // Load build status
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

  // Auto-scroll chat
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

  // Handle chat send
  const handleChatSend = async () => {
    if (!chatInput.trim() || isProcessing) return;
    
    const input = chatInput.trim();
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: input }]);
    setIsProcessing(true);
    
    // Add terminal output
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

  // Apply AI recommendation
  const applyRecommendation = (rec) => {
    setChatHistory(prev => [...prev, { role: 'user', content: `Apply: ${rec.text}` }]);
    setTerminalOutput(prev => [...prev, { type: 'cmd', text: `> Applying: ${rec.text}` }]);
    setAiRecommendations(prev => prev.filter(r => r.id !== rec.id));
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

      {/* LEFT SLIDE PANEL - Chat Response (Full Height) */}
      <div className={`absolute top-16 bottom-12 z-40 bg-black/90 border-r border-white/10 backdrop-blur-md transition-all duration-300 ${leftPanelOpen ? 'left-0 w-72' : '-left-72 w-72'}`}>
        <button
          onClick={() => setLeftPanelOpen(!leftPanelOpen)}
          className="absolute -right-8 top-1/2 -translate-y-1/2 w-8 h-16 bg-black/80 border border-white/10 rounded-r-lg flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-all"
        >
          {leftPanelOpen ? '◀' : '▶'}
        </button>
        
        <div className="p-4 h-full flex flex-col">
          <div className="text-[10px] font-mono text-white/40 tracking-wider mb-3">◆ CHAT RESPONSE</div>
          
          {/* Chat Messages */}
          <div ref={chatRef} className="flex-1 overflow-y-auto space-y-3 scrollbar-thin">
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={`text-xs font-mono ${msg.role === 'user' ? 'text-cyan-400' : msg.role === 'system' ? 'text-amber-400' : 'text-white/80'}`}>
                <span className="text-white/30 text-[9px]">[{msg.role.toUpperCase()}]</span>
                <p className="mt-1 leading-relaxed">{msg.content}</p>
              </div>
            ))}
            {isProcessing && (
              <div className="flex items-center gap-2 text-purple-400 text-xs">
                <div className="w-5 h-5">
                  <NeuralBrain themeColor="#a855f7" isThinking={true} size="sm" />
                </div>
                Processing...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* RIGHT SLIDE PANEL - Workflow Controls (Full Height) */}
      <div className={`absolute top-16 bottom-12 z-40 bg-black/90 border-l border-white/10 backdrop-blur-md transition-all duration-300 ${rightPanelOpen ? 'right-0 w-72' : '-right-72 w-72'}`}>
        <button
          onClick={() => setRightPanelOpen(!rightPanelOpen)}
          className="absolute -left-8 top-1/2 -translate-y-1/2 w-8 h-16 bg-black/80 border border-white/10 rounded-l-lg flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-all"
        >
          {rightPanelOpen ? '▶' : '◀'}
        </button>
        
        <div className="p-4 h-full flex flex-col overflow-y-auto">
          <div className="text-[10px] font-mono text-white/40 tracking-wider mb-4">◆ WORKFLOW CONTROLS</div>
          
          {/* Stage Progress */}
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

          {/* Selected Node */}
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

          {/* Add Node */}
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

          {/* Actions */}
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

      {/* Main Workflow Canvas - Center */}
      <div className={`absolute top-16 bottom-12 z-10 transition-all duration-300 ${leftPanelOpen ? 'left-72' : 'left-0'} ${rightPanelOpen ? 'right-72' : 'right-0'}`}>
        <ReactFlow
          nodes={workflowNodes}
          edges={workflowEdges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.2}
          maxZoom={2}
          className="!bg-transparent"
          style={{ background: 'transparent' }}
          defaultEdgeOptions={{
            style: { stroke: '#00ff88', strokeWidth: 2 },
            animated: true
          }}
        >
          <Background color="rgba(255,255,255,0.02)" gap={30} style={{ opacity: 0.3 }} />
          <Controls className="!bg-black/70 !border-white/20 !rounded-lg" />
        </ReactFlow>
      </div>

      {/* BOTTOM BAR - Chat Prompt | Project Info | Terminal */}
      <div className="absolute bottom-0 left-0 right-0 h-12 z-40 bg-black/95 border-t border-white/10 backdrop-blur-md flex items-center">
        
        {/* Chat Prompt - Left */}
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

        {/* Project Info - Left Center */}
        <div className="w-64 h-full border-r border-white/10 px-3 flex items-center">
          <div className="text-[9px] font-mono text-white/50">
            <span className="text-white/30">PROJECT:</span> <span className="text-cyan-400">{buildStatus?.project_name || 'No Project'}</span>
            <span className="mx-2 text-white/20">|</span>
            <span className="text-white/30">STATUS:</span> <span className={buildStatus?.status === 'certified' ? 'text-green-400' : 'text-amber-400'}>{buildStatus?.status?.toUpperCase() || 'IDLE'}</span>
          </div>
        </div>

        {/* Terminal - Center (Wide) */}
        <div className="flex-1 h-full px-4 flex items-center overflow-hidden">
          <div className="text-[9px] font-mono text-green-400 truncate">
            {terminalOutput.length > 0 ? terminalOutput[terminalOutput.length - 1].text : '> System ready.'}
          </div>
        </div>
      </div>

      {/* Chrome Pulsing Title Styles */}
      <style>{`
        .workflow-chrome-title {
          background: linear-gradient(
            90deg,
            rgba(100, 100, 100, 0.8) 0%,
            rgba(180, 180, 180, 1) 25%,
            rgba(255, 255, 255, 1) 50%,
            rgba(180, 180, 180, 1) 75%,
            rgba(100, 100, 100, 0.8) 100%
          );
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
        <div 
          className="w-full h-full"
          style={{
            backgroundImage: `
              linear-gradient(rgba(0, 255, 136, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0, 255, 136, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px'
          }}
        />
      </div>
    </div>
  );
};

// ============================================================================
// PAGE 2: MAIN IDE
// ============================================================================
const IDEPage = ({ onNavigate, workflowNodes, setWorkflowNodes, workflowEdges, setWorkflowEdges }) => {
  // Main panel slide states
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [agentsPanelOpen, setAgentsPanelOpen] = useState(true);
  const [agentChatOpen, setAgentChatOpen] = useState(false);
  
  // Individual slide panel states (each section slides independently)
  // Stacked folder states (left side) - which folders are slid open
  // Higher z-index = front. When you close a folder, you see the one behind it
  const [leftFolders, setLeftFolders] = useState({
    franklin: true,      // Front - Franklin chat (z-index 40)
    providers: true,     // Behind franklin - LLM providers (z-index 30)
    projects: true,      // Behind providers - Projects (z-index 20)
    build: true          // Back - Frontend/Backend/DB/Deploy (z-index 10)
  });
  
  const toggleLeftFolder = (folder) => {
    setLeftFolders(prev => ({ ...prev, [folder]: !prev[folder] }));
  };
  
  // Stacked folder states (right side)
  const [rightFolders, setRightFolders] = useState({
    agents: true,
    bots: true,
    academy: true
  });
  
  const toggleRightFolder = (folder) => {
    setRightFolders(prev => ({ ...prev, [folder]: !prev[folder] }));
  };
  
  // Panel states
  const [leftPanelView, setLeftPanelView] = useState('interface');
  const [rightTab, setRightTab] = useState('agents');
  
  // Selection states
  const [selectedMode, setSelectedMode] = useState('neural_chat');
  const [expandedCategory, setExpandedCategory] = useState(null);
  const [selectedSubcategories, setSelectedSubcategories] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [selectedBot, setSelectedBot] = useState(null);
  const [selectedProgram, setSelectedProgram] = useState(null);
  
  // Detail panel state (for agent/bot engagement)
  const [detailPanel, setDetailPanel] = useState(null);
  const [detailInput, setDetailInput] = useState('');
  const [detailLoading, setDetailLoading] = useState(false);
  
  // Franklin Onboard Chat - Load from localStorage
  const [franklinChat, setFranklinChat] = useState(() => {
    const saved = localStorage.getItem('franklin_chat');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return [{ role: 'franklin', content: 'Welcome to FRANKLIN OS. I\'m here to help you navigate and build. What would you like to create today?' }];
      }
    }
    return [{ role: 'franklin', content: 'Welcome to FRANKLIN OS. I\'m here to help you navigate and build. What would you like to create today?' }];
  });
  const [franklinInput, setFranklinInput] = useState('');
  const [franklinLoading, setFranklinLoading] = useState(false);
  
  // Grok Response Area - Load from localStorage
  const [grokResponses, setGrokResponses] = useState(() => {
    const saved = localStorage.getItem('grok_responses');
    return saved ? JSON.parse(saved) : [];
  });
  
  // Active Tasks for tracking background work
  const [activeTasks, setActiveTasks] = useState([]);
  
  // Data states
  const [dashboard, setDashboard] = useState(null);
  const [marketplaceAgents, setMarketplaceAgents] = useState([]);
  const [botTiers, setBotTiers] = useState([]);
  const [academyPrograms, setAcademyPrograms] = useState([]);
  
  // Chat/Output states - Load from localStorage
  const [chatInput, setChatInput] = useState('');
  const [outputLog, setOutputLog] = useState(() => {
    const saved = localStorage.getItem('output_log');
    return saved ? JSON.parse(saved) : [];
  });
  const [conversationHistory, setConversationHistory] = useState(() => {
    const saved = localStorage.getItem('conversation_history');
    return saved ? JSON.parse(saved) : [];
  });
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
  const detailRef = useRef(null);
  const franklinRef = useRef(null);

  // Auto-scroll Franklin chat
  useEffect(() => {
    if (franklinRef.current) {
      franklinRef.current.scrollTop = franklinRef.current.scrollHeight;
    }
  }, [franklinChat]);

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
    loadData();
    
    // Poll for active tasks every 5 seconds
    const pollTasks = setInterval(async () => {
      try {
        const res = await axios.get(`${API}/api/tasks/active`);
        setActiveTasks(res.data.tasks || []);
      } catch (e) {
        // Ignore errors
      }
    }, 5000);
    
    return () => clearInterval(pollTasks);
  }, []);

  // Save Franklin chat to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('franklin_chat', JSON.stringify(franklinChat));
  }, [franklinChat]);
  
  // Save output log to localStorage
  useEffect(() => {
    localStorage.setItem('output_log', JSON.stringify(outputLog.slice(-100))); // Keep last 100
  }, [outputLog]);
  
  // Save conversation history to localStorage
  useEffect(() => {
    localStorage.setItem('conversation_history', JSON.stringify(conversationHistory.slice(-50)));
  }, [conversationHistory]);
  
  // Save grok responses to localStorage
  useEffect(() => {
    localStorage.setItem('grok_responses', JSON.stringify(grokResponses.slice(-20)));
  }, [grokResponses]);

  // Auto-scroll output
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [outputLog]);

  // Get color class based on output type
  const getOutputColor = (type) => {
    switch(type) {
      case 'success': return 'text-green-400';
      case 'error': return 'text-red-400';
      case 'warning': return 'text-amber-400';
      case 'user': return 'text-cyan-400';
      case 'system': return 'text-purple-400';
      default: return 'text-white/60';
    }
  };

  // Add output message and Grok response
  const addOutput = (phase, message, type = 'info') => {
    setOutputLog(prev => [...prev, {
      phase,
      message,
      type,
      timestamp: new Date().toISOString()
    }]);
    // Also add to Grok responses for the bottom panel
    if (phase.toLowerCase().includes('grok') || phase === 'GENESIS' || phase === 'COMPLETE' || phase === 'FAILED' || phase === 'SIGNOFF') {
      setGrokResponses(prev => [...prev.slice(-10), { phase, message, type, timestamp: new Date().toISOString() }]);
    }
  };

  // Add node to workflow
  const addWorkflowNode = (label, status = 'pending') => {
    const newNode = {
      id: `node_${Date.now()}`,
      type: 'stage',
      position: { x: Math.random() * 500, y: Math.random() * 300 },
      data: { label, status, type: 'stage' }
    };
    setWorkflowNodes(prev => [...prev, newNode]);
  };

  // Handle Genesis command - Full build orchestration
  const handleGenesis = async (mission) => {
    setIsLoading(true);
    addOutput('GENESIS', `Initiating mission: ${mission}`, 'system');
    addWorkflowNode(`Genesis: ${mission.slice(0, 30)}...`, 'active');
    
    try {
      // Use the new orchestrator for full agent workflow
      const response = await axios.post(`${API}/api/build-orchestrator/build`, {
        mission: mission
      });
      
      if (response.data.output) {
        // Display each agent's output
        response.data.output.forEach(entry => {
          const agentInfo = entry.agent ? ` [${entry.agent}]` : '';
          addOutput(entry.phase.toUpperCase() + agentInfo, entry.message, 
            entry.type === 'success' ? 'success' : 
            entry.type === 'error' ? 'error' : 'info');
        });
      }
      
      // Add workflow nodes from the build
      if (response.data.workflow_nodes) {
        response.data.workflow_nodes.forEach(node => {
          addWorkflowNode(node.label, node.status);
        });
      }
      
      // Show governance log
      if (response.data.governance_log && response.data.governance_log.length > 0) {
        addOutput('GOVERNANCE', `${response.data.governance_log.length} governance actions logged`, 'info');
      }
      
      // Show agents involved
      if (response.data.agents_involved && response.data.agents_involved.length > 0) {
        addOutput('AGENTS', `Build involved: ${response.data.agents_involved.join(', ')}`, 'success');
      }
      
      if (response.data.success) {
        addOutput('SIGNOFF', 'Build complete - Audited, Verified, Certified, Signed Off by Franklin', 'success');
        setFileTreeGlow(true);
        setTimeout(() => setFileTreeGlow(false), 2000);
      } else {
        addOutput('FAILED', 'Build encountered issues', 'error');
      }
    } catch (err) {
      // Fallback to original grok endpoint
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
          addOutput('COMPLETE', 'Task completed successfully!', 'success');
        }
      } catch (fallbackErr) {
        addOutput('ERROR', err.response?.data?.detail || err.message, 'error');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Handle chat/command input - User talks to Franklin
  const handleChatSend = async () => {
    if (!chatInput.trim() || isLoading) return;
    
    const input = chatInput.trim();
    setChatInput('');
    
    // Check for /genesis or /build commands
    if (input.toLowerCase().startsWith('/genesis ') || input.toLowerCase().startsWith('/build ')) {
      const mission = input.replace(/^\/(?:genesis|build)\s+/i, '');
      await handleGenesis(mission);
      return;
    }
    
    if (input.toLowerCase() === '/workflow') {
      onNavigate(PAGES.WORKFLOW);
      return;
    }
    
    if (input.toLowerCase() === '/clear') {
      setOutputLog([]);
      setConversationHistory([]);
      setGrokResponses([]);
      addOutput('SYSTEM', 'Conversation cleared.', 'system');
      return;
    }
    
    if (input.toLowerCase() === '/whiteboard') {
      // Show current whiteboard state
      try {
        const response = await axios.get(`${API}/api/build-orchestrator/whiteboard`);
        if (response.data.sections && response.data.sections.length > 0) {
          addOutput('WHITEBOARD', `Session: ${response.data.mission}`, 'info');
          response.data.sections.forEach(section => {
            addOutput(section.phase.toUpperCase(), `[${section.name}] ${section.verified ? '✓ Verified' : ''} ${section.certified ? '✓ Certified' : ''} ${section.signed_off ? '✓ Signed' : ''}`, 'success');
          });
        } else {
          addOutput('WHITEBOARD', 'No active build session. Start with /genesis <mission>', 'info');
        }
      } catch (e) {
        addOutput('WHITEBOARD', 'No active build session', 'info');
      }
      return;
    }
    
    if (input.toLowerCase() === '/help') {
      addOutput('HELP', 'FRANKLIN OS Commands:', 'system');
      addOutput('HELP', '/genesis <mission> - Start a full build with all agents', 'info');
      addOutput('HELP', '/build <mission> - Same as /genesis', 'info');
      addOutput('HELP', '/whiteboard - View current build session', 'info');
      addOutput('HELP', '/workflow - Open workflow visualization', 'info');
      addOutput('HELP', '/clear - Clear conversation', 'info');
      addOutput('HELP', '/help - Show this help', 'info');
      addOutput('HELP', '', 'info');
      addOutput('HELP', 'Or just type naturally to chat with Franklin!', 'success');
      addOutput('HELP', 'Franklin will coordinate Genesis, Architect, Implementer & Healer agents.', 'info');
      return;
    }
    
    addOutput('USER', input, 'user');
    setIsLoading(true);
    
    // Add to conversation history
    const newHistory = [...conversationHistory, { role: 'user', content: input }];
    setConversationHistory(newHistory);
    
    try {
      // Use orchestrator chat - Franklin perfect-prompts Grok
      const response = await axios.post(`${API}/api/build-orchestrator/chat`, { 
        message: input
      });
      
      if (response.data.response) {
        addOutput('FRANKLIN', response.data.response, 'system');
        setConversationHistory([...newHistory, { role: 'assistant', content: response.data.response }]);
        
        // If ready to build, suggest it
        if (response.data.ready_to_build) {
          addOutput('TIP', 'Ready to build? Type /genesis followed by your project description.', 'info');
        }
      }
    } catch (err) {
      // Fallback to direct Grok chat
      try {
        const response = await axios.post(`${API}/api/grok/chat`, { 
          message: input,
          history: newHistory.slice(-10)
        });
        
        if (response.data.response) {
          addOutput('FRANKLIN', response.data.response, 'system');
          setConversationHistory([...newHistory, { role: 'assistant', content: response.data.response }]);
        }
      } catch (fallbackErr) {
        addOutput('FRANKLIN', `I'm here to help you build software. Try "/genesis create a todo app" or describe what you want to build.`, 'system');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const toggleCategory = (id) => {
    setExpandedCategory(expandedCategory === id ? null : id);
  };

  const toggleSubcategory = (sub) => {
    // Toggle selection state
    const isSelected = selectedSubcategories.includes(sub);
    setSelectedSubcategories(prev => 
      isSelected ? prev.filter(x => x !== sub) : [...prev, sub]
    );
    
    // Trigger action based on subcategory
    if (!isSelected) {
      addOutput('BUILD', `Selected: ${sub}`, 'system');
      addOutput('TIP', `Use /genesis with ${sub} or type what you want to build`, 'info');
    }
  };

  // Handle subcategory click - start building
  const handleSubcategoryAction = (category, subcategory) => {
    addOutput('BUILD', `Initiating ${category} > ${subcategory}...`, 'system');
    setChatInput(`/genesis Create a ${subcategory.toLowerCase()} ${category.toLowerCase()} component`);
  };

  const switchToProjectView = () => {
    setLeftPanelView('project');
    setFileTreeGlow(true);
    setTimeout(() => setFileTreeGlow(false), 2000);
  };

  // Generate agent greeting based on specialization
  const getAgentGreeting = (agent) => {
    const spec = agent.primary_specialization?.toLowerCase() || '';
    if (spec.includes('sales') || spec.includes('business')) {
      return `Hey there! I'm ${agent.name}, your go-to expert for closing deals and driving revenue. What business challenge can I help you tackle today? Need help with lead generation, pitch decks, or scaling your sales operation?`;
    } else if (spec.includes('product') || spec.includes('ux') || spec.includes('design')) {
      return `Hi! I'm ${agent.name}. I specialize in creating products people love. Whether you need help with user research, wireframes, or building an MVP, I'm here. What are you building?`;
    } else if (spec.includes('ai') || spec.includes('ml') || spec.includes('data')) {
      return `Greetings. I'm ${agent.name}, specializing in AI/ML and data science. I can help with predictive models, data pipelines, or implementing machine learning solutions. What data problem are you trying to solve?`;
    } else if (spec.includes('marketing') || spec.includes('brand')) {
      return `Hello! ${agent.name} here. I help brands tell their story and reach the right audience. Need help with positioning, campaigns, or content strategy? Let's make some noise.`;
    } else if (spec.includes('operations') || spec.includes('supply')) {
      return `Hi, I'm ${agent.name}. I optimize operations and streamline processes. Whether it's supply chain, logistics, or operational efficiency, I can help you run leaner. What's slowing you down?`;
    }
    return `Hello! I'm ${agent.name}, specializing in ${agent.primary_specialization}. How can I assist you today?`;
  };

  // Generate bot tier greeting
  const getBotGreeting = (tier) => {
    const tierNum = tier.tier_level || 1;
    if (tierNum === 1) {
      return `Scout Bot activated. I handle low-risk reconnaissance: lead discovery, bid scanning, and basic data gathering. I operate with strict compliance controls. What do you need me to find?`;
    } else if (tierNum === 2) {
      return `Operator Bot online. I can engage in outreach, manage communications, and execute multi-step workflows. I require approval for financial transactions. What operation should I run?`;
    } else if (tierNum === 3) {
      return `Commander Bot ready. I have elevated autonomy for complex missions, deal negotiations, and resource coordination. I can operate semi-independently within your parameters. What's the mission?`;
    } else if (tierNum === 4) {
      return `Sovereign Bot activated. Maximum autonomy mode. I can execute full campaigns, manage portfolios, and make strategic decisions within defined boundaries. What objective should I pursue?`;
    }
    return `${tier.name} ready for deployment. ${tier.description}`;
  };

  // Handle agent click - open detail panel and agent chat
  const handleAgentClick = async (agent) => {
    setSelectedAgent(agent);
    setSelectedBot(null);
    setSelectedProgram(null);
    
    const greeting = getAgentGreeting(agent);
    setDetailPanel({
      type: 'agent',
      data: agent,
      conversation: [{ role: 'agent', content: greeting }]
    });
    setDetailInput('');
    setAgentChatOpen(true); // Open the agent chat slide panel
  };

  // Handle bot tier click - open detail panel
  const handleBotClick = async (tier) => {
    setSelectedBot(tier);
    setSelectedAgent(null);
    setSelectedProgram(null);
    
    const greeting = getBotGreeting(tier);
    setDetailPanel({
      type: 'bot',
      data: tier,
      conversation: [{ role: 'bot', content: greeting }]
    });
    setDetailInput('');
    setAgentChatOpen(true);
  };

  // Handle academy program click - open detail panel
  const handleProgramClick = async (program) => {
    setSelectedProgram(program);
    setSelectedAgent(null);
    setSelectedBot(null);
    
    const greeting = `Welcome to the ${program.name}! This ${program.duration_weeks}-week ${program.level} program covers ${program.field}. Ready to level up your skills? Ask me anything about the curriculum or enrollment process.`;
    setDetailPanel({
      type: 'program',
      data: program,
      conversation: [{ role: 'program', content: greeting }]
    });
    setDetailInput('');
    setAgentChatOpen(true);
  };

  // Close detail panel
  const closeDetailPanel = () => {
    setDetailPanel(null);
    setSelectedAgent(null);
    setSelectedBot(null);
    setSelectedProgram(null);
    setAgentChatOpen(false);
  };

  // Send message in detail panel
  const handleDetailSend = async () => {
    if (!detailInput.trim() || detailLoading || !detailPanel) return;
    
    const input = detailInput.trim();
    setDetailInput('');
    
    // Add user message to conversation
    const newConversation = [...detailPanel.conversation, { role: 'user', content: input }];
    setDetailPanel({ ...detailPanel, conversation: newConversation });
    setDetailLoading(true);
    
    try {
      // Handle Franklin separately - use orchestrator
      if (detailPanel.type === 'franklin') {
        const response = await axios.post(`${API}/api/build-orchestrator/chat`, {
          message: input
        });
        
        const reply = response.data.response || "I'm here to help you build. What would you like to create?";
        setDetailPanel(prev => ({
          ...prev,
          conversation: [...prev.conversation, { role: 'assistant', content: reply }]
        }));
        
        // Also update the Franklin panel chat
        setFranklinChat(prev => [...prev, { role: 'user', content: input }, { role: 'franklin', content: reply }]);
        return;
      }
      
      // Build context based on panel type
      let systemContext = '';
      if (detailPanel.type === 'agent') {
        systemContext = `You are ${detailPanel.data.name}, an elite AI agent specializing in ${detailPanel.data.primary_specialization}. You have a ${detailPanel.data.client_satisfaction}★ rating. Be helpful, professional, and stay in character. Engage the user with questions relevant to your expertise. Keep responses concise but valuable.`;
      } else if (detailPanel.type === 'bot') {
        systemContext = `You are a ${detailPanel.data.name} in the FRANKLIN OS bot tier system. Your autonomy level is ${detailPanel.data.autonomy_level}. You handle tasks like: ${detailPanel.data.task_types?.join(', ') || 'various operations'}. Stay in character as an operational bot. Be direct and task-focused.`;
      } else {
        systemContext = `You are an instructor for the ${detailPanel.data.name} program. This is a ${detailPanel.data.duration_weeks}-week ${detailPanel.data.level} program in ${detailPanel.data.field}. Help the user understand the program, curriculum, and enrollment. Be encouraging and informative.`;
      }
      
      const response = await axios.post(`${API}/api/agent/chat`, {
        message: input,
        context: systemContext,
        history: newConversation.slice(-6)
      });
      
      const reply = response.data.response || "I'm here to help. Could you tell me more about what you need?";
      setDetailPanel(prev => ({
        ...prev,
        conversation: [...prev.conversation, { role: detailPanel.type, content: reply }]
      }));
    } catch (err) {
      // Fallback response
      const fallbackReplies = {
        agent: `That's a great question. Based on my expertise in ${detailPanel.data.primary_specialization}, I'd recommend we schedule a deeper dive. What's your timeline?`,
        bot: `Acknowledged. I can execute that task within my operational parameters. Shall I proceed?`,
        program: `Excellent question! This topic is covered in week 3 of the curriculum. Would you like more details about the program structure?`,
        franklin: `I understand. Let me help you with that. Would you like me to initiate a build process? Try typing /genesis followed by your project idea.`
      };
      setDetailPanel(prev => ({
        ...prev,
        conversation: [...prev.conversation, { role: detailPanel.type === 'franklin' ? 'assistant' : detailPanel.type, content: fallbackReplies[detailPanel.type] || fallbackReplies.franklin }]
      }));
    } finally {
      setDetailLoading(false);
    }
  };

  // Handle Franklin onboard chat
  const handleFranklinSend = async () => {
    if (!franklinInput.trim() || franklinLoading) return;
    
    const input = franklinInput.trim();
    setFranklinInput('');
    setFranklinChat(prev => [...prev, { role: 'user', content: input }]);
    setFranklinLoading(true);
    
    // Check for build commands in Franklin chat
    if (input.toLowerCase().startsWith('/genesis ') || input.toLowerCase().startsWith('/build ')) {
      const mission = input.replace(/^\/(?:genesis|build)\s+/i, '');
      setFranklinChat(prev => [...prev, { role: 'franklin', content: `Initiating build: ${mission}. Check the terminal for progress.` }]);
      setFranklinLoading(false);
      setChatInput(`/genesis ${mission}`);
      setTimeout(() => handleChatSend(), 100);
      return;
    }
    
    try {
      // Use orchestrator chat - Franklin perfect-prompts Grok
      const response = await axios.post(`${API}/api/build-orchestrator/chat`, {
        message: input
      });
      
      const reply = response.data.response || "I can help you with that. Would you like me to guide you through the process?";
      setFranklinChat(prev => [...prev, { role: 'franklin', content: reply }]);
      
      // If ready to build, add a hint
      if (response.data.ready_to_build) {
        setFranklinChat(prev => [...prev, { 
          role: 'franklin', 
          content: "💡 I sense you want to build something! Type '/genesis' followed by your project description to start the full agent workflow." 
        }]);
      }
    } catch (err) {
      // Fallback to direct Grok chat
      try {
        const response = await axios.post(`${API}/api/grok/chat`, {
          message: input,
          history: franklinChat.slice(-6)
        });
        const reply = response.data.response || "I'm here to help. What would you like to build?";
        setFranklinChat(prev => [...prev, { role: 'franklin', content: reply }]);
      } catch (e) {
        setFranklinChat(prev => [...prev, { role: 'franklin', content: "I'm here to help. Type /genesis followed by your project idea to start building, or describe what you want to create." }]);
      }
    } finally {
      setFranklinLoading(false);
    }
  };

  // Auto-scroll detail panel
  useEffect(() => {
    if (detailRef.current) {
      detailRef.current.scrollTop = detailRef.current.scrollHeight;
    }
  }, [detailPanel?.conversation]);

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

  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="franklin-os">
      <GalacticBackground />
      
      {/* FRANKLIN Chrome Branding - GHOST FORMAT, BIGGER, 1/4 DOWN */}
      <div className="fixed inset-x-0 top-[18%] flex justify-center pointer-events-none z-[5] overflow-hidden">
        <h1 
          className="select-none franklin-chrome-ide whitespace-nowrap"
          style={{ 
            fontFamily: "'Orbitron', sans-serif",
            fontSize: 'clamp(4rem,13vw,11rem)',
            fontWeight: 600,
            letterSpacing: '0.45em',
            paddingLeft: '0.22em',
          }}
        >
          FRANKLIN
        </h1>
      </div>
      
      {/* Chrome shimmer styles for IDE - GHOST FORMAT - STATIC, NO ANIMATION */}
      <style>{`
        .franklin-chrome-ide {
          background: linear-gradient(
            180deg,
            rgba(120, 120, 120, 0.35) 0%,
            rgba(160, 160, 160, 0.4) 50%,
            rgba(120, 120, 120, 0.35) 100%
          );
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.08));
        }
      `}</style>

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
          <span className="text-purple-400">AUDIT: {dashboard?.runtime?.audit?.total_entries || 0} entries</span>
          <span className="text-amber-400">AGENTS: {marketplaceAgents.length}</span>
        </div>
      </div>

      {/* LEFT SIDE - Full Height Stacked Sliding Folders */}
      <div className="absolute top-10 bottom-40 left-0 w-72 z-40 overflow-visible" data-testid="left-folders">
        
        {/* FOLDER 4 (Back) - BUILD: Frontend/Backend/Database/Deploy */}
        <StackedFolder 
          title="BUILD" 
          zIndex={10} 
          isOpen={leftFolders.build} 
          onToggle={() => toggleLeftFolder('build')}
          stackOffset={3}
        >
          {/* Build Category Tabs */}
          <div className="flex border-b border-white/10">
            {['FRONTEND', 'BACKEND', 'DATABASE', 'DEPLOY'].map((tab, i) => (
              <button 
                key={tab}
                onClick={() => setExpandedCategory(tab.toLowerCase())}
                className={`flex-1 py-2 text-[8px] font-mono tracking-wider transition-all ${expandedCategory === tab.toLowerCase() ? 'bg-white/10 text-white border-b border-cyan-400' : 'text-white/40 hover:text-white/70'}`}
              >
                {tab}
              </button>
            ))}
          </div>
          
          {/* Nested content based on selected tab - 9 items each */}
          <div className="flex-1 overflow-y-auto p-2 scrollbar-thin">
            {expandedCategory === 'frontend' && (
              <div className="space-y-0.5 text-[9px] font-mono">
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-cyan-400">React Components</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-cyan-400">Vue.js</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-cyan-400">Angular</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-cyan-400">Svelte</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-cyan-400">Next.js</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-cyan-400">TailwindCSS</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-cyan-400">Styled Components</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-cyan-400">CSS Modules</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-cyan-400">Framer Motion</div>
              </div>
            )}
            {expandedCategory === 'backend' && (
              <div className="space-y-0.5 text-[9px] font-mono">
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-green-400">Node.js Express</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-green-400">Python FastAPI</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-green-400">Django REST</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-green-400">GraphQL</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-green-400">REST API</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-green-400">WebSockets</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-green-400">JWT Auth</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-green-400">OAuth 2.0</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-green-400">Microservices</div>
              </div>
            )}
            {expandedCategory === 'database' && (
              <div className="space-y-0.5 text-[9px] font-mono">
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-blue-400">PostgreSQL</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-blue-400">MongoDB</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-blue-400">MySQL</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-blue-400">Redis</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-blue-400">Supabase</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-blue-400">Firebase</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-blue-400">SQLite</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-blue-400">Prisma ORM</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-blue-400">Vector DB</div>
              </div>
            )}
            {expandedCategory === 'deploy' && (
              <div className="space-y-0.5 text-[9px] font-mono">
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-purple-400">Vercel</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-purple-400">Render</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-purple-400">AWS</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-purple-400">Docker</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-purple-400">Kubernetes</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-purple-400">CI/CD Pipeline</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-purple-400">GitHub Actions</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-purple-400">Governance</div>
                <div className="py-1.5 px-2 text-white/70 hover:bg-white/5 rounded cursor-pointer border-l-2 border-transparent hover:border-purple-400">Testing Suite</div>
              </div>
            )}
            {!expandedCategory && (
              <div className="text-[10px] text-white/40 font-mono text-center mt-8">
                Select a category above
              </div>
            )}
          </div>
          
          {/* Workflow button at bottom */}
          <div className="p-3 border-t border-white/10">
            <button
              onClick={() => onNavigate(PAGES.WORKFLOW)}
              className="w-full px-3 py-2 text-[9px] font-mono text-cyan-400 hover:bg-cyan-400/10 rounded border border-cyan-400/30 transition-all"
              data-testid="open-workflow-left"
            >
              ◈ OPEN WORKFLOW
            </button>
          </div>
        </StackedFolder>

        {/* FOLDER 3 - PROJECTS SAVED */}
        <StackedFolder 
          title="PROJECTS" 
          zIndex={20} 
          isOpen={leftFolders.projects} 
          onToggle={() => toggleLeftFolder('projects')}
          stackOffset={2}
        >
          <div className="p-3 border-b border-white/10">
            <div className="text-[10px] font-mono text-white/80 tracking-wider">◆ SAVED PROJECTS</div>
          </div>
          <div className="flex-1 overflow-y-auto p-3 scrollbar-thin">
            <NestedSection title="Project Alpha" icon="📁" color="text-amber-400" defaultOpen>
              <div className="space-y-1 text-[9px] font-mono text-white/60">
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex items-center gap-2">
                  <span className="text-white/30">▶</span> src/
                </div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex items-center gap-2">
                  <span className="text-white/30">▶</span> schemas/
                </div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex items-center gap-2">
                  <span className="text-white/30">○</span> README.md
                </div>
              </div>
            </NestedSection>
            <NestedSection title="Project Beta" icon="📁" color="text-amber-400">
              <div className="space-y-1 text-[9px] font-mono text-white/60">
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex items-center gap-2">
                  <span className="text-white/30">▶</span> api/
                </div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex items-center gap-2">
                  <span className="text-white/30">▶</span> tests/
                </div>
              </div>
            </NestedSection>
            <NestedSection title="Franklin OS" icon="📁" color="text-cyan-400">
              <div className="space-y-1 text-[9px] font-mono text-white/60">
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex items-center gap-2">
                  <span className="text-white/30">▶</span> frontend/
                </div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex items-center gap-2">
                  <span className="text-white/30">▶</span> backend/
                </div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex items-center gap-2">
                  <span className="text-white/30">▶</span> services/
                </div>
              </div>
            </NestedSection>
          </div>
        </StackedFolder>

        {/* FOLDER 2 - LLM PROVIDERS */}
        <StackedFolder 
          title="LLM" 
          zIndex={30} 
          isOpen={leftFolders.providers} 
          onToggle={() => toggleLeftFolder('providers')}
          stackOffset={1}
        >
          <div className="p-3 border-b border-white/10">
            <div className="text-[10px] font-mono text-white/80 tracking-wider">◆ LLM PROVIDERS</div>
          </div>
          <div className="flex-1 overflow-y-auto p-3 scrollbar-thin">
            <NestedSection title="OpenAI" icon="◆" color="text-green-400" defaultOpen>
              <div className="space-y-1 text-[9px] font-mono text-white/60">
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex justify-between">
                  <span>GPT-5.2</span><span className="text-green-400">●</span>
                </div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex justify-between">
                  <span>GPT-4o</span><span className="text-green-400">●</span>
                </div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex justify-between">
                  <span>GPT-4o-mini</span><span className="text-green-400">●</span>
                </div>
              </div>
            </NestedSection>
            <NestedSection title="xAI" icon="◆" color="text-purple-400" defaultOpen>
              <div className="space-y-1 text-[9px] font-mono text-white/60">
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex justify-between">
                  <span>Grok 4</span><span className="text-green-400">●</span>
                </div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex justify-between">
                  <span>Grok 3</span><span className="text-amber-400">●</span>
                </div>
              </div>
            </NestedSection>
            <NestedSection title="Anthropic" icon="◆" color="text-orange-400">
              <div className="space-y-1 text-[9px] font-mono text-white/60">
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex justify-between">
                  <span>Claude Sonnet 4</span><span className="text-green-400">●</span>
                </div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex justify-between">
                  <span>Claude Opus 4</span><span className="text-amber-400">●</span>
                </div>
              </div>
            </NestedSection>
            <NestedSection title="Google" icon="◆" color="text-blue-400">
              <div className="space-y-1 text-[9px] font-mono text-white/60">
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex justify-between">
                  <span>Gemini 3 Pro</span><span className="text-green-400">●</span>
                </div>
                <div className="py-1 px-2 hover:bg-white/5 rounded cursor-pointer flex justify-between">
                  <span>Gemini 3 Flash</span><span className="text-green-400">●</span>
                </div>
              </div>
            </NestedSection>
          </div>
        </StackedFolder>

        {/* FOLDER 1 (Front) - FRANKLIN ONBOARD CHAT - Full height scrolling chat */}
        <StackedFolder 
          title="FRANKLIN" 
          zIndex={40} 
          isOpen={leftFolders.franklin} 
          onToggle={() => toggleLeftFolder('franklin')}
          stackOffset={0}
        >
          <div className="p-3 border-b border-white/10 flex items-center justify-between">
            <div>
              <div className="text-[10px] font-mono text-emerald-400 tracking-wider">◈ FRANKLIN ONBOARD CHAT</div>
              <div className="text-[8px] font-mono text-white/40 mt-1">1M Context Window</div>
            </div>
            {/* Expand to full screen button */}
            <button
              onClick={() => {
                setDetailPanel({
                  type: 'franklin',
                  data: { name: 'FRANKLIN', primary_specialization: 'Sovereign AI Overseer' },
                  conversation: franklinChat.length > 0 ? franklinChat : [
                    { role: 'assistant', content: "Welcome to FRANKLIN OS. I'm here to help you navigate and build. What would you like to create today?" }
                  ]
                });
              }}
              className="px-2 py-1 text-[8px] font-mono text-emerald-400 hover:bg-emerald-400/10 border border-emerald-400/30 rounded transition-all"
              title="Open full screen chat"
            >
              ⛶ EXPAND
            </button>
          </div>
          
          {/* Scrolling chat area - takes all available space */}
          <div 
            ref={franklinRef} 
            className="flex-1 overflow-y-auto p-3 scrollbar-thin space-y-3"
            data-testid="franklin-chat-scroll"
          >
            {franklinChat.map((msg, idx) => (
              <div 
                key={idx} 
                className={`${msg.role === 'user' ? 'ml-4' : 'mr-4'}`}
              >
                <div className={`p-2 rounded-lg text-[10px] font-mono ${
                  msg.role === 'user' 
                    ? 'bg-cyan-500/20 border border-cyan-500/30 text-cyan-100' 
                    : 'bg-white/5 border border-white/10 text-white/80'
                }`}>
                  <div className="text-[8px] text-white/40 mb-1">
                    {msg.role === 'user' ? '◆ YOU' : '◈ FRANKLIN'}
                  </div>
                  <div className="leading-relaxed">{msg.content}</div>
                </div>
              </div>
            ))}
            {franklinLoading && (
              <div className="mr-4">
                <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                  <div className="flex items-center gap-2 text-purple-400 text-[10px]">
                    <div className="w-4 h-4">
                      <NeuralBrain themeColor="#a855f7" isThinking={true} size="sm" />
                    </div>
                    <span>Thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Input at bottom - fixed */}
          <div className="p-3 border-t border-white/10 bg-black/50">
            <div className="flex gap-2">
              <input
                type="text"
                value={franklinInput}
                onChange={(e) => setFranklinInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleFranklinSend()}
                placeholder="Ask Franklin anything..."
                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-[10px] font-mono text-white placeholder-white/30 focus:outline-none focus:border-emerald-500/50"
                disabled={franklinLoading}
                data-testid="franklin-input"
              />
              <button 
                onClick={handleFranklinSend} 
                disabled={franklinLoading} 
                className="px-3 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/30 rounded-lg text-[10px] text-emerald-400 transition-all"
                data-testid="franklin-send"
              >
                ▶
              </button>
            </div>
          </div>
        </StackedFolder>
      </div>

      {/* CENTER - Main Content Area */}
      <div className="absolute top-10 bottom-40 left-72 right-72 z-10">
        {/* Chat Messages Area */}
        <div 
          ref={outputRef}
          className="h-full overflow-y-auto px-8 py-6 scrollbar-thin"
          data-testid="chat-area"
        >
          {outputLog.length === 0 ? (
            <div className="h-full" /> 
          ) : (
            <div className="space-y-4 max-w-2xl mx-auto">
              {outputLog.map((entry, idx) => (
                <div 
                  key={idx} 
                  className={`flex ${entry.type === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
                >
                  <div className={`max-w-[75%] p-4 font-mono text-sm ${
                    entry.type === 'user' 
                      ? 'chat-bubble-user text-cyan-100' 
                      : entry.type === 'error'
                      ? 'bg-red-500/20 border border-red-500/30 text-red-200 rounded-xl'
                      : entry.type === 'success'
                      ? 'bg-green-500/20 border border-green-500/30 text-green-200 rounded-xl'
                      : 'chat-bubble-franklin text-white/90'
                  }`}>
                    <span className="text-white/30 text-[10px] block mb-1 font-semibold tracking-wider">{entry.phase}</span>
                    <span className="leading-relaxed">{entry.message}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
          {isLoading && (
            <div className="flex justify-start max-w-2xl mx-auto mt-4">
              <div className="chat-bubble-franklin p-4">
                <div className="flex items-center gap-3 text-white/70 text-sm font-mono">
                  <div className="w-10 h-10">
                    <NeuralBrain themeColor="#a855f7" isThinking={true} size="sm" />
                  </div>
                  <span>Franklin is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* RIGHT SIDE - Full Height Stacked Sliding Folders */}
      <div className="absolute top-10 bottom-40 right-0 w-72 z-40 overflow-visible" data-testid="right-folders">
        
        {/* FOLDER 3 (Back) - ACADEMY */}
        <StackedFolder 
          title="ACADEMY" 
          zIndex={10} 
          isOpen={rightFolders.academy} 
          onToggle={() => toggleRightFolder('academy')}
          side="right"
          stackOffset={2}
        >
          <div className="p-3 border-b border-white/10">
            <div className="text-[10px] font-mono text-purple-400 tracking-wider">◆ TRAINING PROGRAMS</div>
          </div>
          <div className="flex-1 overflow-y-auto p-3 scrollbar-thin space-y-2">
            {academyPrograms.slice(0, 8).map((program, idx) => (
              <div 
                key={idx} 
                onClick={() => handleProgramClick(program)}
                className={`p-2 rounded bg-white/5 border transition-all cursor-pointer ${
                  selectedProgram?.program_id === program.program_id 
                    ? 'border-purple-400/50 bg-purple-400/10' 
                    : 'border-white/10 hover:border-white/20'
                }`}
              >
                <div className="text-[10px] font-mono text-white/90 truncate">{program.name}</div>
                <div className="text-[8px] text-white/50 mt-1">{program.field} • {program.duration_weeks}w</div>
                <div className="flex justify-between mt-1 text-[8px]">
                  <span className="text-purple-400">{program.level}</span>
                  <span className="text-cyan-400">${program.cost?.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </StackedFolder>

        {/* FOLDER 2 - BOTS */}
        <StackedFolder 
          title="BOTS" 
          zIndex={20} 
          isOpen={rightFolders.bots} 
          onToggle={() => toggleRightFolder('bots')}
          side="right"
          stackOffset={1}
        >
          <div className="p-3 border-b border-white/10">
            <div className="text-[10px] font-mono text-amber-400 tracking-wider">◆ BOT TIERS</div>
          </div>
          <div className="flex-1 overflow-y-auto p-3 scrollbar-thin space-y-2">
            {botTiers.map((tier, idx) => (
              <div 
                key={idx} 
                onClick={() => handleBotClick(tier)}
                className={`p-2 rounded bg-white/5 border transition-all cursor-pointer ${
                  selectedBot?.name === tier.name 
                    ? 'border-amber-400/50 bg-amber-400/10' 
                    : 'border-white/10 hover:border-white/20'
                }`}
              >
                <div className="text-[10px] font-mono text-white/90">{tier.name}</div>
                <div className="text-[8px] text-white/50 mt-1 line-clamp-2">{tier.description?.slice(0, 60)}...</div>
                <div className="flex justify-between mt-1 text-[8px]">
                  <span className="text-amber-400">{tier.autonomy_level?.toUpperCase()}</span>
                  <span className="text-cyan-400">${tier.min_usd?.toLocaleString()}-${tier.max_usd?.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </StackedFolder>

        {/* FOLDER 1 (Front) - AGENTS */}
        <StackedFolder 
          title="AGENTS" 
          zIndex={30} 
          isOpen={rightFolders.agents} 
          onToggle={() => toggleRightFolder('agents')}
          side="right"
          stackOffset={0}
        >
          <div className="p-3 border-b border-white/10">
            <div className="text-[10px] font-mono text-green-400 tracking-wider">◆ ELITE AGENTS</div>
            <div className="text-[8px] font-mono text-white/40 mt-1">{marketplaceAgents.length} available</div>
          </div>
          <div className="flex-1 overflow-y-auto p-3 scrollbar-thin space-y-2">
            {marketplaceAgents.map((agent, idx) => (
              <div 
                key={idx} 
                onClick={() => handleAgentClick(agent)}
                className={`p-2 rounded bg-white/5 border transition-all cursor-pointer ${
                  selectedAgent?.agent_id === agent.agent_id 
                    ? 'border-green-400/50 bg-green-400/10' 
                    : 'border-white/10 hover:border-white/20'
                }`}
              >
                <div className="text-[10px] font-mono text-white/90">{agent.name}</div>
                <div className="text-[8px] text-white/50 mt-1 truncate">{agent.primary_specialization}</div>
                <div className="flex justify-between mt-1 text-[8px]">
                  <span className="text-green-400">★ {agent.client_satisfaction}</span>
                  <span className="text-cyan-400">${agent.starter_price}/mo</span>
                </div>
              </div>
            ))}
          </div>
        </StackedFolder>
      </div>

      {/* FULL-SCREEN CHAT MODAL - Agent/Bot/Academy/Franklin */}
      {detailPanel && (
        <div className="fixed inset-0 z-[100] bg-black flex flex-col">
          {/* Galactic Background */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute inset-0 bg-gradient-to-b from-black via-purple-950/20 to-black" />
            {[...Array(50)].map((_, i) => (
              <div
                key={i}
                className="absolute w-1 h-1 bg-white rounded-full animate-pulse"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  opacity: Math.random() * 0.5 + 0.2,
                  animationDelay: `${Math.random() * 3}s`
                }}
              />
            ))}
          </div>
          
          {/* Header */}
          <div className="relative z-10 px-8 py-6 border-b border-white/10 flex items-center justify-between bg-black/50 backdrop-blur-md">
            <div className="flex items-center gap-6">
              <div>
                <div className="text-sm font-mono text-white/40 uppercase tracking-widest mb-1">
                  {detailPanel.type === 'agent' ? '◆ AGENT CONVERSATION' : 
                   detailPanel.type === 'bot' ? '◆ BOT INTERFACE' : 
                   detailPanel.type === 'franklin' ? '◆ FRANKLIN AI' : '◆ ACADEMY PROGRAM'}
                </div>
                <div className="text-2xl font-bold text-white">{detailPanel.data.name}</div>
                {detailPanel.type === 'agent' && (
                  <div className="text-sm text-white/50 mt-1">{detailPanel.data.primary_specialization} • ★ {detailPanel.data.client_satisfaction}</div>
                )}
                {detailPanel.type === 'franklin' && (
                  <div className="text-sm text-emerald-400 mt-1">Sovereign AI Overseer • 1M Context Window</div>
                )}
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="flex items-center gap-3">
              {/* Read Aloud Button */}
              <button
                onClick={() => {
                  const text = detailPanel.conversation.map(m => `${m.role === 'user' ? 'You said' : detailPanel.data.name + ' said'}: ${m.content}`).join('. ');
                  const utterance = new SpeechSynthesisUtterance(text);
                  utterance.rate = 0.9;
                  utterance.pitch = 1;
                  speechSynthesis.cancel();
                  speechSynthesis.speak(utterance);
                }}
                className="px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 rounded-lg text-sm font-mono text-purple-400 transition-all flex items-center gap-2"
                title="Read conversation aloud"
              >
                🔊 READ ALOUD
              </button>
              
              {/* Stop Reading Button */}
              <button
                onClick={() => speechSynthesis.cancel()}
                className="px-4 py-2 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/30 rounded-lg text-sm font-mono text-amber-400 transition-all"
                title="Stop reading"
              >
                ⏹ STOP
              </button>
              
              {/* Print/PDF Button */}
              <button
                onClick={() => {
                  const printContent = `
                    <html>
                      <head>
                        <title>FRANKLIN OS - Conversation with ${detailPanel.data.name}</title>
                        <style>
                          body { font-family: monospace; padding: 40px; background: #000; color: #fff; }
                          h1 { color: #22c55e; border-bottom: 1px solid #333; padding-bottom: 20px; }
                          .message { margin: 20px 0; padding: 15px; border-radius: 8px; }
                          .user { background: rgba(6, 182, 212, 0.2); border-left: 4px solid #06b6d4; }
                          .assistant { background: rgba(255,255,255,0.05); border-left: 4px solid #666; }
                          .role { font-size: 12px; color: #888; margin-bottom: 8px; text-transform: uppercase; }
                          .content { line-height: 1.6; }
                          @media print { body { background: #fff; color: #000; } .user, .assistant { border: 1px solid #ccc; } }
                        </style>
                      </head>
                      <body>
                        <h1>◆ Conversation with ${detailPanel.data.name}</h1>
                        <p style="color:#888">${detailPanel.type === 'agent' ? detailPanel.data.primary_specialization : ''}</p>
                        ${detailPanel.conversation.map(m => `
                          <div class="message ${m.role === 'user' ? 'user' : 'assistant'}">
                            <div class="role">${m.role === 'user' ? '◆ YOU' : '◆ ' + detailPanel.data.name}</div>
                            <div class="content">${m.content}</div>
                          </div>
                        `).join('')}
                        <p style="margin-top:40px;color:#666;font-size:12px">Generated by FRANKLIN OS • ${new Date().toLocaleString()}</p>
                      </body>
                    </html>
                  `;
                  const printWindow = window.open('', '_blank');
                  printWindow.document.write(printContent);
                  printWindow.document.close();
                  printWindow.print();
                }}
                className="px-4 py-2 bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/30 rounded-lg text-sm font-mono text-cyan-400 transition-all flex items-center gap-2"
                title="Print or save as PDF"
              >
                🖨 PRINT / PDF
              </button>
              
              {/* Close Button */}
              <button 
                onClick={() => setDetailPanel(null)}
                className="ml-4 w-10 h-10 flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 rounded-lg transition-all text-xl"
              >
                ✕
              </button>
            </div>
          </div>
          
          {/* Chat Messages - Large and Readable */}
          <div ref={detailRef} className="relative z-10 flex-1 overflow-y-auto px-8 py-8 scrollbar-thin">
            <div className="max-w-4xl mx-auto space-y-6">
              {detailPanel.conversation.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] p-6 rounded-2xl ${
                    msg.role === 'user' 
                      ? 'bg-cyan-500/20 border border-cyan-500/30' 
                      : 'bg-white/5 border border-white/10'
                  }`}>
                    <div className="text-xs font-mono text-white/40 mb-3 uppercase tracking-wider">
                      {msg.role === 'user' ? '◆ YOU' : `◆ ${detailPanel.data.name}`}
                    </div>
                    <div className={`text-base leading-relaxed ${msg.role === 'user' ? 'text-cyan-100' : 'text-white/90'}`}>
                      {msg.content}
                    </div>
                    {/* Individual message read aloud */}
                    <button
                      onClick={() => {
                        const utterance = new SpeechSynthesisUtterance(msg.content);
                        utterance.rate = 0.9;
                        speechSynthesis.cancel();
                        speechSynthesis.speak(utterance);
                      }}
                      className="mt-3 text-xs text-white/30 hover:text-white/60 transition-all"
                    >
                      🔊 Read this message
                    </button>
                  </div>
                </div>
              ))}
              {detailLoading && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] p-6 rounded-2xl bg-white/5 border border-white/10">
                    <div className="flex items-center gap-3 text-purple-400">
                      <div className="w-3 h-3 bg-purple-400 rounded-full animate-ping"></div>
                      <span className="text-base">{detailPanel.data.name} is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Chat Input - Large */}
          <div className="relative z-10 px-8 py-6 border-t border-white/10 bg-black/50 backdrop-blur-md">
            <div className="max-w-4xl mx-auto flex gap-4">
              <input
                type="text"
                value={detailInput}
                onChange={(e) => setDetailInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleDetailSend()}
                placeholder={`Type your message to ${detailPanel.data.name}...`}
                className="flex-1 bg-white/5 border border-white/20 rounded-xl px-6 py-4 text-base font-mono text-white placeholder-white/30 focus:outline-none focus:border-cyan-500/50"
                disabled={detailLoading}
                data-testid="detail-chat-input"
                autoFocus
              />
              <button
                onClick={handleDetailSend}
                disabled={detailLoading || !detailInput.trim()}
                className="px-8 py-4 bg-gradient-to-r from-cyan-500/30 to-purple-500/30 hover:from-cyan-500/40 hover:to-purple-500/40 border border-cyan-500/30 rounded-xl text-base font-mono text-white disabled:opacity-30 transition-all"
                data-testid="detail-chat-send"
              >
                {detailLoading ? '◐ SENDING...' : '▶ SEND MESSAGE'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* BOTTOM PANEL - Terminal | Grok Response - Auto-snapped, clean layout */}
      <div className="absolute bottom-0 left-0 right-0 h-40 z-50 bg-black border-t border-white/10 flex">
        
        {/* Terminal - Left Half */}
        <div className="flex-1 flex flex-col border-r border-white/10">
          <div className="px-4 py-2 border-b border-white/5 flex items-center justify-between bg-black">
            <div className="text-[10px] font-mono text-cyan-400 tracking-wider flex items-center gap-2">
              <span className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></span>
              TERMINAL
            </div>
            <div className="text-[8px] font-mono text-white/30">SDK Cloud • Ubuntu/Linux • PowerShell</div>
          </div>
          <div className="flex-1 p-3 overflow-y-auto font-mono text-[10px] scrollbar-thin bg-black">
            {outputLog.slice(-12).map((entry, idx) => (
              <div key={idx} className={`mb-0.5 ${getOutputColor(entry.type)}`}>
                <span className="text-white/20">&gt;</span> <span className="text-white/40">[{entry.phase}]</span> {entry.message?.slice(0, 100)}
              </div>
            ))}
            {outputLog.length === 0 && (
              <div className="text-white/25 leading-relaxed">
                &gt; FRANKLIN OS Terminal v2.0<br/>
                &gt; Ready...<br/>
                &gt; Type /genesis &lt;mission&gt; to start
              </div>
            )}
          </div>
          <div className="p-2 border-t border-white/5 bg-black">
            <div className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
                placeholder="/genesis <mission>..."
                className="flex-1 bg-white/5 border border-white/10 px-3 py-1.5 text-[10px] font-mono text-white placeholder-white/20 focus:outline-none focus:border-cyan-500/30"
                data-testid="command-input"
                disabled={isLoading}
              />
              <button
                onClick={handleChatSend}
                disabled={isLoading || !chatInput.trim()}
                data-testid="send-btn"
                className="px-3 py-1.5 bg-cyan-500/10 border border-cyan-500/20 text-[10px] font-mono text-cyan-400 disabled:opacity-30 hover:bg-cyan-500/20 transition-all"
              >
                {isLoading ? '◐' : '▶'}
              </button>
            </div>
          </div>
        </div>

        {/* Grok Response - Right Half */}
        <div className="flex-1 flex flex-col">
          <div className="px-4 py-2 border-b border-white/5 flex items-center justify-between bg-black">
            <div className="text-[10px] font-mono text-purple-400 tracking-wider flex items-center gap-2">
              <span className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></span>
              GROK RESPONSE
            </div>
            <div className="text-[8px] font-mono text-white/30">1M Context Window</div>
          </div>
          <div className="flex-1 p-3 overflow-y-auto scrollbar-thin bg-black">
            {grokResponses.length > 0 ? (
              grokResponses.slice(-8).map((resp, idx) => (
                <div key={idx} className={`mb-1 text-[10px] font-mono ${
                  resp.type === 'success' ? 'text-green-400' :
                  resp.type === 'error' ? 'text-red-400' :
                  'text-white/60'
                }`}>
                  <span className="text-white/20">[{resp.phase}]</span> {resp.message?.slice(0, 120)}
                </div>
              ))
            ) : (
              <div className="text-white/25 text-[10px] font-mono leading-relaxed">
                Grok responses appear here...<br/>
                Use the input below to ask Grok
              </div>
            )}
            {isLoading && (
              <div className="flex items-center gap-2 text-purple-400 text-[10px] font-mono mt-1">
                <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-ping"></span>
                Processing...
              </div>
            )}
          </div>
          <div className="p-2 pr-24 border-t border-white/5 bg-black">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Ask Grok anything..."
                className="flex-1 bg-white/5 border border-white/10 px-3 py-1.5 text-[10px] font-mono text-white placeholder-white/20 focus:outline-none focus:border-purple-500/30"
                data-testid="grok-input"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.target.value.trim()) {
                    const query = e.target.value.trim();
                    e.target.value = '';
                    setChatInput(query);
                    setTimeout(() => handleChatSend(), 100);
                  }
                }}
              />
              <button className="px-3 py-1.5 bg-purple-500/10 border border-purple-500/20 text-[10px] font-mono text-purple-400 hover:bg-purple-500/20 transition-all">▶</button>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .franklin-chrome-dim {
          background: linear-gradient(135deg, rgba(60,60,60,1) 0%, rgba(100,100,100,1) 15%, rgba(160,160,160,1) 30%, rgba(200,200,200,1) 45%, rgba(160,160,160,1) 55%, rgba(100,100,100,1) 70%, rgba(60,60,60,1) 85%, rgba(120,120,120,1) 100%);
          background-size: 200% 200%;
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: chromeShimmer 25s ease-in-out infinite;
          opacity: 0.35;
        }
        @keyframes chromeShimmer { 0% { background-position: 200% 200%; } 50% { background-position: 0% 0%; } 100% { background-position: 200% 200%; } }
        .scrollbar-thin::-webkit-scrollbar { width: 4px; }
        .scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
        .scrollbar-thin::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
        @keyframes fade-in { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
        .animate-fade-in { animation: fade-in 0.3s ease-out; }
      `}</style>
    </div>
  );
}

// ============================================================================
// MAIN APP - Page Router
// ============================================================================
function App() {
  const [currentPage, setCurrentPage] = useState(PAGES.LANDING);
  
  // Shared workflow state (so it persists between IDE and Workflow pages)
  const [workflowNodes, setWorkflowNodes, onNodesChange] = useNodesState([
    { id: 'start', type: 'stage', position: { x: 100, y: 100 }, data: { label: 'Start', status: 'completed', type: 'start' } },
    { id: 'spec', type: 'stage', position: { x: 300, y: 100 }, data: { label: 'Specification', status: 'pending', type: 'stage' } },
    { id: 'arch', type: 'stage', position: { x: 500, y: 100 }, data: { label: 'Architecture', status: 'pending', type: 'stage' } },
    { id: 'impl', type: 'stage', position: { x: 700, y: 100 }, data: { label: 'Implementation', status: 'pending', type: 'stage' } },
    { id: 'cert', type: 'stage', position: { x: 900, y: 100 }, data: { label: 'Certification', status: 'pending', type: 'stage' } },
  ]);
  
  const [workflowEdges, setWorkflowEdges, onEdgesChange] = useEdgesState([
    { id: 'e-start-spec', source: 'start', target: 'spec', animated: true, style: { stroke: '#00ff88' } },
    { id: 'e-spec-arch', source: 'spec', target: 'arch', animated: false, style: { stroke: '#444' } },
    { id: 'e-arch-impl', source: 'arch', target: 'impl', animated: false, style: { stroke: '#444' } },
    { id: 'e-impl-cert', source: 'impl', target: 'cert', animated: false, style: { stroke: '#444' } },
  ]);

  const handleNavigate = (page) => {
    setCurrentPage(page);
  };

  // Render current page
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

  // Default: IDE Page
  return (
    <IDEPage 
      onNavigate={handleNavigate}
      workflowNodes={workflowNodes}
      setWorkflowNodes={setWorkflowNodes}
      workflowEdges={workflowEdges}
      setWorkflowEdges={setWorkflowEdges}
    />
  );
}

export default App;
