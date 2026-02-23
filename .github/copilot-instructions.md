# GitHub Copilot Instructions for YUR FRANKLIN OS

This project is **YUR FRANKLIN OS** (formerly Sovereign Genesis Platform), an AI-powered software factory & IDE designed to build, certify, and deploy enterprise-grade applications.

## 🌟 Core Philosophy & Principles
- **Truth, Trust, Transparency**: Zero hallucination, complete auditable trail for all AI actions.
- **Sovereign Genesis**: Agents build software autonomously but under strict governance.
- **Self-Healing**: The "Grok" agent automatically fixes code issues during the build process.
- **Design Aesthetic**: Galactic liquid glassmorphism cyberpunk.

## 🏗 Architecture Overview

### 1. Backend (Python/FastAPI) (`backend/`)
- **Entry Point**: `backend/server.py` initializes the FastAPI app and routes.
- **Orchestration**:
  - `Franklin` (`backend/franklin_orchestrator.py`): The central nervous system managing user intent and build phases.
  - `GenesisKernel` (`backend/genesis_kernel.py`): The core build pipeline engine.
  - `Grok` (`backend/grok_agent.py`): The self-healing agent for error correction.
- **Data Layer**:
  - **MongoDB** (via `motor`): Stores chat history, terminal logs, and unstructured artifacts.
  - **Supabase/PostgreSQL**: Stores structured data (users, projects, certifications).
- **Key Patterns**:
  - Heavy use of **Pydantic** for data validation and schema definition.
  - **AsyncIO** for all I/O bound operations (database, LLM calls).
  - **Dependency Injection** via function arguments in FastAPI.

### 2. Frontend (React) (`frontend/`)
- **Framework**: React (Create React App) with `craco` override.
- **Styling**: Tailwind CSS (`frontend/tailwind.config.js`).
- **State Management**: React Context / Hooks.
- **Communication**: REST API calls to `REACT_APP_BACKEND_URL` and SSE (Server-Sent Events) for realtime updates.

### 3. Build Phases (`backend/franklin_orchestrator.py`)
Understanding the lifecycle is critical:
1.  `INTAKE`: User request received.
2.  `PERFECT_PROMPT`: Franklin optimizations.
3.  `ARCHITECT`: System design.
4.  `IMPLEMENT`: Code generation.
5.  `HEAL`: Error correction (Grok).
6.  `WHITEBOARD` -> `AUDIT` -> `VERIFY` -> `CERTIFY` -> `SIGNOFF` -> `DEPLOY`.

## 🛠 Developer Workflow

### Backend Setup
1.  **Dependencies**: `backend/requirements.txt`
    ```bash
    cd backend
    pip install -r requirements.txt
    ```
2.  **Environment**: Requires `.env` with `DIRECT_URL` (Supabase), `MONGO_URL`, `API_TOKEN`, etc.
3.  **Run Server**:
    ```bash
    cd backend
    uvicorn server:app --host 0.0.0.0 --port 8000 --reload
    ```
    *Note: `server.py` uses `uvicorn.run` programmatically as well.*

### Frontend Setup
1.  **Dependencies**: `frontend/package.json`
    ```bash
    cd frontend
    npm install --legacy-peer-deps
    ```
2.  **Run Dev Server**:
    ```bash
    npm start
    ```
    *Runs on `localhost:3000` by default.*

## 🧩 Project-Specific Conventions

-   **Agent Communication**: Agents (Franklin, Grok) communicate via structured messages. When implementing new agent capabilities, ensure they log to the `audit_trail` to maintain the "Truth" principle.
-   **File Generation**: Use `backend/file_generator.py` for creating files on disk. Do not use standard `open()` unless necessary, to ensure tracking.
-   **Error Handling**: Use `Grok` for automated recovery where possible. Exceptions should be caught and fed into the `HEAL` phase if they occur during generation.
-   **Security**: All external API keys must be loaded from environment variables. Never hardcode credentials.

## 📂 Key Directories
-   `backend/`: Core logic, API, and Agents.
-   `frontend/`: React UI.
-   `generated_projects/`: Output directory where Franklin builds user projects.
-   `memory/`: Persistent storage for agent context (Multi-tiered memory architecture).
