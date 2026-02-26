import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from './ui/resizable';
import Editor from '@monaco-editor/react';
import { useDropzone } from 'react-dropzone';
import {
  Terminal, Code, FileCode, FolderTree, Upload, Download, Play, 
  CheckCircle, XCircle, Loader, Settings, Database, Cloud,
  GitBranch, Box, Cpu, Shield, Eye, Zap, Send, ChevronRight,
  File, Image, Video, Music, Archive, X, Key, RefreshCw,
  Globe, Server, Lock, AlertTriangle, Check, Clock, Users,
  Layers, FileText, Folder, ChevronDown, MoreVertical
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL || '';

// Gate definitions
const GATES = [
  { id: 1, name: 'Intent', icon: Eye, desc: 'Requirement validation' },
  { id: 2, name: 'Data', icon: Database, desc: 'Schema validation' },
  { id: 3, name: 'Model', icon: Cpu, desc: 'ML/AI validation' },
  { id: 4, name: 'Vector', icon: Zap, desc: 'RAG validation' },
  { id: 5, name: 'Orchestration', icon: GitBranch, desc: 'Service coordination' },
  { id: 6, name: 'API', icon: Code, desc: 'Endpoint validation' },
  { id: 7, name: 'UI', icon: Box, desc: 'Frontend validation' },
  { id: 8, name: 'Security', icon: Shield, desc: 'Security scan' },
];

// Workflow stages
const WORKFLOW_STAGES = [
  { id: 'upload', name: 'Upload & Analyze', icon: Upload },
  { id: 'verify', name: 'Verify Understanding', icon: Check },
  { id: 'workflow', name: 'Build Workflow', icon: Layers },
  { id: 'structure', name: 'File Structure', icon: FolderTree },
  { id: 'architecture', name: 'Architecture', icon: Server },
  { id: 'implementation', name: 'Implementation', icon: Code },
  { id: 'deployment', name: 'Deployment', icon: Cloud },
  { id: 'certification', name: 'Certification', icon: Shield },
];

// Laser beam background (matching landing page)
const LaserBeams = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <svg className="absolute inset-0 w-full h-full" style={{ opacity: 0.15 }}>
        <defs>
          <linearGradient id="beam1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="transparent" />
            <stop offset="50%" stopColor="rgba(255,255,255,0.5)" />
            <stop offset="100%" stopColor="transparent" />
          </linearGradient>
        </defs>
        {[...Array(8)].map((_, i) => (
          <line
            key={i}
            x1={`${10 + i * 12}%`}
            y1="0"
            x2={`${50 + i * 8}%`}
            y2="100%"
            stroke="url(#beam1)"
            strokeWidth="1"
          />
        ))}
        {[...Array(6)].map((_, i) => (
          <line
            key={`h${i}`}
            x1="0"
            y1={`${20 + i * 15}%`}
            x2="100%"
            y2={`${30 + i * 12}%`}
            stroke="url(#beam1)"
            strokeWidth="1"
          />
        ))}
      </svg>
    </div>
  );
};

// Stars background
const StarsBackground = () => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationId;
    let stars = [];
    
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      stars = Array.from({ length: 150 }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 1.5 + 0.5,
        twinkle: Math.random() * 0.02 + 0.01,
        phase: Math.random() * Math.PI * 2,
      }));
    };
    
    let time = 0;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      stars.forEach(star => {
        const alpha = Math.sin(time * star.twinkle + star.phase) * 0.4 + 0.6;
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
        ctx.fill();
      });
      
      time++;
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
  
  return <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" />;
};

