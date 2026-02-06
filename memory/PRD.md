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

## Technology Stack Registry

### Cloud Providers
- AWS, GCP, Azure

### Platform as a Service
- Vercel, Railway, Render, Fly.io

### Container Orchestration
- Kubernetes, Docker, Docker Swarm

### Databases
- PostgreSQL, Supabase, MongoDB, PlanetScale, Neon, CockroachDB

### Cache
- Redis, Upstash, Memcached

### Authentication
- Auth0, Clerk, Firebase Auth, Supabase Auth

### Frontend Frameworks
- Next.js, React, Vue.js, Svelte, Astro

### Backend Frameworks
- FastAPI, Express.js, NestJS, Django, Go (Gin/Echo), Rust (Actix/Axum)

### CSS Frameworks
- Tailwind CSS, shadcn/ui

### CI/CD
- GitHub Actions, GitLab CI/CD

### AI/ML
- OpenAI API, Anthropic Claude, LangChain, Ollama (local)

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

### Phase 3 - Build Engine ✓
- [x] Technology Stack Registry (40+ technologies)
- [x] Build Engine (JSON code artifact generation)
- [x] Multi-stack support (Next.js, FastAPI, PostgreSQL, etc.)
- [x] Docker/Kubernetes configurations
- [x] CI/CD pipeline generation (GitHub Actions)
- [x] Deployment configs (Vercel, Railway, Render)

### Phase 4 - Dual LLM Support ✓ (Feb 6, 2026)
- [x] HybridLLMProvider abstraction layer (`llm_providers.py`)
- [x] Cloud mode (Claude via Emergent Key)
- [x] Local mode (Ollama - Llama3.1, Mistral, CodeLlama, etc.)
- [x] Hybrid mode with automatic fallback
- [x] LLM configuration API (`POST /api/llm/config`)
- [x] LLM status & health check (`GET /api/llm/status`)
- [x] Local model listing (`GET /api/llm/models`)
- [x] LLM test endpoint (`POST /api/llm/test`)
- [x] Socratic engine updated to use hybrid LLM
- [x] Response metadata includes provider/model info
- [x] **Frontend LLM Mode Selector** (Cloud/Local/Hybrid toggle)
- [x] Auto-fallback to cloud when local unavailable

## API Endpoints v2.0

### Core
- `POST /api/analyze` - Socratic analysis (returns llm_info)
- `POST /api/resolve` - Answer ambiguities (returns llm_info)

### Genesis
- `POST /api/genesis/project/init` - Initialize project
- `POST /api/genesis/quality/assess` - Quality gate
- `POST /api/genesis/ouroboros/execute` - Convergence loop

### Governance
- `POST /api/governance/compliance/audit` - Compliance checks
- `POST /api/governance/license/configure` - License generation

### Tech Stack
- `GET /api/stack/catalog` - Full technology catalog
- `GET /api/stack/category/{cat}` - Technologies by category
- `GET /api/stack/tech/{id}` - Technology details
- `POST /api/stack/validate` - Validate stack compatibility

### Build
- `POST /api/build/configure` - Configure tech stack
- `POST /api/build/generate` - Generate project code
- `GET /api/build/artifacts/{id}` - Get generated files
- `GET /api/build/deployment/{id}` - Deployment config

### LLM
- `GET /api/llm/status` - Provider status, config, recommended models
- `POST /api/llm/config` - Switch between cloud/local/hybrid modes
- `GET /api/llm/models` - List available local models
- `POST /api/llm/test` - Test LLM generation

## Testing Status
- Backend: 95-100% pass rate across 21+ endpoint tests
- Frontend: 100% verified via Playwright automation
- End-to-end: Full Socratic workflow tested

## Prioritized Backlog

### P0 - Critical
- [ ] Deploy generated code to cloud (Vercel/Railway/AWS)
- [ ] Live preview of generated applications

### P1 - High Priority
- [ ] Build Engine Phase 2: Generate actual code files (not just JSON artifacts)
- [ ] Streaming LLM responses
- [ ] Marketing content generation (AI copy)
- [ ] More backend templates (NestJS, Django, Go)

### P2 - Medium Priority
- [ ] Visual tech stack selector UI
- [ ] Template library
- [ ] Multi-user collaboration

### P3 - Low Priority
- [ ] Session persistence (refactor in-memory to MongoDB)
- [ ] Drift detection improvements
- [ ] React Flow memoization optimization

## Next Tasks
1. Build Engine Phase 2: Convert JSON artifacts to actual code files
2. Add deployment automation
3. Build visual tech stack selector
4. Implement live preview

## Local LLM Setup Instructions
To use the free, local LLM mode:
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.1:8b

# Start Ollama (usually auto-starts)
ollama serve

# Configure SGP to use local mode via UI or API
# Click "Cloud" button in header → Select "Local" or "Hybrid"
# OR curl -X POST /api/llm/config -d '{"mode": "local"}'
```

Recommended models:
- General: `llama3.1:8b` (4.7GB, fast, high quality)
- Coding: `codellama:13b` (7.4GB, code-specialized)
- Reasoning: `phi3:14b` (7.9GB, strong reasoning)
