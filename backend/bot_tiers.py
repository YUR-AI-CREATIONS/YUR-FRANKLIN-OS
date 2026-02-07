"""
4-Tier Bot System for FRANKLIN OS
Scout → Qualifier → Pipeline → Elite Scalar
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BotTier(Enum):
    """Bot tier levels"""
    SCOUT = 1
    QUALIFIER = 2
    PIPELINE = 3
    ELITE = 4


class AutonomyLevel(Enum):
    """Autonomy levels for bots"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SOVEREIGN = "sovereign"


@dataclass
class BotConfig:
    """Configuration for a bot tier"""
    name: str
    tier_level: int
    description: str
    min_usd: float
    max_usd: float
    allowed_sources: List[str]
    task_types: List[str]
    risk_controls: List[str]
    evidence_requirements: List[str]
    autonomy_level: AutonomyLevel
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "tier_level": self.tier_level,
            "description": self.description,
            "min_usd": self.min_usd,
            "max_usd": self.max_usd,
            "allowed_sources": self.allowed_sources,
            "task_types": self.task_types,
            "risk_controls": self.risk_controls,
            "evidence_requirements": self.evidence_requirements,
            "autonomy_level": self.autonomy_level.value
        }


@dataclass
class BotInstance:
    """Active bot instance"""
    bot_id: str
    name: str
    tier: BotTier
    config: BotConfig
    status: str = "idle"
    created_at: datetime = field(default_factory=datetime.utcnow)
    tasks_completed: int = 0
    total_value_processed: float = 0.0
    current_task: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "bot_id": self.bot_id,
            "name": self.name,
            "tier": self.tier.name,
            "tier_level": self.tier.value,
            "config": self.config.to_dict(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "tasks_completed": self.tasks_completed,
            "total_value_processed": self.total_value_processed,
            "current_task": self.current_task
        }


# Predefined tier configurations
BOT_TIER_CONFIGS = {
    BotTier.SCOUT: BotConfig(
        name="Tier 1 - Scout Bot",
        tier_level=1,
        description="Lead discovery and bid/auction scanning with strict compliance controls.",
        min_usd=0,
        max_usd=2500,
        allowed_sources=["public_bid_portals", "public_auctions", "open_procurement_feeds"],
        task_types=["lead_scrape", "signal_capture", "basic_enrichment"],
        risk_controls=[
            "respect_robots_txt",
            "rate_limit",
            "no_credentialed_access",
            "pii_redaction"
        ],
        evidence_requirements=["source_urls", "timestamped_snapshots", "hashes"],
        autonomy_level=AutonomyLevel.LOW
    ),
    BotTier.QUALIFIER: BotConfig(
        name="Tier 2 - Qualifier Bot",
        tier_level=2,
        description="Qualifies leads, scores opportunities, and routes to agents.",
        min_usd=2500,
        max_usd=20000,
        allowed_sources=["public_bid_portals", "public_auctions", "partner_feeds"],
        task_types=["lead_scoring", "requirements_extraction", "opportunity_ranking"],
        risk_controls=["rate_limit", "consent_required", "pii_redaction"],
        evidence_requirements=["scoring_logs", "rules_snapshot", "source_urls"],
        autonomy_level=AutonomyLevel.MEDIUM
    ),
    BotTier.PIPELINE: BotConfig(
        name="Tier 3 - Pipeline Bot",
        tier_level=3,
        description="Pipeline automation, bid packaging, and compliance pre-checks.",
        min_usd=20000,
        max_usd=300000,
        allowed_sources=["public_bid_portals", "partner_feeds", "internal_crm"],
        task_types=["bid_packaging", "compliance_precheck", "proposal_drafting"],
        risk_controls=["human_approval_required", "audit_logging", "pii_redaction"],
        evidence_requirements=["proposal_hash", "compliance_checklist", "approval_logs"],
        autonomy_level=AutonomyLevel.HIGH
    ),
    BotTier.ELITE: BotConfig(
        name="Elite Scalar - Market Orchestrator Bot",
        tier_level=4,
        description="High-value market orchestration with board oversight.",
        min_usd=300000,
        max_usd=10000000,
        allowed_sources=["approved_partner_feeds", "internal_marketplace"],
        task_types=["market_orchestration", "portfolio_coordination", "capital_routing"],
        risk_controls=["board_approval_required", "audit_logging", "rate_limit"],
        evidence_requirements=["board_signoff", "ledger_anchor", "risk_report"],
        autonomy_level=AutonomyLevel.SOVEREIGN
    )
}


