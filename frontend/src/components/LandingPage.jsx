import React, { useState, useEffect, useRef } from 'react';
import { ArrowUpRight } from 'lucide-react';

// Laser Beams Component - Subtle beams, enhanced stars
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
      
      // Subtle laser beams
      const lasers = [
        { x1: 0, y1: canvas.height * 0.3, angle: 15, alpha: 0.15, width: 1 },
        { x1: canvas.width, y1: canvas.height * 0.2, angle: 165, alpha: 0.1, width: 1 },
        { x1: 0, y1: canvas.height * 0.7, angle: 10, alpha: 0.12, width: 1 },
        { x1: canvas.width, y1: canvas.height * 0.8, angle: 170, alpha: 0.15, width: 1 },
        { x1: canvas.width * 0.5, y1: 0, angle: 90 + Math.sin(time * 0.01) * 5, alpha: 0.08, width: 1.5 },
      ];
      
      lasers.forEach(laser => {
        const length = Math.max(canvas.width, canvas.height) * 1.5;
        const rad = laser.angle * Math.PI / 180;
        const x2 = laser.x1 + Math.cos(rad) * length;
        const y2 = laser.y1 + Math.sin(rad) * length;
        
        ctx.shadowBlur = 15;
        ctx.shadowColor = `rgba(255, 255, 255, ${laser.alpha})`;
        
        ctx.beginPath();
        ctx.strokeStyle = `rgba(255, 255, 255, ${laser.alpha})`;
        ctx.lineWidth = laser.width;
        ctx.moveTo(laser.x1, laser.y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        
        ctx.shadowBlur = 0;
      });
      
      // Enhanced floating stars
      for (let i = 0; i < 150; i++) {
        const baseX = (i * 17) % canvas.width;
        const baseY = (i * 23) % canvas.height;
        const x = baseX + Math.sin(time * 0.001 + i) * 20;
        const y = baseY + Math.cos(time * 0.0015 + i) * 15;
        const twinkle = Math.sin(time * 0.005 + i * 0.5) * 0.5 + 0.5;
        const size = (Math.sin(i) * 0.5 + 1) * twinkle + 0.5;
        const alpha = twinkle * 0.8 + 0.2;
        
        // Star glow
        ctx.shadowBlur = 8;
        ctx.shadowColor = `rgba(255, 255, 255, ${alpha * 0.5})`;
        
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
        ctx.fill();
        
        ctx.shadowBlur = 0;
      }
      
      // Extra bright stars
      for (let i = 0; i < 20; i++) {
        const x = (i * 97) % canvas.width;
        const y = (i * 73) % canvas.height;
        const twinkle = Math.sin(time * 0.003 + i * 2) * 0.5 + 0.5;
        const size = twinkle * 2 + 1;
        
        ctx.shadowBlur = 15;
        ctx.shadowColor = `rgba(255, 255, 255, 0.8)`;
        
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${twinkle * 0.9 + 0.1})`;
        ctx.fill();
        
        ctx.shadowBlur = 0;
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
        
        {/* FRANKLIN Title - Matte Chrome Shimmer */}
        <h1
          className="text-[clamp(3rem,12vw,9rem)] font-semibold tracking-[0.55em] select-none mb-12 franklin-chrome"
          style={{ 
            fontFamily: "'Orbitron', sans-serif",
          }}
          data-testid="franklin-title"
        >
          FRANKLIN
        </h1>
        
        {/* Chrome shimmer styles */}
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
            animation: chromeShimmer 8s ease-in-out infinite;
            filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.15));
          }
          
          @keyframes chromeShimmer {
            0% {
              background-position: 200% 200%;
            }
            50% {
              background-position: 0% 0%;
            }
            100% {
              background-position: 200% 200%;
            }
          }
        `}</style>
        
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
