"""
FRANKLIN OS Marketing Content API Routes
=========================================
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from marketing_content import (
    marketing_generator,
    ContentBrief,
    ContentTone,
    ContentType
)

marketing_router = APIRouter(prefix="/api/marketing/content")


# ============================================================================
#                         PYDANTIC MODELS
# ============================================================================

class ContentBriefRequest(BaseModel):
    project_name: str
    project_description: str
    target_audience: str
    unique_value_proposition: str
    key_features: List[str]
    competitors: List[str] = []
    tone: str = "professional"
    keywords: List[str] = []
    call_to_action: str = ""


class GenerateLandingPageRequest(BaseModel):
    brief: ContentBriefRequest


class GenerateEmailSequenceRequest(BaseModel):
    brief: ContentBriefRequest
    num_emails: int = 5


class GenerateSocialMediaRequest(BaseModel):
    brief: ContentBriefRequest
    platforms: List[str] = ["twitter", "linkedin", "facebook", "instagram"]


class GenerateFullPackageRequest(BaseModel):
    brief: ContentBriefRequest


# ============================================================================
#                         HELPER
# ============================================================================

def _create_brief(request: ContentBriefRequest) -> ContentBrief:
    """Convert request to ContentBrief"""
    tone_map = {
        "professional": ContentTone.PROFESSIONAL,
        "casual": ContentTone.CASUAL,
        "technical": ContentTone.TECHNICAL,
        "persuasive": ContentTone.PERSUASIVE,
        "inspirational": ContentTone.INSPIRATIONAL,
        "urgent": ContentTone.URGENT
    }
    
    return ContentBrief(
        project_name=request.project_name,
        project_description=request.project_description,
        target_audience=request.target_audience,
        unique_value_proposition=request.unique_value_proposition,
        key_features=request.key_features,
        competitors=request.competitors,
        tone=tone_map.get(request.tone, ContentTone.PROFESSIONAL),
        keywords=request.keywords,
        call_to_action=request.call_to_action
    )


# ============================================================================
#                         ROUTES
# ============================================================================

@marketing_router.get("/status")
async def get_marketing_status():
    """Get marketing generator status"""
    return marketing_generator.get_status()


@marketing_router.post("/landing-page")
async def generate_landing_page(request: GenerateLandingPageRequest):
    """Generate landing page content"""
    brief = _create_brief(request.brief)
    
    try:
        content = await marketing_generator.generate_landing_page(brief)
        return {
            "success": True,
            "content": content.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@marketing_router.post("/product-description")
async def generate_product_description(request: GenerateLandingPageRequest):
    """Generate product description"""
    brief = _create_brief(request.brief)
    
    try:
        content = await marketing_generator.generate_product_description(brief)
        return {
            "success": True,
            "content": content.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@marketing_router.post("/email-sequence")
async def generate_email_sequence(request: GenerateEmailSequenceRequest):
    """Generate email marketing sequence"""
    brief = _create_brief(request.brief)
    
    try:
        content = await marketing_generator.generate_email_sequence(brief, request.num_emails)
        return {
            "success": True,
            "content": content.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@marketing_router.post("/social-media")
async def generate_social_media(request: GenerateSocialMediaRequest):
    """Generate social media content"""
    brief = _create_brief(request.brief)
    
    try:
        content = await marketing_generator.generate_social_media(brief, request.platforms)
        return {
            "success": True,
            "content": content.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@marketing_router.post("/full-package")
async def generate_full_marketing_package(request: GenerateFullPackageRequest):
    """Generate complete marketing package"""
    brief = _create_brief(request.brief)
    
    try:
        results = await marketing_generator.generate_full_marketing_package(brief)
        return {
            "success": True,
            "package": {k: v.to_dict() for k, v in results.items()},
            "total_pieces": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@marketing_router.get("/content")
async def list_generated_content():
    """List all generated content"""
    return {
        "content": marketing_generator.list_content(),
        "total": len(marketing_generator.generated_content)
    }


@marketing_router.get("/content/{content_id}")
async def get_content(content_id: str):
    """Get specific generated content"""
    content = marketing_generator.get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


@marketing_router.get("/tones")
async def get_available_tones():
    """Get available content tones"""
    return {
        "tones": [
            {"id": t.value, "name": t.name, "description": {
                "professional": "Formal, business-appropriate language",
                "casual": "Friendly, conversational tone",
                "technical": "Detailed, specification-focused",
                "persuasive": "Action-oriented, conversion-focused",
                "inspirational": "Motivational, aspirational messaging",
                "urgent": "Time-sensitive, creates FOMO"
            }.get(t.value, "")}
            for t in ContentTone
        ]
    }


@marketing_router.get("/content-types")
async def get_content_types():
    """Get available content types"""
    return {
        "types": [
            {"id": ct.value, "name": ct.name}
            for ct in ContentType
        ]
    }
