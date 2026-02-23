"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    GENESIS KERNEL: OUROBOROS-LATTICE CORE                    ║
║                                                                              ║
║  The self-referential improvement engine. Output becomes input until         ║
║  convergence at 99%+ quality threshold is achieved.                          ║
║                                                                              ║
║  Architecture: Immutable Frozen Spine + Extensible Evolution Modules         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json


class PipelineStage(Enum):
    """The Genesis Pipeline Stages"""
    INCEPTION = "inception"           # Initial requirement capture
    SPECIFICATION = "specification"   # Socratic refinement
    ARCHITECTURE = "architecture"     # System design
    CONSTRUCTION = "construction"     # Code generation
    VALIDATION = "validation"         # Quality gate
    EVOLUTION = "evolution"           # Improvement cycle
    DEPLOYMENT = "deployment"         # Production release
    GOVERNANCE = "governance"         # Licensing & compliance


class QualityDimension(Enum):
    """Quality scoring dimensions"""
    COMPLETENESS = "completeness"     # All requirements addressed
    COHERENCE = "coherence"           # Internal consistency
    CORRECTNESS = "correctness"       # Functional accuracy
    SECURITY = "security"             # Vulnerability assessment
    PERFORMANCE = "performance"       # Efficiency metrics
    SCALABILITY = "scalability"       # Growth capacity
    MAINTAINABILITY = "maintainability"  # Code quality
    COMPLIANCE = "compliance"         # Regulatory adherence


@dataclass
class QualityScore:
    """Multi-dimensional quality assessment"""
    dimension: QualityDimension
    score: float  # 0.0 to 100.0
    weight: float  # Importance multiplier
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class Milestone:
    """Evolution playbook milestone"""
    id: str
    name: str
    stage: PipelineStage
    success_criteria: List[str]
    deliverables: List[str]
    target_score: float
    actual_score: Optional[float] = None
    status: str = "pending"  # pending, active, completed, failed
    drift_detected: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None


@dataclass
class SpineCheckpoint:
    """Frozen Spine integrity checkpoint"""
    checkpoint_id: str
    stage: PipelineStage
    state_hash: str
    timestamp: str
    metrics: Dict[str, Any]
    

