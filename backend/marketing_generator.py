"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      MARKETING CONTENT GENERATOR                              ║
║                                                                              ║
║  AI-powered marketing copy, landing pages, and promotional content.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json


@dataclass
class MarketingContent:
    """Generated marketing content package"""
    id: str
    project_name: str
    tagline: str
    headline: str
    subheadline: str
    description: str
    features: List[Dict[str, str]]
    benefits: List[str]
    cta_primary: str
    cta_secondary: str
    seo_title: str
    seo_description: str
    landing_page_html: str
    social_posts: Dict[str, str]
    email_templates: Dict[str, str]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


MARKETING_SYSTEM_PROMPT = """You are an expert marketing copywriter for software products. Generate compelling, conversion-focused content.

Given a product specification, create marketing content in this JSON format:
{
  "tagline": "Punchy 5-10 word tagline",
  "headline": "Main headline (max 12 words)",
  "subheadline": "Supporting value proposition",
  "description": "2-3 paragraph product description focusing on benefits",
  "features": [
    {"title": "Feature Name", "description": "Benefit-focused description", "icon": "icon-name"}
  ],
  "benefits": ["User benefit 1", "User benefit 2", "User benefit 3"],
  "cta_primary": "Primary CTA text (action-oriented)",
  "cta_secondary": "Secondary CTA text",
  "seo_title": "SEO-optimized page title (50-60 chars)",
  "seo_description": "Meta description (150-160 chars)",
  "social_posts": {
    "twitter": "Tweet text (max 280 chars)",
    "linkedin": "LinkedIn post",
    "product_hunt": "Product Hunt tagline"
  },
  "faq": [
    {"question": "Common question", "answer": "Clear answer"}
  ],
  "testimonial_templates": [
    "Template for user testimonial focusing on [benefit]"
  ]
}

Guidelines:
- Focus on USER BENEFITS, not features
- Use action verbs in CTAs
- Keep headlines punchy and scannable
- Include social proof elements
- Optimize for conversions"""


