"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          BUILD ENGINE                                        ║
║                                                                              ║
║  Generates production-ready code from specifications.                        ║
║  Supports multiple tech stacks and deployment targets.                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json

from tech_stack_registry import TechStackRegistry, TechCategory, tech_registry


@dataclass
class BuildArtifact:
    """Generated code artifact"""
    id: str
    path: str
    content: str
    artifact_type: str  # file, directory, config
    language: str
    generated_at: str
    checksum: Optional[str] = None


@dataclass
class BuildManifest:
    """Complete build manifest"""
    id: str
    project_name: str
    tech_stack: Dict[str, str]
    artifacts: List[BuildArtifact]
    deployment_config: Dict[str, Any]
    environment_variables: Dict[str, str]
    created_at: str
    status: str = "pending"


class BuildEngine:
    """
    Code Generation Engine
    
    Transforms specifications into production-ready code across
    multiple technology stacks.
    """
    
    def __init__(self):
        self.registry = tech_registry
        self.artifacts: List[BuildArtifact] = []
        self.manifest: Optional[BuildManifest] = None
        
    def configure_stack(self, selections: Dict[str, str]) -> Dict[str, Any]:
        """
        Configure the technology stack for build.
        
        Args:
            selections: Dict mapping category to tech_id
                e.g., {"database": "postgresql", "frontend": "nextjs"}
        """
        resolved = {}
        missing = []
        
        for category, tech_id in selections.items():
            tech = self.registry.get(tech_id)
            if tech:
                resolved[category] = {
                    "id": tech.id,
                    "name": tech.name,
                    "config_schema": tech.config_schema
                }
            else:
                missing.append(f"{category}: {tech_id}")
        
        validation = self.registry.validate_stack(list(selections.values()))
        
        return {
            "configured": resolved,
            "missing": missing,
            "validation": validation
        }
    
    def generate_project(self, specification: Dict[str, Any], 
                        tech_stack: Dict[str, str],
                        project_name: str) -> BuildManifest:
        """
        Generate complete project from specification.
        
        Args:
            specification: The formal specification from SGP
            tech_stack: Selected technologies by category
            project_name: Name of the project
        """
        build_id = str(uuid.uuid4())
        self.artifacts = []
        
        # Extract components from specification
        components = specification.get("components", [])
        data_model = specification.get("data_model", {})
        api_contracts = specification.get("api_contracts", [])
        security = specification.get("security", {})
        
        # Generate based on selected stack
        frontend_id = tech_stack.get("frontend_framework", "react")
        backend_id = tech_stack.get("backend_framework", "fastapi")
        database_id = tech_stack.get("database", "postgresql")
        css_id = tech_stack.get("css_framework", "tailwindcss")
        
        # Generate frontend
        if frontend_id:
            self._generate_frontend(project_name, frontend_id, css_id, specification)
        
        # Generate backend
        if backend_id:
            self._generate_backend(project_name, backend_id, database_id, 
                                  data_model, api_contracts, security)
        
        # Generate database schemas
        if database_id:
            self._generate_database(project_name, database_id, data_model)
        
        # Generate Docker configuration
        self._generate_docker(project_name, tech_stack)
        
        # Generate CI/CD
        ci_id = tech_stack.get("ci_cd", "github_actions")
        if ci_id:
            self._generate_cicd(project_name, ci_id, tech_stack)
        
        # Generate deployment configs
        deployment_config = self._generate_deployment_config(tech_stack)
        
        # Generate environment template
        env_vars = self._generate_env_template(tech_stack)
        
        # Create manifest
        self.manifest = BuildManifest(
            id=build_id,
            project_name=project_name,
            tech_stack=tech_stack,
            artifacts=self.artifacts,
            deployment_config=deployment_config,
            environment_variables=env_vars,
            created_at=datetime.now(timezone.utc).isoformat(),
            status="generated"
        )
        
        return self.manifest
    
    def _add_artifact(self, path: str, content: str, 
                     artifact_type: str, language: str):
        """Add a build artifact"""
        artifact = BuildArtifact(
            id=str(uuid.uuid4()),
            path=path,
            content=content,
            artifact_type=artifact_type,
            language=language,
            generated_at=datetime.now(timezone.utc).isoformat()
        )
        self.artifacts.append(artifact)
    
    def _generate_frontend(self, project_name: str, framework_id: str, 
                          css_id: str, spec: Dict):
        """Generate frontend code"""
        
        if framework_id == "nextjs":
            # Next.js App Router structure
            self._add_artifact(
                f"{project_name}/frontend/package.json",
                self._nextjs_package_json(project_name, css_id),
                "file", "json"
            )
            
            self._add_artifact(
                f"{project_name}/frontend/app/layout.tsx",
                self._nextjs_layout(project_name),
                "file", "typescript"
            )
            
            self._add_artifact(
                f"{project_name}/frontend/app/page.tsx",
                self._nextjs_home_page(spec),
                "file", "typescript"
            )
            
            if css_id == "tailwindcss":
                self._add_artifact(
                    f"{project_name}/frontend/tailwind.config.ts",
                    self._tailwind_config(),
                    "file", "typescript"
                )
                
        elif framework_id == "react":
            self._add_artifact(
                f"{project_name}/frontend/package.json",
                self._react_package_json(project_name, css_id),
                "file", "json"
            )
            
            self._add_artifact(
                f"{project_name}/frontend/src/App.tsx",
                self._react_app(spec),
                "file", "typescript"
            )
    
    def _generate_backend(self, project_name: str, framework_id: str,
                         database_id: str, data_model: Dict, 
                         api_contracts: List, security: Dict):
        """Generate backend code"""
        
        if framework_id == "fastapi":
            self._add_artifact(
                f"{project_name}/backend/requirements.txt",
                self._fastapi_requirements(database_id),
                "file", "text"
            )
            
            self._add_artifact(
                f"{project_name}/backend/app/main.py",
                self._fastapi_main(project_name, security),
                "file", "python"
            )
            
            # Generate models from data model
            if data_model.get("entities"):
                self._add_artifact(
                    f"{project_name}/backend/app/models.py",
                    self._fastapi_models(data_model, database_id),
                    "file", "python"
                )
            
            # Generate API routes from contracts
            if api_contracts:
                self._add_artifact(
                    f"{project_name}/backend/app/routes.py",
                    self._fastapi_routes(api_contracts),
                    "file", "python"
                )
                
        elif framework_id == "nestjs":
            self._add_artifact(
                f"{project_name}/backend/package.json",
                self._nestjs_package_json(project_name),
                "file", "json"
            )
    
    def _generate_database(self, project_name: str, database_id: str, 
                          data_model: Dict):
        """Generate database schemas and migrations"""
        
        entities = data_model.get("entities", [])
        
        if database_id == "postgresql":
            self._add_artifact(
                f"{project_name}/database/schema.sql",
                self._postgresql_schema(entities),
                "file", "sql"
            )
            
        elif database_id == "supabase":
            self._add_artifact(
                f"{project_name}/database/supabase_schema.sql",
                self._supabase_schema(entities),
                "file", "sql"
            )
            
        elif database_id == "mongodb":
            self._add_artifact(
                f"{project_name}/database/collections.js",
                self._mongodb_collections(entities),
                "file", "javascript"
            )
    
    def _generate_docker(self, project_name: str, tech_stack: Dict):
        """Generate Docker configuration"""
        
        # Dockerfile for backend
        backend_id = tech_stack.get("backend_framework", "fastapi")
        self._add_artifact(
            f"{project_name}/backend/Dockerfile",
            self._dockerfile_backend(backend_id),
            "file", "dockerfile"
        )
        
        # Dockerfile for frontend
        frontend_id = tech_stack.get("frontend_framework", "nextjs")
        self._add_artifact(
            f"{project_name}/frontend/Dockerfile",
            self._dockerfile_frontend(frontend_id),
            "file", "dockerfile"
        )
        
        # Docker Compose
        self._add_artifact(
            f"{project_name}/docker-compose.yml",
            self._docker_compose(project_name, tech_stack),
            "file", "yaml"
        )
    
    def _generate_cicd(self, project_name: str, ci_id: str, tech_stack: Dict):
        """Generate CI/CD configuration"""
        
        if ci_id == "github_actions":
            self._add_artifact(
                f"{project_name}/.github/workflows/ci.yml",
                self._github_actions_ci(project_name, tech_stack),
                "file", "yaml"
            )
            
            self._add_artifact(
                f"{project_name}/.github/workflows/deploy.yml",
                self._github_actions_deploy(project_name, tech_stack),
                "file", "yaml"
            )
    
    def _generate_deployment_config(self, tech_stack: Dict) -> Dict[str, Any]:
        """Generate deployment configuration based on selected platforms"""
        config = {}
        
        cloud = tech_stack.get("cloud_provider")
        serverless = tech_stack.get("serverless")
        container = tech_stack.get("container_orchestration")
        
        if serverless == "vercel":
            config["vercel"] = {
                "framework": tech_stack.get("frontend_framework", "nextjs"),
                "buildCommand": "npm run build",
                "outputDirectory": ".next"
            }
            
        if serverless == "railway":
            config["railway"] = {
                "services": ["backend", "frontend"],
                "databases": [tech_stack.get("database", "postgresql")]
            }
            
        if serverless == "render":
            config["render"] = {
                "services": [
                    {"type": "web", "name": "backend"},
                    {"type": "static", "name": "frontend"}
                ]
            }
            
        if container == "kubernetes":
            config["kubernetes"] = {
                "namespace": "production",
                "replicas": 3,
                "resources": {
                    "requests": {"cpu": "100m", "memory": "128Mi"},
                    "limits": {"cpu": "500m", "memory": "512Mi"}
                }
            }
        
        return config
    
    def _generate_env_template(self, tech_stack: Dict) -> Dict[str, str]:
        """Generate environment variables template"""
        env_vars = {
            "NODE_ENV": "production",
            "API_URL": "https://api.example.com"
        }
        
        db_id = tech_stack.get("database")
        if db_id == "postgresql":
            env_vars["DATABASE_URL"] = "postgresql://user:password@host:5432/dbname"
        elif db_id == "supabase":
            env_vars["SUPABASE_URL"] = "https://xxx.supabase.co"
            env_vars["SUPABASE_ANON_KEY"] = "your-anon-key"
        elif db_id == "mongodb":
            env_vars["MONGODB_URI"] = "mongodb+srv://user:password@cluster.mongodb.net/dbname"
        
        cache_id = tech_stack.get("cache")
        if cache_id == "redis":
            env_vars["REDIS_URL"] = "redis://localhost:6379"
        elif cache_id == "upstash":
            env_vars["UPSTASH_REDIS_URL"] = "https://xxx.upstash.io"
            env_vars["UPSTASH_REDIS_TOKEN"] = "your-token"
        
        auth_id = tech_stack.get("authentication")
        if auth_id == "clerk":
            env_vars["CLERK_PUBLISHABLE_KEY"] = "pk_xxx"
            env_vars["CLERK_SECRET_KEY"] = "sk_xxx"
        elif auth_id == "auth0":
            env_vars["AUTH0_DOMAIN"] = "xxx.auth0.com"
            env_vars["AUTH0_CLIENT_ID"] = "your-client-id"
            env_vars["AUTH0_CLIENT_SECRET"] = "your-client-secret"
        
        return env_vars
    
    # ════════════════════════════════════════════════════════════════════════
    #                         CODE TEMPLATES
    # ════════════════════════════════════════════════════════════════════════
    
    def _nextjs_package_json(self, name: str, css_id: str) -> str:
        deps = {
            "next": "14.1.0",
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "typescript": "^5.3.0"
        }
        
        if css_id == "tailwindcss":
            deps["tailwindcss"] = "^3.4.0"
            deps["autoprefixer"] = "^10.4.0"
            deps["postcss"] = "^8.4.0"
        
        return json.dumps({
            "name": name,
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": deps
        }, indent=2)
    
    def _nextjs_layout(self, name: str) -> str:
        return f'''import type {{ Metadata }} from "next";
import "./globals.css";

export const metadata: Metadata = {{
  title: "{name}",
  description: "Generated by Sovereign Genesis Platform",
}};

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode;
}}) {{
  return (
    <html lang="en">
      <body>{{children}}</body>
    </html>
  );
}}
'''
    
    def _nextjs_home_page(self, spec: Dict) -> str:
        title = spec.get("name", "Welcome")
        return f'''export default function Home() {{
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold">{title}</h1>
      <p className="mt-4 text-gray-600">
        Generated by Sovereign Genesis Platform
      </p>
    </main>
  );
}}
'''
    
    def _react_package_json(self, name: str, css_id: str) -> str:
        return json.dumps({
            "name": name,
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test"
            },
            "dependencies": {
                "react": "^19.0.0",
                "react-dom": "^19.0.0",
                "react-scripts": "5.0.1"
            }
        }, indent=2)
    
    def _react_app(self, spec: Dict) -> str:
        return '''import React from "react";

function App() {
  return (
    <div className="App">
      <h1>Welcome</h1>
    </div>
  );
}

export default App;
'''
    
    def _tailwind_config(self) -> str:
        return '''import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

export default config;
'''
    
    def _fastapi_requirements(self, database_id: str) -> str:
        reqs = [
            "fastapi>=0.109.0",
            "uvicorn[standard]>=0.27.0",
            "pydantic>=2.5.0",
            "python-dotenv>=1.0.0"
        ]
        
        if database_id == "postgresql":
            reqs.extend(["asyncpg>=0.29.0", "sqlalchemy>=2.0.0"])
        elif database_id == "mongodb":
            reqs.append("motor>=3.3.0")
        elif database_id == "supabase":
            reqs.append("supabase>=2.0.0")
        
        return "\n".join(reqs)
    
    def _fastapi_main(self, name: str, security: Dict) -> str:
        return f'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="{name} API",
    description="Generated by Sovereign Genesis Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {{"message": "{name} API is running"}}

