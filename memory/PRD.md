# Sovereign Genesis Platform (SGP) v2.0 - Product Requirements Document

## Original Problem Statement
Build SGP as a **meta-system that creates systems** - not industry-specific, but a universal software factory. The system must:
1. Accept ANY domain requirement via Socratic questioning
2. Self-improve through Ouroboros Loop until 99% quality convergence
3. Detect drift from intended trajectory (Frozen Spine)
4. Track milestones with Evolution Playbook
5. Manage governance, compliance, and licensing
6. Generate complete multi-page applications (Landing, App, Marketing, Governance)

## User Personas
- **Software Architects** - Need mathematically verified specifications
- **Technical Leads** - Want transparent reasoning and quality gates
- **Engineers** - Building verified, secure systems across ANY domain
- **Product Managers** - Need roadmap tracking and milestone management

## Core Architecture

### The Genesis Pipeline
```
INCEPTION → SPECIFICATION → ARCHITECTURE → CONSTRUCTION → VALIDATION → EVOLUTION → DEPLOYMENT → GOVERNANCE
```

### Core Modules (v2.0)
1. **Socratic Engine** - Ambiguity detection, clarifying questions
2. **Genesis Kernel** - Project management, stage advancement
3. **Ouroboros Loop** - Self-referential improvement (99% convergence)
4. **Quality Gate** - 8-dimensional assessment
5. **Frozen Spine** - Drift detection, integrity validation
6. **Evolution Playbook** - Roadmap, milestones, success criteria
7. **Governance Engine** - Compliance, licensing, approvals
8. **Multi-Kernel Orchestrator** - Agent tiers, task coordination

## What's Been Implemented (Feb 2026)

### Phase 1 - MVP ✓
- [x] Socratic Pre-Prompt Engine with ambiguity detection
- [x] Glass Box 2D DAG visualization (React Flow)
- [x] Dark "Tactical Minimalism" theme

### Phase 2 - Genesis Pipeline v2.0 ✓
- [x] **Ouroboros Loop** - Iterates until 99% quality threshold
- [x] **Quality Gate** - 8 dimensions: Completeness, Coherence, Correctness, Security, Performance, Scalability, Maintainability, Compliance
- [x] **Frozen Spine** - SHA-256 state hashing, drift detection
- [x] **Evolution Playbook** - 6 milestones: Requirements Lock, Architecture Blueprint, Core Build, Quality Certification, Production Release, Governance & Licensing
- [x] **Governance Engine** - Approval workflows, compliance audit (GDPR, HIPAA, PCI-DSS, SOC2), license generator (Proprietary, Open Source, SaaS, Enterprise, Freemium)
- [x] **Multi-Kernel Orchestrator** - 6 agent tiers (Commander, Architect, Builder, Validator, Guardian, Executor)
- [x] **Page Generator** - Landing, Application, Marketing, Governance page structures
- [x] Pipeline visualization with 8-stage DAG

### API Endpoints v2.0
**Core:**
- `POST /api/analyze` - Socratic analysis
- `POST /api/resolve` - Answer ambiguities

**Genesis:**
- `POST /api/genesis/project/init` - Initialize project
- `POST /api/genesis/quality/assess` - Quality gate assessment
- `POST /api/genesis/ouroboros/execute` - Run convergence loop
- `GET /api/genesis/project/{id}/status` - Project status
- `GET /api/genesis/project/{id}/roadmap` - Milestone progress

**Governance:**
- `POST /api/governance/compliance/audit` - Run compliance checks
- `POST /api/governance/license/configure` - Generate license
- `POST /api/governance/approval/submit` - Submit approval

**Orchestrator:**
- `POST /api/orchestrator/task/create` - Create task
- `GET /api/orchestrator/agents` - List agents
- `POST /api/orchestrator/pages/generate` - Generate page structure

## Quality Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Completeness | 1.5x | All requirements addressed |
| Coherence | 1.3x | Internal consistency |
| Correctness | 1.5x | Functional accuracy |
| Security | 1.4x | Vulnerability assessment |
| Performance | 1.0x | Efficiency metrics |
| Scalability | 1.0x | Growth capacity |
| Maintainability | 1.1x | Code quality |
| Compliance | 1.2x | Regulatory adherence |

## Prioritized Backlog

### P0 - Critical
- [ ] Code generation engine (actual file output)
- [ ] Deployment automation

### P1 - High Priority  
- [ ] Streaming LLM responses
- [ ] Build engine (Database, Backend, Frontend generation)
- [ ] Marketing content generation (AI-powered copy)

### P2 - Medium Priority
- [ ] Session history sidebar
- [ ] Specification templates library
- [ ] Collaborative multi-user sessions

### P3 - Future
- [ ] Post-quantum cryptography (Kyber, Dilithium)
- [ ] Formal verification integration (Z3, Isabelle)
- [ ] Custom model fine-tuning

## Technical Stack
- **Frontend**: React 19 + React Flow + Tailwind CSS
- **Backend**: FastAPI + MongoDB + emergentintegrations
- **AI**: Claude Sonnet 4.5 via Emergent Universal Key
- **Security**: SHA-256 state hashing, audit trails

## Next Tasks
1. Implement Build Engine (code generation from specs)
2. Add streaming for real-time LLM output
3. Create Deployment Engine
4. Marketing content generation