class MarketingGenerator:
    """Generates marketing content for software products"""
    
    def __init__(self):
        self.templates = {}
    
    def generate_landing_page_html(self, content: Dict[str, Any], 
                                   project_name: str,
                                   tech_stack: Dict[str, str] = None) -> str:
        """Generate a complete landing page HTML"""
        
        features_html = ""
        for feature in content.get('features', [])[:6]:
            features_html += f'''
            <div class="feature-card">
                <div class="feature-icon">
                    <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                </div>
                <h3 class="feature-title">{feature.get('title', 'Feature')}</h3>
                <p class="feature-desc">{feature.get('description', '')}</p>
            </div>'''
        
        benefits_html = ""
        for benefit in content.get('benefits', [])[:5]:
            benefits_html += f'<li class="benefit-item">✓ {benefit}</li>'
        
        faq_html = ""
        for faq in content.get('faq', [])[:5]:
            faq_html += f'''
            <div class="faq-item">
                <h4 class="faq-question">{faq.get('question', '')}</h4>
                <p class="faq-answer">{faq.get('answer', '')}</p>
            </div>'''
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.get('seo_title', project_name)}</title>
    <meta name="description" content="{content.get('seo_description', '')}">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --bg-dark: #0a0a0a;
            --bg-card: #18181b;
            --text-primary: #fafafa;
            --text-secondary: #a1a1aa;
        }}
        body {{
            background: var(--bg-dark);
            color: var(--text-primary);
            font-family: 'Inter', system-ui, sans-serif;
        }}
        .gradient-text {{
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);
        }}
        .feature-card {{
            background: var(--bg-card);
            border: 1px solid #27272a;
            border-radius: 12px;
            padding: 24px;
            transition: border-color 0.2s;
        }}
        .feature-card:hover {{
            border-color: var(--primary);
        }}
        .feature-icon {{
            width: 48px;
            height: 48px;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            margin-bottom: 16px;
        }}
        .feature-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .feature-desc {{
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.6;
        }}
        .benefit-item {{
            padding: 8px 0;
            color: var(--text-secondary);
        }}
        .faq-item {{
            border-bottom: 1px solid #27272a;
            padding: 20px 0;
        }}
        .faq-question {{
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .faq-answer {{
            color: var(--text-secondary);
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="min-h-screen flex items-center justify-center px-6 py-20">
        <div class="max-w-4xl mx-auto text-center">
            <p class="text-indigo-400 font-mono text-sm tracking-wider mb-4 uppercase">{content.get('tagline', 'Welcome')}</p>
            <h1 class="text-5xl md:text-7xl font-bold mb-6 gradient-text">{content.get('headline', project_name)}</h1>
            <p class="text-xl md:text-2xl text-zinc-400 mb-10 max-w-2xl mx-auto">{content.get('subheadline', '')}</p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <a href="#" class="btn-primary px-8 py-4 rounded-lg font-semibold text-white">{content.get('cta_primary', 'Get Started')}</a>
                <a href="#features" class="px-8 py-4 rounded-lg font-semibold border border-zinc-700 hover:border-zinc-500 transition-colors">{content.get('cta_secondary', 'Learn More')}</a>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20 px-6">
        <div class="max-w-6xl mx-auto">
            <h2 class="text-3xl md:text-4xl font-bold text-center mb-4">Powerful Features</h2>
            <p class="text-zinc-400 text-center mb-12 max-w-2xl mx-auto">Everything you need to succeed</p>
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {features_html}
            </div>
        </div>
    </section>

    <!-- Benefits Section -->
    <section class="py-20 px-6 bg-zinc-900/50">
        <div class="max-w-4xl mx-auto">
            <h2 class="text-3xl md:text-4xl font-bold text-center mb-12">Why Choose {project_name}?</h2>
            <div class="grid md:grid-cols-2 gap-8">
                <div>
                    <p class="text-lg text-zinc-300 leading-relaxed">{content.get('description', '')}</p>
                </div>
                <div>
                    <ul class="space-y-2">
                        {benefits_html}
                    </ul>
                </div>
            </div>
        </div>
    </section>

    <!-- FAQ Section -->
    <section class="py-20 px-6">
        <div class="max-w-3xl mx-auto">
            <h2 class="text-3xl md:text-4xl font-bold text-center mb-12">Frequently Asked Questions</h2>
            {faq_html}
        </div>
    </section>

    <!-- CTA Section -->
    <section class="py-20 px-6">
        <div class="max-w-4xl mx-auto text-center">
            <h2 class="text-3xl md:text-4xl font-bold mb-6">Ready to Get Started?</h2>
            <p class="text-zinc-400 mb-8">Join thousands of users already using {project_name}</p>
            <a href="#" class="btn-primary px-10 py-4 rounded-lg font-semibold text-white inline-block">{content.get('cta_primary', 'Start Free Trial')}</a>
        </div>
    </section>

    <!-- Footer -->
    <footer class="py-10 px-6 border-t border-zinc-800">
        <div class="max-w-6xl mx-auto text-center text-zinc-500">
            <p>© 2026 {project_name}. Generated by Sovereign Genesis Platform.</p>
        </div>
    </footer>
</body>
</html>'''
    
    def generate_email_templates(self, content: Dict[str, Any], project_name: str) -> Dict[str, str]:
        """Generate email templates for different purposes"""
        
        welcome_email = f'''Subject: Welcome to {project_name}! 🎉

Hi {{{{name}}}},

Welcome to {project_name}! We're thrilled to have you on board.

{content.get('description', 'Thank you for joining us.')[:200]}

Here's what you can do next:
• Set up your profile
• Explore the dashboard
• Check out our getting started guide

If you have any questions, just reply to this email - we're here to help!

Best,
The {project_name} Team

---
{content.get('tagline', '')}
'''

        launch_email = f'''Subject: Introducing {project_name} - {content.get('tagline', 'Something Amazing')}

Hi {{{{name}}}},

We're excited to announce the launch of {project_name}!

**{content.get('headline', '')}**

{content.get('description', '')}

Key Features:
'''
        for feature in content.get('features', [])[:3]:
            launch_email += f"• {feature.get('title', '')}: {feature.get('description', '')}\n"
        
        launch_email += f'''
Ready to try it? Click here to get started: [CTA LINK]

{content.get('cta_primary', 'Get Started Now')} →

Best,
The {project_name} Team
'''

        return {
            'welcome': welcome_email,
            'launch_announcement': launch_email,
            'subject_lines': [
                f"Welcome to {project_name}! 🎉",
                f"Your {project_name} account is ready",
                f"Get started with {project_name}",
                f"[Action Required] Complete your {project_name} setup"
            ]
        }
    
    def generate_social_posts(self, content: Dict[str, Any], project_name: str) -> Dict[str, str]:
        """Generate social media posts"""
        
        twitter = f"🚀 Introducing {project_name}!\n\n{content.get('tagline', '')}\n\n{content.get('subheadline', '')[:100]}\n\nTry it now → [LINK]\n\n#buildinpublic #saas #startup"
        
        linkedin = f'''🎉 Excited to announce the launch of {project_name}!

{content.get('headline', '')}

{content.get('description', '')[:300]}

Key highlights:
'''
        for benefit in content.get('benefits', [])[:3]:
            linkedin += f"✅ {benefit}\n"
        
        linkedin += f"\nCheck it out: [LINK]\n\n#productlaunch #technology #innovation"
        
        product_hunt = f"{content.get('tagline', project_name)} - {content.get('subheadline', '')[:80]}"
        
        return {
            'twitter': twitter[:280],
            'linkedin': linkedin,
            'product_hunt_tagline': product_hunt[:60],
            'instagram_caption': f"✨ {content.get('headline', '')}\n\n{content.get('description', '')[:150]}...\n\nLink in bio! 👆\n\n#launch #tech #productivity"
        }
    
    def get_system_prompt(self) -> str:
        """Get the LLM system prompt for content generation"""
        return MARKETING_SYSTEM_PROMPT


# Singleton
marketing_generator = MarketingGenerator()
