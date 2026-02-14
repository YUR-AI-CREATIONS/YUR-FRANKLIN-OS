# FRANKLIN OS - COMPLETE SYSTEM ARCHITECTURE

## SYSTEM FLOW
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER JOURNEY                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   LANDING PAGE ──► IDE PAGE (Build) ──► WORKFLOW PAGE (Certify) ──► DEPLOY │
│                                                                             │
│   1. Login/Subscribe    2. Tell Franklin      3. 8-Gate Validation    4. Ship│
│                            what to build         & Certification           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## LAYER 1: DATABASES

### 1.1 Primary Database (Supabase/PostgreSQL)
| Table | Purpose | Status |
|-------|---------|--------|
| `users` | User accounts, auth, subscription tier | NOT BUILT |
| `projects` | User projects metadata | NOT BUILT |
| `builds` | Build sessions, status, artifacts | NOT BUILT |
| `certifications` | Certification records, hashes | NOT BUILT |
| `payments` | Stripe payment records | NOT BUILT |

### 1.2 Document Database (MongoDB)
| Collection | Purpose | Status |
|------------|---------|--------|
| `chat_history` | Franklin/Grok conversations | NOT BUILT |
| `terminal_logs` | Real terminal output | NOT BUILT |
| `build_artifacts` | Generated code files | NOT BUILT |

### 1.3 Vector Database (Future)
| Store | Purpose | Status |
|-------|---------|--------|
| `embeddings` | Code/doc similarity search | NOT BUILT |

---

## LAYER 2: BACKEND SERVICES

### 2.1 Core API Routes
| Route | Purpose | Status |
|-------|---------|--------|
| `/api/auth/*` | User authentication | NOT BUILT |
| `/api/projects/*` | Project CRUD | NOT BUILT |
| `/api/builds/*` | Build management | PARTIAL (no file output) |
| `/api/certify/*` | Certification workflow | NOT BUILT |
| `/api/deploy/*` | Deployment triggers | NOT BUILT |

### 2.2 Agent Services
| Agent | Purpose | Status |
|-------|---------|--------|
| Genesis | Requirements analysis | BUILT (LLM call) |
| Architect | System design | BUILT (LLM call) |
| Implementer | Code generation | PARTIAL (no file creation) |
| Healer | Code validation | PARTIAL (no real tests) |
| Certifier | 8-Gate validation | NOT BUILT |

---

## LAYER 3: MCP SERVERS (Model Context Protocol)

### 3.1 Required MCP Servers
| Server | Purpose | Status |
|--------|---------|--------|
| `mcp-filesystem` | Read/write project files | NOT BUILT |
| `mcp-database` | Query Supabase/Postgres | NOT BUILT |
| `mcp-terminal` | Execute shell commands | NOT BUILT |
| `mcp-docker` | Container management | NOT BUILT |
| `mcp-git` | Version control | NOT BUILT |

---

## LAYER 4: EXTERNAL PROVIDERS

### 4.1 LLM Providers
| Provider | Model | Purpose | Status |
|----------|-------|---------|--------|
| Anthropic | Claude | Primary code gen | CONNECTED |
| XAI | Grok | Secondary/analysis | CONNECTED |
| OpenAI | GPT | Fallback | CONFIGURED |

### 4.2 Infrastructure Providers
| Provider | Service | Purpose | Status |
|----------|---------|---------|--------|
| Supabase | PostgreSQL | Primary DB | CONFIGURED, NOT CONNECTED |
| Supabase | Auth | User auth | NOT CONNECTED |
| Stripe | Payments | Subscriptions | PARTIAL (UI only) |
| Vercel/AWS | Hosting | User deployments | NOT BUILT |

---

## LAYER 5: THE BUILD → CERTIFY FLOW

### 5.1 IDE Page (BUILD)
```
User Input: "Build me a todo API"
           │
           ▼
┌─────────────────────────────────────────┐
│ GENESIS AGENT                           │
│ - Parse requirements                    │
│ - Create specification doc              │
│ OUTPUT: spec.md                         │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ ARCHITECT AGENT                         │
│ - Design system structure               │
│ - Define data models                    │
│ OUTPUT: architecture.md, schema.sql     │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ IMPLEMENTER AGENT                       │
│ - Generate actual code files            │
│ - Create project structure              │
│ OUTPUT: /project/                       │
│   ├── src/                              │
│   │   ├── main.py                       │
│   │   ├── models.py                     │
│   │   └── routes.py                     │
│   ├── tests/                            │
│   ├── requirements.txt                  │
│   └── Dockerfile                        │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ HEALER AGENT                            │
│ - Run syntax checks                     │
│ - Execute tests                         │
│ - Fix issues                            │
│ OUTPUT: health_report.md                │
└─────────────────────────────────────────┘
           │
           ▼
      BUILD COMPLETE
           │
           ▼
   [TRANSFER TO WORKFLOW PAGE]
```

