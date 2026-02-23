"""
SIMPLE BUILD ROUTES
Clean API for the real build system
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from simple_build import simple_build
from certification_engine import certification_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/simple-build", tags=["simple-build"])


class BuildRequest(BaseModel):
    prompt: str
    tech_stack: Optional[str] = "python"


class CertifyRequest(BaseModel):
    build_id: str


# ============================================================================
# BUILD ENDPOINTS
# ============================================================================

@router.post("/build")
async def create_build(request: BuildRequest):
    """
    Build something. Real files, real code.
    
    Example:
        POST /api/simple-build/build
        {"prompt": "build a todo list API", "tech_stack": "python"}
    """
    try:
        result = await simple_build.build(request.prompt, request.tech_stack)
        return result
    except Exception as e:
        logger.error(f"Build failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/build/{build_id}")
async def get_build(build_id: str):
    """Get build details and files"""
    from pathlib import Path
    
    project_dir = Path("/app/generated_projects") / build_id
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Build not found")
    
    files = []
    for f in project_dir.rglob("*"):
        if f.is_file():
            rel_path = str(f.relative_to(project_dir))
            files.append({
                "path": rel_path,
                "size": f.stat().st_size
            })
    
    return {
        "build_id": build_id,
        "files": files,
        "tree": simple_build.get_tree(build_id)
    }


@router.get("/build/{build_id}/file/{filepath:path}")
async def get_file(build_id: str, filepath: str):
    """Get content of a specific file"""
    content = simple_build.get_file(build_id, filepath)
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")
    return {"path": filepath, "content": content}


@router.get("/build/{build_id}/download")
async def download_build(build_id: str):
    """Download build as ZIP"""
    zip_path = simple_build.get_zip_path(build_id)
    if not zip_path:
        raise HTTPException(status_code=404, detail="Build not found")
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"franklin-os-{build_id}.zip"
    )


# ============================================================================
# CERTIFICATION ENDPOINTS
# ============================================================================

@router.post("/certify")
async def certify_build(request: CertifyRequest):
    """
    Run 8-gate certification on a build
    """
    from pathlib import Path
    
    project_dir = Path("/app/generated_projects") / request.build_id
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Build not found")
    
    # Gather files
    files = []
    for f in project_dir.rglob("*"):
        if f.is_file():
            rel_path = str(f.relative_to(project_dir))
            try:
                content = f.read_text()
                ext = f.suffix.lstrip('.')
                lang_map = {'py': 'python', 'js': 'javascript', 'ts': 'typescript',
                           'json': 'json', 'html': 'html', 'css': 'css'}
                files.append({
                    "path": rel_path,
                    "content": content,
                    "language": lang_map.get(ext, ext)
                })
            except Exception:
                pass
    
    # Run certification
    result = await certification_engine.run_all_gates(
        build_id=request.build_id,
        mission="",  # We don't have mission stored, but gates will still run
        spec="",
        architecture="",
        files=files
    )
    
    return result


@router.get("/certify/{build_id}")
async def get_certification(build_id: str):
    """Get certification status for a build"""
    # For now, return a simple status
    # In production, this would query the database
    from pathlib import Path
    
    project_dir = Path("/app/generated_projects") / build_id
    if not project_dir.exists():
        return {"build_id": build_id, "certified": False, "message": "Build not found"}
    
    return {
        "build_id": build_id,
        "certified": False,
        "message": "Run POST /api/simple-build/certify to certify"
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health():
    """Health check"""
    from pathlib import Path
    
    projects_dir = Path("/app/generated_projects")
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        "status": "healthy",
        "projects_dir": str(projects_dir),
        "writable": projects_dir.exists()
    }