@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}
'''
    
    def _fastapi_models(self, data_model: Dict, database_id: str) -> str:
        entities = data_model.get("entities", [])
        code = "from pydantic import BaseModel\nfrom typing import Optional, List\nfrom datetime import datetime\n\n"
        
        for entity in entities:
            name = entity.get("name", "Entity")
            attrs = entity.get("attributes", [])
            
            code += f"class {name}(BaseModel):\n"
            for attr in attrs:
                attr_name = attr.get("name", "field")
                attr_type = attr.get("type", "str")
                
                # Map types
                type_map = {
                    "string": "str",
                    "integer": "int",
                    "boolean": "bool",
                    "datetime": "datetime",
                    "float": "float"
                }
                py_type = type_map.get(attr_type, "str")
                
                code += f"    {attr_name}: {py_type}\n"
            code += "\n"
        
        return code
    
    def _fastapi_routes(self, api_contracts: List) -> str:
        code = "from fastapi import APIRouter, HTTPException\nfrom typing import List\n\nrouter = APIRouter()\n\n"
        
        seen_names = set()
        for contract in api_contracts:
            endpoint = contract.get("endpoint", "/")
            method = contract.get("method", "GET").lower()
            
            # Create unique function name from endpoint + method
            base_name = endpoint.replace("/", "_").strip("_") or "root"
            func_name = f"{method}_{base_name}"
            
            # Handle duplicates by adding counter
            if func_name in seen_names:
                counter = 2
                while f"{func_name}_{counter}" in seen_names:
                    counter += 1
                func_name = f"{func_name}_{counter}"
            seen_names.add(func_name)
            
            code += f'''@router.{method}("{endpoint}")
