/**
 * FranklinIDE
 * 
 * Main IDE layout mirroring VS Code with glassmorphism aesthetic.
 * - Left Sidebar: Agents, LLMs, Files, Tools
 * - Center: Code Editor with Tabs
 * - Right Panel: Inspector, Properties, Settings
 * - Bottom: Terminals (Local, Cloud, MCP)
 * - Floating: Ghost Franklin orchestrator
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  PanelGroup,
  Panel,
  PanelResizeHandle,
} from 'react-resizable-panels';
import {
  Code2,
  Terminal,
  Settings,
  Zap,
  Brain,
  FileCode,
  Shield,
  Play,
  Plus,
  ChevronDown,
  Eye,
} from 'lucide-react';

import GlassPanel from '../ui/GlassPanel';
import ContextWindow from '../ui/ContextWindow';
import GhostFranklin from '../ui/GhostFranklin';
import PreviewPortal from './PreviewPortal';

// GalacticBackground Component - Reused from App.js
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

const FranklinIDE = ({ onNavigate, project }) => {
  const [activeTab, setActiveTab] = useState('editor');
  const [activePreviewTab, setActivePreviewTab] = useState('code'); // 'code' | 'preview'
  const [activeTerminal, setActiveTerminal] = useState('local');
  const [ghostFranklinVisible, setGhostFranklinVisible] = useState(true);
  const [generatedCode, setGeneratedCode] = useState(''); // Store generated code
  const [buildResult, setBuildResult] = useState(null); // Store build result
  const [sidebarOpen, setSidebarOpen] = useState({
    agents: true,
    llms: true,
    files: false,
    tools: true,
  });

  const [openFiles, setOpenFiles] = useState([
    { id: 'main', name: 'main.py', language: 'python', content: '# Your code here\n' },
    { id: 'schema', name: 'schema.sql', language: 'sql', content: 'SELECT * FROM users;\n' },
  ]);

  return (
    <div className="w-screen h-screen bg-slate-950 text-slate-200 overflow-hidden relative">
      {/* GALACTIC BACKGROUND */}
      <GalacticBackground />
      
      {/* GHOST FRANKLIN TEXT WATERMARK */}
      <div className="fixed inset-0 flex items-center justify-center pointer-events-none z-[1]">
        <h1 className="select-none" style={{ fontFamily: "'Orbitron', sans-serif", fontSize: '12vw', fontWeight: 600, letterSpacing: '0.3em', color: 'rgba(80,80,80,0.12)' }}>FRANKLIN</h1>
      </div>

      {/* Background */}
      <div className="absolute inset-0 opacity-20 z-5">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-transparent to-purple-900/20" />
      </div>

      {/* Main Layout */}
      <PanelGroup direction="horizontal" className="relative z-10">
        {/* ============================================================ */}
        {/* LEFT SIDEBAR                                               */}
        {/* ============================================================ */}
        <Panel minSize={15} maxSize={25} defaultSize={18}>
          <div className="h-full flex flex-col overflow-hidden p-3 gap-3">
            <GlassPanel variant="blue" rounded="md" className="!p-0">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-700/40">
                <Brain className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-semibold text-blue-300">AGENTS</span>
              </div>

              {sidebarOpen.agents && (
                <div className="p-3 space-y-2 text-xs">
                  <div className="flex items-center gap-2 p-2 rounded hover:bg-white/5 cursor-pointer transition-colors">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span className="text-slate-300">Franklin Master</span>
                  </div>
                  <div className="flex items-center gap-2 p-2 rounded hover:bg-white/5 cursor-pointer transition-colors">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full" />
                    <span className="text-slate-400">Grok Healer</span>
                  </div>
                  <div className="flex items-center gap-2 p-2 rounded hover:bg-white/5 cursor-pointer transition-colors">
                    <div className="w-2 h-2 bg-blue-500 rounded-full" />
                    <span className="text-slate-400">Genesis Architect</span>
                  </div>
                </div>
              )}
            </GlassPanel>

            {/* LLM Models */}
            <GlassPanel variant="purple" rounded="md" className="!p-0">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-700/40">
                <Zap className="w-4 h-4 text-purple-400" />
                <span className="text-xs font-semibold text-purple-300">LLM MODELS</span>
              </div>

              {sidebarOpen.llms && (
                <div className="p-3 space-y-2 text-xs">
                  <div className="flex items-center justify-between p-2 rounded bg-blue-500/10 border border-blue-500/30 cursor-pointer hover:bg-blue-500/15 transition-colors">
                    <span className="text-blue-300 font-mono">Claude 3.5</span>
                    <span className="text-slate-500 text-xs">Sonnet</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded hover:bg-white/5 cursor-pointer transition-colors text-slate-400">
                    <span className="font-mono">GPT-4o</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded hover:bg-white/5 cursor-pointer transition-colors text-slate-400">
                    <span className="font-mono">Grok 3</span>
                  </div>
                </div>
              )}
            </GlassPanel>

            {/* Tools */}
            <GlassPanel variant="cyan" rounded="md" className="!p-0 flex-1">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-700/40">
                <Shield className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-semibold text-cyan-300">TOOLS</span>
              </div>

              {sidebarOpen.tools && (
                <div className="p-3 space-y-2 text-xs overflow-y-auto flex-1">
                  <button className="w-full flex items-center gap-2 p-2 rounded hover:bg-white/5 transition-colors text-slate-400 hover:text-slate-300">
                    <FileCode className="w-3 h-3" />
                    File Explorer
                  </button>
                  <button className="w-full flex items-center gap-2 p-2 rounded hover:bg-white/5 transition-colors text-slate-400 hover:text-slate-300">
                    <Terminal className="w-3 h-3" />
                    Terminal
                  </button>
                  <button className="w-full flex items-center gap-2 p-2 rounded hover:bg-white/5 transition-colors text-slate-400 hover:text-slate-300">
                    <Code2 className="w-3 h-3" />
                    Code Gen
                  </button>
                </div>
              )}
            </GlassPanel>
          </div>
        </Panel>

        <PanelResizeHandle className="!w-1 hover:bg-blue-500/30 transition-colors" />

        {/* ============================================================ */}
        {/* CENTER & BOTTOM (VERTICAL SPLIT)                           */}
        {/* ============================================================ */}
        <PanelGroup direction="vertical">
          {/* Editor Pane */}
          <Panel minSize={40} defaultSize={70}>
            <div className="h-full flex flex-col overflow-hidden p-3 gap-3">
              <GlassPanel variant="blue" title="CODE EDITOR" rounded="md" className="flex-1 !p-0 flex flex-col">
                {/* Tab Bar */}
                <div className="flex items-center gap-1 px-3 py-2 border-b border-slate-700/40 overflow-x-auto">
                  {/* Preview Tab */}
                  <button
                    onClick={() => setActivePreviewTab('preview')}
                    className={`
                      px-3 py-1 rounded text-xs font-mono whitespace-nowrap
                      flex items-center gap-2 transition-all
                      ${activePreviewTab === 'preview'
                        ? 'bg-cyan-500/20 border border-cyan-500/40 text-cyan-300'
                        : 'text-slate-400 hover:bg-white/5'
                      }
                    `}
                    <Eye className="w-3 h-3" />
                    Preview
                    👁️ Preview
                  </button>

                  {/* Code Tabs */}
                  {openFiles.map((file, idx) => (
                    <button
                      key={file.id}
                      onClick={() => { setActiveTab(file.id); setActivePreviewTab('code'); }}
                      className={`
                        px-3 py-1 rounded text-xs font-mono whitespace-nowrap
                        flex items-center gap-2 transition-all
                        ${activeTab === file.id && activePreviewTab === 'code'
                          ? 'bg-blue-500/20 border border-blue-500/40 text-blue-300'
                          : 'text-slate-400 hover:bg-white/5'
                        }
                      `}
                    >
                      <Code2 className="w-3 h-3" />
                      {file.name}
                      {idx === 0 && <span className="text-xs text-slate-600">•</span>}
                    </button>
                  ))}
                  <button className="px-2 py-1 text-slate-500 hover:text-slate-300 transition-colors">
                    <Plus className="w-3 h-3" />
                  </button>
                  <button className="px-2 py-1 text-slate-500 hover:text-slate-300 transition-colors">
                    <Plus className="w-3 h-3" />
                  </button>
                </div>

                {/* Editor Content */}
                <div className="flex-1 overflow-auto">
                  {activePreviewTab === 'preview' ? (
                    <PreviewPortal
                      buildResult={buildResult}
                      generatedCode={generatedCode}
                      activePreviewTab={activePreviewTab}
                      onTabChange={setActivePreviewTab}
                    />
                  ) : (
                    <pre className="p-4 font-mono text-sm text-slate-300 whitespace-pre-wrap">
                      {openFiles.find(f => f.id === activeTab)?.content}
                    </pre>
                  )}
                </div>
              </GlassPanel>
            </div>
          </Panel>

          <PanelResizeHandle className="!h-1 hover:bg-blue-500/30 transition-colors" />

          {/* Bottom Panel - Terminals & Output */}
          <Panel minSize={20} maxSize={50} defaultSize={30}>
            <div className="h-full flex flex-col overflow-hidden p-3 gap-3">
              <GlassPanel variant="cyan" title="TERMINALS" rounded="md" className="flex-1 !p-0 flex flex-col">
                {/* Terminal Tabs */}
                <div className="flex items-center gap-1 px-3 py-2 border-b border-slate-700/40">
                  {['local', 'cloud', 'mcp', 'output'].map((term) => (
                    <button
                      key={term}
                      onClick={() => setActiveTerminal(term)}
                      className={`
                        px-3 py-1 rounded text-xs font-mono whitespace-nowrap
                        flex items-center gap-2 transition-all
                        ${activeTerminal === term
                          ? 'bg-cyan-500/20 border border-cyan-500/40 text-cyan-300'
                          : 'text-slate-400 hover:bg-white/5'
                        }
                      `}
                    >
                      <Terminal className="w-3 h-3" />
                      {term.charAt(0).toUpperCase() + term.slice(1)}
                    </button>
                  ))}
                </div>

                {/* Terminal Output */}
                <div className="flex-1 overflow-auto bg-slate-950/50 p-4 font-mono text-xs text-slate-400">
                  {activeTerminal === 'local' && (
                    <div>
                      <div className="text-cyan-400">➜ franklin-os</div>
                      <div className="text-slate-600">~ $ </div>
                    </div>
                  )}
                  {activeTerminal === 'cloud' && (
                    <div>
                      <div className="text-purple-400">AWS Lambda</div>
                      <div className="text-slate-600 mt-2">Connected. Ready for deployment.</div>
                    </div>
                  )}
                  {activeTerminal === 'mcp' && (
                    <div>
                      <div className="text-green-400">MCP Servers Active: 3</div>
                      <div className="text-slate-600 mt-2">• Filesystem</div>
                      <div className="text-slate-600">• Database</div>
                      <div className="text-slate-600">• Terminal</div>
                    </div>
                  )}
                  {activeTerminal === 'output' && (
                    <div>
                      <div className="text-blue-400">[Build Output]</div>
                      <div className="text-slate-600 mt-2">✓ Files generated</div>
                      <div className="text-slate-600">✓ Tests passed</div>
                      <div className="text-slate-600">✓ Ready for certification</div>
                    </div>
                  )}
                </div>
              </GlassPanel>
            </div>
          </Panel>
        </PanelGroup>

        <PanelResizeHandle className="!w-1 hover:bg-blue-500/30 transition-colors" />

        {/* ============================================================ */}
        {/* RIGHT PANEL - INSPECTOR                                     */}
        {/* ============================================================ */}
        <Panel minSize={15} maxSize={25} defaultSize={18}>
          <div className="h-full flex flex-col overflow-hidden p-3 gap-3">
            <GlassPanel variant="blue" rounded="md" className="!p-0">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-700/40">
                <Settings className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-semibold text-blue-300">INSPECTOR</span>
              </div>

              <div className="p-3 space-y-3 text-xs overflow-y-auto">
                <ContextWindow
                  type="status"
                  title="Build Status"
                  badge={{ text: 'Ready', color: 'bg-green-500/20 text-green-300' }}
                  defaultOpen={true}
                >
                  <div className="p-3 space-y-2 text-slate-400">
                    <div className="flex justify-between">
                      <span>Files:</span>
                      <span className="text-green-300">12</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Size:</span>
                      <span className="text-blue-300">2.4 MB</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Status:</span>
                      <span className="text-cyan-300">Compiled</span>
                    </div>
                  </div>
                </ContextWindow>

                <ContextWindow
                  type="info"
                  title="Quality Gates"
                  badge={{ text: '8/8', color: 'bg-emerald-500/20 text-emerald-300' }}
                  defaultOpen={true}
                >
                  <div className="p-3 space-y-1 text-slate-400">
                    <div className="flex justify-between text-xs">
                      <span>Completeness</span>
                      <span className="text-green-400">✓</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span>Security</span>
                      <span className="text-green-400">✓</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span>Performance</span>
                      <span className="text-green-400">✓</span>
                    </div>
                  </div>
                </ContextWindow>
              </div>
            </GlassPanel>
          </div>
        </Panel>
      </PanelGroup>

      {/* Ghost Franklin - Floating Orchestrator */}
      <GhostFranklin
        isVisible={ghostFranklinVisible}
        onClose={() => setGhostFranklinVisible(false)}
        onMessage={(msg) => console.log('Franklin received:', msg)}
      />
    </div>
  );
};

export default FranklinIDE;
