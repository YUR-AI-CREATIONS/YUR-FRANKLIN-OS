"""
WORKFLOW GENERATOR API
Converts confirmed TODO list into a unified, structured workflow
with task dependencies, phases, and execution order.
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import Trinity for LLM
from trinity_spine import trinity_spine

router = APIRouter(prefix="/api/workflow", tags=["workflow"])


class TodoItem(BaseModel):
    id: str
    task: str
    priority: str
    category: str
    source_file: Optional[str] = None
    line_reference: Optional[str] = None


class WorkflowTask(BaseModel):
    id: str
    name: str
    description: str
    phase: int
    priority: str
    category: str
    estimated_effort: str  # small, medium, large
    dependencies: List[str]  # IDs of tasks this depends on
    deliverables: List[str]
    status: str = "pending"


class WorkflowPhase(BaseModel):
    phase_num: int
    name: str
    description: str
    tasks: List[WorkflowTask]
    estimated_duration: str


class GenerateWorkflowRequest(BaseModel):
    session_id: str
    todos: List[TodoItem]
    tech_stack: str = "python"
    project_type: str = "web_app"


class WorkflowResult(BaseModel):
    session_id: str
    project_name: str
    tech_stack: str
    total_tasks: int
    total_phases: int
    phases: List[WorkflowPhase]
    file_structure: Dict[str, Any]
    architecture_notes: List[str]
    created_at: str


# Store workflows
workflow_store = {}


def categorize_todos(todos: List[TodoItem]) -> Dict[str, List[TodoItem]]:
    """Group todos by category for better workflow organization"""
    categories = {
        "requirement": [],
        "feature": [],
        "bug": [],
        "refactor": [],
        "test": [],
        "docs": [],
        "other": []
    }
    
    for todo in todos:
        cat = todo.category.lower() if todo.category else "other"
        if cat in categories:
            categories[cat].append(todo)
        else:
            categories["other"].append(todo)
    
    return categories


def determine_dependencies(todos: List[TodoItem]) -> Dict[str, List[str]]:
    """Determine task dependencies based on category and priority"""
    deps = {}
    
    # Requirements come first
    requirements = [t for t in todos if t.category == "requirement"]
    features = [t for t in todos if t.category == "feature"]
    bugs = [t for t in todos if t.category == "bug"]
    refactors = [t for t in todos if t.category == "refactor"]
    tests = [t for t in todos if t.category == "test"]
    docs = [t for t in todos if t.category == "docs"]
    
    # Features depend on requirements
    for f in features:
        deps[f.id] = [r.id for r in requirements[:2]]  # Depend on first 2 requirements
    
    # Tests depend on features
    for t in tests:
        deps[t.id] = [f.id for f in features[:1]]  # Depend on first feature
    
    # Docs depend on features being done
    for d in docs:
        deps[d.id] = [f.id for f in features]
    
    return deps


async def generate_workflow_with_llm(todos: List[TodoItem], tech_stack: str) -> Dict[str, Any]:
    """Use LLM to generate intelligent workflow from todos"""
    
    todos_text = "\n".join([
        f"- [{t.priority.upper()}] {t.id}: {t.task} (Category: {t.category})"
        for t in todos
    ])
    
    prompt = f"""Create a development workflow from these tasks for a {tech_stack} project:

{todos_text}

Return JSON with this structure:
{{
    "project_name": "descriptive name",
    "phases": [
        {{
            "phase_num": 1,
            "name": "Phase Name",
            "description": "what this phase accomplishes",
            "estimated_duration": "X days",
            "tasks": [
                {{
                    "id": "WF-001",
                    "original_todo": "TODO-001",
                    "name": "short task name",
                    "description": "detailed description",
                    "priority": "high/medium/low",
                    "category": "category",
                    "estimated_effort": "small/medium/large",
                    "dependencies": [],
                    "deliverables": ["what this produces"]
                }}
            ]
        }}
    ],
    "file_structure": {{
        "folders": ["src", "tests"],
        "key_files": ["main.py", "config.py"]
    }},
    "architecture_notes": ["important architectural decisions"]
}}

