import React, { useState } from 'react';
import { 
  Code, Download, Rocket, Settings, Check, AlertTriangle, 
  Loader2, FileCode, Database, Shield, TestTube, Sparkles,
  Copy, ExternalLink, Package
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TECH_STACKS = {
  frontend: [
    { id: 'nextjs', name: 'Next.js', icon: '▲' },
    { id: 'react', name: 'React', icon: '⚛' },
  ],
  backend: [
    { id: 'fastapi', name: 'FastAPI', icon: '⚡' },
    { id: 'express', name: 'Express.js', icon: '🟢' },
  ],
  database: [
    { id: 'postgresql', name: 'PostgreSQL', icon: '🐘' },
    { id: 'mongodb', name: 'MongoDB', icon: '🍃' },
    { id: 'supabase', name: 'Supabase', icon: '⚡' },
  ]
};

export const BuildPanel = ({ session, specification, onBuildComplete }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState('config'); // config, building, complete
  const [buildResult, setBuildResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Build configuration
  const [config, setConfig] = useState({
    projectName: 'MyProject',
    frontend: 'nextjs',
    backend: 'fastapi',
    database: 'postgresql',
    includeAuth: true,
    includeTests: true,
    includeCrud: true,
  });

  const handleBuild = async () => {
    // Build works with or without specification - uses defaults if needed
    setIsLoading(true);
    setError(null);
    setStep('building');

    try {
      const projectId = `project-${Date.now()}`;
      
      // Use enhanced build endpoint
      const response = await axios.post(`${API}/build/enhanced`, {
        project_id: projectId,
        project_name: config.projectName,
        specification: specification || {
          name: config.projectName,
          data_model: session?.analysis?.data_model || {
            entities: [
              { name: 'Item', attributes: [{ name: 'name', type: 'string' }] }
            ]
          },
          api_contracts: session?.analysis?.api_contracts || []
        },
        tech_stack: {
          frontend_framework: config.frontend,
          backend_framework: config.backend,
          database: config.database,
          css_framework: 'tailwindcss',
          ci_cd: 'github_actions'
        },
        include_auth: config.includeAuth,
        include_tests: config.includeTests,
        include_crud: config.includeCrud
      });

      setBuildResult({
        ...response.data,
        project_id: projectId
      });
      setStep('complete');
      
      if (onBuildComplete) {
        onBuildComplete(response.data);
      }

    } catch (err) {
      setError(err.response?.data?.detail || 'Build failed');
      setStep('config');
    } finally {
      setIsLoading(false);
    }
  };

  const handleWriteToDisk = async () => {
    if (!buildResult?.project_id) return;
    
    setIsLoading(true);
    try {
      await axios.post(`${API}/build/write`, {
        project_id: buildResult.project_id,
        output_directory: '/app/generated'
      });
      setBuildResult(prev => ({ ...prev, written: true }));
    } catch (err) {
      setError('Failed to write files');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadZip = () => {
    if (!buildResult?.project_id) return;
    window.open(`${API}/build/download/${buildResult.project_id}`, '_blank');
  };

  if (!isOpen) {
    return (
      <button
        data-testid="build-panel-toggle"
        onClick={() => setIsOpen(true)}
        className="fixed bottom-24 right-6 flex items-center gap-2 px-4 py-3 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-mono text-sm shadow-lg hover:shadow-xl transition-all hover:scale-105 z-40"
      >
        <Code size={18} />
        <span>Build Project</span>
        <Sparkles size={14} className="text-yellow-300" />
      </button>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4" data-testid="build-panel">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Code size={20} className="text-white" />
            </div>
            <div>
              <h2 className="font-mono font-bold text-zinc-100">Build Engine</h2>
              <p className="text-xs text-zinc-500">Generate production-ready code</p>
            </div>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-4 overflow-y-auto flex-1">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center gap-2 text-red-400 text-sm">
              <AlertTriangle size={16} />
              {error}
            </div>
          )}

          {step === 'config' && (
            <div className="space-y-6">
              {/* Project Name */}
              <div>
                <label className="block text-xs font-mono text-zinc-400 mb-2">PROJECT NAME</label>
                <input
                  data-testid="project-name-input"
                  type="text"
                  value={config.projectName}
                  onChange={(e) => setConfig(prev => ({ ...prev, projectName: e.target.value }))}
                  className="w-full px-3 py-2 rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:border-indigo-500 focus:outline-none"
                  placeholder="MyProject"
                />
              </div>

              {/* Tech Stack Selection */}
              <div className="grid grid-cols-3 gap-4">
                {/* Frontend */}
                <div>
                  <label className="block text-xs font-mono text-zinc-400 mb-2">FRONTEND</label>
                  <div className="space-y-2">
                    {TECH_STACKS.frontend.map(tech => (
                      <button
                        key={tech.id}
                        onClick={() => setConfig(prev => ({ ...prev, frontend: tech.id }))}
                        className={`w-full px-3 py-2 rounded-lg border text-left text-sm font-mono transition-colors ${
                          config.frontend === tech.id
                            ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-300'
                            : 'bg-zinc-800 border-zinc-700 text-zinc-400 hover:border-zinc-600'
                        }`}
                      >
                        <span className="mr-2">{tech.icon}</span>
                        {tech.name}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Backend */}
                <div>
                  <label className="block text-xs font-mono text-zinc-400 mb-2">BACKEND</label>
                  <div className="space-y-2">
                    {TECH_STACKS.backend.map(tech => (
                      <button
                        key={tech.id}
                        onClick={() => setConfig(prev => ({ ...prev, backend: tech.id }))}
                        className={`w-full px-3 py-2 rounded-lg border text-left text-sm font-mono transition-colors ${
                          config.backend === tech.id
                            ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
                            : 'bg-zinc-800 border-zinc-700 text-zinc-400 hover:border-zinc-600'
                        }`}
                      >
                        <span className="mr-2">{tech.icon}</span>
                        {tech.name}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Database */}
                <div>
                  <label className="block text-xs font-mono text-zinc-400 mb-2">DATABASE</label>
                  <div className="space-y-2">
                    {TECH_STACKS.database.map(tech => (
                      <button
                        key={tech.id}
                        onClick={() => setConfig(prev => ({ ...prev, database: tech.id }))}
                        className={`w-full px-3 py-2 rounded-lg border text-left text-sm font-mono transition-colors ${
                          config.database === tech.id
                            ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
                            : 'bg-zinc-800 border-zinc-700 text-zinc-400 hover:border-zinc-600'
                        }`}
                      >
                        <span className="mr-2">{tech.icon}</span>
                        {tech.name}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Features */}
              <div>
                <label className="block text-xs font-mono text-zinc-400 mb-2">FEATURES</label>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => setConfig(prev => ({ ...prev, includeAuth: !prev.includeAuth }))}
                    className={`px-3 py-2 rounded-lg border text-sm font-mono flex items-center gap-2 transition-colors ${
                      config.includeAuth
                        ? 'bg-purple-500/20 border-purple-500/50 text-purple-300'
                        : 'bg-zinc-800 border-zinc-700 text-zinc-500'
                    }`}
                  >
                    <Shield size={14} />
                    Auth
                    {config.includeAuth && <Check size={12} />}
                  </button>
                  <button
                    onClick={() => setConfig(prev => ({ ...prev, includeTests: !prev.includeTests }))}
                    className={`px-3 py-2 rounded-lg border text-sm font-mono flex items-center gap-2 transition-colors ${
                      config.includeTests
                        ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300'
                        : 'bg-zinc-800 border-zinc-700 text-zinc-500'
                    }`}
                  >
                    <TestTube size={14} />
                    Tests
                    {config.includeTests && <Check size={12} />}
                  </button>
                  <button
                    onClick={() => setConfig(prev => ({ ...prev, includeCrud: !prev.includeCrud }))}
                    className={`px-3 py-2 rounded-lg border text-sm font-mono flex items-center gap-2 transition-colors ${
                      config.includeCrud
                        ? 'bg-green-500/20 border-green-500/50 text-green-300'
                        : 'bg-zinc-800 border-zinc-700 text-zinc-500'
                    }`}
                  >
                    <Database size={14} />
                    CRUD
                    {config.includeCrud && <Check size={12} />}
                  </button>
                </div>
              </div>
            </div>
          )}

          {step === 'building' && (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 size={48} className="text-indigo-400 animate-spin mb-4" />
              <p className="text-zinc-300 font-mono">Generating code...</p>
              <p className="text-zinc-500 text-sm mt-2">Creating {config.projectName}</p>
            </div>
          )}

          {step === 'complete' && buildResult && (
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
                <div className="flex items-center gap-2 text-emerald-400 mb-2">
                  <Check size={20} />
                  <span className="font-mono font-bold">Build Complete!</span>
                </div>
                <p className="text-zinc-400 text-sm">
                  Generated {buildResult.total_artifacts} files for {buildResult.project_name}
                </p>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 rounded-lg bg-zinc-800 border border-zinc-700">
                  <FileCode size={16} className="text-indigo-400 mb-1" />
                  <p className="text-2xl font-mono font-bold text-zinc-100">{buildResult.total_artifacts}</p>
                  <p className="text-xs text-zinc-500">Files</p>
                </div>
                <div className="p-3 rounded-lg bg-zinc-800 border border-zinc-700">
                  <Package size={16} className="text-emerald-400 mb-1" />
                  <p className="text-2xl font-mono font-bold text-zinc-100">
                    {Object.keys(buildResult.artifacts_by_type || {}).length}
                  </p>
                  <p className="text-xs text-zinc-500">Languages</p>
                </div>
                <div className="p-3 rounded-lg bg-zinc-800 border border-zinc-700">
                  <Shield size={16} className="text-purple-400 mb-1" />
                  <p className="text-2xl font-mono font-bold text-zinc-100">
                    {Object.values(buildResult.features || {}).filter(Boolean).length}
                  </p>
                  <p className="text-xs text-zinc-500">Features</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  data-testid="write-to-disk-btn"
                  onClick={handleWriteToDisk}
                  disabled={isLoading || buildResult.written}
                  className={`flex-1 px-4 py-3 rounded-lg font-mono text-sm flex items-center justify-center gap-2 transition-colors ${
                    buildResult.written
                      ? 'bg-emerald-500/20 border border-emerald-500/30 text-emerald-400'
                      : 'bg-indigo-600 hover:bg-indigo-500 text-white'
                  }`}
                >
                  {buildResult.written ? (
                    <>
                      <Check size={16} />
                      Written to Disk
                    </>
                  ) : (
                    <>
                      <Rocket size={16} />
                      Write to Disk
                    </>
                  )}
                </button>
                <button
                  data-testid="download-zip-btn"
                  onClick={handleDownloadZip}
                  className="px-4 py-3 rounded-lg bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-300 font-mono text-sm flex items-center gap-2 transition-colors"
                >
                  <Download size={16} />
                  Download ZIP
                </button>
              </div>

              {buildResult.written && (
                <div className="p-3 rounded-lg bg-zinc-800 border border-zinc-700">
                  <p className="text-xs text-zinc-500 mb-1">Files written to:</p>
                  <code className="text-indigo-400 text-sm font-mono">/app/generated/{buildResult.project_name}/</code>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-zinc-800 flex justify-between">
          {step === 'config' && (
            <>
              <button
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-400 font-mono text-sm transition-colors"
              >
                Cancel
              </button>
              <button
                data-testid="start-build-btn"
                onClick={handleBuild}
                disabled={isLoading || !config.projectName}
                className="px-6 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-mono text-sm flex items-center gap-2 transition-colors disabled:opacity-50"
              >
                <Rocket size={16} />
                Generate Project
              </button>
            </>
          )}
          {step === 'complete' && (
            <button
              onClick={() => {
                setStep('config');
                setBuildResult(null);
              }}
              className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-400 font-mono text-sm transition-colors"
            >
              Build Another
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default BuildPanel;
