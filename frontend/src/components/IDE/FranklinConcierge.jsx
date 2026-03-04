/**
 * FranklinConcierge
 *
 * The adaptive intake + real-time build monitor.
 * No user left behind. No build left unfinished.
 *
 * Modes:
 *   SILENT   — "just build it" — zero friction
 *   BALANCED — default — confirm key decisions only
 *   VERBOSE  — "show me everything" — full transparency
 *
 * Flow:
 *   Prompt → Questions? → Contract → Confirm → Build Stream → Files → Deploy
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Zap, Brain, CheckCircle2, AlertCircle, Loader2, ChevronRight,
  Terminal, FileCode2, Shield, Rocket, Download, Copy,
  Eye, EyeOff, Volume2, VolumeX, Check, X, RefreshCw,
  ChevronDown, ChevronUp, Lock, Unlock, Hash
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// ─────────────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────────────

const MODES = {
  silent:   { label: 'Silent',   icon: VolumeX,  color: '#8b5cf6', desc: 'Zero questions — build immediately' },
  balanced: { label: 'Balanced', icon: Brain,     color: '#06b6d4', desc: 'Ask only critical questions (default)' },
  verbose:  { label: 'Verbose',  icon: Eye,       color: '#10b981', desc: 'Surface every decision for your approval' },
};

const STAGE_LABELS = {
  intake:        { label: 'Intake',         icon: Brain },
  specification: { label: 'Specification',  icon: FileCode2 },
  architecture:  { label: 'Architecture',   icon: Terminal },
  construction:  { label: 'Construction',   icon: Zap },
  validation:    { label: 'Certification',  icon: Shield },
  governance:    { label: 'Governance',     icon: Lock },
  deployment:    { label: 'Deployment',     icon: Rocket },
  complete:      { label: 'Complete',       icon: CheckCircle2 },
  heal:          { label: 'Healing',        icon: RefreshCw },
  error:         { label: 'Error',          icon: AlertCircle },
};

const PLACEHOLDER_PROMPTS = [
  "Build me a SaaS platform for managing construction bids with Stripe billing...",
  "Create a React dashboard that shows real-time AI agent activity...",
  "I need an API that connects Supabase to a React frontend with auth...",
  "Build a job board with company profiles, applications, and email notifications...",
  "Make an ecommerce store for digital products with Stripe and download delivery...",
];

// ─────────────────────────────────────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────────────────────────────────────

export default function FranklinConcierge({ onBuildComplete }) {
  const [mode, setMode]               = useState('balanced');
  const [input, setInput]             = useState('');
  const [phase, setPhase]             = useState('idle');
  // idle → questioning → confirming → building → complete → failed
  const [session, setSession]         = useState(null);
  const [messages, setMessages]       = useState([]);
  const [currentQuestion, setQuestion] = useState(null);
  const [contract, setContract]       = useState(null);
  const [buildEvents, setBuildEvents] = useState([]);
  const [progress, setProgress]       = useState(0);
  const [buildResult, setBuildResult] = useState(null);
  const [error, setError]             = useState(null);
  const [loading, setLoading]         = useState(false);
  const [placeholder]                 = useState(PLACEHOLDER_PROMPTS[Math.floor(Math.random() * PLACEHOLDER_PROMPTS.length)]);
  const [contractExpanded, setContractExpanded] = useState(true);
  const [eventsExpanded, setEventsExpanded]     = useState(true);

  const messagesEndRef = useRef(null);
  const eventSourceRef = useRef(null);
  const inputRef       = useRef(null);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, buildEvents]);

  // Cleanup SSE on unmount
  useEffect(() => () => eventSourceRef.current?.close(), []);

  // ─── HELPERS ──────────────────────────────────────────────────────────────

  const pushMessage = useCallback((role, content, type = 'text') => {
    setMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
      role, content, type,
      ts: new Date().toLocaleTimeString(),
    }]);
  }, []);

  const pushBuildEvent = useCallback((event) => {
    setBuildEvents(prev => [...prev, { ...event, id: Date.now() + Math.random() }]);
    if (event.progress != null) setProgress(event.progress);
  }, []);

  // ─── SUBMIT INITIAL PROMPT ────────────────────────────────────────────────

  const handleSubmit = async () => {
    if (!input.trim() || loading) return;
    const prompt = input.trim();
    setInput('');
    setLoading(true);
    setError(null);
    pushMessage('user', prompt);
    pushMessage('franklin', '...', 'typing');

    try {
      const res = await fetch(`${API_BASE}/api/concierge/intake`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: prompt, user_mode: mode }),
      });
      const data = await res.json();
      setMessages(prev => prev.filter(m => m.type !== 'typing'));

      if (!res.ok) throw new Error(data.detail || 'Intake failed');

      setSession(data.session_id);
      handleIntakeResponse(data);
    } catch (err) {
      setMessages(prev => prev.filter(m => m.type !== 'typing'));
      setError(err.message);
      setPhase('idle');
      pushMessage('franklin', `I ran into an issue: ${err.message}. Please try again.`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleIntakeResponse = (data) => {
    if (data.action === 'question') {
      setPhase('questioning');
      setQuestion(data);
      pushMessage('franklin', data.preamble ? `${data.preamble}\n\n${data.question}` : data.question);
    } else if (data.action === 'contract_ready') {
      setPhase('confirming');
      setContract(data.contract);
      pushMessage('franklin', data.message || 'Here\'s the build contract. Confirm to start.');
    } else if (data.action === 'build_start') {
      setPhase('building');
      setContract(data.contract);
      pushMessage('franklin', data.message || 'Building...');
      subscribeToStream(data.session_id || session);
    }
  };

  // ─── ANSWER QUESTION ─────────────────────────────────────────────────────

  const handleAnswer = async (answer) => {
    if (!session || loading) return;
    setLoading(true);
    pushMessage('user', answer);
    pushMessage('franklin', '...', 'typing');

    try {
      const res = await fetch(`${API_BASE}/api/concierge/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: session, response: answer }),
      });
      const data = await res.json();
      setMessages(prev => prev.filter(m => m.type !== 'typing'));
      if (!res.ok) throw new Error(data.detail || 'Response failed');
      handleIntakeResponse(data);
    } catch (err) {
      setMessages(prev => prev.filter(m => m.type !== 'typing'));
      setError(err.message);
    } finally {
      setLoading(false);
      setQuestion(null);
    }
  };

  // ─── CONFIRM CONTRACT ────────────────────────────────────────────────────

  const handleConfirm = async () => {
    if (!session || loading) return;
    setLoading(true);
    pushMessage('user', 'Confirmed. Build it.');

    try {
      const res = await fetch(`${API_BASE}/api/concierge/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: session }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Confirm failed');
      setPhase('building');
      pushMessage('franklin', `Contract signed: ${data.contract_hash?.slice(0, 12)}... — pipeline starting.`);
      subscribeToStream(session);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    pushMessage('user', 'Let me make some changes.');
    const res = await fetch(`${API_BASE}/api/concierge/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: session, response: 'I want to make changes' }),
    });
    const data = await res.json();
    setMessages(prev => prev.filter(m => m.type !== 'typing'));
    handleIntakeResponse(data);
  };

  // ─── SSE STREAM ───────────────────────────────────────────────────────────

  const subscribeToStream = (sid) => {
    if (eventSourceRef.current) eventSourceRef.current.close();

    const es = new EventSource(`${API_BASE}/api/concierge/${sid}/stream`);
    eventSourceRef.current = es;

    es.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data);
        if (event.type === 'connected') return;

        pushBuildEvent(event);

        if (event.type === 'complete') {
          setPhase('complete');
          setBuildResult(event.data);
          pushMessage('franklin', `${event.data?.file_count || 0} files built. Certified. ${event.data?.deploy_url ? 'Deployed.' : 'Ready to deploy.'}`, 'success');
          if (onBuildComplete) onBuildComplete(event.data);
          es.close();
        } else if (event.type === 'fatal_error') {
          setPhase('failed');
          setError(event.message);
          pushMessage('franklin', event.message, 'error');
          es.close();
        } else if (event.type === 'error') {
          pushMessage('franklin', event.message, 'warning');
        }
      } catch (err) {
        console.error('SSE parse error', err);
      }
    };

    es.onerror = () => {
      if (phase === 'building') {
        pushMessage('franklin', 'Connection interrupted. Build may still be running in the background.', 'warning');
      }
      es.close();
    };
  };

  // ─── RESET ────────────────────────────────────────────────────────────────

  const handleReset = () => {
    eventSourceRef.current?.close();
    setPhase('idle'); setSession(null); setMessages([]);
    setQuestion(null); setContract(null); setBuildEvents([]);
    setProgress(0); setBuildResult(null); setError(null);
    setLoading(false);
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  // ─────────────────────────────────────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────────────────────────────────────

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', height: '100%',
      background: 'rgba(8, 12, 24, 0.95)', color: '#e8f0ff',
      fontFamily: "'Inter', system-ui, sans-serif", overflow: 'hidden',
    }}>

      {/* ── HEADER ── */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(99,102,241,0.2)', display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
        <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'linear-gradient(135deg, #6366f1, #06b6d4)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Brain size={16} color="white" />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 14, letterSpacing: '0.02em' }}>FRANKLIN</div>
          <div style={{ fontSize: 11, color: 'rgba(232,240,255,0.5)' }}>Your sovereign build concierge</div>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
          {Object.entries(MODES).map(([key, m]) => {
            const Icon = m.icon;
            const active = mode === key;
            return (
              <button key={key} onClick={() => setMode(key)} title={m.desc} style={{
                display: 'flex', alignItems: 'center', gap: 4, padding: '4px 8px',
                borderRadius: 6, border: `1px solid ${active ? m.color : 'rgba(255,255,255,0.1)'}`,
                background: active ? `${m.color}22` : 'transparent',
                color: active ? m.color : 'rgba(232,240,255,0.4)',
                cursor: 'pointer', fontSize: 11, fontWeight: active ? 600 : 400,
                transition: 'all 0.15s',
              }}>
                <Icon size={11} />
                {m.label}
              </button>
            );
          })}
          {phase !== 'idle' && (
            <button onClick={handleReset} title="New build" style={{
              padding: '4px 8px', borderRadius: 6, border: '1px solid rgba(255,255,255,0.1)',
              background: 'transparent', color: 'rgba(232,240,255,0.4)',
              cursor: 'pointer', fontSize: 11,
            }}>
              <RefreshCw size={11} />
            </button>
          )}
        </div>
      </div>

      {/* ── CONVERSATION ── */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 8 }}>

        {/* Welcome state */}
        {phase === 'idle' && messages.length === 0 && (
          <WelcomeCard mode={mode} />
        )}

        {/* Chat messages */}
        {messages.map(msg => (
          <ChatBubble key={msg.id} msg={msg} />
        ))}

        {/* Question options */}
        {phase === 'questioning' && currentQuestion && currentQuestion.options && (
          <QuestionOptions
            question={currentQuestion}
            onAnswer={handleAnswer}
            loading={loading}
          />
        )}

        {/* Build contract */}
        {phase === 'confirming' && contract && (
          <BuildContractCard
            contract={contract}
            expanded={contractExpanded}
            onToggle={() => setContractExpanded(e => !e)}
            onConfirm={handleConfirm}
            onReject={handleReject}
            loading={loading}
          />
        )}

        {/* Build progress */}
        {(phase === 'building' || phase === 'complete') && buildEvents.length > 0 && (
          <BuildMonitor
            events={buildEvents}
            progress={progress}
            phase={phase}
            expanded={eventsExpanded}
            onToggle={() => setEventsExpanded(e => !e)}
          />
        )}

        {/* Complete — show files */}
        {phase === 'complete' && buildResult && (
          <BuildResult result={buildResult} />
        )}

        {/* Error */}
        {error && phase === 'failed' && (
          <div style={{ padding: '10px 14px', borderRadius: 8, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#fca5a5', fontSize: 13 }}>
            <AlertCircle size={14} style={{ display: 'inline', marginRight: 6 }} />
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* ── INPUT ── */}
      {(phase === 'idle' || phase === 'questioning') && (
        <InputBar
          value={input}
          onChange={setInput}
          onSubmit={handleSubmit}
          loading={loading}
          placeholder={phase === 'idle' ? placeholder : 'Type your answer or choose above...'}
          disabled={phase === 'questioning' && currentQuestion?.options?.length > 0}
          inputRef={inputRef}
        />
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// SUB-COMPONENTS
// ─────────────────────────────────────────────────────────────────────────────

function WelcomeCard({ mode }) {
  const m = MODES[mode];
  return (
    <div style={{ padding: '20px', borderRadius: 12, background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.2)', textAlign: 'center', margin: 'auto 0' }}>
      <div style={{ fontSize: 28, marginBottom: 8 }}>⚡</div>
      <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 6 }}>Tell me what to build.</div>
      <div style={{ fontSize: 13, color: 'rgba(232,240,255,0.55)', lineHeight: 1.6, maxWidth: 380, margin: '0 auto' }}>
        Describe your idea — clear or vague. Franklin will clarify what matters, lock a build contract, and deliver working code, certified and deployed.
      </div>
      <div style={{ marginTop: 14, display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 12px', borderRadius: 20, background: `${m.color}18`, border: `1px solid ${m.color}44`, fontSize: 12, color: m.color }}>
        <m.icon size={12} />
        {m.label} mode — {m.desc}
      </div>
    </div>
  );
}

function ChatBubble({ msg }) {
  const isUser = msg.role === 'user';
  const isTyping = msg.type === 'typing';

  return (
    <div style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', gap: 8, alignItems: 'flex-start' }}>
      {!isUser && (
        <div style={{ width: 24, height: 24, borderRadius: '50%', background: 'linear-gradient(135deg, #6366f1, #06b6d4)', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: 2 }}>
          <Brain size={12} color="white" />
        </div>
      )}
      <div style={{
        maxWidth: '80%', padding: '8px 12px', borderRadius: isUser ? '12px 12px 4px 12px' : '12px 12px 12px 4px',
        background: isUser ? 'rgba(99,102,241,0.25)' : msg.type === 'error' ? 'rgba(239,68,68,0.12)' : msg.type === 'success' ? 'rgba(16,185,129,0.12)' : msg.type === 'warning' ? 'rgba(245,158,11,0.12)' : 'rgba(255,255,255,0.06)',
        border: `1px solid ${isUser ? 'rgba(99,102,241,0.3)' : msg.type === 'error' ? 'rgba(239,68,68,0.2)' : msg.type === 'success' ? 'rgba(16,185,129,0.2)' : 'rgba(255,255,255,0.08)'}`,
        fontSize: 13, lineHeight: 1.6, color: msg.type === 'error' ? '#fca5a5' : msg.type === 'success' ? '#6ee7b7' : '#e8f0ff',
        whiteSpace: 'pre-wrap', wordBreak: 'break-word',
      }}>
        {isTyping ? (
          <span style={{ display: 'inline-flex', gap: 3 }}>
            {[0,1,2].map(i => <span key={i} style={{ width: 4, height: 4, borderRadius: '50%', background: '#6366f1', animation: `pulse 1s ${i * 0.2}s infinite` }} />)}
          </span>
        ) : msg.content}
        <div style={{ fontSize: 10, color: 'rgba(232,240,255,0.3)', marginTop: 2 }}>{msg.ts}</div>
      </div>
    </div>
  );
}

function QuestionOptions({ question, onAnswer, loading }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, padding: '4px 0 4px 32px' }}>
      {question.options.map((opt, i) => (
        <button key={i} onClick={() => onAnswer(opt)} disabled={loading} style={{
          padding: '8px 14px', borderRadius: 8, border: '1px solid rgba(99,102,241,0.3)',
          background: 'rgba(99,102,241,0.08)', color: '#e8f0ff',
          cursor: loading ? 'not-allowed' : 'pointer', textAlign: 'left',
          fontSize: 13, transition: 'all 0.15s', opacity: loading ? 0.5 : 1,
        }}
          onMouseEnter={e => !loading && (e.target.style.background = 'rgba(99,102,241,0.2)')}
          onMouseLeave={e => !loading && (e.target.style.background = 'rgba(99,102,241,0.08)')}
        >
          <ChevronRight size={12} style={{ marginRight: 6, verticalAlign: 'middle' }} />
          {opt}
        </button>
      ))}
    </div>
  );
}

function BuildContractCard({ contract, expanded, onToggle, onConfirm, onReject, loading }) {
  const stackEntries = Object.entries(contract.tech_stack || {});
  return (
    <div style={{ borderRadius: 12, border: '1px solid rgba(6,182,212,0.3)', background: 'rgba(6,182,212,0.05)', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 8, borderBottom: expanded ? '1px solid rgba(6,182,212,0.15)' : 'none', cursor: 'pointer' }} onClick={onToggle}>
        <Lock size={14} color="#06b6d4" />
        <span style={{ fontWeight: 600, fontSize: 13, color: '#67e8f9' }}>Build Contract — {contract.project_name}</span>
        <span style={{ marginLeft: 'auto', color: 'rgba(232,240,255,0.4)' }}>{expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</span>
      </div>

      {expanded && (
        <div style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          {/* Mission */}
          <div>
            <div style={{ fontSize: 11, color: 'rgba(232,240,255,0.4)', marginBottom: 3 }}>MISSION</div>
            <div style={{ fontSize: 13, lineHeight: 1.5 }}>{contract.mission}</div>
          </div>

          {/* Stack */}
          {stackEntries.length > 0 && (
            <div>
              <div style={{ fontSize: 11, color: 'rgba(232,240,255,0.4)', marginBottom: 4 }}>TECH STACK</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                {stackEntries.map(([k, v]) => (
                  <span key={k} style={{ padding: '2px 8px', borderRadius: 20, background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.25)', fontSize: 11, color: '#a5b4fc' }}>
                    <span style={{ opacity: 0.6 }}>{k}: </span>{v}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Features */}
          {contract.features?.length > 0 && (
            <div>
              <div style={{ fontSize: 11, color: 'rgba(232,240,255,0.4)', marginBottom: 4 }}>FEATURES</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {contract.features.map((f, i) => (
                  <div key={i} style={{ fontSize: 12, display: 'flex', gap: 6, alignItems: 'flex-start' }}>
                    <Check size={11} color="#10b981" style={{ flexShrink: 0, marginTop: 2 }} />
                    <span>{f}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Timeline + Deploy */}
          <div style={{ display: 'flex', gap: 12 }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 11, color: 'rgba(232,240,255,0.4)', marginBottom: 2 }}>TIMELINE</div>
              <div style={{ fontSize: 12, color: '#fbbf24' }}>{contract.timeline_estimate}</div>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 11, color: 'rgba(232,240,255,0.4)', marginBottom: 2 }}>DEPLOY TO</div>
              <div style={{ fontSize: 12, color: '#34d399' }}>{contract.deployment_target}</div>
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
            <button onClick={onConfirm} disabled={loading} style={{
              flex: 1, padding: '10px', borderRadius: 8,
              background: 'linear-gradient(135deg, #6366f1, #06b6d4)', color: 'white',
              border: 'none', cursor: loading ? 'wait' : 'pointer', fontWeight: 700, fontSize: 13,
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              opacity: loading ? 0.7 : 1,
            }}>
              {loading ? <Loader2 size={14} className="spin" /> : <Rocket size={14} />}
              Confirm & Build
            </button>
            <button onClick={onReject} disabled={loading} style={{
              padding: '10px 14px', borderRadius: 8,
              background: 'transparent', color: 'rgba(232,240,255,0.5)',
              border: '1px solid rgba(255,255,255,0.1)', cursor: 'pointer', fontSize: 13,
            }}>
              <X size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function BuildMonitor({ events, progress, phase, expanded, onToggle }) {
  const STAGE_COLORS = {
    build: '#6366f1', cert: '#f59e0b', deploy: '#10b981',
    complete: '#06b6d4', error: '#ef4444', heal: '#f97316',
  };

  return (
    <div style={{ borderRadius: 12, border: '1px solid rgba(99,102,241,0.2)', background: 'rgba(99,102,241,0.04)', overflow: 'hidden' }}>
      {/* Progress bar */}
      <div style={{ height: 2, background: 'rgba(255,255,255,0.06)' }}>
        <div style={{
          height: '100%', width: `${progress}%`,
          background: phase === 'complete' ? 'linear-gradient(90deg, #10b981, #06b6d4)' : 'linear-gradient(90deg, #6366f1, #06b6d4)',
          transition: 'width 0.4s ease',
        }} />
      </div>

      {/* Header */}
      <div style={{ padding: '8px 12px', display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', borderBottom: expanded ? '1px solid rgba(99,102,241,0.1)' : 'none' }} onClick={onToggle}>
        {phase === 'building' ? <Loader2 size={13} color="#6366f1" className="spin" /> : <CheckCircle2 size={13} color="#10b981" />}
        <span style={{ fontSize: 12, fontWeight: 600, color: '#a5b4fc' }}>
          {phase === 'complete' ? 'Build Complete' : `Building — ${progress}%`}
        </span>
        <span style={{ marginLeft: 'auto', fontSize: 11, color: 'rgba(232,240,255,0.3)' }}>{events.length} events</span>
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </div>

      {expanded && (
        <div style={{ maxHeight: 220, overflowY: 'auto', padding: '6px 0' }}>
          {events.map(event => {
            const stageInfo = STAGE_LABELS[event.stage] || { label: event.stage, icon: Terminal };
            const color = STAGE_COLORS[event.type] || '#6366f1';
            return (
              <div key={event.id} style={{
                padding: '4px 12px', display: 'flex', alignItems: 'flex-start', gap: 8,
                borderBottom: '1px solid rgba(255,255,255,0.03)', fontSize: 12,
              }}>
                <div style={{ width: 6, height: 6, borderRadius: '50%', background: color, flexShrink: 0, marginTop: 4 }} />
                <div style={{ flex: 1, lineHeight: 1.4 }}>
                  <span style={{ color: `${color}cc`, fontSize: 10, fontWeight: 600 }}>{stageInfo.label.toUpperCase()} </span>
                  <span style={{ color: 'rgba(232,240,255,0.7)' }}>{event.message}</span>
                </div>
                {event.progress != null && (
                  <span style={{ fontSize: 10, color: 'rgba(232,240,255,0.3)', flexShrink: 0 }}>{event.progress}%</span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function BuildResult({ result }) {
  const [copied, setCopied] = useState(false);
  const files = result.files || [];

  const copyHash = () => {
    navigator.clipboard.writeText(result.audit_certificate || result.cert_hash || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ borderRadius: 12, border: '1px solid rgba(16,185,129,0.3)', background: 'rgba(16,185,129,0.05)', padding: '14px' }}>
      {/* Stats */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 12 }}>
        {[
          { label: 'Files', value: result.file_count || files.length },
          { label: 'Lines', value: result.total_lines || '—' },
          { label: 'Gates', value: '6/8' },
        ].map(stat => (
          <div key={stat.label} style={{ flex: 1, textAlign: 'center' }}>
            <div style={{ fontSize: 20, fontWeight: 700, color: '#34d399' }}>{stat.value}</div>
            <div style={{ fontSize: 10, color: 'rgba(232,240,255,0.4)' }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Cert hash */}
      {result.audit_certificate && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 10px', borderRadius: 6, background: 'rgba(0,0,0,0.3)', marginBottom: 10 }}>
          <Hash size={11} color="#34d399" />
          <span style={{ fontSize: 11, fontFamily: 'monospace', color: '#6ee7b7', flex: 1 }}>
            {result.audit_certificate.slice(0, 32)}...
          </span>
          <button onClick={copyHash} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(232,240,255,0.4)' }}>
            {copied ? <Check size={11} color="#34d399" /> : <Copy size={11} />}
          </button>
        </div>
      )}

      {/* Files */}
      {files.length > 0 && (
        <div style={{ marginBottom: 10 }}>
          <div style={{ fontSize: 11, color: 'rgba(232,240,255,0.4)', marginBottom: 4 }}>GENERATED FILES</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2, maxHeight: 120, overflowY: 'auto' }}>
            {files.slice(0, 20).map((f, i) => (
              <div key={i} style={{ fontSize: 11, fontFamily: 'monospace', color: '#a5b4fc', display: 'flex', alignItems: 'center', gap: 4 }}>
                <FileCode2 size={10} />
                {f.path || f}
                {f.line_count && <span style={{ color: 'rgba(232,240,255,0.3)', marginLeft: 'auto' }}>{f.line_count}L</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: 6 }}>
        {result.deploy_url && (
          <a href={result.deploy_url} target="_blank" rel="noreferrer" style={{
            flex: 1, padding: '8px', borderRadius: 8, textAlign: 'center',
            background: 'linear-gradient(135deg, #10b981, #06b6d4)', color: 'white',
            textDecoration: 'none', fontSize: 12, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
          }}>
            <Rocket size={12} /> Open Live App
          </a>
        )}
        <button style={{
          flex: result.deploy_url ? 0 : 1, padding: '8px 14px', borderRadius: 8,
          border: '1px solid rgba(16,185,129,0.3)', background: 'transparent', color: '#34d399',
          cursor: 'pointer', fontSize: 12, display: 'flex', alignItems: 'center', gap: 6,
        }}>
          <Download size={12} /> Download ZIP
        </button>
      </div>
    </div>
  );
}

function InputBar({ value, onChange, onSubmit, loading, placeholder, disabled, inputRef }) {
  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !disabled) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div style={{ padding: '10px 14px', borderTop: '1px solid rgba(99,102,241,0.15)', flexShrink: 0 }}>
      <div style={{
        display: 'flex', gap: 8, alignItems: 'flex-end',
        background: 'rgba(255,255,255,0.04)', borderRadius: 10,
        border: '1px solid rgba(99,102,241,0.2)', padding: '8px 10px',
      }}>
        <textarea
          ref={inputRef}
          value={value}
          onChange={e => onChange(e.target.value)}
          onKeyDown={handleKey}
          disabled={disabled || loading}
          placeholder={placeholder}
          rows={1}
          style={{
            flex: 1, background: 'transparent', border: 'none', outline: 'none',
            color: '#e8f0ff', fontSize: 13, lineHeight: 1.5, resize: 'none',
            fontFamily: 'inherit', minHeight: 20, maxHeight: 100,
            opacity: disabled ? 0.4 : 1,
          }}
        />
        <button onClick={onSubmit} disabled={!value.trim() || loading || disabled} style={{
          width: 30, height: 30, borderRadius: 7, flexShrink: 0,
          background: value.trim() && !loading ? 'linear-gradient(135deg, #6366f1, #06b6d4)' : 'rgba(255,255,255,0.06)',
          border: 'none', cursor: value.trim() && !loading ? 'pointer' : 'not-allowed',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          transition: 'all 0.15s',
        }}>
          {loading ? <Loader2 size={14} color="rgba(255,255,255,0.5)" className="spin" /> : <Zap size={14} color={value.trim() ? 'white' : 'rgba(255,255,255,0.25)'} />}
        </button>
      </div>
      <div style={{ fontSize: 10, color: 'rgba(232,240,255,0.25)', marginTop: 5, textAlign: 'center' }}>
        Enter to send · Shift+Enter for new line · Your code is yours — no harvesting
      </div>
    </div>
  );
}
