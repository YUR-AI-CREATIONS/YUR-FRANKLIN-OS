"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      GOVERNANCE INTEGRATION FOR SUPERAGENTS                  ║
║                                                                              ║
║  Integrates FrozenSpine governance with agent marketplace, academy,         ║
║  and Trinity Spine autonomous operations. Ensures all agent deployments     ║
║  and runtime purchases are governed and drift-free.                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum

from genesis_kernel import FrozenSpine, PipelineStage
from agent_marketplace import agent_marketplace
from agent_academy import agent_academy
from governance_engine import GovernanceEngine, ApprovalStatus
try:
    from supabase_util import supabase_client
    SUPABASE_AVAILABLE = True
except ImportError:
    supabase_client = None
    SUPABASE_AVAILABLE = False


class GovernanceAction(Enum):
    """Types of governance actions for agents"""
    DEPLOYMENT = "deployment"
    PURCHASE = "purchase"
    RENTAL = "rental"
    CERTIFICATION = "certification"
    ENROLLMENT = "enrollment"
    AUTONOMOUS_EXECUTION = "autonomous_execution"


@dataclass
class GovernanceCheckpoint:
    """Governance checkpoint for agent operations"""
    checkpoint_id: str
    action: GovernanceAction
    agent_id: str
    user_id: str
    state: Dict[str, Any]
    metrics: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verified: bool = False
    drift_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary"""
        return {
            "checkpoint_id": self.checkpoint_id,
            "action": self.action.value,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "state": self.state,
            "metrics": self.metrics,
            "timestamp": self.timestamp,
            "verified": self.verified,
            "drift_score": self.drift_score
        }


class AgentGovernanceLayer:
    """
    Governance Layer for Agent Operations

    Ensures all agent marketplace, academy, and autonomous operations
    are governed by FrozenSpine drift detection and oversight boards.
    """

    def __init__(self):
        self.frozen_spine = FrozenSpine()
        self.governance_engine = GovernanceEngine()
        self.checkpoints: List[GovernanceCheckpoint] = []
        self.active_deployments: Dict[str, Dict[str, Any]] = {}

    async def verify_agent_deployment(self, agent_id: str, user_id: str,
                                    deployment_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify agent deployment through FrozenSpine governance

        Args:
            agent_id: ID of the agent being deployed
            user_id: ID of the user deploying
            deployment_config: Configuration for deployment

        Returns:
            Dict with verification results and governance approval
        """
        # Create governance checkpoint
        checkpoint = GovernanceCheckpoint(
            checkpoint_id=f"deploy_{agent_id}_{user_id}_{datetime.now().timestamp()}",
            action=GovernanceAction.DEPLOYMENT,
            agent_id=agent_id,
            user_id=user_id,
            state={
                "agent_id": agent_id,
                "user_id": user_id,
                "config": deployment_config,
                "stage": "deployment_request"
            },
            metrics={
                "agent_certification_level": await self._get_agent_certification_level(agent_id),
                "user_trust_score": await self._get_user_trust_score(user_id),
                "deployment_complexity": self._calculate_deployment_complexity(deployment_config)
            }
        )

        # Verify against FrozenSpine baseline
        spine_verification = self.frozen_spine.verify_integrity(
            checkpoint.state,
            PipelineStage.DEPLOYMENT
        )

        checkpoint.verified = spine_verification["verified"]
        checkpoint.drift_score = spine_verification.get("drift_score", 0.0)

        # Create approval gate for deployment
        approval_gate = self.governance_engine.create_approval_workflow(["deployment"])[0]

        # Auto-approve if no drift detected and agent is certified
        if checkpoint.verified and checkpoint.metrics["agent_certification_level"] >= 2:
            approval_gate.status = ApprovalStatus.APPROVED
            approval_gate.actual_approvers = ["frozen_spine_system"]
            approval_gate.resolved_at = datetime.now(timezone.utc).isoformat()

        self.checkpoints.append(checkpoint)

        # Store in Supabase for audit trail
        await self._store_governance_checkpoint(checkpoint)

        return {
            "verified": checkpoint.verified,
            "drift_score": checkpoint.drift_score,
            "approved": approval_gate.status == ApprovalStatus.APPROVED,
            "checkpoint_id": checkpoint.checkpoint_id,
            "message": spine_verification["message"],
            "requires_manual_review": not checkpoint.verified or checkpoint.metrics["agent_certification_level"] < 2
        }

    async def verify_agent_purchase(self, agent_id: str, user_id: str,
                                  purchase_type: str, duration_hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Verify agent purchase/rental through governance

        Args:
            agent_id: ID of the agent being purchased
            user_id: ID of the user purchasing
            purchase_type: "purchase" or "rental"
            duration_hours: Hours for rental (if applicable)

        Returns:
            Dict with verification results
        """
        action = GovernanceAction.PURCHASE if purchase_type == "purchase" else GovernanceAction.RENTAL

        checkpoint = GovernanceCheckpoint(
            checkpoint_id=f"{purchase_type}_{agent_id}_{user_id}_{datetime.now().timestamp()}",
            action=action,
            agent_id=agent_id,
            user_id=user_id,
            state={
                "agent_id": agent_id,
                "user_id": user_id,
                "purchase_type": purchase_type,
                "duration_hours": duration_hours,
                "stage": "purchase_request"
            },
            metrics={
                "agent_certification_level": await self._get_agent_certification_level(agent_id),
                "user_purchase_history": await self._get_user_purchase_history(user_id),
                "agent_popularity": await self._get_agent_popularity(agent_id)
            }
        )

        # Verify against FrozenSpine
        spine_verification = self.frozen_spine.verify_integrity(
            checkpoint.state,
            PipelineStage.DEPLOYMENT
        )

        checkpoint.verified = spine_verification["verified"]
        checkpoint.drift_score = spine_verification.get("drift_score", 0.0)

        self.checkpoints.append(checkpoint)
        await self._store_governance_checkpoint(checkpoint)

        return {
            "verified": checkpoint.verified,
            "drift_score": checkpoint.drift_score,
            "approved": checkpoint.verified,  # Purchases auto-approve if verified
            "checkpoint_id": checkpoint.checkpoint_id,
            "message": spine_verification["message"]
        }

    async def verify_autonomous_execution(self, agent_id: str, task_description: str,
                                        execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify autonomous agent execution through Trinity Spine governance

        Args:
            agent_id: ID of the executing agent
            task_description: Description of the autonomous task
            execution_context: Context for the execution

        Returns:
            Dict with verification results
        """
        checkpoint = GovernanceCheckpoint(
            checkpoint_id=f"autonomous_{agent_id}_{datetime.now().timestamp()}",
            action=GovernanceAction.AUTONOMOUS_EXECUTION,
            agent_id=agent_id,
            user_id="trinity_spine_system",
            state={
                "agent_id": agent_id,
                "task_description": task_description,
                "execution_context": execution_context,
                "stage": "autonomous_execution"
            },
            metrics={
                "agent_certification_level": await self._get_agent_certification_level(agent_id),
                "task_complexity": self._calculate_task_complexity(task_description),
                "execution_safety_score": self._assess_execution_safety(execution_context)
            }
        )

        # Strict verification for autonomous operations
        spine_verification = self.frozen_spine.verify_integrity(
            checkpoint.state,
            PipelineStage.DEPLOYMENT
        )

        checkpoint.verified = spine_verification["verified"]
        checkpoint.drift_score = spine_verification.get("drift_score", 0.0)

        # Autonomous operations require higher certification and lower drift tolerance
        autonomous_approved = (
            checkpoint.verified and
            checkpoint.drift_score < 0.05 and  # Stricter threshold for autonomous ops
            checkpoint.metrics["agent_certification_level"] >= 3 and
            checkpoint.metrics["execution_safety_score"] >= 0.8
        )

        checkpoint.verified = autonomous_approved
        self.checkpoints.append(checkpoint)
        await self._store_governance_checkpoint(checkpoint)

        return {
            "verified": autonomous_approved,
            "drift_score": checkpoint.drift_score,
            "approved": autonomous_approved,
            "checkpoint_id": checkpoint.checkpoint_id,
            "message": "Autonomous execution " + ("approved" if autonomous_approved else "blocked - requires governance review"),
            "safety_score": checkpoint.metrics["execution_safety_score"]
        }

    async def verify_certification_request(self, agent_id: str, program_id: str,
                                         ethical_score: float, reliability_score: float) -> Dict[str, Any]:
        """
        Verify agent certification through governance

        Args:
            agent_id: ID of the agent being certified
            program_id: ID of the certification program
            ethical_score: Agent's ethical evaluation score
            reliability_score: Agent's reliability score

        Returns:
            Dict with verification results
        """
        checkpoint = GovernanceCheckpoint(
            checkpoint_id=f"certify_{agent_id}_{program_id}_{datetime.now().timestamp()}",
            action=GovernanceAction.CERTIFICATION,
            agent_id=agent_id,
            user_id="academy_system",
            state={
                "agent_id": agent_id,
                "program_id": program_id,
                "ethical_score": ethical_score,
                "reliability_score": reliability_score,
                "stage": "certification_request"
            },
            metrics={
                "ethical_score": ethical_score,
                "reliability_score": reliability_score,
                "program_difficulty": await self._get_program_difficulty(program_id),
                "agent_training_completion": await self._get_agent_training_completion(agent_id, program_id)
            }
        )

        spine_verification = self.frozen_spine.verify_integrity(
            checkpoint.state,
            PipelineStage.DEPLOYMENT
        )

        checkpoint.verified = spine_verification["verified"]
        checkpoint.drift_score = spine_verification.get("drift_score", 0.0)

        # Certification requires oversight board approval
        approval_gate = self.governance_engine.create_approval_workflow(["certification"])[0]

        # Auto-approve if scores are excellent and no drift
        if (checkpoint.verified and
            ethical_score >= 95 and reliability_score >= 95 and
            checkpoint.drift_score < 0.1):
            approval_gate.status = ApprovalStatus.APPROVED
            approval_gate.actual_approvers = ["frozen_spine_system", "academy_board"]

        self.checkpoints.append(checkpoint)
        await self._store_governance_checkpoint(checkpoint)

        return {
            "verified": checkpoint.verified,
            "drift_score": checkpoint.drift_score,
            "approved": approval_gate.status == ApprovalStatus.APPROVED,
            "checkpoint_id": checkpoint.checkpoint_id,
            "message": spine_verification["message"],
            "requires_board_review": approval_gate.status != ApprovalStatus.APPROVED
        }

    async def get_governance_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get governance status for agents or overall system"""
        if agent_id:
            agent_checkpoints = [c for c in self.checkpoints if c.agent_id == agent_id]
            return {
                "agent_id": agent_id,
                "total_checkpoints": len(agent_checkpoints),
                "verified_checkpoints": len([c for c in agent_checkpoints if c.verified]),
                "avg_drift_score": sum(c.drift_score for c in agent_checkpoints) / max(len(agent_checkpoints), 1),
                "last_checkpoint": agent_checkpoints[-1].to_dict() if agent_checkpoints else None
            }
        else:
            return {
                "total_checkpoints": len(self.checkpoints),
                "verified_checkpoints": len([c for c in self.checkpoints if c.verified]),
                "active_deployments": len(self.active_deployments),
                "system_health": "healthy" if len([c for c in self.checkpoints if not c.verified]) < len(self.checkpoints) * 0.1 else "warning",
                "frozen_spine_status": "active"
            }

    # Helper methods for metrics calculation
    async def _get_agent_certification_level(self, agent_id: str) -> int:
        """Get agent's certification level (1-5)"""
        try:
            certifications = agent_academy.get_certifications(agent_id)
            if certifications:
                # Return highest certification level
                levels = {"Entry Level": 1, "Professional": 2, "Expert": 3, "Master": 4, "Distinguished Fellow": 5}
                return max(levels.get(cert["level"], 1) for cert in certifications)
            return 1  # Uncertified
        except:
            return 1

    async def _get_user_trust_score(self, user_id: str) -> float:
        """Get user's trust score based on history"""
        if not SUPABASE_AVAILABLE or not supabase_client:
            return 50.0  # Default neutral score

        try:
            # Query Supabase for user history
            result = supabase_client.table('user_profiles').select('trust_score').eq('user_id', user_id).execute()
            if result.data:
                return result.data[0].get('trust_score', 50.0)
            return 50.0  # Default neutral score
        except:
            return 50.0

    async def _get_user_purchase_history(self, user_id: str) -> int:
        """Get user's purchase history count"""
        if not SUPABASE_AVAILABLE or not supabase_client:
            return 0

        try:
            result = supabase_client.table('agent_purchases').select('id').eq('user_id', user_id).execute()
            return len(result.data) if result.data else 0
        except:
            return 0

    async def _get_agent_popularity(self, agent_id: str) -> int:
        """Get agent's popularity score"""
        if not SUPABASE_AVAILABLE or not supabase_client:
            return 0

        try:
            result = supabase_client.table('agent_purchases').select('id').eq('agent_id', agent_id).execute()
            return len(result.data) if result.data else 0
        except:
            return 0

    async def _get_program_difficulty(self, program_id: str) -> int:
        """Get program's difficulty level"""
        try:
            programs = agent_academy.get_programs()
            program = next((p for p in programs if p["id"] == program_id), None)
            if program:
                difficulty_map = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
                return difficulty_map.get(program.get("difficulty", "beginner"), 1)
            return 1
        except:
            return 1

    async def _get_agent_training_completion(self, agent_id: str, program_id: str) -> float:
        """Get agent's training completion percentage"""
        try:
            enrollments = agent_academy.get_enrollments(agent_id)
            enrollment = next((e for e in enrollments if e["program_id"] == program_id), None)
            if enrollment:
                return enrollment.get("completion_percentage", 0.0)
            return 0.0
        except:
            return 0.0

    def _calculate_deployment_complexity(self, config: Dict[str, Any]) -> float:
        """Calculate deployment complexity score"""
        complexity = 1.0
        if config.get("autonomous", False):
            complexity += 2.0
        if config.get("multi_region", False):
            complexity += 1.0
        if config.get("custom_integrations"):
            complexity += len(config["custom_integrations"]) * 0.5
        return min(complexity, 5.0)

    def _calculate_task_complexity(self, task_description: str) -> float:
        """Calculate task complexity based on description"""
        complexity_keywords = {
            "deploy": 1.0, "build": 1.5, "integrate": 2.0, "optimize": 2.5,
            "migrate": 3.0, "refactor": 2.0, "security": 3.0, "scale": 2.5
        }
        score = 1.0
        for keyword, weight in complexity_keywords.items():
            if keyword.lower() in task_description.lower():
                score += weight
        return min(score, 5.0)

    def _assess_execution_safety(self, context: Dict[str, Any]) -> float:
        """Assess safety score for autonomous execution"""
        safety_score = 1.0  # Base safety

        # Reduce safety for high-risk operations
        if context.get("involves_payment", False):
            safety_score -= 0.3
        if context.get("involves_user_data", False):
            safety_score -= 0.2
        if context.get("requires_external_api", False):
            safety_score -= 0.1

        # Increase safety for governance features
        if context.get("has_rollback_plan", False):
            safety_score += 0.2
        if context.get("monitored_execution", False):
            safety_score += 0.1
        if context.get("limited_scope", False):
            safety_score += 0.1

        return max(0.0, min(1.0, safety_score))

    async def _store_governance_checkpoint(self, checkpoint: GovernanceCheckpoint):
        """Store governance checkpoint in Supabase"""
        if not SUPABASE_AVAILABLE or not supabase_client:
            return  # Skip storage if Supabase not available

        try:
            data = {
                "checkpoint_id": checkpoint.checkpoint_id,
                "action": checkpoint.action.value,
                "agent_id": checkpoint.agent_id,
                "user_id": checkpoint.user_id,
                "state": checkpoint.state,
                "metrics": checkpoint.metrics,
                "timestamp": checkpoint.timestamp,
                "verified": checkpoint.verified,
                "drift_score": checkpoint.drift_score
            }
            supabase_client.table('governance_checkpoints').insert(data).execute()
        except Exception as e:
            print(f"Failed to store governance checkpoint: {e}")


# Global governance layer instance
agent_governance = AgentGovernanceLayer()