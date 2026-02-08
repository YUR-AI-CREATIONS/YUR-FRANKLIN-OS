# FRANKLIN OS - Product Requirements Document

## Original Problem Statement
Build a "Sovereign Genesis Platform" (SGP), evolved into "FRANKLIN OS" - a sophisticated, VS Code-style IDE. This platform is a complete software factory designed to build, certify, and deploy enterprise-grade applications. The system architecture is multi-layered, encompassing an AI agent academy, tiered agent system, human-AI governance, self-healing code generation engine (Grok), and quality assurance/certification pipeline.

**Design Aesthetic:** Galactic liquid glassmorphism cyberpunk
**Core Principles:** Truth, Trust, Transparency, Zero Hallucination, Complete Auditable Trail

---

## Architecture Overview

### Frontend (React)
- **Landing Page** (`/`): Space-themed entry page with login/command inputs
- **IDE Page** (`/ide`): Main FRANKLIN OS interface with:
  - Left Panel: Interface mode selector & project file tree
  - Center: Scrolling output area for commands and responses
  - Right Panel: Tabs for Agents, Bots, Academy data
  - Bottom Panel: Build categories (Frontend/Backend/Database/Deploy) & command input
- **Workflow Page** (`/workflow`): React Flow visualization of build pipeline

### Backend (FastAPI)
Core Modules:
- `grok_agent.py`: Self-healing agent using XAI API
- `agent_marketplace.py`: Catalog of elite AI agents
- `bot_tiers.py`: 4-tier operational bot governance
- `agent_academy.py`: AI training/certification system
- `franklin_runtime.py`: DPOA, PQC simulation, security layers
- `quality_gates.py`: 5-dimensional quality gate & certification
- `marketing_content.py`: AI marketing copy generator
- `deployment_engine.py`: Controlled deployment system

---

## Implemented Features ✅

### Session Date: 2026-02-08

1. **Full Backend Ecosystem**
   - Grok Self-Healing Agent (XAI API integrated)
   - Agent Marketplace & Bot Tiers systems
   - AI Agent Academy with training programs
   - Franklin Sovereign Runtime (DPOA/PQC)
   - 5-Dimensional Quality Gate & Certification
   - Marketing Content Generator
   - Controlled Deployment Engine

2. **3-Page Frontend Application**
   - Landing page with space theme
   - IDE with functional panels and tabs
   - Electric Workflow visualization

3. **API Integration**
   - All backend APIs connected to frontend
   - Real-time data fetching for agents, bots, academy

4. **Button Functionality** (Verified 2026-02-08)
   - All IDE buttons working correctly
   - Interface mode switching functional
   - Tab navigation working
   - Command input and send working
   - Category expansion working
   - File tree navigation working
   - Workflow navigation working

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/franklin/dashboard` | GET | Sovereign runtime status |
| `/api/marketplace/agents/summary` | GET | Elite agents list |
| `/api/bots/tiers` | GET | Bot tier information |
| `/api/academy/programs` | GET | Training programs |
| `/api/quality/status` | GET | Quality gate status |
| `/api/quality/build/certify` | POST | Start certified build |
| `/api/grok/genesis` | POST | Run Grok self-healing genesis |
| `/api/marketing-content-gen/generate` | POST | Generate marketing content |
| `/api/deployment/deploy` | POST | Manage deployment |
| `/api/analyze` | POST | Analyze user prompt |

---

## Upcoming Tasks

### P0 (High Priority)
- [ ] Full End-to-End Build Test: Complete project build through all 8 phases
- [ ] User domain deployment: `franklin-os.com`, `YUR_AI.com`

### P1 (Medium Priority)
- [ ] Refactor `server.py` into organized routes/services
- [ ] Refactor `App.js` into smaller components

### P2 (Low Priority)
- [ ] Address code quality warnings (ruff linting)
- [ ] Add comprehensive error handling
- [ ] Implement user authentication flow

---

## Technical Stack
- **Frontend:** React, React Flow, TailwindCSS
- **Backend:** Python, FastAPI
- **AI/LLM:** XAI/Grok API
- **Security:** PQC simulation, Merkle Tree auditing

---

## Credentials Required
- `XAI_API_KEY`: Present in `/app/backend/.env`

---

## Known Issues
- React Flow nodeTypes warning (non-breaking)
- Code quality warnings from ruff (cosmetic)

---

## File Structure
```
/app/
├── backend/
│   ├── agent_academy.py
│   ├── agent_marketplace.py
│   ├── bot_tiers.py
│   ├── deployment_engine.py
│   ├── deployment_routes.py
│   ├── franklin_runtime.py
│   ├── franklin_routes.py
│   ├── grok_agent.py
│   ├── marketing_content.py
│   ├── marketing_routes.py
│   ├── quality_gates.py
│   ├── quality_routes.py
│   └── server.py
├── frontend/
│   └── src/
│       ├── App.js
│       ├── App.css
│       └── components/
│           ├── LandingPage.jsx
│           ├── ParticleBackground.jsx
│           ├── nodes/
│           └── panels/
└── memory/
    └── PRD.md
```
