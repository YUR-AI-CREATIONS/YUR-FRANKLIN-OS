# SOVEREIGN GENESIS PLATFORM (SGP) v2.0
## Complete System Documentation

---

## 📁 FILE TREE

```
/app/
├── backend/
│   ├── .env                          # Environment variables (MONGO_URL, EMERGENT_LLM_KEY)
│   ├── server.py                     # FastAPI main application (1100+ lines)
│   ├── llm_providers.py              # Hybrid LLM abstraction (Cloud/Local/Hybrid)
│   ├── genesis_kernel.py             # Core pipeline engine (Ouroboros Loop, Quality Gate)
│   ├── governance_engine.py          # Compliance, licensing, approvals
│   ├── multi_kernel_orchestrator.py  # Agent tiers, task management
│   ├── build_engine.py               # Code generation engine
│   ├── tech_stack_registry.py        # 40+ technology catalog
│   ├── requirements.txt              # Python dependencies
│   └── tests/
│       ├── test_llm_endpoints.py
│       ├── test_build_engine.py
│       └── test_sgp_full.py
│
├── frontend/
│   └── src/
│       ├── App.js                    # Main React application
│       ├── App.css                   # Global styles
│       ├── index.js                  # Entry point
│       ├── index.css                 # Tailwind imports
│       ├── components/
│       │   ├── nodes/                # React Flow node types
│       │   │   ├── InputNode.jsx     # User input visualization
│       │   │   ├── AmbiguityNode.jsx # Clarification question nodes
│       │   │   ├── ResolutionNode.jsx# Resolved answer nodes
│       │   │   ├── SpecNode.jsx      # Specification nodes
│       │   │   ├── ProcessingNode.jsx# Loading/processing states
│       │   │   └── StageNode.jsx     # Pipeline stage nodes
│       │   ├── panels/               # UI panels
│       │   │   ├── Header.jsx        # App header with LLM selector
│       │   │   ├── InputPanel.jsx    # Socratic input terminal
│       │   │   ├── ClarificationPanel.jsx # Q&A interface
│       │   │   ├── LLMSelector.jsx   # Cloud/Local/Hybrid toggle
│       │   │   ├── PipelinePanel.jsx # Genesis pipeline view
│       │   │   ├── QualityGatePanel.jsx # Quality scores display
│       │   │   ├── NodeInspector.jsx # Node detail viewer
│       │   │   └── SpecificationPanel.jsx
│       │   └── ui/                   # Shadcn UI components (60+ components)
│       ├── hooks/
│       │   └── use-toast.js
│       └── lib/
│           └── utils.js
│
├── generated/                        # OUTPUT: Generated projects go here
│   ├── TaskManager/                  # Example generated project
│   │   ├── backend/
│   │   │   ├── app/main.py
│   │   │   ├── app/models.py
│   │   │   ├── app/routes.py
│   │   │   ├── requirements.txt
│   │   │   └── Dockerfile
│   │   ├── frontend/
│   │   │   ├── app/layout.tsx
│   │   │   ├── app/page.tsx
│   │   │   ├── package.json
│   │   │   ├── tailwind.config.ts
│   │   │   └── Dockerfile
│   │   ├── database/schema.sql
│   │   ├── docker-compose.yml
│   │   ├── .github/workflows/ci.yml
│   │   ├── .github/workflows/deploy.yml
│   │   └── sgp-manifest.json
│   └── [Other generated projects...]
│
├── memory/
│   └── PRD.md                        # Product requirements document
│
└── test_reports/
    ├── iteration_1.json
    ├── iteration_2.json
    ├── iteration_3.json
    ├── iteration_4.json
    └── iteration_5.json
```

---

## 🔌 API ENDPOINTS (Complete List)

### CORE APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/` | System health & version info |
| POST | `/api/analyze` | **Socratic Engine** - Analyze prompt, identify ambiguities |
| POST | `/api/resolve` | Submit answers to clarification questions |
| GET | `/api/session/{session_id}` | Get session data |
| GET | `/api/sessions` | List all sessions |

### GENESIS PIPELINE APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/genesis/project/init` | Initialize new Genesis project |
| POST | `/api/genesis/quality/assess` | Run 8-dimension quality assessment |
| POST | `/api/genesis/ouroboros/execute` | Execute convergence loop (until 99%) |
| GET | `/api/genesis/project/{id}/status` | Get project status |
| GET | `/api/genesis/project/{id}/roadmap` | Get milestone roadmap |

### GOVERNANCE APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/governance/compliance/audit` | Run compliance checks |
| POST | `/api/governance/license/configure` | Configure software licensing |
| POST | `/api/governance/approval/submit` | Submit approval for gate |
| GET | `/api/governance/status/{project_id}` | Get governance status |

