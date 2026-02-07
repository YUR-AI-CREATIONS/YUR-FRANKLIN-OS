# FRANKLIN OS - Sovereign Genesis Platform

## Product Requirements Document (PRD)

### Original Problem Statement
Build "FRANKLIN OS," a sophisticated, VS Code-style integrated development environment that serves as a 100% enterprise-grade, end-to-end software factory. The platform features a multi-panel layout with:
- Collapsible/sliding sections for project files, chat, agent configuration, and build options
- Interactive, real-time build process where users are always in control
- Dynamic file tree and "electric" workflow nodes on an infinite canvas
- "Galactic liquid glassmorphism" cyberpunk aesthetic throughout

### User Personas
1. **Enterprise Developers** - Building complex software systems with AI assistance
2. **AI Agent Operators** - Managing and deploying tiered autonomous bots
3. **Business Stakeholders** - Overseeing project governance and compliance

### Core Requirements

#### ✅ Implemented Features

**Landing Page**
- Chrome "FRANKLIN" text with shimmer animation
- Space-themed background with animated stars and laser beams
- Status badges (Garage Online, Oracle Online, Franklin Online, Agents Online, Bots Online)
- Login form and entry CTA

**Main IDE Interface (Page 2)**
- Three-panel layout (Left, Right, Bottom) surrounding center canvas
- Left Panel: Interface modes (NEURAL_CHAT, VISION_AI, CODE_EDITOR, GENESIS, AGENT_BUILDER, WORKFLOW)
- Right Panel: Three tabs (AGENTS, BOTS, ACADEMY) with real data
- Bottom Panel: Build categories (FRONTEND, BACKEND, DATABASE, DEPLOY) with subcategories
- Center: 6-7" scrolling output area for Grok agent responses
- Status bar showing SENTINEL, PQC, AUDIT, AGENTS, BOTS status
- Command input with /genesis and /build commands

**Backend Systems**
- Franklin Sovereign Runtime (PQC keys, DPOA, Sentinel kill-switch, audit logging)
- Neo3 AI Agent Academy (7 training programs, Human-AI Oversight Board, certifications)
- 4-Tier Bot System (Scout → Qualifier → Pipeline → Elite Scalar)
- Agent Marketplace (5 elite agents with metrics, pricing, success stories)
- Grok Self-Healing Agent (Architect → Engineer → Healer pattern)

**API Endpoints**
- `/api/franklin/*` - Runtime, DPOA, PQC, Sentinel, Audit
- `/api/academy/*` - Programs, Board, Enrollments, Certifications
- `/api/bots/*` - Tiers, Bot instances, Task management
- `/api/marketplace/*` - Elite agent profiles, Search, Comparison
- `/api/grok/*` - Genesis loop, Tasks, Output streaming
- `/api/analyze` - Socratic analysis of prompts
- `/api/build/*` - Code generation and project building

### Architecture

```
/app/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── franklin_runtime.py    # Sovereign Runtime (PQC, DPOA, Sentinel)
│   ├── agent_academy.py       # Training & Certification system
│   ├── bot_tiers.py           # 4-Tier Bot system
│   ├── agent_marketplace.py   # Elite Agent profiles
│   ├── grok_agent.py          # Self-healing Grok agent
│   ├── franklin_routes.py     # All FRANKLIN OS API routes
│   └── ... (existing modules)
├── frontend/
│   └── src/
│       ├── App.js             # Main FRANKLIN OS IDE
│       ├── components/
│       │   └── LandingPage.jsx
│       ├── App.css
│       └── index.css
└── memory/
    └── PRD.md
```

### Tech Stack
- **Frontend**: React, React Flow, TailwindCSS
- **Backend**: Python, FastAPI
- **Database**: MongoDB (sessions), Supabase (PostgreSQL)
- **AI/LLM**: Multi-provider (Grok/XAI, Claude, GPT, Gemini)
- **Security**: Post-Quantum Cryptography (Kyber, Dilithium simulation)

---

## Changelog

### 2025-12-07 - Major Implementation Phase

**Backend Systems Created:**
- `franklin_runtime.py` - PQC Key Vault, Audit Log, Sentinel, DPOA Manifest
- `agent_academy.py` - 7 elite training programs with Human-AI Board
- `bot_tiers.py` - 4-tier autonomous bot system
- `agent_marketplace.py` - 5 elite agent profiles with full details
- `grok_agent.py` - Self-healing agent with Architect→Engineer→Healer loop
- `franklin_routes.py` - Complete API routes for all systems

**Frontend Implementation:**
- Completely rebuilt App.js with new FRANKLIN OS layout
- Center scrolling output area (6-7" wide)
- Real-time data loading from all backend systems
- AGENTS, BOTS, ACADEMY tabs in right panel
- Build categories with subcategories
- Status bar showing system health
- Command input with /genesis and /build commands

**API Integration:**
- `/api/franklin/dashboard` - Combined system status
- `/api/marketplace/agents/summary` - Elite agent cards
- `/api/bots/tiers` - Bot tier configurations
- `/api/academy/programs` - Training program listings

---

## Roadmap

### P0 - Critical (Next Sprint)
1. ~~Integrate all backend systems~~ ✅
2. ~~Build AGENTS, BOTS, ACADEMY tabs~~ ✅
3. ~~Implement center scrolling output~~ ✅
4. Create Electric Workflow page (Page 3)
5. Wire up /genesis command to Grok agent
6. Implement sliding left panel file tree with glow effect

### P1 - Important
1. LLM Model Selector UI (Grok, GPT, Claude, Gemini)
2. Agent Builder configuration interface
3. Real-time workflow visualization on canvas
4. Interactive modal build process
5. Evolving file tree during builds

### P2 - Nice to Have
1. Website/Landing Page builder category
2. CODE_EDITOR mode with Monaco
3. Agent training enrollment UI
4. Bot deployment interface
5. Board approval workflow UI

### P3 - Future
1. Production deployment optimization
2. Refactor server.py into routes directory
3. Refactor App.js into smaller components
4. Multi-user support
5. Team collaboration features

---

## Known Issues
1. Grok API requires XAI_API_KEY (currently using fallback)
2. Local LLM (Ollama) not available in cloud environment
3. Code quality warnings in backend (bare except clauses)

---

## Testing Status
- Landing page: ✅ Visual verification
- Main IDE: ✅ Visual verification
- AGENTS tab: ✅ Loads marketplace agents
- BOTS tab: ✅ Loads tier configurations
- ACADEMY tab: ✅ Loads training programs
- API endpoints: ✅ All returning correct data

---

## Credentials & Environment
- All API keys stored in `/app/backend/.env`
- Supabase connected
- MongoDB connected
- Multi-provider LLM support configured

---

**Last Updated**: 2025-12-07
**Status**: MVP Complete - Ready for User Testing