async def {func_name}():
    return {{"message": "{method.upper()} {endpoint} endpoint"}}

'''
        
        return code
    
    def _postgresql_schema(self, entities: List) -> str:
        sql = "-- Generated by Sovereign Genesis Platform\n\n"
        
        for entity in entities:
            name = entity.get("name", "entity").lower()
            attrs = entity.get("attributes", [])
            
            sql += f"CREATE TABLE {name} (\n"
            sql += "    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n"
            
            for attr in attrs:
                attr_name = attr.get("name", "field")
                attr_type = attr.get("type", "string")
                
                type_map = {
                    "string": "VARCHAR(255)",
                    "text": "TEXT",
                    "integer": "INTEGER",
                    "boolean": "BOOLEAN",
                    "datetime": "TIMESTAMP WITH TIME ZONE",
                    "float": "DECIMAL(10,2)"
                }
                sql_type = type_map.get(attr_type, "VARCHAR(255)")
                
                sql += f"    {attr_name} {sql_type},\n"
            
            sql += "    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),\n"
            sql += "    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()\n"
            sql += ");\n\n"
        
        return sql
    
    def _supabase_schema(self, entities: List) -> str:
        sql = self._postgresql_schema(entities)
        sql += "\n-- Enable Row Level Security\n"
        for entity in entities:
            name = entity.get("name", "entity").lower()
            sql += f"ALTER TABLE {name} ENABLE ROW LEVEL SECURITY;\n"
        return sql
    
    def _mongodb_collections(self, entities: List) -> str:
        code = "// Generated by Sovereign Genesis Platform\n\n"
        
        for entity in entities:
            name = entity.get("name", "entity").lower()
            code += f"db.createCollection('{name}');\n"
            
            # Create indexes
            code += f"db.{name}.createIndex({{ createdAt: 1 }});\n\n"
        
        return code
    
    def _dockerfile_backend(self, framework_id: str) -> str:
        if framework_id == "fastapi":
            return '''FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        elif framework_id == "nestjs":
            return '''FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start:prod"]
'''
        return ""
    
    def _dockerfile_frontend(self, framework_id: str) -> str:
        if framework_id in ["nextjs", "react"]:
            return '''FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000

CMD ["npm", "start"]
'''
        return ""
    
    def _docker_compose(self, name: str, tech_stack: Dict) -> str:
        services = {
            "backend": {
                "build": "./backend",
                "ports": ["8000:8000"],
                "environment": ["DATABASE_URL=${DATABASE_URL}"],
                "depends_on": []
            },
            "frontend": {
                "build": "./frontend",
                "ports": ["3000:3000"],
                "environment": ["API_URL=http://backend:8000"],
                "depends_on": ["backend"]
            }
        }
        
        db_id = tech_stack.get("database")
        if db_id == "postgresql":
            services["database"] = {
                "image": "postgres:16-alpine",
                "environment": [
                    "POSTGRES_USER=postgres",
                    "POSTGRES_PASSWORD=postgres",
                    "POSTGRES_DB=app"
                ],
                "volumes": ["pgdata:/var/lib/postgresql/data"]
            }
            services["backend"]["depends_on"].append("database")
        
        cache_id = tech_stack.get("cache")
        if cache_id == "redis":
            services["redis"] = {
                "image": "redis:7-alpine",
                "ports": ["6379:6379"]
            }
        
        # Convert to YAML-like string
        yaml = f"# {name} - Generated by SGP\nversion: '3.8'\n\nservices:\n"
        
        for svc_name, svc_config in services.items():
            yaml += f"  {svc_name}:\n"
            for key, value in svc_config.items():
                if isinstance(value, list):
                    yaml += f"    {key}:\n"
                    for item in value:
                        yaml += f"      - {item}\n"
                else:
                    yaml += f"    {key}: {value}\n"
        
        if db_id == "postgresql":
            yaml += "\nvolumes:\n  pgdata:\n"
        
        return yaml
    
    def _github_actions_ci(self, name: str, tech_stack: Dict) -> str:
        return '''name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          
      - name: Install dependencies
        run: npm ci
        working-directory: ./frontend
        
      - name: Run tests
        run: npm test
        working-directory: ./frontend
        
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          
      - name: Install Python dependencies
        run: pip install -r requirements.txt
        working-directory: ./backend
        
      - name: Run Python tests
        run: pytest
        working-directory: ./backend
'''
    
    def _github_actions_deploy(self, name: str, tech_stack: Dict) -> str:
        serverless = tech_stack.get("serverless", "vercel")
        
        deploy_step = ""
        if serverless == "vercel":
            deploy_step = '''      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
'''
        elif serverless == "railway":
            deploy_step = '''      - name: Deploy to Railway
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
'''
        elif serverless == "render":
            deploy_step = '''      - name: Deploy to Render
        run: curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
'''
        
        return f'''name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
{deploy_step}
'''
    
    def _nestjs_package_json(self, name: str) -> str:
        return json.dumps({
            "name": name,
            "version": "0.1.0",
            "scripts": {
                "build": "nest build",
                "start": "nest start",
                "start:dev": "nest start --watch",
                "start:prod": "node dist/main"
            },
            "dependencies": {
                "@nestjs/common": "^10.0.0",
                "@nestjs/core": "^10.0.0",
                "@nestjs/platform-express": "^10.0.0"
            }
        }, indent=2)
    
    def get_artifacts_summary(self) -> Dict[str, Any]:
        """Get summary of generated artifacts"""
        if not self.manifest:
            return {"error": "No build manifest generated"}
        
        by_language = {}
        for artifact in self.artifacts:
            lang = artifact.language
            if lang not in by_language:
                by_language[lang] = []
            by_language[lang].append(artifact.path)
        
        return {
            "build_id": self.manifest.id,
            "project_name": self.manifest.project_name,
            "total_artifacts": len(self.artifacts),
            "artifacts_by_language": by_language,
            "tech_stack": self.manifest.tech_stack,
            "deployment_config": self.manifest.deployment_config,
            "environment_variables": list(self.manifest.environment_variables.keys())
        }
    
    def write_to_disk(self, output_dir: str) -> Dict[str, Any]:
        """
        Write all generated artifacts to disk as actual files.
        
        Args:
            output_dir: Base directory to write files to (e.g., '/app/generated')
            
        Returns:
            Summary of written files and any errors
        """
        if not self.manifest:
            return {"success": False, "error": "No build manifest generated. Run generate_project() first."}
        
        written_files = []
        errors = []
        
        base_path = Path(output_dir)
        
        for artifact in self.artifacts:
            try:
                # Create full path
                file_path = base_path / artifact.path
                
                # Create parent directories
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write the file
                file_path.write_text(artifact.content, encoding='utf-8')
                
                written_files.append({
                    "path": str(file_path),
                    "relative_path": artifact.path,
                    "language": artifact.language,
                    "size_bytes": len(artifact.content)
                })
                
            except Exception as e:
                errors.append({
                    "path": artifact.path,
                    "error": str(e)
                })
        
        # Write manifest file
        try:
            manifest_path = base_path / self.manifest.project_name / "sgp-manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_data = {
                "id": self.manifest.id,
                "project_name": self.manifest.project_name,
                "tech_stack": self.manifest.tech_stack,
                "deployment_config": self.manifest.deployment_config,
                "environment_variables": self.manifest.environment_variables,
                "created_at": self.manifest.created_at,
                "total_files": len(self.artifacts),
                "files": [{"path": a.path, "language": a.language} for a in self.artifacts]
            }
            manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding='utf-8')
            written_files.append({
                "path": str(manifest_path),
                "relative_path": f"{self.manifest.project_name}/sgp-manifest.json",
                "language": "json",
                "size_bytes": len(json.dumps(manifest_data, indent=2))
            })
        except Exception as e:
            errors.append({"path": "sgp-manifest.json", "error": str(e)})
        
        return {
            "success": len(errors) == 0,
            "output_directory": str(base_path / self.manifest.project_name),
            "total_files_written": len(written_files),
            "files": written_files,
            "errors": errors,
            "project_name": self.manifest.project_name,
            "tech_stack": self.manifest.tech_stack
        }
    
    def get_file_tree(self) -> List[Dict[str, Any]]:
        """Get the file tree structure of generated artifacts"""
        if not self.manifest:
            return []
        
        tree = {}
        for artifact in self.artifacts:
            parts = artifact.path.split('/')
            current = tree
            
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    # File
                    current[part] = {
                        "type": "file",
                        "language": artifact.language,
                        "size": len(artifact.content)
                    }
                else:
                    # Directory
                    if part not in current:
                        current[part] = {"type": "directory", "children": {}}
                    current = current[part].get("children", current[part])
        
        return tree
    
    # ════════════════════════════════════════════════════════════════════════
    #                    ENHANCED CODE GENERATION
    # ════════════════════════════════════════════════════════════════════════
    
    def generate_crud_routes(self, entity_name: str, attributes: List[Dict]) -> str:
        """Generate complete CRUD routes for an entity"""
        name_lower = entity_name.lower()
        name_plural = f"{name_lower}s"
        
        # Build attribute list for create/update
        create_attrs = ", ".join([f'{a["name"]}: {self._py_type(a["type"])}' for a in attributes])
        
        return f'''from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/{name_plural}", tags=["{entity_name}"])

# ═══════════════════════════════════════════════════════════════════════════
#                              DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════

class {entity_name}Create(BaseModel):
    {self._model_fields(attributes, optional=False)}

class {entity_name}Update(BaseModel):
    {self._model_fields(attributes, optional=True)}

class {entity_name}Response(BaseModel):
    id: str
    {self._model_fields(attributes, optional=False)}
    created_at: datetime
    updated_at: datetime

# ═══════════════════════════════════════════════════════════════════════════
#                           IN-MEMORY STORAGE
# ═══════════════════════════════════════════════════════════════════════════

# Replace with actual database in production
{name_plural}_db: dict = {{}}

# ═══════════════════════════════════════════════════════════════════════════
#                              CRUD ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/", response_model={entity_name}Response, status_code=201)
async def create_{name_lower}(data: {entity_name}Create):
    """Create a new {name_lower}"""
    item_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    item = {{
        "id": item_id,
        **data.model_dump(),
        "created_at": now,
        "updated_at": now
    }}
    
    {name_plural}_db[item_id] = item
    return item

@router.get("/", response_model=List[{entity_name}Response])
async def list_{name_plural}(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """List all {name_plural} with pagination"""
    items = list({name_plural}_db.values())
    return items[skip:skip + limit]

@router.get("/{{item_id}}", response_model={entity_name}Response)
async def get_{name_lower}(item_id: str):
    """Get a specific {name_lower} by ID"""
    if item_id not in {name_plural}_db:
        raise HTTPException(status_code=404, detail="{entity_name} not found")
    return {name_plural}_db[item_id]

@router.put("/{{item_id}}", response_model={entity_name}Response)
async def update_{name_lower}(item_id: str, data: {entity_name}Update):
    """Update a {name_lower}"""
    if item_id not in {name_plural}_db:
        raise HTTPException(status_code=404, detail="{entity_name} not found")
    
    item = {name_plural}_db[item_id]
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        item[field] = value
    
    item["updated_at"] = datetime.utcnow()
    return item

@router.delete("/{{item_id}}", status_code=204)
async def delete_{name_lower}(item_id: str):
    """Delete a {name_lower}"""
    if item_id not in {name_plural}_db:
        raise HTTPException(status_code=404, detail="{entity_name} not found")
    
    del {name_plural}_db[item_id]
    return None

@router.get("/search/", response_model=List[{entity_name}Response])
async def search_{name_plural}(q: str = Query(..., min_length=1)):
    """Search {name_plural} by query string"""
    results = []
    q_lower = q.lower()
    
    for item in {name_plural}_db.values():
        # Search in string fields
        for key, value in item.items():
            if isinstance(value, str) and q_lower in value.lower():
                results.append(item)
                break
    
    return results
'''
    
    def generate_auth_module(self, project_name: str) -> Dict[str, str]:
        """Generate complete authentication module"""
        
        auth_models = '''from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
'''
        
        auth_utils = '''import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
import jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        salt, hash_value = hashed.split("$")
        return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
    except:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
'''
        
        auth_routes = '''from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
import uuid
from datetime import datetime

from .auth_models import UserCreate, UserLogin, UserResponse, Token
from .auth_utils import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory user storage (replace with database)
users_db: dict = {}

async def get_current_user(authorization: Optional[str] = Header(None)) -> UserResponse:
    """Dependency to get current authenticated user"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid auth header")
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("user_id")
    if user_id not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserResponse(**users_db[user_id])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate):
    """Register a new user"""
    # Check if email exists
    for user in users_db.values():
        if user["email"] == data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    user = {
        "id": user_id,
        "email": data.email,
        "name": data.name,
        "password_hash": hash_password(data.password),
        "is_active": True,
        "created_at": now
    }
    
    users_db[user_id] = user
    return UserResponse(**user)

@router.post("/login", response_model=Token)
async def login(data: UserLogin):
    """Login and get access token"""
    # Find user by email
    user = None
    for u in users_db.values():
        if u["email"] == data.email:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user["is_active"]:
        raise HTTPException(status_code=401, detail="Account disabled")
    
    access_token = create_access_token({
        "user_id": user["id"],
        "email": user["email"]
    })
    
    return Token(access_token=access_token, expires_in=86400)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """Logout (client should discard token)"""
    return {"message": "Successfully logged out"}
'''
        
        return {
            "auth_models.py": auth_models,
            "auth_utils.py": auth_utils,
            "auth_routes.py": auth_routes
        }
    
    def generate_test_suite(self, entity_name: str, attributes: List[Dict]) -> str:
        """Generate pytest test suite for an entity"""
        name_lower = entity_name.lower()
        name_plural = f"{name_lower}s"
        
        # Build sample data
        sample_data = {}
        for attr in attributes:
            if attr["type"] == "string":
                sample_data[attr["name"]] = f"test_{attr['name']}"
            elif attr["type"] == "integer":
                sample_data[attr["name"]] = 1
            elif attr["type"] == "boolean":
                sample_data[attr["name"]] = True
            elif attr["type"] == "float":
                sample_data[attr["name"]] = 1.5
        
        sample_json = json.dumps(sample_data, indent=8)
        
        return f'''import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ═══════════════════════════════════════════════════════════════════════════
#                         {entity_name.upper()} CRUD TESTS
# ═══════════════════════════════════════════════════════════════════════════

class Test{entity_name}CRUD:
    """Test suite for {entity_name} CRUD operations"""
    
    created_id = None
    
    @pytest.fixture(autouse=True)
    def sample_data(self):
        return {sample_json}
    
    def test_create_{name_lower}(self, sample_data):
        """Test creating a new {name_lower}"""
        response = client.post("/{name_plural}/", json=sample_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "id" in data
        assert data["created_at"] is not None
        
        Test{entity_name}CRUD.created_id = data["id"]
    
    def test_get_{name_lower}(self):
        """Test getting a {name_lower} by ID"""
        if not Test{entity_name}CRUD.created_id:
            pytest.skip("No {name_lower} created")
        
        response = client.get(f"/{name_plural}/{{Test{entity_name}CRUD.created_id}}")
        assert response.status_code == 200
        assert response.json()["id"] == Test{entity_name}CRUD.created_id
    
    def test_list_{name_plural}(self):
        """Test listing all {name_plural}"""
        response = client.get("/{name_plural}/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_update_{name_lower}(self, sample_data):
        """Test updating a {name_lower}"""
        if not Test{entity_name}CRUD.created_id:
            pytest.skip("No {name_lower} created")
        
        # Modify sample data
        updated_data = {{k: f"updated_{{v}}" if isinstance(v, str) else v for k, v in sample_data.items()}}
        
        response = client.put(
            f"/{name_plural}/{{Test{entity_name}CRUD.created_id}}",
            json=updated_data
        )
        assert response.status_code == 200
    
    def test_delete_{name_lower}(self):
        """Test deleting a {name_lower}"""
        if not Test{entity_name}CRUD.created_id:
            pytest.skip("No {name_lower} created")
        
        response = client.delete(f"/{name_plural}/{{Test{entity_name}CRUD.created_id}}")
        assert response.status_code == 204
        
        # Verify deletion
        response = client.get(f"/{name_plural}/{{Test{entity_name}CRUD.created_id}}")
        assert response.status_code == 404
    
    def test_get_nonexistent_{name_lower}(self):
        """Test getting a non-existent {name_lower}"""
        response = client.get("/{name_plural}/nonexistent-id")
        assert response.status_code == 404
    
    def test_search_{name_plural}(self, sample_data):
        """Test searching {name_plural}"""
        # Create a {name_lower} first
        client.post("/{name_plural}/", json=sample_data)
        
        response = client.get("/{name_plural}/search/?q=test")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""
    
    test_user = {{
        "email": "test@example.com",
        "password": "TestPass123!",
        "name": "Test User"
    }}
    access_token = None
    
    def test_register(self):
        """Test user registration"""
        response = client.post("/auth/register", json=self.test_user)
        # May fail if user already exists
        assert response.status_code in [201, 400]
    
    def test_login(self):
        """Test user login"""
        response = client.post("/auth/login", json={{
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        }})
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            TestAuthEndpoints.access_token = data["access_token"]
    
    def test_get_me(self):
        """Test getting current user"""
        if not TestAuthEndpoints.access_token:
            pytest.skip("No access token")
        
        response = client.get(
            "/auth/me",
            headers={{"Authorization": f"Bearer {{TestAuthEndpoints.access_token}}"}}
        )
        assert response.status_code == 200
    
    def test_unauthorized(self):
        """Test unauthorized access"""
        response = client.get("/auth/me")
        assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
#                            HEALTH CHECKS
# ═══════════════════════════════════════════════════════════════════════════

def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
'''
    
    def _py_type(self, type_str: str) -> str:
        """Convert type string to Python type"""
        type_map = {
            "string": "str",
            "integer": "int",
            "boolean": "bool",
            "datetime": "datetime",
            "float": "float"
        }
        return type_map.get(type_str, "str")
    
    def _model_fields(self, attributes: List[Dict], optional: bool = False) -> str:
        """Generate Pydantic model fields"""
        lines = []
        for attr in attributes:
            py_type = self._py_type(attr.get("type", "string"))
            if optional:
                lines.append(f'{attr["name"]}: Optional[{py_type}] = None')
            else:
                lines.append(f'{attr["name"]}: {py_type}')
        return "\n    ".join(lines) if lines else "pass"
