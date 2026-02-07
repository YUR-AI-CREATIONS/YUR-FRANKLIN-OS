import React, { useState, useEffect, useRef } from 'react';
import { ArrowUpRight } from 'lucide-react';

// Laser Beams Component
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
      
      // Draw multiple laser beams
      const lasers = [
        { x1: 0, y1: canvas.height * 0.3, angle: 15, color: 'rgba(138, 43, 226, 0.4)', width: 2 },
        { x1: canvas.width, y1: canvas.height * 0.2, angle: 165, color: 'rgba(0, 191, 255, 0.3)', width: 1.5 },
        { x1: 0, y1: canvas.height * 0.7, angle: 10, color: 'rgba(255, 0, 128, 0.3)', width: 1.5 },
        { x1: canvas.width, y1: canvas.height * 0.8, angle: 170, color: 'rgba(75, 0, 130, 0.4)', width: 2 },
        { x1: canvas.width * 0.5, y1: 0, angle: 90 + Math.sin(time * 0.01) * 5, color: 'rgba(147, 112, 219, 0.2)', width: 3 },
      ];
      
      lasers.forEach(laser => {
        const length = Math.max(canvas.width, canvas.height) * 1.5;
        const rad = laser.angle * Math.PI / 180;
        const x2 = laser.x1 + Math.cos(rad) * length;
        const y2 = laser.y1 + Math.sin(rad) * length;
        
        // Glow effect
        ctx.shadowBlur = 20;
        ctx.shadowColor = laser.color;
        
        ctx.beginPath();
        ctx.strokeStyle = laser.color;
        ctx.lineWidth = laser.width;
        ctx.moveTo(laser.x1, laser.y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        
        ctx.shadowBlur = 0;
      });
      
      // Floating particles
      for (let i = 0; i < 50; i++) {
        const x = (Math.sin(time * 0.001 + i) * 0.5 + 0.5) * canvas.width;
        const y = (Math.cos(time * 0.0015 + i * 1.5) * 0.5 + 0.5) * canvas.height;
        const size = Math.sin(time * 0.005 + i) * 1.5 + 2;
        const alpha = Math.sin(time * 0.003 + i) * 0.3 + 0.4;
        
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${alpha * 0.3})`;
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

// Status Badge Component - Glassmorphism
const StatusBadge = ({ label }) => (
  <div className="px-4 py-2 rounded-full font-mono text-xs uppercase tracking-wider
    bg-white/5 backdrop-blur-md border border-white/10 text-white/70
    hover:bg-white/10 hover:border-white/20 transition-all duration-300
    shadow-[0_0_15px_rgba(138,43,226,0.2)]"
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
    <div className="min-h-screen relative overflow-hidden text-white">
      {/* Galactic Background */}
      <div 
        className="absolute inset-0"
        style={{
          background: `
            radial-gradient(ellipse at 20% 20%, rgba(138, 43, 226, 0.3) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 30%, rgba(75, 0, 130, 0.4) 0%, transparent 45%),
            radial-gradient(ellipse at 40% 80%, rgba(0, 100, 150, 0.3) 0%, transparent 50%),
            radial-gradient(ellipse at 90% 90%, rgba(255, 0, 128, 0.2) 0%, transparent 40%),
            radial-gradient(ellipse at 50% 50%, rgba(30, 0, 50, 0.8) 0%, transparent 70%),
            linear-gradient(180deg, #030108 0%, #0a0015 50%, #050010 100%)
          `
        }}
      />
      
      {/* Animated nebula overlay */}
      <div 
        className="absolute inset-0 opacity-50"
        style={{
          background: `
            radial-gradient(circle at 30% 40%, rgba(147, 112, 219, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 70% 60%, rgba(0, 191, 255, 0.1) 0%, transparent 35%)
          `,
          animation: 'nebulaPulse 8s ease-in-out infinite'
        }}
      />
      
      {/* Laser Beams */}
      <LaserBeams />
      
      {/* Main Content */}
      <div className="relative z-20 min-h-screen flex flex-col items-center justify-center px-6">
        
        {/* FRANKLIN Title - Liquid Glass Effect */}
        <h1
          className="text-[clamp(3rem,12vw,9rem)] font-semibold tracking-[0.55em] mb-12 select-none"
          style={{ 
            fontFamily: "'Orbitron', 'Rajdhani', sans-serif",
            background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(200,180,255,0.7) 25%, rgba(255,255,255,0.5) 50%, rgba(180,200,255,0.7) 75%, rgba(255,255,255,0.3) 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            textShadow: '0 0 80px rgba(138, 43, 226, 0.5), 0 0 120px rgba(75, 0, 130, 0.3)',
            filter: 'drop-shadow(0 0 30px rgba(147, 112, 219, 0.4))'
          }}
          data-testid="franklin-title"
        >
          FRANKLIN
        </h1>
        
        {/* Login Form - Liquid Glass Morphism */}
        <form onSubmit={handleSubmit} className="w-full max-w-2xl mb-8">
          <div 
            className="flex items-center rounded-2xl overflow-hidden backdrop-blur-xl"
            style={{
              background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
              border: '1px solid rgba(255, 255, 255, 0.18)',
              boxShadow: `
                0 8px 32px rgba(138, 43, 226, 0.2),
                inset 0 0 30px rgba(255, 255, 255, 0.05),
                0 0 60px rgba(75, 0, 130, 0.15)
              `
            }}
          >
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="flex-1 px-6 py-4 bg-transparent text-white/90 placeholder-white/40 font-mono text-sm focus:outline-none"
              data-testid="username-input"
            />
            <div className="w-px h-8 bg-gradient-to-b from-transparent via-white/30 to-transparent" />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="flex-1 px-6 py-4 bg-transparent text-white/90 placeholder-white/40 font-mono text-sm focus:outline-none"
              data-testid="password-input"
            />
            <button
              type="submit"
              className="px-6 py-4 text-white/70 hover:text-white hover:bg-white/10 transition-all duration-300"
              data-testid="login-submit"
            >
              <ArrowUpRight className="w-5 h-5" />
            </button>
          </div>
        </form>
        
        {/* Neural Command Label */}
        <p className="text-white/50 font-mono text-xs uppercase tracking-[0.4em] mb-6"
           style={{ textShadow: '0 0 20px rgba(147, 112, 219, 0.5)' }}>
          Input Neural Command
        </p>
        
        {/* Main CTA Button - Liquid Glass */}
        <button
          onClick={onEnterApp}
          className="px-8 py-3 rounded-full font-mono text-sm uppercase tracking-widest mb-10
            backdrop-blur-xl transition-all duration-300
            hover:scale-105 hover:shadow-[0_0_40px_rgba(138,43,226,0.4)]"
          style={{
            background: 'linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 4px 20px rgba(138, 43, 226, 0.3), inset 0 0 20px rgba(255,255,255,0.05)',
            color: 'rgba(255,255,255,0.85)'
          }}
          data-testid="enter-app-btn"
        >
          Open Franklin Garage Preview
        </button>
        
        {/* Status Badges */}
        <div className="flex flex-wrap justify-center gap-3 mb-10">
          <StatusBadge label="Garage Online" />
          <StatusBadge label="Oracle Online" />
          <StatusBadge label="Franklin Online" />
          <StatusBadge label="Agents Online" />
        </div>
        
        <div className="mb-10">
          <StatusBadge label="Bots Online" />
        </div>
        
        {/* Footer Text */}
        <div className="text-center max-w-2xl">
          <p className="text-white/40 font-mono text-xs uppercase tracking-wider leading-relaxed"
             style={{ textShadow: '0 0 10px rgba(147, 112, 219, 0.3)' }}>
            You've reached the world-class Agent + Bot Academy, governed under Franklin OS.
          </p>
          <p className="text-white/50 font-mono text-xs uppercase tracking-wider mt-2"
             style={{ textShadow: '0 0 10px rgba(147, 112, 219, 0.3)' }}>
            Enter Franklin's Garage to explore the Academy and get a free Oracle consultation.
          </p>
        </div>
      </div>
      
      {/* Bottom Accent Line - Liquid gradient */}
      <div 
        className="absolute bottom-0 left-0 right-0 h-1"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(138, 43, 226, 0.8) 30%, rgba(255, 0, 128, 0.6) 50%, rgba(75, 0, 130, 0.8) 70%, transparent 100%)'
        }}
      />
      
      {/* CSS for nebula animation */}
      <style>{`
        @keyframes nebulaPulse {
          0%, 100% { opacity: 0.5; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(1.05); }
        }
      `}</style>
    </div>
  );
};

export default LandingPage;
