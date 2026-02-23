"""
Lightweight catalog of deployable agents.
"""
from typing import List, Dict, Any

AGENT_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "franklin-architect",
        "name": "Franklin Architect",
        "specialty": "System architecture & specs",
        "certified": True,
        "version": "1.0.0",
        "fields": ["architecture", "compliance"]
    },
    {
        "id": "trinity-builder",
        "name": "Trinity Builder",
        "specialty": "Full-stack code generation",
        "certified": True,
        "version": "1.0.0",
        "fields": ["backend", "frontend", "api"]
    },
    {
        "id": "neo-sentinel",
        "name": "Neo Sentinel",
        "specialty": "Security & hardening",
        "certified": True,
        "version": "1.0.0",
        "fields": ["security", "governance"]
    },
    {
        "id": "oracle-analyst",
        "name": "Oracle Analyst",
        "specialty": "Data & quality analysis",
        "certified": True,
        "version": "1.0.0",
        "fields": ["data", "ml", "quality"]
    },
    {
        "id": "citadel-deployer",
        "name": "Citadel Deployer",
        "specialty": "Deployment automation",
        "certified": True,
        "version": "1.0.0",
        "fields": ["devops", "deployment"]
    },
    {
        "id": "medicus-clinical",
        "name": "Medicus Clinical",
        "specialty": "Healthcare & clinical workflows",
        "certified": True,
        "version": "1.0.0",
        "fields": ["healthcare", "clinical", "compliance"]
    },
    {
        "id": "fintech-quant",
        "name": "FinTech Quant",
        "specialty": "Payments, risk, ledgers",
        "certified": True,
        "version": "1.0.0",
        "fields": ["fintech", "risk", "payments"]
    },
    {
        "id": "gov-risk",
        "name": "Civic Sentinel",
        "specialty": "Gov, grants, procurement",
        "certified": True,
        "version": "1.0.0",
        "fields": ["government", "grants", "procurement"]
    },
    {
        "id": "supplychain-optimizer",
        "name": "Chain Orchestrator",
        "specialty": "Logistics & supply chain",
        "certified": True,
        "version": "1.0.0",
        "fields": ["supply_chain", "logistics"]
    },
    {
        "id": "cyber-sentinel",
        "name": "Cyber Sentinel",
        "specialty": "Security, hardening, threat modeling",
        "certified": True,
        "version": "1.0.0",
        "fields": ["security", "appsec", "infra"]
    },
    {
        "id": "genai-safety",
        "name": "GenAI Safety",
        "specialty": "Model safety, guardrails, evals",
        "certified": True,
        "version": "1.0.0",
        "fields": ["genai", "safety", "evaluation"]
    },
    {
        "id": "climate-modeler",
        "name": "Climate Modeler",
        "specialty": "Sustainability, ESG, climate data",
        "certified": True,
        "version": "1.0.0",
        "fields": ["climate", "esg", "sustainability"]
    },
    {
        "id": "manufacturing-quality",
        "name": "Factory QA",
        "specialty": "Manufacturing QA/QC, SPC",
        "certified": True,
        "version": "1.0.0",
        "fields": ["manufacturing", "quality", "iot"]
    },
    {
        "id": "marketing-growth",
        "name": "Growth Strategist",
        "specialty": "Funnels, attribution, MarTech",
        "certified": True,
        "version": "1.0.0",
        "fields": ["marketing", "growth", "ads"]
    },
    {
        "id": "blockchain-ledger",
        "name": "Ledger Architect",
        "specialty": "Blockchain, smart contracts",
        "certified": True,
        "version": "1.0.0",
        "fields": ["blockchain", "smart_contracts", "ledgers"]
    },
    {
        "id": "construction-pro",
        "name": "Construction Pro",
        "specialty": "AEC, earthwork, inspections",
        "certified": True,
        "version": "1.0.0",
        "fields": ["construction", "aec", "earthwork"]
    },
    {
        "id": "legal-counsel",
        "name": "Legal Counsel",
        "specialty": "Contracts, compliance, policy",
        "certified": True,
        "version": "1.0.0",
        "fields": ["legal", "compliance", "policy"]
    },
    {
        "id": "transport-mobility",
        "name": "Transport & Mobility",
        "specialty": "Transportation, routing, logistics",
        "certified": True,
        "version": "1.0.0",
        "fields": ["transportation", "routing", "mobility"]
    },
    {
        "id": "travel-concierge",
        "name": "Travel Concierge",
        "specialty": "Travel booking, itineraries",
        "certified": True,
        "version": "1.0.0",
        "fields": ["travel", "booking", "itinerary"]
    },
    {
        "id": "social-media-strategist",
        "name": "Social Media Strategist",
        "specialty": "Content, scheduling, analytics",
        "certified": True,
        "version": "1.0.0",
        "fields": ["social_media", "content", "engagement"]
    },
    {
        "id": "graphic-designer",
        "name": "Graphic Designer",
        "specialty": "Branding, UI assets",
        "certified": True,
        "version": "1.0.0",
        "fields": ["design", "graphics", "branding"]
    },
    {
        "id": "estate-planner",
        "name": "Estate Planner",
        "specialty": "Wills, trusts, planning",
        "certified": True,
        "version": "1.0.0",
        "fields": ["estate", "planning", "legal"]
    },
    {
        "id": "insurance-generalist",
        "name": "Insurance Generalist",
        "specialty": "P&C, health, life, underwriting",
        "certified": True,
        "version": "1.0.0",
        "fields": ["insurance", "underwriting", "claims"]
    },
    {
        "id": "epa-compliance",
        "name": "EPA Compliance",
        "specialty": "Environmental, EPA, reporting",
        "certified": True,
        "version": "1.0.0",
        "fields": ["environment", "epa", "compliance"]
    },
    {
        "id": "global-finance",
        "name": "Global Finance",
        "specialty": "FX, cross-border, treasury",
        "certified": True,
        "version": "1.0.0",
        "fields": ["finance", "fx", "treasury"]
    },
    {
        "id": "compliance-officer",
        "name": "Compliance Officer",
        "specialty": "Risk, audit, regulatory",
        "certified": True,
        "version": "1.0.0",
        "fields": ["compliance", "risk", "audit"]
    }
]


def get_certified_agents() -> List[Dict[str, Any]]:
    return [a for a in AGENT_CATALOG if a.get("certified")]
