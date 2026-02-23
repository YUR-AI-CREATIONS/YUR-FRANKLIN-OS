"""
Seed data for Supabase catalogs (agents, bots, academy, badges).
"""

AGENT_SEED = [
    {
        "id": "franklin-architect",
        "name": "Franklin Architect",
        "specialty": "System architecture & specs",
        "certified": True,
        "badge": "Frozen Spine Certified",
        "version": "1.0.0",
        "fields": ["architecture", "compliance"]
    },
    {
        "id": "trinity-builder",
        "name": "Trinity Builder",
        "specialty": "Full-stack code generation",
        "certified": True,
        "badge": "Genesis Gate Certified",
        "version": "1.0.0",
        "fields": ["backend", "frontend", "api"]
    },
    {
        "id": "neo-sentinel",
        "name": "Neo Sentinel",
        "specialty": "Security & hardening",
        "certified": True,
        "badge": "Security Gate Certified",
        "version": "1.0.0",
        "fields": ["security", "governance"]
    },
    {
        "id": "oracle-analyst",
        "name": "Oracle Analyst",
        "specialty": "Data & quality analysis",
        "certified": True,
        "badge": "Quality Gate Certified",
        "version": "1.0.0",
        "fields": ["data", "ml", "quality"]
    },
    {
        "id": "citadel-deployer",
        "name": "Citadel Deployer",
        "specialty": "Deployment automation",
        "certified": True,
        "badge": "Deployment Gate Certified",
        "version": "1.0.0",
        "fields": ["devops", "deployment"]
    },
    {
        "id": "medicus-clinical",
        "name": "Medicus Clinical",
        "specialty": "Healthcare & clinical workflows",
        "certified": True,
        "badge": "HIPAA/PHI Ready",
        "version": "1.0.0",
        "fields": ["healthcare", "clinical", "compliance"]
    },
    {
        "id": "fintech-quant",
        "name": "FinTech Quant",
        "specialty": "Payments, risk, ledgers",
        "certified": True,
        "badge": "PCI/AML Ready",
        "version": "1.0.0",
        "fields": ["fintech", "risk", "payments"]
    },
    {
        "id": "gov-risk",
        "name": "Civic Sentinel",
        "specialty": "Gov, grants, procurement",
        "certified": True,
        "badge": "Public Sector Cleared",
        "version": "1.0.0",
        "fields": ["government", "grants", "procurement"]
    },
    {
        "id": "supplychain-optimizer",
        "name": "Chain Orchestrator",
        "specialty": "Logistics & supply chain",
        "certified": True,
        "badge": "Logistics Verified",
        "version": "1.0.0",
        "fields": ["supply_chain", "logistics"]
    },
    {
        "id": "cyber-sentinel",
        "name": "Cyber Sentinel",
        "specialty": "Security, hardening, threat modeling",
        "certified": True,
        "badge": "Security Gate Certified",
        "version": "1.0.0",
        "fields": ["security", "appsec", "infra"]
    },
    {
        "id": "genai-safety",
        "name": "GenAI Safety",
        "specialty": "Model safety, guardrails, evals",
        "certified": True,
        "badge": "Safety & Evals",
        "version": "1.0.0",
        "fields": ["genai", "safety", "evaluation"]
    },
    {
        "id": "climate-modeler",
        "name": "Climate Modeler",
        "specialty": "Sustainability, ESG, climate data",
        "certified": True,
        "badge": "ESG Ready",
        "version": "1.0.0",
        "fields": ["climate", "esg", "sustainability"]
    },
    {
        "id": "manufacturing-quality",
        "name": "Factory QA",
        "specialty": "Manufacturing QA/QC, SPC",
        "certified": True,
        "badge": "Six Sigma Aligned",
        "version": "1.0.0",
        "fields": ["manufacturing", "quality", "iot"]
    },
    {
        "id": "marketing-growth",
        "name": "Growth Strategist",
        "specialty": "Funnels, attribution, MarTech",
        "certified": True,
        "badge": "Growth Certified",
        "version": "1.0.0",
        "fields": ["marketing", "growth", "ads"]
    },
    {
        "id": "blockchain-ledger",
        "name": "Ledger Architect",
        "specialty": "Blockchain, smart contracts",
        "certified": True,
        "badge": "Ledger Verified",
        "version": "1.0.0",
        "fields": ["blockchain", "smart_contracts", "ledgers"]
    },
    {
        "id": "construction-pro",
        "name": "Construction Pro",
        "specialty": "AEC, earthwork, inspections",
        "certified": True,
        "badge": "Construction Certified",
        "version": "1.0.0",
        "fields": ["construction", "aec", "earthwork"]
    },
    {
        "id": "legal-counsel",
        "name": "Legal Counsel",
        "specialty": "Contracts, compliance, policy",
        "certified": True,
        "badge": "Legal Review Ready",
        "version": "1.0.0",
        "fields": ["legal", "compliance", "policy"]
    },
    {
        "id": "transport-mobility",
        "name": "Transport & Mobility",
        "specialty": "Transportation, routing, logistics",
        "certified": True,
        "badge": "Mobility Verified",
        "version": "1.0.0",
        "fields": ["transportation", "routing", "mobility"]
    },
    {
        "id": "travel-concierge",
        "name": "Travel Concierge",
        "specialty": "Travel booking, itineraries",
        "certified": True,
        "badge": "Travel Certified",
        "version": "1.0.0",
        "fields": ["travel", "booking", "itinerary"]
    },
    {
        "id": "social-media-strategist",
        "name": "Social Media Strategist",
        "specialty": "Content, scheduling, analytics",
        "certified": True,
        "badge": "Social Growth",
        "version": "1.0.0",
        "fields": ["social_media", "content", "engagement"]
    },
    {
        "id": "graphic-designer",
        "name": "Graphic Designer",
        "specialty": "Branding, UI assets",
        "certified": True,
        "badge": "Design Certified",
        "version": "1.0.0",
        "fields": ["design", "graphics", "branding"]
    },
    {
        "id": "estate-planner",
        "name": "Estate Planner",
        "specialty": "Wills, trusts, planning",
        "certified": True,
        "badge": "Estate Ready",
        "version": "1.0.0",
        "fields": ["estate", "planning", "legal"]
    },
    {
        "id": "insurance-generalist",
        "name": "Insurance Generalist",
        "specialty": "P&C, health, life, underwriting",
        "certified": True,
        "badge": "Insurance Certified",
        "version": "1.0.0",
        "fields": ["insurance", "underwriting", "claims"]
    },
    {
        "id": "epa-compliance",
        "name": "EPA Compliance",
        "specialty": "Environmental, EPA, reporting",
        "certified": True,
        "badge": "EPA Ready",
        "version": "1.0.0",
        "fields": ["environment", "epa", "compliance"]
    },
    {
        "id": "global-finance",
        "name": "Global Finance",
        "specialty": "FX, cross-border, treasury",
        "certified": True,
        "badge": "Global Finance",
        "version": "1.0.0",
        "fields": ["finance", "fx", "treasury"]
    },
    {
        "id": "compliance-officer",
        "name": "Compliance Officer",
        "specialty": "Risk, audit, regulatory",
        "certified": True,
        "badge": "Compliance Verified",
        "version": "1.0.0",
        "fields": ["compliance", "risk", "audit"]
    }
]


