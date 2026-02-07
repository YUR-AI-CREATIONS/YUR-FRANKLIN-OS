import React from 'react';
import { 
  Zap, Code, Shield, Cpu, Database, Rocket, 
  GitBranch, Layers, Check, ArrowRight, Sparkles,
  Bot, FileCode, Cloud, Video
} from 'lucide-react';

const FEATURES = [
  {
    icon: Bot,
    title: "Socratic Engine",
    description: "AI-powered requirements analysis that asks the right questions to clarify your vision"
  },
  {
    icon: Layers,
    title: "8-Stage Pipeline",
    description: "From inception to deployment through a rigorous quality-gated process"
  },
  {
    icon: Code,
    title: "Real Code Generation",
    description: "Generates production-ready Python, TypeScript, SQL, Docker, and CI/CD configs"
  },
  {
    icon: Database,
    title: "40+ Tech Stacks",
    description: "Next.js, FastAPI, PostgreSQL, Supabase, Vercel, AWS, and more"
  },
  {
    icon: Shield,
    title: "Quality Gate",
    description: "8-dimension scoring ensures 99% quality convergence before output"
  },
  {
    icon: Cloud,
    title: "Multi-LLM Support",
    description: "OpenAI, Anthropic, xAI, Google, or local Ollama - your choice"
  }
];

const INTEGRATIONS = [
  { name: "OpenAI", status: "active" },
  { name: "Anthropic", status: "active" },
  { name: "xAI/Grok", status: "active" },
  { name: "Google", status: "active" },
  { name: "Supabase", status: "active" },
  { name: "Kling AI", status: "active" }
];

const STATS = [
  { value: "40+", label: "Technologies" },
  { value: "8", label: "Quality Dimensions" },
  { value: "99%", label: "Convergence Target" },
  { value: "14+", label: "Files Generated" }
];

export const LandingPage = ({ onEnterApp }) => {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white overflow-x-hidden">
      {/* Gradient Orbs */}
      <div className="fixed top-0 left-1/4 w-[600px] h-[600px] bg-indigo-600/20 rounded-full blur-[128px] pointer-events-none" />
      <div className="fixed bottom-0 right-1/4 w-[400px] h-[400px] bg-purple-600/20 rounded-full blur-[128px] pointer-events-none" />
      
      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <Zap size={22} className="text-white" />
          </div>
          <div>
            <h1 className="font-mono text-lg font-bold tracking-tight">SOVEREIGN GENESIS</h1>
            <p className="text-[10px] text-zinc-500 font-mono">v2.0 • Ouroboros-Lattice Core</p>
          </div>
        </div>
        <button
          onClick={onEnterApp}
          className="px-5 py-2 rounded-lg bg-white/10 hover:bg-white/20 border border-white/10 font-mono text-sm transition-all"
        >
          Launch App
        </button>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 px-6 pt-20 pb-32 max-w-7xl mx-auto">
        <div className="max-w-4xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 mb-6">
            <Sparkles size={14} className="text-indigo-400" />
            <span className="text-xs font-mono text-indigo-400">AI-Powered Software Factory</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold leading-tight mb-6">
            <span className="bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
              Describe it.
            </span>
            <br />
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              We build it.
            </span>
          </h1>
          
          <p className="text-xl text-zinc-400 max-w-2xl mb-10 leading-relaxed">
            Transform vague ideas into production-ready applications. Our Socratic AI clarifies your requirements, 
            then generates complete codebases with authentication, CRUD operations, tests, and deployment configs.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={onEnterApp}
              data-testid="hero-cta"
              className="group px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 font-mono font-semibold text-lg flex items-center justify-center gap-3 hover:shadow-lg hover:shadow-indigo-500/25 transition-all"
            >
              Start Building
              <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
            </button>
            <a
              href="#features"
              className="px-8 py-4 rounded-xl bg-white/5 border border-white/10 font-mono font-semibold text-lg flex items-center justify-center gap-2 hover:bg-white/10 transition-all"
            >
              See How It Works
            </a>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20">
          {STATS.map((stat, i) => (
            <div key={i} className="p-6 rounded-2xl bg-white/5 border border-white/10 text-center">
              <div className="text-4xl font-mono font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                {stat.value}
              </div>
              <div className="text-sm text-zinc-500 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-10 px-6 py-24 bg-zinc-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">The Genesis Pipeline</h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">
              Eight stages of intelligent processing transform your requirements into deployable code
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <div 
                  key={i}
                  className="group p-6 rounded-2xl bg-zinc-900 border border-zinc-800 hover:border-indigo-500/50 transition-all duration-300"
                >
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <Icon size={24} className="text-indigo-400" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-sm text-zinc-400 leading-relaxed">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Pipeline Visualization */}
      <section className="relative z-10 px-6 py-24">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">How It Works</h2>
            <p className="text-zinc-400">From idea to production in minutes</p>
          </div>

          <div className="grid md:grid-cols-4 gap-4">
            {[
              { step: "1", title: "Describe", desc: "Enter your app idea in plain English" },
              { step: "2", title: "Clarify", desc: "Answer AI questions to refine requirements" },
              { step: "3", title: "Generate", desc: "Watch as code is generated in real-time" },
              { step: "4", title: "Deploy", desc: "Download ZIP or deploy to cloud" }
            ].map((item, i) => (
              <div key={i} className="relative">
                <div className="p-6 rounded-2xl bg-zinc-900 border border-zinc-800 h-full">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 flex items-center justify-center font-mono font-bold mb-4">
                    {item.step}
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-zinc-400">{item.desc}</p>
                </div>
                {i < 3 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-10">
                    <ArrowRight size={24} className="text-zinc-600" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Integrations */}
      <section className="relative z-10 px-6 py-24 bg-zinc-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Connected & Ready</h2>
            <p className="text-zinc-400">All integrations configured and operational</p>
          </div>

          <div className="flex flex-wrap justify-center gap-4">
            {INTEGRATIONS.map((int, i) => (
              <div key={i} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-zinc-900 border border-zinc-800">
                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                <span className="font-mono text-sm">{int.name}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 px-6 py-32">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-6xl font-bold mb-6">
            Ready to build?
          </h2>
          <p className="text-xl text-zinc-400 mb-10">
            Stop writing boilerplate. Start shipping products.
          </p>
          <button
            onClick={onEnterApp}
            className="px-10 py-5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 font-mono font-semibold text-xl hover:shadow-lg hover:shadow-indigo-500/25 transition-all"
          >
            Launch Sovereign Genesis
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-6 py-8 border-t border-zinc-800">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Zap size={18} className="text-indigo-400" />
            <span className="font-mono text-sm text-zinc-500">Sovereign Genesis Platform v2.0</span>
          </div>
          <div className="text-xs text-zinc-600">
            Powered by Ouroboros-Lattice Core • Multi-LLM Architecture
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
