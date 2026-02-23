"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      PROMPT OPTIMIZATION ENGINE                               ║
║                                                                              ║
║  AI-powered prompt refinement for maximum specification clarity.              ║
║  Transforms vague requirements into precise, actionable specifications.       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class OptimizedPrompt:
    """Result of prompt optimization"""
    original: str
    optimized: str
    enhancements: List[str]
    extracted_entities: List[str]
    extracted_actions: List[str]
    suggested_tech_stack: Dict[str, str]
    complexity_score: int  # 1-10
    estimated_components: List[str]
    warnings: List[str]


OPTIMIZATION_SYSTEM_PROMPT = """You are a Prompt Optimization Engine for a software factory platform. Your job is to take vague, incomplete user requirements and transform them into comprehensive, precise specifications.

RULES:
1. NEVER remove user intent - only enhance and clarify
2. Add explicit technical requirements that are implied
3. Identify all entities (nouns) and actions (verbs)
4. Suggest appropriate technology choices
5. Flag potential ambiguities that need user input
6. Estimate complexity (1-10 scale)

Given a user prompt, return a JSON response with:
{
  "optimized_prompt": "The enhanced, detailed version of the requirement",
  "enhancements": ["List of specific additions/clarifications made"],
  "extracted_entities": ["User", "Task", "Project", etc.],
  "extracted_actions": ["create", "update", "delete", "authenticate", etc.],
  "suggested_tech_stack": {
    "frontend": "nextjs or react",
    "backend": "fastapi or express",
    "database": "postgresql or mongodb",
    "auth": "jwt or oauth",
    "deployment": "vercel or railway"
  },
  "complexity_score": 1-10,
  "estimated_components": ["Auth Module", "Dashboard", "API Layer", etc.],
  "warnings": ["Any concerns or clarifications needed"],
  "data_model": {
    "entities": [
      {"name": "EntityName", "attributes": [{"name": "field", "type": "string"}], "relationships": []}
    ]
  },
  "api_contracts": [
    {"endpoint": "/api/resource", "method": "GET", "description": "..."},
    {"endpoint": "/api/resource", "method": "POST", "description": "..."}
  ]
}

Be thorough. A simple "todo app" should become a full specification with user auth, CRUD operations, data persistence, error handling, and deployment considerations."""


MARKETING_SYSTEM_PROMPT = """You are a Marketing Content Generator for software products. Generate compelling, professional marketing copy.

Given a product specification, create:
{
  "tagline": "A punchy 5-10 word tagline",
  "headline": "Main marketing headline (max 15 words)",
  "subheadline": "Supporting headline explaining value prop",
  "description": "2-3 paragraph product description",
  "features": [
    {"title": "Feature Name", "description": "Brief description", "icon": "suggested-icon-name"}
  ],
  "benefits": ["Benefit 1", "Benefit 2", "Benefit 3"],
  "cta_primary": "Primary call-to-action text",
  "cta_secondary": "Secondary CTA text",
  "seo_title": "SEO optimized page title",
  "seo_description": "Meta description for SEO",
  "social_proof_suggestions": ["Type of testimonial/proof to add"],
  "landing_page_sections": [
    {"section": "hero", "content": "..."},
    {"section": "features", "content": "..."},
    {"section": "pricing", "content": "..."},
    {"section": "faq", "content": "..."}
  ]
}

Be creative but professional. Focus on user benefits, not just features."""


