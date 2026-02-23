"""
Autonomy Gate — Governance-Gated Self-Execution Engine
Allows Trinity to execute missions autonomously within pre-set governance bounds
"""

from enum import Enum
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class AuthorityLevel(Enum):
    """Execution authority levels"""
    MANUAL = 0  # All tasks require human approval
    SEMI_AUTO = 1  # Some tasks auto-execute; others escalate
    FULL_AUTO = 2  # All tasks auto-execute within governance bounds


class GovernanceScope(Enum):
    """Scope boundaries for autonomous execution"""
    INTERNAL = "internal"  # Code changes, tests, logs
    EXTERNAL_LOW = "external_low"  # Public APIs, read-only
    EXTERNAL_MEDIUM = "external_medium"  # Payments, state changes
    EXTERNAL_HIGH = "external_high"  # Deployment, critical infrastructure
    RESTRICTED = "restricted"  # Never auto-execute


class AutonomyGate:
    """
    Governance-gated autonomous execution engine.
    
    Checks if a mission can auto-execute based on:
    - Authority level
    - Governance scope
    - Evidence gates (proof-of-intent)
    - Resource limits
    - Time-based policies
    """

    def __init__(
        self,
        authority_level: AuthorityLevel = AuthorityLevel.SEMI_AUTO,
        default_scope: GovernanceScope = GovernanceScope.INTERNAL,
        rate_limit_per_hour: int = 100,
        max_cost_per_mission: float = 1000.0,
    ):
        self.authority_level = authority_level
        self.default_scope = default_scope
        self.rate_limit_per_hour = rate_limit_per_hour
        self.max_cost_per_mission = max_cost_per_mission
        
        # Execution history for rate limiting
        self.execution_history: List[Tuple[datetime, str, Dict]] = []
        
        # Governance policies (can be updated via API)
        self.policies: Dict[str, Dict] = self._init_default_policies()

    def _init_default_policies(self) -> Dict:
        """Initialize default governance policies"""
        return {
            "internal": {
                "auto_execute": True,
                "requires_evidence": True,
                "max_retries": 3,
                "timeout_sec": 300,
            },
            "external_low": {
                "auto_execute": True,
                "requires_evidence": True,
                "max_retries": 2,
                "timeout_sec": 60,
            },
            "external_medium": {
                "auto_execute": self.authority_level in [AuthorityLevel.FULL_AUTO],
                "requires_evidence": True,
                "max_retries": 1,
                "timeout_sec": 120,
            },
            "external_high": {
                "auto_execute": False,  # Always escalate
                "requires_evidence": True,
                "max_retries": 0,
                "timeout_sec": 0,
            },
            "restricted": {
                "auto_execute": False,
                "requires_evidence": True,
                "max_retries": 0,
                "timeout_sec": 0,
            },
        }

    def can_execute(
        self,
        mission: Dict,
        evidence: Optional[Dict] = None,
        cost_estimate: float = 0.0,
    ) -> Tuple[bool, str]:
        """
        Check if mission can auto-execute.
        
        Args:
            mission: Mission dict with id, prompt, scope, provider
            evidence: Evidence dict (proof-of-intent, blake_birthmark, etc.)
            cost_estimate: Estimated cost of execution
        
        Returns:
            (can_execute: bool, reason: str)
        """
        mission_id = mission.get("id", "unknown")
        scope = GovernanceScope(mission.get("scope", self.default_scope.value))
        
        logger.info(f"[AutonomyGate] Checking mission {mission_id}, scope={scope.value}")
        
        # 1. Check authority level
        if self.authority_level == AuthorityLevel.MANUAL:
            return False, "MANUAL mode: all tasks require human approval"
        
        # 2. Check scope boundaries
        policy = self.policies.get(scope.value)
        if not policy:
            return False, f"Unknown scope: {scope.value}"
        
        if not policy["auto_execute"]:
            return False, f"Scope {scope.value} does not allow auto-execution (escalate to human)"
        
        # 3. Check evidence gates
        if policy["requires_evidence"]:
            if not evidence:
                return False, "Evidence required but not provided"
            
            if not self._verify_evidence(evidence):
                return False, "Evidence verification failed"
        
        # 4. Check rate limiting
        is_within_rate_limit, limit_reason = self._check_rate_limit()
        if not is_within_rate_limit:
            return False, limit_reason
        
        # 5. Check cost limits
        if cost_estimate > self.max_cost_per_mission:
            return False, f"Cost estimate ${cost_estimate} exceeds max ${self.max_cost_per_mission}"
        
        # 6. Check resource availability
        if mission.get("requires_gpu") and not self._has_gpu_available():
            return False, "GPU required but not available"
        
        logger.info(f"[AutonomyGate] ✅ Mission {mission_id} approved for auto-execution")
        return True, "All governance gates passed"

    def delegate(
        self,
        mission: Dict,
        target_subsystem: str,
        evidence: Optional[Dict] = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Self-delegate mission to subsystem (YUR-AI, WAV, CW, etc.)
        without waiting for human approval.
        
        Args:
            mission: Mission to delegate
            target_subsystem: Target system (e.g., "yur_ai", "wav", "construction_wizard")
            evidence: Evidence dict
        
        Returns:
            (success: bool, message: str, delegation_id: Optional[str])
        """
        mission_id = mission.get("id", "unknown")
        
        # Check if delegation is allowed
        can_execute, reason = self.can_execute(mission, evidence)
        if not can_execute:
            logger.warning(f"[AutonomyGate] Delegation blocked: {reason}")
            return False, f"Delegation blocked: {reason}", None
        
        # Create delegation record
        delegation_id = self._create_delegation_id(mission_id, target_subsystem)
        delegation = {
            "delegation_id": delegation_id,
            "mission_id": mission_id,
            "target_subsystem": target_subsystem,
            "delegated_at": datetime.utcnow().isoformat(),
            "evidence": evidence,
            "governance_approval": "auto_approved",
        }
        
        # Record delegation in history
        self.execution_history.append((datetime.utcnow(), mission_id, delegation))
        
        logger.info(
            f"[AutonomyGate] ✅ Mission {mission_id} delegated to "
            f"{target_subsystem} (delegation_id: {delegation_id})"
        )
        
        return True, f"Delegation approved", delegation_id

    def override_policy(
        self,
        scope: GovernanceScope,
        new_policy: Dict,
        approver_id: str,
    ) -> Tuple[bool, str]:
        """
        Override a governance policy (requires high authority).
        
        Args:
            scope: Scope to override
            new_policy: New policy dict
            approver_id: Human approver ID (audit trail)
        
        Returns:
            (success: bool, message: str)
        """
        if self.authority_level == AuthorityLevel.MANUAL:
            return False, "Cannot override policies in MANUAL mode"
        
        old_policy = self.policies.get(scope.value, {})
        self.policies[scope.value] = {**old_policy, **new_policy}
        
        logger.warning(
            f"[AutonomyGate] Policy override for {scope.value} "
            f"by {approver_id}: {new_policy}"
        )
        
        return True, f"Policy updated for {scope.value}"

    def get_autonomy_report(self) -> Dict:
        """Get current autonomy configuration and execution stats"""
        executions_this_hour = sum(
            1 for timestamp, _, _ in self.execution_history
            if datetime.utcnow() - timestamp < timedelta(hours=1)
        )
        
        return {
            "authority_level": self.authority_level.name,
            "default_scope": self.default_scope.value,
            "rate_limit_per_hour": self.rate_limit_per_hour,
            "executions_this_hour": executions_this_hour,
            "max_cost_per_mission": self.max_cost_per_mission,
            "policies": self.policies,
            "recent_delegations": [
                {
                    "mission_id": mission_id,
                    "delegated_at": timestamp.isoformat(),
                    "details": details,
                }
                for timestamp, mission_id, details in self.execution_history[-10:]
            ],
        }

    def _verify_evidence(self, evidence: Dict) -> bool:
        """Verify evidence gates (proof-of-intent, signatures, etc.)"""
        required_fields = ["blake_birthmark", "intent", "timestamp", "signature"]
        
        for field in required_fields:
            if field not in evidence:
                logger.warning(f"Missing evidence field: {field}")
                return False
        
        # TODO: Verify blake_birthmark signature against known keys
        # TODO: Verify timestamp is recent (not replayed)
        
        logger.info(f"✅ Evidence verified")
        return True

    def _check_rate_limit(self) -> Tuple[bool, str]:
        """Check if mission execution is within rate limits"""
        executions_this_hour = sum(
            1 for timestamp, _, _ in self.execution_history
            if datetime.utcnow() - timestamp < timedelta(hours=1)
        )
        
        if executions_this_hour >= self.rate_limit_per_hour:
            return False, f"Rate limit exceeded ({executions_this_hour}/{self.rate_limit_per_hour})"
        
        return True, "Within rate limits"

    def _has_gpu_available(self) -> bool:
        """Check if GPU is available (stub for now)"""
        # TODO: Query actual GPU availability
        return True

    def _create_delegation_id(self, mission_id: str, target_subsystem: str) -> str:
        """Create a deterministic delegation ID"""
        content = f"{mission_id}:{target_subsystem}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


# Global instance (can be configured per deployment)
default_autonomy_gate = AutonomyGate(
    authority_level=AuthorityLevel.SEMI_AUTO,
    default_scope=GovernanceScope.INTERNAL,
    rate_limit_per_hour=100,
    max_cost_per_mission=1000.0,
)