BOT_TASK_TIERS_SEED = [
    {
        "id": "bot-tier-1",
        "name": "Tier 1 - Scout Bot",
        "tier_level": 1,
        "description": "Lead discovery and bid/auction scanning with strict compliance controls.",
        "autonomy_level": "low",
        "scope": "Discovery & signals",
        "allowed_sources": ["public_bid_portals", "public_auctions", "open_procurement_feeds"],
        "task_types": ["lead_scrape", "signal_capture", "basic_enrichment"],
        "risk_controls": ["respect_robots_txt", "rate_limit", "no_credentialed_access", "pii_redaction"],
        "evidence_requirements": ["source_urls", "timestamped_snapshots", "hashes"]
    },
    {
        "id": "bot-tier-2",
        "name": "Tier 2 - Qualifier Bot",
        "tier_level": 2,
        "description": "Qualifies leads, scores opportunities, and routes to agents.",
        "autonomy_level": "medium",
        "scope": "Lead scoring & routing",
        "allowed_sources": ["public_bid_portals", "public_auctions", "partner_feeds"],
        "task_types": ["lead_scoring", "requirements_extraction", "opportunity_ranking"],
        "risk_controls": ["rate_limit", "consent_required", "pii_redaction"],
        "evidence_requirements": ["scoring_logs", "rules_snapshot", "source_urls"]
    },
    {
        "id": "bot-tier-3",
        "name": "Tier 3 - Pipeline Bot",
        "tier_level": 3,
        "description": "Pipeline automation, bid packaging, and compliance pre-checks.",
        "autonomy_level": "high",
        "scope": "Bid packaging & compliance",
        "allowed_sources": ["public_bid_portals", "partner_feeds", "internal_crm"],
        "task_types": ["bid_packaging", "compliance_precheck", "proposal_drafting"],
        "risk_controls": ["human_approval_required", "audit_logging", "pii_redaction"],
        "evidence_requirements": ["proposal_hash", "compliance_checklist", "approval_logs"]
    },
    {
        "id": "bot-tier-4",
        "name": "Elite Scalar - Market Orchestrator Bot",
        "tier_level": 4,
        "description": "High-value market orchestration with board oversight.",
        "autonomy_level": "sovereign",
        "scope": "Market orchestration",
        "allowed_sources": ["approved_partner_feeds", "internal_marketplace"],
        "task_types": ["market_orchestration", "portfolio_coordination", "capital_routing"],
        "risk_controls": ["board_approval_required", "audit_logging", "rate_limit"],
        "evidence_requirements": ["board_signoff", "ledger_anchor", "risk_report"]
    }
]


