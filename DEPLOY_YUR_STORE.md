# Deploying Franklin OS to yur-ai.store

## Frontend
- Env: `REACT_APP_BACKEND_URL`, `REACT_APP_BRIDGE_API`, `REACT_APP_YUR_API`.
- Start: `npm install --legacy-peer-deps && npm start` (or `npm run build` for prod).

## Backend
- Core env:
  - `DIRECT_URL`, `MONGO_URL`, `DB_NAME`
  - `GENERATED_PROJECTS_DIR`
  - `API_TOKEN` (optional auth for lithium endpoints)
  - `ASR_PROVIDER`, `ASR_API_KEY` (for real voice dictation)
  - Deploy tokens: `RAILWAY_TOKEN`, `VERCEL_TOKEN`, or kube/VM creds for agent deploys
- Run: `uvicorn server:app --host 0.0.0.0 --port 8000`

## Realtime
- SSE: `/api/lithium/stream/projects/{project_id}` pushes build/cert/deploy events.

## Agents & Academy
- Catalog: `/api/lithium/agents/catalog`
- Deploy: `/api/lithium/agents/deploy`
- Badges: `/api/lithium/academy/agents`

## Voice Dictation
- POST `/api/lithium/voice/transcribe` with `file` (audio/webm). Uses provider if configured; otherwise stubbed.
