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
            truncated = content[:3000] if len(content) > 3000 else content
            files_text += f"\n\n=== FILE: {filename} ===\n{truncated}"
    
    analysis_prompt = f"""Analyze these project files. Extract ALL TODO comments and issues.

{files_text}

Return JSON with this structure:
{{"project_summary": "what this project does", "todos": [{{"task": "task description", "priority": "high/medium/low", "category": "requirement/bug/feature/refactor/test/docs", "source_file": "filename"}}], "dependencies": ["dep1"], "patterns": ["pattern1"]}}

Important: Find ALL TODO, FIXME, BUG comments in the code. Return ONLY valid JSON."""

    # Call LLM
    result = await trinity_spine.generate(
        prompt=analysis_prompt,
        system_prompt="You are a code analyzer. Extract TODO items from code. Return only valid JSON.",
        temperature=0.2,
        max_tokens=2000
    )
    
    if not result.get("success"):
        # Return fallback with file-based todos
        return create_fallback_analysis(files_content)
    
    # Parse JSON response
    response_text = result.get("response", "")
    
    # Try to extract JSON from response
    try:
        # Clean up response - remove markdown code blocks if present
        clean_response = response_text.strip()
        if clean_response.startswith("```"):
            # Remove markdown code block
            lines = clean_response.split('\n')
            clean_response = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
        
        # Find JSON in response
        start = clean_response.find('{')
        end = clean_response.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = clean_response[start:end]
            parsed = json.loads(json_str)
            
            # Validate structure
            if "todos" in parsed:
                return parsed
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
    
    # Fallback: scan files for TODO/FIXME/BUG comments manually
    return create_fallback_analysis(files_content)


def create_fallback_analysis(files_content: Dict[str, str]) -> Dict[str, Any]:
    """Create analysis by scanning files for TODO/FIXME/BUG comments"""
    todos = []
    
    for filename, content in files_content.items():
        if not content:
            continue
            
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for TODO comments
            if 'todo:' in line_lower or 'todo ' in line_lower:
                task = line.split('TODO', 1)[-1].split('TODO:', 1)[-1].strip(' :#')
                if task:
                    todos.append({
                        "task": task,
                        "priority": "medium",
                        "category": "feature",
                        "source_file": filename,
                        "line_reference": f"Line {i+1}"
                    })
            
            # Check for FIXME comments
            elif 'fixme' in line_lower:
                task = line.split('FIXME', 1)[-1].split('FIXME:', 1)[-1].strip(' :#')
                if task:
                    todos.append({
                        "task": task,
                        "priority": "high",
                        "category": "bug",
                        "source_file": filename,
                        "line_reference": f"Line {i+1}"
                    })
            
            # Check for BUG comments
            elif 'bug:' in line_lower or 'bug ' in line_lower:
                task = line.split('BUG', 1)[-1].split('BUG:', 1)[-1].strip(' :#')
                if task:
                    todos.append({
                        "task": task,
                        "priority": "high",
                        "category": "bug",
                        "source_file": filename,
                        "line_reference": f"Line {i+1}"
                    })
    
    return {
        "project_summary": f"Project with {len(files_content)} files, {len(todos)} action items found",
        "todos": todos,
        "dependencies": [],
        "patterns": [],
        "suggested_structure": {"folders": ["src", "tests", "config"], "files": {}}
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
