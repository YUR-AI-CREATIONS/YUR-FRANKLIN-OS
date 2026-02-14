# FRANKLIN OS - Product Requirements Document

## Original Problem Statement
Build "FRANKLIN OS," a sophisticated, VS Code-style IDE for building, certifying, and deploying enterprise applications with a "galactic liquid glassmorphism" cyberpunk aesthetic. The user demands a fully functional software factory where telling the AI to "build X" results in actual generation of certified, downloadable source code - NOT mocked or simulated features.

## User Persona
Enterprise software developers who need a streamlined, AI-powered development environment that can:
- Generate real, production-ready code from natural language descriptions
- Provide 8-gate quality certification
- Allow download of generated projects as ZIP files

## Core Requirements

### P0 - Critical (Must Have)
1. **Real Code Generation** - When user says "build X", real code files must be created on the server ✅ DONE
2. **LLM Integration** - Reliable LLM calls that don't timeout ✅ DONE (Multi-provider fallback)
3. **File Download** - Users must be able to download generated code as ZIP ✅ DONE
4. **8-Gate Certification** - Real validation of generated code quality ⏳ EXISTS (needs E2E test)

### P1 - High Priority
1. **Chat Persistence** - Conversations should survive page refresh
2. **Stripe Subscription Gating** - User authentication and subscription management
3. **Code Refactoring** - Break down monolithic App.js and server.py

### P2 - Medium Priority
1. **Supabase Integration** - Fix PostgreSQL connection (needs valid credentials)
2. **Whiteboard View** - Collaborative review feature
3. **Workspace View** - Project management view

### P3 - Low Priority
1. **OCTANT FOUNDRY** - Financial models (Escrow, Social Currency)
2. **IDE Layout** - Match original wireframe proportions

---

## What's Been Implemented (Feb 14, 2026)

### Simple Build System (`/api/build/create`)
- **New endpoint that takes a single prompt and generates real files**
- Multi-provider LLM fallback: Anthropic → XAI → OpenAI → Google
- Parses code blocks from LLM response into actual files
- Creates project directory on server disk
- Generates downloadable ZIP file
- Returns file contents, stats, and tree structure

### API Endpoints Working
- `POST /api/build/create` - Create build from prompt
- `GET /api/build/{id}` - Get build info
- `GET /api/build/{id}/file/{path}` - Get specific file content
- `GET /api/build/{id}/download` - Download as ZIP
- `GET /api/build/health/check` - Service health check

### Frontend Integration
- IDE page calls `/api/build/create` when user types build request
- Generated code displayed in editor
- "SEND TO CERTIFICATION" and "DOWNLOAD" buttons available
- Terminal shows real-time build progress

---

## Architecture

```
/app/
├── backend/
│   ├── simple_build.py          # NEW: Core build service (LLM + file generation)
│   ├── simple_build_routes.py   # NEW: API routes for build
│   ├── server.py                # Main FastAPI app (monolith - needs refactor)
│   ├── certification_engine.py  # 8-gate validation
│   └── .env                     # API keys
├── frontend/
│   └── src/
│       └── App.js               # Main app (monolith - needs refactor)
└── generated_projects/          # Where real files are created
```

---

## Known Issues

1. **Monolithic Files** - App.js and server.py are too large
2. **Supabase Connection** - PostgreSQL auth failing (using MongoDB fallback)
3. **Chat Persistence** - State lost on page refresh
4. **Stripe Integration** - UI exists but not fully functional

---

## Test Results

### Feb 14, 2026
- ✅ Build endpoint creates real files on disk
- ✅ LLM calls succeed (Anthropic provider)
- ✅ ZIP download works
- ✅ Frontend displays generated code
- ⏳ 8-gate certification needs E2E test
