"""
TRINITY SPINE ROUTES
Layer 0 API endpoints for FRANKLIN OS
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from trinity_spine import trinity_spine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trinity", tags=["trinity-spine"])


class GenerateRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096


class GovernanceRequest(BaseModel):
    artifact: Dict[str, Any]
    policy_type: Optional[str] = "build"


class LedgerRequest(BaseModel):
    event_type: str
    data: Dict[str, Any]
    signature: Optional[str] = None


class MissionRequest(BaseModel):
    name: str
    description: str
    spec: Dict[str, Any]


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
            "gemini": "gemini-3-flash",
            "gpt": "gpt-5.2",
            "grok": "grok-3",
            "claude": "claude-4.5"
        }
    }


# ============================================================================
# LLM GENERATION
# ============================================================================

@router.post("/generate")
async def trinity_generate(request: GenerateRequest):
    """
    Generate text using Trinity's multi-provider LLM system.
    
    Trinity handles:
    - Provider selection and fallback
    - Load balancing
    - Rate limiting
    - Response validation
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
# GOVERNANCE & COMPLIANCE
# ============================================================================

@router.post("/governance/validate")
async def validate_governance(request: GovernanceRequest):
    """
    Validate an artifact against Trinity governance policies.
    
    Returns compliance score and any policy violations.
    """
    return await trinity_spine.validate_governance(
        artifact=request.artifact,
        policy_type=request.policy_type
    )


@router.get("/evolution/playbook/{domain}")
async def get_evolution_playbook(domain: str = "default"):
    """Get evolution playbook for a domain"""
    playbook = await trinity_spine.get_evolution_playbook(domain)
    
    if not playbook:
        return {
            "domain": domain,
            "playbook": None,
            "message": "No playbook configured for this domain"
        }
    
    return playbook


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


# ============================================================================
# MISSIONS
# ============================================================================

@router.post("/missions")
async def create_mission(request: MissionRequest):
    """Create a new mission in Trinity"""
    return await trinity_spine.create_mission(
        name=request.name,
        description=request.description,
        spec=request.spec
    )


@router.get("/missions/{mission_id}")
async def get_mission(mission_id: str):
    """Get mission by ID"""
    mission = await trinity_spine.get_mission(mission_id)
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return mission