ACADEMY_MODULES_SEED = [
    {
        "id": "academy-qmc-foundations",
        "title": "QMC Foundations for Agent Optimization",
        "summary": "Core theory and practical setup for quasi-Monte Carlo workflows.",
        "level": "advanced",
        "status": "active",
        "content": {
            "objectives": [
                "Explain QMC variance reduction",
                "Compare Sobol sequences with pseudo-random sampling",
                "Apply QMC to multi-dimensional risk models"
            ],
            "lessons": [
                "QMC fundamentals",
                "Sobol sequence generation",
                "Error bounds and convergence"
            ],
            "labs": ["Build a Sobol-driven estimator", "Compare QMC vs Monte Carlo output"],
            "assessments": ["QMC concept quiz", "Variance reduction report"]
        },
        "tags": ["qmc", "education", "optimization"],
        "metadata": {"track": "QMC Turbo Teaching"}
    },
    {
        "id": "academy-qpmc-service",
        "title": "QPyMC Service Integration Lab",
        "summary": "Hands-on integration with the QPyMC service stack.",
        "level": "advanced",
        "status": "active",
        "content": {
            "objectives": [
                "Deploy the QPyMC service",
                "Invoke QMC endpoints",
                "Interpret integration results"
            ],
            "lessons": [
                "Service deployment",
                "API request patterns",
                "Result validation"
            ],
            "labs": ["Deploy QPyMC container", "Run qmc-integrator test cases"],
            "assessments": ["Service readiness checklist"]
        },
        "tags": ["qpymc", "qmc", "integration"],
        "metadata": {"track": "QMC Turbo Teaching"}
    },
    {
        "id": "academy-turbo-teaching",
        "title": "Turbo Teaching Loop - Observe, Simulate, Correct",
        "summary": "Accelerated learning cycle for agents using QMC simulation feedback.",
        "level": "advanced",
        "status": "active",
        "content": {
            "objectives": [
                "Operate the turbo teaching loop",
                "Generate adaptive lessons from simulation outcomes",
                "Validate improvement with assessments"
            ],
            "lessons": [
                "Loop architecture",
                "Simulation-driven feedback",
                "Adaptive lesson generation"
            ],
            "labs": ["Run a turbo teaching cycle", "Score improvements across iterations"],
            "assessments": ["Turbo teaching report"]
        },
        "tags": ["qmc", "education", "self-evolution"],
        "metadata": {"track": "QMC Turbo Teaching"}
    },
    {
        "id": "academy-self-evolution",
        "title": "Self-Evolution Protocol - Hypothesis to Deployment",
        "summary": "Full lifecycle of self-evolution with governance guardrails.",
        "level": "expert",
        "status": "active",
        "content": {
            "objectives": [
                "Draft evolution proposals",
                "Run sandbox + red-team validation",
                "Prepare board-ready deployment packages"
            ],
            "lessons": [
                "Hypothesis generation",
                "Risk gating and validation",
                "Deployment and rollback"
            ],
            "labs": ["Create an evolution proposal", "Run a sandbox report"],
            "assessments": ["Board readiness review"]
        },
        "tags": ["self-evolution", "governance", "safety"],
        "metadata": {"track": "Sovereign Evolution"}
    },
    {
        "id": "academy-governance-alliance",
        "title": "Monthly Governance & Audit Alliance",
        "summary": "Human + AI alliance protocol for monthly audits and board governance.",
        "level": "expert",
        "status": "active",
        "content": {
            "objectives": [
                "Execute monthly evidence collection",
                "Run AI pre-audit validation",
                "Publish ledger-anchored audit report"
            ],
            "lessons": [
                "Evidence bundle integrity",
                "Board scoring process",
                "Ledger anchoring"
            ],
            "labs": ["Compile evidence registry", "Draft monthly report"],
            "assessments": ["Audit alliance checklist"]
        },
        "tags": ["governance", "audit", "alliance"],
        "metadata": {"track": "Governance Alliance"}
    },
    {
        "id": "academy-graduation",
        "title": "Agent Graduation & Classification",
        "summary": "Criteria for agent graduation, certification, and tier placement.",
        "level": "intermediate",
        "status": "active",
        "content": {
            "objectives": [
                "Apply tier criteria",
                "Validate certifications",
                "Maintain graduation evidence"
            ],
            "lessons": [
                "Tier requirements",
                "Certification mapping",
                "Ongoing evaluation"
            ],
            "labs": ["Tier placement case study"],
            "assessments": ["Graduation rubric review"]
        },
        "tags": ["academy", "certification", "tiers"],
        "metadata": {"track": "Agent Lifecycle"}
    }
]


