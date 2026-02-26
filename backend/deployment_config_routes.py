"""
DEPLOYMENT CONFIG GENERATOR API
Generates Docker and Kubernetes deployment configurations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/deployment-config", tags=["deployment"])


class GenerateDeploymentRequest(BaseModel):
    session_id: str
    tech_stack: str
    project_name: str
    port: int = 8000
    replicas: int = 2
    include_docker: bool = True
    include_k8s: bool = True
    include_compose: bool = True


class DeploymentFile(BaseModel):
    name: str
    path: str
    content: str
    type: str  # dockerfile, compose, k8s


class DeploymentResult(BaseModel):
    session_id: str
    project_name: str
    tech_stack: str
    files: List[DeploymentFile]
    total_files: int
    created_at: str


deployment_store = {}


# Templates per tech stack
DOCKER_TEMPLATES = {
    "python": {
        "dockerfile": '''# Python FastAPI Application
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "{port}"]
''',
        "compose": '''version: '3.8'

services:
  {project_name}:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "{port}:{port}"
    environment:
      - DATABASE_URL=${{DATABASE_URL}}
      - API_KEY=${{API_KEY}}
      - DEBUG=false
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{port}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
''',
        "k8s_deployment": '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {project_name}
  labels:
    app: {project_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {project_name}
  template:
    metadata:
      labels:
        app: {project_name}
    spec:
      containers:
      - name: {project_name}
        image: {project_name}:latest
        ports:
        - containerPort: {port}
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {project_name}-secrets
              key: database-url
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: {port}
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: {port}
          initialDelaySeconds: 5
          periodSeconds: 10
''',
        "k8s_service": '''apiVersion: v1
kind: Service
metadata:
  name: {project_name}-service
spec:
  selector:
    app: {project_name}
  ports:
  - protocol: TCP
    port: 80
    targetPort: {port}
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {project_name}-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: {project_name}.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {project_name}-service
            port:
              number: 80
'''
    },
    "javascript": {
        "dockerfile": '''# Node.js Application
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1

CMD ["node", "src/index.js"]
''',
        "compose": '''version: '3.8'

services:
  {project_name}:
    build: .
    ports:
      - "{port}:{port}"
    environment:
      - NODE_ENV=production
      - PORT={port}
    env_file:
      - .env
    restart: unless-stopped
    networks:
      - app-network

  mongodb:
    image: mongo:7
    restart: unless-stopped
    volumes:
      - mongo-data:/data/db
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  mongo-data:
''',
        "k8s_deployment": '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {project_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {project_name}
  template:
    metadata:
      labels:
        app: {project_name}
    spec:
      containers:
      - name: {project_name}
        image: {project_name}:latest
        ports:
        - containerPort: {port}
        env:
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
''',
        "k8s_service": '''apiVersion: v1
kind: Service
metadata:
  name: {project_name}-service
spec:
  selector:
    app: {project_name}
  ports:
  - port: 80
    targetPort: {port}
  type: LoadBalancer
'''
    },
    "typescript": {
        "dockerfile": '''# TypeScript Application
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

EXPOSE {port}
CMD ["node", "dist/index.js"]
''',
        "compose": '''version: '3.8'

services:
  {project_name}:
    build: .
    ports:
      - "{port}:{port}"
    environment:
      - NODE_ENV=production
    env_file:
      - .env
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB={project_name}
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
''',
        "k8s_deployment": '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {project_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {project_name}
  template:
    metadata:
      labels:
        app: {project_name}
    spec:
      containers:
      - name: {project_name}
        image: {project_name}:latest
        ports:
        - containerPort: {port}
''',
        "k8s_service": '''apiVersion: v1
kind: Service
metadata:
  name: {project_name}-service
spec:
  selector:
    app: {project_name}
  ports:
  - port: 80
    targetPort: {port}
'''
    },
    "go": {
        "dockerfile": '''# Go Application - Multi-stage build
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server ./cmd/server

FROM alpine:3.18
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /app/server .

RUN adduser -D -g '' appuser
USER appuser

EXPOSE {port}
CMD ["./server"]
''',
        "compose": '''version: '3.8'

services:
  {project_name}:
    build: .
    ports:
      - "{port}:{port}"
    env_file:
      - .env
    restart: unless-stopped
''',
        "k8s_deployment": '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {project_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {project_name}
  template:
    metadata:
      labels:
        app: {project_name}
    spec:
      containers:
      - name: {project_name}
        image: {project_name}:latest
        ports:
        - containerPort: {port}
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "200m"
''',
        "k8s_service": '''apiVersion: v1
kind: Service
metadata:
  name: {project_name}-service
spec:
  selector:
    app: {project_name}
  ports:
  - port: 80
    targetPort: {port}
'''
    },
    "rust": {
        "dockerfile": '''# Rust Application - Multi-stage build
FROM rust:1.75-alpine AS builder

WORKDIR /app
RUN apk add --no-cache musl-dev
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/target/release/{project_name} .

RUN adduser -D -g '' appuser
USER appuser

EXPOSE {port}
CMD ["./{project_name}"]
''',
        "compose": '''version: '3.8'

services:
  {project_name}:
    build: .
    ports:
      - "{port}:{port}"
    restart: unless-stopped
''',
        "k8s_deployment": '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {project_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {project_name}
  template:
    metadata:
      labels:
        app: {project_name}
    spec:
      containers:
      - name: {project_name}
        image: {project_name}:latest
        ports:
        - containerPort: {port}
        resources:
          requests:
            memory: "32Mi"
            cpu: "25m"
          limits:
            memory: "64Mi"
            cpu: "100m"
''',
        "k8s_service": '''apiVersion: v1
kind: Service
metadata:
  name: {project_name}-service
spec:
  selector:
    app: {project_name}
  ports:
  - port: 80
    targetPort: {port}
'''
    }
}


@router.post("/generate", response_model=DeploymentResult)
async def generate_deployment_config(request: GenerateDeploymentRequest):
    """Generate Docker and Kubernetes deployment configurations"""
    
    tech_stack = request.tech_stack.lower()
    if tech_stack not in DOCKER_TEMPLATES:
        tech_stack = "python"
    
    templates = DOCKER_TEMPLATES[tech_stack]
    project_name = request.project_name.lower().replace(" ", "-").replace("_", "-")
    
    files = []
    
    # Generate Dockerfile
    if request.include_docker:
        dockerfile_content = templates["dockerfile"].format(
            port=request.port,
            project_name=project_name
        )
        files.append(DeploymentFile(
            name="Dockerfile",
            path="Dockerfile",
            content=dockerfile_content,
            type="dockerfile"
        ))
        
        # Add .dockerignore
        dockerignore = '''node_modules
.git
.env
*.log
__pycache__
.pytest_cache
.coverage
dist
build
*.egg-info
.venv
venv
'''
        files.append(DeploymentFile(
            name=".dockerignore",
            path=".dockerignore",
            content=dockerignore,
            type="dockerfile"
        ))
    
    # Generate docker-compose.yml
    if request.include_compose:
        compose_content = templates["compose"].format(
            port=request.port,
            project_name=project_name
        )
        files.append(DeploymentFile(
            name="docker-compose.yml",
            path="docker-compose.yml",
            content=compose_content,
            type="compose"
        ))
    
    # Generate Kubernetes manifests
    if request.include_k8s:
        k8s_deployment = templates["k8s_deployment"].format(
            port=request.port,
            project_name=project_name,
            replicas=request.replicas
        )
        files.append(DeploymentFile(
            name="deployment.yaml",
            path="k8s/deployment.yaml",
            content=k8s_deployment,
            type="k8s"
        ))
        
        k8s_service = templates["k8s_service"].format(
            port=request.port,
            project_name=project_name
        )
        files.append(DeploymentFile(
            name="service.yaml",
            path="k8s/service.yaml",
            content=k8s_service,
            type="k8s"
        ))
        
        # Add namespace
        namespace = f'''apiVersion: v1
kind: Namespace
metadata:
  name: {project_name}
'''
        files.append(DeploymentFile(
            name="namespace.yaml",
            path="k8s/namespace.yaml",
            content=namespace,
            type="k8s"
        ))
    
    result = DeploymentResult(
        session_id=request.session_id,
        project_name=project_name,
        tech_stack=tech_stack,
        files=files,
        total_files=len(files),
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    deployment_store[request.session_id] = result.dict()
    
    return result


@router.get("/result/{session_id}")
async def get_deployment_config(session_id: str):
    """Get stored deployment config"""
    if session_id not in deployment_store:
        raise HTTPException(status_code=404, detail="Deployment config not found")
    return deployment_store[session_id]
