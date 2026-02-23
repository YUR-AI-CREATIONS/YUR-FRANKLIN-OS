# FRANKLIN OS - Product Requirements Document

## Original Problem Statement
Build "FRANKLIN OS," a sophisticated IDE for building and certifying enterprise applications with a "galactic liquid glassmorphism" cyberpunk aesthetic. Users interact with AI agent (Franklin) to define projects which are then built by specialized agents.

## User's Core Requirement
**"I literally want to tell Franklin to build me something and he build it and deliver it with the Franklin OS certification and I can run it and see it in action"**

## What's Been Implemented

### February 2026 - BUILD WITH TECH STACK ✅

**Tech Stack Selection:**
- [x] Tech stack selector in header (Python, JavaScript, TypeScript, Go, Rust, Java)
- [x] Modal for selecting stack with framework descriptions
- [x] Stack passed to build API for targeted code generation

**Build System:**
- [x] Fast Build API generates production-ready code for selected stack
- [x] Real working code - not pseudocode
- [x] Franklin OS Certification with governance log
- [x] Copy and Download functionality

**Pages:**
- [x] Landing Page (login + pricing)
- [x] IDE Page (Franklin chat + code panel + Grok analyst)
- [x] **Workflow page REMOVED** as per user request

## Tech Stacks Supported
| Stack | Frameworks |
|-------|------------|
| 🐍 Python | FastAPI, Flask, Django |
| ⚡ JavaScript | Node.js, Express, React |
| 📘 TypeScript | Node.js, Next.js, NestJS |
| 🔵 Go | Gin, Fiber, Echo |
| 🦀 Rust | Actix, Rocket, Axum |
| ☕ Java | Spring Boot, Quarkus |

## API Endpoints

### Build APIs
- `POST /api/build-orchestrator/fast-build` - Main build endpoint (takes mission + stack)
- `POST /api/build-orchestrator/chat` - Chat with Franklin

## Architecture
```
/app/
├── backend/
│   ├── server.py
│   ├── franklin_orchestrator.py  # fast_build() method
│   └── franklin_routes.py
├── frontend/
│   └── src/
│       ├── App.js                # 2 pages: Landing + IDE
│       └── components/
│           └── LandingPage.jsx
└── memory/
    └── PRD.md
```

## Backlog

### P1 - High Priority
- [ ] Stripe user authentication
- [ ] Chat persistence to database
- [ ] Multi-file project generation

### P2 - Medium Priority
- [ ] Code execution sandbox
- [ ] Git integration
- [ ] Project templates

### P3 - Refactoring
- [ ] Split App.js into smaller components
