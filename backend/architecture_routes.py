"""
ARCHITECTURE GENERATOR API
Generates system architecture documentation based on project workflow and tech stack
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from trinity_spine import trinity_spine

router = APIRouter(prefix="/api/architecture", tags=["architecture"])


class WorkflowPhase(BaseModel):
    phase_num: int
    name: str
    tasks: List[Dict[str, Any]]


class GenerateArchitectureRequest(BaseModel):
    session_id: str
    tech_stack: str
    project_name: str
    phases: Optional[List[WorkflowPhase]] = []
    file_structure: Optional[Dict[str, Any]] = {}


class ComponentDef(BaseModel):
    name: str
    type: str  # api, service, database, cache, queue, external
    description: str
    responsibilities: List[str]
    dependencies: List[str]


class LayerDef(BaseModel):
    name: str
    description: str
    components: List[ComponentDef]


class ArchitectureResult(BaseModel):
    session_id: str
    project_name: str
    tech_stack: str
    architecture_type: str  # monolith, microservices, serverless, etc.
    layers: List[LayerDef]
    data_flow: List[Dict[str, str]]
    key_decisions: List[str]
    security_considerations: List[str]
    scalability_notes: List[str]
    created_at: str


# Store architectures
architecture_store = {}


# Architecture templates per tech stack
ARCH_TEMPLATES = {
    "python": {
        "type": "Layered Monolith",
        "layers": [
            {
                "name": "Presentation Layer",
                "description": "API endpoints and request handling",
                "components": [
                    {"name": "FastAPI Router", "type": "api", "description": "REST API endpoints", "responsibilities": ["HTTP request handling", "Input validation", "Response serialization"], "dependencies": ["Service Layer"]},
                    {"name": "Middleware", "type": "service", "description": "Cross-cutting concerns", "responsibilities": ["Authentication", "Logging", "Error handling"], "dependencies": []}
                ]
            },
            {
                "name": "Service Layer",
                "description": "Business logic and orchestration",
                "components": [
                    {"name": "Business Services", "type": "service", "description": "Core business logic", "responsibilities": ["Business rules", "Workflow orchestration", "Data transformation"], "dependencies": ["Data Layer"]},
                    {"name": "Integration Services", "type": "service", "description": "External system integration", "responsibilities": ["Third-party API calls", "Message handling"], "dependencies": ["External Services"]}
                ]
            },
            {
                "name": "Data Layer",
                "description": "Data access and persistence",
                "components": [
                    {"name": "Repositories", "type": "service", "description": "Data access abstraction", "responsibilities": ["CRUD operations", "Query building", "Transaction management"], "dependencies": ["Database"]},
                    {"name": "Models", "type": "service", "description": "Domain entities", "responsibilities": ["Data validation", "Business constraints"], "dependencies": []}
                ]
            },
            {
                "name": "Infrastructure Layer",
                "description": "External systems and resources",
                "components": [
                    {"name": "Database", "type": "database", "description": "PostgreSQL/MongoDB", "responsibilities": ["Data persistence", "Query execution"], "dependencies": []},
                    {"name": "Cache", "type": "cache", "description": "Redis cache layer", "responsibilities": ["Session storage", "Query caching"], "dependencies": []},
                    {"name": "External Services", "type": "external", "description": "Third-party APIs", "responsibilities": ["LLM providers", "Payment gateways"], "dependencies": []}
                ]
            }
        ],
        "data_flow": [
            {"from": "Client", "to": "FastAPI Router", "description": "HTTP Request"},
            {"from": "FastAPI Router", "to": "Business Services", "description": "Service call"},
            {"from": "Business Services", "to": "Repositories", "description": "Data operation"},
            {"from": "Repositories", "to": "Database", "description": "SQL/NoSQL query"},
            {"from": "Database", "to": "Repositories", "description": "Query result"},
            {"from": "Repositories", "to": "Business Services", "description": "Domain objects"},
            {"from": "Business Services", "to": "FastAPI Router", "description": "Response data"},
            {"from": "FastAPI Router", "to": "Client", "description": "HTTP Response"}
        ],
        "key_decisions": [
            "FastAPI for high-performance async API handling",
            "Pydantic for data validation and serialization",
            "Repository pattern for data access abstraction",
            "Dependency injection for testability",
            "Environment-based configuration management"
        ],
        "security": [
            "JWT-based authentication",
            "Input validation at API boundary",
            "SQL injection prevention via ORM",
            "Rate limiting on public endpoints",
            "Secrets management via environment variables"
        ],
        "scalability": [
            "Stateless API design for horizontal scaling",
            "Database connection pooling",
            "Async I/O for concurrent request handling",
            "Cache layer for frequently accessed data",
            "Background task queue for heavy operations"
        ]
    },
    "javascript": {
        "type": "Express MVC",
        "layers": [
            {
                "name": "Routes Layer",
                "description": "HTTP routing and middleware",
                "components": [
                    {"name": "Express Router", "type": "api", "description": "Route definitions", "responsibilities": ["URL mapping", "HTTP method handling"], "dependencies": ["Controllers"]},
                    {"name": "Middleware Stack", "type": "service", "description": "Request pipeline", "responsibilities": ["Auth", "Validation", "Error handling"], "dependencies": []}
                ]
            },
            {
                "name": "Controller Layer",
                "description": "Request/Response handling",
                "components": [
                    {"name": "Controllers", "type": "service", "description": "Request handlers", "responsibilities": ["Input parsing", "Response formatting"], "dependencies": ["Services"]}
                ]
            },
            {
                "name": "Service Layer",
                "description": "Business logic",
                "components": [
                    {"name": "Services", "type": "service", "description": "Business operations", "responsibilities": ["Business rules", "Data processing"], "dependencies": ["Models"]}
                ]
            },
            {
                "name": "Data Layer",
                "description": "Database interaction",
                "components": [
                    {"name": "Models", "type": "service", "description": "Data models", "responsibilities": ["Schema definition", "Validation"], "dependencies": ["Database"]},
                    {"name": "Database", "type": "database", "description": "MongoDB/PostgreSQL", "responsibilities": ["Data storage"], "dependencies": []}
                ]
            }
        ],
        "data_flow": [
            {"from": "Client", "to": "Express Router", "description": "HTTP Request"},
            {"from": "Express Router", "to": "Controllers", "description": "Route handling"},
            {"from": "Controllers", "to": "Services", "description": "Business call"},
            {"from": "Services", "to": "Models", "description": "Data operation"},
            {"from": "Models", "to": "Database", "description": "Query"},
            {"from": "Database", "to": "Client", "description": "Response flow"}
        ],
        "key_decisions": [
            "Express.js for lightweight, flexible routing",
            "MVC pattern for separation of concerns",
            "Mongoose/Sequelize for ORM",
            "JWT for stateless authentication",
            "ESLint + Prettier for code quality"
        ],
        "security": [
            "Helmet.js for HTTP headers",
            "CORS configuration",
            "Input sanitization",
            "Rate limiting with express-rate-limit",
            "bcrypt for password hashing"
        ],
        "scalability": [
            "Cluster mode for multi-core utilization",
            "Redis for session storage",
            "Connection pooling",
            "Load balancer ready",
            "Stateless design"
        ]
    },
    "typescript": {
        "type": "Clean Architecture",
        "layers": [
            {
                "name": "Interface Adapters",
                "description": "Controllers and Presenters",
                "components": [
                    {"name": "Controllers", "type": "api", "description": "HTTP handlers", "responsibilities": ["Request handling", "Response formatting"], "dependencies": ["Use Cases"]},
                    {"name": "DTOs", "type": "service", "description": "Data transfer objects", "responsibilities": ["Type safety", "Validation"], "dependencies": []}
                ]
            },
            {
                "name": "Application Layer",
                "description": "Use cases and business rules",
                "components": [
                    {"name": "Use Cases", "type": "service", "description": "Application logic", "responsibilities": ["Business workflows", "Orchestration"], "dependencies": ["Domain"]},
                    {"name": "Interfaces", "type": "service", "description": "Port definitions", "responsibilities": ["Contract definitions"], "dependencies": []}
                ]
            },
            {
                "name": "Domain Layer",
                "description": "Enterprise business rules",
                "components": [
                    {"name": "Entities", "type": "service", "description": "Domain objects", "responsibilities": ["Business rules", "Invariants"], "dependencies": []},
                    {"name": "Value Objects", "type": "service", "description": "Immutable values", "responsibilities": ["Type safety"], "dependencies": []}
                ]
            },
            {
                "name": "Infrastructure Layer",
                "description": "External concerns",
                "components": [
                    {"name": "Repositories", "type": "service", "description": "Data access", "responsibilities": ["Persistence"], "dependencies": ["Database"]},
                    {"name": "Database", "type": "database", "description": "Data store", "responsibilities": ["Storage"], "dependencies": []}
                ]
            }
        ],
        "data_flow": [
            {"from": "Client", "to": "Controllers", "description": "HTTP Request"},
            {"from": "Controllers", "to": "Use Cases", "description": "Command/Query"},
            {"from": "Use Cases", "to": "Entities", "description": "Domain logic"},
            {"from": "Use Cases", "to": "Repositories", "description": "Persistence"},
            {"from": "Repositories", "to": "Database", "description": "Data operation"}
        ],
        "key_decisions": [
            "Clean Architecture for maintainability",
            "TypeScript for type safety",
            "Dependency Inversion Principle",
            "CQRS for complex domains",
            "Zod for runtime validation"
        ],
        "security": [
            "Type-safe validation",
            "Strict TypeScript config",
            "Input sanitization",
            "JWT with refresh tokens",
            "Role-based access control"
        ],
        "scalability": [
            "Domain-driven design",
            "Modular architecture",
            "Easy to split into microservices",
            "Testable components",
            "Cache strategies"
        ]
    },
    "go": {
        "type": "Hexagonal Architecture",
        "layers": [
            {
                "name": "Adapters",
                "description": "External interfaces",
                "components": [
                    {"name": "HTTP Handlers", "type": "api", "description": "REST endpoints", "responsibilities": ["Request handling"], "dependencies": ["Ports"]},
                    {"name": "Repository Impl", "type": "service", "description": "Data access", "responsibilities": ["Database operations"], "dependencies": ["Database"]}
                ]
            },
            {
                "name": "Ports",
                "description": "Interface definitions",
                "components": [
                    {"name": "Service Interfaces", "type": "service", "description": "Business contracts", "responsibilities": ["API contracts"], "dependencies": []},
                    {"name": "Repository Interfaces", "type": "service", "description": "Data contracts", "responsibilities": ["Data contracts"], "dependencies": []}
                ]
            },
            {
                "name": "Core",
                "description": "Business logic",
                "components": [
                    {"name": "Services", "type": "service", "description": "Business services", "responsibilities": ["Business logic"], "dependencies": ["Domain"]},
                    {"name": "Domain", "type": "service", "description": "Domain models", "responsibilities": ["Domain rules"], "dependencies": []}
                ]
            }
        ],
        "data_flow": [
            {"from": "Client", "to": "HTTP Handlers", "description": "Request"},
            {"from": "HTTP Handlers", "to": "Services", "description": "Service call"},
            {"from": "Services", "to": "Repository Impl", "description": "Data access"},
            {"from": "Repository Impl", "to": "Database", "description": "Query"}
        ],
        "key_decisions": [
            "Hexagonal architecture for testability",
            "Interface-based design",
            "Goroutines for concurrency",
            "Context for cancellation",
            "Structured logging"
        ],
        "security": [
            "Input validation",
            "SQL injection prevention",
            "TLS everywhere",
            "Secret management",
            "Audit logging"
        ],
        "scalability": [
            "Goroutine-based concurrency",
            "Efficient memory usage",
            "Connection pooling",
            "Horizontal scaling",
            "gRPC for internal services"
        ]
    },
    "rust": {
        "type": "Actix Web Service",
        "layers": [
            {
                "name": "HTTP Layer",
                "description": "Web framework",
                "components": [
                    {"name": "Actix Handlers", "type": "api", "description": "Route handlers", "responsibilities": ["Request processing"], "dependencies": ["Services"]},
                    {"name": "Extractors", "type": "service", "description": "Request parsing", "responsibilities": ["Data extraction"], "dependencies": []}
                ]
            },
            {
                "name": "Service Layer",
                "description": "Business logic",
                "components": [
                    {"name": "Services", "type": "service", "description": "Business services", "responsibilities": ["Business logic"], "dependencies": ["Repository"]}
                ]
            },
            {
                "name": "Data Layer",
                "description": "Persistence",
                "components": [
                    {"name": "Repository", "type": "service", "description": "Data access", "responsibilities": ["CRUD"], "dependencies": ["Database"]},
                    {"name": "Database", "type": "database", "description": "PostgreSQL", "responsibilities": ["Storage"], "dependencies": []}
                ]
            }
        ],
        "data_flow": [
            {"from": "Client", "to": "Actix Handlers", "description": "HTTP Request"},
            {"from": "Actix Handlers", "to": "Services", "description": "Service call"},
            {"from": "Services", "to": "Repository", "description": "Data operation"},
            {"from": "Repository", "to": "Database", "description": "SQL query"}
        ],
        "key_decisions": [
            "Actix-web for performance",
            "Diesel for type-safe SQL",
            "Serde for serialization",
            "Tokio async runtime",
            "Error handling with thiserror"
        ],
        "security": [
            "Memory safety by default",
            "Type-safe SQL queries",
            "No null pointer exceptions",
            "Compile-time checks",
            "Secure by design"
        ],
        "scalability": [
            "Zero-cost abstractions",
            "Efficient memory usage",
            "Async I/O",
            "Multi-threaded runtime",
            "Low latency"
        ]
    }
}


@router.post("/generate", response_model=ArchitectureResult)
async def generate_architecture(request: GenerateArchitectureRequest):
    """Generate system architecture documentation"""
    
    tech_stack = request.tech_stack.lower()
    
    if tech_stack not in ARCH_TEMPLATES:
        tech_stack = "python"  # Default fallback
    
    template = ARCH_TEMPLATES[tech_stack]
    
    # Build layers with proper models
    layers = []
    for layer_data in template["layers"]:
        components = [
            ComponentDef(
                name=c["name"],
                type=c["type"],
                description=c["description"],
                responsibilities=c["responsibilities"],
                dependencies=c["dependencies"]
            )
            for c in layer_data["components"]
        ]
        layers.append(LayerDef(
            name=layer_data["name"],
            description=layer_data["description"],
            components=components
        ))
    
    result = ArchitectureResult(
        session_id=request.session_id,
        project_name=request.project_name,
        tech_stack=tech_stack,
        architecture_type=template["type"],
        layers=layers,
        data_flow=template["data_flow"],
        key_decisions=template["key_decisions"],
        security_considerations=template["security"],
        scalability_notes=template["scalability"],
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    architecture_store[request.session_id] = result.dict()
    
    return result


@router.get("/result/{session_id}")
async def get_architecture(session_id: str):
    """Get stored architecture for a session"""
    if session_id not in architecture_store:
        raise HTTPException(status_code=404, detail="Architecture not found")
    return architecture_store[session_id]
