# Franklin OS / Sovereign Genesis Platform - Product Requirements Document

## Original Problem Statement
Build a "Sovereign Genesis Platform" (SGP), now branded as "Franklin OS" - a 100% enterprise-grade, end-to-end software factory. The core of the application is a "Genesis Pipeline" that visually builds a workflow, generates code for multi-page applications, and handles specifications. The system should provide a real-time, visual build experience with automatic layout and per-stage execution controls.

## Design Theme: FRANKLIN OS
- **Aesthetic**: Cyberpunk/Neural network with dark navy background
- **Primary Colors**: Cyan (#00C8FF), Teal (#00FFD4)
- **Background**: Dark navy gradient (#0a1628 → #0d1f3c)
- **Visual Effects**: 
  - Animated plexus network background
  - Animated wave patterns
  - Ghost text watermarks
  - Tracer animations on active elements

## User Personas
1. **Enterprise Developers** - Need to rapidly generate production-ready codebases
2. **Solution Architects** - Want to visualize and control the software generation pipeline
3. **Technical Leads** - Require quality gates and compliance checks

## Core Requirements
1. Visual pipeline with 8 stages: Inception → Specification → Architecture → Construction → Validation → Evolution → Deployment → Governance
2. Real-time build visualization with "spider web" workflow expansion
3. Socratic AI that asks clarifying questions before generating code
4. Multi-LLM support (OpenAI, Anthropic, xAI, Google)
5. Code generation with downloadable ZIP output
6. Quality assessment and Ouroboros loop for iterative improvement

## Tech Stack
- **Frontend**: React, React Flow, TailwindCSS, Dagre (auto-layout)
- **Backend**: FastAPI, Python
- **Database**: MongoDB (sessions), Supabase (project data)
- **AI**: Multi-provider LLM architecture

---

## Implementation Status

### ✅ Completed (December 2025)

#### UI/UX Improvements (Latest Session)
- **Tracer Animation**: Added glowing border animation that traces around the active stage node
- **Global Loading Indicator**: Added top-center loading indicator showing "Processing [stage]..."
- **Collapsible Questions Panel**: Made the clarification panel collapsible with click-to-expand
- **Better Zoom Controls**: Set minZoom=0.1, maxZoom=2 for better canvas navigation
- **Improved Auto-Layout**: Better dagre spacing (nodesep=100, ranksep=150) and positioning
- **Pipeline Panel Hidden by Default**: No longer blocks the canvas view
- **Visual Node Processing State**: Nodes show "Processing..." text when active

#### Previous Sessions
- Full workflow visualization with spider web effect
- Per-stage "RUN" buttons on each pipeline node
- Auto-layout using dagre library
- AI Recommendation highlighting (first option marked with AI badge)
- "Auto Build" feature for autonomous execution
- Landing page integration
- Deployment configuration (Render, Vercel)
- Error handling for React rendering issues

### 🔄 In Progress
- User verification of UI improvements

### 📋 Backlog

#### P1 - High Priority
- Deploy to Production (Render + Vercel)
- Implement Checkpoints/Save Progress feature

#### P2 - Medium Priority
- Refactor `server.py` into `/routes/` structure
- Refactor `App.js` state management (Context or Zustand)
- Address code quality warnings (ruff linting)
- Consider WebSockets/SSE for true real-time updates

---

## Key Files
- `/app/frontend/src/App.js` - Main application logic
- `/app/frontend/src/App.css` - Global styles including tracer animations
- `/app/frontend/src/components/nodes/StageNode.jsx` - Pipeline stage node component
- `/app/frontend/src/components/panels/ClarificationPanel.jsx` - Questions panel
- `/app/backend/server.py` - FastAPI endpoints

## API Endpoints
- `POST /api/analyze` - Socratic analysis
- `POST /api/resolve` - Submit answers to questions
- `POST /api/genesis/project/init` - Initialize project
- `POST /api/genesis/quality/assess` - Quality assessment
- `POST /api/build/enhanced` - Generate code
- `GET /api/build/download-zip` - Download generated code
