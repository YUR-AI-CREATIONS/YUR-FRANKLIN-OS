# Sovereign Genesis Platform (SGP) - Product Requirements Document

## Original Problem Statement
Build the Sovereign Genesis Platform MVP - an AI-powered Neural-Symbolic reasoning engine that uses a Probabilistic-to-Deterministic Bridge approach. The system features:
1. **Socratic Pre-Prompt Engine** - Refuses to answer ambiguous prompts directly, parsing them for missing variables and returning clarifying questions
2. **Glass Box Visualization** - 2D DAG showing the reasoning flow transparently
3. **Formal Specification Generation** - Once ambiguities resolved (confidence ≥99.5%), generate formal specs

## User Personas
- **Software Architects** - Need mathematically verified specifications
- **Technical Leads** - Want transparent reasoning for auditing
- **Engineers** - Building formally verified, secure systems

## Core Requirements (Static)
1. Claude Sonnet 4.5 integration via Emergent LLM Key
2. 2D Interactive DAG using React Flow
3. Dark minimalist theme ("Tactical Minimalism")
4. Socratic questioning loop before any code generation
5. Confidence scoring system (target: 99.5% for spec generation)

## Architecture
- **Frontend**: React 19 + React Flow + Tailwind CSS
- **Backend**: FastAPI + MongoDB + emergentintegrations
- **AI**: Claude Sonnet 4.5 via Emergent Universal Key

## What's Been Implemented (Feb 2026)

### Phase 1 - MVP Complete ✓
- [x] Socratic Pre-Prompt Engine with ambiguity detection
- [x] Glass Box 2D DAG visualization
- [x] Custom React Flow nodes (Input, Ambiguity, Resolution, Spec, Processing)
- [x] Floating glass panels (Input Terminal, Clarification, Node Inspector, Specification)
- [x] Real-time confidence scoring
- [x] Session management with MongoDB persistence
- [x] Formal specification generation endpoint
- [x] Dark theme with Azeret Mono + IBM Plex Sans typography

### API Endpoints
- `POST /api/analyze` - Analyze prompt, detect ambiguities
- `POST /api/resolve` - Process user answers, update confidence
- `POST /api/generate-spec` - Generate formal specification
- `GET /api/session/{id}` - Retrieve session
- `GET /api/sessions` - List recent sessions

## Prioritized Backlog

### P0 - Critical (Next Sprint)
- [ ] Streaming responses for real-time LLM output visualization
- [ ] Enhanced error handling for LLM quota exhaustion

### P1 - High Priority
- [ ] Dual-mode interface (Junior vs Architect mode)
- [ ] TLA+ specification output format
- [ ] Export specifications to multiple formats (JSON, YAML, Markdown)

### P2 - Medium Priority
- [ ] Session history sidebar
- [ ] Specification templates library
- [ ] Collaborative sessions (multi-user)

### P3 - Future
- [ ] Local inference option (Air-Gap mode)
- [ ] Integration with formal verification tools (Z3, Isabelle)
- [ ] Custom MoE model fine-tuning

## Technical Notes
- LLM integration uses emergentintegrations library
- All sessions stored in MongoDB `sessions` collection
- Specifications stored in `specifications` collection
- Node positions auto-calculated based on DAG depth

## Next Tasks
1. Add streaming support for real-time LLM visualization
2. Implement session history panel
3. Add specification export functionality
