"""
FILE STRUCTURE GENERATOR API
Generates industry-standard file trees based on tech stack and workflow
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/file-structure", tags=["file-structure"])


class WorkflowTask(BaseModel):
    id: str
    name: str
    category: str
    priority: str


class GenerateStructureRequest(BaseModel):
    session_id: str
    tech_stack: str
    project_name: Optional[str] = "project"
    tasks: Optional[List[WorkflowTask]] = []


class FileNode(BaseModel):
    name: str
    path: str
    type: str  # file or folder
    content: Optional[str] = None
    children: Optional[List['FileNode']] = []


class StructureResult(BaseModel):
    session_id: str
    tech_stack: str
    project_name: str
    total_files: int
    total_folders: int
    tree: List[FileNode]
    created_at: str


# Store generated structures
structure_store = {}


# Industry-standard templates per language
TEMPLATES = {
    "python": {
        "folders": [
            {"name": "src", "desc": "Source code"},
            {"name": "src/api", "desc": "API routes"},
            {"name": "src/models", "desc": "Data models"},
            {"name": "src/services", "desc": "Business logic"},
            {"name": "src/utils", "desc": "Utility functions"},
            {"name": "tests", "desc": "Test files"},
            {"name": "tests/unit", "desc": "Unit tests"},
            {"name": "tests/integration", "desc": "Integration tests"},
            {"name": "config", "desc": "Configuration"},
            {"name": "docs", "desc": "Documentation"},
        ],
        "files": [
            {"name": "main.py", "path": "src/main.py", "content": '"""Main application entry point"""\n\nfrom fastapi import FastAPI\n\napp = FastAPI(title="{project_name}")\n\n@app.get("/")\ndef root():\n    return {{"status": "running", "project": "{project_name}"}}\n'},
            {"name": "__init__.py", "path": "src/__init__.py", "content": '"""Source package"""'},
            {"name": "__init__.py", "path": "src/api/__init__.py", "content": '"""API package"""'},
            {"name": "__init__.py", "path": "src/models/__init__.py", "content": '"""Models package"""'},
            {"name": "__init__.py", "path": "src/services/__init__.py", "content": '"""Services package"""'},
            {"name": "__init__.py", "path": "src/utils/__init__.py", "content": '"""Utils package"""'},
            {"name": "requirements.txt", "path": "requirements.txt", "content": "fastapi>=0.100.0\nuvicorn>=0.23.0\npydantic>=2.0.0\npython-dotenv>=1.0.0\npytest>=7.0.0\n"},
            {"name": ".env.example", "path": ".env.example", "content": "# Environment variables\nDATABASE_URL=\nAPI_KEY=\nDEBUG=false\n"},
            {"name": "README.md", "path": "README.md", "content": "# {project_name}\n\n## Setup\n```bash\npip install -r requirements.txt\n```\n\n## Run\n```bash\nuvicorn src.main:app --reload\n```\n"},
            {"name": "pytest.ini", "path": "pytest.ini", "content": "[pytest]\ntestpaths = tests\npython_files = test_*.py\n"},
            {"name": "test_main.py", "path": "tests/unit/test_main.py", "content": '"""Unit tests for main module"""\n\ndef test_placeholder():\n    assert True\n'},
        ]
    },
    "javascript": {
        "folders": [
            {"name": "src", "desc": "Source code"},
            {"name": "src/routes", "desc": "Express routes"},
            {"name": "src/controllers", "desc": "Route controllers"},
            {"name": "src/models", "desc": "Data models"},
            {"name": "src/middleware", "desc": "Express middleware"},
            {"name": "src/utils", "desc": "Utility functions"},
            {"name": "tests", "desc": "Test files"},
            {"name": "config", "desc": "Configuration"},
            {"name": "public", "desc": "Static assets"},
        ],
        "files": [
            {"name": "index.js", "path": "src/index.js", "content": 'const express = require("express");\nconst app = express();\nconst PORT = process.env.PORT || 3000;\n\napp.use(express.json());\n\napp.get("/", (req, res) => {\n  res.json({ status: "running", project: "{project_name}" });\n});\n\napp.listen(PORT, () => {\n  console.log(`Server running on port ${PORT}`);\n});\n'},
            {"name": "package.json", "path": "package.json", "content": '{{\n  "name": "{project_name}",\n  "version": "1.0.0",\n  "main": "src/index.js",\n  "scripts": {{\n    "start": "node src/index.js",\n    "dev": "nodemon src/index.js",\n    "test": "jest"\n  }},\n  "dependencies": {{\n    "express": "^4.18.0",\n    "dotenv": "^16.0.0"\n  }},\n  "devDependencies": {{\n    "jest": "^29.0.0",\n    "nodemon": "^3.0.0"\n  }}\n}}'},
            {"name": ".env.example", "path": ".env.example", "content": "PORT=3000\nDATABASE_URL=\nAPI_KEY=\n"},
            {"name": "README.md", "path": "README.md", "content": "# {project_name}\n\n## Setup\n```bash\nnpm install\n```\n\n## Run\n```bash\nnpm run dev\n```\n"},
            {"name": ".gitignore", "path": ".gitignore", "content": "node_modules/\n.env\n*.log\ndist/\n"},
        ]
    },
    "typescript": {
        "folders": [
            {"name": "src", "desc": "Source code"},
            {"name": "src/routes", "desc": "API routes"},
            {"name": "src/controllers", "desc": "Route controllers"},
            {"name": "src/models", "desc": "Data models"},
            {"name": "src/types", "desc": "TypeScript types"},
            {"name": "src/middleware", "desc": "Middleware"},
            {"name": "src/utils", "desc": "Utility functions"},
            {"name": "tests", "desc": "Test files"},
            {"name": "config", "desc": "Configuration"},
        ],
        "files": [
            {"name": "index.ts", "path": "src/index.ts", "content": 'import express, {{ Application }} from "express";\nimport dotenv from "dotenv";\n\ndotenv.config();\n\nconst app: Application = express();\nconst PORT = process.env.PORT || 3000;\n\napp.use(express.json());\n\napp.get("/", (req, res) => {{\n  res.json({{ status: "running", project: "{project_name}" }});\n}});\n\napp.listen(PORT, () => {{\n  console.log(`Server running on port ${{PORT}}`);\n}});\n'},
            {"name": "package.json", "path": "package.json", "content": '{{\n  "name": "{project_name}",\n  "version": "1.0.0",\n  "main": "dist/index.js",\n  "scripts": {{\n    "build": "tsc",\n    "start": "node dist/index.js",\n    "dev": "ts-node-dev src/index.ts",\n    "test": "jest"\n  }},\n  "dependencies": {{\n    "express": "^4.18.0",\n    "dotenv": "^16.0.0"\n  }},\n  "devDependencies": {{\n    "@types/express": "^4.17.0",\n    "@types/node": "^20.0.0",\n    "typescript": "^5.0.0",\n    "ts-node-dev": "^2.0.0",\n    "jest": "^29.0.0",\n    "@types/jest": "^29.0.0"\n  }}\n}}'},
            {"name": "tsconfig.json", "path": "tsconfig.json", "content": '{{\n  "compilerOptions": {{\n    "target": "ES2020",\n    "module": "commonjs",\n    "outDir": "./dist",\n    "rootDir": "./src",\n    "strict": true,\n    "esModuleInterop": true,\n    "skipLibCheck": true\n  }},\n  "include": ["src/**/*"],\n  "exclude": ["node_modules", "dist"]\n}}'},
            {"name": ".env.example", "path": ".env.example", "content": "PORT=3000\nDATABASE_URL=\nAPI_KEY=\n"},
            {"name": "README.md", "path": "README.md", "content": "# {project_name}\n\n## Setup\n```bash\nnpm install\n```\n\n## Run\n```bash\nnpm run dev\n```\n"},
        ]
    },
    "go": {
        "folders": [
            {"name": "cmd", "desc": "Application entry points"},
            {"name": "cmd/server", "desc": "Server command"},
            {"name": "internal", "desc": "Private application code"},
            {"name": "internal/handlers", "desc": "HTTP handlers"},
            {"name": "internal/models", "desc": "Data models"},
            {"name": "internal/services", "desc": "Business logic"},
            {"name": "pkg", "desc": "Public libraries"},
            {"name": "tests", "desc": "Test files"},
            {"name": "config", "desc": "Configuration"},
        ],
        "files": [
            {"name": "main.go", "path": "cmd/server/main.go", "content": 'package main\n\nimport (\n\t"fmt"\n\t"log"\n\t"net/http"\n)\n\nfunc main() {\n\thttp.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {\n\t\tfmt.Fprintf(w, `{"status":"running","project":"{project_name}"}`)\n\t})\n\n\tlog.Println("Server starting on :8080")\n\tlog.Fatal(http.ListenAndServe(":8080", nil))\n}\n'},
            {"name": "go.mod", "path": "go.mod", "content": "module {project_name}\n\ngo 1.21\n"},
            {"name": "README.md", "path": "README.md", "content": "# {project_name}\n\n## Setup\n```bash\ngo mod tidy\n```\n\n## Run\n```bash\ngo run cmd/server/main.go\n```\n"},
            {"name": "Makefile", "path": "Makefile", "content": ".PHONY: build run test\n\nbuild:\n\tgo build -o bin/server cmd/server/main.go\n\nrun:\n\tgo run cmd/server/main.go\n\ntest:\n\tgo test ./...\n"},
        ]
    },
    "rust": {
        "folders": [
            {"name": "src", "desc": "Source code"},
            {"name": "src/handlers", "desc": "Request handlers"},
            {"name": "src/models", "desc": "Data models"},
            {"name": "src/services", "desc": "Business logic"},
            {"name": "tests", "desc": "Integration tests"},
        ],
        "files": [
            {"name": "main.rs", "path": "src/main.rs", "content": 'use actix_web::{{web, App, HttpResponse, HttpServer}};\n\nasync fn index() -> HttpResponse {{\n    HttpResponse::Ok().json(serde_json::json!({{\n        "status": "running",\n        "project": "{project_name}"\n    }}))\n}}\n\n#[actix_web::main]\nasync fn main() -> std::io::Result<()> {{\n    HttpServer::new(|| {{\n        App::new().route("/", web::get().to(index))\n    }})\n    .bind("127.0.0.1:8080")?\n    .run()\n    .await\n}}\n'},
            {"name": "Cargo.toml", "path": "Cargo.toml", "content": '[package]\nname = "{project_name}"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\nactix-web = "4"\nserde = {{ version = "1", features = ["derive"] }}\nserde_json = "1"\ntokio = {{ version = "1", features = ["full"] }}\n'},
            {"name": "README.md", "path": "README.md", "content": "# {project_name}\n\n## Setup\n```bash\ncargo build\n```\n\n## Run\n```bash\ncargo run\n```\n"},
        ]
    }
}


def build_tree(folders: List[dict], files: List[dict], project_name: str) -> List[FileNode]:
    """Build a tree structure from folders and files"""
    tree = []
    folder_nodes = {}
    
    # Create folder nodes
    for folder in folders:
        parts = folder["name"].split("/")
        current_path = ""
        
        for i, part in enumerate(parts):
            parent_path = current_path
            current_path = f"{current_path}/{part}" if current_path else part
            
            if current_path not in folder_nodes:
                node = FileNode(
                    name=part,
                    path=current_path,
                    type="folder",
                    children=[]
                )
                folder_nodes[current_path] = node
                
                if parent_path and parent_path in folder_nodes:
                    folder_nodes[parent_path].children.append(node)
                elif not parent_path:
                    tree.append(node)
    
    # Add files
    for file in files:
        path = file["path"]
        content = file["content"].replace("{project_name}", project_name)
        
        file_node = FileNode(
            name=file["name"],
            path=path,
            type="file",
            content=content
        )
        
        # Find parent folder
        parts = path.split("/")
        if len(parts) > 1:
            parent_path = "/".join(parts[:-1])
            if parent_path in folder_nodes:
                folder_nodes[parent_path].children.append(file_node)
            else:
                tree.append(file_node)
        else:
            tree.append(file_node)
    
    return tree


def count_nodes(tree: List[FileNode]) -> tuple:
    """Count files and folders in tree"""
    files = 0
    folders = 0
    
    def traverse(nodes):
        nonlocal files, folders
        for node in nodes:
            if node.type == "file":
                files += 1
            else:
                folders += 1
                if node.children:
                    traverse(node.children)
    
    traverse(tree)
    return files, folders


@router.post("/generate", response_model=StructureResult)
async def generate_file_structure(request: GenerateStructureRequest):
    """
    Generate industry-standard file structure for the given tech stack.
    """
    tech_stack = request.tech_stack.lower()
    
    if tech_stack not in TEMPLATES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported tech stack: {tech_stack}. Supported: {list(TEMPLATES.keys())}"
        )
    
    template = TEMPLATES[tech_stack]
    project_name = request.project_name.lower().replace(" ", "_").replace("-", "_")
    
    # Build tree
    tree = build_tree(template["folders"], template["files"], project_name)
    
    # Count nodes
    total_files, total_folders = count_nodes(tree)
    
    result = StructureResult(
        session_id=request.session_id,
        tech_stack=tech_stack,
        project_name=project_name,
        total_files=total_files,
        total_folders=total_folders,
        tree=tree,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    # Store result
    structure_store[request.session_id] = result.dict()
    
    return result


@router.get("/result/{session_id}")
async def get_structure(session_id: str):
    """Get stored file structure for a session"""
    if session_id not in structure_store:
        raise HTTPException(status_code=404, detail="Structure not found")
    return structure_store[session_id]


@router.get("/templates")
async def list_templates():
    """List available tech stack templates"""
    return {
        "templates": list(TEMPLATES.keys()),
        "details": {
            k: {"folders": len(v["folders"]), "files": len(v["files"])}
            for k, v in TEMPLATES.items()
        }
    }
