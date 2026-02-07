import React, { useState, useEffect, useRef } from 'react';
import { ArrowUpRight } from 'lucide-react';

// Laser Beams Component - Enhanced visibility
const LaserBeams = () => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationId;
    let time = 0;
    
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    const drawLasers = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Enhanced white laser beams - more visible
      const lasers = [
        { x1: 0, y1: canvas.height * 0.25, angle: 12, alpha: 0.4, width: 1.5 },
        { x1: canvas.width, y1: canvas.height * 0.15, angle: 168, alpha: 0.35, width: 1.5 },
        { x1: 0, y1: canvas.height * 0.65, angle: 8, alpha: 0.35, width: 1.5 },
        { x1: canvas.width, y1: canvas.height * 0.75, angle: 172, alpha: 0.4, width: 1.5 },
        { x1: canvas.width * 0.3, y1: 0, angle: 95 + Math.sin(time * 0.008) * 3, alpha: 0.3, width: 2 },
        { x1: canvas.width * 0.7, y1: canvas.height, angle: -85 + Math.sin(time * 0.01) * 3, alpha: 0.3, width: 2 },
        { x1: 0, y1: canvas.height * 0.45, angle: 5, alpha: 0.25, width: 1 },
        { x1: canvas.width, y1: canvas.height * 0.5, angle: 175, alpha: 0.25, width: 1 },
      ];
      
      lasers.forEach(laser => {
        const length = Math.max(canvas.width, canvas.height) * 2;
        const rad = laser.angle * Math.PI / 180;
        const x2 = laser.x1 + Math.cos(rad) * length;
        const y2 = laser.y1 + Math.sin(rad) * length;
        
        // Strong glow effect
        ctx.shadowBlur = 30;
        ctx.shadowColor = `rgba(255, 255, 255, ${laser.alpha * 0.8})`;
        
        ctx.beginPath();
        ctx.strokeStyle = `rgba(255, 255, 255, ${laser.alpha})`;
        ctx.lineWidth = laser.width;
        ctx.moveTo(laser.x1, laser.y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        
        // Double stroke for more glow
        ctx.shadowBlur = 15;
        ctx.strokeStyle = `rgba(255, 255, 255, ${laser.alpha * 0.5})`;
        ctx.lineWidth = laser.width * 3;
        ctx.stroke();
        
        ctx.shadowBlur = 0;
      });
      
      // Floating stars/particles - slightly brighter
      for (let i = 0; i < 100; i++) {
        const x = (Math.sin(time * 0.0005 + i * 0.5) * 0.5 + 0.5) * canvas.width;
        const y = (Math.cos(time * 0.0008 + i * 0.7) * 0.5 + 0.5) * canvas.height;
        const size = Math.sin(time * 0.003 + i) * 1 + 1.5;
        const alpha = Math.sin(time * 0.002 + i) * 0.3 + 0.5;
        
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${alpha * 0.6})`;
        ctx.fill();
      }
      
      time += 1;
      animationId = requestAnimationFrame(drawLasers);
    };
    
    resize();
    drawLasers();
    
    window.addEventListener('resize', resize);
    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resize);
    };
  }, []);
  
  return <canvas ref={canvasRef} className="absolute inset-0 z-10 pointer-events-none" />;
};

// Status Badge Component
const StatusBadge = ({ label }) => (
  <div className="px-4 py-2 rounded-full font-mono text-xs uppercase tracking-wider
    bg-transparent border border-white/20 text-white/50
    hover:border-white/40 hover:text-white/70 transition-all duration-300"
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
    <div className="min-h-screen relative overflow-hidden text-white bg-black">
      {/* Laser Beams */}
      <LaserBeams />
      
      {/* Main Content - All centered together */}
      <div className="relative z-20 min-h-screen flex flex-col items-center justify-center px-6">
        
        {/* FRANKLIN Title */}
        <h1
          className="text-[clamp(3rem,12vw,9rem)] font-semibold tracking-[0.55em] text-transparent bg-clip-text bg-gradient-to-r from-white/30 via-white/70 to-white/20 opacity-70 select-none mb-12"
          style={{ 
            fontFamily: "'Orbitron', sans-serif",
            textShadow: '0 0 70px rgba(255, 255, 255, 0.2)',
          }}
          data-testid="franklin-title"
        >
          FRANKLIN
        </h1>
        
        {/* Login Form */}
        <form onSubmit={handleSubmit} className="w-full max-w-2xl mb-4">
          <div className="flex items-center gap-3 rounded-full border border-white/15 bg-white/5 px-4 py-2 backdrop-blur-sm">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="h-10 w-full bg-transparent text-sm text-white placeholder:text-white/35 focus:outline-none"
              data-testid="username-input"
            />
            <div className="h-8 w-px bg-white/20" />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="h-10 w-full bg-transparent text-sm text-white placeholder:text-white/35 focus:outline-none"
              data-testid="password-input"
            />
            <button
              type="submit"
              className="flex h-10 w-10 items-center justify-center rounded-full border border-white/20 bg-white/10 hover:bg-white/20 transition-all"
              data-testid="login-submit"
            >
              <ArrowUpRight className="h-4 w-4" />
            </button>
          </div>
        </form>
        
        {/* Labels and CTA */}
        <div className="flex flex-col items-center gap-2 text-center mb-8">
          <span className="text-[11px] uppercase tracking-[0.4em] text-white/35">
            Input neural command
          </span>
          <button
            onClick={onEnterApp}
            className="rounded-full border border-white/20 px-4 py-2 text-[10px] uppercase tracking-[0.35em] text-white/60 hover:border-white/40 hover:text-white transition-all"
            data-testid="enter-app-btn"
          >
            Open Franklin Garage Preview
          </button>
        </div>
        
        {/* Status Badges */}
        <div className="flex flex-wrap justify-center gap-3 mb-4">
          <StatusBadge label="Garage Online" />
          <StatusBadge label="Oracle Online" />
          <StatusBadge label="Franklin Online" />
          <StatusBadge label="Agents Online" />
        </div>
        
        <div className="flex justify-center mb-6">
          <StatusBadge label="Bots Online" />
        </div>
        
        {/* Footer Text */}
        <div className="text-center max-w-2xl">
          <p className="text-white/25 font-mono text-xs uppercase tracking-wider leading-relaxed">
            You've reached the world-class Agent + Bot Academy, governed under Franklin OS.
          </p>
          <p className="text-white/35 font-mono text-xs uppercase tracking-wider mt-1">
            Enter Franklin's Garage to explore the Academy and get a free Oracle consultation.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