class PromptOptimizer:
    """
    Transforms vague prompts into comprehensive specifications.
    Uses pattern matching + LLM enhancement.
    """
    
    # Common patterns to detect and expand
    EXPANSION_PATTERNS = {
        r'\b(app|application)\b': [
            'web application with responsive design',
            'user authentication system',
            'data persistence layer',
            'API backend'
        ],
        r'\b(todo|task)\b': [
            'task creation with title and description',
            'task status tracking (pending/in-progress/completed)',
            'due dates and reminders',
            'task categorization/tagging',
            'task assignment (if multi-user)'
        ],
        r'\b(user|account)\b': [
            'user registration with email verification',
            'secure login with password hashing',
            'password reset functionality',
            'user profile management',
            'session management'
        ],
        r'\b(dashboard)\b': [
            'analytics overview widgets',
            'recent activity feed',
            'quick action buttons',
            'data visualization charts',
            'customizable layout'
        ],
        r'\b(e-?commerce|shop|store)\b': [
            'product catalog with categories',
            'shopping cart functionality',
            'checkout process',
            'payment integration (Stripe)',
            'order management',
            'inventory tracking'
        ],
        r'\b(blog|cms)\b': [
            'rich text editor for content',
            'post categorization and tagging',
            'SEO optimization fields',
            'media upload and management',
            'comment system',
            'draft/publish workflow'
        ],
        r'\b(chat|messaging)\b': [
            'real-time messaging (WebSocket)',
            'conversation threads',
            'message history',
            'typing indicators',
            'read receipts',
            'file/image sharing'
        ],
        r'\b(booking|reservation|appointment)\b': [
            'calendar view for availability',
            'time slot selection',
            'booking confirmation emails',
            'cancellation/rescheduling',
            'reminder notifications'
        ]
    }
    
    # Tech stack suggestions based on keywords
    TECH_SUGGESTIONS = {
        'real-time|chat|live': {'backend': 'fastapi', 'extra': 'websockets'},
        'e-commerce|payment': {'payment': 'stripe', 'database': 'postgresql'},
        'blog|cms|content': {'frontend': 'nextjs', 'database': 'postgresql'},
        'mobile|native': {'frontend': 'react-native', 'backend': 'fastapi'},
        'api|microservice': {'backend': 'fastapi', 'database': 'postgresql'},
        'simple|basic|mvp': {'frontend': 'react', 'backend': 'fastapi', 'database': 'sqlite'},
        'enterprise|scale': {'backend': 'fastapi', 'database': 'postgresql', 'cache': 'redis', 'deployment': 'kubernetes'}
    }
    
    def __init__(self):
        self.default_tech_stack = {
            'frontend': 'nextjs',
            'backend': 'fastapi',
            'database': 'postgresql',
            'css': 'tailwindcss',
            'auth': 'jwt',
            'deployment': 'vercel'
        }
    
    def quick_optimize(self, prompt: str) -> Dict[str, Any]:
        """
        Quick optimization using pattern matching (no LLM).
        Good for instant feedback before full LLM analysis.
        """
        prompt_lower = prompt.lower()
        
        # Extract entities (capitalized words and nouns)
        entities = self._extract_entities(prompt)
        
        # Extract actions (verbs)
        actions = self._extract_actions(prompt)
        
        # Find expansions
        enhancements = []
        for pattern, expansions in self.EXPANSION_PATTERNS.items():
            if re.search(pattern, prompt_lower):
                enhancements.extend(expansions)
        
        # Remove duplicates while preserving order
        enhancements = list(dict.fromkeys(enhancements))
        
        # Suggest tech stack
        tech_stack = self.default_tech_stack.copy()
        for pattern, suggestions in self.TECH_SUGGESTIONS.items():
            if re.search(pattern, prompt_lower):
                tech_stack.update(suggestions)
        
        # Estimate complexity
        complexity = self._estimate_complexity(prompt, enhancements)
        
        # Build optimized prompt
        optimized = self._build_optimized_prompt(prompt, enhancements, entities, actions)
        
        # Estimate components
        components = self._estimate_components(prompt_lower, entities)
        
        return {
            'original': prompt,
            'optimized': optimized,
            'enhancements': enhancements[:10],  # Top 10
            'extracted_entities': entities,
            'extracted_actions': actions,
            'suggested_tech_stack': tech_stack,
            'complexity_score': complexity,
            'estimated_components': components,
            'warnings': self._generate_warnings(prompt_lower)
        }
    
    def _extract_entities(self, prompt: str) -> List[str]:
        """Extract potential entities from prompt"""
        # Common entity words
        entity_patterns = [
            r'\b(user|admin|customer|client|member)\b',
            r'\b(task|todo|item|project|job)\b',
            r'\b(product|order|cart|payment)\b',
            r'\b(post|article|comment|message)\b',
            r'\b(booking|appointment|reservation)\b',
            r'\b(file|document|image|media)\b',
            r'\b(notification|alert|reminder)\b',
            r'\b(category|tag|label)\b',
            r'\b(dashboard|report|analytics)\b',
            r'\b(settings|profile|preferences)\b'
        ]
        
        entities = []
        prompt_lower = prompt.lower()
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, prompt_lower)
            entities.extend([m.capitalize() for m in matches])
        
        # Add capitalized words as potential entities
        cap_words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        entities.extend(cap_words)
        
        return list(dict.fromkeys(entities))  # Remove duplicates
    
    def _extract_actions(self, prompt: str) -> List[str]:
        """Extract actions/operations from prompt"""
        action_patterns = [
            r'\b(create|add|make|build|generate)\b',
            r'\b(read|view|show|display|list|get)\b',
            r'\b(update|edit|modify|change)\b',
            r'\b(delete|remove|cancel)\b',
            r'\b(login|logout|register|signup|authenticate)\b',
            r'\b(search|filter|sort|find)\b',
            r'\b(upload|download|import|export)\b',
            r'\b(send|receive|notify|share)\b',
            r'\b(book|reserve|schedule)\b',
            r'\b(pay|checkout|purchase|subscribe)\b'
        ]
        
        actions = []
        prompt_lower = prompt.lower()
        
        for pattern in action_patterns:
            matches = re.findall(pattern, prompt_lower)
            actions.extend(matches)
        
        # Default CRUD if entities found but no actions
        if not actions and self._extract_entities(prompt):
            actions = ['create', 'read', 'update', 'delete']
        
        return list(dict.fromkeys(actions))
    
    def _estimate_complexity(self, prompt: str, enhancements: List[str]) -> int:
        """Estimate project complexity 1-10"""
        score = 3  # Base score
        
        prompt_lower = prompt.lower()
        
        # Complexity factors
        if re.search(r'real-?time|websocket|live', prompt_lower):
            score += 2
        if re.search(r'payment|stripe|checkout', prompt_lower):
            score += 2
        if re.search(r'auth|login|user', prompt_lower):
            score += 1
        if re.search(r'api|integration|external', prompt_lower):
            score += 1
        if re.search(r'analytics|dashboard|report', prompt_lower):
            score += 1
        if re.search(r'mobile|responsive|native', prompt_lower):
            score += 1
        if re.search(r'enterprise|scale|performance', prompt_lower):
            score += 2
        
        # Enhancement count affects complexity
        score += min(len(enhancements) // 3, 2)
        
        return min(score, 10)
    
    def _build_optimized_prompt(self, original: str, enhancements: List[str], 
                                entities: List[str], actions: List[str]) -> str:
        """Build an optimized, detailed prompt"""
        parts = [original.strip()]
        
        if enhancements:
            parts.append("\n\nRequired Features:")
            for i, enh in enumerate(enhancements[:8], 1):
                parts.append(f"  {i}. {enh}")
        
        if entities:
            parts.append(f"\n\nCore Entities: {', '.join(entities)}")
        
        if actions:
            parts.append(f"Operations: {', '.join(actions)}")
        
        parts.append("\n\nTechnical Requirements:")
        parts.append("  - RESTful API architecture")
        parts.append("  - Secure authentication")
        parts.append("  - Input validation and error handling")
        parts.append("  - Responsive UI design")
        parts.append("  - Database persistence")
        
        return '\n'.join(parts)
    
    def _estimate_components(self, prompt_lower: str, entities: List[str]) -> List[str]:
        """Estimate required components"""
        components = ['API Layer', 'Database Schema']
        
        if re.search(r'user|auth|login', prompt_lower):
            components.extend(['Auth Module', 'User Management'])
        
        if re.search(r'dashboard|analytics', prompt_lower):
            components.append('Dashboard')
        
        if re.search(r'admin', prompt_lower):
            components.append('Admin Panel')
        
        # Add entity-based components
        for entity in entities[:5]:
            components.append(f'{entity} Management')
        
        if re.search(r'notification|email|alert', prompt_lower):
            components.append('Notification System')
        
        if re.search(r'file|upload|media', prompt_lower):
            components.append('File Management')
        
        if re.search(r'search|filter', prompt_lower):
            components.append('Search & Filtering')
        
        return list(dict.fromkeys(components))
    
    def _generate_warnings(self, prompt_lower: str) -> List[str]:
        """Generate warnings for potential issues"""
        warnings = []
        
        if len(prompt_lower.split()) < 5:
            warnings.append("Prompt is very short. Consider adding more details.")
        
        if not re.search(r'user|auth|login', prompt_lower):
            warnings.append("No authentication mentioned. Consider if user accounts are needed.")
        
        if re.search(r'payment|money|subscription', prompt_lower):
            warnings.append("Payment functionality requires PCI compliance considerations.")
        
        if re.search(r'health|medical|patient', prompt_lower):
            warnings.append("Healthcare data may require HIPAA compliance.")
        
        if re.search(r'user data|personal|gdpr', prompt_lower):
            warnings.append("Personal data handling may require GDPR compliance.")
        
        if not re.search(r'mobile|responsive|desktop', prompt_lower):
            warnings.append("Platform not specified. Defaulting to responsive web.")
        
        return warnings
    
    def get_system_prompt(self) -> str:
        """Get the LLM system prompt for full optimization"""
        return OPTIMIZATION_SYSTEM_PROMPT
    
    def get_marketing_prompt(self) -> str:
        """Get the LLM system prompt for marketing content"""
        return MARKETING_SYSTEM_PROMPT


# Singleton instance
prompt_optimizer = PromptOptimizer()
