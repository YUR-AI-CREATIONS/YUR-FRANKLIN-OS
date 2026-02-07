"""
Agent Marketplace - Elite AI Agent Profiles
Pre-configured AI agents with performance metrics, pricing, and specializations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for an agent"""
    client_satisfaction: float = 4.5
    task_completion_rate: float = 95.0
    avg_response_time: float = 2.0
    problem_resolution_rate: float = 90.0
    client_retention_rate: float = 90.0
    annual_projects: int = 100
    error_rate: float = 2.0
    uptime_sla: float = 99.9
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_satisfaction": f"{self.client_satisfaction}/5.0",
            "task_completion_rate": f"{self.task_completion_rate}%",
            "avg_response_time": f"{self.avg_response_time}s",
            "problem_resolution_rate": f"{self.problem_resolution_rate}%",
            "client_retention_rate": f"{self.client_retention_rate}%",
            "annual_projects": f"{self.annual_projects}+",
            "error_rate": f"{self.error_rate}%",
            "uptime_sla": f"{self.uptime_sla}%"
        }


@dataclass
class PricingTier:
    """Pricing tier for an agent"""
    name: str
    monthly: float
    annual: float
    cost_per_task: float
    features: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "monthly": f"${self.monthly:,.0f}",
            "annual": f"${self.annual:,.0f}",
            "cost_per_task": f"${self.cost_per_task:.0f}",
            "features": self.features
        }


@dataclass
class SuccessStory:
    """Success story for an agent"""
    title: str
    client: str
    challenge: str
    solution: str
    results: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "client": self.client,
            "challenge": self.challenge,
            "solution": self.solution,
            "results": self.results
        }


@dataclass
class Testimonial:
    """Testimonial for an agent"""
    quote: str
    author: str
    title: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "quote": self.quote,
            "author": self.author,
            "title": self.title
        }