### ORCHESTRATOR APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/orchestrator/task/create` | Create orchestrated task |
| GET | `/api/orchestrator/agents` | List all agents |
| POST | `/api/orchestrator/pages/generate` | Generate page structure |
| GET | `/api/orchestrator/status` | Get orchestrator overview |

### TECH STACK APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stack/catalog` | Get full technology catalog (40+ techs) |
| GET | `/api/stack/category/{cat}` | Get techs by category |
| GET | `/api/stack/tech/{id}` | Get technology details |
| GET | `/api/stack/search?q=` | Search technologies |
| POST | `/api/stack/validate` | Validate stack compatibility |

### BUILD ENGINE APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/build/configure` | Configure tech stack for project |
| POST | `/api/build/generate` | **Generate code artifacts** (14+ files) |
| POST | `/api/build/write` | **Write files to disk** (/app/generated/) |
| GET | `/api/build/tree/{project_id}` | Get file tree structure |
| GET | `/api/build/artifacts/{project_id}` | List generated artifacts |
| GET | `/api/build/artifact/{project_id}/{artifact_id}` | Get file content |
| GET | `/api/build/deployment/{project_id}` | Get deployment config |

### LLM PROVIDER APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/llm/status` | Get LLM provider status & config |
| POST | `/api/llm/config` | **Switch LLM mode** (cloud/local/hybrid) |
| GET | `/api/llm/models` | List available local models |
| POST | `/api/llm/test` | Test LLM generation |

---

## ⚡ FUNCTIONALITIES

### 1. SOCRATIC ENGINE
- **Purpose**: Analyze ANY requirement and identify ambiguities
- **How it works**:
  1. User enters a prompt (e.g., "Build a task management app")
  2. LLM analyzes and returns clarifying questions across 8 categories:
     - AUTH (authentication)
     - DATA (database/persistence)
     - SCALE (scalability requirements)
     - SECURITY (encryption, compliance)
     - INTEGRATION (external APIs)
     - ERROR (error handling)
     - PERFORMANCE (latency, throughput)
     - UI (user interface)
  3. Returns confidence score (0-100%)
  4. User answers questions until confidence reaches 99.5%

### 2. GENESIS PIPELINE (8 Stages)
```
INCEPTION → SPECIFICATION → ARCHITECTURE → CONSTRUCTION → VALIDATION → EVOLUTION → DEPLOYMENT → GOVERNANCE
```
- Each stage has quality gates
- **Ouroboros Loop**: Self-improvement cycle until 99% convergence
- **Frozen Spine**: Drift detection from intended trajectory
- **Evolution Playbook**: Milestone tracking

### 3. QUALITY GATE (8 Dimensions)
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Completeness | 1.5 | All requirements addressed |
| Coherence | 1.3 | Internal consistency |
| Correctness | 1.5 | Functional accuracy |
| Security | 1.4 | Vulnerability assessment |
| Performance | 1.0 | Efficiency metrics |
| Scalability | 1.0 | Growth capacity |
| Maintainability | 1.1 | Code quality |
| Compliance | 1.2 | Regulatory adherence |

### 4. MULTI-KERNEL ORCHESTRATOR
**Agent Tiers**:
- Strategic Commander (Tier 1)
- System Architect (Tier 2)
- Code Builder (Tier 3)
- Quality Validator (Tier 4)
- DevOps Engineer (Tier 5)
- Documentation Writer (Tier 6)

### 5. TECHNOLOGY STACK REGISTRY (40+ Technologies)
**Categories**:
- Cloud Providers: AWS, GCP, Azure
- PaaS: Vercel, Railway, Render, Fly.io
- Containers: Kubernetes, Docker, Docker Swarm
- Databases: PostgreSQL, MongoDB, Supabase, PlanetScale, Neon, CockroachDB
- Cache: Redis, Upstash, Memcached
- Auth: Auth0, Clerk, Firebase Auth, Supabase Auth
- Frontend: Next.js, React, Vue.js, Svelte, Astro
- Backend: FastAPI, Express.js, NestJS, Django, Go, Rust
- CSS: Tailwind CSS, shadcn/ui
- CI/CD: GitHub Actions, GitLab CI/CD
- AI/ML: OpenAI, Anthropic Claude, LangChain

