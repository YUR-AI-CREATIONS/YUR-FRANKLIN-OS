# Sovereign Genesis Platform (SGP) v2.0 - Product Requirements Document

## Original Problem Statement
Build SGP as a **meta-system that creates systems** - not industry-specific, but a universal software factory. The system must:
1. Accept ANY domain requirement via Socratic questioning
2. Self-improve through Ouroboros Loop until 99% quality convergence
3. Detect drift from intended trajectory (Frozen Spine)
4. Track milestones with Evolution Playbook
5. Manage governance, compliance, and licensing
6. Generate complete multi-page applications (Landing, App, Marketing, Governance)
7. Support cutting-edge tech stack options (AWS, K8s, Vercel, Supabase, etc.)
8. Support dual-mode LLM (cloud + local) for cost-free development
9. **Write actual code files to disk** (not just JSON artifacts)

## What's Been Implemented (Feb 2026)

### Phase 1 - MVP ✓
- [x] Socratic Pre-Prompt Engine with ambiguity detection
- [x] Glass Box 2D DAG visualization (React Flow)
- [x] Dark "Tactical Minimalism" theme

### Phase 2 - Genesis Pipeline v2.0 ✓
- [x] Ouroboros Loop (99% convergence)
- [x] Quality Gate (8 dimensions)
- [x] Frozen Spine (drift detection)
- [x] Evolution Playbook (milestones)
- [x] Governance Engine (compliance/licensing)
- [x] Multi-Kernel Orchestrator (agent tiers)

### Phase 3 - Build Engine v1 ✓
- [x] Technology Stack Registry (40+ technologies)
- [x] Build Engine (JSON code artifact generation)
- [x] Multi-stack support (Next.js, FastAPI, PostgreSQL, etc.)
- [x] Docker/Kubernetes configurations
- [x] CI/CD pipeline generation (GitHub Actions)
- [x] Deployment configs (Vercel, Railway, Render)

### Phase 4 - Dual LLM Support ✓ (Feb 6, 2026)
- [x] HybridLLMProvider abstraction layer
- [x] Cloud mode (Claude via Emergent Key)
- [x] Local mode (Ollama - Llama3.1, Mistral, etc.)
- [x] Hybrid mode with automatic fallback
- [x] Frontend LLM Mode Selector

### Phase 5 - Real Code Generation ✓ (Feb 6, 2026)
- [x] **POST /api/build/write** - Writes actual code files to disk
- [x] **GET /api/build/tree** - Returns file tree structure
- [x] Generated files saved to `/app/generated/{project_name}/`
- [x] Creates complete project structure:
  - `backend/` - FastAPI app (main.py, models.py, routes.py, Dockerfile)
  - `frontend/` - Next.js/React app (page.tsx, layout.tsx, Dockerfile)
  - `database/` - SQL schemas
  - `.github/workflows/` - CI/CD pipelines
  - `docker-compose.yml`
  - `sgp-manifest.json`

## API Endpoints v2.0

### Core
- `POST /api/analyze` - Socratic analysis
- `POST /api/resolve` - Answer ambiguities

### Genesis Pipeline
- `POST /api/genesis/project/init` - Initialize project
- `POST /api/genesis/quality/assess` - Quality gate
- `POST /api/genesis/ouroboros/execute` - Convergence loop

### Build Engine
- `POST /api/build/generate` - Generate code artifacts (14+ files)
- `POST /api/build/write` - **Write files to disk**
- `GET /api/build/tree` - Get file tree structure
- `GET /api/build/artifacts/{id}` - Get artifact list
- `GET /api/build/artifact/{id}/{artifact_id}` - Get file content
- `GET /api/build/deployment/{id}` - Deployment config

### LLM
- `GET /api/llm/status` - Provider status
- `POST /api/llm/config` - Switch modes

### Tech Stack
- `GET /api/stack/catalog` - Technology catalog

## Generated Project Structure
```
/app/generated/{ProjectName}/
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── models.py       # Pydantic models from data model
│   │   └── routes.py       # API endpoints from contracts
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── layout.tsx      # Next.js layout
│   │   └── page.tsx        # Home page
│   ├── package.json
│   ├── tailwind.config.ts
│   └── Dockerfile
├── database/
│   └── schema.sql          # PostgreSQL/Supabase schema
├── .github/workflows/
│   ├── ci.yml              # CI pipeline
│   └── deploy.yml          # Deployment pipeline
├── docker-compose.yml
└── sgp-manifest.json       # Build metadata
```

## Testing Status
- Backend: 100% pass rate across all endpoints
- Build Engine: 14+ files generated, all valid syntax
- File Writing: Verified files exist on disk
- End-to-end: Full workflow tested

## Prioritized Backlog

### P0 - Critical
- [ ] Deploy generated code to cloud (one-click Vercel/Railway)
- [ ] Live preview of generated applications

### P1 - High Priority  
- [ ] More sophisticated code generation (CRUD operations, auth)
- [ ] Streaming LLM responses
- [ ] Marketing content generation

### P2 - Medium Priority
- [ ] Visual tech stack selector UI
- [ ] Download generated project as ZIP
- [ ] Template library

## Usage Flow
1. Enter requirements in Socratic Terminal
2. Answer clarification questions (ambiguities)
3. Reach 99% confidence score
4. Select tech stack (or use defaults)
5. `POST /api/build/generate` - Creates artifacts
6. `POST /api/build/write` - **Writes actual code to disk**
7. Files available at `/app/generated/{project_name}/`
