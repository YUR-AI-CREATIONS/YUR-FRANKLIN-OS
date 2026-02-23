# FRANKLIN OS - Product Requirements Document

## Original Problem Statement
Build "FRANKLIN OS," a sophisticated, VS Code-style IDE for building, certifying, and deploying enterprise applications with a "galactic liquid glassmorphism" cyberpunk aesthetic. The core mission is to create a fully functional software factory where a user interacts with an AI agent (Franklin) to define a project, which is then executed by a team of specialized agents (Grok, Genesis, Architect, etc.).

## User's Core Requirement (CRITICAL)
**"I literally want to tell Franklin to build me something and he fucking build it and deliver it and the full core code format with the Franklin OS certification and I can run it and I can see it in action"**

## What's Been Implemented

### February 2026 - BUILD FUNCTIONALITY WORKING ✅

**Core Build System:**
- [x] **Fast Build API** (`/api/build-orchestrator/fast-build`) - generates production-ready code in a single LLM call
- [x] **Spec → Architecture → Code → Certification** pipeline
- [x] **Real working code** delivered - not pseudocode, not placeholders
- [x] **Franklin OS Certification** with signed approval from all agents
- [x] **Copy and Download** functionality for generated code
- [x] **Multiple tabs** (CODE, SPEC, ARCHITECTURE) to view all deliverables

**Frontend:**
- [x] User types "build me X" → Franklin executes build
- [x] Real-time terminal output showing build progress
- [x] Generated code displayed in center panel
- [x] Certification badge shows agents involved
- [x] Download button to get the code

**Visual Consistency:**
- [x] Galaxy Black Glassmorphism on ALL pages
- [x] Ghost FRANKLIN text
- [x] Sparkly star background

### Previous Session Work

**UI/UX:**
- [x] 3-page application: Landing → IDE → Workflow
- [x] Landing page with login and Stripe pricing
- [x] IDE page with Franklin/Grok panels
- [x] Workflow page with Genesis Pipeline visualization

**Stripe Integration:**
- [x] Backend payment routes
- [x] 4 subscription tiers

## API Endpoints

### Build APIs (CORE)
- `POST /api/build-orchestrator/fast-build` - **MAIN BUILD** - Single call, full code delivery
- `POST /api/build-orchestrator/build` - Full multi-agent build (slower)
- `POST /api/build-orchestrator/chat` - Chat with Franklin
- `GET /api/build-orchestrator/whiteboard` - View all sections

### Other APIs
- `POST /api/grok/chat` - Direct Grok conversation
- `GET /api/payments/packages` - Subscription tiers
- `POST /api/payments/checkout` - Stripe checkout

## Architecture

```
/app/
├── backend/
│   ├── server.py              # Main FastAPI
│   ├── franklin_orchestrator.py # BUILD ENGINE - fast_build() method
│   ├── franklin_routes.py     # API routes including /fast-build
│   └── ...
├── frontend/
│   └── src/
│       ├── App.js             # IDE with build UI
│       └── components/
│           └── LandingPage.jsx
└── memory/
    └── PRD.md
```

## How It Works

1. User types: "build me a todo list API"
2. Frontend detects "build" keyword → calls `/api/build-orchestrator/fast-build`
3. Backend calls Grok with comprehensive prompt
4. LLM generates: Specification, Architecture, Implementation, Usage Guide
5. Response parsed and displayed in center panel
6. Code is certified by Franklin with governance log
7. User can COPY or DOWNLOAD the code

## Backlog

### P1 - High Priority
- [ ] Stripe user authentication (currently UI-only)
- [ ] Chat persistence to database
- [ ] Code execution/preview sandbox

### P2 - Medium Priority
- [ ] Whiteboard collaborative view
- [ ] Workspace view
- [ ] Multiple file generation
- [ ] Git integration

### P3 - Refactoring
- [ ] Split App.js into components
- [ ] Split server.py into modules

## Technical Notes
- Frontend: React + Tailwind CSS
- Backend: FastAPI + MongoDB
- LLM: Grok (XAI) via direct API
- Payments: Stripe