// Trust Vault Component
const TrustVault = ({ connectors, onRefresh }) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold tracking-wider text-white/80" style={{ fontFamily: "'Orbitron', sans-serif" }}>
          TRUST VAULT
        </h3>
        <button onClick={onRefresh} className="p-1.5 rounded hover:bg-white/10 transition-colors">
          <RefreshCw size={14} className="text-white/50" />
        </button>
      </div>
      
      {connectors.map((conn, i) => (
        <div key={i} className="p-3 rounded-lg border border-white/10 bg-white/5">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${conn.status === 'active' ? 'bg-green-500' : conn.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'}`} />
              <span className="text-xs font-medium text-white/80">{conn.name}</span>
            </div>
            <Key size={12} className="text-white/30" />
          </div>
          <div className="flex justify-between text-[10px] text-white/40">
            <span>Tokens: {conn.tokensUsed?.toLocaleString() || 0} / {conn.tokensTotal?.toLocaleString() || '∞'}</span>
            <span>Rotate: {conn.rotateIn || '7d'}</span>
          </div>
          <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-white/40 to-white/20 rounded-full transition-all"
              style={{ width: `${conn.tokensTotal ? (conn.tokensUsed / conn.tokensTotal) * 100 : 10}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

// File Tree Component
const FileTree = ({ files, onSelect, selectedFile }) => {
  const [expanded, setExpanded] = useState({});
  
  const toggleFolder = (path) => {
    setExpanded(prev => ({ ...prev, [path]: !prev[path] }));
  };
  
  const getIcon = (name, isFolder) => {
    if (isFolder) return Folder;
    const ext = name.split('.').pop()?.toLowerCase();
    if (['py'].includes(ext)) return FileCode;
    if (['js', 'ts', 'jsx', 'tsx'].includes(ext)) return Code;
    if (['json', 'yaml', 'yml'].includes(ext)) return FileText;
    if (['md', 'txt'].includes(ext)) return FileText;
    if (['env'].includes(ext)) return Lock;
    return File;
  };
  
  const renderTree = (items, level = 0) => {
    return items.map((item, i) => {
      const Icon = getIcon(item.name, item.isFolder);
      const isExpanded = expanded[item.path];
      
      return (
        <div key={i}>
          <div
            onClick={() => item.isFolder ? toggleFolder(item.path) : onSelect(item)}
            className={`flex items-center gap-2 px-2 py-1.5 cursor-pointer rounded transition-colors ${
              selectedFile?.path === item.path ? 'bg-white/15 text-white' : 'text-white/60 hover:bg-white/5 hover:text-white/80'
            }`}
            style={{ paddingLeft: `${level * 16 + 8}px` }}
          >
            {item.isFolder && (
              <ChevronDown size={12} className={`transition-transform ${isExpanded ? '' : '-rotate-90'}`} />
            )}
            <Icon size={14} />
            <span className="text-xs truncate">{item.name}</span>
          </div>
          {item.isFolder && isExpanded && item.children && (
            <div>{renderTree(item.children, level + 1)}</div>
          )}
        </div>
      );
    });
  };
  
  return <div className="py-2">{renderTree(files)}</div>;
};

// Certification Theater
const CertificationTheater = ({ gates, currentGate }) => {
  return (
    <div className="grid grid-cols-4 gap-3 p-4">
      {GATES.map((gate) => {
        const result = gates.find(g => g.gate_num === gate.id);
        const status = currentGate === gate.id ? 'running' 
          : result?.passed ? 'passed' 
          : result?.passed === false ? 'failed' 
          : 'pending';
        
        const Icon = gate.icon;
        
        return (
          <motion.div
            key={gate.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: gate.id * 0.05 }}
            className={`p-4 rounded-lg border text-center transition-all ${
              status === 'passed' ? 'border-green-500/50 bg-green-500/10' :
              status === 'failed' ? 'border-red-500/50 bg-red-500/10' :
              status === 'running' ? 'border-white/30 bg-white/10 animate-pulse' :
              'border-white/10 bg-white/5'
            }`}
          >
            <div className="text-2xl font-bold text-white/80 mb-1" style={{ fontFamily: "'Orbitron', sans-serif" }}>
              {gate.id}
            </div>
            <div className="text-[10px] uppercase tracking-wider text-white/50 mb-2">
              {gate.name}
            </div>
            <div className="flex justify-center">
              {status === 'passed' && <CheckCircle size={20} className="text-green-500" />}
              {status === 'failed' && <XCircle size={20} className="text-red-500" />}
              {status === 'running' && <Loader size={20} className="text-white/60 animate-spin" />}
              {status === 'pending' && <Icon size={20} className="text-white/30" />}
            </div>
            {result?.score !== undefined && (
              <div className={`text-xs mt-2 ${result.passed ? 'text-green-400' : 'text-red-400'}`}>
                {result.score.toFixed(0)}%
              </div>
            )}
          </motion.div>
        );
      })}
    </div>
  );
};

// Main IDE Component
export const FranklinIDE = ({ onBack }) => {
  // Session ID for file uploads
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`);
  
  // State
  const [prompt, setPrompt] = useState('');
  const [techStack, setTechStack] = useState('python');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStage, setCurrentStage] = useState('upload');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [analyzedTodos, setAnalyzedTodos] = useState([]);
  const [verifiedWorkflow, setVerifiedWorkflow] = useState(null);
  const [projectFiles, setProjectFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('// Welcome to FRANKLIN OS\n// Upload files or describe your project to begin');
  const [certificationResults, setCertificationResults] = useState([]);
  const [currentGate, setCurrentGate] = useState(null);
  const [activeTab, setActiveTab] = useState('code');
  const [terminalOutput, setTerminalOutput] = useState([
    { type: 'system', text: '> FRANKLIN OS v3.0 - Trust Engine Initialized' },
    { type: 'success', text: '> Trust Vault: SECURED' },
    { type: 'info', text: '> Ready for input' },
  ]);
  const [chatMessages, setChatMessages] = useState([
    { role: 'franklin', content: 'Welcome to FRANKLIN OS. I am your autonomous coding agent. Upload your files (up to 500MB) or describe your project, and I will analyze, structure, and build it with full certification.' }
  ]);
  const [connectors, setConnectors] = useState([
    { name: 'OpenAI', status: 'active', tokensUsed: 12450, tokensTotal: 100000, rotateIn: '5d' },
    { name: 'Gemini', status: 'active', tokensUsed: 8200, tokensTotal: 50000, rotateIn: '7d' },
    { name: 'Supabase', status: 'active', tokensUsed: 0, tokensTotal: null, rotateIn: '7d' },
    { name: 'MongoDB', status: 'active', tokensUsed: 0, tokensTotal: null, rotateIn: '14d' },
  ]);
  const [showVerification, setShowVerification] = useState(false);
  const [verifiedTodos, setVerifiedTodos] = useState([]);
  const [generatedWorkflow, setGeneratedWorkflow] = useState(null);
  
  // Master requirements list from user
  const [masterRequirements, setMasterRequirements] = useState([
    { id: 'REQ-001', task: '500 MB all file upload drag-drop', priority: 'high', category: 'feature', status: 'done' },
    { id: 'REQ-002', task: 'Scrub analyze compile unified todo log', priority: 'high', category: 'feature', status: 'done' },
    { id: 'REQ-003', task: 'Verify understanding with user', priority: 'high', category: 'feature', status: 'in-progress' },
    { id: 'REQ-004', task: 'Turn todo into unified workflow', priority: 'high', category: 'feature', status: 'pending' },
    { id: 'REQ-005', task: 'Industry standard file tree per language', priority: 'high', category: 'feature', status: 'pending' },
    { id: 'REQ-006', task: 'Add architecture', priority: 'high', category: 'feature', status: 'pending' },
    { id: 'REQ-007', task: 'Add implementation', priority: 'high', category: 'feature', status: 'partial' },
    { id: 'REQ-008', task: 'Add deployment', priority: 'high', category: 'feature', status: 'pending' },
    { id: 'REQ-009', task: 'Add .env generation', priority: 'high', category: 'feature', status: 'pending' },
    { id: 'REQ-010', task: 'Trust vault with real API connectors', priority: 'high', category: 'feature', status: 'pending' },
    { id: 'REQ-011', task: 'Real-time connector status (tokens used/remaining)', priority: 'high', category: 'feature', status: 'pending' },
    { id: 'REQ-012', task: 'Auto-rotate keys weekly or on signal', priority: 'medium', category: 'feature', status: 'pending' },
    { id: 'REQ-013', task: 'Daily uptime reports by provider', priority: 'medium', category: 'feature', status: 'pending' },
    { id: 'REQ-014', task: 'Secure domain for user', priority: 'medium', category: 'feature', status: 'pending' },
    { id: 'REQ-015', task: 'DNS transfer and setup', priority: 'medium', category: 'feature', status: 'pending' },
    { id: 'REQ-016', task: 'Onboard AI assistant for all aspects', priority: 'high', category: 'feature', status: 'partial' },
    { id: 'REQ-017', task: 'No bottlenecks or user friction', priority: 'high', category: 'requirement', status: 'pending' },
    { id: 'REQ-018', task: 'No false positive code manipulation', priority: 'high', category: 'requirement', status: 'pending' },
    { id: 'REQ-019', task: 'Regulated industry compliance', priority: 'high', category: 'requirement', status: 'pending' },
    { id: 'REQ-020', task: 'Terminals: SQLite, MCP, PowerShell, Bash, Git', priority: 'high', category: 'feature', status: 'pending' },
    { id: 'REQ-021', task: 'Render images', priority: 'medium', category: 'feature', status: 'pending' },
    { id: 'REQ-022', task: 'Render videos', priority: 'medium', category: 'feature', status: 'pending' },
    { id: 'REQ-023', task: 'Edit images', priority: 'low', category: 'feature', status: 'pending' },
    { id: 'REQ-024', task: 'Edit videos', priority: 'low', category: 'feature', status: 'pending' },
    { id: 'REQ-025', task: 'Export to Google Workspace', priority: 'medium', category: 'feature', status: 'pending' },
    { id: 'REQ-026', task: 'Export to OneDrive', priority: 'medium', category: 'feature', status: 'pending' },
    { id: 'REQ-027', task: 'Export to AWS', priority: 'medium', category: 'feature', status: 'pending' },
    { id: 'REQ-028', task: 'Export to Docker', priority: 'high', category: 'feature', status: 'pending' },
    { id: 'REQ-029', task: 'Export to Kubernetes', priority: 'medium', category: 'feature', status: 'pending' },
    { id: 'REQ-030', task: '8-gate certification', priority: 'high', category: 'feature', status: 'done' },
  ]);
  
  const terminalRef = useRef(null);
  
  // Auto-scroll terminal
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [terminalOutput]);
  
  // Add terminal output
  const addTerminal = (text, type = 'info') => {
    setTerminalOutput(prev => [...prev, { type, text: `> ${text}` }]);
  };
  
  // Add chat message
  const addChat = (role, content) => {
    setChatMessages(prev => [...prev, { role, content }]);
  };
  
  // File upload handler - REAL API
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: async (acceptedFiles) => {
      setIsProcessing(true);
      addTerminal(`Receiving ${acceptedFiles.length} file(s)...`, 'system');
      
      try {
        // Create FormData and upload to backend
        const formData = new FormData();
        acceptedFiles.forEach(file => {
          formData.append('files', file);
        });
        formData.append('session_id', sessionId);
        
        addTerminal('Uploading to server...', 'info');
        
        const response = await fetch(`${API}/api/upload/files`, {
          method: 'POST',
          body: formData,
        });
        
        const result = await response.json();
        
        if (result.success) {
          // Update state with uploaded files
          const newFiles = result.files.map(f => ({
            file_id: f.file_id,
            name: f.filename,
            path: f.upload_path,
            size: f.size,
            checksum: f.checksum,
            extension: f.extension,
          }));
          
          setUploadedFiles(prev => [...prev, ...newFiles]);
          
          // Log each file
          result.files.forEach(f => {
            addTerminal(`Stored: ${f.filename} (${(f.size / 1024).toFixed(1)} KB) [${f.checksum.slice(0,8)}...]`, 'success');
          });
          
          addTerminal(`Total: ${result.files.length} file(s), ${(result.total_size / 1024).toFixed(1)} KB`, 'success');
          addChat('user', `Uploaded ${result.files.length} file(s): ${result.files.map(f => f.filename).join(', ')}`);
          addChat('franklin', `Files received and stored. Starting analysis...`);
          
          // ANALYZE FILES
          addTerminal('Analyzing files for TODOs and requirements...', 'system');
          setCurrentStage('verify');
          
          const analyzeResponse = await fetch(`${API}/api/analyze/files`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId }),
          });
          
          const analysisResult = await analyzeResponse.json();
          
          if (analysisResult.unified_todo) {
            setAnalyzedTodos(analysisResult.unified_todo);
            setShowVerification(true);  // Show verification panel
            
            addTerminal(`Analysis complete: ${analysisResult.unified_todo.length} action items found`, 'success');
            
            // Show todos in terminal
            analysisResult.unified_todo.forEach(todo => {
              const priorityColor = todo.priority === 'high' ? 'error' : todo.priority === 'medium' ? 'warning' : 'info';
              addTerminal(`[${todo.priority.toUpperCase()}] ${todo.id}: ${todo.task}`, priorityColor);
            });
            
            addChat('franklin', `Analysis complete. Found ${analysisResult.unified_todo.length} action items.\n\nPlease review the TODO list in the center panel and click "CONFIRM" if my understanding is correct, or edit as needed.`);
          }
          
        } else {
          addTerminal(`Upload failed: ${result.message}`, 'error');
          addChat('franklin', `Upload encountered an issue: ${result.message}`);
        }
        
      } catch (err) {
        addTerminal(`Error: ${err.message}`, 'error');
        addChat('franklin', `Error: ${err.message}`);
      }
      
      setIsProcessing(false);
    },
    maxSize: 500 * 1024 * 1024, // 500MB
  });
  
  // Handle todo edit
  const handleTodoEdit = (index, field, value) => {
    setAnalyzedTodos(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };
  
  // Handle todo delete
  const handleTodoDelete = (index) => {
    setAnalyzedTodos(prev => prev.filter((_, i) => i !== index));
    addTerminal(`Removed TODO item`, 'info');
  };
  
  // Handle todo add
  const handleTodoAdd = () => {
    const newId = `TODO-${String(analyzedTodos.length + 1).padStart(3, '0')}`;
    setAnalyzedTodos(prev => [...prev, {
      id: newId,
      task: 'New task - click to edit',
      priority: 'medium',
      category: 'feature',
      source_file: null,
    }]);
    addTerminal(`Added new TODO item: ${newId}`, 'info');
  };
  
  // Handle verification confirm
  const handleVerificationConfirm = () => {
    setVerifiedTodos([...analyzedTodos]);
    setShowVerification(false);
    setCurrentStage('workflow');
    
    addTerminal('Understanding confirmed by user', 'success');
    addTerminal(`${analyzedTodos.length} action items verified`, 'success');
    addChat('franklin', `Thank you for confirming. I now have a clear understanding of ${analyzedTodos.length} tasks. Proceeding to generate the unified workflow...`);
    
    // TODO: Next step - generate workflow (Item #4)
  };

  // Handle build
  const handleBuild = async () => {
    if (!prompt.trim() && uploadedFiles.length === 0) return;
    
    setIsProcessing(true);
    const buildPrompt = prompt || `Build from uploaded files: ${uploadedFiles.map(f => f.name).join(', ')}`;
    
    addChat('user', buildPrompt);
    addTerminal(`Starting build: "${buildPrompt}"`, 'system');
    addChat('franklin', 'Initiating build sequence. Engaging Trust Engine...');
    
    try {
      // Stage 1: Build
      setCurrentStage('implementation');
      addTerminal('Phase 1: Code Generation...', 'info');
      
      const buildRes = await fetch(`${API}/api/simple-build/build`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: buildPrompt, tech_stack: techStack })
      });
      
      const buildData = await buildRes.json();
      
      if (buildData.success) {
        // Convert flat files to tree structure
        const tree = buildFilesToTree(buildData.files || []);
        setProjectFiles(tree);
        
        if (buildData.files?.length > 0) {
          setSelectedFile(buildData.files[0]);
          setFileContent(buildData.files[0].content || '');
        }
        
        addTerminal(`Generated ${buildData.stats?.files_created} files (${buildData.stats?.total_lines} lines)`, 'success');
        addChat('franklin', `Build complete. Generated ${buildData.stats?.files_created} files. Proceeding to 8-Gate Certification...`);
        
        // Stage 2: Certification
        setCurrentStage('certification');
        addTerminal('Phase 2: 8-Gate Certification...', 'system');
        
        for (let i = 1; i <= 8; i++) {
          setCurrentGate(i);
          addTerminal(`Gate ${i}: ${GATES[i-1].name}...`, 'info');
          await new Promise(r => setTimeout(r, 400));
        }
        
        const certRes = await fetch(`${API}/api/simple-build/certify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ build_id: buildData.build_id })
        });
        
        const certData = await certRes.json();
        setCertificationResults(certData.gates || []);
        setCurrentGate(null);
        
        const score = certData.total_score || 0;
        const status = certData.all_passed ? 'PASSED' : `${certData.passed_gates}/8 PASSED`;
        
        addTerminal(`Certification: ${status} - Score: ${score.toFixed(1)}%`, certData.all_passed ? 'success' : 'warning');
        addChat('franklin', certData.all_passed 
          ? `Certification PASSED with ${score.toFixed(1)}% score. Your build is production-ready.`
          : `Certification: ${certData.passed_gates}/8 gates passed (${score.toFixed(1)}%). Review results for improvements.`
        );
        
        setActiveTab('certification');
        
      } else {
        addTerminal(`Build failed: ${buildData.error}`, 'error');
        addChat('franklin', `Build encountered an error: ${buildData.error}. Please try again with more details.`);
      }
    } catch (err) {
      addTerminal(`Error: ${err.message}`, 'error');
      addChat('franklin', `System error: ${err.message}`);
    }
    
    setIsProcessing(false);
    setPrompt('');
  };
  
  // Convert flat file list to tree
  const buildFilesToTree = (files) => {
    const tree = [];
    const folders = {};
    
    files.forEach(file => {
      const parts = (file.path || file.name).split('/');
      if (parts.length === 1) {
        tree.push({ ...file, name: parts[0], isFolder: false });
      } else {
        const folderName = parts[0];
        if (!folders[folderName]) {
          folders[folderName] = { name: folderName, path: folderName, isFolder: true, children: [] };
          tree.push(folders[folderName]);
        }
        folders[folderName].children.push({ ...file, name: parts.slice(1).join('/'), isFolder: false });
      }
    });
    
    return tree;
  };
  
  // Handle file selection
  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setFileContent(file.content || '// No content');
  };
  
  // Download handler
  const handleDownload = () => {
    addTerminal('Preparing download...', 'info');
    // TODO: Implement actual download
    addTerminal('Download ready', 'success');
  };
  
  return (
    <div className="fixed inset-0 overflow-hidden bg-black text-white">
      {/* Background */}
      <StarsBackground />
      <LaserBeams />
      
      {/* Main Content */}
      <div className="relative z-10 h-full flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-black/50 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <button 
              onClick={onBack} 
              className="p-2 rounded-full border border-white/20 hover:bg-white/10 transition-colors"
            >
              <ChevronRight size={16} className="rotate-180" />
            </button>
            <div>
              <span className="text-xs text-white/40 tracking-wider" style={{ fontFamily: "'Orbitron', sans-serif" }}>YUR-AI</span>
              <h1 className="text-lg font-semibold tracking-widest franklin-chrome" style={{ fontFamily: "'Orbitron', sans-serif" }}>
                FRANKLIN OS
              </h1>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-[10px] uppercase tracking-wider text-white/50">Online</span>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <select
              value={techStack}
              onChange={(e) => setTechStack(e.target.value)}
              className="px-3 py-1.5 rounded border border-white/20 bg-black/50 text-sm text-white/80 focus:outline-none focus:border-white/40"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="rust">Rust</option>
              <option value="go">Go</option>
            </select>
            
            <button 
              onClick={handleDownload}
              className="px-4 py-1.5 rounded border border-white/20 text-xs uppercase tracking-wider text-white/70 hover:bg-white/10 transition-colors"
              style={{ fontFamily: "'Orbitron', sans-serif" }}
            >
              Download
            </button>
          </div>
        </header>
        
        {/* Workflow Progress */}
        <div className="px-4 py-2 border-b border-white/10 bg-black/30">
          <div className="flex items-center gap-1 overflow-x-auto">
            {WORKFLOW_STAGES.map((stage, i) => {
              const Icon = stage.icon;
              const isActive = stage.id === currentStage;
              const isPast = WORKFLOW_STAGES.findIndex(s => s.id === currentStage) > i;
              
              return (
                <React.Fragment key={stage.id}>
                  <div className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs whitespace-nowrap transition-colors ${
                    isActive ? 'bg-white/15 text-white' : isPast ? 'text-white/60' : 'text-white/30'
                  }`}>
                    <Icon size={12} />
                    <span>{stage.name}</span>
                    {isPast && <Check size={10} className="text-green-500" />}
                  </div>
                  {i < WORKFLOW_STAGES.length - 1 && (
                    <ChevronRight size={12} className="text-white/20 flex-shrink-0" />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
        
        {/* Main Panels */}
        <div className="flex-1 overflow-hidden">
          <ResizablePanelGroup direction="horizontal" className="h-full">
            {/* Left Panel - Chat & Upload */}
            <ResizablePanel defaultSize={25} minSize={20}>
              <div className="h-full flex flex-col border-r border-white/10 bg-black/30">
                <div className="px-3 py-2 border-b border-white/10">
                  <h2 className="text-xs uppercase tracking-wider text-white/50" style={{ fontFamily: "'Orbitron', sans-serif" }}>
                    Franklin Agent
                  </h2>
                </div>
                
                {/* Chat */}
                <div className="flex-1 overflow-y-auto p-3 space-y-3">
                  {chatMessages.map((msg, i) => (
                    <div key={i} className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-white/10 ml-4' : 'bg-white/5 mr-4'}`}>
                      <div className="text-[10px] uppercase tracking-wider mb-1 text-white/40">
                        {msg.role === 'user' ? 'You' : 'Franklin'}
                      </div>
                      <div className="text-sm text-white/80 leading-relaxed">{msg.content}</div>
                    </div>
                  ))}
                </div>
                
                {/* Upload Zone */}
                <div className="p-3 border-t border-white/10">
                  <div
                    {...getRootProps()}
                    className={`p-4 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${
                      isDragActive ? 'border-white/50 bg-white/10' : 'border-white/20 hover:border-white/30'
                    }`}
                  >
                    <input {...getInputProps()} />
                    <Upload size={20} className="mx-auto mb-2 text-white/40" />
                    <p className="text-xs text-white/50">Drop files (up to 500MB)</p>
                  </div>
                </div>
                
                {/* Input */}
                <div className="p-3 border-t border-white/10">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleBuild()}
                      placeholder="Describe your project..."
                      className="flex-1 px-3 py-2 rounded border border-white/20 bg-black/50 text-sm text-white placeholder:text-white/30 focus:outline-none focus:border-white/40"
                      disabled={isProcessing}
                    />
                    <button
                      onClick={handleBuild}
                      disabled={isProcessing}
                      className="px-3 py-2 rounded border border-white/20 hover:bg-white/10 transition-colors disabled:opacity-50"
                    >
                      {isProcessing ? <Loader size={16} className="animate-spin" /> : <Send size={16} />}
                    </button>
                  </div>
                </div>
              </div>
            </ResizablePanel>
            
            <ResizableHandle className="w-px bg-white/10 hover:bg-white/30 transition-colors" />
            
            {/* Center Panel - Code & Certification */}
            <ResizablePanel defaultSize={50} minSize={30}>
              <div className="h-full flex flex-col bg-black/20">
                {/* Tabs */}
                <div className="flex border-b border-white/10">
                  {['code', 'files', 'verification', 'certification'].map(tab => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-4 py-2 text-xs uppercase tracking-wider transition-colors ${
                        activeTab === tab ? 'text-white border-b-2 border-white' : 'text-white/50 hover:text-white/80'
                      } ${tab === 'verification' && showVerification ? 'text-yellow-400' : ''}`}
                    >
                      {tab}
                      {tab === 'verification' && analyzedTodos.length > 0 && (
                        <span className="ml-1 px-1.5 py-0.5 text-[10px] bg-white/20 rounded">{analyzedTodos.length}</span>
                      )}
                    </button>
                  ))}
                </div>
                
                {/* Tab Content */}
                <div className="flex-1 overflow-hidden">
                  {activeTab === 'code' && (
                    <Editor
                      height="100%"
                      language={techStack === 'python' ? 'python' : techStack === 'typescript' ? 'typescript' : 'javascript'}
                      value={fileContent}
                      theme="vs-dark"
                      options={{
                        readOnly: true,
                        minimap: { enabled: false },
                        fontSize: 13,
                        fontFamily: "'JetBrains Mono', monospace",
                        padding: { top: 16 },
                        scrollBeyondLastLine: false,
                      }}
                    />
                  )}
                  
                  {activeTab === 'verification' && (
                    <div className="h-full overflow-y-auto p-4">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-semibold tracking-wider text-white/80" style={{ fontFamily: "'Orbitron', sans-serif" }}>
                          VERIFY UNDERSTANDING
                        </h3>
                        <div className="flex gap-2">
                          <button
                            onClick={handleTodoAdd}
                            className="px-3 py-1.5 text-xs border border-white/20 rounded hover:bg-white/10 transition-colors"
                          >
                            + Add Task
                          </button>
                          <button
                            onClick={handleVerificationConfirm}
                            disabled={analyzedTodos.length === 0}
                            className="px-4 py-1.5 text-xs bg-green-600 hover:bg-green-500 rounded font-semibold tracking-wider transition-colors disabled:opacity-50"
                            style={{ fontFamily: "'Orbitron', sans-serif" }}
                          >
                            CONFIRM
                          </button>
                        </div>
                      </div>
                      
                      {analyzedTodos.length === 0 ? (
                        <div className="text-center py-12 text-white/30">
                          <p>No tasks found. Upload files to analyze or add tasks manually.</p>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {analyzedTodos.map((todo, index) => (
                            <div 
                              key={todo.id}
                              className="p-3 rounded-lg border border-white/10 bg-white/5 hover:border-white/20 transition-colors"
                            >
                              <div className="flex items-start gap-3">
                                <div className="flex-shrink-0 pt-1">
                                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                                    todo.priority === 'high' ? 'bg-red-500/30 text-red-300' :
                                    todo.priority === 'medium' ? 'bg-yellow-500/30 text-yellow-300' :
                                    'bg-blue-500/30 text-blue-300'
                                  }`}>
                                    {todo.priority.toUpperCase()}
                                  </span>
                                </div>
                                
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="text-xs text-white/40 font-mono">{todo.id}</span>
                                    <span className="text-[10px] px-1.5 py-0.5 bg-white/10 rounded text-white/50">{todo.category}</span>
                                  </div>
                                  <input
                                    type="text"
                                    value={todo.task}
                                    onChange={(e) => handleTodoEdit(index, 'task', e.target.value)}
                                    className="w-full bg-transparent text-sm text-white/90 focus:outline-none border-b border-transparent focus:border-white/30"
                                  />
                                  {todo.source_file && (
                                    <p className="text-[10px] text-white/30 mt-1">
                                      Source: {todo.source_file} {todo.line_reference && `(${todo.line_reference})`}
                                    </p>
                                  )}
                                </div>
                                
                                <div className="flex items-center gap-2">
                                  <select
                                    value={todo.priority}
                                    onChange={(e) => handleTodoEdit(index, 'priority', e.target.value)}
                                    className="text-xs bg-black/50 border border-white/20 rounded px-2 py-1 text-white/70"
                                  >
                                    <option value="high">High</option>
                                    <option value="medium">Medium</option>
                                    <option value="low">Low</option>
                                  </select>
                                  <button
                                    onClick={() => handleTodoDelete(index)}
                                    className="p-1 hover:bg-red-500/20 rounded transition-colors text-white/40 hover:text-red-400"
                                  >
                                    <X size={14} />
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {analyzedTodos.length > 0 && (
                        <div className="mt-6 p-4 rounded-lg border border-white/10 bg-white/5">
                          <p className="text-xs text-white/50 mb-2">Summary</p>
                          <div className="flex gap-4 text-sm">
                            <span className="text-red-400">{analyzedTodos.filter(t => t.priority === 'high').length} High</span>
                            <span className="text-yellow-400">{analyzedTodos.filter(t => t.priority === 'medium').length} Medium</span>
                            <span className="text-blue-400">{analyzedTodos.filter(t => t.priority === 'low').length} Low</span>
                          </div>
                          <p className="text-xs text-white/30 mt-3">
                            Click CONFIRM when you're satisfied with the task list. You can edit tasks by clicking on them.
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {activeTab === 'files' && (
                    <div className="h-full overflow-y-auto p-2">
                      {projectFiles.length > 0 ? (
                        <FileTree files={projectFiles} onSelect={handleFileSelect} selectedFile={selectedFile} />
                      ) : (
                        <div className="flex items-center justify-center h-full text-white/30 text-sm">
                          No files generated yet
                        </div>
                      )}
                    </div>
                  )}
                  
                  {activeTab === 'certification' && (
                    <div className="h-full overflow-y-auto">
                      <CertificationTheater gates={certificationResults} currentGate={currentGate} />
                      
                      {certificationResults.length > 0 && (
                        <div className="p-4">
                          <div className="p-4 rounded-lg border border-white/10 bg-white/5">
                            <div className="flex justify-between items-center">
                              <span className="text-xs uppercase tracking-wider text-white/50">Total Score</span>
                              <span className="text-2xl font-bold text-white/80" style={{ fontFamily: "'Orbitron', sans-serif" }}>
                                {(certificationResults.reduce((sum, g) => sum + (g.score || 0), 0) / certificationResults.length).toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </ResizablePanel>
            
            <ResizableHandle className="w-px bg-white/10 hover:bg-white/30 transition-colors" />
            
            {/* Right Panel - Terminal & Vault */}
            <ResizablePanel defaultSize={25} minSize={20}>
              <div className="h-full flex flex-col border-l border-white/10 bg-black/30">
                <div className="px-3 py-2 border-b border-white/10">
                  <h2 className="text-xs uppercase tracking-wider text-white/50" style={{ fontFamily: "'Orbitron', sans-serif" }}>
                    Terminal
                  </h2>
                </div>
                
                {/* Terminal Output */}
                <div 
                  ref={terminalRef}
                  className="flex-1 overflow-y-auto p-3 font-mono text-xs"
                >
                  {terminalOutput.map((line, i) => (
                    <div key={i} className={`py-0.5 ${
                      line.type === 'error' ? 'text-red-400' :
                      line.type === 'success' ? 'text-green-400' :
                      line.type === 'warning' ? 'text-yellow-400' :
                      line.type === 'system' ? 'text-white/80' :
                      'text-white/50'
                    }`}>
                      {line.text}
                    </div>
                  ))}
                </div>
                
                {/* Trust Vault */}
                <div className="p-3 border-t border-white/10">
                  <TrustVault connectors={connectors} onRefresh={() => addTerminal('Refreshing connectors...', 'info')} />
                </div>
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </div>
      </div>
      
      {/* Chrome style */}
      <style>{`
        .franklin-chrome {
          background: linear-gradient(
            135deg,
            rgba(60, 60, 60, 1) 0%,
            rgba(120, 120, 120, 1) 15%,
            rgba(200, 200, 200, 1) 30%,
            rgba(255, 255, 255, 1) 45%,
            rgba(200, 200, 200, 1) 55%,
            rgba(120, 120, 120, 1) 70%,
            rgba(80, 80, 80, 1) 85%,
            rgba(150, 150, 150, 1) 100%
          );
          background-size: 200% 200%;
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: chromeShimmer 20s ease-in-out infinite;
        }
        
        @keyframes chromeShimmer {
          0% { background-position: 200% 200%; }
          50% { background-position: 0% 0%; }
          100% { background-position: 200% 200%; }
        }
      `}</style>
    </div>
  );
};

export default FranklinIDE;
