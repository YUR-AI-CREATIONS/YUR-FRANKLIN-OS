# GitHub Copilot Instructions for YUR FRANKLIN OS

## Repository Overview

YUR FRANKLIN OS (formerly Sovereign Genesis Platform v2.0) is an AI-powered software factory and VS Code-style IDE that builds, certifies, and deploys enterprise-grade applications. The platform combines cutting-edge AI agents, self-healing code generation, and comprehensive quality assurance pipelines.

## Core Principles

- **Truth, Trust, Transparency**: Zero hallucination, complete auditable trail
- **Aesthetic**: Galactic liquid glassmorphism cyberpunk design
- **Quality-First**: 8-dimensional quality gate system with weighted criteria
- **AI-Powered**: Multi-tiered AI agent system with human-AI governance

## Technology Stack

### Backend (Python)
- **Framework**: FastAPI 0.110.1
- **Language**: Python 3.11+
- **AI/LLM**: XAI Grok, Anthropic Claude, OpenAI, Local Ollama
- **Database**: MongoDB (Motor async driver)
- **Authentication**: JWT, OAuth2
- **Security**: PQC simulation, Merkle Tree auditing

### Frontend (JavaScript/React)
- **Framework**: React 19.0.0
- **Routing**: React Router 7.5.1
- **Visualization**: React Flow 12.10.0, Recharts 3.6.0
- **UI Components**: Radix UI, shadcn/ui (60+ components)
- **Styling**: Tailwind CSS 3.4.17
- **Build Tool**: Craco 7.1.0

## Project Structure

```
backend/          # FastAPI services and core engines
frontend/         # React application with IDE interface
generated/        # Output directory for generated projects
memory/          # Project documentation and PRDs
test_reports/    # Test results and quality assessments
tests/           # Test suites
```

## Coding Standards

### Python Backend
- Follow PEP 8 style guide
- Use `black` for code formatting
- Prefer async/await patterns for I/O operations
- Use type hints for function signatures
- Keep functions focused and single-purpose
- Add docstrings for all public functions and classes

### JavaScript/React Frontend
- Follow Airbnb JavaScript style guide
- Use functional components with hooks
- Prefer named exports over default exports
- Use proper component hierarchy and composition
- Keep components small and focused (< 300 lines)
- Use Tailwind CSS classes for styling
- Follow the established glassmorphism design patterns

### Commit Messages
- Use conventional commits format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Example: `feat(genesis): add ouroboros convergence loop`

## Key Components

### Backend Core Engines
1. **genesis_kernel.py**: Core 8-stage pipeline engine with Ouroboros Loop
2. **build_engine.py**: Multi-language code generation engine
3. **llm_providers.py**: Hybrid Cloud/Local/Hybrid LLM support
4. **grok_agent.py**: Self-healing code generation with XAI API
5. **multi_kernel_orchestrator.py**: 6-tier agent management system
6. **governance_engine.py**: Compliance and licensing management
7. **quality_gates.py**: 8-dimensional certification system
8. **franklin_runtime.py**: DPOA and PQC simulation runtime

