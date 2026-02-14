"""
SIMPLE BUILD ROUTES
Clean API endpoints for the simple build service.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import logging

from simple_build import simple_build

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/build", tags=["build"])


class SimpleBuildRequest(BaseModel):
    prompt: str


@router.post("/create")
async def create_build(request: SimpleBuildRequest):
    """
    Create a new build from a simple prompt.
    
    Example:
        POST /api/build/create
        {"prompt": "build a calculator with add, subtract, multiply, divide"}
    
    Returns:
        Build ID, file list, tree structure, and all file contents.
    """
    if not request.prompt or len(request.prompt.strip()) < 3:
        raise HTTPException(status_code=400, detail="Prompt too short")
    
    try:
        result = await simple_build.build(request.prompt.strip())
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500, 
                detail=result.get("error", "Build failed")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Build failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{build_id}")
async def get_build(build_id: str):
    """Get build info including tree and file list."""
    tree = simple_build.get_tree(build_id)
    if "not found" in tree.lower():
        raise HTTPException(status_code=404, detail="Build not found")
    
    return {
        "build_id": build_id,
        "tree": tree,
        "exists": True
    }


@router.get("/{build_id}/file/{filepath:path}")
async def get_file(build_id: str, filepath: str):
    """Get content of a specific file from a build."""
    content = simple_build.get_file(build_id, filepath)
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "build_id": build_id,
        "path": filepath,
        "content": content
    }


@router.get("/{build_id}/download")
async def download_build(build_id: str):
    """Download the entire build as a ZIP file."""
    zip_path = simple_build.get_zip_path(build_id)
    if not zip_path:
        raise HTTPException(status_code=404, detail="Build not found")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"franklin-build-{build_id}.zip"
    )


@router.get("/health/check")
async def health_check():
    """Health check for the build service."""
    return {
        "status": "online",
        "service": "simple_build",
        "llm_providers": {
            "anthropic": bool(simple_build.anthropic_key),
            "xai": bool(simple_build.xai_key),
            "openai": bool(simple_build.openai_key),
            "google": bool(simple_build.google_key)
        }
    }