Organize into logical phases: Setup, Core Features, Testing, Documentation.
Return ONLY valid JSON."""

    result = await trinity_spine.generate(
        prompt=prompt,
        system_prompt="You are a project manager creating development workflows. Return only valid JSON.",
        temperature=0.3,
        max_tokens=3000
    )
    
    if not result.get("success"):
        return create_fallback_workflow(todos, tech_stack)
    
    response_text = result.get("response", "")
    
    try:
        clean_response = response_text.strip()
        if clean_response.startswith("```"):
            lines = clean_response.split('\n')
            clean_response = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
        
        start = clean_response.find('{')
        end = clean_response.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = clean_response[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    return create_fallback_workflow(todos, tech_stack)


def create_fallback_workflow(todos: List[TodoItem], tech_stack: str) -> Dict[str, Any]:
    """Create a structured workflow without LLM"""
    
    categorized = categorize_todos(todos)
    phases = []
    task_counter = 1
    
    # Phase 1: Setup & Requirements
    phase1_tasks = []
    for todo in categorized.get("requirement", []):
        phase1_tasks.append({
            "id": f"WF-{task_counter:03d}",
            "original_todo": todo.id,
            "name": todo.task[:50],
            "description": todo.task,
            "priority": todo.priority,
            "category": todo.category,
            "estimated_effort": "medium",
            "dependencies": [],
            "deliverables": ["Requirement documented"]
        })
        task_counter += 1
    
    if phase1_tasks:
        phases.append({
            "phase_num": 1,
            "name": "Setup & Requirements",
            "description": "Define project requirements and initial setup",
            "estimated_duration": f"{len(phase1_tasks)} days",
            "tasks": phase1_tasks
        })
    
    # Phase 2: Core Features
    phase2_tasks = []
    phase1_ids = [t["id"] for t in phase1_tasks]
    
    for todo in categorized.get("feature", []):
        phase2_tasks.append({
            "id": f"WF-{task_counter:03d}",
            "original_todo": todo.id,
            "name": todo.task[:50],
            "description": todo.task,
            "priority": todo.priority,
            "category": todo.category,
            "estimated_effort": "large" if todo.priority == "high" else "medium",
            "dependencies": phase1_ids[:1],
            "deliverables": ["Feature implemented", "Code reviewed"]
        })
        task_counter += 1
    
    if phase2_tasks:
        phases.append({
            "phase_num": 2,
            "name": "Core Implementation",
            "description": "Build core features and functionality",
            "estimated_duration": f"{len(phase2_tasks) * 2} days",
            "tasks": phase2_tasks
        })
    
    # Phase 3: Bug Fixes & Refactoring
    phase3_tasks = []
    phase2_ids = [t["id"] for t in phase2_tasks]
    
    for todo in categorized.get("bug", []) + categorized.get("refactor", []):
        phase3_tasks.append({
            "id": f"WF-{task_counter:03d}",
            "original_todo": todo.id,
            "name": todo.task[:50],
            "description": todo.task,
            "priority": todo.priority,
            "category": todo.category,
            "estimated_effort": "small" if todo.category == "bug" else "medium",
            "dependencies": phase2_ids[:1] if phase2_ids else [],
            "deliverables": ["Issue resolved", "Tests passing"]
        })
        task_counter += 1
    
    if phase3_tasks:
        phases.append({
            "phase_num": 3,
            "name": "Stabilization",
            "description": "Fix bugs and refactor code",
            "estimated_duration": f"{len(phase3_tasks)} days",
            "tasks": phase3_tasks
        })
    
    # Phase 4: Testing & Documentation
    phase4_tasks = []
    phase3_ids = [t["id"] for t in phase3_tasks]
    all_prev_ids = phase1_ids + phase2_ids + phase3_ids
    
    for todo in categorized.get("test", []) + categorized.get("docs", []):
        phase4_tasks.append({
            "id": f"WF-{task_counter:03d}",
            "original_todo": todo.id,
            "name": todo.task[:50],
            "description": todo.task,
            "priority": todo.priority,
            "category": todo.category,
            "estimated_effort": "small",
            "dependencies": all_prev_ids[-2:] if all_prev_ids else [],
            "deliverables": ["Tests written" if todo.category == "test" else "Documentation complete"]
        })
        task_counter += 1
    
    # Add any uncategorized tasks
    for todo in categorized.get("other", []):
        phase4_tasks.append({
            "id": f"WF-{task_counter:03d}",
            "original_todo": todo.id,
            "name": todo.task[:50],
            "description": todo.task,
            "priority": todo.priority,
            "category": todo.category,
            "estimated_effort": "medium",
            "dependencies": [],
            "deliverables": ["Task complete"]
        })
        task_counter += 1
    
    if phase4_tasks:
        phases.append({
            "phase_num": 4,
            "name": "Quality & Docs",
            "description": "Testing and documentation",
            "estimated_duration": f"{len(phase4_tasks)} days",
            "tasks": phase4_tasks
        })
    
    # If no phases created, create a single phase with all tasks
    if not phases:
        all_tasks = []
        for todo in todos:
            all_tasks.append({
                "id": f"WF-{task_counter:03d}",
                "original_todo": todo.id,
                "name": todo.task[:50],
                "description": todo.task,
                "priority": todo.priority,
                "category": todo.category,
                "estimated_effort": "medium",
                "dependencies": [],
                "deliverables": ["Task complete"]
            })
            task_counter += 1
        
        phases.append({
            "phase_num": 1,
            "name": "Implementation",
            "description": "Complete all tasks",
            "estimated_duration": f"{len(all_tasks)} days",
            "tasks": all_tasks
        })
    
    # Generate file structure based on tech stack
    file_structures = {
        "python": {
            "folders": ["src", "tests", "config", "docs"],
            "key_files": ["main.py", "requirements.txt", "config.py", ".env"]
        },
        "javascript": {
            "folders": ["src", "tests", "public", "config"],
            "key_files": ["index.js", "package.json", "config.js", ".env"]
        },
        "typescript": {
            "folders": ["src", "tests", "types", "config"],
            "key_files": ["index.ts", "package.json", "tsconfig.json", ".env"]
        },
        "go": {
            "folders": ["cmd", "internal", "pkg", "tests"],
            "key_files": ["main.go", "go.mod", "config.go"]
        },
        "rust": {
            "folders": ["src", "tests", "benches"],
            "key_files": ["main.rs", "Cargo.toml", "lib.rs"]
        }
    }
    
    return {
        "project_name": f"{tech_stack.capitalize()} Project",
        "phases": phases,
        "file_structure": file_structures.get(tech_stack, file_structures["python"]),
        "architecture_notes": [
            f"Using {tech_stack} as primary language",
            "Modular architecture for scalability",
            "Test-driven development approach"
        ]
    }


@router.post("/generate", response_model=WorkflowResult)
async def generate_workflow(request: GenerateWorkflowRequest):
    """
    Generate a unified workflow from confirmed TODO items.
    Organizes tasks into phases with dependencies and deliverables.
    """
    
    if not request.todos:
        raise HTTPException(status_code=400, detail="No TODO items provided")
    
    # Generate workflow
    workflow_data = await generate_workflow_with_llm(request.todos, request.tech_stack)
    
    # Build phases
    phases = []
    total_tasks = 0
    
    for phase_data in workflow_data.get("phases", []):
        tasks = []
        for task_data in phase_data.get("tasks", []):
            tasks.append(WorkflowTask(
                id=task_data.get("id", f"WF-{total_tasks+1:03d}"),
                name=task_data.get("name", "Task"),
                description=task_data.get("description", ""),
                phase=phase_data.get("phase_num", 1),
                priority=task_data.get("priority", "medium"),
                category=task_data.get("category", "feature"),
                estimated_effort=task_data.get("estimated_effort", "medium"),
                dependencies=task_data.get("dependencies", []),
                deliverables=task_data.get("deliverables", []),
                status="pending"
            ))
            total_tasks += 1
        
        phases.append(WorkflowPhase(
            phase_num=phase_data.get("phase_num", len(phases) + 1),
            name=phase_data.get("name", f"Phase {len(phases) + 1}"),
            description=phase_data.get("description", ""),
            tasks=tasks,
            estimated_duration=phase_data.get("estimated_duration", "TBD")
        ))
    
    result = WorkflowResult(
        session_id=request.session_id,
        project_name=workflow_data.get("project_name", "Project"),
        tech_stack=request.tech_stack,
        total_tasks=total_tasks,
        total_phases=len(phases),
        phases=phases,
        file_structure=workflow_data.get("file_structure", {}),
        architecture_notes=workflow_data.get("architecture_notes", []),
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    # Store workflow
    workflow_store[request.session_id] = result.dict()
    
    return result


@router.get("/result/{session_id}")
async def get_workflow(session_id: str):
    """Get stored workflow for a session"""
    if session_id not in workflow_store:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow_store[session_id]


@router.post("/update-task-status")
async def update_task_status(session_id: str, task_id: str, status: str):
    """Update the status of a workflow task"""
    if session_id not in workflow_store:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflow_store[session_id]
    
    for phase in workflow["phases"]:
        for task in phase["tasks"]:
            if task["id"] == task_id:
                task["status"] = status
                return {"success": True, "task_id": task_id, "new_status": status}
    
    raise HTTPException(status_code=404, detail="Task not found")


@router.get("/health")
async def workflow_health():
    """Check workflow service health"""
    return {
        "status": "healthy",
        "workflows_created": len(workflow_store)
    }
