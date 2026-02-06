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
- OpenAI API, Anthropic Claude, LangChain

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
- [x] Build Engine (code generation)
- [x] Multi-stack support (Next.js, FastAPI, PostgreSQL, etc.)
- [x] Docker/Kubernetes configurations
- [x] CI/CD pipeline generation (GitHub Actions)
- [x] Deployment configs (Vercel, Railway, Render)

## API Endpoints v2.0

### Core
- `POST /api/analyze` - Socratic analysis
- `POST /api/resolve` - Answer ambiguities

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

## Prioritized Backlog

### P0 - Critical
- [ ] Deploy generated code to cloud (Vercel/Railway/AWS)
- [ ] Live preview of generated applications

### P1 - High Priority
- [ ] Streaming LLM responses
- [ ] Marketing content generation (AI copy)
- [ ] More backend templates (NestJS, Django, Go)

### P2 - Medium Priority
- [ ] Visual tech stack selector UI
- [ ] Template library
- [ ] Multi-user collaboration

## Next Tasks
1. Add deployment automation
2. Build visual tech stack selector
3. Implement live preview
