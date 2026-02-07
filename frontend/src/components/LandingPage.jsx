import React, { useEffect, useRef, useState } from 'react';

// Plexus/Network Background Canvas
const PlexusBackground = () => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationId;
    let particles = [];
    
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    const createParticles = () => {
      particles = [];
      const numParticles = Math.floor((canvas.width * canvas.height) / 15000);
      for (let i = 0; i < numParticles; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          radius: Math.random() * 2 + 1
        });
      }
    };
    
    const drawParticles = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          if (dist < 150) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(0, 200, 255, ${(1 - dist / 150) * 0.3})`;
            ctx.lineWidth = 1;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }
      
      // Draw particles
      for (const p of particles) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0, 200, 255, 0.8)';
        ctx.fill();
        
        // Update position
        p.x += p.vx;
        p.y += p.vy;
        
        // Bounce off edges
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
      }
      
      animationId = requestAnimationFrame(drawParticles);
    };
    
    resize();
    createParticles();
    drawParticles();
    
    window.addEventListener('resize', () => {
      resize();
      createParticles();
    });
    
    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resize);
    };
  }, []);
  
  return (
    <canvas 
      ref={canvasRef} 
      className="fixed inset-0 z-0 pointer-events-none"
      style={{ background: 'linear-gradient(180deg, #0a1628 0%, #0d1f3c 50%, #0a1628 100%)' }}
    />
  );
};

// Animated Wave Component
const AnimatedWaves = () => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationId;
    let time = 0;
    
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = 300;
    };
    
    const drawWaves = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const waves = [
        { amplitude: 40, frequency: 0.01, speed: 0.02, offset: 0, color: 'rgba(0, 200, 255, 0.6)' },
        { amplitude: 30, frequency: 0.015, speed: 0.025, offset: 50, color: 'rgba(0, 150, 255, 0.4)' },
        { amplitude: 35, frequency: 0.012, speed: 0.018, offset: -30, color: 'rgba(0, 255, 200, 0.3)' },
      ];
      
      for (const wave of waves) {
        ctx.beginPath();
        ctx.strokeStyle = wave.color;
        ctx.lineWidth = 2;
        
        for (let x = 0; x <= canvas.width; x += 5) {
          const y = canvas.height / 2 + 
            Math.sin(x * wave.frequency + time * wave.speed) * wave.amplitude +
            Math.sin(x * wave.frequency * 2 + time * wave.speed * 1.5) * (wave.amplitude * 0.5) +
            wave.offset;
          
          if (x === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.stroke();
      }
      
      time += 1;
      animationId = requestAnimationFrame(drawWaves);
    };
    
    resize();
    drawWaves();
    
    window.addEventListener('resize', resize);
    
    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resize);
    };
  }, []);
  
  return (
    <canvas 
      ref={canvasRef} 
      className="absolute top-0 left-0 w-full z-10 pointer-events-none"
      style={{ height: '300px' }}
    />
  );
};

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
    <div className="min-h-screen relative overflow-hidden" style={{ background: '#0a1628' }}>
      {/* Plexus Network Background */}
      <PlexusBackground />
      
      {/* Animated Waves at Top */}
      <AnimatedWaves />
      
      {/* Main Content */}
      <div className="relative z-20 min-h-screen flex flex-col items-center justify-center px-6">
        
        {/* FRANKLIN Ghost Title */}
        <h1 
          className="text-[12vw] md:text-[10vw] font-bold tracking-[0.3em] text-transparent mb-8 select-none"
          style={{
            fontFamily: "'Orbitron', 'Rajdhani', 'Share Tech Mono', sans-serif",
            WebkitTextStroke: '1px rgba(0, 200, 255, 0.3)',
            textShadow: '0 0 60px rgba(0, 200, 255, 0.2), 0 0 120px rgba(0, 200, 255, 0.1)',
            letterSpacing: '0.3em'
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
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M7 17L17 7M17 7H7M17 7V17" />
              </svg>
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
