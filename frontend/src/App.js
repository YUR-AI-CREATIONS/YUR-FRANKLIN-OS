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

// Page Navigation
const PAGES = {
  LANDING: 'landing',
  IDE: 'ide',
  WORKFLOW: 'workflow'
};

// Stars & Galactic Background Component
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
      
      if (starsRef.current) {
        starsRef.current.forEach(star => {
          const twinkle = Math.sin(time * star.speed * 0.05 + star.phase) * 0.5 + 0.5;
          
          if (star.type === 'bright') {
            ctx.shadowBlur = 12;
            ctx.shadowColor = `rgba(255, 255, 255, ${twinkle * 0.6 * opacity})`;
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.size * twinkle + 0.5, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${(twinkle * 0.9 + 0.1) * opacity})`;
            ctx.fill();
            ctx.shadowBlur = 0;
          } else {
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.size * (twinkle * 0.3 + 0.7), 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${(twinkle * 0.6 + 0.2) * opacity})`;
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
    const interval = setInterval(loadStatus, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

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

  return (
    <div className="h-screen w-screen overflow-hidden bg-black text-white relative" data-testid="workflow-page">
      <GalacticBackground opacity={0.5} />
      
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 h-14 z-50 bg-black/80 backdrop-blur-md border-b border-white/10 flex items-center px-6">
        <button
          onClick={onBack}
          className="px-4 py-2 text-xs font-mono text-white/70 hover:text-white hover:bg-white/10 rounded transition-all flex items-center gap-2"
          data-testid="back-to-ide"
        >
          ◀ BACK TO IDE
        </button>
        
        <div className="flex-1 text-center">
          <h1 className="text-lg font-mono tracking-widest text-white/90">
            ◈ ELECTRIC WORKFLOW
          </h1>
          <p className="text-[10px] text-white/40 tracking-wider">VISUAL BUILD PIPELINE</p>
        </div>
        
        <div className="flex items-center gap-4">
          {buildStatus && (
            <div className="text-[10px] font-mono text-white/50">
              BUILD: <span className="text-cyan-400">{buildStatus.build_id}</span>
              <span className="ml-2 text-white/30">|</span>
              <span className={`ml-2 ${buildStatus.status === 'certified' ? 'text-green-400' : 'text-amber-400'}`}>
                {buildStatus.status?.toUpperCase()}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Main Workflow Canvas */}
      <div className="absolute top-14 left-0 right-72 bottom-0 z-10">
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
          className="bg-transparent"
          defaultEdgeOptions={{
            style: { stroke: '#00ff88', strokeWidth: 2 },
            animated: true
          }}
        >
          <Background color="rgba(255,255,255,0.03)" gap={30} />
          <Controls className="!bg-black/70 !border-white/20 !rounded-lg" />
          <MiniMap 
            className="!bg-black/70 !border-white/20 !rounded-lg"
            nodeColor={(node) => {
              if (node.data?.status === 'completed') return '#00ff88';
              if (node.data?.status === 'active') return '#00aaff';
              if (node.data?.status === 'failed') return '#ff4444';
              return '#666666';
            }}
            maskColor="rgba(0, 0, 0, 0.8)"
          />
        </ReactFlow>
      </div>

      {/* Right Panel - Node Details & Controls */}
      <div className="absolute top-14 right-0 bottom-0 w-72 z-40 bg-black/90 border-l border-white/10 backdrop-blur-md overflow-y-auto">
        <div className="p-4">
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

          {/* Selected Node Details */}
          {selectedNode && (
            <div className="mb-6 p-3 bg-white/5 rounded-lg border border-white/10">
              <div className="text-xs font-mono text-white/60 mb-2">SELECTED NODE</div>
              <div className="text-sm font-mono text-white/90">{selectedNode.data?.label || selectedNode.id}</div>
              <div className="text-[10px] text-white/50 mt-1">{selectedNode.data?.type || 'stage'}</div>
              {selectedNode.data?.status && (
                <div className={`text-[10px] mt-2 ${
                  selectedNode.data.status === 'completed' ? 'text-green-400' :
                  selectedNode.data.status === 'active' ? 'text-cyan-400' :
                  'text-white/40'
                }`}>
                  Status: {selectedNode.data.status.toUpperCase()}
                </div>
              )}
            </div>
          )}

          {/* Add Node Controls */}
          <div className="mb-6">
            <div className="text-xs font-mono text-white/60 mb-2">ADD NODE</div>
            <div className="grid grid-cols-2 gap-2">
              {['Stage', 'Decision', 'Action', 'Check'].map(type => (
                <button
                  key={type}
                  className="px-3 py-2 text-[10px] font-mono bg-white/5 border border-white/10 rounded hover:bg-white/10 hover:border-white/20 transition-all"
                >
                  + {type}
                </button>
              ))}
            </div>
          </div>

          {/* Workflow Actions */}
          <div className="space-y-2">
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
  // Panel collapse states
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  
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
  const [detailPanel, setDetailPanel] = useState(null); // { type: 'agent'|'bot'|'program', data: {...}, conversation: [] }
  const [detailInput, setDetailInput] = useState('');
  const [detailLoading, setDetailLoading] = useState(false);
  
  // Data states
  const [dashboard, setDashboard] = useState(null);
  const [marketplaceAgents, setMarketplaceAgents] = useState([]);
  const [botTiers, setBotTiers] = useState([]);
  const [academyPrograms, setAcademyPrograms] = useState([]);
  
  // Chat/Output states
  const [chatInput, setChatInput] = useState('');
  const [outputLog, setOutputLog] = useState([]);
  const [conversationHistory, setConversationHistory] = useState([]);
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
  }, []);

  // Auto-scroll output
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [outputLog]);

  // Add output message
  const addOutput = (phase, message, type = 'info') => {
    setOutputLog(prev => [...prev, {
      phase,
      message,
      type,
      timestamp: new Date().toISOString()
    }]);
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

  // Handle Genesis command
  const handleGenesis = async (mission) => {
    setIsLoading(true);
    addOutput('GENESIS', `Starting mission: ${mission}`, 'system');
    addWorkflowNode(`Genesis: ${mission.slice(0, 30)}...`, 'active');
    
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
        addWorkflowNode('Build Complete', 'completed');
        setFileTreeGlow(true);
        setTimeout(() => setFileTreeGlow(false), 2000);
      } else {
        addOutput('FAILED', `Task failed after ${response.data.task?.attempts || 0} attempts`, 'error');
        addWorkflowNode('Build Failed', 'failed');
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
      addOutput('SYSTEM', 'Conversation cleared.', 'system');
      return;
    }
    
    if (input.toLowerCase() === '/help') {
      addOutput('HELP', 'Available commands:', 'system');
      addOutput('HELP', '/genesis <mission> - Start a build mission', 'info');
      addOutput('HELP', '/build <mission> - Same as /genesis', 'info');
      addOutput('HELP', '/workflow - Open workflow view', 'info');
      addOutput('HELP', '/clear - Clear conversation', 'info');
      addOutput('HELP', '/help - Show this help', 'info');
      addOutput('HELP', 'Or just type naturally to chat with Franklin!', 'success');
      return;
    }
    
    addOutput('USER', input, 'user');
    setIsLoading(true);
    
    // Add to conversation history
    const newHistory = [...conversationHistory, { role: 'user', content: input }];
    setConversationHistory(newHistory);
    
    try {
      // Try to have a real conversation via Grok
      const response = await axios.post(`${API}/api/grok/chat`, { 
        message: input,
        history: newHistory.slice(-10) // Last 10 messages for context
      });
      
      if (response.data.response) {
        addOutput('FRANKLIN', response.data.response, 'system');
        setConversationHistory([...newHistory, { role: 'assistant', content: response.data.response }]);
      }
    } catch (err) {
      // Fallback to analyze endpoint
      try {
        const response = await axios.post(`${API}/api/analyze`, { prompt: input });
        
        if (response.data.analysis?.summary) {
          addOutput('FRANKLIN', response.data.analysis.summary, 'system');
        } else {
          addOutput('FRANKLIN', `I understood your request. Confidence: ${response.data.confidence_score}%`, 'system');
        }
        
        if (response.data.analysis?.ambiguities?.length > 0) {
          response.data.analysis.ambiguities.forEach(amb => {
            addOutput('QUESTION', `${amb.question}`, 'warning');
          });
        }
        
        if (response.data.can_proceed) {
          addOutput('READY', 'Ready to build. Use /genesis <description> to start.', 'success');
        }
      } catch (analyzeErr) {
        addOutput('FRANKLIN', `I'm here to help you build software. Try commands like "/genesis create a todo app" or just describe what you want to create.`, 'system');
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

  // Handle agent click - open detail panel
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
  };

  // Close detail panel
  const closeDetailPanel = () => {
    setDetailPanel(null);
    setSelectedAgent(null);
    setSelectedBot(null);
    setSelectedProgram(null);
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
        program: `Excellent question! This topic is covered in week 3 of the curriculum. Would you like more details about the program structure?`
      };
      setDetailPanel(prev => ({
        ...prev,
        conversation: [...prev.conversation, { role: detailPanel.type, content: fallbackReplies[detailPanel.type] }]
      }));
    } finally {
      setDetailLoading(false);
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

      {/* LEFT PANEL */}
      <div className={`absolute left-0 top-0 bottom-0 z-40 silver-glass silver-outline overflow-hidden transition-all duration-300 ${leftCollapsed ? 'w-12' : 'w-56'}`}>
        {/* Collapse Toggle */}
        <button
          onClick={() => setLeftCollapsed(!leftCollapsed)}
          className="absolute top-3 right-3 z-50 w-6 h-6 flex items-center justify-center text-white/40 hover:text-white silver-btn rounded transition-all"
          data-testid="collapse-left"
        >
          {leftCollapsed ? '▶' : '◀'}
        </button>
        
        {!leftCollapsed && (
          <>
        <div className={`absolute inset-0 transition-transform duration-300 ${leftPanelView === 'interface' ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="p-4 h-full flex flex-col">
            <div className="text-[10px] font-mono text-white/40 mb-4 tracking-wider">◆ INTERFACE_MODE</div>
            
            <div className="space-y-1">
              {INTERFACE_MODES.map(mode => (
                <button
                  key={mode.id}
                  onClick={() => {
                    setSelectedMode(mode.id);
                    if (mode.id === 'workflow') {
                      onNavigate(PAGES.WORKFLOW);
                    }
                  }}
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

        <div className={`absolute inset-0 transition-transform duration-300 ${leftPanelView === 'project' ? 'translate-x-0' : 'translate-x-full'}`}>
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
          </>
        )}
      </div>

      {/* CENTER CHAT AREA - Main conversation with Franklin */}
      <div className={`absolute top-0 bottom-64 z-30 flex flex-col transition-all duration-300 ${leftCollapsed ? 'left-14' : 'left-60'} ${rightCollapsed ? 'right-14' : 'right-68'}`}>
        
        {/* FRANKLIN Chrome Branding - CENTER STAGE, Properly Sized */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-[1] overflow-hidden">
          <h1 
            className="franklin-chrome select-none whitespace-nowrap"
            style={{ 
              fontFamily: "'Orbitron', sans-serif",
              fontSize: 'clamp(3rem, 10vw, 8rem)',
              letterSpacing: '0.4em'
            }}
          >
            FRANKLIN
          </h1>
        </div>

        {/* Chat Messages Area - Overlays on FRANKLIN */}
        <div 
          ref={outputRef}
          className="flex-1 overflow-y-auto px-8 py-6 z-10 scrollbar-silver"
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
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{animationDelay: '0ms'}} />
                    <span className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{animationDelay: '150ms'}} />
                    <span className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{animationDelay: '300ms'}} />
                  </div>
                  <span>Franklin is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Detail Panel - Shows when agent/bot/program selected */}
        {detailPanel && (
          <div className="absolute left-0 top-0 bottom-0 w-80 silver-glass flex flex-col z-20" data-testid="detail-panel">
            {/* Header */}
            <div className="p-4 border-b border-white/10 flex items-start justify-between">
              <div>
                <div className="text-[10px] font-mono text-white/40 tracking-wider mb-1">
                  {detailPanel.type === 'agent' ? '◆ AGENT' : detailPanel.type === 'bot' ? '◆ BOT' : '◆ PROGRAM'}
                </div>
                <div className="text-sm font-mono text-white">{detailPanel.data.name}</div>
                <div className="text-[10px] text-white/50 mt-1">
                  {detailPanel.type === 'agent' && detailPanel.data.primary_specialization}
                  {detailPanel.type === 'bot' && `${detailPanel.data.autonomy_level?.toUpperCase()} AUTONOMY`}
                  {detailPanel.type === 'program' && `${detailPanel.data.field} • ${detailPanel.data.level}`}
                </div>
              </div>
              <button 
                onClick={closeDetailPanel}
                className="w-8 h-8 flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 rounded-lg transition-all"
              >
                ✕
              </button>
            </div>
            
            {/* Stats */}
            <div className="px-4 py-3 border-b border-white/10 bg-white/5">
              {detailPanel.type === 'agent' && (
                <div className="flex justify-between text-[10px] font-mono">
                  <span className="text-green-400">★ {detailPanel.data.client_satisfaction}</span>
                  <span className="text-cyan-400">${detailPanel.data.starter_price}/mo</span>
                </div>
              )}
              {detailPanel.type === 'bot' && (
                <div className="flex justify-between text-[10px] font-mono">
                  <span className="text-amber-400">TIER {detailPanel.data.tier_level || '?'}</span>
                  <span className="text-cyan-400">${detailPanel.data.min_usd?.toLocaleString()} - ${detailPanel.data.max_usd?.toLocaleString()}</span>
                </div>
              )}
              {detailPanel.type === 'program' && (
                <div className="flex justify-between text-[10px] font-mono">
                  <span className="text-purple-400">{detailPanel.data.duration_weeks} WEEKS</span>
                  <span className="text-cyan-400">${detailPanel.data.cost?.toLocaleString()}</span>
                </div>
              )}
            </div>
            
            {/* Conversation */}
            <div ref={detailRef} className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-silver">
              {detailPanel.conversation.map((msg, idx) => (
                <div key={idx} className={`text-sm font-mono ${msg.role === 'user' ? 'text-cyan-400' : 'text-white/80'}`}>
                  {msg.role === 'user' && <span className="text-white/40 text-[10px]">[YOU] </span>}
                  {msg.role !== 'user' && <span className="text-white/40 text-[10px]">[{detailPanel.data.name?.split(' ')[0]?.toUpperCase()}] </span>}
                  <span className="leading-relaxed">{msg.content}</span>
                </div>
              ))}
              {detailLoading && (
                <div className="text-sm text-purple-400 animate-pulse flex items-center gap-2">
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-ping" />
                  Thinking...
                </div>
              )}
            </div>
            
            {/* Input */}
            <div className="p-3 border-t border-white/10">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={detailInput}
                  onChange={(e) => setDetailInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleDetailSend()}
                  placeholder={`Ask ${detailPanel.data.name?.split(' ')[0]}...`}
                  className="flex-1 silver-input rounded-lg px-3 py-2 text-xs font-mono text-white placeholder-white/30"
                  disabled={detailLoading}
                />
                <button
                  onClick={handleDetailSend}
                  disabled={detailLoading || !detailInput.trim()}
                  className="silver-btn px-4 py-2 rounded-lg text-xs font-mono text-white disabled:opacity-30"
                >
                  ▶
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* RIGHT PANEL */}
      <div className={`absolute right-0 top-0 bottom-64 z-40 silver-glass silver-outline transition-all duration-300 ${rightCollapsed ? 'w-12' : 'w-64'}`}>
        {/* Collapse Toggle */}
        <button
          onClick={() => setRightCollapsed(!rightCollapsed)}
          className="absolute top-3 left-3 z-50 w-6 h-6 flex items-center justify-center text-white/40 hover:text-white silver-btn rounded transition-all"
          data-testid="collapse-right"
        >
          {rightCollapsed ? '◀' : '▶'}
        </button>
        
        {!rightCollapsed && (
          <>
        <div className="flex border-b border-white/10 mt-8">
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
          {rightTab === 'agents' && (
            <div className="space-y-3">
              <div className="text-[10px] font-mono text-white/40 tracking-wider mb-2">◆ ELITE_AGENTS</div>
              {marketplaceAgents.map((agent, idx) => (
                <div 
                  key={idx} 
                  onClick={() => handleAgentClick(agent)}
                  className={`p-3 rounded bg-white/5 border transition-all cursor-pointer ${
                    selectedAgent?.agent_id === agent.agent_id 
                      ? 'border-green-400/50 bg-green-400/10' 
                      : 'border-white/10 hover:border-white/20'
                  }`}
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

          {rightTab === 'bots' && (
            <div className="space-y-3">
              <div className="text-[10px] font-mono text-white/40 tracking-wider mb-2">◆ BOT_TIERS</div>
              {botTiers.map((tier, idx) => (
                <div 
                  key={idx} 
                  onClick={() => handleBotClick(tier)}
                  className={`p-3 rounded bg-white/5 border transition-all cursor-pointer ${
                    selectedBot?.name === tier.name 
                      ? 'border-amber-400/50 bg-amber-400/10' 
                      : 'border-white/10 hover:border-white/20'
                  }`}
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

          {rightTab === 'academy' && (
            <div className="space-y-3">
              <div className="text-[10px] font-mono text-white/40 tracking-wider mb-2">◆ TRAINING_PROGRAMS</div>
              {academyPrograms.slice(0, 5).map((program, idx) => (
                <div 
                  key={idx} 
                  onClick={() => handleProgramClick(program)}
                  className={`p-3 rounded bg-white/5 border transition-all cursor-pointer ${
                    selectedProgram?.program_id === program.program_id 
                      ? 'border-purple-400/50 bg-purple-400/10' 
                      : 'border-white/10 hover:border-white/20'
                  }`}
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
          </>
        )}
      </div>

      {/* BOTTOM PANEL */}
      <div className={`absolute bottom-0 h-64 z-40 silver-glass silver-outline flex flex-col transition-all duration-300 ${leftCollapsed ? 'left-12' : 'left-56'} ${rightCollapsed ? 'right-12' : 'right-64'}`}>
        {/* BRANDING BAR - Category Buttons */}
        <div className="flex border-b border-white/10 shrink-0">
          {BUILD_CATEGORIES.map(cat => (
            <button
              key={cat.id}
              onClick={() => toggleCategory(cat.id)}
              className={`flex-1 py-3 text-[10px] font-mono uppercase tracking-wider transition-all border-r border-white/5 last:border-r-0 ${
                expandedCategory === cat.id 
                  ? 'text-white bg-white/10 franklin-chrome-dim' 
                  : 'text-white/50 hover:text-white/80 hover:bg-white/5'
              }`}
            >
              {cat.label}
              <span className="ml-1 opacity-50">{expandedCategory === cat.id ? '▼' : '▶'}</span>
            </button>
          ))}
          
          {/* Workflow Button */}
          <button
            onClick={() => onNavigate(PAGES.WORKFLOW)}
            className="px-4 py-2 text-[10px] font-mono uppercase tracking-wider text-cyan-400 hover:bg-cyan-400/10 transition-all border-l border-white/10"
            data-testid="open-workflow"
          >
            ◈ WORKFLOW
          </button>
        </div>

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

        {dashboard && (
          <div className="flex items-center gap-4 px-4 py-2 border-b border-white/10 bg-white/5 text-[9px] font-mono shrink-0">
            <span className="text-green-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
              SENTINEL: {dashboard.runtime?.sentinel?.status || 'ACTIVE'}
            </span>
            <span className="text-cyan-400">PQC: ONLINE</span>
            <span className="text-purple-400">AUDIT: {dashboard.runtime?.audit?.total_entries || 0} entries</span>
            <span className="text-amber-400">AGENTS: {marketplaceAgents.length}</span>
            <span className="text-white/40">GROK: ONLINE</span>
          </div>
        )}

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
                className="flex-1 silver-input rounded-lg px-4 py-3 text-sm font-mono text-white placeholder-white/30"
                data-testid="command-input"
                disabled={isLoading}
              />
              <button
                onClick={handleChatSend}
                disabled={isLoading || !chatInput.trim()}
                data-testid="send-btn"
                className="silver-btn px-6 py-3 rounded-lg text-sm font-mono text-white transition-all disabled:opacity-30"
              >
                {isLoading ? '◐' : 'SEND ▶'}
              </button>
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
        .file-tree-glow { animation: glowPulse 2s ease-out; }
        @keyframes glowPulse { 0% { box-shadow: inset 0 0 0 rgba(100,200,255,0); } 50% { box-shadow: inset 0 0 30px rgba(100,200,255,0.3); } 100% { box-shadow: inset 0 0 0 rgba(100,200,255,0); } }
        @keyframes fade-in { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
        .animate-fade-in { animation: fade-in 0.3s ease-out; }
        .scrollbar-thin::-webkit-scrollbar { width: 4px; }
        .scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
        .scrollbar-thin::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
      `}</style>
    </div>
  );
};

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
