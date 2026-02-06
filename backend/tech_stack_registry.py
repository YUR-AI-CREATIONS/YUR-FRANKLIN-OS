"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    TECHNOLOGY STACK REGISTRY                                 ║
║                                                                              ║
║  Comprehensive catalog of cutting-edge technologies available for            ║
║  code generation and deployment. Fully extensible adapter architecture.      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


# ============================================================================
#                           TECHNOLOGY CATEGORIES
# ============================================================================

class TechCategory(Enum):
    CLOUD_PROVIDER = "cloud_provider"
    CONTAINER_ORCHESTRATION = "container_orchestration"
    SERVERLESS = "serverless"
    DATABASE = "database"
    CACHE = "cache"
    AUTHENTICATION = "authentication"
    FRONTEND_FRAMEWORK = "frontend_framework"
    BACKEND_FRAMEWORK = "backend_framework"
    CSS_FRAMEWORK = "css_framework"
    CI_CD = "ci_cd"
    MONITORING = "monitoring"
    MESSAGE_QUEUE = "message_queue"
    STORAGE = "storage"
    CDN = "cdn"
    SEARCH = "search"
    AI_ML = "ai_ml"


# ============================================================================
#                           TECHNOLOGY DEFINITIONS
# ============================================================================

@dataclass
class TechOption:
    """Individual technology option"""
    id: str
    name: str
    category: TechCategory
    description: str
    tier: str  # free, pro, enterprise
    features: List[str]
    config_schema: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    incompatible_with: List[str] = field(default_factory=list)
    setup_complexity: str = "medium"  # low, medium, high
    documentation_url: Optional[str] = None


