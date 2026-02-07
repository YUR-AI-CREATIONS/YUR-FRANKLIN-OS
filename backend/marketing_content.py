"""
FRANKLIN OS Marketing Content Generator
========================================
AI-powered marketing content generation for certified products.
Generates landing pages, product descriptions, email sequences, and social content.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of marketing content"""
    LANDING_PAGE = "landing_page"
    PRODUCT_DESCRIPTION = "product_description"
    EMAIL_SEQUENCE = "email_sequence"
    SOCIAL_MEDIA = "social_media"
    PRESS_RELEASE = "press_release"
    BLOG_POST = "blog_post"
    AD_COPY = "ad_copy"


class ContentTone(Enum):
    """Tone of the content"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    TECHNICAL = "technical"
    PERSUASIVE = "persuasive"
    INSPIRATIONAL = "inspirational"
    URGENT = "urgent"


@dataclass
class MarketingContent:
    """Generated marketing content"""
    content_id: str
    content_type: ContentType
    title: str
    content: str
    metadata: Dict[str, Any]
    tone: ContentTone
    target_audience: str
    keywords: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_id": self.content_id,
            "content_type": self.content_type.value,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "tone": self.tone.value,
            "target_audience": self.target_audience,
            "keywords": self.keywords,
            "generated_at": self.generated_at.isoformat()
        }


@dataclass
class ContentBrief:
    """Brief for content generation"""
    project_name: str
    project_description: str
    target_audience: str
    unique_value_proposition: str
    key_features: List[str]
    competitors: List[str] = field(default_factory=list)
    tone: ContentTone = ContentTone.PROFESSIONAL
    keywords: List[str] = field(default_factory=list)
    call_to_action: str = ""
    
    def to_prompt(self) -> str:
        return f"""
