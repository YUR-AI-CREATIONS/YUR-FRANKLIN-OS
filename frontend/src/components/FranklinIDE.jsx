import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from './ui/resizable';
import Editor from '@monaco-editor/react';
import { useDropzone } from 'react-dropzone';
import {
  Terminal, Code, FileCode, FolderTree, Upload, Download, Play, 
  CheckCircle, XCircle, Loader, Settings, Database, Cloud,
  GitBranch, Box, Cpu, Shield, Eye, Zap, Send, ChevronRight,
  File, Image, Video, Music, Archive, MoreHorizontal, X,
  Maximize2, Minimize2, RefreshCw, Copy, Trash2, ExternalLink
} from 'lucide-react';
import '../LiquidGalaxy.css';

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

// Brand showcase items
const BRANDS = [
  { name: 'Docker', icon: Box },
  { name: 'Kubernetes', icon: Cloud },
  { name: 'AWS', icon: Cloud },
  { name: 'PostgreSQL', icon: Database },
  { name: 'MongoDB', icon: Database },
  { name: 'Redis', icon: Zap },
  { name: 'Git', icon: GitBranch },
  { name: 'Python', icon: FileCode },
  { name: 'TypeScript', icon: Code },
  { name: 'React', icon: RefreshCw },
];

// Terminal types
const TERMINALS = [
  { id: 'bash', name: 'Bash', icon: Terminal },
  { id: 'powershell', name: 'PowerShell', icon: Terminal },
  { id: 'sqlite', name: 'SQLite', icon: Database },
  { id: 'git', name: 'Git', icon: GitBranch },
];

