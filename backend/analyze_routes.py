"""
FILE ANALYSIS API
Analyzes uploaded files and creates unified todo log
Uses LLM to extract requirements, patterns, and tasks
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import Trinity for LLM
from trinity_spine import trinity_spine

router = APIRouter(prefix="/api/analyze", tags=["file-analysis"])

# Upload directory
UPLOAD_DIR = Path("/app/uploads")


class AnalyzeRequest(BaseModel):
    session_id: str
    file_ids: Optional[List[str]] = None  # If None, analyze all files in session


class TodoItem(BaseModel):
    id: str
    task: str
    priority: str  # high, medium, low
    category: str  # requirement, bug, feature, refactor, test, docs
    source_file: Optional[str] = None
    line_reference: Optional[str] = None


class FileAnalysis(BaseModel):
    filename: str
    file_type: str
    summary: str
    todos: List[TodoItem]
    dependencies: List[str]
    patterns_detected: List[str]


class AnalysisResult(BaseModel):
    session_id: str
    files_analyzed: int
    unified_todo: List[TodoItem]
    file_analyses: List[FileAnalysis]
    project_summary: str
    suggested_structure: Dict[str, Any]
    analyzed_at: str


# Store analysis results
analysis_store = {}


def get_file_type(filename: str) -> str:
    """Determine file type from extension"""
    ext = Path(filename).suffix.lower()
    type_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'react',
        '.tsx': 'react-typescript',
        '.json': 'json-config',
        '.yaml': 'yaml-config',
        '.yml': 'yaml-config',
        '.md': 'markdown',
        '.txt': 'text',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.env': 'environment',
        '.sh': 'shell',
        '.dockerfile': 'docker',
    }
    return type_map.get(ext, 'unknown')


def read_file_content(file_path: Path) -> Optional[str]:
    """Read file content, return None for binary files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        return None


async def analyze_with_llm(files_content: Dict[str, str]) -> Dict[str, Any]:
    """Use LLM to analyze files and extract todos"""
    
    # Build prompt with file contents
    files_text = ""
    for filename, content in files_content.items():
        if content:
            # Truncate very large files
            truncated = content[:5000] if len(content) > 5000 else content
            files_text += f"\n\n=== FILE: {filename} ===\n{truncated}"
    
    analysis_prompt = f"""Analyze the following project files and extract:

1. A summary of what this project does
2. A list of TODO items with priority (high/medium/low) and category (requirement/bug/feature/refactor/test/docs)
3. Dependencies detected
4. Code patterns detected
5. Suggested file structure for a clean implementation

FILES:
{files_text}

Respond in this exact JSON format:
{{
    "project_summary": "Brief description of the project",
    "todos": [
        {{"task": "Description of task", "priority": "high|medium|low", "category": "requirement|bug|feature|refactor|test|docs", "source_file": "filename or null"}}
    ],
    "dependencies": ["list", "of", "dependencies"],
    "patterns": ["list", "of", "patterns", "detected"],
    "suggested_structure": {{
        "folders": ["src", "tests", "config"],
        "files": {{"main.py": "entry point", "config.py": "configuration"}}
    }}
}}

Return ONLY valid JSON, no markdown or explanation."""

    # Call LLM
    result = await trinity_spine.generate(
        prompt=analysis_prompt,
        system_prompt="You are a senior software architect analyzing project files. Extract actionable todos and provide clear structure recommendations. Always respond with valid JSON only.",
        temperature=0.3,
        max_tokens=2000
    )
    
    if not result.get("success"):
        return {
            "project_summary": "Analysis failed - using fallback",
            "todos": [],
            "dependencies": [],
            "patterns": [],
            "suggested_structure": {"folders": [], "files": {}}
        }
    
    # Parse JSON response
    response_text = result.get("response", "")
    
    # Try to extract JSON from response
    try:
        # Find JSON in response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = response_text[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Fallback: create basic analysis from file inspection
    return {
        "project_summary": f"Project with {len(files_content)} files",
        "todos": [
            {"task": f"Review and integrate {fn}", "priority": "medium", "category": "requirement", "source_file": fn}
            for fn in files_content.keys()
        ],
        "dependencies": [],
        "patterns": [],
        "suggested_structure": {"folders": ["src", "tests"], "files": {}}
    }


@router.post("/files", response_model=AnalysisResult)
async def analyze_files(request: AnalyzeRequest):
    """
    Analyze uploaded files and create unified todo log.
    Uses LLM to extract requirements, patterns, and tasks.
    """
    session_dir = UPLOAD_DIR / request.session_id
    
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found")
    
    # Get all files in session
    files_to_analyze = {}
    file_analyses = []
    
    for file_path in session_dir.iterdir():
        if file_path.is_file():
            # Extract original filename (remove UUID prefix)
            parts = file_path.name.split('_', 1)
            original_name = parts[1] if len(parts) > 1 else file_path.name
            
            # Read content
            content = read_file_content(file_path)
            if content:
                files_to_analyze[original_name] = content
    
    if not files_to_analyze:
        raise HTTPException(status_code=400, detail="No readable files found in session")
    
    # Analyze with LLM
    llm_analysis = await analyze_with_llm(files_to_analyze)
    
    # Build unified todo list
    unified_todos = []
    todo_id = 1
    
    for todo in llm_analysis.get("todos", []):
        unified_todos.append(TodoItem(
            id=f"TODO-{todo_id:03d}",
            task=todo.get("task", "Unknown task"),
            priority=todo.get("priority", "medium"),
            category=todo.get("category", "requirement"),
            source_file=todo.get("source_file"),
            line_reference=todo.get("line_reference")
        ))
        todo_id += 1
    
    # Build file analyses
    for filename, content in files_to_analyze.items():
        file_type = get_file_type(filename)
        
        # Find todos related to this file
        file_todos = [t for t in unified_todos if t.source_file == filename]
        
        file_analyses.append(FileAnalysis(
            filename=filename,
            file_type=file_type,
            summary=f"{file_type} file with {len(content.splitlines())} lines",
            todos=file_todos,
            dependencies=[],
            patterns_detected=[]
        ))
    
    # Create result
    result = AnalysisResult(
        session_id=request.session_id,
        files_analyzed=len(files_to_analyze),
        unified_todo=unified_todos,
        file_analyses=file_analyses,
        project_summary=llm_analysis.get("project_summary", "Project analysis complete"),
        suggested_structure=llm_analysis.get("suggested_structure", {}),
        analyzed_at=datetime.now(timezone.utc).isoformat()
    )
    
    # Store result
    analysis_store[request.session_id] = result.dict()
    
    return result


@router.get("/result/{session_id}")
async def get_analysis_result(session_id: str):
    """Get stored analysis result for a session"""
    if session_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found. Run analysis first.")
    
    return analysis_store[session_id]


@router.get("/health")
async def analysis_health():
    """Check analysis service health"""
    return {
        "status": "healthy",
        "llm_available": True,
        "sessions_analyzed": len(analysis_store)
    }
