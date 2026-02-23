"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      TRINITY SPINE GOVERNANCE INTEGRATION                   ║
║                                                                              ║
║  Integrates Trinity Spine autonomous operations with FrozenSpine governance ║
║  to ensure all autonomous agent executions are verified and drift-free.     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field

from agent_governance import agent_governance, GovernanceAction
from trinity.trinity import app as trinity_app  # Import Trinity FastAPI app


@dataclass
class TrinityExecution:
    """Trinity Spine execution record"""
    execution_id: str
    agent_id: str
    task_description: str
    execution_context: Dict[str, Any]
    governance_checkpoint: str
    status: str  # "pending", "approved", "executing", "completed", "failed"
    result: Optional[Dict[str, Any]] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    drift_score: float = 0.0
    safety_score: float = 0.0


class TrinityGovernanceBridge:
    """
    Bridge between Trinity Spine and FrozenSpine Governance

    Ensures all autonomous operations go through governance verification
    before execution, maintaining system integrity and preventing drift.
    """

    def __init__(self):
        self.active_executions: Dict[str, TrinityExecution] = {}
        self.execution_history: List[TrinityExecution] = []

    async def request_autonomous_execution(self, agent_id: str, task_description: str,
                                         execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request autonomous execution through governance verification

        Args:
            agent_id: ID of the agent requesting autonomous execution
            task_description: Description of the task to execute
            execution_context: Context and parameters for execution

        Returns:
            Dict with approval status and execution details
        """
        # Create execution record
        execution_id = f"trinity_{agent_id}_{datetime.now().timestamp()}"
        execution = TrinityExecution(
            execution_id=execution_id,
            agent_id=agent_id,
            task_description=task_description,
            execution_context=execution_context,
            governance_checkpoint="",
            status="pending"
        )

        # Request governance verification
        governance_result = await agent_governance.verify_autonomous_execution(
            agent_id,
            task_description,
            execution_context
        )

        execution.governance_checkpoint = governance_result["checkpoint_id"]
        execution.drift_score = governance_result["drift_score"]
        execution.safety_score = governance_result.get("safety_score", 0.0)

        if governance_result["approved"]:
            execution.status = "approved"
            self.active_executions[execution_id] = execution

            # Start execution in background
            asyncio.create_task(self._execute_autonomous_task(execution))

            return {
                "approved": True,
                "execution_id": execution_id,
                "governance_checkpoint": execution.governance_checkpoint,
                "drift_score": execution.drift_score,
                "safety_score": execution.safety_score,
                "message": "Autonomous execution approved and started"
            }
        else:
            execution.status = "rejected"
            self.execution_history.append(execution)

            return {
                "approved": False,
                "execution_id": execution_id,
                "governance_checkpoint": execution.governance_checkpoint,
                "drift_score": execution.drift_score,
                "message": f"Autonomous execution rejected: {governance_result['message']}",
                "requires_manual_review": True
            }

    async def _execute_autonomous_task(self, execution: TrinityExecution):
        """Execute the autonomous task through Trinity Spine"""
        try:
            execution.status = "executing"
            execution.started_at = datetime.now(timezone.utc).isoformat()

            # Call Trinity Spine execution
            # This would integrate with the actual Trinity execution logic
            result = await self._call_trinity_execution(
                execution.agent_id,
                execution.task_description,
                execution.execution_context
            )

            execution.status = "completed"
            execution.result = result
            execution.completed_at = datetime.now(timezone.utc).isoformat()

        except Exception as e:
            execution.status = "failed"
            execution.result = {"error": str(e)}
            execution.completed_at = datetime.now(timezone.utc).isoformat()

        finally:
            # Move to history
            self.execution_history.append(execution)
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]

    async def _call_trinity_execution(self, agent_id: str, task_description: str,
                                    execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the actual Trinity Spine execution logic

        This is a placeholder that would integrate with the real Trinity implementation
        """
        # Placeholder for Trinity execution
        # In real implementation, this would call the appropriate Trinity functions

        # Simulate execution time
        await asyncio.sleep(1)

        return {
            "agent_id": agent_id,
            "task_completed": True,
            "execution_time": 1.0,
            "result": f"Autonomous task '{task_description}' completed successfully",
            "governed_execution": True
        }

    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an autonomous execution"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
        else:
            execution = next((e for e in self.execution_history if e.execution_id == execution_id), None)

        if not execution:
            return None

        return {
            "execution_id": execution.execution_id,
            "agent_id": execution.agent_id,
            "status": execution.status,
            "governance_checkpoint": execution.governance_checkpoint,
            "drift_score": execution.drift_score,
            "safety_score": execution.safety_score,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "result": execution.result
        }

    async def get_active_executions(self) -> List[Dict[str, Any]]:
        """Get all active autonomous executions"""
        return [
            {
                "execution_id": e.execution_id,
                "agent_id": e.agent_id,
                "task_description": e.task_description,
                "status": e.status,
                "governance_checkpoint": e.governance_checkpoint,
                "drift_score": e.drift_score,
                "safety_score": e.safety_score,
                "started_at": e.started_at
            }
            for e in self.active_executions.values()
        ]

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an active autonomous execution"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.status = "cancelled"
            execution.completed_at = datetime.now(timezone.utc).isoformat()
            execution.result = {"cancelled": True, "reason": "User cancellation"}

            # Move to history
            self.execution_history.append(execution)
            del self.active_executions[execution_id]
            return True

        return False

    async def get_governance_metrics(self) -> Dict[str, Any]:
        """Get governance metrics for Trinity operations"""
        total_executions = len(self.execution_history)
        approved_executions = len([e for e in self.execution_history if e.status == "completed"])
        rejected_executions = len([e for e in self.execution_history if e.status == "rejected"])
        failed_executions = len([e for e in self.execution_history if e.status == "failed"])

        avg_drift_score = sum(e.drift_score for e in self.execution_history) / max(total_executions, 1)
        avg_safety_score = sum(e.safety_score for e in self.execution_history) / max(total_executions, 1)

        return {
            "total_executions": total_executions,
            "approved_executions": approved_executions,
            "rejected_executions": rejected_executions,
            "failed_executions": failed_executions,
            "active_executions": len(self.active_executions),
            "approval_rate": approved_executions / max(total_executions, 1),
            "avg_drift_score": avg_drift_score,
            "avg_safety_score": avg_safety_score,
            "system_health": "healthy" if avg_drift_score < 0.1 and avg_safety_score > 0.7 else "warning"
        }


# Global Trinity governance bridge instance
trinity_governance = TrinityGovernanceBridge()


# FastAPI routes for Trinity Governance (to be added to Trinity app)
async def request_trinity_execution(agent_id: str, task_description: str, execution_context: dict):
    """API endpoint for requesting governed Trinity execution"""
    return await trinity_governance.request_autonomous_execution(
        agent_id, task_description, execution_context
    )

async def get_trinity_execution_status(execution_id: str):
    """API endpoint for getting Trinity execution status"""
    result = await trinity_governance.get_execution_status(execution_id)
    if not result:
        return {"error": "Execution not found"}
    return result

async def cancel_trinity_execution(execution_id: str):
    """API endpoint for cancelling Trinity execution"""
    cancelled = await trinity_governance.cancel_execution(execution_id)
    return {"cancelled": cancelled}

async def get_trinity_governance_metrics():
    """API endpoint for Trinity governance metrics"""
    return await trinity_governance.get_governance_metrics()