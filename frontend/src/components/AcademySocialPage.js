import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useProject } from '../context/ProjectContext';

const API = process.env.REACT_APP_BACKEND_URL || '';

const AcademySocialPage = ({ onBack }) => {
  const { project } = useProject();
  const [agents, setAgents] = useState([]);
  const [modules, setModules] = useState([]);
  const [badges, setBadges] = useState([]);

  useEffect(() => {
    const fetchBadges = async () => {
      try {
        const res = await axios.get(`${API}/api/lithium/academy/agents`);
        setAgents(res.data?.certified_agents || []);
      } catch {
        setAgents([]);
      }
      try {
        const resMods = await axios.get(`${API}/api/lithium/academy/modules`);
        setModules(resMods.data?.modules || []);
      } catch {
        setModules([]);
      }
      try {
        const resBadges = await axios.get(`${API}/api/lithium/academy/badges`);
        setBadges(resBadges.data?.badges || []);
      } catch {
        setBadges([]);
      }
    };
    fetchBadges();
  }, []);

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="h-12 border-b border-white/20 flex items-center px-4">
        <button onClick={onBack} className="mr-3 text-sm font-mono text-cyan-400 hover:text-cyan-200">← Back</button>
        <span className="text-base font-mono text-white">AI Academy</span>
        <div className="flex-1" />
        {project && <span className="text-xs font-mono text-white/60">Project: {project.project_id}</span>}
      </div>
      <div className="p-6 space-y-4">
        <div className="border border-white/15 rounded bg-white/5 p-4">
          <h3 className="text-sm font-mono text-amber-300 mb-2">Certified Agents & Badges</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
            {agents.map(agent => (
              <div key={agent.id} className="border border-white/10 rounded p-3 bg-white/5">
                <div className="text-sm font-mono text-white">{agent.name}</div>
                <div className="text-xs text-white/60">{agent.specialty}</div>
                <div className="text-[11px] text-green-300 mt-1">{agent.badge}</div>
              </div>
            ))}
            {agents.length === 0 && <div className="text-sm text-white/60">No badges loaded yet.</div>}
          </div>
        </div>
        <div className="border border-white/15 rounded bg-white/5 p-4">
          <h3 className="text-sm font-mono text-green-300 mb-2">Certifications</h3>
          <p className="text-sm text-white/70">Franklin certifications appear here once stages are complete.</p>
          <div className="grid md:grid-cols-2 gap-3 mt-3">
            {modules.map(m => (
              <div key={m.id} className="border border-white/10 rounded p-3 bg-black/30">
                <div className="text-sm font-mono text-white">{m.title}</div>
                <div className="text-xs text-white/60">{m.summary}</div>
                <div className="text-[11px] text-amber-300 mt-1">Level: {m.level} • Status: {m.status}</div>
              </div>
            ))}
          </div>
          <div className="grid md:grid-cols-2 gap-3 mt-3">
            {badges.map(b => (
              <div key={b.id} className="border border-white/10 rounded p-3 bg-black/30">
                <div className="text-sm font-mono text-white">{b.name}</div>
                <div className="text-xs text-white/60">{b.domain_name}</div>
                <div className="text-[11px] text-green-300 mt-1">Level: {b.level}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AcademySocialPage;
