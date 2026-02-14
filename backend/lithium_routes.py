"""
LITHIUM API ROUTES
Real endpoints for build, certify, download
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from build_service import build_service
from database import db
from certification_engine import certification_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lithium", tags=["lithium"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class BuildRequest(BaseModel):
    mission: str
    spec_content: str
    architecture_content: str
    code_content: str
    health_report: str = ""
    user_id: Optional[str] = None
    project_id: Optional[str] = None


class CertifyRequest(BaseModel):
    build_id: str


# ============================================================================
# BUILD ROUTES
# ============================================================================

@router.post("/build")
async def create_build(request: BuildRequest):
    """
    Create a new build with real files
    
    This endpoint:
    1. Parses the code content into actual files
    2. Creates project directory structure
    3. Stores in database (PostgreSQL + MongoDB)
    4. Returns build ID and file list
    """
    try:
        result = await build_service.create_build(
            mission=request.mission,
            spec_content=request.spec_content,
            architecture_content=request.architecture_content,
            code_content=request.code_content,
            health_report=request.health_report,
            user_id=request.user_id,
            project_id=request.project_id
        )
        return result
    except Exception as e:
        logger.error(f"Build creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/build/{build_id}")
async def get_build(build_id: str):
    """Get build status and details"""
    try:
        result = await build_service.get_build_status(build_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get build failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/build/{build_id}/tree")
async def get_build_tree(build_id: str):
    """Get project directory tree"""
    try:
        tree = await build_service.get_project_tree(build_id)
        return {"build_id": build_id, "tree": tree}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/build/{build_id}/file/{filepath:path}")
async def get_file_content(build_id: str, filepath: str):
    """Get content of a specific file"""
    try:
        content = await build_service.get_file_content(build_id, filepath)
        if content is None:
            raise HTTPException(status_code=404, detail="File not found")
        return {"build_id": build_id, "path": filepath, "content": content}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/build/{build_id}/download")
async def download_build(build_id: str):
    """Download build as ZIP file"""
    try:
        zip_path = await build_service.download_zip_path(build_id)
        if not zip_path:
            raise HTTPException(status_code=404, detail="Build not found or ZIP not available")
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"franklin-os-build-{build_id}.zip"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CERTIFICATION ROUTES
# ============================================================================

@router.post("/certify")
async def certify_build(request: CertifyRequest):
    """
    Run 8-gate certification on a build
    
    This runs REAL validation:
    - Gate 1: Intent validation
    - Gate 2: Data validation
    - Gate 3: Model validation
    - Gate 4: Vector/RAG validation
    - Gate 5: Orchestration validation
    - Gate 6: API validation
    - Gate 7: UI validation
    - Gate 8: Security validation
    """
    try:
        result = await build_service.certify_build(request.build_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Certification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certification/{build_id}")
async def get_certification(build_id: str):
    """Get certification status for a build"""
    try:
        await db.initialize()
        cert = await db.get_certification(build_id)
        if not cert:
            return {"build_id": build_id, "certified": False, "message": "Not certified yet"}
        
        return {
            "build_id": build_id,
            "certified": cert.get("all_gates_passed", False),
            "hash": cert.get("certification_hash"),
            "certified_at": cert.get("certified_at").isoformat() if cert.get("certified_at") else None,
            "gates": [
                {
                    "gate": i,
                    "name": ["Intent", "Data", "Model", "Vector", "Orchestration", "API", "UI", "Security"][i-1],
                    "passed": cert.get(f"gate_{i}_passed", False),
                    "details": cert.get(f"gate_{i}_details", {})
                }
                for i in range(1, 9)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/certify/gate/{gate_num}")
async def run_single_gate(gate_num: int, request: CertifyRequest):
    """Run a single certification gate"""
    if gate_num < 1 or gate_num > 8:
        raise HTTPException(status_code=400, detail="Gate number must be 1-8")
    
    try:
        await db.initialize()
        build = await db.get_build(request.build_id)
        if not build:
            raise HTTPException(status_code=404, detail="Build not found")
        
        artifacts = await db.get_build_artifacts(request.build_id)
        files = artifacts.get("files", []) if artifacts else []
        
        result = await certification_engine.run_single_gate(
            gate_num=gate_num,
            build_id=request.build_id,
            mission=build.get("mission", ""),
            spec=build.get("spec_content", ""),
            architecture=build.get("architecture_content", ""),
            files=files
        )
        
        return {
            "gate_num": result.gate_num,
            "gate_name": result.gate_name,
            "passed": result.passed,
            "score": result.score,
            "checks_run": result.checks_run,
            "checks_passed": result.checks_passed,
            "details": result.details,
            "errors": result.errors,
            "warnings": result.warnings
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# USER/PROJECT ROUTES (for future use)
# ============================================================================

@router.get("/user/{user_id}/builds")
async def get_user_builds(user_id: str):
    """Get all builds for a user"""
    try:
        await db.initialize()
        builds = await db.get_user_builds(user_id)
        return {"user_id": user_id, "builds": builds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/builds/pending")
async def get_pending_builds():
    """Get builds pending certification"""
    try:
        await db.initialize()
        builds = await db.get_pending_certification_builds()
        return {"pending_builds": builds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def lithium_health():
    """Health check for Lithium services"""
    status = {
        "lithium": "online",
        "database": "unknown",
        "file_system": "unknown"
    }
    
    try:
        await db.initialize()
        # Test database
        await db.pg.fetchval("SELECT 1")
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
    
    try:
        # Test file system
        from pathlib import Path
        test_dir = Path("/app/generated_projects")
        test_dir.mkdir(parents=True, exist_ok=True)
        status["file_system"] = "writable"
    except Exception as e:
        status["file_system"] = f"error: {str(e)}"
    
    return status