DOMAIN_BADGES_SEED = [
    {
        "id": "badge-construction-audit-gold",
        "domain_name": "Construction Auditing",
        "name": "Gold Standard Audit",
        "description": "Validated against zoning, permitting, and RSMeans benchmarks.",
        "level": "gold",
        "criteria": {"trust_score": 85, "compliance_score": 90, "consensus": 0.35}
    },
    {
        "id": "badge-insurance-claims-gold",
        "domain_name": "Insurance Auditing",
        "name": "Claims Integrity Seal",
        "description": "Claims reviewed with evidence-backed underwriting and fairness checks.",
        "level": "gold",
        "criteria": {"trust_score": 85, "compliance_score": 90}
    },
    {
        "id": "badge-underwriting-platinum",
        "domain_name": "Finance & Underwriting",
        "name": "Underwriting Assurance",
        "description": "Underwriting outputs validated with AML, KYC, and disclosure checks.",
        "level": "platinum",
        "criteria": {"trust_score": 88, "compliance_score": 92, "consensus": 0.4}
    },
    {
        "id": "badge-public-accountability",
        "domain_name": "Government Grants & Bonds",
        "name": "Public Accountability Mark",
        "description": "Procurement and eligibility reviewed to public-sector standards.",
        "level": "platinum",
        "criteria": {"trust_score": 88, "compliance_score": 92, "consensus": 0.4}
    },
    {
        "id": "badge-digital-assets-gold",
        "domain_name": "Crypto & Digital Assets Auditing",
        "name": "Digital Asset Risk Shield",
        "description": "Custody and AML controls verified for digital asset audits.",
        "level": "gold",
        "criteria": {"trust_score": 82, "compliance_score": 88}
    },
    {
        "id": "badge-real-estate-gold",
        "domain_name": "Real Estate Portfolio Auditing",
        "name": "Portfolio Integrity Badge",
        "description": "Valuation and disclosure checks passed for portfolio audits.",
        "level": "gold",
        "criteria": {"trust_score": 82, "compliance_score": 88}
    }
]
