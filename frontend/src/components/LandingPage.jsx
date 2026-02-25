import React, { useState, useEffect, useRef } from 'react';
import { ArrowUpRight, Check, Zap, Star, Crown } from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || '';

// Laser Beams Component - Subtle beams, sparkly stars
const LaserBeams = () => {
  const canvasRef = useRef(null);
  const starsRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationId;
    let time = 0;
    
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      starsRef.current = generateStars(canvas.width, canvas.height);
    };
    
    const generateStars = (w, h) => {
      const stars = [];
      for (let i = 0; i < 150; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          size: Math.random() * 1 + 0.3,
          speed: Math.random() * 1.5 + 0.5,
          phase: Math.random() * Math.PI * 2,
          type: 'regular'
        });
      }
      for (let i = 0; i < 20; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          size: Math.random() * 1.5 + 1,
          speed: Math.random() * 2 + 1,
          phase: Math.random() * Math.PI * 2,
          type: 'sparkle'
        });
      }
      for (let i = 0; i < 5; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          size: Math.random() * 2 + 1.5,
          speed: Math.random() * 2.5 + 1.5,
          phase: Math.random() * Math.PI * 2,
          type: 'super'
        });
      }
      return stars;
    };
    
    const drawLasers = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const lasers = [
        { x1: 0, y1: canvas.height * 0.3, angle: 15, alpha: 0.15, width: 1 },
        { x1: canvas.width, y1: canvas.height * 0.2, angle: 165, alpha: 0.1, width: 1 },
        { x1: 0, y1: canvas.height * 0.7, angle: 10, alpha: 0.12, width: 1 },
        { x1: canvas.width, y1: canvas.height * 0.8, angle: 170, alpha: 0.15, width: 1 },
        { x1: canvas.width * 0.5, y1: 0, angle: 90 + Math.sin(time * 0.005) * 3, alpha: 0.08, width: 1.5 },
      ];
      
      lasers.forEach(laser => {
        const length = Math.max(canvas.width, canvas.height) * 1.5;
        const rad = laser.angle * Math.PI / 180;
        const x2 = laser.x1 + Math.cos(rad) * length;
        const y2 = laser.y1 + Math.sin(rad) * length;
        
        ctx.shadowBlur = 15;
        ctx.shadowColor = `rgba(255, 255, 255, ${laser.alpha})`;
        ctx.strokeStyle = `rgba(255, 255, 255, ${laser.alpha * 0.7})`;
        ctx.lineWidth = laser.width;
        ctx.beginPath();
        ctx.moveTo(laser.x1, laser.y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        ctx.shadowBlur = 0;
      });
      
      if (starsRef.current) {
        starsRef.current.forEach(star => {
          const twinkle = Math.sin(time * star.speed * 0.06 + star.phase) * 0.5 + 0.5;
          const sparkle = Math.sin(time * star.speed * 0.1 + star.phase * 2) * 0.3 + 0.7;
          
          if (star.type === 'super') {
            const intensity = twinkle * sparkle;
            ctx.shadowBlur = 12;
            ctx.shadowColor = `rgba(255, 255, 255, ${intensity * 0.5})`;
            ctx.strokeStyle = `rgba(255, 255, 255, ${intensity * 0.3})`;
            ctx.lineWidth = 0.5;
            const len = star.size * 2 * intensity;
            ctx.beginPath();
            ctx.moveTo(star.x - len, star.y);
            ctx.lineTo(star.x + len, star.y);
            ctx.moveTo(star.x, star.y - len);
            ctx.lineTo(star.x, star.y + len);
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.size * intensity + 0.3, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${intensity * 0.9})`;
            ctx.fill();
            ctx.shadowBlur = 0;
          } else if (star.type === 'sparkle') {
            const intensity = twinkle * sparkle;
            ctx.shadowBlur = 8;
            ctx.shadowColor = `rgba(255, 255, 255, ${intensity * 0.4})`;
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.size * intensity + 0.3, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${intensity * 0.85 + 0.1})`;
            ctx.fill();
            ctx.shadowBlur = 0;
          } else {
            const intensity = twinkle * 0.6 + 0.4;
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.size * (intensity * 0.3 + 0.7), 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${intensity * 0.7})`;
            ctx.fill();
          }
        });
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

// Pricing Card Component
const PricingCard = ({ pkg, packageId, isPopular, onSelect, loading }) => {
  const icons = {
    free: Zap,
    starter: Star,
    pro: Crown,
    enterprise: Crown
  };
  const Icon = icons[packageId] || Zap;
  
  return (
    <div className={`relative p-4 rounded-xl border backdrop-blur-sm transition-all duration-300 hover:scale-105 ${
      isPopular 
        ? 'border-cyan-500/50 bg-cyan-500/10' 
        : 'border-white/10 bg-white/5 hover:border-white/30'
    }`}>
      {isPopular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-cyan-500 rounded-full text-[9px] font-mono uppercase tracking-wider">
          Most Popular
        </div>
      )}
      
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-4 h-4 ${isPopular ? 'text-cyan-400' : 'text-white/60'}`} />
        <span className="text-sm font-mono text-white/90">{pkg.name}</span>
      </div>
      
      <div className="mb-3">
        <span className="text-2xl font-mono text-white">${pkg.amount}</span>
        <span className="text-xs text-white/40">/mo</span>
      </div>
      
      <ul className="space-y-1 mb-4">
        {pkg.features.map((feature, idx) => (
          <li key={idx} className="flex items-center gap-2 text-[10px] font-mono text-white/60">
            <Check className="w-3 h-3 text-green-400" />
            {feature}
          </li>
        ))}
      </ul>
      
      <button
        onClick={() => onSelect(packageId)}
        disabled={loading}
        className={`w-full py-2 rounded-lg text-[10px] font-mono uppercase tracking-wider transition-all ${
          isPopular
            ? 'bg-cyan-500 text-black hover:bg-cyan-400'
            : 'bg-white/10 text-white/70 hover:bg-white/20 border border-white/10'
        } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        {loading ? 'Processing...' : packageId === 'free' ? 'Start Free' : 'Subscribe'}
      </button>
    </div>
  );
};

export const LandingPage = ({ onNavigateToIDE }) => {
  const onEnterApp = onNavigateToIDE; // Alias for backward compatibility
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPricing, setShowPricing] = useState(false);
  const [packages, setPackages] = useState(null);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  
  // Check for payment success
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    if (sessionId && sessionId !== 'free_tier_no_payment') {
      // Poll payment status
      const checkStatus = async () => {
        try {
          const response = await axios.get(`${API}/api/payments/status/${sessionId}`);
          if (response.data.payment_status === 'paid') {
            localStorage.setItem('franklin_user', JSON.stringify({
              email: response.data.user_email,
              package: response.data.package,
              authenticated: true
            }));
            // Clear URL params and enter app
            window.history.replaceState({}, '', window.location.pathname);
            onEnterApp();
          }
        } catch (err) {
          console.error('Payment status check failed:', err);
        }
      };
      checkStatus();
    }
  }, [onEnterApp]);
  
  // Fetch packages
  useEffect(() => {
    const fetchPackages = async () => {
      try {
        const response = await axios.get(`${API}/api/payments/packages`);
        setPackages(response.data.packages);
      } catch (err) {
        console.error('Failed to fetch packages:', err);
      }
    };
    fetchPackages();
  }, []);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    // Store user session
    localStorage.setItem('franklin_user', JSON.stringify({
      username,
      authenticated: true,
      package: 'free'
    }));
    onEnterApp();
  };
  
  const handleSelectPackage = async (packageId) => {
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/api/payments/checkout`, {
        package_id: packageId,
        origin_url: window.location.origin,
        user_email: email || username || null
      });
      
      if (response.data.url) {
        if (packageId === 'free') {
          localStorage.setItem('franklin_user', JSON.stringify({
            email: email || username,
            package: 'free',
            authenticated: true
          }));
          onEnterApp();
        } else {
          // Redirect to Stripe checkout
          window.location.href = response.data.url;
        }
      }
    } catch (err) {
      console.error('Checkout error:', err);
      alert('Payment initialization failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden text-white bg-black">
      <LaserBeams />
      
      <div className="relative z-20 min-h-screen flex flex-col items-center justify-center px-6">
        
        {/* YUR-AI Branding */}
        <div className="text-center mb-6" data-testid="yurai-branding">
          <h2 
            className="text-[clamp(2rem,8vw,5rem)] font-bold tracking-[0.4em] mb-2 yurai-chrome"
            style={{ fontFamily: "'Orbitron', sans-serif" }}
          >
            YUR-AI
          </h2>
          <p 
            className="text-[clamp(0.7rem,2vw,1rem)] tracking-[0.2em] text-white/50 mb-4"
            style={{ fontFamily: "'Rajdhani', sans-serif" }}
          >
            presents to all the dependable open-source TRUST engine
          </p>
        </div>
        
        {/* FRANKLIN Title */}
        <h1
          className="text-[clamp(3rem,12vw,9rem)] font-semibold tracking-[0.55em] select-none mb-2 franklin-chrome"
          style={{ fontFamily: "'Orbitron', sans-serif" }}
          data-testid="franklin-title"
        >
          FRANKLIN
        </h1>
        
        {/* OS Subtitle */}
        <p 
          className="text-[clamp(1rem,3vw,1.5rem)] tracking-[0.5em] text-cyan-400 mb-3"
          style={{ fontFamily: "'Orbitron', sans-serif" }}
        >
          OS
        </p>
        
        {/* Trust Tagline */}
        <p 
          className="text-[clamp(0.8rem,2.5vw,1.1rem)] tracking-[0.15em] text-white/60 mb-12 italic"
          style={{ fontFamily: "'Rajdhani', sans-serif" }}
        >
          trust is not implied — it's verified
        </p>
        
        <style>{`
          .franklin-chrome, .yurai-chrome {
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
            animation: chromeShimmer 20s ease-in-out infinite;
            filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.15));
          }
          
          @keyframes chromeShimmer {
            0% { background-position: 200% 200%; }
            50% { background-position: 0% 0%; }
            100% { background-position: 200% 200%; }
          }
        `}</style>
        
        {!showPricing ? (
          <>
            {/* Login Form */}
            <form onSubmit={handleSubmit} className="w-full max-w-2xl">
              <div className="flex items-center gap-3 rounded-full border border-white/15 bg-white/5 px-4 py-2 backdrop-blur-sm">
                <input
                  type="text"
                  placeholder="Email or Username"
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
          </>
        ) : (
          <>
            {/* Pricing Section */}
            <div className="w-full max-w-4xl mb-6">
              <div className="text-center mb-6">
                <h2 className="text-xl font-mono text-white/90 tracking-wider mb-2">Choose Your Plan</h2>
                <p className="text-xs font-mono text-white/40">Scale your AI-powered development</p>
              </div>
              
              {/* Email input for subscription */}
              <div className="flex justify-center mb-6">
                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-64 px-4 py-2 rounded-full border border-white/20 bg-white/5 text-sm text-white placeholder:text-white/35 focus:outline-none focus:border-cyan-500/50"
                />
              </div>
              
              {/* Pricing Cards */}
              {packages && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {Object.entries(packages).map(([id, pkg]) => (
                    <PricingCard
                      key={id}
                      packageId={id}
                      pkg={pkg}
                      isPopular={id === 'pro'}
                      onSelect={handleSelectPackage}
                      loading={loading}
                    />
                  ))}
                </div>
              )}
              
              {/* Back button */}
              <div className="flex justify-center mt-6">
                <button
                  onClick={() => setShowPricing(false)}
                  className="text-xs font-mono text-white/40 hover:text-white/70 transition-all"
                >
                  ← Back to Login
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default LandingPage;
