import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useProject } from '../context/ProjectContext';

const API = process.env.REACT_APP_BACKEND_URL || '';

const AGENT_TIERS = [
  {
    name: 'Tier 1 - Associate Agent',
    autonomy: 'low',
    range: '$0 - $2,500',
    description: 'Entry delivery with strict human review and consensus.',
    tasks: ['data_capture', 'summarization', 'checklists']
  },
  {
    name: 'Tier 2 - Specialist Agent',
    autonomy: 'medium',
    range: '$2,500 - $20,000',
    description: 'Domain specialist with evidence-backed delivery.',
    tasks: ['domain_analysis', 'audit_support', 'risk_screening']
  },
  {
    name: 'Tier 3 - Principal Agent',
    autonomy: 'high',
    range: '$20,000 - $300,000',
    description: 'Principal delivery with governance spot checks.',
    tasks: ['lead_audit', 'governance_review', 'portfolio_signoff']
  },
  {
    name: 'Elite Scalar - Sovereign Agent',
    autonomy: 'sovereign',
    range: '$300,000 - $10,000,000',
    description: 'Board-level approval and sovereign autonomy.',
    tasks: ['enterprise_deployment', 'capital_structuring', 'sovereign_audit']
  }
];

const BOT_TASK_TIERS = [
  {
    name: 'Tier 1 - Scout Bot',
    autonomy: 'low',
    scope: 'Discovery & signals',
    sources: 'Public bid portals, auctions, open feeds',
    controls: 'Respect robots.txt, rate limit, no credentialed access, PII redaction'
  },
  {
    name: 'Tier 2 - Qualifier Bot',
    autonomy: 'medium',
    scope: 'Lead scoring & routing',
    sources: 'Public + partner feeds',
    controls: 'Rate limit, consent required, PII redaction'
  },
  {
    name: 'Tier 3 - Pipeline Bot',
    autonomy: 'high',
    scope: 'Bid packaging & compliance',
    sources: 'Partner feeds, internal CRM',
    controls: 'Human approval, audit logging, PII redaction'
  },
  {
    name: 'Elite Scalar - Market Orchestrator Bot',
    autonomy: 'sovereign',
    scope: 'Market orchestration',
    sources: 'Approved partner feeds, internal marketplace',
    controls: 'Board approval, audit logging, rate limit'
  }
];