// Stars background component
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
      stars = Array.from({ length: 200 }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 2 + 0.5,
        speed: Math.random() * 0.5 + 0.1,
        brightness: Math.random(),
        twinkleSpeed: Math.random() * 0.02 + 0.01,
      }));
    };
    
    let time = 0;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      stars.forEach(star => {
        const twinkle = Math.sin(time * star.twinkleSpeed) * 0.5 + 0.5;
        const alpha = star.brightness * twinkle * 0.8 + 0.2;
        
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
        ctx.fill();
        
        // Glow effect for brighter stars
        if (star.size > 1.5) {
          ctx.beginPath();
          ctx.arc(star.x, star.y, star.size * 3, 0, Math.PI * 2);
          const gradient = ctx.createRadialGradient(
            star.x, star.y, 0,
            star.x, star.y, star.size * 3
          );
          gradient.addColorStop(0, `rgba(0, 240, 255, ${alpha * 0.3})`);
          gradient.addColorStop(1, 'transparent');
          ctx.fillStyle = gradient;
          ctx.fill();
        }
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
  
  return <canvas ref={canvasRef} className="stars-layer" />;
};

// Certification Theater Component
const CertificationTheater = ({ gates, isRunning, currentGate }) => {
  return (
    <div className="cert-theater">
      {GATES.map((gate, index) => {
        const gateResult = gates.find(g => g.gate_num === gate.id);
        const status = currentGate === gate.id ? 'running' 
          : gateResult?.passed ? 'passed' 
          : gateResult?.passed === false ? 'failed' 
          : 'pending';
        
        const Icon = gate.icon;
        
        return (
          <motion.div
            key={gate.id}
            className={`cert-gate ${status}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className="gate-number">{gate.id}</div>
            <div className="gate-name">{gate.name}</div>
            <div className="gate-status">
              {status === 'passed' && <CheckCircle size={20} color="#00ff88" />}
              {status === 'failed' && <XCircle size={20} color="#ff3366" />}
              {status === 'running' && <Loader size={20} color="#00f0ff" />}
              {status === 'pending' && <Icon size={20} color="#52525b" />}
            </div>
            {gateResult?.score !== undefined && (
              <div className="mt-2 text-xs" style={{ color: gateResult.passed ? '#00ff88' : '#ff3366' }}>
                {gateResult.score.toFixed(0)}%
              </div>
            )}
          </motion.div>
        );
      })}
    </div>
  );
};

// File Upload Component
const FileUploadZone = ({ onFilesAccepted }) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: onFilesAccepted,
    maxSize: 500 * 1024 * 1024, // 500MB
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
      'video/*': ['.mp4', '.webm', '.mov'],
      'application/*': ['.pdf', '.zip', '.json'],
      'text/*': ['.txt', '.md', '.py', '.js', '.ts', '.jsx', '.tsx'],
    }
  });
  
  return (
    <div {...getRootProps()} className={`upload-zone ${isDragActive ? 'active' : ''}`}>
      <input {...getInputProps()} />
      <Upload size={48} color="#00f0ff" style={{ marginBottom: 16 }} />
      <p style={{ fontFamily: 'Orbitron', fontSize: 14, color: '#00f0ff', marginBottom: 8 }}>
        DROP FILES HERE
      </p>
      <p style={{ fontSize: 13, color: '#a1a1aa' }}>
        Images, Videos, Code, Documents up to 500MB
      </p>
    </div>
  );
};

// Terminal Component
const TerminalPanel = ({ type, output }) => {
  const terminalRef = useRef(null);
  
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [output]);
  
  return (
    <div className="terminal-container" ref={terminalRef}>
      {output.map((line, i) => (
        <div key={i} className={`terminal-line ${line.type}`}>
          {line.text}
        </div>
      ))}
    </div>
  );
};

// Main IDE Component
export const FranklinIDE = ({ onBack }) => {
  // State
  const [buildPrompt, setBuildPrompt] = useState('');
  const [techStack, setTechStack] = useState('python');
  const [isBuilding, setIsBuilding] = useState(false);
  const [isCertifying, setIsCertifying] = useState(false);
  const [currentBuild, setCurrentBuild] = useState(null);
  const [certificationResults, setCertificationResults] = useState([]);
  const [currentGate, setCurrentGate] = useState(null);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('// Select a file to view');
  const [activeTab, setActiveTab] = useState('code');
  const [activeTerminal, setActiveTerminal] = useState('bash');
  const [terminalOutput, setTerminalOutput] = useState([
    { type: 'system', text: '> FRANKLIN OS Terminal v3.0' },
    { type: 'info', text: '> Trinity Spine: CONNECTED' },
    { type: 'info', text: '> Ouroboros Loop: STANDBY' },
    { type: 'success', text: '> System ready for build' },
  ]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [showUpload, setShowUpload] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { role: 'franklin', content: 'Welcome to FRANKLIN OS. I am your autonomous coding agent, fluent in all languages. Tell me what to build.' }
  ]);
  
  // Add terminal output
  const addTerminal = (text, type = 'info') => {
    setTerminalOutput(prev => [...prev, { type, text: `> ${text}` }]);
  };
  
  // Handle build
  const handleBuild = async () => {
    if (!buildPrompt.trim() || isBuilding) return;
    
    setIsBuilding(true);
    setCertificationResults([]);
    setCurrentGate(null);
    addTerminal(`Initiating build: "${buildPrompt}"`, 'system');
    addTerminal(`Tech Stack: ${techStack.toUpperCase()}`, 'info');
    
    setChatMessages(prev => [...prev, 
      { role: 'user', content: buildPrompt },
      { role: 'franklin', content: 'Initiating build sequence. Engaging Trinity Spine orchestration...' }
    ]);
    
    try {
      // Build
      addTerminal('Phase 1: Code Generation...', 'info');
      const buildRes = await fetch(`${API}/api/simple-build/build`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: buildPrompt, tech_stack: techStack })
      });
      
      const buildData = await buildRes.json();
      
      if (buildData.success) {
        setCurrentBuild(buildData);
        setFiles(buildData.files || []);
        addTerminal(`Build complete: ${buildData.stats?.files_created} files created`, 'success');
        addTerminal(`Total lines: ${buildData.stats?.total_lines}`, 'info');
        
        setChatMessages(prev => [...prev, {
          role: 'franklin',
          content: `Build complete. Generated ${buildData.stats?.files_created} files (${buildData.stats?.total_lines} lines). Proceeding to 8-Gate Certification...`
        }]);
        
        // Auto-select first file
        if (buildData.files?.length > 0) {
          const firstFile = buildData.files[0];
          setSelectedFile(firstFile);
          setFileContent(firstFile.content || '// Loading...');
        }
        
        // Start certification
        setIsCertifying(true);
        addTerminal('Phase 2: 8-Gate Certification...', 'system');
        
        for (let i = 1; i <= 8; i++) {
          setCurrentGate(i);
          addTerminal(`Running Gate ${i}: ${GATES[i-1].name}...`, 'info');
          await new Promise(r => setTimeout(r, 500)); // Visual delay
        }
        
        const certRes = await fetch(`${API}/api/simple-build/certify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ build_id: buildData.build_id })
        });
        
        const certData = await certRes.json();
        setCertificationResults(certData.gates || []);
        setCurrentGate(null);
        setIsCertifying(false);
        
        const allPassed = certData.all_passed;
        const score = certData.total_score || 0;
        
        if (allPassed) {
          addTerminal(`CERTIFICATION PASSED - Score: ${score.toFixed(1)}%`, 'success');
          addTerminal('Build is PRODUCTION READY', 'success');
        } else {
          addTerminal(`CERTIFICATION: ${certData.passed_gates}/8 gates passed - Score: ${score.toFixed(1)}%`, 'warning');
        }
        
        setChatMessages(prev => [...prev, {
          role: 'franklin',
          content: allPassed 
            ? `Certification PASSED with ${score.toFixed(1)}% score. All 8 gates cleared. Build is production-ready and can be deployed.`
            : `Certification complete: ${certData.passed_gates}/8 gates passed (${score.toFixed(1)}%). Review failed gates for improvements.`
        }]);
        
      } else {
        addTerminal(`Build failed: ${buildData.error || 'Unknown error'}`, 'error');
        setChatMessages(prev => [...prev, {
          role: 'franklin',
          content: `Build failed: ${buildData.error}. Please try again with a clearer prompt.`
        }]);
      }
    } catch (err) {
      addTerminal(`Error: ${err.message}`, 'error');
      setChatMessages(prev => [...prev, {
        role: 'franklin',
        content: `System error: ${err.message}. Checking Trinity Spine connection...`
      }]);
    }
    
    setIsBuilding(false);
  };
  
  // Handle file selection
  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setFileContent(file.content || '// No content');
  };
  
  // Handle download
  const handleDownload = async () => {
    if (!currentBuild?.build_id) return;
    
    addTerminal('Preparing download...', 'info');
    window.open(`${API}/api/simple-build/build/${currentBuild.build_id}/download`, '_blank');
    addTerminal('Download initiated', 'success');
  };
  
  // Handle file upload
  const handleFilesAccepted = (acceptedFiles) => {
    setUploadedFiles(prev => [...prev, ...acceptedFiles.map(f => ({
      name: f.name,
      size: f.size,
      type: f.type,
      file: f
    }))]);
    addTerminal(`Uploaded ${acceptedFiles.length} file(s)`, 'success');
    setShowUpload(false);
  };
  
  // Get file icon
  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(ext)) return Image;
    if (['mp4', 'webm', 'mov'].includes(ext)) return Video;
    if (['mp3', 'wav', 'ogg'].includes(ext)) return Music;
    if (['zip', 'tar', 'gz'].includes(ext)) return Archive;
    return File;
  };
  
  return (
    <div className="fixed inset-0 overflow-hidden">
      {/* Background */}
      <div className="liquid-galaxy" />
      <StarsBackground />
      
      {/* Main Content */}
      <div className="relative z-10 h-full flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-3 border-b border-white/10" style={{ background: 'rgba(0,0,0,0.5)' }}>
          <div className="flex items-center gap-4">
            <button onClick={onBack} className="btn-secondary" style={{ padding: '6px 12px' }}>
              <ChevronRight size={16} style={{ transform: 'rotate(180deg)' }} />
            </button>
            <h1 style={{ fontFamily: 'Orbitron', fontSize: 20, color: '#00f0ff', letterSpacing: 4 }}>
              FRANKLIN OS
            </h1>
            <span className="status-dot" style={{ width: 8, height: 8, borderRadius: '50%', background: '#00ff88', boxShadow: '0 0 10px #00ff88' }} />
            <span style={{ fontSize: 11, color: '#00ff88', fontFamily: 'Orbitron' }}>ONLINE</span>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Tech Stack Selector */}
            <select
              value={techStack}
              onChange={(e) => setTechStack(e.target.value)}
              className="input-field"
              style={{ width: 140, padding: '8px 12px', fontSize: 12 }}
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="rust">Rust</option>
              <option value="go">Go</option>
            </select>
            
            <button onClick={() => setShowUpload(true)} className="btn-secondary" style={{ padding: '8px 12px' }}>
              <Upload size={16} />
            </button>
            
            {currentBuild && (
              <button onClick={handleDownload} className="btn-primary" style={{ padding: '8px 16px' }}>
                <Download size={16} style={{ marginRight: 8 }} />
                Download
              </button>
            )}
          </div>
        </header>
        
        {/* Brand Showcase */}
        <div className="brand-showcase" style={{ background: 'rgba(0,0,0,0.3)', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
          {BRANDS.map((brand, i) => {
            const Icon = brand.icon;
            return (
              <div key={i} className="brand-item">
                <Icon size={14} />
                {brand.name}
              </div>
            );
          })}
        </div>
        
        {/* Main Panels */}
        <div className="flex-1 overflow-hidden p-4">
          <ResizablePanelGroup direction="horizontal" className="h-full">
            {/* Left Panel - Chat & Files */}
            <ResizablePanel defaultSize={25} minSize={15}>
              <div className="glass-panel illuminated-border h-full flex flex-col">
                <div className="panel-header">
                  <div className="status-dot" />
                  <span>FRANKLIN</span>
                </div>
                
                {/* Chat Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {chatMessages.map((msg, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-500/20 ml-8' : 'bg-white/5 mr-8'}`}
                    >
                      <div className="text-xs mb-1" style={{ color: msg.role === 'user' ? '#0080ff' : '#00f0ff', fontFamily: 'Orbitron' }}>
                        {msg.role === 'user' ? 'YOU' : 'FRANKLIN'}
                      </div>
                      <div style={{ fontSize: 13, lineHeight: 1.5 }}>{msg.content}</div>
                    </motion.div>
                  ))}
                </div>
                
                {/* Input */}
                <div className="p-4 border-t border-white/10">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={buildPrompt}
                      onChange={(e) => setBuildPrompt(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleBuild()}
                      placeholder="Tell me what to build..."
                      className="input-field flex-1"
                      disabled={isBuilding}
                    />
                    <button 
                      onClick={handleBuild}
                      disabled={isBuilding || !buildPrompt.trim()}
                      className="btn-primary"
                      style={{ padding: '12px' }}
                    >
                      {isBuilding ? <Loader size={18} className="animate-spin" /> : <Send size={18} />}
                    </button>
                  </div>
                </div>
              </div>
            </ResizablePanel>
            
            <ResizableHandle className="resize-handle w-2 mx-1 rounded" />
            
            {/* Center Panel - Code & Certification */}
            <ResizablePanel defaultSize={50} minSize={30}>
              <div className="glass-panel illuminated-border h-full flex flex-col">
                {/* Tabs */}
                <div className="tab-bar">
                  <button 
                    className={`tab-item ${activeTab === 'code' ? 'active' : ''}`}
                    onClick={() => setActiveTab('code')}
                  >
                    <Code size={14} style={{ marginRight: 6, display: 'inline' }} />
                    Code
                  </button>
                  <button 
                    className={`tab-item ${activeTab === 'certification' ? 'active' : ''}`}
                    onClick={() => setActiveTab('certification')}
                  >
                    <Shield size={14} style={{ marginRight: 6, display: 'inline' }} />
                    Certification
                  </button>
                  <button 
                    className={`tab-item ${activeTab === 'files' ? 'active' : ''}`}
                    onClick={() => setActiveTab('files')}
                  >
                    <FolderTree size={14} style={{ marginRight: 6, display: 'inline' }} />
                    Files
                  </button>
                </div>
                
                {/* Tab Content */}
                <div className="flex-1 overflow-hidden">
                  <AnimatePresence mode="wait">
                    {activeTab === 'code' && (
                      <motion.div
                        key="code"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="h-full"
                      >
                        <Editor
                          height="100%"
                          language={techStack === 'python' ? 'python' : 'javascript'}
                          value={fileContent}
                          theme="vs-dark"
                          options={{
                            readOnly: true,
                            minimap: { enabled: true },
                            fontSize: 13,
                            fontFamily: 'JetBrains Mono',
                            padding: { top: 16 },
                          }}
                        />
                      </motion.div>
                    )}
                    
                    {activeTab === 'certification' && (
                      <motion.div
                        key="certification"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="h-full overflow-y-auto p-4"
                      >
                        <h3 style={{ fontFamily: 'Orbitron', fontSize: 14, color: '#00f0ff', marginBottom: 16 }}>
                          8-GATE CERTIFICATION THEATER
                        </h3>
                        <CertificationTheater 
                          gates={certificationResults} 
                          isRunning={isCertifying}
                          currentGate={currentGate}
                        />
                        
                        {certificationResults.length > 0 && (
                          <div className="mt-6 p-4 rounded-lg" style={{ background: 'rgba(0,0,0,0.3)' }}>
                            <div className="flex justify-between items-center mb-2">
                              <span style={{ fontFamily: 'Orbitron', fontSize: 12, color: '#a1a1aa' }}>TOTAL SCORE</span>
                              <span style={{ fontFamily: 'Orbitron', fontSize: 24, color: certificationResults.every(g => g.passed) ? '#00ff88' : '#ffaa00' }}>
                                {(certificationResults.reduce((sum, g) => sum + (g.score || 0), 0) / certificationResults.length).toFixed(1)}%
                              </span>
                            </div>
                            <div className="progress-bar">
                              <div 
                                className="progress-fill" 
                                style={{ width: `${certificationResults.reduce((sum, g) => sum + (g.score || 0), 0) / certificationResults.length}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </motion.div>
                    )}
                    
                    {activeTab === 'files' && (
                      <motion.div
                        key="files"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="h-full overflow-y-auto p-4"
                      >
                        <h3 style={{ fontFamily: 'Orbitron', fontSize: 14, color: '#00f0ff', marginBottom: 16 }}>
                          PROJECT FILES
                        </h3>
                        <div className="space-y-2">
                          {files.map((file, i) => {
                            const Icon = getFileIcon(file.path || file.name || '');
                            return (
                              <div
                                key={i}
                                onClick={() => handleFileSelect(file)}
                                className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                                  selectedFile === file ? 'bg-cyan-500/20 border border-cyan-500/50' : 'bg-white/5 hover:bg-white/10'
                                }`}
                              >
                                <Icon size={16} color="#00f0ff" />
                                <span className="flex-1 truncate" style={{ fontFamily: 'JetBrains Mono', fontSize: 13 }}>
                                  {file.path || file.name}
                                </span>
                                <span style={{ fontSize: 11, color: '#52525b' }}>
                                  {file.lines || '?'} lines
                                </span>
                              </div>
                            );
                          })}
                          {files.length === 0 && (
                            <div className="text-center py-8" style={{ color: '#52525b' }}>
                              No files generated yet
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            </ResizablePanel>
            
            <ResizableHandle className="resize-handle w-2 mx-1 rounded" />
            
            {/* Right Panel - Terminal */}
            <ResizablePanel defaultSize={25} minSize={15}>
              <div className="glass-panel illuminated-border h-full flex flex-col">
                {/* Terminal Tabs */}
                <div className="tab-bar">
                  {TERMINALS.map(term => {
                    const Icon = term.icon;
                    return (
                      <button
                        key={term.id}
                        className={`tab-item ${activeTerminal === term.id ? 'active' : ''}`}
                        onClick={() => setActiveTerminal(term.id)}
                      >
                        <Icon size={12} style={{ marginRight: 4, display: 'inline' }} />
                        {term.name}
                      </button>
                    );
                  })}
                </div>
                
                {/* Terminal Output */}
                <div className="flex-1 overflow-hidden p-2">
                  <TerminalPanel type={activeTerminal} output={terminalOutput} />
                </div>
                
                {/* Terminal Input */}
                <div className="p-3 border-t border-white/10">
                  <div className="flex items-center gap-2">
                    <span style={{ color: '#00ff88', fontFamily: 'JetBrains Mono', fontSize: 13 }}>$</span>
                    <input
                      type="text"
                      placeholder="Enter command..."
                      className="input-field flex-1"
                      style={{ fontSize: 13, fontFamily: 'JetBrains Mono', padding: '8px 12px' }}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && e.target.value) {
                          addTerminal(e.target.value, 'system');
                          addTerminal('Command execution is simulated', 'info');
                          e.target.value = '';
                        }
                      }}
                    />
                  </div>
                </div>
              </div>
            </Panel>
          </PanelGroup>
        </div>
      </div>
      
      {/* File Upload Modal */}
      <AnimatePresence>
        {showUpload && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center"
            style={{ background: 'rgba(0,0,0,0.8)' }}
            onClick={() => setShowUpload(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="glass-panel p-6 w-full max-w-lg"
              onClick={e => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-4">
                <h3 style={{ fontFamily: 'Orbitron', fontSize: 16, color: '#00f0ff' }}>UPLOAD FILES</h3>
                <button onClick={() => setShowUpload(false)} className="p-2 hover:bg-white/10 rounded">
                  <X size={20} />
                </button>
              </div>
              <FileUploadZone onFilesAccepted={handleFilesAccepted} />
              
              {uploadedFiles.length > 0 && (
                <div className="mt-4 space-y-2">
                  {uploadedFiles.map((f, i) => {
                    const Icon = getFileIcon(f.name);
                    return (
                      <div key={i} className="flex items-center gap-3 p-2 bg-white/5 rounded">
                        <Icon size={16} color="#00f0ff" />
                        <span className="flex-1 truncate" style={{ fontSize: 13 }}>{f.name}</span>
                        <span style={{ fontSize: 11, color: '#52525b' }}>{(f.size / 1024).toFixed(1)} KB</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FranklinIDE;
