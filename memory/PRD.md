# FRANKLIN OS - Product Requirements Document

## Original Problem Statement
Build "FRANKLIN OS," a sophisticated, VS Code-style IDE for building, certifying, and deploying enterprise applications with a "galactic liquid glassmorphism" cyberpunk aesthetic. The core mission is to create a fully functional software factory where a user interacts with an AI agent (Franklin) to define a project, which is then executed by a team of specialized agents (Grok, Genesis, Architect, etc.).

## User's Vision
- Chrome FRANKLIN title with shimmer effect
- Galactic starfield background with twinkling stars
- 3-column IDE layout: Franklin (left) | Code Area (center) | Grok (right)
- Transparent, resizable panels
- Ghost "FRANKLIN" text visible through panels
- Terminal at bottom center
- **Consistent Galaxy Black Glassmorphism across ALL pages**
- **Franklin chat that ACTUALLY BUILDS and delivers code**
- **FRANKLIN OS Certification for every build**

## Current Status: WORKING ✅

### What Works NOW:
1. **Tell Franklin what to build** → Type "build me X" in Franklin prompt
2. **Genesis agents work on it** → Genesis, Architect, Implementer, Healer
3. **Code is generated** → Displayed in center CODE panel
4. **FRANKLIN OS CERTIFIED** → Badge shows certification status
5. **COPY/DOWNLOAD** → Get the code immediately
6. **Workflow page** → Navigate pipeline with chat commands

## Core Architecture
```
/app/
├── backend/
│   ├── server.py              # Main FastAPI app
│   ├── franklin_routes.py     # Core API routes
│   ├── franklin_orchestrator.py # Genesis→Architect→Implementer→Healer pipeline
│   ├── payment_routes.py      # Stripe payment integration
│   └── grok_agent.py          # Grok chat agent
├── frontend/
│   └── src/
│       ├── App.js             # Main app with 3 pages
│       └── components/
│           └── LandingPage.jsx # Login + Pricing
└── memory/
    └── PRD.md
```

## What's Been Implemented

### February 2026 - Build System WORKING

**The Build Pipeline:**
- [x] User types "build me X" in Franklin prompt
- [x] Frontend detects build intent and calls `/api/build-orchestrator/build`
- [x] Backend orchestrator runs 4-agent pipeline:
  - Genesis: Analyzes requirements, creates specification
  - Architect: Designs system architecture
  - Implementer: Writes production-ready code
  - Healer: Reviews and validates code quality
- [x] Franklin signs off with GENESIS_CERTIFIED stamp
- [x] Code displayed in center panel
- [x] COPY and DOWNLOAD buttons available
- [x] Terminal shows real-time progress
- [x] Certification badge in header

**LLM Integration:**
- [x] Uses Anthropic Claude via Emergent integration
- [x] Fallback to XAI if needed
- [x] 120s timeout for longer builds

### Previous Features (Still Working)
- [x] 3-page application: Landing → IDE → Workflow
- [x] Galaxy Black Glassmorphism on all pages
- [x] Sparkly twinkling stars background
- [x] Ghost "FRANKLIN" text
- [x] Workflow page with functional chat commands
- [x] Stripe pricing integration (UI)

## API Endpoints

### Build APIs
- `POST /api/build-orchestrator/build` - Build something (mission payload)
- `POST /api/build-orchestrator/chat` - Chat with Franklin

### Payment APIs
- `GET /api/payments/packages` - Get subscription packages
- `POST /api/payments/checkout` - Create Stripe checkout session

## Backlog / Future Tasks

### P1 - High Priority
- [ ] Persist build results to database (survive page refresh)
- [ ] Implement full Stripe authentication
- [ ] Add code execution sandbox (run the generated code)

### P2 - Medium Priority
- [ ] OCTANT FOUNDRY 8-Gate Architecture (user blueprint)
- [ ] Escrow payment model
- [ ] Whiteboard/Workspace views
- [ ] Refactor App.js into smaller components

## Technical Notes
- Frontend: React with Tailwind CSS
- Backend: FastAPI with MongoDB
- LLM: Claude (Anthropic) via Emergent integration
- Payments: Stripe via emergentintegrations
- Workflow: ReactFlow for visual pipelines

## Design Philosophy
- **Truth**: No hidden actions, all processes visible in terminal
- **Trust**: Code is generated and certified before delivery
- **Transparency**: Real-time feedback, no black boxes
