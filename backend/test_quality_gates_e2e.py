"""
End-to-End Tests for Quality Gates and Governance Integration
Tests the complete quality certification pipeline with governance verification
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from genesis_kernel import QualityGate, QualityDimension, PipelineStage
from genesis_kernel import QualityGate as KernelQualityGate
from agent_governance import agent_governance, GovernanceAction


class TestQualityGatesE2E:
    """End-to-end tests for quality gates with governance"""

    def test_quality_gate_initialization(self):
        """Test that quality gates initialize with 8 dimensions"""
        gate = KernelQualityGate()

        # Check all 8 dimensions are present
        expected_dimensions = {
            QualityDimension.COMPLETENESS,
            QualityDimension.COHERENCE,
            QualityDimension.CORRECTNESS,
            QualityDimension.SECURITY,
            QualityDimension.PERFORMANCE,
            QualityDimension.SCALABILITY,
            QualityDimension.MAINTAINABILITY,
            QualityDimension.COMPLIANCE
        }

        assert set(gate.dimension_weights.keys()) == expected_dimensions
        assert len(gate.dimension_weights) == 8

    def test_quality_assessment_complete_artifact(self):
        """Test quality assessment on a complete software artifact"""
        gate = KernelQualityGate()

        # Mock complete artifact
        complete_artifact = {
            "type": "python_function",
            "code": """
def calculate_fibonacci(n: int) -> int:
    '''Calculate the nth Fibonacci number using dynamic programming'''
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
            """,
            "tests": """