class BotTierSystem:
    """Manages the 4-tier bot system"""
    
    def __init__(self):
        self.bots: Dict[str, BotInstance] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
    
    def get_tier_configs(self) -> List[Dict[str, Any]]:
        """Get all tier configurations"""
        return [config.to_dict() for config in BOT_TIER_CONFIGS.values()]
    
    def get_tier_config(self, tier: BotTier) -> Dict[str, Any]:
        """Get configuration for a specific tier"""
        return BOT_TIER_CONFIGS[tier].to_dict()
    
    def create_bot(self, name: str, tier: BotTier) -> BotInstance:
        """Create a new bot instance"""
        bot_id = f"bot_{tier.name.lower()}_{len(self.bots) + 1:04d}"
        config = BOT_TIER_CONFIGS[tier]
        
        bot = BotInstance(
            bot_id=bot_id,
            name=name,
            tier=tier,
            config=config
        )
        
        self.bots[bot_id] = bot
        logger.info(f"Created {tier.name} bot: {bot_id}")
        return bot
    
    def get_bot(self, bot_id: str) -> Optional[BotInstance]:
        """Get a bot by ID"""
        return self.bots.get(bot_id)
    
    def list_bots(self, tier: BotTier = None) -> List[Dict[str, Any]]:
        """List all bots, optionally filtered by tier"""
        if tier:
            return [b.to_dict() for b in self.bots.values() if b.tier == tier]
        return [b.to_dict() for b in self.bots.values()]
    
    def assign_task(self, bot_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a task to a bot"""
        bot = self.bots.get(bot_id)
        if not bot:
            return {"success": False, "message": "Bot not found"}
        
        # Validate task value against tier limits
        task_value = task.get("value_usd", 0)
        if task_value < bot.config.min_usd or task_value > bot.config.max_usd:
            return {
                "success": False,
                "message": f"Task value ${task_value} outside tier limits (${bot.config.min_usd}-${bot.config.max_usd})"
            }
        
        # Validate task type
        task_type = task.get("type", "")
        if task_type and task_type not in bot.config.task_types:
            return {
                "success": False,
                "message": f"Task type '{task_type}' not allowed for {bot.tier.name} tier"
            }
        
        # Check approval requirements
        if "human_approval_required" in bot.config.risk_controls:
            task["requires_approval"] = True
        if "board_approval_required" in bot.config.risk_controls:
            task["requires_board_approval"] = True
        
        bot.status = "active"
        bot.current_task = task
        
        return {
            "success": True,
            "message": f"Task assigned to {bot.name}",
            "task": task,
            "bot": bot.to_dict()
        }
    
    def complete_task(self, bot_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Mark a task as completed"""
        bot = self.bots.get(bot_id)
        if not bot:
            return {"success": False, "message": "Bot not found"}
        
        if not bot.current_task:
            return {"success": False, "message": "No active task"}
        
        completed = {
            "task": bot.current_task,
            "result": result,
            "completed_at": datetime.utcnow().isoformat(),
            "bot_id": bot_id
        }
        
        self.completed_tasks.append(completed)
        bot.tasks_completed += 1
        bot.total_value_processed += bot.current_task.get("value_usd", 0)
        bot.status = "idle"
        bot.current_task = None
        
        return {
            "success": True,
            "message": "Task completed",
            "completed": completed
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall bot system status"""
        return {
            "total_bots": len(self.bots),
            "active_bots": len([b for b in self.bots.values() if b.status == "active"]),
            "idle_bots": len([b for b in self.bots.values() if b.status == "idle"]),
            "bots_by_tier": {
                tier.name: len([b for b in self.bots.values() if b.tier == tier])
                for tier in BotTier
            },
            "total_tasks_completed": sum(b.tasks_completed for b in self.bots.values()),
            "total_value_processed": sum(b.total_value_processed for b in self.bots.values()),
            "queued_tasks": len(self.task_queue)
        }


# Global bot tier system instance
bot_tier_system = BotTierSystem()
