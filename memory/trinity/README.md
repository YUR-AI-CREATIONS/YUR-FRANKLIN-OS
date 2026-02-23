# Trinity AI Intelligence Console

Multi-project AI orchestration system with unified routing across Gemini, OpenAI, and Anthropic engines. Features automatic failover, telemetry, metrics, and project-based memory management.

## Quick Start

### Local Development (Windows)
```pwsh
cd C:\TrinityAI
pip install -r requirements.txt
./start-local.ps1 -Port 8090
```
Open http://localhost:8090

### Docker (with Monitoring Stack)
```pwsh
cd C:\TrinityAI
# Optional: Export API keys
$env:GEMINI_API_KEY="your-key"
$env:OPENAI_API_KEY="your-key"
$env:ANTHROPIC_API_KEY="your-key"

docker compose up --build -d
```

**Services:**
- API: http://localhost:8090
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Key Features

- **Unified Orchestrator**: Single routing engine with automatic failover
- **Multi-Engine Support**: Gemini (multimodal), OpenAI, Anthropic
- **Project Workspaces**: Isolated memory and document management
- **Telemetry**: JSON logging + Prometheus metrics
- **Rate Limiting**: Per-IP protection on heavy endpoints
- **Health Checks**: `/health/live`, `/health/ready`, `/health/ai`
- **Observability**: Pre-configured Grafana dashboards

## API Endpoints

### Health & Monitoring
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness check
- `GET /health/ai` - Engine availability
- `GET /metrics` - Prometheus metrics

### Projects & Documents
- `GET /projects` - List projects
- `POST /create_project` - Create project
- `POST /upload/{project}` - Upload & analyze documents
- `POST /chat/{project}` - Chat with context
- `POST /scan_project/{project}` - Re-analyze all documents

See full API reference in comments within `app.py`.

## Testing

```pwsh
# Full test suite
python -m pytest -q

# Smoke tests (validates routing)
python trinity_mothership.py --run-smoke

# Integration harness
python trinity_test.py
```

## Environment Variables

```env
GEMINI_API_KEY=<optional>
OPENAI_API_KEY=<optional>
ANTHROPIC_API_KEY=<optional>
PORT=8090
```

Engines without keys are skipped; check `/health/ai` for active engines.

## Architecture

- `app.py` - FastAPI application with routes
- `trinity_orchestrator_unified.py` - Core routing engine
- `trinity_mothership.py` - Handler registration
- `config.py` - Centralized environment config
- `telemetry.py` - Logging & Prometheus metrics
- `gemini_master.py` - Gemini multimodal handlers

### Flow
1. Prompt classified by intent
2. Routed to primary engine
3. Automatic failover on error
4. Telemetry logged (JSONL + Prometheus)

## Documentation

- `OPERATIONS.md` - Deployment and operations guide
- `SECURITY_CONSOLIDATION.md` - Security audit and recommendations

## Troubleshooting

**Port in use:** `./start-local.ps1 -Port 8091`

**Missing keys:** App runs without keys; unavailable engines are skipped. Check `/health/ai`.

**Docker issues:** `docker logs trinity-api`


Quick start

- Install dependencies (recommended to use a virtualenv):

```pwsh
python -m pip install -r requirements.txt
```

- Start the API server:

```pwsh
Start-Process -FilePath python -ArgumentList '-m uvicorn app:app --port 8080' -NoNewWindow
```

- Register handlers and run smoke tests via the mothership:

```pwsh
python trinity_mothership.py --run-smoke
```

Testing

- Unit tests and smoke tests run in mocked mode in CI. To run smoke tests locally without calling external APIs:

```pwsh
$env:TRINITY_MOCK=1; python smoke_test.py
```

- Playwright UI tests are provided as a placeholder but require the `playwright` package and browsers installed:

```pwsh
pip install playwright pytest-playwright
playwright install
pytest tests/playwright/test_ui.py
```

Notes

- API keys for Gemini/OpenAI/Anthropic must be set in environment variables (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) for live runs.
- `trinity_orchestrator_unified.py` contains a simple plugin registry; use `register_handler(kind, func)` to add custom handlers.
