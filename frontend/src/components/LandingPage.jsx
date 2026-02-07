import React, { useState } from 'react';
import { ArrowUpRight } from 'lucide-react';
import ParticleBackground from './ParticleBackground';

export const LandingPage = ({ onEnterApp }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [disabled, setDisabled] = useState(false);

  const isReady = username.trim().length > 0 && password.trim().length > 0 && !disabled;

  const handleSubmit = () => {
    if (isReady || true) { // Allow entry even without credentials for demo
      onEnterApp();
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#04060b] text-white">
      {/* Grid Background */}
      <div className="absolute inset-0 garage-grid" />
      
      {/* Snow/Particle Effect */}
      <div className="absolute inset-0 oracle-snow opacity-40" />
      
      {/* Particle Network */}
      <ParticleBackground />

      {/* Left Side Navigation */}
      <div className="absolute left-6 top-10 z-10 hidden flex-col gap-4 text-xs uppercase tracking-[0.35em] text-white/50 md:flex">
        <span className="text-white">Vault</span>
        <span>Branches</span>
        <span>System</span>
      </div>

      {/* Status Badges - Top Right */}
      <div className="absolute right-6 top-10 z-10 hidden flex-col gap-2 md:flex">
        <StatusBadge label="Garage Online" />
        <StatusBadge label="Oracle Online" />
        <StatusBadge label="Franklin Online" />
        <StatusBadge label="Agents Online" />
      </div>

      {/* Ghost FRANKLIN Title */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <h1
          className="text-[clamp(3rem,12vw,9rem)] font-semibold tracking-[0.55em] text-transparent bg-clip-text bg-gradient-to-r from-white/30 via-cyan-200/70 to-white/20 opacity-70 select-none"
          style={{ 
            textShadow: '0 0 70px rgba(98, 200, 255, 0.35)',
            fontFamily: "'Orbitron', 'Rajdhani', sans-serif"
          }}
          data-testid="franklin-title"
        >
          FRANKLIN
        </h1>
      </div>

      {/* Bottom Input Section */}
      <div className="absolute bottom-10 left-1/2 z-10 w-full max-w-3xl -translate-x-1/2 px-6">
        {/* Login Form */}
        <div className="flex items-center gap-3 rounded-full border border-white/15 bg-white/5 px-4 py-2 backdrop-blur-xl shadow-[0_0_40px_rgba(15,23,42,0.45)]">
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={disabled}
            placeholder="Username"
            className="h-10 w-full bg-transparent text-sm text-white placeholder:text-white/35 focus:outline-none"
            data-testid="username-input"
          />
          <div className="h-8 w-px bg-white/20" />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSubmit();
              }
            }}
            disabled={disabled}
            placeholder="Password"
            className="h-10 w-full bg-transparent text-sm text-white placeholder:text-white/35 focus:outline-none"
            data-testid="password-input"
          />
          <button
            type="button"
            aria-label="Enter Franklin Garage"
            onClick={handleSubmit}
            className="flex h-10 w-10 items-center justify-center rounded-full border border-white/20 transition bg-white/10 hover:bg-white/20"
            data-testid="login-submit"
          >
            <ArrowUpRight className="h-4 w-4" />
          </button>
        </div>

        {/* Labels and CTA */}
        <div className="mt-4 flex flex-col items-center gap-3 text-center">
          <span className="text-[11px] uppercase tracking-[0.4em] text-white/35">
            Input neural command
          </span>
          <button
            onClick={onEnterApp}
            className="rounded-full border border-white/20 px-6 py-2.5 text-[10px] uppercase tracking-[0.35em] text-white/60 hover:border-cyan-500/50 hover:text-cyan-400 hover:shadow-[0_0_20px_rgba(0,200,255,0.2)] transition-all"
            data-testid="enter-app-btn"
          >
            Open Franklin Garage Preview
          </button>
        </div>

        {/* Footer Text */}
        <div className="mt-8 text-center">
          <p className="text-[10px] uppercase tracking-[0.3em] text-white/25 leading-relaxed">
            You've reached the world-class Agent + Bot Academy, governed under Franklin OS.
          </p>
          <p className="text-[10px] uppercase tracking-[0.3em] text-white/35 mt-1">
            Enter Franklin's Garage to explore the Academy and get a free Oracle consultation.
          </p>
        </div>
      </div>

      {/* Bottom Accent Line */}
      <div 
        className="absolute bottom-0 left-0 right-0 h-[2px]"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(200, 150, 50, 0.6) 50%, transparent 100%)'
        }}
      />
    </div>
  );
};

// Status Badge Component
const StatusBadge = ({ label }) => (
  <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.3em] text-white/40">
    <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
    <span>{label}</span>
  </div>
);

export default LandingPage;