class FrozenSpine:
    """
    The Immutable Core - Drift Detection System
    
    Maintains cryptographic hashes of system state at each checkpoint.
    Any deviation from expected trajectory triggers drift alerts.
    """
    
    def __init__(self):
        self.checkpoints: List[SpineCheckpoint] = []
        self.baseline_hash: Optional[str] = None
        self.drift_threshold: float = 0.15  # 15% deviation triggers alert
        
    def _compute_state_hash(self, state: Dict[str, Any]) -> str:
        """Generate deterministic hash of system state"""
        serialized = json.dumps(state, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()
    
    def create_checkpoint(self, stage: PipelineStage, state: Dict[str, Any], 
                         metrics: Dict[str, Any]) -> SpineCheckpoint:
        """Freeze current state as immutable checkpoint"""
        checkpoint = SpineCheckpoint(
            checkpoint_id=str(uuid.uuid4()),
            stage=stage,
            state_hash=self._compute_state_hash(state),
            timestamp=datetime.now(timezone.utc).isoformat(),
            metrics=metrics
        )
        self.checkpoints.append(checkpoint)
        
        if self.baseline_hash is None:
            self.baseline_hash = checkpoint.state_hash
            
        return checkpoint
    
    def verify_integrity(self, current_state: Dict[str, Any], 
                        expected_stage: PipelineStage) -> Dict[str, Any]:
        """Check for drift from frozen baseline"""
        current_hash = self._compute_state_hash(current_state)
        
        # Find most recent checkpoint for this stage
        stage_checkpoints = [c for c in self.checkpoints if c.stage == expected_stage]
        
        if not stage_checkpoints:
            return {
                "verified": True,
                "drift_detected": False,
                "message": "No baseline checkpoint exists for comparison"
            }
        
        latest = stage_checkpoints[-1]
        
        # Compare metrics for drift detection
        drift_score = self._calculate_drift(latest.metrics, current_state.get("metrics", {}))
        
        return {
            "verified": drift_score < self.drift_threshold,
            "drift_detected": drift_score >= self.drift_threshold,
            "drift_score": drift_score,
            "baseline_checkpoint": latest.checkpoint_id,
            "message": "DRIFT ALERT: System deviating from trajectory" if drift_score >= self.drift_threshold else "On track"
        }
    
    def _calculate_drift(self, baseline_metrics: Dict, current_metrics: Dict) -> float:
        """Calculate normalized drift score between metric sets"""
        if not baseline_metrics or not current_metrics:
            return 0.0
            
        total_drift = 0.0
        comparisons = 0
        
        for key in baseline_metrics:
            if key in current_metrics:
                baseline_val = float(baseline_metrics[key]) if isinstance(baseline_metrics[key], (int, float)) else 0
                current_val = float(current_metrics[key]) if isinstance(current_metrics[key], (int, float)) else 0
                
                if baseline_val > 0:
                    drift = abs(current_val - baseline_val) / baseline_val
                    total_drift += drift
                    comparisons += 1
                    
        return total_drift / max(comparisons, 1)


class QualityGate:
    """
    The 99% Convergence Engine
    
    Multi-dimensional quality assessment with iterative refinement
    until target threshold is achieved.
    """
    
    CONVERGENCE_THRESHOLD = 99.0
    MAX_ITERATIONS = 10
    
    def __init__(self):
        self.dimension_weights = {
            QualityDimension.COMPLETENESS: 1.5,
            QualityDimension.COHERENCE: 1.3,
            QualityDimension.CORRECTNESS: 1.5,
            QualityDimension.SECURITY: 1.4,
            QualityDimension.PERFORMANCE: 1.0,
            QualityDimension.SCALABILITY: 1.0,
            QualityDimension.MAINTAINABILITY: 1.1,
            QualityDimension.COMPLIANCE: 1.2
        }
        
    def assess(self, artifact: Dict[str, Any], stage: PipelineStage) -> Dict[str, Any]:
        """Perform comprehensive quality assessment"""
        scores: List[QualityScore] = []
        
        for dimension in QualityDimension:
            score = self._evaluate_dimension(artifact, dimension, stage)
            scores.append(score)
            
        # Calculate weighted aggregate
        total_weighted = sum(s.score * s.weight for s in scores)
        total_weight = sum(s.weight for s in scores)
        aggregate_score = total_weighted / total_weight if total_weight > 0 else 0
        
        # Identify gaps
        gaps = [s for s in scores if s.score < 90]
        critical_gaps = [s for s in scores if s.score < 70]
        
        return {
            "aggregate_score": round(aggregate_score, 2),
            "passed": aggregate_score >= self.CONVERGENCE_THRESHOLD,
            "dimension_scores": [
                {
                    "dimension": s.dimension.value,
                    "score": s.score,
                    "weight": s.weight,
                    "findings": s.findings,
                    "recommendations": s.recommendations
                } for s in scores
            ],
            "gaps_count": len(gaps),
            "critical_gaps": len(critical_gaps),
            "improvement_priority": [
                s.dimension.value for s in sorted(gaps, key=lambda x: x.score)
            ]
        }
    
    def _evaluate_dimension(self, artifact: Dict, dimension: QualityDimension, 
                           stage: PipelineStage) -> QualityScore:
        """Evaluate single quality dimension"""
        # Base scoring logic - extensible per dimension
        score = 70.0  # Default baseline
        findings = []
        recommendations = []
        
        if dimension == QualityDimension.COMPLETENESS:
            score, findings, recommendations = self._assess_completeness(artifact, stage)
        elif dimension == QualityDimension.COHERENCE:
            score, findings, recommendations = self._assess_coherence(artifact)
        elif dimension == QualityDimension.CORRECTNESS:
            score, findings, recommendations = self._assess_correctness(artifact)
        elif dimension == QualityDimension.SECURITY:
            score, findings, recommendations = self._assess_security(artifact)
        elif dimension == QualityDimension.PERFORMANCE:
            score, findings, recommendations = self._assess_performance(artifact)
        elif dimension == QualityDimension.SCALABILITY:
            score, findings, recommendations = self._assess_scalability(artifact)
        elif dimension == QualityDimension.MAINTAINABILITY:
            score, findings, recommendations = self._assess_maintainability(artifact)
        elif dimension == QualityDimension.COMPLIANCE:
            score, findings, recommendations = self._assess_compliance(artifact)
            
        return QualityScore(
            dimension=dimension,
            score=score,
            weight=self.dimension_weights[dimension],
            findings=findings,
            recommendations=recommendations
        )
    
    def _assess_completeness(self, artifact: Dict, stage: PipelineStage):
        score = 75.0
        findings = []
        recommendations = []
        
        # Check for required fields based on stage
        required_fields = {
            PipelineStage.SPECIFICATION: ["requirements", "constraints", "entities"],
            PipelineStage.ARCHITECTURE: ["components", "interfaces", "data_model"],
            PipelineStage.CONSTRUCTION: ["code", "tests", "documentation"],
        }
        
        stage_requirements = required_fields.get(stage, [])
        present = sum(1 for f in stage_requirements if f in artifact)
        
        if stage_requirements:
            score = (present / len(stage_requirements)) * 100
            missing = [f for f in stage_requirements if f not in artifact]
            if missing:
                findings.append(f"Missing required elements: {missing}")
                recommendations.append(f"Add {', '.join(missing)} to achieve completeness")
        else:
            score = 85.0
            
        return score, findings, recommendations
    
    def _assess_coherence(self, artifact: Dict):
        # Check internal consistency
        score = 85.0
        findings = []
        recommendations = []
        
        # Verify cross-references exist
        if "components" in artifact and "interfaces" in artifact:
            score = 90.0
        else:
            findings.append("Component-interface mapping incomplete")
            recommendations.append("Ensure all components have defined interfaces")
            
        return score, findings, recommendations
    
    def _assess_correctness(self, artifact: Dict):
        score = 80.0
        findings = []
        recommendations = []
        
        if artifact.get("validated", False):
            score = 95.0
        else:
            findings.append("Artifact not yet validated")
            recommendations.append("Run validation suite")
            
        return score, findings, recommendations
    
    def _assess_security(self, artifact: Dict):
        score = 75.0
        findings = []
        recommendations = []
        
        security_fields = ["authentication", "authorization", "encryption"]
        present = sum(1 for f in security_fields if f in artifact.get("security", {}))
        
        score = 60 + (present / len(security_fields)) * 40
        
        if present < len(security_fields):
            findings.append("Security specification incomplete")
            recommendations.append("Define auth, authz, and encryption strategies")
            
        return score, findings, recommendations
    
    def _assess_performance(self, artifact: Dict):
        score = 80.0
        findings = []
        recommendations = []
        
        if "performance_requirements" in artifact:
            score = 90.0
        else:
            findings.append("No performance requirements defined")
            recommendations.append("Specify latency, throughput targets")
            
        return score, findings, recommendations
    
    def _assess_scalability(self, artifact: Dict):
        score = 80.0
        findings = []
        recommendations = []
        
        if "scalability" in artifact or "scale_requirements" in artifact:
            score = 88.0
        else:
            findings.append("Scalability not addressed")
            recommendations.append("Define horizontal/vertical scaling strategy")
            
        return score, findings, recommendations
    
    def _assess_maintainability(self, artifact: Dict):
        score = 82.0
        findings = []
        recommendations = []
        
        if artifact.get("documentation"):
            score += 10
        else:
            findings.append("Documentation missing")
            recommendations.append("Add inline documentation and README")
            
        return score, findings, recommendations
    
    def _assess_compliance(self, artifact: Dict):
        score = 78.0
        findings = []
        recommendations = []
        
        if "compliance" in artifact or "regulations" in artifact:
            score = 92.0
        else:
            findings.append("Compliance requirements not specified")
            recommendations.append("Identify applicable regulations (GDPR, HIPAA, etc.)")
            
        return score, findings, recommendations


class EvolutionPlaybook:
    """
    Roadmap & Milestone Management with Adaptive Learning
    
    Tracks progress, detects drift, and adapts strategy based on outcomes.
    """
    
    def __init__(self):
        self.milestones: List[Milestone] = []
        self.iteration_history: List[Dict] = []
        
    def create_roadmap(self, specification: Dict[str, Any]) -> List[Milestone]:
        """Generate milestone roadmap from specification"""
        self.milestones = [
            Milestone(
                id=str(uuid.uuid4()),
                name="Requirements Lock",
                stage=PipelineStage.SPECIFICATION,
                success_criteria=["All ambiguities resolved", "Stakeholder sign-off"],
                deliverables=["Formal specification document", "Acceptance criteria"],
                target_score=99.5
            ),
            Milestone(
                id=str(uuid.uuid4()),
                name="Architecture Blueprint",
                stage=PipelineStage.ARCHITECTURE,
                success_criteria=["Component diagram complete", "Interface contracts defined"],
                deliverables=["System architecture", "Data model", "API contracts"],
                target_score=95.0
            ),
            Milestone(
                id=str(uuid.uuid4()),
                name="Core Build Complete",
                stage=PipelineStage.CONSTRUCTION,
                success_criteria=["All components implemented", "Unit tests passing"],
                deliverables=["Source code", "Test suite", "Build artifacts"],
                target_score=90.0
            ),
            Milestone(
                id=str(uuid.uuid4()),
                name="Quality Certification",
                stage=PipelineStage.VALIDATION,
                success_criteria=["99% quality gate passed", "Security audit clear"],
                deliverables=["Quality report", "Security assessment", "Performance benchmarks"],
                target_score=99.0
            ),
            Milestone(
                id=str(uuid.uuid4()),
                name="Production Release",
                stage=PipelineStage.DEPLOYMENT,
                success_criteria=["Deployment successful", "Smoke tests passing"],
                deliverables=["Live application", "Monitoring dashboards", "Runbook"],
                target_score=99.0
            ),
            Milestone(
                id=str(uuid.uuid4()),
                name="Governance & Licensing",
                stage=PipelineStage.GOVERNANCE,
                success_criteria=["License terms defined", "Compliance verified"],
                deliverables=["License agreement", "Compliance certificate", "IP documentation"],
                target_score=100.0
            )
        ]
        return self.milestones
    
    def update_milestone(self, milestone_id: str, score: float, 
                        status: str, drift: bool = False) -> Milestone:
        """Update milestone progress"""
        for m in self.milestones:
            if m.id == milestone_id:
                m.actual_score = score
                m.status = status
                m.drift_detected = drift
                if status == "completed":
                    m.completed_at = datetime.now(timezone.utc).isoformat()
                return m
        raise ValueError(f"Milestone {milestone_id} not found")
    
    def get_current_milestone(self) -> Optional[Milestone]:
        """Get the active milestone"""
        for m in self.milestones:
            if m.status in ["pending", "active"]:
                return m
        return None
    
    def record_iteration(self, iteration_data: Dict):
        """Record iteration for learning"""
        self.iteration_history.append({
            **iteration_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    def get_progress_report(self) -> Dict[str, Any]:
        """Generate roadmap progress report"""
        completed = [m for m in self.milestones if m.status == "completed"]
        active = [m for m in self.milestones if m.status == "active"]
        pending = [m for m in self.milestones if m.status == "pending"]
        failed = [m for m in self.milestones if m.status == "failed"]
        drifted = [m for m in self.milestones if m.drift_detected]
        
        total_target = sum(m.target_score for m in self.milestones)
        total_actual = sum(m.actual_score or 0 for m in self.milestones)
        
        return {
            "total_milestones": len(self.milestones),
            "completed": len(completed),
            "active": len(active),
            "pending": len(pending),
            "failed": len(failed),
            "drift_alerts": len(drifted),
            "overall_progress": round((len(completed) / len(self.milestones)) * 100, 1) if self.milestones else 0,
            "quality_trajectory": round((total_actual / total_target) * 100, 1) if total_target > 0 else 0,
            "milestones": [
                {
                    "id": m.id,
                    "name": m.name,
                    "stage": m.stage.value,
                    "target_score": m.target_score,
                    "actual_score": m.actual_score,
                    "status": m.status,
                    "drift_detected": m.drift_detected
                } for m in self.milestones
            ],
            "iterations_count": len(self.iteration_history)
        }


class OuroborosLoop:
    """
    The Self-Referential Improvement Engine
    
    Continuously refines output until convergence threshold is met.
    Output becomes input for the next iteration.
    """
    
    def __init__(self, quality_gate: QualityGate, spine: FrozenSpine, 
                 playbook: EvolutionPlaybook):
        self.quality_gate = quality_gate
        self.spine = spine
        self.playbook = playbook
        self.max_iterations = 10
        self.convergence_threshold = 99.0
        
    async def execute_loop(self, initial_artifact: Dict[str, Any], 
                          stage: PipelineStage,
                          refine_callback: Callable) -> Dict[str, Any]:
        """
        Execute the Ouroboros improvement loop.
        
        Args:
            initial_artifact: Starting state
            stage: Current pipeline stage
            refine_callback: Async function to refine artifact based on recommendations
            
        Returns:
            Final artifact with quality assessment
        """
        current_artifact = initial_artifact
        iteration = 0
        history = []
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Assess quality
            assessment = self.quality_gate.assess(current_artifact, stage)
            
            # Create spine checkpoint
            checkpoint = self.spine.create_checkpoint(
                stage=stage,
                state=current_artifact,
                metrics={"score": assessment["aggregate_score"], "iteration": iteration}
            )
            
            # Check for drift
            drift_check = self.spine.verify_integrity(current_artifact, stage)
            
            # Record iteration
            iteration_record = {
                "iteration": iteration,
                "score": assessment["aggregate_score"],
                "passed": assessment["passed"],
                "drift_detected": drift_check["drift_detected"],
                "gaps": assessment["gaps_count"],
                "checkpoint_id": checkpoint.checkpoint_id
            }
            history.append(iteration_record)
            self.playbook.record_iteration(iteration_record)
            
            # Check convergence
            if assessment["passed"]:
                return {
                    "status": "CONVERGED",
                    "final_score": assessment["aggregate_score"],
                    "iterations": iteration,
                    "artifact": current_artifact,
                    "assessment": assessment,
                    "history": history,
                    "message": f"Quality threshold achieved in {iteration} iteration(s)"
                }
            
            # Check for drift alert
            if drift_check["drift_detected"]:
                return {
                    "status": "DRIFT_ALERT",
                    "final_score": assessment["aggregate_score"],
                    "iterations": iteration,
                    "artifact": current_artifact,
                    "assessment": assessment,
                    "drift_info": drift_check,
                    "history": history,
                    "message": "Execution halted due to trajectory drift. Manual review required."
                }
            
            # Refine artifact using callback (feeds output back as input)
            current_artifact = await refine_callback(
                current_artifact, 
                assessment["improvement_priority"],
                assessment["dimension_scores"]
            )
            
        # Max iterations reached
        return {
            "status": "MAX_ITERATIONS",
            "final_score": assessment["aggregate_score"],
            "iterations": iteration,
            "artifact": current_artifact,
            "assessment": assessment,
            "history": history,
            "message": f"Maximum iterations ({self.max_iterations}) reached. Best score: {assessment['aggregate_score']}%"
        }


class GenesisKernel:
    """
    The Master Orchestrator
    
    Coordinates all subsystems: Spine, Quality Gate, Playbook, Ouroboros Loop.
    Manages the complete Genesis Pipeline from inception to deployment.
    """
    
    def __init__(self):
        self.spine = FrozenSpine()
        self.quality_gate = QualityGate()
        self.playbook = EvolutionPlaybook()
        self.ouroboros = OuroborosLoop(self.quality_gate, self.spine, self.playbook)
        self.current_stage = PipelineStage.INCEPTION
        self.project_id: Optional[str] = None
        self.project_state: Dict[str, Any] = {}
        
    def initialize_project(self, project_name: str, description: str) -> Dict[str, Any]:
        """Initialize a new Genesis project"""
        self.project_id = str(uuid.uuid4())
        self.project_state = {
            "project_id": self.project_id,
            "name": project_name,
            "description": description,
            "current_stage": self.current_stage.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "artifacts": {},
            "quality_history": [],
            "status": "active"
        }
        
        # Create initial roadmap
        self.playbook.create_roadmap(self.project_state)
        
        # Create genesis checkpoint
        self.spine.create_checkpoint(
            stage=PipelineStage.INCEPTION,
            state=self.project_state,
            metrics={"stage": "inception", "completeness": 0}
        )
        
        return {
            "project_id": self.project_id,
            "status": "initialized",
            "roadmap": self.playbook.get_progress_report(),
            "message": f"Genesis project '{project_name}' initialized. Ready for specification phase."
        }
    
    def advance_stage(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to advance to next pipeline stage"""
        # Assess current artifact
        assessment = self.quality_gate.assess(artifact, self.current_stage)
        
        # Update milestone
        current_milestone = self.playbook.get_current_milestone()
        if current_milestone:
            if assessment["passed"]:
                self.playbook.update_milestone(
                    current_milestone.id,
                    assessment["aggregate_score"],
                    "completed"
                )
            else:
                self.playbook.update_milestone(
                    current_milestone.id,
                    assessment["aggregate_score"],
                    "active"
                )
        
        if not assessment["passed"]:
            return {
                "advanced": False,
                "current_stage": self.current_stage.value,
                "score": assessment["aggregate_score"],
                "required_score": self.quality_gate.CONVERGENCE_THRESHOLD,
                "gaps": assessment["improvement_priority"],
                "message": f"Quality threshold not met. Score: {assessment['aggregate_score']}%. Required: {self.quality_gate.CONVERGENCE_THRESHOLD}%"
            }
        
        # Advance to next stage
        stages = list(PipelineStage)
        current_index = stages.index(self.current_stage)
        
        if current_index < len(stages) - 1:
            self.current_stage = stages[current_index + 1]
            self.project_state["current_stage"] = self.current_stage.value
            self.project_state["artifacts"][stages[current_index].value] = artifact
            
            # Activate next milestone
            next_milestone = self.playbook.get_current_milestone()
            if next_milestone:
                self.playbook.update_milestone(next_milestone.id, 0, "active")
            
            return {
                "advanced": True,
                "previous_stage": stages[current_index].value,
                "current_stage": self.current_stage.value,
                "score": assessment["aggregate_score"],
                "roadmap": self.playbook.get_progress_report(),
                "message": f"Advanced to {self.current_stage.value} stage"
            }
        else:
            return {
                "advanced": False,
                "current_stage": self.current_stage.value,
                "score": assessment["aggregate_score"],
                "message": "Pipeline complete. All stages finished.",
                "complete": True
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "project_id": self.project_id,
            "current_stage": self.current_stage.value,
            "roadmap": self.playbook.get_progress_report(),
            "spine_checkpoints": len(self.spine.checkpoints),
            "convergence_threshold": self.quality_gate.CONVERGENCE_THRESHOLD,
            "project_state": self.project_state
        }
