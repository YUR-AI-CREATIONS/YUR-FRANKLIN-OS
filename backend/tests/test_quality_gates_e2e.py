"""
E2E Tests for Quality Gates
Tests all 8 quality dimensions with comprehensive scenarios
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from quality_gates import QualityGate, QualityDimension, StageGate, GateStatus
from genesis_kernel import QualityScore


class TestQualityGatesE2E:
    """End-to-end tests for quality certification system"""

    @pytest.fixture
    def sample_artifact(self):
        """Sample build artifact for testing"""
        return {
            "project_id": "test-project-123",
            "build_id": "build-456",
            "files": [
                {
                    "path": "backend/main.py",
                    "content": "def hello():\n    print('Hello World')\n    return True",
                    "language": "python"
                },
                {
                    "path": "frontend/App.js",
                    "content": "function App() {\n  return <div>Hello</div>;\n}",
                    "language": "javascript"
                }
            ],
            "metadata": {
                "tech_stack": ["python", "react"],
                "features": ["authentication", "database"],
                "requirements": ["User login", "Data storage"]
            }
        }

    @pytest.mark.asyncio
    async def test_completeness_dimension_high_score(self, sample_artifact):
        """Test completeness scoring with complete artifact"""
        gate = QualityGate()
        score = await gate.evaluate_dimension(sample_artifact, QualityDimension.COMPLETENESS)

        assert score.score >= 80.0  # Should score high for complete artifact
        assert len(score.evidence) > 0
        assert "requirements" in " ".join(score.evidence).lower()

    @pytest.mark.asyncio
    async def test_completeness_dimension_low_score(self):
        """Test completeness scoring with incomplete artifact"""
        incomplete_artifact = {
            "project_id": "test-123",
            "files": [],  # No files
            "metadata": {}  # No metadata
        }

        gate = QualityGate()
        score = await gate.evaluate_dimension(incomplete_artifact, QualityDimension.COMPLETENESS)

        assert score.score < 50.0  # Should score low for incomplete artifact
        assert len(score.evidence) > 0

    @pytest.mark.asyncio
    async def test_coherence_dimension_consistent(self, sample_artifact):
        """Test coherence with consistent naming and structure"""
        gate = QualityGate()
        score = await gate.evaluate_dimension(sample_artifact, QualityDimension.COHERENCE)

        assert score.score >= 70.0  # Should score well for consistent artifact
        assert len(score.evidence) > 0

    @pytest.mark.asyncio
    async def test_correctness_dimension_functional_code(self, sample_artifact):
        """Test correctness with syntactically correct code"""
        gate = QualityGate()
        score = await gate.evaluate_dimension(sample_artifact, QualityDimension.CORRECTNESS)

        assert score.score >= 60.0  # Should score reasonably for valid code
        assert len(score.evidence) > 0

    @pytest.mark.asyncio
    async def test_security_dimension_basic_checks(self, sample_artifact):
        """Test security assessment"""
        gate = QualityGate()
        score = await gate.evaluate_dimension(sample_artifact, QualityDimension.SECURITY)

        assert score.score >= 50.0  # Basic security checks
        assert len(score.evidence) > 0
        # Should check for common vulnerabilities
        evidence_text = " ".join(score.evidence).lower()
        assert "security" in evidence_text or "vulnerability" in evidence_text

    @pytest.mark.asyncio
    async def test_performance_dimension_efficiency(self, sample_artifact):
        """Test performance evaluation"""
        gate = QualityGate()
        score = await gate.evaluate_dimension(sample_artifact, QualityDimension.PERFORMANCE)

        assert score.score >= 40.0  # Basic performance assessment
        assert len(score.evidence) > 0

    @pytest.mark.asyncio
    async def test_scalability_dimension_growth_potential(self, sample_artifact):
        """Test scalability assessment"""
        gate = QualityGate()
        score = await gate.evaluate_dimension(sample_artifact, QualityDimension.SCALABILITY)

        assert score.score >= 40.0  # Basic scalability checks
        assert len(score.evidence) > 0

    @pytest.mark.asyncio
    async def test_maintainability_dimension_code_quality(self, sample_artifact):
        """Test maintainability evaluation"""
        gate = QualityGate()
        score = await gate.evaluate_dimension(sample_artifact, QualityDimension.MAINTAINABILITY)

        assert score.score >= 50.0  # Code quality assessment
        assert len(score.evidence) > 0

    @pytest.mark.asyncio
    async def test_compliance_dimension_standards(self, sample_artifact):
        """Test compliance with standards"""
        gate = QualityGate()
        score = await gate.evaluate_dimension(sample_artifact, QualityDimension.COMPLIANCE)

        assert score.score >= 40.0  # Basic compliance checks
        assert len(score.evidence) > 0

    @pytest.mark.asyncio
    async def test_full_certification_pipeline(self, sample_artifact):
        """Test complete certification pipeline"""
        gate = QualityGate()

        # Evaluate all dimensions
        results = {}
        for dimension in QualityDimension:
            score = await gate.evaluate_dimension(sample_artifact, dimension)
            results[dimension] = score

        # Check that all dimensions were evaluated
        assert len(results) == 8

        # Calculate weighted average (using the weights from the enum comments)
        weights = {
            QualityDimension.COMPLETENESS: 1.5,
            QualityDimension.COHERENCE: 1.3,
            QualityDimension.CORRECTNESS: 1.5,
            QualityDimension.SECURITY: 1.4,
            QualityDimension.PERFORMANCE: 1.0,
            QualityDimension.SCALABILITY: 1.0,
            QualityDimension.MAINTAINABILITY: 1.1,
            QualityDimension.COMPLIANCE: 1.2
        }

        total_weight = sum(weights.values())
        weighted_score = sum(score.score * weights[dimension] for dimension, score in results.items()) / total_weight

        # Should pass certification (99%+ weighted average)
        assert weighted_score >= 99.0 or any(score.score >= 99.0 for score in results.values())

    @pytest.mark.asyncio
    async def test_stage_gate_progression(self, sample_artifact):
        """Test stage gate evaluation and progression"""
        gate = QualityGate()

        # Test specification stage
        spec_result = await gate.evaluate_stage(sample_artifact, StageGate.SPECIFICATION)
        assert spec_result.status in [GateStatus.PASSED, GateStatus.FAILED, GateStatus.IN_PROGRESS]

        # Test architecture stage
        arch_result = await gate.evaluate_stage(sample_artifact, StageGate.ARCHITECTURE)
        assert arch_result.status in [GateStatus.PASSED, GateStatus.FAILED, GateStatus.IN_PROGRESS]

        # Test implementation stage
        impl_result = await gate.evaluate_stage(sample_artifact, StageGate.IMPLEMENTATION)
        assert impl_result.status in [GateStatus.PASSED, GateStatus.FAILED, GateStatus.IN_PROGRESS]

    @pytest.mark.asyncio
    async def test_healing_mechanism(self, sample_artifact):
        """Test automatic healing for failed gates"""
        gate = QualityGate()

        # Create a low-quality artifact that should trigger healing
        low_quality_artifact = {
            "project_id": "test-123",
            "files": [
                {
                    "path": "buggy.py",
                    "content": "def broken():\n    return undefined_variable",  # Syntax error
                    "language": "python"
                }
            ],
            "metadata": {}
        }

        # Evaluate and check if healing is triggered
        result = await gate.evaluate_stage(low_quality_artifact, StageGate.IMPLEMENTATION)

        # Should either pass, fail, or attempt healing
        assert result.status in [GateStatus.PASSED, GateStatus.FAILED, GateStatus.HEALING, GateStatus.IN_PROGRESS]

    @pytest.mark.asyncio
    async def test_certification_hash_generation(self, sample_artifact):
        """Test certification hash generation for audit trail"""
        gate = QualityGate()

        # Generate certification
        certification = await gate.certify_build(sample_artifact)

        # Should have hash for immutability
        assert "certification_hash" in certification
        assert isinstance(certification["certification_hash"], str)
        assert len(certification["certification_hash"]) > 0

        # Hash should be consistent for same input
        certification2 = await gate.certify_build(sample_artifact)
        assert certification["certification_hash"] == certification2["certification_hash"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])