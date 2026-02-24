"""
TRINITY SPINE ROUTES
Layer 0 API endpoints for FRANKLIN OS - connects to Lithium API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

from trinity_spine import trinity_spine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trinity", tags=["trinity-spine"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class GenerateRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096


class BuildRequest(BaseModel):
    mission: str
    spec_content: Optional[str] = ""
    architecture_content: Optional[str] = ""
    code_content: Optional[str] = ""
    health_report: Optional[str] = ""
    user_id: Optional[str] = None
    project_id: Optional[str] = None


class CertifyRequest(BaseModel):
    build_id: str


class DeployAgentRequest(BaseModel):
    agent_id: str
    task: str
    target: str
    project_id: Optional[str] = None


class LedgerRequest(BaseModel):
    event_type: str
    data: Dict[str, Any]
    signature: Optional[str] = None


# ============================================================================
# HEALTH & STATUS
# ============================================================================

@router.get("/health")
async def trinity_health():
    """Check Trinity Engine connection and available providers"""
    return await trinity_spine.health_check()


@router.get("/providers")
async def trinity_providers():
    """Get available LLM providers from Trinity"""
    providers = await trinity_spine.get_providers()
    return {
        "providers": providers,
        "primary_order": ["gemini", "grok", "claude", "gpt"],
        "models": {
            "gemini": "gemini-2.5-flash",
            "gpt": "gpt-5.2",
            "grok": "grok-3",
            "claude": "claude-4.5"
        }
    }


# ============================================================================
# SPINE STATUS (READ-ONLY)
# ============================================================================

@router.get("/spine/status")
async def spine_status():
    """Get spine status (read-only view from external Trinity)"""
    return await trinity_spine.get_spine_status()


@router.get("/spine/ledger/{ref}")
async def spine_ledger(ref: str):
    """Get ledger reference (read-only pointer)"""
    return await trinity_spine.get_ledger_ref(ref)


# ============================================================================
# LLM GENERATION
# ============================================================================

@router.post("/generate")
async def trinity_generate(request: GenerateRequest):
    """
    Generate text using Trinity's multi-provider LLM system.
    
    Uses providers in order: Gemini -> OpenAI -> XAI
    """
    result = await trinity_spine.generate(
        prompt=request.prompt,
        system_prompt=request.system_prompt,
        provider=request.provider,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Generation failed")
        )
    
    return result


# ============================================================================
# LITHIUM BUILD API (proxy to external Trinity)
# ============================================================================

@router.post("/lithium/build")
async def lithium_build(request: BuildRequest):
    """
    Create a build via external Lithium API.
    
    This proxies to the Trinity Engine's Lithium build endpoint.
    """
    result = await trinity_spine.create_build(
        mission=request.mission,
        spec_content=request.spec_content,
        architecture_content=request.architecture_content,
        code_content=request.code_content,
        health_report=request.health_report,
        user_id=request.user_id,
        project_id=request.project_id
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@router.post("/lithium/certify")
async def lithium_certify(request: CertifyRequest):
    """Run 8-gate certification via Lithium API"""
    result = await trinity_spine.certify_build(request.build_id)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@router.get("/lithium/status/{build_id}")
async def lithium_status(build_id: str):
    """Get build and certification status from Lithium"""
    return await trinity_spine.get_build_status(build_id)


# ============================================================================
# AGENT CATALOG
# ============================================================================

@router.get("/agents/catalog")
async def agents_catalog():
    """Get agent catalog from Trinity/Lithium"""
    agents = await trinity_spine.get_agents_catalog()
    return {"agents": agents}


@router.post("/agents/deploy")
async def deploy_agent(request: DeployAgentRequest):
    """Deploy an agent via Trinity/Lithium"""
    result = await trinity_spine.deploy_agent(
        agent_id=request.agent_id,
        task=request.task,
        target=request.target,
        project_id=request.project_id
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


# ============================================================================
# ACADEMY
# ============================================================================

@router.get("/academy/modules")
async def academy_modules():
    """Get academy training modules"""
    modules = await trinity_spine.get_academy_modules()
    return {"modules": modules}


@router.get("/academy/badges")
async def academy_badges():
    """Get academy achievement badges"""
    badges = await trinity_spine.get_academy_badges()
    return {"badges": badges}


# ============================================================================
# IMMUTABLE LEDGER
# ============================================================================

@router.post("/ledger/anchor")
async def anchor_to_ledger(request: LedgerRequest):
    """
    Anchor an event to the immutable ledger.
    
    Used for:
    - Build certifications
    - Governance decisions
    - Compliance attestations
    - Evolution milestones
    """
    return await trinity_spine.anchor_to_ledger(
        event_type=request.event_type,
        data=request.data,
        signature=request.signature
    )