def test_fibonacci():
    assert calculate_fibonacci(0) == 0
    assert calculate_fibonacci(1) == 1
    assert calculate_fibonacci(5) == 5
    assert calculate_fibonacci(10) == 55
            """,
            "documentation": "Function to calculate Fibonacci numbers efficiently",
            "security_review": "No security vulnerabilities identified",
            "performance_metrics": {"time_complexity": "O(n)", "space_complexity": "O(1)"}
        }

        result = gate.assess(complete_artifact, PipelineStage.CONSTRUCTION)

        assert "aggregate_score" in result
        assert "dimension_scores" in result
        assert "passed" in result
        assert result["aggregate_score"] >= 70  # Should score reasonably for complete artifact

    def test_quality_assessment_incomplete_artifact(self):
        """Test quality assessment on an incomplete artifact"""
        gate = KernelQualityGate()

        incomplete_artifact = {
            "type": "python_function",
            "code": "def bad_function():\n    pass"  # No tests, docs, or analysis
        }

        result = gate.assess(incomplete_artifact, PipelineStage.CONSTRUCTION)

        assert result["aggregate_score"] < 80  # Should score lower for incomplete artifact
        assert result["gaps_count"] > 0  # Should have gaps

    @pytest.mark.asyncio
    async def test_governance_agent_deployment_verification(self):
        """Test governance verification for agent deployment"""
        # Mock agent and user data
        agent_id = "test_agent_001"
        user_id = "test_user_001"
        deployment_config = {
            "environment": "production",
            "autonomous": False,
            "permissions": ["read", "write"]
        }

        with patch.object(agent_governance, '_get_agent_certification_level', return_value=3), \
             patch.object(agent_governance, '_get_user_trust_score', return_value=85.0), \
             patch.object(agent_governance, '_calculate_deployment_complexity', return_value=2.0):

            result = await agent_governance.verify_agent_deployment(
                agent_id, user_id, deployment_config
            )

            assert "verified" in result
            assert "drift_score" in result
            assert "checkpoint_id" in result
            assert "approved" in result
            assert result["approved"]  # Should be approved for certified agent

    @pytest.mark.asyncio
    async def test_governance_purchase_verification(self):
        """Test governance verification for agent purchase"""
        agent_id = "test_agent_002"
        user_id = "test_user_002"

        with patch.object(agent_governance, '_get_agent_certification_level', return_value=2), \
             patch.object(agent_governance, '_get_user_purchase_history', return_value=5), \
             patch.object(agent_governance, '_get_agent_popularity', return_value=25):

            result = await agent_governance.verify_agent_purchase(
                agent_id, user_id, "purchase"
            )

            assert result["approved"]  # Should auto-approve verified purchases
            assert result["checkpoint_id"].startswith("purchase_")

    @pytest.mark.asyncio
    async def test_governance_autonomous_execution_strict(self):
        """Test strict governance for autonomous execution"""
        agent_id = "test_agent_003"
        task_description = "Deploy production database migration"
        execution_context = {
            "involves_payment": False,
            "involves_user_data": True,
            "requires_external_api": True,
            "has_rollback_plan": True,
            "monitored_execution": True
        }

        with patch.object(agent_governance, '_get_agent_certification_level', return_value=4), \
             patch.object(agent_governance, '_calculate_task_complexity', return_value=3.0), \
             patch.object(agent_governance, '_assess_execution_safety', return_value=0.9):

            result = await agent_governance.verify_autonomous_execution(
                agent_id, task_description, execution_context
            )

            assert result["approved"]  # Should approve with high certification and safety
            assert result["safety_score"] >= 0.8
            assert result["checkpoint_id"].startswith("autonomous_")

    @pytest.mark.asyncio
    async def test_governance_certification_verification(self):
        """Test governance verification for agent certification"""
        agent_id = "test_agent_004"
        program_id = "expert_program"

        with patch.object(agent_governance, '_get_program_difficulty', return_value=3), \
             patch.object(agent_governance, '_get_agent_training_completion', return_value=95.0):

            result = await agent_governance.verify_certification_request(
                agent_id, program_id, 92.0, 89.0
            )

            # Certifications require board review, so approved may be False
            assert "approved" in result
            assert "checkpoint_id" in result
            assert "requires_board_review" in result
            assert result["checkpoint_id"].startswith("certify_")
            assert result["requires_board_review"]  # Certifications need board review

    def test_governance_checkpoint_creation(self):
        """Test that governance checkpoints are created correctly"""
        initial_checkpoint_count = len(agent_governance.checkpoints)

        # Create a mock checkpoint
        from agent_governance import GovernanceCheckpoint
        checkpoint = GovernanceCheckpoint(
            checkpoint_id="test_checkpoint_001",
            action=GovernanceAction.DEPLOYMENT,
            agent_id="test_agent",
            user_id="test_user",
            state={"test": "state"},
            metrics={"test": "metrics"}
        )

        agent_governance.checkpoints.append(checkpoint)

        assert len(agent_governance.checkpoints) == initial_checkpoint_count + 1
        assert agent_governance.checkpoints[-1].checkpoint_id == "test_checkpoint_001"

    @pytest.mark.asyncio
    async def test_governance_status_reporting(self):
        """Test governance status reporting"""
        # Test system-wide status
        system_status = await agent_governance.get_governance_status()

        assert "total_checkpoints" in system_status
        assert "verified_checkpoints" in system_status
        assert "system_health" in system_status

        # Test agent-specific status
        agent_status = await agent_governance.get_governance_status("test_agent_001")

        assert "agent_id" in agent_status
        assert "total_checkpoints" in agent_status
        assert "avg_drift_score" in agent_status

    def test_quality_gate_convergence_threshold(self):
        """Test that quality gate has proper convergence threshold"""
        gate = KernelQualityGate()

        assert hasattr(gate, 'CONVERGENCE_THRESHOLD')
        assert gate.CONVERGENCE_THRESHOLD == 99.0

    def test_quality_gate_max_iterations(self):
        """Test that quality gate has proper max iterations"""
        gate = KernelQualityGate()

        assert hasattr(gate, 'MAX_ITERATIONS')
        assert gate.MAX_ITERATIONS == 10

    def test_frozen_spine_integration(self):
        """Test that governance uses FrozenSpine"""
        from genesis_kernel import FrozenSpine

        # Check that agent_governance has frozen_spine
        assert hasattr(agent_governance, 'frozen_spine')
        assert isinstance(agent_governance.frozen_spine, FrozenSpine)

    def test_governance_action_enum(self):
        """Test that governance actions are properly defined"""
        from agent_governance import GovernanceAction

        actions = [action.value for action in GovernanceAction]
        expected_actions = [
            "deployment", "purchase", "rental",
            "certification", "enrollment", "autonomous_execution"
        ]

        for action in expected_actions:
            assert action in actions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])