const AgentBotCockpit = ({ onBack }) => {
  const { project } = useProject();
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [task, setTask] = useState('');
  const [target, setTarget] = useState('railway');
  const [status, setStatus] = useState('');

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await axios.get(`${API}/api/lithium/agents/catalog`);
        setAgents(res.data?.agents || []);
        if (project?.agent_id) {
          const preset = (res.data?.agents || []).find(a => a.id === project.agent_id);
          if (preset) setSelectedAgent(preset);
        }
      } catch (e) {
        setStatus(`Failed to load agents: ${e.message}`);
      }
    };
    fetchAgents();
  }, []);

  const deployAgent = async () => {
    if (!selectedAgent) {
      setStatus('Select an agent first.');
      return;
    }
    try {
      const res = await axios.post(`${API}/api/lithium/agents/deploy`, {
        agent_id: selectedAgent.id,
        task: task || 'Run assigned mission',
        target,
        project_id: project?.project_id
      });
      setStatus(`Deployment scheduled (${res.data.deploy_id})`);
    } catch (e) {
      setStatus(`Deploy failed: ${e.response?.data?.detail || e.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="h-12 border-b border-white/20 flex items-center px-4">
        <button onClick={onBack} className="mr-3 text-sm font-mono text-cyan-400 hover:text-cyan-200">← Back</button>
        <span className="text-base font-mono text-white">Agent & Bot Deployment</span>
        <div className="flex-1" />
        {project && <span className="text-xs font-mono text-white/60">Project: {project.project_id}</span>}
      </div>
      <div className="p-6 space-y-4">
        <div className="border border-white/15 rounded bg-white/5 p-4">
          <h3 className="text-sm font-mono text-cyan-300 mb-2">Franklin ↔ Grok Handshake</h3>
          <p className="text-sm text-white/70">
            Franklin gathers intent, hands off to Grok, and Grok returns refined code and deployment steps.
          </p>
        </div>

        <div className="border border-white/15 rounded bg-white/5 p-4">
          <h3 className="text-sm font-mono text-green-300 mb-3">Certified Agents</h3>
          <div className="grid md:grid-cols-2 gap-3">
            {agents.map(agent => (
              <button
                key={agent.id}
                onClick={() => setSelectedAgent(agent)}
                className={`text-left p-3 rounded border ${selectedAgent?.id === agent.id ? 'border-cyan-400 bg-cyan-500/10' : 'border-white/10 bg-white/5'} hover:border-cyan-300 transition-all`}
              >
                <div className="text-sm font-mono text-white">{agent.name}</div>
                <div className="text-xs text-white/60">{agent.specialty}</div>
                <div className="text-[11px] text-green-300 mt-1">{agent.badge}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="border border-white/15 rounded bg-white/5 p-4 space-y-3">
          <h3 className="text-sm font-mono text-amber-300">Deployment Console</h3>
          <div className="flex flex-col gap-2">
            <label className="text-xs text-white/60">Task</label>
            <input
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="e.g., Harden API and deploy to staging"
              className="bg-black/40 border border-white/15 rounded px-3 py-2 text-sm text-white focus:outline-none"
            />
            <label className="text-xs text-white/60">Target</label>
            <select
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              className="bg-black/40 border border-white/15 rounded px-3 py-2 text-sm text-white focus:outline-none"
            >
              <option value="railway">Railway</option>
              <option value="vercel">Vercel</option>
              <option value="k8s">Kubernetes</option>
              <option value="vm">VM</option>
            </select>
            <button
              onClick={deployAgent}
              className="mt-2 px-4 py-2 text-sm font-mono text-white bg-cyan-600 rounded hover:bg-cyan-500 transition-all"
            >
              Deploy Selected Agent
            </button>
            {status && <div className="text-xs text-white/70">{status}</div>}
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-4">
          <div className="border border-white/15 rounded bg-white/5 p-4 space-y-2">
            <h3 className="text-sm font-mono text-cyan-200">Agent Tiers</h3>
            {AGENT_TIERS.map(tier => (
              <div key={tier.name} className="border border-white/10 rounded p-3 bg-black/30">
                <div className="text-sm font-mono text-white">{tier.name}</div>
                <div className="text-xs text-white/60">{tier.description}</div>
                <div className="text-[11px] text-white/50 mt-1">Autonomy: {tier.autonomy} • Range: {tier.range}</div>
                <div className="text-[11px] text-green-300 mt-1">Tasks: {tier.tasks.join(', ')}</div>
                <button
                  onClick={() => setTask(`Tier preset: ${tier.tasks[0]}`)}
                  className="mt-2 text-[11px] px-2 py-1 border border-cyan-400/50 text-cyan-200 rounded hover:bg-cyan-500/15"
                >
                  Use preset
                </button>
              </div>
            ))}
          </div>
          <div className="border border-white/15 rounded bg-white/5 p-4 space-y-2">
            <h3 className="text-sm font-mono text-amber-200">Bot Task Tiers</h3>
            {BOT_TASK_TIERS.map(tier => (
              <div key={tier.name} className="border border-white/10 rounded p-3 bg-black/30">
                <div className="text-sm font-mono text-white">{tier.name}</div>
                <div className="text-xs text-white/60">{tier.scope}</div>
                <div className="text-[11px] text-white/50 mt-1">Sources: {tier.sources}</div>
                <div className="text-[11px] text-green-300 mt-1">Controls: {tier.controls}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentBotCockpit;