@dataclass
class EliteAgent:
    """Elite AI Agent profile"""
    agent_id: str
    name: str
    primary_specialization: str
    secondary_specialization: str
    tertiary_specialization: str
    advanced_skills: List[str]
    metrics: PerformanceMetrics
    pricing: List[PricingTier]
    use_cases: List[str]
    success_stories: List[SuccessStory]
    testimonials: List[Testimonial]
    strong_points: List[str]
    multilingual_names: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specializations": {
                "primary": self.primary_specialization,
                "secondary": self.secondary_specialization,
                "tertiary": self.tertiary_specialization
            },
            "advanced_skills": self.advanced_skills,
            "metrics": self.metrics.to_dict(),
            "pricing": [p.to_dict() for p in self.pricing],
            "use_cases": self.use_cases,
            "success_stories": [s.to_dict() for s in self.success_stories],
            "testimonials": [t.to_dict() for t in self.testimonials],
            "strong_points": self.strong_points,
            "multilingual_names": self.multilingual_names
        }
    
    def to_summary(self) -> Dict[str, Any]:
        """Get a summary view of the agent"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "primary_specialization": self.primary_specialization,
            "client_satisfaction": self.metrics.client_satisfaction,
            "task_completion_rate": self.metrics.task_completion_rate,
            "starter_price": self.pricing[0].monthly if self.pricing else 0
        }


# Pre-configured Elite Agents
ELITE_AGENTS = [
    EliteAgent(
        agent_id="agent_marcus_thompson",
        name="Marcus Thompson",
        primary_specialization="Enterprise Sales & Business Development",
        secondary_specialization="Market Analysis & Strategy Consulting",
        tertiary_specialization="Client Relationship Management",
        advanced_skills=[
            "Complex deal negotiation",
            "Multi-stakeholder coordination",
            "Revenue optimization",
            "Territory expansion strategies",
            "Enterprise account management"
        ],
        metrics=PerformanceMetrics(
            client_satisfaction=4.9,
            task_completion_rate=98.7,
            avg_response_time=1.2,
            problem_resolution_rate=96.3,
            client_retention_rate=94.5,
            annual_projects=250,
            error_rate=0.8,
            uptime_sla=99.95
        ),
        pricing=[
            PricingTier("Starter", 499, 4990, 50, "Up to 10 tasks/week"),
            PricingTier("Professional", 1299, 12990, 30, "Up to 50 tasks/week"),
            PricingTier("Enterprise", 0, 0, 17.5, "Unlimited tasks, 24/7 support")
        ],
        use_cases=[
            "B2B Sales Strategy",
            "Account Management",
            "Pipeline Development",
            "Negotiation Support",
            "Market Expansion",
            "Partnership Development",
            "Revenue Optimization"
        ],
        success_stories=[
            SuccessStory(
                "Fortune 500 Enterprise Transformation",
                "Global Technology Company",
                "Stagnant sales growth and market penetration issues",
                "Implemented comprehensive sales reorganization strategy",
                ["Revenue increased by 156% in 18 months", "Sales cycle reduced from 6 to 3 months", "$12.5M additional annual revenue"]
            )
        ],
        testimonials=[
            Testimonial(
                "Marcus transformed our entire sales organization. The 156% revenue increase speaks for itself.",
                "Jennifer Martinez",
                "VP Sales"
            )
        ],
        strong_points=[
            "Deep Enterprise Expertise",
            "Strategic Thinking",
            "Relationship Building",
            "Data-Driven Approach",
            "Communication Excellence"
        ],
        multilingual_names={
            "English": "Marcus Thompson",
            "Mandarin": "马库斯·汤普森",
            "Japanese": "マーカス・トンプソン",
            "Arabic": "ماركوس طومسون"
        }
    ),
    EliteAgent(
        agent_id="agent_sarah_chen",
        name="Sarah Chen",
        primary_specialization="Product Management & UX/UI Design",
        secondary_specialization="Agile Development Methodologies",
        tertiary_specialization="User Research & Analytics",
        advanced_skills=[
            "Product roadmap development",
            "Design thinking and innovation",
            "User experience optimization",
            "Feature prioritization frameworks",
            "Cross-functional team leadership"
        ],
        metrics=PerformanceMetrics(
            client_satisfaction=4.8,
            task_completion_rate=97.4,
            avg_response_time=0.8,
            problem_resolution_rate=98.1,
            client_retention_rate=96.2,
            annual_projects=180,
            error_rate=0.5,
            uptime_sla=99.98
        ),
        pricing=[
            PricingTier("Starter", 599, 5990, 60, "Up to 8 tasks/week"),
            PricingTier("Professional", 1499, 14990, 35, "Up to 40 tasks/week"),
            PricingTier("Enterprise", 0, 0, 22.5, "Unlimited tasks, priority support")
        ],
        use_cases=[
            "Product Launch Planning",
            "UX/UI Optimization",
            "Feature Prioritization",
            "User Research",
            "Analytics Implementation",
            "Agile Transformation",
            "MVP Development"
        ],
        success_stories=[
            SuccessStory(
                "Mobile App Redesign & Growth",
                "Fintech Mobile Application",
                "Declining user engagement and poor app store ratings",
                "Led complete UX/UI redesign with user research",
                ["App store rating improved to 4.6 stars", "Daily active users increased by 240%", "Top 10 in Finance category"]
            )
        ],
        testimonials=[
            Testimonial(
                "Sarah's UX expertise transformed our app from a 2-star to 4.6 stars. Our users actually love using our product now.",
                "David Kumar",
                "Head of Product"
            )
        ],
        strong_points=[
            "User-Centric Mindset",
            "Data-Driven Decisions",
            "Technical Understanding",
            "Creative Problem-Solving",
            "Analytical Rigor"
        ],
        multilingual_names={
            "English": "Sarah Chen",
            "Mandarin": "莎拉·陈",
            "Japanese": "サラ・チェン",
            "Arabic": "سارة تشين"
        }
    ),
    EliteAgent(
        agent_id="agent_dr_marcus_chen",
        name="Dr. Marcus Chen",
        primary_specialization="AI/ML & Data Science Strategy",
        secondary_specialization="Research & Development Leadership",
        tertiary_specialization="Technical Due Diligence & Innovation",
        advanced_skills=[
            "Machine learning architecture",
            "Big data infrastructure",
            "AI ethics and governance",
            "Research team leadership",
            "Technology assessment and evaluation"
        ],
        metrics=PerformanceMetrics(
            client_satisfaction=4.95,
            task_completion_rate=99.2,
            avg_response_time=1.5,
            problem_resolution_rate=99.1,
            client_retention_rate=98.7,
            annual_projects=120,
            error_rate=0.2,
            uptime_sla=99.99
        ),
        pricing=[
            PricingTier("Starter", 1999, 19990, 150, "Up to 4 tasks/week"),
            PricingTier("Professional", 3999, 39990, 100, "Up to 10 tasks/week"),
            PricingTier("Enterprise", 0, 0, 87.5, "Unlimited, 24/7 support")
        ],
        use_cases=[
            "AI/ML Strategy Development",
            "Technical Due Diligence",
            "Research Team Building",
            "Machine Learning Implementation",
            "Data Infrastructure Design",
            "Regulatory Compliance",
            "Innovation Assessment"
        ],
        success_stories=[
            SuccessStory(
                "AI-Powered Enterprise Transformation",
                "Fortune 100 Financial Services",
                "Digital transformation requiring major AI investments without clear ROI",
                "Developed comprehensive AI strategy and led implementation roadmap",
                ["Identified 25 high-ROI AI use cases worth $450M", "320% ROI on AI investments within 2 years"]
            )
        ],
        testimonials=[
            Testimonial(
                "Dr. Chen's AI strategy transformed our organization. His ability to identify high-value use cases was invaluable.",
                "Patricia O'Neill",
                "Chief Digital Officer"
            )
        ],
        strong_points=[
            "PhD-Level Expertise",
            "Practical Experience",
            "Strategic Vision",
            "Research Leadership",
            "Ethics & Governance"
        ],
        multilingual_names={
            "English": "Dr. Marcus Chen",
            "Mandarin": "陈博士",
            "Japanese": "チェン博士",
            "Arabic": "الدكتور تشين"
        }
    ),
    EliteAgent(
        agent_id="agent_jennifer_williams",
        name="Jennifer Williams",
        primary_specialization="Marketing & Brand Strategy",
        secondary_specialization="Digital Marketing & Growth",
        tertiary_specialization="Content Strategy & Communications",
        advanced_skills=[
            "Brand positioning and development",
            "Multi-channel marketing strategy",
            "Marketing analytics and attribution",
            "Campaign development and execution",
            "Thought leadership programs"
        ],
        metrics=PerformanceMetrics(
            client_satisfaction=4.85,
            task_completion_rate=98.1,
            avg_response_time=2.1,
            problem_resolution_rate=97.5,
            client_retention_rate=95.8,
            annual_projects=200,
            error_rate=0.6,
            uptime_sla=99.96
        ),
        pricing=[
            PricingTier("Starter", 699, 6990, 70, "Up to 12 tasks/week"),
            PricingTier("Professional", 1699, 16990, 40, "Up to 45 tasks/week"),
            PricingTier("Enterprise", 0, 0, 27.5, "Unlimited, priority access")
        ],
        use_cases=[
            "Brand Repositioning",
            "Growth Marketing",
            "Content Strategy",
            "Campaign Management",
            "Marketing Analytics",
            "Lead Generation",
            "Customer Advocacy"
        ],
        success_stories=[
            SuccessStory(
                "B2B SaaS Brand Transformation",
                "Enterprise Software Company",
                "Brand perceived as low-cost commodity rather than premium solution",
                "Led complete brand repositioning and integrated marketing strategy",
                ["Premium positioning enabled 34% price increase", "Brand awareness increased from 12% to 67%", "$18M annual revenue increase"]
            )
        ],
        testimonials=[
            Testimonial(
                "Jennifer's brand repositioning strategy was transformative. She helped us redefine how the market sees us.",
                "Thomas Bennett",
                "CEO"
            )
        ],
        strong_points=[
            "Strategic Marketing Thinking",
            "Creative Excellence",
            "Data-Driven Approach",
            "Multi-channel Expertise",
            "Market Understanding"
        ],
        multilingual_names={
            "English": "Jennifer Williams",
            "Mandarin": "詹妮弗·威廉斯",
            "Japanese": "ジェニファー・ウィリアムス",
            "Arabic": "جنيفر ويليامز"
        }
    ),
    EliteAgent(
        agent_id="agent_david_rodriguez",
        name="David Rodriguez",
        primary_specialization="Operations & Supply Chain Management",
        secondary_specialization="Business Process Optimization",
        tertiary_specialization="Organizational Efficiency & Cost Reduction",
        advanced_skills=[
            "Lean and Six Sigma methodologies",
            "Supply chain optimization",
            "Process automation and digitalization",
            "Performance management systems",
            "Cost reduction and efficiency programs"
        ],
        metrics=PerformanceMetrics(
            client_satisfaction=4.9,
            task_completion_rate=99.1,
            avg_response_time=1.8,
            problem_resolution_rate=98.6,
            client_retention_rate=97.1,
            annual_projects=160,
            error_rate=0.3,
            uptime_sla=99.97
        ),
        pricing=[
            PricingTier("Starter", 749, 7490, 75, "Up to 10 tasks/week"),
            PricingTier("Professional", 1799, 17990, 45, "Up to 40 tasks/week"),
            PricingTier("Enterprise", 0, 0, 32.5, "Unlimited, executive access")
        ],
        use_cases=[
            "Supply Chain Optimization",
            "Process Improvement",
            "Cost Reduction",
            "Operational Scaling",
            "Automation Strategy",
            "Vendor Management",
            "Performance Management"
        ],
        success_stories=[
            SuccessStory(
                "Manufacturing Operations Transformation",
                "Mid-size Manufacturing Company",
                "Outdated operations, high costs, and quality issues",
                "Led comprehensive operational transformation including process redesign and automation",
                ["Operating costs reduced by 28% ($12M annually)", "Quality defect rates reduced by 67%", "Employee safety incidents reduced by 85%"]
            )
        ],
        testimonials=[
            Testimonial(
                "David's operational transformation was remarkable. The 28% cost savings directly improved our profitability.",
                "Robert Chen",
                "COO"
            )
        ],
        strong_points=[
            "Operational Excellence",
            "Analytical Rigor",
            "Implementation Capability",
            "Change Management",
            "Cost Consciousness"
        ],
        multilingual_names={
            "English": "David Rodriguez",
            "Spanish": "David Rodríguez",
            "Mandarin": "大卫·罗德里格斯",
            "Japanese": "ダビッド・ロドリゲス"
        }
    )
]


class AgentMarketplace:
    """Manages the elite agent marketplace"""
    
    def __init__(self):
        self.agents = {agent.agent_id: agent for agent in ELITE_AGENTS}
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all agent profiles"""
        return [agent.to_dict() for agent in self.agents.values()]
    
    def get_agent_summaries(self) -> List[Dict[str, Any]]:
        """Get summary view of all agents"""
        return [agent.to_summary() for agent in self.agents.values()]
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific agent profile"""
        agent = self.agents.get(agent_id)
        return agent.to_dict() if agent else None
    
    def search_agents(self, specialization: str = None, max_price: float = None) -> List[Dict[str, Any]]:
        """Search agents by criteria"""
        results = []
        for agent in self.agents.values():
            if specialization:
                specs = [agent.primary_specialization, agent.secondary_specialization, agent.tertiary_specialization]
                if not any(specialization.lower() in s.lower() for s in specs):
                    continue
            
            if max_price is not None:
                starter_price = agent.pricing[0].monthly if agent.pricing else 0
                if starter_price > max_price:
                    continue
            
            results.append(agent.to_summary())
        
        return results
    
    def get_comparison(self) -> Dict[str, Any]:
        """Get comparison data for all agents"""
        return {
            "performance_comparison": [
                {
                    "name": a.name,
                    "satisfaction": a.metrics.client_satisfaction,
                    "completion_rate": a.metrics.task_completion_rate,
                    "resolution_rate": a.metrics.problem_resolution_rate,
                    "retention_rate": a.metrics.client_retention_rate,
                    "specialization": a.primary_specialization
                }
                for a in self.agents.values()
            ],
            "pricing_comparison": [
                {
                    "name": a.name,
                    "starter": a.pricing[0].monthly if a.pricing else 0,
                    "professional": a.pricing[1].monthly if len(a.pricing) > 1 else 0,
                    "specialization": a.primary_specialization
                }
                for a in self.agents.values()
            ]
        }


# Global marketplace instance
agent_marketplace = AgentMarketplace()