PROJECT: {self.project_name}
DESCRIPTION: {self.project_description}
TARGET AUDIENCE: {self.target_audience}
UNIQUE VALUE: {self.unique_value_proposition}
KEY FEATURES: {', '.join(self.key_features)}
TONE: {self.tone.value}
KEYWORDS: {', '.join(self.keywords)}
CTA: {self.call_to_action}
"""


class MarketingGenerator:
    """
    AI-powered marketing content generator using Grok.
    Generates certified, professional marketing materials.
    """
    
    def __init__(self):
        self.api_key = os.getenv("XAI_API_KEY")
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.model = "grok-3"
        self.generated_content: Dict[str, MarketingContent] = {}
        
        if self.api_key:
            logger.info("[MARKETING] Grok-powered content generator initialized")
        else:
            logger.warning("[MARKETING] XAI_API_KEY not configured")
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def _generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Call Grok API for content generation"""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 4096
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"[MARKETING] Generation error: {str(e)}")
            return None
    
    async def generate_landing_page(self, brief: ContentBrief) -> MarketingContent:
        """Generate landing page copy"""
        system_prompt = """You are an expert copywriter specializing in high-converting landing pages.
        Create compelling, professional landing page content that:
        - Has a powerful headline and subheadline
        - Highlights key benefits (not just features)
        - Includes social proof sections
        - Has clear calls to action
        - Uses the specified tone
        
        Format the output as JSON with these sections:
        {
            "headline": "...",
            "subheadline": "...",
            "hero_cta": "...",
            "benefits": [{"title": "...", "description": "..."}],
            "features": [{"title": "...", "description": "..."}],
            "testimonial_placeholder": "...",
            "final_cta": "...",
            "footer_tagline": "..."
        }
        """
        
        user_prompt = f"""Create landing page content for:
        {brief.to_prompt()}
        
        Make it compelling and conversion-focused.
        """
        
        content = await self._generate(system_prompt, user_prompt)
        
        if not content:
            content = self._fallback_landing_page(brief)
        
        content_id = f"lp_{len(self.generated_content) + 1:04d}"
        
        result = MarketingContent(
            content_id=content_id,
            content_type=ContentType.LANDING_PAGE,
            title=f"Landing Page - {brief.project_name}",
            content=content,
            metadata={"sections": ["hero", "benefits", "features", "cta"]},
            tone=brief.tone,
            target_audience=brief.target_audience,
            keywords=brief.keywords
        )
        
        self.generated_content[content_id] = result
        return result
    
    async def generate_product_description(self, brief: ContentBrief) -> MarketingContent:
        """Generate product description"""
        system_prompt = """You are an expert product copywriter.
        Create a compelling product description that:
        - Clearly explains what the product does
        - Highlights unique value propositions
        - Addresses target audience pain points
        - Includes key features and benefits
        - Has a strong closing statement
        
        Format as JSON:
        {
            "short_description": "...",
            "long_description": "...",
            "tagline": "...",
            "key_benefits": ["..."],
            "technical_specs": ["..."],
            "ideal_for": "..."
        }
        """
        
        user_prompt = f"""Create product description for:
        {brief.to_prompt()}
        """
        
        content = await self._generate(system_prompt, user_prompt)
        
        if not content:
            content = self._fallback_product_description(brief)
        
        content_id = f"pd_{len(self.generated_content) + 1:04d}"
        
        result = MarketingContent(
            content_id=content_id,
            content_type=ContentType.PRODUCT_DESCRIPTION,
            title=f"Product Description - {brief.project_name}",
            content=content,
            metadata={"word_count": len(content.split())},
            tone=brief.tone,
            target_audience=brief.target_audience,
            keywords=brief.keywords
        )
        
        self.generated_content[content_id] = result
        return result
    
    async def generate_email_sequence(self, brief: ContentBrief, num_emails: int = 5) -> MarketingContent:
        """Generate email marketing sequence"""
        system_prompt = f"""You are an expert email marketing copywriter.
        Create a {num_emails}-email sequence that:
        - Nurtures leads through the funnel
        - Builds trust and authority
        - Addresses objections
        - Drives conversions
        
        Format as JSON array:
        [
            {{
                "email_number": 1,
                "subject_line": "...",
                "preview_text": "...",
                "body": "...",
                "cta": "...",
                "send_day": 0
            }}
        ]
        """
        
        user_prompt = f"""Create email sequence for:
        {brief.to_prompt()}
        
        Generate {num_emails} emails that guide prospects to conversion.
        """
        
        content = await self._generate(system_prompt, user_prompt)
        
        if not content:
            content = self._fallback_email_sequence(brief, num_emails)
        
        content_id = f"em_{len(self.generated_content) + 1:04d}"
        
        result = MarketingContent(
            content_id=content_id,
            content_type=ContentType.EMAIL_SEQUENCE,
            title=f"Email Sequence - {brief.project_name}",
            content=content,
            metadata={"num_emails": num_emails},
            tone=brief.tone,
            target_audience=brief.target_audience,
            keywords=brief.keywords
        )
        
        self.generated_content[content_id] = result
        return result
    
    async def generate_social_media(self, brief: ContentBrief, platforms: List[str] = None) -> MarketingContent:
        """Generate social media content"""
        platforms = platforms or ["twitter", "linkedin", "facebook", "instagram"]
        
        system_prompt = """You are a social media marketing expert.
        Create engaging social media content that:
        - Is platform-appropriate
        - Uses relevant hashtags
        - Drives engagement
        - Includes calls to action
        
        Format as JSON:
        {
            "twitter": [{"post": "...", "hashtags": ["..."]}],
            "linkedin": [{"post": "...", "hashtags": ["..."]}],
            "facebook": [{"post": "...", "hashtags": ["..."]}],
            "instagram": [{"caption": "...", "hashtags": ["..."]}]
        }
        """
        
        user_prompt = f"""Create social media content for:
        {brief.to_prompt()}
        
        Platforms: {', '.join(platforms)}
        Generate 3 posts per platform.
        """
        
        content = await self._generate(system_prompt, user_prompt)
        
        if not content:
            content = self._fallback_social_media(brief, platforms)
        
        content_id = f"sm_{len(self.generated_content) + 1:04d}"
        
        result = MarketingContent(
            content_id=content_id,
            content_type=ContentType.SOCIAL_MEDIA,
            title=f"Social Media - {brief.project_name}",
            content=content,
            metadata={"platforms": platforms},
            tone=brief.tone,
            target_audience=brief.target_audience,
            keywords=brief.keywords
        )
        
        self.generated_content[content_id] = result
        return result
    
    async def generate_full_marketing_package(self, brief: ContentBrief) -> Dict[str, MarketingContent]:
        """Generate complete marketing package"""
        logger.info(f"[MARKETING] Generating full package for: {brief.project_name}")
        
        results = {}
        
        # Generate all content types
        results["landing_page"] = await self.generate_landing_page(brief)
        results["product_description"] = await self.generate_product_description(brief)
        results["email_sequence"] = await self.generate_email_sequence(brief)
        results["social_media"] = await self.generate_social_media(brief)
        
        logger.info(f"[MARKETING] Full package generated: {len(results)} pieces")
        return results
    
    # Fallback methods for when API is unavailable
    def _fallback_landing_page(self, brief: ContentBrief) -> str:
        return json.dumps({
            "headline": f"Introducing {brief.project_name}",
            "subheadline": brief.unique_value_proposition,
            "hero_cta": brief.call_to_action or "Get Started Today",
            "benefits": [{"title": f, "description": f"Experience the power of {f.lower()}"} for f in brief.key_features[:3]],
            "features": [{"title": f, "description": f"Built with {f.lower()} in mind"} for f in brief.key_features],
            "testimonial_placeholder": "See what our customers are saying...",
            "final_cta": "Start Your Journey",
            "footer_tagline": f"{brief.project_name} - {brief.unique_value_proposition}"
        }, indent=2)
    
    def _fallback_product_description(self, brief: ContentBrief) -> str:
        return json.dumps({
            "short_description": f"{brief.project_name}: {brief.unique_value_proposition}",
            "long_description": f"{brief.project_description}\n\nBuilt for {brief.target_audience}, {brief.project_name} delivers {', '.join(brief.key_features[:3])}.",
            "tagline": brief.unique_value_proposition,
            "key_benefits": brief.key_features,
            "technical_specs": ["Enterprise-grade security", "99.9% uptime SLA", "24/7 support"],
            "ideal_for": brief.target_audience
        }, indent=2)
    
    def _fallback_email_sequence(self, brief: ContentBrief, num_emails: int) -> str:
        emails = []
        subjects = [
            f"Discover {brief.project_name}",
            f"How {brief.project_name} solves your biggest challenge",
            f"See {brief.project_name} in action",
            f"What others are saying about {brief.project_name}",
            f"Limited time offer for {brief.project_name}"
        ]
        
        for i in range(min(num_emails, len(subjects))):
            emails.append({
                "email_number": i + 1,
                "subject_line": subjects[i],
                "preview_text": f"Learn how {brief.project_name} can help you...",
                "body": f"Hi there,\n\n{brief.unique_value_proposition}\n\nBest,\nThe Team",
                "cta": brief.call_to_action or "Learn More",
                "send_day": i * 2
            })
        
        return json.dumps(emails, indent=2)
    
    def _fallback_social_media(self, brief: ContentBrief, platforms: List[str]) -> str:
        content = {}
        for platform in platforms:
            if platform == "twitter":
                content[platform] = [
                    {"post": f"🚀 Introducing {brief.project_name}! {brief.unique_value_proposition}", "hashtags": brief.keywords[:3]}
                ]
            elif platform == "linkedin":
                content[platform] = [
                    {"post": f"Excited to announce {brief.project_name}.\n\n{brief.project_description}\n\n{brief.call_to_action}", "hashtags": brief.keywords[:5]}
                ]
            else:
                content[platform] = [
                    {"post": f"Check out {brief.project_name}! {brief.unique_value_proposition}", "hashtags": brief.keywords[:5]}
                ]
        
        return json.dumps(content, indent=2)
    
    def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get generated content by ID"""
        content = self.generated_content.get(content_id)
        return content.to_dict() if content else None
    
    def list_content(self) -> List[Dict[str, Any]]:
        """List all generated content"""
        return [c.to_dict() for c in self.generated_content.values()]
    
    def get_status(self) -> Dict[str, Any]:
        """Get generator status"""
        return {
            "configured": self.is_configured(),
            "model": self.model,
            "total_generated": len(self.generated_content),
            "content_types": {
                ct.value: len([c for c in self.generated_content.values() if c.content_type == ct])
                for ct in ContentType
            }
        }


# Global instance
marketing_generator = MarketingGenerator()