### 6. BUILD ENGINE (Code Generation)
**What it generates**:
- `backend/app/main.py` - FastAPI application with CORS, health checks
- `backend/app/models.py` - Pydantic models from data model entities
- `backend/app/routes.py` - API endpoints from contracts
- `backend/requirements.txt` - Python dependencies
- `backend/Dockerfile` - Container config
- `frontend/app/page.tsx` - Next.js/React pages
- `frontend/app/layout.tsx` - Layout component
- `frontend/package.json` - Node dependencies
- `frontend/tailwind.config.ts` - Tailwind config
- `frontend/Dockerfile` - Frontend container
- `database/schema.sql` - PostgreSQL/Supabase schema
- `docker-compose.yml` - Multi-service orchestration
- `.github/workflows/ci.yml` - CI pipeline
- `.github/workflows/deploy.yml` - Deployment pipeline
- `sgp-manifest.json` - Build metadata

### 7. LLM PROVIDER SYSTEM (Dual Mode)
| Mode | Provider | Cost | Description |
|------|----------|------|-------------|
| Cloud | Claude Sonnet 4.5 | Pay per request | Via Emergent LLM Key |
| Local | Ollama (Llama 3.1) | Free | Requires local Ollama install |
| Hybrid | Both | Smart routing | Local first, cloud fallback |

**Recommended Local Models**:
- `llama3.1:8b` - General purpose (4.7GB)
- `codellama:13b` - Code generation (7.4GB)
- `phi3:14b` - Reasoning (7.9GB)
- `mistral:7b` - Fast general (4.1GB)

### 8. GOVERNANCE ENGINE
- **Compliance Categories**: GDPR, HIPAA, SOC2, PCI-DSS, ISO27001, ACCESSIBILITY
- **License Types**: MIT, Apache 2.0, GPL, Proprietary, Custom
- **Approval Workflow**: Pending → Approved/Rejected/Conditional

---

## 🎨 FRONTEND FEATURES

### React Flow Canvas
- Interactive DAG visualization
- Draggable nodes
- Animated edges
- MiniMap navigation
- Zoom controls

### UI Components
- **Header**: Logo, project ID, stage indicator, LLM selector, confidence score
- **Input Panel**: Terminal-style input for requirements
- **Clarification Panel**: Q&A interface with options
- **Pipeline Panel**: 8-stage progress visualization
- **Quality Gate Panel**: Dimension scores with recommendations
- **Node Inspector**: Detailed node information

---

## 🚀 USAGE FLOW

```
1. ENTER REQUIREMENTS
   └─> POST /api/analyze with prompt
   
2. ANSWER CLARIFICATIONS  
   └─> POST /api/resolve with answers
   └─> Repeat until confidence >= 99.5%
   
3. INITIALIZE PROJECT
   └─> POST /api/genesis/project/init
   
4. RUN QUALITY ASSESSMENT
   └─> POST /api/genesis/quality/assess
   
5. EXECUTE OUROBOROS (if needed)
   └─> POST /api/genesis/ouroboros/execute
   └─> Loops until 99% convergence
   
6. SELECT TECH STACK
   └─> GET /api/stack/catalog
   └─> POST /api/stack/validate
   
7. GENERATE CODE
   └─> POST /api/build/generate
   └─> Creates 14+ file artifacts
   
8. WRITE TO DISK
   └─> POST /api/build/write
   └─> Files at /app/generated/{project}/
   
9. DEPLOY (future)
   └─> One-click to Vercel/Railway/AWS
```

---

## 📊 TEST STATUS

| Component | Tests | Pass Rate |
|-----------|-------|-----------|
| LLM Endpoints | 19 | 100% |
| Build Engine | 14 | 100% |
| Full E2E | 21 | 95-100% |
| Frontend UI | All verified | 100% |

---

## 🔧 CONFIGURATION

### Backend (.env)
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
EMERGENT_LLM_KEY=sk-emergent-xxxxx
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=https://code-genesis-14.preview.emergentagent.com
WDS_SOCKET_PORT=443
```

---

## 📝 GENERATED PROJECT EXAMPLE

**Input**: "Build a task management app with user auth"

**Output** (`/app/generated/TaskManager/`):
```
TaskManager/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI with CORS
│   │   ├── models.py        # User, Task Pydantic models
│   │   └── routes.py        # GET/POST /tasks endpoints
│   ├── requirements.txt     # fastapi, uvicorn, pydantic, asyncpg
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── layout.tsx       # Next.js root layout
│   │   └── page.tsx         # Home page component
│   ├── package.json         # next, react, tailwindcss
│   ├── tailwind.config.ts
│   └── Dockerfile
├── database/
│   └── schema.sql           # CREATE TABLE user, task
├── docker-compose.yml       # backend, frontend, postgres, redis
├── .github/workflows/
│   ├── ci.yml               # Test pipeline
│   └── deploy.yml           # Vercel/Railway deployment
└── sgp-manifest.json        # Build metadata
```