class TechStackRegistry:
    """
    Central registry of all available technologies.
    Provides selection, validation, and configuration management.
    """
    
    def __init__(self):
        self.technologies: Dict[str, TechOption] = {}
        self._register_all_technologies()
    
    def _register_all_technologies(self):
        """Register all available technology options"""
        
        # ════════════════════════════════════════════════════════════════════
        #                         CLOUD PROVIDERS
        # ════════════════════════════════════════════════════════════════════
        
        self._register(TechOption(
            id="aws",
            name="Amazon Web Services (AWS)",
            category=TechCategory.CLOUD_PROVIDER,
            description="Industry-leading cloud platform with 200+ services",
            tier="pro",
            features=[
                "EC2 Compute", "S3 Storage", "RDS Databases", "Lambda Serverless",
                "EKS Kubernetes", "CloudFront CDN", "Route53 DNS", "IAM Security",
                "CloudWatch Monitoring", "SQS/SNS Messaging", "ElastiCache"
            ],
            config_schema={
                "region": {"type": "string", "default": "us-east-1"},
                "access_key_id": {"type": "string", "secret": True},
                "secret_access_key": {"type": "string", "secret": True},
                "profile": {"type": "string", "optional": True}
            },
            setup_complexity="high",
            documentation_url="https://docs.aws.amazon.com"
        ))
        
        self._register(TechOption(
            id="gcp",
            name="Google Cloud Platform (GCP)",
            category=TechCategory.CLOUD_PROVIDER,
            description="Google's cloud with AI/ML leadership",
            tier="pro",
            features=[
                "Compute Engine", "Cloud Storage", "Cloud SQL", "Cloud Functions",
                "GKE Kubernetes", "Cloud CDN", "Cloud DNS", "IAM",
                "Cloud Monitoring", "Pub/Sub", "Memorystore", "Vertex AI"
            ],
            config_schema={
                "project_id": {"type": "string"},
                "region": {"type": "string", "default": "us-central1"},
                "credentials_json": {"type": "string", "secret": True}
            },
            setup_complexity="high",
            documentation_url="https://cloud.google.com/docs"
        ))
        
        self._register(TechOption(
            id="azure",
            name="Microsoft Azure",
            category=TechCategory.CLOUD_PROVIDER,
            description="Enterprise-focused cloud with Microsoft integration",
            tier="pro",
            features=[
                "Virtual Machines", "Blob Storage", "Azure SQL", "Azure Functions",
                "AKS Kubernetes", "Azure CDN", "Azure DNS", "Azure AD",
                "Azure Monitor", "Service Bus", "Redis Cache", "Azure OpenAI"
            ],
            config_schema={
                "subscription_id": {"type": "string"},
                "tenant_id": {"type": "string"},
                "client_id": {"type": "string"},
                "client_secret": {"type": "string", "secret": True},
                "region": {"type": "string", "default": "eastus"}
            },
            setup_complexity="high",
            documentation_url="https://docs.microsoft.com/azure"
        ))
        
        # ════════════════════════════════════════════════════════════════════
        #                      PLATFORM AS A SERVICE
        # ════════════════════════════════════════════════════════════════════
        
        self._register(TechOption(
            id="vercel",
            name="Vercel",
            category=TechCategory.SERVERLESS,
            description="Frontend cloud platform with instant deployments",
            tier="free",
            features=[
                "Instant Deployments", "Edge Functions", "Serverless Functions",
                "Preview Deployments", "Analytics", "Custom Domains",
                "Automatic HTTPS", "Git Integration", "Next.js Optimized"
            ],
            config_schema={
                "token": {"type": "string", "secret": True},
                "team_id": {"type": "string", "optional": True},
                "project_name": {"type": "string"}
            },
            setup_complexity="low",
            documentation_url="https://vercel.com/docs"
        ))
        
        self._register(TechOption(
            id="railway",
            name="Railway",
            category=TechCategory.SERVERLESS,
            description="Modern deployment platform with database hosting",
            tier="free",
            features=[
                "One-Click Deploy", "Auto Scaling", "Built-in Databases",
                "Environment Variables", "Preview Environments", "Cron Jobs",
                "Private Networking", "GitHub Integration", "Docker Support"
            ],
            config_schema={
                "token": {"type": "string", "secret": True},
                "project_id": {"type": "string", "optional": True}
            },
            setup_complexity="low",
            documentation_url="https://docs.railway.app"
        ))
        
        self._register(TechOption(
            id="render",
            name="Render",
            category=TechCategory.SERVERLESS,
            description="Unified cloud for web services and databases",
            tier="free",
            features=[
                "Web Services", "Static Sites", "Background Workers",
                "Cron Jobs", "PostgreSQL", "Redis", "Private Services",
                "Auto Deploy", "Custom Domains", "DDoS Protection"
            ],
            config_schema={
                "api_key": {"type": "string", "secret": True},
                "owner_id": {"type": "string", "optional": True}
            },
            setup_complexity="low",
            documentation_url="https://render.com/docs"
        ))
        
        self._register(TechOption(
            id="fly_io",
            name="Fly.io",
            category=TechCategory.SERVERLESS,
            description="Deploy apps close to users with edge computing",
            tier="free",
            features=[
                "Edge Deployment", "Global Distribution", "Persistent Storage",
                "Private Networking", "Auto Scaling", "Machines API",
                "Postgres Clusters", "Redis", "Docker Native"
            ],
            config_schema={
                "api_token": {"type": "string", "secret": True},
                "org": {"type": "string", "optional": True}
            },
            setup_complexity="medium",
            documentation_url="https://fly.io/docs"
        ))
        
        # ════════════════════════════════════════════════════════════════════
        #                    CONTAINER ORCHESTRATION
        # ════════════════════════════════════════════════════════════════════
        
        self._register(TechOption(
            id="kubernetes",
            name="Kubernetes (K8s)",
            category=TechCategory.CONTAINER_ORCHESTRATION,
            description="Production-grade container orchestration",
            tier="pro",
            features=[
                "Pod Orchestration", "Service Discovery", "Load Balancing",
                "Auto Scaling (HPA/VPA)", "Rolling Updates", "Self-Healing",
                "Secret Management", "ConfigMaps", "Persistent Volumes",
                "Network Policies", "RBAC", "Helm Charts"
            ],
            config_schema={
                "kubeconfig": {"type": "string", "secret": True},
                "context": {"type": "string", "optional": True},
                "namespace": {"type": "string", "default": "default"}
            },
            setup_complexity="high",
            documentation_url="https://kubernetes.io/docs"
        ))
        
        self._register(TechOption(
            id="docker",
            name="Docker",
            category=TechCategory.CONTAINER_ORCHESTRATION,
            description="Industry-standard containerization",
            tier="free",
            features=[
                "Container Images", "Dockerfile", "Docker Compose",
                "Multi-stage Builds", "Volume Mounts", "Network Isolation",
                "Docker Hub Registry", "BuildKit", "Health Checks"
            ],
            config_schema={
                "registry_url": {"type": "string", "default": "docker.io"},
                "username": {"type": "string", "optional": True},
                "password": {"type": "string", "secret": True, "optional": True}
            },
            setup_complexity="low",
            documentation_url="https://docs.docker.com"
        ))
        
        self._register(TechOption(
            id="docker_swarm",
            name="Docker Swarm",
            category=TechCategory.CONTAINER_ORCHESTRATION,
            description="Native Docker clustering and orchestration",
            tier="free",
            features=[
                "Service Orchestration", "Load Balancing", "Rolling Updates",
                "Service Discovery", "Secrets Management", "Configs",
                "Overlay Networks", "Stack Deployments"
            ],
            config_schema={
                "manager_ip": {"type": "string"},
                "join_token": {"type": "string", "secret": True}
            },
            setup_complexity="medium",
            documentation_url="https://docs.docker.com/engine/swarm"
        ))
        
        # ════════════════════════════════════════════════════════════════════
        #                           DATABASES
        # ════════════════════════════════════════════════════════════════════
        
        self._register(TechOption(
            id="postgresql",
            name="PostgreSQL",
            category=TechCategory.DATABASE,
            description="Advanced open-source relational database",
            tier="free",
            features=[
                "ACID Compliance", "JSON/JSONB Support", "Full-Text Search",
                "Geospatial (PostGIS)", "Partitioning", "Replication",
                "Row-Level Security", "Triggers", "Stored Procedures",
                "Extensions", "Foreign Data Wrappers"
            ],
            config_schema={
                "host": {"type": "string"},
                "port": {"type": "integer", "default": 5432},
                "database": {"type": "string"},
                "username": {"type": "string"},
                "password": {"type": "string", "secret": True},
                "ssl_mode": {"type": "string", "default": "require"}
            },
            setup_complexity="medium",
            documentation_url="https://www.postgresql.org/docs"
        ))
        
        self._register(TechOption(
            id="supabase",
            name="Supabase",
            category=TechCategory.DATABASE,
            description="Open-source Firebase alternative with PostgreSQL",
            tier="free",
            features=[
                "PostgreSQL Database", "Real-time Subscriptions", "Auth",
                "Storage", "Edge Functions", "Auto-generated APIs",
                "Row Level Security", "Database Webhooks", "Branching",
                "AI Vector Store", "GraphQL"
            ],
            config_schema={
                "url": {"type": "string"},
                "anon_key": {"type": "string", "secret": True},
                "service_role_key": {"type": "string", "secret": True}
            },
            setup_complexity="low",
            documentation_url="https://supabase.com/docs"
        ))
        
        self._register(TechOption(
            id="mongodb",
            name="MongoDB",
            category=TechCategory.DATABASE,
            description="Document-oriented NoSQL database",
            tier="free",
            features=[
                "Document Model", "Flexible Schema", "Aggregation Pipeline",
                "Atlas Search", "Time Series", "Sharding", "Replication",
                "Change Streams", "Transactions", "GridFS"
            ],
            config_schema={
                "connection_string": {"type": "string", "secret": True},
                "database": {"type": "string"}
            },
            setup_complexity="low",
            documentation_url="https://docs.mongodb.com"
        ))
        
        self._register(TechOption(
            id="planetscale",
            name="PlanetScale",
            category=TechCategory.DATABASE,
            description="Serverless MySQL platform with branching",
            tier="free",
            features=[
                "MySQL Compatible", "Database Branching", "Non-blocking Schema Changes",
                "Horizontal Sharding", "Connection Pooling", "Insights",
                "Auto Scaling", "Point-in-time Recovery"
            ],
            config_schema={
                "host": {"type": "string"},
                "username": {"type": "string"},
                "password": {"type": "string", "secret": True},
                "database": {"type": "string"}
            },
            setup_complexity="low",
            documentation_url="https://docs.planetscale.com"
        ))
        
        self._register(TechOption(
            id="neon",
            name="Neon",
            category=TechCategory.DATABASE,
            description="Serverless PostgreSQL with branching",
            tier="free",
            features=[
                "Serverless PostgreSQL", "Database Branching", "Auto-suspend",
                "Scale to Zero", "Point-in-time Recovery", "Pooler",
                "Logical Replication", "Extensions"
            ],
            config_schema={
                "connection_string": {"type": "string", "secret": True}
            },
            setup_complexity="low",
            documentation_url="https://neon.tech/docs"
        ))
        
        self._register(TechOption(
            id="cockroachdb",
            name="CockroachDB",
            category=TechCategory.DATABASE,
            description="Distributed SQL database for global scale",
            tier="free",
            features=[
                "Distributed SQL", "PostgreSQL Compatible", "Multi-region",
                "Serializable Isolation", "Auto Rebalancing", "Geo-partitioning",
                "Survivability", "Change Data Capture"
            ],
            config_schema={
                "connection_string": {"type": "string", "secret": True},
                "cluster": {"type": "string"}
            },
            setup_complexity="medium",
            documentation_url="https://www.cockroachlabs.com/docs"
        ))
        
        # ════════════════════════════════════════════════════════════════════
        #                             CACHE
        # ════════════════════════════════════════════════════════════════════
        
        self._register(TechOption(
            id="redis",
            name="Redis",
            category=TechCategory.CACHE,
            description="In-memory data store for caching and messaging",
            tier="free",
            features=[
                "Key-Value Store", "Pub/Sub", "Streams", "Lua Scripting",
                "Transactions", "Persistence", "Cluster Mode", "Sentinel",
                "JSON Support", "Search", "Time Series", "Graph"
            ],
            config_schema={
                "host": {"type": "string"},
                "port": {"type": "integer", "default": 6379},
                "password": {"type": "string", "secret": True, "optional": True},
                "ssl": {"type": "boolean", "default": False}
            },
            setup_complexity="low",
            documentation_url="https://redis.io/docs"
        ))
        
        self._register(TechOption(
            id="upstash",
            name="Upstash",
            category=TechCategory.CACHE,
            description="Serverless Redis and Kafka",
            tier="free",
            features=[
                "Serverless Redis", "REST API", "Global Replication",
                "Pay-per-request", "Kafka", "QStash (Message Queue)",
                "Edge Caching", "Vector Database"
            ],
            config_schema={
                "url": {"type": "string"},
                "token": {"type": "string", "secret": True}
            },
            setup_complexity="low",
            documentation_url="https://docs.upstash.com"
        ))
        
        self._register(TechOption(
            id="memcached",
            name="Memcached",
            category=TechCategory.CACHE,
            description="High-performance distributed memory cache",
            tier="free",
            features=[
                "Distributed Caching", "Simple Key-Value", "LRU Eviction",
                "Multi-threaded", "Low Latency"
            ],
            config_schema={
                "servers": {"type": "array", "items": {"type": "string"}},
                "username": {"type": "string", "optional": True},
                "password": {"type": "string", "secret": True, "optional": True}
            },
            setup_complexity="low",
            documentation_url="https://memcached.org"
        ))
        
        # ════════════════════════════════════════════════════════════════════
        #                         AUTHENTICATION
        # ════════════════════════════════════════════════════════════════════
        
        self._register(TechOption(
            id="auth0",
            name="Auth0",
            category=TechCategory.AUTHENTICATION,
            description="Enterprise identity platform",
            tier="free",
            features=[
                "Universal Login", "Social Connections", "MFA",
                "Passwordless", "RBAC", "Organizations", "Actions",
                "Breached Password Detection", "Anomaly Detection"
            ],
            config_schema={
                "domain": {"type": "string"},
                "client_id": {"type": "string"},
                "client_secret": {"type": "string", "secret": True},
                "audience": {"type": "string", "optional": True}
            },
            setup_complexity="medium",
            documentation_url="https://auth0.com/docs"
        ))
        
        self._register(TechOption(
            id="clerk",
            name="Clerk",
            category=TechCategory.AUTHENTICATION,
            description="Modern authentication with beautiful UI",
            tier="free",
            features=[
                "Pre-built Components", "Social Login", "MFA",
                "Organizations", "User Management", "Sessions",
                "JWTs", "Webhooks", "React/Next.js SDK"
            ],
            config_schema={
                "publishable_key": {"type": "string"},
                "secret_key": {"type": "string", "secret": True}
            },
            setup_complexity="low",
            documentation_url="https://clerk.com/docs"
        ))
        
        self._register(TechOption(
            id="firebase_auth",
            name="Firebase Authentication",
            category=TechCategory.AUTHENTICATION,
            description="Google's authentication service",
            tier="free",
            features=[
                "Email/Password", "Social Providers", "Phone Auth",
                "Anonymous Auth", "Custom Claims", "Multi-tenancy",
                "Identity Platform", "App Check"
            ],
            config_schema={
                "api_key": {"type": "string"},
                "auth_domain": {"type": "string"},
                "project_id": {"type": "string"}
            },
            setup_complexity="low",
            documentation_url="https://firebase.google.com/docs/auth"
        ))
        
        self._register(TechOption(
            id="supabase_auth",
            name="Supabase Auth",
            category=TechCategory.AUTHENTICATION,
            description="Open-source auth with PostgreSQL RLS",
            tier="free",
            features=[
                "Email/Password", "Magic Links", "Social Providers",
                "Phone Auth", "Row Level Security", "Custom Claims",
                "Multi-factor Auth", "SSO (SAML)"
            ],
            config_schema={
                "url": {"type": "string"},
                "anon_key": {"type": "string", "secret": True}
            },
            setup_complexity="low",
            documentation_url="https://supabase.com/docs/guides/auth"
        ))
        
        # ════════════════════════════════════════════════════════════════════
        #                       FRONTEND FRAMEWORKS
        # ════════════════════════════════════════════════════════════════════
        
        self._register(TechOption(
            id="nextjs",
            name="Next.js",
            category=TechCategory.FRONTEND_FRAMEWORK,
            description="React framework for production",
            tier="free",
            features=[
                "Server Components", "App Router", "API Routes",
                "Static Generation", "SSR", "ISR", "Image Optimization",
                "Middleware", "Edge Runtime", "Turbopack"
            ],
            config_schema={
                "version": {"type": "string", "default": "14"}
            },
            setup_complexity="low",
            documentation_url="https://nextjs.org/docs"
        ))
        
        self._register(TechOption(
            id="react",
            name="React",
            category=TechCategory.FRONTEND_FRAMEWORK,
            description="Library for building user interfaces",
            tier="free",
            features=[
                "Component-Based", "Virtual DOM", "Hooks",
                "Context API", "Suspense", "Concurrent Mode",
                "Server Components", "React 19 Actions"
            ],
            config_schema={
                "version": {"type": "string", "default": "19"}
            },
            setup_complexity="low",
            documentation_url="https://react.dev"
        ))
        
        self._register(TechOption(
            id="vue",
            name="Vue.js",
            category=TechCategory.FRONTEND_FRAMEWORK,
            description="Progressive JavaScript framework",
            tier="free",
            features=[
                "Composition API", "Reactive System", "Single-File Components",
                "Vue Router", "Pinia State", "Nuxt.js", "Vite"
            ],
            config_schema={
                "version": {"type": "string", "default": "3"}
            },
            setup_complexity="low",
            documentation_url="https://vuejs.org"
        ))
        
        self._register(TechOption(
            id="svelte",
            name="Svelte/SvelteKit",
            category=TechCategory.FRONTEND_FRAMEWORK,
            description="Compiler-based framework",
            tier="free",
            features=[
                "No Virtual DOM", "Compile-time Optimization", "Stores",
                "SvelteKit", "SSR", "Form Actions", "Load Functions"
            ],
            config_schema={
                "kit": {"type": "boolean", "default": True}
            },
            setup_complexity="low",
            documentation_url="https://kit.svelte.dev"
        ))
        
        self._register(TechOption(
            id="astro",
            name="Astro",
            category=TechCategory.FRONTEND_FRAMEWORK,
            description="Content-focused web framework",
            tier="free",
            features=[
                "Zero JS by Default", "Islands Architecture", "Multi-framework",
                "Content Collections", "View Transitions", "SSR", "Hybrid Rendering"
            ],
            config_schema={
                "version": {"type": "string", "default": "4"}
            },
            setup_complexity="low",
            documentation_url="https://docs.astro.build"
        ))
        
        # ════════════════════════════════════════════════════════════════════
        #                       BACKEND FRAMEWORKS
        # ════════════════════════════════════════════════════════════════════
        
        self._register(TechOption(
            id="fastapi",
            name="FastAPI",
            category=TechCategory.BACKEND_FRAMEWORK,
            description="Modern, fast Python web framework",
            tier="free",
            features=[
                "Async Support", "Auto OpenAPI", "Type Hints",
                "Dependency Injection", "OAuth2", "WebSockets",
                "Background Tasks", "Middleware"
            ],
            config_schema={
                "version": {"type": "string", "default": "0.109"}
            },
            setup_complexity="low",
            documentation_url="https://fastapi.tiangolo.com"
        ))
        
        self._register(TechOption(
            id="express",
            name="Express.js",
            category=TechCategory.BACKEND_FRAMEWORK,
            description="Minimal Node.js web framework",
            tier="free",
            features=[
                "Middleware", "Routing", "Template Engines",
                "Error Handling", "Static Files", "CORS"
            ],
            config_schema={
                "version": {"type": "string", "default": "4"}
            },
            setup_complexity="low",
            documentation_url="https://expressjs.com"
        ))
        
        self._register(TechOption(
            id="nestjs",
            name="NestJS",
            category=TechCategory.BACKEND_FRAMEWORK,
            description="Progressive Node.js framework",
            tier="free",
            features=[
                "TypeScript", "Decorators", "Modules", "Dependency Injection",
                "GraphQL", "WebSockets", "Microservices", "CQRS"
            ],
            config_schema={
                "version": {"type": "string", "default": "10"}
            },
            setup_complexity="medium",
            documentation_url="https://docs.nestjs.com"
        ))
        
        self._register(TechOption(
            id="django",
            name="Django",
            category=TechCategory.BACKEND_FRAMEWORK,
            description="High-level Python web framework",
            tier="free",
            features=[
                "ORM", "Admin Interface", "Forms", "Authentication",
                "Middleware", "Templates", "Security", "REST Framework"
            ],
            config_schema={
                "version": {"type": "string", "default": "5"}
            },
            setup_complexity="medium",
            documentation_url="https://docs.djangoproject.com"
        ))
        
        self._register(TechOption(
            id="golang",
            name="Go (Gin/Echo)",
            category=TechCategory.BACKEND_FRAMEWORK,
            description="High-performance Go web frameworks",
            tier="free",
            features=[
                "Fast Routing", "Middleware", "JSON Validation",
                "Error Management", "Rendering", "Concurrency"
            ],
            config_schema={
                "framework": {"type": "string", "enum": ["gin", "echo", "fiber"], "default": "gin"}
            },
            setup_complexity="medium",
            documentation_url="https://gin-gonic.com/docs"
        ))
        
        self._register(TechOption(
            id="rust_actix",
            name="Rust (Actix/Axum)",
            category=TechCategory.BACKEND_FRAMEWORK,
            description="Blazing fast Rust web frameworks",
            tier="pro",
            features=[
                "Memory Safety", "Zero-Cost Abstractions", "Async",
                "WebSockets", "Middleware", "Extractors"
            ],
            config_schema={
                "framework": {"type": "string", "enum": ["actix", "axum"], "default": "axum"}
            },
            setup_complexity="high",
            documentation_url="https://actix.rs/docs"
        ))
        
        # ════════════════════════════════════════════════════════════════════
        #                         CSS FRAMEWORKS
        # ════════════════════════════════════════════════════════════════════
        
        self._register(TechOption(
            id="tailwindcss",
            name="Tailwind CSS",
            category=TechCategory.CSS_FRAMEWORK,
            description="Utility-first CSS framework",
            tier="free",
            features=[
                "Utility Classes", "JIT Compiler", "Dark Mode",
                "Responsive Design", "Custom Plugins", "Typography Plugin",
                "Forms Plugin", "Container Queries"
            ],
            config_schema={
                "version": {"type": "string", "default": "3"},
                "plugins": {"type": "array", "items": {"type": "string"}}
            },
            setup_complexity="low",
            documentation_url="https://tailwindcss.com/docs"
        ))
        
        self._register(TechOption(
            id="shadcn",
            name="shadcn/ui",
            category=TechCategory.CSS_FRAMEWORK,
            description="Re-usable components built with Radix and Tailwind",
            tier="free",
            features=[
                "Copy-Paste Components", "Radix Primitives", "Tailwind Styling",
                "Dark Mode", "Accessible", "Customizable", "TypeScript"
            ],
            config_schema={
                "style": {"type": "string", "enum": ["default", "new-york"], "default": "default"}
            },
            dependencies=["tailwindcss"],
            setup_complexity="low",
            documentation_url="https://ui.shadcn.com"
        ))
        
        # ════════════════════════════════════════════════════════════════════
        #                             CI/CD
        # ════════════════════════════════════════════════════════════════════
        
        self._register(TechOption(
            id="github_actions",
            name="GitHub Actions",
            category=TechCategory.CI_CD,
            description="CI/CD built into GitHub",
            tier="free",
            features=[
                "Workflow Automation", "Matrix Builds", "Artifacts",
                "Secrets Management", "Environments", "Reusable Workflows",
                "Self-hosted Runners"
            ],
            config_schema={
                "workflows_path": {"type": "string", "default": ".github/workflows"}
            },
            setup_complexity="low",
            documentation_url="https://docs.github.com/actions"
        ))
        
        self._register(TechOption(
            id="gitlab_ci",
            name="GitLab CI/CD",
            category=TechCategory.CI_CD,
            description="Integrated CI/CD in GitLab",
            tier="free",
            features=[
                "Pipeline as Code", "Auto DevOps", "Container Registry",
                "Environments", "Review Apps", "Security Scanning"
            ],
            config_schema={
                "config_file": {"type": "string", "default": ".gitlab-ci.yml"}
            },
            setup_complexity="medium",
            documentation_url="https://docs.gitlab.com/ee/ci"
        ))
        
        # ════════════════════════════════════════════════════════════════════
        #                           AI/ML
        # ════════════════════════════════════════════════════════════════════
        
        self._register(TechOption(
            id="openai",
            name="OpenAI API",
            category=TechCategory.AI_ML,
            description="GPT models, DALL-E, Whisper, embeddings",
            tier="pro",
            features=[
                "GPT-4/GPT-5", "DALL-E 3", "Whisper", "Embeddings",
                "Fine-tuning", "Assistants API", "Function Calling"
            ],
            config_schema={
                "api_key": {"type": "string", "secret": True},
                "organization": {"type": "string", "optional": True}
            },
            setup_complexity="low",
            documentation_url="https://platform.openai.com/docs"
        ))
        
        self._register(TechOption(
            id="anthropic",
            name="Anthropic Claude",
            category=TechCategory.AI_ML,
            description="Claude models with long context",
            tier="pro",
            features=[
                "Claude 3.5/4", "200K Context", "Vision", "Tool Use",
                "Constitutional AI"
            ],
            config_schema={
                "api_key": {"type": "string", "secret": True}
            },
            setup_complexity="low",
            documentation_url="https://docs.anthropic.com"
        ))
        
        self._register(TechOption(
            id="langchain",
            name="LangChain",
            category=TechCategory.AI_ML,
            description="Framework for LLM applications",
            tier="free",
            features=[
                "Chains", "Agents", "RAG", "Memory",
                "Callbacks", "Tools", "LangSmith", "LangServe"
            ],
            config_schema={},
            setup_complexity="medium",
            documentation_url="https://python.langchain.com/docs"
        ))
        
    def _register(self, tech: TechOption):
        """Register a technology option"""
        self.technologies[tech.id] = tech
    
    def get_by_category(self, category: TechCategory) -> List[TechOption]:
        """Get all technologies in a category"""
        return [t for t in self.technologies.values() if t.category == category]
    
    def get_by_tier(self, tier: str) -> List[TechOption]:
        """Get all technologies by tier (free, pro, enterprise)"""
        return [t for t in self.technologies.values() if t.tier == tier]
    
    def get(self, tech_id: str) -> Optional[TechOption]:
        """Get a specific technology by ID"""
        return self.technologies.get(tech_id)
    
    def search(self, query: str) -> List[TechOption]:
        """Search technologies by name or features"""
        query_lower = query.lower()
        results = []
        
        for tech in self.technologies.values():
            if (query_lower in tech.name.lower() or 
                query_lower in tech.description.lower() or
                any(query_lower in f.lower() for f in tech.features)):
                results.append(tech)
        
        return results
    
    def validate_stack(self, tech_ids: List[str]) -> Dict[str, Any]:
        """Validate a technology stack for compatibility"""
        issues = []
        warnings = []
        selected = [self.get(tid) for tid in tech_ids if self.get(tid)]
        
        # Check for incompatibilities
        for tech in selected:
            for incompat in tech.incompatible_with:
                if incompat in tech_ids:
                    issues.append(f"{tech.name} is incompatible with {incompat}")
        
        # Check for missing dependencies
        for tech in selected:
            for dep in tech.dependencies:
                if dep not in tech_ids:
                    warnings.append(f"{tech.name} recommends {dep}")
        
        # Check for required categories
        categories_present = set(t.category for t in selected)
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "categories_covered": [c.value for c in categories_present],
            "total_technologies": len(selected)
        }
    
    def get_catalog(self) -> Dict[str, Any]:
        """Get complete technology catalog organized by category"""
        catalog = {}
        
        for category in TechCategory:
            techs = self.get_by_category(category)
            catalog[category.value] = [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "tier": t.tier,
                    "features": t.features[:5],  # Top 5 features
                    "complexity": t.setup_complexity
                } for t in techs
            ]
        
        return catalog


# Global registry instance
tech_registry = TechStackRegistry()