### Frontend Components
- **LandingPage.jsx**: Space-themed landing page
- **nodes/**: React Flow node components (Input, Ambiguity, Spec, Processing)
- **panels/**: UI panels (Header, Input, Clarification, Pipeline, QualityGate)
- **ui/**: Shadcn UI components library

## Genesis Pipeline Stages

The platform follows an 8-stage development pipeline:

1. **INCEPTION**: Requirement validation and initial analysis
2. **SPECIFICATION**: Detailed specification generation
3. **ARCHITECTURE**: System design and technical architecture
4. **CONSTRUCTION**: Code generation and artifact creation
5. **VALIDATION**: Testing and quality assurance
6. **EVOLUTION**: Optimization and refinement
7. **DEPLOYMENT**: Deployment preparation and configuration
8. **GOVERNANCE**: Compliance checking and certification

## Quality Gates

When working with quality assurance features, understand the 8-dimensional system with weights:

- Completeness (1.5x weight)
- Coherence (1.3x)
- Correctness (1.5x)
- Security (1.4x)
- Performance (1.0x)
- Scalability (1.0x)
- Maintainability (1.1x)
- Compliance (1.2x)

Target threshold: ≥ 90% for production deployment

## LLM Provider Integration

The platform supports multiple LLM providers through `llm_providers.py`:

- **Cloud Mode**: XAI Grok, Anthropic Claude, OpenAI
- **Local Mode**: Ollama with models like llama3.1, codellama, phi3
- **Hybrid Mode**: Intelligent routing based on task complexity

When adding LLM features:
- Use the unified `LLMProvider` interface
- Handle fallbacks gracefully
- Include proper error handling and retries
- Log token usage for cost tracking

## API Endpoint Patterns

When creating new API endpoints:
- Use FastAPI's dependency injection for shared resources
- Include proper request/response models with Pydantic
- Add appropriate HTTP status codes
- Include OpenAPI documentation strings
- Implement error handling with HTTPException
- Use async endpoint handlers for I/O operations

Example:
```python
@app.post("/api/resource", response_model=ResourceResponse)
async def create_resource(
    resource: ResourceCreate,
    db: Database = Depends(get_database)
) -> ResourceResponse:
    """Create a new resource with validation."""
    try:
        result = await db.resources.insert_one(resource.dict())
        return ResourceResponse(id=str(result.inserted_id), **resource.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Testing Guidelines

- Write unit tests for core logic functions
- Use pytest for backend testing
- Use Jest/React Testing Library for frontend testing
- Test quality gate calculations thoroughly
- Mock external LLM API calls in tests
- Aim for >80% code coverage on critical paths

## Security Considerations

- Never commit API keys or secrets
- Use environment variables for configuration
- Validate and sanitize all user inputs
- Implement proper authentication and authorization
- Follow OWASP security best practices
- Run security scans before deployment

## UI/UX Guidelines

- Follow the galactic liquid glassmorphism cyberpunk aesthetic
- Use the established color palette (dark backgrounds, accent colors)
- Ensure responsive design for all screen sizes
- Maintain consistent spacing and typography
- Add loading states for async operations
- Provide clear error messages and user feedback
- Keep animations smooth and purposeful

## Generated Projects Structure

When working with the build engine, generated projects should include:
- Backend API (FastAPI/Express/Django)
- Frontend application (Next.js/React/Vue)
- Database schemas and migrations
- Docker and docker-compose configurations
- CI/CD pipelines (GitHub Actions/GitLab)
- Deployment configurations (Vercel/Railway/AWS)
- Comprehensive README and documentation

## Agent Marketplace & Bot Tiers

The platform includes specialized AI agents organized in tiers:
- **Tier 6**: Strategic Commander (architecture, strategy)
- **Tier 5**: Spec Writer (requirements, PRDs)
- **Tier 4**: Code Generator (implementation)
- **Tier 3**: Test Engineer (QA, testing)
- **Tier 2**: Refactorer (optimization)
- **Tier 1**: Documentation Writer (docs, comments)

When extending agent capabilities, maintain this hierarchical structure.

## Environment Configuration

Required environment variables:

Backend (.env):
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=franklin_os
CORS_ORIGINS=http://localhost:3000
XAI_API_KEY=your_xai_api_key_here
EMERGENT_LLM_KEY=your_emergent_llm_key_here
```

Frontend (.env):
```
REACT_APP_BACKEND_URL=http://localhost:8000
WDS_SOCKET_PORT=443
```

## Common Patterns

### Error Handling
Always use try-except blocks with specific exception types and meaningful error messages.

### Async Operations
Prefer async/await for I/O operations, database queries, and API calls.

### State Management
Use React hooks (useState, useEffect, useContext) for component state management.

### Code Generation
Follow the established template patterns in `build_engine.py` for consistency.

## Getting Help

- **Documentation**: See `SGP_COMPLETE_DOCUMENTATION.md` for complete system documentation
- **Architecture**: See `ARCHITECTURE.md` for system architecture details
- **API Docs**: Run backend and visit http://localhost:8000/docs
- **Issues**: Check GitHub Issues for known problems and solutions

## Contributing Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes following these guidelines
4. Run tests: `pytest backend/tests/` and `npm test` in frontend
5. Commit with conventional commits
6. Push and open a Pull Request

## Special Notes

- The Ouroboros Loop iterates until 99% convergence is achieved
- Quality gates must pass before deployment
- Generated projects are placed in `generated/[ProjectName]/`
- The platform supports 40+ pre-configured technologies
- Self-healing is powered by XAI Grok integration
- Socratic Engine analyzes requirements across 8 categories

## Performance Considerations

- Optimize database queries with proper indexing
- Use caching for frequently accessed data
- Implement rate limiting on API endpoints
- Monitor LLM API usage and costs
- Use pagination for large data sets
- Optimize React re-renders with useMemo and useCallback

## Deployment

- Backend: Can be deployed to Railway, Render, or AWS
- Frontend: Can be deployed to Vercel or Netlify
- Database: MongoDB Atlas or self-hosted MongoDB
- Use environment-specific configurations
- Implement health check endpoints
- Set up monitoring and logging

---

**Remember**: This is a production-grade AI software factory. Every contribution should maintain the high standards of quality, security, and user experience that define YUR FRANKLIN OS.
