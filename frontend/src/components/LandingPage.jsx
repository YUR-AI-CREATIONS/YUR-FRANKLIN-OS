import React, { useState } from 'react';
import { ArrowUpRight } from 'lucide-react';

// Status Badge Component
const StatusBadge = ({ label, online = true }) => (
  <div className={`px-4 py-2 rounded border font-mono text-xs uppercase tracking-wider transition-all
    ${online 
      ? 'border-cyan-500/50 text-cyan-400 bg-cyan-500/10 hover:bg-cyan-500/20' 
      : 'border-zinc-600 text-zinc-500 bg-zinc-800/50'
    }`}
  >
    {label}
  </div>
);

export const LandingPage = ({ onEnterApp }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onEnterApp();
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-[#04060b] text-white">
      {/* Oracle Snow / Lasers Effect */}
      <div className="absolute inset-0 oracle-snow opacity-40" />
      
      {/* Main Content */}
      <div className="relative z-20 min-h-screen flex flex-col items-center justify-center px-6">
        
        {/* FRANKLIN Gradient Title - matching the pic */}
        <h1
          className="text-[clamp(3rem,12vw,9rem)] font-semibold tracking-[0.55em] text-transparent bg-clip-text bg-gradient-to-r from-white/30 via-cyan-200/70 to-white/20 opacity-70 mb-12 select-none"
          style={{ 
            textShadow: '0 0 70px rgba(98, 200, 255, 0.35)',
            fontFamily: "'Orbitron', 'Rajdhani', sans-serif"
          }}
          data-testid="franklin-title"
        >
          FRANKLIN
        </h1>
        
        {/* Login Form */}
        <form onSubmit={handleSubmit} className="w-full max-w-2xl mb-8">
          <div 
            className="flex items-center rounded-lg overflow-hidden"
            style={{
              background: 'linear-gradient(90deg, rgba(30, 40, 60, 0.8) 0%, rgba(40, 50, 70, 0.9) 100%)',
              border: '1px solid rgba(0, 200, 255, 0.2)',
              boxShadow: '0 0 30px rgba(0, 200, 255, 0.1)'
            }}
          >
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="flex-1 px-6 py-4 bg-transparent text-cyan-100 placeholder-cyan-700 font-mono text-sm focus:outline-none"
              data-testid="username-input"
            />
            <div className="w-px h-8 bg-cyan-500/30" />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="flex-1 px-6 py-4 bg-transparent text-cyan-100 placeholder-cyan-700 font-mono text-sm focus:outline-none"
              data-testid="password-input"
            />
            <button
              type="submit"
              className="px-6 py-4 text-cyan-400 hover:text-cyan-300 hover:bg-cyan-500/10 transition-all"
              data-testid="login-submit"
            >
              <ArrowUpRight className="w-5 h-5" />
            </button>
          </div>
        </form>
        
        {/* Neural Command Label */}
        <p className="text-cyan-600 font-mono text-xs uppercase tracking-[0.4em] mb-6">
          Input Neural Command
        </p>
        
        {/* Main CTA Button */}
        <button
          onClick={onEnterApp}
          className="px-8 py-3 rounded border border-cyan-500/50 text-cyan-400 font-mono text-sm uppercase tracking-widest hover:bg-cyan-500/10 hover:border-cyan-400 transition-all mb-10"
          data-testid="enter-app-btn"
        >
          Open Franklin Garage Preview
        </button>
        
        {/* Status Badges */}
        <div className="flex flex-wrap justify-center gap-3 mb-10">
          <StatusBadge label="Garage Online" online={true} />
          <StatusBadge label="Oracle Online" online={true} />
          <StatusBadge label="Franklin Online" online={true} />
          <StatusBadge label="Agents Online" online={true} />
        </div>
        
        <div className="mb-10">
          <StatusBadge label="Bots Online" online={true} />
        </div>
        
        {/* Footer Text */}
        <div className="text-center max-w-2xl">
          <p className="text-cyan-700 font-mono text-xs uppercase tracking-wider leading-relaxed">
            You've reached the world-class Agent + Bot Academy, governed under Franklin OS.
          </p>
          <p className="text-cyan-600 font-mono text-xs uppercase tracking-wider mt-2">
            Enter Franklin's Garage to explore the Academy and get a free Oracle consultation.
          </p>
        </div>
      </div>
      
      {/* Bottom Accent Line */}
      <div 
        className="absolute bottom-0 left-0 right-0 h-1"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(200, 150, 50, 0.8) 50%, transparent 100%)'
        }}
      />
    </div>
  );
};

export default LandingPage;
