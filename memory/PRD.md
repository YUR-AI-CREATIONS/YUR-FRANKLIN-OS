# FRANKLIN OS - Product Requirements Document

## Original Problem Statement
Build "FRANKLIN OS," a sophisticated IDE for building and certifying enterprise applications with a "galactic liquid glassmorphism" cyberpunk aesthetic. Users interact with AI agent (Franklin) to define projects which are then built by specialized agents.

## User's Core Requirement
**"I literally want to tell Franklin to build me something and he build it and deliver it with the Franklin OS certification and I can run it and see it in action"**

## What's Been Implemented

### December 2025 - COMPLETE WORKFLOW PIPELINE ✅

**Item #1: 500MB File Upload**
- [x] Real API at `/api/upload/files`
- [x] Drag-and-drop support
- [x] Files stored to `/app/uploads` with checksums

**Item #2: File Analysis & TODO Extraction**
- [x] Real API at `/api/analyze/files`
- [x] LLM-based analysis with fallback scanner
- [x] Extracts TODO/FIXME/BUG comments from code

**Item #3: User Verification**
- [x] Full verification UI in VERIFICATION tab
- [x] Add/Edit/Delete tasks
- [x] Priority selection (high/medium/low)
- [x] Category selection (requirement/feature/bug/etc.)
- [x] CONFIRM button to proceed

**Item #4: TODO Verification (UI Complete)**
- [x] Summary showing task counts by priority
- [x] Editable task descriptions
- [x] Source file and line references displayed

**Item #5: Unified Workflow Generation**
- [x] Real API at `/api/workflow/generate`
- [x] Converts TODOs into phased workflow
- [x] Task dependencies and deliverables
- [x] Recommended file structure per language
- [x] Architecture notes
- [x] WORKFLOW tab displays full workflow
- [x] "PROCEED TO FILE STRUCTURE" button

### Earlier - BUILD WITH TECH STACK ✅

**Tech Stack Selection:**
- [x] Tech stack selector in header (Python, JavaScript, TypeScript, Go, Rust)
- [x] Stack passed to build API for targeted code generation

**Build System:**
- [x] Fast Build API generates production-ready code for selected stack
- [x] 8-Gate Certification runs and returns real scores
- [x] Copy and Download functionality

**Pages:**
- [x] Landing Page (YUR-AI branding)
- [x] IDE Page (Franklin chat + code panel + verification + workflow + certification)

## Architecture
```
/app/
├── backend/
│   ├── server.py              # Main FastAPI app
│   ├── upload_routes.py       # File upload API
│   ├── analyze_routes.py      # File analysis API  
│   ├── workflow_routes.py     # Workflow generation API (NEW)
│   ├── simple_build_routes.py # Code generation + certification
│   └── trinity_spine.py       # LLM provider
├── frontend/
│   └── src/
│       ├── App.js             # Router: Landing + IDE
│       └── components/
│           └── FranklinIDE.jsx # Main IDE component
└── uploads/                   # User file storage
```

## API Endpoints

### Core Workflow APIs
- `POST /api/upload/files` - Upload files (up to 500MB)
- `POST /api/analyze/files` - Analyze files for TODOs
- `POST /api/workflow/generate` - Generate unified workflow
- `POST /api/simple-build/build` - Code generation
- `POST /api/simple-build/certify` - 8-Gate certification

## Backlog

### P0 - Next Up
- [ ] Item #6: Industry standard file tree per language
- [ ] Item #7: Add architecture documentation
- [ ] Make Trust Vault show REAL API status

### P1 - High Priority
- [ ] Working terminal with real command execution
- [ ] Deployment config generation (Docker/K8s)
- [ ] .env file generation

### P2 - Medium Priority
- [ ] Real-time connector status
- [ ] Auto-rotate keys
- [ ] Domain/DNS management
