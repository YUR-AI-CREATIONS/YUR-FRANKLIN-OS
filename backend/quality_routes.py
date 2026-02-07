"""
FRANKLIN OS Quality Gate API Routes
====================================
Stage-gated build certification with full audit trail.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from quality_gates import (
    quality_gate_system, 
    QualityDimension, 
    StageGate,
    GateStatus
)

quality_router = APIRouter(prefix="/api/quality")


# ============================================================================
#                         PYDANTIC MODELS
# ============================================================================

class StartBuildRequest(BaseModel):
    project_name: str
    project_description: str


class StageCheck(BaseModel):
    name: str
    passed: bool
    evidence: str = ""
    issue: str = ""


class EvaluateStageRequest(BaseModel):
    build_id: str
    stage: str  # specification, architecture, implementation, integration, quality, certification
    checks: List[StageCheck]


class ApplyHealRequest(BaseModel):
    build_id: str
    stage: str
    fix_description: str


class ScoreDimensionRequest(BaseModel):
    build_id: str
    dimension: str  # originality, effectiveness, appearance, functionality, monetizable
    score: float
    evidence: List[str]


class GenerateCertificateRequest(BaseModel):
    build_id: str


# ============================================================================
#                         BUILD LIFECYCLE
# ============================================================================

@quality_router.post("/build/start")
async def start_certified_build(request: StartBuildRequest):
    """Start a new quality-gated build"""
    try:
        build_id = quality_gate_system.start_build(
            project_name=request.project_name,
            project_description=request.project_description
        )
        return {
            "success": True,
            "build_id": build_id,
            "message": f"Build {build_id} initialized. Ready for stage evaluation.",
            "next_stage": "specification"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@quality_router.get("/build/{build_id}/status")
async def get_build_status(build_id: str):
    """Get current build status"""
    try:
        return quality_gate_system.get_build_status(build_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@quality_router.get("/builds")
async def list_builds():
    """List all builds"""
    builds = []
    for build_id in quality_gate_system.builds:
        try:
            builds.append(quality_gate_system.get_build_status(build_id))
        except:
            pass
    return {"builds": builds, "total": len(builds)}


# ============================================================================
#                         STAGE GATES
# ============================================================================

@quality_router.post("/stage/evaluate")
async def evaluate_stage_gate(request: EvaluateStageRequest):
    """Evaluate a stage gate with checks"""
    try:
        stage = StageGate(request.stage)
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid stage. Must be one of: {[s.value for s in StageGate]}"
        )
    
    try:
        checks = [
            {
                "name": c.name,
                "passed": c.passed,
                "evidence": c.evidence,
                "issue": c.issue
            }
            for c in request.checks
        ]
        
        result = quality_gate_system.evaluate_stage(
            build_id=request.build_id,
            stage=stage,
            checks=checks
        )
        
        return {
            "success": result.status == GateStatus.PASSED,
            "result": result.to_dict(),
            "message": f"Stage {stage.value}: {result.score:.1f}% - {result.status.value}",
            "can_proceed": result.status == GateStatus.PASSED,
            "needs_healing": result.status == GateStatus.FAILED
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@quality_router.post("/stage/heal")
async def apply_stage_heal(request: ApplyHealRequest):
    """Apply a fix to a failed stage"""
    try:
        stage = StageGate(request.stage)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid stage")
    
    try:
        result = quality_gate_system.apply_heal(
            build_id=request.build_id,
            stage=stage,
            fix_description=request.fix_description
        )
        
        return {
            "success": True,
            "result": result.to_dict(),
            "status": result.status.value,
            "heal_attempts": result.heal_attempts,
            "escalated": result.status == GateStatus.ESCALATED,
            "message": "Heal applied. Re-evaluate stage to verify fix." if result.status != GateStatus.ESCALATED else "Max heal attempts reached. Escalated to human review."
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
#                         DIMENSION SCORING
# ============================================================================

@quality_router.post("/dimension/score")
async def score_quality_dimension(request: ScoreDimensionRequest):
    """Score a quality dimension with evidence"""
    try:
        dimension = QualityDimension(request.dimension)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid dimension. Must be one of: {[d.value for d in QualityDimension]}"
        )
    
    try:
        ds = quality_gate_system.score_dimension(
            build_id=request.build_id,
            dimension=dimension,
            score=request.score,
            evidence=request.evidence
        )
        
        return {
            "success": True,
            "dimension_score": ds.to_dict(),
            "passed": ds.score >= 99.0,
            "message": f"{dimension.value}: {ds.score:.1f}% - {'PASSED' if ds.score >= 99 else 'BELOW THRESHOLD'}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@quality_router.get("/dimensions")
async def get_dimensions_info():
    """Get information about all quality dimensions"""
    return {
        "dimensions": [
            {
                "id": d.value,
                "name": d.name,
                "threshold": 99.0,
                "description": {
                    "originality": "No plagiarism, unique architecture, IP-clean code",
                    "effectiveness": "Solves the stated problem, does what it should do",
                    "appearance": "Professional UI/UX, polished, production-ready visuals",
                    "functionality": "All features work correctly, tested, zero bugs",
                    "monetizable": "Revenue-ready, deployable immediately, scalable"
                }.get(d.value, "")
            }
            for d in QualityDimension
        ],
        "pass_threshold": 99.0,
        "message": "All dimensions must score 99%+ for certification"
    }


# ============================================================================
#                         CERTIFICATION
# ============================================================================

@quality_router.post("/certificate/generate")
async def generate_certificate(request: GenerateCertificateRequest):
    """Generate a certificate if all gates passed"""
    try:
        certificate = quality_gate_system.generate_certificate(request.build_id)
        
        return {
            "success": True,
            "certified": certificate.is_certified(),
            "certificate": certificate.to_dict(),
            "message": f"Certificate {certificate.certificate_id} issued! Project is CERTIFIED."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@quality_router.get("/certificate/{certificate_id}")
async def get_certificate(certificate_id: str):
    """Get a certificate by ID"""
    cert = quality_gate_system.certificates.get(certificate_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return cert.to_dict()


@quality_router.get("/certificates")
async def list_certificates():
    """List all issued certificates"""
    return {
        "certificates": [c.to_dict() for c in quality_gate_system.certificates.values()],
        "total": len(quality_gate_system.certificates)
    }


# ============================================================================
#                         AUDIT
# ============================================================================

@quality_router.get("/audit/trail")
async def get_audit_trail(build_id: str = None, limit: int = 100):
    """Get audit trail entries"""
    return {
        "audit_trail": quality_gate_system.get_audit_trail(build_id, limit),
        "total_entries": len(quality_gate_system.audit_trail)
    }


@quality_router.post("/audit/random/{build_id}")
async def perform_random_audit(build_id: str):
    """Perform a random audit on a build"""
    try:
        result = quality_gate_system.random_audit(build_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
#                         STAGES INFO
# ============================================================================

@quality_router.get("/stages")
async def get_stages_info():
    """Get information about all stage gates"""
    return {
        "stages": [
            {
                "id": s.value,
                "name": s.name,
                "order": idx + 1,
                "description": {
                    "specification": "Requirements complete, all ambiguities resolved",
                    "architecture": "Scalable, secure, follows best practices",
                    "implementation": "Tests pass, no bugs, clean code",
                    "integration": "All components work together, API contracts met",
                    "quality": "99%+ on all 5 quality dimensions",
                    "certification": "Audit complete, license generated, ready to ship"
                }.get(s.value, ""),
                "pass_criteria": "Must pass all checks to proceed to next stage"
            }
            for idx, s in enumerate(StageGate)
        ],
        "total_stages": len(StageGate),
        "message": "Build must pass ALL stages before certification"
    }


# ============================================================================
#                         QUICK STATUS
# ============================================================================

@quality_router.get("/status")
async def get_quality_system_status():
    """Get overall quality system status"""
    total_builds = len(quality_gate_system.builds)
    certified_builds = len([
        b for b in quality_gate_system.builds.values() 
        if b.get("status") == "certified"
    ])
    
    return {
        "system": "Franklin OS Quality Gate System",
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "total_builds": total_builds,
        "certified_builds": certified_builds,
        "certification_rate": f"{(certified_builds/total_builds*100) if total_builds > 0 else 0:.1f}%",
        "total_certificates": len(quality_gate_system.certificates),
        "audit_entries": len(quality_gate_system.audit_trail),
        "pass_threshold": "99%",
        "stages": len(StageGate),
        "dimensions": len(QualityDimension),
        "authority": {
            "ai": "Franklin",
            "enterprise": "Franklin OS Enterprise"
        },
        "principles": [
            "Zero Hallucination",
            "No Drift",
            "Sovereign Grade",
            "Evidence-Based",
            "Fully Auditable"
        ]
    }
