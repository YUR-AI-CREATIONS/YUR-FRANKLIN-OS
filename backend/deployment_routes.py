"""
FRANKLIN OS Deployment API Routes
===================================
Controlled, hardened deployment with full rollback and audit logging.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from deployment_engine import (
    deployment_engine,
    Environment,
    DeploymentStatus
)

deploy_router = APIRouter(prefix="/api/deploy")


# ============================================================================
#                         PYDANTIC MODELS
# ============================================================================

class CreateDeploymentRequest(BaseModel):
    build_id: str
    project_name: str
    environment: str = "dev"  # dev, staging, prod


class DeployRequest(BaseModel):
    deployment_id: str
    artifact: Dict[str, Any]
    config: Dict[str, Any]


class RollbackRequest(BaseModel):
    deployment_id: str
    authority: str


class KillSwitchRequest(BaseModel):
    authority: str
    reason: str


class DeactivateKillSwitchRequest(BaseModel):
    authority: str
    override_code: str


# ============================================================================
#                         ROUTES
# ============================================================================

@deploy_router.get("/status")
async def get_deployment_status():
    """Get deployment engine status"""
    return deployment_engine.get_status()


@deploy_router.post("/create")
async def create_deployment(request: CreateDeploymentRequest):
    """Create a new deployment"""
    try:
        env_map = {
            "dev": Environment.DEV,
            "staging": Environment.STAGING,
            "prod": Environment.PROD
        }
        
        environment = env_map.get(request.environment, Environment.DEV)
        
        deployment = deployment_engine.create_deployment(
            build_id=request.build_id,
            project_name=request.project_name,
            environment=environment
        )
        
        return {
            "success": True,
            "deployment": deployment.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@deploy_router.post("/execute")
async def execute_deployment(request: DeployRequest):
    """Execute a deployment"""
    try:
        result = deployment_engine.deploy(
            deployment_id=request.deployment_id,
            artifact=request.artifact,
            config=request.config
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@deploy_router.post("/rollback")
async def rollback_deployment(request: RollbackRequest):
    """Rollback a deployment to previous checkpoint"""
    try:
        result = deployment_engine.rollback(
            deployment_id=request.deployment_id,
            authority=request.authority
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@deploy_router.post("/kill-switch/activate")
async def activate_kill_switch(request: KillSwitchRequest):
    """Activate kill switch - halt all deployments"""
    try:
        result = deployment_engine.activate_kill_switch(
            authority=request.authority,
            reason=request.reason
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@deploy_router.post("/kill-switch/deactivate")
async def deactivate_kill_switch(request: DeactivateKillSwitchRequest):
    """Deactivate kill switch with principal override"""
    try:
        result = deployment_engine.deactivate_kill_switch(
            authority=request.authority,
            override_code=request.override_code
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@deploy_router.get("/kill-switch/status")
async def get_kill_switch_status():
    """Get kill switch status"""
    return {
        "kill_switch_active": deployment_engine.kill_switch_active,
        "public_access_enabled": deployment_engine.public_access_enabled
    }


@deploy_router.get("/list")
async def list_deployments(environment: str = None):
    """List all deployments"""
    env_map = {
        "dev": Environment.DEV,
        "staging": Environment.STAGING,
        "prod": Environment.PROD
    }
    
    env = env_map.get(environment) if environment else None
    return {"deployments": deployment_engine.list_deployments(env)}


@deploy_router.get("/{deployment_id}")
async def get_deployment(deployment_id: str):
    """Get deployment details"""
    deployment = deployment_engine.get_deployment(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment


@deploy_router.get("/audit/log")
async def get_audit_log(limit: int = 100):
    """Get immutable deployment audit log"""
    return {
        "audit_log": deployment_engine.get_audit_log(limit),
        "total_entries": len(deployment_engine.audit_log)
    }


@deploy_router.get("/environments")
async def get_environments():
    """Get available environments"""
    return {
        "environments": [
            {
                "id": "dev",
                "name": "Development",
                "description": "Rapid iteration environment",
                "restrictions": []
            },
            {
                "id": "staging",
                "name": "Staging",
                "description": "Full system simulation",
                "restrictions": ["Requires DEV deployment"]
            },
            {
                "id": "prod",
                "name": "Production",
                "description": "Locked, auditable, rollback-ready",
                "restrictions": ["Requires STAGING deployment", "Audit required"]
            }
        ],
        "progression": "DEV → STAGING → PROD",
        "no_shortcuts": True
    }
