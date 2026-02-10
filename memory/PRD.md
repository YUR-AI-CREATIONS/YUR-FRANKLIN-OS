# FRANKLIN OS - Product Requirements Document

## Original Problem Statement
Build "FRANKLIN OS," a sophisticated, VS Code-style IDE for building, certifying, and deploying enterprise applications with a "galactic liquid glassmorphism" cyberpunk aesthetic. The core mission is to create a fully functional software factory where a user interacts with an AI agent (Franklin) to define a project, which is then executed by a team of specialized agents (Grok, Genesis, Architect, etc.).

## User's Vision
- Chrome FRANKLIN title with shimmer effect
- Galactic starfield background with twinkling stars
- 3-column IDE layout: Franklin (left) | Code Area (center) | Grok (right)
- Transparent, resizable panels
- "1 million context" labels on panels
- Ghost lines connecting Franklin ↔ Code ↔ Grok
- Terminal at bottom center
- Projects/Folders tabs
- Stripe integration for user subscriptions
- **Consistent Galaxy Black Glassmorphism across ALL pages**
- **Franklin chat on Workflow page that executes real actions**

## Core Architecture
```
/app/
├── backend/
│   ├── server.py              # Main FastAPI app
│   ├── franklin_routes.py     # Core API routes
│   ├── franklin_orchestrator.py # User→Franklin→Grok→Agents workflow
│   ├── persistence.py         # Chat persistence
│   ├── payment_routes.py      # Stripe payment integration
│   └── ...
├── frontend/
│   └── src/
│       ├── App.js             # Main app with 3 pages
│       └── components/
│           └── LandingPage.jsx # Login + Pricing
└── memory/
    └── PRD.md
```

## What's Been Implemented

### February 2026 - Current Session

**Visual Consistency Achieved:**
- [x] Galaxy Black Glassmorphism on ALL three pages (Landing, IDE, Workflow)
- [x] Sparkly twinkling stars background on all pages
- [x] Ghost "FRANKLIN" text on IDE and Workflow pages
- [x] Consistent glass-blur effects and color scheme

**Functional Chat on Workflow Page:**
- [x] Franklin chat panel with natural language command parsing
- [x] Commands that execute real actions:
  - "move to [stage]" - navigate pipeline stages
  - "run ouroboros" - start convergence loop
  - "check quality" - show quality gate scores
  - "status" - show current pipeline state
  - "reset" - reset the pipeline
  - "next/previous stage" - navigate stages
- [x] Regular questions sent to AI backend for intelligent responses
- [x] Clickable stages in the right panel for quick navigation
- [x] Live quality gate progress bars during convergence
- [x] Terminal output showing real-time updates

### December 2025 - Previous Session

**UI/UX:**
- [x] 3-page application: Landing → IDE → Workflow
- [x] Landing page with chrome FRANKLIN title, login form, pricing view
- [x] IDE page matching user's wireframe:
  - Left: Franklin panel (resizable, transparent)
  - Center: Code area with ghost lines indicator
  - Right: Grok panel (resizable, transparent)
  - Bottom: Terminal + Projects/Folders sections
  - Franklin Prompt and Grok Prompt aligned with panels
  - "1 million context" labels on both panels
- [x] Workflow page restored to original state (Electric Workflow with ReactFlow)
- [x] Galactic background with twinkling stars
- [x] Ghost FRANKLIN title visible through transparent panels

**Stripe Integration:**
- [x] Backend payment routes (`/api/payments/checkout`, `/api/payments/status`, `/api/payments/packages`)
- [x] Webhook endpoint for Stripe events
- [x] 4 subscription tiers: Free ($0), Starter ($9.99), Pro ($29.99), Enterprise ($99.99)
- [x] Frontend pricing cards with Stripe checkout flow
- [x] Payment status polling on success redirect

**Agent Orchestration:**
- [x] User → Franklin → Grok → Agents pipeline
- [x] `/genesis` command for initiating builds
- [x] Real-time terminal output
- [x] Grok response panel

**Chat & Persistence:**
- [x] Franklin chat with localStorage persistence
- [x] Grok responses with localStorage persistence
- [x] Terminal output history
- [x] Saved chats functionality

## API Endpoints

### Payment APIs
- `GET /api/payments/packages` - Get subscription packages
- `POST /api/payments/checkout` - Create Stripe checkout session
- `GET /api/payments/status/{session_id}` - Get payment status
- `GET /api/payments/user/{email}` - Get user subscription
- `POST /api/webhook/stripe` - Stripe webhook handler

### Agent APIs
- `POST /api/build-orchestrator/build` - Start build with agents
- `POST /api/build-orchestrator/chat` - Chat with Franklin
- `POST /api/grok/chat` - Direct Grok conversation

## Subscription Packages
| Package | Price | Features |
|---------|-------|----------|
| Free | $0/mo | Basic access, 1 project, Community support |
| Starter | $9.99/mo | Full IDE, 5 projects, Email support, 1M context |
| Pro | $29.99/mo | Unlimited projects, Priority support, Team collaboration |
| Enterprise | $99.99/mo | Custom deployment, Dedicated support, SLA guarantee |

## Backlog / Future Tasks

### P1 - High Priority
- [ ] Implement "Whiteboard" view for collaborative code agreement
- [ ] Implement "Workspace" view for auto-populated code sections
- [ ] Make panels slide in/out smoothly with proper animation
- [ ] Synchronize prompt box movements with panel resizing

### P2 - Medium Priority
- [ ] Implement remaining UI windows (Pulse, Matrix, Ledger, Archive)
- [ ] Vector DB integration for "Memory Mesh"
- [ ] Supabase database schema creation
- [ ] Continuous workflow loop ("The Loop")

### P3 - Low Priority / Refactoring
- [ ] Break down App.js into smaller components
- [ ] Create route-based sections (/studio, /agents, /academy)
- [ ] Optimize React re-renders
- [ ] Add proper TypeScript types

## Technical Notes
- Frontend: React with Tailwind CSS
- Backend: FastAPI with MongoDB
- Payments: Stripe via emergentintegrations library
- LLM: Claude via Anthropic/Emergent integration
- Workflow: ReactFlow for visual pipelines

## Known Issues
- App.js is still monolithic (~800 lines) but significantly reduced from 2000+
- Some panel alignment may need fine-tuning based on screen size
