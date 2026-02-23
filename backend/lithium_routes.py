"""
LITHIUM API ROUTES
Real endpoints for build, certify, download
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Header, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import asyncio
import os
import uuid
import json

from build_service import build_service
from database import db
from certification_engine import certification_engine
from franklin_realtime import broker
from agents_catalog import AGENT_CATALOG, get_certified_agents
from supabase_util import get_supabase, safe_upsert, table_has_rows, upsert_build_record, upsert_artifacts, upsert_certification
from supabase_seeds import AGENT_SEED, BOT_TASK_TIERS_SEED, ACADEMY_MODULES_SEED, DOMAIN_BADGES_SEED
from headless_worker import enqueue_job, jobs as headless_jobs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lithium", tags=["lithium"])

API_TOKEN = os.getenv("API_TOKEN")
SPINE_URL = os.getenv("SPINE_URL")
SPINE_ROOT_HASH = os.getenv("SPINE_ROOT_HASH")
SPINE_READ_TOKENS = {t.strip() for t in os.getenv("SPINE_READ_TOKENS", "").split(",") if t.strip()}
RATE_BUCKET: Dict[str, float] = {}
RATE_WINDOW = 1.0  # seconds between requests per client (very light placeholder)


async def require_auth(request: Request, authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    if not API_TOKEN:
        return
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    if x_api_key:
        token = x_api_key
    if token != API_TOKEN:
        logger.warning("Auth failed for %s", request.url.path)
        raise HTTPException(status_code=401, detail="Unauthorized")


def rate_limit(request: Request):
    key = request.client.host if request.client else "global"
    now = asyncio.get_event_loop().time()
    last = RATE_BUCKET.get(key, 0)
    if now - last < RATE_WINDOW:
        raise HTTPException(status_code=429, detail="Too many requests")
    RATE_BUCKET[key] = now


def require_spine_read_token(request: Request, authorization: Optional[str] = Header(None), x_spine_read_token: Optional[str] = Header(None)):
    if not SPINE_READ_TOKENS:
        return
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    if x_spine_read_token:
        token = x_spine_read_token
    if not token or token not in SPINE_READ_TOKENS:
        raise HTTPException(status_code=401, detail="Unauthorized (spine read)")


def seed_supabase_catalogs():
    sb = get_supabase()
    if not sb:
        return
    try:
        if not table_has_rows("agents_catalog"):
            safe_upsert("agents_catalog", AGENT_SEED)
        if not table_has_rows("bot_task_tiers"):
            safe_upsert("bot_task_tiers", BOT_TASK_TIERS_SEED)
        if not table_has_rows("academy_modules"):
            safe_upsert("academy_modules", ACADEMY_MODULES_SEED)
        if not table_has_rows("domain_badges"):
            safe_upsert("domain_badges", DOMAIN_BADGES_SEED)
    except Exception as e:
        logger.warning("Supabase seeding failed: %s", e)


@router.get("/headless/jobs/{job_id}")
async def headless_job_status(job_id: str):
    job = headless_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


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
    agent_id: Optional[str] = None
    contract: Optional[dict] = None


class HeadlessBuildRequest(BaseModel):
    prompt: str
    project_id: str
    agent_id: Optional[str] = None
    contract: Optional[dict] = None


class CertifyRequest(BaseModel):
    build_id: str


# ============================================================================
# REALTIME STREAM (SSE)
# ============================================================================


@router.post("/headless/build")
async def headless_build(req: HeadlessBuildRequest):
    if not req.project_id:
        raise HTTPException(status_code=400, detail="project_id required")
    job_id = enqueue_job(req.prompt, req.project_id, req.agent_id, req.contract)
    return {"job_id": job_id, "status": "queued"}


@router.get("/stream/projects/{project_id}")
async def stream_project(project_id: str, request: Request, authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    await require_auth(request, authorization, x_api_key)
    rate_limit(request)
    queue = await broker.subscribe(project_id)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                data = await queue.get()
                yield f"data: {data}\n\n"
        finally:
            await broker.unsubscribe(project_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


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
        if request.project_id:
            await broker.push(request.project_id, {
                "type": "build_progress",
                "status": "started",
                "project_id": request.project_id,
                "stage": "construction"
            })

        result = await build_service.create_build(
            mission=request.mission,
            spec_content=request.spec_content,
            architecture_content=request.architecture_content,
            code_content=request.code_content,
            health_report=request.health_report,
            user_id=request.user_id,
            project_id=request.project_id
        )
        # Supabase record
        upsert_build_record({
            "build_id": result.get("build_id"),
            "status": result.get("status"),
            "file_count": result.get("stats", {}).get("files_created"),
            "total_lines": result.get("stats", {}).get("total_lines"),
            "agent_id": request.agent_id,
            "contract": request.contract
        }, project_id=request.project_id, mission=request.mission)
        upsert_artifacts(result.get("build_id"), result.get("files", []))
        if request.project_id:
            await broker.push(request.project_id, {
                "type": "build_progress",
                "status": "completed",
                "project_id": request.project_id,
                "build_id": result.get("build_id"),
                "stage": "construction"
            })
        return result
    except Exception as e:
        logger.error(f"Build creation failed: {e}")
        if request.project_id:
            await broker.push(request.project_id, {
                "type": "build_progress",
                "status": "error",
                "project_id": request.project_id,
                "error": str(e)
            })
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


@router.get("/status/{build_id}")
async def get_status(build_id: str, request: Request, authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    await require_auth(request, authorization, x_api_key)
    rate_limit(request)
    try:
        build = await build_service.get_build_status(build_id)
    except Exception as e:
        logger.error(f"Status build failed: {e}")
        build = {"error": str(e)}

    cert = None
    try:
        await db.initialize()
        cert = await db.get_certification(build_id)
    except Exception as e:
        cert = {"error": str(e)}

    return {
        "build": build,
        "certification": cert if cert else {"certified": False}
    }


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
    project_id = None
    try:
        build_status = await build_service.get_build_status(request.build_id)
        if isinstance(build_status, dict) and build_status.get("build"):
            project_id = build_status["build"].get("project_id")
    except Exception:
        project_id = None

    try:
        # Broadcast start
        await broker.push(request.build_id, {
            "type": "cert_progress",
            "status": "started",
            "build_id": request.build_id,
            "stage": "validation"
        })
        if project_id:
            await broker.push(project_id, {
                "type": "cert_progress",
                "status": "started",
                "build_id": request.build_id,
                "project_id": project_id,
                "stage": "validation"
            })

        result = await build_service.certify_build(request.build_id)

        await broker.push(request.build_id, {
            "type": "cert_progress",
            "status": "completed",
            "build_id": request.build_id,
            "stage": "governance",
            "result": result
        })
        if project_id:
            await broker.push(project_id, {
                "type": "cert_progress",
                "status": "completed",
                "build_id": request.build_id,
                "project_id": project_id,
                "stage": "governance",
                "result": result
            })
        upsert_certification(request.build_id, result)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Certification failed: {e}")
        await broker.push(request.build_id, {
            "type": "cert_progress",
            "status": "error",
            "build_id": request.build_id,
            "error": str(e)
        })
        if project_id:
            await broker.push(project_id, {
                "type": "cert_progress",
                "status": "error",
                "build_id": request.build_id,
                "project_id": project_id,
                "error": str(e)
            })
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
# VOICE TO BUILD (ASR STUB)
# ============================================================================

@router.post("/voice/transcribe")
async def transcribe_voice(request: Request, file: UploadFile = File(...), provider: Optional[str] = None, authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    await require_auth(request, authorization, x_api_key)
    rate_limit(request)
    # Stub implementation: real providers can be wired via env
    text = "Transcribed voice request (stub). Provide ASR provider/env to enable real transcription."
    try:
        await file.read()  # drain upload; ignore content
    except Exception as e:
        logger.warning("ASR read failed: %s", e)
    return {"text": text, "provider": provider or "stub"}


# ============================================================================
# AGENTS / BOTS
# ============================================================================

class DeployRequest(BaseModel):
    agent_id: str
    task: str
    target: str
    project_id: Optional[str] = None


@router.get("/agents/catalog")
async def list_agents(request: Request, authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    await require_auth(request, authorization, x_api_key)
    rate_limit(request)
    sb = get_supabase()
    seed_supabase_catalogs()
    if sb:
        try:
            if not table_has_rows("agents_catalog"):
                safe_upsert("agents_catalog", AGENT_SEED)
            res = sb.table("agents_catalog").select("*").execute()
            if res.data:
                return {"agents": res.data}
        except Exception as e:
            logger.warning("Supabase agents fetch failed: %s", e)
    return {"agents": AGENT_CATALOG}


@router.post("/agents/deploy")
async def deploy_agent(req: DeployRequest, request: Request, authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    await require_auth(request, authorization, x_api_key)
    rate_limit(request)
    agent = next((a for a in AGENT_CATALOG if a["id"] == req.agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if not agent.get("certified"):
        raise HTTPException(status_code=400, detail="Agent not certified")
    deploy_id = str(uuid.uuid4())
    event = {
        "type": "agent_deploy",
        "status": "scheduled",
        "agent_id": req.agent_id,
        "task": req.task,
        "target": req.target,
        "deploy_id": deploy_id
    }
    if req.project_id:
        event["project_id"] = req.project_id
        await broker.push(req.project_id, event)
    logger.info("Agent deploy scheduled %s -> %s", req.agent_id, req.target)
    return {"deploy_id": deploy_id, "agent": agent, "status": "scheduled"}


# ============================================================================
# AI ACADEMY
# ============================================================================

@router.get("/academy/agents")
async def academy_agents(request: Request, authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    await require_auth(request, authorization, x_api_key)
    rate_limit(request)
    sb = get_supabase()
    if sb:
        try:
            if not table_has_rows("agents_catalog"):
                safe_upsert("agents_catalog", AGENT_SEED)
            res = sb.table("agents_catalog").select("*").eq("certified", True).execute()
            if res.data:
                return {"certified_agents": res.data}
        except Exception as e:
            logger.warning("Supabase academy agents fetch failed: %s", e)
    return {"certified_agents": get_certified_agents()}


@router.get("/academy/modules")
async def academy_modules(request: Request, authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    await require_auth(request, authorization, x_api_key)
    rate_limit(request)
    sb = get_supabase()
    if sb:
        try:
            if not table_has_rows("academy_modules"):
                safe_upsert("academy_modules", ACADEMY_MODULES_SEED)
            res = sb.table("academy_modules").select("*").execute()
            if res.data:
                return {"modules": res.data}
        except Exception as e:
            logger.warning("Supabase modules fetch failed: %s", e)
    return {"modules": ACADEMY_MODULES_SEED}


@router.get("/academy/badges")
async def academy_badges(request: Request, authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    await require_auth(request, authorization, x_api_key)
    rate_limit(request)
    sb = get_supabase()
    if sb:
        try:
            if not table_has_rows("domain_badges"):
                safe_upsert("domain_badges", DOMAIN_BADGES_SEED)
            res = sb.table("domain_badges").select("*").execute()
            if res.data:
                return {"badges": res.data}
        except Exception as e:
            logger.warning("Supabase badges fetch failed: %s", e)
    return {"badges": DOMAIN_BADGES_SEED}


# ============================================================================
# SPINE (READ-ONLY) ENDPOINTS
# ============================================================================

@router.get("/spine/status")
async def spine_status(request: Request, authorization: Optional[str] = Header(None), x_spine_read_token: Optional[str] = Header(None)):
    require_spine_read_token(request, authorization, x_spine_read_token)
    return {
        "spine": "online",
        "url": SPINE_URL,
        "root_hash": SPINE_ROOT_HASH,
        "note": "read-only view; writes anchored externally"
    }


@router.get("/spine/ledger/{ref}")
async def spine_ledger(ref: str, request: Request, authorization: Optional[str] = Header(None), x_spine_read_token: Optional[str] = Header(None)):
    require_spine_read_token(request, authorization, x_spine_read_token)
    return {
        "ref": ref,
        "url": SPINE_URL,
        "root_hash": SPINE_ROOT_HASH,
        "message": "External spine ledger is hosted separately; this is a read-only pointer."
    }



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