### 5.2 Workflow Page (CERTIFY)
```
Build arrives from IDE
           │
           ▼
┌─────────────────────────────────────────┐
│ GATE 1: INTENT VALIDATION               │
│ - Verify spec matches user intent       │
│ - Schema integrity check                │
│ STATUS: ○ PENDING                       │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ GATE 2: DATA VALIDATION                 │
│ - Test data ingestion                   │
│ - Verify ETL pipelines                  │
│ STATUS: ○ PENDING                       │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ GATE 3: MODEL VALIDATION                │
│ - Verify LLM config                     │
│ - Context window checks                 │
│ STATUS: ○ PENDING                       │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ GATE 4: VECTOR/RAG VALIDATION           │
│ - Test retrieval accuracy               │
│ - Embedding quality check               │
│ STATUS: ○ PENDING                       │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ GATE 5: ORCHESTRATION VALIDATION        │
│ - Loop detection                        │
│ - Tool handshake verification           │
│ STATUS: ○ PENDING                       │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ GATE 6: API VALIDATION                  │
│ - Endpoint fuzzing                      │
│ - Error handling checks                 │
│ STATUS: ○ PENDING                       │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ GATE 7: UI VALIDATION                   │
│ - Component render test                 │
│ - Responsiveness check                  │
│ STATUS: ○ PENDING                       │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ GATE 8: SECURITY VALIDATION             │
│ - PII redaction test                    │
│ - Prompt injection test                 │
│ STATUS: ○ PENDING                       │
└─────────────────────────────────────────┘
           │
           ▼
   ALL GATES PASSED
           │
           ▼
┌─────────────────────────────────────────┐
│ FRANKLIN OS CERTIFICATION               │
│ - Generate certificate hash             │
│ - Sign with timestamp                   │
│ - Store in blockchain/DB                │
│ OUTPUT: GENESIS_CERTIFIED               │
└─────────────────────────────────────────┘
           │
           ▼
      READY TO DEPLOY
```

---

## LAYER 6: DEPLOYMENT TARGETS

### 6.1 Supported Platforms
| Platform | Type | Status |
|----------|------|--------|
| Vercel | Frontend/Serverless | NOT BUILT |
| Railway | Full-stack | NOT BUILT |
| AWS ECS | Containers | NOT BUILT |
| Docker Hub | Registry | NOT BUILT |

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Database Foundation
- [ ] Connect Supabase PostgreSQL
- [ ] Create users table
- [ ] Create projects table
- [ ] Create builds table
- [ ] Create certifications table
- [ ] Connect MongoDB for chat/logs

### Phase 2: Real File Generation
- [ ] Implement file parser (extract code from LLM response)
- [ ] Create project directory structure
- [ ] Write actual files to disk/storage
- [ ] Generate downloadable ZIP

### Phase 3: Build → Workflow Transfer
- [ ] Save build to database after IDE completion
- [ ] Load build on Workflow page
- [ ] Display build artifacts in certification UI
- [ ] Track gate progress in database

### Phase 4: 8-Gate Certification
- [ ] Implement Gate 1: Schema validation
- [ ] Implement Gate 2: Data validation
- [ ] Implement Gate 3: Model validation
- [ ] Implement Gate 4: RAG validation
- [ ] Implement Gate 5: Orchestration validation
- [ ] Implement Gate 6: API validation
- [ ] Implement Gate 7: UI validation
- [ ] Implement Gate 8: Security validation

### Phase 5: Deployment Integration
- [ ] Docker container generation
- [ ] Push to registry
- [ ] Deploy to target platform
- [ ] Health check verification

---

## HONEST STATUS

| Layer | Completion |
|-------|------------|
| Landing Page UI | 90% |
| IDE Page UI | 85% |
| Workflow Page UI | 80% |
| LLM Integration | 70% |
| Database Connection | 10% |
| Real File Generation | 0% |
| Real Certification | 0% |
| Real Deployment | 0% |

**TOTAL SYSTEM COMPLETION: ~25%**

The UI exists. The LLM calls work. But the system does NOT:
- Create actual files
- Run real tests
- Perform real certification
- Deploy anything

This document is the truth.
