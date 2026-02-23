"""
SIMPLE BUILD ROUTES
Clean API for the real build system
"""

import os
from datetime import datetime
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
    Run 8-gate certification on a build and save results to database
    """
    from pathlib import Path
    from lithium_database import lithium_db
    
    project_dir = Path("/app/generated_projects") / request.build_id
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Build not found")
    
    # Initialize database
    await lithium_db.initialize()
    
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
    
    # Get build info from database
    build_info = await lithium_db.get_build(request.build_id)
    mission = build_info.get("mission", "") if build_info else ""
    
    # Run certification
    result = await certification_engine.run_all_gates(
        build_id=request.build_id,
        mission=mission,
        spec="",
        architecture="",
        files=files
    )
    
    # Save certification to database
    try:
        await lithium_db.save_certification(result)
        logger.info(f"Certification saved for build {request.build_id}")
    except Exception as e:
        logger.warning(f"Failed to save certification: {e}")
    
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
    """Health check with database status"""
    from pathlib import Path
    from lithium_database import lithium_db
    
    await lithium_db.initialize()
    
    projects_dir = Path("/app/generated_projects")
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    db_status = await lithium_db.health_check()
    
    return {
        "status": "healthy",
        "projects_dir": str(projects_dir),
        "writable": projects_dir.exists(),
        "database": db_status
    }


@router.get("/db/status")
async def db_status():
    """Detailed database status"""
    from lithium_database import lithium_db
    
    await lithium_db.initialize()
    status = await lithium_db.health_check()
    
    return {
        "supabase_url": os.getenv("SUPABASE_URL"),
        "mongo_url": "configured" if os.getenv("MONGO_URL") else "not configured",
        "connections": status
    }


@router.get("/builds")
async def list_builds():
    """List all builds (from filesystem)"""
    from pathlib import Path
    
    projects_dir = Path("/app/generated_projects")
    builds = []
    
    if projects_dir.exists():
        for d in projects_dir.iterdir():
            if d.is_dir():
                files = list(d.rglob("*"))
                file_count = len([f for f in files if f.is_file()])
                builds.append({
                    "build_id": d.name,
                    "files": file_count,
                    "created": datetime.fromtimestamp(d.stat().st_ctime).isoformat()
                })
    
    return {"builds": sorted(builds, key=lambda x: x["created"], reverse=True)}
